<#
.SYNOPSIS
  Safe preflight + opt-in remediation script for AlienPc ComfyUI (RTX 5070 Ti 16 GB).
.DESCRIPTION
  Runs read-only checks by default (-Mode Audit). Pass -Mode Apply (supports -WhatIf)
  on AlienPc after verifying the GPU is idle:
    1. Checks model roots in extra_model_paths.yaml for NTFS junctions/symlinks
       that break comfy-aimdo Dynamic VRAM caching (ComfyUI #14276).
    2. Audits C:\AI\director\config\llama-swap.yaml for leftover LLM slots and missing
       --use-ck-attention / --disable-pinned-memory flags; backs up and installs
       llama-swap.alienpc-comfy-only.yaml when -ApplyLlamaSwap is passed.
    3. Audits (and with -UpgradePackages fixes) venv package collisions:
       - upgrades comfy-kitchen>=0.2.41 and comfy-aimdo>=0.6.0 (plain comfy-kitchen so Windows torch\lib cublas64_13.dll is used without duplicate nvidia-cublas DLL conflicts)
       - resolves CPU onnxruntime overwriting onnxruntime-gpu while pinning the existing onnxruntime-gpu version (1.26.0)
       - resolves triple OpenCV collision (opencv-python 4.11 + contrib 4.13 + headless 4.13)
    4. Audits (and with -PruneCustomNodes disables via .disabled suffix):
       - ComfyUI-MiniMaxH3-Prompt-Writer in comfyui_auto (unused UI modal)
       - Banned face-swap/ID packs in comfyui_longvideo (ComfyUI-PuLID-Flux, ComfyUI_PuLID_Flux_ll, comfyui-reactor-node)
    5. Audits (and with -ApplyCommunityScripts backs up to _archive\ and updates) C:\AI\community scripts:
       - scripts\comm.py, scripts\make_b2_request.py, scripts\run_graph_job.py, scripts\run_queue.py, sy_test_graph.json
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [ValidateSet('Audit', 'Apply')]
    [string]$Mode = 'Audit',
    [switch]$ApplyLlamaSwap,
    [switch]$ApplyCommunityScripts,
    [switch]$UpgradePackages,
    [switch]$PruneCustomNodes,
    [string]$ComfyAutoRoot = 'C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI',
    [string]$ComfyLongRoot = 'C:\AI\comfy-longvideo\ComfyUI',
    [string]$CommunityRoot = 'C:\AI\community',
    [string]$LlamaSwapConfig = 'C:\AI\director\config\llama-swap.yaml',
    [string]$LockFile = 'C:\AI\locks\gpu-render.lock'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CleanYaml = Join-Path $ScriptDir 'llama-swap.alienpc-comfy-only.yaml'

Write-Host "=== [1/6] GPU Render Lock & Active Queue Check ==="
if (Test-Path -LiteralPath $LockFile) {
    $rawLock = (Get-Content -LiteralPath $LockFile -Raw -ErrorAction SilentlyContinue).Trim()
    if ($rawLock -match '^(\d+)') {
        $lockPid = [int]$Matches[1]
        if (Get-Process -Id $lockPid -ErrorAction SilentlyContinue) {
            throw "ABORT: $LockFile is held by live PID $lockPid ($rawLock). Wait for active render to finish."
        }
    }
}
Write-Host "  OK: No live PID holds $LockFile"

Write-Host "=== [2/6] Model Root ReparsePoint (Symlink/Junction) Audit (ComfyUI #14276) ==="
$ModelRoots = @(
    (Join-Path $ComfyAutoRoot 'models'),
    (Join-Path $ComfyLongRoot 'models'),
    'E:\LTX_Models',
    'C:\Users\derek\HardcoreNSFW-LTX-Pipeline\ComfyUI\models'
)
$reparseHits = @()
foreach ($mr in $ModelRoots) {
    if (-not (Test-Path -LiteralPath $mr)) {
        Write-Host "  SKIP (not present): $mr"
        continue
    }
    $rootItem = Get-Item -LiteralPath $mr -Force
    if ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        $reparseHits += $rootItem.FullName
    }
    $subHits = @(Get-ChildItem -LiteralPath $mr -Force -Recurse -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
        Select-Object -ExpandProperty FullName)
    $reparseHits += $subHits
}
if ($reparseHits.Count -gt 0) {
    Write-Warning ("  FOUND {0} symlink/junction folder(s) under model roots (breaks comfy-aimdo VBAR caching):" -f $reparseHits.Count)
    $reparseHits | ForEach-Object { Write-Warning "    - $_" }
} else {
    Write-Host "  OK: 0 symlinks/junctions found across model directories (extra_model_paths.yaml clean)."
}

