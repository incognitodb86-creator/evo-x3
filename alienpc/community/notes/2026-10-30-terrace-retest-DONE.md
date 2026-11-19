# 2026-10-30 terrace-retest queue - DONE (Forge, autonomous run on Derek's 9:40 PM word)
Plan `plans\2026-10-29-terrace-retest-plan.md`; briefs 2 and 3. Built and self-checked before any render (15 arms, 15 PASS, 0 DROP - `notes\terrace_retest_arms_self_check.txt`, table `notes\2026-10-29-terrace-retest-diff.md`). **No arm dropped, no arm hand-edited, no settings changed to make anything pass.**

## What ran
14/15 graphs queued through `run_graph_job.py --frames 124`, one job at a time, each behind `gpu_guard` IDLE and `gpu-render.lock`; `test_p6_review.py` + `test_guard_scope.py` passed (26) before every single render, and `comm.guard_ok` runs inside the runner. All 14 came back OBJECTIVE ok at 124 frames. 0 recoveries needed: no JOB error, no OOM, no WinError 1450, no ComfyUI crash, no stall, no redo. Nothing was killed; llama-swap, strata and the pi-mobile hub were never touched.

| arm | seed | judged file | judged WxH | frames (ffprobe / OBJECTIVE) | audio | wall s | harness s | MB | judge flags | dropped/why |
|---|---|---|---|---|---|---|---|---|---|---|
| b2_s51083002 | 51083002 | terrace_retest_b2_s51083002.mp4 | 768x1344 | 124 / 124 | True | 140.9 | 180.1 | 2.31 | precheck:static_no_transition; vlm:start_kept,target_reached; zoom:none | - |
| b2_s51083012 | 51083012 | terrace_retest_b2_s51083012.mp4 | 768x1344 | 124 / 124 | True | 162.3 | 180.1 | 2.32 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| b2_s51083013 | 51083013 | terrace_retest_b2_s51083013.mp4 | 768x1344 | 124 / 124 | True | 140.5 | 180.1 | 2.42 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s1_s51083002 | 51083002 | terrace_retest_s1_s51083002.mp4 | 768x1344 | 124 / 124 | True | 141.8 | 180.1 | 2.34 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s2_s51083002 | 51083002 | terrace_retest_s2_s51083002.mp4 | 768x1344 | 124 / 124 | True | 130.5 | 180.1 | 2.35 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s3_s51083002 | 51083002 | terrace_retest_s3_s51083002.mp4 | 768x1344 | 124 / 124 | True | 144.6 | 180.2 | 2.31 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s4_s51083002 | 51083002 | terrace_retest_s4_s51083002.mp4 | 768x1344 | 124 / 124 | True | 125.1 | 180.1 | 2.21 | precheck:static_no_transition; vlm:target_reached; zoom:none | - |
| s5_s51083002 | 51083002 | terrace_retest_s5_s51083002.mp4 | 768x1344 | 124 / 124 | True | 138.8 | 180.2 | 2.22 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s6_s51083002 | 51083002 | terrace_retest_s6_s51083002.mp4 | 768x1344 | 124 / 124 | True | 129.0 | 180.1 | 2.30 | precheck:static_no_transition; vlm:target_reached; zoom:none | - |
| s7_s51083002 | 51083002 | terrace_retest_s7_s51083002.mp4 | 768x1344 | 124 / 124 | True | 142.7 | 180.2 | 2.47 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| s8_s51083002 | 51083002 | terrace_retest_s8_s51083002.mp4 | 768x1344 | 124 / 124 | True | 140.5 | 180.2 | 2.30 | precheck:static_no_transition; vlm:target_reached; zoom:none | - |
| t4c_s51083002 | 51083002 | t4c_s51083002_raw.mp4 | 768x1344 | 124 / 124 | True | 126.8 | 181.4 | 2.32 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| t4c_s51083012 | 51083012 | t4c_s51083012_raw.mp4 | 768x1344 | 124 / 124 | True | 115.5 | 120.1 | 2.46 | precheck:static_no_transition; vlm:target_reached; zoom:none | - |
| t4c_s51083013 | 51083013 | t4c_s51083013_raw.mp4 | 768x1344 | 124 / 124 | True | 140.2 | 180.2 | 2.21 | precheck:static_no_transition; vlm:start_kept; zoom:none | - |
| t4g_s51083002 | 51083002 | - | ? | ? / None | None | None | None | 0.00 | none | not rendered (optional cell) |

