# Research — Community speed×quality practices: MiniMax-H3 / 10Eros-Max / Comfy Max

**When_CT:** 2026-10-02 ~10:25 CT (America/Chicago)  
**Owner:** executor research ONLY  
**Scope:** What the **community** (and official Comfy/MiniMax tips) actually do for speed without quality loss — not our AlienPc scoreboard.  
**Action:** **NO Dial ping** · no queue · no argv change  
**Matrix policy (Derrick):** **Do not smoke KNOWN_FAIL.** Smoke **DISPUTED** as fair one-axis A/B. Treat **CONSENSUS_DEFAULT** as freeze/start, not as proven KEEP on our box.

**Tags (this file):**

| Tag | Meaning for our matrix |
|-----|------------------------|
| **CONSENSUS_DEFAULT** | Broad agreement / official template default — freeze as start; not a quality crown |
| **DISPUTED** | Real speed claims, split quality reports — **fair one-axis A/B** |
| **KNOWN_FAIL** | Repeated community + author +/or official warnings of quality/accuracy/stability loss for our use (REF2VA finals / AV) — **SKIP smoke** |
| **OFFICIAL_TIP** | Comfy docs / Comfy-Org / model README (not Reddit habit alone) |
| **COMMUNITY_HABIT** | Reddit / Medium / pack READMEs / field guides |
| **UNPROVEN_HYPE** | Headline × without careful same-seed quality gate |

---

## Headline (6 bullets for parent)

