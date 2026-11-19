# Render-queue template

Script: `C:\AI\community\scripts\run_queue.py`. Use it for every render queue. Do not write a per-test queue script.

Request graphs: build each `<run dir>\<tag>\request.api.json` with `scripts\make_b2_request.py` from `templates\b2.api.json` (the B2 default; see `templates\b2.README.md`). Do not copy old run graphs.

What it does: one GPU window per batch. Lock only: it runs the pytest gate, takes `C:\AI\locks\gpu-render.lock` once (rc 7 if it is held; there is no gpu_guard step), unloads the LLM and wakes comfyui_auto once, then renders every clip back to back. Before every clip it runs comm.guard_ok on every prompt string, keeps comfyui_auto awake, runs the static check, then the render and the OBJECTIVE check. A failed clip gets one unchanged retry, then is logged FAIL and skipped; the queue goes on. A `finally` block unloads comfyui_auto and releases the lock, also on error or Ctrl-C.

Order file: `<run dir>\_render_order.json`, `{"order": [{"pos", "tag", "arm", "scene", "seed"}]}`; each `<run dir>\<tag>\request.api.json` is the graph.
Log: appends START/DONE lines to `<run dir>\_render_queue.log`, ending with `BATCH closed rc=<n> reason=<why>`.
Stop cleanly: create an empty file `<run dir>\STOP`. It halts after the clip in flight. Delete the file before resuming.

## Start or resume a run

Stage first (before asking for a go), then use the AGENTS.md Render launch line and end the turn; no waits or checks.

    C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py --run-dir <run dir> --dry-run
    C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py --run-dir <run dir> [--resume] [--frames <n>] --detach

The dry run lists the clips and makes no lock, GPU or HTTP call. `--detach` prints the batch PID; output goes to `<run dir>\_run_queue.out.log`.
Set `--frames` per clip from the plan; it must equal c0.length in the request (124 is only run_queue's fallback when omitted); the frame check only confirms each clip came out at that length. `--size` defaults to 768x1344.
Exit codes (run_queue.py docstring): 0 done, 1 STOP file, 2 pytest gate failed, 4 ComfyUI down, 5 a clip failed twice (others still rendered), 6 clips missing a DONE ok line, 7 GPU busy (lock held), 8 uncaught error (incl. a lock-tool error), 9 a previous batch was killed or never closed, 130 Ctrl-C.
