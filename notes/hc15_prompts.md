# HC15 prompts - clip 1 = ali163_hc15_bd002_s51150001 (15.083 s, 362 f, 1344x768, 24 fps)

Written to `notes/prompt_guide_20261024.md` (official MiniMax six-section Ref2VA format,
`detailed_description` 350-500 words, `At MM:SS.mmm` beats, canon camera type + amplitude + speed,
no negation prose, `overall_soundscape` 1-4 sentences, `non_diegetic_music` 1-3 sentences).
Structure copied from the 12 validated blocks in `notes/im1_prompts.md` (the 3.1 gate set).

Subject grounding is measured, not imagined (this box has no vision on explicit material):
`notes/ali163_hc_r4g2_facebox.py` on `C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD002.jpg`
(1376x768, ratio 1.7922) found exactly 2 faces, left-to-right: face 1 box 252,93,214,105 with hair luma
254.5 (platinum blonde), face 2 box 738,44,129,175 with hair luma 162.6 (dark brown). So `<Subject 1>`
is the blonde woman on the left of frame, `<Subject 2>` the dark-haired woman right of centre. The folder
`CHARACTER.md` (approved by Derrick 2026-10-19 12:30 PM CT) states these are fictional adult women,
adults-only screened by insightface age >= 18. Room, furnishings, wardrobe, light, colour and camera
are delegated to `<Picture 1>` in every section: Forge has no measurement of them and invents none.

Face crops (the reference slots): `BD002_w1_face.png`, `BD002_w2_face.png` in
`ComfyUI/input/community/hc`, cut by `scripts/face_crop.py --size 512` from the two measured boxes.

Identity gate result (`notes/ali163_hc_r4g2_verify.py`, run 2026-10-24 14:27): `BD002_w2_face.png` PASSES
(ArcFace cosine 0.99 vs the source face box, 1 face, 15.0% of crop); `BD002_w1_face.png` **FAILS**
(cosine 0.503, face only 10.9% of crop). Every shipped crop in the same table measures 0.905-0.992, so the
blonde's face box on BD002 (252,93,214,105 - wider than tall, h/w 0.49) is a tilted/profile detection, not a
clean frontal face. The failing crop is therefore EXCLUDED from the graph: ref slots are
`ref_image_1` = `BD002.jpg` (start still) and `ref_image_2` = `BD002_w2_face.png`, and `<Subject 1>`'s face,
hair, body and skin ride on `<Picture 1>` alone. Measured face geometry of the other five picks (same probe):
BD006 left box h/w 0.58, BD013 left box h/w 0.68 - same tilt problem on the pair picks; the solo picks
GI046 (201x201, h/w 1.00, 2.24% of frame) and GI063 (166x202, h/w 1.22) are the frontal faces, so the next
HC15 clips go to those, where both/all crops can pass the gate.

---

### id=ali163_hc15_bd002_s51150001 chunk=c0 seed=51150001

subject_definitions:
<Subject 1> is the platinum-blonde woman on the left of the two-woman start photograph in <Picture 1>, a fictional adult aged 22: slim and toned, natural shoulder definition, a defined waist, gently rounded hips, long legs with visible knee and calf definition, light skin with visible pores and fine vellus hair, long loose platinum-blonde hair, and the wardrobe she wears in <Picture 1>. Her face, hair, body, skin and figure all come from <Picture 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman right of centre in the two-woman start photograph in <Picture 1>, a fictional adult aged 24: soft and full, a wide hip spread, thick thighs, a rounded seat, a full bust, warm skin with visible pores, long dark brown hair, and the wardrobe she wears in <Picture 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1>.
<Picture 1> is the approved 16:9 start photograph of <Subject 1> and <Subject 2> close together, the blonde woman at the left third of frame and the dark-haired woman right of centre, both faces in the upper half of frame. It is the first frame of this video and it defines their bodies, skin, figures, faces, hair, wardrobe, the room, the furnishings, the light, the colour cast and the camera position.

summary:
[reference generation] The target video is the first 5.17 seconds of a single continuous 16:9 shot of <Subject 1> and <Subject 2>, two fictional adult women dressed as in <Picture 1>, who turn to each other, kiss, and draw each other's tops up and off their shoulders, ending the segment bare-chested and chest to chest. The shot uses <Picture 1> as the first frame and the scene, and <Picture 2> as the face and hair of <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the blonde woman of <Picture 1>, keeping her face, hair, slim figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - the dark-haired woman of <Picture 2> and <Picture 1>, keeping her face, hair, full figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Picture 1> ([Shot 1] first frame): fully_preserved - the room, furnishings, wall, light direction, colour cast, the standing start position of the pair, the 16:9 framing and the camera height.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women.
[Shot 1] A single continuous 16:9 medium two-shot that keeps the framing, the room, the light and the colour of <Picture 1> exactly, with <Picture 1> as the first frame. <Subject 1> stands at the left third of frame and <Subject 2> stands right of centre, both in the wardrobe of <Picture 1>, in the same positions, at the same distance from the lens and at the same height as the opening photograph, weight settled on their back feet, hips angled toward each other. Photorealistic skin and anatomy: natural matte skin with visible pores and fine vellus hair, real adult body mass with joint definition, five separate fingers on each hand, natural adult proportions, a soft sheen of sweat only where skin presses skin. The camera starts as a Static Shot on the pair, then a Push In with small amplitude at slow speed closes the lens distance by a hand's width across the segment. At 00:00.000, the frame is the opening photograph: the two women facing each other, eyes lowered, mouths closed, hands loose at their sides, the light of <Picture 1> lying across their collarbones. At 00:01.300, <Subject 1> lifts her chin and closes the last centimetres between their mouths; her left hand rises to cup the side of <Subject 2>'s neck and her fingers spread into the dark hair at her temple, and <Subject 2>'s right palm slides onto the blonde's ribcage; both mouths open into the kiss and their breaths quicken visibly. At 00:02.900, <Subject 2>'s free hand hooks the hem of <Subject 1>'s top and draws it up over her ribs and chest in one continuous pull, the fabric stretching and sliding off her shoulders, while <Subject 1>'s hands lift the dark-haired woman's top off her shoulders in the same motion; both garments travel up and out of frame and their bare chests come into the light: <Subject 1> slim and lightly shaped with small light-brown areolae, <Subject 2> fuller and heavier, breasts hanging softly with their weight and darker areolae, skin catching the key light along the collarbones. At 00:04.300, the women settle chest to chest, <Subject 1>'s palms flat at her sides, <Subject 2>'s forearm across the blonde's waist, shoulders and chests in continuous contact, the kiss continuing, hair falling forward over their jaws, mouths parting for one visible breath and closing again. The shot ends with <Subject 1> and <Subject 2> still kissing, bare-chested, foreheads touching, <Subject 2>'s hand resting on the blonde's ribs, both chests rising fast.

