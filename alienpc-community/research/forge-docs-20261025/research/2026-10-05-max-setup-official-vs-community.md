# RESEARCH — Max / MiniMax-H3 REF2VA setup vs official + community — 2026-10-05

**When_CT:** 2026-10-05 ~8:42 AM CT (America/Chicago)  
**Ask (Derrick):** Are we running the best setup based on official documentation? What about community guidance?  
**Scope:** Local KEEP/experimental + Comfy MiniMax H3 tutorial + MiniMaxAI model card + MiniMax API guide + opened community pages. No AlienPc Shell. No skill/Jobs edit. No invent numbers. Adults 21+ fiction I2V / REF2VA only.

---

## Lead answer

**PARTIAL.** Argv and sampling (NODDV / no-fp8 / ck-attn / beta / 25 / res_multistep / match / sigma 12/3) are a fair fleet KEEP with one deliberate scheduler diverge from the official Comfy template. The production **canvas 864×480 is not the official quality canvas** — official open weights and MiniMax model card default the short edge to **768**. Soft mush at 864×480 matches official “soft frame = resolution first.” TRY-NEXT native ~768 is the official-aligned quality move; Remacri after a native survivor only.

---

## TLDR (8 lines)

1. **Official Comfy + MiniMaxAI:** native quality = **~768 short edge** (~1 MP; 1344×768 @ 16:9); soft = resolution first; sampler **`res_multistep`** + scheduler **`simple`**; Lightning off → **20** steps, raise to **25** if reference drifts; sigma **12 / 3**; `ref_image_size` default **`match`**.
2. **Fleet KEEP:** same sampler + sigma + match + **25** steps + ck ON + NODDV/no-fp8; scheduler **`beta`** (not simple); canvas still **864×480**.
3. **Best per official?** **No on canvas.** **Yes/near on steps-for-ref, sampler, sigma, match.** **Partial on scheduler** (beta wins fleet fair wall; official template is simple).
4. **Community:** Image Studio / edge-dit quality path = `res_multistep`+`simple`+20 (+768 recommended). Civitai low-VRAM / Director packs often ship **864×480 + 25 + simple** and push Sage/Turbo — speed/VRAM, not official quality SoT.
5. **Sage:** official docs recommend it for ~2× speed; fleet **DROP/skipped** after speed matrix; community often ON. Do not reopen without Derrick GO + fair pack.
6. **DROPs still hold:** STEPS-20, SPARSEsol, Sage, fp8, Lightning 4-step R2V — official warns Lightning starves R2V refs; fleet measured STEPS-20 under-denoise and SPARSEsol slower.
7. **Hosted API** only exposes **768P / 2K** + duration — no steps/scheduler knobs; 2K is regenerate-from-768, not open-weight native.
8. Dial packing **NE768** with KEEP argv untouched is the right next axis per official.

---

## 1) Our claimed defaults (local only)

| Claim | Source |
|-------|--------|
| Production argv: NODDV triad + no-fp8 + `--use-ck-attention` | `max-8189-production-keep.md` |
| Workflow: scheduler **beta** · **25 steps** · `res_multistep` · REF2VA match · **864×480** · 124f (until GO) | same · `alienpc-local-video-ops/SKILL.md` · hardcore director SKILL |
| Fair warm SoT: beta **125.5s** vs simple **135.4s**; Integrity ≈BASE → beta KEEP | `SCOREBOARD_MATRIX.md` OPT-SCH-WARM-BETA |
| DROP: STEPS-20 (under-denoise), SPARSEsol (slower), Sage skipped, Turbo/Lightning/fp8/DynVRAM | keep + `experimental-do-not-default.md` |
| Hardcore: 480 = preview; native short edge ~768; Remacri does not invent detail; `ref_image_size=max` = identity test | `alienpc-hardcore-i2v-director/SKILL.md` |
| Prior research already: TRY native ~768; Remacri after survivor; KEEP argv | `/workspace/cos/research/2026-10-05-max-ref2va-sharper-quality-settings.md` |

---

## 2) Official documentation (opened)

### ComfyUI MiniMax H3 tutorial
https://docs.comfy.org/tutorials/video/minimax/minimax-h3

| Topic | Quote / fact |
|-------|----------------|
| Native canvas | Open weights: **768px short edge** (~1 MP) @ 24 fps ~15 s. Full-quality 16:9: Megapixels **0.98** → **1344×768**. Skip 1.0 MP (1376×768) over 768×1344 area cap. |
| Soft frames | “Frames well above the native canvas do not hold detail… a soft frame is a **resolution problem first**.” Steps do not add sharpness the native canvas cannot resolve. |
| Steps | Lightning off default **20**. If reference still drifts, raise to **25**. Lightning 4-step on R2V starves reference tokens. |
| Sampler / scheduler | Every local workflow: **`res_multistep`** + **`simple`**. |
| Sigma | Model definition: **`shift` 12** / **`audio_shift` 3** (FastH3 distilled uses 10/3 — different checkpoint). |
| Sage | Optional ~2× speed, “minimal quality loss”; install package + patch or `--use-sage-attention`. |
| ck-attention | Documented for INT8 morphing / garbled text when using bf16 + Kitchen backend, or launch `--use-ck-attention` (0.32.0+). Kitchen does **not** support int8-convrot checkpoints (alignment crash). |
| Sparse | Built-in Model Sparse Attention experimental; `sol-attn` for base H3. |

