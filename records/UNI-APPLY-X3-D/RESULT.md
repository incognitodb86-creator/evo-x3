# UNI-APPLY-X3-D RESULT

When: 2026-11-19 7:33-7:52 PM CT (America/Chicago). Doer: Max X3 lane (executor), Derrick t2958u/t2959u/t2960u ("apply all the stuff from opus that we can"; t2948u go to finish the plan). Lease line taken and removed. snapshot: in this commit. Rollback: not triggered.

Source: `mono` `0fdf10a2` (includes Opus `382eda61` + `466bcf3b`, box `2d5da1b8`, `9b10d437`, `9d35c650`, `c012e816`, `fabf26ee`) **merged three-way** with the uncommitted W1b fixes that were live on the X3 (base = `mono` `6be684a`, which equals live `community` `827d012` / `render` `a24f81b`). `MONO-S5` is still not done (`/home/evo/AI/evo-x3` does not exist), so files were copied into the part-branch checkouts; nothing was committed or pushed there.

## Step 0 - DONE
- HEADs: `/home/evo/AI/render` `a24f81b` (x3-linux), `/home/evo/AI/community` `827d012` (x3-linux), `/home/evo/AI/forge` `4cbbba0` (not touched).
- Backup root: `/home/evo/AI/_archive/20261119/x3-d-apply-1940/` (`pre-apply-existing.tar` = the 42 existing files before the copy, `inc/` = the 58 files applied, `beta7_convert.py.pre-layoutfix`, `test_u52_e2e_passthrough.py.pre`, `pi-job.pre-B2`, `syntax-check.ts.pre`).

## Item 1 - Writer files - DONE (with fixes)
- Kept live (Derrick t2951/t2953): `writer_prompt.md` example strip, the 6-word clone regenerate gate in `render_writer_pipeline.py`, filler rules incl. `"right there"` in `config.yaml` `filler_lines`, `wp_lint`/`wp_llm`/`wp_state` W1b changes, `ref2va_system_prompt.txt` / `ref2va_user_prefix.txt`.
- Added from mono: SK1/SK3 lines, `model_alias: flash-next-uncensored-v2`, `--prose-file`, Beta 7 wiring, realism LoRA block (`enabled: false`).
- Root cause found: the example strip lived only in the compiled `writer_prompt.md`; `wp_compile_prompt.py` rebuilds it from `render/AGENTS.md`, so any recompile dropped it (a compile run wiped it once during this apply; restored from backup within a minute). Fix: same three example lines stripped in `render/AGENTS.md`; recompile is now stable. `writer_prompt.md` sha256 `418777e9376457ace4d45f809cfded15416e9c345db80fb27246a89ec1a9187f` = `config.yaml` `writer_prompt_sha256`; `wp_compile_prompt.py` -> `rules=77 PASS=77 hard_fail=0 result=OK`.
- Dry writer ask (LLM): NOT RUN (writer runs go through Hermes next; see X3-E).

## Item 2 - RP1-RP3 - DONE
- `ffmpeg -h full | grep -c fps_mode` = 2.
- `test_vision_read_cache.py test_remote_comfy.py test_last_frame_extract.py test_run_queue_keep_comfy_process.py`: 26 passed.

## Item 3 - Skills - DONE
- `community/skills` updated (SK5, FX1 `flux-klein-prompting`). Hermes loads it from `skills.external_dirs` (X3-E), so no local Hermes copy was made (it would shadow the community copy).

## Item 4 - pi YAML syntax check - DONE (settings skipped)
- `/home/evo/.pi/agent/extensions/syntax-check.ts` = `config/pi-evo/extensions/syntax-check.ts` (`yaml.safe_load` count 1).
- `/home/evo/.pi/agent/settings.json` NOT replaced: live already names `flash-next-uncensored-v2-sub`; the repo copy would re-add the v1 `-sub` key.

## Item 5 - ST6 - DONE (dry run only)
- `/usr/local/bin/evo-raw-clip-cleanup` installed (root 0755). Dry run: `DRY_RUN candidates=0 bytes=0 list=/home/evo/AI/_runs/st6-raw-cleanup-20261119-1950.txt`. `--apply` never run.

## Fixes made during the apply (Opus/mono mistakes)
1. `beta7_convert.convert_to_beta7` (wired into the pipeline by `9d35c650`) flattened one-line sections to `summary: ...` on the header line. The official layout (our `h3-prompting/references/worked-examples.md`, `build_request.py`) puts each header on its own line. Now always `header:\n body`.
2. `test_u52_e2e_passthrough.py` still expected the pre-U56 behaviour (audio header kept + warning). It now expects the Beta 7 conversion (soundscape folded into plain sound sentences, no header).
3. `test_beta7_convert.py` hard-coded the filler list without Derrick's `"right there"` (t2951).

## Tests (in place, `/home/evo/AI/render/x3/.venv/bin/python3`)
- `community/scripts/parody`: before 560 passed, 1 skipped -> after **577 passed, 1 skipped**.
- `test_prose_file_gate.py test_flux_h3_redteam.py test_beta7_convert.py`: 19 passed.
- `community/scripts/tests`: 151 -> 160 passed, 2 skipped. `h3max_bridge`: 6 passed.
- After the copy, every tracked `scripts/ skills/ templates/` file and `render/` file on the X3 matches `mono` `x3/` byte for byte (sha256 check).
