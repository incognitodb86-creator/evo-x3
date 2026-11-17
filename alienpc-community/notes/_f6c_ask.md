## F6c needs one render GO (2026-11-13 23:5x CT, Forge ralph pass)

F6c's last clause is "one test render through the skill passes with an OBJECTIVE ok line (GPU gate, lock, small frames, non-Sydney)". Everything else about that clause is prepared and measured; the only thing missing is your GO for a GPU window (standing rule: any render needs Derrick's go).

- Gate measured OPEN this pass: `C:\AI\locks\gpu-render.lock` absent; `comfy_ctl.py status` 23:52:27 CT `guard=(0, ['IDLE'])`, no queued job.
- The one command the skill points at is ready and dry-run clean (no lock/GPU/HTTP):
  `C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py --run-dir C:\AI\community\runs\f6c_comfy_render_skill_2026-11-13 --frames 124 --size 768x1344 --no-upscale`
  -> `queue 1 clips, 0 already DONE ok, 1 to render / pos 1 c1_f6c_preflight / dry run: no lock, GPU or HTTP call made`
- The clip: the existing non-Sydney B2 graph copied from `runs/speed_ab_20261113/arm_C_6step_base/request.api.json` (22 nodes, seed 51083601, 124 f, 768x1344), output prefix redirected into the F6c run dir. Adults guard `guard_reason=(True, '')`. Cost: that same graph rendered 124 f in 122 s on this box today (`runs/speed_ab_20261113/status.log` 22:21:11 CT `OBJECTIVE ok arm_C_6step_base frames=124 size=768x1344 audio=True`); add ~35-40 s for the comfyui_auto wake.
- Why "small frames" is not smaller here: H3 is on a frame grid ((frames - 5) % 17 == 0), so the smallest legal clip is 22 f, and no 22-frame render exists on this box as precedent. 124 f at 768x1344 is the shape with measured OBJECTIVE-ok history today. Say "go" for that, or name a smaller/other shape and I will use it.
- The other two F6c clauses were proved this pass: description length 287 chars (<=1024), and `pi --print` on the already-loaded model lists `comfy-render` and does not list `alienpc-local-video-ops` (46 names, saved `notes/_f6c_pi_skill_list.txt`).

Nothing was queued by this pass. No GPU, no lock, no render, no model load.
