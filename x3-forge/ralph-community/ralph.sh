#!/usr/bin/env bash
# Plain capped Ralph loop for Forge on the EVO-X3 (bash port of the AlienPc Windows Ralph runner + U53 safety checks).
# Runs pi --print on PROMPT.md, one fix_plan item per pass, stops at PLAN_COMPLETE, NO_PROGRESS or the -Max cap.
# Max Architect 2026-11-15, X3 Phase 2 (Derrick t1784s6566 "port ralph-loop to Linux"); U53 B3+I2 2026-11-16. Forge owns this file.
# Usage: ralph.sh [-Max 10] [-Model x3-local/flash-next-uncensored] [-PassLimitSec 3600] [-IterationTimeoutSec 7200]
#                 [-GpuWaits 30] [-GpuWaitSec 120] [-GpuLockPath <lock>] [-LockPollSec 2]
#                 [-MemoryRoot <dir>] [-WorkDir <pi cwd>] [-TargetRepo <repo|none>] [-PiCwd <work|target|dir>]
#                 [-WorktreeRoot <dir>] [-NoWorktree] [-MaxDiffFiles 10] [-StaleHours 12] [-ClearStale]
#                 [-BackpressureCmd <cmd>] [-CommandOverride <cmd>] [-LogPath <path>]
# Start detached: nohup setsid bash ralph.sh -Max N >/dev/null 2>&1 &
# Exit codes: 0 done/capped, 4 another copy running, 5 bad args.
set -uo pipefail
Max=10; Model='x3-local/flash-next-uncensored'; GpuWaits=30; GpuWaitSec=120
GpuLockPath="$HOME/AI/locks/gpu-render.lock"; IterationTimeoutSec=7200; CommandOverride=''; LogPath=''
PassLimitSec=3600; LockPollSec=2; MemoryRoot="$HOME/AI/fleet-brain/25_memory/shared"; WorkDir="$HOME/AI/forge"
TargetRepo='auto'; PiCwd='work'; WorktreeRoot="$HOME/AI/_worktrees"; NoWorktree=0
MaxDiffFiles=10; StaleHours=12; ClearStale=0; BackpressureCmd=''
while [ $# -gt 0 ]; do
  case "$1" in
    -Max|--max) Max="$2"; shift 2;;
    -Model|--model) Model="$2"; shift 2;;
    -GpuWaits) GpuWaits="$2"; shift 2;;
    -GpuWaitSec) GpuWaitSec="$2"; shift 2;;
    -GpuLockPath) GpuLockPath="$2"; shift 2;;
    -IterationTimeoutSec) IterationTimeoutSec="$2"; shift 2;;
    -PassLimitSec|--pass-limit-sec) PassLimitSec="$2"; shift 2;;
    -LockPollSec) LockPollSec="$2"; shift 2;;
    -MemoryRoot|--memory-root) MemoryRoot="$2"; shift 2;;
    -WorkDir) WorkDir="$2"; shift 2;;
    -TargetRepo) TargetRepo="$2"; shift 2;;
    -PiCwd|--pi-cwd) PiCwd="$2"; shift 2;;
    -WorktreeRoot) WorktreeRoot="$2"; shift 2;;
    -NoWorktree) NoWorktree=1; shift 1;;
    -MaxDiffFiles) MaxDiffFiles="$2"; shift 2;;
    -StaleHours) StaleHours="$2"; shift 2;;
    -ClearStale) ClearStale=1; shift 1;;
    -BackpressureCmd) BackpressureCmd="$2"; shift 2;;
    -CommandOverride) CommandOverride="$2"; shift 2;;
    -LogPath) LogPath="$2"; shift 2;;
    *) echo "unknown arg $1" >&2; exit 5;;
  esac
