# FLUX.2 settings + prompting research (AlienPc :8189, RTX 5070 Ti 16 GB)
Written 2026-10-09 ~22:25 CT by an executor. Tags: **[official]** = BFL or Comfy-Org docs/model cards/repos · **[community]** = Reddit/Civitai/GitHub/third-party guides · **[inferred]** = my reasoning or local run logs, not a published claim · **[local]** = measured on AlienPc in earlier box runs.
Earlier, longer research this builds on (not repeated): `/workspace/cos/research/2026-10-02-flux2-speed-quality-practices.md`, `/workspace/cos/status/RESEARCH_FLUX2_KLEIN_9B_5070TI_2026-10-02.md`.

## 1. Does FLUX.2 do video? No.
- FLUX.2 is an **image-only** family. BFL's capability table lists only Text-to-Image, single-reference Image Editing, and multi-reference Image Editing for every open variant. There is no video variant. **[official]** https://github.com/black-forest-labs/flux2
- Mapping for Derrick's labels: **"t2v" → text-to-image (T2I)**; **"i2v" → reference-image / edit (ReferenceLatent) workflow**. **[inferred]**

## 2. Variants, licence, recommended settings
| Variant | Params | Distilled? | Steps | Guidance | Licence | Notes |
|---|---|---|---|---|---|---|
| [klein] 4B | 4B | step + guidance distilled | **4** | **1.0** (ignored) | Apache-2.0 | ~13 GB bf16 (HF card); Comfy: ~8.4 GB, ~1.2 s on 5090 |
| [klein] 4B Base | 4B | no | **50** | **4.0** | Apache-2.0 | Comfy: ~9.2 GB, ~17 s on 5090 |
| [klein] 9B / 9B KV | 9B | step + guidance distilled | 4 | 1.0 | FLUX Non-Commercial, gated | ~29 GB bf16; FP8 9.43 GB |
| [klein] 9B Base | 9B | no | 50 | 4.0 | FLUX Non-Commercial, gated | FP8 9.57 GB |
| [dev] | 32B | guidance distilled only | 50 (28 "good trade-off") | 4 | FLUX.2-dev Non-Commercial | fp8mixed 35.46 GB + Mistral-Small-3 TE |
Sources **[official]**: https://github.com/black-forest-labs/flux2 · https://huggingface.co/black-forest-labs/FLUX.2-klein-4B · https://huggingface.co/black-forest-labs/FLUX.2-dev · https://huggingface.co/docs/diffusers/api/pipelines/flux2 · https://docs.comfy.org/tutorials/flux/flux-2-klein · https://docs.comfy.org/tutorials/flux/flux-2-dev
- BFL's own pick for a consumer GPU (3090/4070 class): **[klein] 4B**; for LoRA/fine-tune: Base or Dev; for max quality: Dev. **[official]** (flux2 README)
- Guidance is ignored on step-distilled models (Diffusers). **[official]** In ComfyUI, KSampler cfg=1.0 skips the negative/uncond pass, so the **negative prompt does nothing at cfg 1** (earlier runs carried NEG text that had no effect). **[inferred]** from ComfyUI sampler code behaviour.
- BFL says **FLUX.2 does not support negative prompts**: describe what you want ("sharp focus" not "no blur"). **[official]** https://docs.bfl.ai/guides/prompting_guide_flux2
- Resolution: multiples of 16, min 64², max **4 MP**, "recommended up to 2 MP". **[official]** (BFL prompting guide). All approved start images are **768×1376** (÷16 OK, ~1.06 MP). **[local]**
- Sampler/scheduler in Comfy templates: **euler + Flux2Scheduler** (BFL reference uses FlowMatch Euler). **[official]** (Comfy templates; Diffusers `FlowMatchEulerDiscreteScheduler`). Earlier local runs used exactly this. **[local]**

