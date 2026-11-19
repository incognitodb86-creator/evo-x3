# U45 Result — Portable Path Fixes Committed, Community Merge Completed & Pushed

Date: 2026-11-16 (CT)
Executor: Antigravity (Gemini 4 Hydrogen High) on EVO-X3 (`/home/evo/AI/community` as user `evo`)
Brief: `/home/derekboone/evo-x3/records/U45-pathfix-merge-brief-20261116.md`

> **Status: COMPLETED & PUSHED.**
> Step-1 portable path fixes (`1b1a88d`) and the `gitea/x3-community` merge (`10de4d0`) passed all three gates (`scripts/parody` `574 passed, 5 skipped, 0 failed`; `scripts/tests` strictly better than baseline with `118 passed, 6 failed` vs `116 passed, 8 failed`; U41 `guide`-mode byte-identical check `True` / `6727` and `8920` bytes), were pushed normally via `git push gitea HEAD:x3-community` (no force), and the `pre-u45` stash was restored intact (`28 / 28` SHA-256 checksums verified).

---

## 1. Step-1 Commit & Path Portability

- **Step-1 Commit SHA:** `1b1a88d4c237571bb11258d8d9d1ff69b8bda4db` (`1b1a88d`)
- **Commit message:** `X3: commit linuxize path fixes for parody tests`
- **Staged & committed paths (11 explicit paths, verified via `git diff --cached --name-only`):**
  All 11 paths were updated from hardcoded `/home/derekboone/AI/...` / `/home/evo/AI/...` to `__file__`-derived / `~/...` portable expressions across `derekboone` and `evo`, without changing test assertions or production behavior:
  1. `scripts/parody/test_longclip_baseline.py`: `REPO_ROOT = Path(__file__).resolve().parents[2]`
  2. `scripts/parody/test_longclip_beats.py`: `REPO_ROOT = Path(__file__).resolve().parents[2]`
  3. `scripts/parody/test_longclip_skill_routing.py`: `REPO_ROOT = Path(__file__).resolve().parents[2]`
  4. `scripts/parody/test_parody_phase1.py`: `repo_root = Path(__file__).resolve().parents[2]`, `ai_root = repo_root.parent`, derived `index_dir`, `refmods_dir`, `approved_dir`, `aliases_path`
  5. `scripts/parody/test_parody_phase3.py`: `_REPO_ROOT = Path(__file__).resolve().parents[2]`, derived `INDEX_DIR` and `REFMODS_DIR`
  6. `scripts/parody/test_parody_stitch.py`: `REPO_ROOT = Path(__file__).resolve().parents[2]`
  7. `scripts/parody/test_t1109_writer_index_refmods.py`: `_AI_ROOT = Path(__file__).resolve().parents[3]`, derived `render/` and `5slock/` test path strings
  8. `scripts/parody/test_writer_finalize.py`: `Path(__file__).resolve().parents[2]` for `runs/...` and `Path(__file__).resolve().parents[1]` for `scripts/` (preserving original mixed line endings)
  9. `scripts/parody/test_writer_pipeline.py`: `Path(__file__).resolve().parents[3]` for `render/...` paths (preserving original mixed line endings)
  10. `scripts/parody/writer_sys.py`: docstring `~/AI/render/AGENTS.md` and `str(Path(__file__).resolve().parents[3] / "locks" / "gpu-render.lock")` in `_AGENT_MARKERS`
  11. `scripts/tests/test_run_queue_keep_comfy_process.py`: `v2_root = os.path.join(os.path.dirname(SCRIPTS), "runs", "overnight_5min_rough_20261115_v2")`
- **Not pushed alone:** `1b1a88d` was kept local until after all merge gates passed, then pushed together with the merge commit in Step 5.

---

## 2. Merge & Push Summary

- **Starting local `HEAD`:** `a4f58a76d18bfdb6151f040238fa3764f8b79292` (U41)
- **Step-1 `HEAD`:** `1b1a88d4c237571bb11258d8d9d1ff69b8bda4db`
- **Fetched remote tip (`gitea/x3-community`):** `4f1793497355882e6beaf8a18235f2d5d17bfb4d` (unchanged from U43)
- **Merge Commit SHA:** `10de4d01e0a7cea250a38504632ba72e235d9dbc` (`10de4d0`) — `Merge gitea/x3-community (P1b/U36/U37) into x3-linux (U40/U41 + path fixes); keep both sides`
- **Push result (`git push gitea HEAD:x3-community`, no force):** `4f17934..10de4d0  HEAD -> x3-community`
- **Post-push `HEAD`:** `10de4d01e0a7cea250a38504632ba72e235d9dbc`
- **Post-push `gitea/x3-community`:** `10de4d01e0a7cea250a38504632ba72e235d9dbc`
- **`git status -sb` after final git action (`git stash drop`):**
  ```
  ## x3-linux...gitea/x3-community
   M _archive/alienpc-only/dummy_run/build_report.json
   M _archive/alienpc-only/dummy_run/clip_NOT_READY.txt
   M agent-shared/AGENTS.md
   M agent-shared/prompts/render.md
   M agent-shared/skills/google-voice-texts/SKILL.md
   M agent-shared/skills/ralph-loop/SKILL.md
   M notes/2026-11-15-keep-comfy-vram-fit.md
   M notes/actions.log
   M scripts/parody/scene_addenda.py
  ?? dummy_run/
  ```

