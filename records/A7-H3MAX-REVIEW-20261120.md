# H3max A7 / TQ4 clip review — 2026-11-20

Date: 2026-11-20 7:35 AM CT (America/Chicago). Reviewer: Max. No images or prompt prose are in this file. Clips stay on the QNAP; hashes are in [BENCH-ALIENPC-1/QNAP-MEDIA-INDEX-20261120.md](./BENCH-ALIENPC-1/QNAP-MEDIA-INDEX-20261120.md).

The video model refused to review the clips. This review used frames sampled 4–7 times per clip, plus ffmpeg YDIF motion stats. Audio was not judged.

## Production setup

The baseline `tq1_oc_ref_2pass` (euler/simple, VSA 0.0, prompt headers kept) stays as the production setup. None of the A7 stage-2 changes beat it. The earlier `tq2_vsa_0.2` promotion (`4d909034`) is **not** the pick pending Derrick; do not treat `tq2_vsa_0.2` as promoted.

## A7 stage-2 vs baseline

- `tq2_vsa_0.2`: oilier, more plastic skin, and a distorted face near the start. YDIF max spike 17.9, against 15.9 for the baseline.
- `tq3_lcm_simple`: softer, waxier, with a high spike of 17.1.
- `tq3_res_multistep`: about equal, with more motion (mean 9.6 vs 7.6).
- `tq5_headerfree`: weaker match to the face in the still.

`tq2_vsa_0.0`, `tq3_euler_simple`, and `tq5_headers` were already recorded as controls copied from the `tq1_oc_ref_2pass` winner (byte-identical) and were not used as independent comparisons.

## A7 stage-1

- `oc_ref_1pass` is close to 2-pass.
- `guide_2pass` is the smoothest (YDIF sd 1.89) but its face drifts after about 6 s.

## TQ4

- `tq4_long_continuation_b7` is consistent across the 10 s join, with slight face drift.
- `tq4_ref2va_16x9_b7` and `tq4_two_person_b7` are only 5.2 s, and their first frame is a tight crop before cutting to a wide shot.

TQ4 still waits on Derrick's eye pick before any promotion. No 16:9 2-pass candidate exists.
