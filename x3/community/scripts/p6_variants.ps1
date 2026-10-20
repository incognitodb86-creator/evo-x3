# P6 variants (Derek 2026-10-20 2:25 PM CT "try it both ways"): anti-burn 0.5 and intra-clip cuts, run after P6 finishes.
$py='C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\.venv\Scripts\python.exe'; $S='C:\AI\community\scripts'; $SH='C:\AI\community\shots'; $L='C:\AI\community\p6.log'
while(-not (Select-String -Path $L -Pattern 'P6 DONE' -Quiet)){ Start-Sleep 120 }
foreach($t in 'ab05','cuts','cuts_ab05'){ "$(Get-Date -f 'yyyy-MM-dd HH:mm:ss') CT P6V $t start" | Add-Content $L; & $py -u "$S\batch_queue.py" "$SH\p6_1min_$t.json" "p6_1min_$t" *> "C:\AI\community\p6v_$t.out"; "$(Get-Date -f 'yyyy-MM-dd HH:mm:ss') CT P6V $t rc=$LASTEXITCODE" | Add-Content $L }
try { Invoke-WebRequest http://127.0.0.1:8080/unload -UseBasicParsing -TimeoutSec 120 | Out-Null } catch {}
"$(Get-Date -f 'yyyy-MM-dd HH:mm:ss') CT P6V DONE" | Add-Content $L
