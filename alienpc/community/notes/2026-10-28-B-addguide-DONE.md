# B re-run with the #74 Add Guide fix — DONE (2026-10-28 18:15 CT)

Brief: `notes/2026-10-28-max-brief-B-addguide.md`, including *Added 17:05: check graph vs LokkenJP first*.
Run dir: `C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007` · tag `terrace_dom_q5guide_20261028_s51083007` · arm id 07.
Graph built by `runs/terrace_dom_q5guide_20261028_s51083007/build_graph.py` from a **copy** of B's graph
(`terrace_dom_q5_20261028_s51083005.api.json`), edited, never rebuilt.

## Files delivered

| File | Bytes | Content |
|---|---:|---|
| `terrace_dom_q5guide_20261028_s51083007_raw.mp4` | **4,520,700** | the untouched render, 768×1344 @ 24/1, 243 frames, 10.125 s, h264 + aac, 3572 kbps |
| `terrace_dom_q5guide_20261028_s51083007_final.mp4` | **5,770,214** | `ffmpeg -c:v libx264 -preset slow -crf 18 -c:a copy` **of the raw, native 768×1344** (no upscale), 4559 kbps |

- QNAP `/pi-drop/` — uploaded with `pi_qnap.py put`, and `pi_qnap.py ls /pi-drop/` reports the same sizes:
  `…_raw.mp4 4520700`, `…_final.mp4 5770214`. **No RTX output, as the brief says** (`_rtx12`/`_rtx920` do not exist for this arm).
- Also in the run dir: `request.api.json` (20,072 B) + `<tag>.api.json` (19,068 B) + `<tag>.api.pretty.json` (20,072 B) —
  compared node by node: **26/26 nodes identical**, the byte gap is the runner's compact re-serialization of the same graph.
  `build_graph.py`, `prompt_seg0.txt` (13,129 B),
  `status.log`, `objective.json`, `<tag>.mp4.json`, `<tag>_stills_contact.png` (runner's contact sheet), `motion_check.py` + `motion_check.txt`.

## Render time, exact

- `2026-10-28 17:50:50 CT` GPU window opened (`gpu_window.ps1`, `gpu_lock -Acquire` → pid 34272, `gpu_guard` IDLE);
  prompt `dcc4ec73-3912-46ff-96c0-ecc23c4fd4ef` submitted `17:51:20`; `17:55:20` **JOB end ok secs=240.1**;
  `17:55:21` comfyui_auto unloaded, lock released, post-window `gpu_guard` IDLE. **One PowerShell call, one render, rc=0, no redo.**
- **240.1 s = 0.99 s/frame** for 243 frames at 768×1344. Same wall time as B's 240.1 s by arithmetic:
  8 steps at 0.258 MP (≈15 s/step) + 3 steps at 1.03 MP (≈45 s/step) ≈ 4 low + 4 full. For the record: A native-8 = 360.1 s, C native-12 = 480.2 s.
- Objective gate first pass: `frames=243 size=768x1344 audio=True dur=10.125 bytes=4520700`, blackdetect/freezedetect clean (`blackfreeze: []`).

## What changed in the graph — node ids, exactly

Diff note (required by the brief): **`notes/2026-10-28-B-graph-vs-lokken.md`** — B's 26 nodes vs LokkenJP's published
`H3_Turbo_2Pass_ErosMax_b7_simple_v1.json` (re-downloaded, SHA256 `05FA6B2A06C98F5FC40880B807A75537562F2D433E37E255F118AD05D67C57E7`,
68,606 B, byte-identical to the copy in `notes/web/`). Node count stays 26: **−3 deleted, +3 added**.

The two miswires that burned B (both were B's, not the model's):
1. **`s0_split` `SplitSigmas(step 4)`** truncated pass 1 to **4 of the 8 scheduled steps and stopped at a non-zero sigma** —
   the published workflow has **no SplitSigmas at all**: its `BasicScheduler "Scheduler First Pass"` (sgm_uniform, 8, 1.0)
   feeds the sampler the whole schedule.
2. **`s1_sig` `ManualSigmas "0.9035, 0.6316, 0.3158, 0.0000"`** = 4 steps from sigma 0.9035, i.e. **denoise ≈0.9 at full
   resolution** — a single-pass r2v template pasted in as pass 2, so every frame of the clip was thrown away and
   re-drawn from near-pure noise. The published second pass is `BasicScheduler "Scheduler Second Pass"` =
   **scheduler `beta`, steps 3, denoise 0.4** — a partial-denoise refine.

Edits applied to the copy:

| Node | Change |
|---|---|
| `c0` `MiniMaxH3ReferenceToVideo` | **`ref_image_size`: `"match"` → `"max"`** ← the #74 setting (the "Reference to Video" input Derek named). `prompt`, `width 384`, `height 672`, `length 243`, `ref_images.ref_image_0 ← img` untouched. |
| **`ag0`** *(added)* `MiniMaxH3AddGuide` | `positive ← c0:0`, `latent ← c0:1`, `image ← img:0`, `vae ← vvae:0`, `frame_idx 0` → `s0_guide.conditioning` |
| **`ag1`** *(added)* `MiniMaxH3AddGuide` | `positive ← c0:0`, `latent ← s1_cat:0`, `image ← img:0`, `vae ← vvae:0`, `frame_idx 0` → `s1_guide.conditioning` |
| **`p2sched`** *(added)* `BasicScheduler` | `model ← m_shift:0`, **`scheduler "beta"`, `steps 3`, `denoise 0.4`** → `s1_samp.sigmas` (published second-pass scheduler) |
| `s0_split` *(deleted)* | pass-1 sigmas now `s0_samp.sigmas ← s0_sched:0` (the full 8-step schedule; `s0_sched` values unchanged: simple, 8, 1.0) |
| `s1_sig` *(deleted)* | the ManualSigmas string, replaced by `p2sched` |
| `ksel1` *(deleted)* | one `KSamplerSelect` for both passes, as published: `s1_samp.sampler ← ksel:0`. Name stays **`euler`** = B's constant + the beta7 stock dial; the published `er_sde` is the readme's alternate (documented deviation). |
| `dec_a` `VAEDecodeAudio` | `samples: ["s1_samp", 0]` → **`["s0_sep", 1]`** — the published graph decodes the **first-pass** audio latent (its `VAEDecodeAudio ← HaltExecution ← 35:1`), so the second pass no longer overwrites the soundtrack. Video decode stays on the pass-2 latent (`dec_v ← s1_samp:0`), which is what the published preview switch resolves to. |
| `lsu3` `MinimaxH3LatentUpscaler3D` | **`enable_temporal_chunking: false → true`** (published widget value). `model_name` stays `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` — the published `_fp16` checkpoint is gated on HF and not installed, and the node's `model_name` COMBO lists only installed files. Mode stays `scale by multiplier 2.0`, `align 32`, `force_unload true`, `cuda`, `fp16`. |
| `save` | `filename_prefix → community/terrace_dom_q5guide_20261028_s51083007/terrace_dom_q5guide_20261028_s51083007` |

Unchanged from B, verified by assertions in `build_graph.py` (it refuses to write if any of these moved):
seed **51083002** · prompt **13,128 chars byte-identical** (no `<Picture 1> is the correct scene identity…` steering sentence, brief rule 3) ·
`community/TERRACE2_768x1344.png` · `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` · CLIP nvfp4_awq ·
video/audio VAEs · euler · **8 steps** on pass 1 · **shift 12 / 3** · **VSA vsa keep_percent 10** (start 0, end 1, dense "0,1", 12288/256, exact_kv_and_rows) ·
**243 frames** · 24 fps · 384×672 → 768×1344. Static validation in the builder (link targets, reachability from `save`) plus the runner's
own `static_check` against the live `/object_info` — both clean.

Geometry kept on purpose: the published `ResolutionSelector` is 0.3 MP with a 4:3 preset list and 32-rounding, and
`mode "megapixels"` target 1.0 does **not** land on this cell's canvas (416×768 → ~768×1408). 384×672 (0.258 MP,
inside the published 0.2–0.3 MP first-pass band) × 2.0 = **exactly 768×1344**, so the arm stays comparable with A/C/v2.

