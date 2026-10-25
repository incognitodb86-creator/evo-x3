# Face lock on MiniMax-H3 / 10Eros-Max beta6: LoRAs, adapters and other methods (2026-10-10)

**Scope:** AlienPc RTX 5070 Ti 16 GB, ComfyUI 0.38, TenStrip 10Eros-Max H3 beta6 int8 (REF2VA hybrid), Euler/simple, 8 steps, shift 10/3, 768 short edge, 5-10 s, 1-2 refs + `MiniMaxH3AddGuide` frame-0 pin. All subjects are fictional adults.
**Problem:** faces drift after head turns and spins (LP10: holds 0-4 s, drifts 6-9 s after the spin); with two refs the second face is weaker (TR1: blonde 7, brunette 6).
**Builds on (not repeated):** `2026-10-09-h3-face-lock-prompting.md` (label rules, turn budget, steps, pin, face size, ref_image_size arithmetic), `2026-10-05-max-h3-face-lora-hunt.md` (LoRA landscape, Ostris, fal), `2026-10-06-face-detailer-ab-480-eyes.md` (CodeFormer / Impact detailer lanes), fix-test round 1 review `cos/brain-staging/60_reviews/max-clips/2026-10-10-fixtest-stills.md`.
**Labels:** [OFFICIAL] docs or source · [AUTHOR] tool author · [COMMUNITY] user report · [INFERRED] our reasoning. Access 2026-10-10 ~7:40-8:10 AM CT.
**Excluded on purpose:** real-person / celebrity-named LoRAs and RefMods (incl. the real-person-named H3 LoRA listed in the 10-05 hunt and most of the malcolmrey RefMod library). Any LoRA or RefMod we make is for an original fictional character only.

---
## 0. Direct answer: is there a face-lock LoRA for H3?
**No.** There is no generic "face-lock" / identity-consistency LoRA for H3 (Comfy-Org `loras/` = turbo only; TenStrip ships full checkpoints; Civitai/HF searches turn up per-character LoRAs, FaceSwap / Character-Swap LoRAs, and anatomy/style LoRAs only). What exists instead:
1. **Per-character LoRAs**: you train one per character (ai-toolkit `minimax_h3_ref2va`, fal trainer). On a REF2VA model they add little on top of a good reference (note.com A/B: "honestly the same… can't tell the difference" at 0.7/1.0) [COMMUNITY], but "RefMod + identity LoRA beats either alone" (malcolmrey Jinx test) [COMMUNITY].
2. **RefMods** (`ComfyUI-MiniMaxH3Mod`): a ~1-1.6 MB no-training "reference latent adapter" you extract from your own images in seconds. This is the closest thing to a loadable face-lock file. [AUTHOR]
3. **FaceSwap / Character-Swap LoRAs** (UntMods, akatz): video-to-video re-facing, a different job (needs a source video).
4. **H3-FaceRefine**: a post-pass that re-renders the face crop with H3 using the reference. Not a LoRA but the most direct fix for a drifted face window.
Wan / Hunyuan / CogVideoX identity adapters (Stand-In, Lynx, MAGREF, Phantom, ConsisID, HunyuanCustom) and image adapters (IP-Adapter FaceID, PuLID, InstantID) are tied to their own model and **do not load on H3** (33B single-stream DiT, Qwen3-VL TE). Their only role here is making better *stills* (refs, guide frames, LoRA datasets) on an image model.

