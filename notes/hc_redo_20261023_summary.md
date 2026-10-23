# ALI-163 hc redo - FINAL summary (2026-10-23, Forge)

> **Correction 2026-10-23 (Max, 4:51 PM CT):** the 2:59 PM CT claim that the redos use the approved start still is wrong. r3r–r6 used face crops only; the start still was not in the graph (found 4:03 PM CT; fix in ALI-184 BQ1). The original lines below are kept.

## FINAL reopened (Max 3:16 PM CT) - what this pass added

- **clip 3 now has renders.** The original R6 id `ali147_pool_hc_r3_s51130003` died on the rc=2 static check (audio_vae on MiniMaxH3ImageToVideo); the fixed graph was re-queued under two NEW ids, both now verified here: `ali147_pool_hc_r3r_s51130003` (R6R, face crops only) and `ali147_pool_hc_r3b_s51130003` (BQ1c rewire = the approved start still back in c0 + c1 ref slots plus the 2 face crops).
- Contact sheet `notes\hc_redo_20261023_contact.png` is now **9 rows x 5 frames** (adds the r3r and r3b rows, same 5 timestamps, labelled with id / seed / start still / reference images).
- New objective items per clip (pure PIL, no vision judge): the 5 sheet frames are counted, sha256'd, checked for duplicates, and their grayscale luma stdev is reported (a black/flat frame would sit near 0; every rendered clip here measures 33.9-56.8).
- This pass is CPU only: no render, no GPU, no new seed, no ComfyUI port call, no vision judge.

METHOD_ONLY. Review = contact sheet + objective checks only (ffprobe -count_packets, ffmpeg stream copy, sha256, status.log greps). NO vision judge was called on any output (superseded 2026-10-22). No quality redo was requested. **KEEP is Derrick's only.**

Contact sheet: `C:/AI/community/notes/hc_redo_20261023_contact.png` (9 rows x 5 frames, built by notes\ali163_hc_final_sheet.py from frames extracted by notes\ali163_hc_final_media.ps1 at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s; rows 0 and 1 use the SAME timestamps, so old clip 1 and new clip 1 line up frame-for-frame). Raw objective dump: notes\ali163_hc_final_objective.json (notes\ali163_hc_final_check.py).

## R1 length + R2 causes (3 lines)
1. R1 length: 243 frames = c0 124 + win1.extension_frames 119 (overlap 22) at 24 fps = 10.125 s per clip (notes/hc_redo_research_20261023.md; R1 line in TASKS.md). Every R-clip and every check below uses 243 f.
2. R2 top causes (ranked, notes/hc_redo_research_20261023.md '## R2 diagnosis'): (1) `c1` was MiniMaxH3ImageToVideo with NO ref_images slot, so the whole continuation chunk had no fresh appearance input; (2) one `ref_images` slot holding the wide two-person start still at `ref_image_size = match` = 1.03 Mpx shared by two faces.
3. R2 causes 3-5: `subject_definitions` bound both subjects to the same `<Picture 1>` (and 7 `<Picture>` mentions pointed at slots that do not exist); `c1.prompt` had no subject_definitions and no `<Picture>` anchor (free-text hair wording = the model prior that lets a new face in); the landscape 1344x768 canvas plus a landscape two-shot shrinks the face area, and nothing compensated for it.

## Budget (C:/Users/derek/5slock/ralph-community/logs/p7_budget.json)
read at FINAL tick: used_min **467.5**, jobs **37**, cap_min 615, job_cap 45, updated 2026-10-23T17:28:21.
R-line gate was used_min < 475 and jobs < 35 (495 min / 35 jobs); the harness caps are now 615 min / 45 jobs (Derrick 1:07 PM CT). At the first FINAL tick jobs was 35 = the R-line cap, so clip 3 could not be re-requested under an R-line id; that reading (used_min 450.8 / jobs 35) is the recorded BAKEOFF START. **clip 3 was then re-rendered twice under the ALI-173 bakeoff allowance** (Max 3:15 PM CT gave R6R one slot; BQ1c took one more), which is why jobs is now above 35. No render ran in this pass.

## Table (all 10 rows: 2 old-batch reference + 6 R-clips + 2 clip-3 re-renders r3r / r3b)

