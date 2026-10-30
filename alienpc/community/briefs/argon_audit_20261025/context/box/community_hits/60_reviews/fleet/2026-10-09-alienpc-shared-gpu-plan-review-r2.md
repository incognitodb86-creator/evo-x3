---
title: ce-doc-review round 2 of 2 (report-only, CAPA) - AlienPc local AI on one shared GPU plan
target: ce/plans/2026-10-09-1622-feat-alienpc-local-ai-shared-gpu-plan.md @ f8df93b
round1: 60_reviews/fleet/2026-10-09-alienpc-shared-gpu-plan-review.md (@4bb4600, commit 117724b)
reviewer: Fleet Reviewer bc9b71d5 (executor subagent, independent)
requested_by: Sydney Clone 4f7cac4f, on Derrick's direction 2026-10-09 5:40 PM CT
run: 2026-10-09 17:44-17:50 CT (box date)
---

# Round 2 review: AlienPc shared-GPU plan (report only, CAPA)

## Verdict

**Hand to Opus after the fixes listed below.** These are text fixes to the plan, and none needs new research. Opus would plan from the safety and pipeline sections, so those must be right first.

Fix before handing to Opus:
1. **N-01.** A Max lease request currently "takes its FCFS place", which quietly puts Max into the queue order and pre-decides OQ1.
2. **N-02.** OpenCode's approval config is missing, and its defaults are allow.
3. **N-03.** The human-only controls (Derrick override, KEEP, the lease record, the upstream key) can be reached by a tool-using agent running as the same Windows user.
4. **N-04.** U12 clears the uncensored model for tools before it proves the approval stop works.
5. **N-07 and N-08.** The KTD19 switch trigger and the stage handoff files are undefined.
6. **N-11.** The agy credit spend has no recorded standing approval.

A hard precondition applies regardless of these fixes. Opus runs in agy on AlienPc, so the handover can only happen in a Sydney Clone Shell window. That window waits on (a) the max pack and lease-skill update by the fleet architect, Sydney, on Derrick's yes, and (b) Sydney's box release line. Box check: both files are unchanged, with mtimes 10:17 and 10:36 CT. This is the plan's own gate (`plan:377`, `plan:492`), and it is correct.

**Round 1 closure:** 22 Closed, 2 Partial (R-20, R-21), 0 Open.
**New CAPA findings:** P0 0 · P1 4 · P2 10 · P3 6 (20). **Over-applied gates:** 0.

Labels: VERIFIED = read on the box. RELAYED = from the request or from the plan's own record of Derrick's chat. ASSUMPTION = marked.

## Method

- `git log 4bb4600..f8df93b` shows 9 commits, from 9429fab to f8df93b. `git diff --stat` shows the plan (+336/−75), a new decision file, a new open-issue file, and an unrelated learning. The f8df93b plan is **identical** to the working copy (775 lines). All `plan:N` line numbers refer to f8df93b.
- I checked each round-1 finding against the f8df93b text and the files it now cites. That includes the box director repo `/workspace/director-m2/repo` (HEAD `63d8984`, VERIFIED), `50_decisions/`, `05_open-issues/`, the settings research `/workspace/cos/research/2026-10-09-alienpc-optimal-settings.md`, and the quota watcher README and script in `/workspace/cos/director-ws/tools/`.
- The OpenCode permission defaults were checked on the web (opencode.ai and dev.opencode.ai docs, 2026-10-09). The rest is box-only. I did not touch AlienPc, message any agent, open any Imagine prompt or sidecar, or view any image or video. `cross_model_review_mode: off`, so there was no cross-model pass. The lenses were the same as round 1, applied in one pass. This is round 2 of 2, the final round.

## 1. Round 1 closure table (R-01 to R-24)

