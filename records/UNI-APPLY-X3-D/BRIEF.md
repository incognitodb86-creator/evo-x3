Goal: After `UNI-APPLY-X3-A` has a `RESULT.md`, apply the rest of the X3 file items on the EVO-X3 (SK1, SK2, SK3, SK5, RP1-RP3, FX1 incl. the Hermes copy, ST6 dry run) under the X3 lease, so the writer benchmark (`BENCH-X3-W1`) tests the prompt we keep.

# UNI-APPLY-X3-D (X3 Forge): rest of the X3 files, Nov 19 2026

Authority: Derrick 2026-11-19 (11:11/11:16 CT Card 2 file work; 13:09 CT render review handoff RP1-RP3; prompting chat FX1; 13:15 CT skills review SK1-SK5; t2546u/t2571u ST6) and `records/uplan/PLAN.md` "Order of work" step X2. Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required)
- `/home/derekboone/evo-x3/records/UNI-APPLY-X3-A/RESULT.md` exists. If not, stop (`BLOCKED`) without taking the lease.
- X3 lease free (`/home/derekboone/AI/locks/x3-lease.txt` empty). No active render (`ps aux | grep -E 'queue-remote|run_queue' | grep -v grep` empty).
- Max import of `mono` (this brief's commit or newer) into `/home/derekboone/evo-x3`, gitleaks clean. The bridge includes `1f8eb17` (S1b `EVO_AI_ROOT` paths and `lint_ctx.json` for N3), `8c942bc` (Ralph loop `mono` fix), `9b10d43` (`--prose-file`), `9d35c65` (`flux_still.py`, `detect_still_identity`, H3 LoRA/`--realism-lora`, `beta7_convert` wiring, `writer_prompt.md` recompile), and `c012e81` (`miraclein_refmod.candidate` schema fix, Flux Photographer persona + `--hybrid`, `syntax-check.ts` YAML check). After pull/bridge, run `python3 -m pytest -q -p no:cacheprovider test_prose_file_gate.py test_flux_h3_redteam.py test_beta7_convert.py` (all pass) plus full `pytest -q` in `community/scripts/parody` and record pass/fail counts. Since `MONO-S5` has already switched over (`git -C /home/evo/AI/evo-x3 pull --ff-only`), pull the `mono` clone directly instead of part-branch patches.

## Access & Lease
- Doer: X3 Forge as `evo`. `sudo` only for `/usr/local/bin` installs and rollbacks.
- Lease take: ONE line `forge-x3 | UNI-APPLY-X3-D | <start time>` in `/home/derekboone/AI/locks/x3-lease.txt` (stop if not empty). Release: truncate it when done or blocked.
- Backup root: `/home/evo/AI/_archive/20261119/x3-d/`.

## Work (stop on first failure)

### Step 0 — record and back up
- Record `git -C <checkout> rev-parse HEAD` for `/home/evo/AI/render`, `/home/evo/AI/community`, `/home/evo/AI/forge`.
- Back up: `render/AGENTS.md`, `render/OPERATOR.md`, `render/writer_pipeline/{writer_prompt.md,config.yaml}`, `community/scripts/{remote_comfy.py,run_queue.py}`, `community/scripts/parody/{build_request.py,render_writer_pipeline.py}`, `/home/evo/.pi/agent/settings.json`, `forge/.pi/settings.json`.

### Item 1 — Writer files (SK1 persona lines + recompile, SK3 model name)
- Comes in with the render checkout (`x3/render/AGENTS.md`, `writer_pipeline/writer_prompt.md`, `writer_pipeline/config.yaml`).
- Verify: `sha256sum /home/evo/AI/render/writer_pipeline/writer_prompt.md` = `5e7643b7c3cf016df572a81c3646ac73bab451b6cf49c42a2d66244d0855c572` and equals `writer_prompt_sha256` in `config.yaml`; recompile check with `python3 /home/evo/AI/community/scripts/parody/wp_compile_prompt.py` as `RUN_ME.md` says (77/77 PASS, 0 hard_fail); one dry writer ask (`render_writer_pipeline.py` dry run, no queue) reaches READY.

### Item 2 — Render pipeline speedups (RP1-RP3)
- Comes in with the community checkout.
- Check real ffmpeg supports the new flag: `ffmpeg -hide_banner -h full | grep -c fps_mode` > 0. If 0, stop (`BLOCKED`, RP3 needs ffmpeg 5.1+).
- Tests: `cd /home/evo/AI/community && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider scripts/parody/test_vision_read_cache.py scripts/tests/test_remote_comfy.py scripts/tests/test_last_frame_extract.py scripts/tests/test_run_queue_keep_comfy_process.py` (all pass).

### Item 3 — Skills (SK5 link/path fixes, FX1 `flux-klein-prompting`)
- Comes in with the community checkout (`skills/`).
- Hermes copy (no sudo, `evo:evo 0644`): `mkdir -p /home/evo/.hermes/skills/flux-klein-prompting && install -m 0644 /home/evo/AI/community/skills/flux-klein-prompting/SKILL.md /home/evo/.hermes/skills/flux-klein-prompting/SKILL.md`.
- Verify: `hermes skills list` shows `flux-klein-prompting` and `pi-job`; no broken relative links under `community/skills` (`grep -rn '](' ... ` spot check of 3 files).

### Item 4 — pi settings & YAML syntax-check (SK2 Forge skills, SK3 v2 subagent model, L7 YAML upgrade)
- `x3/forge/.pi/settings.json` comes in with the forge checkout. It is your own settings file: do not restart your own panes; it loads on the next pane start (Max restarts panes after your RESULT).
- `install -m 0644 /home/derekboone/evo-x3/config/pi-evo/settings.json /home/evo/.pi/agent/settings.json`.
- Update `syntax-check.ts` (adds `.yaml`/`.yml` validation): `install -m 0644 /home/derekboone/evo-x3/config/pi-evo/extensions/syntax-check.ts /home/evo/.pi/agent/extensions/syntax-check.ts`.
- Verify: both JSON settings parse (`python3 -m json.tool <file> >/dev/null`), `grep -c flash-next-uncensored-v2-sub` > 0 in each, and `grep -c 'yaml\.safe_load' /home/evo/.pi/agent/extensions/syntax-check.ts` > 0.
- Note for Max (not yours): live `/home/evo/.pi/.../panes/{forge,render}/settings.json` still name the v1 `-sub` model; Max fixes them on the box.

### Item 5 — ST6 raw-clip cleanup, install + dry run only
- `sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/evo-raw-clip-cleanup /usr/local/bin/evo-raw-clip-cleanup`
- Dry run (default; deletes nothing): `/usr/local/bin/evo-raw-clip-cleanup` -> prints `DRY_RUN candidates=<n> bytes=<b> list=/home/evo/AI/_runs/st6-raw-cleanup-<stamp>.txt`. Put the count, bytes and list path in RESULT.
- **Never run `--apply`.** Deleting raw clips needs Derrick's yes on that list in chat (they can't be recovered).

## Rollback
- Item 1-4: restore the Step 0 backups (or `git -C <checkout> reset --keep <recorded HEAD>`, no force push anywhere). Item 3: remove `/home/evo/.hermes/skills/flux-klein-prompting/`. Item 5: `sudo rm /usr/local/bin/evo-raw-clip-cleanup` (dry run changed nothing).

## Rules
- No renders, no `llama-swap.yaml` edits, no restarts except what an item says. Never read or print secrets (`models.json`, tokens, `.env`). Cite `mono` SHAs in RESULT.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-D/RESULT.md`, release the lease, then stop. List items 1-5 as `DONE`, `BLOCKED` or `SKIPPED` with the recorded HEADs, verify output, and the ST6 dry-run numbers.
