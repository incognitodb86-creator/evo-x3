---
name: AlienPc Max movie director
description: >-
  use this when building a multi-clip Max (~1 min) product scene on AlienPc —
  beat sheet first, distinct progressive prompts per cell, continuity wiring
  separate from act progression; never stitch same-act hops as a movie
---
# AlienPc Max movie director
> **Retired 2026-10-19 (Derrick 9:12 AM CT: "Yes, retire them"; overrides V11-V13 in /workspace/cos/plans/2026-10-19-community-overrides.md):** per-clip judges, ArcFace face bands, hand/limb gate, aftercare keyword gate, writer LLM, schema pass gate, 48-beat sheets and the 98-check preflight are OFF the default path (archived, not deleted; archive /workspace/cos/_archive/retired-gates-2026-10-19/). Default now: Derrick reviews by eye and the bad chunk is re-rolled; hand-written short prompts, 4-6 shots per scene; the saved API workflow + ComfyUI's own validation (`POST /prompt` node_errors, `GET /object_info`) as the config check before each test.

## When
Building a **~1 minute Max product** (or any multi-section REF2VA chain sold as a scene) on AlienPc (ComfyUI via llama-swap `http://127.0.0.1:8080/comfyui`, backend `127.0.0.1:10002`; prompts hand-written and short (vl_judge writer LLM retired 2026-10-19); one job at a time; canvas per local-video-ops). Not for single 5s keepers, fabric peel matrices, or fair **continuity-method** A/B smokes.

Pairs with: [REF2VA prompt](sand-workflow:ref2va-prompt) · [AlienPc hardcore I2V director](sand-workflow:alienpc-hardcore-i2v-director) · [AlienPc local video ops](sand-workflow:alienpc-local-video-ops) · Research 1-min continuity SoT `/workspace/cos/research/2026-10-05-max-h3-1min-multi-section-continuity.md`

## Outcome
A **directed scene**: N in-band clips (H3 frames%17==5) with **different prompts that advance one continuous story**, then assemble. Not a stitch of the same animate. Clip tiers: 124f native (Method C wiring) or the test tier 107f + RIFE x2 (local-video-ops "RIFE 20"); both are wiring/tier options, pick one per scene and label it.

## HARD — product vs method smoke (LOCKED 2026-10-06 Derrick FAIL)
| Label | Allowed | Forbidden as product |
|-------|---------|----------------------|
| **Product minute** | Beat sheet · **distinct PRIMARY MOTION per cell** · scene progression · stitch only after progressive seams | Same act body × seeds/hops sold as a movie |
| **Method smoke (C vs A)** | Same act body × seeds **only** to compare continuity wiring (Video-continue vs last-frame) | Calling that pack a 1-min clip / KEEP candidate |

