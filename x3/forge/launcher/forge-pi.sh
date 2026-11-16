#!/bin/bash
# Forge pi chat on the EVO-X3 (config mirror of AlienPc Forge: cwd C:\Users\derek\forge, bare `pi --remote` on global
# settings + global AGENTS.md = C:\AI\community\agent-shared\AGENTS.md). Max Architect 2026-11-15, Derrick t1745u "Any gaps".
# Model: x3-local/flash-next (cutover mapping Forge/general -> Flash-Next) instead of llama-swap/coding_swift15_iq3s_esp.
# Project settings ~/AI/forge/.pi/settings.json carry Forge's packages/skills/prompts so X3's global pi stays unchanged.
# NOT production: AlienPc Forge stays live until Derrick OKs the picks. No --remote (herdr/pi-mobile not on the X3).
set -euo pipefail
cd "$HOME/AI/forge"
export PATH="$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH"
exec pi --approve --model "${FORGE_MODEL:-x3-local/flash-next}" "$@"
