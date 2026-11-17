# U40 Result — Code-Fix Batch (U37 Decisions 2–4, PixlStash Repoint, Extend-Seam Fixes)

Date: 2026-11-16 (CT)
Executor: Antigravity (Gemini 4 Hydrogen High) on EVO-X3 (edits in `/home/evo/AI/render` and `/home/evo/AI/community` as user `evo`)
Brief: `/home/derekboone/evo-x3/records/U40-code-fixes-brief-20261116.md`

---

## 1. Summary of Changes & Commits

### `/home/evo/AI/render` (branch `x3-linux`, local commits; push blocked for `evo` — see §7)
1. **Commit `35e098d`** — `X3: commit U37/consolidation evo-path, config, and queue-remote edits`
   - Reviewed all 12 pre-existing dirty files against HEAD `6a49943`; all 12 were legitimate U37 / consolidation / linuxize / retest2 edits (details in §2), gitleaks clean (`0` leaks).
2. **Commit `2904e1b`** — `U40: repoint AGENTS.md and RUN_ME.md vault docs to merged 5slock/libraries/vault.db`
   - `AGENTS.md`: replaced `approved_characters\vault.db` / `render/stills/approved_characters/vault.db` references with the merged vault `/home/evo/AI/5slock/libraries/vault.db`.
   - `RUN_ME.md`: updated Stills & PixlStash vaults note to `~/AI/5slock/libraries/vault.db` with `~/AI/render/stills/approved_characters/POOL` as POOL folder fallback.
   - Backups saved under `/home/evo/AI/render/_archive/u40-20261116/`.

