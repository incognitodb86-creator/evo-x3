# 2026-11-03 - three REF2VA prompts for the blowjob POV act at three lengths (15-second test)

Record of: `C:\AI\community\runs\bj_pov_len_20261103\` (prompts + graphs + queue + `prompts.md`). No render run, no GPU, no lock, harness not running.

## Asks

Derrick, via Max: use the REF2VA prompt skill to write "her sucking my dick" three ways - short, medium, long - so a later render shows which style wins. "I want three videos, each 15 seconds long, as a test."

## Built

| arm | words | chars | sha256 (12) | seed | frames |
|---|---|---|---|---|---|
| `p_short` | 1,391 | 7,901 | `cb34d906277f` | 51083130 | 362 |
| `p_medium` | 2,010 | 11,358 | `2530c96e4ea8` | 51083131 | 362 |
| `p_long` | 2,895 | 16,282 | `69f850e0e579` | 51083132 | 362 |

One act, one continuous shot: the woman of the nightclub start frame kneels at the seated man's thighs, braces with both hands, takes his penis into her mouth, works continuous deep oral strokes at one cycle per 1.5 s, ends mid-stroke alive on the last frame.

Fixed across arms: the four references (`start_bj` = `<Picture 1>` anchor, `face_a`/`face_b` = `<Picture 2>`/`<Picture 3>` attribute transfer, `start_pov` = `<Picture 4>` for his lap and penis), the definitions, the verbatim R11 identity clause, the retention lines and markers, `[reference generation]`, the clock ranges 00:00.000-00:15.083, the tempo, camera, light, audio cues, no speech. Only the amount of detail changes: short = compressed definitions + one sentence per beat; medium = full definition block + 2-3 sentences per beat; long = + material/light inventory + per-beat body/wardrobe/hand detail + per-frame continuity (R20).

## Rules used

R1-R31 from `h3-prompting`; R32-R44 from `h3-max-ref2va-prompt`: R32 (no `overall_soundscape:` / `non_diegetic_music:`, plain R7 cues), R33 (four wired pictures declared, no `<Video>`/`<Audio>` labels, his scene kept inside `<Picture 4>`), R34 (the `[reference generation]` subset), R35 (per-shot retention lines with markers, action line, hand lock), R36 (frame-anchor prose, no keyframe-alignment line), R37 (speech left off), R38 (all English), R39 (style sentences before `[Shot 1]`), R40 (no `<scenetrans>`), R41 (no word cap; upstream 350-500 is hosted style, the real limit is tokenizer overflow ~3100 text tokens), R42 (paste matches the graph), R44 (gate).

## Graph and math

Base = `runs/bj_pov_kf_20261102/d1_kf/request.api.json` (B2 REF2VA, standing beta7 line: `ref_image_size: "max"`, Euler/simple 8 steps, shift 12/3, VSA keep_percent 10, base 672x384 -> latent upscaler 2.0 -> 1344x768, pass 2 3 steps denoise 0.4 with the start frame as first-frame guide, audio VAE, 24 fps). Per arm: prompt bytes, `c0.length=362`, `ref_images.ref_image_4` + `img4`, unique seed, prefix. 362 frames = 15.083 s at 24 fps, 24f-aligned; prompts written to that endpoint. Builder `build_graphs.py`, ids `_prompt_ids.json`, queue `_render_order.json`.

## Honest limits

- The measured KEEP length on this lane is 124 f; the longest ever run here is 243 f (6 min wall). 362 f has never run on this box: expected ~13-16 min per clip, ~45 min for the three in one GPU window. Wall time and tokenizer overflow are part of what this test measures.
- The three arms share one seed series by design (one axis = length), so per-arm variance is unknown: a difference this small is a hint, not a result (R30).
- Short prompt was not taken to 350-500 words: the four-label set, the R11 clause and the R35 lines are mandatory and set a floor near 1,400 words. So "short" here means the shortest compliant REF2VA paste, not a caption.
- `p_long` is 2,895 words; if it overflows the tokenizer the queue logs the error at that arm and the other two are unaffected.
- Audio cues are written; audio quality on this lane is judged by ears (TenStrip #77).

## Gate (R44, run 2026-11-03, output in `prompts.md`)

`guard_ok` True x3, `adult_stated` True x3, minors-risky 0 x3, `then|after|afterwards|next` 0 and negatives 0 in `detailed_description` x3, banned wording 0 x3, four sections in order x3, clock ranges contiguous to 00:15.083 x3, `PRIMARY MOTION` stated 3-4 times with tempo/amplitude/last-frame continuity in each, labels exactly the four wired pictures + three subjects, `run_queue.py --run-dir runs/bj_pov_len_20261103 --dry-run` = 3 clips, no GPU call.

## Next

Render needs Derek's GO (R30): harness up, then `python scripts/run_queue.py --run-dir runs/bj_pov_len_20261103`. Judging is by eyes per R17-R19, with wall time recorded per arm.
