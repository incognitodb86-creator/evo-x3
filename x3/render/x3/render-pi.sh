#!/bin/bash
# Start Render's pi chat on the EVO-X3. Mirror of AlienPc's production Render pane
# (C:\AI\director\scripts\pi_herdr_at_logon.ps1 $renderPiArgs, stripped pi: render skills only, no MCP,
# no CE/coding extensions, no global AGENTS.md). Max Architect 2026-11-15, Derrick t1739u-t1741u.
#   bash ~/AI/render/x3/render-pi.sh                           # interactive
#   bash ~/AI/render/x3/render-pi.sh -p --no-session "<ask>"   # one-shot
# Differences from AlienPc, on purpose:
#   - model x3-local/gemma4-heretic (Derrick cutover mapping; Q8_0 llama.cpp Vulkan + mmproj vision, thinking medium as on AlienPc since 2026-11-15 r2)
#     instead of llama-swap/gemma4_heretic_poly_think --thinking medium
#   - no --remote / herdr-agent-state.ts / pi-mobile: herdr and the phone bridge are not on the X3 (phone cutover is gated)
# Writing is dry-run only. Renders run on AlienPc ComfyUI; queue only after Derrick's yes (x3/queue-remote.sh).
# NOT the production Render chat until Derrick OKs the picks; AlienPc stays production until cutover.
#   - --no-extensions is kept on purpose: a bare `pi` in this folder would also load
#     plannotator, pi-canvas, pi-say and the compound-engineering plugin from
#     ~/AI/render/.pi/settings.json. Intended extensions are passed with -e:
#     pi-permission-system, cc-safety-net, loop-guard, pi-subagents, pi-memory.
set -euo pipefail
R="$HOME/AI/render"; S="$HOME/AI/community/skills"
cd "$R"
export PI_CODING_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/panes/render}"
export PATH="$R/x3/.venv/bin:$HOME/.local/bin:$PATH"
# PixlStash read token for still lookups (AGENTS.md uses $PIXL_KEY; Max 2026-11-16, Derrick t2190u)
[ -r "$HOME/.config/pixlstash/render-read.token" ] && export PIXL_KEY="$(tr -d '[:space:]' < "$HOME/.config/pixlstash/render-read.token")"
exec pi --approve \
  --no-extensions \
  -e "$R/.pi/npm/node_modules/pi-permission-system/index.ts" \
  -e "$HOME/.pi/agent/npm/node_modules/cc-safety-net/dist/pi/index.js" \
  -e "$R/.pi/extensions/loop-guard.ts" \
  -e "$HOME/.pi/agent/npm/node_modules/pi-subagents/bundle/index.js" \
  -e "$R/.pi/npm/node_modules/pi-memory/index.ts" \
  --no-mcp \
  --no-skills \
  --skill "$S/h3-parody-identity" --skill "$S/h3-prompting" \
  --no-context-files \
  --append-system-prompt "$R/AGENTS.md" \
  --model "${RENDER_MODEL:-x3-local/gemma4-heretic}" \
  --thinking medium \
  "$@"