overall_soundscape:
The room tone of the space in <Picture 1>, a soft ventilation hum and a faint outside wash through an open window. Fabric friction as the two tops stretch and slide off shoulders, a light knock of a palm against a wall, heel shifts on the floor. Quickened nasal breathing from both women, small open-mouthed sighs at the mouth of the kiss, a low humming moan pressed against the other's mouth.

non_diegetic_music:
A single muted electric piano figure in a slow three-beat loop with soft brush cymbals, low volume, tempo around 70 bpm, dynamics rising gently with the kiss and settling at the end of the segment.

---

### id=ali163_hc15_bd002_s51150001 chunk=c1 seed=51150001

subject_definitions:
<Subject 1> is the platinum-blonde woman of the start photograph in <Picture 1>, a fictional adult aged 22: slim and toned, defined waist, gently rounded hips, light skin with visible pores and fine vellus hair, long loose platinum-blonde hair, bare-chested as she became in <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 24: soft and full, wide hip spread, thick thighs, rounded seat, full bust, warm skin with visible pores, long dark brown hair, bare-chested as she became in <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it is the reference that defines their bodies, skin, figures, faces, hair, the room, the furnishings, the light, the colour cast and the camera context for both women.

summary:
[video continuation + reference generation] This segment continues the same single continuous shot from <Video 1>: over the next 4.96 seconds <Subject 1> and <Subject 2>, both bare-chested from the first segment, work each other's lower garment down and off, part, and look at each other's naked bodies, ending with <Subject 2> stepping back onto the bed and <Subject 1> kneeling between her thighs. The same room, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, slim figure, skin tone (all carried from <Picture 1> and <Video 1>) and the state her body reached in <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, full figure, skin tone and the state her body reached in <Video 1>.
<Video 1> (the first 5.17 seconds of this clip): fully_preserved - the room, the light direction, the colour cast, the framing, the camera height, and the fact that both women's tops lie discarded outside frame.
<Picture 1> (scene anchor): partially_preserved - the room, furnishings, wall, light and colour carry; the two women are now bare-chested where they were dressed in the photograph.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women.
[Shot 1] One continuous take that carries the lens position, room, light and colour of <Video 1> forward, the camera resuming as an Arc Shot with small amplitude at slow speed, curving a quarter of the way around the pair so the window light moves from the left of frame toward the camera, then settling into a Push In with small amplitude at slow speed. Both women stand in the positions where the first segment left them, bare-chested, their discarded tops on the floor outside frame, skin glossy where their chests pressed. At 00:05.200, <Subject 1> breaks the kiss for one long breath, drops her forehead to <Subject 2>'s shoulder, and her hands go to the waistband of <Subject 2>'s lower garment; she works the fabric down over the dark-haired woman's hips with both palms, and the garment slides down her thighs and off her shoes. At 00:06.900, <Subject 2> pulls the blonde's lower garment down in the same way, stepping out of it, and for the first time both women stand naked in the light of <Picture 1>: <Subject 1> slim, hips narrow, a neat triangle of pale pubic hair, small pale areolae, her breasts light and shaped as she moves; <Subject 2> full, wide hips, thick thighs, a dark triangle of pubic hair, heavy breasts that swing and settle with her weight, a round seat that catches the light. At 00:08.500, <Subject 2> turns and steps back onto the low bed behind her, sitting on the edge, elbows behind her, chest arched forward, thighs parting as she settles, and she looks down at <Subject 1> with her mouth open and breathing hard; <Subject 1> steps in toward her and lowers herself onto her knees between the dark-haired woman's thighs, one hand on each knee, thumbs pressing into the soft inner thigh flesh. At 00:09.900, <Subject 1> lifts her face toward <Subject 2>'s stomach, blonde hair falling forward against the darker skin of her inner thighs, her hands sliding up under the wet folds at the apex of <Subject 2>'s thighs, fingers spreading the labia apart; <Subject 2>'s hand comes down into the blonde's hair and grips it, her hips lifting an inch off the mattress, her mouth open on a soundless syllable. The camera is steady, focus held on the contact point, the window light grazing both bodies, skin detail crisp and natural at the close distance, and the shot ends on <Subject 1> kneeling between <Subject 2>'s thighs with her fingers on the wet, swollen folds and <Subject 2>'s hand tight in her hair.

