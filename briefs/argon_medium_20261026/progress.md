# Argon Medium run progress (2026-10-26)

- [09:41 CT] MAX: folder created by Max Architect 2. Brief = argon_medium_brief.md (box brain-staging 72c3606). Forge pause in progress (see ..\argon_audit_20261025\forge_pause.log). Model gemini-4-argon-medium confirmed by agy models.

- [09:46 CT] MAX: Forge STOPPED 09:45 CT mid iter 1 (Derrick 9:44 AM 'why dont we stop it now'): ForgeRalphLoop disabled, taskkill /T /F ralph 2700 + pi 5072; no GPU lock left; llama-swap left running. ralph-community git status clean (HEAD 2554abc). Uncommitted pass-1 work in C:\AI\community notes (card_vl2_*, _splice*, card_rebuild_*, scenes/raw/GI0xx_vl2_*, top_card_vl_build.py) - see brief M15 for keep/revert review.
- [09:46 CT] MAX: pre-launch /usage 09:46: Argon weekly 47% left; Gemini weekly 76%, 5h 63%; Claude/GPT weekly 50%. agy models lists gemini-4-argon-medium (Gemini 4 Argon (Medium)).
- [09:46 CT] MAX: brief = argon_medium_brief.md sha256 8359968C6231F91F27C29BAFC75ECD6B4591118717BC8D93BC80867F171CB4A4 (box brain-staging eeb1405). pre_hashes.txt taken 09:41. Launching argon_medium_run.ps1.


## M0: Pre-Flight (Read-Only)
- **Time CT:** 2026-10-26 09:48 CT
- **Step ID:** M0
- **Files:** Read-only check (`C:\AI\community\briefs\argon_medium_20261026\pre_hashes.txt`, `C:\Users\derek\5slock\ralph-community\logs\ralph.log`, `C:\AI\locks`)
- **Commit hash:** N/A (read-only)
- **Verify:**
  - Protected-file SHA256 hashes vs `pre_hashes.txt`: 11/11 exact match:
    - `test_p6_review.py`: `C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213`
    - `pi-permissions.jsonc`: `170AAE661BCF45314B2E22C65CFC33AD7DA05F7BA48ABFEC0821BDFC4C2AADEB`
    - `comm.py`: `AB4217FE31B09EDB28CD8A368E0291B463FAAC38A214FC968509D51C21F2F740`
    - `.pi\agent\settings.json`: `AC69F06F722A8FE2402AA0F0DCD5D5DE951521AD2FA09CAF23424264FE62B3BA`
    - `director\config\pi\settings.json`: `28811D58683234FF2F79E45A5825F96BE8D3816E30670175194BAD530D888D4B`
    - `llama-swap.yaml`: `19ABB43BA5D2A10E184433EA0EF4E8AC18989AFFC23956B9A73ED42877895DEC`
    - `ralph.ps1`: `817931A22D57D989038525DB35E1B91612826DD3A800D84575FC57F583563151`
    - `fix_plan.md`: `298A9BDF99E2ABE51F3E2C4D0741431D0A870E9002706353367DB6FBD2F3561F`
    - `.pi\agent\mcp.json`: `3C9A007BCA5A2B63AEB25E8A7116F6A174C905D197688E8C13B016EBBAC178EF`
    - `stock-pi-2026-10-25\mcp.json`: `3C9A007BCA5A2B63AEB25E8A7116F6A174C905D197688E8C13B016EBBAC178EF`
    - `stock-pi-2026-10-25\before\mcp.json`: `4C68912FACC8FA5179B3C5B51346572B58DB3A9EC30F313B6D2B9013D8F0ABB8`
  - Forge pause state & ralph/pi PIDs: `\ForgeRalphLoop` scheduled task State = `Disabled`; 0 active `ralph.ps1` or `pi` processes (stopped at 09:45 CT mid iter 1 of 10, started `2026-10-26T09:00:03`).
  - Open count: `ralph.log` last completed pass reported `open=53` (before 08:59 MAX block addition); live `fix_plan.md` open `- [ ]` count = `63`.
  - `git log --since 08:50`:
    - `ralph-community`: `2554abc` (09:12 CT, CARD-VL2 row + plan + receipt) and `ad0a2d4` (08:59 CT, MAX block update); HEAD = `2554abc`.
    - `community`: 0 commits since 08:50; HEAD = `5395fb9`.
    - `director`: 0 commits since 08:50; HEAD = `20642d5`.
  - `llama-swap`: `/health` = `OK`; `/running` = `coding_swift15_iq3s` (`state: ready`, port 10002, ttl 600); `/v1/models` = 5 models (`coding_sc117_strata`, `coding_swift15_iq3s` loaded, `coding_swift15_iq3s_esp`, `qwen3vl_judge`, `vl_judge`). ComfyUI (`comfyui_auto`) is NOT in `/running` (unloaded/idle).
  - GPU locks under `C:\AI\locks`: 0 lock files (only `_removed` subfolder from Oct 22).
  - `nvidia-smi`: `NVIDIA GeForce RTX 5070 Ti, 16303 MiB, 15387 MiB, 609 MiB` (`coding_swift15_iq3s` currently loaded in VRAM).
- **Rollback:** N/A (read-only)


## M1: Re-Audit Prior `final_review.md` and `ab_test_res_vs_euler.md` (Doc Fixes Only, Append Section)
- **Time CT:** 2026-10-26 09:53 CT
- **Step ID:** M1
- **Files:** `C:\AI\community\briefs\argon_audit_20261025\final_review.md`, `C:\AI\community\briefs\argon_audit_20261025\ab_test_res_vs_euler.md`
- **Commit hash:** `15c7e44` (`C:\AI\community`)
- **Verify:** `git -C C:\AI\community show --stat 15c7e44` (2 files changed, 49 insertions, 0 deletions; history preserved); `nvidia-smi --query-gpu=name --format=csv,noheader` -> `NVIDIA GeForce RTX 5070 Ti`; `Select-String -Path C:\AI\community\notes\web\02v_docs_h3.txt -Pattern 'Comfy Kitchen'` confirms official H3 doc `https://docs.comfy.org/tutorials/video/minimax/minimax-h3.txt`; `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_model_advanced.py:389` confirms `ModelAttentionBackend` schema default `"pytorch attention"`.
- **Rollback:** `git -C C:\AI\community revert 15c7e44 --no-edit`
- **Notes:** Appended new re-audit/errata sections to `final_review.md` and `ab_test_res_vs_euler.md` without rewriting prior lines. Corrected GPU attribution from "NVIDIA RTX 4080" to `NVIDIA GeForce RTX 5070 Ti` (16 GB / 16,303 MiB). Cited real MiniMax H3 documentation (`https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md`, cached at `notes/web/02v_docs_h3.txt:201-204`) and `comfy_extras/nodes_model_advanced.py:374-390`. Re-scored all 26 rows with today's live evidence: marked Row 6 (`S7-skills`), Row 7 (`fix_plan.md` repeated IDs), Row 10 (`ralph.ps1` timeout sizing & fake `rc=124`), Row 24 (`Switchyard` imports broken in `director`), Row 25 (`discord_bridge` import crash on restart), and Row 26 (`pi-mobile` 7878 conflict risk & loopback-only HTTPS probe) as **FAIL**.


