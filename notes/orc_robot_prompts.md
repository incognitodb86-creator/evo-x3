# ORC-ROBOT - the robot (GI063) 5-second prompt, written from the card (ORC-ROBOT, fix_plan L27)

Derrick's ask (`fix_plan.md` L27, receipt `notes/plans/receipts/ORC-ROBOT-L27.md`): write the H3 prompt for
the robot start image from what is in the picture - species, body, build, the partner as the picture shows
them - in community prompt structure and published defaults, render it 15 s 16:9 with audio, send the mp4 and
a contact sheet. The render half of that row is gated by `C:/AI/community/notes/needs_derrick.md` row 21 (the
same card's consent ruling), so this pass writes and gates the prose and the graph and queues the render to
him. The orc half of the row is already paid: the 5 s GI046 clips are `notes/top5_prompts.md` /
`notes/top5_build.py` (E5 and CK-ATTN, needs_derrick rows 30, 31), and row 28 says the anatomy words are his.

**One block: GI063 c0, one 124-frame pass at 24 fps = 5.167 s.** `id=ali163_top5_gi063_s51160011`,
seed 51160011, graph `p7/graphs/ali163_top5_gi063_s51160011.api.json` =
`p7/graphs/ali163_hc15_gi063_s51150031.api.json` minus the continuation nodes, `ksel.sampler_name` euler,
`c0.length` 124, this prompt, this seed, its own save prefix, and `m_attn.attention` = pytorch attention
(the published value: docs/02v_docs_h3.md:196 names it as the default, and the live schema default is
"pytorch attention" for a node whose options are pytorch/comfy-kitchen; the checkpoint on this box is the
int8_convrot family). Steps (8), shift (10/3), canvas (1344x768), the guide at frame 0, the VSA node, the
vae chain, `mkvid` and the two reference slots are NOT touched.

**Format** is the IM1 shape `C:/AI/community/notes/im1_prompts.md` and its gate
`C:/AI/community/notes/ali31_prompt_set_check.py`: the six `c0` sections in order, beats inside the window
the graph measures (0.0-5.167 s), camera terms with amplitude and speed, the 350-500-word band on the
`detailed_description` field, and the card gate `hc15_anchor_carry_build.card_measure/card_fires`.
L15: no negation wording in the prose (the shipped set carries 0).

**Card contract used** (the `gate` of `C:/AI/community/notes/scenes/GI063.facts.json`, the card CARD-VL
rebuilt from the uncensored captions): 2 figures; 12 `per_chunk_tokens`; 8 `room_required` + 4
`light_required`; `open_beat` poses for both figures; `open_beat_ban` for both; per-figure `banned` plus the
`any` list, which for this card bans the pronouns "he", "him", "his" and "a man"/"the man" (the robot is
it/its/the robot); `head_in_frame` true for both, so no head rule; every person-word sentence carries
`aged NN` and every age sentence carries the card's `age_marker` words "canon declaration" (age_min 21,
the canon lock v2.3.0); `consent_gate.require` = "the card record shows restraint and gives no consent
evidence" and "notes/needs_derrick.md row 21", with its `ban` list (every eagerness claim and every distress
word) absent. Every appearance word below is a verbatim card row (`gate.evidence`): "human female",
"fair, glistening with sweat", "long, wavy blonde", "pink lace lingerie set (bra and panties)", "black
fishnet stockings on right leg only", "clear high-heeled sandals with straps", "prone on a black padded
bench", "upper body propped on forearms", "head turned toward camera", "mouth slightly open, drool visible
from corner of lip", "chained at wrists", "ankles to bench leg", "heavy silver chains",
"anthropomorphic metallic robot", "tall, muscular, articulated limbs with visible joints and segments",
"polished silver metal plating", "head is a smooth metallic dome with sensor-like details",
"black tight-fitting shorts", "bent at waist", "right hand gripping her right buttock",
"cylindrical metallic appendage", "dark interior", "matte black", "studio or interrogation-style chamber",
"indistinct equipment or furniture silhouettes", "black padded bench/table with metal frame",
"large flat-screen tv", "displaying a blurred image of a similar scene", "cool blue glow",
"strong directional lighting from front-left", "highlighting the woman's skin, hair, and the metallic
surfaces of the robot", "soft shadows cast under the bench".