### `/home/evo/AI/community` (branch `x3-linux`, local commit; push blocked for `evo` — see §7)
- **Commit `0530815`** — `U40: U37 pools/remote_idle/oral lint, PixlStash merged vault, overlap consistency, optional seam crossfade` (9 named files staged; unrelated pre-existing dirty files left untouched; gitleaks staged scan `0` leaks; backups under `/home/evo/AI/community/_archive/u40-20261116/`):
  - **A.1 (`scripts/parody/resolve.py`, `scripts/parody/test_u37_builder_fixes.py`):** Added `RENDER_APPROVED_STILLS_DIR` (`Path(__file__).resolve().parents[3] / "render" / "stills" / "approved_characters"`, resolving to `/home/evo/AI/render/stills/approved_characters`) and `_HOME_RENDER_APPROVED_STILLS_DIR` (`~/AI/render/stills/approved_characters`) to `APPROVED_IMAGE_POOLS`; updated `validate_reference_images()` to expand leading `~` via `.expanduser()`. Added unit test `test_resolve_accepts_render_approved_characters_pool_and_tilde`.
  - **A.2 (`scripts/remote_comfy.py`, `scripts/tests/test_remote_comfy.py`):** Updated `remote_idle()` to query `GET /system_stats` before `GET /queue`. On HTTP 409 from `/system_stats`, returns `None` (unloaded/idle) without touching `/queue`; only queries `/queue` when `/system_stats` returns HTTP 200. Added `test_remote_idle_checks_system_stats_before_queue` (409 no `/queue`, 200+idle, 200+busy, 500 error).
  - **A.3 (`scripts/parody/wp_lint.py`, `scripts/parody/test_u37_builder_fixes.py`):** Extended `MOUTH_CONTACT_RE` to match `enters? her mouth`, and extended `MODE_RULES["oral"]["banned_contact"]` to catch vaginal contact phrasing (`deep in her`, `buried in her`, `inside her` when not followed by `mouth`/`throat`) so `oral_contact` triggers cleanly alongside `oral_silence`. Added `test_wp_lint_catches_enters_her_mouth_oral_silence_and_deep_in_her_oral_contact`.
  - **B (`scripts/parody/submit_parody_run.py`, `scripts/parody/test_modular_s3_and_writer_sys.py`, `scripts/parody/test_u37_builder_fixes.py`):**
    - Repointed `_PIXLSTASH_VAULTS` exclusively to `(_AI_ROOT / "5slock" / "libraries" / "vault.db",)` and dropped `approved_characters/vault.db`.
    - Updated `_STILL_LIBRARY_ROOTS` to `(_AI_ROOT / "render" / "stills" / "approved_characters", _AI_ROOT / "5slock" / "libraries")` (keeping the POOL folder fallback).
    - Updated `test_part4_pixlstash_stills_vault_and_voice_ref_attach` to assert the single merged vault (no `approved_characters/vault.db`) and added `test_pixlstash_lookup_uses_merged_vault_only_and_skips_if_token_absent` + `test_pixlstash_live_api_token_skips_when_not_ready`.
    - Note on PixlStash HTTP API: grep across both `render` and `community` found no existing PixlStash HTTP API client code (only read-only sqlite queries against `_PIXLSTASH_VAULTS`).
  - **C1 (Voice RefMod on continuation beats 2 and 3):** Verified `3dd04d1` (`runtime_packs_tail_audio()` + `continuation_cond_audio_rows()` + `_continuation_voice_refmods()`) is intact in `build_request.py` and was not reverted by later commits or dirty edits. Beats 2 and 3 keep the installed `minimaxh3_oc_poolclub_v1_refmod_audio` (25 s / `latent_t=1000`) on the shared `refmods` loader with `packed == reserved` (`2000 == 2000`, `2130 == 2130`, `2074 == 2074`). Note: `minimaxh3_oc_poolclub_v1_refmod_audio_23s.safetensors` is not present in `/home/evo/AI/comfy-alienpc/models/refmods/`.
  - **C2 (`scripts/parody/build_request.py`, `scripts/parody/test_writer_beats_continuation.py`):** Confirmed `rebase_continuation_shot_clocks(..., clock_target="window")` and `_BEAT_SHOT_CLOCK_RE` from `27d4e39` are intact, and added explicit per-beat `overlap_consistency` verification in `build_writer_beats_continuation_request()` confirming the single applied overlap drives carry (`c{n}_gen`), trim (`c{n}_append`), assembly (`c{n}` length / `window_frames`), and shot clocks (`applied_overlap_frames`). Extended tests in `test_writer_beats_continuation.py` (`test_beat2_two_cuts_39f_overlap_consistency_and_shot1_not_1625s`) covering the 2-cut beat 2 (`00:03.250` / `00:06.250` -> `00:03.958` / `00:06.958`, global `248` / `320`, Shot 1 `56f` / `2.333 s`, not `1.625 s`) and beat 3 at overlap 22 (`00:06.500` -> `513`, and `00:03.500` / `00:05.750` -> `441` / `495`).
  - **C3 (`scripts/parody/build_request.py`, `scripts/parody/test_writer_beats_continuation.py`):** Added optional seam audio crossfade & loudness tracing (`soft_av_release_weights`, `trace_seam_loudness`, `apply_seam_audio_crossfade`) supporting both 15 ms half-cosine de-click (`mode="declick"`, Herrgott pattern) and 8-tick half-cosine Soft AV release (`mode="soft_av"`, TimelineDirector pattern), wired into `build_writer_beats_continuation_request(..., audio_seam_crossfade=False)` (default `False` documented via `DEFAULT_SEAM_AUDIO_CROSSFADE`). Added `test_optional_audio_seam_crossfade_and_loudness_trace`.
  - **C4 (`scripts/parody/build_request.py`, `scripts/parody/test_writer_beats_continuation.py`):** Added `parse_plan_end_actions()` + `test_parse_plan_end_actions_extracts_plan_lines` to extract `- end_action (...): ...` lines directly from `PLAN.md`.

---

## 2. Review Outcome for the 12 Dirty `/home/evo/AI/render` Files

