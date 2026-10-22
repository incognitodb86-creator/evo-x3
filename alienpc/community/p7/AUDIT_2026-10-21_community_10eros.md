# AUDIT 2026-10-21: AlienPc 10Eros (MiniMax-H3) pipeline vs official + community practice

Read-only audit, written 2026-10-21 ~15:10 CT. No models loaded, no renders, no llama-swap/ComfyUI calls. Only this file was written.

## Scope and evidence
- Workflow audited: `C:\AI\community\runs\p7_r3_c3_sd1000\p7_r3_c3_sd1000_seg1.api.json` (built by `scripts\comm.py build()`, driven by `batch_queue.py`).
- Launch: `C:\AI\director\config\llama-swap.yaml` model `comfyui_auto`.
- Local docs read: custom_nodes `comfyui-minimax-h3-continuation` (README, docs/LEARNINGS.md, example workflow), `ComfyUI_MiniMax_H3_Extender` README, `MiniMax-H3-Prompt-Rewriter-ComfyUI` README, `10S-Comfy-nodes` README, official templates in `.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\` (`video_fastvideo_fasth3_i2v.json`, `video_minimax_h3_r2v.json`, `video_minimax_h3_i2v_continuation.json`), `C:\AI\community\guides\VIDEO_PROMPT_WRITING_GUIDE_{base,ref}_en.md`, `p7\KNOBS.md`, `p7\notes\p7_r3_close.md`.
- Runtime log: `ComfyUI\user\comfyui_10004.prev.log` (2026-10-21 11:35-12:16 CT, three seg renders).
- Machine: RTX 5070 Ti 16 GB, 63.7 GB RAM, ComfyUI 0.38.0, torch 2.15.0.dev cu130, comfy-kitchen 0.2.36, sageattention 2.2.0 installed (unused).

### Measured timing (from log, 768x1344, 10 steps per chunk)
- Chunk 1 (243 f): 10 steps in 5:26 (~32.7 s/it). Chunk 2 (window 260 f incl. 22 f hidden overlap): 7:09 (~43 s/it). Video+audio decode ~45 s. Prompt executed 13:33-13:54 per 20 s segment.
- Log lines worth knowing: `DynamicVRAM support detected and enabled`; `Using Comfy Kitchen attention`; `VSA: the model has no to_gate_compress layers; running the fine stage without the coarse branch`; `VSA: extra_tokens ignored`; UNET `20702MB Staged` (does not fit 16 GB, streamed by DynamicVRAM).
- Community baseline (5070 Ti, aggregated): MiniMax H3 R2V 5 s at 1344x768 ~7 min 50 s typical (steps not stated) - https://www.simpligen.io/gpu/rtx-5070-ti-16gb . Our 10 s chunk at 5:26 is already at or better than that baseline, so speed is not badly off; the big levers are steps/resolution, not flags.

## Primary sources (what "official" means here)
- [MC] 10Eros-Max model card (TenStrip, HF): https://huggingface.co/TenStrip/10Eros-Max
- [CV] beta6 Civitai description (mirror): https://civarchive.com/models/2851079?modelVersionId=3393047
- [D54] TenStrip reply "I actually use the fasth3 I2V comfy template. Just add steps and change sampler": https://huggingface.co/TenStrip/10Eros-Max/discussions/54
- [D61] TenStrip on shift ("10/3 ... not suggested, it's required") + LokkenJP two-pass workflow: https://huggingface.co/TenStrip/10Eros-Max/discussions/61
- [D63] I2V/ref anchoring thread, ref aspect = output aspect: https://huggingface.co/TenStrip/10Eros-Max/discussions/63
- [CD] Comfy docs MiniMax H3 overview: https://docs.comfy.org/tutorials/video/minimax/minimax-h3
- [CN] Comfy docs native T2V/I2V/R2V: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native
- [FH] Comfy docs FastH3: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo
- [TPL] Official template `video_fastvideo_fasth3_i2v.json` (local copy, read above): UNET int8_convrot, TE nvfp4_awq, VAE int8 + audio fp32, ModelAttentionBackend comfy kitchen attention, BlockSparseAttention vsa 10 / 0.2 / 1.0 / min_tokens 12288 / extra 256 / exact_kv_and_rows, MiniMaxH3SigmaShift 10/3, BasicGuider, KSamplerSelect res_multistep, BasicScheduler simple 8 steps denoise 1, 24 fps.
- [GC] Continuation node pack (ttulttul): local README/LEARNINGS + Comfy Registry `comfyui-minimax-h3-continuation`.
- [EXT] MiniMax H3 Extender (tritant): https://github.com/tritant/ComfyUI_MiniMax_H3_Extender (installed locally).
- [AB] H3 Anti-Burn LoRA: https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA
- [I15529] ck attention + int8_convrot crash: https://github.com/Comfy-Org/ComfyUI/issues/15529
- [I15337] 5070 Ti VAE-decode crash, workaround `--disable-async-offload --disable-pinned-memory`: https://github.com/Comfy-Org/ComfyUI/issues/15337
- [I15665] H3 4x slowdown regression (`v = v.clone()`): https://github.com/Comfy-Org/ComfyUI/issues/15665
- [VR] DynamicVRAM / flags explainer (traced to cli_args.py): https://www.instasd.com/post/comfyui-vram-offloading-guide ; confirmed locally in `comfy\cli_args.py` line 170.
- [W4] beta6 W4A8 quant (11.68 GB): https://huggingface.co/berryber09/10Eros-Max-h3-turbo-beta6-pruned-w4a8
- [CQ] community OOM/handover tip (16 GB 5070 Ti): https://www.reddit.com/r/StableDiffusion/comments/1vg5ana/fix_minimax_h3_oom_on_16gb_vram_vram_debug_node/

## Settings table

| # | Setting | Ours | Official / community recommendation | Source | Verdict |
|---|---|---|---|---|---|
| 1 | Checkpoint | `10Eros_Max_h3_8stepTURBO_beta6_int8` (20.2 GB, pruned int8) | beta6 TURBO; int8 mirror is the standard build. Author: "not good to run on smaller cards" | MC, CV | match (note: 16 GB is below author's target) |
| 2 | Steps | 10 per chunk | beta6 "8-12 step" target; FastH3 template 8 "just add steps". Comfy docs: reference shots and audio want more (audio 12+) | MC, CV, D54, TPL, CD | match (inside 8-12) |
| 3 | Sampler | euler | Author's go-to for motion = res_multistep/simple; FastH3 template = res_multistep; euler/simple listed as working (4-8 steps); LCM/simple = best turbo audio | MC, TPL | minor deviation (euler valid, but not the template/author default; 10 steps is above the euler/simple 4-8 range quoted) |
| 4 | Scheduler | simple | simple (template, author) | MC, TPL | match |
| 5 | Sigma shift | video 10 / audio 3 (MiniMaxH3SigmaShift) | 10/3 "required" for beta6 | D61, MC, TPL | match |
| 6 | CFG / guider | BasicGuider (CFG 1, no negative) | FastH3 template uses BasicGuider; distilled turbo | TPL | match |
| 7 | Denoise | 1.0 both chunks | 1.0; continuation pack says "normal full-denoise schedule" | GC | match |
| 8 | Attention backend | ModelAttentionBackend `comfy kitchen attention` + `--use-ck-attention` | FastH3 template does exactly this on an int8_convrot UNET. Comfy docs overview say ck cannot run int8_convrot (I15529, still open) - but the log shows it runs here without the crash | TPL vs CD/I15529 | match to template; docs conflict = unknown whether ck is fully active on every layer (no crash, no fallback warning seen) |
| 9 | Sparse attention | BlockSparseAttention vsa keep 10, start 0.2, end 1.0, min_tokens 12288, sink exact_kv_and_rows | Author: "fully dense or with Fastv2 VSA sparse node settings"; "VSA will work better over SLA or Sol"; avoid SLA. Values identical to FastH3 template. Comfy docs: vsa needs matching (gate) weights; log confirms beta6 has no to_gate_compress, so coarse branch is skipped | MC, CV, TPL, CD, log | match to author/template; quality risk flagged (never A/B'd vs dense here) |
| 10 | Cache / spectrum | none | "No cache or spectrum if doing reference" | MC | match |
| 11 | Text encoder | qwen3vl_32b nvfp4_awq, CLIPLoader type minimax | same in all official templates | TPL | match |
| 12 | Video VAE / audio VAE | int8_convrot / fp32 | templates use int8 video + fp32 audio | CD, TPL | match |
| 13 | Mode for chunk 1 | MiniMaxH3ReferenceToVideo (Ref2VA), 1 ref image | beta6 is "a Reference model with T2V ability"; transfer I2V to reference generation | CV, D61 | match |
| 14 | Ref image prep | centre-crop to 768x1344 (comm.stage), ref_image_size `match` | community: crop ref to output aspect for beta6; `match` is template default (`max` = 2048 px, much slower) | D63, CN, TPL | match |
| 15 | Resolution | 768x1344 (9:16) | H3 trained ~1 MP, 768x1344 is the cap, multiples of 32 | CD, CN | match |
| 16 | Frames chunk 1 | 243 (17k+5) | 17k+5 grid; trained range ~124-362 f | CD | match |
| 17 | Continuation method | GuidedContinuationWindow overlap 22 / extension 238 + LatentTailGuide + Append, same seed | Pack: overlap 17k+5 (22 example), extension multiple of 17 (119 example), same seed; window 260 f stays in trained range | GC | match (238 is 2x example; allowed) |
| 18 | Continuation conditioning | MiniMaxH3ImageToVideo with T2VA prompt, no reference image | Pack example does this (on base fl2va). For beta6 the author says it is a reference model; Extender's Ref2VA + Motion Context keeps `<Picture N>` + a `subject_definitions` block on every clip | GC vs CV, EXT | deviation (for a reference-tuned checkpoint) |
| 19 | Anti-burn on continuation | off in this workflow (knob exists, null) | Comfy docs: Anti-Burn LoRA ~0.5 on clips after the first; LoRA card: start 0.5, int8-merged setups need more | CD, AB | minor deviation (only 1 continuation per segment, so burn exposure is low) |
| 20 | Long video assembly | 3 independent 20 s segments, each restarting from the still, ffmpeg concat -c copy | Community: chain continuations (Extender Motion Context, official `video_minimax_h3_i2v_continuation`); Extender adds seam correction + PCM audio join | EXT, CD | deviation if one continuous minute is wanted; intended if hard cuts are the design (P6 "cuts" parents) |
| 21 | fps | 24 | 24 | CD | match |
| 22 | Decode | VAEDecode / VAEDecodeAudio (native H3 tiling) | templates same | TPL | match |
| 23 | Two-pass / upscale | none (single pass at full res) | Author: "optionally run an upscale pass to clean up reference noise"; LokkenJP: single pass 8-10 preferred, two-pass "usually faster"; Comfy docs: H3 3D latent upscaler then refine denoise 0.1-0.5; Extender v3.0.5 Latent Refine | CV, D61, CD, EXT | unknown/optional (H3 latent upscaler weights not present: `models\latent_upscale_models` only has the LTX x2 file) |
| 24 | `--lowvram` | set | No-op when DynamicVRAM is on (cli_args.py help text; log: DynamicVRAM enabled) | VR, local | deviation (cosmetic; misleading only) |
| 25 | `--disable-async-offload --disable-pinned-memory` | set | Default ON is faster, but the documented workaround for the 5070 Ti/Windows VAE-decode crash; issue still open | I15337, VR | match (keep) |
| 26 | `v = v.clone()` slowdown | line not present in `comfy\ldm\minimax\model.py` 0.38.0 | regression source in 0.32-0.33 | I15665 | match (not affected) |
| 27 | Prompt format chunk 1 | six Ref2VA sections (subject_definitions ... non_diegetic_music) | official ref guide six sections | local ref guide | match |
| 28 | Prompt length chunk 1 | 350-500 words checked on the whole prompt (seg1 c0 = 517 words total) | ref guide: `detailed_description` "normally 350-500 English words" | ref guide line 242 | minor deviation (count is applied to all six sections, so detailed_description lands ~330-360, at or below the floor) |
| 29 | Prompt format chunk 2 | T2VA 3 fields, identity restated in prose | base guide T2VA form is valid; Extender recommends subject_definitions at the start of every clip | base guide, EXT | partial (see #18) |
| 30 | Prompt length chunk 2 | 300-500 words (150-250 per 5 s) | base guide gives no word count; author: "longer and more embellished ... usually better" | base guide, CV | unknown (house rule, not official) |
| 31 | Prompt author | local LLM + official guide (prompt_writer.py) | author: use an LLM enhancer with the official guide; community node pack (installed) offers the same plus a format checker | CV, Rewriter README | match (tooling overlap, see harness section) |

## Top 5 fixes - QUALITY (ranked by expected impact)
1. Keep the reference on the continuation chunk. Chunk 2 currently runs MiniMaxH3ImageToVideo with no `<Picture 1>`, so identity rides only on the 22-frame latent tail and prose. beta6 is a reference-tuned model [CV]; the community way is Ref2VA conditioning on every clip with a `subject_definitions` block at the top of each clip prompt plus motion context [EXT]. Fix: use the installed MiniMax H3 Extender (Ref2VA, Motion Context ON, global ref = POOL) or, if staying API-driven, test MiniMaxH3ReferenceToVideo as the conditioning source into LatentTailGuide (UNVERIFIED that the tail guide accepts Ref2VA conditioning - the Extender does this internally). Targets identity_consistency, the dim P7 kept tripping on.
2. A/B sampler res_multistep/simple vs euler/simple at the same 10 steps and seed. It is the FastH3 template default and the author's "go-to for best motion quality" [MC, TPL]. Not a P7 knob today (KNOBS.md lists sampler as unavailable) - this is a settings gap, not something the knob loop can find.
3. One dense-attention A/B (bypass BlockSparseAttention only). The log proves VSA runs without its coarse branch on beta6 (no gate weights); docs say vsa wants matching weights [CD], while the author says VSA is fine [MC]. Cost ~+30-60% time for that one probe (unmeasured). If dense wins clearly on artifacts/identity, use dense for finals and VSA for drafts.
4. Make the long-form assembly a real chain when continuity is wanted: Extender (Motion Context, seam correction, PCM audio join, per-clip anti-burn via per-clip LoRA) instead of 3 independent 20 s renders hard-concatenated. If cuts are the creative intent, keep it, but say so in KNOBS.
5. Prompt length + format hygiene: apply the 350-500 check to `detailed_description` only (official wording) and run the installed `MiniMax-H3 Prompt Check` node logic (or equivalent) before render. Also consider steps 12 for finals only (Comfy docs: audio converges 12+, reference shots want more steps) - but note P7 round 1 `st12` lost on artifacts, so treat as a seeded A/B, not a default.
- Also cheap: Anti-Burn LoRA 0.5 on chunk 2 [CD, AB] - low impact with only one continuation per segment; matters once chains get longer (Extender path).

## Top 5 fixes - SPEED (ranked by expected impact)
1. Steps 10 -> 8 (FastH3 template value; still inside author's 8-12). Expected ~-20% sampling time: ~-1:05 on chunk 1 and ~-1:26 on chunk 2, so ~11.2 min instead of ~13.6 min per segment (linear estimate from logged s/it). Quality cost unmeasured - A/B with the judge.
2. Two-pass: first pass at lower resolution, H3 3D latent upscaler x2, short refine (denoise 0.1-0.5, enough steps) [CD, D61 LokkenJP, EXT v3.0.5]. LokkenJP: "usually faster, and allows quick previews". Needs the H3 latent upscaler weights (not installed; the Mamad8/MiniMaxH3 upscaler nodes are installed). Gain UNVERIFIED on 16 GB.
3. Stop paying ComfyUI wake + model staging per job: KNOBS measured ~50 s ComfyUI wake per segment job plus TE re-staging each prompt; batching all segments of a run into one ComfyUI session (or one Extender Full Batch) removes repeats. ~1 min/segment.
4. Fit the UNET in VRAM: beta6 W4A8 pruned (11.68 GB) [W4] would end weight streaming (20.7 GB staged today). Expected gain is small (compute-bound: GPU already at ~33-43 s/it; streaming ~5-6 GB/step without async/pinned is likely ~1-3 s/step - estimate, not measured) and quality impact of W4A8 is UNVERIFIED. Comfy docs do say "CPU offload costs more than precision tradeoffs" [CD]. Low priority.
5. Do NOT chase these: Sage attention (ck already in place and template-matched; Sage int8 attention causes end-of-clip morphing per [CD]); cache/spectrum nodes (author: accuracy loss with references [MC]); SLA/sol sparsity (author: destroys beta6 [MC]); re-enabling pinned memory/async offload (crash workaround on this exact GPU [I15337]). Remove `--lowvram` only for clarity (no speed change).

## Harness pieces that have a community equivalent
| Custom piece | Community equivalent | Recommendation |
|---|---|---|
| `comm.build()` continuation chain + `batch_queue.stitch()` ffmpeg concat | MiniMax H3 Extender (installed): Ref2VA per clip, Motion Context, disk cache, validation/resume, seam + audio-join correction, per-clip LoRA, Latent Refine | Replace for long-form. Caveat: Extender is a UI-heavy node (JS widgets, .ext projects); driving it headless from ralph/batch_queue via /prompt is UNVERIFIED - test once in the UI first. |
| `comm.build()` graph from scratch | Official `video_fastvideo_fasth3_i2v` template (author's base) + `video_minimax_h3_r2v` | Our chain already equals the FastH3 template; export the template (with Ref2VA node swap) as the API base instead of hand-built JSON so ComfyUI updates flow in. |
| `prompt_writer.py` (LLM + guide in system prompt, word-count retry) | MiniMax-H3-Prompt-Rewriter-ComfyUI (installed): "Prompt Writer (Ref2VA)", "Guide Prompt (any LLM)", "Prompt Check", "Reference Caption" | Keep the LLM path (it is the same method), but adopt Prompt Check for validation; optionally the Omni rewriter for Ref2VA (it looks at the reference). |
| `comm.stage()` centre-crop + Lanczos | core/KJNodes resize-with-crop nodes in-graph | Optional; current code is small and correct. |
| `comm.frames_for()` 17k+5 math | ComfyMathExpression used in official templates | Optional. |
| `p6_review.py` VLM judge + composite | no clear community standard found (UNVERIFIED) | Keep; note P7 close notes show the pairwise term decides most verdicts - a judge-noise problem, not a settings one. |
| Adults-only guard | n/a (policy) | Keep. |

## Stale / misleading local items
- `custom_nodes\10S-Comfy-nodes` README: LTX2-only nodes ("will not work on other diffusion models"); not used by the H3 graph. Not harmful, just irrelevant to beta6.
- Fleet skill `ltx-comfy-pipeline` (box skill `ltx-comfy-pipeline-2`) still describes LTX-era 10Eros v1.2/v1.3, 8n+1 frames, fp8 flags and `--lowvram`; it conflicts with H3 rules (17k+5, 10/3 shift, DynamicVRAM). Should be updated or marked superseded for H3 work.
- `KNOBS.md` says "sigma shift locked 10/3 by C2" - correct and matches the author's requirement; "sampler" listed as not a knob - that blocks the #2 quality A/B.
- `comm.py` comment "D9/TenStrip: ref aspect == output" - consistent with [D63].

## Unverified / open
- Whether ck attention is active on all H3 attention calls with this int8_convrot UNET (docs say unsupported; template and our log say it runs).
- Whether MiniMaxH3LatentTailGuide accepts MiniMaxH3ReferenceToVideo conditioning.
- Real quality effect of VSA-without-gates vs dense on beta6, and of W4A8 vs int8.
- Two-pass speed gain on this card.
- Reddit threads could not be fetched directly (blocked); claims from them are taken via the cited articles/issues only.