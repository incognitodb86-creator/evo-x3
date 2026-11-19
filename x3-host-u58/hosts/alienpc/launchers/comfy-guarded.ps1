# comfy-guarded.ps1 - opens ComfyUI ONLY when the GPU is free. ALI-150 v2, 2026-10-21 (audited finding F10).
# ComfyUI is a llama-swap member: opening its page LOADS it and swaps out whatever LLM is loaded, so this must be guarded.
#   1. runs gpu_guard.ps1 -Gpu  (image-generator queue, Switchyard queue, render processes, live lock pid, GPU utilisation)
#   2. not IDLE  -> a message box with the reason, nothing opened, exit 3
#   3. IDLE      -> opens the ComfyUI page through llama-swap: http://127.0.0.1:8080/upstream/comfyui_auto/
# The long-video build, if you need it, is http://127.0.0.1:8080/upstream/comfyui_longvideo/ (README lists it; no shortcut).
# The page is reached through llama-swap, never by its own port and never the llama-swap root page.

param(
    [string]$Url = 'http://127.0.0.1:8080/upstream/comfyui_auto/'
)

$ErrorActionPreference = 'Continue'
$guardPs1 = 'C:\AI\director\scripts\gpu_guard.ps1'
$wsh = New-Object -ComObject WScript.Shell

Write-Host 'checking the GPU (gpu_guard.ps1 -Gpu) before opening ComfyUI ...'
if (-not (Test-Path -LiteralPath $guardPs1)) {
    $null = $wsh.Popup('Cannot find the guard script:' + [Environment]::NewLine + $guardPs1 + [Environment]::NewLine + [Environment]::NewLine + 'Nothing was opened.', 0, 'GPU check missing', 48)
    exit 2
}
$guardOut = & powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $guardPs1 -Gpu 2>&1
$rc = $LASTEXITCODE
$guardOut | ForEach-Object { Write-Host ('  ' + $_) }

if ($rc -ne 0) {
    $reason = ($guardOut | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($reason)) { $reason = 'guard exit ' + $rc }
    $null = $wsh.Popup('The GPU is busy, so ComfyUI was NOT opened (opening it would load it and swap out the model in use).' + [Environment]::NewLine + [Environment]::NewLine + 'Reason from gpu_guard.ps1 -Gpu:' + [Environment]::NewLine + $reason + [Environment]::NewLine + [Environment]::NewLine + 'Wait for the job to finish, then try again.', 0, 'ComfyUI not opened - GPU busy', 48)
    Write-Host 'NOT opened: GPU busy.'
    exit 3
}

Write-Host ('GPU idle - opening ' + $Url)
try {
    Start-Process $Url
} catch {
    $null = $wsh.Popup('The guard said IDLE but the page could not be opened:' + [Environment]::NewLine + $_.Exception.Message, 0, 'ComfyUI not opened', 48)
    exit 4
}
Start-Sleep -Seconds 2
