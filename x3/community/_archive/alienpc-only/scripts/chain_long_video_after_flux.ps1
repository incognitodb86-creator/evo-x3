$ErrorActionPreference='Continue'
$log='C:\AI\community\runs\chain_long_video.log'; $d='C:\AI\community\runs\sslcaio_20261030'
$py='C:\AI\director\.venv\Scripts\python.exe'; $rq='C:\AI\community\scripts\run_queue.py'; $lock='C:\AI\locks\gpu-render.lock'
function L($m){ Add-Content -Path $log -Value ("{0} CT chain_long_video_after_flux[{1}]: {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$PID,$m) }
function LockBusy{ if(!(Test-Path $lock)){return $false}; $t=Get-Content $lock -Raw -EA SilentlyContinue; $ids=[regex]::Matches("$t",'\d{2,7}')|%{[int]$_.Value}; foreach($i in $ids){ if(Get-Process -Id $i -EA SilentlyContinue){return $true} }; return $false }
function FluxBusy{ $p=Get-CimInstance Win32_Process -EA SilentlyContinue; $qa=@($p|?{$_.CommandLine -match 'queue_all\.ps1' -and $_.ProcessId -ne $PID}); $rqp=@($p|?{$_.Name -match 'python' -and $_.CommandLine -match 'run_queue\.py'}); return @($qa.Count,$rqp.Count,(LockBusy)) }
L "started; waiting for queue_all.ps1 FLUX batch to finish (poll 60 s)"
while($true){ $b=FluxBusy; if($b[0] -eq 0 -and $b[1] -eq 0 -and -not $b[2]){break}; Start-Sleep 60 }
L "FLUX batch finished (no queue_all, no run_queue, lock free); starting ss, lc, aio"
$batches=@(@('ss',124,'768x1344'),@('lc',729,'512x896'),@('aio',243,'768x1344'))
foreach($x in $batches){ $q="$d\_order_$($x[0]).json"
 while($true){ L "batch $($x[0]) start frames=$($x[1]) size=$($x[2])"
  & $py $rq --run-dir $d --queue $q --resume --frames $x[1] --size $x[2] *>> "$d\_chain_$($x[0]).out.log"; $rc=$LASTEXITCODE
  L "batch $($x[0]) rc=$rc"
  if($rc -eq 7){ L "GPU busy; retry in 60 s"; Start-Sleep 60; continue }
  if($rc -ne 0){ L "STOP chain on rc=$rc (batch $($x[0]))"; exit $rc }
  break } }
L "DONE all three batches (ss, lc, aio) ran"
