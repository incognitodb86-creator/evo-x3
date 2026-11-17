# U40 brief: one code-fix batch (U37 decisions 2–4, PixlStash repoint, extend-seam fixes)

Written Mon Nov 16 2026, late morning CT, by Grok Bot (Max executor) for Antigravity (Gemini 4 Hydrogen High) on the X3.
Updated 10:31 AM CT with Prompt maker's beat-file handoff (section C).

## Approval (already granted — do the work)

- U37 decisions 2–4: card t1919s7071, "Yes, apply Antigravity's three code fixes after the OC test".
- PixlStash / OC / parody repoint: t1924u and t1927u. Derrick: update the parody script to the merged database; ensure the OC scripts and related lookups point at PixlStash.
- Fold in Prompt maker's extend-seam fixes: t1929u, and Prompt maker's message citing Derrick t288u ("he should fold in your fixes to what he is doing"). Prompt maker's 10:31 AM CT beat-file update is in scope (copy + hash repin + finish the 39f cut-shift). Do not edit beat prompt text.
- Do **not** queue or render. Derrick stopped the OC test to get setup right first. The extend rerender still waits on his yes. Dry runs only.

Read first, in this order:

1. This brief.
2. `/home/derekboone/evo-x3/records/U37-RESULT.md` — section "Decisions Derrick Needs", items 2–4 (recommended: Yes). Those are now approved.
3. `/home/derekboone/evo-x3/records/extend-seam-fixes-2026-11-16.md` — Prompt maker's research (copied from the box).
4. `/home/derekboone/evo-x3/records/extend-test-3beat-20261115/` — updated pack (copied from the box 10:31 AM CT). Includes `PLAN.md` (new `end_action` lines), `beat1.txt`–`beat3.txt`, `beats_data.py`, `build_extend.py`, `lint_report.json`. Pre-seamfix originals are under `_archive/pre-seamfix-20261116/`. Lint is clean; visible length is still 566f.
5. `/home/derekboone/evo-x3/records/voice-cap-followup/PROMPT.md` — the follow-up PROMPT whose pack hashes must be repinned.

## Source of truth (this is the important one)

Work **only** in the evo repos, as user `evo`:

- `/home/evo/AI/render` — branch `x3-linux`, HEAD `6a49943` ("Sync AlienPc master (render) into x3-linux for consolidation P0"), **12 dirty files** (listed below).
- `/home/evo/AI/community` — branch `x3-linux`, HEAD `d153a17` ("X3: linuxize paths…"). There are many already-dirty files here (about 50). Do **not** sweep-commit them.

You are launched as `derekboone`. `/home/evo/AI` is mode 700, so you cannot traverse it as derekboone. For every read or write under `/home/evo/**`, write a script file (for example `/tmp/u40-step.sh`), then run:

```
sudo -n -iu evo bash /tmp/u40-step.sh
```

