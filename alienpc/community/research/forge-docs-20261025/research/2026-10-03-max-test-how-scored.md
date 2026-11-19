# Max tests — how they were scored (2026-10-03)

Not a standing fact. No skill or Job was edited. Numbers below are copied from the cited files. None were recomputed.

## TLDR

The six still axes (Identity, Face, Hands/HF, Contact/seam, Wardrobe, OverallQuality), each at or above 0.95, were not filled on any Max test. That gate was not used, so it was not used properly.

What ranked or labeled Max instead depends on the pack. The 2026-10-02 production speed board used wall time plus one relative word, Integrity about equal to BASE or FAIL, written as a Bot head-to-head. It did not fill the five axes the plan named, and it did not take a mean of three seeds.

The 20-vs-25 native watch used eight bot decimals. Overall was the worst axis. One axis under 0.95 failed the clip. All 18 failed. That is not the six still names.

Older Max used other rulers: InsightFace cosine mean, one pixel-correlation Integrity number (later voided), motion-amp words, or TECH only. Beach clips used Face, Camera, Hands, and Overall as decimals. Q3, Q5, upscale Integrity, static-shot, and beach 20-step have no score row.

The 2026-10-02 production KEEP line is Derrick's GO on argv (NODDV, no fp8, ck-attn ON, scheduler beta, 25 steps). It is not a six-axis quality crown.

## 1. Was the six-axis 0.95 gate used?

**No.**

Search of the Max packs and the 2026-10-02 / 2026-10-03 score notes found no row with columns Identity, Face, Hands/HF, Contact/seam, Wardrobe, OverallQuality. The strings OverallQuality, Hands/HF, and Contact/seam do not appear in those packs.

The 0.95 cutoff does show up, pasted onto other lists:

- Steps watch: Identity, Face, Anatomy, Coverage, Camera, Motion, Hands, Overall. One under 0.95 is FAIL. File `/workspace/cos/status/2026-10-02-steps20-vs-25-native-scores.md` lines 7-9.
- Face loop: PRIMARY Max Face/ID at or above 0.95 on an InsightFace cosine, not six human axes. File `/workspace/MAX_FACE_095_LOOP_2026-10-01/SCOREBOARD.md` line 7.
- Beach brainstorm: pass bar stays at or above 0.95 on each scored axis, for Face, Camera, Hands. File `/workspace/cos/status/2026-10-03-ce-brainstorm-beach-quality-speed.md` line 39.
- Speed-matrix plan: thumbs at or above BASE on Face/ID, Hands, Oral/contact, Wardrobe, Motion amp. Those columns were not filled on the result board.

None of those is the 2026-09-27 still sheet applied to a Max clip.

## 2. How each Max run was actually scored

One quoted row per distinct method. Six axes means the still six. Integrity mean means the LTX composite averaged across three seeds. That mean was not used on these Max boards.

### A. Speed matrix — relative Bot word, not a number

File: `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md`

Columns: Cell, Wall, delta vs BASE, TECH, Integrity, Note.

Who wrote it: the board calls Integrity a relative Bot H2H (line 10). No per-axis decimals. No scorer name beyond that.

Six axes: no. Integrity mean of seeds: no. Overall = worst axis: no. PASS/FAIL: mixed with the word about-equal-to-BASE. OPT-STEPS-20 is FAIL under-denoise. OPT-SCH-WARM-BETA is about-equal BASE PASS and the Note says KEEP.

Quoted row (lines 19-23). Source text uses the sign for about-equal and marks KEEP in bold:

```
| Cell | Wall | Δ vs BASE | TECH | Integrity | Note |
| OPT-SCH-WARM-BETA | 125.5s | warm SoT | OK | ≈BASE PASS | **KEEP** |
```
Source lines 19-23. The header row in the file is `| Cell | Wall | Δ vs BASE | TECH | Integrity | Note |`.

