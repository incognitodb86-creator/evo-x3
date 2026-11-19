# Fleet audit against community practice (2026-10-23)

- **Asked by:** Derrick, 7:45 PM CT: "audit all our bots skills instructions subagents ect. i want community for grokbot as well. Why do we keep having all these issues". At 7:46 PM CT he added: "Ensure our compound engineering shit is going to be used."
- **Written by:** Alfred's executor, finished 7:53 PM CT. **This is a report only. Nothing was changed.**
- **Labels:** VERIFIED means I saw it on disk, in a transcript or in Linear this run. RELAYED means a bot said it. ASSUMPTION means an inference.
- **Restore caveat:** most files on the box have mtimes of Oct 23, 7:36–7:48 AM CT, from this morning's restore. The standing rules, ROSTER and 00_INDEX exist and were edited after the restore (2:59 PM CT). Older history (Oct 20–22) is mostly gone; see Root cause 4.

---

## 1. Why the same problems keep happening (ranked)

### RC1. Too many bots with overlapping jobs, all talking to each other
- **9 live bots.** The ROSTER also lists about 40 retired, parked or absorbed ids, all from about 6 weeks of churn. VERIFIED: `01_roster/ROSTER.md`.
- **Three bots govern the fleet:**
  - Alfred: "designs, audits, and governs".
  - Max Architect: its title is "Max lane, fleet rules & records", and the ROSTER says it "absorbed Chief of Staff / router duties" and is the "fleet architect".
  - Fleet Reviewer: "fleet hygiene".
- **Alfred is missing from the ROSTER live table.** The roster's last full rewrite was Oct 15.
- **Max Architect Backup is supposed to be idle**, but today it ran the GMD library download (3:51 PM and 4:21 PM CT, VERIFIED in its transcript). That is Max-lane work done by a second bot.
- **In Max's last hour (7:28–7:46 PM CT)** it handled 4 messages from Alfred and 3 from Household while Derrick waited.
- **Community guidance:**
  - Grok Bot docs: "Create a separate Bot when the work has a distinct goal, set of tools … approval boundary", and "Ask for a single owner at each stage; parallel handoffs create duplicate work and noisy updates." [G1]
  - OpenAI: "maximize a single agent's capabilities first." [O1]
  - Cognition: multi-agent systems work "when writes stay single-threaded". [C2]

### RC2. Each failure gets fixed by adding a rule, gate or skill, not by simplifying
- **Instructions:** 9 profiles total 11,473 characters. The standing rules are 9 items (4.0 KB), and item 9 alone is a paragraph of quotes and exceptions. Lane packs add another 31 files (19.7 KB).
- **Skills:** 69 custom skills, 43,772 words, 244 hard-rule words (NEVER, MUST, ALWAYS, STOP and so on). VERIFIED.
- **Control skills born from incidents:** `token-efficiency-capa`, `box-chrome-resource-capa`, `single-session-exclusivity-capa`, `cos-stop-the-line`, `cos-browser-dispatch` (17 hard rules), `cos-subagent-dispatch`, `setup-notify-card`, `grok-bot-success-scorecard`.
- **Bots copy the pattern.** Max added its own controls to Forge:
  - ALI-175 "Hazard-only permission list + lease check + loop caps in ralph.ps1 (gate)".
  - ALI-154 and ALI-156: a custom per-job unload and a "queue-aware graceful cmdStop".
  - Derrick, 7:21 PM CT: "I want community fucking settings stop adding your own shit". At 7:04 PM: "Why are these in .py? Why not a.md? … What does the community do?" VERIFIED in Max's transcript.
- **Community guidance:**
  - Anthropic: "find the simplest solution possible, and only increase complexity when needed." [A1]
  - Ralph: AGENTS.md should be about 60 lines and "NOT a changelog". [R1]

### RC3. Huge conversations that never restart
- **Transcript sizes:**
  - Max Architect: 14,818 messages, with Derrick at about turn 1,618.
  - AlienPc Local AI: 6,120.
  - Max Architect Backup: 1,638.
  - Fleet Reviewer: 1,156.
- **Rule 8 already asks for "milestone handoff + fresh chat"**, and ALI-176 (F2) is marked complete, but Max is still in the same chat.
- **Community guidance:**
  - Huntley: "The more you use the context window, the worse the outcomes you'll get." Use one task per loop with fresh context. [R2]
  - Grok Bot docs: memory "is not a substitute for an authoritative source". [G1]

