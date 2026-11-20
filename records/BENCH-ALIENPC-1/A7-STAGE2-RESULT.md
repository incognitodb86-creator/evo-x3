# A7 stage 2 — TQ2 / TQ3 / TQ5 on tq1_oc_ref_2pass — 2026-11-19

All times are America/Chicago (CT). Doer: Max Architect executor. Derrick t2948u (6:48 PM CT): "Go... Don't wait on my go, complete the damn plan."

TQ1 winner (Max video review): `tq1_oc_ref_2pass` 6/10, ahead of `tq1_oc_guide_2pass` 5/10 and `tq1_oc_ref_1pass` 4/10. Recorded in `A7-QUEUED.md`. Base request sha256 `718479ecaa544c46a73f8027b987c2d627044cd1d26864f9ce92f674670508b0`. Same still, prompt sha `6adb8150…`, seed **51083601**. Winner defaults: `m_vsa.start_percent=0.0`, `ksel.sampler_name=euler`, `s0_sched=simple` 8 steps, pass-2 `p2sched=beta` 3 steps denoise 0.4, 4-header prompt. Templates were not edited.

Run dir: `C:\AI\community\runs\a7_stage2_20261119\`. Lease `Max | A7 stage-2 TQ2/TQ3/TQ5 | 2026-11-19 18:51:17 CT`, cleared 19:13:35 CT. `gpu-render.lock` acquired 18:51:57 (pid 26968), released 19:09:27. BATCH rc=0, done=4/4. RTX 2x ULTRA post-pass on. No LoRA names or prompt text in this file.

Queued arms each changed **only the named field** from a copy of the winner request:

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

Winner control raw was 7,068,488 B; upscale 7.1 s, 31,132,812 B. Time vs control: VSA 0.2 was +11.6 s; `res_multistep` −9.4 s; `lcm` −12.0 s; header-free −3.4 s. Eye pick of quality is Derrick's (no bot KEEP). `er_sde` was not used.

NAS: `\\NAS4CBE37.local\renders\runs\a7_stage2_20261119\<arm>\` — all 7 arms, hash MATCH on each upscaled mp4, no `_raw` files. Also copied `_render_order.json`, `_run_queue.out.log`, `_render_queue.log`, `status.log`.

M5 realism was **not** started: that LoRA was dropped (t2885u) and archived earlier today; config stays disabled.