| clip | id | ok/rc | frames (probe/expected) | WxH | fps | audio (mp4) | m4a | m4a dur | mp4 bytes | render s | seed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| clip 1 OLD | `ali147_pool_hc_c1_s51100001` | True/0 | 481/481 | 1344x768 | 24/1 | aac,32000,2 | True | 20.042000 | 5487624 | 832.5 | 51100001 |
| clip 2 OLD | `ali147_pool_hc_c2_s51100002` | True/0 | 481/481 | 1344x768 | 24/1 | aac,32000,2 | True | 20.042000 | 6509571 | 847.3 | 51100002 |
| clip 1 NEW (R4) | `ali147_pool_hc_r1_s51130001` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 2774534 | 526.7 | 51130001 |
| clip 2 NEW (R5) | `ali147_pool_hc_r2_s51130002` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 3831791 | 541.7 | 51130002 |
| clip 3 (R6) | `ali147_pool_hc_r3_s51130003` | False/2 | None/243 | NonexNone | None | - | False | - | - | - | 51130003 |
| clip 3 R6R | `ali147_pool_hc_r3r_s51130003` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 3760110 | 416.3 | 51130003 |
| clip 3 BQ1c | `ali147_pool_hc_r3b_s51130003` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 3527348 | 481.9 | 51130003 |
| clip 4 (R7) | `ali147_pool_hc_r4_s51130004` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 3712205 | 416.2 | 51130004 |
| clip 5 (R8) | `ali147_pool_hc_r5_s51130005` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 2543598 | 411.3 | 51130005 |
| clip 6 (R9) | `ali147_pool_hc_r6_s51130006` | True/0 | 243/243 | 1344x768 | 24/1 | aac,32000,2 | True | 10.125000 | 3650591 | 426.3 | 51130006 |

Probe = `ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0` (exact packet count, not the container count).

## Per clip

### clip 1 OLD - `ali147_pool_hc_c1_s51100001` (HC1/HC2 batch (481 f))
- mp4: `C:/AI/community/runs\ali147_pool_hc_c1_s51100001\ali147_pool_hc_c1_s51100001.mp4` exists=True, bytes=5487624, sha256=4fafb9f7de06728f1c71615ffb036d75dccde446bd38c9dcb8cb506a6abc222c
- m4a: `C:/AI/community/runs\ali147_pool_hc_c1_s51100001\ali147_pool_hc_c1_s51100001.m4a` exists=True, bytes=326142, sha256=acc67888bc8ebde30f9fc10d294def16aa94921c615160264461e70a4e7f7ce7, probe=['aac,audio,32000,2', '20.042000']
- video probe: 1344x768, fps 24/1, packets 481 (expected 481) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 55.48 (0 would mean a black/flat frame); mean/stdev per frame = [(117.15, 61.37), (113.51, 55.48), (106.51, 58.64), (105.15, 59.09), (105.36, 58.22)]
- render secs: 832.5 (prompt_id d48e6c13-7754-41c4-b032-c04d0eacd19d), finished 2026-10-23 09:48 CT
- result.json: ok=True rc=0 started 2026-10-23T09:33:40 finished 2026-10-23T09:48:41 wall_min=15 budget_used_min_at_finish=390.3 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 09:34:47 CT JOB start ali147_pool_hc_c1_s51100001 prompt_id=d48e6c13-7754-41c4-b032-c04d0eacd19d`
- status.log: `2026-10-23 09:48:40 CT JOB end ali147_pool_hc_c1_s51100001 ok secs=832.5 file=C:\AI\community\runs\ali147_pool_hc_c1_s51100001\ali147_pool_hc_c1_s51100001.mp4`
- status.log: `2026-10-23 09:48:40 CT OBJECTIVE ok ali147_pool_hc_c1_s51100001 frames=481 audio=True dur=20.042 bytes=5487624 contact=C:\AI\community\runs\ali147_pool_hc_c1_s51100001\ali147_pool_hc_c1_s51100001_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD004.jpg (HC1, pair)
- reference input(s) in graph: img = community/hc/HC1_Two_women_in_studio_editorial.jpg (start still only; no sheet ref on c0 or c1)
- sound line: overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, sharp inhales, heavy breathing, and rising moans and gasps from both women, one 
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [238], seed [51100001]
- failures: none (objective items all pass)

