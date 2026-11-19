# RESEARCH — Max / MiniMax-H3 REF2VA sharper quality settings — 2026-10-05

**When_CT:** 2026-10-05 ~8:30 AM CT (America/Chicago)  
**Ask (via AlienPc Dial 2):** Settings for sharper Quality on :8189 after ORC BJ A oral + B doggy **864×480 · 362f (~15s)** TECH (beta/25/ck/NODDV) — Quality soft (mushy hands/contact, plastic skin). Intent: bump native short-edge ~768 + Remacri.  
**Scope:** Local research + official Comfy MiniMax H3 / MiniMaxH3ReferenceToVideo. No AlienPc Shell. No skill/Jobs edit. No invent numbers. No quality KEEP crown.  
**Adults 21+ fiction I2V / REF2VA only.**

---

## Dial card (paste)

KEEP: argv NODDV + no-fp8 + --use-ck-attention ON + scheduler beta + 25 steps + res_multistep + REF2VA `ref_image_size=match` + sigma video 12 / audio 3 — settings GO only (2026-10-02 Derrick) · `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md` · `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md` · A/B 15s boards `/workspace/MAX_REF_ORC_BJ_15S_2026-10-05/SCOREBOARD_A_ORAL_15S.md` (+ B)

TRY-NEXT: one-axis native canvas short-edge ~768 AR-locked to Cond (e.g. landscape 1344×768 / portrait 768×1344 inside 768×1344 area cap); leave argv/steps/scheduler/sigma/match alone; OOM → stop, do not drop NODDV — https://docs.comfy.org/tutorials/video/minimax/minimax-h3 · local plan `/workspace/cos/status/ce-plan-beach-quality-speed-2026-10-03.md` · Remacri only after a native survivor, single Lanczos after 4× (`downscale_ratio=1`), not a hand/contact fix — `/workspace/cos/research/2026-10-02-remacri-settings-check.md`

DROP: STEPS-20 · SPARSEsol · Sage · fp8/DynVRAM peel · Lightning 4-step on R2V · Topaz as generate fix · Remacri as Quality/hand fix · inventing clip KEEP on soft mush — `max-8189-production-keep.md` · `experimental-do-not-default.md` · Comfy R2V Lightning note · `/workspace/cos/research/2026-10-02-free-video-upscalers.md`

---

## TLDR (6 lines)

1. Settings KEEP is already Derrick GO (beta/25/ck/NODDV/match/sigma 12/3). Soft mushy hands/contact/plastic is a **Quality break in words**, not a reason to reopen STEPS-20/SPARSE/Sage/fp8.
2. Soft at 864×480 is a **resolution-first** problem per Comfy: steps do not add sharpness the native canvas cannot resolve; open weights are ~768 short edge / ~1 MP.
3. TRY-NEXT = one-axis native ~768 short edge (AR-lock Cond), same KEEP argv. No fair scored 768 ORC BJ yet (Q5 seed 25100334 VOID wrong cond).
4. Remacri enlarges only; cannot invent anatomy. Fix double Lanczos; run after native survivor. Not a score axis.
5. Leave `ref_image_size=match` and sigma 12/3 unless a measured ID or audio failure. `max` is slower ID fidelity, not a sharpener.
6. 15s A/B boards are **TECH ok / KEEP no** on clips; Dial “15s KEEP” means the settings stack, not a quality crown.

---

## 1) Resolution & `ref_image_size`

| Fact | Cite |
|------|------|
| Open weights: **768px short edge**, ~1 MP, 24 fps, ~15 s. Frames well above native do not hold detail; later upscale cannot recover what generate left out. Soft frame = **resolution problem first**. | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 |
| Full-quality 16:9 native: Megapixels **0.98** → **1344×768**. Skip 1.0 MP (1376×768) — over 768×1344 area cap. Node defaults 1344×768. | same Comfy guide · https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo |
| Fleet production canvas still **864×480** (preview / prior KEEP match). | `max-8189-production-keep.md` · SCOREBOARD_MATRIX |
| Local plans already name climbing to **768 short edge** (e.g. 768×1344 portrait / 1344×768 landscape) after 480 issues; **OOM stop; do not drop NODDV**; Remacri not a substitute for native pass. | `/workspace/cos/status/ce-plan-beach-quality-speed-2026-10-03.md` · `ce-plan-5s-quality-speed-2026-10-03.md` |
| Q5 768 script target was **1344×768**, same beta/25/ck/match/sigma 12/3 — seed **25100334 VOID** (wrong cond). **NO scored quality result** for 768. | `/workspace/Q5_5S_768/run_q5_768.py` · `/workspace/cos/research/2026-10-03-ce-system-cause-doublecheck.md` |
| `ref_image_size=match` (default): scale refs down to gen pixel area (speed). `max`: up to 2048 short edge, stronger identity, refs ride every step → can be several× slower. Never upscales refs. | Comfy node docs · local `/workspace/cos/research/2026-10-02-max-ref-image-best-practices.md` |
| Beach measure: seated 362f/480, `max` **1170.5s** vs `match` **597.3s** (**1.96×**). Identity knob, not sharpness. | `/workspace/cos/audits/2026-10-03-beach-speed-audit.md` |
| 15s A/B used **match** at 864×480. | SCOREBOARD_A/B_ORAL/DOGGY_15S |

