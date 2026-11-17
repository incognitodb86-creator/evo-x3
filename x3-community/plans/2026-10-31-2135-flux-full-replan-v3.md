---
title: FLUX full plan v3 - verified state, community best, execution order
date: 2026-10-31 9:35 PM CT
author: Forge (pi, AlienPc) - drafted on Derek's words of 9:17 PM CT
status: PROPOSED to Derrick (his Q1-Q13 cards stay open; the plan is ACTIVE for the work his existing answers already authorise)
supersedes: 2026-10-30-flux-full-replan.md (v2) for build order, gates and arm wiring; v2's arm tables, decision log and KTD cards stay as the source of truth for scope
plan_of_record_for: Phases 1-2 scoring, Phase 3, Phase 4 (conditional), Phase 5, Deliverable set, Phase 6, Phase 7, Phase 8 (conditional)
canonical_copy: C:\AI\fleet-brain\40_projects\flux2-overnight\plans\2026-10-31-flux-full-replan-v3.md (Gitea derrick/fleet-brain, master)
---

# FLUX full plan v3 (2026-10-31)

Derrick, 2026-10-31 9:17 PM CT: **"Check gitea and the flux test plan double check it and update for
community best and then execute all phases of the plan."** This file is that double-check, the
community update, and the execution order. Nothing here cuts approved work: v2's answer "Nothing is
cut" still holds. Three gates stay his calls (the S2 calibration, Phase 6 downloads, the C8-P and
C8-S bars), and two phases stay conditional on measured triggers (Phase 4, Phase 8). Everything that
his existing answers already authorise goes into the loop now.

## 0. What v3 changes, and why (one line per change, gap ids from `60_reviews/fleet/2026-10-31-flux-replan-p3-7-gap-review.md`)

| # | Change | From |
|---|---|---|
| V3-1 | **Phase 1 is re-labelled and scored as a copy test.** Its 61 renders asked for no pose change, so they measured copying, not editing. Score it, record C8-R for the record, and do not use its counts as a Phase 1 pass. | GR-1, MF-3 |
| V3-2 | **Phase 2's 294 images are quarantined and scored before any re-run.** The winner is chosen from scores, not from a re-render. | GR-1, Scout input 4 |
| V3-3 | **Phase 3+ use new prompts and new poses/scenes, not Phase 1's inherited ones.** The current builder re-reads `p1_L_*` request files, so every later arm inherited Phase 1's prompt text; that is what produced the near-copies. | GR-2, Scout input 1 |
| V3-4 | **S2 is the reference arm** (Klein 9B-KV body pass + BFS head-swap pass 2), adopted by Derrick 1:16 AM CT Oct 31 (33/54 PASS, median 0.522, 0 COPY). Later phases carry S2 forward as the baseline, and single-variable arms are built *on top of S2*, not on top of a bare L run. | GR-3, Scout input 1 |
| V3-5 | **Every gate names its machine enforcer.** A phase build stops if the previous phase's score file is missing or under the bar; no bot decides. New: `scripts/queue/flux_phase_gate.py`. | GR-4, Scout input 3 |
| V3-6 | **Phase 3's unbuildable arms get their missing inputs built** (CROP graph + context size, ANGLE picks, head boxes, mask grow/feather px) and Phase 3 is run complete, not one-arm. | GR-5, GR-6 |
| V3-7 | **The Deliverable set is built on S2** with a manifest, not on "the best arm" left ambiguous. | GR-8 |
| V3-8 | **The prompt path is wired to the adopted S2 stills skill** (`alienpc-stills-pose-edit-prompting`) for every phase prompt, and the S2 README's four community deltas are put to a measured 8-cell test (V3-9). | GR-9, Scout input 1 |
| V3-9 | **Community update to S2 (new, this session):** four S2 settings sit below the values the maintainer documents today. Test them in one 8-cell matrix, keep the scored S2 as the control. Details §4. | research note `notes/2026-10-31-flux-community-best-check.md` |
| V3-10 | **Phase 6's download ask is corrected and small:** C13 331.4 MB + C15 165.7 MB + C16 79.7 MB = **0.58 GB**, not the 3.6 GB in v2 Q2. RMBG-2.0 (C14) stays out ("Do not implement", Oct 30 7:30 AM). | verified from `queue_storyboard.py --dry-run` |
| V3-11 | **Phase 8 candidate list updated:** FLUX 3 Image Klein (open 5.6B, released 2026-10-17, generation + multi-reference editing) is added next to Qwen-Image-Edit-2511 + BFS v5, with the honest note that FLUX.2 Klein LoRAs do not carry over to it. | research note rows 9-11 |
| V3-12 | **Scout's five input points are addressed** - §9 has the point-by-point coverage. | Scout input 1-5 |

