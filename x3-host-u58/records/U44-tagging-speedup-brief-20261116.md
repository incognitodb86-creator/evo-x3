# U44 brief: speed up PixlStash tagging (Gemma alongside faces, several pictures at once)

Written Mon Nov 16 2026, late morning CT, by Max for Antigravity (Gemini 4 Hydrogen High) on the X3.

## Approval (already granted — do the work)

Derrick, widget t1950s7194: "Yes, run Gemma alongside the faces and tag several pictures at once."

This job changes the already-running U42 sidecar so Phase A (InsightFace, CPU) runs at the same time as VLM tagging (gemma4-heretic, GPU), and so the VLM tags N pictures at once (default 3). Then restart the runner from where it left off, verify both phases move together, write RESULT, and stop. The tagging process itself must keep running after you stop.

## When to start

Start now. Two other Antigravity jobs may still be running. They are unrelated to this speedup. **Leave them running. Do not kill them, do not wait for them, and do not touch their files except as noted below.**

- **U43** (community git merge, test, and push): `U43-agy-launch.sh` / agy around PID 110567, started 11:34 AM CT. Do not touch `/home/evo/AI/community`, do not run git there, and do not write U43 records.
- **U42** (original tagging-pass agy, PID **104945**, wrapper `/home/derekboone/evo-x3/records/U42-agy-launch.sh`, started 11:14 AM CT): it started the runner and may still be waiting to write `U42-RESULT.md` after the first Gemma tags. Those tags have already started (see current state below). **Leave the U42 agy process running.** Do not kill it, and do not write or overwrite `U42-RESULT.md` or the U42 brief/log/meta. You **are** allowed to edit `tag_runner.py`, the `u42-pixlstash-tagger.service` unit, and (only) the `gemma4-heretic` entry in llama-swap, because that is this approved speedup. Before you edit `tag_runner.py`, copy it to `_archive` (see Work). If the file's mtime is still changing because U42 is mid-edit, wait until it has been stable for 60 seconds, then back it up and proceed. This speedup is now your job, not U42's.

## Who and where

You are launched as `derekboone`. PixlStash, the library, and the runner belong to `evo`. `/home/evo/AI` is mode 700. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u44-step.sh`) and run:

```
sudo -n -iu evo bash /tmp/u44-step.sh
```

For systemd --user as evo, set `XDG_RUNTIME_DIR=/run/user/1001` (evo's uid is 1001) inside that script. No nested quoting one-liners. Prefer Python in those scripts for API work.

`/etc/evo-x3/llama-swap.yaml` is root-owned. Back it up and edit it with `sudo -n`; do not print secrets from `/etc/evo-x3/llm.env` or any 0600 token file.

## Current state (verified ~11:35 AM CT; re-check live counts)

- Sidecar: `/home/evo/AI/pixlstash-tagging/tag_runner.py` (28,421 bytes, 746 lines, mtime 11:33 AM CT). Python 3 under `/home/evo/.venvs/pixlstash/bin/python`.
- systemd --user unit (evo, linger already yes): `u42-pixlstash-tagger.service` at `/home/evo/.config/systemd/user/u42-pixlstash-tagger.service`, enabled, **active**. Current Main PID at brief time: **110346** (started 11:33:44 CST after U42 sent SIGTERM to the previous process and restarted the unit so InsightFace and VLM batches could interleave). The older PID 107138 is gone. Re-read the live Main PID; do not assume 110346 lasts.
- Progress (keep this path and format): `/home/derekboone/evo-x3/records/U42-tagging-progress.log` and `.json` are symlinks to `/var/tmp/u42-progress/`. Mode 644, counts only, derekboone can already read them. At ~11:35 CT the json showed: `total_pictures=32964`, `pictures_done=20`, `pictures_skipped=0`, `pictures_failed=0`, `tags_added=309`, `faces_assigned_insightface=11971`, `faces_processed=12006`, `seconds_per_image≈4.33`, `rate_per_min≈13.86`. Just after the 11:33 restart, a 10-picture sample was `5.44 s/image` and ETA about 2 days. **These are the "before" rates** (single-picture VLM, phases not truly concurrent). Re-read live numbers when you start, and put both the brief-time figures and your fresh baseline in RESULT.
- Resume state: `/home/evo/AI/pixlstash-tagging/u42_state.db`. Pictures already done must stay skipped. Do not wipe this db or the progress files.
- The runner already mentions ThreadPool / concurrent / workers, and U42 changed it at 11:33 to interleave InsightFace (`combine=mean`, `>= 0.55`, 300-face chunks) with VLM batches. After that restart, face matching barely moved once VLM began (11,971 assigned, then only up to 12,006 while pictures_done rose). Treat the current interleave as **same-thread sharing**, not the concurrent Phase A this brief asks for. Read the live code and implement real overlap (a thread or separate process).
- PixlStash: `http://127.0.0.1:9537`, library `/home/evo/AI/5slock/libraries`, **32,964 pictures**, **116,876 faces**. Tokens, 0600, owner `evo` (never printed, never on argv):
  - `/home/evo/.config/pixlstash/tagger-write.token` — scope ALL (write)
  - `/home/evo/.config/pixlstash/render-read.token` — scope READ
