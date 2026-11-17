# ALI-173 B1/B2 - `C:/AI/community/runs/bakeoff_gpu_events.jsonl` (append-only, six keys, machine-parsable)

Written by the loop that touches the GPU. One JSON object per line, keys exactly:

| key | rule |
|-----|------|
| `event` | one of `request_staged`, `precheck_pass`, `render_start`, `render_pass`, `render_fail`, `gpu_window_open`, `gpu_window_close` |
| `iter` | `^loop\d\d$` (the loop number, e.g. `loop07`) - not a timestamp, not a job id |
| `ts` | wall clock, ISO-8601 seconds, from `datetime.now()` on this box |
| `job_id` | `^[a-z0-9_]+_s\d+$` - the real job id, not `loop01`. **Underscores are required** for the ids in use (`ali147_pool_hc_r3b_s51130001`, `ali173_cont_hc1_s51140001`); B1's first schema line said `^[a-z0-9]+_s\d+$`, which rejects every real id on this box - corrected here, and B1's tick note says so. |
| `sha256` | 64 lowercase hex, the real `hashlib.sha256` of the graph file the event is about - never a placeholder |
| `status` | `ok` / `fail` / `blocked` |

Self-destruct probes (B1's rule: the key must be proved by length AND by a probe that must NOT pass):
a 65-hex and a 63-hex `sha256`, a non-hex `sha256` (upper case / short), `iter` = `loop1`, `job_id` =
`loop01`, `job_id` = an id with dashes, a 5-key line and a 7-key line. A validator that accepts any of
those is worthless.

Durability, checked on 2026-10-23: `C:/AI/community/runs/` is **gitignored** by C:/AI/community
(`.gitignore:10 runs/`), so this file is on disk but never in git. `ralph.ps1` contains **no** `git clean`
(`grep -n 'clean -fdx' ralph.ps1` = 0 hits) - the scope restore is `git -C $K checkout -- <path>` on
TRACKED ralph-community files (ralph.ps1:110), and a NEW file in ralph-community is moved to `_removed`
(ralph.ps1:96; `_removed/` holds only 2026-10-20 entries today). So an untracked `runs/` file survives
iterations, and nothing restores it. The real reason B1's 18:2x CT check found this file missing is
simply that **it had never been written** - B1 produced the schema doc and validators in `notes/`, and
A2's precondition ("events exist under runs/") was unmet. Keep the durable schema, ledger, findings and
validators in `notes/` (tracked), and re-emit `render_*` events when the harness runs jobs.

Current lines: 4 (loop07, `job_id ali173_cont_hc1_s51140001`, `sha256` = the sha of
`runs/ali173_cont_hc1_s51140001/request.api.json` = `1efecedd53549c5e05887985f352a18d5897ca8587588af39b67052bfabd2088`):
`request_staged` + `precheck_pass` (18:30:25) and the `gpu_window_open` / `gpu_window_close` pair for the
18:12:36-18:13:00 CT read-only schema window (comfy_ok=True, queue (0,0), gpu_guard IDLE rc 0).
Validate with `python C:/AI/community/notes/ali173_b2_events_check.py` (it re-hashes the graph file named by
each line and refuses a sha that is not that file; `--selftest` = 12 probes: 65-hex, 63-hex, UPPERCASE, iter=loop1,
job_id=loop01, dashed job_id, unknown event, 5-key, 7-key, a sha from a different graph, missing file). A
`render_start`/`render_pass` (or `render_fail`) pair is due when the harness runs the job - the loop never renders.
