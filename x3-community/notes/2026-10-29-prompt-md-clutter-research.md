# 2026-10-29 - PROMPT.md is clutter: measurement, community basis, and a rebuild proposal

Ask (Derek 2026-10-29 08:4x CT): "do research this is confusing and clutter and carries weird shit. How would you improve it?"
Scope: research + proposal only. **PROMPT.md was not edited by this note's pass.** Probe: `notes/prompt_md_clutter_probe.py` (read-only, CPU, no GPU, no ComfyUI call).

## 1. What the file is, measured
`C:/Users/derek/5slock/ralph-community/PROMPT.md` = **5,645 B, 28 lines, ~920 words**, sha256 `fee26967…`. Blocks: `0a 0b 0c 0d 0e 1 2 3 4 99999 999999 9999999 99999999` - ids from three different eras of this loop.
Concentration: line 28 (GPU lock) = **939 chars**, lines 13-14 (my B2 1e/1f) = **1,015 chars** -> **two lines are 18% of the file**, and with line 28 that is **35%**.

The lineage of the same file: 334 B (Oct 17 `loop1017`) -> 2,349 B (Oct 22 `ali147`) -> 12,095 B (Oct 23 `archive/2026-10-23-prereset`) -> 5,645 B (today). It inflates, then a "prereset/overeng" archive prunes it. Inflation is the file's normal failure mode, and this box has already paid for two full rewrites.

## 2. The "weird shit", each item verified against disk
| # | Defect (measured) | Evidence |
|---|---|---|
| 1 | **Line 1 is false.** 0a says `fix_plan.md (pinned in ralph.ps1 argv)`. The live loop pins **only** PROMPT.md: `ralph.ps1:51` -> `pi --print ... "@$K\PROMPT.md"`. Nothing pins fix_plan, AGENTS.md, specs. | `ralph.ps1:51`; `prompt_md_clutter_probe.py` PATHS block |
| 2 | **Dead pointers.** "Script reuse: ... (`p15_writer_batch.py`, `bk26_judge_harness.py`, `p15_driver.ps1`, etc.)" - `notes\p15_writer_batch.py` **MISSING**, `notes\p15_driver.ps1` **MISSING**; only `bk26_judge_harness.py` exists (44,778 B). `notes\guard_requests.md` exists in **neither** repo. | probe "RELATIVE NAMES" block |
| 3 | **Two-repo path ambiguity.** Rule 1g "append one line to `notes\progress.md`" - that file exists in **both** roots (`ralph-community` 122,399 B **and** `C:\AI\community`). Rule 2 "if saved in `notes\web`, reuse it" + `git add notes\web` - that dir exists only in `C:\AI\community` (1,158 files), not in the loop cwd. Today I hit this myself and had to resolve it by reading. | probe table |
| 4 | **A contract the harness no longer has.** Rule 3 (`<promise>COMPLETE</promise>` exit token, "ONLY when fix_plan.md has 0 open items"). `ralph.ps1` is now a plain capped loop: it writes `iter/max/pi_rc/gpu_wait/gpu_busy` and nothing about tokens, open items, ticks, denies, checkfails. The records that made the token meaningful (`FALSE_COMPLETE` 2026-10-24 04:04, 10:01 `TOKEN_ECHO`, 2026-10-26 04:06 `TOKEN_ECHO open=59`, `summary: ... ticks=+1 open=16`) come from a **0.5-era harness that is gone**. So the prompt keeps the token rule, and the box lost the metrics that made prompt tuning possible. | `logs/ralph.log` (last `summary:` line 2026-10-23 19:06), `ralph.ps1:97,101` |
| 5 | **Rules other files still cite were deleted.** `notes/self_diagnosis.md` header = "append-only, **PROMPT.md SELF-DIAGNOSE**" and the skill `forge-self-diagnose` says "Use at the start of every pass" - PROMPT.md contains **no** SELF-DIAGNOSE rule (probe: False). The 36 KB self-diagnosis log and its skill are contract-drift debris. | probe DRIFT block |
| 6 | **Duplicated rules.** The 939-char GPU paragraph restates what the code already enforces (`run_graph_job.py` runs `gpu_guard.ps1`, takes/releases `gpu-render.lock`, runs `comm.guard_ok` before the POST, unloads `comfyui_auto`), and it also exists in `ralph-community/AGENTS.md` (29 lines: run_graph_job, gpu_guard, lock, comfy_ctl, subagents) and `skills/h3-hc-render/SKILL.md`. The adults gate appears in PROMPT + AGENTS + `community/RUNBOOK.md` (52 lines) + fix_plan; `test_p6_review.py` in PROMPT + AGENTS + fix_plan; "350-500 word" in PROMPT + RUNBOOK + fix_plan; "KEEP is Derrick" in PROMPT + skill. Measured rows in the probe's duplication matrix. | probe DUPLICATION MATRIX |
| 7 | **Provenance living inside an instruction.** My own 1e line is the current worst offender (748 chars): the operational content is ~110 chars ("copy <path>", "--frames 243"); the rest is the history of a decision that belongs in a note and in the file name (`default_b2_terrace_dom_q5guide_s51083007.api.json` already names the run). I wrote this today, so it is a live example of the mechanism, not an abstract criticism. | lines 13-14 |

