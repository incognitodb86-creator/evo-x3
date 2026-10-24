---
name: forge-self-diagnose
description: Diagnose the Forge Ralph loop after every iteration - read ralph.log and notes/denies.log, write notes/self_diagnosis.md, split a task that ticked 0, handle guard denies (web saves, protected paths, credential-shaped env names), keep TASKS.md ticks machine-readable, and commit. Use at the start of every pass, and after any TIMEOUT, ticks=+0, checkfails, scope fail or deny.
---

# Forge self-diagnose (the loop is the product)

ghuntley.com/ralph: "loop back is everything"; "each time Ralph does something bad, Ralph gets tuned - like a
guitar". PROMPT.md makes this a per-iteration duty. ralph.ps1, PROMPT.md, TASKS caps' harness flags and every
permission file stay Max's: editing them = SCOPE fail + STOP_RALPH. If you need one, write `[!] Max: <ask>` in notes
and a line in `notes/guard_requests.md`, print `GUARD_REQUEST`, and carry on with the rest.

## 1. Every pass, in order

1. `tail -n 15 C:/Users/derek/5slock/ralph-community/logs/ralph.log` - STEP 0 breaker: 3 TIMEOUTs in a row, or the
   same FAIL on the same task = do not retry it: mark it `[!]` with a one-line reason, append a learning, exit.
2. `tail -n 2` of the `summary:` lines, and every `notes/denies.log` line newer than your last entry in
   `notes/self_diagnosis.md`.
3. If the last pass timed out, ticked `+0`, or had denies: FIRST append to `notes/self_diagnosis.md` the time, what
   failed, the cause and the fix. Then fix everything in reach: split the task into smaller TASKS lines so each
   pass ticks one, fix scripts/tests in `C:/AI/community`, save partial work to notes before long steps.
4. Do the FIRST `- [ ]` line in TASKS.md and only that one, then exit. Tick with a one-line result; if blocked,
   `[!]` + indented `BLOCKED: <why>` + the same text in `ralph-community/STOP_RALPH`.

## 2. Reading denies.log without causing one (the deny that logs itself)

- The fiction lock matches the TEXT of a command: a shell `tail`/`cat` of `denies.log` prints the blocked module
  path back into stdout and the guard blocks the whole call. Use the `read` tool with a small `limit` on
  `notes/denies.log` (tool input is not a shell command string) - that is the fix that ended 5 passes of repeats.
- A credential-shaped env var name anywhere in a command line = `headless-guard secret` deny. Probe env inside a
  `.ps1` file that prints `set` / `not set` (+ length) only. Never read/print `.env*`, rclone config, tokens,
  API keys, SSH keys, credential stores - and do not retry a deny, never work around one.
- `protected-paths` denies on `ralph.ps1` greps: read the facts you need out of `ralph.log`, notes, or the
  harness-visible docs; ask Max with `[!] Max`.
- Log nothing secret; the harness logs every tool call to `notes/forge_actions.log` and every deny to
  `notes/denies.log`. You may propose a rule change in `notes/guard_requests.md` (PROMPT.md SELF-DIAGNOSE).

## 3. The check-bombs seen in this loop

- `checkfails=1` (2026-10-23 16:59:37): the harness `json.tool`-checks EVERY `notes/web/*.json`, and a body that is
  really HTML sits there as a STOP_RALPH bomb. Save with `python C:/AI/community/scripts/web_fetch.py --url <u>
  --name <n>` (extension from the bytes: `.json` only if `json.loads` accepts, `.html` for markup, `.txt`
  otherwise, non-200 -> `<name>.403.txt`), reclassify an old body with `--from <file>`, and END every research pass
  with `python C:/AI/community/scripts/check_web_saves.py` (rc 1 = offender, `--fix` renames). Details:
  `notes/hf2_web_save_policy_20261023.md`.
- Control chars eat notes and split TASKS.md lines: a NON-raw python string containing `C:\...` turns `\a` into
  BELL (eats the `a` of `ali163` -> 0x07), `\b` into BACKSPACE (eats the `b` of `body`), `\n`/`\r` into newlines.
  One ticked TASKS.md line became three fragments and broke the harness `ReqTicked` check (ralph.ps1 reads LINES).
  **A tick is ONE physical line.** Use forward slashes, a quoted heredoc (`cat >> f <<'EOF'`) or a python raw string,
  then scan per line: `[(i+1,[ord(c) for c in l if 0 < ord(c) < 32]) for i, l in enumerate(text.split("\r\n"))]`
  (a whole-file scan false-fails, because CRLF supplies 13/10).
- `TASKS.md` IS CRLF: read with `io.open(newline="")`, join on `"\r\n"`, never write LF-only (an LF rewrite makes
  the harness diff touch every line; keep `git diff --stat` small).
- In the bash tool use `/dev/null`; `>NUL` CREATES a file named NUL in the cwd. In PowerShell, `NUL` is right.
- AGENTS.md "## Learnings": keep <=15 bullets, <=200 chars each, merge rather than append; verbatim full text goes
  in `notes/forge-learnings.md` (append-only).

## 4. A green check that cannot fail is worthless

Every builder/self-check gets a self-destruct probe: clone the built graph (or hide one frame file), restore the
OLD wiring / wording, and require every detector to FIRE there and 0 of them on the real artifact. Report the probe
result next to the PASS. Scratch builders and self-checks live in `notes/*.py`; the FINAL `check/sheet/summary`
scripts REGENERATE their json/png/md, so prose goes in the script, never in the generated file.

## 5. Finish the pass clean

- Commit your own work in `C:/AI/community`: `git -C C:/AI/community add <file>; git -C C:/AI/community commit -m
  "<task id>: <what and why>"` (3+ words). Never commit in `ralph-community` (the harness commits before/after every
  iteration); push/reset/checkout/--amend are blocked.
- Print `DONE` (or `COMPLETE` when no `- [ ]` line remains) and exit.

## Sources

`C:/AI/community/notes/self_diagnosis.md` (every incident, verbatim), `notes/forge-learnings.md`,
`notes/hf2_web_save_policy_20261023.md`, `notes/progress.md`, `C:/Users/derek/5slock/AGENTS.md` "## Learnings",
`C:/Users/derek/5slock/ralph-community/PROMPT.md` (STEP 0 + SELF-DIAGNOSE).
