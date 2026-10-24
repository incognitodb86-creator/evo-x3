$K='C:\Users\derek\5slock\ralph-community'; $L="$K\logs"
$PID | Set-Content "$L\reset_launcher.pid"
while(Get-Process -Id 11380 -ErrorAction SilentlyContinue){ Start-Sleep 10 }
"old loop 11380 exited (seen) $(Get-Date -Format s)" | Add-Content "$L\reset_launch.log"
$cli="$env:APPDATA\npm\node_modules\@earendil-works\pi-coding-agent\dist\bundle\cli.js"
$a="`"$cli`" --print --provider llama-swap --model coding_swift15_iq3s --session-dir `"$K\sessions`" `"@$K\RESET_BRIEF_20261023.md`" `"Follow RESET_BRIEF_20261023.md exactly. Do the reset yourself, then run the baseline test and write BASELINE_TEST_20261023.md.`""
$p=Start-Process node -ArgumentList $a -WorkingDirectory $K -RedirectStandardOutput "$L\reset_20261023.log" -RedirectStandardError "$L\reset_20261023.err.log" -WindowStyle Hidden -PassThru
$p.Id | Set-Content "$L\reset_pi.pid"
"forge reset pi started pid $($p.Id) $(Get-Date -Format s)" | Add-Content "$L\reset_launch.log"
$p.WaitForExit(); "forge reset pi exited code $($p.ExitCode) $(Get-Date -Format s)" | Add-Content "$L\reset_launch.log"
