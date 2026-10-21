# P7 round 1 probe plan - how each knob was picked (P7.1.1, 2026-10-20 late CT)

Sources read this iteration: `p7\KNOBS.md` (sections 2, 3, 5, 6), `runs\P6_RANKING.json` (the latest review of all three round-1 parents),
`shots\p6_1min_cuts.json`, `shots\p6_1min_cuts_ab05.json`, `shots\p6_1min_community.json`, `runs\P7_LEADERBOARD.md`,
`scripts\p6_review.py` `check_shots` / `ALLOWED_KEYS` (read only), `ralph-community\ralph.ps1` lines 155-201 (job validation, read only).
No GPU, no llama-swap, no ComfyUI, no image or video opened. All characters are fictional adults aged 21+.

## Weakest segment

`P6_RANKING.json` gives `"weakest_segment": 1` for all three parents (C1 segment_scores seg1 6.5 < seg2 7.55 < seg3 7.7; C2 seg1 7.25 < seg3
8.0 < seg2 8.95; C3 seg1 6.95 < seg3 8.05 < seg2 9.05). KNOBS section 3 says probe the parent's `weakest_segment`, so **all three round-1
probes are segment 1** (ids end `_seg1`, seed 51080000 kept, as required for a fair compare).

## C1 = `p6_1min_cuts` (composite 7.682) -> knob `pmot`

Dims: motion_quality **6.4**, artifacts 6.7, temporal 7.4, burn 7.4, prompt 7.5, pacing 7.7, identity 8.7. Lowest dim is motion_quality by 0.3,
no tie, so the tie order is not needed. KNOBS row `pmot` = "motion_quality or prompt_adherence" -> prompt clause
" Slow, smooth, continuous movement with natural weight." appended to the end of `beat` AND to the end of the single chunk, nothing else changed.
Not `st12`: that row needs artifacts or temporal to be the lowest dim (artifacts is 6.7, second, not lowest).
Not `cut4`/`cut6`: pacing_cuts 7.7 is not lowest even though this parent has the cut clause.
Not `sd`: some dim is clearly lowest. No `ab05`: sat_drift_max 0.0876 < 0.15 and clip_late_max 0.0068 < 0.03, no `severe_burn` flag.
Because `pmot` changes beat text, the job is **left out of `reuse_prompts`** so batch_queue writes fresh prompts for it (KNOBS section 1).
Known cost of that: the child differs from the parent by the clause plus new LLM wording, which is exactly what KNOBS prescribes for `p_*` knobs.

## C2 = `p6_1min_cuts_ab05` (composite 6.950) -> knob `st12`

Dims: artifacts **6.8**, motion_quality 7.0, temporal 7.2, pacing 7.8, prompt 7.8, burn 8.3, identity 8.7. Lowest dim is artifacts ->
KNOBS row `st12` = steps 10 -> 12, prompts reused (beat text untouched). Its own objective penalty table agrees it is the blur/artifact arm:
`blur_drift 1.0` (the maximum) and `sharp_drift_min -0.5137`, `sharpness 337.8` (worst of the three parents).
`ab03` (0.5 -> 0.3) also qualifies by its own condition - anti-burn parent with `sharp_drift_min` < -0.4 - but `st12` is the row that matches the
lowest dimension, so `st12` goes first and `ab03` stays available for round 2 (never the same knob twice in a row, and this would be C2's first try).

## C3 = `p6_1min_community` (composite 5.764, hard flag `identity_break`) -> knob `ab05`

Dims: motion_quality **7.4**, artifacts 7.5, temporal 8.0, burn 8.0, prompt 8.4, pacing 8.4, identity 9.2. 7.4 vs 7.5 is not an exact tie, so the
tie order technically points at `pmot`; `ab05` is nevertheless legal by its own written trigger. Chosen `ab05` (antiburn null -> 0.5, prompts
reused) because the objective trigger fires harder here than anywhere on the board: `sat_drift_max 0.2258` is 1.5x the 0.15 threshold,
`clip_late_max 0.016`, and `burn_sat_drift 1.41` + `burn_clip 0.18` are the two largest burn penalties in the whole P6 set (objective_score 7.02
is the weakest of the three parents). Anti-burn is also the one knob whose effect the objective metrics re-measure, so round 1 gets a measurable
result on the only parent whose composite is dragged down by the objective component.
`pmot` (motion 7.4) is therefore held back for round 2 for this slot if `ab05` does not promote; `pexp` is not allowed until `ab07` fails; `pid`
is not allowed because identity_consistency is this parent's *highest* dim (9.2) despite the `identity_break` flag - flagged for Derek in the
leaderboard's open items rather than chased here.

## Same-knob / cap check

Three different knobs this round (pmot, st12, ab05), one per slot, no slot has a previous attempt, so the "never the same knob twice in a row"
rule is satisfied. 0 of 3 full renders used (probes are not full renders). Expected GPU cost per KNOBS 6: 3 x ~15 min probes = ~45 min, then the
3-pair probe review ~8-10 min; budget file `p7_budget.json` does not exist yet, so `BudgetGet` reports 0 of 360 min and 0 of 16 jobs.

## Files written by P7.1.1

- `shots\p7_r1_c1_pmot.json` (1 shot, `p7_r1_c1_pmot_seg1`)
- `shots\p7_r1_c2_st12.json` (1 shot, `p7_r1_c2_st12_seg1`, steps 12)
- `shots\p7_r1_c3_ab05.json` (1 shot, `p7_r1_c3_ab05_seg1`, antiburn 0.5)
- `p7\JOB_REQUEST.json` (request_id `p7_r1_probes`, 3 render jobs, `stitch: false`)
- `p7\notes\p7_r1_probes.md` (this file), plus 3 planned rows in `runs\P7_LEADERBOARD.md` History

Checked against `check_shots`: ids `<job_id>_seg1`; only `ALLOWED_KEYS`; image D15 in APPROVED; 768x1344; steps int 8-12 (10 and 12); seed
51080000 positive int; antiburn null or 0.5; mode r2v; arm long_r2v; secs 10 and chunk_secs 10; one chunk; all strings <= 1500 chars; adults-only
guard text unchanged apart from the appended clause. `reuse_prompts` entries pass the ralph.ps1 regexes and both source prompt folders exist
(`runs\p6_1min_cuts_ab05\prompts\p6_1min_cuts_ab05_seg1_c0_long_r2v.txt` + `_c1_long_cont.txt`,
`runs\p6_1min_community\prompts\p6_1min_seg1_c0_long_r2v.txt` + `_c1_long_cont.txt`).
