# llama-swap-control.ps1 - the only STOP / RESTART control for llama-swap. ALI-150 v2, 2026-10-21.
# Replaces the old .cmd wrappers (audited findings F6, F7, F8). Old files are in ..\_archive_v1\scripts\.
#
#   llama-swap-control.ps1 -Action Stop      frees the GPU, leaves llama-swap DOWN until Restart or the next logon
#   llama-swap-control.ps1 -Action Restart   frees the GPU, then brings llama-swap back the same way logon does
#
# Safety, in order: refuses if C:\AI\locks\gpu-render.lock exists; refuses unless gpu_guard.ps1 -Gpu says IDLE (exit 0);
# asks for a typed YES; shows what is loaded (GET /running); then llama-swap's own POST /api/models/unload;
# then it PROVES the unload worked (supervisor CORRECTION_v2 item 3): the unload did not go through while
# GET /health still answers -> REFUSED, exit 1, the task and the process are NOT touched, so a half-done
# request never kills a working model; GET /running still names a model after the unload -> REFUSED, exit 1.
# When llama-swap answers /health no more it is already down, and going on is fine.
# Only then it ends the keepalive scheduled task (Stop-ScheduledTask) and the llama-swap process. It NEVER
# disables or unregisters the task, so llama-swap still comes back by itself at the next logon.
#
# Run only from the two shortcuts (they use -NoExit, so you can read it).

param(
    [Parameter(Mandatory = $true)][ValidateSet('Stop', 'Restart')][string]$Action
)

$ErrorActionPreference = 'Continue'
$base       = 'http://127.0.0.1:8080'
$taskNm     = 'Switchyard llama-swap'
$guardPs1   = 'C:\AI\director\scripts\gpu_guard.ps1'
$renderLock = 'C:\AI\locks\gpu-render.lock'

function Say($m) { Write-Host $m }
function Line    { Say (('-' * 78)) }

function Test-ServiceUp {
    # $true when llama-swap answers GET /health. $false = it does not answer, so it is down (that is fine for a stop).
    try { $null = Invoke-WebRequest -Uri "$base/health" -Method Get -TimeoutSec 5 -UseBasicParsing; return $true }
    catch { return $false }
}

function Test-RunningEmpty([string]$text) {
    # $true when a GET /running answer names NO model: no text, an empty JSON list/object, a bare none/null,
    # or an explicit "no model". Anything else counts as "a model is still listed" - that is the safe side.
    if ([string]::IsNullOrWhiteSpace($text)) { return $true }
    $t = $text.Trim()
    if ($t -in @('[]', '{}', 'null', 'none', '"none"', '""')) { return $true }
    if ($t -match '(?i)no model|not loaded|nothing loaded') { return $true }
    return $false
}

Say ''
Line
Say ('llama-swap - ' + $Action.ToUpper() + '   (this DOES end the model that is loaded right now)')
Line
Say '  * the model in use (Forge / the Switchyard LLM / an image generator) is unloaded: any work in progress with it is lost'
Say '  * this is not a pause: the next request has to load the model again, which takes time'
if ($Action -eq 'Stop') {
    Say '  * STOP leaves llama-swap DOWN. Nothing model-related will answer until you use the "Restart" shortcut, or log off and on.'
    Say '  * the keepalive task is only ENDED for now, never disabled: the next logon starts it again on its own'
} else {
    Say '  * RESTART brings it back within about a minute, exactly as at logon; no model is preloaded, the first request loads it'
}
Say '  * the model processes that belong to llama-swap (Strata, llama-server, the image generator) are its children;'
Say '    llama-swap is ended after the models are freed, and Windows can leave those children running; if you see one left,'
Say '    note its pid and end it by hand - this script will not end a process it did not start.'
Say ''
Say 'GPU guard is checked first. Nothing is touched until you type YES.'
Line
Say ''

