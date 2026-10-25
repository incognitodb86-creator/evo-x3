# AUD1 - citation repair for the two shipped audits (plan)

## Goal
Every quote in `notes/cf1_setup_audit_20261024.md` and `notes/hc15_start_fidelity_audit.md`
must resolve, verbatim, in a body that is on disk in `notes/web/`, at the line printed.
Anything that does not resolve is marked REFUTED / NO-SOURCE / BLOCKED with the grep receipt,
never left as a bare URL.

## Why this item
AGENTS.md L4 (2026-10-25): the same invented-citation fault that 0.4 caught in a pi doc is
present in these two shipped docs - rows cite a URL whose saved body has 0 hits for the quoted
text (RIFE, lowvram, "cfg 1.0", "1280x768 for 16 GB cards", "topk 0.1-0.2", "video-only ON",
"euler is for simple motion and faster tests"). A doc whose citations do not resolve is
unusable as a build spec, and the next pass will re-queue renders off it.

## Files
- `notes/cf1_setup_audit_20261024.md` - repair the Source column of every row; add an
  AUD1 receipt section (claim -> phrase -> grep count -> disposition) and the banned wording.
- `notes/hc15_start_fidelity_audit.md` - repair lines 36, 89, 93, 96, 132 (the fabricated
  card quotes + the 1280x768/16 GB row); record the card's real sentences; add the AUD1 section.
- `notes/ali02_citation_check.py` - add CITES rows for the replacement wording, BANNED rows for
  the refuted wording (the anti-restore control), and add both docs to `SCAN_DOCS`.
- `fix_plan.md` (ralph-community) - tick AUD1 in the same commit as the work.

## Test (must be run, output quoted)
1. `python notes/ali02_citation_check.py` = 0 problems, every new row prints `ok`/`ban-ok`.
2. `python notes/ali02_citation_check.py --selftest` = fires 3 of 3 + 2 scan detectors.
3. Old-wiring probe (the non-vacuity proof): drive `run()` with the OLD fabricated phrases as
   CITES rows -> every one MUST print MISSING-TEXT; the same phrases as BANNED rows on the real
   bodies -> `ban-ok`. Zero fires on the probe = the check is worthless (L10).
4. `python -m pytest -q C:/AI/community/scripts/tests/test_p6_review.py` = 21 passed.
5. `python C:/AI/community/scripts/check_web_saves.py` = CLEAN.

## Done when
- Each repaired row prints a body + line that a grep reproduces.
- The four fabricated card quotes and the four fabricated docs quotes are in `BANNED`, so
  restoring any of them fails the check.
- Both docs are in `SCAN_DOCS` (a dead `web/<file>` token in either doc = rc 1).
- Receipts quoted in the docs and in `notes/progress.md`; AUD1 ticked; community +
  ralph-community committed.

## Hard lines for this pass
No GPU, no queue, no render, no new script/probe/harness (the repair rides the existing
checker), comm.py untouched, adults gate green.

## Note on tool views (found this pass)
`read` returned a 17,638-byte alias-aware `ali02_citation_check.py`; disk + `git show HEAD`
both give 15,059 B / sha `cae1a2b0e87d2d07` (mtime 2026-10-23 22:33, last commit `b13dead`).
The `read` view was stale, so the checker was read and patched from bash/python (authoritative)
and the docs were verified equal in both views before editing (cf1 7,882 B `0d3b00be`,
fidelity 19,620 B `a5be87b1`).

## RESULTS (measured at ship, 2026-10-27)
Gate: `python C:/AI/community/notes/ali02_citation_check.py` rc 0 = `checked 133 citations + 40 bans, 0
problems`, `global-absence scan: 22 tokens over 1146 bodies, 0 problems`, `auto-cite scan: 133 tokens over 8
docs, 0 problems`, `unverifiable (blocked) this pass: 3`. `--selftest` rc 0 = all six detectors fire.
`python -m py_compile` rc 0. AUD1 added 46 CITES rows, 24 file-scoped BANNED rows, 9 `card-no-*` refutation
rows, 22 GLOBAL_ABSENT tokens, and the two audit docs + the gate's own docstrings in SCAN_DOCS/AUTO_CITE.

Ship suite: `test_p6_review.py` 21 passed; `pytest` suite 38 passed; `check_web_saves.py` CLEAN (172 json);
`ali05_loop_check.py` VERDICT CLEAN + `--selftest` 56 seeded faults 0 silent; `ali06_learnings_check.py`
RESULT CLEAN (33 write-up lessons incl. the new Lesson 33) + `--selftest` CLEAN; `rt_window_probe.py --check`
CLEAN (13 checks) + `--selftest` 13 seeds fired; `ali11_run_checks.py --run` = 27 of 29 rows green. The two
red rows are **pre-existing and unrelated to citations**: `notes/pass_checks/20261025-05.json` (the last manifest
before this pass) shows the identical pair - `review_folder_flags` (`MANIFEST_UNCLEAN problems=11`) and
`adults_probe_gate` (`notes/ali10_probe_results.json`). Item 3.4 owns the first; the second is the adults-probe
artifact row. No GPU work this pass; `gpu_guard.ps1` rc 0 (IDLE) at open and at ship.

Two findings this pass produced that the plan did not predict:
1. The card on disk is 3,698 B / **63 lines** in **five** byte-identical copies (md5 `6471e229…`,
   sha256[:16] `ba3be667bf67bba7`): `03y_mc_readme.txt`, `03y_mc_readme_main2.txt`, `hc15_tenstrip_readme.txt`,
   `agy51_tenstrip_readme.md`, `pq1_tenstrip_card.txt`. Six CITES rows written mid-pass returned MISSING-TEXT
   because they quoted the 15,125 B revision; they are now `card-no-*` BANNED rows. The 2.1b card map in
   `notes/hc15_start_fidelity_audit.md` is off at `:20`->`:24`, `:40`->`:39`, `:30`->`:29`, and its
   `:41`/`:46`/`:51`/`:56` rows are 0 hits.
2. `notes/plans/aud1-citation-repair.md` cites `notes/web/pq1_tenstrip_d27_text.txt:12` - **that file is not on
   disk**, and its two sentences ("euler + simple 6/8 steps", "res_multistep is for faster convergence") are 0
   hits in all 1,146 bodies. A dated CORRECTION block was inserted into that plan; the gate rows are
   `g-d27-no-euler-line` and `g-d27-no-convergence-line`.

Plan written; the gate extension and the two audit rewrites are the work. Ship state: gate + `--selftest` green (all six detectors fire), full ship suite green, `fix_plan.md` AUD1 ticked in the same commit, progress appended, both trees committed. `notes/ali05_loop_check.py` (cwd `C:/Users/derek/5slock/ralph-community`) reports `plan open items outside ## Optional: python=59 powershell=59` after the tick; this pass also restored 12 plan rows that a pass boundary had deleted (they lived only in the working tree; HEAD `c3ea342` has 0 matches for `2.0**`/`Q2**`/`AUD1`), so this pass prints NO completion token.
