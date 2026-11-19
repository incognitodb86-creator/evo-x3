# ALI-147 RS4 - REFSHEET render verification (read-only, 2026-10-22 ~18:30 CT, Forge)

Task: TASKS.md `RS4 Render REFSHEET (GPU; unload the LLM first, ALI-154)`. The render was requested by the previous
iteration (notes\ali147_refsheet_rs4_request.md) and the harness ran it after that exit. This file records only the
verification half - Forge never runs GPU work, ffmpeg, run_graph_job.py or the vision judge. Everything below is
quoted from harness files plus my own read-only ffprobe / certutil / cmp runs. METHOD_ONLY; no judging of content.

## 1. Harness result - ok=true, single attempt, no redo, no STUCK

`C:\AI\community\p7\jobs\ali147_pool_refsheet_s51080000.result.json` (mtime 2026-10-22 18:22):

```
"started": "2026-10-22T18:06:30", "rc": 0, "ok": true, "kind": "graph",
"note": "run_graph_job rc=0 (ok)", "finished": "2026-10-22T18:22:13", "wall_min": 15.7,
"budget_used_min": 259.3, "budget_cap_min": 390
```

outputs = status.log, objective.json, ali147_pool_refsheet_s51080000.mp4, ali147_pool_refsheet_s51080000_stills_contact.png.

## 2. status.log lines (runs\ali147_pool_refsheet_s51080000\status.log, 635 B, mtime 18:22)

```
2026-10-22 18:06:30 CT UNLOAD LLM coding_swift15_iq3s_esp
2026-10-22 18:07:10 CT JOB start ali147_pool_refsheet_s51080000 prompt_id=9c0338a3-8603-4647-92bf-18bbc1a67544
2026-10-22 18:22:13 CT JOB end ali147_pool_refsheet_s51080000 ok secs=902.7 file=C:\AI\community\runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000.mp4
2026-10-22 18:22:13 CT OBJECTIVE ok ali147_pool_refsheet_s51080000 frames=481 audio=True dur=20.042 bytes=5733637 contact=C:\AI\community\runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000_stills_contact.png
2026-10-22 18:22:13 CT UNLOAD comfyui_auto (POST /api/models/unload)
```

- `JOB start` + `JOB end ... ok` present for the arm tag; the LLM unload (ALI-154) is the first line, ComfyUI unload the last.
- "no JOB error, no CLIP_SKIP": grep of `JOB error|CLIP_SKIP|error|Error|SKIP|redo|STUCK` over status.log = **No matches found**.
  `p7\jobs\ali147_pool_refsheet_s51080000.err.out` = 0 bytes; the .out is byte-for-byte the same five lines.
- objective.json `attempts` has exactly **one** entry (secs 902.7) -> no objective redo, no STUCK, no "id already used" refusal.

## 3. objective.json (harness) - all four check fields pass

```
"frames": 481, "w": 768, "h": 1344, "fps": "24/1", "audio": true,
"duration": 20.041688, "bytes": 5733637, "secs": 902.7, "blackfreeze": []
"ok": true
```

`blackfreeze: []` is the harness's own blackdetect + freezedetect pass (run_graph_job.py:42-44,
`blackdetect=d=1.0:pix_th=0.10,freezedetect=n=-60dB:d=2`) = **no black or frozen frames**.

## 4. My independent ffprobe (not the harness's)

```
ffprobe -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,avg_frame_rate,width,height,codec_name
  -> h264,768,1344,24/1,24/1,481
ffprobe -show_entries stream=index,codec_type,codec_name,sample_rate,channels,duration
  -> 0,h264,video,20.041667
     1,aac,audio,32000,2,20.041688
```

481 video packets at 768x1344, 24/1 fps (avg 24/1), audio stream present (aac 32000 Hz 2ch). Matches objective.json.

## 5. sha256 of the output (certutil.exe -hashfile ... SHA256)

`C:\AI\community\runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000.mp4` (5,733,637 B)
= `4a467b1f4f9f553c6efe51461bdfca535d9bbbcc21c89864db0eee52493b5223`

## 6. The graph that rendered IS RS3's graph

