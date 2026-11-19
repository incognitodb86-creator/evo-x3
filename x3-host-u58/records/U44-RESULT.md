# U44 Result: PixlStash Tagging Speedup (Concurrent Phase A + N=3 VLM)

**Status:** Complete and verified; `u42-pixlstash-tagger.service` is running unattended in the background.

## Times (America/Chicago / CT)

- **U44 started:** `2026-11-16 11:36:50 CST`
- **Before-speedup tagger stopped cleanly:** `2026-11-16 11:42:02 CST` (exit 0 on `SIGTERM`)
- **llama-swap reloaded & warmed up (`-np 3 -c 393216`):** `2026-11-16 11:42:25 CST` – `11:42:48 CST`
- **U44 tagger started:** `2026-11-16 11:43:01 CST` (`started_at_ct: 2026-11-16 11:43:02 CST`)
- **30-second concurrency check:** `2026-11-16 11:43:34 CST`
- **~5-minute verification sample:** `2026-11-16 11:48:39 CST` (~5 min 37 sec elapsed)

## PIDs & How to Follow Progress

- **U44 agy PID:** `111836` (wrapper `111832`)
- **Live runner (`u42-pixlstash-tagger.service`):** Main PID `116492` (`active (running)`), running `/home/evo/.venvs/pixlstash/bin/python -u /home/evo/AI/pixlstash-tagging/tag_runner.py` with `U44_VLM_CONCURRENCY=3`
- **llama-swap / llama-server PIDs:** `116263` (`llama-swap`), `116344` (`podman run` `llama-swap-gemma4-heretic`), `116372` (`llama-server` on `127.0.0.1:8081`)
- **Progress files (counts only):**
  - JSON: `/home/derekboone/evo-x3/records/U42-tagging-progress.json` (symlink to `/var/tmp/u42-progress/U42-tagging-progress.json`)
  - Log: `/home/derekboone/evo-x3/records/U42-tagging-progress.log` (symlink to `/var/tmp/u42-progress/U42-tagging-progress.log`)
  - Service status: `sudo -n -iu evo bash -c 'XDG_RUNTIME_DIR=/run/user/1001 systemctl --user status u42-pixlstash-tagger.service'`

## Preflight & Baseline Checks

- **Library counts confirmed (read-only `COUNT(*)`):** `32,964` pictures and `116,876` faces in `/home/evo/AI/5slock/libraries/vault.db` (`character_count = 2`).
- **GPU render lock:** `/home/derekboone/AI/locks/gpu-render.lock` remained `0` bytes (`Nov 16 10:26`); not deleted, no flock held, no live render process running.
- **Disk space:** `739 GiB` free on `/` (`/dev/mapper/fedora-root`).

## Changes Made

### 1. `/home/evo/AI/pixlstash-tagging/tag_runner.py` (mode `0750`, owner `evo`)

- **Concurrent Phase A (InsightFace, CPU):** Moved InsightFace matching into a dedicated background thread (`run_phase_a_loop`) running simultaneously with VLM tagging from startup, instead of interleaving synchronously in the main thread every 250 VLM pictures. Preserved `combine=mean` and `INSIGHTFACE_STRICT_THRESHOLD = 0.55`. Added persistent per-run tracking (`already_owned_faces`, `attempted_faces_by_char`) and per-picture `/faces` batch caching so Phase A does not re-scan already-assigned faces across rounds.
- **TOCTOU-safe face naming check:** In `process_one_picture`, immediately before writing any `person ...` tag when `vlm_people` is non-empty, `count_unassigned_faces(pid)` re-fetches `GET /api/v1/pictures/{pid}/faces` to confirm how many faces still have `character_id is None` at write time (rather than relying on the pre-VLM count). Never creates character gallery entries and never overwrites InsightFace assignments.
- **N=3 concurrent VLM requests:** Added `U44_VLM_CONCURRENCY` env var and `--vlm-concurrency` CLI argument (default `3`, validated `1..16`). Replaced per-batch barrier `ThreadPoolExecutor` (`BATCH_SIZE = 50`, `VLM_WORKERS = 2`) with a single `ThreadPoolExecutor(max_workers=self.vlm_concurrency)` fed continuously via a sliding in-flight window (`max(N*2, N+1)`) and 200-picture bulk tag prefetching, draining cleanly on `SIGTERM`/`SIGINT` without losing completed picture records.
- **Thread-safe HTTP & failure recovery:** Switched from shared `httpx.Client` instances to thread-local clients (`get_pixl_client()`, `get_llm_client()`) with short transient retries on `ReadError`/`RemoteProtocolError`/`ConnectError`, and added thumbnail fallback (`/api/v1/pictures/thumbnails/{pid}.webp`) when `/api/v1/pictures/{pid}.{fmt}` returns `400`, `404`, `500`, or `httpx.HTTPError` (recovering prior `HTTP_500` and `ReadError` failures caused by non-latin1 header encoding on some original stills).
- **Progress reporting:** Protected `ProgressReporter.write()` with a `threading.Lock` and atomic per-thread temp files. Kept all existing JSON keys and log format, and added `vlm_concurrency`, `vlm_session_processed`, `vlm_seconds_per_image`, `vlm_pictures_per_min`, `vlm_eta`, `phase_a_status`, `phase_a_session_assigned`, and `phase_a_faces_per_min`. Resume state in `u42_state.db` (`done`/`skipped` skipped, failed retried) was preserved.

