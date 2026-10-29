---
name: h3-prompting
description: The single home for MiniMax-H3 / 10Eros-Max prompt rules (R1-R31) on this box - output only the prompt, adults only (18+, fictional, minors = hard stop), the five prompt sections with plain audio cues at the end of the main prompt (no overall_soundscape block, TenStrip HF #77), the verbatim reference clauses that keep identity, get-into-position, PRIMARY MOTION and contact geometry, the response dial and slap-to-face, garment end states, <Video 1> continuation, positives-only plain wording, LoRA trigger hygiene, the detail checklist, the contradiction phrases to keep out and 4 worked examples. ref2va-prompt, h3-ref2va-prompt-chain and the director's prompt sections are pointers to this file. Use when writing, reviewing or auditing any H3 prompt text: notes/hc_*.txt, specs/prompt_v2, a run's prompt file, a MiniMaxH3ReferenceToVideo paste, a multi-cell chain, an I2V POS, or a Continuum sequence_prompt.
---

# H3 prompting - the single home (U2, 2026-10-29)

Every MiniMax-H3 / 10Eros-Max prompt rule on this box lives in this file and only here. `ref2va-prompt`,
`h3-ref2va-prompt-chain` and the `alienpc-hardcore-i2v-director` prompt sections point here and must not restate a
rule; a rule duplicated in two skills is a defect (plan `C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md`,
unit U2, check "each rule string appears in exactly one skill"). Rule numbers are stable: cite them as `R11` in a
review, a diff gate or a commit message, never the sentence.

**Voice.** Write as an expert H3 shot director for adult fiction: explicit concrete motion, precise verbs, sensory
detail, clean grammar, no filler, no plot summary, one act per clip; say what happens.

Model/lane facts (beta7 dials, node names, ports, queue, watch/triage, KEEP policy) stay in `h3-hc-render`,
`alienpc-local-video-ops` and the director - this file is prompt text only.

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
   transition if the start image is not already in position.
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
`overall_soundscape:` sections; they are history. Nothing is re-rendered from them.)

**R8 - Shot headers and time, no transition words.** Camera/lens/light sentences come before `[Shot 1]`; beats carry
clock ranges that total the clip duration (`[Shot 1] 00:00.000 - 00:04.000 ...`, `[Shot 2] At 00:05.000, the camera
cuts to ...`). Never use "then / after / afterwards / next" to move the story: those trigger premature cuts. One
continuous shot is one `[Shot 1]`.

**R9 - Length.** `detailed_description` has no word cap - long, literal, in time order beats short (TenStrip's own
advice; a 6.5k-char prompt is about 1.7k tokens). The Ralph loop's per-pass target is 350-500 words (PROMPT.md 1c) -
that is the loop's budget, not the model's. Overflow raises
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

**R15 - `ref_image_size` default is `match`** (the production argv). `max` only as a labelled one-axis identity
cell after a watched mid-clip identity break, never as a silent default.

## 3. Motion, contact, anatomy

**R16 - Get-into-position when the start image is not in position for the act.** Never jump straight to
thrust/pump/bounce (that is where melt, floating join and orifice teleport come from). Write an ordered beat inside
`[Shot 1]` before the act - STAND, TURN, KNEEL, BRACE, SETTLE - with clock ranges, then the act, in one continuous
shot. Soften "preserve camera angle / framing" when the pose must change, and keep face/identity, wardrobe, light
`fully_preserved`. If the transition is too long for one clip, unlock the still first
(`alienpc-stills-pose-edit-prompting`), then paste. **Open state:** a cell whose only reference is `<Picture 1>` is
independent of the cell before it - do not write "opens mid-[previous beat]" unless that pose is in the still, or
you pass Multiframe / the previous clip's last frame, or the clip is a R10 continuation. Default: the first ~2
seconds establish from `<Picture 1>` into the beat, then the timed phases; get off a standing pose fast when the
beat needs pin or penetration.

**R17 - Name ONE PRIMARY MOTION with tempo and amplitude**, e.g. `PRIMARY MOTION - continuous deep frontal thrust,
about one full cycle every half second, full depth travel, hips staying in contact`, and keep that tempo for the
timed phases. Contact beats dominate the clock time; compress approach theatre. Keep the motion alive on the final
frame - end mid-energy, never a freeze tableau.