| ID | Status | Evidence at f8df93b |
|---|---|---|
| R-01 offline units need the Shell | **Closed** | `plan:25` "every AlienPc step needs Sydney Clone to own the Shell (R24). That includes agy runs, pytest, syncs and read-only file reads."; `plan:392` (the 4:06 handoff is treated as superseded until Derrick answers) |
| R-02 OQ1 closed quietly | **Closed** (see N-01 for a new route that reopens it) | `plan:54` "For now, Max ComfyUI renders stay on Sydney's lease ... whether Max should ever join the queue stays open for Derrick (OQ1)"; `plan:196` |
| R-03 Max request behind an uncapped session | **Closed** by Derrick's 5:13 rule (RELAYED) | `plan:57` "The running holder keeps priority until Derrick overrides ... resolves the earlier open question"; `plan:80` R26 |
| R-04 no request path | **Closed** (residual N-16) | `plan:219` "The box handoff line is authoritative ... Sydney asks for the lease back with a box line addressed to Sydney Clone ... `director lease init`" |
| R-05 pack/skill gate | **Closed** | `plan:377` "**Gate:** no lease move to Sydney Clone, and so no U2, until the fleet architect (Sydney) updates the pack and skill text on Derrick's yes." Sydney as fleet architect is VERIFIED in `canon/fleet-bot-allowlist.md:16`. |
| R-06 C: model location | **Closed** (residual N-17) | `plan:189`; `plan:217`; `plan:526` "A profile whose weights path is on `D:\` is rejected at config load" |
| R-07 VRAM headroom | **Closed** (new runtime risk N-12) | `plan:246` "`-c 32768 -ctk q8_0 -ctv q8_0`"; `plan:251` "`required_mib` is taken from the U2 re-measure plus a 512 MiB margin"; `plan:259`; `plan:174` |
| R-08 U2 vs U3/U4 | **Closed** | `plan:503` "tag `abcfc3d` as `m2-live-base` and run from that tag ... not merged ... until U2 has passed"; `plan:747` |
| R-09 WebSocket M2 item | **Closed** | `plan:506` "recorded as 'EXCEPTION: polling, pending Derrick'"; `plan:409` |
| R-10 U12 named GOs | **Closed** | `plan:410`; `plan:739`, `plan:745`, `plan:750`, `plan:751` |
| R-11 drill unobservable | **Closed** | `plan:228` "`status-history.jsonl`"; `plan:750` |
| R-12 status before U9 | **Closed** | `plan:585`, `plan:590`, `plan:636` (state); `plan:651` (rendering in U9) |
| R-13 no rollback/off switch | **Closed** | `plan:648` "`director queue stop`"; `plan:737`; `plan:775` "one local commit that `git revert` can undo" |
| R-14 runner lifetime | **Closed** | `plan:216` "launched detached, with a pid file ... runs `director queue stop`, so no Sydney Clone process survives a handover"; `plan:407`, `plan:408` |
| R-15 box split | **Closed** | `plan:240` KTD15. The box repo exists at `63d8984` (VERIFIED). |
| R-16 per-item pause | **Closed** | `plan:719` "`paused`, with a one-line reason ... It never holds the queue or the lane."; `plan:725` |
| R-17 sidecars | **Closed** | `plan:720` "Any other file ... including Grok Imagine prompt or sidecar files, is never opened"; `plan:726` |
| R-18 conflicts 8/11 | **Closed** | `plan:384`, `plan:387`. `05_open-issues/2026-10-09-alienpc-planning-read-during-max-lease.md` exists (VERIFIED). |
| R-19 learning cited as proposal | **Closed** | `plan:229` "(proposal: harness-gates-must-abort-not-warn)"; `plan:451` |
| R-20 circular swap check | **Partial**, now a new contradiction (N-13) | `plan:745` "at least 10 swaps ... the p95, the max". But `plan:746` "keep it at or below Derrick's figure unless he agrees otherwise" contradicts KTD8's 3x rule (`plan:229`). |
| R-21 agy self-report | **Partial**: the canary still leans on model refusal (N-14) | `plan:486` "agy is asked to run a GPU command ... and it refuses both, citing the rule" |
| R-22 queue root / bypass | **Closed** for a misconfigured front end (same-user reach is N-03) | `plan:215` "`D:\AI\director-queue\`"; `plan:218` "`--api-key` set to a per-start key" |
| R-23 head-of-line | **Closed** | `plan:560`, `plan:569`, `plan:412` |
| R-24 llama.cpp upgrade GO | **Closed** | `plan:257` "the installed b11482 has every flag above. An upgrade, if Derrick gives its own install GO, goes to **b11518**"; research `:133` |