### 2. `/home/evo/.config/systemd/user/u42-pixlstash-tagger.service`

- Added `Environment=U44_VLM_CONCURRENCY=3` and ran `systemctl --user daemon-reload` as `evo` before restart.

### 3. `/etc/evo-x3/llama-swap.yaml` (only `gemma4-heretic` modified)

- **Old:** `-np 2 -c 524288` (`2 × 262,144` per slot) and `concurrencyLimit: 2`.
- **New:** `-np 3 -c 393216` (`3 × 131,072` per slot, fitting the `560–1120` image token budget + prompt while keeping total KV memory smaller than `524288` to avoid U27's `-np 4 -c 1048576` `server_slot::prompt_save` crash) and `concurrencyLimit: 3`.
- **Reload method:** Confirmed no other clients were active on `gemma4-heretic` (all slots idle after stopping the tagger; no other llama-swap model containers loaded), validated config with `llama-swap -validate` (`config is valid: 5 model(s), 0 peer(s)`), restarted `llama-swap.service` (`evo-llama-swap` does not run `-watch-config`), verified `http://127.0.0.1:8080/health`, warmed up `gemma4-heretic` (`HTTP 200`), confirmed `http://127.0.0.1:8081/health` (`{"status":"ok"}`), `/slots` (`3` slots at `n_ctx=131072`), and live command line `-np 3 -c 393216`.
- **Did not need to drop N:** `N=3` ran cleanly for the full 5+ minute check with zero llama-server errors, OOMs, or asserts.

## Rates & Verification (Before vs After)

| Metric | Brief Baseline (~11:35 CST) | Fresh Pre-Stop Baseline (11:42:02 CST, PID 110346) | After U44 Full 5.6-min Window (11:43:02 → 11:48:39 CST, PID 116492) | After U44 Steady-State VLM Post-Phase-A (11:44:59 → 11:48:39 CST) |
|---|---:|---:|---:|---:|
| `pictures_done` | 20 | 134 | 222 (+88) | 155 → 222 (+67 in 220s) |
| `pictures_failed` | 0 | 44 | **0** (all 44 recovered) | 0 |
| `tags_added` | 309 | 1,995 | 3,312 (+1,317) | — |
| `faces_assigned_insightface` | 11,971 | 11,971 (stalled) | **15,459** (+3,488; `phase_a_status=completed`) | 15,459 (completed at 11:44:48) |
| `faces_processed` | 12,006 | 12,094 | 15,704 (+3,610) | — |
| `seconds_per_image` | 4.33 | 3.62 | 3.79 (includes Phase A overlap + 44 failure retries) | **3.28** |
| `rate_per_min` | 13.86 | 16.59 | 15.85 | **18.27** |
| `eta` | 1 day, 15:37:27 | 1 day, 9:00:44 | 1 day, 10:28:12 | ~1 day, 6h |
| `phase_a_faces_per_min` | stalled after initial 300 | stalled (0 for 8m) | 619.71 avg (`2,379–4,139` fpm peak while active) | completed |

**Concurrent progress verified:** Between `11:43:02` and `11:44:29 CST`, `faces_assigned_insightface` rose continuously (`11,971 → 15,459`, `+3,488` faces) **at the exact same time** as `pictures_done` rose (`134 → 150`) across all 3 `gemma4-heretic` slots (`id 0`, `id 1`, `id 2`). Phase A finished all remaining `>= 0.55` matches at `11:44:48 CST`, and VLM tagging continued steadily (`pictures_done = 222`, `pictures_failed = 0` at `11:48:39 CST`).

## Backups Created (Preserved)

- **Runner backup:** `/home/evo/AI/pixlstash-tagging/_archive/tag_runner.py.bak-20261116-u44-pre-speedup`
- **Unit backup:** `/home/evo/AI/pixlstash-tagging/_archive/u42-pixlstash-tagger.service.bak-20261116-u44-pre-speedup`
- **llama-swap yaml backup:** `/etc/evo-x3/llama-swap.yaml.bak-20261116-u44-pre-speedup`
- **Vault sqlite backup (`0600`, owner `evo`):** `/home/evo/AI/5slock/_u44_vault.db.bak-pre-speedup` (`1,037,094,912` bytes; existing `_u39_` and `_u42_` backups untouched)

## Other Jobs, Locks & Skipped Items

- **U42 & U43:** Left untouched and never killed or had their files/records overwritten (U42 agy PID `104945` had already exited before U44 started at `11:36:50 CST`; U43 agy PID `110567` was running during U44 preflight and finished on its own; `/home/evo/AI/community` and `U42-RESULT.md` were not touched).
- **Stale lock:** `/home/derekboone/AI/locks/gpu-render.lock` (`0` bytes, `10:26` CT) was left in place and did not block the runner.
- **Not done / not needed:**
  - No ROCm / PyTorch / onnxruntime-migraphx downloads (`default_device=cpu` left untouched).
  - No drop from `N=3` to `2` or `1` needed (`-np 3 -c 393216` ran with 0 errors).
  - No U42 mid-edit wait needed (`tag_runner.py` mtime `11:33:41 CST` was already stable >3 minutes at preflight).
  - No other client wait needed (`gemma4-heretic` slots were idle after stopping the tagger).
