# Final review of the unified plan (2026-11-19 ~14:00 CT)

Reviewer: orchestrator (Claude Opus 5.5, VS Code), asked by Derrick 13:55 CT: "double check for errors, missing
information, potential issues & improvements. Do it yourself. This is the final review." Read: `records/uplan/PLAN.md`,
`records/hermes-direct-render/PLAN.md`, the five `UNI-APPLY-*` briefs, and Max's snapshots (`85a6114` X3 13:45 CT,
`434ceeb` AlienPc 13:52 CT) on `mono` `efa5857`. Nothing was checked on a host.

**Verdict: APPROVE after the fixes below (all made in this commit).** The open items at the end are things only the box,
a test result, or Derrick can answer; each has a step that answers it.

## Fixed in this commit

| # | Sev | Problem | Fix |
|---|---|---|---|
| 1 | MAJOR | `UNI-APPLY-X3-C` item 2 installed `pi-job` from `mono`, which already carries `H1c` (AlienPc-first coding), with no ESP-off alias prerequisite. Idle-AlienPc coding jobs would hit a model that doesn't exist yet. | `pi-job` is installed once, in `UNI-APPLY-X3-B` (after the alias). X3-C item 2 marked moved; X3-B now installs the `pi-job` Hermes skill and runs the `L9` `MEDIA:` check. |
| 2 | MAJOR | Done work had no apply brief: RP1-RP3, SK1-SK5, FX1 (incl. the Hermes copy), ST6, the M4/TQ template syncs, the `comm.py` carryover fix, and the M3 node check. | New `UNI-APPLY-X3-D` (X3) and `UNI-APPLY-ALIENPC-C` (AlienPc). |
| 3 | MAJOR | Benchmarks had no briefs, and the order table didn't show that the X3 (writer choice) and AlienPc (Flux / Miraclein setup and tests) run at the same time. | Two-lane "Order of work" table; new `BENCH-X3-W1` and `BENCH-ALIENPC-1`. |
| 4 | MAJOR | SK1 changes the writer prompt (persona lines, recompiled `writer_prompt.md`). If it lands after W1, W1 tests a prompt we then change. | X3-D (with SK1) runs before W1; W1 waits for X3-D's RESULT. |
| 5 | MINOR | Hermes -> pi coding had no live test in any brief, and the `pi-job` skill named coding only at the end of its description. | X3-B test 5 (coding ask in Hermes WebUI -> `pi-job code`, route checked); skill description now starts with coding. |
| 6 | MINOR | W1 quiet window (Gufo unloaded) could overlap an AlienPc test session, leaving coding nowhere to run. | Rule in the order section: tell Derrick the window; don't overlap it with the AlienPc lane. |
| 7 | MINOR | Stale text: rename note broken by an earlier link fix; RP/SK/TQ/FX1 rows said "not started / in progress"; C14 still asked to download Miraclein NVFP4; G6 / cards 8 and 12 open though the snapshot answers them; M1 not marked done. | Fixed in `PLAN.md`. |

## Coverage check (Derrick's questions)

| Area | Covered by | Status |
|---|---|---|
| Hermes skills | `H4` prune (19 kept), `pi-job` (coding + renders, `L9`), `pixlstash-image-library` (`H8`), `flux-klein-prompting` (Hermes copy in X3-D), `h3-writer` (Hermes plan U6, after W4) | covered |
| Hermes SOUL | Live SOUL routes video asks to `pi-job` (right until H9). Hermes plan R15 returns SOUL to stock with OC facts in `memories/USER.md` during U3-U9 (order step X8). | covered, at X8 |
| Hermes AGENTS.md / context | Hermes plan U4/U6: desk `AGENTS.md` = copy of `render/OPERATOR.md` per profile, drift-checked (KTD2) | covered, at X8 |
| Hermes model, UI, search, delivery | Gufo now, W4 winner later; WebUI `H7` done; search `H2` after the ACL (card 11); inline clips `L9` (X3-B) | covered |
| Hermes render pipeline | Today via `pi-job render`; Hermes-direct `H9` after the render-a vs render-b test (card 43) | covered, at X8 |
| Hermes -> pi coding | `pi-job code|review`, `H1c` routing, X3-B tests 1 and 5 | covered |
| pi set up for coding | X3 Forge: v2 model, SK2 skills, loop-guard + auto-continue (`H10`), L7 syntax check, `H5` `make check-all` gate, L6 STUCK bundle. AlienPc Forge: AGT1 (`coding_swift15_iq3s`, idle-only rule) | covered |
| Flux / Miraclein install | Weights + nodes already on AlienPc (K1); node load check M3 in ALIENPC-C; FX1 prompting skill on both machines; still tests in BENCH-ALIENPC-1 | covered |

## Open (answered by a later step, not by this file)

- **Hermes still asks:** Hermes has no route for "make a still" asks until the still templates are picked (A5). Add it to the Hermes skill at step X8 (with H9).
- **W1 arms 2/3:** whether `gemma4-heretic` and `ref2va-27b` weights are still on disk is unverified (`ref2va-27b` was commented out of llama-swap on 2026-11-17). BENCH-X3-W1 step 1 checks; a missing arm is skipped, not downloaded.
- **Klein9 widget enums** used by the M4 candidates are unverified until ALIENPC-C item 2 lists them.
- **RP3** needs ffmpeg with `-fps_mode` on the X3; X3-D checks before testing.
- **Live drift for Max:** `panes/{forge,render}/settings.json` still name the v1 `-sub` model.
- **X3-A** (running since 13:45) installs the older `pi-job` skill copy; X3-B reinstalls the current one. No action.
- **Code follow-ups** N1 (recompile vs long_continuation), N2 (L3 detached HEAD), N3 (recompile lint context), N5 (inbox sidecar restarts) stay open; L3 timer and `recompile` stay off until fixed.
- **Derrick, when the step comes up:** card 3/43 (X8), card 9 (FCSydny/FCMegan voice clip, preference only), cards 10/14 (extra writer arms, X6), card 22 (R2 download, A6), card 24 (depth LoRA, A5), cards 5/6 (lock-down, A8). Any time: S5/S6 switchover, card 11 ACL.
