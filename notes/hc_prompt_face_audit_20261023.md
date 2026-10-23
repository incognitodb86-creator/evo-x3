# ALI-163 R4F - prompt / reference / face-box AUDIT of c1, c2, r1, r2 (2026-10-23, Forge)

Task line `R4F FACE RESEARCH` (WIDENED part), ralph-community\TASKS.md. Companion: notes\hc_face_research_20261023.md (similarity tables T1-T3 + the ranked fix list F1-F10).
No GPU, no ComfyUI/llama-swap call, no render, no vision judge, no download. Machine-measured only:
prompts and reference slots come from `runs\<id>\request.api.json`; pixel sizes from PIL; face boxes from SCRFD-10G + ArcFace glintr100 on CPU (`C:\AI\qa_gate_venv`, `notes\hc_r4f_facelib.py`); the reference-canvas math mirrors the installed community node `ComfyUI\custom_nodes\ComfyUI_MiniMax_H3_Extender\extender.py:2267-2310` with `REF_IMAGE_SHORT_EDGE = 2048` (`extender.py:113`) and the `match`/`max` rule of `ref_image_size` (`extender.py:2271-2274`, default `match` at `extender.py:5007`).
Builder script: `C:\AI\community\notes\ali163_hc_r4f_audit.py` (this file's tables are its output).

## ali147_pool_hc_c1_s51100001  (c1, 1344x768)

| setting | value |
|---|---|
| model (UNETLoader) | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors |
| clip | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| video vae / audio vae | minimax_h3_video_vae_int8_convrot.safetensors / minimax_h3_audio_vae_fp32.safetensors |
| c0 class_type | MiniMaxH3ReferenceToVideo |
| c0 length (frames) | 243 |
| c1 class_type | MiniMaxH3ImageToVideo |
| c1 length | ['win1', 1] |
| continuation window | {"extension_frames": 238, "overlap_frames": 22} |
| total frames (c0 + extension) | 243 + 238 |
| width x height x fps | 1344x768x24 |
| steps / scheduler / sampler / denoise | 10 / simple / euler / 1.0 |
| shift_video / shift_audio | 10.0 / 3.0 |
| noise_seed | 51100001 |
| ref_image_size (c0 / c1) | match / n/a (I2V) |
| save prefix | community/ali147_pool_hc_c1_s51100001/ali147_pool_hc_c1_s51100001 |

### Reference slots (<Picture N> -> LoadImage -> file) as wired in the graph

| chunk | slot | LoadImage node | file on disk | file px | aspect | sha256(12) | ref_image_size | ref canvas px | ref Mpx | faces in ref | biggest face px | face % of ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c0 | <Picture 1> | `img` (LoadImage) | `community/hc/HC1_Two_women_in_studio_editorial.jpg` | 1376x768 | 1.792 | dd9ed0cb69e4 | match | 1344x768 | 1.03 | 2 | 175x150 | 2.43% |

### Prompt nodes (every text node in the graph)

| chunk | class_type | chars | blocks present (in order) | subject binding lines |
|---|---|---|---|---|
| c0 | MiniMaxH3ReferenceToVideo | 4497 | subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music | 6 |
| c1 | MiniMaxH3ImageToVideo | 2794 | integrated_multimodal_description, overall_soundscape, non_diegetic_music | 0 |

#### ali147_pool_hc_c1_s51100001.c0 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 25, with soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 24, with a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
 4| 
 5| summary:
 6| [reference generation] The target video is a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm photo studio. The shot uses <Picture 1> only as appearance guidance while freely composing the environment, wardrobe and camera. The two women kiss, pull each other's clothing off, and settle onto a dark studio floor with <Subject 2> on her knees between the spread thighs of <Subject 1>, who leans back on her hands. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.
 7| 
 8| retention_analysis:
 9| <Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
10| <Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long dark hair, soft feminine figure and warm skin; her kneeling position and the movement of her head are actions, not a change of identity.
11| Their clothing from <Picture 1> is removed during the shot and lies in a heap on the floor beside them for the rest of the clip.
12| 
13| detailed_description:
14| The target video is a realistic, warmly lit studio scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
15| [Shot 1] The shot opens on <Subject 1>, the blonde adult woman from <Picture 1>, and <Subject 2>, the dark-haired adult woman from <Picture 1>, standing close together in front of a warm beige seamless studio backdrop lit by a soft key light from the left. They are both fully clothed in studio outfits taken from <Picture 1>. The camera starts in a medium two-shot and moves in slowly and steadily, low amplitude, no cuts. They kiss with open mouths, tongues touching, and <Subject 1>'s hands pull the shirt of <Subject 2> up and over her head while <Subject 2> unfastens the front of <Subject 1>'s top. The garments slide off shoulders and arms with visible friction, then drop to the floor. <Subject 1> is bare-breasted: full natural breasts with soft realistic weight, smooth skin and round light-brown areolae with natural nipples. <Subject 2> is also topless, her darker-skinned breasts swaying as she moves. They lower themselves onto the dark studio floor. <Subject 1> leans back on both palms, elbows bent, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs, leans forward, and presses her mouth and tongue against the bare, wet vulva of <Subject 1>, her thumbs spreading the outer lips apart while her tongue works in slow, continuous strokes. <Subject 1>'s hips rise in small weighted thrusts toward the contact, her stomach tensing, fingers pressing into the floor. Her thighs tremble and her toes curl. Wet gloss shows at the point of contact, and thin strands of blonde hair stick to her inner thigh. The camera keeps a stable focal plane on the two bodies with the backdrop softly blurred, drifting slightly lower to keep the contact in frame without cutting. Both women keep their eyes open at times and glance at the camera, expressions dazed and pleased. Breathing is heavy, chests rising and falling. The shot ends with <Subject 2> still between the thighs of <Subject 1>, head down, hips of <Subject 1> lifting into the contact, the discarded clothing in a heap beside them.
16| 
17| overall_soundscape:
18| A quiet studio room tone with a low, soft air-conditioning hum. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, soft wet sliding sounds from the tongue against the vulva, fabric sliding off skin and landing softly on the floor, deep breathing, and low moaning and gasping from both women. No dialogue, no announcer, no crowd, no music-video narration; the room stays otherwise silent.
19| 
20| non_diegetic_music:
21| N/A
```

#### ali147_pool_hc_c1_s51100001.c1 subject/reference binding, line by line (verbatim from the graph)

```text
 1| integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous studio moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the prior clip are kept exactly: <Subject 1> with long blonde hair, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, lightly tanned skin; <Subject 2> with long dark hair, soft feminine figure, warm smooth skin, bare breasts. They are on the dark studio floor in front of the warm beige seamless backdrop, both naked, their discarded studio clothing in a heap beside them. <Subject 1> is leaning back on her hands with her thighs spread; <Subject 2> is on her knees between them, head down, mouth and tongue on the wet vulva of <Subject 1>. The camera holds a stable shot, then pushes in with small amplitude at slow speed, keeping both bodies framed from the knees to the top of the head. <Subject 2> works in slow, continuous strokes, her tongue flat and moving, her fingers spread on the inner thighs of <Subject 1> to hold them open. <Subject 1> lifts her hips in slow weighted thrusts into the contact, her stomach tightening, her chest heaving, her head falling back and her mouth opening in a long soundless moan. Her hands leave the floor, grip the shoulders of <Subject 2>, and press her closer. Wet gloss stretches and breaks at the point of contact, with visible slip on the skin. <Subject 2> looks up briefly toward the camera with her mouth still pressed to the contact, then goes back down, her dark hair falling forward and brushing the thigh of <Subject 1>. The thighs of <Subject 1> tremble, her toes curl, her hips rise higher and press down in a small shuddering rhythm as the clip ends, both women still locked in the same contact, the camera steady on them.
 2| 
 3| overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. A soft skin squeak on the floor as weight shifts. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.
 4| 
 5| non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

<details><summary>verbatim full prompt - ali147_pool_hc_c1_s51100001.c0 (4497 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 25, with soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 24, with a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.

summary:
[reference generation] The target video is a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm photo studio. The shot uses <Picture 1> only as appearance guidance while freely composing the environment, wardrobe and camera. The two women kiss, pull each other's clothing off, and settle onto a dark studio floor with <Subject 2> on her knees between the spread thighs of <Subject 1>, who leans back on her hands. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
<Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long dark hair, soft feminine figure and warm skin; her kneeling position and the movement of her head are actions, not a change of identity.
Their clothing from <Picture 1> is removed during the shot and lies in a heap on the floor beside them for the rest of the clip.

detailed_description:
The target video is a realistic, warmly lit studio scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
[Shot 1] The shot opens on <Subject 1>, the blonde adult woman from <Picture 1>, and <Subject 2>, the dark-haired adult woman from <Picture 1>, standing close together in front of a warm beige seamless studio backdrop lit by a soft key light from the left. They are both fully clothed in studio outfits taken from <Picture 1>. The camera starts in a medium two-shot and moves in slowly and steadily, low amplitude, no cuts. They kiss with open mouths, tongues touching, and <Subject 1>'s hands pull the shirt of <Subject 2> up and over her head while <Subject 2> unfastens the front of <Subject 1>'s top. The garments slide off shoulders and arms with visible friction, then drop to the floor. <Subject 1> is bare-breasted: full natural breasts with soft realistic weight, smooth skin and round light-brown areolae with natural nipples. <Subject 2> is also topless, her darker-skinned breasts swaying as she moves. They lower themselves onto the dark studio floor. <Subject 1> leans back on both palms, elbows bent, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs, leans forward, and presses her mouth and tongue against the bare, wet vulva of <Subject 1>, her thumbs spreading the outer lips apart while her tongue works in slow, continuous strokes. <Subject 1>'s hips rise in small weighted thrusts toward the contact, her stomach tensing, fingers pressing into the floor. Her thighs tremble and her toes curl. Wet gloss shows at the point of contact, and thin strands of blonde hair stick to her inner thigh. The camera keeps a stable focal plane on the two bodies with the backdrop softly blurred, drifting slightly lower to keep the contact in frame without cutting. Both women keep their eyes open at times and glance at the camera, expressions dazed and pleased. Breathing is heavy, chests rising and falling. The shot ends with <Subject 2> still between the thighs of <Subject 1>, head down, hips of <Subject 1> lifting into the contact, the discarded clothing in a heap beside them.

overall_soundscape:
A quiet studio room tone with a low, soft air-conditioning hum. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, soft wet sliding sounds from the tongue against the vulva, fabric sliding off skin and landing softly on the floor, deep breathing, and low moaning and gasping from both women. No dialogue, no announcer, no crowd, no music-video narration; the room stays otherwise silent.

non_diegetic_music:
N/A
```

</details>

<details><summary>verbatim full prompt - ali147_pool_hc_c1_s51100001.c1 (2794 chars)</summary>

```text
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous studio moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the prior clip are kept exactly: <Subject 1> with long blonde hair, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, lightly tanned skin; <Subject 2> with long dark hair, soft feminine figure, warm smooth skin, bare breasts. They are on the dark studio floor in front of the warm beige seamless backdrop, both naked, their discarded studio clothing in a heap beside them. <Subject 1> is leaning back on her hands with her thighs spread; <Subject 2> is on her knees between them, head down, mouth and tongue on the wet vulva of <Subject 1>. The camera holds a stable shot, then pushes in with small amplitude at slow speed, keeping both bodies framed from the knees to the top of the head. <Subject 2> works in slow, continuous strokes, her tongue flat and moving, her fingers spread on the inner thighs of <Subject 1> to hold them open. <Subject 1> lifts her hips in slow weighted thrusts into the contact, her stomach tightening, her chest heaving, her head falling back and her mouth opening in a long soundless moan. Her hands leave the floor, grip the shoulders of <Subject 2>, and press her closer. Wet gloss stretches and breaks at the point of contact, with visible slip on the skin. <Subject 2> looks up briefly toward the camera with her mouth still pressed to the contact, then goes back down, her dark hair falling forward and brushing the thigh of <Subject 1>. The thighs of <Subject 1> tremble, her toes curl, her hips rise higher and press down in a small shuddering rhythm as the clip ends, both women still locked in the same contact, the camera steady on them.

overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. A soft skin squeak on the floor as weight shifts. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.

non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

</details>

### Face box per woman over 5 evenly spaced frames (SCRFD-10G thr 0.4 at 640x640, frame 1344x768 = 1.032 Mpx)

| frame | n_faces | woman | box px (WxH) | face area px2 | % of frame | arcface cos to her sheet anchor |
|---|---|---|---|---|---|---|
| 0 | 2 | w1 | 108x189 | 20562 | 1.99% | 0.127 |
| 0 | 2 | w2 | 108x189 | 20562 | 1.99% | 0.225 |
| 80 | 1 | w1 | 181x183 | 33340 | 3.23% | 0.136 |
| 80 | 1 | w2 | 181x183 | 33340 | 3.23% | 0.350 |
| 160 | 2 | w1 | 111x150 | 16699 | 1.62% | 0.168 |
| 160 | 2 | w2 | 111x150 | 16699 | 1.62% | 0.216 |
| 240 | 2 | w1 | 104x131 | 13803 | 1.34% | 0.065 |
| 240 | 2 | w2 | 104x131 | 13803 | 1.34% | 0.203 |
| 320 | 2 | w1 | 119x151 | 18081 | 1.75% | 0.101 |
| 320 | 2 | w2 | 191x166 | 31978 | 3.10% | 0.171 |

## ali147_pool_hc_c2_s51100002  (c2, 1344x768)

| setting | value |
|---|---|
| model (UNETLoader) | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors |
| clip | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| video vae / audio vae | minimax_h3_video_vae_int8_convrot.safetensors / minimax_h3_audio_vae_fp32.safetensors |
| c0 class_type | MiniMaxH3ReferenceToVideo |
| c0 length (frames) | 243 |
| c1 class_type | MiniMaxH3ImageToVideo |
| c1 length | ['win1', 1] |
| continuation window | {"extension_frames": 238, "overlap_frames": 22} |
| total frames (c0 + extension) | 243 + 238 |
| width x height x fps | 1344x768x24 |
| steps / scheduler / sampler / denoise | 10 / simple / euler / 1.0 |
| shift_video / shift_audio | 10.0 / 3.0 |
| noise_seed | 51100002 |
| ref_image_size (c0 / c1) | match / n/a (I2V) |
| save prefix | community/ali147_pool_hc_c2_s51100002/ali147_pool_hc_c2_s51100002 |

### Reference slots (<Picture N> -> LoadImage -> file) as wired in the graph

| chunk | slot | LoadImage node | file on disk | file px | aspect | sha256(12) | ref_image_size | ref canvas px | ref Mpx | faces in ref | biggest face px | face % of ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c0 | <Picture 1> | `img` (LoadImage) | `community/hc/HC2_Two_women_in_passionate_embrace.jpg` | 1376x768 | 1.792 | 530f056f4eb2 | match | 1344x768 | 1.03 | 2 | 133x203 | 2.52% |

### Prompt nodes (every text node in the graph)

| chunk | class_type | chars | blocks present (in order) | subject binding lines |
|---|---|---|---|---|
| c0 | MiniMaxH3ReferenceToVideo | 4777 | subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music | 6 |
| c1 | MiniMaxH3ImageToVideo | 3227 | integrated_multimodal_description, overall_soundscape, non_diegetic_music | 0 |

#### ali147_pool_hc_c2_s51100002.c0 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 26, with soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 25, with a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
 4| 
 5| summary:
 6| [reference generation] The target video is a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm bedroom at dusk. The shot uses <Picture 1> only as appearance guidance for the two faces, hair and figures while freely composing the room, wardrobe and camera. The two women embrace and kiss hard, shrug off their clothes, lie down naked side by side and press their groins together while rubbing, <Subject 2> sliding one hand between the thighs of <Subject 1>. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.
 7| 
 8| retention_analysis:
 9| <Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing, embracing and being touched are actions, not a change of identity.
10| <Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long dark hair, soft feminine figure, wide hips and warm skin; her movements on the bed and the shifting of her legs are actions, not a change of identity.
11| Their clothing from <Picture 1> is shrugged off during the shot and lands on the bedroom rug, and both women stay naked for the rest of the clip.
12| 
13| detailed_description:
14| The target video is a realistic, warmly lit bedroom scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
15| [Shot 1] The shot opens on <Subject 1>, the blonde adult woman from <Picture 1>, and <Subject 2>, the dark-haired adult woman from <Picture 1>, standing chest to chest beside a rumpled bed in a bedroom lit by warm dusk light through a half-curtained window, a soft lamp glow filling the shadows. They are both fully clothed in the everyday outfits implied by <Picture 1>. The camera starts in a medium two-shot at chest height and drifts in slowly and steadily, low amplitude, no cuts. They kiss with open mouths, tongues moving, hands roaming over each other's back and breasts through the fabric. <Subject 2> shrugs her top off her shoulders and pulls the shirt of <Subject 1> over her head; the garments slide down arms and drop to the rug. Both women are naked: <Subject 1> with full natural bare breasts, soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer bare breasts and wider hips. They sit and lie down onto the bed, propped on elbows, legs tangling. <Subject 1> parts her thighs and <Subject 2> settles against her, pressing her own naked groin along the wet vulva of <Subject 1> and rubbing in slow, continuous, weighted strokes, her head tipped back and eyes half closed. <Subject 2> slides one hand under the buttock of <Subject 1>, thumb working at her entrance, and <Subject 1> guides two of her fingers inside her, her palm flat against her stomach, fingers curling with visible rhythm. Wet gloss stretches between their pressed groins, skin sliding on skin, and the bedding creases under their weight. <Subject 1> arches, her chest heaving, toes curling, a hand fisted in the dark hair of <Subject 2>; <Subject 2> leans down and kisses her jaw while her hand keeps its rhythm. The camera keeps the two bodies and the point of contact in frame, the window light raking across their skin, the room softly blurred behind them. The shot ends with them still pressed together, <Subject 2> moving against the thighs of <Subject 1>, fingers still working, both breathing hard.
16| 
17| overall_soundscape:
18| A quiet bedroom room tone with a low distant city hum and soft traffic outside the window, plus a faint bedside lamp buzz. Close muffled intimate sound: wet kissing and tongue sounds, fabric sliding off skin and landing softly on the rug, bedsprings creaking and bedding rustling under shifting weight, skin sliding on skin, soft flesh thudding and skin of the bodies clapping together as groins press and rub, soft wet sliding sounds at the point of contact, small wet finger sounds, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no crowd, no narration; the room stays otherwise silent.
19| 
20| non_diegetic_music:
21| N/A
```

#### ali147_pool_hc_c2_s51100002.c1 subject/reference binding, line by line (verbatim from the graph)

```text
 1| integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous bedroom moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the prior clip are kept exactly: <Subject 1> with long blonde hair, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, lightly tanned skin; <Subject 2> with long dark hair, soft feminine figure, wide hips, bare breasts, warm smooth skin. They are naked on the rumpled bed in the warm dusk bedroom, their discarded clothing on the rug beside the bed frame. <Subject 2> lies on her side facing <Subject 1>, her groin pressed along the spread, wet thighs of <Subject 1>, one arm under the neck of <Subject 1>, her other hand between the thighs of <Subject 1> with two fingers moving in and out in a slow steady rhythm, thumb working at her entrance. <Subject 1> is propped on one elbow, her chest heaving, her free hand gripping the sheets, her hips answering with small weighted forward strokes so that their groins meet on every pass. The camera holds a stable shot, then pushes in with small amplitude at slow speed, keeping both bodies framed from the knees to the top of the head and the point of contact in the lower third of the frame. They kiss deeply, tongues sliding, then <Subject 1> turns her face into the shoulder of <Subject 2>, mouth open, biting her own lip to keep from crying out. Wet gloss stretches and breaks between their pressed groins, with visible slip on the skin, and the dark hair of <Subject 2> falls forward across the shoulder of <Subject 1>. The thighs of <Subject 1> tremble, her toes curl, her stomach tightens, her hips rise and press down in a small shuddering rhythm as the fingers of <Subject 2> quicken, one hand flattening on the stomach of <Subject 1> to hold her in place. <Subject 2> lifts her head, looks briefly toward the camera with dazed eyes, then goes back down against the neck of <Subject 1>. The bedding creases, the bedsprings give a short creak, and the two women stay locked in the same contact, hips moving together as the clip ends, the camera steady on them.
 2| 
 3| overall_soundscape: Soft bedroom room tone with a low distant city hum, muffled night traffic beyond the window and a faint lamp buzz. Intimate close sound: repeated wet kissing and tongue sounds, soft wet sliding sounds and small wet finger sounds at the point of contact, skin sliding on skin, soft flesh thudding and skin of the bodies clapping together as hips answer the contact, fabric and bedding rustling with every shift of weight, a short bedspring creak, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.
 4| 
 5| non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

<details><summary>verbatim full prompt - ali147_pool_hc_c2_s51100002.c0 (4777 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 26, with soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 25, with a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.

summary:
[reference generation] The target video is a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm bedroom at dusk. The shot uses <Picture 1> only as appearance guidance for the two faces, hair and figures while freely composing the room, wardrobe and camera. The two women embrace and kiss hard, shrug off their clothes, lie down naked side by side and press their groins together while rubbing, <Subject 2> sliding one hand between the thighs of <Subject 1>. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing, embracing and being touched are actions, not a change of identity.
<Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 1> gives her identity, long dark hair, soft feminine figure, wide hips and warm skin; her movements on the bed and the shifting of her legs are actions, not a change of identity.
Their clothing from <Picture 1> is shrugged off during the shot and lands on the bedroom rug, and both women stay naked for the rest of the clip.

detailed_description:
The target video is a realistic, warmly lit bedroom scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
[Shot 1] The shot opens on <Subject 1>, the blonde adult woman from <Picture 1>, and <Subject 2>, the dark-haired adult woman from <Picture 1>, standing chest to chest beside a rumpled bed in a bedroom lit by warm dusk light through a half-curtained window, a soft lamp glow filling the shadows. They are both fully clothed in the everyday outfits implied by <Picture 1>. The camera starts in a medium two-shot at chest height and drifts in slowly and steadily, low amplitude, no cuts. They kiss with open mouths, tongues moving, hands roaming over each other's back and breasts through the fabric. <Subject 2> shrugs her top off her shoulders and pulls the shirt of <Subject 1> over her head; the garments slide down arms and drop to the rug. Both women are naked: <Subject 1> with full natural bare breasts, soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer bare breasts and wider hips. They sit and lie down onto the bed, propped on elbows, legs tangling. <Subject 1> parts her thighs and <Subject 2> settles against her, pressing her own naked groin along the wet vulva of <Subject 1> and rubbing in slow, continuous, weighted strokes, her head tipped back and eyes half closed. <Subject 2> slides one hand under the buttock of <Subject 1>, thumb working at her entrance, and <Subject 1> guides two of her fingers inside her, her palm flat against her stomach, fingers curling with visible rhythm. Wet gloss stretches between their pressed groins, skin sliding on skin, and the bedding creases under their weight. <Subject 1> arches, her chest heaving, toes curling, a hand fisted in the dark hair of <Subject 2>; <Subject 2> leans down and kisses her jaw while her hand keeps its rhythm. The camera keeps the two bodies and the point of contact in frame, the window light raking across their skin, the room softly blurred behind them. The shot ends with them still pressed together, <Subject 2> moving against the thighs of <Subject 1>, fingers still working, both breathing hard.

overall_soundscape:
A quiet bedroom room tone with a low distant city hum and soft traffic outside the window, plus a faint bedside lamp buzz. Close muffled intimate sound: wet kissing and tongue sounds, fabric sliding off skin and landing softly on the rug, bedsprings creaking and bedding rustling under shifting weight, skin sliding on skin, soft flesh thudding and skin of the bodies clapping together as groins press and rub, soft wet sliding sounds at the point of contact, small wet finger sounds, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no crowd, no narration; the room stays otherwise silent.

non_diegetic_music:
N/A
```

</details>

<details><summary>verbatim full prompt - ali147_pool_hc_c2_s51100002.c1 (3227 chars)</summary>

```text
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous bedroom moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the prior clip are kept exactly: <Subject 1> with long blonde hair, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, lightly tanned skin; <Subject 2> with long dark hair, soft feminine figure, wide hips, bare breasts, warm smooth skin. They are naked on the rumpled bed in the warm dusk bedroom, their discarded clothing on the rug beside the bed frame. <Subject 2> lies on her side facing <Subject 1>, her groin pressed along the spread, wet thighs of <Subject 1>, one arm under the neck of <Subject 1>, her other hand between the thighs of <Subject 1> with two fingers moving in and out in a slow steady rhythm, thumb working at her entrance. <Subject 1> is propped on one elbow, her chest heaving, her free hand gripping the sheets, her hips answering with small weighted forward strokes so that their groins meet on every pass. The camera holds a stable shot, then pushes in with small amplitude at slow speed, keeping both bodies framed from the knees to the top of the head and the point of contact in the lower third of the frame. They kiss deeply, tongues sliding, then <Subject 1> turns her face into the shoulder of <Subject 2>, mouth open, biting her own lip to keep from crying out. Wet gloss stretches and breaks between their pressed groins, with visible slip on the skin, and the dark hair of <Subject 2> falls forward across the shoulder of <Subject 1>. The thighs of <Subject 1> tremble, her toes curl, her stomach tightens, her hips rise and press down in a small shuddering rhythm as the fingers of <Subject 2> quicken, one hand flattening on the stomach of <Subject 1> to hold her in place. <Subject 2> lifts her head, looks briefly toward the camera with dazed eyes, then goes back down against the neck of <Subject 1>. The bedding creases, the bedsprings give a short creak, and the two women stay locked in the same contact, hips moving together as the clip ends, the camera steady on them.

overall_soundscape: Soft bedroom room tone with a low distant city hum, muffled night traffic beyond the window and a faint lamp buzz. Intimate close sound: repeated wet kissing and tongue sounds, soft wet sliding sounds and small wet finger sounds at the point of contact, skin sliding on skin, soft flesh thudding and skin of the bodies clapping together as hips answer the contact, fabric and bedding rustling with every shift of weight, a short bedspring creak, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.

non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

</details>

### Face box per woman over 5 evenly spaced frames (SCRFD-10G thr 0.4 at 640x640, frame 1344x768 = 1.032 Mpx)

| frame | n_faces | woman | box px (WxH) | face area px2 | % of frame | arcface cos to her sheet anchor |
|---|---|---|---|---|---|---|
| 0 | 2 | w1 | 97x187 | 18254 | 1.77% | 0.139 |
| 0 | 2 | w2 | 116x179 | 20909 | 2.03% | 0.203 |
| 80 | 2 | w1 | 102x125 | 12878 | 1.25% | 0.078 |
| 80 | 2 | w2 | 90x123 | 11215 | 1.09% | 0.173 |
| 160 | 2 | w1 | 156x128 | 20075 | 1.94% | 0.164 |
| 160 | 2 | w2 | 156x128 | 20075 | 1.94% | 0.186 |
| 240 | 2 | w1 | 139x150 | 21088 | 2.04% | 0.283 |
| 240 | 2 | w2 | 139x150 | 21088 | 2.04% | 0.155 |
| 320 | 1 | w1 | 170x199 | 34095 | 3.30% | 0.150 |
| 320 | 1 | w2 | 170x199 | 34095 | 3.30% | 0.196 |

## ali147_pool_hc_r1_s51130001  (r1, 1344x768)

| setting | value |
|---|---|
| model (UNETLoader) | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors |
| clip | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| video vae / audio vae | minimax_h3_video_vae_int8_convrot.safetensors / minimax_h3_audio_vae_fp32.safetensors |
| c0 class_type | MiniMaxH3ReferenceToVideo |
| c0 length (frames) | 124 |
| c1 class_type | MiniMaxH3ReferenceToVideo |
| c1 length | ['win1', 1] |
| continuation window | {"extension_frames": 119, "overlap_frames": 22} |
| total frames (c0 + extension) | 124 + 119 |
| width x height x fps | 1344x768x24 |
| steps / scheduler / sampler / denoise | 10 / simple / euler / 1.0 |
| shift_video / shift_audio | 10.0 / 3.0 |
| noise_seed | 51130001 |
| ref_image_size (c0 / c1) | max / max |
| save prefix | community/ali147_pool_hc_r1_s51130001/ali147_pool_hc_r1_s51130001 |

### Reference slots (<Picture N> -> LoadImage -> file) as wired in the graph

| chunk | slot | LoadImage node | file on disk | file px | aspect | sha256(12) | ref_image_size | ref canvas px | ref Mpx | faces in ref | biggest face px | face % of ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c0 | <Picture 1> | `img` (LoadImage) | `community/hc/HC1_Two_women_in_studio_editorial.jpg` | 1376x768 | 1.792 | dd9ed0cb69e4 | max | 1376x768 | 1.06 | 2 | 175x150 | 2.49% |
| c0 | <Picture 2> | `sheet` (LoadImage) | `community/hc/HC1_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 022cd65e0c33 | max | 1152x2016 | 2.32 | 2 | 212x310 | 2.84% |
| c0 | <Picture 3> | `sheet2` (Load Image (HC1_w2 darkhair sheet)) | `community/hc/HC1_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 8336fa03aab3 | max | 1152x2016 | 2.32 | 4 | 247x349 | 3.73% |
| c1 | <Picture 1> | `sheet` (LoadImage) | `community/hc/HC1_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 022cd65e0c33 | max | 1152x2016 | 2.32 | 2 | 212x310 | 2.84% |
| c1 | <Picture 2> | `sheet2` (Load Image (HC1_w2 darkhair sheet)) | `community/hc/HC1_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 8336fa03aab3 | max | 1152x2016 | 2.32 | 4 | 247x349 | 3.73% |

### Prompt nodes (every text node in the graph)

| chunk | class_type | chars | blocks present (in order) | subject binding lines |
|---|---|---|---|---|
| c0 | MiniMaxH3ReferenceToVideo | 4210 | subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music | 9 |
| c1 | MiniMaxH3ReferenceToVideo | 3443 | subject_definitions, integrated_multimodal_description, overall_soundscape, non_diegetic_music | 3 |

#### ali147_pool_hc_r1_s51130001.c0 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 24, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
 4| <Picture 1> is the start still of <Subject 1> and <Subject 2> seated close together in a warm photo studio.
 5| <Picture 2> is the multi-view reference sheet of <Subject 1> alone.
 6| <Picture 3> is the multi-view reference sheet of <Subject 2> alone.
 7| 
 8| summary:
 9| [reference generation] The target video is the first 5 seconds of a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm photo studio. The shot uses <Picture 1> for the scene and <Picture 2> and <Picture 3> only as appearance guidance for the two women while freely composing the environment, wardrobe and camera. The two women lean in, kiss with open mouths, and pull each other's studio clothing off, ending topless and close. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.
10| 
11| retention_analysis:
12| <Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 2> keeps her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
13| <Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 3> keeps her identity, long dark hair, soft feminine figure, wide hips and warm skin; kneeling and touching are actions, not a change of identity.
14| Their studio clothing from <Picture 1> is removed during the shot and lies in a heap on the dark studio floor for the rest of the clip.
15| 
16| detailed_description:
17| The target video is a realistic, warmly lit studio scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen, realistic natural body proportions, and dynamic video with fluid natural motions.
18| [Shot 1] The shot opens on <Subject 1>, the blonde adult woman of <Picture 2>, and <Subject 2>, the dark-haired adult woman of <Picture 3>, seated close together on a dark studio floor in front of a warm beige seamless backdrop lit by a soft key light from the left. They wear the studio outfits of <Picture 1>. The camera starts in a medium two-shot and moves in slowly and steadily, low amplitude, no cuts. They lean in and kiss with open mouths, tongues touching, faces close, eyes half closed. <Subject 1>'s hands pull the shirt of <Subject 2> up and over her head while <Subject 2> unfastens the front of <Subject 1>'s top. The garments slide off shoulders and arms with visible friction and drop to the floor. Both women end the shot topless: <Subject 1> with full natural breasts of soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer, darker-skinned breasts that sway as she moves. Their faces stay close, foreheads touching, breathing heavy, chests rising and falling. Body contact is continuous and weighted: hips shifting, knees parting, thighs brushing, one hand flat on the floor for balance. The camera keeps a stable focal plane on the two bodies with the backdrop softly blurred. The shot ends with the two women still kissing, naked from the waist up, the discarded clothing in a heap beside them.
19| 
20| overall_soundscape:
21| A quiet studio room tone with a low, soft air-handling hum. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, fabric sliding off skin and landing softly on the floor, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no counting, no crowd, no narration; the room stays otherwise silent.
22| 
23| non_diegetic_music:
24| N/A
```

#### ali147_pool_hc_r1_s51130001.c1 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin.
 4| 
 5| integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous studio moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the first 5 seconds are kept exactly, <Subject 1> exactly as the sheet in <Picture 1> and <Subject 2> exactly as the sheet in <Picture 2>: <Subject 1> with long blonde hair, slim natural figure and full natural bare breasts; <Subject 2> with long dark hair, soft feminine figure, wide hips and bare breasts. They are on the dark studio floor in front of the warm beige seamless backdrop, both topless, their discarded studio clothing in a heap beside them. <Subject 1> leans back on both palms, elbows bent, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs, leans forward, and presses her mouth and tongue against the bare, wet vulva of <Subject 1>, her thumbs spreading the outer lips apart while her tongue works in slow, continuous strokes. <Subject 1>'s hips rise in small weighted thrusts toward the contact, her stomach tensing, her fingers pressing into the floor, her thighs trembling and her toes curling. Wet gloss shows at the point of contact, and thin strands of blonde hair stick to her inner thigh. The camera holds a stable focal plane on the two bodies with the backdrop softly blurred, drifting slightly lower to keep the contact in frame without cutting, small amplitude, slow speed, no cuts. <Subject 1>'s hands leave the floor, grip the shoulders of <Subject 2>, and press her closer; her chest heaves and her mouth opens in a long moan. Both women keep their eyes open at times and glance toward the camera, expressions dazed and pleased. The clip ends with <Subject 2> still between the thighs of <Subject 1>, head down, and the hips of <Subject 1> lifting into the contact.
 6| 
 7| overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the floor as weight shifts, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.
 8| 
 9| non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

<details><summary>verbatim full prompt - ali147_pool_hc_r1_s51130001.c0 (4210 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 24, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
<Picture 1> is the start still of <Subject 1> and <Subject 2> seated close together in a warm photo studio.
<Picture 2> is the multi-view reference sheet of <Subject 1> alone.
<Picture 3> is the multi-view reference sheet of <Subject 2> alone.

summary:
[reference generation] The target video is the first 5 seconds of a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm photo studio. The shot uses <Picture 1> for the scene and <Picture 2> and <Picture 3> only as appearance guidance for the two women while freely composing the environment, wardrobe and camera. The two women lean in, kiss with open mouths, and pull each other's studio clothing off, ending topless and close. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 2> keeps her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
<Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 3> keeps her identity, long dark hair, soft feminine figure, wide hips and warm skin; kneeling and touching are actions, not a change of identity.
Their studio clothing from <Picture 1> is removed during the shot and lies in a heap on the dark studio floor for the rest of the clip.

detailed_description:
The target video is a realistic, warmly lit studio scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen, realistic natural body proportions, and dynamic video with fluid natural motions.
[Shot 1] The shot opens on <Subject 1>, the blonde adult woman of <Picture 2>, and <Subject 2>, the dark-haired adult woman of <Picture 3>, seated close together on a dark studio floor in front of a warm beige seamless backdrop lit by a soft key light from the left. They wear the studio outfits of <Picture 1>. The camera starts in a medium two-shot and moves in slowly and steadily, low amplitude, no cuts. They lean in and kiss with open mouths, tongues touching, faces close, eyes half closed. <Subject 1>'s hands pull the shirt of <Subject 2> up and over her head while <Subject 2> unfastens the front of <Subject 1>'s top. The garments slide off shoulders and arms with visible friction and drop to the floor. Both women end the shot topless: <Subject 1> with full natural breasts of soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer, darker-skinned breasts that sway as she moves. Their faces stay close, foreheads touching, breathing heavy, chests rising and falling. Body contact is continuous and weighted: hips shifting, knees parting, thighs brushing, one hand flat on the floor for balance. The camera keeps a stable focal plane on the two bodies with the backdrop softly blurred. The shot ends with the two women still kissing, naked from the waist up, the discarded clothing in a heap beside them.

overall_soundscape:
A quiet studio room tone with a low, soft air-handling hum. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, fabric sliding off skin and landing softly on the floor, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no counting, no crowd, no narration; the room stays otherwise silent.

non_diegetic_music:
N/A
```

</details>

<details><summary>verbatim full prompt - ali147_pool_hc_r1_s51130001.c1 (3443 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous studio moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the first 5 seconds are kept exactly, <Subject 1> exactly as the sheet in <Picture 1> and <Subject 2> exactly as the sheet in <Picture 2>: <Subject 1> with long blonde hair, slim natural figure and full natural bare breasts; <Subject 2> with long dark hair, soft feminine figure, wide hips and bare breasts. They are on the dark studio floor in front of the warm beige seamless backdrop, both topless, their discarded studio clothing in a heap beside them. <Subject 1> leans back on both palms, elbows bent, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs, leans forward, and presses her mouth and tongue against the bare, wet vulva of <Subject 1>, her thumbs spreading the outer lips apart while her tongue works in slow, continuous strokes. <Subject 1>'s hips rise in small weighted thrusts toward the contact, her stomach tensing, her fingers pressing into the floor, her thighs trembling and her toes curling. Wet gloss shows at the point of contact, and thin strands of blonde hair stick to her inner thigh. The camera holds a stable focal plane on the two bodies with the backdrop softly blurred, drifting slightly lower to keep the contact in frame without cutting, small amplitude, slow speed, no cuts. <Subject 1>'s hands leave the floor, grip the shoulders of <Subject 2>, and press her closer; her chest heaves and her mouth opens in a long moan. Both women keep their eyes open at times and glance toward the camera, expressions dazed and pleased. The clip ends with <Subject 2> still between the thighs of <Subject 1>, head down, and the hips of <Subject 1> lifting into the contact.

overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the floor as weight shifts, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.

non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

</details>

### Face box per woman over 5 evenly spaced frames (SCRFD-10G thr 0.4 at 640x640, frame 1344x768 = 1.032 Mpx)

| frame | n_faces | woman | box px (WxH) | face area px2 | % of frame | arcface cos to her sheet anchor |
|---|---|---|---|---|---|---|
| 0 | 2 | w1 | 89x148 | 13284 | 1.29% | 0.268 |
| 0 | 2 | w2 | 89x148 | 13284 | 1.29% | 0.204 |
| 40 | 2 | w1 | 101x184 | 18775 | 1.82% | 0.074 |
| 40 | 2 | w2 | 113x177 | 20078 | 1.95% | 0.175 |
| 80 | 2 | w1 | 100x192 | 19290 | 1.87% | 0.232 |
| 80 | 2 | w2 | 100x192 | 19290 | 1.87% | 0.087 |
| 120 | 2 | w1 | 95x182 | 17486 | 1.69% | 0.133 |
| 120 | 2 | w2 | 112x176 | 19881 | 1.93% | 0.096 |
| 160 | 2 | w1 | 114x176 | 20240 | 1.96% | 0.556 |
| 160 | 2 | w2 | 114x176 | 20240 | 1.96% | 0.324 |

## ali147_pool_hc_r2_s51130002  (r2, 1344x768)

| setting | value |
|---|---|
| model (UNETLoader) | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors |
| clip | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| video vae / audio vae | minimax_h3_video_vae_int8_convrot.safetensors / minimax_h3_audio_vae_fp32.safetensors |
| c0 class_type | MiniMaxH3ReferenceToVideo |
| c0 length (frames) | 124 |
| c1 class_type | MiniMaxH3ReferenceToVideo |
| c1 length | ['win1', 1] |
| continuation window | {"extension_frames": 119, "overlap_frames": 22} |
| total frames (c0 + extension) | 124 + 119 |
| width x height x fps | 1344x768x24 |
| steps / scheduler / sampler / denoise | 10 / simple / euler / 1.0 |
| shift_video / shift_audio | 10.0 / 3.0 |
| noise_seed | 51130002 |
| ref_image_size (c0 / c1) | max / max |
| save prefix | community/ali147_pool_hc_r2_s51130002/ali147_pool_hc_r2_s51130002 |

### Reference slots (<Picture N> -> LoadImage -> file) as wired in the graph

| chunk | slot | LoadImage node | file on disk | file px | aspect | sha256(12) | ref_image_size | ref canvas px | ref Mpx | faces in ref | biggest face px | face % of ref |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c0 | <Picture 1> | `img` (LoadImage) | `community/hc/HC2_Two_women_in_passionate_embrace.jpg` | 1376x768 | 1.792 | 530f056f4eb2 | max | 1376x768 | 1.06 | 2 | 133x203 | 2.58% |
| c0 | <Picture 2> | `sheet` (LoadImage) | `community/hc/HC2_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 0daac8df30bb | max | 1152x2016 | 2.32 | 4 | 188x266 | 2.16% |
| c0 | <Picture 3> | `sheet2` (Load Image (HC2_w2 darkhair sheet)) | `community/hc/HC2_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 3c9701692eb0 | max | 1152x2016 | 2.32 | 6 | 227x319 | 3.13% |
| c1 | <Picture 1> | `sheet` (LoadImage) | `community/hc/HC2_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 0daac8df30bb | max | 1152x2016 | 2.32 | 4 | 188x266 | 2.16% |
| c1 | <Picture 2> | `sheet2` (Load Image (HC2_w2 darkhair sheet)) | `community/hc/HC2_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 3c9701692eb0 | max | 1152x2016 | 2.32 | 6 | 227x319 | 3.13% |

### Prompt nodes (every text node in the graph)

| chunk | class_type | chars | blocks present (in order) | subject binding lines |
|---|---|---|---|---|
| c0 | MiniMaxH3ReferenceToVideo | 4573 | subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music | 9 |
| c1 | MiniMaxH3ReferenceToVideo | 3780 | subject_definitions, integrated_multimodal_description, overall_soundscape, non_diegetic_music | 3 |

#### ali147_pool_hc_r2_s51130002.c0 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 26, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
 4| <Picture 1> is the start still of <Subject 1> and <Subject 2> locked in a close passionate embrace.
 5| <Picture 2> is the multi-view reference sheet of <Subject 1> alone.
 6| <Picture 3> is the multi-view reference sheet of <Subject 2> alone.
 7| 
 8| summary:
 9| [reference generation] The target video is the first 5 seconds of a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm bedroom at dusk. The shot uses <Picture 1> for the scene and <Picture 2> and <Picture 3> only as appearance guidance for the two women while freely composing the room, wardrobe and camera. The two women stand locked in an embrace, kiss with open mouths, and pull each other's clothing off, ending naked and falling back onto the bed. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.
10| 
11| retention_analysis:
12| <Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 2> keeps her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
13| <Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 3> keeps her identity, long dark hair, soft feminine figure, wide hips and warm skin; embracing and undressing are actions, not a change of identity.
14| Their clothing from <Picture 1> is pulled off during the shot and lands on the bedroom rug, and both women are naked for the rest of the clip.
15| 
16| detailed_description:
17| The target video is a realistic, warmly lit bedroom scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
18| [Shot 1] The shot opens on <Subject 1>, the blonde adult woman of <Picture 2>, and <Subject 2>, the dark-haired adult woman of <Picture 3>, standing locked chest to chest in a passionate embrace beside a rumpled bed in a bedroom lit by warm dusk light through a half-curtained window, a soft lamp glow filling the shadows. They wear the everyday clothing of <Picture 1>. The camera starts in a medium two-shot at chest height and drifts in slowly and steadily, low amplitude, no cuts. They kiss hard with open mouths, tongues moving, faces close, eyes half closed, hands roaming over each other's back and breasts through the fabric. <Subject 2> shrugs her own top off her shoulders and pulls the shirt of <Subject 1> up and over her head while <Subject 1> unfastens the front of <Subject 2>'s top. The garments slide off shoulders, breasts and hips with visible friction and drop to the rug. Both women end the shot naked: <Subject 1> with full natural bare breasts of soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer bare breasts, a natural waist and wide hips. Skin meets skin as they press together, hips shifting, knees parting, thighs brushing, one hand flat on the bed for balance. The camera keeps a stable focal plane on the two bodies with the window light raking across their skin and the room softly blurred behind them. The shot ends with the two naked women sinking down onto the edge of the bed, still kissing, foreheads touching, chests rising and falling, the discarded clothing on the rug.
19| 
20| overall_soundscape:
21| A quiet bedroom room tone with a low distant city hum and soft traffic outside the window, plus a faint bedside lamp buzz. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, fabric sliding off skin and landing softly on the rug, bedsprings creaking and bedding rustling as weight settles, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no counting, no crowd, no narration; the room stays otherwise silent.
22| 
23| non_diegetic_music:
24| N/A
```

#### ali147_pool_hc_r2_s51130002.c1 subject/reference binding, line by line (verbatim from the graph)

```text
 1| subject_definitions:
 2| <Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture.
 3| <Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin.
 4| 
 5| integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous bedroom moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the first 5 seconds are kept exactly, <Subject 1> exactly as the sheet in <Picture 1> and <Subject 2> exactly as the sheet in <Picture 2>: <Subject 1> with long blonde hair, slim natural figure and full natural bare breasts; <Subject 2> with long dark hair, soft feminine figure, wide hips and bare breasts. They are on the rumpled bed in the warm dusk bedroom, both naked, their discarded clothing on the rug beside the bed. <Subject 1> lies back against the pillows, propped on both elbows, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs and presses her own naked groin down against the bare, wet vulva of <Subject 1>, sliding her hips in slow, continuous, weighted strokes, her thumbs spreading the outer lips apart as she grinds. <Subject 1>'s hips rise in small weighted thrusts up into the contact, her stomach tensing, her fingers pressing into the mattress, her thighs trembling around the hips of <Subject 2> and her toes curling. <Subject 2> hooks one arm under the knees of <Subject 1> to pull her closer and keeps the rhythm, her own breasts sliding along the stomach of <Subject 1>. Wet gloss shows at the point of contact, skin slides on skin, thin strands of blonde hair stick to her inner thigh, and the bedding creases and shifts under their weight. The camera holds a stable focal plane on the two bodies and the point of contact, drifting slightly lower to keep it in frame without cutting, small amplitude, slow speed, no cuts. <Subject 1>'s hands leave the mattress, grip the shoulders of <Subject 2>, and press her harder against the contact; her chest heaves and her mouth opens in a long moan. Both women keep their eyes open at times and glance toward the camera, expressions dazed and pleased. The clip ends with <Subject 2> still pressed between the thighs of <Subject 1>, hips moving, and the hips of <Subject 1> lifting into the contact.
 6| 
 7| overall_soundscape: Soft bedroom room tone with a low distant city hum, soft traffic outside the window and a faint bedside lamp buzz. Intimate close sound: skin sliding on skin, repeated soft wet sliding sounds at the point of contact, soft flesh thudding and skin of the bodies clapping together as hips grind and rise into contact, a slick wet skin squeak on the mattress as weight shifts, bedsprings creaking and bedding rustling, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.
 8| 
 9| non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

<details><summary>verbatim full prompt - ali147_pool_hc_r2_s51130002.c0 (4573 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 26, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin.
<Picture 1> is the start still of <Subject 1> and <Subject 2> locked in a close passionate embrace.
<Picture 2> is the multi-view reference sheet of <Subject 1> alone.
<Picture 3> is the multi-view reference sheet of <Subject 2> alone.

summary:
[reference generation] The target video is the first 5 seconds of a 10-second single continuous shot of <Subject 1> and <Subject 2> in a warm bedroom at dusk. The shot uses <Picture 1> for the scene and <Picture 2> and <Picture 3> only as appearance guidance for the two women while freely composing the room, wardrobe and camera. The two women stand locked in an embrace, kiss with open mouths, and pull each other's clothing off, ending naked and falling back onto the bed. Explicit adult content, two consenting fictional adults. dynamic video, fluid natural motions.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - <Picture 2> keeps her identity, long blonde hair, slim natural figure, full natural breasts and lightly tanned skin; undressing and being touched are actions, not a change of identity.
<Subject 2> (appears in [Shot 1]): fully_preserved - <Picture 3> keeps her identity, long dark hair, soft feminine figure, wide hips and warm skin; embracing and undressing are actions, not a change of identity.
Their clothing from <Picture 1> is pulled off during the shot and lands on the bedroom rug, and both women are naked for the rest of the clip.

detailed_description:
The target video is a realistic, warmly lit bedroom scene, photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen where it is damp, realistic natural body proportions, and dynamic video with fluid natural motions.
[Shot 1] The shot opens on <Subject 1>, the blonde adult woman of <Picture 2>, and <Subject 2>, the dark-haired adult woman of <Picture 3>, standing locked chest to chest in a passionate embrace beside a rumpled bed in a bedroom lit by warm dusk light through a half-curtained window, a soft lamp glow filling the shadows. They wear the everyday clothing of <Picture 1>. The camera starts in a medium two-shot at chest height and drifts in slowly and steadily, low amplitude, no cuts. They kiss hard with open mouths, tongues moving, faces close, eyes half closed, hands roaming over each other's back and breasts through the fabric. <Subject 2> shrugs her own top off her shoulders and pulls the shirt of <Subject 1> up and over her head while <Subject 1> unfastens the front of <Subject 2>'s top. The garments slide off shoulders, breasts and hips with visible friction and drop to the rug. Both women end the shot naked: <Subject 1> with full natural bare breasts of soft realistic weight, smooth skin and round light-brown areolae with natural nipples; <Subject 2> with softer bare breasts, a natural waist and wide hips. Skin meets skin as they press together, hips shifting, knees parting, thighs brushing, one hand flat on the bed for balance. The camera keeps a stable focal plane on the two bodies with the window light raking across their skin and the room softly blurred behind them. The shot ends with the two naked women sinking down onto the edge of the bed, still kissing, foreheads touching, chests rising and falling, the discarded clothing on the rug.

overall_soundscape:
A quiet bedroom room tone with a low distant city hum and soft traffic outside the window, plus a faint bedside lamp buzz. Close, muffled intimate sound: wet kissing and tongue sounds, soft flesh thudding and skin of the bodies clapping together, fabric sliding off skin and landing softly on the rug, bedsprings creaking and bedding rustling as weight settles, deep breathing, and low moaning and gasping from both women, one low and one higher. No dialogue, no announcer, no counting, no crowd, no narration; the room stays otherwise silent.

non_diegetic_music:
N/A
```

</details>

<details><summary>verbatim full prompt - ali147_pool_hc_r2_s51130002.c1 (3780 chars)</summary>

```text
subject_definitions:
<Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture.
<Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium two-shot continues from the previous bedroom moment as one unbroken take. Photorealistic skin and anatomy: natural matte skin with visible pores, fine vellus hair and only a soft natural sheen of wetness on the inner thighs, realistic natural body proportions, and dynamic video, fluid natural motions. The same two fictional adult women established in the first 5 seconds are kept exactly, <Subject 1> exactly as the sheet in <Picture 1> and <Subject 2> exactly as the sheet in <Picture 2>: <Subject 1> with long blonde hair, slim natural figure and full natural bare breasts; <Subject 2> with long dark hair, soft feminine figure, wide hips and bare breasts. They are on the rumpled bed in the warm dusk bedroom, both naked, their discarded clothing on the rug beside the bed. <Subject 1> lies back against the pillows, propped on both elbows, head tipped back, and slowly spreads her thighs. <Subject 2> moves onto her knees between those thighs and presses her own naked groin down against the bare, wet vulva of <Subject 1>, sliding her hips in slow, continuous, weighted strokes, her thumbs spreading the outer lips apart as she grinds. <Subject 1>'s hips rise in small weighted thrusts up into the contact, her stomach tensing, her fingers pressing into the mattress, her thighs trembling around the hips of <Subject 2> and her toes curling. <Subject 2> hooks one arm under the knees of <Subject 1> to pull her closer and keeps the rhythm, her own breasts sliding along the stomach of <Subject 1>. Wet gloss shows at the point of contact, skin slides on skin, thin strands of blonde hair stick to her inner thigh, and the bedding creases and shifts under their weight. The camera holds a stable focal plane on the two bodies and the point of contact, drifting slightly lower to keep it in frame without cutting, small amplitude, slow speed, no cuts. <Subject 1>'s hands leave the mattress, grip the shoulders of <Subject 2>, and press her harder against the contact; her chest heaves and her mouth opens in a long moan. Both women keep their eyes open at times and glance toward the camera, expressions dazed and pleased. The clip ends with <Subject 2> still pressed between the thighs of <Subject 1>, hips moving, and the hips of <Subject 1> lifting into the contact.

overall_soundscape: Soft bedroom room tone with a low distant city hum, soft traffic outside the window and a faint bedside lamp buzz. Intimate close sound: skin sliding on skin, repeated soft wet sliding sounds at the point of contact, soft flesh thudding and skin of the bodies clapping together as hips grind and rise into contact, a slick wet skin squeak on the mattress as weight shifts, bedsprings creaking and bedding rustling, sharp inhales, heavy breathing, and rising moans and gasps from both women, one low and one higher. No dialogue, no counting, no announcer, no crowd noise, nothing in the background talking.

non_diegetic_music: A very low sustained synth pad at a slow tempo with a soft sub-bass pulse, sparse and quiet, staying under the body sounds and fading slightly at the end.
```

</details>

### Face box per woman over 5 evenly spaced frames (SCRFD-10G thr 0.4 at 640x640, frame 1344x768 = 1.032 Mpx)

| frame | n_faces | woman | box px (WxH) | face area px2 | % of frame | arcface cos to her sheet anchor |
|---|---|---|---|---|---|---|
| 0 | 2 | w1 | 98x159 | 15711 | 1.52% | 0.138 |
| 0 | 2 | w2 | 98x159 | 15711 | 1.52% | 0.280 |
| 40 | 2 | w1 | 147x253 | 37317 | 3.62% | 0.332 |
| 40 | 2 | w2 | 147x253 | 37317 | 3.62% | 0.256 |
| 80 | 0 | - | - | - | - | - |
| 120 | 2 | w1 | 105x153 | 16207 | 1.57% | 0.192 |
| 120 | 2 | w2 | 96x162 | 15723 | 1.52% | 0.286 |
| 160 | 2 | w1 | 111x163 | 18126 | 1.76% | 0.425 |
| 160 | 2 | w2 | 111x163 | 18126 | 1.76% | 0.343 |

## Start stills (the approved picks, as placed in ComfyUI\input\community\hc)

| pick (pair) | file | px | aspect | sha256(12) | faces | per-face box px | face area | % of frame | label | cos to that sheet |
|---|---|---|---|---|---|---|---|---|---|---|
| HC1_Two_women_in_studio_editorial.jpg (HC1) | `HC1_Two_women_in_studio_editorial.jpg` | 1376x768 | 1.792 | dd9ed0cb69e4 | 2 | 175x150 | 26271 | 2.49% | w1 | 0.431 |
| HC1_Two_women_in_studio_editorial.jpg (HC1) | `HC1_Two_women_in_studio_editorial.jpg` | 1376x768 | 1.792 | dd9ed0cb69e4 | 2 | 126x162 | 20542 | 1.94% | w2 | 0.369 |
| HC2_Two_women_in_passionate_embrace.jpg (HC2) | `HC2_Two_women_in_passionate_embrace.jpg` | 1376x768 | 1.792 | 530f056f4eb2 | 2 | 133x203 | 27289 | 2.58% | w2 | 0.240 |
| HC2_Two_women_in_passionate_embrace.jpg (HC2) | `HC2_Two_women_in_passionate_embrace.jpg` | 1376x768 | 1.792 | 530f056f4eb2 | 2 | 186x144 | 26976 | 2.55% | w1 | 0.217 |

## Reference sheets (ComfyUI\output\community\hc_sheets, all 10 as built by R3)

| sheet | px | aspect | Mpx | sha256(12) | faces | face boxes px (WxH, y-band) | biggest face % of sheet | panel reading |
|---|---|---|---|---|---|---|---|---|
| `HC1_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 2.32 | 022cd65e0c33 | 2 | 212x310@y119, 102x153@y668 | 2.84% | faces in y-third(s) [0] of 3 |
| `HC1_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 2.32 | 8336fa03aab3 | 4 | 247x349@y152, 185x268@y152, 101x145@y709, 62x136@y741 | 3.73% | faces in y-third(s) [0, 1] of 3 |
| `HC2_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 2.32 | 0daac8df30bb | 4 | 188x266@y130, 110x190@y102, 97x139@y606, 70x131@y655 | 2.16% | faces in y-third(s) [0] of 3 |
| `HC2_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 2.32 | 3c9701692eb0 | 6 | 227x319@y138, 78x103@y706, 65x102@y1021, 55x103@y725, 51x106@y1087, 54x98@y1029 | 3.13% | faces in y-third(s) [0, 1] of 3 |
| `HC3_w1_left_00001_.png` | 1152x2016 | 0.571 | 2.32 | 92e67db3a2e4 | 4 | 179x265@y133, 75x127@y726, 74x108@y1052, 58x104@y81 | 2.06% | faces in y-third(s) [0, 1] of 3 |
| `HC3_w2_right_00001_.png` | 1152x2016 | 0.571 | 2.32 | fbaf562317d0 | 4 | 194x282@y134, 179x260@y134, 82x120@y684, 67x113@y764 | 2.37% | faces in y-third(s) [0, 1] of 3 |
| `HC4_00001_.png` | 1152x2016 | 0.571 | 2.32 | ee2459d1f021 | 3 | 215x297@y141, 88x126@y868, 75x117@y891 | 2.76% | faces in y-third(s) [0, 1] of 3 |
| `HC5_00001_.png` | 1152x2016 | 0.571 | 2.32 | 06127d1f970c | 3 | 206x293@y125, 103x152@y675, 83x151@y679 | 2.62% | faces in y-third(s) [0, 1] of 3 |
| `HC6_w1_blonde_00001_.png` | 1152x2016 | 0.571 | 2.32 | abd37c7953c6 | 4 | 222x324@y136, 95x158@y243, 95x140@y638, 56x88@y705 | 3.11% | faces in y-third(s) [0, 1] of 3 |
| `HC6_w2_darkhair_00001_.png` | 1152x2016 | 0.571 | 2.32 | d6ed95d56a11 | 4 | 208x287@y136, 53x108@y124, 53x99@y1092, 44x103@y1060 | 2.58% | faces in y-third(s) [0, 1] of 3 |

## Slot/size summary (the machine part of the comparison)

| clip | c0 refs (kind) | c1 refs (kind) | c0 ref_image_size | c1 ref_image_size | pick in c1 refs? | sheet in c1 refs? | c0 ref Mpx total | c1 ref Mpx total | target canvas Mpx |
|---|---|---|---|---|---|---|---|---|---|
| c1_s51100001 | 1 ['pick'] | 0 [] | match | n/a | False | False | 1.03 | 0.00 | 1.03 |
| c2_s51100002 | 1 ['pick'] | 0 [] | match | n/a | False | False | 1.03 | 0.00 | 1.03 |
| r1_s51130001 | 3 ['pick', 'sheet', 'sheet'] | 2 ['sheet', 'sheet'] | max | max | False | True | 5.70 | 4.64 | 1.03 |
| r2_s51130002 | 3 ['pick', 'sheet', 'sheet'] | 2 ['sheet', 'sheet'] | max | max | False | True | 5.70 | 4.64 | 1.03 |


---

## ANALYSIS (written part, R4F pass 2 - 2026-10-23)

Author: Forge Ralph (ALI-163 R4F, widened scope). All numbers above are machine-measured by `C:\AI\community\notes\ali163_hc_r4f_audit.py`; this block is the reading of them. Community sources read (local, saved): `C:\AI\community\notes\web\ext_readme.md` (MiniMax-H3-ComfyUI-Extender README, https://github.com/chaos20044/MiniMax-H3-ComfyUI-Extender - `subject_definitions` at the start of every clip prompt, lines 379-406) and `C:\AI\community\notes\web\comfy_h3_tutorial.html` (https://docs.comfy.org/tutorials/video/minimax-minimax-h3-alpha, Ref2VA = "Lock identity, style, motion, camera, or voice from references"). Implementation read: `ComfyUI\custom_nodes\ComfyUI_MiniMax_H3_Extender\extender.py` (installed local copy of the community node) lines 110-116 and 2267-2310.

### A. Prompt texts: listing (verbatim above, complete)

Every text node of all four graphs is quoted verbatim in the `<details>` blocks above - 8 prompts (c0 + continuation chunk of each of c1, c2, r1, r2), with char counts in each clip's *Prompt nodes* table:

- `c1.c0` - 4497 chars, 21 lines, opens with `subject_definitions:...`, blocks: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music
- `c1.c1` - 2794 chars, 5 lines, opens with `integrated_multimodal_description: [Shot 1] Live...`, blocks: integrated_multimodal_description, overall_soundscape, non_diegetic_music
- `c2.c0` - 4777 chars, 21 lines, opens with `subject_definitions:...`, blocks: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music
- `c2.c1` - 3227 chars, 5 lines, opens with `integrated_multimodal_description: [Shot 1] Live...`, blocks: integrated_multimodal_description, overall_soundscape, non_diegetic_music
- `r1.c0` - 4210 chars, 24 lines, opens with `subject_definitions:...`, blocks: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music
- `r1.c1` - 3443 chars, 9 lines, opens with `subject_definitions:...`, blocks: subject_definitions, integrated_multimodal_description, overall_soundscape, non_diegetic_music
- `r2.c0` - 4573 chars, 24 lines, opens with `subject_definitions:...`, blocks: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music
- `r2.c1` - 3780 chars, 9 lines, opens with `subject_definitions:...`, blocks: subject_definitions, integrated_multimodal_description, overall_soundscape, non_diegetic_music

Source of truth for the wording: `C:\AI\community\notes\ali163_hc_r5_build.py::prompts(pair)` (lines 80-145). It emits the **v1** style (one start-still ref, hair-colour binding) for HC3/HC4/HC5/HC6 and the **v2** style (pick + 2 per-woman sheets, sheet-first binding) for HC1/HC2. c1/c2 (the 120 s clips, the only approved pair) carry the v1 shape; r1/r2 carry v2. R6-R9 are HC3-HC6, i.e. they inherit the **v1** shape with the R5 sheet wiring bolted on (`refs_json` 3 slots, `ref_image_size=max`, `continuation_window` on node `win1`, length 243).

### B. Line-by-line comparison of the two prompt shapes

Identity binding, c1/c2 (v1, verbatim, c1.c0 lines 2-3):

```text
<Subject 1> is the adult woman with long blonde hair shown in <Picture 1>, a fictional adult aged 25, ...
<Subject 2> is the adult woman with long dark hair shown in <Picture 1>, a fictional adult aged 24, ...
```

Identity binding, r1/r2 (v2, verbatim, r1.c0 lines 2-6):

```text
<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, ...
<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, ...
<Picture 1> is the start still of <Subject 1> and <Subject 2> seated close together in a warm photo studio.
<Picture 2> is the multi-view reference sheet of <Subject 1> alone.
<Picture 3> is the multi-view reference sheet of <Subject 2> alone.
```

Continuation chunk of r1/r2 (v2, verbatim, r1.c1 lines 2-4):

```text
<Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 1>, a fictional adult aged 25, ...
<Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 2>, ...
<Picture 1> is the multi-view reference sheet of <Subject 1> alone.
```

Mechanical differences, in the order they matter:

1. **Who is in charge of identity in the second chunk.** c1/c2 continue with `MiniMaxH3ImageToVideo` and **zero** image references (c1.c1 2794 chars, c2.c1 3227 chars, 0 binding lines, no `subject_definitions:` block): identity is carried by the last generated frame. r1/r2 continue with `MiniMaxH3ReferenceToVideo` whose only references are the **two Klein sheets** - the approved start still (the only real evidence of the two faces) is **never** a reference in chunk 2 (`pick in c1 refs? = False`, `sheet in c1 refs? = True`, slot/size summary). So from frame ~120 on, r1/r2 are drawn from the sheet faces.
2. **Reference pixel weight.** `ref_image_size` is `max` in both r1/r2 chunks, and the node's `max` rule is `scale = min(1, 2048/min(w,h))` (`extender.py:2274`, `REF_IMAGE_SHORT_EDGE = 2048` at `extender.py:113`), i.e. a 1152x2016 sheet is **not** downscaled at all: each sheet enters the VAE at 2.32 Mpx. r1/r2 chunk 1 = 5.70 Mpx of reference, chunk 2 = 4.64 Mpx, for a 1.03 Mpx (1344x768) canvas = 5.5x / 4.5x. c1/c2 = 1.03 Mpx in chunk 1 (`match` = cap at canvas pixels) and 0 Mpx in chunk 2.
3. **Aspect mismatch.** The reference set mixes 16:9 (1376x768 pick, 1.792) with 9:16 (1152x2016 sheets, 0.571) in one slot list, and the 9:16 slots are the big ones. The 16:9 start frame - the only thing that matches the 1344x768 target - is 18% of the reference pixels in chunk 1 and 0% in chunk 2.
4. **Face density per slot.** A pick slot holds exactly 2 faces (175x150 + 126x162 for HC1; 133x203 + 186x144 for HC2, 1.94-2.58% of the frame). A sheet slot holds 2-6 faces (multi-view panels: 188x266 to 247x349 for the biggest panel, 44x99 to 110x190 for the profile/back panels, all in the top two thirds of the 2016 px height). The model must pick which panel is the identity and which is a pose, from a collage with up to 6 faces in it.
5. **Anchors.** v1 names the woman by hair colour inside the same picture the video starts from ("the adult woman with long blonde hair shown in <Picture 1>"). v2 names her **sheet-first** ("the adult woman shown in the multi-view reference sheet in <Picture 2>") and demotes the start still to a scene/wardrobe reference ("<Picture 1> is the start still of ..."). Neither shape uses a left/right spatial anchor: `left woman` / `right woman` occur in 0 of the 8 submitted prompt strings and `RIGHT` in 0 of 8 (the 2 `LEFT` hits are the lowercase word "left" in prose such as "a soft key light from the left"); the R5 builder's v1 template for HC3-HC6 does use "the adult woman on the LEFT side of <Picture 1>", which is why R6-R9 need the anchor restored.
6. **Face language.** No prompt in any of the four clips contains a face crop / close-up / bust / headshot / portrait / macro / shallow-depth instruction (see the word table below: 0 hits for `close-up`, `crop`, `bust`, `headshot`, `portrait`, `macro`, `shallow depth of field`, `bokeh`, `negative prompt`, `4K`, `ultra`, `hyper`). `face` occurs in only 4 of the 8 prompt strings and where it occurs it is action prose (r1: "faces close", "faces stay close, foreheads touching"); the binding lines of v1 and v2 never use the word, and `facial` occurs in 0 of 8 - there is no facial-identity word in the binding at all. Skin-quality language is `natural matte skin` / `visible pores` (8 of 8) inside `detailed_description:`; `detailed skin` 0 of 8.
7. **Length.** r1/r2 = 124 frames in c0 + `win1.extension_frames` 119 (overlap 22) = 243 frames = 10.1 s of video. c1/c2 = 243 + 238 = 481 frames = 20.0 s. All four are 1344x768 at 24 fps, 10 steps, `simple`, `euler`, `denoise 1.0` on **both** chunks (`s0_sched` and `s1_sched`), `shift_video 10.0`, `shift_audio 3.0`. The R4G spec keeps that sampling and the 243 f (124 + 119) shape for R6-R9 - length is not a face fix, it is the batch shape R1/R2 chose.

### C. Reference images as placed (tables above, read out)

- Picks: `HC1_Two_women_in_studio_editorial.jpg` 1376x768, 1.792, sha256 `dd9ed0cb69e4`; `HC2_Two_women_in_passionate_embrace.jpg` 1376x768, 1.792, sha256 `530f056f4eb2` - both in `ComfyUI\input\community\hc\`, both wired as `<Picture 1>` of chunk 1 in all four clips.
- Sheets used by r1/r2: `HC1_w1_blonde_00001_.png` `022cd65e0c33`, `HC1_w2_darkhair_00001_.png` `8336fa03aab3`, `HC2_w1_blonde_00001_.png` `0daac8df30bb`, `HC2_w2_darkhair_00001_.png` `3c9701692eb0` - all 1152x2016, 0.571, 2.32 Mpx, all in the **same** `input\community\hc` folder (the LoadImage strings resolve, no ` [output]` tag needed).
- All 10 sheets R3 built (HC1 w1/w2, HC2 w1/w2, HC3 w1/w2, HC4, HC5, HC6 w1/w2) are 1152x2016 portrait multi-view collages; per-woman sheets exist only for HC1, HC2 and HC6; HC4, HC5 are single sheets for the pair and HC3 has 2 per-woman sheets; so "one sheet per woman" is true only for 5 of the 6 pairs.
- Face quality of those sheets, measured: sheet-to-sheet cosine inside a pair is 0.30-0.57 and pick-to-own-sheet is 0.22-0.47 (R4F pass 1 table T1, same detector). The two per-woman sheets of one pair are therefore as close to each other in face space as a sheet is to the real face it was built from: the Klein 9B edit flattened the two women toward one generic face, HC2 worst (pick->sheet 0.217-0.240).

### D. Face box size per woman, per clip (measured, 5 frames each)

| clip | faces per sampled frame | face box px (W x H) | face area px2 | % of 1344x768 frame | video face vs her sheet anchor (cos) |
|---|---|---|---|---|---|
| c1 (no sheets, 120 s) | 2 (one frame 1) | 104x131 - 191x166 | 13,803 - 33,340 | 1.34 - 3.23% | 0.065 - 0.350 |
| c2 (no sheets, 120 s) | 2 (one frame 1) | 90x123 - 170x199 | 11,215 - 34,095 | 1.09 - 3.30% | 0.078 - 0.283 |
| r1 (sheets, 60 s) | 2 | 89x148 - 114x192 | 13,284 - 20,240 | 1.29 - 1.96% | 0.074 - 0.556 |
| r2 (sheets, 60 s) | 2 (one frame 0) | 96x153 - 147x253 | 15,711 - 37,317 | 1.52 - 3.62% | 0.138 - 0.425 |

Reading: every clip renders the two faces at 90-190 px wide, i.e. 1.1-3.6% of the frame, and **the sheet-fed clips do not render bigger faces than the sheet-free clips** - r1 is the smallest of the four (89-114 px wide). At 1344x768 a 100 px face is ~70 px at 1080p, which is the whole reason the output reads as "no facial detail". In 6 of the 10 sampled r1/r2 frames the best-matching face for woman 1 and for woman 2 is the *same* detection, so the second face in frame scores lower against both anchors: the pair is not separable per woman in the video.

### E. Prompt-language count (all 8 submitted prompt strings, case-insensitive substring count)

| term | prompts containing it (of 8) |
|---|---|
| `face` | 4 |
| `facial` | 0 |
| `close-up` | 0 |
| `close up` | 0 |
| `crop` | 0 |
| `bust` | 0 |
| `headshot` | 0 |
| `portrait` | 0 |
| `macro` | 0 |
| `shallow depth of field` | 0 |
| `bokeh` | 0 |
| `negative prompt` | 0 |
| `4K` | 0 |
| `8K` | 0 |
| `ultra` | 0 |
| `hyper8n` | 0 |
| `hyper` | 0 |
| `detailed skin` | 0 |
| `natural matte skin` | 8 |
| `visible pores` | 8 |
| `long blonde hair` | 8 |
| `long dark hair` | 8 |
| `LEFT` | 2 |
| `RIGHT` | 0 |
| `left woman` | 0 |
| `right woman` | 0 |
| `on the left` | 0 |
| `on the right` | 0 |
| `multi-view reference sheet` | 4 |
| `identity` | 4 |
| `same woman` | 0 |
| `Picture 1` | 6 |
| `Picture 2` | 4 |
| `Picture 3` | 2 |

`denoise`/`shift` are graph settings, not prompt words: all four clips, both chunks: `BasicScheduler` `steps 10`, `scheduler simple`, `denoise 1.0`, `euler`, shift `shift_video 10.0` / `shift_audio 3.0` (the H3 distill path, and the reason the community README puts identity language in `subject_definitions:` at the top of every clip prompt: with `denoise 1.0` the prompt is the only lever). No prompt in the batch contains a negative-prompt block (H3 prompt fields are positive-only).

### F. Five-line summary (plain language, exactly five lines)

1. The redo let the reference sheets speak for identity: the second chunk of r1/r2 receives **only** the two 9:16 multi-view sheets, the approved start still is never a reference there, and those sheet faces measure cosine 0.22-0.47 from the real faces in the still, so the model faithfully renders the Klein sheet's generic face and the result drifts off the pick.
2. Pixel weight is why: with `ref_image_size=max` a 1152x2016 sheet is fed at full 2.32 Mpx, so the redo carries 5.70 Mpx of reference in chunk 1 and 4.64 Mpx in chunk 2 against a 1.03 Mpx frame, 4.5-5.5x the reference load of the approved 481-frame clips, which use one 1.03 Mpx 16:9 start frame and nothing at all in the continuation.
3. The prompts never ask for a face: 0 of 8 prompt strings contain close-up / crop / bust / headshot / portrait / macro / shallow-depth / negative-prompt words, and the face boxes prove it - 90-190 px wide, 1.1-3.6% of the frame, sheet-fed clips no better than sheet-free ones, which is unresolvable at 1080p; only a 400-550 px face-crop reference plus explicit face language changes that, keeping the full-body 16:9 start frame.
4. The binding got weaker at the same time: v1 names each woman by hair colour inside the same picture the video starts from, v2 names her "the woman shown in the multi-view reference sheet" and demotes the start still to scenery, and no submitted prompt uses the left/right spatial anchor - so hair colour is the only thing separating the two identities, and the pair's sheets are 0.30-0.57 similar to each other, which invites a swap.
5. What to change for R6-R9 (R4G), no new renders and no new seeds in this pass: keep the 16:9 approved start frame as the ONLY reference and keep it present in **every** chunk including the continuation (c1/c2's chunk 2 has no reference at all, r1/r2's chunk 2 has only the two sheets), carry the extender README's `subject_definitions` wording on both chunks with "<Subject 1> is the exact same woman shown in <Picture 1>", say the picture is for her face and hair only, add one "the camera frames her face in close-up" beat per woman, keep `denoise 1.0 / shift 10 and 3 / euler / 10 steps`, and keep 1344x768 / 24 fps / 243 f (124 c0 + 119 extension) with audio.

### G. R4F -> R4G

R4F (research + measurement, this pass) is complete: the ranked fix list is `C:\AI\community\notes\hc_face_research_20261023.md` (F1-F10); this file is the prompt/reference/face-box audit it was built on. R4G (next task, TASKS.md line 36) applies F1 (approved pick as the ONLY reference, Klein sheets dropped from c0 **and** c1), F2 (`ref_image_size` back to the node default `match`, 1 ref), F3 (extender `subject_definitions` wording on both chunks, "the exact same woman shown in <Picture 1>"), F4 (picture = face and hair only, garment words out of the binding) and F7 (one face close-up beat per woman) to the remaining redo lines R6-R9 in the builder `C:\AI\community\notes\ali163_hc_r5_build.py`; no render is requested while `used_min >= 475` or `jobs >= 35`. F8 (a per-woman 400-550 px face crop) is the strongest single change by these numbers but needs a Derrick-approved crop written into `ComfyUI\input\community\hc`, so it stays out of the no-download set.

Statements required by the task: c1, c2, r1, r2 prompt texts are listed verbatim and completely (section A + the `<details>` blocks); the line-by-line comparison is section B; the reference images as placed (pixel sizes, aspect, sha256, per-face box sizes) are in the tables of sections C and D; face box size per woman per clip is measured in D. **No new renders were submitted in this pass** (no `p7\JOB_REQUEST.json` was written, no GPU touched), **no new seeds** (only the seeds of the four already-submitted clips are named), **no vision judge**, **no download, no install** (R4F runs used `C:\AI\qa_gate_venv` only, per its ALLOWLIST).

## R4G (2026-10-23, Forge): the old r1/r2 prompt text and reference slots vs the CITED wording, line by line

Written by `C:\AI\community\notes\ali163_hc_r4g_build.py` (the builder) and `C:\AI\community\notes\ali163_hc_r4g_audit.py` (this section). Task line R4G = graph builder + prompt text work: **no GPU, no render, no JOB_REQUEST.json, no download, no new node, no vision judge, no new seeds**.

### R4G.0 Inputs (read this pass)

| file | bytes | sha256(12) |
|---|---|---|
| runs\ali147_pool_hc_r1_s51130001\request.api.json (r1) | 13805 | 2c8eeb6d2d0b |
| runs\ali147_pool_hc_r2_s51130002\request.api.json (r2) | 14507 | 5719961fa101 |
| runs\ali147_pool_hc_r3_s51130003\request.api.json (R6) | 14720 | ed52ea0b0e0f |
| runs\ali147_pool_hc_r4_s51130004\request.api.json (R7) | 13585 | b17333d681f6 |
| runs\ali147_pool_hc_r5_s51130005\request.api.json (R8) | 13600 | a47142b394b9 |
| runs\ali147_pool_hc_r6_s51130006\request.api.json (R9) | 15371 | e20106ff422f |
| notes\hc_r3_c0.txt (R6 c0) | 5043 | fd4815380ed9 |
| notes\hc_r3_c1.txt (R6 c1) | 4323 | 95a4fb18c924 |
| notes\hc_r4_c0.txt (R7 c0) | 4371 | a9c8a808383e |
| notes\hc_r4_c1.txt (R7 c1) | 3856 | 26ae52224813 |
| notes\hc_r5_c0.txt (R8 c0) | 4449 | 2f5788568b3f |
| notes\hc_r5_c1.txt (R8 c1) | 3803 | fb212b9e80a1 |
| notes\hc_r6_c0.txt (R9 c0) | 5306 | bbdbbb96925f |
| notes\hc_r6_c1.txt (R9 c1) | 4705 | 0133ac0f226f |
| notes\web\ext_readme.md | 21826 | 2acf218bdced |
| notes\web\longvid_readme.md | 40528 | a6b23f0d1676 |
| notes\web\hf_eros_d63.html | 294656 | 860f49e97969 |

### R4G.1 The cited community wording, quoted VERBATIM from the saved copies (file + line numbers)

`notes\web\ext_readme.md` = https://raw.githubusercontent.com/tritant/ComfyUI_MiniMax_H3_Extender/main/README.md (the node installed on this box, `ComfyUI\custom_nodes\ComfyUI_MiniMax_H3_Extender`), lines 379-392:

> When using image references, it is strongly recommended to place a `subject_definitions` block at the **beginning of every clip prompt**.
>
> This helps MiniMax H3 keep the same subjects, identities, clothing, visual roles and even the environment associated with a reference image from one clip to the next.
>
> ### Example
>
> > **subject_definitions:**  
> > `<Picture 1>` is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions, clothing, accessories, and overall look of `<Subject 1>`, as well as the established environment and visual context of the scene.  
> > `<Picture 2>` is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions, clothing, accessories, and overall look of `<Subject 2>`.  
> > `<Subject 1>` is the exact same woman shown in `<Picture 1>`.  
> > `<Subject 2>` is her friend, the exact same woman shown in `<Picture 2>`.  
> > `<Subject 3>` is the same street environment and scene context established in `<Picture 1>`.
>
> Place this `subject_definitions` block at the **very beginning of every clip prompt**.
>

`notes\web\longvid_readme.md` = https://raw.githubusercontent.com/Smite79/MiniMax-H3-LongVideos/main/README.md:

- L174-179 (F4 - once a garment is off the shot says the picture is for that person's face and hair only, and the prompt names the garment no more than the beat does):
> - A reference picture shows its person in the clothes they had on, and H3 copies what it
>   sees, print and all, back onto them. So the picture goes in cropped to their face and
>   hair (see Reference pictures), and once a garment is off the shot also says the picture
>   is for their face and hair only. `info` shows *naked:* for each undressed person.
> - The prompt names the garment no more than the beat does, since every mention is one
>   more pull toward drawing it.
- L349-350 (F5 - a beat that sets the camera framing (close-up, the camera frames her face) holds only its own people):
>   between frame only the beat's people as above. A beat that sets the camera's framing
>   (*close-up*, *the camera frames her face*) always holds only its own people.
- L436-437 (F7 - a person's own picture is left out of shots that start on a frame they are already in):
> Once a person is held, their own picture (written right after their name, as in
> `Mara <Picture 1>`) is left out of shots that start on a frame they are already in. A
- L458-461 (F4/F8 - a person's picture goes in cropped to their face and hair, so clothes come only from the words (the 400-550 px crop is NOT approved for this batch, so R4G uses the full pick at `match` instead)):
> A person's picture always goes in cropped to their face and hair (found with DWPose), so
> their clothes come only from the words: the clothes in the picture never end up on top of
> the ones the scene describes. `info` marks it *face and hair* under *pictures:*, and says
> when no face could be found and the whole picture went in.
- L621-621 (F6 - denoise is fixed at 1.0: partial denoise desyncs the joint audio/video schedule):
> - Denoise is fixed at 1.0: partial denoise desyncs the joint audio/video schedule.

The 10Eros-Max card wording (https://huggingface.co/TenStrip/10Eros-Max/discussions/63, saved as `notes\web\hf_eros_d63.html`, quoted in `notes\hc_face_research_20261023.md` item 5): `<Subject 1>` (appears in [Shot 1]): **fully_preserved - her face, hair, clothes, bone structure are exactly as in `<picture 1>`**.

Node code read locally (no download): `ComfyUI\custom_nodes\ComfyUI_MiniMax_H3_Extender\extender.py:110-116, 2267-2310` - `ref_image_size` `match` caps every reference to the canvas pixels, `max` only downscales a side over 2048, so the 1152x2016 Klein sheets entered the VAE at full 2.32 Mpx against a 1.032 Mpx canvas (R4F section C).

### R4G.2 Reference slots AS WIRED in the graph - old r1/r2 (submitted) vs new R6-R9 (this pass)

| clip | chunk | class | ref_image_size | ref slots -> LoadImage node -> file | file WxH | file Mpx | effective Mpx into the VAE |
|---|---|---|---|---|---|---|---|
| r1 | c0 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC1_Two_women_in_studio_editorial.jpg` | 1376x768 | 1.057 | 1.057 |
| r1 | c0 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_2 -> sheet (LoadImage) -> `community/hc/HC1_w1_blonde_00001_.png` | 1152x2016 | 2.322 | 2.322 |
| r1 | c1 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_1 -> sheet (LoadImage) -> `community/hc/HC1_w1_blonde_00001_.png` | 1152x2016 | 2.322 | 2.322 |
| r2 | c0 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC2_Two_women_in_passionate_embrace.jpg` | 1376x768 | 1.057 | 1.057 |
| r2 | c0 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_2 -> sheet (LoadImage) -> `community/hc/HC2_w1_blonde_00001_.png` | 1152x2016 | 2.322 | 2.322 |
| r2 | c1 | MiniMaxH3ReferenceToVideo | max | ref_images.ref_image_1 -> sheet (LoadImage) -> `community/hc/HC2_w1_blonde_00001_.png` | 1152x2016 | 2.322 | 2.322 |
| R6 | c0 | MiniMaxH3ReferenceToVideo | match | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC3_lesbian_beach.jpg` | 1792x1008 | 1.806 | 1.032 |
| R6 | c1 | MiniMaxH3ImageToVideo | (no ref_image_size key) | (0 reference images) | - | - | - |
| R6 | graph | - | - | **LoadImage nodes = 1 ['img']; c0 refs = 1 (the approved pick), c1 refs = 0** | - | - | - |
| R7 | c0 | MiniMaxH3ReferenceToVideo | match | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC4_strip_tease_aerobics.jpg` | 1792x1008 | 1.806 | 1.032 |
| R7 | c1 | MiniMaxH3ImageToVideo | (no ref_image_size key) | (0 reference images) | - | - | - |
| R7 | graph | - | - | **LoadImage nodes = 1 ['img']; c0 refs = 1 (the approved pick), c1 refs = 0** | - | - | - |
| R8 | c0 | MiniMaxH3ReferenceToVideo | match | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC5_spicy_solo.jpg` | 1792x1008 | 1.806 | 1.032 |
| R8 | c1 | MiniMaxH3ImageToVideo | (no ref_image_size key) | (0 reference images) | - | - | - |
| R8 | graph | - | - | **LoadImage nodes = 1 ['img']; c0 refs = 1 (the approved pick), c1 refs = 0** | - | - | - |
| R9 | c0 | MiniMaxH3ReferenceToVideo | match | ref_images.ref_image_1 -> img (LoadImage) -> `community/hc/HC6_women_casino_lounge.jpg` | 1376x768 | 1.057 | 1.032 |
| R9 | c1 | MiniMaxH3ImageToVideo | (no ref_image_size key) | (0 reference images) | - | - | - |
| R9 | graph | - | - | **LoadImage nodes = 1 ['img']; c0 refs = 1 (the approved pick), c1 refs = 0** | - | - | - |

The Klein sheet nodes (`sheet`, `sheet2`) are deleted from the new graphs: no sheet is referenced by any clip in this batch, and the prompt text carries no `<Picture 2>`-or-higher slot (counted in .3/.4).

### R4G.3 Line by line: the OLD r1/r2 `subject_definitions` text vs the NEW R4G text (verbatim, with the F-rule per line)

Pair clips compare pair-to-pair: r1 (HC1, pair) -> R6 (HC3, pair); r2 (HC2, pair) -> R9 (HC6, pair). The solo clips R7 (HC4) and R8 (HC5) have no submitted solo baseline; their new text is listed in .4.

#### r1.c0 (submitted, sheeted) vs R6.c0 (new, pick-only) - 6 lines

| # | F-rule for this line | OLD (verbatim) | old flags | NEW (verbatim) | new flags |
|---|---|---|---|---|---|
| 1 | F3: block header at the very beginning of every clip prompt (README L379, L392) | subject_definitions: | - | subject_definitions: | - |
| 2 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture. | sheet-ref(Picture2+), subject-line | <Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions, and overall look of <Subject 1> and of <Subject 2>. The photograph in <Picture 1> shows two adult women close together, and it is the only visual reference for either woman in this clip. The woman on the left of <Picture 1> is fully clothed, her face is small in the frame, and this picture is the only visual reference for her in this clip; the same is true of the woman on the right of <Picture 1>. <Picture 1> is used for the faces and the hair of the two women only: the environment, the wardrobe and the camera of this video are new and are not taken from <Picture 1>. | garment-word, face/identity-words, verbatim-def-head |
| 3 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 24, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin. | sheet-ref(Picture2+), subject-line | <Subject 1> is the exact same woman shown in <Picture 1>, the woman on the left of the photograph, a fictional adult aged 21, preserving her face, hairstyle, and body proportions with complete fidelity, with a slim natural figure, a natural waist, gently rounded hips and full natural breasts. | face/identity-words, binding-phrase, subject-line |
| 4 | prose line, no identity rule attached | <Picture 1> is the start still of <Subject 1> and <Subject 2> seated close together in a warm photo studio. | - | <Subject 2> is the exact same woman shown in <Picture 1>, the woman on the right of the photograph, a fictional adult aged 23, preserving her face, hairstyle, and body proportions with complete fidelity, with a soft feminine figure, wide hips and full natural breasts. | face/identity-words, binding-phrase, subject-line |
| 5 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Picture 2> is the multi-view reference sheet of <Subject 1> alone. | sheet-ref(Picture2+) | (dropped) | - |
| 6 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Picture 3> is the multi-view reference sheet of <Subject 2> alone. | sheet-ref(Picture2+) | (dropped) | - |

#### r1.c1 (submitted, sheeted) vs R6.c1 (new, pick-only) - 5 lines

| # | F-rule for this line | OLD (verbatim) | old flags | NEW (verbatim) | new flags |
|---|---|---|---|---|---|
| 1 | F3: block header at the very beginning of every clip prompt (README L379, L392) | subject_definitions: | - | subject_definitions: | - |
| 2 | F3: subject line rebuilt on the card wording (face, hairstyle, body proportions) with the binding phrase | <Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture. | subject-line | This continuation chunk carries no reference pictures at all: the identity of both women is carried by these words and by the first 5 seconds of this clip. | face/identity-words |
| 3 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin. | sheet-ref(Picture2+), subject-line | <Subject 1> is the exact same woman shown in <Picture 1> of the first 5 seconds of this clip, preserving her face, hairstyle, and body proportions with complete fidelity: the woman who was on the left of that photograph, a fictional adult aged 21, with a slim natural figure, a natural waist, gently rounded hips and full natural bare breasts with round light-brown areolae and natural nipples. | face/identity-words, binding-phrase, subject-line |
| 4 | prose line, no identity rule attached | (no such line) | - | <Subject 2> is the exact same woman shown in <Picture 1> of the first 5 seconds of this clip, preserving her face, hairstyle, and body proportions with complete fidelity: the woman who was on the right of that photograph, a fictional adult aged 23, with a soft feminine figure, wide hips and full natural bare breasts. | face/identity-words, binding-phrase, subject-line |
| 5 | prose line, no identity rule attached | (no such line) | - | Their faces, hairstyles and body proportions in this continuation are the faces, hairstyles and body proportions of the first 5 seconds, unchanged; undressing and being touched are actions, not a change of identity. | garment-word, face/identity-words |

Per-clip identity facts for r1 -> R6: pick refs in c0 old 2 -> new 1; refs in c1 old 1 -> new 0; `<Picture 2+>` occurrences old 12 -> new 0; binding phrase old 0 -> new 4; "in close-up" beats old 0 -> new 4 (women 2, one per woman in c0 beat 1 and in c1).

#### r2.c0 (submitted, sheeted) vs R9.c0 (new, pick-only) - 6 lines

| # | F-rule for this line | OLD (verbatim) | old flags | NEW (verbatim) | new flags |
|---|---|---|---|---|---|
| 1 | F3: block header at the very beginning of every clip prompt (README L379, L392) | subject_definitions: | - | subject_definitions: | - |
| 2 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 1> is the adult woman shown in the multi-view reference sheet in <Picture 2>, the blonde woman of the two-woman start still in <Picture 1>, a fictional adult aged 26, with long loose blonde hair, soft natural features, a slim natural figure with full natural breasts and gently rounded hips, and smooth lightly tanned skin with a natural matte texture. | sheet-ref(Picture2+), subject-line | <Picture 1> is the reference image defining the exact visual appearance, identity, face, hairstyle, body proportions, and overall look of <Subject 1> and of <Subject 2>. The photograph in <Picture 1> shows two adult women embracing close together, and it is the only visual reference for either woman in this clip. The woman on the left of <Picture 1> is fully clothed, her face is small in the frame, and this picture is the only visual reference for her in this clip; the same is true of the woman on the right of <Picture 1>. <Picture 1> is used for the faces and the hair of the two women only: the environment, the wardrobe and the camera of this video are new and are not taken from <Picture 1>. | garment-word, face/identity-words, verbatim-def-head |
| 3 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 2> is the adult woman shown in the multi-view reference sheet in <Picture 3>, the dark-haired woman of the two-woman start still in <Picture 1>, a fictional adult aged 25, with long dark hair, a soft feminine figure, natural waist, wide hips and full natural breasts, and warm smooth skin. | sheet-ref(Picture2+), subject-line | <Subject 1> is the exact same woman shown in <Picture 1>, the woman on the left of the photograph, a fictional adult aged 21, preserving her face, hairstyle, and body proportions with complete fidelity, with a slim natural figure, a natural waist, gently rounded hips and full natural breasts. | face/identity-words, binding-phrase, subject-line |
| 4 | prose line, no identity rule attached | <Picture 1> is the start still of <Subject 1> and <Subject 2> locked in a close passionate embrace. | - | <Subject 2> is the exact same woman shown in <Picture 1>, the woman on the right of the photograph, a fictional adult aged 25, preserving her face, hairstyle, and body proportions with complete fidelity, with a soft feminine figure, wide hips and full natural breasts. | face/identity-words, binding-phrase, subject-line |
| 5 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Picture 2> is the multi-view reference sheet of <Subject 1> alone. | sheet-ref(Picture2+) | (dropped) | - |
| 6 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Picture 3> is the multi-view reference sheet of <Subject 2> alone. | sheet-ref(Picture2+) | (dropped) | - |

#### r2.c1 (submitted, sheeted) vs R9.c1 (new, pick-only) - 5 lines

| # | F-rule for this line | OLD (verbatim) | old flags | NEW (verbatim) | new flags |
|---|---|---|---|---|---|
| 1 | F3: block header at the very beginning of every clip prompt (README L379, L392) | subject_definitions: | - | subject_definitions: | - |
| 2 | F3: subject line rebuilt on the card wording (face, hairstyle, body proportions) with the binding phrase | <Subject 1> is the adult woman from the multi-view reference sheet in <Picture 1>, the blonde woman established in the first 5 seconds of this clip: long loose blonde hair, soft natural features, slim natural figure, full natural bare breasts with round light-brown areolae and natural nipples, and lightly tanned skin with a natural matte texture. | subject-line | This continuation chunk carries no reference pictures at all: the identity of both women is carried by these words and by the first 5 seconds of this clip. | face/identity-words |
| 3 | F1+F2: this <Picture N> is a Klein multi-view sheet (2-6 faces, pick-vs-own-sheet cosine 0.22-0.47, two unrelated sheets 0.69) - the slot and the line are GONE in the new prompt | <Subject 2> is the adult woman from the multi-view reference sheet in <Picture 2>, the dark-haired woman established in the first 5 seconds of this clip: long dark hair, soft feminine figure, natural waist, wide hips, bare breasts, and warm smooth skin. | sheet-ref(Picture2+), subject-line | <Subject 1> is the exact same woman shown in <Picture 1> of the first 5 seconds of this clip, preserving her face, hairstyle, and body proportions with complete fidelity: the woman who was on the left of that photograph, a fictional adult aged 21, with a slim natural figure, a natural waist, gently rounded hips and full natural bare breasts with round light-brown areolae and natural nipples. | face/identity-words, binding-phrase, subject-line |
| 4 | prose line, no identity rule attached | (no such line) | - | <Subject 2> is the exact same woman shown in <Picture 1> of the first 5 seconds of this clip, preserving her face, hairstyle, and body proportions with complete fidelity: the woman who was on the right of that photograph, a fictional adult aged 25, with a soft feminine figure, wide hips and full natural bare breasts. | face/identity-words, binding-phrase, subject-line |
| 5 | prose line, no identity rule attached | (no such line) | - | Their faces, hairstyles and body proportions in this continuation are the faces, hairstyles and body proportions of the first 5 seconds, unchanged; undressing and being touched are actions, not a change of identity. Both dark evening dresses from the first 5 seconds lie in a heap on the red vinyl booth seat and stay there; both women stay dressed from the waist down. | garment-word, face/identity-words |

Per-clip identity facts for r2 -> R9: pick refs in c0 old 2 -> new 1; refs in c1 old 1 -> new 0; `<Picture 2+>` occurrences old 12 -> new 0; binding phrase old 0 -> new 4; "in close-up" beats old 0 -> new 4 (women 2, one per woman in c0 beat 1 and in c1).

### R4G.4 The new prompt files (R6-R9) - guard_ok, v2 blocks, close-up beats, slots used

| file | chars | guard_ok | subject_definitions: | overall_soundscape: | non_diegetic_music: | retention_analysis: (c0) / integrated_multimodal_description: (c1) | "in close-up" | <Picture 1> | <Picture 2+> | binding-phrase lines |
|---|---|---|---|---|---|---|---|---|---|---|
| notes\hc_r3_c0.txt (R6 c0) | 5042 | **True** | True | True | True | True | 2 | 12 | 0 | 2 |
| notes\hc_r3_c1.txt (R6 c1) | 4322 | **True** | True | True | True | True | 2 | 2 | 0 | 2 |
| notes\hc_r4_c0.txt (R7 c0) | 4370 | **True** | True | True | True | True | 1 | 9 | 0 | 1 |
| notes\hc_r4_c1.txt (R7 c1) | 3855 | **True** | True | True | True | True | 1 | 1 | 0 | 1 |
| notes\hc_r5_c0.txt (R8 c0) | 4448 | **True** | True | True | True | True | 1 | 9 | 0 | 1 |
| notes\hc_r5_c1.txt (R8 c1) | 3802 | **True** | True | True | True | True | 1 | 1 | 0 | 1 |
| notes\hc_r6_c0.txt (R9 c0) | 5305 | **True** | True | True | True | True | 2 | 12 | 0 | 2 |
| notes\hc_r6_c1.txt (R9 c1) | 4704 | **True** | True | True | True | True | 2 | 2 | 0 | 2 |

`guard_ok` is `C:\AI\community\scripts\comm.py::guard_ok` (the youth guard the runner applies), run here on all 8 files: all True; no youth-coded word (minor/teen/school/young/underage) appears in any of them; every character is a named fictional adult aged 21+ (content lock v2.3.0).

### R4G.5 Builder self-check - 9 numbered checks per clip, captured from a real run of the builder

`python C:\AI\community\notes\ali163_hc_r4g_build.py` -> rc 0; R6 9/9 checks; R7 9/9 checks; R8 9/9 checks; R9 9/9 checks (the raw run prints 112 PASS/FAIL lines because check 1 prints one line per allowed node)

- **R6** / ali147_pool_hc_r3_s51130003 / seed 51130003: checks 1, 2, 3, 4, 5, 6, 7, 8, 9 -> **9/9 PASS**; 14720 sha256 ed52ea0b0e0fcd642491ad56219846b572f973c08b9a645ae07b3856342bc8fb
  - PASS 1 graph diff vs ali147_pool_refsheet_b_s51080000: nodes +[] -['sheet'], count 25, changed nodes ['c0', 'c1', 'img', 'noise', 'save', 'sheet', 'win1'], per-node keys as expected
  - PASS 2 frames = c0 124 + win1.extension_frames 119 = 243 (the R1 count 243), 24 fps, 10.125 s
  - PASS 3 geometry 1344x768 (16:9) in c0 and c1
  - PASS 4 c0 refs ['ref_images.ref_image_1'] (the pick only, node img), c1 refs [] (class MiniMaxH3ImageToVideo, 0 refs), no sheet node, pick community/hc/HC3_lesbian_beach.jpg resolves in ComfyUI\input and is byte-identical to approved GI173.jpg: True
  - PASS 5 c0 ref_image_size = match (node default, ref downscaled to the 1344x768 canvas px); c1 has no ref_image_size (0 refs)
  - PASS 6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), single pass (2 SamplerCustomAdvanced, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768
  - PASS 7 prompts byte-exact in the graph, v2 blocks present (c0 subject_definitions/summary/retention_analysis/detailed_description, c1 subject_definitions/integrated_multimodal_description + first 5 seconds), overall_soundscape: + non_diegetic_music: in both, guard_ok, no youth-coded words (c0 5042 chars, c1 4322 chars)
  - PASS 8 extender/model-card wording in BOTH chunks: verbatim <Picture 1> definition in c0, binding phrase '<Subject 1> is the exact same woman shown in <Picture 1>' in c0 and c1, c1 declares 0 reference pictures, picture = face and hair only + fully clothed/small-face/only-reference sentence in c0, close-up face beats 2/2 (women 2), subjects c0 2 c1 2 = 2 women, no <Picture 2+>, no garment word inside any binding line
  - PASS 9 id charset + live ralph.ps1 id gates ['^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$', '^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'], id free (no result.json/objective.json/output folder), no JOB_REQUEST.json queued (R4G = no render)

- **R7** / ali147_pool_hc_r4_s51130004 / seed 51130004: checks 1, 2, 3, 4, 5, 6, 7, 8, 9 -> **9/9 PASS**; 13585 sha256 b17333d681f6ed6e23c174942508d4f57c396376c67c618eb86b90c63c51de27
  - PASS 1 graph diff vs ali147_pool_refsheet_b_s51080000: nodes +[] -['sheet'], count 25, changed nodes ['c0', 'c1', 'img', 'noise', 'save', 'sheet', 'win1'], per-node keys as expected
  - PASS 2 frames = c0 124 + win1.extension_frames 119 = 243 (the R1 count 243), 24 fps, 10.125 s
  - PASS 3 geometry 1344x768 (16:9) in c0 and c1
  - PASS 4 c0 refs ['ref_images.ref_image_1'] (the pick only, node img), c1 refs [] (class MiniMaxH3ImageToVideo, 0 refs), no sheet node, pick community/hc/HC4_strip_tease_aerobics.jpg resolves in ComfyUI\input and is byte-identical to approved GI107.jpg: True
  - PASS 5 c0 ref_image_size = match (node default, ref downscaled to the 1344x768 canvas px); c1 has no ref_image_size (0 refs)
  - PASS 6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), single pass (2 SamplerCustomAdvanced, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768
  - PASS 7 prompts byte-exact in the graph, v2 blocks present (c0 subject_definitions/summary/retention_analysis/detailed_description, c1 subject_definitions/integrated_multimodal_description + first 5 seconds), overall_soundscape: + non_diegetic_music: in both, guard_ok, no youth-coded words (c0 4370 chars, c1 3855 chars)
  - PASS 8 extender/model-card wording in BOTH chunks: verbatim <Picture 1> definition in c0, binding phrase '<Subject 1> is the exact same woman shown in <Picture 1>' in c0 and c1, c1 declares 0 reference pictures, picture = face and hair only + fully clothed/small-face/only-reference sentence in c0, close-up face beats 1/1 (women 1), subjects c0 1 c1 1 = 1 women, no <Picture 2+>, no garment word inside any binding line
  - PASS 9 id charset + live ralph.ps1 id gates ['^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$', '^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'], id free (no result.json/objective.json/output folder), no JOB_REQUEST.json queued (R4G = no render)

- **R8** / ali147_pool_hc_r5_s51130005 / seed 51130005: checks 1, 2, 3, 4, 5, 6, 7, 8, 9 -> **9/9 PASS**; 13600 sha256 a47142b394b92b3b9589692c66f0b162f70df9be4974d8dca1ec35f42a68bfc5
  - PASS 1 graph diff vs ali147_pool_refsheet_b_s51080000: nodes +[] -['sheet'], count 25, changed nodes ['c0', 'c1', 'img', 'noise', 'save', 'sheet', 'win1'], per-node keys as expected
  - PASS 2 frames = c0 124 + win1.extension_frames 119 = 243 (the R1 count 243), 24 fps, 10.125 s
  - PASS 3 geometry 1344x768 (16:9) in c0 and c1
  - PASS 4 c0 refs ['ref_images.ref_image_1'] (the pick only, node img), c1 refs [] (class MiniMaxH3ImageToVideo, 0 refs), no sheet node, pick community/hc/HC5_spicy_solo.jpg resolves in ComfyUI\input and is byte-identical to approved GI150.jpg: True
  - PASS 5 c0 ref_image_size = match (node default, ref downscaled to the 1344x768 canvas px); c1 has no ref_image_size (0 refs)
  - PASS 6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), single pass (2 SamplerCustomAdvanced, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768
  - PASS 7 prompts byte-exact in the graph, v2 blocks present (c0 subject_definitions/summary/retention_analysis/detailed_description, c1 subject_definitions/integrated_multimodal_description + first 5 seconds), overall_soundscape: + non_diegetic_music: in both, guard_ok, no youth-coded words (c0 4448 chars, c1 3802 chars)
  - PASS 8 extender/model-card wording in BOTH chunks: verbatim <Picture 1> definition in c0, binding phrase '<Subject 1> is the exact same woman shown in <Picture 1>' in c0 and c1, c1 declares 0 reference pictures, picture = face and hair only + fully clothed/small-face/only-reference sentence in c0, close-up face beats 1/1 (women 1), subjects c0 1 c1 1 = 1 women, no <Picture 2+>, no garment word inside any binding line
  - PASS 9 id charset + live ralph.ps1 id gates ['^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$', '^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'], id free (no result.json/objective.json/output folder), no JOB_REQUEST.json queued (R4G = no render)

- **R9** / ali147_pool_hc_r6_s51130006 / seed 51130006: checks 1, 2, 3, 4, 5, 6, 7, 8, 9 -> **9/9 PASS**; 15371 sha256 e20106ff422f9150598dbf22548b356b8dbd35bafa1cb007159f9cbc44519aff
  - PASS 1 graph diff vs ali147_pool_refsheet_b_s51080000: nodes +[] -['sheet'], count 25, changed nodes ['c0', 'c1', 'img', 'noise', 'save', 'sheet', 'win1'], per-node keys as expected
  - PASS 2 frames = c0 124 + win1.extension_frames 119 = 243 (the R1 count 243), 24 fps, 10.125 s
  - PASS 3 geometry 1344x768 (16:9) in c0 and c1
  - PASS 4 c0 refs ['ref_images.ref_image_1'] (the pick only, node img), c1 refs [] (class MiniMaxH3ImageToVideo, 0 refs), no sheet node, pick community/hc/HC6_women_casino_lounge.jpg resolves in ComfyUI\input and is byte-identical to approved BD076.jpg: True
  - PASS 5 c0 ref_image_size = match (node default, ref downscaled to the 1344x768 canvas px); c1 has no ref_image_size (0 refs)
  - PASS 6 sampling fixed as base (denoise 1.0 in the base sched/samplers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8), single pass (2 SamplerCustomAdvanced, no RIFE/refine/upscale), audio VAE + audio decoder wired, 1344x768
  - PASS 7 prompts byte-exact in the graph, v2 blocks present (c0 subject_definitions/summary/retention_analysis/detailed_description, c1 subject_definitions/integrated_multimodal_description + first 5 seconds), overall_soundscape: + non_diegetic_music: in both, guard_ok, no youth-coded words (c0 5305 chars, c1 4704 chars)
  - PASS 8 extender/model-card wording in BOTH chunks: verbatim <Picture 1> definition in c0, binding phrase '<Subject 1> is the exact same woman shown in <Picture 1>' in c0 and c1, c1 declares 0 reference pictures, picture = face and hair only + fully clothed/small-face/only-reference sentence in c0, close-up face beats 2/2 (women 2), subjects c0 2 c1 2 = 2 women, no <Picture 2+>, no garment word inside any binding line
  - PASS 9 id charset + live ralph.ps1 id gates ['^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+(_[a-z0-9]+)?_s\\d+|ali173_[a-z0-9]+(_[a-z0-9]+)?_s\\d+)$', '^(ali147_pool|ali173)_[a-z0-9]+(_[a-z0-9]+)?_s\\d+$'], id free (no result.json/objective.json/output folder), no JOB_REQUEST.json queued (R4G = no render)

`ALL CHECKS PASS (112 PASS lines, 9 numbered checks per clip: ['R6', 'R7', 'R8', 'R9'])`

The 9 checks are: 1 graph diff vs the RS6 base is only the intended nodes/keys (sheet deleted; c0/c1/img/noise/save/win1 keys as listed; every other node byte-identical); 2 frames 124 + 119 = 243 at 24 fps = 10.125 s (the R1 frame count); 3 1344x768 in both chunks; 4 exactly 1 LoadImage (the approved pick, byte-identical to the approved file, resolves in ComfyUI\input) on c0 and 0 reference images on c1 (c1 = MiniMaxH3ImageToVideo), no sheet node; 5 `ref_image_size = match` on c0 and no ref key at all on c1; 6 sampling byte-identical to the base (denoise 1.0 on both schedulers, euler/simple/10 steps, shift 10/3, vsa, beta6 int8, single pass, audio VAE + audio decoder wired); 7 prompts byte-exact in the graph + v2 blocks + guard_ok; 8 the R4G identity wording (verbatim `<Picture 1>` definition, binding phrase in BOTH chunks, c1 declares 0 reference pictures, picture = face and hair only, fully-clothed/small-face sentence, one close-up beat per woman, no `<Picture 2+>`, no garment word inside any binding line); 9 id charset + the live ralph.ps1 id gates + id free + no JOB_REQUEST.json queued.

One builder fix in this pass: check 6 counted `KSamplerAdvanced` nodes, which this graph does not use (it uses 2 `SamplerCustomAdvanced` + `KSamplerSelect`), so check 6 reported FAIL on a correct graph. It now counts the real node class; no graph byte changed by that fix.

### R4G.6 Five-line plain summary

1. The Klein multi-view sheets are gone from both chunks of R6-R9: each new graph has exactly **1 LoadImage** (the approved pick) on c0 with `ref_image_size = match` (1.032 Mpx into the VAE, the canvas size) and **0 reference images** on c1.
2. Both chunks now open with `subject_definitions:` in the extender README's verbatim wording - the `<Picture 1>` definition line naming identity, face, hairstyle and body proportions, and `<Subject 1> is the exact same woman shown in <Picture 1>` (pairs: both subjects bind to the one pair pick); c1 says the continuation carries no reference pictures at all.
3. The pick is declared to be for the face and the hair only, the picture is named the only visual reference, and no garment word sits inside any binding line (garment words stay in the action prose, where the R4F count showed they were the only garment mentions).
4. One "the camera frames her face in close-up" beat per woman sits in c0 beat 1 and in c1; sampling is untouched (denoise 1.0, cfg 1, euler/simple, 10 steps, shift 10/3, vsa, beta6 int8, single pass, 243 f = 124 + 119, 24 fps, audio wired).
5. The builder self-check is **9/9 PASS on all four clips** (112 PASS lines, rc 0); prompt files hc_r3_c0/_c1, hc_r4_c0/_c1, hc_r5_c0/_c1, hc_r6_c0/_c1 all pass `guard_ok`; R4G requested **no render** - `p7\JOB_REQUEST.json` is not written, the ids are free, and R6-R9 request them one at a time under the 475-min / 35-job gate.


## 8b. R4G2 (2026-10-23, the crop path) - what changed in this audit

Face crops (scripts\face_crop.py, --size 512, boxes from CPU SCRFD-10G notes\ali163_hc_r4g2_facebox.py, verified by notes\ali163_hc_r4g2_verify.py with SCRFD-10G + ArcFace glintr100, table notes\face_r4g2\r4g2_table.txt):

| crop | source pick | face box | px | faces in crop | face % of crop | cos(crop, source face) |
|---|---|---|---|---|---|---|
| HC3_w1_face.png | GI173.jpg | 382,0,171,240 | 512x512 | 1 | 15.0 % | 0.992 |
| HC3_w2_face.png | GI173.jpg | 799,228,222,204 | 512x512 | 1 | 16.5 % | 0.922 |
| HC4_w1_face.png | GI107.jpg | 830,56,107,143 | 512x512 | 1 | 15.6 % | 0.960 |
| HC5_w1_face.png | GI150.jpg | 307,154,163,212 | 512x512 | 1 | 15.7 % | 0.958 |
| HC6_w1_face.png | BD076.jpg | 471,33,209,157 | 512x512 | 1 | 16.3 % | 0.905 |
| HC6_w2_face.png | BD076.jpg | 783,68,133,190 | 512x512 | 1 | 15.0 % | 0.910 |

Pair separation: cos(HC3_w1, HC3_w2) = 0.272 and cos(HC6_w1, HC6_w2) = 0.098 - the two crops of a pair are provably different women, so a swapped reference slot in R6/R9 cannot pass silently.

The reference-pixel problem in section 8 is solved by geometry: a 512x512 crop is 0.26 Mpx against a 1344x768 = 1.03 Mpx canvas, so `ref_image_size` "match" (the node default, now set on c0) never resamples the reference and the face enters the VAE at crop resolution. Reference area share = 0.26/(1.03+0.26) = 20 % for one crop, 0.52/1.55 = 34 % for a pair (the RS6 sheet was 2.32 Mpx = 69 %).

Wording shipped in the four c0 prompts and the two pair c1 prompts (F1-F5 kept: definition-line count == women, <Subject N> count == women, no garment word inside a binding line, the calm-camera close-up beat, face-and-hair-only reference framing):
1. "The photograph in <Picture 1> shows ... her face is small in the frame" is GONE - untrue of a crop. Replaced by "<Picture 1> is a tight close-up crop of the face and hair of one adult woman, cut from the approved photograph in which she is fully clothed, and the face fills the picture": the fully-clothed provenance R4G asked for survives, reworded so it no longer claims a wide frame.
2. pairs: <Picture 1> -> <Subject 1>, <Picture 2> -> <Subject 2>; the graph wires ref_image_1 -> img (the left-hand woman's crop) and ref_image_2 -> img2 (the right-hand woman's crop); summary + retention lines bind both faces and hair and exclude environment, wardrobe, bodies and camera.
3. the dead "<subject 1/2> is the woman on the left/right of the input photo" fragments (never registered, and after R4G2 also unbacked) are gone from all four c0 files.
4. pair c1 files: "the woman who was on the left/right of that photograph" -> "the woman on the left/right in the opening five seconds of this clip" - c0 no longer describes a photograph layout, and c1 conditions on the clip's own first five seconds.

Graphs (notes\ali163_hc_r4g2_build.py, ALL CHECKS PASS, 116 PASS lines = 10 numbered checks x 4 clips, base runs\ali147_pool_refsheet_b_s51080000, one LoadImage per woman, no Klein sheet node): R6 ali147_pool_hc_r3_s51130003 15,020 B sha 15839d966d18; R7 ali147_pool_hc_r4_s51130004 13,544 B sha 28c9f4da246a; R8 ali147_pool_hc_r5_s51130005 13,569 B sha 7436c17ba1b9; R9 ali147_pool_hc_r6_s51130006 15,655 B sha 661b3af6fbe3. c0 1344x768 length 124 + win1.extension_frames 119 = 243 f @ 24 fps, c1 MiniMaxH3ImageToVideo with 0 reference images, sampling and audio byte-identical to the base. R4G2 requested no render: p7\JOB_REQUEST.json not written, all four ids free.

