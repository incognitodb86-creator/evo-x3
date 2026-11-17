# 0.1 - Community best practice for our stack (research pass, 2026-10-23)

Ralph loop, Pi, Pi-on-llama-swap, llama-swap ComfyUI passthrough, ComfyUI video/H3, Compound
Engineering on Pi. Primary sources only, saved under `C:/AI/community/notes/web/` (prefix
`01r_*`). This is item 0.1 of `C:/Users/derek/5slock/ralph-community/fix_plan.md`: research only,
no config changes. Every claim below is tagged with its source file so any later item can be
re-checked. Written by Forge on AlienPc (Windows 11, RTX 4090, 64 GB).

## 0. Verdict in ten lines

1. Our Pi is **current** (1.4.0 = upstream v1.4.0, 2026-10-21) and our llama-swap is **current**
   (v266, built 2026-10-22 = upstream latest). Nothing to do on versions.
2. Our Pi settings are **stock-schema**: every key in `settings.json` exists in pi 1.4.0 docs
   (`01r_pi_configuration.html`, `01r_pidev_settings.html`). The non-stock part is two hand-written
   extensions and two disabled built-ins, not invented settings.
3. **CE is not installed in Pi.** `pi list` = `npm:pi-permission-system@0.8.0` only. The CE clone at
   `C:/AI/ce-plugin` (3.30.5) is dead weight until `pi install git:github.com/EveryInc/compound-engineering-plugin`
   is run (CE README, `01r_ce_readme.html` L334-337).
4. **CE needs `pi-subagents`** to dispatch its reviewer/research/implementation subagents:
   `pi install npm:pi-subagents` (CE README L340-343). Latest 0.81.0 (2026-10-22), not installed.
5. Our three Pi skills (`C:/AI/community/skills/*`) are **not discoverable** from Ralph's cwd: pi
   searches `~/.pi/agent/skills`, `.agents/skills`, project `.pi/skills` up the tree
   (`01r_pidev_skills.html` L59-63). Fix = user skills dir, `skills: []` in settings, or a local package.
6. Ralph community core is unanimous: **one task per loop**, **fresh context every loop**,
   **fixed stack allocation every loop** (PROMPT.md + fix_plan.md + specs), **main context as
   scheduler**, **subagents as the memory extension**, **exactly one subagent for build/test**,
   **Markdown over JSON** (`01r_ghuntley_ralph.html`, `01r_ghuntley_htrw_readme.txt`,
   `01r_snarktank_readme.txt`).
7. Our loop already matches the core: `ralph.ps1` runs `pi --print ... "@PROMPT.md"` per iteration
   with a **new session per iteration** (`--session-dir`), exits on `<promise>COMPLETE</promise>`,
   `-Max` bound, logs to `logs/ralph.log`. That is the published `while :; do cat PROMPT.md | agent; done`
   shape with a bounded count.
8. The one Ralph gap worth code: **exit detection is single-signal**. frankbria requires
   `completion_indicators >= 2` **and** the model's `EXIT_SIGNAL: true` (README L240-246); we trust one
   literal token. Premature "complete" is the classic Ralph failure (frankbria "Common Issues" L344-352).
9. **llama-swap ComfyUI**: our config already follows the official guide exactly - reserved id
   `comfyui_auto`, `compat.ignoreWebsockets: true` (the documented websocket fix), `checkEndpoint: /`,
   `cmdStop` graceful script, `unlisted: true` (llama-swap `docs/comfyui.md`, `01r_ls_comfyui.txt`).
   The doc's `/comfyui/<path>` passthrough is the stock way for an agent to drive ComfyUI.
10. **ComfyUI community tooling** = `comfy-cli` (`--where local --json`, envelope/1) and
    `comfy-mcp` (MCP server on top of comfy-cli: `run_workflow`, `get_queue`, `get_execution_error`,
    `get_logs`, `list_nodes`...), plus pi's built-in `builtin:mcp` - which we have disabled. Community
    path for H3 work is "introspect the live install, don't guess schemas" (`01r_comfycdocs_custom_node_issues.txt`,
    `01r_comfymcp_readme.html`).

## 1. Method

- Fetched with `curl.exe -sL --max-time 30`, classified and saved by
  `C:/AI/community/scripts/web_fetch.py` (extension chosen from the bytes; a 200-with-HTML body never
  lands as `.json`). Every pass ends with `python C:/AI/community/scripts/check_web_saves.py`.
  Final state of this pass: see section 12 (count printed by the checker).
- `npx skills` / skillhub were NOT used: this pass reads repos and docs directly (item 0.1 is reading).
- Negative results recorded, not silently dropped:
  - `https://pi.dev/docs/providers.html` -> 404. Correct path: `https://pi.dev/docs/latest/providers.html`
    (saved as `01r_pi_providers.html`).
  - `https://raw.githubusercontent.com/snarktank/ralph/main/progress.txt` -> 404 (that file is
    created by `ralph.sh` at runtime, it is not in the repo).
  - `https://pi.dev/llms.txt` -> 404 (saved then deleted).
  - `https://api.github.com/repos/ghuntley/ralphpipe` -> `{"message":"Not Found"}` and
    `api.github.com/search/repositories?q=ralphpipe` -> 0 hits. The "ralphpipe" name circulating in
    our notes has no such repo; treat that note as unverified.
  - `https://flowithpro.com/journeys/pi-llama-cpp-local-model` -> 404 (saved then deleted).
- Out of scope on purpose: `snarktank/ai-rp` (roleplay agent, unrelated to this loop),
  `teachingai/full-knowledge-base-Wan` (12k stars, Wan2.2 ComfyUI tutorial collection - a 194 MB
  JSON index, sampled only: it is Chinese-language tutorial links, not a spec: `01r_wan_fullkb_index.json`).
- No secrets in this file: Pi's `models.json` uses an `apiKey` command that reads a local key file;
  the path stays in `models.json`, the value is never written here.

## 2. Verified local state (read-only checks, 2026-10-23)

| Component | Local | Upstream (fetched) | Verdict |
|---|---|---|---|
| pi | 1.4.0 (`pi --version`) | v1.4.0, 2026-10-21 (`01r_pimono_release.json`) | current |
| pi-permission-system | 0.8.0 (only package in `pi list`) | latest 0.8.0, 2026-07-03 (`01r_npm_pi_permission_system.json`) | current, sole package |
| pi-subagents | not installed | 0.81.0, 2026-10-22 (`01r_npm_pi_subagents.json`) | missing (CE needs it) |
| pi-ask-user | not installed | 0.17.0, 2026-10-19 (`01r_npm_pi_ask_user.json`) | CE-recommended, interactive only |
| Compound Engineering | clone `C:/AI/ce-plugin` 3.30.5, not a pi package | `compound-engineering-v3.32.0`, 2026-10-23 (`01r_ce_release.json`) | behind + not wired into pi |
| llama-swap | v266 (c099777) built 2026-10-22 (`llama-swap --version`), exe `C:/AI/llama-swap-trial/bin` | v266, 2026-10-22 (`01r_llamaswap_release.json`) | current |
| ComfyUI | git `6b747c04` = v0.38.0, 2026-09-29 | v0.42.1, 2026-10-19 (`01r_comfyui_release.json`) | 4 releases behind (H3 nodes live in core, see section 7) |
| ComfyUI custom nodes | 49 dirs (`comfyctl:`, `example/`, `__pycache__` filtered), 223 `.py` | - | H3/LTX/Wan/SeedVR2/VHS present |
| Pi skills | `C:/AI/community/skills/{forge-self-diagnose,h3-hc-render,h3-prompting}` | pi discovery paths | not discoverable from Ralph cwd |
| Ralph loop | `ralph.ps1` 14 lines: `pi --print --provider llama-swap --model $Model --session-dir $K\sessions "@$K\PROMPT.md"`, `-Max` (default 10), sleep 2s, exit on `<promise>COMPLETE</promise>` | ghuntley bash loop, snarktank `ralph.sh` (max 10), frankbria (max 50) | shape matches; exit detection single-signal |
| Pi runner | `C:/AI/director/scripts/forge.ps1` = gpu_guard then `node .../bundle/cli.js @args` | pi stock CLI is on PATH (`pi`) | custom launcher, guard justified by real render-kill failures |

