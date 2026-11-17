# U52: Apply the U51 edits with beta7 corrections (Derrick approved, Nov 16 2026, 3:43 PM CT, card t2091s7616)

Derrick's exact answer: "Apply all 7 U51 edits with the beta7 corrections (headers handled in the writer brief plus a warning, skill rewording, citation fixes)".

Inputs (read both in full first):
- /home/derekboone/evo-x3/records/U51-RESULT.md (section 2 bugs, section 3 target pipeline, section 4 edits 1-7)
- /home/derekboone/evo-x3/records/U51-beta7-check-20261116.md (corrections)

Files are owned by evo. Write a step script to /tmp and run it with `sudo -n -iu evo bash /tmp/u52-step.sh` (same as U40/U41).

## HARD RULES
- Back up every file before editing: `<dir>/_archive/<name>.bak-20261116-u52`.
- Do NOT queue or render anything. Do not call run_queue.py, queue-remote.sh, or `--queue`. Do not POST to ComfyUI. No `--yes-derrick`.
- Do NOT edit llama-swap.yaml, systemd units, keys, tokens, or PixlStash. Do not print secrets.
- Do NOT view images or read PixlStash library contents. Do not read Sydney's chats, persona or memory.
- No `git add -A`, no push, no force. Commit only the files you changed, by explicit path, in /home/evo/AI/community with author "Max Architect <max@fleet.local>" (via `git -c user.name=... -c user.email=...`). For /home/evo/AI/render, commit too if it is a git repo; otherwise leave the backups.
- Do not lose useful existing material. Keep RefMod/voice-ref resolution, guide/ref still modes, vision caption, scene memory, the 18+ guard (youth_hint, scale_adult, _MINOR_RE), missing-file/RefMod/graph errors, remote queue and upscale. Keep the skills' craft content. Only change the wording from "gate/blocked/NOT_READY/do not loosen" to advice.
- The only policy hard stops left are 18+ (youth_hint / scale_adult / _MINOR_RE), an empty or refused writer output, and missing still/RefMod/graph files. Everything else is a warning or note.

## EDITS (from U51 section 4, with the beta7 corrections)
1. build_request.py: add `align_h3_frames()` (ComfyUI align_frame_count, `while f % 17 != 5: f += 1`; >243 still raises), use it in validate_single_clip_frames and main. Make advisory/passthrough the default for writer requests: no rewriting, stripping, reordering or injecting of the writer's sections; remove the "; all characters are consenting adults." injection; stop dropping spoken lines in convert_speech. Checks go to warnings.
2. run_queue.py graph_expect: cover MiniMaxH3ReferenceToVideo, MiniMaxH3ImageToVideo and EmptyMiniMaxH3LatentAV, and apply the same 17n+5 alignment to the expected length.
3. render_writer_pipeline.py: snap explicit --frames with br.align_h3_frames BEFORE the writer call, so the writer's timestamps fit the real length. Remove the automatic rewrite/rewrite_block/rewrite_builder loop; put any retry behind a new `--fix-once` flag, default off. Keep the writer's output verbatim. Downgrade surface_mismatch and missing ending_state.pose to warnings. Stop clean_still_read from mutating captions. Fix summary_line `queued=` to report r.get("submitted"). Keep the beat-card/candidate machinery only if removing it would break tests that cover real behavior; prefer the smallest change that makes the writer text pass through untouched, and say in RESULT what you kept and why.
4. wp_lint.py: remove the [Shot 2+] ban (keep a soft warning if shot timestamps are non-monotonic or past clip length). Make all rules advisory except youth_hint and scale_adult. Make the 3-line talk minimum a note.
   - beta7 CORRECTION: add a loud `!` warning (not a strip, not a block) if `overall_soundscape:` or `non_diegetic_music:` appears (TenStrip HF #77 says they wreck beta7 audio).
5. submit_parody_run.py: the writer-run path uses the snapped frames and the advisory/passthrough build by default; strict only if `--strict` is passed.
6. Instructions and skills:
   - /home/evo/AI/render/AGENTS.md: skills are craft advice; Render may write writer_output.txt directly and call writer-run, or use render_writer_pipeline.py as a helper; remove "builder rejects/rewrites" and "do not edit writer_output.txt" constraints.
   - h3-prompting SKILL.md (every copy under /home/evo/AI/community/skills and /home/evo/AI/render): mark R5-R31 (except the 18+ rule) as craft advice; add the 17n+5 frame note; reword "(the builder sends these back NOT_READY)", "the builder flags both", "(builder W5; do not loosen)" and similar as advice. Fix citations: R11's #63 retention format came from a user's prompt (Portland01), not TenStrip, and the thread is beta6; #49 has no confirmed TenStrip author; R9's "TenStrip's own advice" on long prompts is unverified. Say so plainly and don't delete the advice.
   - beta7 CORRECTION: /home/evo/AI/render/rewriter/ref2va-system-prompt.md and the writer brief/system prompt used by render_writer_pipeline.py: no `overall_soundscape:` / `non_diegetic_music:` headers; audio as plain diegetic sound sentences at the end of detailed_description (h3-prompting R7). Remove the silent header stripper from build_request/wp_lint only after this is done.
7. /home/evo/AI/render/x3/queue-remote.sh line ~32: message says "X3 submitter busy: waiting in background..." instead of "GPU busy".

## TESTS (required)
- Update tests that asserted the old blocking/rewriting behavior so they assert the new passthrough/warning behavior. Don't delete coverage of 18+, missing files, RefMods, guide/ref modes or the remote queue.
- Add end-to-end tests (Derrick: bugs must be caught end to end, per clip type, not by hand-made unit fixtures alone): for each of talk, single position, and guide and ref still modes, run render_writer_pipeline.py up to the built request with a stubbed writer reply (no LLM, no queue) using --frames 120. Assert c0.inputs.length == 124, slots/build_report agree, graph_expect(request) == 124, the writer's text (including a 3rd spoken line and a [Shot 2] line) reaches c0.inputs.prompt unchanged, no "consenting adults" text, and a header gives a warning but isn't stripped and doesn't block.
- Run the full suite: `cd /home/evo/AI/community/scripts && /home/evo/AI/render/x3/.venv/bin/python3 -m pytest -q parody` plus any run_queue tests. Everything must pass.

## STOP CONDITION
Write /home/derekboone/evo-x3/records/U52-RESULT.md with: each edit (done/skipped + why), every file changed with its backup path, commit hashes, the pytest summary line, the new e2e test names and results, and anything you kept from the old machinery and why. Then stop. Do not start any render.
