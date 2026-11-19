---
title: "evo-x3 monorepo consolidation: one main branch for X3 + AlienPc setup"
date: 2026-11-19
type: plan
artifact_contract: ce-unified-plan/v1
product_contract_source: derrick-chat (t2620u, t2621u)
execution: code
tier: T2 Durable (plan file asked for; >1 device; repo restructure)
author: Max Architect (executor subagent). PLAN ONLY, nothing restructured, moved or merged
review: outside AI (Opus) reviews this file before any step runs
pending_upload: true
---

# evo-x3 monorepo consolidation

Related: ../hermes-direct-render/PLAN.md · **single plan for review: [../unified-implementation/PLAN.md](../unified-implementation/PLAN.md)** (live audit 2026-11-19 10:42-10:55 AM CT; Wave 5 = this plan)

PLAN ONLY. No branch was merged, no folder moved, no live checkout touched. Facts below were read live (read-only) on 2026-11-19 ~10:00-10:10 AM CT. Labels: VERIFIED (read live), ASSUMPTION (to test in the step that uses it).

## Goal Capsule

| Field | Value |
|---|---|
| Objective | One repo, one main branch, one folder per part, full history kept, for the whole X3 + AlienPc setup (Derrick t2620u/t2621u). |
| Means | `git filter-repo --to-subdirectory-filter` per part branch, merged with `--allow-unrelated-histories` into a NEW branch `mono` on Gitea `derrick/evo-x3`; live checkouts switch by clone + symlink (X3) / junction (AlienPc) so no running path changes. |
| Authority | Derrick t2620u/t2621u (plan); every step below needs his yes after Opus review. |
| Out of scope | General scattered-files / QNAP cleanup (Derrick defers it to Opus). Moving or deleting runtime data (runs, models, PixlStash, outputs). Any change to llama-swap.yaml, ComfyUI, Hermes config. |
| Stop conditions | Tree-hash check (S3) fails; gitleaks finds a live secret in history; any render, Forge or Hermes job active at switchover; any smoke test in S5/S6 fails → roll back that machine. |

## Summary

Today each part lives on its own branch of `derrick/evo-x3`, and AlienPc pushes to two separate Gitea repos. The plan builds a new `mono` branch where `u58` (host config, hosts/, records/, scripts/) stays at the root and each other part moves under a folder, keeping every commit. Live checkouts then become symlinks/junctions into one clone, so `/home/evo/AI/render`, `/home/evo/AI/community`, `/home/evo/AI/forge`, `C:\AI\render` and `C:\AI\community` keep working at the same paths. With that method 0 hardcoded paths must change; repointing instead would touch 63 files (list in Appendix). Old part branches stay untouched (no force push) as rollback and get archive tags later on Derrick's yes.

Community way: git-filter-repo docs, example "git filter-repo --to-subdirectory-filter my-module/" (newren/git-filter-repo Documentation, accessed 2026-11-19) and git-subtree docs (git/git contrib/subtree, "add <repository> <remote-ref>", `--squash` imports one commit) → adapt: filter-repo + unrelated-histories merge keeps per-file history under the new path (subtree add keeps commits but pre-merge history does not show under the prefix path); `git sparse-checkout` cone mode (git-scm docs) used on AlienPc only to skip X3 folders.

---

## Product Contract

### Current layout (VERIFIED)

Gitea `derrick/evo-x3` branches (commits / tracked files / last commit):

| Branch | What | Commits | Files | Live checkout tracking it |
|---|---|---|---|---|
| `x3-render` | Render: OPERATOR.md, AGENTS.md, writer_pipeline, x3/render-pi.sh, queue-remote.sh, .pi | 53 | 33 | `/home/evo/AI/render` (local branch `x3-linux`, upstream `gitea/x3-render`) |
| `x3-community` (= `x3-linux`, same SHA 6bdcc49c) | community: scripts (render_writer_pipeline, run_queue, remote_upscale), skills, templates | 685 | 3,518 | `/home/evo/AI/community` (local `x3-linux`, upstream `gitea/x3-community`) |
| `u58` | X3 host: config/, hosts/x3, hosts/alienpc, scripts/ (pi-job, sync-renders, snapshot), records/ | 48 | 1,053 | `/home/derekboone/evo-x3` (upstream `gitea/u58`) |
| `u58-chat-read-plan` | Forge (ralph-community, loop-guard, records) | 14 | 22 | `/home/evo/AI/forge` |
| `alienpc-render` (5c3450d) | copy of AlienPc `C:\AI\render` | 34 | 20 | AlienPc `C:\AI\render` pushes to separate Gitea repo `derrick/alienpc-render` (master) |
| `alienpc-community` (6dadffc) | copy of AlienPc `C:\AI\community` | 636 | 3,486 | AlienPc `C:\AI\community` pushes to `derrick/alienpc-community-pc` (master) |
| `evo-x3-all` | flat snapshot, one folder per part (no history) | 24 | 11,328 | none |
| also | `main` (9, 2026-11-15), `x3-forge` (9), `x3-pi-config` (19), `x3-bakeoffs` (1), `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup` | | | none |

