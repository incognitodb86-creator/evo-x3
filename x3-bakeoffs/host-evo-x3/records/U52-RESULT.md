# U52 Result: U51 Edits Applied with Beta7 Corrections

**Date:** 2026-11-16  
**Scope:** Applied all 7 U51 edits with the U51-beta7 corrections across `/home/evo/AI/community` and `/home/evo/AI/render`. Nothing was queued or rendered; no secrets, images, PixlStash contents, or Sydney data were accessed.

---

## 1. Edits Summary (1–7)

1. **Edit 1 (`build_request.py`) — DONE**
   - Added `align_h3_frames(frames, max_frames=None)` matching ComfyUI's `align_frame_count` (`while f % 17 != 5: f += 1`, raising `ValueError` for `< 1` or `> 243`).
   - Wired `align_h3_frames` into `validate_single_clip_frames` and `main()`.
   - Made advisory/passthrough the default for `build_writer_request(..., strict=False, advisory=None)`: writer sections/prose pass through verbatim with no rewriting, stripping, reordering, or section injection; rule checks (`lint_writer_prompt`, `check_writer_consistency`, `overall_soundscape:` / `non_diegetic_music:` header warning, `validate_hook_ask` / `resolve_brief` warnings) go to `report["warnings"]` and `report["flags"]`. Hard stops left: 18+ (`_MINOR_RE`, `_YOUTH_GATE_RE`, `_UNDER18_AGE_RE`, `_adult_age_ok`), empty/refused writer output (`WriterRefusal`), and missing still / RefMod / graph errors.
   - Removed the `"; all characters are consenting adults."` injection from `finalize_writer_prompt`.
   - Stopped `convert_speech` from dropping spoken lines on `max_lines` or `budget` (all lines are kept in `pieces` with `kept: True`).
   - Removed silent stripping of `overall_soundscape:` and `non_diegetic_music:` headers in `finalize_writer_prompt`; both headers are preserved with a loud `! WARNING` when present.

2. **Edit 2 (`run_queue.py`) — DONE**
   - Updated `graph_expect(g)` to inspect `MiniMaxH3ReferenceToVideo`, `MiniMaxH3ImageToVideo`, and `EmptyMiniMaxH3LatentAV` in priority order.
   - Applied ComfyUI's `17n+5` frame alignment (`while f % 17 != 5: f += 1` for `f >= 1`) to the base node's `length` before adding `MiniMaxH3GuidedContinuationWindow` `extension_frames`.

3. **Edit 3 (`render_writer_pipeline.py`) — DONE**
   - Snapped explicit `--frames` via `br.align_h3_frames(int(job["frames"]))` in `run_clip` **before** `slots.json`, `brief_block`, and the writer LLM call so the writer sees the aligned length (`120 -> 124`).
   - Removed the automatic `rewrite` / `rewrite_block` / `rewrite_builder` retry loops; gated a single retry behind `--fix-once` (default `False`).
   - Kept the writer's output verbatim (stopped calling `clean_prose` and `normalize_prose` in `run_clip`; multi-section writer outputs pass through untouched via `_materialise_writer_text`, while headerless single-paragraph outputs keep their text verbatim inside `assemble_output`).
   - Downgraded `surface_mismatch` (`cowgirl` / `reverse_cowgirl` on waist-high surface) and `missing_inherited_ending_state_pose` from `_Stop()` (`NOT_READY`) to `result["warnings"]`.
   - Updated `clean_still_read` to return `(dict(d), [])` without mutating captions.
   - Updated `prose_messages` and `brief_block` to explicitly instruct against `overall_soundscape:` / `non_diegetic_music:` headers (R7 / 10Eros-Max beta7).
   - Fixed `summary_line(r)` to report `queued={bool(r.get('submitted'))}` instead of hardcoded `queued=False`.
   - Surfaced `audio_header_beta7` `! WARNING` messages from `wp_lint` into `result["warnings"]`.

4. **Edit 4 (`wp_lint.py`) — DONE (with beta7 correction)**
   - Removed the `[Shot 2+]` ban (`SHOT2_RE` check); replaced it with a soft warning (`shot_timestamp`) when `[Shot N]` (`N >= 2`) timestamps are non-monotonic or exceed `clip_seconds`, and exempted valid `[Shot N] At MM:SS.mmm` cut headers from the `timestamp` check.
   - Reduced `SAFETY_HARD` to `frozenset({"youth_hint", "scale_adult"})`, making all other craft/format/dialogue/act rules advisory.
   - Converted `talk_lines` (3-line minimum) to a soft advisory note (`hard=False`).
   - Added `audio_header_beta7`: emits a loud `! WARNING` (`hard=False`, penalty `HARD_WEIGHT`) whenever `overall_soundscape:` or `non_diegetic_music:` appears, without stripping or blocking.