Exact Pi config read for this pass (`C:/Users/derek/.pi/agent/settings.json`):
`defaultProvider llama-swap`, `defaultModel coding_swift15_iq3s_esp`,
`defaultThinkingLevel high`, `defaultTools [read, edit, write, bash, grep, find, ls]`
(subset of pi defaults - `read, bash, edit, write` are the built-in four, `grep/find/ls` come from
`--tools`/`defaultTools` in 1.4.0), `compaction.enabled true` with
`reserveTokens 16384 / keepRecentTokens 16384` and per-model overrides
(24576/20000 for `llama-swap/coding_swift15_iq3s_esp` and `coding_sc117_strata`,
12288 for `strata/qwen3.8-flash-next-iq3_xxs`), `httpIdleTimeoutMs 1950000`,
`retry {enabled, maxRetries 2, provider {timeoutMs 1200000, maxRetries 0}}`,
`enableInstallTelemetry false`, `enableAnalytics false`,
`extensions ["-builtin:llama.cpp", "-builtin:mcp", "C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts", "C:/AI/director/.pi/extensions/protected-paths.ts"]`,
`images.blockImages true`.
`models.json`: providers `strata` and `llama-swap`, both `baseUrl http://127.0.0.1:8080/v1`,
`api openai-completions`, `apiKey` = shell command reading a local key file; model entries carry
`contextWindow 92160`, `maxTokens 16384`, sampling params
`temperature 1.0, top_p 0.95, top_k 20, min_p 0, presence_penalty 0`.
All of these keys are documented pi keys - no invented settings.

## 3. Ralph loop - community best practice

### 3.1 ghuntley.com/ralph (the technique, 2025-07-14, `01r_ghuntley_ralph.html`)

- The loop is a bash loop: `while :; do cat PROMPT.md | claude-code ; done`. "Ralph is a
  technique", "the technique is deterministically bad in an undeterministic world", "Ralph can be
  done with any tool that does not cap tool calls and usage."
  -> Our `ralph.ps1` is exactly this, with a `-Max` bound and `pi` in `--print` mode.
- Monolith, not microservices: "Ralph is monolithic. Ralph works autonomously in a single repository
  as a single process that performs one task per loop." Multi-agent agent-to-agent plumbing is
  "not needed" at this stage. -> Keep one agent per iteration; do not build agent-to-agent plumbing.
- Fixed stack allocation: "deterministically allocate the stack the same way every loop" -
  PROMPT.md + `@fix_plan.md` + `@specs/*` every iteration. Verbatim prompt pattern: "Follow the
  fix_plan.md and choose the most important thing."
  -> We pass `@PROMPT.md` every iteration; fix_plan.md is reached through PROMPT.md, not pinned in
  the launcher. Cheapest conformant move: add `@C:/Users/derek/5slock/ralph-community/fix_plan.md`
  to the launcher argv (one token, no new guard).
- Context is the budget: "the name of the game is that you only have approximately 170k of context
  window to work with. The more you use the context window, the worse the outcomes." "Your primary
  context window should operate as a scheduler", "Ralph requires a mindset of not allocating to the
  primary context window. Instead ... spawn subagents."
  -> Pi has no subagent tool in our config (pi-subagents not installed, no Task tool). This is the
  single biggest structural gap for 0.4/0.5: research, log reading and graph diffs all land in one
  context.
- Subagent throttle: "You may use up to N parallel subagents for all operations but only 1 subagent
  for build/tests" - "if you fan out to a couple of hundred subagents and then tell those subagents
  to run the build and test ... what you'll get is bad form back pressure."
- "don't assume it's not implemented" is the documented fix for Ralph's "Achilles' heel": ripgrep
  gives a false "not implemented" and Ralph writes a second implementation. Our PROMPT.md already
  carries this line.
- "no cheating": "Claude has the inherent bias to do minimal and placeholder implementations"; the
  fix is an explicit no-placeholder clause + "run the tests for that unit of code that was
  improved" + "capture the why" in test/doc comments ("future loops will not have the reasoning in
  their context window").
- Backpressure: types, tests, lints, static analysers - "anything can be wired in as back pressure",
  "the wheel has got to turn fast" (fast feedback beats maximal correctness). Dynamic languages
  require a type checker (pyrefly, dialyzer).
- Tuning, not blaming tools: "Every time Ralph has taken a wrong direction ... I haven't blamed the
  tools; instead, I've looked inside. Each time Ralph does something bad, Ralph gets tuned - like a
  guitar." "There is no such thing as a perfect prompt ... it has evolved through continual tuning
  based on observation of LLM behaviour." -> supports our per-pass self-diagnosis habit
  (notes/self_diagnosis.md) and short stable prompts.

### 3.2 ghuntley/how-to-ralph-wiggum playbook (`01r_ghuntley_htrw_readme.txt`, Clayton Madison)

Repo shape: `loop.sh`, `PROMPT_plan.md`, `PROMPT_build.md`, `AGENTS.md`, `IMPLEMENTATION_PLAN.md`,
`specs/*`, `src/`, `src/lib/`. Two modes: PLANNING (specs + code -> plan) and BUILDING (one task:
research -> implement -> validate -> commit).

- "Context is everything." Advertised 200K => usable ~176K. Target **40-60% utilization** = the
  "smart zone"; past clipping, tool calls still execute but the model cannot see their results.
  -> Local: our models advertise 92160 context (`models.json`) with compaction
  reserveTokens 24576 / keepRecentTokens 20000 on the Ralph model - the same discipline at a smaller
  scale. PROMPT.md must stay lean; reads must be targeted (grep before read, subagents later).
- **Markdown over JSON**: "JSON consumes ~3-4x more tokens than markdown for equivalent information
  density. LLMs are trained on diverse markdown." AGENTS.md = "Single, canonical heart of the loop",
  **~60 lines**, "NOT a changelog", sections Build & Run / Validation / Operational Notes / Codebase
  Patterns. "Status, progress, and planning belong in IMPLEMENTATION_PLAN.md, not here."
  -> Our two AGENTS.md files (ralph-community ~35 lines, 5slock ~40 lines) conform; keep the cap and
  push status into TASKS.md / notes. "AGENTS.md is how backpressure gets wired in per-project" - it
  must carry the real test / typecheck / lint commands (ours does).
- IMPLEMENTATION_PLAN.md is disposable: "I have deleted the TODO list multiple times" -> PLANNING
  regenerates it; BUILDING updates it (mark complete, add discoveries). No template on purpose.
- Acceptance-driven backpressure (enhancement): specs carry **acceptance criteria**, the plan carries
  **test requirements derived from them**, Ralph chooses the **how**. "Specify WHAT to verify
  (outcomes), not HOW to implement (approach)." Prevents placeholder work and gives a clean
  completion signal. -> Direct fit for our fix_plan: each R-line should name its check command.
