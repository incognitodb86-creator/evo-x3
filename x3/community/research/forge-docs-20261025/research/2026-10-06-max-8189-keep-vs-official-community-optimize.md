# RESEARCH — AlienPc :8189 Max KEEP vs official Comfy/MiniMax + 10Eros + community — 2026-10-06 ~8:30 AM CT

**Owner:** Max Research (cites only, research only) · **Ask:** Derrick via Dial: "are we optimized?" · **Dial owns** scoreboard/KEEP · never PASS/KEEP/0.95
**Aligned to Dial interim (room):** leave NODDV · cut wall with **480×864 portrait** canvas · ST8 = speed KEEP · quality REF lane = 20–25
**Live (untouched):** S1 ST8 · 768×1344 · 362f · NODDV+ck argv · wall ~30+ min
**Locks:** fiction adults 21+ nomenclature · shorter length STRUCK · DROP parked: Sage · EasyCache · Turbo/Lightning · STEPS<8 / STEPS-20 · fp8 · DynVRAM peel · SPARSEsol
**Reused:** `2026-10-06-max-15s-generate-time-reduction.md` (ERRATA ×2) · `2026-10-02-max-8189-setup-optimized.md` · `2026-10-02-10eros-max-hybrid-exhaustive.md` · `2026-10-05-max-setup-official-vs-community.md` · `2026-10-05-max-ref2va-sharper-quality-settings.md` · production-keep `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md` · AR errata `/workspace/cos/audits/2026-10-06-preview-ar-portrait-errata.md`