### MiniMaxH3ReferenceToVideo node
https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo

- Defaults: width **1344**, height **768**, length **124**, `ref_image_size` **`match`** (down only to gen area; `max` = 2048 short edge, slower identity).
- Trained length band ~**124–362** frames @ 24 fps.

### MiniMaxAI model card
https://huggingface.co/MiniMaxAI/MiniMax-H3

- “The shorter side is set to **768 pixels by default**.” 2K via **H3-Regenerate-2K** (not open-sourced as local native).
- H3-Base produces **768p**. API/hosted path separates Context-IR + Base + Regenerate-2K.

### MiniMax platform video guide
https://platform.minimax.io/docs/guides/video-generation.md

- Local-relevant: MiniMax-H3 output **768P / 2K**, duration **4–15 s**. No local steps/scheduler/sigma knobs (hosted).
- H3 Max (fal post-train) offers **480P / 768P** — different product; do not treat 480P as H3 open-weight quality SoT.

---

## 3) Community (pages actually opened)

| Source | What it recommends | Role |
|--------|-------------------|------|
| **Civitai** Minimax H3 Multi Ref low-VRAM (Director quick guide) https://civitai.com/models/2862009/minimax-h3-multi-ref-workflow-for-low-vram | Default sampling: canvas **0.4MP 16:9 (864×480)**, 5s/124f, **25 steps**, `res_multistep`+**`simple`**, CFG 1.0, sigma **12/3**. Strongly pushes Sage / Turbo / Spectrum for speed; notes disable Turbo → 20–25 steps. | Low-VRAM / Director pack — **preview canvas matches fleet 864×480**; scheduler **simple** (not beta); Sage opposite of fleet DROP. |
| **edge-dit.cpp** docs https://raw.githubusercontent.com/THU-MIG/edge-dit.cpp/main/docs/minimax-h3.md | Trained/released for **768p**; recommended quality short edge **768**. Sampling path: **`res_multistep` + `simple`**. CLI examples often show **864×480** + 20 steps as a runnable size, not as quality SoT. Ref2VA: `match` vs `max` (Diffusers official path uses 2048 short edge). | Primary implementer doc — aligns with Comfy on sampler/scheduler/768 quality. |
| **ComfyUI-MiniMax-H3-Image-Studio** (GitHub README / forks; sampling table) | Base quality: `res_multistep` + **`simple`** + **20** + 12/3. Native ~1344×768 / 0.98 MP. REF2VA Turbo 4-step = different profile. `match` faster; 2048 short-edge stronger ID. Beta appears in some FL2VA “reference detail” benches — **not** the documented REF2VA quality preset. | Community packaging of official recipes. |
| **Seedance blog** “Best MiniMax H3 Settings…” | Repeats Comfy baseline: 1344×768, res_multistep, simple, 20, shifts 12/3. | Secondary aggregator — cite only as echo of official; not primary evidence. |
| Reddit / Comfy forum primary threads on H3 quality knobs | **NO_DATA** this pass — search did not return a primary Reddit/forum thread that was opened and quoted. | Mark thin. |

---

## 4) Comparison table