Write-Host "=== [3/6] AlienPc llama-swap.yaml Audit (No Local LLMs + --use-ck-attention) ==="
if (Test-Path -LiteralPath $LlamaSwapConfig) {
    $lsRaw = Get-Content -LiteralPath $LlamaSwapConfig -Raw
    $hasLlm = $lsRaw -match '(?m)^\s*(coding_\w+|strata\w*|vl_judge|qwen3vl_judge|gemma4\w*)\s*:'
    $hasCk = $lsRaw -match '--use-ck-attention'
    $hasNoPin = $lsRaw -match '--disable-pinned-memory'
    Write-Host ("  Current {0}: llm_slots_present={1}, --use-ck-attention={2}, --disable-pinned-memory={3}" -f $LlamaSwapConfig, $hasLlm, $hasCk, $hasNoPin)
    if ($Mode -eq 'Apply' -and $ApplyLlamaSwap) {
        $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
        $bak = "$LlamaSwapConfig.bak-$stamp"
        if ($PSCmdlet.ShouldProcess($LlamaSwapConfig, "Backup to $bak and install ComfyUI-only llama-swap.yaml")) {
            Copy-Item -LiteralPath $LlamaSwapConfig -Destination $bak -Force
            Copy-Item -LiteralPath $CleanYaml -Destination $LlamaSwapConfig -Force
            Write-Host "  APPLIED: Installed $CleanYaml -> $LlamaSwapConfig (backup: $bak)"
        }
    }
} else {
    Write-Warning "  MISSING: $LlamaSwapConfig not found on this machine."
}

Write-Host "=== [4/6] Custom Nodes Audit ==="
$PruneMap = @(
    @{ Root = $ComfyAutoRoot; Name = 'ComfyUI-MiniMaxH3-Prompt-Writer'; Reason = 'Unused browser modal; prompts authored headlessly on EVO-X3' },
    @{ Root = $ComfyLongRoot; Name = 'ComfyUI-PuLID-Flux'; Reason = 'Banned face-ID pack in run_graph_job.py BANNED list' },
    @{ Root = $ComfyLongRoot; Name = 'ComfyUI_PuLID_Flux_ll'; Reason = 'Banned face-ID pack in run_graph_job.py BANNED list' },
    @{ Root = $ComfyLongRoot; Name = 'comfyui-reactor-node'; Reason = 'Banned reactor pack in run_graph_job.py BANNED list' }
)
foreach ($entry in $PruneMap) {
    $nodeDir = Join-Path (Join-Path $entry.Root 'custom_nodes') $entry.Name
    if (Test-Path -LiteralPath $nodeDir) {
        Write-Host ("  ACTIVE (prune candidate): {0} ({1})" -f $nodeDir, $entry.Reason)
        if ($Mode -eq 'Apply' -and $PruneCustomNodes) {
            $dst = "$nodeDir.disabled"
            if ($PSCmdlet.ShouldProcess($nodeDir, "Disable custom node -> $dst")) {
                Rename-Item -LiteralPath $nodeDir -NewName ($entry.Name + '.disabled')
                Write-Host "  DISABLED: $dst"
            }
        }
    } else {
        Write-Host ("  OK (already disabled or absent): {0}" -f $nodeDir)
    }
}

