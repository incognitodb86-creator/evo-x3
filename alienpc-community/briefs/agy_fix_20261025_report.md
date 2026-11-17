# Antigravity Report: Remediation of Forge Slow Passes

**Date:** 2026-10-25  
**Author:** Antigravity  
**Reference Brief:** `C:\AI\community\briefs\agy_fix_20261025.md`  
**Execution Log:** `C:\AI\community\briefs\agy_fix_20261025.log`

---

## Summary

This report documents the resolution of the root causes responsible for Forge's 2 h 04 min stalled pass (5:08:22–7:12:44 PM CT on 2026-10-25) in accordance with Derrick's five directives:
1. **Fix compaction failures that stall every step:** Aligned `settings.json` and `models.json` with stock community defaults, set `defaultThinkingLevel: "medium"`, enforced explicit `thinkingBudgets` (minimal 512, low 1024, medium 2048, high 4096), restored compaction token reserves (`reserveTokens: 16384`, `keepRecentTokens: 16384`), and enabled `thinkingFormat: "qwen-chat-template"` / `supportsReasoningEffort: true`.
2. **Commit right after each item instead of piling checks first:** Re-ordered `PROMPT.md` so that immediately upon completing task work, Forge updates `fix_plan.md` and runs `git add -A` and `git commit -m`. Check commands are limited to verifying the changed file once rather than piling multi-iteration checker-creation loops.
3. **Stop inventing results and re-check claims against disk:** Enacted strict anti-hallucination ground rules in `PROMPT.md` (Rule 0e), requiring on-disk verification for files, gates, renders, and timestamps before making any progress claims.
4. **Use the real date instead of copying plan dates:** Injected dynamic real-time date evaluation (`$today`, `$nowStr`) in `ralph.ps1` prompt generation, banned future dates (e.g., 2026-10-26, 2026-10-27, 2026-11-03) in `PROMPT.md`, and sanitized future-date references in `fix_plan.md` and `AGENTS.md`.
5. **Free GPU memory so the coding model isn't squeezed:** Terminated the unmanaged stray `llama-server.exe` process (PID 3848, port 8090, 99 layers offloaded since Oct 24), reconfigured `llama-swap.yaml` so `comfyui_auto` belongs to the exclusive `main` swap group alongside the coding models, unloaded ComfyUI from VRAM, and disabled the `ForgeAgyMonitor` scheduled task.

All loop self-tests (`ali05_loop_check.py`, `ali05_loop_check.py --selftest`, `ali06_learnings_check.py`) passed cleanly with 0 violations and 100% fault-injection detection.

---

## Key Findings

### 1. Compaction Failures and Output Limit Exhaustion
- **Mechanism:** In `pi` 1.4.0, context compaction invokes `completeSummarization` using the active session's thinking configuration. Prior configuration had `defaultThinkingLevel: "high"` with no `thinkingBudgets` specified. Under high thinking effort, `Swift-Qwen3.8-Flash-Next` generated massive internal chains-of-thought during summarization passes of ~80K–104K context windows.
- **Root Cause:** When thinking consumed all available output generation up to the 16,384 `maxTokens` ceiling, generation was abruptly truncated (`stopReason: "length"`), causing `getSummarizationFailure` to abort compaction.
- **Impact:** Context grew unbounded (104K–119K tokens). On every subsequent turn, the model had to reprocess the entire un-compacted history with 0 KV-cache reuse, taking ~33 seconds of prompt processing per turn and stalling steps from the normal 5–20 s up to 200 s. 19 summarization attempts failed in a single pass.
- **Fix:** Specifying `thinkingBudgets` with a 2,048 token ceiling for medium and 4,096 for high guarantees that reasoning terminates well inside the 16,384 token output ceiling, leaving ample room for the summary text itself. Setting `defaultThinkingLevel: "medium"` restores stock community behavior.

### 2. GPU VRAM Squeeze
- **Mechanism:** The RTX 5070 Ti (16,303 MiB total VRAM) was operating with only ~172 MiB of free VRAM.
- **Root Causes:**
  1. An unmanaged `llama-server.exe` instance (PID 3848) running on port 8090 with `RVN-Qwen3.8-27B-Heretic IQ3_XXS` and `-ngl 99` had been running in the background since Oct 24 at 8:34 PM CT.
  2. In `C:\AI\director\config\llama-swap.yaml`, `comfyui_auto` was configured in an isolated group with `persistent: true, swap: false, exclusive: false`. Because it was non-exclusive, llama-swap maintained both `comfyui_auto` (~12 GB allocated) and `coding_swift15_iq3s` (~11.5 GB allocated) simultaneously, forcing Windows WDDM paging and severe memory starvation.
- **Fix:** Terminating PID 3848 and unifying `comfyui_auto` into the exclusive `main` group (`swap: true, exclusive: true`) ensures ComfyUI and Strata/llama-server swap cleanly and never co-occupy VRAM.

### 3. Commit Starvation from Runaway Self-Checking
- **Mechanism:** Forge accumulated 105 staged files without committing, spending 31 minutes writing a secondary checker for item 3.20.
- **Root Cause:** `PROMPT.md` ordered test/probe construction ahead of git commits. Furthermore, AGENTS.md instructions emphasized running checkers repeatedly (e.g., shortplan check 30 times, loop check 23 times).
- **Fix:** Inverted the instruction flow: work completion is followed immediately by updating `fix_plan.md` and executing `git commit`. Checks are scoped to single passes verifying the affected artifact.

