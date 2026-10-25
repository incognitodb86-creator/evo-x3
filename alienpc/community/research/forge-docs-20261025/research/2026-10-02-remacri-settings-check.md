# Remacri settings check — 2026-10-02

Scope: 864×480, 124-frame I2V, 16GB RTX 5070 Ti, target 1920×1066. No new generate.

## Graph note (read)

`C:\Users\derek\Desktop\MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02\clips\ai\SCH_WARM_BETA_1080_AI_NOTE.txt` (machine ecc21911). Not on the box copy (`/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/clips/ai` is empty).

Quoted path line:

> CRT_UpscaleModelAdv absent (CRT-Nodes import fail, soundfile). Used Remacri 4x_foolhardy_Remacri.pth via ImageUpscaleWithModelBatched per_batch=1 precision=float16 downscale_ratio=0.56 lanczos, then ImageScale lanczos 1920x1066, VHS nvenc_h264-mp4.

Also in that note: out 1920×1066, 24fps, 124f, ~5.17s, bytes=7479514, wall **76.1s** (prompt 4b837071). The ~83s figure is the other clip, not this note.

Arithmetic from those dims only: 864×4=3456, 480×4=1920. Exact width ratio 1920/3456=0.555… . 0.56×3456=1935.36 and 0.56×1920=1075.2, then a second Lanczos to 1920×1066. Effective scale vs source is 1920/864≈2.222, not 4 and not 2.

## Knob verdicts

| Knob | Verdict | Why |
|---|---|---|
| Model `4x_foolhardy_Remacri.pth` | **RIGHT** | OpenModelDB: ESRGAN, scale **4x**, 64nf 23nb, RGB. Author text: interpolated so skin and detail “don’t become mushy and blurry.” https://openmodeldb.info/models/4x-Remacri |
| Run the 4x net, then resize (not a 2x Remacri) | **RIGHT** | No 2x Remacri on that page. Real-ESRGAN `enhance()` runs the network at `self.scale`, then **one** `cv2.INTER_LANCZOS4` only if `outscale != scale`. https://github.com/xinntao/Real-ESRGAN/blob/master/realesrgan/utils.py . Civitai’s 4x-Remacri recipe: multiply 4×, then one resize to 1920 wide. https://developer.civitai.com/orchestration/recipes/image-upscaler . chunks.md Speed preset (2x output): “The engine still runs the 4x model before downsampling.” https://chunks.md/4x-remacri-online |
| `downscale_ratio=0.56` **and** a second ImageScale Lanczos to 1920×1066 | **WRONG** (double resample) | KJNodes: models are fixed 4x; set `downscale_ratio` below 1 to land the final size; default method lanczos; ratio step 0.01, default 1. https://comfy.icu/node/ImageUpscaleWithModelBatched . 0.56 is the hundredth above 0.555…, so it does **not** hit 1920×1066. The following ImageScale is a second Lanczos. Official pattern is one Lanczos after the 4x pass. |
| `per_batch=1` | **RIGHT** | Same node: default 16; drop to 8, 4, or **1** if VRAM is tight. 1 is slowest and does not change the weights. 124 frames at a 3456×1920 intermediate on 16GB. This run finished (76.1s). No published per-batch number for a 5070 Ti 16GB. |
| `precision=float16` | **MIXED, keep** | KJNodes default is float32; float16 is the documented VRAM cut “at a small quality risk.” Real-ESRGAN CLI default is fp16 (`--fp32` opts out). https://github.com/xinntao/Real-ESRGAN/blob/master/inference_realesrgan.py . CRT `precision=auto` is fp16 on CUDA. https://comfy.icu/node/CRT_UpscaleModelAdv . Not a cited cause of plastic skin. |
| No tile | **RIGHT** for this run | Batched node has no tile input. RealESRGANer tile default is **0** (no tile). Tile is the OOM fallback: “If you encounter CUDA out of memory, try to set --tile with a smaller number.” This job did not OOM. No Remacri or 16GB tile size is published on OpenModelDB or in that argparse. Do not invent 512. |
| CRT wrapper skipped | **RIGHT** | Note: `CRT_UpscaleModelAdv` missing because CRT-Nodes failed on `soundfile`. That node’s defaults are tile_count **1** (no tile), batch_size **1**, precision **auto** (fp16 on CUDA). It can do fixed 1920×1066 in one step. Skipping it did not pick a wrong model. Reinstall only to collapse the two resizes, not to fix hands. |
| Plastic look; hands/contact still bad | **Not a bad knob** | OpenModelDB and Upscayl-comparison writeups treat Remacri as the **less** mushy / less plastic choice vs Real-ESRGAN, with a grain-on-flat-areas tradeoff. https://chunks.md/4x-remacri-online https://whichoneisreal.com/compare/ai-image-upscaler/ . KJNodes: frame upscalers are not temporal and do not repair motion. A plain model upscale does not invent missing anatomy. Hands/contact stay a generate problem. |

## One next setting

Set `downscale_ratio=1` and keep a **single** ImageScale Lanczos to 1920×1066 (or, if CRT imports, `use_fixed_resolution` 1920×1066, `tile_count=1`). Leave model, fp16, and `per_batch=1` alone. Do not switch to a 2x model for this file: this weights file is 4x-only.

nvenc rate is not in the note, so the encode is not scored.