**Call:** For mushy soft Quality, TRY native ~768 short edge **before** flipping `match`→`max`. Keep match unless mid-clip **identity** fails.

---

## 2) Steps / scheduler

| Fact | Cite |
|------|------|
| **KEEP:** `res_multistep` + **`beta`** + **25 steps**. | SCOREBOARD_MATRIX · `max-8189-production-keep.md` |
| **DROP STEPS-20:** faster wall, Integrity under-denoise / softer contact vs BASE. | SCOREBOARD_MATRIX |
| Comfy template default (Lightning off): **20** steps; if reference still drifts, raise to **25**. Lightning 4-step on R2V **starves** reference tokens. Most prompt/motion gain by ~16; high-freq detail can climb toward ~50; **steps do not add sharpness native canvas cannot resolve**. | Comfy MiniMax H3 guide |
| Template ships scheduler **`simple`**; fleet fair warm preferred **`beta`** (125.5s vs simple 135.4s, Integrity ≈BASE). | Comfy guide · SCOREBOARD_MATRIX |
| Sampler for REF-heavy: `res_multistep` + beta/normal often beats simple (Comfy R2V tips). | `/workspace/cos/research/2026-10-02-max-h3-prompting-best-practices.md` |

**Call:** Do **not** reopen STEPS-20 for “sharper.” Do **not** expect more steps at 480 to fix soft mush — Comfy says soft = resolution first. KEEP beta/25.

---

## 3) Sigma / shift

| Fact | Cite |
|------|------|
| H3 model definition: **`shift` 12 / `audio_shift` 3**. Workflows (except FastH3) read those. FastH3 uses 10/3 for its distilled schedule. | Comfy MiniMax H3 guide (Sampler and scheduler) |
| Local graphs: `MiniMaxH3SigmaShift` **shift_video 12.0 / shift_audio 3.0** on speed matrix and 15s A/B. | `queue_15s_ref2va.py` · SCOREBOARD_A/B · speed matrix scripts |
| Raise **audio** shift ~6–9 only if turbo **audio** thin — picture sharpness not cited. | AUDIT_10EROS_MAX · `/workspace/cos/research/2026-10-02-max-audio-sex-sounds.md` · ce-plan-max-speed-quality-matrix OPT-AUDIO-SHIFT optional |

**Call:** Leave **12 / 3** for sharper picture. No cited picture-quality win from changing video shift on base/TURBO-hybrid KEEP. FastH3 shift pair is a **different checkpoint** — do not mix.

---

## 4) Length vs quality

| Fact | Cite |
|------|------|
| Trained length band **~124–362f (~5–15s)** @ 24 fps. | Comfy node `length` · Comfy guide |
| 15s A oral + B doggy: **362f**, 864×480, beta/25/ck/NODDV/match, sigma 12/3 — **TECH ok**, clip **KEEP: no**. Walls ~611s / ~606s. | SCOREBOARD_A/B_15S |
| Longer clip ≠ more native spatial detail. Soft mush at 15s still resolution/generate anatomy. | Comfy “soft frame = resolution first” |
| Product ~60s = multi-clip chain, not one Generate. | local-video-ops · max-h3 prompting research |

**Call:** Staying at 15s (362f) is in-band. Length alone will not clear mushy hands. Prefer sharper **native canvas** at the same length (or a shorter TECH at 768 if VRAM forces it) — do not invent a new frame count.

---

## 5) Remacri vs native

| Fact | Cite |
|------|------|
| Remacri = post file upscaler (`4x_foolhardy_Remacri.pth`), not a score axis. Topaz dropped as generate fix. | fleet locks · free-video-upscalers · remacri-settings-check |
| Author intent: less mushy/blurry skin than some ESRGAN peers; still **enlarge only**; **not temporal**; does **not** repair melted hands/contact. Plastic/grain tradeoff known. | https://openmodeldb.info/models/4x-Remacri · remacri-settings-check · free-video-upscalers |
| Prior 864→~1080 graph: WRONG double Lanczos (`downscale_ratio=0.56` then second ImageScale). TRY: `downscale_ratio=1` + **one** Lanczos to target (or CRT fixed res if import works). | remacri-settings-check |
| Plans: Remacri **only after native survivor**. Do not Remacri a 480 Quality fail and call it fixed. | ce-plan-beach-quality-speed · ce-plan-5s-quality-speed · brainstorm Remacri not hand fix |
| Stay on Remacri vs free alternatives for enlarge-class; SeedVR2 redraw risk on contact — not installed, not tonight. | free-video-upscalers |

