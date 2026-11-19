#!/usr/bin/env bash
# Sync finished X3-queued and QNAP-mounted render outputs into /srv/renders and PixlStash (plan-v32 P4.7).
# 2026-11-19 (Max Architect, Derrick t2546u): only the RTX-upscaled final video goes to /srv/renders and PixlStash:
# a clip is taken only when its <tag>/render_ok.json has an "upscale" block; *_raw.mp4, temp files and contact
# sheets are never copied. QNAP side: read-only mount /mnt/qnap/renders (mnt-qnap-renders.automount), new runs only
# (run dirs newer than $QNAP_SINCE). SYNC_DRY=1 lists what would be copied and copies nothing.
set -euo pipefail

DEST="/srv/renders"
INBOX="/home/evo/AI/pixl-inbox"
IMPORT_PY="/home/evo/AI/pixlstash-tagging/import_inbox.py"
STATE_FILE="/home/evo/AI/_runs/sync-renders.seen"
QNAP_SINCE="/home/evo/AI/_runs/sync-renders.qnap-since"   # created once; older QNAP runs are not imported
DRY="${SYNC_DRY:-0}"
mkdir -p "$DEST" "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"
[ -e "$QNAP_SINCE" ] || touch "$QNAP_SINCE"
NEW=0

sync_one() {
  local run_id="$1" src="$2"
  local base dst
  base="$(basename "$src")"
  dst="$DEST/${run_id}_${base}"
  if grep -Fxq "$dst" "$STATE_FILE" 2>/dev/null || [ -e "$dst" ]; then
    return 0
  fi
  if [ "$DRY" = 1 ]; then echo "WOULD COPY $src -> $dst"; return 0; fi
  cp -p "$src" "$dst"
  if [ -d "$INBOX" ]; then
    cp -p "$src" "$INBOX/${run_id}_${base}"
  fi
  echo "$dst" >> "$STATE_FILE"
  NEW=$((NEW + 1))
}

# For each <run>/<tag>/render_ok.json with an "upscale" block, sync <run>/<clip> (the 2x file).
sync_runs() {   # run dirs on stdin
  local run tagdir ok clip
  while IFS= read -r run; do
    for ok in "$run"/*/render_ok.json; do
      [ -f "$ok" ] || continue
      jq -e '.upscale | type == "object"' "$ok" >/dev/null 2>&1 || continue
      tagdir="$(dirname "$ok")"
      clip="$(jq -r '.clip // empty' "$ok" | tr '\\' '/')"
      [ -n "$clip" ] || clip="$(basename "$tagdir")/$(basename "$tagdir").mp4"
      case "$clip" in *_raw.mp4|*.tmp.mp4|*..*) continue;; *.mp4) ;; *) continue;; esac
      [ -f "$run/$clip" ] && sync_one "$(basename "$run")" "$run/$clip"
    done
  done
}

# 1. X3-queued render outputs under ~/AI/community/runs/<run>/<tag>/
if [ -d /home/evo/AI/community/runs ]; then
  sync_runs < <(find /home/evo/AI/community/runs -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true)
fi

# 2. AlienPC runs on the QNAP renders share (read-only mount), new run dirs only
if [ -d /mnt/qnap/renders/runs ]; then
  sync_runs < <(find /mnt/qnap/renders/runs -mindepth 1 -maxdepth 1 -type d -newer "$QNAP_SINCE" 2>/dev/null || true)
fi

# 3. Import any newly staged files into PixlStash
if [ "$DRY" != 1 ] && [ "$NEW" -gt 0 ] && [ -f "$IMPORT_PY" ]; then
  /home/evo/.venvs/pixlstash/bin/python "$IMPORT_PY" >/dev/null 2>&1 || true
fi
