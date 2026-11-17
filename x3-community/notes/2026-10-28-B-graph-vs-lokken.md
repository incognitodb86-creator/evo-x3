# B's graph vs LokkenJP's published beta 7 two-pass workflow (2026-10-28 18:15 CT)

Task rule being executed: `2026-10-28-max-brief-B-addguide.md` → *Added 17:05: check graph vs LokkenJP first*.
Compared: `runs/terrace_dom_q5_20261028_s51083005/{request.api.json,terrace_dom_q5_20261028_s51083005.api.json}`
(both 18,077 B, byte-identical to each other; 26 nodes) against the published workflow, node by node.

## Provenance of the published workflow (downloaded, not rebuilt from memory)

- LokkenJP's repo: `https://huggingface.co/LokkenJP/TenEros_Max_optimized_learned`. Its model card (saved today:
  `notes/web/lokken_b7_readme_20261028.md`) is the "learned B7" re-quant of `TenStrip/10Eros-Max` and points at its
  workflow folders. `GET /api/models/LokkenJP/TenEros_Max_optimized_learned/tree/main/SampleWorkFlowTwoPassOptimized`
  lists two files at the top level (the readme: "the latest workflow is at the folder's top level, previous versions under old/"):
  - `H3_Turbo_2Pass_ErosMax_b7_simple_v1.json` — 68,606 B  ← **the reference used here**
  - `H3_Turbo_2Pass_ErosMax_b7_experimental_refmods_v3b.json` — 189,504 B (an "experimental refmods" variant, not B's shape)
- `.../resolve/main/SampleWorkFlowTwoPassOptimized/H3_Turbo_2Pass_ErosMax_b7_simple_v1.json` re-downloaded
  2026-10-28 17:4x CT, immediately before the 17:50 render → SHA256 `05FA6B2A06C98F5FC40880B807A75537562F2D433E37E255F118AD05D67C57E7`, 68,606 B,
  **identical to the copy saved earlier today** at `notes/web/lokken_b7_2pass_simple_v1.json`. So the local file is
  the published file verbatim; the diff below was read off it with a workflow parser
  (`5slock/tmp_lokken/dump_wf.py`, resolved links + widget values), not from memory.
- Shape of the published file: 30 top-level nodes + a subgraph `Single-reference two-pass generation`
  (id `7fcfd5ca…`, 12 nodes) + `Encode 24 FPS video` + `Output saving quality – encoder preset`. B is a flat
  API graph, so the comparison is **per function**, matched by node type and role.

## The two real miswires (this is why B looked burned)

**1. Pass 1 was sampled at half its schedule.**
Published: `BasicScheduler "Scheduler First Pass" [24]` → `scheduler "sgm_uniform", steps 8, denoise 1.0`, output wired
straight into the pass-1 `SamplerCustomAdvanced.sigmas`. **There is no `SplitSigmas` node anywhere in the published
workflow.**
B: `s0_sched` `BasicScheduler("simple", 8, 1.0)` → **`s0_split` `SplitSigmas(step = 4)`** → pass-1 sampler.
`SplitSigmas` output 0 is the first `step` sigmas, so B ran **4 of 8 steps and stopped at a non-zero sigma** — pass 1
never reaches the end of its schedule, so the low-res base is under-converged. (The 4-step split + the fixed sigma
string came from the pack's *single-pass* r2v template, which `build_graph.py` copied and repurposed as a two-pass.)

**2. Pass 2 was a full re-synthesis, not a refine — the burn.**
Published: `BasicScheduler "Scheduler Second Pass" [102]` → **`scheduler "beta", steps 3, denoise 0.4`**.
B: `s1_sig` **`ManualSigmas "0.9035, 0.6316, 0.3158, 0.0000"`** = 4 steps starting at sigma 0.9035 →
**effective denoise ≈ 0.9 at full resolution**: every frame of the 1.03 MP clip is thrown away and re-drawn from
near-pure noise in 4 steps. The pass-1 result (identity, lighting, the start image) is not preserved by that, and the
model's own high-noise full-frame re-composition at shift 12 is exactly what reads as blown highlights / baked
contrast / "burned". A 0.9-denoise single-pass schedule is a *one-pass* recipe; as a *second* pass it is the bug.

## Node-by-node table

| Item | Published `simple_v1` | B (`terrace_dom_q5`) | Action in the q5guide graph |
|---|---|---|---|
| Pass-1 sigmas | `BasicScheduler [24]` sgm_uniform, 8, **1.0**, full schedule, **no SplitSigmas** | `s0_sched` simple 8 1.0 → **`s0_split` SplitSigmas step 4** (4 steps, truncated) | **`s0_split` deleted**; `s0_samp.sigmas ← s0_sched` (full 8-step schedule). Scheduler name **kept `simple`** (B's constant, pairs with the euler sampler, = the beta7 stock Euler/simple dial on this box; sgm_uniform is the published pairing for its er_sde — the readme lists both pairings) |
| Pass-2 sigmas / denoise | `BasicScheduler [102]` **"beta", 3, 0.4** | **`s1_sig` ManualSigmas 0.9035/0.6316/0.3158/0.0**, 4 steps, denoise ≈0.9 | **`s1_sig` deleted**; new **`p2sched` = BasicScheduler(model `m_shift`, scheduler `beta`, steps 3, denoise 0.4)**; `s1_samp.sigmas ← p2sched` |
| CFG | no `CFGGuider` node; both passes `BasicGuider` (guidance 1.0, turbo contract) | same (`s0_guide`, `s1_guide`) | no change — matches |
| Sampler | **one** `KSamplerSelect [18]` = `er_sde`, fed to *both* samplers via the subgraph's `sampler` input | two nodes `ksel` + `ksel1`, both `euler` | **`ksel1` deleted**, `s1_samp.sampler ← ksel` (structural match). **Name kept `euler`** — B's constant in `ab_q4_q5_brief_2026-10-28.md` and the beta7 stock dial; `er_sde` is the readme's alternate. Documented deviation. |
| Latent upscaler | `MinimaxH3LatentUpscaler3D [26]`: `minimax_h3_latent_upscaler_3d_fp16.safetensors`, mode **"megapixels"** ← `PrimitiveFloat [23] "Final Target Megapixels (2nd Pass)" = 1`, align 32, **`enable_temporal_chunking = true`**, `force_unload = true`, cuda, fp16 | `lsu3`: `..._conv_v1_bf16.safetensors`, mode **"scale by multiplier" 2.0**, align 32, **chunking false**, force_unload true, cuda, fp16 | **`enable_temporal_chunking → true`** (published). model_name **kept** `conv_v1_bf16`: the fp16 checkpoint is gated on HF and is not installed (the node's `model_name` COMBO lists only installed files). geometry kept, see next row. |
| Resolution | first pass from `ResolutionSelector [20]` = "4:3 (Standard)", **0.3 MP**, multiple 32; second pass = the 1.0 MP primitive | 384×672 (0.258 MP) in `c0`, ×2.0 → **768×1344** | **Kept.** The selector has no 9:16 preset and 32-rounding a megapixels target does not land on this cell's canvas (416×768 → 1.0 MP ≈ 768×1408). The brief fixes the output at 768×1344 native so B stays comparable with A/C/v2; 384×672 is inside the published 0.2–0.3 MP first-pass band (its own table). Documented deviation. |
| Video decode | `VAEDecode [25]` ← `ComfySwitchNode "Choose video for preview" [95]`, `on_false` = **pass-2** sampler output (preview switch is `false`) | `dec_v ← s1_samp:0` = pass-2 | no change — matches (the switch node is a preview toggle) |
| **Audio decode** | `VAEDecodeAudio [14]` ← `HaltExecution "Halt Execution (Audio VAE Last)" [86]` ← **`35:1`, the FIRST-pass audio latent** | **`dec_a ← s1_samp:0`** = the pass-2 AV latent, so the 0.9-denoise pass 2 overwrites the pass-1 soundtrack | **`dec_a.samples ← ["s0_sep", 1]`** (published data flow). `HaltExecution` itself is a VRAM-ordering node (decode the audio VAE last), not part of the data flow, so it is not reproduced in an API graph. |
| Model stack | `UNETLoader [30]` → `LoraLoaderModelOnly [36]` *"Load TURBO LoRA (skip if model includes it)"* → `H3PowerLoraStack [101]` (default payload `{"on": false}`) → `MiniMaxH3SigmaShift [38] (12, 3)` → `BlockSparseAttention [100]` → `ModelAttentionBackend [37] "comfy kitchen attention"` → `ModelPreviewOverrideKJ [12]` for the pass-2 guider | `unet → m_attn → m_vsa → m_shift`, both guiders on `m_shift` | **Kept** (same effective settings, minus no-ops): the Turbo LoRA is "skip if the model includes it" and beta7 int8HQ is turbo; `H3PowerLoraStack` and `ModelPreviewOverrideKJ` are **not installed on this box** (the first defaults to off, the second only re-draws previews). These are `model_options` patches, so the order difference is inert. Noted, not copied. |
| VSA | `BlockSparseAttention`: vsa, keep_percent **10**, start 0, end 1, dense_blocks "0,1", min_tokens 12288, extra_tokens 256, sink `exact_kv_and_rows`, verbose false | `m_vsa` identical field for field | no change — matches |
| Sigma shift | `MiniMaxH3SigmaShift` **12 / 3** | `m_shift` 12 / 3 | no change — matches |
| Attention backend | `"comfy kitchen attention"` | same | matches |
| Text encoder | `qwen3vl_32b_minimax_h3_int4_convrot.safetensors` | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | **Kept** — the A/B/C brief's constant, installed, used by arms A, C and v2. |
| Checkpoint | `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` (LokkenJP's own re-quant) | `10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors` | **Kept** — the brief mandates it (Derek's standing beta7 rule). |
| Video / audio VAE | `minimax_h3_video_vae_int8_convrot` / `minimax_h3_audio_vae_fp32` | same | matches |
| Frame count | `ComfyMathExpression [19]` `max(5, round(a*24)) + (5 - (max(5,round(a*24)) % 17)) % 17` from a duration primitive (15 s → 362) | fixed **243** in `c0` | **Kept** — 243 is the brief's constant and is already 17·14+5, a legal H3 clip length. |
| Noise | one `RandomNoise [31]` feeding **both** samplers | one `noise` feeding both ✓ | matches (seed kept **51083002**, B's value) |
| AV assembly | `LTXVSeparateAVLatent [35]` → video → upscaler; `LTXVConcatAVLatent [10]`(upscaled video, **pass-1 audio** `35:1`) → pass 2 | `s0_sep`, `s1_cat` same wiring ✓ | matches |
| Conditioning source | one `MiniMaxH3ReferenceToVideo [11]`, `ref_image_size "match"`, its `positive` fed to **both** guiders | `c0`, `"match"`, fed to both guiders | **#74 fix**: `ref_image_size → "max"`, and each guider's conditioning now goes through an Add Guide node (below) |
| Post-processing | `RTXVideoSuperResolution [39]` scale 1.2 ULTRA, grain 0.005, encoder-preset subgraph, SaveVideo | plain CreateVideo 24 fps → SaveVideo | **Not added** — the brief: "No RTX upscale", final = crf-18 of the raw at native res. |
| Prompt | `PrimitiveStringMultiline [2]` | 13,128-char B prompt | **byte-identical**, no `<Picture 1>` steering sentence (brief rule 3). |

## The #74 Add Guide change (the one deliberate difference from the published graph)

`MiniMaxH3AddGuide` ("Add Guide for MiniMax H3") is a **core** node on this box —
`ComfyUI/comfy_extras/nodes_minimax_h3.py:165`. Its contract, read off that file:
required `positive`, `latent`, `frame_idx`; optional `vae`, `audio_vae`, `image`, `audio`; output = CONDITIONING
(`positive`) — so it is inserted **between** `c0` and each `BasicGuider`, exactly as the discussion says.
Two facts that constrain the wiring:
- `latent` must be a **MiniMax H3 AV latent** (`nodes_minimax_h3.py:194`, it asserts a nested 2-tensor latent whose
  video tensor is 5D with 24 channels), and it takes the target canvas from that latent
  (`height = video.shape[3] * 16`), centre-cropping the guide image to it. So `ag0.latent ← c0:1` (the pass-1 AV
  latent, 384×672) and `ag1.latent ← s1_cat:0` (the pass-2 AV latent, 768×1344) — the latent going into each sampler.
- **`vae` is not optional once an image is connected**: `if vae is None: raise ValueError("anchoring guide frames
  needs the vae input")`. The discussion gives no settings, and the brief says leave the other inputs at defaults —
  an unconnected `vae` with an `image` connected is a hard runtime error, so `vae ← vvae` on both nodes is forced by
  the node, not chosen. `audio`/`audio_vae` are left at defaults (unused, no audio guide).
- `frame_idx = 0` (its own default) = anchor the start image at frame 0, which is what TERRACE2 is.

Nodes added: **`ag0`** (positive `c0:0`, latent `c0:1`, image `img:0`, vae `vvae:0`, frame_idx 0) →
`s0_guide.conditioning`; **`ag1`** (positive `c0:0`, latent `s1_cat:0`, image `img:0`, vae `vvae:0`, frame_idx 0) →
`s1_guide.conditioning`. `img` is the existing `LoadImage community/TERRACE2_768x1344.png`, i.e. both guides are fed
the initial first-frame image. Node count stays 26 (−3 deleted `s0_split`/`s1_sig`/`ksel1`, +3 added `p2sched`/`ag0`/`ag1`).

## Kept constants (unchanged from B)

seed 51083002 · prompt (13,128 chars, byte-identical) · `community/TERRACE2_768x1344.png` ·
beta7 int8HQ · euler · 8 steps on pass 1 · shift 12/3 · VSA keep_percent 10 (0→1, dense "0,1") · 243 frames ·
24 fps · 384×672 → 768×1344 · no RTX.

## Cost note for the fixed graph

B measured 240.1 s = 4 steps at 0.258 MP + 4 steps at 1.03 MP. The fixed graph is 8 steps at 0.258 MP + 3 steps at
1.03 MP ≈ 8×~15 s + 3×~45 s ≈ **~270 s + upscaler/decode**, i.e. in the same band as B (arm A native-8 measured
360.1 s). Not a cost outlier; the second pass got *cheaper* than B's.
