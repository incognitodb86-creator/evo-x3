# Upscale: why Remacri, what else, NVIDIA? — 2026-10-02

**Stamp:** 2026-10-02 20:31 CT  
**Owner:** CoS research only. Dial owns Max scoreboard and KEEP 1080 CUDA/Remacri. No AlienPc Shell. No KEEP change. No invented timings.

**Question:** Why is the 1080 path Remacri, what open models exist instead, and does NVIDIA already upscale this?

**Stack this applies to:** already-rendered local I2V, about **864×480** (aspect 1.8, not 16:9), then a ~1080-wide export (local target **1920×1066**). AlienPc is **RTX 5070 Ti 16 GB**.

---

## Why Remacri (local)

**Not a quality crown.** Local files pick it as the mid CUDA export arm that was already on disk, not as a scored win over NVIDIA or Topaz.

| Source | What it actually says |
|--------|------------------------|
| `/workspace/cos/research/2026-10-02-reddit-h3-upscale-cmp-review.md` | KEEP row: “Remacri CRT as mid AI arm — Fits ‘better than enlarge, lighter than SeedVR2’ niche.” Explicit non-change: “Do **not** drop Remacri just because Reddit didn’t A/B it.” Same note: RTX Super/VSR was **underweighted** and should be an extra arm, not a silent swap. |
| `/workspace/cos/status/ce-plan-alienpc-home-upscale-clear-2026-10-02.md` | Plan step: “AI 1080: Remacri CRT on :8189 KEEP argv → `clips/ai/`.” Optional SeedVR only if Remacri loses. |
| `/workspace/cos/research/2026-10-02-remacri-settings-check.md` | Graph note from the desktop AI note (not re-run here): CRT node missing (`soundfile`), so the job used `4x_foolhardy_Remacri.pth` via `ImageUpscaleWithModelBatched` fp16, `per_batch=1`, `downscale_ratio=0.56` Lanczos, **then** a second Lanczos to 1920×1066, then **NVENC** H.264. One clip: 124f, ~5.17s, wall **76.1s**. Settings check calls the **model** RIGHT (skin/detail, less mush) and the **double Lanczos** WRONG. Hands/contact stay a generate problem. |
| `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/FAIR_LF_D12_pack/FAIR_LF_D12_SCOREBOARD.md` | Different job (still, UltimateSDUpscale, denoise 0.15, 1.5×). **QUALITY FAIL.** “sharpens HF … but does not improve Cond-face hold.” Not the 1080 video KEEP. |

**NOT FOUND locally:** a head-to-head that crowned Remacri over NVIDIA VSR, Maxine, or Topaz on a Max clip. “CUDA” in KEEP 1080 CUDA/Remacri means the Comfy upscale runs on the GPU and the file is encoded with NVENC. It does **not** mean NVIDIA’s Video Super Resolution model.

Author reason used by the settings check, from OpenModelDB (FoolhardyVEVO, 2021-04-09): interpolated ESRGAN so “skin and other details don’t become mushy and blurry.” https://openmodeldb.info/models/4x-Remacri

---

## 1) What Remacri is

- **File:** `4x_foolhardy_Remacri.pth`. Architecture **ESRGAN**, scale **4× only**, size 64nf / 23nb, RGB. Date on OpenModelDB: **2021-04-09**. License **CC-BY-NC-SA-4.0** (private use; **no commercial-use grant** on that page). https://openmodeldb.info/models/4x-Remacri
- **How it was built:** interpolation of photo/“IRL” ESRGAN models (Siax, Superscale, Pixel Perfect, and others), not an anime-only train. Same page.
- **Where it runs:** any loader that accepts an ESRGAN `.pth` (Comfy `UpscaleModelLoader` / KJ batched upscale, chaiNNer-style graphs). It is a **per-frame still model**. Local KJ note in the settings check: frame upscalers are **not temporal** and do not repair motion.
- **Live-action vs anime:** aimed at textured photos (skin, fabric, foliage). Tradeoff called out by a host writeup: it can **add grain on flat areas**. https://chunks.md/4x-remacri-online (page has no publication date). Anime-specific nets (Real-ESRGAN anime 6B, AnimeSharp) are the wrong default for this I2V. A third-party Chinese review prefers Remacri over anime6B when the picture is high-texture rather than flat cel shade; that is opinion, not our score. https://visionpaletteai.com/news/ai-upscaler-comparison-foolhardy-remacri-review
- **Our geometry:** 4× of 864×480 is 3456×1920, then one Lanczos down to 1920×1066. Effective scale vs source is about **2.22×**, not 4×. There is no 2× Remacri weights file on the OpenModelDB page.