## 1. Applies to every phase (unchanged from v2, restated because they bind the new items)

- Fictional adults 18+ from `approved_characters` only; never E10/`_dropped`/`_needs_derrick`/real-named. `guard_ok` runs on every job before submit; vision never decides identity, age or resemblance.
- Face-detector ban stays as v2's faces section: no InsightFace/ReActor/PuLID/InstantID/FaceID/AuraFace face_sim in any graph, MediaPipe allowed **only** for T2 head boxes, DWPose body+hands only (face keypoints off), SDPose face keypoints off if T4 is used. `run_queue.guard_graph` blocks banned classes; the static banned-class check runs on every imported graph before each phase go.
- Judging = six yes/no checks (Identity, Face, Hands, Contact, Wardrobe, OverallQuality) + `face_scores()` for ranking only. Scores are counts; **Derrick gives the 1-5 and the KEEP**. Blind sheets on every scored phase.
- One GPU job at a time: `gpu-render.lock`, `run_queue.py --detach`, a STOP file halts a batch. Renders are requested only through llama-swap `comfyui_auto`.
- C7 disk floor: start a phase only with >=12 GB free on C:, stop below 8 GB (logged). Checked: 238.8 GB free at 9:25 PM CT.
- C12 lease order: the FLUX work runs before the Strata/llama-swap update.
- C-MULTI: one position cue per prompt for multi-character groups. C3 = the community NSFW 9B on disk (`FLUX-KLEIN-9B-FP8-NSFW.safetensors`, sha256 `39e16031...aa5b3d3b` = the Jib Mix v1.0 Temptation build named in v2 line 25). **No base-model download is needed for any phase.**
- Sizes: 1.0 MP class, multiples of 16 (752x1360 / 1360x752 / 768x1344 as the phase table says). No video in any stills batch.
- Downloads are asked one at a time inside that phase's go message; no download is started on a phase go alone.

## 2. Verified state on the box (2026-10-31 9:2x PM CT, read-only checks)

