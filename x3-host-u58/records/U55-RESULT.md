# U55 Result (2026-11-16)

## Overall Status: DONE

Summary of work: replaced the `submit_parody_run.py` graph-building layer in Render's writer queue path with 8 known-good AlienPc-rendered API templates in `/home/evo/AI/community/templates/`, a minimal 140-line template filler (`/home/evo/AI/community/scripts/parody/fill_request.py`), RefMod resolution helpers moved into `/home/evo/AI/community/scripts/parody/resolve.py`, archived `scripts/parody/submit_parody_run.py`, updated all callers/skills/docs/tests, verified all test suites + one real remote AlienPc render with `--position walking`, and committed + pushed both repos to Gitea.

---

## Work & Test Status

| Item | Status | Notes |
| --- | --- | --- |
| Work #1: 8 known-good API templates in `templates/` | DONE | Copied from AlienPc-completed runs; per-clip inputs (`c0.prompt`, `c1.prompt`, `img*.image`, `refmods.mod_1..8`, `save.filename_prefix`) reset to neutral placeholders. `b2.api.json` and `b2_refmod.api.json` untouched. Honest `beta6_int8` gap documented below for 3 clip types. |
| Work #2: `scripts/parody/fill_request.py` (140 lines) + `render_writer_pipeline.py` integration | DONE | Copies template, edits only per-clip fields, enforces 18+ safety guard (`_check_writer_18plus` + refusal check) while accepting arbitrary free-text `--position` (including `walking`), writes `prompt.txt`, `clip/request.api.json`, `build_report.json`, and `DRY_RUN` or `_render_order.json`. |
| Work #3: Archive `submit_parody_run.py` & repoint callers/skills/docs/tests | DONE | Moved to `scripts/parody/_archive/submit_parody_run.py.bak-20261116-u55`; callers, 5 skills, `render` docs/`loop-guard`/`x3_adapt.py`, and test suites updated. Left two historical reference docs untouched (`templates/b2.README.md` legacy 2-pass note and `skills/h3-parody-identity/references/h3-parody-identity-reference.md`) with zero working callers. |
| Work #4: Move writer RefMod picker into `scripts/parody/resolve.py` | DONE | Moved OC RefMod discovery/resolution helpers (`resolve_writer_refmods`, `index_named_identity`, etc.) into `resolve.py`; verified `resolve.resolve_writer_refmods(character="FCSydny")` returns `['minimaxh3_oc_poolclub_v1_refmod_audio', 'minimaxh3_oc_poolclub_v1_refmod_visual']`. |
| Dry E2E verification across all 8 clip types | DONE | Verified by `scripts/parody/test_u55_clip_types_e2e.py` (9 tests covering all 8 templates, `--position walking`, and 18+ block). |
| Real AlienPc remote render (`--position walking`) | DONE | `runs/u55_walking_smoke` (`73` frames, `plain` template) -> `prompt_id=ff7b1294-20e1-4d35-adde-9f6cdc2f5b3e`, `clip/clip.mp4` (`1,765,844` bytes). |
| Git commits & pushes (`community` + `render`) | DONE | Scoped commits by explicit path; `community` pushed to `gitea/x3-community` (`d06c559`); `render` pushed to `gitea/x3-render` (`38cd9eb`). |

---

## Templates Created (`/home/evo/AI/community/templates/`)

| Template | Nodes | Source Run | Render Model & Proof |
| --- | --- | --- | --- |
| `plain.api.json` | 22 | `runs/clip_001_beach_sunset/clip/request.api.json` | `beta7_int8HQ`, `768x1344`, 243f, `OBJECTIVE ok` 2026-11-16 18:57:22 CT (`5,140,232` B) |
| `oc_guide.api.json` | 22 | `runs/fcsydny-gvr2-20261116/guide/clip/request.api.json` | `beta7_int8HQ`, `768x1344`, 243f, `OBJECTIVE ok` 2026-11-16 14:47:01 CT (`4,084,081` B) |
| `oc_ref.api.json` | 21 | `runs/fcsydny-gvr2-20261116/ref/clip/request.api.json` | `beta7_int8HQ`, `768x1344`, 243f, `OBJECTIVE ok` 2026-11-16 14:55:13 CT (`3,703,770` B) |
| `named_parody.api.json` | 20 | `templates/b2_refmod.api.json` (`runs/vf_20261104/vf_b/request.api.json`) | `beta7_int8HQ` (4bc9bba), `768x1344`, 192f, `OBJECTIVE ok` 2026-11-04 17:21:30 CT (`1,581,414` B) |
| `talk.api.json` | 22 | `runs/cassie_party_parody/guide/clip/request.api.json` | `beta7_int8HQ`, `768x1344`, 124f, `JOB end ok` 2026-11-16 15:20:02 & 16:08:22 CT (`1,295,402` B) |
| `two_person.api.json` | 20 | `runs/ali163_tr5s_gi102_s51170001/request.api.json` | `beta6_int8`, `1344x768`, 124f, `OBJECTIVE ok` 2026-10-26 13:17:00 CT (`1,565,994` B) |
| `long_continuation.api.json` | 25 | `p4/p4_A10_cont_noAB.api.json` | `beta6_int8`, `576x1024`, 481f, `p4_result.json` ok 2026-10-20 CT (`355.7s`) |
| `ref2va_16x9.api.json` | 19 | `runs/ali163_tr5s10p_gi102_s51170001/request.api.json` | `beta6_int8`, `1344x768`, 124f, `OBJECTIVE ok` 2026-10-26 14:02:51 CT (`1,752,402` B) |

