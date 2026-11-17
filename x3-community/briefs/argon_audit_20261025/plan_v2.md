# AlienPc Full-Stack Audit & One-at-a-Time Remediation Plan (v2)

- **Date:** 2026-10-25 22:47 CT (`2026-10-25T22:19:33-05:00`) | **Model:** Gemini 4 Argon (High) | **Mode:** `PLAN MODE - nothing changed`
- **Hardware Baseline (Verified on Disk):** NVIDIA GeForce RTX 5070 Ti (`16,303 MiB` / 16 GB GDDR7 VRAM, compute capability 12.0), cited from [strata-swift15-iq3s.log](file:///C:/AI/strata-0.2.2/strata-swift15-iq3s.log#L21) and [gpu_guard.ps1](file:///C:/AI/director/scripts/gpu_guard.ps1#L95).
- **Last Updated:** 2026-10-25

---

## Summary & Audit Response Matrix (Fleet Reviewer Round 1 -> Plan v2)

This v2 plan resolves all findings (`A-1`..`A-10`, `K-1`, `K-2`, `G-1`), Section 7 fixes (`Fix 1`..`Fix 12`), and Section 8 AlienPc checks (`S8-1`..`S8-10`) from [fleet_audit.md](file:///C:/AI/community/briefs/argon_audit_20261025/context/fleet_audit.md#L1-L266), applying Derrick's 10:15 PM and 10:17 PM CT rules ([revise_brief.md](file:///C:/AI/community/briefs/argon_audit_20261025/revise_brief.md#L6-L7): *"I want best practices and community guidance? Geared on what works best on my setup"* and *"Community adults only. I want community fucking swttings"*). Nothing on AlienPc was modified during this run.

| Finding / Fix / S8 Check ID | How v2 Addresses It (Item / Step ID) | Or Why Not, With Live Evidence (`path:line`) |
| :--- | :--- | :--- |
| **A-1 / Fix 1 / S8-6** (P0: unguarded `/prompt` script) | Added **Step 0 (`A6-01a`)** first. Forge gates `ali173_pw1d_run.py` through `comm.guard_ok` and `comm.BASE` (`/comfyui`). Interim rule: `ali173_pw1d_run.py` is unused until Step 0 lands. | Grep of all `.py` files found only 2 `/prompt` callers: `comm.py:195` (guarded at `L188-191`) and `notes\ali173_pw1d_run.py:373,382` (unguarded on `:10004` at `L39`). |
| **A-2 / Fix 2 / S8-2** (P1: adults-only gap ordered 5th) | Moved `A6-01` to front as **Step 0 (`A6-01a`)** and **Step 1 (`A6-01b`)**. Interim rule: no renders run until Steps 0–1 pass verification. | `scripts\run_graph_job.py:124-126` and `scripts\comm.py:186-191` inspect only `n["inputs"].get("prompt")`. |
| **A-3 / Fix 3** (P1: `negative_prompt` / `no:` lines vs `guard_ok`) | Scanned all **164 saved ComfyUI API graphs** in report mode. In **Step 1 (`A6-01b`)**, `comm.guard_ok` stays 100% strict; Continuum `no:` lines use artifact tokens only (`no: watermark, extra limbs...`), and any negative-key policy change is a card to Derrick. New tests go in `tests/test_guard_scope.py` (`test_p6_review.py` untouched). | Across 164 graphs: **0 hits** on positive descriptions; **2 hits** on `PrimitiveStringMultiline.inputs.value` (`node 188` in `runs\ali173_cont_hc1_s51140001\ali173_cont_hc1_s51140001.api.json:188` & `request.api.json`) from a `no: ... minors, underage ...` avoidance line (`ali10_adults_probe.py:99-100`). |
| **A-4 / Fix 4** (P1: step owner, rollback, commit log) | Every step in **Part 5 (Steps 0..12)** uses the audit template as a `fix_plan.md` item: **Owner: Forge**, **Gate**, **One Change**, **Verify**, **Rollback**, and **Log/Commit**. Antigravity and Max do not edit Forge's files. | `ralph-community\ralph.ps1:45-90`, `PROMPT.md:1-25`. |
| **K-1 / A-5 / Fix 5 / S8-1,2,3,10** (`llama-swap.yaml:97`, live argv, `comm.py` `attention=`, `int8_convrot`, Oct 9 KEEP, ALI-162) | **Dropped CLI half** of `A6-02` and Root Cause 9 (already removed by ALI-162). Kept the graph-level `comm.py` `attention="comfy kitchen attention"` fix as **Step 8 (`A6-02`)**. Noted Derrick's Oct 9 `ck-attention` KEEP (`production-defaults-st8-dynamic-vram.md:5`) and applied his Oct 19 & Oct 25 10:15 PM rule: official H3 docs state Comfy Kitchen cannot run `int8_convrot` checkpoints, so Step 8 validates `"pytorch attention"` on seed `51150011` under **Derrick's GO**. | `Select-String` on `config\llama-swap.yaml:97` has **0 hits** for `lowvram|use-ck-attention` (`cf1_setup_audit_20261024.md:51-75`); live ComfyUI `main.py` procs = 0. `comm.py:75,84,123` sets `attention="comfy kitchen attention"`. Safetensors header of `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` has 195 `.comfy_quant` tensors with `{"format": "int8_tensorwise", "convrot": true, "convrot_groupsize": 256, "per_row": true}`. Cited in `02v_docs_h3.txt:80,201` and `ali173_b2_obj_ModelAttentionBackend.json:1`. |
| **A-6 / Fix 6** (P1: `A3-04` budget cap over-control) | Changed **`A3-04` (Step 10)** to a **non-blocking counter only** (`used_min` and `jobs` incremented in `logs/p7_budget.json` after each render). **No refuse-on-cap gate** in `run_graph_job.py`. | `ralph-community\logs\p7_budget.json:1-7` (`472.9 min / 38 jobs`), `run_graph_job.py:185-190`. |
| **A-7 / Fix 7** (P2: refusal-vector order; vision boundary) | Ordered **`A1-04` (Step 11)** strictly after Steps 0–1 (`A6-01a/b`) are verified. Stated in `A1-02..A1-04`: vision captions describe scene/lighting/action only (**vision never decides identity or age**; adult status comes from canon + `comm.guard_ok`; celebrity/real-person LoRAs are prohibited). | `ralph-community\notes\refusal_vector_test_20261025.md:51-130`, `derricks-standing-rules.md:11`. |
| **A-8 / Fix 8 / S8-7** (P2: drop custom scanner; size timeout) | **Dropped** the custom PowerShell secret scanner per Derrick's 10:17 PM rule. Measured all 39 `p7/jobs/*.result.json` files and set `ralph.ps1` per-iteration timeout in **Step 10 (`A2-01`)** to **`4500s` (75 min)** (`> 3,048s + 1,200s` queue timeout). | Max render across 39 `p7\jobs\*.result.json` is **`50.80 min` (`3,048s`)** in `ali147_pool_fix4_s51080000.result.json:1` (next: `47.00 min`, `46.60 min`). `ralph.ps1:65`. |
| **A-9 / Fix 9 / S8-5** (P2: F12 guard extensions) | Added **`A2-03` (Verified Disabled on Disk)** and a check in **Step 2** so they remain absent. | Absent from live `.pi\agent\settings.json:59-61` (`extensions: ["-builtin:llama.cpp"]`) and `config\pi\settings.json:33-36`; renamed on disk to `headless-guard-and-truncate.ts.disabled-2026-10-25` (67,476 B) and `protected-paths.ts.disabled-2026-10-25` (10,242 B) in `C:\AI\director\.pi\extensions\`. |
| **K-2 / Fix 10 / S8-4** (`f7d3fad`/`fd426b8` vs `:7878` during/between passes) | Replaced v1's assertion with the 3-part test in **`A2-02` (Step 11)**. Verified live both **during** and **after** a Forge pass: `:7878` is bound by `pi --print` during a pass and closes when the pass exits (`"PM2"` is task ID `"Pi-Mobile 2"`, not `pm2`). | `git show --stat f7d3fad fd426b8` wrote `~/.pi/agent/pi-mobile/config.json` (`{"port": 7878, "enabled": true}`) + `tailscale serve 7878` (`https://<tailnet>:8443 -> http://127.0.0.1:7878`). At `22:19:33 CT` while `ralph.ps1` (`PID 31688`) ran `pi --print` (`PID 5956`), `:7878` was `LISTENING` on `PID 5956`; at `22:23:25 CT` after `PID 5956` exited, `netstat -ano` showed **0 listeners on `:7878`** (`pi_mobile_live_20261025.md:7-35`). |
| **G-1 / Fix 11 / S8-8,9** (Gating: Derrick's go, `gpu_guard.ps1`, `ralph.log` copy, `discord_bridge`, Switchyard) | Added **Derrick's GO** gates to `comm.py` steps (`Steps 1, 8, 9`), `discord_bridge` stop (`Step 12`), and Switchyard flags (`Step 12`). Added `gpu_guard.ps1` rc 0 check to `Steps 5..9, 11`. Added `Copy-Item logs/ralph.log logs/ralph.log.bak-20261025` before NUL-stripping (`Step 12`). | `Get-CimInstance Win32_Process` proved `PID 26972` (`.venv` watchdog) -> `PID 27152` (`Python312` watchdog) -> `PID 26876` (`.venv` worker) -> `PID 26896` (`Python312` worker) is **one** Windows venv launcher chain. Switchyard commits `d9efd2f..b6384bc` (`DONE.md:1-17`, `CHANGES.md:80-152`) are **already merged** in `C:\AI\director` (`HEAD=36dadae`, 20/20 unit tests pass in `3.13s`). |
| **A-10 / Fix 12** (P3: `<tailnet>`, 128K CPU vision fallback, `A3-02` risk, rollback) | Replaced tailnet hostnames with `<tailnet>`. Added **128K-first CPU vision fallback** in **`A1-03` (Step 7)** using Strata's `"vision": {"gpu": false}` (`strata-vision.exe`) block. Documented real risk on `A3-02` and rollback on Step 2 (`A4-01`). | `strata-swift15-iq3s.log:52-53` shows GPU `--vision` at 96K left only `567 MiB` free VRAM (`< 1024 MiB` limit); `strata-swift15-iq3s.json:49-56` configures CPU `strata-vision.exe`. |

---

## Key Findings — Part 1: Top 10 Root Causes

1. **Adults-Only Guard (`comm.guard_ok`) Key-Scope Gap & Unguarded `/prompt` Script:** `comm.py:186-191` and `run_graph_job.py:124-126` inspect only `n["inputs"].get("prompt")`, missing 94 prompt-bearing inputs across 164 saved graphs (`CLIPTextEncode.text`: 52, `MiniMaxH3PromptPackBridge.prompt_1..6`: 30, `clips_json`: 5, `sequence_prompt`, `PrimitiveStringMultiline.value`: 2). Also, `notes\ali173_pw1d_run.py:373-382` posts to `127.0.0.1:10004/prompt` without `comm.guard_ok`.
2. **Runaway Custom Gate & Seeded-Fault Accumulation ("Over-Testing"):** Despite `derricks-standing-rules.md:7` and `PROMPT.md:24` (*"Add nothing custom"*), `PROMPT.md:12` and `AGENTS.md:13-29` mandate seeded-fault probes for every task (`notes/ali11_run_checks.py:50-216` runs 33 custom scripts with >10,000s total timeouts).
3. **Brittle Line-Numbered Plan Generator (`ali14d_shortplan_build.py`):** `notes/ali14d_shortplan_build.py:61-717` enforces `SIZE_CAP = 40000` B and `<id>-L<line>.md` receipts. Adding 1 line in `fix_plan.md` (40,962 B) shifts line numbers (`RECEIPT_EXTRA=191` in `iter-20261025-05.log:18`), `--emit` clobbers 96 rows (`iter-20261025-03.log:32`), and `--selftest` crashes with `IndexError` at L717.
4. **Two Conflicting `AGENTS.md` Files Loaded Into Every Pi Session:** Running Pi from `ralph-community` loads parent `5slock/AGENTS.md` (60 lines > 40-line cap), child `ralph-community/AGENTS.md` (39 lines), and stale `.pi/agent/pi-hermes-memory/STANDING.md:1-5`. The parent injects obsolete rules (`JOB_REQUEST.json` L52 vs `run_graph_job.py` L24; *"no budget ledger"* L15 vs `p7_budget.json` L17).
5. **Ping-Pong Between `llama-swap.yaml` Groups and Render-Window Gates:** `llama-swap.yaml:30-41` puts `comfyui_auto` in `groups.main` (`swap: true, exclusive: true`) per `agy_fix_20261025_report.md:36`, `PROMPT.md:25`, and `llama-swap` single-GPU docs (`agy41_ls_groups.md:33-57`), while `rt_window_probe.py:160-165` and `AGENTS.md:9` demand `persistent: true, exclusive: false` (risking 16 GB VRAM co-residency OOM).
6. **94K-Token Turn-1 Context Bloat Inside the 128K Window:** Loading `@PROMPT.md`, `@fix_plan.md` (40.9 KB), two `AGENTS.md` files, 38 skills (`AGENTS.md:16`), and `notes/progress.md` (172.5 KB / ~45K tokens) consumes ~70–94K tokens on Turn 1. Keeping 128K (`131072`) while rotating `progress.md` and trimming unused web/marketing skills restores >110K tokens of working room.
7. **Thinking Token Starvation Misdiagnosed as "Vision Refusals":** Qwen3.5/Qwen3.8 emit 378–521 tokens in `reasoning_content` before `content` (`vision_battery_20261025.md:46-57`). With `"max_tokens": 300` in `strata-swift15-iq3s.json:54`, 9/12 calls hit `finish_reason="length"` with `content=""`. Setting `reasoning_effort="none"` on VL judges and `max_tokens: 3000` on Swift yields 17/17 captions.
8. **Strata Vision VRAM Constraint at 128K & Mismatched Base Refusal Vector:** `strata-swift15-iq3s.log:8-53` shows GPU `--vision` at 96K left only `567 MiB` free VRAM (`<1024 MiB` paging limit) on the `16,303 MiB` 5070 Ti. Keeping **128K (`131072`)**, CPU vision (`"vision": {"gpu": false, "max_tokens": 3000}` via `strata-vision.exe` in `strata-swift15-iq3s.json:49-56`) preserves VRAM headroom. Also, `strata-swift15-iq3s-esp.json:35-99` has `args` vs `args_written` drift and uses a base control vector with 4/12 (33.3%) refusal on Swift 1.5 (`refusal_vector_test_20261025.md:51-58`).
9. **ComfyUI H3 In-Graph `comfy kitchen attention` on `int8_convrot` UNET & Unanchored `ReferenceToVideo` Defaults in `comm.py`:** CLI `--lowvram`/`--use-ck-attention` are gone (`llama-swap.yaml:97`), but `comm.py:75-123` defaults `m_attn` (`ModelAttentionBackend`) to `attention="comfy kitchen attention"`, `ksel="euler"`, `ref_image_size="max"`, and no `MiniMaxH3AddGuide`. Safetensors header check confirms `10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors` is `"format": "int8_tensorwise", "convrot": true`, and official H3 docs (`02v_docs_h3.txt:80,201`) state **Comfy Kitchen cannot run `int8_convrot` checkpoints** (default `"pytorch attention"`). Also, `ref_image_size="match"` (`02v_docs_h3_native.txt:218`), `res_multistep` (`03y_mc_readme.txt:33`), and `MiniMaxH3AddGuide` (`SSIM 0.9154` vs `0.3476` in `needs_derrick.md:24`) anchor start frames.
10. **Loop Iteration Hang Risk, Ephemeral `pi-mobile` Listener, and Unupdated Budget Counter:** `ralph.ps1:65` has no timeout (36m hang vs `50.80 min` = `3,048s` max render in `p7/jobs/*.result.json`); `pi-mobile` (`:7878`) binds during `pi --print` (`PID 5956` at `22:19:33 CT`) and closes after (`0` listeners at `22:23:25 CT`); and `run_graph_job.py:185-190` never increments `logs/p7_budget.json` (`472.9 min / 38 jobs`).

---

## Key Findings — Part 2: Prioritized Audit Items (`P0` / `P1` / `P2`)

| ID | Pri | Step | Evidence (`path:line`) | Upstream / Community Source | Risk / Gate | Verify |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| **A6-01a** | **P0** | Step 0 | `ali173_pw1d_run.py:39,373-382` unguarded `/prompt` POST on `:10004`. | Hard Line 3 (`revise_brief.md:29`) | Unused until Step 0 lands. | `py_compile` + `ali10_adults_probe.py --check` (`D12`=0). |
| **A6-01b** | **P0** | Step 1 | `run_graph_job.py:124-126` & `comm.py:186-191` check only `"prompt"`; 2/164 graphs hit on `no: ... minors` (`ali173_cont_hc1_s51140001.api.json:188`). | Hard Line 3 & Derrick 10:17 PM rule | `guard_ok` stays 100% strict; `comm.py` needs **Derrick GO**. | `pytest test_p6_review.py test_guard_scope.py`. |
| **A4-01** | **P0** | Step 2 | Parent `5slock/AGENTS.md:1-60` conflicts with `ralph-community/AGENTS.md:1-39`; stale `STANDING.md:1-5`. | Pi `contextFiles` & Huntley Ralph (`<40` lines) | Copy to `notes/AGENTS.20261025.archived.md` first. | `AGENTS.md` `<40` lines; `Test-Path` pass. |
| **A3-01** | **P0** | Step 3 | `ali14d_shortplan_build.py:61-717` fails on `fix_plan.md` (`40,962 B`, `IndexError` L717). | Huntley Ralph checklist (`2026-10-23-fleet-community-audit.md:64-82`) | Copy `fix_plan.md` to `.archived.md`; archive `[x]` rows. | `fix_plan.md` `<15 KB`, all `- [ ]` intact. |
| **A3-02** | **P0** | Step 4 | `ali11_run_checks.py:50-216` runs 33 custom seeded-fault scripts (>10,000s timeouts). | `PROMPT.md:24` (*"Add nothing custom"*) | Changes pass criteria; keep `pytest`, `py_compile`, `json.tool`, `check_web_saves.py`, `rt_window_probe.py`. | `ali11_run_checks.py` rc 0 in `<10s`. |
| **A1-01** | **P0** | Step 5 | `rt_window_probe.py:160-165` & `AGENTS.md:9` conflict with `llama-swap.yaml:30-41` (`groups.main`). | `llama-swap` single-GPU docs (`agy41_ls_groups.md:33-57`) | Gate on `gpu_guard.ps1` rc 0; prevents 16 GB OOM. | `gpu_guard.ps1` & `rt_window_probe.py --check` rc 0. |
| **A1-02** | **P0** | Step 6 | `strata-swift15-iq3s.json:54` `max_tokens: 300` & VL thinking truncate 9/12 captions (`vision_battery_20261025.md:46-57`). | Qwen3-VL API (`reasoning_effort: "none"`, `max_tokens: 3000`) | Vision describes scene/lighting only (**never identity/age**). | `gpu_guard.ps1` rc 0 + `ali163_vision_probe.py` (17/17). |
| **A1-03** | **P0** | Step 7 | `strata-swift15-iq3s.log:52-53`: GPU `--vision` at 96K left `567 MiB` free VRAM (`<1024 MiB` limit). | Strata CPU vision (`strata-vision.exe`, `"gpu": false` in `strata-swift15-iq3s.json:49-56`) | **128K (`131072`) stays**; CPU `strata-vision.exe` keeps `>=1024 MiB` free VRAM. | `gpu_guard.ps1` rc 0 + `-c 131072` + `>=1024 MiB` free. |
| **A6-02** | **P0** | Step 8 | `comm.py:75,84,123` uses `attention="comfy kitchen attention"` on `int8_convrot` UNET (`10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors`). | Official H3 docs (`02v_docs_h3.txt:80,201`) & schema (`ali173_b2_obj_ModelAttentionBackend.json:1`): `"pytorch attention"` | Reverses Oct 9 KEEP per 10:15 PM rule; needs seed `51150011` A/B + **Derrick GO**. | `gpu_guard.ps1` rc 0 + seed `51150011` A/B + `pytest`. |
| **A6-03** | **P1** | Step 9 | `comm.py:96,118-120` uses `ref_image_size="max"`, `euler`, no `MiniMaxH3AddGuide` (`SSIM 0.3476` vs `0.9154`). | Official H3 docs (`02v_docs_h3_native.txt:218`, `03y_mc_readme.txt:33`) | 1 variable/render on seed `51150011`; needs **Derrick GO**. | `gpu_guard.ps1` rc 0 + seed `51150011` A/B + `pytest`. |
| **A3-03** | **P1** | Step 10 | `notes/progress.md` (172.5 KB) + 38 skills (`AGENTS.md:16`) bloat Turn 1 to ~94K tokens. | Pi compaction docs & Huntley Ralph | Archive `progress.md` (keep last 20 lines); 128K stays. | `progress.md` `<10 KB`, `contextWindow=131072`. |
| **A3-04** | **P1** | Step 10 | `logs/p7_budget.json:1-7` frozen at `472.9 min / 38 jobs` since Oct 23. | `AGENTS.md:10` & Audit `A-6` | **Counter only** (`used_min`, `jobs`); **no refuse-on-cap gate**. | `json.tool logs/p7_budget.json` pass. |
| **A2-01** | **P1** | Step 10 | `ralph.ps1:65` has no timeout; max render in `p7/jobs` is **`50.80 min` (`3,048s`)** (`ali147_pool_fix4_s51080000.result.json`). | `ralph-claude-code` timeout & Audit `A-8` | Set timeout to **`4500s` (75 min)**; **no custom secret scanner**. | PowerShell AST check on `ralph.ps1` (0 errors). |
| **A1-04** | **P1** | Step 11 | `strata-swift15-iq3s-esp.json:35-99` `args` drift & base control vector (33.3% refusal in `refusal_vector_test_20261025.md:51-58`). | `llama-cvector-generator` & Audit `A-7` | Strictly **after Steps 0–1** under `gpu_guard.ps1` rc 0; no real-person LoRAs. | `json.tool` + `ali318_refusal_probe.py` (`3/3`). |
| **A2-02** | **P2** | Step 11 | `.pi/agent/models.json:1-121` omits VL judges; `:7878` listens during `pi --print` (`PID 5956`) & closes after (`K-2`). | Pi `models.json` & `@ifi/pi-mobile` (`pi_mobile_live_20261025.md:7-35`) | Add VL judges; run 3-part `:7878` check (`https://<tailnet>:8443`). | `json.tool models.json` + 3-part `:7878` log. |
| **A3-05** | **P2** | Step 12 | `logs/ralph.log` has NUL bytes; 4 `discord_bridge` PIDs (`26972->27152->26876->26896`) are **1** venv chain. | Global UTF-8 rule & Audit `G-1` | Copy `ralph.log.bak-20261025` first; no `discord_bridge` stop without **Derrick GO**. | `Test-Path ralph.log.bak-20261025` & 0 NUL bytes. |
| **A5-01** | **P2** | Step 12 | Verified live: `switchyard-upgrade/repo` (`d9efd2f..b6384bc`) is **already merged** in `C:\AI\director` (`HEAD=36dadae`, 20/20 tests pass). | `DONE.md:1-17` & `CHANGES.md:80-152` | Already merged; enabling flags in `director.yaml` needs **Derrick GO**. | `pytest` 3 Switchyard unit test files (20 passed). |
| **A2-03** | **P2** | Step 2 | Verified live: F12 extensions absent from `settings.json:59-61` and renamed to `.disabled-2026-10-25` on disk. | Audit `A-9` (`F12`) | Already disabled; verify they stay absent in Step 2. | `Select-String settings.json` = 0 hits. |

---

## Key Findings — Part 3: What Is Missing (Information Needed and Not Found)

1. **No Swift-1.5-Specific Refusal Vector on Disk:** Both `.gguf` vectors on disk were extracted from base `Qwen3.8-Flash-Next`, not `Swift-Qwen3.8-Flash-Next` (`refusal_vector_test_20261025.md:51-130`).
2. **Derrick's Sign-Off on Escalated Cards (`needs_derrick.md:1-38`):**
   - **Audit `A-5` / `A6-02`:** Confirming `comm.py` switch from `"comfy kitchen attention"` (Oct 9 KEEP) to `"pytorch attention"` for `int8_convrot` after inspecting the seed `51150011` A/B contact sheet.
   - **Audit `A-3`:** Confirming Continuum `no:` avoidance lines omit banned tokens (keeping `guard_ok` 100% uniform) vs a separate negative-key rule.
   - **Rows 18, 21, 28 in `needs_derrick.md`:** `GI063_PK014` wording reframe, `GI046_BD002` start still anatomy flaw, and `GI063.txt` re-caption review.
3. **Human Phone QR Pairing for `pi-mobile` (`https://<tailnet>:8443`):** Requires Derrick to run `/remote` in an interactive `pi` terminal and scan the QR code (`pi_mobile_live_20261025.md:37-41`).

---

## Key Findings — Part 4: Conflicts Found Between Files

| Conflict Topic | File A (`path:line`) | File B (`path:line`) | Community / Standing Resolution |
| :--- | :--- | :--- | :--- |
| **1. `comfyui_auto` Group** | `llama-swap.yaml:30-41` & `PROMPT.md:25`: in `groups.main` (`swap: true, exclusive: true`). | `AGENTS.md:9`, `5slock/AGENTS.md:25`, `rt_window_probe.py:160-165`: separate `persistent: true, exclusive: false` group. | `llama-swap` single-GPU docs (`agy41_ls_groups.md:33-57`): keep in `groups.main` (`exclusive: true`) while `run_graph_job.py` holds `gpu-render.lock`. |
| **2. Render Submission** | `5slock/AGENTS.md:52`: *"write `p7/JOB_REQUEST.json`... END the iteration"*. | `AGENTS.md:8` & `PROMPT.md:25`: Forge runs `run_graph_job.py` directly. | Direct `run_graph_job.py` execution (archive `5slock/AGENTS.md` in Step 2). |
| **3. Custom Gates vs Stock** | `PROMPT.md:24` & `derricks-standing-rules.md:7`: *"Add nothing custom"* / *"Community/stock settings first"*. | `PROMPT.md:12` & `AGENTS.md:13-29`: mandates seeded-fault probes & `ali14d_shortplan_build.py`. | Huntley Ralph pattern: plain markdown `fix_plan.md` + standard `pytest` / `py_compile` / `json.tool`. |
| **4. H3 Attention on `int8_convrot`** | `comm.py:75-123` & Oct 9 KEEP (`production-defaults-st8-dynamic-vram.md:5`): `"comfy kitchen attention"`. | Official H3 docs (`02v_docs_h3.txt:80,201`) & `cf1_setup_audit_20261024.md:52`: Comfy Kitchen cannot run `int8_convrot`; default `"pytorch attention"`. | Per Derrick's 10:15 PM rule, follow official H3 docs (`"pytorch attention"`), verified by seed `51150011` A/B + Derrick GO. |
| **5. H3 Sizing, Sampler & Guide** | `comm.py:96-120`: `ref_image_size="max"`, `euler`, no `MiniMaxH3AddGuide`. | `02v_docs_h3_native.txt:218`, `03y_mc_readme.txt:33`, `ali163_hc15_bd002_s51150011.api.json:202-393`: `"match"`, `res_multistep`, `AddGuide` (`SSIM 0.9154`). | Official H3 defaults + `MiniMaxH3AddGuide` frame-0 anchor, verified 1 variable at a time on seed `51150011`. |
| **6. `rt_window_probe.py` Path** | `PROMPT.md:25` & `5slock/AGENTS.md:25`: cites `community/notes/rt_window_probe.py`. | Actual file on disk is `ralph-community/notes/rt_window_probe.py:1-240`. | Fix path in `PROMPT.md:25` to `ralph-community/notes/rt_window_probe.py`. |

---

## Action Items — Part 5: Proposed Order of One-at-a-Time Changes (Forge `fix_plan.md` Items)

Every step below is executed **by Forge** from `C:\Users\derek\5slock\ralph-community` as a `fix_plan.md` item, one variable at a time. Antigravity and Max do not edit Forge's files.

### Step 0 (`A6-01a`, P0): Gate `ali173_pw1d_run.py` Through `comm.guard_ok` Before Any `/prompt` POST
- **Owner:** Forge (`0.1-pw1d-guard`) | **Gate:** Self-edit (`ali173_pw1d_run.py` is unused until Step 0 lands).
- **One Change:** In `C:\AI\community\notes\ali173_pw1d_run.py`, import `comm` (`C:\AI\community\scripts`), replace `127.0.0.1:10004` (`L39-40`) with `comm.BASE` (`/comfyui`), and run `comm.guard_ok` on `SHORT_PROMPT` and every string in `graph` before `post("/prompt", ...)` (`L372`), exiting `3` if `False`.
- **Verify:** `python -m py_compile C:/AI/community/notes/ali173_pw1d_run.py` and `C:/AI/director/.venv/Scripts/python.exe notes/ali10_adults_probe.py --check` (`D12 queue_census` = 0 unguarded sites).
- **Rollback:** `git -C C:/AI/community revert HEAD --no-edit`
- **Log / Commit:** `git -C C:/AI/community add notes/ali173_pw1d_run.py && git -C C:/AI/community commit -m "A6-01a: gate ali173_pw1d_run.py /prompt through comm.guard_ok and /comfyui"` + commit in `ralph-community` and log in `notes/progress.md`.

### Step 1 (`A6-01b`, P0): Expand Pre-Render `guard_ok` Key Scope in `run_graph_job.py` and `comm.py`
- **Owner:** Forge (`0.2-guard-key-scope`) | **Gate:** `run_graph_job.py` & `tests/test_guard_scope.py` are Forge self-edits; **`comm.py` requires Derrick's explicit GO** (`G-1`). `test_p6_review.py` is never edited.
- **One Change:** Expand the pre-queue `guard_ok` loop in `C:\AI\community\scripts\run_graph_job.py:124-126` (and `comm.py:186-191` on Derrick's GO) to inspect all prompt-bearing node inputs (`prompt`, `text`, `prompt_1..6`, `clips_json`, `sequence_prompt`, `value`). Keep `comm.guard_ok` 100% strict; in Continuum V39 builders (`PrimitiveStringMultiline`), use artifact-avoidance tokens only on `no:` lines (`no: watermark, text overlay, logos, extra limbs, deformed hands, blurry, camera cuts`). Add unit tests in `C:\AI\community\scripts\tests\test_guard_scope.py`.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe -m pytest C:/AI/community/scripts/tests/test_p6_review.py C:/AI/community/scripts/tests/test_guard_scope.py` (`test_p6_review.py` sha256 `c3c2e1693eefc0cdb7ea1ee382cbe7db62568c160edafe399fe5fd17f078e213` unchanged).
- **Rollback:** `git -C C:/AI/community revert HEAD --no-edit`
- **Log / Commit:** `git -C C:/AI/community add scripts/run_graph_job.py scripts/comm.py scripts/tests/test_guard_scope.py && git -C C:/AI/community commit -m "A6-01b: expand guard_ok check to all prompt-bearing H3 node inputs"` + commit in `ralph-community` and log in `notes/progress.md`.

### Step 2 (`A4-01` & `A2-03`, P0): Archive Duplicate `5slock/AGENTS.md`, Clean `STANDING.md`, and Verify F12 Extensions Stay Off
- **Owner:** Forge (`0.3-agents-consolidate`) | **Gate:** Forge self-edit.
- **One Change:** Copy `../AGENTS.md` to `../notes/AGENTS.20261025.archived.md`, replace `../AGENTS.md` with a 1-line pointer (`See C:/Users/derek/5slock/ralph-community/AGENTS.md`), fix the `rt_window_probe.py` path in `PROMPT.md:25`, and replace stale Oct 15 `C:\AI\director` lines in `C:\Users\derek\.pi\agent\pi-hermes-memory\STANDING.md` (backup `STANDING.20261025.archived.md`).
- **Verify:** `(Get-Content ../AGENTS.md).Count -le 3`, `(Get-Content AGENTS.md).Count -le 40`, every path in `AGENTS.md` passes `Test-Path`, and `Select-String -Path C:/Users/derek/.pi/agent/settings.json -Pattern 'headless-guard|protected-paths'` = 0 hits (`A2-03`).
- **Rollback:** `Copy-Item ../notes/AGENTS.20261025.archived.md ../AGENTS.md -Force` and `Copy-Item C:/Users/derek/.pi/agent/pi-hermes-memory/STANDING.20261025.archived.md C:/Users/derek/.pi/agent/pi-hermes-memory/STANDING.md -Force`.
- **Log / Commit:** `git add AGENTS.md PROMPT.md notes/progress.md && git commit -m "A4-01: consolidate duplicate AGENTS.md and fix rt_window_probe path"`.

### Step 3 (`A3-01`, P0): Retire `ali14d_shortplan_build.py` `-L<line>` Requirement and Restore Plain Markdown `fix_plan.md`
- **Owner:** Forge (`0.4-plain-fix-plan`) | **Gate:** Forge self-edit (copy taken first; no deletes).
- **One Change:** Copy `fix_plan.md` to `notes/plans/fix_plan.20261025.archived.md`, move completed `- [x]` rows to `notes/plans/completed_archive_20261025.md`, remove the `ali14d_shortplan_build.py` `-L<line>` mandate from `AGENTS.md`, and keep `fix_plan.md` as a plain-markdown checklist (`<15 KB`).
- **Verify:** `(Get-Item fix_plan.md).Length -lt 15000` and all open `- [ ]` items remain intact.
- **Rollback:** `git revert HEAD --no-edit`.
- **Log / Commit:** `git add fix_plan.md AGENTS.md notes/plans/completed_archive_20261025.md notes/progress.md && git commit -m "A3-01: archive completed rows and restore plain markdown fix_plan.md"`.

### Step 4 (`A3-02`, P0): Prune 33-Script `ali11_run_checks.py` Runner to Core Project Validators
- **Owner:** Forge (`0.5-prune-gate-churn`) | **Gate:** Forge self-edit.
- **One Change:** Copy `notes/ali11_run_checks.py` to `notes/ali11_run_checks.20261025.archived.py`, remove the *"seeded-fault probe"* mandate from `PROMPT.md:12` and `AGENTS.md`, and simplify `notes/ali11_run_checks.py` to run only real project validators (`pytest test_p6_review.py test_guard_scope.py`, `py_compile`, `json.tool`, `check_web_saves.py`, `rt_window_probe.py --check`).
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe notes/ali11_run_checks.py` exits 0 in `<10s`.
- **Rollback:** `git revert HEAD --no-edit`.
- **Log / Commit:** `git add PROMPT.md AGENTS.md notes/ali11_run_checks.py notes/progress.md && git commit -m "A3-02: pare ali11_run_checks.py to fast project validators and drop seeded-fault rule"`.

### Step 5 (`A1-01`, P0): Align `rt_window_probe.py` and `AGENTS.md` With `llama-swap.yaml` `groups.main` (`exclusive: true`)
- **Owner:** Forge (`0.6-llamaswap-group-sync`) | **Gate:** Forge self-edit under `powershell -NoProfile -File C:/AI/director/scripts/gpu_guard.ps1` rc 0 (`IDLE`).
- **One Change:** Update `AGENTS.md:9` and `notes/rt_window_probe.py:160-165` so `RT_GROUP` checks that `comfyui_auto` is in `groups.main` (`swap: true, exclusive: true`) with `ttl: 300` and `unloadTimeout: 1900`, matching live `C:\AI\director\config\llama-swap.yaml:30-41` and `PROMPT.md:25`.
- **Verify:** `powershell -NoProfile -File C:/AI/director/scripts/gpu_guard.ps1` (rc 0) and `C:/AI/director/.venv/Scripts/python.exe notes/rt_window_probe.py --check` (rc 0).
- **Rollback:** `git revert HEAD --no-edit`.
- **Log / Commit:** `git add AGENTS.md notes/rt_window_probe.py notes/progress.md && git commit -m "A1-01: align AGENTS.md and rt_window_probe.py with llama-swap groups.main"`.

### Step 6 (`A1-02`, P0): Fix Vision Thinking Token Truncation (`reasoning_effort="none"` on VL Judges, `max_tokens: 3000` on Swift)
- **Owner:** Forge (`0.7-vision-truncation-fix`) | **Gate:** Forge self-edit under `gpu_guard.ps1` rc 0 (`IDLE`). Vision describes scene/lighting/action only (**never identity or age**).
- **One Change:** Copy `C:\AI\strata-0.2.2\strata-swift15-iq3s.json` to `.bak-20261025`, update `"max_tokens": 300` (`L54`) to `3000`, and pass `reasoning_effort="none"` (`chat_template_kwargs: {"enable_thinking": false}`) when calling `vl_judge` / `qwen3vl_judge` in `p6_review.py` / caption callers.
- **Verify:** Under `gpu_guard.ps1` rc 0, run `python -m json.tool C:/AI/strata-0.2.2/strata-swift15-iq3s.json > $null` and `C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_vision_probe.py --check` (`17/17` captions, `finish_reason="stop"`).
- **Rollback:** `Copy-Item C:/AI/strata-0.2.2/strata-swift15-iq3s.json.bak-20261025 C:/AI/strata-0.2.2/strata-swift15-iq3s.json -Force` and `git -C C:/AI/community revert HEAD --no-edit`.
- **Log / Commit:** Commit in `C:\AI\community` and `ralph-community` + `notes/progress.md`.

### Step 7 (`A1-03`, P0): Verify Swift 1.5 Vision With 128K-First CPU Vision Fallback (`strata-vision.exe`)
- **Owner:** Forge (`0.8-swift-vision-128k`) | **Gate:** Forge self-edit under `gpu_guard.ps1` rc 0 (`IDLE`). **Hard Line:** 128K context (`--max-context 131072`) never shrinks.
- **One Change:** Copy the CPU `"vision"` block from `strata-swift15-iq3s.json:49-56` (`"exe": "...\\strata-vision.exe", "gpu": false, "max_tokens": 3000, "threads": 10`) into `strata-swift15-iq3s-esp.json` (backup `.bak-20261025`). Test 1 image on `coding_swift15_iq3s` at `--max-context 131072`; keep `"gpu": false` so `strata-vision.exe` runs `mmproj` on CPU while `131072` stays in VRAM with `>1,024 MiB` free headroom.
- **Verify:** Under `gpu_guard.ps1` rc 0, check `C:\AI\strata-0.2.2\strata-swift15-iq3s.log` tail for `--max-context 131072`, no `<1024 MiB` warning, and HTTP 200 caption on a 1-image test.
- **Rollback:** `Copy-Item C:/AI/strata-0.2.2/strata-swift15-iq3s-esp.json.bak-20261025 C:/AI/strata-0.2.2/strata-swift15-iq3s-esp.json -Force`.
- **Log / Commit:** Record test output in `notes/` and commit in `ralph-community` + `notes/progress.md`.

### Step 8 (`A6-02`, P0): Fixed-Seed A/B & Update `comm.py` `ModelAttentionBackend` From `comfy kitchen attention` to `"pytorch attention"`
- **Owner:** Forge (`0.9-h3-pytorch-attention-ab`) | **Gate:** Requires `gpu_guard.ps1` rc 0 (`IDLE`) for A/B render, and **Derrick's explicit GO** before editing `C:\AI\community\scripts\comm.py:75,123` (reversing Oct 9 `ck-attention` KEEP per Derrick's Oct 25 10:15 PM rule for `int8_convrot`).
- **One Change:** Clone `ali163_hc15_bd002_s51150011.api.json` on seed `51150011` changing only `m_attn.inputs.attention` to `"pytorch attention"` (`ali173_b2_obj_ModelAttentionBackend.json:1`, `02v_docs_h3.txt:80,201`). Render via `run_graph_job.py` under `gpu_guard.ps1` rc 0, build contact sheet (`ali163_hc_final_check.py` + `ali163_hc_final_sheet.py`), and on Derrick's GO update `attention="pytorch attention"` in `comm.py:75,123`.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe -m pytest C:/AI/community/scripts/tests/test_p6_review.py C:/AI/community/scripts/tests/test_guard_scope.py` (100% green) and objective check pass on seed `51150011`.
- **Rollback:** `git -C C:/AI/community revert HEAD --no-edit`.
- **Log / Commit:** `git -C C:/AI/community add scripts/comm.py && git -C C:/AI/community commit -m "A6-02: set comm.py default attention to pytorch attention for int8_convrot"` + commit in `ralph-community`.

### Step 9 (`A6-03`, P1): One-Variable-at-a-Time A/B & Update `comm.py` H3 Graph Defaults (`ref_image_size="match"`, `MiniMaxH3AddGuide`, `res_multistep`)
- **Owner:** Forge (`1.1-h3-graph-defaults`) | **Gate:** Requires `gpu_guard.ps1` rc 0 (`IDLE`) and **Derrick's explicit GO** for `comm.py` edits and KEEP decisions (`IM1`).
- **One Change:** On seed `51150011`, validate one variable per render: (a) `ref_image_size: "match"` with `MiniMaxH3AddGuide` (`frame_idx: 0, strength: 1.0`) on `c0` (`SSIM 0.9154` in `ali163_hc15_bd002_s51150011`), then (b) `sampler_name: "res_multistep"` (`02v_docs_h3.txt:180`, `03y_mc_readme.txt:33`). On Derrick's GO, update `comm.first_pass()` and `comm._common()` in `comm.py:96,118-120`.
- **Verify:** `C:/AI/director/.venv/Scripts/python.exe -m pytest C:/AI/community/scripts/tests/test_p6_review.py C:/AI/community/scripts/tests/test_guard_scope.py` (100% green).
- **Rollback:** `git -C C:/AI/community revert HEAD --no-edit`.
- **Log / Commit:** Commit in `C:\AI\community` and `ralph-community` + `notes/progress.md`.

### Step 10 (`A3-03`, `A3-04` & `A2-01`, P1): Rotate `progress.md`, Add Non-Blocking `p7_budget.json` Counter, and Set `4500s` Timeout in `ralph.ps1`
- **Owner:** Forge (`1.2-context-counter-timeout`) | **Gate:** Forge self-edits. **Zero refuse-on-cap gate** (`A-6`) and **zero custom PowerShell secret scanner** (`A-8`).
- **One Change (3 sub-items, 1 commit each):** (1) `A3-03`: Copy `notes/progress.md` (172.5 KB) to `notes/progress_archive_20261025.md`, keep latest 20 entries in `notes/progress.md` (`<8 KB`), and disable unused web/marketing skills from `compound-engineering-plugin` in `C:\Users\derek\.pi\agent\settings.json` (backup `.bak-20261025-skills`). (2) `A3-04`: In `C:\AI\community\scripts\run_graph_job.py` `finally` (`L189`), atomically update `used_min` and `jobs` in `logs/p7_budget.json` (**counter only, never refusing a render**). (3) `A2-01`: In `ralph.ps1:65` (backup `.bak-20261025-timeout`), wrap `pi` in a `4500s` (75 min) timeout job (`> 3,048s` max render in `ali147_pool_fix4_s51080000.result.json` + `1,200s` queue timeout).
- **Verify:** `(Get-Item notes/progress.md).Length -lt 10000`, `python -m json.tool logs/p7_budget.json > $null`, and PowerShell AST parse of `ralph.ps1` (`0` errors).
- **Rollback:** `git revert HEAD --no-edit` and `git -C C:/AI/community revert HEAD --no-edit`.
- **Log / Commit:** Separate commits in `ralph-community` and `C:\AI\community` + `notes/progress.md`.

### Step 11 (`A1-04` & `A2-02`, P1 / P2): Sync `strata-swift15-iq3s-esp.json`, Add VL Judges to `models.json`, and Run 3-Part `pi-mobile` Test
- **Owner:** Forge (`1.3-esp-models-pimobile`) | **Gate:** Runs only **after Steps 0 and 1 (`A6-01a/b`) are verified** (`A-7`). Any Strata probe requires `gpu_guard.ps1` rc 0.
- **One Change:** (1) `A1-04`: Backup `C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.json` to `.bak-20261025-sync` and sync `args` with `args_written` (`--pool-workers 13`); any Swift control-vector sweep must pass `ali318_refusal_probe.py` (`3/3` coding pass) under `gpu_guard.ps1` rc 0. (2) `A2-02`: Backup `C:\Users\derek\.pi\agent\models.json` to `.bak-20261025-vl`, add `vl_judge` and `qwen3vl_judge` (`input: ["text", "image"]`), and run the 3-part `pi-mobile` check (`Get-NetTCPConnection -LocalPort 7878 -State Listen` during vs between passes + `https://<tailnet>:8443` status).
- **Verify:** `python -m json.tool C:/Users/derek/.pi/agent/models.json > $null` and `python -m json.tool C:/AI/strata-0.2.2/strata-swift15-iq3s-esp.json > $null`.
- **Rollback:** Restore `.bak-20261025-vl` and `.bak-20261025-sync`.
- **Log / Commit:** Commit in `ralph-community` + `notes/progress.md`.

### Step 12 (`A3-05` & `A5-01`, P2): Copy `ralph.log` Before NUL-Strip; Record `discord_bridge` & Switchyard Status for Derrick
- **Owner:** Forge (`1.4-log-hygiene-and-cards`) | **Gate:** `ralph.log` cleanup runs **only after copying to `logs/ralph.log.bak-20261025` first** (`G-1`). Stopping `discord_bridge` or enabling Switchyard flags in `C:\AI\director\config\director.yaml` requires **Derrick's explicit GO** (`G-1`).
- **One Change:** Copy `logs/ralph.log` to `logs/ralph.log.bak-20261025`, strip `0x00` bytes from `logs/ralph.log` (UTF-8 no BOM), and record in `C:\AI\community\notes\needs_derrick.md` that: (a) the 4 `discord_bridge` PIDs (`26972->27152->26876->26896`) are 1 Windows `.venv` wrapper chain (1 watchdog + 1 worker) and need no kill unless Derrick wants `discord_bridge` stopped; and (b) `switchyard-community-upgrade` (`d9efd2f..b6384bc`) is already merged in `C:\AI\director` (`20/20` unit tests passing), awaiting only Derrick's GO to enable `confirm_free` / `as_model_enabled` / `stall_ladder_enabled` in `config/director.yaml`.
- **Verify:** `Test-Path logs/ralph.log.bak-20261025` is `True` and `([System.IO.File]::ReadAllBytes("logs/ralph.log") -contains 0)` is `False`.
- **Rollback:** `Copy-Item logs/ralph.log.bak-20261025 logs/ralph.log -Force`.
- **Log / Commit:** Commit in `ralph-community` and `C:\AI\community` + `notes/progress.md`.

---

## Part 6: Files Read and Used for Plan v2 (42 Files)

1. `C:\AI\community\briefs\argon_audit_20261025\`: `revise_brief.md:1-33`, `brief.md:1-96`, `context/fleet_audit.md:1-266`, `plan.md:1-335`
2. `context\box\`: `packs/fleet/derricks-standing-rules.md:1-11`, `packs/max/production-defaults-st8-dynamic-vram.md:1-27`, `audits/2026-10-23-fleet-community-audit.md:1-242`, `audits/2026-10-23-max-overcontrol-audit.md:1-6`
3. `C:\AI\director\`: `config/llama-swap.yaml:1-121`, `scripts/gpu_guard.ps1:1-201`, `scripts/comfy_graceful_stop.ps1:1-25`, `config/pi/settings.json:1-40`
4. `C:\AI\community\scripts\`: `comm.py:1-241`, `run_graph_job.py:1-191`, `p6_review.py:1-631`, `tests/test_p6_review.py:1-90`
5. `C:\AI\community\notes\`: `ali173_pw1d_run.py:1-434`, `cf1_setup_audit_20261024.md:1-179`, `needs_derrick.md:1-38`, `ali173_b2_obj_ModelAttentionBackend.json:1`, `web/02v_docs_h3.txt:1-243`, `web/02v_docs_h3_native.txt:190-254`, `web/02v_cicalooo_card.txt:1-61`, `web/03y_mc_readme.txt:1-63`, `web/agy41_ls_groups.md:1-120`
6. `C:\AI\community\p7\` & `runs\`: `p7/graphs/ali163_hc15_bd002_s51150011.api.json:1-394`, `runs/ali173_cont_hc1_s51140001/ali173_cont_hc1_s51140001.api.json:1-220`, `p7/jobs/ali147_pool_fix4_s51080000.result.json:1`, `briefs/agy_fix_20261025_report.md:1-133`
7. `C:\Users\derek\5slock\AGENTS.md:1-60` & `ralph-community\`: `PROMPT.md:1-25`, `AGENTS.md:1-39`, `ralph.ps1:1-94`, `fix_plan.md:1-159`, `logs/p7_budget.json:1-7`, `notes/pi_mobile_live_20261025.md:1-64`, `notes/ali15_pi_mobile_probe.py:1-150`, `notes/vision_battery_20261025.md:1-88`, `notes/refusal_vector_test_20261025.md:1-134`, `notes/rt_window_probe.py:1-240`, `notes/ali10_adults_probe.py:1-120`, `notes/ali11_run_checks.py:1-220`, `notes/ali14d_shortplan_build.py:1-725`
8. `.pi\agent\` (`settings.json:1-66`, `models.json:1-121`, `pi-hermes-memory/STANDING.md:1-5`), `C:\AI\strata-0.2.2\` (`strata-swift15-iq3s.json:1-103`, `strata-swift15-iq3s-esp.json:1-109`, `strata-swift15-iq3s.log:1-60`), `C:\AI\switchyard-upgrade\` (`DONE.md:1-17`, `CHANGES.md:1-152`)
