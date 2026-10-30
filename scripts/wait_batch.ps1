<# wait_batch.ps1 - one blocking wait for a run_queue.py batch (phase 2 S11, Max 2026-10-30, Derrick 11:01 AM CT go).
Why: every Forge model call makes llama-swap stop comfyui_auto to load the LLM, which kills the clip in flight.
Use: after launching a batch, run this ONCE and make no other tool or model calls until it returns.
  powershell -File C:\AI\community\scripts\wait_batch.ps1 -BatchPid <PID> -RunDir <run folder>
It returns only when the batch process exits, then prints DONE/FAIL counts and the last lines of the log. #>
param([Parameter(Mandatory)][int]$BatchPid, [Parameter(Mandatory)][string]$RunDir)
$log = Join-Path $RunDir '_render_queue.log'
$p = Get-Process -Id $BatchPid -ErrorAction SilentlyContinue
if ($p) { "waiting on batch PID $BatchPid (started $($p.StartTime)) - no polling"; $p.WaitForExit() } else { "batch PID $BatchPid not running" }
"batch exited $(Get-Date -Format 'yyyy-MM-ddTHH:mm:sszzz')"
if (Test-Path $log) {
  $l = Get-Content $log
  "DONE ok: $(@($l | Select-String ' DONE ').Count)  FAIL: $(@($l | Select-String ' FAIL ').Count)"
  $l | Select-Object -Last 8
}