**Honest Template Gap Note:** No AlienPc-completed `beta7_int8HQ` runs exist on disk for `two_person`, `long_continuation` (`extend-test-3beat-20261115/dry-u40` was dry-only), or `ref2va_16x9` (`u41_dry_*` were dry-only), so those 3 templates were sourced from the latest AlienPc-completed `beta6_int8` runs on disk rather than fabricating untested graphs.

---

## E2E Diffs Observed (Template vs Filled `clip/request.api.json`)

From `scripts/parody/test_u55_clip_types_e2e.py`:
- `plain`: `['c0.inputs.length', 'c0.inputs.prompt', 'img_1.inputs.image', 'save.inputs.filename_prefix']`
- `oc_guide`: `['c0.inputs.length', 'c0.inputs.prompt', 'img_1.inputs.image', 'refmods.inputs.mod_1', 'refmods.inputs.mod_2', 'save.inputs.filename_prefix']`
- `oc_ref`: `['c0.inputs.length', 'c0.inputs.prompt', 'img_1.inputs.image', 'refmods.inputs.mod_1', 'refmods.inputs.mod_2', 'save.inputs.filename_prefix']`
- `named_parody`: `['c0.inputs.prompt', 'refmods.inputs.mod_1', 'save.inputs.filename_prefix']`
- `talk`: `['c0.inputs.prompt', 'img_1.inputs.image', 'save.inputs.filename_prefix']`
- `two_person`: `['c0.inputs.prompt', 'img.inputs.image', 'img2.inputs.image', 'noise.inputs.noise_seed', 'save.inputs.filename_prefix']`
- `long_continuation`: `['c0.inputs.prompt', 'c1.inputs.prompt', 'img.inputs.image', 'noise.inputs.noise_seed', 'save.inputs.filename_prefix']`
- `ref2va_16x9`: `['c0.inputs.prompt', 'img.inputs.image', 'noise.inputs.noise_seed', 'save.inputs.filename_prefix']`

---

## Real AlienPc Remote Queue Verification

- **Command**: `/home/evo/AI/render/x3/.venv/bin/python3 /home/evo/AI/community/scripts/parody/render_writer_pipeline.py /home/evo/AI/community/runs/u55_walking_smoke --ask "an adult woman in a white sundress walks barefoot along the beach at sunset" --position walking --still "/home/evo/AI/5slock/libraries/flow-export-2026-10-09/ex/39_Aug 21, 03_25 PM_part02of02/Woman_dancing_on_coastal_shoreline_20261009143458_7.jpg" --still-read /home/evo/AI/community/runs/clip_001_beach_sunset/still_read.json --frames 73 --queue --yes-derrick`
- **Run dir**: `/home/evo/AI/community/runs/u55_walking_smoke`
- **`build_report.json`**: `hook="fill_request"`, `position="walking"`, `frames=73`, `template="plain"`, `status="READY"`, `canvas=[768, 1344]`
- **ComfyUI `prompt_id`**: `ff7b1294-20e1-4d35-adde-9f6cdc2f5b3e`
- **Render log**: `OBJECTIVE ok clip frames=73 size=768x1344 audio=True bytes=1765844` (`BATCH closed rc=0 reason=all queued clips DONE ok done=1/1`)
- **Output file**: `/home/evo/AI/community/runs/u55_walking_smoke/clip/clip.mp4` (`1,765,844` bytes)

---

## Modified & Archived Files

