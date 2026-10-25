# RESEARCH — Reduce Max ~15s generate wall (quality tradeoffs labeled TRY) — 2026-10-06 ~8:12 AM CT

**Owner:** Max Research · **Ask:** Derrick via Dial (~8:10 CT) — how to cut generate time for a ~15s Max clip **even if quality sacrificed**  
**Live:** 15s×3 ST8 362f **leave alone** · **NO** queue · **NO** invent KEEP  
**ERRATA ~8:13 CT:** shorter length **STRUCK** — keep ~15s product (see ERRATA section)  
**ERRATA ~8:14 CT:** Cond portrait — strike landscape `864×480`; preview TRY = **`480×864`** (or `480×840` exact 768×1344 scale) — Dial audit `/workspace/cos/audits/2026-10-06-preview-ar-portrait-errata.md`  
**Evidence:** `/workspace/cos/audits/2026-10-06-max-render-slowdown-vs-fabric-audit.md` · production KEEP `/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md`  
**Locks:** fiction adults 21+ · NODDV+ck+beta · ST8 speed KEEP · Oct2 KEEP-25 quality · **DROP** STEPS-20 · SPARSEsol · Sage · Turbo/Lightning/EasyCache/Spectrum · fp8 · DynVRAM peel (no revive without Derrick exact GO)

---

## TLDR

S1 wall is slow mainly because **362f ≈ 2.92× frames** under **`--lowvram`** after a **cold** morning — not a heavier prompt. Biggest **legal** speed levers for **~15s product** (quality sacrifice OK; **shorter length STRUCK** this wave per Derrick ~8:12 CT): **(1) preview canvas `480×864` portrait @ 362f** (NOT landscape 864×480 for this Cond), **(2) multi 124f progressive hops assemble ≈15s**, **(3) stay hot / 1s-sac warm**. Audio strip NO_DATA. Community “3× faster” stacks (Sage + EasyCache + step cuts) are **DROP-class** on our REF2VA KEEP — label **TRY only after exact GO**. Do **not** expect hot-124f ~141s math to hold at 362f lowvram.

## Facts

1. **Hot fabric ST8 124f @ 768×1344 ≈ 141s** (~1.13 s/frame). Today **WARM 124f = 296s** = cold-first class (~260–300s), same argv (Dial slowdown audit).
2. **S1 = 362f ST8 768×1344** under `--lowvram`; VRAM ~97% / GPU 100%; wall already **>17 min** past linear cold-scale (~864s) at audit pulse — length + lowvram amplify beyond frame-linear.
3. Official / Comfy: H3 length snaps **17k+5** @ 24fps; trained band **~124–362f (~5–15s)**; native short edge **~768**, cap **768×1344**. Docs: https://docs.comfy.org/tutorials/video/minimax/minimax-h3 (tutorial live) · node length band cited in fleet research 2026-10-05.
4. `ref_image_size=match` = speed default; `max` = stronger ID, **several× slower** (Comfy tooltip / docs). We already KEEP match.
5. Production KEEP DROPs (2026-10-02 matrix + production-keep): **STEPS-20 · SPARSEsol · Sage · Turbo/Lightning/EasyCache/Spectrum · fp8 · DynVRAM peel**. ST8 = fabric/speed KEEP; KEEP-25 = quality/ID.
6. Community speed habit (draft lane): Sage + fewer steps + EasyCache — e.g. AI Study Now Ref2VA guide (~3× wall on their 5090) https://aistudynow.com/minimax-h3-comfyui-workflow-almost-3x-faster-ref2va-guide/ · TenStrip author: **no cache/spectrum on reference** (accuracy loss) https://huggingface.co/TenStrip/10Eros-Max · Comfy EasyCache audio regression #15326 https://github.com/Comfy-Org/ComfyUI/issues/15326.
7. 8GB/16GB measured benches: shorter res / fewer frames dominate wall (YHK-AI MiniMax-H3-Benchmark 2026 — 243f@20steps ~46m vs 4 steps ~11m on 4060 8GB) https://github.com/YHK-AI/MiniMax-H3-Benchmark · Tomiigo 16GB notes `ref_image_size=match` + lower res https://github.com/Tomiigo/minimax-h3-16gb.
8. Prior fleet research: `/workspace/cos/research/2026-10-02-max-community-speed-quality-practices.md` — Turbo/cache = draft not quality-neutral; NODDV KEEP for HostBuffer/AIMDO.