Not a git checkout but part of the setup (added after the 2026-11-19 live audit): AlienPc Forge `C:\Users\derek\forge` is a junction to `C:\Users\derek\5slock` (pi working root, ralph loop, x3run/x3put), and the AlienPc global pi folder `C:\Users\derek\.pi\agent\` (AGENTS.md, settings, permissions, extensions, skill links). Their instruction/config files are tracked as read-only copies under `u58` `hosts/alienpc/live/`; runtime data there (runs, sessions, libraries) stays out. Decide in S2 whether `5slock` gets its own folder in `mono` (default: keep the `hosts/alienpc/live/` copy).

Notes: `x3-community` and `alienpc-community` share history (merge-base c85afa00); `x3-render` and `alienpc-render` too (7c219cce). AlienPc `C:\AI\community` has 131 uncommitted changes and `C:\AI\render` 9. GitHub `incognitodb86-creator/evo-x3` mirrors these branches, pushed from the box clone `/workspace/evo-x3-u57`.

### Requirements

- R1. One repo (`derrick/evo-x3`), one main branch, one folder per part, full history kept. Pass: for each part, `git rev-parse mono:<prefix>` equals the tree hash of the part branch tip it was built from; `git log -- <prefix>/<file>` shows pre-merge commits. Gate: Max, then Opus review.
- R2. Live Render, Forge, Hermes, `evo-renders-sync` timer, render-pi.sh and queue-remote.sh keep working through and after switchover. Pass: S5 smoke list all green. Gate: Max under X3 lease.
- R3. AlienPc ComfyUI and its launchers keep working. Pass: S6 smoke list green. Gate: Max under AlienPc lease.
- R4. No secrets in the new branch or its history; ignore rules cover `.env`, `*.token`, `*.cred`, `auth.json`, `mcp.json`, `models.json`; snapshot script never copies mcp.json or Authorization headers. Pass: `gitleaks detect` over full `mono` history clean (or every hit triaged as rotated/false positive by Derrick); `git ls-files` shows no ignored-name files. Gate: Max + Derrick for any hit.
- R5. Gitea is primary; GitHub is a mirror pushed from the box via gh. Pass: Gitea `mono` tip == GitHub `mono` tip; no credentials added on X3 or AlienPc. Gate: Max.
- R6. Rollback to today's layout in minutes per machine. Pass: rollback rehearsed on paper; old dirs kept as `*.pre-mono` until Derrick's yes.
- R7. No force push, no history rewrite of existing branches, explicit `git add` paths only.

### Proposed layout (branch `mono`)

```text
/                     <- u58 as is: README.md, config/, hosts/x3/, hosts/alienpc/, scripts/, records/, bench/, ...
x3/render/            <- x3-render        (live: /home/evo/AI/render -> symlink)
x3/community/         <- x3-community     (live: /home/evo/AI/community -> symlink)
x3/forge/             <- u58-chat-read-plan (live: /home/evo/AI/forge -> symlink)
alienpc/render/       <- alienpc-render   (live: C:\AI\render -> junction)
alienpc/community/    <- alienpc-community (live: C:\AI\community -> junction)
records/              <- stays at root (Hermes plan, this plan, all U-records)
```

u58 stays at the root rather than under `x3/host/` because its scripts write repo-relative paths (`hosts/x3/live`, `config/bin`); moving it is card Q3. Each imported part keeps its own `.gitignore` inside its folder (nested ignores apply).

---

## Planning Contract

### Key Technical Decisions

- KTD1. Merge method: `git filter-repo --to-subdirectory-filter <prefix>/` on a throwaway clone of each part branch, then `git merge --allow-unrelated-histories` into `mono` (started from u58). Rejected: `git subtree add` (keeps commits, but history before the merge is not under the prefix path, so `git log -- x3/render/...` loses it); `--squash` (drops history, against R1); flat copy like `evo-x3-all` (no history).
- KTD2. New branch `mono`, nothing rewritten. Imported commits get new SHAs inside `mono` only; the original branches and their SHAs stay on Gitea and GitHub. Making `mono` the default branch and archiving old ones is card Q1.
- KTD3. Live switchover by clone + link, not by repointing: one clone per machine, old dirs renamed `*.pre-mono`, then `ln -s` (X3) / `mklink /J` directory junction (AlienPc, no admin or developer mode needed). Untracked runtime data inside old checkouts (`community/runs/`, `render/x3/.venv/`, writer state, caches) is moved into the same relative place in the clone before the link goes live, so absolute paths, venv shebangs and `realpath` calls resolve unchanged (ASSUMPTION A1, tested in S5).
- KTD4. AlienPc uses a cone-mode sparse checkout (`alienpc/`, `hosts/alienpc/`, `records/`) to avoid pulling X3's 3.5k community files twice.
- KTD5. Secrets first: ignore-rule additions and the snapshot-script fix land on `u58` BEFORE the build, so `mono` starts clean; a full-history gitleaks run happens before any push.

### Assumptions

- A1. Python/bash code that calls `Path.resolve()`/`realpath` on `/home/evo/AI/...` works when that path is a symlink (resolved path changes to the clone path; any code that compares resolved paths to hardcoded strings would break). Test: pytest suites in x3/community/scripts/parody and a dry render.
- A2. `git filter-repo` is installable on the box (pip, ~100 KB). Audit 2026-11-19: not installed on the box, the X3 or AlienPc.
- A3. The Hermes context-file rule that skips symlinks pointing outside the project (see Hermes plan H2) does not affect Render, because render-pi.sh passes OPERATOR.md by path with `--no-context-files`. Hermes desk files (Hermes plan) live outside these repos.

### Secret safety (planned step S1)

- `.gitignore` (root) additions: `.env`, `.env.*`, `*.token`, `*.secret`, `*.key` (with `!*.pub` style exceptions if needed). Already present and kept: `*.env`, `*.cred`, `auth.json`, `**/auth.json`, `**/mcp.json`, `models.json`, `models-store.json`.
- Untrack (index only, files kept on disk) the 2 still-tracked `records/gufo-phase1-20261117/backup-20261117-070651-pre-gufo/home-evo-pi-panes-{forge,render}/mcp.json` (VERIFIED tracked in u58 HEAD 4cd04c7 despite the ignore rule; contents not opened). Derrick's yes (card Q5).
- `scripts/snapshot-live-setup.sh`: delete line 70 (`scrub_evo "$A/mcp.json" ...`); add `mcp.json` to the pane-file skip list on line 84 (`auth.json|models-store.json|mcp.json|*.secret|*.log`); add a final guard that greps the snapshot output for `Authorization`/`Bearer ` header values and `mcp.json` files and exits non-zero before any commit. Test: run the script into a temp dir; guard passes; no mcp.json in output.
- Pre-push: existing gitleaks pre-push hook (box `ops/gitleaks-pre-push.sh`) on the box clone that pushes GitHub.
- Separate finding (not changed here): AlienPc Gitea remotes embed credentials in the remote URL (values not shown). Card Q6.

### Ordered steps

| Step | Where | Lease | What | Test |
|---|---|---|---|---|
| S0 | chat | none | Opus reviews this plan; Derrick answers cards Q1-Q7 and says yes. | yes recorded |
| S1 | X3 repo `u58` (repo files only) | none | Secret safety edits above; commit explicit paths; push Gitea, then GitHub from box. | gitleaks clean; snapshot dry run passes guard |
| S2 | X3 + AlienPc | take X3 lease + AlienPc lease | Freeze: no render/Forge/Hermes job running; commit or stash AlienPc's 131 + 9 changes per Q4; push all part branches; record tip SHAs in `records/monorepo-consolidation/FREEZE.md`. | all `git status` clean or stashed; SHAs recorded |
| S3 | box `/workspace/evo-x3-mono` | leases held | Fresh clones from Gitea; filter-repo per part to its prefix; `mono` = u58 + 5 unrelated-history merges; add root README map. | tree hash per prefix == part tip tree; gitleaks full history; `git log -- x3/render/OPERATOR.md` shows old commits |
| S4 | Gitea, GitHub | leases held | Push `mono` to Gitea (new branch), then from box clone to GitHub via gh. | tips equal |
| S5 | X3 (X3 Forge) | X3 lease | As evo: clone `mono` to `/home/evo/AI/evo-x3` ; move untracked runtime dirs into the clone; rename `/home/evo/AI/{render,community,forge}` to `*.pre-mono`; `ln -s` each to `evo-x3/x3/{render,community,forge}`; `/home/derekboone/evo-x3` switched to branch `mono` (same path). | smoke list below |
| S6 | AlienPc (AlienPc Forge) | AlienPc lease | Clone `mono` sparse to `C:\AI\evo-x3`; rename `C:\AI\render`, `C:\AI\community` to `*.pre-mono`; `mklink /J` each to `C:\AI\evo-x3\alienpc\...`; move untracked runtime data. | ComfyUI launcher starts; one X3 remote render job completes |
| S7 | Gitea | none | Leases cleared; part branches frozen (no new pushes; README note); archive tags + default-branch switch only on Q1 yes; `*.pre-mono` dirs removed only on Derrick's yes after 7 days. | RESULT.md filled |

S5 smoke list (X3): `render-pi.sh` starts and shows OPERATOR.md; `render_writer_pipeline.py` dry ask returns READY/NOT_READY with correct paths; `queue-remote.sh <run> --yes-derrick --dry-run` passes its checks; pytest in `x3/community/scripts/parody` green; `evo-renders-sync.service` one manual run exits 0 and still sees `/home/evo/AI/community/runs`; `pi-job status` and a `pi-job review` dry task start Forge; Hermes gateway `is-active`; `evo-x3-config-rsync-qnap` dry run reads `/home/derekboone/evo-x3`.

### Rollback

Per machine, in under 5 minutes: remove the symlink/junction, rename `*.pre-mono` back, move runtime dirs back (they were moved, not copied: the move list from S5/S6 is the undo list). Repo side needs nothing: old branches untouched, `mono` is additive and can be deleted on Derrick's yes.

### Open questions for Derrick (cards)

- Q1. When `mono` passes, make it the default branch on Gitea and GitHub and add `archive/<branch>` tags for the old part branches? (Branch deletion only on a later separate yes.)
- Q2. Old side branches `main` (2026-11-15), `x3-forge`, `x3-pi-config`, `x3-bakeoffs`, `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `evo-x3-all`: import into `mono` under `archive/`, or leave as tags only? Plan default: tags only.
- Q3. Keep u58 content at repo root (default) or move it to `x3/host/` (would require editing repo-relative paths in its scripts)?
- Q4. AlienPc `C:\AI\community` has 131 uncommitted changes and `C:\AI\render` 9: commit them as-is (after gitleaks), or stash and review first?
- Q5. Untrack the two tracked `mcp.json` backup files from u58 (index only)?
- Q6. AlienPc Gitea remote URLs carry embedded credentials: switch them to Git Credential Manager during S6? (Changes how AlienPc authenticates; Derrick types nothing new.)
- Q7. Retire the separate Gitea repos `derrick/alienpc-render` and `derrick/alienpc-community-pc` after S6 (archive, not delete)?

