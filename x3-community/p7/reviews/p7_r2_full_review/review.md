# P7 comparison

Generated 2026-10-21 12:20 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (16 calls, 0 failures, 71 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_community` | 7.04 | 7.78 | 8.19 | 7.02 | identity_break | 1 |
| 2 | `p7_r2_c3_pmot_full_pool` | 5.38 | 7.81 | 1.81 | 7.67 | - | 1 |

## Verdicts (child vs parent)

- `p7_r2_c3_pmot_full_pool` vs `p6_1min_community`: **KEEP_PARENT** (composite 5.38 vs 7.04, pairwise consistent child win=False)

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_community` | 7.40 | 8.00 | 8.00 | 9.20 | 8.40 | 7.50 | 8.40 |
| `p7_r2_c3_pmot_full_pool` | 7.40 | 7.60 | 8.40 | 9.30 | 8.50 | 7.50 | 8.30 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_community` | 0.459 | 1.199 | 0.2258 | 0.016 | -0.4062 | 6.095 | 0.01 | 2.29 | 4 | 4.051 |
| `p7_r2_c3_pmot_full_pool` | 0.512 | 1.213 | 0.0042 | 0.0596 | 0.0086 | 6.861 | 0.02 | 0.87 | 3 | 4.272 |

## Judge reasons (global call)

- `p6_1min_community`: motion_quality: Smooth, weighted movements; no floaty or rubbery motion.; temporal_consistency: Minor shimmer in background lights; no major morphing or flicker.; burn_exposure: Slight over-saturation in skin tones; exposure drifts slightly over time.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All beats and cuts occur as described, with clear transitions.; artifacts: Minor hand/finger blurring in some frames; otherwise clean.; pacing_cuts: Cuts land precisely on beat markers; rhythm is readable and smooth.
- `p7_r2_c3_pmot_full_pool`: motion_quality: Smooth transitions, natural weight, but some frames show slight rubbery limb motion.; temporal_consistency: Minor flicker in background lights and slight shimmer on skin in some frames.; burn_exposure: Natural exposure and color, slight orange tint on skin in later frames.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All beats and cuts occur as described, with clear, readable rhythm.; artifacts: Minor hand/finger errors and slight melting in some poses, especially F10-F12.; pacing_cuts: Cuts land cleanly, rhythm is readable, no jarring transitions.