## 2. New CAPA findings

Format: severity · confidence. Then the finding, the corrective action (CA, which fixes this plan) and the preventive action (PA, which stops it recurring).

### P1

**N-01. P1 · 75. A Max lease request takes an FCFS place, which pre-decides OQ1.**
- **Finding:** KTD6 puts Sydney's lease request into the queue's own order: "The request takes its first-come-first-served place, so anything submitted after it waits behind it. No new session starts ahead of it." (`plan:222`). Read literally, Max waits behind every job queued before the request, not just the running holder. Derrick's R26 says only "A lease request or a newer job waits behind them" (`plan:80`), where "them" is the running holder. The U6 test says "the hold starts at the job boundary" (`plan:591`). Ordering Max work relative to queue jobs is the substance of OQ1: "Should Max ComfyUI renders ever route through this queue?" (`plan:196`). The plan is inconsistent with itself (KTD6 vs R26 vs U6) and partly decides an open question.
- **CA:** Rewrite the `plan:222` bullet so that a Max request waits only for the running holder and goes ahead of jobs that are waiting but not started. This matches R26 and U6. Alternatively, put the exact ordering to Derrick as part of OQ1. Add a U6 test where two jobs are waiting when Sydney's request arrives, and the lease moves after the running one only.
- **PA:** Add a self-check line to the plan: any new rule that orders Max work against queue jobs is an OQ1 decision and needs Derrick's explicit pick.

**N-02. P1 · 75. The OpenCode approval config is missing, and its defaults are allow.**
- **Finding:** KTD14 relies on "Each coding or agent front end runs with per-action approval on, and its workspace is limited to the paths the submitter names" (`plan:239`). But the KTD10 config (`plan:231-235`) lists only the provider, model, small_model and timeouts. It has no `permission` block. OpenCode's docs say "If you don't specify anything, OpenCode starts from permissive defaults: Most permissions default to "allow"" (dev.opencode.ai/docs/permissions). In V2, every agent starts from `{ "action": "*", "resource": "*", "effect": "allow" }` (opencode.ai/v2/docs/permissions). With an uncensored idle model, shell and edit would run without asking.
- **CA:** Add a pinned permission block to KTD10:
  - shell, edit and webfetch set to `ask`
  - external_directory set to `deny`
  - explicit `deny` for `director *`, `git push *`, `Stop-Process`/`taskkill`, `nvidia-smi`, and any request to 127.0.0.1:8189, :8080 or :8700
  - reads of `D:\AI\director-queue\*` and `C:\AI\models\*` denied

  Add a U12 check that fails if the loaded OpenCode config lacks the block.
- **PA:** Any front end added later (the "general agent" front end is still unnamed) ships with its approval config written into the plan, and gets a test proving that "ask" or "deny" fires.

**N-03. P1 · 75. The human-only controls can be reached by a same-user tool agent, so they lean on the model not trying.**
- **Finding:** The override is "Only Derrick's identity can set the override" (`plan:582`), while identity is "a named flag checked against an allowlist ... It is not authentication" (`plan:368`). KEEP is a POST that "carries a per-page token" (`plan:674`) from a localhost page that any local process can GET. The lease record and the upstream key live in files in the queue root: "Only the runner and the gateway read that key from the queue root" (`plan:218`). An agent session with shell access, running as the same Windows user, can run `director lease override --by Derrick`, fetch the page token and POST KEEP, edit the lease record, or read the upstream key. Only the model's own restraint stops this. That is model refusal, not a code control, and it is exactly the case the uncensored override makes likely to be tested.
- **CA:**
  1. Block agent front ends from the `director` CLI, the queue root, `127.0.0.1:8700` and `:8080` with deny rules (N-02).
  2. Preferably, run coding and agent sessions as a separate low-privilege Windows user. That user gets read and write only on the submitter-named paths, and no access to the queue root, the runs dir, `C:\AI\models`, the ComfyUI install or the Max pool folders. This is a settings change, so it needs Derrick's GO.
  3. Make override and KEEP require an action at the dashboard by the human, with a token that is never written to a file the agent user can read.