| Phase | What exists | Proof |
|---|---|---|
| 1 | 61/61 rendered Oct 30 16:53, `BATCH closed rc=0`; 61 png in `runs/flux_p1_20261030` | `_render_queue.log`; file count 61 |
| 1 scores | **no `scores.csv` in the run dir.** Max's review area has a scored CSV (61 rows, 51 ok / 10 flag, mean face_sim 0.845, pose unchanged) and MF-3 says Phase 1 = copy test | `60_reviews/fleet/2026-10-31-max-flux-render-audit.md` |
| 2 | 294 png in `runs/2026-10-31_flux_replan_p2_0011` (portrait + landscape orders), batch log `done=233/233 rc=0` | file count 294; `_render_queue.log` |
| 2 scores | **none** | no CSV anywhere under `runs/` |
| 3 | Only `L05` builds (60 jobs). CROP, ANGLE, P-B1, B2 print as not built with named reasons. One job rendered Oct 31 09:10, then a STOP file; `done=1/10 rc=1` | `queue_flux_replan.py --dry-run --phase 3`; `runs/2026-10-31_flux_replan_p3_0012` |
| 3 prompt inheritance | the builder reads Phase 1's `p1_L_*` request files to build its prompts | `queue_flux_replan.py` lines 53-56 |
| 4 | not built; conditional on Phase 3 hand scores < 6/30 | v2 KTD7 |
| 5 | not built; pose manifest not picked (2 characters x 6 poses) | `queue_flux_replan.py` GAPS phase 5 |
| 6 | `queue_storyboard.py --dry-run` builds **68 ready jobs** (S0 16, S4 32, S5 12, MC 8, all `guard_ok` passed). S1/S2/S9 blocked on C13/C16/C15 LoRA files (577 MB total); S3/S6/S7/S8/S10/S11' not built (need a QuadView sheet, a best S5 panel, base-9B, C17+C18, chained panels, undefined RefGrid refs). No C8-S bar set | dry run 2026-10-31 21:2x CT |
| 7 | T1 needs the official Klein edit graph (not on disk); T2 MediaPipe allowed and needed for head boxes; T3 needs an xy sweep tool (no xy node installed); T4 conditional; T5 needs a graph probe | `custom_nodes/` list |
| 8 | not built; conditional on G-SWITCH-EDITS (Klein <=2/30 after >=3 rounds, challenger >=6/30 and beats L by >=6) | v2 Phase 8 row |
| Deliverable set | not built (4 poses x 2 characters, 24 jobs on S2) | v2 + GR-8 |
| Instruments | `scripts/make_render.py` has `face_scores()` on the ComfyUI venv InsightFace (CPU, scoring only); S2 templates `templates/flux_stills_s2_kv.api.json` + `flux_stills_s2_bfs.api.json` + `scripts/queue/s2_dryrun_check.py`; `queue_storyboard.py`; 61 tests pass (`pytest -q scripts/tests/`) | local runs |
| Models on disk | `FLUX-KLEIN-9B-FP8-NSFW.safetensors` (C3), `flux-2-klein-9b-kv-fp8.safetensors`, `bfs_head_v1_flux-klein_9b_step3750_rank64.safetensors`, `MS_real_and_Details_klein`, `NSFW_MASTER_FLUX`, `QuadView_klein9b_v1`, `TripleView_klein9b_v1` | `models/diffusion_models`, `models/loras` |
| Custom nodes | present: `comfyui-storyboard`, `comfyui_controlnet_aux` (DWPose). Not installed: xy sweep, Segment/Remove-background, story-teller | `custom_nodes/` |

## 3. Gates, with the machine enforcer (V3-5)

`scripts/queue/flux_phase_gate.py --phase N` reads the score CSV of phase N-1 in its run dir and
refuses (`GATE FAIL`, rc 2) if the file is absent, the row count is below the phase's job count, or
the phase bar is not met. It prints the bar, the counts, and the file it checked, into the run dir's
`_gate.txt`. The bar for each phase:

| Phase | Gate before building/running | Enforcer |
|---|---|---|
| 1 (close-out) | none; scored as a copy test, counts recorded | `flux_phase_gate.py --phase 1 --report-only` |
| 2 (score only) | Phase 1 `scores.csv` present | gate |
| 3 | Phase 2 `scores.csv` present **and** a named winner; prompt manifest present with >=1 new pose per cell | gate + `queue_flux_replan.py` manifest check |
| 4 | Phase 3 `scores.csv` present **and** hands < 6/30 (KTD7). If hands >= 6/30 the phase is **not run** and the trigger result is recorded | gate (reads the hand flag counts) |
| 5 | Phase 3 winner recorded, pose manifest complete, **C8-P bar set by Derrick** | gate + manifest check |
| Deliverables | Phase 5 done, S2 chosen (already adopted Oct 31 1:16 AM) | gate |
| 6 | Deliverable set done; **C8-S bar set by Derrick**; for S1/S2/S9 the C13/C16/C15 yes | gate + file-presence check (already in `queue_storyboard.py`) |
| 7 | Phase 6 scored; each probe's graph passes the banned-class check | gate + `guard_graph` |
| 8 | G-SWITCH-EDITS trigger met, and the model is on disk | gate + file-presence check |

