# Storyboard and long-video review, 2026-10-15
Research only. Nothing installed or downloaded (code files under 100 KB read only), AlienPc not touched.
Sources: Reddit through Arctic Shift (posts + up to 50 comments each), the HF API + raw README/config/__init__/runtime.py/sampler.py, and the GitHub README.
Our constraints: ComfyUI 0.38.x pinned, about 64 GB RAM, an H3 render needs about 35 GiB, no SageAttention, NVIDIA driver never touched, hard cuts only, frame 0 pinned.
Skill note: alienpc-max-movie-director still lists **Method C (prior clip as <Video 1>, [video continuation])** as the source of truth and Method A (last frame as <Picture 2>) as a fallback. That conflicts with "hard cuts only". The skill should be brought in line with the current rule (see the design section).

---
## 1. H3 Prompt Studio (story mode update)
- Real URL: https://www.reddit.com/r/StableDiffusion/comments/1vqrpjn/minimax_h3_prompt_studio_story_mode_update/ (u/lololerigolo60, score 56, 18 comments)
- Repo: https://github.com/lololerigolo60/Minimax-H3-prompt-studio (25 stars, last push 2026-08-17, no license)
- **Summary:** a CustomTkinter desktop app. A local LLM (Ollama, LM Studio or llama.cpp) writes H3 structured prompts. It has 5 modes (T2VA, I2VA, FL2VA, L2VA, Ref2VA). In Ref2VA "storyboard mode" and the Story→Sequences tab you give it a reference library and a premise. Pass A writes a story of 200-500 words. Pass B splits it into N sequences as JSON, choosing refs, dialogue and camera per sequence. Pass C expands each sequence into its own isolated 6-section Ref2VA prompt.
- **Mechanics:** prompt text only. It does no rendering and no ComfyUI integration (a commenter asked for a ComfyUI export). Optional VLM auto-description (qwen2.5vl). It repairs truncated JSON and saves sessions as JSON.
- **Requirements:** Python + a local LLM endpoint. Nothing on the GPU side.
- **0.38 / hardware fit:** it never touches ComfyUI, so 0.38 is irrelevant. It could run on the box or any machine. If the LLM runs on AlienPc while H3 renders, it competes for RAM and VRAM, so plan LLM work before the render window.
- **Evidence:** weak. The top comment (12) complains there is no example. OP later posted one video. Two users call it "convenient", and one says refining a prompt is slow. Pixaroma's workflow was named as simpler.
- **Verdict: SKIP the tool, borrow the idea.** We already write 6-section Ref2VA prompts with a beat sheet (ref2va-prompt + max-movie-director). Its "isolated prompt per sequence" + refs chosen per beat matches what we do. A third-party GUI with no license adds nothing, and it can't enforce our distinct-PRIMARY-MOTION gate.

## 2. Smite79/MiniMax-H3-Longvideos (HF)
- Real URL: https://huggingface.co/Smite79/MiniMax-H3-Longvideos (GitHub mirror: https://github.com/Smite79/MiniMax-H3-LongVideos). 136 likes, 910 downloads. Created 2026-08-14, last modified 2026-10-12 10:14 PM CT. Demo Space grochowski/MiniMax-H3-Longvideos-Demo. License: no redistribution. The README calls it "a constant work in progress".
- **File list:** LICENSE, README, `__init__.py`, audio.py, conditioning.py, config.json, overlay.py, pose_control.py, restraints.py, runtime.py, sampler.py (1705 lines), shot_length.py, sound.py, test_node.py, test_pose.py, upscale.py, wardrobe.py, and `hyperflow_endpoint_v1.0.safetensors` (28 MB). **There is no workflow JSON.** The wiring is UNETLoader + CLIPLoader(type minimax) + video VAE + the *converted* audio VAE → H3-LongVideos → images/audio → Video Combine.
- **Summary:** one custom node that takes one multi-paragraph prompt and renders it shot by shot (H3 caps out at about 15 s per shot). By default **each shot starts on the last frame of the one before**. A `cut` line starts a shot fresh. The node joins everything into one video with one soundtrack.
- **Mechanics:**
  - The scene paragraph, `anchor` (framing) and `character_memory` are prepended to every shot. Each later paragraph is one shot, passed word for word. `plan_only` prints every shot's text without rendering.
  - State tracking by text parsing: restraints (`hold:`/`release:`), clothing (`remove:`/`wear:`), and `exit:`. Removed garments drop out of later descriptions. Picture tags (`<Picture N>`) are dropped from shots that open on a frame where that person is already visible. After a `cut`, a person last seen alone gets that frame as their look reference.
  - Continuity: a continued shot's prompt says "same place, same people, one moment earlier". **It also corrects colour drift.** The first frame of a continued shot is graded to match the frame it continues from, and that correction carries through the shot. This addresses the burn that builds when H3 clips are chained.
  - Shot length is either "from the beat" (about 2.2 s per action, or the spoken line at about 2 words/s + 1.5 s) or fixed at `shot_seconds`. `seconds:` overrides it. H3 Shot Length converts seconds to a valid frame count. Outputs include frames_per_shot, total_frames, shots and video_seconds.
  - Optional pose control: a half-size draft, then DWPose skeleton, then a re-render through `minimax_h3_fun_controlnet_union_pruned_int8_convrot` (models/model_patches) for the first `pose_end` of the steps. Retries on a new seed are kept if the restraint "held". This needs the comfyui_controlnet_aux DWPose ckpts.
  - Optional latent upscale (H3 latent upscaler pack) or final upscale (RTX VSR or a model). Supports FastH3 (VSA attention, `--disable-cuda-malloc`) and Hyperflow 8-step. cfg 1, denoise fixed at 1.0. One seed for the whole video.
  - Memory: it overrides ComfyUI's per-token memory estimate (120 KB vs about 105 KB per token) so the model streams instead of OOMing. The error on OOM says to lower megapixels or shot_seconds.