# 1) a render lock means someone is using the GPU right now
if (Test-Path -LiteralPath $renderLock) {
    Say "REFUSED: the render lock file exists: $renderLock"
    Say '  its text (pid + time + note):'
    try { Get-Content -LiteralPath $renderLock -ErrorAction Stop | ForEach-Object { Say ('    ' + $_) } }
    catch { Say '    (could not read it)' }
    Say '  Read it. If that pid is not running, the lock is stale: you may remove that file by hand, then use this shortcut.'
    Say '  If the pid is alive, a render is running: wait for it, do not remove the lock. (exit 1)'
    Read-Host 'Press Enter to close' | Out-Null
    exit 1
}

# 2) the real guard: render processes, Switchyard queue, image-generator queue, live lock pid, GPU utilisation
if (-not (Test-Path -LiteralPath $guardPs1)) {
    Say "REFUSED: cannot find the guard script: $guardPs1 (exit 1)"
    Read-Host 'Press Enter to close' | Out-Null
    exit 1
}
Say 'checking the GPU (gpu_guard.ps1 -Gpu), this takes a few seconds ...'
$guardOut = & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $guardPs1 -Gpu 2>&1
$guardRc = $LASTEXITCODE
Line
$guardOut | ForEach-Object { Say ('  ' + $_) }
Line
if ($guardRc -ne 0) {
    Say "REFUSED: the guard says the GPU is busy (exit $guardRc). Nothing was changed. Fix the reason above first. (exit 1)"
    Read-Host 'Press Enter to close' | Out-Null
    exit 1
}
Say 'guard: IDLE - it is safe to free the GPU now.'
Say ''

# 3) typed confirmation
$answer = Read-Host "Type YES to continue (anything else aborts, changes nothing)"
if ($answer -cne 'YES') {
    Say 'ABORTED by you: nothing was changed, no model was unloaded.'
    Read-Host 'Press Enter to close' | Out-Null
    exit 1
}
Say ''

# 4) llama-swap's own API: first what is loaded, then the clean unload, then proof that nothing is loaded.
Say 'GET /running (what is loaded right now)'
$runTxt = $null
try {
    $run = Invoke-WebRequest -Uri "$base/running" -Method Get -TimeoutSec 10 -UseBasicParsing
    $runTxt = ("$($run.Content)").Trim()
    Say ('  answer: ' + $(if ([string]::IsNullOrWhiteSpace($runTxt)) { '(no answer text)' } else { $runTxt }))
    if (-not (Test-RunningEmpty $runTxt)) {
        Say '  -> the model named above is the one that will be killed; the GPU frees only after it stops.'
    }
} catch {
    Say ('  no answer - ' + $_.Exception.Message)
}
Say ''
Say "POST $base/api/models/unload"
$unloadOk = $false
try {
    $null = Invoke-RestMethod -Uri "$base/api/models/unload" -Method Post -TimeoutSec 60
    $unloadOk = $true
    Say '  accepted: llama-swap unloaded its models'
} catch {
    Say ('  no clean answer: ' + $_.Exception.Message)
}
if (-not $unloadOk) {
    # SAFETY: an unload that did not go through must NOT be followed by ending the service, that would kill a
    # working model with no proof that it was freed. It is only safe when llama-swap does not answer at all.
    if (Test-ServiceUp) {
        Line
        Say 'REFUSED: POST /api/models/unload did not go through and llama-swap still answers GET /health (exit 1).'
        Say '  Nothing was stopped: the keepalive task and the llama-swap process are left exactly as they are,'
        Say '  so no loaded model was killed by this half-done request. Use this shortcut again, or unload one'
        Say '  model first on the UI page: http://127.0.0.1:8080/ui'
        Line
        Read-Host 'Press Enter to close' | Out-Null
        exit 1
    }
    Say '  llama-swap does not answer /health either, so it is already down: continuing is safe, nothing to free.'
}
Say ''
Say 'GET /running again, as proof that no model is loaded before the service is ended'
$afterTxt = $null
try {
    Start-Sleep -Seconds 2
    $after = Invoke-WebRequest -Uri "$base/running" -Method Get -TimeoutSec 10 -UseBasicParsing
    $afterTxt = ("$($after.Content)").Trim()
    Say ('  answer: ' + $(if ([string]::IsNullOrWhiteSpace($afterTxt)) { '(empty - no model loaded)' } else { $afterTxt }))
    if (-not (Test-RunningEmpty $afterTxt)) {
        Line
        Say 'REFUSED: GET /running still names a loaded model after the unload, so it may still be on the GPU (exit 1).'
        Say '  Nothing was stopped: the keepalive task and the llama-swap process are left exactly as they are.'
        Say '  Unload that model on the UI page (http://127.0.0.1:8080/ui) and use this shortcut again.'
        Line
        Read-Host 'Press Enter to close' | Out-Null
        exit 1
    }
    Say '  no model is listed any more: it is safe to end the service.'
} catch {
    if (Test-ServiceUp) {
        Line
        Say 'REFUSED: GET /running did not answer while GET /health does, so the unload cannot be proved (exit 1).'
        Say '  Nothing was stopped, so no model was killed by this script. Check http://127.0.0.1:8080/ui'
        Line
        Read-Host 'Press Enter to close' | Out-Null
        exit 1
    }
    Say '  no answer and /health does not answer either: llama-swap is down, continuing.'
}
Say ''

