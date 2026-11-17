# RESEARCH — Max :8189 KEEP vs official MiniMax-H3 docs + 10Eros author + community — 2026-10-06

**When_CT:** 2026-10-06 ~8:25 AM CT · **Owner:** executor for Dial 3 (research only) · **AlienPc / Comfy :8189 not touched** (no Shell, no queue, no /free, no argv change) · Live S1 left alone
**Fiction lock:** LoRA/Cond names are labels only. This brief covers only technical settings (argv, canvas, steps, sampler, wall time).
**Tools:** WebFetch (docs.comfy.org, HF, GitHub, InstaSD, Comfy blog) · curl (HF raw README + HF tree API, Civitai public API v1, ComfyUI `master` source on raw.githubusercontent) · Read (local priors). No Firecrawl: the plugin skills path `/home/box/agent-data/plugins/firecrawl/skills/` doesn't exist, and every page came through without it.

## Plan (≤10 lines · plan-md-quality-bar)
1. Re-fetch the official primaries today: Comfy H3 tutorial, startup flags, the two H3 node pages, MiniMaxAI HF card.
2. Pull the 10Eros author settings: TenStrip HF README plus Civitai card 2851079 (beta5).
3. Check the `--lowvram` meaning against ComfyUI source (`cli_args.py`, `model_management.py`, `main.py`). Docs alone aren't enough here.
4. Read the 5 local priors plus today's audits for measured walls (no invented numbers).
5. Give a verdict per axis (a) argv (b) canvas (c) steps (d) 15s@768 wall: OPTIMIZED / PARTIAL / NOT.
6. Name the gaps as one-axis TRY candidates only. No KEEP and no PASS from me. Derrick decides with an exact GO.

---

## TLDR
- **(a) argv / lowvram: PARTIAL.** NODDV (no dynamic VRAM) is a correct, documented workaround: HostBuffer crashes are the aimdo/DynamicVRAM path, and upstream fix PR #15944 is still **open**. **But our stated reason for `--lowvram` is wrong.** Official docs and ComfyUI source both say that with dynamic VRAM off, `--lowvram` **only moves the text encoder to the CPU**. UNET partial loading/streaming happens in plain NORMAL_VRAM mode too. Separately, `--disable-async-offload` + `--disable-pinned-memory` is the **slowest offload path**. Comfy's own blog says those two features cut the offload penalty by 10–50%. They were added in the same step as two other changes (Oct 2 S0 chain), so we never proved either one was needed.
- **(b) canvas: OPTIMIZED for quality.** 768×1344 is exactly the official native cap (768 short edge, ~1 MP, multiple of 32). For speed at 362f on 16 GB it sits right at a memory cliff (see d).
- **(c) steps: PARTIAL.** ST8 matches the author's band for TURBO-hybrid (res_multistep 6–9). **But the author's card says `beta` at 8–9 steps gives "a plastic/burned look"** and recommends `simple`. Our Oct 5 notes complained of exactly "plastic skin". Also, **KEEP-25 on a TURBO-baked checkpoint matches neither source.** Official 20–25 steps assumes base weights with turbo off. Author turbo recipes stop at 9 steps and say non-turbo full-step is better for audio. The non-turbo `hybrid_beta5_w4a8_14gb_optimized` (same 14.0 GB) is the file that matches a 20–25-step quality lane.
- **(d) 15s @ 768×1344 portrait wall: NOT OPTIMIZED.** Local evidence: NE768 362f showed **UNET 0.00 MB resident / 13,349 MB offloaded, ~950–1,100 s/it vs 19.4 s/it** at 864×480/362f. Today's S1 is 30+ min. That is a VRAM spill cliff (~91.7k video tokens vs ~36.9k), made worse by synchronous unpinned weight streaming. A community 5070 Ti 16 GB report shows the same cliff (1,027 s full-res vs 170 s downscaled at 243f).

---

## Facts (cited · access date 2026-10-06 CT unless noted)

