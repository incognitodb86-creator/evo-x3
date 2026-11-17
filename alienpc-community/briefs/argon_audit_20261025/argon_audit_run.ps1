Set-Location C:\AI
$b='C:\AI\community\briefs\argon_audit_20261025'
"[$(Get-Date -Format o)] argon_audit start" | Out-File -Append "$b\argon_audit.log"
& 'C:\Users\derek\AppData\Local\agy\bin\agy.exe' -p "Read and carry out the brief at C:\AI\community\briefs\argon_audit_20261025\brief.md. This is PLAN MODE: read and analyze only, change nothing; write only the plan file named in the brief." --model gemini-4-argon-high --mode plan --dangerously-skip-permissions --add-dir C:\AI --add-dir C:\Users\derek\5slock --add-dir C:\Users\derek\.pi --add-dir C:\Users\derek\HardcoreNSFW-TestRuntime --print-timeout 0 --log-file "$b\argon_audit.agy.log" *> "$b\plan_stdout.md"
"[$(Get-Date -Format o)] argon_audit end exit=$LASTEXITCODE" | Out-File -Append "$b\argon_audit.log"