- **PA:** Add a U12 red-team drill, sandboxed and with a named GO. Inside an agent session, try the override, a KEEP POST, a lease-record edit and an upstream-key read. Each one passes only if a code or OS control blocks it, whatever the model does.

**N-04. P1 · 75. U12 clears the model for tools before proving the approval stop works.**
- **Finding:** U12 step 3 ends with "Only on a pass does the profile become `tools_allowed: true`, recorded with the date." (`plan:743`). The approval-stop test is the last step, "11. Approval-stop test ... (only if the front-end install was approved)" (`plan:751`). The step-3 "OpenCode session through the gateway with at least 8 tool steps" also runs in an unnamed workspace.
- **CA:** Move the approval-stop test and the N-03 drill before `tools_allowed: true`. Run the step-3 smoke test in a throwaway workspace (a temp dir), with the N-02 permissions active. Make `tools_allowed: true` require both test evidence files.
- **PA:** Add to KTD4 that a profile is never tool-cleared without the safety-control evidence filed beside the smoke-test evidence.

### P2

**N-05. P2 · 75. The workspace limit isn't enforced.**
- **Finding:** "its workspace is limited to the paths the submitter names" (`plan:239`) has no enforcement. OpenCode's `external_directory` check covers file tools, but a shell command can touch any path the Windows user can reach. On AlienPc that includes Max production folders, the ComfyUI install and Sydney's orchestrators, which the handoff forbids touching.
- **CA:** Use N-03 item 2 (separate user plus ACLs) as the enforcement, and N-02's shell `ask` as the second layer.
- **PA:** Add a U12 test where a shell command writes outside the named path. It passes only if it is blocked.

**N-06. P2 · 50. Who answers the approval prompts is unclear.**
- **Finding:** R19 says tool steps that send, post, buy, delete or share wait for "Derrick's yes" (`plan:106`). But Sydney Clone runs sessions through Shell, where an interactive approval prompt can't be answered. Non-interactive use of OpenCode either blocks or follows its config, and the plan doesn't say which.
- **CA:** Define two modes. Sydney Clone's sessions run non-interactive with those action classes set to `deny`, and the job raises a notice for Derrick. Derrick's own sessions at the PC use `ask`.
- **PA:** Add the mode to the job record and test both.

**N-07. P2 · 75. The KTD19 switch trigger is undefined.**
- **Finding:** The plan says "When the agy quota watcher reports Sonnet out of tokens" (`plan:268`). The watcher README says alerts have `kind=quota|rate_limit`, and "IDE error lines don't name the model, so IDE alerts usually show `model: "unknown"`" (`director-ws/tools/agy_quota_watch.README.md`). A transient `rate_limit` or an unknown-model alert could trigger a needless switch. Opus running out during planning has no rule at all.
- **CA:** Define the trigger as `kind=quota`, with `model_family` Claude Sonnet, or `unknown` confirmed by Sydney Clone in the agy UI. A `rate_limit` alert means wait. If `reset_at` is soon, waiting may beat switching. Add the rule for Opus running out (wait for reset, or Derrick names a fallback).
- **PA:** Keep a watcher-event-to-action table in `AGY_TASKS.md` (U1).

**N-08. P2 · 75. Context can be lost when the model switches mid-unit.**
- **Finding:** "Sydney Clone makes each switch and checks the work at every handoff: tests rerun, diff read, and any partial edit reconciled before the next model continues" (`plan:270`). Nothing says what the next model starts from. Quota exhaustion is abrupt and mid-turn. Whether agy carries conversation context across a model change is unverified. The plan stage (Opus) also has no tests to rerun.
- **CA:** Each stage writes a file. Opus writes `docs/agy-plans/Ux-plan.md`. Sonnet updates `docs/agy-plans/Ux-progress.md` after each step. Flash starts only from those files plus `git diff`. Sydney Clone checks the Opus plan against the unit's task prompt and the Planning Contract before Sonnet starts.
- **PA:** Build this into the `AGY_TASKS.md` template. One check: a switched unit's final diff must cover every step listed in the plan file.

