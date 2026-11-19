#!/usr/bin/env bash
# Launch Antigravity (Gemini 4 Hydrogen High) for U45 path-fix commit + community merge.
# No secrets here or on argv.
set -u
export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
WD="/home/derekboone/evo-x3"
BRIEF="/home/derekboone/evo-x3/records/U45-pathfix-merge-brief-20261116.md"
META="/home/derekboone/evo-x3/records/U45-agy.meta.txt"
LOG="/home/derekboone/evo-x3/records/U45-agy.log"
cd "$WD" || exit 1
PROMPT="Read and carry out ${BRIEF} in full, in the order given. Follow every HARD RULE in it. When done or blocked, write /home/derekboone/evo-x3/records/U45-RESULT.md as the STOP CONDITION says, then stop."
{
  echo "start=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
  echo "model=gemini-4-hydrogen-high"
  echo "cwd=${WD}"
  echo "brief=${BRIEF}"
  echo "pid_wrapper=$$"
  echo "host=$(hostname)"
} > "$META"
set +e
"$AGY" -p "$PROMPT" \
  --model gemini-4-hydrogen-high \
  --mode auto \
  --dangerously-skip-permissions \
  --add-dir /home/derekboone/evo-x3 \
  --disable-slash-commands \
  --print-timeout 0 \
  >> "$LOG" 2>&1
CODE=$?
{ echo "exit_code=${CODE}"; echo "end=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"; } >> "$META"
exit "$CODE"
