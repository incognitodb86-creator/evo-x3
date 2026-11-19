# CK-ATTN — the Comfy Kitchen attention conflict, settled by one seed-locked A/B (2026-10-25)

Derrick 2026-10-25 6:48 PM CT (MAX block, `fix_plan.md:18`, his pick 3 of six): "Sort out the Comfy
Kitchen attention conflict." This item decides nothing about pixels: KEEP is Derrick's, and no vision
model scored a rendered frame here (PROMPT.md 4, 20:37 line).

## The measured state before the change (23:2x-23:3x CT)

- `C:/AI/community/p7/graphs/`: **18 tracked graphs, 18 carry a `ModelAttentionBackend` node; 17 request
  `comfy kitchen attention` and exactly 1 requests `pytorch attention`**
  (`ali163_hc15_bd002_s51150021`, the NOW-P1 graph). Both 5-second arms
  (`ali163_top5_gi046_s51160001`, arm a, and this item's `ali163_top5_gi046_s51160002`, arm b) sit on
  the int8 checkpoint: `unet = UNETLoader {unet_name:
  "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors"}` = 21,709,633,539 B, and
  `vvae = .../minimax_h3_video_vae_int8_convrot.safetensors`.
- The server does not ask for CK: `C:/AI/director/config/llama-swap.yaml:97` launches `comfyui_auto`
  with `--listen --port 8189 --disable-async-offload --disable-pinned-memory` — no
  `--use-ck-attention`, no `--use-sage-attention`, no `--lowvram`. The request lives in the graph node.
- The checkpoint family is named by its author: `notes/web/hc15_tenstrip_readme.txt:47-48` lists the int8
  builds as the repo `cicalooo/10Eros-Max-h3-int8-convrot`. 21,709,633,539 B is the 21 GB
  `pruned_int8_convrot` row of the ComfyUI docs table (`notes/web/02v_docs_h3.txt:75`).
- The published rule, verbatim: `notes/web/02v_docs_h3.txt:201` — "Templates use **`int8_convrot`**
  checkpoints. **Comfy Kitchen does not support them** (issue #15529). Use default attention, or switch
  `UNETLoader` to **`pruned_bf16`** then change backend." The same sentence is the table footnote at
  `:80`: "Comfy Kitchen attention cannot run `int8_convrot` checkpoints; use a `bf16` build with that
  backend." The bar is the int8 family only: the fp8_scaled / fp32 / bf16 rows (`:77-79`) list "Comfy
  Kitchen attention" as available, and `:214` of `notes/web/01_h3_ckpt_versions.txt` describes it as
  "ComfyUI-Kitchen (comfy-kernel int8 attention)", with `:216` "int8_convrot ... needs the int8 convrot
  mm kernel".
- The other published branch is out of reach on this box: the live `/object_info` `UNETLoader` list
  (`notes/ckattn_20261025_obj_UNETLoader.json`, read 23:32 CT) offers 3 unet files and the only H3 one
  is the int8 file; `pruned_bf16` is 40 GB and `bf16` 66 GB (`notes/web/02v_docs_h3.txt:76,79`) on a
  16 GB RTX 5070 Ti.

## The live schema on this box (ComfyUI system 0.38.0, read 23:32 CT)

`notes/ckattn_20261025_obj_ModelAttentionBackend.json` (+ `..._system_stats.json`, dumped by
`notes/ali173_b2_objinfo.py --only ModelAttentionBackend,BlockSparseAttention,UNETLoader --prefix
ckattn_20261025_obj --full-name ../runs/ckattn_20261025_object_info_full.json`; the 13 MB full dump
went to the gitignored `runs/` so the pinned 2026-10-23 dump the offline gates are validated against
stayed untouched):

- `attention`: options `["pytorch attention", "comfy kitchen attention"]`, **default
  `"pytorch attention"`**, `display_name: "backend"`, tooltip "Comfy Kitchen attention uses quantized
  INT8 attention and is available only on Nvidia and AMD GPUs."
- Node description: "When used with Block Sparse Attention, this backend is used whenever sparse
  attention is inactive or unsupported." So the dense backend is the fallback the sparse node calls, and
  a 124-frame / 1344x768 pass is exactly the regime its own `min_tokens` default (12,288) puts into
  dense mode (`notes/ckattn_20261025_obj_BlockSparseAttention.json`).
- `BlockSparseAttention` in this build: `selection` = DYNAMICCOMBO `sol-attn`(tau 1.3) / `sla`
  (keep_percent 10.0) / `vsa` (keep_percent 10.0, tooltip "FastH3-VSA checkpoints are trained at 10"),
  plus `start_percent` default **0.2**, `end_percent` 1.0, `dense_blocks`, `min_tokens` 12288,
  `extra_tokens` 256, `sink_conditioning`, `verbose`. Our graph's `vsa` / `keep_percent 10` /
  `start_percent 0.2` are those defaults, so the sparse row is at published settings (recorded, not
  changed — one variable per render, IM1).

## The A/B (one variable)

Arm a = the paid `ali163_top5_gi046_s51160001` (rendered 22:52:27-22:56:27 CT by E5, `comfy kitchen
attention`). Arm b = `ali163_top5_gi046_s51160002`, built by `notes/top5_build.py --arm b`.

`A31.diff_paths(arm_a_graph, arm_b_graph)` = **`['m_attn.attention', 'save.filename_prefix']`** —
measured, printed by the gate, and gated by ck `ab`. Node sets equal, prompt text byte-identical
(`notes/top5_prompts.md` carries a second block header for arm b with the identical body, and
`doc_block()` refuses a doc whose two bodies differ, a second seed, a non-`c0` chunk, or an id outside
the two arms), `noise_seed` 51160001 in both, steps 8, scheduler simple, shift 10/3, canvas 1344x768,
guide at frame 0, the same three reference slots and files, VSA `vsa`/10/0.2.

## Objective result — the two clips, off disk

Both read through the render path itself: `C:/AI/director/.venv/Scripts/python.exe
C:/AI/community/scripts/run_graph_job.py <run_dir> <id> --frames 124`, `gpu_guard.ps1` rc 0 = IDLE
before the queue, the gpu-render lock acquired and released inside the run, one job, no restart, no
second queue, no re-queue.

| measure | arm a `...s51160001` (comfy kitchen) | arm b `...s51160002` (pytorch) |
| --- | --- | --- |
| wall, from its own `status.log` | `JOB end ... ok secs=240.2` | `JOB end ... ok secs=300.2` |
| ffprobe v:0 packets / dims / fps | 124 packets, 1344x768, 24/1 | 124 packets, 1344x768, 24/1 |
| container duration | 5.166688 s | 5.166688 s |
| audio (unfiltered `-show_streams`, L20) | 1 audio stream, `audio=True` | 1 audio stream, `audio=True` |
| bytes | 2,923,814 | 2,987,706 |
| SHA-256 | `86352bca1b2962456618a4e8f55cf132612b75af2b9080d3b373fd9f366a5dc8` | `c1eaf35c25087f440f217be68c8b865fb9cbbc632b4c7ac7f6dc844d80a5031c` |
| blackdetect d=0.2 pix_th=0.10 | 0 detections | 0 detections |
| `objective.json` / `status.log` / output dir | all three = PAID | all three = PAID |

Between the two arms (`ffmpeg -lavfi ssim` / `psnr`, same seed so a difference is the backend):

- SSIM `Y:0.697382 U:0.965288 V:0.973061 All:0.787980 (6.736228)`, per-frame last row
  `n:124 Y:0.679446 ... All:0.776236` (stats file `runs/ckattn_ssim.log`).
- PSNR `y:22.902205 u:39.062338 v:40.922172 average:24.619919 min:21.326778 max:35.649020`.

No peak-VRAM number is claimed: the log streams I can read this pass
(`C:/AI/director/logs/llama-swap.out.log`, last 3 MB) carry no ComfyUI VRAM/`out of memory` line for
this window, so an 11.4-vs-16 GB ceiling is not measured here (L4: no unmeasured number).

## The answer

1. **On this box, with this int8/convrot checkpoint, ComfyUI 0.38.0 runs both values.** Arm a (CK)
   rendered twice (15:35 CT the 15 s line, 22:52 CT the 5 s clip) and arm b (pytorch, the schema
   default and the published value for this family) rendered at 23:41-23:46 CT. The published
   incompatibility is not enforced by this build at 124 frames / 8 steps: it produced no failure, no
   fallback log, no OOM.
2. **CK is the faster path here: 240.2 s vs 300.2 s for the same 124-frame clip = 60 s (20 % of the
   pytorch wall) and 2.1 % smaller output bytes.** If the paid CK clip is the one Derrick keeps, the
   cost of keeping the published-incompatible value is 0 s and it buys 60 s per 5-second clip.
3. **The backend is a real image variable, not a no-op:** SSIM 0.79 luma / PSNR 24.6 dB average between
   same-seed arms. Any A/B that moves attention must therefore be judged on pixels by Derrick, not
   assumed equivalent (no KEEP claim here).
4. **The graph states the value on purpose now.** `notes/top5_build.py` gate 19 `attention` reads the
   unet file, classifies the quant family by the published naming, reads the live options/default, and
   names the conflict with its citations. Gate 20 `ab` bounds the A/B to one key. `--check --arm b` =
   `VERDICT TOP5 CHECK CLEAN (20 checks, 0 findings, arm b ali163_top5_gi046_s51160002)`.
   `--check` (arm a) = `VERDICT NOT CLEAN 1 of 20`, `FAIL attention :: ATTENTION-CK-INT8 ...` with the
   doc/README/schema citations inline — the paid graph's disclosed state, not a regression.
   `--selftest --arm b` = `SELFTEST OK arm b ...: 23 seeds fire their named check, 0 silent, 0 findings
   on the real graph, 4 paid-state probes and 4 attention behaviour probes all read as designed`;
   `--selftest` (arm a) = `SELFTEST OK arm a ...: 20 seeds fire, the paid graph fires only the disclosed
   attention conflict, 4 paid-state probes and 4 attention behaviour probes read as designed`. The
   attention probes are the L10 form: the paid CK-on-int8 wiring FIRES `ATTENTION-CK-INT8`; a real fp8
   file (`FLUX-KLEIN-9B-FP8-NSFW.safetensors`) + CK stays CLEAN, so the rule is a published rule, not a
   ban; an off-disk bf16 name prints `ATTENTION-UNET-MISSING`; a value outside the live options prints
   `ATTENTION-VALUE-OUTSIDE-SCHEMA`.
5. **Nothing else in the tree moves.** 17 other graphs keep asking for CK; this item does not rewrite
   shipped, paid graphs. The gate protects what is emitted from here, and `ATTENTION-CK-INT8` names the
   same condition in any of them if they are ever re-emitted through this builder.

## Rows for needs_derrick (recorded, not acted on)

- **VSA vocabulary, the sharp version.** The live `vsa` tooltip says "Percent of video cubes each query
  cube keeps; **FastH3-VSA** checkpoints are trained at 10"
  (`notes/ckattn_20261025_obj_BlockSparseAttention.json`), while the checkpoint's author writes "with
  **Fastv2** VSA sparse node settings ... **SLA sparsity seems to destroy it**, avoid using that on any
  workflows" (`notes/web/hc15_tenstrip_readme.txt:16`) and recommends "Full gates, Fastv2
  turbo/VSA gates" as his ideal (`:15-16`). Our graph uses `vsa` at `keep_percent 10`,
  `start_percent 0.2` = the live schema defaults, so the settings are published-default; the open
  question is only which sparse family this Fastv2-turbo checkpoint was trained against. Unresolvable
  from the docs on disk; it is your "Comfy Kitchen attention conflict" row's second half, so it stays
  yours (PROMPT.md 20:36).
- **Corrections to the E5 row's recorded numbers** (`notes/top5_euler_5s_20261025.md:33-35`), measured
  off that run's own files this pass: its clip is **2,923,814 bytes** (not 3,582,464), its canvas is
  **1344x768** (not 1024x576), and its wall is **240.2 s** per its `status.log` (not 3,375,622 ms).
  Its graph SHA `47f4163b134115229d72840899e2523952223747859448e8323ea26299816a1d` and the 124/124
  packet count check out. L12 again: a clean pass is measured off disk, never from a plan.
