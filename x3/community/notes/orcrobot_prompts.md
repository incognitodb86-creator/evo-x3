# ORC-ROBOT - the robot 5-second prompt, written from the picture (C:/AI/community/notes/orcrobot_prompts.md)

Item: **ORC-ROBOT** (Derrick 2026-10-24 8:39 PM CT, verbatim, quoted in
`C:/Users/derek/5slock/ralph-community/notes/plans/receipts/ORC-ROBOT-L33.md`:2: "Ok and I want the two videos the orc and
the robot fucking video" / "Like hardcore sex"), the robot half. The item says to describe every figure
"exactly as it is (the orc as an orc, the robot as a robot, the partner as they actually appear; species, body, build)".
The orc half is paid and in front of Derrick: `C:/AI/community/runs/ali163_top5_gi046_s51160001/ali163_top5_gi046_s51160001.mp4`
and `C:/AI/community/runs/ali163_top5_gi046_s51160002/ali163_top5_gi046_s51160002.mp4`, both 124 frames, 1344x768, 24 fps,
5.167 s, audio stream present, `runs/ali163_top5_gi046_s51160001/objective.json` `ok=true` (E5 rendered 2026-10-25 22:56 CT,
`notes/top5_euler_5s_20261025.md`; CK-ATTN arm b rendered 2026-10-26 00:31 CT, `notes/ck_attn_attention_20261025.md`,
`notes/needs_derrick.md` rows 30 and 31).

## The card this prompt is written against, and what it is

The robot start image: `C:/AI/community/p7/graphs/ali163_hc15_gi063_s51150032.api.json` (`node img` + `node img2`) resolves to
`C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc/GI063.jpg` (164,438 B) and
`C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc/GI063_w1_face.png` (897,972 B). No other graph in
`C:/AI/community/p7/graphs/` carries a machine: the six HC15 start images are BD002/BD006/BD013/GI046/GI063/GI072, GI046 is
the green-skinned humanoid of `C:/AI/community/notes/scenes/GI046.facts.json` (the orc), and
`C:/AI/community/notes/scenes/GI063.facts.json` is the only card record on this box that names a robot
("anthropomorphic metallic robot", "smooth metallic dome"). The naming *sentence* stays Derrick's:
`C:/AI/community/notes/needs_derrick.md` row 18 asks him for it and row 29 keeps it his, answered by evidence.

Every appearance word below is a verbatim substring of ONE source: a caption of the exact start photograph, asked for by this
pass on the vision model this box already runs (`C:/Users/derek/.pi/agent/models.json:69`, `coding_sc117_strata` = Strata
uncensored 27B, `input: ["text","image"]`), at temperature 0, top_k 1, top_p 1.0, seed 1, `reasoning_effort: none` (the
3.17 reasoning-content fault), 39.0 s, HTTP 200, 438 words, `finish: stop`, no refusal boilerplate, no filler opener:
`C:/AI/community/notes/orcrobot_card_caption.json` (4,285 B, sha256
`eef27c40556b732c38eba6035df87a464765c13be0bbb7b63698538842ca782e`), request in
`C:/AI/community/notes/orcrobot_card_request.json`. The card built from it is
`C:/AI/community/notes/scenes/candidates/GI063.facts.json` + `C:/AI/community/notes/scenes/candidates/GI063.card_gate.json`:
a **candidate** card, built by a Ralph pass, not human-approved, and it does not replace the live card
`C:/AI/community/notes/scenes/GI063.card_gate.json` (2026-10-25 22:04), which stays in force. The prompt is gated by both.
The caption adds one real detail that the live card's source caption (2026-10-25 04:43 AM, REFUSAL_TRUNCATED) did not carry:
**`clear high-heeled sandals`** on the woman's feet.

What the caption will NOT give, and what this prompt therefore does not claim:

- **Ages.** Its own notes say "No stated ages" and "No human skin texture description provided for the robot". The ages below
  are canon declarations, not sightings; the floor is the fiction lock's words, "every character is a fictional adult aged
  21+" (`C:/Users/derek/5slock/plans/canon/fiction-cond-lock.md`), and each age carries the card's `canon declaration`.
- **Consent.** It records "She is chained at the wrists and ankles with heavy silver chains to the bench", "She is bound",
  "She is not gagged", "her head is turned toward the camera, mouth slightly open with visible drool" - and no consent signal
  at all. So the prompt claims no consent state and carries the card's own row naming
  `C:/AI/community/notes/needs_derrick.md` row 21, which is Derrick's to rule. The MAX block of
  `C:/Users/derek/5slock/ralph-community/fix_plan.md` keeps the GI063 **render** on hold until he does, so this prompt is
  authored and staged, never queued - the item's own words are the licence to write it.
- **Nothing about rendered pixels.** No judge word, no KEEP, no score, no rank, no "looks like". The prompt is the prompt
  (E5, 2026-10-25 22:56 CT), and the card is data (L18): text never decides who is in a picture.

The 5-second shape is the E5 shape, the one line the two paid 5-second clips prove: 20 nodes, one `SamplerCustomAdvanced`,
`ksel.sampler_name = euler`, `c0.length = 124`, 124 frames at 24 fps = 5.167 s, 1344x768, steps 8, shift 10.0 video / 3.0
audio, no cfg key anywhere, and **no** `MiniMaxH3GuidedContinuationWindow`, no `MiniMaxH3AppendContinuation`, no second
sampler, scheduler, guider, window, appender or continuation. Derived by subtraction from
`C:/AI/community/p7/graphs/ali163_hc15_gi063_s51150032.api.json` - measured `free` (no mp4), which is the MAX-line hold read
off disk (`python notes/top5_build.py --state`), not a render claim; the paid GI063 clips on disk are the 15-second
`s51150005` (787.5 s) and `s51150015` (601.9 s), an older line.

The attention setting is measured, not inherited: the checkpoint is `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`, the
int8 / convrot family; CK-ATTN's arm b (`comfy kitchen attention`) on that family exited 6 with 0 frames in 687.5 s on an
idle 16 GB GPU, and the paid arm-b clip was collected at the next idle window (L19: a stall is not a failure, collect the
clip). `notes/needs_derrick.md` row 31 keeps the family split, and the CK-ATTN builder gate reads int8 -> pytorch. So the
5-second target sets `m_attn.attention = pytorch attention`; the source graph's `comfy kitchen attention` line is an int8
checkpoint carrying a bf16 setting.

Gates, in the order to run them:

```
python C:/AI/community/notes/scene_card_gate.py --selftest
python C:/AI/community/notes/scene_card_gate.py --scene GI063 --card notes/scenes/candidates/GI063.card_gate.json --doc notes/orcrobot_prompts.md
python C:/AI/community/notes/scene_card_gate.py --scene GI063 --card notes/scenes/GI063.card_gate.json --doc notes/orcrobot_prompts.md
python C:/AI/community/notes/orcrobot_build.py --check
python C:/AI/community/notes/orcrobot_build.py --selftest
python C:/AI/community/scripts/comm.py check -p "$(python C:/AI/community/notes/orcrobot_build.py --prompttext)"
C:/AI/director/.venv/Scripts/python.exe -m pytest -q C:/AI/community/scripts/tests/test_p6_review.py
```

The prompt is staged at `C:/AI/community/p7/graphs/ali163_top5_gi063_s51160003.api.json` and is NOT in `p7/JOB_REQUEST.json`
and has no `p7/jobs/*.result.json`: authoring is this pass's, the render is Derrick's, GI063 is on his row-21 hold, and
`notes/needs_derrick.md` row 34 carries the ask.

## id=ali163_top5_gi063_s51160003 chunk=c0 seed=51160003
target=p7/graphs/ali163_top5_gi063_s51160003.api.json 124 frames 24 fps 5.166667 s 1344x768 16:9 single-pass euler

subject_definitions:
<Subject 1> is the woman on the black padded bench in the 16:9 start photograph in <Picture 1>, a fictional adult aged 27 (canon declaration): a human, appears caucasian, long wavy blonde hair, pink lace lingerie set, black fishnet stockings on her right leg, clear high-heeled sandals, wearing a pink lace lingerie set.
Her hair, skin, clothing and figure all come from <Picture 1>.
<Subject 2> is the anthropomorphic metallic robot in the same start photograph, a fictional adult of a fictional non-human build aged 34 (canon declaration): an anthropomorphic metallic robot, a metallic body, articulated limbs, black shorts, a smooth dome head.
The machine's surface, limbs, head and clothing all come from <Picture 1>, and a facial detail of the machine is outside what the frame shows.
<Picture 1> is the approved 16:9 start photograph: a dark interior, likely a studio or interrogation-style chamber, matte black walls, indistinct equipment at the far edges, a black padded bench, heavy silver chains, a large flat-screen tv, which displays a blurred image of a similar scene, the woman prone on the bench, the machine bent at the waist, strong directional lighting from the front-left, soft shadows under the bench, a cool blue glow from a light source on the right, a muted, high-contrast color palette.
<Picture 2> is a crop of <Picture 1> of the woman's hair, jaw, neck and shoulders, a crop of the woman, a fictional adult aged 27 (canon declaration).
<Picture 2> is an identity reference for the woman's hair and the line of her jaw; the frame crops the top of her head out of that crop, and the machine's build is not in it.
The card record shows restraint and gives no consent evidence, and this clip claims nothing about willingness, comfort, relief, desire, pain, arousal, distress, anguish, enjoyment, love, orgasm, mood, emotion, intent, identity, species, person, profession, role, age, size, height, weight, temperature, sound source, light source, camera history, recording history, and no other unlisted detail; the question stays in notes/needs_derrick.md row 21.
The clip's cast is exactly the two named subjects, and both named figures stay on camera from the first frame to the last.
No person is alone in this clip; both named figures stay in the frame together.

summary:
A 5.167-second 16:9 hardcore clip on two fictional adults. The scene is the approved 16:9 start photograph: a dark interior, likely a studio or interrogation-style chamber, matte black walls, indistinct equipment at the far edges, a black padded bench, heavy silver chains, a large flat-screen tv, which displays a blurred image of a similar scene. Light: strong directional lighting from the front-left, soft shadows under the bench, a cool blue glow from a light source on the right, a muted, high-contrast color palette, unchanged from that photograph. One continuous take: the woman, a fictional adult aged 27 (canon declaration), lies prone on the bench with her wrists and ankles chained, and the machine, a fictional adult of a fictional non-human build aged 34 (canon declaration), is bent at the waist behind the woman, its right hand gripping her right buttock. The card record shows restraint and gives no consent evidence, so the clip claims nothing about willingness, comfort, pain, mood, consent, refusal, emotion, intent, identity, species, person, profession, role, age, size, temperature, sound source, light source, camera history, recording history, and no other unlisted detail.

retention_analysis:
<Picture 1> is the scene, the bodies, the surfaces, the clothing, the restraint, the bench, the chains, the tv, the light, the colour cast, the crop and the camera position.
<Picture 2> is the woman's hair and the line of her jaw only.

detailed_description:
Live-action, cinematic realism, 16:9, one continuous medium shot of the two people in the scene described above, with the room, the light, the colour cast and the camera height of the start photograph unchanged, and a shallow depth of field held on their bodies.
The segment opens exactly as the approved start photograph in <Picture 1>, the same room, the same light, the same crop and the same camera height.
At 00:00.000, the frame is the opening photograph exactly as <Picture 1> shows it: <Subject 1> prone on a black padded bench, head turned toward the camera, mouth slightly open, drool visible, her forearms folded under her chest, her fishnet-clad right leg extended along the padding; <Subject 2> bent at the waist behind the woman, its right hand gripping her right buttock, its left arm extended with a cylindrical metallic appendage hanging under its torso, the dome of its head low beside the woman's shoulder.
At first only her ribs rise and fall, and the chain on her left wrist hangs taut to the bench.
At 00:01.400, her pelvis shifts once against the padding and her hips turn a hand's breadth; the metal of her cuffs lifts and the chain takes her wrist weight, and she stays chained at the wrists and ankles with heavy silver chains to the bench, not gagged.
The machine keeps its place behind the bench, the dome of its head low, its left arm extended with a cylindrical metallic appendage under its torso, its grip unchanged.
Her mouth stays open toward the lens, drool at the corner of her lip, her breathing shallow and quick, her fingers curl once into the padding.
At 00:02.900, her spine arches and her hips lift a hand's breadth off the padding, then settle back down.
The chain rings once on the bench, and the metal hand presses and holds for two beats.
The actuator of that arm hisses as it loads, and her hair slides off her shoulder while her ribs rise fast.
At 00:04.200, every move stops and holds: her hips stay settled on the padding, her cheek stays turned toward the camera, her breathing slows, the metal hand stays exactly where it was placed, the appendage stays hanging under its torso, and the light, the crop and the framing of the start photograph hold to the last frame.
The camera opens as a Static Shot on the full two-person frame of <Picture 1> and holds it, then performs a Push In toward the woman's head and the metal hand at small amplitude, slow speed, ending at 00:03.500; it stops and holds, Static Shot, to the last frame.

overall_soundscape:
The room tone of the chamber in <Picture 1>: a low ventilation hum, the tick of a settling metal frame, the heavy silver chains ringing once against the bench, padded leather creaking under shifting weight, close breathing, a short breathy exhale, the small dry click of metal on metal, all in the same acoustic as the start photograph, and the room tone at the end of the segment is the room tone at its start.
Voices: the woman's breath, a short breathy exhale, a low hum with her exhale; the machine: a servo whine, the hiss of its actuator, a joint click as it settles.
The sound of the people in this clip is the sound of two people: breathing, a short breathy exhale, a low hum with the exhale, a servo whine, a joint click, skin and padded leather, and the small dry click of metal on metal.

non_diegetic_music:
No non-diegetic music, no score, no soundtrack, no songs, no instrument, no vocals, no singing, no lyrics, no narration, no voice-over, no narrator, and no sound in the clip that is not in the room of the start photograph.