### clip 2 OLD - `ali147_pool_hc_c2_s51100002` (HC1/HC2 batch (481 f))
- mp4: `C:/AI/community/runs\ali147_pool_hc_c2_s51100002\ali147_pool_hc_c2_s51100002.mp4` exists=True, bytes=6509571, sha256=a9f68cc6881a7bc35c8d060fa096d797af077a36eea101d4942437c5f08dc234
- m4a: `C:/AI/community/runs\ali147_pool_hc_c2_s51100002\ali147_pool_hc_c2_s51100002.m4a` exists=True, bytes=329467, sha256=04c2c7a613c468b11028a4005cbf46e51e80263643556a3fbf148d583035bd76, probe=['aac,audio,32000,2', '20.042000']
- video probe: 1344x768, fps 24/1, packets 481 (expected 481) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: none extracted (clip 2 OLD is table-only by spec - the old-batch row of the contact sheet is clip 1 OLD; clip 3 R6 has no render at all)
- render secs: 847.3 (prompt_id 8f8b405b-dec5-4bbc-ae3b-9833508b7804), finished 2026-10-23 10:06 CT
- result.json: ok=True rc=0 started 2026-10-23T09:51:28 finished 2026-10-23T10:06:07 wall_min=14.6 budget_used_min_at_finish=404.9 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 09:51:59 CT JOB start ali147_pool_hc_c2_s51100002 prompt_id=8f8b405b-dec5-4bbc-ae3b-9833508b7804`
- status.log: `2026-10-23 10:06:06 CT JOB end ali147_pool_hc_c2_s51100002 ok secs=847.3 file=C:\AI\community\runs\ali147_pool_hc_c2_s51100002\ali147_pool_hc_c2_s51100002.mp4`
- status.log: `2026-10-23 10:06:06 CT OBJECTIVE ok ali147_pool_hc_c2_s51100002 frames=481 audio=True dur=20.042 bytes=6509571 contact=C:\AI\community\runs\ali147_pool_hc_c2_s51100002\ali147_pool_hc_c2_s51100002_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: C:/Users/derek/5slock/approved_characters/FLOW_BLONDE_DARK_PAIRS_2026-10-19/BD007.jpg (HC2, pair)
- reference input(s) in graph: img = community/hc/HC2_Two_women_in_passionate_embrace.jpg (start still only)
- sound line: overall_soundscape: A quiet bedroom room tone with a low distant city hum and soft traffic outside the window, plus a faint bedside lamp buzz. Close muffled intimate sound: wet kissing and tongue sounds, fabric sliding off skin and landing softly on the rug, bedsprings creaking and bedding rustling under shifting weight, skin sliding on skin, soft flesh thudding and skin of the bodies clapping tog
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [238], seed [51100002]
- failures: none (objective items all pass)

### clip 1 NEW (R4) - `ali147_pool_hc_r1_s51130001` (R4 (243 f, Klein sheet refs))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r1_s51130001\ali147_pool_hc_r1_s51130001.mp4` exists=True, bytes=2774534, sha256=b5f78becd371b800dd7e44051365f682df5ad0254266a6f635cb3ce726d9f9e8
- m4a: `C:/AI/community/runs\ali147_pool_hc_r1_s51130001\ali147_pool_hc_r1_s51130001.m4a` exists=True, bytes=164299, sha256=7b89d5a0a32940cca2ed1c8e5a08ca42f1f26905e3e266b4dad93d2a0dc6f1fd, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 56.77 (0 would mean a black/flat frame); mean/stdev per frame = [(101.58, 63.62), (107.79, 58.82), (105.64, 57.1), (103.19, 61.75), (96.19, 56.77)]
- render secs: 526.7 (prompt_id 3d2bf21f-d176-4e10-a9c7-fb807389404a), finished 2026-10-23 11:55 CT
- result.json: ok=True rc=0 started 2026-10-23T11:46:15 finished 2026-10-23T11:55:41 wall_min=9.4 budget_used_min_at_finish=417.9 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 11:46:53 CT JOB start ali147_pool_hc_r1_s51130001 prompt_id=3d2bf21f-d176-4e10-a9c7-fb807389404a`
- status.log: `2026-10-23 11:55:40 CT JOB end ali147_pool_hc_r1_s51130001 ok secs=526.7 file=C:\AI\community\runs\ali147_pool_hc_r1_s51130001\ali147_pool_hc_r1_s51130001.mp4`
- status.log: `2026-10-23 11:55:40 CT OBJECTIVE ok ali147_pool_hc_r1_s51130001 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=2774534 contact=C:\AI\community\runs\ali147_pool_hc_r1_s51130001\ali147_pool_hc_r1_s51130001_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC1 BD004 (pair)
- reference input(s) in graph: img = community/hc/HC1_Two_women_in_studio_editorial.jpg + sheet refs community/hc/HC1_w1_blonde_00001_.png, community/hc/HC1_w2_darkhair_00001_.png
- sound line: overall_soundscape: Soft studio room tone with a low air-handling hum and a faint high-frequency studio-light buzz. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the floor as weight shifts, sharp inhales, heavy breathing
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130001]
- failures: none (objective items all pass)

