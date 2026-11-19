# brief8 terrace settings test v3 - arm diff (each arm vs the B2 baseline request, the changed key only)

Baseline: `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json`, 26 nodes, sha256 `8d1d1a41e9915f2a3ef3f1350b65a4bf563f9607af7e3ed9538e4c9abae4695e`.
Built by `runs/terrace_settings_v3_20261030/_build_arms.py`; audited by `notes/terrace_v3_arms_audit.py`.
7 arms x 7 clips = 49 graphs; 42 need a render, 7 reuse v2 clips (verified by ffprobe below).

## the axis shared by every arm (identical on all 49, so the arm comparison stays one-variable)

| widget | baseline | every v3 graph |
|---|---|---|
| `c0.length` | 243 | **124** frames (the same 5 s screen as the v2 queue, 24 fps) |
| `img.image` | `community/TERRACE2_768x1344.png` | the scene frame: terrace, `imageA_768x1344_crop.png`, `imageB_768x1344_crop.png` |
| `c0.prompt` | the B2 v1 text | the scene prompt: B2v2 `e202e512…`, promptA `97ed1361…`, promptB `83efcf50…` |
| `noise.noise_seed` | 51083002 | the shared seed for that clip |
| `save.filename_prefix` | the old run path | `community/terrace_settings_v3_20261030/<tag>/<tag>` |

The only LoadImage node is `img`, and it feeds `c0.ref_images.ref_image_1` and both `MiniMaxH3AddGuide` nodes, so one widget carries the start frame. Verified link-for-link identical to the baseline in all 49 graphs: no wiring drift is possible. Everything else - steps 8, euler, simple, beta/3 pass 2, shift 12/3, VSA keep_percent 10, comfy kitchen attention, scale 2.0, align 32, 384x672 pass 1 -> 768x1344, ref_image_size max, fps 24 - is asserted unchanged in every arm by name.

## each arm: the one variable