The header (lines 5-9) says Derrick GO 2026-10-02 about 11:20 CT for argv: NODDV, no fp8, use-ck-attention ON, scheduler beta, 25 steps, REF2VA match, 864x480, 124f. That KEEP is the stack GO. The same file does not show six axes clearing 0.95.

The plan this board cites asked for a different card. `/workspace/cos/status/ce-plan-max-speed-quality-matrix-2026-10-02.md` line 82: PASS only if TECH is OK and human thumbs are at or above baseline on Face/ID, Hands, Oral/contact, Wardrobe, and Motion amp. The result table does not have those columns.

### B. Steps 20 vs 25 — eight bot decimals, overall = worst

File: `/workspace/cos/status/2026-10-02-steps20-vs-25-native-scores.md`

Who wrote it: the file says this executor watched frames directly (8 frames plus native frame 100). No MAE, no bookend correlation, no auto score (line 5).

Rule in the file (line 7): Hostile Integrity. Overall is the worst axis, not an average. One axis under 0.95 is FAIL. Axes: Identity, Face, Anatomy, Coverage, Camera, Motion, Hands, Overall.

Six axes: no (eight names, and not the still six). Integrity mean: no. Overall = worst: yes, stated. PASS/FAIL: all 18 FAIL (line 49). No KEEP.

Quoted row (lines 15-17), POOL_TERRACE_ATTACH:

```
| seed | 25 wall | 20 wall | 25 overall | 20 overall | fail |
| 25102401 | 251.4s | 100.6s | 0.40 | 0.40 | Camera pushes in off the wide standing rear; motion is a lean, not a readable thrust |
```

The file does not print the other seven decimals for that seed, only overall and the fail sentence. P157 was not rescored here; the file says prior both arms FAIL, overall about 0.25-0.30 (line 3).

### C. P157 native — seven decimals, overall equals the low axis, rule not stated in-file

File: `/workspace/MAX_STEPS20_VS_25_2026-10-02/SCORE_NATIVE_P157.md`

Columns: seed, arm, identity, face, anatomy, coverage, contact/motion, hands, overall.

Who wrote it: not named. Line 3 says Integrity is not crowned.

Six axes: no. Integrity mean: no. The row overall equals the lowest axis on every seed (0.30, 0.25, 0.30), but this file does not say worst axis. PASS/FAIL: Both arms FAIL. No KEEP (line 27). A frame-delta mean is logged as a motion check, not the crown (line 25).

Quoted row (lines 16-18):

```
| seed | arm | identity | face | anatomy | coverage | contact/motion | hands | overall |
| 25102401 | 25 beta | 0.70 | 0.55 | 0.40 | 0.60 | 0.30 | 0.30 | 0.30 |
```

### D. S0, IMP1-IMP3, early ck-attn — TECH only

Files:

- `/workspace/MAX_REF_ORC_BJ_S0_2026-10-02/SCOREBOARD.md` (S0 NOFP8, elapsed 350.8s)
- `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/SCOREBOARD_IMP1.md` (340.8s)
- same folder SCOREBOARD_IMP2.md (340.7s) and SCOREBOARD_IMP3.md
- `/workspace/MAX_REF_ORC_BJ_S0_2026-10-02/SCOREBOARD_AB_CKATTN.md` (285.5s vs 350.8s, 18.6%)

Columns are a field table: label TECH, KEEP no, TECH ok YES, thumbs n00 / n_mid / n_end only. CKATTN notes say no integrity scripts.

Six axes: no. Integrity mean: no. Overall = worst: no. PASS/FAIL: TECH yes/no only. The status note `/workspace/cos/status/2026-10-02-max-speed-ab-ckattn.md` line 40 says KEEP (Integrity) is no, and line 57 says do not treat the wall win as Integrity KEEP.

Quoted row (IMP1, lines 15-18):

```
| elapsed | 340.8s |
| label | TECH |
| KEEP | no |
| TECH ok | YES |
```

### E. Face 0.95 loop — InsightFace cosine mean, not the still six

