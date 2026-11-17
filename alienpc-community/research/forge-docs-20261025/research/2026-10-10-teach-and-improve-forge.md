# Teaching and improving Forge (Pi 1.1.0 + Huihui-Qwen3.8-27B-abliterated IQ3_XXS-mtp)
_Research date: 2026-10-10 (CT). Done on the box only; nothing on AlienPc was touched._

**Baseline:** Forge Bench easy 7/7, medium 4/6.
- M1 fixed the symptom, not the root cause (datetime serialization never traced back to where values are written).
- M2 did a "cleanup" nobody asked for, removed imports that were still used, burned the 40K per-task budget, and never re-ran the tests.

**Failure modes:** (F1) no root-cause tracing, (F2) scope creep, (F3) no final test run, (F4) token waste.

**Main point:** the community's consensus for 27B-class local agents is to **enforce in the harness and keep the prompt short.** Small models follow a short checklist about as well as a long one, but they skip the steps they find inconvenient (running the final test, staying in scope) unless the harness blocks or nudges them. Pi was built for this: `tool_call` can block, and `agent_before_settle` and `turn_end` can inject a message and force one more model turn. One caveat about our own data: 6 medium tasks is too few. One task is about 17 points, so every change below needs 3 runs per task before we believe the delta.

---

## Ranked improvements

| # | Improvement | Targets | Effort | Expected gain | How to verify on Forge Bench |
|---|---|---|---|---|---|
| 1 | **Thinking/sampling fix:** `preserve_thinking:false`, `reasoning_effort:medium` for edit turns, official Qwen3.8 thinking sampling (see diff) | F4, partly F3 | 15 min (config) | Large token cut per task. Old reasoning traces stop piling up in a 64K window. Likely saves M2-type budget blowouts | tokens/task (median, p90), budget-exceeded count, pass@1 on the same 13 tasks x3 runs |
| 2 | **Test-before-done gate** (Pi extension) | F3 | ~1-2 h (Forge can build it) | Removes the "finished without testing" class entirely. Turns some fails into self-fixes | % of runs whose last tool call after an edit is a passing test (target 100%), medium pass@1 |
| 3 | **Scope guard + diff-size/import guard** (Pi extension) | F2 | ~2 h | Stops unrequested cleanups and import deletions (M2) | count of out-of-scope edits/blocks per run, `git diff --numstat` lines vs reference patch, M2 pass |
| 4 | **AGENTS.md rule block** (below; about 900 tokens) | F1-F4 | 10 min | Moderate. Rules alone are weak at 27B, but they give the gates the vocabulary they cite back to the model | A/B: bench with and without the block, 3 runs each |
| 5 | **Root-cause skill + reproduce-first workflow** (Agentless-style localize, reproduce, fix, verify) | F1 | ~1 h (SKILL.md + 1 bench task) | M1-class fixes land where the bad value is written | add 2 "symptom far from cause" tasks. Pass needs a test at the write site, not just the read site |
| 6 | **Token watchdog + loop detector** (Pi extension) | F4 | ~1-2 h | Wraps up the run gracefully before the budget dies. Catches repeated tool calls | budget-exceeded count goes to 0. Runs that hit the 75% nudge still finish with a passing test |
| 7 | **Bench hygiene:** 3 runs per task, expand medium to 12+ tasks, log tokens/turns/tests | measurement | ~2 h | No direct gain, but it stops us chasing noise | stable pass@1 ± spread |
| 8 | **Bounded lessons file** (≤15 one-line lessons, each tied to a bench failure) | F1-F4 over time | ongoing | Small, steady gains | each lesson must flip at least one failing task without regressing others, or it gets deleted |
| 9 | **Better quant** (IQ3_S / IQ3_M / UD-Q3_K_XL if it fits 16 GB with 64K q8 KV) | all | download + 1 bench run | Unknown, plausibly +1 medium task. Community reports more loops and tool-call failures at low bits | same bench x3, plus tok/s and VRAM headroom |
| 10 | **MTP tuning:** `--spec-draft-n-max 3` (community optimum), optionally `ngram-mod,draft-mtp` | speed only | 15 min | +0-20% tok/s. More turns fit in wall-clock time, quality unchanged | `draft_n_accepted/draft_n` in server responses, tok/s |
| 11 | **Fine-tune on own traces** (SFT, then DPO, QLoRA, rented GPU) | all | days + $ | Uncertain, can regress (see section 6). Do it last | held-out bench split only |

