# H3 / 10Eros-Max REF2VA: better prompts, native audio, lip sync and voice choice
Research for Derrick, Friday Oct 9, 2026, written ~3:05 PM CT. Read-only.
Scope: MiniMax-H3 / TenStrip 10Eros-Max (beta6 int8 8-step TURBO) image-to-video through `MiniMaxH3ReferenceToVideo` in ComfyUI. TE `qwen3vl_32b_minimax_h3_nvfp4_awq` (CLIPLoader type `minimax`), separate video and audio VAEs. Locked test shape: 768x1344, 243 frames (10 s), 8 steps, shift 10, Euler/simple, one start image of a fictional adult character.
What I did not do: touch AlienPc, run any render, install anything, or read any Grok Imagine prompts or prompt sidecar files. On the box I read P1 to P5 (for structure only), the prior research notes, the `ref2va-prompt` and `alienpc-ltx-i2v-prompting` skills, and the old harness script `/workspace/maxops/sydney-strip-2026-10-09/scripts/run_clip.py`.
Labels: **[VERIFIED]** means I checked it today in an official doc, the model card, or source code. **[AUTHOR]** means TenStrip said it. **[COMMUNITY]** means a Reddit, HF or Civitai user said it (anecdotal). **[3rd-party]** means an SEO or blog site (low weight). **[UNVERIFIED]** means my inference or estimate, not yet tested.

Deliverables:
- This note.
- `/workspace/maxops/sydney-10s-tests-2026-10-09/P1_STRIP_TWERK_10S_V4_AUDIO_DRAFT.txt`. It is a draft for your approval and is not queue-ready: it holds two variants, V4A (audio) and V4B (audio plus one spoken line).

---

## TL;DR

1. **Audio is generated on every run already. Our harness just throws it away.** `MiniMaxH3ReferenceToVideo` outputs one joint audio+video latent, and the sampler denoises both together. The old harness (`run_clip.py`) only wires `VAEDecode` (video) into `CreateVideo`, and the audio half is never decoded. The probed 10 s clip has one h264 stream and no audio stream. **Turning audio on costs about the same as it does now.** You add `VAEDecodeAudio` (sampler LATENT plus the audio VAE) and plug its output into `CreateVideo.audio` (or `VHS_VideoCombine.audio`). The extra work is an audio decode and a mux, which I estimate at seconds, not minutes [VERIFIED wiring from the official R2V template; the time is UNVERIFIED].
2. **The soundscape text already shapes the picture.** Audio and video come out of one pass with one conditioning, so changing the audio wording changes the video too. Deleting the audio sections does not count as "audio off" and is not a fair visual control. The fair control is the same prompt, decoded with and without audio. One graph can save both files from one sampler run at no extra cost.
3. **Our V3 prompt dialect is already right.** It uses the six official sections, about 450 words in `detailed_description`, `[keyframe completion]` for a start-frame shot, "The camera holds a static shot.", and no negatives. The improvements are small:
   - (a) Describe the appearance fully once in `subject_definitions` and once at the first appearance in `[Shot 1]`, then stop. V3 says "ice-blue" 7 times and "lens" 11 times; the official guide says to reuse the label "without redefining".
   - (b) Make the environment a `<Subject 2>` with its own retention line.
   - (c) Tie sound to each action inside `detailed_description` (official: "synchronized diegetic sound").
   - (d) Name physical sound sources with relative loudness in `overall_soundscape`.
   - (e) Write vocals as positives ("wordless moans"), never "no speech".
4. **Describing the subject's hair, eyes and outfit helps when it matches the picture.** It is the official pattern. It fights the reference only when it contradicts the image, or when it is re-stated so often that it crowds out the action (that second risk is UNVERIFIED). The strongest face-consistency levers are not words:
   - `ref_image_size=max`
   - more steps (turbo starves reference tokens)
   - no cache or spectrum
   - a face that is not frame-filling (community: close-ups drift at ~3 s)
5. **No negative prompt exists** (BasicGuider at cfg 1). **No prompt weighting either.** The Comfy H3 tokenizer calls the Qwen tokenizer with `disable_weights=True`, so `(word:1.3)` is read as literal text [VERIFIED in code]. **No chat template:** the H3 TE gets raw text, and its checkpoint is cut at layer 50, so it cannot write or rewrite prompts. An LLM rewriter has to be a separate model. MiniMax's own rewriter (H3-Context-IR) is hosted-only.
6. **Audio quality on our lane (8-step turbo) will be the weak spot.** Comfy says speech and timbre are weakest at 8 steps and usable from 12 up. TenStrip says H3's integrated audio is "probably it's biggest weakness", that non-turbo full-step audio is always better, and that LCM/simple is "best turbo audio", with audio shift up to 5 to 9. Community reports turbo "thumping and knocking" and "gurgling" sex sounds.
7. **Lip sync works two ways.**
   - **(A) Prompt-only:** a `<d>[English] …</d>` line makes H3 generate the voice and the mouth motion together, natively [VERIFIED as a capability, in official examples]. At 8-step turbo, expect weak or garbled speech [VERIFIED weak at 8 steps per Comfy; COMMUNITY reports of garbling].
   - **(B) Exact audio:** you supply a recorded or TTS line. Plain `ref_audio` is only a **voice-timbre reference** and the model re-synthesizes speech. To make the mouth follow your actual waveform, lock the audio into the latent with a noise mask (core ComfyUI supports audio-latent masks). Community nodes package this: `VRGDG_MiniMaxH3AudioDrive`, `MiniMax H3 LipSync Latent Setup` from ComfyUI-MiniMax-H3-LongMedia, and `ComfyUI-H3-NativeAudioLock`. Each is a new custom node, so it needs your GO.
   - **Post-process fallbacks on 16 GB:** MuseTalk 1.5 or LatentSync 1.5 (about 8 GB), or InfiniteTalk (16 GB only with block swap and lots of system RAM).
8. **You can steer the voice three ways.**
   - **Prompt words**, which is official: age, gender, pitch, timbre, speaking rate and accent, written outside `<d>`.
   - **A `<Audio N>` timbre reference**, which is loose. Community says tone carries over but accent and pronunciation do not.
   - **TTS first**, the most control. Generate the line locally (Qwen3-TTS VoiceDesign describes a fictional voice in words; IndexTTS-2 adds emotion sliders; Chatterbox and Kokoro are small), then use it as a timbre reference, an audio lock, or a post lip-sync source.
   - Use designed or synthetic voices only. Do not clone real people.

---

## Q1. Improving H3 REF2VA prompts

### 1.1 What the official sources say (structure and length)
- **Six sections, fixed order:** `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music` [VERIFIED. MiniMax official skill `h3-prompt-writing/SKILL.md`, "Ref2VA rewrites use … in that order"; ref guide]. https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
- **Length:** "For generation tasks, `detailed_description` is normally 350-500 English words. Dialogue-dense content prioritizes fitting the complete spoken timeline… A single shot does not automatically justify a shorter description." [VERIFIED, ref guide] https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
  - V3 P1 is 453 words, which is in range.
  - My V4A/V4B drafts are 513 and 524 words, slightly over because of the added sound clauses. Trim if you want to stay strictly in band.
