# AlienPc ComfyUI Configuration Snapshot & Remediation Pack (2026-11-17)

Read-only snapshot of AlienPc ComfyUI config captured `2026-11-17 13:45 CT` (no models, no outputs, no keys), paired with the fleet-locked ComfyUI-only `llama-swap` configuration and preflight/remediation script.

## Live Install Summary (`comfyui_auto` vs `comfyui_longvideo`)

| Property | `comfyui_auto` (Primary Render Engine) | `comfyui_longvideo` (Secondary Long-Video Build) |
| --- | --- | --- |
| Path | `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` | `C:\AI\comfy-longvideo\ComfyUI` |
| ComfyUI Version | `v0.38.0` (`6b747c0428c343e1417219641db93a4fb7cb69ae`) | `v0.38.0` (`6b747c0428c343e1417219641db93a4fb7cb69ae`) |
| Python / PyTorch | Python `3.12.10` / `torch 2.15.0.dev20260928+cu130` (CUDA `13.0`) | Python `3.12.10` / `torch 2.15.0.dev20260928+cu130` (CUDA `13.0`) |
| `comfy-kitchen` / `comfy-aimdo` | `0.2.36` / `0.5.5` (upgrade target: `>=0.2.41` / `>=0.6.0`) | `0.2.36` / `0.5.5` (upgrade target: `>=0.2.41` / `>=0.6.0`) |
| Custom Nodes | 48 total (**13 enabled**, 35 `.disabled`) | 45 total (**44 enabled**, 1 `.disabled`) |
| Idle TTL / Stop | `ttl: 300` / `unloadTimeout: 1900` via `comfy_graceful_stop.ps1` | `ttl: 600` / `unloadTimeout: 1900` via `comfy_graceful_stop.ps1` |

## Key Audit Findings & Remediations Included Here

1. **Restored `--use-ck-attention` in `llama-swap` Launchers (`llama-swap_comfy_entries.yaml` & `llama-swap.alienpc-comfy-only.yaml`):**
   - The snapshot revealed `--disable-pinned-memory --reserve-vram 1.5` was already active (so `comfy-aimdo` Dynamic VRAM is enabled with 1.5 GiB headroom), **but `--use-ck-attention` had been dropped from both `cmd` lines**. While graph nodes with `ModelAttentionBackend = "comfy kitchen attention"` still patched UNET attention, unpatched VAE/CLIP attention fell back to PyTorch SDPA. Both `cmd` entries now pass `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5` and `concurrencyLimit: 999`.
2. **ComfyUI-Only `llama-swap.yaml` (`llama-swap.alienpc-comfy-only.yaml`):**
   - `llama-swap.exe` on `127.0.0.1:8080` must remain running because Tailscale Serve `:8446` proxies to `http://127.0.0.1:8080/upstream/comfyui_auto` for on-demand wake + 300 s idle unload. `llama-swap.alienpc-comfy-only.yaml` removes all legacy local LLM/VLM slots (`coding_*_strata`, `vl_judge`, `qwen3vl_judge`) so no API call can ever load an LLM onto the RTX 5070 Ti, and preserves `^/system_stats$` in `upstream.ignorePaths` so EVO-X3 readiness/idle probes return `409` without waking an idle ComfyUI.
3. **Tailscale Serve Surface (`tailscale_serve_status.txt`):**
   - `:8446` -> `http://127.0.0.1:8080/upstream/comfyui_auto` (tailnet-only, path-scoped; does not expose `llama-swap` admin routes). Scope `:8446` via Tailscale ACLs to `tag:evo-x3` + Derrick's admin devices.
   - `:8445` (`127.0.0.1:9537`, legacy AlienPc PixlStash) and `:8444` (`127.0.0.1:7889`) are still active on AlienPc; retire `:8445` (`tailscale serve --https=8445 off`) once AlienPc PixlStash is no longer needed since canonical PixlStash moved to EVO-X3.
4. **Custom Node & `.venv` Hygiene (`apply-on-alienpc.ps1`):**
   - `ComfyUI-MiniMaxH3-Prompt-Writer` is currently enabled in `comfyui_auto`, and banned face-ID nodes (`ComfyUI-PuLID-Flux`, `ComfyUI_PuLID_Flux_ll`, `comfyui-reactor-node`) are enabled in `comfyui_longvideo`.
   - Both `.venv`s have `onnxruntime` (CPU) installed alongside `onnxruntime-gpu` (`1.26.0`) and 3 conflicting OpenCV packages (`opencv-python 4.11.0.86`, `opencv-contrib-python 4.13.0.92`, `opencv-python-headless 4.13.0.92`).
   - Run `.\apply-on-alienpc.ps1 -Mode Audit` first on AlienPc, then `.\apply-on-alienpc.ps1 -Mode Apply -ApplyLlamaSwap -ApplyCommunityScripts -PruneCustomNodes -UpgradePackages` during an idle window (plain `comfy-kitchen>=0.2.41` without `[cublas]` avoids duplicate `nvidia-cublas` DLL conflicts with Windows `torch\lib`, and `onnxruntime-gpu==1.26.0` is pinned via `--no-deps`).
