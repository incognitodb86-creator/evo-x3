# Research — FLUX.2 speed×quality practices (AlienPc :8189 stills + Max stack)

**When_CT:** 2026-10-02 ~10:35 CT (America/Chicago)  
**Owner:** executor research ONLY  
**Scope:** Community + official practices for **FLUX.2** (primary: **[klein] 4B/9B**; secondary notes: **Dev 32B** + Turbo LoRA) on **RTX 5070 Ti 16 GB** / TestRuntime Comfy **:8189**.  
**Goal lens:** **speed with no quality sacrifice** for upcoming smokes **AFTER** Max speed matrix.  
**Action:** **NO Dial ping** · no queue · no argv change · DRAFT matrix only  

**Local SoT context:**
- Production B: Flux stills + 10Eros-Max on `:8189` · LTX `:8188` = METHOD only — `status/2026-10-02-alienpc-sot-B-flux-max.md`
- Install / pick: `status/ce-plan-flux2-alienpc-2026-10-02.md` · VRAM: `status/RESEARCH_FLUX2_KLEIN_9B_5070TI_2026-10-02.md`
- Max matrix (runs first): `status/ce-plan-max-speed-quality-matrix-2026-10-02.md`
- Policy (Derrick): **skip KNOWN_FAIL** · fair A/B **DISPUTED** · report near-miss faster+worse · **no early KEEP**

**Tags (this file):**

| Tag | Meaning for Flux2 matrix |
|-----|--------------------------|
| **CONSENSUS_DEFAULT** | Official template / BFL sample / broad agreement — freeze as BASE start; not a quality crown on our box |
| **DISPUTED** | Real speed claims, split quality reports — **fair one-axis A/B** after Max |
| **KNOWN_FAIL** | Repeated official/community warnings of quality/stability loss for our use — **SKIP smoke** |
| **OFFICIAL_TIP** | BFL / Comfy docs / Comfy blog / model README |
| **COMMUNITY_HABIT** | Guides / Reddit / pack READMEs |
| **BOX_CONSTRAINT** | 5070 Ti 16 GB + shared `:8189` with Max argv |

---

## Headline (6 bullets for parent)

1. **Speed matrix BASE = FLUX.2 [klein] 4B distilled FP8 HAVE** (speed levers only; 9B official gated / community NSFW HAVE) — **not** Dev 32B. Distilled quality stack is already the speed product: **exactly 4 steps · CFG≈1.0 · euler · Flux2Scheduler BASE** (simple is the OPT-SCHED arm) **· matched Qwen3 TE · real `flux2-vae`**. Extra steps / high CFG on distilled = **KNOWN_FAIL** (waxy/deep-fried). **Unlock quality host = FLUX-KLEIN-9B-FP8-NSFW after Derrick GO (separate product/stills lane); official 9B remains gated.**  
2. **No quality-neutral 2× left on distilled Klein** the way Turbo/Lightning claim for video — model is already 4-step. Remaining levers are **attention / compile / NVFP4 / res / refs / argv** and are mostly **DISPUTED** or VRAM tradeoffs.  
3. **KNOWN_FAIL → skip:** steps≠4 on distilled · CFG≫1.5 distilled · Euler A on distilled · Fake Flux.1 VAE · wrong TE size · Dev 32B as primary on 16 GB · TeaCache/EasyCache as KEEP final · multi-ref climb as “free speed” · stacking Sage+Kitchen patches.  
4. **DISPUTED (smoke later):** Sage (`--use-sage-attention` / node) · ck-attn · torch.compile · NVFP4 · TeaCache (CPU cache_device) as *near-miss* · base vs distilled for unlock · community 9B NSFW vs official · Flux2Scheduler vs simple · single-ref res climb.  
5. **Shared `:8189` argv conflict:** Flux2 CE plan used `--fp8_e4m3fn-* --lowvram`; Max matrix freezes **NODDV + fp8 CLI OFF**. Flux2 speed matrix requires **TECH-ARGV-FLUX**: recycle TR, then test **fp8 CLI ON + lowvram + NODDV triad**; HostBuffer → STOP. Do not silently inherit Max fp8-OFF; tag peel-NODDV as a **stability hold / DISPUTED**, not a quality KNOWN_FAIL.  
6. **Turbo analog:** fal **FLUX.2-dev-Turbo** LoRA (8-step) is for **Dev 32B**, not Klein distilled. Treat as **SKIP for Klein primary**; optional later Dev/GGUF draft lane only.

**Write path:** `/workspace/cos/research/2026-10-02-flux2-speed-quality-practices.md`  
**DRAFT matrix:** `/workspace/cos/status/ce-plan-flux2-speed-quality-matrix-DRAFT-2026-10-02.md`

