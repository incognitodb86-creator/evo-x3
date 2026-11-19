# RESEARCH 2026-10-21: Forge / agentic loops / local serving / ComfyUI ops on AlienPc vs community practice

Written 2026-10-21 ~16:30 CT by Grok Bot (research executor). This file is the only thing written. Nothing was loaded, rendered,
installed or changed. No model endpoint was called. Video-pipeline settings are covered by
`C:\AI\community\p7\AUDIT_2026-10-21_community_10eros.md` (today, 15:10 CT); that audit is referenced here and not repeated.

Derek's rules applied: use existing community tools first, build custom only when nothing fits (and say why), flag third-party
code that needs review, decide on raw benchmark wins. Claims I could not open this session are marked UNVERIFIED.

---

## 0. What I inspected on AlienPc (read-only)

| Item | Finding |
|---|---|
| `C:\AI\director\config\llama-swap.yaml` | llama-swap **v265 (d1e743f, built 2026-10-14)** at `C:\AI\llama-swap-trial\bin`. One `main` group, `swap: true, exclusive: true`, 7 members (3 Strata coders, 2 VLM judges, 2 ComfyUI). `cmdStop: taskkill /T /F /PID ${PID}` on all. `unloadTimeout` 15 s (LLMs) / 30 s (ComfyUI). ComfyUI `ttl: 0`, `compat.ignoreWebsockets: true`. |
| Forge backend | Not llama.cpp: the coder runs on **Strata 0.2.1.1** (`sy_strata_launch.py` → `strata-engine`) with `strata-swift15-iq3s-esp.json`: `--expert-cache auto --spec 4 --spec-min-p 0.5 --mtp --max-context 98304 --kv int8 --vision --control-vector-scaled ...experimental-speed-projection.gguf:1.0 --control-vector-layer-range 4 44 --cvec-mode project --pool-workers 13`. No `--vram-reserve-mib`. |
| Strata logs | Every coder config logs the engine's own low-VRAM warning, e.g. swift15-esp: `WARNING: only 128 MiB of VRAM free at the start of this request (below 1024 MiB)`; swift15 plain: `152 MiB ... LOW: requests may stall; add --vram-reserve-mib 1060`; iq3_xxs: suggests `1049`; huihui: `1023`. Decode in the last 12 requests of the ESP log: 85.5-104.4 tok/s, drafts accepted ~65-76 %. |
| llama-swap log | `stop signal failed: exit status 128` x43 in `llama-swap.out.log`; no `CUDA error` / `out of memory` lines. |
| pi | `@earendil-works/pi-coding-agent` **1.3.0**. settings (secret-looking keys filtered out, `auth.json` not read): packages `npm:pi-permission-system@0.8.0`; extensions `-builtin:llama.cpp`, `-builtin:mcp`, `headless-guard-and-truncate.ts`, `protected-paths.ts`; tools read/edit/write/bash/grep/find/ls; thinking high; compaction on; retry 2. Folders `pi-subagents`, `pi-hermes-memory`, `mcp-workflows` exist under `~\.pi\agent` but only pi-permission-system is in `packages` (not checked whether the others load). |
| Ralph | `ralph-community\ralph.ps1`: gpu_guard before every iteration, git checkpoints before/after, py_compile/json.tool on changed files, scope check + restore, harness-owned file hashing, 20-min timeout, no-progress stop, model may only *request* GPU work via `JOB_REQUEST.json`. TASKS.md = one task per iteration, top to bottom. |
| Bench | `C:\AI\bench\community\RESULTS.md` (chain-20261020-2022): Ralph replay 25/25 all arms; BFCL 41/42/44 of 52; Polyglot-python 6/6/7 of 12; HumanEval+ 22/22/21 of 24 (strata / swift / swift+ESP). The file's own rule recommended plain `coding_swift15_iq3s`; Derek chose Swift+ESP. |
| Judge | `p6_review.py` already does **swapped-order pairwise** with "disagreement across orders → split (0.5)" plus an absolute rubric at temperature 0, JSON response format. |
| GPU now | 852 / 16303 MiB used, 0 % util (idle at time of read). |
| Processes | Each director process appears twice (venv `python.exe` + `Python312\python.exe`). That matches how a Windows venv launcher re-spawns the base interpreter; probably not a duplicate run, but not proven here. |

