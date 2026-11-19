#!/bin/bash
set -euo pipefail
set -a
source /home/evo/.config/forge-mcp/unifi.env
set +a
export UNIFI_READ_ONLY="${UNIFI_READ_ONLY:-true}"
exec /home/evo/.local/bin/unifi-network-mcp "$@"
