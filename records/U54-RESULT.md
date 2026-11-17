# U54 Result (2026-11-16)

## Status by Item

### Approved Fixes
- **Fix 1 (One path for named people):** DONE — `resolve_named_identity()` in `/home/evo/AI/community/scripts/parody/render_writer_pipeline.py`, Cassie Howard -> Sydney Sweeney alias in `/home/evo/AI/community/scripts/parody/aliases.json`, `IDENTITY (parody)` brief + `<Subject 1>` / `<Audio 1>` naming in `assemble_output()`, `--names` / `--actor` CLI flags, `spoof` overlay updated to tone-only, no `FCSydny` default. Asks without names stay on the plain writer.
- **Fix 2 (The ask beats the still & preserve quoted dialogue):** DONE — Updated `/home/evo/AI/render/AGENTS.md` (L7, L42, L45, L78, L81) so still stays for face/body/light/framing and the ask beats the still for setting/wardrobe/lines. Updated `render_writer_pipeline.py` so quoted `<d>` lines from the ask raise `max_lines_per_speaker` / `speech_words_max` and are marked mandatory verbatim in `brief_block` and `prose_messages`.
- **Fix 3 (PixlStash search in Render AGENTS.md):** DONE — Updated `/home/evo/AI/render/AGENTS.md` (L14, L172) to search by `character_id` (`FCSydny = 1`, `FCMegan = 2`), note `file_path` is relative to `/home/evo/AI/5slock/libraries/`, and remove stale `stills/approved_characters/POOL` wording (18+ is the only check).
- **Fix 4 (End-to-end tests):** DONE — Added `/home/evo/AI/community/scripts/parody/test_u54_named_e2e.py` covering a named talk clip (Cassie Howard / Sydney Sweeney) and a named spoof clip (Daenerys Targaryen / Emilia Clarke) through the real pipeline (dry, no `--queue`), asserting names, RefMod stems, and every ask line.

### Simplification Cuts
- **Cut 1 (Default `n_candidates: 1`, drop judge, keep `--n-candidates` flag):** DONE
- **Cut 2 (Talk clips & `--frames` runs use minimal beat card, no LLM planning call):** DONE
- **Cut 3 (Shrink live `wp_lint.py` checks, keep 18+ hard stop, remove dead `block_ready`):** DONE (`minimal=True` in live pipeline; 18+ `youth_hint`/`scale_adult`/`_MINOR_RE` preserved; `block_ready` removed from `config.yaml`)
- **Cut 4 (Keep one writer command, retire classic parody CLI):** DONE (`submit_parody_run.py` defaults to `_writer_run_cli`; classic parser moved to `classic_main` / `classic` subcommand for `test_parody_ba5c.py`; `AGENTS.md` and `skills/h3-parody-identity/SKILL.md` updated)
- **Cut 5 (`render-pi.sh` loads only `h3-prompting` and `h3-parody-identity`):** DONE (Ref2VA/hardcore skills noted as on-demand in `AGENTS.md`; spoof contradiction in `AGENTS.md` L81 aligned)
- **Cut 6 (`build_request.py` split, repair loop, second linter):** SKIPPED (held per brief)
- **Cut 7 (Fix stale docs/config: Windows paths, still pool, "no vault on X3"):** DONE (`RUN_ME.md` rewritten for X3 Linux, `AGENTS.md` L53/L160/L173 updated, `config.yaml` `default_character`/`still_pool` removed, `auto_still` updated)
- **Cut 8 (Stop writing per-run debug files after queueing):** DONE (`cand_*`, `lint_*`, `slots.json`, `route.json`, `beat_card*`, `rewrite*` gated behind `--debug`)
- **Cut 9 (Merge acts, modes, overlays into one classification):** DONE (removed duplicate `spoof` regex from `render_writer_pipeline.py` `TONE_WORDS`; unified in `wp_router.route_mode` with `tone_flags`)
- **Cut 10 (77-rule compile gate):** SKIPPED (held per brief)
- **Cut 11 (Remove frozen A/B sampler and persona arms):** DONE (pinned sampler A and persona `current` in `config.yaml`, removed sampler B and `--sampler-arm` / `--persona` CLI flags)

