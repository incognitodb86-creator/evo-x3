# U45 brief: commit linuxize path fixes, redo the community merge, test, and push if gates pass

Written Mon Nov 16 2026, around midday CT, by Max for Antigravity (Gemini 4 Hydrogen High) on the X3.

## Approval (already granted — do the work)

Derrick, widget t1951s7204: "Yes, commit the test path fixes, redo the merge, and push if tests pass."

This is a two-step git job in `/home/evo/AI/community`: (1) commit the 11 linuxize test/helper path fixes on their own, then (2) merge `gitea/x3-community` using the already-proven U43 resolutions, test, and push normally if the gates pass. It is not a rebase and not a force push.

## Read this first

Read `/home/derekboone/evo-x3/records/U43-RESULT.md` in full before touching the repo. It records:

- The 6 conflict resolutions that already worked (section 2). Reuse those resolutions; do not invent a third behavior.
- Why the U43 tests failed (section 3): the 11 linuxize path fixes were still uncommitted and had been stashed, so committed files still hardcoded `/home/derekboone/AI/...`.
- The U41 byte-identical check that passed on the resolved tree (section 4): `build_parody_request` True / 6727 bytes, `build_writer_request` True / 8920 bytes.
- The two blocking questions (section 7). This brief is the approved answer to Q1 (commit the 11 path fixes first) and a narrowed answer to Q2 (`scripts/tests` must be no worse than a measured pre-merge baseline; known Windows-only failures are allowed; do not make `scripts/tests` a perfect-pass gate).

## When to start

Start now. U43 aborted cleanly: merge aborted, stash restored, hashes matched, nothing pushed. U44 tagging speed-up is finished. The PixlStash tagger (`u42-pixlstash-tagger` and its follow-on) may still be running. **Do not touch it.** Do not stop it, do not read library images, do not write into `/home/evo/AI/5slock/`, do not edit llama-swap, and do not take the GPU lease. This job only touches the community git tree, tests, and the U45 records files.

## Source of truth

Work **only** in the evo community repo, as user `evo`:

- Repo: `/home/evo/AI/community`
- Branch: `x3-linux` (tracks `gitea/x3-community`)
- Local HEAD at U43 close: `a4f58a7` (U41), parent `0530815` (U40). Confirm this, or record the actual SHA if it has moved, before you start.
- Remote tip at U43 close: `gitea/x3-community` = `4f17934`. Fetch first. If the remote tip has moved, merge that newer tip the same way and record the new SHA in RESULT.
- Do **not** use `/home/derekboone/AI/community` as a substitute (different HEAD).

