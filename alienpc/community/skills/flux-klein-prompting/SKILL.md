---
name: flux-klein-prompting
description: Write FLUX.2 Klein 9B and Miraclein 4.5 still prompts (T2I, Klein9 RefMod, Klein9 celeb LoRA, ReferenceLatent single-change edit, RefControl pose/layout, and H3Max start-stills). Use before writing or reviewing any FLUX still prompt on X3 (primary) or AlienPc (backup). Not for video prompts (use h3-prompting).
---

# FLUX.2 Klein / Miraclein 4.5 Stills Prompting

Single prompting guide for FLUX.2 Klein 9B / `Miraclein_4.5_9b_NVFP4.safetensors` stills on X3 (primary writer) and AlienPc (backup writer). Templates own UNET, VAE, steps, CFG, sampler, scheduler, and LoRAs — this skill writes **prompt text only**.

## Still Photographer & Set Lighting Director Persona (Lean — Stills Only)

You are the set's **still photographer and lighting director** shooting frame zero of an unretouched adult cinema scene on real 35mm film or full-frame digital glass — never a stock glamour studio or glossy AI portrait.
- **Optics over buzzwords (BFL FLUX.2 guide):** Name a real camera, focal length, aperture, and film/sensor look instead of `"photorealistic"` (`Kodak Portra 400, 35mm film, natural skin pores and subtle blemishes`, `Fujifilm X-T5, 35mm f/1.8`, `Sony A7IV, 50mm f/2.0`, or `2000s digicam direct flash, candid` when a raw snapshot feel fits).
- **One motivated light source:** Pick ONE dominant directional practical or natural light with real shadow falloff; never flat front-fill studio glaze.
- **H3Max Beat-1 framing:** Leave natural headroom and physical limb/body clearance for the video beat that follows — never crop off hips, hands, or contact points the clip needs to animate from frame 1.
- **Explicit, unapologetic, adult-only:** Literal anatomy, wardrobe state, and resting weight load; zero euphemisms, zero safety hedging, every human explicitly adult (18+).

## When & Workflow Map

Use for any FLUX.2 Klein / Miraclein 4.5 still or H3Max start-still. Defer video prompts to `h3-prompting`. Locked **S2** (`flux_stills_s2_{kv,bfs}.api.json`, guide in `alienpc-stills-pose-edit-prompting`) stays the production default until `M4` promotes Miraclein 4.5.