overall_soundscape:
The same room tone as <Video 1>, the window wash a little louder with the camera closer. Fabric pooling on the floor, a dull thud of a body settling on a mattress, a bed frame creaking once, palms sliding on wet skin. Breathing that turns into a rising open-mouthed moan from <Subject 2>, short sharp breaths from <Subject 1>, the wet sound of fingers working.

non_diegetic_music:
The muted electric piano figure continues, a brushed snare entering, tempo around 70 bpm, dynamics swelling slightly as the kneeling position settles and easing back at the end of the segment.

---

### id=ali163_hc15_bd002_s51150001 chunk=c2 seed=51150001

subject_definitions:
<Subject 1> is the platinum-blonde woman of the start photograph in <Picture 1>, a fictional adult aged 22: slim and toned, light skin with visible pores, long loose platinum-blonde hair, naked, kneeling as she was at the end of <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 24: soft and full, wide hips, thick thighs, full heavy breasts, warm skin with visible pores, long dark brown hair, naked, seated on the bed as she was at the end of <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it defines their faces, bodies, skin, the room, the furnishings, the light, the colour cast and the camera context.

summary:
[video continuation + reference generation] This segment continues the same single continuous take from <Video 1> for the final 4.96 seconds: <Subject 1> goes down on <Subject 2> at the edge of the bed, <Subject 2> arches and comes with her hand in the blonde's hair, and <Subject 1> rises with wet fingers to kiss her, ending the fifteen seconds chest to chest. The room, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, slim figure, skin tone and her kneeling position at the end of <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, full figure, skin tone and her seated position at the end of <Video 1>.
<Video 1> (the first 10.13 seconds of this clip): fully_preserved - the room, the light, the colour cast, the framing, the camera height, the discarded clothing outside frame, and the wetness already on <Subject 2>.
<Picture 1> (scene anchor): partially_preserved - the room, wall, light and colour carry; both women are naked and the pair are now at the bed.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the contact of the two women.
[Shot 1] One continuous take resuming the exact framing and lens height of <Video 1>, the camera a Push In with small amplitude at slow speed for the first three beats, then a Pedestal Up with small amplitude at slow speed as <Subject 1> rises, and a Pull Out with small amplitude at slow speed for the last beat so the two women settle back into the medium framing of the opening photograph. At 00:10.200, <Subject 1> leans in and takes <Subject 2> onto her tongue, flat and broad, two long licks upward through the swollen wet folds, her fingers pressing the labia apart and her nose grazing the darker skin; <Subject 2>'s hips snap forward onto her face and her thighs clamp around the blonde's shoulders, toes curling. At 00:11.700, <Subject 1> works her tongue in fast, short circles on the swollen nub, one thumb rubbing in slow circles beside it, and she takes two fingers deep inside, knuckle grazing, a wet sound opening with it; <Subject 2>'s back bows off the mattress, her hand tight in the blonde's hair steering her, her mouth open, jaw shaking, a long rising moan breaking into words she swallows. At 00:13.100, <Subject 2>'s thighs tremble and press the blonde's head hard against her, her hips stutter in three short pulses, her breasts shivering, the areolae taut, and she comes with her eyes shut, head thrown back, hand twisting in the dark hair at her own nape; the blonde's cheek and chin are wet and gleaming in the window light. At 00:14.400, <Subject 1> rises up out of the kneeling position, wiping her mouth with the back of her wrist, and <Subject 2> pulls her in by the hair so their chests meet, skin sliding on skin; <Subject 1> lifts her wet fingers to <Subject 2>'s breast and draws them down the dark-haired woman's cleavage, leaving a shining streak, and they kiss hard, tongues meeting, both breathing through their open mouths. The final frame is the two women chest to chest in the same 16:9 medium framing and the same light as <Picture 1>, <Subject 2>'s arm locked around the blonde's waist, <Subject 1>'s hand on the back of her neck, both naked, both slick, the room steady behind them.

overall_soundscape:
The room tone of <Video 1> with the window wash steady underneath. Wet tongue and finger sounds, a mattress creak, the bed frame knocking the wall once, palms slapping thigh, hair being gripped. <Subject 2> moaning loudly and rising into a broken cry, then short gasps against the blonde's mouth; <Subject 1> humming against skin, both women breathing hard in the last second.

non_diegetic_music:
The electric piano figure resolves into a slower two-chord loop, brushed snare dropping out, tempo around 70 bpm, dynamics peaking at the climax and fading to a soft sustain as the two women come together.

---

## Clip 2 = ali163_hc15_bd006_s51150002 (15.083 s, 362 f, 1344x768, 24 fps, seed 51150002)

Same guide as clip 1. Measured grounding (`notes/ali163_hc_r4g2_facebox.py`, row `HC15B`, run 2026-10-25):
`C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD006.jpg` = 1376x768,
ratio 1.7922, exactly 2 faces left-to-right: box 215,146,156,91 (1.35% of frame, h/w 0.58 = tilted,
hair luma 245.5 = blonde) and box 537,90,109,141 (1.46% of frame, h/w 1.29 = frontal, hair luma 186.2 =
dark brown). `CHARACTER.md` (Derrick-approved 2026-10-19 12:30 PM CT): fictional adults, insightface
age >= 18 screening, blonde + dark-haired pair. Identity gate (`notes/ali163_hc_r4g2_verify.py`, run
2026-10-25): `BD006_w2_face.png` PASSES (cos 0.888, 15.3% of crop); `BD006_w1_face.png` **FAILS**
(cos 0.058) for the same reason as BD002_w1 - the blonde's box is wider than tall, a tilted/profile
detection - so that crop is EXCLUDED and the graph carries 2 slots: `ref_image_1` = `BD006.jpg`,
`ref_image_2` = `BD006_w2_face.png`; `<Subject 1>` (the blonde) rides on `<Picture 1>` alone.
Pair distinctness: cos(HC15B_w1 vs HC15B_w2) = 0.216, i.e. the two crops are different people.
Roles are reversed from clip 1 on purpose: here the dark-haired woman kneels, so the woman who carries a
verified face crop is the active subject. Room, light, colour, wardrobe stay delegated to `<Picture 1>`.