Do not use nested quoting one-liners. Do not edit `/home/derekboone/AI/render` or `/home/derekboone/AI/community` as a substitute (those clones are at different HEADs and are not this batch's trees).

Python for tests: `/home/evo/AI/render/x3/.venv/bin/python`.

## HARD RULES

- Back up each file before editing: `*.bak-20261116` next to the file, or copy to `_archive/`. Never delete; archive.
- No renders and no queueing. No `queue-remote.sh`, no `--wait` that submits, no ComfyUI submit. Dry builds and unit tests only.
- Never view images. Never open PixlStash library contents, stills, or anything under `/home/evo/AI/5slock/` as pictures. Do not dump `vault.db` rows that contain image data. You may `stat` the vault file to see whether it exists, and grep **code** (not the vault) for paths.
- Do not touch the live PixlStash copy job. Do not write into `/home/evo/AI/5slock/`. Do not create or rotate API tokens (another job owns install + token).
- Never pass tokens, passwords, or `LLAMA_SWAP_KEY` on argv, and never print them. If you need the PixlStash read token, read it from a file under `/home/evo/.config/pixlstash/` inside an evo script and keep it in the process environment; do not echo it, do not write it into logs, RESULT, commit messages, or the brief.
- No `git add -A` in community. Stage named files only in both repos. Clear commit messages.
- Do **not** edit Prompt maker's beat prompt text (`beat1.txt`, `beat2.txt`, `beat3.txt`, and do not rewrite the scene wording in `beats_data.py`). Copy the updated files into place after a backup; leave their bytes unchanged.
- Do **not** implement ComfyUI native masked continuation (PR 15375 / Herrgott masked AV). That is a proposal only and needs a later Derrick yes.
- Do not touch Windows partitions, USB X3BACKUP, BIOS, LUKS, Tailscale, llama-swap.yaml, Sydney private files, or the original ComfyUI folder. No plugin installs. No new SSH keys or ACLs.
- If the merged PixlStash vault or the read token is not ready yet, tests that need them must **skip cleanly** (pytest skip, not fail). State that clearly in RESULT.

## The 12 dirty render files (review, then commit if legitimate)

Uncommitted on `/home/evo/AI/render` at HEAD `6a49943`:

- `.pi/agent/pi-permissions.jsonc`
- `.pi/extensions/loop-guard-test.mjs`
- `.pi/settings.json`
- `AGENTS.md`
- `RUN_ME.md`
- `writer_pipeline/acceptance/t3_plan.py`
- `writer_pipeline/acceptance/wp_accept.py`
- `writer_pipeline/config.yaml`
- `writer_pipeline/dialogue_blacklist.jsonl`
- `x3/README-X3.md`
- `x3/linuxize.py`
- `x3/queue-remote.sh`

Review the diff as user evo. If they are legitimate consolidation / linuxize / U37-sync edits, commit them in scoped, clear-message commit(s) **before or with** your new render-side edits, not mixed with unrelated leftovers. If any file is not legitimate, leave it unstaged and say so in RESULT. Do not commit secrets or machine-local junk.

Community already has a large dirty tree (linuxize / prior sync). Leave those files alone unless a change in this batch actually touches them. Commit only the files you change (or that are required for the change), by name.

## Work, in this order

### A. U37 decisions 2–4

See `U37-RESULT.md` for the findings. Implement all three:

1. Add `render/stills/approved_characters` (X3 path: `/home/evo/AI/render/stills/approved_characters`, also accept `~/AI/render/stills/approved_characters`) to `resolve.py` `APPROVED_IMAGE_POOLS`. Today it only includes `~/AI/5slock/approved_characters` (empty / wrong on X3) and a Windows NAS UNC path, so CLI `--image .../POOL/...` rejects local X3 approved stills unless `image_pools` is passed in Python.
2. In `remote_comfy.py` `remote_idle()`, check `GET /system_stats` **before** `GET /queue`. `/system_stats` is already in AlienPc llama-swap `ignorePaths` (409 when ComfyUI is unloaded, 200 when loaded). On 409, treat as idle and do **not** touch `/queue`. Only query `/queue` when `/system_stats` returns 200.
3. Extend `wp_lint` `MOUTH_CONTACT_RE` and `oral_contact` so they match the phrase `"enters her mouth"` (U37 Ask 3 `cand_3` slipped through with `"enters her mouth ... deep in her"` plus a post-entry `(S1)` line). Add or extend a test.

### B. PixlStash repoint (merged vault only)

Canonical vault, and the only one the code may use:

`/home/evo/AI/5slock/libraries/vault.db`

Do this:

1. In `scripts/parody/submit_parody_run.py`, `_PIXLSTASH_VAULTS` (about line 730) must point only at that merged vault. Drop the `approved_characters` vault entirely (the Nov 13 merge already moved the unique pictures into the main library; the old DB must not be copied or read).
2. Grep **both** repos for: `vault.db`, `approved_characters`, `5slock`, `PixlStash`, `pixlstash`, `FCSydny`, `poolclub`. Every OC, parody, or stills lookup (including FCSydny, poolclub, celeb stills) must use the merged vault, not old folders and not the old Approved characters database.
3. Where the code already supports the PixlStash HTTP API, use it on localhost with the **read** token from a file under `/home/evo/.config/pixlstash/` (read from file; never argv or logs). If that config dir or token file does not exist yet, do not create a token; keep the code wired for the path and skip API-backed tests cleanly.
4. Keep the POOL folder fallback where it already exists (decision A.1 stills path is a pool fallback, not a second vault).
5. The vault file may already be appearing on disk while another job is still copying it, and the token may not be present. Existence of `vault.db` is not proof the library is complete. Tests that need a ready vault or token must skip cleanly. RESULT must say whether the vault file and the token file were present, without printing the token.

### C. Prompt maker extend-seam fixes (code only; 10:31 AM CT pack update)

Research: `/home/derekboone/evo-x3/records/extend-seam-fixes-2026-11-16.md`.

Updated pack (box source `/workspace/maxops/prompts/extend-test-3beat-20261115/`, already copied to the records path above): lint is clean, still 566 visible frames. Old versions are in the pack's `_archive/pre-seamfix-20261116/`. Prompt maker owns beat prompt text; you do not edit it.

**C0. Place the updated pack, then repin hashes.**

- Find where the extend-test-3beat run on the X3 reads its beat files / PLAN / builder inputs (search the evo repos and existing run dirs). Back up any existing copies to `_archive/` or `*.bak-20261116`. Copy the updated files from `/home/derekboone/evo-x3/records/extend-test-3beat-20261115/` into that location. If no on-X3 run directory exists yet, keep the records copy as the input to the dry build and say so in RESULT. Confirm the copied `beat1.txt`–`beat3.txt` bytes and sha256 match the hashes below. Do not edit beat prompt text.
- Repin the voice-cap-followup `PROMPT.md` hashes. Working copy: `/home/derekboone/evo-x3/records/voice-cap-followup/PROMPT.md`. If another copy exists in a repo or handoff dir on the X3, update that too after a backup. Replace `808424141FE88045` / `7115D0AE1CFBFA53` / `ED7BC54BD52A366E` with these full sha256 values (computed on the box 10:31 AM CT from the updated files; re-check on the copies you place):

  - beat1.txt: `5d507f9a774c12dd0bc40f9fbfa87514f7dcc16d6eb910ab407604cad125bd93`
  - beat2.txt: `e893d29c03bfc0f9d38ab085afb3588271c73a03ff91da572e0201b45a85ea1f`
  - beat3.txt: `f306fd34c09966f8558f9cdb371558c0ce7152d1815e37ebebd2f4b7ce637d7c`

**C1. Trimmed voice RefMod on continuation beats 2 and 3.** Community commit `3dd04d1` is "parody: voice RefMod on every latent-tail beat again (Multishot tail-audio merge fix)". Confirm the current evo community tree actually applies that trimmed ≤23 s voice RefMod on latent-tail / continuation beats (beats 2 and 3 of the 3-beat extend test). If a later edit or dirty file turned voice back off on tail beats, restore the `3dd04d1` behavior. Do not queue a render.

**C2. One overlap value everywhere, including shot-clock math — finish the 39f builder cut-shift.** The 8ee347e / extend-test bug: beat 2 clocks were authored for a 22f overlap, but a 39f overlap was applied (exactly 17f early cuts; Shot 1 visible trimmed to 1.625 s). Commit `12d0733` applies overlap 39 on beat 2 (window 226f, start f153) and 22 on beat 3. The same applied overlap must drive carry, trim, assembly, **and** shot-clock rebasing. Rebase rule (from PLAN.md and the follow-up PROMPT): `local = authored + (applied - 22)`. For beat 2 that means window-local cuts at **00:03.958** and **00:06.958** (95/24 and 167/24), global f248 / f320. Write **window-local** clocks into the assembled continuation-window prompt, not global times. Beat 3 at overlap 22 is already fine (no-op rebase; window-local 00:03.500 / 00:05.750, global f441 / f495). Shot 1 must not be trimmed to 1.625 s. The dry build **must** show beat 2 cut times 00:03.958 / 00:06.958. Add or finish the test coverage for this rebase. Do not edit pack beat files to fake the clocks; the builder does the shift.

**C3. Optional short audio crossfade over the overlap at each seam, with a loudness trace.** Follow the TimelineDirector pattern in the research (half-cosine Soft AV release over the last ticks of the carried overlap, or a short ~15 ms audio de-click at stitch). Visual crossfade is not required (visual seams were already clean). Trace loudness across the overlap/seam in the dry-run or unit test output (numbers in RESULT; do not invent a render). Make the crossfade optional (flag or setting, default documented).

**C4. Use PLAN.md `end_action` lines** for the builder's `beat_closer` / `--end-action`. They are already in `/home/derekboone/evo-x3/records/extend-test-3beat-20261115/PLAN.md`. Do not invent new wording and do not edit beat prompt text.

**C5. Out of scope:** do **not** implement native masked continuation (PR 15375). Mention it in RESULT as explicitly skipped.

Then: a **dry build** of the extend-test-3beat run that shows the overlap math is consistent (one overlap value in carry, trim, assembly, and shot clocks) and that prints beat 2 window-local cut times 00:03.958 / 00:06.958, with Shot 1 not 1.625 s, and beat 3 unchanged at 22f. Do not queue. If you have to construct the run dir from the records pack, say what you used.

## Tests

From `/home/evo/AI/community`, as evo:

```
/home/evo/AI/render/x3/.venv/bin/python -m pytest -q scripts/parody
```

Baseline known from U37: `555 passed, 6 skipped`. Keep existing passes passing. Record before/after counts. New skips for a not-yet-ready vault/token are OK if they are explicit pytest skips and called out in RESULT.

Also run the render repo tests, ignoring `_archive/` and `bakeoff/` (use the repo's existing pytest layout; do not invent a huge extra suite).

Dry-build the extend-test-3beat run as above and include the overlap numbers and cut times in RESULT.

## Commits and push

- Scoped, named files only. No `git add -A` in community.
- Include the 12 dirty render files once reviewed as legitimate.
- The updated beat pack may be copied into a run dir; do not commit beat prompt text changes you did not author, and do not rewrite those files. Hash-repin of `PROMPT.md` and builder/code/tests are in scope to commit where they live in a repo. The records copies of the pack and follow-up PROMPT can stay uncommitted in `records/` (or commit only if that tree is already a repo — it is not; leave records files as files).
- Clear messages that say what changed (U37 pools / remote_idle / mouth lint; PixlStash merged-vault repoint; one overlap + 39f cut-shift + voice-on-tail + optional seam crossfade; hash repin).
- After tests pass, push to the existing Gitea remotes (`gitea/x3-render`, `gitea/x3-community`) as backup. If push is blocked, commit locally and say so. Run gitleaks or the repo's usual secret scan if it is already set up; never commit tokens.

## STOP CONDITION

Write `/home/derekboone/evo-x3/records/U40-RESULT.md` (you can write it as derekboone) and stop. Include:

- What changed, in which files, and the commit hashes.
- Review outcome for the 12 dirty render files.
- Pytest counts (community `scripts/parody` and render tests), including any clean skips.
- Dry-build overlap math (the one value, and that clocks/carry/trim/assembly agree) and the beat 2 cut times (must be 00:03.958 / 00:06.958; Shot 1 not 1.625 s; beat 3 at 22f unchanged).
- Confirmation that placed `beat1.txt`–`beat3.txt` match the sha256 values in C0, and that voice-cap-followup `PROMPT.md` was repinned. No beat prompt text edits.
- Whether `/home/evo/AI/5slock/libraries/vault.db` and `/home/evo/.config/pixlstash/` were present, and that vault-dependent tests skipped if not ready. No token values.
- Confirmation: no render queued; PR 15375 not implemented; `end_action` lines taken from PLAN.md.
- Anything blocked or left for Derrick.

Then stop. Do not start a second batch, do not queue, do not wait for a render yes.
