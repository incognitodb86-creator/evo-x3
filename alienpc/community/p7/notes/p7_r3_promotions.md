# P7.3.3 - round-3 promotions (2026-10-21, ~13:05 CT)

One verdict to read: `p7_r3_probe_review`. Sources read this iteration:

- `p7\reviews\p7_r3_probe_review\review.json` + `.md` (verdicts, pairs, per-window cards, objective tables)
- `p7\jobs\p7_r3_c3_sd1000.result.json` - ok=true rc=0, wall 16.6 min, `budget_used_min 211.2` of 360, note `batch_queue rc=0 rendered=1/1 prompts_reused=0 stitch=False`, no `refused`
- `p7\jobs\p7_r3_probe_review.result.json` - ok=true rc=0, wall 1.1 min, `budget_used_min 212.3` of 360, 8 judge calls / 0 failures / 51.9 s, no `refused`
- `p7\KNOBS.md` sections 1-4 (request format, POOL shot rules, knob table, promotion rule + caps)

## Verdict: KEEP_PARENT - so P7.3.3 requests nothing

`verdicts[0]` = parent `p6_1min_community:seg1`, child `p7_r3_c3_sd1000:seg1`, **`verdict: KEEP_PARENT`**,
`consistent_child_win: false`, `parent_composite: 8.015`, `child_composite: 4.92`.
`pairs[0]`: `score_x 1.0`, `consistent: true` - `xy` winner A and `yx` winner B are both the parent, on all 7 dims in both orders.
No PROMOTE arm applies (needs a consistent child win with +0.25, or +0.75 alone; the child is 3.1 **below**).

Written by this task: **no** `shots\p7_r3_c3_*_full.json`, **no** `p7\JOB_REQUEST.json`. There is no `JOB_REQUEST.json` on disk (P7.3.2's
request was archived to `p7\jobs\request_iter05.json` when the harness ran it, 12:49), so nothing is re-run after this iteration. No GPU work.
Full-render allowance stays **2 of 3**; C3's parent stays `p6_1min_community`.

## Why the child lost, in numbers (the fourth loss on the same term)

| | child `p7_r3_c3_sd1000:seg1` | parent `p6_1min_community:seg1` |
|---|---|---|
| composite | 4.92 | 8.015 |
| abs VLM card | **7.405** | 7.118 |
| objective | **9.93** (penalties: burn_clip 0.07 only) | 9.45 (tex_flicker 0.03, burn_clip 0.18, color_drift 0.34) |
| pairwise (field) | 1.806 | **8.194** |
| hard flags | `identity_break` (-0.75) | none in this review |
| dims (child/parent) | motion 6.6/6.0, temporal 7.6/7.0, burn 8.3/8.0, identity 9.3/9.0, prompt 7.9/7.4, artifacts 6.2/5.8, pacing 7.5/7.4 - **child higher on all seven** | |
| objective detail | `sat_drift_max` -0.1505, `clip_late_max` 0.0124, `sharp_drift_min` -0.0015, `color_drift_max` 2.877, `freeze` 0.0, sharpness 436.4, sat_mean 0.3373, motion 4.017 | -0.2693 / 0.016 / -0.083 / 6.095 / 0.002 / 414.4 / 0.5212 / 4.425 |

Composite arithmetic checks out: child 0.4(7.405) + 0.4(1.806) + 0.2(9.93) - 0.75 = 4.92. Strip the 0.75 flag penalty and it is 5.67 -
still 2.3 behind, so the flag is not what lost it either. The whole gap is the pairwise field term (0.4 weight, 1.806 vs 8.194 = 2.55 composite).
This is the **fourth** time on this board and the **third** for C3: `p7_r1_full_review` (child better on all 7 abs dims, lost 5.258 vs 7.732),
`p7_r2_full_review` (child better on abs + objective + no flags, lost 5.379 vs 7.042), `p7_r2_probe_review` C1 seed (split), and now this one.
Read plainly: on this harness a single-segment POOL child cannot beat a re-scored D15 parent in the 2-candidate pairwise field, because the
pairwise term is re-based to the field and the head-to-head reason is the image - `yx` reason: "B matches reference perfectly: same hair,
outfit, lighting... A has wrong hair color, wrong setting". A = the child (blonde) in that order. The `compare` ref files confirm the
mechanism: `ref_D15.jpg` for the parent, `ref_POOL.jpg` for the child, and the head-to-head has one reference in front of the judge.

## The answer to the question this probe was built to answer

P7.3.1 asked whether `p6_1min_community` seg1's `identity_break` flag (`P6_RANKING`, window 1, worst_frame F4) is **structural or a seed
lottery**. Evidence, round 3, same beats, seed 51080000 -> 51081000, POOL:

- The **parent** in this 2-candidate review carries **no flags at all**, and its own window 2 raises `body_horror` + `frozen` (worst_frame F5)
  - the `identity_break` from `P6_RANKING` did **not** reproduce.
- The **child** raises `identity_break` + `severe_burn` + `body_horror` + `frozen` in window 2 (worst_frame F2) while its window 1 is clean.
- So the flag is a per-render window event, not a property of seed 51080000 or of that beat: it moved with the roll. The parent's identity
  dimension (9.0-9.3) never drops, matching the `P6_RANKING` note that its identity_consistency is the highest of the five.
- A seed re-roll also improved every objective measure on this segment (`color_drift_max` 6.095 -> 2.877, `sat_drift_max` -0.2693 -> -0.1505,
  `sharp_drift_min` -0.083 -> -0.0015, `freeze` -> 0.0) and its abs card. **Seed changes are real variance, not a knob that improves the video**:
  round 2's C1 seed probe was a split; this one is a win on every measured side and a loss in the field. Do not read `sd` as progress.

## Judge-quality caveat (for S1, new this round)

The same score vector **6/7/8/9/7/5/7** appears four times in this review: the parent's window 1, the parent's window 2, the child's window 2,
and the child's global card - with near-verbatim reasons ("Hands slide down but motion feels rubbery, no weight or timing realism" on both
videos). The child's window 1 is 8/9/9/10/10/9/10. Two output modes, repeated across different videos and windows. Treat per-window judge
numbers as low-information; the objective table (pure CPU) and the direction of the head-to-head are the usable signals. `p6_review.py`
`compare` costs 1.1 min wall for 8 calls, so a review is cheap - the thing that is not cheap is a render.

## What this leaves for F1 / S1

- Slots unchanged: C1 `p6_1min_cuts`, C2 `p6_1min_cuts_ab05`, C3 `p6_1min_community` - all three are the original P6 runs.
- Budget **212.3 of 360 min**, jobs **15 of 16**. The last slot belongs to F1's `p7_final_rank` (~20-30 min expected). The remaining
  full-render allowance is unusable: a render + its review = 2 slots and only 1 exists.
- Round 3 changed no parent and asked for nothing - it is evidence, and the evidence is: the only knob that ever won is `pmot` (twice at
  probe scale, lost twice at full scale); `ab03` moved nothing; `st12` made its own target dim worse; `sd` is variance. Nothing in P7
  promoted a setting, so `p7_final_rank` will be ranking the three P6 parents against each other, on POOL-free (D15) footage.