### id=ali163_hc15_bd006_s51150002 chunk=c0 seed=51150002

subject_definitions:
<Subject 1> is the blonde woman on the left of the two-woman start photograph in <Picture 1>, a fictional adult aged 23: tall and athletic, broad shoulders, a flat stomach, firm long legs with visible knee and calf definition, fair skin with visible pores and fine vellus hair, long straight blonde hair, and the wardrobe she wears in <Picture 1>. Her face, hair, body, skin and figure all come from <Picture 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman right of centre in the two-woman start photograph in <Picture 1>, a fictional adult aged 25: compact and soft, narrow waist, wide hips, full breasts, a round seat, olive skin with visible pores, long wavy dark brown hair, and the wardrobe she wears in <Picture 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1>.
<Picture 1> is the approved 16:9 start photograph of <Subject 1> and <Subject 2> standing side by side, the blonde woman at the left third of frame and the dark-haired woman right of centre, both faces in the upper half of frame. It is the first frame of this video and it defines their bodies, skin, figures, faces, hair, wardrobe, the room, the furnishings, the wall, the light, the colour cast and the camera position.

summary:
[reference generation] The target video is the first 5.17 seconds of a single continuous 16:9 shot of <Subject 1> and <Subject 2>, two fictional adult women dressed as in <Picture 1>, who kiss, pull each other's tops up and off, and stand bare-chested in the light of the opening photograph. The shot uses <Picture 1> as the first frame and the scene, and <Picture 2> as the face and hair of <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the blonde woman of <Picture 1>, keeping her face, hair, athletic figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - the dark-haired woman of <Picture 2> and <Picture 1>, keeping her face, hair, soft figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Picture 1> ([Shot 1] first frame): fully_preserved - the room, the wall, the light direction, the colour cast, the standing start position of the pair, the 16:9 framing and the camera height.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women.
[Shot 1] A single continuous 16:9 medium two-shot that keeps the framing, the room, the wall, the light and the colour of <Picture 1> exactly, with <Picture 1> as the first frame. <Subject 1> stands at the left third of frame and <Subject 2> stands right of centre, both in the wardrobe of <Picture 1>, at the same distance from the lens and the same height as the opening photograph, weight on their back feet, hips angled toward each other. Photorealistic skin and anatomy: natural matte skin with visible pores and fine vellus hair, real adult body mass with joint definition, five separate fingers on each hand, natural adult proportions, a soft sheen of sweat only where skin presses skin. The camera starts as a Static Shot on the pair, then a Push In with small amplitude at slow speed closes the lens distance by a hand's width across the segment. At 00:00.000, the frame is the opening photograph: the two women facing each other, chins lifted, mouths closed, hands loose at their sides, the light of <Picture 1> lying across their collarbones. At 00:01.200, <Subject 2> rises onto her front feet and presses her mouth to <Subject 1>'s mouth; her hands slide up the blonde's ribcage and her fingers open into the blonde hair at the nape, and <Subject 1>'s palms settle on the dark-haired woman's waist, thumbs pressing into the soft flesh above her hips; both mouths open into the kiss and their breathing quickens visibly. At 00:02.800, <Subject 1>'s hands hook the hem of <Subject 2>'s top and draw it up in one continuous pull, fabric stretching over her ribs and breasts and sliding off her shoulders, while <Subject 2> pulls the blonde's top up over her chest and head in the same motion; both garments leave frame and their bare chests come into the light: <Subject 1> taut and flat-chested with small pale areolae and the long line of her abdomen, <Subject 2> soft and full, heavy breasts swinging once with her weight and settling, darker areolae, skin catching the key light along the underside of her breasts. At 00:04.200, the women settle chest to chest, <Subject 1>'s forearms around the dark-haired woman's back, <Subject 2>'s hands cupping the blonde's breasts, thumbs rubbing, the kiss continuing, hair falling forward over their jaws, mouths parting for one visible breath and closing again. The shot ends with <Subject 1> and <Subject 2> still kissing, bare-chested, hips forward, <Subject 2>'s thigh between the blonde's legs, both chests rising fast.

overall_soundscape:
The room tone of the space in <Picture 1>, a soft ventilation hum and a faint outside wash through an open window. Fabric friction as two tops stretch and slide off shoulders, a light knock of a heel on the floor, a palm sliding on a ribcage. Quickened breathing from both women, small open-mouthed sighs at the mouth of the kiss, a low humming moan pressed against the other's mouth.

non_diegetic_music:
A low muted guitar figure over a slow finger-snare loop, low volume, tempo around 68 bpm, dynamics rising gently with the kiss and settling at the end of the segment.

### id=ali163_hc15_bd006_s51150002 chunk=c1 seed=51150002

subject_definitions:
<Subject 1> is the blonde woman of the start photograph in <Picture 1>, a fictional adult aged 23: tall and athletic, flat stomach, firm long legs, fair skin with visible pores, long straight blonde hair, bare-chested as she became in <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 25: compact and soft, narrow waist, wide hips, full heavy breasts, round seat, olive skin with visible pores, long wavy dark brown hair, bare-chested as she became in <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it defines their bodies, skin, figures, faces, hair, the room, the wall, the light, the colour cast and the camera context for both women.