All 12 files at `6a49943` were reviewed via `git diff`, found legitimate (no secrets or machine-local junk), and committed in `35e098d`:
- `.pi/agent/pi-permissions.jsonc` — `/home/derekboone` -> `/home/evo` path migration.
- `.pi/extensions/loop-guard-test.mjs` — `/home/derekboone` -> `/home/evo` test cases.
- `.pi/settings.json` — `~`-relative paths + U37 Step B exclusion of 5 duplicate `fleet-brain/20_skills/current` render skills.
- `AGENTS.md` — `/home/derekboone` -> `/home/evo` path migration.
- `RUN_ME.md` — U37 Step B `## 0. EVO-X3 Section (Linux)`.
- `writer_pipeline/acceptance/t3_plan.py` — `Path(__file__).resolve()` relative `STILL` path.
- `writer_pipeline/acceptance/wp_accept.py` — `_AI_ROOT = Path(__file__).resolve().parents[3]` relative paths.
- `writer_pipeline/config.yaml` — U37 Step C `block_ready` (`dial`, `throat`, `negatives`) + `~/AI/render/stills/approved_characters/POOL` globs.
- `writer_pipeline/dialogue_blacklist.jsonl` — U37 Step D retest2 rolling blacklist entries.
- `x3/README-X3.md` — consolidation P1b + `evo` user documentation.
- `x3/linuxize.py` — `HOME = str(Path.home())`.
- `x3/queue-remote.sh` — consolidation P1b (`run_queue.py --remote` driver).

---

## 3. Pytest Counts (Post-Final Edit)

| Suite | Before | After | Notes |
|---|---|---|---|
| `community`: `scripts/parody` | `555 passed, 6 skipped` | `562 passed, 6 skipped` (4.80 s) | `test_part4_pixlstash_stills_vault_and_voice_ref_attach` unskipped on Linux; `test_pixlstash_live_api_token_skips_when_not_ready` skips cleanly (6 skipped total) |
| `community`: `scripts/tests/test_remote_comfy.py` | `5 passed` | `6 passed` (0.02 s) | Added `test_remote_idle_checks_system_stats_before_queue` |
| `render`: `--ignore=_archive --ignore=x3/bakeoff` | `3 passed` | `3 passed` (0.05 s) | Used `--ignore=x3/bakeoff` (relative to repo root) |

---

## 4. Dry-Build Overlap Math, Cut Times, and Loudness Trace

No pre-existing `extend-test-3beat` run dir existed on X3, so `/home/evo/AI/community/runs/extend-test-3beat-20261115/` was constructed from `/home/derekboone/evo-x3/records/extend-test-3beat-20261115/` and dry-built into `/home/evo/AI/community/runs/extend-test-3beat-20261115/dry-u40/` (`DRY_RUN` marker written; no queue, no render):

- **Visible frames:** `192 + 187 + 187 = 566` (`23.5833 s` at 24 fps).
- **Beat 2 (`c2`):**
  - Requested overlap `22`, **applied overlap `39`** (`overlap_audio_t = 65`), `extension_frames = 187`, `window_frames = 226` (`window_audio_t = window_audio_official_t = 377`).
  - Carry (`c2_gen.overlap_frames = 39`), trim (`c2_append` wired to `c2_gen:2/3`), assembly (`c2.length` wired to `c2_gen:1`), and shot clocks (`applied_overlap_frames = 39`) all use `39` (`consistent: true`).
  - **Window-local cut times in `c2.prompt`:** `00:03.958` (`95f`) and `00:06.958` (`167f`); global `[248, 320]`; Shot 1 `frames_after_the_join = 56` (`2.333 s`, not `39f` / `1.625 s`). (`00:10.333` / `00:13.333` absent from prompt.)
- **Beat 3 (`c3`):**
  - Requested overlap `22`, **applied overlap `22`** (`overlap_audio_t = 37`), `extension_frames = 187`, `window_frames = 209` (`window_audio_t = window_audio_official_t = 348`).
  - Carry (`c3_gen.overlap_frames = 22`), trim (`c3_append` wired to `c3_gen:2/3`), assembly (`c3.length` wired to `c3_gen:1`), and shot clocks (`applied_overlap_frames = 22`) all use `22` (`consistent: true`).
  - Note on beat 3 clocks: the updated 10:31 AM CT `beat3.txt` dropped `INSERT_JOIN` and has one authored cut `[Shot 2] At 00:06.500,` (`156f`), which rebases as no-op to window-local `00:06.500` (`156f`), global `513`. (Unit test `test_beat2_two_cuts_39f_overlap_consistency_and_shot1_not_1625s` also verifies `00:03.500 / 00:05.750` -> global `441 / 495` at overlap 22.)
