<#
restart_talk_agent.ps1 - restart the talk-lane agent in its herdr pane so a new persona file loads.
Built 2026-10-29 12:36 CT on Derek s request (persona2). It restarts ONE pane, by pid and pane id; it never
touches another agent, never touches a render, and never takes the GPU lock.

Flow: wait a grace period (so the running agent can finish its answer and report first) -> kill that process
tree -> poll the pane until its shell prompt is free -> run talk_agent_launch.ps1 in that pane -> verify a node
process carrying the persona file is back in the foreground -> log it.

It is started detached (WMI process create), so it survives being the thing it kills: a child of this agent is
inside the tree that taskkill removes, so the caller must not use a plain child process.
#>
param(
  [string]$Pane       = 'wG:p1',
  [long]$PidToKill    = 0,
  [int]$GraceSec      = 60,
  [int]$PromptTimeout = 90,
  [string]$LaunchScript = 'C:\AI\community\talk\talk_agent_launch.ps1',
  [string]$Log        = 'C:\AI\community\talk\restart_agent.log'
)
function L($m) { $l = "$(Get-Date -Format s) $m"; Add-Content -LiteralPath $Log -Value $l -Encoding UTF8 }
function Fg {
  try {
    $j = (& herdr pane process-info --pane $Pane 2>&1) -join ''
    $o = $j | ConvertFrom-Json
    return @($o.result.process_info.foreground_processes)
  } catch { return @() }
}
L "START pane=$Pane pid_to_kill=$PidToKill grace=$GraceSec launch=$LaunchScript"
Start-Sleep -Seconds $GraceSec

if ($PidToKill -gt 0) {
  $p = Get-Process -Id $PidToKill -EA SilentlyContinue
  if ($null -eq $p) { L "target pid $PidToKill is already gone, nothing to kill" }
  else {
    $r = (& taskkill /PID $PidToKill /T /F 2>&1) -join ' '
    L "taskkill rc=$LASTEXITCODE :: $r"
  }
} else { L "no pid given, skipping the kill and only running the launch command" }

$deadline = (Get-Date).AddSeconds($PromptTimeout); $free = $false
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 3
  if ((Fg).Count -eq 0) { $free = $true; break }
}
if (-not $free) { L "ABORT: pane $Pane has no free shell prompt after $PromptTimeout s, launch not sent, run it by hand: powershell -NoProfile -ExecutionPolicy Bypass -File $LaunchScript"; exit 3 }
L "pane shell prompt is free, sending the launch command"

$cmd = "powershell -NoProfile -ExecutionPolicy Bypass -File $LaunchScript"
$out = (& herdr pane run $Pane $cmd 2>&1) -join ' '
L "pane run rc=$LASTEXITCODE :: $out"

$ok = $false
$deadline = (Get-Date).AddSeconds(180)
while ((Get-Date) -lt $deadline) {
  Start-Sleep -Seconds 10
  $f = Fg
  if ($f | Where-Object { ($_.argv -join ' ') -match 'talk-persona' }) { $ok = $true; break }
}
if ($ok) {
  $f = Fg | Where-Object { ($_.argv -join ' ') -match 'talk-persona' } | Select-Object -First 1
  L "PASS: agent is back in $Pane pid=$($f.pid) argv=$(($f.argv) -join ' ')"
  exit 0
}
L "UNVERIFIED: no agent carrying the persona file was seen in $Pane within 180 s - check the pane, launch by hand if needed: $cmd"
exit 4
