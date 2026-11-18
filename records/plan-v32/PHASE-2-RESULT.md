# Phase 2 result (plan v3.2) — 2026-11-18 CST

| Step | Status |
|---|---|
| P2.1 labels | Done on X3. herdr workspaces relabelled `Render-X3` (w3) / `Forge-X3` (w4). `herdr-panes.sh` (live + repo) has a LABEL map and renames restored workspaces. Launchers (`forge-pi.sh`, `render-pi.sh`, all copies) pass `--name` and `--append-system-prompt "You are <X>-X3 on evo-x3."`. One-shot checks: Forge answered "I'm Forge-X3 running on evo-x3."; Render answered "I'm Render-X3, running on host evo-x3." Forge pane w4:p1 restarted once (footer shows Forge-X3, 0.0%/131k). **w3:p1 (Render) NOT restarted** (open "A or B" chat): pi-mobile shows `Render-X3` after its next restart. AGENTS.md untouched. |
| P2.2 cleanup | Manifest `P2.2-CLEANUP-MANIFEST.md` + 16 small logs (`bakeoff/polystrata-logs/`) pushed to Gitea (87a3330, 188f2bc) BEFORE deleting. Deleted only manifest items. Disk: 593G -> 923G free (~330 GiB; heretic Q8 hardlinks freed 0). Kept intact: Huihui v2 GGUF@cbc7fba (105G + mmproj), flash-next*, gemma4-heretic Q8, qwen27b Q8+DFlash2, u34-final-...0733. Note: `du` target total was 373G incl. 26G hardlinked, so ~330 not the planned ~348. |
| P2.3 layout | `~/AI/_runs/` (+`ralph/`, `.gitignore`) created; `ralph.sh` default logDir -> `$HOME/AI/_runs/ralph` (lock stays in `ralph-community/logs`); PROMPT.md line 1 updated. U23 gap 11 verified already fixed: relative run_dir rejected by `render_writer_pipeline.py` and `fill_request.py` CLIs (rc 3, nothing created); suite 689 passed, 3 skipped, 6 xfailed. `_worktrees/` empty, no stale worktrees. `_archive/*.bak-*` kept until a verified QNAP backup. Ralph logging path not smoke-run (would touch the live fix_plan.md). |
| P2.4 Tailscale | Draft only: `P2.4-TAILSCALE-ACL-DRAFT.hujson` (tags tag:box/tag:nas, tests block). NOT applied. Derrick: download current policy first, merge, Preview/Save in admin console. Open question: also gate `evo-x3-1:8445` (PixlStash)? |

## For Max/Derrick (AlienPC, not touched)
- `C:\AI\director\scripts\pi_herdr_at_logon.ps1`: add Forge/Render/Sydney-AlienPC labels.
- `git config --system core.longpaths true`; apply U23 #11 patch `~/AI/_xfer/alienpc-patches/still-guard-rundir-20261115.patch`.
- Nightly tagger timer waits for P4.6.

## Uncommitted by me
`forge/ralph-community/PROMPT.md` and `render/x3/render-pi.sh` also hold other people's earlier uncommitted edits, so I did not commit them whole. My changes are in place on disk.
