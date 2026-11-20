# REA parody pipeline: coding result (C8)

When: 2026-11-20, C8 check 1:06–1:10 PM America/Chicago (CST).
Doer: Max Architect. Worktree `/home/evo/AI/_worktrees/rea-parody`, branch `pi/rea-parody`.
HEAD before this file: `406899fc2094a013184a9496a9cda7e4bdcc0c1b` (`rea C7: queue and assemble`).
Did not push. Did not fast-forward `mono`. Max will do the dual-host snapshot push.

## Commit list — OK

`git log --oneline mono..pi/rea-parody` shows exactly 7 commits, `rea C1` through `rea C7`, in order:

| Commit | Date (CST) | Subject |
|---|---|---|
| `873aa9e` | 2026-11-20 11:53:05 | rea C1: onset probe |
| `bfd43b1` | 2026-11-20 12:03:26 | rea C2: shot plan helpers |
| `237eabb` | 2026-11-20 12:10:33 | rea C3: flux rea templates + lora cap |
| `ad15866` | 2026-11-20 12:17:01 | rea C4: plan stage |
| `518225b` | 2026-11-20 12:23:38 | rea C5: flux and build stages |
| `edf2ed4` | 2026-11-20 12:31:27 | rea C6: color match and master |
| `406899f` | 2026-11-20 12:45:47 | rea C7: queue and assemble |

Authors: Forge-X3. No extra commits between `mono` and `pi/rea-parody`.

## File-scope — OK (no extras)

Each commit's `git show --name-status` matches the files named in that unit's section of `PIJOB-TASKS.md`. No extra paths.

- C1 (`873aa9e`): added `x3/community/scripts/parody/rea_onset_probe.py`, `test_rea_onset_probe.py`.
- C2 (`bfd43b1`): added `x3/community/scripts/parody/rea_shot_plan.py`, `test_rea_shot_plan.py`.
- C3 (`237eabb`): modified `x3/community/scripts/parody/flux_still.py`; added `test_flux_rea_templates.py`, `x3/community/templates/flux_rea_edit.candidate.api.json`, `x3/community/templates/flux_rea_pose.candidate.api.json`.
- C4 (`ad15866`): added `x3/community/scripts/parody/rea_parody_remake.py`, `test_rea_parody_remake.py`.
- C5 (`518225b`): modified `rea_parody_remake.py`, `test_rea_parody_remake.py`.
- C6 (`edf2ed4`): added `x3/community/scripts/parody/rea_color_match.py`, `test_rea_color_match.py`.
- C7 (`406899f`): modified `rea_parody_remake.py`, `test_rea_parody_remake.py`.

## Leftover fixtures

`git status` showed only untracked `x3/comfy-alienpc/`. Removed the three leftover untracked PNGs from Max's 11:56 AM CST test run, and nothing else:

- `x3/comfy-alienpc/input/community/parody_ref_0db62ddda3_megan_flux.png`
- `x3/comfy-alienpc/input/community/parody_ref_1c75b4bb23_sydney_flux.png`
- `x3/comfy-alienpc/input/community/parody_ref_5ed7b5554d_plain.png`

Left untouched four later untracked PNGs dated 12:09–12:10 PM CST in the same folder. The full parody suite then recreated the same three 11:56 filenames at 1:08 PM CST as test side effects. All of `x3/comfy-alienpc/` remains untracked and was not added to this commit.

## Tests

Command (as `evo`), 2026-11-20 1:08:04–1:08:34 PM CST:

`cd x3/community/scripts/parody && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q`

venv Python 3.14.10. Result: **6 failed, 694 passed, 1 skipped** in 29.78s (exit 1). Failures were not fixed.

First failures:

1. `test_parody_phase1.py::TestParodyPhase1::test_u2_r2_good_row_native_face_voice` — expected a native-face RefMod slot path; no slot path matched.
2. `test_parody_phase1.py::TestParodyPhase1::test_u2_r4_dual_match_stacking` — same class of assertion on a dual-match slot path.
3. `test_parody_phase3.py::TestParodyPhase3::test_r7a_request_nodes_and_8_slots` — request `mod_1` was `(none)` instead of the expected H3 RefMod stem.
4. `test_parody_phase3.py::TestParodyPhase3::test_r8_run_record_artifacts` — `loaded_refmods` was empty (`IndexError` on index 0).
5. `test_rea_onset_probe.py::test_cli_writes_json` — C1 CLI test: `subprocess.Popen` raised `RuntimeError: U3 CPU fixture blocked subprocess.Popen`. This is the only failure in a C1–C7 new test file. The other new unit tests (`test_rea_shot_plan.py`, `test_flux_rea_templates.py`, `test_rea_parody_remake.py`, `test_rea_color_match.py`) did not appear in the failure list.
6. `test_writer_pipeline.py::test_acceptance3_round2` — summary-wording assertion failed (forbidden terms still present / expected prefix missing). Prompt prose is not recorded here.

## Model per unit

All seven REA units ran on the X3. Each `detail=` line is `commits_added=1 model=x3`. No STUCK on C1–C7.

| Unit | pi-job run | Status | detail= | Updated (CST) |
|---|---|---|---|---|
| C1 | `20261120-115102-code-8b2a` | DONE | `commits_added=1 model=x3` | 2026-11-20 11:53:34 |
| C2 | `20261120-115825-code-db01` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:03:37 |
| C3 | `20261120-120359-code-873d` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:10:49 |
| C4 | `20261120-121102-code-03c0` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:17:17 |
| C5 | `20261120-121724-code-0b73` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:23:52 |
| C6 | `20261120-122406-code-503e` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:31:47 |
| C7 | `20261120-123159-code-2a40` | DONE | `commits_added=1 model=x3` | 2026-11-20 12:46:09 |

Same-day code run, not a REA unit: `20261120-070728-code-3e81` was `status=STUCK` with `detail=rc=0 commits_added=0 model=x3` at 7:09:14 AM CST. That job was a slugify smoke test under `/home/evo/AI/_scratch/gemma-pi-test-20261120-0702/repo2`, not C1–C7.

## Push

Not done in this check. No gitleaks, no `mono` fast-forward, no GitHub/Gitea push.
