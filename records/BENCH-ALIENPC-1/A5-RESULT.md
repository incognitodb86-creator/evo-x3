# A5 / BENCH-ALIENPC-1 Step 2 — Flux / Miraclein still tests

Date: 2026-11-19, America/Chicago (CT). Authority: Derrick `t2978u` + `t2976u` (all remaining Flux/Miraclein tests tonight, before REA-Video). X3 was not touched. Nothing was committed or pushed to `mono`. Production candidate templates were not edited. No stills are attached; images stay on AlienPc.

Lease: taken `2026-11-19 21:16:21 CT` (`GrokBot | A5 Flux/Miraclein remaining arms`). Cleared to 0 bytes `21:29 CT`. `gpu-render.lock` absent after the last arm. GPU idle ~433 MiB / 0% after unload.

## Compatibility (live AlienPc, no production-template edits)

`flux_still.py` was missing from live AlienPc earlier tonight and was staged from mono, with these live-host fixes only:

- Windows queues locally (no `--remote`; that flag is the X3 tailnet path).
- `A5_KEEP_COMFY=1` can pass `--keep-comfy-process` so one model family can be timed cold then warm.
- Live `build_request.py` / `resolve.py` still lack `_check_writer_18plus` and `names_from_flux_refmod_or_lora`. `flux_still.py` uses getattr fallbacks; 18+ still runs via `wp_lint` youth/under-18 guards (all prompts PASS).
- `fill_request.comfy_lora_name()` is present and writes `klein9\...` (OPUS-FINDINGS #4). Confirmed on the Hybrid graph (backslash prefix, strength 0.60).
- **Klein9RefModsLoader widget values are stems, not filenames.** The first RefMod submit failed `value_not_in_list` (list length 1457) because `flux_still` sent a `.safetensors` filename. The file is installed under `ComfyUI\models\refmods-klein9\` (1,456 Klein9 RefMods). After switching the per-run graph to the stem form, RefMod and Hybrid passed. LoRA enums already used the `klein9\` prefix correctly.
- H3 `REFMODS_DIR` in live `resolve.py` still points at missing `C:\AI\comfy-alienpc\models\refmods`. These Klein/Miraclein arms did not use that path. Actual H3 RefMods remain under the ComfyUI `models\refmods` tree.

## Prompts and still_read

Backup writer on AlienPc used `flux-klein-prompting` (X3 was busy). Each arm is a 66–80 word positive-only 18+ caption (edit 66 words). `wp_lint` PASS on all seven text files. ST5 reference pictures (`m4_t2i` identity and `m4_refmod` pose/layout ref) were passed through a written still_read + 18+ text lint (card 30) before pose/layout; both PASS. No VLM still_read was loaded on the GPU (would have contended with Flux). Prompt text is not repeated here.

## Result table

Wall time is the runner wall (build + lock + wake if any + sample + harvest). "Sample" is submit-to-DONE from `status.log` / JOB secs when logged. "Cold" means that arm's log includes a `comfyui_auto` wake. "Warm-process" means the Comfy process was kept from a previous arm (`/free` still ran, so weights may reload). Peak VRAM is `nvidia-smi` 1 s samples during the runner, except Arm 1 (logger was not running yet). Sampler: Miraclein arms `euler` / 12 steps / CFG 1.1; Klein arms `lcm` / 4 steps / CFG 1.0 (candidate defaults). Seed `51083601`, canvas `768x1344`, `--no-upscale`. UNET: Miraclein arms `Miraclein_4.5_9b_NVFP4.safetensors`; Klein arms `flux-2-klein-9b-kv-fp8.safetensors`.

| Arm | Result | Template | Steps / CFG / sampler | Cold/warm | Wall (s) | Sample (s) | Peak VRAM | Output PNG |
|---|---|---|---|---|---:|---:|---:|---|
| 1 M4 T2I (earlier tonight) | PASS | `miraclein_t2i.candidate.api.json` | 12 / 1.1 / euler | Cold | 85.9 | 30 | not sampled | `C:\AI\community\runs\m4_t2i_a5_20261119\still\still.png` (1,511,919 B) |
| 2a M4 RefMod | PASS on retry | `miraclein_refmod.candidate.api.json` | 12 / 1.1 / euler; retention `partially_preserved (0.7)` | First try: node_error (filename vs stem), 21:18:40–21:18:47. Retry: warm-process | 62.0 | 55 | 14,733 MiB | `C:\AI\community\runs\m4_refmod_a5_20261119\still\still.png` (1,399,998 B) |
| 2b M4 Hybrid | PASS | same RefMod candidate + Hybrid stack (RefMod 0.85 + Prodigy LoRA 0.60) | 12 / 1.1 / euler | Warm-process | 48.9 | 43 | 14,799 MiB | `C:\AI\community\runs\m4_hybrid_a5_20261119\still\still.png` (1,152,959 B) |
| 3 M4 Edit | PASS on retry | `miraclein_edit.candidate.api.json` | 12 / 1.1 / euler; lighting-only edit of Arm 1 still | First try: rendered 768x1360, queue objective failed (peak 15,700 MiB). Retry: cold wake | 62.4 | 33.1 | 15,526 MiB | `C:\AI\community\runs\m4_edit_a5_20261119\still\still.png` (1,564,614 B) |
| 4 ST4 Klein T2I | PASS | `flux_stills_t2i_klein.candidate.api.json` | 4 / 1.0 / lcm | Cold | 39.7 | 16 | 15,273 MiB | `C:\AI\community\runs\st4_klein_t2i_a5_20261119\still\still.png` (1,678,018 B) |
| 5 ST5 Pose | PASS | `flux_stills_pose_klein.candidate.api.json` | 4 / 1.0 / lcm; `refcontrol_v2_poses` @ 0.9 | Warm-process | 21.9 | 12.1 | 13,420 MiB | `C:\AI\community\runs\st5_pose_a5_20261119\still\still.png` (1,497,275 B) |
| 6 ST5 Layout | PASS | `flux_stills_layout_klein.candidate.api.json` | 4 / 1.0 / lcm | Warm-process, then unload | 17.6 | 6.0 | 15,684 MiB | `C:\AI\community\runs\st5_layout_a5_20261119\still\still.png` (1,521,392 B) |

All final PNGs are 768x1344 RGB. Peak VRAM stayed under the 16 GB target (highest successful sample: 15,684 MiB on layout; first failed edit hit 15,700 MiB).

Clock notes (CT): lease 21:16:21; Arm 2a retry 21:20:59–21:22:01; Hybrid 21:22:16–21:23:05; Edit first fail 21:23:17–21:23:53; Edit retry 21:25:12–21:26:14; ST4 21:26:25–21:27:05; Pose 21:27:54–21:28:16; Layout 21:28:23–21:28:41; lease cleared 21:29.

## Arm-specific findings

**Hybrid / Miraclein NVFP4 + Prodigy LoRA:** The Hybrid graph loaded `Miraclein_4.5_9b_NVFP4.safetensors` and the Klein9 Prodigy LoRA at strength 0.60 with a Windows backslash subfolder name. No NVFP4 loader errors. Queue `rc=0`.

**Edit 768x1360 vs 768x1344:** The candidate graph includes `ImageScaleToTotalPixels` (1.0 MP, step 16) ahead of `GetImageSize`. A 768x1344 source was scaled to 768x1360, and `run_queue` rejected the still (`objective size 768x1360 != 768x1344`). Production template was left unchanged. The retry used a per-run rewire around that scale node so the latent followed the source canvas; then the objective passed.

**ST5 same 1.0 MP scale:** Pose/layout candidates use `ResizeImageMaskNode` (`scale total pixels` 1.0) on both reference images, which would have hit the same objective failure. Per-run graphs were rewired to the unscaled LoadImage outputs (3 links each). Still_read PASS beforehand. Pose includes `DWPreprocessor` + `refcontrol_v2_poses` @ 0.9. Layout does **not** load a RefControl LoRA; it only has an inactive `bfs_head` LoRA at strength 0.0. That is a candidate-template gap vs the skill (RefControl pose/layout), left unedited.

**4-step Klein scouts:** ST4/ST5 used the candidate defaults (4 steps, LCM, CFG 1.0). The `flux-klein-prompting` skill warns that 4-step scouts can cause anatomy errors on seated/multi-person stills. Derrick should eye-check identity, skin, and pose; `KEEP` is his.

## Klein9 realism LoRA availability (read-only, nothing downloaded)

Local `ComfyUI\models\loras` tree: 63 safetensors, 11 Klein-named. Generic realism/skin/anatomy/detail filename matches (2):

- `MS_real_and_Details_klein.safetensors` — 474.07 MiB, loras root (Klein-named realism/detail, already on disk)
- `H3_realism_people_v1.safetensors` — 125.15 MiB, H3 (not Klein9)

Public Flux.2 Klein 9B realism/consistency LoRAs (URLs and sizes only; **not downloaded**, not installed):

- [Mrpopo's Flux.2 Klein 9B photorealistic v1.0](https://civitai.com/models/2647025/mrpopos-flux2-klein-9b-photorealistic) — Civitai, 316.04 MB, 2026-05-24
- [Realism Slider v2.0](https://civitai.com/models/2401004/realism-slider) — Civitai, 19.78 MB, 2026-03-09 (usage tip: strength up to 6)
- [Flux2 Klein 9B Realistic Detail v1.0](https://civitai.com/models/2662689/flux2-klein-9b-realistic-detail) — Civitai, 158.03 MB; also [Hugging Face](https://huggingface.co/SOLRICKS/Flux2-Klein-9B-Realistic-Detail)
- [Candid Film v2.0 (Klein 9B)](https://civitai.com/models/2313101/candid-film) — Civitai, 168.01 MB, 2026-03-09
- [ypsa13/Flux2-Klein-9B-Consistency](https://huggingface.co/ypsa13/Flux2-Klein-9B-Consistency) — Hugging Face (consistency / color-cast; size not listed in the card snapshot)
- [houseofboern/more-detail-flux-klein-9b](https://huggingface.co/houseofboern/more-detail-flux-klein-9b) — Hugging Face, edit-style detail LoRA (needs a control image)

Depth LoRA (card 24) was not downloaded. Candidate templates remain unpromoted (`S2` allowlist still REFUSEs `*.candidate.api.json`). Derrick judges the PNGs by eye.

## Issues for morning review

1. Klein9 RefMod loader wants **stems**, not `.safetensors` filenames — now handled in the AlienPc `flux_still.py` copy; mono still needs the same fix before the next X3-side sync.
2. Edit/pose/layout candidates scale to 1.0 MP and miss the 768x1344 queue objective unless the per-run graph bypasses that node. Fix the candidates on `mono` later (do not silently promote).
3. Layout candidate has no RefControl LoRA (inactive head LoRA only).
4. Live `resolve.py` / `build_request.py` are behind mono (`_check_writer_18plus`, `names_from_flux_refmod_or_lora`, wrong H3 `REFMODS_DIR`).
5. 4-step Klein ST4/ST5 anatomy should be eye-checked before any promotion.
6. No git commit/push was made (X3/mono left for the other executor).
