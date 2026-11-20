---
name: pi-job
description: "Use for ANY coding or code-review job: hands it to pi with pi-job code|review (AlienPc Swift when idle, X3 Gufo when busy) and reports DONE with the commit or STUCK. Not for renders: renders use h3-render."
---

# pi-job (coding hand-off to pi)

Hermes does renders itself (h3-render skill). pi is only for code. Use `/usr/local/bin/pi-job` for code changes and
code reviews in a git repo.

## Commands
- `pi-job code [--timeout-min N] <repo_path> "<task>"`: runs Forge detached. `DONE` only if a new git commit is
  created, else `STUCK`. pi is stopped after 60 min unless `--timeout-min` (5-480) says otherwise.
- `pi-job review [--timeout-min N] <repo_path> "<task>"`: runs a read-only Forge review detached (default 30 min).
- `pi-job wait <job_id> [--timeout 170]`: blocks up to 170 s while the job is working, then prints its status.
- `pi-job status <job_id>`: prints job status (and recent log lines while it runs).

Only one `pi-job` runs at a time. Tell Derrick the job ID right after starting a job.

## Flow
1. Code or review ask: run `pi-job code|review <repo> "<the ask, verbatim>"` and give the job ID.
2. Run `pi-job wait <job_id> --timeout 170` in a bounded loop (several rounds in one terminal call) until the status
   is no longer QUEUED/RUNNING.
3. `DONE`: report the new commit SHA and the one-line summary. `STUCK`: quote the `detail=` line exactly and stop.
   Never retry on your own. If the detail says `timed_out_after=`, the job ran out of time: tell Derrick, and only if
   he says so, start it again with a longer `--timeout-min` (the work done so far is still in the repo).
4. `REFUSED: another pi-job is already running (<id>)`: the single slot is busy (maybe Derrick's own job). Tell him
   and retry about every 10 s only if he asks.

## Old pi render path
`pi-job render|approve|queue|upscale` still exist in the script as a fallback. Use them only when Derrick says
"use the old pi render".
