# UNI-APPLY-X3-B-PIJOB RESULT

When: 2026-11-19 16:36–16:38 America/Chicago (CST)
Doer: max-x3lane. Source: mono `5564e9df` (`pi-job` sha256 `c7858c1a4686e2698602075054599a7cd3670f85190eccc310a40d5efd6d9f97`). Did not fast-forward `/home/derekboone/evo-x3`. Did not read `models.json`. Did not restart Hermes. W1b left running. No `pi-job` process was running at install/verify. snapshot: pending Max. Rollback: not triggered.

## Pre-install — DONE (parent override on render-window gate)
- No `pi-job` / `queue-remote` / `run_queue` process.
- `python3 ast.parse` on source and live `/usr/local/bin/pi-job`: pass.
- Brief's required `:8447/health` non-2xx-during-approved-render gate and Swift routing tests were **not** used as an install blocker (parent: install if no `pi-job` process; skip tests that need Swift or a render window). Those tests are listed PENDING below.

## Install — DONE
- Backup root: `/home/evo/AI/_archive/20261119/x3b-pijob/`
  - `/home/evo/AI/_archive/20261119/x3b-pijob/pi-job.20261119-163603` (previous live, 29400 bytes, mtime 2026-11-19 08:14)
  - `/home/evo/AI/_archive/20261119/x3b-pijob/pi-job.SKILL.md.20261119-163603` (previous skill, 6229 bytes, mtime 2026-11-19 13:43)
- `sudo install -o root -g root -m 0755` -> `/usr/local/bin/pi-job` (16:36). Live sha256 `c7858c1a4686e2698602075054599a7cd3670f85190eccc310a40d5efd6d9f97` (matches repo).
- Hermes skill (no sudo, no gateway restart): `/home/evo/.hermes/skills/pi-job/SKILL.md` sha256 `8856ff22666474b9402435110de2b09d1685b3886011835ef742d7a7297fc66c` (matches repo).
- `/usr/local/bin/pi-job --help` exits 0 (subcommands: code, review, render, queue, upscale, status, approve, recompile, wait).

## Tests
- H1c idle / busy / `PI_JOB_FORCE_X3=1`: **PENDING** (needs Swift and/or an approved render window).
- L5 `pi-job status`: **PENDING** (not run during W1b so the writer benchmark is not disturbed).
- H5 + L6 `make check-all` STUCK / escalate.md: **PENDING** (needs a `pi-job code` / Swift run).
- L9 `pi-job wait` MEDIA: line: **PENDING** (render-window / finished-job live check skipped).
- Hermes -> pi coding hand-off (R11): **PENDING** (do not restart Hermes; not exercised).
- L1 / L4 / L8 / ST3 `pi-job render --still`: `SKIPPED - legacy pi-job render path, superseded by H9; code ships inside pi-job but is not live-tested or relied on`.