## 4. S2 and the community deltas (V3-4, V3-9) - one 8-cell calibration, control included

S2 as adopted and scored (pass 1 KV body at 4 steps CFG 1, LoRA off; pass 2 BFS head at strength
0.5 on the community NSFW 9B, 4 steps lcm) is **not changed by this plan**. The maintainer's current
Klein card (accessed 2026-10-31 21:05 CT, `Alissonerdx/BFS-Best-Face-Swap/docs/flux-2-klein.md`)
documents four values we sit below; the S2 README already lists them as "Listed for Derrick,
unchanged". They are tested once, cheaply, with the scored S2 as the control:

| Axis | S2 today (control, 4 cells) | Community value (test, 4 cells) | Source |
|---|---|---|---|
| BFS LoRA strength | 0.5 | **1.0** | "Start around LoRA strength `1.0`; adjust after checking identity preservation" |
| Head-swap prompt | older wording, "high quality, sharp details, 4k" | current card wording, adds **"Keep the body, clothing, pose, framing, and background intact."** | same doc, Prompt section |
| Head reference (Picture 2) | full approved still | **head crop** of the approved still | "Image 2: reference face/head" |
| Pass-2 sampler/steps on the NSFW 9B | lcm, 4 steps | **Euler/simple, 10 steps** (author: "8-12 Steps of Euler/Simple seems to be good") | C3 author card (PARTIAL: CivArchive mirror of the Civitai card) |
| Input order | Picture 1 = pass-1 body, Picture 2 = head | unchanged - matches the card's "Do not reverse" | same doc |

Matrix: 4 control + 8 test cells (2 strengths x 2 prompts x 2 head inputs at Euler/10) = 12 jobs,
one character, one pose, two seeds per cell. Judgment: the six yes/no checks + `face_scores()`
ranking, then **Derrick's blind Y/N breaks ties**. Nothing is adopted from this matrix without his
KEEP; if no cell beats the control, S2 stays exactly as scored and the deltas are recorded as tested.

Also from the card (accepted, no test needed): keep the head-swap prompt free of scene-change text -
S2's two-pass split already does this. "You can add a short expression or pose instruction when it is
visible in the target image" is added to the prompt rules in the stills skill path.

## 5. Phases, as they are executed

The per-phase arm tables are v2's; this section only fixes wiring, order and what must be built.

**Phase 1 close-out (no renders).** Score the 61 images with the six checks + `face_scores()`, write
`scores.csv` in the run dir, record the C8-R count, and file the C8-R call as **"copy test - not
counted as a Phase 1 pass"** (the prompts asked no pose change; mean face_sim 0.845). Report to
Derrick with the counts.

**Phase 2 (score only, no re-render).** Score all 294 quarantined images (every arm: ORIG, E, CTRL,
E8, ES10, STR08, STR12, L-FULL, CROP-if-any), write `scores.csv`, name the winner by counts, build
blind sheets, and report. The winner is a recommendation; the KEEP is his.

**S2 calibration (new, 12 jobs).** Section 4. Gate: Phase 2 scored.

**Phase 3 (180 jobs, complete, on the v2 arm list).** Build the missing inputs first:
- `head_boxes.csv` for the Phase 1 stills via MediaPipe (T2, the only allowed face detector, boxes
  only) with a human check on 3 of them; mask grow 16 px, feather 12 px (the values the plan left
  unset - stated here, recorded, and put in the run dir so the numbers are reproducible).
- CROP graph: core ImageScaleBy + crop to a 512-576 px head context, BFS head swap at the reference
  strength, core ImageStitch back; documented as `templates/flux_crop_bfs_stitch.api.json`.