---

## Sources cited

### Official / model authors

| Source | URL |
|--------|-----|
| ComfyUI Flux.2 Klein guide (templates, files, 4B/9B) | https://docs.comfy.org/tutorials/flux/flux-2-klein |
| ComfyUI Flux.2 Dev guide | https://docs.comfy.org/tutorials/flux/flux-2-dev |
| Comfy blog — Klein 4B/9B performance + FP8/NVFP4 repos | https://blog.comfy.org/p/flux2-klein-4b-fast-local-image-editing |
| BFL FLUX.2 [klein] 4B card (4 steps, guidance_scale=1.0, ~13GB) | https://huggingface.co/black-forest-labs/FLUX.2-klein-4B |
| BFL FLUX.2 [klein] 9B | https://huggingface.co/black-forest-labs/FLUX.2-klein-9B |
| BFL klein 4B/9B FP8 | https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8 · https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-fp8 |
| BFL klein NVFP4 | https://huggingface.co/black-forest-labs/FLUX.2-klein-4b-nvfp4 · https://huggingface.co/black-forest-labs/FLUX.2-klein-9b-nvfp4 |
| Comfy-Org flux2-dev (fp8mixed + Turbo LoRAs) | https://huggingface.co/Comfy-Org/flux2-dev |
| fal FLUX.2-dev-Turbo (8-step LoRA; Comfy keys) | https://huggingface.co/fal/FLUX.2-dev-Turbo |
| NVIDIA RTX AI Garage (Flux / Comfy / NVFP4 context) | https://blogs.nvidia.com/blog/rtx-ai-garage-flux-ltx-video-comfyui-gdc/ |
| BFL blog Klein | https://bfl.ai/blog/flux2-klein-towards-interactive-visual-intelligence |

### Community guides / issues

| Source | URL |
|--------|-----|
| nomadoor — Klein workflows (4-step distilled, max 4 refs, Flux2Scheduler≈simple) | https://comfyui.nomadoor.net/en/basic-workflows/flux-2-klein/ |
| neurocanvas — Klein Comfy setup (CFG/steps fail modes) | https://neurocanvas.net/blog/flux-2-klein-comfyui-guide/ |
| earngenix — Klein prompting / Sage tip / 4B exactly-4 warning | https://www.earngenix.com/workflows/flux2-klein-image-comfyui |
| earngenix — Flux2 Dev multi-ref / TE fp8 | https://www.earngenix.com/workflows/flux2-comfyui |
| Thunder Compute — Flux Comfy guide (Klein table; GGUF; Euler A avoid) | https://www.thundercompute.com/blog/flux-comfyui-ai-image-generation |
| WillItRunAI — Flux 2 local / FP8 / compile | https://willitrunai.com/blog/how-to-run-flux-2-locally |
| StableDiffusionTutorials — Flux.2 Dev GGUF/FP8/BF16 | https://www.stablediffusiontutorials.com/2025/11/flux-2.html |
| kombitz — Dev Turbo + GGUF on consumer GPUs | https://www.kombitz.com/2026/01/01/how-to-use-flux-2-dev-turbo-lora-in-comfyui-with-gguf-models/ |
| Reddit — Flux2 Turbo Comfy keys | https://www.reddit.com/r/StableDiffusion/comments/1pzbrg1/flux2_turbo_lora_corrected_comfyui_lora_keys/ |
| KJNodes #670 — Patch Sage crash on Flux2 Klein; native `--use-sage-attention` path | https://github.com/kijai/ComfyUI-KJNodes/issues/670 |
| blepping/ComfyUI-bleh #13 — Sage on Flux speed varies | https://github.com/blepping/ComfyUI-bleh/issues/13 |
| ComfyUI-TeaCache README (FLUX / Kontext thresh; “acceptable quality loss”) | https://github.com/welltop-cn/ComfyUI-TeaCache |
| TeaCache #176 — CUDA cache JPEG artifacts on Flux; CPU cache_device fix | https://github.com/welltop-cn/ComfyUI-TeaCache/discussions/176 |
| TeaCache #113 — torch.compile cudagraphs ~14% / MAE 0 on Flux.1 (not Flux2-proven) | https://github.com/welltop-cn/ComfyUI-TeaCache/issues/113 |
| Local COS | `ce-plan-flux2-alienpc-2026-10-02.md` · `RESEARCH_FLUX2_KLEIN_9B_5070TI_2026-10-02.md` · Max practices / matrix |

---

## Consensus stack (quality-first finals on this box)

What official + careful community converge on when the goal is **keep quality**, not max FPS drafts:

