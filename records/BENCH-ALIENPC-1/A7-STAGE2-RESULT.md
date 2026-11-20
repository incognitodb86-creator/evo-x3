# A7 stage 2 — TQ2 / TQ3 / TQ5 on tq1_oc_ref_2pass — 2026-11-19

All times are America/Chicago (CT). Doer: Max Architect executor. Derrick t2948u (6:48 PM CT): "Go... Don't wait on my go, complete the damn plan."

TQ1 winner (Max video review): `tq1_oc_ref_2pass` 6.0/10, ahead of `tq1_oc_guide_2pass` 5/10 and `tq1_oc_ref_1pass` 4/10. Recorded in `A7-QUEUED.md`. Base request sha256 `718479ecaa544c46a73f8027b987c2d627044cd1d26864f9ce92f674670508b0`. Same still, prompt sha `6adb8150…`, seed **51083601**. Winner defaults: `m_vsa.start_percent=0.0`, `ksel.sampler_name=euler`, `s0_sched=simple` 8 steps, pass-2 `p2sched=beta` 3 steps denoise 0.4, 4-header prompt. Templates were not edited.

Run dir: `C:\AI\community\runs\a7_stage2_20261119\`. Lease `Max | A7 stage-2 TQ2/TQ3/TQ5 | 2026-11-19 18:51:17 CT`, cleared 19:13:35 CT. `gpu-render.lock` acquired 18:51:57 (pid 26968), released 19:09:27. BATCH rc=0, done=4/4. RTX 2x ULTRA post-pass on. No LoRA names, RefMod names, character names, or prompt text in this file.

## Clip verification

Queued arms each changed **only the named field** from a copy of the winner request. Every queued arm is 243 frames, 768x1344 raw with audio, then RTX 2x to 1536x2688.

| Arm | Field changed | Request sha256 | prompt_id | JOB s | OBJECTIVE (raw) | UPSCALE | Upscaled sha256 |
|---|---|---|---|---:|---|---|---|
| `tq2_vsa_0.2` | `m_vsa.start_percent` 0.0 → 0.2 | `f1b44c7bdd79…` | `d01592ee-7083-4c17-8e97-b67422871834` | **246.9** (18:53:01–18:57:11) | 243f 768x1344 audio yes 7,201,822 B | 8.9 s, 31,804,032 B, 1536x2688 | `7E7123BFE7882EBFB4BF0DCB1BA5BEBA03F82244A22C93ECF0A08160F8980AD9` |
| `tq3_res_multistep` | `ksel.sampler_name` euler → res_multistep | `992ce04dbac3…` | `075e7c00-493f-41fd-bc52-163ab0ae62b0` | **225.9** (18:57:16–19:01:05) | 243f 768x1344 audio yes 7,719,611 B | 7.3 s, 31,864,172 B | `C7EB51E35B90D9659337BFD8FA7CE3C6FE35395A3036F6238E326226CA66DBF4` |
| `tq3_lcm_simple` | `ksel.sampler_name` euler → lcm (s0 scheduler already simple; pass-2 beta left alone) | `962ab06cc502…` | `15c3f76a-2900-462a-80af-8d599c643081` | **223.3** (19:01:08–19:04:55) | 243f 768x1344 audio yes 7,260,188 B | 7.4 s, 31,163,080 B | `4C8BE299B506F331D467C795E95FD12FA099E15FDF37F24E5A685C06EE40179A` |
| `tq5_headerfree` | `c0.prompt` only, via `beta7_convert.py --mode plain` (READY, 2397 vs 3509 chars, 4 header labels removed) | `2443d333f4d0…` | `1ae80109-5c6c-42f0-abb2-cc99735872ba` | **231.9** (19:04:58–19:08:53) | 243f 768x1344 audio yes 7,299,360 B | 7.3 s, 32,283,021 B | `D0DE484675402916B6FF21C6BD1DAD67930C714A6534447D6AB03BDF9517CCB7` |

Controls (field-identical to the winner, **not re-queued**). Upscaled clip copied from stage 1; sha matches the winner:

| Arm | Why control | JOB s (winner) | Upscaled sha256 |
|---|---|---:|---|
| `tq2_vsa_0.0` | start_percent already 0.0 | 235.3 (17:18:39–17:22:38) | `0677CB7611A39C6BB61DDA809BF7CB29D216B9ECF3F843B50441A3E9607890B9` |
| `tq3_euler_simple` | already euler + simple on pass 1 | 235.3 | same `0677CB76…` |
| `tq5_headers` | already 4-header prompt | 235.3 | same `0677CB76…` |

Winner control raw was 7,068,488 B; upscale 7.1 s, 31,132,812 B. Time vs control: VSA 0.2 was +11.6 s; `res_multistep` −9.4 s; `lcm` −12.0 s; header-free −3.4 s. `er_sde` was not used.

NAS: `\\NAS4CBE37.local\renders\runs\a7_stage2_20261119\<arm>\` — all 7 arms, hash MATCH on each upscaled mp4, no `_raw` files. Also copied `_render_order.json`, `_run_queue.out.log`, `_render_queue.log`, `status.log`.

## Max videoReview vs baseline `tq1_oc_ref_2pass` (6.0/10, 235.3 s)

Recorded 2026-11-19 evening CT. Scores are Max `videoReview` only. `PLAN.md` still requires Derrick's eye pick before any production-template promotion or S2 allowlist change.

| Arm | Setting | JOB s | Score | Verdict | Notes |
|---|---|---:|---|---|---|
| `tq2_vsa_0.2` | `m_vsa.start_percent=0.2` | 246.9 | **6.5/10** | **APPROVED WINNER** | Steadier face identity, smoother thrusting, tighter lip-sync 0:02–0:05, less jeans warping 0:04–0:08; slight finger blending 0:06–0:08. |
| `tq3_res_multistep` | `res_multistep` | 225.9 | **6.0/10** | **TIED** | Better face and bounce 0:05–0:09, offset by unsupported floating leg 0:03–0:09. |
| `tq3_lcm_simple` | `lcm` | 223.3 | **6.0/10** | **TIED** | Faster thrusting 0:04–0:09, offset by glossier skin, early mouth warp 0:00–0:02, leg/boot jitter 0:04–0:09. |
| `tq5_headerfree` | plain prompt via `beta7_convert.py --mode plain` | 231.9 | **4.0/10** | **WORSE** | Severe facial morphing/crossed eyes 0:02–0:05, arm-into-leg deformation 0:01–0:08, worse lip-sync, gray blurry artifact 0:01–0:02. |

Header-free lost to the 4-header control. That keeps U56 Decision #1 (4-header Beta 7 layout) unless Derrick overrules it.

## Mystic audio arm (separate run; not promoted)

Clip `arm5_mystic_audio.mp4` from `C:\AI\community\runs\h3max_lora_test_20261119\arm5_mystic_audio\`. Settings: `lcm` sampler, `beta` scheduler (t2868u / HF discussion #98). JOB **295.0 s**. 243 frames, 768x1344 raw with audio, RTX 2x to 1536x2688. Upscaled sha256 `6A6108D0EED03B5DA5D2CC37165042C49728201C27B97058924C0ACC5931A100`. Render and NAS details are in `ARM5-MYSTIC-KJNODES-RESULT.md`. NAS: `\\NAS4CBE37.local\renders\runs\h3max_lora_test_20261119\arm5_mystic_audio\`, hash MATCH, no `_raw` file.

Max `videoReview`: **4.5/10 (REJECTED)**. Clear voice audio, but worse lip-sync 0:04–0:09, vanishing skirt and hand at 0:01, severe anatomical merging 0:01–0:10, deformed tongue 0:02–0:10. Do not promote this arm into a production template.

## A7 promotion / A8 lockdown (not done)

Nothing in this pass promoted a template, edited an AlienPc production or candidate template, changed the S2 allowlist, or flipped Manager security. X3 was not touched.

Per `records/uplan/PLAN.md`:

- **A7** is "Video template A/B, fixed seed, Derrick picks by eye: TQ1 -> TQ4 -> TQ2/TQ3 -> TQ5, then M5 realism; plus a Mystic LoRA audio arm." The planned output is production templates. Verify for TQ1 is "Derrick eye pick before S2 promotion." TQ2/TQ3/TQ5 each say "Derrick eye pick recorded." TQ4 smoke still needs Derrick's eye pick; promotion of those Beta 7 candidates also needs the X3 Forge `pick_template()` routing fix. M5 realism was dropped (t2885u) and stays disabled. The Mystic audio arm is rejected above.
- Max's recorded pick for the stage-2 graph change, pending Derrick's eye pick: promote `m_vsa.start_percent=0.2` on the `tq1_oc_ref_2pass` graph; leave pass-1 sampler at `euler` (the `res_multistep` and `lcm` arms tied the 6.0/10 baseline); keep the 4-header prompt (header-free is worse). Do not apply that promotion until Derrick confirms.
- **A8** waits on A5 and A7: "Lock down: S2 allowlist hook (lists A5/A7 winners), then S1 Manager `strong` (after the last node install)." A5 still tests were not run (each still still needs Derrick's yes; see `A5-RESULT.md`). S1 Manager is still `security_level = normal` (audit A15) and the S1 row needs Derrick's yes; it was not flipped.

M5 realism was **not** started: that LoRA was dropped (t2885u) and archived earlier today; config stays disabled.
