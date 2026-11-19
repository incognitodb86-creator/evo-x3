# Why Max clip 2 was ~7 min (not a step-count rewarm)

**Date:** 2026-10-02 (America/Chicago). Research only. AlienPc not touched. Queue not restarted.

## Observed

- Live argv: `main.py --listen 127.0.0.1 --port 8189 --lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention`.
- Same process. REF2VA, 864x480, 124f, res_multistep, scheduler beta, NODDV, no fp8.
- Earlier today, same NODDV triad, fair warm beta KEEP **125.5s**; cold BASE **360.8s**; warm 20-step cell **100.3s** (faster, as fewer steps should be). Source: `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md`.
- Tonight P157 seed 25102401: 25-step **331.3s**, then 20-step **442.1s** (same still, same seed, only `steps` changed). A shorter sample was slower. That is not a step-count cost.

## Answers

1. **No.** A step-count change does not invalidate the diffusion weights. `run_matrix.py` keeps the same node ids and the same UNETLoader / CLIPLoader / VAELoader inputs; only `BasicScheduler.steps` changes. Comfy's execution cache keys on node inputs (`comfy_execution/caching.py`). The loader nodes are unchanged, so they are not re-executed. A cond-image change *does* miss LoadImage and `MiniMaxH3ReferenceToVideo` (re-encode), but it does not by itself change the UNET loader key. An i2v image change can still *evict* a resident UNET under memory pressure (observed by users, not by the cache key): https://github.com/Comfy-Org/ComfyUI/issues/14618 (kingp0dd: image change flushed the LTX UNET; text-only change did not). Clip 2 did not change the still.

2. **`--lowvram` does not unload the diffusion model after every prompt.** Current help text: no effect while Dynamic VRAM is on; with Dynamic VRAM off it runs the text encoder on CPU. https://docs.comfy.org/development/comfyui-server/startup-flags and `comfy/cli_args.py` (`--lowvram`: "Doesn't do anything if dynamic vram is enabled. If dynamic vram isn't being used this option makes the text encoders run on the CPU."). `--disable-dynamic-vram` switches to estimate-based loading. It does not force a per-job reload. Users report the opposite: it *stops* the DynamicVRAM disk-reload-on-prompt-change bug. https://github.com/Comfy-Org/ComfyUI/issues/14618. The flag that dumps VRAM after every workflow is `--disable-smart-memory`, and it is not in this argv. https://github.com/Comfy-Org/ComfyUI/issues/6597. Default without `--highvram` *may* move weights GPU→CPU after use, but smart memory keeps them in VRAM when they fit. A 14GB UNET does not stay fully resident on a 16GB card once VAE-decode of 124 frames needs the card, so the next sample pays a partial reload from RAM (`Unloaded partially` / `loaded partially`). That is not a process restart.

3. **Most likely: clip 1 never left the cold path, and clip 2 paid a worse partial reload under RAM pressure, not a new Comfy start.** 331s is cold-BASE class (360s). 442s is slower than cold despite 20 steps vs 25. Same-day evidence that a hot NODDV process does *not* do this: warm beta 125.5s and warm 20-step 100.3s. With async offload and pinned memory both off, the partial GPU refill is a synchronous unpinned copy. After clip 1 the 32B TE (forced onto CPU by `--lowvram`), the decoded frames, and the unpinned weight traffic can push the RAM-resident copy into the pagefile, so clip 2 re-reads weights and then samples. That matches "second job slower than first," which a true warm cache cannot do. Leaving the queue alone is what keeps the weights resident: do not POST `/free` (`unload_models` / `free_memory` calls `unload_all_models()`), do not change loader inputs or node ids, and do not queue Remacri or any second model until the 24 natives finish. Those are the in-process evictors. Pinned memory and async offload cannot be turned back on without a restart. Do not restart.

4. Do not kill the current generate.

## Cites

- https://docs.comfy.org/development/comfyui-server/startup-flags
- https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/cli_args.py
- https://github.com/Comfy-Org/ComfyUI/issues/6597
- https://github.com/Comfy-Org/ComfyUI/issues/14618
- https://github.com/Comfy-Org/ComfyUI/issues/14162
- https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/model_management.py
