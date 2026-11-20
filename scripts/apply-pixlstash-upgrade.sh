#!/usr/bin/env bash
# apply-pixlstash-upgrade.sh — Deploy PX1 (diverse PixlStash picker + Hermes skills) & PX2 (persist 14G/16G memcap),
# inspect PixlStash health/dedup/penalised-tags (--status), and optionally create orientation Smart Sets (PX3).
#
# Authority: Derrick 2026-11-20 ~09:56-10:01 AM CT (smart score >= 2.2 floor only, never sort; ST3c memcap; PixlStash 2.0).
# Plan: records/PIXLSTASH-UPGRADE-20261120/PLAN.md
#
# Usage:
#   bash scripts/apply-pixlstash-upgrade.sh --status                       # read-only: memcap, dedup counts, penalised tags
#   bash scripts/apply-pixlstash-upgrade.sh --dry-run                      # default: preview PX1 + PX2 changes
#   bash scripts/apply-pixlstash-upgrade.sh --apply                        # take X3 lease, back up, install PX1 + PX2
#   bash scripts/apply-pixlstash-upgrade.sh --create-smart-sets            # preview the 4 PX3 Smart Set definitions
#   bash scripts/apply-pixlstash-upgrade.sh --create-smart-sets --apply [--token-file <path>]
#                                          # PX1+PX2, then list existing sets + print the 4 to create (no POST:
#                                          # the v2.0.1 Smart Set filter schema is unverified; create them in the UI)
#   bash scripts/apply-pixlstash-upgrade.sh --rollback                     # restore backups

set -euo pipefail

MODE="dry-run"
DO_SMART_SETS=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LEASE_FILE="/home/derekboone/AI/locks/x3-lease.txt"
HERMES_HOME_DIR="/home/evo/.hermes"
BAK_DIR="/home/evo/AI/_archive/20261120-pixlstash-upgrade"
MEMCAP_DST="/home/evo/.config/systemd/user/pixlstash.service.d/10-memcap.conf"
PICKER_DST="/home/evo/AI/render/x3/still_candidate_sheet.py"
PICKER_TEST_DST="/home/evo/AI/render/x3/test_still_candidate_sheet.py"
READ_TOKEN_FILE="/home/evo/.config/pixlstash/render-read.token"
WRITE_TOKEN_FILE="${PIXL_WRITE_TOKEN_FILE:-$READ_TOKEN_FILE}"
# dedup/counts is write-scoped (read token gets 403 "Token is read-only"); used ONLY for that status call.
DEDUP_TOKEN_FILE="${PIXL_DEDUP_TOKEN_FILE:-/home/evo/.config/pixlstash/tagger-write.token}"
PIXL_URL="http://127.0.0.1:9537"
PY_EVO="/home/evo/AI/render/x3/.venv/bin/python3"
STAGE_DIR=""
LEASE_HELD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --apply) MODE="apply"; shift ;;
    --rollback) MODE="rollback"; shift ;;
    --status) MODE="status"; shift ;;
    --create-smart-sets) DO_SMART_SETS=1; shift ;;
    --token-file) WRITE_TOKEN_FILE="$2"; shift 2 ;;
    --repo) REPO_DIR="$2"; shift 2 ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

ts_ct() { TZ=America/Chicago date '+%Y-%m-%d %H:%M:%S CT'; }

# Run as evo WITHOUT sudo -i. sudo -i re-escapes argv for a login shell: it leaves "$" unescaped (so $1/$B expand
# to empty in evo's login shell) and turns newlines into line continuations, which breaks every multi-line
# bash -c script below. -u/-H passes argv as-is; PATH covers evo's hermes CLI.
as_evo() {
  sudo -n -u evo -H env -C /home/evo \
    PATH="/home/evo/.local/bin:/home/evo/.hermes/hermes-agent/.hermes/bin:/usr/local/bin:/usr/bin:/bin" \
    HERMES_HOME="$HERMES_HOME_DIR" "$@"
}

cleanup() {
  if [[ -n "$STAGE_DIR" && -d "$STAGE_DIR" ]]; then
    rm -rf "$STAGE_DIR" || true
  fi
  if [[ "$LEASE_HELD" -eq 1 ]]; then
    : > "$LEASE_FILE" || true
    LEASE_HELD=0
    echo "[$(ts_ct)] Lease cleared: $LEASE_FILE"
  fi
}
trap cleanup EXIT