5. **Edit 5 (`submit_parody_run.py`) — DONE**
   - `submit_writer_run` now defaults to `strict=False` (advisory passthrough) and aligns `frames = br.align_h3_frames(frames)` at entry (`report["frames"]` and `c0.inputs.length` agree).
   - Added `--strict` to `_writer_run_cli` (`submit_parody_run.py writer-run`), defaulting to passthrough (`strict=False`) and using strict checking only when `--strict` is passed.
   - In passthrough mode, `scene_addenda.resolve_brief` `not_ready` messages and `build_writer_request` warnings are recorded in `report["warnings"]` without blocking.

6. **Edit 6 (Instructions, skills, rewriter & writer prompts) — DONE (with beta7 correction)**
   - `/home/evo/AI/render/AGENTS.md`: clarified that skills and craft rules are craft advice (only 18+, empty/refused output, and missing still/RefMod/graph files hard-stop); Render may write `writer_output.txt` directly and call `submit_parody_run.py writer-run` or use `render_writer_pipeline.py` as a helper; removed "builder checks/rejects/rewrites" and "do not edit its writer_output.txt" constraints.
   - `/home/evo/AI/community/skills/h3-prompting/SKILL.md` (the only copy under `/home/evo/AI/community/skills` and `/home/evo/AI/render`): marked R5–R31 (except R4 18+ youth guard) as craft advice; added the `17n+5` frame-grid note (`align_frame_count`, `120 -> 124`, cap `243`); reworded all `(the builder sends these back NOT_READY)` / `(builder W5; do not loosen)` / `gated by` phrases as craft advice while keeping R7 strongest advice citing TenStrip HF #77; fixed citations (R11 `#63` retention format attributed to `Portland01` in beta6 thread #63 rather than TenStrip; `#49` noted as unverified TenStrip authorship; R9 long-prompt TenStrip attribution noted as unverified while keeping the craft advice).
   - `/home/evo/AI/render/rewriter/ref2va-system-prompt.md` and `/home/evo/AI/render/writer_pipeline/writer_prompt.md`: removed `overall_soundscape:` and `non_diegetic_music:` headers from the format, section table, instructions, and complete example, replacing them with R7 plain diegetic sound sentences at the end of `detailed_description`.

7. **Edit 7 (`/home/evo/AI/render/x3/queue-remote.sh`) — DONE**
   - Updated the line 32 busy message from `"GPU busy: ..."` to `"X3 submitter busy: waiting in background; queues automatically when the X3 submit queue frees (log $RUN/_render_queue.log)"`.

---

## 2. Files Changed & Backup Paths

### `/home/evo/AI/community` (Commit `a5025fc3f81956ec8e794bf5c3e4aecc009015b2`, author `Max Architect <max@fleet.local>`)
- `scripts/parody/build_request.py` -> `scripts/parody/_archive/build_request.py.bak-20261116-u52`
- `scripts/run_queue.py` -> `scripts/_archive/run_queue.py.bak-20261116-u52`
- `scripts/parody/render_writer_pipeline.py` -> `scripts/parody/_archive/render_writer_pipeline.py.bak-20261116-u52`
- `scripts/parody/wp_lint.py` -> `scripts/parody/_archive/wp_lint.py.bak-20261116-u52`
- `scripts/parody/submit_parody_run.py` -> `scripts/parody/_archive/submit_parody_run.py.bak-20261116-u52`
- `skills/h3-prompting/SKILL.md` -> `skills/h3-prompting/_archive/SKILL.md.bak-20261116-u52`
- `scripts/parody/test_builder_fixes_t1437.py` -> `scripts/parody/_archive/test_builder_fixes_t1437.py.bak-20261116-u52`
- `scripts/parody/test_modular_s3_and_writer_sys.py` -> `scripts/parody/_archive/test_modular_s3_and_writer_sys.py.bak-20261116-u52`
- `scripts/parody/test_u37_builder_fixes.py` -> `scripts/parody/_archive/test_u37_builder_fixes.py.bak-20261116-u52`
- `scripts/parody/test_u41_shape_and_ref_mode.py` -> `scripts/parody/_archive/test_u41_shape_and_ref_mode.py.bak-20261116-u52`
- `scripts/parody/test_writer_finalize.py` -> `scripts/parody/_archive/test_writer_finalize.py.bak-20261116-u52`
- `scripts/parody/test_writer_pipeline.py` -> `scripts/parody/_archive/test_writer_pipeline.py.bak-20261116-u52`
- `scripts/parody/test_u52_e2e_passthrough.py` *(new file; no prior file to back up)*