- llama-swap: systemd `llama-swap.service` (main PID 1403 at brief time), `LISTEN_ADDR=127.0.0.1:8080`, config `/etc/evo-x3/llama-swap.yaml`, EnvironmentFile `/etc/evo-x3/llm.env`, wrapper `/usr/local/bin/evo-llama-swap`. The **gemma4-heretic** slot is already loaded. Live llama-server flags include `-np 2 -c 524288` (comment in the yaml: 262,144 per slot) and `concurrencyLimit: 2`. Official sampling, mmproj, and image token budget (`--image-min-tokens 560 --image-max-tokens 1120`) stay as they are.
- **U27 history (read this before raising `--parallel`):** on 2026-11-15 the yaml was tried at `-np 4 -c 1048576` / `concurrencyLimit: 4`. llama-server aborted twice in `server_slot::prompt_save` (GGML_ASSERT tensor not allocated, kyuz0 build 12405). It was rolled back to `-np 2`. If N=3 errors, OOM, or hits that assert, drop to 2, then 1, and say so in RESULT. Do not retry 4.
- Vault backups already on disk (do not overwrite them): `/home/evo/AI/5slock/_u42_vault.db.bak-pre-tag` (11:15 AM CT, ~970 MiB) and `/home/evo/AI/5slock/_u39_vault.db.bak-prerewrite`. Live `vault.db` was ~987 MiB at 11:34. Root filesystem had ~739 GiB free; a fresh `_u44_vault.db.bak-pre-speedup` will fit.
- Stale lock: `/home/derekboone/AI/locks/gpu-render.lock` is still **0 bytes**, mtime **10:26:41 AM CT**. Do not delete it. Do not treat it as a live hold. Same rule as U42: the GPU is busy only when a live render holds it (lock first number is a live PID, a live flock holder, or a live `run_graph_job` / ComfyUI / render process).
- There is no `_archive` under `/home/evo/AI/pixlstash-tagging/` yet. Create one. Other `_archive` dirs exist under `/home/evo/AI/{render,forge,sydney,community}/`.

## HARD RULES

