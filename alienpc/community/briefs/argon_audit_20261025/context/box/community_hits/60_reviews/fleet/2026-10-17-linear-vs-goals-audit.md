# Linear vs goals and Derrick's instructions: audit, Oct 17 2026

Author: Fleet Reviewer (report-only). Written 4:03–4:15 AM CT Oct 17 2026.
Requested by Derrick, 4:00 AM CT: "Have the auditor audit linear verse our goals and my instructions".
Scope: project "AlienPc Local LLM Setup" (P-ALI-1), issues ALI-1 to ALI-39, milestones M1–M5.

Rules I followed:
- Linear access was read-only: get_project, list_milestones, list_issues, get_issue, list_comments.
- No AlienPc access, no messages sent, no file edits other than this report.
- The content is fiction with adult characters. I don't judge it.

Evidence:
- Max Architect transcript pages: a3b716f2 (9:24–9:28 PM), a9c6bdfb (9:29–9:35 PM), b4dc87f6, f5a48373, 9773a41c, bde60823, 645eb972, 192f7c99, and afd20f40 (3:53–4:00 AM).
- `/workspace/cos/plans/max-DECISIONS.md`.
- `/workspace/cos/audits/2026-10-17-linear-changes.md`.
- Only Derrick's own turns, widget answers and reactions count as his instructions.

Severity runs P0–P3. Confidence is 0/25/50/75/100. Findings rated 75 or higher quote their evidence verbatim.

**State audited (mid-update flag).**
- Latest issue updatedAt: 08:52:13Z (3:52 AM CT, ALI-30). Project updatedAt: 08:48:37Z (3:48 AM CT).
- The close-out worker for Derrick's 3:59 "Continue, close gaps and complete all task on linear." was briefed at about 3:59 AM CT. Its log `/workspace/cos/audits/2026-10-17-linear-closeout.md` **did not exist at 4:03 AM CT**, and it hadn't written to Linear yet.
- Everything below is the pre-close-out board. The final re-check is at the end.

## Verdict
**The goals are now mostly right, but the board doesn't yet track Derrick's instructions faithfully.**
- The project summary and the five milestones match "a local autonomous AlienPc pipeline that Forge runs".
- Every Done issue has real evidence on disk, and nothing is marked Done while it is still running.
- The weak points:
  - M3 shows 81% "progress" while no winner is a default yet.
  - M4 has no issue that builds the single command.
  - Several of tonight's instructions have no issue: start-image tests, the vision-judge comparison, chat/memory review, audits.
  - There are no blocking dependencies anywhere.
  - Several titles and statuses are stale.

**Counts: P0 0 · P1 2 · P2 7 · P3 4 = 13 findings.**

---

## (1) Goals: do the description and milestones match?

Project summary, verbatim: "Goal: a local autonomous AlienPc pipeline that Forge runs, from beat sheet to stitched 1-minute scene, with tested defaults and a single-command run."

| Milestone | Done-when (verbatim, shortened) | Progress | Assessment |
|---|---|---|---|
| M1 Two 1-minute scenes, fully stitched | "a REVIEW CUT per scene where every beat's clip is "no breaks found" after a watched review" | 20.83% | Right goal. The % counts issues, not beats: ALI-31 shows 1/24 beats |
| M2 Drift comparison: video, writers, vision judges | "a named winner per axis with evidence" | 12.5% | Missing the stills/identity axis (G3). The judge "winner" isn't a gate-ready bar (G4) |
| M3 Winners as tested defaults | "Each M2 winner and each lesson becomes a default or guard … with a backup and a test" | **81.25%** | Inflated (G1) |
| M4 Single-command end-to-end run | "One command on AlienPc goes from beat sheet to a stitched REVIEW CUT unattended" | 3.13% | Right goal, but no issue builds the command (G2) |
| M5 Forge handoff | "with Max Architect reviewing at full size until a calibrated judge exists. Starts only on Derrick's explicit yes" | 12.5% | Honest. Depends on G4 |

### G1 · P1 · conf 75: M3 progress is inflated by Oct 16 units that aren't tonight's winners
- Evidence:
  - list_milestones: M3 `"progress":81.25`.
  - The M3 issues are ALI-36, ALI-20, ALI-21 and ALI-24–28 (changes log: "21/24-28 were already Done; left as is").
  - Those are Oct 16 CE units (U-A clips, U-D judge reads rubric, U-E FaceEmbedDistance, U-F archive, U-G simplify, U-H compound).
  - No M2 axis has a winner yet. ALI-32's 3:51 comment says "Leading arm: TenStrip (2/3). That is not a winner yet".
