---
language: en
license: apache-2.0
tags:
- gguf
- qwen35
- qwen3.5
- prompt-enhancer
- text-to-video
- uncensored
- sulphur
- ltx
- comfyui
- llama.cpp
- lm-studio
- multimodal
- vision
base_model: SulphurAI/Sulphur-2-base
pipeline_tag: text-generation
library_name: llama.cpp
---

# Sulphur-2 Prompt Enhancer Uncensored - GGUF

Quantized GGUF files for the uncensored prompt enhancer from [SulphurAI/Sulphur-2-base](https://huggingface.co/SulphurAI/Sulphur-2-base/tree/main/prompt_enhancer_uncensored). Converts short prompts into detailed video generation prompts for LTX 2.3 / Sulphur-2.

## Model Info

| Field | Value |
|-------|-------|
| Base | Qwen3.5-9B (multimodal) |
| Architecture | qwen35 |
| Context | 262,144 tokens |
| Blocks | 32 layers |
| Embedding | 4096 |
| Uncensoring | Rimuru A+(B-C) merge, B=Hauhau |

## Files

| File | Size | BPW | Description |
|------|------|-----|-------------|
| `prompt_enhancer_uncensored-Q4_K_M.gguf` | 5.3 GB | 5.02 | Standard 4-bit k-quant (balanced) |
| `prompt_enhancer_uncensored-IQ4_NL.gguf` | 5.1 GB | 4.85 | Importance-aware 4-bit (non-linear) |
| `mmproj-prompt_enhancer_uncensored.gguf` | 880 MB | — | Vision projector (BF16) |

Converted from BF16 safetensors → F16 GGUF → quantized with llama.cpp. No requantization — clean F16 source.

## Usage

### ComfyUI

Drop both the model GGUF and mmproj into `ComfyUI/models/text_encoders/` or `ComfyUI/models/LLM/GGUF/`. Use with [ComfyUI-Qwen3.5-Uncensored](https://github.com/Deaquay/ComfyUI-Qwen3.5-Uncensored) node.

### LM Studio / llama.cpp

```bash
llama-server -m prompt_enhancer_uncensored-Q4_K_M.gguf \
  --mmproj mmproj-prompt_enhancer_uncensored.gguf \
  -ngl 99 --host 0.0.0.0
```

## Source

- Original model: [SulphurAI/Sulphur-2-base](https://huggingface.co/SulphurAI/Sulphur-2-base)
- Quantized by [PeppX](https://huggingface.co/PeppX)
