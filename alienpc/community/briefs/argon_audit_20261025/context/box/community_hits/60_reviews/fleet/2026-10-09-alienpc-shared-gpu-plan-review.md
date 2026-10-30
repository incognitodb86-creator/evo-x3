---
title: ce-doc-review (report-only) - AlienPc local AI on one shared GPU plan
target: ce/plans/2026-10-09-1622-feat-alienpc-local-ai-shared-gpu-plan.md @ 4bb4600
reviewer: Fleet Reviewer bc9b71d5 (executor subagent, independent)
requested_by: Sydney Clone 4f7cac4f, on Derrick's go 2026-10-09 5:02 PM CT
run: 2026-10-09 17:02-17:08 CT (box date)
---

# Review: AlienPc local AI on one shared GPU plan (report only)

## Verdict

**Ready after fixes. Not ready to build as written.** No unit should start until fixes 1-6 are made. Fixes 7-17 are needed before U2 or U12 (the live units).

Must fix before any unit starts:
1. **R-01 (P0).** The offline units (U1, U3-U11) need AlienPc Shell, but the plan marks them unblocked while Sydney holds the lease.
2. **R-02 (P1).** Restore the open question about Max renders joining the queue. The plan quietly closed it.
3. **R-03 (P1).** Don't hard-code "Sydney's lease take waits behind an uncapped session" into U6/U7 before Derrick decides.
4. **R-04 (P1).** Define how Sydney's lease request actually reaches AlienPc. Today only the current owner can write the lease record.
5. **R-05 (P1).** Gate U2 on updating the pack and skill text (or on a cited decision file) that lets the lease move to Sydney Clone.
6. **R-06 (P1).** Put the C: model-location decision into the plan. The research the plan cites schedules downloads on D:.

Counts: **P0 1 · P1 5 · P2 11 · P3 7 (24 findings).** Over-applied gates found: **0.**

Labels: VERIFIED = I read it on the box. RELAYED = Derrick's settled decisions as given in the review request (I found no shared-memory file for them on the box). ASSUMPTION = marked as such.

## Scope and method

- **Target:** `git -C /workspace/cos/brain-staging show 4bb4600:ce/plans/2026-10-09-1622-feat-alienpc-local-ai-shared-gpu-plan.md` (589 lines). `diff` against the working copy: **identical**. All `plan:N` line numbers below refer to this file.
- **Classification:** `unified-plan` (Product Contract plus Planning Contract plus units).
- **Mode:** non-interactive and report-only. Nothing was applied (no Apply tier). `cross_model_review_mode: off` (`.compound-engineering/config.yaml`), so no cross-model pass ran.
- **Lenses:** coherence and feasibility (always on); scope-guardian (12 units); adversarial (new queue/lease architecture); security-lens, lightly (gateway session tokens). There was no subagent primitive, so this reviewer applied each lens in one pass. Coverage note: personas were not dispatched separately.
- **Context read (VERIFIED):** `10_packs/max/*`, `10_packs/fleet/*`, the `alienpc-local-exec-lease` SKILL.md, the handoff `30_handoff/inbox/2026-10-09-1606-alienpc-director-m2.md`, `/workspace/cos/director-ws/{docs/PLAN.md, M2_live_runbook_2026-10-09.md, docs/M0_results.md, M1_live_results.md}`, `/workspace/cos/research/2026-10-09-local-llm-community-variants.md`, plan git history (`e9b04e3`..`4bb4600`), and the canon fiction lock. The canon was checked only for the vision-review rules (rules 4 and 5) and is cited by path, never pasted.
- **Not touched:** AlienPc and every user machine, all agents, and Grok Imagine prompts and sidecars. No images or videos were viewed.

## 1. Settled decisions: honoured, contradicted or reopened

Method: I took each decision from the request (RELAYED) and from the plan's own Key Decisions (`plan:49-55`), grepped the plan for each one, and compared it with earlier plan commits (`git show 40682ec`).

