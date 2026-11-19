Goal: Perform ONE install of `config/bin/pi-job` -> `/usr/local/bin/pi-job` on the EVO-X3 (coding/review path: H1c, H5, L5, L6; legacy render helpers L1/L4/L8/ST3 ship in the file but are SKIPPED per H9) under the X3 lease and run the H1c/H5/L5/L6 live checks.

# UNI-APPLY-X3-B-PIJOB (X3 Forge): Single `pi-job` install and coding-path live verification on EVO-X3, Nov 19 2026

Authority: Derrick 2026-11-19 11:11/11:16 CT (Card 2 + Forge execution), Derrick 2026-11-19 ~12:35 CT (Hermes is main chat interface, pi is coding-only -> C11 + H9; cards answered in chat), and `records/unified-implementation/PLAN.md` + `records/unified-implementation/CODE-REVIEW-20261119-opus-delta.md` ("Apply order for Max", item 4). Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required — do not launch until met)
1. **Derrick's live yes in chat:** Card 13 (`H1c`: AlienPc Swift `ESP off` when `:8447` idle and no `gpu-render.lock`, X3 Gufo when busy; render always wins, 503 -> resume on X3) and Card 21 (`coding_swift15_iq3s` ESP off everywhere — AlienPc Forge AND `pi-job`) are **ANSWERED YES** (Derrick 2026-11-19 12:29 CT, side chat); Card 1 live `/usr/local/bin/pi-job` install yes answered in chat (Max records id).
2. **Card 21 ESP-off alias `coding_swift15_iq3s` added on BOTH sides BEFORE installing `pi-job`** (see the Max-owned Prerequisite section below; Max confirms both aliases in the launch message — Forge never reads `models.json`).
3. **`UNI-APPLY-X3-A` completed first** (specifically ST3 `import_inbox.py` with `flock`).
4. **X3 lease free** (`/home/derekboone/AI/locks/x3-lease.txt` empty). The doer takes it at start (one line, see Access & Lease). No lease-taken/released files, no brain or `records/status/` mirrors, no git commit for the lease, no message to Derrick.
5. **Approved render window available for the Pre-install `:8447/health` busy check**, no active render during the install step itself, and **not during the Hermes bakeoff window** (Plan C16).
6. **Max import complete** from `mono` tip `3217c67 (or newer at Max import)` (includes `b96560f` H1c card-21 routing) with clean `gitleaks`.

- **If `MONO-S5` already passed:** `/home/evo/AI/render` and `/home/evo/AI/community` are symlinks into the `mono` clone; skip the part-branch bridge and run `git -C /home/evo/AI/evo-x3 pull --ff-only` instead. Everything else in this brief is unchanged.

