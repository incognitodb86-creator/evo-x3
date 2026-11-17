# U53: Forge batch from Fleet Reviewer's audit (EVO-X3), Nov 16 2026

Owner: Max Architect. Approved by Derrick on Fleet Reviewer card t274s961 (4:14 PM CT) and in Max chat t2115u ("ok go").
Full audit with evidence and a fix for every row: /home/derekboone/evo-x3/records/2026-11-16-forge-audit.md (brain 60_reviews/fleet @ 87e735d). Read it first. Do ONLY the items below.

## Approved items (do in this order)
1. **B3, Ralph lock.** ralph.sh treats the 0-byte ~/AI/locks/gpu-render.lock (left by queue-remote.sh's flock) as "GPU busy", so each pass waits an hour and gets skipped. Make ralph.sh test the lock with `flock -n` (the same way queue-remote.sh does), not by checking whether the file exists. Then run a 2-item smoke loop that uses no GPU and makes no renders, and show it doesn't stall.
2. **B4, Gitea restore.**
   - Commit by path only (never `git add -A`) on community x3-linux and the x3-forge files.
   - Linuxize the x3-forge paths to /home/evo.
   - Add agent-shared/extensions.
   - Relay-push to Gitea the same way earlier X3 commits reached it. If no push credentials exist on the X3, stop that step and say so in RESULT.
   - Prove it with a fresh clone into /tmp and a dry start (no model load, no agent launched).
3. **I2, Forge loop safety checks** (Derrick: "Yes to Forge loop safety checks, even though it isn't stock"):
   - clear stale fix_plan items;
   - a per-pass backpressure check that includes a skill-load smoke test;
   - a `git diff --stat` file cap per pass;
   - deny edits to skills/ and AGENTS.md from inside loops;
   - one worktree per loop.
4. **I3, fix the failing tests. Don't mark them xfail.** In community/scripts/tests:
   - test_b2_lora_param.py (4 tests): hardcoded C:\AI\community template path.
   - test_run_queue_keep_comfy_process.py::test_default_off_end_to_end_writer_run_argv: fixture is from before U52 and comes back NOT_READY.
   - test_run_queue_one_at_a_time.py::test_free_comfy_calls_api_free_when_loaded: calls a live local ComfyUI. Mock it, or skip it in Linux remote mode.
   - Collection error, test_free_comfy_args.py (StopIteration): AlienPc-only input.
   - Collection error, test_phase1_still.py: Windows template path.
   - The real bug: comm.py:29 writes its log to a Windows path. Make it portable, derived from __file__.
   - Target: `pytest -q tests` and `pytest -q parody` both fully green, with true totals reported.
5. **I8, rule-8 sweep of Forge AGENTS.md.** Fix these contradictions, then trim:
   - L50 vs the lease README;
   - L39 vs PROMPT.md L4;
   - L29 MCP;
   - the launcher L6 note.
   - Keep every rule that is still useful (Derrick: no overcorrecting, lose nothing useful).
6. **I9 (part), subagent model per pane,** so subagents don't evict Forge's model. Do NOT upgrade pi-subagents; that needs Derrick's yes.
7. **I11.** Add a per-run worktree and a lease-line convention for future agy runs to the launcher template, as a note plus a template. Don't change how this run was launched.
8. **I12, evo's Gitea token.** Check whether evo holds a Gitea token. If it does, move it into the one locked owner-only X3 key file (/etc/evo-x3, owner-only), point its readers at that file, and verify they still work before deleting the old copy. Never print the value.

## NOT approved (don't touch)
- B1 (agy rights), B2 (Forge trifecta and auto-approve), I1, I4, I5 (decisions D1-D5).
- I6 and I7 memory and load tests: these run after the writer tests.
- I10, archiving the AlienPc Forge stack.

## HARD RULES
- Back up every file before editing it as `<file>.bak-20261116-u53` in that folder's _archive/.
- Commit by explicit path. No `git add -A`. No force push.
- Don't run H3 renders, queue-remote.sh, run_queue.py --queue or --yes-derrick. Don't touch AlienPc.
- Don't restart or edit llama-swap.
- Don't restart render-pi or the Render pane, and never type into a herdr pane.
- Restart Forge's pane only if an item needs it, and say so in RESULT.
- No secrets in output, logs, argv, chats or commits.
- Don't read PixlStash library contents, Sydney chats, persona or memory.
- Don't touch the Windows partitions, X3BACKUP, the BIOS or the tagger service.

## STOP CONDITION
Write /home/derekboone/evo-x3/records/U53-RESULT.md with:
- per item: DONE, BLOCKED (with the reason) or SKIPPED;
- files changed with their backup paths;
- commits;
- push result;
- the fresh-clone dry-start output;
- the smoke-loop output;
- pytest totals for tests/ and parody/.

Then stop.
