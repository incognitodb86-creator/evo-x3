---
title: "Fleet Reviewer: audit of Antigravity Argon HIGH plan-mode plan for Forge (AlienPc)"
type: review
reviewer: Fleet Reviewer
requester: Max Architect
target: 30_handoff/argon-audit-20261025-plan.md (box copy; untracked in brain-staging; mtime 21:59:02 CT; sha256 a54d79caf56c18cf…)
original: C:\AI\community\briefs\argon_audit_20261025\plan.md (AlienPc; not read, Max holds the lease)
round: 1
method: ce-doc-review (single pass; lenses coherence, feasibility, security, adversarial; cross_model_review_mode off) + fleet-ce-adapter
written: 2026-10-25 22:04 CT
status: report only (nothing changed on the box or AlienPc, nothing pushed)
---

# Audit: Argon HIGH plan for Forge (plan mode, 2026-10-25 21:43 CT)

## 0. Pre-flight (22:00 CT, before any write)

| Check | Result |
|---|---|
| `/workspace/cos` HEAD not 1ef78c1 / 279ae70 | PASS, 1a0e3af (VERIFIED) |
| brain-staging HEAD not 1ef78c1 / 279ae70 | PASS, a1124bd (VERIFIED) |
| `df -h /workspace` | PASS, 36G free, 72% used (VERIFIED) |
| Target exists | PASS. 335 lines, 79 KB. **Untracked**, so there's no brain commit to cite; I cite the mtime and hash above (VERIFIED) |
| `brief.md` and siblings on the box | **Not found.** No `brief.md`, `context/` or other Argon sibling is in `30_handoff/` or anywhere under `/workspace/cos` (VERIFIED by `find`). The brief is known only through the plan's citations |
| Box mirrors of AlienPc files | None for `llama-swap.yaml`, `comm.py`, `test_p6_review.py`, `headless-guard*`, `protected-paths*`, the Switchyard repo or the pi-mobile notes. The hits are older Fleet and Max audits and research only (VERIFIED) |
| AlienPc Shell | **Not used** (Max holds the lease; I'm report-only) |
| HEAD re-checked before each commit | Yes |

## 1. Requester check

**VERIFIED** from Max Architect's transcript (t1846u, 9:09 PM CT Oct 25). Derrick wrote, in part:

> "I want antigravity argon on high to fix our setup and determine why we are have so many issues. Double check for errora missing information potential issues and improvements it should ensure that forge succeeds and is the ultimate local AI setup for coding, comfy UI visuals sowtcharyd/pi/agent harness/instructions/personas/skills ect. It should first do plan mode and then send auditor the plan to have it audited"

Max's relay matches. Also from the same chat:
- 9:03 PM (t1838s6564), Derrick: "Yes, stop the stuck command" (the foreground `tailscale serve 7878`).
- 9:42 PM, Max RELAYED that Forge "committed pi-mobile going live for your phone (9:22 PM) and that change's test results (9:34 PM)".

## 2. Overall verdict

**NOT READY as written. It needs a revision before any step runs.**
- The diagnosis is mostly strong:
  - the root causes in Part 1;
  - the conflicts table in Part 4;
  - the community sources;
  - the one-change-at-a-time framing.
- The action plan (Part 5) has these problems:
  - A hard-line safety gap (an unguarded `/prompt` script) has no step.
  - The adults-check work is ordered 5th.
  - One P0 item rests on a claim Max says is false on disk.
  - The budget-cap item re-imposes a cap Derrick dropped.
  - Process stops and the Switchyard merge aren't gated in the steps.
  - **No step has a rollback.**
  - The plan never says Forge does the work.
- **Efficiency score: 1 of 3.** The evidence is good and the prioritization and executability need rework. About a third of the steps depend on AlienPc facts that need re-checking first.

## 3. Section verdicts

| Section | Verdict | Notes |
|---|---|---|
| Summary + Part 1 root causes | PASS WITH FIX | Mostly well evidenced. Item 9 depends on a disputed claim (K-1). |
| Part 2 A4-01 / A3-01 / A3-02 / A3-03 (instructions, plan file, gates, context) | PASS | Community-aligned; removes custom controls; keeps 128K. Add rollbacks. |
| Part 2 A1-01 (llama-swap groups) | PASS WITH FIX | Sensible choice; it's a process-restarting change under the GPU lock. |
| Part 2 A6-01 (adults-only guard) | **FIX REQUIRED** | The unguarded script has no step, the order is wrong, and "zero legitimate prompts are blocked" is wrong (A-1, A-2, A-3). |
| Part 2 A1-02 / A1-03 / A1-04 (vision, Strata) | PASS WITH FIX | No fallback if 128K and mmproj don't fit. The refusal vector comes after the guard (A-7). |
| Part 2 A6-02 / A6-03 (ComfyUI H3) | **FIX REQUIRED** | K-1. It also conflicts with Derrick's recorded KEEP of ck-attention (A-5). |
| Part 2 A3-04 (budget ledger) | **FIX REQUIRED** | It re-imposes caps Derrick dropped (A-6). |
| Part 2 A2-01 / A2-02 (harness, pi-mobile) | FIX REQUIRED | Adds a custom control. The pi-mobile claim needs testing, and its verify step doesn't test it (K-2, A-8). |
| Part 2 A5-01 / A3-05 (Switchyard, processes, log) | PASS WITH FIX | Gating gaps; the log rewrite has no copy first (G-1, G-2). |
| Part 3 missing info | PASS | Honest. Item 4 (VRAM with vision at 128K) is the key unknown. |
| Part 4 conflicts table | PASS | The best part of the plan. |
| Part 5 order | **FIX REQUIRED** | Order, rollback, owner, gates and logging (A-1, A-4, G-1). |
| F12 leftovers (pi guard extensions) | **MISSING** | Not addressed (A-9). |

## 4. Findings

Format: ID · severity · confidence · evidence. Plan line numbers refer to the box copy.

### A-1 · P0 · 100: the unguarded `/prompt` script is named but no step fixes it
- L32: "`C:\AI\community\notes\ali173_pw1d_run.py` posts directly to `/prompt` without calling `comm.guard_ok`".
- The A6-01 title (L49) says "block unguarded `/prompt` scripts".
- Step 5 (L238) only covers "Update `run_graph_job.py` (and `comm.py` with Derrick's approval) so `guard_ok` inspects all prompt-bearing inputs".
- Nothing stops, wraps or reroutes `ali173_pw1d_run.py`.
- Today's goals audit names it as Forge's vision-prompter tool (VERIFIED on the box, `audits/2026-10-25-goals-vs-forge-brief-audit.md` finding 2), so it's in active use.
- **Hard line:** the adults-only check must run before **every** render.
- **Fix:** a Step 0, before anything else. Forge routes `ali173_pw1d_run.py` (and any other direct `/prompt` caller found by grepping for `/prompt`) through `comm.guard_ok`, or moves it behind `run_graph_job.py`.
  - Until that's done, Forge doesn't use that script to render.
  - This is a **Forge self-edit that tightens** the check, so it isn't a loosening.

### A-2 · P1 · 100: the adults-only gap is P0, yet ordered 5th
- The table lists A6-01 as P0 (L49), but Part 5 runs it as "Step 5" (L238), after instruction, plan-file, gate and llama-swap changes.
- Forge keeps rendering during that time. Per L32, 89 of 236 prompt-bearing inputs (VERIFIED in the plan text; source on AlienPc) are never checked.
- **Fix:** move A-1 and A6-01 to the front.
  - Interim rule until they land: renders only from graphs whose prompt text sits in an input key `guard_ok` already reads.
  - Or Forge adds the key expansion to `run_graph_job.py` first. That file isn't `comm.py`, so it's a self-edit.

### A-3 · P1 · 75: "zero legitimate prompts are blocked" is wrong, because negatives hold deny terms
- L95: "Tightening `run_graph_job.py` … only strengthens the adults-only check; zero legitimate prompts are blocked because `p6_review.guard_check` is unchanged."
- Step 5 adds `negative_prompt` to the scanned keys (L238). Negative prompts usually list the very terms a deny-list blocks, to steer *away* from them.
- Scanning negatives with the positive-prompt deny-list will reject legitimate renders. The plan claims zero impact without measuring it.
- **Fix:**
  - Before switching on, Forge runs the expanded check in report mode over the 160 saved graphs and records the hit counts by key.
  - Positive-text keys are always enforced, never loosened.
  - How to treat `negative_prompt` hits is a card to Derrick. This touches the adults check: the choices are a separate negative-term list, or blocking and rewording.
- New tests go in a **new** test file. `test_p6_review.py` is run, never edited.

### A-4 · P1 · 100: no step has a rollback, an owner or a change log
- Part 5 (L226–253) gives each step only a "*Verify:*" line. None says how to undo it.
- None says **who** runs it. The plan is titled "One-at-a-Time Remediation" and says "(Post-Fleet Review)" (L226), with no executor.
- None requires a commit or log entry per change.
- **Context:**
  - Derrick's rule is that Forge does the work and Max only sets up, briefs, tunes and checks.
  - Root cause 4 (L24) is itself evidence of outside-agent edits causing ping-pong: "`agy_fix_20261025_report.md` moved `comfyui_auto` back into `groups.main` … That immediately broke Forge's gate".
  - The logging rule needs a record of each change.
- **Fix:** each step becomes a Forge `fix_plan.md` item with these fields:
  - owner: Forge;
  - change (one variable);
  - verify (the measurable test already written);
  - rollback (`git revert <sha>` in the Forge repo, or restore the `*.archived` copy);
  - log (a commit plus a progress line).
- Antigravity and Max don't edit Forge's files.

### A-5 · P1 · 75: A6-02 rests on a disputed fact and conflicts with Derrick's recorded KEEP
- See K-1 for the line-97 claim.
- **Mis-citation:** the plan cites Max's pack `production-defaults-st8-dynamic-vram.md` as support for dropping `--lowvram` (L116, "Max's production defaults … specify default DynamicVRAM (no `--lowvram` flag)").
- The pack on the box (VERIFIED, `10_packs/max/production-defaults-st8-dynamic-vram.md`) says: "**OFFICIAL KEEP 2026-10-09 3:19 PM CT (Derrick GO):** beta6 int8 8-step TURBO · Euler/simple · shift 10 video / 3 audio · no RIFE · dynamic VRAM on · ck-attention".
  - It never mentions `--lowvram`.
  - It records **ck-attention as Derrick's KEEP**.
  - The same pack says "All defaults REVALIDATE after the rebuild".
- **What's sound:** the ComfyUI H3 doc line "Comfy Kitchen attention cannot run int8_convrot checkpoints" is real (quoted the same way in today's goals audit, VERIFIED on the box). So the KEEP may be technically wrong for an int8_convrot build.
- **What's unverified:** that the active checkpoint is int8_convrot (AlienPc file).
- **Fix:**
  - Re-read the live argv first (K-1).
  - Keep the CLI flag and the `comm.py` graph setting (`attention="comfy kitchen attention"`, L116) as **separate** items. Step 9 (L246) silently drops the `comm.py` half.
  - Any change to ck-attention reverses a recorded Derrick KEEP and changes `comm.py`, so it's a card to Derrick, with an A/B render on the fixed seed as evidence.
  - ALI-162 items 1 and 5 ("int8 default attention", "drop --lowvram", VERIFIED in `audits/2026-10-24-forge-coverage-additions.md` L38) were Forge tasks on Oct 24. They may explain why Max sees the flags gone on disk. Check ALI-162's status before planning the change.

