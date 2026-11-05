---
name: h3-max-ref2va-prompt
description: The REF2VA prompt lane for MiniMax H3-Max / 10Eros-Max beta7 on this box - the standing Max lane unless Derek directs otherwise. Use for any paste into MiniMaxH3ReferenceToVideo: the reference-label set for images, videos and audio, task-type tags, retention lines, frame anchors, style opening, language and visible-text rules, the speech form, the node contract and graph facts for our builder, the chain lane and the pre-queue gate. Cross-lane prompt rules are NOT restated here: they are R1-R31 in the h3-prompting skill and every one of them applies to a REF2VA paste. Not for render dials, graph wiring, queue (h3-hc-render / video-render) or FLUX stills (alienpc-stills-pose-edit-prompting).
---

# H3-Max REF2VA prompt lane (AlienPc setup)

Created 2026-11-03 at Derek's request: the REF2VA lane is its own skill, scoped to **H3-Max (10Eros-Max beta7)
and this box's graph**, not a section of the cross-lane file. Upstream source for the new rules: MiniMax-AI/MiniMax-H3
`skills/h3-prompt-writing/references/ref-en.txt`, read at clone HEAD `199b7d0e1fd95e7b3eafa8c15eca692534142427`
(2026-10-28); review and full diff `C:\AI\community\notes\2026-11-03-h3-upstream-prompt-skill-review.md`,
patch record `C:\AI\community\notes\2026-11-03-h3-ref2va-skill-split.md`.

## 0. Lane status

- **REF2VA is the standing Max lane.** A Max clip is a REF2VA paste into `MiniMaxH3ReferenceToVideo` unless Derek
  directs another lane by name (first-frame I2V, stills).
- This skill owns only REF2VA-specific rules, numbered R32-R44. Rule numbers are box-unique and stable: cite
  `R<n>` in a review, a gate or a commit message, never the sentence.

## 1. The shared rules (h3-prompting, unchanged, all apply)

R2. Render rules (adults only, no real likeness, guard_ok) live in C:\AI\render\AGENTS.md; run render work from C:\AI\render.

`C:\AI\community\skills\h3-prompting\SKILL.md` is the single home for the cross-lane rules; read it first, do not
restate it here.

- **All of R1-R4 and R16-R31 apply to a REF2VA paste**, unchanged (output contract, adults-only and the youth guard,
  motion/contact/anatomy, the response dial, camera line, positives-only, plain wording, sound nouns, contradiction
  phrases, label discipline, one pose per cell, the pre-queue diff gate, LoRA trigger hygiene).
- **R5, R6, R8-R15** are the paste shape, and this file states their REF2VA reading: §2 below, items 1-8.
- **The REF2VA checklist is section 5 of `h3-prompting` plus section 5 of this file.** The shared 11 items are not
  copied here; R32-R44 is a superset.
- The rule index is **§7 of `h3-prompting`**.

## 2. REF2VA reading of the paste shape (R5, R6, R8-R15 as they apply here)

1. **R5 (REF2VA reading of the shape).** Five sections in that order (`subject_definitions`, `summary`, `retention_analysis`,
   `detailed_description`, and `continuation:` only on continued clips). The reference image is **conditioning**, not
   frame 0; no keyframe-alignment line (see R36).
2. **R6 (REF2VA reading of the task type).** `[reference generation]` is the default tag. `[video continuation]` only on
   continued cells (R10). `[keyframe completion]` is a labelled one-axis try. Nothing in our graph emits
   `[video editing]` / `audio reuse` / `audio reference` today (see R33, R34).
3. **R7 (REF2VA reading of audio).** Plain real-sound cues at the end of `detailed_description`; no
   `overall_soundscape:` / `non_diegetic_music:` block (R32 names why upstream has them).