Rule 4 of the file itself already demands the fix: *"keep them stock-simple, cite community source in commit message"*, and 9999999: *"Add nothing custom ... unless a real failure showed up and fix is a published community version with URL."* The file violates its own constitution: 3 of the 13 blocks are dead, 4 blocks duplicate other files, 1 line is factually wrong.

## 3. Community basis (published, with URLs)
- **The loop's own source - Geoffrey Huntley, "Ralph Wiggum as a software engineer", 2025-07-14, https://ghuntley.com/ralph/** : Ralph is `while :; do cat PROMPT.md | claude-code ; done`. What goes on the stack every loop is **the plan and the specs**: *"Your task is to implement missing stdlib (see @specs/stdlib/\*) ... Follow the @fix_plan.md and choose the most important thing."* - i.e. the prompt is a few sentences that **point at** pinned artifacts. *"One item per loop"*, *"the name of the game is that you only have approximately 170k of context window... The more you use the context window, the worse the outcomes you'll get"*, *"your primary context window should operate as a scheduler"* (subagents for expensive allocation), and tuning by **observed** bad behaviour: *"Each time Ralph does something bad, Ralph gets tuned - like a guitar"*, *"There is no such thing as the perfect prompt."* Notably the box quotes the "40-60% utilization / primary context window is a scheduler" line in 0d and then adds ~900 words of prompt.
- **Anthropic, "Effective context engineering for AI agents", 2025-09-29, https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents** : context rot and the attention budget; *"find the smallest possible set of high-signal tokens"*; system prompts at the **"right altitude"** - *"at one end we see brittle if-else hardcoded prompts, at the other prompts that are overly general"* (line 28 is exactly the brittle-hardcoded end); *"teams will often stuff a laundry list of edge cases into a prompt ... We do not recommend this"*; organise into delimited sections; **"just in time" retrieval** - keep *"lightweight identifiers (file paths, stored queries, web links)"* and load data with tools at runtime, which is what the skills system on this box already is.
- **This box already has the right mechanism**: `C:/AI/community/skills/{h3-hc-render,h3-prompting,forge-self-diagnose}/SKILL.md` are description-gated and loaded on demand. Reference material in PROMPT.md is the same content loaded unconditionally, every pass, in a repo that also has AGENTS.md, RUNBOOK.md and fix_plan.md carrying copies of it.

## 4. The rebuild rule I propose
**PROMPT.md = the loop protocol only.** Three tests for any line that stays:
1. **Is it enforced by code?** Then it must not be prose here - name the enforcing file. (`comm.guard_ok`, `run_graph_job.py`, the permission policy, the tests do the work.)
2. **Is it needed on every pass?** Then keep it, as one imperative line. (The MAX block, one item per pass, the default graph + frames, the record/commit shape, stop conditions.)
3. **Is it reference material, provenance, history, a scene ruling, a list of tools/models?** Then it moves out: skills, AGENTS.md/RUNBOOK.md, notes. Point at it with a path (Anthropic's "just in time"; Huntley's "@specs/@fix_plan.md").

Target: **<= 1.8 KB / ~18 lines**, 5 sections, no numeric magic ids, **absolute paths only**, one owner per fact.

## 5. Draft replacement (paste-ready, not applied)
```
# Forge loop protocol (ralph-community) - one item per pass. Read all of it.

## 1. Queue
Read C:\Users\derek\5slock\ralph-community\fix_plan.md first: the MAX block at the top is the queue, do the ONE open MAX item and nothing else. (Nothing pins fix_plan.md; you must read it.) Do not edit pi settings, packages, extensions, llama-swap/ComfyUI config, scripts\comm.py, ralph.ps1, PROMPT.md, pi-permissions.

## 2. Render item only (the stock path)
1. Pick a still with C:\AI\community\notes\hc_pick_scan_20261023.py (unless MAX names one); scene holds: C:\AI\community\notes\needs_derrick.md.
2. Caption once with your own model (one ask, one image), then write one 350-500 word H3 prompt; count the words, nothing else.
3. Gate: C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py (the same adults-only check runs inside run_graph_job.py; never loosen it).
4. Graph: copy C:\AI\community\p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json to <run_dir>\request.api.json; change ONLY LoadImage path, c0.prompt, noise_seed, filename_prefix. That file is the paid B2 setup (243 f, 768x1344, beta7 int8HQ, euler/simple 8 + pass 2 beta/3/0.4, shift 12/3, VSA keep 10, AddGuide frame 0, one reference); its history is C:\AI\community\notes\2026-10-29-item4-b2-default-DONE.md - do not restate it here.
5. Run: ...run_graph_job.py <run_dir> <id> --frames 243 (the number MUST equal c0.length in the graph you copied). One GPU job, gate first, never re-render a paid clip. Read C:\AI\community\skills\h3-hc-render\SKILL.md before building or judging any graph.

## 3. Hard rules (each line names the owner)
- Adults only, fictional, no minors: scripts\comm.py guard_ok + the tests above. No vision model judges, scores or picks rendered output; KEEP is Derrick's alone.
- GPU: queue only through run_graph_job.py (it runs gpu_guard, holds C:\AI\locks\gpu-render.lock, unloads after). No second job, no restart, no LLM request while a render runs.
- Secrets: never read/print .env*, keys, tokens, SSH, rclone, credential stores (permission policy enforces this; keep credential-shaped names out of shell command text).
- Change nothing custom (guards, caps, breakers, timers, hooks) without a real failure + a published community fix + URL.
- Facts live in code, skills, AGENTS.md, RUNBOOK.md - never restate a rule in a second place; if a rule needs changing, change its owner.

## 4. Records (one shape, absolute paths)
git commit once per repo you touched (message: what/why/evidence). Append one line to C:\AI\community\notes\progress.md, and to C:\Users\derek\5slock\ralph-community\notes\progress.md only if that repo changed. Append what you learned to the file that owns it (skills/AGENTS.md), not to the prompt. On a guard deny, a scope hit, an objective fail or a stalled render: write one line to C:\AI\community\notes\needs_derrick.md starting "[!] Max:" and stop.

## 5. Stop
Stop after the one MAX item. No completion token, no summary of work you did not do, no second task "while you were in there".
```
Dropped: 0b/0c/0d/0e (context discipline: AGENTS.md + the skills already own it), rule 2 (web-save plumbing is `scripts/check_web_saves.py` + AGENTS.md), rule 3 (the exit token - nothing in the current harness reads it, and it has a documented failure history), the "Script reuse" line (2 of 3 files gone), the 939-char GPU paragraph (the runner enforces it), the GI063 ruling and the vision-model inventory (scene registry / notes), the numeric ids.
Kept because it is the highest-signal content on the box: the default graph path, `--frames 243` == `c0.length`, the two tests, the one-item-per-pass rule, KEEP is Derrick.

