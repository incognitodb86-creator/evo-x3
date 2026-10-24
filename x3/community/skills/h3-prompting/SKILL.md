---
name: h3-prompting
description: Write MiniMax-H3 / 10Eros-Max v2 chunk prompts (c0 Ref2VA + c1 continuation) that keep identity, bodies and audio - subject_definitions wording, the overall_soundscape line, positive-only descriptive style, contradiction phrases to keep out. Use when writing or reviewing any prompt file in notes/hc_*.txt, specs/prompt_v2, notes/im1_prompts.md, or a sequence_prompt for Continuum.
---

# H3 prompting (v2 format)

Derrick 2026-10-23 6:24-6:25 PM CT: prompts must be **greatly improved and much more descriptive**. Write the text
as a plain `notes/*.txt` file FIRST, then embed it in the builder: prompts become reviewable and diffable, and the
prompt/graph variables stay separable. Fiction lock: every character is a fictional adult 21+, and the youth-guard
module named in AGENTS.md "## Scope" is never edited (the lock matches the TEXT of a command too, so never put that
path in a command string).

## 0. When to use this skill

- Writing or reviewing any clip prompt: `notes/hc_*.txt`, `specs/prompt_v2/*`, `notes/im1_prompts.md`, a Continuum `sequence_prompt`, or the `overall_soundscape:` line of any chunk.
- PQ1 (prompt research) and IM1 (the one-variable A/B re-render) - the plan and the open list are in section 7.
- After a clip is judged weak: section 6 is the vocabulary that fixed identity drift and under-skin detail.

## 1. Section skeleton (keep the section names and the line counts stable)

Worked example: `specs/prompt_v2/v2_seg1_c0_r2v.txt`, rendered baselines `notes/hc_r3b_c0.txt` (22 lines) and
`notes/hc_r3b_c1.txt` (14 lines). Keep line counts identical to the baseline you are comparing against, so a
side-by-side changes references and wording, never structure.

1. `subject_definitions:` - `<Picture N>` sentences binding each subject to a reference, one line per subject.
2. `summary:` - `[reference generation]` + the shot count, duration, who, where, and the action in one beat.
3. `retention_analysis:` - `<Subject N> (appears in [Shot 1]): fully_preserved - <which picture keeps what>`,
   plus the clothing clause when wardrobe is removed (see 3).
4. `detailed_description:` (c0) / `integrated_multimodal_description:` (c1) - `[Shot 1]` beat by beat across the
   10 s with camera, lens, lighting, setting, body/anatomy and motion quality.
5. `overall_soundscape:` - REQUIRED (it is the audio test): room tone + the body-sound beats.
6. `non_diegetic_music:` - sparse, under the body sounds.

## 2. Reference wording that measurably works (keep verbatim, per forge-learnings)

- `"<Picture N> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject N>"`
- `"<Subject N> is the exact same woman shown in <Picture N> of the reference pictures and in the first 5 seconds
  of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity"`
- `"the face fills ..."` (face-crop framing clause), `"dynamic video, fluid natural motions"`.
- Give EVERY reference its own distinguishing description, and split roles by what each reference actually is:
  the approved full-body start still = bodies, skin, figures, wardrobe, setting, light and camera
  (`<Picture 1>`); the face crops = face and hair only (`<Picture 2>`/`<Picture 3>`). In `retention_analysis`
  name which picture keeps face/hairstyle and which keeps body/skin/figure.

## 3. The clothing clause

`"The light clothing worn at the start of this shot is the clothing of <Picture 1>; it is removed during the shot
and lies ... for the rest of the clip, so the bodies that become bare are the same bodies the photograph shows."`
Plus `"... is an action in the story ..."` in `retention_analysis`, so H3 does not read the start photo's clothes as
a body change.

## 4. Body / skin quality words the community swears by (state them positively)

Matte skin with visible pores and fine vellus hair, only a soft natural sheen where damp, never a waxy, plastic or
airbrushed surface; realistic natural body proportions with joint definition; real adult body mass with weight on
waist, hips, thighs and breasts; five separate fingers; natural elbow and knee hinging; fluid, physically plausible
motion; shallow depth of field, cinematic lighting. Community rule: describe what you WANT, never `don't X` /
`no X` in the prompt body.

## 5. Contradiction phrases that MUST be absent (they cancelled the body reference)

`"body proportions"` (inside crop sentences), `"are new and are not taken from"`,
`"used for the faces and the hair of the two women only"`, `"These two crops are the only visual references"`,
`"carries no reference pictures at all"`. Assert them absent in the builder gate and prove the gate fires by
restoring the old wording in a clone (self-destruct probe).

## 6. Length, repeats, negatives

- Prompt length is NOT a sampler budget: the encoder is the Qwen3VL-32B path
  (`comfy/text_encoders/minimax.py MiniMaxH3Tokenizer`, `embedding_size 5120`); a 6.5k-char prompt is ~1.7k tokens.
  Overflow raises `ValueError "MiniMax H3 text segment exceeds the supported prompt length"` - it does not truncate.
  Community trick to try: paste the structured prompt twice.
- A negative prompt needs `CFGGuider` (pos+neg+cfg) + `NAGuidance` (cond+uncond, ~2x per step); the stock graph has
  NO cfg key. `H3ContinuumSamplerV39` has no negative/CFG key at all, so `no:` lines get appended to
  `sequence_prompt` there.
- c1 (chunk 2) MUST carry references too - a chunk with no `<Picture N>` drifts (notes/hc_redo_research_20261023.md L1).

## 7. Open prompt-quality work (PQ1)

Research + cite: TenStrip 10Eros-Max model card and discussions (`huggingface.co/TenStrip/10Eros-Max`, incl. #50
prompt format per version and #49 prompt-writer system prompts), MiniMax `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`,
`huggingface.co/MiniMaxAI/MiniMax-H3` discussions, civitai guides. Save citations to `notes/prompt_guide_20261023.md`
and the rewritten prompts verbatim to `notes/im1_prompts.md`. Reddit `.json` endpoints return a "Blocked" HTML page
from this box - cite HF/GitHub/civitai instead.

## Sources

`C:/AI/community/specs/prompt_v2/*.txt`, `notes/hc_r3b_c0.txt` + `notes/hc_r3b_c1.txt`,
`notes/hc_face_research_20261023.md`, `notes/hc_redo_research_20261023.md`,
`notes/bq1_prompt_diff.txt`, `notes/forge-learnings.md`, `notes/settings_audit_20261023.md`.