**R18 - Body inventory is explicit:** exactly one adult man and one adult woman (or the number the still shows), two
arms and two legs each, five fingers when hands are visible, one continuous torso each, breast size and body mass
locked to `<Picture 1>`. Use literal anatomical words (penis, shaft, glans, vagina, vulva, breasts, buttocks, hips,
thighs, groin, pelvis), not euphemism.

**R19 - State the contact geometry, then lock it.** Say the join: hips stacked / flush / named orifice, and the
supports (knees, hands, mattress, wall). For a vaginal cell: fully sheathed, hips flush (no tip-only, no miss, no
float), measurable in-out depth each stroke. For an oral cell: shaft past the lips with deep oral travel on the deep
stroke, not tip-lick-only. Keep the contact type constant per cell, and write the pull-out and reseat beat when the
contact type changes. No wrong-orifice teleport. Standing tip-against-fabric, floating join and grind-without-entry
are the usual FAILs even when the prose says "spear".

**R20 - Motion verbs, not mush:** hips rock, deep stroke, thrust, bounce with impact jiggle, pelvis grinds, ribs
move with breath. Phased contact beats ("lips seal mid-shaft, pull back until the tip clears, pause, re-seal") beat
"passionate oral". Anti-melt positives: readable seam, wet contact, an air gap on peel cells.

**R21 - The response dial is Derek's to name - never soften it.** In dominance/rough scenes he names the receiver's
response, `eager` **or** `not into it`; write exactly the one he names. `not into it` = flat unsmiling face, eyes on
the lens, chin level, jaw set, shoulders square, arms hanging at her sides, hips stiff, knees not opening, hands
never touching the dominant, breath tight through her nose; her body may answer mechanically (flush, punched breath,
stomach tightening) while her face stays flat, and she ends the clip the same way. State consent once in `summary`
(her word, she keeps it). Never convert it into enjoyment, moaning, arching, leaning in, gripping the dominant or a
closing smile. *(Derek 2026-10-28, runs/terrace_dom_20261028_s51083002: "she is not into it".)*

**R22 - A bare "she slaps her" lands on the face**, not the thigh or hip, unless Derek names a target. Write the
mechanics: full palm to cheek and jaw, head snaps sideways about 45 degrees, hair whips, mouth opens on a punched
breath, cheek flushes red and the flush stays. The face stays readable and `fully_preserved`: features, jaw line,
eyes, brows, fringe unchanged, head returns square to the lens, no mark, no swelling, no bruise, no tear. One slap
unless he asks for more. *(Derek 2026-10-28.)*

**R23 - Camera line is one sentence, in natural English inside `[Shot 1]`:** `The camera holds a static shot.` -
locked-off tripod, fixed framing, fixed focal length (MiniMax VIDEO_PROMPT_WRITING_GUIDE section 4.3). "Static
documentary framing" / "documentary porn framing" is not that vocab and still pushes in. No `[Static shot]` token
syntax. A static hold cannot also reveal a person who starts outside the crop - do not write "reveal"; the trained
way to fit a new full body is a zoom out, and in a static shot the entering person is cut by the existing frame
edge.

## 4. Wording

**R24 - Positives only.** Describe what is seen and heard. No `no X / never X / without X / not / none` stacks in
the prompt body, and a ban list is never the plan: the stock graph has no CFG/negative path (BasicGuider cfg 1),
`H3ContinuumSamplerV39` has no negative key at all, so naming "no X" can add X. Locks are retention markers, not
negatives. (A negative prompt needs `CFGGuider` + `NAGuidance`, about 2x per step - a separate, labelled arm.)

**R25 - Plain concrete wording, no quality buzzwords and no style mash.** Write visible, mechanical, audible detail
in time order; that is what "more descriptive" means. English prose, not JSON, not a POS template, not a thesaurus
of adjectives; skin is matte with visible pores and fine vellus hair and only a soft natural sheen where damp, never
waxy, plastic, airbrushed, oiled, glossy or glistening; realistic proportions with joint definition, real adult body
mass with weight on waist, hips, thighs and breasts, natural elbow and knee hinging, fluid physically plausible
motion; shallow depth of field and the lighting the still shows. No hedge words ("may brace" becomes the action).

