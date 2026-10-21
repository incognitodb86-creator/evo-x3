# P7 comparison

Generated 2026-10-21 09:57 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (8 calls, 0 failures, 28 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p7_r2_c3_pmot:seg1` | 8.12 | 7.10 | 8.19 | 10.00 | - | 1 |
| 2 | `p6_1min_cuts_ab05:seg1` | 7.92 | 7.19 | 8.19 | 8.81 | - | 1 |
| 3 | `p7_r2_c2_ab03:seg1` | 5.17 | 6.57 | 1.81 | 9.08 | - | 1 |
| 4 | `p7_r2_c1_sd1000:seg1` | 4.89 | 6.63 | 5.00 | 8.68 | body_horror, broken_cut, frozen, identity_break, severe_burn | 1 |
| 5 | `p6_1min_cuts:seg1` | 4.84 | 6.23 | 5.00 | 9.23 | body_horror, broken_cut, frozen, identity_break, severe_burn | 1 |
| 6 | `p6_1min_community:seg1` | 4.73 | 7.16 | 1.81 | 9.45 | body_horror | 1 |

## Verdicts (child vs parent)

- `p7_r2_c1_sd1000:seg1` vs `p6_1min_cuts:seg1`: **KEEP_PARENT** (composite 4.89 vs 4.84, pairwise consistent child win=False)
- `p7_r2_c2_ab03:seg1` vs `p6_1min_cuts_ab05:seg1`: **KEEP_PARENT** (composite 5.17 vs 7.92, pairwise consistent child win=False)
- `p7_r2_c3_pmot:seg1` vs `p6_1min_community:seg1`: **PROMOTE** (composite 8.12 vs 4.73, pairwise consistent child win=True)

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p7_r2_c3_pmot:seg1` | 6.80 | 7.30 | 8.30 | 8.40 | 7.10 | 6.40 | 7.70 |
| `p6_1min_cuts_ab05:seg1` | 6.40 | 7.40 | 8.00 | 9.00 | 7.40 | 6.10 | 7.10 |
| `p7_r2_c2_ab03:seg1` | 5.40 | 6.70 | 8.00 | 8.40 | 6.80 | 6.10 | 7.10 |
| `p7_r2_c1_sd1000:seg1` | 6.00 | 7.00 | 8.00 | 8.30 | 6.40 | 5.00 | 6.60 |
| `p6_1min_cuts:seg1` | 5.40 | 6.40 | 8.00 | 7.70 | 6.70 | 5.60 | 6.60 |
| `p6_1min_community:seg1` | 6.00 | 7.00 | 8.30 | 9.00 | 7.70 | 5.80 | 7.40 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p7_r2_c3_pmot:seg1` | 0.249 | 1.151 | -0.2066 | 0.0092 | 0.0816 | 1.441 | 0.008 | 0.0 | 0 | 3.783 |
| `p6_1min_cuts_ab05:seg1` | 0.412 | 1.188 | 0.0879 | 0.0005 | -0.3016 | 4.854 | 0.006 | 0.0 | 3 | 3.167 |
| `p7_r2_c2_ab03:seg1` | 0.415 | 1.162 | 0.0674 | 0.0005 | -0.3016 | 4.854 | 0.002 | 0.0 | 3 | 3.085 |
| `p7_r2_c1_sd1000:seg1` | 0.381 | 1.12 | 0.0745 | 0.0009 | -0.4866 | 4.427 | 0.011 | 0.0 | 3 | 3.195 |
| `p6_1min_cuts:seg1` | 0.378 | 1.137 | 0.0423 | 0.0068 | -0.4082 | 2.192 | 0.022 | 0.0 | 3 | 3.136 |
| `p6_1min_community:seg1` | 0.244 | 1.156 | -0.2693 | 0.016 | -0.083 | 6.095 | 0.002 | 0.0 | 0 | 4.425 |

## Judge reasons (global call)

- `p7_r2_c3_pmot:seg1`: motion_quality: Smooth transitions, natural weight, but slight rubbery quality in later frames.; temporal_consistency: Minor flicker in background lights and slight texture shimmer in F5-F8.; burn_exposure: Consistent warm skin tones, no burnt highlights or oversaturation.; identity_consistency: Face, hair, and outfit remain consistent across all frames and cuts.; prompt_adherence: Actions follow prompt: untie top, slide hands down, sway, look back, bite lip.; artifacts: Minor hand/finger errors in F9-F12, slight melting at edges in F11-F12.; pacing_cuts: Cuts land cleanly, rhythm readable, no jarring transitions.
- `p6_1min_cuts_ab05:seg1`: motion_quality: Smooth transitions, but some poses feel slightly rubbery, especially in F7-F8.; temporal_consistency: Minor flicker in F5-F6, background slightly shifts in F7-F8, but overall stable.; burn_exposure: Skin has warm, consistent glow; no severe burn, but slight orange tint in later frames.; identity_consistency: Face, hair, and outfit remain consistent across all frames and cuts.; prompt_adherence: Actions follow prompt: untie strap, cut to close-up, turn, sway, look back. All beats executed.; artifacts: Minor hand/finger blurring in F5-F6, slight melting in F7-F8, but no major body errors.; pacing_cuts: Cuts land cleanly at 5.9s and 10.8s, rhythm readable, no jarring transitions.
- `p7_r2_c2_ab03:seg1`: motion_quality: Strained motion: strap drop and sway feel rubbery, not weighty; some frames frozen.; temporal_consistency: Minor flicker in background lights; slight shimmer on skin; background drifts slightly.; burn_exposure: Skin has warm, slightly orange glow; highlights are natural but not perfectly balanced.; identity_consistency: Face, hair, body, and outfit remain consistent across all frames and cuts.; prompt_adherence: Beat 1: strap drop and cut to face are executed; Beat 2: pose and sway are present.; artifacts: Minor hand/finger errors in F5, F6; slight melting in F7; duplicated strap in F8.; pacing_cuts: Cuts land cleanly; rhythm is readable; no jarring joins between shots.
- `p7_r2_c1_sd1000:seg1`: motion_quality: Motion is mostly smooth but lacks weight; some frames show slight floatiness, especially in limb transitions.; temporal_consistency: Minor flicker and shimmer in background lights; no major morphing, but some texture instability in skin.; burn_exposure: Skin tones are warm and consistent; no severe burn, but highlights are slightly over-saturated in later frames.; identity_consistency: Face, hair, and body remain consistent across frames; outfit state matches reference, though strap removal is slightly delayed.; prompt_adherence: Beat 1 actions are mostly followed, but the cut to close-up is slightly off-timing; Beat 2 motion is incomplete and lacks full sway.; artifacts: Minor hand/finger errors in F5-F6; slight melting in F10-F12; duplicated limbs in F11; warped face in F12.; pacing_cuts: Cuts land mostly on beat, but F4-F5 and F10-F11 are slightly jarring; rhythm is re
- `p6_1min_cuts:seg1`: motion_quality: Motion is stiff and rubbery, especially in F3-F4 and F8-F12; actions lack natural weight and timing.; temporal_consistency: Minor flicker and shimmer in F5-F6; background bokeh slightly shifts between frames.; burn_exposure: Skin has warm, slightly orange tint; exposure consistent but not natural; no severe burn.; identity_consistency: Face, hair, and body remain consistent across frames; outfit state matches reference except for F3-F4 where top is removed.; prompt_adherence: Beat 1: Untying strap and cut to close-up are present; Beat 2: Swaying and shoulder look are partially captured but not fully synchronized.; artifacts: F5-F6 show slight hand/finger melting; F10-F12 show minor facial warping and duplicated shoulder regions.; pacing_cuts: Cut at 5.9s (F4) is jarring; pacing of Beat 2 is uneven with slow drift in F7-F8.
- `p6_1min_community:seg1`: motion_quality: Struggles with natural weight; some poses feel rubbery, especially in F5-F8 where motion is abrupt.; temporal_consistency: Minor flicker and shimmer in background lights; slight texture boiling in F7-F8.; burn_exposure: Skin has warm, slightly orange tint; exposure consistent but not perfectly natural.; identity_consistency: Face, hair, and body remain consistent across all frames; outfit changes are cleanly executed.; prompt_adherence: Beat 1: Untying strap and letting it fall is shown clearly. Beat 2: Swaying and looking back is captured with good rhythm.; artifacts: Minor hand/finger errors in F5-F8; slight melting at hip edges in F7-F8.; pacing_cuts: Cuts land cleanly; rhythm of the beat is readable, though some transitions feel slightly jarring.
