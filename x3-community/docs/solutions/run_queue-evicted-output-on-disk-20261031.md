# run_queue: evicted/stalled job whose output was already on disk got re-rendered (2026-10-31)

## Symptom
Klein N12 batch (runs/2026-10-31_klein_explicit_0010): 12 stills submitted together around 06:51 CT. At 06:59:40, pos 4-12 were logged `FAIL ... stall evicted` and re-rendered one at a time (about 29 min each). A `_00002_` duplicate showed up at 07:29:52.

## What it looked like
It looked like llama-swap broke the run: its cmdStop (comfy_graceful_stop.ps1) waited 331 s for ComfyUI's queue to drain, then killed comfyui_auto at 06:59:05. But the stop worked. The queue had drained, and all 12 PNGs were on disk (06:53:54-06:59:01).

## Real cause
The run_queue graphs save with `filename_prefix = community/<run>/<tag>`, so ComfyUI writes flat files: `output/community/<run>/<tag>_00001_.png`. The evict/stall fallback, `run_graph_job.collect_from_disk`, only looked in `output/community/<tag>/` (the folder layout run_graph_job uses). It found nothing, so every evicted job counted as failed and got its "unchanged retry".

## Fix
`scripts/run_queue.py`: new `disk_output(run_dir, tag, since)`, which `finish()` checks first. It looks for an exact `<tag>_NNNNN_.png|.mp4` in `output/community/<run>/` with mtime >= submit time minus 5 s and takes the newest; then it tries the old per-tag folder. The file then goes through the normal OBJECTIVE check, render_ok.json and DONE line. This covers stills and clips. Backup: `run_queue.py.bak-0735`.

## The test
`scripts/tests/test_run_queue_evict_disk.py`: an evicted still and a stalled clip whose files exist after submit are both collected as DONE with no FAIL (so no retry), and a near-miss tag (`E1` vs `E11`) is ignored. A job with nothing on disk still returns None and fails.

## Prevention checklist
- [ ] Before calling a run stalled or evicted, check the disk outputs (output/community/<run>/ and /<tag>/) and comfy-graceful-stop.log.
- [ ] Don't prompt Forge while a render batch is queued.
- [ ] Watcher scripts must write a heartbeat line every few minutes.
- [ ] Any new save-prefix layout must have a matching disk-fallback path and a test.
