#!/bin/bash
# Load llama-swap client key into the environment only (never argv/logs), then run the arm.
set -euo pipefail
set -a; . <(sudo -n cat /etc/evo-x3/llm.env); set +a
export OPENAI_API_KEY="$LLM_KEY_BOX"
exec "$@"
