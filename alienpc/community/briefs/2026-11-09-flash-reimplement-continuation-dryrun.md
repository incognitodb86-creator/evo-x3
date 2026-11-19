# 2-Beat Native Continuation Dry-Run Node List & Frame Math

**Date:** 2026-11-09  
**Execution:** In-memory dry run via `build_request.py` and `submit_parody_run.py` (no GPU, no ComfyUI queue, no render).  
**Subject:** Megan Fox (Jennifer Check)  
**Configuration:** 768x1344 canvas, 24 fps, 8 steps, beta7_int8HQ UNET, INDEX + RefMod retention 1.0.

---

## 1. Frame Arithmetic & Window Plan

| Parameter | Beat 1 (Base) | Beat 2 (Continuation) | Total / Deliverable |
| :--- | :--- | :--- | :--- |
| **Beat Index** | 1 (`c0`) | 2 (`c2`) | 2 beats in 1 clip |
| **Is Continuation** | `False` | `True` | - |
| **Base Frames** | 192 (8.0000 s) | 192 | - |
| **Overlap Frames** | 0 | 22 (0.9167 s, hidden) | 22 (trimmed by append) |
| **Extension Frames** | - | 187 (7.7917 s) | 187 new frames |
| **Sampled Window** | 192 frames (<= 243) | 209 frames (<= 243) | Max window = 209 <= 243 |
| **Cumulative Output** | 192 frames | 379 frames (15.7917 s) | **379 frames (15.7917 s)** |
| **Grid Checks** | (192 - 5) % 17 == 0 (11k+5) | (22 - 5) % 17 == 0; 187 % 17 == 0 | Valid H3 17k+5 audio grid |
| **Stitched** | `False` | `False` | **`False` (Single mp4)** |

---

## 2. Complete Graph Node List (28 Nodes)

