#!/bin/bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [args...]" >&2
  exit 2
fi
exec sudo -n bash -c '. /etc/evo-x3/llm.env; export LLM_KEY_BOX OPENAI_API_KEY="$LLM_KEY_BOX"; exec sudo -u derekboone --preserve-env=LLM_KEY_BOX,OPENAI_API_KEY "$@"' -- "$@"
