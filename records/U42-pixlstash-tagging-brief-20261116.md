# U42 brief: PixlStash tagging pass on the X3 GPU

Written Mon Nov 16 2026, late morning CT, by Max for Antigravity (Gemini 4 Hydrogen High) on the X3.

Approval: Derrick t1944s7162 — "Yes, start the tagging pass on the X3 GPU."

This job sets up and **starts** the unattended tagging pass, verifies that real progress has begun (counts only), writes RESULT, and exits. The tagging process itself must keep running after you stop. Nothing renders.

Prior context (read these; do not reopen library images):

- Move RESULT: `/home/derekboone/evo-x3/records/U39-pixlstash-move-RESULT.md`
- Plan / model pick: box copies also at `/home/derekboone/evo-x3/records/` if present; originals `/workspace/maxops/pixlstash/pixlstash-integration-findings-20261116.md` (section 7) and `pixlstash-location-plan-20261116.md`. If the box paths are not on this machine, follow this brief and U39. The planned approach is **gemma4-heretic via llama-swap** plus **InsightFace via the official PixlStash API**. Prefer InsightFace when a named gallery match exists; use the VLM only for unmatched faces. Do not invent a legal name with no gallery entry.

## When to start

Start now. U41 is a separate Antigravity job, started 11:01 AM CT, still editing parody scripts and skills. **Do not touch U41's files or wait for it.** Do not edit anything under `/home/evo/AI/community/scripts/parody/`, `/home/evo/AI/community/scripts/build_request.py`, or `/home/evo/AI/community/skills/`. Your work is PixlStash tagging only.

## Who and where

You are launched as `derekboone`. PixlStash and the library belong to `evo`. `/home/evo/AI` is mode 700. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u42-step.sh`) and run:

```
sudo -n -iu evo bash /tmp/u42-step.sh
```

No nested quoting one-liners. Prefer Python in those scripts for API work.

Live service (U39):

- PixlStash 2.0.1, systemd --user `pixlstash.service` for `evo`, linger already yes
- `http://127.0.0.1:9537` (localhost only). OpenAPI is at `/openapi.json` (2.0.1, 285+ paths)
- Active library: `/home/evo/AI/5slock/libraries` (merged vault only; `approved_characters` was not copied)
- Counts to preserve: **32,964 pictures**, **116,876 faces** (faces were counted with read-only `COUNT(*)` on `vault.db`; the official API has no library-wide face total)
- `default_device` is currently `cpu`. `insightface_model_pack` is `buffalo_l`. Do not change the face pack.
- Tokens, 0600, owner `evo` (values never printed, never on argv):
  - `/home/evo/.config/pixlstash/tagger-write.token` — scope ALL (write)
  - `/home/evo/.config/pixlstash/render-read.token` — scope READ
- Config: `/home/evo/.config/pixlstash/server-config.json` (0600)
- llama-swap: `http://127.0.0.1:8080` (systemd `llama-swap.service`, `LISTEN_ADDR=127.0.0.1:8080`, EnvironmentFile `/etc/evo-x3/llm.env`). Vision slot already wired: **`gemma4-heretic`** (Gemma 4 26B A4B IT Heretic Q8_0 + official Unsloth mmproj BF16, `--image-min-tokens 560 --image-max-tokens 1120`, official sampling already in the slot). Do not retune the slot and do **not** edit `/etc/evo-x3/llama-swap.yaml`.

## HARD RULES

- **Never view, open, describe, sample, thumbnail, or base64 library images.** Max and you stay out of the pictures entirely. Only local models may touch them. Never print tag names, captions, descriptions, face/character names, filenames, paths of library stills, or bbox contents in logs or RESULT. **Counts and progress only.**
- Never print tokens, passwords, or API keys, and never put them on a command line. Read them from files into the process environment or a header file. `curl -H "Authorization: Bearer $(cat token)"` prints the token in `ps`; do not do that. Use a script that reads the file and makes the request, or curl `--header @file`.
- No renders, no queueing, no ComfyUI. Do not touch AlienPc's PixlStash, its libraries, or any original ComfyUI folder.
- Do not edit `llama-swap.yaml`. Do not unload a model to serve a live render; if a live render starts, you stop instead.
- No downloads over about 5 GB. If official GPU support for PixlStash's own models would require a large ROCm/PyTorch/ORT wheel, **do not download it**. Leave `default_device=cpu`, run gemma4-heretic on the GPU through llama-swap, and say so in RESULT.
- Do not create new API keys or tokens. Use the existing PixlStash tokens and whatever existing llama-swap credential files already work on this box.
- Do not delete `/home/derekboone/AI/locks/gpu-render.lock` (see the lock section).
- Back up `vault.db` with the official sqlite backup API **before the first write**. 0600, owner `evo`. Do not overwrite `/home/evo/AI/5slock/_u39_vault.db.bak-prerewrite`.
- No `git add -A`. This job should not need a community/render code commit; if you add a small sidecar under evo's PixlStash or `/home/evo/AI/pixlstash-tagging/`, keep it out of git unless it clearly belongs in an existing repo, and never commit tokens.
- Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, Sydney private files, or U41's parody/skill files.

