#!/bin/bash
# Sydney pi chat on the EVO-X3: launch-config mirror ONLY of AlienPc's $sydneyPiArgs (C:\AI\director\scripts\pi_herdr_at_logon.ps1).
# Max Architect 2026-11-15, Derrick t1745u. Sydney's persona, private files, chats and memory were NOT read or copied:
# ~/AI/sydney holds no persona. Do not start this as Sydney until Derrick (or Sydney's own lane) moves those files.
# Model: x3-local/gemma4-heretic (cutover mapping; AlienPc uses llama-swap/gemma4_heretic_poly_think --thinking medium).
# Omitted on purpose: --remote, herdr-agent-state.ts, pi-mobile (not on the X3; phone cutover gated).
set -euo pipefail
R="$HOME/AI/render"; S="$HOME/AI/community/skills"
cd "$HOME/AI/sydney"
export PATH="$R/x3/.venv/bin:$HOME/.local/bin:$PATH"
exec pi --approve \
  --no-extensions \
  -e "$R/.pi/npm/node_modules/pi-permission-system/index.ts" \
  -e "$HOME/.pi/agent/npm/node_modules/cc-safety-net/dist/pi/index.js" \
  -e "$R/.pi/npm/node_modules/pi-memory/index.ts" \
  -e "$R/.pi/extensions/loop-guard.ts" \
  --no-mcp --no-skills \
  --skill "$S/video-render" --skill "$S/image-render" --skill "$S/comfy-render" \
  --skill "$S/h3-parody-identity" --skill "$S/h3-prompting" --skill "$S/h3-max-ref2va-prompt" \
  --skill "$S/h3-hc-render" --skill "$S/alienpc-hardcore-i2v-director" --skill "$S/alienpc-stills-pose-edit-prompting" \
  --no-context-files \
  --append-system-prompt "$R/AGENTS.md" \
  --model "${SYDNEY_MODEL:-x3-local/gemma4-heretic}" \
  --thinking medium \
  "$@"
