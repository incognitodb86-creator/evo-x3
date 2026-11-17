#!/usr/bin/env bash
# Verified minimal headless launcher for U56 Ralph loop on EVO-X3 (run as user `evo`).
# Strips extension/skill/git-plugin bloat (--no-approve --offline --no-extensions + explicit cc-safety-net & loop-guard),
# clears PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR, suppresses pytest bytecode/cache pollution, and kills process groups cleanly.
# Usage:
#   bash run-u56-pass.sh 1                          # Run 1 verified headless pass (e.g. Item 0)
#   RALPH_THINKING=high bash run-u56-pass.sh 3       # Deeper reasoning per pass (default medium; "off" restores U56 behaviour)
set -euo pipefail

if [ "$(id -un)" != "evo" ]; then
  echo "ERROR: Run as user 'evo' (not root or derekboone)." >&2
  exit 1
fi

MAX_PASSES="${1:-1}"
MODEL="${2:-x3-local/flash-next-uncensored}"
# Thinking on (Qwen3.8-Flash-Next card: lower effort causes more failed/retried agentic turns), so allow 30 min per pass.
THINKING="${RALPH_THINKING:-medium}"
PASS_LIMIT_SEC="${PASS_LIMIT_SEC:-1800}"
LOG_DIR="/home/evo/ralph-u56/loopA"
mkdir -p "$LOG_DIR"

# Pre-flight: abort if stray ppid=1 pi processes or active tagger swaps would starve slots
if ps -eo pid,ppid,pgid,etime,cmd | grep -E "ralph\.sh|pi --.*PROMPT\.md" | grep -v grep; then
  echo "ERROR: Existing ralph.sh or headless pi process detected above. Stop it first." >&2
  exit 2
fi

if XDG_RUNTIME_DIR="/run/user/$(id -u)" systemctl --user is-active --quiet u42-pixlstash-tagger.service 2>/dev/null; then
  echo "WARNING: u42-pixlstash-tagger.service is active on gemma4-heretic and will swap-thrash 'main' group!" >&2
  echo "Pause it first with: systemctl --user stop u42-pixlstash-tagger.service" >&2
  exit 3
fi

SAFETY_EXT="/home/evo/.pi/agent/npm/node_modules/cc-safety-net/dist/pi/index.js"
LOOP_GUARD_EXT="/home/evo/AI/render/.pi/extensions/loop-guard.ts"
EXT_FLAGS="--no-extensions"
[ -f "$SAFETY_EXT" ] && EXT_FLAGS="$EXT_FLAGS -e $SAFETY_EXT"
[ -f "$LOOP_GUARD_EXT" ] && EXT_FLAGS="$EXT_FLAGS -e $LOOP_GUARD_EXT"

# --no-extensions/--no-mcp/--no-skills/--no-context-files/--offline are proven on the X3 (render-pi.sh, U53).
# --no-approve and --no-prompt-templates exist in current upstream pi; only pass them if this pi build lists them.
export PATH="$HOME/.local/bin:$PATH"
PI_HELP="$(pi --help 2>&1 || true)"
OPT_FLAGS=""
for f in --no-approve --no-prompt-templates; do
  if printf '%s\n' "$PI_HELP" | grep -q -- "$f"; then OPT_FLAGS="$OPT_FLAGS $f"; else echo "NOTE: pi has no $f flag; skipping it" >&2; fi
done
# Structured read-only search tools (grep/find use ripgrep/fd) when this pi build has --tools.
if printf '%s\n' "$PI_HELP" | grep -q -- "--tools"; then OPT_FLAGS="$OPT_FLAGS --tools read,bash,edit,write,grep,find,ls"; else echo "NOTE: pi has no --tools flag; default tools only" >&2; fi

BACKPRESSURE_CMD='cd "$RALPH_WORKTREE/scripts" && PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless python -m pytest -q -p no:cacheprovider tests parody 2>&1 | tail -1 | grep -Eq "^[0-9]+ passed, 3 skipped(, 6 errors)? in" && { uv run -q --no-project --with ruff python /home/evo/AI/forge/ralph-community/lint_changed.py "$RALPH_WORKTREE" "${RALPH_PASS_BASE:-HEAD}"; [ $? -ne 3 ]; }'

CMD_OVERRIDE="env -u PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR PI_CODING_AGENT_DIR=/home/evo/.pi/panes/forge pi$OPT_FLAGS --offline --print --no-session --no-context-files $EXT_FLAGS --no-mcp --no-skills --thinking $THINKING --model $MODEL \"@/home/evo/AI/forge/ralph-community/PROMPT.md\" \"Read /home/evo/AI/forge/ralph-community/fix_plan.md. Complete ONLY the top unchecked - [ ] item inside the current community worktree (\$RALPH_WORKTREE), run its pytest check to verify it passes, git commit your edited files by explicit path on the worktree branch (never git add -A), tick - [x] on that item in /home/evo/AI/forge/ralph-community/fix_plan.md, and stop immediately. Never delete any files or _archive directories.\""

cd /home/evo/AI/forge/ralph-community
exec bash ./ralph.sh \
  -Max "$MAX_PASSES" \
  -WorkDir /home/evo/AI/render \
  -TargetRepo /home/evo/AI/community \
  -PiCwd target \
  -PassLimitSec "$PASS_LIMIT_SEC" \
  -MaxDiffFiles 10 \
  -MemoryRoot /home/evo/AI/forge/ralph-community/notes/_pi_memory \
  -LogPath "$LOG_DIR/ralph.log" \
  -BackpressureCmd "$BACKPRESSURE_CMD" \
  -CommandOverride "$CMD_OVERRIDE"
