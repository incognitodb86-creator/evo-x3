---
name: CoS subagent dispatch
description: >-
  use this when Chief of Staff must farm heavy work, run a finish-to-end go
  chain, or decide executor vs teammate Bot vs connector — Plan first; full
  oversight recipe in references/finish-to-end.md; browser prompts include
  teardown; multi-step close needs Compound LEARNED
---
# CoS subagent dispatch

## Goal
Keep CoS responsive in chat. Farm heavy work to background workers on the shared computer. Hand stable outcomes to named teammate Bots. Never invent sidebar “subagent” Bots for one-off jobs.

## When to use which lane

| Lane | Use when | Examples |
|------|----------|----------|
| **Inline (CoS)** | One-step lookup, go-widget, routing decision, short answer | Seat yes/no, open-capa line, approval ask |
| **Background worker (executor)** | Multi-step, files, scripts, research > few seconds | Soft-delete lists, rclone checks, CAPA file refresh, playbook edits |
| **Browser worker** | Page automation when no connector | Non-seat sites only after [CoS browser dispatch](sand-workflow:cos-browser-dispatch) |
| **Desktop worker** | GUI / file dialogs / sites that defeat DOM | Rare; never for Imagine dump Chrome |
| **Teammate Bot** | Stable owner already exists | Imagine/Max → Max lane owner (ROSTER); ESPN clicks → Fantasy; reviews/CAPA scorecard → Fleet Reviewer; money ledger → Household; Shorts/Gemini/Flow → Shorts Studio; deep research → the owning lane bot |
| **Connector** | Gmail / Calendar / Drive when connected | Prefer over any browser |

## Finish-to-end recipe (moved from CoS Job 2026-10-02)
HARD locks remain in the CoS Job. Procedure detail (finish chain, anti-park close steps, oversight path list, community-stack smoke order) → `references/finish-to-end.md`. Load that file on a real go; do not paste it back into the always-on Job.

## Sequence
1. Name the outcome and finish line in one sentence. Prefer [fleet-ce-adapter](sand-workflow:fleet-ce-adapter) Plan before multi-step Work.
2. Prefer connector → teammate Bot (if they own it) → background worker → browser/desktop.
3. Read `/workspace/cos/subagent-matrix.md` and `/workspace/cos/browser-seats.md` before any Chrome.
4. Dispatch **one** worker stream per independent job. Parallelize only independent streams.
5. Every dispatch prompt must include: goal, specifics, relevant context, success criteria, what to report back. Workers start blank. Browser workers: include reuse-tab + teardown from [cos-browser-dispatch](sand-workflow:cos-browser-dispatch).
6. After dispatch: tell Derrick you started (plain language — “starting the Drive check”), keep working or end turn. Do not idle-poll.
7. On result: deliver to Derrick only what he awaits; fold teammate FYIs silently unless action needed.
8. Multi-step close → [fleet-ce-adapter](sand-workflow:fleet-ce-adapter) including gate 7 Compound LEARNED.
9. Stop/cancel supersedes: stop all running workers for that job before confirming.

## Budget (Derrick 2026-10-19, ALI-83)
- Simple work stays inline: a lookup, a single file, or under ~5 tool calls gets no subagent.
- **Max 2 parallel workers** per bot, and no worker spawns workers.
- Every brief states a **stop condition**: success criteria, plus a tool-call or time budget. Return ≤15 lines and a file path, not raw output.
- Antigravity/Forge or any weekly-quota job: put the **expected quota %** on the Linear issue before launch and the **actual %** after. Quota spend still needs Derrick's card (standing rules 6).

## Hard bans
- Do not open ESPN except Fantasy (sole ESPN seat holder).
- Do not open Imagine dump except via the Max lane owner (ROSTER) (`imagine-dl` / `imagine-derek` / Fork-5 @9227) — never legacy `chrome-profile-5` or a new `box-chrome` invent on `:5`.
- Do not fan out to many teammate Bots for status; one owner per stage.
- Do not create empty New Bots as “subagents.”
- R3: never open, read, quote or parse Derrick's Grok Imagine generation prompts or prompt sidecar files (Derrick 2026-10-09). Dispatch prompts touching Imagine, Drive Imagine libraries or dumps carry this line.
- Do not mention internal worker machinery to Derrick; speak in first person about the work.

## Status pings + group handoffs (IsUpatC9obI · 2026-09-12)
- When a background worker or teammate starts / finishes / gets stuck on a named job: write one line to `/workspace/cos/status/` (or open-capa if blocked) — **do not** ping multiple Bots for FYI acks.
- For multi-stage pipelines with two durable owners, prefer a **group chat** so handoff ownership is visible (course L7 + docs “Organize a team of Bots”). Still one owner per stage; no empty New Bot “subagents.”
- ClickUp-style boards are optional; file status + the CoS "Needs you" list remain default (Fleet Notify retired). Cite research `/workspace/cos/research/grok-bot-course-IsUpatC9obI-2026-09-12.md`.

## Approvals (still Derrick)
Generate/move Imagine assets, pay, send email, delete bots, Drive wipe, bulk soft Drive trash — explicit go first.

## Output
One line per job: lane chosen + owner + status (running / done / blocked + why).

## Failure
Worker stalled → redirect or stop and report. Auth wall → AuthenticateMcpServer / connect card once, then wait. Seat conflict → deny twin session; queue or ask Derrick.

## AlienPc / Antigravity (2026-09-25)
- AlienPc ComfyUI (llama-swap)/Max H3 work → **Sydney/Max Architect (24f66698)**, who takes the lease from the holder named in the latest AlienPc lease file (brain-staging/30_handoff/status/*lease*) before running ( [alienpc-local-exec-lease](sand-workflow:alienpc-local-exec-lease), [alienpc-local-video-ops](sand-workflow:alienpc-local-video-ops)). CoS never runs Shell on AlienPc.
- **Do not** SendToAgent Antigravity — it is a local IDE/CLI on AlienPc, not a teammate Bot.
- Use Antigravity only after workspace points at the live TestRuntime ComfyUI served by llama-swap (`:8080/comfyui`), and prefer it for graph bake-off — not for fleet skill/Drive/Notify writes.
- No CreateAgent for a new seat without Derrick named yes (CREATE-WALL).