File: `/workspace/MAX_FACE_095_LOOP_2026-10-01/SCOREBOARD.md`

Who wrote the numbers: script scripts/_score_if_woman.py, buffalo_l, cosine vs the Cond woman (lines 21-22). Vision_est is a separate column, called hostile, not named to a person.

Six axes: no. The mean here is IF_mean (cosine across samples of one clip), not the LTX Integrity mean across three seeds. Overall = worst: no. Bar stated as Face/ID at or above 0.95. No row reaches 0.95.

Quoted row (lines 9 and 16):

```
| Cell | Mode | Axis | Steps | Res | Len | Gen | IF_mean | IF_min | Vision_est | Notes |
| C5 | FL2VA | short+strong+s25 | 25 | 864x480 | 73 | 130s | 0.568 | 0.519 | ~0.75 | best P157 IF |
```

POOL_C2 is the highest filled IF_mean on that board: 0.801, still marked far under 0.95 (line 18).

### F. Max vs LTX H2H — one pixel-corr Integrity, later voided

File: `/workspace/MAX_VS_LTX_H2H_2026-10-01/SCOREBOARD.md`

JSON: `/workspace/MAX_VS_LTX_H2H_2026-10-01/integrity_reviews/MAX_C5_SCORE_INTEGRITY.json`

Who wrote it: the JSON field method is "LTX Recipe-B / hc_flf_135 Integrity (pixel-corr + face_crop bookends); NOT InsightFace". scored_ct is 2026-10-01 16:59:47 CT. I, Q, and M are each PASS. Integrity is one number for one clip, not a mean of three seeds.

Six axes: no. The JSON caveat says hostile vision on Face/ID, body, hands, wardrobe, contact, and motion is still required for PASS at or above 0.95. That watch is not the number in the Integrity field.

Quoted row (scoreboard lines 16-18):

```
| Lane | Seed | Res | Len | Gen | Integrity | I/Q/M | face_mid |
| MAX C5 (VOID crown) | 25100157 | 864x480 | 73 | ~130s | 0.9787 | P/P/P | 0.915 |
```

JSON metrics that feed 0.9787 include n00_vs_n_end 0.9796. The same scoreboard line 2 voids the crown: motion amp FAIL equals Integrity FAIL, because the bookends are a near-freeze. Derrick eye FAIL. NOT KEEP.

### G. Vision board — Motion, Face, Min; PASS only if all at or above 0.95

File: `/workspace/MAX_VISION_RESCORE_2026-10-01/VISION_INTEGRITY_BOARD.md`

Header: LTX hostile axes. PASS only if all at or above 0.95. Near-still motion at or under 0.4 is FAIL. Columns: Clip, Motion, Face, Min, PASS. Min is the low of the two filled numbers. Ranges, not one seed full axis list. Six still axes: no. Integrity mean: no. The companion SCOREBOARD.md in that folder is READY_FOR_VISION with pending review, not these numbers.

Quoted row (lines 4-8):

```
| Clip | Motion | Face | Min | PASS |
| C1-C5 P157 short/bookend | 0.25-0.35 | 0.6-0.8 | 0.25-0.35 | NO |
```

Line 15: auto Integrity 0.98 was bookend correlation, not quality.

### H. M1 / M2 / M3 — motion amp, bookend number ignored

M1 `/workspace/MAX_M1_STRONG_THRUST_2026-10-01/SCOREBOARD.md`: auto n00_vs_n_end=0.9774 voided. Video watch: motion amp PASS, amp about 0.8-0.9. Wardrobe-on called the real gap. No six axes. No overall column.

M2 `/workspace/MAX_M2_I2VA_STRONG_THRUST_2026-10-01/SCOREBOARD.md`: No bookend auto score. Visual watch only. KEEP is Derrick GO. NO_DATA for a numeric or axis row.

M3 `/workspace/MAX_M3_CONTACT_NUDIFY_2026-10-01/SCOREBOARD.md`:

