#!/usr/bin/env bash
# Launch Antigravity Orchestrator (Argon) to implement U31 audit fixes.
# No secrets in this script or on the command line.
set -u
export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
WD="/home/derekboone/evo-x3"
BRIEF="/home/derekboone/evo-x3/records/U31-agy-brief.md"
META="/home/derekboone/evo-x3/records/U31-agy.meta.txt"
LOG="/home/derekboone/evo-x3/records/U31-agy.log"
cd "$WD" || exit 1
PROMPT="Read and carry out /home/derekboone/evo-x3/records/U31-agy-brief.md in full. The review to implement is /home/derekboone/evo-x3/records/agy-redteam-review-20261115.md. Write the record to /home/derekboone/evo-x3/records/U31-agy-audit-fixes-20261115.md. Follow every hard rule in the brief."
START="$(date '+%Y-%m-%d %H:%M:%S')"
{
  echo "start=${START} America/Chicago"
  echo "model=gemini-pro-orchestrator-g1-pro"
  echo "cwd=${WD}"
  echo "brief=${BRIEF}"
  echo "pid_wrapper=$$"
  echo "host=$(hostname)"
} > "$META"
set +e
"$AGY" -p "$PROMPT" \
  --model gemini-pro-orchestrator-g1-pro \
  --mode auto \
  --dangerously-skip-permissions \
  --add-dir /home/derekboone/evo-x3 \
  --add-dir /home/derekboone/AI/render \
  --add-dir /home/derekboone/AI/community \
  --add-dir /home/derekboone/AI/forge \
  --add-dir /home/derekboone/.pi/agent \
  --disable-slash-commands \
  --print-timeout 0 \
  >> "$LOG" 2>&1
CODE=$?
set -e
{
  echo "exit_code=${CODE}"
  echo "end=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
} >> "$META"
exit "$CODE"
