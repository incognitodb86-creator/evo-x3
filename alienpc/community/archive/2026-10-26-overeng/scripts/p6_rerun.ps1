$py='C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\.venv\Scripts\python.exe'; $L='C:\Users\derek\5slock\ralph-community\logs'
& $py -u C:\AI\community\scripts\p6.py *> "$L\p6.out"
"$(Get-Date -f s) P6 exit $LASTEXITCODE" | Add-Content "$L\chain.log"; "CHAIN_DONE $(Get-Date -f s)" | Set-Content "$L\CHAIN_DONE.txt"
