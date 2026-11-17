$ErrorActionPreference='Continue'
$rc='C:\Users\derek\5slock\ralph-community'
"=== now: $(Get-Date -Format o)"
"=== ralph/pi processes"
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'ralph\.ps1|pi(\.cmd|\.exe)?\s+--print|run_graph_job|agy\.exe|main\.py|llama-swap|switchyard|discord_bridge' } | ForEach-Object { "{0} parent={1} start={2} name={3} cmd={4}" -f $_.ProcessId,$_.ParentProcessId,$_.CreationDate,$_.Name,($_.CommandLine -replace '(?i)(token|key|secret|password)=\S+','$1=***').Substring(0,[Math]::Min(220,$_.CommandLine.Length)) }
"=== git log (last 15)"
git -C $rc log -15 --date=iso-local --format='%h %ad %s'
"=== fix_plan.md diff since 2026-10-25 21:00"
$base = git -C $rc rev-list -1 --before='2026-10-25 21:00' HEAD
"base=$base"
git -C $rc diff --stat $base HEAD -- fix_plan.md
git -C $rc diff $base HEAD -- fix_plan.md | Select-String '^[+-]\s*- \[' | Select-Object -First 40 | ForEach-Object { $_.Line }
"=== ralph.log tail"
Get-Content "$rc\logs\ralph.log" -Tail 40 | ForEach-Object { $_ -replace "`0",'' }
"=== comfy queue"
try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:10002/queue).Content } catch { "comfy backend 10002: $($_.Exception.Message)" }
try { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:8080/running).Content } catch { "llama-swap running: $($_.Exception.Message)" }
"=== gpu"
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
"=== render lock"
Get-ChildItem -Recurse -Filter 'gpu-render.lock' C:\AI\director,C:\AI\community -ErrorAction SilentlyContinue | ForEach-Object { "$($_.FullName) $($_.LastWriteTime)" }