---

## (a) Current state: what is already good

1. **Harness choice is right.** In the only multi-harness local-model study I found, pi was the top harness: 123/160 (76.9 %) vs qwen 75.0 %, claude 66.2 %, opencode 63.8 %, aider 62.5 %, and the fastest of the top three; it was also the only harness in the only 16/16 cell [HB]. opencode read or ran the hidden grader in 14 cells [HB]. There is no benchmark case for moving Forge off pi.
2. **GPU arbitration is fail-closed.** One exclusive llama-swap group, plus `forge.ps1` → `gpu_guard.ps1`, plus the Ralph rule that the model only requests GPU jobs, is stricter than the community examples I found [LS962].
3. **The Ralph harness already does most of what Huntley says matters:** a fresh process each loop, one task per loop, the same files every loop, git checkpoints, a stop file. What is missing is test/typecheck backpressure (item 5).
4. **The judge already de-biases position** the way the literature says to: run both orders, and a flip counts as a tie [PB].
5. **The bench decision rule is sound** (equal task counts, a per-benchmark tolerance, an agentic gate). Its weakness is n (item 3), not its design.
6. **The video settings match the template and the author** on 25 of 31 rows (today's audit). Not repeated here.
7. **Speed is healthy right now:** 86-104 tok/s decode, 65-76 % draft acceptance, ~90 %+ prompt reuse in the logged requests.

---

## (b) Top 10 improvements, ranked by expected impact ÷ effort

| # | What | Impact | Effort | Risk | Community vs custom |
|---|---|---|---|---|---|
| 1 | Add `--vram-reserve-mib ~1100` to the Strata coder configs | High (removes a documented 7x stall mode) | 10 min + 1 A/B | Low | Engine's own flag |
| 2 | Decide ESP with data: per-request off switch via a llama-swap `setParamsByID` alias, no extra model | High (correctness of the default) | 30 min + bench | Low | Engine feature + llama-swap feature |
| 3 | Raise bench resolution (more tasks, ≥3 seeds, paired per-task) and use the official harnesses where possible | High (every later decision depends on it) | Medium (GPU hours) | Low | Community harnesses |
| 4 | Move "never swap out a render" into llama-swap: ComfyUI `cmdStop` that waits for the queue, then `/api/free`, then kills | Med-High | Medium | Medium | Community pattern; small PowerShell port |
| 5 | Ralph backpressure: harness-run pytest + ruff + a type checker as a gate each iteration; specs + plan file | Med-High (self-correction) | Small-Med | Low | Huntley playbook; tiny harness edit |
| 6 | Fresh-context reviewer loop via `pi-subagents` (worker → reviewer → worker) | Medium | Small | Medium (third-party) | Community package |
| 7 | Bench two candidate coders: Strata's own **Coder** pack and **Qwen3-Coder-Next** | Medium (possible upgrade) | Medium | Low (bench only) | Community models |
| 8 | Judge upgrade: checklist-trained FIRM-Video-8B as the absolute scorer, plus repeat sampling | Medium | Medium | Medium (content refusals, GGUF) | Community model |
| 9 | Sandbox pi's bash on Windows with `pi-landstrip` (AppContainer, no network by default) | Medium (defense in depth) | Medium | Medium (third-party, Git Bash quirks) | Community package |
| 10 | ComfyUI env + workflow versioning with `comfy node save-snapshot` / Manager snapshots next to the API JSONs in git | Low-Med | Small | Low | Community tool |

### 1. Strata `--vram-reserve-mib` (fixes the "128-266 MB free" pain point)
- **What:** add `"--vram-reserve-mib", "1100"` to `"args"` in `strata-swift15-iq3s-esp.json`, `strata-swift15-iq3s.json` and `strata-iq3_s.json` (the rollback). The engine's own suggestions in the local logs range from 1023 to 1060 MiB. Also consider NVIDIA Control Panel → CUDA Sysmem Fallback Policy = *Prefer No Sysmem Fallback* for the strata-engine executable, so an over-sized cache fails instead of paging.
- **Why it matters / evidence:** Strata docs: under WDDM an over-committed cache "pages instead of failing ... the start looks normal ... and only the speed collapses". Measured on a 4080S: 0 MiB free = 13.7/14.7 tok/s; `auto` at 217 MiB free = 102/122 tok/s; `auto` + reserve 1500 = 89-101 tok/s. A 16 GB 5080 fell from 40.9 to 16.6 tok/s when the reserve went from 770 to 0 [STR-VRAM]. The docs say below ~1 GiB on Windows "decode fell from 91 to 3 tok/s at 70K tokens and then a window never finished" and "the fix is a larger `--vram-reserve-mib`" [STR-VRAM]. Your free figure is 128-272 MiB, and pi runs at 44-63K tokens of context (local log), which is the regime where that stall was reported. Today's decode is fine, so this is insurance against the stall, plus a likely cure for any unexplained slow or stuck Ralph iterations.
- **Cost:** a few hundred expert-cache slots. The 4080S table suggests a single-digit-% decode loss; that is *their* card, so measure yours: 5 interleaved pairs, same prompts, and read the `tok/s` lines.
- **Effort:** a JSON edit (BOM-less), applied between iterations, never while ComfyUI renders. **Risk:** low; rollback = remove the arg.
- **Custom vs community:** an engine flag. Nothing custom.

### 2. ESP on Swift: the docs contradict the name, so decide it with data
- **What the Strata docs say about ESP** [STR-ESP]: it is "**EXPERIMENTAL**". The vector's package describes it as "a **refusal-direction projection**". It is "not an optimization in the engine: on the same text it costs 0.2-0.4% per token". On code it gives "perplexity +15%", and the top-1 token changes at 10 % of positions. Setup offers it "Only for the original Qwen3.8-Flash-Next, **not Swift 1.5**". The default config runs it on Swift 1.5.
- **What the local bench says:** Swift+ESP vs plain Swift: BFCL +2 tasks, Polyglot +1 task, HumanEval+ −1 task. Its faster wall time comes with *fewer* completion tokens on Polyglot (150.6K vs 172.0K) and *more* on HumanEval+ and Ralph. That is output-length variance, which the docs predict ("depends on the text the model writes"). Every delta is ≤ 1-2 tasks at temp 1.0, so by Derek's own raw-wins rule **no arm has won yet**. The RESULTS.md rule picked plain Swift.
- **Community way to test it cheaply:** Strata accepts `"experimental_speed_projection": false` per request, and with it off "the output is token-for-token the stock model's" [STR-ESP]. llama-swap's `filters.setParamsByID` "combine[s] with aliases to create variant behaviour without reloading the model" [LS-CFG]. So one loaded engine can serve two IDs, e.g. `coding_swift15_iq3s_esp` (ESP on) and `coding_swift15_iq3s_esp:stock` (ESP off). That gives a true paired A/B with no model swap, and the ESP side stays available for `prompt_writer.py`, where fewer refusals on adult prompts is the actual point.
  - Caveats: switching drops the conversation cache once per switch [STR-ESP], so don't interleave on a single conversation. setParamsByID is in llama-swap main today; **UNVERIFIED that v265 (2026-10-14) has it**. Check the release notes, or validate the YAML before relying on `-watch-config`.
- **Recommendation:** run item 3's bigger bench on `:stock` vs ESP. Until ESP wins, Forge's coding default should follow the rule (plain Swift, or ESP-off via the alias). Derek decides.
- **Effort:** small. **Risk:** low. **Custom:** none.

### 3. Bench resolution: the current n cannot separate the arms
- **Problem:** RESULTS.md says it: "one task is worth ... Aider Polyglot python 8.3 pts, HumanEval+ 4.2 pts" and "A 2-point tolerance is below one-task resolution". Polyglot is 12 Python tasks under a whole-file re-implementation, not the official runner.
- **Community practice:** the 225-task Aider Polyglot snapshot found the second attempt is worth +21.8 to +38.2 points, and it warns that results "cannot isolate model quality from serving configuration" unless the build, templates and seeds are frozen. It recommends repeated seeds [AP]. harness-bench runs each (model, harness, task) cell sandboxed, with hidden graders the agent cannot see, and notes that single-cell conclusions are "shaky" [HB].
- **Do:** (a) the full Polyglot **Python track (34 tasks)** at minimum, with the official aider benchmark runner under WSL2 + Docker if you want all 6 languages (225) (UNVERIFIED on this box); (b) ≥3 seeds per arm, and report per-task paired wins/losses, not only %; (c) freeze the engine build, config hash and template per run; (d) keep the Ralph replay as the agentic gate, but grow it past 5 tasks (25/25 for every arm means it no longer discriminates).
- **Effort:** medium (GPU time; schedule when no renders run). **Risk:** low. **Custom:** the existing bench scripts stay. The official runner replaces the whole-file re-implementation.

### 4. Put the render-protection rule in llama-swap itself
- **What:** today the rule "never load an LLM while ComfyUI renders" lives in every caller (forge.ps1, ralph.ps1, director). Any caller that skips the guard (a bench, a Discord-bridge request, a curl) makes llama-swap kill ComfyUI mid-render after its 30 s `unloadTimeout`. The community pattern makes ComfyUI's `cmdStop` (1) poll `/prompt` until `queue_remaining == 0`, (2) POST `/api/free` with `unload_models` and `free_memory`, (3) wait until `/system_stats` shows ~90 %+ VRAM free, (4) then kill. `unloadTimeout` is raised to cover a render (the example uses 180 s; yours would need ≥ the longest segment, ~15-30 min) [LS962].
- **Why:** llama-swap only force-kills after `unloadTimeout` ("We wait up to gracefulTimeout for the process to exit on its own. If still alive ... kill the process ... tree", llama-swap `process_command.go`), so a waiting cmdStop protects the render at the proxy. The maintainer also suggests a wrapper process (like `cmd/vllm-wrapper`) as "more effective" [LS962].
- **Windows port:** the example is `sh`. It needs a PowerShell one-liner or a `.ps1` (custom, ~30 lines, because no Windows version exists). Note that llama-swap does not pipe cmdStop stdout to its log ("stdout/stderr are not hooked up", maintainer, Jul 2026 [LS962]), so log to a file.
- **Pair with Strata's own gates** [STR-VRAM]: `"min_free_vram_mib"` makes Strata answer **503** "the GPU is in use by another program" instead of starting into a full card, and `"before_load"` runs a command (e.g. ComfyUI `/api/free`) before a reload. Neither needs custom code.
- **Effort:** medium. **Risk:** medium. An LLM request now *waits* behind a render (desired), and pi's `httpIdleTimeoutMs` 600 s / provider timeout 1200 s must exceed that wait or pi errors. Test with a short dummy render first. Keep gpu_guard as the second layer.

### 5. Ralph: add test/type backpressure as a harness gate, plus a spec/plan file
- **Evidence:** Huntley: "Anything can be wired in as back pressure to reject invalid code generation", "the wheel has got to turn fast", and for dynamic languages "I must stress the importance of wiring in a static analyser/type checker ... such as pyrefly". Without one, "you will run into a bonfire of outcomes" [RALPH]. His playbook: "Every loop's context is allocated with the same files ... (PROMPT.md + AGENTS.md)"; "`AGENTS.md` specifies actual commands to make backpressure project-specific"; LLM-as-judge for subjective criteria "with binary pass/fail" [RALPH-HOW] (opened via search result text only; the raw GitHub fetch returned empty).
- **Gap here:** ralph.ps1 gates only `py_compile` and `json.tool`. `C:\AI\director` already has `.ruff_cache`, `.mypy_cache`, `.pytest_cache` and `tests\`, so the tools exist.
- **Do:** after each iteration the *harness* (not the model) runs `ruff check` + `pytest -x -q <tests for changed modules>` + `mypy` (or pyrefly) on changed files. Fail → the iteration is "fail", the output goes into the next iteration's prompt (`notes\last_failure.md`), and two fails in a row trips the existing stop rule. This is the "self-correct and keep going until done" behaviour Derek wants, with the evidence created outside the model.
- **Effort:** small-medium (an edit to the existing harness). **Risk:** low. Test runtime must stay short ("speed of the wheel"). **Custom vs community:** the method is Huntley's; the code is a few lines in your harness. There is no reason to adopt a third-party Ralph runner, because yours already has stricter scope guards than any I saw.

### 6. Fresh-context reviewer via `pi-subagents`
- **What:** `pi install npm:pi-subagents` (v0.80.0, MIT, 573K downloads/mo, needs pi ≥ 1.2.0; you have 1.3.0). Built-in `scout`, `worker`, `reviewer`, `oracle`. The recommended loop is "clarify → scout → worker → fresh reviewers → worker"; there are `/review-loop` and "Run a review loop ... max of 3 rounds" prompts and an opt-in "Watchdog" adversarial change reviewer [PSA].
- **Why:** a reviewer with a clean context catches what the worker's long context misses, and it is a community package rather than more harness code.
- **Evidence:** NO_DATA for a local-model benchmark of review loops. Treat it as a hypothesis: A/B it on the Ralph replay (with more than 5 tasks, see #3) for pass rate, tokens and wall time.
- **Risk / review flag:** **third-party code, which runs inside pi. Review the source before installing.** It is 6.5 MB with 5 deps + 5 peers [PSA]. Pi's own docs: "Packages can execute extension code ... Review third-party package source before installing it" [PI-PKG]. On one 16 GB GPU the children run sequentially on the same model, so time per task goes up. Check it does not conflict with `headless-guard-and-truncate.ts` / `protected-paths.ts` (child sessions must load the same guards; UNVERIFIED). A `pi-subagents` folder already exists under `~\.pi\agent`: check what is installed before adding anything.

### 7. Candidate coder models worth one bench run (no switch without wins)
- **Strata Coder pack** (ISTA-DASLab Qwen3.8-Flash-Next-GSQ-RCO-Coder, IQ1_M; keeps 256 of 512 experts): the authors claim "91% of the full model's SWE-bench Verified score, 99% of LiveCodeBench". It reads prompts the fastest of the Strata sizes, but decodes ~55 tok/s short / 43 at 128K in Strata's own table, vs IQ3_S 53 / 46 on the same box. It is weaker outside code and non-English [STR-MODELS]. Same engine, same llama-swap pattern: low effort.
- **Qwen3-Coder-Next UD-IQ3_XXS** (llama.cpp): 145/225 (64.4 %) Pass@2 on the *full* Polyglot in one uncontrolled local run [AP]. It would need llama.cpp with MoE CPU offload on 16 GB + 64 GB RAM. Speed on AlienPc is UNVERIFIED, and it is likely well below Strata's 86-104 tok/s.
- **Not candidates for this box:** 27-31B dense models (Qwen3.6-27B, gemma-4-31b) top harness-bench [HB], but they were measured on a 128 GB M3 Max; on 16 GB they need ≤ Q3 or offload. A SharedTutor listicle claims "Devstral Small 2 24B ... 68.0% SWE-bench Verified" at ~15 GB [AGG, UNVERIFIED, aggregator].
- **Effort:** medium. **Risk:** low (bench only). **Community.**

### 8. Video judge: better absolute scorer + repeat sampling (extends audit "harness pieces" row on p6_review)
- **Evidence:** FIRM-Video (Aug 2026): a checklist "check-before-score" reward model. FIRM-Video-8B (Qwen3-VL-8B base) cut overall MAE vs human from **1.33 to 0.78** (base Qwen3-VL-8B 1.33, Qwen3-VL-235B 1.27, GPT-5 1.08). Best-of-8 on VBench beat VideoScore2 and base Qwen3-VL-8B on all three generators [FIRM]. Weights: `VisionXLab/FIRM-Video-8B-Qwen3VL` on HF [FIRM-HF]. It scores 8 uniformly sampled frames per video and uses three fixed prompts (IF / WC / PQ) that return JSON `{reasoning, score}` [FIRM]. That maps directly onto p6_review's absolute rubric.
- **Position-bias research:** position bias "is not due to random chance" and is "strongly affected by the quality gap between solutions". Close pairs are where flips happen, and an 8B judge (Llama-3.1-8B) showed low repetition stability (0.75-0.79) [PB]. So: (a) keep the swap-and-tie rule; (b) for close pairs, run k=3 repeats at temp > 0 per order, or don't let the pairwise term decide a promotion when the orders disagree; (c) majority vote across `qwen3vl_judge` and `vl_judge` (both already configured). The paper's "majority voting ... useful for over 95%" result was for *capable* judges [PB], so for 8-9B judges it is a hypothesis.
- **Risks:** FIRM-Video-8B is **not abliterated**, and its refusal behaviour on adult content is UNVERIFIED (the current judge is abliterated for that reason). A GGUF + mmproj for llama-server is UNVERIFIED (you may need to convert it). It was trained on 1-6 s clips (median 3.3 s), not 20 s segments. Validate on ~20 already-ranked P6/P7 clips against Derek's own picks before swapping.
- **Effort:** medium. **Custom:** p6_review stays (no community equivalent found, per the audit); only the model and prompts change.

### 9. OS-level sandbox for pi's bash on Windows: `pi-landstrip`
- **What:** a pi extension that wraps every `bash` call (AI and `!` commands) in an AppContainer. On Windows: "Pi's Git Bash/MSYS shell cannot run under LPAC", so it uses standard AppContainer. With `windows.allowLoopback: false` (the default) the worker "has no network". Writes are limited to the project [LAND].
- **Why for you:** no loopback means a bash command cannot reach `127.0.0.1:8080`. That would be an OS-level guarantee behind "the model never starts GPU work", instead of only path guards + git restore. Pi's official isolation guide lists Docker / Docker Sandboxes / OpenShell / Gondolin (Linux micro-VM) for whole-process isolation [PI-ISO]. On native Windows, pi-landstrip is the option I found that keeps pi on the host.
- **Risks / review flag:** **third-party native binaries** (`@landstrip/landstrip`, Apache-2.0 AND LGPL-2.1+). Review before install. "Pi's filesystem tools and plugin callbacks remain trusted code outside the Landstrip sandbox", so read/edit/write are not sandboxed and your protected-paths extension stays necessary [LAND]. Ralph commands that need loopback (none should) would break. Python venvs and PowerShell called from Git Bash under AppContainer are UNVERIFIED. Try it on the bench workdir first.
- **Effort:** medium. **Custom:** none.

### 10. ComfyUI environment + workflow versioning
- **What:** before any node update or ComfyUI bump, run `comfy node save-snapshot --output <file>.json` (comfy-cli) or ComfyUI-Manager's `POST /snapshot/save`; restore with `comfy node restore-snapshot <file>` [CCLI]. Commit the snapshot plus the API-format workflow JSONs (`runs\*.api.json`, templates) to the existing `C:\AI\community` git repo. `comfy node deps-in-workflow --workflow X --output Y` lists a workflow's node dependencies [CCLI].
- **Why:** 46 custom node packs are installed, the GPU-specific crash workarounds depend on exact versions (audit rows 25-26: issues 15337 / 15665), and the audit recommends exporting templates as the API base.
- **Effort:** small. **Risk:** low (save is read-only; restore is a deliberate step). **Review flag:** `comfy-cli` is a pip install into a venv (Comfy-Org, first-party). Install it in its own venv, not ComfyUI's.

---

## (c) Quick wins for tonight (no GPU, no touching running jobs)

All of these are file edits or reading. Each takes effect at the next model load, so apply them **between** Ralph iterations or while no LLM is loaded, and never while ComfyUI renders.

1. **Add `--vram-reserve-mib 1100`** to the three Strata coder JSONs (backup `.bak-20261021-reserve`, BOM-less, validate with `check_jsonc.mjs`). Benchmark tomorrow against tonight's `tok/s` log lines (item 1).
2. **Silence the benign llama-swap warning (optional, cosmetic).** `exit status 128` from `taskkill` means "There is no running instance of the task": part of the tree was already gone. Buildbot treats 128 as success for exactly this case [TK]. llama-swap logs it as a warning and still waits for exit, then force-kills the tree after `unloadTimeout` (source: `internal/process/process_command.go`, `runtime_windows.go`). On Windows its *default* `cmdStop` is already `taskkill /f /t /pid ${PID}` (`model_config.go`), so the explicit lines add nothing. To mute it: `cmdStop: 'cmd /c "taskkill /T /F /PID ${PID} >nul 2>&1 & exit /b 0"'`. This does **not** fix low free VRAM; item 1 does.
3. **Remove `--lowvram` from the ComfyUI cmd lines** for clarity (audit row 24: a no-op with DynamicVRAM). Keep `--disable-async-offload --disable-pinned-memory`.
4. **Write a `comfy node save-snapshot`** (or copy ComfyUI-Manager's latest snapshot under `user\__manager\snapshots` if present) into git (item 10). Read-only for ComfyUI.
5. **Draft the bigger bench plan** (item 3) and the ESP alias YAML (item 2) as files. Don't apply them until llama-swap v265's support for `setParamsByID` is confirmed.
6. **Review the pi-subagents and pi-landstrip sources** (read only, `npm pack` into a scratch folder) so an install decision can be made tomorrow.
7. **Mark the fleet skill `ltx-comfy-pipeline` superseded for H3 work** (from today's audit).

---

## (d) Not worth doing (now)

| Idea | Why not |
|---|---|
| Switch Forge from pi to OpenCode / Aider / Claude-Code-with-local / Goose / Codex CLI | pi led the only local multi-harness study (76.9 % vs 62.5-75 %) and opencode peeked at hidden graders [HB]. A switch would also throw away your guards. No local Goose / Codex-CLI / OpenHands result found (NO_DATA). |
| Move the coder to llama.cpp / ik_llama.cpp / vLLM / ExLlamaV3 / LM Studio | Strata is purpose-built for this 125B-A6B MoE on 12-16 GB + 64 GB RAM: VRAM expert cache + CPU experts + MTP verify [STR-PAPER]. Your 86-104 tok/s at 44-63K context already beats the numbers Strata publishes for IQ3_S on other cards. No benchmark found showing another engine wins for this model. vLLM on Windows needs WSL2, which pins only ~1 GB, so Strata's KV streaming is off there [STR-VRAM]. |
| Share the GPU between LLM and ComfyUI concurrently | 16 GB is already over-committed by each side alone (H3 UNET 20.7 GB staged; Strata fills VRAM by design). Keep the exclusive swap. Strata's `vram_elastic` shrink (#533) exists, but it was measured on a 12 GB card with Q2_0 and makes decode slower [STR-VRAM]. Not worth it next to a 20 GB video model. |
| A bigger VLM judge (Qwen3-VL-32B / 30B-A3B) | Doesn't fit next to anything at Q8 on 16 GB, and on FIRM-Video-Bench Qwen3-VL-30B-A3B (MAE 1.40) and 235B (1.27) were no better than the 8B (1.33). The fine-tuned 8B was best (0.78) [FIRM]. |
| More MCP servers in Ralph (filesystem / git / search / playwright) | Ralph runs `--no-mcp` with pi's native read/edit/bash/grep, and each tool schema costs context on a local model. Add one only when a task needs it (a SearXNG MCP for research tasks, UNVERIFIED). |
| KV-cache / flash-attention / slot tuning on the llama.cpp VLM judges | They already run `-fa on -ctk q8_0 -ctv q8_0 -np 1`, the same flags the harness-bench recipes use [HB]. Nothing left to gain. |
| Rebuilding pieces that have community equivalents | See the audit's harness table (Extender, Prompt-Check node, official templates). Adopt those; don't write new ones. |
| Third-party "Ralph runner" packages | Yours is stricter (scope restore, harness-owned file hashing, GPU job broker). Copy Huntley's *method* (#5), not someone's script. |

---

## Sources (opened this session unless marked)

| Tag | Source | URL | Published | Status |
|---|---|---|---|---|
| HB | Minervini, "[WIP] Benchmarking Local LLMs Against Coding Agent Harnesses" | https://neuralnoise.com/2026/harness-bench-wip/ | 2026-04-28 | opened. WIP, single machine (M3 Max 128 GB), private tasks |
| AP | Kovalov, "Eight Quantized Local Models on Aider Polyglot" | https://sergeykovalov.com/local-models-aider-polyglot-benchmark/ | 2026-07-27 | opened. Uncontrolled, one run per model |
| STR-VRAM / STR-ESP | Strata `docs/DETAILS.md` ("Sharing the GPU", "expert cache size is a budget", "Experimental speed projection") | https://raw.githubusercontent.com/Niko1221/Strata/master/docs/DETAILS.md | living doc, read 2026-10-21 | opened (primary, maintainer) |
| STR-MODELS | Strata `docs/MODELS.md` | https://raw.githubusercontent.com/Niko1221/Strata/master/docs/MODELS.md | living doc | opened |
| STR-PAPER | Strata paper "Running a 125-Billion-Parameter Model on a Normal PC" | https://raw.githubusercontent.com/Niko1221/Strata/master/docs/paper/Strata-Paper.pdf | 2026-09 | search excerpt only (PDF not opened) |
| STR-1902 | Strata issue #1902 (Swift 1.5 IQ3_S support; runs on 5070 Ti 16 GB) | https://github.com/Niko1221/Strata/issues/1902 | 2026-10-11/15 | search excerpt only |
| LS-CFG | llama-swap `docs/config.example.yaml` + source (`process_command.go`, `runtime_windows.go`, `model_config.go`), main @ c31d416 2026-10-21 | https://github.com/mostlygeek/llama-swap | 2026-10-21 | cloned + read |
| LS962 | llama-swap discussion #962 "Comfyui single gpu model switch" (incl. maintainer replies) | https://github.com/mostlygeek/llama-swap/discussions/962 | 2026-07-28..31 | opened |
| TK | buildbot issue #6140 (taskkill exit 128 = no running instance) | https://github.com/buildbot/buildbot/issues/6140 | 2021-07-16 | opened via search result text |
| RALPH | Huntley, "Ralph Wiggum as a 'software engineer'" | https://ghuntley.com/ralph/ | UNDATED on page | search result text (primary author) |
| RALPH-HOW | ghuntley/how-to-ralph-wiggum README | https://github.com/ghuntley/how-to-ralph-wiggum | UNDATED | search result text only; direct fetch returned empty |
| PI-PKG | Pi docs: Packages | https://pi.dev/docs/latest/packages | living doc | search result text (primary) |
| PI-ISO | Pi docs: Run Pi in an isolated environment | https://pi.dev/docs/latest/containerization | living doc | opened |
| PSA | pi-subagents package page (v0.80.0, 2026-10-21) | https://pi.dev/packages/pi-subagents | 2026-10-21 | opened |
| LAND | pi-landstrip README (v0.17.35) | https://cdn.jsdelivr.net/npm/pi-landstrip@0.17.35/README.md | UNDATED | opened |
| PB | Shi et al., "Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge" | https://arxiv.org/abs/2406.07791 | v9 (2024→) | opened |
| FIRM | Zhang et al., "FIRM-Video: Check Before You Score" | https://arxiv.org/html/2608.21839 | 2026-08-22 | opened |
| FIRM-HF | VisionXLab FIRM-Reward collection (FIRM-Video-8B-Qwen3VL) | https://huggingface.co/collections/VisionXLab/firm-reward | updated 2026-08-24 | opened |
| CCLI | Comfy CLI command reference | https://docs.comfy.org/comfy-cli/reference | living doc | opened |
| AGG | SharedTutor "Best Local AI Model for Coding with 16GB VRAM" | https://sharedtutor.com/2026/10/06/best-local-ai-model-for-coding-16gb-vram/ | 2026-10-06 | search excerpt only. AGGREGATOR, unverified numbers |
| AUDIT | Today's video audit | C:\AI\community\p7\AUDIT_2026-10-21_community_10eros.md | 2026-10-21 | read locally |

**Searched, not found / dead ends:** a llama-swap-specific fix for "stop signal failed" on Windows (none; it is taskkill's exit code). The VideoScore2 GitHub page rendered empty via fetch. The how-to-ralph-wiggum raw fetch was empty. No local-model benchmark for Goose, Codex CLI or OpenHands. No benchmark of review-subagent loops on local models. Reddit was not used.

**Open questions to verify next:** (1) does llama-swap v265 support `filters.setParamsByID`; (2) the decode cost of `--vram-reserve-mib 1100` on this card; (3) FIRM-Video-8B refusals on adult clips + GGUF availability; (4) whether pi-landstrip AppContainer breaks the venv/PowerShell calls Ralph tasks make; (5) whether the `pi-subagents` / `pi-hermes-memory` folders under `~\.pi\agent` are installed packages or leftovers.
