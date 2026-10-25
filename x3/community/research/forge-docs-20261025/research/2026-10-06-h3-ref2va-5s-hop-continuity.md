# RESEARCH — H3 / REF2VA / TenStrip 5s→5s hop continuity — 2026-10-06 ~11:23 CT

**Ask (Dial URGENT):** How to hop 5s→5s so next clip picks up same scene + last frame (continuity stitch). ≥3 primary URLs or NO_DATA. Fiction Cond 21+ OK.

**Answer:** Official SoT = **REF2VA Method C** — prior clip as `<Video 1>` + task **`[video continuation]`**, keep **original Cond** as `<Picture 1>` Face/ID `fully_preserved`. Last-frame-as-only-start = **fallback A** (REF2VA has empty latent — no hard frame-0 pin). TenStrip continuation-specific = **NO_DATA**. Fleet pastes ready: `POS_HOP_C_SETTLE_V1` / `POS_HOP_A_SETTLE_V1`.

## Dial TLDR (5s→5s)

1. Gen cell N @ **124f (~5s)** REF2VA, canvas SoT **768×1344** (or locked AR), ST8 **simple** if fleet default.
2. For cell N+1: wire **same Cond** → `<Picture 1>` `fully_preserved`; wire **clip N** → `ref_video_1` / `<Video 1>`; summary/task includes **`[video continuation]`** (ref_en §2.3).
3. One PRIMARY MOTION per hop; end N with ≥0.5–1s settle so continue has a clean tail.
4. Same seed family across hops unless labeled axis; same steps/scheduler.
5. **Do not** default I2VA `video_minimax_h3_i2v_continuation` (conflicts REF2VA/10Eros rule) unless Derrick GO I2VA.
6. Optional fallback A: extract last frame of N → `<Picture 2>` + `keyframe completion` (keep Cond Pic1). Paste twin exists.
7. After land: **seam-replay TECH** (trim if N+1 re-plays N’s tail) → ffmpeg concat. Latent Continuation / Extender = inventory optional, not required for Method C.
8. Pastes: `/workspace/cos/research/2026-10-05-1min-hop-ca-pastes.md` · C sha `fcc1efba…` · A sha `f938ca45…`.

## Primaries (≥3) — access 2026-10-06 CT

1. https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo — REF2VA empty latent; `ref_videos` ≤3; length trained ~124–362 (~5–15s)  
2. https://docs.comfy.org/tutorials/video/minimax/minimax-h3 — open weights ~15s @24fps; R2V vs I2V; continuation template is **I2V-family** (named, not REF default)  
3. https://docs.comfy.org/built-in-nodes/MiniMaxH3ImageToVideo — FL2VA `first_frame`/`last_frame` (bookend path; not REF SoT)  
4. Local official mirror: `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` — `[video continuation]` / continue-from-end  
5. Secondary tooling (not fleet SoT): https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation · https://github.com/tritant/ComfyUI_MiniMax_H3_Extender  

## TenStrip / 10Eros

- Prefer REF2VA even for single still (CivArchive 2851079) — **yes**.  
- Author **continuation hop recipe** — **NO_DATA** (use MiniMax ref_en + fleet Method C).

## Related (Dial waiting ask — longer length wall)

Already stamped: `/workspace/cos/research/2026-10-06-h3-longer-length-vs-wall.md` — 10s wall super-linear vs 5s; trained 124–362; hops or preview for product length.

## Prior SoT

- `/workspace/cos/research/2026-10-05-max-h3-1min-multi-section-continuity.md`  
- `/workspace/cos/research/2026-10-05-1min-hop-ca-pastes.md`

No KEEP.