## Max-owned Prerequisite: ESP-off alias `coding_swift15_iq3s` (complete before launching Forge)
- **AlienPc `llama-swap` (Max, or AlienPc Forge via X3/Max brief — Card 38 `INV1b` APPROVED, Derrick 2026-11-19 12:29 CT, side chat):**
  1. Take the AlienPc lease. Confirm idle: `Test-Path C:\AI\locks\gpu-render.lock` is `False` and `https://alienpc.tailf242b2.ts.net:8447/health` returns `200` (never edit during a render).
  2. Back up AlienPc llama-swap config to `C:\AI\_archive\20261119\llama-swap\`.
  3. Add/enable the exact ESP-off alias `coding_swift15_iq3s` (ESP off everywhere — both AlienPc Forge and `pi-job` use `coding_swift15_iq3s`, Card 21), then reload llama-swap.
  4. Verify `/v1/models` lists exact id `"coding_swift15_iq3s"` (exact-id match count = `1`, not substring match on `_esp`).
  5. Rollback: restore from `C:\AI\_archive\20261119\llama-swap\` and reload llama-swap. Release AlienPc lease.
- **X3 pi `models.json` (Max ONLY — secrets rule; Forge never reads `models.json`):**
  1. Under X3 lease, back up `/home/evo/.pi/agent/models.json` to `/home/evo/AI/_archive/20261119/models.json` (`0600`, never printed or committed).
  2. Add `alienpc/coding_swift15_iq3s` alias without printing any keys.
  3. Rollback: restore `/home/evo/AI/_archive/20261119/models.json` (`0600`).
- State in the Forge launch message that both aliases are verified live.

## Access & Lease
- **Doer:** X3 Forge (`/home/evo/AI/forge`, pi panes `w4:p1-p3`), running as `evo`. `sudo` is allowed **only** for installing/rolling back `/usr/local/bin/pi-job`.
- **Source on `mono`:** `config/bin/pi-job` in `/home/derekboone/evo-x3` (`mono` SHAs: `07369ec` H1c, `48e7358` L1, `febc22c` L4, `c8056a8` L5, `27999a6` L6, `952d165` L8, `658dc18` L8 fix, `03340b1` H1c fix, `a5a86ce` ST3 fix, `dbc7156` H5 fix, `f353e3e` L4 fix, `9b86a78` L6 fix, `db00dde` L1 fix, **`b96560f` H1c card 21**; latest `pi-job` commit `b96560f`, `mono` tip `3217c67 (or newer at Max import)`).
- **Backup root:** `/home/evo/AI/_archive/20261119/`.
- **Lease take:** write ONE line to `/home/derekboone/AI/locks/x3-lease.txt`: `x3-forge | UNI-APPLY-X3-B-PIJOB | <start time>`. If the file is not empty, stop.
- **Lease release:** truncate `/home/derekboone/AI/locks/x3-lease.txt` (`: > /home/derekboone/AI/locks/x3-lease.txt`) when done or blocked. No status files, mirrors, commits, or messages for the lease.

## Work (ONE install — stop on first failure)

1. **Pre-install checks (MUST pass before touching `/usr/local/bin/pi-job`):**
   - **Aliases:** Confirm Max's launch message states both `coding_swift15_iq3s` aliases are in place (**do NOT read `models.json`**). Optionally check AlienPc `/v1/models` JSON for exact `"id": "coding_swift15_iq3s"` and print **only** the exact-id match count (`1`).
   - **H1c AlienPc busy gate check (review #5 — BEFORE install):** During an approved AlienPc render, run:
     ```bash
     curl -s -o /dev/null -w '%{http_code}\n' https://alienpc.tailf242b2.ts.net:8447/health
     ```
     Proceed with install **only if non-2xx** while the render is active. If no approved render is available to test this, OR if `:8447/health` returns `200` during a render, **STOP** and report `BLOCKED` (**do NOT install `pi-job`**).
   - **No-write syntax check:**
     ```bash
     python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' /home/derekboone/evo-x3/config/bin/pi-job
     ```
   - Wait until the approved render finishes and verify no active render or `pi-job` run is in progress before installing.

2. **Backup and ONE install (Install table row):**
   - `mkdir -p /home/evo/AI/_archive/20261119`
   - Back up live file: `cp -a /usr/local/bin/pi-job /home/evo/AI/_archive/20261119/pi-job`
   - Install: `sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/pi-job /usr/local/bin/pi-job`
   - Verify (no-write AST parse + CLI help):
     ```bash
     python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' /usr/local/bin/pi-job
     /usr/local/bin/pi-job --help
     ```

3. **Re-snapshot:** **Max closeout step** — Forge does **not** run `snapshot-live-setup.sh` or `sync-config-copies.sh`; write `snapshot: pending Max` in `RESULT.md`.

## Tests (coding/review path only; **if ANY post-install test fails, run Rollback immediately**)

1. **H1c — AlienPc idle vs render-busy routing + `PI_JOB_FORCE_X3=1` (Card 13 & Card 21, `b96560f`):**
   - **Idle path:** With AlienPc idle (`:8447/health` returns `200`, no `gpu-render.lock`), run a `pi-job code` smoke task -> verify job log shows route `alienpc` with `coding_swift15_iq3s` (ESP off) and **0 X3 llama-swap swaps**.
   - **Busy / render-wins path:** With an approved AlienPc render running (`:8447/health` returns non-2xx), run a `pi-job code` smoke task -> verify job log shows route `x3` and **0 X3 llama-swap swaps** (503 during a run also resumes on `x3`). X3 Gufo remains the writer/Hermes model.
   - **Forced-X3 check:** Run `PI_JOB_FORCE_X3=1 /usr/local/bin/pi-job code ...` -> verify job log shows route `x3` and **0 X3 llama-swap swaps**.

2. **L5 — `pi-job status`:**
   - Run `/usr/local/bin/pi-job status` -> prints resident model, `MemAvailable`, AlienPc gate status, and last 3 jobs.

3. **H5 + L6 — `make check-all` failure -> `STUCK` + `escalate.md`:**
   - In a throwaway `/tmp/pijob-h5-test` git repo with a `Makefile` containing `check-all: ; @false`, run `pi-job code` with prompt `"do not edit any file; reply done"` -> verify non-zero `make check-all` marks `STUCK`, writes `~/AI/_runs/<id>/escalate.md` (with task, git diff, last 3 errors), and still fires the STUCK ntfy. Remove `/tmp/pijob-h5-test` after.

4. **Legacy `pi-job` render items (`L1`, `L4`, `L8`, `ST3` `pi-job render --still` trigger) — DO NOT live-test:**
   - Mark all four in `RESULT.md` as: `SKIPPED - legacy pi-job render path, superseded by H9; code ships inside pi-job but is not live-tested or relied on` (Derrick 2026-11-19 ~12:35 CT: Hermes is main chat interface; pi is for coding only).
   - Do **not** run `pi-job recompile`, `pi-job queue`, `pi-job render --pick`, or `pi-job render --still`.

## Rollback (mandatory if ANY post-install test fails)
- Restore backup: `sudo install -o root -g root -m 0755 /home/evo/AI/_archive/20261119/pi-job /usr/local/bin/pi-job`
- Verify `/usr/local/bin/pi-job --help` exits 0 and record `snapshot: pending Max` in `RESULT.md`.

## Closeout (Max only, after `RESULT.md`)
- As `derekboone` in `/home/derekboone/evo-x3`: run `scripts/snapshot-live-setup.sh` and `scripts/sync-config-copies.sh`, run `gitleaks`, and commit snapshot updates by explicit path.

## Rules
- **Do not run `pi-job recompile`, `pi-job queue`, `pi-job render --pick`, or `pi-job render --still`** (legacy render path superseded by H9; also never use `recompile` on `long_continuation` until N1 is fixed).
- No `llama-swap.yaml` edits by Forge. Never read or print `models.json`, llama-swap keys, or ntfy tokens.
- No unauthorized renders. Stop on first failed check, run Rollback if `pi-job` was already installed, and record exact stdout/stderr (redacted of any secrets).
- Cite `mono` SHAs (`b96560f` / `3217c67 (or newer at Max import)`) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-B-PIJOB/RESULT.md`, then stop. List Pre-install (incl. `:8447/health` HTTP code during approved render), Install, Tests 1-3 (`H1c` idle/busy/`PI_JOB_FORCE_X3=1`, `L5`, `H5+L6`), and `L1`/`L4`/`L8`/`ST3 render trigger` (`SKIPPED - legacy pi-job render path, superseded by H9; code ships inside pi-job but is not live-tested or relied on`) with `mono` SHAs, backup path, route logs + swap count, rollback status if triggered, and `snapshot: pending Max`.
