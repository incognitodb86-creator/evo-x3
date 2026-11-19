#!/usr/bin/env bash
# Launch Antigravity for U56 (Render writer-pipeline fixes). Pattern = U55-agy-launch.sh.
# MODEL must be passed in the environment (no default, so nothing starts by accident). No secrets here or on argv.
set -u
MODEL="${MODEL:?set MODEL, e.g. gemini-4-hydrogen-high}"
export PATH="/home/derekboone/.local/bin:$PATH"
AGY="/home/derekboone/.local/bin/agy"
WD="/home/derekboone/evo-x3"
REC="/home/derekboone/evo-x3/records"
RUN="$REC/U56-render-writer-fixes"
BRIEF="$RUN/U56-agy-brief-20261117.md"
META="$REC/U56-agy.meta.txt"
LOG="$REC/U56-agy.log"
LEASE="$REC/status/$(date '+%Y-%m-%d-%H%M')-evo-x3-lease-taken-agy-u56-render-writer-fixes.md"
cd "$WD" || exit 1
mkdir -p "$REC/status"
cat > "$LEASE" <<L
---
type: lease-take
host: EVO-X3
holder: agy U56 (launched by Grok Bot for Derrick/Max)
taken: $(date '+%Y-%m-%d %H:%M') CT
---
# EVO-X3 lease taken: agy U56, Render writer-pipeline fixes
Scope: edits in /home/evo/AI/render and /home/evo/AI/community, dry writer tests on flash-next-uncensored only. Not touched: llama-swap, Halogen, renders, ComfyUI. Release when RESULT.md exists.
L
PROMPT="Read and carry out ${BRIEF} in full, in the order given. Follow every HARD RULE in it. When done or blocked, write ${RUN}/RESULT.md as the STOP CONDITION says, then stop."
{
  echo "start=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
  echo "model=${MODEL}"
  echo "cwd=${WD}"
  echo "brief=${BRIEF}"
  echo "lease_file=${LEASE}"
  echo "lease_line=holder=agy unit=U56 scope=render+community writer fixes taken=$(date '+%Y-%m-%d %H:%M') CT"
  echo "pid_wrapper=$$"
  echo "host=$(hostname)"
} > "$META"
set +e
"$AGY" -p "$PROMPT" \
  --model "$MODEL" \
  --mode auto \
  --dangerously-skip-permissions \
  --add-dir /home/derekboone/evo-x3 \
  --disable-slash-commands \
  --print-timeout 0 \
  >> "$LOG" 2>&1
CODE=$?
{ echo "exit_code=${CODE}"; echo "end=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"; } >> "$META"
REL="$REC/status/$(date '+%Y-%m-%d-%H%M')-evo-x3-lease-released-agy-u56-render-writer-fixes.md"
cat > "$REL" <<L
---
type: lease-release
host: EVO-X3
holder: agy U56
released: $(date '+%Y-%m-%d %H:%M') CT
---
# EVO-X3 lease released: agy U56
State left: see $RUN/RESULT.md (exit_code=${CODE}). Next holder: free.
L
exit "$CODE"
