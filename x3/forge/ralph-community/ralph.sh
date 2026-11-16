#!/usr/bin/env bash
# Plain capped Ralph loop for Forge on the EVO-X3 (bash port of the AlienPc Windows Ralph runner; same behavior).
# Runs pi --print on PROMPT.md, one fix_plan item per pass, stops at PLAN_COMPLETE, NO_PROGRESS or the -Max cap.
# Max Architect 2026-11-15, X3 Phase 2 (Derrick t1784s6566 "port ralph-loop to Linux"). Forge owns this file.
# Usage: ralph.sh [-Max 10] [-Model x3-local/flash-next] [-PassLimitSec 3600] [-IterationTimeoutSec 7200]
#                 [-GpuWaits 30] [-GpuWaitSec 120] [-GpuLockPath <lock>] [-LockPollSec 2]
#                 [-MemoryRoot <dir>] [-WorkDir <pi cwd>] [-CommandOverride <cmd>] [-LogPath <path>]
# Start detached: nohup setsid bash ralph.sh -Max N >/dev/null 2>&1 &
# Exit codes: 0 done/capped, 4 another copy running, 5 bad args.
set -uo pipefail
Max=10; Model='x3-local/flash-next'; GpuWaits=30; GpuWaitSec=120
GpuLockPath="$HOME/AI/locks/gpu-render.lock"; IterationTimeoutSec=7200; CommandOverride=''; LogPath=''
PassLimitSec=3600; LockPollSec=2; MemoryRoot="$HOME/AI/fleet-brain/25_memory/shared"; WorkDir="$HOME/AI/forge"
while [ $# -gt 0 ]; do
  case "$1" in
    -Max|--max) Max="$2"; shift 2;;
    -Model|--model) Model="$2"; shift 2;;
    -GpuWaits) GpuWaits="$2"; shift 2;;
    -GpuWaitSec) GpuWaitSec="$2"; shift 2;;
    -GpuLockPath) GpuLockPath="$2"; shift 2;;
    -IterationTimeoutSec) IterationTimeoutSec="$2"; shift 2;;
    -PassLimitSec|--pass-limit-sec) PassLimitSec="$2"; shift 2;;
    -LockPollSec) LockPollSec="$2"; shift 2;;
    -MemoryRoot|--memory-root) MemoryRoot="$2"; shift 2;;
    -WorkDir) WorkDir="$2"; shift 2;;
    -CommandOverride) CommandOverride="$2"; shift 2;;
    -LogPath) LogPath="$2"; shift 2;;
    *) echo "unknown arg $1" >&2; exit 5;;
  esac
done
K="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$K" || exit 5
day=$(date +%Y%m%d)
if [ -n "$LogPath" ]; then logDir="$(dirname "$(realpath -m "$LogPath")")"; idx="$(realpath -m "$LogPath")"
elif [ -n "$CommandOverride" ]; then logDir="${TMPDIR:-/tmp}/ralph_override_$$"; idx="$logDir/ralph.log"
else logDir="$K/logs"; idx="$logDir/ralph.log"; fi
mkdir -p "$K/logs" "$K/sessions" "$K/notes" "$logDir"
run="$logDir/ralph-$day-$$.log"
log() { local l; l="$(date +%Y-%m-%dT%H:%M:%S) $*"; printf '%s\n' "$l" >>"$idx"; printf '%s\n' "$l" >>"$run"; printf '%s\n' "$l"; }
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
export PATH="$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH"
# The model key is read by pi's models.json (!command from /etc/evo-x3); this script never reads or exports it.
lock="$K/logs/ralph.lock"
if [ -f "$lock" ]; then
  lp="$(tr -dc '0-9' <"$lock")"
  if [ -n "$lp" ] && [ "$lp" != "$$" ] && kill -0 "$lp" 2>/dev/null; then log "ALREADY_RUNNING pid $lp - second loop not started"; exit 4; fi
  log "stale ralph.lock (pid ${lp:-?} not alive) - taking it"
fi
echo $$ >"$lock"
trap 'rm -f "$lock"' EXIT
stall=0; stopReason=''

# GPU lock rule: test with flock -n (same as queue-remote.sh / remote_comfy.py).
# A 0-byte or unlocked file is free; only an active flock is busy.
lock_pid() { [ -f "$GpuLockPath" ] || { echo 0; return; }; local p; p="$(grep -oE '[0-9]+' "$GpuLockPath" | head -1)"; echo "${p:--1}"; }
gpu_busy() {
  [ -e "$GpuLockPath" ] || return 1
  if ! flock -n "$GpuLockPath" true 2>/dev/null; then
    local p; p="$(lock_pid)"
    if [ "$p" -gt 0 ] 2>/dev/null; then
      BUSY="flock held on $GpuLockPath (pid $p)"
    else
      BUSY="flock held on $GpuLockPath"
    fi
    return 0
  fi
  return 1
}
in_tree() { # $1 child pid, $2 root pid
  local cur="$1" n=0
  while [ "$n" -lt 32 ] && [ "${cur:-0}" -gt 0 ]; do
    [ "$cur" = "$2" ] && return 0
    cur="$(ps -o ppid= -p "$cur" 2>/dev/null | tr -d ' ')"; n=$((n+1))
  done
  return 1
}
kill_tree() { # kill the pass's whole process group (pass runs under setsid)
  kill -TERM -- "-$1" 2>/dev/null; sleep 3; kill -KILL -- "-$1" 2>/dev/null
}
top_item() {
  local t; t="$(grep -m1 -E '^\s*- \[ \]' "$K/fix_plan.md" 2>/dev/null | sed -E 's/^\s+//')"
  [ -z "$t" ] && { echo '(none)'; return; }; echo "${t:0:90}"
}
mtime() { stat -c %Y "$1" 2>/dev/null || echo 0; }