### clip 2 NEW (R5) - `ali147_pool_hc_r2_s51130002` (R5 (243 f, Klein sheet refs))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r2_s51130002\ali147_pool_hc_r2_s51130002.mp4` exists=True, bytes=3831791, sha256=55cef572bab00c30c3ba5ec453a540384e7d63ef57d51cd5e6db9a5f09e70f53
- m4a: `C:/AI/community/runs\ali147_pool_hc_r2_s51130002\ali147_pool_hc_r2_s51130002.m4a` exists=True, bytes=166973, sha256=2a52eaa076213904a257113cd80649640058040935e7d0f933d8d2064a1d27f3, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 45.58 (0 would mean a black/flat frame); mean/stdev per frame = [(76.64, 59.04), (83.22, 54.81), (73.87, 45.58), (84.3, 48.69), (83.09, 48.87)]
- render secs: 541.7 (prompt_id 8f6267ef-36e8-4cc1-b095-60bfcb7bfba0), finished 2026-10-23 12:09 CT
- result.json: ok=True rc=0 started 2026-10-23T11:59:43 finished 2026-10-23T12:09:16 wall_min=9.5 budget_used_min_at_finish=427.4 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 12:00:13 CT JOB start ali147_pool_hc_r2_s51130002 prompt_id=8f6267ef-36e8-4cc1-b095-60bfcb7bfba0`
- status.log: `2026-10-23 12:09:15 CT JOB end ali147_pool_hc_r2_s51130002 ok secs=541.7 file=C:\AI\community\runs\ali147_pool_hc_r2_s51130002\ali147_pool_hc_r2_s51130002.mp4`
- status.log: `2026-10-23 12:09:15 CT OBJECTIVE ok ali147_pool_hc_r2_s51130002 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=3831791 contact=C:\AI\community\runs\ali147_pool_hc_r2_s51130002\ali147_pool_hc_r2_s51130002_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC2 BD007 (pair)
- reference input(s) in graph: img = community/hc/HC2_Two_women_in_passionate_embrace.jpg + sheet refs community/hc/HC2_w1_blonde_00001_.png, community/hc/HC2_w2_darkhair_00001_.png
- sound line: overall_soundscape: Soft bedroom room tone with a low distant city hum, soft traffic outside the window and a faint bedside lamp buzz. Intimate close sound: skin sliding on skin, repeated soft wet sliding sounds at the point of contact, soft flesh thudding and skin of the bodies clapping together as hips grind and rise into contact, a slick wet skin squeak on the mattress as weight shifts, bedspri
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130002]
- failures: none (objective items all pass)

### clip 3 (R6) - `ali147_pool_hc_r3_s51130003` (R6 (243 f, face-crop refs) - NOT RENDERED)
- mp4: `C:/AI/community/runs\ali147_pool_hc_r3_s51130003\ali147_pool_hc_r3_s51130003.mp4` exists=False
- m4a: `-` exists=False
- video probe: NonexNone, fps None, packets None (expected 243) -> n/a
- audio in mp4: -; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: none extracted (clip 2 OLD is table-only by spec - the old-batch row of the contact sheet is clip 1 OLD; clip 3 R6 has no render at all)
- render secs: None (prompt_id None), finished None
- result.json: ok=False rc=2 started 2026-10-23T14:14:42 finished 2026-10-23T14:15:36 wall_min=0.9 budget_used_min_at_finish=428.3 note="run_graph_job rc=2 (static check failed, see status.log)"
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC3 GI173 (pair)
- reference input(s) in graph: img = community/hc/HC3_w1_face.png, img2 = community/hc/HC3_w2_face.png (face crops, R4G2)
- sound line: overall_soundscape: Soft exterior room tone with distant surf, a light sea breeze and occasional far gull calls. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the stone as weight shifts, sharp inhales, heavy breathing, a
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130003]
- FAILURES: rc=2 - run_graph_job rc=2 (static check failed, see status.log); status.log tail: `2026-10-23 14:14:42 CT UNLOAD LLM coding_swift15_iq3s | 2026-10-23 14:15:36 CT STATIC_FAIL ali147_pool_hc_r3_s51130003 c1.audio_vae: not an input of MiniMaxH3ImageToVideo`. No mp4, no m4a, no frames (the job never queued a sample). The graph was fixed after the fail by the iter 03 builder pass (notes\ali163_hc_r4g2_build.py pops the invalid `c1.audio_vae` link + runs the offline static self-check), so this clip is renderable, **but the job id `ali147_pool_hc_r3_s51130003` is spent** (p7\jobs\<id>.result.json exists = the runner refuses 'id already used') and the R-line job cap 35/35 was reached at that moment. Reported, not self-requested (PROMPT.md: real failures = rc 4 or TIMEOUT; rc=2 is a static-check failure, and STUCK is reported, never re-requested).
- RESOLVED (Max 3:15 PM CT): the fixed clip-3 graph was re-queued under two NEW ids inside the ALI-173 bakeoff allowance - `ali147_pool_hc_r3r_s51130003` (R6R, face crops only, ok rc=0, 243 f, 416.3 s) and `ali147_pool_hc_r3b_s51130003` (BQ1c rewire = start still + 2 face crops on c0 AND c1, ok rc=0, 243 f, 481.9 s). Both are verified in this file and both have their own contact-sheet row.

