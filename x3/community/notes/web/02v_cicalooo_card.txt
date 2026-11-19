---
library_name: comfyui
license: other
license_name: minimax-h3-community-license-agreement
license_link: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
tags:
- comfyui
- int8
- convrot
- diffusion-model
base_model:
- TenStrip/10Eros-Max
---

# 10Eros-Max H3 — INT8 ConvRot

Native ComfyUI INT8 ConvRot conversions of [TenStrip/10Eros-Max](https://huggingface.co/TenStrip/10Eros-Max).

## Available models

### TURBO Hybrid Beta3

- [Full INT8 ConvRot](10Eros_Max_h3_TURBO-hybrid_beta3_int8_convrot.safetensors) — 200 quantized layers.
- [INT8 ConvRot with skip edges](10Eros_Max_h3_TURBO-hybrid_beta3_int8_convrot_skip_edges.safetensors) — 184 quantized layers; blocks 0, 1, 48, and 49 remain at BF16.

See [SKIP_EDGES.md](SKIP_EDGES.md) for a detailed explanation of the skip-edges variants.

### Beta2

Existing Beta2 INT8 ConvRot variants remain available:

- `10Eros_Max_h3_TURBO_ref2va_beta2_int8_convrot.safetensors`
- `10Eros_Max_h3_TURBO_ref2va_beta2_int8_convrot_skip_edges.safetensors`
- `10Eros_Max_h3_fl2va_beta2_pruned_int8_convrot.safetensors`
- `10Eros_Max_h3_fl2va_beta2_pruned_int8_convrot_skip_edges.safetensors`
- `10Eros_Max_h3_ref2va_beta2_pruned_int8_convrot.safetensors`
- `10Eros_Max_h3_ref2va_beta2_pruned_int8_convrot_skip_edges.safetensors`

## Conversion format

- Native ComfyUI `int8_tensorwise`
- Per-channel absmax quantization
- ConvRot enabled
- Groupsize: 256
- Source precision: BF16

The skip-edges variants preserve the model’s boundary blocks at higher precision and are the more conservative quality-focused option.

## Usage

Place the selected file in:

```text
ComfyUI/models/diffusion_models
```

Use a ComfyUI version with native INT8 ConvRot support.

## License

This model follows the [MiniMax H3 Community License Agreement](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE). Review the license terms before use or redistribution.
