# MiniMax-H3 REF2VA face lock (identity consistency) + nude anatomy rendering: prompt fixes vs setting fixes

**Date:** Fri 2026-10-09, about 5:42 to 6:15 PM CT
**For:** Derrick, via CoS. Research only. Nothing was queued, nothing touched AlienPc, no Grok Imagine prompts or sidecars were read, and no skill was edited.
**Model / settings in scope:** TenStrip 10Eros-Max H3 **beta6 int8**, `MiniMaxH3ReferenceToVideo`, 8 steps, Euler / simple, `MiniMaxH3SigmaShift` video 10 / audio 3, `BasicGuider` cfg 1 (no negative branch), `ref_image_size=match`, seed 43029049.
**Inputs read first:**
- skill `/home/box/agent-data/workflows/ref2va-prompt/SKILL.md`
- two-ref prompts `/workspace/maxops/two-ref-2026-10-09/prompts/` (OR_CONTROL_ONEREF, TR_A_MODERN, TR_B_ELVES_FANTASY, TR_C_ANCIENT_GREECE)
- review `/workspace/cos/brain-staging/60_reviews/max-clips/2026-10-09-tworef-face-lock.md`
- harness `/workspace/maxops/two-ref-2026-10-09/queue_tworef.py`
- (steering 5:49 PM) single-ref elf prompts `/workspace/maxops/elf-nude-test-2026-10-09/N*_10S.txt`, the clips `clips/` and the Cond stills in that folder
- prior local research (listed in Sources)

**Face rule:** faces are described by features, hair and light only. Nothing here says or judges whether a face looks like any real person.
**Claim tags:**
- **[OFFICIAL]** = MiniMax docs, a MiniMax staff reply, Comfy-Org docs, or ComfyUI source code.
- **[COMMUNITY]** = Reddit, blogs, GitHub/HF/Civitai users, third-party tools, and the model author TenStrip (marked "author").
- **[INFERRED]** = my reasoning from the sources plus our own clips and files. Not measured.

---

## 0. Key findings

1. **REF2VA does not pin frame 0. I2VA does. You can have both by chaining `Add Guide for MiniMax H3` at frame 0 after the REF2VA node.**
   - In the ComfyUI source, `MiniMaxH3ReferenceToVideo` returns an empty AV latent plus `minimax_refs` (reference tokens, no frame index).
   - `MiniMaxH3ImageToVideo` attaches `first_frame` as a `minimax_keyframes` entry at `resolved_frame_index 0`.
   - `MiniMaxH3AddGuide` appends the same kind of `minimax_keyframes` entry to whatever positive conditioning you feed it, including REF2VA's.
   - Comfy's official Multiframe Reference template is exactly this (ref2va checkpoint + REF2VA node + chained Add Guide). Its docs say "`<Picture 1>` is both the identity lock and the first frame of the video." [OFFICIAL, source + docs]
   - The skill line "true first-frame lock = I2VA and cannot mix with a reference image on the same node" is true for one node. The graph can still do both.
   - This is a **setting / graph fix**, the strongest single-ref fix available.
2. **`ref_image_size=max` is a no-op for the files we use.**
   - From the source: `match` scales each ref down to the generation pixel area, `max` scales down to a 2048 px short edge, and **neither ever upscales**.
   - Elf Conds (768x1376): `match` gives 768x1344, `max` gives 768x1376, a 2% difference.
   - Two-ref refs on the box (244x192 and 262x172): both modes give 256x192 and 256x160, identical.
   - `max` only changes anything when a ref file is larger than about 1 MP. [OFFICIAL source + INFERRED arithmetic]
   - The real lever is **more pixels on the face**: a large, sharp face crop.
