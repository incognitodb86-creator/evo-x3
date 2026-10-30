# Max brief for pi, 2026-10-28 3:50 PM CT (Derek: "get us back on track", "don't overcomplicate this, build the scripts and follow workflows", "we are now using beta 7")

The last session ran out of context (89%, compaction failed) after writing ~20 probe/helper scripts and rendering nothing. Fresh start. Rules for this session:
- NO new scripts. Use what exists. If something is missing, stop and tell Derek in one line.
- One PowerShell call per render. Never use the bash tool.
- Keep replies short. Do not read big files in full; read only the lines you need.

Spec: C:\AI\community\notes\ab_q4_q5_brief_2026-10-28.md (read once).
Already built and checked (beta7 int8HQ, seed 51083002, v2 prompt, TERRACE2 still):
- A: C:\AI\community\runs\terrace_dom_q4_20261028_s51083004\request.api.json (8 steps)
- C: C:\AI\community\runs\terrace_dom_c12_20261028_s51083006\request.api.json (12 steps)
- B: C:\AI\community\runs\terrace_dom_q5_20261028_s51083005\request.api.json (needs a ComfyUI restart to load MinimaxH3LatentUpscaler3D; ask Derek before restarting)

Steps, in order:
1. Render A: powershell -NoProfile -ExecutionPolicy Bypass -File C:\AI\community\scripts\gpu_window.ps1 -Dir <A dir> -Tag terrace_dom_q4_20261028_s51083004 -Frames 243 -Timeout 1800
   (gpu_window.ps1 takes the GPU lock, runs run_graph_job.py, which runs the adults-only guard, and releases the lock.)
2. Render C the same way with the C dir and tag.
3. RTX smoke fix: in C:\AI\community\runs\rtx_smoke_20261028\request.api.json the RTX node failed with "rtx.scale: not an input". RTXVideoSuperResolution's resize_type is a V3 dynamic combo, so the nested input is keyed "resize_type.scale". Fix only that key in post_graph_build.py, rebuild, rerun the smoke with gpu_window.ps1 -Frames 24. If that still fails, stop and report the exact error; do not write a probe.
4. If the smoke passes: post-process A and C (raw kept, RTX 1.2x ULTRA, finalize_encode.py crf 18).
5. Message Derek: A and C file paths, render seconds, and ask whether to restart ComfyUI for B.
No KEEP or PASS (Derek judges). No deletes. Never kill pi --remote or the :7878 hub.
