---
name: h3-hc-render
description: Wire, gate, request and verify a MiniMax-H3 / 10Eros-Max (beta6 int8) ComfyUI clip for the Forge Ralph loop - graph keys, reference-image wiring, frame/canvas math, the p7 budget gate, JOB_REQUEST.json, and the objective proof checks. Use when building a graph, requesting a render, checking a rendered clip, or touching p7/JOB_REQUEST.json.
---

# H3 hardcore render

Work the loop in this order. One job per pass. Never mix a request pass with a proof pass.

## 0. When to use this skill

- A render-request task in this batch: writing an arm graph, re-requesting a dead clip, choosing length/canvas, counting jobs, spending GPU minutes.
- Verifying a rendered clip (frame count, fps, audio, seams, hashes) or deciding whether a pass may submit at all.
- Any MiniMaxH3 / Continuum 3.10.2 job: the numbers below are the ones that already burned real jobs.

## 1. Read the state before anything

- `tail -n 15 C:/Users/derek/5slock/ralph-community/logs/ralph.log` (TIMEOUT / same-FAIL breaker: PROMPT.md STEP 0).
- Budget gate `C:/Users/derek/5slock/ralph-community/logs/p7_budget.json` -> `used_min`, `jobs`, `cap_min 615`,
  `job_cap 45`. R-lines stop at the original 495 min / 35 jobs; the extra 120 min / 10 jobs are the ALI-173
  bakeoff. There is NO `p7_budget.json` under `C:/AI/community` - never quote an assumed count.
  Request only while `jobs < cap` and `used_min + 10 <= cap_min`, else `[!] BLOCKED: budget` + STOP_RALPH.
- GPU lock: `python C:/AI/community/scripts/comfy_ctl.py status` (no arguments to gpu_guard). Never stop/restart
  ComfyUI while a render runs; after every start/restart continue only if `comfy_ok=True`.
- Direct-HTTP renders (bakeoff arms only): wake + queue + wait + fetch in ONE script call, log the window in
  `C:/AI/community/notes/bakeoff_gpu_ledger.md`.

## 2. Graph wiring (the part that has actually broken)

- Base graph: copy `C:/AI/community/runs/ali147_pool_promptv2_s51080000/request.api.json` and change ONLY the
  listed keys (`width`/`height` on c0+c1, the two prompts, `img.image`, `noise.noise_seed`, `save.filename_prefix`).
- Model `10Eros_Max_h3_8stepTURBO_beta6_int8`, euler/simple, 10 steps, shift 10 (video) / 3 (audio). Steps live in
  `s0_sched`/`s1_sched`, sampler in `ksel`, shift in `m_shift`; there is NO cfg key in these graphs at all.
- **References (this is what fixed body quality): 3 slots on c0 AND c1.**
  `ref_images.ref_image_1` = the approved full-body start still (the body/scene reference, `<Picture 1>`),
  `ref_image_2`/`ref_image_3` = face crops (face + hair only, `<Picture 2>`/`<Picture 3>`). r3r-r6 used face crops
  only and the start still was not in the graph at all - that is the failure Derrick rejected. Builder:
  `C:/AI/community/notes/ali163_hc_bq1_build.py` (r4g2 builder stays frozen so old ids reproduce).
- Read ref slots with `fullmatch(r"ref_images\.ref_image_\d+")` over nodes whose `class_type` starts with
  `MiniMaxH3` (submitted graphs also carry a `ref_images` dict, so a bare key scan false-fails). Seed is
  `inputs["noise_seed"]` (RandomNoise has no `seed`).
- `ref_image_size`: `match` caps a reference to the canvas pixels, `max` only downscales sides over 2048
  (`ComfyUI_MiniMax_H3_Extender/extender.py:113,2274`).