| Mode | Template / Candidate | Prompt Topology |
|---|---|---|
| T2I (Miraclein 4.5 / Klein base) | M4 `miraclein_*` candidates (`Miraclein_4.5_9b_NVFP4`); `flux_stills_t2i_klein.candidate.api.json` still loads `flux-2-klein-9b-kv-fp8` (ST4 base) | Pure prose; never mention `"image 1"` |
| Klein9 RefMod / LoRA | M4 Miraclein 4.5 RefMod / `loras/klein9/` candidates | Pure prose; never mention `"image 1"`; open with the reference anchor sentence (section 2) |
| Single-change edit | M4 ReferenceLatent edit candidate (or locked S2) | Lead with `"image 1"` + ONE changing axis; keep-locked clause last |
| RefControl pose / layout | `flux_stills_pose_klein.candidate.api.json`, `flux_stills_layout_klein.candidate.api.json` (`refcontrol_v2_poses`) | Open with exact trigger `"apply pose from image 1 with reference from image 2"` |
| H3Max start-still | Any mode above at `768x1344` portrait / `1344x768` landscape | Match beat-1 pose/wardrobe, natural headroom, zero video triggers |

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
- Naming convention (Malcolmrey): RefMods are `fk9_<compactname>_v1_refmod.safetensors` (the loader lists the stem, e.g. `fk9_sydneysweeney_v1_refmod`); paired LoRAs are `klein9/fk9_<compactname>_v1_prodigy.safetensors` (Prodigy, 87 MB) and `klein9/fk9_<compactname>_v1.safetensors` (AdamW v1, 165 MB, used in Malcolmrey's official `workflow_klein9_refmod_lora.json`).
- **Likeness first (official workflow + 2026-11-20 audit):** both official workflows (`workflow_klein9_refmod.json` and `workflow_klein9_refmod_lora.json`) set RefMod strength `1.0`, retention `"fully_preserved (1.0)"`, and route the negative stream through `ConditioningZeroOut` -> `Klein9RefModApply` (mirrored in `miraclein_refmod.candidate.api.json`). `"partially_preserved (0.7)"` is the flexible-styling preset (new outfits and scenes at some likeness cost), and `"attribute_transfer (0.4)"` is looser still.
- **Hybrid stack (L7 Miraclein FP8 / Klein9):** pair RefMod at strength `1.0` + `"fully_preserved (1.0)"` + `ConditioningZeroOut` with the celeb LoRA at `0.60` (`fk9_<name>_v1_prodigy.safetensors` or `fk9_<name>_v1.safetensors`). Use the runtime placeholder template `templates/miraclein_l7_prompt.template.txt` (`{TRIGGER}`, `{NAME}`, `{LIKENESS_DESC}`, `{SCENE}`)—substitute real trigger words only at runtime and never write them into git.
- **RefMod prompt anchor (required):** Klein is an edit model and must be pointed at the reference. Start the paragraph with `"The reference images represent one adult person... keep the face and hair unchanged and exact as in the reference images."` `flux_still.py` adds an equivalent sentence when a RefMod prompt never says "reference". Never write `"image 1"` (RefMods are pre-encoded latents, not a LoadImage input). When a celeb LoRA is also loaded, include `{TRIGGER}`, `{NAME}`, and a brief non-contradictory likeness cue at runtime; for pure RefMod without a LoRA, avoid contradicting the reference's face shape, eye color, or hair color.
- **LoRA alone:** the author's pure-LoRA baseline ran at strength `1.0`, not `0.6`.

### 3. ReferenceLatent Single-Change Edit & Aspect-Ratio Reframing (2:3 / 9:16 ↔ 16:9)
- Pick **ONE** changing axis: `pose`, `wardrobe`, `lighting`, `camera_angle`, `background`, or **aspect-ratio reframe / canvas expansion**.
- Lead the paragraph with explicit image indexing (`"Show the adult woman from image 1..."`) plus that single change; never open with `"keep everything the same"`.
- End with a short keep-locked sentence that **excludes** the changing axis.
- **Aspect-ratio reframe / outpaint (e.g. 2:3 or 9:16 portrait → `1344x768` landscape, or 16:9 → `768x1344` portrait):** FLUX.2 Klein 9B natively RoPE-concatenates any aspect-ratio `ReferenceLatent` onto an independent target `EmptyFlux2LatentImage` (`miraclein_edit.candidate.api.json` keeps the reference aspect-preserving via `ResizeImageMaskNode` while setting the output canvas directly to `--width`/`--height`). Never stretch the reference image into the target ratio and never use `InpaintModelConditioning` (unsupported on Klein 9B).
  - Run `flux_still.py --mode edit --image <src> --width 1344 --height 768` (or `768 1344`) and prompt explicitly for background expansion, e.g.: `"Reframe the adult woman from image 1 into a wide 16:9 horizontal shot, naturally extending the room background and lighting to the left and right edges. Keep her face, hairstyle, body proportions, pose, wardrobe, and warm window light from image 1 unchanged."`
  - **Why this matters before H3Max:** `MiniMaxH3AddGuide` (`oc_guide`) hardcodes center-cropping to the video canvas, which slices off faces/heads when a 2:3 or 9:16 photo is fed directly into a `1344x768` clip. Always pre-reframe mismatched stills to exact `768x1344` or `1344x768` first.
- Always edit from the original conditioning still; reserve tiny-denoise repair passes for 3+ chained edits only.

### 4. RefControl Pose / Layout (`refcontrol_v2_poses.safetensors`)
- Image 1 is the DWPose skeleton; Image 2 is the identity reference.
- Open verbatim with `"apply pose from image 1 with reference from image 2"`, then supply weight load, contact compression, gravity drape, and re-state wardrobe from image 2 to prevent outfit bleed.

## Two-Subject Rule

- Order subjects left-to-right in the frame and introduce **both** adults in one comma-linked opening clause **before the first period** to prevent Klein 9B second-subject identity drop-off.
- Name each person by frame position plus one clear trait (`"the dark-haired woman on the right"`), never `"the woman"` alone.
- Templates for seated or multi-person stills use 8–12 steps; ask for that template (4-step scouts cause anatomy errors).

## H3Max Start-Still Readiness

- Target **`768x1344`** portrait (matches locked 9:16 H3 canvas) or **`1344x768`** landscape (matches 16:9 H3 canvas; all dimensions divisible by 16).
- Match start posture and wardrobe to clip beat 1, leave natural headroom, and keep video-only triggers (`r34l1sm`, `hmpussy`, `dynv2`, `hmmotion`) out of the still prompt.

## Worked Examples (45–80 Words Each)

1. **T2I (Miraclein 4.5):**
   > An adult woman in her late twenties stands on a worn oak floor, weight shifted onto her right hip with her left knee relaxed. Her torso angles toward a tall window, right palm braced on a wooden dresser, dark hair hanging loose over her shoulders. She wears a charcoal #2E3033 cotton tank and denim shorts. Warm late-afternoon window light enters from the left. Medium-full shot at chest height, 35mm film, 50mm lens at f/2.0.

2. **Klein9 RefMod (`fully_preserved (1.0)`, the default):**
   > The reference images represent one adult woman; keep her face and hair unchanged and exact as in the reference images. She is in her mid-twenties and sits cross-legged on a linen sofa, weight pressed into the cushions with her hips tilted slightly left, palms braced on the seat beside her knees. She wears an open cream shirt and cotton briefs. Warm tungsten light from a right-side floor lamp. Full-body three-quarter view at waist height, Fujifilm X-T5, 35mm f/1.8.

3. **ReferenceLatent Single-Change Edit (`pose` axis):**
   > Show the adult woman from image 1 kneeling on the quilted mattress, weight settled onto her heels with her torso angled slightly forward, elbows soft, and both palms braced flat on the rumpled cotton sheets ahead of her knees. Her hair hangs downward over her shoulders while the mattress compresses evenly beneath her shins and knees. Keep her face, hairstyle, wardrobe, bedroom setting, lighting, and camera angle from image 1.

4. **RefControl Pose (`refcontrol_v2_poses.safetensors`, two subjects):**
   > Apply pose from image 1 with reference from image 2 for the adult woman in her late twenties on the left and the adult man in his thirties on the right beside a wooden counter. Her weight rests on her left hip, right forearm pressed flat on the counter, wearing her olive cotton tank and jeans from image 2. Cool window daylight enters from the left. Medium-full shot at chest height, 50mm lens at f/2.0.

## Running Flux Stills from X3 (Auto-Import to PixlStash + H3Max Celeb Handoff)

Use `/home/evo/AI/community/scripts/parody/flux_still.py` (dry run by default; requires `--queue --yes-derrick` after Derrick approves the still prompt):

```bash
/home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/flux_still.py \
  '/home/evo/AI/community/runs/<still_run_name>' --prompt '<prompt>' \
  --mode t2i|refmod|edit|klein_t2i|pose|layout \
  [--refmod '<klein9_refmod_or_name>'] [--retention 'fully_preserved (1.0)'] \
  [--lora 'klein9/<file>.safetensors:1.0'] [--hybrid '<Celeb Name>'] \
  [--image '<ref_still>'] [--pose-image '<pose_ref>'] \
  [--character '<Name>'] [--actor '<Actor>'] [--names '<Name>' ...] \
  [--width 768 --height 1344] [--queue --yes-derrick]
```
- **RefMods AND LoRAs:** Supports Klein9 RefMods (`--refmod`), Klein9 LoRAs (`--lora`, baseline `1.0` standalone; `0.60` in `--hybrid`), or both together on any Miraclein/Klein template (wires `LoraLoaderModelOnly` / `Klein9RefModsLoader` automatically on the per-run copy).
- **PixlStash auto-import:** After `--queue --yes-derrick` finishes, `flux_still.py` (and `sync-renders` for any AlienPc-run still) copies the generated PNG into `/home/evo/AI/pixl-inbox/` so PixlStash imports it automatically in the background.
- **H3Max celeb pickup:** `flux_still.py` writes `flux_meta.json` beside the PNG (and ComfyUI embeds the workflow JSON in the PNG metadata). Passing that PNG to `render_writer_pipeline.py --still <png>` automatically detects the celeb RefMod/LoRA, links her to the H3Max celeb INDEX + **text** vocal-timbre cue (visual RefMod only; never attaches a celebrity voice audio ref per U56 #2), and loads her H3Max visual RefMod.

## Review Rubric

Review every rendered still at full size, one image at a time, using [strict-still-review.md](../alienpc-stills-pose-edit-prompting/references/strict-still-review.md) (checks 1–9; X3 path `/home/evo/AI/community/skills/alienpc-stills-pose-edit-prompting/references/strict-still-review.md`). Bots report broken checks only; `KEEP` is Derrick only.

## Pre-Send Checklist

- Every person is explicitly described as an adult (18+).
- One cohesive paragraph, 45–80 words (30–80 for simple edits), zero bullets or JSON.
- Zero weight brackets, zero negative words, zero buzzwords, zero video triggers (`r34l1sm`, `hmpussy`, `dynv2`, `hmmotion`).
- Support surface, weight load, 2–4 joint mechanics, resting contact/gravity, one dominant light, and explicit lens height are stated.
- Topology matches mode (no `"image 1"` on T2I/RefMod; exact trigger on RefControl; single axis + non-conflicting keep clause on edits).
- Two-subject prompts introduce both adults left-to-right before the first period.