- ANGLE picks: angle-matched head refs per still from the approved folder; skip a cell if none.
- Then `queue_flux_replan.py --phase 3` with the **new prompt manifest** (V3-3): 2 characters x 3
  scenes x 3 poses, prompts written by the stills skill, two seeds. B1 head-mask composite runs on the
  Phase 2 winner's outputs (CPU), B2 only if B1 seams > 3.
Gate: Phase 2 scored + S2 calibration reported.

**Phase 4 (conditional).** Run only if Phase 3's hand counts are < 6/30: hand-crop pack, hand LoRA
(`MS_real_and_Details_klein` is on disk), SDPose flag for T4 if DWPose fails >= 3/12. If the trigger
is not met, record "Phase 4 trigger not met (hands x/30)" in `DONE` and move on.

**Phase 5 (pose quality, ~400 jobs).** Pick the manifest first (2 approved characters x 6 poses,
CC0 + Sexinfo sources, one position cue per C-MULTI), write `poses_manifest.csv`, and **ask for the
C8-P bar** (Q11) in the Phase 5 go message. Built on the reference arm + single-variable deltas per
v2's P0-P14 table. Run in two batches (P0-P7, then P8-P14) with a score CSV after each.

**Deliverable set (24 jobs).** S2, 4 poses x 2 characters, via `scripts/make_render.py` + the S2
batch path with a manifest, blind sheet, and QNAP delivery of what passes.

**Phase 6 (storyboard).** Run the 68 ready jobs as staged (S0 baseline, S4 restated-vs-omitted, S5
one-shot 2x2 grid, MC multi-character). Ask for the **C8-S bar** (Q12) and the **0.58 GB** of
Phase 6 LoRAs (C13 331.4 MB, C15 165.7 MB, C16 79.7 MB) in the Phase 6 go message; S1/S2/S9 build
only after the files land. S3/S6/S7/S8/S10/S11' stay not-built until their inputs exist, with the
reason printed by the script (no silent drops).

**Phase 7 (sweeps and community workflows, 120-180 jobs).** T1 = the official Klein 9B edit template
(graph JSON fetched to `templates/`, no model download); T2 = MediaPipe head boxes (built for Phase
3, reused); T3 = xy-grid sweep (needs a small xy node; ask before installing anything); T4 = SDPose
only if the DWPose flag count says so; T5 = Smart Character Swap probe (graph inspected node-by-node
for face detectors before its go). Every arm's prompt comes from the stills skill.

**Phase 8 (conditional, model change).** Only if G-SWITCH-EDITS is met. Candidate list, in order:
1. Qwen-Image-Edit-2511 + BFS v5 (C10 ~30.3 GB) - v2's plan, disk fits (238.8 GB free).
2. **FLUX 3 Image Klein** (open 5.6B, released 2026-10-17): newer, smaller, multi-reference
   editing; **its LoRAs are not interchangeable with FLUX.2 Klein**, so the S2 parts would have to be
   re-earned, and no FLUX 3 BFS head-swap weight is listed as of 2026-10-31. Needs its own research
   pass (file sizes, FP8 fit in 16 GB, encoder files) before any download ask.
3. Local FLUX.2 Klein **distilled vs base** A/B - v2's own fallback; the distilled file is on disk,
   `flux-2-klein-base-9b-fp8` (9.57 GB, gated) is not.

## 6. What "all phases" means, stated plainly

Executed now, on his existing answers: Phase 1 close-out, Phase 2 scoring, S2 calibration, Phase 3
(full), Phase 4 if its trigger fires, Phase 5 manifest + run once C8-P is set, Deliverable set,
Phase 6 staged run (68 jobs) with the download/bar ask, Phase 7 probes that need no new model.
Not executed by this plan: Phase 4 and Phase 8 when their triggers do not fire; Phase 6 arms needing
C13/C15/C16 before he says yes to those files; Phase 8's model download; LTX (his word, excluded);
the 294 Phase 2 images are scored, never re-rendered.

