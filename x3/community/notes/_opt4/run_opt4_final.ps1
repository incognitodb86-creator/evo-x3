# OPT4 final verification bench (ralph pass 2026-10-31): strata-bench.ps1 x3 at the kept config.
# GPU lock held for the whole item, released in a finally. Owner = the live ralph.ps1 process pid.
$ErrorActionPreference = 'Stop'
$dir = 'C:\AI\community\notes\_opt4'
$out = Join-Path $dir 'bench.jsonl'
$log = Join-Path $dir 'final.log'
function L($m) { $line = "{0} {1}" -f (Get-Date -Format s), $m; Add-Content -LiteralPath $log -Value $line -Encoding UTF8; Write-Output $line }

# live ralph pid = the owner of the lock (a dead pid is stale to gpu_guard)
$ralph = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
  Where-Object { $_.CommandLine -like '*ralph.ps1*' } | Select-Object -First 1 -ExpandProperty ProcessId
if (-not $ralph) { $ralph = 0 }
L "ralph owner pid = $ralph"

$ramFree = { [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2) }
$vram = { (nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null) }

& 'C:\AI\director\scripts\gpu_lock.ps1' -Acquire -Owner $ralph -Note 'OPT4 final bench' | Tee-Object -FilePath $log -Append
try {
  L ("pre RAM free GB = " + (& $ramFree) + " ; VRAM used MiB = " + (& $vram))
  & 'C:\AI\community\notes\strata-bench.ps1' -Base 'http://127.0.0.1:8080' -Model 'coding_swift15_iq3s_esp' `
      -Runs 3 -Tag 'opt4-final' -Out $out | ForEach-Object { L ("row " + $_) }
  L ("post RAM free GB = " + (& $ramFree) + " ; VRAM used MiB = " + (& $vram))
}
finally {
  & 'C:\AI\director\scripts\gpu_lock.ps1' -Release -Owner $ralph | Tee-Object -FilePath $log -Append
  & 'C:\AI\director\scripts\gpu_lock.ps1' | Tee-Object -FilePath $log -Append
}