---

## 2) Other open models (one line each)

No AlienPc benchmark in this note. Fit is from each model’s own page.

| Model | Fit |
|-------|-----|
| **Real-ESRGAN x4plus** | General 4× photo restoration, synthetic degradation, BSD-3-Clause (commercial use allowed). Often smoother / more “plastic” than Remacri in community writeups; our settings check cites that as why Remacri was kept. https://openmodeldb.info/models/4x-realesrgan-x4plus (2021-07-22) |
| **Real-ESRGAN x4plus anime 6B** | Same family, **6** blocks, **anime**. Wrong default for live-action skin. BSD-3-Clause. https://openmodeldb.info/models/4x-realesrgan-x4plus-anime-6b (2021-12-12) |
| **4x-UltraSharp** | Kim2091 4× ESRGAN; lots of invented texture; trained mostly on JPEG. Sharper, easier to overcook skin. CC-BY-NC-SA-4.0. https://openmodeldb.info/models/4x-UltraSharp (2021-10-27) |
| **4x-Nomos8kSC** | Helaman 4× photo ESRGAN with on-the-fly JPEG + blur, “realistic sr.” CC-BY-4.0 (commercial use allowed). Cleaner-photo alternative, not an anime net. https://openmodeldb.info/models/4x-Nomos8kSC (2023-05-10) |
| **4x-AnimeSharp** | Kim2091 interpolation of UltraSharp and TextSharp; “works amazingly on anime,” text second. Not this stack. CC-BY-NC-SA-4.0. https://openmodeldb.info/models/4x-AnimeSharp (2021-12-28) |
| **4x SwinIR-M pretrain** | Transformer (SwinIR Medium), not ESRGAN. Kim2091 calls it a simple ethical pretrain on textures. Heavier image arch; community picker treats SwinIR as a **slow, image-first** class, not the lightweight video default. CC0. https://openmodeldb.info/models/4x-SwinIR-M-Pretrain (2024-05-15) · architecture class: https://github.com/Sirosky/Upscale-Hub/wiki/%F0%9F%A4%B7-How-to-Pick-a-Model |

**x2 Real-ESRGAN:** not opened on OpenModelDB in this pass. Do not treat a 2× filename as verified here. Remacri itself has no 2× weights.

**Also already in the local plan, not swapped in here:** Lanczos/CUDA scale as the enlarge **control**; SeedVR2 **3B** as the heavy quality arm (7B called a bad idea on 16 GB). LTX-as-upscaler is a local **do-not** for faces. Those are prior stamps, not new measurements.

---

## 3) NVIDIA — what actually upscales

Three different things get called “NVIDIA upscale.” Only some can write a new mp4.

### Playback: RTX Video Super Resolution (consumer driver)

- NVIDIA FAQ: real-time AI on **Tensor cores** for video **played** in Chrome, Edge, Firefox, or VLC. Input it will enhance: about **360p–1440p**. It turns on only when the picture is being scaled up to the display. It does **not** use DLSS. https://nvidia.custhelp.com/app/answers/detail/a_id/5448
- **Playback does not save a file.** The boost ends when playback ends. A 2026 VLC how-to states that split explicitly. https://unifab.ai/resource/vlc-upscale
- Same FAQ: NVIDIA also ships an **RTX Video SDK**. Apps that integrated it (examples named: **DaVinci Resolve**, **Wondershare Filmora**) can run the effect inside the editor, including offline. That is an app export, **not** a Comfy node and not the KEEP graph.
- Developer page (now under “NVIDIA AI for Media”): the RTX Video model is described as usable for **offline processing in creative apps** or real-time playback. https://developer.nvidia.com/rtx-video-sdk
- Local plan already asked for an RTX arm **or** an explicit N/A if there is no driver/Comfy path (`2026-10-02-reddit-h3-upscale-cmp-review.md`). Headless Comfy does not get VSR for free.

### Games only: DLSS

- FAQ, same page: DLSS Super Resolution / Frame Generation needs **game-engine** data (motion vectors, depth, optical flow). “It doesn’t work on streamed video.” Useless on an already-rendered mp4.

### Encode only: NVENC

