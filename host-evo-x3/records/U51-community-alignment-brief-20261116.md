# U51: Community alignment review of the Render H3 pipeline (EVO-X3), Nov 16 2026. REPORT ONLY.

Owner: Max Architect. Derrick, t2078u: "double check everything against the community stuff. I want a community pipeline that includes our guidance and skills for making prompts as a helper only not to override shit."

## Goal
Find out what the community actually does for MiniMax H3 / 10Eros prompt-to-video, then compare our pipeline step by step. The target design: the community workflow is the backbone, and our prompt skills and guidance only help the writer, never block or override.

## Research (cite a URL for every claim)
- The official MiniMax H3 docs and prompt-writing guide, and the official/ComfyUI H3 workflow templates (Ref2V / I2V / guide).
- The pytraveler MiniMax-H3-Prompt-Rewriter (HF model plus ComfyUI node) and how people wire it.
- Community workflows and tips on Reddit, HF discussions, Civitai and GitHub from the last ~60 days: frame counts and valid lengths, resolution, seeds, how the prompt is made, and whether anyone runs prompt linters or gates.

## Ours (read, don't edit)
/home/evo/AI/community/scripts/parody/ (render_writer_pipeline.py, wp_lint.py, build_request.py), /home/evo/AI/community/scripts/run_queue.py, /home/evo/AI/render/x3/queue-remote.sh, /home/evo/AI/render/AGENTS.md, and the Render skills under /home/evo/AI/render (h3-prompting, h3-parody-identity and similar). Use `sudo -n -u evo` to read.

Known bugs today:
(a) talk line_topics minItems 2 versus a lint rule needing 3-5 lines (fixed);
(b) lint was made warn-only except youth_hint and scale_adult;
(c) --frames 120 was passed straight to the H3 request, H3 rendered 124 (the valid grid is 5+17k), and run_queue's objective check rejected it.

## Deliver
Write /home/derekboone/evo-x3/records/U51-RESULT.md with:
1. A table of our pipeline steps in order, each marked COMMUNITY (matches community practice), HELPER (our guidance that only advises), or OVERRIDE (ours blocks, rewrites or replaces community behavior), with file:line and a community source.
2. Every bug or mismatch found, including (c), with the smallest fix.
3. A minimal target pipeline: the community backbone, plus where our skills plug in as advice only. Keep everything useful we have; don't over-strip.
4. The proposed edits as a numbered list (file, what changes, backup name). DO NOT APPLY THEM.

## HARD RULES
- Report only: no edits, no git, no queueing, nothing touching AlienPc/ComfyUI or locks, no restarts, never typing into Render's pane.
- Never read PixlStash library contents, never read Sydney's chats, and never put secrets on command lines.

## STOP CONDITION
Write U51-RESULT.md, then stop.
