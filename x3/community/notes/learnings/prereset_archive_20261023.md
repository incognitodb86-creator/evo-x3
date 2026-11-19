# 0.3 pre-reset archive - result (2026-10-23, Forge/Ralph)

**Item:** fix_plan.md 0.3 "Archive (copy, never delete) the pre-reset files to
C:\AI\community\archive\2026-10-23-prereset\ ... Commit."

## What is in the archive now
`C:\AI\community\archive\2026-10-23-prereset\MANIFEST.json` - 80 files, 1,622,608 bytes, one
`{source, bytes, sha256, src_mtime, mode}` entry per file.

| group | files | what |
|---|---|---|
| archive root (mode `deployed`) | 5 | ralph.ps1, PROMPT.md, TASKS.md (the 131 KB pre-reset plan), RESET_BRIEF_20261023.md, launch_reset_20261023.ps1 - copied by Max during the 20:06 deploy, verified by dest hash only (their live sources were overwritten) |
| `ralph-community/` | 63 | `*.bak-*` (44: PROMPT.md, TASKS.md, ralph.ps1 histories), `STOP_RALPH*` (17), `.TASKStmp.md`, `.c2scratch.md` |
| `ralph-community/_logs/` | 2 | `logs/PROMPT.md.bak-20261022-selfheal`, `logs/ralph.ps1.bak-20261023-breaker` - dest dir renamed `_logs` because `C:\AI\community\.gitignore` ignores `logs/` at any depth, so the copies would never have been committed |
| `5slock/` | 7 | the live `AGENTS.md` (10,628 B, the over-controlled Max-rules version) + its 6 `AGENTS.md.bak-*`. **C:\Users\derek\5slock is not a git repo** (`git rev-parse` = "not a git repository"), so this archive is the only backup those 7 files have |
| `pi-extensions/` | 3 | `headless-guard-and-truncate.ts` (67,476 B), `headless-guard-allowlist.json` (8,792 B), `protected-paths.ts` (10,242 B) - the three fix_plan 0.4 removes from settings.json; the 8 `.bak-*` siblings in that folder stay in place |

Scope was the **loop** files only. `C:\Users\derek\5slock\drv.py.bak-*`, `wfsnap/`, `_removed/`,
clips/frames and the render-script histories are not loop files and were left alone.

## Checks (all run, all green)
- `python notes/prereset_archive_20261023.py --archive` -> `copied=75 skipped_identical=0
  entries=80 files=80 bytes=1622608`, RESULT OK rc 0; re-run -> `copied=0 skipped_identical=75`
  (idempotent, no duplicate copies).
- `--verify` -> `entries=80 problems=0` rc 0: every archived byte matches its manifest sha **and**
  its live source sha, and every source file is still on disk = proof it was a **copy, not a move**
  (RESET_BRIEF: "Never delete anything").
- `--selftest` (the self-destruct probe) -> on a temp **clone** of the archive it flips the bytes of
  `5slock/AGENTS.md` and deletes `ralph-community/ralph.ps1.bak-20261023-job35`; the verifier raised
  exactly those two (`HASH` + `MISSING`) and 0 problems on the real tree => the check can fail, so
  the green result means something.
- Source trees after the run: 63 + 2 + 7 + 3 = 75 live files, unchanged.
- `git -C C:\AI\community add -A archive` stages 81 paths, `git status --ignored` on the archive =
  0 ignored (the `_logs` rename is why).

## Notes for the next pass
- 0.3 is what makes 0.4 safe: settings.json still loads
  `C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts` + `protected-paths.ts`
  (`-builtin:mcp` is also still disabled). Both extensions and the allowlist are now archived +
  committed, so dropping them from `extensions[]` loses nothing. Back up settings.json in the same
  commit (it is not in any repo).
- The live loop files (ralph.ps1 1,116 B = the 15-line snarktank port, PROMPT.md,
  ralph-community/AGENTS.md, fix_plan.md) were **not** archived this pass: they are the *new* stock
  set, and ralph-community is a git repo (harness commits each iteration).
- 0.1/0.2 (community research + claim-by-claim verification) are the remaining gate before 0.5's
  rewrites; 0.4 can be done before 0.1/0.2 only if the baseline test (1.1-1.4) starts, which the
  RESET_BRIEF wants anyway ("the first passes run under [the guard extensions]").
- Builder script: `C:\Users\derek\5slock\ralph-community\notes\prereset_archive_20261023.py`
  (`--archive` / `--verify` / `--selftest`). Re-run `--verify` any time the archive is touched.
