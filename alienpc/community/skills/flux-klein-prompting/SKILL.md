---
name: flux-klein-prompting
description: Write FLUX.2 Klein 9B and Miraclein 4.5 still prompts (T2I, Klein9 RefMod, Klein9 celeb LoRA, ReferenceLatent single-change edit, RefControl pose/layout, and H3Max start-stills). Use before writing or reviewing any FLUX still prompt on X3 (primary) or AlienPc (backup). Not for video prompts (use h3-prompting).
---

# FLUX.2 Klein / Miraclein 4.5 Stills Prompting

Single prompting guide for FLUX.2 Klein 9B / `Miraclein_4.5_9b_NVFP4.safetensors` stills on X3 (primary writer) and AlienPc (backup writer). Templates own UNET, VAE, steps, CFG, sampler, scheduler, and LoRAs — this skill writes **prompt text only**.

## When & Workflow Map

Use for any FLUX.2 Klein / Miraclein 4.5 still or H3Max start-still. Defer video prompts to `h3-prompting`. Locked **S2** (`flux_stills_s2_{kv,bfs}.api.json`, guide in `alienpc-stills-pose-edit-prompting`) stays the production default until `M4` promotes Miraclein 4.5.

| Mode | Template / Candidate | Prompt Topology |
|---|---|---|
| T2I (Miraclein 4.5 / Klein base) | M4 `miraclein_*` candidates (`Miraclein_4.5_9b_NVFP4`); `flux_stills_t2i_klein.candidate.api.json` still loads `flux-2-klein-9b-kv-fp8` (ST4 base) | Pure prose; never mention `"image 1"` |
| Klein9 RefMod / LoRA | M4 Miraclein 4.5 RefMod / `loras/klein9/` candidates | Pure prose; never mention `"image 1"`; light facial detail at retention >= 0.7 |
| Single-change edit | M4 ReferenceLatent edit candidate (or locked S2) | Lead with `"image 1"` + ONE changing axis; keep-locked clause last |
| RefControl pose / layout | `flux_stills_pose_klein.candidate.api.json`, `flux_stills_layout_klein.candidate.api.json` (`refcontrol_v2_poses`) | Open with exact trigger `"apply pose from image 1 with reference from image 2"` |
| H3Max start-still | Any mode above at `768x1344` portrait / `1792x1008` landscape | Match beat-1 pose/wardrobe, natural headroom, zero video triggers |

## Core Rules

1. **Adult 18+ floor (Standing Rule 5):**
   - Explicitly describe every human subject as an adult aged 18+ (e.g., `"adult woman in her late twenties"`, `"adult man in his thirties"`).
   - Youth-coded terms are forbidden. The existing youth guard stays on; if blocked, stop and report — never reword around it.
2. **Positive-only, zero weight syntax, zero buzzwords:**
   - Never use `(word:1.2)`, `((brackets))`, or `[word:0.8]` — Klein's Qwen3-8B tokenizer ignores A1111 weights and feeds brackets as literal noise.
   - Emphasis comes strictly from front-loading (token order) and concrete nouns.
   - Never write negative words (`no`, `not`, `without`, `never`, `don't`, `avoid`, `blurry`, `deformed`, `extra limbs`), tag soup (`8k`, `4k`, `masterpiece`, `best quality`, `ultra detailed`, `photorealistic`, `hyperrealistic`), or multi-word ALL-CAPS blocks.
3. **One cohesive paragraph, 45–80 words:**
   - Write a single natural-language paragraph (30–80 words acceptable for simple single-axis edits).
   - Output prompt text only: zero bullet points, zero JSON braces, zero preamble or word counts.
4. **Grounded, unpolished photography:**
   - Target natural skin pores, real fabric weave, practical room light, and real gravity.
   - Avoid plastic, airbrushed, or glossy CGI phrasing unless explicitly requested.
