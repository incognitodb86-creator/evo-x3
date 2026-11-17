# U2 prompt-skill merge - DONE note (2026-10-29, MAX block item 1)

Brief: Max 09:56 CT on Derrick's go ("Go, brief Forge on step 2"). Plan unit:
`C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md` -> Units -> **U2 Prompt-skill merge**.
**File edits only. No GPU, no render, no model load, no queue.** MAX block: **stop after U2** - U3-U5 not started.

## Verdict

`C:/AI/community/notes/u2_check.py` -> **exit 0, ALL CLAUSES PASS (46/46) at the end of the FIX pass below**,
read-only. (v1 reported 31/31 at 10:26 CT; Max's independent verify at 10:29 found real defects that v1 could not
see, so v1's tick was premature - the tick line in `fix_plan.md` now carries the fix-pass evidence.)
Run: `C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/u2_check.py`

The plan's U2 check is the literal instrument: **each rule string appears in exactly one skill.** The check parses
the 31 numbered rule blocks out of the home file, normalises them (whitespace collapsed, markdown stripped) and
searches the first 90 normalised chars of every rule across **all 10 SKILL.md files in both skill trees**
(`C:\AI\community\skills` + `C:\Users\derek\.pi\agent\skills`):

- `rules_R1_to_R31_parsed_from_home` - 31 rule blocks, ids R1..R31 in order.
- `each_rule_string_in_exactly_one_skill` - **31/31 unique to the home skill, duplicates = none.**
- `pointer_*_carries_no_rule_text` - the three pointer skills contain **zero** home rule signatures.
- `pointer_*_shrank_vs_backup` - ref2va-prompt 8,635 -> 3,030 B; h3-ref2va-prompt-chain 3,533 -> 3,122 B;
  alienpc-hardcore-i2v-director 19,545 -> 19,112 B (its prompt sections became pointers; lane content kept).
- `promptmd_L16_dead_names_gone` / `promptmd_L16_every_path_exists` - the dead names are gone and **all 7 paths
  L16 now names exist on disk**; `promptmd_one_line_only_changed` - exactly line 16 changed, file length unchanged.
- `backups_exist_with_pre_edit_bytes` - all 5 `.bak-20261029-u2*` files match the sha256 prefixes printed before
  any edit (02d7a031 / d61b2d36 / eb9a0ba6 / 21a3095e / 38cef8b1) - the backups are the true pre-edit bytes.
- `youth_guard_tests_pass` - `test_p6_review.py` + `test_guard_scope.py` = **26 passed** (CPU only), guard unchanged.
- `gpu_idle` - `gpu_guard.ps1` = IDLE.
- `u2_writes_are_the_allowed_set` - the files written under `C:\AI\community` since the backups are exactly the
  home skill, its backup, the HF save, and my `notes/u2_*.py` scripts (+ a `.pytest_cache` from the guard run).

## FIX pass (Max verify 10:29 CT, `notes\2026-10-29-max-U2-verify-FAIL.md`) - 10:3x-10:5x CT

Max's verdict: "FAIL (close)" - backups, PROMPT.md L16, examples and the two short pointers PASS; the director still
restated prompt rules and still sent writers to a second paste template that uses `overall_soundscape`; R26 overlapped
R7; Example 2 shortened the R11 clause; R22/Example 1 used negative stacks against R24; the mid snapshot sat in the
skill folder; and my check had been loosened. Every item is closed:

| Max item | fix | clause that proves it |
|---|---|---|
| 1 director L122-128 | the "static hold vs full reveal" section is now one line: "Static hold / "reveal" / camera-fit moves / frame-0 behaviour / `ref_image_size`: **R6, R15, R23** in ..."; the restated sentences are gone | `no_rule_phrases_paraphrased_in_alienpc-hardcore-i2v-director`, `max_named_key_phrases_absent_from_pointers` ("does not pin frame 0", "zoom out" now appear in no pointer) |
| 1 director L56, L95-96 | the pointer to `references/max-i2v-prompt-improve-v1.md` is marked **HISTORY, not a live guide** in both places, and the pack itself got a HISTORY header (with `.bak-20261029-u2fix`, sha8 612ec3b3) naming R7 and the HF #77 ruling; "read before writing a Max I2V paste" is gone | `every_skill_file_naming_audio_blocks_marks_it_superseded`, `no_rule_phrases_in_pointer_supporting_files` (23 archived rule phrases live there, allowed only because the file declares itself history) |
| 1 director L63 | "only if loaded" -> "**R31** decides (a trigger word needs the LoRA in the graph)"; the Klein-side LoRA sentence was kept (I re-added it after one edit trimmed it) | `max_named_key_phrases_absent_from_pointers` ("only if loaded") |
| 1 "another lane never enters Max TE" in one place | kept in the director (its lane), `ref2va-prompt` now points to it | `max_te_lane_rule_in_one_place` = exactly `alienpc-hardcore-i2v-director/SKILL.md` |
| 2 ref2va L21-25, L27 | node-mixing -> (R6); "the still wins" -> (R28); the TE duplicate -> a pointer; gate item 3 -> "Run the **R30** diff gate" | `no_rule_phrases_paraphrased_in_ref2va-prompt` = 0 of 2,304 rule shingles |
| 2 chain L62-63, L68, L78 | same-Cond and seed text -> (R29); the open-state mechanism -> "R16's open-state clause says what counts as a reference"; audit keeps only cites | `no_rule_phrases_paraphrased_in_h3-ref2va-prompt-chain` = 0 ("unique seed per cell" and the R29 wording are gone) |
| 3 h3 R26 vs R7 | R26 is now **vocabulary only** (number kept so `R<n>` citations stay stable); the soundscape/no-music repeat is R7's alone | `home_rules_do_not_share_phrases` = no pair of home rules shares a 5-word phrase |
| 3 Example 2 R11 clause | the full verbatim clause is in Example 2 (no "...") | `example2_carries_the_full_r11_clause` (scanned with whitespace normalised, so hard wrapping cannot hide a shortening) |
| 3 R22 / Example 1 negatives | "no mark, no swelling, no bruise, no tear" -> "the struck cheek stays smooth and unbroken, her eyes stay clear and dry, her face stays unwounded" | `no_negatives_in_r22_or_examples` |
| 3 "~10 KB each" | the home now states the measured **9,749 B for both** (the file is 9.7 KB total, not each) | `home_examples_sourced_as_planned` asserts the measured string is present |
| 4 mid snapshot | `SKILL.md.mid-20261029-u2-examples` (36,481 B) moved to `C:\AI\community\notes\`; the skill folder holds SKILL.md + references only | `mid_snapshot_moved_out_of_skill_folder` |
| 5 the check itself | see below | 46 clauses, exit 0 |

Also fixed while in there: R5's summary line no longer restates R16's opening words (found by the new internal
duplication clause), the director's content floor points at **R2** instead of repeating the adults-only wording (its
canon-file gate stays), and the home's claim "both notes roots point at the same file" was **false** - p15 exists only
in `C:\Users\derek\5slock\ralph-community\notes\`; the home now says that (`home_states_p15_single_copy_location`).

### What I changed in the instrument (Max item 5), and why v1 missed this

1. **A phrase check, not a prefix check.** v1 compared the first 90 normalised characters of each rule - it can only
   find copies. v2 takes every 5-word shingle of every home rule (2,304 of them), masks paths, filenames, skill names
   and `R<n>` citations (citing a rule is a pointer, not a restatement), drops shingles made only of function words,
   and requires **zero** of them in any pointer SKILL.md. That is what caught the paraphrases in Max's check 2.
2. **Key phrases**: the four phrases Max named are asserted absent from every pointer skill.
3. **Internal duplication** inside the home is a FAIL (the R26/R7 overlap).
4. **References scan**: every file under any skill dir naming the two audio blocks must mark them superseded/deleted
   by R7 - this is the clause that would have caught the director pack on day one.
5. **Audio pass-list**: "block", "history", "nothing" removed; the test works on **sentences** (v1 tested single
   lines, which fails on hard-wrapped prose).
6. **Restored scope clause** v1 dropped: nothing under `scripts/`, `p7/`, `p3/`, `runs/`, `specs/` may be written by
   this unit (pytest caches excluded). Plus the 5 u2fix backups verified by sha prefix, the mid-snapshot location, and
   the pointer-size guards (no pointer may grow more than 400 B in the fix pass, none may return to its pre-U2 size).

## What changed (5 files, all backed up first)

| file | before | after | change |
|---|---|---|---|
| `C:\AI\community\skills\h3-prompting\SKILL.md` | 6,362 B | **28,383 B** + `references/examples_archived.md` 9,749 B | **the single home**: R1-R31 numbered rules, output contract, adults-only, five-section shape with the audio rule, identity/wardrobe/motion/contact/wording rules, the detail checklist, 2 current-shape examples, section 7 "who defers to this file", sources. The 2 archived p15 few-shots (verbatim) live in the skill's supporting file |
| `C:\Users\derek\.pi\agent\skills\ref2va-prompt\SKILL.md` | 8,635 B | 3,030 B | rule index by number + node/lane facts + the pre-queue gate |
| `C:\Users\derek\.pi\agent\skills\h3-ref2va-prompt-chain\SKILL.md` | 3,533 B | 3,122 B | chain lane (cell scheduling, shared refs by builder, seeds, queue gate, judging policy) + chain audit; all prompt rules -> R cites |
| `C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md` | 19,545 B | 19,112 B | its 5 prompt-rule sections (Max POS craft, H3 prompt shape, frame-one identity, Static Shot vocab, static hold vs reveal) + the POS/one-act/Cond!=act bullets + the director-card paste line -> pointers; still->intent, fair loop, watch words, beta7 argv, ports, KEEP policy all kept |
| `C:\Users\derek\5slock\ralph-community\PROMPT.md` L16 | 5,802 B | 6,122 B | dead `p15_writer_batch.py` / `p15_driver.ps1` replaced by real scripts; prompt-rule and render-dial pointers named by path |

**After the FIX pass (10:5x CT):** home SKILL.md **28,753 B** (28,383 before the fix: +370 for the R26 rewrite,
the positives wording and the corrected example/source notes); director SKILL.md **19,269 B** (pre-U2 19,545 -> -276;
the fix pass removed the restated rule sentences and added cite + history lines); ref2va-prompt **3,029 B**
(8,635 -> -5,606); h3-ref2va-prompt-chain **3,029 B** (3,533 -> -504); the director's history pack +596 B (its
HISTORY header). Net: **no rule text is restated anywhere** - 0 of 2,304 home-rule 5-word shingles appear in any
pointer skill, and none of the four key phrases Max named appears in any pointer.

Backups: `SKILL.md.bak-20261029-u2` x4 + `PROMPT.md.bak-20261029-u2-l16` (the U2 edit) and `.bak-20261029-u2fix`
for the five files the FIX pass touched (sha8 5a293990 / 47e69734 / 612ec3b3 / 3e534e78 / 54f8c402). The
intermediate 36 KB SKILL.md snapshot is kept **out of the skill folder**, in
`C:\AI\community\notes\SKILL.md.mid-20261029-u2-examples` (Max item 4). The `.pi` skills tree is **not a git repo**,
so the `.bak` is the only rollback there; `C:\AI\community` and `ralph-community` are repos, so those two files also
have git history.

### Context cost (measured, and what I did about it)

With the two archived p15 few-shots inline, the home skill grew to **36,109 B** - it loads on every prompt task,
against PROMPT.md 0d ("Context is the budget"). The verbatim examples moved to the skill's **supporting file**
`references/examples_archived.md` (pi skills support supporting files - pi docs `configuration.md`), leaving
**SKILL.md 28,383 B** and keeping the plan's 3-6 examples inside the skill package (2 archived verbatim + 2
current-shape inline). `u2_check.py` enforces `home_skill_size_within_context_budget` (SKILL.md <= 30,000 B) and
prints the load cost. **28 KB (~7k tokens) is still the largest skill on the box** - the rule set is what it is;
if Max wants a leaner load, the split point is the per-topic rule groups (section 4) into supporting files, which
would trade one-file reading for a smaller load. Flagged for Max, not done unasked.

## Plan clause -> evidence

- **Single home, numbered rules** - R1-R31 in `h3-prompting`; instrument proves uniqueness across all skills.
- **"Output only the prompt"** - R1, and the loop's own 1c ("Count words; nothing else") is cited, not restated.
- **Adults only (18+)** - R2/R3: 18+ floor, fictional, minors = hard stop, no policy text in the paste; the p15
  canon-age declaration convention (21+ with a stated age) is kept as the prompt-side convention because both
  archived examples use it.
- **3-6 examples from `notes\p15_writer_skill.md`** - `home_has_all_p15_fewshots` + `home_examples_3_to_6`: p15
  carries **exactly 2** few-shots; both are reproduced **character-for-character** (LF-normalized; the source is
  CRLF) in the skill's `references/examples_archived.md` and labelled as archived history. The remaining 2 examples
  are composed from this box's measured rules and named runs (the dominance cell's response dial + slap-to-face,
  and a get-into-position from a standing Cond) and are inline in the current shape (audio inline, no soundscape
  block). Package total = **4**, inside the 3-6 range; no p15 bytes were changed.
- **Plain wording + a detail checklist only if p15 or Wan `prompt_extend.py` already has them (review T-6)** -
  `p15_writer_skill_untouched`: p15 already has "Grounding & Core Standards" (plain concrete wording, positives
  only, no transition words) and a "Rubric & Review Guide (Self-Refine Check)" = the detail checklist, so both are
  allowed and the checklist is section 5, adapted only on the audio line. `wan_prompt_extend_absent_recorded`:
  **`prompt_extend.py` is not on this box** (`C:\` depth 6, plus both `ComfyUI-WanVideoWrapper` trees searched -
  present trees: `C:\AI\comfy-longvideo\...\ComfyUI-WanVideoWrapper`, `C:\Users\derek\ComfyUI-038-longvideos\...`),
  so the T-6 gate is met by p15 alone. Recorded, not assumed.
- **The three skills become pointers** - checked: they point at the home by skill name and absolute path and carry
  no rule text.
- **Repoint the dead PROMPT.md L16 scripts** - measured: `p15_writer_batch.py` and `p15_driver.ps1` do not exist
  anywhere (searched `C:\AI\community` and `C:\Users\derek\5slock`); `bk26_judge_harness.py` does. L16 now names
  `notes\bk26_writer_batch.py`, `notes\bk26_judge_harness.py`, `notes\bk26_judge_batch.py`, `notes\p15_driver.py`,
  `C:\AI\community\scripts\run_graph_job.py, verify_cell.py, prompt_stats.py, review_pack.py, finalize_encode.py`
  plus the two skill paths - 7 paths, all verified to exist.
- **Audio (TenStrip HF #77)** - R7 deletes the `overall_soundscape:` / `non_diegetic_music:` blocks and puts plain
  cues at the end of the main prompt, quoting the owner verbatim; the page text is saved to
  `C:\AI\community\notes\web\tenstrip_hf77_audio_20261029.md` (one fetch, `check_web_saves.py` = CLEAN, 174 files).
  The home's own mentions of the two tokens are all in a deleted/forbidden/superseded context
  (`home_audio_rule_no_soundscape_block`).
- **Reuse existing guides, do not duplicate** - section 7 of the home names the lanes that keep their own material
  (`h3-hc-render` dials, `alienpc-local-video-ops` queue/watch, `alienpc-stills-pose-edit-prompting` FLUX.2,
  `alienpc-ltx-i2v-prompting` LTX baseline); the LTX and render skills were **not** edited.
- **Youth guard unchanged** - 26 tests pass; `scripts/comm.py` untouched.
- **Backups + one START and one DONE line** - `notes/actions.log` 10:0x START and this DONE line.

## Honest deviations and notes for Max

1. **`notes\p15_writer_skill.md` resolves to `C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md`**
   (13,379 B). There is **no** `p15_writer_skill.md` under `C:\AI\community\notes`. The plan's U4 "one notes root"
   item has this split; I used the file that exists and did not move anything.
2. **18+ vs 21+**: the plan says "adults only (18+)"; p15 and both its examples declare canon ages **21+**. The
   home keeps both as separate things (the floor is 18+/no minors, the in-prompt convention is a stated 21+ age),
   which is what the archived examples require. If Max wants one number, say which and I will make it single.
3. **The audio change is forward-looking.** Existing run records (e.g.
   `runs\terrace_dom_q5guide_20261028_s51083007\prompt_seg0.txt`, `overall_soundscape:` at line 28) and the B2
   default graph are **not** edited - they are history and the audited default. Reusing an archived example means
   moving its sound sentences to the end of the description (stated in the home, section 6).
4. **`p15_writer_skill.md` itself was not edited** - it is the writer model's system prompt, not a rule file. Its
   `overall_soundscape:` instruction is marked superseded by R7 in the home's section 7; if Max wants the writer
   model to change too, that is a separate, owned edit (it feeds `notes\bk26_writer_batch.py`).
5. **`C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\references\max-i2v-prompt-improve-v1.md`**
   still carries 6 `overall_soundscape` mentions. It is a references file, not a skill, so U2's check does not
   cover it and I left it; it is the director's paste-ready template pack, so it should follow R7 when you want it.
6. **LTX lane untouched** (the plan named three pointer targets). Its "POS = plain English motion prose / never
   JSON-as-POS" family is its own baseline wording; the instrument confirms no home rule signature appears in it.
7. Sizes: prompt-rule text moved **out** of three `.pi` skills (-6.4 KB) into the one home. Reading a prompt task
   now loads one rule file (28 KB) plus three short pointers; the 20 KB of archived example text is read on demand.
   The load cost is stated above and is Max's call.

## Files written by this unit

`C:\AI\community\skills\h3-prompting\SKILL.md` (+ `.bak-20261029-u2`, `.bak-20261029-u2fix`) and its
supporting file `references\examples_archived.md`,
the 3 `.pi` skills (+ `.bak-20261029-u2` and `.bak-20261029-u2fix` each) and
`alienpc-hardcore-i2v-director\references\max-i2v-prompt-improve-v1.md` (+ `.bak-20261029-u2fix`),
`ralph-community\PROMPT.md` L16 (+ `.bak-20261029-u2-l16`),
`C:\AI\community\notes\web\tenstrip_hf77_audio_20261029.md`,
`C:\AI\community\notes\u2_start_record.py`, `u2_director_pointerize.py`, `u2_director_fixup.py`,
`u2_audio_lines_probe.py`, `u2_rules_probe.py`, `u2_examples_move.py`, `u2_examples_normalize.py`,
`u2_check.py` (v1, then v2 after the verify), `u2_closeout_record.py`, `u2fix_start_record.py`,
`u2fix_closeout_record.py`, this note,
`C:\AI\community\notes\SKILL.md.mid-20261029-u2-examples` (moved out of the skill folder),
`fix_plan.md` item 1 (tick line rewritten with the FIX-pass evidence; + `fix_plan.md.bak-20261029-u2-tick`),
`notes\actions.log`, `notes\progress.md`.

## Stop

MAX block: **"Stop after U2."** U3 (Sydney talk session), U4 (storage) and U5 (lean PROMPT.md) are **not started**.
`gpu_guard.ps1` = IDLE before and after; nothing rendered, no model loaded, no queue touched.
