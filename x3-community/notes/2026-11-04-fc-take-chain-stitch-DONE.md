# FC take chain - stitch + pack DONE (2026-11-04, Forge/pi, sydney lane)

Plan of record: `C:\AI\community\plans\2026-11-03-1955-fc-take-chain-10-plan.md` (10 x 10.125 s, one axis per cell,
hard cuts + 60 ms audio crossfade). The 10 cells were rendered 2026-11-03 20:03-20:42 CT, `BATCH closed rc=0 ...
done=10/10` (actions.log 2762). This pass is the **Stitch + Deliverables** half of that plan: the film, `key.csv`,
the review grid, and the QNAP pack. **No GPU work in this pass**: ffmpeg + copies only, no model load, no
`C:\AI\locks\gpu-render.lock`, no render, nothing deleted, no config write.

Run dir `C:\AI\community\runs\take_chain_20261104\` - the plan named it `face_take_chain_20261104`; the run was built
under `take_chain_20261104` and every record here uses the real name. No rename (a rename would break the shas in
`key.csv` paths). Lane record: this file, in `C:\AI\community\notes\`. The plan asks for the lane record under
`C:\Users\derek\sydney\notes\`; AGENTS.md forbids me opening that folder, so it is filed in the shared notes tree.

## New tool (kept, reusable)

`C:\AI\community\scripts\queue\take_chain_stitch.py` - proves the cells are uniform (ffprobe codec/canvas/fps/pix_fmt/
sample rate/channels) before writing anything, then: video-only `concat` demuxer with `-c:v copy` (bit-for-bit video,
hard cuts), audio crossfaded 60 ms per seam (`acrossfade` chain, triangle curves), muxed back with `apad` +
`-shortest`, `+faststart`. It writes `_stitch\{concat_list.txt,_video_only.mp4,<name>.mp4,key.csv,review_grid.png}`,
prints one `PROOF` line per artifact, and **exits 0 only when the film's duration equals the sum of the cells**.
Usage `python scripts\queue\take_chain_stitch.py <run_dir> --name <stem> --grid`.

First run exited `STITCH FAIL ... dur=10.125 want=101.250 delta=-91.125`: the mux mapped `0:v:0` from the **cell
list**, not from `_video_only.mp4`, and `-shortest` quietly truncated the film to one cell. Fixed by putting the
concatenated video at input 0 and mapping audio from inputs 1..n. The second run passed. The duration
equality check is what caught it; without it the file would have shipped as a 10-second film.

## Proof (ffprobe, this pass)

Cells, all ten uniform: h264 768x1344 yuv420p 24/1 fps, aac 32000 Hz stereo, 10.125000 s each.

Film `C:\AI\community\runs\take_chain_20261104\_stitch\fc_take_chain_20261104.mp4`:

```
video h264 768x1344@24/1  nb_frames=2430  duration=101.250000
audio aac  32000 Hz 2ch   nb_frames=3165  duration=101.248000
format duration=101.250000  size=34522215
sha256 a62ecd6cd622522f027f246cca9d84b07ee8696ceb100efab8864253ef6ec994
key.csv sha256 0d12aff64aa2526f631d55d6f7dea6709b32ecced7f3b7b546b7856807eb3e7a   (10 rows + header)
review_grid.png sha256 198956e109a6c307b092c89a9c7153a096ebc9f6fbeb5b3a4c63e73313779fe4  (1536x1108)
```

`STITCH OK cells=10 xfade=0.06`, delta `+0.000` s. The audio bed is **0.540 s shorter** than the video by design
(9 seams x 60 ms), so from mid-film the sound leads the picture by up to 0.54 s; the bed is room tone + breath, not
lip-sync, which is what the plan chose. `apad` fills the tail. Stated in the pack README, not hidden.

## Per-cell render record (from the run's own status.log, 2026-11-03)

| cell | frames | size | wall (submit→OBJECTIVE ok) | s/frame |
|---|---|---|---|---|
| c01_s51083401 | 243 | 768x1344 | 248 s | 1.021 |
| c02_s51083402 | 243 | 768x1344 | 227 s | 0.934 |
| c03_s51083403 | 243 | 768x1344 | 227 s | 0.934 |
| c04_s51083404 | 243 | 768x1344 | 226 s | 0.930 |
| c05_s51083405 | 243 | 768x1344 | 226 s | 0.930 |
| c06_s51083406 | 243 | 768x1344 | 226 s | 0.930 |
| c07_s51083407 | 243 | 768x1344 | 226 s | 0.930 |
| c08_s51083408 | 243 | 768x1344 | 226 s | 0.930 |
| c09_s51083409 | 243 | 768x1344 | 229 s | 0.942 |
| c10_s51083410 | 243 | 768x1344 | 226 s | 0.930 |

First submit 20:04:17, last OBJECTIVE ok 20:42:40 = **38.4 min wall for 10 clips**, 2513 s summed per-clip wall.
243-frame cells at **0.930-1.021 s/frame** here, against the 243-frame single render recorded 2026-10-28 at
360.2 s = 1.48 s/frame (same beta7 dial). Conditions differ (a batch keeps `comfyui_auto` loaded between jobs, the
LLM was unloaded for the whole window), so this is a recorded number, **not a speed claim**.

## Pack (delivered, byte-verified)

`python scripts\pi_qnap.py put C:\AI\community\review\fc-take-chain-2026-11-04\pack /pi-drop/fc-take-chain-2026-11-04`
-> `Transferred: 82.798 MiB ... Transferred: 26 / 26, 100%`. `pi_qnap.py ls` on the NAS returns **26 files** with the
same byte sizes as local: 10 clips (bytes match `render_ok.json` exactly), 10 contact sheets, the film
(34,522,215 B), `key.csv`, `review_grid.png`, `README.txt`, `status.log`, `_render_order.json`.
Staging copy kept at `C:\AI\community\review\fc-take-chain-2026-11-04\pack\` (review/ is gitignored, by rule).

## One by-eye look, flagged as not judged

The coding model looked at `review_grid.png` (one mid-frame per cell, t=5 s) and reports, **as an unverified
by-eye sample, no VLM, no judge, not a quality claim**: a face readable at that single timestamp in 6 of 10 cells
(c03, c04, c06, c07, c08, c10; c01/c02/c05/c09 face away at t=5 s - most of those cells end on a face-beat, which
is what the plan asked for, so t=5 s is the wrong probe for them); and c10 reads as a continuity break in hair
tone and top vs the other nine. Per-cell contact sheets are in the pack for his eye. Nothing here is a KEEP.

## The ask (in notes\needs_derrick.md)

Watch `fc_take_chain_2026-11-04` on the QNAP, score the cells 0-10, name any KEEP. The seam behaviour
(0.540 s cumulative audio lead) is the known cost of the 60 ms crossfade; the seamless latent-tail variant stays a
labelled follow-up, not this pass.
