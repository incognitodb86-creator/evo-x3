# run_queue evict/stall disk fallback missed flat outputs (2026-10-31)
- Cause: run_queue jobs save with prefix community/<run>/<tag>, so files land flat at output/community/<run>/<tag>_00001_.png. The fallback (run_graph_job.collect_from_disk) only looked in output/community/<tag>/, found nothing, so after comfy_graceful_stop killed comfyui_auto at 06:59:05 all 9 landed Klein N12 stills (pos 4-12) were logged "FAIL stall evicted" and re-rendered as retries.
- Fix: scripts/run_queue.py adds disk_output(run_dir, tag, since), checked first in finish(): exact <tag>_NNNNN_.png|mp4 in output/community/<run>/, mtime >= submit-5 s, newest wins; then the old per-tag folder. Then the normal OBJECTIVE check, render_ok.json and DONE line. Stills and clips both.
- Backup: scripts/run_queue.py.bak-0735. Written atomically (temp + Move-Item).
- Tests: new scripts/tests/test_run_queue_evict_disk.py (still evicted, clip stalled, nothing landed). 44 passed with p6_review, guard_scope, phase1_still. py_compile ok.
- The running N12 batch still uses the old code (already loaded). Left alone, duplicates not cleaned up.