| arm | changed widget | baseline -> new | clips | to render | reuse |
|---|---|---|---|---|---|
| a0 | B2 control (no setting change) | prompt text (see the note above) | 7 | 4 | 3 |
| s1a | sampler er_sde, scheduler stays simple | ksel.sampler_name → `er_sde` | 7 | 7 | 0 |
| s1b | scheduler sgm_uniform, sampler stays euler, pass 2 stays beta | s0_sched.scheduler → `sgm_uniform` | 7 | 7 | 0 |
| s2 | unet activation_learned_HQ | unet.unet_name → `10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` | 7 | 6 | 1 |
| s3 | latent upscaler fp16 | lsu3.model_name → `minimax_h3_latent_upscaler_3d_fp16.safetensors` | 7 | 6 | 1 |
| s6 | pass-1 steps 6 | s0_sched.steps → `6` | 7 | 6 | 1 |
| s8 | prompt only: the line file bytes (incl. its own trailing LF) + '\n' + the scene prompt = the v2 join (Max's correction 2026-10-30) | prompt text (see the note above) | 7 | 6 | 1 |

`a0` and `s8` change no widget: they are the control and the prompt-only arm. `s1a`/`s1b` split the old v2 `s1` arm, which moved two settings at once and is therefore not reusable.

## the 7 reused clips (verified, no render)

| v3 slot | v2 clip | sha256 | ffprobe |
|---|---|---|---|
| a0_terr_s51083002 | `runs/terrace_retest_v2_20261030/b2_s51083002` | `4a4874cf6189e572…` | 768x1344, 124 f, audio yes |
| a0_terr_s51083012 | `runs/terrace_retest_v2_20261030/b2_s51083012` | `301d1812e69b166e…` | 768x1344, 124 f, audio yes |
| a0_terr_s51083013 | `runs/terrace_retest_v2_20261030/b2_s51083013` | `49dcfece3f7b1e5b…` | 768x1344, 124 f, audio yes |
| s2_terr_s51083002 | `runs/terrace_retest_v2_20261030/s2_s51083002` | `3fc9b0be93934cc6…` | 768x1344, 124 f, audio yes |
| s3_terr_s51083002 | `runs/terrace_retest_v2_20261030/s3_s51083002` | `19e9d213aead2fe6…` | 768x1344, 124 f, audio yes |
| s6_terr_s51083002 | `runs/terrace_retest_v2_20261030/s6_s51083002` | `8e4240d8db71c31b…` | 768x1344, 124 f, audio yes |
| s8_terr_s51083002 | `runs/terrace_retest_v2_20261030/s8_s51083002` | `edffa80e9f4a351b…` | 768x1344, 124 f, audio yes |

## prompts as embedded (the graph string, hashed)

| prompt | chars | sha256 | guard_ok |
|---|---|---|---|
| s8 | 13312 | `12e46703e6ca8268e72be760d8bb10e340eed96b15f8dc353557829bbc0c0217` | PASS |
| s8 | 14160 | `46195643c6c613165a3855ae325862ac6c0088b414a2004630d18029d29cc894` | PASS |
| s8 | 12634 | `5f335a68ee249ab7087baf24bd86ead0d4097234d8e6b91ebb54621bd26649d5` | PASS |
| a0、s1a、s1b、s2、s3、s6 | 12975 | `83efcf50adea32d778f5b3a181192c0cd9098f322eff4ea87c46bc3fc128e8fe` | PASS |
| a0、s1a、s1b、s2、s3、s6 | 12297 | `97ed1361923b62a0dad9ae4c53ab48e80a5c0eee3805be90fa199f83f9e68e51` | PASS |
| a0、s1a、s1b、s2、s3、s6 | 13823 | `e202e512249f2f1cf823d0bcd56702522d9ee5ac603ab5f07079309cddaae0b5` | PASS |

Every prompt embedded in a graph is byte-identical to the file it came from: the terrace prompt hashes to `e202e512…`, promptA to `97ed1361…`, promptB to `83efcf50…` - the same hashes brief8 names, so what is submitted is what Max staged. The `s8` prompt is the line file's own bytes (the 335-char line, sha256 of the text `dae75674…`, plus its own trailing LF) + one more LF + the scene prompt, per Max's correction on 2026-10-30 - the same join the v1/v2 queue used. The built S8 prompts hash to the three values Max supplied (`46195643c6c6…` terrace, `5f335a68ee24…` imgA, `12e46703e6ca…` imgB), and the audit asserts those values: a mismatch is an audit failure, not a note.

## is each reused clip really the same instrument? (the check that decides the reuse)

The plan's baseline is the v2 B2 graph, so every reused slot's v3 graph is compared with the v2 graph that made its clip. The only allowed difference is the output prefix.

| v3 slot | v2 graph | widget delta | links | frames | seed | prompt chars (bytes) |
|---|---|---|---|---|---|---|
| a0_terr_s51083002 | `b2_s51083002` | `save.filename_prefix` | identical | 124 = 124 | 51083002 | 13823 → 13823 (+0) | same instrument |
| a0_terr_s51083012 | `b2_s51083012` | `save.filename_prefix` | identical | 124 = 124 | 51083012 | 13823 → 13823 (+0) | same instrument |
| a0_terr_s51083013 | `b2_s51083013` | `save.filename_prefix` | identical | 124 = 124 | 51083013 | 13823 → 13823 (+0) | same instrument |
| s2_terr_s51083002 | `s2_s51083002` | `save.filename_prefix` | identical | 124 = 124 | 51083002 | 13823 → 13823 (+0) | same instrument |
| s3_terr_s51083002 | `s3_s51083002` | `save.filename_prefix` | identical | 124 = 124 | 51083002 | 13823 → 13823 (+0) | same instrument |
| s6_terr_s51083002 | `s6_s51083002` | `save.filename_prefix` | identical | 124 = 124 | 51083002 | 13823 → 13823 (+0) | same instrument |
| s8_terr_s51083002 | `s8_s51083002` | `save.filename_prefix` | identical | 124 = 124 | 51083002 | 14160 → 14160 (+0) | same instrument |

All seven reused slots now differ from the v2 graphs that made their clips by the output prefix and nothing else - `a0`, `s2`, `s3`, `s6` and (after Max's 2026-10-30 correction of the S8 join) `s8` too. Every reused clip is therefore the same instrument as the graph queued for it, which is the evidence the plan's reuse needs. The prompts are byte-identical to the v2 prompts (`+0 B` in the table), which is what the corrected join is for.
