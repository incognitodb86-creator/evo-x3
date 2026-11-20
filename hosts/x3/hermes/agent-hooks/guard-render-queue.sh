#!/usr/bin/env bash
# Hermes pre_tool_call shell hook (matcher: "terminal", fail_closed: true).
# Defense-in-depth guardrail on top of queue-remote.sh / flux_still.py:
#   1. Blocks queuing a video or Flux still without --yes-derrick.
#   2. Blocks queuing any run folder that still contains clip_NOT_READY.txt or still_NOT_READY.txt.
# Reads Hermes hook JSON payload from stdin; emits {"decision":"block","reason":"..."} or {}.
set -euo pipefail

exec python3 -c '
import json, os, re, sys

try:
    payload = json.load(sys.stdin)
except Exception as e:
    print(json.dumps({"decision": "block", "reason": f"guard-render-queue: invalid hook payload ({e})"}))
    sys.exit(0)

tool = str(payload.get("tool_name") or "")
inp = payload.get("tool_input") or {}
cmd = str(inp.get("command") or "") if isinstance(inp, dict) else ""

if (tool and tool != "terminal") or not cmd.strip():
    print("{}")
    sys.exit(0)

is_queue_remote = bool(re.search(r"\bqueue-remote\.sh\b", cmd)) and "--dry-run" not in cmd
is_flux_queue = bool(re.search(r"\bflux_still\.py\b", cmd)) and bool(re.search(r"(?:^|\s)--queue(?:\s|$)", cmd))
is_pipe_queue = bool(re.search(r"\brender_writer_pipeline\.py\b", cmd)) and bool(re.search(r"(?:^|\s)--queue(?:\s|$)", cmd))
is_rq_remote = bool(re.search(r"\brun_queue\.py\b", cmd)) and "--dry-run" not in cmd
# 2026-11-20 REA pipeline: its GPU stages (`flux ... --queue`, `queue`) call flux_still/queue-remote internally.
is_rea_queue = bool(re.search(r"\brea_parody_remake\.py\b", cmd)) and bool(
    re.search(r"(?:^|\s)--queue(?:\s|$)", cmd) or re.search(r"\brea_parody_remake\.py\s+queue\b", cmd))

if not (is_queue_remote or is_flux_queue or is_pipe_queue or is_rq_remote or is_rea_queue):
    print("{}")
    sys.exit(0)

if (is_queue_remote or is_flux_queue or is_pipe_queue or is_rea_queue) and not re.search(r"(?:^|\s)--yes-derrick(?:\s|$)", cmd):
    print(json.dumps({
        "decision": "block",
        "reason": "guard-render-queue: queuing requires --yes-derrick after Derrick\x27s explicit yes in chat",
    }))
    sys.exit(0)

runs_root = os.environ.get("EVO_RUNS_ROOT", "/home/evo/AI/community/runs").rstrip("/")
pattern = re.escape(runs_root) + r"/([^/\s\x27\"`]+)"
for m in re.finditer(pattern, cmd):
    run_dir = os.path.join(runs_root, m.group(1))
    for marker in ("clip_NOT_READY.txt", "still_NOT_READY.txt"):
        p = os.path.join(run_dir, marker)
        if os.path.isfile(p):
            try:
                lines = open(p, encoding="utf-8", errors="replace").read().strip().splitlines()
                why = (lines[0] if lines else marker)[:200]
            except OSError:
                why = marker
            print(json.dumps({
                "decision": "block",
                "reason": f"guard-render-queue: run {m.group(1)} is NOT_READY ({why})",
            }))
            sys.exit(0)

print("{}")
'