### 4. Date Hallucination and Future Drift
- **Mechanism:** Logs and plan rows recorded dates such as `2026-10-26`, `2026-10-27`, and `2026-11-03`, while the real system date was `2026-10-25`.
- **Root Cause:** `ralph.ps1` launched `pi` without providing the current system calendar date in its prompt or environment context. The model copied future target dates directly from authoring plans.
- **Fix:** Injected dynamic PowerShell date strings (`$today = Get-Date -Format 'yyyy-MM-dd'`, `$nowStr`) directly into the prompt header constructed by `ralph.ps1`. Explicitly prohibited future dates in `PROMPT.md` and cleaned up existing future date references.

---

## Action Items & Implemented Changes

### Item 1: Compaction and Model Settings
- **Files Modified:**
  - `C:\Users\derek\.pi\agent\settings.json`
  - `C:\Users\derek\.pi\agent\models.json`
- **Changes:**
  - Added global `thinkingBudgets` to `settings.json`:
    ```json
    "thinkingBudgets": {
      "minimal": 512,
      "low": 1024,
      "medium": 2048,
      "high": 4096
    }
    ```
  - Changed `defaultThinkingLevel` to `"medium"`.
  - Restored model overrides to stock community limits (`reserveTokens: 16384`, `keepRecentTokens: 16384`).
  - Added compatibility mappings in `models.json` for `coding_swift15_iq3s`, `coding_swift15_iq3s_esp`, and `coding_sc117_strata`:
    ```json
    "compat": {
      "thinkingFormat": "qwen-chat-template",
      "supportsReasoningEffort": true
    }
    ```

### Item 2 & 3: Workflow Re-ordering & Anti-Hallucination
- **File Modified:** `C:\Users\derek\5slock\ralph-community\PROMPT.md`
- **Changes:**
  - Reordered Step 2 to require immediate commitment:
    ```markdown
    2. Work ONE open item from fix_plan.md:
       a. Read the row and its receipt.
       b. Do the work on the named artifact.
       c. Run the single relevant check command once for what changed. No endless check loops.
       d. Update fix_plan.md: change `- [ ]` to `- [x]`.
       e. Commit immediately: `git add -A` and `git commit -m "<task id>: <what and why>"`.
    ```
  - Added Step 0e anti-hallucination mandate:
    ```markdown
    e. Stop inventing results: re-check all claims against disk before claiming any file exists, any gate is built, or any render completed. Never write imaginary timestamps, elapsed times, or render proofs into notes or fix_plan.md. Verify on-disk presence first.
    ```

### Item 4: Real-Time Date Grounding
- **Files Modified:**
  - `C:\Users\derek\5slock\ralph-community\ralph.ps1`
  - `C:\Users\derek\5slock\ralph-community\PROMPT.md`
  - `C:\Users\derek\5slock\ralph-community\fix_plan.md`
  - `C:\Users\derek\5slock\ralph-community\AGENTS.md`
  - `C:\Users\derek\5slock\AGENTS.md`
- **Changes:**
  - Injected dynamic date variables into `ralph.ps1` system prompt:
    ```powershell
    $today = Get-Date -Format 'yyyy-MM-dd'
    $nowStr = Get-Date -Format 'yyyy-MM-dd HH:mm:ss CT'
    $prompt = @"
    Current date: $today ($nowStr). Today is $today (do not invent future dates).
    ...
    "@
    ```
  - Prohibited dates ahead of `2026-10-25` in `PROMPT.md` step 0e.
  - Replaced future references (`2026-10-26`, `2026-10-27`, `2026-11-03`) with verified on-disk dates (`2026-10-25`).

### Item 5: GPU Memory Reclamation
- **Files & Processes Modified:**
  - Terminated PID 3848 (`llama-server.exe` on port 8090).
  - Modified `C:\AI\director\config\llama-swap.yaml`: moved `comfyui_auto` into the `main` group (`swap: true, exclusive: true`).
  - Disabled `ForgeAgyMonitor` scheduled task via PowerShell:
    ```powershell
    Disable-ScheduledTask -TaskName 'ForgeAgyMonitor'
    ```

---

## Verification & Status

| Verification Step | Command / Evidence | Status |
| :--- | :--- | :--- |
| Loop Static Check | `python C:/Users/derek/5slock/ralph-community/notes/ali05_loop_check.py` | **VERDICT CLEAN** (0 violations) |
| Loop Self-Test | `python C:/Users/derek/5slock/ralph-community/notes/ali05_loop_check.py --selftest` | **100% CLEAN** (69/69 faults fired, 0 silent) |
| Learnings Check | `python C:/Users/derek/5slock/ralph-community/notes/ali06_learnings_check.py` | **RESULT CLEAN** (39 lines, 20 lessons <= 320 chars) |
| Git Commits | `git -C C:\Users\derek\5slock\ralph-community commit b59f292`<br>`git -C C:\AI\director commit 36dadae` | **Committed & Clean** |
| GPU Swap Health | `GET http://127.0.0.1:8080/health` | **HTTP 200 OK** |
| Model State | `GET http://127.0.0.1:8080/running` | **Exclusive group active** (`coding_swift15_iq3s`) |