## 3. Files and text encoders (ComfyUI)
| Role | File | Size | Source |
|---|---|---|---|
| VAE (all FLUX.2) | flux2-vae.safetensors | 0.34 GB | Comfy-Org/flux2-dev **[official]** |
| TE for 4B | qwen_3_4b.safetensors (fp4 alt: qwen_3_4b_fp4_flux2 3.85 GB) | 8.04 GB | Comfy-Org/vae-text-encorder-for-flux-klein-4b **[official]** |
| TE for 9B | qwen_3_8b_fp8mixed.safetensors (bf16 16.38, fp4mixed 6.8) | 8.66 GB | Comfy-Org/vae-text-encorder-for-flux-klein-9b **[official]** |
| TE for Dev | mistral_3_small_flux2_fp8 (bf16 35.58, fp4_mixed 12.28) | 18.03 GB | Comfy-Org/flux2-dev **[official]** |
| 4B distilled FP8 / Base FP8 | flux-2-klein-4b-fp8 / flux-2-klein-base-4b-fp8 | 4.07 / 4.09 GB | black-forest-labs **[official]** |
| 9B distilled FP8 / Base FP8 | flux-2-klein-9b-fp8 / flux-2-klein-base-9b-fp8 | 9.43 / 9.57 GB (gated) | black-forest-labs **[official]** |
| NVFP4 (RTX 50 native) | flux-2-klein-4b-nvfp4 / flux-2-klein-9b-nvfp4 | 2.46 / 5.76 GB | black-forest-labs **[official]** |
| Dev FP8 | flux2_dev_fp8mixed | 35.46 GB | Comfy-Org/flux2-dev **[official]** |
| Dev Turbo LoRA (8-step) | Flux_2-Turbo-LoRA_comfyui | 2.76 GB | Comfy-Org/flux2-dev, fal/FLUX.2-dev-Turbo **[official]** — Dev only, not Klein |
- Never mix TE sizes (4B↔qwen_3_4b, 9B↔qwen_3_8b). FLUX.1 `ae.safetensors` is not interchangeable with flux2-vae; use `EmptyFlux2LatentImage`. **[official]** (Comfy docs file map) + **[community]** https://github.com/bako02/flux2-prompt-guide
- Klein LoRAs are trained per size: a 4B LoRA will not load on 9B and vice versa (different widths). **[inferred]** from architecture; verify `ss_base_model_version` / `modelspec.architecture` in each header.

## 4. 16 GB VRAM and speed
- Dev 32B on 16 GB needs heavy offload (35 GB FP8 + 18 GB TE); BFL's consumer example is a 4090 with a 4-bit model and a *remote* text encoder. Treat Dev as off-matrix here. **[official]** (FLUX.2-dev card) + **[inferred]**
- **[local]** AlienPc, `FLUX-KLEIN-9B-FP8-NSFW` + qwen_3_8b_fp8mixed, 4 steps, cfg 1, euler, 1792×1008, 1 ref, argv `--lowvram --disable-dynamic-vram --disable-async-offload --disable-pinned-memory --use-ck-attention`: **48.2 s first image (cold), 15.1 s warm** (`/workspace/overnight_chat/E1b/results.json`, 2026-10-06).
- 4B base at 50 steps: ~17 s on 5090 **[official]** → ~40–50 s on 5070 Ti **[inferred]** (5090 ≈ 2–2.5× faster).
- NVFP4 is the RTX 50 VRAM/speed path; NVIDIA and Comfy claim large gains. **[official]** https://blogs.nvidia.com/blog/rtx-ai-garage-flux-ltx-video-comfyui-gdc/ — not yet tested locally.
- Sage/ck attention, torch.compile, TeaCache: disputed on Klein; keep off the quality matrix. **[community]** (see 2026-10-02 research)

## 5. Samplers / schedulers (community)
- Klein is tuned around **Euler**; it is **scheduler-sensitive**: Karras, exponential and kl_optimal break it; simple / normal / beta / beta57 / bong_tangent are fine. **[community]** https://www.reddit.com/r/FluxAI/comments/1r6m4t5/klein_9b_realism_test_sampler_and_scheduler/
- Klein loses colour on each edit; a **ddpm pass at 0.05–0.08 denoise** restores colour. **[community]** (same thread)
- Klein 9B distilled T2I realism: **res_multistep, cfg ~0.8** reported to reduce plastic skin / fix anatomy. **[community]** https://www.reddit.com/r/comfyui/comments/1ql9pjn/creating_realistic_almost_images_with_flux2_klein/
- Distilled: 4 steps, cfg 1; more steps do not help, and higher cfg breaks output. **[community]** (r/StableDiffusion guide snippet, Apify search 2026-10-09) — agrees with **[official]**.
- res_2s / beta57 need the RES4LYF custom node pack. **[community]** Check it is installed before queueing.

