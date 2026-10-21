# P6 objective-metrics preview (no model)

Generated 2026-10-20 19:55 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `None` (0 calls, 0 failures, 0 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

**PREVIEW (--no-model): objective metrics only; no VLM scores, no pairwise. Not a final ranking.**

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_cuts` | 8.63 | - | - | 8.63 | - | - |
| 2 | `p6_1min_cuts_ab05` | 7.88 | - | - | 7.88 | - | - |
| 3 | `p6_1min_community` | 7.02 | - | - | 7.02 | - | - |
| 4 | `p6_1min_ab05` | 6.67 | - | - | 6.67 | - | - |
| 5 | `p6_1min_switchyard` | 4.42 | - | - | 4.42 | - | - |

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | - | - | - | - | - | - | - |
| `p6_1min_cuts_ab05` | - | - | - | - | - | - | - |
| `p6_1min_community` | - | - | - | - | - | - | - |
| `p6_1min_ab05` | - | - | - | - | - | - | - |
| `p6_1min_switchyard` | - | - | - | - | - | - | - |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | 0.539 | 1.168 | 0.0876 | 0.0068 | -0.4082 | 3.448 | 0.011 | 1.44 | 15 | 4.322 |
| `p6_1min_cuts_ab05` | 0.536 | 1.236 | 0.0974 | 0.0019 | -0.5137 | 4.854 | 0.004 | 0.75 | 14 | 5.135 |
| `p6_1min_community` | 0.459 | 1.199 | 0.2258 | 0.016 | -0.4062 | 6.095 | 0.01 | 2.29 | 4 | 4.051 |
| `p6_1min_ab05` | 0.364 | 1.138 | 0.2476 | 0.0139 | -0.4649 | 9.446 | 0.01 | 0.98 | 6 | 3.753 |
| `p6_1min_switchyard` | 0.887 | 1.255 | 0.226 | 0.197 | -0.5545 | 7.217 | 0.022 | 5.07 | 11 | 5.63 |
