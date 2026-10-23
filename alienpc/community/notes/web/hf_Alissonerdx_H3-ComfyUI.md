---
license: other
license_name: mixed-asset-licenses
license_link: https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/blob/main/LICENSES.md
base_model:
  - MiniMaxAI/MiniMax-H3
tags:
  - lora
  - video
  - comfyui
  - minimax-h3
---

# MiniMax H3 LoRAs for ComfyUI

Experimental LoRAs for [MiniMax H3](https://huggingface.co/MiniMaxAI/MiniMax-H3), packaged for
ComfyUI and tested mainly with the
[`ref2va` weights](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/main/diffusion_models).

These are research models, not finished tools. Results vary substantially with the source clip,
resolution, prompt and reference images.

## Models

| Model | Purpose | Trigger | Documentation | Workflow |
|---|---|---|---|---|
| [`minimax_h3_lms_v1.0_r64`](loras/minimax_h3_lms_v1.0_r64.safetensors) | Sharpness/detail enhancement using an aligned source-video guide | Fixed enhancement caption | [LMS / Sharpness guide](docs/lms.md) | [`minimax_h3_lms_workflow.json`](workflows/minimax_h3_lms_workflow.json) |
| [`minimax_h3_style_transfer_v1.0_r64`](loras/minimax_h3_style_transfer_v1.0_r64.safetensors) | Transfer a visual style from an image or text description onto a video | `style_transfer:` | [Style Transfer guide](docs/style-transfer.md) | [`minimax_h3_style_transfer_workflow.json`](workflows/minimax_h3_style_transfer_workflow.json) |
| [`minimax_h3_vfx_edit_v1.0_r128`](loras/minimax_h3_vfx_edit_v1.0_r128.safetensors) | General prompt-directed VFX editing with an aligned source video | `vfx_edit:` | [VFX Edit guide](docs/vfx-edit.md) | [`minimax_h3_vfxedit_wokflow.json`](workflows/minimax_h3_vfxedit_wokflow.json) |
| [`minimax_h3_vfx_edit_v1.0_r128_ffp`](loras/minimax_h3_vfx_edit_v1.0_r128_ffp.safetensors) | Higher-resolution VFX Edit version with experimental first-frame propagation | `vfx_edit:` | [VFX Edit and FFP guide](docs/vfx-edit.md) | [`minimax_h3_vfxedit_wokflow.json`](workflows/minimax_h3_vfxedit_wokflow.json) |
| [`minimax_h3_head_swap_v1.0_r32`](loras/minimax_h3_head_swap_v1.0_r32.safetensors) | Experimental reference-image head replacement over an aligned source video | `head_swap:` | [Head Swap guide and prompt template](docs/head-swap.md) | [`minimax_h3_head_swap_workflow.json`](workflows/minimax_h3_head_swap_workflow.json) |
| [`minimax_h3_character_swap_v1.1_ref2va_fro`](loras/minimax_h3_character_swap_v1.1_ref2va_fro.safetensors) **(recommended)** | Replace the main guide subject with the character in a reference image while following the guide performance; 80 MB SVD extraction | `body_swap:` | [Character Swap guide, prompt template and examples](docs/character-swap.md) | [Shot Planner](workflows/minimax_h3_character_swap_workflow_v1.1.json) / [native nodes](workflows/minimax_h3_character_swap_workflow_native_nodes_v1.1.json) |
| [`minimax_h3_character_swap_v1.0_ref2va_r64_gl`](loras/minimax_h3_character_swap_v1.0_ref2va_r64_gl.safetensors) | Previous Character Swap release (rank 64) | `body_swap:` | [Character Swap guide](docs/character-swap.md) | [Shot Planner](workflows/minimax_h3_character_swap_workflow_v1.0.json) / [native nodes](workflows/minimax_h3_character_swap_workflow_native_nodes_v1.0.json) |
| [`minimax_h3_live_wallpaper_v1.0_ref2va_r32`](loras/minimax_h3_live_wallpaper_v1.0_ref2va_r32.safetensors) | Animate one to three reference images; often more faithful to facial features, but with less predictable camera behavior | `live_wallpaper:` | [Live Wallpaper guide](docs/live-wallpaper.md) | [`minimax_h3_live_wallpaper_workflow.json`](workflows/minimax_h3_live_wallpaper_workflow.json) |
| [`minimax_h3_live_wallpaper_v1.0_ref2va_r64`](loras/minimax_h3_live_wallpaper_v1.0_ref2va_r64.safetensors) | Camera-aware continuation of R32 for prompt-directed camera behavior and temporal reference frames | `live_wallpaper:` | [Live Wallpaper guide](docs/live-wallpaper.md) | [`minimax_h3_live_wallpaper_workflow.json`](workflows/minimax_h3_live_wallpaper_workflow.json) |

## Latent Upscaler

[`h3_upscaler_lms_v0.1`](latent_upscaler/h3_upscaler_lms_v0.1.safetensors) is the recommended FP16
release of an experimental latent-upscaler checkpoint. It was trained for 2,000 steps with the same
sharpness dataset used for the LMS LoRA and initialized from the
[LBH-123-AI/Minimax_h3_latent_Upscaler](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler)
project and its
[`minimax_h3_latent_upscaler_3d_fp16.safetensors`](https://huggingface.co/LBH-123-AI/Minimax_h3_latent_Upscaler/blob/main/minimax_h3_latent_upscaler_3d_fp16.safetensors)
checkpoint.

See the [Latent Upscaler guide](docs/latent-upscaler.md) for setup, scope and limitations.

## Common setup

Place LoRAs in `ComfyUI/models/loras/`. The included workflows list their required models and
custom nodes inside the graph. Keep the output aspect ratio matched to the source clip and use an
H3-supported frame count (`17n + 5`: 5, 22, 39, 56, 73, 90, 107, 124, ...).

The LMS, Style Transfer, VFX Edit and Head Swap models use an aligned source-video guide through
`MiniMaxH3AddGuide` at `frame_idx = 0`. This is different from a native image/video reference:
the guide shares the generated video's spatial and temporal grid.

## License and credits

Licenses are specified by asset. The separate [Character Swap license](LICENSE_CHARACTER_SWAP.md)
applies only to the Character Swap LoRA weight files listed in
[LICENSES.md](LICENSES.md); it does not apply to the other LoRAs, workflows, docs, or examples.
Use of the Character Swap LoRA, including commercial use in videos and films, requires no prior
permission. Organizations with over US $1,000,000 in annual gross revenue must credit its origin
for commercial use. Offering the LoRA as a hosted API, SaaS, or other remote model service is not
allowed. See the [full license](LICENSE_CHARACTER_SWAP.md) and check each other asset's applicable
terms before use.

Base model credit to [MiniMaxAI](https://huggingface.co/MiniMaxAI/MiniMax-H3), ComfyUI-ready
weights to [Comfy-Org](https://huggingface.co/Comfy-Org/MiniMax-H3), and guide-latent training
support to [ostris/ai-toolkit](https://github.com/ostris/ai-toolkit) and
[ComfyUI-AIToolkit-MiniMaxH3](https://github.com/ostris/ComfyUI-AIToolkit-MiniMaxH3).