done
K="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$K" || exit 5
day=$(date +%Y%m%d)
if [ -n "$LogPath" ]; then logDir="$(dirname "$(realpath -m "$LogPath")")"; idx="$(realpath -m "$LogPath")"
elif [ -n "$CommandOverride" ]; then logDir="${TMPDIR:-/tmp}/ralph_override_$$"; idx="$logDir/ralph.log"
else logDir="$K/logs"; idx="$logDir/ralph.log"; fi
mkdir -p "$K/logs" "$K/sessions" "$K/notes" "$K/_archive" "$logDir"
run="$logDir/ralph-$day-$$.log"
log() { local l; l="$(date +%Y-%m-%dT%H:%M:%S) $*"; printf '%s\n' "$l" >>"$idx"; printf '%s\n' "$l" >>"$run"; printf '%s\n' "$l"; }
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
export PATH="$HOME/AI/render/x3/.venv/bin:$HOME/.local/bin:$PATH"
# The model key is read by pi's models.json (!command from /etc/evo-x3); this script never reads or exports it.
lock="$K/logs/ralph.lock"
if [ -f "$lock" ]; then
  lp="$(tr -dc '0-9' <"$lock")"
  if [ -n "$lp" ] && [ "$lp" != "$$" ] && kill -0 "$lp" 2>/dev/null; then log "ALREADY_RUNNING pid $lp - second loop not started"; exit 4; fi
  log "stale ralph.lock (pid ${lp:-?} not alive) - taking it"
fi
echo $$ >"$lock"

loopPolicyDir=""
CURRENT_PASS_PID=""
wtWorkDir=""; wtWorkRepo=""; wtWorkStart=""
wtTargetDir=""; wtTargetRepo=""; wtTargetStart=""
PassCwd=""

kill_tree() { # kill the pass's whole setsid process group (-PGID) so pi children cannot orphan to ppid 1
  local p="${1:-}"
  [ -n "$p" ] && [ "$p" -gt 1 ] 2>/dev/null || return 0
  kill -TERM -- "-$p" 2>/dev/null || kill -TERM "$p" 2>/dev/null || true
  sleep 2
  kill -KILL -- "-$p" 2>/dev/null || kill -KILL "$p" 2>/dev/null || true
}

cleanup() {
  trap - EXIT INT TERM
  if [ -n "${CURRENT_PASS_PID:-}" ]; then
    log "CLEANUP killing active pass process group PID $CURRENT_PASS_PID"
    kill_tree "$CURRENT_PASS_PID"
    wait "$CURRENT_PASS_PID" 2>/dev/null || true
    CURRENT_PASS_PID=""
  fi
  rm -f "$lock"
  [ -n "$loopPolicyDir" ] && rm -rf "$loopPolicyDir"
}
trap 'cleanup; exit 143' TERM
trap 'cleanup; exit 130' INT
trap cleanup EXIT
stall=0; stopReason=''

# GPU lock rule: test with flock -n (same as queue-remote.sh / remote_comfy.py).
# A 0-byte or unlocked file is free; only an active flock is busy.
lock_pid() { [ -f "$GpuLockPath" ] || { echo 0; return; }; local p; p="$(grep -oE '[0-9]+' "$GpuLockPath" | head -1)"; echo "${p:--1}"; }
gpu_busy() {
  [ -e "$GpuLockPath" ] || return 1
  if ! flock -n "$GpuLockPath" true 2>/dev/null; then
    local p; p="$(lock_pid)"
    if [ "$p" -gt 0 ] 2>/dev/null; then
      BUSY="flock held on $GpuLockPath (pid $p)"
    else
      BUSY="flock held on $GpuLockPath"
    fi
    return 0
  fi
  return 1
}
in_tree() { # $1 child pid, $2 root pid
  local cur="$1" n=0
  while [ "$n" -lt 32 ] && [ "${cur:-0}" -gt 0 ]; do
    [ "$cur" = "$2" ] && return 0
    cur="$(ps -o ppid= -p "$cur" 2>/dev/null | tr -d ' ')"; n=$((n+1))
  done
  return 1
}
top_item() {
  local t; t="$(grep -m1 -E '^\s*- \[ \]' "$K/fix_plan.md" 2>/dev/null | sed -E 's/^\s+//')"
  [ -z "$t" ] && { echo '(none)'; return; }; echo "${t:0:90}"
}
mtime() { stat -c %Y "$1" 2>/dev/null || echo 0; }