## 6. What moves where (single owner per fact)
| Content in today's PROMPT.md | New owner | Mechanism |
|---|---|---|
| GPU-lock paragraph | `scripts/run_graph_job.py` (code) + `skills/h3-hc-render` | one line: "queue only through run_graph_job.py" |
| adults-only wording | `scripts/comm.py` + the two tests (code) | one line naming the tests |
| research/web rules | `scripts/check_web_saves.py`, AGENTS.md | one line: "saves go through check_web_saves.py" |
| GI063 hold ruling, "vision models exist" list, model names | `notes/needs_derrick.md` scene section + the render skill | path pointer |
| prompt provenance (B2 decision text) | this note + `notes/2026-10-29-item4-b2-default-DONE.md` + the graph filename | path pointer |
| self-diagnosis ritual | `skills/forge-self-diagnose` (already description-gated) | skill, not prompt; and its header must stop citing a PROMPT.md rule that no longer exists |
| completion token / exit gate | nothing (the plain loop stops at `-Max`); if you want an early exit, put it back in `ralph.ps1` where it can be enforced | code |

## 7. How to prove the new file is better (no GPU, cheap)
1. **Fix the measurement first.** `ralph.ps1` currently logs `iter/pi_rc/gpu_*` only; the 0.5-era line (`ticks=±N denies=N checkfails=N scope=N open=N`) is what made tuning possible. Re-add those five fields (ticks = `- [ ]` -> `- [x]` delta of fix_plan.md, denies = count of `notes/denies.log` lines newer than the pass start, open = `- [ ]` count outside Optional). Without it, any prompt change is a feeling.
2. **Baseline, then A/B.** Pin the prompt's sha256 in the note. Run 3 CPU-only passes with the old file, 3 with the new, on comparable MAX items. Compare: pass wall time, ticks/pass, denies, scope hits, and bytes of prompt allocated. Expect: fewer words in, same ticks, fewer denials (the "credential-shaped name in command text" class drops once the prose stops seeding it).
3. **An anti-clutter ratchet** (the durable part, and the fix for "carries weird shit" recurring): a ~60-line check script, run at the end of any pass that touches a rule file, that fails on (a) any path named in PROMPT.md/AGENTS.md that does not exist, (b) any file citing a rule id that PROMPT.md no longer contains, (c) any rule string appearing in 2+ of {PROMPT.md, AGENTS.md, RUNBOOK.md, skills}, (d) prompt size over a cap (e.g. 2 KB). That is a "sign next to the slide" in Huntley's sense, expressed as a check with a self-test, not a paragraph - the same non-vacuity standard this box already applies to its other gates.
4. Rollback: `PROMPT.md.bak-*` + git; the old file is never deleted, matching the box's archive-not-delete habit.

## 8. Open questions for Derek/Max (I did not act on these)
- Is the plain capped `ralph.ps1` intended (no scope check, no check tier, no token gate, no metrics)? Two of the 13 prompt rules only make sense in the old harness; if the plain loop is deliberate, drop those rules (this proposal does). If not, restore the harness features and keep the rules.
- Which progress.md is canonical for the loop, and should `notes/` live in `ralph-community` at all (both roots have progress.md + self_diagnosis.md today)?
- `notes/guard_requests.md` is referenced by history and exists nowhere; revive it or delete every reference to it.
