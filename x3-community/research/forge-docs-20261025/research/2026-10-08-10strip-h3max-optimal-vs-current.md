# RESEARCH: 10Strip (TenStrip / 10Eros) H3 Max optimal settings vs AlienPc Max Studio CURRENT. 2026-10-08 ~1:12 PM CT (written 13:12:42 CT per file mtime; label corrected 2026-10-08 13:40 CT, was future-dated "~1:40 PM CT"; body unchanged)

**Owner:** Max Research executor (research only) · **AlienPc / Comfy :8189 not touched** (no Shell lease, no queue, no argv change, no messages)
**Locks:** KEEP = Derrick exact GO only (nothing here is a KEEP recommendation) · fiction adults 21+ · NO_DATA = not in our files / not published. Never guessed.
**Name check:** "10Strip" = Civitai/HF author **TenStrip**. The model is **10Eros-Max** ("H3 Eros Max", Civitai 2851079), a merge on **MiniMax-H3**. **Latest release = beta5** (Civitai published 2026-09-07; HF repo last modified 2026-09-08). Today the author lists no beta6 and no H3 workflow repo (TenStrip/Workflows last modified 2026-04-20, pre-H3). The "workflow" recs below therefore come from the author's card, README and comments, plus the stock Comfy H3 templates the author says the files "drop straight into".

## TLDR (where we are off the author/official optimum)
1. **TE placement (biggest wall cost).** We run the 32B TE on the **CPU** (`--lowvram` under NODDV = TE→CPU only). Official default is TE on GPU, with partial-load streaming in NORMAL_VRAM. Fixing it needs an argv change, so Derrick GO (W3, see TE spike stamp).
2. **Turbo-look / plastic mitigation not used.** The author recommends **LCM/simple 6–8** or **Tr1dae Latent Contrast 0.85**, "which eliminates that". Tr1dae pack is installed on :8189 (10-02). We use neither.
3. **Audio shift at ST8.** We run the default 12/3. The author says raising **audio shift to ~6–10 (e.g. 9)** "can improve audio in some low step situations". Official docs say audio is weakest at 8 steps.
4. **No concept LoRA.** We stack zero LoRAs. The author: "1 additional lora at 0.5 would've saved you 100 generations". Concept LoRAs on top of beta5 at **0.2–0.6** (new LoRAs 0.5–1.0). For t2v/some i2v, "100% be loading mystic_v4, anatomy enhancer…".
5. **Quality lane and quant.** KEEP-25 runs on the **TURBO** file. The author says turbo = 4–8 steps "instead of 25", and the 20–25 full-step lane is the **non-turbo** file (already on disk, W9). For w4a8, the author links **LokkenJP learned quant** files as "the correct use and optimization files". We run stock TenStrip w4a8.

