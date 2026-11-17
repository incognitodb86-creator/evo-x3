# Forge community-standards research (box only), 2026-10-23 ~11:15 AM CT

Scope: the community norms Forge (pi + Ralph + llama-swap/llama.cpp on AlienPc) gets measured against. Every claim cites the URL I fetched today.

## 1. Ralph loop: ghuntley's original and the well-known forks

**Original (ghuntley), https://ghuntley.com/ralph/**
- "In its purest form, Ralph is a Bash loop": `while :; do cat PROMPT.md | claude-code ; done`. "Ralph can be done with any tool that does not cap tool calls and usage."
- **One item per loop**, repeated for emphasis. "You may relax this restriction as the project progresses, but if it starts going off the rails, then you need to narrow it down to just one item."
- The context is allocated the same way every loop: PROMPT.md, then specs/*, then `@fix_plan.md`. The prompt says "Follow the fix_plan.md and choose the most important thing."
- **Don't assume it's not implemented**: search the codebase before changing it.
- **Backpressure** comes from build, tests, type checks and static analysers: "After implementing functionality or resolving problems, run the tests for that unit of code that was improved." The wheel "has got to turn fast."
- **Commit per loop**: "When the tests pass update the @fix_plan.md, then add changed code ... git add -A ... git commit ... git push", and git-tag when green. Recovery is "git reset --hard and kick Ralph back off again".
- **AGENT.md is "the heart of the loop"**. It covers how to build and run, and Ralph updates it with learnings, "but keep it brief". "DO NOT PLACE STATUS REPORT UPDATES INTO @AGENT.md."
- fix_plan.md is disposable: "I have deleted the TODO list multiple times", and you regenerate it with a planning loop. Clean out completed items periodically.
- Tuning: add "signs" (prompt guardrails) when Ralph fails. "Ralph will test you."

**Ralph Playbook (ghuntley/how-to-ralph-wiggum, Clayton Farr), https://github.com/ghuntley/how-to-ralph-wiggum**
- Three phases, two prompts, one loop: `PROMPT_plan.md` does gap analysis, writes `IMPLEMENTATION_PLAN.md`, and commits nothing. `PROMPT_build.md` picks one task, implements it, validates, updates the plan and AGENTS.md, then commits.
- Context loaded each iteration is `PROMPT.md` + `AGENTS.md`. The "smart zone" is 40-60% context utilisation, so tight tasks and one task per loop.
- AGENTS.md is "NOT a changelog or progress diary ... Keep brief (~60 lines). Status, progress, and planning belong in IMPLEMENTATION_PLAN.md."
- Backpressure: "Prompt says 'run tests' generically. AGENTS.md specifies actual commands." LLM-as-judge is an acceptable binary pass/fail gate for subjective output (relevant to video ops).
- **Permissions**: "To operate autonomously, Ralph requires `--dangerously-skip-permissions` — asking for approval on every tool call would break the loop ... a sandbox becomes your only security boundary." Run "in isolated environments with minimum viable access ... Restrict network connectivity where possible." Escape hatches are Ctrl+C, `git reset --hard`, and regenerating the plan.
- The enhanced `loop.sh` takes max iterations and runs `git push` after each iteration. Each iteration is one fresh context, one task, one commit.

**snarktank/ralph (Amp/Claude fork), https://github.com/snarktank/ralph**
- Memory persists via **git history, progress.txt (append-only learnings), and prd.json** (stories with `passes`).
- The loop implements one story, runs checks, **commits if checks pass**, marks it passed, appends learnings, and repeats until done or `max_iterations`. It exits on `<promise>COMPLETE</promise>`.
- "AGENTS.md Updates Are Critical": add reusable patterns and gotchas, not status.

**frankbria/ralph-claude-code, https://github.com/frankbria/ralph-claude-code**
- Files: `.ralph/PROMPT.md`, `.ralph/fix_plan.md` (prioritised `- [ ]` tasks), `.ralph/AGENT.md` (build and test commands), `.ralph/specs/`.
- Defaults in `.ralphrc`: `CLAUDE_TIMEOUT_MINUTES=15`, `ALLOWED_TOOLS="Write,Read,Edit,Bash(git *),Bash(npm *),Bash(pytest)"`. **git is allowed by default.**
- Circuit breaker: `CB_NO_PROGRESS_THRESHOLD=3` (3 loops with no file changes), `CB_SAME_ERROR_THRESHOLD=5`, `CB_COOLDOWN_MINUTES=30` (OPEN goes to HALF_OPEN automatically). Git commits count as progress. Also a rate limit of 100 calls per hour and dual-condition exit (completion indicators plus `EXIT_SIGNAL: true`).

**What the community agrees on:** one PROMPT, one plan file (fix_plan / IMPLEMENTATION_PLAN / prd.json) chosen from by priority, one task per loop, tests and build as backpressure, **a commit per green loop** (git is the memory and the undo), and a short operational AGENTS.md. The breaker trips on no progress or repeated errors, with a cooldown, not on wall-clock alone.

## 2. pi coding agent: recommended configuration and permissions
- Settings live in `~/.pi/agent/settings.json` (global) and `.pi/settings.json` (project, overrides global). Models live in `~/.pi/agent/models.json`. https://pi.dev/docs/latest/configuration
- AGENTS.md / CLAUDE.md are loaded from `~/.pi/agent/`, parent directories and cwd, and concatenated. `APPEND_SYSTEM.md` adds to the system prompt and `SYSTEM.md` replaces it. https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent
- **Permissions model: YOLO by default.** "pi runs in full YOLO mode ... No permission prompts for file operations or commands ... security measures in other coding agents ... are mostly security theater ... If you're uncomfortable with full access, run pi inside a container." "By default, pi has no web search or fetch tool. However, it can use curl." https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- Official security doc: "Safety comes from limiting the files, credentials, processes, and network services Pi can access ... Watching the transcript, using project trust, and reviewing changes do not create a security boundary." It recommends a container, VM or sandbox ("usually the strongest practical option"), scoped short-lived credentials, restricted network when not needed, and "snapshots, backups, or **version control** before substantial changes." For headless (print/JSON/RPC) runs, use `--approve`/`--no-approve` or a saved trust decision. https://pi.dev/docs/latest/security
- Pi deliberately ships no sub-agents, no plan mode and no built-in to-dos. https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent
- Local models: in `models.json`, set `contextWindow` (default 128000) and `maxTokens` (default 16384) **to match the server's real -c**. `samplingParams` are merged into every request for OpenAI-compatible APIs. https://pi.dev/docs/latest/models-configuration
- Compaction triggers at `contextWindow - reserveTokens`. Defaults are reserveTokens 16384 and keepRecentTokens 20000. https://pi.dev/docs/latest/compaction
- llama.cpp with pi: `--jinja`, `--host 127.0.0.1`, `-ngl 999`, `-c 32768` as the example. "Keep `--host 127.0.0.1` for local-only access." https://pi.dev/docs/latest/llama-cpp
- Strata 0.2.2: I found no community documentation, so there's no standard to measure it against.

## 3. AGENTS.md conventions
- An open format, "a README for agents", with no required fields. Popular sections are project overview, build and test commands, code style, testing instructions and security considerations. Nested AGENTS.md files are allowed and the closest one wins. It's "living documentation". https://agents.md/
- For Ralph specifically: operational only, ~60 lines, not a diary. Progress goes in the plan file. https://github.com/ghuntley/how-to-ralph-wiggum ; "keep it brief", "DO NOT PLACE STATUS REPORT UPDATES" in it. https://ghuntley.com/ralph/
- Learnings: snarktank uses a separate append-only `progress.txt` and promotes only reusable patterns into AGENTS.md. https://github.com/snarktank/ralph

## 4. llama.cpp and llama-swap for local agentic coding
- **Tool calling needs `--jinja`** (the default on recent builds). Without it, llama.cpp silently ignores `tools`. `capabilities.tools: true` in llama-swap only advertises support. https://github.com/mostlygeek/llama-swap/blob/main/docs/kb/guides/model-runtime/writing-cmd.md ; https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md
- "**Beware of extreme KV quantizations (e.g. `-ctk q4_0`), they can substantially degrade the model's tool calling performance.**" Known-good examples use `-fa` and Q4_K_M or higher (Q6_K_L) for small and mid models. https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md
- llama-swap minimal cmd uses `--port ${PORT}`. Start small. `-validate` checks config. https://raw.githubusercontent.com/mostlygeek/llama-swap/HEAD/docs/kb/guides/configuration/configuration-overview.md
- A typical community agentic macro is `--jinja --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --parallel 1 --ctx-size 65536`, with ctx-size always set explicitly. `--parallel 1` because higher values split the KV cache. https://github.com/akitaonrails/llm-coding-benchmark/blob/master/docs/llama-swap.md
- **Context:** Qwen's recommended output/context for Qwen3-Coder is 65,536 ("can be increased"). https://unsloth.ai/docs/models/tutorials/qwen3-coder-how-to-run-locally . The pi example is 32K. 64K is the community middle ground for single-stream agentic work. https://github.com/akitaonrails/llm-coding-benchmark/blob/master/docs/llama-swap.md
- **Quant:** the community default is Q4_K_M or UD-Q4_K_XL. Unsloth's Aider Polyglot table shows 3-bit to 4-bit close **on a 671B model** (IQ3_XXS 65.6-66.8% vs Q4_K_M 67.7-69.7%). Low-bit quants hold up on very large models, and smaller dense models lose more. https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/unsloth-dynamic-ggufs-on-aider-polyglot . The llama.cpp tool-calling examples use Q4_K_M and up. https://github.com/ggml-org/llama.cpp/blob/master/docs/function-calling.md
- **Sampling:** use the model card's values, not llama.cpp defaults. For example, Qwen3-Coder uses temp 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05, and min_p 0 to 0.01 ("llama.cpp default is 0.1"). https://unsloth.ai/docs/models/tutorials/qwen3-coder-how-to-run-locally . Pi can push these per model with `samplingParams`. https://pi.dev/docs/latest/models-configuration

## 5. Sandboxing and allowlists for headless agents
- The community norm is **autonomy inside an OS boundary rather than command-by-command allowlists**. Anthropic: sandboxing "safely reduces permission prompts by 84%", and "effective sandboxing requires both filesystem and network isolation." https://www.anthropic.com/engineering/claude-code-sandboxing
- Claude Code sandbox defaults: writes go to the working directory and temp. Reads cover most of the machine, with credential paths deniable. Network goes through an allowed-domain proxy. **On native Windows commands run unsandboxed; use WSL2.** https://code.claude.com/docs/en/sandboxing
- Allowlists are a "prompt fatigue mitigation". Accept-edits mode auto-approves `mkdir, touch, rm, mv, cp, sed` in the workdir. https://code.claude.com/docs/en/security
- Codex: `sandbox_mode = "workspace-write"` plus `approval_policy = "never"` for automation, and network for shell commands is a separate toggle. https://codex-best-practices-d67bea.pages.oit.duke.edu/best-practices/configuration.html
- Ralph forks allow `Bash(git *)`, `npm`, `pytest`, Edit and Write by default. https://github.com/frankbria/ralph-claude-code . The playbook says skip permissions and sandbox instead. https://github.com/ghuntley/how-to-ralph-wiggum
- Pi's position is that allowlists are "security theater". Isolate instead. https://mariozechner.at/posts/2025-11-30-pi-coding-agent/ ; https://pi.dev/docs/latest/security
- Threat model: the "lethal trifecta" is private data, untrusted content and external communication. Remove one leg, and the easiest is usually exfiltration. https://simonwillison.net/2025/jun/16/the-lethal-trifecta/ ; https://simonwillison.net/2025/Sep/26/how-to-stop-ais-lethal-trifecta/

## 6. Read-only web access for local agents
- Codex's default `web_search = "cached"` serves pre-indexed results, which "reduces exposure to prompt injection from arbitrary live content". Web search and shell network access are **separate controls**. https://learn.chatgpt.com/docs/agent-approvals-security ; https://learn.chatgpt.com/docs/config-file/config-basic
- Claude Code's network goes through an allowed-domain proxy, so `curl`/`git`/`npm` only reach allowed hosts. https://code.claude.com/docs/en/sandboxing
- Pi has no web tool by default, but curl is available. Treat fetched content as prompt-injection surface. https://mariozechner.at/posts/2025-11-30-pi-coding-agent/
- Since Forge has no secrets-bearing tools of its own, the norm supports giving it a **read-only fetch/search path** (docs, package indexes) while keeping exfiltration legs (posting, auth'd APIs) closed. https://simonwillison.net/2025/Sep/26/how-to-stop-ais-lethal-trifecta/

## 7. Addendum: the model and quant community (Strata docs), ~11:25 AM CT
- The project's own model table for Qwen3.8-Flash-Next (ISTA-DASLab GSQ-RCO GGUFs) lists Q2_0 as "good", IQ2_XS as "a bit better" and **IQ3_XXS as "best"**. On 64 GB of RAM, "keep its context at 128K or less". There's also an expert-pruned **Coder** variant "for code" (91.3% of full SWE-bench Verified, runs at 262K on 64 GB). https://raw.githubusercontent.com/Niko1221/Strata/main/docs/DETAILS.md
- So for this specific MoE, IQ3_XXS *is* the community top-quality pick on 64 GB. The generic "Q4_K_M" norm applies to small and dense models (section 4).
- The project measures with sampling at temperature 1.0, top_p 0.95 and top_k 20, and the model's default thinking level is **high**. Optional `thinking_budget_tokens` is supported. https://raw.githubusercontent.com/Niko1221/Strata/main/docs/DETAILS.md
- Prior box record /workspace/cos/plans/2026-10-19-community-overrides.md (F1-F10, S7) already lists Strata-specific community keys: tool_call_recovery, client contextWindow = server context, and so on.