**FAIL class (learn):** overnight `MAX_1MIN_C_VS_A` = method smoke. Stitching same S1 peel hops = **reject**. No KEEP from the Max lane owner (KEEP = Derrick's exact GO).

## Beat sheet (required before queue)
Write `BEAT_SHEET.md` in the pack folder before any Generate:

1. **Scene one-liner** — who, where, what changes over ~60s.
2. **Beats (4–6 shots per scene, default 2026-10-19; was 4–12 cells; 48-beat sheets retired)** — each row: `cell_id` · `intent_id` · **PRIMARY MOTION (unique)** · Cond/Pic job · prior Video job · ~length · settle note.
3. **Progression rule** — each cell must change at least one of: act phase, intensity, contact plane, wardrobe state, or partner action. **Same PRIMARY MOTION wording across cells = do not queue.**
4. **Seam contract** — end of cell N leaves a readable hold/settle that cell N+1 continues; no teleport pose mid-scene without a still unlock first.
5. **Non-goals** — no multi-act montage inside one cell; no single Generate = 60s; no policy/disclaimer text in Max-read pastes.
6. **Camera risk per beat** — mark side or profile start poses as high-risk (strict face gate retired 2026-10-19; history: S1B03, S1B04 and side-camera S1B05: 0 strict candidates in 103 panels; front-facing beats: 18 of 120). For penetrative beats, pick a start pose where the join faces the camera (open-thigh missionary S1B08 = both AI_KEEPs). Changing a profile beat's camera is Derrick's call; the bot flags it. [FINDING_side_face_metric.md; COMPARE_035_vs_055.md 07:23]

## Continuity wiring (orthogonal to beats)
- **SoT ★ Method C:** prior clip → `<Video 1>` · `[video continuation]` (+ optional task markers per Research) · **original Cond** stays `<Picture 1>` Face/ID `fully_preserved`.
- **Method A:** last-frame as `<Picture 2>` + keyframe completion — **labeled fallback / fair twin only**.
- Fair C vs A compares **wiring only** (same beat prompt). Product chains use **one chosen wiring** + **changing beat prompts**.

## Per-cell prompt craft
1. Load [REF2VA prompt](sand-workflow:ref2va-prompt) — six sections, Static Shot line when hold asked.
2. **One PRIMARY MOTION** obvious and pose-continuous with Cond + prior settle.
3. Diff gate: vs prior cell paste, the diff must show the **beat advance words** (and wiring tags if hop). Extra policy/notes = fix before queue.
4. Length argv in-band only; audio STRIPPED until picture seams pass (or labeled audio axis).
5. **Roll writer rules forward.** Once a writer rule is tested on one beat (held seeds, the rule is the only change), write it into every beat that hasn't run yet before its round 1, so new beats don't start on the old wording. S1B09 r1 and S1B10 r1 ran on the old jewelry wording after P18 had already fixed the cuffs: gold cuffs on 5/6 and 4/5 reviewed bodies, one round each lost. [LOOP_NOTES 07:00 / 07:10]

## Queue / watch / assemble
1. **Warm** then cells in beat order (or Plan-labeled parallel only when fair method).
2. After each cell: **watch full clip** (package D). Hard scrapes → reject folder. Soft → word breaks + optional draft 1–5.
3. **Seam-replay TECH** before concat (first frames of N+1 vs tail of N).
4. A bot may assemble a labelled **REVIEW CUT** (file name `REVIEW_CUT_*`, passing clips only, missing beats listed) without a GO. Product / KEEP still needs Derrick's exact GO.
5. **KEEP = Derrick exact GO only.** Bots never PASS / KEEP / 0.95 / Integrity mean.


## Autonomous overnight loop (Derrick 2026-10-17 2:57 AM CT, Fleet Reviewer audit F1–F16)
Stages per beat: beat sheet → minors guard → still panel → face pass (e.g. head swap) → strict still review → clip → frame check (cuts, face drift, garment) + watched review → redo → stitch REVIEW CUT. (2026-10-19: strict still review / face-drift gates are retired from the default path; Derrick reviews by eye and the bad chunk is re-rolled.)
1. **Finished vs blocked.** Finished = REVIEW CUT covering every beat, each clip "no breaks found". Any beat parked = run reports **BLOCKED (n of N beats)**, never "done with blockers".
2. **Budgets, rules and park criteria** live in [local-video-ops](sand-workflow:alienpc-local-video-ops) "Autonomous loop control"; follow them for panels and clips.
3. **Loop state + brief on disk:** `LOOP_STATE.md` (beat × stage × round × budget left × best candidate × next action, heartbeat ≤5 min) and `BRIEF_<date>.md` (goal, deadline, done/blocked, budgets, priority order) before launch. Every takeover reads both first.
4. **Scope = the minute.** An overnight product plan targets ~60 s (e.g. 12 × 5 s beats) or says why not.

## Scoreboard checklist (T3/T6 · Max lane owner)
Before queue **or** before harvest chat for any pack labeled product / 1min / movie / stitch / continuous scene:
1. Confirm **distinct PRIMARY MOTION** per cell (or refuse queue).
2. If PRIMARY text/sha is **identical across ≥2 cells** → force label **METHOD_ONLY** · refuse product wording · CAPA if Plan said product.
3. No stitch GO ask until `BEAT_SHEET.md` exists and seams pass.
4. **Seeds:** product packs = **new random seeds every wave**; fixed `71–73` = METHOD twin only.
Full Pre-Derrick table → [alienpc-local-video-ops](sand-workflow:alienpc-local-video-ops) `video-integrity-motion-amp.md`.

## Owners
| Role | Owns |
|------|------|
| Sydney/Max Architect (24f66698) | Scoreboard · takes the AlienPc lease to render (single holder = latest lease file) · queue · handoff |
| CoS | CE Plan / CAPA |
| Max lane owner (ROSTER) (research subagents) | Beat sheet research + hop pastes |
| Fleet Reviewer | Fairness stamp (one axis, seeds, no prompt leak) — never KEEP |

## Deliverables
`BEAT_SHEET.md` · per-cell REF2VA pastes · pack Desktop folder · seam notes · scoreboard · reject reasons

## Anti-patterns (DO-NOT-REPEAT)
- Same animate × N seeds → stitch → call it good
- Fair C/A method pack presented as the 1-min product
- Reusing product seed ladder `71–73` for “more of the same” 5s / parade
- Multi-position montage in one 5s prompt
- Bot crowning KEEP / PASS / 0.95
- Dropping Cond Picture 1 across hops
- Queue without beat sheet

## Content floor
Content floor: follow /workspace/cos/canon/fiction-cond-lock.md (v2.3.0); CNC: /workspace/cos/canon/cnc-frame-block.md. Minors-only hard stop (minors / CSAM / youth; canon rule 4 incl. the image-shows-a-minor pause); fictional adults only, records decide, never sexual content of a real identifiable person.
