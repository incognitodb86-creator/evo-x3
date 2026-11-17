#!/usr/bin/env bash
# Launch Antigravity Orchestrator (Argon) to run U21 B1-B5 and U32 deep-research bake-off.
# No secrets in this script or on the command line.
set -u
export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
WD="/home/derekboone/evo-x3"
BRIEF="/home/derekboone/evo-x3/records/U21-agy-brief.md"
META="/home/derekboone/evo-x3/records/U21-agy.meta.txt"
LOG="/home/derekboone/evo-x3/records/U21-agy.log"
cd "$WD" || exit 1
PROMPT="Read and carry out /home/derekboone/evo-x3/records/U21-agy-brief.md in full. The B1-B5 protocol is /home/derekboone/evo-x3/records/U21-benchmark-protocol-rev9-8141f53.md, with method detail in /home/derekboone/evo-x3/records/2026-11-15-llm-benchmarking-methods.md. The deep-research bake-off is section 5 of /home/derekboone/evo-x3/records/coding-harness-research-20261115.md. Write records to /home/derekboone/evo-x3/records/U21-benchmarks-20261115.md and /home/derekboone/evo-x3/records/U32-deep-research-bakeoff-20261115.md. Follow every hard rule in the brief."
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