- Hardware H.264/HEVC encoder. The Remacri job already uses it (`VHS nvenc_h264-mp4`). It does not invent pixels. Do not “switch to NVIDIA” by changing the encoder.

### Offline SDK: Maxine / Video Effects Super Resolution

- **Not** the NVIDIA App toggle. Developer **Video Effects SDK** filter “Super Resolution”: upscales, sharpens, keeps content. Mode 0 = more artifact removal (lossy). Mode 1 = more enhancement (cleaner sources). Scales **4/3, 1.5×, 2×, 3×, 4×**. **4× input cap is 540p** (so 480-tall can 4×; 3× input cap is 720p). Sample app takes `--in_file` / `--out_file`. https://docs.nvidia.com/maxine/vfx/latest/Filters/SuperResolution.html · https://github.com/NVIDIA-Maxine/Maxine-VFX-SDK
- A separate lighter **Upscale** filter exists in the same SDK (fast sharpen, not the SuperRes model). System guide: https://docs.nvidia.com/deeplearning/maxine/vfx-sdk-system-guide/
- This is a license-gated SDK (AI Enterprise / eval), not something already in the KEEP argv. A newer broadcast “Video Super Resolution” NIM (480p→8K, sharpness/hallucination controls) is a **different** pro product on the AI-for-Media page. Do not conflate it with the free driver toggle.
- **NVIDIA Broadcast** is the consumer webcam-effects app (background, noise). It is not the offline mp4 exporter. The upscale filter lives in the VFX SDK above.

**5070 Ti:** consumer RTX Video FAQ/reviews list RTX 20/30/40/50 as the tensor-core family. This note does **not** measure 50-series VSR quality or a Maxine build on this GPU.

---

## 4) Topaz — his license vs the 1.7 app

**Fleet fact (not re-verified against his account in this pass):** perpetual **Video Enhance AI**, order TS-10728392, May 2022, login **derek.boone86@gmail.com**. Unlocks legacy **Video AI**, final build **v7.1.5**. Does **not** unlock subscription **Topaz Video 1.7**.

Official split: https://docs.topazlabs.com/topaz-video/tvai-vs-tv (fetched 2026-10-02)

- Video AI: discontinued, **v7.1.5 is final**, no new models. Installer from Account → Legacy. “Expired” means no updates, not “license dead.”
- Topaz Video: subscription. “Includes **all models from Video AI plus** newer models such as Hyperion 2, Starlight Precise 2.5, Starlight HQ, Starlight Fast 2, Gaia 2, Starlight Sharp, Denoise, Nyx XL, Proteus Natural.”
- Legacy app “discontinued in September 2025” and “will not be optimized or updated for newer OS updates or new systems.” A 5070 Ti smoke can fail even with a valid login. Not tested here.
- Account → Legacy is what confirms **which version he actually owns**. A May 2022 purchase is not proof that every model later added to 7.1.5 was in the original entitlement.

**Progressive models named on the Video AI enhancement doc** (this is the legacy app’s model guide, not the 1.7-only list): Proteus, Iris, Nyx, Rhea, Artemis, Gaia, Theia, plus Dione for interlaced, plus Starlight (original cloud; Mini called out as the first local diffusion model). https://docs.topazlabs.com/video-ai/filters/enhancement

| Model | Role on that page | In his perpetual license? |
|-------|-------------------|---------------------------|
| **Proteus** | General; noise; low-to-medium footage; manual sliders. Progressive or interlaced. | **Named on the Video AI guide.** Still confirm the installed build. |
| **Artemis** | Balance of detail / noise / artifacts. Variants HQ, MQ, LQ, halo, alias. | **Named on the Video AI guide.** |
| **Gaia HQ / Gaia CG** | HQ polish and **CG/animation line work**. Not the live-action default. | **Named on the Video AI guide.** Gaia **2** is listed as a **newer subscription** model. Do not assume Gaia 2. |
| **Nyx** | Denoise for high-res, poor light. 1× keeps res; 2× also scales. Not a general 4× upscaler. | **Named on the Video AI guide.** **Nyx XL** is a subscription extra. |
| **Iris** | Noise/compression plus **face** recovery. “Improve Detail” goes extreme fast. | **Named on the Video AI guide.** |
| **Rhea / Theia** | Rhea = fine detail, **4×**. Theia = extra sharpen, two tune modes. | **Named on the Video AI guide.** Not claimed as the May 2022 day-one set. |
| **Starlight Precise, Proteus Natural, Gaia 2, Nyx XL** | Current-app models. | **Subscription extras** on the TV-vs-TVAI page. **Not in the perpetual line unless a source says otherwise. None does.** |

