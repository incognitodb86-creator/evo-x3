---
title: CAPA apply audit (Max Architect, applied ~7:55–8:00 PM CT Oct 16)
written_ct: 2026-10-16 ~8:15 PM CT
reviewer: Fleet Reviewer executor (report-only; nothing edited)
requested_by: Derrick 7:58 PM CT ("Auditor your skill fixed"), relayed by Max Architect
---

# CAPA apply audit, 2026-10-16

## Verdict
**Applied faithfully, with no scope creep in the files. The memory pass is incomplete, and two small contradictions remain.**
- Every applied B/C file change matches the CAPA text.
- Nothing destructive happened: everything was archived or backed up.
- The deferred AlienPc items are open, as expected.
- Gaps: the memory pass (B13 / C11) is incomplete and wasn't reported as deferred. The stills skill now depends on a single test-run folder for its rubric.

## Approval check
- **Transcript** (page 63597614, positions 9324–9366):
  - Widget "Apply the CAPA?" offered: "Apply all, test the judges first, then all models" / "Apply all, but keep all models judging now" / "Rule fixes only, no trims yet".
  - Derrick, **7:54 PM CT**: "Apply all; judge test first, then all models" (the first option, verbatim).
- **What "all" referred to:**
  - The message right before the widget linked `/workspace/cos/audits/2026-10-16-max-capa-combined.md`.
  - It summarized "Rule changes I'd make (15)" (B1–B15) and "Trims, all archived rather than deleted" (C rows).
  - It flagged one conflict: "The trims say to use just two judges until the judge test passes, but you asked for all the models. My pick is to run the test first and then use all the models."
  - So "all" = B1–B15 + C1–C12 as shown. "Judge test first, then all models" resolves C5 (calibrate first, then every vision model judges).
- **DECISIONS logging:** the 7:54 row records it verbatim with that scope. ✅
- **Display caveat:** Derrick saw a summary plus a link, not each row. The two AlienPc deletes-by-archive (C1/C2/C6/C7) and the C10 folder move were included under "Trims, all archived rather than deleted". That matches what was done.

## Findings (severity-ranked)

### P2: Memory pass incomplete, and not reported as deferred (conf 80)
- Done, per the transcript:
  - B9: forgot the 3:01 fact and wrote a narrowed one.
  - Forgot the Oct 15 "Dark Roast … only vision judge" fact.
  - Wrote the B13 pointer fact.
  - Wrote the B8 no-secrets fact (after RecallMemory, so no duplicate was found).
- Not done:
  - **B13's 6:32 fact fix.** That fact ("…give the same checklist to the Dark Roast vision judge") was never forgotten or rewritten. At about 6:50 Max said "The outdated Dark Roast fact gets overridden by the newer memory, so I'll leave it as is." It still contradicts the new video-ops banner "Judges = every vision model in the test".
  - **C11:** no merge of duplicate judge/review/lesson facts, no drop of stale Switchyard/:8189 facts, and no fix to the 3:36 attribution.
- The 7:56 message to Derrick lists only AlienPc items as pending ("The rest waits… AlienPc script cleanup, the judge script review, the judge test and the face-check install"). The C11 gap was left out.

### P2: The narrowed 3:01 fact kept the license wording (conf 75)
- B9 text: "A yes from Derrick covers only the thing asked. New scope or any "approved" label needs his words…"
- Written fact: "his "yes" or OK means **act right away with no extra confirmation rounds**, but it covers only the thing he was asked about; …"
- The scope limit is there, but the "act right away" phrase that drove F7 was kept. It isn't the B9 text verbatim.

### P2: The stills skill's rubric pointer depends on one test-run folder (conf 70)
- The stills skill L40 now says: "The one rubric … lives in `/workspace/renders/5s-lock-20261016/judge/STRICT_STILL_REVIEW.md`". The same path is in the pointer memory fact and the plan.
- A durable skill shouldn't depend on a single run's output folder; it breaks if that test folder is archived.
- skill-authoring also says to keep run-specific details out of the recipe.
- Smallest fix: move the rubric to `alienpc-stills-pose-edit-prompting/references/strict-still-review.md` and point the run folder at it, with Derrick's OK.

### P3: Skill files were hand-edited instead of written through UpdateSkill (conf 70)
- The edits used `cp` and python on the SKILL.md files.
- skill-authoring says to manage user skills with UpdateSkill (write/delete). The `.bak` files are also left in the skill folders.
- No frontmatter keys were dropped: all 4 changed skills keep `name` and `description` unchanged.
- The edits don't break anything, but they bypass the sanctioned path.

### P3: Small nuance lost in the director's triage (conf 60)
- The hardcore director's "Spot-check scrapes; **loosen if he would have kept one**" was replaced by a link to video-ops package D.
- Video-ops L40 keeps the spot-check, but not "loosen if he would have kept one".
- Low impact, but it's a calibration-toward-Derrick rule. Consider keeping one clause.

