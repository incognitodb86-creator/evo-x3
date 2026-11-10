# Flash Cleanup Continuation Report

## Date
2026-11-09

## Summary
Completed cleanup of the three leftover continuation items per `briefs/2026-11-09-flash-cleanup-continuation.md`:
1. Removed `plan_continuation_chain` entirely; callers and tests now use `_layout_chain` or `continuation_layout` directly.
2. In `submit_parody_run.py`, removed the leftover `plan_c2v_chain` metadata call on the 2+ `--beat` path. Updated module docstring and CLI `--beat` / `--seconds` help text to describe one native continuation graph rather than stitched cells, while preserving single-shot accuracy and long-seconds refusal without beats.
3. Sized the 2+ `--beat` chain with omitted `--seconds` from `continuation_layout` defaults (192 base frames, 187 extension frames, sampled window 209 frames <= 243 ceiling) rather than `plan_cells`. The 2-beat default exactly matches the verified 379-frame layout. Single-shot graphs remain byte-identical to the baseline.
4. Obeyed all hard limits: no commit, no render, no ComfyUI queue, no new flags or nodes, and touched only the three designated files plus this report.

## Key Findings
- **2-Beat Default Frame Total:** **379 frames** (15.7917 seconds at 24 fps).
  - Beat 1 (Base `c0`): 192 frames (8.0000 s).
  - Beat 2 (Continuation `c2`): 22 overlap frames (hidden), 187 extension frames (7.7917 s).
  - Sampled Window: $22 + 187 = 209$ frames ($\le 243$ ceiling).
  - Cumulative Output: $192 + 187 = 379$ frames.
- **Changed Files & Functions:**
  - `scripts/parody/build_request.py`:
    - Added constants `DEFAULT_CONTINUATION_BASE_FRAMES = 192` and `DEFAULT_CONTINUATION_EXTENSION_FRAMES = 187`.
    - `continuation_layout`: Added defaults `base_frames: int = 192, extension_frames: int = 187`.
    - Removed `plan_continuation_chain` function entirely.
    - `build_continuation_request`: Uses `_layout_chain` directly and defaults omitted beat frames to `DEFAULT_CONTINUATION_BASE_FRAMES`.
  - `scripts/parody/submit_parody_run.py`:
    - Updated module docstring to describe 2+ `--beat` as building one native continuation graph.
    - `submit_parody_job`: Bypasses `plan_cells` on `is_multi_beat`, sets up beat specifications and previews total frames using `_layout_chain`. Omits `plan_c2v_chain` call on the 2+ `--beat` path.
    - `main`: Updated `--beat` help text ("repeat 2+ for one native continuation graph, not stitched cells") and `--seconds` help text ("single shot up to the measured ceiling of 243 frames / ~10.1s; longer asks require 2+ --beat").
  - `scripts/parody/test_parody_dynamic.py`:
    - `test_multi_beat_shared_anchor_cells`: Replaced call to `br.plan_continuation_chain` with `br._layout_chain`.
    - Added `test_plan_continuation_chain_removed`: Asserts `plan_continuation_chain` is absent from `build_request`.
    - Added `test_continuation_layout_defaults_match_verified_379_layout`: Asserts `continuation_layout()` default returns the 379-frame layout with 209-frame sampled window.
    - Added `test_two_beats_omitted_seconds_uses_continuation_defaults`: Verifies `submit_parody_job` with 2 beats and omitted `--seconds` does not call `plan_c2v_chain` and yields exact 379 total frames.
- **Test Counts:**
  - Command: `C:\AI\director\.venv\Scripts\python.exe -m pytest C:\AI\community\scripts\parody -q --tb=short`
  - Results: **113 passed, 2 failed** (115 collected).
  - The 2 failures are the pre-existing known beat-sheet doc checks (`test_beat_sheet_c2v_unproven_marking` and `test_beat_sheet_methods_specified` in `test_longclip_beats.py`).
  - `test_parody_dynamic.py`: **36 passed, 0 failed**.
- **Single-Shot Byte-Identical Verification:**
  - `test_single_shot_byte_identical_and_locked_dials` passed cleanly with matching SHA256 hashes:
    - Graph: `949666d54685f2e94979841e0c5a925a40486bf44f44e3c563941a462270dee8`
    - Prompt: `521ba2341a7c135bfb4831b95d6688441fc029d234e1c223e065a49d2b9a3b50`

## Action Items
- None. All three leftover items have been cleaned up and verified.