## 6. Prompting
**Official (BFL):** https://docs.bfl.ai/guides/prompting_guide_flux2 · https://github.com/black-forest-labs/skills/blob/master/skills/flux-image-best-practices/rules/multi-reference-editing.md
1. Structure **Subject → Action → Style → Context**; word order matters, and the model weights early tokens most. **[official]**
2. Length: 30–80 words is usually ideal; 80+ only for complex scenes. **[official]**
3. **JSON structured prompts are official** (schema: scene, subjects[{description, position, action}], style, color_palette, lighting, mood, background, composition, camera{angle, lens, depth_of_field}); FLUX.2 "understands both formats equally well". **[official]** (Guide is written for [pro]/[max]; applying it to Klein is **[inferred]**, so test it.)
4. Photorealism: name the camera, lens, aperture or film stock ("shot on Fujifilm X-T5, 35mm f/1.4"). Hex colours work when tied to a specific object. **[official]**
5. No negatives; state the positive (e.g. "empty scene"). **[official]**
6. Reference images: give each image a role and index it ("the person from image 1, the room from image 2"); Klein takes **up to 4 references** (the Comfy doc says FLUX.2 handles up to 10, and Dev ~6). Keep reference lighting and perspective similar. **[official]**
**Community:**
7. Edit template: "Using image 1 as the base, change X to Y. Keep identity, pose, framing, wardrobe… unchanged. Match the existing perspective and lighting." Make one change per prompt. **[community]** https://aireiter.com/blog/flux-2-klein-prompt-guide-image-editing-consistency
8. Counter-view: reference subjects by **visual attributes, not index**; match reference and target latent resolution (`ImageScaleToTotalPixels`), or textures come out baked and over-contrasty. **[community]** https://github.com/bako02/flux2-prompt-guide → this is a matrix axis.
9. LoRAs: put the **trigger phrase first**; strength 1.0 = the trained look, 0.6–0.8 keeps more base style; style LoRAs can be faint on distilled 4B, so try 1.5–2; ≥2 smears on Dev. **[community]** https://spicyapi.ai/models/flux-2-klein-4b-lora · https://spicyapi.ai/models/flux-2-dev-lora

## 7. Top 5 prompt techniques for the matrix
1. Front-load the subject and key action (S→A→Style→Context), 30–80 words. [official]
2. JSON structured prompt as an A/B against natural language. [official; Klein use inferred]
3. Camera/lens/film-stock descriptors for realism, and positive phrasing only (no negatives). [official]
4. Edits: index each reference + one change + an explicit "keep … unchanged" invariant list; match ref and output resolution. [official + community]
5. LoRA trigger first, strength 0.6–1.0 (do not go above ~1.5 on distilled). [community]

## 8. Local workflow JSONs found (box; AlienPc offline)
- `/workspace/flux2_klein_4b_edit_distilled_template.json`: Comfy Klein 4B distilled edit template copy.
- `/workspace/FAIR_FLUX2_KLEIN4B_P163_P188_2026-10-02/` (knobs: flux-2-klein-4b-fp8, qwen_3_4b, 4 steps, cfg 1, euler, Flux2Scheduler, 1792×1008, 3 seeds).
- `/workspace/FAIR_FLUX2_KLEIN9B_P163_ACTFIRST_2026-10-02/` and `/workspace/overnight_chat/E1b/` (FLUX-KLEIN-9B-FP8-NSFW, qwen_3_8b_fp8mixed, 4/1.0/euler/Flux2Scheduler, 1792×1008).
- Runner scripts: `/workspace/MAX_FLUX_E1*_2026-10-0[56]/scripts/*.py`, `/workspace/MAX_FLUX_R1_FACE_768_2026-10-05/`.
- `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/FAIR_FLUX_KLEIN_pack/_fair_flux_klein_lf_runner.py` wires `MS_real_and_Details_klein`.
- (Not read: Grok Imagine prompts/sidecars; the E1C `F4_*` celebrity-try cell was skipped.)
