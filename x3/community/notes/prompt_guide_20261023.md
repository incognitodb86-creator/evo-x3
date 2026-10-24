# PQ1 PROMPT QUALITY - MiniMax H3 / 10Eros / TenStrip prompt guide + IM1 prompt plan
Written by Derek_Zooey_Ralph on 2026-10-23 (Asia/Shanghai 19:20, UTC 11:20). Task = PQ1 in
ralph-community/TASKS.md. No render, no GPU: this is the research + template + per-clip plan
that IM1 (prompt-quality redo, same seeds) renders from.

## 0. Sources actually read (local copies under C:/AI/community/notes/web/)
| # | Source | Local file | What it gives |
| - | ------ | ---------- | ------------- |
| S1 | MiniMax official `docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` (Full-Reference Mode Rewrite Output Format Guide) fetched from `huggingface.co/MiniMaxAI/MiniMax-H3/resolve/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` | `pq1_minimax_ref_guide.txt` (23,553 B) + `_text.txt` | the 6-section ref2va format, label rules, summary task-type prefixes, retention markers, audio relationship markers, dialogue rules, soundscape rules, full example |
| S2 | MiniMax official `docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md` (T2VA / I2VA / FL2VA / L2VA) same repo | `pq1_minimax_base_guide.txt` (15,773 B) + `_text.txt` | keyframe instruction lines, shot/cut grammar, the camera-motion vocabulary, speaker grammar, overall_soundscape and non_diegetic_music rules, 4 worked examples |
| S3 | TenStrip model card `TenStrip/10Eros-TenStrip-H3-R2VA-Turbo-beta6-TURBO` (model created by TenStrip; beta6 turbo) fetched from `huggingface.co/api/models/...?expand=all` | `pq1_tenstrip_card.txt` | which prompt format per beta, turbo/non-turbo step+sampler+shift+LoRA table, NegPip negative-prompt rule, Extender continuation chain + slot order, "describe every little detail very precisely", crop-to-aspect rule |
| S4 | TenStrip HF discussion index (329 discussions) | `pq1_tenstrip_disc_full.json`, `pq1_tenstrip_disc_titles.txt` | which threads are prompt-related (list in notes/self_diagnosis.md) |
| S5 | TenStrip HF discussions, per-thread HTML, text extracted by `notes/ali163_pq1_extract.py` into `..._text.txt` | `pq1_tenstrip_d13/d21/d35/d45/d47/d49/d50/d52/d53/d57/d61/d63/d68/d69_text.txt` | owner answers on prompt format, audio wording, likeness, babble, greasy skin, continuation fps, steps |
| S6 | Civitai model cards via `civitai.com/api/v1/models/<id>` | `pq1_civitai_model_2863386 / 2866184 / 2940826 / 2967166 / 3010554 / 3016975.json` + `_text.txt` | camera-move test results (Stable Yogi), the "direct the sequence" prompting doctrine (catlover1937), LLM prompt-writer / portable generator / reverse-prompt tools (duckyshell, Liornyx, airi_mizuki17, vamorand) |
| S7 | Reddit | none | **blocked**: `old.reddit.com/r/StableDiffusion/search.json?q=MiniMax+H3+prompt` -> HTTP 403 (`pq1_reddit_sd_search.403.txt`), `www.reddit.com/r/comfyui/search.json?q=H3+prompt` -> HTTP 403 (`pq1_reddit_comfy_search.403.txt`). `notes/web/reddit_anatomy.html` is a CSS-only shell (0 `<h1>`, body never rendered). `notes/reddit_digest_20261023.md` does not exist. Reddit was NOT a source for this guide. |

Extraction + checking helpers:
- `C:/AI/community/notes/ali163_pq1_extract.py` - strips every saved source to `..._text.txt`
  (`sources=22` on the last run) and checks `im1_prompts.md` (12 blocks, seeds, section headers,
  beats, length, banned wording) with a self-destruct probe.
- `C:/AI/community/notes/ali163_pq1_audit.py` - prints the per-file prompt audit used in section 3
  (bytes, lines, section words, beat count, camera/amplitude wording, `<Subject>/<Picture>/<Video>`
  line counts, summary prefix, negation count). Run order: `python -m py_compile` then `python` it.

