# P6 ranking - five one-minute videos

Generated 2026-10-21 13:09 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (27 calls, 0 failures, 108 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_cuts` | 7.20 | 6.82 | 6.86 | 8.63 | - | 1 |
| 2 | `p6_1min_cuts_ab05` | 6.54 | 7.42 | 5.00 | 7.88 | - | 1 |
| 3 | `p6_1min_community` | 5.77 | 7.78 | 3.15 | 7.02 | - | 1 |

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | 6.40 | 7.40 | 7.40 | 8.70 | 7.50 | 6.70 | 7.70 |
| `p6_1min_cuts_ab05` | 7.00 | 7.20 | 8.30 | 8.70 | 7.80 | 6.80 | 7.80 |
| `p6_1min_community` | 7.40 | 8.00 | 8.00 | 9.20 | 8.40 | 7.50 | 8.40 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_cuts` | 0.539 | 1.168 | 0.0876 | 0.0068 | -0.4082 | 3.448 | 0.011 | 1.44 | 15 | 4.322 |
| `p6_1min_cuts_ab05` | 0.536 | 1.236 | 0.0974 | 0.0019 | -0.5137 | 4.854 | 0.004 | 0.75 | 14 | 5.135 |
| `p6_1min_community` | 0.459 | 1.199 | 0.2258 | 0.016 | -0.4062 | 6.095 | 0.01 | 2.29 | 4 | 4.051 |

## Judge reasons (global call)

- `p6_1min_cuts`: motion_quality: Weight and timing mostly natural, but some frames show slight rubbery transitions.; temporal_consistency: Minor flicker and shimmer in background lights, but no major morphing or boiling textures.; burn_exposure: Skin shows slight orange saturation and contrast creep, especially in later frames.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All beats and cuts occur as described, with clear transitions and rhythm.; artifacts: Minor hand/finger errors and slight melting in some close-ups, but no major body part duplication.; pacing_cuts: Cuts land cleanly at requested points, with no jarring transitions or rhythm disruption.
- `p6_1min_cuts_ab05`: motion_quality: Some motion blur and slight floatiness in transitions, but overall natural timing.; temporal_consistency: Minor flicker and texture shimmer in background and skin, especially in F3/F4.; burn_exposure: Skin tones warm and slightly over-saturated, but exposure remains consistent.; identity_consistency: Face, hair, and body remain consistent across frames and cuts, with minor variations in expression.; prompt_adherence: Most actions and cuts follow the prompt, though some poses are slightly off-beat.; artifacts: Minor hand/finger errors and slight melting in F8/F12, but no major body distortions.; pacing_cuts: Cuts land mostly on beat, but F6/F10 show slight jarring transitions.
- `p6_1min_community`: motion_quality: Smooth, weighted movements; no floaty or rubbery motion.; temporal_consistency: Minor shimmer in background lights; no major morphing or flicker.; burn_exposure: Slight over-saturation in skin tones; exposure drifts slightly over time.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: All beats and cuts occur as described, with clear transitions.; artifacts: Minor hand/finger blurring in some frames; otherwise clean.; pacing_cuts: Cuts land precisely on beat markers; rhythm is readable and smooth.