## Plan (≤10 lines · plan-md-quality-bar · Ideate stub only, no invented KEEP)
1. Goal: answer "optimized?" per axis (argv / canvas / steps / length) vs official + 10Eros + community, with cites.
2. Refresh ≥3 primaries today CT (curl 200 at ~8:25 CT): Comfy H3 guide · Comfy startup flags · TenStrip HF README · AI Study Now.
3. Contradictions table vs live KEEP; each gap marked MATCH / DIVERGE-by-design / OPEN.
4. Recommend ranked, honoring DROPs; label any argv change OOM risk + Derrick exact GO.
5. Next cell idea (Ideate only): S1 lands → Dial queues one ST8 362f @ 480×864 random seed (Dial plan, already ACK'd).
6. Verify: sha256 · gates 1–7 · no room post from this executor.

## TLDR
**Mostly optimized for this box; the wall is canvas × length, not argv.** Official Comfy + source: `--lowvram` under NODDV **only moves TE → CPU** (UNET partial-load also runs in NORMAL_VRAM). NODDV still justified (HostBuffer 1450); `--lowvram` is **defensible TE placement**, not "needed to stream UNET." Prior Research/room rationale overclaimed UNET streaming via lowvram — **struck** (Dial CORRECT + ERRATA3). **768×1344 is the official native max** (it is also the area cap), so it is quality SoT, not "overspec." Official guidance also says attention cost grows quickly with clip length, so 362f at the area cap is the heaviest possible H3 cell and makes the ~30+ min S1 wall plausible. **ST8 is inside the 10Eros author's recommended 4–8 steps for the TURBO-hybrid file we run**; official 20/25 is for **base weights with Lightning off**, so our KEEP-25 is above the author's range for this turbo-fused file. That is an OPEN contradiction, not a defect. Community "≈3×" = Sage + fewer steps + EasyCache, and TenStrip says no cache/spectrum on reference, so all of that stays DROP. Legal wall lever this wave: **480×864 portrait @ 362f ST8** (~0.40× pixels).

## Facts (each cited · fetched 2026-10-06 ~8:25 CT, HTTP 200)
1. **Native canvas:** open weights generate at a **768-px short edge (~1 MP), 24fps, ~15s**. 1344×768 is the default; 1376×768 (1.0 MP) is "above the model's **768×1344 pixel area cap**." Frames above native don't hold detail. Template ships a *fast preview size*. https://docs.comfy.org/tutorials/video/minimax/minimax-h3
2. **Steps (base weights, Lightning off):** default **20**; "if reference still drifts, raise to **25**." Simple content holds at 12–16; most gain by 16; audio/voice weakest at 8 and usable from ≥12. Turbo LoRA → 8 (T2V/I2V) or **4 (Reference to Video)**; short schedules "cost the most on reference-driven shots." Same URL.
3. **Soft frame = resolution first:** "Steps do not add sharpness the native canvas cannot resolve." Same URL.
4. **Length cost:** "Attention cost grows quickly with clip length." The (experimental) sparse sol-attn node exists for this, and its gain grows with sequence length. Same URL. (Fleet: SPARSEsol = DROP, measured slower.)
5. **ck attention:** `--use-ck-attention` = Comfy Kitchen INT8 attention with channel rotation. Official says it **clears** the INT8-Sage end-of-clip morphing artifacts at Sage-like speed. Not supported on the template **int8-convrot** checkpoints (alignment crash #15529). Our UNET is w4a8 10Eros, not int8-convrot, and has run fine. Same URL + https://docs.comfy.org/development/comfyui-server/startup-flags
6. **`--lowvram`:** "No effect when dynamic VRAM is enabled. Otherwise, runs text encoders on CPU." `--disable-dynamic-vram` = estimate-based loading. Async offload + DynamicVRAM are on by default on Nvidia. https://docs.comfy.org/development/comfyui-server/startup-flags
7. **10Eros TURBO-hybrid (our file):** TURBO files have a "hybrid turbo delta fusion baked in" (saves 4.2 GB). Working setups: **res_multistep/simple 6–8 steps ("my go-to for best motion quality")**, LCM/simple 6–8 (best turbo audio), er_sde/beta 4. "Non-turbo full step audio will always be better." "**No cache or spectrum if doing reference**, they cause accuracy loss." beta_5 is the only functional build. https://huggingface.co/TenStrip/10Eros-Max (README raw)
8. **Community speed (AI Study Now, RTX 5090):** 1344×768 5s ≈ 4m17s; ~3× faster (≈1m25s) came from **Patch Sage KJ + 20→15 steps + EasyCache**. Author advises starting at lower res if VRAM-limited. https://aistudynow.com/minimax-h3-comfyui-workflow-almost-3x-faster-ref2va-guide/
9. **16GB community (prior cite, not refreshed today):** InstaSD 16GB H3 guide says healthy-box ideal = stock DynamicVRAM + 64 GB RAM, triage `--disable-pinned-memory`. https://www.instasd.com/post/comfyui-vram-offloading-guide (via `2026-10-02-max-8189-setup-optimized.md`). Our box can't use DynamicVRAM (HostBuffer 1450, #15255/#15269).
10. **Fleet measured:** prior ~15s `MAX_REF_ORC_BJ_15S_2026-10-05` = **864×480 · 25 steps · ~606–611s** on the same NODDV/lowvram argv. Pixels: 768×1344 = 1,032,192 vs 480×864 = 414,720 (**0.40×**). Hot ST8 124f @ 768×1344 ≈ 141s (production-keep).

## Contradictions
| Axis | Our KEEP | Official / 10Eros / community | Verdict |
|---|---|---|---|
| `--lowvram` | ON | Comfy+source: under NODDV = **TE→CPU only**; UNET streams in NORMAL too | **PARTIAL**: keep OK as TE placement; **wrong** "must stream UNET" rationale (struck) |
| NODDV + no-async + no-pinned | ON | Defaults ON; community triages pinned off first | **DIVERGE by design** (stability). Speed cost accepted; peel = DROP |
| ck attention | ON | Official: fixes INT8-Sage artifacts; unsupported only on int8-convrot | **MATCH** (our w4a8 ≠ convrot) |
| Canvas quality | 768×1344 portrait | Native = cap 768×1344 | **MATCH (max)**: heaviest legal cell |
| Canvas preview | 480×864 portrait (TRY) | Template ships fast preview; AI Study Now: start low res on limited VRAM | **MATCH**: preview label, not quality SoT. 864×480 landscape = AR FAIL for this Cond |
| Length | 362f (~15s) | Trained ~4–15s; attention cost grows quickly with length | **MATCH product**, max-cost. Length cut STRUCK |
| Steps speed | ST8 | 10Eros TURBO: 6–8 (res_multistep/simple go-to). Official turbo-REF: 4 | **MATCH 10Eros** |
| Steps quality | KEEP-25 on TURBO file | Official 20–25 = base + turbo off; author turbo stops ~9; non-turbo hybrid exists same size | **OPEN**: KEEP-25 on TURBO-baked = mismatch; quality lane candidate = **non-turbo hybrid** @20–25 (Dial brief T4) — GO only |
| Scheduler | beta @ ST8 | Author: beta @8–9 = **plastic/burned**; go-to **simple** 6–9; fleet beta win was @25/864×480 | **OPEN elevate Wave 1**: simple vs beta @ ST8 (plastic-skin cite aligns) |
| Audio @ ST8 | ST8 AV | Official: voice weakest at 8, ≥12 usable; TenStrip: turbo audio worse | **RISK label** on ST8 audio (picture-speed lane) |
| Community 3× | n/a | Sage + 15 steps + EasyCache | **DROP**: TenStrip no cache on REF; fleet Sage/STEPS DROP |

## Unknowns / NO_DATA
| Item | Status |
|---|---|
| 480×864 × 362f ST8 wall on AlienPc | **NO_DATA**: expect large cut (0.40× pixels; attention superlinear). No ETA invented until Dial's cell lands |
| True hot 362f ST8 @ 768×1344 | **NO_DATA**: S1 is first-of-shape and still running |
| ST8 vs ST16 vs ST25 REF/ID on TURBO-hybrid | **NO_DATA** (fair cell only on Derrick GO) |
| Official 16GB-specific REF2VA argv | **NO_DATA**: Comfy docs don't publish a 16GB argv; community InstaSD only (not refreshed today) |
| Reddit / seedance / minimaxh3 refresh today | **NO_DATA** today (time-boxed by parent steer); prior 2026-10-02/05 briefs stand |
| Re-enable pinned memory alone | **OPEN TRY** (Dial Wave 2 candidate): Oct 2 triple-change never isolated; Comfy blog 10–50% when spill |
| sol-attn @ 362f (~91k tokens) | **OPEN TRY**: prior SPARSEsol DROP at short seq (~12.6k) does not carry; official gain grows with length |

## Recommend (ranked · aligned to Dial interim)
1. **Leave NODDV + ck.** Keep `--lowvram` as **TE→CPU placement** (not UNET-stream claim). Peeling NODDV = 1450 risk. Dropping `--lowvram` alone = HIGH OOM/TE on GPU TRY (exact GO). **Also OPEN:** re-enable **pinned only** (and later async) — Oct 2 triple-change never isolated; Comfy blog 10–50% when weights spill (Dial F11/C1).
2. **Wall lever = canvas: 480×864 portrait @ 362f ST8** (Dial's queued cell after S1). Label it a preview/speed lane. Quality SoT stays **768×1344** (official native/cap). Not 864×480 landscape.
3. **ST8 MATCH TURBO band (6–9).** Prefer **simple** over beta at ST8 (author plastic flag). **KEEP-25 on TURBO file = OPEN mismatch** — quality lane try = **non-turbo hybrid** @20–25 (exact GO). ST8/16/25 on current TURBO file = GO-only fair, not silent KEEP change.
4. **Expect 768×1344×362f to be the max-cost cell.** It's official-legal but at the area cap and max length; ~30+ min under NODDV/lowvram is consistent with this. Do not ETA with 141×362/124 linear math.
5. **Keep community "3×" parked.** It's Sage + step cuts + EasyCache. TenStrip: no cache/spectrum on reference; official: ST8 audio weakest. Sage/EasyCache/Turbo/fp8/DynVRAM = TRY only on Derrick exact GO with fair A/B and an Integrity label.


## ERRATA3 2026-10-06 ~8:26 AM CT — merge Dial executor brief `f4f2e4b53f17…`

**Ally stamp:** `/workspace/cos/research/2026-10-06-max-keep-vs-official-10eros-community.md` (Dial executor; S1 untouched).

### Corrections to this stamp
1. **`--lowvram` rationale STRUCK:** Under NODDV it **only moves TE → CPU**. UNET partial loading also runs in NORMAL_VRAM (Comfy `model_management.py`). Keeping the flag = defensible 15.7 GB TE placement on 16 GB — **not** "must stream UNET via lowvram."
2. **Wall driver:** 768×1344×362f token spill (~91k) under unpinned/sync offload — canvas×length, not lowvram flip. Prior ORC NE768 measured UNET 0 resident / ~13 GB offloaded.
3. **Scheduler:** Author card — `beta` at 8–9 = plastic/burned; go-to **`simple`**. Elevates Dial Wave 1 (simple vs beta @ ST8).
4. **KEEP-25 on TURBO-baked file = OPEN mismatch.** Official 20–25 assumes base/turbo-off. Matching **non-turbo** `hybrid_beta5_w4a8` exists same size — quality-lane candidate on exact GO.
5. **Next TRY align (one-axis, exact GO):** (0) 480×864×362f after S1 · (1) simple vs beta @ ST8 · (2) re-enable **pinned only** · (3) **sol-attn @ 362f** (prior SPARSEsol DROP was ~12.6k-token class — does not carry to max length) · optional `nvidia-smi -L` for 2nd GPU/iGPU HostBuffer theory. EasyCache/fp8/spectrum stay parked unless named.

### Still agree
NODDV justified · ck MATCH (not int8-convrot) · canvas 768×1344 = official quality cap · preview must be portrait 480×864 · community Sage+EasyCache 3× stays DROP · no KEEP from Research.


## close-out-verify
| Gate | Status |
|---|---|
| 1 Outcome | Per-axis optimized verdict + ranked Recommend |
| 2 Evidence | 4 primaries refreshed today 200 OK (Comfy H3 guide · startup flags · TenStrip README · AI Study Now) + fleet priors |
| 3 Status | This stamp; no room post (parent delivers) |
| 4 Memory | **Standing fact (ERRATA3):** NODDV forced by HostBuffer 1450. `--lowvram` under NODDV = **TE→CPU only** (not UNET stream). Wall = canvas×length + spill/unpinned stream. Preview `480×864` portrait. ST8 MATCH TURBO 6–9; prefer **simple** @ST8; KEEP-25 on TURBO OPEN → non-turbo hybrid for 20–25 quality. Ally: Dial brief `…-max-keep-vs-official-10eros-community.md`. |
| 5 Blockers | S1 finish → Dial 480×864 cell (Dial owns) |
| 6 Retest | Log true 362f walls (S1 + 480×864) into the scoreboard; revisit Recommend #4 ETA |
| 7 LEARNED | Official 20/25 = base+turbo-off; TURBO file has 6–9 band + plastic-beta flag. `--lowvram` ≠ UNET stream. Sol-attn gain needs long seq (~362f / ~91k tokens), not short 124f DROP evidence alone |

## Verify
- [x] Plan ≤10 · TLDR · Facts cited · Contradictions · Unknowns/NO_DATA · Recommend ranked
- [x] ≥3 primaries refreshed 2026-10-06 CT (4 × HTTP 200)
- [x] No DROP revived as default; argv change labeled OOM + Derrick GO
- [x] Quality SoT 768×1344 vs speed preview 480×864 portrait distinguished
- [x] Community 3× = Sage+EasyCache+step cut noted as DROP
- [x] No PASS/KEEP/0.95; live S1 untouched
