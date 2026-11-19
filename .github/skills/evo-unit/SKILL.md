---
name: evo-unit
description: "Use when starting or closing an EVO-X3 unit of work: new PLAN.md, U## agy brief for Antigravity on the X3, RESULT file, or X3/AlienPc lease take/release file. Templates and naming for records/."
argument-hint: "What to create: plan <topic> | brief U## <slug> | result U## | lease take|release <holder> <job>"
---

# EVO unit files

Templates for the files one unit of work produces. The naming and record rules are in
`.github/instructions/records.instructions.md`.

## Flow

1. **Plan** (`records/<topic>/PLAN.md`) from [plan-template.md](./assets/plan-template.md). Plan only: nothing
   runs. `evo-plan-reviewer` reviews it, then Derrick answers the Q# cards and gives his yes (S0).
2. **Brief** (`records/U##-<slug>-brief-YYYYMMDD.md`) from [brief-template.md](./assets/brief-template.md),
   one per approved step that agy runs on the box.
3. **Lease**: the runner takes it on the box before mutating work, using
   [lease-taken-template.md](./assets/lease-taken-template.md), and releases it with
   [lease-released-template.md](./assets/lease-released-template.md). From this Windows clone you only draft
   these files; you never hold a lease.
4. **Result** (`records/U##-RESULT.md` or `records/<topic>/RESULT.md`) from
   [result-template.md](./assets/result-template.md). agy writes it on the box. Max or a reviewer checks it.

## Procedure

1. Read the matching template and the newest real example of that kind in `records/` (for example
   `records/U55-agy-brief-20261116.md`, `records/U55-RESULT.md`, `records/monorepo-consolidation/PLAN.md`).
2. For a U number, list `records/U*` and take the highest number plus one. Mark it ASSUMPTION; the box can be
   ahead.
3. Fill every `<...>` field. Delete any template line that doesn't apply rather than leaving it empty.
4. Cite Derrick's message ids (`t####u`) for every scope decision. If there is no id for a decision, it goes in as
   a Q# card, not a fact.
5. Before handing over, check:
   - no secrets, tokens, auth headers or real key values;
   - every live step names its lease, its test and its rollback;
   - the STOP CONDITION names the exact RESULT path.

## Brief rules (from U53–U56 practice)

- Title line: `# U## (Antigravity, Hydrogen High): <goal>, <Mon DD YYYY>`. The launcher runs
  `gemini-4-hydrogen-high`.
- Open with Derrick's quotes and ids, then "Max verifies your RESULT afterwards."
- State the access: which user runs it, which repos it uses, `sudo -n -u evo` when the repos belong to evo.
- Code changes go in a per-run worktree (`records/agy-launcher-convention.md`).
- Rules always include: back up changed files as `*.bak-YYYYMMDD-u##` in `_archive/`, commit by path only, no
  force push, push to the gitea remote named in the brief, no secrets on argv or in output, keep it small (no new
  gates or knobs).
