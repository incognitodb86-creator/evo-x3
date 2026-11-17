#!/usr/bin/env bash
# Template launcher for future Antigravity (agy) runs on EVO-X3 (U53 I11).
# Enforces per-run git worktree isolation + X3 lease-line metadata (see records/agy-launcher-convention.md
# and records/evo-x3-lease-README.md). No secrets here or on argv.
set -euo pipefail

UNIT="${UNIT:?set UNIT e.g. U54}"
BRIEF="${BRIEF:?set BRIEF e.g. /home/derekboone/evo-x3/records/U54-brief.md}"
TARGET_REPO="${TARGET_REPO:-}"          # e.g. /home/evo/AI/community (empty = no code worktree)
LEASE_FILE="${LEASE_FILE:-}"            # required for mutating runs (records/status/*-evo-x3-lease-taken-*.md)
LEASE_SCOPE="${LEASE_SCOPE:-unspecified}"
READ_ONLY="${READ_ONLY:-0}"             # set READ_ONLY=1 only for read-only inspection runs

export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
REC="/home/derekboone/evo-x3/records"
META="${REC}/${UNIT}-agy.meta.txt"
LOG="${REC}/${UNIT}-agy.log"

if [ "$READ_ONLY" != "1" ]; then
  [ -n "$LEASE_FILE" ] && [ -f "$LEASE_FILE" ] || {
    echo "REFUSED: mutating agy run requires an active LEASE_FILE (see records/evo-x3-lease-README.md)" >&2
    exit 2
  }
fi

LEASE_LINE="holder=agy unit=${UNIT} scope=${LEASE_SCOPE} taken=$(date '+%Y-%m-%d %H:%M') CT file=${LEASE_FILE:-read-only}"

WD="/home/derekboone/evo-x3"
WT_DIR=""
WT_BRANCH=""
if [ -n "$TARGET_REPO" ]; then
  REPO_ROOT="$(git -C "$TARGET_REPO" rev-parse --show-toplevel)"
  WT_BRANCH="agy/${UNIT}"
  WT_DIR="/home/derekboone/evo-x3/_worktrees/${UNIT}-$(basename "$REPO_ROOT")"
  mkdir -p "$(dirname "$WT_DIR")"
  if [ ! -d "$WT_DIR" ]; then
    git -C "$REPO_ROOT" worktree add -b "$WT_BRANCH" "$WT_DIR" HEAD
  fi
  WD="$WT_DIR"
fi

cd "$WD"
PROMPT="Read and carry out ${BRIEF} in full, in the order given. Follow every HARD RULE in it. When done or blocked, write ${REC}/${UNIT}-RESULT.md as the STOP CONDITION says, then stop."

{
  echo "start=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
  echo "model=gemini-4-hydrogen-high"
  echo "cwd=${WD}"
  echo "brief=${BRIEF}"
  echo "worktree=${WT_DIR:-none}"
  echo "branch=${WT_BRANCH:-none}"
  echo "lease_line=${LEASE_LINE}"
  echo "pid_wrapper=$$"
  echo "host=$(hostname)"
} > "$META"

ADD_DIRS=(--add-dir /home/derekboone/evo-x3)
[ -n "$WT_DIR" ] && ADD_DIRS+=(--add-dir "$WT_DIR")

set +e
"$AGY" -p "$PROMPT" \
  --model gemini-4-hydrogen-high \
  --mode auto \
  --dangerously-skip-permissions \
  "${ADD_DIRS[@]}" \
  --disable-slash-commands \
  --print-timeout 0 \
  >> "$LOG" 2>&1
CODE=$?
set -e
{ echo "exit_code=${CODE}"; echo "end=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"; } >> "$META"
exit "$CODE"