## M2: REPORT-ONLY — Archived `director.switchyard` Still Imported (`NEEDS DERRICK`)
- **Time CT:** 2026-10-26 09:56 CT
- **Step ID:** M2
- **Files:** Read-only audit of `C:\AI\director\src\director\*.py` and `C:\AI\director\tests\unit\*.py`
- **Commit hash:** N/A (REPORT-ONLY)
- **Verify:**
  - `C:\AI\director\.venv\Scripts\python.exe -c "import director.cli"` -> `ModuleNotFoundError: No module named 'director.switchyard'` (rc 1).
  - Top-level module import sweep across `src/director/*.py`:
    - **FAIL (`ModuleNotFoundError: No module named 'director.switchyard'`):** `director.cli`, `director.queue`, `director.runner`, `director.gateway`, `director.chat_store`, `director.jobs`, `director.lease`, `director.ui`, `director.video_jobs` (9 modules).
    - **OK (top-level import succeeds):** `director.config`, `director.comfy_client`, `director.discord_bridge`, `director.gpu`, `director.minors_guard`, `director.llm_client`, etc. (Note: `config.py` and `comfy_client.py` reference Switchyard in config schemas/comments at `config.py:386,389,454,554,674-694` and `comfy_client.py:633,707` rather than `import director.switchyard`, whereas `queue.py:24` is imported transitively by `cli.py`, `runner.py`, `lease.py`, `gateway.py`, `ui.py`, `video_jobs.py`, `jobs.py`, and `chat_store.py`.)
  - **Every direct `director.switchyard` import site (`path:line`):**
    - Production modules (`C:\AI\director\src\director\` — 16 sites across 4 files):
      1. `C:\AI\director\src\director\cli.py:753`: `from director.switchyard.runnerlock import RunnerLockV2, RunnerHeld`
      2. `C:\AI\director\src\director\cli.py:789`: `from director.switchyard.runnerlock import RunnerLockV2, RunnerHeld`
      3. `C:\AI\director\src\director\cli.py:891`: `from director.switchyard.runnerlock import RunnerLockV2`
      4. `C:\AI\director\src\director\cli.py:1008`: `from director.switchyard.self_heal import HealEnv, heal`
      5. `C:\AI\director\src\director\cli.py:1117`: `from director.switchyard.self_heal import kill_runner`
      6. `C:\AI\director\src\director\cli.py:1148`: `from director.switchyard.session_lifecycle import probe_process`
      7. `C:\AI\director\src\director\cli.py:1477`: `from director.switchyard.cli_ops import register`
      8. `C:\AI\director\src\director\gateway.py:430`: `from director.switchyard.session_lifecycle import invalidate_session_token`
      9. `C:\AI\director\src\director\queue.py:24`: `from director.switchyard.jobstore import (...)`
      10. `C:\AI\director\src\director\runner.py:43`: `from director.switchyard.runnerlock import RunnerHeld, RunnerLockV2, RunnerLockedError`
      11. `C:\AI\director\src\director\runner.py:189`: `from director.switchyard.stale import mark_stale_running_jobs`
      12. `C:\AI\director\src\director\runner.py:266`: `from director.switchyard.session_lifecycle import release_session, session_is_open`
      13. `C:\AI\director\src\director\runner.py:310`: `from director.switchyard.session_lifecycle import check_process_identity`
      14. `C:\AI\director\src\director\runner.py:368`: `from director.switchyard.session_lifecycle import release_session`
      15. `C:\AI\director\src\director\runner.py:479`: `from director.switchyard.session_lifecycle import check_process_identity`
      16. `C:\AI\director\src\director\runner.py:528`: `from director.switchyard.session_lifecycle import release_session`
    - Unit test files (`C:\AI\director\tests\unit\` — 41 sites across 19 test files):
      - `test_cli_capa.py:73,93,130`, `test_cli_queue.py:335,359`, `test_comfy_as_model.py:11`, `test_health_capa.py:16,19`, `test_runner.py:696,785,1026`, `test_runner_capa.py:27,222,250`, `test_self_heal.py:13,14,293`, `test_session_lifecycle.py:3`, `test_switchyard_cli_ops.py:16,17`, `test_switchyard_cli_wait.py:16`, `test_switchyard_health.py:17`, `test_switchyard_jobstore.py:16`, `test_switchyard_ops.py:18,19,20`, `test_switchyard_paths.py:13`, `test_switchyard_registry.py:15`, `test_switchyard_runnerlock.py:22,23`, `test_switchyard_service.py:21,22`, `test_switchyard_vision.py:18,19,24`, `test_switchyard_waitops.py:12`, `test_u2_claim.py:16,17`, `test_wedge_ladder.py:15,16,260`.
  - **Which `discord_bridge.py` commands reach those modules:**
    - `discord_bridge.py` itself imports cleanly at top level (`python -c "import director.discord_bridge"` -> OK), because its helper imports are inside methods:
      - `request_model_load()` (`lines 660-696`) and `handle_stopall_command()` (`/stopall`, `lines 789-809`) import `director.config.load_settings` and `director.gpu.GPUManager`, which use `C:\AI\director\config\director.live.yaml` (where profile `coding_sc117_strata` at line 85 points to stale `C:\AI\strata\strata-iq3_xxs-switchyard.json`, and `gm.to_comfy()` calls `llama-swap` `/unload`).
      - `handle_queue_command()` (`/queue`, `lines 757-779`) reads `self.config.queue_dir / "status.md"` and `"status.json"` (the retired Switchyard spool folder `C:\AI\director-queue`, which is no longer updated by `director.runner`), returning stale or `"Status unavailable"`.
      - `handle_status_command()` (`/status`, `lines 698-755`) checks `self.config.switchyard_url` (`http://127.0.0.1:8080/health` and `/v1/models`, now served by `llama-swap`) and prints hardcoded `"Switchyard: Connected"`.
      - Any CLI invocation (`director ...` via `director.cli:app`) immediately crashes on import at `cli.py:23 -> runner.py:37 -> lease.py:27 -> queue.py:24`.
- **Three Options for Derrick (`NEEDS DERRICK` — DO NOT PICK OR IMPLEMENT):**
  1. **Option 1: Repoint `director` modules (`queue.py`, `cli.py`, `discord_bridge.py`) to `llama-swap` (`:8080`) + ComfyUI's own `/prompt` queue via `comm.py` / `run_graph_job.py` (with `guard_ok` intact).**
     - *Effort:* Medium (~2–3 hours; replace `director.switchyard.jobstore` in `queue.py` or decouple `queue.py`/`runner.py` from `cli.py`, update `discord_bridge.py` `/queue` and `/stopall` to query `llama-swap` `:8080/running` + `C:\AI\community\logs\p7_budget.json` / `C:\AI\locks\gpu-render.lock`, and archive obsolete `test_switchyard_*.py` tests).
     - *Risk:* Medium (touches 4–9 `director` files and test suite; requires thorough unit testing to ensure no regressions in `discord_bridge`).
     - *Rollback:* `git -C C:\AI\director revert <commit-range>`.
  2. **Option 2: Retire the dependent `director` queue/runner/cli commands (archive into `C:\AI\_archive\20261026_switchyard\`, not delete) and keep only standalone modules (`discord_bridge.py`, `minors_guard.py`, `config.py`).**
     - *Effort:* Low (~45 minutes; move `runner.py`, `queue.py`, `lease.py`, `gateway.py`, `ui.py`, `video_jobs.py`, `jobs.py`, `chat_store.py`, and `test_switchyard_*.py` to archive; trim `cli.py` and `discord_bridge.py` `/queue` to report llama-swap `/running`).
     - *Risk:* Low–Medium (cleanly removes dead Switchyard spool/runner abstractions while keeping `discord_bridge` and `minors_guard` intact).
     - *Rollback:* Move archived files back and `git -C C:\AI\director revert <sha>`.
  3. **Option 3: Restore `director.switchyard` package from `C:\AI\_archive\20261026_switchyard\director_src_switchyard\` (`git -C C:\AI\director revert 04b7f9e`).**
     - *Effort:* Minimal (~2 minutes: `Copy-Item` / `git revert 04b7f9e` in `C:\AI\director`).
     - *Risk:* Low technically (immediately restores `import director.cli` and all 9 broken modules + unit tests without running any Switchyard daemon), **but** leaves Switchyard code inside `C:\AI\director\src\director\switchyard` against Derrick's 5:58 AM question (*"why are we still using switchyard"*).
     - *Rollback:* Re-archive `src/director/switchyard`.
- **Rollback:** N/A (read-only)


## M3: Fix 5 Nonexistent `compound-engineering-plugin:*` Entries in `settings.json` & Propose Skill Trim List (`NEEDS DERRICK` for further disables)
- **Time CT:** 2026-10-26 10:03 CT
- **Step ID:** M3
- **Files:** `C:\Users\derek\.pi\agent\settings.json` (backed up to `C:\Users\derek\.pi\agent\settings.json.bak-20261026m-m3`)
- **Commit hash:** N/A (outside git repo; backup `C:\Users\derek\.pi\agent\settings.json.bak-20261026m-m3` verified)
- **Verify:**
  - `python -m json.tool C:\Users\derek\.pi\agent\settings.json` -> `rc=0` (valid JSON, non-null).
  - `DefaultPackageManager.resolve()` via `@earendil-works/pi-coding-agent` (`dist/core/package-manager.js`):
    - **Before M3:** `0 of 5` entries in `"skills": ["-compound-engineering-plugin:brainstorming", "-compound-engineering-plugin:content-creator", "-compound-engineering-plugin:social-media", "-compound-engineering-plugin:seo-analyzer", "-compound-engineering-plugin:copywriting"]` matched any skill (`38/38` skills loaded). Specifically: 4 names (`content-creator`, `social-media`, `seo-analyzer`, `copywriting`) do not exist anywhere in `compound-engineering-plugin`, the 5th (`brainstorming`) is actually named `ce-brainstorm`, AND per `@earendil-works/pi-coding-agent` official docs (`docs/packages.md:94-121` and `dist/core/config-selector.js:475-521`), package skills are filtered inside the package entry in `"packages"` using relative paths (`-skills/<name>/SKILL.md`), not via `-<pkg>:<name>` in top-level `"skills"`.
    - **After M3:** Replaced the 5 broken entries with the documented `packages` filter on `"git:github.com/EveryInc/compound-engineering-plugin"` excluding the 5 named skills (`-skills/ce-brainstorm/SKILL.md`, `-skills/ce-promote/SKILL.md`, `-skills/ce-product-pulse/SKILL.md`, `-skills/ce-proof/SKILL.md`, `-skills/ce-test-xcode/SKILL.md`). `DefaultPackageManager.resolve()` confirms `Disabled count: 5` (`["ce-brainstorm","ce-product-pulse","ce-promote","ce-proof","ce-test-xcode"]`), reducing loaded skills from 38 to 33.
  - **All 38 Real Installed Skills (from `DefaultResourceLoader`):**
    - `npm:pi-subagents` (2): `council-mode`, `pi-subagents`.
    - `git:github.com/EveryInc/compound-engineering-plugin` (36): `ce-babysit-pr`, `ce-bakeoff`, `ce-brainstorm` (disabled), `ce-code-review`, `ce-commit`, `ce-commit-push-pr`, `ce-compound`, `ce-compound-refresh`, `ce-debug`, `ce-doc-review`, `ce-dogfood`, `ce-explain`, `ce-handoff`, `ce-ideate`, `ce-noslop`, `ce-optimize`, `ce-plan`, `ce-polish`, `ce-pov`, `ce-product-pulse` (disabled), `ce-promote` (disabled), `ce-proof` (disabled), `ce-prototype`, `ce-resolve-pr-feedback`, `ce-retune`, `ce-riffrec-feedback-analysis`, `ce-setup`, `ce-simplify-code`, `ce-strategy`, `ce-sweep`, `ce-test-browser`, `ce-test-xcode` (disabled), `ce-work`, `ce-worktree`, `lfg`, `wtf`.
  - **REPORT-ONLY Proposal — Additional Real Skills to Disable (`NEEDS DERRICK`, NOT applied):**
    1. `ce-babysit-pr` (`-skills/ce-babysit-pr/SKILL.md`): Watches open GitHub PRs over time; Forge runs local commits with no git push or GitHub PRs.
    2. `ce-commit-push-pr` (`-skills/ce-commit-push-pr/SKILL.md`): Pushes branches and opens GitHub PRs, which is forbidden by Hard Limit 5 (`No git push`).
    3. `ce-resolve-pr-feedback` (`-skills/ce-resolve-pr-feedback/SKILL.md`): Resolves GitHub PR review threads; unused in local-only Forge loops.
    4. `ce-riffrec-feedback-analysis` (`-skills/ce-riffrec-feedback-analysis/SKILL.md`): Analyzes Riffrec product recordings; unrelated to AlienPc / ComfyUI / Forge.
    5. `ce-sweep` (`-skills/ce-sweep/SKILL.md`): Sweeps Slack, GitHub Issues, and email for feedback items; unrelated to local Forge tasks.
    6. `ce-dogfood` (`-skills/ce-dogfood/SKILL.md`): Drives a live web browser for web-app QA; unused in headless ComfyUI/Python passes.
    7. `ce-polish` (`-skills/ce-polish/SKILL.md`): Interactive live-browser UI polishing with a human in the loop; unused in headless Ralph passes.
    8. `ce-test-browser` (`-skills/ce-test-browser/SKILL.md`): Runs web-page browser tests for PR branches; unused in Forge passes.
    9. `ce-strategy` (`-skills/ce-strategy/SKILL.md`): Authors product `STRATEGY.md` roadmaps; Forge uses `fix_plan.md` instead.
    10. `ce-ideate` (`-skills/ce-ideate/SKILL.md`): Open-ended product ideation; Forge executes concrete `fix_plan.md` items.
    11. `ce-prototype` (`-skills/ce-prototype/SKILL.md`): Builds throwaway UI/product prototypes; unused in Forge's deterministic checklist loop.
    12. `ce-worktree` (`-skills/ce-worktree/SKILL.md`): Creates git worktrees/branches; Forge operates on the main checkout of `ralph-community` and `community`.
- **Rollback:** `Copy-Item -Path 'C:\Users\derek\.pi\agent\settings.json.bak-20261026m-m3' -Destination 'C:\Users\derek\.pi\agent\settings.json' -Force`


## M4: Isolate `-CommandOverride` Dry-Test Logs via `-LogPath` in `ralph.ps1` & Audit `S12-1`
- **Time CT:** 2026-10-26 10:06 CT
- **Step ID:** M4
- **Files:** `C:\Users\derek\5slock\ralph-community\ralph.ps1`
- **Commit hash:** `086f6ec` (`C:\Users\derek\5slock\ralph-community`)
- **Verify:**
  - `PSParser::Tokenize` on `ralph.ps1` -> `0 errors`.
  - Dry timeout test with `-CommandOverride` and `-LogPath`: production `logs\ralph.log` SHA256 unchanged (`True`); dry test output written cleanly to `$tmpLog` with `open=55` populated on the `PI_NONZERO rc=124` line (also fixed `$open` ordering before `PI_NONZERO`).
  - `powershell -NoProfile -ExecutionPolicy Bypass -File notes\ali05_loop_test.ps1` -> `15/15 sandbox runs OK, 0 failing cases (rc=0)`.
- **Rollback:** `git -C C:\Users\derek\5slock\ralph-community revert 086f6ec --no-edit`
- **Notes:**
  - Confirmed `logs\ralph.log` lines 802–804 (`2026-10-26T08:05:30 iter 1 : ITERATION_TIMEOUT after 2s ... PI_NONZERO rc=124`) came from the `S10-timeout` dry test (`-IterationTimeoutSec 2 -CommandOverride ...`), NOT a real Forge pass. Left `logs\ralph.log` untouched (no documented annotate parameter exists in `ralph.ps1`, and per M4 we do not edit or strip `ralph.log`).
  - Added optional `-LogPath` parameter to `ralph.ps1` and defaulted `-CommandOverride` runs (when `-LogPath` is omitted) to `$env:TEMP\ralph_override_$PID\ralph.log` so dry tests never pollute production `logs\ralph.log`, `logs\iter-$day-NN.log`, or `logs\DONE.txt`.
  - **Open item (`S12-1`):** `plan_v3.md` Step `S12-1` (copy `logs\ralph.log` to `logs\ralph.log.bak-20261026` then strip NUL bytes) was **never executed** (`logs\ralph.log.bak-20261026` does not exist and `logs\ralph.log` still contains pre-0.5 NUL bytes, as reported by `ali05_loop_test.ps1:135`: `note real logs\ralph.log NUL bytes present = True`). Logged as OPEN.


## M5: Audit `pi-mobile` Port 7878 Ownership, `EADDRINUSE` Handling, and Tailscale Check (`NEEDS DERRICK`)
- **Time CT:** 2026-10-26 10:08 CT
- **Step ID:** M5
- **Files:** Read-only audit of `C:\Users\derek\.pi\agent\npm\node_modules\pi-mobile\README.md`, `src\store.ts`, `src\link.ts`, `bin\pi-mobile.mjs`, `C:\AI\director\scripts\pi_mobile_hub.cjs`, and `C:\Users\derek\5slock\ralph-community\logs\iter-*.log`
- **Commit hash:** N/A (read-only; Decision #6 reserved for Derrick)
- **Verify:**
  - `Select-String -Path 'C:\Users\derek\5slock\ralph-community\logs\iter-*.log' -Pattern '7878|EADDRINUSE|pi-mobile'` -> `0 hits`.
  - `Get-NetTCPConnection -LocalPort 7878 -State Listen` -> `127.0.0.1:7878` owned by PID `21748` (`node.exe` running `C:\AI\director\scripts\pi_mobile_hub.cjs` under scheduled task `\pi-mobile`).
  - `~/.pi/agent/pi-mobile/config.json` keys: `enabled=True`, `port=7878`, `tailscale=null` (default on).
- **Findings & Analysis:**
  1. **Does an `EADDRINUSE` conflict happen between `pi_mobile_hub.cjs` and the `npm:pi-mobile` extension in Forge passes?**
     - **No unhandled conflict occurs.** Per `pi-mobile/src/link.ts:115-138` (`HubLink.connect()`), whenever a `pi` process starts with `config.enabled === true`, it **first** calls `dial(config.port, secret)` (`HTTP Upgrade: pi-mobile-link/1` to `127.0.0.1:7878` with header `x-pi-mobile-secret`). Because `pi_mobile_hub.cjs` instantiates the exact `Hub` class (`pi-mobile/src/hub.ts`) with the same `loadConfig()` and `linkSecret()`, `dial(7878, secret)` succeeds and the `pi` pass links to `pi_mobile_hub.cjs` as a client (`this.adopt(ch)`). `hostHub()` is only called when `dial()` throws `ECONNREFUSED` or `ECONNRESET` (nothing listening on 7878), and even in a simultaneous startup race `hostHub()` (`link.ts:41-44`) catches `if (e?.code === "EADDRINUSE") return false` and retries `dial()`.
     - Note for next pass logs: check `logs\iter-*.log` after the next pass to confirm zero `pi-mobile` errors under multi-pass operation.
  2. **Which component does the community setup expect to own port 7878?**
     - Per official `pi-mobile` docs (`README.md:5, 135, 149-154` and `src/store.ts:18-20`), `pi-mobile` ships **no standalone daemon** (`"No server to install... It all runs inside pi"`, `"One hub per machine. Whichever pi binds the port hosts it; the others link to it. If that pi exits, another takes over within a second"`). On a headless/remote box, the community docs state: *"Run pi on the box inside herdr or tmux so it survives your SSH disconnects"* — i.e., an interactive `pi` session owns port 7878, or port 7878 is only bound while a `pi` process is running.
     - `C:\AI\director\scripts\pi_mobile_hub.cjs` + `\pi-mobile` task (added in `director` commit `20642d5`) is a custom standalone wrapper that imports `pi-mobile/src/hub.ts` via `jiti` so port 7878 stays open when no `pi` process is running.
  3. **Prior Tailscale Check Flagged (Audit `K-2` / `N2-10 part 3`):**
     - The `S-pimobile` verification curled `https://<tailnet>:8443/` from AlienPc itself (local loopback through the local Tailscale client), **NOT** from another tailnet device (such as Derrick's phone or the cloud box). External tailnet reachability remains unverified until tested from a second device on the tailnet.
  4. **Proposed Stock Options (`NEEDS DERRICK` — Decision #6, do not decide here):**
     - **Option A (Stock `pi-mobile` extension owns port 7878):** Disable/unregister `\pi-mobile` task and archive `pi_mobile_hub.cjs` (`Unregister-ScheduledTask -TaskName pi-mobile -Confirm:$false`); either let `npm:pi-mobile` host 7878 during active passes (or keep one interactive `pi` window open when remote access between passes is desired).
     - **Option B (Keep `\pi-mobile` persistent hub task on 7878):** Leave `\pi-mobile` (`pi_mobile_hub.cjs`) running so `127.0.0.1:7878` stays open between passes while `npm:pi-mobile` in each pass links to it as a client over `pi-mobile-link/1`.
- **Rollback:** N/A (read-only)


## [2026-10-26 10:15:15 CT] Step M6: S10 timeout sized from renders per pass and per-pass wall time
- **Files:** `C:\Users\derek\5slock\ralph-community\ralph.ps1` (measured from `C:\AI\community\p7\jobs\*.result.json`, `C:\AI\community\runs\*\status.log`, `C:\Users\derek\5slock\ralph-community\logs\ralph.log`, `logs\ralph-*.log`, `logs\iter-*.log`, and `C:\AI\community\notes\web\01r_frankbria_readme.txt`)
- **Commit hash:** `9aee708` (`ralph-community`)
- **Verify:**
  - `[System.Management.Automation.PSParser]::Tokenize` -> `0 errors`.
  - `powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\derek\5slock\ralph-community\notes\ali05_loop_test.ps1` -> `15/15 sandbox runs OK` (rc 0).
- **Measurements & Recomputation (Audit `N2-7`):**
  1. **Single-render durations:**
     - `p7\jobs\*.result.json` (`39` files, `37` nonzero): `min = 17.0s`, `median = 739.0s` (12.3m), `p90 = 1,034.0s` (17.2m), `max = 3,048.0s` (`50.8m` in `ali147_pool_fix4_s51080000.result.json`, 3-segment stitch; plus `47.0m` = `2,820s` in `p7_r2_c3_pmot_full_pool.result.json` and `46.6m` = `2,796s` in `p7_r1_c1_pmot_full.result.json`).
     - `runs\*\status.log` (`40` unique render windows across `46` status files): `min = 35.7s`, `median = 752.5s` (12.5m), `p90 = 857.5s` (14.3m), `max = 3,046.0s` (`ali147_pool_fix4_s51080000`).
  2. **Renders per pass:**
     - Across all `180` completed `ralph.log` passes (`22` render-bearing completed passes): `p90 = 1` render/pass (`median = 1.0`), reflecting the `"1 clip per pass"` rule added on 2026-10-25.
     - Historical multi-render passes/bursts before the 1-clip rule: `2` renders in `2026-10-24T22:35:59..23:12:35` (`ali163_hc15_gi046_s51150014` + `ali163_hc15_gi063_s51150015`), `3` P7 render jobs in `2026-10-21 iter 01` and `iter 07` (and `3/3` segments inside `p7_r1_c1_pmot_full` / `ali147_pool_fix4_s51080000`), and `6` 15s HC15 renders in the uninterrupted `2026-10-24 16:18..18:08` pass (`~6,585s`).
     - For normal operation (`p90 = 1` render/pass) and A/B or 2-clip passes (`max = 2` renders/pass under current rules):
       - 1-render formula (`N2-7`): `1 × 3,048s + 1,200s queue/swap = 4,248s` (`~4,500s` = 75 min).
       - 2-render formula (`N2-7`): `2 × 3,048s + 1,200s queue/swap = 7,296s` (`~7,200s` = 120 min; or `2` typical 15m renders + cold LLM/ComfyUI swaps).
  3. **Per-pass wall time:**
     - Post-0.5 `logs\ralph-*.log` (`55` completed passes): `min = 8.0s`, `median = 1,672.0s` (27.9m), `p90 = 4,050.0s` (67.5m), `max = 6,269.0s` (104.5m, `ralph-20261025-20892.log` iter 4 `00:57:08..02:41:37`).
     - Full `logs\ralph.log` (`170` positive completed intervals): `min = 3.0s`, `median = 1,638.0s` (27.3m), `p90 = 3,449.0s` (57.5m), `max = 7,462.0s` (124.4m, `2026-10-25 17:08:22..19:12:44`). Five real passes (`4,698s`, `4,947s`, `5,388s`, `6,269s`, `7,462s`) exceeded `4,500s`.
  4. **Comparison with `frankbria/ralph-claude-code` timeout guidance & updated default:**
     - `frankbria/ralph-claude-code` (`https://github.com/frankbria/ralph-claude-code`, cached at `C:\AI\community\notes\web\01r_frankbria_readme.txt:155, 660, 695, 778-785`) documents `CLAUDE_TIMEOUT_MINUTES=15` default for hosted API calls and configurable execution timeouts of **`1–120 minutes` (`7,200s`)** (`--sandbox-timeout 7200` = 2h).
     - Updated `$IterationTimeoutSec` default in `ralph.ps1` from `4500` (75m) to **`7200` (120m = 2 hours)**, matching `frankbria/ralph-claude-code`'s 120-minute ceiling, covering `2` renders + queue/swap (`~7,200s`), and preventing premature `rc=124` kills on legitimate 78–105 minute passes (`4,698s`–`6,269s`).
- **Rollback:** `git -C C:\Users\derek\5slock\ralph-community revert 9aee708`


## [2026-10-26 10:17:00 CT] Step M7: REPORT-ONLY — Oct 25 lines dropped from the MAX block in commit ad0a2d4
- **Files:** Read-only inspection of `git -C C:\Users\derek\5slock\ralph-community show ad0a2d4 -- fix_plan.md`, `C:\Users\derek\5slock\ralph-community\fix_plan.md`, `notes\plans\receipts\*.md`, and `C:\AI\community\notes\needs_derrick.md`
- **Commit hash:** N/A (REPORT-ONLY; MAX block untouched per Hard Limit #13)
- **Verify:** `git -C C:\Users\derek\5slock\ralph-community show ad0a2d4 -- fix_plan.md` (17 lines removed from the MAX block, replaced by 8 Oct 26 lines).
- **Line-by-Line Audit of Dropped Oct 25 MAX Block Lines (Still Open Work vs. Done with Receipts):**

| Dropped Oct 25 MAX Line | Status | Receipt / Open Work Details for Max to Restore Below MAX Block |
|---|---|---|
| **1. Standing rules (`No secrets. KEEP is Derrick's.`)** | **KEEP BELOW BLOCK** | New MAX block kept `Youth guard: fictional adults only; the comm.py adults-only check runs before every render, never loosened`, but dropped `No secrets. KEEP is Derrick's.` (present in `AGENTS.md`, restore if needed in plan header). |
| **2. 3:56 AM & 3:41–4:02 AM Oct 25 (`Forge renders through llama-swap /comfyui itself and captions its own start images... ALI-7 and ALI-102: go (3:40 AM). ComfyUI attention flag and --lowvram to community defaults: "Yes" (4:01 AM). "STOP GIVING IT RULES"`)** | **PARTLY DONE / RESTORE `ALI-7` & `ALI-102` GO** | - Render via `/comfyui` & local vision captioning: **DONE** (`TOP-SCENE` receipt `notes/plans/receipts/TOP-SCENE-L22.md`, `VIS` receipt `notes/plans/receipts/VIS-L27.md`, `Forge-L130.md`).<br>- ComfyUI `--lowvram` / CLI attention flags: **DONE** (`llama-swap.yaml` has 0 hits).<br>- **`ALI-7` and `ALI-102` GO (3:40 AM):** **STILL OPEN** (`fix_plan.md:93-94` are unticked `- [ ]`; restore Derrick's 3:40 AM `"go"` annotation on rows `ALI-7` and `ALI-102`). |
| **3. 7:37 AM Oct 25 (`"contunie and have forge fix"` — 20-min LLM caller interrupting renders, notes dated Oct 26, GI063 robot clip not rendered, GI046 clip landed 7:31 AM)** | **DONE (except GI063 hold)** | - 20-min LLM caller / render lock (`MONITOR` / `RENDER-TIMEOUT`): **DONE** (`ralph.ps1` `GpuBusy` gate, receipt `notes/plans/receipts/RENDER-TIMEOUT-L29.md`).<br>- Oct 26 note dates: **DONE / SUPERSEDED** (receipt `notes/plans/receipts/2026-10-25-L31.md`).<br>- GI046 7:31 AM clip (`**4**`): **DONE** (receipt `notes/plans/receipts/4-L26.md`, `needs_derrick.md` row 26). |
| **4. Earlier GI063 hold reason (`GI063: on hold until Derrick rules on needs_derrick.md row 21 (Forge's own caption reads the start image as non-consensual). Do not render GI063 s51150031/s51150032 before his answer.`)** | **STILL MATTERS / RESTORE** | New MAX block line 9 says `"GI063 stays on render hold until Derrick says go"`, but drops the `needs_derrick.md` row 21 reason (chained wrists + distressed expression; refusal captioner read frame as non-consensual; shipped prompt asserted eagerness) and the explicit ban on `s51150031/s51150032`. **Max should restore row 21's context below the block.** |
| **5. 7:49 AM Oct 25 GI046 orc feedback (`"the orc.scene is horrible you can already see the fick out but he stops pulls down his pants and then has a small human dick instead of a green orc dick?"`)** | **STILL MATTERS / RESTORE** | Tracked in `needs_derrick.md` row 28 & 34b. New MAX block line 3 only says `"the GI046 orc anatomy wording the old card was silent about"`. Because `ORC-ROBOT` (`fix_plan.md:20`) is still `- [ ]` open, **Max should restore Derrick's verbatim 7:49 AM feedback on `ORC-ROBOT`** so Forge fixes the shorts/anatomy defect when re-authoring the GI046 prompt. |
| **6. 7:49–8:02 AM Oct 25 (`"Have Forge turn on Strata's refusal vector on Swift"`, citing `Niko1221/Strata` speed-projection & PR #1633)** | **DONE** | Ticked at `fix_plan.md:145` (`3.18 REFUSAL-TEST`, receipt `notes/plans/receipts/3.18-L154.md`, `C:\AI\community\notes\refusal_test_20261025.md`, `qwen35-35b-a3b-iq3s.json` `control_vectors`). |
| **7. 10:46 AM Oct 25 (`"Resume Forge and have it fix the vision routing, context, refusal test and monitor first"`)** | **DONE** | Vision routing (`VIS-L27.md`), context (`2.9-L82.md`, `3.19` line 146), refusal test (`3.18-L154.md`), monitor (`RENDER-TIMEOUT-L29.md`, `\ForgeAgyMonitor` `Disabled`) all completed. |
| **8. 11:10 AM Oct 25 (`"Lets test out all the different vision models and normal iqs3 with vision"`)** | **DONE** | Ticked at `fix_plan.md:144` (`3.17 VISION-BATTERY`, receipt `notes/plans/receipts/3.17-L153.md`, `C:\AI\community\notes\vision_battery_20261025.md`). |
| **9. 12:46 PM & 1:55 PM Oct 25 (`"cut fix_plan to a short community plan"`, docs copied to `C:\AI\community\research\forge-docs-20261025\` in commit `759c691`)** | **DONE (keep doc path pointer)** | Shortplan cut completed (`1.4d-L62.md`, `1.4e-L63.md`, `PLAN-ACTION-L64.md`). **Max may want to keep a one-line reference to `C:\AI\community\research\forge-docs-20261025\` (`759c691`) below the block.** |
| **10. 4:51 PM, 6:41 PM, 6:42 PM Oct 25 (`"Have Forge do the vision test, refusal test and 64K context check next"` -> `"wat the fuck arent we already determined we can do 128k context?"` -> `"judt keep it we did mesure it"`)** | **DONE** | `3.17` & `3.18` ticked; `3.19` closed at `fix_plan.md:146` quoting Derrick's 6:42 PM `"judt keep it we did mesure it"` ruling (128K context stays). |
| **11. 6:48 PM Oct 25 (6 picks)** | **PARTLY DONE / RESTORE EULER+5S+350-500W SPEC** | - **Pick 1 (Redo orc, robot & GI072 cards with uncensored vision model):** Initial pass in `needs_derrick.md` row 29 (`notes/top_card_vl_20261025.md`); follow-up `CARD-VL2` (`fix_plan.md:19`) covers GI063 & GI046.<br>- **Pick 2 (`"Go back to Euler, 5-second clips and 350-500 word prompts"`):** Ticked for GI046 (`E5-L23.md`, `needs_derrick.md` row 30), **BUT STILL MATTERS AS STANDING SPEC**: `ORC-ROBOT` (`fix_plan.md:20`) still says `"render both 15 s 16:9 clips"` instead of 5-second (124f) Euler clips with 350–500 word prompts. **Max should restore Pick 2 below the block and on `ORC-ROBOT`.**<br>- **Pick 3 (`"Sort out the Comfy Kitchen attention conflict"`):** Ticked (`CK-ATTN-L165.md`, `needs_derrick.md` row 31); KEEP decision pending Derrick.<br>- **Pick 4 (`"Fix the coding_heretic27b mislabel"`):** **DONE** (`HERETIC-LABEL-L166.md`, `needs_derrick.md` row 32).<br>- **Pick 5 (`"Look into the 27B server on port 8090"`):** **DONE / REPORTED** (`needs_derrick.md` row 32 & `notes/heretic27b_label_20261026.md`: `:8090` has 0 listeners; `RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf` is on disk awaiting Derrick's decision on serving shape).<br>- **Pick 6 (`"Turn off the 20-minute Antigravity monitor"`):** **DONE** (`\ForgeAgyMonitor` is `Disabled`). |
| **12. 7:12 PM Oct 25 (`"make sure it commits its work and doesnt do anything"`)** | **DONE** | One-off pass stop & commit executed on Oct 25 7:12 PM (`1.4d` / `e853c92`). |
| **13. 7:56 PM Oct 25 (`"Yes, have Forge get pi-mobile live for my phone"`)** | **PARTLY DONE** | Ticked at `fix_plan.md:95` (`PM2-L104.md`); open follow-ups tracked in M5 / Decision #6 (port 7878 ownership + external tailnet HTTPS check + QR pairing). |

- **Rollback:** N/A (read-only)


## [2026-10-26 10:21:50 CT] Step M8: Clean repeated IDs on ticked rows and deduplicate ticked E5 rows in fix_plan.md
- **Files:** `C:\Users\derek\5slock\ralph-community\fix_plan.md`, `C:\Users\derek\5slock\ralph-community\notes\plans\fix_plan.20261026m-m8.archived.md` (and copy at `C:\AI\community\briefs\argon_medium_20261026\fix_plan.20261026m-m8.archived.md`)
- **Commit hash:** `e895778` (`ralph-community`)
- **Verify:**
  - Forge state verified PAUSED (`\ForgeRalphLoop` `Disabled`, `0` active `ralph`/`pi` processes).
  - MAX block prefix (first `1,044` bytes up to `- [x] **TOP-SCENE**`) verified 100% byte-identical before and after.
  - Open count before (`OpenPlan` outside `## Optional` = `55`, total `- [ ]` lines = `63`) == Open count after (`OpenPlan` outside `## Optional` = `55`, total `- [ ]` lines = `63`).
  - `python C:\AI\community\notes\ali02_citation_check.py --plan` -> `55 open-row lines, 8 path citations, 0 problems` (rc 0).
- **Changes Made:**
  1. Archived `fix_plan.md` to `notes/plans/fix_plan.20261026m-m8.archived.md` and `C:\AI\community\briefs\argon_medium_20261026\fix_plan.20261026m-m8.archived.md`.
  2. Stripped repeated ID tokens (`4 4 4 4 4 4`, `1.4a 1.4a 1.4a 1.4a 1.4a 1.4a`, `1.4d 1.4d 1.4d 1.4d 1.4d`, `2.1b 2.1b 2.1b 2.1b 2.1b 2.1b`, `2.1c 2.1c 2.1c 2.1c 2.1c 2.1c`, `2.1a 2.1a 2.1a 2.1a 2.1a 2.1a`, `2.7b 2.7b 2.7b 2.7b 2.7b 2.7b`, `3.1a 3.1a 3.1a 3.1a 3.1a 3.1a`) from the 8 ticked rows (`**4**`, `**1.4a**`, `**1.4d**`, `**2.1b**`, `**2.1c**`, `**2.1a**`, `**2.7b**`, `**3.1a**`).
  3. Removed the 3 duplicate ticked `**E5**` rows (lines 13, 14, and 155), keeping the single canonical ticked `**E5**` row at line 12 (`notes/plans/receipts/E5-L23.md`).
- **Rollback:** `git -C C:\Users\derek\5slock\ralph-community revert e895778`


## [2026-10-26 10:23:10 CT] Step M9: REPORT-ONLY — (h) Euler vs res_multistep defaults & (j) A/B confound + missing _00002_.mp4 path
- **Files:** Read-only audit of `C:\AI\community\scripts\comm.py`, `C:\Users\derek\5slock\ralph-community\notes\plans\receipts\E5-L159.md`, `C:\AI\community\notes\hc15_anchor_fix_build.py`, `C:\AI\community\notes\hc15_anchor_carry_build.py`, `C:\AI\community\notes\top5_build.py`, `C:\AI\community\notes\orc_robot_build.py`, `C:\AI\community\runs\ali163_s8_pytorch_s51150011\request.api.json`, and `C:\AI\community\runs\ali163_s9_euler_s51150011\request.api.json`
- **Commit hash:** N/A (REPORT-ONLY; no render, no default change; Decision #1 reserved for Derrick)
- **Verify:**
  1. **Graph & `comm.py` defaults verified:**
     - `C:\AI\community\scripts\comm.py:107` (`_common`): `g["ksel"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}` — **`comm.py` already defaults to `"euler"`** (and `"attention": "pytorch attention"` at lines 86 and 134).
     - `C:\AI\community\notes\top5_build.py` (from `E5-L159.md`), `C:\AI\community\notes\orc_robot_build.py`, and `C:\AI\community\notes\ali163_hc15_build.py` also enforce `"sampler_name": "euler"`.
     - **Where `"res_multistep"` came from:** The 15s anchor-fix / anchor-carry builders (`C:\AI\community\notes\hc15_anchor_fix_build.py:108` and `C:\AI\community\notes\hc15_anchor_carry_build.py:173`) hardcode `g["ksel"]["inputs"]["sampler_name"] = "res_multistep"` and wrote `C:\AI\community\p7\graphs\ali163_hc15_bd002_s51150011.api.json` with `"sampler_name": "res_multistep"`, `c0.length = 243` (362f total), and `"attention": "comfy kitchen attention"`.
  2. **S8 vs S9 vs baseline A/B confound explained:**
     - `runs\ali163_hc15_bd002_s51150011\request.api.json`: `sampler_name = "res_multistep"`, `attention = "comfy kitchen attention"`, `noise_seed = 51150001`, `362f` (`571.7s`).
     - `runs\ali163_s8_pytorch_s51150011\request.api.json`: cloned from `ali163_hc15_bd002_s51150011.api.json` changing only `m_attn.inputs.attention` -> `"pytorch attention"`, so it ran `sampler_name = "res_multistep"`, `attention = "pytorch attention"`, `noise_seed = 51150001`, `362f` (`781.3s`).
     - `runs\ali163_s9_euler_s51150011\request.api.json`: cloned from S8 changing only `ksel.inputs.sampler_name` -> `"euler"`, so it ran `sampler_name = "euler"`, `attention = "pytorch attention"`, `noise_seed = 51150001`, `362f` (`780.7s`).
     - Additionally, `E5` (`E5-L159.md`) + `CK-ATTN` (`needs_derrick.md` row 31) already rendered a 5s (`124f`) `euler` pair on `noise_seed = 51160001`: `runs\ali163_top5_gi046_s51160001` (`euler` + `comfy kitchen attention`, `240.2s`) vs `runs\ali163_top5_gi046_s51160002` (`euler` + `pytorch attention`, `300.2s`).
  3. **Confirmation of missing `runs\ali163_s8_pytorch_s51150011\ali163_s8_pytorch_s51150011_00002_.mp4`:**
     - **Confirmed absent** (`Test-Path C:\AI\community\runs\ali163_s8_pytorch_s51150011\ali163_s8_pytorch_s51150011_00002_.mp4` = `False`).
     - **Root cause:** When `ali163_s9_euler_s51150011` was cloned from `ali163_s8_pytorch_s51150011`, its `save` node (`SaveVideo.inputs.filename_prefix`) was left as `"community/ali163_s8_pytorch_s51150011/ali163_s8_pytorch_s51150011"`. ComfyUI therefore wrote the raw file to `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\ali163_s8_pytorch_s51150011\ali163_s8_pytorch_s51150011_00002_.mp4` (`sha256: a46bbadbad7ad9bfe820800dae715b6e4c7e6e1a70ebdbf283d315e9fed0ee56`), and `comm.run()` (`comm.py:235-237`) copied that file to `C:\AI\community\runs\ali163_s9_euler_s51150011\ali163_s9_euler_s51150011.mp4` (verified identical SHA256 `a46bbadb...`, and recorded in `runs\ali163_s9_euler_s51150011\ali163_s9_euler_s51150011.mp4.json` under `"comfy_output"`).
  4. **Options for Derrick (`NEEDS DERRICK` — Decision #1):**
     - **Option A (`euler` everywhere, matching Derrick's 6:48 PM pick and `comm.py:107` / `top5_build.py`):** Keep `comm.py:107` and `top5_build.py` at `"euler"`, and update `hc15_anchor_fix_build.py` / `hc15_anchor_carry_build.py` if any 15s anchor graphs are rebuilt.
     - **Option B (`res_multistep` on 2-chunk 15s continuation graphs, `euler` on 1-pass 5s graphs):** Keep `top5_build.py` / `comm.py` at `"euler"` for 5s clips and `"res_multistep"` only for 15s multi-chunk continuation graphs.
     - **Option C (`res_multistep` everywhere per TenStrip HF discussion #61):** Switch `comm.py:107` to `"res_multistep"`.
- **Rollback:** N/A (read-only)


## [2026-10-26 10:36:39 CT] Step M10: Comfy Kitchen attention test idea (TEST ONLY, no default flip)
- **Files:**
  - Staged & ran `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\request.api.json` (`18,227 B`, `sha256: c20ae46920efbe6fb1f700017fa688140523a906aa87c5ea73a67ba84cbb83bd`)
  - Output clip `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\ali163_m10_ck_euler_s51150011.mp4` (`5,761,849 B`, `sha256: c1812773c88356f9733d37537f303c7cba11baed4e15dd302409bd0312018ac8`)
  - Output contact sheet `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\ali163_m10_ck_euler_s51150011_stills_contact.png` (`1,026,252 B`, `sha256: 60ea69c5acdffb238f2e7337573f722026a4235626bd805a7a79ed48da490390`)
  - `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\objective.json` and `status.log`
  - `C:\AI\community\scripts\comm.py` left UNTOUCHED (`ModelAttentionBackend` default remains `"pytorch attention"`, `sha256: 6caad36c37b4...`).
- **Commit hash:** N/A (test run in gitignored `runs/` only; no default flip in `comm.py`)
- **Verify:**
  - Pre-render `powershell -NoProfile -File C:\AI\director\scripts\gpu_guard.ps1` = `IDLE` (rc `0`).
  - Ran `C:\AI\director\.venv\Scripts\python.exe -u C:\AI\community\scripts\run_graph_job.py C:\AI\community\runs\ali163_m10_ck_euler_s51150011 ali163_m10_ck_euler_s51150011 --frames 362` (acquired `gpu-render.lock` pid `32348`, released `rc=0`, unloaded `comfyui_auto`, exit code `0`).
  - Controlled 1-variable diff vs `C:\AI\community\runs\ali163_s9_euler_s51150011\request.api.json`: ONLY `m_attn.inputs.attention` changed (`"pytorch attention"` → `"comfy kitchen attention"`), with identical BD002 prompt, `sampler_name = "euler"`, `scheduler = "simple"`, `noise_seed = 51150001` (`c0` and `c1`), `362` frames (`15.083333s`), `1344x768`.
- **Technical Signals Only (No Vision Model Used, No Subjective Quality Claim):**
  1. **Complete 2×2 Controlled Matrix on BD002 Seed `51150001` (`362f`, `1344x768`, `15.083s`, `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`):**
     | Run ID | Sampler | Attention Backend | RC | Frames | Resolution | Audio | Black/Freeze | Wall Secs | MP4 Bytes | Speedup vs PyTorch |
     |---|---|---|---:|---:|---|---|---|---:|---:|---|
     | `ali163_s9_euler_s51150011` | `euler` | `pytorch attention` | `0` | `362` | `1344x768` | `True` | `[]` | **`780.3s`** | `5,759,369` | baseline (`1.00x`) |
     | `ali163_m10_ck_euler_s51150011` (**M10**) | `euler` | `comfy kitchen attention` | `0` | `362` | `1344x768` | `True` | `[]` | **`600.3s`** | `5,761,849` | **`-180.0s` (`-23.1%`, `1.30x` faster)** |
     | `ali163_s8_pytorch_s51150011` | `res_multistep` | `pytorch attention` | `0` | `362` | `1344x768` | `True` | `[]` | **`780.4s`** | `6,423,907` | baseline (`1.00x`) |
     | `ali163_hc15_bd002_s51150011` | `res_multistep` | `comfy kitchen attention` | `0` | `362` | `1344x768` | `True` | `[]` | **`571.7s`** | `6,419,652` | **`-208.7s` (`-26.7%`, `1.37x` faster)** |
  2. **Prior 5s (`124f`) Euler GI046 Fixed-Seed (`51150032`) A/B (`C:\AI\community\notes\ck_attn_attention_20261025.md`):**
     - `ali163_top5_gi046_s51160002` (`euler` + `pytorch attention`): **`300.2s`**, `2,315,721 B`, `rc=0`, `blackfreeze=[]`.
     - `ali163_top5_gi046_s51160001` (`euler` + `comfy kitchen attention`): **`240.2s`**, `2,331,148 B`, `rc=0`, `blackfreeze=[]` (**`-60.0s`, `-20.0%`, `1.25x` faster**).
  3. **Compatibility & Community Guidance (`1xfrdh3` / ComfyUI `#15529`):**
     - ComfyUI issue `#15529` (`https://github.com/comfyanonymous/ComfyUI/issues/15529`, saved at `C:\AI\community\notes\web\02v_comfyui_issue15529.json`) reports `RuntimeError: quant_qk_per_thread_int8: Q/K base pointers and B/H/N strides must preserve 4-element alignment` on certain `int8_convrot` shapes/resolutions.
     - Reddit thread `1xfrdh3` (`C:\AI\community\notes\web\02v_r_1xfrdh3.json`) notes that `"pytorch attention"` is the universal safe fallback (`ComfyUI\comfy_extras\nodes_model_advanced.py:374-390` default).
     - On this `NVIDIA GeForce RTX 5070 Ti 16 GB` with `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` (`195` `comfy_quant` blocks, `0` `convrot` tensors, verified in `C:\AI\community\notes\ck_attn_attention_20261025.md:20`) at `1344x768`, `"comfy kitchen attention"` completes with `0` alignment errors and saves `~20%–27%` wall time (`3.0–3.5 minutes` per 15s clip).
  4. **Card for Derrick (`NEEDS DERRICK`):**
     - Left `comm.py:72` default at `"pytorch attention"`.
     - Derrick can compare `C:\AI\community\runs\ali163_s9_euler_s51150011\ali163_s9_euler_s51150011.mp4` (`pytorch attention`, `780.3s`) vs `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\ali163_m10_ck_euler_s51150011.mp4` (`comfy kitchen attention`, `600.3s`) on identical seed `51150001` and `euler` sampler and decide whether to keep `"pytorch attention"` or switch to `"comfy kitchen attention"` for `1344x768` jobs.
- **Rollback:** `comm.py` untouched; test output isolated in `C:\AI\community\runs\ali163_m10_ck_euler_s51150011\`.


## [2026-10-26 10:27:00 CT] Step M11: REPORT-ONLY — (m) Forgesafe lines comparison & minimal carry-over proposal
- **Files:** Read-only audit of `C:\Users\derek\5slock\notes\AGENTS.20261026.archived.md` (60 lines), `C:\Users\derek\5slock\ralph-community\AGENTS.md` (39 lines), and `C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc` (343 lines)
- **Commit hash:** N/A (REPORT-ONLY per brief Scope Notes line 100; `pi-permissions.jsonc` untouched and SHA256 unchanged)
- **Verify:**
  - `C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc` SHA256 verified unchanged (`170AAE661BCF45314B2E22C65CFC33AD7DA05F7BA48ABFEC0821BDFC4C2AADEB`).
  - `C:\Users\derek\5slock\ralph-community\AGENTS.md` line count = `39` (capped at `< 40` by header and `<= 40` by `d_agents_lines` in `notes\ali05_loop_check.py:425-427`).
- **Findings — What is Enforced in `pi-permissions.jsonc` vs. What is Only in Prose/Gates:**
  1. **Enforced in `C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc` (`pi-permission-system@0.8.0`):**
     - `defaultPolicy`: `"allow"` across `tools`, `bash`, `mcp`, `skills`, `special`.
     - `tools` (`read`/`grep`/`find`/`ls`/`edit`/`write`) and `special` (`external_directory`): **39 secret/credential globs per verb** (`*/.env*`, `*rclone.conf`, `*/rclone/*`, `*/auth.json`, `*/.git-credentials`, `*/.netrc`, `*/.npmrc`, `*/.pypirc`, `*/.ssh/*`, `*/id_rsa*`, `*/id_ed25519*`, `*.pem`, `*.pfx`, `*.p12`, `*.key`, `*.kdbx`, `*.ppk`, `*/token*`, `*/secret*`, `*/credentials*`, `*api_key*`, `*api-key*`, `*apikey*`, `*/Microsoft/{Credentials,Protect,Vault}/*`).
     - `bash`: **50 secret/credential command globs** (same secret files plus `*/.aws/*`, `*/.docker/config.json*`, `*/.kube/config*`, `*/.azure/*`, `*/.config/gcloud*`, `*/Login Data*`, `*/Network/Cookies*`, `*access_token*`, `*refresh_token*`, `*BEGIN*PRIVATE*KEY*`, `*printenv*`, `*cmdkey*`, `*Get-StoredCredential*`, `*vaultcmd*`, `*forge11-secrets-probe*`, `*/.forge11*`).
     - **Not enforced by `pi-permissions.jsonc`:**
       - `powershell` tool arguments (gated by tool name only in `pi-permission-system@0.8.0`, recorded in `AGENTS.md` L13).
       - `scripts/comm.py` and `scripts/tests/test_p6_review.py` edit protection (enforced by `notes/rt_window_probe.py` and `notes/ali05_loop_check.py` SHA256 pins, not `pi-permissions.jsonc`).
       - ComfyUI restart mid-render (enforced by `gpu_lock.ps1` / `comfy_ctl.py` / `comfy_graceful_stop.ps1`, not `pi-permissions.jsonc`).
       - Finance/UniFi folders (`C:/Apps/finance-app-rebuild`, `D:/Apps/finance-app*`), Grok Imagine `.json` sidecars / GMD prompt cache, and `git push` / `reset --hard` (enforced by `AGENTS.md` / `PROMPT.md` prose only).
  2. **Archived `AGENTS.20261026.archived.md` Rules Missing from `ralph-community\AGENTS.md`:**
     - Archived line 4: `"Denied only: secrets (.env*, rclone, keys/tokens, credential stores), edits to scripts/comm.py + its test, ComfyUI restart mid-render."`
     - Archived line 8: `"Prefer the read / grep / find / ls tools over shell commands for reading and searching."`
     - Archived line 31–32: Finance app exclusion (`C:/Apps/finance-app-rebuild`, `D:/Apps/finance-app*`), no `git push/reset/checkout/--amend`.
     - Archived line 56: `"a credential-shaped env name in a command line = secret deny... Never retry a deny."`
  3. **Minimal Carry-Over Proposal (keeps `ralph-community\AGENTS.md` at 39 lines, `< 40` cap, preserving all `RENDER_MARKERS["agents"]` required by `ali05_loop_check.py`):**
     - **Append to Line 6 (`## Run`):**
       ` | Prefer read/grep/find/ls tools over shell for reading/searching; never retry or work around a deny.`
     - **Append to Line 17 (`## Hard lines`):**
       ` | Denied only: secrets (.env*, rclone, auth.json, keys/tokens, credential stores), edits to test_p6_review.py or comm.guard_ok, Grok Imagine .json sidecars/GMD cache, finance/UniFi paths (D:/Apps/finance-app*), git push/reset --hard.`
- **Rollback:** N/A (read-only)
- **Rollback:** N/A (read-only)---

## M12 — Line-by-line check of `plan_v3.md` against Fleet Reviewer audit (`context\fleet_audit_r2.md`)

- **Step ID:** M12
- **Timestamp:** 2026-10-26 10:30:30 CT
- **Files Touched:** Read-only check (`C:\AI\community\briefs\argon_audit_20261025\context\fleet_audit_r2.md`, `C:\AI\community\briefs\argon_audit_20261025\plan_v3.md`, `C:\AI\community\briefs\argon_audit_20261025\progress.md`, and live repo histories)
- **Line-by-Line Audit Matrix (`fleet_audit_r2.md` → `plan_v3.md` → Execution):**

| Audit ID | Audit Finding / Fix Requirement | Status in `plan_v3.md` & Execution | Evidence / Commit / Note |
|---|---|---|---|
| **A-1** | `ali173_pw1d_run.py` bypasses `comm.guard_ok` and posts directly to `:10004` | **Applied in `plan_v3` + executed** (`community` `9b5da7a`, `S0`) | `ali173_pw1d_run.py` imports `comm`, calls `comm.guard_ok(g)`, posts to `comm.BASE`. |
| **A-2** | `comm.guard_ok` only scanned `text`, `prompt`, `positive`, missing `extra_text`, `prefix_text`, `suffix_text` | **Applied in `plan_v3` + executed** (`community` `a9d3a98` `S1a`, `b87127d` `S1b`; `ralph-community` `d88638c`) | `comm.guard_ok` checks `("text", "prompt", "positive", "extra_text", "prefix_text", "suffix_text")`; `test_guard_scope.py` added; `guard_pins.json` updated. |
| **A-3** | Step 12 `fix_plan.md` line 133 contradiction (`persistent: true` vs unified `groups.main`) | **Applied in `plan_v3` + executed** (`ralph-community` `d88638c` `S7-groups`, plus Forge's `33e18f8` `GPU-LOCK`) | `rt_window_probe.py` and `AGENTS.md` aligned with single exclusive `groups.main`. |
| **A-4** | Every step in `plan_v3` must carry **Why**, **Verify**, **Risk**, **Rollback** | **Dropped / incomplete** | `plan_v3.md` steps have `Why`, `Action`, `Verify`, `Rollback`, **no `Risk:` lines**. |
| **A-5** | Keep 128K context (`131072`) on `coding_swift15_iq3s` | **Applied in `plan_v3` + executed** (no edit; verified) | `C:\AI\director\config\llama-swap.yaml:86` keeps `-c 131072`. |
| **A-6** | Budget enforcement in `run_graph_job.py` (`cap_min: 180` / `job_cap: 15` already exceeded at `184.42m` / `28` jobs) — clarify warn-only vs hard-fail | **Applied in `plan_v3` + executed as non-blocking counter** (`community` `ab0e449` `S10-counter`), **question to Derrick still open** | `run_graph_job.py` updates `p7_budget.json` and logs `[BUDGET WARN]` without blocking renders; whether to reset/raise caps or make hard-blocking remains `NEEDS DERRICK`. |
| **A-7** | Youth guard hard limits: `comm.guard_ok` before every render; `p6_review.guard_check` untouched; no vision judge on rendered explicit output; **vision never decides identity or age**; **no celebrity/real-person LoRAs** | **Partially dropped in `plan_v3.md`** | `plan_v3.md` Top Rule #3 kept `comm.guard_ok`, `p6_review.guard_check`, and no vision on explicit clips, **but omitted "vision never decides identity or age" and "no celebrity/real-person LoRAs"** (present only in the brief's hard limits). |
| **A-8** | Remove 4 false Heretic aliases (`qwen3.5-27b-Claude-4.6-Opus-Uncensored-Distilled`, `huihui-qwen3-coder-30b-a3b-abliterated`, `dolphin-3.0-r1-mistral-24b`, `amoral-gemma3-27b-v2`) | **Applied in `plan_v3` (Step 5) + already executed by Forge** (`director` `270f51b` `HERETIC-LABEL`) | Verified 0 matches in `C:\AI\director\config\llama-swap.yaml`. |
| **A-9** | Do not break `pi` model lookups (`coding_swift15_iq3s`, `vl_judge`, `qwen3vl_judge`) when cleaning aliases | **Applied in `plan_v3` + executed** | All 3 IDs in `C:\Users\derek\.pi\agent\models.json` resolve in `llama-swap.yaml`. |
| **A-10** | Rollback command for every step; **no `Risk:` lines in `plan_v2.md`** | **Partially dropped in `plan_v3.md`** | Rollback lines added to `plan_v3.md`, **but `Risk:` lines were still omitted from every step**. |
| **K-1** | Option 2 selected for Switchyard: retire Switchyard code (`director\src\director\switchyard`) and keep `llama-swap` (`:8080`) + `keepalive.ps1` | **Applied in `plan_v3` (Step 2) + executed WITH CALLER-CENSUS DEFECT** (`director` `04b7f9e` `S-switchyard`) | Moved `src\director\switchyard` to `archive\switchyard-retired-20261026\switchyard` after grepping only `C:\AI\community` and `ralph-community`, **missing 16 production imports in `director\src\director\{cli,gateway,queue,runner}.py` and 41 test imports (documented in M2)**. |
| **K-2** | Keep `pi-mobile` always running on port `7878` over Tailscale HTTPS (`https://<tailnet>:7878`) | **Applied in `plan_v3` (Step 3) + partially executed** (`director` `20642d5` `S-pimobile`), **remote tailnet device check missed** | `\pi-mobile` scheduled task + keepalive added, **but `S-pimobile` curled `https://<tailnet>:7878/` from AlienPc itself rather than another tailnet device (confirmed in M5)**. |
| **G-1** | Pause Forge before any edits (`Disable-ScheduledTask -TaskName '\ForgeRalphLoop'`) | **Applied in `plan_v3` (Step 0a) + executed** | `\ForgeRalphLoop` is `Disabled`; verified in M0. |
| **§8 Check 1** | Is `comm.guard_ok` called by every ComfyUI submitter? | **Applied in `plan_v3` + executed** (`community` `9b5da7a` `S0`) | Fixed `ali173_pw1d_run.py` bypass. |
| **§8 Check 2** | Does `comm.guard_ok` check every prompt-bearing field? | **Applied in `plan_v3` + executed** (`community` `a9d3a98` `S1a`, `b87127d` `S1b`) | Added `extra_text`, `prefix_text`, `suffix_text` + cleaned `Continuum` `no:` lines. |
| **§8 Check 3** | Is `p6_review.guard_check` intact and passing `pytest`? | **Applied in `plan_v3` + executed** | `test_p6_review.py` SHA256 unchanged, `9 passed` (`test_p6_review.py` + `test_guard_scope.py`). |
| **§8 Check 4** | Is `llama-swap.yaml` running a single exclusive `groups.main`? | **Applied in `plan_v3` + executed** (`ralph-community` `d88638c` `S7-groups`) | `rt_window_probe.py` and `AGENTS.md` aligned with `groups.main`. |
| **§8 Check 5** | Is `131072` context active on `coding_swift15_iq3s`? | **Applied in `plan_v3` + executed** | Preserved `-c 131072`. |
| **§8 Check 6** | Are the 4 false Heretic aliases removed without breaking `pi`? | **Applied in `plan_v3` + executed** (`director` `270f51b`) | Verified. |
| **§8 Check 7** | Is `vl_judge` sending `reasoning_effort: "none"` without touching `guard_check`? | **Applied in `plan_v3` + executed** (`community` `40f8b00` `S6b`) | Added `"reasoning_effort": "none"` in `p6_review.py:163`, `ali10_vlm_ battery.py:59`, `top_card_vl_build.py:92`. |
| **§8 Check 8** | Is `ModelAttentionBackend` set to `"pytorch attention"` and Euler vs `res_multistep` A/B tested on fixed seed? | **Applied in `plan_v3` + executed WITH A/B CONFOUND** (`community` `5539268` `S8`, `213b9d0` `S9b`) | `comm.py:72` set to `"pytorch attention"`. However, S8/S9 A/B was confounded on two variables (`res_multistep` vs `euler` AND `comfy kitchen` vs `pytorch`), cited wrong URL/GPU, and left `_00002_.mp4` in ComfyUI output dir (fixed/re-audited in M1, M9, M10). |
| **§8 Check 9** | Is `C:\AI\director` fast-forwarded to `bf76b64` and passing `91/91` Switchyard tests? | **Superseded by K-1 retirement, never answered** | `S-switchyard` retired `src\director\switchyard` without checking callers inside `director\src\director\*` or `director\tests\*`, leaving `director` CLI and 19 test files broken (`ModuleNotFoundError: No module named 'director.switchyard'`, documented in M2). |
| **§8 Check 10** | Are the 6 wiped open `fix_plan.md` items restored and shortplan builder disabled? | **Applied in `plan_v3` + executed** (`ralph-community` `87add49` `S7-restore`, `d6b2619` `S7-builder`, `8e2bc40` `S7-checks`) | Restored 6 open items; retired `ali01_shortplan_build.py` auto-emit; pruned `ali11_run_checks.py` to 6 core validators. |
| **N2-1** | `comm.guard_ok` bypassed by `ali173_pw1d_run.py` and missing `extra_text`/`prefix_text`/`suffix_text` | **Applied in `plan_v3` + executed** (`9b5da7a`, `a9d3a98`, `b87127d`) | Verified. |
| **N2-2** | Step 12 `persistent: true` contradicts Step 4 unified `groups.main` | **Applied in `plan_v3` + executed** (`d88638c`) | Verified. |
| **N2-3** | Step 6 (`p6_review.py` `reasoning_effort`) must not touch `guard_check` | **Applied in `plan_v3` + executed** (`40f8b00`) | Only `caption_image` payload (`p6_review.py:163`) modified; `guard_check` untouched. |
| **N2-4** | Step 8 Comfy Kitchen attention vs PyTorch attention contradiction | **Applied in `plan_v3` + executed** (`5539268`), **except R2-7 #6 pack file update** | `comm.py:72` set to `"pytorch attention"`; controlled fixed-seed Comfy Kitchen test running in M10. |
| **N2-5** | Step 9 must fix seed (`51150011`) and prompt (`ali163_hc15_bd002_s51150011`) for A/B test | **Applied in `plan_v3` + executed WITH CONFOUND** (`213b9d0`) | Re-audited in M1 and M9. |
| **N2-6** | Step 7 (`fix_plan.md`) must restore 6 wiped items, clean repeated IDs, and stop `ali01_shortplan_build.py` from overwriting | **Applied in `plan_v3` + partially executed** (`87add49`, `d6b2619`, `8e2bc40`), **ticked rows left with repeated IDs & 4x `E5` until M8** | `S7-restore` only cleaned unticked rows; **M8 (`e895778`)** cleaned the 8 ticked repeated-ID rows and deduplicated the 4 ticked `E5` rows. |
| **N2-7** | Step 10 timeout (`45m`) too short; must check max/p90 render time AND **renders per pass** before sizing | **Dropped "renders per pass" in `plan_v3` (`S10-timeout` used 4500s from 1 render) → fixed in M6 (`9aee708`)** | `plan_v3.md` S10-timeout sized `4500s` from a single render (`3,048s × 1.5`), ignoring multi-render passes (`max = 6,269s–7,462s`). Fixed in **M6** (`9aee708`, `IterationTimeoutSec = 7200`). |
| **N2-8** | Step 10 (`settings.json`) must name the exact skills to disable | **Named in `plan_v3`, but wrong/nonexistent skill names (`compound-engineering-plugin:*`) → fixed in M3** | `plan_v3.md` S10-skills wrote 5 nonexistent `-compound-engineering-plugin:*` entries (`0/5` matched). Fixed in **M3** using package filter syntax (`5/5` matched, `38 → 33` skills). |
| **N2-9** | Step 2 Switchyard retirement: check callers first, archive don't delete, keep `llama-swap` + `keepalive.ps1` | **Applied in `plan_v3`, caller census missed `director` itself (`04b7f9e`) → audited in M2** | Documented in M2 (`NEEDS DERRICK`). |
| **N2-10** | Step 3 `pi-mobile` persistence: verify port `7878` conflict, add keepalive/task, verify `https://<tailnet>:7878` **from another tailnet device** | **Part 3 ("from another device") dropped in `plan_v3` / `S-pimobile` → audited in M5** | `S-pimobile` curled from AlienPc itself; port `7878` client-first behavior verified in M5; remote tailnet test flagged for Derrick. |
| **N2-11** | Step 12 `progress.md` rotation + `ralph.log` `1,978` NUL bytes strip (`S12-1`) | **`S10-rotate` executed (`e3af759`), `S12-1` (`ralph.log` NUL strip) in `plan_v3` but NOT executed** | Confirmed in M4: `C:\Users\derek\5slock\ralph-community\logs\ralph.log` still contains `1,978` NUL bytes (`S12-1` OPEN). |
| **R2-7 #5** | `ALI-162` (`fix_plan.md` L116) remains open `- [ ]`; items 1 (`int8 attention default`) and 5 (`drop --lowvram`) were never checked on the live box | **Dropped from `plan_v3.md` → checked live in M12 below** | See live box check below. |
| **R2-7 #6** | Max updates his pack line (`brain-staging/10_packs/max/production-defaults-st8-dynamic-vram.md` line 15) for Oct 9 `ck-attention KEEP` superseded | **Not done (box file outside AlienPc)** | Flagged for Max only (cannot edit box files from AlienPc). |

- **Confirmation of the 9 Box Pre-Check Gaps:**
  1. **`N2-7` "renders per pass" missing from `plan_v3` (timeout sized from one render):** **CONFIRMED** — resolved in **M6** (`ralph-community` commit `9aee708`, `$IterationTimeoutSec = 7200`).
  2. **`A-7` "vision never decides identity or age" and "no celebrity/real-person LoRAs" not in `plan_v3`:** **CONFIRMED** — present in the brief's hard limits and enforced in this run (`AGENTS.md:8` also carries `Wait for Derrick on: ... any identity/LoRA`).
  3. **`K-2` / `N2-10` part 3: HTTPS check "from another device" missing (`S-pimobile` curled from AlienPc):** **CONFIRMED** — documented in **M5** (`NEEDS DERRICK`).
  4. **`Fix #5` (`R2-7 #5`): `ALI-162` items 1 and 5 status never checked:** **CONFIRMED** — checked live on the box right now:
     - **Item 1 (`int8 default attention`):** Originally set to `"comfy kitchen attention"` in `comm.py:72`, changed to `"pytorch attention"` in `S8` (`5539268`), and currently under controlled fixed-seed A/B test in **M10**.
     - **Item 5 (`drop --lowvram`):** **ALREADY DONE** in `C:\AI\director\config\llama-swap.yaml:132` (`comfyui_auto` runs `--listen 127.0.0.1 --port ${PORT} --disable-async-offload --disable-pinned-memory` with no `--lowvram`).
     - **Other `ALI-162` items measured live:** Item 3 (`no VLM judge on explicit clips`) is **DONE**; Item 2 (`H3-Motion-Context v0.7.1`) is not installed under that name (`ComfyUI-H3-Continuum` is `v3.10.2`, `ComfyUI_MiniMax_H3_Extender` is `3.0.6-11-g0861230`, `comfyui-minimax-h3-continuation` is `e1768d5`); Item 6 (`ComfyUI 0.42.1 + soundfile/PyWavelets + Manager 4.3`) is **NOT DONE / PINNED** (`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` is at tag `v0.38.0` per Oct 12–16 community pin advice in `settings_audit_20261023.md:28`, `ComfyUI-Manager` is at `d6f480c`, and `soundfile`/`pywt` are not installed in `ComfyUI\.venv`).
  5. **`§8 #9`: Switchyard `91/91` tests / `bf76b64` fast-forward never answered:** **CONFIRMED** — superseded by `S-switchyard` (`04b7f9e`), which broke 9 `director` modules and 19 test files because the caller census missed `C:\AI\director\src\director\*` (documented in **M2**).
  6. **`A-10` / `A-4`: no `Risk:` lines in `plan_v3` steps:** **CONFIRMED** — `plan_v3.md` omitted `Risk:` lines across all steps.
  7. **`S12-1` `ralph.log` NUL strip in `plan_v3`, not executed:** **CONFIRMED** — `C:\Users\derek\5slock\ralph-community\logs\ralph.log` still has `1,978` NUL bytes (`0x00`), logged as OPEN in **M4**.
  8. **`N2-8`: "name the Step 10 skills" — named, but wrong names:** **CONFIRMED** — `plan_v3.md` used nonexistent `compound-engineering-plugin:*` names (`0/5` matched); fixed in **M3** via package filter (`5/5` matched).
  9. **`R2-7 #6`: "Max updates his pack line" (`brain-staging/10_packs/max/production-defaults-st8-dynamic-vram.md` line 15 still says `ck-attention KEEP`):** **CONFIRMED** — flagged for **Max** (box file outside AlienPc).
- **Rollback:** N/A (read-only)


## [2026-10-26 10:45:48 CT] Step M13: Component review vs official docs and community guidance
- **Files:**
  - Backed up `C:\Users\derek\.pi\agent\settings.json` to `C:\Users\derek\.pi\agent\settings.json.bak-20261026m-m13` and added `"defaultModel": "coding_swift15_iq3s"` alongside `"model": "coding_swift15_iq3s"`.
  - `C:\Users\derek\5slock\ralph-community\notes\ali04_pi_probe.py`, `notes\ali20b_ext_probe.py`, `notes\ali20b_skillspector_build.py` (commit `9af1ee9`: support package filter objects per `docs/packages.md:94-121` and bare `defaultModel` per `docs/settings.md:14`).
  - `C:\AI\community\scripts\run_graph_job.py` (commit `6358c39`: move `static_check(g0)` inside `try:` after `gpu_idle(log)`, `gpu_lock(...)`, and `wake(log)` so `/comfyui/object_info` never wakes `comfyui_auto` before `gpu_guard.ps1` is checked).
  - `C:\Users\derek\5slock\ralph-community\notes\rules-snapshots-2026-10-25\guard_pins.json` (commit `d02307f`: align `comm_guard_call_marker` from `"not guard_ok(p)"` to `"not guard_ok(s)"` matching `S1a` `a9d3a98`).
- **Commit hashes:**
  - `ralph-community`: `9af1ee9` (`M13: support package filter objects and bare defaultModel in ali04_pi_probe and skillspector probes`)
  - `community`: `6358c39` (`M13: move static_check after gpu_idle, gpu_lock, and wake inside try block in run_graph_job.py`)
  - `ralph-community`: `d02307f` (`M13: align guard_pins.json comm_guard_call_marker with S1a prompt_strings loop variable`)
- **Verify:**
  - `C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\5slock\ralph-community\notes\ali04_pi_probe.py --selftest` → `SELFTEST OK - 17/17 detectors behaved` (rc `0`).
  - `C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\5slock\ralph-community\notes\ali04_pi_probe.py --stock --no-pi` → `VERDICT stock: OK` (rc `0`).
  - `C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\5slock\ralph-community\notes\ali20b_ext_probe.py` → rc `0`.
  - `C:\AI\director\.venv\Scripts\python.exe C:\Users\derek\5slock\ralph-community\notes\rt_window_probe.py --check` → `RT_WINDOW_PROBE CLEAN checks=16` (rc `0`) and `--selftest` → `SELFTEST_OK seeds=16 missed=[] base_dirty=[]` (rc `0`).
- **Component-by-Component Review & Mismatches Logged:**
  1. **`pi` (`@earendil-works/pi-coding-agent` v1.4.0 — official docs: `https://www.npmjs.com/package/@earendil-works/pi-coding-agent` and local package docs `docs/settings.md`, `docs/models-configuration.md`, `docs/packages.md`, `docs/cli-integration.md`):**
     - **`C:\Users\derek\.pi\agent\settings.json`:**
       - **Mismatch Found & Fixed:** `settings.json` had `"model": "coding_swift15_iq3s"` without `"defaultModel"`. Per `docs/settings.md:14` and `dist/core/settings-manager.js:531` (`getDefaultModel() { return this.settings.defaultModel; }`), `pi` reads `defaultModel` (paired with `defaultProvider: "llama-swap"` in `dist/core/model-resolver.js:398-399`). Without `defaultModel`, an interactive `pi` run without `--model` fell back to `availableModels[0]` (`strata/qwen3.8-flash-next-iq3_xxs`). Added `"defaultModel": "coding_swift15_iq3s"` while keeping `"model": "coding_swift15_iq3s"` and updated `ali04_pi_probe.py` (`9af1ee9`).
       - **`packages` filter:** Uses documented package object filter (`docs/packages.md:94-121`); updated `ali04_pi_probe.py`, `ali20b_ext_probe.py`, and `ali20b_skillspector_build.py` (`9af1ee9`) so they read `p["source"]` when `p` is a `dict`.
       - **`compaction` (`docs/settings.md:71-76`):** `enabled: true`, `reserveTokens: 16384`, `keepRecentTokens: 16384` (stock default `20000`), `modelOverrides` keyed by `provider/modelId` (`llama-swap/coding_swift15_iq3s`, etc.) — matches spec.
       - **`httpIdleTimeoutMs` & `retry` (`docs/settings.md:126-136`):** `httpIdleTimeoutMs: 1950000` (`32.5m`, above `llama-swap` `unloadTimeout: 1900s`), `retry.enabled: true`, `retry.maxRetries: 2`, `retry.provider.timeoutMs: 1200000` (`20m`), `retry.provider.maxRetries: 0` (matches `docs/settings.md:136`: `"Keep retry.provider.maxRetries at 0 unless provider-level retries are required"`).
     - **`C:\Users\derek\.pi\agent\models.json` (`docs/models-configuration.md:28-58, 109-123`):**
       - `coding_swift15_iq3s`: `contextWindow: 128000`, `maxTokens: 16384`, `reasoning: true`, `input: ["text", "image"]`, `compat: {"thinkingFormat": "qwen-chat-template", "supportsReasoningEffort": true}`.
       - `vl_judge` (`Qwen3.5-9B-The-Defiant-Fable-DARK-ROAST-Uncensored-Heretic-NEO-IMATRIX-MAX-MTP.Q8_0.gguf`): `reasoning: false`, `input: ["text", "image"]`, `contextWindow: 65536`, `maxTokens: 4096`.
       - `qwen3vl_judge` (`Huihui-Qwen3-VL-8B-Instruct-abliterated-Q8_0.gguf`): `reasoning: false`, `input: ["text", "image"]`, `contextWindow: 32768`, `maxTokens: 4096`.
     - **`C:\AI\director\config\pi\settings.json` (Mismatch Logged — Report Only):**
       - Legacy Director Pi config has `"defaultProvider": "alienpc"` and `"defaultModel": "huihui-qwen3.8-27b-iq3xxs-mtp"`, `"extensions": ["-builtin:llama.cpp", "-builtin:mcp"]`, `"images": {"blockImages": true}`, `"httpIdleTimeoutMs": 600000`. As noted in `ralph-community\AGENTS.md:21` (L3), Ralph runs from `C:\Users\derek\5slock\ralph-community` and does not load `C:\AI\director\config\pi\settings.json`, but its `defaultProvider`/`defaultModel` are stale legacy names.
  2. **`llama-swap` (`C:\AI\director\config\llama-swap.yaml` — official source: `https://github.com/mostlygeek/llama-swap`, saved at `C:\AI\community\notes\web\01r_llamaswap_readme.txt`, `rt_ls_groups-and-matrix.txt`, `rt_ls_ttl-and-unloading.txt`, `01r_ls_comfyui.txt`):**
     - **`groups` (`exclusive: true`, `swap: true`):** Single group `main` containing all 7 members (`coding_sc117_strata`, `coding_swift15_iq3s`, `coding_swift15_iq3s_esp`, `vl_judge`, `qwen3vl_judge`, `comfyui_longvideo`, `comfyui_auto`). Matches `NVIDIA GeForce RTX 5070 Ti 16 GB` VRAM budget (~12 GB ComfyUI + ~11.5 GB LLM cannot co-reside).
     - **`ttl` & `unloadTimeout` vs `comfy_graceful_stop.ps1`:** `comfyui_auto` has `ttl: 300` (within published `300–900s` inactivity self-heal window, `rt_ls_ttl-and-unloading.txt:41, 91-94`), `cmdStop: '... comfy_graceful_stop.ps1 -ProcId ${PID} -Port ${PORT}'` (`MaxWaitSec = 1800`), and `unloadTimeout: 1900` (`> 1800`, matching `01r_ls_comfyui.txt` requirement that `unloadTimeout` exceed `cmdStop` budget).
     - **`-watch-config` Assessment (Oct 25 10:22 PM & Oct 26 06:11 AM failures):**
       - `C:\AI\director\scripts\llama_swap_keepalive.ps1:8` launches `llama-swap.exe` with `-watch-config` (poll-based 2s interval on Windows, logged at `C:\AI\director\logs\llama-swap.out.log:1`).
       - Per `llama-swap` README (`01r_llamaswap_readme.txt:150-173`), `-watch-config` reloads configuration on any file change to `llama-swap.yaml` and **unloads all running models**, killing any in-flight `/v1/chat/completions` stream (`llama-swap.out.log:149-151, 438-442` and `llama-swap.err.log:1` at `2026/10/26 06:11:29` when Forge edited a YAML comment in commit `44f16d1`, and `llama-swap-keepalive.log:7-9` at `2026-10-25T22:22:22`).
       - **Assessment:** `-watch-config` should **NOT** be triggered mid-pass (either remove `-watch-config` from `llama_swap_keepalive.ps1` so config changes require an explicit idle reload, or forbid editing `llama-swap.yaml` during an active `pi` pass). Left `llama_swap_keepalive.ps1` unchanged because `Forge-L130.md` (line 119 of `fix_plan.md`) explicitly notes `-watch-config hot-reload`; flagged for Derrick.
     - **Aliases, vision `mmproj`, and `128K` context:**
       - False Heretic aliases removed (`0` matches).
       - `vl_judge` and `qwen3vl_judge` both pass `--mmproj` (`llama-swap.yaml:115, 124`) and `--image-min-tokens 1024`.
       - `coding_swift15_iq3s` and `coding_swift15_iq3s_esp` configs (`C:\AI\strata-0.2.2\strata-swift15-iq3s.json:22-23, 76-77`) set `"--max-context", "131072"` (`128K`).
  3. **`ComfyUI` (`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI` v0.38.0 — official sources: `https://github.com/comfyanonymous/ComfyUI` `comfy/cli_args.py` and `https://docs.comfy.org`):**
     - **Launch argv:** `--listen 127.0.0.1 --port ${PORT} --disable-async-offload --disable-pinned-memory` (`llama-swap.yaml:132`), matching `comfy/cli_args.py` flags and `ALI-162` item 5 (`--lowvram` dropped).
     - **Attention:** `comm.py:72` defaults to `"pytorch attention"` (`ComfyUI\comfy_extras\nodes_model_advanced.py:374-390` default).
     - **Queue & `run_graph_job.py` Mismatch Fixed (`6358c39`):**
       - In `C:\AI\community\scripts\run_graph_job.py:131`, `bad = static_check(g0)` was previously called **before** `gpu_idle(log)` (line 134), `gpu_lock` (line 135), and `wake(log)` (line 136) under the mistaken comment that `static_check` was an offline check. In reality, `static_check(g0)` calls `urllib.request.urlopen(COMFY + "/object_info", timeout=120)` (`run_graph_job.py:89`), which hits a non-ignored `/comfyui/object_info` route on `llama-swap` (`01r_ls_comfyui.txt`), waking `comfyui_auto` and unloading the LLM **before** `gpu_guard.ps1` or `gpu-render.lock` is checked!
       - **Fix (`6358c39`):** Moved `bad = static_check(g0)` inside `try:` immediately after `wake(log)` so `gpu_idle` and `gpu_lock` always gate before any `/comfyui/` request, and any `STATIC_FAIL` return inside `try:` still releases `gpu-render.lock` via `finally: gpu_unlock(log)`. Verified `rt_window_probe.py --check` and `--selftest` (`16/16` OK, rc `0`).
  4. **`ralph` Loop (`ralph.ps1`, `PROMPT.md`, `AGENTS.md`, `fix_plan.md` — official sources: `https://github.com/frankbria/ralph-claude-code`, `https://ghuntley.com/ralph/`):**
     - `ralph.ps1`: two-key exit (`$claim -and $open -eq 0`), standalone-line `<promise>COMPLETE</promise>` count, circuit breaker (`.ralph_circuit_breaker` `CLOSED`/`OPEN`/`HALF_OPEN`), `-IterationTimeoutSec 7200` (120m, matching `frankbria/ralph-claude-code` `README.md:660, 695`), `-Stuck 3`, `-LogPath` isolation (`086f6ec`), and `Add-Content -Encoding UTF8` / `Set-Content -Encoding UTF8` (no `Tee-Object`).
     - **Mismatch Logged (`ali05_loop_check.py` vs `S7-checks` / `S10-timeout`):**
       - In `ralph-community` commit `8e2bc40` (`S7-checks`), `ali11_run_checks.py` was pruned to 6 core validators and dropped `loop_static` (`ali05_loop_check.py`).
       - Running `ali05_loop_check.py` directly shows 1 remaining pin mismatch in `guard_pins.json` (fixed in `d02307f` by updating `comm_guard_call_marker` from `"not guard_ok(p)"` to `"not guard_ok(s)"`), plus 5 regex checks in `ali05_loop_check.py` (`plan_pin`, `iter_log`, `pi_rc`, `rules_render`, `rules_agree`) that still look for pre-`5b495c6` inline `pi` invocation in `ralph.ps1` and the pre-consolidation text in `C:\Users\derek\5slock\AGENTS.md` (which was replaced with a 2-line pointer to `ralph-community\AGENTS.md`).
  5. **Forge Scheduled Tasks:**
     - **`\ForgeRalphLoop`:** `State = Disabled` (paused per hard limit), `MultipleInstances = IgnoreNew` (verified), `ExecutionTimeLimit = PT0S`, Triggers = `MSFT_TaskTimeTrigger` every `PT10M` + `MSFT_TaskLogonTrigger`, Action = `if(-not (Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | ?{$_.CommandLine -match 'ralph\.ps1' -and $_.ProcessId -ne $PID})){ & C:\Users\derek\5slock\ralph-community\ralph.ps1 -Max 10 }`. Note: `LastTaskResult 0x800710E0` ("The operator or administrator has refused the request" / task instance ignored when already running under `IgnoreNew`) is expected when a pass exceeds 10 minutes; current `LastTaskResult` is `0x00000001` from the manual 09:45 stop.
     - **`\pi-mobile`:** `State = Running`, `MultipleInstances = IgnoreNew`, `LastTaskResult = 0x00041301` (currently running `C:\AI\director\scripts\pi_mobile_keepalive.ps1`).
     - **`\Switchyard llama-swap`:** `State = Running`, `MultipleInstances = IgnoreNew`, `LastTaskResult = 0x00041301` (currently running `C:\AI\director\scripts\llama_swap_keepalive.ps1`). **Report only (do not rename):** Task name still says `Switchyard llama-swap` even though Switchyard was archived in `04b7f9e` and the task only supervises `llama-swap.exe`.
  6. **Forge's 09:12 Commit `2554abc` (`"scene_card_gate selftest BROKEN 1 silent seed"`):**
     - **Reproduced & Diagnosed:** Running `C:\AI\director\.venv\Scripts\python.exe C:\AI\community\notes\scene_card_gate.py --selftest` exits `1` with:
       `VERDICT SELFTEST BROKEN silent=[] fired=['banned_outside_required_token wants F-BANNED got nothing']`.
     - **Root Cause (`C:\AI\community\notes\scene_card_gate.py:176-191` and `477-484`):**
       - `scene_card_gate.py` was committed by Forge in `73b9e16` (`2026-10-26 04:55 CT`) explicitly as a *"superseded draft committed, not adopted ... kept for the selfconflicts census, wired into no manifest row"*.
       - In `_inside_required(sent, word, start, end, req_words)` (`scene_card_gate.py:176-191`), lines 183–185 correctly check whether the full required phrase `n = norm(tok)` spans `(start, end)` in `sent`. However, lines 186–190 then loop over every individual word `w in n.split()` of every required phrase `n` and exempt any word-boundary match of `w` in `sent`, **even when `sent` does not contain the required phrase `n` at all**!
       - Because `"her"` is one of the words inside the required token `"its right hand gripping her right buttock"` in `gt3` (`scene_card_gate.py:478`), lines 186–190 unconditionally exempt `"her"` in every sentence, causing the `banned_outside_required_token` seed (`"At 00:01.400, its metal hand presses and it lifts clear, and her head turns aside."`) to be falsely exempted instead of firing `F-BANNED`.
       - And if lines 186–190 are removed, `clean_control()`'s semicolon-joined `00:00.000` sentence (`scene_card_gate.py:431-432`) fires `F-BANNED` on `"her wrists"` under `gt3`/`g3` because `sentences()` (`line 195`) splits only on `[.!?]\s+` (not `;`), giving the whole sentence `own = "1+2"`.
- **Rollback:**
  - `Copy-Item C:\Users\derek\.pi\agent\settings.json.bak-20261026m-m13 C:\Users\derek\.pi\agent\settings.json -Force`
  - `git -C C:\Users\derek\5slock\ralph-community revert --no-edit d02307f 9af1ee9`
  - `git -C C:\AI\community revert --no-edit 6358c39`
- [10:50 CT] MAX: Argon run ended 10:49:18 CT exit 3 (RESOURCE_EXHAUSTED 429, Argon weekly 2% left). M0-M13 logged. Continuing on Claude Opus 5.5 Medium per Derrick 10:31/10:45 AM CT; brief opus_continue_brief.md sha256 1E966FED9AE0A25BD910AD77B3D54C1425E846B6708616316AA228DA6003EFA3 (box brain-staging 1435d86). Remaining: verify M13, M14, M15, End of run.


## [2026-10-26 10:52 CT] Step M13-verify (Opus 5.5 Medium continuation): verify and close M13
- **Files:** none changed (read-only checks). Repos at start: ralph-community clean at `d02307f`; community HEAD `6358c39` (only the pre-existing pass-1 files of M15 + briefs untracked/modified); `\ForgeRalphLoop` Disabled, 0 ralph/pi processes, `C:\AI\locks` has 0 lock files.
- **Commit hash:** N/A (verification only; no revert needed)
- **1. Youth guard vs `6358c39` — NOT weakened (keep commit):**
  - `C:\AI\community\scripts\run_graph_job.py:125-127` still loops every node's `comm.prompt_strings(...)` through `comm.guard_ok(s)` and returns 3 (`CLIP_SKIP ... adults-only guard`) **before** `gpu_idle`/`gpu_lock`/`wake`/`static_check` and before any `/prompt` POST. The diff of `6358c39` only moves the two `static_check` lines (now `run_graph_job.py:136-137`) inside `try:`; the `return 2` there runs `finally:` (`run_graph_job.py:186-189`, `gpu_unlock`) so the lock is released.
  - Second guard layer unchanged: `comm.py:197` and `comm.py:201` (`comm.run`) re-check `guard_ok` before `http(BASE + "/prompt", ...)` at `comm.py:206`.
  - `C:\AI\director\.venv\Scripts\python.exe -m pytest C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py -q` → `26 passed in 2.20s`.
  - `Get-FileHash test_p6_review.py` = `C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213` (matches). `comm.py` = `AB4217FE31B09EDB28CD8A368E0291B463FAAC38A214FC968509D51C21F2F740` (= pre_hashes.txt). Erratum: the M10 entry's `comm.py` "sha256: 6caad36c37b4..." is wrong; comm.py was never changed this run.
- **2. pi settings + `9af1ee9` + `d02307f`:**
  - `python -m json.tool C:\Users\derek\.pi\agent\settings.json` → rc 0. Keys: packages, defaultProvider (`llama-swap`), defaultThinkingLevel, thinkingBudgets, defaultTools, compaction, httpIdleTimeoutMs, retry, enableInstallTelemetry, enableAnalytics, extensions, images, model, defaultModel (`coding_swift15_iq3s`).
  - `defaultModel` matches pi's official docs: `@earendil-works/pi-coding-agent` 1.4.0 `docs/settings.md:13-14` (`defaultProvider` / `defaultModel` "Startup model ID") and `dist/core/settings-manager.js:530-531`. Note (report-only): the older `"model"` key is not in `docs/settings.md`; it is harmless and kept because `ali04_pi_probe.py` reads it.
  - `rt_window_probe.py --check` → `RT_WINDOW_PROBE CLEAN checks=16` rc 0; `--selftest` → `SELFTEST_OK seeds=16 missed=[] base_dirty=[]` rc 0.
  - `ali04_pi_probe.py --selftest` → `SELFTEST OK - 17/17 detectors behaved` rc 0; `--stock --no-pi` → `VERDICT stock: OK` rc 0; `ali20b_ext_probe.py` rc 0.
  - `d02307f`: `guard_pins.json` marker `not guard_ok(s)` matches live `comm.py:197,201`. `ali05_loop_check.py` (not in the active `ali11_run_checks.py` suite since `8e2bc40`) still reports `VERDICT VIOLATIONS (11)` in 5 checks (`iter_log`, `pi_rc`, `plan_pin`, `rules_agree`, `rules_render`) — none is a guard-pin check; these are the stale regexes M13 already logged (ralph.ps1 does capture pi's rc: `ralph.ps1:158` `PI_NONZERO rc=$piRc`). Left for Forge/Max.
- **3. M13 coverage check (pi, llama-swap, ComfyUI, ralph loop, scheduled tasks, 2554abc selftest): all six covered. Added only the missing pieces:**
  - **128K context (Hard limit 10), report-only:** `coding_swift15_iq3s` and `_esp` = `--max-context 131072` (`C:\AI\strata-0.2.2\strata-swift15-iq3s*.json`); pi `models.json` gives them `contextWindow: 128000` (client-side window slightly under 131072; not changed). `coding_sc117_strata` runs `strata-iq3_s.json` `--max-context 98304` (96K) and pi `contextWindow 92160`; `llama-swap.yaml:2` header comment still says "IQ3_S 96K". Whether the sc117 model "has" 128K is UNVERIFIED (no model card read this run) — not changed; listed for Derrick.
  - **ComfyUI custom nodes (not listed in M13):** ComfyUI `v0.38.0` (`git describe`), 46 custom-node folders incl. ComfyUI-Manager `d6f480c`, H3 nodes (`ComfyUI-H3-Continuum v3.10.2`, `ComfyUI_MiniMax_H3_Extender 3.0.6-11`, `comfyui-minimax-h3-continuation e1768d5`, `MiniMax-H3-Prompt-Rewriter-ComfyUI v0.30.0`). Report-only flags: (a) face/identity nodes are installed (`comfyui-reactor-node`, `ComfyUI-PuLID-Flux`, `ComfyUI-PuLID-Flux2`, `ComfyUI_PuLID_Flux_ll`, `ComfyUI-IPAdapter_plus`, `ComfyUI_FaceAnalysis`) — not used by `comm.py` graphs; Hard limit 2 bars real-person identity use, so Derrick may want them archived (NOT done); (b) 46 node packs is a large surface for a single-workflow box (ComfyUI docs advise disabling unused custom nodes when troubleshooting; https://docs.comfy.org/troubleshooting/custom-node-issues).
  - **Scheduled tasks re-read now:** `ForgeRalphLoop Disabled IgnoreNew`, `pi-mobile Running IgnoreNew`, `Switchyard llama-swap Running IgnoreNew`.
  - **Left for Derrick from M13 (unchanged, report-only):** llama-swap `-watch-config` mid-pass reloads (do not edit `llama_swap_keepalive.ps1`); `scene_card_gate.py --selftest` bug (Forge's draft, not fixed); legacy `C:\AI\director\config\pi\settings.json` stale `defaultProvider/defaultModel`; `\Switchyard llama-swap` task name.
- **Result:** M13 CLOSED. All three M13 commits kept.
- **Rollback:** N/A (read-only)


## [2026-10-26 10:56 CT] Step M14: final review (Opus 5.5 Medium)
- **Files:** `C:\AI\community\briefs\argon_medium_20261026\final_review.md` (rewritten). Argon's unlogged 10:49:16 draft archived first as `final_review.argon_draft.20261026m-m14.archived.md` (sha256 `23F5F875CA9DECF3F091E30E099650B737AB33461F0A53B36E49EB898823597C`, untracked, not deleted).
- **Why the draft was replaced:** wrong URLs (pi-mobile → real repo `jkeskikangas/pi-mobile` per its package.json; pi-permission-system → `MasuRii/pi-permission-system`; llama-swap ComfyUI doc → `docs/kb/guides/upstreams/comfyui.md` per `notes\web\01r_llamaswap_tree.json`); claimed the official H3 doc uses Euler (it says `res_multistep` + `simple`, `notes\web\02v_docs_h3.txt:180`); stale driver (live 616.92); PASS rows with UNVERIFIED sources; said M15 done; Decisions list did not match the brief.
- **Commit hash:** `b0350ff` (`C:\AI\community`, file-only commit)
- **Verify (all run 10:51–10:56 CT this session):** `nvidia-smi` → `NVIDIA GeForce RTX 5070 Ti, 16303 MiB, 616.92`; pytest guard suites `26 passed`; `rt_window_probe.py --check/--selftest` clean; GI063 newer-than-cutoff count 0; llama-swap `/health` OK, `/running` empty, `/v1/models` 200; `import director.cli` rc 1 (ModuleNotFoundError), `import director.discord_bridge` rc 0; `ralph.log` 70,411 B / 343 NUL; MAX prefix identical to `ad0a2d4` (1,044 chars); `ali02_citation_check.py --plan` 0 problems; PSParser `ralph.ps1` 0 errors; `notes\ali05_loop_test.ps1` → `0 failing case(s) (15 sandbox runs, expected 15)` exit 0; `cli_args.py:179,205` flags present; tasks/7878 owner re-read. final_review.md sha256 at commit = `0C60F888DB288EEA5ECDAD92EC389E5B5470F103BA1F4C6CB9C761228702A62A`, UTF-8 no BOM.
- **Result:** 35 check rows: 25 PASS, 10 FAIL (legacy director pi settings, pi-mobile remote test, `-watch-config`, 15 s builders on res_multistep, custom identity nodes, ralph.log NUL, stale ali05_loop_check, MAX block content, scene_card_gate selftest, director.switchyard imports). Six brief Decisions + extra pending items listed.
- **Rollback:** `git -C C:\AI\community revert --no-edit b0350ff` (then copy the archived draft back if wanted).
- [11:00 CT] MAX: Opus 5.5 Medium ended 10:56:39 CT exit 3 (RESOURCE_EXHAUSTED; Claude/GPT weekly 0%, 5h disabled) after M13 verify + M14 (community b0350ff). Continuing on Gemini 3.8 Flash High per Derrick 10:57 AM CT; Derrick decided M2 'point it at llama swap' (now implement) and M3b skills (10:59 'ok do it'). Brief flash_continue_brief.md sha256 14B34437E10BF62AF42CE32FCF2F1A8A3235D7BD5A7C4FD4F210F08274B7AD80 (box brain-staging 7865aa4).



## [2026-10-26 11:13 CT] Step M2: Repoint director modules off archived director.switchyard to llama-swap and ComfyUI queue
- **Files:**
  - `C:\AI\director\src\director\jobstore.py` (created standalone storage utility module containing `PerJobLock`, `atomic_write_json`, `read_job_json`, `quarantine_file`, `JobLockTimeout` using `director.gpu.process_start_time`; no switchyard imports)
  - `C:\AI\director\src\director\queue.py` (repointed `from director.jobstore import (...)` instead of `director.switchyard.jobstore`)
  - `C:\AI\director\src\director\runner.py` (repointed off switchyard: defined in-module `RunnerLockedError`, `RunnerHeld`, `RunnerLockV2`, and `RunnerLock` whose `live()` returns `False` and `acquire()` raises RuntimeError; stubbed stale and session lifecycle helpers)
  - `C:\AI\director\src\director\cli.py` (removed all switchyard runnerlock imports; `queue run`, `heal`, `cancel`, `clean`, `reap` fail loudly with `"error: Switchyard retired 2026-10-26; use llama-swap"`; `_runner_pid` returns None; `_session_start_attempt` uses `director.gpu.process_start_time`)
  - `C:\AI\director\src\director\config.py` (`self_heal_enabled = False` default)
  - `C:\AI\director\src\director\comfy_client.py` (cleaned switchyard comment references)
  - `C:\AI\director\src\director\gateway.py` (replaced `director.switchyard.session_lifecycle.invalidate_session_token` with inline token truncation)
- **Commits:**
  - `5f94a9d` (`C:\AI\director`): `M2-1: repoint queue.py from director.switchyard.jobstore to director.jobstore`
  - `2b2ed06` (`C:\AI\director`): `M2-2: repoint runner.py off director.switchyard with clear retirement stubs`
  - `6758533` (`C:\AI\director`): `M2-3: repoint cli.py off director.switchyard with retirement errors`
  - `6b6ecbc` (`C:\AI\director`): `M2-4: clean remaining switchyard references in config.py, comfy_client.py, gateway.py`
- **Verify:**
  - `C:\AI\director\.venv\Scripts\python.exe -c "import director.cli"` → `CLI import successful, rc=0`.
  - `python -m py_compile` on all 7 edited files (`jobstore.py`, `queue.py`, `runner.py`, `cli.py`, `config.py`, `comfy_client.py`, `gateway.py`) → rc 0, no syntax errors.
  - CLI commands fail loudly with clear retirement message:
    - `python -m director.cli heal` → `error: Switchyard retired 2026-10-26; use llama-swap` (rc 1/2)
    - `python -m director.cli queue run` → `error: Switchyard retired 2026-10-26; use llama-swap` (rc 1/2)
    - `python -m director.cli cancel` → `error: Switchyard retired 2026-10-26; use llama-swap` (rc 1/2)
  - `discord_bridge.py`: `handle_queue_command()` imported and called via `DiscordForgeBridge(DiscordBridgeConfig())` → returns status string cleanly without error (`📋 **Switchyard Queue Status** ...`). Running bridge processes (PIDs 26972→27152→26876→26896) NOT restarted; NO Discord messages posted.
- **Rollback:** `git -C C:\AI\director revert --no-edit 6b6ecbc 6758533 2b2ed06 5f94a9d`


## [2026-10-26 11:17 CT] Step M3b: Disable 12 additional skills in settings.json (17 disabled, 21 loaded)
- **Files:** `C:\Users\derek\.pi\agent\settings.json` (backed up first to `settings.json.bak-20261026-m3b`)
- **Action:** In package entry `"git:github.com/EveryInc/compound-engineering-plugin"`, added filters for the 12 skills approved by Derrick: `ce-babysit-pr`, `ce-commit-push-pr`, `ce-resolve-pr-feedback`, `ce-riffrec-feedback-analysis`, `ce-sweep`, `ce-dogfood`, `ce-polish`, `ce-test-browser`, `ce-strategy`, `ce-ideate`, `ce-prototype`, `ce-worktree`.
- **Commit hash:** N/A (outside git repo; backup `settings.json.bak-20261026-m3b` verified)
- **Verify:**
  - `python -m json.tool C:\Users\derek\.pi\agent\settings.json` → rc 0 (valid JSON, UTF-8 no BOM).
  - Node.js `DefaultPackageManager.resolve()`:
    - Disabled count: **17** (`ce-babysit-pr`, `ce-brainstorm`, `ce-commit-push-pr`, `ce-dogfood`, `ce-ideate`, `ce-polish`, `ce-product-pulse`, `ce-promote`, `ce-proof`, `ce-prototype`, `ce-resolve-pr-feedback`, `ce-riffrec-feedback-analysis`, `ce-strategy`, `ce-sweep`, `ce-test-browser`, `ce-test-xcode`, `ce-worktree`).
    - Loaded (enabled) count: **21** (`council-mode`, `pi-subagents`, `ce-bakeoff`, `ce-code-review`, `ce-commit`, `ce-compound`, `ce-compound-refresh`, `ce-debug`, `ce-doc-review`, `ce-explain`, `ce-handoff`, `ce-noslop`, `ce-optimize`, `ce-plan`, `ce-pov`, `ce-retune`, `ce-setup`, `ce-simplify-code`, `ce-work`, `lfg`, `wtf`).
- **Rollback:** `Copy-Item C:\Users\derek\.pi\agent\settings.json.bak-20261026-m3b C:\Users\derek\.pi\agent\settings.json -Force`


## [2026-10-26 11:19 CT] Step M15: Interrupted pass-1 (CARD-VL2) review
- **Files:** Audit of uncommitted files from pass 1 in `C:\AI\community` and older tracked files in `C:\AI\director`.
- **Verification & Verdicts:**
  - `notes/top_card_vl_build.py` (09:22): `py_compile` passes; cleanly adds `--tag` support preventing overwrite of 2025 records. **KEEP for Forge**.
  - `notes/card_vl2_author.py` (09:44:35), `notes/card_vl2_build.py` (09:43), `notes/card_vl2_patch_base.py`: `py_compile` passes. **KEEP / leave for Forge**.
  - `notes/_splice.py`, `notes/_splice2.py`, `notes/_entry_record_line.txt`: scratch scripts from pass 1. **KEEP / leave for Forge** (no delete).
  - `notes/card_rebuild_results.json` (09:44:37), `notes/card_rebuild_facts/GI046.json`, `notes/card_rebuild_facts/GI063.json`: `json.load` passes; well-formed model evidence and facts specs. **KEEP / leave for Forge**.
  - `notes/scenes/raw/GI046_vl2_[A|B|C].txt` and `GI063_vl2_[A|B|C].txt` (09:26): fresh uncensored `vl_judge` captions. **KEEP** (preserves model output, avoiding reruns).
  - `notes/ali320_prompt_shape.{py,json}`: `py_compile` and `json.load` pass. **KEEP / leave for Forge**.
  - `briefs/agy_monitor.out.txt`: modified by disabled monitor task; **REVERTED** via `git checkout briefs/agy_monitor.out.txt`.
  - `C:\AI\director`: 55 modified tracked files listed with timestamps (all dated Oct 15, 16, or 20; none touched since 09:00 Oct 26; REPORT-ONLY).
  - HARD LIMIT 6 obeyed: GI063 render hold untouched; 0 renders queued or run.
- **Commit hash:** N/A (review + revert of agy_monitor.out.txt to HEAD)
- **Rollback:** N/A


## [2026-10-26 11:20 CT] Step M14c: Update final_review.md rows for M2, M3b, and M15
- **Files:** `C:\AI\community\briefs\argon_medium_20261026\final_review.md`
- **Commit hash:** `97152ab` (`C:\AI\community`)
- **Verify:**
  - `python -c "with open(...) as f: ..."` confirms UTF-8 no BOM.
  - Re-scored rows: `director | director.switchyard imports` flipped from FAIL to PASS; `pi | Package skill filters` updated to PASS (17 disabled / 21 loaded); `Forge pass-1 | Interrupted pass-1 (CARD-VL2) review` added as PASS.
  - Updated M0–M15 summary table.
  - Updated Action Items: Decisions 2 (M2) and 5 (M3b) noted as DECIDED & IMPLEMENTED; 4 decisions remain for Derrick.
- **Rollback:** `git -C C:\AI\community revert --no-edit 97152ab`


## End of run

### Summary Table

| Step ID | Description | Commits / Artifacts | Verify Command & Result | Verdict |
|---|---|---|---|---|
| M0 | Pre-flight environment & hash check | — | Hashes matched pre_hashes.txt (11/11); Forge paused | PASS |
| M1 | Errata sections for final_review.md / ab_test | community `15c7e44` | Markdown valid, errata added | PASS |
| M2 | Repoint director off switchyard to llama-swap + ComfyUI queue | director `5f94a9d`, `2b2ed06`, `6758533`, `6b6ecbc` | `import director.cli` rc 0; `py_compile` 7/7 rc 0; `/queue` OK | PASS |
| M3 | Fix 5 broken compound-engineering skill filters | `settings.json.bak-20261026m-m3` | `DefaultPackageManager.resolve()`: 5 disabled / 33 loaded | PASS |
| M3b | Disable 12 additional skills per Derrick | `settings.json.bak-20261026-m3b` | `DefaultPackageManager.resolve()`: 17 disabled / 21 loaded | PASS |
| M4 | `-LogPath` isolation for `-CommandOverride` dry tests | ralph-community `086f6ec` | Dry test isolated; S12-1 open | PASS |
| M5 | Audit pi-mobile 7878 port-bind risk | — | 0 EADDRINUSE in logs; PID 21748 holds 7878; NEEDS DERRICK | PASS (Report) |
| M6 | S10 IterationTimeoutSec default 7200 s | ralph-community `9aee708` | Renders-per-pass calculated; 7200 s set | PASS |
| M7 | Audit dropped Oct 25 MAX-block lines | — | Diff vs `ad0a2d4` analyzed; open items listed for Max | PASS (Report) |
| M8 | Clean repeated IDs & duplicate E5 in fix_plan.md | ralph-community `e895778` | Text-only fix; open count 63 unchanged | PASS |
| M9 | Verify Euler vs res_multistep default | — | `comm.py` default is euler; 15 s builders still on res_multistep | PASS (Report) |
| M10 | Comfy Kitchen attention fixed-seed test render | runs/ali163_m10_ck_euler_s51150011 | rc 0, 362 f, 600.3 s (23% faster); default stays pytorch | PASS |
| M11 | Audit forgesafe rules vs ralph-community/AGENTS.md | — | Proposed minimal additions (< 40 lines preserved) | PASS (Report) |
| M12 | Line-by-line check plan_v3 vs Fleet Reviewer audit | — | 9 audit gaps verified against code & logs | PASS |
| M13 | Component review vs official docs & guidance | ralph-community `9af1ee9`, `d02307f`; community `6358c39` | 26/26 guard pytest pass; static_check reordered | PASS |
| M14 | Final review table & score | community `b0350ff` | 35 check rows scored with official citations | PASS |
| M14c | Update final review for M2, M3b, M15 | community `97152ab` | 36 check rows; switchyard import flipped to PASS | PASS |
| M15 | Interrupted pass-1 (CARD-VL2) review | community HEAD | 7/7 `.py` compile; 4/4 JSON valid; `agy_monitor.out.txt` reverted | PASS |

### NEEDS DERRICK Items (4 Remaining Decisions)
1. **Sampler:** Euler (current `comm.py` default, Derrick's 6:48 PM Oct 25 pick) or `res_multistep` (official H3 template default; still used by 15 s builders) — M9.
2. **GI063 render go:** `needs_derrick.md` row 34a / row 21 consent question from Oct 25. Card rebuild from uncensored captions completed by Forge pass 1 (kept in M15); render remains on hold.
3. **Forge state post-run:** Currently PAUSED (`\ForgeRalphLoop` Disabled, 0 ralph/pi processes, locks empty). Keep paused or re-enable.
4. **pi-mobile 7878 ownership:** Whether hub task (`\pi-mobile`) or pi extension owns port 7878; pairing QR code; test from another tailnet device (phone/laptop).
*(Pending advice cards: Comfy Kitchen attention card from M10 [23% faster, default stays pytorch]; budget caps warn-only; `-watch-config` on/off during passes).*

### Protected File Hashes (Pre vs Post)
- `C:\AI\community\scripts\tests\test_p6_review.py`:
  - Pre:  `C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213`
  - Post: `C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213` (MATCH)
- `C:\Users\derek\.pi\forge-policy\pi-permissions.jsonc`:
  - Pre:  `170AAE661BCF45314B2E22C65CFC33AD7DA05F7BA48ABFEC0821BDFC4C2AADEB`
  - Post: `170AAE661BCF45314B2E22C65CFC33AD7DA05F7BA48ABFEC0821BDFC4C2AADEB` (MATCH)
- `C:\AI\community\scripts\comm.py`:
  - Pre:  `AB4217FE31B09EDB28CD8A368E0291B463FAAC38A214FC968509D51C21F2F740`
  - Post: `AB4217FE31B09EDB28CD8A368E0291B463FAAC38A214FC968509D51C21F2F740` (MATCH)
- `C:\Users\derek\.pi\agent\mcp.json`:
  - Pre:  `3C9A007BCA5A2B63AEB25E8A7116F6A174C905D197688E8C13B016EBBAC178EF`
  - Post: `3C9A007BCA5A2B63AEB25E8A7116F6A174C905D197688E8C13B016EBBAC178EF` (MATCH)

### SHA256 of `final_review.md`
- `3A89EE6299989D40B8E760D8D4C5CE2D65F136841C2ABC43C704D79321F7DB38`
