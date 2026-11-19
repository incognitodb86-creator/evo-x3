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

Related: ../hermes-direct-render/PLAN.md · **single plan for review: [../uplan/PLAN.md](../uplan/PLAN.md)** (live audit 2026-11-19 10:42-10:55 AM CT; Wave 5 = this plan)

Status: **REVIEWED (`VERDICT: CHANGES` addressed, 2026-11-19 CT) & APPROVED BY DERRICK TO RUN S1–S7** after Max mirrors `u58` from GitHub to Gitea. S1 repo-file prep (`.gitignore`, `scripts/snapshot-live-setup.sh`, untracking the 2 `gufo` `mcp.json` index entries) landed on `u58` alongside this revision; live host/box work (S1 dry run + gitleaks, S1b–S7) has NOT started yet. Labels: VERIFIED (read live or against repo refs), ASSUMPTION (to test in the step that uses it).

## Goal Capsule

| Field | Value |
|---|---|
| Objective | One repo, one main branch, one folder per part, full history kept, for the whole X3 + AlienPc setup (Derrick t2620u/t2621u). |
| Means | `git filter-repo --to-subdirectory-filter` per part branch, merged with `--allow-unrelated-histories` into a NEW branch `mono` on Gitea `derrick/evo-x3`; live checkouts switch by `--no-checkout` clone + dir adoption + symlink (X3) / junction (AlienPc) so existing paths stay unchanged after patching `resolve().parents`/`show-toplevel` sites (S1b). |
| Authority | Derrick t2620u/t2621u (plan), t2624u/t2625u (recommendations), and 2026-11-19 Copilot approval (Q1–Q8 approved, Opus review fixes folded in, S1 repo prep landed on GitHub `u58`, authorized to run S1–S7 after mirroring `u58` to Gitea). |
| Out of scope | General scattered-files / QNAP cleanup (deferred). Moving or deleting runtime data (runs, models, PixlStash, outputs). Any change to llama-swap.yaml, ComfyUI, Hermes config. |
| Stop conditions | Tree-hash or root-diff check (S3) fails; gitleaks finds any unbaselined live secret in history; any render, Forge, Hermes job, timer, or open file handle is active at switchover; non-fast-forward AlienPc branch sync in S2; any smoke test in S5/S6 fails → roll back that machine. |

## Summary

Today each part lives on its own branch of `derrick/evo-x3`, and AlienPc pushes to two separate Gitea repos. The plan builds a new `mono` branch where `u58` (host config, hosts/, records/, scripts/) stays at the root and each other part moves under a folder, keeping every commit. Live checkouts then become symlinks/junctions into one clone, so `/home/evo/AI/render`, `/home/evo/AI/community`, `/home/evo/AI/forge`, `C:\AI\render` and `C:\AI\community` keep working at the same paths. Symlinks/junctions avoid rewriting the 63 literal hardcoded path sites (Appendix), while a small targeted pre-freeze patch (S1b, 8 sites across 3 part branches) fixes scripts that compute paths via `Path.resolve().parents[N]` or `git rev-parse --show-toplevel`. Old part branches stay untouched (no force push) as rollback and get `archive/<branch>` tags in S7 (Q1 approved).

Community way: git-filter-repo docs, example "git filter-repo --to-subdirectory-filter my-module/" (newren/git-filter-repo Documentation, accessed 2026-11-19) and git-subtree docs (git/git contrib/subtree, "add <repository> <remote-ref>", `--squash` imports one commit) → adapt: filter-repo + unrelated-histories merge keeps per-file history under the new path (subtree add keeps commits but pre-merge history does not show under the prefix path); `git sparse-checkout` cone mode (git-scm docs) used on AlienPc only to skip X3 folders.

---

## Product Contract

### Current layout (VERIFIED)

Gitea `derrick/evo-x3` branches (commits / tracked files / last commit):