Write-Host "=== [5/6] Python Venv Package Audit (comfy-kitchen, comfy-aimdo, onnxruntime, opencv) ==="
foreach ($root in @($ComfyAutoRoot, $ComfyLongRoot)) {
    $py = Join-Path $root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $py)) {
        Write-Host "  SKIP (venv python not present on this host): $py"
        continue
    }
    $pipOut = & $py -m pip list --format=freeze
    $ckLine = ($pipOut | Where-Object { $_ -like 'comfy-kitchen==*' }) -join ', '
    $aimdoLine = ($pipOut | Where-Object { $_ -like 'comfy-aimdo==*' }) -join ', '
    $ortLines = ($pipOut | Where-Object { $_ -match '^onnxruntime(-gpu)?==' }) -join ', '
    $cvLines = ($pipOut | Where-Object { $_ -match '^opencv-.*==' }) -join ', '
    Write-Host "  [$root]"
    Write-Host "    comfy-kitchen : $ckLine"
    Write-Host "    comfy-aimdo   : $aimdoLine"
    Write-Host "    onnxruntime   : $ortLines"
    Write-Host "    opencv        : $cvLines"

    if ($Mode -eq 'Apply' -and $UpgradePackages) {
        if ($PSCmdlet.ShouldProcess($py, 'Upgrade comfy-kitchen>=0.2.41, comfy-aimdo>=0.6.0, and deduplicate onnxruntime/opencv')) {
            # Install plain comfy-kitchen (no [cublas] extra) so Windows torch\lib\cublas64_13.dll is used without duplicate nvidia-cublas wheels
            & $py -m pip install --upgrade 'comfy-kitchen>=0.2.41' 'comfy-aimdo>=0.6.0'
            $ortGpuMatch = $pipOut | Where-Object { $_ -match '^onnxruntime-gpu==(.+)$' } | Select-Object -First 1
            if (($pipOut | Where-Object { $_ -match '^onnxruntime==' }) -and $ortGpuMatch) {
                $ortGpuVer = ($ortGpuMatch -split '==', 2)[1].Trim()
                & $py -m pip uninstall -y onnxruntime onnxruntime-gpu
                & $py -m pip install --no-deps "onnxruntime-gpu==$ortGpuVer"
            }
            if (@($pipOut | Where-Object { $_ -match '^opencv-.*==' }).Count -gt 1) {
                & $py -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless
                & $py -m pip install --no-deps 'opencv-contrib-python==4.13.0.92'
            }
        }
    }
}

Write-Host "=== [6/6] AlienPc C:\AI\community Scripts & Test Graph Sync ==="
$BundledCommunity = Join-Path (Split-Path -Parent $ScriptDir) 'alienpc-community'
$CommFiles = @(
    'scripts\comm.py',
    'scripts\make_b2_request.py',
    'scripts\run_graph_job.py',
    'scripts\run_queue.py',
    'sy_test_graph.json'
)
if (-not (Test-Path -LiteralPath $BundledCommunity)) {
    Write-Host "  SKIP (bundled alienpc-community folder not beside alienpc-comfyui-config): $BundledCommunity"
} elseif (-not (Test-Path -LiteralPath $CommunityRoot)) {
    Write-Host "  SKIP (live CommunityRoot not present on this host): $CommunityRoot"
} else {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    foreach ($rel in $CommFiles) {
        $src = Join-Path $BundledCommunity $rel
        $dst = Join-Path $CommunityRoot $rel
        if (-not (Test-Path -LiteralPath $src)) { continue }
        $same = (Test-Path -LiteralPath $dst) -and ((Get-FileHash -LiteralPath $src).Hash -eq (Get-FileHash -LiteralPath $dst).Hash)
        if ($same) {
            Write-Host "  OK (already up to date): $dst"
        } else {
            Write-Host "  DIFFERS (update pending): $dst"
            if ($Mode -eq 'Apply' -and $ApplyCommunityScripts) {
                $archDir = Join-Path (Split-Path -Parent $dst) '_archive'
                $bakPath = Join-Path $archDir ((Split-Path -Leaf $dst) + ".bak-$stamp")
                if ($PSCmdlet.ShouldProcess($dst, "Backup to $bakPath and install updated $rel")) {
                    New-Item -ItemType Directory -Force -Path $archDir | Out-Null
                    if (Test-Path -LiteralPath $dst) {
                        Copy-Item -LiteralPath $dst -Destination $bakPath -Force
                    }
                    Copy-Item -LiteralPath $src -Destination $dst -Force
                    Write-Host "  APPLIED: $dst (backup: $bakPath)"
                }
            }
        }
    }
}

Write-Host "=== Done ($Mode) ==="