## `MiniMaxH3AddGuide` facts read off the node itself (`ComfyUI/comfy_extras/nodes_minimax_h3.py:165`)

- It is a **core** node on this box (no install needed) — required `positive`, `latent`, `frame_idx`; optional `vae`, `audio_vae`, `image`, `audio`;
  output = CONDITIONING, so it goes **between** `c0` and each `BasicGuider`, exactly as the discussion describes.
- **`vae` is not optional in practice**: `if vae is None: raise ValueError("anchoring guide frames needs the vae input")`.
  The brief says "leave the other inputs at defaults" — an unconnected `vae` with an image connected is a hard runtime error,
  so `vae ← vvae` on both nodes is forced by the node, not chosen. `audio`/`audio_vae` left at defaults (no audio guide).
- `latent` must be a real H3 **AV** latent (it asserts a nested 2-tensor latent, video tensor 5D with 24 channels) and it takes
  the target canvas from that latent (`height = video.shape[3] * 16`), centre-cropping the guide image to it. So the pass-1 guide
  is encoded at 384×672 and the pass-2 guide at 768×1344 — the pass-2 guide is the start image at its native size,
  which is the point of `ref_image_size: max`. `frame_idx 0` is the node's own default = anchor at frame 0.

## Objective signal that the burn is gone (proxy, not a verdict)

- **h264 bitrate at fixed crf is a high-frequency-energy proxy, not a quality score.** This raw: **3572 kbps**
  (4.52 MB) vs B's raw **9135 kbps** (11.56 MB). The corrected graph now sits in the band of the single-pass arms
  (A 3459, C 3625) instead of 2.5× above them — i.e. the pass-2 re-synthesised detail that made B look baked is no longer there.
- `motion_check.py` (in the run dir, run on the raw): noise floor **5.650** (B's floor was 11.183 — the same inflation),
  right-half `right/floor` **0.63×–2.15×** with no collapse; the 8–10 s window keeps ~0.85–1.05× instead of flatlining.
  Motion floors are per-path, so these numbers are only comparable **within** this cell.
- Derek's watch is the judge. The claim here is narrower than "it looks good": the pass that re-drew every frame at 0.9 denoise
  is gone, and the two independent proxies moved the way a de-burned clip should.

## Not done, on purpose

- No RTX super-resolution, no `_rtx12`/`_rtx920` (brief).
- `verify_cell.py` from B's dir **not** run on this cell — it asserts B's own recipe (B's sigma nodes, B's byte size), so its FAIL
  count would be a false alarm, not a defect. `motion_check.py` (recipe-independent) was copied and run instead.
- `HaltExecution` and `ComfySwitchNode` from the published graph not reproduced: a VRAM-ordering node and a preview toggle,
  neither is in the data flow. `ModelPreviewOverrideKJ` / `H3PowerLoraStack` are not installed here and are preview-only / off by default.

GPU state after: `gpu_guard` IDLE, lock released, comfyui_auto unloaded.