### Official — Comfy / MiniMax
| # | Fact | Source |
|---|------|--------|
| F1 | Open weights generate at **768 px short edge (~1 MP), 24 fps, ~15 s**. For 16:9 native use 0.98 MP = **1344×768**. Skip 1.0 MP (1376×768): it's **above the 768×1344 pixel-area cap**. Keep multiple = 32. Frames well above native don't hold detail. **"A soft frame is a resolution problem first."** | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 (2026-10-06) |
| F2 | Steps: base weights with Lightning **off = 20 steps (default)**. Turbo LoRA on = **8** (T2V/I2V) / **4** (R2V). On reference-driven shots turbo leaves the reference "barely applied" and pose/face drift. For close reference following, keep turbo off at 20 and raise to **25** if it still drifts. Simple content holds at 12–16. High-frequency detail improves up to ~50, and **turbo/distilled builds surface the grid artifacts first**. Most prompt/motion gain is reached by step 16. **Audio converges last: at 8 steps speech/voice is weakest; 12+ is usable.** | same |
| F3 | Every local template uses **`res_multistep` + `simple`**. Shift comes from the model definition (**video 12 / audio 3**). FastH3 uses 10/3. On distilled 8-step builds, a wrong shift shows grid artifacts. | same |
| F4 | `--use-ck-attention` (≥0.32) is the doc's fix for INT8 attention artifacts on **bf16** checkpoints. Comfy Kitchen attention **crashes on int8_convrot checkpoints** (issue #15529). The doc doesn't address w4a8. | same |
| F5 | Sparse attention (`sol-attn`, ≥0.35): **"the gain grows with sequence length"**. Sequences below `min_tokens` (default **12,288**) stay dense. **"Short clips gain little."** Defaults: start 0.2 / end 1.0, tau 1.3, `exact_kv_and_rows` keeps audio rows dense. | same |
| F6 | **`--lowvram`: "No effect when dynamic VRAM is enabled. Otherwise, runs text encoders on CPU."** Async offload is on by default on Nvidia. `--disable-pinned-memory` / `--disable-async-offload` / `--disable-dynamic-vram` are opt-outs. `--fast-disk` is dynamic-loading only. | https://docs.comfy.org/development/comfyui-server/startup-flags (2026-10-06) |
| F7 | **Source check (ComfyUI `master`, read 2026-10-06):** `cli_args.py` help text matches F6. In `model_management.py`, `--lowvram` sets `LOW_VRAM`. `text_encoder_device()` returns **CPU** under LOW_VRAM but **GPU** under NORMAL_VRAM (fp16-capable GPU). Partial model loading (`lowvram_model_memory`) runs for **both** `LOW_VRAM` **and** `NORMAL_VRAM` (L1021). In `main.py`, aimdo init only runs when `enables_dynamic_vram()` is true, so with NODDV the aimdo HostBuffer path is never initialized. | https://raw.githubusercontent.com/Comfy-Org/ComfyUI/master/comfy/cli_args.py · …/comfy/model_management.py · …/main.py (2026-10-06) |
| F8 | Node `length`: 17k+5 grid at 24 fps. **Trained range ~124–362**, longer untested. Defaults are 1344×768 / 124. `first_frame` is stretched; `last_frame` is cover-cropped. | https://docs.comfy.org/built-in-nodes/MiniMaxH3ImageToVideo (2026-10-06) |
| F9 | REF2VA `ref_image_size`: `match` (default) scales refs down to the generation area. `max` goes up to 2048 short edge and **can be several times slower**, because ref tokens ride every step. | https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo (2026-10-06) |
| F10 | MiniMax card: 4–15 s output, **default short side 768**, 24 fps, 32 kHz stereo. Checkpoints are **CFG-distilled**. VisualVAE f16t4 plus 1×2×2 patchify gives an **effective 32× spatial / 4× temporal** token grid. Native sparse attention was trained but not in the initial OSS release. | https://huggingface.co/MiniMaxAI/MiniMax-H3 (2026-10-06) |
| F11 | Comfy blog (2026-01-09): async offload + pinned memory are **on by default for all NVIDIA**. They give **10–50%** speedup whenever weights can't fully fit in VRAM. Benchmarks include an **RTX 5070 Ti**. Gains scale with PCIe link. | https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia (2026-10-06) |

