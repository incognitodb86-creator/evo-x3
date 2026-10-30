# Render-queue template (S4/S8)

Script: `C:\AI\community\scripts\run_queue.py` (sha256 f1765eef54558d42dad79676bc6e3673ec528e944a5a7d06213db9ead95fdd24, 2026-10-30).
Use it for every render queue. Do not write a per-test queue script.

What it does: one GPU window per batch. It runs the pytest gate, gpu_guard and takes gpu-render.lock once, unloads the LLM and wakes comfyui_auto once, then renders every clip back to back. Before every clip it runs comm.guard_ok on every prompt string, touches /comfyui/system_stats so the 300 s ttl never fires, runs the static check, then the render with run_graph_job's redo rule and the OBJECTIVE check, plus one unchanged whole-clip retry. A second failure stops the queue. A `finally` block unloads comfyui_auto and releases the lock, also on error or Ctrl-C.

Order file: `<run dir>\_render_order.json`, `{"order": [{"pos", "tag", "arm", "scene", "seed"}]}`; each `<run dir>\<tag>\request.api.json` is the graph.
Log: appends START/DONE lines to `<run dir>\_render_queue.log` (same format as before).
Stop cleanly: create an empty file `<run dir>\STOP`. It halts after the clip in flight. Delete the file before resuming.

## Resume the terrace v3 run (after the old driver finishes the clip in flight and exits)

    cd C:\AI\community
    python scripts\run_queue.py --run-dir C:\AI\community\runs\terrace_settings_v3_20261030 --queue C:\AI\community\runs\terrace_settings_v3_20261030\_render_order.json --resume --dry-run
    python scripts\run_queue.py --run-dir C:\AI\community\runs\terrace_settings_v3_20261030 --queue C:\AI\community\runs\terrace_settings_v3_20261030\_render_order.json --resume

## Start a new run

    python scripts\run_queue.py --run-dir C:\AI\community\runs\<new run> --dry-run
    python scripts\run_queue.py --run-dir C:\AI\community\runs\<new run> [--frames 124] [--size 768x1344]

Always do the dry run first: it lists the clips and makes no lock, GPU or HTTP call.
Exit codes: 0 done, 1 STOP file, 2 pytest gate, 4 ComfyUI down, 5 a clip failed twice, 7 GPU busy, 130 Ctrl-C.
Phase 2 audit (plan S9): DONE-to-next-START gap under 10 s in `_render_queue.log`.
