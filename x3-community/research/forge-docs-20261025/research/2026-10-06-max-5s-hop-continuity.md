# RESEARCH — Max 5s hop continuity (same scene / last-frame match) — 2026-10-06 ~11:25 CT

**Owner:** Dial (Max Studio ask via Derrick) · research-only  
**Ask:** How to hop from one ~5s I2V/REF2VA clip to the next while picking up the **same scene and last frame** so they match (stitch).  
**Locks:** Fiction adults 21+ Cond only · NO gen · NO invent KEEP · leave live R3c68 alone  
**Related SoT:** `/workspace/cos/research/2026-10-05-max-h3-1min-multi-section-continuity.md` (C★ vs A) · hop pastes `ONE_MIN_CONTINUITY_2026-10-05/meta/POS_HOP_{C,A}_SETTLE_V1.txt`  
**Live queue (do not kill):** AlienPc `:8189` **R3c68 6s sA** START 11:23:23 CT · `prompt_id 8c720252-…` · length **141** · seed 43029049 · pend=0 · **10s sB already CELL_DONE** (wall 375.4s) — interrupt was 480@15s, not 10s sB.

---

## 1) TLDR — method Dial can run on our ST8+simple 768×1344 124f cells

**Do not one-shot 10–15s for product.** Hot 5s (~124f) is the Integrity/speed sweet spot; longer is super-linear wall + place drift (R3c10). Chain **N×124f hops**, then soft-cut assemble.

### ★ Default for THIS fleet (REF2VA / TenStrip rule) — Method C

**Prior clip → `ref_video_1` / `<Video 1>` + summary task `[reference generation + video continuation]` + keep ORIGINAL Cond as `<Picture 1>` Face/ID `fully_preserved` every hop.**

Dial checklist (cell *N+1*):

1. **Canvas lock:** same **768×1344** · ST8 · `res_multistep`+`simple` · `ref_image_size=match` · same seed family (chain default = **same seed** every section unless labeled axis).
2. **Wire Cond:** ORIGINAL Cond still → `ref_image_1` / `<Picture 1>` · Face/ID **fully_preserved** (identity re-anchor — do **not** drop Cond).
3. **Wire prior clip:** Cell *N* MP4 frames → `ref_video_1` / `<Video 1>` (24fps, ≥5f, ideally full prior cell ≤ length). Prompt: continue from **end** of `<Video 1>`.
4. **Task prefix:** `[reference generation + video continuation]` (optional later: `+ keyframe completion` only if also landing on a still — **OFF** for pure C arm / C-vs-A fair twin).
5. **Place lock in prompt:** name pool/horizon/wardrobe **end-state of N = open-state of N+1**; one PRIMARY MOTION only; prefer **≥0.5–1s settle** at end of *N* so hop has a clean handoff pose.
6. **Seam-replay TECH before concat:** compare first ~0.5–1s of *N+1* to tail of *N*; if continuation **re-plays** source end, trim overlap frames (ffmpeg) — amount **NO_DATA** until first smoke.
7. **Assemble:** soft-cut on settle frames (method D). Native Prepare/Stitch / Motion Context = **not installed on AlienPc today** (inventory 2026-10-06 ~11:24 CT).

Ready pastes (settle hop after T0 peel):  
`/workspace/MAX_STRIP_5S_MATRIX_2026-10-05/ONE_MIN_CONTINUITY_2026-10-05/meta/POS_HOP_C_SETTLE_V1.txt`

### Labeled fallback — Method A (last-frame Cond assist)

1. Export **last frame** of cell *N* (ffmpeg `select=eq(n\,LAST)` or VHS/SaveImage).
2. Wire as `<Picture 2>` / extra REF · summary `[reference generation + keyframe completion]`.
3. **Still keep** ORIGINAL Cond as `<Picture 1>` Face/ID re-lock.
4. Twin paste: `POS_HOP_A_SETTLE_V1.txt`.

**Why A is fallback, not SoT:** REF2VA emits an **empty** latent — last-frame-as-Cond alone does **not** hard-pin frame 0 the way I2VA `first_frame` does. Official dialect prefers video-continue for “extend from existing video.”

### What NOT to do for hop match

| Anti-pattern | Why |
|--------------|-----|
| Drop Cond Picture 1 across hops | Face/place drift (seen on long single gens; worse across seams) |
| New wardrobe/place in hop-0 prompt | Model merges contradictions; bg teleport |
| Identical FL2VA bookends | VOID C5 freeze |
| Default to `video_minimax_h3_i2v_continuation` | I2VA-family — conflicts Derrick REF2VA/TenStrip default |
| Expect latent Prepare/Stitch without install | AlienPc object_info: **no** MiniMaxH3LatentLab* / Motion Context / H3-Continuous nodes (2026-10-06) |
| One 243–362f cell hoping for Instant Match | Super-linear wall + place lock weak (R3c10 / length research) |

### If Dial later installs latent continuation (optional upgrade)

