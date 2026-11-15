$ErrorActionPreference = "Continue"
$run = "C:\evo-x3\runs\h2_usb_backup_20261114"
Set-Location C:\evo-x3
$agy = "$env:LOCALAPPDATA\agy\bin\agy.exe"
$prompt = "Read C:\evo-x3\runs\h2_usb_backup_20261114\brief.md and do it fully. Respect every STOP. Never print secrets or recovery keys. Write C:\evo-x3\runs\h2_usb_backup_20261114\RESULT.md."
$meta = Join-Path $run "agy.meta.txt"
@("start=$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))","model=gemini-4-hydrogen-low","pid_wrapper=$PID") | Set-Content -LiteralPath $meta -Encoding utf8
& $agy -p $prompt --model gemini-4-hydrogen-low --dangerously-skip-permissions --add-dir C:\evo-x3 --disable-slash-commands --print-timeout 0 --log-file (Join-Path $run "agy.log") 1> (Join-Path $run "agy.out") 2> (Join-Path $run "agy.err")
$code = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }
"exit_code=$code" | Add-Content -LiteralPath $meta -Encoding utf8
"end=$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" | Add-Content -LiteralPath $meta -Encoding utf8