> Integrity note for this file: every number in section 3 is the output of `ali163_pq1_audit.py` on
> the current disk state. An earlier hand-written audit in this same iteration quoted line numbers
> and word counts (`hc_r3_c0.txt:27`, `:74`, "470-520 words", "`At 00:07.000` beats exist in R4 c0")
> that this script disproved - the real `hc_r3_c0.txt` is 5,151 bytes / 23 lines, the crop sentence
> is at line 2, and 0 of the 14 shipped prompts contains a single `MM:SS` timestamp. Prompt artifacts
> in this repo are read from disk by script, never from memory.

## 1. Research findings, one line each, with citations

1. **Ref2VA is the format for beta5/beta6 and it is a hard format, not a style.** TenStrip: "beta 5
   and up use R2VA prompting, earlier use FL2VA prompting" (S3 card lines 62-63; "Use L2VA for first
   frame. R2VA for everything else", S3 line 30). Owner in #45 on why prompts get ignored: "It is not
   ignoring it. It is heavily trained on ref2va prompts and if you do not give it the correct prompt
   structure it does not follow the format well... Make sure you are using the H3 prompt writing docs
   and sections" (`pq1_tenstrip_d45_text.txt`). Owner in #49: "Fl2va for beta4 and earlier, ref2va for
   beta5" (`pq1_tenstrip_d49_text.txt`).
2. **The six sections are the contract, in this order:** `subject_definitions`, `summary`,
   `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`
   (S1 section 1, lines 11-24). `summary` starts with a bracketed task-type prefix such as
   `[reference generation]` / `[video continuation + keyframe completion]`, types joined with `" + "`,
   and "Do not introduce new reference labels in this section" (S1 section 3, lines 121-155).
3. **A face-crop image must NOT get its own `<Picture N>` line.** S1 section 2.2: "If an image is used
   only to define a character, scene, costume, or style, do not create a standalone picture entry.
   Instead, cite the image source inside the corresponding `<Subject N>` definition." Our r1-r6 prompts
   all give `<Picture 2>`/`<Picture 3>` their own lines -> format violation.
4. **Detail is the whole game, and plot summary is the failure mode.** S1 header: "Make
   `detailed_description` as detailed and explicit as possible. For each shot, clearly establish the
   current composition, subject appearance and position, environment and lighting, actions and state
   changes, camera movement, current sound, and the points where referenced content actually appears...
   Avoid reducing the description to a plot summary or a list of reference relationships." TenStrip
   independently: "The key to success is the correct prompting: describe every little detail very
   precisely, the model can do 4-6 seconds in 4 steps" (S3 line 64).
