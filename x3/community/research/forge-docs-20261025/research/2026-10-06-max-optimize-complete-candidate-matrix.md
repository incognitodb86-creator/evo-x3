# RESEARCH: AlienPc :8189 Max REF2VA COMPLETE optimize candidate matrix (2026-10-06 ~8:35 AM CT)

**Owner:** Max Research (cites/verify only) · **Ask:** Derrick via Dial: "verify ALL optimize options that can work on our setup, test everything unless known dead"
**SoT plan (aligned, not forked):** Dial `/workspace/cos/status/ce-plan-alienpc-max-full-verify-matrix-2026-10-06.md`. Wave IDs W0–W13 are Dial's. Research-added rows use **+R#** sub-arms for Dial to slot; they are not new wave numbers.
**Reused stamps:** `2026-10-06-max-8189-keep-vs-official-community-optimize.md` (ERRATA3 `983c9f9d…`) · `2026-10-06-max-keep-vs-official-10eros-community.md` (`f4f2e4b53f17…`) · production-keep `max-8189-production-keep.md`
**Locks:** fiction adults 21+ nomenclature · one axis per cell · KEEP = Derrick exact GO only · Research never PASS/KEEP/0.95 · AlienPc/S1 untouched by this executor

## Plan (≤10 lines · plan-md-quality-bar)
1. Read the ERRATA3 stamp, Dial executor brief, old optimize plan, production-keep, and Dial full-verify plan (SoT).
2. Refresh primaries today (curl 200, 08:30–08:31 CT): Comfy H3 guide · startup flags · R2V node · TenStrip HF README + HF tree · Comfy NVIDIA blog · Tomiigo 16GB README · GitHub #14250 / PR #15944 / #15326.
3. Classify every knob into exactly one of MUST / SHOULD / RISK_OK_ONE_SMOKE / SKIP_KNOWN_DEAD, with a THIS-box cite for every SKIP.
4. Map rows onto Dial W-IDs. Flag SKIPs and adds that Dial missed.
5. Recommend in Dial's serial order with +R inserts. Standing fact. close-out-verify.