### RC4. The disk fills to 100% and the platform restore rolls back days of work
- **What the docs say:** Recover and Reset "rebuild the computer from your last saved data; if the computer can't be reached to save first, very recent changes don't come back." [G1] ASSUMPTION: a full disk is what blocks those saves.
- **Evidence of the rollback (VERIFIED):**
  - Brain git commits jump from Oct 19, 8:19 PM CT to Oct 23, 1:58 PM CT.
  - `/workspace/cos/audits` has 97 files from Oct 10–19 but only 1 from Oct 20–22.
  - The 7:28 PM CT memory fact cites `/workspace/cos/audits/2026-10-23-max-overcontrol-audit.md`. That file no longer exists.
- **What fills the disk:**
  - `/home/box/Downloads` holds 51 GB of the 128 GB disk; `grok_downloads` alone is 45 GB. These are Imagine and GMD library dumps.
  - Disk Saver deleted 20,811 duplicate files (32.66 GB) at 2:24 PM CT (`/workspace/cleanup-log-2026-10-23/result.txt`).
  - Its 7:34 PM CT report says the restore had already copied 13,781 files back and the disk was 100% full, with 924 MB free (RELAYED).
  - The second run (`cleanup-log-2026-10-23b`) deleted 0.
- **Now:** 65% used, 46 GB free (about 7:48 PM CT).
- **Memory pressure too:** one Chrome renderer on Fork-5 (the GMD scan) is using 11 GB of RAM right now.
- **Result:** every restore brings back older rules and files, so bots redo fixes, and Derrick repeats himself.

### RC5. Compound Engineering and Linear are named in the rules but are not how work runs
- **Rule 3 says** "ce-plan before, ce-code-review after".
- **CE artifacts in the brain repo:**
  - 6 plans, all dated Oct 10.
  - 4 reviews, all dated Oct 10.
  - Nothing in `ce/plans` after Oct 10.
- **Skill calls:** I sampled about 500 recent transcript messages across 8 bots and found no Skill tool calls and no ce- runs by Max today (0 CE mentions in about 250 Max messages).
- **Linear:**
  - The AlienPc project has 9 issues In Progress; the cap is 3.
  - Shorts and Fantasy have no Linear issues in the last 3 days.
  - ALI-179 "Event trigger in place of the 20-minute timers" is still unstarted.
- See section 6.

### RC6. Memory is being used as the rulebook, and it contradicts itself
- **113 shared memory facts**, with chains of corrections. For example, "single-AlienPc-executor" (Oct 17) is still in memory beside the Oct 23 rewording.
- **The ROSTER keeps all its addenda.** Lines 99 and 104 still say "single AlienPc executor".
- **Several sources of truth:** profile text, standing rules, packs, ROSTER, memory and skill text all restate the same rules. When one changes, the others go stale (RC4 makes this worse).

---

## 2. Per-bot table

The size column is the profile instruction length in characters. "Recent activity" comes from the transcripts I sampled.

| Bot | Size | Skills named | Recent activity / evidence | Verdict | What to cut |
|---|---|---|---|---|---|
| **Alfred** 55d11ab0 | 407 | none named | Relayed Derrick's words to Max, stopped Forge (7:45–7:46 PM CT) | **Keep.** Sole governance bot, absorbing Fleet Reviewer | Add the one CE line. Add itself to the ROSTER |
| **Max Architect** 24f66698 | 2,048 | alienpc-local-exec-lease | 14,818 messages; adding custom controls to Forge; 3 subagents plus 1 MessageSubagent in about 1 hour | **Keep** as Forge's director only | Cut to about 600 characters: drop "fleet rules & records", the CoS duties, the six-step pre-message checklist, and the rule restatements (link instead). Fresh chat |
| **Max Architect Backup** e5485fa9 | 1,060 | none | Ran the GMD download today while "idle" | **Retire.** Hide it; don't delete | Its whole job. Conversations survive outside the box [G1], and Duplicate a Bot can rebuild a backup if one is needed |
| **Shorts Studio** 2a44b7e2 | 1,711 | 9 lane + 4 CE | Last conversation Oct 10 (49 messages total); dormant | **Keep but pause** until Derrick restarts Shorts | Seat ports, the minors/LoRA restatements (link the pack), and 30 lane skills cut to 4 |
| **AlienPc Local AI** 4f7cac4f | 1,260 | 3 | Last activity Oct 19; job is "Forge tooling records only" | **Retire.** Merge into Max; Forge keeps its own records in git | All of it |
| **Disk Saver** 51439999 | 217 | none | Did the 2:24 PM CT cleanup; the restore undid it | **Merge** into Alfred as one skill | The bot. The real fix is moving the dumps off the box (Fix 2) |
| **Household** 81ae1a53 | 978 | 3 + CE | Finance app via Antigravity on AlienPc, 7:36 PM CT | **Keep** | The 4-skill CE list. Use the one-line route instead |
| **Fantasy** 9d72b1ab | 1,255 | 3 + CE | Lineup moves on Oct 22, done right with approval | **Keep** | The CE line (no engineering work), the archived-draft path text, and other-lane "Never" lines |
| **Fleet Reviewer** bc9b71d5 | 2,537 (longest) | 3 | Two Max audits today (1:59 and 4:11 PM CT) | **Merge** into Alfred as an on-demand fresh reviewer subagent running ce-code-review / ce-doc-review | The bot, its weekly routine, and the 0/25/50/75/100 confidence and efficiency-score scheme |
| *New Agent (tmp)* | 0 | none | Empty | **Delete** (Derrick) | Not applicable |

