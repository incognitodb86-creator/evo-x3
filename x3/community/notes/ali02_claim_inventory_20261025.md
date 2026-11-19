[TOOL OUTPUT TRUNCATED: 221 lines / 50.1 KB exceeds the 1000-line / 32.0 KB cap.
Full output saved to: C:\Users\derek\AppData\Local\Temp\pi-tool-outputs\7e85745f-574e-4748-aad8-4b468a156b28.txt
Showing the first 40 and last 40 lines. Inspect the file with targeted reads (Select-String, head, tail, read with offset/limit); never print it whole.]
--- first 40 lines ---
# ALI-02 - Claim inventory + local probe findings (run 2026-10-25)

Answers the fix_plan 0.2/0.2x ask: "list the old notes' key claims and source them".
Every row = a claim **as written in our notes**, the source it names, a verdict, and the evidence.

## Method (this pass)
- Local probes (scripts ON DISK): `notes/ali02_local_probe.py`, `_probe2.py`, `_probe3.py`.
  A 4th probe was run in the session and **is not on disk** (`_probe4.py` does not exist),
  so every row that cited it is re-attributed below (see M1) and the parts no committed
  script reproduces are marked **GAP**.
  -> installed ComfyUI, node classes/schemas, installed Continuum code, the real R3b graph + ref images,
  the installed checkpoint, venv, nvidia-smi, official Continuum V39 workflow fetch.
- Primary-source fetches: `notes/ali02_sources.json` (149 URLs) -> bodies in `notes/web/`, all saved through
  `scripts/web_fetch.py` (extension from body; non-200 stamped `.404/.401.txt`) and validated by
  `scripts/check_web_saves.py`. Run stats: 80 bodies (HTTP 200), 69 stamped failures (401/404), 12 already saved.
- Verdicts: **VERIFIED** (named source contains the claim), **VERIFIED-DRIFT** (true, number/name stale),
  **NOT FOUND** (named source contains no such string), **REFUTED** (source says otherwise),
  **UNVERIFIABLE** (source not reachable anonymously this pass).

Verdict shorthand below; `file:line` = our note; `web/NAME` = `C:/AI/community/notes/web/NAME`.