# I2-1: Clear stale fix_plan.md items before starting the loop so leftover items from earlier runs never execute.
clear_stale_fix_plan() {
  local fp="$K/fix_plan.md"
  [ -f "$fp" ] || return 0
  local hasOpen=0
  grep -qE '^\s*- \[ \]' "$fp" 2>/dev/null && hasOpen=1
  local now fpMtime doneMtime ageSec staleReason=""
  now=$(date +%s); fpMtime=$(mtime "$fp"); ageSec=$((now - fpMtime))
  if [ "$ClearStale" = 1 ]; then
    staleReason="explicit -ClearStale"
  elif [ "$hasOpen" = 1 ] && [ "$StaleHours" -gt 0 ] && [ "$ageSec" -gt $((StaleHours * 3600)) ]; then
    staleReason="fix_plan.md older than ${StaleHours}h (${ageSec}s)"
  elif [ "$hasOpen" = 1 ] && [ -f "$logDir/DONE.txt" ] && grep -q 'done=true' "$logDir/DONE.txt" 2>/dev/null; then
    if python3 -c 'import os,sys; sys.exit(0 if os.stat(sys.argv[1]).st_mtime_ns > os.stat(sys.argv[2]).st_mtime_ns else 1)' "$logDir/DONE.txt" "$fp"; then
      staleReason="previous DONE.txt (done=true) is newer than fix_plan.md"
    fi
  fi
  if [ -n "$staleReason" ]; then
    local arch="$K/_archive/fix_plan.stale-$(date +%Y%m%d-%H%M%S).md"
    cp -p "$fp" "$arch"
    python3 - "$fp" << "PY"
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
lines = p.read_text(encoding="utf-8", errors="replace").splitlines(True)
kept = [ln for ln in lines if not re.match(r"^\s*- \[ \]", ln)]
p.write_text("".join(kept), encoding="utf-8")
PY
    log "STALE_FIX_PLAN_CLEARED ($staleReason) - archived to $arch; cleared unchecked items"
  fi
}

# I2-4 (tool layer): Build a loop-scoped pi-permissions.jsonc denying edits to skills/ and AGENTS.md inside loops.
build_loop_policy() {
  local basePolicy="$HOME/.pi/agent/pi-permissions.jsonc"
  loopPolicyDir="$logDir/loop-policy-$$"
  mkdir -p "$loopPolicyDir"
  python3 - "$basePolicy" "$loopPolicyDir/pi-permissions.jsonc" << "PY"
import pathlib, re, sys

src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
text = src.read_text(encoding="utf-8") if src.is_file() else "{\n  \"tools\": {},\n  \"bash\": {}\n}\n"

tool_rules = """
    // I2 loop guard: deny edits to skills/ and AGENTS.md from inside Ralph loops
    "skill_manage": "deny",
    "edit:*/skills/*": "deny",
    "write:*/skills/*": "deny",
    "edit:*skills/*": "deny",
    "write:*skills/*": "deny",
    "edit:*/AGENTS.md": "deny",
    "write:*/AGENTS.md": "deny",
    "edit:AGENTS.md": "deny",
    "write:AGENTS.md": "deny",
"""
bash_rules = """
    // I2 loop guard: deny shell writes to skills/ and AGENTS.md from inside Ralph loops
    "*sed *skills/*": "deny",
    "*sed *AGENTS.md*": "deny",
    "*tee *skills/*": "deny",
    "*tee *AGENTS.md*": "deny",
    "*>*skills/*": "deny",
    "*>*AGENTS.md*": "deny",
    "*rm *skills/*": "deny",
    "*rm *AGENTS.md*": "deny",
    "*mv *skills/*": "deny",
    "*mv *AGENTS.md*": "deny",
    "*cp *skills/*": "deny",
    "*cp *AGENTS.md*": "deny",
    "*python*skills/*": "deny",
    "*python*AGENTS.md*": "deny",
"""

def inject(doc: str, section: str, snippet: str) -> str:
    m = re.search(rf'"{re.escape(section)}"\s*:\s*\{{', doc)
    if not m:
        return doc
    depth = 1
    i = m.end()
    in_str = False
    esc = False
    in_line_comment = False
    while i < len(doc):
        ch = doc[i]
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
        elif in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == "/" and i + 1 < len(doc) and doc[i + 1] == "/":
                in_line_comment = True
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return doc[:i] + snippet + "  " + doc[i:]
        i += 1
    return doc

text = inject(text, "tools", tool_rules)
text = inject(text, "bash", bash_rules)
dst.write_text(text, encoding="utf-8")
PY
  export PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR="$loopPolicyDir"
}

