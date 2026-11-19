# brief8 Step A READY — terrace settings test v3: 49 arm graphs built, checked, no render

Built 2026-10-30 08:33–08:52 CT by Forge (the brief's file is stamped 08:33:21; the actions.log DONE line is 08:51:33). Brief `briefs/2026-10-30-0840-forge-brief8-terrace-settings-test.md`.
Plan `plans/2026-10-30-0700-terrace-proper-settings-test-plan.md`, sha256 `5d5fa1ac8419ded2babd5aa4d397935cdcc68290275cd6d545f7bc9f2ca3653b`
— verified equal to the copy in `C:\Users\derek\_max2_s8chk\`, so I ran the plan the brief names.
**PAUSED here: no GPU, no queue, no `gpu-render.lock`, no model load, no render, no scoring, nothing deleted.**

**Update 08:55–08:59 CT — Max answered this note (§8 records his answers).** Item 1 changed the build: S8 is now the
line **file's own bytes including its trailing LF**, then one more LF, then the prompt — the v2 double-LF join. All 21
S8 graphs and prompt files were rebuilt, re-audited, and both scripts now **assert Max's three expected sha256s**
(§4). Nothing else in the 49 changed; the render order is unchanged (tags unchanged).

## Verdicts (every script re-runnable, every output on disk)

| step | result |
|---|---|
| preflight `runs/terrace_settings_v3_20261030/_preflight_check.py` | **PASS** — inputs hash to the brief's prefixes; PNGs really 768×1344 (IHDR); B2 baseline intact; all 20 arm widget paths present; S2/S3 model files on disk; prompts 6/6 sections, within the plan's ±15 %, guard PASS |
| build `_build_arms.py` | **PASS** — 49 request dirs (7 arms × 7 clips), 42 render targets, 7 reuse; zero undeclared widget changes; zero link changes |
| audit `notes/terrace_v3_arms_audit.py` (independent, reads the built files) | **49 PASS / 0 PROBLEM**; `guard_ok` **PASS 49/49**; reuse clips ffprobe 768×1344 / 124 f / audio |
| one-page diff table | `notes/2026-10-30-brief8-arms-diff.md` |
| full inventory (196 files, path + sha256) | `notes/2026-10-30-brief8-arms-inventory.md` |
| contact sheet of the start frames | `notes/2026-10-30-brief8-start-frames.png` (1170×828; PIL geometry only, no vision model, no caption) |
| Step B render order, drawn now | `runs/terrace_settings_v3_20261030/_render_order.json` — interleave check **PASS** |
| drift instrument | `notes/terrace_v3_drift_check.py` → `notes/2026-10-30-brief8-environment.txt`; a real gap found, §7 |
| **S8 rebuild after Max's answer** | **BUILD PASS + AUDIT PASS 49/49** — the three S8 prompts hash to Max's expected `46195643c6c6… / 5f335a68ee24… / 12e46703e6ca…` (asserted as a gate in both scripts), and `s8_terr_s51083002` is byte-identical to the v2 graph that made the reused clip except `save.filename_prefix` |

## 1. Inputs — I copied them, I edited none

| file | bytes | sha256 |
|---|---|---|
| `C:\Users\derek\_max2_brief8\imageA_768x1344_crop.png` | 1,363,348 | `4d07281de511581a36736c7d1fd9a3835e96cd502555046b211a533bd4fd95d0` |
| `C:\Users\derek\_max2_brief8\imageB_768x1344_crop.png` | 1,444,384 | `4c9ae12f9f082d5cb2cb1bcd3306bcf88faee7fac783a5b72093db99ef5bcc0d` |
| `C:\Users\derek\_max2_s8chk\promptA.txt` | 12,297 | `97ed1361923b62a0dad9ae4c53ab48e80a5c0eee3805be90fa199f83f9e68e51` |
| `C:\Users\derek\_max2_s8chk\promptB.txt` | 12,975 | `83efcf50adea32d778f5b3a181192c0cd9098f322eff4ea87c46bc3fc128e8fe` |
| copies in `ComfyUI\input\community\` (names preserved, no rename/crop/pad) | same | same — `COPY-OK sha match` for all five copies |
| my `_src\` copies (`promptA.txt`, `promptB.txt`, `s8_line_pic1_scene_identity.txt`) | 12,297 / 12,975 / 336 | as above; line file `cec841d0175654699b20f41b4e47dc049eabf2f0b8087de496009626488a334c` (file bytes; the **335-char text** hashes `dae7567438227802b08d6276faece019759c43958199f97cb2482c5daf8e2908` = the verified v1/v2 line) |
| cond frame `ComfyUI\input\community\TERRACE2_768x1344.png` (unchanged) | 1,352,963 | `b891c85fdf057b5ed915d8fea369f4d9139fabd644404d7116745af80f1c3777` |

Objective facts about Max's prompts, measured not judged: all six sections present in A and B; word counts
2,116 (−10.2 %) and 2,310 (−2.0 %) against the Terrace line's 2,357 — inside the plan's 15 % band; `comm.guard_ok`
PASS on all three. Each prompt is embedded **byte-for-byte**: `c0.prompt` in every imgA graph hashes to
`97ed1361…`, every imgB graph to `83efcf50…`, every terrace graph to `e202e512…` — so what is submitted is what
Max staged. Plan L41's *content* criteria (two adults fully in frame, faces/hands visible, clean first frame,
≥3 scene differences from Terrace) are gate 1 = Max's: I verified the measurable part only (exact 768×1344,
ratio 4:7, no stretch, PNG integrity, hashes).

## 2. What was built

`runs/terrace_settings_v3_20261030/` — 49 request dirs, named `<arm>_<scene>_s<seed>`:
`a0|s1a|s1b|s2|s3|s6|s8` × `terr`(seeds 51083002/51083012/51083013) + `imgA`,`imgB`(51083002/51083012).
Each dir: `request.api.json`, `prompt_full.txt` (byte-identical to `c0.prompt`), `graph_diff.txt`, `build_meta.json`,
`build.log`. Root: `_preflight_check.py`, `_build_arms.py`, `_arms_table.json` (the machine-readable matrix),
`_render_order.json`, `_src/`. Verified count: 49 `request.api.json`, 50 dirs (49 + `_src`). The builder stays at the
root — no 49 copies of it (recorded deviation from the v1/v2 habit).

## 3. The arm axis — one variable per arm (full one-pager: `notes/2026-10-30-brief8-arms-diff.md`)

| arm | the one variable | clips | render | reuse |
|---|---|---|---|---|
| a0 | none (B2 control) | 7 | 4 | 3 |
| s1a | `ksel.sampler_name = er_sde` (scheduler stays `simple`) | 7 | 7 | 0 |
| s1b | `s0_sched.scheduler = sgm_uniform` (sampler stays `euler`; pass 2 stays `beta`) | 7 | 7 | 0 |
| s2 | `unet.unet_name = 10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors` | 7 | 6 | 1 |
| s3 | `lsu3.model_name = minimax_h3_latent_upscaler_3d_fp16.safetensors` | 7 | 6 | 1 |
| s6 | `s0_sched.steps = 6` | 7 | 6 | 1 |
| s8 | prompt text only: `#74 line + "\n" + prompt` | 7 | 6 | 1 |

Shared axis, identical on all 49 (so the arm comparison stays one-variable): `c0.length` 243→**124** frames (the same
5 s screen as the v2 queue, 24 fps), `img.image` → the scene frame, `c0.prompt` → the scene prompt,
`noise.noise_seed` → the shared seed, `save.filename_prefix` → `community/terrace_settings_v3_20261030/<tag>/<tag>`.
The only `LoadImage` node in this graph is `img`, and it feeds `c0.ref_images.ref_image_1` **and** both
`MiniMaxH3AddGuide` nodes — verified in all 49, links identical to the baseline, node count 26.
`STOCK` settings asserted unchanged **by name in every arm**: steps 8, euler, `simple`, pass 2 `beta`/3/0.4,
shift 12/3, VSA `keep_percent 10`, comfy kitchen attention, `mode.scale 2.0`, `align 32`, denoise 1.0,
pass-1 384×672 → output 768×1344, `ref_image_size max`, fps 24. Declared no-op keys are counted, not hidden:
`img.image` on the 21 terrace graphs and `noise.noise_seed` on the 21 seed-51083002 graphs equal the baseline value.

On the plan's L11 (baseline = the v2 B2 graph, sha `124fb133…`): I built from the Oct-28 graph of record
(`8d1d1a41…`) and then **proved** what the plan wants — §5 shows each reused slot's graph is byte-identical to the v2
graph that made its clip. Same instrument, demonstrated rather than asserted.

## 4. Prompts as embedded (the S8 axis in hashes)

| set | chars | sha256 |
|---|---|---|
| terrace B2v2 (a0, s1a, s1b, s2, s3, s6) | 13,823 | `e202e512249f2f1cf823d0bcd56702522d9ee5ac603ab5f07079309cddaae0b5` |
| promptA (same arms, imgA) | 12,297 | `97ed1361923b62a0dad9ae4c53ab48e80a5c0eee3805be90fa199f83f9e68e51` |
| promptB (same arms, imgB) | 12,975 | `83efcf50adea32d778f5b3a181192c0cd9098f322eff4ea87c46bc3fc128e8fe` |
| s8 terrace | 14,160 | `46195643c6c613165a3855ae325862ac6c0088b414a2004630d18029d29cc894` |
| s8 imgA | 12,634 | `5f335a68ee249ab7087baf24bd86ead0d4097234d8e6b91ebb54621bd26649d5` |
| s8 imgB | 13,312 | `12e46703e6ca8268e72be760d8bb10e340eed96b15f8dc353557829bbc0c0217` |

**Resolved by Max on 2026-10-30 (his words: his brief wording was wrong).** The S8 prompt is the line file's own
bytes — the 335-char text (sha256 of the text `dae75674…`) **plus its own trailing LF** — then **one more LF**, then
the scene prompt: the v2 join. Builder and audit now treat Max's three values as a gate: a built S8 prompt that does
not hash to `46195643c6c6…` / `5f335a68ee24…` / `12e46703e6ca…` fails, and the audit re-derives the string from
the file, not from my builder. The rebuilt lengths (14,160 / 12,634 / 13,312 = prompt + 337) match the v2 S8 prompt
length exactly, and `s8_terr_s51083002` is now `+0 B` against the v2 graph (§5), so the reuse is byte-exact. The
S8 graph shas moved accordingly, e.g. `s8_terr_s51083002/request.api.json` → `31d1bbd0b829ef9f…`,
`s8_imgA_s51083012` → `d474ae2e4fb5f457…`, `s8_imgB_s51083002` → `4c083bcfa7a70aa7…`; `_arms_table.json` →
`cdefdad7ae6da4b5…`; the diff/inventory records regenerated (`de397058ddb6edc5…` / `b96444d7fb933b9c…`).

## 5. The 7 reused clips: verified, and the graphs are the same instrument

| v3 slot | v2 graph it matches | widget delta | links | clip ffprobe |
|---|---|---|---|---|
| a0_terr_s51083002/12/13 | `terrace_retest_v2_20261030/b2_s51083002|12|13` | `save.filename_prefix` only | identical | 768×1344, 124 f, audio yes |
| s2_terr_s51083002 | `…/s2_s51083002` | `save.filename_prefix` only | identical | idem |
| s3_terr_s51083002 | `…/s3_s51083002` | `save.filename_prefix` only | identical | idem |
| s6_terr_s51083002 | `…/s6_s51083002` | `save.filename_prefix` only | identical | idem |
| s8_terr_s51083002 | `…/s8_s51083002` | `save.filename_prefix` only (after the §4 rebuild) | identical | idem |

Clip sha256s are in `notes/2026-10-30-brief8-arms-diff.md`. All seven slots are byte-identical to the v2 graphs that
made the reused clips apart from the output prefix, so the reuse is the same instrument in every case. The v2 `s1`
arm is not reused (it moved two settings at once) — `s1a`/`s1b` are the plan's split, and all 14 of their clips
render.

## 6. Step B order, drawn now (so the gate can read it before a frame is rendered)

`notes/terrace_v3_render_order.py` → `_render_order.json`: `random.Random(20261030)`, cells = (scene, seed)
(shuffled, jobs inside shuffled), then a greedy pick that never repeats the previous cell **or** the previous arm.
Result: 42 jobs = 2 pilots + 40 main; per arm `a0 4, s1a 7, s1b 7, s2 6, s3 6, s6 6, s8 6`; minimum gap between two
jobs of the same arm: `a0 1, s1a 2, s1b 3, s2 2, s3 2, s6 4, s8 2`; consecutive-job check **PASS**. Estimated GPU
time from the **measured** v2 walls (110.7–144.7 s per 124 f clip), one job at a time: **4,649–6,077 s
(77.5–101.3 min)**.
The plan's gates sit inside this order: pos 1–2 are the pilots (plan step 2, which asks for a pilot GO **separate**
from the GO for the other 40), the drift check runs before pos 3, and the plan asks for **Derrick's GO for the other
40**. **Answered by Max: Derek's 8:31 AM CT GO covers both pilots and all 42 new renders; no separate plan GOs.** So
Step B runs pos 1 → pos 42 with no further GO, starting with the drift check (§7, option (a): record, no re-render).

