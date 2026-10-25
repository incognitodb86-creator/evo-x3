---
name: AlienPc stills pose-edit prompting
description: >-
  Use before any AlienPc FLUX.2 Klein 9B still: pose/wardrobe edits of a start
  image, per-shot start frames, or a 2x2 storyboard sheet for H3 Ref2VA. Current
  llama-swap setup (2026-10-16), 768x1344 portrait.
---
> Stop rule: if 2+ judges or runs fail the same way, treat it as a harness bug. Before blaming any model, dump one request (image bytes, prompt, max_tokens) and the parser output. Report "harness suspect", not "models failed".
# AlienPc stills pose-edit prompting (Klein 9B)

## When
- A start image needs a **different pose or wardrobe state** before a Max H3 clip (when the change is too big for one 124f Ref2VA clip).
- Making **per-shot start frames** (regression runs G and S).
- Making a **2x2 storyboard sheet** for the Reddit sheet method (run R).
Not for video prompts: use [REF2VA prompt](sand-workflow:ref2va-prompt) and [hardcore I2V director](sand-workflow:alienpc-hardcore-i2v-director).

## Setup (2026-10-16, llama-swap only)
- ComfyUI is reached only through llama-swap: `http://127.0.0.1:8080/comfyui` (model `comfyui_auto`; API key in `director.live.yaml`, never print it). No `:8189`, no `:8188`, no Switchyard.
- Model: FLUX.2 Klein 9B (fp8). Text encoder: the **flux2** encoder; VAE: the **FLUX.2 VAE**. The old defaults (wrong encoder/VAE) give a shape-mismatch error; fixed in `D:\AI\director\src\director\config.py` on 2026-10-16.
- ViMax keyframes use the same model via `CUSTOM_image_generator_comfy_flux_klein.py` in sync submit mode.
- Size: **768x1344 portrait** (or 1344x768 landscape) to match Max video. Never square or smaller sizes. Seed 20261015 for regression tests. If the source differs, resize/crop the reference to 768x1344 first. Measure output (python PIL) before reporting any size.
- Submit with the director's `ComfyClient.run()` (it waits on the sync hold so a llama-swap swap can't kill the job).

