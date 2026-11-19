# Research — Can Max MiniMax-H3 REF2VA cut ~350s without quality sacrifice?

**Date:** 2026-10-02 ~09:40 CT (America/Chicago)  
**Owner:** executor research ONLY  
**Scope:** AlienPc Comfy `:8189` Max / 10Eros MiniMax-H3 REF2VA  
**Action:** **NO AlienPc change** · no argv restart · no queue · no workflow edit  

## Baseline (locked)

| Item | Value |
|------|--------|
| Comfy | 0.38.0 · `:8189` |
| GPU | RTX 5070 Ti 16 GB (Blackwell) |
| Argv | `--lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory` (**no fp8**) |
| Constraint | **NODDV required** — AIMDO HostBuffer WinError **1450** when DynamicVRAM ON |
| Stack | w4a8 UNET (10Eros Max TURBO-hybrid) + nvfp4 TE (Qwen3-VL) |
| TECH | 864×480 · **124f** · **25** steps · `res_multistep` · REF2VA |
| Observed wall | ~**341–350 s** per successful smoke (warm-ish) |

**Question:** Can we cut that ~350 s **without quality sacrifice** (Integrity / hands / oral / Face gate still fair)?

**Headline answer:** **PARTIAL.** Large cuts (≥2×) need Turbo / cache / fewer steps and are **not** quality-neutral for REF2VA finals. Quality-preserving levers on this NODDV box are small (~5–15% denoise, maybe ~20–50 s) if anything — and several “community free lunches” are **slower or broken** under `--lowvram` + NODDV.

---

## Sources (2026)

1. wildminder `awesome-minimax-H3` performance guide (2026-08-16) — consumer tiers, Turbo/EasyCache/Sage/sol-attn field verdicts  
2. ByronLeeeee `ComfyUI-MiniMax-H3-Optimization-Suite` EVALUATION_REPORT — **5070 Ti 16 GB**, fused MLP / Sage2 / CAB vs 20-step  
3. HF `drbaph` / `Alberto454` MiniMax-H3 Turbo LoRA ComfyUI READMEs — 4 / 6–8 step recipes  
4. seedance.tv / minimaxh3.co — stock 20-step `res_multistep` quality baseline; Turbo ≠ drop-in fewer steps  
5. ComfyUI #15326 — EasyCache **audio regression** on H3 (video SSIM high, audio muffled)  
6. app.nz EasyCache H3 sweeps — reject cache if motion/audio/face drift vs same-seed uncached  
7. Local COS: `2026-10-02-hostbuffer-disable-dynamic-vram.md`, `2026-10-02-max-8189-setup-optimized.md` — NODDV triad locked; fp8 CLI already dropped as harmful  
8. Community Reddit consolidation (`1vmprjh`, `1vmjdiw`, `1vmnwf7`) — draft→final; Ref2VA ≥20 steps for audio; 25 common floor  

---

## Lever matrix (YES / PARTIAL / NO)

Legend: **YES** = credible quality-neutral (or bit-identical) speedup on *this* class of box · **PARTIAL** = speed possible but quality/product change or unproven under NODDV · **NO** = do not use for “no quality loss” finals · **Time save** = rough wall estimate vs ~350 s baseline (denoise-dominated).