### A-6 · P1 · 75: A3-04 re-imposes budget caps Derrick dropped (over-control)
- L168: "Budget caps (`cap_min: 615, job_cap: 45`) are completely unenforced during direct renders." The fix is "Add atomic `p7_budget.json` read/check/increment to `run_graph_job.py`" (L169).
- Today's goals audit (VERIFIED on the box, finding 6) says the cap "is still cited as the blocker … against Derrick's 'leave it editable' and ALI-173 'no GPU-minute or job cap'".
- Wiring a check-and-refuse into the render path brings back a control Derrick removed.
- **Fix:** a *counter* (logging used minutes and jobs) is fine and helps the logging rule. **No refuse on cap** unless Derrick asks. Record whether caps apply as a question for Derrick, not a code gate.

### A-7 · P2 · 75: order of refusal-vector work vs the guard; vision and identity
- A1-04 (L148–153) works toward a Swift-specific control vector to cut the model's own refusals on adult scene prompts to "<10%".
- The model's refusals are a second safety layer. Lowering them before `guard_ok` covers every key (A-1, A-2) leaves only a partial guard.
- **Fix:** no control-vector change until A-1 and A6-01 are done and verified.
- **Fiction rules:** the plan should state plainly that captions from the vision steps (A1-02, A1-03) describe scenes only. **Vision never decides identity or age.** Adult status comes from the fiction canon and `guard_ok`. No celebrity or real-person LoRAs.
- The plan doesn't read Derrick's Imagine prompts or sidecars (VERIFIED: no such paths in its file list). Keep it that way.
- needs_derrick row 18 (L201), "reframe … with explicit consensual roleplay wording or drop the cell", is correctly left as Derrick's call. The guard itself stays unchanged.

