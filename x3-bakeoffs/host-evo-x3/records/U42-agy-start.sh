#!/usr/bin/env bash
# One-shot starter: setsid/nohup the U42 launch script. No secrets.
set -euo pipefail
WD=/home/derekboone/evo-x3
REC="$WD/records"
LAUNCH="$REC/U42-agy-launch.sh"
LOG="$REC/U42-agy.log"
WLOG="$REC/U42-agy-wrapper.log"
PIDF="$REC/U42-agy-wrapper.pid"

already=0
while read -r pid cmd; do
  [ -z "${pid:-}" ] && continue
  if [ "$pid" = "$$" ] || [ "$pid" = "$PPID" ]; then
    continue
  fi
  echo "EXISTING pid=$pid cmd=$cmd"
  already=1
done < <(ps -u derekboone -o pid=,args= | awk '/U42-agy-launch\.sh/ || (/\/.local\/bin\/agy( |$)/ && /U42-pixlstash-tagging-brief/ ) {print}')

if [ "$already" -eq 1 ]; then
  echo "ALREADY RUNNING; not launching a second copy" >&2
  exit 1
fi

: > "$LOG"
: > "$WLOG"
cd "$WD"
setsid nohup "$LAUNCH" </dev/null >> "$WLOG" 2>&1 &
WPID=$!
echo "$WPID" > "$PIDF"
sleep 1
echo "wrapper_pid=$WPID"
echo "launch_time=$(date '+%Y-%m-%d %H:%M:%S') America/Chicago"
if ps -p "$WPID" >/dev/null 2>&1; then
  ps -p "$WPID" -o pid,lstart,cmd
else
  echo "captured pid $WPID exited; looking for launch.sh / agy"
fi
echo "=== related procs ==="
ps -u derekboone -o pid,lstart,cmd | awk '/U42-agy/ || (/\/.local\/bin\/agy( |$)/ && /U42/)'
echo "=== meta ==="
cat "$REC/U42-agy.meta.txt" 2>/dev/null || echo "meta not yet"
ls -la "$LOG" "$WLOG" "$PIDF" "$REC/U42-agy.meta.txt" 2>/dev/null || true