# I2-5: One git worktree per loop.
setup_worktrees() {
  RunWorkDir="$K"
  [ -d "$WorkDir" ] && RunWorkDir="$WorkDir"
  if [ "$NoWorktree" = 1 ]; then
    log "WORKTREE disabled (-NoWorktree); cwd=$RunWorkDir"
    return 0
  fi
  local tag="ralph-$day-$$"
  local loopDir="$WorktreeRoot/$tag"
  mkdir -p "$loopDir"
  local workRoot=""
  workRoot="$(git -C "$WorkDir" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$workRoot" ]; then
    wtWorkRepo="$workRoot"
    wtWorkStart="$(git -C "$workRoot" rev-parse HEAD)"
    wtWorkDir="$loopDir/$(basename "$workRoot")"
    local br="${tag}-$(basename "$workRoot")"
    if git -C "$workRoot" worktree add -b "$br" "$wtWorkDir" HEAD >/dev/null 2>&1; then
      # Symlink untracked pi runtime dirs (.pi/npm, .pi/git) if WorkDir is forge
      for sub in npm git; do
        if [ -e "$workRoot/.pi/$sub" ] && [ ! -e "$wtWorkDir/.pi/$sub" ]; then
          mkdir -p "$wtWorkDir/.pi"
          ln -s "$workRoot/.pi/$sub" "$wtWorkDir/.pi/$sub"
        fi
      done
      RunWorkDir="$wtWorkDir"
      export RALPH_FORGE_WORKTREE="$wtWorkDir"
      log "WORKTREE work repo=$workRoot branch=$br path=$wtWorkDir"
    else
      log "WORKTREE_WARN failed to create worktree for $workRoot; using $WorkDir"
      wtWorkDir=""; wtWorkRepo=""
    fi
  fi

  local resolvedTarget=""
  if [ "$TargetRepo" = "none" ]; then
    resolvedTarget=""
  elif [ "$TargetRepo" = "auto" ]; then
    [ -d "$HOME/AI/community/.git" ] && resolvedTarget="$HOME/AI/community"
  else
    resolvedTarget="$TargetRepo"
  fi
  if [ -n "$resolvedTarget" ]; then
    local tRoot=""
    tRoot="$(git -C "$resolvedTarget" rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -n "$tRoot" ] && [ "$tRoot" != "$wtWorkRepo" ]; then
      wtTargetRepo="$tRoot"
      wtTargetStart="$(git -C "$tRoot" rev-parse HEAD)"
      wtTargetDir="$loopDir/$(basename "$tRoot")"
      local tbr="${tag}-$(basename "$tRoot")"
      if git -C "$tRoot" worktree add -b "$tbr" "$wtTargetDir" HEAD >/dev/null 2>&1; then
        for sub in npm git; do
          if [ -e "$tRoot/.pi/$sub" ] && [ ! -e "$wtTargetDir/.pi/$sub" ]; then
            mkdir -p "$wtTargetDir/.pi"
            ln -s "$tRoot/.pi/$sub" "$wtTargetDir/.pi/$sub"
          fi
        done
        export RALPH_WORKTREE="$wtTargetDir"
        log "WORKTREE target repo=$tRoot branch=$tbr path=$wtTargetDir"
      else
        log "WORKTREE_WARN failed to create worktree for $tRoot"
        wtTargetDir=""; wtTargetRepo=""
      fi
    fi
  fi
  # Ensure relative symlink forge/AGENTS.md -> ../community/agent-shared/AGENTS.md resolves if community wasn't cloned into loopDir
  if [ -n "$wtWorkDir" ] && [ ! -e "$loopDir/community" ] && [ -d "$HOME/AI/community" ]; then
    ln -s "$HOME/AI/community" "$loopDir/community"
  fi
}