- Non-deterministic backpressure (enhancement): criteria that cannot be computed (creative quality,
  aesthetics, content fit) get an **LLM-as-judge with binary pass/fail**
  (`{pass: boolean, feedback?: string}`), multimodal for images, `fast` vs `smart` judges, placed in
  `src/lib/` so the loop discovers it; variance is accepted because the loop iterates to pass.
  -> Local: we host vision judges (`vl_judge`, `qwen3vl_judge`) and our FINAL checks are
  builder-only ("no vision judge on explicit output", Derrick 2026-10-23 6:12 PM CT). Community
  endorses the mechanism; the standing instruction forbids it on explicit renders. Flagged for Derek
  in section 11 - do not add a judge unasked.
- "Steer upstream" = deterministic setup (specs, AGENTS.md, PROMPT); "steer downstream" =
  backpressure (tests, typecheck, lint, build). Both ends, nothing in the middle.

### 3.3 snarktank/ralph (22,052 stars; `01r_snarktank_readme.txt`, `_ralph_sh.txt`, `_prompt_md.txt`, `_agents.txt`, `_claude_md.txt`, `_contents.json`, `_prd_example.json`)

- `ralph.sh` (`set -e`, `MAX_ITERATIONS` default **10**, `--tool amp|claude`, `--tail-logs`) pipes
  the prompt into the agent and `2>&1 | tee -a logs/ralph-<date>.log`, then "if output contains
  'COMPLETE_TASK' then exit". Our `-Max 10` default and COMPLETE token match this shape.
- State lives on disk: `prd.json` (`project`, `branchName`, `description`, `userStories[]` with
  `id / title / acceptanceCriteria / priority / passes / notes`), `progress.txt` (append-only, with a
  Continuous Learning section), `archive/` + `.last-branch` (a fresh start when the project changes),
  `logs/`.
- `prompt.md` per iteration: read PRD, read progress log + Codebase Patterns, verify branch,
  "**Select the highest priority user story where passes: false**", implement exactly one story, run
  quality checks, commit as `feat: [ Story ID ] - [ Story Title ]`, set `passes: true`, append the
  progress log with the commit/thread reference.
- Continuous learning is a file convention: `AGENTS.md` collects "Codebase Rules ... useful to
  future development"; Claude's template calls this **loopback** - the file must name the commands
  the agent uses to evaluate its own work inside the same loop, and "the linter is your friend".
  Ours: the Learnings block in AGENTS.md + `notes/forge-learnings.md` = the same mechanism.
- The PRD is JSON in this implementation while the playbook argues for markdown; both ship upstream.
  Our markdown `fix_plan.md` + notes is the conformant choice (and the harness ticks it).

### 3.4 frankbria/ralph-claude-code (9,710 stars, pushed 2026-10-17; `01r_frankbria_readme.txt`, `_repo.json`)

- Same five-step cycle (read instructions -> execute -> track progress -> evaluate completion ->
  repeat), 14 CLI flags, `--max-iterations 50` default, `--sleep-seconds 5`, per-iteration logs under
  `.ralph/logs/`, `PHASE_OUTPUT` markers (`[RESEARCH] [IMPLEMENT] [TEST] [CRITIQUE] [ITERATE]`).
- **Exit is a two-key lock**: "Completion indicators found (minimum 2 required) AND the agent emits
  `EXIT_SIGNAL: true`"; also all tasks in `.ralph/fix_plan.md` complete "except unchecked items under
  `## High Priority` / `## Optional`", "multiple consecutive done signals", "excessive loops on
  testing", "usage limits reached".
- Documented failure modes to steal: "Agent gets stuck in testing loops" (fix: proceed once tests
  pass consistently), "Mistakes warnings as critical errors - **Read actual error messages!**",
  "Premature exit" (fix: require 2 completion indicators), "Timeout handling - long builds require
  patience".
- Self-correction: `fix_plan.md` keeps a Completed Tasks section with "Notes on what worked well".
- Mapping to 0.5, all of it loop logic in `ralph.ps1` + `fix_plan.md` (no new guard): (a) two-key
  exit, (b) consecutive-done counter, (c) a test-loop breaker expressed as an iteration counter, not
  a timer, (d) per-iteration log files, (e) `## Optional` exemption so stretch items never block the
  exit.

## 4. Pi (docs, settings, packages, extensions, MCP, compaction, skills)

### 4.1 The config surface is small and stock (`01r_pidev_settings.html`, `01r_pi_configuration.html`)

- Locations: global `~/.pi/agent/settings.json` plus `models.json`, project `.pi/settings.json`
  overrides; precedence CLI > project > global > defaults.
- Every key we use is documented: `defaultProvider`, `defaultModel`, `defaultThinkingLevel`,
  `defaultTools`, `enabledModels`, `compaction {enabled, reserveTokens, keepRecentTokens,
  modelOverrides}`, `retry {enabled, maxRetries, provider {timeoutMs, maxRetries}}`,
  `httpIdleTimeoutMs`, `telemetry`, `enableInstallTelemetry`, `enableAnalytics`, `lastNChoices`,
  `skills`, `terminal`, `images {blockImages, autoResize}`, `transport`, `theme`.
  -> No invented settings on this machine. 0.4 can be a subtraction pass, not an addition pass.
- `images.blockImages: true` is the documented switch for a text-only model; pi's `read` tool then
  refuses images. Correct for the coding model; vision belongs to the judge models. Do not flip it.
- Telemetry: `enableInstallTelemetry` default true, `enableAnalytics` default false; we set both
  false. Stock keys, privacy-hardened - keep.
- Built-ins are disabled with `-builtin:<name>` entries in `extensions`
  (`-builtin:mcp`, `-builtin:llama.cpp`, `-builtin:codemode`, `-builtin:tool-search`). The syntax is
  stock; the *decision* to disable MCP and llama.cpp is ours (see 4.4).

### 4.2 Pi against llama-swap (`01r_pidev_llamacpp.html`, `01r_pidev_modelsconfig.html`, `01r_pi_providers.html`)

- pi's own llama.cpp route (`01r_pidev_llamacpp.html`, "Local Models with llama.cpp") is a **direct
  connection to llama-server in router mode**: start `llama-server` with `--models-dir ~/models`,
  `--no-models-autoload`, `--jinja`, `-ngl 999`, `-c 32768` ("Omit it to use the model's native
  context, which may require substantially more memory"), then `/login llama.cpp` (default URL
  `http://127.0.0.1:8080`), `/llama` to load a model, `/model` to select it; the same values via
  `LLAMA_BASE_URL` / `LLAMA_API_KEY`; per-model context via llama.cpp model presets; plus a dedicated
  page "Run Pi with NVIDIA RTX and llama.cpp". Multi-shard and multimodal models go in
  subdirectories; restart the router after adding files.
  -> Two consequences. (1) **Keeping `-builtin:llama.cpp` off is correct**: that built-in is pi's
  direct llama.cpp path, a second way to load/unload GPU models next to llama-swap, which is exactly
  the class of request our "one GPU job at a time" rule forbids. Write that reason in AGENTS.md.
  (2) **Item 2.9 (context above 64K) is a launch-args + `models.json` job**; this page and the RTX
  page are the sources for `-c`, model presets and KV settings - not a pi setting.
- For an **OpenAI-compatible proxy** such as llama-swap, the documented route is `models.json`: a
  provider block with `baseUrl`, `api`, an `apiKey` given as a shell command that prints the value (so
  the value never sits in the file), and per-model `contextWindow`, `maxTokens`, `params`.
