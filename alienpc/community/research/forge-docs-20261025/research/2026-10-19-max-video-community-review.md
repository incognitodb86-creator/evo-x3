# Max video: our attempts vs community practice (2026-10-19)

Asked by Derrick, 2026-10-19 8:36 AM CT: "Ok, lets review our previous attempts at making videos. Are we still over complicating this? What does the community do for sex, prompting, poses, ect? Transitioning scenes? I think alot of this is how we are prompting? Do research"
Rules followed: `/workspace/cos/canon/fiction-cond-lock.md` v2.3.0 (fictional adults 18+, no real people, minors guard on). Read-only research. Nothing was downloaded, installed or changed on AlienPc.
Sources: Reddit blocks our fetcher ("blocked by network security"), so Reddit quotes come from the search engine's indexed copy and are marked *(indexed)*. Civitai/CivArchive, HF, docs.comfy.org and note.com were read directly. Rows marked *(10-18 file)* come from `research/community-1min-video-practice-2026-10-18.md` and were not re-opened today.

---
## Verdict (short)
**Yes, we are still overcomplicating it, and the prompt is a big part of it.** The model is fine. Our best clips (Oct 9-10) came from the plainest setup. Everything we added after that (Klein/Flux stills, head swap, PuLID, multi-ref, judges, ArcFace gates, a 45-beat LLM writer with a JSON schema) made no measured difference to identity and made the Oct 17 run fail. The community setup for NSFW H3 is: **one good start image + one short, literal action prompt + one or two NSFW LoRAs at low strength + roll a few seeds and pick by eye.** We have **never loaded an H3 NSFW concept/position LoRA** (`part2_1018/part2_run.py` notes line 107: "H3 concept LoRA files on AlienPc (mystic_v4, anatomy enhancer, pose LoRAs): not in our files"). That is the biggest gap.

---
## PART 1: Our history (box files)

