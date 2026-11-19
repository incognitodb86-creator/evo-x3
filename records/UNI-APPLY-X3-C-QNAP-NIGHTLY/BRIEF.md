Goal: After `UNI-APPLY-X3-A` has a `RESULT.md`, install unified-plan item `ST7` on the EVO-X3 (move X3 render QNAP publish out of the 2-minute `sync-renders` and onto a nightly 03:30 timer) under the X3 lease.

# UNI-APPLY-X3-C-QNAP-NIGHTLY (X3 Forge): Install ST7 QNAP nightly copy on EVO-X3, Nov 19 2026

Authority: Derrick 2026-11-19 t2716u (QNAP copy of finished renders moves to a nightly backup; Hermes and PixlStash already show clips; supersedes t2555 for X3-queued runs) and `records/unified-implementation/PLAN.md` item `ST7`. Max verifies your `RESULT.md` afterwards. This brief is file-only until applied; do not start until `UNI-APPLY-X3-A/RESULT.md` exists.

## Needs before launch (ALL required — do not launch until met)
- **`UNI-APPLY-X3-A` `RESULT.md` is present** at `/home/derekboone/evo-x3/records/UNI-APPLY-X3-A/RESULT.md`. If it is missing, stop (`BLOCKED`) and do not take the lease.
- **X3 lease free** (`/home/derekboone/AI/locks/x3-lease.txt` empty). The doer takes it at start (one line, see Access & Lease). No lease-taken/released files, no brain or `records/status/` mirrors, no git commit for the lease, no message to Derrick.
- **No active render**, and **not during the Hermes bakeoff window** (Plan C16).
- **Max import complete** from the `ST7` `mono` tip (or newer). Root-copy files are read from `/home/derekboone/evo-x3`. **ONE BRANCH:** push only `mono` (Derrick ~13:05 CT).

- **If `MONO-S5` already passed:** `/home/evo/AI/render` and `/home/evo/AI/community` are symlinks into the `mono` clone; run `git -C /home/evo/AI/evo-x3 pull --ff-only` instead of any part-branch pull. Everything else in this brief is unchanged.

## Access & Lease
- **Doer:** X3 Forge (`/home/evo/AI/forge`, pi panes `w4:p1-p3`), running as `evo`. Use `sudo` only to install or roll back files under `/usr/local/bin`.
- **Source on `mono`:** `/home/derekboone/evo-x3` (`config/bin/sync-renders`, `config/bin/evo-renders-qnap-nightly`, `hosts/x3/systemd/user/evo-renders-qnap-nightly.{service,timer}`).
- **Backup root:** `/home/evo/AI/_archive/20261119/st7-qnap-nightly/` (do not overwrite `UNI-APPLY-X3-A` backups in `/home/evo/AI/_archive/20261119/`).
- **Lease take:** write ONE line to `/home/derekboone/AI/locks/x3-lease.txt`: `forge-x3 | UNI-APPLY-X3-C-QNAP-NIGHTLY | <start time>`. If the file is not empty, stop.
- **Lease release:** truncate `/home/derekboone/AI/locks/x3-lease.txt` (`: > /home/derekboone/AI/locks/x3-lease.txt`) when done or blocked. No status files, mirrors, commits, or messages for the lease.

## Work (stop on first failure)

### Step 0 — No render running, then backups
- Confirm no render is running: `ps aux | grep -E 'queue-remote|run_queue' | grep -v grep` (must be empty). If it is not empty, stop (`BLOCKED`) and release the lease.
- `mkdir -p /home/evo/AI/_archive/20261119/st7-qnap-nightly`
- Back up live files if they exist:
  - `cp -a /usr/local/bin/sync-renders /home/evo/AI/_archive/20261119/st7-qnap-nightly/sync-renders`
  - if `/usr/local/bin/evo-renders-qnap-nightly` exists: `cp -a` it into the same backup dir
  - if the unit files exist under `/home/evo/.config/systemd/user/`: `cp -a` `evo-renders-qnap-nightly.service` and `evo-renders-qnap-nightly.timer` into the backup dir