| Piece | Practice | Tag |
|-------|----------|-----|
| **Primary UNET** | **klein distilled FP8** — start **4B** (`flux-2-klein-4b-fp8`) HAVE; 9B after gate / NSFW A/B | OFFICIAL_TIP · CONSENSUS_DEFAULT · BOX_CONSTRAINT |
| **Skip as primary** | FLUX.2 **Dev 32B** BF16/FP8 without GGUF — VRAM class wrong for 16 GB finals | BOX_CONSTRAINT · KNOWN_FAIL as quality host without heavy offload |
| **TE** | 4B→`qwen_3_4b` · 9B→`qwen_3_8b_fp8mixed` — **never mix** | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| **VAE** | **`flux2-vae.safetensors` only** (not FAKE / not Flux.1 AE) | OFFICIAL_TIP · KNOWN_FAIL if wrong |
| **Steps (distilled)** | **Exactly 4** (BFL sample + Comfy distilled templates) | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| **CFG (distilled)** | **1.0** (BFL `guidance_scale=1.0`); community allows ≤~1.5 — higher → waxy/deep-fried | OFFICIAL_TIP · KNOWN_FAIL if CFG high |
| **Sampler / sched** | **euler + Flux2Scheduler BASE** (template/local TECH SoT); **simple** is OPT-SCHED only | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| **Steps/CFG (base)** | Base ≈ **20–24** (guides) / Comfy blog **~50** on 5090 timing tables · CFG **~3.5–5** — different product; not “faster distilled” | OFFICIAL_TIP · DISPUTED for unlock quality |
| **Refs** | Edit: **single Cond first**; multi-ref max **4** (nomadoor); Dev docs advertise up to **10** — cost scales | OFFICIAL_TIP · CONSENSUS_DEFAULT |
| **Resolution** | locked Cond-native dims **÷16**; P163 Integrity SoT = **1792×1008**; climb only as a product cell after Integrity PASS | LOCAL TECH SoT · CONSENSUS_DEFAULT |
| **Attention** | **One** backend; Sage optional in many Flux2 workflows (bypass OK) | COMMUNITY_HABIT · CONSENSUS_DEFAULT (anti-stack) |
| **Quant** | **FP8** default on 16 GB; **NVFP4** = RTX 50 speed/VRAM upgrade after clean FP8 | OFFICIAL_TIP · DISPUTED until local smoke |
| **Draft→final** | Cache / Turbo / aggressive thresh = **draft**; finals off | COMMUNITY_HABIT · CONSENSUS_DEFAULT |
| **Fill** | **STOPPED** (local Derrick) | BOX_CONSTRAINT |

**BFL distilled is already the “Lightning analog.”** Do not bolt fal Dev-Turbo onto Klein and call it consensus.

---

## Lever-by-lever → matrix tag

### 1. Steps (distilled vs base)

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Distilled Klein: **4** inference steps (BFL Diffusers sample; Comfy Distilled Image Edit templates). Base: full-step (blog ~50 on 5090; community often 20–24). |
| COMMUNITY_HABIT | **More than 4 on distilled actively hurts** (earngenix / neurocanvas: overcooked / deep-fried). |
| Tag | Distilled steps≠4 → **KNOWN_FAIL**. Base step ladder → **DISPUTED** (quality vs wall), separate product cell. |

### 2. CFG / guidance

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Distilled: `guidance_scale=1.0`. Flux family often uses KSampler CFG=1 + embedded / FluxGuidance for Dev-class. |
| COMMUNITY_HABIT | Distilled CFG 1.0–1.5; CFG high → plastic/waxy. Base CFG 3.5–5. |
| Tag | Distilled CFG≫1.5 → **KNOWN_FAIL**. FluxGuidance sweeps on Dev → **DISPUTED** (not Klein primary). |

### 3. Sampler / scheduler

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Templates ship euler + Flux2Scheduler / simple. |
| COMMUNITY_HABIT | Avoid **Euler Ancestral** on distilled (Thunder). simple ≈ Flux2Scheduler for practical quality (nomadoor). |
| Tag | Euler A distilled → **KNOWN_FAIL**. **Flux2Scheduler is BASE**; simple → **DISPUTED OPT-SCHED** (likely near-tie). |