5. **Still-frame physics only — zero video triggers:**
   - Describe resting posture, weight load, and contact tension — never video motion or follow-through verbs.
   - Never emit video-only LoRA triggers (`r34l1sm`, `hmpussy`, `dynv2`, `hmmotion`).
6. **Explicit wardrobe and anatomy clarity:**
   - State garment states directly (`"bare breasts"` when top is off, `"nude"` when nude) with unobstructed contact geometry.
   - Known Klein `"from behind"` fix: use a side-profile camera and explicit rear alignment (`"groin pressed to her buttocks, shaft entering her from behind, unobstructed contact"`).

## Prompt Priority Order (8 Slots -> 1 Paragraph)

Assemble the paragraph in this exact priority order:

1. Mode trigger or image index + single change *(edit / pose modes only)*
2. Adult subject(s) identity and frame-relative position
3. Support surface anchor and weight load
4. 2–4 defining joint mechanics in plain biomechanical words
5. Resting contact compression and downward gravity drape
6. Wardrobe state and tactile materials
7. Setting and ONE dominant directional light source
8. Camera angle, explicit vertical lens height, and real lens/camera *(followed by keep-locked clause in edit modes only)*

### Pose, Laterality, Camera & Light Discipline

- **Support anchor & weight load:** Klein 9B has no internal prompt upsampler. Name the physical surface holding the body and which limb or hip carries the weight (natural weight shift / contrapposto over stiff 50/50 symmetry).
- **Joint mechanics:** Express 2–4 defining joint positions in concrete plain words (`"torso angled slightly forward, left knee bent at a right angle, right forearm braced flat"`).
- **Resting contact & gravity:** Name surface compression (mattress, cushion, skin), fabric tension, and downward gravity drape of hair and loose cloth.
- **Frame-relative laterality:** Prefer camera/frame-relative cues (`"on the left side of the frame"`, `"arm nearest the camera"`, `"hand closer to the right edge"`) over ambiguous anatomical left/right.
- **Camera & explicit vertical height:** State ONE clear camera angle, ONE explicit vertical lens height (`"at chest height"`, `"at bed level"`, `"at knee height"`), and ONE grounded camera/lens cue (`"35mm film, 50mm lens at f/2.0"`, `"Fujifilm X-T5, 35mm f/1.8"`). Do not stack conflicting shot scales.
- **Light, hex color & signage:** Name ONE dominant practical or natural light source with direction and color temperature. Bind any `#RRGGBB` hex directly to an object (`"charcoal #2E3033 cotton tank"`). Wrap requested signage or text in quotation marks.

## Mode-Specific Rules

### 1. T2I (`Miraclein_4.5_9b_NVFP4.safetensors`)
- Pure natural-language prose.
- Never reference `"image 1"` or edit/keep clauses.

### 2. Klein9 RefMod (`models/refmods-klein9/`) & Klein9 LoRA (`loras/klein9/`)
- Identity and style come from pre-encoded `Klein9RefModApply` latents or Klein9 LoRAs, not raw input images — never write `"image 1"` in prose.
- Live `Klein9RefModApply` retention strings include the number: `"partially_preserved (0.7)"`, `"attribute_transfer (0.4)"`, `"fully_preserved (1.0)"`.
- At retention `>= 0.7`, keep facial biometrics minimal in text so prose does not fight the RefMod latents.

### 3. ReferenceLatent Single-Change Edit
- Pick **ONE** changing axis: `pose`, `wardrobe`, `lighting`, `camera_angle`, or `background`.
- Lead the paragraph with explicit image indexing (`"Show the adult woman from image 1..."`) plus that single change; never open with `"keep everything the same"`.
- End with a short keep-locked sentence that **excludes** the changing axis.
- Always edit from the original conditioning still; reserve tiny-denoise repair passes for 3+ chained edits only.

