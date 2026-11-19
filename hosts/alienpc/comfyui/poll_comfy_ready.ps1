# Poll until healthy or timeout
param([int]$MaxSeconds=180)
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
$base='http://127.0.0.1:8188'
Write-Host "Polling $base/system_stats (max $MaxSeconds s)..."
$sw=[Diagnostics.Stopwatch]::StartNew()
$healthy=$false
while($sw.Elapsed.TotalSeconds -lt $MaxSeconds){
  Start-Sleep -Milliseconds 1200
  try {
    $s = Invoke-RestMethod "$base/system_stats" -TimeoutSec 4 -ErrorAction Stop
    if($s -and $s.devices -and $s.devices.Count -gt 0){
      $d=$s.devices[0]
      $vramFree = [math]::Round($d.vram_free / 1MB, 0)
      Write-Host "HEALTHY: $($d.name) VRAM_free=${vramFree}MB  elapsed=$([int]$sw.Elapsed.TotalSeconds)s"
      # Also check loras loaded if possible via /object_info or just success
      $healthy=$true
      break
    }
  } catch {
    $tail = ''
    if(Test-Path 'comfy_stdout.log'){ $tail = (Get-Content 'comfy_stdout.log' -Tail 1 -ErrorAction SilentlyContinue) }
    if( ($sw.Elapsed.TotalSeconds % 10) -lt 2 ){ Write-Host "  ... $($sw.Elapsed.TotalSeconds.ToString('0'))s : $tail" }
  }
}
if($healthy){
  Write-Host '=== COMFY READY FOR TESTS ==='
  exit 0
} else {
  Write-Host 'TIMEOUT. Last logs:'
  if(Test-Path 'comfy_stdout.log'){ Get-Content 'comfy_stdout.log' -Tail 25 }
  exit 1
}