- Our `models.json` follows that schema exactly: two provider blocks (`strata`, `llama-swap`) on
  `http://127.0.0.1:8080/v1`, `api: openai-completions`, an `apiKey` command that reads a local
  key file, `contextWindow 92160`, `maxTokens 16384`, and `params`
  `temperature 1.0 / top_p 0.95 / top_k 20 / min_p 0 / presence_penalty 0`.
  -> 0.4 verdict: nothing invented here. Keep. The sampling block matters because local
  GGUF builds are sensitive to it, and the ESP variant is the model the loop runs.
- The llama.cpp package page is also the best doc on **model-side context and quantization effects**
  (KV quantization flags, `n_ctx`, flash attention). Our llama.cpp judges use `-c 65536` /
  `-c 32768`, `-fa on`, `-ctk q8_0 -ctv q8_0`, `-np 1`, `--image-min-tokens 1024` - the documented
  flags, so judge config is stock-shaped too.
- Pi's `--session-dir` gives a **new session per process**: `pi --print ... --session-dir <dir>` is
  the documented headless shape (`01r_pi_cli-integration.html`, `01r_pidev_cli.html`). Our loop uses
  it, so every iteration starts clean: the community-required "fresh context each loop" is satisfied.

### 4.3 Compaction and context pressure (`01r_pidev_compaction.html`, `01r_pi_configuration.html`)

- Compaction is on by default; settings are `enabled`, `reserveTokens` (kept for the next exchange),
  `keepRecentTokens` (how much recent context survives), and `modelOverrides` per `provider/model`.
- Branch-summarization keeps a path-navigable history, and summarization requests disable
  prompt-cache writes. On a local single-slot server (llama-swap swap group) prompt-cache behavior is
  worth knowing: every summarize call is a real GPU request, i.e. compaction is not free on this box.
- Local state: Ralph model 24576 reserve / 20000 keepRecent, strata 12288, global 16384/16384.
  With a 92160 window that keeps the loop in the playbook's "smart zone" for long sessions.
  -> 0.5 note: the loop's context risk is not the model's window, it is PROMPT.md + notes bloat:
  reading ralph.log, denies.log and sessions inside the iteration is exactly what the playbook warns
  about. Community answer = subagent (fan-out), not a bigger window.

### 4.4 Packages, extensions, MCP, built-ins (`01r_pidev_packages.html`, `01r_pi_packages.html`, `01r_pi_extensions.html`, `01r_pi_mcp.html`, `01r_pidev_security.html`)

- Pi packages are declared in `settings.json:packages` as `npm:<name>@<version>` / `git:<repo>` and
  installed with `pi install <source>`; `pi list` shows what is live. A package can ship
  `extensions`, `skills`, `prompts`, `themes`, `mcpServers` (see each package's `pi` field in
  `package.json`).
- Built-ins (`builtin:mcp`, `builtin:llama.cpp`, `builtin:codemode`, `builtin:tool-search`) are
  switched off with `-builtin:<name>` in `settings.extensions`. Both forms are stock; the reason has
  to be ours.
  - `-builtin:llama.cpp`: sensible on this box - pi's llama.cpp integration talks to a llama.cpp
    server directly, while all GPU access here goes through llama-swap; keeping both would create a
    second path to the GPU (the documented "one GPU job at a time" constraint). **Documented reason,
    keep.**
  - `-builtin:mcp`: removes pi's MCP client. Community tooling for ComfyUI is an MCP server
    (comfy-mcp, section 6) and CE does not need MCP. So the choice is defensible for the coding loop
    but it closes the door on the community ComfyUI agent path. **0.4 decision: re-enable for
    render/QA work, keep off for the loop, decide once and write the reason in AGENTS.md.**
- `01r_pidev_security.html` (pi's own security page): "No YOLO mode" - pi asks for confirmation
  before potentially dangerous operations and has configurable permission settings; "Trust your
  model" (a model that can run tools can do what the tools allow); secret hygiene (pi's own project
  template ignores the standard private-file conventions); a project-trust dialog; and the page says
  plainly that **isolation is not built in**: "Use protection - for stronger isolation use a sandbox
  or VM", pointing at a container guide.
  -> So the community-sanctioned safety stack for pi = permissions + trust + sandbox. `npm:pi-permission-system`
  (installed, current at 0.8.0) implements the permissions layer; it is the reason
  `C:/AI/community/notes/web` is unreadable by the `read` tool from this cwd (observed live during
  this pass: "Current agent is not permitted to run tool 'read' for path ... outside working
  directory ... policy-enforced"), while bash reads are allowed. That is real, working, published
  protection.
  -> Our two hand-written extensions (`C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts`,
  `protected-paths.ts`) sit on top of it. Per 0.4's rule (no custom guard without a real failure plus
  a published source) the audit is: `protected-paths.ts` duplicates what `pi-permission-system`
  already does (candidate for removal), and the headless guard's deny-list is the loop's only
  protection for the render/GPU and secrets - the class of failure with a real history on this box.
  **0.4 plan: read both files line by line, delete what pi-permission-system already covers, keep the
  GPU and secret rules, and confirm the guard does not cap iterations/context/tool calls (a custom cap
  needs a source).**
- Interactive extras that exist upstream: `npm:pi-ask-user` (0.17.0, blocks the model and renders a
  searchable question with allow / allow-always / deny, and "remembers permanent rules"), CE's
  recommendation for richer questions. Headless Ralph should not install interactive prompts by
  default - `--print` mode has no UI. Not needed; record as deliberately absent.

### 4.5 Skills (`01r_pidev_skills.html`)

- A skill = a directory with `SKILL.md` (frontmatter `name` + `description`); pi discovers them
  recursively from the user dir `~/.pi/agent/skills/`, the Agent Skills locations `~/.agents/skills/`
  and `.agents/skills/`, project `.pi/skills/` (walking up to the repo root), and from packages.
  Malformed files are skipped; name collisions keep the first.
- The model loads a skill when a task matches; "A model might fail to load a relevant skill, so use
  `/skill:name` when you need to force it"; `disable-model-invocation: true` makes a skill
  command-only; `enableSkillCommands` controls command discovery.
- Local state: three skills live in `C:/AI/community/skills/`
  (`forge-self-diagnose`, `h3-hc-render`, `h3-prompting`). Ralph's cwd is
  `C:/Users/derek/5slock/ralph-community`; there is no `.pi/` in it or in `C:/Users/derek/5slock`, and
  `~/.pi/agent/skills` and `~/.agents/skills` do not exist. **None of the three skills is
  discoverable by the loop today.** 0.4 fix (all stock): create `~/.pi/agent/skills` and copy/symlink
  the three directories, or add `skills: ["C:/AI/community/skills"]` to the global settings, or ship
  them as a local pi package. Pick one, do not invent a loader.

## 5. llama-swap (routing, TTL, ComfyUI passthrough, auth)

Sources: README (`01r_llamaswap_readme.txt`, v266), docs index (`01r_llamaswap_tree.json`),
`01r_ls_configuration-overview.txt`, `01r_ls_comfyui.txt`, `01r_ls_upstream-passthrough.txt`,
`01r_ls_ttl-and-unloading.txt`, `01r_ls_capacity-and-queues.txt`,
`01r_ls_client-compatibility-and-loading-feedback.txt`, `01r_ls_api-keys-and-auth.txt`,
`01r_ls_mcp-endpoint.txt`.

### 5.1 ComfyUI passthrough (`docs/comfyui.md` = `01r_ls_comfyui.txt`)