### 4. RefControl Pose / Layout (`refcontrol_v2_poses.safetensors`)
- Image 1 is the DWPose skeleton; Image 2 is the identity reference.
- Open verbatim with `"apply pose from image 1 with reference from image 2"`, then supply weight load, contact compression, gravity drape, and re-state wardrobe from image 2 to prevent outfit bleed.

## Two-Subject Rule

- Order subjects left-to-right in the frame and introduce **both** adults in one comma-linked opening clause **before the first period** to prevent Klein 9B second-subject identity drop-off.
- Name each person by frame position plus one clear trait (`"the dark-haired woman on the right"`), never `"the woman"` alone.
- Templates for seated or multi-person stills use 8–12 steps; ask for that template (4-step scouts cause anatomy errors).

## H3Max Start-Still Readiness

- Target **`768x1344`** portrait (matches locked B2 canvas) or **`1792x1008`** landscape (all dimensions divisible by 16).
- Match start posture and wardrobe to clip beat 1, leave natural headroom, and keep video-only triggers (`r34l1sm`, `hmpussy`, `dynv2`, `hmmotion`) out of the still prompt.

## Worked Examples (45–80 Words Each)

1. **T2I (Miraclein 4.5):**
   > An adult woman in her late twenties stands on a worn oak floor, weight shifted onto her right hip with her left knee relaxed. Her torso angles toward a tall window, right palm braced on a wooden dresser, dark hair hanging loose over her shoulders. She wears a charcoal #2E3033 cotton tank and denim shorts. Warm late-afternoon window light enters from the left. Medium-full shot at chest height, 35mm film, 50mm lens at f/2.0.

2. **Klein9 RefMod (`partially_preserved (0.7)`):**
   > An adult woman in her mid-twenties sits cross-legged on a linen sofa, weight pressed into the cushions with her hips tilted slightly left. Her torso leans forward, palms braced on the seat beside her knees, hair draping over her collarbones. She wears an open cream shirt and cotton briefs. Warm tungsten light from a right-side floor lamp fills the room. Full-body three-quarter view at waist height, Fujifilm X-T5, 35mm f/1.8.

3. **ReferenceLatent Single-Change Edit (`pose` axis):**
   > Show the adult woman from image 1 kneeling on the quilted mattress, weight settled onto her heels with her torso angled slightly forward, elbows soft, and both palms braced flat on the rumpled cotton sheets ahead of her knees. Her hair hangs downward over her shoulders while the mattress compresses evenly beneath her shins and knees. Keep her face, hairstyle, wardrobe, bedroom setting, lighting, and camera angle from image 1.

4. **RefControl Pose (`refcontrol_v2_poses.safetensors`, two subjects):**
   > Apply pose from image 1 with reference from image 2 for the adult woman in her late twenties on the left and the adult man in his thirties on the right beside a wooden counter. Her weight rests on her left hip, right forearm pressed flat on the counter, wearing her olive cotton tank and jeans from image 2. Cool window daylight enters from the left. Medium-full shot at chest height, 50mm lens at f/2.0.

## Review Rubric

Review every rendered still at full size, one image at a time, using [strict-still-review.md](../alienpc-stills-pose-edit-prompting/references/strict-still-review.md) (checks 1–9; X3 path `/home/evo/AI/community/skills/alienpc-stills-pose-edit-prompting/references/strict-still-review.md`). Bots report broken checks only; `KEEP` is Derrick only.

## Pre-Send Checklist

- Every person is explicitly described as an adult (18+).
- One cohesive paragraph, 45–80 words (30–80 for simple edits), zero bullets or JSON.
- Zero weight brackets, zero negative words, zero buzzwords, zero video triggers (`r34l1sm`, `hmpussy`, `dynv2`, `hmmotion`).
- Support surface, weight load, 2–4 joint mechanics, resting contact/gravity, one dominant light, and explicit lens height are stated.
- Topology matches mode (no `"image 1"` on T2I/RefMod; exact trigger on RefControl; single axis + non-conflicting keep clause on edits).
- Two-subject prompts introduce both adults left-to-right before the first period.
