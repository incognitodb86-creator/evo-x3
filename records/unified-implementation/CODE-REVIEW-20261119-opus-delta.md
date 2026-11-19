VERDICT: APPROVE

Delta code review of mono 3a130d1..c0c9492 (13 fix commits), Claude Opus 5.5, 2026-11-19 CT. Read-only. Scope: my
findings 1-3, 6-15 and 20 from CODE-REVIEW-20261119-opus.md, plus anything new the fixes added. Scratch copy:
`C:\tmp\evo-work\cr-delta` (git archive of c0c9492 subtrees). Nothing ran on a host. No secrets read or printed.

All 14 findings in scope are fixed. The two BLOCKs (L3, L8) are now safe to apply. I found 6 new issues, all MINOR.
None of them blocks the apply. N1 should be fixed before `pi-job recompile` is used on a long_continuation run.

| # | Item | Result | file:line (c0c9492) | Note |
|---|---|---|---|---|
| 1 | L3 | FIXED | config/bin/evo-worktree-cleanup:26-46,62 | Skips a worktree if `status --porcelain` is non-empty, and also when status fails (`STATUS_ERROR`). Age is the newest of the last commit time and the newest file mtime. Saves `diff HEAD`. `--force` is gone. Still no timer unit in mono, so it only runs by hand (see N2). |
| 2 | L8 | FIXED (see N1, N3) | config/bin/pi-job:800-872 | Refuses unless the status is READY. Fails closed when `wp_lint.py` is missing. `fill_request` is no longer called, and the code writes `clip/request.api.json` directly. VERIFIED in scratch: `wp_lint` imports through `build_request`, which adds `scripts/` to sys.path, so `comm` resolves. `lint(text, {'kind':...})` passes on the u37 `GOOD_SEX` fixture, the same fixture with the `REF_MODE_PICTURE1_LEAD` prefix, and two beta7-converted fixtures. |
| 3 | H1c | FIXED | config/bin/pi-job:375-409 | Checks `/running` first and probes `/slots` only when `flash-next-uncensored-v2` is already loaded. Uses any slot count above 0. The model id matches config/llama-swap.yaml:50 (`main` group). Small race: see N4. Halogen `/slots` is still unverified here. |
| 6 | ST3 | FIXED (see N5) | config/bin/sync-renders:95-106 | Starts the import when `NEW>0` or when the inbox has any non-hidden file. The lock file `.import_inbox.lock` is hidden, so it doesn't trigger a start by itself. |
| 7 | ST3 | FIXED | hosts/x3/pixlstash-tagging/import_inbox.py:47-67,81-188; config/bin/pi-job:618-669 | Takes a non-blocking `flock` on `<inbox>/.import_inbox.lock` and releases it in `finally`. A run that finds the lock busy returns `stopped_reason=locked` and doesn't touch any files. `pi-job render --still` now uses the same detached `pixl-import` unit, with no inline 60 s timeout. |
| 8 | H5 | FIXED | config/bin/pi-job:460-479,503-512 | When the Makefile has a `^check-all\s*:` target, runs `timeout 600 make check-all` after pi. A non-zero rc (including timeout 124 and missing make 127) means STUCK plus an ntfy. Note: `timeout` only signals `make`, so its child processes can outlive the timeout. Low risk. |
| 9 | S2 | FIXED | alienpc/community/scripts/template_allowlist.py:40,313-363; scripts/allowlist_promoted.json | The manifest moved to `scripts/` and starts as `[]`. Names are refused if they contain `/`, `\`, `..` or NUL, or end in `.candidate`. Paths must resolve inside `templates/`. The sha256 must match. The old `templates/allowlist_promoted.json` path is no longer read. |
| 10 | S2 | FIXED | template_allowlist.py:86-105,292-307 | Each template has a node-id-to-key map. Unlisted keys must match exactly, and an unlisted `VAR_SENTINEL` is refused (fail closed). VERIFIED in scratch: for all 10 core templates, every key that was variable before is still allowed, and every mapped node id exists. The tests pass: `12 passed`. |
| 11 | L4 | FIXED (code); PARTIAL (data) | config/bin/pi-job:268-294 | Returns a URL only for the QNAP copy. The Render desk still has to write `--out <crun>/contact_sheet.jpg` (OPERATOR.md, render worker). Until it does, `sheet_url` stays `none`. |
| 12 | L6 | FIXED | config/bin/pi-job:506-510,517-520,530-533,550-553,604-607 | All 5 `_write_stuck_bundle` call sites are wrapped in `try/except`, so the ntfy that follows always runs. |
| 13 | H3 | FIXED | hosts/x3/systemd/user/evo-morning-status.service:10,29; evo-weekly-worktrees.service:19 | Uses https on :8447, globs `*/render_ok.json`, and adds `git --no-optional-locks status`. |
| 14 | H2 | FIXED | hosts/x3/hermes/config.yaml:39-41 | The comment now has the full deny list: 127/8, ::1, 100.64/10, 10/8, 172.16/12, 192.168/16, fc00::/7, 169.254/16, fe80::/10, 0/8 and ::/128. It still allows only 127.0.0.1:8888. No other lines changed. |
| 15 | L7 | FIXED | config/pi-evo/extensions/syntax-check.ts:12 | Uses `ast.parse`, which writes no `__pycache__`. The pi `tool_result` contract is still unverified here. |
| 20 | L1 | FIXED | config/bin/pi-job:591,869 | The Copy text is now `pi-job queue <id> <code>`. ntfy `copy` action support is still unverified here. |
| N1 | L8 | NEW (MINOR) | config/bin/pi-job:855-856 | recompile sets `c1.inputs.prompt` to the full edited prompt. `fill_request` (fill_request.py:111) gives c1 `continuation_prompt or final_prompt`. On a long_continuation run, recompile overwrites the continuation prompt. | 
| N2 | L3 | NEW (MINOR) | config/bin/evo-worktree-cleanup:57-63 | A clean worktree on a detached HEAD with commits that aren't on any branch passes the checks. Removing it deletes its HEAD reflog, so those commits can be garbage-collected. Plain `worktree remove` also deletes ignored files (build outputs, local `.env`). |
| N3 | L8 | NEW (MINOR) | config/bin/pi-job:837-842 | The lint context is only `{'kind': ...}`. The pipeline also passes `slots`, `blacklist`, `cloned` and `cfg`, so blacklist and slot checks are skipped on edited prompts. `kind` falls back to `sex` when `build_report.json` has no kind. The safety hard-stops (`SAFETY_HARD`) still run. |
| N4 | H1c | NEW (MINOR) | config/bin/pi-job:396-404 | Race between `/running` and `/upstream/.../slots`: if Gufo unloads between the two calls, the `/slots` probe loads it again. That needs a TTL unload inside about 2 s. Rare. |
| N5 | ST3 | NEW (MINOR) | config/bin/sync-renders:99 | Any non-hidden file in the inbox that `import_inbox.py` skips (its `EXT` filter, for example a sidecar `.json`/`.txt`) restarts a no-op `pixl-import` every 2 min, forever. It's harmless but noisy in the journal. |
| N6 | docs | NEW (MINOR) | reports/u58-pijob.md "Fix round" | The worker notes cite part-branch SHAs (c5df885, 708381a, 48afdd8, e0b343d, ...). The mono SHAs are 658dc18, 03340b1, a5a86ce, dbc7156, ... Max should cite the mono SHAs in RESULT files. |

Fixes (one line each):
- N1: Set `c1.inputs.prompt` only when it equals c0's old prompt. Otherwise leave it, or refuse recompile when `c1` exists.
- N2: Skip a worktree when `git -C "$wt" symbolic-ref -q HEAD` fails and `git branch --contains HEAD` is empty. Optionally skip when `git status --porcelain --ignored` is non-empty.
- N3: Read `lint_ctx` from `build_report.json` when it's there.
- N5: Use the same extension list in the `find` (or `-iname` for each `EXT`).

## Apply order for Max (replaces the old one)

1. **Safe now (docs and data, no live effect):** INV1, INV2, ST2, RV1 (user YAML), ST4/ST5/M4 candidates, R5 (X3 lease, no active render).
2. **Safe with the normal test step:** ST1, W3a, RV2, H4, the H5 files, H2 comment copy (14), L7 (15). Check L7 with a broken-file test on the box.
3. **ST3 pair:** `sync-renders` and `import_inbox.py` (6, 7) together. On the X3, run `bash -n` and trigger one sync. Then confirm two things: `pixl-import` keeps running after the sync exits, and a second run returns `locked`. Then L2 and the H3 units (13).
4. **pi-job last, as one install:** first add the ESP-off `coding_swift15_iq3s` alias on both sides (old #4, card 21). Then install pi-job, which carries H1c, H5, L1, L4, L5, L6, L8 and the ST3 trigger. Live tests:
   - H1c with a render running (#5: `:8447/health` must return non-2xx while busy).
   - Gufo `/slots` exists, and a run makes 0 swaps.
   - L8: edit a READY run's prompt and check the old code now fails. Don't use recompile on long_continuation until N1 is fixed.
5. **L3 by hand only:** run with `DRY_RUN=1` once and read the log. Add a timer only after N2 is fixed and Derrick says yes.
6. **Hold:** the S2 hook into `comm.py`/gate needs a Derrick-approved commit to `scripts/allowlist_promoted.json` for any new template. H2 live needs the SSRF guard active and Derrick's yes.

Verified: `git log`/`diff 3a130d1..c0c9492` on `C:\tmp\evo-work\mono.git`. AST parse of pi-job, import_inbox.py and
template_allowlist.py. `pytest scripts/tests/test_template_allowlist.py` (12 passed, Python on this PC). Script that
compares variable fields before and after across all 10 core templates. `wp_lint.lint` with the kind-only ctx on test
fixtures. llama-swap model id and group (config/llama-swap.yaml:43-51).
Could not verify here: `bash -n` on the two shell scripts (no bash distro on this PC), Halogen `/slots`, the
gpu_lock_gate `/health` semantics, ntfy `copy`, the pi `tool_result` contract, and `flock` behaviour (fcntl is a no-op
on Windows, so this needs the box).
