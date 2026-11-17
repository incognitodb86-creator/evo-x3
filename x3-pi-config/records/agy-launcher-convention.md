# Future `agy` Launcher Convention (Per-Run Worktree + Lease Line)

Added for **U53 I11** (2026-11-16). Applies to **future** `agy` runs only; existing `U53-agy-launch.sh` / `U53-agy-start.sh` were not modified.

## 1. Per-run git worktree
- Every mutating or coding `agy` run targeting a git repo (`~/AI/community`, `~/AI/forge`, `~/AI/render`, `~/evo-x3`) must launch inside its own per-run git worktree (`~/evo-x3/_worktrees/agy-<UNIT>-<repo>` on branch `agy/<UNIT>`), never directly on the shared live branch.
- Pass `--add-dir "$WT_DIR"` (and `--add-dir /home/derekboone/evo-x3` for records) so the run writes records in `~/evo-x3/records/` and code changes in its isolated worktree.
- On completion, run tests/checks in the worktree before fast-forward/merging `agy/<UNIT>` into the target branch, then prune the worktree.

## 2. Lease-line convention
- Follow `records/evo-x3-lease-README.md` (N5 one-holder X3 lease): any build, install, config edit, restart, GPU/model work, or test run takes a lease first (`records/status/YYYY-MM-DD-HHMM-evo-x3-lease-taken-agy-<job>.md` and corresponding `fleet-brain/30_handoff/status/` entry) and writes a release file when done.
- Every future launcher records a mandatory lease line in `records/<UNIT>-agy.meta.txt` before invoking `agy`:
  - `lease_file=<path-to-lease-taken-md>` (or `lease_mode=read-only` for read-only inspections)
  - `lease_line=holder=agy unit=<UNIT> scope=<scope> taken=<YYYY-MM-DD HH:MM CT>`
  - `worktree=<WT_DIR>` and `branch=agy/<UNIT>`
- Template: [agy-launch-TEMPLATE.sh](file:///home/derekboone/evo-x3/records/agy-launch-TEMPLATE.sh).