```
| TECH | PASS |
| Visual motion amp | 0.62 (mid thrust energy present) |
| Bookend Integrity auto | NOT USED (n00 vs n_end 0.974 ignored) |
| Bare hip-seam / lower unlock | FAIL inherited |
| Face/ID collapse | NO |
| KEEP | NO |
```

Six axes: no. Integrity mean: no. Overall = worst: not used. PASS/FAIL is per gate, not one overall.

### I. Beach — Face, Camera, Hands, Overall (not the still six)

Filled table: `/workspace/cos/status/2026-10-03-ce-brainstorm-beach-quality-speed.md` lines 15-19, about 10:11 CT. The file does not name the watcher.

Quoted row:

```
| 25100321 C1 | keyframe completion, 480x864, ref match, 362f, beta, 25. Wall 597.3s | Face 0.70, Camera 0.30 zoom out, Hands 0.40. Overall 0.30. |
```

On that row and on 25100314 (Face 0.30, Camera 0.30, Hands 0.30, Overall 0.30), Overall equals the lowest number written. The file also says one miss fails the cell and the pass bar is at or above 0.95 (line 39). Six still axes: no. Integrity mean: no.

Same file, C2 seed 25100322: Finished. Not scored. Dance seed 25100324: Running or queued.

Later audit `/workspace/cos/audits/2026-10-03-beach-speed-audit.md` writes scores those lines did not have:

- 25100324: dance about 0.70, face 0.70, camera 0.30, hands 0.60, overall 0.30 (line 47).
- C2: overall 0.35, face 0.45 vs match face 0.70 (line 49). Other C2 axes are not listed, so worst-axis cannot be checked for 0.35 from that sentence.
- Beach 20-step seed 25100326: no beach 20-step wall and no beach 20-step score (line 21). NO_DATA.

Q labels in `/workspace/cos/status/ce-plan-beach-quality-speed-2026-10-03.md` are cells, not axes: Q1 is the dance prompt (called 25100324), Q2 is ref_image_size max, Q3 is canvas 768x1344. Q3 is not a scored run. NO_DATA for a Q3 score.

### J. 5-second hands (the other Q1) — not scored

`/workspace/cos/status/ce-plan-5s-quality-speed-2026-10-03.md` lines 3 and 114: seeds 25100332, 25100333, and 25100334 are VOID (neon still, not the beach photo). Not scored. No Q5 Max quality score file was found. WAN GGUF Q5 notes are a different model, not a Max axis score. NO_DATA for Q5.

### K. Upscale and static-shot — boards exist, scores do not

`/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_UPSCALE_H2H.md` line 9: Lanczos rows READY, Bot Integrity pending. AI rows BLOCKED. Lanczos score table in SCOREBOARD_LANCZOS_UPSCALE.md is also pending. NO_DATA.

`/workspace/cos/status/ce-plan-max-staticshot-2026-10-03.md` names a smoke. No score row for MAX_STATICSHOT_CYCLE was found. NO_DATA.

`/workspace/MAX_VS_LTX_SMOKE_2026-10-01/SCOREBOARD.md` and `/workspace/MAX_SMOKE_FL2VA_FACE_2026-10-01/SCOREBOARD.md` are TECH_PASS plus a thumb glance. No axis decimals. Derrick eye was still open on the FL2VA face smoke.

## Used properly?

**No.** Reason: the six-axis still gate was never filled on a Max clip, so it could not have been applied. The boards that do use 0.95 use other axis lists, or one auto Integrity number, or a relative word. The production KEEP is an argv GO, not those six checks.

## Contradictions