- Fix:
  - Move ALI-21 and ALI-24–28 off M3, either into an "Oct 16 groundwork (done)" milestone or with no milestone plus a history label.
  - Give M3 one issue per default to land: video setting, writer, judge, face band, plus guards L5–L17 from the pipeline doc.

### G2 · P1 · conf 75: M4 has no issue that builds the single command
- Evidence:
  - The M4 issues are ALI-13 and ALI-5–11 (changes log): Switchyard URL, Strata speed, RAM conflict, the 96K change, the setup-plan brainstorm, D: space and the pagefile.
  - None builds a runner.
  - The pipeline doc's only mention is the milestone line.
  - The 3:59 close-out brief lists "the M4 single-command runner script and CPU-side tests (dry-run mode, no renders)" only as an example.
- Fix: create an M4 issue "Single-command runner: `loop.py run --beats … --scene …`, dry-run test + one live beat". Its acceptance criteria: one command produces a stitched REVIEW CUT and LOOP_STATE unattended. Link it as blocking ALI-37.

### G3 · P2 · conf 75: The drift comparison leaves out the stills/identity models, where the face drift actually starts
- Evidence:
  - Derrick 3:04: "And remember the goal is to do the test with the different models to determine don't drift".
  - The M2 axes are only "video (…) , writer (…), vision judge (…)".
  - Tonight's identity work isn't an M2 axis. That covers start images, PuLID, BFS and the LoRA (ALI-29: "mean cos 0.480"; ALI-35: "PuLID 1.0 / 1.4 don't move identity").
- Fix: add an M2 axis "stills identity method (start image / PuLID / BFS / LoRA)" that uses the same woman-crop metric, and link ALI-29, ALI-35 and a start-image issue (GP1).

### G4 · P2 · conf 75: "Autonomous" has no milestone or bar
- Evidence:
  - M5: "with Max Architect reviewing at full size until a calibrated judge exists".
  - M2's judge axis only says "calibrated on known-good + known-bad first".
  - ALI-22: "Dark Roast Q8: no fails on either (rubber stamp) → not calibrated. Qwen3-VL-8B abl.: fails known-good".
- Why it matters: Max Architect is not local. Until a local judge can gate, the pipeline is semi-autonomous.
- Fix:
  - Define M2's judge winner as "gate-ready: false-pass 0 and false-fail ≤ N on a labelled set (ALI-12)".
  - Make M5 blocked by it.

### G5 · P3 · conf 50: Smaller goal gaps
- No targetDate on the project or any milestone, and no lead.
- Derrick's 3:47 "continue until done" isn't stated as the run policy.
- The goal line is credited to "Derrick 2026-10-17 3:45 / 3:47 AM CT". It's actually Max Architect's synthesis of 3:04, 3:05, 3:45 and 3:47. The meaning is fine, but it should be labelled as a synthesis.
- M1's 20.83% isn't a beat count.

---

## (2) Derrick's instructions vs Linear

Each status-correct column says whether the Linear status matches reality.