**R26 - No audio/music/score vocabulary in the paste** beyond R7's plain cues: no "soundscape", no soundtrack, no
foley list, no music description, no onomatopoeia words, no dialogue lines (H3 does not do speech on this lane).

**R27 - Contradiction phrases must be absent** (they cancelled the body reference in measurement):
`body proportions` inside crop sentences, `are new and are not taken from`,
`used for the faces and the hair of the two women only`, `These two crops are the only visual references`,
`carries no reference pictures at all`. Assert them absent in the builder gate, and prove the gate fires by
restoring the old wording in a clone (self-destruct probe).

**R28 - Labels keep one meaning** in every section; tags are 1-based by connection order; each subject, garment and
place is described in full once (in `subject_definitions` and at first appearance) and referred to by label after
that. Never describe who someone looks like. Never invent wardrobe, a location or a partner that is not in the
reference - the still Derek attached or named wins.

**R29 - One pose, one finish, one wardrobe path per cell**: no `or` / pick-one forks, no multi-act montage in one
clip, no hedged alternatives. In a chain, subject definitions are identical on every cell, the same Cond still is
used unless Derek supplies new refs, seeds are unique per cell, and the summary says cell N of M and what that cell
must not do.

**R30 - Write to a file, then gate.** Before queueing: re-check every section above, the R10 line on continued
clips, the response dial Derek named (R21), the absence list (R27), the adults-only tests, and
**diff against the baseline cell - only the one axis of this cell may change** (one-variable A/B). Keep section
names and line counts identical to the baseline being compared, so a side-by-side changes references and wording,
never structure.

**R31 - LoRA trigger words only when that LoRA is loaded**, at weight 0.2-0.6 in the paste, and never a general
NSFW LoRA (Mystic and friends) on beta 7. A trigger for a LoRA that is not in the graph is a defect, not a hint.

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

## 6. Worked examples