Prior local recipe `/workspace/cos/research/2026-10-02-topaz-video-ai-settings.md` is a **Topaz Video 1.7.0 / Precise 2.6** note. It says itself it is **not** a 7.x recipe. Do not run Precise on the perpetual install. That note also says Precise wants ~16 GB and not to run Remacri on the GPU at the same time.

---

## 5) Practical call for this stack (no KEEP change)

| Path | What it does to an 864×480 mp4 | Fit |
|------|--------------------------------|-----|
| **Remacri (current KEEP)** | Writes a file. 4× ESRGAN on CUDA, then Lanczos to 1920×1066, NVENC. Per-frame. ~76s / 124f on one noted clip. Does not fix anatomy. Double Lanczos on that run was a settings bug. NC license. | Stay the export until Dial scores a replacement. |
| **NVIDIA driver VSR** | Playback only (VLC/browser) unless Resolve/Filmora/SDK is used to export. | Good **look** check. Not a Comfy pass. Not a KEEP swap. |
| **NVIDIA Maxine SuperRes** | Can write a file (SDK sample). 2× of 480p is in range. Extra install and license. | Later arm, not tonight’s smoke. |
| **DLSS / NVENC** | DLSS cannot ingest the mp4. NVENC only encodes. | Ignore as “the NVIDIA upscaler.” |
| **Topaz legacy (Proteus or Artemis)** | Writes a file **if** 7.x runs on the 5070 Ti. Temporal video model, custom output size, so it can hit 1920×1066 without a fake 16:9. Precise/Natural/Nyx XL are the wrong app. | The one comparison worth a smoke. May fail on new GPU. |

**Recommended next smoke (Dial, not CoS, not a KEEP edit):**

One already-rendered **864×480** KEEP clip, three looks, no second generate:

1. Existing Remacri mp4 (optionally re-export **once** with a **single** Lanczos to 1920×1066 — settings check only; same weights).
2. **Topaz Video AI** from Account → Legacy, login **derek.boone86@gmail.com**. Progressive, **Proteus** (Estimate / Auto, Improve Detail low). Custom size **1920×1066** (not 1920×1080 — that stretches 864×480). H.264. If the app will not start or will not see the 5070 Ti, stop and record that. Do not install Topaz Video 1.7 to “fix” it.
3. Same source file in **VLC** with NVIDIA App → RTX Video Super Resolution on, output module Direct3D11, upscaling mode Super Resolution. Eyes only. No file unless DaVinci is already installed.

Do not run Remacri and Topaz on the GPU together. Do not change KEEP argv unless Dial’s scoreboard says so.

---

## Sources

- Local: `2026-10-02-remacri-settings-check.md`, `2026-10-02-reddit-h3-upscale-cmp-review.md`, `ce-plan-alienpc-home-upscale-clear-2026-10-02.md`, `2026-10-02-topaz-video-ai-settings.md`, `FAIR_LF_D12_SCOREBOARD.md`
- https://openmodeldb.info/models/4x-Remacri
- https://chunks.md/4x-remacri-online
- https://openmodeldb.info/models/4x-realesrgan-x4plus
- https://openmodeldb.info/models/4x-realesrgan-x4plus-anime-6b
- https://openmodeldb.info/models/4x-UltraSharp
- https://openmodeldb.info/models/4x-Nomos8kSC
- https://openmodeldb.info/models/4x-AnimeSharp
- https://openmodeldb.info/models/4x-SwinIR-M-Pretrain
- https://github.com/Sirosky/Upscale-Hub/wiki/%F0%9F%A4%B7-How-to-Pick-a-Model
- https://nvidia.custhelp.com/app/answers/detail/a_id/5448
- https://developer.nvidia.com/rtx-video-sdk
- https://docs.nvidia.com/maxine/vfx/latest/Filters/SuperResolution.html
- https://github.com/NVIDIA-Maxine/Maxine-VFX-SDK
- https://docs.nvidia.com/deeplearning/maxine/vfx-sdk-system-guide/
- https://docs.topazlabs.com/topaz-video/tvai-vs-tv
- https://docs.topazlabs.com/video-ai/filters/enhancement
- https://unifab.ai/resource/vlc-upscale
