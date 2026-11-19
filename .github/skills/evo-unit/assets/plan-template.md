---
title: "<one-line plan title>"
date: <YYYY-MM-DD>
type: plan
artifact_contract: ce-unified-plan/v1
product_contract_source: derrick-chat (<t####u, ...>)
execution: <code | ops | docs>
tier: <T1 Quick | T2 Durable (<why>)>
author: <agent name>. PLAN ONLY, nothing applied
review: <evo-plan-reviewer | outside AI (Opus)> reviews this file before any step runs
pending_upload: true
---

# <Plan title>

Related: <../other-topic/PLAN.md or none>

PLAN ONLY. Nothing below has been run. Facts were read on <date time CT>. Labels: VERIFIED (read; say where),
ASSUMPTION (to test in the step that uses it).

## Goal Capsule

| Field | Value |
|---|---|
| Objective | <what Derrick asked for, with ids> |
| Means | <the approach, in one sentence> |
| Authority | <Derrick ids>; every step needs his yes after review |
| Out of scope | <what this plan does not touch> |
| Stop conditions | <checks that halt the plan or force a rollback> |

## Summary

<3–6 plain sentences: what exists today, what changes, why this way. Say how the community does it, if relevant,
and cite the source with the date you read it.>

---

## Product Contract

### Current state (VERIFIED)

<table or bullets of what exists now, with paths, SHAs and counts>

### Requirements

- R1. <requirement>. Pass: <check>. Gate: <who signs off>.

---

## Planning Contract

### Key Technical Decisions

- KTD1. <decision>. Rejected: <alternative> (<why>).

### Assumptions

- A1. <assumption>. Test: <how and in which step>.

### Secret safety

<what could leak and how each step prevents it; or "No secret surface: <why>">

### Ordered steps

| Step | Where | Lease | What | Test |
|---|---|---|---|---|
| S0 | chat | none | Review this plan; Derrick answers Q-cards and says yes. | yes recorded |
| S1 | <host/repo> | <none / X3 / AlienPc> | <what> | <check> |

### Rollback

<per host: exact undo and how long it takes>

### Open questions for Derrick (cards)

- Q1. <yes/no question with the default shown>

---

## Verification Contract

| Check | Command | Step |
|---|---|---|
| <check> | `<command>` | S1 |

## Definition of Done

<R# marked DONE in RESULT.md with evidence; leases cleared; Derrick's Q answers recorded>