Four examples: two are the winning prompts archived in
`C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md` (verbatim - that file carries exactly two
few-shots, so the remaining two are composed from this box's measured rules and named runs). **In the two archived
examples the `overall_soundscape:` and `non_diegetic_music:` blocks are superseded by R7**: on reuse, move those
sound sentences, unedited in wording, to the end of `detailed_description` and delete the two blocks. The
`p15_writer_skill.md` file itself is not edited - it is the writer model's system prompt.

The two **archived** winning prompts - both few-shots from `p15_writer_skill.md`, verbatim - are in the
supporting file `references/examples_archived.md` in this skill directory (they are ~10 KB each: read them when
a full paste is needed, they are not loaded with the skill). That file also carries the audio-supersession
note. Together the skill package carries **4 worked examples**, inside the plan's 3-6 range. The two below are
short, current-shape examples (audio inline, no soundscape block) built from this box's measured rules.

### Example 1 - R21 `not into it` + R22 slap to the face + R12 clothing clause

(short shape for a 124-243 f dominance cell; the pose came from the Cond, so no get-into-position beat is needed -
that is why R16 asks "is the still already in position?" first. Composed from Derek's 2026-10-28 corrections on
`runs/terrace_dom_20261028_s51083002`.)

```text
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>, and the stone terrace, evening light and framing of this shot.
<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; a fictional adult aged 26 by canon declaration, wearing the black silk blouse, grey trousers and brown belt shown in <Picture 1>.
<Subject 2> is the adult man in <Picture 1>, a fictional adult aged 31 by canon declaration, short dark hair, bare forearms, wearing the dark trousers shown in <Picture 1>.

summary:
[reference generation] On the stone terrace the man pins the woman's wrists against the wall and slaps her face once, hard; she consents to the scene and takes it flatly, facing the lens.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - face, jaw line, eyes, brows and fringe, and the black silk blouse and grey trousers, which are an action in the story: the blouse is unbuttoned during the shot and lies on the stone bench for the rest of the clip.
<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - terrace stone, railing, warm evening light from the right, framing.

detailed_description:
[Shot 1] The camera holds a static shot, waist up, three-quarter view matching <Picture 1>, warm light from the right. 00:00.000 - 00:03.000: <Subject 2>'s left forearm presses her wrists together against the stone above her head, his right hand at her waist; her shoulders square to the lens, chin level, jaw set, arms straight at her sides once his forearm drops, hips stiff, knees not opening, her hands never touching him, breath tight through her nose. 00:03.000 - 00:05.000: his palm strikes her cheek and jaw - a full palm slap, her head snaps sideways about 45 degrees, hair whips, her mouth opens on a punched breath, her cheek flushes red and the flush stays; her face stays readable, her head returns square to the lens, her expression stays flat, no mark, no swelling, no bruise, no tear. 00:05.000 - 00:08.000: her chest rises and falls fast under the open blouse, stomach tightening, skin flush spreading at her throat, while her face stays flat, eyes on the lens, arms at her sides, hands never touching him; she ends the clip facing the lens, flat, breathing hard. The black silk blouse is unbuttoned and off her shoulders and lies on the stone bench beside her for the rest of the clip. Room tone of the terrace at dusk, the flat strike of his palm on her cheek, her punched breath through her nose, the stone's faint wind and the silk sliding onto the bench.
```

### Example 2 - R16 get-into-position from a standing Cond, then R17 PRIMARY MOTION

(a standing Cond with the act not yet in position: the ordered beats come first, in the same `[Shot 1]`. Composed
to the R16/R17/R19 rules; the failure it prevents is the documented melt / floating join / thrust-from-standing.)

```text
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1> and the bedroom, lighting and framing of this shot; it also shows <Subject 2>.
<Subject 1> is the exact same woman shown in <Picture 1> ... a fictional adult aged 27 by canon declaration, in the navy camisole and matching shorts shown in <Picture 1>, standing with her back to the lens at the bedside.
<Subject 2> is the adult man in <Picture 1>, a fictional adult aged 30 by canon declaration, shirtless, in grey sweatpants, standing behind her.

summary:
[reference generation] The woman turns and lowers herself onto the bed and the man joins her from behind into a rear-linked rhythm, in one continuous shot; the shorts are drawn aside during the shot.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - face and hair, body, the navy camisole; the shorts are an action in the story and stay drawn aside at her thighs for the rest of the clip.
<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - bedroom, linens, warm front-left light, framing.

detailed_description:
[Shot 1] The camera holds a static shot, full body, matching <Picture 1>. 00:00.000 - 00:02.000: <Subject 1> turns on her heels toward the bed, plants both palms on the mattress, opens her feet wider and bends her knees, lowering her hips; <Subject 2> steps in close behind her, sets one knee onto the mattress and presses his hips flush against her buttocks. 00:02.000 - 00:04.000: his hand guides her hair aside and braces between her shoulders; her elbows bend and her forearms settle on the linens, palms flat, five fingers spread, her lower back arches. 00:04.000 - 00:08.000: PRIMARY MOTION - continuous dense rear thrust, about one full cycle every half second, full depth travel, his pelvis staying in contact with her buttocks; her head rocks forward on each deep stroke, her breasts swing under the camisole, the navy shorts stay drawn aside at her thighs and stay visible, her palms press and release on the linens. 00:08.000 - 00:10.000: the rhythm keeps its tempo to the last frame, her breath breaking into short audible exhales, her hips answering stroke for stroke. Warm room tone, the mattress springs under his knee, skin slapping against skin each stroke, wet friction at the join, her short exhales, his low breath through his nose.
```

## 7. Pointers (who defers to this file)

- `ref2va-prompt`, `h3-ref2va-prompt-chain` (`.pi/agent/skills`) and `alienpc-hardcore-i2v-director` "Max POS
  craft / H3 prompt shape / Static Shot / static hold vs reveal / frame-one identity" - all point here; they keep
  only their lane (node wiring, chain scheduling, still→intent match, watch/triage, queue).
- `h3-hc-render` owns graph/request wiring and the render dials; this file never sets steps, shift, VSA, fps.
- `alienpc-stills-pose-edit-prompting` owns FLUX.2 still prompts; `alienpc-ltx-i2v-prompting` is the LTX baseline
  lane (its own POS rules) and is not a Max prompt source.
- The writer model's system prompt `notes\p15_writer_skill.md` (both notes roots point at the same file) keeps its
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
