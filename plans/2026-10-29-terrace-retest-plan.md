# Terrace community-settings retest — fair stock baseline + one change at a time — 1 page

Derrick's decisions this comes from: "can you confirm the exact stuff and audit it to confirm it was done correctly?" (Oct 29 4:38 PM CT) → verification found T4 was not stock → "ce-plan this out" (4:46 PM) → "5 seconds… less time" (4:58 PM) → "Ok let's keep the b2 setup and make it default" (6:59 AM Oct 29) → "plan only, no rendering" (8:22 PM, Max brief `briefs/2026-10-29-2025-forge-brief.md`).

Written by Forge 20:55 CT from Max's draft `briefs/2026-10-29-terrace-retest-plan.md`, **checked against the files on disk**. All numbers came from `notes/terrace_retest_plan_probe.py`/`probe2.py` → `notes/terrace_retest_plan_probe.txt`; the long write-up is `notes/2026-10-29-terrace-retest-plan-findings.md` (F1-F8). B2 = `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json`, 20,072 B, 26 nodes, sha256 `8d1d1a41…4695e` — byte-identical to the default `p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json`.

**Goal:** Find out fairly whether true stock LokkenJP simple_v2, or any single TenStrip/LokkenJP recommended setting, beats B2.

**Done when:** Derrick has blind-scored every clip (hidden filenames, `_raw` native files only) in one table — arm | mean score | flags | render seconds. Pass = mean ≥ 1.0 above B2 on the same seeds **and** wins ≥ 2 of 3 seeds, seed by seed. B2 stays the default until that table says otherwise.

**Writer inputs:** none. Every arm renders B2's prompt bytes unchanged — 13,128 chars, sha256 `fcad1c379bf097f3…`, hash-checked in the builder — except S8, which prepends one preservation line (F5). No agent vision: Forge does not look at the still, frames or clips; judging is Derrick's; the VLM judge is a separate instrument and informational.

**Pictures:** Picture 1 = `ComfyUI\input\community\TERRACE2_768x1344.png` (1,352,963 B, sha256 `b891c85f…`; real pixels 768×1344 = **4:7, not 9:16**) — start image and open frame in every arm. Canvas in every arm: **768×1344 @ 24 fps** (F2/F3).

**Who builds:** Forge. Each graph = deep-copy of B2's api.json (of the stock file for T4c) with the changed-input set asserted to be exactly the intended paths, writing `graph_diff.txt` + `guard_check.py` like the T2b/T3 builders; renders only via `scripts/gpu_window.ps1`. Max briefs and checks. No new nodes, controls, or installs.

**Community baseline:** TenStrip 10Eros-Max README + discussions, and LokkenJP `H3_Turbo_2Pass_ErosMax_b7_simple_v2.json` — the on-disk copy `runs/terrace_dom_q5stockv2_20261028_s51083011/stock_simple_v2.json`, sha256 `a315ac74a24a14d4…` (the draft's prefix matches; it is T4's saved copy, not a live download). Adults-only guard (`comm.guard_ok`) before every render; one GPU job at a time on `C:/AI/locks/gpu-render.lock`.

**Arms** (dir/tag `terrace_retest_<arm>_20261029_s<seed>`; each arm touches only these paths, plus `noise.noise_seed` and `save.filename_prefix`):

| Arm | Base | The only changes (real node ids) |
|---|---|---|
| B2 | B2 | nothing — control arm |
| **T4c** | stock | ui 9 `LoadImage` mode 4→0 + image→TERRACE2 (this is what turns both Add Guides on); prompt→B2's bytes; `Seed (rgthree)` −1→fixed; Duration 15→**5.0**; `ResolutionSelector` → **9:16 (Portrait Widescreen) + 0.25 MP** (= pass-1 384×672, B2's own pass-1 canvas); upscaler `mode.megapixels` **1.0** kept → 768×1344; prefix; plus T4's raw-save nodes |
| S1 | B2 | `ksel.sampler_name` euler→**er_sde** + `s0_sched.scheduler` simple→**sgm_uniform** (TenStrip names the pair, so they move together) |
| S2 | B2 | `unet.unet_name` → **beta7_activation_learned_HQ** |
| S3 | B2 | `lsu3.model_name` → **minimax_h3_latent_upscaler_3d_fp16** (scale 2.0 kept) |
| S4 | B2 | `c0.ref_image_size` max→**match** |
| S5 | B2 | delete `ag0`/`ag1`; both `s?_guide.conditioning` ← `["c0",0]` (ref_image_size stays max) |
| S6 | B2 | `s0_sched.steps` 8→**6** (off-dial: the ckpt is an 8-step distill) |
| S7 | B2 | `ksel.sampler_name` → **res_multistep** |
| S8 | B2 | `c0.prompt` = the #63/#50 preservation line + one blank line + B2's bytes, built from a file, `startswith` asserted, result hashed |

**Stage 1 — fair baseline (6 clips):** B2 vs T4c on seeds 51083002 + **51083012** + **51083013** (verified unused). T4c is scored on its `_raw` (before RTX and grain) = native 768×1344, pixel-comparable to B2's raw.
**Stage 2 — one change (8 clips, seed 51083002):** S1–S8. Only an arm that strictly beats B2 on that seed gets the other two seeds; only an arm that passes gets one 243-frame confirmation render (Duration 10.0 for T4c) for late-clip drift/flicker.
**Length (Derrick 4:58 PM):** every arm screens at **124 frames = 5.17 s** — 121 is not reachable (F1).