- **Never view, open, describe, sample, thumbnail, or base64 library images.** Never print tag names, captions, descriptions, face/character names, filenames, paths of library stills, or bbox contents in logs or RESULT. **Counts and progress only.**
- Never print tokens, passwords, or API keys, and never put them on a command line. Read them from the existing 0600 files into the process environment or a header file. `curl -H "Authorization: Bearer $(cat token)"` prints the token in `ps`; do not do that.
- No ROCm / PyTorch / onnxruntime-migraphx download. Leave PixlStash `default_device=cpu`. Face matching stays on CPU; only gemma4-heretic uses the GPU, through llama-swap.
- No deleting. Back up first and use `_archive` (or a `.bak-…` next to the yaml) instead of deleting. Do not overwrite the existing `_u39_` / `_u42_` vault backups.
- Do not delete `/home/derekboone/AI/locks/gpu-render.lock`. Do not let that stale 0-byte file block the runner.
- Do not create new API keys or tokens. Use the existing PixlStash tokens and the existing official llama-swap credential files already on this box.
- Edit **only** the `gemma4-heretic` entry in `/etc/evo-x3/llama-swap.yaml` (the `-np` / `-c` and matching `concurrencyLimit` as needed). Do not retune sampling, mmproj, image token budget, or any other model (`qwen27b`, `embed-small`, aliases, groups). Do not edit `/etc/evo-x3/llm.env`.
- No renders, no queueing, no ComfyUI, no `git add -A`, no force push. Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, Sydney private files, AlienPc, the original ComfyUI folder, or U43's community git tree.
- If a live render later takes the GPU, stop the tagging process cleanly, leave resume state intact, write RESULT, and exit. Do not fight the render for VRAM.

## Work

### 0. Preflight

- Confirm `u42-pixlstash-tagger.service` is active and record the live Main PID, progress counts, and current `seconds_per_image` / `rate_per_min` / ETA. These are the before-speedup baseline.
- Confirm pictures are still 32,964 and faces still 116,876 (official count / read-only `COUNT(*)`; no image rows dumped). If the picture count has left 32,964, stop and write RESULT.
- Confirm no live render, per the lock rule above.
- Disk: if `/` still has plenty of free space (it did: ~739 GiB), take a fresh official sqlite backup of `/home/evo/AI/5slock/libraries/vault.db` to `/home/evo/AI/5slock/_u44_vault.db.bak-pre-speedup` (0600, owner `evo`) **before you restart the runner**. Do not overwrite `_u42_vault.db.bak-pre-tag`. If disk is unexpectedly tight, skip the new backup, say why, and rely on the existing `_u42_` copy.

### 1. Back up and change `tag_runner.py`

Create `/home/evo/AI/pixlstash-tagging/_archive/` if needed and copy the live `tag_runner.py` there with a timestamped name (for example `tag_runner.py.bak-20261116-u44-pre-speedup`).  Owner `evo`. Then change the runner so:

1. **Phase A runs concurrently with VLM tagging**, using a thread or a separate process. InsightFace stays on CPU. The face-match assignment still wins: the VLM may only name faces that still have `character_id` **None** when it writes them, **re-checked immediately before the write** (a TOCTOU-safe read of the current assignment, not a value cached at the start of the VLM call). Do not invent a legal name with no gallery entry, and do not overwrite an InsightFace assignment.
2. **VLM tagging uses N concurrent requests**, defaulting to **3**, configurable by environment variable and by a CLI arg (pick a clear name such as `U44_VLM_CONCURRENCY` / `--vlm-concurrency`). Keep official API writes. Pictures already done or skipped in `u42_state.db` stay skipped (resume must keep working).
3. **Progress files stay in the existing json/log format and paths** (the `records/` symlinks to `/var/tmp/u42-progress/` are fine). Add VLM-specific rate / ETA fields (for example VLM seconds per image, VLM pictures per minute, VLM ETA) without dropping the existing keys. Counts only; no tag or caption text.
4. If you need a unit change to pass N (Environment= or ExecStart args), back up the unit into the same `_archive` first, then `daemon-reload` as evo before the restart.

Do not switch to a PixlStash plugin that would store a llama-swap key in plain text. Keep the sidecar.

### 2. llama-swap: `--parallel N` only if needed, official docs, careful reload

Concurrent VLM requests only help if the **gemma4-heretic** llama-server has enough slots. Today that slot is already `-np 2 -c 524288` with `concurrencyLimit: 2`.

