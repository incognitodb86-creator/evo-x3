#!/bin/bash
# Forge Vaultwarden MCP wrapper (Max Architect 2026-11-16). Secrets come from the 0600 env file; nothing on argv.
set -euo pipefail
set -a; source /home/evo/.config/forge-mcp/vaultwarden.env; set +a
export BW_CLI_PATH=/home/evo/.local/bin/bw
BW=/home/evo/.local/bin/bw
export BITWARDENCLI_APPDATA_DIR=/home/evo/.config/forge-mcp/bw-data
mkdir -p "$BITWARDENCLI_APPDATA_DIR"; chmod 700 "$BITWARDENCLI_APPDATA_DIR"
st=$($BW status 2>/dev/null | python3 -c 'import sys,json;print(json.load(sys.stdin).get("status",""))' 2>/dev/null || echo "")
if [ "$st" = "unauthenticated" ] || [ -z "$st" ]; then
  [ "$($BW config server 2>/dev/null)" = "$BW_SERVER" ] || $BW config server "$BW_SERVER" >/dev/null
  $BW login --apikey >/dev/null 2>&1
fi
BW_SESSION=$($BW unlock --passwordenv BW_PASSWORD --raw 2>/dev/null)
export BW_SESSION
$BW sync >/dev/null 2>&1 || true
exec /home/evo/.local/bin/mcp-server-bitwarden "$@"