You are launched as `derekboone`. `/home/evo/AI` is mode 700. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u45-step.sh`), then run:

```
sudo -n -iu evo bash /tmp/u45-step.sh
```

Git, specifically, must run as evo:

```
sudo -n -u evo -H git -C /home/evo/AI/community …
```

No nested quoting one-liners. Python: `/home/evo/AI/render/x3/.venv/bin/python`.

The remote is `gitea`. evo's credentials already work. Do not print credentials, tokens, or passwords. Do not edit git remotes or credential files.

## HARD RULES

- Merge, do not rebase. `git merge gitea/x3-community`. Each side's commits must stay intact.
- **No force push. No `--force`, no `+` refspec, no rebase of already-written commits, no `reset --hard` of published or dirty work.** If the push is rejected, leave the merge commit in place, restore the stash if it is safe, and write the question in RESULT.
- Never `git add -A` in this repo. Stage named files only, by explicit path.
- Never discard the remaining pre-existing dirty work. After step 1, snapshot it, stash it with `git stash push -u -m pre-u45`, restore it at the end, and prove the file list and sha256 values match the snapshot. The 11 committed files are expected to be gone from the dirty list.
- Do not push the step-1 commit alone. If the merge gates fail, keep that commit local, do not push, restore the stash, and write the question in RESULT.
- No renders, no queueing, no GPU, no lease. No `queue-remote.sh`, no `--wait` that submits, no ComfyUI `/prompt`. Unit tests and the dry byte-identical check only.
- Never view images. Never open PixlStash library contents, stills, or anything under `/home/evo/AI/5slock/` as pictures. Tests must use tiny synthetic images, not library stills.
- Never pass tokens or secrets on argv, and never print them.
- Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, llama-swap.yaml, Sydney private files, the original ComfyUI folder, or the running tagger service (`u42-pixlstash-tagger` or any follow-on tagging process / progress files).
- If a conflict is ambiguous (you cannot keep both sides' behavior without guessing), or the gates cannot pass: `git merge --abort`, keep the step-1 commit local, restore the stash, verify the snapshot, write the question in RESULT, and stop. Do not push a broken tree.

## The 11 files (U43-RESULT section 7 Q1)

Commit **only** these paths, staged by explicit path:

- `scripts/parody/test_longclip_baseline.py`
- `scripts/parody/test_longclip_beats.py`
- `scripts/parody/test_longclip_skill_routing.py`
- `scripts/parody/test_parody_phase1.py`
- `scripts/parody/test_parody_phase3.py`
- `scripts/parody/test_parody_stitch.py`
- `scripts/parody/test_t1109_writer_index_refmods.py`
- `scripts/parody/test_writer_finalize.py`
- `scripts/parody/test_writer_pipeline.py`
- `scripts/parody/writer_sys.py`
- `scripts/tests/test_run_queue_keep_comfy_process.py`

## Work (do in this order)

### 0. Fetch, then inspect starting state

`git fetch gitea` as evo. Confirm branch `x3-linux`, no merge or rebase in progress, and that the 11 files above are among the dirty paths (they were, after U43 restored the stash). If the tree is unexpectedly clean, or a merge is already in progress, stop and write the question in RESULT.

### 1. Commit only the 11 linuxize path fixes

Inspect the dirty diffs of those 11 files first. They currently exist as uncommitted linuxize edits (U43: committed copies still hardcoded `/home/derekboone/AI/...`).

Prefer making the paths `__file__`-derived and portable across `derekboone` and `evo`, the same way U36 did in already-committed files such as `scripts/parody/resolve.py` and `scripts/parody/submit_parody_run.py` (`Path(__file__).resolve()` / `expanduser()`, not a hardcoded `/home/derekboone/AI/...` or `/home/evo/AI/...`). If a file is already `__file__`-derived, leave that as-is and just commit it. Do not change test assertions or production behavior beyond the path fix.

Then, as evo, stage **only** those 11 paths by name. Never `git add -A`. Confirm `git diff --cached --name-only` is exactly those 11 paths and nothing else. Commit with this exact message:

```
X3: commit linuxize path fixes for parody tests
```

Record the step-1 commit SHA in RESULT. Do not push it.

### 2. Snapshot the remaining dirty work, then stash it

After the step-1 commit, the 11 files should be clean. Everything else that was dirty or untracked must be preserved.

Write a snapshot **before** stashing, as derekboone, to:

- `/home/derekboone/evo-x3/records/U45-pre-stash-list.txt` — relative paths of every remaining dirty and untracked file (`git status --porcelain` plus a recursive file list of `dummy_run/` if it is still untracked).
- `/home/derekboone/evo-x3/records/U45-pre-stash-sha256.txt` — `sha256sum` of every one of those files, sorted by path.

Take the hashes from the evo worktree (script as evo, write the two records files into derekboone's records dir, mode 644, owned by derekboone if you can). Do not include `.git/` or unrelated trees. The 11 committed files must not appear in this snapshot.

Then, as evo, in `/home/evo/AI/community`:

```
git stash push -u -m pre-u45
```

Confirm the worktree is clean (`git status --porcelain` empty) and `git stash list` shows `pre-u45`. If the stash command fails or would drop files, stop and write the question in RESULT. Do not continue with a dirty or partially-stashed tree.

### 2b. Measure the `scripts/tests` pre-merge baseline

On this clean pre-merge HEAD (step-1 commit present, remaining dirty work stashed), as evo from `/home/evo/AI/community`:

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/tests
```

