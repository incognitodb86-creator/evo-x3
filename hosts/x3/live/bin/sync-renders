#!/usr/bin/env bash
# Sync finished X3-queued and QNAP-mounted render outputs into /srv/renders and PixlStash (plan-v32 P4.7).
# 2026-11-19 (Max Architect, Derrick t2546u): only the RTX-upscaled final video goes to /srv/renders and PixlStash:
# a clip is taken only when its <tag>/render_ok.json has an "upscale" block; *_raw.mp4, temp files and contact
# sheets are never copied. QNAP side: read-only mount /mnt/qnap/renders (mnt-qnap-renders.automount), new runs only
# (run dirs newer than $QNAP_SINCE). SYNC_DRY=1 lists what would be copied and copies nothing.
# 2026-11-19 t2716u (Derrick): do not publish X3-queued finals to /mnt/qnap/renders/runs from this 2-minute sync.
# That copy runs once nightly at 03:30 via /usr/local/bin/evo-renders-qnap-nightly (supersedes t2555 for
# X3-queued runs). This script still imports AlienPc runs from the QNAP share read-only (section 2).
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
  # L2: grab one poster frame per clip into /srv/renders/<run_id>.jpg for chat preview.
  local poster="$DEST/${run_id}.jpg"
  if [ ! -e "$poster" ] && command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -nostdin -loglevel error -y -ss 0.5 -i "$dst" -frames:v 1 -q:v 3 "$poster" 2>/dev/null || true
  fi
  if [ -d "$INBOX" ]; then
    cp -p "$src" "$INBOX/${run_id}_${base}"
  fi
  echo "$dst" >> "$STATE_FILE"
  NEW=$((NEW + 1))
}

# For each <run>/<tag>/render_ok.json:
# - Video clips: require an "upscale" block, sync 2x .mp4 to /srv/renders and $INBOX (never *_raw.mp4).
# - Flux stills (job_type == "still"): copy finished .png/.jpg/.webp to $INBOX for PixlStash auto-import.
sync_still() {
  local run_id="$1" src="$2"
  local base dst
  base="$(basename "$src")"
  dst="$INBOX/${run_id}_${base}"
  if grep -Fxq "$dst" "$STATE_FILE" 2>/dev/null || [ -e "$dst" ]; then
    return 0
  fi
  if [ "$DRY" = 1 ]; then echo "WOULD IMPORT STILL $src -> $dst"; return 0; fi
  if [ -d "$INBOX" ]; then
    cp -p "$src" "$dst"
    echo "$dst" >> "$STATE_FILE"
    NEW=$((NEW + 1))
  fi
}

sync_runs() {   # run dirs on stdin
  local run tagdir ok clip jtype
  while IFS= read -r run; do
    for ok in "$run"/*/render_ok.json; do
      [ -f "$ok" ] || continue
      tagdir="$(dirname "$ok")"
      jtype="$(jq -r '.job_type // empty' "$ok" 2>/dev/null || true)"
      if [ "$jtype" = "still" ]; then
        clip="$(jq -r '.clip // .file // empty' "$ok" 2>/dev/null | tr '\\' '/')"
        [ -n "$clip" ] || clip="$(basename "$tagdir")/$(basename "$tagdir").png"
        case "$clip" in *contact_sheet*|*..* ) continue;; *.png|*.jpg|*.jpeg|*.webp) ;; *) continue;; esac
        [ -f "$run/$clip" ] && sync_still "$(basename "$run")" "$run/$clip"
        continue
      fi
      jq -e '.upscale | type == "object"' "$ok" >/dev/null 2>&1 || continue
      clip="$(jq -r '.clip // empty' "$ok" | tr '\\' '/')"
      [ -n "$clip" ] || clip="$(basename "$tagdir")/$(basename "$tagdir").mp4"
      case "$clip" in *_raw.mp4|*.tmp.mp4|*..*) continue;; *.mp4) ;; *) continue;; esac
      [ -f "$run/$clip" ] && sync_one "$(basename "$run")" "$run/$clip"
    done
  done
}

# 1. X3-queued render outputs under ~/AI/community/runs/<run>/<tag>/
#    QNAP publish of these finals is in evo-renders-qnap-nightly (Derrick t2716u).
if [ -d /home/evo/AI/community/runs ]; then
  sync_runs < <(find /home/evo/AI/community/runs -mindepth 1 -maxdepth 1 -type d 2>/dev/null || true)
fi

# 2. AlienPC runs on the QNAP renders share (read-only mount), new run dirs only
if [ -d /mnt/qnap/renders/runs ]; then
  sync_runs < <(find /mnt/qnap/renders/runs -mindepth 1 -maxdepth 1 -type d -newer "$QNAP_SINCE" 2>/dev/null || true)
fi

# 3. Import any staged or left-over files in $INBOX into PixlStash (ST3a + review #6: start whenever $INBOX has
#    files, not only when NEW>0, so timed-out batches retry on the next 2-min pass; detached transient user unit
#    survives oneshot exit; fixed unit name acts as lock: if pixl-import is active or exists, skip).
if [ "$DRY" != 1 ] && [ -f "$IMPORT_PY" ] && [ -d "$INBOX" ]; then
  if [ "$NEW" -gt 0 ] || [ -n "$(find "$INBOX" -maxdepth 1 -type f ! -name '.*' \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.webp' -o -iname '*.gif' -o -iname '*.mp4' -o -iname '*.webm' -o -iname '*.mov' \) -print -quit 2>/dev/null || true)" ]; then
    if ! systemctl --user is-active --quiet pixl-import.service 2>/dev/null; then
      systemd-run --user --unit=pixl-import --collect \
        --description="PixlStash inbox import" \
        /home/evo/.venvs/pixlstash/bin/python "$IMPORT_PY" >/dev/null 2>&1 || true
    fi
  fi
fi
