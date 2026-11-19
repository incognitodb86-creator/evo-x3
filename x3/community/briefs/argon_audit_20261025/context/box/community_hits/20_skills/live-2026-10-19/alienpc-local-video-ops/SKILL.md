---
name: AlienPc local video ops
description: >-
  use this when inventorying, configuring, leasing, or quality-gating AlienPc
  ComfyUI — llama-swap :8080/comfyui (backend :10002) Max production, package D
  watch+auto triage, Pre-Derrick auto-CAPA, autonomous loop control, community
  WF+deps, single Shell lease
---
> **Retired 2026-10-19 (Derrick 9:12 AM CT: "Yes, retire them"; overrides V11-V13 in /workspace/cos/plans/2026-10-19-community-overrides.md):** per-clip judges, ArcFace face bands, hand/limb gate, aftercare keyword gate, writer LLM, schema pass gate, 48-beat sheets and the 98-check preflight are OFF the default path (archived, not deleted; archive /workspace/cos/_archive/retired-gates-2026-10-19/). Default now: Derrick reviews by eye and the bad chunk is re-rolled; hand-written short prompts, 4-6 shots per scene; the saved API workflow + ComfyUI's own validation (`POST /prompt` node_errors, `GET /object_info`) as the config check before each test.
> Results rule: a test arm is "pending" until clips.csv/review.csv/fd CSV has ≥1 non-skip row for it; any JOB error or CLIP_SKIP marks it "broken" in LOOP_STATE and Linear within one heartbeat.
> Restart rule: comfy_ok() + canary() pass, then release the queue (loop.py.fix0815 does this; never bypass it by hand).
> **Current setup (2026-10-16, overrides anything below):** ComfyUI only through llama-swap at `http://127.0.0.1:8080/comfyui`; llama-swap starts the ComfyUI backend on `127.0.0.1:10002` (scripts that post to :10002 directly bypass llama-swap's sync hold, so nothing else may call a model in the group while they render) (exclusive group: comfyui_auto, coding_sc117_strata, vl_judge; one job at a time). `:8188`, `:8189`, Switchyard, LTX, Wan 2.2 and Flux.1 Kontext are retired/deleted; stills = FLUX.2 Klein 9B (flux2 encoder + FLUX.2 VAE). (RETIRED 2026-10-19, not default; see top note:) Director = **vl_judge (Dark Roast Q8)** with the REF2VA skill loaded. Judges = every vision model in the test (Dark Roast Q8, Qwen3-VL-8B abliterated, and any other judge arm), each calibrated on a known-good and a known-bad still first (Derrick 2026-10-16 7:54 PM CT: "judge test first, then all models"). **No judge has passed yet** (U-B Oct 16; judge comparison Oct 17 4:01–4:02 AM CT: vl_judge and qwen3vl_judge both failed calibration, 9/18 agreement, stills all "no breaks", strips all "breaks"), so Max's full-size review is the only gate until a judge is promoted (bar kept by Derrick 2026-10-17 5:55 AM CT: passes calibration AND ≥90% agreement with the strict review on a labelled set AND 0 false passes on hard breaks); rules in alienpc-stills-pose-edit-prompting (end of retired text). Strata is coding only. Video = 768x1344 or 1344x768 @ 24 fps, H3 frames%17==5 (124 default); the 5s-lock driver renders clips at 768x1120 (open canvas question for Derrick, residual R5). Extension clips carry `<Video 1>`, injected by code. LTX references below are historical only.
>
> **(RETIRED 2026-10-19, optional tool only)** **Judge rubric v2 (PROVISIONAL, 2026-10-17, advisory only, not promoted):** prompt `loop1017/judgecmp/judge_rubric_v2.json`, run with `judge_cmp_j1.py <model> --rubric v2` (or job env `J1_RUBRIC=v2`; v1 stays the default). Community-first design (DSG atomic yes/no, T2I-CoReBench visible-evidence-only, describe-then-answer in two stages, counts/colours as values decided in code): one candidate image per call plus the E10 reference labelled "identity/attire reference only, do not judge it"; strips are split into single frames; questions count her hands/arms/legs and his hands, fused fingers, toes through boots, garment worn-and-held / missing vs the beat / ghosted, face parts in place, genitals plausible, dark stone-hall style, attire vs ref (circlet, choker, wrist-cuff colour silver not gold, silver knee-high boots). Every yes/no is phrased YES = break; any one YES = FAIL. Never judges identity from a face (canon v2.3.0). The promotion bar is unchanged.

# AlienPc local video ops

## When
ComfyUI on AlienPc (ListMachines → AlienPc): **llama-swap :8080/comfyui** (backend :10002) TestRuntime = FLUX.2 Klein stills + Max H3 I2V (**production**). `:8188` / `:8189` are retired (historical rows below). Before claiming local I2V READY.

**Pair:** [AlienPc community matrix cell](sand-workflow:alienpc-community-matrix-cell) for every matrix cell. **Lease detail:** [AlienPc local-exec lease](sand-workflow:alienpc-local-exec-lease).

**Canon:** `/workspace/cos/research/alienpc-ltx-stack-2026-09-25/`

## HARD — Max llama-swap :8080/comfyui production argv (Turbo KEEP 2026-10-09 Derrick GO · restated 2026-10-14)
**KEEP:** `10Eros_Max_h3_8stepTURBO_beta6_int8` (beta6 int8 Turbo) · **Euler** (simple) · **8 steps** · **shift 10** (video; 3 audio) · dynamic VRAM ON · no-fp8 · `--use-ck-attention` ON · ComfyUI **0.38.x pinned** · REF2VA match · length default **124f**. **Tests / local loop:** **6 steps + RIFE 20**. Old Oct 2 non-Turbo beta/25-step = optional quality A/B experiment only, not default.  
**Preview canvas (speed / low-VRAM):** **864×480** — not native quality SoT; soft Quality here = resolution miss until fair NE768 or Derrick GO.  
**Quality canvas (TRY / fair after Derrick GO):** **~768 short edge** AR-locked to Cond (~1344×768 @ 16:9 landscape). One axis only; OOM → stop, do not peel steps/scheduler. Remacri does not invent missing generate detail.  
**DROP:** STEPS-20 · SPARSEsol · Sage · Lightning/EasyCache/Spectrum/fp8 peel (Turbo beta6 int8 is KEEP). ("DynVRAM peel" DROP (superseded 2026-10-09: dynamic VRAM ON is KEEP).)  
**Dynamic VRAM (KEEP 2026-10-09 Derrick):** ON by default (Oct 8: cold first run 116.2s → 44.1s; hot unchanged). If WinError 1450 / paging-file errors return, disable dynamic VRAM for that single cell and log it. ST8 Turbo default stays. All defaults REVALIDATE after rebuild.  
`:8188` is retired (H2H rows are historical). Full argv + evidence → `references/max-8189-production-keep.md` (historical file name).

## HARD — Matrix warm-first (LOCKED 2026-10-05 ~8:20 PM CT Derrick GO)
**Next Max decision matrices:** ~**1s sacrificial** (unscored) → **full 124f warm** (unscored) before scored rows. Do not change an in-flight pack. Closed fair arms = baseline — **do not re-queue** same steps/Cond/seeds just to compare (ST8-only vs prior ST16 pack OK). Details → `references/max-8189-production-keep.md`.

## HARD — Community WF + deps first (LOCKED 2026-09-25 ~14:11 CT Derrick)
If a published 10Eros/image-lock WF exists: **download WF + ALL weights**, verify on disk, run **as-published** before freestyle. Gap tables name downloads. Forbidden: bare official as dial host; GOLDEN+one-knob as community match; smoke then discover missing LoRAs.

## HARD — ≥3 smokes · FAIL→fix · still AR · community FAIL=OUR SETUP · single lease
See [alienpc-community-matrix-cell](sand-workflow:alienpc-community-matrix-cell) for full text. CondSafe/NSFW/cam/Union GOLDEN = our pin; community as-published overrides when matching community is the goal.

## HARD — Video watch + scoring v2 package D (LOCKED 2026-10-05 Derrick GO)
**Watch the full clip** for triage and drafts. Screenshots/thumbs alone never crown (scripts = collage notes only).

**Auto triage (every clip, no ask):**
1. Hard scrapes → **reject folder** with one-line reason; HOLD off Derrick's eyes. Hard set = objective TECH (blank, corrupt, frozen, near-static) **and** clear Identity melt named in words after a watched clip. Spot-check **Identity-melt rejects** (judgment risk); spot-check a sample of TECH rejects too. Never delete silently.
2. Soft breaks → **candidate**: name Identity / Quality / Motion breaks in words + optional **draft 1–5** (labeled draft).
3. Derrick crowns: confirm/edit 1–5; fair cells **A/B** first; **KEEP = exact GO only**.
4. Banned bot crowns: PASS, KEEP, Integrity mean, 0.95. Face-match / auto metrics are optional notes only (calibrated ArcFace bands in strict-still-review.md check 8 retired from the default path 2026-10-19); a metric never clears a candidate alone. Identity = same character as the Cond; vision and face-match never decide whether a person is real (R1).

**HOLD = hold from Derrick's eyes, not stop (2026-10-17):** every "CAPA + HOLD" below keeps failing work away from Derrick; the loop continues with the next fix until that beat's budget is spent, and parking follows "Autonomous loop control".

**Pre-Derrick auto-CAPA (LOCKED 2026-10-06):** Stills **Contact/Hands FAIL** (hard scrape) · still pose FAIL vs intent · setup FAIL · product≠method (T3/T6 METHOD_ONLY) · fairness alone ≠ surface (T4) · chain-past-FAIL · systemic hard scrapes → **CAPA file + HOLD** before Derrick review. Soft Quality candidates may still surface; **Contact/Hands stills are never soft.** Full table → `references/video-integrity-motion-amp.md` · CAPA `/workspace/cos/audits/2026-10-06-scoring-auto-capa-pre-derrick-capa.md`. Stills/panels: if no candidate clears review (Derrick's eye review; the Max full-size review + calibrated-judge gate is retired 2026-10-19) → CAPA + HOLD from Derrick's eyes, then the next round. Never offer Derrick a choice between failing candidates or a "borderline/accept" option; report the blocker and next fix. Before any render: start panels cleared this gate, size 768x1344/1344x768, plan unit named.

Do not crown with image criteria / IF / thumb-glance / TECH alone. A freeze is a Motion break. Full locks → `references/video-integrity-motion-amp.md`. Brief: `/workspace/cos/research/2026-10-05-ai-video-scoring-best-practices.md`.

## HARD — Autonomous loop control (Derrick 2026-10-17 2:57 AM CT; Fleet Reviewer F1–F13)
- **Per-beat budget:** panels ≥3 rounds × ≥8 candidates, one variable per round, before a beat may park; clips ≤5 redos per beat, **stop on the first "no breaks found"**. Reset the budget whenever the metric, harness or rubric changes.
- **Park criteria (write which):** (a) budget spent, (b) no progress across 3 rounds (best face distance not better by ≥0.03 and no new rubric pass), (c) a Derrick-only blocker with no in-scope alternative.
- **Priority:** product beats (panels → clips → stitch) before research/diagnostic arms; diagnostics only in gaps or after every beat is finished or parked. A blocked path falls straight to the next open beat.
- **Run length:** each run follows the deadline in its BRIEF (whether no-deadline runs become the default is pending Derrick). If Derrick removes the deadline for a run (e.g. Oct 17 overnight run, 3:47 AM CT: "Not at 630 when it's done continue until done and we have our pipeline setup ..."), that run continues until every beat is finished or parked and its stated goals are met; it is not a default for future runs. GPU idle >10 min while a beat is open = defect (log it, queue the next round). Keep LOOP_STATE current (heartbeat ≤5 min) and write a full handoff before a worker runs out of context.
- **Loop state:** `LOOP_STATE.md` per run (beat × stage × round × budget left × best × next action, heartbeat ≤5 min); takeovers read it first.
- **Learn and improve (Derrick 3:45 AM CT: lessons land as steps, defaults or guards):** each lesson goes 1) into LOOP_STATE `## Pipeline changes` (lesson · evidence · proposed step/default/guard · status), 2) becomes a tested default in the loop worker or job config (one-variable arm, ≥3 seeds, backup + test; production-recipe changes stay loop test defaults until Derrick's decision row), 3) then a skill update (staged, Derrick-approved), 4) then a Fleet Reviewer audit that checks it landed. A note alone is not a learned lesson.

## HARD — overnight horrible CAPA (LOCKED 2026-09-26 · package D 2026-10-05 · Pre-Derrick 2026-10-06)
Scout ≠ KEEP. Fair dial = one locked axis ≥3, for stills, panels, judges and renders alike: change ONE variable per round (method, LoRA, prompt style, steps/cfg, or judge), everything else held, so the result can be attributed. Empty POS never winner. POS dialect by host (no LTX POS→Max). Watch Identity/Quality/Motion (package D) before asking Derrick GO — no Integrity/PASS crowns. Overnight must not parade FAIL packs until CAPA on disk. Full → `references/overnight-horrible-capa.md`.

## Stack lock (LOCKED 2026-10-02 exact B — Derrick via CoS)
**Flux.1 Kontext / FLUX.2 [klein] stills + Max (10Eros H3 / MiniMax-H3) I2V on llama-swap :8080/comfyui** = **PRODUCTION SoT**. LTX Recipe B (:8188, retired) = archived baseline/METHOD/H2H evidence only. Home stays HOLD until Derrick clears Identity, Quality, and Motion and gives exact GO. Max KEEP needs fair H2H + exact GO. **1-min path:** Max-first REF after env+Max GO (Flux2 F1 deferred). License NOT a CoS gate. ZI/Qwen parked; WAN deferred; Fill STOPPED. Goal = realistic thrust/contact, not Face-freeze. Stamps: `/workspace/cos/audits/2026-10-02-alienpc-stack-A-vs-B.md` · `2026-10-02-flux2-max-skill-research.md` · `ce-plan-flux2-alienpc-2026-10-02.md`.

## HARD — Max-first product order (~1-min)
REF2VA-first on llama-swap :8080/comfyui after Max GO · If Derrick attached a still, that file is the cond. Do not substitute HC3 · Flux2 F1 deferred · multi-clip for ~60s · no LTX POS→Max · KEEP=Derrick GO only. Full 10-step → `references/max-first-product-order.md`. Product packs also need [alienpc-max-movie-director](sand-workflow:alienpc-max-movie-director) (beat sheet / multi-phase; METHOD_ONLY labeled).

## HARD — Flux2 fair matrix (stills lane METHOD only)
S0 → F1-confirm (host frozen ≥3) → F2 → optional F1b. Cell1-first `FAIR_FLUX2_KLEIN9B_P163_ACTFIRST_F1`. scout ≠ crown. Cite Plan `status/ce-plan-alienpc-fair-matrix-replicate-2026-10-02.md`.

## HARD — AlienPc local-exec lease (LOCKED 2026-10-02)
**One Shell owner:** the holder in the latest `30_handoff/status/*lease*` file only. Others never run Shell on AlienPc; ask that holder. Hang >15–30s empty → stop, no retry-spam. Recover: Quit → kill local-exec-daemon → relaunch → ~1 min → one probe. PowerShell-native. Full → `references/local-exec-lease-full.md` · skill [alienpc-local-exec-lease](sand-workflow:alienpc-local-exec-lease).

## HARD — background job brief wording (LOCKED 2026-10-01 ~18:55 CT)
Never put explicit porn labels in helper task briefs. Neutral dial language: cell name, Cond, POS path, thrust/motion intent, adults 18+, ports, paths. Spicy POS stays in Cond/POS files on disk.
Content floor: fiction-cond-lock v2.3.0 via (pack: max, fiction-and-cnc-follow-the-linked-canon.md) — minors-only hard stop; fictional adults only, records decide, never sexual content of a real identifiable person; pause any clip whose image shows a minor (canon rule 4). R3: never open, read, quote or parse Derrick's Grok Imagine generation prompts or prompt sidecar files (Derrick 2026-10-09).

## Max prompts
Use `/workspace/MAX_PROMPT_LTX_PARITY_2026-10-01/` strong-thrust FL2VA/I2VA pastes; ban soft-thrust Face ladders.

## EXPERIMENTAL / DO NOT DEFAULT
STEPS-20 · SPARSEsol · Sage · fp8 · non-Turbo beta/25 A/B · SaveH3Embedding A/B · RefMods · dual Shell · Fill · WAN — **not** production. Full table → `references/experimental-do-not-default.md`. KEEP stays beta6 int8 Turbo · Euler · 8 steps · shift 10 · dynamic VRAM ON · ck · ComfyUI 0.38.x.


## Default test steps (LOCKED 2026-10-05 ~9:27 PM CT Derrick GO)
**Production = ST8 Turbo.** **Tests / local loop = ST6 + RIFE 20.** ST16 or old non-Turbo 25 only as an optional experiment Derrick names.
**RIFE 20 (as implemented 2026-10-16 11:31 PM CT in drv.py `--rife20`, after the 2026-10-07 MAX_RIFE_R20_10S_ST6 cell; definition pending Derrick, OQ1):** generate 107 frames (17n+5, ~21 fps over 5 s), frame 0 pinned, RIFE VFI rife47 ×2 → 213 frames, play 42.6 fps = 5.0 s.
