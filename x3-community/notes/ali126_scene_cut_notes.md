# 2.6 (ALI-126/128) - ~1 min 16:9 review cut, hard-cut with ffmpeg

Built by `C:/AI/community/notes/ali126_scene_cut_build.py` (the only writer of these files).
Method: the FFmpeg project's own concat page `https://trac.ffmpeg.org/wiki/Concatenate` (saved body `notes/web/07ff_trac_concat.html`): concat demuxer, and
`-c copy` is only valid when every input shares codec + canvas + rate, which is measured here, not assumed.
Stitch mode used: `copy`. ffmpeg `C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe` / ffprobe `C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe` (8.0.1-full_build).

Objective numbers only. `KEEP` is Derrick's alone (AGENTS.md), and this file has no vision judge,
no ranking and no quality claim. Every row below is re-measured off disk by ffprobe `-of json` parsed by
field name; `--check` recomputes them and fails on drift. Nothing was rendered, queued or fetched by this item.

## Scene folder (open this)

- folder: `C:/AI/community/runs/ali126_scene1_hc169`
- cut: `C:/AI/community/runs/ali126_scene1_hc169/scene_hardcut.mp4`
- contact sheet: `C:/AI/community/runs/ali126_scene1_hc169/contact_sheet.png` (1344x512, one mid-clip frame per input, grid order = the row order below)
- media lives under `runs/`, which is gitignored (.gitignore:10), so the committed record is this doc + the manifest

## Hard-cut arm (the scene that exists)

| # | clip | s | frames | canvas | fps | v/a codec | audio | bytes | sha256-16 |
|---|------|---|--------|--------|-----|-----------|-------|-------|-----------|
| 1 | ali147_pool_hc_r1_s51130001 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 2774534 | b5f78becd371b800 |
| 2 | ali147_pool_hc_r2_s51130002 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 3831791 | 55cef572bab00c30 |
| 3 | ali147_pool_hc_r3b_s51130003 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 3527348 | d125b8feb11e4aea |
| 4 | ali147_pool_hc_r4_s51130004 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 3712205 | c031b097817e0ca0 |
| 5 | ali147_pool_hc_r5_s51130005 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 2543598 | 87b8dd7f54f1702d |
| 6 | ali147_pool_hc_r6_s51130006 | 10.125 | 243 | 1344x768 | 24/1 | h264/aac | 10.125 32000Hz 2ch | 3650591 | 9f17cddfa1e72c70 |
| **sum** |  6 clips | **60.75** | **1458** | 1344x768 | 24/1 |  |  |  |  |

Measured scene: `scene_hardcut.mp4` = 60.75 s, 1458 video packets, 1344x768, 24/1 fps, video h264 + audio aac 32000Hz 2ch, 19871740 bytes, sha256 `4d37f6851afb717a03c2ba6c66e272e6d02a37213fba5369fc2660a6925c5037`.

Target: 60.0 s +/- 5.0 (item text: ~1 min from 5-10 s clips). Measured total of the pool = 60.75 s; each clip
is 5.0-10.5 s, so 6 clips is the shortest cut that reaches ~1 min and 6 is what the 16:9 pool holds at
one clip per seed (51130001, 2, 3, 4, 5, 6). Clip order is by seed, which is deterministic and is NOT a
narrative edit: beat order and any KEEP are Derrick's.

## Continuation material on disk (the A/B row)

| arm / clip | s | frames | canvas | fps | audio | bytes |
|------------|---|--------|--------|-----|-------|-------|
| ali173_cont_hc1_s51140001 | 10.0 | 240 | 1024x576 | 24/1 | aac 32000Hz 2ch | 1986190 |
| p6_1min_cuts_stitched(2026-10-20 hard-cut arm) | 60.125 | 1443 | 768x1344 | 24/1 | aac 32000Hz 2ch | 16064702 |
| p6_1min_community_stitched(2026-10-20 continuation arm) | 60.125 | 1443 | 768x1344 | 24/1 | aac 32000Hz 2ch | 14138495 |

Objective consequence: the only 16:9 continuation render on disk is `ali173_cont_hc1_s51140001` (10.0 s,
1024x576), so a continuation arm of the same ~60 s at 1344x768 cannot be cut from the material that
exists; the 2026-10-20 continuation arm is 768x1344 vertical. A same-canvas, same-seed A/B therefore needs a
render window (fix_plan 2.6b), and scaling 1024x576 into 1344x768 would compare an upscale, not a method.

## Independent proof (commands run by hand, outside this builder)

```
ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0 \
        runs/ali126_scene1_hc169/scene_hardcut.mp4   -> 1344,768,24/1,1458
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of csv=p=0 \
        runs/ali126_scene1_hc169/scene_hardcut.mp4   -> aac,32000,2,60.782
ffprobe -v error -show_entries format=duration,size -of csv=p=0 ...   -> 60.782000,19871740
certutil.exe -hashfile runs/ali126_scene1_hc169/scene_hardcut.mp4 SHA256   -> 4d37f6851afb717a03c2ba6c66e272e6d02a37213fba5369fc2660a6925c5037
```

The container duration (60.782000 s) is longer than the video stream (60.75 s = 1458 packets at 24/1 fps) because the concat
demuxer keeps each source's packet timeline; the video stream is what `-count_packets` counts, so the frame
proof is 1458 = 6 x 243.
A note for AGENTS.md's proof line: raw `-show_streams` output is `key=value`, so a `,audio,` substring test
finds 0 hits; use `-select_streams a:0 ... -of csv` (measured 0 vs 1 on this file).

## Reproduce

```
python C:/AI/community/notes/ali126_scene_cut_build.py --build
python C:/AI/community/notes/ali126_scene_cut_build.py --check    # expect: PROBLEMS 0 VERDICT CLEAN
python C:/AI/community/notes/ali126_scene_cut_build.py --selftest # expect: SELFTEST_CLEAN seeds=14 fired=14 silent=0 real_tree_problems=0
```

