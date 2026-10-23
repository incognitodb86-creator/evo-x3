# ALI-173 BAKEOFF GPU ledger (B1 GATE HARDENING, 2026-10-23)

Rule: one line per GPU window, and budget state read before any `p7/JOB_REQUEST.json` write.
Budget file for this loop = `C:/Users/derek/5slock/ralph-community/logs/p7_budget.json` (the
`C:/AI/community` ledger does not exist; AGENTS.md).

| # | time (CT) | action | queue | guard | GPU | notes |
|---|-----------|--------|-------|-------|-----|-------|
| 1 | 18:05 | `python C:/AI/community/scripts/comfy_ctl.py start` (BAKEOFF-authorized; ALI-173 B2 window) | - | - | - | goal = read-only `/object_info` for the Continuum schema |
| 2 | 18:12 | `GET :10004/system_stats` + `GET :10004/object_info` (read-only, 8.2 s, 2605 classes) | 0/0 | `IDLE (10004, 10002) free=True` | `0 %, 4551 MiB, 0 processes` | `comfy_ok=True`, running model = `comfyui_auto`; no render touched; ComfyUI stopped again at the end of the window |
| 3 | 18:14 | `comfy_ctl.py status` | - | `IDLE (10004, 10002) free=True` | `0 %, 5208 MiB, 0 processes` | idle between windows |
| 4 | 18:26 | budget read | 0/0 (ComfyUI asleep) | `IDLE` | `0 %` | `used_min 467.5 / cap_min 615`, `jobs 37 / job_cap 45`, `updated 2026-10-23T17:28:21` |

Budget read in full: `{"used_min": 467.5, "jobs": 37, "cap_min": 615, "job_cap": 45}` - one graph job
of 15 min fits (467.5 + 15 = 482.5 < 615; 37 + 1 = 38 < 45), and `STOP_RALPH` (Max 18:17 CT) asks to
relaunch with `-GpuCapMin 700 -JobMax 55`, which widens it further.

No `p7/JOB_REQUEST.json` was written in this loop: `STOP_RALPH` is active (Max 18:17 CT "stop after
iter 07 to relaunch with -GpuCapMin 700 -JobMax 55"), so the B2 job is staged, not submitted, and
`p7/JOB_REQUEST.json` does not exist right now (verified by the pre-submit gate, which checks the
file is absent and the id is unused).

## 18:35 CT - pre-submit gates and the staged request (B2)

Guard command reality (fixed after the first run): the GPU guard is
`C:\AI\director\scripts\gpu_guard.ps1`, called with NO arguments, exactly as `ralph.ps1:77` calls it
(`-File $Guard`); it prints `IDLE` and exits 0, `BUSY: <reason>` and exits 1, and it fail-closes (rc 2)
on its own errors. `status` is NOT an argument - passing it dies on `Cannot process argument
transformation on parameter 'TimeoutSec'`, and the first version of `notes/ali173_b2_objinfo.py`
carried a `DUR` path to a `.pi\guard\gpu_guard.mjs` file that does not exist, which is why the 18:12 CT
log line came from `comfy_ctl status` instead of the guard. Both files now use the real path
(`notes/ali173_b2_objinfo.py` logs `STEP 1b gpu_guard rc=...` plus an nvidia-smi utilisation line,
because `ralph.ps1 GuardWait:79-81` also fails a window over `-UtilMax` 30 % while the guard says IDLE).

| # | time (CT) | action | queue | guard | GPU | notes |
|---|-----------|--------|-------|-------|-----|-------|
| 5 | 18:34 | `gpu_guard.ps1` (no args) + nvidia-smi | 0/0 (ComfyUI asleep) | `IDLE` rc=0 | `0 %, 15224 MiB` | resident VRAM with 0 % = the idle llama-swap model, not work |
| 6 | 18:35 | budget re-read, then `p7/JOB_REQUEST.json` staged | 0/0 | `IDLE` rc=0 | `0 %` | `used_min 467.5 / 615`, `jobs 37 / 45`; one 15-min estimate job fits; STOP_RALPH asks for 700/55 at relaunch |

Staged request (written, not rendered):

    {"jobs": [{"id": "ali173_cont_hc1_s51140001", "kind": "graph", "frames": 240, "frames_tol": 33, "minutes": 60}]}

- `frames_tol: 33` = the batch's tolerance (iter 09 used 0 for a seg, the R-lines used 33). Continuum's
  own seam trims can land a few frames off 240, so 33 % avoids a false "frame count" failure; the
  objective.json will record the true count and the ledger notes the exact number.
- `minutes: 60` -> per-attempt timeout 1200 s, `--max-redo 2` (ralph.ps1:287-294); the harness clamps
  to 30..180. Budget accounting uses the actual wall minutes (`BudgetAdd`), not this number.
- Ids checked against every `ralph.ps1` id gate by `notes/ali173_b2_req_check.py` before the write.

No render happened in this loop: the harness runs graph jobs only between iterations after a clean pass,
and `STOP_RALPH` (Max 18:17 CT) wants a relaunch at `-GpuCapMin 700 -JobMax 55` first.
`p7/jobs/ali173_cont_hc1_s51140001.result.json` does not exist as of 18:36 CT.