| Our setting | Official (Comfy / MiniMaxAI) | Community (opened) | Match / diverge | Action |
|-------------|------------------------------|--------------------|-----------------|--------|
| Canvas **864×480** | Native quality **~768 short edge** (1344×768 @ 16:9). Template ships fast preview; raise MP for full quality. Soft = resolution first. | Civitai Director default **864×480** (low VRAM). edge-dit: 768 recommended quality; examples often 864×480. Image Studio: start ~0.98 MP. | **DIVERGE** from official quality SoT; **MATCH** common low-VRAM preview | **TRY** native short-edge ~768 AR-locked (Dial NE768). Do not crown 480 soft. |
| Scheduler **beta** | Template: **`simple`** | Image Studio / edge-dit quality: **simple**. Civitai Director: **simple**. Beta used in some FL2VA detail tests, not REF2VA quality SoT. | **DIVERGE** from official template | **KEEP** beta for now (fair warm 125.5s vs simple 135.4s, Integrity ≈BASE). Optional later fair A/B at **768** if soft remains — do not invent a flip. |
| Steps **25** | Default 20; **raise to 25** if reference drifts. Lightning off for R2V fidelity. | Image Studio quality 20; Civitai Director 25; Turbo packs 4–8 (DROP for our R2V KEEP). | **MATCH** official “raise to 25 for ref”; diverge from template default 20 | **KEEP** 25. **DROP** STEPS-20 still (fleet under-denoise). |
| Sampler **res_multistep** | Required in every local H3 workflow | Same across Image Studio, edge-dit, Civitai | **MATCH** | **KEEP** |
| Sigma **12 / 3** | Model definition shift 12 / audio 3 | Same in Studio / Civitai / edge-dit examples | **MATCH** | **KEEP** |
| `ref_image_size=match` | Node default `match` | Community: match = speed; max = ID (slower). Diffusers/official ref path often 2048 short edge | **MATCH** default | **KEEP** match unless mid-clip **identity** fails → then fair `max` cell |
| `--use-ck-attention` ON | Documented launch flag / Kitchen backend path | Civitai: Kitchen vs Sage mutually exclusive in some packs | **MATCH** documented option | **KEEP** (fleet fair Integrity ≈BASE, cold −26.3%) |
| NODDV + no-fp8 | Comfy documents fp8 counterparts; Sage needs fp16/bf16; HostBuffer is local | Community uses INT8 convrot widely; Sage ON often | Local evidence KEEP | **KEEP** NODDV/no-fp8 |
| Sage **OFF / DROP** | Official recommends Sage for speed | Civitai “strongly recommended” | **DIVERGE** (fleet measured/skipped) | **DROP** until Derrick GO + fair pack |
| SPARSEsol **DROP** | Official documents sparse as experimental speedup | Civitai adds sol-attn options | Fleet measured **slower** | **DROP** |
| Lightning / Turbo 4-step R2V **DROP** | Official: 4-step starves R2V refs | Turbo packs exist; not quality SoT for base REF2VA | **MATCH** official warning | **DROP** |
| Remacri / upscale after generate | Official: generate at native; upscale separate; cannot recover missing detail | Community refine/upscale nodes exist | Align with “native first” | Remacri **after** native survivor only — not hand/contact fix |

---

## 5) Contradictions (do not collapse)

1. **Official quality canvas (768)** vs **fleet production canvas (864×480)** vs **Civitai low-VRAM default (864×480)** — last two are preview/VRAM, not MiniMax quality SoT.
2. **Official/community quality scheduler = simple** vs **fleet KEEP = beta** — beta won fair wall + Integrity ≈BASE at 480; not proven at 768; not official template.
3. **Official template steps = 20** vs **official “raise to 25 for ref”** vs **fleet 25 KEEP** vs **fleet STEPS-20 DROP** — 25 is the ref-fidelity advice; 20 as fleet default was measured worse for Integrity.
4. **Official Sage recommend** vs **fleet Sage DROP** vs **Civitai Sage ON** — speed vs Integrity/known-risk; do not reopen casually.
5. **Hosted 480P** exists on **H3 Max** (fal) — not open-weight H3-Base quality guidance.
6. **Dial “settings KEEP”** ≠ clip quality KEEP — soft mush at 480 is a Quality break in words; argv GO stands.

---

## 6) Unknowns (NO_DATA — do not invent)

- Fair scored ORC BJ / Max Integrity at **1344×768 or 768×1344 × 362f** on RTX 5070 Ti 16GB with KEEP argv (wall / OOM).
- Whether **beta vs simple** Integrity stays ≈ at **768** (only measured at 864×480).
- Whether ~768 alone clears mushy hands/contact on oral/doggy (no fair scored cell yet).
- Primary Reddit / Comfy forum consensus thread (not opened this pass).
- Hosted Context-IR / Regenerate-2K quality delta vs local Remacri (different product path).

---

## 7) Sources

**Local:**  
`/home/box/agent-data/workflows/alienpc-local-video-ops/references/max-8189-production-keep.md`  
`/home/box/agent-data/workflows/alienpc-local-video-ops/references/experimental-do-not-default.md`  
`/home/box/agent-data/workflows/alienpc-local-video-ops/SKILL.md`  
`/home/box/agent-data/workflows/alienpc-hardcore-i2v-director/SKILL.md`  
`/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md`  
`/workspace/cos/research/2026-10-05-max-ref2va-sharper-quality-settings.md`

**Official:**  
https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo  
https://huggingface.co/MiniMaxAI/MiniMax-H3  
https://platform.minimax.io/docs/guides/video-generation.md  

**Community (opened):**  
https://civitai.com/models/2862009/minimax-h3-multi-ref-workflow-for-low-vram  
https://raw.githubusercontent.com/THU-MIG/edge-dit.cpp/main/docs/minimax-h3.md  
ComfyUI-MiniMax-H3-Image-Studio README / sampling table (GitHub)  
Seedance blog (secondary echo only)

---

*Research only · 2026-10-05 ~8:42 AM CT · no AlienPc Shell · no invent KEEP · settings KEEP = 2026-10-02 Derrick GO · canvas TRY = official native ~768*
