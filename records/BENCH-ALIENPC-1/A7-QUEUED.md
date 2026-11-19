# A7 TQ A/B, stage 1 queued (2026-11-19 17:09 CT, America/Chicago)

Derrick's go: t2881u ("yes start both"). Run dir on AlienPc: `C:\AI\community\runs\a7_tq_ab_20261119\`.
Fixed seed 51083601, the same approved start still and the same prompt as `h3max_lora_test_20261119\arm0_baseline`
(copied, not retyped). Same RefMods as arm0. No LoRAs. Candidate graphs filled on copies; templates untouched.
No arm needs KJNodes (disabled on AlienPc). Lease line `Max | A7 TQ A/B | 2026-11-19 17:09:10 CT`.

| pos | tag | template | request sha256 (first 12) |
|---|---|---|---|
| control | `h3max_lora_test_20261119/arm0_baseline` (live `oc_guide.api.json` 1-pass, identical graph, rendered 16:22-16:27 CT) | `oc_guide.api.json` | (not re-rendered) |
| 1 | `tq1_oc_guide_2pass` | `oc_guide_2pass.candidate.api.json` | 6b3ad7818ed2 |
| 2 | `tq1_oc_ref_1pass` | `oc_ref.api.json` | b918b6e35e66 |
| 3 | `tq1_oc_ref_2pass` | `oc_ref_2pass.candidate.api.json` | 718479ecaa54 |
| 4 | `tq4_two_person_b7` | `two_person.b7.candidate.api.json` (smoke; both refs = the one still) | 26bba5b5c406 |
| 5 | `tq4_ref2va_16x9_b7` | `ref2va_16x9.b7.candidate.api.json` (smoke, 1344x768) | 55e7275022e5 |
| 6 | `tq4_long_continuation_b7` | `long_continuation.b7.candidate.api.json` (smoke; beat-2 prompt = same prompt) | 9ff697348eba |

Frames and size come from each template (run_queue's graph-is-authority rule): TQ1 243f 768x1344 output,
TQ4 two_person / ref2va 124f 1344x768, long_continuation 243+238f 768x1344. RTX 2x post-pass on.

Prepared, not queued (wait for Derrick's eye pick of TQ1): TQ2 VSA `start_percent` 0.2 vs 0.0, TQ3 `res_multistep`
vs `euler`+`simple` (`er_sde` banned), optional lcm/simple audio check, TQ5 headers. Mystic LoRA audio arm waits on
Derrick. Note in the run dir: `STAGE2_PENDING.md`.