### 4. FP8 / NVFP4 / GGUF / BF16

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Comfy workflows ship **FP8** UNETs; NVFP4 repos exist for Klein; Dev = `flux2_dev_fp8mixed`. BF16 9B ~29 GB. |
| BOX_CONSTRAINT | 5070 Ti: FP8 distilled 4B ~8–10 GB; 9B FP8 tight with lowvram; NVFP4 best *future* speed/VRAM on 50-series. GGUF = last resort. |
| Tag | BF16 9B / Dev full as primary → **KNOWN_FAIL** for this box. FP8 = **CONSENSUS_DEFAULT**. NVFP4 = **DISPUTED** (install after FP8 green). GGUF Q2–Q4 as quality final → **KNOWN_FAIL**; Q5–Q8 draft only → **DISPUTED**. |

### 5. Attention — Sage / ck-attn / Patch Sage KJ

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP / habit | Many Flux2 workflow packs include Sage node (bypass if missing). |
| COMMUNITY | KJNodes #670: **Patch Sage Attention KJ** hard-crashed Flux2 Klein for one reporter; **native `--use-sage-attention`** worked. Kijai: Patch Sage fine on 4090/5090 with correct wheel — **install/env dependent**. bleh #13: Sage on Flux can be small/zero gain depending on head size / path. |
| Max learn | ck-attn wall wins TECH-only on H3; Integrity open — **do not early KEEP** on stills either. |
| Tag | Sage / ck-attn / Patch Sage → **DISPUTED** one-axis A/Bs. **If an ON arm silently falls back or the graph/kernel is unchanged, mark VOID, not KEEP.** Stacking backends → **KNOWN_FAIL**. Patch Sage alone if prior crash on this TR → treat as **KNOWN_FAIL until wheel verified**. |

### 6. torch.compile / `--fast`

| Lens | Finding |
|------|---------|
| COMMUNITY | TeaCache #113: cudagraphs ~14% / **0 MAE** on **Flux.1** 4060 Ti — **not** Flux.2 Klein proof. First compile cold. Breaks with some EasyCache / GGUF combos historically. |
| Tag | **DISPUTED** — fair A/B after BASE; cold vs warm wall separate. |

### 7. Resolution / batch / multi-ref

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | Klein: up to 4MP; refs max 4 (nomadoor). Dev: multi-ref up to 10 (Comfy Dev docs). |
| BOX_CONSTRAINT | Res/ref climb = **VRAM + wall**; not free speed. Batch>1 rarely quality-neutral on 16 GB. |
| Tag | Multi-ref / 2–4MP as speed “win” → **KNOWN_FAIL** framing. Res ladder & ref count = **product/ID cells**, not same-clip speed ranking (mirror Max Gemini amend). Batch>1 → **DISPUTED** / likely SKIP if OOM. |

### 8. Cache (TeaCache / EasyCache / Spectrum analogs)

| Lens | Finding |
|------|---------|
| COMMUNITY | TeaCache README: FLUX ~2× with **“acceptable visual quality loss”** (thresh 0.4). Kontext lower thresh. #176: CUDA cache → JPEG artifacts on Flux; **cache_device=cpu** mitigates. |
| Policy | Derrick: faster+worse still report as near-miss; **do not KEEP** if Integrity drops. |
| Tag | Cache ON as quality KEEP → **KNOWN_FAIL**. Cache ON as **near-miss report** cell → optional **DISPUTED** (draft lane). Spectrum/EasyCache from Max video stack → **SKIP** on stills unless Flux-specific node proven. |

### 9. Lightning / Turbo analogs

| Lens | Finding |
|------|---------|
| OFFICIAL_TIP | **Klein distilled = 4-step product.** fal **FLUX.2-dev-Turbo** = LoRA on **Dev**, 8 steps, guidance 2.5, custom sigmas; Comfy keys via ByteZSzn / Comfy-Org. |
| COMMUNITY | Turbo+GGUF used to squeeze Dev onto 12–16 GB class — quality claims author-optimistic; always A/B. |
| Tag | Turbo on **Klein** → **KNOWN_FAIL** / wrong checkpoint. Turbo on Dev/GGUF → **DISPUTED draft**; finals without Turbo. |

### 10. Argv / VRAM / DynamicVRAM (shared :8189)

| Lens | Finding |
|------|---------|
| Local Flux2 plan | `--fp8_e4m3fn-unet --fp8_e4m3fn-text-enc --lowvram` |
| Local Max matrix | **NODDV triad** + **fp8 CLI OFF** (HostBuffer 1450 CAPA; kitchen q_scale) |
| Tag | **BOX_CONSTRAINT:** Flux2 BASE argv must be **explicit Flux stills recipe**, not silent Max freeze. DynamicVRAM HostBuffer re-enable → **KNOWN_FAIL** (Max CAPA; assume stills risk until proven). Peel NODDV for Flux-only → **DISPUTED stability**, not quality crown. |

### 11. Community NSFW 9B vs official 9B / 4B