take_lease() {
  local what="$1"
  mkdir -p "$(dirname "$LEASE_FILE")"
  if [[ -s "$LEASE_FILE" ]]; then
    echo "BLOCKED: X3 lease is not empty ($LEASE_FILE):" >&2
    cat "$LEASE_FILE" >&2
    exit 1
  fi
  printf '%s | %s | %s\n' "${USER:-derekboone}" "$what" "$(ts_ct)" > "$LEASE_FILE"
  LEASE_HELD=1
  echo "[$(ts_ct)] Lease taken: $(cat "$LEASE_FILE")"
}

pixl_curl() {
  # Token is read inside an evo subshell and passed on curl stdin (-K -), never on argv or printed.
  local method="$1" path="$2" tok_file="$3" body="${4:-}"
  as_evo bash -c '
    set -euo pipefail
    m="$1"; url="$2"; tf="$3"; body="$4"
    [[ -r "$tf" ]] || { echo "MISSING/UNREADABLE token file: $tf" >&2; exit 2; }
    if [[ -n "$body" ]]; then
      ( tok="$(tr -d "\r\n" < "$tf")"; printf "header = \"Authorization: Bearer %s\"\n" "$tok" ) \
        | curl -sS -w "\nHTTP_CODE:%{http_code}\n" -K - -X "$m" -H "Content-Type: application/json" "$url" -d "$body"
    else
      ( tok="$(tr -d "\r\n" < "$tf")"; printf "header = \"Authorization: Bearer %s\"\n" "$tok" ) \
        | curl -sS -w "\nHTTP_CODE:%{http_code}\n" -K - -X "$m" "$url"
    fi
  ' _ "$method" "${PIXL_URL}${path}" "$tok_file" "$body"
}

check_sources() {
  local f
  for f in \
    "$REPO_DIR/x3/render/x3/still_candidate_sheet.py" \
    "$REPO_DIR/x3/render/x3/test_still_candidate_sheet.py" \
    "$REPO_DIR/hosts/x3/hermes/skills/pixlstash-image-library/SKILL.md" \
    "$REPO_DIR/hosts/x3/hermes/skills/h3-render/SKILL.md" \
    "$REPO_DIR/hosts/x3/systemd/user/pixlstash.service.d/10-memcap.conf"; do
    [[ -f "$f" ]] || { echo "MISSING source file: $f (use --repo <mono-clone>)" >&2; exit 1; }
  done
}

do_status() {
  echo "=== PixlStash service memcap & cgroup memory.events (read-only) ==="
  sudo -n systemctl --user -M evo@ show pixlstash.service -p ActiveState -p MemoryHigh -p MemoryMax -p MemoryCurrent || true
  local cg
  cg="$(sudo -n systemctl --user -M evo@ show pixlstash.service -p ControlGroup --value 2>/dev/null || true)"
  if [[ -n "$cg" && -r "/sys/fs/cgroup${cg}/memory.events" ]]; then
    cat "/sys/fs/cgroup${cg}/memory.events"
  fi
  echo "=== /api/v1/dedup/counts (counts only) ==="
  pixl_curl GET /api/v1/dedup/counts "$DEDUP_TOKEN_FILE" || true
  echo "=== /api/v1/users/me/penalised-tags (tag names & weights only) ==="
  pixl_curl GET /api/v1/users/me/penalised-tags "$READ_TOKEN_FILE" || true
}

do_smart_sets() {
  local is_dry="$1"
  # 4 orientation-matched render-ready Smart Sets (Smart Score >= 2.2 floor, likeness >= 0.55, non-video).
  python3 - "$is_dry" <<'PY'
import json, sys
dry = (sys.argv[1] == "1")
defs = [
    {"name": "FCSydny 9:16", "character_id": 1, "aspect": "portrait", "min_smart_score": 2.2, "min_likeness": 0.55, "formats": ["JPEG", "PNG"]},
    {"name": "FCSydny 16:9", "character_id": 1, "aspect": "landscape", "min_smart_score": 2.2, "min_likeness": 0.55, "formats": ["JPEG", "PNG"]},
    {"name": "FCMegan 9:16", "character_id": 2, "aspect": "portrait", "min_smart_score": 2.2, "min_likeness": 0.55, "formats": ["JPEG", "PNG"]},
    {"name": "FCMegan 16:9", "character_id": 2, "aspect": "landscape", "min_smart_score": 2.2, "min_likeness": 0.55, "formats": ["JPEG", "PNG"]},
]
if dry:
    print("[dry-run] Planned Smart Sets (verify exact v2.0.1 /api/v1/picture_sets schema live before POST):")
    print(json.dumps(defs, indent=2))
PY
  [[ "$is_dry" -eq 1 ]] && return 0

  echo "Checking existing picture sets via GET /api/v1/picture_sets..."
  local existing
  existing="$(pixl_curl GET /api/v1/picture_sets "$WRITE_TOKEN_FILE")"
  echo "$existing" | tail -n 3
  echo "NOTE: Smart Set filter JSON schema varies slightly across v2.0.x builds. If POST returns 403 (read-only token)"
  echo "      pass --token-file <write-token>, or create these 4 Smart Sets in PixlStash UI -> Picture Sets -> New Smart Set:"
  echo "      FCSydny 9:16 | FCSydny 16:9 | FCMegan 9:16 | FCMegan 16:9 (smart_score >= 2.2, likeness >= 0.55, JPEG/PNG)."
}