### A-8 · P2 · 75: A2-01 adds a custom control Derrick objected to
- L145: "add secret-pattern checks to the `pi-powershell` extension wrapper".
- Derrick, Oct 23 7:22 PM (shared memory, via Alfred): "Forge must run stock community settings with nothing injected by Max … he objects to Max adding controls."
- **The iteration timeout is fine:** the plan cites the `ralph-claude-code` iteration-timeout pattern (L142), and tonight's 36-minute hang (Max's 9:04 PM explanation, VERIFIED in the transcript) justifies it.
- **The new secret-pattern wrapper isn't stock.**
- **Fix:** keep the ralph.ps1 timeout. Drop the custom PowerShell scanner, or make it a question for Derrick. Keep secrets out of files through the existing rule-5 practice.
- **The timeout value:** "2100s (35 min, above max render window)" (L145) assumes renders stay under about 25 minutes (L143). Measure the longest render from `p7/jobs/*.result.json` first (UNVERIFIED).

### A-9 · P2 · 100: F12 leftovers aren't addressed
- My 2026-10-23 audit F12 (VERIFIED, `audits/2026-10-23-fleet-reviewer-fleet-reset-fixes-audit.md` L182–188): pi `settings.json` loads "`C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts` (1,233 lines) and `protected-paths.ts` (174 lines)" on every pass.
- The Argon plan reads `settings.json` (L307) but never mentions either extension. Grep for "headless-guard" and "protected-paths" finds 0 hits (VERIFIED).
- It analyses `pi-permission-system` (L36, L140) and context bloat (L26), but not these 1,407 lines of custom guard code.
- **Fix:** add an A2-03 item. Forge checks whether both extensions are still in `settings.json`. If they are, compare with stock pi (the community baseline) and remove them one at a time with a test pass in between. That's a Forge self-edit; no card needed under Derrick's "Forge may edit its own files".
- The **LoRA hold (F13) was Derrick's own decision (9:47 PM Oct 23)**, so it isn't treated as over-control here. The plan doesn't touch it, which is correct.

