# Max harness (Derrick 7:30 AM CT Oct 31): keep Forge idle until the FLUX queue_all batch ends, then brief Forge on the long-video guard fix.
$log='C:\AI\community\runs\chain_long_video.log'
function L($m){ Add-Content $log ("{0} CT brief_forge_after_flux[{1}]: {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$PID,$m) }
L "start; waiting for queue_all.ps1 and run_queue to finish"
while($true){
  $qa=@(Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'queue_all\.ps1' -and $_.ProcessId -ne $PID }).Count
  $rq=@(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? { $_.CommandLine -match 'run_queue\.py' }).Count
  if($qa -eq 0 -and $rq -eq 0){ break }; Start-Sleep 60 }
L "FLUX batch finished; prompting forge"
$o = herdr agent prompt forge "Derrick: FLUX is done, do the long video fix now. Read and do C:\AI\community\briefs\2026-10-31-0654-long-video-guard-fix.md (FLUX has finished, so the chain will start right away)." 2>&1 | Out-String
L ("herdr prompt rc={0} {1}" -f $LASTEXITCODE, $o.Substring(0,[Math]::Min(120,$o.Length)))
