# Plan: NOW-P2 — A/B numbers for the 4 published switches (clip-11 vs the switch set)

## Goal
Give Derek the before/after evidence for the four published switches on the one clip where they are
the only variable: `ali163_hc15_bd002_s51150011` (BEFORE, rendered 2026-10-24 19:54, 571.7 s) vs
`ali163_hc15_bd002_s51150021` (AFTER, steps 12, pytorch attention, ref_image_size match, antiburn
LoRA 0.5 on the continuation only). Deliver the frame-0 SSIM/PSNR + ArcFace numbers, the full
before/after comparison, and a labelled contact sheet. No render: BOTH clips are already paid for.

## Measured starting state (read off disk 2026-10-26)
- `runs/ali163_hc15_bd002_s51150021/` has the mp4: 6,297,740 B, 1344x768, 24/1, 362 packets, audio.
- Its `objective.json` carries `"attempts": []` and `status.log` ends in poll-warn lines: the client
  stalled, the runner recorded nothing. The clip exists: ComfyUI
  `output/community/ali163_hc15_bd002_s51150021/` holds **7 byte-identical mp4s** (sha256 prefix
  `b8d0b7b8e8b9bbe4`, mtimes 2026-10-24 22:11 → 2026-10-25 03:12), and the runs copy has the same
  sha. That is the pre-RENDER-TIMEOUT re-queue burn this repo already fixed and measured.
- Frame-0 numbers for the BEFORE clip already exist in `notes/hc15_audit/metrics.json`
  (SSIM 0.915424 cover / PSNR 29.580949, ArcFace best_cos 0.875 / 0.748).
- `notes/ali163_hc_final_check.py` / `notes/ali163_hc_final_sheet.py` are hard-coded to the 2026-10-23
  roster, so they cannot measure this pair. `notes/hc15_anchor_fix_build.py` already carries the
  frame-0 metric machinery (`probe`/`extract`/`fit`/`ssim_psnr`, `hc_r4f_facelib`), the A/B graph
  diff (`diff_paths`, `NOW_ALLOWED`) and NOW-P1's `--now-*` modes.

## Files (scope)
- `C:/AI/community/notes/hc15_anchor_fix_build.py` — extend with `--ab-metrics`, `--ab-sheet`,
  `--ab-note`, `--ab-check`, `--ab-selftest` (one builder per line, no new script).
- `C:/AI/community/notes/hc15_audit/ab_metrics_20261026.json` — generated numbers (git-tracked;
  `runs/` is gitignored, L8/L20).
- `C:/AI/community/notes/hc15_audit/now_p2_ab_sheet.png` — labelled sheet, and a copy in
  `runs/ali163_hc15_bd002_s51150021/` (the review surface Derek opens).
- `C:/AI/community/notes/now_p2_before_after_20261026.md` — the human surface, generated from the JSON.
- `C:/AI/community/notes/progress.md`, `fix_plan.md`, `AGENTS.md` (learning line).

## Method (no GPU, no queue)
1. For each id: `ffprobe -of json` (frames/canvas/fps/duration/audio, second unfiltered pass for
   audio), `ffmpeg` frame extract at 0/181/361 and at the 5 sheet timestamps, SSIM + PSNR against the
   start still in both fit modes (cover, stretch), CPU SCRFD-10G + ArcFace cosine of each start-still
   face vs the best face in the frame (`notes/hc_r4f_facelib.py`, needs onnxruntime →
   `C:/Program Files/Python312/python.exe`; the director venv has none, L16).
2. Graph settings read out of the two `.api.json` files, and `diff_paths(before, after)` required to
   equal `NOW_ALLOWED` (the 4 switches + the LoRA wiring + the save prefix) — so the A/B is provably
   one variable set, with byte-identical prompts, seed 51150001, start frame and face crops.
