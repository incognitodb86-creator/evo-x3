---
name: h3-hc-render
description: Wire, gate, request and verify a MiniMax-H3 / 10Eros-Max (beta7 int8HQ, default since 2026-10-28) ComfyUI clip for the Forge Ralph loop - graph keys, reference-image wiring, frame/canvas math, the p7 budget gate, JOB_REQUEST.json, and the objective proof checks. Use when building a graph, requesting a render, checking a rendered clip, or touching p7/JOB_REQUEST.json.
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

- Base graph: copy `C:/AI/community/p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json` - the B2 setup,
  made the default by Derrick 2026-10-29 6:59 AM CT ("Ok let's keep the b2 setup and make it default") and a
  byte-identical copy of `C:/AI/community/runs/terrace_dom_q5guide_20261028_s51083007/request.api.json`
  (sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 20072 B, 26 nodes: two-pass, 384x672
  -> LatentUpscaler3D x2 -> 768x1344 portrait, 243 frames, 24 fps, `MiniMaxH3AddGuide` frame 0 on both passes,
  `ref_images.ref_image_1` only, pass 2 = `beta`/3/denoise 0.4). Change ONLY `img.image`, `c0.prompt`,
  `noise.noise_seed`, `save.filename_prefix`, and request with `--frames 243` (= c0.length). The previous defaults
  (`runs/ali147_pool_promptv2_s51080000/request.api.json`, then `p7/graphs/stock_base_tenstrip10.api.json`,
  124 f 1344x768 single-pass beta6) are superseded for new runs; old ids keep their own graphs in `runs/`.
  The 3-ref/1344x768 paragraphs below predate B2 and apply only when a brief asks for that shape.
- Model `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, euler/simple, 8 steps, shift 12 (video) / 3 (audio), VSA 90% sparse, no SLA/cache/spectrum with reference (beta 7 settings from Derek's 2026-10-28 brief; beta 6 is deleted). Steps live in
  `s0_sched`/`s1_sched`, sampler in `ksel`, shift in `m_shift`; there is NO cfg key in these graphs at all.
- beta7 background flicker (TenStrip HF 10Eros-Max #76/#79): mitigation = the 2-pass B2 graph we already use; watch #79.
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

## 5. Proof (next pass, objective only; review = qwen3vl_judge + Z zoom, flag-only; Derrick gives the only KEEP)

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

## 6. Stock render path (moved verbatim from PROMPT.md by U5, 2026-10-29)
Steps a-g for one render item, then script reuse and research rules:
   - For a render item (stock path):
     a. Pick one approved, never-animated still with C:\AI\community\notes\hc_pick_scan_20261023.py (unless named in MAX). GI063 render hold is RELEASED (Derrick 2026-10-27 9:09 AM CT — wrongly flagged by wrong model; do NOT treat GI063 as hold; keep youth guard on GI063).
     b. Caption once with your own model (coding_swift15_iq3s_esp, the ralph.ps1 default): one ask, one image. Vision models exist and stay: the Forge vision model Swift via mmproj, the W7 and W8 writer mmproj files, and JoyCaption.
     c. Write one natural-language H3 prompt from that caption, following h3-prompting (no word cap; long, literal, in time order).
     d. Check: C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py. comm.guard_ok also runs inside run_graph_job.py before /prompt POST; never loosen either.
     e. Build graph: copy C:\AI\community\p7\graphs\default_b2_terrace_dom_q5guide_s51083007.api.json to <run_dir>\request.api.json and change only LoadImage path, c0.prompt, noise_seed, filename_prefix. That file IS the B2 setup (Derrick 2026-10-29 6:59 AM CT "Ok let's keep the b2 setup and make it default"): a byte-identical copy of runs\terrace_dom_q5guide_20261028_s51083007\request.api.json, sha256 8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e, 20072 B, 26 nodes = beta7 int8HQ, euler/simple, 8 steps full schedule + pass 2 beta/3/denoise 0.4, shift 12/3, VSA keep_percent 10, AddGuide frame 0 on both passes, ref_image_size max, 384x672 -> LatentUpscaler3D x2 -> 768x1344, 243 frames, 24 fps. Do not change any of those.
     f. Render: C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_graph_job.py <run_dir> <id> --frames 243 (the number must equal c0.length in the graph you copied; the B2 default renders 243 f = 10.125 s at ~240 s GPU. runs gpu_guard and gpu lock).
     g. Finish: commit once in each repo touched and append one line to notes\progress.md. Then stop.
   - Script reuse: reuse the existing scripts, never repeat steps by hand - notes\p15_driver.py writer stage is THE prompt writer (Swift captions -> Swift writes, h3-prompting rules; defaults --writer w2 --mode capswift; notes\bk26_writer_batch.py is bake-off history), p15_driver.py judge stage is the review (qwen3vl_judge + Z zoom via C:\AI\community\judge\vlm_variants.py, flag-only; bk26_judge_* are history); render/QC tools C:\AI\community\scripts\run_graph_job.py, verify_cell.py, prompt_stats.py, review_pack.py, finalize_encode.py. One manifest drives them. Prompt rules live in C:\AI\community\skills\h3-prompting\SKILL.md (cite its R numbers); render dials in C:\AI\community\skills\h3-hc-render\SKILL.md.

2. Research rules: at most one fetch per URL, no retries. If saved in notes\web, reuse it. Fetch -> python C:\AI\community\scripts\check_web_saves.py -> git add notes\web && git commit in same iteration. Reading ComfyUI\custom_nodes with read tool is denied.


### GPU lock and render window (moved from PROMPT.md rule 99999999)
GPU lock: renders and start-image captioning go through llama-swap ComfyUI swap, ONE job at a time. Queue only via C:\AI\community\scripts\run_graph_job.py (comm.guard_ok enforced before POST). Gate before queuing: C:\AI\director\scripts\gpu_guard.ps1 rc 0 = IDLE, and python C:\AI\community\scripts\comfy_ctl.py status. Driver busy guard: while C:\AI\locks\gpu-render.lock is held by a test driver, Forge in interactive chats replies that a test is running and does not load models, render, or run GPU/heavy work; read-only questions are fine. While render runs: no second job, no ComfyUI restart, no llama-swap load/unload/upstream, no LLM requests (run_graph_job.py holds C:/AI/locks gpu-render lock; comfyui_auto exclusive main group ttl: 300). Client stall (exit 6) collects clip from ComfyUI\output\community\<id>\, never re-render. KEEP is Derrick's alone; no vision model judges, scores or picks rendered explicit output.