| Branch | What | Commits | Files | Live checkout tracking it |
|---|---|---|---|---|
| `x3-render` | Render: OPERATOR.md, AGENTS.md, writer_pipeline, x3/render-pi.sh, queue-remote.sh, .pi | 53 | 33 | `/home/evo/AI/render` (local branch `x3-linux`, upstream `gitea/x3-render`) |
| `x3-community` (= `x3-linux`, same SHA 6bdcc49c) | community: scripts (render_writer_pipeline, run_queue, remote_upscale), skills, templates | 685 | 3,518 | `/home/evo/AI/community` (local `x3-linux`, upstream `gitea/x3-community`) |
| `u58` | X3 host: config/, hosts/x3, hosts/alienpc, scripts/ (pi-job, sync-renders, snapshot), records/ | 54 (at `e0c446f`, before S1) | 1,071 | `/home/derekboone/evo-x3` (upstream `gitea/u58`) |
| `u58-chat-read-plan` | Forge (ralph-community, loop-guard, records) | 14 | 22 | `/home/evo/AI/forge` |
| `alienpc-render` (5c3450d) | copy of AlienPc `C:\AI\render` | 34 | 20 | AlienPc `C:\AI\render` pushes to separate Gitea repo `derrick/alienpc-render` (master) |
| `alienpc-community` (6dadffc) | copy of AlienPc `C:\AI\community` | 636 | 3,486 | AlienPc `C:\AI\community` pushes to `derrick/alienpc-community-pc` (master) |
| `evo-x3-all` | flat snapshot, one folder per part (no history); current `origin/HEAD` (`96b71aa`) | 28 | 11,328 | none |
| also | `main` (9, 2026-11-15), `x3-forge` (9), `x3-pi-config` (19), `x3-bakeoffs` (1), `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `feature/alienpc-only-remediation`, `feature/x3-community-u56`, `feature/x3-forge-u56`, `feature/x3-pi-config-u56`, `feature/x3-render-u56`, `feature/x3-u56-render-consolidated` | | | none |

Not a git checkout but part of the setup (added after the 2026-11-19 live audit): AlienPc Forge `C:\Users\derek\forge` is a junction to `C:\Users\derek\5slock` (pi working root, ralph loop, x3run/x3put), and the AlienPc global pi folder `C:\Users\derek\.pi\agent\` (AGENTS.md, settings, permissions, extensions, skill links). Their instruction/config files are tracked as read-only copies under `u58` `hosts/alienpc/live/`; runtime data there (runs, sessions, libraries) stays out. Decide in S2 whether `5slock` gets its own folder in `mono` (default: keep the `hosts/alienpc/live/` copy).

Notes: `x3-community` and `alienpc-community` share history (merge-base c85afa00); `x3-render` and `alienpc-render` too (7c219cce). AlienPc `C:\AI\community` has 131 uncommitted changes and `C:\AI\render` 9. GitHub `incognitodb86-creator/evo-x3` mirrors these branches, pushed from the box clone `/workspace/evo-x3-u57`.

### Requirements

- R1. One repo (`derrick/evo-x3`), one main branch, one folder per part, full history kept. Pass: for each part, `git rev-parse mono:<prefix>` equals the tree hash of the part branch tip it was built from; `git log -- <prefix>/<file>` shows pre-merge commits. Gate: Max, then Opus review.
- R2. Live Render, Forge, Hermes, `evo-renders-sync` timer, render-pi.sh and queue-remote.sh keep working through and after switchover. Pass: S5 smoke list all green. Gate: Max under X3 lease.
- R3. AlienPc ComfyUI and its launchers keep working. Pass: S6 smoke list green. Gate: Max under AlienPc lease.
- R4. No unbaselined live secrets in the new branch or its history; ignore rules cover `.env`, `.env.*`, `*.env`, `*.token`, `*.secret`, `*.key` (`!*.pub`), `*.cred`, `auth.json`, `mcp.json`, `models.json`; snapshot script never copies `mcp.json` or unredacted Authorization/Bearer headers. Pass: `gitleaks git --log-opts="mono" --config .gitleaks.toml` clean with `.gitleaksignore` baselining only the known `1f4004a` Home Assistant header (HA is down per Derrick 2026-11-19; rotate if ever brought back online); `git ls-files` over secret-name patterns (`.env`, `.env.*`, `*.env`, `**/auth.json`, `**/mcp.json`, `**/models-store.json`, `*.token`, `*.cred`, `*.secret`, `*.key`) is empty; `git ls-files -ci --exclude-standard` triaged in S3. Gate: Max + Derrick for any new hit.
- R5. Gitea is primary; GitHub is a mirror pushed from the box host (`/workspace/evo-x3-u57`, separate from X3 — `gh` stays absent on X3 by rule) via `gh`. Pass: Gitea `mono` tip == GitHub `mono` tip; no new plaintext credentials added on X3 or AlienPc (AlienPc switches to Git Credential Manager per Q6). Gate: Max.
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

- KTD1. Merge method: clone each part branch with `--single-branch --no-tags`, run `git filter-repo --to-subdirectory-filter <prefix>/` on that throwaway clone, then fetch with `--no-tags` and `git merge --allow-unrelated-histories` into `mono` (started from `u58`). `--no-tags` prevents tag collisions between shared x3/alienpc history. Rejected: `git subtree add` (pre-merge history does not follow `git log -- <prefix>/...`); `--squash` (drops history, against R1); flat copy like `evo-x3-all` (no history).
- KTD2. New branch `mono`, nothing rewritten. Imported commits get new SHAs inside `mono` only; the original branches and their SHAs stay untouched on Gitea and GitHub. Making `mono` the default branch and adding `archive/<branch>` tags is approved (Q1).
- KTD3. Live switchover by `--no-checkout` clone + whole-dir adoption + link: quiesce all timers/processes first, clone `mono` with `--no-checkout`, move each old checkout into its target prefix (`x3/{render,community,forge}` on X3; `alienpc/{render,community}` on AlienPc), move its `.git` aside to `*.pre-mono/.git` (preserving instant rollback), run mixed `git reset` and check out only missing tracked files, verify `git status` shows only expected untracked runtime files, then create `ln -s` (X3) / `mklink /J` (AlienPc). This handles the 16 tracked files already under `x3-community/runs/` (VERIFIED via `ls-tree`) without clobbering or nesting `runs/`. If any machine moves runtime dirs individually instead, save the exact list from `git ls-files -o --directory` (plain and `-i --exclude-standard`) to `records/monorepo-consolidation/MOVES-<host>.txt` before moving.
- KTD4. AlienPc uses `--no-checkout --filter=blob:none` + cone-mode sparse checkout (`alienpc`, `hosts/alienpc`, `records`) BEFORE first checkout so Windows never attempts to create the Windows-invalid filenames under `hosts/x3/live/systemd` (VERIFIED: `mnt-qnap-derek\x2dhomes.automount`).
- KTD5. Secrets & ignore hygiene first: ignore-rule additions (anchoring root `/_archive/` and `/sessions/` so they do not shadow tracked part folders), `scripts/snapshot-live-setup.sh` guard, and untracking the 2 `gufo` `mcp.json` index entries land on `u58` in S1 BEFORE the build. Because `u58` history already holds the `1f4004a` Home Assistant header (untracked in `849bce7`; HA is down per Derrick 2026-11-19), S1/S3 baselines only those exact `1f4004a` fingerprints in `.gitleaksignore` instead of rewriting history (R7), and a full-history `gitleaks git` run gates any push.

### Assumptions

- A1. **DISPROVEN (VERIFIED by Opus review `git grep`, 2026-11-19):** scripts that call `Path.resolve().parents[N]` or `git rev-parse --show-toplevel` resolve inside the `mono` clone instead of `/home/evo/AI` or `/home/evo/AI/forge` (and Python ≥3.8 `os.path.realpath` also resolves Windows junctions). Affected sites to patch in **S1b** before S5:
  - `x3-community`: `scripts/parody/render_writer_pipeline.py:50`, `scripts/parody/resolve.py:14,15,20,21,469`, `scripts/parody/sync_refmods.py:163`, `scripts/parody/test_modular_s3_and_writer_sys.py:500-501`
  - `x3-render`: `writer_pipeline/acceptance/wp_accept.py:8`, `writer_pipeline/acceptance/t3_plan.py:9`
  - `u58-chat-read-plan`: `ralph-community/ralph.sh:321,354`
  Fix: use `EVO_AI_ROOT` defaulting to `/home/evo/AI` (or `.absolute()` instead of `.resolve()`) for the Python paths, and explicit Forge root (`SCRIPT_DIR` / `FORGE_ROOT`) in `ralph.sh`. Verified by pytest + S5 `resolve.py` and `ralph.sh` smoke checks.
- A2. `git filter-repo` was NOT installed on the box, the X3, or AlienPc (audit 2026-11-19). **RESOLVED:** the `mono` branch (`235bfefa` base merge + `747eeb3c` README/FREEZE) was built on Derrick's Windows PC using `git-filter-repo` (`a40bce548d2c`) and pushed to GitHub `origin/mono`, so neither X3 nor AlienPc needs `git-filter-repo` installed.
- A3. The Hermes context-file rule that skips symlinks pointing outside the project (see Hermes plan H2) does not affect Render, because render-pi.sh passes OPERATOR.md by path with `--no-context-files`. Hermes desk files (Hermes plan) live outside these repos.

### Secret safety (step S1 — repo edits landed on `u58`, live dry run + gitleaks remain for Max)

- `.gitignore` (root, **DONE on `u58`**): added `.env`, `.env.*`, `*.token`, `*.secret`, `*.key`, `!*.pub`; anchored `/sessions/` and `/_archive/` to root so tracked part archives are not shadowed. Kept: `*.env`, `*.cred`, `auth.json`, `**/auth.json`, `**/mcp.json`, `models.json`, `models.json.*`, `!models.json.example`, `models-store.json`.
- Untracked (index only, files kept on disk, **DONE on `u58` per Q5**): `records/gufo-phase1-20261117/backup-20261117-070651-pre-gufo/home-evo-pi-panes-{forge,render}/mcp.json` (contents not opened).
- `scripts/snapshot-live-setup.sh` (**DONE on `u58`**): supports `SNAPSHOT_OUT` for isolated temp-dir dry runs (including PixlStash tagging output); deleted `scrub_evo "$A/mcp.json"`; added `mcp.json` to the pane-file skip list; added a final guard checking `find "$R" -name 'mcp.json'` and `grep -rIliE` for unredacted Authorization/Bearer headers (prints filenames only, never values, exits non-zero). Dry run on X3 takes the X3 lease: `SNAPSHOT_OUT=/tmp/evo-snap-test bash scripts/snapshot-live-setup.sh && rm -rf /tmp/evo-snap-test`.
- `.gitleaks.toml` / `.gitleaksignore`: `origin/u58-chat-read-plan:.gitleaks.toml` is VERIFIED identical to root `.gitleaks.toml` (re-check at S3 freeze and merge any new Forge entries with `x3/forge/` prefix). In S1/S3 on the box, record only the known `1f4004a` Home Assistant header fingerprints in `.gitleaksignore` (Derrick 2026-11-19: HA is down; rotate before ever bringing HA back online).
- Pre-push: existing gitleaks pre-push hook (box `ops/gitleaks-pre-push.sh`) runs on `/workspace/evo-x3-u57` before pushing GitHub.
- Separate finding (approved in Q6): AlienPc Gitea remotes embed credentials in the remote URL (values not shown). Switch AlienPc remotes to Git Credential Manager in S6, run `git remote set-url` on any `*.pre-mono` backup dirs to scrub embedded creds from `.git/config`, and rotate that Gitea token.

### Ordered steps

| Step | Where | Lease | What | Test |
|---|---|---|---|---|
| S0 | chat / GitHub `u58` | none | **DONE (2026-11-19):** Opus reviewed PLAN.md (`VERDICT: CHANGES`); all 15 findings folded in; Derrick approved Q1–Q8 and authorized S1–S7. Max mirrors `u58` from GitHub to Gitea first. | verdict + yes recorded |
| S1 | X3 + box (`u58`) | X3 lease (for snapshot dry run) | Repo edits already landed on `u58` (mirror to Gitea). On X3: dry-run `SNAPSHOT_OUT=/tmp/evo-snap-test bash scripts/snapshot-live-setup.sh` and remove `/tmp/evo-snap-test`. On box: run `gitleaks git --log-opts="u58" --config .gitleaks.toml`, add only `1f4004a` HA fingerprints to `.gitleaksignore`, commit explicit path, push Gitea + GitHub. | snapshot dry run passes guard; `gitleaks git --log-opts="u58"` clean |
| S1b | `mono` (`x3/community/`, `x3/render/`, `x3/forge/`; file work, no part-branch push - one-branch rule 2026-11-19) | none for the files; X3 lease for the smoke checks | Patch the 8 `resolve().parents[N]` / `git rev-parse --show-toplevel` sites (A1) using explicit `git add`, and check AlienPc scripts for `realpath`/`resolve().parents` assumptions. Also check the newer sites on `mono` (`h3max_bridge.py:90`, `c2v_chain.py:512`, `run_record.py:20`, `voice_refmod_trim.py:58`, `wp_compile_prompt.py:18`, `writer_sys.py:16,25`). Commit to `mono` only. | `pytest -q` in `scripts/parody` green; `resolve.py` resolves `/home/evo/AI` via symlink test; `ralph.sh` prints Forge root |
| S2 | X3 + AlienPc + box | take X3 lease + AlienPc lease | Quiesce: stop `evo-renders-sync.timer` & evo user timers on X3; confirm `/proc/*/cwd` and `lsof +D /home/evo/AI/{render,community,forge}` are empty. Stop ComfyUI, launchers, and open shells on AlienPc. On AlienPc: inspect `git status --porcelain -uall` + file sizes for the 131 + 9 changes, refuse media (`*.png`, `*.mp4`, `*.wav`, etc.) and files > 5 MB, run `gitleaks` on changed files, commit explicit paths & push to `derrick/alienpc-{render,community-pc}`. From box: fetch `master` from both AlienPc repos and fast-forward push to `derrick/evo-x3` `alienpc-render` / `alienpc-community` (STOP if non-FF). Push all X3 part branches; record source + target tip SHAs in `records/monorepo-consolidation/FREEZE.md`. | all `git status` clean; zero open handles; FF syncs + SHAs recorded |
| S3 | Windows PC build → `mono` (**DONE**) | none | **DONE (2026-11-19):** Built `mono` from fresh `--single-branch --no-tags` clones using `git-filter-repo` + `git merge-tree --write-tree --allow-unrelated-histories` (`235bfefa` base merge, 8,148 files, 1,482 commits), verified root `git diff --exit-code` (`0`) + all 5 prefix tree hashes exact-match + per-file history + 0 secret-name files, then added root `README.md` map & `FREEZE.md` (`747eeb3c`). On box after mirroring `mono` to Gitea: run `gitleaks git --log-opts="mono" --config .gitleaks.toml`, triage `git ls-files -ci --exclude-standard`, and re-check `x3/forge/.gitleaks.toml`. | base tree/root/history checks PASS (`FREEZE.md`); box `gitleaks git` pending |
| S4 | GitHub `origin/mono` → Gitea (**pushed to GitHub; mirror to Gitea pending**) | none | `mono` (`747eeb3c` + any follow-up commits) is pushed to GitHub `origin/mono` (no force push). On the box (`/workspace/evo-x3-u57`, separate from X3; holds `ops/gitleaks-pre-push.sh`): fetch `u58` and `mono` from GitHub `origin` and push to primary Gitea `gitea` (`derrick/evo-x3`). Resume Gitea-primary → GitHub fast-forward mirroring thereafter. | `git ls-remote gitea refs/heads/mono` == `git ls-remote origin refs/heads/mono` |
| S5 | X3 (**Max, or AlienPc Forge over SSH — NOT X3 Forge**) | X3 lease | **Owner rule (unified review Finding 9):** X3 Forge MUST NOT run S5 on itself because S5 renames `/home/evo/AI/forge` (X3 Forge's own cwd/records) and S2's freeze forbids any active Forge job. Confirm timers stopped and `/proc/*/cwd` + `lsof +D` empty. As `evo`: `git clone --no-checkout <gitea-url> /home/evo/AI/evo-x3` (branch `mono`), adopt `/home/evo/AI/{render,community,forge}` into `/home/evo/AI/evo-x3/x3/{render,community,forge}` (moving each old `.git` to `/home/evo/AI/<part>.pre-mono/.git` so rollback is instant), run mixed `git reset` and restore only missing root files, verify `git status` shows only expected untracked runtime files, then `ln -s /home/evo/AI/evo-x3/x3/<part> /home/evo/AI/<part>`. Switch `/home/derekboone/evo-x3` to `mono` and exclude `x3/` and `alienpc/` in `evo-x3-config-rsync-qnap` (Q8). Restart stopped timers. | smoke list below |
| S6 | AlienPc (**Max / host shell — NOT a running AlienPc Forge pi pane**) | AlienPc lease | **Owner/quiesce rule (unified review Finding 9):** Stop ComfyUI, launchers, open shells, AND **AlienPc Forge's pi panes** before swapping `C:\AI\community` (its skill links and global `AGENTS.md` point into `C:\AI\community`). Configure Git Credential Manager for Gitea (Q6). Run `git clone --no-checkout --filter=blob:none <gitea-url> C:\AI\evo-x3`, `git -C C:\AI\evo-x3 sparse-checkout init --cone --sparse-index`, `git -C C:\AI\evo-x3 sparse-checkout set alienpc hosts/alienpc records`, adopt `C:\AI\render` & `C:\AI\community` into `C:\AI\evo-x3\alienpc\{render,community}` (keeping old `.git` in `*.pre-mono` and running `git remote set-url` on `*.pre-mono` to scrub embedded creds), `git checkout mono` / mixed `git reset`, then `mklink /J C:\AI\render C:\AI\evo-x3\alienpc\render` and `mklink /J C:\AI\community C:\AI\evo-x3\alienpc\community`. Rotate the old AlienPc Gitea token (Q6). | ComfyUI launcher starts; one X3 remote render job completes; AlienPc Forge skill links & global `AGENTS.md` resolve cleanly after swap; no embedded creds left in `.git/config` |
| S7 | Gitea + GitHub | none | Clear X3 & AlienPc leases; freeze part branches (README note, no new pushes); make `mono` default branch on Gitea + GitHub and create `archive/<branch>` tags for old part + Q2 side branches (Q1/Q2 approved); archive (read-only, do not delete) `derrick/alienpc-render` and `derrick/alienpc-community-pc` (Q7 approved); keep `*.pre-mono` backup dirs until Derrick's separate yes after 7 days. | `RESULT.md` filled; R1–R7 marked DONE |

S5 smoke list (X3): `render-pi.sh` starts and shows OPERATOR.md; `resolve.py` prints existing `5slock` and PixlStash directories behind the symlink; `ralph.sh`: not run after S5 until its mono rework lands (see Update 14:30 CT); `render_writer_pipeline.py` dry ask returns READY/NOT_READY with correct paths; `queue-remote.sh <run> --yes-derrick --dry-run` passes its checks; pytest in `x3/community/scripts/parody` green; `evo-renders-sync.service` one manual run exits 0 and still sees `/home/evo/AI/community/runs`; `pi-job status` and a `pi-job review` dry task start Forge; Hermes gateway `is-active`; `evo-x3-config-rsync-qnap` dry run reads `/home/derekboone/evo-x3` and skips `x3/` and `alienpc/`.

### Rollback

Per machine, in under 5 minutes:
- **X3:** stop `evo-renders-sync.timer` / evo user timers, remove the 3 symlinks, move `/home/evo/AI/evo-x3/x3/{render,community,forge}` back to `/home/evo/AI/{render,community,forge}` (carrying any runs created after switchover), restore each `.git` from `<part>.pre-mono/.git`, run `git -C /home/derekboone/evo-x3 switch u58`, and restart the stopped timers. (If per-file moves were used instead of whole-dir adoption, reverse `records/monorepo-consolidation/MOVES-x3.txt` plus any post-switchover runs.)
- **AlienPc:** stop ComfyUI/launchers, remove the 2 junctions (`rmdir C:\AI\render`, `rmdir C:\AI\community`), move `C:\AI\evo-x3\alienpc\{render,community}` back (carrying any post-switchover files), restore each `.git` from `*.pre-mono/.git`, and restart ComfyUI.
- **Repo side:** needs nothing — old branches remain untouched, and `mono` is additive.

### Open questions — DECIDED BY DERRICK (2026-11-19 CT)

- Q1. When `mono` passes, make it the default branch on Gitea and GitHub (current default `origin/HEAD` is `evo-x3-all`) and add `archive/<branch>` tags for the old part branches (branch deletion only on a later separate yes): **APPROVED (YES).**
- Q2. Old side branches (`main`, `x3-forge`, `x3-pi-config`, `x3-bakeoffs`, `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `evo-x3-all`, `feature/alienpc-only-remediation`, `feature/x3-community-u56`, `feature/x3-forge-u56`, `feature/x3-pi-config-u56`, `feature/x3-render-u56`, `feature/x3-u56-render-consolidated`): **APPROVED — tags only (`archive/<branch>`).**
- Q3. Keep `u58` content at repo root: **APPROVED (YES).**
- Q4. AlienPc `C:\AI\community` (131 uncommitted) and `C:\AI\render` (9 uncommitted): **APPROVED — filter out media/oversized (>5 MB) files, run `gitleaks`, commit the rest as-is and fast-forward sync into `evo-x3`.**
- Q5. Untrack the two tracked `gufo` `mcp.json` backup files from `u58` (index only, files kept on disk; contents not opened): **APPROVED (YES — done on `u58`).**
- Q6. AlienPc Gitea remote URLs with embedded credentials: **APPROVED — switch to Git Credential Manager in S6, scrub `*.pre-mono/.git/config` URLs with `git remote set-url`, and rotate the exposed Gitea token.**
- Q7. Separate Gitea repos `derrick/alienpc-render` and `derrick/alienpc-community-pc` after S6: **APPROVED — archive (read-only, do not delete).**
- Q8 (from Opus review). (a) Baseline `1f4004a` Home Assistant header fingerprints in `.gitleaksignore` without rewriting history (Derrick 2026-11-19: HA is down; rotate if ever brought back online); (b) land S1 ignore rules + snapshot guard; (c) patch the 8 symlink/junction `resolve().parents`/`show-toplevel` sites in S1b before S5; (d) exclude `x3/` and `alienpc/` from `evo-x3-config-rsync-qnap`: **APPROVED (YES).**

