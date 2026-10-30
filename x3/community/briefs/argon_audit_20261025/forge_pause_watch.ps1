$b='C:\AI\community\briefs\argon_audit_20261025'; $log="$b\forge_pause.log"
function L($m){ "[$(Get-Date -Format o)] $m" | Out-File -Append -Encoding utf8 $log }
L "watch start: waiting for pi 36784 to exit; ralph ps 2908"
while (Get-Process -Id 36784 -ErrorAction SilentlyContinue) { Start-Sleep -Milliseconds 500 }
L "pi 36784 exited"
Stop-Process -Id 2908 -Force -ErrorAction SilentlyContinue
$kids = Get-CimInstance Win32_Process -Filter "ParentProcessId=2908"
L "stopped ralph powershell 2908 (between passes)"
foreach($k in $kids){ if($k.CommandLine -match 'pi-coding-agent|cli\.js --print'){ $age=((Get-Date)-$k.CreationDate).TotalSeconds; L "new pi child $($k.ProcessId) age=${age}s (just spawned, pre-render) -> stop"; Stop-Process -Id $k.ProcessId -Force -ErrorAction SilentlyContinue } }
Start-Sleep 3
$left = Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'ralph\.ps1|pi-coding-agent.*--print' -and $_.ProcessId -ne $PID }
L ("remaining ralph/pi procs: " + (($left | % ProcessId) -join ','))
"paused $(Get-Date -Format o)" | Out-File -Encoding utf8 "$b\forge_paused.txt"
L "forge_paused.txt written"