Do #1-#4 together as "v2", then #5-#6 as "v3". Measure each stage separately.

---

## 1. AGENTS.md / system-prompt guidance for Qwen-class local agents

What the community and the docs say:
- Keep it short and explicit: inspect before editing, make the smallest safe change, run the targeted tests, then report changed files, what was verified, and the risks. Spell out workspace boundaries and a **stop condition**. ([Qwen3.8-27B agentic coding guide](https://www.qwen3827b.wiki/coding/Qwen3-8-27B-agentic-coding))
- Pi users put durable rules in `AGENTS.md` / `APPEND_SYSTEM.md` and push behavior into extensions instead of growing the prompt. Pi's core prompt is deliberately minimal. ([r/LocalLLaMA: best local harness](https://www.reddit.com/r/LocalLLaMA/comments/1vukppf/whats_the_best_local_ai_harness_for_coding/), [pi.dev](https://pi.dev))
- What hurts at 27B: long rule lists that pull against each other, vague goals ("make it clean"), and anything that invites exploration. What helps: numbered procedures, concrete commands, an explicit "do not" list, and a fixed final-report format.
- Telling the model about its own budget and stop condition reduces looping. ([Qwen3.6-27B looping thread](https://www.reddit.com/r/LocalLLaMA/comments/1uue278/working_around_qwen3627bs_toolcall_failures_and/))

### Exact AGENTS.md block for Forge (about 900 tokens)

```markdown
# Forge rules (follow in order; the harness enforces 3, 4, 6)

## 1. Understand before editing
- Restate the task in one line. List the files you expect to change.
- Read the failing test or error and the code it touches. Do not explore unrelated files.

## 2. Find the root cause (bugs)
- Reproduce first: run the failing test or a one-line repro and note the actual output.
- Trace the bad value BACKWARD: where is it read -> where is it computed -> where is it WRITTEN or serialized? Fix it at the earliest point where it goes wrong, not where it is displayed.
- Before editing, write one line: `ROOT CAUSE: <file:function> because <reason>`.
- If the same bug pattern exists at other write sites in the task's files, fix those too, and list them.

## 3. Stay in scope
- Change only what the task requires. No refactors, renames, reformatting, comment rewrites, or "cleanup" unless asked.
- Never delete imports, functions, or variables unless your change made them unused AND `rg` shows no remaining uses.
- If you notice an unrelated problem, mention it in the final report; do not fix it.
- Prefer small `edit` calls (exact oldText/newText). Use `write` only for new files. Re-read the lines around an edit if it fails (watch CRLF/whitespace).

## 4. Verify before you finish
- After your LAST edit, run the task's test command and paste the pass/fail summary line.
- If tests fail, fix and re-run. You may not finish with failing or unrun tests unless you report exactly why.
- If no test exists for the bug, add a minimal one at the root-cause site.

## 5. Self-review (one pass, brief)
- Run `git diff --stat` and `git diff`. For each hunk ask: required by the task? If not, revert it.
- Confirm that no used import or symbol was removed.

## 6. Budget
- Budget is about 40K tokens per task. Keep thinking short on routine steps; think harder only for root-cause analysis.
- Do not re-read files you already read unless they changed. Use `rg -n` and read only line ranges you need.
- Use `head`/`tail` or `-q` flags on noisy commands.
- At a harness budget warning: stop exploring, finish the minimal fix, run tests, report.

## Final report (exactly this, max 8 lines)
ROOT CAUSE: ...
CHANGED: file:lines - why (one line each)
TESTS: <command> -> <N passed / M failed>
NOT DONE / RISKS: ...
```

---

## 2. Harness-level enforcement: Pi extension specs (small units Forge can build)

Pi API facts used here, from the [extensions doc](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/extensions.md) and [types.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/extensions/types.ts):
- `pi.on("tool_call", ...)` can **block** a call with `{ block: true, reason }`. It can also mutate the input.
- `tool_result` can rewrite content or `isError`.
- `turn_end` and `agent_before_settle` return `{ entries: [{type:"custom_message", customType, content, display}], continue: true }`, which forces **one** more model request. Guard these against loops.
- `ctx.getContextUsage()` returns context usage. Token stats come from `ctx.sessionManager.getEntries()`.
- `ctx.executeTool(name,args)` runs a built-in tool from inside an extension.
- `pi.appendEntry()` stores state outside the model context.
- The built-in edit tool is **search-replace** (`edits[]: {oldText,newText}`, each match must be unique).
- Relevant existing examples to copy from: `protected-paths.ts`, `permission-gate.ts`, `dirty-repo-guard.ts`, `git-checkpoint.ts`, `plan-mode/`, `todo.ts` ([examples dir](https://github.com/earendil-works/pi/tree/main/packages/coding-agent/examples/extensions)).
- Known cosmetic issue: a blocked tool briefly renders as "running" ([issue #2543](https://github.com/badlogic/pi-mono/issues/2543)).

Shared config is `.forge/task.json`, written by the bench runner per task:
```json
{ "testCmd": "pytest -q tests/test_x.py", "scope": ["src/app/serialize.py", "tests/**"], "tokenBudget": 40000, "maxDiffLines": 120 }
```
If the file is missing, fall back to the env vars `FORGE_TEST_CMD`, `FORGE_SCOPE`, `FORGE_BUDGET`.

### Ext A: `forge-test-gate.ts` (fixes F3)
- **State:** `editsSinceGreen` (bool), `nudges` (int), `lastTest` ({cmd, exitCode, summary}).
- **tool_result** for `edit`/`write` with no error: set `editsSinceGreen = true`.
- **tool_result** for `bash` whose command matches `testCmd`, or the regex `/(pytest|npm test|go test|cargo test|vitest|jest)/`: parse the exit code and summary line. On exit 0, set `editsSinceGreen = false`.
- **agent_before_settle:** if `editsSinceGreen && nudges < 2`, then `nudges++` and return `{entries:[{type:"custom_message",customType:"forge-gate",display:true,content:"GATE: you edited files after the last passing test. Run `<testCmd>` now, fix any failure, then give the final report."}], continue:true}`.
  - Option B (stronger): run `ctx.executeTool("bash",{command:testCmd})` itself and inject the tail of the output (at most 40 lines).
- If tests are still red after 2 nudges, let it settle and log `forge_gate: FAILED_RED` through `pi.appendEntry` so the bench can score it.
- **Unit tests:** (1) edit then settle → one nudge. (2) edit, passing test, settle → no nudge. (3) failing tests stay red → at most 2 nudges, then the run settles.

### Ext B: `forge-scope-guard.ts` (fixes F2)
- **tool_call** on `edit`/`write`: resolve the path relative to cwd. If it is outside `scope` globs, block with `{block:true, reason:"SCOPE: <path> is not in task scope <list>. If truly required, explain why in one line and edit only the minimal lines."}`.
  - Allow one override: if the model's previous assistant text contains `SCOPE-EXCEPTION: <path>`, admit that path once.
- **Import/symbol deletion check** on `edit`: for each `edits[i]`, compute the lines present in `oldText` but missing from `newText`. If any matches `^\s*(import |from .* import |const .*= require\(|use |#include)` (or a `def`/`function`/`class` header), extract the names and run `rg -w <name>` across the repo, excluding the edited hunk. If uses remain, block with a reason listing `file:line` of the uses.
- **Diff-size guard:** after each successful edit, run `git diff --numstat`. If total changed lines exceed `maxDiffLines`, block the next edit with "DIFF: N lines changed (> limit). Revert unrelated hunks (`git diff` review) before continuing."
- **bash guard:** block `sed -i`, `perl -pi`, `> file`, `git checkout -- .`, and `rm` on tracked files outside scope. This stops the model from routing around the edit block.
- **Unit tests:** out-of-scope write blocked, in-scope allowed, removal of a used import blocked, removal of a truly unused import allowed, a 200-line diff triggers the guard.

### Ext C: `forge-token-watchdog.ts` (fixes F4, plus loops)
- **turn_end:** add up assistant `usage` (input+output) from the entries since the task's user message, and track `ctx.getContextUsage()`.
- At **50%** of `tokenBudget`: inject (display:true, no forced continue) "BUDGET 50%: N tokens used. Next: minimal fix → run tests → report."
- At **75%**: inject "BUDGET 75%: stop exploring. No new file reads except files you will edit. Run `<testCmd>` and finish." From then on, block `read` of files not already read and not in scope.
- At **90%**: allow only `edit` inside scope and `bash` running testCmd or `git diff`. Every other call is blocked with a reason pointing to the final report.
- **Loop detector:** hash `(toolName, JSON(input))`. If the same hash appears 3 times in the last 6 calls, block it with "LOOP: identical call repeated; change approach or finish." (SWE-Gym counts 3x repeats as "stuck in loop": [arXiv 2412.21139](https://arxiv.org/abs/2412.21139).)
- **Output trimming** in `tool_result` for bash: if the output is over 6K chars, keep the head (40 lines) and tail (80 lines) plus a note "[trimmed N lines]". This is the biggest cheap token saver on test logs.
- **Logging:** write per-turn tokens to `pi.appendEntry` for the bench report.

### Edit format
Keep Pi's built-in **search-replace `edit`**. Aider's benchmarks show search/replace "diff" formats beat whole-file for capable models and save many tokens; whole-file only wins for weak models on tiny files ([aider edit formats](https://aider.chat/docs/more/edit-formats.html)). SWE-agent found that **lint/validate-on-edit** with immediate error feedback matters more than the format itself ([SWE-agent ACI, arXiv 2405.15793](https://arxiv.org/abs/2405.15793)).

Optional add-on to Ext B: after a `.py` edit, run `python -m py_compile` (or `ruff check --select F401,F821`) and append the errors to the tool result. That would have caught M2's broken imports right away. Our CRLF miss: have Ext B normalize `\r\n` in `oldText` when the file is CRLF (mutate `event.input`).

---

## 3. Workflow patterns (evidence)
- **Localize → reproduce → repair → validate** (Agentless): a simple fixed pipeline competitive with complex agents, where the reproduction test gates acceptance ([arXiv 2407.01489](https://arxiv.org/abs/2407.01489)). This maps onto rule 2 plus Ext A.
- **Plan-then-act:** Pi users with Qwen 27-35B write PLAN.md, have the model review it, then implement phase by phase with git ([r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1vukppf/whats_the_best_local_ai_harness_for_coding/)). For bench-size tasks, use a one-line `ROOT CAUSE` plus a file list rather than a full plan, which costs tokens. Pi ships a `plan-mode/` example for larger tasks.
- **Self-review pass:** the `git diff` review in rule 5 is cheap (about 1-2K tokens) and directly targets F2.
- **Reflection on failure** (Reflexion, [arXiv 2303.11366](https://arxiv.org/abs/2303.11366)): use it between bench runs, not inside a run. Turn each failure into a one-line lesson (section 5). In-run reflection at 27B mostly burns tokens.
- **Auto-continue on early stop:** the community's Pi extension watches for loops or an early stop and injects a "continue" prompt when the goal isn't met ([thread](https://www.reddit.com/r/LocalLLaMA/comments/1uue278/working_around_qwen3627bs_toolcall_failures_and/)). Ext A/C cover this.

### `skills/root-cause/SKILL.md` (loaded on demand; only the name and description sit in the prompt: [Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md))
```markdown
---
name: root-cause
description: Use when fixing a bug, wrong value, serialization/format error, or failing test, to trace the fault back to where the value is produced or written.
---
1. Reproduce: run the failing test; copy the exact wrong vs expected value.
2. Find the read/display site (rg the field name). Then find every WRITE site: rg for assignments, constructors, serializers (to_dict/json/dump/isoformat/strftime), DB/ORM save, API response builders.
3. For each write site ask: does the bad value already exist here? Walk upstream until the first site where it's wrong.
4. Fix there. Add or extend a test that asserts the value at that write site.
5. rg the same pattern at the other write sites in scope; fix or list them.
6. Write `ROOT CAUSE: file:function because ...`, then continue with rule 4 (run tests).
```

---

## 4. Sampling and thinking: recommended llama-server changes

Source: the official [Qwen3.8-27B model card](https://huggingface.co/Qwen/Qwen3.8-27B).
- **Thinking mode:** temp 1.0, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, repetition_penalty 1.0.
- **Non-thinking mode:** temp 0.7, top_p 0.8, top_k 20, presence_penalty 1.5.
- **`reasoning_effort`:** xhigh (default) / medium / low.
- **`preserve_thinking`** is on by default and keeps earlier reasoning in context. Turning it off is the documented way to stop context growth.
- The card warns that lower effort can *increase* total tokens through retries, so measure it.
- For precise coding, Qwen3.5 and community MTP builds use temp 0.6 ([froggeric MTP GGUF](https://huggingface.co/froggeric/Qwen3.6-27B-MTP-GGUF), [Qwen3.5 card](https://huggingface.co/Qwen/Qwen3.5-0.8B)).
- Never use greedy decoding (loops).

Proposed diff (the exact current flags were not readable from the box, so this reconstructs them from the brief; please check against the real launch script):
```diff
 llama-server -m Huihui-Qwen3.8-27B-abliterated-IQ3_XXS-mtp.gguf \
   -ngl 99 -c 65536 -fa on -np 1 --jinja \
   --cache-type-k q8_0 --cache-type-v q8_0 \
-  --reasoning-budget 6000 -n 12288
+  --reasoning-budget 6000 -n 12288 \
+  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 \
+  --presence-penalty 0 --repeat-penalty 1.0 \
+  --chat-template-kwargs '{"preserve_thinking": false, "reasoning_effort": "medium"}' \
+  --spec-type draft-mtp --spec-draft-n-max 3
```
Notes:
- **A/B the temperature:** 0.6 (variant A) vs the official 1.0 (variant B), 3 runs each, then keep the winner. If you see loops at 0.6, raise presence_penalty to 0.3-0.5 before raising temperature.
- **`preserve_thinking:false`** is the single biggest F4 lever. With it on, every earlier turn's reasoning (up to 6K each) stays inside the 64K window. Verify the abliterated GGUF's embedded template still honors the kwarg: grep the template for `preserve_thinking`. If it doesn't, have the gateway strip `reasoning_content` from history.
- **`reasoning_effort` per phase:** the gateway or a Pi extension can set `medium` by default and `xhigh` only for the first turn (localization/root cause). Pi exposes thinking-level control to extensions (`pi` session control methods). The alternative is a tighter `--reasoning-budget` (for example 3000) on edit/test turns.
- **Pi `maxTokens`:** check that `maxTokens` in Pi's models.json is ≥ 12288, or streams get cut off ([Pi hanging thread](https://www.reddit.com/r/LocalLLaMA/comments/1vr9gy0/qwen_38_27b_hanging_in_pidev/)).
- **MTP:** n-max 3 is the reported sweet spot below F16, with about 75% acceptance at 3 drafts ([llama.cpp PR #22673](https://github.com/ggml-org/llama.cpp/pull/22673)). `ngram-mod,draft-mtp` can help with code that repeats context verbatim ([unsloth notes](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF/commit/ac393bc3d23fd5a929a85e2f33c7c4fd5be02d43)). Check `draft_n_accepted/draft_n`. MTP lowers prompt-processing speed slightly.

---

## 5. Few-shot, skills, and memory without bloat
- Use **skills** (progressive disclosure) for procedures: root-cause, add-regression-test, safe-import-removal. Only the descriptions sit in context. Note that the model may fail to load a skill, so the bench prompt can force it with `/skill:root-cause` for bug tasks ([Pi skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)).
- **Lessons file:** `.forge/LESSONS.md`, at most 15 lines and at most 400 tokens. Each line is `trigger → action (source: bench task, date)`. It's included from AGENTS.md. Lessons that don't move the bench get pruned. Every lesson must be backed by a failing case (no speculative rules).
- **Few-shot:** one compressed "golden trace" (about 300 tokens: repro → ROOT CAUSE line → 1 edit → test pass → report) works better at 27B than several long examples. Put it in the root-cause skill, not in AGENTS.md.
- For larger memory, Pi's `context` / `before_agent_start` hooks can inject only the lessons whose trigger matches the task text (keyword match is enough).

---

## 6. Model-level options
- **Quant:** IQ3_XXS is aggressive for a 27B dense agent. Community reports tie low-bit quants to more loops and tool-call errors, and people reported fewer problems at Q4-Q5 ([thread](https://www.reddit.com/r/LocalLLaMA/comments/1uue278/working_around_qwen3627bs_toolcall_failures_and/)). On 16 GB with 64K q8 KV, test the next steps up, IQ3_S / IQ3_M (or UD-Q3_K_XL if an MTP build exists for the abliterated variant). Check VRAM headroom first. If 64K doesn't fit, try 48K and compare, since a bigger quant at 48K may beat IQ3_XXS at 64K. The non-abliterated official Qwen3.8 at the same quant is also worth one bench run as a control: abliteration can cost a little capability.
- **MTP:** see section 4. No separate draft model is needed.
- **Fine-tuning on our own traces:**
  - **Data:** Pi session JSONL ([session format](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/session-format.md)) → ChatML with tool calls in the model's native template. Keep only runs that pass the bench and Ext A's final test, have no scope blocks, and stay under budget. Keep reasoning on, but trimmed. Store failing runs too, to build DPO pairs (same task: passing trace = chosen, failing trace = rejected).
  - **Size:** the literature used about 500 successful trajectories, roughly 19 turns and 19K tokens each, for large gains on weak bases ([SWE-Gym](https://arxiv.org/abs/2412.21139)), and 5K for SOTA on 32B ([SWE-smith](https://swesmith.com/guides/train_swe_agent/)). Realistic for us is 200-500 traces, which needs a much bigger task pool. Synthesize tasks SWE-smith-style by injecting bugs into our own repos.
  - **Risk 1, self-training can hurt:** in SWE-Gym, on-policy self-training with OpenHands dropped a 32B from 15.3% to 8.7%. Rejection-sampling SFT in a fixed workflow gave only +0.7-3 points and plateaued after 2 rounds. Teacher traces (a frontier model driving Pi on the same tasks) are the stronger data source.
  - **Risk 2, MTP heads:** QLoRA changes the hidden states the MTP head was trained on, so draft acceptance may drop (speed, not quality). The MTP tensors must survive merge and GGUF conversion (mainline `convert_hf_to_gguf.py` b9180+ keeps them).
  - **Risk 3, abliteration:** coding-only SFT rarely restores refusals, but LoRA on top of an abliterated model can partly undo the orthogonalization. Run a refusal smoke test after.
  - **Risk 4, quantization:** fine-tune bf16 weights, then re-quantize to IQ3 with a fresh imatrix. IQ3 noise can erase small SFT gains.
  - **Rented GPU:** QLoRA on a 27B dense model at 32K seq needs about 48-80 GB (1x A100/H100 80GB, a few hours for about 500 traces).

---

## 7. What the community measures
- **pass@1 / resolve rate**, averaged over k runs. Qwen reports avg@3 for its own SWE benchmark ([model card](https://huggingface.co/Qwen/Qwen3.8-27B)).
- **Stuck-in-loop % and empty-patch %** ([SWE-Gym](https://arxiv.org/abs/2412.21139)).
- **Tokens/task and wall-clock/task.** Locally, cost = time.
- **Harnesses:** SWE-bench Lite/Verified via `sb-cli`, the SWE-smith task generators, Terminal-Bench, and Aider polyglot (edit-format compliance).
- **Forge Bench should log per run:** pass, tokens, turns, wall time, final-test-ran, scope blocks, diff lines vs reference, loops, gate nudges, MTP acceptance.

---

## Staged teaching loop
1. **Baseline (v1):** run easy+medium x3 with the current config. Record the metrics above in `bench/results/<date>-v1.jsonl`.
2. **Analyze:** for each failure, tag it F1-F4 (or a new tag) and write a one-line cause. Pick a fix type by rule: a behavior the model *skips* → extension; a behavior it doesn't *know* → skill or lesson; a behavior it does inconsistently → sampling/thinking.
3. **Change exactly one layer per stage:** v2 = settings (#1) + AGENTS.md (#4). v3 = Ext A + B. v4 = Ext C + root-cause skill. v5 = quant test.
4. **Re-run x3 and track the delta:** `results/summary.md` gets one row per version (pass@1 mean±spread, tokens median/p90, gate/scope counts). Revert anything that doesn't help.
5. **Grow the bench:** add 2 tasks per new failure class (held-out copies kept aside for fine-tune eval).
6. **Fine-tune data collection, on from v2:** save every session JSONL plus task id, pass/fail, and metrics. Once there are ≥200 clean passes on a ≥50-task pool (plus optional teacher traces), run SFT, then DPO on the held-out split. Gate the rollout on: no drop in pass@1, MTP acceptance within 10%, refusal smoke test clean.