### clip 3 R6R - `ali147_pool_hc_r3r_s51130003` (R6R re-render of clip 3 (243 f, face crops only))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r3r_s51130003\ali147_pool_hc_r3r_s51130003.mp4` exists=True, bytes=3760110, sha256=642cdea337d13974addc5273b21c3a9f8e43fbb06c3d4d0decdc67a73278a482
- m4a: `C:/AI/community/runs\ali147_pool_hc_r3r_s51130003\ali147_pool_hc_r3r_s51130003.m4a` exists=True, bytes=165349, sha256=4f8264942172d20a9c0f061d1c163c880e4942ce93754a4449f587d5d0f5c88e, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 45.92 (0 would mean a black/flat frame); mean/stdev per frame = [(117.76, 45.92), (129.94, 53.01), (126.02, 46.34), (129.84, 50.79), (137.74, 62.25)]
- render secs: 416.3 (prompt_id 72c98f52-ed8c-4117-bc4c-dab4d0b35f49), finished 2026-10-23 15:31 CT
- result.json: ok=True rc=0 started 2026-10-23T15:23:59 finished 2026-10-23T15:31:51 wall_min=7.9 budget_used_min_at_finish=458.7 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 15:24:54 CT JOB start ali147_pool_hc_r3r_s51130003 prompt_id=72c98f52-ed8c-4117-bc4c-dab4d0b35f49`
- status.log: `2026-10-23 15:31:50 CT JOB end ali147_pool_hc_r3r_s51130003 ok secs=416.3 file=C:\AI\community\runs\ali147_pool_hc_r3r_s51130003\ali147_pool_hc_r3r_s51130003.mp4`
- status.log: `2026-10-23 15:31:51 CT OBJECTIVE ok ali147_pool_hc_r3r_s51130003 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=3760110 contact=C:\AI\community\runs\ali147_pool_hc_r3r_s51130003\ali147_pool_hc_r3r_s51130003_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC3 GI173 (pair)
- reference input(s) in graph: img = community/hc/HC3_w1_face.png, img2 = community/hc/HC3_w2_face.png (2 face crops only, R4G2 wiring; NO start still in this graph - Max 4:51 PM CT)
- sound line: overall_soundscape: Soft exterior room tone with distant surf, a light sea breeze and occasional far gull calls. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the stone as weight shifts, sharp inhales, heavy breathing, a
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130003]
- failures: none (objective items all pass)

### clip 3 BQ1c - `ali147_pool_hc_r3b_s51130003` (BQ1c test render of clip 3 (243 f, start still + 2 face crops))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r3b_s51130003\ali147_pool_hc_r3b_s51130003.mp4` exists=True, bytes=3527348, sha256=d125b8feb11e4aea368714c88cccd863cb40659a0117f7817d1ceb78a4f320f3
- m4a: `C:/AI/community/runs\ali147_pool_hc_r3b_s51130003\ali147_pool_hc_r3b_s51130003.m4a` exists=True, bytes=166134, sha256=bceb4cd611f3276f2262d354aed8b8ac44936f957aa82df0fd80e7dcb7053885, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 47.22 (0 would mean a black/flat frame); mean/stdev per frame = [(135.92, 56.31), (131.12, 58.29), (120.6, 47.22), (121.62, 54.26), (138.03, 64.47)]
- render secs: 481.9 (prompt_id 886bc3a9-caed-4f42-9efd-54be8a8b23ce), finished 2026-10-23 17:28 CT
- result.json: ok=True rc=0 started 2026-10-23T17:19:31 finished 2026-10-23T17:28:21 wall_min=8.8 budget_used_min_at_finish=467.5 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 17:20:19 CT JOB start ali147_pool_hc_r3b_s51130003 prompt_id=886bc3a9-caed-4f42-9efd-54be8a8b23ce`
- status.log: `2026-10-23 17:28:20 CT JOB end ali147_pool_hc_r3b_s51130003 ok secs=481.9 file=C:\AI\community\runs\ali147_pool_hc_r3b_s51130003\ali147_pool_hc_r3b_s51130003.mp4`
- status.log: `2026-10-23 17:28:21 CT OBJECTIVE ok ali147_pool_hc_r3b_s51130003 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=3527348 contact=C:\AI\community\runs\ali147_pool_hc_r3b_s51130003\ali147_pool_hc_r3b_s51130003_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC3 GI173 (pair)
- reference input(s) in graph: img = community/hc/HC3_lesbian_beach.jpg (start still back in c0 ref_1) + community/hc/HC3_w1_face.png + community/hc/HC3_w2_face.png (BQ1 rewire, c0 AND c1)
- sound line: overall_soundscape: Soft exterior room tone with distant surf, a light sea breeze and occasional far gull calls. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, a soft skin squeak on the stone as weight shifts, sharp inhales, heavy breathing, a
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130003]
- failures: none (objective items all pass)

