# U43 brief: merge community conflicts (U40/U41 + P1b/U36/U37), test, and push

Written Mon Nov 16 2026, late morning CT, by Max for Antigravity (Gemini 4 Hydrogen High) on the X3.

## Approval (already granted — do the work)

Derrick, widget t1949s7187: "Yes, have Antigravity merge the community conflicts, test, and push."

This is a merge, test, and normal push of `/home/evo/AI/community`. It is not a rebase and not a force push.

## When to start

Start now. U41 is finished and verified (`a4f58a7`, RESULT `/home/derekboone/evo-x3/records/U41-RESULT.md`, 574 passed / 5 skipped in `scripts/parody`, guide-mode byte-identical to the U41 backup).

U42 PixlStash tagging may still be running under a separate agy / tagging process. **Do not touch it.** Do not stop it, do not read library images, do not write into `/home/evo/AI/5slock/`, do not edit llama-swap, and do not take the GPU lease. This job only touches the community git tree, tests, and the U43 records files.

## Source of truth

Work **only** in the evo community repo, as user `evo`:

- Repo: `/home/evo/AI/community`
- Branch: `x3-linux` (tracks `gitea/x3-community`)
- Local HEAD should be `a4f58a7` (U41), parent `0530815` (U40).
- Remote tip at brief time: `gitea/x3-community` = `4f17934`.
- Do **not** use `/home/derekboone/AI/community` as a substitute (different HEAD).

