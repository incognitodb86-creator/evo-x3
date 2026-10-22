# ALI-147 RS6 - REFSHEET_B requested (no render by Forge) - 2026-10-22

Task: `- [ ] RS6 Render REFSHEET_B (GPU). Check: as RS4 for ali147_pool_refsheet_b_s51080000, plus
sbs_refsheet_refsheetb.mp4 and stills at frame 0 (opening, since chunk 1 changed).`

Per PROMPT.md Forge may only REQUEST a job; `scripts\run_graph_job.py` is run by the harness after this
iteration exits, so the render half is verified by the next iteration and the line stays `- [ ]`.

## What was written this iteration
- `C:\AI\community\p7\JOB_REQUEST.json` = `{"jobs": [{"id": "ali147_pool_refsheet_b_s51080000", "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}]}`
  - `python -m json.tool` prints exactly one job with only id / kind / frames / frames_tol / minutes. Nothing else in the file.
  - The file was absent before this write (the harness consumed the RS4 request at 18:05 -> `p7\jobs\request_iter01.json`), so there is no stale request.
- Pre-request check script: `C:\AI\community\notes\ali147_refsheet_b_rs6_precheck.py` (read-only, CPU only; `python -m py_compile` clean; prints `ALL CHECKS PASS`).

## Pre-request checks (read-only, from RS5's graph, no GPU / ComfyUI / llama-swap call)
`runs\ali147_pool_refsheet_b_s51080000\request.api.json` = 12,144 B, 26 nodes, parses under `python -m json.tool`.
- Adults-only guard: the harness's own `comm.guard_ok` (scripts\comm.py, imported, not edited) **passes** on both prompt nodes: c0 3,951 chars sha256 `afa3cf3e9c12ffad948ca919b2e9ff747eb8179ced216ce4db91117550131d08`, c1 2,569 chars sha256 `49c94ba7759859e26af01dff17230b80a834fa4b1ff57bcaac332cf40c655045` (c1 = RS3's, unchanged).
- Fairness vs the parent arm REFSHEET (`ali147_pool_refsheet_s51080000\request.api.json`): node key set **identical** (no new node), and exactly **two** nodes differ - `c0` (the one change) and `save` (filename_prefix). 24/26 nodes byte-identical, including all model/VAE/CLIP loaders, m_shift, m_vsa, schedulers, ksel, win1, tail guide, mkvid.
- `c0` = `MiniMaxH3ReferenceToVideo` with `ref_images.ref_image_1 = ["img",0]` (the start still), `ref_images.ref_image_2 = ["sheet",0]` (RS3's sheet node reused, no new LoadImage), no `ref_image_3`, `ref_image_size = "max"`, `length 243`, `768x1344`, `vae=vvae`, `audio_vae=avae`, `clip=clip`.
- `c0` prompt: the added text is only the `subject_definitions:` block, binding `<Picture 1>` = the start still and `<Picture 2>` = the sheet; the whole tail from `summary:` on is **byte-identical** to REFSHEET's c0.
- `c1` (chunk 2) is byte-identical to RS3 (sheet as its `ref_image_1`, `max`, length from `win1`), and has no `ref_image_2` - arm 5b adds the sheet to chunk 1 only.
- Both LoadImage strings resolve inside `ComfyUI\input` (no `ValueError: Invalid file path`), verified by path + sha256:
  - `img` = `community/POOL_768x1344.png` 1,354,030 B sha256 `9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075` (the graphs' start-still image, per RS0 item 3).
  - `sheet` = `community/RS016_portrait_1152x2016.png` 2,314,891 B sha256 `da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a` = RS1's sheet.
- Held-equal settings: seed `noise_seed 51080000`; steps 10 on both schedulers; sampler euler; scheduler simple; shift_video 10 / shift_audio 3; fps 24; `win1` extension_frames 238 / overlap_frames 22 -> frame target 243 + 238 - 22 + 22 = **481**. The only setting delta vs the parent arm is `save.filename_prefix` -> `community/ali147_pool_refsheet_b_s51080000/ali147_pool_refsheet_b_s51080000`.
- Job id is free: the arm folder holds only `request.api.json` + `graph_diff.txt` (8,211 B, the 4 RS5 deltas) - no `status.log`, `objective.json`, mp4 or `.api.json`; no `p7\jobs\ali147_pool_refsheet_b_s51080000.result.json`. So the failed-job move rule (`*.failed-20261022`) does not apply.

## Baselines carried to the verification iteration (RS4's numbers, from the real files)
- REFSHEET (chunk-2-only arm, the direct control for this arm): `status.log` `JOB start 2026-10-22 18:07:10 CT` / `JOB end ... ok secs=902.7` 18:22:13 CT; objective.json 481 frames / 768x1344 / 24/1 / audio true / 20.041688 s / 5,733,637 B / blackfreeze []; mp4 sha256 `4a467b1f4f9f553c6efe51461bdfca535d9bbbcc21c89864db0eee52493b5223`. FIX1 seg-1 render secs 857.5, CTRL 809.7.
- The harness writes `runs\<id>\<id>.api.json`: `cmp` it against `request.api.json` (no output = the graph that rendered is RS5's).

## For Max (not Forge's files, same as RS4)
`run_graph_job.py` has no hstack path, so `sbs_refsheet_refsheetb.mp4` and any fixed frame-0 still are
harness/Max files (also outside Forge's writable list): its only contact sheet is 0.5 s steps in the
+-1.5 s windows around 0:10-0:50 -> for a 481-frame / 20.04 s clip that is frames 204-276 and
444/456/468/480, which never includes frame 0. Since chunk 1 changed in this arm, the frame-0 opening
stills matter and only Max can produce them. Every other RS6 item (status.log lines, ffprobe
481/768x1344/24/audio, black/frozen via the harness blackdetect+freezedetect, sha256, render secs) is
verifiable next iteration from status.log + objective.json + ffprobe + certutil.

METHOD_ONLY. KEEP is Derrick's only. No render, no ffmpeg, no GPU / ComfyUI / llama-swap / Strata call by Forge.