- The speed plan required five named axes at or above baseline. The result board collapsed that to Integrity about-equal-to-BASE PASS or FAIL under-denoise.
- Early ck-attn (09:44-09:49 CT) says Integrity KEEP is no. The matrix later says ck ON Integrity about-equal-to-BASE PASS and the stack KEEP is Derrick GO about 11:20 CT. Wall and quality are not the same claim.
- C5 auto score is Integrity 0.9787 and I/Q/M all PASS. The same file voids it as motion FAIL. The vision board scores that ladder Motion 0.25-0.35 and PASS NO.
- Face-loop IF_mean 0.568 and Vision_est about 0.75 are different scales. Neither is the still six, and neither clears 0.95.
- Beach brainstorm (about 10:11 CT) says C2 is not scored and 25100324 is still running. The beach speed audit later prints decimals for both. Those two files disagree on whether a score existed.
- Live review `/workspace/cos/audits/2026-10-03-live-scored-research-review.md` line 19 says the director skill quotes seed 25102401 as Integrity 0.30. That 0.30 is the steps-watch overall on the oral still, not the matrix cell that says about-equal-to-BASE PASS for the beta stack.
- P157 overall matches the lowest axis, but only the other steps file states the worst-axis rule. The matrix does not use that rule.

## Unknowns

- No saved per-axis thumbs for the speed-matrix Bot H2H. Who watched, and what they saw on hands or contact, is not in the table.
- P157 decimals have no named watcher in SCORE_NATIVE_P157.md.
- Beach C2 full axis list is not in the audit sentence (only overall 0.35 and face 0.45).
- Beach 20-step 25100326, Q3 canvas, Q5, Lanczos Integrity, AI upscale, and the static-shot smoke: NO_DATA.
- This note did not re-watch any clip.

## Sources

- `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_MATRIX.md`
- `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_UPSCALE_H2H.md`
- `/workspace/MAX_REF_ORC_BJ_SPEED_MATRIX_2026-10-02/SCOREBOARD_LANCZOS_UPSCALE.md`
- `/workspace/cos/status/ce-plan-max-speed-quality-matrix-2026-10-02.md`
- `/workspace/cos/status/2026-10-02-max-speed-matrix-exec.md`
- `/workspace/cos/status/2026-10-02-max-speed-ab-ckattn.md`
- `/workspace/cos/status/2026-10-02-steps20-vs-25-native-scores.md`
- `/workspace/MAX_STEPS20_VS_25_2026-10-02/SCORE_NATIVE_P157.md`
- `/workspace/MAX_REF_ORC_BJ_S0_2026-10-02/SCOREBOARD.md`
- `/workspace/MAX_REF_ORC_BJ_S0_2026-10-02/SCOREBOARD_AB_CKATTN.md`
- `/workspace/cos/status/max-ref-orc-bj-prompt-pack-2026-10-02/SCOREBOARD_IMP1.md` (IMP2 and IMP3 same pattern)
- `/workspace/MAX_FACE_095_LOOP_2026-10-01/SCOREBOARD.md`
- `/workspace/MAX_VS_LTX_H2H_2026-10-01/SCOREBOARD.md`
- `/workspace/MAX_VS_LTX_H2H_2026-10-01/integrity_reviews/MAX_C5_SCORE_INTEGRITY.json`
- `/workspace/MAX_VISION_RESCORE_2026-10-01/VISION_INTEGRITY_BOARD.md`
- `/workspace/MAX_M1_STRONG_THRUST_2026-10-01/SCOREBOARD.md`
- `/workspace/MAX_M2_I2VA_STRONG_THRUST_2026-10-01/SCOREBOARD.md`
- `/workspace/MAX_M3_CONTACT_NUDIFY_2026-10-01/SCOREBOARD.md`
- `/workspace/cos/status/2026-10-03-ce-brainstorm-beach-quality-speed.md`
- `/workspace/cos/audits/2026-10-03-beach-speed-audit.md`
- `/workspace/cos/status/ce-plan-beach-quality-speed-2026-10-03.md`
- `/workspace/cos/status/ce-plan-5s-quality-speed-2026-10-03.md`
- `/workspace/cos/audits/2026-10-03-live-scored-research-review.md`
- Prior notes, not re-litigated: `/workspace/cos/research/2026-10-03-six-axis-how-used.md` and `/workspace/cos/research/2026-10-03-score-criteria-drift-from-ltx.md`
