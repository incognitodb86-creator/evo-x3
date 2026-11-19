#!/usr/bin/env bash
# Local git pre-commit secret guard for EVO-X3 clones (Forge / pi-job / manual commits).
# 1. Refuses staged forbidden secret filenames (auth.json, mcp.json, models.json, .env, *.token, *.cred, *.secret, *.key, SSH keys).
# 2. Runs gitleaks on staged changes (with repo .gitleaks.toml if present).
# 3. Always runs a fast built-in regex scan on staged additions (defense-in-depth if gitleaks is absent).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# --- 1. Forbidden staged filenames (ignore *.example / *.template) ---
bad_names=()
while IFS= read -r -d '' f; do
  [ -n "$f" ] || continue
  base="$(basename "$f")"
  case "$base" in
    *.example|*.template|*.sample) continue ;;
    auth.json|mcp.json|models.json|models-store.json|.env|.env.*|*.env|*.token|*.cred|*.secret|*.key|id_rsa|id_rsa.*|id_ed25519|id_ed25519.*|*.pem|*.p12|*.pfx)
      bad_names+=("$f") ;;
  esac
done < <(git diff --cached --name-only --diff-filter=ACM -z 2>/dev/null || true)

if [ "${#bad_names[@]}" -gt 0 ]; then
  echo "PRE-COMMIT BLOCKED: forbidden secret filename(s) staged:" >&2
  printf '  - %s\n' "${bad_names[@]}" >&2
  echo "Unstage with: git restore --staged <path>" >&2
  exit 1
fi

# --- 2. gitleaks staged scan (supports both gitleaks <8.19 `protect` and >=8.19 `git --staged`) ---
if command -v gitleaks >/dev/null 2>&1; then
  cfg_args=()
  [ -f "$REPO_ROOT/.gitleaks.toml" ] && cfg_args=(--config "$REPO_ROOT/.gitleaks.toml")
  if gitleaks git --help >/dev/null 2>&1; then
    if ! gitleaks git --staged --no-banner --redact "${cfg_args[@]}" "$REPO_ROOT"; then
      echo "PRE-COMMIT BLOCKED: gitleaks detected a secret in staged changes." >&2
      exit 1
    fi
  else
    if ! gitleaks protect --staged --no-banner --redact "${cfg_args[@]}" -s "$REPO_ROOT"; then
      echo "PRE-COMMIT BLOCKED: gitleaks detected a secret in staged changes." >&2
      exit 1
    fi
  fi
fi

# --- 3. Built-in high-confidence staged diff scan (always runs; fails closed on obvious tokens/keys) ---
if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
  PY="$(command -v python3 || command -v python)"
  git diff --cached --unified=0 --no-color -- . ':(exclude)*.example' ':(exclude)*.template' 2>/dev/null | "$PY" -c '
import re, sys

pat = re.compile(
    r"(?i)("
    r"authorization:\s*bearer\s+[a-z0-9._-]{16,}|"
    r"gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|"
    r"tskey-[A-Za-z0-9-]{16,}|"
    r"sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    r")"
)
cur_file = ""
hits = []
for line in sys.stdin:
    if line.startswith("+++ b/"):
        cur_file = line[6:].strip()
    elif line.startswith("+") and not line.startswith("+++"):
        m = pat.search(line[1:])
        if m:
            hits.append((cur_file, m.group(0)[:18] + "..."))
if hits:
    print("PRE-COMMIT BLOCKED: high-confidence secret pattern in staged diff:", file=sys.stderr)
    for f, tok in hits[:10]:
        print(f"  - {f}: {tok}", file=sys.stderr)
    sys.exit(1)
'
fi
exit 0
