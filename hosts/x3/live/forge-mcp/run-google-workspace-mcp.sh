#!/bin/bash
set -euo pipefail
set -a
source /home/evo/.config/forge-mcp/google-workspace.env
set +a
exec /home/evo/.local/bin/workspace-mcp "$@"