### 10Eros author (TenStrip)
| # | Fact | Source |
|---|------|--------|
| T1 | Civitai model **2851079 "H3 Eros Max"**, beta5 published **2026-09-07**. Says: "**Use TURBO-hybrid_int8 by default**." TURBO files have the turbo delta baked in. "**Non-turbo full step audio will always be better.**" The file labeled just "hybrid" is non-turbo. Non-turbo option: "**6 warmup and 4 PDD turbo steps**". | https://civitai.com/api/v1/models?username=TenStrip (public API, 2026-10-06) |
| T2 | Working samplers for beta5 TURBO: `er_sde/beta57` 4–6 (best style preservation / least drift). **`res_multistep/simple` 6–9 ("good motion quality, beta will be the sharpest fast motion at 8–9 steps but will give a plastic/burned look")**. `LCM/simple` 6–8 (best turbo audio). `Euler/simple` 4–8. | same (Civitai) · HF README lists `res_multistep/simple 6-8 steps (my go-to for best motion quality)` https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md (2026-10-06) |
| T3 | "**No cache or spectrum if doing reference, they cause accuracy loss.**" Concept LoRAs on top at 0.2–0.6. beta3/beta4 are "corrupted test versions"; beta5 is the only functional one. | HF README (2026-10-06) |
| T4 | Repo has **both** `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized` (ours) **and** non-turbo `10Eros_Max_h3_hybrid_beta5_w4a8_14gb_optimized`, each **14.0 GB**. Repo last modified 2026-09-08. | https://huggingface.co/api/models/TenStrip/10Eros-Max/tree/main (2026-10-06) |

### Community
| # | Fact | Source |
|---|------|--------|
| C1 | **RTX 5070 Ti 16 GB** measured H3 (Linux, DynVRAM): REF graph at length 243 took **1,027 s full-res vs 170 s downscaled** (peaks 14.5–15.6 GB). `--disable-pinned-memory` made a run ~20% slower (180 s vs 150 s) because weights get re-read every step. Windows page-locks 40% of RAM vs 90% on Linux. | https://github.com/Tomiigo/minimax-h3-16gb README (2026-10-06) |
| C2 | InstaSD (read ComfyUI master 2026-08-08): `--lowvram` does nothing under DynamicVRAM. Async offload uses 2 transfer streams. Pinned RAM makes transfers fast. 16 GB advice: stock flags + 64 GB RAM, `--disable-pinned-memory` only if OOM. Spill example: a 4070 went from 167 s at 608×352 to **11 min at 864×480**, "every sampling step is paying transfer costs". | https://www.instasd.com/post/comfyui-vram-offloading-guide (2026-10-06) |
| C3 | Issue #14250 (open): HostBuffer.read_file_slice fails inside the **`comfy_aimdo` host_buffer** path. Several reporters fixed it by **hiding a second GPU/iGPU** (`--cuda-device`/`CUDA_VISIBLE_DEVICES`) instead of disabling pinned memory. Linked to #15255 and to PR **#15944 "Fix/aimdo windows pin budget"**, which shows **Open** today. | https://github.com/Comfy-Org/ComfyUI/issues/14250 · https://github.com/Comfy-Org/ComfyUI/pull/15944 (2026-10-06) |