summary:
[video continuation + reference generation] This segment continues the same single continuous shot from <Video 1>: over the next 4.96 seconds <Subject 1> and <Subject 2>, both bare-chested from the first segment, work each other's lower garment down and off, and <Subject 2> sinks down onto her knees in front of the standing blonde. The same room, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, athletic figure, skin tone (carried from <Picture 1> and <Video 1>) and the bare-chested state her body reached in <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, soft figure, skin tone and the bare-chested state her body reached in <Video 1>.
<Video 1> (the first 5.17 seconds of this clip): fully_preserved - the room, the wall, the light direction, the colour cast, the framing, the camera height, and the fact that both women's tops lie discarded outside frame.
<Picture 1> (scene anchor): partially_preserved - the room, wall, light and colour carry; the two women are now bare-chested where they were dressed in the photograph.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women.
[Shot 1] One continuous take that carries the lens position, room, wall, light and colour of <Video 1> forward, the camera resuming as an Arc Shot with small amplitude at slow speed, curving a quarter of the way around the pair so the window light travels from the left of frame toward the camera, then settling into a Push In with small amplitude at slow speed. Both women stand in the positions where the first segment left them, bare-chested, their discarded tops on the floor outside frame, skin glossy where their chests pressed. At 00:05.200, <Subject 2> breaks the kiss for one long breath and drops her mouth to the front of the blonde's collarbone; her hands go to the waistband of <Subject 1>'s lower garment and she works the fabric down over the blonde's hips and thighs with both palms, the garment pooling at her ankles. At 00:06.800, <Subject 1> pulls the dark-haired woman's lower garment down in the same way, stepping on the fabric as it falls, and for the first time both women stand naked in the light of <Picture 1>: <Subject 1> tall, legs long, hips narrow, a neat pale triangle of pubic hair, small pale areolae, abdominal muscles visible as she shifts her weight; <Subject 2> compact, hips wide, thick thighs, a dark triangle of pubic hair, heavy breasts that swing and settle with her weight, a round seat that catches the light. At 00:08.400, <Subject 2> steps back a half pace, looks at the blonde's whole body with her mouth open, breathing hard, then slides down onto her knees on the floor in front of her, one hand on the blonde's thigh for balance, the other at her own breast, thumbs rubbing her own areola as she settles. At 00:09.900, <Subject 1>'s hands come down into the dark hair at <Subject 2>'s temples and grip, her thighs parting, and <Subject 2> presses her face against the blonde's inner thighs, her tongue visible as it licks a long stroke upward through the wet pale folds; the blonde's head tips back, her jaw opening, her fingers tightening in the dark hair. The camera is steady, focus held on the contact point, the window light grazing both bodies, skin detail crisp and natural at the close distance, and the shot ends on <Subject 2> kneeling between the standing blonde's thighs with her fingers on the blonde's knees and the blonde's hips forward.

overall_soundscape:
The same room tone as <Video 1>, the window wash a little louder with the camera closer. Fabric pooling on the floor, a knee settling on the floorboards, palms sliding on wet skin, hair being gripped. Breathing that turns into a rising open-mouthed moan from <Subject 1>, short sharp breaths from <Subject 2>, the wet sound of a tongue working.

non_diegetic_music:
The muted guitar figure continues, a brushed snare entering, tempo around 68 bpm, dynamics swelling slightly as the kneeling position settles and easing back at the end of the segment.

### id=ali163_hc15_bd006_s51150002 chunk=c2 seed=51150002

subject_definitions:
<Subject 1> is the blonde woman of the start photograph in <Picture 1>, a fictional adult aged 23: tall and athletic, fair skin with visible pores, long straight blonde hair, naked, standing as she was at the end of <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 25: compact and soft, wide hips, thick thighs, full heavy breasts, olive skin with visible pores, long wavy dark brown hair, naked, kneeling as she was at the end of <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it defines their faces, bodies, skin, the room, the wall, the light, the colour cast and the camera context.

summary:
[video continuation + reference generation] This segment continues the same single continuous take from <Video 1> for the final 4.96 seconds: <Subject 2> goes down on the standing <Subject 1>, the blonde comes with her hand in the dark hair, and the pair rise together to kiss chest to chest in the framing of the opening photograph. The room, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, athletic figure, skin tone and her standing position at the end of <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, soft figure, skin tone and her kneeling position at the end of <Video 1>.
<Video 1> (the first 10.13 seconds of this clip): fully_preserved - the room, the wall, the light, the colour cast, the framing, the camera height, the discarded clothing on the floor outside frame, and the wetness already on <Subject 1>.
<Picture 1> (scene anchor): partially_preserved - the room, wall, light and colour carry; both women are naked and the pair are now on the floor in front of the wall.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the contact of the two women.
[Shot 1] One continuous take resuming the exact framing and lens height of <Video 1>, the camera a Push In with small amplitude at slow speed for the first three beats, then a Pedestal Up with small amplitude at slow speed as <Subject 2> is kissed upward, and a Pull Out with small amplitude at slow speed for the last beat so the two women settle back into the medium framing of the opening photograph. At 00:10.200, <Subject 2> takes the blonde onto her tongue, flat and broad, two long licks upward through the swollen wet pale folds, her fingers pressing the labia apart and her nose grazing the fair skin; <Subject 1>'s hips snap forward onto her face and her thighs clamp around the dark-haired woman's shoulders, toes curling on the floor. At 00:11.600, <Subject 2> works her tongue in fast short circles on the swollen nub, one thumb rubbing slow circles beside it, and she takes two fingers deep inside, knuckle grazing, a wet sound opening with it; <Subject 1>'s back bows, her hand tight in the dark hair steering, her mouth open, jaw shaking, a long rising moan breaking into words she swallows. At 00:13.000, <Subject 1>'s thighs tremble and press the dark head hard against her, her hips stutter in three short pulses, her abdominal muscles cramping, her small breasts shivering, the areolae taut, and she comes with her eyes shut, head thrown back, fingers twisting in the dark hair; the dark-haired woman's chin and cheek are wet and gleaming in the window light. At 00:14.300, <Subject 2> rises up off her knees and <Subject 1> pulls her in by the hair so their chests meet, skin sliding on skin; <Subject 2> lifts her wet fingers to the blonde's breast and draws them down the taut cleavage, leaving a shining streak, and they kiss hard, tongues meeting, both breathing through their open mouths. The final frame is the two women chest to chest in the same 16:9 medium framing and the same light as <Picture 1>, <Subject 1>'s arm locked around the dark-haired woman's waist, <Subject 2>'s hand on the back of her neck, both naked, both slick, the wall steady behind them.

