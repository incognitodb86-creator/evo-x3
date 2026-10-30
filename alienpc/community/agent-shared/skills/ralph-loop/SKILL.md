---
name: ralph-loop
description: Use when a brief has more than ~3 steps that can each be checked, or a command can measure progress (fix_plan items, staging runs, test-until-green, file-by-file migrations). Covers when to loop, how to write fix_plan.md items, and how to start ralph.ps1 with a cap. Not for one-off fixes, questions, or work that needs Derrick's decision part-way.
---

# Ralph loop (Forge)

Based on the community Ralph pattern: https://github.com/ghuntley/how-to-ralph-wiggum
and the pi-ralph-loop skill: https://github.com/lnilluv/pi-ralph-loop/blob/main/skills/ralph-loop/SKILL.md
(wording only; the add-on is not installed).

## The idea
- Each pass is a fresh `pi --print` with a clean context. Nothing carries over in memory.
- The plan on disk (fix_plan.md) is the memory. Git history and notes\progress.md are the record.
- One task per pass. Do it, check it, mark it, commit, stop.
- Cap the passes. Tests and check commands are the backpressure: an item is not done until its check passes.

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
- One task per item, self-contained: a fresh pass must do it from the item text alone (full paths, inputs, outputs).
- Each item names its check ("Done when ..." plus a command or file that proves it).
- Done = item changed to `- [x]` with a one-line RESULT, one commit per repo touched, one line in notes\progress.md.
- Order matters: the pass takes the top open `- [ ]` item. Put blockers first.
- Max owns the MAX block and replaces it; never stack a second block.
- If an item can't finish, mark it partial with the reason (or add a needs_derrick.md line) and stop; don't loop on it.

## Starting our loop
From C:\Users\derek\5slock\ralph-community:

    .\ralph.ps1 -Max N

- Pick N = open items + 1 or 2 spare (sensible cap: 3-12; default is 10). Never uncapped.
- Each pass runs `pi --print --provider llama-swap --model <model> @PROMPT.md`; PROMPT.md says: read fix_plan.md, do the open MAX item, check, mark [x], commit, stop.
- Per-pass output goes to logs\iter-*.log; logs\DONE.txt shows the last pass; IterationTimeoutSec (default 7200) kills a hung pass.
- Only one ralph.ps1 at a time. Check before starting: `Get-CimInstance Win32_Process | ? CommandLine -match 'ralph.ps1'`.

## Never
- Never start a loop (ralph.ps1, or any nested pi loop) from inside a loop pass. A pass does its one item and exits.
- Never edit ralph.ps1 or PROMPT.md from inside a pass.
- Never tick an item whose check did not pass.

## GPU rule
- One GPU job at a time, held under C:\AI\locks\gpu-render.lock (the lock names a live PID).
- A GPU render can't overlap Forge's own LLM work: ralph.ps1 waits (GpuWaits x GpuWaitSec) while a live render holds the lock and skips the pass if it outlasts that. Don't start a render from a pass while the loop's next pass will need the LLM; render items are staged, and the render is launched outside the loop.
- A dead PID in the lock is stale and is ignored.