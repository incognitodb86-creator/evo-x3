# TOP5 - one 5-second, single-pass, euler prompt (E5)

Derrick 2026-10-25 6:48 PM CT (MAX block, `fix_plan.md` L18): "Go back to Euler, 5-second clips and
350-500 word prompts." His 10:40 AM line sets the scope: "I just want the 5 second clips to be good and I
will choose the scenes."

**One block: GI046 c0, one 124-frame pass at 24 fps = 5.167 s.** The scene is the one with a current card
(`C:/AI/community/notes/scenes/GI046.facts.json`, rebuilt 21:58 CT from the uncensored `vl_judge` captions
by CARD-VL). No new scene is chosen here.

**Format** is the IM1 shape `C:/AI/community/notes/im1_prompts.md` and its gate
`C:/AI/community/notes/ali31_prompt_set_check.py`: the six `c0` sections in order, beats inside the clip
the graph measures (`hc15_anchor_carry_build.top_windows` on the emitted graph = 0.0-5.167 s), camera terms
with amplitude and speed, the 350-500-word band on the `detailed_description` main field, and the card gate
`hc15_anchor_carry_build.card_measure/card_fires`.

**Card contract used** (`gate` of the facts file): 2 figures; 11 `per_chunk_tokens`; 7 `room_required` +
3 `light_required`; `open_beat` poses for both figures; `open_beat_ban`; per-figure `banned` + the
`any` list; `head_in_frame` 1=true / 2=false with `head_allow` phrasing; every person-word sentence
carries `aged NN` (age_min 21) and every age sentence carries the card's `age_marker` words
"canon declaration"; `consent_gate.require` "both of them consent" with its `ban` list absent.
Every appearance word below is a verbatim card row (`gate.evidence`): "human female", "slim, toned",
"light, glossy", "blonde, long and wavy", "center-left foreground", "lying prone on stomach",
"propped on forearms", "hips lifted", "silver chain-link bikini top and bottom", "choker necklace",
"tiara", "sparkling tiara", "green-skinned humanoid", "extremely muscular", "large hands and feet",
"green, textured with visible muscle definition", "black athletic shorts", "kneeling behind figure 1",
"hands placed on figure 1's lower back and thigh", "upper-right background",
"partially cropped at top and right edges", "interior living space", "dark wood flooring",
"beige shag rug", "beige upholstered sofa", "soft, diffused lighting from front-left",
"highlights on skin and metallic jewelry", "no direct sunlight".

**Known unsatisfiable gate row (measured, not assumed):** `gate.open_beat` requires the opening beat to
say "lying prone on stomach" for figure 1, and `gate.open_beat_ban` forbids the substring "lying" in the
same opening beat for figure 2. The opening beat is one string, so no wording satisfies both.
`notes/top5_build.py --check` measures that as `card_unsat` with a constructed minimal prompt, and the
emitted prompt's card-firing set is required to be exactly that one row. Reported to the card owner.

**Graph target:** `p7/graphs/ali163_top5_gi046_s51160001.api.json` =
`ali163_hc15_gi046_s51150032.api.json` minus the continuation nodes, `ksel.sampler_name` euler,
`c0.length` 124, this prompt, seed 51160001, its own save prefix. Steps (8), shift (10/3), canvas
(1344x768), the guide at frame 0, the attention/VSA chain and the two reference slots are NOT touched.

### id=ali163_top5_gi046_s51160001 chunk=c0 seed=51160001

subject_definitions:
<Subject 1> is the human female in the center-left foreground of the 16:9 start photograph in <Picture 1>, a fictional adult aged 27 (canon declaration): a slim, toned frame that the second caption of the same start still reads as curvaceous, light, glossy skin with visible pores, blonde, long and wavy hair falling past her shoulders, a sparkling tiara, a choker necklace, and the silver chain-link bikini top and bottom she wears in <Picture 1>, the silver chain-link bikini and choker of that start photograph. Her face, hair, body, skin and figure all come from <Picture 1>, and her face and hair are the face and hair in the face crop in <Picture 2>.
<Subject 2> is the green-skinned humanoid in the upper-right background of the same start photograph, a fictional adult aged 34 of a fictional non-human species (canon declaration): extremely muscular with large hands and feet, skin green, textured with visible muscle definition, black athletic shorts, kneeling behind figure 1 and leaning forward with both hands placed on figure 1's lower back and thigh, partially cropped at top and right edges, his head out of frame, the frame crops him at the neck.
<Picture 1> is the approved 16:9 start photograph: an interior living space with dark wood flooring, a beige shag rug covering most of the floor, a beige upholstered sofa out of focus in the background, <Subject 1> lying prone on stomach on the rug with her upper body propped on forearms and hips lifted, and <Subject 2> kneeling behind figure 1. It is the first frame of this video and it defines both bodies, their skin, the room, the rug, the sofa, the floor, the light, the colour cast, the crop and the camera position.
<Picture 2> is the face crop of <Subject 1>, the same human female, a fictional adult aged 27 (canon declaration), forehead, hair, jaw and shoulders filling the square. It is an identity reference for her face and hair only.