---

## Verification Contract

| Check | Command | Step |
|---|---|---|
| Root equality (pre-README) | `git diff --exit-code <u58-freeze-sha> mono -- . ':(exclude)x3' ':(exclude)alienpc'` | S3 |
| Prefix tree equality | `test "$(git rev-parse mono:<prefix>)" = "$(git rev-parse <part-freeze-sha>^{tree})"` (all 5 prefixes) | S3 |
| History kept | `git log --oneline -- x3/render/OPERATOR.md \| wc -l` > 1 | S3 |
| Secrets | `gitleaks git --log-opts="u58" --config .gitleaks.toml` (S1); `gitleaks git --log-opts="mono" --config .gitleaks.toml` (S3); secret-name `git ls-files` empty; `git ls-files -ci --exclude-standard` triaged | S1, S3 |
| Mirror | `git ls-remote gitea refs/heads/mono` == `git ls-remote origin refs/heads/mono` | S4 |
| Live | S5 / S6 smoke lists (including `resolve.py` and `ralph.sh` behind symlinks) | S5, S6 |

## Definition of Done

R1-R7 marked DONE in `records/monorepo-consolidation/RESULT.md` with evidence; leases cleared; Q1-Q8 decisions executed and recorded; `*.pre-mono` kept until Derrick's yes after 7 days.

