#!/usr/bin/env bash
# Install scripts/gitleaks-pre-commit.sh into .git/hooks/pre-commit of one or more git repos.
# Usage:
#   bash scripts/install-gitleaks-precommit.sh [<repo_dir> ...]
#   bash scripts/install-gitleaks-precommit.sh --check [<repo_dir> ...]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SRC="$SCRIPT_DIR/gitleaks-pre-commit.sh"
[ -f "$HOOK_SRC" ] || { echo "MISSING $HOOK_SRC" >&2; exit 2; }

CHECK_ONLY=0
REPOS=()
for arg in "$@"; do
  if [ "$arg" = "--check" ]; then
    CHECK_ONLY=1
  else
    REPOS+=("$arg")
  fi
done
if [ "${#REPOS[@]}" -eq 0 ]; then
  REPOS+=("$(cd "$SCRIPT_DIR/.." && pwd)")
fi

rc=0
for repo in "${REPOS[@]}"; do
  common_dir="$(git -C "$repo" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -z "$common_dir" ]; then
    echo "SKIP not a git repo: $repo" >&2
    rc=1
    continue
  fi
  case "$common_dir" in
    /*) ;;
    *) common_dir="$repo/$common_dir" ;;
  esac
  hooks_dir="$common_dir/hooks"
  dst="$hooks_dir/pre-commit"

  if [ "$CHECK_ONLY" = 1 ]; then
    if [ -x "$dst" ] && grep -q "gitleaks-pre-commit.sh" "$dst" 2>/dev/null; then
      echo "OK pre-commit hook installed in $repo ($dst)"
    elif [ -L "$dst" ] && [ "$(readlink -f "$dst" 2>/dev/null || true)" = "$(readlink -f "$HOOK_SRC" 2>/dev/null || true)" ]; then
      echo "OK pre-commit hook symlinked in $repo ($dst)"
    else
      echo "MISSING pre-commit hook in $repo ($dst)"
      rc=1
    fi
    continue
  fi

  mkdir -p "$hooks_dir"
  if [ -e "$dst" ] && ! grep -q "gitleaks-pre-commit.sh" "$dst" 2>/dev/null; then
    bak="$dst.bak-$(date +%Y%m%d-%H%M%S)"
    cp -a "$dst" "$bak"
    echo "backed up existing hook -> $bak"
  fi
  cat > "$dst" <<EOF
#!/usr/bin/env bash
# Managed by scripts/install-gitleaks-precommit.sh
exec bash "$HOOK_SRC" "\$@"
EOF
  chmod 0755 "$dst" "$HOOK_SRC"
  echo "installed $dst -> $HOOK_SRC"
done
exit "$rc"