**Card rows that need a sentence shape (measured, not assumed):** the `light_required` row "highlighting the
woman's skin, hair, and the metallic surfaces of the robot" ends on the alias "robot", so in a sentence of
its own it is owned by figure 2 and charges the card-banned words "skin" and "face" (inside "surfaces") to
the robot; the row is carried inside a longer sentence that ends on a figure-1 alias, and that sentence
carries the age row. The `room_required` row "indistinct equipment or furniture silhouettes" contains the
card-banned-for-figure-2 substring "fur" (in "furniture"), so it sits in a sentence that carries no figure
alias at all and is owned by nobody. `notes/orc_robot_build.py --selftest` seeds each of those shapes.

---

### id=ali163_top5_gi063_s51160011 chunk=c0 seed=51160011

subject_definitions:
<Subject 1> is the human female on the left side of the frame in the 16:9 start photograph in <Picture 1>, a fictional adult aged 27 (canon declaration): fair, glistening with sweat, long, wavy blonde hair, the pink lace lingerie set (bra and panties) she wears, black fishnet stockings on right leg only, clear high-heeled sandals with straps, prone on a black padded bench with the upper body propped on forearms, head turned toward camera, mouth slightly open with drool visible from the corner of the lip, chained at wrists to the bench edge and chained at the ankles to the bench leg by heavy silver chains. Her face, hair, body and figure all come from <Picture 1>, and her face and hair are the face and hair in the face crop in <Picture 2>.
<Subject 2> is the anthropomorphic metallic robot in the same 16:9 start photograph, a fictional adult aged 31 of a fictional non-human machine species (canon declaration), tall, muscular, with articulated limbs with visible joints and segments, a smooth metallic dome head with sensor-like details, black tight-fitting shorts over the pelvic area and bare metal elsewhere. It stands bent at waist over the hips of <Subject 1>, right hand gripping her right buttock, left arm extended downward with a cylindrical metallic appendage near her lower back and hip. The dome head, limbs and shorts of the robot all come from <Picture 1>.
<Picture 1> is the approved 16:9 start photograph: a dark interior, a studio or interrogation-style chamber with matte black walls, indistinct equipment or furniture silhouettes along the far wall, a black padded bench/table with metal frame at the centre, a large flat-screen tv mounted on the back wall, displaying a blurred image of a similar scene, <Subject 1> prone on a black padded bench and chained at wrists, and <Subject 2> bent at waist over her hips. The photograph is the first frame of the video, and the first frame defines both bodies, the room, the bench, the chains, the screen, the light, the colour cast, the crop and the camera position.
<Picture 2> is the face crop of <Subject 1>, the same human female, a fictional adult aged 27 (canon declaration), forehead, hair, cheek and neck filling the square. It is an identity reference for her face and hair only.

summary:
[reference generation] One continuous 16:9 shot of 5.167 seconds in the dark interior of <Picture 1>. <Subject 1>, the human female prone on a black padded bench, a fictional adult aged 27 (canon declaration), keeps her forearms propped and her head turned toward camera. <Subject 2>, the anthropomorphic metallic robot, a fictional adult aged 31 of a fictional non-human machine species (canon declaration), stays bent at waist over her hips with one hand on her right buttock as the lens closes in and stops. The card record shows restraint and gives no consent evidence, and notes/needs_derrick.md row 21 carries that question to Derrick. <Picture 1> is the first frame and the scene; <Picture 2> is her face and hair only.

