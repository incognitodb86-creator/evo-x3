#!/bin/bash
# Queue a READY Render run dir from the EVO-X3 on AlienPc's ComfyUI over the tailnet
# (Derrick: "X3 can queue ComfyUI renders on AlienPc over the tailnet"). Max Architect 2026-11-15.
# NEVER run without Derrick's explicit yes for this exact prompt (paste prompt.txt to him first).
# Steps: 1) refuse unless READY (prompt.txt + clip/request.api.json, no clip_NOT_READY.txt)
#        2) upload every LoadImage still the graph references to ComfyUI input (POST /upload/image, subfolder kept)
#        3) submit clip/request.api.json with ~/evo-x3/scripts/comfy-submit.sh (POST /prompt, polls /history)
# POST /prompt wakes comfyui_auto in AlienPc llama-swap's exclusive group and unloads AlienPc's LLM; check the GPU first.
set -euo pipefail
RUN=${1:?usage: queue-remote.sh <run_dir> --yes-derrick}
[ "${2:-}" = "--yes-derrick" ] || { echo "refused: pass --yes-derrick only after Derrick approved this prompt" >&2; exit 2; }
API=${COMFY_API:-https://alienpc.tailf242b2.ts.net:8446}
REQ="$RUN/clip/request.api.json"
[ -f "$RUN/prompt.txt" ] && [ -f "$REQ" ] && [ ! -f "$RUN/clip_NOT_READY.txt" ] || { echo "refused: $RUN is not READY" >&2; exit 3; }
IN_LOCAL="$HOME/AI/comfy-alienpc/input"
jq -r '(if has("prompt") then .prompt else . end) | to_entries[] | select(.value.class_type=="LoadImage") | .value.inputs.image' "$REQ" | sort -u |
while read -r img; do
  f="$IN_LOCAL/$img"; [ -f "$f" ] || { echo "missing local still $f" >&2; exit 4; }
  sub=$(dirname "$img"); [ "$sub" = "." ] && sub=""
  curl -sS -m 300 -F "image=@$f" -F "subfolder=$sub" -F "type=input" -F "overwrite=true" "$API/upload/image"; echo
done
exec "$HOME/evo-x3/scripts/comfy-submit.sh" "$REQ"