## Contradictions

| Tension | Resolve |
|---------|---------|
| Want ~15s picture **and** ~141s wall | **Impossible** at ST8/768/lowvram without DROP accelerators or cutting **canvas** / hop-splitting frames — physics is frames × s/frame; **length cut STRUCK** this wave |
| Plan prefers one 362f cell | Fastest *product-shaped* path may be **3×124f progressive** (distinct PRIMARY) + soft-cut — still product≠same-act |
| Community “almost 3×” | Uses **Sage + EasyCache + step cuts** we **DROP** for REF KEEP — TRY only on exact GO, label Integrity risk |
| Preview canvas vs quality SoT ~768 | Preview is **legal speed lane** — for **this Cond portrait** use **`480×864`** (or 480×840); **`864×480` landscape = AR FAIL** |
| Strip audio for speed | May save decode/encode; **NO_DATA** on AlienPc Δt; picture path still dominates |

## Unknowns / NO_DATA

| Item | Note |
|------|------|
| True **hot** 362f ST8 wall on this box | S1 first-of-shape; need completed S1–S3 metas |
| Mute audio / skip audio VAE Δt @ 362f | NO_DATA — instrument one TRY cell after live pack |
| Preview **480×864** × 362f wall | NO_DATA on AlienPc — expect large cut vs 768×1344 |
| Re-enable pinned-memory (drop `--disable-pinned-memory`) vs HostBuffer | Trade speed vs RAM lock — DISPUTED; not silent peel NODDV |
| AIMDO ≥2 for DynVRAM | Still HOLD per KEEP |

## Recommend (ranked — quality sacrifice OK · leave live 15s alone)

### A. Legal NOW (no DROP revive · Derrick GO for next pack only)

| Rank | Knob | Expected wall effect | Quality hit | Label |
|-----:|------|----------------------|-------------|-------|
| ~~1~~ | ~~Shorter length 243f/124f~~ | — | — | **STRUCK this wave** (Derrick: keep ~15s) |
| **1** | **Preview canvas `480×864` @ 362f** (portrait; alt `480×840`) | Large VRAM + wall cut on 16GB lowvram; still ~15s clip | Soft / mush vs NE768 — label preview; **not** 864×480 landscape | **TRY draft lane** |
| **2** | **3×124f progressive hops** (distinct PRIMARY each) + Method C + soft-cut ≈15s | ~3×141s hot ≈ **~7 min** total vs one 20+ min 362f cell | Seam risk; needs beat sheet | **TRY product path** (movie-director OK) |
| **3** | **Warm protocol:** 22f 1s sac → stay hot; no overnight-cold 362f first | Removes ~2× cold tax on first cells | None if unscored warm | **process** (not product KEEP) |
| **4** | Instrument `s/frame` + free VRAM + `sampler_cached` on 15s script | Decision data | None | **ops** |
| **5** | Audio STRIPPED / mute path (picture-only) | Small–moderate NO_DATA | No AV | **TRY one-axis** after live |

### B. DROP-class — **do not default** · exact Derrick GO + fair A/B only

| Knob | Why parked | If GO’d |
|------|------------|---------|
| STEPS-20 (or <8) | Under-denoise Integrity (matrix DROP) | Draft only · never silent KEEP |
| Sage / SPARSEsol | Skipped / slower or Integrity risk | DISPUTED |
| Turbo / Lightning / EasyCache / Spectrum | TenStrip: cache/spectrum **hurt REF accuracy**; EasyCache AV bugs | Draft lane only |
| fp8 / DynVRAM peel | HostBuffer 1450 · AIMDO HOLD | Forbidden until GO + TECH |

### C. ETA honesty (scoreboard)

