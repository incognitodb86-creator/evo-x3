---
title: torch.compile, Sage and caches do not help the AlienPc Max lane
tags: [max, speed]
date: 2026-10-09
---
- torch.compile demotes the model off dynamic VRAM (ComfyUI PR #12612), H3 can't use CUDA graphs (#15551 open), the one H3 measurement was ~1.5% faster with diverged output. Skip.
- SageAttention 2.x = no gain over ck-attention locally (44.7 vs 43.3 s) and blackscreen reports on RTX 5070 Ti. Keep ck.
- TeaCache/EasyCache/MagCache always change output; TenStrip: no cache on reference runs.
- Remaining quality-neutral levers (async offload, pinned memory, fp16acc, Comfy 0.39) are worth ~0-15%; A/B queued 2026-10-09. GPU already at 300 W cap and ~2775 MHz under load, not thermally throttled.
- Source: /workspace/cos/research/2026-10-09-alienpc-speedups-torch-compile.md