### clip 4 (R7) - `ali147_pool_hc_r4_s51130004` (R7 (243 f, face-crop refs))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r4_s51130004\ali147_pool_hc_r4_s51130004.mp4` exists=True, bytes=3712205, sha256=c031b097817e0ca0473eb33205da5be8177b12de2a734124867c9460fb363332
- m4a: `C:/AI/community/runs\ali147_pool_hc_r4_s51130004\ali147_pool_hc_r4_s51130004.m4a` exists=True, bytes=165323, sha256=7e9dba1e35b974486513ce9e757faa25eefdcd5969067e858e5eea818566ecff, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 49.73 (0 would mean a black/flat frame); mean/stdev per frame = [(106.57, 59.23), (137.71, 49.73), (135.62, 49.97), (113.6, 62.26), (129.56, 53.09)]
- render secs: 416.2 (prompt_id 19d0276b-c9d1-4028-96a8-8f5b82eaa0a1), finished 2026-10-23 14:29 CT
- result.json: ok=True rc=0 started 2026-10-23T14:22:01 finished 2026-10-23T14:29:26 wall_min=7.4 budget_used_min_at_finish=435.7 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 14:22:29 CT JOB start ali147_pool_hc_r4_s51130004 prompt_id=19d0276b-c9d1-4028-96a8-8f5b82eaa0a1`
- status.log: `2026-10-23 14:29:26 CT JOB end ali147_pool_hc_r4_s51130004 ok secs=416.2 file=C:\AI\community\runs\ali147_pool_hc_r4_s51130004\ali147_pool_hc_r4_s51130004.mp4`
- status.log: `2026-10-23 14:29:26 CT OBJECTIVE ok ali147_pool_hc_r4_s51130004 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=3712205 contact=C:\AI\community\runs\ali147_pool_hc_r4_s51130004\ali147_pool_hc_r4_s51130004_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC4 GI107 (solo)
- reference input(s) in graph: img = community/hc/HC4_w1_face.png (face crop, R4G2)
- sound line: overall_soundscape: A quiet interior room tone with a faint high-frequency window-air hiss. Rhythmic close sound: bare feet slapping and sliding on pale wood, cloth rustling as the sports top is pulled off and lands softly on the floor, palms sliding over wet skin, the barre creaking lightly under a hand, deep breathing and counted exhales, low moaning as her breathing quickens. One clear radio be
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130004]
- failures: none (objective items all pass)

### clip 5 (R8) - `ali147_pool_hc_r5_s51130005` (R8 (243 f, face-crop refs))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r5_s51130005\ali147_pool_hc_r5_s51130005.mp4` exists=True, bytes=2543598, sha256=87b8dd7f54f1702dacbb86a4f0c2560a030ec614ff1dc7065e3699da7ef5b625
- m4a: `C:/AI/community/runs\ali147_pool_hc_r5_s51130005\ali147_pool_hc_r5_s51130005.m4a` exists=True, bytes=165906, sha256=222ba75e27106fc3cf81ce3af0c591426158e0cb51f3109e061ff2f94f1635bd, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 33.94 (0 would mean a black/flat frame); mean/stdev per frame = [(60.86, 33.94), (70.34, 52.11), (72.48, 47.33), (87.6, 47.49), (92.15, 52.48)]
- render secs: 411.3 (prompt_id 4342a681-e226-4d9d-9703-c70edb823d43), finished 2026-10-23 14:41 CT
- result.json: ok=True rc=0 started 2026-10-23T14:33:45 finished 2026-10-23T14:41:15 wall_min=7.5 budget_used_min_at_finish=443.2 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 14:34:23 CT JOB start ali147_pool_hc_r5_s51130005 prompt_id=4342a681-e226-4d9d-9703-c70edb823d43`
- status.log: `2026-10-23 14:41:14 CT JOB end ali147_pool_hc_r5_s51130005 ok secs=411.3 file=C:\AI\community\runs\ali147_pool_hc_r5_s51130005\ali147_pool_hc_r5_s51130005.mp4`
- status.log: `2026-10-23 14:41:15 CT OBJECTIVE ok ali147_pool_hc_r5_s51130005 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=2543598 contact=C:\AI\community\runs\ali147_pool_hc_r5_s51130005\ali147_pool_hc_r5_s51130005_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC5 GI150 (solo)
- reference input(s) in graph: img = community/hc/HC5_w1_face.png (face crop, R4G2)
- sound line: overall_soundscape: Quiet interior room tone with a faint distant traffic hum through closed curtains. Close, wet sound: fingertips sliding on wet skin, soft skin-on-skin contact at the chest, the bedspread rustling and the mattress springs creaking as she lies back, sheet fabric gripping under a hand, a wet sliding sound at the point of contact, sharp inhales, heavy breathing, and a rising moan t
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130005]
- failures: none (objective items all pass)

