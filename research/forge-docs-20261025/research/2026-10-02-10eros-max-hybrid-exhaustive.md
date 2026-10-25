# EXHAUSTIVE RESEARCH — AlienPc 10Eros / MiniMax-H3 / Max hybrid — 2026-10-02

**When_CT:** 2026-10-02 ~8:00 AM CT (America/Chicago)  
**Owner:** CoS executor (research-only) · **Machine:** AlienPc `ecc21911-e61e-44fb-80b1-4bbe46bc56bd` · RTX 5070 Ti 16GB  
**Goal framing (Derrick):** ~1-minute hardcore (21+) fiction video · least token/GPU burn · prefer Max if it can hold length+identity+motion **without** a full FLF/Flow stack · LTX already failed the length bar · **Max capability unknown / never fair-proven**  
**SoT B:** Flux+Max `:8189` = PRODUCTION · LTX Recipe B `:8188` = METHOD / fair H2H only (`status/2026-10-02-alienpc-sot-B-flux-max.md`)  
**Scope:** Docs + local inventory + community · **NO Dial ping · NO Comfy smoke · NO invent KEEP**  
**Primary local priors:** `research/alienpc-ltx-stack-2026-09-25/{INVENTORY_10EROS_MAX,RESEARCH_10EROS_MINMAX_HYBRID,AUDIT_10EROS_MAX_SMOKE_READY,RESEARCH_MINIMAX_H3_FL2VA,PLAN_MAX_VS_RECIPE_B_FAIR}_*.md` · `status/ce-brainstorm-ai-porn-director-1min-2026-10-02.md` · `CAPA_MAX_DRIFT_VS_LTX_WORKFLOW_2026-10-01.md`

---

## Setup inventory (our stack — cited)

### Ports / SoT

| Item | Lock | Cite |
|------|------|------|
| Production SoT | **B** — Flux Kontext (stills) + **10Eros-Max / MiniMax-H3** I2V on **`:8189`** | `status/2026-10-02-alienpc-sot-B-flux-max.md` · `audits/2026-10-02-alienpc-stack-A-vs-B.md` |
| Baseline / H2H | LTX Recipe B EnhOFF **`:8188`** — METHOD only, not 1-min product path | same · KEEP_GL_CHOKE L160/L240 lineage |
| Home NSFW batch | **0/10 QUALITY HOLD** | SoT B stamp |
| Max video KEEP | Not until fair program + Derrick exact GO | PLAN_MAX_VS_RECIPE_B · SoT B |

### Hardware

| Item | Value | Cite |
|------|-------|------|
| GPU | RTX **5070 Ti 16GB** Blackwell (NVFP4-capable class) | AUDIT / INVENTORY / RESEARCH_10EROS |
| RAM | ~64 GB | AUDIT_10EROS_MAX_SMOKE_READY |
| Disk (2026-10-01 probe) | C:~94.9 GB free · D:~128.9 · E:~32.3 (LTX vault tight) | AUDIT §3 |

### Weights / TE / VAE on AlienPc (TestRuntime C: — 2026-10-01 refresh)