for ((i=1; i<=Max; i++)); do
  log "iter $i of $Max start"
  gpuWait=0; BUSY=''
  while gpu_busy && [ "$gpuWait" -lt "$GpuWaits" ]; do
    if [ "$gpuWait" -eq 0 ] || [ $((gpuWait % 5)) -eq 0 ]; then log "iter $i : GPU_BUSY defers the pass ($BUSY) - no LLM request while a GPU job runs; waited $gpuWait of $GpuWaits"; fi
    sleep "$GpuWaitSec"; gpuWait=$((gpuWait+1))
  done
  if gpu_busy; then log "iter $i : GPU_DEFERRED - the GPU window outlasted $GpuWaits waits ($BUSY); skipping this pass, no LLM request"; continue; fi
  [ "$gpuWait" -gt 0 ] && log "iter $i : GPU_CLEAR after $gpuWait waits"

  iterLog="$(printf '%s/iter-%s-%02d.log' "$logDir" "$day" "$i")"; iterTmp="${iterLog%.log}.tmp.log"; rm -f "$iterTmp"
  hb="$K/notes/heartbeat.txt"; prog="$K/notes/progress.md"
  topItem="$(top_item)"
  if [ "$topItem" = '(none)' ]; then log "iter $i : PLAN_COMPLETE - no open item, loop stopped"; echo "iter=$i max=$Max done=true reason=plan_complete" >"$logDir/DONE.txt"; stopReason=plan_complete; break; fi
  progBefore="$(mtime "$prog")"
  passCap=$(( PassLimitSec < IterationTimeoutSec ? PassLimitSec : IterationTimeoutSec ))
  echo "$(date +%Y-%m-%dT%H:%M:%S) iter=$i state=start cap=${passCap}s item=$topItem" >"$hb"
  # Shared fleet memory for this pass only (process scope; Sydney's sessions never see it).
  export PI_MEMORY_DIR="$MemoryRoot"; mkdir -p "$MemoryRoot"
  log "iter $i : PI_MEMORY_DIR=$PI_MEMORY_DIR (process scope, this pass only)"
  if [ -n "$CommandOverride" ]; then
    setsid bash -c "cd \"$K\" && $CommandOverride" >"$iterTmp" 2>&1 &
  else
    setsid bash -c 'cd "$1" && exec pi --approve --print --model "$2" --no-session "@$3/PROMPT.md"' _ "$WorkDir" "$Model" "$K" >"$iterTmp" 2>&1 &
  fi
  pp=$!; start=$(date +%s); lockEnd=''; timedOut=0
  while kill -0 "$pp" 2>/dev/null; do
    sleep "$LockPollSec"
    if gpu_busy; then lp="$(lock_pid)"; if [ "$lp" -le 0 ] || ! in_tree "$lp" "$pp"; then lockEnd="$BUSY"; break; fi; fi
    if [ $(( $(date +%s) - start )) -ge "$passCap" ]; then timedOut=1; break; fi
  done
  if [ -n "$lockEnd" ]; then
    log "iter $i : GPU_LOCK_MIDPASS ($lockEnd) - GPU window opened outside this pass; ending the pass now (pi tree PID $pp)"
    kill_tree "$pp"; wait "$pp" 2>/dev/null; piRc=125
  elif [ "$timedOut" = 1 ]; then
    log "iter $i : ITERATION_TIMEOUT after ${passCap}s - killing process tree PID $pp..."
    kill_tree "$pp"; wait "$pp" 2>/dev/null; piRc=124
  else
    wait "$pp"; piRc=$?
  fi
  [ -f "$iterTmp" ] && mv -f "$iterTmp" "$iterLog"
  if [ "$piRc" -ne 0 ]; then log "iter $i : PI_NONZERO rc=$piRc - pass text in $iterLog"; else log "iter $i : pass complete rc=0"; fi
  sha="$(git -C "$K" rev-parse --short HEAD 2>/dev/null)"
  if [ "$(mtime "$prog")" -le "$progBefore" ]; then echo "- $(date +%Y-%m-%dT%H:%M:%S) [ralph.sh auto] iter $i rc=$piRc head=$sha item: $topItem (model wrote no progress line)" >>"$prog"; log "iter $i : progress line written by harness"; fi
  echo "$(date +%Y-%m-%dT%H:%M:%S) iter=$i state=end rc=$piRc head=$sha item=$topItem" >"$hb"
  echo "iter=$i max=$Max pi_rc=$piRc gpu_wait=$gpuWait" >"$logDir/DONE.txt"
  afterItem="$(top_item)"
  if [ "$afterItem" != '(none)' ] && [ "$afterItem" = "$topItem" ]; then stall=$((stall+1)); else stall=0; fi
  if [ "$stall" -ge 2 ]; then log "iter $i : NO_PROGRESS on same item twice - stopped ($topItem)"; echo "iter=$i max=$Max done=true reason=no_progress" >"$logDir/DONE.txt"; stopReason=no_progress; break; fi
  sleep 2
done
if [ -z "$stopReason" ]; then
  # a final check so a plan finished on the last pass reports PLAN_COMPLETE
  if [ "$(top_item)" = '(none)' ]; then log "PLAN_COMPLETE - no open item after the last pass"; echo "iter=$Max max=$Max done=true reason=plan_complete" >"$logDir/DONE.txt"
  else log "max iterations ($Max) reached - loop stopped at cap"; echo "iter=$Max max=$Max done=true" >"$logDir/DONE.txt"; fi
fi
exit 0