| Lens | Finding |
|------|---------|
| Local | 4B official HAVE; 9B official **403 gate**; NSFW 9B HAVE interim. |
| Tag | Weight choice = **product/ID A/B** after speed BASE on 4B — **DISPUTED** for anatomy unlock, not a speed lever. |

---

## Default SKIP / HAVE gates (before any queue)

These are inventory gates, not quality verdicts: do not place unavailable artifacts in the smoke queue.

- **SKIP-NVFP4-UNTIL-HAVE** — NVFP4 weights are not on disk; revisit only after download and verification.
- **SKIP-BASE-WEIGHTS-UNTIL-HAVE** — `flux-2-klein-base-4b-fp8` is not on disk; keep base-vs-distilled as a parked product cell.
- **SKIP-OFFICIAL-9B-UNTIL-GATE** — official 9B is gated; no smoke until the BFL gate and Derrick GO.
- **SKIP-INHERIT-MAX-ARGV** — Max fp8 CLI-OFF is not the Flux FP8 stills lane; use TECH-ARGV-FLUX instead.
- **Peel-NODDV** is a **STABILITY_HOLD / DISPUTED** path, not a quality KNOWN_FAIL; peel one axis at a time only after the hybrid TECH cell fails.

## Same-clip **speed ranking** set (draft — after Max)

Mirrors Max Gemini amend: exclude product-changing knobs from speed crown. **Required pre-cell 0b: TECH-ARGV-FLUX** — recycle TR, then test `--fp8_e4m3fn-unet --fp8_e4m3fn-text-enc --lowvram` plus the NODDV triad; HostBuffer → STOP.

| Order | Cell | Why |
|-------|------|-----|
| 0 | **BASE** | klein 4B distilled FP8 HAVE · 4 · CFG1 · euler + **Flux2Scheduler** · 1 ref · locked Cond-native÷16 (**P163: 1792×1008**) · Sage/ck OFF · cache OFF · Flux TECH argv |
| 1 | OPT-SAGE | `--use-sage-attention` ON vs OFF |
| 2 | OPT-CKATTN | `--use-ck-attention` ON vs OFF (no early KEEP) |
| 3 | OPT-COMPILE | torch.compile / Compile Model ON vs OFF (warm wall) |
| 4 | OPT-SCHED | Flux2Scheduler vs simple |
| 5 | OPT-NVFP4 | if weights HAVE — else SKIP until download |

**Product / ID cells (not speed winners):** base vs distilled · 4B vs 9B NSFW · ref count · res climb · unlock INSTRUCT · Kontext vs Klein host.

**Near-miss report (optional):** TeaCache CPU-cache · CFG 1.5 · **NM-STEPS-GT4-DIST (steps 5–8; expect FAIL quality)** — only if Derrick wants visible worse+faster rows. Do not hide faster+worse results.

---

## What community does vs what we should copy

| Community habit | Copy? |
|-----------------|-------|
| Use Klein **distilled 4-step** as daily driver | **Yes** — consensus |
| Enable Sage node “because template has it” without A/B | **No** — fair ON/OFF |
| Stack TeaCache + compile + Sage + Turbo | **No** — draft stack; Integrity suicide for KEEP |
| Run Dev Turbo+GGUF on 16 GB and call it Flux2 quality | **No** as primary; optional draft lane |
| Raise steps on distilled when image “looks soft” | **No** — KNOWN_FAIL; switch to **base** instead |
| Fair one-axis A/B with same seed/Cond | **Yes** — our matrix rule (community rarely does) |

---

## Implications for DRAFT matrix (no Dial execute)

1. **Max matrix first** — Flux2 DRAFT stays parked.  
2. **BASE = klein 4B distilled FP8 HAVE**, euler + **Flux2Scheduler**, locked Cond-native÷16 (**P163 1792×1008**) — Integrity SoT; **4B is speed BASE only**.  
3. Smoke only **DISPUTED** speed levers; **SKIP** known-fails.  
4. Report **near-miss** faster+worse if run.  
5. Run mandatory **TECH-ARGV-FLUX** after a full TR recycle: fp8 CLI ON + lowvram + NODDV triad; HostBuffer → STOP; never inherit Max fp8-OFF.  
6. No Dial ping from this research pack.

---

## Changelog

| When_CT | Change |
|---------|--------|
| 2026-10-02 ~10:35 | Initial research write — executor; no Dial |
| 2026-10-02 ~10:55 | CAPA-1..5 applied: Flux2Scheduler/1792×1008 BASE, TECH-ARGV-FLUX, 4B speed banner, HAVE gates, attn VOID + optional NM-STEPS-GT4; still DRAFT/no Dial |