`cmp runs\ali147_pool_refsheet_s51080000\request.api.json runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000.api.json`
= **no output = byte-identical** (11,424 B, 26 nodes). The harness submitted exactly the RS3 graph.

`graph_diff.txt` (git diff --no-index vs FIX1) still shows only the RS3 changes: c1 `prompt` gets the 2-line
`subject_definitions` block, c1 `ref_image_size` "match" -> "max", c1 `ref_images.ref_image_1` `img` -> `sheet`,
the new `sheet` LoadImage node ("community/RS016_portrait_1152x2016.png") and the SaveVideo `filename_prefix`.
Chunk 1 (c0), seed 51080000, 243/238/22, steps 10, 768x1344, fps 24 are untouched.

The sheet resolved at render time (no "Invalid file path"), and I re-verified the file the node points at:
`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png` SHA256 =
`da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a` = RS1's required hash. The start still node
`img` (community/POOL_768x1344.png, 9cf9ff95...) is unchanged, so the arm's only variables are the sheet + ref_image_size + the c1 subject block.

## 7. Render seconds vs the seg-1 baselines (numbers only, no quality claim)

| Arm | objective.json `secs` | 481 frames |
|---|---|---|
| CTRL | 809.7 s | yes |
| FIX1 (the arm's own baseline) | 857.5 s | yes |
| FIX5 (8 steps) | 706.8 s | yes |
| **REFSHEET** | **902.7 s** | yes |

REFSHEET - FIX1 = **+45.2 s (+5.27 %)**; REFSHEET - CTRL = +93.0 s (+11.5 %). Wall clock 15.7 min (harness), GPU-side 902.7 s.

## 8. Contact sheet - what it actually covers (derived from run_graph_job.py:45-52, not from viewing it)

`contact_sheet()` takes stills every 0.5 s in +-1.5 s windows around 0:10/0:20/0:30/0:40/0:50, keeping only
`t <= duration-0.05`. For this clip (duration 20.041688 s) that is t = 8.5-11.5 s and t = 18.5, 19.0, 19.5, 20.0 s
= frames 204-276 and 444/456/468/480, tiled 7x2.

- Requested frames **230, 243, 256** (the 0:10 chunk-2 join, at 10.125 s) and **480** (the segment end) ARE inside that sheet.
- Requested **frame 0** is NOT in it (no window reaches t=0), and the 0:30/0:40/0:50 windows fall past this 20.04 s clip.
- File: `C:\AI\community\runs\ali147_pool_refsheet_s51080000\ali147_pool_refsheet_s51080000_stills_contact.png` (1,721,371 B, mtime 18:22).
- Image reading is disabled in this model, so the sheet is recorded by path/size/code-derived coverage, never viewed. No vision judge was called (superseded 2026-10-22).

## 9. Two RS4 check items that do NOT exist, and are not Forge's to make

1. `sbs_fix1_refsheet.mp4` (hstack FIX1 | REFSHEET, labels on) - **not produced**: `grep hstack` over
   `C:\AI\community\scripts\run_graph_job.py` = no match; `find C:\AI\community\runs -name sbs_*` = 0 files, so no
   ALI-147 arm has one. Making it needs an ffmpeg hstack + drawtext render, and `runs\*.mp4` is outside Forge's
   writable files (PROMPT.md allows only TASKS.md, p7\JOB_REQUEST.json, request.api.json / PROOF.md / fairness.txt,
   notes\*, one AGENTS.md line; ffmpeg is allowed only as a CPU dry run into a scratch folder for a harness fix).
2. A still at **frame 0** - outside the harness contact-sheet windows (item 8), and a still is a rendered asset, same restriction.

Both are Max/harness outputs (the plan's Proof section assigns the side-by-sides to the box executor, "Files
`sbs_<arm>.mp4` in each arm folder"). Forge did not run ffmpeg. RS4 is therefore marked `[!]` + BLOCKED: every
objective item in its check passes and is recorded above; the two file-producing items need Max/Derrick.

## 10. Governance

METHOD_ONLY. No quality judgment, no A/B claim, no keeper. No vision judge, no scene score. **KEEP is Derrick's only.**
No install, no download, no delete, no copy, no GPU/ComfyUI/llama-swap/Strata call, no render, no ffmpeg by Forge.