### What H3 is (for targeting the research)
- "H3" = **10Eros-Max**, TenStrip's merge of **MiniMax H3** (`alienpc-hardcore-i2v-director/SKILL.md:39`: "10Eros-Max (MiniMax-H3) I2V"). Production file `10Eros_Max_h3_8stepTURBO_beta6_int8` (`10_packs/max/production-defaults-st8-dynamic-vram.md`).
- MiniMax H3 is **its own model family**: a joint audio+video DiT, 24 fps, frame grid 17k+5 (124 f ≈ 5 s, 362 f ≈ 15 s) (https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/28). It is **not** a Wan, HunyuanVideo or LTX derivative. Our own Oct 10 research found Wan-bound identity tools "n/a for H3 (architecture-bound)" (`cos/research/2026-10-10-face-lock-lora-and-methods.md:43`). 10Eros grafts Wan/LTX attention into H3, but it is built "on the release full bf16 fl2va model as a base" (https://civarchive.com/models/2851079?modelVersionId=3294059). **So: Wan/LTX LoRAs and Wan tricks (SVI, VACE, Lightning) do not apply. Search Civitai with base model = "MiniMax H3".**

### What we tried, what worked, what didn't
| Period | Method | Result |
|---|---|---|
| Oct 9 | beta6 int8 TURBO, Euler/simple 8 steps, shift 10/3, no RIFE, one start image (OFFICIAL KEEP 3:19 PM CT) | **Best on record.** Best clip `V2_768_5S_B6_EULER_SIMPLE_ST8`. ST8 beat ST6; er_sde ruled out (burned look, finger melt) (production-defaults pack) |
| Oct 10 fix-test | Describe fabric/light exactly as in the start image; AddGuide frame-0 pin; hip turn not spin; 2 refs labelled | Helped fabric/light. "Still unsolved: the garment teleports at about 2s; hands fuse into fabric" (same pack) |
| Oct 10 face-lock | "v2 face block": ~120-word face description in `subject_definitions` + "same face" each phase, waist-up for 2-ref | Confirmed on 2 seeds, but prompts became 795-931 words (`maxops/facelock-v2-2026-10-10/FV2_*.txt`, `wc -w`) |
| Oct 9 audit | Video review of 16 clips | Faces hold frontal, drift at turns (best-supported finding); 16/16 clips had a hand defect, 11 fused into skin; 8/12 strip clips dropped the garment wrong; one ref beat two (`audits/2026-10-09-max-full-day-audit-review.md` C10, C13, F-15/16) |
| Oct 16 night | Klein 9B stills + SNOFS LoRA, multi-ref, 2x2 ref sheet, PuLID 1.0/1.4, BFS head swap | Ref choice, multi-ref and PuLID left ArcFace identity at cos 0.10-0.17 ("a different person"). Only BFS head swap moved it (~0.48). Only 1 of 4 beats got a usable panel; clips: bikini top "vanishes"/"dissolves" in 2 of 3 watched takes (`audits/2026-10-17-max-night-results.md`) |
| Oct 17 day | Judges (Dark Roast, Qwen3-VL, Qwen2.5-VL), 0.35/0.55 face gates, ADetailer/DWPose hand gate, HADM, writer LLM + JSON schema, 98-check preflight, canary | Most of the day went on harness, schema and config audits rather than clips (max-DECISIONS 12:22 PM-9:52 PM rows) |
| Oct 17 overnight | run_1017_2205: 45 beats, Flux/Klein stills + multiple refs + judge notes, stitched | Derrick, Oct 18 6:20 AM CT: "I think last night run was a failure honestly" |
| Oct 18 | H3 Continuation 22-frame chaining (single start image, no Klein, no extra refs); Part 2 runs "not with the judge and other stuff"; H3-LongVideos L1/L2 | Approved and queued; **no verdict recorded in max-DECISIONS.md yet** |

### Where we add complexity
1. **Prompt length and shape.** REF2VA six sections with `detailed_description` "~350-500 words" (`ref2va-prompt/SKILL.md:36`, `alienpc-hardcore-i2v-director/SKILL.md:67`: "never paste the short intent card into Max TE"). Actual FV2 prompts: **795-931 words for a 5-10 s clip**.
2. **Face blocks.** A ~120-word face description in `subject_definitions`, then repeated ("her same face… soft oval face, pale ice-blue eyes…") in every phase of the same prompt.
3. **Too many actions per clip.** FV2 pool clip packs 4 timed phases into 5 s: strap slide, peel, toss, turn into a three-quarter rear stance, twerk.
4. **Multi-ref.** 2 refs, chained refs E2/E7/E9, a 2x2 sheet, whole previous clip as `<Video 1>` (Part 2 B/T).
5. **Stills pipeline.** Klein 9B + SNOFS + PuLID + BFS head swap + a planned face LoRA, before any video.
6. **Judges and gates.** 3+ vision judges, ArcFace bands, hand/limb detectors, a strict 9-check still rubric, frame-check scripts.
7. **Beat sheets and orchestration.** 45-48-beat sheets, writer LLM + schema, 98-check preflight, canary, 24 KB custom queue script, one seed for every cell.
8. **Policy wrapped around the prompt.** The skills carry many rules (diff gates, label rules, retention lines) that each made sense alone but add up to a long, rigid paste.

---
## PART 2: What the community does (MiniMax H3 / 10Eros, NSFW i2v)

### (a) Prompt structure and length
- **Use I2VA format for a start image, not REF2VA.** Official ComfyUI guide: "I2VA opens with a fixed image-alignment line, blank line, then body fields" (`integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`) (https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide). Civitai guide: "For I2V, use the image as the first-frame anchor; don't use Ref2VA prompting unless running reference mode" (https://civitai.com/articles/35774/minimax-h3-prompt-guide). *Conflict:* the 10Eros author says beta6 "is essentially a true hybrid, i.e. just a Reference model" and "If I2V is having issues it should be transferred to reference generation" (https://civarchive.com/models/2851079?modelVersionId=3294059). So REF2VA is defensible on beta6, but it doesn't have to be 900 words.
- **Length fits the clip.** "124 [frames] ~5.2 s: One shot, one action beat. 2-5 sentences total… Overstuffing is the most common failure: ten events in five seconds means the model rushes, drops instructions, or slideshows" (https://github.com/shinshin86/comfy-agent/blob/main/docs/minimax-h3-prompting.md). HF system prompt: "~5 seconds (124 frames): 2-3 segments", "Each segment should be 1-3 sentences" (https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/28). 10Eros author: "Jamming like 10 motions into 5 seconds will cause it to rush" (civarchive 2851079 comments).
- **Short and hand-written often beats LLM-long.** u/arlokino: "more detail in the prompt just confuses the model… writing short prompts by hand has gotten me much better results" (https://www.reddit.com/r/StableDiffusion/comments/1vq57lf/ *(indexed)*). u/GrayingGamer: "longer prompts, more tokens, more chance for confusion… You don't need an LLM to write a short story with purple prose" (https://www.reddit.com/r/StableDiffusion/comments/1vlto2s/ *(indexed)*). *Conflict:* the 10Eros author says "The longer and more embellished the prompt, the better the output will be usually" — but his own example is **one ~90-word literal paragraph** of actions in time order (civarchive 2851079). Common ground: literal, time-ordered actions; no padding; no repeated blocks.
- **Don't re-describe the start image.** "Do not re-describe scene content the image already shows unless you are locking it; spend the words on what *changes*" (shinshin86 doc above). Name the things to keep once (hair, outfit, accessories, position), not a paragraph of facial anatomy (https://note.com/lively_lilac741/n/n1b1ccbed110e).
- **Literal sex wording, natural language, not tags.** "❌ He puts his penis in her pussy, make hot sex ✅ Live-action pornographic explicit… The man slowly moves his lower body forward… Then he backstrokes and starts a repeated thrusting sex motion…" (civarchive 2851079). u/kualikuri: anchor NSFW parts "by describing their position relative to their nearest non-NSFW parts… H3 seems to understand common vernacular terms better than clinical terms" (https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/ *(indexed)*). The first sentence sets the frame; "breathless exerted breathing" in the soundscape stops random talking (civarchive 2851079 comments).
- **No negative prompt.** "H3 is CFG-distilled… BasicGuider — no negative prompt, no CFG. Put exclusions in the positive prompt" (https://civitai.com/models/2920367/). Official: "Ban lists add unwanted concepts" (docs.comfy.org prompt guide). We already do this.
- **Camera:** one camera phrase; "Do not make large facial movements and camera movements at the same time" (note.com above). Static camera for sex clips.

### (b) Poses and sex acts: LoRAs + start image, not prompt alone
- **The start image carries the pose.** "The model will take shortcuts to whatever sex type it sees" in the input image; "Use a better start image… so that composition is closer up and able to be more detailed… Increase the resolution and decrease length" (10Eros author, civarchive 2851079 comments).
- **Concept/position LoRAs are standard.** "For t2v and even some i2v you should 100% be loading mystic_v4, anatomy enhancer, or a related concept lora on top", beta5 needing "lower strength 0.2-0.6"; "1 additional lora at 0.5 would've saved you '100 generations'"; "If there's a lora for the concept you probably want to use it" (civarchive 2851079). Reddit stack: "MysticXXX to 0.5 for general use or 0.8-1.0 for NSFW" (u/Chiduk99); "base model with Mystic on 0.5 and some concept specific lora based on the scene" (u/Significant-Baby-690); "2-3 LoRAs for the same thing, all with lower weights" (u/kualikuri) (https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/ *(indexed)*). Start low: "I always, always start at 0.10 with H3 for every lora" (u/DaddyWolfgang, civarchive 2851079).
- **Key LoRAs (base MiniMax H3):** MysticXXX v4, anatomy, "0.2-1" (https://civarchive.com/models/2856467?modelVersionId=3266628); HMNSFW AIO V2.5, all-in-one sex motion, i2v 0.6-0.8 (https://civarchive.com/models/2834417?modelVersionId=3268303); HMMisDog, missionary/doggy POV, no trigger, Euler/simple 8, shift 6 (https://civarchive.com/models/2924146?modelVersionId=3308736); Blowjob v3 trigger `bl0w_j0b` (https://civarchive.com/models/2845331?modelVersionId=3212494); Lotus position (https://civarchive.com/models/2987266?modelVersionId=3386925).
- **Known model faults that match ours (so not only our prompts):** 10Eros "goes overboard removing clothes and strips them off… often just disappearing rather than ripping them off" and "struggles with actually adhering to a first frame" (u/jenniferhoustonpancakes); the woman thrusts instead of the man by default (u/MisticRain69); penis/position shifts mid-clip (civarchive 2851079 comments). Fix offered: a pose LoRA, a closer start image, more literal wording.
- **Pose control** beyond the start image: nobody in these threads uses ControlNet/DWPose for H3 NSFW; they use the start image plus a LoRA, or an extra reference image of the pose in REF2VA marked `partially_preserved` (civarchive 2851079 comments).

### (c) Transitions and multi-clip scenes
- **Two camps** *(10-18 file)*: (1) **one continuous take** chained on a latent tail (H3 Continuum https://civitai.com/models/2860061/, H3 Multishot https://civitai.com/models/2833322/, H3 Long Video https://civitai.com/models/2993319/, Smite79 H3-LongVideos, ttulttul H3-Continuation, which we installed Oct 18); (2) **cuts**: one still per shot, a plain I2V run per shot, about 3 takes, pick by eye, cut in an editor. A 60-90 s piece is about 12-20 shots of 3-5 s.
- **Naive last-frame chaining degrades** ("loses context and the characters and quality become bad") (https://www.reddit.com/r/comfyui/comments/1oaxtfu/ *(10-18 file)*). Latent-tail chaining keeps motion; Continuum's maintainer says it "does not claim to improve or solve cumulative image-quality drift" and keeps chains to ~3-6 chunks *(10-18 file)*.
- **First+last frame (FL2VA)** is native in H3 (`first_frame`/`last_frame`; `MiniMaxH3AddGuide` anchors an image at any frame) (https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native *(10-18 file)*). Write it as "a convergence… landing exactly on the final frame. Prefer one continuous shot" (shinshin86 doc).
- **Inside one clip**, H3 does cuts itself: `[Shot 2] At 00:03.500, the camera cuts to…` (docs.comfy.org prompt guide). A 10 s clip = "Two or three beats, at most one cut" (shinshin86 doc).
- **Identity across clips:** keep the face large and in frame ("H3 distorts faces on wide shots… keep faces reasonably large", Smite79 README *(10-18 file)*; "Keep your character's face in frame - faces carry identity between shots", Multishot). A measured r/comfyui post: close-ups drift at ~3 s, over-the-shoulder shots last the full 6.5 s (https://www.reddit.com/r/comfyui/comments/1vm8j2c/ *(indexed title/snippet only)*). Re-roll only the bad chunk with a new seed *(10-18 file)*. Anti-burn LoRA at ~0.5 on chunk 2+ (https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA *(10-18 file)*).

### (d) Settings
- **10Eros TURBO already has turbo baked in.** "Do not add LightX2V / ModelTC / other speed LoRAs", euler/simple 6 steps on 8 GB (https://civitai.com/models/2920367/). Our ST8 Euler/simple is inside the author's ranges ("Euler/simple 4-8 steps"; res_multistep/simple 6-8 "my go-to for best motion quality") (https://huggingface.co/TenStrip/10Eros-Max/blob/main/README.md).
- **beta6 vs beta5:** beta6 "does not replace b5… It is not good to run on smaller cards… designed more for… higher end systems", 8-12 steps, shift 10/3. beta5 TURBO int8 is the fast default and "Other concept Loras will also load on top more readily" (civarchive 2851079). We are on 16 GB with beta6. (Derrick picked beta6 on video, 6.2 vs 4.5, so it stays; beta5 is an optional arm later.)
- **CFG 1, BasicGuider, no negative** (civitai 2920367). **No Sage/Spectrum/SLA/cache** with reference: "they'll also destroy your quality and prompt adherence" (u/kualikuri, Reddit 1wbpwcq *(indexed)*; README: "SLA sparsity seems to destroy it").
- **Resolution:** prompt-test at ~0.3 MP, final at ~0.6 MP (u/kualikuri); 8 GB graph does 0.4 MP then a latent upscale at denoise 0.18 (civitai 2920367). Small faces smear: "Some finger digits and fine motion will smear more at low resolution" (civarchive 2851079). Our 768x1344 (~1.0 MP) at 124 f is at the top of 16 GB (night run peak 15.0-15.8 GB of 16.3).
- **Frames:** 124 f (≈5 s) standard; shift 6 is what the Hearmeman pose LoRAs are tuned on (HMMisDog card), vs our 10.

### Prompt templates (fictional adults; fill the brackets)
**T1. Solo tease, I2VA, 5 s (about 70 words)**
```
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action erotic and sensual, warm bedroom lamplight. The adult woman in <Picture 1> stays on the bed in the same pose, keeping her [hair], [lingerie colour and item], and the room as shown. She slowly slides one bra strap off her shoulder with her fingertips, then the other, looking into the lens with a small smile. The camera holds a static shot.

overall_soundscape: Quiet room tone, soft fabric rustle, slow breathing.

non_diegetic_music: N/A
```
**T2. Sex act, start image already shows the couple in position, 5 s (10Eros-author style, about 90 words; + MysticXXX 0.4-0.5 and a pose LoRA)**
```
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action explicit sexual intimate recording, [light as in the image]. The adult couple stays in the [missionary / doggystyle / cowgirl] position shown in <Picture 1> on the [bed]. He moves his hips forward in slow, steady thrusts, his penis sliding in and out of her pussy, his hands on her hips. With each thrust her body rocks and her breasts bounce. She looks at the lens, lips parted. The camera holds a static shot.

overall_soundscape: Breathless exerted breathing, soft moans, rhythmic skin contact, the bed creaking.

non_diegetic_music: N/A
```
**T3. Transition, next chunk or FL2VA bridge (2 beats, 10 s, one cut at most)**
```
[Shot 1] Continuing from the previous moment, the adult woman from <Picture 1> lies back on the bed and pulls him toward her by the hand; he climbs over her, keeping the same room and light. [Shot 2] At 00:05.000, the camera cuts to a waist-up side view: they are in the missionary position and he begins slow thrusts. Her face stays toward the lens.
```
(For FL2VA: end on the start image of the next scene, one shot, written as a path to that last frame.)

---
## PART 3: Verdict and test

### Where we overcomplicate (yes, in 6 places)
1. **Prompt:** 800-930 words with repeated face blocks and 4 phases per 5 s. Community: 2-5 sentences / about 60-120 words, one action per 5 s.
2. **Stills pipeline + head swap + PuLID:** our own data shows multi-ref and PuLID did nothing for identity; community uses one good still per shot.
3. **Multi-ref:** one start image is the baseline; extra refs only for a specific fix.
4. **Judges, gates, schema, preflight:** nobody in these communities gates every clip; review by eye, re-roll the bad one.
5. **45-beat sheets with one seed:** the community uses 4-6 latent-chained chunks or 12-20 cut shots, each with its own seed, a few takes each.
6. **Missing piece, not extra:** no NSFW concept/pose LoRA. That is where the community gets sex acts, anatomy and hand/contact quality from.

### Top 5 changes
1. **Short I2VA prompt** (T1/T2 form): alignment line, one action, one camera line, one soundscape. Name the keep-items once; drop the face block.
2. **Add MysticXXX v4 at 0.4-0.5** on every NSFW clip, plus **one pose LoRA** (HMNSFW AIO 0.6, or HMMisDog for missionary/doggy) when there is sex in frame. Start low, step up.
3. **The start image does the pose.** Sex clips start from an image already in that position, face fairly large (waist-up), aspect matching the video. No Klein/head-swap passes.
4. **Scenes = cuts or a short latent chain**, not 45 beats: 4-6 shots, each 5 s, own seed, 2-3 takes, pick by eye; join with the installed 22-frame continuation or hard cuts in an editor.
5. **Retire from the default path** (archive, not delete): judges, ArcFace gates, writer schema, 98-check preflight, multi-ref, PuLID/BFS. Keep beta6 ST8 Euler/simple shift 10/3, CFG 1, no negative, and the minors text guard.

### Small test (6 clips, one GPU job each, Derrick reviews by eye)
Settings: current KEEP (beta6 int8, Euler/simple, 8 steps, shift 10/3, 124 f, 768x1344, no RIFE), seed per clip recorded. Start images: `01_BEDROOM_LINGERIE.jpg` (approved Oct 18) for solo clips; for the sex clip, one approved start image that already shows the couple in position. If none exists, Derrick picks one existing approved panel. No new stills pipeline.
| # | Clip | Changes vs control |
|---|---|---|
| 1 | Control: our current long REF2VA prompt, no LoRA (or reuse a matched existing clip to save a render) | — |
| 2 | T1 short I2VA prompt, no LoRA | prompt only |
| 3 | T1 + MysticXXX v4 0.5 | + 1 LoRA |
| 4 | T2 sex clip from couple-in-position image + MysticXXX 0.4 + HMNSFW AIO 0.6 | + pose LoRA |
| 5 | Clip 4 with HMMisDog 0.7 instead of AIO (missionary/doggy only), shift 6 per its card | LoRA swap |
| 6 | T3: chunk 2 chained off clip 3 or 4 with the installed 22-frame continuation, short prompt | transition |
Pass = Derrick says which of 1 vs 2 and 2 vs 3 looks better (prompt effect, LoRA effect), and whether 4/5 read as the act with fewer hand/contact faults. No judges.

### Downloads needed (each is a card for Derrick; nothing downloaded)
| File | Size | Source |
|---|---|---|
| `MysticXXX_MMH3-V4.safetensors` (anatomy/NSFW concept, base MiniMax H3) | 147.91 MB | Civitai/CivArchive https://civarchive.com/models/2856467?modelVersionId=3266628 ; HF mirror https://huggingface.co/sintecs/minimax_h3_loras |
| `HMNSFW-AIO-V2.5.safetensors` (all-in-one sex motion) | ~82 MB (search-engine summary, not opened; check on the card) | https://civarchive.com/models/2834417?modelVersionId=3268303 ; HF `Hearmeman/minimax-h3-loras` (NSFW-gated page) |
| `hm_nsfw_mis_doggy_only_v16_r32_384_minimax-h3_epoch170.safetensors` (HMMisDog) | 295.80 MB | https://civarchive.com/models/2924146?modelVersionId=3308736 |
Optional, not needed for the test: Blowjob v3 (`bl0w_j0b`, civarchive 2845331, size not checked), H3-Anti-Burn-LoRA (HF Imagineer13, for chained chunk 2+, size not checked), 10Eros beta5 TURBO int8 (19.53 GB, civarchive 2851079) as a later model arm.
Licence note: Civitai pages say the MiniMax H3 Community Licence grant "excludes the European Union, the United Kingdom, the Republic of Korea and the United States of America" (https://civitai.com/models/2734359/better-human-motion-minimax-h3). That's Derrick's call; flagged, not judged.

## Not checked / gaps
- Reddit threads not opened live (blocked); quotes from indexed copies. The drift-measurement post (1vm8j2c) timed out; only its title/snippet used.
- Oct 18 results (22-frame chaining test, Part 2, run L) have no Derrick verdict in max-DECISIONS.md; check those clips before running clip 6.
- No H3 pose-ControlNet NSFW practice found; not researched further.