- **Requirements:** config says ComfyUI >=0.31 with native H3. The README recommends a hybrid fl2va/ref2va merge UNET. Pose mode needs controlnet_aux + the H3 fun controlnet. No SageAttention needed.
- **0.38 / hardware fit:** probably loads on 0.38, but this is UNVERIFIED. runtime.py imports `comfy.system_memory`, `comfy.memory_management` and `patcher.model.dynamic_pins` (dynamic-VRAM internals). Some calls are in try/except, but `_ram_available()` is not guarded. If 0.38 lacks those modules, the RAM-pin path will fail. The README also says to pull the latest version often, which works against a pinned stack. RAM: it renders shots one at a time in one process, so peak should be about one H3 render (~35 GiB) plus pose drafts, which fits in 64 GB. The model stays resident across shots, so a full minute is one long job; a crash midway loses shots unless frames are saved. Our ck-attention is fine.
- **Fit with our rules:** its default is **last-frame chaining**, which breaks our hard-cut + frame-0-pin rule. With `cut` on every paragraph it becomes a batch runner: shared anchor/memory text, a person's "last seen" frame as their look ref, and audio stitching. We already do most of that through the beat sheet. The parts we don't have: colour-drift grading (moot under hard cuts), the wardrobe/state ledger, and `plan_only`.
- **Evidence:** moderate on popularity (136 likes), but there are no example videos or user reports in the repo; we didn't check the demo Space. The project is fast-moving, has a noted fork dispute, and widgets get recreated between versions (workflow breakage).
- **Verdict: TEST, limited and later, on a copy, not the pinned production Comfy.** Test it on a clone of the 0.38 env with every paragraph set to `cut` + `plan_only` first. Meanwhile, reuse its ideas right away without installing it: (a) a per-beat wardrobe/state ledger in BEAT_SHEET.md, (b) an anchor + character_memory block repeated in every cell, (c) shot length from the beat (about 2.2 s per action). Do not adopt its last-frame chaining for product.

## 3. "MiniMax H3 can use a storyboard as a visual reference"
- Real URL: https://www.reddit.com/r/StableDiffusion/comments/1vecz21/minimax_h3_can_use_a_storyboard_as_a_visual/ (u/Kandoo85, score 246, 88 comments; video https://v.redd.it/gyp1zf3yr5hh1)
- **Summary:** OP fed one storyboard image (panels + text/dialogue) as the visual reference in the stock **R2V/Ref2VA** workflow, with a short prompt ("Use the Storyboard as a Reference"). One-shot result: H3 followed much of the panel layout, and it even read dialogue from text inside the image. OP says it worked across multiple storyboards. No custom nodes and no shared workflow.
- **Mechanics:** a single multi-panel image goes in as `<Picture N>`, and H3 does internal cuts inside one ≤15 s generation. A commenter notes that MiniMax's official T2V format has a native "Storyboard: [0s-1.5s] Shot 1…" timeline, which explains why this works.
- **Requirements:** the native H3 Ref2VA workflow. Nothing extra. A commenter asked whether output resolution can stay low while the storyboard ref stays high-res; that went unanswered.
- **0.38 / hardware fit:** fine, since it's the native workflow.
- **Evidence:** one example video; high engagement but mostly "cool". One user (retroblade) couldn't reproduce it. Another suggests 4 separate images + a proper prompt would beat a single sheet. It's not a long-video method: everything happens inside one generation.
- **Verdict: TEST, small.** Useful for **previs**: a storyboard sheet as a composition/pose ref for a single cell, not for spanning 60 s. It doesn't fit hard-cut-per-cell directly unless one panel is used per cell.

