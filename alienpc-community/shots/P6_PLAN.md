# P6 shot lists (ALI-128) - arms x shots x seeds

Checked by the Ralph loop (task C5) on 2026-10-20. Files in scope: `C:\AI\community\shots\p6_pairs.json` and `C:\AI\community\shots\p6_1min_community.json`.
Both parse: `python -m json.tool` exits 0 on each. Every requirement in C5 was already met, so **neither file was edited** and no `.bak-20261020-ralph` copy was made for them (nothing to roll back). No image file was opened and no new image was added.
Runner that consumes them: `C:\AI\community\scripts\p6.py` -> `batch_queue.py p6_pairs.json p6_pairs --no-stitch`, then `batch_queue.py p6_1min_community.json p6_1min_community` (stitch + one rclone copy), then `sy_1min.py`, then `llama-swap /unload`. Nothing has been rendered yet - this loop does no GPU jobs.

## 1. p6_pairs.json - D1 x D2 = 4 arms, same shots, same seeds, finals

3 shots x 4 arms = 12 jobs. Every row is 768x1344, steps 10 (finals per D3/D10), 5 s, no continuation, no LoRA, VSA on, shift 10 video / 3 audio, euler/simple (all from `comm.py build`, `comm.py:110`).

| shot | start image (approved key) | seed | i2v short | i2v long | ref2va short | ref2va long |
|---|---|---|---|---|---|---|
| S1 courtyard, auburn hair | FD006 | 51070001 | `p6_S1_i2v_short` | `p6_S1_i2v_long_i2v` | `p6_S1_r2v_short` | `p6_S1_r2v_long_r2v` |
| S2 black studio, metallic top | FD003 | 51070002 | `p6_S2_i2v_short` | `p6_S2_i2v_long_i2v` | `p6_S2_r2v_short` | `p6_S2_r2v_long_r2v` |
| S3 penthouse balcony, mesh bikini | D15 | 51070003 | `p6_S3_i2v_short` | `p6_S3_i2v_long_i2v` | `p6_S3_r2v_short` | `p6_S3_r2v_long_r2v` |

What differs inside a shot group (nothing else):

