# relaunch_ralph.ps1 - restart a Forge Ralph loop with new parameters at a clean point (Forge, 2026-11-05).
# Why: a brief can add fix_plan.md items AFTER a loop has started, so its -Max cap (skill rule: item count + 2, capped
# at 12) and pass limits have to be re-applied. ralph.ps1 refuses a second copy (logs\ralph.lock, exit 4), so the old
# loop must be stopped first. Order matters: the old loop is killed while its current pass is in flight, i.e. BEFORE the
# loop can start a new pass, so no fresh pass (which may already have woken ComfyUI) is ever cut in half. Nothing here
# touches llama-swap, ComfyUI, strata, pi-mobile, pi, the gate, or another agent's loop (Sydney's loop has a different
# root and is never matched by this root filter).
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\community\scripts\relaunch_ralph.ps1 \
#     -Root C:\Users\derek\5slock\ralph-community -Max 12 -PassLimitSec 3600 -IterationTimeoutSec 3600 -GpuWaits 90 -GpuWaitSec 120
param(
  [string]$Root = 'C:\Users\derek\5slock\ralph-community',
  [int]$Max = 12,
  [int]$PassLimitSec = 3600,
  [int]$IterationTimeoutSec = 3600,
  [int]$GpuWaits = 90,
  [int]$GpuWaitSec = 120
)
function Say($m) { "$(Get-Date -Format s) $m" }
$K = [IO.Path]::GetFullPath($Root).TrimEnd('\')
if (-not (Test-Path -LiteralPath "$K\ralph.ps1")) { Say "no ralph.ps1 in $K"; exit 1 }
$lockFile = "$K\logs\ralph.lock"

$old = $null
if (Test-Path -LiteralPath $lockFile) {
  $t = ([IO.File]::ReadAllText($lockFile)).Trim()
  if ($t -match '^\d+$') { $old = [int]$t }
}
if ($old -and (Get-Process -Id $old -EA SilentlyContinue)) {
  $cl0 = (Get-CimInstance Win32_Process -Filter "ProcessId=$old").CommandLine
  if ($cl0 -notmatch [regex]::Escape("$K\ralph.ps1")) { Say "ralph.lock pid $old is not a loop of this root - leaving it alone"; $old = $null } }
if ($old -and (Get-Process -Id $old -EA SilentlyContinue)) {
  $cl = (Get-CimInstance Win32_Process -Filter "ProcessId=$old").CommandLine
  Say "stopping old loop PID $old : $cl"
  & taskkill /PID $old /T /F 2>&1 | ForEach-Object { Say "  taskkill: $_" }
  Start-Sleep -Seconds 3
  if (Get-Process -Id $old -EA SilentlyContinue) { Say "OLD LOOP STILL ALIVE - not starting a second copy"; exit 1 }
  Say "old loop stopped (its in-flight pass tree was killed with it; no newer pass had been started)"
} else {
  Say "no live loop pid in ralph.lock (stale/absent: $(if ($old) { "pid $old not alive" } else { 'no pid' }))"
}

$loopRe = '-File\s+"?' + [regex]::Escape("$K\ralph.ps1") + '"?'   # the loop's OWN -File invocation only: a pi chat/loop pass whose prompt text merely MENTIONS ralph.ps1 (its command line carries the prompt) must never look like a live loop.
$alive = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'powershell.exe' -and $_.CommandLine -match $loopRe })
if ($alive.Count -gt 0) { Say "refusing to start: ralph.ps1 for this root still alive: $($alive.ProcessId -join ',')"; exit 1 }

$cmd = "powershell -NoProfile -ExecutionPolicy Bypass -File $K\ralph.ps1 -Max $Max -PassLimitSec $PassLimitSec -IterationTimeoutSec $IterationTimeoutSec -GpuWaits $GpuWaits -GpuWaitSec $GpuWaitSec"
$r = Invoke-CimMethod Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $K }
if ($r.ReturnValue -ne 0) { Say "WMI Create failed ReturnValue=$($r.ReturnValue)"; exit 1 }
$newPid = $r.ProcessId
Say "started new loop PID $newPid : $cmd"
Start-Sleep -Seconds 8
$lockNow = if (Test-Path -LiteralPath $lockFile) { ([IO.File]::ReadAllText($lockFile)).Trim() } else { '(none)' }
Say "ralph.lock now = $lockNow (expected new PID $newPid)"
if (Test-Path -LiteralPath "$K\logs\ralph.log") { Get-Content -LiteralPath "$K\logs\ralph.log" -Tail 4 | ForEach-Object { Say "  log: $_" } }
"NEW_LOOP_PID=$newPid"
