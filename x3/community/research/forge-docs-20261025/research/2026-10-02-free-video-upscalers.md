# Free local upscalers vs Remacri — Max I2V on 16GB

**When:** 2026-10-02 ~21:47 CDT  
**Ask:** Better free Comfy upscaler, or a LoRA, than `4x_foolhardy_Remacri` for finished live-action clips (864×480, 124 frames, RTX 5070 Ti 16GB).  
**Did not install anything. Did not touch AlienPc.**

## Call

**Stay on Remacri.** Nothing free and local is clearly better for these clips.

Remacri only enlarges. It looks plastic and it cannot fix hands, contact, or a camera push. Every option that might look less plastic either redraws the picture (bad for contact) or is the same per-frame ESRGAN family (not a real step up). There is no video-upscale LoRA for Max.

Do not generate at 1080 inside the sample. Do not use the LTX 2× spatial upscaler on Max pixels. Do not use Ultimate SD Upscale.

## What is already on the box

From the 2026-10-02 catalog note (`PLAN_AI_1080_UPSCALE.md`):

| Thing | Kind | Use on Max |
|---|---|---|
| `4x_foolhardy_Remacri.pth` | ESRGAN **model** | Current post pass. Enlarge only. |
| `ltx-2-spatial-upscaler-x2-1.0.safetensors` | LTX latent **model** | Wrong family. Skip. |
| `UpscaleModelLoader` / `ImageUpscaleWithModel` / `CRT_UpscaleModelAdv` | **nodes** | How Remacri runs. |
| `ComfyUI_UltimateSDUpscale` | **node** | Tiles frames back through an SD checkpoint. Redraws faces and contact. |
| `RTXVideoSuperResolution` | **node** (small NVIDIA model) | Present in that catalog. Not proven better than Remacri. |
| SeedVR / SeedVR2 upscale | **not installed** | No upscale node, no weights. |

## Ranking

1. **Remacri (keep).** Per-frame 4× ESRGAN. Same node can target ~1080 instead of full 4× (3456×1920). Fits 16GB if Max is unloaded and frames are batched/tiled. Does not redraw anatomy. Plastic skin is the known cost. https://openmodeldb.info/models/4x-Remacri
2. **RTX Video Super Resolution.** Only other enlarge-class option that is temporal and already a node. Not clearly better. See below.
3. **SeedVR2 3B FP8.** Best *detail* rumor, and a free weight does fit this card in small batches. It is a diffusion restorer, slow, and not installed. Not the next smoke.
4. **Nomos8kSC / Real-ESRGAN x4plus.** Photo ESRGAN swaps. Same job as Remacri, maybe slightly less anime-crunch. Not worth a smoke.
5. **4x-UltraSharp.** Sharper ESRGAN. More of the plastic problem, not less.
6. **FlashVSR.** Fast diffusion video SR. Redraws. Official sparse path is unproven on RTX 50. Skip.
7. **No LoRA.** Nothing to load.

## SeedVR2 (model + nodes, not a LoRA)

Still the community quality pick on MiniMax H3 **T2V** demos, and still the slow one. That earlier note holds. Current status (Oct 2026):

- Free. Apache 2.0. Official Comfy docs and the NumZ node both ship 3B and 7B in FP16, FP8, INT8, and GGUF. https://docs.comfy.org/tutorials/utility/seedvr2 https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler
- **Installed 2026-10-06 ~10:58 CT** on TR `:8189` disk: NumZ `custom_nodes/seedvr2_videoupscaler` (HEAD 4490bd1) + `models/SEEDVR2/seedvr2_ema_3b_fp8_e4m3fn.safetensors` + `ema_vae_fp16.safetensors`. **Comfy restart still required** to load NumZ nodes (R3c was live; no restart). See `/workspace/cos/gbrain/04_memory/max-studio-2026-10-06/SEEDVR2_INSTALL_2026-10-06.md`.
- **16GB fit:** NumZ’s current README puts 12–16GB on **FP8**, with BlockSwap or VAE tiling if it OOMs. 8GB and under wants GGUF Q4/Q8 plus BlockSwap. 7B FP16 is a 24GB job. An older NumZ note that “even 3B needs 18GB” is outdated; v2.5 is the one that claims 16GB.
- **124 frames:** do not run as one batch. Temporal consistency wants batch size `4n+1` (5, 9, 13…). On 16GB the safe start is **3B FP8, batch 5, short side 1080, color correction `lab`**, Max unloaded. 124 frames is about 25 batches. A 4090 timing in an old NumZ table was ~0.2–0.3 fps at 1080-class output. Expect minutes, not Remacri’s short pass. Not measured on this 5070 Ti.
- **Redraw:** yes, it can. It is a one-step diffusion restorer. Comfy’s docs call it “conservative” and say it keeps structure. Reddit H3 viewers said it is the sharpest and **sometimes too sharp**. NumZ also had a 7B plastic/specular bug (fixed in their 2.5.6 notes). It will not repair a bad hand or a camera push, and it can invent texture on skin and contact. That is the wrong failure for these clips.
- H3 thread (T2V, 5090, not our I2V): SeedVR2 = quality, RTX = speed, LTX upscale = worse than native. https://www.reddit.com/r/StableDiffusion/comments/1vfmjla/ and the local review `2026-10-02-reddit-h3-upscale-cmp-review.md`.