do_rollback() {
  take_lease "PIXLSTASH-UPGRADE rollback"
  as_evo bash -c '
    set -euo pipefail
    B="'"$BAK_DIR"'"
    [[ -f "$B/still_candidate_sheet.py" ]] && cp -a "$B/still_candidate_sheet.py" "'"$PICKER_DST"'"
    [[ -f "$B/test_still_candidate_sheet.py" ]] && cp -a "$B/test_still_candidate_sheet.py" "'"$PICKER_TEST_DST"'"
    [[ -f "$B/pixlstash-image-library.SKILL.md" ]] && cp -a "$B/pixlstash-image-library.SKILL.md" "'"$HERMES_HOME_DIR"'/skills/pixlstash-image-library/SKILL.md"
    [[ -f "$B/h3-render.SKILL.md" ]] && cp -a "$B/h3-render.SKILL.md" "'"$HERMES_HOME_DIR"'/skills/creative/h3-render/SKILL.md"
    [[ -f "$B/10-memcap.conf" ]] && cp -a "$B/10-memcap.conf" "'"$MEMCAP_DST"'"
    true
  '
  sudo -n systemctl --user -M evo@ daemon-reload
  local props
  props="$(as_evo bash -c 'f="$1"; [[ -f "$f" ]] && grep -E "^Memory(High|Max|SwapMax)=" "$f" | tr "\n" " "' _ "$BAK_DIR/10-memcap.conf" || true)"
  if [[ -n "$props" ]]; then
    # shellcheck disable=SC2086
    sudo -n systemctl --user -M evo@ set-property --runtime pixlstash.service $props
    echo "Live memcap reset to: $props"
  fi
  echo "[$(ts_ct)] Rollback complete (no PixlStash restart required)."
}

if [[ "$MODE" == "status" ]]; then
  do_status
  exit 0
fi

if [[ "$DO_SMART_SETS" -eq 1 && "$MODE" == "dry-run" ]]; then
  do_smart_sets 1
  exit 0
fi

if [[ "$DO_SMART_SETS" -eq 1 && "$MODE" == "rollback" ]]; then
  echo "--create-smart-sets cannot be combined with --rollback (Smart Sets are removed in the PixlStash UI)." >&2
  exit 2
fi

check_sources

if [[ "$MODE" == "rollback" ]]; then
  do_rollback
  exit 0
fi

if [[ "$MODE" == "dry-run" ]]; then
  echo "=== DRY RUN (no live changes) ==="
  echo "[dry-run] Would back up existing files into $BAK_DIR"
  echo "[dry-run] PX1: install upgraded still_candidate_sheet.py + test_still_candidate_sheet.py into /home/evo/AI/render/x3/ and run pytest"
  echo "[dry-run] PX1: install canonical pixlstash-image-library/SKILL.md and updated h3-render/SKILL.md into $HERMES_HOME_DIR/skills/"
  echo "[dry-run] PX2: persist 10-memcap.conf (MemoryHigh=14G, MemoryMax=16G, MemorySwapMax=2G) + daemon-reload + set-property --runtime (no PixlStash restart)"
  [[ "$DO_SMART_SETS" -eq 1 ]] && do_smart_sets 1
  echo "Run with --apply to execute, or --status to inspect live PixlStash health/dedup/penalised-tags."
  exit 0
fi

# === APPLY ===
take_lease "PIXLSTASH-UPGRADE PX1+PX2"

