#!/usr/bin/env bash
# Launch Antigravity (Hydrogen Medium) for U54 Forge batch.
# No secrets here or on argv.
set -u
export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
WD="/home/derekboone/evo-x3"
BRIEF="/home/derekboone/evo-x3/records/U54-agy-brief-20261116.md"
META="/home/derekboone/evo-x3/records/U54-agy.meta.txt"
LOG="/home/derekboone/evo-x3/records/U54-agy.log"
cd "$WD" || exit 1
PROMPT="Read and carry out ${BRIEF} in full, in the order given. Follow every HARD RULE in it. When done or blocked, write /home/derekboone/evo-x3/records/U54-RESULT.md as the STOP CONDITION says, then stop."
{
  echo "start=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
  echo "model=gemini-4-hydrogen-medium"
  echo "cwd=${WD}"
  echo "brief=${BRIEF}"
  echo "pid_wrapper=$$"
  echo "host=$(hostname)"
} > "$META"
set +e
"$AGY" -p "$PROMPT" \
  --model gemini-4-hydrogen-medium \
  --mode auto \
  --dangerously-skip-permissions \
  --add-dir /home/derekboone/evo-x3 \
  --disable-slash-commands \
  --print-timeout 0 \
  >> "$LOG" 2>&1
CODE=$?
{ echo "exit_code=${CODE}"; echo "end=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"; } >> "$META"
exit "$CODE"