| Component | Status | Path / note | Cite |
|-----------|--------|-------------|------|
| `10Eros_Max_h3_TURBO-hybrid_beta5_w4a8_14gb_optimized.safetensors` | **HAVE** (~13.04 GB) | TR `models\diffusion_models\` | PLAN_MAX · AUDIT · RESEARCH_MINIMAX_H3_FL2VA |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | **HAVE** (~14.61 GB) | TR `models\text_encoders\` | same |
| `minimax_h3_video_vae_int8_convrot` | **HAVE** (~2.62 GB) | TR `models\vae\` | same |
| `minimax_h3_audio_vae_fp32` | **HAVE** (~0.56–0.58 GB) | TR `models\vae\` | same |
| Stock MiniMax FL2VA/Ref2VA DiT (separate) | **MISS** (use Max hybrid as UNET swap into stock templates) | AUDIT |
| LTX Recipe B `10Eros_v1.2_fp8mixed_learned` | **HAVE** | `E:\LTX_Models\checkpoints\` | INVENTORY / RESEARCH_10EROS |
| Wan2.2 I2V Q5 High+Low + Wan2.1 VAE | **HAVE** on TR · **HOLD** behind Max prep | AUDIT §1.3 |
| Cond trunk P157 / P163 / HC1 | **HAVE** (Desktop FAIR packs) | AUDIT §7.2 · FL2VA research |

### Runtime blockers (still open as of last audit)

| Gate | Status | Cite |
|------|--------|------|
| ComfyUI ≥ **0.30** (native `MiniMaxH3ImageToVideo` / `MiniMaxH3ReferenceToVideo`) | **MISS** at TR **0.22.0** (last probe) | AUDIT Dial exec · RESEARCH_MINIMAX_H3_FL2VA §2 |
| Prefer ≥0.31 W4A8 · ≥0.32 kitchen attn · Multiframe ≥0.34 · Fun ControlNet/sparse ≥0.35 · FastH3 ≥0.36 | Version ladder from Comfy docs | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 |
| USA MiniMax H3 Community License ack | **FLAG / MISS** — Excluded Territories include **USA** | AUDIT §4 · https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE · https://platform.minimax.io/h3-license |
| Derrick explicit **Max GO** | Required before queue | PLAN_MAX · director brainstorm |
| Max C5 fair crown | **VOID** (bookend freeze / IF ladder) | `CAPA_MAX_DRIFT_VS_LTX_WORKFLOW_2026-10-01.md` |
| Fair H2H Max vs Recipe B | **PLAN only** — not executed as product PASS | PLAN_MAX_VS_RECIPE_B_FAIR |

### Naming — three “hybrid” layers (do not conflate)

| Layer | Meaning | Exact artifacts | Cite |
|-------|---------|-----------------|------|
| **A. Product graft** | TenStrip **10Eros-Max** = GST / attention graft of LTX 2.3 + Wan 2.2 + Krea 2 character into **MiniMax-H3** (not LTX LoRA) | `TenStrip/10Eros-Max` | RESEARCH_10EROS · kombitz 2026-09-07 · CivArchive 2851079 |
| **B. File tag hybrid vs TURBO-hybrid** | Non-turbo full-step vs ~4.2 GB turbo-delta **baked in** | `…_hybrid_beta5*` · `…_TURBO-hybrid_beta5*` · our HAVE = **TURBO-hybrid beta5 w4a8** | RESEARCH_10EROS · AUDIT |
| **C. FL2VA↔Ref2VA DiT hybrid** | Runtime/loader splice: FL2VA quality base + Ref2VA `adaln_proj` overlay (community loaders) | scottmudge HybridLoader · ANe5s Combined loader · smhfacct hybrids | GitHub / comfy.icu (web 2026-10-02) |

**Not the same as:** LTX `10Eros_v1.2` CondSafe Recipe B · YT “Ten Eros on Sulphur-2” LTX stack (`status/ce-learned-yt-10eros-2026-09-25.md` = LTX lineage, not H3 Max).

---

## Capability map (modes, lengths, I2V/FLF/ref, strengths/limits)

### Official MiniMax-H3 modes (stock)

| Mode | Meaning | Inputs | Prompt dialect | Comfy node / template | Cite |
|------|---------|--------|----------------|----------------------|------|
| **T2VA** | Text → AV | text only | 3 fields: `integrated_multimodal_description` · `overall_soundscape` · `non_diegetic_music` | `video_minimax_h3_t2v.json` · ImageToVideo in t2va | HF MiniMax-H3 · local `MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_base_en.md` · Comfy docs |
| **I2VA** | First-frame → develop forward | 1 still = first | base-en + first-frame alignment line | `video_minimax_h3_i2v.json` (first only) · `MiniMaxH3ImageToVideo` | same · RESEARCH_MINIMAX_H3_FL2VA |
| **FL2VA** | First+last bookends (LTX “FLF” analog) | 2 stills | base-en dual-picture alignment; prefer **single shot** interpolate | same I2V template + last_frame wired | same |
| **L2VA** | Last-frame land | 1 still = last | base-en last-frame alignment | build from I2V | base-en guide |
| **REF2VA** | Omni-reference identity/style/motion/voice | ≤9 images · ≤3 videos · ≤3 audio · ≤12 mixed | **Six sections:** subject_definitions → summary → retention_analysis → detailed_description → soundscape → music | `video_minimax_h3_r2v.json` · `MiniMaxH3ReferenceToVideo` | HF · ref_en guide · Comfy docs |

**Author (TenStrip) rule for Max:** prefer **REF2VA prompting** even for a single still — “treat i2v as single-image reference”; do **not** classic LTX I2V prose. (CivArchive beta5 card via RESEARCH_10EROS / AUDIT §6.)

### Length / resolution / audio (official + Comfy)

| Spec | Value | Implication for ~60s goal | Cite |
|------|-------|---------------------------|------|
| Official output duration | **4–15 seconds** | **Single Max generation ≠ 1 minute** | HF MiniMaxAI/MiniMax-H3 README |
| FPS | **24** | Frame math = length/24 | same |
| Native canvas | ~**768px short edge** · ~1 MP (e.g. 1344×768 @16:9) | Higher MP ≠ trained detail | Comfy MiniMax H3 tutorial |
| 2K | Hosted **H3-Regenerate-2K** / API — not free local base | Local = 768p class + separate upscale | HF README · Comfy docs |
| Audio | Native **32 kHz stereo** with video | AV product possible; turbo audio failure modes | HF · AUDIT §8 |
| Comfy `length` widget | INT 5–3600 step 17; **trained ~124–362 frames (~5.17–15.08 s)**; **longer untested** | Node *allows* >15s; docs warn untested — **not a proven 60s path** | https://docs.comfy.org/built-in-nodes/MiniMaxH3ImageToVideo |
| API H3-Max (cloud fast) | 5–15 s · 480P/768P · **no middle frames / no multimodal ref video** | Different product from local open weights; useful only as capability reference | Tencent MiniMax API guide (web 2026-10-02) |

### Extended / multi-shot capabilities (community + Comfy beyond base 15s)

| Mechanism | What it does | ~60s relevance | Confidence | Cite |
|-----------|--------------|----------------|------------|------|
| **I2V continuation template** | `video_minimax_h3_i2v_continuation` in Comfy template library | Chain next segment from prior | Med — official template exists; AlienPc unproven | Comfy docs workflow index |
| **Multiframe Reference** | Anchor refs at timestamps along timeline (Add Guide / Multiframe WF) · needs Comfy ≥0.34 | Mid-clip identity beats without classic FLF | Med | Comfy docs · comfy.org Multiframe WF |
| **VideoExtend / patched extend** | Feed prior AV latent tail → next segment | Continuity without full FLF Flow | Med-Low — community backport / fork | comfy.icu MiniMaxH3VideoExtendPatched |
| **Multishot sampler packs** | Chain N shots; trim seam frame; e.g. 30s demo (3×~10s) | Direct analog of “few long shots → 1 min” | Med (demo exists; NSFW Integrity unknown) | HF joeygambino/MiniMax-H3-Multishot-Workflow |
| **Context Segments / Easy packs** | Segment prompts + motion/RGB/soft AV continuity modes | Structured multi-beat 1-min | Med-Low (custom nodes) | nkxx188 ComfyUI-MiniMaxH3-Easy |
| **Fun ControlNet Union** | Drive with pose/depth/canny or inpaint mask · ≥0.35 | Act lock / contact geometry assist | Med | Comfy docs |
| **FL2VA↔Ref2VA hybrid loaders** | Overlay Ref2VA `adaln_proj` (blocks ~25–49 or 45–49) on FL2VA base | One UNET that does I2V quality + refs | Med (community theory; VRAM/Comfy version sensitive) | scottmudge ComfyUI_MinimaxH3HybridLoader · ANe5s Hybrid |
| **10Eros Max Ref2VA builds** | Native TenStrip ref2va restitch or transplant s0.80 | Better REF path than forcing FL2VA hybrid alone | Med | HF Stuubs/10eros_Max_Ref2va · PromptHero beta2 notes |
| **Sparse attention / FastH3** | Speed on long sequences · ≥0.35/0.36 | Makes multi-clip less painful | Med | Comfy docs |

### 10Eros-Max strengths vs limits (author + our audits)

| Strength (claimed / useful) | Limit / failure | Cite |
|-----------------------------|-----------------|------|
| NSFW concept / literal sex motion vocabulary (community + author) | Breast inflate · contact-type teleport (vaginal↔anal) · clothes vanish · blue cast · finger smear · plastic turbo look | AUDIT §8 · RESEARCH_10EROS author rules |
| REF2VA multi-ref identity across segments | Grafted Max can **dilute** per-frame video-ref accuracy vs stock Ref2VA (TenStrip note via Stuubs card) | Stuubs/10eros_Max_Ref2va |
| TURBO-hybrid fewer steps (4–8) once warm | Turbo audio thump/knock; author: non-turbo better for audio; turbo+extra LoRAs risky for i2v | AUDIT · RESEARCH_10EROS |
| Native stereo AV | Audio polish ≠ picture Integrity; mute OK for v1 | director brainstorm |
| Dual-capable hybrid DiT (load into FL or REF templates) | Prompt dialect + node still differ; LTX POS paste fails | RESEARCH_MINIMAX_H3_FL2VA |
| Fits 16GB via w4a8 / NVFP4 / GGUF | W4A8 kitchen CUDA crashes reported → fallback NVFP4/GGUF; INT8 ConvRot poor 16GB default | AUDIT §2 · Comfy Sage/INT8 notes |

### What Max has **not** proven on AlienPc

| Claim | Status | Cite |
|-------|--------|------|
| Fair Integrity ≥ Recipe B KEEP on same Cond/seeds | **UNPROVEN** (PLAN only) | PLAN_MAX |
| Continuous ~60s single generation | **Docs contradict trained range**; untested >362f | HF + Comfy node docs |
| C5 “0.9787 PASS” | **VOID** — near-identical bookends 0.9796 · hostile Face~0.78 · motion FAIL | CAPA_MAX_DRIFT |
| Length ladder / multi-shot 1-min assembly | **Never fair-run** | director brainstorm · this research |

---

## Paths to 1-min goal (ranked by token/burn simplicity)

**Constraint (docs):** one H3 shot ≈ **≤15 s trained**. A ~60 s product **requires multiple generations** (or an untested >15 s experiment). “Without full FLF” means: avoid expensive Flux still farm + LTX-style multi-bookend Flow **until** simpler Max multi-shot fails.

| Rank | Path | What you do | Burn | When it wins | When it dies | Cite |
|-----:|------|-------------|------|--------------|--------------|------|
| **1 ★** | **Max multi-shot chain (simplest AV)** | After env GO: TECH I2VA/REF → fair Integrity @ ~8–15s → **N× segments** (continuation / multishot / last-frame seed of prior) → concat ~4×15s or 6×10s | Low–Med GPU · low still tokens | Identity+thrust hold across seams; REF locks Face | Seam morph · identity drift · contact collapse | Comfy continuation · Multishot HF · director Step 1b |
| **2** | **Max + light per-beat FL2VA** | Same as #1 but each segment gets first(+optional last) still for pose/act beat | Med | Continuity needs stronger pose anchors than REF alone | Still factory cost rises; C5-style identical-bookend freeze if last=first | FL2VA guide · CAPA C5 anti-pattern |
| **3** | **Max REF2VA identity hub + chained motion** | Cond + extra angle refs · six-section retention · segment chain | Med | Multi-angle identity is the hard problem | Diluted Max ref tracking vs stock Ref2VA; prompt complexity | Stuubs · TenStrip prefer REF |
| **4** | **Hybrid FL2VA+Ref2VA loader** | Overlay adaln for refs on FL2VA quality | Med + setup risk | Need both bookends and refs in one DiT | Custom node / Comfy version / VRAM | HybridLoader READMEs |
| **5** | **Untested single `length` >362 frames** | Set length toward ~1440f (~60s) on ImageToVideo | High fail risk · may OOM | Only as **labeled scout** after #1 TECH | Docs: longer **untested**; not a plan-of-record | Comfy MiniMaxH3ImageToVideo |
| **6** | **Flux unlock stills → Max FLF/Flow assembly** | Fair Flux2 stills → wardrobe unlock → full bookend Flow | High token (stills+video) | Max chain fails without strong still tickets | Premature if Max length/chain never probed | director brainstorm deferrals · fair F1 CAPA |
| **7** | **LTX Recipe B multi-segment** | CondSafe FLF / extend chain on `:8188` | Known METHOD · length already failed product bar | Fair H2H baseline only | Not SoT B production for 1-min | RESEARCH_LONGER_VIDEOS_LTX · SoT B |
| **8** | **WAN2.2** | Alternate I2V host HAVE on TR | Parallel stack cost | Only if Derrick flips Max-before-WAN | Explicit HOLD behind Max | AUDIT |

**Explicit non-paths (this dial):** crowning Flux2 cell1 fair-n as the finish line · Face/IF ladder · empty-POS · invent KEEP · Dial ping without Derrick GO · grafting Max into `:8188`.

---

## Best theory (director recommendation + why)

### Recommendation (efficiency-first)

1. **Accept the physics:** Max/H3 is a **≤~15 s native clip engine** (official + Comfy trained range). The 1-min movie is a **multi-clip Max director problem**, not a “one Generate = 60s” problem.  
2. **Do not build full Flux→FLF Flow first.** Derrick’s preference stands *as reframed*: prefer Max **without a whole Flow/still farm** — i.e. Path **#1 multi-shot chain** before Path #6.  
3. **First decisive unknown:** after **Comfy≥0.30 + license ack + Max GO**, run **S0 TECH** then **L1 length/Integrity** at **~8–15 s** on HAVE Cond (P163 BEST class) with **H3 dialect** (I2VA first, or author-preferred REF single-still) — **non-identical bookends**, thrust POS, hostile Identity+Contact+Motion (CAPA C5 gates).  
4. **If L1 PASS:** run **M-chain scout** (continuation or last-frame→next I2VA) for **2 clips → 3 → aim 4×15s**; fair ≥3 only on the locked chain recipe that works.  
5. **If chain fails identity/contact:** escalate to Path #2/#3 (light FL2VA / stronger REF), then only then Path #6 Flux still QUALITY.  
6. **Optional H2H vs Recipe B** after a product-capable Max chain exists — METHOD quality compare, not a blocker to shipping the minute if Derrick only wants the movie (`ce-brainstorm-ai-porn-director-1min`).

### Why this is best theory

| Argument | Evidence |
|----------|----------|
| Single-shot 60s is **not** what docs support | HF 4–15s · Comfy trained 124–362f |
| LTX already failed length for this outcome | director brainstorm · RESEARCH_LONGER_VIDEOS_LTX (extend/chain advice mirrors H3) |
| Multi-shot is the **documented** way communities get 30–60s | Multishot 30s demo · continuation templates · VideoExtend |
| Full FLF Flow is higher burn and was the thing Derrick wants to **avoid if possible** | User t1632 · director efficiency bias |
| C5 proved short identical-bookend FL2VA can **fake** Integrity | CAPA_MAX_DRIFT — must not repeat |
| Weights mostly **HAVE**; env gates are the real block | AUDIT HAVE table · Comfy 0.22 < 0.30 |

### Theory we reject (until evidence)

- “Max 3 can do 1 min without any multi-clip” as **plan-of-record** — contradicts official duration.  
- “C5 proved Max quality” — VOID.  
- “Flux2 fair-n unlock is the goal” — stills are inputs; movie is the goal (Derrick t1630–t1632).

---

## Official documentation (links + takeaways)

| Source | URL | Takeaways |
|--------|-----|-----------|
| MiniMax-H3 model card | https://huggingface.co/MiniMaxAI/MiniMax-H3 | Omni AV · **4–15s** · 24fps · 768p short edge · FL2VA vs Ref2VA variants · Context-IR + Regenerate-2K for full 2K · safety/porn moderation on hosted paths · Community License |
| H3 LICENSE | https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE | **USA = Excluded Territory** — FLAG before local use |
| USA/EU license form | https://platform.minimax.io/h3-license | Ack path called out in AUDIT |
| Prompt skills (official) | https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills | h3-prompt-writing skill · base-en / ref-en |
| Local prompt guides (landed) | `…/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_{base,ref}_en.md` | I2VA/FL2VA/L2VA structures · REF six-section |
| Comfy MiniMax H3 tutorial | https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | Native Comfy ≥0.30 · T2V/I2V/R2V (+ continuation) · Multiframe ≥0.34 · ControlNet/sparse ≥0.35 · FastH3 ≥0.36 · res_multistep+simple · shift 12/3 · Sage Attention notes · int8+Sage morph caveat · commercial local needs MiniMax commercial license via Comfy |
| Comfy `MiniMaxH3ImageToVideo` | https://docs.comfy.org/built-in-nodes/MiniMaxH3ImageToVideo | `length` trained **~124–362**; longer untested; first stretch / last cover crop behavior |
| Stock templates | https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/video_minimax_h3_{i2v,t2v,r2v}.json | Swap UNET to Max quant; no CondSafe/JoyAI/10S |
| Comfy-Org weights | https://huggingface.co/Comfy-Org/MiniMax-H3 | TE + VAEs we already HAVE paths for |
| Platform I2V / FL2V API (Hailuo lineage + H3) | https://platform.minimax.io/docs/api-reference/video-generation-i2v · …/video-generation-fl2v | Cloud duration/resolution matrices (Hailuo 6/10s class; H3 separate 4–15s in guides) — **API ≠ AlienPc local**, use for capability vocabulary only |
| Tencent MiniMax API table | https://intl.cloud.tencent.com/document/product/1300/83715 | H3 vs **H3-Max** cloud: Max = faster/cheaper · no intermediate frames · no multimodal ref video · 5–15s · no 2K |

---

## Community best practices (links + takeaways; mark confidence)

| Practice | Takeaway | Conf. | Cite |
|----------|----------|-------|------|
| Prefer REF prompting for identity | TenStrip: treat still as reference; six-section retention | **High** (author) | RESEARCH_10EROS · AUDIT §6 · CivArchive 2851079 |
| TURBO for speed/T2V; non-turbo for AV quality | Audio thump on turbo; raise audio shift if thin | **Med-High** | AUDIT scout settings · author rules |
| Concept LoRAs (mystic/anatomy) @ **0.2–0.6** | After TECH works — METHOD knob | **Med** | AUDIT §2.6 |
| Avoid cache/spectrum on reference shots | Accuracy loss | **Med** | AUDIT §5.3 |
| Explicit size locks (“petite breasts”) | Counters Max inflate | **Med-High** | AUDIT §8 |
| Literal contact prose > NEG bans | Bans can amplify on H3 | **Med-High** | AUDIT §6 |
| Hybrid loader: FL2VA base + Ref2VA `adaln_proj` blocks ~25–49 (or 45–49) | Quality + reference pathway | **Med** | scottmudge HybridLoader · ANe5s / comfy.icu |
| Native 10Eros Ref2VA > transplant for REF tasks; FL model better for pure image ref | Match checkpoint to task | **Med** | Stuubs card · PromptHero beta2 |
| Multishot: end each shot on what the **next** shot expects; trim seam frame | Invisible joins | **Med** | joeygambino Multishot README |
| Continuation: context_frames small (e.g. 2); optional pin last_frame | Chain longer takes | **Med-Low** (backport maturity) | VideoExtendPatched |
| 16GB: w4a8 14GB or NVFP4-HQ; TE CPU offload; `--lowvram` | Our HAVE matches this class | **High** (local inventory) | AUDIT ranked DL |
| Sage Attention ~2×; disable if INT8 morph/garble | Kitchen attn needs bf16 path | **Med** | Comfy docs |
| GGUF Q5 path for consumer VRAM | Alt if w4a8 kitchen fails | **Med** | Abiray GGUF READMEs |
| Reddit / r/SD discussions | Graft ≠ dataset finetune; FL2VA/Hybrid maze; turbo R2V timing | **Low-Med** (volatile threads) | RESEARCH_10EROS Reddit table |
| Kombitz explainer | GST / cross-model transfer overview; experimental expectations | **Med** (secondary) | https://www.kombitz.com/2026/09/07/10eros-max-the-new-minimax-h3-model/ |
| Motion Director Civit pack | Community wiring example; prefer stock templates first | **Low-Med** | Civitai 2934559 via AUDIT |

---

## Gaps / unknowns for Derrick GO

| # | Gap | Why it blocks 1-min | Suggested ack |
|---|-----|---------------------|---------------|
| G1 | **Comfy TR still <0.30?** (last probe 0.22.0) | Native H3 nodes MISS — weights HAVE but unusable | Confirm current version; upgrade ≥0.30 (prefer ≥0.31 for our w4a8) |
| G2 | **USA H3 license** | Legal FLAG · Excluded Territory | Explicit ack / form / accept research risk |
| G3 | **Explicit Max smoke GO** | Policy gate | Narrow GO: TECH+length probe only |
| G4 | **Native continuous length on our quant** | Docs say ≤15s trained; >362f unknown on w4a8 TURBO-hybrid | Fair L1 @ 8–15s first; optional labeled >15s scout later |
| G5 | **Multi-shot continuity (continuation / Multishot)** | Required for ~60s without Flow | After L1 PASS — chain smoke |
| G6 | **Best Max mode for hardcore Integrity** | I2VA vs FL2VA vs REF never fair-picked post-CAPA | Sub-knob S1–S3 after TECH (PLAN_MAX) |
| G7 | **Hostile motion-amp scoring** | C5 VOID taught auto bookend scores lie | Bot/hostile vision mandatory; no IF crown |
| G8 | **Wardrobe / bare-seam still** | Bare-act briefs may need Flux unlock | Defer until Max chain needs it |
| G9 | **Audio on/off for v1** | Turbo AV failure modes | Mute OK until picture CANDIDATE |
| G10 | **Fair H2H vs Recipe B** | Optional for ship; required if claiming “Max better” | After product-path works |
| G11 | **Ref2VA Max checkpoint on disk** | HAVE is TURBO-hybrid (FL-oriented); dedicated Max Ref2VA may help Path #3 | Only if REF path weak |
| G12 | **Home 0/10 HOLD** | Don’t confuse Dial smoke with home unlock | Keep labels honest |

**No Dial ping this turn.** Draft remains draft until Derrick GO.

---

## Next smokes (narrow, fair)

**Precondition:** G1–G3 cleared · adults 21+ · `:8189` only · single lease · Cond HAVE (prefer **P163 BEST** AR lock) · H3 dialect · **no** Recipe B POS paste · **no** identical first=last bookends · label scout/fair · KEEP=Derrick GO only.

| Order | Cell | Frozen | One axis | Seeds | Pass spirit | Stop |
|------:|------|--------|----------|------:|-------------|------|
| **0** | Env verify | — | Comfy≥0.30 · object_info H3 nodes · w4a8 loads | 0 | Nodes present · 1 dry graph | Abort if MISS |
| **1** | **S0 TECH** | Cond P163 · TURBO-hybrid w4a8 · TE CPU · ~5s · 0.3–0.4 MP · I2VA or REF-single | — | 1 OK | Graph completes · frames land | OOM/node → env FAIL |
| **2** | **L1 Integrity@length** | Host+mode+Cond+POS+sampler from S0 | **Length class only** (~8s → ~12–15s) | **≥3** / class for fair claim | Hostile Identity + Contact + **Motion amp** (thrust readable; n00≠n_end freeze = FAIL) | Soft freeze / anatomy soup = FAIL→RT one knob |
| **3** | **M1 mode** (only if L1 needs it) | Cond+length+seeds policy | **I2VA vs FL2VA vs REF** | ≥3 / mode | Same hostile gates | Lock winner for chain |
| **4** | **C1 chain scout** | Winning L1/M1 locks | Continuity method (continuation vs last-frame seed vs Multishot) | 1 then ≥3 | 2-clip then 3-clip identity hold | Seam FAIL → Path #2/#3 |
| **5** | **C2 minute assembly** | Locked chain recipe | Clip count toward ~60s | ≥3 on final recipe | Product bar from director brainstorm | CANDIDATE only |
| **6** | **Optional H2H** | Same Cond/seeds/length class | Host Max vs Recipe B | Twin ≥3 | METHOD scorecard | Not required to ship movie |
| **Defer** | Flux2 F1-confirm ≥3 | — | — | — | Only if Max needs better still/seam | fair F1 CAPA |
| **Defer** | Full FLF Flow | — | — | — | Only if C1/C2 fail | director Plan B |
| **Never** | Face/IF ladder · C5 re-crown · Dial=home unlock · invent KEEP | — | — | — | — | CAPA_MAX_DRIFT |

### Scoreboard columns (video)

Identity · Contact Integrity · Motion amp · Length/continuity class · Wardrobe/seam · TECH (screening only) · label (scout/fair/CANDIDATE/FAIL/HOLD).

---

## Source index (compact)

**Local:** INVENTORY_10EROS_MAX · RESEARCH_10EROS_MINMAX_HYBRID · AUDIT_10EROS_MAX_SMOKE_READY · RESEARCH_MINIMAX_H3_FL2VA · PLAN_MAX_VS_RECIPE_B_FAIR · MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_{base,ref}_en · RESEARCH_LONGER_VIDEOS_LTX · CAPA_MAX_DRIFT_VS_LTX_WORKFLOW · status/{2026-10-02-alienpc-sot-B-flux-max,ce-brainstorm-ai-porn-director-1min,ce-learned-yt-10eros} · audits/{2026-10-02-alienpc-stack-A-vs-B,2026-10-02-flux2-max-skill-research}

**Official web:** HF MiniMaxAI/MiniMax-H3 · LICENSE · Comfy MiniMax H3 tutorial + MiniMaxH3ImageToVideo node · Comfy-Org templates · MiniMax skills repo · platform API I2V/FL2V · Tencent H3/H3-Max table

**Community web:** TenStrip/10Eros-Max · Stuubs/10eros_Max_Ref2va · DmitryDB / Abiray quants · scottmudge HybridLoader · ANe5s Hybrid · joeygambino Multishot · VideoExtendPatched · kombitz explainer · CivArchive 2851079 · Reddit pointers in RESEARCH_10EROS

---

*Research only · 2026-10-02 ~8:00 AM CT · no Dial ping · no smoke · no invent KEEP*