- `MiniMaxH3ImageToVideo` has NO `audio_vae` (only `ReferenceToVideo` does) -> static rc=2.
- `clips_json` must keep `"validated": false` (true = the UI checkbox; the Extender refuses to sample it headless).
- `LoadImage` strings must resolve inside `ComfyUI/input`; job outputs are written as `<sub>/<name>.png [output]`.
- Continuum arm: canvas must be a multiple of 32 (832x468 is unreachable, use 1024x576),
  `target_frames = chunks * chunk_seconds * fps`, and `H3ContinuumSamplerV39` has no negative/CFG key.
  ComfyUI 0.19.2 dropped `sparse_blocks`/`sparse_size`/`max_dims` - the frozen r3b nodes 10/11 are schema-STALE.

## 3. Frame / canvas math

- Batch canvas 1344x768 (16:9), 24 fps. Community length: **243 frames = 10.125 s**, grid `(frames - 5) % 17 == 0`
  (c0 `length` 124 = 17*7+5; window overlap 22 + extension 119; c1 141 generated / 22 hidden; 124 + 119 = 243 =
  17*14+5). 481 f = 20 s is the shape Derrick rejected. `duration = round(frames/24, 6)`.
  Sources: `notes/hc_redo_research_20261023.md` (row table), `notes/ali147_summary.md`.

## 4. Static self-check, then request

- Offline clone of `run_graph_job.static_check`: `notes/ali163_hc_r4g2_build.py` check 11 (schema parsed from
  `comfy_extras/nodes_minimax_h3.py`, no network). Every builder gets a **self-destruct probe**: restore the old
  wiring in a clone and require every detector to fire there and none on the real graph. A green check that cannot
  fail is worthless.
- Test the id against every `ralph.ps1` `-notmatch` pattern before writing it (patterns at ralph.ps1:202 and :283).
  To re-request a dead clip, clone its rendered `ok=True` sibling graph and change only the per-clip keys.
- Write `C:/AI/community/p7/JOB_REQUEST.json` (ABSOLUTE path; a `ralph-community/p7/` folder must never exist):
  `{"jobs": [{"id": "<id>", "kind": "graph", "frames": 243, "frames_tol": 0, "minutes": 60}]}` + trailing newline,
  `python -m json.tool` it, tick the TASKS line, print DONE, EXIT. A request is submittable only while
  `C:/AI/community/p7/jobs/<id>.result.json` is absent. Never write proof/notes/audit files in a request pass.
- One seed per clip. Never request a quality redo (harness redos = same seed, then seed+1).

## 5. Proof (next pass, objective only, NO vision judge on explicit output)

- `result.json` ok/rc; frames + rate + size:
  `ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0 <mp4>`
- Duration: `ffprobe -v error -show_entries format=duration -of csv=p=0 <mp4>`; audio line in
  `ffprobe -show_streams -of csv=p=0` prints `aac,audio,...` -> test `',audio' in line`, never `startswith("audio")`.
- Audio copy: `ffmpeg -y -i <mp4> -vn -c:a copy <id>.m4a`; frames: `ffmpeg -y -ss <t> -i <mp4> -frames:v 1 <png>`.
- Hashes: `certutil.exe -hashfile <path> SHA256`; graph compare: plain `cmp a b` (`cmp -s && echo` is denied).
- Contact sheet + objective json + summary md are GENERATOR OUTPUTS
  (`notes/ali163_hc_final_{check,sheet,summary}.py`) - prose goes in the script, never in the generated file.
  Frame flatness = PIL `ImageStat` grayscale stdev (a flat frame sits near 0; good clips measured 33.9-56.8).
- Face similarity (CPU ArcFace/SCRFD in `C:/AI/qa_gate_venv`): `notes/hc_r4f_facelib.py`, `notes/ali163_hc_r4f_face.py`.
- Review = contact sheet + these numbers. KEEP is Derrick's alone; a score never triggers a redo.

## Sources

`C:/AI/community/notes/hc_redo_research_20261023.md`, `notes/hc_face_research_20261023.md`,
`notes/bakeoff_gpu_findings.md` + `notes/ali173_b2_object_info_full.json` (live schema dump),
`notes/ali163_hc_bq1d_objective.json`, `notes/forge-learnings.md`, `C:/Users/derek/5slock/AGENTS.md` "## Check commands".
