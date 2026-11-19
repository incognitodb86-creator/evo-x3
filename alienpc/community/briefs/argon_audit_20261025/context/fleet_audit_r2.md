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

---

## Round 2 (2026-10-25, 23:05 CT): plan v2

Reviewer: Fleet Reviewer, ce-doc-review single pass (coherence, feasibility, security, adversarial), report only, for Max Architect.

### R2-0. Pre-flight (VERIFIED, 23:01 CT)
| Check | Result |
|---|---|
| `/workspace/cos` HEAD | 52a179d (not 1ef78c1 / 279ae70) |
| brain-staging HEAD | 58dff9a (not a stale marker) |
| `df -h /workspace` | 36G free of 128G (28% free), above 10 GB / 15% |
| Target `30_handoff/argon-audit-20261025-plan-v2.md` | Exists, untracked, mtime 23:00 CT, **39,882 bytes, sha256 d38c1df50519f867…** (matches Max's d38c1df5… and size) |
| `revise_brief.md` on the box | **Not present** (VERIFIED by `find /workspace`); known only via v2's citations (v2 L11, L49) |
| AlienPc Shell | Not used (Max holds the lease) |
| HEAD re-checked before commit | Yes |

### R2-1. Derrick's words (VERIFIED, ReadTranscript of Max Architect's chat)
- 9:09 PM (t1846u): the original ask; verified in round 1 §1.
- 10:14 PM, answering "What next for Argon's plan?": **"Have Argon high revise the plan in plan mode using Fleet Reviewer's audit, then send it back for another audit"**.
- 10:15 PM (t1854u): **"I don't remember those kitchen attention? I want best practices and community guidance? Geared on what works best on my setup"**.
- 10:16 PM (t1855u): **"After it passes the audit have antigravity flash high implement all the changes and setup forge and optimize or whatever"**, then (t1856u) "Ok cool".
- 10:17 PM (t1857u): **"Community adults only. I want community fucking swttings"**. Context (VERIFIED): Max's message just before it said "how negative prompts get handled by the stricter adults-only check is your call ... I'll ask you about that one item before Flash high starts." So 10:17 is his reply to the negative-prompt question, not a general rule.
- Also relevant, 6:48 PM, answering "Which of these should I hand Forge in your words?": **"Sort out the Comfy Kitchen attention conflict"** and **"Go back to Euler, 5-second clips and 350–500 word prompts"** (VERIFIED).
- Shared memory (RELAYED via Max, 2026-10-19 9:04 AM CT): "if i made any descision that odesn match communit best pracitces we should change it"; and (via Max, 2026-10-16): "When the community way is clear, just switch to it — don't turn it into an A/B against our custom path."

### R2-2. What these mean
- **A-5 (ck-attention).** Derrick doesn't remember choosing it, asked at 6:48 PM to sort out the conflict, and wants community best practice for his setup. Under his Oct 19 rule the Oct 9 KEEP of ck-attention is **superseded**, not reversed by a new KEEP. Rule 4's card is for setting a KEEP, so **no card is needed** to move `comm.py` to the community default (`"pytorch attention"`, the H3 docs' default). What is needed: one fixed-seed check render on 51150011 that the new default runs and isn't visibly broken, and a logged decision: Forge's `progress.md` plus a "superseded 2026-10-25" line in Max's `production-defaults-st8-dynamic-vram.md`, which Max edits. That's a check, not an A/B debate (Oct 16). A card only if the check render fails or is clearly worse. Confidence 75.
- **"Community adults only."** It answers the negative-prompt question with "the community way, adults only". It doesn't loosen anything: the adults-only check stays on before every render, strict on every prompt-bearing input. The reading that fits his words is community-standard negatives (artifact tokens, as in the official H3/Wan negatives) with `guard_ok` unchanged. But it touches the hard limit and is two words, so the Continuum `no:` rewrite should get **a one-line confirm** before it lands (see N2-3), not a design card.
- **"Rule" labels.** v2 calls both messages "rules" (L11 "Derrick's 10:15 PM and 10:17 PM CT rules", L22 "per Derrick's 10:17 PM rule", L50 "Hard Line 3 & Derrick 10:17 PM rule", L57, L88, L155). It doesn't change the `guard_ok` strictness ("`guard_ok` stays 100% strict", L17, L50), so the guard isn't loosened. But Step 1 uses the 10:17 words to settle the negative-line question that v2 itself still lists as Derrick's card (L75). Fix: quote them as his 10:15 and 10:17 answers, not rules.
- **10:16 is a go.** Once v2 passes this audit, it is Derrick's go for the reversible changes, including the reversible `comm.py` guard-scope tightening that round 1 G-1 gated. It doesn't cover KEEP changes, deletes, process stops, the Switchyard merge or anything irreversible (rule 4). It also names **Antigravity Flash High as the implementer** (N2-1).

### R2-3. Item status
| Item | Status | v2 evidence |
|---|---|---|
| A-1 unguarded `/prompt` | CLOSED | Step 0 L98-103: "run `comm.guard_ok` on `SHORT_PROMPT` and every string in `graph` before `post("/prompt", ...)` ... exiting `3`"; L15 "unused until Step 0 lands"; grep of all callers L15 |
| A-2 ordering | CLOSED | L16 "Interim rule: no renders run until Steps 0–1 pass verification" |
| A-3 negatives | PARTIAL | Report mode done (L17: 164 graphs, 2 hits on `PrimitiveStringMultiline.value`); new test file, `test_p6_review.py` sha pinned (L108). But Step 1 rewrites the `no:` lines (L107) while L75 still lists that as Derrick's card (N2-3) |
| A-4 template, owner | PARTIAL | Template on every step (L18, Steps 0-12). Owner "Forge" and "Antigravity and Max do not edit Forge's files" (L96) conflicts with Derrick's 10:16 words (N2-1). "One change" is broken in Steps 1, 6, 9, 10, 11 (N2-8) |
| A-5 ck-attention vs KEEP | PARTIAL | CLI half dropped, graph half kept as Step 8 (L19, L154-159); ALI-162 noted. Premise "int8_convrot" contested (N2-6); gating should follow R2-2 |
| A-6 budget cap | CLOSED | L20, L60, Step 10 (2) "counter only, never refusing a render" |
| A-7 vector order, vision | CLOSED | L21 "vision never decides identity or age ... celebrity/real-person LoRAs are prohibited"; Step 11 gate L176 |
| A-8 scanner, timeout | PARTIAL | Scanner dropped (L22, L169). Timeout 4500s rests on "3,048s" (L22), **not checked** (RELAYED-from-Max); kill semantics missing (N2-7) |
| A-9 F12 extensions | CLOSED (v2 claim) | L23, L66, Step 2 verify L115. The disk state is v2's claim; not confirmed by Max or me |
| A-10 smaller issues | CLOSED | `<tailnet>` used (no tailnet host in v2, VERIFIED by grep); CPU vision fallback Step 7; A3-02 risk L53; Step 2 rollback L116 |
| K-1 llama-swap flags | PARTIAL | CLI half CLOSED: 0 hits and no live ComfyUI (L19; RELAYED-from-Max agrees). v2's header quote `"convrot": true` (L19, L40) is **contradicted** (RELAYED-from-Max: 195 `comfy_quant` entries, no "convrot" string) |
| K-2 pi-mobile 7878 | PARTIAL | Assertion replaced by a test (L24, L63, Step 11 L177). Result matches Max (RELAYED-from-Max: listens only during a pass, PIDs 5956/21476, gap 22:22:45-22:28:22). Part (3) is only "status", not an HTTPS request from another device; no decision on reach between passes (N2-10) |
| G-1 gating | PARTIAL | `discord_bridge` stop on GO (L183), `ralph.log` copy first (L184), `gpu_guard` in Steps 5-9, 11. Switchyard "already merged" (L25, L65, L184) is wrong (N2-5) |
| Fix 1 | CLOSED | = A-1 |
| Fix 2 | CLOSED | = A-2 |
| Fix 3 | PARTIAL | = A-3 |
| Fix 4 | PARTIAL | = A-4 |
| Fix 5 | PARTIAL | = K-1 / A-5 |
| Fix 6 | CLOSED | = A-6 |
| Fix 7 | CLOSED | = A-7 |
| Fix 8 | PARTIAL | = A-8 |
| Fix 9 | CLOSED | = A-9 |
| Fix 10 | PARTIAL | = K-2 |
| Fix 11 | PARTIAL | = G-1 |
| Fix 12 | CLOSED | = A-10 |

### R2-4. New findings
**N2-1 · P1 · 100. Who implements.** L96: "Every step below is executed **by Forge** ... Antigravity and Max do not edit Forge's files." Derrick at 10:16 PM: "have antigravity flash high implement all the changes and setup forge". His latest words govern over the standing "Forge does the work" and round 1's A-4 line. Fix: Part 5 says Flash High implements each step, in order, under Max's AlienPc lease and `gpu_guard.ps1` rc 0 for anything GPU. It commits in the Forge repos with the step ID and logs each change in Forge's `notes/progress.md`, so Forge's history and `fix_plan.md` stay the record.

**N2-2 · P1 · 100. Step 9(b) contradicts Derrick's explicit pick.** L163: "(b) `sampler_name: "res_multistep"`". Derrick at 6:48 PM: "Go back to Euler" (VERIFIED). The Oct 9 KEEP also says Euler/simple. Even under the community-first rule, he picked Euler four hours ago in his own words. Fix: drop 9(b), or make it a card that says plainly "community docs suggest res_multistep; you picked Euler at 6:48 PM". 9(a) can go ahead (community defaults, no KEEP conflict).

**N2-3 · P1 · 75. Step 1 is two changes and settles an open card.** L107 bundles three things: the key-scope expansion, the Continuum `no:` rewrite ("use artifact-avoidance tokens only on `no:` lines"), and new tests. L75 still lists "Continuum `no:` avoidance lines omit banned tokens ... vs a separate negative-key rule" as Derrick's sign-off. Doing the rewrite inside Step 1 implements one card option before he signs it, so it is a gate bypass. The rewrite also removes the "no: ... minors, underage" avoidance terms (L17), which is a generation-side safety steer even though the guard stays strict. Fix:
- Split it. **Step 1a:** expand the scope in `run_graph_job.py`, plus `comm.py` (a reversible tightening, covered by 10:16 once this passes), plus `tests/test_guard_scope.py`. Graphs that now hit are blocked, which fails closed.
- **Step 1b:** the Continuum `no:` rewrite, after a one-line confirm from Derrick. Suggested wording: "Community negatives: artifact-only `no:` lines; the adults-only check stays strict on every prompt input. OK?"

**N2-4 · P1 · 75. Step 6 edits `p6_review.py`, which holds the adults check.** L142: "pass `reasoning_effort="none"` ... when calling `vl_judge` / `qwen3vl_judge` in `p6_review.py`". `p6_review.guard_check` is part of the guard path (round 1 A-3). Step 6 also bundles a Strata config change (`max_tokens` 300 → 3000) with a judge-call change in another repo. Fix:
- Split into 6a (the Strata `max_tokens` change) and 6b (the judge calls).
- 6b touches only the judge request parameters, never `guard_check`.
- 6b's verify adds `pytest test_p6_review.py test_guard_scope.py` and the `test_p6_review.py` sha check (as in L108).
- If any VL judge output feeds an age or identity decision, stop: vision never decides identity or age.

**N2-5 · P2 · 100 (RELAYED-from-Max). Switchyard is not merged.** L65: "`switchyard-upgrade/repo` (`d9efd2f..b6384bc`) is **already merged** in `C:\AI\director`". Max reports d9efd2f is in director and b6384bc is not. Step 12 (L184) would then tell Derrick he is "awaiting only Derrick's GO to enable" flags. Fix: Step 12 records the true state. The merge is its own step and needs Derrick's go; enabling the flags is a separate go after the merge, with `pytest` re-run.

**N2-6 · P2 · 75 (RELAYED-from-Max). The int8_convrot premise is unverified.** L19 and L40 quote `"convrot": true` from the safetensors header. Max finds no "convrot" string. Fix: A6-02's reason becomes "the H3 docs' default is `pytorch attention`; community default for this setup" (R2-2), not "Comfy Kitchen cannot run this checkpoint". Drop or correct the header quote. Re-read the header in Step 8's first line and log the result.

**N2-7 · P2 · 50. The 4500s timeout needs kill semantics and a real basis.** L170 wraps `pi` in a 4500s job "`> 3,048s` max render ... `+ 1,200s` queue". The 3,048s longest render isn't checked (RELAYED-from-Max), and a pass can run more than one render. A timeout that kills only `pi` can leave `run_graph_job.py` and a queued ComfyUI job running with `gpu-render.lock` held. Fix:
- Measure from the result files first.
- Size the timeout per pass: renders per pass × longest render, plus queue time.
- The timeout kills the whole process tree, then runs `comfy_graceful_stop.ps1` (it exists, L195) or checks the lock is released.
- Verify with a forced short timeout on a dry pass.

**N2-8 · P2 · 75. Judgment gaps for Flash High.**
- Step 0 does two things: adding the guard and rerouting `:10004` → `comm.BASE` (`/comfyui`, through llama-swap). Keep the reroute, but say why (community single-GPU swap, L36) and verify with one guarded dry submit.
- Step 9(a) changes `ref_image_size` and adds `MiniMaxH3AddGuide` in one render. That's two variables; split them.
- Step 10(1) says "disable unused web/marketing skills" but doesn't name them. List them by name.
- Step 11 (1) says "sync `args` with `args_written`" without saying which one is right, and "any Swift control-vector sweep" is open-ended. Name the target values, or move the sweep to a later plan.
- Step 4's verify "exits 0 in `<10s`" may be unrealistic with pytest plus `rt_window_probe`; use rc 0 and log the time.
- Step 2's F12 verify checks only `.pi\agent\settings.json`; also check `config\pi\settings.json` (L23 cites both).

**N2-9 · P3 · 75. The "rule" wording** (R2-2). Relabel L11, L22, L50, L57, L88, L155 as Derrick's 10:15 and 10:17 PM answers, quoted.

**N2-10 · P3 · 75. pi-mobile between passes.** v2 confirms `:7878` exists only during a pass (L24) but proposes nothing for the gaps. The Serve route on 8443 then has nothing behind it, so the phone gets an error between passes (ASSUMPTION: 502). Making it persistent means a new always-on daemon that exposes an agent-control surface on the tailnet. Under rule 1 (no daemons unless Derrick asks) that is **Derrick's choice**. Fix: add a short card: "pi-mobile works only while Forge is in a pass. Keep it that way (default), or run it persistently?" Also make part (3) a real HTTPS request from another tailnet device.

**N2-11 · P3 · 50. Header times.** L3 shows "22:47 CT (`2026-10-25T22:19:33-05:00`)", two different times. Nit.

### R2-5. Standing rules check
- **Adults-only check never loosened:** HOLDS. `guard_ok` stays strict (L17, L50), and the scope only widens. Watch the Step 1b negative rewrite (N2-3) and the Step 6 `p6_review.py` edit (N2-4).
- **`test_p6_review.py` never edited:** HOLDS. Run only, sha pinned (L106, L108).
- **No secrets:** HOLDS. The v2 grep found no emails, tailnet hosts or tokens; only 127.0.0.1.
- **No deletes:** HOLDS. Every trim copies first (Steps 2, 3, 10, 12); nothing is removed outright.
- **128K stays:** HOLDS (Step 7 L148, Step 10 L59).
- **One change at a time from the community baseline:** PARTIAL. Steps 1, 6, 9, 10 and 11 bundle changes (N2-3, N2-4, N2-8).
- **Who does the work:** see N2-1. Derrick's 10:16 words name Flash High.
- **No new controls Derrick objected to:** HOLDS. The scanner and the cap are dropped; the counter is logging only.
- **Fiction rules:** HOLDS. No Imagine prompts or sidecars read (v2 file list, L191-200); vision never decides identity or age (L21); no celebrity LoRAs.

### R2-6. Readiness for Antigravity Flash High
- **Ready once N2-1 (the executor line) is fixed:** Step 0, Step 1a (N2-3 split), Step 2 (add the `config\pi\settings.json` check), Step 3, Step 4, Step 5, Step 7.
- **Ready after a text fix, no card:**
  - Step 6 (split, keep the guard untouched, N2-4);
  - Step 8 (fix the convrot premise; one check render plus a logged "KEEP superseded" decision, R2-2);
  - Step 9(a) (one variable per render);
  - Step 10 (name the skills; timeout kill semantics after measuring, N2-7);
  - Step 11 (name the `args` target; part 3 HTTPS; the vector sweep deferred or defined);
  - Step 12 (true Switchyard state).
- **Need Derrick's card or confirm:**
  - Step 1b, the Continuum `no:` rewrite (one-line confirm);
  - Step 9(b), `res_multistep` vs his 6:48 PM "Go back to Euler";
  - the Switchyard merge, and later the flag enable;
  - a `discord_bridge` stop (only if he wants it);
  - pi-mobile persistent or not (N2-10);
  - the pi-mobile QR pairing (his own action, L77).
- **Must not start before Steps 0-1a are verified:** any render (L16), and Step 11's vector work (L176).

### R2-7. Round 2 verdict: READY WITH FIXES
The plan is close. The safety items are fixed and ordered first, and the over-controls are gone. Before Flash High starts, apply the fixes below to v2, or have Max carry them in Flash High's brief.

Fix list (in order):
1. **N2-1:** name Flash High as the implementer (Derrick 10:16 PM), committing in the Forge repos with step IDs and logging in `progress.md`, under the AlienPc lease and the GPU lock.
2. **N2-3:** split Step 1 into 1a (scope plus tests, now) and 1b (the `no:` rewrite, after a one-line confirm).
3. **N2-2:** drop Step 9(b), or make it a card naming the 6:48 PM Euler pick.
4. **N2-4:** split Step 6; `guard_check` untouched; add the guard tests and the sha check to its verify.
5. **N2-5:** correct the Switchyard state; the merge needs Derrick's go.
6. **N2-6 and R2-2:** Step 8 rests on the community default, not convrot. No card: one check render, then a logged "Oct 9 KEEP superseded" decision (Max updates his pack line).
7. **N2-7:** measure the longest render and renders per pass; the timeout kills the process tree and frees the GPU lock.
8. **N2-8:** split 9(a); name the Step 10 skills; define Step 11's `args` target and defer the vector sweep; fix the Step 2 and Step 4 verifies.
9. **N2-10:** a pi-mobile persistence card; a real HTTPS check from another device.
10. **N2-9 and N2-11:** relabel the "rules" as quoted answers; fix the header time.

Efficiency score (round 2): 2/3.

### R2-8. Verified vs not
- **VERIFIED:**
  - the v2 file hash and size;
  - Derrick's 6:48, 10:14, 10:15, 10:16 and 10:17 PM words and the 10:17 context;
  - v2's text and line numbers;
  - the standing rules file;
  - no secrets in v2.
- **RELAYED-from-Max:**
  - K-1's llama-swap hits (0) and no live ComfyUI;
  - `comm.py:75/123` still set ck-attention;
  - no "convrot" string in the header;
  - the 7878 PIDs and the gap times;
  - Switchyard b6384bc not in director;
  - the 3,048s render not checked.
- **RELAYED (shared memory):** Derrick's Oct 16 and Oct 19 community-first wording.
- **UNVERIFIED (AlienPc only):**
  - every AlienPc path, line and count v2 cites (164 graphs, the F12 renames, the `discord_bridge` chain, 20/20 Switchyard tests);
  - whether the VL judges feed any age or identity decision.
- ASSUMPTION: the Serve route returns 502 between passes.
- `revise_brief.md`: not on the box.

Report only. Nothing changed on the box (beyond this report) or AlienPc; not pushed.