### `/home/evo/AI/community`
- Created: `scripts/parody/fill_request.py` (140 lines), `scripts/parody/test_u55_clip_types_e2e.py`, and 8 templates under `templates/`
- Archived (`git rm`): `scripts/parody/submit_parody_run.py` -> `scripts/parody/_archive/submit_parody_run.py.bak-20261116-u55`
- Modified + backed up (`_archive/*.bak-20261116-u55`):
  - `scripts/parody/resolve.py` -> `scripts/parody/_archive/resolve.py.bak-20261116-u55`
  - `scripts/parody/render_writer_pipeline.py` -> `scripts/parody/_archive/render_writer_pipeline.py.bak-20261116-u55`
  - `scripts/parody/build_request.py` -> `scripts/parody/_archive/build_request.py.bak-20261116-u55`
  - `scripts/queue/chain_queue.py` -> `scripts/queue/_archive/chain_queue.py.bak-20261116-u55`
  - `skills/comfy-render/SKILL.md` -> `skills/comfy-render/_archive/SKILL.md.bak-20261116-u55`
  - `skills/h3-hc-render/SKILL.md` -> `skills/h3-hc-render/_archive/SKILL.md.bak-20261116-u55`
  - `skills/h3-parody-identity/SKILL.md` -> `skills/h3-parody-identity/_archive/SKILL.md.bak-20261116-u55`
  - `skills/h3-prompting/SKILL.md` -> `skills/h3-prompting/_archive/SKILL.md.bak-20261116-u55`
  - `skills/video-render/SKILL.md` -> `skills/video-render/_archive/SKILL.md.bak-20261116-u55`
  - `scripts/tests/test_run_queue_keep_comfy_process.py` -> `scripts/tests/_archive/test_run_queue_keep_comfy_process.py.bak-20261116-u55` (5 `submit_parody_run` CLI tests removed)
  - `scripts/parody/test_u52_e2e_passthrough.py` -> `scripts/parody/_archive/test_u52_e2e_passthrough.py.bak-20261116-u55`
  - `scripts/parody/test_u54_named_e2e.py` -> `scripts/parody/_archive/test_u54_named_e2e.py.bak-20261116-u55`
  - `scripts/parody/test_u37_builder_fixes.py` -> `scripts/parody/_archive/test_u37_builder_fixes.py.bak-20261116-u55`
  - `scripts/parody/test_u41_shape_and_ref_mode.py` -> `scripts/parody/_archive/test_u41_shape_and_ref_mode.py.bak-20261116-u55`
  - `scripts/parody/test_t1109_writer_index_refmods.py` -> `scripts/parody/_archive/test_t1109_writer_index_refmods.py.bak-20261116-u55`
  - `scripts/parody/test_modular_s3_and_writer_sys.py` -> `scripts/parody/_archive/test_modular_s3_and_writer_sys.py.bak-20261116-u55`
  - `scripts/parody/test_parody_ba5c.py` -> `scripts/parody/_archive/test_parody_ba5c.py.bak-20261116-u55`
  - `scripts/parody/test_parody_dynamic.py` -> `scripts/parody/_archive/test_parody_dynamic.py.bak-20261116-u55`
  - `scripts/parody/test_parody_phase3.py` -> `scripts/parody/_archive/test_parody_phase3.py.bak-20261116-u55`
  - `scripts/parody/test_writer_finalize.py` -> `scripts/parody/_archive/test_writer_finalize.py.bak-20261116-u55`
  - `scripts/parody/test_longclip_skill_routing.py` -> `scripts/parody/_archive/test_longclip_skill_routing.py.bak-20261116-u55`
- Pre-existing untouched local modifications: `notes/actions.log`, `dummy_run/`, `scripts/dummy_run/`

### `/home/evo/AI/render`
- Modified + backed up (`/home/evo/AI/render/_archive/*.bak-20261116-u55`):
  - `AGENTS.md` -> `_archive/AGENTS.md.bak-20261116-u55`
  - `RUN_ME.md` -> `_archive/RUN_ME.md.bak-20261116-u55`
  - `x3/README-X3.md` -> `_archive/README-X3.md.bak-20261116-u55`
  - `x3/x3_adapt.py` -> `_archive/x3_adapt.py.bak-20261116-u55`
  - `.pi/extensions/loop-guard.ts` -> `_archive/loop-guard.ts.bak-20261116-u55`
  - `.pi/extensions/loop-guard-test.mjs` -> `_archive/loop-guard-test.mjs.bak-20261116-u55`
- Pre-existing untouched local modifications: `writer_pipeline/dialogue_blacklist.jsonl`, `x3/render-pi.sh`

---

## Final Verification Results

- `pytest -q tests` (run from `/home/evo/AI/community/scripts` after all commits): **`137 passed, 2 skipped in 6.52s`** (down from `142 passed, 2 skipped` in U54 after removing 5 `submit_parody_run`-only CLI flag tests)
- `pytest -q parody` (run from `/home/evo/AI/community/scripts` after all commits): **`544 passed, 1 skipped in 11.84s`** (down from `583 passed, 5 skipped` in U54 after removing `submit_parody_run`-only tests across `parody/` and adding 9 E2E tests in `test_u55_clip_types_e2e.py`)
- `node .pi/extensions/loop-guard-test.mjs` (in `/home/evo/AI/render`): **`loop-guard unit tests OK 8`**

---

## Git Commits & Push Results

- `/home/evo/AI/community` (`x3-linux`): commit `d06c559` (`32 files changed, 3260 insertions(+), 3125 deletions(-)`), pushed `c26fc7d..d06c559 HEAD -> x3-community` to `gitea`
- `/home/evo/AI/render` (`x3-linux`): commit `38cd9eb` (`6 files changed, 36 insertions(+), 35 deletions(-)`), pushed `b8714a6..38cd9eb HEAD -> x3-render` to `gitea`