---

## Verification Contract

| Check | Command | Step |
|---|---|---|
| Tree equality | `git rev-parse mono:x3/render` vs `git rev-parse <x3-render tip>^{tree}` (same for each prefix; root vs u58 minus added folders) | S3 |
| History kept | `git log --oneline -- x3/render/OPERATOR.md \| wc -l` > 1 | S3 |
| Secrets | `gitleaks detect --log-opts="mono"` on the box | S1, S3 |
| Mirror | `git ls-remote gitea refs/heads/mono` == `git ls-remote origin refs/heads/mono` | S4 |
| Live | S5 / S6 smoke lists | S5, S6 |

## Definition of Done

R1-R7 marked DONE in `records/monorepo-consolidation/RESULT.md` with evidence; leases cleared; Derrick's answers to Q1-Q7 recorded; `*.pre-mono` kept until his yes.

---

## Appendix: hardcoded paths (read-only grep, 2026-11-19)

Pattern: `/home/evo/AI/(render|community)`, `/home/derekboone/AI/(render|community)`, `evo-x3/pi-chats`, `/home/(evo|derekboone)/evo-x3`, plus `pi-job`'s `HOME / "AI" / ...` joins. Excluded: tests, `_archive`, `archive`, `runs`, logs, `.bak`. AlienPc `C:\AI\...` paths were not grepped (junctions keep them).