1. **Consensus stack for “best quality” finals:** base (or hybrid non-turbo) weights · **Lightning/Turbo OFF** · **~20–25 steps** · `res_multistep`/`simple` · shift **12/3** · CFG **~1.0** · **one** attention backend · **no** EasyCache/Spectrum on REF · `ref_image_size=match` first.  
2. **Community “fast” stack is usually a draft lane**, not quality-neutral: Turbo/Lightning 4–8 · EasyCache · Spectrum · lower MP — then re-run final without them.  
3. **ck-attn is NOT early KEEP:** habit on some 40/50-series; wall wins reported; **Integrity not proven**; Kitchen can **crash** on int8_convrot (#15529). Tag = **DISPUTED**.  
4. **KNOWN_FAIL → skip smoke:** EasyCache/Spectrum on REF+AV finals · Turbo/Lightning as KEEP final · stacked attention patches · fp8 CLI with kitchen · DynamicVRAM ON when HostBuffer 1450 · CAB as quality-neutral.  
5. **Community rarely fair-A/Bs** exclusive backends, NODDV peels, or audio metrics — they stack levers and eyeball. Our matrix must not copy that habit.  
6. **Implications:** BASE = NODDV+no-fp8+**ck-attn OFF**; A/B ck-attn · Sage · sol-attn · steps · scheduler · match/max; never crown Turbo/cache.

**Write path:** `/workspace/cos/research/2026-10-02-max-community-speed-quality-practices.md`

---

## Sources cited

### Official / model authors

| Source | URL |
|--------|-----|
| Comfy MiniMax H3 tutorial (steps, Lightning, Sage, Kitchen, sol-attn, ref_image_size) | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 |
| Comfy-Org MiniMax-H3 README (int8_convrot > fp8) | https://huggingface.co/Comfy-Org/MiniMax-H3 |
| MiniMaxH3ReferenceToVideo `ref_image_size` tooltip | https://github.com/comfyanonymous/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py |
| TenStrip / 10Eros-Max README (sampling; **no cache/spectrum on reference**) | https://huggingface.co/TenStrip/10Eros-Max |
| Abiray 10Eros-Max Hybrid GGUF (mirrors TenStrip sampling + no cache/spectrum) | https://huggingface.co/Abiray/10Eros-Max-Hybrid-Beta5-GGUF |

### Community guides / packs / issues

| Source | URL |
|--------|-----|
| wildminder awesome-minimax-H3 performance guide (2026-08-16) | https://github.com/wildminder/awesome-minimax-H3/blob/main/guides/minimax-h3-performance.md |
| ByronLeeeee ComfyUI-MiniMax-H3-Optimization-Suite | https://github.com/ByronLeeeee/ComfyUI-MiniMax-H3-Optimization-Suite |
| Andrew Zhu Medium — days of H3 testing (Sage+EasyCache vs Sol-Attn quality) | https://xhinker.medium.com/minimax-h3-everything-i-know-after-days-of-testing-what-works-what-not-648e4df78128 |
| InstaSD — sparse attention 2.5× stack | https://www.instasd.com/post/minimax-h3-sparse-attention-comfyui-guide |
| InstaSD — EasyCache vs TeaCache vs Spectrum | https://www.instasd.com/post/comfyui-easycache-teacache-spectrum-speedup |
| Saganaki22 ComfyUI-sol-attn | https://github.com/Saganaki22/ComfyUI-sol-attn |
| Zironic H3-Optimizations | https://github.com/Zironic/H3-Optimizations |
| xmarre ComfyUI-Spectrum-MiniMax-H3 | https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3 |
| ComfyUI #15326 EasyCache audio regression on H3 | https://github.com/Comfy-Org/ComfyUI/issues/15326 |
| ComfyUI #15529 Kitchen INT8 + int8_convrot alignment crash | https://github.com/Comfy-Org/ComfyUI/issues/15529 |
| ComfyUI #15255 / #15352 HostBuffer / DynamicVRAM | https://github.com/Comfy-Org/ComfyUI/issues/15255 · https://github.com/Comfy-Org/ComfyUI/issues/15352 |
| Reddit r/comfyui Sage vs Spectrum 3090 | https://www.reddit.com/r/comfyui/comments/1vi7yxw/minimax_h3_performance_comparison_no_acceleration/ |
| Reddit r/StableDiffusion tips (Sage / EasyCache coherence) | https://www.reddit.com/r/StableDiffusion/comments/1vegtac/minimax_h3_tips_and_tricks_and_what_i_experienced/ |
| Reddit r/comfyui EasyCache / Sage draft habit | https://www.reddit.com/r/comfyui/comments/1vg7v94/minimax_h3_fast_preview_quality_final_are_nearly/ |
| Reddit PSA Comfy Kitchen attention | https://www.reddit.com/r/comfyui/comments/1vpxg8l/public_service_announcement_if_youre_getting_slow/ |
| lightx2v / Turbo Ref2VA notes (community compare) | https://note.com/sepiablue/n/nefe91449936e · https://comfylab.dev/blog/workflows/minimax-h3-comfyui-pdd-acc-vs-turbo-lora-rtx-3090/ |
| Local COS (AlienPc constraints) | `research/2026-10-02-max-h3-faster-gen-no-quality-loss.md` · `audits/2026-10-02-max-optimization-ab-coverage.md` · `status/ce-plan-max-speed-quality-matrix-2026-10-02.md` |

---

## Consensus stack (quality-first finals)

What community *and* official tips converge on when the goal is **keep quality**, not max FPS:

| Piece | Practice | Tag |
|-------|----------|-----|
| Weights | Prefer **pruned int8_convrot** when CUDA/kitchen allow; **fp8 only if int8 unavailable** (Comfy-Org) | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| Lightning / Turbo LoRA | **OFF** for ID-critical R2V; base **20** steps (raise **→25** if ref drifts) | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| Sampler / scheduler | Template: **`res_multistep` + `simple`**; TenStrip also likes `res_multistep/simple` 6–8 on turbo hybrids | OFFICIAL_TIP · CONSENSUS_DEFAULT (start) |
| Flow shift | Video **12** / audio **3** | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| CFG | **~1.0** (guidance-distilled; true CFG doubles cost) | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| Attention | **Pick one** backend — do **not** stack Sage + Kitchen + SLA + sol patches | COMMUNITY_HABIT · CONSENSUS_DEFAULT (anti-stack) |
| Cache / Spectrum on REF | **OFF** — TenStrip: “No cache or spectrum if doing reference, they cause accuracy loss” | OFFICIAL_TIP (model author) · KNOWN_FAIL if used for REF finals |
| `ref_image_size` | Start **`match`**; **`max`** only when identity needs more tokens (slower) | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| Audio VAE | **fp32** (fp16/bf16 buzz / desync) | COMMUNITY_HABIT · CONSENSUS_DEFAULT |
| Workflow pattern | **Draft → final**: accelerate drafts; finals disable Turbo/cache/Spectrum | COMMUNITY_HABIT · CONSENSUS_DEFAULT |
| NODDV / pinned / async | On HostBuffer/AIMDO-broken Windows boxes: `--disable-dynamic-vram` (± pinned/async) to **finish gens** | COMMUNITY_HABIT (stability) · CONSENSUS_DEFAULT **for our box** — not a quality A/B |

**10Eros-Max-specific (TenStrip):** non-turbo full-step audio **always better** than turbo versions; hybrid TURBO bake is a product choice — stacking *another* Turbo LoRA is unproven and fights REF accuracy.

---

## Lever-by-lever: official tip vs habit vs hype → matrix tag

### 1. `--use-ck-attention` / Comfy Kitchen dense attention

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Kitchen INT8 backend clears morphing/text artifacts on **bf16** when Sage INT8 hurts late blocks; flag `--use-ck-attention` (≥0.32). **int8_convrot + Kitchen can crash** (alignment #15529) — docs say keep default attn or switch to bf16 then Kitchen. |
| COMMUNITY_HABIT | Many 40/50-series users report Kitchen **faster/cleaner than Sage**; Reddit PSA for slow gens / AMD. Parallel packs require Kitchen. |
| UNPROVEN_HYPE | “Always free lunch / always KEEP” — false. Hardware- and checkpoint-dependent. |
| **Matrix tag** | **DISPUTED** — fair **ON vs OFF** (and vs Sage). **Not early KEEP.** Prior AlienPc wall −18.6% was TECH-only; Integrity gate open. |

### 2. Model Sparse Attention `sol-attn` (official) / community Sol-Attn packs

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Built-in Model Sparse Attention, `method=sol-attn` (≥0.35); keep early/late denser; `sink_conditioning=exact_kv_and_rows`; default `tau≈1.3`; short clips gain little. |
| COMMUNITY_HABIT | Saganaki / KingGore / Zironic / PlagueKind SLA: big speed on long seq; **compose Sage as fallback in front, not behind**; do not stack SLA packs. |
| Quality split | wildminder/jo-nike: Sol-Attn **lossless/bit-identical** (their grid). xhinker Medium: Sol-Attn **faster but face detail loss** → stopped for finals. PlagueKind: sparsity 0.85–0.9 “almost free,” 0.95 minor deg. |
| UNPROVEN_HYPE | “2.5× with no quality loss” headlines — depends on sparsity %, motion, and pack defaults (retained vs discarded knobs are inverted across packs). |
| **Matrix tag** | **DISPUTED** — fair A/B vs dense (and separately vs ck-attn; **one owner**). Not KNOWN_FAIL at conservative tau / official defaults. |

### 3. SageAttention (`--use-sage-attention` / Patch Sage KJ / H3-specific Sage node)

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | ~**2×** possible; minimal quality loss; install sageattention + KJ patch; INT8 can morph late / garble text → Kitchen path on bf16. |
| COMMUNITY_HABIT | Broadest “first accelerator” habit; 1.6–2× common on healthy VRAM. KJ H3 MemoryEfficientSage preferred over generic patch by careful testers. |
| Caveat | On **≤12 GB + heavy offload**, Sage can be **2.5–3× slower** (VRAM → more offload) — 12 GB guide / wildminder. |
| **Matrix tag** | **DISPUTED** under our **NODDV+lowvram** — A/B required; may lose. Not CONSENSUS_DEFAULT on this box. |

### 4. Turbo / Lightning LoRA (4–8 step)

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Lightning switch → 4 steps on R2V templates: **starves reference tokens**; pose/face drift. Leave **OFF** for close REF; use base 20 / raise 25. |
| COMMUNITY_HABIT | Draft weapon: ~2–3.4×; 8-step Acc often better motion than 4-step; strength **0.8–0.85** not 1.0 for less breakage; audio/timbre often worse; TenStrip: non-turbo audio better. |
| UNPROVEN_HYPE | “4-step looks the same” — contradicted by freeze-pose / anime contrast / background detail / voice ring reports. |
| **Matrix tag** | **KNOWN_FAIL** as quality-neutral **final / KEEP** arm. Draft-only lane if ever — **do not smoke as speed-winner cell**. |

### 5. EasyCache / TeaCache

| Lens | Finding |
|------|---------|
| OFFICIAL / bug | #15326: EasyCache **degrades H3 audio** (video SSIM can stay high). Core node experimental. |
| Model author | TenStrip: **no cache on reference**. |
| COMMUNITY_HABIT | Popular draft combo with Sage; some claim near-baseline video; many report coherence / likeness / physics loss on R2V; Spectrum author: EasyCache “destroys output hard” on H3. |
| TeaCache | Stale / breaks on modern Comfy — avoid as default. |
| Stack | **Do not** stack EasyCache + Spectrum; wildminder: EasyCache **cannot combine with Turbo** (skipped steps). |
| **Matrix tag** | **KNOWN_FAIL** for REF2VA **final AV / Integrity** smokes. Skip. |

### 6. Spectrum

| Lens | Finding |
|------|---------|
| Author README | Approximate, **not** bit-identical; trajectory / fast-detail / eyes / fingers can degrade; A/B advised. |
| TenStrip | No spectrum on reference. |
| COMMUNITY_HABIT | Pairs with Sage for wall clock; needs higher step counts to “shine”; lossy; audio hurt reports; some R2V no-ops. Real Comfy gains ~1.2–1.4× not paper 4.8×. |
| **Matrix tag** | **KNOWN_FAIL** for quality-neutral REF finals. Skip. |

### 7. Steps (25 / 20 / 12–16)

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Template **20**; raise **25** if REF drifts; simple content 12–16; detail up to ~50; **audio settles later than picture**. |
| COMMUNITY_HABIT | Ref2VA often **≥20** for audio; **25** common floor; MiniMax marketing sometimes 30–50; some prefer no-LoRA 12 for looks (disputed). |
| **Matrix tag** | **25↔20 = DISPUTED** (fair A/B). **12–16 without Turbo = KNOWN_FAIL** for our Integrity finals. |

### 8. Scheduler (`simple` vs `beta` / `normal`) / sampler

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Templates ship **`res_multistep` + `simple`**. |
| COMMUNITY_HABIT / prompting BPs | On REF, `beta`/`normal` sometimes preferred; TenStrip turbo recipes mix er_sde/beta, LCM/simple, euler/simple. |
| **Matrix tag** | Scheduler **simple↔beta/normal = DISPUTED**. Sampler change = later optional DISPUTED (not first). |

### 9. NODDV / `--disable-dynamic-vram` (+ pinned / async)

| Lens | Finding |
|------|---------|
| COMMUNITY_HABIT | Confirmed workaround for HostBuffer.read_file_slice / AIMDO crashes (#15255 family); `--disable-pinned-memory` for pinned OOM on video models. |
| Our box | Triad **required** to complete Max smokes (CAPA). |
| **Matrix tag** | **CONSENSUS_DEFAULT (stability freeze)** — **not** a quality speed A/B. Re-enable DynamicVRAM = **KNOWN_FAIL / blocked** until HostBuffer cleared (≥2 TECH). Peel async/pinned alone = HOLD (stability risk), not speed matrix. |

### 10. fp8 CLI / quant choice

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Prefer **int8_convrot**; fp8_scaled only if int8 unavailable. |
| COMMUNITY_HABIT | Blackwell: int8 often ~10% faster than fp8 (xhinker). FP8 <15% gain vs INT8 on non-Blackwell (12 GB guide). |
| Our box | fp8 CLI casts **break** kitchen RoPE/q_scale — DROP CAPA. |
| **Matrix tag** | Re-enable fp8 CLI = **KNOWN_FAIL**. Weight-format swaps only if UNET class changes. |

### 11. `ref_image_size` match vs max

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | `match` = faster, gen-area sized; `max` = up to 2048 short edge, stronger ID, **several× slower** (tokens every step). |
| COMMUNITY_HABIT | Start match; max when identity soft. |
| **Matrix tag** | **DISPUTED** quality vs wall — fair A/B after Integrity baseline. Default freeze = **match** (CONSENSUS_DEFAULT start). |

### 12. ByronLee suite / CAB / NVFP4 fused MLP / FirstBlockCache

| Lens | Finding |
|------|---------|
| COMMUNITY_HABIT | NVFP4 fused MLP ~bit-identical **on NVFP4 UNET**; CAB low-step = speed with SSIM loss; FirstBlockCache claimed faster than Spectrum (less vetted). |
| Our UNET | **w4a8 / TURBO-hybrid** — fused MLP claim **does not transfer**. |
| **Matrix tag** | NVFP4 fused / CAB quality-neutral = **KNOWN_FAIL / N/A** for current weights. FirstBlockCache = **UNPROVEN_HYPE** → skip until after core DISPUTED lanes. |

---

## What the community skips A/B’ing (habit gaps)

Copying community workflow **without** our rules would miss:

1. **Exclusive backend A/B** — users stack Sage+Spectrum+Turbo+SLA and post one timer.  
2. **Same-seed Integrity gates** — rare Bot/thumbs Face/Hands/Oral/Contact; mostly “looks fine.”  
3. **Audio metrics** with EasyCache — long under-reported until #15326.  
4. **NODDV one-flag peels** — triad applied as blob; no fair speed×stability peel.  
5. **sol-attn vs ck-attn as mutually exclusive owners** — packs fight silently.  
6. **Turbo vs base trajectory** — different NFE/shift → not same-seed fair quality.  
7. **10Eros hybrid ≠ stock H3** — Turbo LoRA recipes from lightx2v assume stock Ref2VA, not baked hybrid.  
8. **Paper × vs Comfy ×** — Spectrum 4.8× paper vs ~1.3× node.

**We must not skip those** — matrix stays one-axis, same seed, thumbs ≥ baseline.

---

## Implications for our Max speed matrix

Aligns with `status/ce-plan-max-speed-quality-matrix-2026-10-02.md` + Derrick steering (**ck-attn not early KEEP**):

| Matrix action | Why (community-backed) |
|---------------|------------------------|
| **BASE = NODDV + no-fp8 + ck-attn OFF** | Stability freeze + no early crown |
| **Smoke DISPUTED:** ck-attn ON/OFF · Sage · sol-attn (one owner) · steps 25↔20 · scheduler simple↔beta · match↔max · length/mode later | Real community split / official tips |
| **SKIP KNOWN_FAIL smokes:** EasyCache · Spectrum · Lightning/Turbo as KEEP · stacked attn · fp8 CLI · DynamicVRAM ON · CAB / NVFP4 fused on w4a8 · steps 12–16 no Turbo | Author + official + bug evidence |
| **Draft lane separate** (if Derrick wants iteration speed) | Community draft→final — never crowning |
| **A1 audio after L1 visual** | Audio settles later; cache hurts audio first |
| **Winner rule** | Wall ↓ **and** thumbs ≥ BASE — matches community failures when speed-only crowned |

### Suggested fair order (unchanged intent; tags applied)

1. **OPT-CK** — ck-attn ON vs OFF (**DISPUTED**, not KEEP)  
2. **OPT-SCH** — simple vs beta (**DISPUTED**)  
3. **OPT-STEPS** — 25 vs 20 (**DISPUTED**)  
4. **OPT-REF** — match vs max (**DISPUTED**)  
5. **OPT-SOL** — sol-attn conservative vs dense (**DISPUTED**; exclusive vs other attn)  
6. **OPT-SAGE** — Sage vs dense / vs winner attn (**DISPUTED**; last among attn — NODDV may hurt)  
7. **OPT-LEN / mode** — product change; label clearly  
8. **Never queue:** EasyCache · Spectrum · Lightning KEEP · fp8 · DynamicVRAM  

---

## Quick reference table

| Lever | Official tip | Community habit | Hype risk | **Our tag** |
|-------|--------------|-----------------|-----------|-------------|
| ck-attn | Kitchen for bf16 artifacts; int8_convrot may crash | Faster than Sage on many 40/50 | Always KEEP | **DISPUTED** |
| sol-attn | Official sparse node; sink exact | Packs 1.1–2.5×; quality split | 2.5× lossless | **DISPUTED** |
| Sage | ~2×, minimal loss | First accel habit | Always free under lowvram | **DISPUTED** |
| Turbo/Lightning | OFF for close R2V | Draft 4–8 step | Same as 20-step | **KNOWN_FAIL** (final) |
| EasyCache | — | Draft + Sage | Lossless on H3 | **KNOWN_FAIL** (REF AV) |
| Spectrum | — | Stack with Sage | Paper 4.8× | **KNOWN_FAIL** (REF final) |
| Steps 20/25 | 20 base; 25 if drift | ≥20–25 Ref2VA | 12-step = best | **DISPUTED** (20↔25) |
| Scheduler | simple | beta/normal on REF | — | **DISPUTED** |
| NODDV | HostBuffer workaround | Required on broken AIMDO | Speed win | **CONSENSUS_DEFAULT** (stability) |
| fp8 | Prefer int8 | Blackwell int8>fp8 | fp8 free speed | **KNOWN_FAIL** (CLI re-on) |
| ref_image_size | match first; max = ID | Same | max free | **DISPUTED** (match↔max) |

---

## Verdict stamp

| Question | Answer |
|----------|--------|
| Is there a community **quality-neutral** mega-stack? | **No** — finals strip Turbo/cache/Spectrum; attn is one backend. |
| Is **ck-attn** community best-practice KEEP? | **No** — common habit / sometimes official Kitchen tip, but **DISPUTED** and checkpoint-fragile. |
| Should we smoke EasyCache/Spectrum/Turbo for “no quality loss”? | **No — KNOWN_FAIL** for our REF2VA Integrity finals. |
| What should Dial smoke? | Only **DISPUTED** one-axis cells vs BASE; skip **KNOWN_FAIL**. |

**No Dial ping this turn** (research write only).
