Goal: After `UNI-APPLY-X3-E-HERMES` has a `RESULT.md`, install the local `gitleaks` pre-commit secret guard on the X3 `mono` clone, wire read-only MCP servers (Gitea, plus Google Workspace / UniFi only if their creds are filled) into Hermes for GrokBot parity, and optionally enable `ntfy` push on the morning digest, under the X3 lease.

# UNI-APPLY-X3-F-PARITY (X3 Forge): gitleaks pre-commit guard + read-only Hermes MCPs + ntfy digest, Nov 19 2026

Authority: Derrick 2026-11-19 15:34 / 15:50 CT ("i want grokbot parity with our setup" -> "2 & 3": Hermes GrokBot-parity pack + X3 `gitleaks` pre-commit hook). Plans: `records/uplan/PLAN.md` (step `X4c`) and `records/hermes-direct-render/PLAN.md`. Max verifies your `RESULT.md` afterwards.

## Needs before launch (ALL required)
- `/home/derekboone/evo-x3/records/UNI-APPLY-X3-E-HERMES/RESULT.md` exists. If not, stop (`BLOCKED`) without taking the lease.
- Max pulled `mono` (this brief's commit or newer) into `/home/derekboone/evo-x3` and `/home/evo/AI/evo-x3`.
- X3 lease free (`/home/derekboone/AI/locks/x3-lease.txt` empty). No render running. Not during the `BENCH-X3-W1` quiet window. No Hermes chat mid-turn.

## Access & Lease
- **Doer:** X3 Forge as `evo`. No sudo needed. (Max installs the pre-commit hook into `/home/derekboone/evo-x3` separately as `derekboone` during closeout.)
- **Source:** `/home/evo/AI/evo-x3/scripts/{gitleaks-pre-commit.sh,install-gitleaks-precommit.sh}`, `/home/derekboone/evo-x3/hosts/x3/hermes/mcp-servers.readonly.yaml.example`.
- **Backup root:** `/home/evo/.hermes/_archive/20261119-x3-f/`.
- **Lease take:** ONE line `forge-x3 | UNI-APPLY-X3-F-PARITY | <start time>` in `/home/derekboone/AI/locks/x3-lease.txt` (stop if not empty).
- **Lease release:** `: > /home/derekboone/AI/locks/x3-lease.txt` when done or blocked.

## Work (stop on first failure)

### Step 0 - Backups
```bash
B=/home/evo/.hermes/_archive/20261119-x3-f; mkdir -p "$B"
cp -a /home/evo/.hermes/config.yaml "$B/config.yaml"
[ -f /home/evo/AI/evo-x3/.git/hooks/pre-commit ] && cp -a /home/evo/AI/evo-x3/.git/hooks/pre-commit "$B/pre-commit.before"
```

### Item 1 - Install `gitleaks` pre-commit hook on `/home/evo/AI/evo-x3`
- Install and verify:
  ```bash
  bash -n /home/evo/AI/evo-x3/scripts/gitleaks-pre-commit.sh /home/evo/AI/evo-x3/scripts/install-gitleaks-precommit.sh
  bash /home/evo/AI/evo-x3/scripts/install-gitleaks-precommit.sh /home/evo/AI/evo-x3
  bash /home/evo/AI/evo-x3/scripts/install-gitleaks-precommit.sh --check /home/evo/AI/evo-x3
  ```
- Self-test in a throwaway `/tmp` git repo (never leave test commits in `evo-x3`):
  1. Stage a clean `.txt` file -> `bash /home/evo/AI/evo-x3/scripts/gitleaks-pre-commit.sh` exits `0`.
  2. Stage a file named `auth.json` -> exits `1` (`PRE-COMMIT BLOCKED: forbidden secret filename`).
  3. Stage a file containing a synthetic `ghp_...` string -> exits `1` (`PRE-COMMIT BLOCKED`).
  4. Remove the `/tmp` test repo.
- Record whether `command -v gitleaks` is present in `RESULT.md` (hook still runs the filename + regex guard if `gitleaks` is absent).

### Item 2 - Read-only MCP servers in Hermes (GrokBot parity; ZERO Vaultwarden)
- Check live wrappers in `/home/evo/.config/forge-mcp/` (never print `.env` or token contents; check file existence/non-empty only):
  - `gitea`: `/home/evo/.config/forge-mcp/run-gitea-mcp.sh` + `/home/evo/.config/forge-mcp/GITEA_ACCESS_TOKEN` non-empty -> **enable read-only**.
  - `google-workspace`: enable ONLY if `/home/evo/.config/forge-mcp/run-google-workspace-mcp.sh` exists AND `google-creds/` is non-empty (not placeholder). Otherwise leave commented/disabled and note `SKIPPED (placeholder creds)`.
  - `unifi`: enable ONLY if `/home/evo/.config/forge-mcp/run-unifi-mcp.sh` exists AND `unifi.env` is populated (no placeholder `CHANGE_ME` / blank host; check with `grep -q` without printing values). Otherwise leave commented/disabled and note `SKIPPED (placeholder creds)`.
  - **NEVER add `vaultwarden`** to Hermes `config.yaml`.
- Apply via `hermes config set` (matching `hosts/x3/hermes/mcp-servers.readonly.yaml.example`):
  ```bash
  hermes config set mcp_servers.gitea '{"command":"/home/evo/.config/forge-mcp/run-gitea-mcp.sh","args":["--host","https://qnap.tailf242b2.ts.net","--read-only"],"tools":{"exclude":["*create*","*update*","*delete*","*merge*","*fork*","*push*","*write*","*edit*","*add*","*remove*"]}}'
  ```
  (Add `mcp_servers.google-workspace` and/or `mcp_servers.unifi` with the exact `tools.exclude` lists from `mcp-servers.readonly.yaml.example` ONLY if their credential check above passed.)
- Restart gateway only when no chat is mid-turn: `systemctl --user restart hermes-gateway`; verify `systemctl --user is-active hermes-gateway` is `active`.
- Verify read-only tools: run `hermes mcp list` (or `hermes doctor` / gateway log check) and confirm `gitea` connects with **zero** create/delete/push/write/merge tools exposed.

### Item 3 - Optional `ntfy` push test on `morning-digest.sh`
- Check `/home/evo/.config/evo-x3/ntfy-x3.token` exists and is `0600` (`stat -c '%a'`). Never print it.
- Run a plain stdout smoke (no push): `bash /home/evo/.hermes/scripts/morning-digest.sh` -> 6 lines printed, exit 0.
- If `morning-lab-digest` cron exists and Derrick wants phone push enabled, update the cron script env (`MORNING_DIGEST_NTFY=1`) or leave default stdout-only (WebUI/gateway delivery) and note which is active.

### Rollback
```bash
B=/home/evo/.hermes/_archive/20261119-x3-f
cp -a "$B/config.yaml" /home/evo/.hermes/config.yaml
rm -f /home/evo/AI/evo-x3/.git/hooks/pre-commit
[ -f "$B/pre-commit.before" ] && cp -a "$B/pre-commit.before" /home/evo/AI/evo-x3/.git/hooks/pre-commit
systemctl --user restart hermes-gateway
```

## Closeout (Max only, after `RESULT.md`)
- As `derekboone`: run `bash /home/derekboone/evo-x3/scripts/install-gitleaks-precommit.sh /home/derekboone/evo-x3`, refresh snapshots (`scripts/snapshot-live-setup.sh`), run `gitleaks`, and commit `RESULT.md` + snapshots on `mono`.

## Rules
- Stop on first failure. No renders, no `llama-swap.yaml` edits, no Vaultwarden MCP in Hermes, never read or print secret/token/`.env` contents.
- Cite `mono` SHAs in `RESULT.md`.

STOP CONDITION: when done or blocked, write `/home/derekboone/evo-x3/records/UNI-APPLY-X3-F-PARITY/RESULT.md`, release the lease, and stop. List Step 0 and Items 1-3 as `DONE`, `BLOCKED`, or `SKIPPED` with exact check outputs, MCP tool counts, backup paths, and `snapshot: pending Max`.