### Local priors (fleet evidence · not re-measured)
| # | Fact | Path |
|---|------|------|
| L1 | Production KEEP: NODDV triad + no fp8 + ck. `beta` · `res_multistep` · dual lane **ST8 speed** (2026-10-05 GO) / **KEEP-25 quality/ID** (2026-10-02 GO). DROP list: STEPS-20, SPARSEsol, Sage, Turbo/Lightning/EasyCache/Spectrum, fp8, DynVRAM peel. | `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md` |
| L2 | Oct 2 matrix (864×480 · 124f · 25 steps): beta warm 125.5 s vs simple 135.4 s · ck cold −26.3% · STEPS-20 100.3 s "under-denoise" · **SPARSEsol 306 s FAIL speed** · Sage skipped. | `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md` |
| L3 | Oct 2 rationale: "`--lowvram` KEEP while NODDV … Needed for 15.7GB TE + 14GB UNET on 16GB card without AIMDO streaming". S0 chain: NODDV alone + :8188 up → access violation, then **NODDV + disable-async + disable-pinned + :8188 closed** → past load. **Three variables changed in one step.** | `/workspace/cos/research/2026-10-02-max-8189-setup-optimized.md` §2, §7 |
| L4 | Earlier speed research: no quality-neutral 2×. ck/sol-attn is the best fair one-knob. Turbo LoRA stacking on TURBO-hybrid is unproven. | `/workspace/cos/research/2026-10-02-max-h3-faster-gen-no-quality-loss.md` |
| L5 | Max file inventory: TURBO-hybrid beta5 w4a8 (~13.04 GB) + `qwen3vl_32b_minimax_h3_nvfp4_awq` TE (~14.61 GB) + int8_convrot video VAE + fp32 audio VAE. 64 GB RAM. RTX 5070 Ti 16 GB. | `/workspace/cos/research/2026-10-02-10eros-max-hybrid-exhaustive.md` |
| L6 | Oct 5 sharper-quality research: soft = resolution first; Quality complaint included **"plastic skin"**. KEEP beta/25. | `/workspace/cos/research/2026-10-05-max-ref2va-sharper-quality-settings.md` |
| L7 | **NE768 1344×768 · 362f · 25 steps:** interrupted at step 2/25. "**~950–1100 s/it … UNET 0.00 MB resident, 13349 MB offloaded vs morning 864x480/362f 19.4 s/it**". Not a CUDA OOM. | `/workspace/MAX_REF_ORC_BJ_15S_NE768_2026-10-05/SCOREBOARD_A_ORAL_15S_NE768.md` L14, L34 |
| L8 | Today: hot ST8 124f @ 768×1344 ≈ **140.4 s**. Today's cold WARM 124f = 296.1 s. **S1 362f ST8 still running at ≥1,005 s** (08:05 CT), GPU 15.85/16.3 GB at 100%. The Auditor later notes 30+ min. | `/workspace/cos/audits/2026-10-06-max-render-slowdown-vs-fabric-audit.md` · `/workspace/cos/audits/2026-10-06-15s-wall-vs-prior-and-lowvram-fairness-auditor.md` |

### Derived (arithmetic from F10, labeled as derivation, not a measurement)
Video tokens ≈ (W/32)·(H/32)·((frames−1)/4+1): **768×1344×362f ≈ 91.7k** · 864×480×362f ≈ 36.9k · 768×1344×124f ≈ 31.2k · **864×480×124f ≈ 12.6k** (just above the sparse `min_tokens` 12,288). Ref/audio tokens come on top.

---

## Verdicts

