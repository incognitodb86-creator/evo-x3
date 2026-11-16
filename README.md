# derrick/evo-x3

Private Gitea home for EVO-X3 infra: sanitized configs, records, scripts, and bench notes. Secrets stay in Vaultwarden and in `/etc/evo-x3/*.env` on the host (never in this repo).

- **Gitea:** https://qnap.tailf242b2.ts.net/derrick/evo-x3
- **Default branch:** `main`
- **Live host:** `derekboone@evo-x3-1.tailf242b2.ts.net`. The host directory `~/evo-x3` is the ops tree (bakeoff logs, tarballs, in-progress records). It is not a checkout of this repo.

## Layout

- `configs/` — live sanitized copies of `/etc/evo-x3/llama-swap.yaml`, the Open WebUI quadlet, `ttm.conf`, `llama-swap.service`, kernel args, and env file *names*. See `configs/README.md`.
- `stage/` — original Fedora/Windows stage tree. Production llama-swap, Open WebUI, and `ttm.conf` copies are kept identical to `configs/`.
- `scripts/` — host scripts (`download-models.sh`, `evo-host-setup.sh`, `evo-model-tests.py`, Serve checks, pi launchers). Pi launchers do not include Sydney's persona, chats, or memory.
- `records/` — unit records (U1–U22 and later).
- `ops/` — config-backup timer units and the gitleaks pre-push helper.
- `harness/` and `runs/` — harness settings and historical run artifacts (agy logs are gitignored).

## Git practice (EVO plan rev 10, G1–G8)

- One repo per project. This repo is X3 infra only. Render, Forge, pi user config, and `alienpc-community` stay in their own repos (the last already exists as `derrick/alienpc-community`). Do not put model weights here.
- Default branch is `main`. Intended protection (needs a Gitea admin / Household; bot-box has write, not admin): no force-push, no branch deletion; allowlist bot-box for direct push until that is comfortable, then merge through pull requests. Feature branches and PRs are the norm for code changes.
- One job, one branch, one worktree:

```bash
git fetch origin
git worktree add ../wt/<job> -b job/$(date +%Y-%m-%d)-<slug> origin/main
# when the PR is merged:
git worktree remove ../wt/<job>
git worktree prune
```

The plan's path is `../wt/<job>` and the branch name is `job/<date>-<slug>`.

- Small commits: one logical change, with the unit id in the message (for example `G1:`, `U22:`, `UB:`). The benchmark unit is **UB** (renamed in plan rev 10; it is not the U21 harness record).
- Never `git add -A`. Stage explicit paths, then check `git diff --cached --name-only`.
- Secret scan: `ops/gitleaks-pre-push.sh` (official gitleaks 8.30.1). A pre-push hook is installed at `.git/hooks/pre-push`. Abort on any hit.

## Re-sync (no new scheduled task)

From a clone or worktree of this repo, after the files you changed are committed:

```bash
git push origin HEAD
```

Then confirm:

```bash
~/.config/gitea-box/check-push.sh /workspace/evo-x3/repo
```

(If you are on a worktree, pass that worktree path instead.) The existing daily config-backup *timer* on the X3 is unchanged; this re-sync is a manual one-liner only.

To refresh live configs from the host (sanitize first; never copy `*.env` or `*.cred`):

```bash
# example: llama-swap yaml is already placeholder-only
scp derekboone@evo-x3-1.tailf242b2.ts.net:/etc/evo-x3/llama-swap.yaml configs/llama-swap.yaml
cp configs/llama-swap.yaml stage/config/llama-swap/config-production.yaml
```
