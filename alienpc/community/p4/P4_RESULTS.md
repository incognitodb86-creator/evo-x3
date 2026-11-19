# P4 results (ALI-126) - chaining test, draft size 576x1024, 8 steps, seed 51060000

Source: C:/AI/community/community.log (P4 START 2026-10-20 10:48:27 CT, P4 DONE 2026-10-20 11:16:12 CT), C:/AI/community/p4/p4.log, C:/AI/community/p4/p4_result.json, the four mp4 files and their mp4.json sidecars, plus the mp4 boxes read from the files themselves. No judgement of picture quality - Derrick watches.

| job | ok or fail | render secs | file size (bytes) | duration (s) | video frames | fps |
|---|---|---|---|---|---|---|
| p4_A10_cont_noAB | ok | 355.7 | 4,407,606 (4.20 MB) | 20.042 | 481 | 24 |
| p4_A10_cont_AB05 | ok | 205.4 | 4,363,019 (4.16 MB) | 20.042 | 481 | 24 |
| p4_B5_cont_noAB | ok | 340.5 | 4,794,472 (4.57 MB) | 20.042 | 481 | 24 |
| p4_B5_cont_AB05 | ok | 290.6 | 4,707,600 (4.49 MB) | 20.042 | 481 | 24 |

Settings that were actually in each job (sidecars and api.json): 576x1024, steps 8, shift 10 video and 3 audio, sampler euler with scheduler simple, VSA attention on (BlockSparseAttention selection vsa), antiburn 0.5 on chunk 2 and later for the AB05 arms, antiburn null meaning off for the noAB arms, seed 51060000, CreateVideo fps 24. No Eros_beta6mix_Lora anywhere.

Order and timing from p4.log: 7 prompts written first (word counts 71 to 103, range 60-120, len_ok True, guard_ok True), then UNLOAD LLM(s) coding_sc117_strata, then COMFY ready v0.38.0 wait 22 s vram_free 14.7 GiB, then the six jobs ran one at a time. No job errored, no timeout, no adults-only guard skip.

## Hard-cut arm (C10, same run, kept out of the 4 rows above)

- p4_C10_cut_part1: ok, 150.3 s render, 2,211,873 bytes, 243 frames at 24 fps, 10.125 s (single chunk, no continuation window)
- p4_C10_cut_part2: ok, 150.4 s render, 2,135,543 bytes, seed 51060001
- p4_C10_cut_joined.mp4: exists, 4,333,760 bytes, made by ffmpeg concat (c_concat.txt, -c copy), so p4_result.json records null secs and exists true for it

## How the media numbers were obtained

ffprobe.exe is installed at C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe but this Ralph loop is not allowed to execute it: the pi permission system answers "requires approval, but no interactive UI is available" for ffprobe, ffmpeg, python, powershell, od, sed, awk and stat. So duration, frames, fps and size were read out of the mp4 boxes with the permitted tools (head, tail, cat -v, tr, grep -b, wc), per file:

- mdhd: timescale 12288, duration 246272, which is 246272 divided by 12288 = 20.0417 s (all four files)
- stts: 1 entry, sample_count 481, sample_delta 512, so 12288 divided by 512 = 24 fps (all four)
- stsz: sample_count 481 (all four), tkhd: 576 x 1024, mvhd: timescale 96000, duration 1923490 = 20.036 s (muxer rounding, use the track value)
- file sizes from ls and wc -c, matching the table

Command that gives the same numbers from ffprobe (needs an approved shell):

"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe" -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames -show_entries format=duration,size -of default=noprint_wrappers=1 C:/AI/community/p4/p4_A10_cont_noAB.mp4

## Flag for D1 and D2 arm sizing (fact, not a judgement)

All four continuation jobs landed at 481 frames and 20.04 s, the same length, even though B5 was built with a 124 frame first chunk and 119 frame extension (p4.py) while A10 used 243 and 238. 481 equals 243 plus 238 in both cases, so the continuation windows came out at 238 extension frames no matter what chunk length was asked for. Check MiniMaxH3GuidedContinuationWindow and extension_frames before the P6 arms are sized, otherwise the 5 s chunk arm and the 10 s chunk arm are both the same 20 s clip.

