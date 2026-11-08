---
name: ralph-loop
description: Use when a coding brief has 4+ steps that can each be checked and needs multiple passes (fix_plan items, file-by-file migrations, fixing failing tests one at a time). Covers when to loop, how to write fix_plan.md items, and how to start ralph.ps1 with a cap. Not for one-off fixes, renders, research, questions, or work that needs Derrick's decision part-way.
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
If a step needs Derrick's decision, put it as the last item ("STOP and report"), or split the loop there.

## Writing fix_plan.md items
- One task per item, sized small enough to fit cleanly in one context window, self-contained: a fresh pass must do it from the item text alone (full paths, inputs, outputs).
- Each item names its check ("Done when ..." / "Pass:" plus a command or file that proves it).
- Verify before ticking: item is changed to `- [x]` with a one-line RESULT ONLY when every clause of its check passes; otherwise change its checkbox from `- [ ]` to `- [PARTIAL]` or `- [BLOCKED]` with one line why (never leave `- [ ]` on a partial or blocked item). Keep one concern per commit per repo touched, and append one line in notes\progress.md.
- Do simple edits and checks directly — never write one-off helper or probe scripts for one-off edits; only keep scripts meant to be reused.
- Order matters: the pass takes the top open `- [ ]` item (skipping `- [PARTIAL]`, `- [BLOCKED]`, and items with a `PARTIAL`/`BLOCKED` sub-bullet). Put blockers first.
- Blocks: one "## <OWNER> (<who>, <date time>; brief <path>)" header per brief. Max replaces only his MAX block; Forge adds a FORGE block for its own briefs above older open blocks; never edit another owner's open items.
- If an item can't finish, change its checkbox to `- [PARTIAL]` or `- [BLOCKED]` with the reason (or add a needs_derrick.md line) and stop; don't loop on it.


Start (only this): Invoke-CimMethod Win32_Process -MethodName Create -Arguments @{CommandLine='powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\derek\5slock\ralph-community\ralph.ps1 -Max N'; CurrentDirectory='C:\Users\derek\5slock\ralph-community'} then reply `PID=<ProcessId>, log ralph-community\logs\ralph.log`; cap N = item count + 2 (max 12). Long items (benchmarks): add -PassLimitSec 3600. ralph.ps1 refuses a second copy (logs\ralph.lock, exit 4), loads LLAMA_SWAP_KEY from User scope if missing (exit 3), and stops on PLAN_COMPLETE or NO_PROGRESS (same item still open after two passes).

## Moved from global AGENTS.md line 11 (2026-11-05, Derrick)
- Multi-step coding briefs (4+ checkable steps, multi-pass): do NOT do them in chat. Load skill ralph-loop, write the steps as fix_plan.md items, commit, start ralph.ps1 in the background (skill "Start"), reply with PID + logs\ralph.log, end the turn. One-off fixes and questions stay inline. 1-3 step fixes, research and renders stay a direct turn (no Ralph).

Superseded 2026-11-06 (Derrick t395u): renders are queued directly with run_queue.py on the saved graph, not as Ralph items. Historical: Render routing (Derrick 2026-11-05 9:21 AM CT): new render or video items go in C:\AI\render\fix_plan.md; start with -Root C:\AI\render -PromptFile C:\Users\derek\5slock\ralph-community\PROMPT.md (one PROMPT.md for both roots since the 2026-11-05 cleanup; a render start without -PromptFile points at the archived C:\AI\render\PROMPT.md and runs no prompt) (log C:\AI\render\logs\ralph.log; same cap rule). Existing `[render]`-tagged items in the main fix_plan.md finish there. Both loops can run at once; see GPU-lock rule in C:\AI\render\AGENTS.md.


## Sizing a pass over big text (2026-11-08, measured on the 30-chat Sydney lane review)

Learning: `C:/AI/fleet-brain/20_learnings/fleet/2026-11-08-large-text-ralph-passes-need-24k-bytes-and-a-private-memory-root.md` (unreviewed).

- **One pass = at most 24 KB of source text.** On this box's local coding model a pass reads about 20-25 KB of digest and writes a structured report in 20-40 minutes. Generate the items from a manifest with a script - bins of at most 24 KB, one bin = one plan item, the file paths written inside the item - never hand-write an item that names a 50-95 KB read.
- **`-PassLimitSec 2400 -IdleTimeout 900` for that class of item.** A too-small limit is worse than a big one: 1500 s killed every pass of a 50 KB-item loop mid-work (`ITERATION_TIMEOUT` + `PI_NONZERO rc=124`), two kills on one item read as `NO_PROGRESS`, and the loop stopped with real work unfinished. Set the cap above a measured completed pass, not below a guess.
- **Cap N = open item count + 2**, so a killed pass has a retry slot. **Launch detached** (`Start-Process`, or `Invoke-CimMethod` as above): a loop started inside a foreground tool call dies when that tool call times out.
- **Reports are append-only.** Each pass appends its section to its report and keeps its own validator printing `ALL OK`. `write` is denied outside the loop root, so write the draft inside the root and deliver it with a shell copy.
- **Reading private chats: `-MemoryRoot <loop root>/notes/_pi_memory`** (parameter added 2026-11-08, empty keeps the old default exactly). Without it every pass summary lands in `C:/AI/fleet-brain/25_memory/shared/daily/`, which is fleet-visible on the box; the daily file for 2026-11-07 carried 42 real-name strings from a lane-chat review (kept out of git by `25_memory/shared/.gitignore`, which is not a privacy boundary).
- **A loop is finished only when its log says `PLAN_COMPLETE`.** Read the log and the plan before telling Derrick it completed; "done" is not a status the runner prints for a stopped loop.