**N-09. P2 · 50. Each code unit has two authors.**
- **Finding:** Sydney Clone drafts and tests U3-U11 in the box worktree (`plan:22`, `plan:240`), and agy builds the same units on AlienPc under KTD19 (`plan:264-270`). The plan doesn't say which is the code of record.
- **CA:** Pick one per unit in `AGY_TASKS.md`. Either the box draft is the source and agy only audits and finishes it, or agy builds and the box draft is reference only.
- **PA:** Add an author field to each task prompt.

**N-10. P2 · 50. The scope of "audit and CAPA" is ambiguous.**
- **Finding:** Derrick's 5:40 line (RELAYED in the request) was "after audit and CAPA, send it to Opus to plan". The plan turns it into a step inside every agy task (`plan:265`) and asks who runs it (`plan:402`). It may simply mean this plan-level audit.
- **CA:** Record this round-2 review as the plan-level audit and CAPA. Ask Derrick whether a per-unit audit is also wanted.
- **PA:** When a directive is turned into a process step, quote it verbatim in the plan.

**N-11. P2 · 75. The agy credit spend has no recorded standing approval.**
- **Finding:** The plan says "Governs R14 (credit spend stays under Derrick's existing agy approval)." (`plan:277`). `50_decisions/` holds only two files, the Huihui pick and the Max steps defaults (VERIFIED). The fleet pack says "A standing approval counts only when it is a recorded decision naming the action, scope, cap and expiry" (`10_packs/fleet/external-actions-need-derricks-exact-yes.md:12`).
- **CA:** Record Derrick's 5:40 directive as a decision file with scope (agy Opus, Sonnet and Flash for this plan's U1-U13 builds), cap and expiry. Cite it as `(decision: ...)`.
- **PA:** Every model or credit pipeline cites its decision file in the KTD that defines it.

