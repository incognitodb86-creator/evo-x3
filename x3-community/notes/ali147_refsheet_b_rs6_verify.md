# ALI-147 RS6 - REFSHEET_B (arm 5b) render verification (Forge, 2026-10-22, read-only)

Task: `- [ ] RS6 Render REFSHEET_B (GPU). Check: as RS4 for ali147_pool_refsheet_b_s51080000, plus
sbs_refsheet_refsheetb.mp4 and stills at frame 0 (opening, since chunk 1 changed).`
The request half was written last iteration (notes\ali147_refsheet_b_rs6_request.md, idcheck
notes\ali147_refsheet_b_rs6_idcheck.py). This iteration = verification only. No GPU / ComfyUI /
llama-swap / Strata call, no render, no ffmpeg by Forge.

## 1. Harness result - ok
`C:\AI\community\p7\jobs\ali147_pool_refsheet_b_s51080000.result.json`:
`"ok": true`, `"rc": 0`, `"note": "run_graph_job rc=0 (ok)"`, started 2026-10-22T18:54:34,
finished 2026-10-22T19:11:34, wall_min 17; budget_used_min 276.3 < budget_cap_min 390.
`ali147_pool_refsheet_b_s51080000.err.out` = 0 bytes. One attempt, no redo, no STUCK.

## 2. status.log (runs\ali147_pool_refsheet_b_s51080000\status.log) - quoted, CT
```
2026-10-22 18:54:34 CT UNLOAD LLM coding_swift15_iq3s_esp
2026-10-22 18:55:15 CT JOB start ali147_pool_refsheet_b_s51080000 prompt_id=da83b45e-32c7-4e15-8c7b-cd9b16dc3f6b
2026-10-22 19:11:33 CT JOB end ali147_pool_refsheet_b_s51080000 ok secs=978.1 file=C:\AI\community\runs\ali147_pool_refsheet_b_s51080000\ali147_pool_refsheet_b_s51080000.mp4
2026-10-22 19:11:33 CT OBJECTIVE ok ali147_pool_refsheet_b_s51080000 frames=481 audio=True dur=20.042 bytes=5705213 contact=C:\AI\community\runs\ali147_pool_refsheet_b_s51080000\ali147_pool_refsheet_b_s51080000_stills_contact.png
2026-10-22 19:11:34 CT UNLOAD comfyui_auto (POST /api/models/unload)
```
`JOB start` + `JOB end ... ok` + `OBJECTIVE ok` present. grep of `error|SKIP|redo|STUCK|clip_skip`
(case-insensitive) over status.log = **no matches** -> no JOB error, no CLIP_SKIP.
The LLM was unloaded before the job (18:54:34) and ComfyUI unloaded after (19:11:34) - ALI-154 form.

## 3. objective.json - ok
`"ok": true`, one attempt: frames 481, 768x1344, fps 24/1, audio true, duration 20.041688 s,
bytes 5,705,213, `secs` 978.1, `blackfreeze: []` (the harness blackdetect + freezedetect found no
black and no frozen frames = the RS4 "no black or frozen frames" item).
Contact sheet: `ali147_pool_refsheet_b_s51080000_stills_contact.png` 1,773,478 B, PIL (1816, 900),
SHA256 def7cbe01c4dcb1319585f639f908d7ad1fce030cbc149653996b9e11ab8832d.
Per run_graph_job.py:45-52 its windows are t=8.5-11.5 s + 18.5-20.0 s = frames 204-276 and
444/456/468/480 (it keeps t <= dur-0.05), so it covers 230/243/256/480 but never frame 0.
`<id>.mp4.json`: `"label": "METHOD_ONLY"`, `"plan": "ALI-147"`, `"attempt": 0`,
comfy_output `...\ComfyUI\output\community\ali147_pool_refsheet_b_s51080000\ali147_pool_refsheet_b_s51080000_00001_.mp4`.

## 4. My own ffprobe -count_packets (the AGENTS.md command) - matches
video: `768,1344,24/1,24/1,481` -> 481 packets, 768x1344, r_frame_rate 24/1, avg_frame_rate 24/1.
audio: `aac,32000,2,20.041688` -> audio stream present, 32 kHz 2ch.