5. **Word budget: 350-500 words for `detailed_description`, and a single shot is not an excuse to go
   short** (S1 section 5.2, lines 225-244: "For generation tasks, `detailed_description` is normally
   350-500 English words... A single shot does not automatically justify a shorter description").
   Measured in section 3: five of the seven shipped c0 prompts sit below that floor.
6. **Style opening goes before `[Shot 1]` in full-reference mode, one or two sentences** (S1 5.2), and
   `[Shot 1]` carries "the overall style and initial composition" in the shared grammar (S2 4.1, e.g.
   `[Shot 1] Live-action, cinematic, a medium-wide shot frames...`).
7. **Timing is written as shot cuts, not as a shot list.** S2 4.2: first shot has no timestamp; later
   shots start `At 00:03.500,` with cut verbs (`the shot cuts to / transitions to / switches to`); "A
   cut should introduce new information... If only the distance or a slight angle needs to change,
   prefer camera motion." S1 5.1: `[Shot N] At MM:SS.mmm, ...`.
8. **Camera language has a fixed vocabulary and it is written as a sentence, not a tag stack.** S2 4.3
   table: `Zoom In/Out`, `Push In / Pull Out`, `Pan Left/Right`, `Truck Left/Right`, `Tilt Up/Down`,
   `Pedestal Up/Down`, `Arc Shot`, `Tracking Shot`, `Static Shot`, `Shake Slightly/Strongly`, `POV`,
   `Roll Clockwise/Counterclockwise`, plus `with small/large amplitude` and `at slow/fast speed`;
   "Camera motion should be written as a natural English action within the shot, rather than stacked as
   separate labels at the end of a sentence." Example: "The camera pushes in with small amplitude at
   slow speed toward the folded letter in her hands."
9. **Real-world camera-move tests agree with the vocabulary** (S6, civitai 2940826, creator
   `Stable_Yogi`, "MiniMax H3 Camera Shots - 11 Tested Prompt Moves"): Pan Right, Pull Out, Push In and
   Truck Right are shown working on one reference subject, and the two orbit seeds produced partial
   arcs, i.e. full `Arc Shot` is the known limit. Card also: "Write the subject, scene, action,
   lighting, and camera direction in one prompt" and "Run a short test before spending time on a longer
   clip."
10. **Prompting doctrine from the community prompt-writing skills: direct the sequence, do not caption
    a picture** (S6, civitai 3010554, creator `catlover1937`, "Moody Minimax H3 Prompt Writing Skill -
    LLM SYSTEM PROMPT"): "a video prompt is not just an image prompt with some movement added. You're
    not describing a picture anymore. You're directing an entire sequence of events... Where does the
    character start? How does the movement begin? What happens next? Where is the camera? What should
    stay consistent?" Card also names the five structural jobs: subject definitions, reference
    relationships, continuity analysis, detailed shot descriptions, audio direction (same five we must
    fill), and credits `@noway163` as the prompting reference inside the Moody Discord.
11. **Reference slots carry roles and the order matters.** S1 5.3 gives the natural anchors: "the shot
    begins from `<Picture 1>`", "the shot's keyframe corresponds to `<Picture 2>`", "the shot ends on
    `<Picture 3>`". TenStrip's Extender doc (S3 lines 141-154) orders slots by role: "reference image 1
    is the last frame in the chain. reference image 2 is the start frame"; "If you want to keep body and
    face, use reference images with max set on the reference resize node and set the start image on the
    image node to be the start frame". #63 (owner, `pq1_tenstrip_d63_text.txt`) for a start-image-locked
    i2v-style lead-in: "`<Image N> is the correct scene identity. All lighting, lighting hue, color
    palette, visual output style, camera angle, camera focal length, camera orbit, camera framing,
    background, background objects, and characters fully preserved from <Image N>` ... add a natural
    language i2v style prompt after it, or add a timestamp of when to reference the picture too".
12. **Face crops alone are a known cause of likeness loss.** #63 (user, 2026-10-23): beta6 "fails to
    adhere to face ref images as well as previous models did", "when using 3 images with face
    reference, in my experience you'll get 3 different faces", and the report that "FL2VA seems to
    retain likenesses from start images well"; user `Ahsokabre` in #63: "I'm always using 3 images of
    the person, headshot full body and a detail shot". #45 confirms "Beta 6 fixed prompt adherence.
    Beta5 is more prone to this issue because of the ref2va prompt training."
13. **Our shipped r3-r6 wiring is the documented bad shape, and it is the body-quality defect.**
    `hc_r3_c0.txt:2` verbatim (same sentence in `hc_r4_c0.txt:2`, `hc_r5_c0.txt:2`, `hc_r6_c0.txt:2`):
    "These two crops are the only visual references in this clip and they are used for the faces and
    the hair of the two women only: the environment, the wardrobe, the bodies and the camera of this
    video are new and are not taken from `<Picture 1>` or `<Picture 2>`." In those four prompts every
    slot is a face crop (line 1: "Each picture is a tight close-up crop of one woman's face and hair...
    and the face fills its picture"), so **no full-body start photo reaches the model at all** - the
    bodies are invented from words, which is exactly what the R3-R6 body/limb defect report says:
    "r3r-r6 body+limb issues" (TASKS.md R5/R6 result lines, R5 c0 = "1 extra hand and extra leg") and
    "r3r-r6 4/6 reject: physics contact, likeness, hand anatomy, limb count, motion tempo, clothing
    integrity, camera drift" (TASKS.md R6 line 63), against r1-r2 where the start still was in the
    slot. The approved fix is in the r3b pair, built after that batch: `hc_r3b_c0.txt:2` puts
    `<Picture 1>` back as "the approved full-body start photograph ... defines the bodies, skin,
    figures, faces, hair, wardrobe, lighting and camera context for both women", with the crops
    keeping face/hair identity only, and it carries no "only visual reference" sentence
    (`ali163_pq1_audit.py`: stale=1 in r3/r4/r5/r6 c0, stale=0 in r1/r2/r3b c0).
14. **Audio is prompt-driven and needs a background layer.** #35 (owner TenStrip,
    `pq1_tenstrip_d35_text.txt`): "Sex sound is 'soft flesh thudding and skin of the bodies clapping
    together' and other stuff is usually 'soft wet sliding sounds'", "audio shift from 3-9, for best
    results 3", "best low step audio from LCM/simple 6-9 steps", "non turbo beta5 20-25 steps"; user
    advice in the same thread: "describe background sound more (in standard soundscape), background air
    conditioner or something I think helps". S1 section 6 + S2 4.6 back this: `overall_soundscape` is
    1-4 sentences of ambience + physical action sound + non-verbal human sound, `N/A` only for explicit
    total silence; `non_diegetic_music` is 1-3 sentences of instrumentation/tempo/dynamics, no abstract
    mood words, `N/A` when there is no score.
15. **Babble and voice defects have a prompt side.** #52 "H3 Babbling Solution" (S5): reduce turbo
    prompt adherence (beta6 turbo LoRA strength 0.4; S3 line 71 agrees), "Describe the background sound
    more (in standard soundscape)... ref audio should be under 90 frames", and for negation use the
    negpip token-weight node with one line per unwanted item (S3 lines 88-94 give the string form).
16. **Negative prompts are not used by the model - do not spend prompt surface on "do not show X".**
    S3 lines 77-78: "No negative prompt is required; it uses the NegPip embedded guidance. If you need
    more negation use Comfy negpip token weight node." (S1/S2 never use prohibition wording.)
17. **Visual defects are often the start image, not the words.** #57 (user): shiny/oily face was fixed
    by removing "reflections on the face" in the start image; #53 (user): "Starting image helps" for
    grease, and the owner explains the step/contrast coupling: "The more steps, the more contrast,
    saturation, microdetail and hardness of highlights". #47: "9 steps max ever needed". This is
    settings/starting-image scope, not prompt scope - recorded so the prompt is not blamed (and so we
    do not stuff quality words into it).
18. **Continuation fps / slow motion has a wording fix.** #68: owner "add 'dynamic video, fluid natural
    motions' with different seeds"; user: "the workflow is fine and it should output 24 fps"; owner:
    "I suggest a reword of the prompt. This is a difficult scene to prompt for." Our c1 chunks are
    continuations, so the continuation grammar (S1 summary prefix `[video continuation + ...]`,
    `<Video N>` = "continuing from the end of an original video", S1 2.3) must be used there.
19. **Prompt-writer tooling exists and is LLM-based** (S6): civitai 2863386 `duckyshell`
    ComfyUI-MiniMaxH3-Prompt-Writer (LLM prompt writer, local GGUF/Ollama/llama.cpp providers), 3016975
    `Liornyx` "MiniMax H3 Prompt Generator (Portable)" (Qwen-VL GGUF, "Strict H3 template output"),
    2866184 `airi_mizuki17` Reverse Prompt & Expansion (NSFW), 2967166 `vamorand` HB1 vision-LLM
    REF2VA prompter. All emit the official section format, which is the evidence that PW1 (prompt-writer
    install) is the right follow-up and that the format in section 2 below is machine-checkable.
20. **Prompt adherence is model-version dependent, so a prompt fix must be judged per model.** #61:
    "reference adherence has improved with beta6"; "10/3 shift required". S3: beta6 turbo = 4 steps
    simple / 8-12 steps lcm, CFG 1, `UniLPMS` sampler, shift 10 video + 3 audio.

## 2. Prompt template for IM1 (what every improved prompt must contain)

Target = ref2va full-reference format (S1), 16:9, 24 fps. c0 = 124 frames (5.166667 s, one shot,
starts on the approved start photo). c1 = continuation chunk (141 generated frames, first 22 hidden,
119 new visible, 5.875 s chunk / 4.958 s new). Keep the six section names in this order; c1 swaps
`detailed_description` for `integrated_multimodal_description` as the continuation/chunk field we
already ship.

```text
subject_definitions:
<Subject 1> is the man in <Picture 1> and <Picture 2>, [face: bone structure, hair, skin incl.
  facial hair and any marks; body: height/build/measurements, skin texture, visible marks,
  hand detail, genitals as visible anatomy; clothing as visible fabric/state; what Picture 1
  supplies (body, pose, wardrobe, room, light, camera) and what Picture 2 supplies (face, hair)].
<Subject 2> is the woman in <Picture 1> and <Picture 3>, [same pattern; state natural anatomical
  detail plainly, adult anatomy].
<Picture 1> is the first frame of [Shot 1] and the scene anchor for the target video: [framing,
  contact layout, wardrobe state, room, light, colour cast, depth of field, grain].
<Picture 2> / <Picture 3> are cited inside <Subject 1> / <Subject 2> and get NO standalone line
  (S1 2.2).

summary:
[reference generation] one sentence naming who does what in one shot, plus the preserved-anchor list
  (room, light, camera, wardrobe state) - a summary of the clip, no per-asset assignments
  (#63 in S5; S1 section 3).

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - <named visible details>.
<Subject 2> (appears in [Shot 1]): fully_preserved - <named visible details>.
<Picture 1> (maps to [Shot 1]): fully_preserved - framing, contact layout, room, light, lens
  character.
No <Audio N> line for c0 (no audio asset is attached); for c1 use <Video 1> (appears in [Shot 1]):
  reference - ... (S1 4.1 markers fully_preserved / partially_preserved / transferred / reused;
  audio markers fully_copy / partially_copy / reference / weak_reference, S1 4.2).

detailed_description:
Style sentence(s) before [Shot 1] (S1 5.2).
[Shot 1] Live-action, cinematic, <framing + composition + light>, <Picture 1> as the first frame ...
  <action onset -> continuous development -> result, per body part, per contact point, per
  secondary motion (hair, fabric, chest/belly, thighs)>
At 00:01.200, ... At 00:02.600, ... At 00:04.100, ... (beats inside the shot, plain sentences;
  no cut verb unless the shot really changes - S2 4.2)
Camera: <Static Shot / Push In / Pan Right / Truck Left / Tilt Up / Pedestal Down / Tracking Shot /
  Shake Slightly> <with small amplitude> <at slow speed>, written as one sentence (S2 4.3).
Voice: <Subject 1> (S1) ... <d>[English] exact line</d> only when the scene speaks; non-verbal
  sound goes to overall_soundscape (S1 5.4, S2 4.4/4.6).
End state sentence naming where the shot stops (position, contact, breath), 350-500 words total.

overall_soundscape:
1-4 sentences: room tone / ventilation hum + the diegetic contact sounds ("soft flesh thudding",
"skin of the bodies clapping together", "soft wet sliding sounds", fabric rustle, breath,
skin-slap) + non-verbal human vocalisation, in English, no timestamp (S1 6, S2 4.6, #35 in S5).

non_diegetic_music:
N/A (S2 4.7) when the scene has no score.
```

Rules that follow from the citations, as hard rules for IM1:
- describe only what is visible/audible; no quality tags, no "8k/masterpiece", no mood adjectives
  in `non_diegetic_music` (S2 4.7).
- positive phrasing; the shipped model takes negation through the negpip node, not prose (S3 77-78).
- every `<Subject N>` / `<Picture N>` / `<Video N>` used later must be defined first and keeps one
  meaning everywhere (S1 section 2 preamble).
- no standalone `<Picture N>` line for identity-only crops (S1 2.2).
- beats carry times; the shot ends in a named state (S2 3.1, S1 5.3).
- camera in canon words + amplitude + speed (S2 4.3).

## 3. What the 14 shipped prompts actually contain
Output of `python notes/ali163_pq1_audit.py` on 2026-10-23 (descw = words in
`detailed_description` / `integrated_multimodal_description`, soundw = words in
`overall_soundscape`, beats = `At MM:SS` timestamps, ampl = the words "amplitude"/"speed", stale =
the "only visual reference" sentence, pics/subj/video = lines starting with `<Picture N>` /
`<Subject N>` / containing `<Video 1>`, negs = negation phrases counted in the two prose sections):

```text
hc_r1_c0.txt  descw=275 soundw=70  beats=0 ampl=1 stale=0 pics=3 subj=4 video=0 negs=2
hc_r1_c1.txt  descw=345 soundw=90  beats=0 ampl=1 stale=0 pics=0 subj=2 video=0 negs=2
hc_r2_c0.txt  descw=315 soundw=90  beats=0 ampl=1 stale=0 pics=3 subj=4 video=0 negs=2
hc_r2_c1.txt  descw=396 soundw=102 beats=0 ampl=1 stale=0 pics=0 subj=2 video=0 negs=2
hc_r3_c0.txt  descw=337 soundw=76  beats=0 ampl=1 stale=1 pics=1 subj=4 video=0 negs=2
hc_r3_c1.txt  descw=429 soundw=91  beats=0 ampl=1 stale=0 pics=0 subj=2 video=0 negs=2
hc_r3b_c0.txt descw=435 soundw=76  beats=0 ampl=1 stale=0 pics=1 subj=4 video=0 negs=2
hc_r3b_c1.txt descw=498 soundw=91  beats=0 ampl=1 stale=0 pics=0 subj=2 video=0 negs=2
hc_r4_c0.txt  descw=335 soundw=96  beats=0 ampl=1 stale=1 pics=1 subj=2 video=0 negs=2
hc_r4_c1.txt  descw=404 soundw=87  beats=0 ampl=1 stale=0 pics=0 subj=1 video=0 negs=2
hc_r5_c0.txt  descw=375 soundw=77  beats=0 ampl=1 stale=1 pics=1 subj=2 video=0 negs=2
hc_r5_c1.txt  descw=387 soundw=83  beats=0 ampl=1 stale=0 pics=0 subj=1 video=0 negs=2
hc_r6_c0.txt  descw=378 soundw=82  beats=0 ampl=1 stale=1 pics=1 subj=4 video=0 negs=2
hc_r6_c1.txt  descw=463 soundw=92  beats=0 ampl=1 stale=0 pics=0 subj=2 video=0 negs=2
```

| Gap | Verified evidence | Fix in IM1 |
| --- | --------------- | ---------- |
| no beat timing anywhere | `beats=0` in 14/14; timing is prose ("In the first two seconds ... during the middle four seconds" in `hc_r3_c0.txt:16`) and the clip ends with a state sentence ("ends with the two women still kissing", `hc_r1_c0.txt:18`) | `At 00:01.200,` / `At 00:02.600,` beats inside `[Shot 1]`, ending in a named state (S2 4.2, S1 5.3) |
| continuation chunks have no continuation label | `video=0` in 14/14; the six c1 files start `subject_definitions:` then go straight to `integrated_multimodal_description:` (`hc_r3b_c1.txt:1-7`) | add the summary/retention shape + `<Video 1> ... reference -` line for the continuation chunk (S1 2.3, 3, 4.2; #68) |
| no `summary:` / `retention_analysis:` section in any c1 | the six c1 files: sections present = subject_definitions, integrated_multimodal_description, overall_soundscape, non_diegetic_music (`hc_r3b_c1.txt`, 15 lines) | add `summary:` with `[video continuation + reference generation]` prefix + `retention_analysis:` lines (S1 1, 3, 4) |
| face-crop / reference-sheet images get standalone `<Picture N>` lines and the start photo is demoted | r1/r2 c0: `pics=3` (`hc_r1_c0.txt:4-6` = "`<Picture 1>` is the start still...", "`<Picture 2>` is the multi-view reference sheet of `<Subject 1>` alone", same for 3); r3-r6 c0: every slot is a crop + the "only visual references" sentence (`hc_r3_c0.txt:1-2`) | crops/sheets cited inside `<Subject N>` only; one `<Picture 1>` line = first frame + scene anchor (S1 2.1/2.2) |
| `summary` is a per-asset assignment paragraph | `hc_r1_c0.txt:9` ("The shot uses `<Picture 1>` for the scene and `<Picture 2>` and `<Picture 3>` only as appearance guidance for the two women while freely composing the ...") and the same shape in r2-r6 c0 (`hc_r3_c0.txt:7`, `hc_r3b_c0.txt:7`) | one clip-summary sentence + the preserved-anchor list, no assignments (#63 in S5, S1 3) |
| description below the 350-word floor in 5 of 7 c0 prompts | `descw`: r1 275, r2 315, r3 337, r4 335, r5 375, r6 378, r3b 435 | 350-500 words in every c0 `detailed_description` (S1 5.2) |
| soundscape is one long sentence, and negation tails eat prompt surface | `soundw` 70-102 in all 14; negation samples from the audit: "no dialogue, no announcer, no counting, no crowd", "no cuts" | 1-4 sentences of ambience + contact sound + breath, ambience layer named (fan/vent/air), negation moved to the negpip node (S2 4.6, S1 6, #35/#52 in S5, S3 77-78) |
| camera wording is not canon vocabulary | `hc_r1_c0.txt:18` "The camera starts in a medium two-shot and moves in slowly and steadily, low amplitude"; the audit's `ampl=1` in 14/14 with no canon type words | canon `Push In / Pull Out / Pan / Truck / Tilt / Pedestal / Arc / Tracking / Static / Shake` + `with small\|large amplitude` + `at slow\|fast speed` in one sentence (S2 4.3, civitai 2940826) |
| no speaker IDs while moaning is written as prose only | no `(S1)` / `<d>` in any file; moaning sits in the description text ("her mouth opens in a long moan", `hc_r3b_c1.txt:8`) | keep non-verbal sound in `overall_soundscape`; add `(Sx)` + `<d>[English] ...</d>` only for clips that speak (S1 5.4, S2 4.4) |

Not a gap: `non_diegetic_music` is present in all 14 (S2 4.7 allows 1-3 sentences; N/A is allowed when
there is no score), the 16:9 start photos match the crop rule (S3), and every prompt already states
fictional-adult ages (content lock).

## 4. IM1 plan (one variable: the prompt; seeds stay)
IM1 = the six R clips re-rendered with the section-2 template, same seeds 51130001-51130006, same
graph (steps 4 / euler / shift 10 video / 3 audio / cfg absent), same start photos and face crops,
same 1024x576 canvas. Body-quality fix rides in the same variable because the wiring sentence that
broke the body reference is prompt text (finding 13); no graph change, no LoRA change, no step change
- those are the next single variables (IM2 = start photo / crop policy, IM3 = steps/LoRA strength).
The 12 verbatim prompts (6 clips x c0/c1) are in `C:/AI/community/notes/im1_prompts.md`;
`ali163_pq1_extract.py` checks them (12 blocks, seeds, all six section headers, the right c0/c1
field names, `At MM:SS` beats, >=5000/4000 chars, and the stale "only visual reference" wording
must be absent - its self-destruct probe is `PQ1_DESTRUCT=notes/hc_r3_c0.txt`, which must fail).

## 5. Kept / killed after this research
- Kept: the 6 approved picks; the 16:9 crops (S3 "crop images to the output aspect (16:9 for 16:9)");
  the anatomy detail paragraphs (detail is what the model is trained to read, S1 header, S3 line 64).
- Killed for IM1: face-crop-only reference prose (finding 13); prose denial lists (finding 16);
  quality-word inflation (finding 17).
- Not prompt fixes, so not in IM1: greasy skin / contrast / microdetail (steps + start image,
  finding 17), VSA/FastH3 speed, two-pass latent upscaling for skin detail (#21, #61 - settings,
  next single variables).