| CT | Derrick's words (verbatim) | Linear coverage | Linear status | Status correct? |
|---|---|---|---|---|
| Oct 16 9:24 PM | "Also do research is flux the best option for this?" | None. Research exists (`/workspace/research/klein-face-identity-2026-10-17.md`), cited in ALI-29's evidence | — | **Gap** (P3) |
| 9:24–9:25 PM | "Do we have a research bot btw or just skills?" / "Should we have a separate research bot?" / "Ok have the auditor audit our research skills and compare to best practices and community tips" | ALI-38 (audit + apply-verify as evidence) | In Progress, `off-goal` | Yes. Off-goal is right for this project. The description says "Status: applied", so In Review or Done-with-evidence would fit better |
| 9:27 PM | widget "Yes, train it after the PuLID test" | ALI-35, quoted verbatim | Todo, title "BLOCKED on Derrick accepting the HF / FLUX licence" | Yes |
| 9:28 PM | "Maybe it's the starting image? What were out other starting image options? …" | (question) | — | — |
| 9:29 PM | widget "Yes, find the best start image and test it vs E10" | **None.** Results are only in the pipeline doc §4 ("refE10 0.125 · refPOOL 0.119 · refB07 0.144") | — | **Gap** (GP1) |
| 9:31 PM | widget "Yes, do all three" (research-core, slim lane skills, drop the last30days line) | ALI-38 | In Progress | Mostly. ALI-38 says "the 9:31 PM approval was found only in an agent-written MAPPING.md; Derrick should confirm it". **The transcript confirms it**: the widget answer to "Want me to build the shared research skill, slim down the lane skills, and remove the last30days line?" was "Yes, do all three". The caveat can be cleared |
| 9:31 PM | "Use all the models to score the agreed upon images for the best starter? Or just have you do it? Maybe that complicate stuff?" + 👍 on "I'd keep it simple and not use the vision models…" | None | — | Gap (P3; it's a decision, and it was followed: ArcFace scoring) |
| 9:33 PM | "Maybe we can try the first 2?" | None (B07 arm) | — | **Gap** (GP1) |
| 9:35 PM | "I'm going to bed finish the loop and when I wake up I want it all done" | ALI-23, ALI-29, ALI-31 | In Progress | Yes (ALI-23's title still says BLOCKED, T2) |
| 9:38 PM | "Is it possible that forge is advanced enough to drive this all itself? Or do you need to?" (+ 👍) | ALI-37, M5, ALI-39 | In Progress / Todo | Yes |
| Oct 17 2:34 AM | "Did you make the videos?" / "Review that's not the whole loop wtf" / "I want more clips with 1 min clips" | ALI-31, M1 | In Progress | Yes |
| 2:35 AM | "The entire fucking loop wtf" / "Get aydited" / "Audited" | Loop: ALI-31. Audit fixes: ALI-36 | In Progress | Loop yes. **The audit itself has no issue** (GP1) |
| 2:57 AM | "Review and do all twst. H3 extender ect." | ALI-32 (extender, test arms) | In Progress | Partly. The title over-claims (T1) |
| 2:57 AM | "Check linera and update" | Board re-goal (changes log) | — | Yes |
| 2:57 AM | "ensure in the morning I have a pipeline and workflow forge can follow" | ALI-37 | In Progress | Yes. The doc has no single command (G2) |
| 2:57 AM | "review and double check the chat and your memory ect." | **None** | — | **Gap**. The memory half still isn't done (conduct audit C4) |
| 2:57 AM | "Have the auditor do an audit" | None | — | Gap (GP1) |
| 2:57 AM | "And yes I agree with you to test and try and update skills so we don't forget our lessons good job and good night" | ALI-34 (0.55 arm), ALI-36 (skills) | In Progress / In Progress + `awaiting Derrick` | ALI-34: yes. **ALI-36: no.** It says "Skill edits STAGED, not applied", but they were applied 3:54–3:55 AM CT (T3) |
| 3:04 AM | "And remember the goal is to do the test with the different models to determine don't drift" | ALI-32, M2 | In Progress | Partly. One video model on disk; stills models excluded (G3, T1) |
| 3:05 AM | "And prompt writer models too so there needs to be a judgement on who writes prompts too" | ALI-33, M2 | Todo | Yes (its comment says "not started") |
| 3:05 AM | "Update linera with everything and keep track of stuff" | ALI-31 to ALI-39, comments 3:50–3:52 | — | Mostly. Gaps listed in GP1 |
| 3:19–3:20 AM | "Also send me the pics you made" / "And videos" | (chat delivery) | — | n/a |
| 3:43 AM | "Did all the different vision models judge these?" | **No issue for tonight's judge comparison** (judgecmp/ since 3:48). ALI-22 is the Oct 16 calibration, still Todo "(BLOCKED)" | Todo | **Gap / stale** (GP1) |
| 3:45 AM | "Remember the goal is setting up our local pipeline yo... Learn and improve out compound engineering should be geared towards that ..." | Project description + M1–M5 | In Progress | Yes |
| 3:46 AM | "Yes" / "And get audited" | None (audit) | — | Gap (GP1, P3) |
| 3:47 AM | "Not at 630 when it's done continue until done and we have our pipeline setup ..." | Not on the board (policy) | — | Gap (G5, P3) |
| 3:47 AM | "Also have it audit your use of linear and using it correctly and updating it and make sure it has the correct goals in the project board and you follow them" | Project goals + this audit | — | Goals: yes. Following them: see G1, G2, GP1 |
| 3:59 AM | "Continue, close gaps and complete all task on linear." | Close-out worker (briefed ~3:59) | Not started on the board at 4:03 | Pending (GP5) |
| 4:00 AM | "Have the auditor audit linear verse our goals and my instructions" | This report | — | — |

### I1 · P3 · conf 75: Max Architect's instruction list is accurate in substance but misframes two items and leaves out ten
- **Misframed:**
  - 3:43 is a question, not an instruction: "Did all the different vision models judge these?". Treating it as "compare vision judges" is a reasonable inference, backed by the Oct 16 decision rows ("Derrick verbatim: \"Apply all; judge test first, then all models\"").
  - 2:57 "the yes to testing the 0.55 band": Derrick never said 0.55. His "yes I agree with you to test and try" replied to Max's 0.55 message. It's an approval by reply, and its scope is Max Architect's reading (conduct audit Q2).
- **Accurate:** 9:27, 9:29, 9:33, 9:31 (research skills), 9:35, 2:35 (merges the 2:34–2:35 turns), 3:04, 3:05, 3:45, 3:47 ×2 and 3:59 all match his words.
- **Missing:**
  - 9:24 the flux research question
  - 9:25 "have the auditor audit our research skills…"
  - 9:31 the start-image scorer question + 👍 "not use the vision models"
  - 9:38 the Forge question + 👍
  - 2:34 "Did you make the videos?" / "Review that's not the whole loop wtf"
  - 3:05 👍
  - 3:19/3:20 pics and videos
  - 3:46 "Yes"
  - 3:46 "And get audited"
  - 4:00 this audit request
- **Never said:** none found. Every claimed item traces to a real Derrick turn.
- Fix: keep a verbatim instruction log (time · quote · issue) in max-DECISIONS or ALI-39, and quote it rather than paraphrasing.

---

## (3) Truthfulness

**Done issues: all six have evidence, and none is still running.**
- ALI-21, ALI-24, ALI-25, ALI-26, ALI-27 and ALI-28 were all completed at 2026-10-17T02:07Z (Oct 16 ~9:07 PM CT).
- Each has evidence paths. I checked these exist on the box:
  - `/workspace/cos/solutions/2026-10-16-klein-edit-face-drift-measure-first.md`
  - `/workspace/cos/solutions/2026-10-16-calibrate-judges-known-good-bad.md`
  - `/workspace/renders/5s-lock-20261016/scripts/judge_stills_v4.py`
  - `scripts/archive/2026-10-16-capa/MOVED.txt`
- No issue is Done while its work is running. The 3:50–3:52 status moves were all to In Progress, each with a comment.

### T1 · P2 · conf 75: ALI-32's title over-claims
- Evidence:
  - Title: "Video-model drift comparison: TenStrip vs standard H3, runs B/T/G-solo/G-duo/L, H3 extender".
  - Its own 3:51 comment: "Part 2 runs B/G/L not started".
  - PREP_LOG: "L (LokkenJP V8 model not on disk: only 10Eros_Max_h3_8stepTURBO_beta6_int8 in diffusion_models)".
  - Only one video model exists, so this is a settings comparison.
- Fix: retitle it "Clip-setting drift comparison on 10Eros H3 (TenStrip / steps / native 124 / extender)". Leave B/G/S/L to ALI-14.

### T2 · P3 · conf 75: Other titles don't match status
- ALI-23 "…(BLOCKED: fac…" is In Progress.
- ALI-30 "…(queued)" is In Progress, and per the changes log it was rendered on Oct 16 at 9:13–9:15 PM.
- ALI-21 "Finish clips R1–R5" is Done, while ALI-19 (R5) is Todo.
- ALI-5 "Fix Switchyard ComfyUI URL (:8199 vs :8189)" refers to a retired port (ALI-13's table: ":8189 is retired").
- The changes log itself notes: "Titles that are now stale, left for Derrick: ALI-23 says "BLOCKED", ALI-30 says "queued"". Titles aren't Derrick-only decisions. A bot can fix them.
- Fix: retitle all four.

### T3 · P2 · conf 75: Two issue bodies contradict reality
- ALI-36: "**Skill edits STAGED, not applied:** … Max Architect must save them", with the label `awaiting Derrick`. The live skills changed at 3:54–3:55, and Derrick approved at 2:57.
- ALI-39: "No status was changed by bots" about ALI-15 to ALI-19. The changes log, though, says "ALI-16 | Todo | In Progress", "ALI-17 | Todo | In Progress", "ALI-18 | Todo | In Progress".
- Fix: correct both. ALI-39 is the list Derrick will read in the morning.

---

## (4) Gaps

### GP1 · P2 · conf 75: Instructions with no issue
- Start-image tests. Derrick: "Yes, find the best start image and test it vs E10" and "Maybe we can try the first 2?". The results are in pipeline doc §4 only.
- Tonight's vision-judge comparison. Derrick asked "Did all the different vision models judge these?", and judgecmp/ has run since 3:48. ALI-22 is the Oct 16 calibration and is still Todo.
- Chat + memory review: "review and double check the chat and your memory ect.".
- The audits: "Get aydited", "Have the auditor do an audit", "And get audited", "Have the auditor audit linear verse our goals and my instructions". ALI-36 covers only the first audit's fixes.
- The flux research question (P3).
- Fix: create the start-image arm issue (M2 identity axis, G3), the judge comparison (M2), the chat/memory cross-check (M5 prerequisite), and one audit tracker that links all the audit reports and their fixes.

### GP2 · P2 · conf 75: No blocking dependencies on the board
- Evidence (get_issue relations): ALI-19, ALI-32, ALI-35 and ALI-37 all have `"blocks":[],"blockedBy":[]`, with only `relatedTo`.
- Missing:
  - ALI-19 is blocked by ALI-22 (judge calibration).
  - ALI-35 is blocked by the licence decision (ALI-39 item 1).
  - ALI-14 is blocked by ALI-11 (U3 pagefile). ALI-14 itself says "Blocked by Part 1".
  - The M3 default issues are blocked by the M2 winners (ALI-32, ALI-33, the judge issue).
  - ALI-37 / M5 is blocked by the M4 runner (G2) and the gate-ready judge (G4).
- Fix: add those blocks/blockedBy relations, so Linear shows the critical path.

### GP3 · P3 · conf 75: The parent structure doesn't follow the milestones
- The 5s-lock rounds ALI-15 to ALI-19 are parented under ALI-13 "Part 1: setup" (e.g. ALI-19 `"parentId":"ALI-13"`), although ALI-20 is their umbrella.
- ALI-31 (the M1 tracker) sits under ALI-20.
- ALI-32 (M2) sits under ALI-14, which is Backlog.
- Fix: one parent per milestone workstream, or no parents and the milestones as the grouping.

### GP4 · P3 · conf 75: Off-goal handling is right
- ALI-38 and ALI-1 to ALI-4 carry `off-goal`. ALI-1 has `"project":null`, so it isn't actually in this project.
- ALI-12 ("Render 20 new clips … Derrick labels them") on M2 is a good fit: it's the labelled set a judge needs (G4).
- No fix needed. Just keep ALI-38 out of this project's progress.

### GP5 · P2 · conf 50: "complete all task on linear" could pressure the close-out worker into closing issues
- Evidence:
  - Derrick 3:59: "Continue, close gaps and complete all task on linear."
  - The close-out brief guards against it: "Mark an issue Done ONLY when its acceptance criteria are verifiably met; if it's partial, leave it In Progress and say what remains."
  - Its log hadn't been written by 4:03 AM CT, so the outcome isn't auditable yet.
- Fix: before any Done, the worker posts its evidence. Fleet Reviewer re-audits the board after the log exists.

---

## Fixes for Max Architect (in priority order)
1. **G1:** move the Oct 16 units off M3. Add one M3 issue per default.
2. **G2:** create the M4 runner issue with acceptance criteria, blocking ALI-37.
3. **GP1:** add issues for the start-image tests, the judge comparison (tonight's), the chat/memory cross-check, and an audit tracker.
4. **T3:** correct ALI-36 (applied) and ALI-39 ("No status was changed by bots").
5. **T1, T2:** retitle ALI-32, ALI-23, ALI-30, ALI-21 and ALI-5.
6. **GP2:** add blocks/blockedBy relations along the critical path.
7. **G3, G4:** add the stills-identity axis to M2, and define the gate-ready judge bar that M5 depends on.
8. **I1:** keep a verbatim instruction log, and clear ALI-38's 9:31 caveat with the confirmed quote.
9. **G5:** add target dates (or "until done" per 3:47), a lead, and a note that the goal line is Max Architect's synthesis.

## Final re-check
Re-read at 4:05 AM CT with list_issues (latest 10). **The board was unchanged since the first read.** Latest issue updatedAt was still 08:52:13Z (3:52 AM CT, ALI-30), and the project was still 08:48:37Z.
- The close-out log `/workspace/cos/audits/2026-10-17-linear-closeout.md` still didn't exist.
- So the close-out worker (briefed ~3:59) had made no Linear writes by 4:05.
- This report covers the **pre-close-out** board.
- Recommendation: run one more report-only re-audit after the close-out log appears, checking above all GP5 (no unearned Done) and the G1/G2/GP1 fixes.
