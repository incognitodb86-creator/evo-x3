#!/bin/bash
# Submit a saved ComfyUI API-format workflow (request.api.json) from the X3 to AlienPc's GPU over the tailnet.
# Endpoint: https://alienpc.tailf242b2.ts.net:8446  (Tailscale Serve -> AlienPc llama-swap 127.0.0.1:8080/upstream/comfyui_auto)
# DO NOT run for an H3 render without Derrick's yes for that prompt.
# POST /prompt wakes comfyui_auto in llama-swap's exclusive `main` group: it unloads whatever LLM is loaded on AlienPc
# (Render/Forge writer) and can take a few minutes to load. Check the GPU is free first.
set -euo pipefail
API=${COMFY_API:-https://alienpc.tailf242b2.ts.net:8446}
REQ=${1:?usage: comfy-submit.sh request.api.json}
CID=${COMFY_CLIENT_ID:-evo-x3-$(hostname)-$$}
# request.api.json may be the bare graph or already {"prompt": {...}}; wrap if needed.
BODY=$(jq -c --arg cid "$CID" 'if has("prompt") then . + {client_id:$cid} else {prompt:., client_id:$cid} end' "$REQ")
RESP=$(printf %s "$BODY" | curl -sS -m 1200 -H "Content-Type: application/json" --data-binary @- "$API/prompt")
echo "$RESP"
PID=$(jq -r '.prompt_id // empty' <<<"$RESP"); [ -n "$PID" ] || exit 1
# Poll history until outputs appear (keeps llama-swap's ttl reset while waiting).
while :; do
  H=$(curl -sS -m 60 "$API/history/$PID" || true)
  if jq -e --arg p "$PID" '.[$p].outputs | length > 0' <<<"$H" >/dev/null 2>&1; then
    jq --arg p "$PID" '.[$p].outputs' <<<"$H"; break
  fi
  sleep 30
done
# Fetch a file: curl -o out.mp4 "$API/view?filename=<name>&subfolder=<sub>&type=output"
