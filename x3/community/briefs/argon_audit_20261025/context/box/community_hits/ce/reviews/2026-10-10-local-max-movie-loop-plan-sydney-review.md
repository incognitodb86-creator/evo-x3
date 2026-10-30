---
title: Local Max Movie Loop plan - Max lane review (Fleet Architect, formerly Sydney)
date: 2026-10-10
reviewer: Fleet Architect (24f66698), Max lane owner
plan: ce/plans/2026-10-10-1800-feat-local-max-movie-loop-plan.md
mode: report-only (the plan is not edited)
verdict: READY AFTER FIXES (P0 1 · P1 6 · P2 6 · P3 3)
---

# Local Max Movie Loop plan: Max lane review

I checked the plan against how Max runs today. My sources were the max pack, the max-video and flux2 learnings, max-lane, the 60s continuity plan and its 26 review fixes, max-fix-tests, the face-lock v2 pack, the eight AlienPc and REF2VA skills, and fiction lock v2.1.2. Paths are relative to `brain-staging/` unless they start with `/`. "Plan:N" means a line in the plan file. Anything I could not check on disk is marked **UNVERIFIED**.

## Test vs production split (Derrick, 6:13 PM CT; record it as written)

| | Local-loop TESTS (this plan) | Production Max KEEP (unchanged) |
|---|---|---|
| Model | beta6 int8 8-step TURBO | beta6 int8 8-step TURBO |
| Sampler / scheduler | Euler / simple | Euler / simple |
| Steps | **6 (st6)** | **8** |
| Shift | 10 video / 3 audio | 10 video / 3 audio |
| Frame rate | **RIFE 20**: render a reduced frame count, then RIFE back up to 24 fps | **native 24 fps, no RIFE** |
| Dynamic VRAM / attention | on / ck-attention | on / ck-attention |

For these tests, st6 + RIFE 20 is settled. It is **not** a conflict, and no 8-step control is needed. The production KEEP stays as listed (`10_packs/max/production-defaults-st8-dynamic-vram.md:15,17`; `40_projects/max-lane/NEXT.md:10`). Plan D4 (plan:55) and R15/R16 (plan:86-87) should say "settled for tests", and OQ1 (plan:188) should be closed with the R20 definition below.

## Answers to the plan's open questions

### OQ1: what "RIFE 20" means
- Derrick (6:13 PM CT): it works like R12. You render fewer frames, then RIFE interpolates back up to full rate. The point is speed.
- **R12 is defined in the files.** The RIFE fair harness has `arm_cfg` R12 = `{"gen": 56, "rife": 2, "fps": 24, "fps_declared": "gen12_rife2x_play24"}` (`/workspace/maxops/audit-2026-10-09/alienpc-meta/scripts/queue_dynvram.py:47-48`). R8 = 39 gen frames, RIFE 3x (`:49-50`). R0 = native 124 frames (`:45-46`). The research table says the same: "R12 ~56-73 (12fps semantics) | RIFE VFI 2x → ~24" (`/workspace/cos/research/2026-10-06-h3-lowfps-rife-film-fair-cell.md:41`). Node: `RIFE VFI`, `rife47.pth`, integer `multiplier` (`queue_dynvram.py:116-121`). Measured walls at 768x1344, ST8, 5 s: R0 ~139 s, R12 ~54 s, R8 ~38 s (`/workspace/cos/status/ce-plan-alienpc-max-rife-fps-fair-2026-10-06.md:4,57`).
- **So R20, by the same naming, means: generate at about 20 fps worth of frames, then RIFE up to 24 fps playback.**
  - 5 s: ~103 gen frames instead of 124.
  - 10 s: ~203 gen frames instead of 243.
  - That is about 16% fewer frames. Render time tracks frames (`20_learnings/max-video/render-time-tracks-steps-only.md:6-7`), so expect about 16% off each render.