## RTX Video Super Resolution (node, not a LoRA)

- Free Comfy node, RTX only. Apache-2.0 repo. https://github.com/Comfy-Org/Nvidia_RTX_Nodes_ComfyUI
- NVIDIA (2026-03-17): small model, scale factor 1–4, quality 4 = “maximum edge sharpening and artifact removal.” Their guide’s 16GB / 5070 Ti line is for the **whole** LTX gen workflow, not a measured VRAM number for VSR alone. https://www.nvidia.com/en-au/geforce/news/rtx-ai-video-generation-guide/
- A third-party walkthrough: 20s of 720×1280 at 2× finished in 17s on a 5090, and **it does not add new detail**. https://www.nextdiffusion.ai/tutorials/video-upscaling-nvidia-rtx-video-super-resolution-comfyui
- On this card a 5s 864×480 clip at 2× (1728×960) or 4× should be easy **after Max is unloaded**. No published 124-frame VRAM figure. The catalog already lists the node.
- Enlarge, not a redraw of anatomy. Temporal, so less flicker than per-frame Remacri. It still only sharpens what is there. Nobody has A/B’d it against Remacri on these contact clips, so it is not “clearly better.”

## ESRGAN family (models, same nodes Remacri already uses)

All of these are per-frame. They fit 16GB the same way Remacri does (batch 1–4, tile if needed). They do not see motion. They do not fix hands or camera push.

| Model | Kind | vs Remacri | License |
|---|---|---|---|
| `4x_foolhardy_Remacri` | interpolated photo ESRGAN | Current. Softer than UltraSharp, still plastic on skin. | CC-BY-NC-SA-4.0. https://openmodeldb.info/models/4x-Remacri |
| `4x-UltraSharp` | detail-heavy ESRGAN | More invented texture. Worse for skin. | CC-BY-NC-SA-4.0. https://openmodeldb.info/models/4x-UltraSharp |
| `4xNomos8kSC` | photo ESRGAN, trained on realistic stills, jpg/blur | Closest “less plastic still” swap. Pretrained from Real-ESRGAN x4plus. Still per-frame. | CC-BY-4.0. https://huggingface.co/Phips/4xNomos8kSC |
| `RealESRGAN_x4plus` | general photo ESRGAN | Older, softer. Nomos was trained on top of it. | BSD-3-Clause. https://openmodeldb.info/models/4x-realesrgan-x4plus |

`4x-Anime` / `RealESRGAN_x4plus_anime_6B` are the wrong training set for live action.

## FlashVSR (diffusion model + custom node)

- One-step **diffusion** streaming VSR. Public weights (v1.1 recommended). https://github.com/OpenImagingLab/FlashVSR https://huggingface.co/JunhaoZhuang/FlashVSR-v1.1
- Authors want **4×**. Their speed number is ~17 fps for 768×1408 on an **A100**, not a 5070 Ti.
- Official Block-Sparse Attention is tested on A100/A800/H200. **RTX 40/50 compatibility is unknown.** They also warn that many Comfy ports drop that attention and look worse.
- Third-party Comfy guide (not a measurement here): 16GB = Tiny + tiled VAE, not Full at 4×. https://www.nextdiffusion.ai/tutorials/flashvsr-stable-video-upscaling-comfyui
- Redraws. Can change texture. Skip for faithful contact clips. The 1038lab Comfy wrapper is GPL-3.0. https://github.com/1038lab/ComfyUI-FlashVSR

## LoRA? No.

- **No LoRA upscales a finished Max clip.** A LoRA only changes the sampler. It cannot sharpen 864×480 frames after the fact.
- `larryvrh/MiniMax-H3-Turbo-Lora` is a **4-step speed** LoRA, not an upscaler. https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora
- The “MiniMax H3 latent upscaler” is a **latent model**, not a LoRA. It doubles a clean H3 latent **inside the generate job**, then a second sample repaints detail. That is “upscale during the smoke,” and the second pass can change motion and anatomy. Authors say a direct decode can even look softer, and to use a pixel upscaler on a finished video. https://github.com/mamad8c/ComfyUI-H3-Latent-Upscaler-Mamad8 https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler
- LTX Recipe B’s `ltx-2-spatial-upscaler-x2` is LTX-only. Leave it off Max.

## Not the next smoke

Stay on Remacri for export. If a single later experiment is wanted, the only cheap one is **RTX VSR, 2×, quality 4, one finished clip, Max unloaded**. Judge skin and contact against the Remacri of that same clip. If it is softer or the same, stop. Do not install SeedVR2 or FlashVSR for that test.
