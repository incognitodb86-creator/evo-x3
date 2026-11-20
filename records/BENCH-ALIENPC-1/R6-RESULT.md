# R6 ComfyUI speed test (AlienPc) — 2026-11-19

All times are America/Chicago (CT). This file is a report only; it was not committed from this pass.

Derrick's go: card t2912s10214. Plan row R6: try `--fast fp16_accumulation`, then `cublas_ops`, one at a time. Never `fp8_matrix_mult` or `autotune`. Success is a blind same-seed comparison that ties or beats the baseline. Rollback is dropping the flag.

## A7 (prerequisite)

A7 in `C:\AI\community\runs\a7_tq_ab_20261119\` finished before this work started.

- Last job `tq4_long_continuation_b7` started 17:29:33 CT, OBJECTIVE ok 17:41:25 CT (481 frames, 768x1344, audio yes, 14,808,873 raw bytes).
- `comfyui_auto` unloaded 17:41:28 CT; GPU lock released and BATCH closed 17:42:15 CT, `done=6/6`, rc=0.
- ComfyUI `:10003` was already down (unable to connect).
- All 6 clips exist as non-zero mp4s (raw + 2x): TQ1 guide 2-pass, ref 1-pass, ref 2-pass; TQ4 two-person, 16:9 Ref2VA, long continuation.
- Removed only the lease line `Max | A7 TQ A/B | 2026-11-19 17:09:10 CT`.

## Dropped LoRAs archived

Lease taken: `Max | archive dropped LoRAs + R6 speed test | 2026-11-19 17:44:05 CT`.

Derrick t2885u dropped both. Templates under `C:\AI\community\templates`, scripts, docs, and director config had no filename references. Render defaults do not load either LoRA. (A skill doc mentions the realism trigger word only; nothing pointed at the files.)

Both files were in the live `comfyui_auto` models tree (`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\loras`). The original ComfyUI folder was not touched. SHA-256 was taken before the move, files were moved to `C:\AI\_archive\20261119\loras-dropped\`, and the hashes were re-checked there. Sources are gone from the live loras folder (81 files remain, down from 83).

| Label | Size (bytes) | SHA-256 (pre = post) |
|---|---:|---|
| the bulge LoRA | 296,485,336 | `9340B705EC9EF9CF2FEF62B1FA636821314E41BAF8489A698AEF7F5932B03B14` |
| the realism LoRA | 131,229,656 | `ACC529601D2DA117FB81179E76C56E488A3BEAB1171659D305F04FA3655B787E` |

## Environment (read live)

- Host: AlienPc, NVIDIA GeForce RTX 5070 Ti.
- Live ComfyUI (`comfyui_auto`): `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI`, version **0.46.0** (newer than the 0.38.0 snapshot in the remediation pack).
- Python 3.12.10, PyTorch `2.15.0.dev20260928+cu130`, CUDA 13.0.
- Official and local flag syntax (this version's `comfy/cli_args.py` and [ComfyUI startup flags](https://docs.comfy.org/development/comfyui-server/startup-flags)): `--fast fp16_accumulation` enables only that feature. Bare `--fast` enables every option, including the banned `fp8_matrix_mult` and `autotune`. That was not used.
- `fp16_accumulation`: on NVIDIA this version sets `torch.backends.cuda.matmul.allow_fp16_accumulation = True` (`comfy/model_management.py`). The attribute exists on this torch (current value was False before the test). Official docs list torch >= 2.7; 2.15 satisfies that.
- `cublas_ops`: this version imports the `cublas_ops` package and otherwise leaves `CUBLAS_IS_AVAILABLE = False`. `pip show` found no `cublas_ops` / `cublas-ops` in the ComfyUI venv. **The package was not installed.** That arm was skipped.
- Production argv (from `C:\AI\director\config\llama-swap.yaml`, `comfyui_auto` cmd only): `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5`. Backed up to `C:\AI\_archive\20261119\llama-swap.yaml.before-r6` (SHA-256 `ED16B3923421FC376F24C5ECCAEDAEC5469F6C68C800D0B5AAEAB606DBC6524E`).

## Method

Run dir: `C:\AI\community\runs\r6_speed_20261119\`.

Copied the saved `request.api.json` from `C:\AI\community\runs\h3max_lora_test_20261119\arm0_baseline` (SHA-256 `4359FFFB2C8EE252458CCF8CAC10C73F0858D4896439EADD16D7C6E5F3A6E5BC`) into each arm folder with no prompt edits. Same approved still, prompt (`prompt_sha256` `6adb8150…` matches arm0), seed **51083601**, 1-pass `oc_guide`. Queued with `C:\AI\community\scripts\run_queue.py` (RTX 2x ULTRA post-pass on, as in A7 / arm0).

Wall seconds are from the `JOB end` lines. Frame count and size are from the graph / OBJECTIVE / ffprobe (243 frames, 768x1344 raw). `run_queue` logged `cli frames=124 vs graph frames=243`; the graph is the authority and the outputs are 243 frames.

YAML was edited only while ComfyUI was idle and no render was queued. llama-swap is already running with `-watch-config`. Reload was confirmed in `C:\AI\director\logs\llama-swap.out.log` (`configuration reloaded` at 17:56:53 CT for the flag, 18:04:31 CT for the restore). The live `comfyui_auto` process argv for the fp16 arm was checked and included `--fast fp16_accumulation`. Unload/reload used llama-swap's normal path (`run_queue` GET `/comfyui/` wake and `POST /api/models/unload/comfyui_auto`). llama-swap, strata, the hub, and pi were not killed.

One clip per arm. The two wall times differed by 0.2 s, so a second clip was not needed. `cublas_ops` was not run.

## Results

| Arm | Flag | JOB end (s) | Upscale (s) | Raw frames / size / audio | Raw bytes | Errors | SSIM All vs baseline re-render (mean / min / max) | PSNR avg vs baseline (mean / min / max dB) |
|---|---|---:|---:|---|---:|---|---|---|
| r6_baseline | none (production argv) | **286.5** | 8.1 | 243, 768x1344, yes | 7,312,231 | none | (reference) | (reference) |
| r6_fp16_acc | `--fast fp16_accumulation` | **286.3** | 7.8 | 243, 768x1344, yes | 7,330,643 | none | **0.782641 / 0.738986 / 0.985052** (243 frames) | **21.708 / 19.710 / 42.480** |
| r6_cublas_ops | skipped | — | — | — | — | `cublas_ops` package not installed; not pip-installed | — | — |

Notes:

- Historical same-graph arm0 from earlier today was 304.7 s JOB + 18.7 s upscale, also a fresh Comfy start. Today's baseline re-render is the apples-to-apples control. The 18 s gap vs arm0 is ordinary run-to-run variation and is much larger than the 0.2 s gap between today's two arms.
- Raw SHA-256: baseline `7F48A36DAC6B7DD050B4649E6432C547CC49EC9F62118A3EE28687C7D6857552`; fp16 `0EF2DD767CC64976101FDEDB182EC84859DBEAD1ACDBFBDF7B2B294378A4DCA4`. Not identical, as the SSIM/PSNR already show.
- ffprobe: both raw clips are h264 yuv420p, 768x1344, 24 fps, 243 frames, 10.125 s, AAC 32 kHz stereo.
- Video-render peak VRAM was not in any log (same gap as A4: ComfyUI stdout is not captured). Upscale `peak_torch` was 108 MiB on both arms.
- ffmpeg SSIM/PSNR compared the raw clips, fp16 vs the baseline re-render, 243 frames. No perceptual review and no images were sent.
- Metrics live in `C:\AI\community\runs\r6_speed_20261119\metrics\`.

## Argv restored

After the test, `llama-swap.yaml` was copied back from `llama-swap.yaml.before-r6`. Live SHA-256 again matches `ED16B3923421FC376F24C5ECCAEDAEC5469F6C68C800D0B5AAEAB606DBC6524E`. The restored `comfyui_auto` cmd is the original `--use-ck-attention --disable-pinned-memory --reserve-vram 1.5` with no `--fast`. watch-config reloaded at 18:04:31 CT. ComfyUI was already unloaded; `:10003` is down; `gpu-render.lock` is absent.

The lease line `Max | archive dropped LoRAs + R6 speed test | 2026-11-19 17:44:05 CT` was removed. The lease file is empty.

## Recommendation

**Leave production unchanged (flag off).** `--fast fp16_accumulation` did not beat the baseline: 286.3 s vs 286.5 s is a wall-time tie, but the same-seed output is not a quality tie (mean SSIM 0.78, mean PSNR ~21.7 dB). R6's bar was a blind same-seed comparison that ties or beats the baseline. This fails on quality, and there is no speed win to trade for that change.

Do not enable `cublas_ops` either, unless Derrick later says yes to installing the `cublas_ops` package and we run the same comparison.

No git commit was made on AlienPc or in this clone.
