#!/bin/bash
# EVO-X3 herdr panes (Linux port of AlienPc C:\AI\director\scripts\pi_herdr_at_logon.ps1; consolidation P3,
# Max Architect 2026-11-16). Runs as evo from herdr-panes.service. For each chat in PANES it creates one herdr
# workspace (label via LABEL map, e.g. Render-X3 / Forge-X3) if missing, then runs that chat's launcher in the pane:
#   ~/evo-x3/pi-chats/<name>-pi.sh --remote [+ pi-mobile and herdr extensions for the --no-extensions launchers]
# The launchers hold the full AlienPc-equivalent argv (extensions, skills, AGENTS.md, model, thinking).
# Default PANES="render forge". Sydney retired 20261117-100137 (Derrick t82u), files in _archive/sydney-retired-20261117-100137. Sydney workspace copied 2026-11-16 (Derrick t1881u).
set -uo pipefail
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin"
LOG=${HERDR_PANES_LOG:-$HOME/evo-x3/logs/herdr-panes.log}; mkdir -p "$(dirname "$LOG")"
log() { echo "$(date +%FT%T%z) $*" >> "$LOG"; }
PANES=${PANES:-"render forge"}
declare -A CWD=([render]="$HOME/AI/render" [forge]="$HOME/AI/forge" [sydney]="$HOME/AI/sydney")
declare -A LABEL=([render]="Render-X3" [forge]="Forge-X3" [sydney]="Sydney-X3")
MOB="$HOME/.pi/agent/npm/node_modules/pi-mobile/src/index.ts"
HST=$(ls "$HOME"/.pi/agent/extensions/herdr*.ts 2>/dev/null | head -1)
for i in $(seq 1 30); do herdr status 2>/dev/null | grep -q "status: *running" && break; sleep 1; done
herdr status 2>/dev/null | grep -q "status: *running" || { log "ERROR herdr server not running"; exit 1; }
panes_json=$(herdr pane list 2>/dev/null); [ -n "$panes_json" ] || panes_json='{}'
for name in $PANES; do
  dir=${CWD[$name]:-}; label=${LABEL[$name]:-$name}; launcher="$HOME/evo-x3/pi-chats/$name-pi.sh"
  [ -d "$dir" ] && [ -r "$launcher" ] || { log "ERROR $name: missing $dir or $launcher"; continue; }
  extra="--remote"
  if grep -q -- "--no-extensions" "$launcher"; then
    [ -f "$MOB" ] && extra="$extra -e $MOB"; [ -n "$HST" ] && extra="$extra -e $HST"
  fi
  # herdr restores workspaces after a server restart/boot but not the agent in them: herdr agent list
  # only returns panes with a live agent, so query herdr pane list + herdr workspace get to match an
  # existing restored pane by workspace label or cwd; skip only when pi is already running there.
  row=""
  best_pane=""
  best_agent="none"
  best_wid=""
  best_wlabel=""
  while IFS=$'\t' read -r pid wid pcwd pagent; do
    [ -n "$pid" ] || continue
    wlabel=$(herdr workspace get "$wid" 2>/dev/null | jq -r '.result.workspace.label // ""')
    if [ "$wlabel" = "$label" ] || [ "$wlabel" = "$name" ] || [ "$pcwd" = "$dir" ]; then
      if [ "$pagent" = "pi" ]; then
        best_pane="$pid"
        best_agent="pi"
        best_wid="$wid"
        best_wlabel="$wlabel"
        break
      elif [ -z "$best_pane" ]; then
        best_pane="$pid"
        best_agent="${pagent:-none}"
        best_wid="$wid"
        best_wlabel="$wlabel"
      fi
    fi
  done < <(printf %s "$panes_json" | jq -r '.result.panes[]? | [.pane_id, .workspace_id, .cwd, (.agent // "none")] | @tsv')
  if [ -n "$best_wid" ] && [ "$best_wlabel" != "$label" ]; then
    herdr workspace rename "$best_wid" "$label" >> "$LOG" 2>&1; log "workspace rename $best_wid ($best_wlabel -> $label) rc=$?"
  fi
  if [ -n "$best_pane" ]; then
    row="$best_pane $best_agent"
  fi
  pane="$best_pane"; agent="$best_agent"
  if [ -n "$row" ] && [ "$agent" = "pi" ]; then log "$name pi already running in $pane; skip"; continue; fi
  if [ -z "$row" ]; then
    out=$(herdr workspace create --cwd "$dir" --label "$label" --no-focus 2>&1); rc=$?
    pane=$(printf %s "$out" | grep -o '"pane_id" *: *"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/')
    log "workspace create $name label=$label rc=$rc pane=${pane:-none}"
    [ -n "$pane" ] || { log "ERROR $name: no pane_id in: ${out:0:200}"; continue; }
  else
    log "$name workspace restored, pane $pane has no agent; relaunching"
  fi
  sleep 2
  herdr pane run "$pane" "bash $launcher $extra" >> "$LOG" 2>&1; log "pane run $name rc=$? (bash $launcher $extra)"
done
log done
