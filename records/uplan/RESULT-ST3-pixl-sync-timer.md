# RESULT: PixlStash sync timer (ST3 / evo-renders-sync)

When: 2026-11-19 18:19–18:23 America/Chicago (CST)
Doer: Max Architect (box), ssh `evo-x3-1` as `derekboone`; evo files via `cd /tmp; sudo -n -u evo …`. Approval: Derrick t2939u (yes to the PixlStash sync timer item).
Lease: appended `Max Architect | PixlStash sync timer evo-renders-sync ST3 | 2026-11-19T18:19:41-06:00` to `/home/derekboone/AI/locks/x3-lease.txt` (append only); removed that line only when done. W1b `max-helper` lines were left in place. W1b Q5-fast tmux session was left running. No `llama-swap.yaml` edit. Windows partitions and USB not touched. PixlStash library contents, captions, names and tags were not viewed (counts only). PixlStash journal was not read.

## What was already live
- `/usr/local/bin/sync-renders` sha256 `874e12062fbc1551899127fe3966ce4eb6a6e0f6a023a1323f573beddbb530c8` (matches `mono` `config/bin/sync-renders`, includes still auto-import to `/home/evo/AI/pixl-inbox`).
- `/home/evo/AI/pixlstash-tagging/import_inbox.py` sha256 `2b8726630a4c75e71a4173b96921f13c7c9f8aceb4dde3ba11f4b83ce4c1d497` (matches `mono`).
- `/home/evo/.config/systemd/user/evo-renders-sync.service` sha256 `6c97706f00af230c1cd04833388186a93164e6b29b8d73fd79d1c34dcb274838`
- `/home/evo/.config/systemd/user/evo-renders-sync.timer` sha256 `4b47938b0767a6cd31ac808da6780dd28fc5ade48c14046d753f86531c790bae`
- Schedule (stock unit text, unchanged): `OnBootSec=1min`, `OnUnitActiveSec=2min`, `Persistent=true`, `WantedBy=timers.target`. Service `Type=oneshot` `ExecStart=/usr/local/bin/sync-renders`. Inbox import is started detached as `systemd-run --user --unit=pixl-import --collect`.

## Backup
`/home/evo/AI/_archive/20261119/pixl-sync-timer-20261119-181941/` (`sync-renders`, `import_inbox.py`, `systemd-user/evo-renders-sync.{service,timer}`). Hashes match the live files (no content change).

## Re-arm (stock systemd)
The evo user manager started 15:38:50 CST. The timer was `enabled` / `active` but `SubState=elapsed`, `NextElapseUSecMonotonic=infinity`, last trigger 15:24:15 CST: `OnBootSec` had already passed for this boot, and `OnUnitActiveSec` had no service activation in that manager lifetime.

Ran as evo (machine bus): `systemctl --user -M evo@ daemon-reload && enable evo-renders-sync.timer && start evo-renders-sync.timer`, then one `start --wait evo-renders-sync.service`.

## First run (manual, to arm OnUnitActiveSec)
- Start 2026-11-19 18:19:42 CST, exit 2026-11-19 18:19:52 CST
- `start --wait` rc=0, elapsed 10.457 s, `Result=success`, `ExecMainStatus=0`
- After the run: `pending_images` 5, `pixl-import.service` active; a concurrent `import_inbox.py` print (counts only, token read from the locked X3 key file, never printed or put on a command line) was `{"files": 0, "batches": 0, "imported": 0, "duplicate": 0, "failed": 0, "timed_out": 0, "remaining": 0, "elapsed_s": 0.0, "stopped_reason": "locked"}`
- After `pixl-import` finished (transient unit collected, `LoadState=not-found`): `pending_images` 0, `_imported` count 806→811, `_failed` 0

## Timer-fired run
- `evo-renders-sync.timer` listed, enabled, `SubState=waiting`, next 18:21:42 CST
- Fired 18:21:46 CST (within `AccuracySec=1min`), service 18:21:46–18:21:47 CST, `Result=success`, `ExecMainStatus=0`
- Re-armed: next 18:23:46 CST (2 min). Enabled, active, waiting, listed.

## Snapshots
- X3: `scripts/snapshot-live-setup.sh` (`SNAPSHOT_OUT=/tmp/x3-live-snap-20261119`, 127 files) + `scripts/sync-config-copies.sh` to `/tmp/x3-config-snap` (28 files, sudo reads). Secret-like scan clean. `config/` copies were unchanged vs `mono`. Live tree refresh: only `hosts/x3/live/hermes/memories-listing.txt` content change (parent-dir mtime). Preserved files the script does not emit: `hosts/x3/live/README.md`, `hermes-webui/install.txt`, `containers/_archive/`.
- AlienPc (read-only, machine `ecc21911-e61e-44fb-80b1-4bbe46bc56bd`): `custom-nodes.tsv` (`ComfyUI-KJNodes` now enabled), `pip-freeze.txt` / `comfy.settings.json` / `extra_model_paths.yaml` unchanged, `community-HEAD.txt` still `8eec1d3d`, inventory re-read (RefMod counts unchanged; archived bulge LoRA no longer in `loras\MinimaxH3`). Redacted llama-swap copy updated: live ComfyUI cmd no longer includes `--fast fp16_accumulation` (live file was not edited). Proposed AGT1 agent copies were not overwritten.

## Rollback
Restore the four files from `/home/evo/AI/_archive/20261119/pixl-sync-timer-20261119-181941/` and `systemctl --user -M evo@ daemon-reload`. To stop the timer: `systemctl --user -M evo@ disable --now evo-renders-sync.timer`.