STAGE_DIR="$(mktemp -d /tmp/pixlstash-up-stage.XXXXXX)"
chmod 0755 "$STAGE_DIR"
cp "$REPO_DIR/x3/render/x3/still_candidate_sheet.py" "$STAGE_DIR/still_candidate_sheet.py"
cp "$REPO_DIR/x3/render/x3/test_still_candidate_sheet.py" "$STAGE_DIR/test_still_candidate_sheet.py"
cp "$REPO_DIR/hosts/x3/hermes/skills/pixlstash-image-library/SKILL.md" "$STAGE_DIR/pixlstash-image-library.SKILL.md"
cp "$REPO_DIR/hosts/x3/hermes/skills/h3-render/SKILL.md" "$STAGE_DIR/h3-render.SKILL.md"
cp "$REPO_DIR/hosts/x3/systemd/user/pixlstash.service.d/10-memcap.conf" "$STAGE_DIR/10-memcap.conf"
chmod 0644 "$STAGE_DIR"/*

echo "=== Step 1: Backups + install PX1 (picker + skills) & PX2 (14G/16G memcap) ==="
as_evo bash -c '
  set -euo pipefail
  B="'"$BAK_DIR"'"
  mkdir -p "$B" "'"$HERMES_HOME_DIR"'/skills/pixlstash-image-library" "'"$HERMES_HOME_DIR"'/skills/creative/h3-render" "$(dirname "'"$MEMCAP_DST"'")"
  [[ -f "'"$PICKER_DST"'" && ! -f "$B/still_candidate_sheet.py" ]] && cp -a "'"$PICKER_DST"'" "$B/still_candidate_sheet.py"
  [[ -f "'"$PICKER_TEST_DST"'" && ! -f "$B/test_still_candidate_sheet.py" ]] && cp -a "'"$PICKER_TEST_DST"'" "$B/test_still_candidate_sheet.py"
  [[ -f "'"$HERMES_HOME_DIR"'/skills/pixlstash-image-library/SKILL.md" && ! -f "$B/pixlstash-image-library.SKILL.md" ]] && \
    cp -a "'"$HERMES_HOME_DIR"'/skills/pixlstash-image-library/SKILL.md" "$B/pixlstash-image-library.SKILL.md"
  [[ -f "'"$HERMES_HOME_DIR"'/skills/creative/h3-render/SKILL.md" && ! -f "$B/h3-render.SKILL.md" ]] && \
    cp -a "'"$HERMES_HOME_DIR"'/skills/creative/h3-render/SKILL.md" "$B/h3-render.SKILL.md"
  [[ -f "'"$MEMCAP_DST"'" && ! -f "$B/10-memcap.conf" ]] && cp -a "'"$MEMCAP_DST"'" "$B/10-memcap.conf"

  install -m 0755 "'"$STAGE_DIR"'/still_candidate_sheet.py" "'"$PICKER_DST"'"
  install -m 0644 "'"$STAGE_DIR"'/test_still_candidate_sheet.py" "'"$PICKER_TEST_DST"'"
  install -m 0644 "'"$STAGE_DIR"'/pixlstash-image-library.SKILL.md" "'"$HERMES_HOME_DIR"'/skills/pixlstash-image-library/SKILL.md"
  install -m 0644 "'"$STAGE_DIR"'/h3-render.SKILL.md" "'"$HERMES_HOME_DIR"'/skills/creative/h3-render/SKILL.md"
  install -m 0644 "'"$STAGE_DIR"'/10-memcap.conf" "'"$MEMCAP_DST"'"
'
rm -rf "$STAGE_DIR"
STAGE_DIR=""

echo "=== Step 2: Persist memcap (daemon-reload + live property, no PixlStash restart) ==="
sudo -n systemctl --user -M evo@ daemon-reload
# --runtime: the drop-in file is the persistent copy; a plain set-property would also write a user.control drop-in
# that outranks 10-memcap.conf and survives --rollback.
sudo -n systemctl --user -M evo@ set-property --runtime pixlstash.service MemoryHigh=14G MemoryMax=16G MemorySwapMax=2G

echo "=== Step 3: Verify picker unit tests ==="
as_evo "$PY_EVO" -m pytest -q "$PICKER_TEST_DST"

if [[ "$DO_SMART_SETS" -eq 1 ]]; then
  do_smart_sets 0
fi

echo "=== Step 4: Post-apply status ==="
do_status
echo "DONE. Backups saved in $BAK_DIR. Run with --rollback to undo."