You are launched as `derekboone`. `/home/evo/AI` is mode 700. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u43-step.sh`), then run:

```
sudo -n -iu evo bash /tmp/u43-step.sh
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
- Never `git add -A` in this repo. Stage named files only (the conflicted paths you resolved, by name).
- Never discard the pre-existing dirty work. Back it up with `git stash push -u -m pre-u43`, restore it at the end, and prove the file list and sha256 values match a snapshot taken beforehand.
- No renders, no queueing, no GPU, no lease. No `queue-remote.sh`, no `--wait` that submits, no ComfyUI `/prompt`. Unit tests and the dry byte-identical check only.
- Never view images. Never open PixlStash library contents, stills, or anything under `/home/evo/AI/5slock/` as pictures. Tests must use tiny synthetic images, not library stills.
- Never pass tokens or secrets on argv, and never print them.
- Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, llama-swap.yaml, Sydney private files, the original ComfyUI folder, or the U42 tagging runner / progress files.
- If a conflict is ambiguous (you cannot keep both sides' behavior without guessing), or tests cannot pass: `git merge --abort`, restore the stash, verify the snapshot, write the question in RESULT, and stop. Do not push a broken tree.

## Starting state (verified 11:33 AM CT)

`x3-linux` is **ahead 2, behind 6** versus `gitea/x3-community`. No merge or rebase is in progress. Stash list is empty.

Local-only commits (keep these):

- `0530815` U40: U37 pools/remote_idle/oral lint, PixlStash merged vault, overlap consistency, optional seam crossfade
- `a4f58a7` U41: still shape warning, `--aspect auto`, `--still-mode guide|ref` (default guide unchanged), and skill notes

Remote-only commits (keep these; tip `4f17934` carries P1b/U36/U37):

- `ac8b52b` X3 P1b: `run_queue.py --remote` via `scripts/remote_comfy.py` (uploads, POST `/prompt` over AlienPc Serve :8446, `/view` download, flock, systemd-run detach, upscale deferred; dry run lists uploads; tests)
- `7731a05` U36: make runtime script paths portable across derekboone and evo (derive from `__file__` / expanduser)
- `41cc2fa` U37 Step B: update shared render skills for X3 paths, remote queue recipe, GPU-lock wording, and lane scope
- `c605072` U37 Step B fix: remove agent-only `pi_qnap.py` marker from `h3-parody-identity` SKILL.md
- `8289c2f` U37 Step C: require `--still`, enforce absolute run paths, and make fps/aspect/throat/negatives hard lint failures
- `4f17934` U37 Step C/D fix: derive `submit_parody_run.py` `AI_ROOT` paths from `__file__` for evo portability

Expected conflicts (from the earlier rebase attempt, which was aborted with no push; the worktree was restored). Both sides modified:

- `scripts/parody/resolve.py`
- `scripts/parody/submit_parody_run.py`

Both sides added:

- `scripts/parody/test_u37_builder_fixes.py`
- `scripts/remote_comfy.py`
- `scripts/tests/test_remote_comfy.py`

Resolve every conflict that actually appears, including any extra files not listed here, by keeping both sides' behavior.

The worktree is dirty and must be preserved exactly:

- 37 modified files (linuxize / prior sync; listed by `git status` at 11:33 AM CT). None of these were in the U41 commit. Do not sweep-commit them.
- Untracked: `dummy_run/`

U41 backup used for the byte-identical check (must remain untouched):

- `/home/evo/AI/community/_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41`

## Work (do in this order)

### 0. Fetch, then snapshot the dirty tree

`git fetch gitea` as evo (so `gitea/x3-community` is current). If the remote tip has moved past `4f17934`, merge that newer tip the same way and record the new SHA in RESULT. Do not start the merge until the dirty tree is stashed.

Write a snapshot **before** stashing, as derekboone, to:

- `/home/derekboone/evo-x3/records/U43-pre-stash-list.txt` — relative paths of every dirty and untracked file (`git status --porcelain` plus a recursive file list of `dummy_run/`).
- `/home/derekboone/evo-x3/records/U43-pre-stash-sha256.txt` — `sha256sum` of every one of those files, sorted by path.

Take the hashes from the evo worktree (script as evo, write the two records files into derekboone's records dir, mode 644, owned by derekboone if you can). Do not include `.git/` or unrelated trees.

Then, as evo, in `/home/evo/AI/community`:

```
git stash push -u -m pre-u43
```

Confirm the worktree is clean (`git status --porcelain` empty) and `git stash list` shows `pre-u43`. If the stash command fails or would drop files, stop and write the question in RESULT. Do not continue with a dirty or partially-stashed tree.

### 1. Merge (not rebase)

```
git merge gitea/x3-community
```

Use a clear merge message if you have to set one, for example: `Merge gitea/x3-community (P1b/U36/U37) into x3-linux (U40/U41); keep both sides`. Do not complete `git commit` for the merge until step 3 tests pass (while `MERGE_HEAD` still exists you can still `git merge --abort`).

### 2. Resolve every conflict by keeping both sides

Goal: the U37 / P1b / U36 remote fixes **and** the U40 / U41 local fixes all remain, working together.

Keep from the remote (P1b / U36 / U37), including but not limited to:

- `remote_idle` / `/system_stats`, `/queue` behavior
- `APPROVED_IMAGE_POOLS` and the rest of the U37 remote builder / lint / path fixes
- `scripts/remote_comfy.py` remote-queue client (uploads, POST `/prompt`, `/view` download, flock, systemd-run detach, dry-run upload listing, tests)
- `submit_parody_run.py` `AI_ROOT` derived from `__file__` (evo portability), required `--still`, absolute run paths, hard lint failures for fps/aspect/throat/negatives
- Skill wording from U37 Step B (X3 paths, remote queue recipe, GPU-lock, lane scope) and the Step B fix that removed the agent-only `pi_qnap.py` marker from `h3-parody-identity`

Keep from local U40 / U41, including but not limited to:

- Shape check (warn only, never block), `--aspect auto`, `--still-mode guide|ref` with default `guide` **byte-identical** to the U41 backup builder
- Writer-run / pipeline pass-through of those flags
- Vault path `5slock/libraries/vault.db` (U40 PixlStash merged vault; do not revert to `approved_characters/vault.db`)
- U40 overlap / seam / oral-lint / pools work that landed in `0530815`
- U41 skill notes on crop vs `--aspect auto` / `--still-mode ref` in `skills/h3-parody-identity/SKILL.md` and `skills/h3-prompting/SKILL.md`

For the both-added test files (`scripts/parody/test_u37_builder_fixes.py`, `scripts/tests/test_remote_comfy.py`, and any other both-added test file), **merge the tests** so the file covers both sides. Do not keep only one side's tests. Do not delete a test just because the other side lacks it.

For `scripts/remote_comfy.py`, keep the remote P1b implementation and fold in any local additions rather than dropping either.

If two edits truly cannot coexist, stop: `git merge --abort`, restore the stash, write the question in RESULT. Do not invent a third behavior.

After resolving, `git add` only the conflicted paths by name. Never `git add -A`. Leave the pre-existing dirty files out of the index (they are in the stash).

### 3. Test (must pass before the merge commit, and before push)

From `/home/evo/AI/community` as evo:

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/tests
```

Everything must pass. `scripts/parody` must have **at least 574 passed**, plus whatever the remote side's tests add. Record the exact counts for both directories (passed / skipped / failed).

Rerun the U41 byte-identical check described in `/home/derekboone/evo-x3/records/U41-RESULT.md` section 4, against `_archive/u41-20261116/scripts/parody/build_request.py.bak-20261116-u41`. Default / `guide` mode must still be **byte-identical** for both:

- `build_parody_request` (U41: True, 6727 bytes)
- `build_writer_request` (U41: True, 8920 bytes)

Both must be True after the merge. If either is not, `git merge --abort`, restore the stash, and write the question in RESULT. Do not "fix" the default guide graph to make the merge easier unless both sides already required that change and you can show it; the default guide graph is locked.

Use synthetic images only. No library stills. No queue. No render.

### 4. Commit the merge, then push (no force)

Only if step 3 passed and no conflict was left ambiguous:

- Complete the merge with `git commit` (named, already-staged resolved files only; no `git add -A`, no extra dirty files).
- Then: `git push gitea HEAD:x3-community`
- **NO force.** No `--force`, no `--force-with-lease`, no `+HEAD:x3-community`.

Record the merge SHA and the remote tip after the push (`git rev-parse HEAD` and `git rev-parse gitea/x3-community`, plus `git status -sb`).

If the push is rejected, do not force, do not rebase, do not reset. Restore the stash if the worktree is clean enough to do so safely, and write the rejection in RESULT.

### 5. Restore the stash and verify it is intact

```
git stash pop
```

(or `git stash apply` then drop only after the hash check passes). If pop conflicts with the merge result, do not discard either side: leave the stash, write the question in RESULT, and stop.

Then verify against the step-0 snapshot:

- The set of dirty / untracked paths matches `U43-pre-stash-list.txt` (the merge commit's own files should be committed and therefore not dirty; the 37 pre-existing modified files plus `dummy_run/` must be back).
- `sha256sum` of those restored files matches `U43-pre-stash-sha256.txt` exactly.

If the hashes do not match, stop and report. Never `checkout --` or otherwise throw away the restored files to "clean up."

## STOP CONDITION

Write `/home/derekboone/evo-x3/records/U43-RESULT.md` (as derekboone) and stop. Include:

- The resolution for **each** conflicted file (what you kept from each side, in enough detail that Max can audit it).
- Test counts for `scripts/parody` and `scripts/tests` (passed / skipped / failed).
- The byte-identical result for both the parody and writer builds (True/False, and byte sizes).
- The merge SHA, the pushed remote tip (or the exact push rejection), and `git status -sb` after the push.
- Whether the stash was restored intact (list + sha256 match: yes/no), and the snapshot file paths.
- Confirmation of no render, no queue, no image viewing, no force push, and no `git add -A`.

If you aborted: say so clearly, confirm the stash is restored and hashes match, and write the blocking question. Then stop. Do not start another approach.
