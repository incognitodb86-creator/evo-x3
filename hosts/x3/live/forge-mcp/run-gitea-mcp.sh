#!/bin/bash
set -euo pipefail
TOKEN_FILE=/home/evo/.config/forge-mcp/GITEA_ACCESS_TOKEN
export GITEA_ACCESS_TOKEN="$(cat "$TOKEN_FILE")"
exec /home/evo/.local/bin/gitea-mcp "$@"
