#!/bin/bash
# Start Render's pi chat on the EVO-X3. Mirror of AlienPc's production Render pane
# (C:\AI\director\scripts\pi_herdr_at_logon.ps1 $renderPiArgs, stripped pi: render skills only, no MCP,
# no CE/coding extensions, no global AGENTS.md). Max Architect 2026-11-15, Derrick t1739u-t1741u.
#   bash ~/AI/render/x3/render-pi.sh                           # interactive
#   bash ~/AI/render/x3/render-pi.sh -p --no-session "<ask>"   # one-shot
# Differences from AlienPc, on purpose:
#   - model x3-local/flash-next-uncensored (matches writer_pipeline/config.yaml + render/.pi/settings.json -> zero GPU swaps; vision tower enabled in llama-swap.yaml, plus joycaption fallback in small group)
#   - loads lean OPERATOR.md (~55 lines) in system prompt while keeping full AGENTS.md intact for wp_compile_prompt.py / 77-rule gate
#   - no --remote / herdr-agent-state.ts / pi-mobile: herdr and the phone bridge are managed separately
# Writing is dry-run only until Derrick approves. Renders run on AlienPc ComfyUI (x3/queue-remote.sh --yes-derrick).
#   - --no-extensions is kept on purpose: a bare `pi` in this folder would also load
#     plannotator, pi-canvas, pi-say and the compound-engineering plugin from
#     ~/AI/render/.pi/settings.json. Intended extensions are passed with -e:
#     pi-permission-system, cc-safety-net, loop-guard, pi-subagents, pi-memory.
set -euo pipefail
R="$HOME/AI/render"; S="$HOME/AI/community/skills"
cd "$R"
export PI_CODING_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/panes/render}"
export PI_MEMORY_DIR="${PI_MEMORY_DIR:-$HOME/.pi/panes/render/memory}"  # own memory per chat (Derrick t2318u)
export PATH="$R/x3/.venv/bin:$HOME/.local/bin:$PATH"
# PixlStash read token for still lookups (AGENTS.md uses $PIXL_KEY; Max 2026-11-16, Derrick t2190u)
[ -r "$HOME/.config/pixlstash/render-read.token" ] && export PIXL_KEY="$(tr -d '[:space:]' < "$HOME/.config/pixlstash/render-read.token")"
exec pi --approve \
  --name "${RENDER_NAME:-Render-X3}" \
  --no-extensions \
  --exclude-tools contact_supervisor \
  -e "$R/.pi/npm/node_modules/pi-permission-system/index.ts" \
  -e "$HOME/.pi/agent/npm/node_modules/cc-safety-net/dist/pi/index.js" \
  -e "$R/.pi/extensions/loop-guard.ts" \
  -e "$R/.pi/extensions/auto-continue.ts" \
  -e "$HOME/.pi/agent/npm/node_modules/pi-subagents/bundle/index.js" \
  -e "$R/.pi/npm/node_modules/pi-memory/index.ts" \
  --no-mcp \
  --no-skills \
  --skill "$S/h3-parody-identity" --skill "$S/h3-prompting" \
  --no-context-files \
  --append-system-prompt "${RENDER_PROMPT_FILE:-$R/OPERATOR.md}" \
  --append-system-prompt "You are Render-X3 on evo-x3." \
  --model "${RENDER_MODEL:-x3-local/flash-next-uncensored-v2}" \
  --thinking "${RENDER_THINKING:-low}" \
  "$@"
