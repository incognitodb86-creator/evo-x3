---
name: h3-hc-render
description: Wire, gate, request and verify a MiniMax-H3 / 10Eros-Max (beta7 int8HQ, default since 2026-10-28) ComfyUI clip for the Forge Ralph loop - graph keys, reference-image wiring, frame/canvas math and the objective proof checks. Use when building a graph, requesting a render or checking a rendered clip.
---

# H3 hardcore render

R2. Render rules (adults only, no real likeness, guard_ok) live in C:\AI\render\AGENTS.md; run render work from C:\AI\render.

Work the loop in this order. One job per pass. Never mix a request pass with a proof pass.

## 0. When to use this skill

- A render-request task in this batch: writing an arm graph, re-requesting a dead clip, choosing length/canvas, counting jobs, spending GPU minutes.
- Verifying a rendered clip (frame count, fps, audio, seams, hashes) or deciding whether a pass may submit at all.
- Any MiniMaxH3 / Continuum 3.10.2 job: the numbers below are the ones that already burned real jobs.

## 1. Read the state before anything

- `tail -n 15 C:/Users/derek/5slock/ralph-community/logs/ralph.log`.
- GPU state: `python C:/AI/community/scripts/comfy_ctl.py status`. Never stop/restart
  ComfyUI while a render runs; after every start/restart continue only if `comfy_ok=True`.

## 2. Graph wiring (the part that has actually broken)