- **`cond_audio_rows` (voice RefMod on all beats):**
  - `refapply`: packed `2000 == 2000` reserved (`ok: true`)
  - `c2_refapply`: packed `2130 == 2130` reserved (`ok: true`, `minimaxh3_oc_poolclub_v1_refmod_audio` + `minimaxh3_oc_poolclub_v1_refmod_visual`)
  - `c3_refapply`: packed `2074 == 2074` reserved (`ok: true`, `minimaxh3_oc_poolclub_v1_refmod_audio` + `minimaxh3_oc_poolclub_v1_refmod_visual`)
- **Loudness trace (synthetic 32 kHz seam with phase/DC discontinuity `seam_step_delta = 0.289695`):**
  - `declick` (`15.0 ms`, `480` samples): `seam_step_delta` drops to `0.000913`; segments `pre_overlap_tail = -12.70 dBFS`, `overlap_tail = -12.90 dBFS`, `seam_join = -13.01 dBFS`, `post_seam = -12.80 dBFS`.
  - `soft_av` (`8` ticks = `200 ms`, `6400` samples, tail weights `[1.0, 1.0, 0.969846, 0.883022, 0.75, 0.586824, 0.413176, 0.25, 0.116978, 0.030154]`): `seam_step_delta` drops to `0.000071`; segments `pre_overlap_tail = -12.70 dBFS`, `overlap_tail = -15.62 dBFS`, `seam_join = -20.10 dBFS`, `post_seam = -15.80 dBFS`.

---

## 5. Pack Hashes, `PROMPT.md` Repin, Vault/Token Status

- Placed pack `/home/evo/AI/community/runs/extend-test-3beat-20261115/` `beat1.txt`–`beat3.txt` bytes were copied unchanged (no beat prompt text edited) and verified by `sha256sum`:
  - `beat1.txt`: `5d507f9a774c12dd0bc40f9fbfa87514f7dcc16d6eb910ab407604cad125bd93`
  - `beat2.txt`: `e893d29c03bfc0f9d38ab085afb3588271c73a03ff91da572e0201b45a85ea1f`
  - `beat3.txt`: `f306fd34c09966f8558f9cdb371558c0ce7152d1815e37ebebd2f4b7ce637d7c`
- `/home/derekboone/evo-x3/records/voice-cap-followup/PROMPT.md` (backed up to `/home/derekboone/evo-x3/_archive/u40/PROMPT.md.bak-20261116`) was repinned to those exact three full sha256 values. No other copies existed on X3.
- **PixlStash vault & token check:**
  - `/home/evo/AI/5slock/libraries/vault.db`: **present** (`1,163,423,744` bytes via `stat`; contents not read/dumped).
  - `/home/evo/.config/pixlstash/`: **not present** (`No such file or directory`). No token created. Live API/token test (`test_pixlstash_live_api_token_skips_when_not_ready`) skips cleanly via `pytest.skip`.

---

## 6. Explicit Confirmations

- **No render queued:** `queue-remote.sh` was never run; ComfyUI `/prompt` was never called; dry build wrote `DRY_RUN` marker only.
- **PR #15375 / native masked continuation:** Not implemented (explicitly skipped per C5).
- **`end_action` lines:** Parsed verbatim from `/home/evo/AI/community/runs/extend-test-3beat-20261115/PLAN.md` via `parse_plan_end_actions` (no new wording invented).

---

## 7. Blocked / Left for Derrick

- **Gitea push from `evo` blocked on missing Gitea credentials** (`fatal: could not read Username for 'https://qnap.tailf242b2.ts.net': terminal prompts disabled`). Local commits are clean on `x3-linux`:
  - `/home/evo/AI/render`: `35e098d`, `2904e1b` (need push to `gitea/x3-render`).
  - `/home/evo/AI/community`: `0530815` (needs push to `gitea/x3-community`).
- **Pre-existing dirty tree in `/home/evo/AI/community`:** ~44 other pre-existing dirty/untracked items (linuxize/prior sync) were intentionally left uncommitted per brief rules.
- **PixlStash API token:** `/home/evo/.config/pixlstash/` does not exist yet (owned by the separate install/token job).
- **Live `extend-test-3beat` render:** Waiting on Derrick's yes after reviewing the dry build.
