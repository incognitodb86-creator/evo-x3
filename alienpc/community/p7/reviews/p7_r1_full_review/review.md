# P7 comparison

Generated 2026-10-21 08:58 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (16 calls, 0 failures, 70 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_cuts` | 7.73 | 6.82 | 8.19 | 8.63 | - | 1 |
| 2 | `p7_r1_c1_pmot_full` | 5.26 | 7.33 | 1.81 | 8.02 | - | 3 |

## Verdicts (child vs parent)

- `p7_r1_c1_pmot_full` vs `p6_1min_cuts`: **KEEP_PARENT** (composite 5.26 vs 7.73, pairwise consistent child win=False)

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | 6.40 | 7.40 | 7.40 | 8.70 | 7.50 | 6.70 | 7.70 |
| `p7_r1_c1_pmot_full` | 7.10 | 7.80 | 7.90 | 9.00 | 8.10 | 7.60 | 8.30 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | 0.539 | 1.168 | 0.0876 | 0.0068 | -0.4082 | 3.448 | 0.011 | 1.44 | 15 | 4.322 |
| `p7_r1_c1_pmot_full` | 0.613 | 1.217 | 0.0766 | 0.0018 | -0.7914 | 4.896 | 0.016 | 0.87 | 13 | 4.498 |

## Judge reasons (global call)

- `p6_1min_cuts`: motion_quality: Weight and timing mostly natural, but some frames show slight rubbery transitions.; temporal_consistency: Minor flicker and shimmer in background lights, but no major morphing or boiling textures.; burn_exposure: Skin shows slight orange saturation and contrast creep, especially in later frames.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All beats and cuts occur as described, with clear transitions and rhythm.; artifacts: Minor hand/finger errors and slight melting in some close-ups, but no major body part duplication.; pacing_cuts: Cuts land cleanly at requested points, with no jarring transitions or rhythm disruption.
- `p7_r1_c1_pmot_full`: motion_quality: Smooth, weighted motion with natural timing; slight rubbery quality in some transitions.; temporal_consistency: Minor flicker in F5/F6; background remains stable; no major morphing.; burn_exposure: Skin tones slightly oversaturated in later frames; highlights begin to burn slightly.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All actions, cuts, and settings match prompt exactly; rhythm clear and readable.; artifacts: Minor hand/finger blurring in F10/F11; otherwise clean with no body melting.; pacing_cuts: Cuts land precisely as requested; no jarring joins; beat rhythm clear.
