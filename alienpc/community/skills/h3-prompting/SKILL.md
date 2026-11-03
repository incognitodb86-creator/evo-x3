---
name: h3-prompting
description: The single home for MiniMax-H3 / 10Eros-Max prompt rules (R1-R31) on this box - output only the prompt, adults only (18+, fictional, minors = hard stop), the five prompt sections with plain audio cues at the end of the main prompt (no overall_soundscape block, TenStrip HF #77), the verbatim reference clauses that keep identity, get-into-position, PRIMARY MOTION and contact geometry, the response dial and slap-to-face, garment end states, <Video 1> continuation, positives-only plain wording, LoRA trigger hygiene, the detail checklist, the contradiction phrases to keep out and 4 worked examples. The REF2VA lane (single clip and multi-cell chain) is the separate skill
`h3-max-ref2va-prompt` (rules R32-R44); references/ref2va-lane.md and references/ref2va-chain-lane.md are pointers to
it. The director's prompt sections point to this file. Use when writing, reviewing or auditing any H3 prompt text: notes/hc_*.txt, specs/prompt_v2, a run's prompt file, a MiniMaxH3ReferenceToVideo paste, a multi-cell chain, an I2V POS, or a Continuum sequence_prompt. Since 2026-11-03 the REF2VA lane (the standing Max lane) is its own skill,
`h3-max-ref2va-prompt`, with REF2VA-specific rules R32-R44; this file keeps R1-R31 (all lanes) and the rule index, and
no rule sentence is duplicated between the two.
---

# H3 prompting - the single home (U2, 2026-10-29)

Every MiniMax-H3 / 10Eros-Max prompt rule on this box lives in this file and only here. The REF2VA lane files in references\ (ref2va-lane.md, ref2va-chain-lane.md),
and the `alienpc-hardcore-i2v-director` prompt sections point here and must not restate a
rule; a rule duplicated in two skills is a defect (plan `C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md`,
unit U2, check "each rule string appears in exactly one skill"). Rule numbers are stable: cite them as `R11` in a
review, a diff gate or a commit message, never the sentence.

**Voice.** Write as an expert H3 shot director for adult fiction: explicit concrete motion, precise verbs, sensory
detail, clean grammar, no filler, no plot summary, one act per clip; say what happens.

Model/lane facts (beta7 dials, node names, ports, queue, watch/triage, KEEP policy) stay in `h3-hc-render`,
`alienpc-local-video-ops` and the director - this file is prompt text only.

**Lane split (2026-11-03).** The REF2VA paste lane for H3-Max is the skill `h3-max-ref2va-prompt`
(`C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md`, rules R32-R44, chain lane in its `references\chain-lane.md`);
REF2VA is the standing Max lane unless Derek names another lane. This file keeps R1-R31, which apply to every lane
including REF2VA, plus the rule index (section 9). A rule sentence lives in exactly one file; numbers are box-unique
and stable; a REF2VA paste is gated by section 5 here **and** section 5 of the REF2VA skill.

## 0. Output contract

**R1 - Output only the prompt.** When asked for a prompt, deliver the prompt text and nothing else: no preamble, no
options, no explanation, no self-review, no word count in the paste. Write it to a plain `notes/*.txt` (or the run
dir's prompt file) first, then embed it in the builder, so prompts stay diffable and the prompt/graph variables stay
separable. Counting words is a private check, never output (PROMPT.md item 1c: "Count words; nothing else").

**R2 - Adults only, 18+.** Every subject is a **fictional adult**; the canon age declared inside the prompt stays
**21+ with a stated age** (the p15 writer-skill convention: "a grown woman aged 28 by canon declaration"). Minors
are a **hard stop**: pause any item whose image shows a minor. Never sexual content of a real identifiable person;
character labels are folder names, not real people.

**R3 - Fiction and policy text never enter the paste.** No governance/safety/consent-policy sentences, no "this is
fiction", no age-rating boilerplate, no model-name instructions. Consent, when Derek states it, is one plain clause
in `summary` (R21), not a paragraph.

**R4 - The youth guard is never edited and its path is never typed.** The adults-only module named in AGENTS.md
"## Scope" (`scripts/comm.py`, `guard_ok`, `prompt_strings`, and `scripts/tests/test_p6_review.py` +
`test_guard_scope.py`) is untouched by prompt work; the guard matches command TEXT, so never put that path in a
command string. `run_graph_job.py` runs `comm.guard_ok` before any POST - never loosen it.

## 1. Shape of the paste

**R5 - Five sections, in this order, one paste per act.**

1. `subject_definitions:` - one line each for `<Picture N>`, `<Subject N>`, and the place if it must stay.
2. `summary:` - starts with the task-type tag (R6), then one short paragraph: who, where, what happens, and the
   entry transition when the still is not already in position (R16).
3. `retention_analysis:` - one line per label: `fully_preserved` / `partially_preserved` / `attribute_transfer` /
   `weak_reference`, naming which picture keeps face-and-hair and which keeps body/skin/wardrobe (R11, R13).
4. `detailed_description:` - the shot, beat by beat in time order (R8, R9), then the plain audio cues (R7).
5. `continuation:` - only for continued clips, and it is exactly the R10 line.

**R6 - Task type.** Default `[reference generation]`. `keyframe completion` is a labelled one-axis try, never a
silent freeze. `MiniMaxH3ReferenceToVideo` does not pin frame 0 (the still is conditioning); first-frame lock is
`MiniMaxH3ImageToVideo`, and a reference image cannot be mixed with it on one node.

**R7 - Audio is plain cues in the main prompt, never a section. No `overall_soundscape:` block, no
`non_diegetic_music:` block, no music/foley score.** TenStrip (model owner, HF 10Eros-Max discussion #77, quoted in
`C:\AI\community\notes\web\tenstrip_hf77_audio_20261029.md`): *"Don't use developer H3 style prompting, it causes
the most interference. 'overall_soundcape' especially is actually the easiest way to introduce extremely bad audio
and will cause the model to go out of it's way and start putting cartoon sounds on the output and ignore prompt and
should be deleted. Prompt very normal audio queues in prompt or at the end of the main prompt."* So: at the END of
`detailed_description`, one or two sentences naming the real sounds in the order they happen - room tone, breath
through the nose, skin-on-skin impact, wet friction, fabric rustle, footfall - each tied to the action that makes
it. No "soundscape", no soundtrack, no music unless Derek asks for it by name. (Old runs and old prompts keep their
`overall_soundscape:` sections: those blocks are **deleted** for anything written fresh on this box, and nothing is
re-rendered from them.)

**R8 - Shot headers and time, no transition words.** Camera/lens/light sentences come before `[Shot 1]`; beats carry
clock ranges that total the clip duration (`[Shot 1] 00:00.000 - 00:04.000 ...`, `[Shot 2] At 00:05.000, the camera
cuts to ...`). Never use "then / after / afterwards / next" to move the story: those trigger premature cuts. One
continuous shot is one `[Shot 1]`.

**R9 - Length.** `detailed_description` has no word cap - long, literal, in time order beats short (TenStrip's own
advice; a 6.5k-char prompt is about 1.7k tokens). No minimum or maximum word count anywhere (Derrick 2026-10-29). The only hard limit is the encoder: overflow raises
`ValueError "MiniMax H3 text segment exceeds the supported prompt length"`; it never truncates
(`comfy/text_encoders/minimax.py MiniMaxH3Tokenizer`, `embedding_size 5120`).

**R10 - A continued clip begins exactly:** `[video continuation] Continuing seamlessly from <Video 1>.`
(`<Video 1>` = the previous clip). A continuation without `<Video 1>` is invalid - rewrite it. Only a hard cut to a
new scene has no `<Video 1>`, and it must be labelled `hard cut`. Storyboard runs reference `<Shot Reference N>` for
their panel. Every continued clip carries references again: a chunk with no `<Picture N>` drifts
(`C:\AI\community\notes\hc_redo_research_20261023.md`).

## 2. Keeping identity, bodies and wardrobe

**R11 - Use these clauses verbatim** (measured, `notes/forge-learnings.md`, `notes/hc_face_research_20261023.md`):

- `<Picture N> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject N>`
- `<Subject N> is the exact same woman shown in <Picture N> of the reference pictures and in the first 5 seconds of
  this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity`
- `HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, no melt, merge or extra digit`
  whenever hands are visible.
- Retention lines in the TenStrip #63 shape: `<Subject 1> (appears in [Shot 1]): fully_preserved - <what keeps what>`
  and `<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - <setting, light, framing>`.

**R12 - The clothing clause** (when wardrobe comes off during the shot):
`The light clothing worn at the start of this shot is the clothing of <Picture 1>; it is removed during the shot and
lies <where> for the rest of the clip, so the bodies that become bare are the same bodies the photograph shows.`
Plus the matching `... is an action in the story ...` clause in `retention_analysis`, so H3 does not read the start
photo's clothes as a body change.

**R13 - Split the jobs of the references** and give every reference its own distinguishing description: the approved
full-body start still = bodies, skin, figures, wardrobe, setting, light and camera (`<Picture 1>`); face crops = face
and hair only (`<Picture 2>`, `<Picture 3>`); a pose reference (`<Picture 2>` in a two-ref arm) = target pose only.
Say which is which in `subject_definitions` and `retention_analysis`.

**R14 - Describe the start image from its own text records** (panel prompt, notes, the run's facts file) - looking
at the image itself needs Derek's specific permission (`alienpc-pi-rules`). The model follows words over pixels for
materials and wardrobe, so cover in order: fabric and opacity (sheer / mesh / opaque, wet / dry, skin through it),
fit and construction (straps, ties, how it comes off), light (direction, colour, rim, wet specular), composition
(crop, camera height, aspect, placement), props and surfaces that move or make sound, hair and visible skin detail.
Name each garment's **end state** and say it stays visible ("the top falls to the stone floor beside her boots and
stays there"); a garment that moves or comes off gets its own `<Subject N>` and a `retention_analysis` line. Copy
wardrobe and jewellery words from the panel prompt word for word: one colour, one item, one place.

**R15 - `ref_image_size` default is `max`** (B2, Derrick 2026-10-30; `max` only downscales sides over 2048). `match` (caps a
reference to the canvas pixels) is a labelled pre-B2 option only, used when a brief names it; never a silent default.

## 3. Motion, contact, anatomy

Moved verbatim to [references/motion-contact-anatomy.md](references/motion-contact-anatomy.md) (rules R10, R16, R17, R18, R19, R20, R21, R22, R23). Read it before writing motion, contact or body lines.

## 4. Wording

Moved verbatim to [references/wording.md](references/wording.md) (rules R7, R10, R21, R24, R25, R26, R27, R28, R29, R30, R31). Read it before final wording.

## 5. Detail checklist (from `p15_writer_skill.md`'s self-refine rubric, audio line updated for R7)

1. All five sections present, in order (R5), task type named (R6); continued clips carry the R10 line.
2. Every subject declared a fictional adult with a stated 21+ age; zero terms that could trip the youth guard.
3. No `overall_soundscape:` / `non_diegetic_music:` block; audio is plain cues at the end of the description (R7).
4. Retention lines present and specific (R11); the clothing clause present when wardrobe comes off (R12).
5. Skin words: dry matte, natural pores - zero `oiled / glossy / sheen / wet sheen / glistening`.
6. Literal anatomy named at the contact points; five-finger hands named; screen side and contact plane restated.
7. Zero `then / after / afterwards / next` in `detailed_description` (R8); zero negatives in the body (R24).
8. Timed beats total the clip length; PRIMARY MOTION named with tempo (R17); motion alive on the last frame.
9. Camera line exactly R23; no "reveal" on a static hold.
10. Response dial is the one Derek named (R21); a bare slap is to the face (R22); garments have named end states.
11. Nothing outside the prompt was output (R1); the diff gate shows only this cell's axis (R30); no trigger word
for a LoRA that is not loaded (R31).
12. **REF2VA pastes only:** run the additional gate in section 5 of `h3-max-ref2va-prompt` (labels vs wired inputs,
task-type tags, role-scoped retention lines, frame anchors, style opening, language, no `<scenetrans>`, speech form).

## 6. Worked examples

Moved verbatim to [references/worked-examples.md](references/worked-examples.md).

## 7. Pointers (who defers to this file)

- **REF2VA (the standing Max lane): skill `h3-max-ref2va-prompt`** - `C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md`
  (rules R32-R44, its own gate, paste skeleton) and `...\references\chain-lane.md` (multi-cell chains). Its section 2
  is the REF2VA reading of R5, R6, R8-R15; it never restates a rule of this file. The two files this pointer replaces
  are archived at `C:\AI\community\archive\2026-11-03-ref2va-split\`; thin pointers remain at
  [references/ref2va-lane.md](references/ref2va-lane.md) and [references/ref2va-chain-lane.md](references/ref2va-chain-lane.md)
  so old citations resolve.
- `alienpc-hardcore-i2v-director` "Max POS
  craft / H3 prompt shape / Static Shot / static hold vs reveal / frame-one identity" - all point here; they keep
  only their lane (node wiring, chain scheduling, still→intent match, watch/triage, queue).
- `h3-hc-render` owns graph/request wiring and the render dials; this file never sets steps, shift, VSA, fps.
- `alienpc-stills-pose-edit-prompting` owns FLUX.2 still prompts; `alienpc-ltx-i2v-prompting` is the LTX baseline
  lane (its own POS rules) and is not a Max prompt source.
- The writer model's system prompt `C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md` (the only copy
  on this box - `C:\AI\community\notes\` has none) keeps its
  own rubric and few-shots: it is a model prompt, not a rule file, so it is not merged and not edited here. Its
  `overall_soundscape:` instruction is superseded by R7 for anything written fresh on this box.

## 8. Sources

Model card and community: `huggingface.co/TenStrip/10Eros-Max` discussions #77 (audio, saved at
`C:\AI\community\notes\web\tenstrip_hf77_audio_20261029.md`), #63 (retention lead-in lines), #50 (prompt format per
version), #49 (prompt-writer system prompts); MiniMax `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`
(`huggingface.co/MiniMaxAI/MiniMax-H3`); civitai guides. Reddit `.json` endpoints return a "Blocked" HTML page from
this box - cite HF/GitHub/civitai.
Box evidence: `C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md` (persona, standards, rubric, its two
few-shots), `C:\AI\community\notes\hc_face_research_20261023.md`, `notes/hc_redo_research_20261023.md`,
`notes/bq1_prompt_diff.txt`, `notes/forge-learnings.md`, `notes/prompt_guide_20261023.md`, `notes/im1_prompts.md`,
`C:\AI\community\specs\prompt_v2\*.txt`, `C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\prompt_seg0.txt`
(the current B2 KEEP paste, with the old audio blocks), `C:\AI\community\skills\h3-hc-render\SKILL.md`,
the 2026-10-28 prompt corrections in MEMORY (slap-to-face, the response dial, beta 7 dials).
Upstream (read 2026-11-03): MiniMax-AI/MiniMax-H3 `skills/h3-prompt-writing/references/ref-en.txt` and `base-en.txt`
(local clone, HEAD `199b7d0`, 2026-10-28) - the source of the REF2VA rules R32-R41 in `h3-max-ref2va-prompt`; the
reason our paste shape differs from the hosted format is **R32** there. Reviews: `notes\2026-11-03-h3-upstream-prompt-skill-review.md`,
`notes\2026-11-03-h3-ref2va-skill-split.md`.

## 9. Rule index and rule homes (citations resolve from this table)

| Numbers | Where the rule text lives |
| --- | --- |
| R1-R4, R7-R9, R16-R31 | this file, sections 0-4 (R16-R23 in `references/motion-contact-anatomy.md`, R24-R31 in `references/wording.md`) |
| R5, R6, R10-R15 | this file, sections 1-2; the REF2VA reading of them is section 2 of `h3-max-ref2va-prompt\SKILL.md` |
| R32-R44 | `C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md` - REF2VA on H3-Max only: R32 hosted audio fields,
R33 label set and wired inputs, R34 task-type tags, R35 role-scoped retention, R36 frame anchors and the alignment line,
R37 speech form, R38 language and visible text, R39 style opening, R40 continuity tokens, R41 length provenance,
R42 the graph contract, R43 the chain lane, R44 the REF2VA gate |
| Render dials, graph wiring, queue | `h3-hc-render`, `alienpc-local-video-ops` (never prompt rules) |

A new rule is added in the file that owns its lane and gets the next box-unique number; never renumber an old rule.