Record the exact passed / skipped / failed / error / collection-error counts, and the full list of failing or uncollectable node ids, in RESULT and in `/home/derekboone/evo-x3/records/U45-tests-baseline.txt`. This is the baseline the merged tree must not be worse than. Known Windows-only failures already in this baseline are allowed to remain, including (from U43, confirm against what you actually measure):

- `scripts/tests/test_b2_lora_param.py` (`C:\AI\community` in `make_b2_request.py`)
- `scripts/tests/test_free_comfy_args.py` (`C:\AI\...` candidates only)
- `scripts/tests/test_phase1_still.py` (`C:\AI\community` in `make_bfs_request.py`)
- `scripts/tests/test_run_queue_one_at_a_time.py` (`C:\AI\community\community.log` in `scripts/comm.py`, and/or `free_comfy` remote no-op)

Do not start porting the rest of `scripts/tests` in this job. The approved work is the 11-file commit plus the merge.

### 3. Merge (not rebase), using the U43 resolutions

```
git merge gitea/x3-community
```

Use a clear merge message if you have to set one, for example: `Merge gitea/x3-community (P1b/U36/U37) into x3-linux (U40/U41 + path fixes); keep both sides`. Do not complete `git commit` for the merge until step 4 gates pass (while `MERGE_HEAD` still exists you can still `git merge --abort`).

Resolve every conflict that actually appears, including any extra files not listed in U43, by keeping both sides' behavior. The proven U43 resolutions (see U43-RESULT section 2) were:

1. `scripts/parody/resolve.py`: remote U36 `__file__`-derived `DEFAULT_APPROVED_STILLS_DIR`; local U40 `RENDER_APPROVED_STILLS_DIR`, `_HOME_RENDER_APPROVED_STILLS_DIR`, deduplicated 4-entry `APPROVED_IMAGE_POOLS`, and `expanduser()` in `validate_reference_images`.
2. `scripts/parody/submit_parody_run.py`: remote U36/U37 `__file__`-derived roots, absolute `--run-dir`, required `--still`; local U40/U41 merged PixlStash vault, `still_mode`, `--aspect auto`, shape warning, writer-run pass-through.
3. `scripts/parody/test_u37_builder_fixes.py`: merge the tests — remote U37 sections 1–3 and local U40 section 4.
4. `scripts/remote_comfy.py`: remote P1b implementation plus local U40 `remote_idle` (`/system_stats` before `/queue`).
5. `scripts/tests/test_remote_comfy.py`: merge the tests — remote P1b's 5 tests plus local U40 `test_remote_idle_checks_system_stats_before_queue`.
6. `skills/h3-parody-identity/SKILL.md`: remote U37 Step B wording and `pi_qnap.py` marker removal; local U40/U41 merged vault path and `--aspect auto` / `--still-mode ref` notes.

Auto-merged files in U43 (`build_request.py`, `render_writer_pipeline.py`, `wp_lint.py`, `skills/h3-prompting/SKILL.md`) already carried both sides; verify that is still true.

If two edits truly cannot coexist, stop: `git merge --abort`, keep the step-1 commit local, restore the stash, write the question in RESULT. Do not invent a third behavior.

After resolving, `git add` only the conflicted paths by name. Never `git add -A`. Leave the pre-existing remaining dirty files out of the index (they are in the stash).

### 4. Gates (must pass before the merge commit, and before push)

From `/home/evo/AI/community` as evo, use synthetic images only. No library stills. No queue. No render.

**Gate A — `scripts/parody`:**

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody
```

Must have **0 failures**, **0 collection errors**, and **passed >= 574**. Record the exact passed / skipped / failed / error counts.

**Gate B — `scripts/tests` no worse than the step-2b baseline:**

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/tests
```

Compare to the pre-merge baseline. Allow the known Windows-only failures that were already in the baseline. Do not allow new failures, new collection errors, or a higher failed/error count than the baseline. Record both sets of counts and the failing node ids.

