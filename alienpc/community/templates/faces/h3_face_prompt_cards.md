# h3_face_prompt_cards.md - four copy-paste cards for face-LoRA clips (built 2026-11-03)

The fast path for "make me a clip of this face": pick a card, fill the blanks, run one command.
A face is named by its `FC_*` alias. The words that the LoRA
listens for (its trigger phrase) are **injected by the builder** from the private map, at a `{TRIGGER}` token
in place, or at the front of the paste when there is no token. Do not type the words yourself in a card.

Everything else follows the standing prompt lanes: `skills/h3-prompting/SKILL.md` (R1-R31, all lanes) and, for a
REF2VA job, `skills/h3-max-ref2va-prompt/SKILL.md` (R32-R44). These cards are skeletons for that shape, not a
shortcut around it: five sections in order (R5), task-type tag first (R6), plain audio cues at the end of
`detailed_description` and no soundscape block (R7), clock ranges and no transition words (R8), the verbatim
identity clauses (R11), the start frame described from its own text records (R14), adults 18+ with a stated age (R2).

## The command (one line, builds the request)

```
C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\sydney\tools\render_face_clip.py \
  --fc FC_<ALIAS> --prompt-file <card.txt> --image community/<start_frame>_768x1344.png \
  --seed <n> --run-name face_<topic>_<YYYYMMDD> --frames 124 [--go]
```

The builder refuses: an `FC_*` that is not FIT, a face with no trigger phrase in the private map, a frame count
off the `(frames-5) % 17 == 0` grid, and any build while `C:\AI\locks\gpu-render.lock` exists. `--go` hands the
job to `scripts/run_queue.py --detach`, which takes the lock and runs the pytest and adults-only gates itself.

## Card 1 - single action, one continuous shot (the default)

```
subject_definitions:
<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>.
<Subject 1> is <FC_ALIAS>, a fictional adult woman aged <21+ stated age>, in <place, one line>.

summary:
[reference generation] <Subject 1>, <face and body in the start frame in one clause>, in <place and light>,
<what happens in the clip in one sentence>. Her face, hair and body stay exactly as in <Picture 1>.

retention_analysis:
<Subject 1>: fully_preserved face, hairstyle, skin and figure from <Picture 1>.
<place>: partially_preserved <what stays>, <what may change>.

detailed_description:
<camera, lens, height, distance, light, in 2-3 sentences.>
[Shot 1] 00:00.000 - 00:05.100 <Subject 1> <start-frame state as it is in the image, in the present tense>.
<beat 2: one action verb, one body part, one direction, at a stated moment.>
<beat 3: the response, described flatly: face, chin, arms, hips, hands.>
At the end <the last visible state, so the clip ends in a clean pose>.
<one or two plain audio sentences tied to those actions.>
```

## Card 2 - two beats with a change of position (entry transition)

Use when the start frame is not already in the position the action needs. Fill R16's entry transition in
`summary` (how she gets into position in the first seconds), then two timed shots. Keep every contact stated
(belt, rail, fabric, hands) and never imply a position the start frame contradicts.

```
subject_definitions: (as card 1)
summary:
[reference generation] ... In the first two seconds she <entry transition: turns, steps, sits, lowers>.
retention_analysis: (as card 1)
detailed_description:
<camera block.>
[Shot 1] 00:00.000 - 00:02.500 <the entry transition, beat by beat.>
[Shot 2] 00:02.500 - 00:08.000 <the action, in the new position, with the contacts named.>
<ending state.> <plain audio cues.>
```

## Card 3 - face and eye-line close (identity test cell)

For checking a face at strength 1.0 with the least story around it. Keep it a tight portrait, one shot,
no wardrobe change, no occluders over the face, and a plain background, so a score measures the identity.

```
subject_definitions: (as card 1)
summary:
[reference generation] A close portrait of <Subject 1> in <plain place, soft light>. She looks at the camera,
then <one small movement>, and returns her eyes to the camera.
retention_analysis:
<Subject 1>: fully_preserved face, hairline, brows, eyes, lips, jaw, skin.
detailed_description:
<eye-level close shot, 50mm feel, head and shoulders fill the frame, soft key from the front-left.>
[Shot 1] 00:00.000 - 00:05.100 She holds a calm neutral expression, blinks once, <one small movement: turns her
head two degrees, tucks hair, breath>, then settles. Her face is unobstructed the whole clip; nothing crosses it.
<quiet room tone and breath, tied to the beats.>
```

## Card 4 - a face in a scene with others (crowd, one face)

The face LoRA loads for one identity; the other people must be described, not named. For a scene where extras
must not carry a face identity, add the person-remover only as its own tested cell - it is FIT and installed,
but no cell on this box has proven it in a crowd, so write it as a labelled try, never as a silent default.

```
subject_definitions:
<Picture 1> ... <Subject 1> (the FC_* face). <Subject 2>, <Subject 3> are <described adults, ages stated>,
no reference images.
summary: [reference generation] <Subject 1> in <place> with <Subject 2> and <Subject 3>; <what happens>.
retention_analysis:
<Subject 1>: fully_preserved face, hair, body. <Subject 2>, <Subject 3>: weak_reference, described appearance only.
detailed_description: <camera block; one shot; keep <Subject 1>'s face toward the camera at the key beats;
state who touches what.> <plain audio cues.>
```

## Before submitting (the short check)

- `guard_ok` runs on every submit through `run_queue.py`; a clip of a **real** person is Derek's ask and GO (R2).
- One GPU job at a time: `run_queue.py` takes `gpu-render.lock`; a build into a busy window is refused.
- Strength lives in the template (`templates/faces/<FC>.api.json`, `strength_model 1.0`), and the trigger comes
  from the private map. `--strength` is for a labelled A/B cell only, and the number goes in the run record.
