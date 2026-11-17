Set-Location C:\AI
$b='C:\AI\community\briefs\argon_medium_20261026'
"[$(Get-Date -Format o)] argon_medium start pid=$PID" | Out-File -Append "$b\argon_medium.log"
$dirs = @('C:\AI','C:\Users\derek\5slock','C:\Users\derek\.pi','C:\Users\derek\HardcoreNSFW-TestRuntime')
$add = foreach($d in $dirs){ '--add-dir'; $d }
& 'C:\Users\derek\AppData\Local\agy\bin\agy.exe' -p "Read and carry out the brief at C:\AI\community\briefs\argon_medium_20261026\argon_medium_brief.md. Do the to-do items M0..M14 in order, one change per commit with its step ID, logging each in progress.md in that folder. Obey every HARD LIMIT in the brief." --model gemini-4-argon-medium --mode auto --dangerously-skip-permissions @add --print-timeout 0 --log-file "$b\argon_medium.agy.log" *> "$b\argon_medium_stdout.md"
"[$(Get-Date -Format o)] argon_medium end exit=$LASTEXITCODE" | Out-File -Append "$b\argon_medium.log"
powershell -NoProfile -ExecutionPolicy Bypass -File "$b\hashes_m.ps1" -Out post_hashes.txt | Out-Null
"[$(Get-Date -Format o)] post snapshot written" | Out-File -Append "$b\argon_medium.log"

