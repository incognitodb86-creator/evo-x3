# P7.3.1 - round 3 probes (2026-10-21, ~12:40 CT)

One probe, not three. Reason first, then the knob.

## Why round 3 is one probe and not three (the caps, not the minutes)

Read from the newest result files, not from the board's older planning paragraphs:

- `p7\jobs\p7_r2_full_review.result.json` (newest): `ok=true rc=0 wall_min 1.6 budget_used_min 194.6 budget_cap_min 360`. **165.4 GPU min left, no `refused` field anywhere**, so the GPU-minutes budget is not exhausted and round 3 is open.
- Jobs used: **13 of 16** - `p7_r1_rank`, `p7_r1_c1_pmot`, `p7_r1_c2_st12`, `p7_r1_c3_ab05`, `p7_r1_probe_review`, `p7_r1_c1_pmot_full`, `p7_r1_full_review`, `p7_r2_c1_sd1000`, `p7_r2_c2_ab03`, `p7_r2_c3_pmot`, `p7_r2_probe_review`, `p7_r2_c3_pmot_full_pool`, `p7_r2_full_review`. **3 job slots left** (`request_iterNN.json` files are the harness's archives, they cost nothing).

The three job slots left buy exactly one of these:

| plan | slots | result |
|---|---|---|
| 3 probes (what P7.3.1 asks for literally) | 3 -> 16/16 | probe review (P7.3.2) gets `refused: budget`, and **F1's `p7_final_rank` can never run**, so S1 has no winner to name. The loop ends in a BLOCKED summary. |
| **1 probe + 1 probe review + `p7_final_rank`** | 3 -> 16/16 | round 3 produces probe evidence, F1 runs, S1 names a winner. Cost ~15-17 (probe) + ~2 (probe review) + ~20-30 (final rank) = ~40-50 min, field ends ~235-245 of 360. |
| skip round 3, F1 only | 1 -> 14/16 | F1 runs, S1 names a winner, 2 slots and ~150 min unused. |

A round-3 probe can never change a parent under these slots: promotion needs probe + probe review + full render + full review = 4 slots. So round 3 is evidence only, and the deliverable (S1) must keep its slot. That is why the request has **one** render job. Full-render allowance left (1 of 3) is unreachable for the same reason: 2 slots for render + review, and F1 needs the last one.

## The three knob ledgers (decision table, from each parent's latest review)

- **C1 `p6_1min_cuts`** - latest review `p7\reviews\p7_r1_full_review\review.json` (whole clip, composite 7.732, `weakest_segment` 1). Lowest dims motion_quality 6.4 then artifacts 6.7 (spread 0.3 -> the seed row's "no dim clearly lowest" trigger fires), but **`sd` is barred**: it was C1's round-2 knob and lost, and KNOBS 3 bans repeating a knob whose last try was not promoted. `st12` needs artifacts lowest (it is 2nd). `cut4`/`cut6` need pacing_cuts lowest (it is 6th of 7). `pmot` is formally legal (its probe was promoted in round 1) and is the only authorised knob left - **already paid for at both scales** (16.4 min probe PROMOTE, 46.6 min full render, lost 5.258 vs 7.732 on the pairwise term). Reported, not re-spent.
- **C2 `p6_1min_cuts_ab05`** - latest review `p7\reviews\p7_r2_probe_review\review.json` **seg1 only** (parent re-scored 7.917 there, `weakest_segment` 1; the whole-clip 6.950 is only in `runs\P6_RANKING.json`). Parent's card in that review: **artifacts 6.1 lowest**, motion_quality 6.4 next (spread 0.3), so `pmot` is *not* authorised (motion is not the lowest dim on the parent's own card - the 5.4 in the Slots table is the ab03 child's card). `ab07` needs a burn trigger: sat_drift_max 0.0879 (< 0.15), clip_late_max 0.0005 (< 0.03), no `severe_burn` -> not authorised. `st12` is formally allowed again (not the immediately previous knob) but it is a measured failure on this parent (artifacts 6.10 -> 5.70, plus `body_horror`/`identity_break`/`severe_burn` flags). **`sd` is authorised twice over**: spread 0.3 < 0.5 and the "previous knob rejected twice" arm (round 1 `st12`, round 2 `ab03`, both rejected).
- **C3 `p6_1min_community`** - latest review `p7\reviews\p7_r2_full_review\review.json` (whole clip, composite 7.042, `weakest_segment` 1, segment scores 6.95 / 9.05 / 8.05). Lowest dims motion_quality 7.4 then artifacts 7.5 - **spread 0.1**, the tightest on the board, so the seed row's trigger fires on its own terms. C3 has never tried `sd`. `pmot` is legal only because its last try was promoted, and its full-clip test has now been paid for and lost (47.0 min); the board's own advice is not to spend a third `pmot`. `st12` needs artifacts to be the lowest dim (it is 2nd). `ab05` already lost (round 1), `ab07` needs a 0.5 parent, `pexp` needs `ab07` first, `pid` needs identity lowest (9.2 is the parent's highest), cut knobs do not exist on a parent with no cut clause.

## The probe I ran: C3, `sd1000`, segment 1

`shots\p7_r3_c3_sd1000.json` = `shots\pool_parents\p6_1min_community.json` seg1 copied byte for byte, **only** `id` and `seed` changed (51080000 -> **51081000**, the table's "seed + 1000 on the probed segment"). POOL image and the KNOBS section 2 image_note verbatim, 768x1344, `mode r2v`, `arm long_r2v`, `secs 10`, `chunk_secs 10`, one chunk, `steps 10`, `antiburn null`, no LoRAs. Probe segment = the parent's `weakest_segment` (1) in every review it appears in.

Why C3 and not C2, when both are authorised for `sd`:
1. C3's trigger is the strongest number on the board (0.1 spread) and the slot has no seed history; C2's is a tie-break on a slot with two rejections.
2. C3's parent is the only parent carrying a **hard flag** - `identity_break` from segment 1 window 1, worst_frame F4 - so this is the one probe in the round whose answer is readable outside the pairwise field term: the child's own per-window card, its flags and the objective table are in the review regardless of the verdict. If the flag survives a seed re-roll it is structural (beats/settings), if it disappears it is a seed lottery. C2 has no flags and no open objective signal, so a C2 seed probe is expected to return exactly what round 2's seed probe returned: a split (parent 4.837 vs child 4.889, `score_x` 0.5, `consistent` false) - noise.
3. Round 2's lesson on this knob is recorded as "treat seed re-rolls as noise, not signal", which is precisely the hypothesis worth one probe on the slot where a seed re-roll is the only untried move.

Honest limits of this probe:
- **The POOL/D15 confound applies.** The parent is a D15 run, so this child is POOL-vs-D15 and `p7_r2_full_review` already showed the judge's head-to-head reason being the image ("B's frames suffer from identity break (wrong hair/face)"). A `KEEP_PARENT` verdict here is expected to be the image, not the seed: read the child's own card, not the verdict.
- **It cannot change C3's parent** (no slots for a full render + review), and a single segment is not a run, so it cannot enter `p7_final_rank` either. It is evidence for Derek's summary, nothing more.
- **`reuse_prompts` is left out on purpose** (KNOBS 1 POOL rule: the parent is a D15 run whose prompts describe the D15 subject, the harness would skip the entries). batch_queue writes one fresh POOL prompt for seg1, ~5 min of LLM, which is inside the remaining budget.

## Request

`p7\JOB_REQUEST.json` = `{"request_id": "p7_r3_probes", "jobs": [{"kind": "render", "id": "p7_r3_c3_sd1000", "stitch": false}]}` - one render job, single segment, no stitch, no uploads.

Expected: ~15-17 GPU min (measured 14.4-17.2 for single-segment probes) + ~5 min of LLM prompt writing, field ~214/360, jobs 14/16.

## What P7.3.2-P7.3.5 and F1 should do with the remaining 2 slots

- P7.3.2: write the probe review `p7_r3_probe_review`, pairs `["p6_1min_community:seg1=p7_r3_c3_sd1000:seg1"]` (15/16). If a full render ever needs a slot, it does not have one.
- P7.3.3: **no promotion is possible** even on a PROMOTE verdict (a full render + its review need 2 slots, F1 needs the last) -> tick "no promotion (job slots)".
- P7.3.4: tick "skipped: nothing promoted".
- P7.3.5: record the verdict in History, parents unchanged (C1 `p6_1min_cuts`, C2 `p6_1min_cuts_ab05`, C3 `p6_1min_community`).
- F1: `p7_final_rank` over the three D15 parents (the only same-image field, per the Open items note; `p7_r2_c3_pmot_full_pool` is POOL and its parent is D15, so including it re-runs the confound). 16/16.
- S1: name the rank-1 of that field, and report the POOL question as open for Derek: the clean POOL answer needs a POOL version of each parent (3 full renders = 3 slots) which P7 can no longer afford.
