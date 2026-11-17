# Flash High cleanup: drop leftover names, then stop (no commit, no render)

Repo: C:\AI\community, branch docs/parody-identity-docs-20261106, HEAD cc26413. The 3 uncommitted files already have the verified native continuation. Backup first to C:\AI\_archive\2026-11-09-flash-cleanup-backup\. Edit only scripts/parody/build_request.py, submit_parody_run.py, and test_parody_dynamic.py. No other files, no docs, no commits, no render, no ComfyUI queue, no new flags or nodes. Do not touch run_queue.py, AGENTS.md, c2v_chain.py, or any sydney folder.

Do only these three:

1. Remove the name `plan_continuation_chain` entirely. Callers and tests must use `_layout_chain` or `continuation_layout` directly.

2. In submit_parody_run.py, remove the leftover `plan_c2v_chain` metadata call on the 2+ `--beat` path. Fix help text and docstrings on that path so they describe one native continuation graph, not stitched cells. Do not change stitch behavior for the no-beats long-seconds case, which is already refused; leave single-shot help accurate.

3. When 2+ `--beat` are given and `--seconds` is omitted, size the chain from `continuation_layout` defaults (one window per beat, each sampled window <=243 frames), not `plan_cells`. The 2-beat default should match the verified 379-frame layout if that is already the default; report the exact frame total. Single-shot graphs must stay byte-identical to the current (and 3c801f1) builder.

Do not bring back `plan_beat_windows`, `_split_frames`, or `test_parody_continuation.py`.

Run `C:\AI\director\.venv\Scripts\python.exe -m pytest C:\AI\community\scripts\parody -q --tb=short`. The 2 known beat-sheet doc failures may remain. Save a short report of changed functions, test counts, and the 2-beat default frame total to briefs/2026-11-09-flash-cleanup-continuation-report.md.

Stop when it works. If the small approach fails, report it; do not redesign.