## TLDR
- **31 knobs classified: 7 MUST · 12 SHOULD · 5 RISK_OK_ONE_SMOKE · 7 SKIP_KNOWN_DEAD.** Dial's order **0→1→2→(2b)→5→6→3→4→7→8→9** stands.
- **SKIP flags Dial missed or under-classed:**
  - (a) **`--fast-disk` under NODDV**: docs say "disk-backed *dynamic* loading", so it is inert with `--disable-dynamic-vram`. Split W12: reserve-vram = SHOULD, fast-disk = SKIP (evaluate only inside W4).
  - (b) **10Eros TURBO int8-convrot** (author default): ck attention crashes on int8_convrot (#15529), and the file is 20.97 GB on a 16 GB card.
  - (c) **`--highvram` / `--gpu-only`**: TE ~14.6–15.7 GB + UNET ~13–14 GB cannot both be resident in 16 GB.
  - (d) **`--novram` / `--disable-smart-memory`**: both add transfer at a spill cliff.
  - (e) **`--fast fp8_matrix_mult`**: fp8 class.
  - (f) W13 confirmed SKIP. Single 5070 Ti, and an iGPU is not CUDA-enumerated, so hiding devices is a no-op.
- **Adds Dial missed (+R):**
  - +R1 cliff-finder canvas **576×1024**
  - +R2 **LCM/simple 6–8** (author's best turbo audio)
  - +R3 **er_sde/beta57 4–6** (RISK, steps<8 class)
  - +R4 **ST16** on TURBO
  - +R6 **KJ MemoryEfficient Sage patch** (reduces peak VRAM; Tomiigo 16GB)
  - +R7 **sol-attn start 0.4 / end 0.9**
  - +R8 **ref_image_size max** (quality/ID only)
  - +R9 **`--fast fp16_accumulation`** (last)
- **Harness preconditions (METHOD-FAIL traps):**
  - **W2 Sage on Blackwell** needs sageattention ≥2.x built for sm_120. Otherwise it falls back silently and the A/B is void.
  - **W7 sol-attn** needs the comfy-kitchen `sol_attn` kernel. Otherwise every layer is "silently dense".
  - **EasyCache/Spectrum on REF stay RISK, never KEEP-eligible.** TenStrip says "No cache or spectrum if doing reference", and #15326 (EasyCache degrades H3 audio) is open today.

## Facts (cited · fetched 2026-10-06 08:30–08:31 CT, HTTP 200 unless noted)
| # | Fact | Source |
|---|---|---|
| F1 | Native = 768 short edge (~1 MP), 24 fps; 768×1344 = area cap; frames above native don't hold detail; "soft frame is a resolution problem first"; multiples of 32 | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 |
| F2 | Steps: base + Lightning off = 20 default, raise to 25 if ref drifts; turbo LoRA → 8 (T2V/I2V), **4 (Reference to Video)**; "a short schedule costs the most on reference-driven shots… at 4 steps a reference can end up barely applied"; simple content 12–16; audio/voice weakest at 8; turbo/distilled builds surface grid artifacts first | same |
| F3 | Sage ≈ "roughly double" speed, via KJ Patch node or `--use-sage-attention`; INT8 Sage → **morphing near end of clip**; Comfy Kitchen attention (`--use-ck-attention`, ≥0.32) clears it at Sage-like speed; ck only listed when INT8 kernels available | same |
| F4 | Sparse `sol-attn` (≥0.35, experimental): gain grows with sequence length; needs CUDA + comfy-kitchen `sol_attn` kernel, **"without them every layer silently falls back to dense"**; defaults start 0.2 / end 1.0, tau 1.3 (tau 1.0≈16% exact blocks, 1.5≈7%); suggests start ~0.4 / end ~0.9 to keep opening/closing dense; `min_tokens` 12,288; "short clips gain little" | same |
| F5 | Shift 12 / audio 3 comes from model definition; LoRA must match build; turbo LoRAs carry no adaln (load on pruned or full) | same |
| F6 | `--lowvram`: "No effect when dynamic VRAM is enabled. Otherwise, runs text encoders on CPU." `--reserve-vram GB` = VRAM reserved for OS/others; `--fast-disk` = "Prefer disk-backed **dynamic** loading over unpinned RAM"; `--disable-dynamic-vram` = estimate-based loading; async offload default on Nvidia (`--async-offload [NUM_STREAMS]`, default 2); `--novram` = minimal VRAM; `--disable-smart-memory` = aggressively offload; `--gpu-only` = everything incl. TE on GPU; `--fast` opts fp16_accumulation / fp8_matrix_mult / cublas_ops / autotune "may affect quality or stability"; fp8 UNET/TE storage flags exist; `--cuda-device` hides other devices | https://docs.comfy.org/development/comfyui-server/startup-flags |
| F7 | R2V `ref_image_size`: match (default) scales refs down to gen area; **max** = 2048 short edge "for best identity fidelity… can be several times slower"; length trained ~124–362 | https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo |
| F8 | TenStrip: TURBO files = hybrid turbo delta baked in; non-turbo available; "Non-turbo full step audio will always be better"; working: er_sde/beta 4 · er_sde/beta57 4–6 · **res_multistep/simple 6–8 (go-to motion)** · **LCM/simple 6–8 (best turbo audio)** · LCM/beta 4–6 · Euler/simple 4–8; **"No cache or spectrum if doing reference, they cause accuracy loss"**; int8 versions = cicalooo **int8-convrot**; concept LoRAs 0.2–0.6 | https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md |
| F9 | HF tree: TURBO-hybrid and non-turbo `hybrid_beta5_w4a8_14gb_optimized` both present (14.0 GB each) | https://huggingface.co/api/models/TenStrip/10Eros-Max/tree/main |
| F10 | Comfy blog (2026-01-09): NVFP4 + **async offload + pinned memory** on by default for NVIDIA; 10–50% when weights don't fit (cited via f4f2 brief F11; page 200 today, body JS-rendered) | https://blog.comfy.org/p/new-comfyui-optimizations-for-nvidia |
| F11 | Tomiigo (RTX 5070 Ti): `--disable-pinned-memory` ≈ +1/5 runtime (180 s vs 150 s), weights re-read each step; `--reserve-vram 1.5` because desktop on same card ("accounting limit"); **Windows page-locks 40% of RAM vs 90%** (never run on Windows); 16 GB unconstrained REF L243: **1,027 s full-res vs 170 s downscaled**; graph uses KJ `MiniMaxH3MemoryEfficientSageAttentionPatch` ("reducing peak VRAM") + EasyCache; Sage needs v2 built from source, with `TORCH_CUDA_ARCH_LIST=12.0` `_qattn_sm89` doesn't import → KJ fallback | https://github.com/Tomiigo/minimax-h3-16gb (README raw) |
| F12 | #14250 HostBuffer.read_file_slice (aimdo) **OPEN**; PR #15944 "Fix/aimdo windows pin budget" **OPEN**; #15326 "Regression: EasyCache degrades the audio stream on MiniMax H3" **OPEN** (HTML state today) | https://github.com/Comfy-Org/ComfyUI/issues/14250 · https://github.com/Comfy-Org/ComfyUI/pull/15944 · https://github.com/Comfy-Org/ComfyUI/issues/15326 |
| L1 | Fleet: fp8 CLI / DynVRAM peel = DROP (HostBuffer 1450 / kitchen float8); SPARSEsol 306 s FAIL @864×480×124f; beta 125.5 s vs simple 135.4 s @25 steps; Sage skipped | production-keep · `experimental-do-not-default.md` · `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md` |
| L2 | NE768 362f: UNET 0 MB resident / 13,349 MB offloaded, ~950–1,100 s/it vs 19.4 s/it @864×480×362f | f4f2 brief L7 |
| L3 | W13 DONE (Dial): `nvidia-smi -L` = single RTX 5070 Ti | Dial full-verify plan (Research did not run it) |
| D1 | Derived tokens (W/32·H/32·((f−1)/4+1)): 768×1344×362f ≈ 91.7k · 576×1024×362f ≈ 52.4k · 480×864×362f ≈ 36.9k · 768×1344×124f ≈ 31.2k · 480×864×124f ≈ 12.6k (≈ `min_tokens` 12,288). Derivation, not a measurement. | F4 + MiniMax card |

## Contradictions
1. **Dial W12 "fast-disk SHOULD if docs apply"** vs F6: fast-disk is disk-backed *dynamic* loading → inert under NODDV. **SKIP under NODDV.** Pair it only with a W4 DynVRAM arm.
2. **Dial W2 "ck vs Sage"** vs F3/F11: Sage on Blackwell needs sm_120-built v2. A stock pip 1.0.6 install or a missing kernel falls back silently, and that is a METHOD FAIL, not a "Sage loses" result. Also, INT8 Sage artifacts cluster at **clip end**, so TECH words must cover the tail frames.
3. **Author default "TURBO-hybrid_int8"** vs our ck argv: the int8 builds are int8-convrot, and ck crashes on int8_convrot (#15529, F3 page). So int8 cannot pair with KEEP ck → SKIP on THIS setup. w4a8 stays.
4. **W10 EasyCache/Spectrum RISK** vs TenStrip "no cache/spectrum on reference" plus open #15326 audio regression. Research agrees with RISK_OK_ONE_SMOKE because Derrick wants re-tests, but these rows are **never KEEP-eligible on REF2VA without an Integrity label** (Void in Dial plan already).
5. **W7 BASE**: the sol-attn arm must twin S1 exactly (768×1344×362f ST8 ck beta, same seed, METHOD label). Otherwise it fails one-axis.
6. **Harness 480×864×124f ≈ 12.6k tokens** sits at `min_tokens`, which is consistent with keeping SPARSEsol-short SKIP and W7-only-at-362f.

## Unknowns (NO_DATA, do not invent)
- Whether sageattention v2 (sm_120) and the KJ MemEff patch are installed on AlienPc. Check under Dial's lease before W2.
- Whether comfy-kitchen `sol_attn` is available on the AlienPc build (Comfy 0.38 ≥0.35 OK). The prior 306 s SPARSEsol result never proved the kernel was active.
- Windows pinned budget at 40% of 64 GB ≈ 25.6 GB (derived) vs ~13 GB UNET plus TE. W5 stability under NODDV with aimdo off is not measured.
- GPU-TE (W3) time vs CPU-TE for nvfp4-AWQ 32B. VRAM needed for desktop on the same card (reserve-vram size) is not measured.
- Non-turbo hybrid is not on disk (download ~14 GB, Dial lease). Whether TURBO-25 "under-denoise" was a scoring artifact.
- Cliff location between 36.9k and 91.7k tokens (+R1 answers it).
- `--fast fp16_accumulation` effect on the w4a8 path: no H3 data.

## FULL MATRIX TABLE (Dial W-IDs = SoT · +R = Research add for Dial to slot)
| # | ID | Knob | Class | Cite / THIS-box reason | Harness | Gate |
|---|---|---|---|---|---|---|
| 1 | W0 | Canvas 768×1344 (S1) vs **480×864** ×362f | **MUST_TEST** | GO; F1 native cap vs preview; D1 0.40× px | ST8 362f portrait | wall + TECH |
| 2 | W0 | Length 124 vs 362 | **MUST_TEST** (as wall dimension) | F7 trained 124–362; product length cut STRUCK (Derrick lock); 124 = harness only, 362 = W0/W7 | 362f wall rows; 124f fair arms | no product length change |
| 3 | +R1 | Canvas **576×1024** ×362f (cliff-finder, exact 9:16, ×32) | **SHOULD_TEST** | F1 ×32 / AR; L2 cliff; D1 52.4k between 36.9k and 91.7k | ST8 362f vs W0 | only if W0 fast but soft |
| 4 | W1 | Scheduler **simple vs beta** @ST8 | **MUST_TEST** | GO + ERRATA3; F8 go-to simple; author beta@8–9 plastic | 480×864 124f METHOD twin | ≥2 TECH |
| 5 | +R2 | Sampler **LCM/simple 6–8** | **SHOULD_TEST** | F8 "best turbo audio"; unproven here | 480×864 124f vs W1 winner | after W1; audio words |
| 6 | +R3 | Sampler **er_sde/beta57 4–6** (also covers official turbo-REF 4) | **RISK_OK_ONE_SMOKE** | F8 author (least drift); F2 4-step REF "barely applied"; fleet STEPS<8 DROP | 480×864 124f | Derrick named |
| 7 | W8 | Steps **ST8 vs ST12** | **SHOULD_TEST** | F2 audio usable ≥12 | 480×864 124f | TECH audio |
| 8 | +R4 | Steps **ST16** on TURBO | **SHOULD_TEST** | F2 most gain by 16; production-keep "better quality on ask = ST16"; ST16 vs ST25 OPEN | 480×864 124f | after W8 |
| 9 | W9 | **Non-turbo hybrid @20–25** vs TURBO-25 (KEEP-25 OPEN; covers ST20/25) | **SHOULD_TEST** | F2 20–25 = base/turbo-off; F8 non-turbo audio better; F9 file 14 GB | download; 124f then 768 | after speed waves |
| 10 | W2 | Attn **ck vs Sage** | **MUST_TEST** | GO; F3 ≈2×; **precondition** sageattention v2 sm_120 (F11) else void | restart argv; 480×864 124f | check tail morph; revert on NaN |
| 11 | W2b | Attn **stock** (no ck/Sage) | **SHOULD_TEST** | F3 templates ship standard attn | 480×864 124f | if W2 muddy |
| 12 | +R6 | **KJ MemoryEfficient Sage patch** | **SHOULD_TEST** | F11 "reducing peak VRAM" (spill cliff); experimental | sub-arm after W2 Sage clean | one axis vs W2 Sage |
| 13 | W7 | **sol-attn @ 768×1344×362f** | **MUST_TEST** | ERRATA3; F4 gain grows with length; D1 91.7k ≫ 12,288; **precondition** sol_attn kernel log | twin S1 exact seed | exact GO revive |
| 14 | +R7 | sol-attn **start 0.4 / end 0.9** | **SHOULD_TEST** | F4 doc suggestion (dense open/close) | after W7 | one axis vs W7 |
| 15 | SKIP | SPARSEsol @ short 124f/480 | **SKIP_KNOWN_DEAD** (as speed) | F4 short clips gain little; D1 12.6k ≈ min_tokens; L1 306 s measured | — | revive only as W7 |
| 16 | W3 | Drop **`--lowvram` only** (NODDV kept) | **MUST_TEST** | GO HIGH; F6 TE→CPU only; tests GPU-TE | 480×864 124f | OOM → restore argv |
| 17 | W12a | **`--reserve-vram`** (e.g. 1.5) | **SHOULD_TEST** | F6; F11 desktop on same card; L3 single GPU → desktop shares 5070 Ti | separate cell only if W3 OOMs | accounting limit, not speed |
| 18 | W4 | **DynVRAM ON** one smoke | **RISK_OK_ONE_SMOKE** | GO HIGH; F12 #14250 + PR #15944 OPEN; CAPA 1450 | interrupt budget | fail → NODDV restore |
| 19 | W5 | Re-enable **pinned only** | **MUST_TEST** | ERRATA3; F10 10–50%; F11 +1/5 when off; Windows 40% page-lock caveat | 124f then opt. 362f@768 | HostBuffer → revert |
| 20 | W6 | Re-enable **async-offload only** (streams=2 default) | **SHOULD_TEST** | F6 default on; F10 | 480×864 124f | after W5 stable |
| 21 | W12b | **`--fast-disk`** under NODDV | **SKIP_KNOWN_DEAD** | F6 "disk-backed **dynamic** loading"; NODDV = estimate-based → inert on THIS argv | — | only inside a W4 arm |
| 22 | W13 | 2nd-GPU/iGPU HostBuffer hide theory | **SKIP_KNOWN_DEAD** | L3 single 5070 Ti; iGPU not CUDA-enumerated → `--cuda-device`/CUDA_VISIBLE_DEVICES no-op; NODDV already skips aimdo | — | DONE |
| 23 | SKIP | fp8 CLI casts (`--fp8_*-unet/-text-enc`, `--fast fp8_matrix_mult`) | **SKIP_KNOWN_DEAD** | L1 measured HostBuffer 1450 / kitchen float8 on this box; weights already w4a8 / nvfp4 | — | measured |
| 24 | +R9 | **`--fast fp16_accumulation`** | **SHOULD_TEST** (last) | F6 docs-listed experimental "may affect quality"; NO_DATA on H3/w4a8 | 480×864 124f | Integrity label |
| 25 | +R10 | `--highvram` / `--gpu-only` | **SKIP_KNOWN_DEAD** | F6 gpu-only keeps TE on GPU; TE ~14.6–15.7 GB + UNET ~13–14 GB > 16 GB on THIS card | — | — |
| 26 | +R11 | `--novram` / `--disable-smart-memory` | **SKIP_KNOWN_DEAD** (as speed) | F6 minimal VRAM / aggressive offload → more transfer at L2 cliff | — | — |
| 27 | +R14 | 10Eros **TURBO int8-convrot** (author default) | **SKIP_KNOWN_DEAD** | F8 int8 = convrot; F3/#15529 ck crashes on int8_convrot; 20.97 GB > 16 GB | — | w4a8 stays |
| 28 | W10a | **EasyCache on REF** | **RISK_OK_ONE_SMOKE** | F8 TenStrip no cache on REF; F12 #15326 OPEN audio regression | 124f | Derrick named · Integrity · never KEEP |
| 29 | W10b | **Spectrum on REF** | **RISK_OK_ONE_SMOKE** | F8 TenStrip no spectrum on REF | 124f | Derrick named · Integrity |
| 30 | W11 | **Turbo LoRA stack** on TURBO-hybrid | **RISK_OK_ONE_SMOKE** | F8 delta already baked (double-turbo); F5 loads; fleet Turbo DROP | 124f | GO |
| 31 | +R8 | **ref_image_size max** vs match | **SHOULD_TEST** (quality/ID only) | F7 "best identity fidelity… several times slower" | 480×864 124f; never speed lane | after W9 |

**Counts:** MUST 7 · SHOULD 12 · RISK_OK_ONE_SMOKE 5 · SKIP_KNOWN_DEAD 7 (total 31).
**Held constants (not candidates):** shift 12/3 (F5 model-def) · `res_multistep` except +R2/+R3 · `ref_image_size=match` except +R8 · w4a8 TURBO except W9 · Cond portrait AR.

## Recommend (ranked · Dial serial order SoT + Research inserts)
1. **W0 → W1 (+R2 after W1)**: cheapest, LOW risk. Simple vs beta at ST8 targets the plastic flag. +R1 576×1024 only if W0 is fast but soft.
2. **W2 (precondition: sageattention v2 sm_120 verified) → W2b → +R6**: void the arm if the Sage kernel falls back. TECH must cover tail frames.
3. **W5 pinned → W6 async**: highest expected wall win at the spill cliff (F10/F11). Revert on the first HostBuffer.
4. **W3 drop lowvram** (W12a reserve-vram retry only if OOM) **→ W4 DynVRAM one smoke**. Restore production argv after each.
5. **W7 sol-attn @362f×768 twin of S1** (precondition: kernel active) **→ +R7 0.4/0.9 → W8 ST12 → +R4 ST16 → W9 non-turbo → +R8 ref max**.

RISK rows (+R3, W10a/b, W11) run only when Derrick names them, with an Integrity label. +R9 runs last. SKIP rows stay out of the matrix.

## research-to-fleet-memory: Standing fact
> **Standing fact (2026-10-06):** On AlienPc :8189 Max (single RTX 5070 Ti 16 GB, NODDV), `--fast-disk` is inert (docs: dynamic loading only), 10Eros int8-convrot cannot pair with KEEP ck attention (#15529), `--gpu-only/--highvram` cannot fit TE+UNET in 16 GB, and the 2nd-GPU HostBuffer hide fix is a no-op (single CUDA device). Sage A/B is valid only with sageattention v2 built for sm_120. sol-attn A/B is valid only at long sequences (≫12,288 tokens, e.g. 362f@768) with the comfy-kitchen sol_attn kernel active. EasyCache/Spectrum on REF2VA are never KEEP-eligible (TenStrip + open #15326).
Owner applies after Auditor stamp; Research does not write 04_memory.

## close-out-verify
| Gate | Status |
|---|---|
| 1 Outcome | 31-knob matrix, 4 classes, aligned to Dial W-IDs, +R adds and SKIP flags |
| 2 Evidence | 9 primaries curl 200 today 08:30–08:31 CT (Comfy H3 · flags · R2V · TenStrip README · HF tree · Comfy blog · Tomiigo · #14250 · PR #15944 · #15326) + fleet priors |
| 3 Status | This stamp + thin align note `/workspace/cos/status/ce-plan-alienpc-max-optimize-complete-matrix-2026-10-06.md`; no room post (parent delivers) |
| 4 Memory | Standing fact above (suggestion; owner applies) |
| 5 Blockers | S1 finish; Sage/sol_attn install checks under Dial lease; non-turbo download |
| 6 Retest | Re-stamp after W0/W2/W5/W7 land with walls |
| 7 LEARNED | Silent-fallback knobs (Sage, sol-attn) need a kernel-active precondition, or the A/B is METHOD FAIL. Dynamic-only flags (fast-disk, lowvram-under-DynVRAM) must be classified against NODDV. |

## Verify
- [x] Plan ≤10 · TLDR · Facts cited · Contradictions · Unknowns · FULL MATRIX · Recommend · close-out-verify
- [x] Every SKIP has a THIS-box reason (single GPU, NODDV, ck, 16 GB, measured fp8)
- [x] All minimum knobs covered (canvas · length · sched · attn ck/Sage/stock · lowvram · DynVRAM · pinned · async · sol-attn@362f · non-turbo · EasyCache · Spectrum · turbo LoRA · steps 8/12/16/20/25 · 2nd GPU · fast-disk · reserve-vram · fp8 · SPARSEsol short/long · ref_image_size)
- [x] Dial wave numbers not forked; +R are sub-arms
- [x] No PASS/KEEP/0.95; AlienPc/S1 untouched; no room/Dial message