| Axis | Verdict | Why (cites) |
|------|---------|-------------|
| **(a) argv / lowvram** | **PARTIAL** | ✅ NODDV is justified: the HostBuffer fail lives in the aimdo path (C3, F7), and the upstream fix PR #15944 is still open. ✅ No fp8 CLI casts (L3). ✅ ck ON was measured −26% (L2) and isn't the int8_convrot crash case (F4). ⚠️ **`--lowvram` rationale is wrong.** Under NODDV it only puts the 32B TE on the CPU (F6, F7). UNET streaming happens without it. Keeping it is a defensible TE-placement choice, but "needed to stream weights" is incorrect. ❌ **`--disable-async-offload` + `--disable-pinned-memory` force synchronous pageable transfers**, the worst case once weights spill (F11, C1, C2). Their necessity is **unproven** because three variables changed at once (L3). |
| **(b) canvas** | **OPTIMIZED (quality)** | 768×1344 = 9:16 at the official 768-short-edge pixel-area cap, multiple of 32 (F1, F10). Matches the Oct 5 canvas split (L1). Speed cost is covered in (d). Preview for this portrait Cond must stay **portrait (480×864)**, as today's errata already says. |
| **(c) steps ST8 vs 20–25** | **PARTIAL** | ✅ **ST8 is inside the author's TURBO band** (T2). Official turbo templates also use 8 for I2V (F2). ⚠️ **Scheduler `beta` at 8 steps is author-flagged "plastic/burned"** (T2). The beta win was measured at **25 steps / 864×480 / 124f** (L2) and never re-tested at ST8. ⚠️ At ST8, official docs say audio speech is weakest and reference adherence is weaker (F2). ❌ **KEEP-25 lane runs a TURBO-baked file at 25 steps.** Official 20–25 assumes base weights with turbo off (F2). Author turbo recipes stop at 9 and say non-turbo is better for audio (T1–T2). A matching non-turbo w4a8 file exists at the same size (T4). |
| **(d) 15s @ 768 portrait wall** | **NOT OPTIMIZED** | Measured spill cliff: UNET 0 MB resident, ~950–1,100 s/it vs 19.4 s/it (L7). S1 is 30+ min vs ~412 s hot-linear (L8). That's ~2.5× tokens over the 480 canvas (derived) pushing the working set past 16 GB. Each step then streams ~13 GB of weights with async and pinned both off (F11). Community 16 GB shows the same ~6× cliff (C1). We already DROPPED the one doc-endorsed long-sequence speedup (sol-attn), but that drop was measured at ~12.6k tokens, where the doc says gains are small (F5, L2). |

---

## Contradictions
1. **Dial/Auditor in-room claim** ("`--lowvram` because TE+UNET > 16 GB, must stream weights", Auditor fairness PASS) **vs official docs + source** (F6, F7): streaming happens without `--lowvram`; with NODDV it only changes TE placement. The flag can stay. The *reason* in the room and in L3 should be corrected.
2. **Fleet `beta` KEEP vs author** (T2: beta gives plastic/burned at 8–9 steps; use `simple`) **and official** (F3: all templates use `simple`). The fleet's beta evidence is a 25-step / 480 / 124f speed delta (L2), not an ST8 768 quality test. The Oct 5 "plastic skin" complaint (L6) lines up with the author's warning. That's a correlation, not proven cause.
3. **Fleet "STEPS-20 under-denoise vs 25" on TURBO-hybrid** (L2) **vs author** (turbo good at 4–9) **and official** (20–25 is for non-turbo). Possible explanations: a Bot-vision scoring artifact, a TURBO+REF interaction, or fair variance. No external source backs "turbo needs 25". Treat KEEP-25 as a local preference, not doc-aligned.
4. **SPARSEsol DROP** (L2, 306 s slower) **vs doc** (F5: gains scale with sequence; short clips gain little). The drop was measured at ~12.6k tokens, about at `min_tokens`. A 362f@768 run is ~91.7k tokens (7.3×), so the DROP doesn't transfer to the 15s lane. Also, 2.4× *slower* is odd for a "falls back to dense" case; a cold kernel/JIT run is possible (NO_DATA).
5. **Author "Use TURBO-hybrid_int8 by default"** (T1) vs our w4a8. Not a defect: int8 is 20.97 GB vs 14.0 GB on a 16 GB card, so w4a8 is the sane 16 GB pick. Just noting it differs from the author default.
6. **Pinned-memory folklore.** Disabling it is the community first-line OOM fix (C2, C3). But the HostBuffer failure class is aimdo/DynVRAM (C3, F7), which NODDV already bypasses. Several reporters fixed it by hiding a second GPU instead (C3).

