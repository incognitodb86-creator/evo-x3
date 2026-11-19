---
description: "Use when writing or editing EVO-X3 records: plans (PLAN.md), U## agy briefs, RESULT files, audits and status notes under records/."
applyTo: "records/**"
---

# Records

Templates for each kind are in the `evo-unit` skill (`.github/skills/evo-unit/assets/`).

## File kinds and names

| Kind | Path |
|---|---|
| Plan | `records/<topic>/PLAN.md`, then `RESULT.md` in the same folder once it has run |
| agy brief | `records/U##-<slug>-brief-YYYYMMDD.md` |
| Unit result | `records/U##-RESULT.md` |
| Apply brief (Forge) | `records/<ID>/BRIEF.md`, then `RESULT.md` in the same folder |
| agy run files | `U##-agy-launch.sh`, `-start.sh`, `.meta.txt`, `.log`, `-wrapper.log`: written on the box, never by hand |

Leases are not records (Derrick Nov 17, per Max `d80617f`): one line `<who> | <what> | <start time>` in
`/home/derekboone/AI/locks/x3-lease.txt` (AlienPc: one line per brain `10_packs/max/max-briefing.md`), taken at start
and cleared when done or blocked. Briefs name that line; never write lease files or `records/status/` mirrors.

U numbers come from the box and fleet brain, which can be ahead of this clone. Propose the highest number you see
plus one, mark it ASSUMPTION, and let Derrick or Max confirm it.

## Rules

- Old records are history. Don't rewrite a past brief, RESULT, log or audit. Add a new dated file or a
  `## Update YYYY-MM-DD` section.
- A plan can change freely until Derrick's S0 yes. After that, record changes in a dated section.
- Keep frontmatter keys that are already there (`pending_upload`, `artifact_contract`, `tier`). Don't flip
  `pending_upload` yourself.
- Plans use `artifact_contract: ce-unified-plan/v1`: Goal Capsule, Summary, Product Contract (current layout
  VERIFIED, R# requirements each with Pass and Gate), Planning Contract (KTD#, A# assumptions with tests, S# steps
  with Where/Lease/What/Test, Rollback, Q# cards for Derrick), Verification Contract, Definition of Done.
- Mark statuses as DONE, BLOCKED or SKIPPED, facts as VERIFIED or ASSUMPTION, and review verdicts as
  `VERDICT: APPROVE|CHANGES|BLOCK`.
- No secrets, tokens, auth headers or pairing codes in records. Point to where the secret lives instead.
- Every step that touches a live host names its lease, its test and its rollback.
