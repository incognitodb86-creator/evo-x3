# Folded in from skill h3-ref2va-prompt-chain (verbatim body, audit 2026-10-29). Original description:

description: Pointer skill for MiniMax-H3 Ref2VA prompt CHAINS on AlienPc Max (many cells from one Condition still, batched through llama-swap). Every prompt rule for a cell lives in the h3-prompting skill (C:\AI\community\skills\h3-prompting\SKILL.md, rules R1-R31). This file keeps only chain-lane facts - cell scheduling, shared references, batching seeds, queue gates, judging policy, and the chain audit list. Use for any multi-cell H3 chain; cite rules as R<n>.


# H3 Ref2VA prompt chain (pointer - U2 2026-10-29)

**Every rule a cell must satisfy is in skill `h3-prompting`, file
`C:\AI\community\skills\h3-prompting\SKILL.md`.** Cite `R<n>`; do not restate a rule in a brief. The rule families
a chain needs: paste shape and task type (R5-R6), audio as plain cues (R7), shot timing (R8), continuation between
cells (R10), identity clauses, retention lines and hand lock (R11), clothing clause and garment remnants (R12, R14),
reference roles (R13), open state and get-into-position per cell (R16), PRIMARY MOTION and motion density (R17),
body inventory (R18), contact geometry per cell (R19), motion verbs (R20), response dial (R21), camera line (R23),
positives-only and no hedging (R24-R25), the per-cell hygiene of **R29**, the pre-queue diff (R30), LoRA triggers (R31). The per-cell audit is the checklist in
`h3-prompting` section 5.

## Chain lane (this file only)

- **A chain is N cells from one Condition still.** Which Cond a chain keeps and how seeds are handled is **R29**
  in `C:\AI\community\skills\h3-prompting\SKILL.md`. Each cell is its own paste file in the run dir, built by a
  parameterized builder that changes only that cell's axis (R30), so a chain diff is reviewable.
- **References:** the shared subject definitions are pasted into every cell by the builder, never retyped; a
  continued cell carries `<Video 1>` (R10); a cell that must open in a pose the still does not show needs a
  reference that shows that pose - **R16**'s open-state clause says what counts as one.
- **Batching:** the seed rule is **R29**; one variable per cell. The render dials and queue
  mechanics are `h3-hc-render` / `alienpc-local-video-ops` (beta7 is the standing KEEP line, never re-decided per
  chain).
- **Queue gate:** do not queue Comfy until Derek reviews the pack or gives the exact GO for it.
- **Judging policy:** KEEP is Derek's exact GO only, agents never self-KEEP; TECH (duration, frames, metrics) never
  overrides a contact FAIL; a cell that fails contact is re-cut, not re-labelled.

## Chain audit (this file only - the rest is `h3-prompting` section 5)

- [ ] Cond identity and per-cell seeds follow R29; the builder diff shows only this cell's axis in each paste and
      identical subject definitions across cells (R30).
- [ ] Each cell's summary states its position in the chain (R29).
- [ ] No cell opens mid-a-previous-beat without a reference that shows it (R16 open state).
- [ ] Pack shown to Derek before any queue; no KEEP claimed by an agent.