**Cost (projected from measured renders, not measured):** B2 243 f = 240.1 s; stock full chain 243 f = 240.1 s; 12-step 2-pass = 300.1 s → 15.0 s per extra pass-1 step at 0.258 MP; ×124/243 → **~2 min per screening clip**: Stage 1 ≈ 13–16 min, Stage 2 ≈ 15–20 min, +4 min per winner's extra seeds, +5 min per confirmation. S1/S2/S4 move their own seconds (the node's tooltip: `max` "can be several times slower"); every arm's real seconds go in the table. Judge runs are separate GPU windows (~3 min per 36 clips + load/unload).

**Acceptance before GPU:** Max diffs each arm's `api.json` against B2 (T4c against `_ui2api/api_stock.json`) and confirms exactly the intended change set, same still/seed/prompt hash, 768×1344, `c0.length`/Duration == the `--frames` argument, guard on; that table goes to Derrick before GO. Before any clip is judged: `judge/prechecks.py` (CPU; DINOv2/CLIP consistency vs the start image, cut counts — the closest instrument on this box to the "zero identity drift" gauge Oct 28 said was missing) and `judge/vlm_judge.py` + `vlm_variants.py --variants Z`; **flags are informational**, never a score or a pass. Scoring pack: `review/terrace-retest-2026-10-29/` (the box's convention; `60_reviews/` from the template does not exist), clips renamed to random tokens in shuffled order, answer key outside the pack — needs a small CPU pack builder, written and dry-run before GO (the old review-cut builder survives only as `notes/ali27_review_loop_manifest.json`).

**Stop:** Stage 1 first. If T4c loses, run Stage 2 anyway — it tests single settings. Stop after Stage 2's seed follow-ups. If nothing passes, B2 stays and settings work is closed; next is the prompt-and-still arm. Any render error, objective-gate failure or diff mismatch stops that arm and is reported, not retried with changes (the harness may re-queue the same graph, `--max-redo` 2). No GPU until Max's diff table is approved.

**Not in this plan:** beta5 (not on disk — a download), the Eros-Max LoRA (#76), the text encoder alone, LCM at 6–8 steps, 15 s length. Each is a later one-change arm with its own yes.

## Corrections to the draft — what does not match the files (detail in F1-F8)

1. **121 f is impossible.** The stock chain derives frames from Duration: `max(5,round(a*24)) + (5 - (max(5,round(a*24)) % 17)) % 17` → 5.0 s = **124**, 10.0 = 243, 15 = **362**; every value is ≡5 mod 17. Screen at **124 f** in both arms (`c0.length = 124` / Duration 5.0), and keep `--frames` equal — `run_graph_job.py:176` fails on any mismatch.
2. **The selector does have 9:16.** The installed `comfy_extras/nodes_resolution.py` offers 8 options incl. **`9:16 (Portrait Widescreen)`**, 2:3, 3:4, 21:9; the draft's four-option list is the workflow's own stale MarkdownNote. No hand-tied width/height needed.
3. **768×1344 is 4:7, not 9:16, so the MP values must be paired:** 9:16 at 1.0 MP → **768×1376**; the draft's 0.98 → 768×1344 is real only for a 9:16 pass-1 size. Use **recipe A**: 9:16 + **0.25 MP** → pass-1 **384×672 = B2's pass 1**, then the stock upscaler value 1.0 → exactly **768×1344** (scale 2.016 vs B2's 2.0). Recipe B (stock 0.3 → 416×736, upscaler 0.98) hits the same canvas but adds a low-res-budget variable to the baseline arm.
4. **T4c is a system test, not a setting test.** Stock also differs in the UNet file, the CLIP file, the scheduler, model-chain order + `H3PowerLoraStack`/`ModelPreviewOverrideKJ`, **audio from pass 2** (B2 decodes pass 1), and RTX + grain + crf-18 inside the graph. T4c answers only "does the stock box as a whole beat B2"; only S1–S8 isolate a setting.
5. **The S8 line is #63/#50, not #74** (#74 = Add Guide + `ref_image_size: max`). B2's prompt already opens `<Picture 1> is the composition and identity anchor…`, so S8 adds a second, stronger claim about the same picture; Max's Oct 28 brief forbade pairing that line with the Add Guides (thread: **faces not blinking for seconds**) — that is exactly what S8 must be watched for.
6. **No downloads needed** — both beta7 UNets and both 3D upscalers are on disk; beta5 is absent (draft right). All arm values exist on this build; `ref_image_size` is also a speed dial. The judge and the Z zoom exist, Z has never run here for real, and its 5 checks are p15-tuned absolutes — `target_reached` is meaningless on this cell.

**Derrick's decisions before any GPU:** (1) GO for 124-frame screening + recipe A + 3 seeds (≈35–45 min GPU + judge windows), or a smaller cut (Stage 1 + S1/S4/S8); (2) confirm the 0–10 scale and the ≥+1.0 mean / ≥2-of-3 pass rule; (3) yes/no for the S8 prompt line; (4) nothing here changes the default — B2 stays the default graph and `PROMPT.md` 1e unless a passing arm is adopted later, in a separate step.
