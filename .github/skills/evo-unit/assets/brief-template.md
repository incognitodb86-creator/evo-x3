# U<##> (Antigravity, Hydrogen High): <goal in plain words>, <Mon DD YYYY>

Derrick <t####u>: "<his words>". Plan: <records/<topic>/PLAN.md step S#, or none>. Max verifies your RESULT afterwards.

## Goal
<2–4 sentences: the outcome, and the way the community does it if that applies.>

## Access
- You run as <derekboone | evo>. Repos: <paths>. <Use `sudo -n -u evo bash -c '...'` for evo-owned repos.>
- Work in your per-run worktree `~/evo-x3/_worktrees/U<##>-<repo>` on branch `agy/U<##>` (records/agy-launcher-convention.md).
- Lease: <one line `agy | U<##> <job> | <start time>` in /home/derekboone/AI/locks/x3-lease.txt, taken at start (stop if not empty), cleared when done or blocked | read-only, no lease>.
- Why: <the problem this fixes, with run/log evidence>.

## Work
1. <step>
2. <step>

## Tests
- <test that must pass, with the exact command>
- <end-to-end or smoke check that would fail if the work is wrong>

## Rules
- Back up every file you change as *.bak-<YYYYMMDD>-u<##> in _archive/. Commit by path only, no `git add -A`, no force push, then push to <gitea remote and branch>.
- Don't <restart panes / edit llama-swap / touch ComfyUI / read PixlStash or chat memory> unless listed above. No secrets on argv or in output.
- Keep it small: no new gates, linters, check steps or config knobs.

STOP CONDITION: when done or blocked, write /home/derekboone/evo-x3/records/U<##>-RESULT.md, then stop. List each Work and Tests item as DONE, BLOCKED or SKIPPED with <evidence the reviewer needs: files and backups, commits and pushes, test totals, proof paths>.