- **UNVERIFIED, and the implementer must decide:**
  - **How 20 gets to 24.** RIFE VFI only takes an integer multiplier, and 24/20 = 1.2. No file defines an R20 arm. Two candidates: (a) RIFE 2x to a 40 fps-equivalent, then `ffmpeg fps=24` resample; (b) a different integer path. Pick one, write it into the `rife.json` template and `U1_live_retest.md`, and keep it fixed for the whole run.
  - **Exact frame counts.** They must be lengths the REF2VA node accepts. Every length used so far (22, 39, 56, 62, 124, 243) worked, but the rule behind them is not written down.
  - **Timing.** A 20 fps-semantics clip carries about 8.4 s of model motion across 10.1 s of playback, so motion plays about 17% slower. Prompts may need phase times compressed by about 20/24, or motion that is a bit faster than wanted.
  - **Quality.** RIFE ghosting and smear on limbs, fabric and fast motion is the documented risk (`research/2026-10-06-h3-lowfps-rife-film-fair-cell.md:27-28`). Derrick said RIFE 2x looked worse than native (`render-time-tracks-steps-only.md:8`). That is accepted for these tests, but the review has to look at the RIFE output (see F8).

### st6 fit
st6 = 6 sampler steps on the same stack (plan:60 is correct). The 10 s review measured ST6 at ~305-309 s and ST8 at ~395-399 s, hot, 243 frames (about 23% faster). ST8 won or tied every category, and the big defects were the same at both step counts (`/workspace/maxops/sydney-10s-tests-2026-10-09/REVIEW_ST6_vs_ST8_10S_2026-10-09.md:3,32-34`; `20_learnings/max-video/st6-vs-st8-10s-beta6.md:7-8`).

For these tests st6 + R20 is settled and fits the goal of proving the loop. The plan just needs to:
- record the test vs production split (above);
- make the KTD3 preflight (plan:216) check `steps == 6` and the R20 frame count for loop jobs, plus a `TEST_ST6_R20` label, so a production Max job never inherits it;
- update the budget (plan:135, 145). The estimate is about 0.84 x 305 s ≈ 255 s per 10 s cell before Method C overhead, plus RIFE. **UNVERIFIED; U1 measures it.**

