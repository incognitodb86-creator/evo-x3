#!/bin/bash
# Forge pi chat on the EVO-X3 (config mirror of AlienPc Forge: cwd C:\Users\derek\forge, bare `pi --remote` on global
# settings + global AGENTS.md = C:\AI\community\agent-shared\AGENTS.md). Max Architect 2026-11-15, Derrick t1745u "Any gaps".
# Model: x3-local/flash-next (cutover mapping Forge/general -> Flash-Next) instead of llama-swap/coding_swift15_iq3s_esp.
# Project settings ~/AI/forge/.pi/settings.json carry Forge's packages/skills/prompts so X3's global pi stays unchanged.
# X3 Forge pane launcher: runs as evo from herdr-panes.sh (which passes --remote for herdr/pi-mobile).
set -euo pipefail
cd "$HOME/AI/forge"
export PI_CODING_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/panes/forge}"
export PATH="$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH"
exec pi --approve --model "${FORGE_MODEL:-x3-local/flash-next}" --thinking "${FORGE_THINKING:-medium}" "$@"
