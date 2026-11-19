# llama-swap-status.ps1 - READ ONLY status check. ALI-150 v2, 2026-10-21.
# It only reads: GET http://127.0.0.1:8080/health, GET http://127.0.0.1:8080/running,
# the scheduled task state, and the llama-swap process list. If something is down it says so and
# changes nothing: no start, no end, no reload, no unload, no model load.
# Written by ALI-150 v2; audited finding F8. Run only from the "llama-swap Status (read only)" shortcut.

$ErrorActionPreference = 'Continue'
$base   = 'http://127.0.0.1:8080'
$taskNm = 'Switchyard llama-swap'

function Get-ReadOnlyJson([string]$url) {
    # GET only, short timeout, never writes anything
    try {
        $r = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 5 -UseBasicParsing
        return [pscustomobject]@{ up = $true; code = [int]$r.StatusCode; body = ("$($r.Content)").Trim() }
    } catch {
        return [pscustomobject]@{ up = $false; code = 0; body = $_.Exception.Message }
    }
}

Write-Host ''
Write-Host 'llama-swap status - READ ONLY. Nothing here starts, ends, unloads or loads anything.'
Write-Host ('time: ' + (Get-Date -Format 's'))
Write-Host (('-' * 78))

$h = Get-ReadOnlyJson "$base/health"
if ($h.up) {
    Write-Host ("/health   : ANSWERING (HTTP {0}) {1}" -f $h.code, $h.body)
} else {
    Write-Host ('/health   : NOT ANSWERING - ' + $h.body)
    Write-Host '            llama-swap is DOWN. It comes back by itself at the next logon, or use the "Restart (kills loaded model)" shortcut.'
}

$r = Get-ReadOnlyJson "$base/running"
if ($r.up) {
    Write-Host ('/running  : ' + $(if ([string]::IsNullOrWhiteSpace($r.body)) { '(no model loaded)' } else { $r.body }))
    Write-Host '            open http://127.0.0.1:8080/ui in a browser to see the full model list and what is loaded now.'
} else {
    Write-Host ('/running  : NOT ANSWERING - ' + $r.body)
}

Write-Host (('-' * 78))
Write-Host "scheduled task '$taskNm' (the keepalive that starts llama-swap at logon):"
try {
    $t  = Get-ScheduledTask -TaskName $taskNm -ErrorAction Stop
    $i  = $t | Get-ScheduledTaskInfo
    Write-Host ('  state       : ' + $t.State)
    Write-Host ('  last run    : ' + $i.LastRunTime)
    Write-Host ('  last result : ' + $i.LastTaskResult)
    if ($t.State -eq 'Running') { Write-Host '  note        : the keepalive loop is running; if llama-swap dies it will be started again within ~30 s.' }
    if ($t.State -eq 'Disabled') { Write-Host '  WARNING     : the task is DISABLED - llama-swap will NOT come back at logon. Re-enable it in Task Scheduler; no launcher does that.' }
} catch {
    Write-Host ('  task not found or not readable: ' + $_.Exception.Message)
}

Write-Host (('-' * 78))
Write-Host 'llama-swap process:'
$procs = @(Get-Process llama-swap -ErrorAction SilentlyContinue)
if ($procs.Count -eq 0) {
    Write-Host '  no llama-swap process'
} else {
    foreach ($p in $procs) {
        Write-Host ('  pid ' + $p.Id + '  started ' + $(try { $p.StartTime } catch { '?' }) + '  ' + $p.Path)
    }
    Write-Host '  note: the model processes (Strata / llama-server / image generator) are children; the UI page above shows what is loaded.'
}
Write-Host (('-' * 78))
Write-Host 'That was a read-only check. GPU work was not touched.'
Read-Host 'Press Enter to close' | Out-Null
