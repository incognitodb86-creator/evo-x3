# UNI-APPLY-X3-F-PARITY RESULT (hook part of X4c only)

When: 2026-11-19 16:36–16:38 America/Chicago (CST)
Doer: max-x3lane. MCP wiring, Hermes config, ntfy, and gateway restart were not in scope (parent: hook part of X4c only; MCP waits). snapshot: pending Max. Rollback: not triggered. Did not fast-forward `/home/derekboone/evo-x3` (still `a383932`, which lacks `scripts/gitleaks-*.sh`).

## Step 0 — Backups — DONE (hook paths)
- No prior `.git/hooks/pre-commit` on `/home/derekboone/evo-x3` (only `pre-commit.sample`).
- Hook script copies kept in `/home/derekboone/.local/lib/evo-gitleaks/`:
  - `gitleaks-pre-commit.sh.bak-20261119-163751` (working hook, sha256 `11cba7e5b629c5f65e5cae60915d9651ebe6a97a0e47582b642de176b0204190`)
  - `gitleaks-pre-commit.sh.official-dfbfe3bb-broken` and `gitleaks-pre-commit.sh.orig-dfbfe3bb` (committed mono `5564e9df`/`a6018891` text, sha256 `dfbfe3bb665c23d7cf5233a6691c00a418a8d7a365f263d5f50b42c13d01ad4c`)

## Item 1 — gitleaks pre-commit hook — DONE (with noted hook-script fix)
- `/home/evo/AI/evo-x3` does not exist (S5 not applied). Hook installed only on the brief-named clone that exists: `/home/derekboone/evo-x3`.
- Installer and hook script live in `/home/derekboone/.local/lib/evo-gitleaks/` (stable path; not copied into the stale clone working tree). `install-gitleaks-precommit.sh` sha256 `d635c7f48cf62754571317332ada15d71dd72659fa3377424db0b0561d661a3d` (matches repo). Wrapper: `/home/derekboone/evo-x3/.git/hooks/pre-commit` execs `/home/derekboone/.local/lib/evo-gitleaks/gitleaks-pre-commit.sh`.
- `bash -n` on both scripts: pass. `bash …/install-gitleaks-precommit.sh --check /home/derekboone/evo-x3`: `OK pre-commit hook installed in /home/derekboone/evo-x3 (.../.git/hooks/pre-commit)`, rc=0.
- `command -v gitleaks`: `/usr/bin/gitleaks` version `8.30.0` (hook also has the built-in regex/filename guard).
- Official committed hook (`dfbfe3bb…`, a6018891 split-regex form `r"-"*5 + r"BEGIN … KEY" + r"-"*5` inside `python -c`) fails the built-in scan with: `SyntaxError: invalid syntax. Did you mean 'True'?` at `pat = re.compile(`. Verbatim clean-file result with that official text: `clean_rc=1` (would block good commits).
- Live hook therefore kept at sha256 `11cba7e5b629c5f65e5cae60915d9651ebe6a97a0e47582b642de176b0204190` (same script, that one regex written as a single raw-string literal so implicit concatenation is valid). Throwaway `/tmp` repo self-tests, then removed:
  - staged clean `.txt` -> rc=0
  - staged `auth.json` -> rc=1, `PRE-COMMIT BLOCKED: forbidden secret filename(s) staged:`
  - staged synthetic `ghp_…` string -> rc=1, `PRE-COMMIT BLOCKED: high-confidence secret pattern in staged diff:`

## Item 2 — Read-only MCP in Hermes — SKIPPED (MCP wiring waits; Hermes not restarted)

## Item 3 — ntfy morning-digest — SKIPPED (not in this apply)