## 7. Cards for Derrick (asked as chat messages, not decided here)

1. **C8-P bar** for Phase 5 (his standing rule: he sets it before the phase runs).
2. **C8-S bar** for Phase 6, same.
3. **Phase 6 LoRA files, 0.58 GB** (C13/C15/C16) - v2 Q2's 3.6 GB figure is corrected here.
4. **S2 calibration yes/no** (section 4): test the four community values against the scored S2 control, 12 jobs.
5. **Phase 7 xy node** (T3) and any workflow JSON/mini-node installs - each asked before install.
6. For information, no action: the C3 model is already on disk (sha match), so no phase needs a base model.

## 8. Instruments

| Tool | Use | Status |
|---|---|---|
| `scripts/make_render.py` (`face_scores()`, `guard_ok`) | scoring counts, per-job guard | on disk, tested |
| `scripts/queue/flux_phase_gate.py` | gate enforcement (section 3) | **to build** (Phase 1 item) |
| `scripts/queue/queue_flux_replan.py` | Phase 3+ orders | on disk; needs the new manifest path (V3-3) |
| `scripts/queue/queue_storyboard.py` | Phase 6 | on disk, dry run 68 ready |
| `templates/flux_stills_s2_kv.api.json` + `_bfs.api.json`, `s2_dryrun_check.py`, S2 batch path | S2 two-pass builds | on disk |
| `templates/flux_crop_bfs_stitch.api.json` | Phase 3 CROP arm | **to build** |
| `assets/make_blind_pack.py` | blind packs | on disk |
| `scripts/tests/` | 61 tests pass | green at 21:2x CT |

## 9. Scout's five input points, point by point (F0)

1. *Phases 2/3 at S2 + the S2 prompt skill, new prompts and poses* - V3-3, V3-4, V3-8, sections 4-5.
2. *Every arm of every phase must be buildable; today Phase 3 builds only 1* - section 2 records the
   exact buildable set per phase, and V3-6 builds the missing Phase 3 inputs before the run; Phase 6/7
   not-built arms print their reason (no silent drop).
3. *Every gate names the bot or script; no phase starts on a missing/failed score file* - section 3,
   `flux_phase_gate.py` (V3-5).
4. *Quarantine and score the 294 Phase 2 images before any rerun* - V3-2, Phase 2 item; no re-render
   of Phase 2 is in this plan.
5. *Take Forge's context from the live llama-swap config, not the old 256K* - checked live at
   7:35 PM CT: pi runs `coding_swift15_iq3s_esp` through llama-swap `:8080` with
   `--max-context 131072` (128K, auto-compact ~110K). Item sizing in the fix_plan follows that.

## 10. Execution order = the fix_plan items

`C:\Users\derek\5slock\ralph-community\fix_plan.md`, block `# FLX`, one item per phase, inserted
after the OPT4 items so the running model-tuning loop finishes first. Items: FLX-1 Phase 1
close-out, FLX-2 Phase 2 scoring, FLX-3 S2 calibration, FLX-4 Phase 3, FLX-5 Phase 4 (conditional),
FLX-6 Phase 5 manifest + run, FLX-7 Deliverable set, FLX-8 Phase 6, FLX-9 Phase 7, FLX-10 Phase 8
(conditional report). F0 is closed by this file (section 9). Ralph runs one item per pass, under
`-PassLimitSec 3600`, GPU lock held per batch, DONE/BLOCKED note per item in
`C:\AI\community\notes\`, this file's `## Done log` gets one line per item.

## Done log

- 2026-10-31 9:35 PM CT v3 written by Forge (this file + community note `notes/2026-10-31-flux-community-best-check.md` + the verified-state table). No build, no render, no GPU, no lock, nothing downloaded.
