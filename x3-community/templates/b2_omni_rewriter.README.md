# b2_omni_rewriter.api.json - B2 RefMod + Dedicated Omni Prompt Rewriter Pipeline

Last Updated: 2026-11-12

## Purpose

Wires the dedicated LightX2V MiniMax-H3 prompt rewriter ([pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI](https://github.com/pytraveler/MiniMax-H3-Prompt-Rewriter-ComfyUI) v0.34.0+) directly ahead of H3 (`c0` `MiniMaxH3ReferenceToVideo`) in Render's ComfyUI pipeline.

## Pipeline Architecture

1. **`img_1` (`LoadImage`)**:
   Loads the reference still image from `ComfyUI/input/community/...`.
2. **`rewriter_options` (`MiniMaxH3RewriterOptions`)**:
   - `adapter`: `MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]` (from `ComfyUI/models/LLM/MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF/`)
   - `max_new_tokens`: `4096` (official recommendation; overrides node 2048 default)
   - `temperature`: `0.7`
   - `top_p`: `0.9`
   - `top_k`: `20`
   - `repetition_penalty`: `1.05`
   - `auto_download`: `False` (local files only)
   - `gpu_layers`: `-1` (all offloaded to GPU during rewrite)
   - `n_ctx`: `8192`
3. **`rewriter` (`MiniMaxH3PromptWriterOmni`)**:
   - `model`: `Qwen2.5-Omni-7B GGUF Q4_K_M · 6.2 GB download · ~9 GB with the adapter and a 12k context`
   - `task`: `REF2VA`
   - `resolution`: `768x1344`
   - `duration`: `10.0`
   - `greedy`: `True` (official Omni greedy sampler; do_sample off)
   - `seed`: `42`
   - `keep_model_loaded`: `False` (CRITICAL: unloads the 7B Omni model immediately upon rewrite completion so all 16 GB VRAM is freed for H3 DiT sampling)
   - `options`: connects to `["rewriter_options", 0]`
   - `ref_0`: connects to `["img_1", 0]`
4. **`c0` (`MiniMaxH3ReferenceToVideo`)**:
   - `prompt`: receives `["rewriter", 0]` directly from the rewriter node.
   - All standard H3 conditioning, resolution (768x1344), length (192 frames default), and VAE bindings remain intact.
5. **`out_rewritten_prompt` (`PreviewAny`)**:
   - Captures output 0 (`rewritten_prompt`) for history/inspection without altering pipeline execution.
6. **H3 Sampling & Decoding (`s0_guide`, `s0_samp`, `refapply`, `refmods`, `mkvid`, `save`)**:
   - Identical to `b2_refmod.api.json` frozen dial.

## Weights Used

- **Base GGUF + mmproj**:
  - `ComfyUI\models\LLM\Qwen2.5-Omni-7B-GGUF\Qwen2.5-Omni-7B-Q4_K_M.gguf` (4.68 GB)
  - `ComfyUI\models\LLM\Qwen2.5-Omni-7B-GGUF\mmproj-Qwen2.5-Omni-7B-Q8_0.gguf` (1.55 GB)
- **Adapter GGUF**:
  - `ComfyUI\models\LLM\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-GGUF\MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf` (343.2 MB)
  *(Note: `adapter_model.safetensors` is NOT attached to the GGUF node)*
- **Second Arm (Fallback)**:
  - `ComfyUI\models\LLM\Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf` (5.63 GB)
