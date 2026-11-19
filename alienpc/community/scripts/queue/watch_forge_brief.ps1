# watch_forge_brief.ps1 - after Max briefs Forge, catch a silent stop. No gates: it only logs and writes a STALL file.
# OK  = FORGE_REPORT.md exists, or a run_queue batch for the run dir has started.
# STALL = Forge shows idle/done (2 checks in a row) with neither.
param([string]$RunDir='C:\AI\community\runs\sslcaio_20261030',[string]$Name='sslcaio_20261030',[int]$MaxHours=6)
$log='C:\AI\community\runs\chain_long_video.log'
$herdr='C:\Users\derek\.herdr\packages\standalone\releases\0.9.5-x86_64-pc-windows-msvc\herdr.exe'
function L($m){ Add-Content $log ("{0} CT watch_forge_brief[{1}]: {2}" -f (Get-Date -f 'yyyy-MM-dd HH:mm:ss'),$PID,$m) }
$t0=Get-Date; $idle=0
L "start: watching $RunDir (FORGE_REPORT.md or run_queue batch); poll 60 s; first check after 3 min"
Start-Sleep 180
while (((Get-Date)-$t0).TotalHours -lt $MaxHours) {
  if (Test-Path "$RunDir\FORGE_REPORT.md") { L "OK: FORGE_REPORT.md written"; exit 0 }
  $rq = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'run_queue\.py' -and $_.CommandLine -match [regex]::Escape($Name) -and $_.CommandLine -notmatch 'dry-run' }
  $ql = Get-ChildItem $RunDir -Recurse -Filter _render_queue.log -EA 0 | Where-Object { $_.LastWriteTime -gt $t0 }
  if ($rq -or $ql) { L "OK: run_queue batch started for $Name"; exit 0 }
  $g = & $herdr agent get forge 2>&1 | Out-String
  if ($g -match '"agent_status":"(idle|done)"') { $idle++ } else { $idle=0 }
  if ($idle -ge 2) {
    $f="C:\AI\community\runs\STALL_$Name.txt"
    "$(Get-Date -f 'yyyy-MM-dd HH:mm') CT STALL: Forge is $($Matches[1]) with no FORGE_REPORT.md and no run_queue batch for $RunDir. Max: read Forge's session log for this run (with Derrick's OK) and re-brief." | Set-Content $f
    L "STALL: forge $($Matches[1]) with no report and no batch; wrote $f"; exit 2
  }
  Start-Sleep 60
}
L "timeout after $MaxHours h with no report/batch"; exit 3