With KTD3 (links at the same paths): 0 files must change. If paths were repointed instead: 63 files.

| Group | Files | Count |
|---|---|---|
| X3 system | `/usr/local/bin/sync-renders` (lines 80-82), `/usr/local/bin/evo-x3-config-rsync-qnap` (48, 81, 83), `/usr/local/bin/pi-job` (lines 25-41: AI/render, AI/community, evo-x3/pi-chats) | 3 |
| Hermes | `/home/evo/.hermes/skills/pi-job/SKILL.md` | 1 |
| pi launchers | `/home/evo/evo-x3/pi-chats/{README.md,render-pi.sh,forge-pi.sh}`; `/home/derekboone/evo-x3/pi-chats/{README.md,forge-pi.sh,sydney-pi.sh}` (sydney file not opened) | 6 |
| other X3 scripts | `/home/evo/evo-x3/scripts/herdr-panes.sh`, `/home/evo/AI/pixlstash-tagging/index_map.py` | 2 |
| x3-render repo | `writer_pipeline/config.yaml`, `x3/README-X3.md`, `.pi/settings.json` | 3 |
| x3-community repo | `scripts/parody/{build_request,render_writer_pipeline,scene_addenda,voice_refmod_trim}.py`, `scripts/parody/run_batch.sh`, `scripts/run_queue.py`, 19 skill files under `skills/` | 25 |
| Forge repo | `.pi/settings.json`, `launcher/README.md`, `ralph-community/{ralph.sh,run-u56-pass.sh,fix_plan.md,fix_plan.u56-item0.md}`, 4 records/briefs | 10 |
| u58 repo | `config/bin/{evo-x3-config-rsync-qnap,sync-renders}`, `config/forge-pi/settings.json`, `config/pi-evo/{README.md,forge-project-settings.json,pi-chats/README.md,pi-permissions.jsonc}`, `config/pi/pi-permissions.jsonc`, `scripts/evo-agent-host/herdr-panes.sh`, `scripts/forge-mcp/{README.md,server.py}`, `scripts/snapshot-live-setup.sh`, `scripts/sync-renders.sh` | 13 |