## Files Modified & Backups (`.bak-20261116-u54`)
- `/home/evo/AI/community/scripts/parody/aliases.json` -> `_archive/aliases.json.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/render_writer_pipeline.py` -> `_archive/render_writer_pipeline.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/submit_parody_run.py` -> `_archive/submit_parody_run.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/wp_lint.py` -> `_archive/wp_lint.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/wp_router.py` -> `_archive/wp_router.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/test_writer_pipeline.py` -> `_archive/test_writer_pipeline.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/test_parody_ba5c.py` -> `_archive/test_parody_ba5c.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/test_u52_e2e_passthrough.py` -> `_archive/test_u52_e2e_passthrough.py.bak-20261116-u54`
- `/home/evo/AI/community/scripts/parody/test_u54_named_e2e.py` (new file)
- `/home/evo/AI/community/skills/h3-parody-identity/SKILL.md` -> `skills/h3-parody-identity/_archive/SKILL.md.bak-20261116-u54`
- `/home/evo/AI/render/AGENTS.md` -> `/home/evo/AI/render/_archive/AGENTS.md.bak-20261116-u54`
- `/home/evo/AI/render/RUN_ME.md` -> `/home/evo/AI/render/_archive/RUN_ME.md.bak-20261116-u54`
- `/home/evo/AI/render/x3/render-pi.sh` -> `/home/evo/AI/render/_archive/render-pi.sh.bak-20261116-u54`
- `/home/evo/AI/render/writer_pipeline/config.yaml` -> `/home/evo/AI/render/writer_pipeline/_archive/config.yaml.bak-20261116-u54`

## Pre-existing Uncommitted Files (Left Untouched)
- `/home/evo/AI/render/writer_pipeline/dialogue_blacklist.jsonl`: modified before U54 started (contains lines from earlier runs); left uncommitted.
- `/home/evo/AI/community`: `notes/actions.log`, `dummy_run/`, `scripts/dummy_run/` left uncommitted.

## Commits & Pushes

### `/home/evo/AI/community` (`x3-linux` -> `gitea/x3-community`)
- `c3ce901` U54 Fix 1: one path for named people (INDEX + RefMod + spoof as tone only)
- `adf17ed` U54 Fix 2: ask beats still and preserve quoted dialogue in writer pipeline
- `5f54823` U54 Fix 4: add end-to-end tests for named talk and named spoof clips
- `85a1a7e` U54 Cut 1: default n_candidates to 1, drop judge call, keep --n-candidates flag
- `f6393a5` U54 Cut 2: talk clips and --frames runs use minimal beat card with no LLM planning call
- `e54e079` U54 Cut 3: shrink live wp_lint checks to 18+ hard stops, headers, blacklist, and spoken_words
- `0093343` U54 Cut 4: retire classic parody CLI from default main(), point skill to one writer command
- `f45d7b6` U54 Cut 7: remove still_pool lookup from auto_still
- `e8509fc` U54 Cut 8: gate per-run debug files (cand_*, lint_*, slots, route, beat_card*) behind --debug
- `bba4c33` U54 Cut 9: unify routing in wp_router (spoof/cinematic/gonzo as tone flags, remove duplicate spoof regex)
- `c26fc7d` U54 Cut 11: remove --sampler-arm and --persona CLI flags and A/B overrides

### `/home/evo/AI/render` (`x3-linux` -> `gitea/x3-render`)
- `52c7f62` U54 Fix 2: ask beats still for setting, wardrobe, and lines in AGENTS.md
- `341f88f` U54 Fix 3: PixlStash search by character_id and remove stale POOL wording in AGENTS.md
- `8709ca3` U54 Cut 1: default n_candidates to 1 in config.yaml
- `297d072` U54 Cut 3: remove dead block_ready config from config.yaml
- `aff0846` U54 Cut 4: standardize AGENTS.md on the one writer command
- `2698069` U54 Cut 5: load only h3-prompting and h3-parody-identity in render-pi.sh; keep one craft source
- `fa769de` U54 Cut 7: fix stale Windows paths, still_pool, default_character, and vault.db docs
- `2068e09` U54 Cut 11: pin sampler A and persona current in config.yaml, remove sampler B

## Pytest Totals (Final, after all edits)
- `pytest -q tests`: **142 passed, 2 skipped** in 7.07s
- `pytest -q parody`: **583 passed, 5 skipped** in 15.81s

## Live Dry E2E Output (`render_writer_pipeline.py`, no `--queue`)
1. **Named TALK (`--still-mode guide`)** — `/tmp/u54_e2e_talk`:
   - `READY run=/tmp/u54_e2e_talk pick=cand_1 score=80 spoken_words=11 seconds=32.4 queued=False`
   - `refmods.stems`: `['minimaxh3_sydneysweeney_v1_refmod']`, `source`: `'character'`, `still_mode`: `'guide'`, `submitted`: `False`
   - `prompt.txt` contains `Cassie Howard (Sydney Sweeney)` and all 4 ask lines (`You look good.`, `So good.`, `You can do this.`, `Just breathe.`).
2. **Named SPOOF (`--still-mode ref`)** — `/tmp/u54_e2e_spoof`:
   - `READY run=/tmp/u54_e2e_spoof pick=cand_1 score=100 spoken_words=9 seconds=23.7 queued=False`
   - `refmods.stems`: `['minimaxh3_emiliaclarke_v1_refmod']`, `source`: `'character'`, `still_mode`: `'ref'`, `submitted`: `False`
   - `prompt.txt` contains `Daenerys Targaryen (Emilia Clarke)` and both ask lines (`Where are my dragons?`, `Do not lie to me.`).
