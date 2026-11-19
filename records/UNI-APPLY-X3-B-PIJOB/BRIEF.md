Goal: Perform ONE install of `config/bin/pi-job` -> `/usr/local/bin/pi-job` on the EVO-X3 (H1c, H5, L1, L4, L5, L6, L8, ST3 trigger) under the X3 lease and run the exact live verification checks from the Opus delta apply order.

# UNI-APPLY-X3-B-PIJOB (X3 Forge): Single `pi-job` install and live verification on EVO-X3, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 + Forge execution) and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", item 4). Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required — do not launch until met)
1. **Derrick's live yes** for Card 13 (`H1c` X3-primary coding + AlienPc ESP-off overflow), Card 21 (`coding_swift15_iq3s` ESP-off alias), and live `/usr/local/bin/pi-job` install.
2. **Card 21 ESP-off alias `coding_swift15_iq3s` added on BOTH sides BEFORE installing `pi-job`:**
   - **X3 side:** `coding_swift15_iq3s` added to X3 pi `models.json` (Max / authorized config edit under X3 lease; never print secrets or keys from `models.json`).
   - **AlienPc side (prerequisite for AlienPc Forge):** `coding_swift15_iq3s` (ESP off) configured in AlienPc `llama-swap` under the AlienPc lease (requires Derrick's approval of `INV1b` Card 38 if AlienPc Forge edits `llama-swap`, or Max applies it). Keep AlienPc Forge's own default `coding_swift15_iq3s_esp` untouched per Card 21.
3. **`UNI-APPLY-X3-A` completed first** (specifically ST3 `import_inbox.py` with `flock` and L4 `OPERATOR.md` `--out <crun>/contact_sheet.jpg`).
4. **X3 lease taken** (`30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-x3-forge-uni-apply-x3-b-pijob.md`, mirrored to `records/status/`). Max writes/mirrors take and release files on brief issue/closeout unless X3 Forge is verified writable to the brain (Card 28 / M2).
5. **No active render during install**, and **not during the Hermes bakeoff window** (Plan C16). (Test 1 below observes a real AlienPc render — only run with Derrick's render yes or alongside an already-approved render.)
6. **Max import complete** from `mono` tip `5ccba67` (or newer) with clean `gitleaks`.

- **If `MONO-S5` already passed:** `/home/evo/AI/render` and `/home/evo/AI/community` are symlinks into the `mono` clone; skip the part-branch bridge and run `git -C /home/evo/AI/evo-x3 pull --ff-only` instead. Everything else in this brief is unchanged.

## Access & Lease
- **Doer:** X3 Forge (`/home/evo/AI/forge`, pi panes `w4:p1-p3`), running as `evo`. `sudo` is allowed **only** for installing/rolling back `/usr/local/bin/pi-job`.
- **Source on `mono`:** `config/bin/pi-job` in `/home/derekboone/evo-x3` (`mono` SHAs: `07369ec` H1c, `48e7358` L1, `febc22c` L4, `c8056a8` L5, `27999a6` L6, `952d165` L8, `658dc18` L8 fix, `03340b1` H1c fix, `a5a86ce` ST3 fix, `dbc7156` H5 fix, `f353e3e` L4 fix, `9b86a78` L6 fix, `db00dde` L1 fix; latest `pi-job` commit `db00dde`, `mono` tip `5ccba67`).
- **Backup root:** `/home/evo/AI/_archive/20261119/`.
- **Lease take:** `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-x3-forge-uni-apply-x3-b-pijob.md` (mirrored to `records/status/`).
- **Lease release:** `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-released-x3-forge-uni-apply-x3-b-pijob.md` (mirrored to `records/status/`).

## Work (ONE install — stop on first failure)

1. **Pre-install checks:**
   - Verify `coding_swift15_iq3s` alias is present on both X3 pi config (check model id presence without printing any secret/key) and AlienPc `:8446` / llama-swap. If missing on either side, **STOP** and report `BLOCKED`.
   - Verify `python3 -m py_compile /home/derekboone/evo-x3/config/bin/pi-job` exits 0.
   - Verify no active render or `pi-job` run is in progress.

2. **Backup and ONE install (Install table row):**
   - `mkdir -p /home/evo/AI/_archive/20261119`
   - Back up live file: `cp -a /usr/local/bin/pi-job /home/evo/AI/_archive/20261119/pi-job`
   - Install: `sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/pi-job /usr/local/bin/pi-job`
   - Verify `python3 -m py_compile /usr/local/bin/pi-job && /usr/local/bin/pi-job --help` exits 0.

3. **Re-snapshot:**
   - Run `scripts/snapshot-live-setup.sh` and `scripts/sync-config-copies.sh` so `hosts/x3/live/bin/pi-job` matches.

## Tests (exact live checks from delta apply order item 4)

1. **H1c — AlienPc busy gate check (review #5):**
   - With a real AlienPc render running (approved by Derrick), confirm `GET https://alienpc.tailf242b2.ts.net:8447/health` (or configured `PI_JOB_ALIENPC_GATE_URL`) returns **non-2xx** while the render is active.
   - If `:8447/health` returns HTTP 200 while a render is running, **STOP** and mark `BLOCKED`: `PI_JOB_ALIENPC_GATE_URL` must point to a lock-checking gate endpoint before H1c overflow is used.

2. **H1c — Gufo `/slots` exists and 0 swaps:**
   - With X3 Gufo (`flash-next-uncensored-v2`) loaded, confirm `/slots` responds via llama-swap `/running` -> `/upstream/.../slots` (no secret printed in logs) and that running a `pi-job code` smoke task while Gufo is resident completes with **0 llama-swap model swaps**.

3. **L8 — `pi-job recompile` on a non-`long_continuation` `READY` run:**
   - **HARD RULE (N1):** **Do NOT use `pi-job recompile` on any `long_continuation` run** until follow-up `N1` is fixed (`recompile` currently overwrites `c1.inputs.prompt` with `c0`'s prompt).
   - Pick a non-`long_continuation` `READY` run (or scratch copy), note its current P4.11 approval code, edit `prompt.txt` with a small valid change, and run `pi-job recompile <job_id>`.
   - Verify: (a) a new P4.11 code is issued matching the new `prompt.txt` SHA256, (b) the **old code fails** when checked/submitted, and (c) `clip/request.api.json` updated cleanly.

4. **Bundled feature smoke checks (`L5`, `L1`, `L4`, `L6`, `H5`, `ST3`):**
   - **L5:** Run `pi-job status` -> prints resident model, `MemAvailable`, AlienPc gate status, and last 3 jobs.
   - **L1:** Confirm the approval push `Actions` Copy text uses `pi-job queue <id> <code>` (check QNAP ntfy v2.35.0 if reachable).
   - **L4:** Confirm preview returns `sheet_url` only for the QNAP copy (and `none` when QNAP is unavailable or `contact_sheet.jpg` is absent), and `pi-job render --pick N` parses cleanly.
   - **H5 + L6:** In a throwaway `/tmp/pijob-h5-test` repo with a `Makefile` containing a failing `check-all:` target, run `pi-job code` -> verify non-zero `make check-all` marks `STUCK`, writes `~/AI/_runs/<id>/escalate.md` (with task, git diff, last 3 errors), and still fires the STUCK ntfy. Remove `/tmp/pijob-h5-test` after.
   - **ST3:** Confirm `pi-job render --still` invokes detached `systemd-run --user --unit=pixl-import --collect` (and skips when active).

## Rollback
- Restore backup: `sudo install -o root -g root -m 0755 /home/evo/AI/_archive/20261119/pi-job /usr/local/bin/pi-job`
- Verify `/usr/local/bin/pi-job --help` exits 0 and re-run `scripts/snapshot-live-setup.sh`.

## Rules
- **Don't use `pi-job recompile` on `long_continuation` runs until follow-up N1 is fixed.**
- No `llama-swap.yaml` edits. No reading or printing `models.json` keys, llama-swap keys, or ntfy tokens.
- No unauthorized renders. Stop on first failed check and record exact stdout/stderr (redacted of any secrets).
- Cite `mono` SHAs (`db00dde` / `5ccba67`) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-B-PIJOB/RESULT.md`, then stop. List Install and Tests 1-4 as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, backup path, `:8447/health` HTTP code during render, Gufo `/slots` + swap count, L8 old-code failure proof, and snapshot confirmation.
