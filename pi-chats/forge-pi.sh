#!/bin/bash
# Forge pi chat on the EVO-X3 (config mirror of AlienPc Forge: cwd C:\Users\derek\forge, bare `pi --remote` on global
# settings + global AGENTS.md = C:\AI\community\agent-shared\AGENTS.md). Max Architect 2026-11-15, Derrick t1745u "Any gaps".
# Model: x3-local/flash-next (cutover mapping Forge/general -> Flash-Next) instead of llama-swap/coding_swift15_iq3s_esp.
# Project settings ~/AI/forge/.pi/settings.json carry Forge's packages/skills/prompts so X3's global pi stays unchanged.
# X3 Forge pane launcher: runs as evo from herdr-panes.sh (which passes --remote for herdr/pi-mobile).
set -euo pipefail
cd "$HOME/AI/forge"
export PI_CODING_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/panes/forge}"
export PI_MEMORY_DIR="${PI_MEMORY_DIR:-$HOME/.pi/panes/forge/memory}"  # own memory per chat (Derrick t2318u)
export PATH="$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH"
# 2026-11-17 Derrick t2296u/t2298u: thinking high -> medium (community agent-loop default).
# 2026-11-17 Derrick t2322 (Strix Halo community settings): coding sampling temp 0.6 via provider x3-local-coding (same served slot flash-next-uncensored).
exec pi --approve \
  --name "${FORGE_NAME:-Forge-X3}" \
  --append-system-prompt "You are Forge-X3 on evo-x3." \
  --model "${FORGE_MODEL:-x3-local-coding/flash-next-uncensored-v2}" \
  --thinking "${FORGE_THINKING:-medium}" \
  "$@"