### Item 1 — Install `ST7`
- No-write syntax check first:
  ```bash
  bash -n /home/derekboone/evo-x3/config/bin/sync-renders
  bash -n /home/derekboone/evo-x3/config/bin/evo-renders-qnap-nightly
  ```
- Install scripts (sudo yes, `root:root 0755`):
  ```bash
  sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/sync-renders /usr/local/bin/sync-renders
  sudo install -o root -g root -m 0755 /home/derekboone/evo-x3/config/bin/evo-renders-qnap-nightly /usr/local/bin/evo-renders-qnap-nightly
  ```
- Install units (no sudo, `evo:evo 0644`) and enable the timer:
  ```bash
  install -m 0644 /home/derekboone/evo-x3/hosts/x3/systemd/user/evo-renders-qnap-nightly.service /home/evo/.config/systemd/user/evo-renders-qnap-nightly.service
  install -m 0644 /home/derekboone/evo-x3/hosts/x3/systemd/user/evo-renders-qnap-nightly.timer /home/evo/.config/systemd/user/evo-renders-qnap-nightly.timer
  systemctl --user daemon-reload
  systemctl --user enable --now evo-renders-qnap-nightly.timer
  ```
- Do **not** change Tailscale Serve. `/renders/` on 8443 stays pointed at `/mnt/qnap/renders/runs` until Derrick yeses a separate card.

### Item 2 — Verify
  ```bash
  bash -n /usr/local/bin/sync-renders
  bash -n /usr/local/bin/evo-renders-qnap-nightly
  SYNC_DRY=1 /usr/local/bin/evo-renders-qnap-nightly
  ```
- The dry run must only list (`WOULD PUBLISH …`) or print nothing (already published, or mount not writable). It must not copy files.
- Record a checksum of the QNAP runs tree, run one live `sync-renders` (no active render), and confirm the tree is unchanged:
  ```bash
  before=$(find /mnt/qnap/renders/runs -type f -printf '%p %s %T@\n' 2>/dev/null | sort | sha256sum)
  /usr/local/bin/sync-renders
  after=$(find /mnt/qnap/renders/runs -type f -printf '%p %s %T@\n' 2>/dev/null | sort | sha256sum)
  # before and after must be identical; this pass must not write to /mnt/qnap/renders/runs
  ```
- `systemctl --user list-timers evo-renders-qnap-nightly.timer` must show the timer, next elapse around 03:30 local, `Persistent=true`.
- Re-snapshot: **Max closeout step** (record `snapshot: pending Max` in `RESULT.md`).

### Rollback
- Restore `/home/evo/AI/_archive/20261119/st7-qnap-nightly/sync-renders` with `sudo install -o root -g root -m 0755`.
- `systemctl --user disable --now evo-renders-qnap-nightly.timer`, remove the two unit files (or restore backups), `systemctl --user daemon-reload`.
- If the new script was installed: `sudo rm -f /usr/local/bin/evo-renders-qnap-nightly` (or restore the backup if one existed).

## Closeout (Max only, after `RESULT.md`)
- As `derekboone` in `/home/derekboone/evo-x3`: run `scripts/snapshot-live-setup.sh` and `scripts/sync-config-copies.sh`, run `gitleaks`, and commit snapshot updates by explicit path. (Forge never runs these scripts as `evo`.)

## Rules
- **Stop on first failure.** Do not skip a failed install or verify step.
- No `llama-swap.yaml` edits. No service restarts beyond `systemctl --user daemon-reload` and enabling the nightly timer. Do not restart or trigger `evo-renders-sync.timer` except for the one `sync-renders` verify run above.
- No renders. Nothing runs during an active render. No apply during the Hermes bakeoff window (C16).
- Never read, print, or copy secrets. Never view PixlStash library contents. Do not change Tailscale Serve.
- Cite `mono` SHAs (never worker branch SHAs) in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-C-QNAP-NIGHTLY/RESULT.md`, then release the lease and stop. List Step 0, Item 1, and Item 2 as `DONE`, `BLOCKED`, or `SKIPPED` with `mono` SHAs, backup paths, exact verify commands + pass/fail outputs, `snapshot: pending Max`, and rollback status if triggered.
