# U42 PixlStash Tagging — RESULT

- **Date / Start time (CT):** Monday 2026-11-16, job started `11:14:16 CST` (runner initial start `11:25:25 CST`; restarted after InsightFace-interleave update at `11:33:44 CST`).
- **Status:** **Running (detached)** — `u42-pixlstash-tagger.service` (`systemd --user` unit for `evo`, linger enabled) is active and continuing unattended.

## PIDs & How to Follow Progress

- **agy wrapper PID (`U42-agy-wrapper.pid`):** `104941`
- **Detached runner PID (`u42-pixlstash-tagger.service` `MainPID`):** `110346` (previous initial run PID before interleave update: `107138`)
- **Runner script & state (user `evo`):**
  - Script: `/home/evo/AI/pixlstash-tagging/tag_runner.py`
  - State DB: `/home/evo/AI/pixlstash-tagging/u42_state.db`
  - Unit: `/home/evo/.config/systemd/user/u42-pixlstash-tagger.service`
- **Progress files (mode `0644`, counts only, zero secrets; symlinked from `/var/tmp/u42-progress/` so `derekboone` can read directly without weakening `/home/derekboone` `0700`):**
  - Log: `/home/derekboone/evo-x3/records/U42-tagging-progress.log`
  - JSON: `/home/derekboone/evo-x3/records/U42-tagging-progress.json`
- **Follow / control commands:**
  - Watch progress: `tail -f /home/derekboone/evo-x3/records/U42-tagging-progress.log` or `cat /home/derekboone/evo-x3/records/U42-tagging-progress.json`
  - Service status: `sudo -n -iu evo XDG_RUNTIME_DIR=/run/user/1001 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1001/bus systemctl --user status u42-pixlstash-tagger.service`
  - Stop / resume: `systemctl --user stop u42-pixlstash-tagger.service` / `systemctl --user start u42-pixlstash-tagger.service` (resumable and idempotent via `u42_state.db`)

## Devices & Models Used

- **PixlStash built-in models (`default_device`):** Left on **`cpu`** (`server-config.json` unchanged).
  - **Official / package findings on ROCm & Vulkan:** Verified in `/home/evo/.venvs/pixlstash/lib/python3.13/site-packages/pixlstash/utils/accelerator.py` and `startup_checks.py` (`VALID_DEVICE_SETTINGS = {"cpu", "cuda", "mps", "metal", "gpu", "auto"}` — **`vulkan` is not supported**). `gpu_select.py` is NVIDIA-only (`pynvml`). The installed venv has `torch 2.15.0+cu132` (`cuda: False`, `hip: None`) and `onnxruntime 1.32.0` (`AzureExecutionProvider`, `CPUExecutionProvider` only), with no host `/opt/rocm*` or `rocminfo` installed. Per the no->5 GB download rule, no ROCm PyTorch/ORT wheel was downloaded, so PixlStash built-in models and InsightFace (`buffalo_l`) remain on CPU.
- **VLM (`gemma4-heretic` on X3 GPU via `llama-swap`):**
  - Endpoint: `http://127.0.0.1:8080/v1/chat/completions`, model **`gemma4-heretic`** (Gemma 4 26B A4B IT Heretic Q8_0 + Unsloth mmproj BF16, running on AMD Strix Halo GPU via Vulkan-RADV in `llama-swap.service`).
  - Uses already-wired slot settings in `/etc/evo-x3/llama-swap.yaml` (no sampling flags added; `chat_template_kwargs.enable_thinking: false` sent per request for throughput, matching the writer pipeline).
  - Auth: `LLM_KEY_PI` read in-process from existing `0600` `/home/evo/.config/evo-x3/llm.env` (verified HTTP 200 on `/v1/models`; never printed or placed on argv).
- **Face matching:** InsightFace (`buffalo_l`) via PixlStash official API (`POST /api/v1/pictures/face-search` + `POST /api/v1/characters/{id}/faces`) runs first for already-named characters (`>= 0.55` strict threshold; interleaved in bounded chunks with `combine=mean`). VLM only attempts naming when unassigned faces exist (`unassigned_faces > 0`), and writes confident proposed names as tags via `POST /api/v1/pictures/{id}/tags` (no sqlite writes).