overall_soundscape:
The room tone of <Video 1> with the window wash steady underneath. Wet tongue and finger sounds, a knee creaking on the floorboards, palms sliding on taut skin, hair being gripped. <Subject 1> moaning loudly and rising into a broken cry, then short gasps against the dark-haired woman's mouth; <Subject 2> humming against skin, both women breathing hard in the last second.

non_diegetic_music:
The guitar figure resolves into a slower two-chord loop, brushed snare dropping out, tempo around 68 bpm, dynamics peaking at the climax and fading to a soft sustain as the two women come together.

## Clip 3 = ali163_hc15_bd013_s51150003 (15.083 s, 362 f, 1344x768, 24 fps, seed 51150003)

Same guide as clips 1-2. Measured grounding (`notes/ali163_hc_r4g2_facebox.py`, row `HC15C`, run 2026-10-24 box
clock): `C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD013.jpg` = 1376x768,
ratio 1.7922, exactly 2 faces left-to-right: box 414,71,155,106 (1.55% of frame, h/w 0.68 = tilted, hair luma
252.3 = blonde) and box 709,58,113,154 (1.63% of frame, h/w 1.36 = frontal, hair luma 203.5 = dark brown).
`CHARACTER.md` (Derrick-approved 2026-10-19 12:30 PM CT): fictional adults, insightface age >= 18 screening,
blonde + dark-haired pair. Identity gate (`notes/ali163_hc_r4g2_verify.py` rows `HC15C_w1` / `HC15C_w2`, run
2026-10-24 box clock): `BD013_w2_face.png` PASSES at cos **0.989** (face 14.8% of crop); `BD013_w1_face.png`
PASSES the published gate at cos **0.49** (face 19.0% of crop, threshold 0.45) - the lowest accepted value in
the set, every other shipped crop measures 0.888-0.992, and the tilted box (h/w 0.68) is why it is weak.
Reported, not silently used: this clip keeps the **2-slot** shape of clips 1-2 (`ref_image_1` = `BD013.jpg`,
`ref_image_2` = `BD013_w2_face.png`) so the only variable that moves is the source still; adding the marginal
blonde crop as `ref_image_3` is a second variable and is staged as the next single-variable test if Max or
Derrick want it. `<Subject 1>` (the blonde) rides on `<Picture 1>` alone. Pair distinctness:
cos(HC15C_w1 vs HC15C_w2) = 0.132, i.e. the two crops are different people.
Choreography is a third shape, neither clip (blonde active) nor clip 2 (dark-haired active): here the pair
strip each other and finish **side by side on the floor, mutual**, so the six clips are not six copies. Room,
light, colour and wardrobe stay delegated to `<Picture 1>`, and the choreography touches the floor of <Picture 1> only.

### id=ali163_hc15_bd013_s51150003 chunk=c0 seed=51150003

subject_definitions:
<Subject 1> is the blonde woman at the left of centre of the two-woman start photograph in <Picture 1>, a fictional adult aged 24: tall and athletic, broad shoulders, a flat stomach, firm long legs with visible knee and calf definition, fair skin with visible pores and fine vellus hair, long straight blonde hair, and the wardrobe she wears in <Picture 1>. Her face, hair, body, skin and figure all come from <Picture 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman right of centre in the two-woman start photograph in <Picture 1>, a fictional adult aged 26: compact and soft, narrow waist, wide hips, full heavy breasts, round seat, olive skin with visible pores, long wavy dark brown hair, and the wardrobe she wears in <Picture 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1>.
<Picture 1> is the approved 16:9 start photograph of <Subject 1> and <Subject 2> standing side by side, the blonde woman at the left of centre and the dark-haired woman right of centre, both faces in the upper half of frame. It is the first frame of this video and it defines their bodies, skin, figures, faces, hair, wardrobe, the room, the floor, the wall, the light, the colour cast and the camera position.

