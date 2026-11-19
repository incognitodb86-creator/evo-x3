#!/usr/bin/env bash
# Hermes no-agent cron script (zero LLM calls, zero GPU contention): daily 08:00 CT morning lab digest.
# Installed at ~/.hermes/scripts/morning-digest.sh; stdout is delivered verbatim by Hermes cron.
set -euo pipefail

AI_ROOT="${EVO_AI_ROOT:-/home/evo/AI}"
INBOX="$AI_ROOT/pixl-inbox"
RUNS_DIR="$AI_ROOT/community/runs"
LOG_RUNS="$AI_ROOT/_runs"

unit_summary() {
  local u="$1"
  if ! command -v systemctl >/dev/null 2>&1; then echo "n/a"; return; fi
  local res ts
  res="$(systemctl --user show -p Result --value "$u" 2>/dev/null || echo unknown)"
  ts="$(systemctl --user show -p ExecMainExitTimestamp --value "$u" 2>/dev/null || echo never)"
  printf '%s (%s)' "${res:-unknown}" "${ts:-never}"
}

qnap_st="$(unit_summary evo-renders-qnap-nightly.service)"
wt_st="$(unit_summary evo-worktree-cleanup.service)"
wt_log="$(ls -1t "$LOG_RUNS"/stale-worktrees-*.log 2>/dev/null | head -n 1 || true)"
inbox_cnt="$( [ -d "$INBOX" ] && find "$INBOX" -maxdepth 1 -type f ! -name '.*' 2>/dev/null | wc -l | tr -d ' ' || echo 0 )"
imp_st="$(command -v systemctl >/dev/null 2>&1 && systemctl --user is-active pixl-import.service 2>/dev/null || echo idle)"
recent_runs="$( [ -d "$RUNS_DIR" ] && find "$RUNS_DIR" -mindepth 1 -maxdepth 1 -type d -mtime -1 2>/dev/null | wc -l | tr -d ' ' || echo 0 )"
disk_line="$(df -h / "$AI_ROOT" 2>/dev/null | awk 'NR>1{print $6": "$4" free ("$5" used)"}' | paste -sd '; ' - || true)"

echo "EVO-X3 Morning Digest ($(date '+%Y-%m-%d %H:%M %Z'))"
echo "- QNAP nightly copy: $qnap_st"
echo "- Worktree cleanup: $wt_st${wt_log:+ [log: $(basename "$wt_log")]}"
echo "- PixlStash inbox: $inbox_cnt pending (pixl-import: $imp_st)"
echo "- Runs in last 24h: $recent_runs"
echo "- Disk: ${disk_line:-unknown}"
