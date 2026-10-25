# Topaz Video 1.7.0 — 864×480 → ~1080 recipe

**Date:** 2026-10-02 ~7:45 PM CT  
**Owner:** research executor (no AlienPc Shell)  
**Product:** Topaz Video (2026 rebrand). **Not** Topaz Video AI 7.x. Video AI v7.1.5 is the discontinued final legacy build ([TVAI vs TV](https://docs.topazlabs.com/topaz-video/tvai-vs-tv)).

## Version assumption (labeled)

| Claim | Status |
|--------|--------|
| MSI `C:\Users\derek\Downloads\TopazVideo-1.7.0.msi`, ProductName **Topaz Video**, ProductVersion **1.7.0** | **Parent lock**, not re-read from the PC. Filename pattern `TopazVideo-1.7.0.msi` matches the Windows build named on the 1.7.0 release thread. |
| Box `/workspace` grep for Topaz / tvai / `TopazVideo-1.7` | **No installer or version stamp.** Hits were unrelated (Chrome, pip `ProductVersion`, prior upscale notes). |
| Release date of 1.7.0 | **2026-08-11** post by erasmo.topazlabs. Do not treat that as the install time. |

This note uses **only** knobs published for **Topaz Video 1.7.0 / Precise 2.6**. It does not copy Video AI 7.x CLI recipes.

## One default recipe (adult live-action-looking I2V)

Source assumption: progressive square-pixel **864×480** (aspect **1.8**, not 16:9), short generative clip, faces matter, motion should stay the source motion.

**Use Starlight Precise 2.6, sharpness 1, scale 2× → 1728×960, Progressive, H.264, alone.**

| Knob | Set | Why |
|------|-----|-----|
| Video Type | **Progressive** | I2V frames are progressive. Do not pick Interlaced / Dione. |
| Model | **Starlight Precise 2.6** | 1.7.0 model. Docs: medium–high generative or live-action; built for realistic faces/skin; “improves generated content that may have soft, plastic, or slight artificial looks” if structure is already solid. |
| Sharpness | **1** (not the default 3) | 1 = lighter, more natural. 2 = middle. **3 = default = Precise 2.5 sharpness** (sharpest). Release-thread user: level 1 cut “dirty” noise and skin artifacts. |
| Scale | **2× → 1728×960** | Precise outputs are only **Minimum / 2× / 3× / 4×**, not a free 1920 width. 2× keeps 864:480. 3× is 2592×1440 (heavier, past 1080). |
| Recover detail / denoise / sharpen / Focus Fix / grain | **Not on this model** | Those are Proteus-family Advanced Tuning knobs. Precise 2.6 is standalone: sharpness slider only. |
| Second filter, interpolation, stabilization | **Off / not allowed** | Precise “can’t be combined with other filters.” Interpolation invents frames (smear). Stabilization live-preview is “do not use with Starlight.” |
| Codec | **H.264** (not HEVC/H.265) | 1.7.0 HEVC hardware-decode regression. See below. |
| Preview | **Don’t.** Export a few seconds. | Nvidia: Preview / Frame Preview “will not work” on Precise and on Mini. |
| Model files | Model Manager, or first export downloads Neuroserver weights | First export waits on a large download. Local, not cloud, for this clip. |

**Why not a literal 1920×1080 file inside Topaz:** 1920×1080 is 16:9. 864×480 is 9:5. Forcing 1920×1080 stretches. Precise will not offer a custom 1920×1067. If a 1920-wide master is required later, scale the **1728×960** result in a separate Lanczos/ffmpeg pass. Do not stack that inside the Starlight job.

**Why this model and not Mini:** Starlight Mini (also updated in 1.7.0) is the official pick for **low / poor** footage and **below 480p**, and its haze fights plastic. Docs also say Mini has slightly less fine detail than Precise. This source is **at** 480p, not below, and the ask is detail without plastic — so Precise **sharpness 1** is the single default. Switch to Mini only if a short test looks crunchy or the source is mush.

### Fallback only (do not run in parallel with Precise)

**Proteus Natural**, Progressive, if Precise is too slow or the Neuroserver download blocks the night. No manual sliders (by design: less oversharpen than Proteus, less warped small faces). It can target resolutions the codec allows, including a custom **1920×1066** (1920 × 480/864). Still H.264. No Focus Fix. No second pass on the first test.

If someone opens classic **Proteus Manual**: hit **Estimate**, then keep **Improve Detail** low (community practice ~12, not 100), **Recover Original Detail at 0** for the first test (100 = original, 0 = full AI blend), Focus Fix **Off**. Do not max denoise + sharpen together. This is not the default.

## Avoid

- **Gaia CG / Gaia 2** — animation, motion graphics, line art. Not live-action I2V.
- **Rhea / Rhea XL** — 4× fine-detail / beauty “pop”; XL is a render hog and can look cleaned/plastic.
- **Nyx / Nyx XL as the upscaler** — Nyx is a high-res denoise; Nyx XL is not an upscaler (detail stays at input res).
- **Iris with Improve Detail pushed** — face recovery; the detail slider “goes extreme very quickly.”
- **Artemis LQ** — most aggressive denoise + sharpen of the Artemis set.
- **Sharpness 3** on Precise 2.6.
- **Grain / Add Noise** on the first pass (hides or fights the plastic test).
- **Heavy motion-blur shots** — Precise may paint blur as texture.
- **HEVC in or out on 1.7.0.**
- **A second GPU upscale (Remacri) at the same time** — Precise wants 16 GB VRAM recommended; 12 GB is the published floor.

## 1.7.0 HEVC regression

[Staff thread](https://community.topazlabs.com/t/topaz-video-1-7-0-hevc-enhancement-failure-caused-by-hardware-decoding-regression/104446): enhancement that works in **1.6.1** fails in **1.7.0** on some HEVC. Logs show `-hwaccel cuvid` and `hwdownload,format=nv12,...tvai_up=...` plus a failed Intel **hevc_qsv** init even on NVIDIA. Topaz called it a known issue for the next patch and told affected users to roll back to **1.6.1**. Some H.264/Proteus jobs still run. **Feed and export H.264.** Do not “fix” it by staying on HEVC.

Related 1.7.0 noise (not the recipe): multi-tab cards can swap model/resolution ([104537](https://community.topazlabs.com/t/1-7-0-multitabs-setting-bug/104537)); Precise writes large `transformed_*.mmap` temps under `C:\Temp` that can survive a cancel.

## CLI

No 1.7.0 CLI flag list was published on the pages fetched. The legacy Video AI FAQ still points at an old CLI. 1.7.0 logs mention the internal ffmpeg filter name `tvai_up`, but **parameters were not documented** in the 1.7 sources used here. **Do not invent a command line.** Use the app: Enhancement → Precise 2.6 → sharpness 1 → 2× → H.264 export.

## Hardware check (published, not measured here)

Precise 2.6 Nvidia: **≥12 GB VRAM, 16 GB recommended**, **≥32 GB system RAM**, compute target **8.9** (8.6 unsupported). Prior fleet notes say AlienPc is an RTX 5070 Ti 16 GB, which meets the VRAM line; **system RAM was not measured in this pass.** Mini Nvidia floor is 10 GB, 16 GB recommended, compute ≥7.0, 32 GB RAM. The 20 GB VRAM line on the Mini page is the **AMD** requirement.

## Sources

- https://community.topazlabs.com/t/topaz-video-1-7-0/104328 — 1.7.0 release, Precise 2.6 sharpness 1/2/3, Mini 1.7 notes, Neuroserver
- https://community.topazlabs.com/t/topaz-video-1-7-0-hevc-enhancement-failure-caused-by-hardware-decoding-regression/104446 — HEVC hw-decode regression, 1.6.1 rollback
- https://docs.topazlabs.com/topaz-video/project-starlight-series/starlight-precise-25 — Precise 2.6 replaces 2.5 in 1.7.0; scale menu; standalone; preview ban; below-480p → Mini
- https://docs.topazlabs.com/topaz-video/project-starlight-series/starlight-mini — Mini look (haze / less plastic / less fine detail); 1.7.0 no-Pro; min 1280×720; aspect kept
- https://docs.topazlabs.com/topaz-video/filters/enhancement — Progressive model roles (Proteus, Iris, Nyx, Rhea, Artemis, Gaia, Theia); Recover Detail; Focus Fix
- https://docs.topazlabs.com/topaz-video/quick-start — first-run suggestion is Proteus; default codec H.264
- https://docs.topazlabs.com/topaz-video/tvai-vs-tv — Video AI 7.1.5 legacy vs Topaz Video subscription app