### clip 6 (R9) - `ali147_pool_hc_r6_s51130006` (R9 (243 f, face-crop refs))
- mp4: `C:/AI/community/runs\ali147_pool_hc_r6_s51130006\ali147_pool_hc_r6_s51130006.mp4` exists=True, bytes=3650591, sha256=9f17cddfa1e72c70736d9ecc0c013648d189cb169eeb2c4c86524f34d938d911
- m4a: `C:/AI/community/runs\ali147_pool_hc_r6_s51130006\ali147_pool_hc_r6_s51130006.m4a` exists=True, bytes=164660, sha256=e468c9ee6023f8790e42129d466129028f7c0a972f9183fe4a58f0afa14bc002, probe=['aac,audio,32000,2', '10.125000']
- video probe: 1344x768, fps 24/1, packets 243 (expected 243) -> MATCH
- audio in mp4: aac,32000,2; audio stream extract = ffmpeg -vn -c:a copy (stream copy, no re-encode)
- sheet frames: 5/5 present, all sha256 distinct = True, min luma stdev = 56.13 (0 would mean a black/flat frame); mean/stdev per frame = [(91.02, 63.12), (57.53, 60.79), (54.52, 56.97), (76.15, 56.13), (78.88, 59.13)]
- render secs: 426.3 (prompt_id 9c9d0cb9-c26c-429d-917f-c206ac8df841), finished 2026-10-23 14:52 CT
- result.json: ok=True rc=0 started 2026-10-23T14:45:19 finished 2026-10-23T14:52:54 wall_min=7.6 budget_used_min_at_finish=450.8 note="run_graph_job rc=0 (ok)"
- status.log: `2026-10-23 14:45:47 CT JOB start ali147_pool_hc_r6_s51130006 prompt_id=9c9d0cb9-c26c-429d-917f-c206ac8df841`
- status.log: `2026-10-23 14:52:53 CT JOB end ali147_pool_hc_r6_s51130006 ok secs=426.3 file=C:\AI\community\runs\ali147_pool_hc_r6_s51130006\ali147_pool_hc_r6_s51130006.mp4`
- status.log: `2026-10-23 14:52:54 CT OBJECTIVE ok ali147_pool_hc_r6_s51130006 image=False frames=243 size=1344x768 audio=True dur=10.125 bytes=3650591 contact=C:\AI\community\runs\ali147_pool_hc_r6_s51130006\ali147_pool_hc_r6_s51130006_stills_contact.png`
- greps: 'JOB error' = 0, 'CLIP_SKIP' = 0 (both must be 0)
- start still: HC6 BD076 (pair)
- reference input(s) in graph: img = community/hc/HC6_w1_face.png, img2 = community/hc/HC6_w2_face.png (face crops, R4G2)
- sound line: overall_soundscape: Late lounge room tone with distant slot chimes and muffled room murmur far away, ice ticking in a glass, low air-handling hum. Intimate close sound: repeated soft wet sliding sounds and tongue sounds, soft flesh thudding and skin of the bodies clapping together as hips rise into contact, slick wet noises at the point of contact, vinyl squeaking as weight shifts, sharp inhales, 
- graph canvas: width [1344, 1344], height [768, 768], extension_frames [119], seed [51130006]
- failures: none (objective items all pass)

## Objective check list (the FINAL items)

Task check list, item by item: (1) every requested clip passes the objective items or is listed with its failure = the per-id lines below (r3 is the failure line, with its RESOLVED note); (2) m4a per clip = the `m4a` column of the table + the per-clip m4a sha256/probe lines; (3) contact sheet + summary exist = `notes\hc_redo_20261023_contact.png` and this file, both regenerated this pass. No vision judge was called, no quality redo, no new seed, no GPU.