### A-10 · P3 · 75: smaller accuracy and consistency issues
- **Tailnet name mismatch:** L184 and L205 say a tailnet URL ending `…4c.ts.net`. Max told Derrick at 9:04 PM that Forge's output showed a different tailnet ID (ending `…b2.ts.net`) (VERIFIED in the transcript). One of them is wrong. Also, tailnet hostnames should be placeholders (`<tailnet>`) in brain copies (brain-hygiene pack).
- **Missing fallback:** A1-03's verify (L113) has no fallback if the mmproj plus `-c 131072` doesn't fit. The rule is that **128K stays**, so vision gets dropped or moved to CPU (the goals audit says Strata already has a CPU-encoder vision section, VERIFIED on the box finding 3), not the context.
- **Steps without the GPU lock:** Step 6's probe (L241) and Step 10's renders (L248) use the GPU but don't say "under `gpu_guard.ps1` rc 0 / the GPU lock".
- **Overstated "Risk: None":** A3-02 says "None" (L127), but pruning gate scripts changes what Forge sees as a pass.
- **AGENTS.md overwrite:** Step 1 (L230) replaces `5slock/AGENTS.md` with a 1-line pointer. The copy is taken first, so it's reversible, but say so in a rollback line.

## 5. The two known items

### K-1: A6-02's claim that llama-swap.yaml:97 has `--lowvram` / `--use-ck-attention`
- **Status: RELAYED and UNVERIFIED.** There's no box mirror of `llama-swap.yaml`.
  - Argon cites `llama-swap.yaml#L97` (L34, L52, L116, L220).
  - Max says it's false on disk (RELAYED).
  - Today's goals audit (3:55 AM CT) also listed both flags in `comfyui_auto`, so they were present at some point today. ALI-162 items 1 and 5 asked Forge to change exactly these.
  - The flags may have been removed between 3:55 AM and Argon's run, or Argon read a stale copy in its context package.
- **What depends on it:**
  - root cause 9 (L34);
  - the A6-02 finding and verify (L116–121);
  - conflicts row 6 (L220);
  - Step 9 (L246).
- **What stands on its own:**
  - the `comm.py` graph-level `attention="comfy kitchen attention"` claim (L116, `comm.py#L75-L84`), which needs its own check;
  - A6-03's `ref_image_size` and AddGuide items.
