# P7 comparison

Generated 2026-10-21 14:39 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (8 calls, 0 failures, 41 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_community:seg1` | 6.74 | 7.12 | 5.00 | 9.45 | - | 1 |
| 2 | `p7_r3_c3_sd1000:seg1` | 6.20 | 7.41 | 5.00 | 9.93 | identity_break | 1 |

## Verdicts (child vs parent)

- `p7_r3_c3_sd1000:seg1` vs `p6_1min_community:seg1`: **KEEP_PARENT** (composite 6.20 vs 6.74, pairwise consistent child win=False)

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_community:seg1` | 6.00 | 7.00 | 8.00 | 9.00 | 7.40 | 5.80 | 7.40 |
| `p7_r3_c3_sd1000:seg1` | 6.60 | 7.60 | 8.30 | 9.30 | 7.90 | 6.20 | 7.50 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_community:seg1` | 0.244 | 1.156 | -0.2693 | 0.016 | -0.083 | 6.095 | 0.002 | 0.0 | 0 | 4.425 |
| `p7_r3_c3_sd1000:seg1` | 0.259 | 1.129 | -0.1505 | 0.0124 | -0.0015 | 2.877 | 0.0 | 0.0 | 0 | 4.017 |

## Judge reasons (global call)

- `p6_1min_community:seg1`: motion_quality: Struggles with natural weight; some poses feel rubbery, especially in F5-F8 where motion is abrupt.; temporal_consistency: Minor flicker and shimmer in background lights; slight texture boiling in F7-F8.; burn_exposure: Skin has warm, slightly orange tint; exposure consistent but not perfectly natural.; identity_consistency: Face, hair, and body remain consistent across all frames; outfit changes are cleanly executed.; prompt_adherence: Beat 1: Untying strap and letting it fall is shown clearly. Beat 2: Swaying and looking back is captured with good rhythm.; artifacts: Minor hand/finger errors in F5-F8; slight melting at hip edges in F7-F8.; pacing_cuts: Cuts land cleanly; rhythm of the beat is readable, though some transitions feel slightly jarring.
- `p7_r3_c3_sd1000:seg1`: motion_quality: Rubbery strap release, slow sway lacks weight; frozen poses dominate.; temporal_consistency: Minor flicker in water highlights; background stable.; burn_exposure: Slight orange tint in skin, exposure consistent.; identity_consistency: Face, hair, outfit match reference across all frames.; prompt_adherence: Beat 1: strap removal incomplete; Beat 2: sway and turn not fully executed.; artifacts: Melting water droplets, duplicated hands in F5, warped hips in F12.; pacing_cuts: Cuts land cleanly but rhythm feels uneven; F10-F12 feel rushed.
