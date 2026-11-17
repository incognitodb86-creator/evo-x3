# Forge unattended runs: teaching-loop improvements and running without Sydney Clone
Date: 2026-10-10 (CT). ce-brainstorm phase 1, research only. No code changed. AlienPc not touched (GPU teaching round until 6:05 PM CT).

## Context (as given)
Forge = Pi coding agent on local Huihui Qwen3.8-27B abliterated IQ3_XXS-mtp (llama.cpp, 64K ctx, q8_0 KV, `--reasoning-budget 6000 -n 12288`), 16 GB Windows GPU, detached nightly job, 60-min cap. Medium bench: 4/6 (Gemini Flash also 4/6), far fewer tokens, but 4 step-ins (Flash 0), 2 token-limit hits, M1 fixed a symptom instead of the root cause, M2 deleted out of scope. SA-1 lets Sydney Clone approve only `node --test test/`. Lessons become rules only after Sydney Clone approves them.

## (a) Replacing human step-ins safely
- **Pi gives you the gate for free.** `tool_call` handlers can return `{block:true, reason}`, and the model sees the reason and keeps going (deny-and-continue). Tools carry `readOnlyHint` and `destructiveHint` annotations that a policy can key on. [Pi extensions](https://pi.dev/docs/latest/extensions), [permission-gate walkthrough](https://andrewgilliland.dev/articles/how-to-build-a-permission-gate-extension-with-pi/)
- **Config-driven allowlists already exist:** `pi-permission-gate` blocks by default, matches globs on commands and paths, lets deny rules win, keeps its own policy files from being edited, and logs every decision to `.pi/logs/permission-gate_*.jsonl`. That log is already a morning approval queue. [pi-permission-gate](https://pi.dev/packages/pi-permission-gate). `@thurstonsand/pi-permissions` adds allow, request and block modules per scope. [pi-permissions](https://github.com/thurstonsand/pi-permissions/)
- **Headless pitfall:** in print or JSON mode `ctx.hasUI` is false and `ctx.ui.confirm()` returns false without asking, so any confirm becomes a silent deny. In RPC mode the confirm goes to whatever client is attached. [Pi extensions.md](https://github.com/earendil-works/pi/blob/13437ca828894f43f973c630d208b488637d8fa9/packages/coding-agent/docs/extensions.md), [RPC extension UI](https://pi.dev/docs/latest/rpc-extension-ui)
- **What other tools do:**
  - Claude Code `-p` uses `--allowedTools` or `--permission-mode dontAsk`, which denies anything not allowlisted. PreToolUse can return `defer`, which ends the turn with `tool_deferred` so the call can be resumed later. That is effectively a native approval queue. Open issues report that hooks and allowlists are not enforced in `-p` mode, so people back them up with git hooks and OS-level controls. [headless](https://code.claude.com/docs/en/headless), [SDK hooks](https://code.claude.com/docs/en/agent-sdk/hooks), [#33343](https://github.com/anthropics/claude-code/issues/33343), [#30143](https://github.com/anthropics/claude-code/issues/30143)
  - OpenHands headless always auto-approves. Its SDK pairs a risk analyzer with `ConfirmRisky`, confirming only HIGH or UNKNOWN actions, and recommends Docker isolation. [headless](https://docs.openhands.dev/openhands/usage/cli/headless), [security](https://docs.openhands.dev/sdk/guides/security)
- **Isolation is how the community makes broad auto-approve safe.** Ralph-loop skills refuse to start outside a container with no network, a non-root user and no secrets. Chief-wiggum runs each iteration in a git worktree so a candidate patch is reviewed before it touches main. [jkitchin ralph skill](https://github.com/jkitchin/skillz/blob/main/skills/development/ralph-wiggum/SKILL.md), [chief-wiggum-loop](https://github.com/dr-gareth-roberts/chief-wiggum-loop)
- **Consensus:** prefer deny-and-continue (the agent hears why and routes around it) plus a queue of denied actions for the morning. Halt only when the denied action was on the critical path; detect that as the same denial repeated N times.
- **Fit for M2 (out-of-scope deletes):** add a path scope (task-declared file globs), and turn deletes outside scope into a hard deny. With a worktree, a bad delete costs nothing anyway.

## (b) Self-recovery when stuck
- **Stall detection.** OpenHands' stuck detector flags 4 identical action/observation pairs, 3 identical action/error pairs, 3 monologue messages in a row, 6 ping-pong cycles, and repeated context errors. [stuck detector](https://docs.openhands.dev/sdk/guides/agent-stuck-detector). open-ralph-wiggum flags 3 iterations with no file changes, 3 very short iterations, or the same error twice. [ralph.ts](https://github.com/Th0rgal/opencode-ralph-wiggum/blob/master/ralph.ts). Chief-wiggum classifies the cause (no progress, repeated verifier failure, timeout, refusal), pauses, and supports `/wiggum-resume`.
- **Qwen-specific (r/LocalLLaMA):**
  - The common Qwen 3.8 27B failure is looping or overthinking "until it hits the maximum it can output." Suggested fixes: a repeat detector on the last N tool calls, a hard turn cap, and correct samplers (thinking around temp 0.6 / top_p 0.95; no-think around 0.7 / 0.8 with presence_penalty near 1). One commenter reports reasoning effort low ≈ medium on pass@1 at about half the reasoning tokens. [thread](https://www.reddit.com/r/LocalLLaMA/comments/1vxhdz6/qwen_38_27b_thinks_too_much_soturn_it_off/), related: [1vq5to0](https://www.reddit.com/r/LocalLLaMA/comments/1vq5to0/qwen_3827b_unusable_long_thinking/), [Pi + local Qwen](https://www.reddit.com/r/LocalLLaMA/comments/1stjwg5/been_using_pi_coding_agent_with_local_qwen36_35b/) (the last two were only seen as search results; Reddit blocked the full fetch)
  - An overnight 27B write-up says: memory lives in files, not context (a status file rewritten after every step is how the next run resumes); work in small verified slices; when tests go red, stop looping and write the problem down. [mirror of r/LocalLLaMA post](https://prismix.dev/news/c58df799fb2e)
- **Token limits.** Pi auto-compacts when context > window − `reserveTokens` (16384 by default, so about 48K on a 64K window), keeping about 20K of recent tokens. A context overflow or an early `stopReason: "length"` triggers one compact-and-retry. `session_before_compact` lets an extension write its own summary or call a different model. [Pi compaction](https://pi.dev/docs/latest/compaction).
  - Forge's 2 token-limit hits are probably the `-n 12288` output cap: a 6000 reasoning budget plus a large edit or loop output can exceed it. Check whether the hits were output length or context overflow. They need different fixes: a smaller per-edit scope or reasoning effort for the first, compaction tuning or task splitting for the second.
- **Give up cleanly.** SWE-agent autosubmits the current diff on cost or context exhaustion (`submitted (exit_cost)`, `exit_context`) instead of throwing the work away, and does not retry on those errors. [SWE-agent agents.py](https://github.com/SWE-agent/SWE-agent/blob/main/sweagent/agent/agents.py), [lifecycle](https://deepwiki.com/scaleapi/SWE-agent/2.1.2-agent-execution-lifecycle)
- **Fresh context beats a long session.** Ralph's isolated runner starts a fresh process for each iteration and carries only bounded file and ledger memory forward. [chief-wiggum](https://github.com/dr-gareth-roberts/chief-wiggum-loop)
- **Escalating to a stronger model.** Aider's architect/editor split (strong planner, cheap editor with bounded context) is the standard pattern. [Aider context write-up](https://startdebugging.net/2026/05/fix-context-window-exceeded-during-an-aider-refactor/). For Forge, a cloud model (Flash) could take over only after the stuck detector fires, at most once per task, with a cost cap. That keeps token use low while recovering the stalls.
- **Suggested ladder:** stuck signal → inject a "state the root cause and what you tried" nudge → restart with fresh context from the status file and worktree checkpoint → one escalation to the fallback model → park the task (diff, log, reason) for the morning.

## (c) Keeping the teaching loop honest without a reviewer
- The Darwin Gödel Machine keeps an archive of variants, uses staged evals, and rejects variants that lose core ability. It reports transfer to a held-out benchmark. The paper also documents the agent gaming its own evaluation signal, which is exactly why the evaluator must be protected. [DGM paper](https://arxiv.org/abs/2505.22954v3), [code](https://github.com/jennyzzt/dgm). dgm-runner adds a holdout set, protected evaluator files, and rollback when the score drops. [dgm-runner](https://github.com/Crows12138/dgm-runner)
- **Apply to Forge:**
  1. Split the bench into train tasks (lessons may be mined from these) and held-out tasks (never shown and never mined).
  2. A candidate lesson is A/B tested on held-out tasks, comparing with and without the lesson over ≥2 seeds.
  3. Auto-reject a lesson on any held-out regression, a rise in token use or step-ins beyond a threshold, or a lesson that names a specific bench file or test (an overfit smell).
  4. Survivors go to `lessons/candidates/` with their evidence. Sydney Clone or Derrick promotes them in the morning. Nothing becomes a rule unattended, which keeps the current policy intact.
  5. Make the bench, tests and lesson store read-only to Forge (deny in the permission gate, like pi-permission-gate's self-protection).
- **M1 (symptom fix):** add a grader check that the root-cause test or held-out variant also passes, not just the reported failing test. Require the agent to write a one-line "root cause:" note that the grader compares against the task key.

## (d) Watchdogs, heartbeat, morning summary
- Wrap the Pi process in an outer supervisor, not an in-process one. On Windows, a Task Scheduler wrapper script should:
  - set a wall-clock cap (60 min) and an idle cap (no new JSONL event or file change in about 5 min → kill and park);
  - write a heartbeat file each minute and optionally ping a dead-man's switch (healthchecks.io style) so a silent hang gets noticed;
  - check llama-server `/health` before each task and restart it once if it is down.
- Pi's `--mode json` or `rpc` emits JSONL events that the stall detector and summary can parse. OpenHands `--json` and Claude `stream-json` work the same way.
- **Morning summary** (one markdown file, plus email or Slack once approved):
  - per-task pass/fail and exit reason (`done`, `parked:stuck`, `parked:denied`, `cap`, `token_limit`);
  - the denied-actions queue, with one-click approve-to-allowlist suggestions;
  - candidate lessons with held-out deltas;
  - tokens, wall time, and a link to the worktree diffs.
- Chief-wiggum's `--notify` and doctor preflight are good templates.

## What fails today if Sydney Clone is absent (inferred; check against the Forge runner)
1. **Blocked actions.** Anything other than `node --test test/` needs an approval nobody gives. If the gate uses `ctx.ui.confirm` in print/JSON mode, it auto-denies: the run continues but may thrash on the denied path. If it waits on an RPC or approval channel, it stalls until the 60-min cap kills it, and that night's work is lost. Either way the bench showed 4 such events per run, so expect about 1–2 tasks per night to degrade or stall.
2. **No stuck rescue.** Looping or overthinking runs on until the `-n` output cap or the 60-min cap. There is no restart or escalation.
3. **Token-limit hits.** Pi gets one compact-and-retry, then the task fails with no checkpoint or partial-diff salvage unless the runner saves it.
4. **Scope.** Nothing stops M2-style out-of-scope deletes unless the gate denies them. Without a worktree they land in the real tree.
5. **Teaching loop.** It safely freezes, because no lessons get promoted. But candidates pile up with no evidence attached, so the morning review is slow.

## Top 5 improvements (ranked by impact ÷ effort)
1. **Deny-and-continue policy gate with a morning queue** (high impact, low effort). Use pi-permission-gate or a small `tool_call` extension:
   - allowlist read-only tools, edits inside the task's path scope, and `node --test test/` (SA-1);
   - deny deletes outside scope, git push, network and installs, with a reason string the model sees;
   - log every denial to `queue/denied.jsonl`;
   - never wait on a confirm when `!ctx.hasUI`.
   This removes stalls and fixes M2.
2. **Per-task git worktree plus a wall-clock watchdog wrapper** (high impact, low-to-medium effort). Each task runs in its own worktree or branch with a 60-min total cap and a per-task cap of about 12 min. Idle detection on JSONL and heartbeat; the partial diff is always saved (SWE-agent autosubmit style). This makes broader auto-approve safe and means no night is wasted.
3. **Stall detector and recovery ladder** (high impact, medium effort). Use OpenHands thresholds (4× same action/observation, 3× same error, ping-pong) → nudge → fresh-context restart from the status file → park. Fix the samplers (temp 0.6 / top_p 0.95 for thinking) and test a lower reasoning effort or budget. Find out whether the token hits came from `-n` or the context window.
4. **Honest lesson pipeline** (medium-high impact, medium effort): train/held-out split, A/B each candidate on held-out tasks, auto-reject regressions and overfit lessons, bench files read-only, candidates queued with evidence for Sydney Clone or Derrick to approve. Add a root-cause check to the grader for M1.
5. **Morning summary plus a dead-man heartbeat** (medium impact, low effort). One report covering exit reasons, the denied queue, candidate lessons with deltas, and tokens. A missed heartbeat raises an alert.
- Optional 6th: **one-shot cloud fallback escalation** (Flash) on a stuck signal, capped per task. Recovers stalls but adds cost and a dependency.

## Decisions for Derrick
1. **How much to auto-approve unattended.** Options:
   - (a) SA-1 only plus deny-and-continue for everything else;
   - (b) SA-1 plus in-scope edits/creates plus read-only shell (`git diff/status`, `ls`, `node --test` on any path) inside a worktree;
   - (c) broad auto-approve inside a no-network sandbox.
   Recommended: (b). Does it need a new standing approval "SA-2"?
2. **Behavior on a critical-path denial:** park the task and move on (recommended), or halt the whole night's run.
3. **Lesson promotion and cloud fallback:** keep human or Sydney Clone approval for every rule (recommended), or allow auto-promotion of lessons that pass held-out A/B with zero regressions. And: may Forge escalate to Flash unattended, and at what nightly cost cap?

## Research notes
- Reddit: Apify rag-web-browser scraped 0 of 3 pages and old.reddit needs a login. One thread (1vxhdz6) was read fully through apify--web-fetch with rendering. The others were seen as search results or mirrors only.
- Unverified: whether Forge's current gate uses `ctx.ui.confirm` in print mode or an RPC or approval channel. This decides whether "absent Sydney" means a silent deny or a stall until the cap.

## Addendum 2026-10-10 ~6:00 PM CT: Reddit pass via Apify (for the teaching-loop plan review)
Method: Apify `apify--web-fetch` on `www.reddit.com/.../.json` with a custom User-Agent works; `old.reddit.com` .json returned a login wall; `apify--rag-web-browser` Google mode found titles but scraped 0 pages (HTTP 500). Many runs timed out at the MCP layer or hit the 5-concurrent-run cap; firing runs with `waitSecs: 0` and reading the dataset later worked. Reddit text is community opinion, not verified fact.
- **Steering lands late on Qwen 27B.** A user reports that with Qwen 3.8 27B in Pi, a steering message is read only after many rounds of "but wait" reasoning; another says most people run `reasoning_effort` xhigh without knowing, and medium fixes it. A third suggests a `--logit-bias` penalty on "wait" tokens. `pi-llama-skip-reasoning` uses llama.cpp's native skip-reasoning mechanism (PR 23971) to end a reasoning trace without breaking the KV cache. [thread 1wv1e60](https://www.reddit.com/r/LocalLLaMA/comments/1wv1e60/), [package](https://pi.dev/packages/pi-llama-skip-reasoning)
- **Pi is YOLO by default.** Users add a guard extension that asks before destructive actions; one reported Pi running `rm -f` without asking. Popular setups ship a "configurable permission system" extension. [1u4ow2h](https://www.reddit.com/r/LocalLLaMA/comments/1u4ow2h/), [abhinand5/pi-setup](https://github.com/abhinand5/pi-setup), [1sunkcq](https://www.reddit.com/r/LocalLLaMA/comments/1sunkcq/) (search result only)
- **Overnight loop burn (anecdote, low credibility; commenters call it a bot post).** An agent hit a flaky test and rewrote the test ~4,800 times overnight. Fix they adopted: hard budget per run, max retry count per tool call, stop and leave a draft when either trips. Commenters: per-run limits and "if an operation fails X times, stop" are basic. [ChatGPTCoding 1x1ks1u](https://www.reddit.com/r/ChatGPTCoding/comments/1x1ks1u/)
- **Silent permission stall.** Title-level only: "third night this week my coding agent stopped at 1am and waited for me" (halted on a permission prompt). [1wug2e6](https://www.reddit.com/r/ChatGPTCoding/comments/1wug2e6/) (body not loaded)
- **State on disk for long runs.** Title/summary only: moving "shift state" to disk so multi-hour agent runs stay reviewable. [1vyzagg](https://www.reddit.com/r/ChatGPTCoding/comments/1vyzagg/)
- **Idle-GPU autoresearch with Pi.** A user runs Pi's autoresearch extension on an idle local server overnight for benchmarking and perf tuning. [1wqhgva](https://www.reddit.com/r/LocalLLaMA/comments/1wqhgva/) (search snippet only); Karpathy autoresearch pattern (edit, 5-min experiment, keep if metric improves) [1rowp28](https://www.reddit.com/r/LocalLLaMA/comments/1rowp28/), [1ro00p2](https://www.reddit.com/r/LocalLLaMA/comments/1ro00p2/)
- **Single-GPU 27B memory cliff.** A 3090 Qwen 27B stack reports long tool outputs (~25K tokens) crashing until a patch fix, and a second memory cliff around 50-60K for single prompts on one GPU (vLLM). Relevant to a 64K window on 16 GB. [1t07su1](https://www.reddit.com/r/LocalLLaMA/comments/1t07su1/)
- **Harness matters.** Thread title: codex cli beat Pi and opencode for one user's local model. [1wrfp50](https://www.reddit.com/r/LocalLLaMA/comments/1wrfp50/) (search result only)
- r/ClaudeAI search for self-improving CLAUDE.md lessons returned mostly unrelated top posts; relevant titles: Karpathy's 4 CLAUDE.md clauses plus an added clause [1uc7izy](https://www.reddit.com/r/ClaudeAI/comments/1uc7izy/), "Why does this CLAUDE.md file have so many stars?" [1stfoo7](https://www.reddit.com/r/ClaudeAI/comments/1stfoo7/).
- **Unattended needs "decide, record, continue".** The popular Karpathy-style CLAUDE.md clause "Ask, don't assume" was amended by its poster to: "When running unattended, pick the most reasonable interpretation, proceed, and record the assumption rather than blocking." Clause 3, "Don't touch unrelated code", matches our F2 target. [ClaudeAI 1uc7izy](https://www.reddit.com/r/ClaudeAI/comments/1uc7izy/)
- Fetch failures this pass (to retry later): 1wug2e6, 1vyzagg, 1sunkcq, 1wqhgva, 1wrfp50 thread bodies; r/LocalLLaMA searches "qwen 27b stuck loop agent" and "AGENTS.md lessons memory" (empty datasets or MCP timeouts).
