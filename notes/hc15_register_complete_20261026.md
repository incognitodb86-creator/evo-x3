# 2.4b RENDER REGISTER COMPLETE - record (2026-10-26, ralph-community item 2.4b)

Item: **Name the graph AND the prompt keys in every render-register row.**
Plan: `C:/Users/derek/5slock/ralph-community/notes/plans/2.4b-register-complete.md`.
No GPU, no queue, no render, no vision model, no KEEP, no score: every clip in scope was already paid for.
`scripts/comm.py` read, never edited. No secrets touched.

## Pre-state measured on this box (2026-10-26, before the work)

- `C:/AI/community/runs` = **96** dirs; `ComfyUI/output/community` = **62** dirs; `C:/AI/community/p7/graphs` = **21**
  graph files.
- The only tracked render register, the generated block in `C:/AI/community/notes/hc15_20261024.md` built by
  `notes/hc15_anchor_carry_build.py --render-rows`, names **six** clips (2.1c/2.1d scope).
- `git grep s51150032 -- notes/hc15_20261024.md` = **0**: 13 PAID clips are in no register row.
- Of 239 tracked files in `C:/AI/community/notes/`, **235** contain an `ali163_*` id, so "named anywhere" is a
  useless bar; a usable bar must name a tracked register doc.
- 0 tracked graph JSON exists for `s51160001`-`s51160005` (top5) and `s51170001`/`s51170002` (E5 5 s), and 0
  tracked `.result.json` exists for any id.

## What shipped

- `C:/AI/community/notes/hc15_register_complete_build.py` - one generator, four modes:
  `--scope` (census), `--emit` (writes the block), `--check` (re-measures every field of every row),
  `--selftest` (24 named seeded faults).
- The generated block in `C:/AI/community/notes/hc15_20261024.md`: markers
  `BEGIN/END 2.4b complete render registration`, **21 rows, 36,225 B**, each row naming graph path + graph bytes +
  graph sha256, mp4 path + bytes + sha256 (or the exact missing pieces), `run_dir`, the ffprobe line, the audio
  verdict, render start/end/minutes, `objective.json`/`status.log`, `save_prefix`, the approved still, contact
  sheet, **`prompt_keys` + prompt-string count + `guard_ok_all` read from the graph named in the same row**, and
  the ComfyUI output dir. Headings are `#### Clip` so the 0.1 block's `^### Clip` parser never reads these rows.
- Scope, stated and checked as a census, not a constant:
  - **CURRENT = every id with a graph in `C:/AI/community/p7/graphs`** = 21 ids: 13 `paid`,
    1 `clip on disk, client-stalled` (`ali163_hc15_bd002_s51150021`, a 6,297,740-byte mp4, `objective.json`
    `attempts: []` - collected from disk, never re-rendered, not an objective failure), 1 `half-paid`
    (`ali163_hc15_gi046_s51150031`, evidence pieces with no mp4), 6 `staged` (graph only).
  - **LEGACY = a rendered clip in `runs/` with no graph in `p7/graphs`** = 29 dirs = **23 true legacy** +
    **6 alias dirs**. An alias is proven by bytes: `runs/ali163_hc15_bd002_s51150011/ali163_hc15_bd002_s51150011.mp4`
    and `runs/ali163_hc15_bd002_s51150021/ali163_hc15_bd002_s51150021.mp4` carry the same sha256 = the pre-rename
    real dir of a current row. Legacy rule: the clip id appears in a tracked file under `notes/` = **0 LEGACY-UNNAMED**
    (all 23 do; the 235-of-239 id-grep is disclosed in the block header as too weak to be the bar).
- All 21 graphs expose exactly one prompt-bearing key, `prompt`: 2 strings on the 15 s graphs, 3 on the six 0.1
  graphs, 1 on the two 5 s graphs (E5 `s51170001/2`, 559 words, 351-char `prompt` value).
- The top5 family register `notes/top5_euler_5s_20261025.md` is re-read by `ck_family_register` (all 5 rows).
- `notes/ali11_run_checks.py` (ralph-community) gains `render_register_complete` +
  `render_register_complete_selftest` with the captured verdict lines and their counter-samples. Not in `PASS_TIER`:
  it runs ffprobe over 14 clips + sha256s, so it is an item gate (~20 s), not a per-pass row.

## Measured results (exact)

- `python notes/hc15_register_complete_build.py --check` ->
  `VERDICT REGISTER_COMPLETE CLEAN rows=21` with
  `scope current=21 states={'staged': 6, 'paid': 13, 'clip on disk, client-stalled': 1, 'half-paid': 1} legacy=23 aliases=6`
- `python notes/hc15_register_complete_build.py --selftest` ->
  `VERDICT SELFTEST CLEAN seeds=24 fired=24 silent=0 real_findings=0`