## 7. Drift check: I ran the instrument, and it found a gap

`notes/terrace_v3_drift_check.py` → `notes/2026-10-30-brief8-environment.txt` (the first such record on this lane):
ComfyUI HEAD `6b747c0428c343e1417219641db93a4fb7cb69ae`, HEAD date **2026-09-29** → the core code predates the v2
queue (Oct 30 05:35–06:35 CT), so tracked core code has not moved; 64 dirty entries (the unprovable part, stated);
40 `custom_nodes` dirs recorded by git head + manifest version + dir mtime (newest 2026-10-29, i.e. before the v2
window); GPU `RTX 5070 Ti`, driver **616.92**, 16,303 MiB; the model set referenced by the 49 v3 graphs is
**identical** to the set in the v2 graphs (True), sizes/mtimes recorded, files under 2 GB hashed (audio VAE
`8e505d95…`, upscalers `4f57821f…` / `043e5a48…`), the four large ones not hashed by default (`--all-models` does
them, minutes each); `GET /system_stats` through the llama-swap proxy **timed out** (recorded, not hidden).

**The plan's step 3 says "compare with v2", and it cannot be run as written: the v1/v2 queues wrote no environment
record** (searched `notes/` for driver/commit/custom-node/model-sha records — none). So the plan's own fallback
applies. **Answered by Max: option (a) — the 7 reused clips are accepted**, and my DONE note must state that v2
never logged its environment; it will, in those words, with this section as the evidence. My recommendation was (a)
on the strength of the byte-identical graphs (§5) plus core code predating v2 and identical model references; option
(b), the plan's +7 re-renders (~13–17 min), and (c), one extra A0 control, are on the record and not started.

