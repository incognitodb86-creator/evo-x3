# P7 comparison

Generated 2026-10-21 08:04 CT by `C:\AI\community\scripts\p6_review.py` - rubric p7-rubric-v1 (2026-10-20), judge `qwen3vl_judge` (8 calls, 0 failures, 28 s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.

composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).

| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |
|---|---|---|---|---|---|---|---|
| 1 | `p6_1min_cuts_ab05:seg1` | 6.64 | 7.19 | 5.00 | 8.81 | - | 1 |
| 2 | `p7_r1_c1_pmot:seg1` | 6.39 | 6.73 | 5.00 | 8.49 | - | 1 |
| 3 | `p6_1min_community:seg1` | 6.00 | 7.16 | 5.00 | 9.45 | body_horror | 1 |
| 4 | `p7_r1_c3_ab05:seg1` | 5.23 | 7.10 | 5.00 | 9.44 | body_horror, frozen | 1 |
| 5 | `p7_r1_c2_st12:seg1` | 5.05 | 7.04 | 5.00 | 8.69 | body_horror, identity_break, severe_burn | 1 |
| 6 | `p6_1min_cuts:seg1` | 4.84 | 6.23 | 5.00 | 9.23 | body_horror, broken_cut, frozen, identity_break, severe_burn | 1 |

## Verdicts (child vs parent)

- `p7_r1_c1_pmot:seg1` vs `p6_1min_cuts:seg1`: **PROMOTE** (composite 6.39 vs 4.84, pairwise consistent child win=False)
- `p7_r1_c2_st12:seg1` vs `p6_1min_cuts_ab05:seg1`: **KEEP_PARENT** (composite 5.05 vs 6.64, pairwise consistent child win=False)
- `p7_r1_c3_ab05:seg1` vs `p6_1min_community:seg1`: **KEEP_PARENT** (composite 5.23 vs 6.00, pairwise consistent child win=False)

## Dimensions (1-10, higher is better)

| candidate | motion_quality | temporal_consistency | burn_exposure | identity_consistency | prompt_adherence | artifacts | pacing_cuts |
|---|---|---|---|---|---|---|---|
| `p6_1min_cuts_ab05:seg1` | 6.40 | 7.40 | 8.00 | 9.00 | 7.40 | 6.10 | 7.10 |
| `p7_r1_c1_pmot:seg1` | 6.20 | 6.70 | 8.70 | 8.00 | 6.80 | 6.70 | 7.10 |
| `p6_1min_community:seg1` | 6.00 | 7.00 | 8.30 | 9.00 | 7.70 | 5.80 | 7.40 |
| `p7_r1_c3_ab05:seg1` | 6.30 | 7.30 | 8.30 | 8.60 | 7.30 | 5.60 | 7.30 |
| `p7_r1_c2_st12:seg1` | 6.40 | 6.60 | 8.00 | 8.60 | 7.30 | 5.70 | 7.00 |
| `p6_1min_cuts:seg1` | 5.40 | 6.40 | 8.00 | 7.70 | 6.70 | 5.60 | 6.60 |

## Objective metrics (CPU, no model)

| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |
|---|---|---|---|---|---|---|---|---|---|---|
| `p6_1min_cuts_ab05:seg1` | 0.412 | 1.188 | 0.0879 | 0.0005 | -0.3016 | 4.854 | 0.006 | 0.0 | 3 | 3.167 |
| `p7_r1_c1_pmot:seg1` | 0.316 | 1.307 | 0.0001 | 0.0021 | -0.373 | 4.413 | 0.043 | 0.0 | 3 | 3.214 |
| `p6_1min_community:seg1` | 0.244 | 1.156 | -0.2693 | 0.016 | -0.083 | 6.095 | 0.002 | 0.0 | 0 | 4.425 |
| `p7_r1_c3_ab05:seg1` | 0.233 | 1.145 | -0.3164 | 0.0156 | -0.1073 | 6.333 | 0.0 | 0.0 | 0 | 4.27 |
| `p7_r1_c2_st12:seg1` | 0.421 | 1.118 | 0.1195 | 0.0005 | -0.3231 | 4.553 | 0.006 | 0.0 | 3 | 3.345 |
| `p6_1min_cuts:seg1` | 0.378 | 1.137 | 0.0423 | 0.0068 | -0.4082 | 2.192 | 0.022 | 0.0 | 3 | 3.136 |

## Judge reasons (global call)