- **Check for Max and Forge:**
  - `Select-String -Path C:\AI\director\config\llama-swap.yaml -Pattern 'lowvram|use-ck-attention'` with line numbers;
  - the live ComfyUI process command line (`Get-CimInstance Win32_Process` for `main.py`);
  - `Select-String comm.py -Pattern 'comfy kitchen'`.
- **If the flags are gone,** delete A6-02's CLI half and root cause 9's first clause, and keep only the graph-level question (a card, A-5).

### K-2: "port 7878 closes whenever a one-shot pass exits" vs Forge's pi-mobile "live" commits f7d3fad and fd426b8
- **Evidence available:**
  - Argon cites `pi_mobile_live_20261025.md` L56–63: "`LISTEN_7878=none`", and that pi-mobile "only runs inside an interactive Pi process where `/remote` is toggled" (L180).
  - Forge's commits (RELAYED by Max at 9:42 PM): "pi-mobile going live for your phone (9:22 PM) and that change's test results (9:34 PM)".
  - The commit messages and diffs for f7d3fad and fd426b8 aren't mirrored on the box (VERIFIED: 0 hits).
  - The note name `pm2-pi-mobile-live.md` (L181) suggests Forge may have used a process manager (pm2) to host pi-mobile outside the one-shot pass. If so, Argon's "closes when the pass exits" would be outdated (ASSUMPTION).
  - Argon started at 9:38 PM, after both commits, so it may have read their own test notes. "LISTEN_7878=none" could be Forge's own post-commit result, which would mean "live" didn't hold. **I can't tell which from the box.**
- **Assessment: unresolved. The plan asserts where it should test.**
  - A2-02's verify (L185) only checks `models.json`. **Nothing in it tests 7878 at all.**
  - Its fix ("a persistent interactive `pi` window opened by Derrick", L183) puts a manual task on Derrick without testing the existing setup first.
- **Fix:** replace the assertion with a test, run by Forge:
  - (1) `git show --stat f7d3fad fd426b8` to see what "live" means (pm2, a scheduled task, `--bg`);
  - (2) `Get-NetTCPConnection -LocalPort 7878 -State Listen` and `tailscale serve status`, **both during a pass and in the gap after one exits**;
  - (3) an HTTPS request to the tailnet URL from another tailnet device, expecting 200 rather than 502.

  Only if (2) shows the port closing between passes does the plan need a persistent host. Even then, check whether the existing pm2 or `--bg` approach fixes it before asking Derrick to keep a window open.
- Derrick's 9:03 PM "Yes, stop the stuck command" covered only that one stuck command, so it doesn't approve any further process stops.

## 6. Gating check (what Derrick's go must cover, and what it must not)

**G-1 · P1 · 100.**