- Read the official llama.cpp server docs for `--parallel` / `-np` and how `-c` / `--ctx-size` is split across slots. Each slot must still fit the image + prompt (image budget is already 560–1120 tokens). Do not guess; follow the docs and the existing yaml comments (native context 256K; current 2×262,144 = 524,288).
- For N=3, raise that model's `-np` and `concurrencyLimit` to 3, and scale `-c` so each slot still has enough context. Do not blindly copy the U27 `-np 4 -c 1048576` settings. Prefer keeping total KV reasonable on this 128 GB Strix Halo box; if the docs say `-c` is the total cache, `3 × 262144` may be unnecessary and risky. A smaller per-slot size is fine if it still fits image + prompt.
- Back up the yaml first, for example `/etc/evo-x3/llama-swap.yaml.bak-20261116-u44-pre-speedup`. Edit **only** the `gemma4-heretic` entry. Leave comments that record the U44 change.
- **Before reload:** confirm no other client is mid-request on `gemma4-heretic`. Check Render, Sydney, and Forge pi chats (and llama-server slot / queue state). The tagging runner itself will be mid-request; that is expected — stop the tagger **cleanly** first so you are not yanking a write, then reload, then start the tagger again. If Render / Sydney / Forge is busy on this model, **wait** until it is idle. Do not unload a model to serve a live render; if a live render starts, stop and write RESULT instead.
- Reload llama-swap the documented way. Changing `-np` / `-c` only takes effect when the `gemma4-heretic` container is recreated. Prefer a model-level reload / unload of just that model over bouncing the whole `llama-swap.service` if the docs support it. `systemctl restart llama-swap` is the known blunt path (and the documented rollback in U33), but it drops every model. A SIGHUP config reload has raced a warmup request before (U29, HTTP 500, "upstream command exited prematurely"); if you use it, wait for the new server to come healthy before sending work. After reload, confirm `/health` (or the official check) and that the new `-np` / `-c` are actually in the live command line.
- If N=3 causes errors, OOM, or the U27 `prompt_save` assert, roll that yaml entry back toward `-np 2` (or 1 as a last step), reload again, set the runner's N to match, and report that. Do not leave llama-swap broken, and do not touch other models while recovering.

### 3. Restart the tagger and verify (about 5 minutes)

- Restart `u42-pixlstash-tagger.service` as evo after the runner (and llama-swap, if you changed it) are in place. Resume must skip pictures already done.
- Confirm **both** phases progress at the same time: Phase A face counts keep rising **while** `pictures_done` rises. Confirm the VLM picture count is actually increasing, not stuck.
- After about **5 minutes** of the new runner, record seconds per image, pictures per minute, and the ETA, and compare them to the before-speedup baseline. If N=3 is failing, drop to 2, then 1, as above, and measure again.
- Leave the runner going.

## RESULT

Write `/home/derekboone/evo-x3/records/U44-RESULT.md` when both phases are progressing together and the VLM count is rising (after that ~5 minute sample), or sooner if you are blocked. Include:

- Start / verify times in America/Chicago (CT)
- agy / runner PIDs and how to follow progress
- Diff summary of `tag_runner.py` (and the unit, if changed)
- llama-swap change (old vs new `-np` / `-c` / `concurrencyLimit`; how you reloaded; whether you had to drop to 2 or 1)
- Rates before and after: seconds per image, pictures per minute, ETA, plus face-match rate before and after if you have it
- Backup paths: runner `_archive` copy, yaml `.bak`, `_u44_vault.db.bak-pre-speedup` (or why it was skipped)
- That U42 agy (104945) and U43 were left running, and that the stale 0-byte `gpu-render.lock` was not deleted and did not block the runner
- Anything you did not do (ROCm skipped, N reduced, other client made you wait, U42 mid-edit delay)

If you are blocked, still write RESULT with the block and stop.

## STOP CONDITION

Both phases are progressing at the same time, the VLM picture count is rising, a ~5 minute rate/ETA sample is in RESULT (or you dropped N and recorded that), RESULT is written, and the runner is detached and still going — or you are blocked and RESULT says why. Then stop. Do not wait for all 32,964 pictures, and do not babysit U42 or U43.