## GPU lock (read this; a leftover file is present)

Path: `/home/derekboone/AI/locks/gpu-render.lock`

**Current state at brief time (do not "fix" it by deleting):** the file exists, **0 bytes**, mtime **10:26 AM CT**. It is leftover from the u37 3-shot OC test, which **finished at 10:26:41 AM CT**. Nothing is rendering now. llama-swap is running as usual. No flock/lsof holder was on the file when Max checked.

How the lock is honored in our tree (verify in the code if you want, but follow this behavior):

- `comm.gpu_lock_holder` in `/home/evo/AI/community/scripts/comm.py`: a file whose **first number is a live PID** is held; a **dead PID is stale and ignored**; a lock file **with no PID is treated as held (`-1`)**, "as in ralph.ps1". `llm_gate()` therefore **would treat this empty leftover as BUSY and would block/idle forever.** Do not use a naive `gpu_lock_holder` / "file exists" / "no PID = held" check as your stop condition.
- X3 render docs also mention `fcntl.flock` on `~/AI/locks/gpu-render.lock` as a local submitter lock (`/home/evo/AI/render/x3/README-X3.md`). Check for a live flock holder too. `/home/evo/AI/locks/` may be a different path than `/home/derekboone/AI/locks/`; honor a **live** hold on either.

**Correct rule for this pass:** treat the GPU as busy only when a **live render** holds it: a lock file whose first number is a **live PID**, or an flock held by a live process, or a live `run_graph_job` / ComfyUI / render process. Recheck between batches. **Do not idle on the current empty leftover.** Log in RESULT that this leftover would have blocked a naive no-PID=held check, and that you continued because nothing is rendering. Do not delete the file.

If a live render later takes the GPU, **stop the tagging process cleanly**, write/update RESULT with counts so far and a resume note, and exit. Do not fight the render for VRAM.

## Work

### 0. Preflight

- Confirm `pixlstash.service` is active for `evo` and `GET /api/v1/pictures/count` (READ or ALL token, from a script) is 32,964. Confirm faces still 116,876 by the same read-only `COUNT(*)` method U39 used (no image rows dumped).
- Confirm no live render, per the lock rule above.
- sqlite-backup `/home/evo/AI/5slock/libraries/vault.db` to `/home/evo/AI/5slock/_u42_vault.db.bak-pre-tag` (0600, evo) **before the first write**.
- Record baseline counts in the progress log: pictures, faces, characters (count only; U39 saw 2 characters), and how many pictures already have tags / pending-retag sentinels. Official hooks: `TagTask` pending-retag sentinels, and the tagger settings in the live server. Use SQL `COUNT` or official count endpoints. **Do not SELECT or print tag strings.**

### 1. Official PixlStash tagging and faces

Use PixlStash's official tagging and face features, not sqlite writes.