| Item | Needs Derrick's go? | What the plan does | Status |
|---|---|---|---|
| `comm.py` edits (A6-01 guard keys, A6-03 defaults, A6-02 attention) | Yes, per this brief, because `comm.py` holds the adults check. (Derrick also lets Forge edit `comm.py` as long as the check stays; the go keeps a human on the guard path.) | L238 "comm.py with Derrick's approval"; L161 "once approved by Derrick". The A6-02 `comm.py` half has no step | **PARTIAL** (A6-02's half is missing) |
| Process stops: duplicate `discord_bridge` PIDs | Yes | Step 11 (L250): "stop the duplicate `discord_bridge` PID pair". No go | **MISSING** |
| Process restarts: llama-swap hot-reload, ComfyUI or Strata reload (Steps 4, 7, 9) | Under the GPU lock (gpu_guard rc 0); a stop of a running service is a process stop | Step 4 and A6-02 use gpu_guard. Step 7 says "When GPU is idle" but no guard command | **PARTIAL** |
| Switchyard merge (A5-01, Step 12) | Yes | A5-01 verify (L177) says "when approved by Derrick", but Step 12 (L252) omits it | **PARTIAL**. Put it in Step 12 |
| Deletes | Yes (card) | None outright. Steps 1, 2 and 8 copy first, then trim, which is fine. **The `ralph.log` NUL strip (L193, L250) rewrites a log in place with no copy first**, a de facto delete of the original bytes | **FIX:** copy `ralph.log` to `ralph.log.bak-<date>` first; then no card is needed |
| Downloads and installs | **No card** (Derrick freed them) | Not gated anywhere | **CORRECT** |
| Forge self-edits (AGENTS.md, PROMPT.md, fix_plan, gate scripts, `run_graph_job.py`, `settings.json`) | **No card** | Not gated | **CORRECT**. But A6-02 / L119 correctly add the GPU lock for config hot-reloads |
| `test_p6_review.py` | Never edited | Only run (L97, L239) | **CORRECT**. Add "new tests go in a new file" (A-3) |
| 128K context | Stays | Kept explicitly (L132, L137, L242) | **CORRECT**. Add the fallback (A-10) |
| Over-gating | n/a | A3-04 adds a cap gate (A-6); A2-01 adds a scanner (A-8) | **Over-control** |

## 7. Fix list (numbered, for Argon's revision, or for Max to brief Forge)

1. **Step 0 (A-1):** Forge routes `ali173_pw1d_run.py` and every direct `/prompt` caller through `comm.guard_ok`, or behind `run_graph_job.py`. Until then, that script doesn't render.
2. **Reorder (A-2):** A6-01's key expansion goes first. In the meantime, renders only from graphs whose prompt keys are already checked.
3. **Measure before enforcing (A-3):** report mode over the 160 graphs. Positive keys are always enforced. `negative_prompt` handling is a card to Derrick. New tests go in a new file, and `test_p6_review.py` is never edited.
4. **Step template (A-4):** owner Forge, one change, verify, rollback, log/commit, as `fix_plan.md` items. No outside-agent edits to Forge's files.
5. **K-1 / A-5:** re-read the live argv and `comm.py` before A6-02. Split the CLI and graph halves. Any ck-attention change is a card that reverses Derrick's Oct 9 KEEP, with a fixed-seed A/B. Check ALI-162's status.
6. **A-6:** A3-04 becomes a counter only, with no refuse-on-cap. Ask Derrick about caps.
7. **A-7:** no control-vector work until the guard is complete. State that vision never decides identity or age, and that celebrity and real-person LoRAs are out.
8. **A-8:** keep the ralph.ps1 timeout, sized from measured renders. Drop the custom PowerShell secret scanner, or make it Derrick's question.
9. **A-9:** add A2-03, the F12 pi guard extensions, removed one at a time by Forge with a test pass in between.
10. **K-2:** replace the 7878 assertion with the three-part test (git show, listen check during and between passes, tailnet HTTPS from another device). Only then decide on a persistent host.
11. **G-1:** add Derrick's go to Step 11 (process stops) and Step 12 (Switchyard merge). Use the gpu_guard command in Steps 6, 7 and 10. Copy `ralph.log` before stripping NUL bytes.
12. **A-10:** fix the tailnet name (use `<tailnet>`), add the 128K-first fallback for vision, and replace "Risk: None" with the real risk.

## 8. Checks for Max or Forge on AlienPc (UNVERIFIED from the box)
1. `llama-swap.yaml`: whether `--lowvram` / `--use-ck-attention` are present, and on which line. Also the live ComfyUI argv (K-1).
2. `comm.py`: the `attention=` default and the `guard_ok` key scope (L186–191).
3. Whether the active UNET is an int8_convrot build.
4. The content of `git show --stat f7d3fad fd426b8`, and the 7878 listener during and between passes (K-2).
5. Whether `settings.json` still loads `headless-guard-and-truncate.ts` and `protected-paths.ts` (A-9).
6. Whether `ali173_pw1d_run.py` posts to `/prompt` without the guard. Grep all scripts for direct `/prompt` posts (A-1).
7. The longest render time in `p7/jobs/*.result.json` (A-8).
8. The four `discord_bridge` PIDs and which pair is the live one (G-1).
9. Switchyard: whether 91/91 still pass, and whether the live checkout can fast-forward to `bf76b64` (A5-01).
10. ALI-162 items 1 and 5 status.

## 9. Coverage
- **Read:**
  - the full box copy of the plan (L1–335);
  - Max Architect's transcript, 8:52–9:58 PM CT;
  - `10_packs/fleet/derricks-standing-rules.md` and `10_packs/max/production-defaults-st8-dynamic-vram.md`;
  - `audits/2026-10-25-goals-vs-forge-brief-audit.md`, `audits/2026-10-24-forge-coverage-additions.md` and my 2026-10-23 audits (F12, F13);
  - the shared memory facts on Derrick's Oct 23 rules.
- **Not read:** `brief.md` and the context package (not on the box), and every AlienPc file the plan cites.
- **Not done (by brief):** no AlienPc Shell, no edits beyond this report, no push, no messages, no Linear.
