#!/bin/sh
# Secret scan for derrick/evo-x3. Uses a user-local official gitleaks binary.
set -e
GITLEAKS="${GITLEAKS:-$HOME/.local/bin/gitleaks}"
if [ ! -x "$GITLEAKS" ]; then
  # also try PATH
  if command -v gitleaks >/dev/null 2>&1; then
    GITLEAKS=$(command -v gitleaks)
  else
    echo "gitleaks not found; install the official Linux amd64 binary to ~/.local/bin/gitleaks" >&2
    exit 1
  fi
fi
root=$(git rev-parse --show-toplevel)
cd "$root"
# Scan the git history of this repo (all commits). Redact any findings in output.
"$GITLEAKS" git --redact --verbose
echo "gitleaks clean: $($GITLEAKS version 2>/dev/null || echo unknown)"