- `p6_1min_cuts_ab05:seg1`: motion_quality: Smooth transitions, but some poses feel slightly rubbery, especially in F7-F8.; temporal_consistency: Minor flicker in F5-F6, background slightly shifts in F7-F8, but overall stable.; burn_exposure: Skin has warm, consistent glow; no severe burn, but slight orange tint in later frames.; identity_consistency: Face, hair, and outfit remain consistent across all frames and cuts.; prompt_adherence: Actions follow prompt: untie strap, cut to close-up, turn, sway, look back. All beats executed.; artifacts: Minor hand/finger blurring in F5-F6, slight melting in F7-F8, but no major body errors.; pacing_cuts: Cuts land cleanly at 5.9s and 10.8s, rhythm readable, no jarring transitions.
- `p7_r1_c1_pmot:seg1`: motion_quality: Smooth transitions, natural weight, but slight rubbery quality in limb movement.; temporal_consistency: Minor flicker in background lights and slight shimmer on skin, but no major morphing.; burn_exposure: Natural skin tones and lighting, no burnt highlights or oversaturation.; identity_consistency: Face, hair, and outfit remain consistent across frames and cuts, with minor variations in pose.; prompt_adherence: Actions and cuts follow the prompt accurately, including the requested close-up and movement sequence.; artifacts: Minor hand/finger errors and slight melting in some frames, especially in close-ups.; pacing_cuts: Cuts land cleanly and follow the beat, with no jarring transitions.
- `p6_1min_community:seg1`: motion_quality: Struggles with natural weight; some poses feel rubbery, especially in F5-F8 where motion is abrupt.; temporal_consistency: Minor flicker and shimmer in background lights; slight texture boiling in F7-F8.; burn_exposure: Skin has warm, slightly orange tint; exposure consistent but not perfectly natural.; identity_consistency: Face, hair, and body remain consistent across all frames; outfit changes are cleanly executed.; prompt_adherence: Beat 1: Untying strap and letting it fall is shown clearly. Beat 2: Swaying and looking back is captured with good rhythm.; artifacts: Minor hand/finger errors in F5-F8; slight melting at hip edges in F7-F8.; pacing_cuts: Cuts land cleanly; rhythm of the beat is readable, though some transitions feel slightly jarring.
- `p7_r1_c3_ab05:seg1`: motion_quality: Motion is stiff and rubbery, especially in F9-F12 where limbs and torso appear to melt or stretch unnaturally.; temporal_consistency: Minor flicker and shimmer in F5-F8; background remains stable but lighting shifts slightly across frames.; burn_exposure: Skin has warm, slightly orange glow; exposure is consistent but not perfectly natural, with minor contrast creep in later frames.; identity_consistency: Face, hair, and body remain consistent across frames; outfit state changes correctly per prompt, though F9-F12 show slight body distortion.; prompt_adherence: Beat 1 (untie strap) is partially shown but incomplete; Beat 2 (turn, sway, look back) is mostly captured but lacks smooth transition between poses.; artifacts: F9-F12 show noticeable body distortion, melting limbs, and duplicated/overlapping body parts; skin texture is overly smooth and plastic-like.; pacing_cuts:
- `p7_r1_c2_st12:seg1`: motion_quality: Smooth but slightly rubbery transitions; some motion blur in fast moves.; temporal_consistency: Minor flicker and background shimmer; slight drift in lighting.; burn_exposure: Slight overexposure on skin in later frames; otherwise natural.; identity_consistency: Face and hair consistent; outfit mostly intact except for strap removal.; prompt_adherence: Actions mostly followed; cut timing slightly off in close-up transition.; artifacts: Minor hand/finger errors; slight melting in F12; duplicated limbs in F8.; pacing_cuts: Cuts land mostly correctly; slight jarring in F5-F6 transition.
- `p6_1min_cuts:seg1`: motion_quality: Motion is stiff and rubbery, especially in F3-F4 and F8-F12; actions lack natural weight and timing.; temporal_consistency: Minor flicker and shimmer in F5-F6; background bokeh slightly shifts between frames.; burn_exposure: Skin has warm, slightly orange tint; exposure consistent but not natural; no severe burn.; identity_consistency: Face, hair, and body remain consistent across frames; outfit state matches reference except for F3-F4 where top is removed.; prompt_adherence: Beat 1: Untying strap and cut to close-up are present; Beat 2: Swaying and shoulder look are partially captured but not fully synchronized.; artifacts: F5-F6 show slight hand/finger melting; F10-F12 show minor facial warping and duplicated shoulder regions.; pacing_cuts: Cut at 5.9s (F4) is jarring; pacing of Beat 2 is uneven with slow drift in F7-F8.