| # | Lever | Verdict | Est. time save | Quality risk | Notes for AlienPc NODDV |
|---|-------|---------|----------------|--------------|-------------------------|
| 1 | **Steps 25 → 20** (same sampler) | **PARTIAL** | ~**15–20%** denoise ≈ **50–70 s** | **MED** — community: 20 = Comfy quality baseline; Ref2VA audio/fine motion often prefer **≥20–25**; hands/oral Integrity dial may regress | Linear NFE cut. Fair A/B only if same seed + Bot vision all axes. Not “free.” |
| 2 | **Steps 25 → 12–16** (no Turbo adapter) | **NO** | ~40–55% | **HIGH** — under-denoised motion/hands; audio suffer first | Stock model not distilled for this NFE. |
| 3 | **Turbo LoRA / LightX2V 4–8 step** | **NO** *(final)* / **PARTIAL** *(draft)* | **~2–3.4×** (community: 20→4 ≈ 3.4×; 20→8 ≈ 2×) | **HIGH** for KEEP — audio “goes down the shitter”; motion blur; accents; quiet vocals | Max UNET is already **TURBO-hybrid**; stacking another Turbo LoRA is unproven + author notes non-turbo better for audio. Use only as **draft** path, then re-run final at 20–25 no-Turbo. |
| 4 | **CFG / true CFG** | **NO** | **0 or negative** | **HIGH** if true CFG ON | H3 is guidance-distilled; keep **guidance ≈ 1.0**. True CFG = **2×** forwards. Raising CFG cannot cut time. |
| 5 | **Shorter length** (e.g. 124f → 73f / `17n+5`) | **PARTIAL** | ~**proportional** to frames (~30–40% if ~half duration) | **Product change** — not same clip; REF consistency / beat shorter | Valid for **smoke/draft** only, not “same gen faster.” |
| 6 | **Lower resolution** (864×480 → 0.2–0.4 MP) | **PARTIAL** | **large** (often 2×+) | **HIGH** for final Face/hands/contact scores | Community **draft→final** pattern. Do not KEEP at draft res. |
| 7 | **EasyCache / TeaCache** | **NO** *(final AV)* | Draft: ~**1.2–2×** claimed; at **20 steps** EasyCache often **ignored/inverse** | **HIGH for audio** (#15326: video SSIM 0.95+, audio muffled/desync); TeaCache tables are Wan/Flux — **no H3 REF2VA calibrated thresh** | Do **not** enable for Integrity/KEEP. Optional draft-only with same-seed uncached gate. |
| 8 | **SageAttention** (`--use-sage-attention` / node) | **PARTIAL** | Healthy VRAM: **~20–40%** attn; under **heavy offload**: can be **slower** (12 GB guide: Sage **2.5–3× slower**) | **LOW–MED** — usually slight numerical drift; rare NaN → fall back SDPA | On **NODDV + lowvram**, Sage **increases workspace** → more CPU offload → may **hurt**. A/B required; do not assume win. |
| 9 | **sol-attn / Comfy Kitchen attn (`--use-ck-attention`)** | **PARTIAL → best YES-candidate** | Community: **lossless / near-lossless**; ck-attn often **beats Sage** on 40/50-series | **LOW** if bit-identical path (sol-attn claimed) | **Best first “no quality loss” knob** *if* installed and compatible with kitchen + w4a8. Still one-knob A/B under NODDV. |
| 10 | **torch.compile / Compile Model** | **PARTIAL** | Warm: **~10–30%** typical (model-dependent); **cold first 1–3 gens slower** | **LOW** if same kernels; **MED** with nvfp4/kitchen/Triton cache staleness | Poor fit for short smoke sessions. Keep server warm. NODDV + compile unvalidated here. |
| 11 | **Re-enable DynamicVRAM (drop NODDV)** | **NO** | Potentially large *if healthy* | **Stability fail** — HostBuffer **1450** (local CAPA) | Forbidden until AIMDO survives ≥2 TECH smokes. Not a speed experiment. |
| 12 | **Re-enable async-offload and/or pinned-memory alone** | **PARTIAL** | Unknown; maybe **modest** load/step if DMA path safe | **MED–HIGH** HostBuffer recurrence risk | Stability triad was required to *finish* gens. Do not peel for speed without HostBuffer re-test plan. |
| 13 | **NVFP4 Fused MLP (opt suite)** | **NO / N/A** for current UNET | ByronLee: **~7%** denoise, **bit-identical** on **NVFP4 UNET** | **None** on validated NVFP4 path | Local UNET is **w4a8**, not NVFP4 — fused MLP claim **does not transfer**. Skip unless weights change. |
| 14 | **CAB-2 @ 10–14 steps** | **NO** | ~**30–50%** denoise | **HIGH** — SSIM ~0.81–0.83 vs 20-step ref (not aesthetic-safe) | Training-free solver ≠ quality-neutral. |
| 15 | **Spectrum** | **NO** | Unreliable at low steps | **HIGH** (lossy; audio hurt) | Avoid if quality matters. |
| 16 | **fp8 CLI casts** | **NO** | None useful | **BREAKS** kitchen RoPE / q_scale (local S0) | Already audited DROP. |

---

## Synthesis

### Can we cut ~350 s **without** quality sacrifice?

| Goal | Realistic? |
|------|------------|
| **~350 → ~175 s (2×)** quality-neutral | **NO** — needs Turbo and/or aggressive cache/step cut |
| **~350 → ~250–300 s (~15–30%)** with low risk | **PARTIAL** — sol-attn/ck-attn and/or warm compile *if* they win under NODDV; not guaranteed |
| **~350 → ~280–300 s** via **25→20 steps** | **PARTIAL** — measurable, but **not** quality-neutral by definition; fair vision A/B required |
| Flip NODDV / AIMDO for speed | **NO** until HostBuffer 1450 fixed upstream |

**10Eros Max** already embeds turbo-merge DNA. Community “add Turbo LoRA → 4 steps” recipes target **stock** H3, not this hybrid, and conflict with the current Integrity dial (hands 0.90, oral motion, deep-throat face-fuck prompts).

**NODDV tax:** The memory triad that keeps Max alive on 16 GB **caps** how much Sage/cache/compile can help. Guides that quote sub-200 s denoise often assume healthier DynamicVRAM or lighter offload — not this HostBuffer-broken Windows path.

---

## Recommended fair A/B plan (**one knob**)

**Do not change AlienPc in this research turn.** When Dial/parent schedules a speed probe:

### Primary (quality-neutral intent)

1. **Baseline:** current argv + workflow · fixed seed · fixed prompt/Cond/REF · 864×480 · 124f · **25** · `res_multistep` · wall clock + Bot vision axes.  
2. **One knob:** enable **sol-attn** *or* Comfy **`--use-ck-attention`** (pick **one**; prefer kitchen/ck if already in stack).  
3. **Same seed** re-run. Pass only if: wall ↓ **and** Face/ID, Hands, Oral, Contact, Wardrobe all **≥ baseline − 0.01** (or Derrick watch GO) **and** no HostBuffer/OOM.  
4. If wall **↑** or HostBuffer → **revert**; mark Sage/ck as NODDV-hostile on this box.

### Explicitly **not** first knob

- Turbo LoRA / step slash / EasyCache / TeaCache / drop NODDV / peel pinned-async / resolution cut for KEEP.  
- Combine multiple accelerators in one smoke.

### Optional later (accept quality trade — separate lane)

- **Draft lane:** 0.3–0.4 MP · 8–13 steps · Turbo **xor** EasyCache · BlehTAE decode — iterate prompts.  
- **Final lane:** restore 864×480 · 20–25 · no cache · no Turbo LoRA — Integrity score.  
- Or single-knob **25→20** with vision gate if Derrick accepts possible fine-motion/audio tick.

---

## Verdict stamp

| Question | Answer |
|----------|--------|
| Free lunch cut of ~350 s? | **NO** |
| Any quality-neutral speedup plausible? | **PARTIAL** — small; attn kernel A/B first |
| Big speedups available? | **YES** but **with** quality/product sacrifice (Turbo/cache/res/length) |
| Change AlienPc now? | **NO** (research only) |

---

## 3-bullet for parent

1. **No free 2×** on this NODDV Max stack; Turbo/EasyCache/step-slash buy time by selling audio/motion/Integrity.  
2. **Best fair one-knob** for “no quality loss”: **sol-attn or ck-attention** same-seed A/B; expect modest win or a NODDV slowdown — measure, don’t assume.  
3. **Keep** NODDV triad + no-fp8; use draft→final if iteration speed matters more than single-gen wall.

## Dial / executor did NOT

Restart Comfy · change argv · queue Max · SendToUser · invent KEEP · enable cache/Turbo on live graph.
