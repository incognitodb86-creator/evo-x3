# UNI-APPLY-ALIENPC-A Result

Date: 2026-11-19 13:52 CT
Doer: Antigravity Gemini 4 Hydrogen (medium) acting as AlienPc Forge

## Status Summary
- **M7 check**: DONE (no overlap with incoming 10 paths)
- **Patch apply**: DONE (10 files applied & committed locally; not pushed)
- **Tests 1-3**: DONE (all passed)
- **INV1**: SKIPPED (superseded by AGT1 in UNI-APPLY-ALIENPC-B-AGT1)
- **INV1b**: SKIPPED (ships with AGT1 in UNI-APPLY-ALIENPC-B-AGT1)
- **S2 hook**: SKIPPED (held; `scripts/comm.py` and `templates/flux_stills_s2_kv.api.json` untouched)

## Git & Patch Details
- **mono SHAs**: `a808401`, `30f9997`, `df6815c`, `4c4d4a6`, `6129330`, `c0c9492` (staged patch built from `85a6114`)
- **Pre-HEAD**: `6dadffc4742a554435c9a5f4b7ef3a256b4464af`
- **Post-HEAD**: `90c36651de3a392f9d922b6a9fc3ade4b01c3e51` (`UNI-APPLY-ALIENPC-A: S2 allowlist + M4/ST4/ST5 candidates (mono 85a6114)`)
- **Patch path**: `C:\AI\_archive\20261119\community\UNI-APPLY-ALIENPC-A.patch`
- **Patch SHA256**: `E6E9D20BF8A4B2AA62B042AF4626FB27144BBB3C5041CCF7FDD3F9C40B471E2A`
- **Pre-existing target files backed up**: none (all 10 were new files)
- **Locked file check**: `git -C C:\AI\community diff HEAD~1 HEAD --stat -- scripts/comm.py templates/flux_stills_s2_kv.api.json` -> empty (untouched)

## Checks & Tests
- **Idle check**: `Test-Path C:\AI\locks\gpu-render.lock` = `False` (`:8447/health` skipped per 2026-11-19 1:52 PM CT update).
- **Test 1 (S2 pytest)**: `12 passed in 0.26s` (`python -m pytest -p no:cacheprovider C:\AI\community\scripts\tests\test_template_allowlist.py -v` with `PYTHONDONTWRITEBYTECODE=1`).
- **Test 2 (CLI smoke)**:
  - `b2.api.json`: `ALLOW b2` (exit `0`)
  - `b2_omni_rewriter.api.json`: `REFUSE refused LLM/rewriter node rewriter_options (MiniMaxH3RewriterOptions)` (exit `1`)
- **Test 3 (6 candidate JSON + REFUSE check)**: all 6 `*.candidate.api.json` files parsed as valid JSON and returned `REFUSE` (exit `1`) from `template_allowlist.py`:
  - `miraclein_t2i.candidate.api.json` (JSON=OK, rc=1)
  - `miraclein_refmod.candidate.api.json` (JSON=OK, rc=1)
  - `miraclein_edit.candidate.api.json` (JSON=OK, rc=1)
  - `flux_stills_t2i_klein.candidate.api.json` (JSON=OK, rc=1)
  - `flux_stills_pose_klein.candidate.api.json` (JSON=OK, rc=1)
  - `flux_stills_layout_klein.candidate.api.json` (JSON=OK, rc=1)

## `git -C C:\AI\community status -- templates scripts`
```
On branch master
Your branch is ahead of 'gitea/master' by 1 commit.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	scripts/_archive/
	scripts/queue/_archive/
	scripts/tests/_archive/

nothing added to commit but untracked files present (use "git add" to track)
```
