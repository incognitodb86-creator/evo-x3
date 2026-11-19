0. Read fix_plan.md; AGENTS.md (global) is loaded as context. Search the code before assuming something is not built. Study C:\AI\lib\README.md when looking for a script.
1. Take the top unchecked `- [ ]` item only (skipping `- [x]`, `- [PARTIAL]`, `- [BLOCKED]`, and any `- [ ]` item with a `PARTIAL`/`BLOCKED` sub-bullet; one item per pass).
   - **Pre-built render execution:** if `request.api.json` / `prompt.txt` are already built on disk for the item, load **video-render only** and run multi-clip batches in one `run_queue.py` call.
   - **Prompt/workflow authoring:** load `h3-hc-render` section 6 + `h3-prompting` + `h3-max-ref2va-prompt` (+ `h3-parody-identity` for named parody) ONLY when writing or modifying prompts or workflow JSON.
1b. Before creating any script, workflow or skill, search for an existing one and extend or parameterize it instead of copying.
2. Verify before ticking: run the item's check/tests first. Tick `[x]` ONLY after every clause passes; otherwise mark `- [PARTIAL]` or `- [BLOCKED]` with one line why. Append one line to notes\progress.md and commit locally only when code or fix_plan changed (do NOT pull/copy/push fleet-brain or retry offline Gitea per pass). If the item needs Derrick, write notes\needs_derrick.md, mark `- [PARTIAL]`, and stop.
3. Smallest change that meets the item's done-line. Do simple edits directly; no one-off helper scripts, no DONE essays, no sleep-polling, no ce-plan/ce-code-review on small items.
4. When no `- [ ]` item remains in your block, append a short summary to notes\loop-report.md and stop.