- `mode: "i2v"` -> `MiniMaxH3ImageToVideo` with the still as first frame (`comm.py:103`); `mode: "r2v"` -> `MiniMaxH3ReferenceToVideo` with the still as identity reference (`comm.py:106`). Both graphs decode audio, so the i2v arm is I2V(A) as D1 (ALI-116) worded it.
- `arm: "short"` -> 60-120 words per 5 s, `arm: "long_i2v"` -> 150-250 per 5 s, `arm: "long_r2v"` -> 350-500 (`prompt_writer.py:14-17`; the 350-500 figure is the guide's own generation-task length, `guides/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md:242`). Writer tolerance 0.85x-1.15x with 2 retries.
- Same shot = same `image`, same `image_note`, same `beat`, same `seed`, so the only variables are the graph and the prompt length - which is what D1 x D2 asks for.
- The seeds 51070001-51070003 are the same seeds as the 576x1024 / 8-step drafts in `shots/p5_3shot.json`, so any draft clip can be re-run as a final on the same seed.

## 2. p6_1min_community.json - about 60 s, 10 s chunks, continuation only where the beat flows

3 segments, each one graph = 1 base chunk (10 s) + 1 continuation chunk (10 s) = 6 chunks of 10 s, inside the 10-15 s window of D4 (ALI-120). All three use `mode: "r2v"` (identity reference only, so the scene may change) and `arm: "long_r2v"` for the base chunk; `batch_queue.py:13` switches chunk 2 to `long_cont` = 150-250 words per 5 s (300-500 for a 10 s chunk), which is the T2VA form in the base guide - correct, because a continuation carries no picture.

| segment | job id | start image | seed | chunk 1 (new shot, cut written in the prompt) | chunk 2 (continuation, same flowing take) |
|---|---|---|---|---|---|
| 1 balcony | `p6_1min_seg1` | D15 | 51080000 | bikini top strap untied, top falls, eye contact | turns to the window light, hands down over breasts and stomach to hips, looks back over shoulder |
| 2 living room | `p6_1min_seg2` | D15 | 51080001 | "Cut to the dark living room:" walks barefoot to the window, city lights | back against the glass, arms overhead, arch, smiles |
| 3 sofa | `p6_1min_seg3` | D15 | 51080002 | "Cut to a white leather sofa:" slides the bottoms down and drops them | rolls onto her side nude, props head on one hand, laughs, blows a kiss |

Length arithmetic from `comm.py frames_for` (`comm.py:60`) and `batch_queue.graph_for`: base `frames_for(10)` = 243 frames = 10.125 s; extension `frames_for(10) - 5` = 238 frames = 9.917 s; P4 measured 481 frames / 20.04 s for exactly that shape. 3 x 481 = 1443 frames = 60.1 s after the ffmpeg concat. So the file is a ~60 s video, as asked.

The comparison arm is not in this file: `sy_1min.py` builds the current Switchyard path from `shots/p6_1min_beats.json` (6 beats, each split into two 5 s halves = 12 cells, seeds 51090000-51090011) and stages the same D15 still at 768x1344. The two one-minute paths therefore share the character and the start image but not the seeds, since the graphs are unrelated.

## 3. Facts to know before P6 runs (no judgement of picture quality - Derrick watches)

- **Anti-Burn is off** on all three one-minute segments (`"antiburn": null`). D20 (ALI-141) approved the LoRA only for the P4 test, and P4 reported ok/timing only, so the pick is Derrick's. To turn it on: set `"antiburn": 0.5` in this file (back it up first as `p6_1min_community.json.bak-<date>-ralph`); it applies to chunk 2 and later only (`comm.py:118-119`).
- **P4 open item still stands**: all four P4 continuations came out at 238 extension frames no matter what chunk length was requested (`p4/P4_RESULTS.md`). This file asks for 238, so the 60 s total is unaffected; only re-check it if `chunk_secs` is changed.
- **Cut syntax**: the scene changes are written as prose in the beat text ("Cut to the dark living room:"). Each segment is its own graph, so the cut lands at the ffmpeg concat join. The writer is told to follow the ref guide exactly, and that guide marks cuts inside a single clip as `[Shot N] At MM:SS.mmm` (`guides/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md:218`); no `[Shot N]` marker is requested here because every clip in this list is one continuous shot. If D4's `[Shot N]` form is wanted *inside* one 10-15 s chunk instead, that is a beat-text change in this file.
- **Images**: only FD006, FD003 and D15, all three already in `comm.py:38-42 APPROVED` (ALI-80 approved adult stills) and already referenced by `shots/p5_3shot.json`. `stage()` center-crops them to 768x1344 before use.
- **Wall-clock, arithmetic from `community.log`, not a measurement**: 768x1344 / 124 frames / 10 steps took 160.3 s (line 6); 576x1024 / 243 frames / 8 steps took 150.3 s (line 41); 576x1024 / 481 frames / 8 steps took 205-356 s (lines 33-39). The 12 pair clips are the cheap part; the three 20 s finals at full size are the slow part.
- **Upload**: after the one-minute stitch, `batch_queue.upload` copies to `gdrive:AlienPc/community/p6_1min_community`. gdrive still 403s until Derrick re-auths (D15 / ALI-135); the copy is reported in the run log, nothing else changes.

## 4. Where the files land

- `C:\AI\community\runs\p6_pairs\` - 12 mp4 + `.json` sidecars, `prompts\` (one .txt + .json per arm), `.api.json` per job, `contact_sheet.png`, `notes.md`. No stitch (p6.py passes `--no-stitch`) so the four arms stay side by side.
- `C:\AI\community\runs\p6_1min_community\` - 3 segment mp4s + `p6_1min_community_stitched.mp4` (~60 s) + contact sheet + notes.
- `C:\AI\community\runs\p6_1min_switchyard\` - 12 Switchyard cells + `p6_1min_switchyard_stitched.mp4` (~60 s) + contact sheet + notes.
