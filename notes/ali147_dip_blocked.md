# ALI-147 DIP_PROOF - BLOCKED (Forge Ralph, 2026-10-22, iteration after DIP_REQ)

Task: DIP_PROOF in C:\AI\community\runs\ali147_pool_dip_s51080000\PROOF.md. The gate is
`C:\AI\community\p7\jobs\ali147_pool_dip_s51080000.result.json` saying ok=true. It says ok=false,
so per the task line and PROMPT.md the item is marked `[!]` + BLOCKED + STOP_RALPH, and no new job
is requested (a render/ffmpeg re-run is not mine to run, and a quality re-request is never allowed).

## Why it failed (objective, not quality)
- result.json: `ok=false`, `rc=5`, `note="dip_join rc=5"`, started 2026-10-22T16:34:24, finished 16:34:41, wall_min 0.3, kind=dip.
- dip.log last line: `2026-10-22 16:34:41 CT DIP end FAIL`.
- Required frame count for every DIP output is **1443** (plan + task check). Recorded in dip.log for all three: `frames=1444`.
- Independent verification (my own ffprobe, `-select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0`):
  - `dipblack.mp4` -> `768,1344,24/1,1444`
  - `dipwhite.mp4` -> `768,1344,24/1,1444`
  - `base_reenc.mp4` -> `768,1344,24/1,1444`
  - Base input `p7_r2_c3_pmot_full_pool_seg1.mp4` -> `768,1344,24/1,481` (dip.log `segment frames [481, 481, 481]`, sum 1443)
- Every ffmpeg ran clean: `ffmpeg_exit=0` for all three outputs, `audio=True`, `dur=60.192` s; bytes
  base_reenc 35,528,476 / dipblack 36,068,430 / dipwhite 38,222,051. Contact sheets exist for all three
  (`base_reenc_stills_contact.png`, `dipblack_stills_contact.png`, `dipwhite_stills_contact.png`).
- So the fade logic and the audio path are fine. The one-frame overshoot is the encode: `ffmpeg_cmd.txt`
  ends every command with `-c:v libx264 -crf 14 -pix_fmt yuv420p -r 24 -c:a aac`. The concat of
  3x481 packets at 24/1 is 60.125 s; with the `-r 24` output-rate rescale the muxed stream reports
  60.192 s, which ffprobe counts as 1444 packets. No `fps=`/`trim` guard in `dip_join.py`.

## What Derrick needs to decide (no action taken by Forge)
- Option A: patch `C:\AI\community\scripts\dip_join.py` to pin the frame count (e.g. drop `-r 24`, or add
  `fps=24,trim=end_frame=1443` on the concat `[v]`, audio trimmed to match) and let the harness re-run the dip job.
- Option B: accept 1444 frames as the DIP arm result and relax the DIP check to 1443 +-1 (the extra frame
  is a mux artefact, not an image; the three outputs stay frame-aligned with each other and with base_reenc,
  so the by-eye comparison is unaffected).
- The harness performed no redo for `kind=dip` (redos are the graph path: max 2, same seed then seed+1).

Method only. KEEP is Derrick's. Nothing here judges the explicit content.