**Not checked:** I couldn't read Alfred's own main chat (ReadTranscript can't open the main chat). I couldn't list routines: they are server-side, and on disk only Disk Saver has an empty `automations/` folder. Derrick has to check retired ids for live routines in the app; the ROSTER lists the steps.

---

## 3. Skills: retire, merge or shrink (69 → about 15)

### Headline numbers (VERIFIED)
- 69 custom skills (972 KB with references).
- Only 20 are named by any profile or rule.
- 6 are orphans, named by nothing: `bot-fleet-audit`, `gemini-second-opinion`, `imagine-raster-generate`, `shorts-best-prompting`, `shorts-flow-reference-i2v`, `shorts-stills-first-approve`.
- 34 still name retired bots (CoS ×70, Imagine Director, Fleet Notify, Sydney).
- 60 carry the same "CE: follow fleet-ce-adapter" footer.
- 9 `.bak` files sit inside skill folders.
- **Stale content:**
  - `alienpc-local-video-ops` still describes Wan 2.2 (as retired) inside a 1,870-character "current setup" line.
  - The beta5 references are in learnings, not skills.
  - "single AlienPc executor" survives in the ROSTER (lines 99 and 104), not in any skill.
- **Size:** none of the skills is over Anthropic's 500-line limit [A2]. The problem is how many there are, how much they overlap, and how many rules each one carries. The largest:
  - `alienpc-hardcore-i2v-director`: 2,653 words, 18 hard rules.
  - `alienpc-local-video-ops`: 2,405 words, 16 hard rules.
  - `ref2va-prompt`: 1,952 words.

### What to do with each group

| Group (current count) | Action | Keep as |
|---|---|---|
| Fleet controls (10): cos-stop-the-line, cos-subagent-dispatch, cos-browser-dispatch, box-chrome-resource-capa, single-session-exclusivity-capa, token-efficiency-capa, setup-notify-card, grok-bot-success-scorecard, bot-fleet-audit, grok-bot-setup-playbook | **Retire 9, shrink 1.** Built-ins already cover these: approvals, Auto-review, one screen per Bot | `grok-bot-setup-playbook`, about 40 lines: the community targets in section 4 |
| Brain/CE (4): fleet-brain, gbrain-sync, fleet-handoff, fleet-ce-adapter | **Merge into 1.** Drop the CE sizing gate (see section 6) | `fleet-brain`: paths, Drive sync, handoff note |
| AlienPc/Max (7): community-matrix-cell, hardcore-i2v-director, local-exec-lease, local-video-ops, max-movie-director, stills-pose-edit-prompting, ref2va-prompt | **Move the know-how into Forge's own repo** (AGENTS.md, specs, community skills); Forge does the work | `alienpc-local-exec-lease` (shrink to 15 lines) plus `forge-brief` (one page: how Max writes a ce-plan brief for Forge) |
| Imagine (4): dump-ops, drive-port-originals, raster-generate, seat-preflight | **Merge into 1** and write to Drive, not the box (Fix 2) | `imagine-library` |
| Gemini/Google seat and image Gems (9): gemini-spark-cdp-reuse, google-spark-auth, gemini-second-opinion, google-pics-stills, gem-first-image-generate, historical-image-gem, naughty-image-gem, aura-gem-json-prep, nano-banana-4-up | **Merge into 2** | `google-seat` (login and reuse), `image-gem` (one Gem flow, mode by lane) |
| Shorts/Artframe (25) | **Merge into 4. Retire** `youtube-shorts-ops` (202 lines, duplicates artframe-ops), `shorts-best-prompting`, and the 2 experiments (photo-paint-morph, l4-side-feature) | `shorts-research`, `shorts-script`, `shorts-stills-to-clip`, `shorts-qa-publish` |
| Lane (6): household-money-tracker, tech-deals-watch, fantasy-news-scout, fantasy-strategy-cot, last30days-research, research-core | **Keep.** Merge the two fantasy skills | 5 |

### Cleanup for every skill that stays
- Delete the `.bak` files (they already live in git and backups).
- Remove names of retired bots.
- Remove the CE footer.
- Link packs instead of restating them.
- Target about 100 lines or fewer.

---

## 4. Community-target setup

| Question | Community answer | Fleet now | Target |
|---|---|---|---|
| How many bots? | One per distinct goal, tools or approval boundary [G1]; start single-agent [O1]; few writers [C1, C2] | 9 live, about 40 historical | **4 live:** Alfred (governance + review), Max (Forge director), Household, Fantasy. **Shorts Studio paused** until Derrick restarts the lane |
| Instruction length? | AGENTS.md / CLAUDE.md short, ideally under 200 lines, durable facts only [M1]; Ralph's AGENTS.md about 60 lines [R1]; Grok Bot: job, sources, approval boundary [G1] | 217–2,537 characters each, plus 9 rules, 31 pack files and memory | **Under 600 characters per profile:** job, sources, approval boundary, one CE line, link to standing rules. **Standing rules: 5 items, one line each** |
| How many skills? | Skills cost about 100 tokens each until loaded [A2]; useful skills are focused and tested [G1, A2]; build one only after the task works once by hand [G1] | 69 custom, 20 used | **About 15**, each tied to a bot that uses it |
| How much delegation? | Subagents for read-only research or a clean reviewer; writes stay single-threaded [C1, C2]; multi-agent uses about 15× the tokens of chat [A3] | Rule 8 allows 2 parallel workers; Max launches briefing subagents that touch AlienPc | **Inline by default.** Subagents only for research or review. One writer per machine (Forge on AlienPc) |
| Memory hygiene | Memory is not a source of truth; correct stale facts directly [G1]; AGENTS.md is not a diary [R1] | 113 shared facts, with correction chains | **Rules live in one file** (standing rules). Memory holds preferences only. Remove superseded facts |
| Timers vs events | Routines can run on Linear, GitHub, email or webhook events; avoid broad listeners [G1] | 20-minute timers (ALI-179 unstarted); box-resource-watch daemon logs | **Linear-event routines.** No polling daemons |

### Lean standing rules (proposed, 5 lines)
1. Community first: link the community way before building; custom only when nothing fits, and say why.
2. Smallest fix. Add no controls, scripts, daemons or routines unless Derrick asks.
3. Linear is the plan of record: one issue per job, at most 3 In Progress per project.
4. Engineering runs through CE: ce-plan → ce-work → ce-code-review → ce-compound, with ce-debug on any repeat failure.
5. Ask Derrick first for quota spend, money, deletes, KEEP, or anything irreversible.

Lane specifics (the lease, Household's AlienPc scope, the fiction lock) move to the lane pack each one belongs to.

---

## 5. Ordered fix list (each item names the decision it needs)

| # | Fix | Derrick decision needed |
|---|---|---|
| 1 | **Stop the box filling up.** Stop dumping GMD and Imagine output to `/home/box/Downloads`; write straight to Drive or AlienPc, then remove the 45 GB `grok_downloads` copy once the Drive copy is verified. Keep the box under 70% so saves succeed and restores stop rolling back. | "Yes, move the dumps off the box and delete the box copy after a verified Drive copy" |
| 2 | **Recover what the restore lost.** List the Oct 20–22 rule and audit files that vanished (for example, the 7:28 PM overcontrol audit) and rebuild only those that are still live, from Linear and the transcripts. | "Rebuild only live items" vs "accept the loss" |
| 3 | **Cut to 4 live bots.** Retire Max Architect Backup and AlienPc Local AI (hide, don't delete). Merge Fleet Reviewer and Disk Saver into Alfred. Pause Shorts Studio. Delete New Agent. Disable any routines on retired ids. | Yes or no on each bot (5 decisions) |
| 4 | **Give Max a single job.** Rewrite its profile to about 600 characters: "Forge's director: set up, brief, tune, check; Forge does the work." Drop fleet rules and records. Start a fresh chat after a 10-line handoff. | Approve the new profile text |
| 5 | **Shrink the standing rules from 9 to 5 lines** (section 4), with lane exceptions in their packs. Clear superseded memory facts and the ROSTER addenda (move them to history). | Approve the 5-line rules |
| 6 | **Make CE the default route** (section 6): one routing line per profile, fleet-ce-adapter cut to about 10 lines, and the Direct/Chat/Durable sizing gate removed. | Approve the routing lines |
| 7 | **Cut skills from 69 to about 15** (section 3). Retire first, then merge; archive, never delete. | Batch yes on the retire list |
| 8 | **Events over timers.** Finish ALI-179 with Linear-event routines (issue moved to In Review → review; Done → ce-compound). Stop the box-resource and dump-progress watchers. | "Yes, Linear events, no timers" |
| 9 | **Linear clean-up.** Bring AlienPc In Progress from 9 down to 3. Close or merge ALI-146, 148, 149 and 180–184 into one research issue. | Choose the 3 to keep In Progress |

---

## 6. Compound Engineering: is it actually being used?

### What is installed (VERIFIED)
- The CE plugin, with 36 skills, at `/home/box/agent-data/plugins/cache/cursor-public/compound-engineering/*/skills`. That includes ce-plan, ce-work, ce-code-review, ce-compound, ce-debug and lfg.
- The brain repo has `.compound-engineering/config.yaml` and `ce/plans`, `ce/reviews` and `ce/solutions` (which mirrors `20_learnings`).

### What is actually used (VERIFIED)
- 6 ce-plans and 4 ce-reviews, all dated Oct 10. None since.
- 24 learnings (fleet 2, flux2 1, max-video 21).
- Fleet Reviewer's git commits show "ce-plan review" of ALI-99 and ALI-101 on Oct 19.
- In the sampled transcripts (about 500 messages across 8 bots) there were **0 Skill tool calls**.
- The September subagent logs on disk (1,615) contain no ce-plan, ce-code-review or ce-compound at all.

### Why CE isn't used (ASSUMPTION, from the evidence)
1. **`fleet-ce-adapter` puts a gate in front of CE.** It asks for a size first ("Direct = just do it. No ce- skill"), and it says "Never start the chain because a skill exists." The bots size almost everything as Direct.
2. **Profiles list skill names but not when to use them.** Shorts, Household and Fantasy say "CE via fleet-ce-adapter: ce-plan · ce-work · ce-compound · fleet-handoff". None mentions ce-code-review or ce-debug. Max, Backup, AlienPc Local AI, Disk Saver and Alfred have no CE line at all.
3. **The real engineering happens off the box.** Forge runs on AlienPc and Antigravity runs for Household, outside the brain repo CE points at, so ce-* never sees those diffs.
4. **The restore erased the Oct 20–22 trail**, so even any use that did happen is gone.

### Per-bot CE routing

| Bot | Routes work through CE today? | Evidence | Exact line its profile should carry |
|---|---|---|---|
| Max Architect | **No.** Rule 4 says "links a ce-plan file", but there is no CE call | 0 CE mentions in about 250 messages today; last Max ce-plan was Oct 10 | `Forge work: plan with ce-plan (link on the Linear issue), Forge executes, review Forge's commits with ce-code-review, run ce-debug before any second fix, capture learnings with ce-compound into Forge's AGENTS.md.` |
| Household | **Partly.** It names a plan file but doesn't run CE | Transcript mentions `ce-plan-finance-app-rebuild-forge`; no ce-code-review | `Finance app and UniFi: plan with ce-plan, build with ce-work or Antigravity, review with ce-code-review, ce-debug on any repeat failure, capture learnings with ce-compound.` |
| Alfred | **No line** | Profile has no CE line | `Fleet changes: plan with ce-plan, review profile and skill edits with ce-doc-review, capture fleet learnings with ce-compound.` |
| Fleet Reviewer (until merged) | **Yes, for reviews** | Oct 19 "ce-plan review" commits; today's audits mention ce-plan and ce-code-review | `Review with ce-doc-review (plans) and ce-code-review (diffs) only.` |
| Shorts Studio | **No.** Listed, but not used | Last active Oct 10; no CE calls | `Tool or pipeline builds: ce-plan → ce-work → ce-code-review → ce-compound; content work follows lane skills.` |
| Fantasy | **Not needed.** Listed, but there is no engineering work | Only the profile text mentions CE | Remove the CE line. If something must stay: `Capture a learning with ce-compound when a call proves wrong.` |
| Disk Saver (until merged) | **No** | No CE | `Disk keeps filling: run ce-debug before any new cleanup.` |
| Max Backup, AlienPc Local AI | **No** | No CE | Retiring, so no line |

`lfg` is used only when Derrick types "lfg" (unchanged). The adapter shrinks to about 10 lines: where files land (`ce/`), approvals, and "the review is a fresh subagent". No sizing gate.

### How Forge's community bootstrap should use CE (no custom controls)
This follows Huntley's Ralph layout [R1, R2] and Every's Plan → Work → Review → Compound loop [E1].
1. **Plan (Max, on the box).** `ce-plan` writes the spec for one Linear issue. Max copies it into Forge's repo as `specs/<issue>.md`, plus one line in `IMPLEMENTATION_PLAN.md`. Max adds no gates or scripts.
2. **Work (Forge, on AlienPc).** The stock Ralph loop reads `PROMPT.md` + `AGENTS.md` + `specs/*`, picks one task, runs its tests, commits and exits, then restarts with fresh context. Forge may edit its own files. The only fixed checks are the ones Derrick named: secrets, finances, the adults-only check before every render, and logging.
3. **Review (Max).** `ce-code-review` runs on Forge's commit range (`git diff`), at most twice per issue (rule 8). Findings go back as new lines in `IMPLEMENTATION_PLAN.md`, not as new controls.
4. **Compound.** At each milestone, `ce-compound` writes one learning. Only the operational part (build, test and run commands, gotchas) goes into Forge's `AGENTS.md` "Operational Notes", which stays at about 60 lines and is never used as a diary [R1]. Forge then improves itself from that file.
5. **Debug.** The same failure twice runs `ce-debug` on the loop's log before anything new is added (this matches Max rule 2, "harness bug first").

---

## Sources
- [G1] Grok Bot docs, "Work with Grok Bot": https://cursor.com/docs/grok-bot/work (Bots, handoffs, memory, routines, recover/reset). Also https://cursor.com/help/grok-bot/routines and https://docs.x.ai/grok-bot/skills-routines-and-automations
- [A1] Anthropic, "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents
- [A2] Anthropic, Skill authoring best practices / Agent Skills overview (SKILL.md under 500 lines, progressive disclosure, about 100 tokens of metadata per skill): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices , https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- [A3] Anthropic, multi-agent research system (about 15× chat tokens): https://www.anthropic.com/engineering/multi-agent-research-system
- [O1] OpenAI, "A practical guide to building agents": https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- [C1] Cognition, "Don't Build Multi-Agents": https://cognition.com/blog/dont-build-multi-agents ; [C2] "Multi-Agents: What's Actually Working" (2026-04-22): https://cognition.com/blog/multi-agents-working
- [R1] ghuntley/how-to-ralph-wiggum (AGENTS.md about 60 lines, not a changelog): https://github.com/ghuntley/how-to-ralph-wiggum ; [R2] https://ghuntley.com/ralph/ (one item per loop, context degrades)
- [M1] AGENTS.md: https://agents.md/ ; Claude Code memory (keep it short, under about 200 lines): https://code.claude.com/docs/en/memory
- [E1] Every, Compound Engineering: https://every.to/guides/compound-engineering ; https://github.com/everyinc/compound-engineering-plugin

## Evidence paths
- Profiles: `/home/box/agent-data/agents/*/profile.json`. The instructions live in the `description` field; `settings.json` holds only notify flags.
- Skills: `/home/box/agent-data/workflows/*/SKILL.md`
- Rules, roster and index: `/workspace/cos/brain-staging/{10_packs/fleet/derricks-standing-rules.md,01_roster/ROSTER.md,00_INDEX.md}`
- Disk: `/workspace/cleanup-log-2026-10-23{,b}/`, plus `df` and `du` run at about 7:48 PM CT
- Linear: team ALI, 75 issues updated in the last 3 days (read-only query)
