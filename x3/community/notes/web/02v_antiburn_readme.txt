---
license: other
license_name: minimax-h3-community-license-agreement
license_link: LICENSE
base_model:
- MiniMaxAI/MiniMax-H3
base_model_relation: adapter
pipeline_tag: text-to-video
tags:
- lora
- minimax-h3
- video
- video-continuation
- comfyui
---

# H3 Anti-Burn LoRA (universal, v1)

When you make a long MiniMax H3 video by chaining clips, each new clip continues from the end of the previous one.
It copies that ending's small flaws and adds a few more. After a few clips, faces "burn": skin and lines get crunchy
and etched, and the picture gets harsher. This LoRA is used on the **continuation clips** and keeps them close to the
look of the first clip.

It was trained on three turbos (Larry Turbo v4, HyperFlow, lightx2v 8-step) and tested on a fourth model it never
saw, where it cut face burn from +61% to +4%.

## How to use it

- Load it with `LoraLoaderModelOnly` on the model that makes your **continuation clips**: 2, 3, 4 and so on.
- **Don't use it on clip 1.** A first clip has nothing to burn from. The LoRA was never trained or tested there.
- **Start at 0.5.** If faces still get crunchier from clip to clip, go up; turbos that burn harder need more. If
  faces turn soft or waxy, go down; turbos that burn less need less.
- How strongly it acts also depends on your setup. For example, merging it into an 8-bit checkpoint weakens it. So
  try a few values on a 4-5 clip chain before you settle.

## Examples

Each image shows the same chain run without and with the LoRA. The prompts and seeds are the same, so clip 1 is
identical; the LoRA is never used on it. Each frame is taken 1 second before the end of its video, about 37 seconds
in. We picked scenes where the camera stays on the same shot, so the two clip-10 frames compare fairly.

![An unseen model: clip 1, clip 10 without the LoRA, clip 10 with it](images/unseen_model_park.jpg)
Face burn in this scene: **+51%** without the LoRA, **−4%** with it at 0.6.

![lightx2v 8-step: clip 1, clip 10 without the LoRA, clip 10 with it](images/lightx2v_kitchen.jpg)
Face burn in this scene: **+52%** without the LoRA, **+6%** with it at 0.5.

![Larry Turbo v4: clip 1, clip 10 without the LoRA, clip 10 with it](images/larry_kitchen.jpg)
Larry, the hardest burner we tested. Face burn in this scene: **+189%** without the LoRA, **−15%** with it at 0.6,
loaded at full strength (not merged). With a turbo that burns this hard, the LoRA still helps a lot, but it can soften
the image, and here the colour still drifted warmer and darker. Baked into an 8-bit checkpoint, 0.6 is not enough for
Larry; go higher there.

## What we measured

We ran 10-clip chains, each about 37 seconds long. There were 4 scenes per setting (kitchen, kitchen with a second
seed, park, porch), and every number is the average of those chains. "Face burn" is how much the face's fine texture
changed from clip 1 to clip 10:
- 0 means clip 10 looks as clean as clip 1.
- Positive means it burned.
- Negative means it went softer than clip 1.

| Turbo | No LoRA | 0.4 | 0.5 | 0.6 | 0.8 |
|---|---|---|---|---|---|
| An unseen model (**never trained on**) | +61% | | +29% | **+4%** | −13% |
| HyperFlow 8-step (LoRA) | +25% | +4% | **−1%** | −14% | |
| lightx2v 8-step v1.0 768p | +44% | +14% | **0%** | −7% | −37%¹ |
| Larry Turbo v4 (step 600 EMA) | +261% | +212%² | | +159%² | +57%¹ |

¹ 2 chains. ² 3 chains: the park face got too small to measure.

Larry burns far harder than the others and needs more than 0.8 in this setup. At 1.0 its face burn was gone (−19%,
2 chains), but the camera framing started to change. Loaded at full strength (not merged) instead, 0.6 took it from +261% to −5%
(3 chains).

**What else changes at the best strength.** Saturation, skin redness and lip sync stay where they are without the
LoRA. Fine detail drops a little: 4–14% below clip 1, against 3–18% above it without the LoRA. Too much strength
shows up as soft, waxy faces.

**The setup we tested.**
- Checkpoints: ComfyUI's int8 ConvRot pruned MiniMax H3 checkpoints ([Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)).
  Clip 1 used `fl2va`; continuations used `ref2va`.
- LoRA: merged with `LoraLoaderModelOnly` before the turbo.
- Continuations: each one carried the previous clip's last 39 frames and their audio as a protected masked context.
- Sampling: 8 steps, `cfg` 1.
- Resolution: 640×1152, 1152×640 and 864×864.

With other checkpoints (bf16, fp8, GGUF), other step counts or other ways of continuing, expect a different best
strength.

## Limitations

- It is experimental. Four scenes per setting is a small test, and one 10-clip chain can swing ±15 points on its own.
- It prevents burn. It does not repair a video that is already burned.
- It was only tested on continuations from masked context, not on extending a video any other way.
- It was trained and tested on speaking people, with faces at medium to close distance.

## How it was trained

It uses trajectory self-distillation:
1. We recorded what each turbo actually does in a fresh generation: every model call of real 8-step runs. That gave
   150 full-size runs, 50 each from Larry, HyperFlow and lightx2v.
2. The LoRA was trained in continuation mode: the start of the same video is pinned as the protected context
   (sometimes slightly noised), and the target is the turbo's own fresh run. So a continuation learns to look like a
   fresh generation instead of copying and amplifying the flaws in its context.
3. There was no synthetic burn and no fresh-noise loss. Earlier versions that used them softened everything.

Run settings:
- 300 steps, rank 32, learning rate 1e-4, network weight 0.6.
- Resolution 864, 124 frames.
- One RTX PRO 6000 (96 GB).

The training code, configs, recorder node, scoring script and a write-up of everything that didn't work are in
[TryingSomeStuff13/ai-toolkit](https://github.com/TryingSomeStuff13/ai-toolkit/tree/h3-antiburn/extensions_built_in/diffusion_models/minimax_h3/antiburn),
branch `h3-antiburn`.

## File

| | |
|---|---|
| File | `h3_antiburn_universal_v1.safetensors` |
| Size | 310,168,728 bytes |
| SHA256 | `8f76dc3c63afa8c556c620b4b7f2ffeeb666f0aa9382a9ce3a07fd6120d0f154` |
| Type | LoRA, rank 32, bf16, 416 tensors, ComfyUI key format (`diffusion_model.*`) |
| Trained layers | attention and MLP of the 50 DiT blocks and the 2 token-refiner blocks; no adaLN |

## License

This LoRA is a Model Derivative of MiniMax H3 and is distributed under the MiniMax H3 Community License Agreement
(see `LICENSE` and `NOTICE`), including its Acceptable Use Policy. The file holds only new adapter weights; no MiniMax
H3 weights are included.

Thanks to a community compute grant that paid for the GPU time.
