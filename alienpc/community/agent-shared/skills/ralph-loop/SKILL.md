---
name: ralph-loop
description: Use when a brief has more than ~3 steps that can each be checked, or a command can measure progress (fix_plan items, staging runs, test-until-green, file-by-file migrations). Covers when to loop, how to write fix_plan.md items, and how to start ralph.ps1 with a cap. Not for one-off fixes, questions, or work that needs Derrick's decision part-way.
---

# Ralph loop (Forge)

Based on the community Ralph pattern: https://github.com/ghuntley/how-to-ralph-wiggum , https://github.com/snarktank/ralph
and the pi-ralph-loop skill: https://github.com/lnilluv/pi-ralph-loop/blob/main/skills/ralph-loop/SKILL.md
(wording only; the add-on is not installed).

## When to loop

| Use a loop | Don't use a loop |
|---|---|
| A brief with 4+ steps, each checkable | Fix one specific bug |
| Stage several run dirs / templates in order | Answer a question |
| Fix failing tests one at a time | Rename or one-line edit |
| Same change across many files | Anything needing Derrick's choice mid-way |
| Download/verify a list of files | A single render or single command |

Rule of thumb: more than ~3 passes, or you can write a command that measures progress -> loop it.
If a step needs Derrick's decision, put it as the last item ("STOP and report"), or split the loop there.

## Writing fix_plan.md items
- One task per item, sized small enough to fit cleanly in one context window, self-contained: a fresh pass must do it from the item text alone (full paths, inputs, outputs).
- Each item names its check ("Done when ..." / "Pass:" plus a command or file that proves it).
- Verify before ticking: item is changed to `- [x]` with a one-line RESULT ONLY when every clause of its check passes; otherwise change its checkbox from `- [ ]` to `- [PARTIAL]` or `- [BLOCKED]` with one line why (never leave `- [ ]` on a partial or blocked item). Keep one concern per commit per repo touched, and append one line in notes\progress.md.
- Do simple edits and checks directly — never write one-off helper or probe scripts for one-off edits; only keep scripts meant to be reused.
- Order matters: the pass takes the top open `- [ ]` item (skipping `- [PARTIAL]`, `- [BLOCKED]`, and items with a `PARTIAL`/`BLOCKED` sub-bullet). Put blockers first.
- Blocks: one "## <OWNER> (<who>, <date time>; brief <path>)" header per brief. Max replaces only his MAX block; Forge adds a FORGE block for its own briefs above older open blocks; never edit another owner's open items.
- If an item can't finish, change its checkbox to `- [PARTIAL]` or `- [BLOCKED]` with the reason (or add a needs_derrick.md line) and stop; don't loop on it.


Start (only this): Invoke-CimMethod Win32_Process -MethodName Create -Arguments @{CommandLine='powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\derek\5slock\ralph-community\ralph.ps1 -Max N'; CurrentDirectory='C:\Users\derek\5slock\ralph-community'} then reply `PID=<ProcessId>, log ralph-community\logs\ralph.log`; cap N = item count + 2 (max 12). Long items (benchmarks, renders): add -PassLimitSec 3600. ralph.ps1 refuses a second copy (logs\ralph.lock, exit 4), loads LLAMA_SWAP_KEY from User scope if missing (exit 3), and stops on PLAN_COMPLETE or NO_PROGRESS (same item still open after two passes).

## Moved from global AGENTS.md line 11 (2026-11-05, Derrick)
- Multi-step briefs (4+ checkable steps, or a command can measure progress): do NOT do them in chat. Load skill ralph-loop, write the steps as fix_plan.md items, commit, start ralph.ps1 in the background (skill "Start"), reply with PID + logs\ralph.log, end the turn. One-off fixes and questions stay inline.

Render routing (Derrick 2026-11-05 9:21 AM CT): new render or video items go in C:\AI\render\fix_plan.md, and that loop starts with: Invoke-CimMethod Win32_Process -MethodName Create -Arguments @{CommandLine='powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\derek\5slock\ralph-community\ralph.ps1 -Root C:\AI\render -Max N'; CurrentDirectory='C:\AI\render'} (log C:\AI\render\logs\ralph.log; same cap rule, N = open items in C:\AI\render\fix_plan.md + 2, max 12). Existing `[render]`-tagged items in the main fix_plan.md finish there. Both loops can run at once; C:\AI\locks\gpu-render.lock allows one GPU job at a time.
