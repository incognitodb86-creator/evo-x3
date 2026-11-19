# AlienPc Full-Stack Audit & One-at-a-Time Remediation Plan (v3)

- **Date:** 2026-10-26 07:05 CT (`2026-10-26T07:05:00-05:00`) | **Model:** Gemini 3.8 Flash (High) | **Mode:** `IMPLEMENT MODE`
- **Implementer:** Antigravity on Gemini 3.8 Flash High, per Derrick's 10:16 PM instruction ("After it passes the audit have antigravity flash high implement all the changes and setup forge and optimize or whatever") and 6:01 AM approval ("Ok have it do it").
- **Hardware Baseline (Verified on Disk):** NVIDIA GeForce RTX 5070 Ti (`16,303 MiB` / 16 GB GDDR7 VRAM, compute capability 12.0), cited from [strata-swift15-iq3s.log](file:///C:/AI/strata-0.2.2/strata-swift15-iq3s.log#L21) and [gpu_guard.ps1](file:///C:/AI/director/scripts/gpu_guard.ps1#L95).
- **Last Updated:** 2026-10-26

---

## Derrick's Quoted Answers & Context
- **10:15 PM Oct 25:** *"I don't remember those kitchen attention? I want best practices and community guidance? Geared on what works best on my setup"*
- **10:16 PM Oct 25:** *"After it passes the audit have antigravity flash high implement all the changes and setup forge and optimize or whatever"*
- **10:17 PM Oct 25:** *"Community adults only. I want community fucking swttings"* (Context: In response to negative-prompt handling on avoidance lines: community-standard artifact-only negatives, adults-only guard remains 100% strict on all prompt inputs).
- **5:58 AM Oct 26:** *"Also why are we still using switchyard and not llama swap and them community or whatevet?"*
- **5:59 AM Oct 26:** *"Have antigravity review forge and llama swap and stuff and comfy make sure they are setup and config correctly"*
- **6:00 AM Oct 26:** *"Don't waste usage"*
- **6:01 AM Oct 26:** *"Ok have it do it"*
- **6:48 PM Oct 25:** *"Sort out the Comfy Kitchen attention conflict"*; *"Go back to Euler, 5-second clips and 350–500 word prompts"*

---

## Summary & Audit Response Matrix (Fleet Reviewer Round 2 -> Plan v3)

This v3 plan applies all Fleet Reviewer Round 2 fixes (`N2-1`..`N2-11`), Derrick's quoted answers, and the 12 to-do items from `flash_impl_brief.md`.

| Audit ID / Requirement | How v3 Addresses It (Item / Step ID) | Live Evidence & Resolution |
| :--- | :--- | :--- |
| **N2-1** (Implementer: Flash High) | Flash High implements all steps under AlienPc lease & `gpu_guard.ps1` rc 0. Step IDs used in commits & `progress.md`. | Replaces "Owner: Forge". Commits in respective repos (`community`, `ralph-community`, `director`). |
| **N2-2** (Euler vs `res_multistep`) | Step 9(b): `res_multistep` is an approved A/B test vs Euler on seed `51150011`. Euler remains default unless Derrick decides. | Honors Derrick's 6:48 PM "Go back to Euler". Technical metrics only; no vision judge. |
| **N2-3** (Split Step 1: Guard Scope & Negatives) | Split into **Step 1a** (`run_graph_job.py` + `comm.py` + `tests/test_guard_scope.py`) and **Step 1b** (Continuum `no:` lines artifact-only negatives). | `guard_ok` scope expands to all prompt-bearing inputs (`prompt`, `text`, `prompt_1..6`, `clips_json`, `sequence_prompt`, `value`). `test_p6_review.py` sha unchanged. `no:` lines: artifact-avoidance tokens only. |
| **N2-4** (Split Step 6: Strata vs Judge Params) | Split into **Step 6a** (Strata `max_tokens: 3000`) and **Step 6b** (VL judge request params `reasoning_effort="none"`). | `p6_review.guard_check` is NEVER edited. Verify runs `pytest test_p6_review.py test_guard_scope.py` + sha check on `test_p6_review.py`. |
| **N2-5** (Switchyard not merged -> Retire Switchyard) | Step 12(b) replaced by complete Switchyard retirement (To-do 8): search callers, repoint to llama-swap & ComfyUI /prompt via `comm.py`, archive folder to `C:\AI\_archive\20261026_switchyard\`. | Resolves Derrick's 5:58 AM question ("why are we still using switchyard"). No merge, no flags. |
| **N2-6 / R2-2** (Comfy Kitchen -> Community Default) | Step 8 rests on official H3 documentation default (`"pytorch attention"`), NOT convrot claim. Re-read header: 195 `comfy_quant` entries, `convrot` = False. | Supercedes Oct 9 KEEP per Derrick's 10:15 PM answer. Validated by 1 check render on seed `51150011` under `gpu_guard.ps1` rc 0. |
| **N2-7** (Measure render times before timeout) | Step 10(3): Measure all `p7/jobs/*.result.json` render durations & renders/pass. Set timeout = renders/pass * max_render + queue_time. Timeout kills whole process tree & frees GPU lock. | Verified by AST parse (0 errors) and forced short timeout dry pass. |
| **N2-8** (Judgment gaps resolved) | Step 9(a) split into 2 variables (`ref_image_size` alone, then `MiniMaxH3AddGuide` alone). Step 10 names all disabled skills. Step 11: `--pool-workers 13` selected with technical rationale; vector sweep deferred. Step 2 checks both `settings.json` files. Step 4 drops `<10s` from verify. | Strict one-variable-per-render methodology; explicit skill names; robust verification. |
| **N2-9 / N2-11** (Quoted answers & Header time) | Derrick's words quoted as answers; header timestamp synchronized. | Accurate attribution and chronological consistency. |
| **N2-10** (Persistent pi-mobile over Tailscale) | Step 11(3): pi-mobile configured as persistent background service on port 7878. Tested via `tailscale serve` (`https://<tailnet>:8443`). | Solves ephemeral listener drop between passes. Derrick retains QR pairing. |
| **To-do 4** (Vision models in models.json) | Step 11(2): Add uncensored vision models already in `llama-swap.yaml` (`Defiant Fable Heretic 9B` with mmproj, `qwen3-vl-8b-abliterated`) to `.pi\agent\models.json` with input `["text", "image"]`. | No downloads. Exact llama-swap IDs used. |

---

## Part 1: Top 10 Root Causes (Audit Verified)

1. **Adults-Only Guard (`comm.guard_ok`) Key-Scope Gap & Unguarded `/prompt` Script:** `comm.py:186-191` and `run_graph_job.py:124-126` only inspected `n["inputs"].get("prompt")`, missing 94 prompt-bearing inputs across 164 saved graphs (`CLIPTextEncode.text`, `prompt_1..6`, `clips_json`, `sequence_prompt`, `value`). `notes\ali173_pw1d_run.py:373-382` posted directly to `:10004/prompt` without `comm.guard_ok`.
2. **Runaway Custom Gate & Seeded-Fault Probes:** Mandated custom probes (`notes/ali11_run_checks.py`) ran 33 scripts with >10,000s timeouts, generating unnecessary friction against Derrick's "Add nothing custom" rule.
3. **Brittle Line-Numbered Plan Generator:** `ali14d_shortplan_build.py` line-numbering and receipt requirements caused cascade errors whenever `fix_plan.md` was edited.
4. **Duplicate & Conflicting `AGENTS.md` Files:** Parent `5slock/AGENTS.md` and child `ralph-community/AGENTS.md` injected conflicting directives and rules.
5. **Ping-Pong on `llama-swap.yaml` Groups:** Contradictory attempts to force `comfyui_auto` into a persistent group caused VRAM contention risks on a 16 GB card.
6. **Turn-1 Context Window Bloat:** Loading uncompacted notes, duplicate instructions, and 38 unused skills consumed ~70-94K tokens before turn 1 started.
7. **Thinking Token Truncation Misidentified as Refusals:** VL models emitting `reasoning_content` exceeded the 300 `max_tokens` ceiling in Strata, resulting in truncated, blank captions.
8. **Strata Vision VRAM Constraints:** Running vision on GPU at high context risked OOM; Strata CPU vision provides reliable fallback while preserving 128K context.
9. **Comfy Kitchen Attention vs Community Default:** Checkpoint `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` contains 195 `.comfy_quant` entries (no `convrot` string in header). Official H3 documentation specifies `"pytorch attention"` as the default baseline.
10. **Unchecked Pass Timeouts and Ephemeral pi-mobile:** Lack of process tree kill on timeout risked stranded GPU locks; pi-mobile died whenever a one-shot pass ended.

---

## Part 2: Prioritized Action Plan & Step Specifications

Every step below is executed in order by Antigravity Flash High, with one commit per change, logging each in `progress.md`.

### Step 0 (`S0`, P0): Gate `ali173_pw1d_run.py` Through `comm.guard_ok` and `comm.BASE`
- **Step ID:** `S0`
- **File:** `C:\AI\community\notes\ali173_pw1d_run.py`
- **Change:** Import `comm` from `C:\AI\community\scripts`, replace direct `127.0.0.1:10004` calls with `comm.BASE` (`/comfyui`), and validate `SHORT_PROMPT` and every graph string through `comm.guard_ok` before posting to `/prompt`.
- **Verify:** `python -m py_compile C:/AI/community/notes/ali173_pw1d_run.py` and test dry execution without submitting a real render.
- **Rollback:** `git -C C:/AI/community checkout -- notes/ali173_pw1d_run.py`
- **Commit:** In `C:\AI\community`: `S0: gate ali173_pw1d_run.py through comm.guard_ok and comm.BASE`

### Step 1a (`S1a`, P0): Widen `guard_ok` Key Scope in `run_graph_job.py` and `comm.py`
- **Step ID:** `S1a`
- **Files:** `C:\AI\community\scripts\run_graph_job.py`, `C:\AI\community\scripts\comm.py`, `C:\AI\community\scripts\tests\test_guard_scope.py`
- **Change:** Expand pre-render `guard_ok` check loop to inspect all prompt-bearing inputs (`prompt`, `text`, `prompt_1..6`, `clips_json`, `sequence_prompt`, `value`). Add unit tests in `test_guard_scope.py`. Never edit `test_p6_review.py` or `p6_review.guard_check`.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe -m pytest C:/AI/community/scripts/tests/test_p6_review.py C:/AI/community/scripts/tests/test_guard_scope.py`. Confirm `test_p6_review.py` SHA256 matches `pre_impl_hashes.txt`.
- **Rollback:** `git -C C:/AI/community checkout -- scripts/run_graph_job.py scripts/comm.py scripts/tests/test_guard_scope.py`
- **Commit:** In `C:\AI\community`: `S1a: widen guard_ok key scope to all prompt-bearing inputs and add test_guard_scope`

### Step 1b (`S1b`, P0): Continuum `no:` Lines to Community Artifact-Only Negatives
- **Step ID:** `S1b`
- **Files:** Continuum prompt generation scripts / builders in `C:\AI\community\notes\` and `ralph-community`
- **Change:** Update Continuum V39 `no:` negative avoidance lines to use community artifact-avoidance tokens only (`no: watermark, text overlay, logos, extra limbs, deformed hands, blurry, camera cuts`). Guard remains 100% strict on all positive and negative prompt inputs.
- **Verify:** `py_compile` on modified scripts; run `test_guard_scope.py` to ensure no false blocks.
- **Rollback:** `git checkout` on modified files.
- **Commit:** `S1b: update Continuum no: lines to community artifact-only negatives`

### Step 2 (`S-pi` Part 1, P0): Consolidate `AGENTS.md`, Clean `STANDING.md`, Verify F12 Disabled
- **Step ID:** `S-pi-agents`
- **Files:** `C:\Users\derek\5slock\AGENTS.md`, `C:\Users\derek\5slock\ralph-community\AGENTS.md`, `C:\Users\derek\.pi\agent\pi-hermes-memory\STANDING.md`
- **Change:**
  - Back up `C:\Users\derek\5slock\AGENTS.md` as `notes/AGENTS.20261025.archived.md`. Replace with 1-line pointer to `ralph-community/AGENTS.md`.
  - Update `C:\Users\derek\5slock\ralph-community\AGENTS.md` to ensure length is <= 40 lines and all paths exist.
  - Back up and clean `C:\Users\derek\.pi\agent\pi-hermes-memory\STANDING.md`.
  - Check BOTH `C:\Users\derek\.pi\agent\settings.json` and `C:\AI\director\config\pi\settings.json` for F12 extensions (`headless-guard`, `protected-paths`). Confirm absent or disabled.
- **Verify:** `(Get-Content C:\Users\derek\5slock\AGENTS.md).Count -le 3`; `(Get-Content C:\Users\derek\5slock\ralph-community\AGENTS.md).Count -le 40`; F12 regex search returns 0 hits in both settings files.
- **Rollback:** Restore backups.
- **Commit:** In `ralph-community`: `S-pi-agents: consolidate duplicate AGENTS.md, clean STANDING.md, verify F12 disabled`

### Step 3 (`S7-trim` Part 1, P0): Restore Plain Markdown `fix_plan.md` & Retire Shortplan Generator
- **Step ID:** `S7-fixplan`
- **Files:** `C:\Users\derek\5slock\ralph-community\fix_plan.md`, `C:\Users\derek\5slock\ralph-community\notes\ali14d_shortplan_build.py`
- **Change:**
  - Back up `fix_plan.md` to `notes/plans/fix_plan.20261025.archived.md`.
  - Restore full text of the six truncated items (`ORC-ROBOT`, `H3-RESEARCH`, `NOW-P3`, `AUD1`, `ALI-173-STORYBOARD`, `SUBJECT-LABELS`) from git commit `3fcafbb:fix_plan.md`.
  - Archive completed rows into `notes/plans/completed_archive_20261025.md`.
  - Keep `fix_plan.md` as plain clean markdown. Retire the automatic `--emit` rewrite in `ali14d_shortplan_build.py`.
- **Verify:** `fix_plan.md` size < 15 KB; all open items preserved with complete descriptions.
- **Rollback:** Restore backup.
- **Commit:** In `ralph-community`: `S7-fixplan: restore plain markdown fix_plan.md from git 3fcafbb and retire shortplan generator`

### Step 4 (`S7-trim` Part 2, P0): Prune `ali11_run_checks.py` to Core Project Validators
- **Step ID:** `S7-checks`
- **Files:** `C:\Users\derek\5slock\ralph-community\notes\ali11_run_checks.py`, `C:\Users\derek\5slock\ralph-community\PROMPT.md`
- **Change:**
  - Back up `notes/ali11_run_checks.py` to `notes/ali11_run_checks.20261025.archived.py`.
  - Remove seeded-fault probe requirements from `PROMPT.md`.
  - Pare `ali11_run_checks.py` down to real validators: `pytest`, `py_compile`, `json.tool`, `check_web_saves.py`, `rt_window_probe.py --check`.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe notes/ali11_run_checks.py` returns rc 0; log execution time.
- **Rollback:** Restore backup.
- **Commit:** In `ralph-community`: `S7-checks: prune ali11_run_checks.py to core project validators and drop seeded-fault probes`

### Step 5 (`S7-trim` Part 3, P0): Align `rt_window_probe.py` and `AGENTS.md` with `llama-swap.yaml` `groups.main`
- **Step ID:** `S7-groups`
- **Files:** `C:\Users\derek\5slock\ralph-community\notes\rt_window_probe.py`, `C:\Users\derek\5slock\ralph-community\AGENTS.md`
- **Change:** Ensure `RT_GROUP` validation checks that `comfyui_auto` resides in `groups.main` (`swap: true, exclusive: true`) with `ttl: 300` and `unloadTimeout: 1900`, matching `llama-swap.yaml:30-41`.
- **Verify:** Under `gpu_guard.ps1` rc 0, run `C:/AI/director/.venv/Scripts/python.exe notes/rt_window_probe.py --check` (rc 0).
- **Rollback:** `git checkout` on modified files.
- **Commit:** In `ralph-community`: `S7-groups: align rt_window_probe.py and AGENTS.md with llama-swap groups.main`

### Step 6a (`S6a`, P0): Strata Max Tokens Configuration
- **Step ID:** `S6a`
- **Files:** `C:\AI\strata-0.2.2\strata-swift15-iq3s.json`
- **Change:** Back up to `.bak-20261026-s6a`. Update `"max_tokens": 300` to `"max_tokens": 3000` to allow full response completion.
- **Verify:** `python -m json.tool C:/AI/strata-0.2.2/strata-swift15-iq3s.json > $null`.
- **Rollback:** Restore backup.
- **Commit:** Non-git file: backup logged in `progress.md`.

### Step 6b (`S6b`, P0): VL Judge Reasoning Configuration
- **Step ID:** `S6b`
- **Files:** `C:\AI\community\scripts\p6_review.py` (call parameters only, NEVER `guard_check`), `C:\AI\community\notes\ali163_vision_probe.py`
- **Change:** Configure VL judge calls to pass `reasoning_effort="none"` / `chat_template_kwargs: {"enable_thinking": false}`. `guard_check` in `p6_review.py` is UNTOUCHED. Vision describes scene/lighting/composition only; NEVER decides age or identity.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe -m pytest C:/AI/community/scripts/tests/test_p6_review.py C:/AI/community/scripts/tests/test_guard_scope.py`. Confirm `test_p6_review.py` SHA256 matches `pre_impl_hashes.txt`.
- **Rollback:** `git -C C:/AI/community checkout -- scripts/p6_review.py`
- **Commit:** In `C:\AI\community`: `S6b: configure reasoning_effort none for VL judge requests without modifying guard_check`

### Step 7 (`S7-vision`, P0): Strata 128K Context with CPU Vision Fallback
- **Step ID:** `S7-vision`
- **Files:** `C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json`
- **Change:** Back up to `.bak-20261026-s7`. Ensure `"vision": {"gpu": false, "max_tokens": 3000}` uses `strata-vision.exe` on CPU while 128K context (`131072`) stays in VRAM. Headroom remains >= 1024 MiB.
- **Verify:** Check config validity with `json.tool`.
- **Rollback:** Restore backup.
- **Commit:** Non-git file: backup logged in `progress.md`.

### Step 8 (`S8`, P0): Comfy Kitchen Attention -> Community Default (`"pytorch attention"`)
- **Step ID:** `S8`
- **Files:** `C:\AI\community\scripts\comm.py`
- **Change:**
  - Verify GPU idle via `gpu_guard.ps1` rc 0.
  - Run ONE fixed-seed check render on seed `51150011` with `attention="pytorch attention"` via `run_graph_job.py`.
  - Validate render technically (no errors, valid mp4, non-zero file size, no blank frames).
  - Update `comm.py` default `m_attn` from `"comfy kitchen attention"` to `"pytorch attention"` (official H3 docs default).
  - Log: "Oct 9 KEEP superseded 2026-10-26 (Derrick 10:15 PM: community best practice)".
- **Verify:** `pytest` on guard test files; `py_compile C:/AI/community/scripts/comm.py`.
- **Rollback:** `git -C C:/AI/community checkout -- scripts/comm.py`
- **Commit:** In `C:\AI\community`: `S8: set comm.py ModelAttentionBackend default to pytorch attention`

### Step 9a (`S9a`, P1): H3 Reference Sizing & Guide Frame Anchor
- **Step ID:** `S9a`
- **Files:** `C:\AI\community\scripts\comm.py`
- **Change:** Split into 2 individual variables:
  - (1) Test `ref_image_size="match"` on seed `51150011`.
  - (2) Test `MiniMaxH3AddGuide` on seed `51150011`.
  - Record technical metrics in `progress.md`. Update `comm.py` only if community default is verified with no KEEP conflict.
- **Verify:** Technical render checks; `pytest`.
- **Rollback:** `git -C C:/AI/community checkout -- scripts/comm.py`
- **Commit:** In `C:\AI\community`: `S9a: update comm.py reference sizing and guide defaults`

### Step 9b (`S9b`, P1): Approved A/B Test: `res_multistep` vs `euler`
- **Step ID:** `S9b`
- **Files:** Evaluation notes in `C:\AI\community\briefs\argon_audit_20261025\`
- **Change:** Execute A/B test on seed `51150011` comparing `res_multistep` against `euler` under `gpu_guard.ps1` rc 0. Record technical stats (runtime, frame validity). Euler remains default per Derrick's 6:48 PM direction unless Derrick chooses otherwise.
- **Verify:** Log comparative technical metrics in `progress.md`.
- **Rollback:** N/A (configuration default remains Euler).
- **Commit:** In `C:\AI\community`: `S9b: record A/B test metrics for res_multistep vs euler on seed 51150011`

### Step 10 (`S10`, P1): Rotate Progress, Non-Blocking Budget Counter, Process-Tree Timeout
- **Step ID:** `S10-1`, `S10-2`, `S10-3`
- **Files:**
  - `S10-1`: `ralph-community/notes/progress.md`, `C:\Users\derek\.pi\agent\settings.json`
  - `S10-2`: `C:\AI\community\scripts\run_graph_job.py`
  - `S10-3`: `C:\Users\derek\5slock\ralph-community\ralph.ps1`
- **Change:**
  - `S10-1`: Copy `progress.md` to `progress_archive_20261026.md`. Retain latest 20 entries. Disable unused skills by name in `settings.json` (backup `.bak-20261026-skills`): `compound-engineering-plugin:brainstorming`, `compound-engineering-plugin:content-creator`, `compound-engineering-plugin:social-media`, `compound-engineering-plugin:seo-analyzer`, `compound-engineering-plugin:copywriting`.
  - `S10-2`: In `run_graph_job.py`, atomically increment `used_min` and `jobs` in `logs/p7_budget.json` in `finally` block (counter only, zero refuse-on-cap gate).
  - `S10-3`: Measure all `p7/jobs/*.result.json` durations. Calculate timeout = renders/pass * max_duration + queue_time. Implement timeout in `ralph.ps1` that terminates entire pi process tree, then executes `comfy_graceful_stop.ps1` or verifies `gpu-render.lock` release.
- **Verify:** AST parse of `ralph.ps1` (0 errors); dry run test of timeout mechanism; `json.tool logs/p7_budget.json`.
- **Rollback:** Restore backups.
- **Commit:**
  - `S10-1: rotate progress.md and disable unused marketing skills`
  - `S10-2: add non-blocking budget counter to run_graph_job.py`
  - `S10-3: implement process-tree iteration timeout with lock release in ralph.ps1`

### Step 11 (`S11`, P1 / P2): Models.json Vision Setup, ESP Sync, and Persistent pi-mobile
- **Step ID:** `S11-1`, `S11-2`, `S11-3`
- **Files:**
  - `S11-1`: `C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json`
  - `S11-2`: `C:\Users\derek\.pi\agent\models.json`
  - `S11-3`: Scheduled Task / Service config for pi-mobile
- **Change:**
  - `S11-1`: Sync `args` with `args_written` (`--pool-workers 13` because 13 matches host core thread allocation without thread starvation). Defer control-vector sweep.
  - `S11-2`: Add uncensored vision models defined in `llama-swap.yaml` (`Defiant Fable Heretic 9B` with mmproj, `qwen3-vl-8b-abliterated`) to `models.json` with input `["text", "image"]`.
  - `S11-3`: Configure `pi-mobile` as persistent service on port 7878 over Tailscale. Verify listener and run HTTPS status probe via `tailscale serve` (`https://<tailnet>:8443`). QR pairing is left for Derrick.
- **Verify:** `json.tool` on `models.json` and `strata-swift15-iq3s-esp.json`; `Get-NetTCPConnection -LocalPort 7878 -State Listen`; HTTPS probe returns status code.
- **Rollback:** Restore backups.
- **Commit:** In `ralph-community`: `S11: configure vision models in models.json, sync strata args, and setup persistent pi-mobile`

### Step 12 (`S12`, P2): Retire Switchyard, Clean Ralph Log, Verify Discord Bridge
- **Step ID:** `S12-1`, `S12-2`, `S12-3`
- **Files:**
  - `S12-1`: `C:\Users\derek\5slock\ralph-community\logs\ralph.log`
  - `S12-2`: `C:\AI\community\briefs\argon_audit_20261025\discord_bridge_status.md`
  - `S12-3`: `C:\AI\community\briefs\argon_audit_20261025\switchyard_callers.md`, Switchyard directories
- **Change:**
  - `S12-1`: Copy `logs/ralph.log` to `logs/ralph.log.bak-20261026` first, then strip NUL (`0x00`) bytes (UTF-8 no BOM).
  - `S12-2`: Check `discord_bridge` process tree. Confirm watchdog + worker represents single launcher chain; stop nothing if no duplicate.
  - `S12-3`: Find every caller of Switchyard across director, scripts, tasks, settings. Write list to `switchyard_callers.md`. Repoint model swapping to llama-swap and renders to ComfyUI /prompt via `comm.py`. Move Switchyard folder to `C:\AI\_archive\20261026_switchyard\`. Verify llama-swap `/v1/models` and ComfyUI `/system_stats` respond.
- **Verify:** `Test-Path logs/ralph.log.bak-20261026`; 0 NUL bytes; `switchyard_callers.md` complete; Switchyard archive verified.
- **Rollback:** Restore Switchyard from archive if needed.
- **Commit:**
  - `S12-1: sanitize ralph.log with backup`
  - `S12-3: retire switchyard and archive callers`

---

## Part 3: What Is Missing (Information Needed & Handled)
1. **Swift 1.5 Specific Refusal Vector:** Deferred until after all guard and attention changes are verified.
2. **Derrick's Quoted Directives:** Incorporated directly into plan v3.
3. **QR Pairing for pi-mobile:** Derrick performs manually via phone scan.

---

## Part 4: Conflicts Resolution
1. **`comfyui_auto` Group:** Kept in `groups.main` (`exclusive: true`) to avoid 16 GB VRAM OOM.
2. **Render Queue Route:** All renders route through `run_graph_job.py` / `comm.py` with full `guard_ok` validation.
3. **H3 Attention:** Switched to `"pytorch attention"` per official H3 docs and community standard.
4. **Switchyard vs llama-swap:** Switchyard fully retired to `_archive`; llama-swap is the single model supervisor.

---

## Part 5: Implementation Rules & Safety Boundaries
1. **Secrets:** Never touch, print, or log credentials, tokens, or `.env` files.
2. **GPU Lock:** Any GPU-dependent operation must check `gpu_guard.ps1` rc 0.
3. **Youth Guard:** Fictional adults 21+ only. `guard_ok` is never loosened. `test_p6_review.py` is never edited.
4. **No Vision Judge on Rendered Explicit Output:** Technical criteria only.
5. **No Deletes:** Archive only.
6. **128K Context:** Preserved across all models.
7. **One Change Per Commit:** Clear step IDs in commit messages and `progress.md`.
