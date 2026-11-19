---
name: ralph-loop
description: Use when a coding brief has 4+ steps that can each be checked and needs multiple passes (fix_plan items, file-by-file migrations, fixing failing tests one at a time). Covers when to loop, how to write fix_plan.md items, and how to start ralph.sh with a cap. Not for one-off fixes, renders, research, questions, or work that needs Derrick's decision part-way.
---

# Ralph loop (Forge)

Based on the community Ralph pattern: https://github.com/ghuntley/how-to-ralph-wiggum , https://github.com/snarktank/ralph
and the pi-ralph-loop skill: https://github.com/lnilluv/pi-ralph-loop/blob/main/skills/ralph-loop/SKILL.md
(wording only; the add-on is not installed).

## When to loop

| Use a loop | Don't use a loop |
|---|---|
| A brief with 4+ steps, each checkable | Fix one specific bug |
| Same code fix across several modules | Answer a question |
| Fix failing tests one at a time | Rename or one-line edit |
| Same change across many files | Anything needing Derrick's choice mid-way |
| Download/verify a list of files | Any render or research (queue run_queue.py directly) |

Rule of thumb: 4+ checkable coding steps that need several passes -> loop it; 1-3 steps stay one direct turn.
- Multi-step coding briefs (4+ checkable steps, multi-pass): do NOT do them in chat. Load skill ralph-loop, write the steps as fix_plan.md items, start ralph.sh in the background (skill "Start"), reply with PID + logs/ralph.log, and end the turn. One-off fixes and questions stay inline. 1-3 step fixes, research, and renders stay a direct turn (no Ralph; renders are queued directly with `run_queue.py`).
- If a step needs Derrick's decision, put it as the last item ("STOP and report"), or split the loop there.

## Writing fix_plan.md items
- One task per item, sized small enough to fit cleanly in one context window, self-contained: a fresh pass must do it from the item text alone (full paths, inputs, outputs).
- Each item names its check ("Done when ..." / "Pass:" plus a command or file that proves it).
- Verify before ticking: item is changed to `- [x]` with a one-line RESULT ONLY when every clause of its check passes; otherwise change its checkbox from `- [ ]` to `- [PARTIAL]` or `- [BLOCKED]` with one line why (never leave `- [ ]` on a partial or blocked item). Keep one concern per commit per repo touched, and append one line in notes\progress.md.
- Do simple edits and checks directly — never write one-off helper or probe scripts for one-off edits; only keep scripts meant to be reused.
- Order matters: the pass takes the top open `- [ ]` item (skipping `- [PARTIAL]`, `- [BLOCKED]`, and items with a `PARTIAL`/`BLOCKED` sub-bullet). Put blockers first.
- Blocks: one "## <OWNER> (<who>; brief <path>)" header per brief. Max replaces only his MAX block; Forge adds a FORGE block for its own briefs above older open blocks; never edit another owner's open items.
- Before starting a loop, clear any stale `- [ ]` items from older/closed runs in `fix_plan.md` (`ralph.sh` also archives and clears stale `fix_plan.md` items >12h old or older than a finished `DONE.txt`).
- Loop safety (`ralph.sh`): each loop gets its own git worktree (`~/AI/_worktrees/ralph-*`); edits to `skills/` and `AGENTS.md` are denied inside loops; each pass runs a backpressure check (protected paths, `git diff --stat` cap of 10 files, and a skill-load smoke test) and reverts violations.
- If an item can't finish, change its checkbox to `- [PARTIAL]` or `- [BLOCKED]` with the reason (or add a needs_derrick.md line) and stop; don't loop on it.

Start (only this; EVO-X3 Linux copy, X3 Phase 2 Derrick t1784s6566; the AlienPc copy of this skill keeps its Windows start): `cd /home/evo/AI/forge/ralph-community && nohup setsid bash ralph.sh -Max N >/dev/null 2>&1 & echo PID=$!` then reply `PID=<pid>, log /home/evo/AI/forge/ralph-community/logs/ralph.log`; cap N = item count + 2 (max 12). Long items (benchmarks): add -PassLimitSec 3600. ralph.sh runs `pi --approve --print --model x3-local/flash-next-uncensored` (same resident model as Render; subagents `-sub`) with cwd /home/evo/AI/forge (Forge's project settings), refuses a second copy (logs/ralph.lock, exit 4), never reads the model key (models.json reads it from /etc/evo-x3), and stops on PLAN_COMPLETE or NO_PROGRESS (same item still open after two passes).

## Sizing a pass over big text

- **One pass = at most 24 KB of source text.** On the local coding model a pass reads about 20-25 KB of digest and writes a structured report in 20-40 minutes. Generate the items from a manifest with a script - bins of at most 24 KB, one bin = one plan item, the file paths written inside the item - never hand-write an item that names a 50-95 KB read.
- **`-PassLimitSec 2400` for that class of item.** Set the per-pass wall-clock cap above a completed pass so passes are not killed mid-work.
- **Cap N = open item count + 2**, so a killed pass has a retry slot. **Launch detached** (`nohup setsid` as above): a loop started inside a foreground tool call dies when that tool call times out.
- **Reports are append-only.** Each pass appends its section to its report and keeps its own validator printing `ALL OK`. `write` is denied outside the loop root, so write the draft inside the root and deliver it with a shell copy.
- **Reading private chats: `-MemoryRoot <loop root>/notes/_pi_memory`**. Pass `-MemoryRoot` when reviewing private lane transcripts so pass summaries stay inside the private loop root rather than landing in `/home/evo/AI/fleet-brain/25_memory/shared/`.
- **A loop is finished only when its log says `PLAN_COMPLETE`.** Read the log and the plan before telling Derrick it completed; "done" is not a status the runner prints for a stopped loop.