# -PiCwd: where pi runs each pass. work = WorkDir (or its loop worktree), target = TargetRepo (or its loop worktree), else a path.
resolve_pass_cwd() {
  local tgt=""
  case "$TargetRepo" in auto) [ -d "$HOME/AI/community/.git" ] && tgt="$HOME/AI/community";; none) ;; *) tgt="$TargetRepo";; esac
  case "$PiCwd" in
    target) PassCwd="${wtTargetDir:-${tgt:-$RunWorkDir}}" ;;
    work|"") PassCwd="$RunWorkDir" ;;
    *) PassCwd="$PiCwd" ;;
  esac
  [ -d "$PassCwd" ] || { log "BAD_ARGS -PiCwd resolved to missing dir: $PassCwd"; exit 5; }
  log "PI_CWD $PiCwd -> $PassCwd"
}

# Record git HEADs before a pass.
declare -A PRE_HEAD
declare -A PRE_DIRTY
repo_dirty_lines() {
  local repo="$1" ph="$2"
  { git -C "$repo" diff --name-only "$ph" 2>/dev/null; git -C "$repo" status --porcelain 2>/dev/null | sed -E 's/^.. //; s/^.* -> //'; }     | grep -v '^$'     | grep -vE '^(ralph-community/(fix_plan\.md|notes/|logs/|sessions/|_archive/)|\.pi/(npm|git)$|dummy_run/|scripts/dummy_run/)'     | sort -u || true
}
record_pre_pass() {
  PRE_HEAD=()
  PRE_DIRTY=()
  for r in "$wtWorkDir" "$wtTargetDir" "$WorkDir" "$HOME/AI/community" "$HOME/AI/forge"; do
    [ -n "$r" ] && [ -d "$r" ] || continue
    local realR; realR="$(realpath "$r" 2>/dev/null || echo "$r")"
    git -C "$realR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || continue
    local ph; ph="$(git -C "$realR" rev-parse HEAD 2>/dev/null || true)"
    PRE_HEAD["$realR"]="$ph"
    PRE_DIRTY["$realR"]="$(repo_dirty_lines "$realR" "$ph")"
  done
}

revert_worktrees_to_pre() {
  for r in "$wtWorkDir" "$wtTargetDir"; do
    [ -n "$r" ] && [ -d "$r" ] || continue
    local ph="${PRE_HEAD[$r]:-}"
    [ -n "$ph" ] && git -C "$r" reset --hard "$ph" >/dev/null 2>&1 || true
    git -C "$r" clean -fd >/dev/null 2>&1 || true
  done
}