Two clocks are printed on purpose. `harness s` is the runner's own number and is **quantized to the 60 s /history poll** (`comm.py POLL_SEC = 60`, and the loop sleeps before the first check), so every job reads 180.1-180.2 s - it is a ceiling, not a measurement, and it is why S6 at 6 steps and S4 at `ref_image_size: match` look identical to B2. The honest number is `wall s` = the job's last output write by ComfyUI (its own output dir, untouched by the copies into run dirs) minus JOB start; the comfyui_auto wake is inside it. On that clock every arm lands in the same band, so nothing here is >30 % slower than its reference, and the plan's runtime-overrun condition is met by no arm. The spread inside the band (a few seconds) is not resolvable at this poll rate; measuring it needs a tighter poll, which is Max's file to change.

T4c arms write two files: the graph's own processed output (`terrace_retest_t4c_*.mp4`, after RTX x1.2 + grain + crf18 inside the graph; ffprobe reports 768x1344 or 920x1616 across the three) and the `_raw` file at **768x1344** that the plan says to judge. The judged file column shows the `_raw` copy for T4c, as briefed. The runner's OBJECTIVE check landed on whichever of the two the history reported first, so both are collected into each run dir as `<arm>_raw.mp4` and `<arm>_processed.mp4`.

## Judge (flags only - never a KEEP, no scoring by Forge)
Ran the whole recommended tier per clip: `judge\prechecks.py` (CPU, DINOv2/CLIP vs the start frame), `judge\vlm_judge.py` (qwen3vl, 5 absolute checks) and `judge\vlm_variants.py --variants Z` (the worst-frame zoom). Outputs: `review\terrace-retest-2026-10-29\judge_out\`, summary `judge_flags.json`.

- `static_no_transition` on 14/14 rendered clips: b2_s51083002, b2_s51083012, b2_s51083013, s1_s51083002, s2_s51083002, s3_s51083002, s4_s51083002, s5_s51083002, s6_s51083002, s7_s51083002, s8_s51083002, t4c_s51083002, t4c_s51083012, t4c_s51083013
- `start_kept` on 10/14 rendered clips: b2_s51083002, b2_s51083012, b2_s51083013, s1_s51083002, s2_s51083002, s3_s51083002, s5_s51083002, s7_s51083002, t4c_s51083002, t4c_s51083013
- `target_reached` on 5/14 rendered clips: b2_s51083002, s4_s51083002, s6_s51083002, s8_s51083002, t4c_s51083012
- the worst-frame zoom (`--variants Z`, the README's recommended FLAG tier addition) is **clean on 14/14 rendered clips** - it compares the 2 most-changed frames against the start frame, region by region, for background swap and anatomy, and found neither. The combined FLAG tier therefore reduces to the VLM's hard answers, which are the non-informative ones below.

**These flags carry no signal for this cell, and the pass rule must not be read off them.** `static_no_transition` fires on 14/14 and is a fitted threshold for one-ref clips that should leave the start pose - this cell has no target pose by design. `target_reached` is inapplicable for the same reason, and it fired on 5/14 across unrelated arms. `start_kept` fired on 10/14 including all three B2 seeds, so it separates nothing between systems. Nothing in the judge tier measures identity drift over time or the flicker S4 tests - the box has no face-embedding instrument (recorded in the notes on 2026-10-28). Brief3 asks for seed follow-ups on any Stage-2 arm whose flags are strictly fewer than the reference's: read literally that selects **8 of 8** Stage-2 arms (s1_s51083002, s2_s51083002, s3_s51083002, s4_s51083002, s5_s51083002, s6_s51083002, s7_s51083002, s8_s51083002), i.e. 16 more renders driven by a signal that is uniform here. That is a decision, not a fact, so it was not run; the deciding instrument is Derek's blind 0-10 scores of the pack (`review\terrace-retest-2026-10-29\pack\`, 14 neutral ids, key in `key.csv`).

## Standing
GPU lock released, box IDLE. B2 stays the default graph (`p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json`); adoption needs mean > B2 by 1.0 on Derek's scores, wins on 2 of 3 seeds, zero negative-control failures - S4 is the negative control and its clip is in the pack. `t4g` (the guides-on stock variant) is built and NOT rendered: it is the optional cell, Max's call. Full arm diff: `notes\2026-10-29-terrace-retest-diff.md`; per-arm widget diffs: each run dir's `graph_diff.txt`.
