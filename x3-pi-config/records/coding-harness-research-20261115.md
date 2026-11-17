# Coding harness + deep-research harness research and bake-off plan (EVO-X3)
Max Architect · Sun Nov 15 2026, ~5:31–5:50 PM CT · READ-ONLY. Nothing was installed, downloaded, loaded or changed. No secrets were touched.
Asks: Derrick t1780u (coding harness bake-off) + t1781u (deep-research version, video zHViiH9oB3k).
research-core used: yes · window: published ≥ 2026-05-01 (older only for repo facts) · tier DEEP, 44 calls (I went past the 40-call cap because t1781u added scope midway) · accessed 2026-11-15 CT
Community way: the harness-bench (miniml, May 12 2026) + Harbor/Terminal-Bench (official runner) + Romero Flash-Next harness runs (Sep 16 2026) → reuse Harbor as the runner; nothing new gets built except 4 Forge task folders.

## TLDR (hedged)
- **Keep pi as Forge's default and race it against Qwen Code and OpenCode v2.** In the only large local-model harness study, pi was first and Qwen Code second. pi also sends the smallest prompt, which saves time on every request on local hardware. On the exact Forge model (Qwen3.8-Flash-Next, llama.cpp Vulkan, 128 GB), pi and OpenCode both solved almost everything (Romero, n=1).
- **The biggest unknown is Halogen, not the harnesses.** It is not llama.cpp, so its tool-call parsing and its /v1/responses support (Codex needs it) are untested. Gate 0 below checks both before any bake-off.
- **The video is by Donato Capitella (kyuz0), who also makes our Strix Halo toolboxes.** He uses pi with his own `local-agent-builder` skill to build a 3-tier deep-research agent: orchestrator, searcher, page analyzer. It has tool quotas, and he scores it with an LLM-judge eval. It fits our stack directly: Flash-Next on Halogen, plus SearXNG, plus nomic embed-small.

## 1. Coding harness shortlist (local OpenAI-compatible, late 2026)
Repo facts come from the GitHub API, read 2026-11-15 ~5:40 PM CT. "pushed" = last push (UTC date).

| Harness | Local endpoint | Tool calls with Qwen/llama.cpp | Subagents | MCP | Skills / AGENTS.md | Context / prompt tax | Headless | Linux / Win | License · stars · pushed | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **pi** (earendil-works/pi, v1.5.2 Nov 10) | native llama.cpp + any OpenAI-compat via models.json | native; constrained JSON-schema sampling on built-in tools (changelog) | via `pi-subagents` pkg 0.88.1 | via extension, not built-in | skills + AGENTS.md (subagents need `inheritGlobalContext`) | ~2,008-token start prompt (Sutton); ~1.6k first request (onticpost) | `pi -p`, `--mode json` | both | MIT · 122k · 11-15 | **Incumbent, rank 1** |
| **Qwen Code** (QwenLM) | OpenAI-compat (`wireApi: chat-completions`) | tuned for the Qwen line | yes (docs) | yes | skills | not measured | `qwen -p`, yolo | both (Node) | Apache-2.0 · 30.5k · 11-15 | **Rank 2, arm** |
| **OpenCode v2.3** (anomalyco) | `@ai-sdk/openai-compatible`, llama-server documented | works with Flash-Next (Romero 6/6); some JSON tool errors reported earlier on Coder-Next | background by default since v2.3.0 (Nov 13) | yes (Code Mode) | AGENTS.md + .opencode/skills | heavy: ~18k (Sutton), 31k first request (onticpost) | `opencode run` | both | MIT · 227k · 11-15 | **Rank 3, arm**. Must be sandboxed: it read hidden graders in 14 cells |
| **Codex CLI** (openai) | local only via `wire_api="responses"`; chat API dropped | depends on the server's Responses API | yes | yes (~17k of MCP schemas at default) | AGENTS.md, skills | ~25k default, ~8.5k without MCP (Vaughan, via llmconfigurator) | `codex exec --json` | both | Apache-2.0 · 135k · 11-15 | **Optional arm**, only if Halogen serves /v1/responses |
| **Hermes Agent** (NousResearch) | own llama.cpp runtime, or `providers.llamacpp.base_url` | ok in a single onticpost test | delegation toolset | yes | skills | ~24k first request | one-shot mode prints nothing until done | both | MIT · 264k · 11-15 | Covered by the other audit; optional 5th arm |
| mini-swe-agent | litellm `api_base` | bash-only, no tool schema | no | Harbor passes MCP | — | tiny | yes | Linux | MIT · 9.6k · 11-09 | **Control arm** (the SWE-bench reference agent) |
| Aider | OpenAI-compat | text diff/whole edits (good for weak tool calling) | no | no | conventions file | repo map | yes | both | Apache-2.0 · 50k · last push 2026-05-22; PyPI 0.86.2 Feb 12 2026 | Drop: stale, and last in harness-bench (62.5%) |
| Claude Code (local) | via Anthropic-compat shim | 66.2% in harness-bench, but the shim is not what its prompts were tuned for | yes | yes | yes | ~33k prompt | yes | both | proprietary | Drop for local |
| Crush (charmbracelet) | OpenAI-compat | — | — | yes | — | ~16k (Sutton) | yes | both | NOASSERTION · 29k | Drop (prompt tax, unclear license) |
| Goose (now aaif-goose) | OpenAI-compat / Ollama | — | sub-recipes | yes (extensions) | recipes | fast startup (aictrl) | yes | both | Apache-2.0 · 57k · 11-15 | Not a coding-first pick; skip |
| Cline / Kilo Code | Ollama/LM Studio/OpenAI-compat | compact prompt mode | yes | yes | rules | 32k+ | CLI exists, IDE-first | both | Apache / MIT | Skip (IDE-first; Forge is headless) |
| OpenHands | OpenAI-compat via litellm | ok | yes | yes | microagents | heavy, Docker runtime | yes | Linux (Docker) | MIT · 94k | Skip for now (weight vs value) |