3. **The two-ref prompts break the official label rules in three ways that plausibly explain "Picture 2 changed identity":**
   - (a) **Standalone `<Picture N>` lines for identity-only images.** Officially, a standalone Picture is a frame / keyframe / composition anchor. An image used only to define a character should be cited inside its `<Subject N>`. Our lines also describe the ref's "head-and-shoulders crop under soft dusk light with palm silhouette", which contradicts the target scene. [OFFICIAL guide §2.2; COMMUNITY minimax3.com lists "character drifts… image was given a standalone entry" as the first cause]
   - (b) **`attribute_transfer` used for wardrobe / setting / pose.** Officially it means "referenced characteristics are transferred to a **different identifiable target subject**." New wardrobe and setting are not fidelity losses. A dropped ref characteristic is `partially_preserved`. [OFFICIAL §4.1 + MiniMax staff reply HF #71] [INFERRED] Four `attribute_transfer` lines in a two-person prompt is the wording most likely to read as "move appearance onto someone else."
   - (c) **Non-label retention lines** ("Wardrobe (…):", "Setting (…):", "Pose / framing:"), and face and hair split across four `<Picture N>` lines. Officially it is one line per label: `<Subject N> (appears in [Shot 1]): marker - what survives`. [OFFICIAL]
4. **`detailed_description` never uses `<Subject 1>` / `<Subject 2>`, never ties a face to a frame position, and binds both faces in one shared sentence** ("Their faces and hair match `<Picture 1>` and `<Picture 2>` exactly").
   - Official rule: give each Subject its referenced traits plus **position in the frame** at first appearance, then reuse the label. [OFFICIAL §5.3]
   - A two-character benchmark: "a `<Subject>` label carries no identity… restate the appearance in every shot or the model invents a person." [COMMUNITY ai-muninn]
   - **Prompt fix.**
5. **The 0:02–0:04 failure window is the scripted beat.** That is when the heads turn toward each other (near-profile views neither frontal ref shows) and the laugh happens.
   - "Big expressions destroy identity faster than anything else. Asking for a wide genuine laugh gives you a different person at the peak of the motion." [COMMUNITY r/comfyui 1vm8j2c]
   - "A frontal reference provides less information about an extreme side profile." [COMMUNITY]
   - **Prompt fix:** a turn budget and small expressions.
6. **Too much changes at once, with small faces.** Wardrobe + setting + pose (+ ears in B) all change. B and C are full-body walks with the smallest faces. Rank CTRL > A > C > B tracks face size and scene distance. [COMMUNITY one-variable advice; INFERRED from frames: heads about 15–17% of frame height in A vs about 10% in C]
7. **Steps are the biggest setting lever we are under-using.**
   - Comfy: "Reference tokens ride along every sampling step… at 4 steps a reference can end up barely applied, and a subject's pose or face angle can drift… run the base 20-step schedule; if the reference still drifts, raise… to 25." [OFFICIAL]
   - beta6 author target: "8-12 steps, 10/3 shift". We run at the bottom of that band. [COMMUNITY, author]
   - 8 → 12 costs about +50% wall time.
8. **Single-ref elf clips drift for the same structural reasons, plus four of their own:**
   - The face is tiny in a 9:16 full-body Cond: about 90 px tall, about 6 latent rows of reference evidence. [INFERRED]
   - The face **leaves the view** during the back turn (5.5–6.5 s), then comes back low, tilted, and in three-quarter profile beside the hip. With no frame pin it has to be rebuilt. [INFERRED from frames]
   - Framing **pushed in** by 5 s despite "The camera holds a static shot." [INFERRED from frames]
   - 10 s is past the community useful length for anything tighter than waist-up (about 6 s waist-up, about 3 s close-up). [COMMUNITY 1vm8j2c, I2V]
   - The prompts say `<Picture 1> is the first frame of [Shot 1]` but use the `[reference generation]` prefix. Officially a frame anchor is `keyframe completion`, and the node does not pin anyway. [OFFICIAL]
9. **I2VA alone is not the answer on beta6.**
   - The I2VA node takes no reference images.
   - The beta6 author: "If I2V is having issues it should be transferred to reference generation since it still has issues with starting image style first-frame continuity that reference mode does not have." [COMMUNITY, author]
   - Community I2V tests still show mid-clip slide with only a first-frame anchor. "New seeds do NOT fix it. Double anchor (FLF2V) does: worst clips went from −0.53 to −0.10 vs reference." [COMMUNITY r/comfyui 1vo6enw]
   - **Best path [INFERRED]:** REF2VA + Add Guide at frame 0, optionally plus a last-frame guide of the end pose. That gives pin + double anchor + reference tokens.
10. **Gen time (142 vs 144 s) proves nothing either way about Picture 2.**
    - From the source: a 1344x768 5 s clip is 37 latent frames x 84x48 = about 149k video tokens. One ~1 MP ref adds about 4k tokens (+2.7%); a 256x192 ref adds about 192 (+0.1%). [INFERRED]
    - The harness keys `ref_images.ref_image_1` / `ref_images.ref_image_2` are valid autogrow names (prefix `ref_image_`, slots 0–8; the official template uses `_0`, `_1`, `_2`), and refs become `<Picture 1>`, `<Picture 2>` in dict order. [OFFICIAL source]
    - Malformed keys are dropped silently (Comfy #15667 / #15669).
    - A same-seed run with `ref_image_2` unplugged (Cell 0) settles it.
11. **Anatomy (added at 5:56 PM steering):**
    - The ugly genital render in the elf clips is mostly a **pixel-budget + motion + step-count problem, made worse by the wording**.
    - In a full-body 9:16 frame the vulva is a few dozen pixels. The prompts name five sub-parts in that area ("outer and inner labia parted… clit and wet pink opening") during a hip roll, at 8 steps.
    - Comfy: high-frequency detail "keep[s] improving up to about 50 steps… distilled… turbo checkpoints surface [artifacts] first". [OFFICIAL]
    - Community fixes, in order:
      - closer camera distance or a dedicated crop
      - fewer named parts and a shape description (the HMInnie author's axes: mound soft/puffy · cleft "closing to a smooth seam" / "with a defined cleft" · inner lips "tucked away" / "just visible" · labia colour "matching skin" / "pink"), plus the camera side ("shown from the front / from behind")
      - an anatomy tool LoRA: HMPussy V1 (stills; 0.4–0.6 is the safer band on references), HMInnie, Synth Pussy ("No face modification")
      - more steps
    - **Trade-off:** HMPussy and similar LoRAs have a "fairly strong face opinion", above 0.5 they "modify the original subject" (breast size, hair length), and at 0.7–1.0 they snap backgrounds. That fights face lock. [COMMUNITY] See §11.

---
## 1. What we have (facts from our files)

### 1.1 Two-ref test (16:9, 5 s, 1344x768, 124 f)
- Settings (review front-matter): beta6 int8, Euler / simple, 8 steps, shift 10, seed 43029049, no RIFE. Gen 142.0 / 144.1 / 143.9 / 143.4 s (CTRL / A / B / C).
- Harness `build()`: node 6 `MiniMaxH3ReferenceToVideo`, `ref_image_size: "match"`, `ref_images.ref_image_1` ← `--cond`, `ref_images.ref_image_2` ← `--cond2`; `vae` and `audio_vae` wired; `BasicGuider` on the shifted model.
- Box copies of the refs: `refs/REF1_BLONDE.jpg` **244x192**, `refs/REF2_DARKHAIR.jpg` **262x172**. The harness copies refs from the pack `meta/` folder, so AlienPc may have these thumbnails or larger masters. **Open item: check the pixel size of both files in AlienPc `ComfyUI/input`.**
- The refs, by feature and light only:
  - Picture 1: frontal head-and-shoulders, face about half the frame height, long wavy honey-blonde hair parted in the middle, light eyes, silver filigree tiara, wide gold choker, cool dusk sky with palm bokeh.
  - Picture 2: tighter crop with the face filling most of the frame, chin at the bottom edge, head angled slightly down with eyes up to the lens, long straight black hair parted in the middle, light eyes with dark liner, defined dark brows, gold choker at the bottom edge, same dusk / palm light.
  - **Neither ref shows a profile.**
- Output framing (frames at 0.3 / 2.5 / 4.8 s; [INFERRED, eyeballed]):
  - A: two women at three-quarter length, heads about 15–17% of frame height. Navy vs charcoal gowns (low wardrobe contrast); hair contrast strong.
  - C: full-body walk, heads about 10% of frame height (about 75–80 px).
  - CTRL: one woman at three-quarter length.
- Prompt structure (TR_A; B and C follow the same pattern):
  - Standalone `<Picture 1>` / `<Picture 2>` lines describing crop and light, plus `<Subject 1>` / `<Subject 2>` lines.
  - Retention: four `<Picture N> Face/ID…` / `Hair…: fully_preserved` lines; non-label `attribute_transfer` lines for wardrobe / setting / pose (and ears in B); accessories `partially_preserved… otherwise weak_reference`.
  - The description uses "the blonde woman" / "the dark-haired woman" and never the labels, plus "Their faces and hair match `<Picture 1>` and `<Picture 2>` exactly."
  - Scripted action: walk → both turn heads toward each other → smile → laugh → nod, all in the middle second.

### 1.2 Single-ref elf test (9:16, 10 s, 768x1344, 243 f)
- `orchestrate_elfnude.ps1`: `queue_dynvram.py --arm T10 --seed 43029049 --width 768 --height 1344 --sampler euler --scheduler simple`, 8 steps, shift 10, about 400 s each.
- Cond stills: all **768x1376**, full-body 9:16.
- Prompts N1–N3:
  - `<Picture 1> is the first frame of [Shot 1]: …` (standalone, used as a frame anchor, which is the correct use).
  - `<Subject 1>` with real face features (oval face, pale blue eyes, full lips, pointed ears, hair, circlet, choker).
  - Prefix `[reference generation]`.
  - Correct-form retention lines.
  - Phases: fast strip (0–2.5 s) → front show with fingers spreading the labia in a V and a hip roll (2.5–5.5 s) → pivot to turn the back (5.5–6.5 s) → forward bend, hands spreading the buttocks, look back over the right shoulder in three-quarter profile, hip sway (6.5 s to end). Lip bite and parted lips.
- Frames (0.1 / 2 / 5 / 7 / 9.8 s, N1 and N3; [INFERRED, eyeballed]):
  - Opening head about 9–10% of frame height (about 125 px), face about 90 px.
  - By 5 s the framing has **pushed in**.
  - At 7 s the face is turned away (N3 shows the back of the head).
  - At 9.8 s the face returns low and tilted in three-quarter profile beside the hip.
  - The genitals occupy a small part of a full-body frame in phase 2 and a mid-frame region in the rear bend.
- Derrick's verdict: face lock bad on all three, and the female genital anatomy renders ugly.

---

## 2. Official guidance on subject identity

From https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md (local mirror `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`) unless noted.

| # | Rule (quoted or close paraphrase) | Tag | Meaning for us |
|---|---|---|---|
| O1 | "Once a reference label is assigned… it keeps the same meaning across `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, and the audio sections." | OFFICIAL | Use `<Subject N>` in the description too. |
| O2 | "If `<Picture N>`… only identifies the source of another referenced item… cite it inside that item's definition without adding a separate line." | OFFICIAL | Identity-only refs get no standalone line. |
| O3 | §2.2: "Use a standalone `<Picture N>` when the reference image itself serves as a shot's first frame, keyframe, last frame, edited keyframe, or composition anchor… If an image is used only to define a character… do not create a standalone picture entry." | OFFICIAL | Two-ref prompts did the opposite. Elf prompts used it correctly as a first frame, but the node does not pin (O16). |
| O4 | "One subject may be defined by multiple reference assets… state what each asset provides." | OFFICIAL | Same-person face-crop assist: "face comes from `<Picture 2>`". |
| O5 | `fully_preserved` = role fully preserved; `partially_preserved` = "still used, but some defined characteristics are changed or only partially retained"; `attribute_transfer` = "Referenced characteristics are transferred to a **different identifiable target subject**"; `weak_reference` = broad similarity only. | OFFICIAL | `attribute_transfer` is wrong for "same person, new outfit." |
| O6 | "Use one line for each reference label." Format `<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - ...` | OFFICIAL | No free-text retention lines. |
| O7 | "Do not treat newly added actions, backgrounds, or plot events in the target video as losses of reference fidelity." | OFFICIAL | New setting / outfit needs no retention line. |
| O8 | MiniMax staff, HF #71 (Aug 11, 2026): "`partially_preserved` means that some defined reference characteristics are changed, omitted, or only partly used. It does not mean that only part of the Subject is visible." "Distinguish preservation, partial preservation, and attribute transfer correctly." "Describe the relevant characteristics at the Subject's first clear appearance, then reuse the label." | OFFICIAL | Define the Subject as face + hair so `fully_preserved` is true. |
| O9 | §5.3: "At the first clear appearance of an important `<Subject N>`, describe its referenced characteristics, **position in the frame**, and current action… Continue using the same label in later shots without redefining what the label represents." | OFFICIAL | Bind each face to left / right. Describe it once fully, then use the label plus one identifier. |
| O10 | §3: `keyframe completion` = an image is a first frame / keyframe / last frame; `reference generation` = guidance "without serving as a concrete frame." | OFFICIAL | Elf prompts mismatch prefix and Picture role. |
| O11 | Comfy prompt guide tip 8: no negative branch at cfg 1; "a line such as `no subtitles…` registers text as content… scope… through the retention analysis." https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide | OFFICIAL | Locks are positive retention lines. |
| O12 | Comfy tip 9 (sheets): "Give the sheet its own `<Picture N>` entry… since a picture cited only inside a definition is not used as a separate reference." | OFFICIAL (Comfy) | **Tension with O2/O3.** [INFERRED] Comfy's line is about pointing at panels of a multi-view sheet. Follow MiniMax for single-view face refs. Cell 1 tests it. |
| O13 | Comfy R2V tips: tag by connection order; "Assign each reference a job… explicit assignments work much better"; `match` vs `max`; "`res_multistep` with a `beta` or `normal` scheduler tends to outperform `simple` for reference-heavy prompts." (comfyui-wiki mirror) | OFFICIAL (Comfy) | One job per ref. Sampler is a later cell. |
| O14 | Comfy overview: "Reference tokens ride along every sampling step… at 4 steps a reference can end up barely applied… face angle can drift… run the base 20-step schedule… raise… to 25." Also: "Shots with high-frequency detail… keep improving up to about 50 steps… distilled step-reduction LoRAs and turbo checkpoints surface them first." https://docs.comfy.org/tutorials/video/minimax/minimax-h3 | OFFICIAL | 8 steps is short for both identity and fine anatomy. |
| O15 | Node doc + source: `match` "scales each ref (down only, keeping aspect) to the generation's pixel area; `max` uses the reference pipeline's 2048px short edge for best identity fidelity… several times slower"; refs "never upscaled." https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo | OFFICIAL | `max` only helps with large sources. |
| O16 | Source `comfy_extras/nodes_minimax_h3.py`: REF2VA → empty latent + `minimax_refs` (`latent_h = th//16`). TE presents `"<Picture i>: " <vision block>` per image (`comfy/text_encoders/minimax.py`). I2VA → `minimax_keyframes` `{resolved_frame_index: 0}`. AddGuide → appends `{resolved_frame_index: frame_idx, latent}` to `positive`'s keyframes (center-crop to canvas; negative idx counts from the end). | OFFICIAL (source) | REF2VA = no pin. Add Guide works on REF2VA conditioning. |
| O17 | Multiframe Reference: "combines the Reference to Video node with chained Add Guide nodes… `<Picture 1>` is both the identity lock and the first frame." "Pictures connected only to Add Guide nodes… are not visible to the text encoder. Plug them into extra `ref_images` slots too." https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe | OFFICIAL | The sanctioned "identity + pinned frame 0" recipe. |
| O18 | HF card: Ref2VA ≤9 images, ≤3 videos, ≤3 audio, ≤12 mixed. Comfy: "Match an H3 LoRA to the checkpoint build it was distilled on"; full-build LoRAs on pruned checkpoints have their adaln part skipped. | OFFICIAL | Room for extra face / profile refs. LoRA compatibility caveat for §11. |

---

## 3. Community findings (identity)

Reddit blocked every route this turn: WebFetch, Apify `apify--web-fetch` (empty page on old.reddit; a "Prove your humanity" challenge on www.reddit; the .json endpoint never returned), Apify `apify--rag-web-browser` ("Scraped 0 pages, 1 failed"), and `curl` (403). Reddit quotes come from search-index snippets and the third-party mirror reddit.sentinel-team.org (full snapshot of 1vm8j2c).

### 3.1 Face size, length, expressions, turns
- r/comfyui 1vm8j2c (u/ItsMilaVoss, Aug 2026, H3 **I2V** first frame, 6 s, 1120x1664):
  - "face small and turned away (three-quarter from behind): full 6.5 s, no visible drift; waist-up, medium face: about 6.2 s; close-up, face filling the frame: about 2.9 s."
  - Drift signature: "the face gets wider and rounder, the jawline softens, the smile goes generic, and the skin turns waxy."
  - "**Big expressions destroy identity faster than anything else**… a wide genuine laugh gives you a different person at the peak of the motion… Keep the expression small."
  - "'No push-in' does not stop camera movement, but a measurable instruction does… require that the subject's head occupy the same size in frame in the first and the last frame."
  - "Small props drift silently… name the small objects explicitly."
  - A Spanish-language reply: describing the referenced subject makes the model fit the image to the description, so "try not describing the subject." That is a single contrary comment; the official rule (O2 / O9) is to describe it. [INFERRED] Describe accurately and once, and never contradict the image.
  [COMMUNITY]
- r/StableDiffusion 1vihcz6:
  - "bad job at far away faces, a pretty decent job at midway faces… actual close ups do the best job."
  - "Set the ref_image_size to Max… give better results."
  - Format example: "`<Subject 1>` is man who uses: fully_preserved for his appearance."
  - [INFERRED] Combined with 1vm8j2c: close-ups start best but drift fastest, so waist-up is the sweet spot for 5–10 s.
  [COMMUNITY]
- r/comfyui 1w1rio5 (H3 ref2v dance): "~00:07 — face identity drift during head turn." [COMMUNITY]
- minimaxh3.co: "A frontal medium close-up shows more facial information than an extreme profile, a back-facing shot, a distant wide shot…"; "A frontal reference provides less information about an extreme side profile. Move gradually…" [COMMUNITY]
- note.com さっしゅ: "the video will gravitate toward the orientation and distance of the reference… If you provide a back reference, it comes out as a back view"; choose 2–3 refs matching the distance and orientation you want; "For turning around, request a half-turn." [COMMUNITY] → [INFERRED] An added face-only crop can pull framing tighter. State the framing explicitly when you add one.
- TenStrip (LTX 10Eros page): "Expressions, dialogue, movement, and camera/pose change will all attack the guided character's look… have a guided endframe to give the model a future target." [COMMUNITY, author]

### 3.2 Two characters: binding, contrast, position
- ai-muninn bench (2026-09-06; 1344x768, 243 f, 14 steps, res_multistep / simple, match, 2 refs):
  - "no bleed between the two faces (n=1, and I made the designs as different as I could)."
  - "**a `<Subject>` label carries no identity, so restate the full appearance in every shot or the model invents a person.**"
  - "make your two characters as unlike each other as the scene allows."
  - Two similar-looking characters untested.
  [COMMUNITY]
- r/StableDiffusion 1vojyye (two-person replacement, "worked 90% of the time", seed-dependent):
  - Position binding: "The person on the left/foreground… is completely replaced by `<Subject 2>`, adopting the exact facial features, hair, and wardrobe from image2."
  - On two refs for one person: "…didn't work… only started working when I explicitly said… appearance comes from `<Picture 1>`, and face comes from `<Picture 2>`."
  [COMMUNITY]
- virse.ai identity-drift guide (Aug 26, 2026):
  - "Image 1 defines Character A… Character A replaces the left performer"; "Clear Character A and Character B assignments are safer than vague labels."
  - "reducing the number of reference images improved identity accuracy."
  - "Use a Character Board for Full-Body Motion and Turns… front view, rear view, and close-up face."
  - "make the identity-defining features large and clear enough for the scale at which the character appears in the final shot."
  - Debug order: "Test approximately five seconds → Strengthen the face reference → Match the framing → Remove unnecessary references → Clarify… roles → Add a rear view for turning shots → Test another seed → Increase quality settings."
  - 4-step turbo "difficult motion sometimes lost identity… returned to approximately 20 steps."
  [COMMUNITY]
- virse.ai H3 guide: "identity problems become more common when two characters appear together, several face references overlap, or environments change across shots." [COMMUNITY]
- minimax3.com builder (third-party):
  - "If an image exists only to define a character… it does not get a standalone entry… never appears in retention_analysis."
  - "**A character drifts from the uploaded image** — Likely cause: The image was given a standalone entry, so it reads as a frame anchor… Fix: Cite the image inside a definition and delete its separate line."
  - "A reference is never applied at all — …label is defined but never cited in detailed_description."
  - Marker example: "`attribute_transfer` — One person's outfit is put on another person."
  [COMMUNITY]
- minimax-h3.wiki: "Reduce the scene to one identity reference, one subject, and one shot. Once the face and proportions hold, add wardrobe, setting, action, and camera constraints back individually." [COMMUNITY]

### 3.3 Reference crop, resolution, sheets
- r/StableDiffusion 1vjw7pj:
  - "unless you set `ref_image_size: max`… your reference images will be resized down to match the video resolution."
  - "Resolution matters big time for faces. Anything below 1 megapixel will look weird."
  - Face 4-panel sheet + body sheet on neutral grey, with "ref_image_size to max."
  - "good quality close up of face matters more."
  - Body / face binding with separate `fully_preserved` clauses.
  [COMMUNITY]
- virtuavixen: two refs of one subject at "different angles or expressions help the model lock identity." [COMMUNITY]
- movey.ai: a stitched sheet means "fewer pixels per view"; separate inputs are best "when fine facial… detail is critical." [COMMUNITY]
- JahJedi character sheet (HF): neutral multi-view sheets made with H3 at `max`. A true profile panel needed "STRICT profile at exactly 90 degrees." [COMMUNITY]

### 3.4 Seeds, steps, model (TenStrip / 10Eros-Max)
- beta6 author notes (CivArchive mirror):
  - "a heavily modified reference model… Uses 10/3 shift and higher sampling targets of **8-12 steps**… optionally run an upscale pass to clean up reference noise."
  - "a true hybrid, i.e. just a Reference model with T2V ability. **If I2V is having issues it should be transferred to reference generation.**"
  - Built from the full bf16 **fl2va** base with reference deltas, then pruned.
  - Notes "higher levels of noise and noised edges" from reference deltas.
  [COMMUNITY, author]
- beta5 list (same page): "er_sde/beta57 4-6 steps (seems to be best preservation of style and reduced drift)." Not verified on beta6. [COMMUNITY, author]
- README: "No cache or spectrum if doing reference, they cause accuracy loss." [COMMUNITY, author]
- HF #21, TenStrip: "check your sampling and prompting… LLM enhancing with the r2va dev prompting guide, using all subject descriptions… proper tagging." [COMMUNITY, author]
- Stuubs ref2va builds: grafted hybrids "slightly reduce per-frame video-reference accuracy versus the plain base ref2va model." [COMMUNITY] [INFERRED] Prompt and steps have to make up for that.
- beta6 page comment: references "not respected on face and hair", "white eye syndrom". [COMMUNITY, single report]
- r/comfyui 1vo6enw: "With only a first-frame anchor, the host's face slides toward a generic one mid-clip. **New seeds do NOT fix it. Double anchor (FLF2V) does**: worst clips went from −0.53 to −0.10." [COMMUNITY]
- 1vm8j2c reply (u/Etsu_Riot): a 4-step turbo at 8 steps gave "almost [no] morphing… during 20-second clips… What was destroyed was the sound." [COMMUNITY, single report]
- HF MiniMax-H3 #91: Ref2VA with an **audio ref** recast identity even at `max`, native checkpoint, 18 steps. Do not add a voice ref to face-lock tests. [COMMUNITY]

### 3.5 Plumbing (GitHub)
- Comfy #15667 (closed as user error): REF2VA refs were silently ignored via `POST /prompt` because the key was a nested object. Flat dotted keys like the template (`"ref_images.ref_image_0"`) work. Unknown keys are dropped with no warning (feature request #15669). https://github.com/Comfy-Org/ComfyUI/issues/15667 [COMMUNITY + OFFICIAL template]
- Our harness uses the dotted form with in-range slot names. It should be fine; Cell 0 confirms it.

---
## 4. Diagnosis: two-ref clips

| Cause | Evidence | Kind | Weight |
|---|---|---|---|
| Standalone `<Picture N>` lines for identity-only refs, describing ref crop / light that contradicts the target | O2, O3; minimax3 "drifts" FAQ | prompt | high |
| `attribute_transfer` used for wardrobe / setting / pose / ears | O5, O8; minimax3 marker example | prompt | high |
| Description never uses `<Subject N>`, no position binding, one shared face sentence | O1, O9; ai-muninn; 1vojyye; virse | prompt | high |
| Head turns to near-profile + laugh at 0:02–0:04; refs are frontal only | 1vm8j2c; minimaxh3.co; 1w1rio5 | prompt (+ refs) | high |
| Faces small (B / C full-body walks) | 1vihcz6; ranking CTRL > A > C > B | prompt + framing | medium-high |
| Everything changed at once (wardrobe + setting + pose + ears) | wiki; virse | prompt | medium |
| 8 steps | O14; beta6 8–12 band | setting | medium |
| Tiny ref files (≤262 px wide on box) | 1vjw7pj "below 1 megapixel will look weird"; O15 | refs | medium (unverified on AlienPc) |
| Picture 2 is a very tight, chin-cropped, head-down crop | minimaxh3.co; note.com | refs | low-medium |
| `ref_image_size=match` | O15: identical to `max` at these sizes | setting | ~none now |
| Picture 2 not reaching the model | key form valid; Cell 0 | plumbing | low |

## 5. Diagnosis: single-ref elf clips

| Cause | Evidence | Kind | Weight |
|---|---|---|---|
| No frame-0 pin. The "first frame" line only steers | O16, O17 | graph | high |
| Face about 90 px in the ref, small in output | 1vihcz6; virse "large and clear enough" | ref + framing | high |
| Face leaves view (pivot), returns in three-quarter profile, tilted, low | 1vm8j2c; minimaxh3.co; TenStrip LTX note | prompt | high |
| Push-in despite "static shot" | 1vm8j2c "measurable instruction" | prompt | medium-high |
| 10 s with lots of motion and expression (lip bite, parted lips, look back) | 1vm8j2c durations | prompt + length | medium-high |
| `[reference generation]` with a first-frame Picture role | O10 | prompt | low-medium |
| 8 steps | O14 | setting | medium |
| No profile / back reference for the turn | virse board; note.com | refs | medium |
| `ref_image_size` | 768x1376 → 768x1344 vs 768x1376 | setting | ~none |

## 6. Prompt fixes vs setting fixes

### 6.1 Prompt fixes (two-ref)
1. Delete standalone `<Picture 1>` / `<Picture 2>` lines. Cite each picture inside its Subject.
2. Define each Subject as **face + hair only** (identity), cited to its picture. Write wardrobe and setting as new content in the description.
3. Retention: exactly one line per Subject, `fully_preserved - face and hair`. No `attribute_transfer`. If you want something from the ref dropped, use `partially_preserved - … ; <dropped item> not retained`.
4. In the description, bind each Subject to a position (frame-left / frame-right) at first appearance with its face features. Then always write `<Subject N>` + one short identifier ("`<Subject 2>`, black hair") and keep the side fixed.
5. Turn budget: heads turn "about 30 degrees toward each other, never past three-quarter view; both faces stay visible to the camera." Small expressions: "a small closed-mouth smile" instead of a laugh.
6. Face size: waist-up, "each head about one sixth of the frame height in every frame; the camera does not push in."
7. One scene variable at a time. Keep B's ears out until faces hold.
8. Contrast: keep blonde vs black (already strong). Add wardrobe contrast (navy vs charcoal is weak) so position and color carry identity.

### 6.2 Prompt fixes (single-ref)
1. Keep `<Picture 1> is the first frame of [Shot 1]` **and** pin it with Add Guide (setting fix 6.3.1). Change the prefix to `[keyframe completion]`. Without the pin, write `[reference generation]` and cite Picture 1 inside the Subject.
2. Remove the face-away beat, or make it short and late: "she turns her hips to three-quarter rear while her head stays turned toward the camera, face visible the whole time." Replace "look back over the right shoulder in three-quarter profile" with "looks back at the camera over her right shoulder, face turned toward the lens, both eyes visible."
3. Limit the bend: "leans forward slightly at the hips, head up, face toward the camera."
4. Camera lock: "full-body framing held; her head stays the same size in frame from first to last frame; no push-in, no zoom."
5. Split 10 s into two 5 s clips, or chain with a last-frame guide.
6. Small expressions: drop the lip bite or keep one. Avoid a wide open mouth.

### 6.3 Setting / graph fixes
1. **REF2VA + `Add Guide for MiniMax H3` at frame_idx 0** (the same image also on `ref_image_0`). Optionally a last-frame guide at -1 with the target end pose (make it with a still model or a prior clip's frame). [OFFICIAL O17]
2. **Steps 8 → 12** (top of the beta6 band), then try 16 if time allows. [OFFICIAL O14 + author band]
3. **Bigger face pixels:** add a second ref = a sharp face crop of the same person (≥768 px on the face; ≥1 MP file), bound as "face comes from `<Picture 2>`". Then `max` starts to mean something. [COMMUNITY 1vjw7pj, 1vojyye; OFFICIAL O4]
4. `ref_image_size=max` **only after** larger files exist. [OFFICIAL O15]
5. Sampler `res_multistep` + `beta` (Comfy) or er_sde / beta57 (beta5 note) as a later one-change cell. [OFFICIAL O13 / COMMUNITY]
6. Keep seed fixed across A/B. Treat seed as noise, not a fix (1vo6enw). Do one seed sweep only after the prompt is fixed.
7. Do not use cache / spectrum accelerators on reference runs. [author]

## 7. Rewrite template: two-reference `subject_definitions` + `retention_analysis` (+ description binding)

```
[reference generation]

subject_definitions:
<Subject 1> is the woman in <Picture 1>: oval face, light eyes, straight nose, full lips, long wavy honey-blonde hair parted in the middle. Identity is her face and hair only.
<Subject 2> is the woman in <Picture 2>: [face shape], light eyes with dark liner, defined dark brows, [nose], [lips], long straight black hair parted in the middle. Identity is her face and hair only.

summary:
[One sentence: setting, both women, the action, camera.]

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - face and long wavy honey-blonde hair from <Picture 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - face and long straight black hair from <Picture 2>.

detailed_description:
[Shot 1] [Setting, light, lens]. Waist-up two-shot; each head about one sixth of the frame height in every frame; the camera does not push in. <Subject 1>, honey-blonde hair, stands on frame-left in [wardrobe A, distinct color]; <Subject 2>, black hair, stands on frame-right in [wardrobe B, contrasting color]. Both faces are toward the camera and evenly lit by [light]. At 00:01.5, <Subject 1> on the left turns her head about 30 degrees toward <Subject 2>; <Subject 2> on the right turns about 30 degrees toward <Subject 1>; both faces stay visible to the camera, never past three-quarter view. They share a small closed-mouth smile. At 00:03.5 both look back toward the camera. <Subject 1> stays on the left and <Subject 2> stays on the right for the whole shot.

overall_soundscape: ...
non_diegetic_music: ...
```

Notes:
- If a ref item must be dropped (tiara, choker): `<Subject 1> (appears in [Shot 1]): partially_preserved - face and hair from <Picture 1>; tiara and choker not retained.` [OFFICIAL O5, O8]
- If a same-person face crop is added: `<Subject 1> is the woman in <Picture 1>, whose face comes from <Picture 3>` and one retention line for `<Subject 1>`. [OFFICIAL O4; COMMUNITY 1vojyye]
- Single-ref (elf) template:
  ```
  [keyframe completion]
  <Picture 1> is the first frame of [Shot 1].
  <Subject 1> is the elf woman in <Picture 1>: oval face, pale blue eyes, full lips, pointed ears, [hair], [circlet].
  retention_analysis:
  <Picture 1> (appears in [Shot 1]): fully_preserved - opening frame composition.
  <Subject 1> (appears in [Shot 1]): fully_preserved - face, hair and ears.
  ```
  Plus the Add Guide pin. [OFFICIAL O3, O10, O17]

---
## 8. Ranked A/B cells (one change each; same seed 43029049, same settings unless the cell says otherwise)

**Cell 0 (plumbing sanity, 1 run, optional):** TR_A as-is with `ref_image_2` unplugged. If the output barely differs from TR_A, Picture 2 was not reaching the model. Rule this out before reading anything else.

**Cell 1 (two-ref, prompt): Subject-cited identity + `<Subject N>` labels + position binding.** Base: TR_A.
- Delete the two lines that start `<Picture 1>` and `<Picture 2>` in subject_definitions.
- Replace the Subject lines with the §7 template lines ("`<Subject 1>` is the woman in `<Picture 1>`: … Identity is her face and hair only.").
- Replace all retention lines with the two §7 `fully_preserved - face and … hair` lines (no `attribute_transfer`, no Wardrobe / Setting / Pose lines).
- In detailed_description, replace "the blonde woman" → "`<Subject 1>`, honey-blonde hair, on frame-left" at first mention and "`<Subject 1>`" after. Same for `<Subject 2>` on frame-right. Delete "Their faces and hair match `<Picture 1>` and `<Picture 2>` exactly."
- Expected: Picture 2 keeps her identity. **Highest value.** [OFFICIAL O1–O9 + COMMUNITY]

**Cell 2 (both setups, prompt): turn budget + small expression.** Base: Cell 1 winner (or TR_A).
- Replace "turn their heads toward each other… laugh" with: "At 00:01.5 each turns her head about 30 degrees toward the other, never past three-quarter view, both faces visible to the camera; they share a small closed-mouth smile; at 00:03.5 both look back toward the camera."
- Elf version (N1): replace "looking back over her shoulder in three-quarter profile" with "looks back at the camera over her right shoulder, face turned toward the lens, both eyes visible", and "bends forward at the hips" with "leans forward slightly at the hips, head up."
- [COMMUNITY 1vm8j2c, minimaxh3.co]

**Cell 3 (single-ref, graph): Add Guide frame-0 pin.** Base: N1 as-is.
- Add `MiniMaxH3AddGuide` (positive from REF2VA, image = the Cond still, frame_idx 0, strength 1.0) between the REF2VA node and the guider.
- Change the prefix `[reference generation]` → `[keyframe completion]`.
- Expected: frame 0 matches; the face holds longer. Watch 5–7 s. [OFFICIAL O16, O17]

**Cell 4 (both, setting): steps 8 → 12.**
- Change `steps` only. About +50% gen time (~215 s two-ref, ~600 s elf).
- [OFFICIAL O14; author 8–12]

**Cell 5 (both, refs + prompt): add a same-person large face crop.**
- Add `ref_image` = a ≥1 MP crop where the face fills most of the frame (for the elf, crop from the higher-res master if one exists, or regenerate a close-up still).
- Add to the Subject: ", whose face comes from `<Picture 2>`" (`<Picture 3>` in two-ref).
- Set `ref_image_size=max` in the same cell **only if** the crop is >1 MP (otherwise it is a no-op).
- [COMMUNITY 1vjw7pj, 1vojyye; OFFICIAL O4, O15]

Order: 0 (if in doubt) → 1 → 3 → 2 → 4 → 5. Cells 1 and 3 are the cheapest high-value changes; 4 costs time; 5 needs new assets.

---

## 9. What `ref_image_size` can and cannot do (arithmetic)
- `match`: scale down to the generation pixel area (1344x768 ≈ 1.03 MP; 768x1344 same). `max`: scale down to a 2048 short edge. Neither upscales. [OFFICIAL source]
- Two-ref refs 244x192 / 262x172 → both modes give the same size (snapped to /16). Elf Conds 768x1376 → 768x1344 vs 768x1376.
- So: **no expected visual difference** with today's files. Test `max` only alongside larger ref files (Cell 5).

## 10. Open items
- Check the true pixel size of REF1 / REF2 on AlienPc `ComfyUI/input` (not touched this turn).
- Find out whether higher-res masters of the elf Conds exist (for face crops).
- Reddit full threads were not readable (blocked); quotes are from snippets and the sentinel mirror.

---

## 11. Female genital anatomy on H3 / TenStrip (added at 5:56 PM steering)

### 11.1 What the elf prompts ask for
Phase 2 (2.5–5.5 s), verbatim: "…spreads her pussy open with her index and middle fingers in a V, her outer and inner labia parted and her clit and wet pink opening clearly shown to the lens, five fingers readable…", during a hip roll, **in a full-body 9:16 frame**. Phase 4: "bends forward… spreads her ass cheeks apart… so her asshole and her pussy below it are fully shown to the lens… sways her hips… still spread open." The summary line repeats "spreads her pussy open".

### 11.2 Why it renders ugly
| Cause | Evidence | Kind |
|---|---|---|
| **Pixel budget.** In a full-body 768x1344 frame the vulva is roughly 30–50 px tall (about 2–3 latent cells at /16). The prompt names five sub-parts plus a two-finger V inside that area. | [INFERRED] from frames + the latent factor in O16 | framing + prompt |
| **The base model renders genitals soft and vague.** | HMPussy author: the stills LoRA "restores legible structure in female genital anatomy, which the base model renders soft and vague." Fingering LoRA author: "H3 doesn't understand labial and vaginal distension really at all… 10Eros helps massively… but without this LoRA, 10Eros struggles." | COMMUNITY |
| **Motion on top of spread** (hip roll, hip sway while held open). | HMPussy commenter: "In extreme close-ups the texture and details that evolve upon physical interaction is perfect, wish you can capture it at medium full shot range." Fingering LoRA needed staged close-up → medium → full-body training "to prevent zooming or cutting into close-ups." | COMMUNITY |
| **8 steps.** Fine high-frequency detail is the first casualty of few steps. | Comfy: detail "keep[s] improving up to about 50 steps… distilled step-reduction LoRAs and turbo checkpoints surface them first." | OFFICIAL |
| **Rear view orientation errors.** | HMPussy commenter: "When viewed from the rear, I'm getting vaginas that are front facing with clitoris on top." | COMMUNITY |
| **Spread vs anatomy coherence.** | No source shows "spread open" itself causes mush in close-ups (spread / fingering is in the training sets of HMPussy, Synth Pussy, "Pussy spread v0.2"). The mush appears at **medium / full-body distance**. | COMMUNITY + [INFERRED] |

**Answer to "does 'spread open' close-up cause mush?"** Community evidence says the close-up is where it works best. The mush comes from spread + small in frame + motion + few steps, and the base model's weak anatomy prior. Spread at full-body distance is the bad combination. [COMMUNITY + INFERRED]

### 11.3 Prompt wording that renders well (community)
- **Literal, clean, sequential wording, no slang compounds.** 10Eros author: "Describe things cleanly and literally… Prompt in temporal sequence… Not with slang terms; with proper actionable words that can be tokenized." Example phrase: "her wet labia open." [COMMUNITY, author]
- **Shape axes (HMInnie author, written as plain English inside the sentence):**
  - Mound: flat · soft · puffy · very puffy
  - Cleft: closing to a smooth seam · with a defined cleft · parted around a visible opening
  - Inner lips: tucked away · just visible · slightly protruding
  - Labia colour: matching skin · pink · rosy · brown
  - Plus the camera side: "shown from the front" / "from behind" / "from below".
  - These were learned with the HMInnie LoRA (trigger `inniepussy` replaces the word "pussy"). [COMMUNITY] [INFERRED] The same plain-English axes are a sensible wording for the base model too, but expect a weaker effect without the LoRA.
- **Fewer named parts.** [INFERRED] Replace "outer and inner labia parted and her clit and wet pink opening clearly shown" with one shape phrase matched to the distance:
  - full-body: "a smooth, hairless vulva with a soft mound and a closed seam, labia matching her skin tone, shown from the front" (no spread).
  - medium / waist-up: "a soft, hairless vulva, inner lips just visible, pink"; "gently parted with two fingers" at most.
  - close-up: the spread wording can stay, but describe one action ("she slowly parts her labia with two fingers, holding still").
- **Hold still while showing.** [INFERRED from the motion row] "She holds her hips still while…" instead of a hip roll or sway during the spread.
- **One camera side at a time.** [COMMUNITY HMInnie captions + rear-view orientation report] For the rear bend: "shown from behind, her vulva visible below her buttocks, closed seam", and avoid "asshole and her pussy below it are fully shown… still spread open" in a mid-shot.

### 11.4 Pose and camera distance
- Best: close-up or a dedicated crop shot, frontal, still. Lying back / bending from behind work for HMPussy ("works… in most of the positions, especially laying or from the back bending"). [COMMUNITY]
- Standing front: HMPussy commenter: "from the front when standing sometimes the clit and genitals starts a bit higher (like 1-2 cm above the expected position)." [COMMUNITY]
- Full-body walk / strip: keep the anatomy description simple and closed; save explicit spread for a separate close-up clip. [INFERRED]
- **Trade-off with face lock:** a close-up of the genitals takes the face out of frame. Make it its own shot / clip (different framing per 5 s clip), or keep the face in frame with a reclining pose shown from the front. [INFERRED]

### 11.5 Tool LoRAs (non-celebrity) and settings
| LoRA | Trigger / use | Strength (author / community) | Notes | Source |
|---|---|---|---|---|
| **HMPussy V1** (HearmemanAI), `Vagina_minimax-h3_epoch20.safetensors` 74 MB | none required; describe anatomy | author 1.0 originally, "Not needed [motion file], 0.9" for V1; community "0.5–0.6 depends on… distance from camera"; 0.4 already improves | ">0.7 for reliable clitoral hood (sometimes misplaced)"; ">0.5 modifies the original subject" (breast size, hair length), skips shots; "fairly strong face opinion"; "overfit… adds noise, dark"; with i2v "a picture perfect one… completely destroys it"; man in scene "gets a vagina too". Trained on fl2va bf16, LoKr. | https://civarchive.com/models/2846342 |
| HMPussy v0.5 (2 files) | `Vagina` stills 1.0 + `hmpussy` video 0.35 | as listed | motion file holds structure through motion | same page, v0.5; HF mirror bucket |
| **HMInnie v1** `HMInnie_v1_e50.safetensors` | `inniepussy` replaces "pussy"; "shown from the front / behind / below" | not stated | shape axes above; stacks with HMPussy; rank 32, full bf16 base | https://civarchive.com/models/2853405 |
| **Synth Pussy v1.0** (QualityControl) 148 MB | none | not stated | "No face modification"; shaved only; adds exposed breasts through thin clothing; trained on images, spread / fingering work | https://civarchive.com/models/2509189 |
| Free Pussy (kermitfrog1202) 148 MB | none | — | "Works great with Eros 5 turbo at 8 steps"; a ref2va user at 0.2 saw the reference anatomy break down | https://civarchive.com/models/2934054 |
| H3 Innie Pussy (n1eze) | none | 1.0 at 35 steps; users at 8-step turbo saw "background instantly change… 0.4-0.5 fixes" | i2v background snap | https://civarchive.com/models/2841940 |
| Fingering Pussy v1.1_H3 | describe motion | **0.8 with 10ErosMax** | "combo of 10Eros and this LoRA is the golden touch"; works with FL2VA and Ref2VA | https://civarchive.com/models/2007360 |
| Pussy spread v0.2 i2v | — | — | test LoRA, captions follow the H3 guide | https://civarchive.com/models/2885332 |

HF mirror (no account needed): https://huggingface.co/buckets/fdk3r6b/minimax-h3-loras-bucket ("single-concept and they stack").

**Compatibility [OFFICIAL O18 + INFERRED]:** these LoRAs were trained on the full bf16 base (mostly fl2va). beta6 int8 is a pruned grafted hybrid, so the adaln part may be skipped and the effect differs. Start low and step up.

**Recommended LoRA test for Derrick [INFERRED]:**
- Synth Pussy at 0.6 first (claims no face change), or HMPussy V1 at 0.5. Do not go above 0.6 on reference runs until face lock is solved, because of the face / breast / hair / background drift reports.
- No local H3 anatomy LoRA is known on the box; AlienPc inventory was not checked (out of scope this turn).

### 11.6 Anatomy A/B cells (one change each, after the face cells or in parallel on N1)
- **AN1 (prompt, cheapest):** N1 phase 2, replace "spreads her pussy open with her index and middle fingers in a V, her outer and inner labia parted and her clit and wet pink opening clearly shown to the lens" with "rests her right hand on her thigh, her smooth hairless vulva shown from the front, soft mound, closed seam, labia matching her skin tone; she holds her hips still". Phase 4: delete "still spread open" and the hip sway; add "shown from behind, closed seam".
- **AN2 (framing):** a separate 5 s close-up clip of the spread beat only, frontal, still, waist-to-thigh framing.
- **AN3 (LoRA):** N1 unchanged + Synth Pussy 0.6 (or HMPussy V1 0.5).
- **AN4 (setting):** steps 8 → 12 (shared with face Cell 4).

---

## Sources
Official:
- MiniMax H3 reference prompt guide: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- MiniMax staff reply HF #71: https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/71
- Comfy H3 overview: https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- Comfy H3 prompt guide: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- Comfy REF2VA node: https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo
- Comfy Multiframe: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe
- ComfyUI source: https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py
- Comfy issues #15667 / #15669: https://github.com/Comfy-Org/ComfyUI/issues/15667

Community:
- r/comfyui 1vm8j2c (drift by framing, sentinel mirror): https://www.reddit.com/r/comfyui/comments/1vm8j2c/
- r/StableDiffusion 1vihcz6, 1vjw7pj, 1vojyye, 1vprkrb; r/comfyui 1w1rio5, 1vo6enw (snippets)
- ai-muninn two-character bench; virse.ai identity-drift guide + H3 guide; minimax3.com builder; minimaxh3.co; minimax-h3.wiki; note.com さっしゅ; movey.ai; virtuavixen; JahJedi sheet (HF)
- TenStrip 10Eros-Max: https://huggingface.co/TenStrip/10Eros-Max ; beta6 / beta3 pages via CivArchive https://civarchive.com/models/2851079
- Anatomy LoRAs: links in §11.5; HF mirror bucket above.

Local:
- `/home/box/agent-data/workflows/ref2va-prompt/SKILL.md`
- `/workspace/cos/research/2026-10-02-max-ref-image-best-practices.md`
- `/workspace/cos/research/2026-10-05-ref2va-dual-picture-same-person.md`
- `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/MINIMAX_H3_VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`
