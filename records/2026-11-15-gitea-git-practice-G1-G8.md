# G1–G8 Gitea backup and git practice (EVO plan rev 10)

- **When:** 2026-11-15, 6:12–6:17 PM CT (America/Chicago)
- **Owner:** Max Architect 3
- **Plan:** `40_projects/compute-expansion/plans/2026-11-11-evo-x3-setup-plan.md` rev 10 (commit 0657c4e). U10 rollback was not acted on (pending Derrick). The benchmark unit is **UB**, not U21 (U21 in this repo is the on-box harness record).
- **PR:** https://qnap.tailf242b2.ts.net/derrick/evo-x3/pulls/1 (`job/2026-11-15-gitea-backup` → `main`)
- **Branch tip:** `420a28a` (plus this record commit)
- **Gitleaks:** official 8.30.1 (`~/.local/bin/gitleaks`, sha256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` for the linux_x64 tarball). Pre-push hook ran on the branch push at 6:16 PM CT: 13 commits, ~396.86 KB, **no leaks found**.

## Pass tests

| # | Result | Evidence |
|---|---|---|
| G1 | **FAIL on `main` until PR #1 is merged; PASS on the job branch** | Live `/etc/evo-x3/llama-swap.yaml`, Open WebUI quadlet, `ttm.conf`, `llama-swap.service`, `comfy-submit.sh`, `verify-serve.sh`, and kernel args (`amdgpu.gttsize=122880 ttm.pages_limit=31457280`) diff clean against `configs/` and the refreshed `stage/config` production copies on this branch (re-checked 6:16 PM CT). `check-push.sh` on the worktree: `Gitea save OK`. On `main` (`ffbe362`) `config-production.yaml` is still the stale 7:48 AM CT copy the audit flagged. |
| G2 | **FAIL** | This job added host scripts and pi launchers. Still only on the X3 (left unstaged: other Max jobs mid-edit): `~/evo-x3/records/U23*`, `U24*`, `~/evo-x3/bakeoff/` (including RESULTS.md and u26), `~/evo-x3/harness-tests/`, download logs and the llama-swap tarball, `~/u6-262k` (UB long-context test in progress). `~/AI/forge` is not a git repo. `~/AI/render` is a git repo with only an `alienpc-bundle` remote. `derrick/x3-forge`, `derrick/x3-render`, and `derrick/x3-pi-config` do not exist; the box token is `write:repository` only and cannot create repos under `derrick` (POST `/orgs/derrick/repos` 403 needs `write:organization`; admin create 403 needs `write:admin`). Did not create them under `bot-box`. |
| G3 | **FAIL** | `main` `protected=false`. bot-box is a write collaborator, not admin. POST `/branch_protections` returned 403 (`user should be an owner or a collaborator with admin write`). A test force-push to `main` was **not** run: with protection off it would have been accepted and would rewrite `main`. Household or Derrick needs to set: no force-push, no deletion, allowlist bot-box for direct push (or disable direct push and merge through PRs). |
| G4 | **FAIL** (this job has PR #1; earlier jobs do not) | This job used `job/2026-11-15-gitea-backup` and opened PR #1. The last jobs on `main` (U22, U21 harness, U8, …) were pushed directly to `main` with no PR. |
| G5 | **PASS** (for this job; standing practice not yet used elsewhere) | `git worktree list`: `/workspace/evo-x3/repo` on `main`, `/workspace/evo-x3/wt/2026-11-15-gitea-backup` on `job/2026-11-15-gitea-backup`. Path and branch name match the plan (`../wt/<job>`, `job/<date>-<slug>`). Documented in `README.md`. The worktree stays until PR #1 is merged, then it should be removed and pruned. |
| G6 | **PASS** | `git ls-files` has no `*.gguf` / `*.safetensors` / `*.hgn` / `*.bin` / `.env` / `*.cred` / `auth.json`. Tracked tree is 93 files, **620K** (`git count-objects` pack 114.34 KiB). `.gitignore` now also covers weights, env/key files, sessions, caches, and archives. |
| G7 | **PASS** on this clone | Hook present at `/workspace/evo-x3/repo/.git/hooks/pre-push` (from `ops/hooks/pre-push`). Last push (6:16 PM CT) ran gitleaks 8.30.1, no leaks. Hook is local to this clone; other clones need the same install. |
| G8 | **FAIL** | Spot check of the last 10 commits on this branch: five new commits (G5, G7, G2, G1, G6) and U22 / U21 / U8 each name one unit. `c355fee` names U2 but also "Fedora morning closeout". `1758d47` has no unit id and bundles records, production config, and model tests. On `main`, `8b2aff5`, `ced14a6`, and `2e9c8b0` also lack a unit id. |

## Repos

| Repo | Action | URL |
|---|---|---|
| `derrick/evo-x3` | Reused (already existed). Branch pushed; PR #1 opened. | https://qnap.tailf242b2.ts.net/derrick/evo-x3 |
| `derrick/alienpc-community` | Reused; **not** updated. X3 `~/AI/community` `x3-linux` (`82aabc4`) does not contain Gitea `main` (`c6954e89`). No push, no second community repo. | https://qnap.tailf242b2.ts.net/derrick/alienpc-community |
| `derrick/x3-forge` | **Not created** (token cannot create under `derrick`). | — |
| `derrick/x3-render` | **Not created** (same). | — |
| `derrick/x3-pi-config` | **Not created** (same). `~/.pi/agent/models.json` has a literal `apiKey`; do not commit it unsanitized. `auth.json`, sessions, and memory were not copied. | — |

## Needs Derrick (or Household)

1. Create private Gitea repos `derrick/x3-forge`, `derrick/x3-render`, and `derrick/x3-pi-config` (or grant a token that can create under `derrick`). Do not paste a token into chat; Household can mint one or create the empty repos.
2. Set `main` branch protection on those repos and on `derrick/evo-x3`: no force-push, no deletion; allowlist bot-box or require PRs.
3. Merge PR #1 when ready (it is mergeable; gitleaks was clean). Until then, `main` still has the stale production yaml.
4. Later: a planned merge of X3 `x3-linux` into `derrick/alienpc-community` (histories currently diverge). Do not force-push.

Re-sync for this repo: `git push origin HEAD`, then `~/.config/gitea-box/check-push.sh <repo-or-worktree>`. No new scheduled task was added.