retention_analysis:
<Subject 1> (appears in [Shot 1]) the human female, a fictional adult aged 27 (canon declaration): fully_preserved - her long, wavy blonde hair, the pink lace lingerie set, black fishnet stockings on right leg only, clear high-heeled sandals with straps, fair, glistening with sweat, the prone position on the bench, the chains at her wrists and ankles, the head turned toward camera and the framing of <Picture 1>.
<Subject 2> (appears in [Shot 1]) the anthropomorphic metallic robot, a fictional adult aged 31 of a fictional non-human machine species (canon declaration): fully_preserved - the tall, muscular frame, articulated limbs with visible joints and segments, the smooth metallic dome head with sensor-like details, the black tight-fitting shorts, the bent at waist posture over her hips and the crop of the start photograph, all of it as the robot stands in <Picture 1>.
<Picture 1> ([Shot 1] first frame): fully_preserved - the dark interior, matte black walls, indistinct equipment or furniture silhouettes, black padded bench/table with metal frame, heavy silver chains, large flat-screen tv, displaying a blurred image of a similar scene, cool blue glow, strong directional lighting from front-left, soft shadows cast under the bench, the 16:9 framing, the camera height, and both figures in their opening positions.

detailed_description:
Live-action, cinematic realism, 16:9, one continuous medium shot in the dark interior of <Picture 1>, its light, colour cast, crop and camera height unchanged, shallow depth of field held on the two bodies.
[Shot 1] <Picture 1> is the first frame, and the framing, room, light and camera height stay as the photograph sets them. Strong directional lighting from front-left, a key at camera left, rakes the bench, highlighting the woman's skin, hair, and the metallic surfaces of the robot and casting soft shadows cast under the bench, and the woman in the pink lace lingerie set is a fictional adult aged 27 (canon declaration). <Subject 1> lies prone on a black padded bench, upper body propped on forearms, head turned toward camera, mouth slightly open with drool at the corner of the lip, long, wavy blonde hair spread on the pad, the pink lace lingerie set and clear high-heeled sandals with straps on her body, chained at wrists and chained at the ankles. The robot stands bent at waist over her hips, an anthropomorphic metallic robot with articulated limbs with visible joints and segments and a smooth metallic dome head with sensor-like details, in the black tight-fitting shorts it wears, and the polished silver metal plating of the forearm and hand rests on her hip. The camera opens on a Static Shot of the pair, then a Push In with small amplitude at slow speed closes the lens distance by a hand's width across the first third of the segment, and from 00:03.600 the camera stops and holds the same frame for the rest of the segment.
At 00:00.000, the frame is the opening photograph: <Subject 1> prone on a black padded bench, chained at wrists to the bench edge, forearms propped, head turned toward camera; <Subject 2> bent at waist over her hips with one hand on her right buttock and the other arm extended downward with a cylindrical metallic appendage near her lower back and hip; the large flat-screen tv, the heavy silver chains and the soft shadows cast under the bench steady behind them.
At 00:01.400, the hand on her right buttock presses and holds, her shoulder blades lift under the pink lace lingerie set, her elbows straighten, and a strand of long, wavy blonde hair moves across the pad.
At 00:02.900, her hips rise against the pad, her heels bend so her toes lift, the articulated joints at the waist of the robot tighten while the hand stays on her hip, and the cool blue glow shifts along her hair.
At 00:04.200, the camera holds, her breathing rises and falls with her back, the metal hand presses once at her hip, and her face stays turned toward the lens.
The segment ends as it was framed: <Subject 1> propped on forearms on the black padded bench with the chains at her wrists, the robot bent at waist over her hips with its hand on her hip, the crop of <Picture 1> unchanged.
overall_soundscape:
The room tone of the dark interior in <Picture 1>: a low ventilation hum, the faint electrical wash of a screen, chain links ticking once as a wrist turns, the padded bench creaking under a shoulder, cloth friction at the hip, two quickened breaths, a low resonant hum from the machine, short rising sounds.

non_diegetic_music:
A low muted guitar figure over a slow finger-snare loop, low volume, tempo around 68 bpm, dynamics rising gently while the lens closes in and settling as the camera stops and holds.
