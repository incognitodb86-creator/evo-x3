# Remacri MAX lock — 2026-10-06 CT

**Owner:** Dial smoke (Derrick lock)  
**Pack:** `Desktop\MAX_UPSCALE_AB_2026-10-06\`

## Lock

- Model: **`4x_foolhardy_Remacri.pth`** (4× full)
- `ImageUpscaleWithModelBatched`: **`downscale_ratio=1`**, `per_batch=1`, `precision=float16`, **no tile**
- **One** `ImageScale` lanczos → short-edge **~1080** (AR-preserve)
- Max UNET **unloaded** (`/free`) before upscale
- Source: **reuse existing 480** ST8 (W1_simple_sA `43029049`) — no regen

## TECH row (landed)

| field | value |
|-------|-------|
| src | 480×864×124 reused W1 |
| out | **1080×1944×124** |
| wall | **85.3 s** |
| clip | `clips/remacri/UPS_REMACRI_480ST8_1080_…mp4` (~6.63 MB) |
| KEEP | no |

## Next

SeedVR SPEED (Research lock) after ONE restart — in flight / follow `2026-10-06-seedvr2-16gb-speed-quality-settings.md`. QUALITY = batch9 XOR 1440 later.