**N-12. P2 · 75. The VRAM headroom erodes on a live desktop, and an overflow then loses work.**
- **Finding:** See section 3 for the arithmetic. The research baseline is "about 14.44 GiB free (14,782 MiB; Comfy-idle, desktop running)", measured before dynamic VRAM (research `:77`). The compute figure is "Back-solved from randomgenericbot's headless run" (research `:87`), and that source says "with a desktop … maybe 48k" (research `:64`). The plan's headroom is 0.6-1.0 GiB (`plan:251`), and the pass bar is "at least 0.5 GiB free" (`plan:740`). The load-time check doesn't cover a desktop that grows after load (the U13 browser, Derrick's own apps). With "Prefer No Sysmem Fallback" on, as the plan wants (`plan:258`), an overflow becomes a CUDA OOM that crashes llama-server mid-session, not a slowdown. That breaks R27's "no work is lost" for the session context.
- **CA:** Do the U2 re-measure with the dashboard open and a normal desktop running. The runner samples free VRAM during sessions and warns the holder below 0.3 GiB. Fall back to `-ub 256`, then 16K, for the next load.
- **PA:** Add a success criterion: "no session ended by a llama-server OOM". The runner logs every OOM.

**N-13. P2 · 75. The new swap-bound rule contradicts KTD8 and the measured loads (R-20 Partial).**
- **Finding:** "keep it at or below Derrick's figure unless he agrees otherwise" (`plan:746`). Against that are "180 s ... about 3x Derrick's ~1 minute figure" (`plan:229`), "M0 cold load was 77 s" (`director-ws/M1_live_results.md:8`), and the 60 s gap. A bound of about 60 s would fail ordinary swaps.
- **CA:** Set the bound to the measured max times about 1.5, capped at 180 s. If typical swaps exceed about 1 minute, report that to Derrick rather than shrinking the bound.
- **PA:** A bound is never set below the measured max.

**N-14. P2 · 50. The U1 canary leans on agy refusing (R-21 Partial).**
- **Finding:** "agy is asked to run a GPU command ... and it refuses both, citing the rule" (`plan:486`). That tests whether the model complies. The enforced controls are agy's permission prompts and terminal policy, and the canary doesn't check them.
- **CA:**
  - Configure agy's terminal auto-execution off, with a deny list: `nvidia-smi`, `llama-server`, requests to `:8189`/`:8080`, and reads of `D:\AI\director-queue`.
  - The canary passes only if the prompt or the deny list intercepts the step. Sydney Clone watches and denies it.
  - Run the same canary against the idle model in OpenCode (N-02, N-03).
- **PA:** Every refusal-type test in this plan names the code or OS control it proves.

### P3

**N-15. P3 · 50. The "no tools in chat" control sits in the panel, not the gateway.**
- **Finding:** "the panel sends no tools" (`plan:679`). A chat-session token used outside the panel could still send `tools`.
- **CA:** The gateway strips or refuses `tools` for `chat_session` tokens and for profiles with `tools_allowed: false`.
- **PA:** Add a U8 test for both.

**N-16. P3 · 50. The lease-mismatch check can't see the box (R-04 residual).**
- **Finding:** The U6 test compares against "the latest line supplied to the check" (`plan:589`). The AlienPc runner can't read the box, so only the owner supplies that line.
- **CA:** Say it plainly: the owner passes the box line id at `lease release`/`init`, and Sydney Clone compares record and box line at the start of each Shell window.
- **PA:** Add the comparison to her window-start checklist.

**N-17. P3 · 50. The 9B paths vs the D: rejection rule.**
- **Finding:** KTD18 keeps the 9B "where they are" and confirms C: vs D: in U2 (`plan:263`). U3 rejects D: paths (`plan:526`). If only D: copies exist, vision_9b won't load. The runbook says both exist, so this is likely fine.
- **CA:** If no C: copy exists, ask Derrick for a copy GO. Make no D: exception.
- **PA:** None needed.

**N-18. P3 · 50. The watcher process's lifetime is unaddressed.**
- **Finding:** The quota watcher is a long-running PowerShell process on AlienPc ("Only one copy can run at a time"). The plan asks Derrick whether a held runner may outlive a handover (`plan:407`), but not whether the watcher may.
- **CA:** Add the watcher to the same question.
- **PA:** List every long-lived Sydney Clone process in KTD3.

**N-19. P3 · 75. The uncensored override isn't scoped or cited in the plan text.**
- **Finding:** The decision file is dated and scoped: "for the AlienPc idle coding/agent model only. The 9B Heretic vision profile stays tools-off." (`50_decisions/2026-10-09-alienpc-idle-model-uncensored-huihui.md:9`). It records Derrick's 5:06 and 5:10 PM CT lines as RELAYED. The plan's Key Decision says only "This overrides the earlier rule that Heretic/abliterated builds are not for agents and tools." (`plan:55`), with no scope and no `(decision: ...)` cite. The research it relies on still says "Uncensored 27B tunes ... stay **banned for agents/tools** per DEC" (`research/2026-10-09-local-llm-community-variants.md:98`).
- **CA:** Add "AlienPc idle coding/agent profile only" and `(decision: 50_decisions/2026-10-09-alienpc-idle-model-uncensored-huihui.md)` to `plan:55` and R11.
- **PA:** Add a superseded-by pointer to the older DEC. That needs its owner's edit, so it is listed, not done.

**N-20. P3 · 50. The OpenCode install GO may be incomplete.**
- **Finding:** The install GO (`plan:398`) names OpenCode only. Depending on the install route, a runtime such as npm or Node may also be installed.
- **CA:** The GO draft names the exact installer, the runtime if any, the version, and the config file path.
- **PA:** None needed.

## 3. VRAM arithmetic (11.29 GiB idle model, 16 GB display GPU)

Numbers from the settings research (VERIFIED, `research/2026-10-09-alienpc-optimal-settings.md:77-92`):
- File: 12,120,016,416 B = 11.29 GiB. That's the "11 GiB" in the thread table.
- On GPU: 10.90 weights (token_embd 0.38 stays in host RAM; includes the 0.33 MTP head) + 1.06 KV at 32K q8_0 + 0.07 MTP draft KV + 1.2-1.6 compute/CUDA = **13.4-13.8 GiB**.
- Free with Comfy idle and the desktop running: 14.44 GiB, measured before dynamic VRAM. **Headroom 0.6-1.0 GiB.**
- Other contexts: 48K q8_0 is 13.9-14.3 (0.1-0.5 headroom, borderline). 64K q8_0 is 14.5-14.9 and does not fit. 64K q5_1/q4_0 is 13.7-14.1.
- The vision 9B is 9.9-10.9 GiB (research `:117`). The two models can never be resident together, and an LLM never sits beside a running Comfy job (R7). Both hold.
- Risks: dynamic-VRAM residue after a Max job forces a `/free` (cold Max start, logged; `plan:259`). A growing desktop or the dashboard browser after load (N-12). The compute figure comes from a headless report and must be replaced by the U2 measurement (research `:283`). The plan states all of this as an estimate, which is correct.

## 4. Other new-addition checks (both directions)

- **R26/R27 vs Sydney's direct Max access:** this is Derrick's own rule. A long session can keep Max waiting, and the plan names and accepts that risk (`plan:57`, `plan:432`). No conflict beyond N-01.
- **R26 vs the single Shell owner rule:** consistent. The priority covers whoever holds the Shell, and R25 still moves ownership only by release line.
- **Download GO:** complete. It names the file and size, the template's pinned sha256, the `C:\AI\models\` target, C: free space, and "no D: copy" (`plan:396`). The baseline model needs its own GO (`plan:397`). Not pre-approved.
- **Installs:** b11518 (optional, `plan:401`), OpenCode (`plan:398`, see N-20), fastapi (optional, `plan:403`). All gated.
- **Settings:** the sysmem fallback (`plan:400`, `plan:500`), the power plan (`plan:408`) and the startup task (`plan:406`) are all gated.
- **R30 pre-flight:** listing is read-only and ungated, which is correct. Closing is per item on Derrick's yes, a force-kill needs its own yes, and ComfyUI, Sydney's orchestrators, local-exec and system processes are excluded (`plan:496-498`). That matches the handoff's do-not list.
- **agy permissions:** `--dangerously-skip-permissions` is still unused until Derrick answers (`plan:405`). Not pre-approved.
- **Over-applied gates:** none. Read-only listing, box drafts, PLAN edits on the box and decision files are all ungated. "reads included" (`plan:24`) is strict, but it follows Derrick's one-owner rule while the non-Shell-read question (`plan:394`) is open, and where rules conflict the stricter one wins.
- **Uncensored-model choice:** not judged, as instructed. Only its controls were reviewed (N-02 to N-06, N-14, N-15, N-19).

## 5. Fix order

1. N-01 (OQ1 coherence; changes U6).
2. N-02, N-03, N-04, N-05 (front-end and OS controls; these change KTD10, KTD14, U8 and U12).
3. N-07, N-08, N-09, N-11 (the KTD19 pipeline Opus will run under), then N-10.
4. N-12, N-13, N-14, N-06.
5. P3s: N-15 to N-20.

Then hand to Opus in the first Sydney Clone Shell window, after the pack/skill gate and Sydney's release line.

## 6. Could not verify

- Derrick's 5:06, 5:10, 5:13-5:25 and 5:40 PM lines: RELAYED (in the plan, the decision file and the request). There was no shared-memory file on the box.
- Whether agy keeps conversation context across a model switch, the exact Sonnet and Flash ids, and whether Flash has a "high" thinking level: ASSUMPTION per the plan (`plan:275`); AlienPc only.
- OpenCode's behaviour in non-interactive mode with `ask` rules (N-06): not checked.
- The director code at `abcfc3d` on AlienPc. The box copy `63d8984` exists, but the claim that it matches AlienPc is unverified until Sydney Clone's hash compare.
- Whether the pack and skill update and Sydney's release line will happen tonight. Both files are unchanged as of 17:47 CT.

## Coverage

| Lens | Lead findings |
|---|---|
| coherence | N-01, N-09, N-10, N-13, N-16, N-19 |
| feasibility | N-07, N-08, N-12, N-17, N-18, N-20 |
| security-lens | N-02, N-03, N-04, N-05, N-06, N-15 |
| adversarial | N-14, N-11 |
| scope-guardian | none new |

Cross-model pass: skipped (off). Applied fixes: none (report-only). Round 2 of 2: no further review rounds unless new evidence arrives.