### P3: Broken reference links (pre-existing, not introduced) (conf 90)
- The hardcore director cites `references/{experimental-do-not-default,max-8189-production-keep,max-first-product-order,video-integrity-motion-amp}.md`. The matrix cell cites `experimental-do-not-default.md`. The lease skill cites `local-exec-lease-full.md`.
- Those files exist only under `alienpc-local-video-ops/references/`.
- The `.bak-capa` copies have the same link count, so the CAPA didn't cause this.
- Fix: prefix them with `alienpc-local-video-ops/`.

### P3: Rule budget is mostly held; one addition is new (info)
- Added sections:
  - stills "## Judge harness" (B2, 6 bullets);
  - "## LoRA-aware prompting" (B14, 1 bullet);
  - DECISIONS: 2 CORRECTION rows + 2 NOTE rows.
- Tightened existing lines rather than adding: video-ops L45 (B1), L50 (B15), stills L20 (B4), the DECISIONS header (B12).
- Removed: the restated banners in 2 skills and the director's triage/KEEP restatements (C9).
- Net skill lines: 553 → 481. Not an overcorrection.

## Row-by-row check
| Row | File | Status |
|---|---|---|
| B1 | video-ops L45 | ✅ exact text appended |
| B2 | stills "Judge harness" | ✅ §6A text plus the 7:54 quote plus the community line; no "## Size" block (correct) |
| B3 | STRICT_STILL_REVIEW | ✅ checks 8 and 9, no-PASS output, full-size line; old PASS line removed |
| B4 | stills L20 | ✅ appended |
| B5 | judge v4 review | deferred (expected) |
| B6 | plan Amendments | ✅ all listed items present, including "R5 judge scores count only after calibration" |
| B7 / B10 / B12 | DECISIONS | ✅ header replaced; CORRECTION/NOTE rows; old rows kept (append-only) |
| B8 | memory | ✅ fact added (the key rotation is Derrick's) |
| B9 | memory | ⚠ narrowed but not verbatim (P2 above) |
| B11 | judge v4 → one rubric | deferred (expected) |
| B13 | memory | ⚠ pointer added; the 6:32 fact was not fixed |
| B14 | stills LoRA section | ✅ |
| B15 | video-ops L50 | ✅ |
| C3 | box judge v1/v3/.bak | ✅ moved to `/workspace/cos/archive/2026-10-16-capa/box-scripts/` (the AlienPc copies are deferred) |
| C5 | DECISIONS NOTE + video-ops banner + stills harness | ✅ calibrate first, then all models |
| C8 | rubric header = the one rubric | ✅ header done; judge v4 still embeds its own copy until B11 |
| C9 | director/matrix banners and director triage | ✅ links resolve |
| C10 | ltx leftover folder | ✅ moved to `archive/2026-10-16-capa/box-skills/`; gone from workflows |
| C1 / C2 / C4 / C6 / C7 | AlienPc moves, FaceAnalysis | deferred (expected) |
| C11 | memory merge | ❌ not done and not reported (P2 above) |
| Learnings | 4 files in `/workspace/cos/solutions/` | ✅ present, frontmatter has applies_when/retire_when |

## Contradiction sweep
- **PASS wording:** no "overall PASS" or "PASS/FAIL" left in the alienpc skills or the rubric. The rubric uses FAIL / "no breaks found". Consistent with video-ops L43. ✅ (PREP_LOG history still says "me PASS 781…"; that's a log, so leave it.)
- **Size:** 768x1344 in the stills skill L6/L20, the video-ops banner, the movie director L11 and B1. No 768x1120/1376 claims remain. ✅
- **Judge list:** the video-ops banner, stills harness, DECISIONS and plan all say calibrate first, then every vision model. **Exception: the 6:32 memory fact (Dark Roast only).** ⚠ The movie director L11 "prompts by vl_judge Dark Roast" is the director role, not judging. ✅
- **CAPA + HOLD:** video-ops L45, the solutions file and the 7:41 DECISIONS row agree. ✅

## Do NOT cut: all intact
Minors guard (drv.py untouched), backups (`.bak-capa-*` beside every changed file), DECISIONS (append-only, corrections added), Derrick-only KEEP (stills L40, video-ops L43), reference identity check (harness "Never remove the reference"), multi-judge only after calibration, ffmpeg scene scan, batching / one GPU job at a time, the lease, capped re-rolls, strict rubric content (merged and expanded).

## Still open (expected)
AlienPc script retirements (C1/C2/C6/C7), judge v4 code review plus the move to one rubric (B5/B11), calibration run (B2), FaceAnalysis install (C4), key rotation (Derrick).