---

## Appendix: hardcoded paths (read-only grep, 2026-11-19)

Pattern: `/home/evo/AI/(render|community)`, `/home/derekboone/AI/(render|community)`, `evo-x3/pi-chats`, `/home/(evo|derekboone)/evo-x3`, plus `pi-job`'s `HOME / "AI" / ...` joins. Excluded: tests, `_archive`, `archive`, `runs`, logs, `.bak`. AlienPc `C:\AI\...` paths were not grepped (junctions keep them).

With KTD3 (links at the same paths): 0 of the 63 literal paths below must change; 8 relative/symlink-sensitive sites (`resolve().parents[N]` and `git rev-parse --show-toplevel`, listed under A1) are patched in S1b. If literal paths were repointed instead: 63 files.

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

CE steps: plan Durable (this file) · doc review: Opus (`VERDICT: CHANGES`, 2026-11-19 CT — all 15 findings addressed above) · S1 repo edits landed on `u58` · live work (S1 dry run + S1b–S7) authorized by Derrick 2026-11-19 CT · compound n/a.

## Max's recommendations on the open questions (Derrick asked for these, t2624u/t2625u, Nov 19 2026)

Context for the reviewer: Derrick's reviewer (Opus via GitHub Copilot) sees only this GitHub repo. It has no access to the X3, AlienPc, the QNAP, Gitea or the chat, so this file must carry the full context.

