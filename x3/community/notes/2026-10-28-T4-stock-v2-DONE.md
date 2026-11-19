# 2026-10-28 T4 — stock LokkenJP `simple_v2`, the true community baseline

**Status: IN PROGRESS — blocked on ~34 GB of model downloads.** No render yet, no GPU used.
Brief: `notes/2026-10-28-max-brief-T4-stock-simple-v2.md`. Plan arm: T4.

## What is done

**1. The stock workflow is downloaded and pinned.**

- Source: `LokkenJP/TenEros_Max_optimized_learned` →
  `SampleWorkFlowTwoPassOptimized/H3_Turbo_2Pass_ErosMax_b7_simple_v2.json`
- Saved untouched as `runs/terrace_dom_q5stockv2_20261028_s51083011/stock_simple_v2.json`
- **76,320 bytes**, `sha256=a315ac74a24a14d46ee5f7569d36993f71019bad0a9077bddcec9aae0c10949a`
  (matches the HF repo's own tree hash for the file), 35 nodes, 50 links, 3 UUID subgraphs.
- Full read-out for the audit trail: `runs/…/t4_inspect.txt` (629 lines: every node, widget,
  link, group, and the subgraph definitions).

**2. The stock dials, read from the file itself (these are the values the render will use).**

| Dial | Stock value in the JSON |
|---|---|
| Checkpoint (node 30) | `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` |
| Text encoder (node 15) | `qwen3vl_32b_minimax_h3_int4_convrot.safetensors` |
| Video / audio VAE (3 / 4) | `minimax_h3_video_vae_int8_convrot` / `minimax_h3_audio_vae_fp32` — already installed, present |
| Turbo LoRA (node 36) | `Minimax_H3\minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`, **`mode=4` = BYPASSED as shipped** ("skip if model includes it") |
| LoRA stack (101) | `H3PowerLoraStack` quantized_layers `auto`, adaln_port `auto`, its one LoRA row `on=false` — a pass-through as shipped |
| Attention (100 / 37) | `BlockSparseAttention` `vsa` keep_percent **10** → `ModelAttentionBackend` **`comfy kitchen attention`** |
| Sigma shift (38) | video **12.0**, audio **3.0** |
| Sampler (18) | **`er_sde`** — one `KSamplerSelect`, feeds both passes |
| Pass-1 scheduler (24) | **`sgm_uniform` / 8 steps / denoise 1.0** |
| Pass-2 scheduler (102) | `beta` / 3 / 0.4 |
| Resolution (20) | `ResolutionSelector` method **`scale to multiple 32`**, `mp_v1` **0.3 MP**, ratio **`4:3`** |
| Latent upscaler (26, inside the subgraph) | `minimax_h3_latent_upscaler_3d_fp16.safetensors`, mode **`megapixels` 1.0**, align 32, `enable_temporal_chunking=true`, force_unload true, cuda/fp16 |
| R2V (11, inside) | `ref_image_size` **`match`**; `length` is NOT a widget — it is computed by node 19 `ComfyMathExpression` `max(5, round(a*24)) + (5 - (max(5,round(a*24)) % 17)) % 17` from duration `a` = **15.0 s** (node 17) |
| Add Guide (181 / 182) | **`mode=4` = BYPASSED as shipped**, fed by a rgthree Mute/Bypass relay that follows the LoadImage |
| Start image (9) | **`mode=4` = BYPASSED as shipped** — the title says `not reference-only (bypass for T2V)`: as shipped this workflow is **text-to-video**, the image is unwired |
| Preview (12) | `ModelPreviewOverrideKJ` max_resolution 1024, 80 px, `tiny_vae=true` → **`taeh3.safetensors` is loaded at runtime**, preview frames 9, fps 12, tiny VAE name `taeh3.safetensors` |
| Post-process (152) | the Lokken encode subgraph: RTX-upscaled frames, **grain 0.005**, H.264 preset `medium`, full prefix `video/ErosMaxH3_b7_TURBO_2Pass`, preview prefix `video/Preview_ErosMaxH3_b7_TURBO`, preview-mode switch **false** (full render) |
| RTX VSR (39) | `scale by multiplier` **1.2**, quality **ULTRA**, strength 1, 10-bit RGB |
| Save (40) | `SaveVideo` |

Structural note that decides the build: node 39 `RTXVideoSuperResolution` consumes the generator
subgraph's IMAGE and its `upscaled_images` is wired *back* into the same subgraph as
`run_after` ("Wait for RTX"). In UI form that is a legal ordered dependency; in API form the
cycle must be kept as the one-directional pair (generator → RTX, generator → encode) and the
`run_after` ordering input is what the subgraph uses internally to gate its encode step. The
converter has to prove what it did with that link, not silently drop it.

**3. Missing models — all four are fetchable, none needs a substitute.**

| File the stock graph names | Status | Source found |
|---|---|---|
| `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` | MISSING | `LokkenJP/TenEros_Max_optimized_learned` (root), **18,691,644,302 B**, ships a `.sha256` sidecar |
| `qwen3vl_32b_minimax_h3_int4_convrot.safetensors` | MISSING | **`Merserk/MiniMax-H3-INT4-ConvRot`**, exact filename, **14,952,506,624 B** (the official `Comfy-Org/MiniMax-H3` tree has only bf16 / int8_convrot / nvfp4_awq, so this community repo is the name's home — it is the same name the Lokken doc names) |
| `minimax_h3_latent_upscaler_3d_fp16.safetensors` | MISSING | `Asirus/Minimax-H3-Latent-Upscaler-BF16-MAXQUALITY` **690,592,672 B**; byte-identical size in `PixelAlchemist123/Minimax_h3_latent_Upscaler` → SHA will be cross-checked between the two mirrors before use |
| `taeh3.safetensors` (preview tiny VAE) | MISSING | `OzzyGT/taeh3` **22,709,752 B**; same size in `Alissonerdx/Minimax-H3-ComfyUI/vae_approx/` → cross-check |
| `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` | MISSING, **not needed** | the LoRA node is `mode=4` BYPASSED as shipped, so the file is never loaded; `lightx2v/Minimax-h3-Turbo` is the home if it is ever wanted |
| video VAE, audio VAE | PRESENT | `models/vae/` |

Total to fetch **≈ 34.4 GB**. Disk: **198 GB free** → ~163 GB after, above the runtime's
keep-40-GB-free rule. Downloads are CPU/network only, so they run before the GPU window and
cost no GPU time.

**4. Missing custom nodes.**

Needed and **not installed**: `H3PowerLoraStack` (`cicalooo/ComfyUI-H3-PowerLoraStack`).
Needed and **installed**: `ResolutionSelector` (ComfyUI-Custom-Scripts), `ModelPreviewOverrideKJ`
(ComfyUI-KJNodes), `RTXVideoSuperResolution` (Nvidia_RTX_Nodes_ComfyUI), `Seed (rgthree)` /
Mute-Bypass (rgthree-comfy), `ComfyMathExpression` (ComfyMath), `ComfySwitchNode`
(ComfyUI-Custom-Scripts), `MinimaxH3LatentUpscaler3D` (Comfyui_Minimax_h3_latent_Upscaler),
plus the core `MiniMaxH3*` / `LTXV*` / `HaltExecution` nodes.
There is no `LokkenVideoPostProcessing` node in this workflow — the post-process is the author's
own **subgraph** (`f115c91c…` "Encode video + first-pass audio"), so nothing to install for it.
The local node-name dump from 16:46 (`notes/objinfo_20261028.json`) is **not authoritative** — it
has no `HaltExecution` entry, and B2 ran with `HaltExecution` at 17:46 from the same runtime. So
the class check for T4 will be a **live `/object_info` probe inside the GPU window, before the job
is submitted**; a missing class aborts with no render.

## What is left, in order

1. Fetch the four files into the runtime's model dirs with size + SHA verification
   (`t4_fetch_models.py`), cross-check the two mirrored files by SHA256, verify the UNet against
   the author's `.sha256` sidecar.
2. Install `ComfyUI-H3-PowerLoraStack`.
3. Write `wf2api.py` + `build_graph.py`: expand the three subgraphs, drop the frontend-only
   nodes, apply the shipped `mode=4` bypass semantics literally (LoRA node pass-through, Add Guide
   pass-through, LoadImage unwired), then apply **only** the five brief deviations plus the extra
   raw save, and write `graph_diff.txt` from a mechanical comparison against the converted stock
   graph. The widget mapping is derived from each node's own widget-marked `inputs` order
   (`t4_map_check.py`), with a loud abort on any count mismatch.
4. Guard, live class probe, one GPU window, ffprobe, upload, and the DONE note.

## Deliberate deviations to be listed in `graph_diff.txt` (the brief's list, nothing else)

- **(a) start image** — the brief requires B2's start image, so the LoadImage that ships
  `mode=4` (unwired, T2V) is set to `mode=0` and wired, with `image = community/TERRACE2_768x1344.png`
  (B2's `LoadImage` widget). This turns a shipped T2V graph into I2V; it is the brief's
  deviation, stated here in advance.
- **(b) prompt** — the `PrimitiveStringMultiline` value becomes B2's 13,128-char prompt,
  read from `runs/terrace_dom_q5guide_20261028_s51083007/prompt_seg0.txt`, bytes unchanged
  (`sha256=fcad1c379bf097f3…`).
- **(c) seed** — the rgthree Seed node's `-1` (random) becomes `51083002`, control-after-generate
  fixed.
- **(d) length** — stock `length` is a formula output (duration 15.0 s → 362 frames at 24 fps);
  the deviation breaks that link and sets `length = 243` directly, which is the value B2 renders.
- **(e) filename_prefix** — the full-resolution prefix primitive becomes
  `community/terrace_dom_q5stockv2_20261028_s51083011/terrace_dom_q5stockv2_20261028_s51083011`.
- **extra raw save** — one added `CreateVideo` + `SaveVideo` pair on the generator's **native
  pre-RTX** IMAGE + the generated audio, prefix `…/<tag>_raw`, as the brief's "extra output only".
  The shipped RTX chain is kept as-is.

Everything else — er_sde, sgm_uniform 8, beta 3/0.4, 0.3 MP 4:3 at multiple-32, 3d_fp16 at
1.0 MP, `match`, Add Guide bypassed, RTX 1.2 ULTRA, grain 0.005, H.264 `medium`, preview
switch false — stays exactly as shipped.

## Queued work noted, not started

Max's block now also has **T5** (pass-1 12 + 1.0 MP, graph only, no render), **T6** (T5 render),
**T7** (T5 with the lock, render). This session is T4; the queue order is T4 → T5 → T6 → T7,
one GPU window per render, and T6/T7 only run when their turn arrives.