3. Sheet: start still + frame 0 of each clip (labelled with the measured SSIM/PSNR) + a 5-timestamp
   contact strip per clip, all labels printed by ffmpeg/PIL. Builder-only: no vision judge, no score,
   no pick on rendered explicit output.

## Gate (named detectors + non-vacuity)
`--ab-check` = 13 named detectors over the artifacts: pair on disk + shape, graph scope = exactly
`NOW_ALLOWED`, seed/prompts/start identical, every frame measured with finite numbers, the BEFORE
row reproduces `metrics.json` frame 0 within 1e-4 (so the two measurement passes are comparable),
frame 0 is the max-SSIM frame of the three, ArcFace floor 0.45, the render receipt (N identical
copies, all sha equal to the runs copy, 0 `JOB end` rows, `attempts: []`, and the doc disclosing the
stall + collected-from-disk + never re-rendered), sheet fresh/large/labels both ids, 0 KEEP-words and
the KEEP-is-Derrick's line, doc bytes == regenerated doc (no number drift), citations verbatim in
`notes/web/`, builder source carries no GPU/socket token, artifacts git-tracked.
`--ab-selftest` seeds each fault (old-id pair, a switched value back to the old one, a prompt edit,
a None metric, a broken repro, frame 0 not the best, a cosine under the floor, a doc that claims
`objective ok=true`, a stale sheet, a KEEP word, a hand-edited doc, a fake quote, a socket token, an
untracked artifact) and requires every detector to fire on its own seed and 0 on the real tree.

## Done when
`--ab-metrics` prints `FRAME0_BEST_COS` + `GATE_FLOOR n=0.45` + `AB_METRICS_JSON`, `--ab-sheet` prints
the sheet path, `--ab-check` prints `ALL 13 PASS`, `--ab-selftest` prints
`SEEDS_FIRED n/N REAL_CLEAN`, and pytest p6 21 passed + `check_web_saves.py` 0 +
`ali05_loop_check.py` 0 + `ali06_learnings_check.py` 0. fix_plan ticked with the measured numbers.
KEEP is Derek's alone: the doc and sheet carry no verdict, and no ranked row goes in fix_plan.

## LANDED 2026-10-26 (this pass: verify + commit + tick; 0 renders)
The build pass stopped with `ab_metrics_20261026.json`, the doc, the sheet meta and the extended builder STAGED-UNCOMMITTED
and fix_plan NOW-P2 unticked, so by L8/L20 the evidence was one pass boundary from death. This pass re-ran every gate on the
live tree and landed it: `--ab-check` = `CHECKS real ALL 15 PASS`, `--ab-selftest` = `SEEDS_FIRED 20/20 REAL_CLEAN`,
`test_p6_review.py` 21 passed, whole suite 38, `check_web_saves.py` CLEAN 172, `ali02_citation_check.py` 0 problems,
`ali05_loop_check.py` VERDICT CLEAN, `ali06_learnings_check.py` RESULT CLEAN (31 write-up lessons; Lesson 31 carries the
reproduce-before-you-report + media-identity rule with `AGENTS: none` - AGENTS.md is at its 39-line cap, O.2 owns compaction).
Two real defects were closed in the worktree over the staged builder: (1) the doc/label delta formatters raised a real-data
TypeError on a frame with no detected face (a None cosine inside the format operator) - both are None-safe now and the
"5 measured: a None metric" seed fires; (2) the NO-GPU seed appended the literal token its own detector greps, so the seed
was red for the wrong reason - it now builds the token from two pieces and only its own seeded copy is red.
The plan's own "Done when" list is met in full: FRAME0_BEST_COS + GATE_FLOOR n=0.45 + AB_METRICS_JSON, the sheet path,
ALL 15 PASS (the gate grew from 13 to 15 named detectors: 14 NO-GPU and 15 DURABLE were added by the build pass), and
SEEDS_FIRED 20/20 REAL_CLEAN. The item is ticked with the numbers. No verdict, no ranked row, KEEP is Derrick's alone.
