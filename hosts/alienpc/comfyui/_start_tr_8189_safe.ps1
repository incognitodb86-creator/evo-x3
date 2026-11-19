# Safe TR :8189 start - NEVER kill other python / never touch :8188
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$venvPy = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) { throw "No venv python at $venvPy" }
$listen = netstat -ano | Select-String ':8189\s+.*LISTENING'
if ($listen) { Write-Host '8189 already listening; abort'; exit 0 }
$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$env:CUDA_VISIBLE_DEVICES = '0'
$env:PYTHONUNBUFFERED = '1'
$logOut = Join-Path $PSScriptRoot 'comfy_8189_stdout.log'
$logErr = Join-Path $PSScriptRoot 'comfy_8189_stderr.log'
if (Test-Path $logOut) { Copy-Item $logOut ($logOut + '.prev') -Force }
if (Test-Path $logErr) { Copy-Item $logErr ($logErr + '.prev') -Force }
$argv = @('-u','main.py','--listen','127.0.0.1','--port','8189','--fp8_e4m3fn-unet','--fp8_e4m3fn-text-enc','--lowvram')
Write-Host ('Starting TR ComfyUI :8189 via ' + $venvPy)
Write-Host ('argv: ' + ($argv -join ' '))
$p = Start-Process -FilePath $venvPy -ArgumentList $argv -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'comfy_8189.pid'), $p.Id.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Host ('Started PID=' + $p.Id)