## 4. "MiniMaxH3-Generate video from storyboard draft" (the post from the watch digest)
- Found in reddit-h3-watch/seen.json as 1x4cww3 (status reported) and in the 2026-10-12 digest (run of Oct 13), item 4.
- Real URL: https://www.reddit.com/r/StableDiffusion/comments/1x4cww3/ (u/ExpressWarthog8505, score 18, 21 comments; video https://v.redd.it/seaylbhth3vh1)
- **Summary/mechanics:** Ref2VA with `<Picture 1>` = a three-view character sheet and `<Picture 2>` = a 6-panel storyboard, whose panels are labeled `<Shot Reference 1..4>` by position. Each `[Shot N]` in detailed_description is timestamped ("At 00:02.000…, hard cut to…") and says "match the composition, character placement, and pose of <Shot Reference N> in <Picture 2>". An 8 s clip with 4 internal shots. Dual-sampling workflow (official template OK), 4-step LoRA, 9 steps total, about 2.4 MP, rented 48 GB GPU. Assets came from a ComfyUI template. No workflow file.
- **Comments:** the character-sheet description line isn't needed (`<Subject 1> is the character shown in <Picture 1>` is enough). Spell out panel reading order for comic pages. Minimum VRAM unknown.
- **Fit:** native nodes, so 0.38 is fine. 2.4 MP on 48 GB will **not** fit our budget; drop to our usual MP. The trick works inside one clip; for us, the per-panel "match composition/pose of <Shot Reference N>" wording is the useful piece.
- **Evidence:** one example, a full prompt shared, reproducible. Low score.
- **Verdict: TEST (prompt pattern).** Use per-cell: give each cell its single panel (or the sheet + "Shot Reference N") as a pose/composition ref on top of the frame-0 pin.

Other storyboard hits: llm-brainstorm/local-setup-research.md lists **comfyui-weaver** (https://github.com/GuusF/comfyui-weaver, script→storyboard→video via MCP; [UNVERIFIED], not reviewed here). Related digest items: 1x63as3 (1-2 key-pose refs beat storyboards for hard two-person choreography), and 1x6eei4/1x6jui1 (a frame from shot 1 as a ref keeps the set stable). The rg hits under cos/audits are Shorts drafts and not relevant.

---
## Recommended design: 1-minute overnight pipeline
1. **Day: beat sheet (BEAT_SHEET.md)** with 6-10 cells of about 6-10 s each. Each row has a unique PRIMARY MOTION, the pose/wardrobe state at start and end (a state ledger, borrowed from LongVideos), `seconds` set from the beat (~2.2 s per action plus settle), and its Cond still.
2. **Day: storyboard stills.** Make one pose-correct start still per cell with the stills/pose-edit pipeline. Assemble them into one contact sheet for Derrick to review. That sheet is the storyboard. The stills, not the sheet, are what get rendered.
3. **Shared text blocks:** a fixed `anchor` (look/camera/light/location) and a `character_memory` (who + current wardrobe from the ledger) pasted into every cell's subject_definitions/summary.
4. **Per-cell render (hard cut, frame 0 pinned):** Ref2VA/I2V with `<Picture 1>` = that cell's start still (frame 0), `<Picture 2>` = a **set/character frame from approved shot 1** (this morning's tip; face/hair + room only), and optionally `<Picture 3>` = that cell's storyboard panel with "match composition and pose of <Shot Reference N>". No last-frame chaining and no video continuation.
5. **Overnight queue:** cells run in order, one at a time (~35 GiB each, so never in parallel on 64 GB), 2 seeds per cell if time allows. Save each cell to its own file so a crash keeps finished cells.
6. **Morning:** watch every cell. Pick the keepers. Hard-cut concat with ffmpeg; audio stripped or one bed added. Stitch only after Derrick's GO.
7. Update max-movie-director: Method C/A becomes legacy; the hard-cut + frame-0 + shot-1-ref method becomes standard.

## Ranked tests
1. **Shot-1 frame as `<Picture 2>` across 3 hard-cut cells** vs a baseline without it (check set/face stability). Native nodes, no risk.
2. **Per-cell storyboard panel as `<Shot Reference>`** (source 4 wording) on top of the frame-0 pin, vs the pin alone. Check pose/composition match and whether it fights frame 0.
3. **Sheet-as-ref previs** (source 3): one 10-15 s generation from a 4-panel sheet at low MP, used as a cheap animatic to pick beats before the overnight run.
4. **Beat-derived shot lengths + state ledger** in BEAT_SHEET (no code needed). Measure how often wardrobe drifts between cells.
5. **H3-LongVideos on a cloned 0.38 env**: first import-only + `plan_only`, then 3 shots with `cut` on every paragraph. Watch for the unguarded `comfy.system_memory` import failing. Only do this if 1-4 leave gaps.
6. Prompt Studio: no test; at most, run its Pass B prompt idea through our own LLM for beat breakdown.
