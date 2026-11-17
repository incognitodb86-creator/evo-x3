Set-Location C:\AI
$b='C:\AI\community\briefs\argon_audit_20261025'
"[$(Get-Date -Format o)] flash_impl start pid=$PID" | Out-File -Append "$b\flash_impl.log"
$dirs = @('C:\AI','C:\Users\derek\5slock','C:\Users\derek\.pi','C:\Users\derek\HardcoreNSFW-TestRuntime')
if (Test-Path 'D:\AI\director') { $dirs += 'D:\AI\director' }
$add = foreach($d in $dirs){ '--add-dir'; $d }
& 'C:\Users\derek\AppData\Local\agy\bin\agy.exe' -p "Read and carry out the brief at C:\AI\community\briefs\argon_audit_20261025\flash_impl_brief.md. This is IMPLEMENT MODE: do the 12 to-do items in order, one change per commit with its step ID, logging each in progress.md in that folder. Obey every HARD LIMIT in the brief." --model gemini-3.8-flash-high --mode auto --dangerously-skip-permissions @add --print-timeout 0 --log-file "$b\flash_impl.agy.log" *> "$b\flash_impl_stdout.md"
"[$(Get-Date -Format o)] flash_impl end exit=$LASTEXITCODE" | Out-File -Append "$b\flash_impl.log"
powershell -NoProfile -ExecutionPolicy Bypass -File "$b\hashes.ps1" -Out post_impl_hashes.txt | Out-Null
"[$(Get-Date -Format o)] post snapshot written" | Out-File -Append "$b\flash_impl.log"