**Call:** Native ~768 first (detail into the generate). Remacri second for display size, with single-resample fix. Remacri does **not** clear Quality soft hands/contact.

---

## 6) Do-not-reopen drops

| Drop | Why | Cite |
|------|-----|------|
| STEPS-20 | Under-denoise / softer contact | SCOREBOARD_MATRIX |
| SPARSEsol | Activated, slower vs KEEP | SCOREBOARD_MATRIX · experimental-do-not-default |
| Sage | Skipped; not production argv | max-8189-production-keep |
| fp8 / DynVRAM peel | HostBuffer / kitchen float8; NODDV KEEP | experimental-do-not-default |
| Lightning 4-step on R2V | Starves reference tokens | Comfy guide |
| Topaz as generate Quality fix | Fleet drop; perpetual vs 1.7 split separate | upscale-remacri-vs-nvidia · brainstorms |
| Remacri / UltraSharp / latent 2× as hand fix | Enlarge ≠ anatomy | free-video-upscalers · 5s brainstorm |
| Crowning soft clip KEEP | KEEP = Derrick GO on argv; clips A/B KEEP no | scoreboards · live-scored-research-review |

---

## 7) Contradictions (do not collapse)

1. **Comfy template** defaults: scheduler `simple`, 20 steps (Lightning off), canvas 1344×768. **Fleet KEEP:** `beta`, 25 steps, canvas 864×480. Prefer fleet KEEP for argv; use Comfy native-canvas guidance for the **768 try**.
2. Dial phrasing “15s KEEP” vs scoreboards **KEEP: no** — settings stack vs clip quality. Soft Quality ≠ clip KEEP.
3. Remacri is KEEP **export arm** and also called plastic / not a hand fix — both true; different jobs.
4. Q5 “768” run exists as script/output name but seed **VOID** — cannot cite as quality evidence.
5. Older prompting research still says “prefer ~20 base if Lightning starves” — fleet already locked **25** after fair matrix; do not walk back to 20.

---

## 8) Unknowns (NO_DATA — do not invent)

- Wall time / OOM at **1344×768 or 768×1344 × 362f** on RTX 5070 Ti 16GB with KEEP argv.
- Whether ~768 alone clears mushy hands/contact on ORC BJ oral/doggy (no fair scored cell).
- Whether TURBO-hybrid plastic look needs non-turbo hybrid checkpoint (AUDIT names plastic turbo as a failure mode; no fair A/B crown here).
- Best Remacri target dims for a 768-native source (old recipe was 864→1920×1066).
- `ref_image_size=max` quality delta on ORC BJ 15s (only beach speed 1.96× measured).

---

## 9) Sources

**Local:**  
`/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md`  
`/home/box/agent-data/workflows/alienpc-local-video-ops/references/experimental-do-not-default.md`  
`/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md`  
`/workspace/MAX_REF_ORC_BJ_15S_2026-10-05/SCOREBOARD_A_ORAL_15S.md` · `SCOREBOARD_B_DOGGY_15S.md` · `scripts/queue_15s_ref2va.py`  
`/workspace/cos/research/2026-10-02-remacri-settings-check.md` · `2026-10-02-upscale-remacri-vs-nvidia.md` · `2026-10-02-free-video-upscalers.md`  
`/workspace/cos/research/2026-10-02-max-h3-prompting-best-practices.md` · `2026-10-02-max-ref-image-best-practices.md`  
`/workspace/cos/audits/2026-10-03-beach-speed-audit.md`  
`/workspace/cos/status/ce-plan-beach-quality-speed-2026-10-03.md` · `ce-plan-5s-quality-speed-2026-10-03.md`  
`/workspace/Q5_5S_768/run_q5_768.py`  
`/workspace/cos/research/alienpc-ltx-stack-2026-09-25/AUDIT_10EROS_MAX_SMOKE_READY_2026-10-01.md` (shift defaults)

**Official web:**  
https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo  
https://openmodeldb.info/models/4x-Remacri  

---

*Research only · 2026-10-05 ~8:30 AM CT · no AlienPc Shell · no invent KEEP · settings KEEP = prior Derrick GO only*