## 5. Graph provenance - the graph that rendered is RS5's, unchanged
Plain `cmp` of `request.api.json` vs `ali147_pool_refsheet_b_s51080000.api.json` = **no output**
(byte-identical, 12,144 B, 26 nodes). `graph_diff.txt` (8,211 B, RS5) stays the only 4 deltas vs
REFSHEET: c0 prompt (subject_definitions block only, tail from `summary:` byte-identical),
c0 `ref_image_size` match -> max, c0 `ref_images.ref_image_2` = ["sheet", 0] (RS3's sheet node
reused, no new node), save `filename_prefix` -> this id. 24/26 nodes byte-identical, c1 untouched.

## 6. Re-run of the arm precheck (notes\ali147_refsheet_b_rs6_precheck.py) - graph checks PASS
`nodes 26 parent_nodes 26 bytes 12144`; comm.guard_ok PASS on c0 (3,951 chars, sha256
afa3cf3e9c12ffad948ca919b2e9ff747eb8179ced216ce4db91117550131d08) and c1 (2,569 chars, sha256
49c94ba7759859e26af01dff17230b80a834fa4b1ff57bcaac332cf40c655045); node key set identical to
REFSHEET, differing nodes exactly `['c0','save']`; c0 class MiniMaxH3ReferenceToVideo with
ref_image_1 = ["img",0] (start still), ref_image_2 = ["sheet",0] (the sheet), no ref_image_3,
`ref_image_size` "max", length 243, 768x1344, vae/audio_vae/clip wired; prompt binds
`<Picture 1>` = start still and `<Picture 2>` = the sheet; c1 byte-identical to REFSHEET;
seed 51080000, steps 10 both schedulers, euler/simple, shift 10/3, fps 24, win1 238/22 -> 481,
filename_prefix = this id.
LoadImage strings both resolve inside ComfyUI\input (no `Invalid file path`):
`community/POOL_768x1344.png` 1,354,030 B SHA256 9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075
= the graphs' node image; `community/RS016_portrait_1152x2016.png` 2,314,891 B SHA256
da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a = RS1's approved sheet
(certutil, independent of the script).
The script's last five lines are its **pre-request "id free"** checks (no status.log / objective.json
/ mp4 / .api.json / result.json) - they now report FAIL *because the render happened*, which is the
expected post-render state, not a failure.

## 7. sha256 of the output
`ali147_pool_refsheet_b_s51080000.mp4` 5,705,213 B
SHA256 `7ce70a33cda1aed836851fb02d1ea3cbfd3511b77d80b71387f3d63f3c339415` (certutil SHA256).
For comparison: REFSHEET 5,733,637 B / 4a467b1f4f9f553c6efe51461bdfca535d9bbbcc21c89864db0eee52493b5223.

## 8. Render seconds (numbers only, no judgement)
| Arm | objective.json secs | delta vs REFSHEET_B |
|---|---|---|
| REFSHEET_B (this arm, sheet on chunk 1 too) | 978.1 | - |
| REFSHEET (direct control, sheet on chunk 2 only) | 902.7 | +75.4 s / +8.35% |
| FIX1 (text-only chunk 2) | 857.5 | +120.6 s / +14.06% |
| CTRL (base graph) | 809.7 | +168.4 s / +20.80% |
Bytes 5,705,213 vs REFSHEET 5,733,637 = -28,424 B / -0.50%. Recorded as numbers; no keeper claim.

## 9. Not Forge's (per the TASKS.md sbs rule, Max Architect 2026-10-22)
`sbs_refsheet_refsheetb.mp4` (run_graph_job.py has no hstack path) and the frame-0 stills (the
harness sheet never covers frame 0, and chunk 1 is the changed node here, so frame 0 is exactly what
Max wants by eye) = **sbs/stills pending Max**. `find C:/AI/community/runs -name sbs_*` today returns
only `ali147_pool_refsheet_s51080000/sbs_fix1_refsheet.mp4` (19,649,768 B, made by Max 18:34).
No frame-0 still in the arm folder. Per the rule: every objective check passes, so the line is
ticked with "sbs/stills pending Max" written in the result. Not a block, no redo requested.

METHOD_ONLY. No vision judge called. No judging of explicit content. KEEP is Derrick's only.
