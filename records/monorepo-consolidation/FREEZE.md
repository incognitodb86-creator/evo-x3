---
title: "Monorepo build freeze & S3 verification record (mono)"
date: 2026-11-19
type: record
plan: records/monorepo-consolidation/PLAN.md
author: Copilot (Windows build per Derrick's 2026-11-19 instruction; pushed to GitHub origin/mono for Max to mirror to Gitea)
pending_upload: true
---

# Monorepo Consolidation Build Record (`FREEZE.md`)

Built on **2026-11-19 CT** in a clean throwaway directory (`C:\tmp\evo-mono-build`) from the live GitHub `origin` refs using `git filter-repo --to-subdirectory-filter <prefix>/` (fresh `--single-branch --no-tags` clones, no `--force`) and `git merge-tree --write-tree --allow-unrelated-histories` + `git commit-tree`.

No existing branch was rewritten or force-pushed. `mono` is a brand-new additive branch.

## Exact source SHAs & tree-equality proof

Verified against base merge commit **`235bfefa4c9097c0b1f383f6e56ac28d7f7a163d`** (before adding the root `README.md` map and this `FREEZE.md` file):

| Prefix | Source branch | Source commit SHA | Source commits | Expected tree hash | `mono:<prefix>` tree hash | Result |
|---|---|---|---:|---|---|---|
| `/` (root minus `x3/`, `alienpc/`) | `u58` | `65fa220292b3b68f39358468a4a7e705f5cbe3a3` | 55 | `git diff --exit-code` | exact match (`exit 0`) | **VERIFIED** |
| `x3/render` | `x3-render` | `92325452a16a9a3b49ce7c87f347b8b250c991f0` | 53 | `9bd09300ddbf78ee48bf01d443c41c3dbb2f11a6` | `9bd09300ddbf78ee48bf01d443c41c3dbb2f11a6` | **VERIFIED** |
| `x3/community` | `x3-community` (`= x3-linux`) | `6bdcc49cd087329212eb91341b6d2a9704dafbb1` | 685 | `2fed39d790bd4369005f04b9595c8ad7b408a02b` | `2fed39d790bd4369005f04b9595c8ad7b408a02b` | **VERIFIED** |
| `x3/forge` | `u58-chat-read-plan` | `4cbbba003374eb61509931f36d4256526d38e85b` | 14 | `dd9f10d1f86576aa462d7a8e500984d93119e8bd` | `dd9f10d1f86576aa462d7a8e500984d93119e8bd` | **VERIFIED** |
| `alienpc/render` | `alienpc-render` | `5c3450d4f2b644f9d889442216d120e51edd2f77` | 34 | `db217fe42c3ea7bb66464736a40badb69b1c6402` | `db217fe42c3ea7bb66464736a40badb69b1c6402` | **VERIFIED** |
| `alienpc/community` | `alienpc-community` | `6dadffc4742a554435c9a5f4b7ef3a256b4464af` | 636 | `47fc234c950a21da9085e91ac65d6f612fefa209` | `47fc234c950a21da9085e91ac65d6f612fefa209` | **VERIFIED** |

Base merge totals: **8,148 tracked files**, **1,482 commits** (55 + 53 + 685 + 14 + 34 + 636 + 5 merge commits).

## History & secret-name checks (VERIFIED at `235bfefa`)

- `git log --oneline mono -- x3/render/AGENTS.md`: **26 commits**
- `git log --oneline mono -- x3/render/writer_pipeline/config.yaml`: **12 commits**
- `git log --oneline mono -- x3/community/scripts/parody/render_writer_pipeline.py`: **29 commits**
- `git log --oneline mono -- x3/community/skills/h3-prompting/SKILL.md`: **24 commits**
- `git log --oneline mono -- x3/forge/ralph-community/ralph.sh`: **6 commits**
- `git log --oneline mono -- alienpc/render/AGENTS.md`: **22 commits**
- `git log --oneline mono -- alienpc/community/scripts/run_queue.py`: **23 commits**
- Secret-name scan across all 8,148 tracked files (`auth.json`, `mcp.json`, `models-store.json`, `.env`, `.env.*`, `*.env`, `*.token`, `*.cred`, `*.secret`, `*.key`): **0 hits**.

## Branches intentionally NOT auto-merged into `mono`

- `feature/u58-mono-carryover` (`3e56220`): contains unmerged U56/U57 ports (`stage-src/`, `scripts/probe-pi-thinking.sh`, `hosts/alienpc/comfyui-remediation/`) and `REVIEW-NOTES.md` with open live checks (`stage-src` live usage and `switchyard` ownership). Left on its branch for Max/Derrick triage.
- `feature/alienpc-community-carryover` (`4122e40`): per `REVIEW-NOTES.md`, must be diffed against AlienPc's 131 uncommitted `C:\AI\community` changes before merging either.
- All Q2 old side branches (`main`, `x3-forge`, `x3-pi-config`, `x3-bakeoffs`, `feature/forge-coding-u57`, `job/2026-11-15-gitea-backup`, `evo-x3-all`, `feature/alienpc-only-remediation`, `feature/x3-community-u56`, `feature/x3-forge-u56`, `feature/x3-pi-config-u56`, `feature/x3-render-u56`, `feature/x3-u56-render-consolidated`): tags only (`archive/<branch>`) in S7 per Q2.

## Remaining live steps for Max (on box / X3 / AlienPc)

1. **Mirror from GitHub to Gitea:** fast-forward `u58` (`65fa220`) and push the new `mono` branch from GitHub (`origin`) into primary Gitea (`derrick/evo-x3`).
2. **S1 live checks (X3 + box):** run `SNAPSHOT_OUT=/tmp/evo-snap-test bash scripts/snapshot-live-setup.sh && rm -rf /tmp/evo-snap-test` under X3 lease; run `gitleaks git --log-opts="mono" --config .gitleaks.toml` on the box and add only the known `1f4004a` Home Assistant header fingerprints to `.gitleaksignore` (HA is down per Derrick 2026-11-19). Also run `git ls-files -ci --exclude-standard` on Linux `mono` to confirm expected non-secret hits (`x3/community/staging-flux-edit/.../v1/models.json` and historical `*.bak-*`).
3. **S1b symlink & worktree patches (on `mono`, under X3 lease):** patch the 8 `Path.resolve().parents[N]` / `ralph.sh` `git rev-parse --show-toplevel` & `[ -d "$HOME/AI/community/.git" ]` sites listed under A1 in `PLAN.md`, and verify with `pytest -q` + `resolve.py` + `ralph.sh` smoke tests.
4. **S2 AlienPc uncommitted changes (131 + 9):** quiesce AlienPc, filter out media / >5 MB files, run `gitleaks`, diff against `feature/alienpc-community-carryover` (`4122e40`), and land the clean delta directly under `alienpc/community/` and `alienpc/render/` on `mono` (and record final SHAs).
5. **S5 & S6 live switchovers (unified review Finding 9 applied):** run S5 on X3 as **Max or AlienPc Forge over SSH** (never X3 Forge on itself, since S5 renames `/home/evo/AI/forge`). Run S6 on AlienPc from a host shell after stopping ComfyUI, launchers, shells, AND **AlienPc Forge's pi panes** (whose skill links and global `AGENTS.md` point into `C:\AI\community`); verify AlienPc Forge skill links & `AGENTS.md` resolve after the junction swap, configure GCM, scrub `*.pre-mono` URL creds, and rotate the AlienPc Gitea token.
6. **S7 closeout:** clear leases, switch default branch to `mono` on Gitea + GitHub (Q1), create `archive/<branch>` tags (Q1/Q2), archive `derrick/alienpc-render` and `derrick/alienpc-community-pc` read-only (Q7), and write `records/monorepo-consolidation/RESULT.md`.
