$b='C:\AI\community\briefs\argon_audit_20261025'; $log="$b\forge_pause.log"; $rl='C:\Users\derek\5slock\ralph-community\logs\ralph.log'
function L($m){ "[$(Get-Date -Format o)] $m" | Out-File -Append -Encoding utf8 $log }
L "watch start (Max Architect 2, Derrick 9:39 AM CT approval): waiting for pi 5072 (iter 1) to exit; ralph ps 2700; ForgeRalphLoop disabled"
while (Get-Process -Id 5072 -ErrorAction SilentlyContinue) { Start-Sleep -Milliseconds 500 }
L "pi 5072 exited"
$t0=Get-Date
while (((Get-Date)-$t0).TotalSeconds -lt 20) { if (Select-String -Path $rl -Pattern 'iter 1 : open=' -SimpleMatch -EA 0 | ? { $_.Line -like (Get-Date -Format 'yyyy-MM-dd')+'T*' -and $_.Line -ge '2026-10-26T09:00:04' }) { break }; if (Get-CimInstance Win32_Process -Filter "ParentProcessId=2700" | ? { $_.CommandLine -match 'pi-coding-agent|cli\.js' }) { break }; Start-Sleep -Milliseconds 300 }
$kids = Get-CimInstance Win32_Process -Filter "ParentProcessId=2700"
Stop-Process -Id 2700 -Force -ErrorAction SilentlyContinue
L "stopped ralph powershell 2700 (between passes)"
foreach($k in $kids){ if($k.CommandLine -match 'pi-coding-agent|cli\.js'){ $age=((Get-Date)-$k.CreationDate).TotalSeconds; L "new pi child $($k.ProcessId) age=${age}s (just spawned, pre-render) -> stop"; Stop-Process -Id $k.ProcessId -Force -ErrorAction SilentlyContinue } }
Start-Sleep 3
$left = Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'ralph\.ps1|pi-coding-agent.*--print' -and $_.ProcessId -ne $PID }
L ("remaining ralph/pi procs: " + (($left | % ProcessId) -join ','))
"paused $(Get-Date -Format o) by Max Architect 2 for Argon medium run (Derrick 9:39 AM CT)" | Out-File -Encoding utf8 "$b\forge_paused.txt"
"paused $(Get-Date -Format o) by Max Architect 2 for Argon medium run (Derrick 9:39 AM CT)" | Out-File -Encoding utf8 'C:\AI\community\briefs\argon_medium_20261026\forge_paused.txt'
L "forge_paused.txt written (both folders)"