## Unknowns (NO_DATA — do not invent)
- Whether re-enabling **pinned memory** and/or **async offload** under NODDV (aimdo off, :8188 closed) is stable on AlienPc Windows. Never tested one axis at a time (L3).
- TE encode time on CPU (32B nvfp4-AWQ under `--lowvram`) vs on GPU. CPU has no nvfp4 compute, so it likely dequantizes (C1 notes below-Blackwell expansion; CPU path not measured). This probably contributes to cold-cell walls (L8: cold 296 s vs hot 140 s) but isn't measured.
- Whether AlienPc has an **iGPU / second NVIDIA adapter visible** (C3 trigger). A read-only `nvidia-smi -L` under Dial's lease would answer it. I didn't touch AlienPc.
- `sol-attn` wall/quality at 362f@768 on w4a8 + ck. `simple` vs `beta` at ST8 / 768. Non-turbo hybrid w4a8 at 20–25 steps on our REF2VA graph (not on disk; HAVE list shows TURBO only, L5).
- Final S1 wall (still running). True hot 362f@768 s/it.
- Whether KJNodes `MiniMaxH3MemoryEfficientSageAttentionPatch` (C1, "reduces peak VRAM") would lower the cliff vs ck. Sage-family is on the DROP list anyway.

## Recommend (research ranking · every row = one-axis TRY · KEEP/argv change = Derrick exact GO only · Dial owns lease)
1. **Correct the rationale (no runtime change):** tell the room that under NODDV `--lowvram` = TE-on-CPU only (F6/F7). It isn't what lets the UNET stream. Keep it for now.
2. **Wall cliff (d), highest value:** after S1–S3 finish, one-axis TRY **remove `--disable-pinned-memory` only** (keep NODDV, `--lowvram`, async disabled, :8188 closed) on a 124f warm then 362f@768 cell. Watch for HostBuffer/OOM; revert on first fail. If it's stable, a separate TRY re-enables async offload. Basis: F11, C1, C3, L3, L7.
3. **Re-test `sol-attn` only in its regime:** 362f@768 (doc defaults; optionally start 0.4 / end 0.9). The 124f/480 DROP doesn't transfer (Contradiction 4). Mark it DROP-class revive, so exact GO is required.
4. **ST8 scheduler fair twin:** `simple` vs `beta` at ST8 / 768×1344 / 124f, same Cond and seeds, METHOD label. Target: the author-flagged plastic look (T2) and the Oct 5 complaint (L6).
5. **Quality lane checkpoint match:** if a 20–25-step quality/ID lane is wanted, TRY the **non-turbo `10Eros_Max_h3_hybrid_beta5_w4a8_14gb_optimized`** (14.0 GB, same footprint; needs a download) instead of TURBO at 25 (F2, T1, T4). Better audio per the author.
6. **Speed while those wait:** the already-legal lanes from today's research still stand: portrait preview `480×864` @362f, or 3×124f hops (`/workspace/cos/research/2026-10-06-max-15s-generate-time-reduction.md`).
7. **Do not change:** NODDV (until #15944 lands and ≥2 TECH), no fp8, ck ON, shift 12/3, `ref_image_size=match`, 768×1344 quality canvas, no cache/spectrum on reference (T3).

**One-line for Dial:** Canvas matches docs. NODDV and ck are right. But under NODDV `--lowvram` only moves the TE to the CPU, and the real 15s@768 cost is synchronous unpinned weight streaming at a VRAM spill cliff. The next one-axis TRYs on Derrick GO, after S1–S3: re-enable pinned memory, run sol-attn at 362f, and twin `simple` vs `beta` at ST8.

---

## research-to-fleet-memory (suggestion · not written by me)
**Standing fact candidate** for `04_memory` / `max-8189-production-keep.md` (owner applies after Auditor stamp):
> "Under `--disable-dynamic-vram`, `--lowvram` only moves text encoders to CPU (docs startup-flags + ComfyUI source 2026-10-06). UNET partial-load streaming happens in NORMAL_VRAM too. Async offload + pinned memory are the transfer-speed features (Comfy blog 2026-01-09: 10–50% when spilling). 10Eros author (Civitai 2851079 beta5): TURBO = 4–9 steps; `res_multistep+beta` at 8–9 = 'plastic/burned', `simple` recommended; non-turbo `hybrid_beta5_w4a8` exists for full-step / better audio."

*Research only · 2026-10-06 ~8:25 AM CT · AlienPc untouched · no KEEP / no PASS from executor*