If `test_remote_comfy.py` enabling remote mode in-process introduces **new** failures versus the baseline (U43 saw this pollute `test_run_queue_one_at_a_time.py::test_free_comfy_calls_api_free_when_loaded`), fix that isolation / pollution in the test or the enable/teardown path so the merged run is no worse than baseline. Do not "fix" it by deleting tests. If the same pollution was already in the baseline, you may still isolate it if that is a small, safe test-only change that does not worsen the baseline comparison, but it is required only when it introduces new failures.

**Gate C — U41 guide-mode byte-identical check must be True.**

Rerun the check described in `/home/derekboone/evo-x3/records/U41-RESULT.md` section 4, against `_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41`. Default / `guide` mode must still be **byte-identical** for both:

- `build_parody_request` (U41 / U43: True, 6727 bytes)
- `build_writer_request` (U41 / U43: True, 8920 bytes)

Both must be True after the merge. If either is not, `git merge --abort`, keep the step-1 commit local, restore the stash, and write the question in RESULT. Do not "fix" the default guide graph to make the merge easier unless both sides already required that change and you can show it; the default guide graph is locked.

### 5. Commit the merge and push — or abort

**If all gates pass:**

- Complete the merge with `git commit` (named, already-staged resolved files only; no `git add -A`, no extra dirty files).
- Then: `git push gitea HEAD:x3-community`
- **NO force.** No `--force`, no `--force-with-lease`, no `+HEAD:x3-community`.
- This push may include the step-1 commit together with the merge commit, which is intended. What is forbidden is pushing the step-1 commit by itself before the merge gates pass.

Record the step-1 SHA, the merge SHA, and the remote tip after the push (`git rev-parse HEAD` and `git rev-parse gitea/x3-community`, plus `git status -sb`).

If the push is rejected, do not force, do not rebase, do not reset. Restore the stash if the worktree is clean enough to do so safely, and write the rejection in RESULT.

**If any gate fails:**

- `git merge --abort`
- Keep the step-1 commit local. Do not push it.
- Restore the stash (step 6) and write the blocking question in RESULT.
- Stop. Do not start another approach.

### 6. Always restore the stash and verify it is intact

Whether the merge was committed or aborted:

```
git stash pop
```

(or `git stash apply` then drop only after the hash check passes). If pop conflicts with the merge result, do not discard either side: leave the stash, write the question in RESULT, and stop.

Then verify against the step-2 snapshot:

- The set of dirty / untracked paths matches `U45-pre-stash-list.txt` (the 11 committed files must not be dirty; they are minus'd from any earlier full dirty list).
- `sha256sum` of those restored files matches `U45-pre-stash-sha256.txt` exactly.

If the hashes do not match, stop and report. Never `checkout --` or otherwise throw away the restored files to "clean up."

## STOP CONDITION

Write `/home/derekboone/evo-x3/records/U45-RESULT.md` (as derekboone) and stop. Include:

- The step-1 commit SHA, and whether those 11 paths were left as-is or updated to `__file__`-derived before the commit.
- The resolution for **each** conflicted file (what you kept from each side, in enough detail that Max can audit it), or a note that you reused the U43 resolutions unchanged.
- Test counts for `scripts/parody` (passed / skipped / failed / errors / collection errors).
- Test counts for `scripts/tests`: the pre-merge baseline and the merged run, plus the failing node ids on each, and whether the merged run was no worse.
- The byte-identical result for both the parody and writer builds (True/False, and byte sizes).
- The merge SHA, the pushed remote tip (or a clear statement that nothing was pushed), and `git status -sb` after the final git action.
- Whether the stash was restored intact (list + sha256 match: yes/no), and the snapshot file paths.
- Confirmation of no render, no queue, no image viewing, no force push, no `git add -A`, no push of the step-1 commit alone, and no contact with the tagger or llama-swap.

If you aborted: say so clearly, confirm the step-1 commit is still local and unpushed, confirm the stash is restored and hashes match, and write the blocking question. Then stop.