| # | Decision | Status | Evidence |
|---|---|---|---|
| D1 | One system for all four uses (4:16-4:18) | Honoured | `plan:49` "One system for all four uses on AlienPc."; `plan:60` R1 |
| D2 | First come, first served | Honoured (one ambiguity, R-23) | `plan:50`, `plan:65` "Jobs start in submit order" |
| D3 | Coding/agent model stays loaded when idle | Honoured, with a flagged exception | `plan:51`, `plan:76` R10. The exception is `plan:285` "the idle model is unloaded (R7 is read as taking precedence over R10)". It is listed for Derrick at `plan:312`, which is correct handling. |
| D4 | Only Derrick and Sydney Clone submit; others ask Sydney Clone | Honoured | `plan:52`, `plan:61` R2, `plan:127` F3, `plan:138` AE2 |
| D5 | Whether Max renders join the queue is OPEN; for now Sydney keeps direct Max access | **Contradicted: closed without saying so** (R-02). Direct access is also limited (R-03). | `plan:54` "chosen over routing Max through the queue"; `plan:157` "does not route through the queue (R8)". Commit `40682ec` removed "for now" and the OQ1 text. |
| D6 | AlienPc always has exactly one clear Shell owner (4:36) | Honoured in the requirements, **contradicted in the sequencing** (R-01) | `plan:71` R24, `plan:72` R25 versus `plan:25` "Open blockers: none for the offline units" |
| D7 | Max renders stay on Sydney's lease (24f66698); Sydney Clone's live work waits for her release line | Honoured | `plan:70` R8, `plan:144` AE8, `plan:389` U2 dependencies. The lease id 24f66698 is not cited (minor). |
| D8 | All AI models on C: (new LLMs in C:\AI\models, VLM in C:\AI\vlm\models) | **Missing** (R-06) | No `C:\` anywhere in the plan (grep). The cited research plans downloads on D:. |
| D9 | Max official keep: ComfyUI 8189 with dynamic VRAM on | Honoured; side effect not covered (R-07) | `plan:73` R9, `plan:215`, `plan:303` |
| P1 | Plan's own: a session holds the GPU until it ends (4:23) | Honoured; collides with D5 (R-03) | `plan:53`, `plan:67` R23 |

## 2. Lease and single-Shell-owner conflicts

Method: I checked each of the plan's 11 listed conflicts (`plan:297-307`) against its source. "Real" means I confirmed it on the box. "Resolution/owner" means the plan names a fix and who carries it.

| # | Real? | Resolution and owner? | Note |
|---|---|---|---|
| 1 | Yes. Skill: "Single lease: Max Studio only" (`alienpc-local-exec-lease/SKILL.md:27`). Pack: "Max Studio is the sole AlienPc Shell lease holder" (`10_packs/max/one-holder-for-the-alienpc-shell.md:11`) | Fix: fleet architect, on Derrick's yes. **Not sequenced before U2** | R-05 |
| 2 | Plausible. The rule file lives on AlienPc, so not verifiable | Standing approval from Derrick before U12. Fine | |
| 3 | Yes (VRAM) | Assumption plus Open Question for Derrick. But U6/U7 build the assumed behaviour first | R-03, R-07 |
| 4 | Yes (the refused Read is RELAYED) | Open Question for Derrick. The R20 "at any time" wording and the U12 drill are not adjusted | R-11 |
| 5 | Yes. `M0_results.md:3` shows only the 9B | Download GO for Derrick. **Location missing** | R-06 |
| 6 | Plausible (code not visible from the box) | U4. Fine | |
| 7 | Yes. `M2_live_runbook_2026-10-09.md:22` | U2. Fine | |
| 8 | Yes. `director-ws/docs/PLAN.md:51,209` | **No resolution or owner** | R-18 |
| 9 | Yes for the PLAN text (`PLAN.md:17`); .venv not verifiable | Partial. The M2 row still needs WebSocket | R-09 |
| 10 | Yes, per the plan's history | KTD11. A risk more than a conflict | |
| 11 | Yes (self-reported breach) | **No corrective action or owner** | R-18 |

Conflicts the plan missed: R-01, R-03, R-04, R-06, R-07, R-11, R-14 below.

## 3. Findings

Severity: P0 means it would breach a settled rule if built or run as written; P1 must be fixed before build; P2 before the live units; P3 polish. Confidence uses anchors 0/25/50/75/100. Every finding at 75 or above quotes its evidence.

### P0

**R-01. P0 · 75. Offline units need AlienPc Shell, but the plan says they are unblocked while Sydney holds the lease.**
- Location: `plan:25`, `plan:279`, `plan:311` versus `plan:289`, `plan:413`, `plan:576`.
- Evidence: `plan:25` "Open blockers: none for the offline units." `plan:279` "The offline units do not wait for it." `plan:311` "(none blocks U1, U3-U11)". But `plan:289` "agy runs only while Sydney Clone owns the AlienPc Shell", and `plan:576` runs unit tests with "`.venv\Scripts\python -m pytest tests/unit -q` on AlienPc, run by Sydney Clone". The pack says "no second bot runs Shell on that PC at the same time" (`10_packs/max/one-holder-for-the-alienpc-shell.md:11`). The plan's own conflict 11 (`plan:307`) records read-only Shell during Sydney's window as "what R24 forbids". The handoff's earlier permission, "offline M2 work (... `pytest tests/unit` ...) is fine now with no lease" (`30_handoff/inbox/2026-10-09-1606-alienpc-director-m2.md:21`, 4:06 PM), was written before Derrick's 4:36 PM one-owner rule. The plan never reconciles the two.
- Consequence: the next step after this review, building U1/U3, would have agy or Sydney Clone running commands on AlienPc during Sydney's Max queue. That is the dual-Shell pattern the skill forbids (`SKILL.md:42`), and Sydney's queue runs to about 6:10-8:30 PM CT per the handoff.
- Fix: state that U1 and U3-U11 run only while Sydney Clone owns the AlienPc Shell, or move them to the box (R-15). Ask Derrick whether the handoff's "offline fine with no lease" still stands after 4:36. Until he answers, treat it as superseded. Change `plan:25`, `plan:279` and `plan:311` to match.

### P1

**R-02. P1 · 100. The open question about Max renders joining the queue was closed quietly.**
- Location: `plan:54`, `plan:157`; commit `40682ec`.
- Evidence: `plan:54` "**Max ComfyUI renders stay on Sydney's lease; the queue waits on her lease.** ... chosen over routing Max through the queue". `plan:157` "Max ComfyUI production work keeps its lease-based path and does not route through the queue (R8)." The `40682ec` diff removed "Max ComfyUI work stays on Sydney's lease for now. Working default until OQ1 is answered." and removed "OQ1. Do Sydney's Max ComfyUI renders go through this queue, or keep their own lease path?". Derrick's position (RELAYED, 4:16 and 4:36) is that this is still OPEN and the lease path holds "for now".
- Fix: restore "for now / interim" in `plan:54` and `plan:157`. Re-add OQ1 under Open Questions as Derrick's open decision. Keep R8 as the interim behaviour.

**R-03. P1 · 75. Sydney's lease take waits behind an uncapped session, and U6/U7 build that before Derrick decides.**
- Location: `plan:193`, `plan:285`, `plan:468`, `plan:67`.
- Evidence: KTD6 says "the runner finishes the current job or session, unloads its LLM ... and holds" (`plan:193`). R23 sets "no time cap" (`plan:67`). The assumption "Sydney's lease take waits for the current job or session to end" (`plan:285`) is flagged for Derrick, but the U6 test "Hold starts at the job boundary" (`plan:468`) builds it now, and `plan:311` says the decision blocks nothing before U12.
- Consequence: a coding session can hold Max off the GPU indefinitely. That cuts into "Sydney keeps direct Max access" and in practice puts Max behind the queue, which pre-decides R-02.
- Fix: make the behaviour on a pending Max request a Derrick decision **before U6**, not U12. Until he decides, a pending request ends nothing automatically, writes a notice and asks Derrick, and no new session starts while Sydney has announced Max work.

**R-04. P1 · 75. Sydney has no way to request the lease back.**
- Location: `plan:193`, `plan:249`, `plan:460-462`, `plan:108`.
- Evidence: the lease record "is changed only by a `director lease` command run by the current owner" (`plan:193`). The sequence diagram has "S->>LR: lease request (via current owner's release line)" (`plan:249`). While Sydney Clone owns the Shell, Sydney cannot run anything on AlienPc. The state diagram's "Sydney takes the Max lease" (`plan:108`) contradicts R25: "changes only when the current owner writes an explicit lease-release line" (`plan:72`). There are also two sources of truth (the box release line and the AlienPc record), with no rule for which wins and no bootstrap step that creates the record.
- Fix: the request path is a box handoff line from Sydney to Sydney Clone. Sydney Clone, as owner, records it (for example `director lease request --for Sydney`) and later runs `director lease release --to Sydney`. The box line is authoritative and the AlienPc record mirrors it in the same turn. Add record creation to U6/U12.

**R-05. P1 · 75. The lease move is not gated on the pack and skill update.**
- Location: `plan:297`, `plan:279`, `plan:389`.
- Evidence: conflict 1 says "The skill and pack text need a Derrick-approved update by the fleet architect." (`plan:297`). But U2 "runs as soon as Sydney's lease-release line names Sydney Clone and Derrick gives the session GO" (`plan:279`). The fleet adapter puts "pack rule > decision > learning" (`fleet-ce-adapter/SKILL.md` §7).
- Fix: add a U2 precondition. Either the pack and skill text are updated on Derrick's yes, or Derrick's 4:36 decision is recorded as a decision file that the pack links. Cite it in U2.

**R-06. P1 · 75. The C: model-location decision is missing, and the cited research plans D:.**
- Location: `plan:166-167`, `plan:315`, `plan:403`.
- Evidence: the plan has no `C:\` path (grep). The cited research says "D: 117 GB free" and "## 7. Download plan (D: 117 GB free; budget ~100 GB)" (`/workspace/cos/research/2026-10-09-local-llm-community-variants.md:6,166`). The runbook notes "`llm.args` model paths exist (currently `C:\AI\vlm\models\...`; the D: copies also exist)" (`director-ws/M2_live_runbook_2026-10-09.md:26`).
- Fix: add a constraint that new LLM weights go under `C:\AI\models` and the VLM stays in `C:\AI\vlm\models`. U3 profiles and the weights check use those paths. The download GO draft names the C: target and C: free space. The D: copies are not used.

### P2

**R-07. P2 · 75. VRAM headroom for the 27B idle model next to the always-on ComfyUI is very thin, and the plan sets no context size.**
- Location: `plan:37`, `plan:76`, `plan:403`.
- Evidence: the plan sizes the model as "the 27B coding/agent model (~13-14 GB)" (`plan:37`). The research gives "GSQ-RCO IQ3_S = 14.0 GB at 32K f16 KV, 14.1 GB at 64K q8_0 ... 'GB' there means GiB" and "about 14.5–15 GB usable, since it is also the Windows display GPU" (research `:82`, `:6`). The pre-dynamic-VRAM baseline is `comfy_idle_free_mib: 14782`, about 14.4 GiB (`plan:303`). See the arithmetic below.
- Consequence: R10 "always loaded" only fits with about 0.3 GiB to spare, or after a `/free` on Max's ComfyUI. That `/free` makes Max's next render cold (pack: "cold 160.8s off vs 49.0s on", `10_packs/max/production-defaults-st8-dynamic-vram.md:12`), which works against `plan:152` "No Max production render is disturbed".
- Fix: fix the idle profile's context and KV (for example 32K q8_0), with `required_mib` taken from the U2 baseline. Say whether the runner holds or calls `/free` when Comfy is holding VRAM, and put that under the standing approval. Add a "Max cold-start cost" line to the success criteria.

**R-08. P2 · 75. U2 proves the old code, while U3/U4 rewrite the same code in parallel.**
- Location: `plan:279`, `plan:387`, `plan:405`, `plan:422`.
- Evidence: U2's goal is to "prove the existing GPU handoff live" (`plan:387`), but "The offline units do not wait for it" (`plan:279`). U3 changes `GPUManager.to_llm`, and U4 changes ownership in `gpu.py`.
- Fix: pin U2 to `abcfc3d` (a tag or worktree), or run it before merging U3/U4. Add a live regression of the modified handoff to U12.

**R-09. P2 · 75. U2 cannot mark every M2 row item PASS.**
- Location: `plan:394`, `plan:305`.
- Evidence: U2 verification requires "every M2 row item is marked PASS" (`plan:394`). The M2 row includes "WebSocket completion detection" (`director-ws/docs/PLAN.md:186`), while conflict 9 says `websockets` is not installed and "Completion uses polling" (`plan:305`).
- Fix: Derrick decides between amending the M2 row to polling or an install GO. Until then, U2's checklist names the exception.

**R-10. P2 · 75. U12 runs a benchmark, a drill and a destructive-step test without named GOs.**
- Location: `plan:562-565` versus `plan:80`.
- Evidence: R14 says "Every model download, install or benchmark needs Derrick's GO for that exact item" (`plan:80`). U12 step 2 is "Measure five swaps per profile pair" (`plan:562`). Step 4 is a "Max-hold drill (agreed with Sydney)". Step 5 is "check that a scripted delete or send step in an agent session stops for approval". Open Questions (`plan:311-318`) lists none of these.
- Fix: list each one as a named GO under Open Questions. For step 5, name a harmless sandbox target (a throwaway file in a temp dir, and a send to a stub endpoint).

**R-11. P2 · 75. The U12 Max-hold drill can't be observed by its operator.**
- Location: `plan:564`, `plan:300`.
- Evidence: conflict 4 says "While Sydney owns the Shell, Sydney Clone has no Shell path to status" (`plan:300`). U12 step 4 runs the hold drill (`plan:564`) and checks AE4 "status shows the hold reason" (`plan:140`).
- Fix: AE4 evidence comes from the timestamped log and status history, read after the lease returns. Alternatively, Sydney captures status during her hold, or Derrick answers the non-Shell-read question first.

**R-12. P2 · 75. U6 and U8 test status output before the status surface exists.**
- Location: `plan:464`, `plan:467`, `plan:506` versus `plan:366`.
- Evidence: U6 tests "status shows it" and "status shows 'held: Max lease'". U8 tests "shows the holder and the 40 minutes in status". `status.py` arrives in U9, which depends on U8 and U10 (`plan:366`).
- Fix: U6 and U8 tests assert on lease and session state objects. Move status-rendering assertions to U9.

**R-13. P2 · 75. There is no rollback and no off switch.**
- Location: whole plan (grep for rollback/revert/disable: 0 hits). U9 commands are at `plan:517`.
- Evidence: U9 adds "`director submit`, `director queue status`, `director queue run`, `director session start|end`, and `director lease show|release`". There is no stop or drain command. U2 and U12 edit `config/director.yaml`.
- Fix: add `director queue stop` (drain, stop own llama-server, verify `:8080` closed, mark the GPU released). Revert each code unit as one local commit. Snapshot and revert `config/director.yaml` for the live units.

**R-14. P2 · 75. The runner's lifetime doesn't fit the Shell channel or the lease rules.**
- Location: `plan:318`.
- Evidence: "Sydney Clone starts `director queue run` by hand while she owns the Shell, and it does not survive a reboot" (`plan:318`). The skill says "Hang >15–30s empty → stop; ≤1 Shell retry then HOLD" (`SKILL.md:28`), and step 9 calls for "screen/display off = Never · sleep = Never · no auto-lock" during queues (`SKILL.md:37`).
- Fix: launch it detached with a pid file. Define the runner's state when ownership passes to Sydney (stopped, or held with no LLM, and whether a still-running Sydney Clone process counts as ownership). Add the power-plan check as a Derrick-gated settings item.

**R-15. P2 · 50. Box-side and AlienPc-live work are not split.**
- Location: `plan:182`, `plan:358`, `plan:576`.
- Issue: every unit, including U1 (rules and docs only), lives in `D:\AI\director` and is tested on AlienPc. That makes all work Shell-bound (R-01). Much of U3-U11 is mocked Python and could be built and tested on the box, then synced once while Sydney Clone owns the Shell. Confidence is 50 because I can't see how much of the code is Windows-specific.
- Fix: mark U1 as box-side (draft in `/workspace/cos/director-ws`). Consider a box worktree for U3-U11, with the AlienPc test run as the gate.

**R-16. P2 · 50. The lane QA job has no per-item pause outcome.**
- Location: `plan:551`, `plan:84`.
- Issue: U11 says "Results name breaks in words, and there is no pass or fail verdict field." The fiction lock (canon rules 4 and 5, reached via `10_packs/max/fiction-and-cnc-follow-the-linked-canon.md:11`) requires pausing a single item when the image shows youth, with a one-line reason, and never a lane-wide hold. The plumbing has no field for that outcome, so a pause would get lost in advisory text. The two-way check found no over-refusal in the plan.
- Fix: add a `paused` item outcome with a reason. A paused item does not hold the queue.

**R-17. P2 · 50. The lane QA inputs have no guard against Grok Imagine prompt sidecars (R3).**
- Location: `plan:546`.
- Issue: the job takes an output dir of Max output. Nothing stops the runner from reading Grok Imagine prompt or sidecar files in that dir (fleet-ce-adapter §4 R3; `fiction-and-cnc-follow-the-linked-canon.md:11`).
- Fix: the input allowlist is image and video extensions only. Add a test that a sidecar in the dir is never opened.

### P3

**R-18. P3 · 75. Conflicts 8 and 11 have no resolution or owner.**
- Evidence: `plan:304` "the PLAN text is stale" (no fix named). `plan:307` "That overlap is what R24 forbids, and it is reported here."
- Fix: conflict 8 gets a PLAN §2.3 edit owned by Sydney Clone. Conflict 11 gets a file in `05_open-issues/`, a line to Derrick and Sydney in the close, and a rule that planning reads use box copies.

**R-19. P3 · 100. An unreviewed learning is cited as a learning.**
- Evidence: `plan:195` "(learning: `ce/solutions/max-video/harness-gates-must-abort-not-warn.md`)". That file carries `tags: [unreviewed, max, harness]` (line 3). The adapter §7 says "Until then cite it as `(proposal: <slug>)`".
- Fix: change it to `(proposal: harness-gates-must-abort-not-warn)`.

**R-20. P3 · 75. The U12 swap check is circular and the sample is too small.**
- Evidence: "Set the KTD8 bound to the measured p95 plus a margin" (`plan:563`) and "Swap times are logged with p95 under the new bound" (`plan:568`). "Measure five swaps per profile pair" (`plan:562`).
- Fix: use at least 10 swaps per pair. Report the max as well as the p95. Compare against Derrick's ~1 minute figure.

**R-21. P3 · 50. U1 is verified by agy's own report.**
- Location: `plan:383` versus `plan:198`.
- Issue: "agy lists the new rule as loaded" relies on agy's own account, while KTD11 says a result counts "never from agy's walkthrough".
- Fix: Sydney Clone watches a canary task where agy is asked for a forbidden step (for example a GPU command) and refuses.

**R-22. P3 · 50. The queue root is unnamed, and the gateway can be bypassed.**
- Location: `plan:189`, `plan:192`.
- Issue: KTD2 never names the queue root path. llama-server `:8080` stays directly reachable on 127.0.0.1, so a misconfigured front end skips FCFS order and the gap.
- Fix: name the queue root path. Run llama-server with an `--api-key` that only the gateway holds, or on a port the front ends are never given.

**R-23. P3 · 50. Head-of-line behaviour for held jobs is undefined.**
- Location: `plan:230`.
- Issue: a job held for missing weights either blocks everything behind it or is skipped, and skipping bends FCFS (D2).
- Fix: state which. Skip-with-notice is the likely intent; record it as an FCFS exception for Derrick.

**R-24. P3 · 50. A llama.cpp upgrade may need an install GO.**
- Issue: the research says the build is "llama.cpp b11482 (upgrade to b11501+ pending)" (research `:6`) and recommends MTP flags for the pick. If the idle profile needs the upgrade, there is an install with no GO in `plan:311-318`.
- Fix: confirm the pick runs on b11482, or add the upgrade GO.

## 4. Approval gates (both directions)

Method: I listed every consequential step in R14, KTD10, KTD11, U2, U12 and Open Questions, then checked each for an explicit Derrick GO and for any pre-approval.

- **Gated correctly:** model downloads (`plan:80`, `plan:141`, `plan:315`); OpenCode install (`plan:197`, `plan:316`); M4 web UI install (`plan:305`); live U2 commands (`plan:389`); automatic swaps and `/free` through a recorded standing approval with scope, cap and expiry (`plan:298`, `plan:314`, matching `10_packs/fleet/external-actions-need-derricks-exact-yes.md:12`); Windows startup task (`plan:318`); agy `--dangerously-skip-permissions` ("Until he answers, it is not used", `plan:317`), with permission prompts left on (`plan:198`). Nothing is pre-approved.
- **Missing gates:** the U12 benchmark, drill and destructive-step test (R-10); a possible llama.cpp upgrade (R-24); the power-plan settings change (R-14); the M2 row change versus a websockets install (R-09).
- **Over-applied gates:** none found. No read-only or box-only step is gated. The non-Shell status read (`plan:313`) is a real lease question, not over-gating. The closest issue is placement, not a gate: U1 is docs-only but placed on AlienPc (R-15).

## 5. Sequencing and testability

Method: I traced the dependency graph (`plan:261-277`, `plan:356-369`) against each unit's test scenarios, looking for anything used before it exists, then checked each unit's exit criterion and rollback.

- Order is acyclic and mostly sound. Use-before-exist problems: status in U6 and U8 (R-12); U7 tests job and session handlers that arrive in U8 and U10 (acceptable with fakes, P3, not counted).
- Every code unit has concrete test scenarios and a verification line. U1 and U12 have weak or circular checks (R-21, R-20). U2's checklist can't fully pass (R-09).
- There is no rollback anywhere (R-13). Box and AlienPc work are not split (R-15, R-01).

## 6. VRAM arithmetic (from the plan's and research's numbers)

- Card: 16 GB on the Windows display GPU, with about 14.5-15 GB usable (research `:6`). Comfy-idle free is 14782 MiB ≈ 14.44 GiB, measured before dynamic VRAM was turned on (`plan:303`).
- 9B vision: 9.53 + 0.92 GB ≈ 10.45 GB, matching the plan's "~10 GB". This fits, with about 4 GB left for KV and images.
- 27B idle (IQ3_S-mtp, 12.12 GB file): 14.0 GiB at 32K f16 KV and 14.1 GiB at 64K q8_0. Against 14.44 GiB free, that leaves **about 0.3-0.4 GiB**. That's before dynamic-VRAM residue, the Windows desktop, or a coding agent wanting more than 32K context. "Always loaded" will need a `/free` on Comfy after most Max jobs, and Max's next render then runs cold (R-07).
- The LLM and ComfyUI can never run together, which the plan already scopes out (`plan:159`). That holds.

## 7. Fix order

1. R-01, then R-05 and R-04 (lease mechanics; nothing touches AlienPc until these are done).
2. R-02, then R-03 (restore the open question; get Derrick's decision on Max-request behaviour before U6).
3. R-06 and R-07 (model paths and the idle profile size).
4. R-15 (decide what moves to the box), then R-12 and R-08 (unit test boundaries; pin U2).
5. R-09, R-10, R-11, R-13, R-14 (live-unit gates, observability, off switch, runner lifetime).
6. R-16 and R-17 (lane QA plumbing).
7. P3s: R-18 through R-24.

## 8. Could not verify

- The director code at `abcfc3d` and `.agents/rules/10-gpu-safety.md`: both are on AlienPc, which I did not access. Conflicts 2, 6 and 9's .venv state were taken from the plan.
- Derrick's settled decisions: RELAYED from the request. I found no shared-memory file for them on the box.
- The refused director-repo Read (conflict 4) and the planning pass's Shell use (conflict 11): self-reported by the plan.
- Whether Derrick already approved agy quota spend for building, which counts as credit spend under the fleet pack: ASSUMPTION that he did, based on `plan:22`.
- Whether a running background process counts as Shell ownership under the 4:36 rule: needs Derrick (R-14).

## Coverage

| Lens | Applied by | Findings (lead) |
|---|---|---|
| coherence | this reviewer (single pass) | R-02, R-04, R-12, R-18, R-19, R-20, R-23 |
| feasibility | this reviewer | R-01, R-07, R-08, R-09, R-11, R-13, R-14, R-24 |
| scope-guardian | this reviewer | R-06, R-10, R-15 |
| adversarial | this reviewer | R-03, R-05, R-21 |
| security-lens (light) | this reviewer | R-16, R-17, R-22 |

Cross-model pass: skipped (`cross_model_review_mode: off`). Applied fixes: none (report-only). Review round 1 of at most 2.
