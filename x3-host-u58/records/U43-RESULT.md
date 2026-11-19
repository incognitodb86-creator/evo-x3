# U43 Result — Merge Aborted at Step 3 Gate (Pre-Existing Uncommitted Test Linuxize & `scripts/tests` X3 Failures)

Date: 2026-11-16 (CT)
Executor: Antigravity (Gemini 4 Hydrogen High) on EVO-X3 (`/home/evo/AI/community` as user `evo`)
Brief: `/home/derekboone/evo-x3/records/U43-community-merge-brief-20261116.md`

> **Status: ABORTED (`git merge --abort`) before commit and push.**
> All 6 merge conflicts resolved cleanly (keeping both sides' behavior) and the U41 byte-identical check passed (`True`, `6727` and `8920` bytes), **but Step 3 test gates failed** on the clean merged tree (both `scripts/parody` and `scripts/tests`). Per the brief's HARD RULE, I ran `git merge --abort`, restored the `pre-u43` stash, verified all 39 paths and SHA-256 checksums against the pre-stash snapshot, and stopped without committing or pushing.

---

## 1. Merge & Push Status

- **Merge SHA:** None (merge aborted before `git commit` via `git merge --abort`).
- **Remote tip (`gitea/x3-community`):** `4f1793497355882e6beaf8a18235f2d5d17bfb4d` (unchanged; nothing pushed, no force push attempted).
- **Local `HEAD` (`x3-linux`):** `a4f58a76d18bfdb6151f040238fa3764f8b79292` (U41).
- **Merge base:** `d153a1762019ae90ee7d968f9b06a8495f25e811`.
- **`git status -sb` after abort & stash restore:**
  `## x3-linux...gitea/x3-community [ahead 2, behind 6]` with the exact 37 pre-existing modified files (`M ...`) and `?? dummy_run/`.

---

## 2. Conflict Resolutions Tested Before Abort (For Audit)

During Step 1 (`git merge --no-commit gitea/x3-community`), git auto-merged `scripts/parody/build_request.py`, `scripts/parody/render_writer_pipeline.py`, `scripts/parody/wp_lint.py`, and `skills/h3-prompting/SKILL.md` (verified that U40/U41 on `HEAD` already contained all remote U36/U37 hunks in those files), and raised 6 conflicts. Diffing `:1:` (merge-base), `:2:` (local `a4f58a7`), and `:3:` (remote `4f17934`) showed that local `HEAD` already incorporated every remote P1b/U36/U37 hunk in all 6 files while adding U40/U41 work:

1. **`scripts/parody/resolve.py` (`UU`):**
   - Kept from remote (U36): `DEFAULT_APPROVED_STILLS_DIR = Path(__file__).resolve().parents[3] / "5slock" / "approved_characters"`.
   - Kept from local (U40): `RENDER_APPROVED_STILLS_DIR`, `_HOME_RENDER_APPROVED_STILLS_DIR`, deduplicated 4-entry `APPROVED_IMAGE_POOLS`, and `expanduser()` for `~` paths in `validate_reference_images`.
2. **`scripts/parody/submit_parody_run.py` (`UU`):**
   - Kept from remote (U36/U37 Step C/D): `__file__`-derived `PARODY_DIR`, `SCRIPTS_DIR`, `_AI_ROOT`, `INDEX_DIR`, `REFMODS_DIR`, `COMFY_OUT_COMMUNITY`, `QUEUE_PYTHON`; absolute `--run-dir` enforcement; required `--still` and nonexistent-absolute-still checks in `_writer_run_cli` and `submit_writer_run`.
   - Kept from local (U40/U41): merged PixlStash vault (`_PIXLSTASH_VAULTS = (_AI_ROOT / "5slock" / "libraries" / "vault.db",)`, `_STILL_LIBRARY_ROOTS = (_AI_ROOT / "render" / "stills" / "approved_characters", _AI_ROOT / "5slock" / "libraries")`), `still_mode` (`guide|ref`), `--aspect auto`, `read_still_size` / `check_still_canvas_shape` warning, and `writer-run` pass-through.
3. **`scripts/parody/test_u37_builder_fixes.py` (`AA`):**
   - Kept from remote (U37 Step C): all 114 lines of sections 1–3 (missing/nonexistent `--still`, relative `run_dir`, hard `dial`/`throat`/`negatives` lint tests).
   - Kept from local (U40): section 4 (`test_resolve_accepts_render_approved_characters_pool_and_tilde`, `test_wp_lint_catches_enters_her_mouth_oral_silence_and_deep_in_her_oral_contact`, `test_pixlstash_lookup_uses_merged_vault_only_and_skips_if_token_absent`, `test_pixlstash_live_api_token_skips_when_not_ready`).
4. **`scripts/remote_comfy.py` (`AA`):**
   - Kept from remote (P1b): entire remote-queue implementation (`API`, `LOCK`, `INPUT_ROOTS`, `input_files`, `resolve`, `upload_plan`, `_multipart`, `upload`, `download`, `lock_acquire`, `lock_release`, `enable`, `dry_report`).
   - Kept from local (U40): `remote_idle` checking `API + "/system_stats"` before `API + "/queue"` so an unloaded ComfyUI (`409`) returns `None` without waking `comfyui_auto`.
5. **`scripts/tests/test_remote_comfy.py` (`AA`):**
   - Kept from remote (P1b): all 5 original P1b tests (`test_upload_plan_lists_image_and_audio_not_models`, `test_missing_input_fails_closed`, `test_multipart_carries_overwrite_and_file`, `test_lock_is_exclusive_and_released`, `test_enable_routes_submit_through_uploads_and_fetch_through_view`).
   - Kept from local (U40): `test_remote_idle_checks_system_stats_before_queue`.
6. **`skills/h3-parody-identity/SKILL.md` (`UU`):**
   - Kept from remote (U37 Step B + Step B fix): X3 Tailscale Serve `:8446` wording, `~/AI/render/x3/queue-remote.sh`, deferred 2x upscale note, X3 `writer-run` flags/provider, X3 dry-build-then-queue recipe, and removal of the agent-only `pi_qnap.py` marker.
   - Kept from local (U40/U41): merged vault path `~/AI/5slock/libraries/vault.db`, `--aspect ... auto`, and `--image` center-crop vs `--aspect auto` / `--still-mode ref` note.

*(Note: After resolving, only those 6 named paths were staged with `git add --` before running Step 3 checks; nothing was committed.)*

---

## 3. Step 3 Test Results (Observed on the Clean Resolved Merge Tree, Prior to Abort)

Command Python: `/home/evo/AI/render/x3/.venv/bin/python`, working directory `/home/evo/AI/community` as `evo` (with `pre-u43` stashed per Step 0).

### `scripts/parody`
- **Unfiltered run (`pytest -q scripts/parody`):** **2 collection errors** (`0` tests ran; interrupted during collection):
  - `scripts/parody/test_longclip_baseline.py` (`ModuleNotFoundError: No module named 'take_chain_stitch'`)
  - `scripts/parody/test_parody_stitch.py` (`ModuleNotFoundError: No module named 'take_chain_stitch'`)
  - Cause: Committed `test_longclip_baseline.py` and `test_parody_stitch.py` hardcode `REPO_ROOT = Path(r"/home/derekboone/AI/community")`. Their `/home/evo/AI/community` edits live in the stashed 37 dirty files (`pre-u43`), which Step 0 required stashing before merge.
- **Diagnostic run excluding those 2 collection-error files (`--ignore=scripts/parody/test_longclip_baseline.py --ignore=scripts/parody/test_parody_stitch.py`):** **537 passed, 5 skipped, 22 failed** (below the `>= 574 passed` gate).
  - All 22 failures (`test_longclip_beats.py`: 5, `test_longclip_skill_routing.py`: 3, `test_parody_phase1.py`: 3, `test_parody_phase3.py`: 2, `test_writer_pipeline.py`: 9) fail because committed files hardcode `/home/derekboone/AI/...` paths whose `/home/evo/AI/...` updates are inside the stashed `pre-u43` dirty work.

### `scripts/tests`
- **Unfiltered run (`pytest -q scripts/tests`):** **2 collection errors** (`0` tests ran; interrupted during collection):
  - `scripts/tests/test_free_comfy_args.py`: `StopIteration` at `REPO_ROOT = next(d for d in CANDIDATES if os.path.isfile(os.path.join(d, "run_queue.py")))` (`CANDIDATES = [r"C:\AI\community\scripts", r"C:\AI\lib", r"C:\AI\community"]`).
  - `scripts/tests/test_phase1_still.py`: `FileNotFoundError: [Errno 2] No such file or directory: 'C:\\AI\\community/templates/flux_stills_s2_bfs.api.json'` (via `scripts/make_bfs_request.py:27` `COMMUNITY = r"C:\AI\community"`).
- **Diagnostic run excluding those 2 collection-error files (`--ignore=scripts/tests/test_free_comfy_args.py --ignore=scripts/tests/test_phase1_still.py`):** **118 passed, 2 skipped, 6 failed** (`test_remote_comfy.py` passed):
  - `scripts/tests/test_b2_lora_param.py` (**4 failed**): `FileNotFoundError: [Errno 2] No such file or directory: 'C:\\AI\\community/templates/b2.api.json'` (via `scripts/make_b2_request.py:23` `COMMUNITY = r"C:\AI\community"`).
  - `scripts/tests/test_run_queue_keep_comfy_process.py::TestSubmitPassesFlagOnlyWhenAsked::test_default_off_end_to_end_writer_run_argv` (**1 failed**): fails at `scripts/parody/submit_parody_run.py:1471` with `RuntimeError: X3: --queue is not wired through run_queue.py; after Derrick's yes use ~/AI/render/x3/queue-remote.sh <run_dir> (AlienPc ComfyUI over the tailnet)` when `os.name != "nt"`.
  - `scripts/tests/test_run_queue_one_at_a_time.py::TestRunQueueOneAtATime::test_free_comfy_calls_api_free_when_loaded` (**1 failed**): `AssertionError: unexpectedly None` because `comm.free_comfy()` was replaced by the X3 remote no-op (`COMFY free skipped (remote: AlienPc llama-swap ttl + graceful stop own the process)`). When run standalone (`pytest -q scripts/tests/test_run_queue_one_at_a_time.py`), it gets **3 passed, 3 failed** (the 3 failures hit `FileNotFoundError: 'C:\\AI\\community/community.log'` in `scripts/comm.py:29`).

---

## 4. U41 Byte-Identical Check (Observed on the Clean Resolved Merge Tree, Prior to Abort)

Compared `scripts/parody/build_request.py` against `/home/evo/AI/community/_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41` on identical inputs (`json.dumps(..., indent=2, ensure_ascii=False)` + prompt string):

- `build_parody_request`: **`True`**, `6727` bytes (`bak_bytes=6727`, `cur_bytes=6727`, `prompt_match=True`).
- `build_writer_request`: **`True`**, `8920` bytes (`bak_bytes=8920`, `cur_bytes=8920`, `prompt_match=True`).

---

## 5. Stash Restore & Snapshot Verification

- **Snapshot files (written before stashing):**
  - `/home/derekboone/evo-x3/records/U43-pre-stash-list.txt` (39 paths: 37 modified + 2 under `dummy_run/`)
  - `/home/derekboone/evo-x3/records/U43-pre-stash-sha256.txt` (39 SHA-256 digests sorted by path)
- **Stash restored intact:** **Yes** — after `git merge --abort` (and restoring `dummy_run/build_report.json` + `dummy_run/clip_NOT_READY.txt` from `stash@{0}^3`, since running pytest had regenerated `dummy_run/` during the diagnostic test run), verified `39 / 39` paths and `39 / 39` SHA-256 digests match `U43-pre-stash-list.txt` and `U43-pre-stash-sha256.txt` identically, then dropped `stash@{0}`. `git stash list` is now empty.

---

## 6. Explicit Confirmations

- **No render / no queue:** No GPU lease taken, no `queue-remote.sh`, no `--wait` submission, no ComfyUI `/prompt`.
- **No image viewing:** No PixlStash library contents, library stills, or `/home/evo/AI/5slock/` pictures opened or viewed.
- **No force push:** Nothing pushed (`git merge --abort` before commit).
- **No `git add -A`:** Never run; only the 6 conflicted files were staged by name during conflict resolution testing, then cleared by `git merge --abort`.
- **U42 / protected trees untouched:** Did not touch U42 PixlStash tagging, `/home/evo/AI/5slock/`, `llama-swap.yaml`, Sydney private files, Windows partitions, USB X3BACKUP, BIOS, LUKS, or Tailscale.

---

## 7. Blocking Questions for Max / Derrick

1. **Pre-existing dirty linuxize test edits (`scripts/parody`):** The 11 test/helper files in the `pre-u43` dirty work (`test_longclip_baseline.py`, `test_longclip_beats.py`, `test_longclip_skill_routing.py`, `test_parody_phase1.py`, `test_parody_phase3.py`, `test_parody_stitch.py`, `test_t1109_writer_index_refmods.py`, `test_writer_finalize.py`, `test_writer_pipeline.py`, `writer_sys.py`, `test_run_queue_keep_comfy_process.py`) still hardcode `/home/derekboone/AI/...` in git HEAD, which causes `pytest -q scripts/parody` to fail (`2` collection errors + `22` failures) whenever the dirty work is stashed. Should those linuxize path fixes (ideally `__file__`-derived for cross-user portability, like U36) be committed first (or tested after popping the dirty work / on a separate commit) before requiring `pytest -q scripts/parody` to pass cleanly on a committed merge?
2. **Un-ported Windows-only & X3-conflicting tests in `scripts/tests`:** On EVO-X3 Linux, `pytest -q scripts/tests` currently fails on:
   - `test_free_comfy_args.py` (`C:\AI\...` candidates only),
   - `test_phase1_still.py` and `test_b2_lora_param.py` (`make_bfs_request.COMMUNITY` / `make_b2_request.COMMUNITY` hardcoded to `r"C:\AI\community"`),
   - `test_run_queue_one_at_a_time.py` (`comm.LOG = 'C:\\AI\\community/community.log'` standalone, and `test_free_comfy_calls_api_free_when_loaded` failing after `test_remote_comfy.py` enables remote mode in-process),
   - `test_run_queue_keep_comfy_process.py::TestSubmitPassesFlagOnlyWhenAsked::test_default_off_end_to_end_writer_run_argv` (blocked by `submit_writer_run`'s `if os.name != "nt": raise RuntimeError("X3: --queue is not wired through run_queue.py...")` guard).
   Should `scripts/tests` be ported to `__file__`-relative / OS-aware behavior (or `test_remote_comfy.py` scoped/isolated, and X3-only guards bypassed/marked appropriately) in a follow-up commit before making `pytest -q scripts/tests` a blocking merge gate, or should the merge commit proceed once only `test_remote_comfy.py` + `scripts/parody` pass?
