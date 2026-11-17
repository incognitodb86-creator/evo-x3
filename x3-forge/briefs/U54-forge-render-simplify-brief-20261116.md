# U54 (Forge, after U53 is verified): Render pipeline routing + simplify, Nov 16 2026

Derrick t2118u/t2119u/t2121u/t2126u. Forge does this, not agy. Back up as .bak-20261116-u54, scoped commits, end-to-end test per clip type.

## Approved fixes
1. **One path for named people.** Any ask that names a character or celeb (or uses --character) goes through the parody identity step: character and actor names in the prompt, INDEX pairing and the matching RefMod. Spoof is only a tone overlay and talk only a clip type on top of it. Asks with no names stay on the plain writer. Cause: the Cassie run (runs/cassie_party_parody) routed as talk+spoof, so it had no names and only the oc_poolclub RefMod, and it dropped 2 of 4 lines.
2. **The ask beats the still** for setting, wardrobe and lines when they clash. Fix render AGENTS.md L7 ("the still is a locked setup... never contradict") and L42 ("Still nouns win"); keep the still for face, body, light and framing. Also stop the writer from dropping the ask's quoted dialogue.
3. **PixlStash search in Render AGENTS.md.** Pictures are found by `character_id` (FCSydny = 1), not by tag text; file_path is relative to /home/evo/AI/5slock/libraries/. Remove L14's stale "stills/approved_characters/POOL" wording (Derrick: no pools or folders; 18+ is the only check). Verified 4:29 PM: character_id=1 returns paths that exist.
4. **End-to-end tests:** a named talk clip and a named spoof clip, run through the real pipeline (dry, no queue). Each must fail if the names, the RefMod or any ask line is missing.

## Simplification cuts (Derrick t2135s7748: "cuts 1-5, 7-9 and 11, hold 6 and 10")
Full evidence (file:line) for each item: render-overengineering-review-20261116.md, in this folder. Do these items:
1. Set the default n_candidates to 1 and drop the judge. Keep a flag for A/B tests.
2. Talk clips (and runs that already pass --frames) use the in-code minimal beat card, with no LLM planning call.
3. Shrink wp_lint.py to the checks that are actually used. The 18+ hard stop (youth_hint/scale_adult/_MINOR_RE) stays exactly as it is. Remove the dead block_ready config.
4. Keep one writer command and retire the leftover classic parody CLI. Move or keep any tests that still need it.
5. render-pi.sh loads only h3-prompting and h3-parody-identity. The Ref2VA and hardcore skills are pulled in only when the ask needs them. Keep one craft source.
7. Fix stale docs and config: Windows paths, the still pool, and "no vault on X3".
8. Stop writing per-run files that nothing reads after queueing.
9. Merge acts, modes and overlays into one classification, together with fix 1 above.
11. Remove the frozen A/B sampler and persona arms.

Do NOT touch item 6 (the build_request.py split, repair loop and second linter) or item 10 (the 77-rule compile gate).

## Rules
- Back up every file as *.bak-20261116-u54 in _archive/.
- Commit by path only, one commit per item. No `git add -A`, no force push.
- Run the full `pytest -q tests` and `pytest -q parody` suites; they must stay green with no xfail.
- Run a dry end-to-end guide+ref check (no queue) on a named talk ask and a named spoof ask. Each must show the names, the right RefMod and every ask line.
- No renders, no queueing, no llama-swap edits.
- Don't restart Render's pane; Max restarts it after verifying.
- No secrets on argv or in output. Don't read PixlStash contents or Sydney's chats, persona or memory.

When done, write U54-RESULT.md next to this brief, then stop. It should list per item DONE, BLOCKED or SKIPPED, the files and backups, the commits, the pytest totals and the e2e output.
