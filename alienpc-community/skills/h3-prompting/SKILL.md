---
name: h3-prompting
description: The single home for MiniMax-H3 / 10Eros-Max prompt rules (R1-R31) on this box. Covers output prompt formatting, five prompt sections with plain audio cues (TenStrip HF #77), verbatim identity clauses, position/motion/contact geometry, response dials, garment states, <Video 1> continuation, wording, LoRA hygiene, checklist, and worked examples. Use when writing, reviewing, or auditing H3 prompt text, run prompt files, MiniMaxH3ReferenceToVideo pastes, multi-cell chains, I2V POS, or Continuum sequence_prompts. (REF2VA lane is in h3-max-ref2va-prompt; render rules are in C:\AI\render\AGENTS.md).
---

# H3 prompting - the single home (U2, 2026-10-29)

## Named-parody precedence

For named INDEX + RefMod parodies, `h3-parody-identity` owns the tested prompt format, identity binding and exact character/actor voice, vocal-timbre and soundscape contract. Its builder format takes precedence over this file's generic picture-reference five-section, `<Picture N>`, continuation-label and no-labeled-soundscape-header prescriptions; do not rewrite the tested parody prompt to satisfy those other-lane forms. Shared motion/wording guidance applies where compatible; existing adult/minor guards remain unchanged. Ordinary picture-reference and other lanes retain their rules below.

Every MiniMax-H3 / 10Eros-Max prompt rule on this box lives in this file and only here. The REF2VA lane files in references\ (ref2va-lane.md, ref2va-chain-lane.md),
and the `alienpc-hardcore-i2v-director` prompt sections point here and must not restate a
rule; a rule duplicated in two skills is a defect (plan `C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md`,
unit U2, check "each rule string appears in exactly one skill"). Rule numbers are stable: cite them as `R11` in a
review, a diff gate or a commit message, never the sentence.

**Voice.** Write as an expert H3 shot director for adult fiction: explicit concrete motion, precise verbs, sensory
detail, clean grammar, no filler, no plot summary, one act per clip; say what happens.

Model/lane facts (beta7 dials, node names, ports, queue, watch/triage, KEEP policy) stay in `h3-hc-render`,
`video-render` and the director - this file is prompt text only.

**Lane split (2026-11-03).** The REF2VA paste lane for H3-Max is the skill `h3-max-ref2va-prompt`
(`C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md`, rules R32-R44, chain lane in its `references\chain-lane.md`);
REF2VA is the standing Max lane unless Derek names another lane. This file keeps R1-R31, which apply to every lane
including REF2VA, plus the rule index (section 9). A rule sentence lives in exactly one file; numbers are box-unique
and stable; a REF2VA paste is gated by section 5 here **and** section 5 of the REF2VA skill.

## 0. Output contract

**R1 - Output only the prompt.** When asked for a prompt, your very first emitted token must be `subject_definitions:`.
Deliver the complete five-section prompt text and nothing else: no planner notes, no "I will read/write" preamble, no
options, no explanation, no self-review, and no word count. Counting words and checking rules happen silently before token 1.

R2. Render rules (adults only 18+, guard_ok; all adult RefMods and voice refs allowed) live in C:\AI\render\AGENTS.md; run render work from C:\AI\render.

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
silent freeze. For a first-and-last-frame (keyframe completion) clip, describe the physical path that connects the two stills, not two static portraits. `MiniMaxH3ReferenceToVideo` does not pin frame 0 (the still is conditioning); first-frame lock is
`MiniMaxH3ImageToVideo`, and a reference image cannot be mixed with it on one node.

**R7 - Audio is plain cues in the main prompt, never a section. No labeled soundscape or
non-diegetic-music header, no music/foley score.** TenStrip (model owner, HF 10Eros-Max discussion #77, quoted in
`C:\AI\community\notes\web\tenstrip_hf77_audio_20261029.md`): *"Don't use developer H3 style prompting, it causes
the most interference. 'overall_soundcape' especially is actually the easiest way to introduce extremely bad audio
and will cause the model to go out of it's way and start putting cartoon sounds on the output and ignore prompt and
should be deleted. Prompt very normal audio queues in prompt or at the end of the main prompt."* So: at the END of
each beat / `detailed_description`, one to three plain sentences of natural diegetic sound (room tone, footsteps,
fabric, breath, skin-on-skin impact, wet friction) in the order they happen, each tied to the action that makes
it; no labeled header and no cartoon sound effects. No soundtrack, no music unless Derek asks for it by name. (Old
runs may still contain a labeled soundscape section: those blocks are **deleted** for anything written fresh on
this box, and nothing is re-rendered from them.)

**Dialogue - natural in-character talk; voice wording stays outside `<d>`.** Spoken lines are natural in-character talk (reacting, teasing, answering, asides to someone present), never narrating or describing what she is doing on screen, never stage directions or counts. Write each `<d>` line with that speaker's visible mouth or body action on the same beat, outside the `<d>`.
Bad: `Hands on the seat. This one is slow.` Good: `Don't rush me.`
Speech form (official H3 guide section 4.4; R37): `(S1) says in <Actor>'s exact <Character> voice with signature vocal timbre, <short concrete voice description>: <d>[English] words</d>`. Only the `[English]` tag and the verbatim spoken words go inside `<d>`. When two people speak at the same time, use a compound speaker ID such as `(S1,S2)`. Keep IDs stable.
Next to the voice name, add a short concrete description of pitch, texture and pace. Example for Sydney Sweeney as Cassie Howard: `a low, soft, breathy voice with light vocal fry, unhurried`. The Nov 6 tests showed the exact-voice name alone stayed at about 232 Hz, while adding the breathy vocal-fry cue brought it to about 200 Hz. Keep mood words that raise pitch (like `amused, teasing half-smile`) away from the speaking line.

For fictional adult OC / Cond stills (and runs without an attached voice reference): The form is `(S1) ... says in a ... voice, <d>[English] ...</d>`, with a contrasting voice written for each speaker. Never paste the celebrity / INDEX voice line (`says in <Actor>'s exact <Character> voice with signature vocal timbre...`) on OC runs.

**Hardcore dirty talk** (all characters 18+ adults, when Derrick asks for rough, degrading, or hardcore talk; always follow the speech form and voice-reference rules in `h3-parody-identity`). Write one or two fresh, crude lines for that exact stroke: short and filthy, spoken to the other adult, naming the cock, cunt, throat, depth, or being used - never a narration of the act and never a stock set. These two show the filth level, not a bank to copy; write a new line for the beat every time: she, mouth free, on a deep stroke (`Fuck that cunt, I want your cock in my guts.`); he, during a blowjob (`Choke on it. I want to hear you gag.`). Too mild, never ship: `Fuck me harder.` `Take it. Don't you stop.` (the builder sends these back NOT_READY). Bad: `Take your time. I want all of it.` `Get up behind me. Take me on my hands and knees.` `I'm taking it all off.` `Daddy` and `good girl` are adult dominance talk only; the 18+ floor stays. Do not reuse the same lines across a chain. In a 10-15 s clip, one or two lines per speaker is enough, placed on separate beats so the mouth can finish each line. Delivery stays outside `<d>` and matches the intensity (hoarse, tight, breathless, forced), not a calm, flat or default unhurried soft voice. Inside `<d>`: only `[English]` and the verbatim words, ending with `.` `?` or `!`; no ellipses, no emoji, no moan spelled as speech. Moans are not speech: non-verbal moans, breath and impact stay in the plain diegetic sound cues (R7). Do not add a labeled soundscape.

**Oral, riding and sex sound** (2026-11-11). Oral beat: she does not speak while her mouth is on him - no `(S1)` `<d>` line from the moment he is in her mouth until she pulls off (the builder sends it back NOT_READY); never write `no speech`, and never put foley inside `<d>`. Her side is diegetic foley tied to the motion: wet suction on each stroke, a gag on the deep stroke, breath through her nose. (S2) may speak on those beats; on OC / Cond stills he talks filthy (her throat, the depth, the gag, being used) while she stays silent. Cowgirl / riding: PRIMARY MOTION names her rise and her sink and a measurable lift of his pelvis off the mattress (for example a few inches) meeting her descent; if only she moves, the builder sends it back NOT_READY. Sex sound: end the shot with one to three plain diegetic sentences tied to the action (wet impact, moan, mattress creak, gag, punched breath); no labeled `overall_soundscape` or `non_diegetic_music` header and no score that would bury the body sounds (the builder flags both). A silent explicit clip with no talk and no body sound is a miss when the brief wants talk or sex sound.


**R8 - Shot headers and time, no transition words.** Camera/lens/light sentences belong inside `[Shot 1]` (agreeing with R23). `[Shot 1]` gets no timestamp. Later shots open with `[Shot N] At MM:SS.mmm, the camera cuts to ...` only at a real cut. Beats inside a shot are written as time-ordered prose using the four still-open phases (R14). Never use "then / after / afterwards / next" to move the story: those trigger premature cuts. Order comes from sentence sequence and phase wording such as "at first", "as ... builds", "by the end", never from transition words. One continuous shot is one `[Shot 1]`.

**R9 - Length.** `detailed_description` has no word cap - long, literal, in time order beats short (TenStrip's own
advice; a 6.5k-char prompt is about 1.7k tokens). Prompts run as long as the useful timed physical, visual and camera detail runs, with no word floor or quota and no padding, staying under the encoder limit. The only hard limit is the encoder: overflow raises
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
When a scene leads into sex, write a dedicated undress beat or start from a nude still; write removals as "pull down" or "slides down" rather than "takes off" (which can tear bikini strings), and name each garment as it comes off and the named surface it lands on where it stays in view; size the undress beat by the job: 124f (~5.2s) is the floor for one standing garment, while two or more garments or a lying-down removal get a longer undress beat (up to 243f) or start from a nude / near-nude still (a nude or near-nude start still needs no undress beat and can stay one 243f clip); with one primary action per short window, Beat 2 of a split undress-plus-act opens already bare, never restates the start still's clothes, and marks the wardrobe as changed rather than fully preserved.
If a start-still garment still covers the join (penetration), she must pull it aside or take it off before he enters, and the entry sentence must still carry that state — a prior pull-aside line is not enough if the entry sentence reads as if the garment still covers the join (builder W5; do not loosen).

**R13 - Split the jobs of the references** and give every reference its own distinguishing description: the approved
full-body start still = bodies, skin, figures, wardrobe, setting, light and camera (`<Picture 1>`); face crops = face
and hair only (`<Picture 2>`, `<Picture 3>`); a pose reference (`<Picture 2>` in a two-ref arm) = target pose only.
Say which is which in `subject_definitions` and `retention_analysis`.

**R14 - Describe the start image from its own text records** (panel prompt, notes, the run's facts file) - looking
at the image itself needs Derek's specific permission (`alienpc-pi-rules`). Describe only what the still shows; a cropped still never invents out-of-frame hands, feet, or garment edges. Open on the still's own angle and gaze. Frame 0 is pinned whenever a Cond still or AddGuide is used. A clip that opens on a still runs in four phases, in order, inside `[Shot 1]`: first-frame anchor, action onset, continuous development, result or reaction. Never write "don't look at the camera" or "behind the camera"; a start frame facing the lens snaps the gaze back, so start on the still's gaze instead. The model follows words over pixels for
materials and wardrobe, so cover in order: fabric and opacity (sheer / mesh / opaque, wet / dry, skin through it),
fit and construction (straps, ties, how it comes off), light (direction, colour, rim, wet specular), composition
(crop, camera height, aspect, placement), props and surfaces that move or make sound, hair and visible skin detail (a small catchlight in each eye, natural moisture on the lids, and a few flyaway hairs that move a beat late and then settle). Sheer fabric reads more opaque in gathered folds and more translucent on flat areas, with a thin air gap, a soft fabric shadow on the skin, mesh as a visible thread grid, and the cloth color mixing with the skin tone. Environment response: R23.
Name each garment's **end state** and say it stays visible ("the top falls to the stone floor beside her boots and
stays there"); a garment that moves or comes off gets its own `<Subject N>` and a `retention_analysis` line. Copy
wardrobe and jewellery words from the panel prompt word for word: one colour, one item, one place.

**R15 - `ref_image_size` default is `max`** (B2, Derrick 2026-10-30; `max` only downscales sides over 2048). `match` (caps a
reference to the canvas pixels) is a labelled pre-B2 option only, used when a brief names it; never a silent default.

## 3. Motion, contact, anatomy

Canonical rules R16–R23b live in [references/motion-contact-anatomy.md](references/motion-contact-anatomy.md) (already loaded in writer context). Apply them directly to all motion, contact, and body lines.

## 4. Wording

Canonical rules R24–R31 (including R29a) live in [references/wording.md](references/wording.md) (already loaded in writer context). Apply them directly to final wording.

## 5. Detail checklist (from `p15_writer_skill.md`'s self-refine rubric, audio line updated for R7)

1. All five sections present, in order (R5), task type named (R6); continued clips carry the R10 line.
2. No labeled soundscape or non-diegetic-music header; audio is one to three plain diegetic-sound sentences at the end of the description (R7).
3. Retention lines present and specific (R11); the clothing clause present when wardrobe comes off (R12).
4. Skin words: natural pores and fine surface detail, matte by default; `wet / sheen` only where the scene wets the skin (pool, shower, sweat); `realistic oiled skin with visible pores` is allowed - a thin oil sheen that still shows pore texture and fine detail; never `plastic / glossy / waxy` (R25).
5. Literal anatomy named at the contact points; five-finger hands named; screen side and contact plane restated.
6. Zero `then / after / afterwards / next` in `detailed_description` (R8); zero negatives in the body (R24).
7. `[Shot 1]` untimestamped, later shots cut with time only at real cuts, beats in time-ordered prose using the four phases (R8, R14); PRIMARY MOTION named with tempo (R17); motion alive on the last frame; long-run OC sex pacing (R29a).
8. Camera line exactly R23; no "reveal" on a static hold.
9. Response dial is the one Derek named (R21); a bare slap is to the face (R22); garments have named end states.
10. Nothing outside the prompt was output (R1); the diff gate shows only this cell's axis (R30); no trigger word
for a LoRA that is not loaded (R31).
11. **REF2VA pastes only:** run the additional gate in section 5 of `h3-max-ref2va-prompt` (labels vs wired inputs,
task-type tags, role-scoped retention lines, frame anchors, style opening, language, no `<scenetrans>`, speech form).
12. Load-bearing limb, surface pressure, follow-through, camera height vs body angle (R23a/R23b).
13. Every beat writes cause and effect: the motion, then how fabric, flesh and light react to it (cling or swing, bounce or compression, light on damp skin or through sheer cloth), then the settle (R14, R17, R20, R23a, R23b). Name the light in the camera line: source, direction, soft/hard, colour temperature, how it falls on skin and fabric (R23).

## 6. Worked examples

Moved verbatim to [references/worked-examples.md](references/worked-examples.md).

## 7. Pointers (who defers to this file)

- **REF2VA (the standing Max lane): skill `h3-max-ref2va-prompt`** - `C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md`
  (rules R32-R44, its own gate, paste skeleton) and `...\references\chain-lane.md` (multi-cell chains). Its section 2
  is the REF2VA reading of R5, R6, R8-R15; it never restates a rule of this file. The two files this pointer replaces
  are archived at `C:\AI\community\archive\2026-11-03-ref2va-split\`; thin pointers remain at
  [references/ref2va-lane.md](references/ref2va-lane.md) and [references/ref2va-chain-lane.md](references/ref2va-chain-lane.md)
  so old citations resolve.
- `alienpc-hardcore-i2v-director` lives at `C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md` (not copied here). It owns still-to-intent matching, director cards and package D triage. Prompt rules stay in this
  file (R16–R23b, R29a); do not restate them there.
- `h3-hc-render` owns graph/request wiring and the render dials; this file never sets steps, shift, VSA, fps.
- `alienpc-stills-pose-edit-prompting` owns FLUX.2 still prompts.
- **Long-clip beat sheet & multi-shot continuity**: [references/longclip-beat-sheet.md](references/longclip-beat-sheet.md) (beat sheet fields, in-clip [Shot N] preference, one primary beat per clip; C2V runtime marked UNPROVEN).
- The writer model's system prompt `C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md` (the only copy
  on this box - `C:\AI\community\notes\` has none) keeps its
  own rubric and few-shots: it is a model prompt, not a rule file, so it is not merged and not edited here. Its
  labeled soundscape-header instruction is superseded by R7 for anything written fresh on this box.

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
| R1-R4, R7-R9, R16-R23b, R24-R31 (incl. R29a) | this file, sections 0-4 (R16–R23b in `references/motion-contact-anatomy.md`, R24–R29a and R30-R31 in `references/wording.md`) |
| R5, R6, R10-R15 | this file, sections 1-2; the REF2VA reading of them is section 2 of `h3-max-ref2va-prompt\SKILL.md` |
| R32-R44 | `C:\AI\community\skills\h3-max-ref2va-prompt\SKILL.md` - REF2VA on H3-Max only: R32 hosted audio fields,
R33 label set and wired inputs, R34 task-type tags, R35 role-scoped retention, R36 frame anchors and the alignment line,
R37 speech form, R38 language and visible text, R39 style opening, R40 continuity tokens, R41 length provenance,
R42 the graph contract, R43 the chain lane, R44 the REF2VA gate |
| Render dials, graph wiring, queue | `h3-hc-render` (never prompt rules) |

A new rule is added in the file that owns its lane and gets the next box-unique number; never renumber an old rule.


## Sibling: parody / INDEX identity
Named INDEX+RefMod parody runs: load `h3-parody-identity` (name + description + RefMod). Do not fold those rules into this file.

## Sibling: writer-run & custom/INDEX RefMods
All adult RefMods (OC such as `FCSydny` -> `poolclub` visual + audio, INDEX/celebrity, PixlStash-tagged across `approved_characters\vault.db` and Stills `C:\Users\derek\5slock\libraries\vault.db`) and all voice refs (`*_refmod_audio` + `<Audio 1>`) are allowed. Bind likeness to the resolved RefMod(s) plus the start still; wardrobe and pose follow Picture 1 unless the beat writes a change. Explicit craft follows R16–R23b and R29a. Use the Gemma 4 26B A4B Heretic PolyStrata arm A writer pipeline (`render_writer_pipeline.py` flags: `--ask --position --still --still-read --character --frames --shots --shot-count --scene --continue --partner2-still`) or `submit_parody_run.py writer-run` (`--ask --position --still --character --frames --shots --continued --partner2-still --s3-look --s3-in-frame --partner-type --partner-type2 --names`), dry by default (`--queue` only on Derrick's yes). 3-body MMF/FFM asks are supported; >3-body asks fail closed. Only content rule kept is 18+ (youth lint). For a non-human or faceless partner, load only her RefMod; still nouns win on costume, place, roles, wardrobe, races, and scale.