1. Default branch: **yes.** Make `mono` the default on Gitea and GitHub once its checks pass, and tag the old part branches `archive/<branch>`. One default branch puts the whole setup in front of the reviewer.
2. Old side branches (`main`, `x3-forge`, `x3-pi-config`, `x3-bakeoffs`, `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `evo-x3-all`, plus the additional `feature/*` branches in Q2): **tags only.** They're past work, and importing them would clutter the review.
3. `u58` content: **keep it at the repo root.** Moving it to `x3/host/` means editing repo-relative paths in its scripts, which adds risk and gains nothing.
4. AlienPc uncommitted changes (131 in community, 9 in render): **filter out media/oversized files, run a gitleaks scan, pull out anything it flags, then commit the rest as it is.** If they're stashed instead, they never reach GitHub and can't be reviewed.
5. The two tracked `mcp.json` backups under `records/gufo-phase1-20261117/`: **untrack them** (index only; the files stay on disk; contents not opened per repo rule). Untracking keeps the rule simple: no `mcp.json` in git.
6. AlienPc remotes with a login inside the URL: **yes, switch to Git Credential Manager** during the switchover, scrub `*.pre-mono/.git/config` URLs, and rotate the exposed token.
7. Separate Gitea repos `alienpc-render` and `alienpc-community-pc`: **archive them (read-only, not deleted)** after the switchover.

GitHub mirror: GitHub is currently pushed by hand from Max's box after each Gitea save (Gitea is primary). Because this S0/S1 revision was authored on GitHub `u58` at Derrick's direction (2026-11-19), Max should fast-forward `u58` from GitHub to Gitea first, then resume Gitea-primary + fast-forward mirror to GitHub for S1–S7.

## Update 2026-11-19 14:05 CT

Derrick said yes to `S5`/`S6`. Order: `S1b` lands on `mono` first (see row), then `S2`-`S6` in a window when neither lane of the unified plan is running.

## Update 2026-11-19 14:30 CT

`S1b` Python sites done on `mono` `1f8eb17`: they use `EVO_AI_ROOT`, else `/home/evo/AI` when it exists, else the old `resolve()` path. Today that gives the same paths on the X3, so Max can bridge them before S5. Sites: `render_writer_pipeline.py`, `resolve.py`, `sync_refmods.py`, `voice_refmod_trim.py`, `wp_compile_prompt.py`, `writer_sys.py` (lock marker), `wp_accept.py`, `t3_plan.py` and three tests. The other newer sites (`h3max_bridge.py:90`, `c2v_chain.py:512`, `run_record.py:20`, `writer_sys.py:16`) stay inside their own part folder, so they need no change. AlienPc scripts: no `resolve().parents` reaching outside a part; `realpath` uses compare both sides the same way. Windows pytest of the three touched test files: same 101 pass / 18 fail (Windows-only) before and after; the X3 run is in the S5 smoke list.

`ralph.sh` (`:321`, `:354`) is NOT patched. Under `mono`, `git rev-parse --show-toplevel` for both Forge and community returns the one `mono` clone, so Ralph would make one worktree of the whole repo, skip the community worktree (same repo), and its `ralph-community/...` path filters would no longer match (`x3/forge/ralph-community/...`). That is a rework, not a path patch. Default: S5 goes ahead without it, and Ralph is not run after S5 until the rework lands (it is started by hand and has no timer).