### OQ4: how Fleet Architect queues renders without holding the AlienPc Shell
- **Who can submit.** Switchyard already allows only two submitters, Derrick and Sydney Clone. Other bots ask Sydney Clone, and she submits for them (`ce/plans/2026-10-09-1622-feat-alienpc-local-ai-shared-gpu-plan.md:51,67,145`; AE2 `:156`). Holding a Max lease makes the queue stop starting jobs ("held: Max lease", `:149`). Taking the lease for a render would therefore stall the loop.
- **Proposed path** (needs Derrick's yes, because R2 was his pick):
  1. Fleet Architect writes a render request bundle on the box: the prompt `.txt`, the start-image filename from the settled list, the arm (frames, steps, R20 or native), the seed policy, the output name, and the label. It adds one line in `30_handoff/inbox/` addressed to Sydney Clone.
  2. Sydney Clone, as Shell holder, copies the bundle to AlienPc. She submits `max_render` with submitter `sydney` (Fleet Architect) as a named flag. It is not authentication; see shared-GPU plan `:414`. She does this at her next window, in the order requests arrive.
  3. FCFS goes by Switchyard submit time (R4). The box line time is logged for audit.
  4. Sydney Clone copies the outputs back to the box and writes a done line.
  5. Fleet Architect never runs AlienPc Shell and never asks for the lease to render. The lease moves only for non-queue work (installs, ComfyUI restarts), through `30_handoff/status/2026-10-10-1610-alienpc-lease-rule-max-lane.md:3-5`.
- **Plan changes:** KTD2 (plan:215) and U2 step 5 (plan:359) should say "Sydney's jobs are entered by Sydney Clone under submitter `sydney`", not "open to Sydney". **UNVERIFIED:** the submit CLI's flag names (U2 builds them).

### OQ2, OQ3, OQ6 (proposed answers)
- **OQ2.** Have Derrick lock both one-liners in his run GO. It costs one line. The pack requires it before a product queue (`10_packs/max/lock-length-and-beats-before-a-product-queue.md:9`). Also ask him to waive the movie director's second stitch GO (`/home/box/agent-data/workflows/alienpc-max-movie-director/SKILL.md:50`), only for cuts labeled DRAFT.
- **OQ3.** A local stills review does not meet package D's "watch the full clip" (`10_packs/max/scores-in-words-keep-is-derricks-go.md:9`). Call it what it is: a "stills review (2/s + face crops) + TECH motion", not a watch. That is enough for automatic hard-scrape triage, which is objective plus named melts. Derrick's watch of the cut is the full watch. The triage log is the quality stamp (`quality-stamp-before-derricks-eyes.md:9`).
- **OQ6.** Pin frame 0 on **every** cell, but to the right picture (see F1).

## Findings

| # | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|
| F1 | **P0** | **The Method C hop will snap back to the start pose.** The proven graph pins frame 0 with `MiniMaxH3AddGuide` set to the start image, and the FV2 retention marks `<Picture 1>` fully_preserved for "opening composition, thigh-deep stance, ... bikini". KTD4 keeps the original start image as `<Picture 1>` on every hop and defers the pin (OQ6). If the cell-1 template is reused, every seam resets the pose and wardrobe to frame 0 of the movie, so seam teleports are guaranteed. | plan:70, 217, 196; `/workspace/maxops/facelock-v2-2026-10-10/README.md:21`; `FV2_C0R_POOL.txt` retention line; pack `production-defaults-st8-dynamic-vram.md:22`; `20_learnings/max-video/chained-prompts-lock-scene-not-pose.md:7`; ref2va skill `:64-69` | Cell 1: AddGuide frame 0 = start image, as today. Cells 2-N: AddGuide frame 0 = the accepted prior clip's last native frame (PNG at the exact index), or no pin. Never the original start image. The start image stays as the face/hair/skin reference only, with a retention line like "face, hair, skin and proportions come from <Picture N>; pose and wardrobe follow the continuation". Scene and light stay locked; pose and wardrobe are "the starting point and change only as described". Add a U7 test that cell 2's guide image is not the start image. |
| F2 | P1 | **Fleet Architect has no legal submit path.** KTD2 and U2 open `max_render` to "Sydney", but Switchyard R2 allows only Derrick and Sydney Clone. Taking the lease holds the queue. D3 can't be built as written. | plan:46, 82, 215, 359, 366; shared-GPU plan `:67, 145, 149, 156, 414-415` | Use the OQ4 path above. U2 test: "a `sydney` job is entered by Sydney Clone and runs in FCFS order". Get Derrick's yes to add `sydney` as a named submitter that only Sydney Clone can enter. |
| F3 | P1 | **The unsolved defects will park every strip draft.** The garment teleports or vanishes at ~2 s in all 9 fix-test clips, and hands fuse into fabric at every setting. R19's hard list has "seam teleport" but doesn't say how an **in-cell** garment teleport is classed. If the VLM or harness counts it as hard, each strip cell burns 3 attempts and parks. Only finger fusion is called soft (AE3). | plan:92, 151; `20_learnings/max-video/full-spins-break-face-lock-and-garments-teleport.md:8`; `hands-melt-into-garments-every-setting.md:6-8`; `40_projects/max-lane/NEXT.md:16-17` | Add to R19/KTD7: an in-cell garment teleport or vanish and hand-into-fabric fusion are **soft**, logged in words, and the cell advances. Stage around them in the beat sheet: lay the garment down instead of tossing it, keep it in hand, no gripping inside fabric, hands flat on skin, lift tops by the side edges, no full spins. The handoff (`workflow.md`, `prompt-craft.md`) carries this. |
| F4 | P1 | **Forge gets stale or contradictory craft.** U6 gives Forge raw copies of the movie director, REF2VA and hardcore skills. They still say "REF2VA does not pin frame 0", `ref_image_size` match-only, `[reference generation]` as default with keyframe completion only as a try, KEEP = beta/res_multistep/25 steps, and "One Shell owner: Max Studio". None of R4, U5 or U6 names the proven 2026-10-10 prompt defaults or the FV2 templates. | plan:69, 429, 450; ref2va `SKILL.md:102,105`; hardcore `SKILL.md:81`; local-video-ops `SKILL.md:18,60,70`; pack `production-defaults-st8-dynamic-vram.md:19-27`; `face-block-prompts-fix-face-lock.md:7,11` | Point Forge at `40_projects/local-max-movie-loop/sydney-handoff/` (written with this review) instead of the raw skills. Add these U5 lint checks: a face block in subject_definitions; a "same face" anchor in every phase; fabric/light words that match the start-image read; no `spin`/`360`/`full turn`; zero hits for `\b(no|never|not|without|don't|nothing)\b` (60s plan `:138`); labels stable; `[keyframe completion]` + "first frame of [Shot 1]" on pinned cells. |
| F5 | P1 | **The R20 mechanics are undefined.** It's settled as a test setting, but the frame count per length, the 20→24 conversion (RIFE takes an integer multiplier) and the timing effect on prompts are not specified. The budget still assumes native 24 fps (plan:145). | plan:61, 87, 145, 188; `queue_dynvram.py:43-58,116-121`; research lowfps `:41` | Close OQ1 with the R20 definition above. Fix one conversion method and the frame counts in `rife.json`/node_map. U1 renders one R20 ST6 cell, RIFEs it, and records wall times and output frames. Note in the prompt kit whether phase times are written in model time. Method C and seam replay always use the **native** pre-RIFE clip (KTD4 already says so; keep it). |
| F6 | P1 | **The brief template strips the canon minors line.** KTD11/U5 says briefs carry the filename and "confirmed fictional adult" and "nothing else". Canon v2.1.2 requires every image brief to carry its full sentence: no identity or resemblance judging, plus "If any frame shows a minor or clear signs of youth, stop and report that item." R8 cites v2.1.1, but the file is v2.1.2. | plan:75, 224, 431, 439; `/workspace/cos/canon/fiction-cond-lock.md:1,21-22` | The brief template = filename + "confirmed fictional adult" + the canon v2.1.2 brief sentence, exactly, plus nothing about history. Change the U5 test to check that. The reviewer prompt carries the minors stop line, and `youth_pause` stays in the schema (KTD6, already there). |
| F7 | P1 | **The settled list can't be matched by filename, and it carries provenance.** settled-images.md lists folders and pick IDs (E2, E3, E6-E11, B01-B08, M01-M10, the 8 dark-hair picks), not filenames. Line 7 has a provenance note. Matching an exact filename against a snapshot would refuse most listed images, and copying the snapshot into the kit would put history into Forge's context. | plan:224, 427, 433; `10_packs/max/settled-images.md:7-13`; `lora-rules.md:17` | At setup, Sydney Clone writes a kit allowlist: resolved absolute AlienPc paths + sha256 + "confirmed fictional adult", no notes. The guard matches path + sha. The pack sha is logged for traceability only. |
| F8 | P2 | **The delivered artifact is never reviewed.** KTD8 RIFEs after every review, so the R20 cut Derrick sees has had no stills pass, even though RIFE ghosting on fabric and limbs is the known risk. | plan:221, 495; research lowfps `:27-28`; `render-time-tracks-steps-only.md:8` | After RIFE, run the stills sheet (2/s + face crops) on each interpolated cell and the cut. Log RIFE breaks in words; they are soft and never trigger a re-render. Ship the native pre-RIFE cut beside it as `DRAFT_<d>_native.mp4` for reference at zero GPU cost. |
| F9 | P2 | **The review spec is missing face crops and cadence.** KTD6 samples ~0.5 s but has no face crops. Max review = stills at 2+ per second (11+ per 5 s, 21+ per 10 s, plus the last frame) **and face crops at the same times**. A 16K VLM context may not hold 22 frames + 22 crops. | plan:219, 389, 194; `40_projects/max-fix-tests/draft-skill-max-clip-review.md:37-40`; `tools/clip_sheets.py` | Port the `clip_sheets.py` cadence and face-box logic into `clipframes.py`. Batch per 5 s window with a 1-frame overlap (OQ5). Score the face only on frames where it's visible. Add a frame-0 vs start-image check. Check the first 0.5 s of every multi-ref clip for a cut (`standalone-picture-line-can-render-as-opening-shot.md:9`). |
| F10 | P2 | **The Method C template and cost are unproven on beta6.** KTD3 exports templates from Sydney's 10 s cells, which have no `ref_video` input. The only Method C graph is the 2026-10-05 `queue_1min_ref2va.py` (shift 12, res_multistep/beta, beta5 era). Seam replay is NO_DATA. Feeding a whole 10 s clip as `<Video 1>` may cost far more than the assumed +20% and may push VRAM. U1 only times a plain cell. | plan:135, 216, 299, 338; `/workspace/MAX_1MIN_C_VS_A_2026-10-05/scripts/queue_1min_ref2va.py:90-96`; research `2026-10-06-max-5s-hop-continuity.md:26,83` | Build the template from the FV2 graph (REF2VA → AddGuide → BasicGuider, Euler/simple, shift 10) plus the `LoadVideo → GetVideoComponents → ref_videos.ref_video_1` wiring. Add one Method C hop to U1 (time, VRAM, replayed-frame count). If it's heavy, test a tail-only reference video (last ~2 s). **UNVERIFIED** whether the tail is enough. |
| F11 | P2 | **The length check can park a finished draft.** 6 x 10.125 s = 60.75 s nominal. Five crossfades plus replay trims (community overlap is ~22 frames ≈ 0.92 s) can push it under 55 s, and then U8 parks it as `parked:length` after spending the whole budget. | plan:66, 278, 499; research 5s-hop `:54` | Lint the expected length after trims at beat-sheet time: plan about 62-64 s nominal (for example a 7th short settle cell). Report a short cut instead of parking it. It is a DRAFT. |
| F12 | P2 | **OQ2 and OQ3 need Derrick's answers before U11.** The plan raises them but runs autonomously anyway. | plan:189-190 | Use the answers proposed above, and add them to the approvals list (plan:285-292). |
| F13 | P2 | **The lease record is split across stale files.** The pack still names Sydney as sole Shell holder, and so do the skills (movie director, lease skill, local-video-ops "Max Studio"). The live record is Sydney Clone. R14 cites the pack. | `10_packs/max/one-holder-for-the-alienpc-shell.md:10`; `30_handoff/status/2026-10-10-1610-alienpc-lease-rule-max-lane.md:3-5`; `2026-10-10-0946-...:9`; movie director `SKILL.md:65`; lease `SKILL.md:27`; local-video-ops `SKILL.md:60` | R14 should cite the latest `30_handoff/status/*lease*` file as the single live record. Report the stale pack and skill lines to Derrick (a pack edit needs his yes). |
| F14 | P3 | **Name and version drift.** The plan says "Sydney". The bot is Fleet Architect (24f66698, formerly Sydney). R8 says v2.1.1 (plan:182 already notes v2.1.2). | plan:45, 75 | Rename, and cite v2.1.2. |
| F15 | P3 | **Draft B's default image has two bodies.** The orc frame needs limb inventory and partner geometry, and the 10-09 orc clip showed hand-into-hip fusion and clothing morph. Two-ref and two-body faces drift on head turns. | plan:277; ST6 vs ST8 review `:24-26`; `two-ref-faces-drift-on-head-turns.md:6-7` | Keep heads three-quarter or frontal and no profile turns. Use limb inventory every cell. Forge may pick a single-subject listed image instead. |
| F16 | P3 | **The RIFE minute and swap times are relayed, not measured.** | plan:129, 138 | U1 measures them (already planned for swaps; add RIFE). |

## What the plan gets right
- Words-only scoring with no bot KEEP or PASS, a reject folder, and pairwise A/B in both orders (plan:91-94, 220).
- Fail-closed gates with named exits, UTF-8 logs and the ParseFile gate (plan:214, 565), matching the 60s review fixes R1, R2, R9 and R24.
- Warm-first, a new seed per attempt, audio stripped, WinError 1450 handled per cell, no `/interrupt`.
- Item-level minors pause with the other draft continuing (AE4), and resemblance comments dropped (AE5, R10).
- No Grok Imagine prompts or sidecars (R11, U3 test).

## Unverified
- The R20 conversion method and frame counts; R20 wall time; whether phase timing needs compressing.
- Method C cost, VRAM and seam replay on beta6.
- The Switchyard submit flags for a `sydney` submitter.
- Whether any reviewed Method C seam result exists. I found none on the box.