---

## 3. Conflict Resolutions (Reused U43 Resolutions Unchanged)

Verified `:2:` (local) vs `:3:` (remote `gitea/x3-community`) diffs for every conflicted path. As in U43, local `HEAD` already contained all remote P1b/U36/U37 hunks in these 6 files while adding U40/U41 changes, so reusing the U43 resolutions (`:2:` / `--ours`, staged explicitly by path) preserved both sides:

1. **`scripts/parody/resolve.py` (`UU`):** Kept remote U36 `__file__`-derived `DEFAULT_APPROVED_STILLS_DIR`, plus local U40 `RENDER_APPROVED_STILLS_DIR`, `_HOME_RENDER_APPROVED_STILLS_DIR`, deduplicated 4-entry `APPROVED_IMAGE_POOLS`, and `expanduser()` in `validate_reference_images`.
2. **`scripts/parody/submit_parody_run.py` (`UU`):** Kept remote U36/U37 `__file__`-derived roots (`PARODY_DIR`, `SCRIPTS_DIR`, `_AI_ROOT`, `INDEX_DIR`, `REFMODS_DIR`, `COMFY_OUT_COMMUNITY`, `QUEUE_PYTHON`), absolute `--run-dir` check, and required/nonexistent `--still` checks, plus local U40/U41 merged PixlStash vault (`_PIXLSTASH_VAULTS`, `_STILL_LIBRARY_ROOTS`), `still_mode` (`guide|ref`), `--aspect auto`, shape warning (`read_still_size` / `check_still_canvas_shape`), and `writer-run` pass-through.
3. **`scripts/parody/test_u37_builder_fixes.py` (`AA`):** Kept remote U37 sections 1–3 (`--still`, relative `run_dir`, `dial`/`throat`/`negatives` lint) plus local U40 section 4 (`test_resolve_accepts_render_approved_characters_pool_and_tilde`, `test_wp_lint_catches_enters_her_mouth_oral_silence_and_deep_in_her_oral_contact`, `test_pixlstash_lookup_uses_merged_vault_only_and_skips_if_token_absent`, `test_pixlstash_live_api_token_skips_when_not_ready`).
4. **`scripts/remote_comfy.py` (`AA`):** Kept remote P1b remote-queue implementation plus local U40 `remote_idle` (`/system_stats` checked before `/queue` so 409 returns `None` without waking `comfyui_auto`).
5. **`scripts/tests/test_remote_comfy.py` (`AA`):** Kept all 5 remote P1b tests plus local U40 `test_remote_idle_checks_system_stats_before_queue`.
6. **`skills/h3-parody-identity/SKILL.md` (`UU`):** Kept remote U37 Step B Tailscale `:8446` / `queue-remote.sh` / deferred-upscale / `writer-run` / `pi_qnap.py`-marker removal plus local U40/U41 merged vault (`~/AI/5slock/libraries/vault.db`) and `--aspect auto` / `--still-mode ref` notes.

Auto-merged files: `scripts/parody/build_request.py`, `scripts/parody/render_writer_pipeline.py`, `scripts/parody/wp_lint.py`, and `skills/h3-prompting/SKILL.md` matched `HEAD` cleanly (already carried both sides); the remaining 17 U36/U37/P1b files (`run_record.py`, `sync_refmods.py`, `voice_refmod_trim.py`, `wp_compile_prompt.py`, `chain_queue.py`, `run_queue.py`, and 11 `skills/...` docs) auto-merged from `gitea/x3-community` cleanly.

---

## 4. Gate Test Results

Command Python: `/home/evo/AI/render/x3/.venv/bin/python`, CWD: `/home/evo/AI/community` as user `evo`.

### Gate A — `scripts/parody` (on clean merged tree)
- Command: `pytest -q scripts/parody`
- Result: **`574 passed, 5 skipped, 0 failed, 0 errors, 0 collection errors`** (`exit 0`, `15.03s`; meets `>= 574 passed` and `0` failures/errors).

### Gate B — `scripts/tests` (Pre-Merge Baseline vs Merged Run)
Full baseline details recorded in `/home/derekboone/evo-x3/records/U45-tests-baseline.txt`.

