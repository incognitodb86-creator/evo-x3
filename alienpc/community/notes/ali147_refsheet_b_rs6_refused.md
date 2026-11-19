# ALI-147 RS6 - REFSHEET_B render was REFUSED by the harness job-id gate (no GPU used)

Task: `- [ ] RS6 Render REFSHEET_B (GPU). Check: as RS4 for ali147_pool_refsheet_b_s51080000, plus sbs_refsheet_refsheetb.mp4 and stills at frame 0`.
The RS6 request half ran last iteration (notes\ali147_refsheet_b_rs6_request.md, precheck notes\ali147_refsheet_b_rs6_precheck.py = ALL CHECKS PASS). This iteration was for the verification half. Result: **the render never started** - the harness refused the job id, so there is nothing to verify. No objective item of RS6's check is testable.

## Evidence (all read-only, 2026-10-22 18:47 CT)
- `logs\ralph.log`: `2026-10-22T18:44:28 iter 02 start` / `18:46:32 iter 02 exit 0` / `2026-10-22T18:46:35 P7 job refused: bad id 'ali147_pool_refsheet_b_s51080000'` / `18:46:41 iter 03 start`. This is the only `refsheet_b` line in ralph.log (`grep -c refsheet_b ralph.log` = 1) - no `P7 job ... start`, no `ok=`.
- My request was well-formed and is archived verbatim as `p7\jobs\request_iter02.json` (119 B, 18:45):
  `{"jobs": [{"id": "ali147_pool_refsheet_b_s51080000", "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}]}` - one job, the exact form the spec and the RS6 line give.
- `p7\jobs\` has **no** `ali147_pool_refsheet_b_s51080000.result.json` / `.out` / `.err.out` (full listing read). A refusal at the id gate writes no result.json (ralph.ps1:184 `continue`s before `JobResult`).
- `runs\ali147_pool_refsheet_b_s51080000\` contains only RS5's `request.api.json` (12,144 B, 26 nodes) and `graph_diff.txt` (8,211 B). No `status.log`, no `objective.json`, no `<id>.api.json`, no mp4, no `*_stills_contact.png` - consistent with "never submitted".
- Not a budget refusal: `logs\p7_budget.json` = used_min 259.3 / cap_min 390, jobs 21 / job_cap 27 (updated 18:22:13). The id gate (ralph.ps1:184) runs before the budget gate (:187). Not "id already used", not gpu-busy, not a missing request.api.json.

## Root cause: ralph.ps1 job-id regex rejects any underscore in the arm segment
- `ralph.ps1:184` (all job kinds): `if($id -notmatch '^(p7_[a-z0-9_]{3,48}|ali147_pool_[a-z0-9]+_s\d+)$'){ Log "P7 job refused: bad id '$id'"; continue }`
- `ralph.ps1:265` (kind graph/dip, second gate): `if($id -notmatch '^ali147_pool_[a-z0-9]+_s\d+$'){ JobResult ... 'refused: graph/dip ids are ali147_pool_<arm>_s<seed>' }`
- The `p7_` branch allows underscores (`[a-z0-9_]{3,48}`); the `ali147_pool_` branch does not (`[a-z0-9]+`). Verified in Python (script `notes\ali147_refsheet_b_rs6_idcheck.py`, py_compile clean, output):
  - `ali147_pool_ctrl_s51080000` gate1 True, gate2 True (rendered)
  - `ali147_pool_refsheet_s51080000` gate1 True, gate2 True (rendered - no underscore in the arm)
  - `ali147_pool_refsheet_b_s51080000` **gate1 False, gate2 False**  <- the id every RS5/RS6/PV2 line names
  - `ali147_pool_refsheetb_s51080000` gate1 True, gate2 True (an underscore-free arm segment passes)
- So arm 5b is unrenderable through this harness as named. The same gate will refuse the planned PV2 ids that contain an underscore (`ali147_pool_pv2_hmpussy_s51080002` - PV2-4, already [!] for card L1).

## Two fixes, both Max's (not Forge's)
1. **Harness (smallest, keeps every path/name as planned):** in `C:\Users\derek\5slock\ralph-community\ralph.ps1` lines 184 and 265 widen the arm segment `[a-z0-9]+` -> `[a-z0-9_]+` (as the `p7_` branch already does). ralph.ps1 is Max's per PROMPT.md ("a ralph.ps1 bug is [!] + BLOCKED"), so Forge did not touch it. After the widening, re-writing the identical JOB_REQUEST.json is enough - the id is still free (no result.json, no `<id>.mp4`), so no `*.failed-20261022` move is needed.
2. **Rename the arm** to an underscore-free id (`ali147_pool_refsheetb_s51080000`): needs the arm folder moved, `request.api.json`'s `SaveVideo filename_prefix` (and any `LoadImage`-free paths) rewritten, and `graph_diff.txt` regenerated against RS5 - a naming decision that touches what RS5's tick records (24/26 byte-identical nodes, prefix = the new id) and REPORT.md. Forge did not do it unilaterally (no move is covered by the TASKS.md failed-job rule; the id is named in the task lines).

## State left for the next iteration
- `p7\JOB_REQUEST.json` is **absent** (the harness consumed it at 18:46:35 and archived it as `request_iter02.json`). Forge did not re-write the identical request: the same id is refused by a static regex, so it would be refused again with no new information, and PROMPT.md allows one request per iteration for work the harness can run.
- The RS5 graph is intact and preflighted: `runs\ali147_pool_refsheet_b_s51080000\request.api.json` (12,144 B) + graph_diff (only c0 `ref_images.ref_image_2` = ["sheet",0], c0 `ref_image_size` match -> max, the c0 subject_definitions block, `filename_prefix`), adults-only guard passes on both prompts, both LoadImage strings resolve inside `ComfyUI\input` (start still `community/POOL_768x1344.png` 9cf9ff95..., sheet `community/RS016_portrait_1152x2016.png` da0b6a0b...), seed 51080000, steps 10, 768x1344, 24 fps, frame target 481. Baselines for the render-secs comparison stay REFSHEET 902.7 s / FIX1 857.5 s / CTRL 809.7 s.
- `sbs_refsheet_refsheetb.mp4` and the frame-0 opening stills are Max/harness files (`run_graph_job.py` has no hstack path; its contact sheet for a 481-frame clip covers only frames 204-276 + 444/456/468/480), so per the TASKS.md sbs rule they are "pending Max" and never a gate for Forge.

METHOD_ONLY. No GPU/ComfyUI/llama-swap call, no ffmpeg, no render run by Forge. KEEP is Derrick's only.
