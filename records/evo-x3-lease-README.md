---
pending_upload: true
title: EVO-X3 one-holder lease (N5) — format and release step
tags: [evo-x3, lease, n5]
---
# EVO-X3 one-holder lease (N5)

Source: Derrick's yes, Nov 15 2026 6:05 PM CT (Alfred card t498s2271), fixing Fleet Reviewer audit F2 (`60_reviews/home-lab/2026-11-15-evo-x3-build-audit.md` @ b62eb3f). Same convention as the AlienPc lease in `10_packs/max/max-briefing.md` (one-holder-for-the-alienpc-shell); this file only adds the X3 host name.

## Rule
- Only the holder named in the **newest** `30_handoff/status/*-evo-x3-lease-*.md` file runs Shell, installs, builds, model loads or benchmarks on the EVO-X3. A bot's subagents share its lease. Everyone else stays read-only or waits.
- The old Gitea `records/evo-x3-lease.md` (Antigravity Windows-prep, 12:13 PM) is superseded by the brain files below.
- No lease for one quick read-only command (status check, `df`, `systemctl status`). Installs, config edits, restarts, GPU/model work and tests take the lease.
- Don't commit lease files on their own; fold them into the next real commit (AlienPc rule, Derrick 2026-10-30 3:08 PM CT).

## Take file
Path: `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-<holder>-<job>.md`
```
---
type: lease-take
host: EVO-X3
holder: <bot name> (<bot id prefix>)
taken: YYYY-MM-DD HH:MM CT
---
# EVO-X3 lease taken: <holder>, <job> (<Derrick approval id>)
Scope: <what runs>. Not touched: <what stays off-limits>. Release when <condition>.
```

## Release file (required when the job ends or stops)
Path: `30_handoff/status/YYYY-MM-DD-HHMM-evo-x3-lease-released-<holder>-<job>.md`
```
---
type: lease-release
host: EVO-X3
holder: <bot name>
released: YYYY-MM-DD HH:MM CT
---
# EVO-X3 lease released: <holder>, <job>
State left: <services running, anything still loaded, open follow-ups>. Next holder: <name or "free">.
```
After writing it: commit with the job's real commit, run `~/.config/gitea-box/check-push.sh fleet-brain` (or the brain's push check), then tell Alfred so a waiting bot (e.g. Fleet Reviewer's read-only pass) can start.

## When it takes effect
Now for new work. Jobs already running on Nov 15 at 6:12 PM CT (Max Architect 3: Forge→Halogen + 262K test, on-track Phases 1–5, U5/U6 records, Gitea backup, Antigravity red-team unit `agy-x3-redteam-20261115`) are covered by Max Architect 3's lease and are not blocked. Max Architect 3 writes one release file when all of them finish.

## Update 2026-11-19

Superseded by Derrick's one-line lease rule (Derrick Nov 17, recorded by Max in `d80617f`):
- **X3 lease:** write ONE line `<who> | <what> | <start time>` to `/home/derekboone/AI/locks/x3-lease.txt` at start (stop if the file is not empty), and truncate it (`: > /home/derekboone/AI/locks/x3-lease.txt`) when done or blocked.
- **AlienPc lease:** ONE line `<who> | <what> | <start time>` per brain `10_packs/max/max-briefing.md` at start, cleared when done or blocked.
- **No status files:** no lease-taken/released files, no brain `30_handoff/status/` or `records/status/` mirrors, no git commit for the lease, and no message to Derrick.