# I2-2, I2-3, I2-4: Per-pass backpressure check (protected paths, git diff --stat cap, skill-load smoke test).
run_backpressure() {
  local iterNum="$1"
  local failReason=""

  # Check every tracked worktree/repo for protected path edits and diff file cap
  local totalChanged=0
  local seenRepos=""
  for r in "$wtWorkDir" "$wtTargetDir" "$HOME/AI/community" "$HOME/AI/forge"; do
    [ -n "$r" ] && [ -d "$r" ] || continue
    local realR; realR="$(realpath "$r" 2>/dev/null || echo "$r")"
    case " $seenRepos " in *" $realR "*) continue;; esac
    seenRepos="$seenRepos $realR"
    git -C "$realR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || continue

    local ph="${PRE_HEAD[$realR]:-HEAD}"
    local curDirty="" diffNames=""
    curDirty="$(repo_dirty_lines "$realR" "$ph")"
    if [ -n "$curDirty" ]; then
      diffNames="$(comm -23 <(printf '%s\n' "$curDirty" | sort -u) <(printf '%s\n' "${PRE_DIRTY[$realR]:-}" | grep -v '^$' | sort -u) || true)"
    fi

    if [ -n "$diffNames" ]; then
      local statLine
      statLine="$(git -C "$realR" diff --stat "$ph" 2>/dev/null | tail -n 1 || true)"
      log "iter $iterNum : git diff --stat ($realR): ${statLine:-untracked-only}"

      # I2-4: Deny edits to skills/ and AGENTS.md inside loops
      local badProt
      badProt="$(printf '%s\n' "$diffNames" | grep -E '(^|/)skills/|(^|/)AGENTS\.md$' || true)"
      if [ -n "$badProt" ]; then
        failReason="protected path edited inside loop ($realR): $(echo "$badProt" | tr '\n' ',')"
        break
      fi

      local cnt
      cnt="$(printf '%s\n' "$diffNames" | wc -l | tr -d ' ')"
      totalChanged=$((totalChanged + cnt))
    fi
  done

  if [ -z "$failReason" ] && [ "$totalChanged" -gt "$MaxDiffFiles" ]; then
    failReason="git diff --stat file cap exceeded ($totalChanged > $MaxDiffFiles files)"
  fi

  # I2-2: Skill-load smoke test
  if [ -z "$failReason" ]; then
    local settingsTarget="$RunWorkDir/.pi/settings.json"
    [ -f "$settingsTarget" ] || settingsTarget="$HOME/AI/forge/.pi/settings.json"
    local commRoot="${wtTargetDir:-$HOME/AI/community}"
    local forgeRoot="${wtWorkDir:-$HOME/AI/forge}"
    local smokeOut=""
    if ! smokeOut="$(python3 - "$settingsTarget" "$forgeRoot" "$commRoot" 2>&1 << "PY"
import json, os, pathlib, re, sys

settings_path = pathlib.Path(sys.argv[1])
forge_root = pathlib.Path(sys.argv[2])
comm_root = pathlib.Path(sys.argv[3])

cfg = json.loads(settings_path.read_text(encoding="utf-8"))
agents_md = forge_root / "AGENTS.md"
if not agents_md.exists() or not agents_md.read_text(encoding="utf-8").strip():
    raise SystemExit(f"AGENTS.md missing or empty at {agents_md}")

def remap(p_str: str) -> pathlib.Path:
    expanded = os.path.expanduser(p_str)
    for prefix in ("/home/evo/AI/community", "/home/derekboone/AI/community", os.path.expanduser("~/AI/community")):
        if expanded.startswith(prefix):
            return pathlib.Path(str(comm_root) + expanded[len(prefix):])
    return pathlib.Path(expanded)

for ext in cfg.get("extensions", []):
    if ext.startswith("-"):
        continue
    ep = remap(ext)
    if not ep.exists():
        raise SystemExit(f"missing extension path: {ep}")

excludes = {str(remap(s[1:])) for s in cfg.get("skills", []) if s.startswith("-")}
includes = [s for s in cfg.get("skills", []) if not s.startswith("-")]
loaded = 0
for inc in includes:
    root = remap(inc)
    if not root.is_dir():
        raise SystemExit(f"missing skill root: {root}")
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith(".") or child.name == "_archive":
            continue
        if str(child) in excludes:
            continue
        bak = [b.name for b in child.glob("*.bak-*")]
        if bak:
            raise SystemExit(f"leftover backup in skill {child}: {bak}")
        sfile = child / "SKILL.md"
        if not sfile.is_file():
            raise SystemExit(f"missing SKILL.md in {child}")
        txt = sfile.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
        if not m or not re.search(r"(?m)^name:\s*\S+", m.group(1)) or not re.search(r"(?m)^description:\s*\S+", m.group(1)):
            raise SystemExit(f"invalid skill frontmatter: {sfile}")
        loaded += 1