### `/home/evo/AI/render` (Commit `a53dedd3d1b6bcd263164fc692c01921481e968b`, author `Max Architect <max@fleet.local>`)
- `AGENTS.md` -> `_archive/AGENTS.md.bak-20261116-u52`
- `rewriter/ref2va-system-prompt.md` -> `rewriter/_archive/ref2va-system-prompt.md.bak-20261116-u52`
- `writer_pipeline/writer_prompt.md` -> `writer_pipeline/_archive/writer_prompt.md.bak-20261116-u52`
- `x3/queue-remote.sh` -> `x3/_archive/queue-remote.sh.bak-20261116-u52`

---

## 3. What Was Kept From the Old Machinery & Why

- **`beat_card`, `n_candidates` + `judge` selection, and `assemble_output` fallback (only when LLM output lacks section headers):** Kept in `render_writer_pipeline.py` because existing suite tests (`test_beat_card_invalid_twice_skips`, `test_two_clip_chain_scene_state`, `test_writer_pipeline.py` talk/MMF tests, `test_u41_shape_and_ref_mode.py`) exercise beat-card frame sizing when `--frames` is omitted, `scene_state.json` continuity metadata, and candidate/judge flow. When the writer returns a multi-section prompt (containing `subject_definitions:`, `summary:`, `retention_analysis:`, `detailed_description:`, or `integrated_multimodal_description:`), `_materialise_writer_text` passes it through verbatim without calling `clean_prose`, `normalize_prose`, or `assemble_output`.
- **`clean_still_read` function symbol:** Kept as a no-op `(dict(d), [])` wrapper instead of deleting the function so imports/unit callers stay intact without mutating vision captions.
- **`finalize_writer_prompt` & `repair_writer_output` behind `--strict` / `strict=True`:** Kept reachable when `--strict` is explicitly passed to `submit_parody_run.py writer-run` (or `strict=True` in Python) so legacy strict diagnostics and existing `finalize_writer_prompt` unit coverage remain intact while default writer requests are verbatim passthrough.
- **`scene_state.json`, `dialogue_blacklist.jsonl`, `recent_outputs.jsonl`, `RefMod`/voice-ref resolution, `guide`/`ref` still modes, `vision_read`, 18+ safety guard, `queue-remote.sh` + `run_queue.py`:** Preserved in full per U52 HARD RULES.

---

## 4. Test Results (Post-Commit)

- **Full `parody` suite:**  
  `cd /home/evo/AI/community/scripts && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q parody`  
  **Result:** `581 passed, 5 skipped in 12.47s`
- **`run_queue` & guard tests (`scripts/tests/`):**  
  `cd /home/evo/AI/community/scripts && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q tests/test_run_queue_cell_contract.py tests/test_run_queue_evict_disk.py tests/test_run_queue_prompt_sha.py tests/test_adults_guard.py tests/test_guard_scope.py`  
  **Result:** `35 passed in 0.09s`  
  *(Note: the remaining 4 X3/AlienPc-environment tests in `scripts/tests/` — `test_run_queue_keep_comfy_process.py::TestSubmitPassesFlagOnlyWhenAsked::test_default_off_end_to_end_writer_run_argv`, `test_run_queue_one_at_a_time.py::test_free_comfy_calls_api_free_when_loaded`, `test_remote_comfy.py::test_enable_routes_submit_through_uploads_and_fetch_through_view`, and `test_h3_fix_bcd.py::test_mark_collected` — already failed identically at baseline prior to any U52 edit.)*
- **New U52 end-to-end & alignment tests (`scripts/parody/test_u52_e2e_passthrough.py` — `7 passed in 0.94s`, all included in the `581 passed` run):**
  - `test_u52_e2e_pipeline_to_request_frames_and_passthrough[talk-talk-she talks to him beside the bed-guide]` — **PASSED**
  - `test_u52_e2e_pipeline_to_request_frames_and_passthrough[single_position-doggy-doggy on the bed-guide]` — **PASSED**
  - `test_u52_e2e_pipeline_to_request_frames_and_passthrough[guide_mode-doggy-doggy on the bed in guide mode-guide]` — **PASSED**
  - `test_u52_e2e_pipeline_to_request_frames_and_passthrough[ref_mode-doggy-doggy on the bed in ref mode-ref]` — **PASSED**
  - `test_align_h3_frames_and_graph_expect_all_node_types` — **PASSED**
  - `test_summary_line_queued_and_surface_mismatch_warning` — **PASSED**
  - `test_wp_lint_shot_timestamps_and_beta7_audio_warning` — **PASSED**