- [x] `ali147_pool_hc_c1_s51100001`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 481 f (expected 481); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 55.48
- [x] `ali147_pool_hc_c2_s51100002`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 481 f (expected 481); audio stream present = True; m4a per clip = True; no sheet frames (table-only row: clip 2 OLD has no contact-sheet row by spec, clip 3 R6 has no render at all)
- [x] `ali147_pool_hc_r1_s51130001`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 56.77
- [x] `ali147_pool_hc_r2_s51130002`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 45.58
- [ ] `ali147_pool_hc_r3_s51130003`: result.json NOT ok (rc=2); JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe NonexNone None None f (expected 243); audio stream present = False; m4a per clip = False; no sheet frames (table-only row: clip 2 OLD has no contact-sheet row by spec, clip 3 R6 has no render at all)
- [x] `ali147_pool_hc_r3r_s51130003`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 45.92
- [x] `ali147_pool_hc_r3b_s51130003`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 47.22
- [x] `ali147_pool_hc_r4_s51130004`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 49.73
- [x] `ali147_pool_hc_r5_s51130005`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 33.94
- [x] `ali147_pool_hc_r6_s51130006`: result.json ok; JOB start + JOB end quoted above; 'JOB error' = 0 and 'CLIP_SKIP' = 0; probe 1344x768 24/1 243 f (expected 243); audio stream present = True; m4a per clip = True; 5/5 sheet frames, all sha256 distinct = True, min luma stdev = 56.13

**Verdict: all requested R-clip ids ok except the dead `ali147_pool_hc_r3_s51130003` (rc=2, listed with its failure + RESOLVED line) = True** - computed straight from the result.json files in C:\AI\community\p7\jobs, not asserted.

The 7 requested R-clip renders that produced media (r1, r2, r3r, r3b, r4, r5, r6) pass every objective item: 1344x768, 24/1 fps, 243 packets = the R1 count, an audio stream, an extracted `<id>.m4a` (aac, 32000 Hz, 2 ch, 10.125 s), 5 distinct non-black sheet frames, 0 'JOB error' / 0 'CLIP_SKIP'. The original r3 id is listed with its failure (rc=2 static check, no render) and is superseded by r3r (R6R) and r3b (BQ1c). The two old-batch clips (c1, c2) are in the table, and c1 is row 0 of the contact sheet, for the side-by-side; they are 481 f / 20.04 s by design and are not part of the R batch.

Clip 3 is now a 3-way comparison on the same pick (HC3 GI173) and the same seed 51130003: r3 (dead, rc=2) -> r3r (face crops only, the R4G2/R6R wiring) -> r3b (BQ1c rewire: the approved start still back in the ref slots of c0 AND c1 + the 2 face crops + the BQ1 prompt rewire). Side-by-side frames of r3b vs r3r are also in notes\body_quality_r3b_vs_r3r_contact.png (BQ1d). No face-similarity number was run in this pass (not asked by the FINAL check list); the R4F/R4G numbers are in notes\hc_prompt_face_audit_20261023.md.

## Files made by this pass
- notes\ali163_hc_final_check.py (objective dump) -> notes\ali163_hc_final_objective.json. Per clip it now also sha256s the 5 sheet frames, checks they are distinct and reports their PIL grayscale luma stdev (a black/flat frame would sit near 0).
- notes\ali163_hc_final_media.ps1 (m4a stream copy + 5 frames per clip) -> notes\hc_final_frames\*.png; the id list now includes r3r + r3b (r3 has no media to extract).
- notes\ali163_hc_final_sheet.py -> notes\hc_redo_20261023_contact.png (9 rows x 5 frames, labelled) with a built-in self-check: every rendered row's 5 cells must be non-flat (luma stdev > 5) and the NO-RENDER row must show the red panel (mean R > G+15). Self-destruct probe run 2026-10-23: hid r6 frame 4 -> the builder exited rc=1 naming `ali147_pool_hc_r6_s51130006` cell 4; restored -> rc=0 PASS 9 rows.
- this file: C:/AI/community/notes/hc_redo_20261023_summary.md

Written 2026-10-23 17:57 CT by Forge, ALI-163 FINAL (reopened pass: r3r + r3b added to the verify and the contact sheet). METHOD_ONLY; the R4F/R4G face numbers are in notes\hc_prompt_face_audit_20261023.md - no new face metric was run here (the FINAL check list does not ask for one). No vision judge, no GPU, no render, no new seed.
