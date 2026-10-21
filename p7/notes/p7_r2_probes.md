# P7 round 2 probes - why these three knobs (P7.2.1, 2026-10-21)

Sources read this iteration: `p7\KNOBS.md` (sections 2-3), C1 parent's latest review `p7\reviews\p7_r1_full_review\review.json` (C1's parent changed its latest review to that one), and `runs\P6_RANKING.json` (still the latest review for the C2 and C3 parents - neither earned a promoted full render in round 1). All three parents report `weakest_segment: 1`, so all three probes are segment 1 (KNOBS 3: probe the weakest segment, not the default 2). Nothing here touches Switchyard; no new people, images or LoRAs; every character is a fictional adult aged 21+ (canon `fiction-cond-lock.md`).

## C1 - `p7_r2_c1_sd1000` - seed on segment 1
- Parent `p6_1min_cuts`, latest review `p7_r1_full_review`: dims motion_quality 6.4, artifacts 6.7, pacing 7.7, prompt 7.5, burn 7.4, temporal 7.4, identity 8.7. Composite 7.732, no flags, weakest segment 1 (segment scores 6.5 / 7.55 / 7.7).
- The two lowest dims are 0.3 apart, so "no dim is clearly lowest (spread < 0.5)" - the seed row's own trigger. Seed 51080000 -> 51081000 on segment 1 only; beats untouched, so `reuse_prompts` from `p6_1min_cuts_seg1` and no LLM prompt writing.
- Why not `pmot` again: it is technically allowed (its probe was PROMOTE, so the twice-in-a-row rule does not block it), and motion_quality is nominally the lowest dim. But round 1 already paid 16 min for the probe and 47 min for the full clip, and the full clip lost the head-to-head 5.258 vs 7.732 with the judge picking the unmodified parent on all seven dims in both orders. Spending another ~63 min to re-ask the same question is the worst value left in the budget. The seed probe is the cheapest way to test whether segment 1's weakness is sample luck rather than setting.
- Why not `st12`: requires artifacts or temporal_consistency to be lowest; here they are 2nd and tied-4th. Also the same knob is already a known failure on C2 (worse artifacts, three new hard flags).
- `cut4` / `cut6` do not qualify: pacing_cuts 7.7 is not the lowest dim on this parent (it was 6th of 7).

## C2 - `p7_r2_c2_ab03` - anti-burn down on segment 1
- Parent `p6_1min_cuts_ab05` (antiburn 0.5), latest review `runs\P6_RANKING.json`: dims artifacts 6.8, motion 7.0, temporal 7.2, prompt 7.8, pacing 7.8, identity 8.7, burn 8.3. Composite 6.95, no flags, weakest segment 1 (7.25 / 8.95 / 8.0).
- The `ab03` row fires cleanly and measurably: burn is fine (burn_exposure 8.3, no flags, `clip_late_max` 0.0019 is the best number on the board), chunk 2 is soft (`sharp_drift_min` -0.5137 < -0.4, the worst sharpness drop of the three parents), on an anti-burn parent. This is the knob P7.1.1 deliberately held back for round 2 for this reason.
- Why not `sd`: its trigger also technically fires (artifacts 6.8 vs motion 7.0 is a 0.2 spread), but `ab03` has a named objective trigger that the harness re-measures, so a result is interpretable either way; `sd` stays available for round 3.
- Why not `st12` again: it was rejected on this exact slot last round and made its own target dim worse (artifacts 6.10 -> 5.70, plus `body_horror` / `identity_break` / `severe_burn`).

## C3 - `p7_r2_c3_pmot` - motion prompt clause on segment 1
- Parent `p6_1min_community`, latest review `runs\P6_RANKING.json`: dims motion_quality 7.4 (lowest), artifacts 7.5, temporal 8.0, burn 8.0, prompt 8.4, pacing 8.4, identity 9.2; hard flag `identity_break`, composite 5.764, weakest segment 1 (6.95 / 9.05 / 8.05).
- The `pmot` row is the decision table's pointer (motion_quality is the lowest dim) and it is the round-2 held-back knob from P7.1.1. Beat text changes, so segment 1 is left OUT of `reuse_prompts` and batch_queue writes fresh H3 prompts for it between iterations.
- Why not `ab05` again (rejected here last round), `ab07` (its change is 0.5 -> 0.7; this parent is `antiburn: null`, and the up-chain stopped when ab05 lost), `pexp` (only allowed after `ab07` fails): the whole anti-burn branch is closed for this slot this round even though `sat_drift_max` 0.2258 is still over 0.15 - report it, do not chase it.
- Why not `pid`: identity_consistency 9.2 is this parent's highest dim. Why not `cut4` / `cut6`: this parent has no cut clause, so cut knobs do not exist for it. Why not `sd`: same reasoning as C2 - `pmot` targets the lowest dim directly.
- Note for reading the verdict: the C1 round-1 experience says a PROMOTE at probe scale does not predict a full-clip PROMOTE. If C3's probe wins, the full render is still a ~47 min gamble.

## Cost written into this request
Three single-segment probes, two with prompts reused (no LLM time) and one with a beat rewrite for one segment: ~45 min at the measured 14.4-17.2 min per probe. Field after round 1 was 98.4 / 360 min, 7 / 16 jobs, 1 / 3 full renders. No result in `p7\jobs\` carries a `refused` field, so no budget stop applies.