## 8. The CHECKED items, with Max's 2026-10-30 answers

1. **S8 join — resolved, and the build changed.** Max: his brief wording was wrong; use the line file bytes including
   its own trailing LF, then one more LF, then the prompt. Rebuilt, re-audited, his three expected sha256s are now a
   gate in both scripts (§4).
2. **GO scope — answered.** Derek's 8:31 AM CT GO covers both pilots and all 42 new renders; no separate plan GOs.
3. **Drift — answered: option (a)**, accept the 7 reused clips; the DONE note will record that v2 never logged its
   environment (§7).
4. **Flicker masks — out of brief8.** Not built, not run; I do not draw the masks and I do not score.
5. **Scoring and the blind pack — out of brief8.** Not started; Forge scores nothing in this brief.
6. **Plan L41 image content acceptance — unchanged:** gate 1 is Max's. §1 states exactly what I verified objectively
   (exact 768×1344, ratio 4:7, no stretch, PNG integrity, hashes) and nothing more.

Text for the plan's "their paths go here" line (L11-12 area — the plan is Max's file, I do not edit it):
`Image A: C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\imageA_768x1344_crop.png (sha256 4d07281de511581a36736c7d1fd9a3835e96cd502555046b211a533bd4fd95d0);
Image B: …\imageB_768x1344_crop.png (sha256 4c9ae12f9f082d5cb2cb1bcd3306bcf88faee7fac783a5b72093db99ef5bcc0d);
prompts: C:\Users\derek\_max2_s8chk\promptA.txt (97ed1361923b62a0dad9ae4c53ab48e80a5c0eee3805be90fa199f83f9e68e51), promptB.txt (83efcf50adea32d778f5b3a181192c0cd9098f322eff4ea87c46bc3fc128e8fe);
graphs: C:\AI\community\runs\terrace_settings_v3_20261030\<arm>_<scene>_s<seed>\request.api.json.`

## 9. State and files

GPU idle (`gpu_guard` rc 0), no lock file, no render, no queue, nothing killed (llama-swap, strata, pi-mobile hub
untouched), no config and no default-graph change, B2 default unchanged, nothing deleted, no other plan touched,
`C:\Users\derek\_max2_brief8\` and `_max2_s8chk\` untouched. Scripts: `_preflight_check.py`, `_build_arms.py`,
`notes/terrace_v3_arms_audit.py`, `notes/terrace_v3_render_order.py`, `notes/terrace_v3_drift_check.py`,
`notes/terrace_v3_start_frames_contact_sheet.py`. Records: `notes/2026-10-30-brief8-arms-diff.md`,
`notes/2026-10-30-brief8-arms-inventory.md`, `notes/2026-10-30-brief8-environment.txt`,
`notes/2026-10-30-brief8-start-frames.png`.

**PAUSED. Step B starts when `notes/2026-10-30-brief8-arms-CHECKED.md` exists, and follows §6's order verbatim:**
drift check recorded first (option (a), no re-render), then pos 1–42, one job at a time under `gpu-render.lock`,
the pre-render pytest + `guard_ok` gate on every submit, retry once on the same graph and seed, then the plan's
failure rule.