## Backup Path

- Official SQLite backup-API snapshot taken before any write:
  - `/home/evo/AI/5slock/_u42_vault.db.bak-pre-tag` (`1,016,172,544` bytes, mode `0600`, owner `evo`)
  - `/home/evo/AI/5slock/_u39_vault.db.bak-prerewrite` left untouched.

## Baseline vs Current Counts (Counts Only)

| Metric | Baseline (Pre-write) | Current (`11:34:57 CST`) | Notes |
| --- | --- | --- | --- |
| Pictures (`GET /api/v1/pictures/count` & DB) | 32,964 | 32,964 | Formats: 24,229 JPEG, 8,723 MP4, 12 PNG |
| Faces (`COUNT(*)` on `face`) | 116,876 | 116,876 | 116,677 real faces (`face_index >= 0`), 199 sentinels (`face_index = -1`) |
| Characters (`GET /api/v1/characters`) | 2 | 2 | |
| Faces assigned to characters (`character_id IS NOT NULL`) | 3,719 | 15,690 | +11,971 assigned via official InsightFace API |
| Pictures with `>= 1` tag row | 32,963 | 32,964 | Prior `v259` `tag_prediction` (812,249 CONFIRMED / 506,990 REJECTED) + Florence-2 descriptions (32,964) preserved |
| Total `tag` rows | 816,771 | 816,969 | +198 new VLM tags added via `POST /api/v1/pictures/{id}/tags` |
| Sidecar `pictures_done` | 0 | 12 | |
| Sidecar `pictures_skipped` | 0 | 0 | |
| Sidecar `pictures_failed` | 0 | 0 | |
| Sidecar `faces_processed` | 0 | 11,998 | 11,971 InsightFace assignments + 27 unassigned faces inspected in VLM pass |
| Sidecar `characters_named` (VLM) | 0 | 0 | |

## Observed Rate & ETA

- **Observed `seconds_per_image`:** `5.06 s/image` (includes initial ~23 s `gemma4-heretic` cold model load; steady-state after load was ~3.1 s/image across images 2–12 with `VLM_WORKERS=2`)
- **Observed rate:** `11.87 images/min` (climbing as cold-load amortizes)
- **Estimated ETA:** `1 day, 22:18:57` (and dropping toward ~28 h at steady-state ~3.1 s/image)

## GPU Lock (`gpu-render.lock`) Note

- `/home/derekboone/AI/locks/gpu-render.lock` exists at **0 bytes** (mtime `10:26 CST`, unlocked / no `flock` holder, leftover from the completed U37 3-shot OC test; no live `run_graph_job` / ComfyUI / render process running).
- A naive `comm.gpu_lock_holder` / "no-PID = held" check would have treated this empty leftover as held (`-1`) and blocked forever.
- Per the brief, the file was **not deleted**, and the runner checks only for live holds (non-empty live PID, active `fcntl.flock`, or live render processes in `/proc`) between batches and continued cleanly because nothing is rendering. If a live render takes the GPU later, the runner stops cleanly with exit `0` and updates `U42-tagging-progress.json`.

## What Was Not Done

- **No large (>5 GB) downloads:** Did not install ROCm PyTorch/ORT wheels; `default_device` stays `cpu`.
- **Plugin vs sidecar:** Did not install or configure `openai_compatible_captioner` in PixlStash because `http://127.0.0.1:8080` requires an auth key (`401` without it) and storing a llama-swap key in plain-text plugin settings is disallowed. Implemented the official-API sidecar (`tag_runner.py`) instead, reading `LLM_KEY_PI` in-process from `0600` `/home/evo/.config/evo-x3/llm.env`.
- **No missing key block:** `LLM_KEY_PI` in `/home/evo/.config/evo-x3/llm.env` authenticated cleanly against `http://127.0.0.1:8080/v1/models` (`HTTP 200`).
- **U41 & unrelated files untouched:** Did not touch `/home/evo/AI/community/scripts/parody/`, `build_request.py`, `skills/`, `/etc/evo-x3/llama-swap.yaml`, AlienPc, Windows partitions, or git commits (`git add -A` not run).