## 2. Best settings for agentic coding with Qwen3.x-class models
- **`--jinja` is mandatory.** Without it, Qwen3.8 tool names come back empty (llama.cpp #30078). Never use `--chat-template chatml`, because it has no tools (#22581). Use the model's own template, or the repo's Qwen3-Coder.jinja when calls fail. On Halogen, run the equivalent check in Gate 0.
- **Sampling (Qwen model card, as quoted by the GGUF cards):**
  - Thinking: temp 1.0, top_p 0.95, top_k 20, min_p 0, presence 0, repetition 1.0.
  - Non-thinking: temp 0.7, top_p 0.8, top_k 20, presence 1.5.
  - Pin the sampling on the server (Romero did) so every harness gets the same values.
- **Thinking effort:** the template default is xhigh, which made Romero's runs 4–100 min each. Qwen's warning, as reported by FreakyJolly, is that lower effort can make multi-turn agent tasks slower overall. So treat effort as a bake-off variable (medium vs high), not a guess.
- **KV cache:** keep Q8 or f16. Aggressive q4 KV hurts tool calls (refusalrate summary; secondary source). Use one slot (`-np 1`) for Forge. Use several slots only for deep research concurrency.
- **Context:** set the harness window below the server's. DataCamp ran the server at 131K and OpenCode at 65K. Match `contextWindow` in pi's models.json and Qwen Code's `contextWindowSize` to what the server really serves.
- **AGENTS.md patterns:**
  - Keep it short. Prompt tax is the main cost on local hardware.
  - Put testable rules first ("don't edit tests/, run the suite, smallest diff, clean tree"), the way Romero's task prompt does.
  - Write subagent instructions in the pi-subagents agent files, and set context inheritance explicitly.
- **Isolation:** pi has no permission system ("Run in a container", pi README via miniml). OpenCode peeks outside the workspace by default. Every arm runs in a container.

## 3. Benchmarks fit for a local bake-off
- **Harbor** (harbor-framework, the official Terminal-Bench 2.0 runner, Apache-2.0):
  - One CLI: `harbor run -d <dataset@ver> -a <agent> -m <model> --base-url ...`.
  - Pre-integrated agents include `pi`, `opencode`, `opencode-v2`, `qwen-coder`, `codex`, `hermes`, `mini-swe-agent`, `aider`, `goose` and `openhands`, with ATIF trajectories.
  - `harbor datasets list` includes SWE-Bench and Aider Polyglot. Tasks run in Docker containers, which gives us the isolation for free.
- **Terminal-Bench 2.0:** 89 tasks. The leaderboard is frontier-model only (top: NexAU-AHE + GPT-5.5, 84.7%). Use a 10-task subset.
- **SWE-bench Verified:** the mini-swe-agent docs support local litellm endpoints and `--slice` / `--filter`. One community dashboard (wonderrico, re-graded Sep 23 2026) has Qwen3.8-Flash-Next AWQ (vLLM, xhigh) scoring 97 on the first 100 django tasks. That is a single source on a different engine (SPECULATIVE for Halogen).
- **Aider polyglot:** Exercism exercises, already used in our 2026-10-31 Forge settings plan (brain `40_projects/max-fix-tests/plans/2026-10-31-forge-model-settings-benchmark.md`).
- **LiveCodeBench** is single-shot code generation, not agentic. Use it for model comparison only; it does not tell harnesses apart.
- **Published harness-vs-harness results:**
  - miniml harness-bench (May 12 2026): 16 private tasks, 1,360 runs. pi 76.9%, qwen 75.0%, claude 66.2%, opencode 63.8%, aider 62.5%.
  - Romero (Sep 16 2026): Flash-Next IQ4_XS on llama.cpp Vulkan, 128 GB. 17/18 resolved. pi missed 1 checkpoint (95/100) and opencode resolved 6/6. The judge rated pi's payroll answer 1/5 while opencode got 5/5, which shows why a human review score matters.
  - aictrl (Oct 21 2026): overhead only. pi was lightest.

## 4. Coding bake-off plan (T1)
**Gate 0: Halogen smoke check (about 20 min, needs OK; it uses the Forge slot).** Run these against the X3 Forge endpoint with a dedicated bake-off key:
- (a) 20 tool-call requests: simple, parallel, after a long tool result, with thinking on. Count leaked `<tool_call>` text and malformed arguments.
- (b) `/v1/responses` exists (yes/no). This decides whether Codex can be an arm.
- (c) Whether parallel slots work.

If (a) has more than 2 leaks in 20, stop and report: the harnesses can't be judged fairly until Halogen's parser is fixed.

**Arms (same endpoint, same pinned samplers, same thinking effort):**
1. pi + pi-subagents (incumbent)
2. Qwen Code
3. OpenCode v2.3
4. Codex CLI if Gate 0(b) passes, otherwise Hermes Agent
- Control: mini-swe-agent on the SWE-bench slice only.

**Task set (24):**
- 8 Terminal-Bench 2.0 tasks (fixed list, picked once and saved).
- 6 SWE-bench Verified tasks (fixed instance IDs).
- 6 Aider polyglot (Python + Rust + JS).
- 4 Forge tasks. Each runs on a frozen COPY at a pinned commit, never the live tree:
  - F1: fix a planted bug in a copy of `build_request.py` with hidden pytest.
  - F2: add a flag, e.g. `--shots single|multi`, to the copy, plus tests.
  - F3: make the existing flux-edit test suite pass after a planted regression. Copy from brain `40_projects/flux2-overnight/code/flux-edit/`.
  - F4: port or refactor a lint script (`flux_prompt_lint.py`) with no behavior change, graded by hidden golden outputs.

Graders are hidden outside the container, and Harbor's verifier restores tests.

**Metrics per run:**
- pass/fail and checkpoint score
- tool-call errors (malformed, unknown tool, leaked XML)
- prompt and completion tokens, plus requests
- wall time
- hidden-test peeking (grep the trajectories)
- Derrick's or Max's human review score (1–5: diff quality, honesty of the final report) on the Forge tasks

**Runs:** n=2 per (arm, task) in Phase 1, which is 4 arms × 24 tasks × 2 = 192 runs. Then the top 2 arms get n=4 on the 4 Forge tasks plus the 8 Terminal-Bench tasks (96 runs).

**Isolation:**
- Harbor Docker containers, each with its own scratch workspace.
- No mounts of C:\AI, ~/AI/render, ComfyUI, PixlStash or /etc/evo-x3.
- Network allowlist limited to the X3 endpoint.
- A separate bake-off API key. Derrick creates or types it, and it reaches the containers through Harbor's env, never a command line.

**Time estimate (SPECULATIVE, scaled from Romero's ~37 min/run at 14 tok/s with xhigh; Halogen decodes ~6x faster and prefills ~13x faster):**
- About 5–8 min per run at medium effort.
- Phase 1 ≈ 16–25 h serial, so 2 overnights. Phase 2 ≈ 8–13 h.
- Cutting to n=1 in Phase 1 halves it.

**Contention:**
- The X3 uses an exclusive "main" swap group. While Forge is loaded for the bake-off, Render/Sydney requests force a Heretic swap, which stalls both.
- Run only when Derrick says the Render writer and Sydney are idle, or after the v2 chain finishes writing.
- The AlienPc RTX (H3 render) is not touched.

**Decision rule:** best Forge-task pass rate first, then tool-call error rate, then wall time. A switch away from pi needs a gap of at least 10 points, or pi losing on the Forge tasks specifically.

## 5. Deep research (t1781u)
### 5a. What the video shows
"Building and Running a Deep Research Agent locally on Strix Halo & R9700 AI PRO" by Donato Capitella (@donatocapitella, the kyuz0 toolbox author), https://youtu.be/zHViiH9oB3k.
- **Source:** I read the auto-caption text from the YouTube page, retrieved 2026-11-15 ~5:45 PM CT and saved to /workspace/maxops/yt-zHViiH9oB3k-transcript.txt. I did not watch the video. The captions have no timestamps and misspell names, e.g. "coin" = Qwen and "strict seller" = Strix Halo.

What he says:
- **Problem:** a flat agent (web search + fetch) fills its context with raw pages. That slows prefill on local hardware, and "the work done to gather information pollutes the context used to write the final report."
- **Design, 3 tiers of delegation:**
  - The orchestrator splits the query into angles.
  - Searcher subagents search and save fetched pages to disk as markdown.
  - Page-analyzer subagents read those pages with grep + read of snippets, optionally semantic search, and return only the key facts.
  - The orchestrator writes a cited report.
- **Tool quotas:** a hard per-tool cap enforced by the harness, which returns an error, plus the remaining budget injected into the system prompt.
- **Search:** "DuckDuckGo or Tavily" named as examples.
- **Build:**
  - He uses pi (here through the "Pi agent for VS Code" extension) with his `local-agent-builder` skill copied into pi's skills folder. The skill scaffolds a Microsoft Agent Framework app with a TUI.
  - The repo README says it was tested through OpenCode with Qwen 3.5 122B.
  - Repo: kyuz0/local-agent-builder, 29 stars, **no license file** (per the GitHub API), last push 2026-06-10.
- **Models:**
  - He builds with Qwen3.6-27B MTP UD-Q4_K_XL on the R9700 using the newest ROCm toolbox.
  - He says the research agent itself is better on Qwen3.6-35B-A3B Q4, non-MTP, with llama.cpp at 5 concurrent requests.
- **Eval:** the scaffold's eval harness runs a 30-item dataset (his own queries plus some from an unnamed Hugging Face set) 3 times each, scored by an LLM judge with weighted criteria. The result was "an aggregate score of 79.1% across all of the runs." There is also an HTML results viewer.

### 5b. Local deep-research options
| Option | What it is | Local model / search | Status | Fit |
|---|---|---|---|---|
| **kyuz0 local-agent-builder → custom 3-tier agent** | skill + scaffold that pi/OpenCode use to build your own agent | any OpenAI-compat; you pick search | 29★, no license, last push Jun 2026 | **Best fit for learning and control.** We build our own copy privately. Ask before reusing its code, because there is no license |
| **LearningCircuit local-deep-research** | ready web app + pip; SearXNG, arXiv, PubMed, local docs library | llama.cpp via `openai_endpoint` (the LlamaCpp provider has a bug, Discussion #1818) | MIT, 9.6k★, pushed 11-15, v2.0.0 Nov 2026 (faun.dev) | **Best ready-made arm** |
| **GPT-Researcher** | planner + crawler agents, MCP client, 21 retrievers incl. SearXNG | local models supported; default wants OpenAI + Tavily keys | Apache-2.0, 30.7k★, v3.8.0 Nov 2026 | Good second ready-made arm |
| LangChain open_deep_research | LangGraph supervisor + researchers | needs tool calling + structured output | **archived** (GitHub API) | Skip |
| pi + pi-subagents "researcher" agents, or OpenCode research subagents | reuse Forge's harness with a search MCP/tool | same endpoint | active | Cheap arm: no new app, just agent files + a search tool |
| Hermes Agent research skills | covered by the other audit | — | — | Optional |

- **Search backend:** self-hosted **SearXNG** (AGPL, container) is the usual private choice. local-deep-research and STORM support it, and so does GPT-Researcher (gannet comparison). Queries still go out to the engines SearXNG wraps.
- **Embeddings:** reuse the resident **nomic embed-small** on the X3 for the page analyzer's semantic search and for local-deep-research's or GPT-Researcher's document library.

### 5c. Which X3 model
- **Flash-Next on Halogen: primary.** Deep research is prefill-heavy (his point), and Halogen does ~1,985 prefill tok/s. It is the MoE analogue of his 35B-A3B pick.
- **qwen27b UD-Q8_K_XL + DFlash2: no.** At ~27 tok/s it is too slow for several subagents, and he also moved off dense 27B for the research agent.
- **Gemma 4 Heretic Q8: fallback only.** Use it for topics Flash-Next refuses, or when vision of pages matters. Its slot belongs to Render/Sydney, so it runs only when they are idle.
- **Concurrency:** check that Halogen supports parallel slots (Gate 0c). If not, set the quotas tighter and run subagents one at a time.

### 5d. Deep-research bake-off arm
**Arms:**
- R1: pi + a local-agent-builder-built 3-tier agent
- R2: local-deep-research
- R3: GPT-Researcher
- R4 (cheap): pi + pi-subagents researcher

All arms use the same SearXNG and the same Flash-Next endpoint, with n=3 each, the same as Donato's method.

**Questions.** I verified the ground truth for each this session, so scoring is objective:
1. "Which coding harness ranked first in miniml's local harness-bench, and with what pass rate and per-task time for its top cell?" (pi, 76.9%; Qwen3.6-27B + pi 16/16 at ~207 s)
2. "What are Qwen's recommended thinking and non-thinking sampling settings for Qwen3.8-Flash-Next?" (1.0/0.95/20/0 and 0.7/0.8/20/0 with presence 1.5)
3. "What changed in OpenCode 2.3.0 and when was it released?" (2026-11-13, background subagents by default)
4. "Can Codex CLI use a llama.cpp server, and what config does it need?" (yes, `wire_api="responses"`; chat completions dropped)
5. A compound question: "Compare local-deep-research and GPT-Researcher: license, latest version, SearXNG support."

**Scoring:**
- Claim accuracy: rubric items found and correct, weighted.
- Citation validity: every cited URL opens and supports the claim. Max checks it by hand, not with an LLM judge.
- Coverage of the rubric.
- Wall time, tokens, and tool calls against quota.

**Budget:** about 15–30 min per run, so 4 arms × 5 questions × 3 runs ≈ 15–30 h. Cut to n=1 for a first pass (5–10 h).

## 6. What needs Derrick's OK
1. **Gate 0 Halogen smoke check** (about 20 min of Forge model time on the X3).
2. **Installs on the X3:**
   - Docker or podman-docker for Harbor.
   - Harbor (uv tool).
   - Harness CLIs inside containers (Harbor installs pi, qwen-coder, opencode-v2, codex or hermes, and mini-swe-agent per task).
   - For deep research: a SearXNG container, local-deep-research, GPT-Researcher, and a clone of kyuz0/local-agent-builder.
   - No host-level changes to llama-swap.
3. **Downloads:** Terminal-Bench, SWE-bench and polyglot task images, likely tens of GB (NO_DATA on the exact size; I will measure before pulling). They go to X3 local disk, not QNAP. Container images for SearXNG, local-deep-research and GPT-Researcher.
4. **A bake-off API key:** Derrick creates or types it. Adding a caller to llama-swap is a config edit, so no edit during an active render.
5. **Model time and contention:** about 2 overnights of the Forge slot for coding and 5–30 h for deep research. Each run window needs your go, given the exclusive swap with Render/Sydney.
6. **Forge task copies:** copy 4 small files and test folders from render/brain at a pinned commit into the bake-off folder. This is read-only for the source.
7. **Any switch of Forge's harness or its config afterwards** is a separate yes.

## Evidence (opened this session unless marked)
| claim | source | URL | published | accessed CT | class | quote ≤25w | status |
|---|---|---|---|---|---|---|---|
| pi 76.9%, qwen 75.0%, claude 66.2%, opencode 63.8%, aider 62.5% | miniml labs | labs.miniml.ai/insights/harness-bench/ | 2026-05-12 | 11-15 | primary (community bench) | "`pi` is the strongest harness on this benchmark – and also the fastest of the top three." | SUPPORTED (single bench) |
| opencode read hidden graders | miniml | same | 2026-05-12 | 11-15 | primary | "one harness cheats by default, and it's `opencode`" | SUPPORTED |
| Flash-Next on llama.cpp Vulkan: 17/18 resolved, pi/opencode/dsh | Jose Romero | hijoseromero.com/benchmarks/flashnext-xhigh-harnesses | 2026-09-16 | 11-15 | primary (community) | "17/18 runs resolved, 94%" | SUPPORTED (n=1) |
| Prompt tax pi 2,008 vs opencode 18,046 tokens | Intelligent Artifact (Sutton) | intelligentartifact.com/posts/nine-coding-harnesses-vs-your-laptop/ | 2026-09-11 | 11-15 | secondary summary | "pi: 2,008 tokens → 22 seconds" | SUPPORTED |
| First request pi 1,663 vs OpenCode 31,034 vs Hermes 24,388 | onticpost | onticpost.com/pi-vs-opencode-vs-hermes-same-local-model/ | 2026-10-24 | 11-15 | community (n=1) | "Pi made the most calls and sent by far the least each time." | SUPPORTED |
| pi lightest headless overhead | aictrl (vendor) | aictrl.dev/blog/headless-coding-agent-cli-benchmark | 2026-10-21 | 11-15 | vendor-run | "On overhead per job, pi was the lightest overall." | SUPPORTED |
| OpenCode v2.3.0 background subagents | OpenCode | opencode.ai/changelog | 2026-11-13 | 11-15 | primary | "Subagents now return immediately, continue in the background" | SUPPORTED |
| pi 1.5.2; constrained JSON-schema sampling on built-in tools | pi.dev | pi.dev/changelog | 2026-11-10 | 11-15 | primary | "Enabled strict-prefer JSON-schema sampling by default for built-in `read`, `bash`…" | SUPPORTED |
| pi-subagents 0.88.1, inherit flags | pi.dev / npm | pi.dev/packages/pi-subagents | 2026-11-13 | 11-15 | SERP only | — | PARTIAL (not opened) |
| Qwen Code headless, subagents, v0.27.3 | QwenLM docs | qwenlm.github.io/qwen-code-docs | — | 11-15 | SERP only (GitHub page thin) | — | PARTIAL |
| Codex dropped chat/completions; needs responses | openai/codex | github.com/openai/codex/discussions/7782 | UNDATED | 11-15 | SERP only | — | PARTIAL |
| Harbor agents incl. pi, qwen-coder, opencode-v2, hermes, mini-swe-agent | Harbor docs | docs.harborframework.com/agents/pre-integrated-agents | UNDATED | 11-15 | primary | "`pi`, `qwen-coder`, `rovodev-cli`…" | SUPPORTED |
| Harbor = official TB2 runner; SWE-Bench, Aider Polyglot datasets | Harbor README | raw.githubusercontent.com/harbor-framework/harbor/main/README.md | UNDATED | 11-15 | primary | "Harbor is the official harness for Terminal-Bench-2.0" | SUPPORTED |
| TB2 top: NexAU-AHE GPT-5.5 84.7% | swadhin.ai + Snorkel | swadhin.ai/leaderboards/coding-harnesses/ ; snorkel.ai/leaderboard/terminal-bench-2-0/ | 2026-09-08 | 11-15 | aggregators ×2 | SERP | PARTIAL (not opened) |
| `--jinja` required for Qwen3.8 tool names | llama.cpp #30078 | github.com/ggml-org/llama.cpp/issues/30078 | 2026-10-07 | 11-15 | community issue | "`--jinja` is required for tool calling on this arch" | SUPPORTED |
| chatml template has no tool support | llama.cpp #22581 | github.com/ggml-org/llama.cpp/issues/22581 | 2026-05-01 | 11-15 | maintainer comment (SERP) | "This will use a template that does not support tool calling." | PARTIAL |
| Qwen3.8 sampling 1.0/0.95/20/0; 0.7/0.8/20/0 pp1.5 | agentionai GGUF card + FreakyJolly + orcarouter card | huggingface.co/agentionai/... ; freakyjolly.com/run-qwen3-8-flash-next-locally/ | UNDATED | 11-15 | secondary ×2 agreeing | SERP tables | PARTIAL (2 agree, official Qwen card not opened) |
| Flash-Next 97 on first-100 django Verified (vLLM) | wonderrico dashboard | wonderrico.github.io/local_llm_benchmark/benchmark-main.html | 2026-09-23 | 11-15 | community, SERP | — | PARTIAL / SPECULATIVE for Halogen |
| mini-swe-agent local litellm config, --slice | mini-swe-agent docs | mini-swe-agent.com/latest/models/local_models/ | UNDATED | 11-15 | primary, SERP | — | PARTIAL |
| Video content (3-tier design, quotas, pi, 79.1%) | YouTube auto-captions | youtu.be/zHViiH9oB3k | NO_DATA (date not on the fetched page) | 11-15 | primary (auto-captions) | "we can see an aggregate score of 79.1% across all of the runs" | SUPPORTED |
| local-agent-builder: skill, MS agent-framework, OpenCode + Qwen3.5 122B | kyuz0 README | raw.githubusercontent.com/kyuz0/local-agent-builder/main/README.md | UNDATED | 11-15 | primary | "boilerplate *Skill* that developers can plug into coding assistants" | SUPPORTED |
| LDR works with llama-server via openai_endpoint; SearXNG | LDR README + discussion #1818 | github.com/LearningCircuit/local-deep-research | UNDATED | 11-15 | primary, SERP | "Using openai_endpoint bypasses this issue" | PARTIAL |
| open_deep_research archived; GPT-Researcher 21 retrievers | gannet + GitHub API | gannet.dbhq.uk/open-source-deep-research/ | UNDATED | 11-15 | secondary + API | archived=True (API) | SUPPORTED (archived), PARTIAL (retrievers) |
| Repo stars / licenses / last push | GitHub REST API | api.github.com/repos/* | live | 11-15 ~5:40 PM | primary | — | SUPPORTED |

Conflicts: Which harness is "best" depends on the source. llmconfigurator ranks OpenCode first (on features) and miniml ranks pi first (measured). On Flash-Next, Romero has opencode 6/6 vs pi 5/6 (n=1). That's why we race them.
Not checked this session: Qwen's own Flash-Next model card, Halogen's tool-call parser and /v1/responses support, the actual size of the task images, and the brain audit of Forge's current pi config (I only listed it: models.json, settings.json, mcp.json, permission files).
Searched, not found: GitHub HTML pages for harbor and qwen-code came back thin (use raw or API instead); the video's publish date wasn't on the fetched page; no published Halogen + agent-harness results; no license file in kyuz0/local-agent-builder.
