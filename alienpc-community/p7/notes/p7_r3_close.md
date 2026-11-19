# P7.3.5 - round-3 close (2026-10-21 ~13:10 CT)

Round 3 is closed. No parent changed, and by the rules none could. No GPU work requested, none run.

## The one question this task had to answer

`p7\reviews\p7_r3_full_review\review.json` - read it **if any**. There is none, and "none" is provable, not assumed:

- `p7\reviews` contains exactly five folders: `p7_r1_full_review`, `p7_r1_probe_review`, `p7_r2_full_review`, `p7_r2_probe_review`, `p7_r3_probe_review`. No `p7_r3_full_review`.
- `p7\jobs` contains 15 `*.result.json` files. The only round-3 ones are `p7_r3_c3_sd1000.result.json` and `p7_r3_probe_review.result.json`. No `p7_r3_*_full*` result exists, so there was never a full render to review.
- `p7\JOB_REQUEST.json` is **not on disk** (P7.3.2's request is archived at `p7\jobs\request_iter05.json`). Nothing runs after this iteration; the GPU stays untouched.
- `C:\AI\community\shots\p7_r3*` is only the probe shot file - P7.3.3 wrote no full shot list, because the verdict was KEEP_PARENT.

KNOBS section 4: a new parent is created only by a **full render** whose full-vs-parent review says PROMOTE. Round 3 had no full render (its single probe lost: KEEP_PARENT, child 4.92 vs parent 8.015 in `p7_r3_probe_review`), and a full render + its review would have needed job slots 16 **and** 17 while slot 16 belongs to F1's `p7_final_rank`. So round 3 was evidence-gathering by design, exactly as P7.3.1 booked it.

## Final Slots state (all three rounds, unchanged from R2's picks)

| slot | parent | why it is the parent |
|---|---|---|
| C1 | `p6_1min_cuts` | P6 rank 1; round-1 `pmot` full render lost (5.258 vs 7.732); round-2 `sd` probe was a split; round 3 asked for nothing (`pmot` was the only authorised knob, barred by job slots) |
| C2 | `p6_1min_cuts_ab05` | P6 rank 2; round-1 `st12` lost (artifacts got worse), round-2 `ab03` moved nothing measurable, round 3 asked for nothing (`sd` authorised, barred by job slots) |
| C3 | `p6_1min_community` | P6 rank 3; round-1 `ab05` lost; round-2 `pmot` **PROMOTED** at probe scale, its full render `p7_r2_c3_pmot_full_pool` lost (5.379 vs 7.042); round-3 `sd1000` probe lost (4.92 vs 8.015) |

Parent cards after the close, each named by the field it came from (composites are field-relative - never compare across reviews):

- C1 7.732 whole-clip (`p7_r1_full_review`).
- C2 6.950 clip (`P6_RANKING`); 7.917 seg1-only (6-candidate `p7_r2_probe_review`).
- C3 7.042 clip (`p7_r2_full_review`); 5.764 (`P6_RANKING`); 8.015 seg1-only (2-candidate `p7_r3_probe_review`, abs 7.118, objective 9.45, **no flags**).

## Budget, closed (newest result: `p7\jobs\p7_r3_probe_review.result.json`)

`ok=true`, `rc=0`, `wall_min 1.1`, `budget_used_min 212.3`, `budget_cap_min 360`, **no `refused` field in any of the 15 result files**. So this close is by verdict, not by budget:

- GPU minutes: **212.3 of 360**, 147.7 left unused on purpose.
- Job slots: **15 of 16** used (every job that P7.3.1 planned, nothing extra). Slot 16 is F1's `p7_final_rank`.
- Full renders: **2 of 3** (both lost). The remaining allowance is unusable - a render needs a render slot plus a review slot.

## P7 totals for S1, in one line

5 probes, 3 probe reviews, 2 full renders, 2 full reviews, 1 rank job = 15 jobs / 212.3 GPU min / **2 PROMOTE probes at probe scale, 0 parent changes**. `pmot` is the only knob that ever won, twice at segment scale; both full-clip tests of it lost, and all four losses (round-1 full, round-2 full, round-3 probe, round-2 C1 split) were decided by the per-review pairwise field term (weight 0.40), three of them with the child ahead on every absolute dim and on the CPU objective metrics.

## What F1 / S1 must do with this

1. `p7_final_rank` cands = the 3 slot parents (`p6_1min_cuts`, `p6_1min_cuts_ab05`, `p6_1min_community`). The P6 #1 is C1, already on the board, so no 4th candidate is needed; `p6_1min_switchyard` ranked 5th and is not a batch_queue shot list. All three are D15 with identical beats/seeds, so that ranking is same-image and internally comparable - unlike every POOL-vs-D15 verdict on this board.
2. Ask for **exactly one job**. Slot 16 is the last one.
3. Name the winner from `p7_final_rank` rank 1, and carry the pairwise-term finding, the `sd`-is-noise finding (two trials, both noise), the non-reproducing `identity_break` on C3 seg1, and the POOL/D15 confound as open questions for Derek. The detailed evidence is in the History rows and in `p7_r3_promotions.md` / `p7_r3_probes.md`.

## Checks run by this task

- `python C:/AI/community/p7/_scratch/p733_table_check.py` -> header 10 columns, **16 rows, 0 bad**; 5 of the 16 rows are round 3 (C3 probe, C3 probe review, C1 not-requested, C2 not-requested, this close row). That is this task's check.
- No JSON was written (nothing to request), so `json.tool` had nothing to check.
- Nothing else touched: KNOBS.md, scripts, `p7\jobs\*`, `p7\reviews\*`, `runs\P6_RANKING.*`, ComfyUI, no renders, no llama-swap, no GPU. Files written by this task: `runs\P7_LEADERBOARD.md` (Slots rows, a round-3 close note, one round-3 History row, Budget/Rounds bullets) and this note.