No crontab or systemd unit (system or evo user) references these paths (VERIFIED 0 hits); the timer calls `/usr/local/bin/sync-renders`.

CE steps: plan Durable (this file) · doc review: Opus (outside AI) per Derrick · work not started · compound n/a.

## Max's recommendations on the open questions (Derrick asked for these, t2624u/t2625u, Nov 19 2026)

Context for the reviewer: Derrick's reviewer (Opus via GitHub Copilot) sees only this GitHub repo. It has no access to the X3, AlienPc, the QNAP, Gitea or the chat, so this file must carry the full context.

1. Default branch: **yes.** Make `mono` the default on Gitea and GitHub once its checks pass, and tag the old part branches `archive/<branch>`. One default branch puts the whole setup in front of the reviewer.
2. Old side branches (`main`, `x3-forge`, `x3-pi-config`, `x3-bakeoffs`, `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `evo-x3-all`): **tags only.** They're past work, and importing them would clutter the review.
3. `u58` content: **keep it at the repo root.** Moving it to `x3/host/` means editing repo-relative paths in its scripts, which adds risk and gains nothing.
4. AlienPc uncommitted changes (131 in community, 9 in render): **run a gitleaks scan, pull out anything it flags, then commit the rest as it is.** If they're stashed instead, they never reach GitHub and can't be reviewed.
5. The two tracked `mcp.json` backups under `records/gufo-phase1-20261117/`: **untrack them** (index only; the files stay on disk). Max checked them, and they hold a file-path reference (`!cat <path>`), not a literal token. Untracking keeps the rule simple: no `mcp.json` in git.
6. AlienPc remotes with a login inside the URL: **yes, switch to Git Credential Manager** during the switchover.
7. Separate Gitea repos `alienpc-render` and `alienpc-community-pc`: **archive them (read-only, not deleted)** after the switchover.

GitHub mirror: GitHub is currently pushed by hand from Max's box after each Gitea save (Gitea is primary). Until mirroring is automated, every Gitea push in this plan should be followed by the same fast-forward push to GitHub, so the reviewer's copy stays current.