## A. Box facts (probe output; all reproducible by re-running the probe scripts)
| # | Fact | Evidence |
|---|---|---|
| A1 | ComfyUI **0.38.0** (`__version__` in `comfyui_version.py` + `pyproject.toml` + git describe `v0.38.0`) | `ali02_local_probe.py` (comfyui_version.py + pyproject section); git HEAD `58d6250` 2026-10-24 |
| A2 | GPU = **RTX 5070 Ti, 16,303 MiB, driver 616.92** - NOT a 4090 | `nvidia-smi` this pass; matches `p7/AUDIT_2026-10-21_community_10eros.md:8` |
| A3 | Core H3 nodes (`comfy_extras/nodes_minimax_h3.py`): `MiniMaxH3ImageToVideo`, `MiniMaxH3ReferenceToVideo`, `MiniMaxH3AddGuide`, `MiniMaxH3AppendContinuation`, `MiniMaxH3GuidedContinuationWindow`, `MiniMaxH3LatentTailGuide`, **`MiniMaxH3SigmaShift`** (inputs `video_shift` default 10.0, `audio_s ...[+237 chars]
| A4 | R2V node: `ref_image_size` options `["match","max"]` default `match`; `REF_IMAGE_SHORT_EDGE = 2048` = "downscale each reference to 2048 short edge, downscale only, no upscale" | installed `nodes_minimax_h3.py` (probe) |
| A5 | `MiniMaxH3ImageToVideo` has **no** `audio_vae` input; `MiniMaxH3ReferenceToVideo` has 1 (required) | installed source (probe2) - AGENTS.md:31 VERIFIED |
| A6 | Installed Continuum pack = **3.10.2** (`version.py`, `pyproject.toml`, git `describe --tags` = v3.10.2; HEAD `308653c` 2026-10-24; 160 py files, no `nodes.py`) | probe2; registry published latest = **3.10.0** -> local install is git-ahead of the registry |
| A7 | Continuum canvas rules: `H3_CANVAS_MULTIPLE = 32`, min 32, max 16384; presets `Draft 0.30 MP` / `Balanced 0.60 MP` / `Native 768` / `Custom`; native short-edge rule; `target_frames == round(chunk_count * chunk_seconds * fps)` enforced in **`hardening.py:84-88`** (root file, not `v3/hardening. ...[+93 chars]
| A8 | Sampler class present: `H3ContinuumSamplerV39` (33 inputs) - **no `negative`/CFG input**; V39 node set: `H3V39StartStillSequenceDriverV39` (67 inputs), `H3V39DrivingNode` (40), `H3ContinuumSamplerV39` (33), `H3V39SequencePromptDriverV39` (26), `H3V39DrivingNodeV39` (17) + V39 validators | pro ...[+5 chars]
| A9 | **`FaceRefine` does not exist** in ComfyUI core or ANY installed custom node (grep over `nodes.py`, `server/`, all 11 packs = 0 hits); `FaceDetailer` exists only in the Impact pack | **GAP**: no committed probe covers this (`FaceRefine` is in no `ali02_local_probe*.py`); the `read` tool is de ...[+167 chars]
| A10 | `BlockSparseAttention` INPUT keys in 0.38.0 = `selection, keep_percent, extra_tokens, min_tokens, start_percent, end_percent, sink_conditioning, dense_blocks` (+ nested `_font/`/`_extra_font/`). `sparse_blocks`/`sparse_size`/`max_dims` are **absent** (they belong to `TomeSparseAttention` + ` ...[+252 chars]
| A11 | Installed model file = `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` (21,709,633,539 B = 20.22 GiB, mtime 2026-09-23 17:38). `*beta8*` exists nowhere in the install and nowhere in `TenStrip/10Eros-Max` (tree has beta2/3/4/5/6 + `FastH3_VSAgates_UNSTABLE_beta6-int8_HQ`) | `ali02_local_pro ...[+143 chars]
| A12 | R3b real graph (`runs/ali147_pool_hc_r3b_s51130003/request.api.json`): 1344x768, 243 f @24 fps, `ref_image_size="match"`, `seed=51130003`, `ksel=euler`, `s0/s1 BasicScheduler steps=10 denoise=1.0 scheduler=simple`, `m_shift MiniMaxH3SigmaShift video 10 / audio 3`, `m_vsa keep_percent=10 extr ...[+346 chars]
| A13 | The 3 ref images and their real sizes: start still 1152x640; face crops **159x125** (16,201 B) and **157x250** (15,310 B) - all inside the 2048 short-edge rule (no downscale triggered) | `ali02_local_probe3.py` (`imgsize()`, pure-`struct` JPEG/PNG header parse, lines 24-49; PIL is not in the ...[+8 chars]
| A14 | ComfyUI `.venv` (Python 3.12.10): torch **2.15.0.dev20260928+cu130**, torchvision 0.24.0.0a0, torchaudio 2.11.0.a0, numpy 2.4.4, transformers 5.6.2, einops 8.1.1, safetensors 0.7.0; cv2 4.11.0 + mediapipe/scipy/insightface/ultralytics/onnxruntime present; **no PIL**; no bitsandbytes | probe1 ...[+2 chars]
| A15 | ffmpeg 8.0.1 build has **`siti`** (Spatial-Index-Two-Interpolation, ffmpeg doc: "calculate spatial index two interpolation") -> the SI metric in `research/video-review-optimize-2026-10-20.md:37` is computable on this box | probe1 |
| A16 | No `FaceRefine`/`antiburn`/`face`-keyword LoRA in `ComfyUI/models/loras`; present: `PenisV2_minimax-h3_epoch60.safetensors` (309,850,848 B), `h3_antiburn_universal_v1_antiburn_0010.safetensors` (385,033,528 B); **no `Vagina*.safetensors` anywhere in the install** | `ali02_local_probe.py` (lo ...[+167 chars]
--- [141 lines omitted] ---
--- last 40 lines ---
| "End-of-clip morphing or garbled on-screen text with Sage often comes from **INT8 attention quantization**" | `web/02v_docs_h3.txt:199` |
| "Templates use **int8_convrot** checkpoints. **Comfy Kitchen does not support them** (issue #15529). Use default attention, or switch UNETLoader to **pruned_bf16** then change backend" | `web/02v_docs_h3.txt:201` (+ `:80` "Comfy Kitchen attention cannot run int8_convrot checkpoints; use a bf16 bui ...[+6 chars]
| "For base H3 use `method` **sol-attn** (`sla`/`vsa` need matching weights)"; defaults `start_percent` **0.2**, `end_percent` **1.0**; "FastH3 uses **vsa** at `keep_percent` **10**" | `web/02v_docs_h3.txt:208,215` |
| "Use a **latent upscaler** on the 24-channel video latent to avoid VAE round-trip ghosting" + refine `denoise` **0.1-0.5** + "video and audio latents are separate (24 + 32 channels)" | `web/02v_docs_h3.txt:132,134,136` |
| "Trained range ~124-362 frames (~5-15 s)", "Frame grid 17k+5 at 24 fps (124 frames = 5 s)", "Beyond the trained range, chain I2V continuations ... **Errors compound (faces lose texture first)**" | `web/02v_docs_h3.txt:147,148,155` |
| FastH3: "Steps are fixed at 8" (distilled), "BlockSparseAttention ... `keep_percent` 10 starting at 20%", distilled = T2V + first/last-frame I2V only (no Ref2VA) | `web/02v_docs_h3_fastvideo.txt:40,110,17` |
| Template requirements: base T2V/I2V/R2V **0.30.0+**, Multiframe Reference **0.34.0+**, sparse attention / Model Attention Backend **0.35.0+**, FastH3 **0.36.0+** (box runs 0.38.0, A1) | `web/02v_docs_h3.txt:58` |
| Anti-Burn / character-consistency LoRA recommendation (10-15 steps + negative prompt "blurred soft appearance, lowres ...") | `web/02v_docs_h3.txt` (anti-burn section) -> the docs' LoRA is `Imagineer13/H3-Anti-Burn-LoRA`; strengths are not official |

## K. What this changes for the live task (R4 bakeoff)
- **Model arm**: name the file, not the legend: `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` (20.22 GiB, installed). "beta8" is not a file on this box.
- **Shift**: 10/3 (author-required for beta6; core node defaults agree). Keep 10/3 for every arm.
- **Steps**: 10/10 is inside community range (8-12, 8-10); a **12-16 step arm** is docs-supported (most clips 12-16; audio dialogue needs 12+). >50 steps: docs say little visible change.
- **Sampler**: official templates = `res_multistep`+`simple`; our graph = `euler`+`simple`; card lists Euler/simple 4-8, res_multistep/simple 6-8, LCM/simple 6-8 -> the sampler arm is one-variable-legit.
- **Attention**: VSA keep_percent 10 = FastH3 distill setting (`web/02v_docs_h3.txt:215`) and matches our graph (A12); `sla` = card says destroys beta6; base H3 = `sol-attn` (`:208`); INT8+Sage morphing documented (`:199`); comfy-kitchen attention does **not** run int8_convrot checkpoints (`:201`, ` ...[+281 chars]
- **Sage arm is docs-supported and cheap to test**: "roughly 2x speed with small quality impact" (`:186-188`), needs `Patch Sage Attention KJ` (KJNodes = installed, 3.4.16) or `--use-sage-attention`, and float16/bfloat16 layers only (`:193`).
- **First-frame aspect**: our approved still is 1152x640 (16:9) into a 1344x768 canvas; docs warn `first_frame` is resized **without** keeping aspect, so an off-aspect image is stretched (`web/02v_docs_h3_native.txt:139`) -> a crop-to-canvas-aspect arm is a legit one-variable knob for likeness.
- **Turbo/steps arms**: docs default 20 steps, `turbo_mode` 8 (R2V turbo 4), "raise steps (e.g. 25) for motion quality" (`web/02v_docs_h3_native.txt:72,218`) -> a 20-step dense arm is the docs baseline, not an exotic choice.
- **Face/identity arms that are real on this box**: (a) `ref_image_size=max` (cost measured locally: r4a 2:09 `match` vs r3b 5:05 `max`, 1344x768 243 f); (b) **bigger face crops** (1024-2048 px short edge; current 159x125/157x250 are 8-13x under budget); (c) prompt-side `subject_definitions` + `<Pic ...[+315 chars]
- **Continuum arm**: use presets (Balanced 0.60 MP / Native 768) and canvas multiples of 32 - `832x468` is invalid (468 % 32 = 20), `1024x576` is valid; declare frames as `chunks*chunk_seconds*fps`; V39 sampler has no CFG/negative; local 3.10.2 vs registry 3.10.0 (registry version **Flagged**) -> no ...[+24 chars]
- **Length**: 243 f = 10.125 s stays (docs 17k+5 grid, MiniMax disc 28 124/243/362, continuation 22/119).
- **Prompt**: build arms from the on-disk official guides (ref guide: `detailed_description` 350-500 words), NOT from the "50-100 words" line (in no saved body - see M3) and not from `[0s-2s]` timecodes (community invention, thread says RTFM).
- **No GPU, no renders** this pass; KEEP stays Derrick's.

## L. Reproduce
```
python C:/AI/community/notes/ali02_local_probe.py      # ComfyUI, node schemas, venv, ffmpeg, assets
python C:/AI/community/notes/ali02_local_probe2.py     # AST: Continuum constants, V39 sampler inputs
python C:/AI/community/notes/ali02_local_probe3.py     # AST: real R3b graph inputs, installed packs
python C:/AI/community/notes/ali02_fetch.py            # 149 primary sources -> notes/web (safe save rules)
python C:/AI/community/scripts/check_web_saves.py      # harness-safe: every notes/web/*.json parses
python C:/AI/community/notes/ali02_citation_check.py    # every cite must resolve on disk (87 cites + 7 bans)
python C:/AI/community/notes/ali02_citation_check.py --selftest   # the 3 detectors must fire on seeded faults
```

## M. Citation-fix pass (2026-10-24, post-compaction; no fetches - local files only)
`ali02_citation_check.py` went from 86 cites / 3 problems to **87 cites + 7 bans / 0 problems**, plus `--selftest` (seeded MISSING-FILE, MISSING-TEXT, BAN-HOLDS: all 3 fire; 0 on the real set).
1. **M1 - a phantom script.** The draft method block and rows A1/A11/A13/A16 cited `notes/ali02_local_probe4.py`, which **does not exist** (only probe, probe2, probe3 are on disk). Re-attributed: A1 -> probe; A11 -> probe + probe3; A13 -> probe3 (`imgsize()`); A16 -> probe for the two LoRA files, an ...[+187 chars]

[Showing lines 1-219 of 224 (50.0KB limit). Use offset=220 to continue.]