---
## 1. New facts this turn (corrections to earlier notes)
1. **Reference token arithmetic was 4x too high.** H3 = 16x VAE + 2x2 patch, so **32x32 px per token** (Ostris docs: 1344x768x124f = 37,296 tokens; a 1024x1024 still = 1,024 tokens) [OFFICIAL-ish, Ostris]. Our two-ref files (244x192, 262x172; `match`/`max` never upscale) give **~40-50 tokens per face**, vs ~1,000 for a 1 MP ref. The second face is described by about 40 tokens. Fixing this is cheap. [INFERRED from source + Ostris]
2. **`max` is NOT a no-op for the pool start image.** COND_POOL_BIKINI_PORTRAIT.jpg is 1536x2752 (4.2 MP). `match` cuts it to ~1.06 MP (~1,030 tokens); `max` (2048 short-edge cap) keeps it whole (~4,130 tokens). That is about +8% sequence on a 5 s 768x1376 clip (~38k tokens), +4% on 10 s (~74k). The 10-09 "max is a no-op" finding applied to the elf and two-ref files only. [INFERRED from source]
3. **Mid-clip guides work in stock Comfy.** `comfy/ldm/minimax/model.py` (master, 2026-10-08) places every keyframe at `cursor + FRAME_RESCALE * resolved_frame_index`; `MiniMaxH3AddGuide` accepts any `frame_idx` (negative = from end) and only checks the range. The Comfy Multiframe template pins 1.5 s / 3.0 s / 5.0 s. (joeygambino's "stock only supports first/last" note is about an older build.) [OFFICIAL source + docs]
4. **`MiniMaxH3AddGuide` has no strength input** (inputs: positive, vae, audio_vae, latent, image, audio, frame_idx). The 10-09 Cell 3 "strength 1.0" was wrong. A guide pins a whole frame's composition, so a face-crop guide would cut to a close-up; use face crops as **refs**, full frames as **guides**. A Picture used only on Add Guide is invisible to the TE; plug it into `ref_images` too if the prompt cites it. [OFFICIAL]
5. **Reddit is reachable via Apify `trudax/reddit-scraper-lite`** (startUrls or searches; ~$0.01/run). The 10-09 note said all routes failed.

---
## 2. Ranked methods

| # | Method | Fits H3 beta6 on 16 GB? | Files / nodes (size) | Expected gain | Cost | Evidence |
|---|---|---|---|---|---|---|
| 1 | **Motion staging: no 180° spin; hip turn / over-shoulder look with face to lens; small expressions; one motion** | Yes, prompt only | none | **High** on the 6-9 s post-spin drift (the face leaves view and has to be rebuilt) | 0 | Fix-test VR-4: "a 180-degree turn breaks face lock"; F1 face-to-lens BEATS C0R; r/comfyui 1vm8j2c; note.com さっしゅ "request a half-turn"; Reddit 1vqy9bn "stacking two or three actions… pulls the face apart fastest" [COMMUNITY + our A/B] |
| 2 | **Bigger reference pixels: resize the small refs to ~1280 px long edge; for the pool, `ref_image_size=max`** | Yes; +~2k tokens (two-ref) / +3k (pool) | none (offline Lanczos; optionally a face crop) | **High for the weak second face** (40 → ~1,000 tokens); medium for pool | +5-15% time (Reddit: +40-70 s) | Reddit 1vqy9bn "resize each image to 1280 by LONGER EDGE… face consistency improved DRASTICALLY"; 1vjw7pj "below 1 megapixel will look weird"; personmuc "match→max… significantly enhances facial accuracy"; Comfy wiki "max… stronger identity fidelity" [OFFICIAL + COMMUNITY] |
| 3 | **Face block in subject_definitions + short "same face" anchor per beat; differentiating descriptors for two subjects; Subject-cited pictures; one retention line per Subject** | Yes, prompt only | none | Medium-high (TR1 labels already +1 on both faces) | 0 | Official H3 ref guide §5.3; ai-muninn "a label carries no identity, restate"; acedelgado RefMod post: "oval face" vs "more squared jaw" as differentiators cut bleed; TR1 BEATS TR0 [OFFICIAL + COMMUNITY + our A/B] |
| 4 | **Extra guide frames: last-frame (or ~7 s) guide of the end pose with the face to lens** | Yes; one extra latent frame (~1k tokens) | 2nd `MiniMaxH3AddGuide` (stock) + one still | **High for 10 s** (gives the model a future target) | ~+3% time + making the still | r/comfyui 1vo6enw "first-frame only… face slides… double anchor fixes it (−0.53 → −0.10)"; TenStrip LTX page "have a guided endframe"; Comfy multiframe template [OFFICIAL + COMMUNITY + AUTHOR]. Caveat: Reddit 1vqy9bn user saw faces change when chaining "last frame as reference" across clips: use the guide, keep the original ref as identity |
| 5 | **Steps 8 → 12 (→ 20)** | Yes | none | Medium for identity on long/turning clips; ST12 = detail win | +50% (12), +150% (20) | Comfy: "at 4 steps a reference can end up barely applied… run 20; if it still drifts, 25"; Reddit Przemoo_TV "int8, 0.4 MP, image max, 20 steps… face consistency is perfect"; beta6 author band 8-12 [OFFICIAL + COMMUNITY] |
| 6 | **Same-character face crop as an extra ref ("face comes from <Picture 2>"); or a front/three-quarter/profile sheet of the same fictional character** | Yes; +~1k tokens per ref | a ≥1 MP face crop or sheet (make with Flux 2 Klein from the start image) | Medium-high for turns (gives the model the angles it lacks) | small; sheet takes a Flux run | virse "rear view for turning shots"; zodiacrenders "front + side + 3/4 in ONE image"; orlandogourmet66 "2 pictures per character: face close-up + body"; 1vojyye "face comes from <Picture 2>" [COMMUNITY] |
| 7 | **H3-FaceRefine post-pass** (track face → crop to 768 canvas → re-render with H3 + the reference → stitch back) | Yes: same H3 model, canvas capped at 768 (`auto_capped_768`) | `git clone https://github.com/Carasibana/ComfyUI-H3-FaceRefine` (v1.1.x; nodes: H3 Face Track + Crop, H3 Inject Video Latent, H3 Per-Frame Denoise, H3 Face Stitch Back, optional H3 Face Mask (SAM) needs Impact Pack) + `face_yolov8m.pt` (~52 MB; **already on AlienPc** per 10-06 errata) | **Medium-high on the drifted 6-9 s window** (re-imposes the ref on frames where the face is visible); does nothing where the face is turned away (those frames fade to original) | ~+60-100% of a gen (second H3 pass, smaller canvas) | Author README; r/StableDiffusion 1vn4uho "Minimax H3 Face detailer"; phosphene/Ai-Hakase write-up [AUTHOR + COMMUNITY]. Untested on 10Eros beta6 |
| 8 | **RefMod (no-training identity adapter)** | Yes; tokens ≈ refs; 16 GB fine | `git clone https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod` (v0.2.x, "under construction", Windows tested; nodes: Create H3 RefMod / Master, Load H3 RefMods, Apply H3 RefMod (Cond), H3 RefMod Step Curve); files 1-1.6 MB in `models/refmods/`; build your own from the fictional character's images (`encode` mode 1024 px for identity; 40 images took 18 s) | Medium; reported "RefMod + identity LoRA beats either alone"; improved TE path (Adudeguyman Fantastic PromptBuilder) claims less bleed | install + minutes | Comfy wiki news 2026-09-07; author docs; Reddit 1weh5gg, 1wtu82e; skeptic PxTicks "no controlled comparison" [AUTHOR + COMMUNITY, weak controls] |
| 9 | **Original-character LoRA on H3 ref2va (ai-toolkit)** | Training: yes with the 12 GB recipe (7.4 GB VRAM, ~22 GB RAM). Inference: LoRA ~150 MB, fine. **Compat risk:** trained on stock `ref2va_pruned`; beta6 is an fl2va-base graft, so effect may differ | ai-toolkit arch `minimax_h3_ref2va`, rank 16, adapter `ostris/minimax_h3_training_adapter/minimax_h3_ref2va_training_adapter_v1.safetensors` (155 MB), base `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (20.97 GB) + TE nvfp4 (15.69 GB) + VAE (5.21 GB); low-VRAM staged-cache recipe github `ai-toolkit-low-vram-lora-recipes` (note.com かみもと) | **Low-medium** on top of good refs (note.com A/B near-identical); higher when refs are weak or for T2V | ~3 h per 1,000 steps at 512 px on a 4070 12 GB (5070 Ti faster); dataset of 3 refs + ~100 targets of the fictional character | Ostris docs [OFFICIAL]; note.com 2026-08-16 [COMMUNITY, anime test]; 10-05 hunt; Reddit "H3 is a hard model to work with for LoRA training" [COMMUNITY] |
| 10 | **Sampler res_multistep + beta** | Yes | none | Low-medium | 0 | Comfy wiki: "tends to outperform simple for reference-heavy prompts" [OFFICIAL wiki]; untested on beta6 |
| 11 | **FaceSwap_MiniMaxH3_REF2VA as a re-face pass** (our own clip as the source video + start-image face as identity) | Partly: a 10 s clip as video ref doubles the sequence → tight on 16 GB; 5 s OK | `SS_FaceSwap_MiniMax_H3_REF2VA.safetensors` (63 MB) + CRT-Nodes + VideoHelperSuite; trigger `Faceswap`, 0.7-1.0 | Medium in principle; whole-clip re-render, risk to motion/body | ~1 full gen | ComfyUI wiki 2026-09-20; author [AUTHOR]; tested on stock ref2va, not beta6 |
| 12 | **Classic 2D face restore (CodeFormer / GFPGAN / Impact Detailer For AnimateDiff)** | Yes (already installed, 10-06) | see 10-06 note | Low for drift (restores detail, does not pull identity back to the ref; redraws eyes) | small | 10-06 note [INFERRED + COMMUNITY] |
| 13 | **Wan/Hunyuan/CogVideoX identity adapters** (Stand-In 153M on Wan2.1-14B; Lynx ByteDance on Wan2.1; MAGREF, Phantom on Wan2.1; ConsisID on CogVideoX-5B; HunyuanCustom) | **No** (architecture-bound) | n/a | n/a for H3. Only path: switch models (Wan 2.2 14B I2V needs GGUF Q4 on 16 GB) | high | arXiv 2508.07901 (Stand-In), 2509.15496 (Lynx), 2505.23742 (MAGREF); r/comfyui 1pvvd6l "Stand-In best ID control vs VACE & Lynx" |
| 14 | **Image identity adapters** (IP-Adapter FaceID, PuLID / PuLID-Flux2, InstantID) | **No** in H3; **yes** for stills | e.g. `wandrzej/ComfyUI-PuLID-Flux2` (see 10-06 Klein note) | Indirect: better refs, angle sheets, guide frames, LoRA datasets for the fictional character | Flux time | 10-06 flux-e1b note; r/comfyui 1wt9y1m "pulid node acts like a clamp" (image models) [COMMUNITY] |

**Also confirmed (cheap hygiene, from community):** frontal, evenly lit, unoccluded refs ("no hair across the jaw"); keep refs and output close in aspect; turbo LoRA and cache/spectrum accelerators hurt reference adherence (WholeBrain9977: "the problem was the custom workflow… and the turbo Lora"); shorter clips drift less ("three short clips stitched… beat one long one").

---
## 3. Why the two failures happen (updated)
- **Post-spin drift (LP10 6-9 s):** a 180° turn takes the face out of view for ~1 s; when it comes back the model rebuilds it from ~1k ref tokens at 8 steps with no future anchor. Fix order: stage without the full turn (prompt) → end/mid-frame guide → more steps → FaceRefine on what's left.
- **Weaker second face (TR1):** REF2 is a 262x172 file (≈40 tokens), tilted, chin-down, lowered lids, crop ending at the chin; REF1 is similar in size but more frontal. The first fix is pixels, then a contrast-led description. The slot-order diagnostic (A4) separates "slot 2 is weaker" from "this image is weaker".

---
## 4. Recommended next test cells (one change each vs a control; seed 43029049; Euler/simple 8 steps unless the cell says otherwise)
Full list with exact wiring: `/workspace/maxops/facelock-v2-2026-10-10/README.md`.
1. **A0 / A1 / A2: prompt package** FV2_C0R vs P1, FV2_LP10 vs LP10, FV2_TR1 vs TR1 (prompt-only bundles: face block + anchors + hip turn + sheer + light + pin).
2. **A3: two-ref refs resized to 1280 px long edge** (control = A2 winner). Highest expected gain for the brunette.
3. **A4: two-ref slot swap** (diagnostic).
4. **A5: pool `ref_image_size=max`** (control = A0 winner).
5. **A6: 10 s at 12 steps** (control = A1 winner).
6. **B1: 10 s end-frame guide** at frame_idx -1 (still = a good ~6 s frame from the A1 run, or a Flux 2 Klein edit after Flux finishes).
7. **B2: pool face-crop ref** as ref_image_2, "whose face comes from <Picture 2>".
8. **C1-C3 (GO needed):** H3-FaceRefine post-pass on the A1 output; RefMod built from the fictional character's own images; original-character LoRA last.
Score face at 0/2/4/6/8/10 s against the clip's own frame 0 (same-face consistency), plus the existing VR scores. n=1 seed = directional; re-run the winners on 2 more seeds.

---
## 5. Sources (accessed 2026-10-10 CT)
Official / source
- Comfy H3 guide (steps, LoRA build matching, turbo cost): https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- MiniMaxH3AddGuide node doc: https://docs.comfy.org/built-in-nodes/MiniMaxH3AddGuide
- Multiframe Reference workflow: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe
- ComfyUI source `comfy/ldm/minimax/model.py` (master, commit 62c49c4d 2026-10-08), `comfy/model_base.py`, `comfy_extras/nodes_minimax_h3.py` (box copy /tmp/te/comfy)
- Ostris ai-toolkit MiniMax-H3 Ref2VA: https://ostris.com/docs/ai-toolkit/models/minimax-h3-ref2va
- ComfyUI wiki H3 R2V guide (max vs match, res_multistep): https://comfyui-wiki.com/en/tutorial/advanced/video/minimax/minimax-h3
Tools / authors
- H3-FaceRefine: https://github.com/Carasibana/ComfyUI-H3-FaceRefine (README v1.1.2)
- RefMods: https://github.com/Luisacaotica/ComfyUI-MiniMaxH3Mod ; https://comfyui-wiki.com/en/news/2026-09-07-minimax-h3-refmods ; https://huggingface.co/datasets/malcolmrey/various (h3-center/docs)
- Fantastic MiniMax-H3 PromptBuilder (improved RefMod TE path): https://github.com/Adudeguyman/ComfyUI-Fantastic-MiniMaxH3-PromptBuilder
- FaceSwap LoRA: https://comfyui-wiki.com/en/news/2026-09-20-h3-faceswap-lora
- Multishot / keyframes workflow: https://huggingface.co/joeygambino/MiniMax-H3-Multishot-Workflow
- note.com かみもと, 12 GB ref2va character LoRA: https://note.com/sepiablue/n/n67e809a90956
- Stand-In https://arxiv.org/html/2508.07901v4 · Lynx https://arxiv.org/html/2509.15496 · MAGREF https://arxiv.org/html/2505.23742
Reddit (via Apify trudax/reddit-scraper-lite)
- r/StableDiffusion 1vqy9bn "I get different face every time using Ref2Vid" (resize to 1280; start frame; frontal refs; one motion)
- r/StableDiffusion 1vquf9x "How do I maintain facial likeness" (20 steps + max; turbo LoRA and custom nodes were the problem)
- r/StableDiffusion 1weh5gg (RefMod how-to; 40-image RefMod 1.33 MB, 18 s), 1wtu82e (improved RefMods, differentiator descriptors), 1wwyva2 (RefMod location; skeptic note)
- r/comfyui 1wt9y1m (two-stage identity, PuLID on image models), 1pvvd6l (Stand-In vs Lynx), r/comfyui 1vo6enw (double anchor, from 10-09 note)
Local
- Fix-test review: /workspace/cos/brain-staging/60_reviews/max-clips/2026-10-10-fixtest-stills.md
- Prompts + face blocks: /workspace/maxops/facelock-v2-2026-10-10/