if loaded == 0:
    raise SystemExit("no skills loaded")
print(f"SKILL_SMOKE_OK skills={loaded} changed_files={0}")
PY
)"; then
      failReason="skill-load smoke failed: $smokeOut"
    else
      log "iter $iterNum : $smokeOut (changed_files=$totalChanged cap=$MaxDiffFiles)"
    fi
  fi

  if [ -z "$failReason" ] && [ -n "$BackpressureCmd" ]; then
    # Commit the target worktree was at before this pass, so a backpressure command can lint only what changed.
    if [ -n "${wtTargetDir:-}" ]; then
      RALPH_PASS_BASE="${PRE_HEAD[$(realpath "$wtTargetDir" 2>/dev/null || echo "$wtTargetDir")]:-}"; export RALPH_PASS_BASE
    fi
    if ! bash -c "cd \"$RunWorkDir\" && $BackpressureCmd" >>"$idx" 2>&1; then
      failReason="BackpressureCmd failed: $BackpressureCmd"
    fi
  fi

  if [ -n "$failReason" ]; then
    log "iter $iterNum : BACKPRESSURE_FAIL: $failReason"
    return 1
  fi
  log "iter $iterNum : BACKPRESSURE_OK (changed_files=$totalChanged cap=$MaxDiffFiles)"
  return 0
}

clear_stale_fix_plan
build_loop_policy
setup_worktrees
resolve_pass_cwd