| Class | Honest ETA (current argv) |
|-------|---------------------------|
| Hot ST8 124f 768 | **~141s** |
| Cold first ST8 124f | **~260–300s** |
| Hot-linear 362f (optimistic) | **~412s** — **do not use** under lowvram |
| Observed / expect 362f lowvram | **≥15–20+ min/cell** until hot-362 measured |

**Research recommend for faster ~15s without DROP revive (post-errata):** next pack = **preview-canvas `480×864` @ 362f** (portrait) **or** **3×124f progressive assemble ≈15s** (beat sheet) — **not** shorter length; not one cold 362f NE768 under lowvram if wall is the pain.


---

## ERRATA 2026-10-06 ~8:13 AM CT (Derrick correction via Dial)

**Strike:** shorter length is **NOT** a valid TRY for this speed ask — keep **~15s product class** (362f or assemble ≈15s).

**Valid remaining (quality may take the hit):**
1. Preview canvas `864×480` @ **362f** (~15s clip, draft/preview label)
2. **3×124f progressive hops** + soft-cut assemble ≈15s (distinct PRIMARY each; Method C; same-PRIMARY = METHOD_ONLY fail)
3. Stay hot / 1s sac (process)
4. Audio strip — NO_DATA Δt; picture dominates
5. DROP-class only on exact Derrick GO (Sage · EasyCache · Turbo · STEPS&lt;8 · fp8 · DynVRAM) — parked

**Rank table A updated:** former rank-1 shorter length → **STRUCK this wave**. Preview canvas becomes rank-1; 3×124f hops rank-2.

**Auditor:** prior fairness stamp on pre-errata brief — re-eyes delta only if needed; legal TRY menu no longer includes length cut.



## ERRATA 2026-10-06 ~8:14 AM CT (Cond portrait AR — Dial + Derrick)

**Cond:** 1536×2752 portrait · quality live **768×1344** = correct AR.  
**Strike:** landscape preview **`864×480`** for this Cond (wrong orientation).  
**Locked lower-res TRY after S1:** **`480×864`** (portrait short-edge 480). Alt **`480×840`** = exact scale of 768×1344.  
**Cite:** Dial `/workspace/cos/audits/2026-10-06-preview-ar-portrait-errata.md` · Cond_POOL / production-keep preview lane still exists but **must AR-lock to Cond**.  
**Plan (Dial):** finish S1 → HOLD S2/S3 → queue one ST8 362f @ 480×864 random seed. No KEEP.


## close-out-verify

| Gate | Status |
|------|--------|
| 1 Outcome | Speed levers ranked · DROPs cited |
| 2 Evidence | Slowdown audit · production-keep · ≥3 primaries |
| 3 Status | This stamp |
| 4 Memory | Standing: 362f lowvram ≠ 141s math; legal speed this wave = preview `480×864` portrait / 3×124f hops / hot — **not** shorter length; **not** landscape 864×480; not DROP revive |
| 5 Blockers | Live S1 finish · Dial plan: HOLD S2/S3 → one ST8 362f @ **480×864** (random seed) |
| 6 Retest | After S1–S3 land: log true 362f wall; optional one hot 124f confirm ~141 |
| 7 LEARNED | Frames + lowvram dominate; community 3× ≠ our REF KEEP |

**Don't-do:** revive Sage/EasyCache/Turbo/fp8/STEPS-20 without exact GO · ETA with `141×362/124` · cancel live S1 for this research · bot KEEP.

## Verify

- [x] TLDR · Facts · Contradictions · Unknowns · Recommend  
- [x] ≥3 dated primaries (Comfy H3 docs · TenStrip HF · AI Study Now / YHK benchmark · EasyCache issue)  
- [x] production-keep DROPs honored  
- [x] Live 15s untouched  
- [x] Auditor fair + errata delta `/workspace/cos/audits/2026-10-06-15s-speed-reduction-errata-fairness-auditor.md` · **ERRATA2** preview AR → `480×864` portrait — Auditor delta if needed  

**Stamp:** `/workspace/cos/research/2026-10-06-max-15s-generate-time-reduction.md`