# 5) end the keepalive first (Stop-ScheduledTask), so it cannot bring llama-swap back behind our backs
Say "ending the keepalive task '$taskNm' (Stop-ScheduledTask only - the task stays enabled)"
try {
    Stop-ScheduledTask -TaskName $taskNm -ErrorAction Stop
    Say '  task ended'
} catch {
    Say ('  task: ' + $_.Exception.Message)
}

# 6) end the llama-swap process, wait until it is gone
$tries = 0
while ($tries -lt 10) {
    $procs = @(Get-Process llama-swap -ErrorAction SilentlyContinue)
    if ($procs.Count -eq 0) { Say 'llama-swap process: gone'; break }
    if ($tries -eq 0) { Say ('asking llama-swap to close: ' + (($procs | ForEach-Object { 'pid ' + $_.Id }) -join ', ')) }
    $procs | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    $tries++
}
$left = @(Get-Process llama-swap -ErrorAction SilentlyContinue)
if ($left.Count -gt 0) { Say ('llama-swap process still there: ' + (($left | ForEach-Object { 'pid ' + $_.Id }) -join ', ') + ' - check it by hand') }

if ($Action -eq 'Stop') {
    Say ''
    Line
    Say 'STOPPED. llama-swap is DOWN and the GPU is free. To bring it back:'
    Say '  * the "Restart llama-swap (kills loaded model)" shortcut, or'
    Say "  * log off and on: the '$taskNm' task runs at logon and starts it."
    Say 'The task was NOT disabled and NOT unregistered.'
    Say ('Status any time: the "llama-swap Status (read only)" shortcut, or http://127.0.0.1:8080/ui')
    Line
    Read-Host 'Press Enter to close' | Out-Null
    exit 0
}

# 7) Restart: start the keepalive exactly as logon does, then poll /health for up to 60 s
Say ''
Say "starting the keepalive task '$taskNm' (Start-ScheduledTask) - it starts llama-swap the same way logon does"
try {
    Start-ScheduledTask -TaskName $taskNm -ErrorAction Stop
    Say '  task started'
} catch {
    Say ('  task: ' + $_.Exception.Message)
    Say '  you can also log off and on; the task runs at logon.'
}
$deadline = (Get-Date).AddSeconds(60)
$up = $false
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest -Uri "$base/health" -Method Get -TimeoutSec 5 -UseBasicParsing
        $up = $true
        break
    } catch { Start-Sleep -Seconds 3 }
}
Line
if ($up) {
    Say 'llama-swap is UP (/health answers). No model is loaded; the first request loads one, the UI shows which is loaded:'
    Say '  http://127.0.0.1:8080/ui'
} else {
    Say 'llama-swap did NOT answer /health within 60 s. The keepalive retries on its own about every 30 s;'
    Say '  check the "llama-swap Status (read only)" shortcut in a minute, and the log:'
    Say '  C:\AI\director\logs\llama-swap-keepalive.log and llama-swap.err.log in the same folder.'
}
Line
Read-Host 'Press Enter to close' | Out-Null
