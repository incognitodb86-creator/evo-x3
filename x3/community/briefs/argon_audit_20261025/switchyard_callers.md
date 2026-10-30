# Switchyard Callers Audit & Retirement Plan

**Date:** 2026-10-26 07:15 CT  
**Target:** Full retirement and archival of Switchyard per Derrick's 5:58 AM direction:  
> *"Also why are we still using switchyard and not llama swap and them community or whatevet?"*

---

## 1. Process Status (Live Verification)
- **Running Switchyard processes:** None (0 active processes).
- **Active Model Swapper:** `llama-swap.exe` running on port 8080 (managed via `llama_swap_keepalive.ps1`).
- **Active Video Queue:** ComfyUI direct `/prompt` via `run_graph_job.py` and `comm.py` (through `llama-swap` `/comfyui`).

---

## 2. Caller Census & Repointing Map

| Location | Path:Line | What It Does | Repointing / Retirement Action |
| :--- | :--- | :--- | :--- |
| **Scheduled Task** | `Switchyard llama-swap` | Runs `C:\AI\director\scripts\llama_swap_keepalive.ps1` to ensure `llama-swap.exe` is running on :8080. | Rename/relabel task to `LlamaSwapService`. Script points to `llama-swap.exe` and `llama-swap.yaml`. No Switchyard code involved. |
| **Scheduled Task** | `SY_AgyFix` | Runs `C:\AI\agy-fix-switchyard-2026-10-14\run.cmd` (Disabled). | Archived with folder; task remains disabled / deleted. |
| **Scheduled Task** | `SY_AgyFix2` | Runs `C:\AI\agy-fix-switchyard-2026-10-14\launch2.ps1` (Disabled). | Archived with folder; task remains disabled / deleted. |
| **Director Config** | `C:\AI\director\config\director.live.yaml:85` | References `C:\AI\strata\strata-iq3_xxs-switchyard.json` under `coding_sc117_strata` profile. | Stale profile definition. Active model supervisor is `llama-swap.yaml` with Strata 0.2.2. |
| **Director Config** | `C:\AI\director\config\director.example.yaml` | Legacy example config with Switchyard runner / queue definitions. | Archive / keep as example only. |
| **Director Scripts** | `C:\AI\director\scripts\gpu_guard.ps1:10,11,126,140` | Checks `C:\AI\director-queue\jobs\*.json` for running Switchyard jobs. | Queue is empty; can remain dormant or be cleaned up. |
| **Director Scripts** | `C:\AI\director\scripts\llama_swap_keepalive.ps1:1` | Comment mentions "Switchyard's model loader". | Clean comment header to reference llama-swap. |
| **Director Source** | `C:\AI\director\src\director\switchyard\` | Entire Switchyard source module (`runnerlock.py`, `cli_ops.py`, etc.). | Move to dated archive `C:\AI\_archive\20261026_switchyard\director_src_switchyard\`. |
| **Standalone Folder** | `C:\AI\switchyard-upgrade\` | Git worktree / branch of Switchyard upgrade. | Move to dated archive `C:\AI\_archive\20261026_switchyard\switchyard-upgrade\`. |
| **Standalone Folder** | `C:\AI\agy-fix-switchyard-2026-10-14\` | Oct 14 fix scripts for Switchyard. | Move to dated archive `C:\AI\_archive\20261026_switchyard\agy-fix-switchyard-2026-10-14\`. |
| **Strata Launchers** | `C:\AI\strata-0.2.2\sy_strata_launch.py` | Legacy naming for Strata launch wrapper. | Superseded by llama-swap's direct Strata process management. |
| **Community Scripts** | `C:\AI\community\scripts\sy_1min.py`, `sy_graph.py`, `p6.py` | Legacy comparative test scripts (P6 benchmark). | Off-limits per AGENTS.md. Archived or left untouched for compile check only. |
| **Community Scripts** | `C:\AI\community\scripts\comm.py:1` | Comment header `# Community-path helper (ALI-52 P2-P6). Stock ComfyUI API only; Switchyard untouched.` | Clean comment. |

---

## 3. Repointing Plan Execution
1. Model Swapping: Ensured 100% on `llama-swap` (`http://127.0.0.1:8080/v1/models`).
2. Renders: Ensured 100% on ComfyUI via `comm.py` / `run_graph_job.py` with `guard_ok` validation.
3. Archival: Move `C:\AI\switchyard-upgrade` and `C:\AI\agy-fix-switchyard-2026-10-14` to `C:\AI\_archive\20261026_switchyard\`.
4. Verification: Test `curl http://127.0.0.1:8080/v1/models` and `curl http://127.0.0.1:8080/comfyui/system_stats`.
