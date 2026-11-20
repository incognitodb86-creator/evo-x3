# EVO-X3 Hermes coding workspace

This folder is the working directory (`terminal.cwd`) of the Hermes `code` profile. Derrick uses this chat for code
changes, code reviews, and debugging. Renders do not happen here; they use the default (render) chat.

## Who does what

- Hermes reads code, runs read-only checks and tests, explains, and plans.
- pi makes the code changes and reviews, through the `pi-job` skill: `pi-job code <repo> "<task>"` or
  `pi-job review <repo> "<task>"`. Pass Derrick's ask to pi verbatim, give him the job ID, wait, then report DONE with
  the commit SHA or STUCK with the `detail=` line. Do not retry on your own.
- Fine to do here without pi: read files, grep, run tests, show diffs, `git log`, `git status`.

## Repos on this host

- `/home/evo/AI/community`, `/home/evo/AI/render`, `/home/evo/AI/forge` (owner `evo`).
- Do not run `git remote -v` inside `community` or `render`. Do not open `sydney/`, `models.json`, or Grok sidecars.

## Rules

- Back up before the first edit. Prefer small, reversible changes. Do not weaken gates, locks, allowlists, or the 18+
  stop.
- Never print keys or tokens. Do not read `auth.json`, `mcp.json`, `.env` files, `*.token`, `*.cred`,
  `/etc/evo-x3/*`, or `~/.ssh`.
- Changes to llama-swap, systemd units, ComfyUI server config, or live production templates need Derrick's yes for that
  exact change and the X3 lease: one line `<who> | <what> | <start time>` in `/home/derekboone/AI/locks/x3-lease.txt`
  before the change (stop if it is not empty), cleared when done. Read-only checks need no lease.
- No renders here: no `--queue`, no `--yes-derrick`, no `pi-job render|approve|queue`.
- For commands that may run past the 180 s terminal timeout, use the terminal tool with `background=true` and
  `notify_on_complete=true`, then the `process` tool to wait. Never use `setsid` or `nohup` (Hermes blocks them).

## REA pipeline build (Derrick 2026-11-20)

- The REA parody pipeline is built by pi, one unit per `pi-job code`, in the worktree
  `/home/evo/AI/_worktrees/rea-parody` (branch `pi/rea-parody`).
- Unit specs: `records/REA-PARODY-PIPELINE/PIJOB-TASKS.md` in that worktree. When Derrick says `Run REA unit C<n>`,
  read that unit's task text and pass it to `pi-job code /home/evo/AI/_worktrees/rea-parody "<task text>"` exactly
  as written. One unit at a time, in order. After DONE, run the unit's Check command and report the pass/fail counts.
- Do not merge, push, or copy files into `/home/evo/AI/community`; Max does that after review.

## Time

Report times in America/Chicago (CT).
