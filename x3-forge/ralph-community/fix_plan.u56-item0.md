# U56 Ralph Plan — Item 0 Atomic Baseline (Merge Into Your Live fix_plan.md Above Item 1)

> Use this only if you want the headless pass to make the Item 0 edits itself. If you ran
> `bash apply-on-x3.sh evo --with-tests`, Item 0 is already done in the live tree: tick it instead of running it.
> Keep the Render/Forge panes idle during the pass: live `flash-next-uncensored` has `concurrencyLimit: 1` until
> root-apply raises it, so any concurrent pane request makes llama-swap return HTTP 429 to one of them.

**Rules for every pass:**
- Current working directory is `$RALPH_WORKTREE` (the `community` loop worktree). Render's loop worktree is `$RALPH_FORGE_WORKTREE`.
- All required specs for Item 0 are inline below. Never search outside the worktrees, never read `.env` files, and NEVER delete any files or `_archive/` folders.
- Complete strictly **one** `- [ ]` item per pass, verify its pytest command passes, **`git commit` touched files by explicit path inside `$RALPH_WORKTREE`** (never `git add -A`), tick `- [x]` in `/home/evo/AI/forge/ralph-community/fix_plan.md`, and stop immediately.

---

- [ ] **0. Sync the 2 stale checkpoint tests in `$RALPH_WORKTREE` (`community`) and harden the `AGENTS.md` worktree lookup (atomic single pass so the full pytest backpressure gate passes):**
  1. **Part A (`scripts/parody/render-master-rules-20261113.json`, rule `R28` near line 451):**
     - Keep `checks[0]` (`"2.3 cuts of the same beat"`) unchanged.
     - Change `checks[1]` from `"neither is forced"` to `"One continuous \\[Shot 1\\] is the default"` (**must escape `\\[Shot 1\\]`** because `check_writer_prompt_rules.py` compiles `checks` with `re.search`, where unescaped `[Shot 1]` is a regex character class that fails!).
     - Update `"restore_text"` to the exact line-60 text of `/home/evo/AI/render/AGENTS.md`:
       `"- One continuous [Shot 1] is the default. Use 2-3 cuts of the same beat only when the run passes --shots multi or the ask asks for coverage: [Shot 1] has no timestamp, later cuts are \"[Shot N] At MM:SS.mmm, the camera cuts to ...\". Talk, flirt and tease clips stay one shot. On an act clip, [Shot 1] names the act word. A held shot or slow pull-out stays as written."`
  2. **Part B (`scripts/parody/test_writer_pipeline.py`, `test_talk_rules` near line 138):**
     - Because `wp_lint.py` `MODE_RULES["talk"]["min_lines"]` changed from `3` to `2`, fixture `two` (which only stripped the teasing `S1` line, leaving 2 lines) no longer triggers `talk_lines`.
     - Update `two` so it strips **both** `" (S1) says in a teasing voice, <d>[English] Then arrest me, Detective.</d>"` **and** `" (S2) says in a clipped voice, <d>[English] Your bodysuit left a wet trail.</d>"`, leaving 1 dialogue line. Keep the `assert "talk_lines" in ...` line unchanged.
  3. **Part C (`scripts/parody/test_modular_s3_and_writer_sys.py`, `test_contact_regex_and_prompt_compiler_77_rules` near line 499):**
     - Replace the hardcoded `Path(r"/home/evo/AI/render/AGENTS.md")` read with: use `Path(os.environ["RALPH_FORGE_WORKTREE"]) / "AGENTS.md"` when that env var is set and the file exists, else `/home/evo/AI/render/AGENTS.md`, else the sibling `render/AGENTS.md` three levels up from the test file. Add `import os` inside the test. This makes worktree passes validate against the Render worktree they run beside.
  4. **Pass / Done when:**
     - From `$RALPH_WORKTREE/scripts`, run:
       `PYTHONDONTWRITEBYTECODE=1 uv run --no-project --with pytest --with pyyaml --with pillow --with numpy --with pysbd --with opencv-python-headless python -m pytest -q -p no:cacheprovider parody/test_modular_s3_and_writer_sys.py::test_contact_regex_and_prompt_compiler_77_rules parody/test_writer_pipeline.py::test_talk_rules`
       and confirm **`2 passed`**.
     - Commit by explicit path inside `$RALPH_WORKTREE`:
       `git -C "$RALPH_WORKTREE" add scripts/parody/render-master-rules-20261113.json scripts/parody/test_writer_pipeline.py scripts/parody/test_modular_s3_and_writer_sys.py && git -C "$RALPH_WORKTREE" commit -m "u56 item 0: sync R28 regex check, talk_lines fixture, and worktree AGENTS path"`
     - Tick `- [x] **0.` in `/home/evo/AI/forge/ralph-community/fix_plan.md`, append one line to `/home/evo/AI/forge/ralph-community/notes/progress.md`, and stop immediately.