- Request graph (default; Derrick 2026-10-30 "Only make the B2 template file the default"): build it with
  `C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/make_b2_request.py` from
  `C:/AI/community/templates/b2.api.json` (see `templates/b2.README.md`). It patches only the per-run fields
  `c0.prompt`, `noise.noise_seed`, `img.image`, `save.filename_prefix` and `c0.length` (frames, set by the plan; the
  template's 124 is only an example, not part of B2). B2 itself is locked (decision 2026-10-30-keep-b2-render-settings):
  beta7 int8HQ unet, qwen3vl nvfp4_awq TE, two-pass 384x672 -> `minimax_h3_latent_upscaler_3d_conv_v1_bf16` 2x ->
  768x1344 portrait, 24 fps, euler/simple 8 steps, pass 2 `beta`/3/denoise 0.4, shift 12/3, ref_image_size max,
  `MiniMaxH3AddGuide` frame 0 on both passes (ag0, ag1), `ref_images.ref_image_1` only. `--frames` on
  run_queue.py must equal c0.length; the frame check only confirms the clip came out at that length.
  Superseded for new runs: copying old run graphs, `p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json`
  (c0.length 243) and `runs/terrace_retest_v2_20261030/_build_b2_arms.py`; old ids keep their own graphs in `runs/`.
  The 3-ref/1344x768 paragraphs below predate B2 and apply only when a brief asks for that shape.
- Model `10Eros_Max_h3_8stepTURBO_beta7_int8HQ`, euler/simple, 8 steps, shift 12 (video) / 3 (audio), VSA 90% sparse, no SLA/cache/spectrum with reference (beta 7 settings from Derek's 2026-10-28 brief; beta 6 is deleted). Steps live in
  `s0_sched`/`s1_sched`, sampler in `ksel`, shift in `m_shift`; there is NO cfg key in these graphs at all.
- beta7 background flicker (TenStrip HF 10Eros-Max #76/#79): mitigation = the 2-pass B2 graph we already use; watch #79.
- **Pre-B2 / 1344x768 only (B2 uses ref_image_1 + two AddGuides): references were 3 slots on c0 AND c1.**
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

- Canvas 768x1344 portrait (B2), 24 fps. Length is a per-run choice from the plan; H3 grid `(frames - 5) % 17 == 0`
  (124 = 17*7+5 = 5.17 s; 243 = 17*14+5 = 10.125 s). Pre-B2 continuation math: c0 124 + extension 119 = 243
  (window overlap 22; c1 141 generated / 22 hidden). 481 f = 20 s is the shape Derrick rejected. `duration = round(frames/24, 6)`.
  Sources: `notes/hc_redo_research_20261023.md` (row table), `notes/ali147_summary.md`.

## 4. Static self-check, then request

- Static check: `run_graph_job.static_check` (runs inside run_queue.py before submit; schema parsed from
  `comfy_extras/nodes_minimax_h3.py`, no network). Every builder gets a **self-destruct probe**: restore the old
  wiring in a clone and require every detector to fire there and none on the real graph. A green check that cannot
  fail is worthless.
- To re-request a dead clip, clone its rendered `ok=True` sibling graph and change only the per-clip keys.
- One seed per clip. Never request a quality redo (harness redos = same seed, then seed+1).
- Single clip = a batch of one: `run_queue.py --run-dir <run_dir> --frames <n> --detach`. run_graph_job.py is an internal helper run_queue imports; never run it directly.
- "Pick an image" (Derrick): pick from `//NAS4CBE37.local/home/AlienPc-approved/approved_characters/INDEX.csv`; a quick check for stills not used recently is OK (Derrick 2:52 PM CT: "eh i am ok with them searching"). Seed default: a random int made in code (`random.randint(1, 2**31-1)`); never grep runs for uniqueness.
- Search narrowly: use `rg` inside the folder the brief names (notes, templates, scripts, or one run dir); never `grep -r` or `find` across C:\AI\community, C:\ or /c. Set PYTHONIOENCODING=utf-8 when printing workflow text.
- For node inputs, `rg <Node> notes\objinfo\NODE_INDEX.txt` or read NODE_INPUTS.md; never parse custom-node Python source.
- Prompt: use Example 1 for structure only (beat order, clause shape), not its content or tone; write the scene from what Derrick asked for. Example 1 is in `skills/h3-prompting/references/worked-examples.md`; for length/stats reuse `scripts/prompt_stats.py`. No per-clip check scripts.

## 5. Proof (next pass, objective only; no vision model judges, scores or picks rendered explicit output; Derrick gives the only KEEP)

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
`notes/ali163_hc_bq1d_objective.json`, `notes/forge-learnings.md`, `C:/Users/derek/5slock/AGENTS.md` "## Test".

## 6. Stock render path (moved verbatim from PROMPT.md by U5, 2026-10-29)
Steps a-g for one render item, then script reuse and research rules:
   - For a render item (stock path):
     a. Pick one approved, never-animated still with C:\AI\community\notes\hc_pick_scan_20261023.py (unless named in MAX). GI063 render hold is RELEASED (Derrick 2026-10-27 9:09 AM CT — wrongly flagged by wrong model; do NOT treat GI063 as hold; keep youth guard on GI063).
     b. Caption once with your own model (coding_swift15_iq3s_esp, the ralph.ps1 default): one ask, one image. Vision models exist and stay: the Forge vision model Swift via mmproj, the W7 and W8 writer mmproj files, and JoyCaption.
     c. Write one natural-language H3 prompt from that caption, following h3-prompting (no word cap; long, literal, in time order).
     d. Check: C:\AI\director\.venv\Scripts\python.exe -m pytest -q C:\AI\community\scripts\tests\test_p6_review.py C:\AI\community\scripts\tests\test_guard_scope.py. comm.guard_ok also runs inside run_graph_job.py before /prompt POST; never loosen either.
     e. Build graph: C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\make_b2_request.py --arm-dir <run_dir> --prompt-file <txt> --seed <n> --image <ComfyUI input path> --prefix <sub/name> [--frames <n>] writes <run_dir>\request.api.json from C:\AI\community\templates\b2.api.json (the B2 recipe, Derrick decision 2026-10-30; details in templates\b2.README.md). Only prompt, seed, start image, filename prefix and frames change; everything else is locked.
     f. Render (one clip or a batch): C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py --run-dir <run_dir> --frames <n> --detach (AGENTS.md Render; n must equal c0.length in the request; takes gpu-render.lock). run_graph_job.py is a helper run_queue.py imports; never run it directly.
        Frames: the plan sets the frame count per run (e.g. 124 for the terrace retest); c0.length and --frames must be equal.
     g. Finish: commit once in each repo touched and append one line to notes\progress.md. Then stop.
   - Script reuse: reuse the existing scripts, never repeat steps by hand - render/QC tools C:\AI\community\scripts\make_b2_request.py, run_queue.py, verify_cell.py, prompt_stats.py, review_pack.py, finalize_encode.py. Prompt rules live in C:\AI\community\skills\h3-prompting\SKILL.md (cite its R numbers); render dials in C:\AI\community\skills\h3-hc-render\SKILL.md. Review is objective checks only; Derrick gives the only KEEP.

2. Research rules: at most one fetch per URL, no retries. If saved in notes\web, reuse it. Fetch -> python C:\AI\community\scripts\check_web_saves.py -> git add notes\web && git commit in same iteration. Reading ComfyUI\custom_nodes with read tool is denied.


### GPU lock and render window (moved from PROMPT.md rule 99999999)
GPU lock: renders and start-image captioning go through llama-swap ComfyUI swap, ONE job at a time. Every render, one clip or a batch: run_queue.py --detach (AGENTS.md Render). It enforces comm.guard_ok before POST and take the gpu-render lock (rc 7 = busy); the lock decides, there is no gpu_guard step. State: python C:\AI\community\scripts\comfy_ctl.py status. Driver busy guard: while C:\AI\locks\gpu-render.lock is held by a test driver, Forge in interactive chats replies that a test is running and does not load models, render, or run GPU/heavy work; read-only questions are fine. While render runs: no second job, no ComfyUI restart, no llama-swap load/unload/upstream, no LLM requests (run_queue.py holds C:/AI/locks gpu-render lock; comfyui_auto exclusive main group ttl: 300). Client stall (exit 6) collects clip from ComfyUI\output\community\<id>\, never re-render. KEEP is Derrick's alone; no vision model judges, scores or picks rendered explicit output.
