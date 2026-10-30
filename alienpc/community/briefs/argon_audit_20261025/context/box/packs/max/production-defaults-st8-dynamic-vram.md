---
title: Production defaults are ST8 with dynamic VRAM on
applies_when:
  - planning, queueing or answering about AlienPc Max steps, VRAM or launch flags
---
- **Production KEEP (2026-10-09 Derrick GO; restated 2026-10-14):** beta6 int8 8-step TURBO (`10Eros_Max_h3_8stepTURBO_beta6_int8`) · Euler/simple · **8 steps** · shift 10 video / 3 audio · dynamic VRAM ON · ck-attention · ComfyUI 0.38.x pinned. Tests / local loop: **6 steps + RIFE 20**. The old Oct 2 non-Turbo beta/25-step lane is optional experiment only, not default.
- Dynamic VRAM ON is KEEP (Oct 8 test: cold first run 116.2s to 44.1s, hot runs unchanged). If WinError 1450 or paging-file errors return, disable it for that single cell and log it.
- Source of truth for launch argv: `max-8189-production-keep.md` and `alienpc-local-video-ops`.
- All defaults REVALIDATE after the rebuild; until then, state them as current but unrevalidated.

- **Revalidated 2026-10-09 1:07 PM CT (Sydney, pool Cond, Oct 8 settings 480x864x124, ST8, res_multistep/simple):** cold 160.8s off vs 49.0s on; hot 43.0s vs 40.9s. Derrick confirmed dynamic VRAM ON as KEEP (1:21 PM CT). Pack: AlienPc `Desktop\MAX_DYNVRAM_POOL_2026-10-09`.

- **Updated 2026-10-09 ~3:05 PM CT (Derrick decisions today):** model is **beta6 int8 8-step TURBO** (beta5 files deleted 2:46 PM CT; beta5 clips kept). **No RIFE** is default (Derrick: no-RIFE looks better). Shift **10** video / 3 audio. Euler/simple ST8 is the current pick (beta6 review 6.2 vs beta5 best 4.5); res_multistep and er_sde/beta are the alternates. 768 for tests. Remacri only on ask (~3x render time).

- **OFFICIAL KEEP 2026-10-09 3:19 PM CT (Derrick GO):** beta6 int8 8-step TURBO · Euler/simple · shift 10 video / 3 audio · no RIFE · dynamic VRAM on · ck-attention. Steps stay ST8 until the 10s ST6 vs ST8 comparison lands. er_sde ruled out (10s review: Euler 5.8/5.3, res_multistep 5.5/5.1, er_sde 4.8 with burned look and finger melt).

- 2026-10-09 4:54 PM CT Derrick: **Keep 8 steps** after the 10s ST6 vs ST8 review (ST8 wins or ties every category; ST6 ~23% faster). Steps are locked at ST8.

## 2026-10-10 fix-test round: prompt defaults (proven vs control)
- Describe fabric exactly as in the start image (sheer stays sheer).
- Write the start image's light and hold it all clip (no drift to sunset).
- Pin frame 0 with the Add Guide node for MiniMax H3.
- Two refs: clear Picture/Subject labels; references about 1280 px long edge (tiny crops starve the face).
- No full 180-degree spins: a hip turn or an over-the-shoulder look with the face to the lens.
- 8 steps stays the default; 12 is sharper at +50% time (Derrick's call).
- Still unsolved: the garment teleports at about 2s; hands fuse into fabric.
- 2026-10-10 face-lock round, confirmed on 2 seeds: use the v2 face-block prompt (neutral face block in subject_definitions, a "same face" line each beat, a hip turn not a spin, waist-up for two-ref). Templates: /workspace/maxops/facelock-v2-2026-10-10/FV2_*.txt