4. **R8/R9 (REF2VA reading).** `[Shot 1]` untimestamped, later `[Shot N] At MM:SS.mmm`; beats total the clip; no word
   cap (R41 for the provenance of upstream's word range).
5. **R10 (REF2VA reading).** A continued cell opens exactly `[video continuation] Continuing seamlessly from <Video 1>.`
   On this box that chain mechanism is latent-tail continuation (`comm.py build()`:
   `MiniMaxH3GuidedContinuationWindow` + `MiniMaxH3LatentTailGuide` + `MiniMaxH3AppendContinuation`); the phrase is a
   prose cue to the model about the preceding clip in latent context, **not** a `<Video N>` reference label - a real
   `<Video N>` exists only when the graph wires `ref_videos` (R33).
6. **REF2VA reading of R11-R14.** The verbatim identity clauses, the retention lead-in, the clothing clause, the split
   jobs of the references, and describing the start image from its text records. Retention lines follow R35.
7. **R15 (REF2VA reading).** `ref_image_size: "max"` (the graph sets it; the node default is `match`).
8. **R28 (REF2VA reading of labels).** Ordinals are 1-based per label type in connection order, and they follow the
   node's presentation order (R33).

## 3. REF2VA-specific rules

**R32 - Do not paste the hosted pipeline's audio fields.** Upstream's Ref2VA format has six sections because two of
them (`overall_soundscape:`, `non_diegetic_music:`) are the output of **H3-Context-IR**, a hosted preprocessing
system explicitly *not* in the open-source release (MiniMax-H3 README, "H3-Context-IR ... is not included in this
open-source release"). We run H3-Base directly, so the paste keeps the five local sections and R7's plain audio cues:
shot-synchronised real sounds belong in `detailed_description` (upstream's own example puts "a canned audience laugh
begins immediately after the line" in the shot, not in an audio block). Measured reason for the ban: TenStrip (model
owner, HF 10Eros-Max discussion #77) - "overall_soundcape ... is actually the easiest way to introduce extremely bad
audio ... should be deleted."

**R33 - The label set, and what our graph can feed it.** The node contract
(`ComfyUI/comfy_extras/nodes_minimax_h3.py:243-284` + `comfy/text_encoders/minimax.py:3-13`) is:

| Label | Fed by | Limit | Meaning (upstream ref-en §2) |
| --- | --- | --- | --- |
| `<Picture i>` | `ref_images.ref_image_N` | 9 | a concrete frame / keyframe / composition / storyboard anchor, or the source cited inside a `<Subject N>` definition |
| `<Video k>` | `ref_videos.ref_video_N` (24 fps, 2-15 s, ≥5 frames, trimmed to ≤ the clip length) | 3 | a whole-video relationship: an editing source, a continuation start, or its camera movement / cuts / rhythm / temporal structure |
| `<Audio j>` | `ref_video_audios.ref_video_audio_N` (index-paired to `ref_video_N`) and `ref_audios.ref_audio_N` | 3 + 3 | an audio signal copied or referenced: a voice timbre, a BGM, dialogue/lyric content, beat, continuity |
| `<Subject N>` | not an input | - | the reusable visible content (person, garment, prop, environment, pose, style) abstracted from one or more of the above |

Facts to obey: presentation order is images, then each video's soundtrack `<Audio j>` immediately before its
`<Video k>`, then standalone audio; ordinals count **per label type** in that order, so one source video can be
`<Video 1>` and `<Audio 2>` (`nodes_minimax_h3.py:245-249,335`, ref-en §2.5); audio labels are emitted as text only -
audio never enters the text encoder's vision path, its pixels/waves go through the audio VAE (`minimax.py:10,178`).
**Today `scripts/comm.py first_pass()` wires `ref_images.ref_image_1` only, so `<Video N>` and `<Audio N>` are a
labelled arm**: a builder change is required, and a paste may use a label only when that input is wired. A
reference video with sound does not create an `<Audio N>` by itself.

**R34 - Task-type tags: the full set and the honest subset.** Upstream's tags (ref-en §3) are
`keyframe completion`, `reference generation`, `video editing`, `video continuation`, `audio reuse`,
`audio reference`, joined with ` + ` in the `summary:` prefix, each at most once, chosen by the role the asset
actually plays: `[video editing]` only when a supplied source video is directly modified (never for images), and an
`[video editing]` summary opens `The target video is an edited version of <Video 1>.`; a video that supplies only
camera movement, cuts or rhythm is `reference generation`, not `video editing`; `audio reuse` = the signal is copied,
`audio reference` = only timbre, style, words, beat or continuity are followed. **Our graph emits
`[reference generation]`, `[video continuation]` (R10) and, in a labelled arm, `[keyframe completion]` (R6); do not
write the editing or audio tags while the inputs of R33 are unwired.**

**R35 - Retention lines are role-scoped.** Keep R11's lead-in and markers, and add ref-en §4: choose each marker only
inside the role already defined for that label in `subject_definitions`; list every shot a subject appears in
(`<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - ...`); **new actions, backgrounds and story events
in the target clip are not losses of reference fidelity** - do not hedge a `fully_preserved` line into
`partially_preserved` because the clip adds movement. `<Audio N>` has its own markers
(`fully_copy` / `partially_copy` / `reference` / `weak_reference`) and belongs in `retention_analysis` only in the
audio arm; `(Sx)` speaker IDs never appear in `retention_analysis`.

**R36 - Frame anchors in ref mode are prose, not an alignment line.** Name frame roles inside
`subject_definitions` and `detailed_description`: `<Picture 2> is the first frame of [Shot 1], showing ...`,
`the shot begins from <Picture 1>`, `the shot's keyframe corresponds to <Picture 2>`, `the shot ends on <Picture 3>`
(ref-en §5.3). A panel/shot-planning reference is one line: `<Picture 3> is a storyboard reference for [Shot 1] and
[Shot 2], defining their viewpoint, subject placement, and shot order.` (ref-en §2.2) - that is the REF2VA form of the
`<Shot Reference N>` used by storyboard/chain runs (R10). Do not paste the base-mode alignment line into a REF2VA
prompt: `For the target video, at 0.00 seconds ...` and `How the reference pictures align with the target video - ...`
belong to the T2VA/I2VA/FL2VA/L2VA format (base-en §2.1), no core ComfyUI node injects them
(`comfy_extras/nodes_minimax_h3.py` contains no such string), and the frame-lock in ref mode is
`[keyframe completion]` + a `<Picture N>` definition (R6, R36). Those lines are for the first-frame I2V lane only
(`MiniMaxH3ImageToVideo`, built at `comm.py:128,149`).

**R37 - Speech is a labelled arm, and it has an exact form.** The tokens exist on this box
(`comfy/text_encoders/minimax.py:32 MINIMAX_EXTRA_TOKENS = {"<d>": 151669, "</d>": 151670, "<|cutoff|>": 151671,
"<|lyrics_start|>": 151672, "<|lyrics_end|>": 151673, "<|caption_start|>": 151674, "<|caption_end|>": 151675}`) and
upstream's ref example uses them. **The default on every lane is no speech**: briefs set a `no_speech` lock and the
last full pack ran "no-speech on every arm" (`notes\2026-10-30-terrace-b2v2-changelog.md:128,131`), and R26 keeps
dialogue words out of the sound vocabulary. No rule of ours bans speech, so the old claim "H3 does not do speech on
this lane" (removed from R26 on 2026-11-03) is a brief lock stated as a model fact, and is not a reason. When speech
is asked for, write it as:

- `<Subject N> (S1) ... says, <d>[English] exact words</d>` - the subject label keeps identity, `(S1)` is the speaker;
  IDs are assigned once in the order of the first real vocal events and reused everywhere; joint speech is `(S1,S2)`;
  people who never vocalise get no ID (base-en §4.4, ref-en §5.4).
- Voice-over: the exact phrase `says in an off-screen voiceover`, and immediately after the `<d>` block state that the
  on-screen character's lips remain completely closed (base-en §4.4).
- Inside `<d>`: only the language tag and the words, verbatim, in their original language; `[unclear]` for
  unintelligible spans, never a guess; punctuation limited to `, . ? !`; no tildes, emoji, bullets, repeated or
  decorative punctuation; end statements, questions and exclamations with `. ? !` before `</d>` (ref-en §5.4).
- When only a timbre is referenced (`<Audio N>` in the audio arm), do not carry the reference audio's words into the
  clip (ref-en §5.4).
- Before any render of a speech arm: Derek's GO (a render is always his GO) and a labelled A/B cell, because speech
  has never been measured on this lane.

**R38 - Language, and visible text.** All five sections are English. Preserve the original language only inside `<d>`
and for text visibly present in the scene (ref-en preamble). Visible on-screen text - sign, banner, label, subtitle,
neon - is quoted verbatim in English double quotes, untranslated: `A red neon sign reading "营业中" glows above the
doorway.` (base-en §4.5).

**R39 - Open `detailed_description` with the style, in one or two sentences, before `[Shot 1]`.** For our lane: the
photographic style, lighting and grain the start still shows (`The target video is in a realistic photographic style
with warm late-light and shallow depth of field.`), derived from the start image's text records (R14). Then the
camera/lens/light sentences and `[Shot 1]` per R8/R23; keep the camera line exactly R23.

**R40 - `<scenetrans>` does not exist in this build; continuity is prose.** The token table above has no
`<scenetrans>`, so writing it is a defect. Where upstream writes `<scenetrans>` at both ends of a line crossing a
cut, write the continuity in prose (`continues seamlessly across the cut`, `continues uninterrupted into the next
shot`, `carries over from the previous shot`, `remains audible across the transition`). `<|cutoff|>` is a real token
for speech truncated by the end of the clip. The token names are exactly as in the table: `<|cutoff|>`, not
`<cutoff>`.

**R41 - Length, with provenance.** Keep R9: no word cap, long literal beats short, the only hard limit is the
tokenizer overflow `ValueError "MiniMax H3 text segment exceeds the supported prompt length"` (`minimax.py:160`).
Upstream's "normally 350-500 English words" (ref-en §5.2) is the hosted rewrite writer's style target for generic
clips, not a model limit, and short is not a goal.

**R42 - The paste must match what the graph can feed.** Section 4 is the builder contract: `ref_image_1` and
`ref_image_size: "max"` only today; no `ref_videos` / `ref_audios` wiring. Any label of R33 beyond `<Picture N>`
needs a builder change first, and a paste that uses an unwired label fails gate item 1.

**R43 - A chain of REF2VA cells** is `references/chain-lane.md` in this skill: shared subject definitions pasted by
the builder, identical labels and ordinals in every cell (R28, R33), the R10 prose opening plus the latent-tail
mechanism (R33), one axis per cell (R29), and the R30 diff gate per cell.

**R44 - The REF2VA gate** is section 5 of this file, run **after** section 5 of `h3-prompting` (its item 12 points
here). Both gates pass before a cell is staged; a gate failure is fixed in the paste, never by relaxing a rule.

## 4. Our graph, so the paste matches what can be fed

- Node: `MiniMaxH3ReferenceToVideo` on 10Eros-Max beta7 via llama-swap `:8080/comfyui`; model dials, wiring, queue
  and triage are `h3-hc-render`.
- Builder: `C:\AI\community\scripts\make_b2_request.py` -> `scripts/comm.py` `build()/first_pass()`; mode `r2v` wires
  `ref_images.ref_image_1` + `ref_image_size: "max"`; a reference image cannot share a node with
  `MiniMaxH3ImageToVideo` (R6); the builder has no `ref_videos` / `ref_audios` wiring today (R33).
- Chain lane: multi-cell chains are `references/chain-lane.md` in this skill; a chain is N cells from one Condition
  still, cells built by the parameterized builder, one axis per cell (R29, R30).
- A render is Derek's GO; KEEP is Derek's only.

## 5. REF2VA gate (run after `h3-prompting` section 5, do not re-run it)

1. Label audit: every `<Picture / Video / Audio / Subject N>` used in the paste is wired in the graph (R33); ordinals
   are 1-based per type in the node's presentation order; a video-only reference has no invented `<Audio N>`.
2. `summary:` tag prefix is from the honest set (R34) and matches the wired inputs; a continued cell carries R10.
3. Retention lines are role-scoped, list every shot a subject appears in, and are not weakened by added action (R35).
4. No base-mode alignment line anywhere (R36); frame roles named as prose anchors (R36).
5. Style opening present before `[Shot 1]` and derived from the start image (R39).
6. No `<scenetrans>`; continuity in prose; if the token appears anywhere in the paste, stop (R40).
7. No speech unless Derek asked for it; if present, the R37 form is exact, and the render needs his GO.
8. Sections English, original language only inside `<d>` and for quoted visible text (R38).
9. The node contract checks for the lane: `C:\AI\community\scripts\verify_cell.py` and the adults-only tests named in
   `references/chain-lane.md` / `h3-prompting` gate; then the R30 diff gate.

## 6. Paste skeleton (structure only; content comes from the run's records, R14)

```
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>
<Picture 1> is the start frame of [Shot 1] for setting, light and framing
<Subject 1> is the woman in <Picture 1>: <face/hair per the records>, a fictional adult, canon age 28
<Subject 2> is <partner/garment/prop per the records> ...
summary:
[reference generation] <who, where, the entry transition, one consent clause when Derek states it (R21)>
retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe per <Picture 1>
<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - setting, light, framing
<the clothing clause line, R12, when wardrobe comes off>
detailed_description:
<one or two style sentences, R39> <camera/lens/light sentences, R23>
[Shot 1] 00:00.000 - 00:0X.000 <the get-into-position clause (R16), PRIMARY MOTION with tempo (R17), contact
geometry (R19), the response dial Derek named (R21), garment end states (R14), the shot alive on the last frame>
<one or two plain real-sound sentences in the order the sounds happen, R7>
continuation:
[video continuation] Continuing seamlessly from <Video 1>.   (R10 - continued cells only)
```

Worked, full-length examples stay in `h3-prompting/references/worked-examples.md`; this skeleton is the structure,
and R11's clauses are copied verbatim from there.

## 7. Sources

- Upstream: MiniMax-AI/MiniMax-H3 `skills/h3-prompt-writing/` (`SKILL.md`, `references/ref-en.txt`,
  `references/base-en.txt`), read from a local clone at HEAD `199b7d0` (2026-10-28); `npx skills add
  https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing` is the vendor install - **not installed on this
  box on purpose**: two skills stating the same rules breaks the "each rule in exactly one skill" check of
  `C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md` (U2).
- Box contract: `ComfyUI/comfy_extras/nodes_minimax_h3.py:243-284,335`; `ComfyUI/comfy/text_encoders/minimax.py:3-13,32,160,175-178`;
  `C:\AI\community\scripts\comm.py:120-149` (what our builder feeds the node).
- Model owner measurements: TenStrip HF 10Eros-Max #77 (audio), #63 (retention lead-in), #50/#49 (format per version).
- Review and patch records: `C:\AI\community\notes\2026-11-03-h3-upstream-prompt-skill-review.md`,
  `C:\AI\community\notes\2026-11-03-h3-ref2va-skill-split.md`.
- Everything else (R1-R31 evidence) stays in `h3-prompting` section 8.


## Sibling: parody / INDEX identity
Named INDEX+RefMod parody runs: load `h3-parody-identity` (name + description + RefMod). Do not fold those rules into this file.