for ((i=1; i<=Max; i++)); do
  log "iter $i of $Max start"
  gpuWait=0; BUSY=''
  while gpu_busy && [ "$gpuWait" -lt "$GpuWaits" ]; do
    if [ "$gpuWait" -eq 0 ] || [ $((gpuWait % 5)) -eq 0 ]; then log "iter $i : GPU_BUSY defers the pass ($BUSY) - no LLM request while a GPU job runs; waited $gpuWait of $GpuWaits"; fi
    sleep "$GpuWaitSec"; gpuWait=$((gpuWait+1))
  done
  if gpu_busy; then log "iter $i : GPU_DEFERRED - the GPU window outlasted $GpuWaits waits ($BUSY); skipping this pass, no LLM request"; continue; fi
  [ "$gpuWait" -gt 0 ] && log "iter $i : GPU_CLEAR after $gpuWait waits"

  iterLog="$(printf '%s/iter-%s-%02d.log' "$logDir" "$day" "$i")"; iterTmp="${iterLog%.log}.tmp.log"; rm -f "$iterTmp"
  hb="$K/notes/heartbeat.txt"; prog="$K/notes/progress.md"
  topItem="$(top_item)"
  if [ "$topItem" = '(none)' ]; then log "iter $i : PLAN_COMPLETE - no open item, loop stopped"; echo "iter=$i max=$Max done=true reason=plan_complete" >"$logDir/DONE.txt"; stopReason=plan_complete; break; fi
  progBefore="$(mtime "$prog")"
  fpSnapshot="$logDir/fix_plan.pre-$i.bak"
  cp -p "$K/fix_plan.md" "$fpSnapshot"
  record_pre_pass
  passCap=$(( PassLimitSec < IterationTimeoutSec ? PassLimitSec : IterationTimeoutSec ))
  echo "$(date +%Y-%m-%dT%H:%M:%S) iter=$i state=start cap=${passCap}s item=$topItem" >"$hb"
  # Shared fleet memory for this pass only (process scope; Sydney's sessions never see it).
  export PI_MEMORY_DIR="$MemoryRoot"; mkdir -p "$MemoryRoot"
  passDir="${PassCwd:-$RunWorkDir}"
  log "iter $i : PI_MEMORY_DIR=$PI_MEMORY_DIR cwd=$passDir (process scope, this pass only)"
  if [ -n "$CommandOverride" ]; then
    setsid bash -c "cd \"$passDir\" && $CommandOverride" >"$iterTmp" 2>&1 &
  else
    setsid bash -c 'cd "$1" && exec pi --approve --print --model "$2" --no-session "@$3/PROMPT.md" "Follow PROMPT.md for the top unchecked - [ ] item in $3/fix_plan.md, then stop."' _ "$passDir" "$Model" "$K" >"$iterTmp" 2>&1 &
  fi
  pp=$!; CURRENT_PASS_PID="$pp"; start=$(date +%s); lockEnd=''; timedOut=0
  while kill -0 "$pp" 2>/dev/null; do
    sleep "$LockPollSec"
    if gpu_busy; then lp="$(lock_pid)"; if [ "$lp" -le 0 ] || ! in_tree "$lp" "$pp"; then lockEnd="$BUSY"; break; fi; fi
    if [ $(( $(date +%s) - start )) -ge "$passCap" ]; then timedOut=1; break; fi
  done
  if [ -n "$lockEnd" ]; then
    log "iter $i : GPU_LOCK_MIDPASS ($lockEnd) - GPU window opened outside this pass; ending the pass now (pi tree PID $pp)"
    kill_tree "$pp"; wait "$pp" 2>/dev/null; CURRENT_PASS_PID=""; piRc=125
  elif [ "$timedOut" = 1 ]; then
    log "iter $i : ITERATION_TIMEOUT after ${passCap}s - killing process tree PID $pp..."
    kill_tree "$pp"; wait "$pp" 2>/dev/null; CURRENT_PASS_PID=""; piRc=124
  else
    wait "$pp"; piRc=$?; CURRENT_PASS_PID=""
  fi
  [ -f "$iterTmp" ] && mv -f "$iterTmp" "$iterLog"
  if [ "$piRc" -ne 0 ]; then log "iter $i : PI_NONZERO rc=$piRc - pass text in $iterLog"; else log "iter $i : pass complete rc=0"; fi

  if ! run_backpressure "$i"; then
    revert_worktrees_to_pre
    cp -p "$fpSnapshot" "$K/fix_plan.md"
    piRc=126
    log "iter $i : reverted worktree and fix_plan.md after BACKPRESSURE_FAIL"
  fi
  rm -f "$fpSnapshot"

  sha="$(git -C "${wtWorkDir:-$K}" rev-parse --short HEAD 2>/dev/null)"
  if [ "$(mtime "$prog")" -le "$progBefore" ]; then echo "- $(date +%Y-%m-%dT%H:%M:%S) [ralph.sh auto] iter $i rc=$piRc head=$sha item: $topItem (model wrote no progress line)" >>"$prog"; log "iter $i : progress line written by harness"; fi
  echo "$(date +%Y-%m-%dT%H:%M:%S) iter=$i state=end rc=$piRc head=$sha item=$topItem" >"$hb"
  echo "iter=$i max=$Max pi_rc=$piRc gpu_wait=$gpuWait" >"$logDir/DONE.txt"
  afterItem="$(top_item)"
  if [ "$afterItem" != '(none)' ] && [ "$afterItem" = "$topItem" ]; then stall=$((stall+1)); else stall=0; fi
  if [ "$stall" -ge 2 ]; then log "iter $i : NO_PROGRESS on same item twice - stopped ($topItem)"; echo "iter=$i max=$Max done=true reason=no_progress" >"$logDir/DONE.txt"; stopReason=no_progress; break; fi
  sleep 2
done
if [ -z "$stopReason" ]; then
  # a final check so a plan finished on the last pass reports PLAN_COMPLETE
  if [ "$(top_item)" = '(none)' ]; then log "PLAN_COMPLETE - no open item after the last pass"; echo "iter=$Max max=$Max done=true reason=plan_complete" >"$logDir/DONE.txt"
  else log "max iterations ($Max) reached - loop stopped at cap"; echo "iter=$Max max=$Max done=true" >"$logDir/DONE.txt"; fi
fi
exit 0
