# REF2VA chain lane (cells from one still) - h3-max-ref2va-prompt

Chain-lane facts only. **Every prompt rule for a cell is in `../SKILL.md` (R32-R44, this skill) and in
`/home/derekboone/AI/community/skills/h3-prompting/SKILL.md` (R1-R31); cite `R<n>`, never restate a rule in a brief.** The per-cell
audit is `h3-prompting` section 5 plus section 5 of `../SKILL.md`.

## Chain lane (this file only)

- **A chain is N cells from one Condition still.** Which Cond a chain keeps, seeds per cell, and the "cell N of M"
  line in `summary` are **R29**. Each cell is its own paste file in the run dir, built by the parameterized builder
  so the diff shows only that cell's axis (**R30**).
- **Shared subject definitions are pasted into every cell by the builder, never retyped**, and the label ordinals are
  identical in every cell (**R28**, ordinals per **R33**). A cell that opens in a pose the still does not show needs
  a reference that shows that pose - **R16**'s open-state clause says what counts as one; on this graph a pose
  reference is an added `ref_images` slot, and **R33** says what our builder wires today.
- **Between cells:** the R10 opening line is a prose cue; the actual mechanism is latent-tail continuation, see
  **R33** and section 4 of `../SKILL.md`. Never write a `<Video N>` / `<Audio N>` label in a chain cell while those
  inputs are unwired (**R33, R34**).
- **Storyboard panels:** a panel used for shot planning is defined in the R36 form (`<Picture N> is a storyboard
  reference for [Shot 1] and [Shot 2], defining their viewpoint, subject placement, and shot order.`); the
  `<Shot Reference N>` wording of R10 stays valid inside `detailed_description`.
- **Batching:** seeds are **R29**, one variable per cell. Render dials and queue mechanics are `h3-hc-render` /
  `alienpc-local-video-ops`; beta7 is the standing KEEP line and is never re-decided per chain.
- **Queue gate:** do not queue Comfy until Derek reviews the pack or gives the exact GO for it.
- **Judging policy:** KEEP is Derek's exact GO only, agents never self-KEEP; TECH checks never override a contact
  FAIL; a cell that fails contact is re-cut, not re-labelled.

## Chain audit (this file only)

- [ ] Cond identity and per-cell seeds follow R29; the builder diff shows only this cell's axis and identical subject
      definitions across cells (R30).
- [ ] Each cell's `summary` states its position in the chain (R29) and its tag prefix is from the honest set (R34).
- [ ] No cell opens mid-a-previous-beat without a reference that shows it (R16 open state).
- [ ] No `<Video N>` / `<Audio N>` label without a wired input (R33); no base-mode alignment line (R36); no
      `<scenetrans>` (R40).
- [ ] Each cell passes section 5 of `h3-prompting` and section 5 of `../SKILL.md`.
- [ ] Pack shown to Derek before any queue; no KEEP claimed by an agent.
