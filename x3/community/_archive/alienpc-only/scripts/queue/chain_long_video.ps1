# chain_long_video.ps1 - Max long-video-queue lease, Derrick 12:01 AM "yes" + 12:07 AM "queue it to start so it goes automatically".
# Waits for Klein explicit FIRST phase (26 outputs + lock gone), clears the stale ComfyUI process so new nodes load on next wake,
# then briefs Forge (herdr agent prompt) to finish staging and submit via run_queue.py. Never starts Klein k / n12 / finish.
$ErrorActionPreference = 'Continue'
$log  = 'C:\AI\community\runs\chain_long_video.log'
$run  = 'C:\AI\community\runs\2026-10-31_klein_explicit_0010'
$lock = 'C:\AI\locks\gpu-render.lock'
$brief= 'C:\AI\community\briefs\2026-10-31-0010-seed-longclip-aio-finish-and-run.md'
$herdr= 'C:\Users\derek\.herdr\packages\standalone\releases\0.9.5-x86_64-pc-windows-msvc\herdr.exe'
function L($m){ Add-Content $log ("{0} CT chain_long_video[{1}]: {2}" -f (Get-Date -f 'yyyy-MM-dd HH:mm:ss'),$PID,$m) }
L "start; waiting on 26 render_ok.json in $run and $lock gone (poll 60 s)"
$n=0
while ($true) {
  $ok = (Get-ChildItem $run -Recurse -Filter render_ok.json -EA 0 | Measure-Object).Count
  $held = Test-Path $lock
  $rq = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'run_queue\.py' -and $_.CommandLine -match 'klein_explicit_0010' }
  if ($ok -ge 26 -and -not $held -and -not $rq) { L "Klein first phase done: render_ok=$ok, lock free, run_queue gone"; break }
  if ($ok -lt 26 -and -not $held -and -not $rq) { L "Klein batch ended with only $ok/26 render_ok and no lock: STOP, not chaining (Max to check)"; exit 3 }
  if (($n++ % 10) -eq 0) { L "waiting: render_ok=$ok/26 lock_held=$held run_queue_alive=$([bool]$rq)" }
  Start-Sleep 60
}
Start-Sleep 30
# restart: run_queue unloads comfyui_auto at batch end; stop only a leftover ComfyUI main.py (never llama-swap/strata/hub/pi)
$cf = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'ComfyUI\\main\.py' -and ($_.CommandLine -match 'comfy-longvideo' -or $_.CommandLine -match 'HardcoreNSFW-TestRuntime') }
if ($cf) { foreach($p in $cf){ L "stopping leftover ComfyUI pid $($p.ProcessId): $($p.CommandLine)"; Stop-Process -Id $p.ProcessId -Force -EA 0 } } else { L "ComfyUI already unloaded by run_queue; next wake starts it fresh with Continuum/Multishot/SelfLift/UniBlockSwap" }
Start-Sleep 10
if (Test-Path $lock) { L "GPU lock taken by someone else after Klein; Forge's run_queue will wait its turn" }
# brief Forge
$tries=0
while ($tries -lt 30) {
  $g = & $herdr agent get forge 2>&1 | Out-String
  if ($g -match '"agent_status":"(idle|done)"') { break }
  L "forge not idle yet, waiting 60 s"; $tries++; Start-Sleep 60
}
$msg = "New brief from Max (Derrick approved 12:01 AM + 12:07 AM CT): read and do $brief . Klein first phase is done, GPU lock free, Continuum @308653c installed, ComfyUI restarted. Finish SS/LC/AIO staging steps 4-6, dry-run every job, then submit via run_queue.py --detach if it passes. Fictional adults only, approved_characters read-only, run_queue safety check stays, one GPU job via the lock, no images in chat. Do not start Klein k/n12/finish."
$r = & $herdr agent prompt forge $msg 2>&1 | Out-String
L ("herdr agent prompt forge rc={0}: {1}" -f $LASTEXITCODE, ($r -replace '\s+',' ').Substring(0,[Math]::Min(300,($r -replace '\s+',' ').Length)))
Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-WindowStyle','Hidden','-File','C:\AI\community\scripts\queue\watch_forge_brief.ps1' -WindowStyle Hidden
L "chain done; Forge stages + submits; watch_forge_brief.ps1 launched; lease stays open"