- **No practical token cap in local Comfy.** The Qwen tokenizer is built with `max_length=99999999`. The only hard error is "MiniMax H3 text segment exceeds the supported prompt length" if a segment splits into more than one batch, and the code makes that effectively unreachable at our sizes [VERIFIED. https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py and https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py]. The hosted API caps `text` at 7000 characters (prior note 2026-10-08). The limits that matter are the trained distribution (350 to 500 words) and TE encode time, since our TE runs on CPU.
- **Detail rule:** "Make `detailed_description` as detailed and explicit as possible. For each shot, clearly establish the current composition, subject appearance and position, environment and lighting, actions and state changes, camera movement, current sound, and the points where referenced content actually appears… Avoid reducing the description to a plot summary." [VERIFIED, ref guide line 7]
- **The official skill also says:** "Always match the total duration of the description to the requested video length (4–15 seconds)." "Prefer concrete visual and audio details over abstract words like 'cinematic' or 'beautiful'." [VERIFIED, SKILL.md]
- **MiniMax says the rewrite format matters:** "H3-Context-IR is critical to the quality of the final output, so we strongly recommend incorporating it into your generation pipeline or following the 'Prompting Guidance' to build your own context-processing system." [VERIFIED, HF model card] https://huggingface.co/MiniMaxAI/MiniMax-H3. Our hand-written six-section text is that "own context-processing system".
- **The Comfy R2V template note:** "Ref2va's output is very sensitive to prompt wording; matching the reference tags precisely and being explicit about which reference drives which part of the shot tends to work best." The same note says "`beta` or `normal` scheduler tends to outperform `simple` for reference-heavy prompts". That second point is outside today's locked config, but worth a later one-axis cell [VERIFIED, template `video_minimax_h3_r2v.json` MarkdownNote]. https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json
  - Oddity: the template's own example prompt is short free prose ("CUT 1: … TRANSITION … CUT 2"), not the six-section dialect. So H3 tolerates loose prose, but the guide's six-section format is what Context-IR outputs and what MiniMax recommends. Keep six sections.

### 1.2 Does describing hair, eyes and outfit help or fight the reference?
- **Official answer: describe it, once per place, and keep it consistent.**
  - `subject_definitions`: "explain what its label denotes, its reference role, and the main features to follow". The guide's example: "`<Subject 1>` is the young woman in `<Picture 1>`, with long dark hair, a blue cardigan, and a thin silver necklace."
  - `detailed_description` §5: "At the first clear appearance of an important `<Subject N>`, describe its referenced characteristics, position in the frame, and current action… **Continue using the same label in later shots without redefining what the label represents.**"
  - The official Context-IR ref2va example re-describes the man's hair and suit once at `[Shot 1]` and then uses the label [VERIFIED, ref guide and HF README example].
- **When it fights the reference:**
  1. **The text contradicts the image** (wrong hair length, invented jewelry, a different eye color). Our skill already says "Do not invent wardrobe…" [logic; official "main features to follow" implies match].
  2. **Re-stating facial features over and over.** One search-engine summary claimed that repeated facial-feature text "can override the reference". I found no primary quote for that, so it is **[UNVERIFIED]**. It is consistent with the official "without redefining" rule, so V4 cuts the repeats: "ice-blue" goes from 7 to 3, and the face description is given once at first appearance.
