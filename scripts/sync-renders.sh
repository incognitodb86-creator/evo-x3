#!/usr/bin/env bash
# Sync finished X3-queued and QNAP-mounted render outputs into /srv/renders and PixlStash (plan-v32 P4.7).
set -euo pipefail

DEST="/srv/renders"
INBOX="/home/evo/AI/pixl-inbox"
IMPORT_PY="/home/evo/AI/pixlstash-tagging/import_inbox.py"
STATE_FILE="/home/evo/AI/_runs/sync-renders.seen"
mkdir -p "$DEST" "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"

sync_one() {
  local run_id="$1"
  local src="$2"
  local base
  base="$(basename "$src")"
  local dst="$DEST/${run_id}_${base}"
  if grep -Fxq "$dst" "$STATE_FILE" 2>/dev/null || [ -e "$dst" ]; then
    return 0
  fi
  cp -p "$src" "$dst"
  if [ -d "$INBOX" ]; then
    cp -p "$src" "$INBOX/${run_id}_${base}"
  fi
  echo "$dst" >> "$STATE_FILE"
}

# 1. X3-queued render outputs under ~/AI/community/runs/*/clip/
if [ -d /home/evo/AI/community/runs ]; then
  while IFS= read -r f; do
    run_id="$(basename "$(dirname "$(dirname "$f")")")"
    sync_one "$run_id" "$f"
  done < <(find /home/evo/AI/community/runs -maxdepth 3 -path '*/clip/*' -type f \( -name '*.mp4' -o -name '*.png' -o -name '*.jpg' -o -name '*.webp' \) 2>/dev/null || true)
fi

# 2. AlienPC QNAP renders share (when mounted at /mnt/qnap/renders/runs)
if [ -d /mnt/qnap/renders/runs ]; then
  while IFS= read -r f; do
    run_id="$(basename "$(dirname "$(dirname "$f")")")"
    sync_one "$run_id" "$f"
  done < <(find /mnt/qnap/renders/runs -maxdepth 3 -path '*/clip/*' -type f \( -name '*.mp4' -o -name '*.png' -o -name '*.jpg' -o -name '*.webp' \) 2>/dev/null || true)
fi

# 3. Import any newly staged files into PixlStash
if [ -x "$IMPORT_PY" ] || [ -f "$IMPORT_PY" ]; then
  /home/evo/.venvs/pixlstash/bin/python "$IMPORT_PY" >/dev/null 2>&1 || true
fi