## Pose / wardrobe edit prompt
1. Order = importance (Klein reads exactly what you write; word order matters): identity line from image 1 → **the act and the join** → each person's wardrobe → room and light → camera → `Style: … Mood: …` last. [S1, S2] *(join-first order: to test, A/B T2)*
2. Name what stays: same woman from image 1, same face and hair, the kept wardrobe items, same room and light.
3. **One item, one colour, one place.** Write colour + item + where it sits for every item, and never let one adjective cover a list. "gold circlet, gold choker, arm band and wrist cuffs" gave gold cuffs on 8/8 bodies; "a thin gold circlet on her head, a gold choker, a gold arm band on her upper arm, SILVER wrist cuffs on both wrists" gave silver on 7/8 and held on a second beat. [E1] *(tested default)*
4. **Say what is there, not what isn't.** FLUX has no negative-prompt path, and at cfg 1 the negative box is ignored too, so "no tattoos" / "no other jewelry" don't remove anything (tattoo kept on the same seeds after "he has no tattoos"; pendant/bangle on 4/8 after "no other jewelry"). Describe the clean state instead: "his green shoulders and arms are bare, smooth and unmarked", "her neck bare below the choker", "his wide belt buckled flat at his waist". [S3, E2] *(to test, A/B T1)*
5. **Keep each person's items in his or her own sentence**, tied to body parts, with his own materials (brown leather) and a positive head line ("bare head, short dark hair"). Her circlet ended up on the orc, and a silver plate showed on his arm. [S4, E3] *(to test)*
6. **Count and place every hand and leg**: "he has exactly two hands, one holding the back of each of her knees"; "both of her legs visible from thigh to boot". Arm wording fixed hidden arms (S1B02 r5); join and limb wording fixed legs and hand count on S1B05 r7. [E4] *(tested default)*
7. **Make the join face the lens.** Use the LoRA's own position words (SNOFS: "missionary position", "reverse cowgirl position", "doggystyle position", plus "penis" and "vagina") in a full sentence, then say what keeps the sightline open: which thigh is nearest the camera and where it goes ("her near thigh raised toward her chest"), and "the tip of his penis visibly inside her vagina". Both AI_KEEP panels are the S1B08 open-thigh missionary; most c1 fails are a join hidden behind a thigh, a hand or a buckle. [S5, E5] *(to test)*
8. Describe anatomy and fabric honestly (what's under or through the fabric) so Klein doesn't invent coverage.
9. One reference path into the edit (the start image); don't stack extra references.

## Storyboard sheet (Reddit method)
Source: r/StableDiffusion threads 1vecz21 and 1x4cww3. The whole sheet goes into H3 Ref2VA as `<Picture N>`, and each clip's prompt points to its panel with `<Shot Reference N>`.
1. Use **2x2, not 3x3**, at the largest native size (3x3 loses detail you can't upscale back).
2. Prompt the layout first: "a 2x2 storyboard grid of four panels, thin white gutters, same woman, same outfit, same bedroom and lighting in every panel", then describe each panel by position (top-left = shot 1, top-right = shot 2, bottom-left = shot 3, bottom-right = settle/alt).
3. Keep identity, wardrobe state and set consistent across panels; let only the pose and camera change.
4. If you need single panels (for start frames or review), split with existing nodes: Easy-Use `imageSplitGrid` or KJ `ImageGridtoBatch`. XB_ToolBox `XB_StoryboardSlicer` is the community option if installed.
5. Community alternative for one-panel-per-run: Qwen Image Edit 2509/2511 + the Next Scene LoRA (strength 0.7-0.8, prompts start "Next Scene:").

## Checks (every still)
Six yes/no checks, each failure named in words: Identity, Face, Hands, Contact (bodies merging at a join), Wardrobe (state matches the beat), Overall quality. No averages or decimals. The bot names breaks only; it never says PASS or KEEP. **KEEP = Derrick only.** The one rubric (these six + strict additions) lives in `/home/box/agent-data/workflows/alienpc-stills-pose-edit-prompting/references/strict-still-review.md`; Max and every judge load that file.

## Judge harness (vision models)
- Send exactly two images per question, in this order, with this text:
  "IMAGE 1 = IDENTITY REFERENCE ONLY. Use it only for face, hair, body, jewelry, boots. Do NOT judge its pose, clothing or who is beside her.
   IMAGE 2 = CANDIDATE. Judge only IMAGE 2."
- Never remove the reference: Identity and Face checks need it.
- Calibrate before every judged batch: run the judge on 1 known-good and 1 known-bad still. If the verdicts are wrong or reasons cite things not in IMAGE 2, the harness is broken: stop and fix it; don't report judge scores. Only after calibration passes may more vision models join (Derrick 2026-10-16 7:54 PM CT: "judge test first, then all models").
- All-judges-fail-everything or 100% judge agreement on FAIL = harness suspect, not a result.
- Any change to a judge script or judge settings (thinking, tokens, prompt) is a code change: note it in the plan, rerun calibration, and get a review before scores count.
- Prefer a community judge (VLMJudge / Vision LLM Judge node, or 1038lab/ComfyUI-QwenVL with the rubric as system prompt); calibrate with promptfoo llm-rubric cases against llama-swap once image support is confirmed on this box. Face drift: cubiq/ComfyUI_FaceAnalysis FaceEmbedDistance (reference vs candidate) = TECH warn, never a crown.

## LoRA-aware prompting
- LoRA in use → prompt in that LoRA's own example-caption style (trigger words, phrasing, order from its Civitai/HF examples) and start from its published base settings (weight, steps, cfg, sampler). Record LoRA name, hash and settings with the run. Only after that baseline may one setting change per round (see local-video-ops "Fair dial").
- Check the stack against the LoRA author's notes before blaming the prompt. The SNOFS author says to run SNOFS on its own before stacking other NSFW LoRAs or models, and the loop runs SNOFS v1.1 at 1.0 on top of an NSFW merge checkpoint. Candidate arms (current version, strength, steps) are in `/workspace/cos/archive/2026-10-17-skill-edits/proposed3/POSE_LORA_RESEARCH.md`. [S5] *(to test; one variable per arm)*

Sources: S1 BFL Prompt Reference, FLUX.2 [klein] (https://docs.bfl.ml/guides/prompting_unified_reference) · S2 BFL Building a Good Prompt, "put first whatever matters most" (https://docs.bfl.ml/guides/prompting_unified_building) · S3 BFL "Working without negative prompts" (https://docs.bfl.ml/guides/prompting_unified_technical) + BFL skills AGENTS.md (https://github.com/black-forest-labs/skills/blob/master/skills/flux-image-best-practices/AGENTS.md) · S4 BFL Multi-Reference Editing, "say what each image supplies… how the pieces relate" (https://docs.bfl.ai/guides/prompting_editing_multi_reference) · S5 SNOFS model page (https://civarchive.com/models/1972981?modelVersionId=2960556). Evidence E1–E5: loop1017 LOOP_STATE P8/P13/P18 and review.csv rows (see proposed3/DIFF_LIST.md).

## Hard rules
- Adult fiction only. The minors keyword guard stays on; any blocked prompt means stop. Content rules: /workspace/cos/canon/fiction-cond-lock.md and /workspace/cos/canon/cnc-frame-block.md (link only).
- Scout runs can use 1 seed; anything compared fairly uses 3 or more seeds.
- Back up before editing configs. Don't delete files.