## STEP 1: CURRENT config (from our files only)
| Setting | Current | Source path |
|---|---|---|
| Checkpoint | `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized` (13.04 GiB, turbo baked, no LoRA node) | `/workspace/cos/tmp_opt_queue.py` L9 · `research/2026-10-08-max-te-on-gpu-spike.md` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq` (15.69 GB). `CLIPLoader device=default` → **CPU** under `--lowvram` | `tmp_opt_queue.py` L10, L54 · TE spike stamp |
| VAEs | video `minimax_h3_video_vae_int8_convrot` · audio `…_fp32` | `tmp_opt_queue.py` L11–12 |
| Steps | **ST8** default (Derrick lock 2026-10-05 ~9:27 PM CT). ST16 on ask. **KEEP-25** quality/ID lane (Oct 2 GO, not revoked) | `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md` · `handoffs/2026-10-05-fabric-v3-st8-keep.md` |
| Sampler | `res_multistep` (KSamplerSelect) | production-keep · `tmp_opt_queue.py` L31 |
| Scheduler | **`simple`** working default since 2026-10-06 (held baseline, Dial eyes, **NOT KEEP**). ⚠ production-keep.md still says `beta` (2026-10-02/05 KEEP), so the docs have drifted | `gbrain/04_memory/max-optimize-2026-10-06/2026-10-06_decision_max-optimize-simple-over-beta-ST8.md` · `derek-twin/LIVE-RESUME-2026-10-08.md` L39 |
| CFG / guidance | `BasicGuider` (no CFG; checkpoints are CFG-distilled). No CFG-zero/star | `tmp_opt_queue.py` L64 |
| Shift | `MiniMaxH3SigmaShift` video **12** / audio **3** | `tmp_opt_queue.py` L57 |
| Frames | **124f** (~5.17 s) on 17k+5 grid. 243/362 probed (super-linear wall) | production-keep · `…/2026-10-06_note_h3-longer-length-vs-wall.md` |
| fps / RIFE | Native **24 fps** `CreateVideo`. RIFE (rife47, CFI) fair cell 9/9 @768 landed 10-06 (R0 ~139 s · R12→RIFE 2× ~54 s · R8→3× ~38 s). **Awaiting Derrick eyes, not in product path** | `tmp_opt_queue.py` L68 · `max-studio-2026-10-06/RIFE_FAIR_LAND_GO_2026-10-06.md` |
| Canvas | **768×1344** portrait, AR-locked to Cond (quality SoT). Preview 480×864 portrait | production-keep · LIVE-RESUME L39 |
| Ref images | `ref_image_size=match`. Cond as Picture 1 (Method A/C hops add the last frame as Picture 2) | `tmp_opt_queue.py` · `research/2026-10-06-hop-a-5s5s-softcut-result.md` |
| LoRA | **None** in the Max H3 graph (turbo baked) | `tmp_opt_queue.py` build() |
| Attention | Comfy Kitchen (`--use-ck-attention`) | production-keep |
| Cache / spectrum / Sage / sparse | None (DROP list) | production-keep |
| Upscale | Post-gen **`4x_foolhardy_Remacri` full 4×** (`downscale_ratio=1`, ERRATA struck the ~1080 Lanczos). SeedVR2 = CANCEL. RTX VSR + Tr1dae H3 latent upscaler installed 10-02, not in path | `max-studio-2026-10-06/REMACRI_FULL_4X_ERRATA_2026-10-06.md` · `LIVE-RESUME-2026-10-08.md` L17 · `status/2026-10-02-latent-rtx-blockers.md` |
| Face restore | **None in production.** D0/D1 CodeFormer + D2 GFPGAN smoke landed 10-06 (fairness PASS, not KEEP) | `audits/2026-10-06-5s-d1-d2-land-fairness-auditor.md` |
| :8189 argv | `main.py --listen 127.0.0.1 --port 8189 --lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention` | production-keep |
| Warm | ~1 s sacrificial, then full 124f warm (unscored) | production-keep |

## STEP 2: Author / official / community recommendations
**Author (TenStrip), beta5 unless noted:**
- A1 **Default file:** "Use **TURBO-hybrid_int8** by default." The 'fp8' file "is actually a w4a8… **only for 12–16g cards**". "Turbo models sample in **4–8 steps instead of 25**." [P2, P3 Sep 8]
- A2 **Sampler setups:** er_sde/beta 4 · er_sde/beta57 4–6 ("best preservation of style and reduced drift") · **res_multistep/simple 6–8 (README: "my go-to for best motion quality"; card: 6–9)**, where beta at 8–9 is "sharpest fast motion… but plastic/burned" · **LCM/simple 6–8 ("best turbo audio")** · LCM/beta 4–6 · Euler/simple 4–8. Comment Sep 9: "multires[=res_multistep]/beta 8–9 for dark, cinematic, high motion". [P1, P2, P3]
- A3 **Shift:** "Default 12/3", which is also the model default, so "you could remove the node and get the same". "**increasing audio shift to double or triple like 9 can improve audio in some low step situations**" / "up to 6–10 on low steps". [P3 Sep 7, Sep 9]
- A4 **Audio:** "Non-turbo full step audio will always be better." The non-turbo file is for "PDD or Fast accelerations, or mainly full steps". PDD = "6 warmup and 4 PDD turbo steps" (separate pipeline: aptech0081 Acc-LoRAs + Jalen-Brunson PDD-Acc). [P1, P2, P3 Sep 8, Sep 10]
- A5 **Speed:** "Nothing but **comfy_kitchen** backend, or maybe SLA. The other speed ups aren't worth using… reduce a lot of quality." "**No cache or spectrum if doing reference**." [P1, P3 Sep 8]
- A6 **LoRA:** concept LoRAs on top "usually needing lower strength **0.2–0.6**". New LoRAs not in the merge: "**0.5–1.0**". "1 additional lora at 0.5…". For t2v and some i2v "100% be loading mystic_v4, anatomy enhancer, or a related concept lora". Contradiction: on Sep 12 the author says most LoRAs aren't trained on reference and "will impact it negatively", and that he is moving to 5 MB "refmods" (not found published: NO_DATA). [P2, P3]
- A7 **Mode, refs, canvas:** "Don't use i2v, use reference… lock the input image as the start frame". "REF2VA works with **up to 9 images**". Add an extra un-cropped ref for anatomy (`partially_preserved`). "**Increase the resolution and decrease length**." Low-res smear is "also a problem in base model". [P3 Sep 9–10 · P6 quirks]
- A8 **Turbo-look mitigation:** "LCM/simple 6–8 steps or use the **latent contrast node** from Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler and **reduce to 0.85**". [P3 Sep 13 · C3: `contrast=1` no-op, `preserve_norm` default]
- A9 **w4a8 optimization:** "If you download the 'fp8' which is actually a w4a8 you need to check this out too for the correct use and optimization files: LokkenJP/10Eros_Max_optimized_w4a8_exp_learned". [P3 Sep 8]
- A10 **Upscale / face-restore / RIFE / fps / frames:** **NO_DATA from the author** (re-checked today. Matches the 10-06 upscale stamp `c145a993…`).
- A11 **Older-beta note (PromptHero mirror, pre-beta5 text):** "Turbo not recommended yet for i2v… Use 20–25 steps normal sampling… 25 steps with dialogue… full int8 incl. int8 qwen3vl". **Superseded by beta5's turbo-baked recs.** Applies only to non-turbo. [P6]

**Official (Comfy / MiniMax):** res_multistep + simple in every template · shift from the model def 12 / audio 3 · base 20 steps (25 if the reference drifts) · turbo 8 (I2V) / 4 (R2V) · audio weakest at 8 steps, ≥12 usable · native 768 short edge, **768×1344 area cap**, 24 fps, ~15 s max, trained 124–362f · "generate at native canvas and upscale in a separate pass" (2K is hosted-only) · ck attention fixes INT8-Sage artifacts · sol-attn gain grows with length · `--lowvram` under NODDV = TE on CPU · CFG-distilled checkpoints. [O1–O5]

**Community:**
- C1/C2 **LokkenJP (author-linked):** current recommended **V8 INT8/W6A8/W4A8 hybrid, 14.5 GB** of TURBO beta5 (repo updated 2026-10-05). Needs ComfyUI + Comfy Kitchen with W6A8 support. Also ships a learned **non-turbo** beta5 w4a8. Sample workflows:
  - 1-pass: **er_sde/simple 6**, shift **6/3**, comfy-kitchen attention node, R2V **1344×768×124 `match`**, 24 fps, **RTX Video Super Resolution ×1.3 ULTRA**, TE `qwen3vl_32b…int4_convrot` (not in the Comfy-Org TE tree today: provenance NO_DATA).
  - 2-pass v5: res_multistep/simple 6 + ManualSigmas 3–5-step second pass via **MinimaxH3LatentUpscaler3D** to 0.8 MP, shift 12/3, RTX VSR ×1.3.
- C4 **Reddit r/StableDiffusion** "What sampling settings for Minimax H3…": res_multistep + simple preferred over er_sde/sgm_uniform. Motion clearly better after **24→48 fps interpolation**. 0.7 MP @ 8 s on a 4090 ≈ 270–330 s. Others: res_2s/simple 16, 16–20 steps on base.
- C5 **Tomiigo 16 GB (5070 Ti):** `--disable-pinned-memory` ≈ +20% runtime. Full-res REF@243 1,027 s vs 170 s downscaled (10-06 stamp, page 200 today).

## STEP 3: DIFF (current vs 10Strip/official optimum)
| # | Setting | Current | 10Strip / official rec | Flag | Note + cite |
|---|---|---|---|---|---|
| 1 | Checkpoint quant | TURBO beta5 **w4a8** (stock) | Author default **int8 TURBO** (21 GB). w4a8 = "only for 12–16g cards" | **MATCH** (16 GB) | int8 won't fit 16 GB well. A1 |
| 1b | w4a8 build | TenStrip stock w4a8 | Author-linked **LokkenJP learned V8** (int8/w6/w4, 14.5 GB) | **DIFF** | Author: "correct use and optimization files". Needs W6A8 Comfy support. A9, C1 |
| 2 | Steps (speed lane) | ST8 | 6–8 (README go-to) / 6–9 (card) on turbo | **MATCH** | A2 |
| 3 | Steps (quality lane) | KEEP-25 on **TURBO** file | 20–25 = **non-turbo**/base only. Turbo "4–8 instead of 25" | **DIFF** | Mismatch. Non-turbo w4a8 already on disk (W9). A1, A4, O1 |
| 4 | Sampler | res_multistep | res_multistep (go-to motion). LCM for audio. er_sde/beta57 for least drift | **MATCH** | er_sde/beta57 VOID on :8189: RES4LYF import fails (`pywt` missing, 10-02 log). A2 |
| 5 | Scheduler | simple (working default, not KEEP). Docs say beta | simple. beta@8–9 = plastic/burned (beta only for dark/high-motion) | **MATCH** (working) / **DIFF** (production-keep.md still says beta) | Docs out of sync. A2, O1 |
| 6 | CFG | BasicGuider, none | CFG-distilled; templates use no CFG | **MATCH** | O4 |
| 7 | CFG-zero/star tricks | none | none recommended | **MATCH** (N/A) | No source recommends them |
| 8 | Shift video | 12 | 12 (default) | **MATCH** | A3, O1 |
| 9 | Shift audio | 3 | Default 3, but **6–10 (e.g. 9) at low steps** helps audio | **DIFF** | We run low steps (ST8). A3 |
| 10 | Turbo-look fix | none | **LCM/simple 6–8** or **Latent Contrast 0.85** | **DIFF** | LCM R2 "quality parked" 10-06. Contrast never tried. Node pack installed 10-02 (contrast node present? NO_DATA). A8 |
| 11 | Frames | 124f | Trained 124–362. Author: "increase resolution and decrease length" | **MATCH** | A7, O3 |
| 12 | fps / interpolation | native 24. RIFE fair landed, not product | Official 24. Author NO_DATA. Community 24→48 interp | **NO_DATA (author)** | RIFE awaits Derrick eyes. C4 |
| 13 | Canvas | 768×1344 portrait AR-locked | Native 768 short edge, cap 768×1344. Author: raise resolution | **MATCH** | O1 |
| 14 | Mode / refs | REF2VA, Cond = Pic1 (+lastframe on hops) | "Use reference, not i2v". **Up to 9 refs**; add an anatomy ref | **MATCH** mode / **DIFF** ref count | Extra anatomy refs unused. A7 |
| 15 | LoRA stack | none | Concept LoRA **0.2–0.6** (in-merge) / 0.5–1.0 (new) | **DIFF** | Author conflict on ref (A6). H3 LoRA files on AlienPc: NO_DATA |
| 16 | Attention | ck (argv) | "Nothing but comfy_kitchen backend, or maybe SLA" | **MATCH** | A5 |
| 17 | Cache / spectrum / Sage | none | none on reference | **MATCH** | A5 |
| 18 | TE file | nvfp4_awq 15.69 GB | Official TEs: bf16 / int8_convrot / nvfp4_awq. Lokken uses int4_convrot | **MATCH** (smallest official) | O5, C2 |
| 19 | TE placement | **CPU** (`--lowvram`) | Official/default: GPU (NORMAL_VRAM / DynVRAM) | **DIFF** | ~6–7 min per new paste is user-reported only (not logged). TE spike O1. O2 |
| 20 | Async / pinned | both disabled | Default ON; 10–50% when spilling; 5070 Ti −20% without pinned | **DIFF** | W5 pinned TECH ok @480; W6 async no result. O2, C5 |
| 21 | DynamicVRAM | disabled (HostBuffer 1450) | Default ON | **DIFF by design** | Stability. Upstream PR #15944 status not re-checked today |
| 22 | Upscale | Remacri 4× full (post) | Author NO_DATA. Official: separate pass. Community: RTX VSR ×1.3 / H3 latent upscaler 3D 2-pass | **NO_DATA (author)** / DIFF vs community | Community ≠ author. A10, C2 |
| 23 | Face restore | none in prod (CF/GFPGAN smoke) | Author NO_DATA (fix via resolution/composition/extra refs) | **NO_DATA (author)** | A7, A10 |
| 24 | Speed accel (PDD) | none | Non-turbo + PDD "6 warmup + 4 PDD turbo steps" (optional) | **DIFF** (optional) | Needs new custom node + LoRAs. A4 |

## Safe to try (reversible · workflow-node only · no argv / restart / download). Each still needs a Dial lease and Derrick GO to run, and is a one-axis METHOD twin
- S1 Audio shift **3 → 9** at ST8 (row 9).
- S2 **Latent Contrast 0.85** before VAEDecode on ST8 simple. First do a read-only object_info check that the node exists (row 10).
- S3 Re-run **LCM/simple ST8** at 768×1344 for the turbo-look/audio axis. R2 was parked at 480 (row 10).
- S4 Add a 2nd **anatomy reference** image (`partially_preserved`) on one cell (row 14).
- S5 Docs-only: reconcile production-keep.md (`beta`) with the working default `simple`. **Owner + Derrick decide. Not a KEEP.**

## Needs Derrick GO (argv / restart / download / new node / Shell lease)
- G1 Drop `--lowvram` (TE→GPU, W3), optionally `--reserve-vram 2.5` (row 19).
- G2 Re-enable pinned, then async, one at a time (row 20).
- G3 Quality lane: **non-turbo** hybrid w4a8 at 20–25 instead of KEEP-25 on TURBO (row 3). File on disk, but a checkpoint swap.
- G4 Download **LokkenJP V8** learned quant (may need a Comfy/Kitchen update for W6A8) (row 1b).
- G5 Concept LoRA at 0.5 (needs the file; ref-impact risk per author) (row 15).
- G6 Fix RES4LYF (`pip install PyWavelets`) to unlock er_sde/beta57 4–6 (row 4).
- G7 PDD non-turbo pipeline (new custom node) (row 24).
- DynamicVRAM peel, Sage, EasyCache, spectrum, fp8 stay **DROP** (author agrees on cache/spectrum).

## NO_DATA (ask Derrick / read-only check)
1. H3 concept LoRA files on AlienPc (mystic_v4, anatomy enhancer, pose LoRAs): not in our files.
2. Whether the installed Tr1dae pack has the **Latent Contrast** node (installed 10-02; author comment 9-13).
3. Audio shift ≠3 ever tested: no record.
4. TE encode time per new paste: the 6–7 min figure is user-reported; no logged per-node timing.
5. Product fps/interp decision: RIFE landed, Derrick eyes pending.
6. Production face-restore and upscale for the **product** path: Remacri is the lock for the upscale arm; face D1/D2 not KEEP.
7. Scheduler of record: `simple` (working) vs `beta` (production-keep.md). Needs Derrick to confirm which is canonical.
8. Comfy version/commit on AlienPc (needed for LokkenJP V8 W6A8 support): not in files today.
9. Author "refmods" (5 MB concept files + workflow, Sep 12): not found published.

## Sources (all accessed 2026-10-08 CT; HTTP 200 unless noted)
**Author-primary (6)**
- P1 https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md (repo lastModified 2026-09-08)
- P2 https://civitai.com/api/v1/models/2851079 (author card; beta5 published 2026-09-07)
- P3 https://civarchive.com/models/2851079?modelVersionId=3294059 (author comments Sep 7–13, 2026)
- P4 https://huggingface.co/api/models/TenStrip/10Eros-Max/tree/main (file list: TURBO + non-turbo w4a8, int8, bf16)
- P5 https://huggingface.co/api/models?author=TenStrip (no H3 workflow repo; TenStrip/Workflows last mod 2026-04-20)
- P6 https://prompthero.com/ai-models/h3-eros-max-2851079-download/h3-eros-max-beta5 (card mirror incl. older-beta notes)

**Official-primary (5)**
- O1 https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- O2 https://docs.comfy.org/development/comfyui-server/startup-flags
- O3 https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo
- O4 https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/README.md
- O5 https://huggingface.co/api/models/Comfy-Org/MiniMax-H3 (TE files; lastModified 2026-09-29)

**Community (5)**
- C1 https://huggingface.co/LokkenJP/10Eros_Max_optimized_w4a8_exp_learned/raw/main/README.md (author-linked)
- C2 https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned/tree/main/SampleWorkFlowTwoPassOptimized (H3_Turbo_1Pass_JP.json, H3_Turbo_2Pass_JP_with_prev_v5.json; repo lastModified 2026-10-05)
- C3 https://raw.githubusercontent.com/Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler/main/README.md (author-linked)
- C4 https://www.reddit.com/r/StableDiffusion/comments/1vvh0lm/what_sampling_settings_for_minimax_h3_are_you/ (direct fetch **403**; content via WebSearch index snippet)
- C5 https://github.com/Tomiigo/minimax-h3-16gb (200; figures from 10-06 stamp)

**Local priors:** `research/2026-10-06-max-keep-vs-official-10eros-community.md` · `research/2026-10-06-max-8189-keep-vs-official-community-optimize.md` (ERRATA3) · `research/2026-10-06-tenstrip-author-upscale-path.md` · `research/2026-10-08-max-te-on-gpu-spike.md` · production-keep.md · fabric V3 KEEP handoff.

*Research only · no KEEP / PASS · AlienPc untouched · no messages sent*
