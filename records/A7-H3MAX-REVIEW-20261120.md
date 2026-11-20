# H3max A7 / TQ4 clip review — 2026-11-20

Reviewer: Max. No images or prompt prose are in this file. Clips stay on the QNAP; hashes are in [BENCH-ALIENPC-1/QNAP-MEDIA-INDEX-20261120.md](./BENCH-ALIENPC-1/QNAP-MEDIA-INDEX-20261120.md).

The video model refused to review the clips. Both passes used frames sampled 4–7 times per clip, plus ffmpeg YDIF motion stats. Audio was not judged. The comparison against the starting setup is one seed only.

## Verdict (comparison done before 7:43 AM CT; confirmed by Derrick t3013u at 7:43 AM CT)

The original starting setup stays production: `h3max_lora_test_20261119/arm0_baseline`, which is the live `oc_guide.api.json` 1-pass at 768×1344 with MiniMaxH3AddGuide (first frame pinned) and `ref_image_size=match`.

Derrick t3013u (7:43 AM CT): "Ok update the plan that we are staying with our original setup." TQ1, TQ2, TQ3, and TQ5 are closed as not promoted. `oc_ref_2pass` is not promoted; its only real gain on this seed was about 70 s faster, and that speed trade was declined. The earlier `tq2_vsa_0.2` promotion (`4d909034`) is closed, not the pick. **Correction (2026-11-20 ~8 AM CT):** `4d909034` is still in place. `oc_ref_2pass.api.json` is allowlisted, and `pick_template()` still routes default portrait `ref` clips to it on `mono`, X3 live and AlienPc. Nothing was edited this morning. Undoing it waits on Derrick's go.

## How the tq1 graphs differ from the start

Compared with the arm0_baseline `oc_guide` 1-pass:

- `oc_ref_1pass` is the same graph with no AddGuide and `ref_image_size=max`.
- `oc_ref_2pass` renders at 384×672, then a 2× latent upscale and a 3-step beta refine at denoise 0.4.

## Measurements vs the starting setup (before 7:43 AM CT)

YDIF mean / sd / max:

| Region | start (`oc_guide` 1-pass) | `oc_ref_1pass` | `oc_ref_2pass` |
|---|---:|---:|---:|
| Full frame | 7.19 / 2.13 / 12.1 | 7.89 / 2.12 / 13.2 | 7.53 / 2.59 / 15.8 |
| Background strip (top 12%) | 4.22 / 2.47 / 9.4 | 5.75 / 3.06 / 11.3 | 4.91 / 3.09 / 14.9 |

Job time: start 304.7 s, `oc_ref_2pass` 235.3 s (about 70 s faster).

On the frames, the starting setup has the sharpest faces and the closest match to the still. `oc_ref_2pass` faces are softer and more smoothed. 2-pass did not reduce background flicker on this seed.

## A7 stage-2 (7:35 AM CT, vs `tq1_oc_ref_2pass`)

None of the stage-2 changes beat `tq1_oc_ref_2pass` (euler/simple, VSA 0.0, prompt headers kept):

- `tq2_vsa_0.2`: oilier, more plastic skin, and a distorted face near the start. YDIF max spike 17.9, against 15.9 for that baseline.
- `tq3_lcm_simple`: softer, waxier, with a high spike of 17.1.
- `tq3_res_multistep`: about equal, with more motion (mean 9.6 vs 7.6).
- `tq5_headerfree`: weaker match to the face in the still.

`tq2_vsa_0.0`, `tq3_euler_simple`, and `tq5_headers` were already recorded as controls copied from the `tq1_oc_ref_2pass` winner (byte-identical) and were not used as independent comparisons.

## A7 stage-1 notes (7:35 AM CT)

- `oc_ref_1pass` is close to 2-pass.
- `guide_2pass` is the smoothest (YDIF sd 1.89) but its face drifts after about 6 s.

Those stage-1 notes do not change the verdict above: production stays the original `oc_guide` 1-pass.

## TQ4 (7:35 AM CT)

- `tq4_long_continuation_b7` is consistent across the 10 s join, with slight face drift.
- `tq4_ref2va_16x9_b7` and `tq4_two_person_b7` are only 5.2 s, and their first frame is a tight crop before cutting to a wide shot.

TQ4 still waits on Derrick's eye pick before any promotion. No 16:9 2-pass candidate exists.