- **Pre-merge baseline (`1b1a88d`, `pre-u45` stashed):**
  - Unfiltered (`pytest -q scripts/tests`): **`2` collection errors** (`0` tests ran, `exit 2`):
    - `scripts/tests/test_free_comfy_args.py` (`StopIteration`: `C:\AI\...` candidates only)
    - `scripts/tests/test_phase1_still.py` (`FileNotFoundError`: `'C:\\AI\\community/templates/flux_stills_s2_bfs.api.json'`)
  - Filtered (`--ignore=scripts/tests/test_free_comfy_args.py --ignore=scripts/tests/test_phase1_still.py`): **`116 passed, 2 skipped, 8 failed, 0 errors`** (`exit 1`, `7.44s`):
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_cli_lora_none_builds_the_plain_graph`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_lora_injects_the_face_lora_on_the_model_chain`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_lora_none_is_the_plain_b2_graph`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_strength_is_applied`
    - `scripts/tests/test_run_queue_keep_comfy_process.py::TestSubmitPassesFlagOnlyWhenAsked::test_default_off_end_to_end_writer_run_argv`
    - `scripts/tests/test_run_queue_one_at_a_time.py::TestRunQueueOneAtATime::test_eviction_fails_into_retry_wave`
    - `scripts/tests/test_run_queue_one_at_a_time.py::TestRunQueueOneAtATime::test_free_comfy_calls_api_free_when_loaded`
    - `scripts/tests/test_run_queue_one_at_a_time.py::TestRunQueueOneAtATime::test_job_timeout_cancels_via_interrupt_and_queue_delete`

- **Merged run (before merge commit):**
  - Unfiltered (`pytest -q scripts/tests`): **`2` collection errors** (`0` tests ran, `exit 2` — same 2 files):
    - `scripts/tests/test_free_comfy_args.py`
    - `scripts/tests/test_phase1_still.py`
  - Filtered (`--ignore=scripts/tests/test_free_comfy_args.py --ignore=scripts/tests/test_phase1_still.py`): **`118 passed, 2 skipped, 6 failed, 0 errors`** (`exit 1`, `7.48s`):
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_cli_lora_none_builds_the_plain_graph`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_lora_injects_the_face_lora_on_the_model_chain`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_lora_none_is_the_plain_b2_graph`
    - `scripts/tests/test_b2_lora_param.py::TestB2LoraParam::test_strength_is_applied`
    - `scripts/tests/test_run_queue_keep_comfy_process.py::TestSubmitPassesFlagOnlyWhenAsked::test_default_off_end_to_end_writer_run_argv`
    - `scripts/tests/test_run_queue_one_at_a_time.py::TestRunQueueOneAtATime::test_free_comfy_calls_api_free_when_loaded`
- **Comparison:** **Strictly no worse** (2 fewer failures than baseline: `run_queue.py` from the merge resolved `comm.LOG` for `test_eviction_fails_into_retry_wave` and `test_job_timeout_cancels_via_interrupt_and_queue_delete`; same 2 collection errors; 0 new failures).

### Gate C — U41 Guide-Mode Byte-Identical Check
Compared `scripts/parody/build_request.py` against `_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41` on identical inputs (`json.dumps(..., indent=2, ensure_ascii=False)` + prompt):
- `build_parody_request`: **`True`**, `6727` bytes (`bak_bytes=6727`, `cur_bytes=6727`, `prompt_match=True`).
- `build_writer_request`: **`True`**, `8920` bytes (`bak_bytes=8920`, `cur_bytes=8920`, `prompt_match=True`).

---

## 5. Stash Restore & Snapshot Verification

- **Snapshot files (written before stashing, mode `644`, owned by `derekboone`):**
  - `/home/derekboone/evo-x3/records/U45-pre-stash-list.txt` (28 remaining dirty/untracked paths; none of the 11 step-1 paths present)
  - `/home/derekboone/evo-x3/records/U45-pre-stash-sha256.txt` (28 SHA-256 digests sorted by path)
- **Stash restored intact:** **Yes** — after removing pytest-regenerated `dummy_run/` prior to merge commit, ran `git stash apply`, verified `28 / 28` files pass `sha256sum -c` against `U45-pre-stash-sha256.txt` identically, then dropped `stash@{0}` (`git stash list` is now empty).
  *(Note: of the 28 snapshot files, 17 U36/U37/P1b files matched the merged `HEAD` `10de4d0` byte-for-byte — verified `sha256sum` identical across `worktree == HEAD == stash@{0}` — so they are now clean in `git status -sb`, leaving the 9 still-uncommitted modified files and `dummy_run/` (`2` files) dirty/untracked.)*

---

## 6. Explicit Confirmations

- **No render / no queue:** No GPU lease taken, no `queue-remote.sh`, no `--wait` submission, no ComfyUI `/prompt`.
- **No image viewing:** No PixlStash library contents, library stills, or `/home/evo/AI/5slock/` pictures opened or viewed; only tiny synthetic PIL images in `tmp_path` were used by unit tests.
- **No force push:** Used `git push gitea HEAD:x3-community` with no `--force`, no `--force-with-lease`, and no `+` refspec.
- **No `git add -A`:** Never run; only the 11 step-1 files and the 6 conflicted files were staged explicitly by path.
- **No push of step-1 commit alone:** `1b1a88d` remained local until all Step 4 gates passed and was pushed together with merge commit `10de4d0`.
- **No contact with tagger or llama-swap:** Did not touch `u42-pixlstash-tagger`, any tagging follow-on/progress files, `/home/evo/AI/5slock/`, `llama-swap.yaml`, Sydney private files, Windows partitions, USB X3BACKUP, BIOS, LUKS, or Tailscale.