```
Node ID         | Class Type                          | Title / Inputs
----------------|-------------------------------------|------------------------------------------------------------------------------------------------------
avae            | VAELoader                           | minimax_h3_audio_vae_fp32.safetensors
c0              | MiniMaxH3ReferenceToVideo           | Base Beat 1 text conditioning:
                |                                     |   - width: 768, height: 1344, length: 192
                |                                     |   - clip: ['clip', 0], vae: ['vvae', 0], audio_vae: ['avae', 0]
c2              | MiniMaxH3ReferenceToVideo           | Beat 2: continuation text and RefMod chain (no start photo):
                |                                     |   - width: 768, height: 1344, length: ['c2_gen', 1]
                |                                     |   - clip: ['clip', 0], vae: ['vvae', 0], audio_vae: ['avae', 0]
c2_append       | MiniMaxH3AppendContinuation         | Beat 2: trim the hidden overlap, append new video and audio tokens:
                |                                     |   - previous_av_latent: ['s0_samp', 0]
                |                                     |   - sampled_window: ['c2_samp', 0]
                |                                     |   - overlap_video_tokens: ['c2_gen', 2], overlap_audio_tokens: ['c2_gen', 3]
                |                                     |   - transition_video_tokens: ['c2_gen', 4], transition_audio_tokens: ['c2_gen', 5]
c2_gen          | MiniMaxH3GuidedContinuationWindow   | Beat 2: guided continuation window (22 hidden, +187 new frames):
                |                                     |   - previous_av_latent: ['s0_samp', 0]
                |                                     |   - overlap_frames: 22, extension_frames: 187
c2_guider       | BasicGuider                         | Beat 2: guider on RefMod'd, tail-guided conditioning:
                |                                     |   - conditioning: ['c2_tail', 0], model: ['m_shift', 0]
c2_refapply     | MiniMaxH3RefModApply                | Beat 2: RefMod retention 1.0 on continuation beat:
                |                                     |   - conditioning: ['c2', 0], mods: ['refmods', 0]
c2_samp         | SamplerCustomAdvanced               | Beat 2: sample the window (209 frames):
                |                                     |   - guider: ['c2_guider', 0], latent_image: ['c2_gen', 0]
                |                                     |   - noise: ['noise', 0], sampler: ['ksel', 0], sigmas: ['c2_sched', 0]
c2_sched        | BasicScheduler                      | Beat 2: KEEP 8 steps / simple scheduler:
                |                                     |   - model: ['m_shift', 0], steps: 8, scheduler: simple, denoise: 1.0
c2_tail         | MiniMaxH3LatentTailGuide            | Beat 2: native latent-tail guide (frame 0, no VAE round trip):
                |                                     |   - positive: ['c2_refapply', 0], previous_av_latent: ['s0_samp', 0]
                |                                     |   - target_av_latent: ['c2_gen', 0]
                |                                     |   - overlap_video_tokens: ['c2_gen', 2], overlap_audio_tokens: ['c2_gen', 3]
clip            | CLIPLoader                          | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
dec_a           | VAEDecodeAudio                      | samples: ['s0_sep', 1], vae: ['avae', 0]
dec_v           | VAEDecode                           | samples: ['s0_sep', 0], vae: ['vvae', 0]
ksel            | KSamplerSelect                      | sampler_name: euler
m_attn          | ModelAttentionBackend               | attention: comfy kitchen attention, model: ['unet', 0]
m_shift         | MiniMaxH3SigmaShift                 | shift_audio: 3.0, shift_video: 12.0, model: ['m_vsa', 0]
m_vsa           | BlockSparseAttention                | VSA attention blocks, model: ['m_attn', 0]
mkvid           | CreateVideo                         | fps: 24, images: ['dec_v', 0], audio: ['dec_a', 0]
noise           | RandomNoise                         | noise_seed: 51083601
refapply        | MiniMaxH3RefModApply                | Beat 1: Apply H3 RefMod (retention 1.0 = fully_preserved):
                |                                     |   - conditioning: ['c0', 0], mods: ['refmods', 0]
refmods         | MiniMaxH3RefModsLoader              | Shared RefMods loader (mod_1: minimaxh3_meganfox_v1_refmod)
s0_guide        | BasicGuider                         | Beat 1: guider on RefMod'd conditioning:
                |                                     |   - conditioning: ['refapply', 0], model: ['m_shift', 0]
s0_samp         | SamplerCustomAdvanced               | Beat 1: sample base clip (192 frames):
                |                                     |   - guider: ['s0_guide', 0], latent_image: ['c0', 1]
                |                                     |   - noise: ['noise', 0], sampler: ['ksel', 0], sigmas: ['s0_sched', 0]
s0_sched        | BasicScheduler                      | Beat 1: KEEP 8 steps / simple scheduler:
                |                                     |   - model: ['m_shift', 0], steps: 8, scheduler: simple, denoise: 1.0
s0_sep          | LTXVSeparateAVLatent                | Rewired to final joined latent:
                |                                     |   - av_latent: ['c2_append', 0]
save            | SaveVideo                           | video: ['mkvid', 0], filename_prefix: community/dryrun_2beat/clip
unet            | UNETLoader                          | unet_name: 10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors
vvae            | VAELoader                           | minimax_h3_video_vae_int8_convrot.safetensors
```

---

## 3. Airlock Prompt Cues (Beat 1 vs Beat 2)

### Beat 1 Scene
```
Jennifer sits at the mahogany counter, both hands on a cup.
```

### Beat 2 Continuation Scene (Airlock Lead-In)
```
The shot continues from the last seen moment: the same framing, the same standing pose, the same wardrobe and the same room lighting, and she is still in the same place at the same distance from the camera. At first there is only natural micro-motion - a breath, a slow blink, a small shift of weight - before this action. She keeps her exact voice, accent and signature vocal timbre. The camera does not change angle and the shot never resets to a starting photo. She stands up slowly, resting her right hand on the edge.
```

---

## 4. Verification Checkpoints

1. **`--ambience` option:** Soundscape uses specified ambience (`"quiet room ambience, soft natural room tone"` by default).
2. **`--seconds` refusal:** Asks over 243 frames (~10.125s) without 2+ beats raise `ValueError` prior to creating `run_dir`.
3. **Native continuation chain:**
   - Beat 2 `previous_av_latent` = `['s0_samp', 0]` on `c2_gen`, `c2_tail`, and `c2_append`.
   - RefMod applied every beat via shared `refmods` loader.
   - Start photo / `MiniMaxH3AddGuide` on Beat 1 only.
   - 22-frame overlap, sampled window 209 frames (<= 243).
   - One window per beat.
   - `s0_sep` rewired to `['c2_append', 0]`.
4. **Airlock wording:** Verified in `c2` prompt.
5. **No stitched cells:** One graph (`tag="clip"`), `cell_contract` omitted from `_render_order.json`.
6. **Byte-identical single-shot baseline:** Byte-for-byte SHA256 match on single-shot graphs.