- **Levers that actually hold the face** (more than words):
  - `ref_image_size=max` ("best identity fidelity", "several times slower") [VERIFIED, node doc https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo].
  - Steps: "at 4 steps a reference can end up barely applied, and a subject's pose or face angle can drift… run the base 20-step schedule; if the reference still drifts, raise… to 25" [VERIFIED, Comfy overview https://docs.comfy.org/tutorials/video/minimax/minimax-h3]. Our 8-step turbo is the main identity risk, not the wording.
  - No cache or spectrum on reference runs [AUTHOR, README].
  - Face size: r/comfyui "Measured how fast identity drifts in MiniMax H3 image-to-video: close-ups fall apart at ~3s, over-the-shoulder shots survive the full 6.5s" [COMMUNITY, I2V not REF, Aug 2026] https://www.reddit.com/r/comfyui/comments/1vm8j2c/. Our mid-thigh crop is favorable. The look-back over the shoulder in three-quarter profile is also favorable.
  - Clean, sharp, frontal, evenly lit face reference; `fully_preserved` marker [COMMUNITY via search index: r/StableDiffusion "MiniMax-H3 R2V Face issue" https://www.reddit.com/r/StableDiffusion/comments/1vihcz6/ and "I get different face every time…" https://www.reddit.com/r/StableDiffusion/comments/1vqy9bn/. Reddit blocks direct fetch, so I read these from snippets only].
  - Optional extra identity ref: a clean face crop as `<Picture 2>`, marked `partially_preserved` and "not a video frame" (prior note 2026-10-09 background swap). This is a one-axis cell later.
- **The "face-lock block" (retention line plus the evenly-lit-face sentence) is consistent with the official tools.** The guide puts locks in `retention_analysis`, not in bans. Keep it. Phrase it as positive state ("stay the same in every frame"), not "never change" [VERIFIED rule 8, Comfy prompt guide].

### 1.3 Camera language
- **Official vocabulary:** motion type + amplitude + speed, written as a natural English clause inside the shot. Types: Zoom In/Out, Push In/Pull Out, Pan, Truck, Tilt, Pedestal, Arc, Tracking, **Static Shot**, Shake Slightly/Strongly, Roll. Examples: "The camera pushes in with small amplitude at slow speed toward…", "The camera holds a static shot as the runner exits the frame." "Medium amplitude and normal speed are usually omitted." Do not stack labels at the end of a sentence [VERIFIED, base guide §4.3] https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- **The official Context-IR example** uses "The camera holds a perfectly static shot throughout the entire eight-second duration" [VERIFIED, HF README I2VA example]. Our "The camera holds a static shot." matches. V4 adds the framing ("at chest height, framing her from mid-thigh up"), which the official examples also do (composition at shot start).

### 1.4 Timing and phase cues
- **Official:** "Do not add a timestamp to the first shot." Later shots open with a cut time: "[Shot 2] At 00:03.500, the camera cuts to…". Cut only when new information arrives; otherwise use camera motion [VERIFIED, base guide §4.2].
- **Within one shot**, the official Context-IR example uses relative time words: "Early in the clip…", "As the clip progresses into the middle seconds…", "Throughout the remainder of the clip…" [VERIFIED, HF README]. Our "Phase N (~0–3s)" labels are **not in any official doc**. They are plain text the TE reads, and they have worked for us visually, but their effect is **[UNVERIFIED]**. V4 keeps them so the V3 vs V4 A/B stays about content and audio. A later one-axis cell could test "Phase (~Xs)" against relative-time prose.
- **Make the timeline sum to the clip:** 0 to 10 s at 243 frames. V3 and V4 do this (PRIMARY MOTION runs ~5.5 s to the end).
- **For dialogue, tie the line to a visible event, not an absolute timecode:** "tie a line to a visible event… rather than to an absolute timecode, which is what cut times are for" [VERIFIED, Comfy prompt guide, Dialogue and speakers]. V4B starts the line at the beginning, while she faces the lens, before her hands move.

### 1.5 Negative prompts
- **None.** "the H3 templates sample through the `BasicGuider` node… there is no negative branch and a negative prompt has no effect… a line such as `no subtitles and no on-screen text` registers text as content. Say what should be in the shot instead." In full-reference prompts, use retention markers [VERIFIED, Comfy prompt guide tip 8] https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- **Audio corollary:** our older ORC_BJ soundscape starter used "no intelligible speech" (in `2026-10-02-max-audio-sex-sounds.md`). By this rule that adds "speech". V4 uses "wordless moans" instead. Comfy's own fix for unrequested speech is to "write out both fields explicitly and regenerate" [VERIFIED].
- **Prompt weights do not exist** (see TL;DR 5) [VERIFIED code].
- **Embeddings** (`embedding:name`) are supported, but the 10 community style embeddings are SFW effects ("bullet_time", "kiss_camera"…) and not useful here [VERIFIED, Comfy prompt guide].

### 1.6 Prompt-enhancer / LLM-rewrite nodes
- **The H3 TE cannot rewrite.** The Comfy code says: "The H3 presentation is NOT chat-templated: token ids are raw prompt/label text… The conditioning is the unnormalized hidden state after LM layer 50 (the converted checkpoint is truncated there…)". The model card says "H3-Encoder uses the full pretrained weights of Qwen3-VL-32B and provides the hidden states from its 50th layer" [VERIFIED]. So there is no chat template to exploit. Wrapping the prompt in `<|im_start|>` would just be literal text. The truncated 32B cannot generate.
- **Special tokens the TE knows:** `<d>`, `</d>`, `<|cutoff|>`, `<|lyrics_start|>`/`<|lyrics_end|>`, `<|caption_start|>`/`<|caption_end|>` [VERIFIED, minimax.py]. So `<d>[English] …</d>` is a real structural token, not decoration. (The guides also mention `<scenetrans>`. It is not in that token list, so it would be tokenized as plain text [VERIFIED absence; effect UNVERIFIED].)
- **Rewriter options** (catalogued in `2026-10-08-h3max-prompting-and-autoprompt-node.md`, re-summarized here):
  - MiniMax **H3-Context-IR**: hosted API only, not open source. Needs a key. Uploads your refs. Adult-content policy unknown.
  - **ComfyUI-MiniMaxH3-Easy** `✦` optimizer (OpenAI-compatible / Gemini / Ollama) https://github.com/nkxx188/ComfyUI-MiniMaxH3-Easy
  - **pytraveler MiniMax-H3-Prompt-Rewriter** (LightX2V rewriter LoRAs on a 27B base, or GGUF writers) https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI
  - **hyukudan Prompt Enhancer / Guide Builder** https://github.com/hyukudan/ComfyUI-MiniMax-H3-Prompt-Enhancer
  - **ethanfel H3-Guide** compiler https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide
  - **JR OpenAI-compatible optimizer** https://github.com/Goldlionren/ComfyUI_JR_MiniMaxH3Node
  - **javawock7618 LLM system prompt** file https://huggingface.co/javawock7618/comfy-MiniMax-H3-workflows
  - Generic **Ollama/LLM nodes** with the official `ref-en.txt` as system prompt.
- **Do they help?** No public A/B on adult REF2VA exists **[UNVERIFIED]**. The likely value is format compliance: right markers, label consistency, duration math, audio lanes. We already get that from the `ref2va-prompt` skill.
- **Costs and risks:**
  - A resident LLM on the 16 GB card fights the DiT, and the TE is already on CPU.
  - Cloud LLMs may refuse or sanitize adult fiction.
  - Rewriters tend to add filler and "cinematic" words, which the official skill tells you to avoid.
- **Recommendation:** keep manual (skill) authoring. If you want automation, run the LLM off-GPU, on the box or an API, with the official `ref-en.txt` and our skill as system prompt. Paste the result. No AlienPc install needed.

### 1.7 Community and author prompt notes worth keeping
- **TenStrip:** "Sampling and prompt are the key to quality and success." beta6 is "a built mostly-reference hybrid… Samples on 10/3 shift… on multiple samplers like er_sde, euler, LCM, res_multistep, all having some different behaviors with prompt. It's a slow 8-12 step reference model in that configuration." [AUTHOR, README, HF last modified 2026-10-09 07:13 UTC = 2:13 AM CT] https://huggingface.co/TenStrip/10Eros-Max
  - The README's beta6 screenshot shows `ModelSamplingMiniMaxH3` 10/3 → Model Sparse Attention `vsa` keep 10% → Model Attention Backend `comfy kitchen attention` → `euler` / `simple` / **10 steps** [AUTHOR, beta6_sampling_example.png]. Our Euler/simple 8 steps at shift 10 is inside his range. Audio shift should be 3 (confirm the harness sets `shift_audio` 3).
- **TenStrip on sex-sound wording** (HF discussion #35, Sep 7, 2026): "Audio is a massive issue in H3, probably it's biggest weakness… beta5 without turbo will actually do the right sounds sometimes. Sex sound is 'soft flesh thudding and skin of the bodies clapping together' and other stuff is usually 'soft wet sliding sounds'." The original poster reported that category labels such as "Audio: blowjob, deep throat" produced "gurgling sounds" [AUTHOR + COMMUNITY] https://huggingface.co/TenStrip/10Eros-Max/discussions/35. **Lesson: describe the physical sound, not the act label.**
- **Civitai/CivArchive beta5 comment:** "the main issue with turbo-enabled stuff and H3 is the over amplified thumping and knocking sounds in NSFW scenes… the model normalizes certain sfx to ~0dB that normally are very low volume… Replacing any objects that can move (wooden table with a sturdy marble table) can help slightly." TenStrip there: "Audio is lackluster… H3's integrated audio is not good" [COMMUNITY + AUTHOR] https://civarchive.com/models/2851079?modelVersionId=3294059. V4 therefore keeps the splashes "light" and "quieter than her breathing", and names no hard props. Whether loudness words control turbo levels is **[UNVERIFIED]**.

---

## Q2. Audio: how it works, how to turn it on, cost, issues, prompting

### 2.1 How H3 / 10Eros makes audio
- **One model, one pass, two latents.** "The H3-Omni-Transformer jointly predicts video and audio latents, which are then decoded into video and stereo audio." "Neither the attention layers nor the FFN layers contain modality-specific structures" (only I/O layers and AdaLN branches are modality-specific) [VERIFIED, HF model card].
- **Audio VAE:** "uses the same encoder and decoder for both the left and right audio channels… compresses 32 kHz audio into a sequence of latent tokens with a temporal rate of 40 Hz." Output is "32 kHz stereo". Dialogue is "stable" in 11 languages including English [VERIFIED, HF model card].
- **Audio never enters Qwen.** For REF2VA a reference audio is only a text label "<Audio j>: " in the TE, and its content goes in through the audio VAE [VERIFIED, minimax.py docstring "audio never enters Qwen"]. Without `audio_vae` wired, "reference audio only conditions the text encoder" [VERIFIED, node doc].
- **Schedule:** one sigma schedule drives both. "the model inverts the video schedule onto the shared base grid to derive the audio schedule". Defaults are shift 12 and audio_shift 3. Distilled 8-step builds use 10/3 [VERIFIED, Comfy overview].
- **Steps:** "Audio settles later than the picture does… Speech and voice timbre converge last: at 8 steps they are the weakest part of the output, and 12 steps and above keep the track usable." [VERIFIED, Comfy overview]
- **10Eros:** TenStrip says the grafts left `attn_k` and MLP `fc2` alone to protect audio ("if anyone was interested where exactly audio lives in the model it is essentially between those two elements"). He also says beta5 is "slightly louder overall than the base model". He describes beta6's custom turbo as "meant to mimic how Fastv2 looks and sounds" [AUTHOR, HF discussion #7 https://huggingface.co/TenStrip/10Eros-Max/discussions/7, README, CivArchive].

### 2.2 How to enable it in ComfyUI (exact wiring)
Official R2V template wiring [VERIFIED by parsing `video_minimax_h3_r2v.json` links]:
- `SamplerCustomAdvanced.LATENT` → `VAEDecode.samples` (video VAE `minimax_h3_video_vae_int8_convrot`) → `CreateVideo.images`
- `SamplerCustomAdvanced.LATENT` → **`VAEDecodeAudio.samples`** (audio VAE `minimax_h3_audio_vae_fp32`) → **`CreateVideo.audio`**
- `CreateVideo` (fps 24) → `SaveVideo`
- Template note: "each decode node automatically pulls its own half out of the packed latent. `CreateVideo` then muxes the two into a single MP4 with synced sound."

The old harness (`run_clip.py`) has nodes 12 `VAEDecode` → 14 `CreateVideo(images only)` → 15 `SaveVideo`. The audio VAE (node 5) goes only to the REF2VA node, and the results json writes `"audio": "STRIPPED"` [VERIFIED, local file]. The 10 s clip `B6_10S_P1STRIP_EULER_ST8.mp4` probes as h264 only, 243 frames, 10.125 s [VERIFIED ffprobe].

**Draft harness patch (not applied, for whoever owns the harness):**
```python
"13":  {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["11", 0], "vae": ["5", 0]}},
"14":  {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "audio": ["13", 0], "fps": 24}},
"15":  {"class_type": "SaveVideo",   "inputs": {"video": ["14", 0], "filename_prefix": PREFIX + "_AUD", "format": "auto", "codec": "auto"}},
"14m": {"class_type": "CreateVideo", "inputs": {"images": ["12", 0], "fps": 24}},
"15m": {"class_type": "SaveVideo",   "inputs": {"video": ["14m", 0], "filename_prefix": PREFIX + "_MUTE", "format": "auto", "codec": "auto"}},
"16":  {"class_type": "SaveAudio",   "inputs": {"audio": ["13", 0], "filename_prefix": "audio/" + PREFIX.split("/")[-1]}},   # optional standalone FLAC
```
- Also change `res["audio"]` to `"DECODED"`, and add an audio-stream ffprobe (`-select_streams a:0 -show_entries stream=codec_name,sample_rate,channels`).
- The mp4 pick-loop takes the last `.mp4` it sees, so it should pick the `_AUD` file explicitly.
- **With VHS:** `VHS_VideoCombine` has an optional `audio` (AUDIO) input. Wire `VAEDecodeAudio` into it (from VideoHelperSuite docs; I did not re-fetch today, but the AUDIO input is standard there).
- **Audio VAE must be fp32.** We already load `minimax_h3_audio_vae_fp32`. A community GGUF README warns that fp16/bf16 audio VAE "will sound like a buzzing electrical short" [COMMUNITY] https://huggingface.co/Abiray/10Eros-Max-Hybrid-Beta5-GGUF

### 2.3 Render-time cost
- **Denoise: no change.** The audio latent is already in the sequence on every run (node doc: the `latent` output is "Empty audio-video latent… including the aligned video latent and audio latent") [VERIFIED].
- **Rough share of the sequence (my arithmetic, [UNVERIFIED] exact packing):**
  - Video VAE is f16 t4, so 768x1344 gives a 48x84 latent. With the 2x2 patch grid that is about 1,008 tokens per latent frame. 243 frames at t4 is about 61 latent frames, so roughly **61k video tokens**.
  - Audio at 40 Hz for 10.1 s is about **405 tokens per channel** (about 810 if both channels are packed).
  - So audio is roughly **1% of the sequence**.
- **Added cost of turning it on:** `VAEDecodeAudio` (the 577 MB fp32 VAE decoding about 10 s of 32 kHz stereo) plus the mux. I estimate **under ~10 s** and possibly ~1 to 2 s on GPU, more on CPU under `--lowvram` **[UNVERIFIED; measure it]**. VRAM is the audio VAE load (~0.6 GB fp32) at decode time.
- **Re-runs:** if only decode or save nodes are added and nothing upstream changes, Comfy's execution cache should reuse the sampler output and only run the new nodes [UNVERIFIED for our `--lowvram` / no-pinned argv; cache is per-input-hash].
- **Reference wall times for the A/B budget** [local research `2026-10-06-h3-longer-length-vs-wall.md`, beta5 TURBO, older argv]: 10 s @ 768x1344 ST8 hot = **375 to 484 s** (~6 to 8 min). beta6 int8 timing on today's argv is not in our files. Per-new-prompt TE encode on CPU was user-reported at ~6 to 7 min (never logged) **[UNVERIFIED]**.

### 2.4 Known audio quality issues
| Issue | Source | Mitigation |
|---|---|---|
| Speech and timbre weakest at 8 steps; usable from ≥12 | [VERIFIED Comfy overview] | Expect weak dialogue on our lane. A later quality cell is non-turbo 20 to 25 steps |
| Turbo audio worse than full-step | [AUTHOR README] | LCM/simple 6 to 9 "best turbo audio"; non-turbo 20 to 25 "best overall" [AUTHOR HF #35] |
| Thin audio at low steps | [AUTHOR, CivArchive and HF #35] | `shift_audio` "default 3 or maybe up to 5-9" (one-axis cell) |
| Over-loud thumps and knocks, SFX normalized to ~0 dB on turbo NSFW | [COMMUNITY CivArchive] | Name soft or wet sources and relative loudness; avoid props that knock; post-mix if needed |
| "Gurgling" when prompting act labels | [COMMUNITY + AUTHOR HF #35] | Describe physical sound ("soft wet sliding sounds", "soft flesh thudding and skin… clapping") |
| Gibberish speech over silent stretches; garbled speech when prompting talk | [COMMUNITY r/comfyui 1vyweja, 1vi4n6r] | Fill the timeline with explicit non-speech vocal and ambience text; keep dialogue short; more steps |
| Unrequested speech or music | [VERIFIED Comfy tip 7] | Write both audio fields explicitly; `non_diegetic_music: N/A` |
| Wrong speaker gets a ref voice (multi-speaker) | [VERIFIED Comfy, Dialogue and speakers] | One speaker per shot; tie the line to a visible event |
| Buzz with fp16 audio VAE | [COMMUNITY GGUF README] | Keep fp32 (we do) |

### 2.5 Audio prompt best practices (official lanes plus adult-fiction specifics)
- **Lanes** [VERIFIED, base guide §5 and Comfy tip 7]:
  - Dialogue, singing and diegetic music go in `detailed_description`, in the shot where they happen, with `(S1)` and `<d>`.
  - `overall_soundscape` is **1 to 4 sentences** of ambience, physical action sounds and **non-verbal human sounds** ("breathing, laughter, or panting"). `N/A` only for complete silence.
  - `non_diegetic_music` is 1 to 3 sentences of audience-only score (instruments, tempo, dynamics, no mood words), or `N/A`.
- **Synchronized SFX belong in the shot text.** "Every detail should correspond to something visible or audible: … spoken language, and synchronized diegetic sound." [VERIFIED, base guide §4] V4 puts one sound clause per phase (cloth peel, small splash, water slap on each drop, breath huffs).
- **Physical-source vocabulary** [AUTHOR examples above]: wet cloth peeling from skin, light water slaps or splashes, soft skin contact, soft flesh thudding, wet sliding, close breathing, breath catches, short huffs, soft breathy wordless moans. **Avoid category labels** ("sex sounds", "erotic audio") and negatives ("no speech").
- **Loudness words:** state a hierarchy ("quieter than her breathing", "faint distant surf", "close and clear in the foreground") [UNVERIFIED that turbo obeys them; free to try].
- **Moans:** keep them non-lexical and in `overall_soundscape` (plus an optional synced mention in PRIMARY MOTION). Words go only in `<d>`.
- **Music:** keep `N/A` for v1. If you want club music, it is diegetic ("playing from the speakers") and goes in the description.

---

## Q3. Improved template (REF2VA, start-frame shot, with audio)

The template follows. Placeholders are in {braces}. Remove the `(S1)`/`<d>` sentence for no-dialogue cells.

```text
subject_definitions:
<Picture 1> is the first frame of [Shot 1]: {one-line description of the opening frame: who, where, crop, light}.
<Subject 1> is the adult {woman/man} from <Picture 1>: {face shape}, {eye color}, {nose/lips if distinctive}, {hair color, length, style, parting, wet/dry}, {build}, {outfit with material and color}.
<Subject 2> is the {environment} in <Picture 1>: {3–5 concrete scene anchors}.
{Optional: <Picture 2> is a clean close-up face reference of <Subject 1>, not a video frame.}
{Optional, audio ref: <Audio 1> is the voice-timbre reference for <Subject 1> (S1).}

summary:
[keyframe completion{ + audio reference if <Audio 1>}] Starting from <Picture 1>, <Subject 1> {beat 1}, then {beat 2 / get-into-position}, then {PRIMARY MOTION}. {Wardrobe end state}. The camera holds a static shot. The sound is {main sound sources in one clause}.

retention_analysis:
<Picture 1> ([Shot 1] first frame): fully_preserved - the opening composition, {crop}, {key scene anchors} and {light} match <Picture 1>.
<Subject 1> (appears in [Shot 1]): fully_preserved - her face, {eye color} eyes, {hair}, skin tone and body proportions stay the same in every frame; {garment A} stays on; {garment B} comes off and {where it ends}.
<Subject 2> (appears in [Shot 1]): fully_preserved - {scene anchors} are retained.
{<Picture 2>: partially_preserved - only the facial identity of <Subject 1> is used.}
{<Audio 1>: reference - her voice follows the timbre of <Audio 1> without copying the original signal.}

detailed_description:
{1–2 style/light sentences: medium, light direction and color on skin, material detail.}
[Shot 1] The camera holds a static shot {at chest height, framing her from mid-thigh up}. <Subject 1>, {short appearance recap ONCE, matching the picture}, {position and action at frame 0}. {Face-lit sentence.}
Phase 1 (~0–{t1}s){, the line}: {Optional dialogue: facing the lens, <Subject 1> (S1), a young adult woman with a {pitch}, {timbre}, {breathy/husky/clear} voice and a {accent} accent, says {speed/manner}, <d>[English] {≤8 words}</d> Her lips and jaw move clearly with each word, and exactly as her voice stops her lips close into {expression}.} {Action with hand roles, five fingers, cloth physics.} {Synced sound clause: "the wet cloth makes a soft peeling sound…"}
Phase 2 (~{t1}–{t2}s): {action} {sound clause}.
Phase 3 (~{t2}–{t3}s), get-into-position: {ordered STAND/TURN/SETTLE beats; head/eye line}.
PRIMARY MOTION (~{t3}s–end): {act name}. {Tempo: ~N cycles per second}, {amplitude}, {body physics/impact}, {supports and hands}, {head/eyes}. {Synced sound: "each drop lands with a light wet slap…", breath and wordless moans.} She ends mid-{motion}, {end state}.

overall_soundscape:
{Ambience bed} continues throughout: {2–3 quiet environment sources}. Close and clear in the foreground are {breathing}, {physical action sounds in order}, with soft, breathy, wordless {moans/sighs} rising and falling with the rhythm. {Loudness hierarchy: "The {impact sound} stays light and wet, quieter than her breathing."}

non_diegetic_music:
N/A
```
Template rules (all from the sources above):
- Describe the appearance once in definitions and once at first appearance, matching the image.
- Use the label after that.
- No negatives.
- One act.
- Timeline sums to the clip.
- About 350 to 500 words in `detailed_description`.
- At most one short line per ~3 s.
- Voice descriptors go outside `<d>`, words inside.
- Close the lips after the line.

**Rewritten P1 → V4** is saved at `/workspace/maxops/sydney-10s-tests-2026-10-09/P1_STRIP_TWERK_10S_V4_AUDIO_DRAFT.txt`. It is not runnable as a whole file: there are header lines on top, plus V4A and V4B between BEGIN/END markers. What changed versus V3:
1. The pool is now `<Subject 2>`, with its own `fully_preserved` line, per the official environment-as-subject pattern.
2. The summary gains one sound clause.
3. Face repeats are cut ("ice-blue" goes from 7 to 3).
4. The framing clause "at chest height, framing her from mid-thigh up" is added.
5. One synced sound clause per phase.
6. The soundscape is rewritten with a loudness hierarchy and "wordless" moans.
7. V4B adds the one-line dialogue in a new Phase 1 (~0 to 2 s, facing the lens), with voice descriptors and the lip-close cue from the official Context-IR example: "his mouth movements naturally syncing… Exactly as his voice stops, his lips meet… and his jaw ceases speaking motion" [VERIFIED, HF README ref2va example]. The peel is compressed into ~2 to 4 s, and "her lips pressed together" is added to the moan beat so there is no mouthing later.
8. V4B dialogue line: `<d>[English] Want to see what's under this?</d>`. The speaker is "(S1), a young adult woman with a soft, breathy, low voice and a relaxed American accent… says slowly and teasingly". Edit the words, voice or accent to taste.

---

## Q4. Lip sync

### 4.1 Prompt-only (quoted line → H3 makes voice and mouth together)
- **Capability is real and native.** Joint AV generation; official examples speak lines with `(S1)` and `<d>`; the Context-IR ref2va example animates a face to speak "user-provided dialogue" [VERIFIED].
- **How well at our settings:** Comfy says speech is weakest at 8 steps [VERIFIED]. Community reports garbled speech when prompting a character to talk ("Even without audio added, when i prompt the character to speak, the audio is garbled") [COMMUNITY r/comfyui https://www.reddit.com/r/comfyui/comments/1vi4n6r/], and gibberish over silent stretches [COMMUNITY r/comfyui https://www.reddit.com/r/comfyui/comments/1vyweja/]. On 10Eros 8-step turbo, expect intelligible-but-rough at best and gibberish at worst. **Must test** [UNVERIFIED on our stack].
- **Craft that should help** (official plus inference):
  - Face the lens during the line.
  - Use a short line (≤ ~8 words for a 10 s clip).
  - Put voice descriptors outside `<d>`.
  - Explicitly close the lips after the line.
  - Fill the remaining time with non-lexical vocals and ambience text.
  - Don't put words in the soundscape.
- One Reddit user says typing the exact dialogue in double quotes stabilizes facial geometry. That is anecdotal, with a pseudo-technical explanation, and conflicts with the official rule that quotes are for on-screen text and `<d>` is for speech [COMMUNITY r/comfyui https://www.reddit.com/r/comfyui/comments/1w3ccfi/]. **Do not adopt.** Use `<d>`. Quotes risk on-screen text.

### 4.2 Audio-input paths (exact words and timing)
- **`ref_audio_N` = timbre reference, not a driver.** Official marker semantics: `reference` = "only timbre, rhythm, music style, dialogue content, or sound texture is referenced" [VERIFIED]. Community: "H3 treats it as a voice timbre reference, not a lipsync driver… Your file never gets played back"; tone similar, accent and pronunciation missed [COMMUNITY 1vyweja]. Community tips from the same thread (UNVERIFIED): trim the ref to about the line's length, and feed `ref_video_audio` rather than `ref_audio`. Note the 2 to 15 s minimum per clip [VERIFIED].
- **`fully_copy` marker:** officially means "the complete source audio serves as the target video's complete final audio track" [VERIFIED]. It tells the model the intent, but plain sampling still regenerates the audio latent. The waveform is guaranteed only with a latent lock [inference; supported by community nodes existing for exactly this].
- **Latent audio lock (core-capable, packaged by community nodes):**
  - Core ComfyUI PR #15375 "added per-token noise masks for MiniMax H3, covering both the video and audio latents… `0` preserves… audio masks [snap] to whole latent frames" [VERIFIED, Comfy native page https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native].
  - In principle: encode your 10.125 s track with the audio VAE, put it in the audio half of the AV latent, set the audio mask to 0 (keep) and the video mask to 1 (generate). The mouth then follows a fixed audio track. Building this by hand in core needs latent split and concat nodes; I did not confirm core ships an "audio half replace" node **[UNVERIFIED]**.
  - Packaged nodes (each needs your GO to install; none tested by us):
    - **`VRGDG_MiniMaxH3AudioDrive`** (comfyui-vrgamedevgirl): "replaces H3's blank audio latent with your encoded source track, locks it with a zero-denoise mask… passes your original audio through untouched for the final mux". Used in the RunComfy "Talking & Singing Dual Character" REF2VA workflow https://comfy.icu/node/VRGDG_MiniMaxH3AudioDrive · https://github.com/vrgamegirl19/comfyui-vrgamedevgirl · https://www.runcomfy.com/comfyui-workflows/minimax-h3-comfyui-talking-singing-dual-character-4-step-acceleration
    - **`MiniMax H3 • LipSync Latent Setup`** (ComfyUI-MiniMax-H3-LongMedia, vizart-vj): `audio_denoise` 0 = preserved exactly; `video_denoise` 0.35 default (that default is for re-animating an existing video); "describe the semantic action ('speaks', 'sings') and let the source audio own the phonetic timing" https://comfy.icu/node/MiniMaxH3LatentLabLipSyncSetup · https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia
    - **`ComfyUI-H3-NativeAudioLock`** (Shrek3OnVH5 music-video pack): "At non-vocal timestamps, explicitly instruct the model that the mouth remains closed." https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow
  - VRAM: the lock adds only an audio-VAE encode, so it should fit our 16 GB the same as a normal run [UNVERIFIED].
  - Quality is unknown on 10Eros 8-step turbo. The RunComfy page claims "tight lip sync" at 4-step turbo [3rd-party marketing].
- **Post-process lip-sync** on a finished mute or native clip (third-party VRAM figures, UNVERIFIED):
  - **MuseTalk 1.5**, ~8 GB, 256x256 face inpaint, fast; soft mouth at our resolution.
  - **LatentSync 1.5**, ~8 GB; 1.6 needs ~18 GB, too big.
  - **Wav2Lip**: old, low-res mouth.
  - **InfiniteTalk** (Wan2.1-14B based): works on 16 GB with block swap and 64 GB RAM, ~2 to 3 min per 81-frame window at 480p on a 4060 Ti. It re-animates head and body too, so it could alter our twerk motion [COMMUNITY r/comfyui https://www.reddit.com/r/comfyui/comments/1nvyyol/; https://github.com/bmwas/InfiniteTalk].
  - Wan 2.2 S2V uses an English-trained wav2vec2 encoder [COMMUNITY 1vyweja].
  - Comparison source: [3rd-party] https://news.creeta.com/en/open-source-lip-sync-models-2026/
- **Recommendation:** test prompt-only first; it is free. If the words come out garbled at 8 steps, the strongest next step is TTS plus an audio lock (needs one node install). Post-lip-sync is the fallback for the hero clip only.

### 4.3 How to test lip sync (included in the A/B plan below)
- **Intelligibility:** transcribe the AUD file with Whisper (faster-whisper on the box CPU, which runs off AlienPc) and compare to the `<d>` text. Report word error rate and whether extra words or gibberish appear elsewhere.
- **Sync:** step frames around the line (~0 to 2 s). Check that mouth opening matches syllables and that the lips close when the voice stops (the prompt asks for this). Optional objective score: SyncNet LSE-C/LSE-D (heavy; skip for v1).
- **Identity during speech:** compare face frames at 0.5 s, 1.5 s and 3 s against `<Picture 1>`. Speech mouth motion is where faces melt [COMMUNITY 1w3ccfi].
- **Voice match:** does it sound like "young adult woman, soft, breathy, low, relaxed American"? Count extra or wrong voices.
- **Side-effect check:** did the added line change or slow the peel, turn or twerk compared with V4A, same seed?

---

## Q5. Voice choice

1. **Prompt cues (official, free).** "When a speaker first appears, provide enough information… such as character type, age, gender, whether the person is on-screen, pitch, timbre, speaking rate, or accent." Example: "The young woman with a quiet, breathy voice (S1) says: <d>[English] …</d>" [VERIFIED, base guide §4.4]. The ref guide's example uses "in a casual young male voice with a playful tone and an easy conversational pace" [VERIFIED]. At 8 steps, timbre is the last thing to converge, so expect drift [VERIFIED Comfy].
2. **Reference audio clip (`<Audio 1>`, marker `reference`).** Officially supported for timbre and delivery: "<Audio 2>: reference - the target speaker follows <Audio 2>'s voice timbre and measured delivery without copying the original signal." [VERIFIED]. The clip must be 2 to 15 s and must be paired with an image (audio-only is not allowed) [VERIFIED, HF card]. Community: tone carries, accent and pronunciation are weaker [COMMUNITY]. Ethically and legally, use only a voice you made (TTS-designed) or one with documented consent. No real-person cloning.
3. **TTS first, then drive.** Generate the exact line with a local TTS, then either (a) use it as `<Audio 1>` timbre reference (loose), (b) lock it into the latent (exact; needs a node install), or (c) post-lip-sync it.
   - The line must be ≥2 s as a ref clip, so pad it with a breath or silence.
   - For a lock it must be exactly the clip length: 10.125 s, line at 0 to 2 s, then quiet or breaths.
   - **Local TTS that fit 16 GB** (VRAM and features from repo READMEs or 3rd-party roundups, UNVERIFIED on AlienPc). All can also run on the box CPU, slowly, so the AlienPc GPU queue is never touched:

| Model | Size / VRAM | Voice steering | Notes |
|---|---|---|---|
| **Qwen3-TTS 1.7B VoiceDesign** | ~3 to 6 GB | **Describe the voice in words** ("young woman, soft breathy low voice, relaxed American accent") with no cloning | Best fit for fictional characters. ComfyUI: DarioFT/ComfyUI-Qwen3-TTS or TTS-Audio-Suite. https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign · https://github.com/DarioFT/ComfyUI-Qwen3-TTS |
| Qwen3-TTS 0.6B/1.7B Base/CustomVoice | ~3 to 6 GB | Preset or cloned voice | Apache-2.0 (3rd-party roundup) |
| **IndexTTS-2 / 2.5** | ~4.7 to 5.5 GB per Audio-Suite table; 12 GB "comfortable" per 3rd-party | **8 emotion sliders**, emotion ref audio, text mood | Best delivery control (breathy/teasing via emotion mix). https://github.com/index-tts/index-tts · https://localaimaster.com/blog/indextts-2-setup-guide [3rd-party] |
| Chatterbox (Turbo / Multilingual) | 0.5B, ~4 to 6 GB | Zero-shot clone + one "exaggeration" knob | MIT |
| VibeVoice 1.5B (7B = 16 GB+, too big beside H3) | ~5.4 to 8 GB | Multi-speaker, long-form | |
| F5-TTS | ~4 to 6 GB | Clone from reference | |
| Orpheus 3B | ~8 to 12 GB | Emotion tags (e.g. sigh/gasp/groan; tag list from memory, UNVERIFIED) | Apache-2.0 |
| Kokoro-82M | ~2 to 3 GB / CPU | 54 preset voices only | Fastest; least expressive |

   - One wrapper covers most of these: **diodiogod/TTS-Audio-Suite** (Qwen3-TTS, IndexTTS-2, VibeVoice, Chatterbox, F5, Higgs, RVC…) https://github.com/diodiogod/tts-audio-suite.
   - **Caveat:** TTS models are good at words and weak at moans and non-verbal adult vocalization. Keep moans native (H3 soundscape) and use TTS only for the spoken line [inference].
   - **Licenses** vary by model. Check before commercial use (H3 local outputs already need a MiniMax commercial license per Comfy).

---

## Fair A/B test plan (draft. Do not run until the 30-run queue is done and you say GO)

**Locked for every cell:** same `<Picture 1>`, **same seed S** (pick one; a second and third seed come later for robustness), 10Eros beta6 int8 8-step TURBO, Euler / simple, 8 steps, `MiniMaxH3SigmaShift` video 10 / audio 3, 768x1344, `length` 243, `ref_image_size=match`, same argv, no LoRA, no cache. One graph saves **both** `_AUD` (with audio) and `_MUTE` (video only) from the same sampler output, so audio off vs on is a same-latent comparison by construction.

| Cell | Prompt | Audio | Extra | Question it answers |
|---|---|---|---|---|
| **C0** | V3 (current file) | MUTE + AUD (same run) | none | What does our current prompt already sound like? Baseline picture. Sanity: `_MUTE` frames must equal `_AUD` frames (`ffmpeg -f framemd5` on both). Should also match an earlier V3 render at the same seed, if one exists, modulo GPU nondeterminism [UNVERIFIED] |
| **C1** | **V4A** | MUTE + AUD | none | Does the V4 rewrite improve picture (ID, peel, turn, twerk amplitude) and/or audio (synced splashes, breath, no thump, no gibberish) vs C0? |
| **C2** | **V4B** (dialogue) | MUTE + AUD | none | **Lip-sync L0, prompt-only:** intelligibility, sync, lip close, face stability during speech, voice match; side-effects on motion vs C1 |
| C3 (optional, one-axis audio) | V4A | AUD | `shift_audio` 3 → **9** | Author's low-step audio fix. Picture may shift slightly too (shared schedule) |
| C4 (optional, after GO) | V4B + `<Audio 1>` TTS line padded to ~3 s, marker `reference` | AUD | `ref_audio_1` + `audio_vae` (already wired) | **Lip-sync L1:** does a designed TTS voice steer timbre and words? (no new nodes needed) |
| C5 (needs install GO) | V4B prompt text, TTS track padded to exactly 10.125 s locked via `VRGDG_MiniMaxH3AudioDrive` or LongMedia LipSync Setup (`audio_denoise` 0) | AUD = your track | 1 custom node | **Lip-sync L2, exact audio:** mouth follows a fixed waveform? Prompt states lips closed outside the line |
| C6 (fallback, offline) | C1 `_MUTE` + TTS line | post | MuseTalk 1.5 or LatentSync 1.5 | **Lip-sync L3, post:** cost vs quality of post-dub |

**Order:** C0 → C1 → C2 first; these are the core. Decide C3 to C6 after watching.
**Fairness rules:**
- Change one thing per cell except V3 vs V4, which is a whole prompt-version comparison by design. Score it as such.
- Don't remove the audio sections to make a "silent" control: that changes the picture conditioning.
- Blind the reviewer to the cell label for the picture pass.
- Watch the picture pass muted first, then the audio pass, so plausible moans don't rescue a weak picture (our 10-02 rule).
- Confirm ≥2 more seeds before crowning anything.

**Scoring sheet** (words only, no PASS/KEEP per our rules):
- **Picture:** face match at 0 / 3 / 6 / 9 s; bikini-top peel integrity (one garment, air gap, drop and float); turn and squat without melt; twerk tempo (~2 bounces/s) and amplitude; bottoms stay on; hands with five fingers.
- **Audio:** splash timing vs bounce; loudness balance (thump/knock count); breath and moans present and wordless; unrequested speech or music (yes/no); clipping and artifacts.
- **Lip sync (C2, C4, C5):** Whisper transcript vs `<d>` text; mouth-syllable alignment by frame stepping; lips close after the line; extra gibberish later; voice matches descriptors.

**Time cost estimate** (beta6 timings on today's argv are not in our files; numbers scale from beta5 10 s ST8 hot 375 to 484 s, [UNVERIFIED]):

| Cell | Gen | TE re-encode (CPU, new prompt text) | Audio decode + mux | Est. wall |
|---|---|---|---|---|
| C0 | ~6 to 8 min | cached if V3 was just encoded; else ~6 to 7 min (user-reported) | <~10 s | 6 to 15 min |
| C1 | ~6 to 8 min | ~6 to 7 min (new text) | <~10 s | 12 to 15 min |
| C2 | ~6 to 8 min | ~6 to 7 min | <~10 s | 12 to 15 min |
| **Core total (C0 to C2, one seed)** | | | | **~30 to 45 min** |
| C3 | ~6 to 8 min | cached (same text as C1) | <~10 s | 6 to 8 min |
| C4 | ~6 to 8 min (+ small audio-ref encode) | ~6 to 7 min (text changed) | <~10 s | 12 to 15 min, plus TTS gen (seconds on GPU, ~1 to 3 min on box CPU, UNVERIFIED) |
| C5 | ~6 to 8 min | cached if same text as C4 | <~10 s | 6 to 15 min, plus node install and Comfy restart (needs GO; restart blocked while the queue is live) |
| C6 | n/a | n/a | n/a | MuseTalk: minutes on GPU; separate install |
| +2 seeds for C0 to C2 | ×2 gens | cached TE | | +~40 to 50 min |

Audio on vs off itself: **~0 extra generation time** (one sampler run, two save nodes); only decode and mux seconds.

---

## Open items / NO_DATA
1. Whether the current 10 s harness (not the old `run_clip.py`) sets `shift_audio` 3 with `shift_video` 10. I did not see that file.
2. beta6 int8 wall time on today's argv, and real TE CPU encode time per new prompt (never logged).
3. Whether Comfy's cache survives our `--lowvram` / no-pinned argv for decode-only re-runs.
4. Whether core ComfyUI has a node to replace the audio half of an H3 AV latent without custom nodes (needed for a no-install audio lock).
5. No public A/B of prompt-rewriter nodes on adult REF2VA.
6. Whether loudness words in `overall_soundscape` actually tame turbo thumps.
7. Whether "Phase N (~Xs)" labels outperform official relative-time prose.

## Sources (accessed Oct 9, 2026)
**Official, MiniMax**
- HF model card (audio VAE 32 kHz / 40 Hz, H3-Encoder layer 50, Context-IR, ref limits, Context-IR examples incl. lip-sync wording): https://huggingface.co/MiniMaxAI/MiniMax-H3 (last modified 2026-08-13)
- Full-reference guide: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- Base guide (camera table, speakers/voice descriptors, soundscape/music rules): https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- Official skill: https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md
- H3-Context-IR API: https://platform.minimax.io/docs/api-reference/video-generation-v2-h3-context-ir

**Official, Comfy**
- Overview (steps, audio converges last, shifts, sparse attention keeps audio rows dense): https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- Prompt guide (no negative branch, audio lanes, dialogue rules, multi-speaker ref mis-assignment, embeddings): https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- Native workflows (AddGuide with audio, latent noise masks for audio #15375): https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native
- Node doc: https://docs.comfy.org/built-in-nodes/MiniMaxH3ReferenceToVideo
- R2V template JSON (VAEDecodeAudio → CreateVideo wiring; scheduler note): https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json
- TE code (not chat-templated, special tokens, `disable_weights=True`): https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py · https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py

**Author (TenStrip)**
- README + beta6 sampling screenshot: https://huggingface.co/TenStrip/10Eros-Max (last modified 2026-10-09 07:13 UTC = 2:13 AM CT)
- HF discussion #35 (audio wording, shift 5 to 9, LCM best turbo audio): https://huggingface.co/TenStrip/10Eros-Max/discussions/35 (Sep 6 to 13, 2026)
- HF discussion #7 (where audio lives; attn_k/fc2): https://huggingface.co/TenStrip/10Eros-Max/discussions/7
- CivArchive beta5 page + comments (thump/knock, "audio lackluster"): https://civarchive.com/models/2851079?modelVersionId=3294059

**Community**
- r/comfyui identity drift measurement: https://www.reddit.com/r/comfyui/comments/1vm8j2c/
- r/StableDiffusion R2V face issue: https://www.reddit.com/r/StableDiffusion/comments/1vihcz6/ · different face every time: https://www.reddit.com/r/StableDiffusion/comments/1vqy9bn/
- r/comfyui exact audio / ref audio is timbre only: https://www.reddit.com/r/comfyui/comments/1vyweja/
- r/comfyui Minimax lip sync not working (garbled): https://www.reddit.com/r/comfyui/comments/1vi4n6r/
- r/comfyui face melting during audio-driven dialogue: https://www.reddit.com/r/comfyui/comments/1w3ccfi/
- r/comfyui InfiniteTalk on 16 GB: https://www.reddit.com/r/comfyui/comments/1nvyyol/
- (Reddit blocked direct fetch from the box; content is from search-index snippets.)
- Abiray GGUF README (fp32 audio VAE warning): https://huggingface.co/Abiray/10Eros-Max-Hybrid-Beta5-GGUF
- Nodes: https://comfy.icu/node/VRGDG_MiniMaxH3AudioDrive · https://github.com/vrgamegirl19/comfyui-vrgamedevgirl · https://comfy.icu/node/MiniMaxH3LatentLabLipSyncSetup · https://github.com/vizart-vj/ComfyUI-MiniMax-H3-LongMedia · https://github.com/Shrek3OnVH5/MiniMax-H3-NativeAudio-MusicVideo-Workflow
- Rewriter nodes: see §1.6 links.
- TTS: https://github.com/diodiogod/tts-audio-suite · https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign · https://github.com/DarioFT/ComfyUI-Qwen3-TTS
- Lip-sync models: https://github.com/bmwas/InfiniteTalk

**3rd-party (low weight)**
- RunComfy dual-character H3 workflow: https://www.runcomfy.com/comfyui-workflows/minimax-h3-comfyui-talking-singing-dual-character-4-step-acceleration
- Lip-sync model roundup: https://news.creeta.com/en/open-source-lip-sync-models-2026/
- TTS roundups: https://localaimaster.com/blog/best-local-tts-models · https://localaimaster.com/blog/indextts-2-setup-guide · https://apatero.com/blog/tts-audio-suite-comfyui-multi-engine-voice-complete-guide-2025

**Local**
- `/workspace/maxops/sydney-strip-2026-10-09/scripts/run_clip.py` (audio stripped wiring)
- `/workspace/maxops/sydney-10s-tests-2026-10-09/P1…P5*.txt` (structure only)
- `/workspace/cos/research/2026-10-02-max-audio-sex-sounds.md`
- `2026-10-08-h3max-prompting-and-autoprompt-node.md`
- `2026-10-08-10strip-h3max-optimal-vs-current.md`
- `2026-10-09-background-swap-prompting.md`
- `2026-10-06-h3-longer-length-vs-wall.md`
- `/home/box/agent-data/workflows/ref2va-prompt/SKILL.md`

*Research only. AlienPc untouched. No renders. Nothing installed. No messages sent. No Grok Imagine prompts or sidecars read.*