Consult, in this order: official docs ([ai](https://pixlstash.dev/ai.html), [api](https://pixlstash.dev/api.html), [install](https://pixlstash.dev/install.html), the 2.0.1 README/repo), the live OpenAPI, and the installed package under `/home/evo/.venvs/pixlstash/`. Known official write path at brief time (confirm if the live OpenAPI differs):

- `GET /api/v1/taggers` — registered engines (PixlStash Tagger, WD14, Florence-2, JoyCaption, plus any plugins)
- `POST /api/v1/pictures/{id}/reset_tags` and bulk `POST /api/v1/pictures/reset_tags` with `{ "picture_ids": [...], "model": "<engine>" }` — queues a pending-retag sentinel; background `TagTask` does the work
- `POST /api/v1/pictures/{id}/tags` — write tags (sidecar path)
- Character membership and face routes already in OpenAPI (`/api/v1/characters`, `/api/v1/pictures/{id}/faces`, `/api/v1/face-clusters`). `GET /api/v1/face-clusters` needs the official query shape (a bare GET 422'd during U39)
- `GET /api/v1/tag_health` is fine for a **count** of rows; do not dump tag names into the log

The library already has 116,876 faces from the copied vault. Do not wipe faces. Use official InsightFace grouping / membership. Prefer official batch APIs over per-picture chatty loops where they exist.

The pass must be **resumable and idempotent**: skip work already done by the same engine; if you or the machine stop, a restart continues the remainder. Batch picture ids. Log progress as counts.

### 2. PixlStash `default_device` and the X3 GPU (AMD Strix Halo)

Check official docs/repo for GPU on **AMD ROCm or Vulkan** on this hardware. Then decide.

Known at brief time (re-verify in the installed package, do not assume this is still complete):

- Documented `default_device` values are along the lines of `cpu`, `cuda`, `auto`, `gpu`, `mps`. **Not `vulkan`.** `cuda` is the NVIDIA path.
- Official AMD path is **experimental ROCm**, documented mainly for the desktop app ("pip/server, you are more on your own"). PyTorch's ROCm build talks to the GPU through the CUDA API; official README says the bundled ONNX Runtime is the CPU build, so **face extraction and WD14 stay on CPU** unless `onnxruntime-migraphx` is installed.
- This venv is `torch 2.15.0+cu132` (NVIDIA wheel), `torch.cuda.is_available() == False`, ORT providers `AzureExecutionProvider` + `CPUExecutionProvider` only. U39 already set CPU after the service logged that GPU utilisation sampling saw no CUDA device, so it would not contend with llama-swap.

**Switch `default_device` off CPU only if** the official docs support that value on this box, a quick probe shows it actually works, and it does **not** require a download over ~5 GB. If you change it: back up `server-config.json` first (for example `server-config.json.bak-20261116-u42`), restart the user service, and verify pictures=32,964 and faces=116,876 and that the server is still bound to localhost. If counts move or the service fails, restore the backup and leave it on CPU.

If GPU is not officially usable here without a large download: **leave `default_device=cpu`**, do not install huge wheels, and say so in RESULT. PixlStash's own taggers and InsightFace then stay on CPU. The GPU work is gemma4-heretic through llama-swap, which is the planned model anyway.

### 3. gemma4-heretic through llama-swap (required)

This is the planned uncensored local VLM. It will evict flash-next / qwen27b while it is loaded; that is expected and already approved. Do not retask flash-next. Use official model-card / already-wired slot settings; do not add sampling flags.

Official plugin path: `pixlstash-cli plugins install openai_compatible_captioner`, then point it at `http://127.0.0.1:8080` with model `gemma4-heretic`. Plugins run in the server process. **Do not paste a llama-swap key into PixlStash's plain-text plugin settings** if you can avoid it (this was a documented risk in the findings). If the X3 endpoint can be called from localhost without storing a key in the plugin, that is best. Otherwise write a small sidecar that reads any required key from an existing 0600 file and writes tags / character membership through the official API.

llama-swap at `:8080` returned HTTP 401 without a key when Max probed `/v1/models`. `/etc/evo-x3/llm.env` is the unit's EnvironmentFile and holds `LLM_KEY_*` names; at brief time those entries were still documented as placeholders. **Find the existing official way local X3 clients authenticate** (other 0600 files under `/etc/evo-x3/` or evo/derekboone config). Read the file in-process. Never invent a new key, never print it, never put it on argv. If you genuinely cannot call llama-swap without a missing key Derrick must type, stop, write RESULT explaining that, and do not block the official PixlStash CPU tag/face pass if that part can still run.

Person naming: InsightFace match to already-named people / official membership first. The VLM may propose names only for unmatched clusters, written back as person tags or character membership through the API. No sqlite writes, no thumbnails in logs.

### 4. Runner shape (detached; you do not babysit the whole library)

32,964 pictures will take a long time. Do **not** keep the Antigravity process looping on the full library.

- Write a resumable runner as user `evo` (a `systemd --user` unit, or a setsid/nohup process with a pid file). Official PixlStash `TagTask` may already be the right engine for built-in taggers once you queue official `reset_tags` batches; still provide a progress logger and a clean stop-on-live-render hook.
- Progress log (counts only): `/home/derekboone/evo-x3/records/U42-tagging-progress.log` plus a small machine-readable file such as `/home/derekboone/evo-x3/records/U42-tagging-progress.json` (pictures_done, pictures_skipped, pictures_failed, faces_processed, characters_named, seconds_per_image, eta, last_update CT). derekboone must be able to read the progress files (put them in `records/`, mode 644, no secrets).
- Start the runner. Confirm the first real progress: a tagged/processed count that increases, via an official count or the progress log, within a few minutes.
- Then write RESULT and stop. Leave the runner going.

### 5. Stop / resume

The runner must stop cleanly if a live render takes the GPU, if picture count leaves 32,964 unexpectedly, or if the service dies. It must be safe to start again and continue. A clean stop updates RESULT or the progress file with counts and a resume command.

## RESULT

Write `/home/derekboone/evo-x3/records/U42-RESULT.md` when the runner is started and the first real progress is visible, or sooner if you are blocked. Include:

- Start time in America/Chicago (CT)
- agy / runner PIDs and how to follow progress
- Device used for PixlStash's own models (GPU or why not; official finding on ROCm/Vulkan)
- Device and model used for the VLM (expect GPU via llama-swap, `gemma4-heretic`)
- Backup path for `vault.db`
- Baseline vs current counts: pictures, faces, pictures tagged / skipped / failed, faces processed, character names assigned (counts only)
- Observed time per image, rate, and ETA
- The leftover `gpu-render.lock` note (would a naive check have blocked? you continued because the u37 test was already finished)
- Anything you did not do (large download skipped, plugin vs sidecar, key missing, U41 left alone)

If you are blocked before the runner starts, still write RESULT with the block and stop.

## STOP CONDITION

The first real tagged/processed count has increased, RESULT is written, the runner is detached and still going (or you are blocked and RESULT says why). Then stop. Do not wait for all 32,964 pictures.