summary:
[reference generation] One continuous 16:9 shot of 5.167 seconds in the interior living space of <Picture 1>. <Subject 1>, the human female lying prone on stomach on the beige shag rug, a fictional adult aged 27 (canon declaration), keeps her forearms under her chest and her hips lifted. <Subject 2> kneels behind figure 1 in black athletic shorts, a fictional adult aged 34 of a fictional non-human species (canon declaration), keeping both hands on her lower back and thigh as the lens closes in and stops on him. Both of them consent. <Picture 1> is the first frame and the scene; <Picture 2> is her face and hair only.

retention_analysis:
<Subject 1> (appears in [Shot 1]) the human female, a fictional adult aged 27 (canon declaration): fully_preserved - her blonde, long and wavy hair, the sparkling tiara, the choker necklace, the silver chain-link bikini top and bottom, her slim, toned frame, her light, glossy skin, the prone position on the rug and the framing of <Picture 1>.
<Subject 2> (appears in [Shot 1]) the green-skinned humanoid, a fictional adult aged 34 (canon declaration): fully_preserved - his extremely muscular frame, large hands and feet, skin green, textured with visible muscle definition, black athletic shorts, the kneeling position behind figure 1, and the crop of <Picture 1> that keeps him out of frame at the top and right edges.
<Picture 1> ([Shot 1] first frame): fully_preserved - the interior living space, dark wood flooring, beige shag rug, beige upholstered sofa in the background, soft, diffused lighting from front-left, highlights on skin and metallic jewelry, no direct sunlight, the 16:9 framing, the camera height, and both figures in their opening positions.

detailed_description:
Live-action, cinematic realism, 16:9, one continuous medium shot in the interior living space of <Picture 1>, its light, colour cast, crop and camera height unchanged, shallow depth of field held on the two bodies.
[Shot 1] <Picture 1> is the first frame, and the framing, room, light and camera height stay as the photograph sets them. <Subject 1> lies prone on stomach in the center-left foreground, upper body propped on forearms, hips lifted, legs slightly bent, blonde, long and wavy hair spread over the pile, the sparkling tiara and choker necklace on her, the silver chain-link bikini top and bottom on her body. <Subject 2> is kneeling behind figure 1 in the upper-right background, partially cropped at top and right edges, extremely muscular with large hands and feet, in the black athletic shorts he wears, skin green, textured with visible muscle definition, his head out of frame, the frame crops him at the neck. Skin reads photographically on both figures: her light, glossy skin with visible pores, and his green surface as one continuous skin from shoulders to waist, so that where the black athletic shorts ride up at the hip the same green skin continues. The camera opens on a Static Shot of the pair, then a Push In with small amplitude at slow speed closes the lens distance by a hand's width across the first third of the segment, and from 00:03.500 the camera stops and holds the same frame for the rest of the segment.
At 00:00.000, the frame is the opening photograph: <Subject 1> lying prone on stomach on the beige shag rug, propped on forearms, hips lifted, legs slightly bent, palms flat on the pile, face toward the lens; <Subject 2> kneeling behind figure 1, leaning forward with both hands placed on figure 1's lower back and thigh, the beige upholstered sofa, the dark wood flooring and the soft, diffused lighting from front-left steady behind them, his head out of frame, the frame crops him at the neck.
At 00:01.400, both his large hands slide up to her waist and settle, her shoulder blades lift under the silver chain-link bikini top and bottom, her elbows straighten, and a strand of blonde, long and wavy hair moves across her shoulder.
At 00:02.900, her hips lift higher off the rug, her heels bend so her toes come up out of the pile, his forearms tighten as his hands hold her waist, and the tiara and choker necklace catch the soft, diffused lighting from front-left as bright highlights on her skin and on the jewelry.
At 00:04.200, the camera holds, her breathing rises and falls with her shoulders, his thumbs press once at her waist, and her face stays turned toward the lens.
The segment ends as it was framed: <Subject 1> propped on forearms with her hips lifted, <Subject 2> kneeling behind figure 1 with both hands on her lower back and thigh, the crop of <Picture 1> unchanged, his head out of frame.
overall_soundscape:
The room tone of the interior living space in <Picture 1>: a soft ventilation hum, a faint outside wash behind the glass, the pile of the beige shag rug shifting under palms and knees, the small chime of the chain-link bikini and the choker necklace settling, cloth friction at the waist, two quickened breaths, a low chest-deep voice, short rising sounds.

non_diegetic_music:
A low muted guitar figure over a slow finger-snare loop, low volume, tempo around 68 bpm, dynamics rising gently while the lens closes in and settling as the camera stops and holds.
