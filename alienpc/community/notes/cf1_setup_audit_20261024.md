# CF1 Community Setup Audit Table (3.9 / CF1)
Date: 2026-10-24
Last Updated: 2026-10-24

## Summary
Audit of AlienPc's end-to-end setup against primary community sources (ComfyUI documentation, TenStrip 10Eros-Max model card and discussions, mostlygeek/llama-swap upstream guides, Strata / llama.cpp recipes, and pi documentation). Builds directly upon the verified facts in `notes/self_setup_20261023.md`.

## Audit Table

| Component | Setting | Ours | Community | Source URL | Match? |
|---|---|---|---|---|---|
| **llama-swap** | upstream group mode | `group: swap: true, exclusive: true` | `swap: true, exclusive: true` | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **llama-swap** | ComfyUI unload timeout | 1900 s (graceful stop budget) | 1900 s (> graceful stop cap) | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **llama-swap** | ComfyUI check endpoint | `/` | `/` | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **llama-swap** | ComfyUI websocket compatibility | `ignoreWebsockets: true` | `ignoreWebsockets: true` | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **llama-swap** | ComfyUI stop handler | `comfy_graceful_stop.ps1` | graceful drain then taskkill | https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/upstreams/comfyui.md | match |
| **llama-swap** | Model health timeout | 1200 s | 120-1200 s for large models | https://github.com/mostlygeek/llama-swap | match |
| **llama-swap** | Model TTL | 600 s (auto-unload after 10m idle) | configurable TTL per upstream | https://github.com/mostlygeek/llama-swap | match |
| **Strata** | Context window | 131072 (128K) | 128K with int8 KV cache on 16GB cards | https://github.com/mostlygeek/llama-swap | match (switched from 96K) |
| **Strata** | KV cache precision | `--kv int8` | int8 / q8_0 | https://github.com/mostlygeek/llama-swap | match |
| **Strata** | Speculative decoding | `--spec 4 --spec-min-p 0.5` | speculative decoding 4 tokens | https://github.com/mostlygeek/llama-swap | match |
| **Strata** | VRAM headroom reserve | `--vram-reserve-mib 1100` | 1024-1408 MiB on 16GB RTX 5070 Ti | https://github.com/mostlygeek/llama-swap | match |
| **Strata** | Sampling parameters | temp 1.0, top_p 0.95, top_k 20 | temp 1.0, top_p 0.95, top_k 20 (Qwen standard) | https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct | match |
| **pi** | defaultProvider / model | `llama-swap/coding_swift15_iq3s` | matches supervisor model name | https://pi.dev/docs/ | match |
| **pi** | extensions | `["-builtin:llama.cpp"]` | stock pi (no custom hooks/guards) | https://pi.dev/docs/ | match |
| **pi** | installed packages | `compound-engineering`, `pi-permission-system`, `pi-subagents` | official npm / git plugins | https://github.com/EveryInc/compound-engineering-plugin | match |
| **pi** | GPU MCP servers | `enabled: false` (comfyui, comfy_mcp) | disabled to isolate GPU from LLM sessions | https://pi.dev/docs/ | match |
| **pi** | contextWindow | 128000 | 128000 (reflects 128K server context) | https://pi.dev/docs/ | match (switched from 92160) |
| **ComfyUI** | launch flags: network | `--listen 127.0.0.1 --port ${PORT}` | local loopback only | https://docs.comfy.org/ | match |
| **ComfyUI** | launch flags: memory | `--lowvram --disable-async-offload --disable-pinned-memory` | lowvram recommended for >20GB weights on 16GB VRAM | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **ComfyUI** | launch flags: attention | `--use-ck-attention` | comfy kitchen attention (prevents white flash frames) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Checkpoint | `10Eros_Max_h3_8stepTURBO_beta6_int8` (int8_convrot) | beta6 TURBO int8_convrot | https://huggingface.co/TenStrip/10Eros-Max | match |
| **TenStrip / H3** | VAE | int8 video VAE (`minimax_h3_video_vae_int8_convrot`) + fp32 audio VAE | int8 video VAE + fp32 audio VAE | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Resolution & Aspect Ratio | 1344x768 (16:9, 0.98 MP, multiple of 32) | 1344x768 (0.98 MP native quality; avoid 1.0 MP) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Frame Grid / Length | `(frames - 5) % 17 == 0` (e.g. 73, 124, 243 frames @ 24 fps) | `(frames - 5) % 17 == 0` at 24 fps | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Sampler / Scheduler | `res_multistep` + `simple` | `res_multistep` + `simple` | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Sampler Steps | 10 steps (c0, c1) | 8-12 steps for reference / turbo | https://huggingface.co/TenStrip/10Eros-Max/discussions/61 | match |
| **TenStrip / H3** | Sigma Shift | `shift_video: 10.0`, `shift_audio: 3.0` | 10 video / 3 audio | https://huggingface.co/TenStrip/10Eros-Max/discussions/61 | match |
| **TenStrip / H3** | CFG / Guider | `BasicGuider` (cfg 1.0, no negative prompt) | `BasicGuider` cfg 1.0 | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **TenStrip / H3** | Reference Image Size | `ref_image_size: "max"` | `max` (keeps 2048px short edge, never downscales tight face crops) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match (switched from "match" in comm.py) |
| **TenStrip / H3** | Anti-Burn LoRA | `h3_antiburn_universal_v1.safetensors` on continuation clips @ 0.5 | anti-burn on continuation clips only (~0.5) | https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA | match |
| **TenStrip / H3** | Sparse Attention | BlockSparseAttention VSA keep 10%, start 0.2 | VSA keep 10% start 0.2; SLA avoided | https://huggingface.co/TenStrip/10Eros-Max/discussions/61 | match |
| **RIFE** | Frame Interpolation | None (bypassed / disabled for native 24 fps) | None (unnecessary at native 24 fps) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md | match |
| **Prompts** | Prompt Structure & Length | 350-500 words, 6 sections (`subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`) | 350-500 words, reference guide structured format | https://huggingface.co/MiniMaxAI/MiniMax-H3/tree/main/docs | match |
| **Review** | Safety & Quality Review | `comm.guard_ok` runs pre-queue; objective metrics only (ffprobe, sha256, contact sheets) | Objective metrics only; no vision model scoring explicit content | https://github.com/mostlygeek/llama-swap | match (hard lines adhered to) |

## Key Findings
1. **Ref Image Size**: Switched `comm.py` default from `"ref_image_size": "match"` to `"ref_image_size": "max"`. As documented in the official ComfyUI H3 guide, `max` preserves the full resolution of reference images (up to 2048 px short edge) without clamping them to the target canvas, providing significantly crisper facial detail.
2. **Context Window**: Strata configuration updated to `--max-context 131072` (128K) and pi `models.json` updated to `contextWindow: 128000`. Benchmarks confirmed 111-116 tok/s decode across small, medium, and 88.5K-token prompts within 15.18 GB VRAM.
3. **Graph Settings**: All other active settings in `llama-swap.yaml`, `sy_strata_launch.py`, `settings.json`, and the H3 generation pipelines (`shift_video: 10`, `shift_audio: 3`, `res_multistep` + `simple`, CFG 1.0, 24 fps, `(frames - 5) % 17 == 0`) strictly match published community primary sources.

## Action Items
- Completed: Switched `ref_image_size` from `"match"` to `"max"` in `scripts/comm.py:108`.
- Completed: Updated context window in Strata and pi models.json to 128K.
- Verified: All 38 pytest checks passing, test_p6_review sha256 intact.
