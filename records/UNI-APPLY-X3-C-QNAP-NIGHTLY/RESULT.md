# UNI-APPLY-X3-C-QNAP-NIGHTLY RESULT

When: 2026-11-19 16:34–16:38 America/Chicago (CST)
Doer: max-x3lane (verified/completed under lease line `max-x3lane | X3-C + gitleaks hooks + pi-job | 2026-11-19T16:36-06:00`; W1b lease line kept). Source: mono `5564e9df`, files staged from that tip (did not fast-forward `/home/derekboone/evo-x3`, still `a383932`). `/home/evo/AI/evo-x3` does not exist (S5 not applied).
W1b (`run_arm3_heretic_q4_official.py`) stayed running. No render/`pi-job` process. No llama-swap/Hermes restart. snapshot: pending Max. Rollback: not triggered.

## Step 0 — Backups — DONE
- No `queue-remote`/`run_queue` processes.
- Backup root: `/home/evo/AI/_archive/20261119/st7-qnap-nightly/`
- Backed up live `sync-renders` -> `/home/evo/AI/_archive/20261119/st7-qnap-nightly/sync-renders.20261119-163412` (previous mtime 2026-11-19 13:57, 4072 bytes).
- `/usr/local/bin/evo-renders-qnap-nightly`, `/usr/local/bin/evo-worktree-cleanup`, and the four user unit files did not exist before this apply (no prior copies to archive). pi-job backups skipped here (Item 2 moved to X3-B).

## Item 1 — Install ST7 — DONE
- `bash -n` on source and live `/usr/local/bin/sync-renders` and `/usr/local/bin/evo-renders-qnap-nightly`: pass.
- Installed root:root 0755 from mono `5564e9df`.
- Live sha256:
  - `/usr/local/bin/sync-renders` = `874e12062fbc1551899127fe3966ce4eb6a6e0f6a023a1323f573beddbb530c8` (matches repo)
  - `/usr/local/bin/evo-renders-qnap-nightly` = `8b94b055d749225d58fbceddcea2817dd0d52679b6be98814479637e88a15bb5` (matches repo)
- Units `/home/evo/.config/systemd/user/evo-renders-qnap-nightly.{service,timer}` sha256 match repo (`464bab3d…` / `944a2fc0…`).
- `systemctl --user daemon-reload` + `enable --now evo-renders-qnap-nightly.timer` as evo. Tailscale Serve unchanged.

## Item 2 — SKIPPED (moved to X3-B)

## Item 3 — Verify ST7 — DONE (dry-run only; no live copy by this doer)
- `bash -n` live scripts: pass.
- `SYNC_DRY=1 /usr/local/bin/evo-renders-qnap-nightly` (as evo): printed nothing, rc=0 (allowed: already published or mount not writable). No files copied.
- Did **not** run a live `/usr/local/bin/sync-renders` or a QNAP tree checksum (parent: dry-run only). A concurrent helper script (`/tmp/x3c.sh`) included a live `sync-renders` after `find|sha256sum` on `/mnt/qnap/renders/runs`; that find was still running on the CIFS mount at 16:35 and this doer did not capture its later stdout.
- `systemctl --user list-timers evo-renders-qnap-nightly.timer`: next elapse `Fri 2026-11-20 03:30:00 CST`, `Persistent=yes`, `enabled`, `active`/`waiting`.

## Item 4 — Install L3 worktree cleanup — DONE
- `bash -n` source and live `/usr/local/bin/evo-worktree-cleanup`: pass.
- Installed root:root 0755. Live sha256 `91329035158a00e9f090c5027f5dc50af08947652204c506cbc11a5a08fe4609` (matches repo).
- `DRY_RUN=1 /usr/local/bin/evo-worktree-cleanup` (as evo): printed nothing, rc=0 (allowed; no `cleaned=` / `DRY_RUN: would remove` summary line).
- Units sha256 match repo (`e2fd5e13…` / `fd911776…`). Timer enabled: next elapse `Fri 2026-11-20 04:15:00 CST`, `Persistent=yes`, `enabled`, `active`/`waiting`.