Community packs carry prior **AV latent tail** (typical overlap **22f ≈ 0.92s** or **39f ≈ 1.625s** on 17k+5), `video_context_denoise=0`, then **trim overlap** before concat. Better motion continuity than pixel round-trip — but **not** fleet-proven here and **not** installed. Keep Method C as default until inventory + GO.

---

## 2) Primaries (≥3 dated · access 2026-10-06 CT)

| # | URL | What it gives Dial |
|---|-----|--------------------|
| 1 | https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo | REF2VA: empty latent · `ref_videos` ≤3 · length trained **~124–362** · tags `<Picture>`/`<Video>` |
| 2 | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | Official tutorial · ~15s open-weights · names `video_minimax_h3_i2v_continuation` template (I2VA) · Multiframe ≥0.34 |
| 3 | Local primary mirror: `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | Official MiniMax **ref_en** task types: **`video continuation`** · **`keyframe completion`** · combine with ` + ` |
| 4 | https://minimaxh3.cc/guides/minimax-h3-long-video (field guide; sources checked ~2026-09-08) | Long-video = chain short clips · latent carry + trim · airlock beat · Motion Context / H3-Continuous / Multishot pointers |
| 5 | https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation | Latent-tail overlap ~**22f** then append visible suffix (secondary tooling) |
| 6 | https://comfy.icu/node/MiniMaxH3LatentLabPrepareContinuation · StitchContinuation | Prepare overlap (default 22) · stitch trim · `video_context_denoise=0` |
| 7 | https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context | Motion Context recommended 22f video / 24f audio carry + Trim |
| 8 | Fleet SoT: `/workspace/cos/research/2026-10-05-max-h3-1min-multi-section-continuity.md` | C★ SoT · A fallback · Cond re-lock · seam-replay · C vs A smoke |

**TenStrip / 10Eros on continuation specifically:** **NO_DATA** in author primary — mode preference REF2VA is documented; hop recipe = MiniMax ref_en + Comfy REF2VA + fleet smoke.

---

## 3) Contradictions / unknowns

| Tension | Resolve for Dial |
|---------|------------------|
| “Last frame → next Cond” feels obvious | Works better on **I2VA first_frame**; on **REF2VA** empty latent → prefer **`<Video 1>` continuation**; last-frame = assist (A) |
| Comfy ships I2V continuation template | Real, but **I2VA** — labeled only if Derrick GO leaves REF2VA |
| Latent continuation “exact seam” claims | Need pack install + `denoise=0` + trim; **not on AlienPc** today |
| Grafted Max / Stuubs REF vs stock Ref2VA video-ref accuracy | **NO_DATA** — reason C vs A A/B still recommended |
| Does `[video continuation]` re-play tail frames? | **NO_DATA** until seam-replay TECH |
| Best overlap trim (frames) for soft-cut only | **NO_DATA** — start inspect 12–24f (~0.5–1s) |
| Same seed vs new seed per hop | Fleet default **same seed**; vary = labeled axis |
| Place drift on longer single gens (10s) | Motive for hops — not a hop-wiring bug |

---

## 4) Recommend default for our ST8+simple 768×1344 124f cells

| Knob | Default |
|------|---------|
| Cell length | **124f (~5.17s)** hot |
| Mode | **REF2VA** (`MiniMaxH3ReferenceToVideo`) |
| Hop method | **C ★** prior clip → `ref_video_1` + `[reference generation + video continuation]` |
| Identity | ORIGINAL Cond → `<Picture 1>` **every hop** · Face/ID `fully_preserved` |
| Place | Explicit place lock line every hop (pool/horizon/wardrobe end→open) |
| Seed | **Same** across hop chain |
| Sampler | ST8 · res_multistep · simple · match |
| Fallback twin | Method **A** last-frame `<Picture 2>` + `keyframe completion` (fair C vs A) |
| Assemble | Soft-cut after seam-replay trim · ffmpeg/Editor |
| Latent Prepare/Stitch / Motion Context | **HOLD** until install + Derrick GO (inventory miss) |
| Product longer than 5s | **N×124f hops** (e.g. 3× ≈15s) — not one 362f unless labeled cliff probe |

**First smoke after GO (not this turn):** T0 124f → hop C settle → hop A settle (shared T0, seeds 71–73 or locked matrix seeds) · score seams · no KEEP.

---

## Queue note (ops)

- **R3c68 6s sA LIVE** @8189 (141f) — **do not interrupt**.  
- **10s sB done** earlier; 8s cells not yet started (insert sequential).  
- This research **queued nothing** and **killed nothing**.

---

## close-out-verify

- [x] TLDR Dial can run (C★ + A + don’ts)  
- [x] ≥3 dated primaries (Comfy REF2VA · Comfy tutorial · ref_en · long-video guide · continuation GH)  
- [x] Contradictions / NO_DATA listed  
- [x] Default for ST8+simple 768×1344 124f stated  
- [x] Local research searched first · web/Firecrawl used · brief stamped  
- [x] No gen · no KEEP · fiction 21+ Cond only  
- [x] Live 6s left alone · 10s sB not killed  

**Stamp:** `/workspace/cos/research/2026-10-06-max-5s-hop-continuity.md`
