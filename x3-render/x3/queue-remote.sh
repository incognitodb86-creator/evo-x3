#!/bin/bash
# Queue a READY Render run dir from the EVO-X3 on AlienPc's ComfyUI over the tailnet.
# Max Architect 2026-11-15; 2026-11-16 consolidation P1b: now drives run_queue.py --remote (scripts/remote_comfy.py),
# so the X3 gets the same batch behaviour as AlienPc (adults guard, pytest gate, lock, one retry, STOP, timeouts,
# /interrupt + /queue delete, outputs downloaded into <run>/<tag>/, DONE ok / FAIL lines in _render_queue.log).
# Max Architect 2026-11-16 (Derrick t2036u, t2039u): a READY dir is queued after --yes-derrick with no rebuild and no second writer pass.
# A leftover DRY_RUN marker is not a refusal; it is removed on a real queue.
# NEVER run without Derrick's explicit yes for this exact prompt.
# Usage: queue-remote.sh <run_dir> --yes-derrick [--dry-run] [--keep-comfy-process] [--wait]
set -euo pipefail
RUN=$(realpath "${1:?usage: queue-remote.sh <run_dir> --yes-derrick [--dry-run]}")
[ "${2:-}" = "--yes-derrick" ] || { echo "refused: pass --yes-derrick only after Derrick approved this prompt" >&2; exit 2; }
shift 2
DRY=0; EXTRA=(); WAIT=0
for a in "$@"; do case "$a" in --dry-run) DRY=1;; --keep-comfy-process) EXTRA+=("$a");; --wait) WAIT=1;; *) echo "unknown arg $a" >&2; exit 2;; esac; done
TAG=clip
[ -f "$RUN/prompt.txt" ] && [ -f "$RUN/$TAG/request.api.json" ] && [ ! -f "$RUN/${TAG}_NOT_READY.txt" ] || { echo "refused: $RUN is not READY" >&2; exit 3; }
REQ="$RUN/$TAG/request.api.json"
W=$(jq -r '(if has("prompt") then .prompt else . end).c0.inputs.width // empty' "$REQ")
H=$(jq -r '(if has("prompt") then .prompt else . end).c0.inputs.height // empty' "$REQ")
F=$(jq -r '.build.total_frames // empty' "$RUN/build_report.json" 2>/dev/null || true)
[ -n "$F" ] || F=$(jq -r '(if has("prompt") then .prompt else . end).c0.inputs.length // empty' "$REQ")
[ -n "$W" ] && [ -n "$H" ] && [ -n "$F" ] || { echo "refused: cannot read size/frames from $REQ" >&2; exit 3; }
PY=${RQ_PY:-$HOME/AI/render/x3/.venv/bin/python}
# Max Architect 2026-11-16 (Derrick t2049u): works from nohup/ssh shells, and a busy GPU waits instead of failing rc 7.
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
LOCK="$HOME/AI/locks/gpu-render.lock"
if [ "$DRY" = 0 ] && [ "${QR_WAITING:-0}" != 1 ] && ! flock -n "$LOCK" true 2>/dev/null; then
  SELF=$(realpath "$0")
  systemd-run --user --unit "render-wait-$(basename "$RUN")-$$" --setenv=QR_WAITING=1 --setenv=XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" \
    bash -c 'until flock -n "$1" true; do sleep 15; done; exec "$2" "$3" --yes-derrick "${@:4}"' _ "$LOCK" "$SELF" "$RUN" "${EXTRA[@]}"
  echo "X3 submitter busy: waiting in background; queues automatically when the X3 submit queue frees (log $RUN/_render_queue.log)"
  exit 0
fi
cd "$HOME/AI/community"
ARGS=(scripts/run_queue.py --remote --run-dir "$RUN" --size "${W}x${H}" --frames "$F" "${EXTRA[@]}")
ORD='{"order":[{"pos":1,"tag":"clip","arm":"oc_writer","scene":"x3","seed":0}]}'
if [ "$DRY" = 1 ]; then
  if [ -f "$RUN/_render_order.json" ]; then "$PY" "${ARGS[@]}" --dry-run --probe; else printf %s "$ORD" | "$PY" "${ARGS[@]}" --queue /dev/stdin --dry-run --probe; fi
  exit $?
fi
rm -f "$RUN/DRY_RUN"
[ -f "$RUN/_render_order.json" ] || printf %s "$ORD" > "$RUN/_render_order.json"
"$PY" "${ARGS[@]}" --detach
if [ "$WAIT" = 1 ]; then
  until grep -q "BATCH closed" "$RUN/_render_queue.log" 2>/dev/null; do sleep 30; done
  grep "BATCH closed" "$RUN/_render_queue.log" | tail -1
fi