summary:
[reference generation] The target video is the first 5.17 seconds of a single continuous 16:9 shot of <Subject 1> and <Subject 2>, two fictional adult women dressed as in <Picture 1>, who kiss, strip each other naked in one continuous motion, and sit down side by side on the floor of the opening photograph. The shot uses <Picture 1> as the first frame and the scene, and <Picture 2> as the face and hair of <Subject 2>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the blonde woman of <Picture 1>, keeping her face, hair, athletic figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - the dark-haired woman of <Picture 2> and <Picture 1>, keeping her face, hair, soft figure, skin tone, height, build and the wardrobe of <Picture 1>.
<Picture 1> ([Shot 1] first frame): fully_preserved - the room, the floor, the wall, the light direction, the colour cast, the standing start position of the pair, the 16:9 framing and the camera height.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women.
[Shot 1] A single continuous 16:9 medium two-shot that keeps the framing, the room, the floor, the wall, the light and the colour of <Picture 1> exactly, with <Picture 1> as the first frame. <Subject 1> stands at the left of centre and <Subject 2> stands right of centre, both in the wardrobe of <Picture 1>, at the same distance from the lens and the same height as the opening photograph, weight on their back feet, hips angled toward each other. Photorealistic skin and anatomy: natural matte skin with visible pores and fine vellus hair, real adult body mass with joint definition, five separate fingers on each hand, natural adult proportions, a soft sheen of sweat only where skin presses skin. The camera starts as a Static Shot on the pair, then a Push In with small amplitude at slow speed closes the lens distance by a hand's width across the segment. At 00:00.000, the frame is the opening photograph: the two women standing, chins lifted, mouths closed, hands loose at their sides, the light of <Picture 1> lying across their collarbones. At 00:01.400, <Subject 1> closes the half pace and takes <Subject 2>'s mouth; her hands cup the dark-haired woman's jaw and the back of her head, fingers opening into the wavy hair, while <Subject 2>'s palms slide down the blonde's arms and grip her forearms, and both women breathe through their open mouths against each other. At 00:03.000, working together in one continuous motion, they strip: <Subject 1>'s hands hook the hem of <Subject 2>'s top and draw it up over her ribs, heavy breasts and head, and <Subject 2> pulls the blonde's top up and off in the same pull; then their hands go to each other's waistband and the lower garments follow both tops down legs and off, fabric pooling on the floor of <Picture 1> and leaving frame, so that for the first time both women stand naked in the light of the opening photograph: <Subject 1> tall and athletic, taut flat chest with small pale areolae, long defined abdomen, narrow hips, a neat pale triangle of pubic hair; <Subject 2> compact and soft, heavy full breasts swinging once and settling with her weight, darker areolae, wide hips, thick thighs, a dark triangle of pubic hair, her skin catching the key light along the underside of her breasts. At 00:04.400, <Subject 2> sits down onto the floor with her hands on her own knees, and <Subject 1> lowers herself down beside her, closing the gap until their thighs touch, elbows on her knees, faces leaning together, both chests rising fast, nipples taut in the cooler air of the room. The shot ends with the two women seated side by side on the floor of <Picture 1>, shoulders touching, lips pressed together, palms sliding over each other's knees, hair falling forward over their jaws.

overall_soundscape:
The room tone of the space in <Picture 1>, a soft ventilation hum and a faint outside wash through an open window. Fabric friction as two garments stretch and slide off, fabric pooling on the floor, the soft impact of two bodies sitting down, palms sliding on knees. Quickened breathing from both women, small open-mouthed sighs at the mouth of the kiss, a low humming moan pressed against the other's mouth.

non_diegetic_music:
A low muted guitar figure over a slow finger-snare loop, low volume, tempo around 68 bpm, dynamics rising gently with the kiss and settling as the pair sit down.

### id=ali163_hc15_bd013_s51150003 chunk=c1 seed=51150003

subject_definitions:
<Subject 1> is the blonde woman of the start photograph in <Picture 1>, a fictional adult aged 24: tall and athletic, flat stomach, firm long legs, fair skin with visible pores, long straight blonde hair, naked and seated on the floor as she became in <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 26: compact and soft, narrow waist, wide hips, full heavy breasts, round seat, olive skin with visible pores, long wavy dark brown hair, naked and seated on the floor as she became in <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from the body the viewer saw in <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it defines their bodies, skin, figures, faces, hair, the room, the floor, the wall, the light, the colour cast and the camera context for both women.

summary:
[video continuation + reference generation] This segment continues the same single continuous shot from <Video 1>: over the next 4.96 seconds <Subject 1> and <Subject 2>, both naked and seated on the floor, turn toward each other, lock legs and grind pelvis to pelvis in slow long strokes, each woman's hands and mouth working on the other. The same room, floor, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, athletic figure, skin tone (carried from <Picture 1> and <Video 1>) and the seated, naked state her body reached in <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, soft figure, skin tone and the seated, naked state her body reached in <Video 1>.
<Video 1> (the first 5.17 seconds of this clip): fully_preserved - the room, the floor, the wall, the light direction, the colour cast, the framing, the camera height, and the discarded clothing on the floor outside frame.
<Picture 1> (scene anchor): partially_preserved - the room, floor, wall, light and colour carry; the two women are now naked and seated where they were standing and dressed in the photograph.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the contact of the two women.
[Shot 1] One continuous take that carries the lens position, room, floor, wall, light and colour of <Video 1> forward, the camera resuming as an Arc Shot with small amplitude at slow speed, curving a quarter of the way around the seated pair so the window light travels from the left of frame toward the camera, then settling into a Push In with small amplitude at slow speed. The two women sit side by side on the floor where the first segment left them, naked, their discarded clothing in a heap on the floor outside frame, skin glossy where their chests touched. At 00:05.200, <Subject 2> rolls onto her side and opens her legs, one ankle crossing over the blonde's shin, and <Subject 1> follows her down onto an elbow, sliding her own thigh between the dark-haired woman's legs until their pubic bones press together; both women exhale, eyes closing, hair spilling across the floor. At 00:06.800, the pair start a slow rocking rhythm, pelvis grinding against pelvis in long strokes, <Subject 1>'s free hand palm-down on <Subject 2>'s breast with her thumb rubbing a dark areola in small circles, <Subject 2>'s hand flat on the blonde's stomach and sliding up to cup her small breast and pinch the pale nipple between two fingers; the wet contact point of their bodies is visible in the window light, both women slick. At 00:08.400, <Subject 2> lifts the blonde's hand to her mouth and takes two fingers onto her tongue, suction and a slow circle with her tongue, while her other hand reaches between them to press the blonde's swollen wet folds harder against her own, and <Subject 1>'s hips stutter, her abdomen cramping, a broken moan leaving her open mouth. At 00:09.900, the women pull their foreheads together and kiss hard, tongues meeting, <Subject 1>'s fingers sliding down to stroke the dark-haired woman's inner thigh and the side of her breast at the same time, the rocking quickening, sweat darkening the floorboards where the pair are seated. The camera is steady, focus held on where their bodies meet, skin detail crisp and natural at the close distance, and the shot ends with the two women locked leg to leg, chests pressed, mouths on each other's jaws, hips moving fast.