- Stated problem: "ComfyUI is not OpenAI compatible" and "ComfyUI's web UI connects over
  WebSockets ... llama-swap sees those connections as activity, so idle models never unload while a
  browser tab is open". The two documented fixes: **`compat.ignoreWebsockets: true`** and **a
  `checkEndpoint` that is `/`** (the root returns 200, and the ComfyUI API paths return 404, which
  keeps health checks from creating jobs).
- A dedicated passthrough exists: **`/comfyui/<path>` forwards straight to ComfyUI, "bypassing
  OpenAI parsing", and it is wired to the reserved model id `comfyui_auto`.**
- Our config matches the guide on every point: `comfyui_auto` (reserved id) + alias `ls_comfyui`,
  `unlisted: true`, `compat.ignoreWebsockets: true`, `checkEndpoint: /`, `ttl: 0`,
  `cmdStop = comfy_graceful_stop.ps1` (waits for the render queue, cap 1800 s) with
  `unloadTimeout: 1900` so the graceful stop is not killed at the global 15 s.
- `upstream.ignorePaths` (regex list for `.js|.json|.css|.png|.gif|.jpg|.jpeg|.ico|.txt`) is the
  documented way to stop asset traffic from counting as model activity - present in our config.
- **Finding for 2.x/3.x: `comfyui_longvideo` has `ttl: 0` (resident) but `unloadTimeout: 30` and a
  plain `taskkill` stop.** The ttl page is explicit that `ttl` decides *when* to unload and
  `unloadTimeout` decides *how long to wait* (global 10 s, slow backends 30 s and up). A long-video
  render on that instance therefore has ~30 s of graceful-stop budget, versus 1900 s on
  `comfyui_auto`. Give the long-video instance the same graceful-stop shape as `comfyui_auto`,
  or never queue a long render on it. Source: `01r_ls_ttl-and-unloading.txt` L43-57.
- Do NOT add a custom websocket-blocking proxy, custom queue watcher, or bespoke ComfyUI client: the
  passthrough plus these flags are the stock mechanism (item 0.4 "published source" test passed).

### 5.2 Routing, TTL and concurrency (`01r_ls_capacity-and-queues.txt`, `01r_ls_ttl-and-unloading.txt`)

