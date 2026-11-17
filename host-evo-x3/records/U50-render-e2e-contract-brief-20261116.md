# U50 — Render pipeline end-to-end contract check (EVO-X3), Nov 16 2026

Owner: Max Architect. Approved by Derrick (t2073u: "why are these bugs not caught previously").

## Why
Today a talk clip could never reach READY. The beat-card schema for talk allowed 2 line_topics (minItems 2), but wp_lint's talk_lines hard rule needs 3-5 lines. The unit-test fixture also used 2 topics, so the tests passed with the bug baked in. Max fixed it (minItems 3, maxItems 4, line 295), and Derrick then made lint warn-only: only youth_hint and scale_adult still block (render_writer_pipeline.py, around line 1700). Backups are in scripts/parody/_archive/*.bak-20261116-talklines and *-warnonly.

## Task
Files: /home/evo/AI/community/scripts/parody/ (owned by evo; use `sudo -n -u evo`), mainly render_writer_pipeline.py, wp_lint.py and test_writer_pipeline.py.
1. Static contract audit: for EVERY mode/position the pipeline supports (talk, the sex positions, oral, any others in its mode table), compare what the writer is told or allowed (schema minItems/maxItems, beat_task text, word or line budgets, frame/clip_seconds) against every wp_lint rule for that mode. List each mismatch, where one side permits output the other side flags (like talk_lines vs line_topics, or speech_budget 12 words vs 3-5 lines).
2. Fix each mismatch with the smallest edit, on the writer-schema/prompt side by default. Never loosen the 18+ rules (youth_hint, scale_adult). Back up first as .bak-20261116-u50.
3. Add ONE pytest that builds a real-shaped beat card for each mode at the schema's minimum and maximum and checks that lint does not flag line or budget counts. Fix any fixture that hides a mismatch.
4. Real end-to-end: for talk plus 2 other common modes, run render_writer_pipeline.py WITHOUT --queue into /home/evo/AI/community/runs/u50-e2e-<mode>/ using the still /home/evo/AI/5slock/libraries/flow-export-2026-10-09/ex/08_Sep 16, 02_39 PM/Cassie_Howard_on_chrome_pedestal_20261009141358.jpg and --character FCSydny, with a short neutral ask per mode. Record status, pick score, warnings and lint hard flags. (This uses gemma4-heretic through llama-swap; don't restart llama-swap.)
5. Run the whole pytest suite in scripts/parody.

## HARD RULES
- Never pass --queue or --yes-derrick, and never touch AlienPc/ComfyUI or ~/AI/locks.
- Never restart llama-swap, render-pi, herdr or the tagger, and never type into Render's pane.
- Never read PixlStash library contents. No secrets on command lines.
- Don't touch cassie_party_parody/ or fcsydny-gvr2-20261116/ runs.
- No git commits, no `git add -A`.

## STOP CONDITION
Write /home/derekboone/evo-x3/records/U50-RESULT.md with: the mismatch table (mode, writer side, lint side, fix), diffs or line refs, backups, pytest totals, the e2e results per mode, and PASS/FAIL. Then stop.
