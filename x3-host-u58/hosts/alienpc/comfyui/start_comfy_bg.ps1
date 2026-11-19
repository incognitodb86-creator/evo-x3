# Auto-generated: start Comfy in bg using venv python directly (no arg parse issues)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$venvPy = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) { throw "No venv python at $venvPy" }
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 800
$env:PYTORCH_CUDA_ALLOC_CONF = 'expandable_segments:True'
$env:CUDA_VISIBLE_DEVICES = '0'
$env:PYTHONUNBUFFERED = '1'
$logOut = Join-Path $PSScriptRoot 'comfy_stdout.log'
$logErr = Join-Path $PSScriptRoot 'comfy_stderr.log'
Write-Host "Starting ComfyUI with venv: $venvPy (lowvram for 16GB headroom)"
$p = Start-Process -FilePath $venvPy -ArgumentList '-u','main.py','--listen','127.0.0.1','--port','8188','--fp8_e4m3fn-unet','--fp8_e4m3fn-text-enc','--lowvram' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError $logErr -PassThru
Write-Host "Comfy python PID: $($p.Id)"
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'comfy.pid'), $p.Id.ToString(), [System.Text.UTF8Encoding]::new($false))
Start-Sleep 3
Write-Host "Boot initiated. Use poll script or check logs."