# Remacri MAX quality — 480→~1080 vs SeedVR2

**Date:** 2026-10-06 ~12:30 CT  
**Owner:** Max Research → Dial (Arm B baseline)  
**Ask:** `4x_foolhardy_Remacri` MAX quality best practice for video 480→~1080 vs SeedVR; official + community ≥3  
**Fiction:** adults 21+ · Cond/LoRA names = nomenclature only  
**No KEEP**

## TLDR (Dial)

| Lane | Lock |
|------|------|
| **Remacri MAX (Arm B)** | `4x_foolhardy_Remacri.pth` → `ImageUpscaleWithModelBatched` **`downscale_ratio=1`** · **`per_batch=1`** · **`float16`** (try **`float32`** only if VRAM free after Max unload) · **no tile** · then **one** `ImageScale` **lanczos** to short-edge **~1080** · Max **unloaded** · VHS nvenc |
| **Do NOT** | `downscale_ratio=0.56` **and** a second ImageScale (double Lanczos) · Ultimate SD Upscale · latent LTX upscaler · invent anatomy |
| **vs SeedVR2** | Remacri = enlarge-only / speed+faithful baseline · SeedVR = temporal restore / sharper · can redraw skin/contact — A/B same clip only |

Effective scale 480→1080 ≈ **2.25×**. Official Real-ESRGAN + community both say: run the **4×** net, then **one** Lanczos to target (4×→~2× supersample). That downscale-after is the **biggest Remacri quality lever** (averages per-frame noise / flicker).

## MAX knobs (evidence)

| Knob | MAX lock | Why |
|------|----------|-----|
| Model | `4x_foolhardy_Remacri` | OpenModelDB: ESRGAN 4× · interpolated so skin/detail “don’t become mushy and blurry” |
| Net scale | Always **4×** then resize | No 2× Remacri weight; Real-ESRGAN runs `self.scale` then one `INTER_LANCZOS4` if outscale≠scale |
| `downscale_ratio` | **`1`** + one ImageScale | KJNodes: ratio lands final size; mid-ratio + second scale = double resample (fleet WRONG 2026-10-02) |
| Target | short edge **~1080** (AR-locked) | Match SeedVR SPEED short-edge class for fair A/B |
| `per_batch` | **1** | VRAM-safe on 16GB intermediate; does not change weights |
| `precision` | **float16** default; **float32** = tiny MAX try | KJNodes default float32; Real-ESRGAN CLI default fp16; float32 only if `/free` + no OOM |
| Tile | **OFF** unless OOM | RealESRGANer tile default 0 |
| Temporal | None | Per-frame ESRGAN — flicker possible; SeedVR is the temporal fix |

## Remacri vs SeedVR2 (same clip)

| | Remacri | SeedVR2 (C-SPEED) |
|--|---------|-------------------|
| Job | Enlarge / export | Diffusion restore + upscale |
| Temporal | No (flicker risk) | Yes (batch 4n+1) |
| Anatomy | Does **not** invent | Can redraw |
| Wall class | ~1–2 min (76s logged landscape 1080) | Minutes (NO_DATA 5070 Ti) |
| Role in matrix | **Arm B baseline** | **Arm C** after Remacri hot |

## Primaries (≥3)

1. https://openmodeldb.info/models/4x-Remacri — Remacri 4× ESRGAN · less mushy skin claim · CC-BY-NC-SA-4.0  
2. https://github.com/xinntao/Real-ESRGAN/blob/master/realesrgan/utils.py — 4× net then one Lanczos if outscale≠scale  
3. https://comfy.icu/node/ImageUpscaleWithModelBatched — KJNodes `downscale_ratio` / `per_batch` / precision  
4. Community video-upscale recipe (comfyui-mcp): 4× Remacri then ImageScale to clean ~2× = biggest quality lever; flicker → SeedVR2  
5. https://docs.comfy.org/tutorials/utility/seedvr2 — SeedVR2 conservative temporal restore (contrast arm)  
6. Fleet: `/workspace/cos/research/2026-10-02-remacri-settings-check.md` · `2026-10-05-upscale-official-community.md` · `2026-10-06-seedvr2-16gb-speed-quality-settings.md` (disk sha `930a4121…`)

## Non-goals

Ultimate SD Upscale · FlashVSR · UltraSharp swap for this smoke · bot KEEP · queue without exact GO

---

## ERRATA 2026-10-06 ~12:36 CT (Derrick HARD via Dial)

**No downscale.** Remacri MAX = **full 4× keep** (`downscale_ratio=1`, **no** ImageScale shrink to ~1080). Prior TLDR “one Lanczos short-edge ~1080” and “4×→~2× supersample as quality lever” are **STRICKEN** for this fleet lock. Double-Lanczos ban (`0.56`+second scale) still stands. SeedVR SPEED may still use 1080-class as **its** arm — not Remacri.

See: `/workspace/cos/research/2026-10-06-face-detailer-ab-480-eyes.md`