overall_soundscape:
The same room tone as <Video 1>, the window wash a little louder with the camera closer. Skin sliding on skin in the rocking rhythm, a palm on a breast, an elbow shifting on the floor, a hand sucking a finger, wet contact at the meeting of their bodies. Breathing that turns into rising open-mouthed moans from both women, short sharp gasps, a muffled cry against the other's mouth.

non_diegetic_music:
The muted guitar figure continues, a brushed snare entering, tempo around 68 bpm, dynamics swelling with the rocking rhythm and easing at the end of the segment.

### id=ali163_hc15_bd013_s51150003 chunk=c2 seed=51150003

subject_definitions:
<Subject 1> is the blonde woman of the start photograph in <Picture 1>, a fictional adult aged 24: tall and athletic, fair skin with visible pores, long straight blonde hair, naked, seated leg to leg with <Subject 2> as she was at the end of <Video 1>. Her face, hair, body, skin and figure all come from <Picture 1> and from <Video 1>.
<Subject 2> is the adult woman whose face and hair are in the face crop in <Picture 2>, the dark-haired woman of the start photograph in <Picture 1>, a fictional adult aged 26: compact and soft, wide hips, thick thighs, full heavy breasts, olive skin with visible pores, long wavy dark brown hair, naked, seated leg to leg with <Subject 1> as she was at the end of <Video 1>. Her face and hair come from <Picture 2>; her body, skin and figure come from <Picture 1> and from <Video 1>.
<Picture 1> is the approved 16:9 start photograph of the two adult women in the room of <Picture 1>; it defines their faces, bodies, skin, the room, the floor, the wall, the light, the colour cast and the camera context.

summary:
[video continuation + reference generation] This segment continues the same single continuous take from <Video 1> for the final 4.96 seconds: each woman fingers the other, <Subject 2> comes first and <Subject 1> follows, and the pair fold together on the floor in the light and framing of the opening photograph. The room, floor, light, colour, lens and camera height carry from <Video 1>.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hair, athletic figure, skin tone and her seated position at the end of <Video 1>.
<Subject 2> (appears in [Shot 1]): fully_preserved - her face, hair, soft figure, skin tone and her seated position at the end of <Video 1>.
<Video 1> (the first 10.13 seconds of this clip): fully_preserved - the room, the floor, the wall, the light, the colour cast, the framing, the camera height, the discarded clothing on the floor outside frame, and the wetness already on both women.
<Picture 1> (scene anchor): partially_preserved - the room, floor, wall, light and colour carry; both women are naked and seated on the floor in front of the wall.

detailed_description:
Live-action, cinematic realism, warm natural light, muted realistic palette, shallow depth of field held on the two women's faces and the contact of their bodies.
[Shot 1] One continuous take resuming the exact framing and lens height of <Video 1>, the camera a Push In with small amplitude at slow speed for the first two beats, then a Pedestal Up with small amplitude at slow speed as the women lift onto each other, and a Pull Out with small amplitude at slow speed for the last beat so the pair settle back into the medium two-shot framing of the opening photograph. At 00:10.200, <Subject 1> rolls her thumb over the swollen dark nub at the top of the joined bodies while <Subject 2> works two fingers inside herself in the same stroke, knuckle grazing, a wet sound opening with it, her heavy breasts pressing flat against the blonde's ribs; both women are breathing hard, their legs locked, sweat on both chests. At 00:11.600, <Subject 2> comes first: her hips stutter in three short pulses against the blonde's hand, her thighs clamp, her abdomen cramping, her mouth open on a rising cry she swallows into the blonde's jaw, her fingers twisting in the blonde hair, her heavy breasts shivering with each pulse, areolae taut, wetness shining between their bodies. At 00:13.000, <Subject 2> answers it: she slides two fingers into <Subject 1> with one long curling stroke and circles the pale nub with her thumb, and the blonde's back bows, her toes curling on the floor, her flat chest heaving, her hips snapping forward onto the dark-haired woman's hand in four quick pulses, a long broken moan breaking into words she swallows, her eyes shutting. At 00:14.300, the women fold onto each other, foreheads pressed together, <Subject 1>'s arm locked around <Subject 2>'s shoulders, <Subject 2>'s hand open on the blonde's stomach, both bodies twitching, both chests rising and falling fast, mouths parting for breath against each other's lips. The final frame is the two women seated side by side on the floor of <Picture 1> in the same 16:9 medium framing, the same room, wall and light as the opening photograph, both naked, both slick, hair across their faces, the wall steady behind them.

overall_soundscape:
The room tone of <Video 1> with the window wash steady underneath. Wet finger sounds at the meeting of their bodies, skin slapping softly in the rocking, a palm on a thigh, the floor shifting under two bodies, hair being gripped. <Subject 2> crying out and swallowing the cry into the blonde's jaw, <Subject 1> moaning loudly and breaking into words, both women gasping and laughing softly in the last second.

non_diegetic_music:
The guitar figure resolves into a slower two-chord loop, brushed snare dropping out, tempo around 68 bpm, dynamics peaking across the two climaxes and fading to a soft sustain as the pair fold together.