- One exclusive `swap: true` group with `exclusive: true` is the documented single-model-at-a-time
  mechanism; `concurrencyLimit` caps parallel requests per model, `globalConcurrencyLimit` caps
  served inference requests across all models ("what `concurrencyLimit` cannot do since it only
  counts requests to one model"). On one GPU, `globalConcurrencyLimit: 1` is the documented shape;
  our config expresses exclusivity through the swap group instead, which is the documented routing
  mechanism - acceptable, and worth writing down so a future pass does not "fix" it.
- `ttl: 0` = stay resident (ComfyUI instances), `ttl: 600` = unload after 10 min idle (coding and
  judge models), `globalTTL: 0` (no forced unload), `unloadTimeout` raised per slow backend.
- Two more documented knobs we deliberately leave at default: `sendLoadingState` and
  `includeAliasesInList` (`01r_ls_client-compatibility-and-loading-feedback.txt`: clients "should read
  `/v1/models` before choosing a model and be prepared for a request to wait while llama-swap loads
  it"; set `sendLoadingState: true` only when a client can display a loading response "rather than
  timing out or retrying blindly"). pi does not render a llama-swap loading body, so the stock answer
  for us is the long client-side wait we already have (`httpIdleTimeoutMs 1950000`,
  `retry.provider.timeoutMs 1200000`) - leave both flags off and do not add a retry loop.
  `upstream.ignorePaths` is documented as RE2-compatible expressions that stop static/UI paths from
  triggering a swap, "keep the default static-asset patterns" - ours is the default set
  (`01r_ls_upstream-passthrough.txt`).
- `healthCheckTimeout: 1200` and `timeouts.responseHeader: 1200` (20 min) are the documented knobs
  for slow model loads and long renders - both needed on this box (a 4090 loading a 96K-context
  quant is minutes; a render is tens of minutes).
- Loop-relevant knobs for 0.5 (all documented, none invented): queued requests while a model loads
  (`swapQueueSize`, `queueDebug` for logging why a request is queued), `swapRetries` for failed
  swaps, `swappingInterval`, and `logLevel: debug` for a diagnosis pass. The Ralph failure "the agent
  gets stuck / times out while a model swaps" is answered by queue + header-timeout settings, not by
  a custom timer in `ralph.ps1`. Pi's side is `retry {maxRetries 2, provider.timeoutMs 1200000}` and
  `httpIdleTimeoutMs 1950000` - both already sized above a swap.

### 5.3 Auth on a loopback proxy (`01r_ls_api-keys-and-auth.txt`)

- The published mechanism, in one line each: keys live in a file in llama-swap's data directory;
  there are **admin keys (minimum 8 characters)** and **per-model keys**, with groups
  (`modelApiKeyGroups`), a key-management API on the admin port, a command that generates a small
  web UI for key management (`swag`), rotation by regenerating the file, remote validation via
  `apiServerURLs`, and `proxyForwardHeaders` when a trusted reverse proxy forwards the header.
- Documented passthrough rule that matters to us: **calling `/comfyui` requires an admin key**;
  unlisted models are reachable only through the passthrough, and `/v1/models` returns 404 for the
  reserved `comfyui_auto` id.
- Our config has **no keys at all**; the control is that everything binds to `127.0.0.1` and the
  machine is single-user. That is a legitimate posture for a loopback-only box (the docs present keys
  as the answer for exposing the proxy), and it is the honest way to satisfy 0.4's "custom guard
  needs a source" rule: **do not add a hand-written guard in front of llama-swap; if we ever expose
  it, turn on the documented keys** (admin + per-model, rotation documented).
- The GPU-swap guard (`gpu_guard.ps1` + `forge.ps1`) is a different job: it stops the *agent* from
  requesting a model swap while a render runs. No community equivalent found (llama-swap has no
  "render lock" concept; the closest stock knobs are `exclusive`, `concurrencyLimit` and `ttl`). It
  is justified by a documented local failure class (a swap mid-render kills the render) and must stay
  documented in AGENTS.md.

### 5.4 The llama-swap MCP endpoint (`01r_ls_mcp-endpoint.txt`) - read-only and safe

- llama-swap serves **its own documentation as an MCP server at `/api/mcp`** ("the same tools the web
  UI's Help page uses"), speaking **MCP revision 2026-07-28 only** (that revision dropped the
  initialize handshake, which is what lets it be a single stateless POST). Tools are namespaced
  `<provider>__<tool>`: `docs__list_docs`, `docs__get_doc`, `docs__search_docs`,
  `docs__get_config_schema` ("the JSON schema for a config key: type, default, allowed values, child
  keys") and `config__get_config` (the **effective** running config as YAML, defaults filled in,
  credentials `[REDACTED]`, selectable with a jq `query`). "Every tool is annotated `readOnlyHint`".
- With `apiKeys` set, the endpoint requires a key (bearer / `x-api-key` / basic); with none it is
  open, "so treat it the same way you treat the rest of llama-swap".
- Fit for us: the stock way for an agent to answer "what does this config key mean, what is its
  default" from the running instance instead of guessing - it serves 0.5 and 2.9. It is read-only, so
  it cannot load, unload, swap or queue, and does not conflict with the GPU rule. pi-side wiring is in
  `01r_pi_mcp.html`: servers live in `mcp.json`, tools register as `mcp__<server>__<tool>`, exposure is
  per server, `/mcp` inspects/changes it, `--no-mcp` disables MCP for one run, and
  `--tools read,codemode,'mcp__radius__*'` selects tool sets. So MCP can be enabled **for a
  planning/diagnostic run only** - a stock flag, not a custom guard.

## 6. ComfyUI, video and H3

Sources: `01r_comfycli_readme.txt` (comfy-cli), `01r_comfymcp_readme.html` +
`01r_comfymcp_repo.json` (300 stars, pushed 2026-10-22), `01r_comfyui_release.json` (v0.42.1),
`01r_comfycdocs_agenttools_index.txt`, `01r_comfycdocs_mcp.txt`, `01r_comfycdocs_cli.txt`,
`01r_comfycdocs_install_custom_node.txt`, `01r_comfycdocs_custom_node_issues.txt`,
`01r_comfycdocs_h3_schema.json`, `01r_comfydocs_llms.txt`.

- **comfy-cli is the stock automation surface**: `comfy --here node add/remove/list/install/update`,
  `comfy --here which`, `comfy launch`, `comfy install [--fast-deps | --pr | --skip-manager]`,
  `comfy download`, `comfy jobs ls|status`, `comfy generate ...`, `comfy cloud ...`. Every command
  takes `--where local|staging|cloud` and `--json` (envelope/1 output), which is what an agent should
  parse. The custom-node page documents add/remove/update against a running install.
- **comfy-mcp is the stock agent surface**: an MCP server "built on comfy-cli", each tool shelling
  out to `comfy --where local --json`. Tools observed: `comfyui_version`, `run_workflow`,
  `run_template`, `get_template`, `get_queue`, `get_output`, `get_execution_error`, `get_logs`,
  `get_node`, `list_nodes`, `list_partner_models`, `list_workflow_notes`, `list_workflow_slots`.
  Capability set: generate (workflow JSON in API format or UI export), monitor jobs (async submit,
  watch/cancel, "read the failure verdict", collect outputs), **introspect the live install - "search
  the nodes, models, and templates your ComfyUI actually has (custom nodes included), not a static
  catalog"**, build/validate workflows, and manage the server (launch/stop/restart, tail logs, stage
  inputs). Default target is `127.0.0.1:8188` via `COMFYUI_URL` / `COMFYUI_HOST` / `COMFYUI_PORT`.
  The docs page `01r_comfycdocs_mcp.txt` frames the same choice: local ComfyUI + local MCP for coding
  agents (Claude Code / Cursor / Codex), hosted Comfy Cloud for newcomers.
- **The H3 schema question has a community answer: introspect, don't guess.** We keep
  schema-stale bugs because a frozen graph outlives a node update (the r3b nodes 10/11 are known
  schema-stale after ComfyUI 0.19.2 dropped `sparse_blocks` / `sparse_size` / `max_dims`).
  `list_nodes` / `comfy --here node list --json` / a live `object_info` dump is the documented way to
  read a node's real inputs; the docs' custom-node-issues page prescribes reproducing on an updated
  install with the node list attached.
- Version state: local ComfyUI `v0.38.0` (git 6b747c04, 2026-09-29) vs upstream `v0.42.1`
  (2026-10-19) with **49 custom node repos** installed. Community upgrade practice for this shape is
  `comfy node update` against a **test runtime** (the docs' custom-node page: update, reproduce, and
  report to the node repo), and our box already has a second runtime for A/B (`C:/AI/comfy-longvideo`)
  - use that as the upgrade canary, and re-dump `object_info` after the upgrade before re-submitting
  any frozen graph.
- Video node landscape (local inventory, all present): `ComfyUI-H3-Continuum`,
  `ComfyUI_MiniMax_H3_Extender`, `comfyui-minimax-h3-continuation`, `MiniMax-H3-Prompt-Rewriter-ComfyUI`,
  `ComfyUI-MiniMaxH3_LatentUpscaler`, `ComfyUI-H3-Latent-Upscaler-Mamad8`, `ComfyUI-LTXVideo`,
  `ComfyUI-WanVideoWrapper`, `ComfyUI-VideoHelperSuite`, `seedvr2_videoupscaler`. Community video
  guidance we can act on is mostly about workflow mechanics (frame-count grids, chunk math, latent
  upscalers, VHS encode), which our AGENTS.md already encodes as learnings; the new part is the
  tooling (comfy-cli / comfy-mcp) and the schema-introspection habit.
- `01r_comfycdocs_h3_schema.json` (8,540 bytes, JSON-valid) is the **Comfy Router** OpenAPI document
  for the *hosted* model `minimax/minimax-h3` ("the request body Comfy Router accepts ... the INPUT
  schema is the same schema the server validates a call against"). It is **not** the schema of the
  local `MiniMaxH3*` custom nodes - a claim in our notes said it was, and that is wrong (recorded for
  0.2). Useful for a cloud fallback path, useless for validating a local graph. The Wan tutorial index (`01r_wan_fullkb_index.json`, 194 KB) is a link
  collection, not a spec - sampled, low value, kept for the record.

## 7. Compound Engineering on Pi (`01r_ce_readme.html`, `01r_ce_release.json`, `C:/AI/ce-plugin`)

- CE on pi is **a pi package**: `pi install git:github.com/EveryInc/compound-engineering-plugin`.
  Its `package.json` declares `pi.extensions` + `pi.skills` (local clone: `./.pi/extensions/compound-engineering.ts`,
  `./skills`) - so installing it wires the extension and skills; nothing custom is needed.
- Required companion, quoted: "Required companion for CE workflows that dispatch reviewer, research,
  or implementation subagents: `pi install npm:pi-subagents`". Recommended for richer blocking
  questions: `pi install npm:pi-ask-user`. Reload with `/reload-plugins` (omp) / `/reload` (pi) after
  installing.
- The loop CE prescribes (six steps): `/ce-brainstorm` (requirements-only plan) -> `/ce-plan`
  (implementation-ready plan) -> `/ce-work` (execute with host verification, commits, shipping) ->
  `/ce-simplify-code` -> `/ce-code-review` (report-only multi-agent review against the plan; the
  local apply is explicit) -> `/ce-compound` ("Capture the learning into `docs/solutions/` so the
  next loop starts smarter"). "Each cycle compounds ... That return arrow is the whole point."
  Around-the-loop: `/ce-strategy`, `/ce-product-pulse`, `/ce-sweep`, `/ce-compound-refresh`;
  on demand: `/ce-ideate`, `/ce-bakeoff`, `/ce-pov`, `/ce-debug`, `/ce-explain`, `/ce-doc-review`,
  `/ce-optimize`, `/ce-prototype`; git: `/ce-commit`, `/ce-commit-push-pr`, `/ce-babysit-pr`,
  `/ce-worktree`; browser/device: `/ce-test-browser`, `/ce-test-xcode`, `/ce-polish`, `/ce-dogfood`.
- `/lfg` = the hands-off full loop: pick the route to a verified work source, work it, simplify,
  review and apply, capture durable learning, run browser tests, commit; push and open a PR when a
  remote exists, with a bounded CI repair loop; "with no remote it stops at local commits".
  Recommended sequence: `/lfg` runs the loop; start it after `/ce-brainstorm` "so it plans against
  real requirements rather than a one-line prompt".
- Local state: CE 3.30.5 clone on disk, **not installed as a pi package**, latest upstream
  **3.32.0 (2026-10-23)**, `pi-subagents` 0.81.0 absent. Our PROMPT.md names four CE steps
  (plan, work, review, compound) - the CE loop has six, and CE's own docs put brainstorm *before*
  plan and simplify *between* work and review.
- 0.4/0.2 actions, all stock: `pi install git:github.com/EveryInc/compound-engineering-plugin`
  (upgrades to 3.32.0 by definition), `pi install npm:pi-subagents`, `pi update` afterwards; then
  PROMPT.md may reference `/skill:ce-plan`, `/skill:ce-work`, `/skill:ce-code-review`,
  `/skill:ce-compound` (pi 1.4.0 supports `/skill:<name>`, CE docs use that form for hidden skills).
  No custom CE adapter, no hand-written skill shim.

## 8. Gaps and actions, per later item in fix_plan.md

Each row: the community claim (file), our state, and the action that is allowed by the "stock-simple"
rule. Nothing here invents a guard, cap, timer or hook.

| Item | Community source | Our state | Action (stock) |
|---|---|---|---|
| **0.2** claim audit | ghuntley playbook: verify against the repo/docs, not a blog summary; frankbria: "Read actual error messages" | Our notes list claims with star counts and dates | Cross-check the two claims this pass already caught as **wrong/stale**: "ralphpipe repo at ghuntley" (no such repo, 0 search hits) and "H3 schema = the Comfy docs JSON" (it is the **Comfy Router cloud** OpenAPI for `minimax/minimax-h3`, not the local node schema). Record in `notes\self_setup_20261023.md` as claim \| source \| verdict \| action |
| **0.2** | ComfyUI docs: read the node list of the running install (comfy-cli `node list --json`, comfy-mcp `list_nodes`) | Our AGENTS.md carries a hand-transcribed node/schema history with a known stale entry (r3b nodes 10/11) | Add a rule to 2.x: any graph claim must be produced by a live `object_info` / `comfy node list --json` dump, dated, saved in notes |
| **0.4** make pi stock | CE README (pi section): `pi install git:github.com/EveryInc/compound-engineering-plugin` + `pi install npm:pi-subagents`; pi skills doc (discovery paths); pi security doc (permissions + trust + sandbox); pi MCP doc (`mcp.json`, `mcp__<server>__<tool>`, `/mcp`, `--no-mcp`) | Only `npm:pi-permission-system@0.8.0`; CE clone not installed; `pi-subagents` absent; skills undiscoverable; `-builtin:mcp` and `-builtin:llama.cpp` off; 2 custom `.ts` extensions | Execute 0.4 as written: drop the 2 custom extensions, drop `-builtin:mcp`, keep pi-permission-system (its forge-policy is already secrets-only), install CE + pi-subagents, add `~/.pi/agent/skills` (or `skills: []`), log in `notes\installs_downloads.md`. Keep `-builtin:llama.cpp` off and write the one-line reason in AGENTS.md (single GPU path = llama-swap) |
| **0.4** extension audit | pi security: "No YOLO mode", permission settings, "Use protection ... sandbox or VM"; pi-permission-system README/npm | `protected-paths.ts` duplicates path protection that pi-permission-system enforces (observed enforcing out-of-cwd reads this pass) | Delete `protected-paths.ts`; keep the secrets rules; if the truncate half of `headless-guard-and-truncate.ts` caps context/iterations, that is a custom cap -> remove it (pi `compaction` is the stock mechanism) and keep only deny rules with a documented failure behind them |
| **0.4** MCP for the loop | llama-swap `docs/mcp.md`: `/api/mcp` serves **read-only** docs + effective-config tools (`docs__*`, `config__*`, `readOnlyHint`), MCP revision 2026-07-28 only | `-builtin:mcp` off, no `mcp.json` | Optional, safe, high value: one MCP server entry for llama-swap docs (read-only) so config questions get answered from the running instance. Do **not** wire comfy-mcp into the loop: it can launch/stop ComfyUI and run workflows - exactly what the GPU rule forbids |
| **0.5** loop rewrite | ghuntley: fixed stack every loop, one task, main context = scheduler, subagents; frankbria: two-key exit + optional-section exemption + iteration-based test-loop breaker; snarktank: one highest-priority story, progress log, commit format | Fresh session per iteration, `-Max`, single-token exit, shared ralph.log, no progress log, no two-key exit | Rewrite list, all loop logic: (1) pin `@fix_plan.md` in the launcher argv; (2) two-key completion (>= 2 completion indicators **and** the promise token) with a consecutive-done counter; (3) iteration counter that breaks a test-only loop; (4) `## Optional` never blocks exit; (5) append-only progress file with the commit sha per pass; (6) per-iteration log filename; (7) keep `-Max` (snarktank uses 10); (8) no new timers, no GPU calls |
| **0.5** context discipline | playbook: 40-60% utilization, "don't allocate to the primary context window", 1 subagent for build/test; pi compaction modelOverrides | 92160 window, 24576/20000 compaction on the Ralph model, no subagents | After pi-subagents installs, PROMPT.md adds: fan-out reads/research to subagents, exactly one subagent for test+build validation, keep the main context a scheduler. Keep the existing compaction numbers (they already hold the smart zone) |
| **0.6** compound | CE: `/ce-compound` "Capture the learning into `docs/solutions/` so the next loop starts smarter"; snarktank AGENTS.md Codebase Rules; ghuntley "capture the why" | AGENTS.md Learnings (15-line cap) + `notes/forge-learnings.md` + `notes/learnings/` | Same mechanism, CE vocabulary: name the CE skills in PROMPT.md via `/skill:ce-plan`, `/skill:ce-work`, `/skill:ce-code-review`, `/skill:ce-compound`, and point the learnings file at `docs/solutions/`-style entries (one problem, one file, dated) |
| **1.2** adults-only gate | ghuntley: backpressure must be a command in AGENTS.md; snarktank: "loopback" = the file names the checks the agent runs on itself | `test_p6_review.py` + `comm.guard_ok` in `run_graph_job.py`; the pytest command is in both AGENTS.md files | No change. State it in 1.2's record as the primary backpressure, with the SHA256 proof line |
| **1.3 / 2.x renders** | comfy-cli (`--where local --json`), comfy-mcp tool set, llama-swap `/comfyui` passthrough, custom-node-issues page (update + reproduce + report) | Custom `run_graph_job.py` + `comfy_ctl.py` + direct `:10004` submits | Keep the render path (it is proven and carries `comm.guard_ok`), and add the community surface beside it: `comfy --where local --host 127.0.0.1 --port <upstream> node list --json` for schema truth; llama-swap `/comfyui/<path>` as the documented way to reach ComfyUI through the proxy. Adopt the failure-verdict habit: read the execution error, not just the queue |
| **2.x long video** | llama-swap ttl page: `unloadTimeout` = graceful-stop budget, slow backends need more | `comfyui_auto` 1900 s (good); `comfyui_longvideo` 30 s + `taskkill` | Fix in the yaml (allowed under the bakeoff exception, GPU idle + backup + log): give `comfyui_longvideo` the graceful-stop script + a > render-cap `unloadTimeout`, or never queue long renders there |
| **2.9 context raise** | pi `models.json` (per-model `contextWindow`, `params`); llama.cpp docs (`n_ctx`, KV quant `q8_0`, flash attention, `--dram-only`-class flags) | `contextWindow 92160`, `maxTokens 16384`, judges at `-c 65536`/`32768` with `-ctk/-ctv q8_0` | Do the 2.9 change in `models.json` + the strata/llama.cpp launch args, the documented pair; verify with `pi --session-dir` on a real task, not with a synthetic prompt |
| **ComfyUI version** | ComfyUI releases (v0.42.1 vs local v0.38.0); comfy-cli node update; custom-node issues page | 49 node repos, H3 packs local, frozen graphs known schema-stale | Upgrade on the canary runtime (`C:/AI/comfy-longvideo`) with comfy-cli, re-dump `object_info`, compare node inputs for the frozen graphs, then decide on the main runtime. Never upgrade the runtime that is mid-render |
| **CE version** | CE release `compound-engineering-v3.32.0` (2026-10-23); local 3.30.5 | Not installed | `pi install git:...` (installs latest), then `pi list` + `/skill:ce-plan` smoke test. No manual patching of the clone |
| **Judges** | playbook non-deterministic backpressure: LLM-as-judge, binary pass/fail, multimodal | `vl_judge` + `qwen3vl_judge` exist; Derrick forbids a judge picking KEEP | No action. Present the option to Derrick (section 10); do not build it |

## 9. Verified-conformant (do not touch, and do not "fix")

- llama-swap v266 and pi 1.4.0 - both current; no version work in 0.4 beyond CE/subagents.
- `llama-swap.yaml` ComfyUI block: reserved id, `unlisted`, `ignoreWebsockets`, `checkEndpoint: /`,
  graceful `cmdStop`, `unloadTimeout: 1900`, `upstream.ignorePaths` - each one is the documented
  answer to a documented problem in `docs/comfyui.md` and `docs/ttl-and-unloading.md`.
- Single exclusive swap group for one GPU (documented routing) - do not add `globalConcurrencyLimit`
  on top of it "for safety".
- Pi `settings.json` keys, `models.json` provider/model/params shape, compaction model overrides,
  `httpIdleTimeoutMs`, `retry`, `images.blockImages`, telemetry off - all documented keys.
- `ralph.ps1` fresh-session-per-iteration + `@PROMPT.md` + bounded `-Max` = the published shape.
- AGENTS.md size and shape (commands + learnings, no status) = the playbook's ~60-line rule.
- `forge.ps1` + `gpu_guard.ps1` = the one custom guard with a documented failure class behind it;
  keep, keep documented in AGENTS.md, and keep it out of pi's extension chain.

## 10. Open questions for Derrick (research raised these; no action taken)

1. Aesthetic backpressure: the community mechanism for "does this clip look good" is a binary
   LLM/vision judge (playbook, "Non-Deterministic Backpressure"). Our standing instruction is
   "no vision judge picks keepers, KEEP is Derrick's alone". Options: (a) keep as is, (b) judge as
   a *filter* that only flags defects (black frames, no audio, face loss) and never picks, (c) full
   judge scoring on BAKEOFF lines only. (b) is the smallest change and needs no new guard.
2. MCP for the loop: enable `builtin:mcp` with the **read-only** llama-swap docs server only
   (safe, helps 0.5/2.9), or keep MCP fully off?
3. comfy-mcp is powerful enough to run ComfyUI end to end; do we ever want it in the loop, knowing
   it can launch/stop the server (our rule says the loop must not touch llama-swap/ComfyUI control)?
4. Subagents: pi-subagents gives fan-out for research and a single builder/tester. It adds a package
   and a `subagents` tool surface - confirm you want it in the unattended loop (CE requires it).
5. `pi-ask-user` is interactive; the loop is headless. Confirm we stay without it.
6. CE 3.32.0 install will start loading 40+ CE skills into the loop's context. If context is the
   scarcest resource, do we install CE and reference only 4 skills, and keep the rest
   `disable-model-invocation` style command-only?

## 11. Source manifest and how to re-verify

Saved under `C:/AI/community/notes/web/`, 63 files, 3,152,647 bytes, all `*.json` parse
(`python C:/AI/community/scripts/check_web_saves.py` -> CLEAN, rc 0; run at the end of this pass).
Files prefixed `01r_` are this pass; 404 artifacts were saved as `.404.txt` then deleted.

Ralph (github raw + api.github.com + ghuntley.com): `01r_ghuntley_ralph.html` (89 KB,
canonical https://ghuntley.com/ralph/), `01r_ghuntley_htrw_readme.txt` (62 KB,
raw.githubusercontent.com/ghuntley/how-to-ralph-wiggum/main/README.md),
`01r_snarktank_readme.txt` / `_ralph_sh.txt` / `_prompt_md.txt` / `_agents.txt` / `_claude_md.txt` /
`_contents.json` / `_prd_example.json` / `_repo.json` (raw + api.github.com/repos/snarktank/ralph),
`01r_frankbria_readme.txt` (56 KB) + `01r_frankbria_repo.json`,
`01r_ralphpipe_repo.json` (132 B = the Not Found body, kept as the negative result).

Pi (all `https://pi.dev/docs/latest/<slug>`, plus pi.dev docs pages): `01r_pidev_docs.html`,
`01r_pidev_cli.html`, `01r_pidev_settings.html`, `01r_pidev_skills.html`,
`01r_pidev_packages.html`, `01r_pidev_security.html`, `01r_pidev_compaction.html`,
`01r_pidev_llamacpp.html`, `01r_pidev_modelsconfig.html`, `01r_pi_quickstart.html`,
`01r_pi_configuration.html`, `01r_pi_extensions.html`, `01r_pi_mcp.html`, `01r_pi_providers.html`,
`01r_pi_sessions.html`, `01r_pi_codemode.html`, `01r_pi_environment-variables.html`,
`01r_pi_how-pi-works.html`, `01r_pi_cli-integration.html`, `01r_pimono_readme.txt` +
`01r_pimono_release.json` (badlogic/pi-mono), `01r_mza_posts.html` (mariozechner.at),
`01r_npm_pi_permission_system.json`, `01r_npm_pi_subagents.json`, `01r_pi_subagents_readme.txt`,
`01r_npm_pi_ask_user.json` (npm registry metadata).

llama-swap: `01r_llamaswap_readme.txt`, `01r_llamaswap_release.json`,
`01r_llamaswap_tree.json` (docs index, 219 KB), `01r_ls_comfyui.txt`,
`01r_ls_configuration-overview.txt`, `01r_ls_upstream-passthrough.txt`,
`01r_ls_api-keys-and-auth.txt`, `01r_ls_ttl-and-unloading.txt`, `01r_ls_capacity-and-queues.txt`,
`01r_ls_client-compatibility-and-loading-feedback.txt`, `01r_ls_mcp-endpoint.txt`
(docs at github.com/mostlygeek/llama-swap/tree/main/docs).

ComfyUI: `01r_comfydocs_llms.txt` (docs.comfy.org index), `01r_comfycli_readme.txt`
(Comfy-Org/comfy-cli), `01r_comfymcp_readme.html` + `01r_comfymcp_repo.json`,
`01r_comfyui_release.json`, `01r_comfycdocs_agenttools_index.txt`, `01r_comfycdocs_mcp.txt`,
`01r_comfycdocs_cli.txt`, `01r_comfycdocs_install_custom_node.txt`,
`01r_comfycdocs_custom_node_issues.txt`, `01r_comfycdocs_h3_schema.json` (8.5 KB - **Comfy Router
OpenAPI for the hosted `minimax/minimax-h3`**, not a local node schema),
`01r_wan_fullkb_index.json` (194 KB sampled, tutorial link collection).

Compound Engineering: `01r_ce_readme.html`, `01r_ce_release.json`; local clone `C:/AI/ce-plugin`
(3.30.5, `pi.extensions` + `pi.skills` in package.json).

Re-verify commands (all read-only):

```
pi --version ; pi list
"C:/AI/llama-swap-trial/bin/llama-swap.exe" --version
git -C C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI log --oneline -1
ls C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/custom_nodes | wc -l
python C:/AI/community/scripts/check_web_saves.py
curl.exe -sL --max-time 30 https://api.github.com/repos/<owner>/<repo>
curl.exe -sL --max-time 30 https://registry.npmjs.org/<package>
```