- `git grep -c s51150032 -- notes/hc15_20261024.md` -> `notes/hc15_20261024.md:12` (the item's done-when).
- The 0.1 block stays intact: `python notes/hc15_anchor_carry_build.py --render-check` ->
  `render-check: 6 clips measured off disk, 99425 B of note read; 0 failures`;
  `--render-selftest` -> `render-selftest: 20 seeds, all fired and the six real rows are clean`.
- `python notes/ali10_adults_probe.py` -> `VERDICT CLEAN`, `gate=return`, 3 findings (2.1b rows), `live_urls=['127.0.0.1:9']`.
- `python -m py_compile notes/hc15_register_complete_build.py` -> clean.

- `python notes/ali11_run_checks.py --pass` -> `manifest: notes\pass_checks\20261026-06.json all_green=True
  rows=19`, `VERDICT this pass: tests GREEN (19 rows, manifest 20261026-06.json)` - the tier includes
  `learnings_check`/`learnings_selftest` (both `RESULT CLEAN`, 45 lessons), `pytest_p6_review` 21 passed, the whole
  suite 38 passed, `adults_probe_gate`, both secrets matrices, `loop_static` 69 seeded faults 0 silent, and
  `loop_sandbox` 15/15. The two new register rows are NOT in the tier (item gates), and `shortplan_check` is not in
  the tier either, which is why the tier is green while the plan gate is red for the pre-existing classes below.
- `python notes/ali06_learnings_check.py` -> `AGENTS.md 39 lines (cap 39); 21 lesson lines (cap 320 chars);
  45 write-up lessons; 0.2 rows live = 75/41/5` `RESULT CLEAN`.

## Disclosed: the shortplan gate is red for pre-existing reasons, and one rule needed a real fix

`python notes/ali14d_shortplan_build.py --check` on the base plan (base `fb9968e`) is **NOT CLEAN before this
pass touches anything**: 424 findings, 359 `RECEIPT_EXTRA` (receipt files owned by no base row), 63
`RECEIPT_UNTRACKED` (receipts written by the last emit, never committed), 2 `IDS 'E5'` (a base row and an inserted
row carry the same id = 4 rows for 3), 1 `NO_INVENT` (the invented `+TOP-SCENE-L22.md` sheet line), and
`PROGRESS` (no progress row for the current `CLOSURES` - this pass adds the 2.4b row). My pass adds no new class:
the two 2.4b rows went open -> ticked and are named by CLOSURES, and `RECEIPT_UNTRACKED` drops as soon as the
receipts are committed (this commit).

Two of my own measurements changed the plan builder, both with a measured counter-case:

1. **`OPEN_COUNT` fired on a correct cut.** The rule computed `ob - len(closed)`, where `closed` counts *ids*,
   while the plan had **two rows** for id `2.4b` (the 1.4d base row and a later duplicate insert) and this pass
   closed both: 61 - 1 = 60 expected, 59 real. The rule's own words and `ralph.ps1`'s `OpenPlan` both count
   **rows**, so `closed` now extends by rows (`notes/ali14d_shortplan_build.py:506`).
2. **The builder's `--selftest` crashed** at HEAD and with my change:
   `ValueError: max() iterable argument is empty` at the S10 `tail_prose` seed - base `fb9968e` carries no tail
   bucket with prose, so that seed has no target. It now prints a named skip and drops from the required list, the
   same shape the S12 `DONE_WHEN` seed already used, instead of crashing the whole selftest.

3. **The gate is not idempotent across a tick commit, measured.** The base is `git show HEAD:fix_plan.md`, and a
   receipt slug is `<id>-L<line number in the base>`. Before my commit the base was `fb9968e` and `--check` printed
   426 findings (359 `RECEIPT_EXTRA`, 63 `RECEIPT_UNTRACKED`, 2 `IDS 'E5'`, 1 `NO_INVENT`). After the tick commit
   the base is my own commit and the same command prints 488 findings, 486 of them `RECEIPT_MISSING`: every row now
   demands `0.1-L41.md` while the 425 files on disk are `0.1-L37.md`..., because the emitted plan's line numbers moved
   by 4. `RECEIPT_UNTRACKED` measured **0** after this commit, which is the part my pass controls. Reading the gate
   correctly therefore means reading it **before** the tick commit, and the line-number key is the defect: a plan-row
   identity that moves every time the plan is cut. That belongs to a future pass with its own measured cut rule
   (L12/L43 already say an anchor must be computed, not grepped); it is not fixed here and not hand-edited into a
   generated plan.

## Not this item

- The duplicate `E5` row (the `+TOP-SCENE-L22.md` sheet line) is an item 2.1b/1.4d-format defect: it needs its
  own pass with a measured cut rule, not a hand-edit of a generated plan.
- Receipt-store hygiene (359 `RECEIPT_EXTRA`) is a separate cleanup item.
- No KEEP and no ranking: `gi046` is a candidate only because E5 measured it as the graph that renders (4.75 min).
  No prompt quality, no content judgement, and 0 of the 21 graphs carry a `positive_critical` key.
- The `staged` rows are claims about files, not render intent: 6 graphs are staged and unprompted for a render.
