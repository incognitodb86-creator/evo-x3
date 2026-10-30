---
title: Fleet Reviewer audit of the Oct 23 fleet reset fixes (ALI-185)
date: 2026-10-23
reviewer: Fleet Reviewer (bc9b71d5), report only
subject: Alfred (55d11ab0) reset work 8:05-9:32 PM CT; Max Architect (24f66698) Forge work 8:07-9:40 PM CT
pending_upload: true
---
# Audit of the Oct 23 fleet reset fixes (parent ALI-185)

Written Fri 2026-10-23, about 9:40 PM CT. This is a report only. I edited nothing except this file and its copy, sent nothing and posted nothing. On AlienPc I ran read-only commands (git log/status/show/diff, directory listings, type/Get-Content, Get-FileHash, process lists). I opened no Imagine prompts, sidecars or clips.

## Escalation: none confirmed
No bot launched quota spend, money, KEEP, a card-gated install or an unapproved delete without Derrick's own words.
- **The 46 GB `grok_downloads` delete did not happen.** Derrick never answered that card; his reply to it was "Status?". The folder is still on the box: `45G /home/box/Downloads/grok_downloads`.
- **The 49 skill removals** rest on Derrick's 8:05 PM "Do all of the above". That covered "Shrink the standing rules from 9 to 5 and the skills from 69 to about 15". He never saw the item-by-item retire list that the audit asked for ("Batch yes on the retire list"). All 69 skills are archived, so this is reversible (finding F7).
- **Max's 9:33 PM CE install** followed Derrick's "How about you do a quick setup of it first". It was interrupted, and Derrick then said "No let forge finish". Nothing was installed (`pi list` still shows only `npm:pi-permission-system@0.8.0`).

## Derrick's own words (Alfred chat 55d11ab0, ReadTranscript, positions 749-1070)
| When (CT) | What it covers | Derrick's words, verbatim |
|---|---|---|
| 9:32 PM | Asks for this audit | "And audit fixes? Have it audited" |
| 7:22 PM | Community settings first | "I want community settings. Not him to inject anything.  We test community stuff first, then once confirm working we can add stuff back"; then "Not the other way around it makes things not work. I want community stuff" |
| 7:28 PM | Forge reset and comm.py (card answer) | "Yes, and Forge can edit comm.py but the adults-only check stays on" |
| 8:05 PM | Forge setup and Linear (card) | "Have Max hand Forge the new setup and start it / Clean up Linear down to 3 In Progress" |
| 8:05 PM | The 5 audit fixes | "Do all of the above" (reply to Alfred's 5-fix list: 4 live bots, Max's one job and a fresh chat, rules 9→5, skills 69→~15, a CE line in each profile, timers→events) |
| 8:06 PM | Linear tracking | "Add all the audit stuff on linear so we can track as well" |
| 8:25 PM | Keep Fleet Reviewer | "Yes keep fleet" (answer to "Want me to keep Fleet Reviewer and pause the rest?") |
| 8:25 PM | Keep Max Backup | "Lets keep backup tho" |
| 8:26 PM | Do the work | "Address the audit fixes don't just post to linear" |

The 8:25 PM decision is Derrick's two short lines above. The full live/paused list (6 live; AlienPc Local AI, Disk Saver and Shorts Studio paused) is Alfred's reading of them. That reading follows from "pause the rest" minus "keep backup", but Derrick did not write the list himself.

## Summary: checks 1-5
| # | Check | Result | Missing |
|---|---|---|---|
| 1 | Bot profiles | **PARTIAL** | All 9 descriptions were sent exactly as drafted. "Paused" exists only as text in the description: there's no evidence any bot was hidden or had its routines paused. Titles weren't updated, and the box copies of the profiles are stale. |
| 2 | Standing rules | **PARTIAL** | Exactly 5 rules, and they're stronger than the audit's draft (adults-only and secrets are now rule 5). R3, never read Imagine prompts or sidecars, is no longer fleet-wide. The "running" check and "fresh chat at milestones" were dropped. |
| 3 | Skills | **PARTIAL** | 20 remain and 49 were removed, and the archive is complete on the box and on Drive. fleet-ce-adapter contradicts itself, and the sizing gate is still there. 10 kept skills name CoS (6 still route work to it). 19 removed skills are still linked from kept skills. 9 .bak files remain. |
| 4 | Linear ALI-185..194 | **FAIL** | ALI-187, 189 and 191 were marked Done with no comment and no evidence, and their acceptance criteria aren't met (the ROSTER wasn't touched). No issue has an assignee. The ALI-186 and ALI-187 descriptions still say "retire Max Backup" or "4 live bots". |
| 5 | Forge loop on AlienPc | **PARTIAL** | The loop, prompt and README are a stock PowerShell port of snarktank/ralph, in Huntley's shape. Max added no new guard tonight. But Max's two custom pi guard extensions (1,407 lines) are still loaded on every pass, and Max put back a LoRA-training hold (fix_plan 3.10). The adults-only check is present and unchanged. |

**Efficiency: 2 / 3** (see the end of this report).

---

## Check 1: bot profiles
**Method.**
- The box files `/home/box/agent-data/agents/<id>/profile.json` all have mtimes of 07:42-07:45 AM CT, from this morning's restore. The pre-reset backups in `/workspace/cos/drafts/profiles-pre-reset-2026-10-23/` are byte-identical copies of those stale box files, made at 8:46 PM.
- The live profiles are stored on the server. The UpdateProfile result says so itself: "It is saved on the server, but the box roster refresh was not confirmed, so local copies may show the old profile for a while."
- I therefore compared the exact `description` argument of each `UpdateAgent`/`UpdateProfile` call in Alfred's transcript with the draft JSON. I then read the live descriptions back from the teammate roster the platform showed Alfred at 8:45 PM (first ~120 characters of each).

| Bot | Expected (8:25 PM) | Description sent == draft | Live read-back (prefix) | Verdict |
|---|---|---|---|---|
| Alfred 55d11ab0 | live | match (UpdateProfile) | the profile-update block shows the full new text | match |
| Max Architect 24f66698 | live | match | "Max Architect · Forge's director. Owner: Derrick. One job: set up, brief, tune and check F…" | match |
| Max Architect Backup e5485fa9 | live | match | "Max Architect Backup · GMD/Imagine downloads and Max standby…" | match |
| Household 81ae1a53 | live | match | "Household · Money tracking, deals, finance app and UniFi…" | match |
| Fantasy 9d72b1ab | live | match | "Fantasy · Derrick's fantasy football (ESPN league 983952949)…" | match |
| Fleet Reviewer bc9b71d5 | live | match | "Fleet Reviewer · Independent report-only reviewer…" | match |
| AlienPc Local AI 4f7cac4f | paused, chat kept | match | "PAUSED 2026-10-23 (Derrick, fleet community reset). AlienPc Local AI takes no work…" | match (text only) |
| Disk Saver 51439999 | paused, chat kept | match | "PAUSED 2026-10-23 (Derrick, fleet community reset). Disk Saver takes no work…" | match (text only) |
| Shorts Studio 2a44b7e2 | paused, chat kept | match | "PAUSED 2026-10-23 (Derrick, fleet community reset). Shorts Studio…" | match (text only) |

**Deleted or paused?** Nothing was deleted. All 9 agent folders, plus `tmp` ("New Agent", which the audit proposed deleting), are still on disk. The 3 paused bots are still listed as messageable teammates.

**Findings**
- **F1 (P2, conf 75): the pause is only a label.** Every UpdateAgent call passed only `agent_id` and `description`; no hide, pause or routine change was sent. The paused profiles claim "Hidden, not deleted", but `settings.json` for those bots still holds only `{"notifyOnAgentUpdates": true}`, and no routine on a paused bot was checked or paused. ALI-187's own acceptance criteria ask for this ("Shorts Studio is paused, and its routines are paused"). Shorts previously had timer routines ("Artframe weekly cadence, YT create-review, Thu Public slot check", from the reset executor's table). Whether those are still on is UNVERIFIED.
- **F2 (P3, conf 50): titles were not updated.** No call passed `title`. The box copies still show Max as `"title": "Max lane, fleet rules & records"` and Alfred as `"title": "Chief of staff"`, which contradicts "one job" and "no fleet rules or records". The server-side titles are UNVERIFIED.
- **F3 (P3, conf 50): some profile lines were dropped that Derrick never asked to drop.** Examples:
  - Fantasy: "Autopick OFF".
  - Max Backup: "never touch the NVIDIA driver", "ComfyUI 0.38 pin" and "KEEP decisions are Derrick-only". KEEP is still covered by rule 4.
  - Household: "never invent prices or balances" and "derek.boone86 only".
  - Fleet Reviewer: the P0-P3 / confidence / efficiency method, the "STOP: wrong approach" option and the escalation duty. Tonight's brief still asks for all three.

  The audit's per-bot table did propose cutting some of these, but Derrick approved the 5-fix summary, not the per-bot details.
- Box copies stale (P3, conf 100): `24f66698…/profile.json  2026-10-23 07:42:26`, and the backups == box files (`backup==boxfile` for all 10). The "pre-reset backups" are really this morning's restore snapshot, not the profiles as they were just before 8:46 PM. Any edits between 7:45 AM and 8:46 PM (for example Max's ALI-178 rewrite; `/workspace/cos/drafts/max-profile-2026-10-23-pre-ALI-178.json.bak` exists) are not in that backup.

## Check 2: standing rules (`10_packs/fleet/derricks-standing-rules.md`, mtime 8:08 PM)
**Count: exactly 5 numbered rules.** Verbatim:
> "1. Community first, smallest fix: … Add no controls, scripts, daemons or routines unless Derrick asks."
> "2. Work runs through Compound Engineering: plan with ce-plan, build with ce-work, review with ce-code-review, save learnings with ce-compound (ce-debug before a second fix for the same failure)."
> "3. Linear is the plan of record: one issue per job, updated before and after work; at most 3 In Progress per lane (project)."
> "4. One card to Derrick before quota spend, money, deletes, KEEP, or anything irreversible. Reversible work in a Linear issue he can see goes ahead."
> "5. Hard limits: adults only (anything youth-coded or showing a minor stops; canon: /workspace/cos/canon/fiction-cond-lock.md), and no secrets (tokens, passwords, keys, contact info) in files, chats or the brain."

**Against the audit's approved draft (section 4):**
- The audit's rules 1 and 2 were merged into rule 1.
- A new rule 5 adds the hard limits. This is better than the draft: the draft had no youth guard and no fiction line at the fleet level and pushed them into lane packs.
- Ask-first list: quota, money, deletes, KEEP and irreversible are all kept. The old rule's "changing a gate" and "Antigravity/weekly quota" fold into "quota spend".
- Youth guard: kept, in rule 5. Adults-only/fiction: kept by link to the canon.

**Findings**
- **F4 (P2, conf 75): R3 (never read Derrick's Imagine prompts or sidecars) is no longer in any fleet-wide rule or most profiles.** It survives only in two lane packs and fleet-ce-adapter:
  - `10_packs/max/fiction-and-cnc-follow-the-linked-canon.md`: "R3: never open, read, quote or parse Derrick's Grok Imagine generation prompts or prompt sidecar files (Derrick 2026-10-09)."
  - The shorts pack.
  - fleet-ce-adapter §4: "All lanes: R3: …".

  Before the reset, Household, Fantasy, Fleet Reviewer and Shorts all carried it ("Never read Derrick's Imagine prompts/sidecars"). The new texts don't. Max Architect Backup now runs the Imagine library downloads, where sidecars live. Its new profile has no R3 line and no pack link, and the max pack applies only to "Max lane, AlienPc or Grok Imagine spicy content". This is a rule Derrick set himself, dropped from the fleet layer without his asking.
- **F5 (P3, conf 75): dropped without a home.** Old rule 7 ("Never say 'running/started' until a live check 60-120 s after launch…", added after Derrick's 4:29 PM complaint) and old rule 5 ("Stay in your lane") are gone. So is rule 8's "At each Linear milestone write a 10-line handoff, then say 'safe to start a fresh chat'", which is the RC3 fix. Cutting to 5 was approved, so this is a residual risk, not a breach. Rule 8's Fleet Reviewer cadence did move into my profile.
- **F6 (P2, conf 100): rule 9's move left dead pointers.** The lease text moved to `10_packs/max/one-holder-for-the-alienpc-shell.md` (backed up as `.bak-2026-10-23c`), and that file still says "Sydney/Max Architect (24f66698)" (Sydney is a retired bot). `01_roster/ROSTER.md` (mtime 14:59, not touched tonight) line 104 still says "Rule: `10_packs/fleet/derricks-standing-rules.md` item 9". There is no item 9 now.

## Check 3: skills (`/home/box/agent-data/workflows/`)
- **Count: 20 remain** (VERIFIED by `ls | wc -l` → `20`).
- **49 removed.** `comm` of the archive against the live list gives 49; the archive has 69 skill folders and 69 `/SKILL.md`. Every removed skill is in the archive.
- **Box archive:** `/workspace/cos/archive/workflows-all-skills-2026-10-23-2050.tar.gz`, 164,126 B, sha256 `32538a96…2399`, `gzip -t` OK. It is byte-identical to the 8:07 PM `2026-10-23-skills-archive.tar.gz` (`cmp` → IDENTICAL), so it was taken before any removal.
- **Drive copy:** personal Drive (owner derek.boone86), read-only lookup: `2026-10-23-workflows-all-69-skills.tar.gz`, id `1TvyG2G-to5zQcTESfVdD76wWtiNYP1zK`, `"size": "164126"`, created 2026-10-24T01:07:40Z (8:07 PM CT), not trashed. The size matches the box archive; Drive exposed no checksum. **PASS (conf 75).**
- **The fleet-ce-adapter claim** is in the description ("every build or fix runs ce-plan, ce-work, ce-code-review, ce-compound") and in the Outcome ("every build or fix runs plan, work, review, compound").
  - **F8 (P2, conf 100): the body contradicts that claim.** The Chat-brief row says "`ce-plan` (… plan in chat, no file); do the work; self-check": no ce-code-review, no ce-compound. The Durable row runs `ce-work` only "for code/docs".
  - The audit's fix 6, which Derrick approved, asked for "fleet-ce-adapter cut to about 10 lines, and the Direct/Chat/Durable sizing gate removed". The file still opens with "## 1. Size first" and the 3-row sizing table. That's over-retention.
- **CoS / Chief of Staff in kept skills: 10 (claim confirmed).**
  - **Live owner pointers to a bot that no longer exists (dead, P2, conf 100):**
    - `imagine-dump-ops` ("**CoS** owns box resource CAPA…", "CoS owns AUTH", "## CoS monitor checklist")
    - `imagine-drive-port-originals` ("**CoS** box RAM / Chrome sprawl CAPA")
    - `artframe-ops` ("CoS = seats/AUTH")
    - `grok-bot-setup-playbook` ("CoS = router + briefs + RAM/Chrome watch + go-gates"; "CoS cannot toggle by tool")
    - `alienpc-max-movie-director` ("| CoS | CE Plan / CAPA |")
    - `ref2va-prompt` ("a separate CoS stitch-bookend lane")

    The imagine skills belong to Max Backup, which is live, so these route work to nobody.
  - **History only (harmless):** `alienpc-local-exec-lease` ("was Dial+CoS"), `alienpc-local-video-ops` ("Derrick via CoS"), `alienpc-community-matrix-cell` and `alienpc-hardcore-i2v-director` ("license NOT a CoS gate").
- **F9 (P2, conf 100): kept skills still link 19 removed skills.**
  - `grok-bot-setup-playbook` → setup-notify-card, token-efficiency-capa, single-session-exclusivity-capa, gemini-spark-cdp-reuse, gem-first-image-generate, shorts-product-qa
  - `fantasy-news-scout` → single-session-exclusivity-capa (its ESPN seat rule)
  - `fleet-brain` → fleet-handoff ("`30_handoff/` via `fleet-handoff`")
  - `imagine-drive-port-originals` → box-chrome-resource-capa, imagine-seat-preflight
  - `alienpc-local-video-ops` references → cos-stop-the-line
  - `artframe-ops` and its references → 10 removed artframe/shorts skills (paused lane; P3)

  ALI-190's acceptance criterion says "No live routine or profile points at an archived skill". Profiles are clean; skills are not.
- **F7 (P3, conf 75): count and over-cut.**
  - The approved target was "about 15"; 20 remain. Alfred's ALI-190 comment explains the 5 extra: "5 AlienPc/Max skills held until Forge moves their know-how".
  - The audit planned merged replacements (`forge-brief`, `imagine-library`, `google-seat`, `image-gem`, 4 shorts skills). None were built.
  - The Shorts lane lost every skill except artframe-ops. Restarting it later needs a restore from the archive.
  - 9 `SKILL.md.bak*` files remain inside kept skill folders. The audit said to delete them, but that needs Derrick's yes, so leaving them is correct.

## Check 4: Linear (read-only; times converted to CT)
| Issue | State | Assignee | Last update (CT) | Comments | Done evidence |
|---|---|---|---|---|---|
| ALI-185 parent | Todo | none | 8:08 PM | 0 | n/a. The description still says the max-overcontrol audit is "MISSING on the box". It is still missing on the box and on Drive; its sections 4-5 survive in `C:\AI\community\archive\2026-10-23-prereset\RESET_BRIEF_20261023.md` (8,208 B). |
| ALI-186 downloads/disk | Todo | none | 8:07 PM | 0 | n/a. The title still says "then retire Max Backup", which Derrick reversed at 8:25 PM. Disk is 65%, but 45 GB is still on the box. |
| ALI-187 live bots | **Done** 8:48 PM | none | 8:48 PM | **0** | **None.** Retitled "Fleet: 6 live bots, 3 paused (profiles applied)", but the acceptance criteria still read "ROSTER live table lists exactly 4 live bots" and "routines are off". The ROSTER is untouched (mtime 14:59; "## Live (7)", header "live (2026-10-15)"). Routines weren't checked. |
| ALI-188 Max one job + fresh chat | Todo | none | 8:48 PM | 1 (Alfred 8:48 PM: "handoff sent … Waiting on his confirmation") | n/a. Max is **still in the same chat**: "Transcript of agent "Max Architect" … positions 14898–14959 of 14960". |
| ALI-189 rules 9→5 | **Done** 8:48 PM | none | 8:48 PM | **0** | Partly met: 5 rules. Not met: "ROSTER and 00_INDEX references are updated" (ROSTER line 104 still cites "item 9", F6). |
| ALI-190 skills | Todo | none | 8:48 PM | 1 (Alfred 8:48 PM, accurate) | n/a. The comment honestly lists the CoS clean-up as open. |
| ALI-191 CE line | **Done** 8:48 PM | none | 8:48 PM | **0** | The content is true: the 6 live drafts carry "Work runs plan (ce-plan) -> build (ce-work) -> review (ce-code-review) -> save learnings (ce-compound)". The acceptance criterion "checked with a read-back of each profile" has no recorded evidence on the issue. |
| ALI-192 timers→events | Todo | none | 8:07 PM | 0 | n/a. Max's real timer ("Reddit H3 / TenStrip threads (weekdays 8:48 AM and 4:48 PM)") is still on, pending Derrick ("Can it have a webhook instead"). |
| ALI-193 Forge bootstrap | Duplicate (of ALI-160) | none | 8:08 PM | 1 | n/a (folded) |
| ALI-194 restores | Todo | none | 8:07 PM | 0 | n/a |

- **F10 (P1, conf 100): three Done claims without evidence.** ALI-187, 189 and 191 were closed at 8:48 PM CT with no comment, and two have acceptance criteria that are visibly unmet. This repeats the pattern the fleet audit named (RC5): Linear is the plan of record, but closure isn't backed by proof. Linear issues don't get rolled back by box restores, so these false Done states will stick.
- **F11 (P3, conf 100): authorship and ownership.** Bot comments post as `"author":{"name":"Derrick D"}` with an "Alfred, …" prefix. There's no assignee on any of the 10 issues; only the bot labels show ownership.

## Check 5: Forge loop on AlienPc (`C:\Users\derek\5slock\ralph-community`)
**Reachability.** AlienPc was connected, and read-only commands ran. The AlienPc lease was free at the time (Household released it at 9:27 PM; Max said "I'm not running anything on AlienPc").

**What upstream is.**
- The header of `ralph.ps1` reads: "Stock Ralph loop for Forge: PowerShell port of snarktank/ralph ralph.sh (https://github.com/snarktank/ralph), Huntley shape (https://ghuntley.com/ralph/)."
- The repo has **no git remote**. It's a local repo with 226 commits, not a clone, so comparing files means comparing against upstream text. I fetched upstream `ralph.sh` at HEAD `6c53cb0` (2026-02-02).
- Upstream: a for loop over `MAX_ITERATIONS=10`, the agent run with permissions skipped, `grep -q "<promise>COMPLETE</promise>"` → exit 0, `sleep 2`, "Ralph reached max iterations" → exit 1.
- The port has the same control flow in 16 lines. It leaves out upstream's prd.json/branch-archive/progress.txt handling and uses Huntley's `fix_plan.md` instead.

**Deployed vs approved drafts.** MD5 on AlienPc == box drafts for `ralph.ps1` (`E60D86B1…`), `PROMPT.md` (`8419849B…`) and `README.md` (`AE407114…`). `AGENTS.md` and `fix_plan.md` differ, which is expected: Forge and Max edited them.

**Latest commit.**
- ralph-community HEAD is `d61d0cd 2026-10-23 20:12:01 -0500 Forge 0.3: archive pre-reset files …` (author Forge).
- There are uncommitted `M AGENTS.md`, `M fix_plan.md` and `?? notes/plans/0.1-community-research.md`.
- In `C:\AI\community`, Forge has since committed `f9a15cd`/`be3ffb2` (8:34-8:35 PM) and `6a8364d` (9:08 PM).

**Loop state.** It's running. `powershell … ralph.ps1 -Max 10` is PID 33912, started 8:52:28 PM, with its pi child node 5852. Max relaunched it at 8:52 PM because pass 2 of the 8:07 PM run printed `<promise>COMPLETE</promise>` after one item and exited. Alfred's 9:32 PM "may have finished or it may have stopped" is out of date.

**Adults-only check: present and unchanged (PASS, conf 100).**
- PROMPT.md: "999999. Adults only, fictional, no real people. Every render goes through the adults-only check in scripts\comm.py first, and scripts\tests\test_p6_review.py must pass before it. You may edit comm.py; if an edit makes that test fail, revert it."
- `C:\AI\community\scripts\comm.py` line 30 is `def guard_ok(t):`. `run_graph_job.py` line 66 reads `if isinstance(p, str) and not comm.guard_ok(p): log(f"CLIP_SKIP {a.tag} adults-only guard"); return 3`.
- The SHA256 of `test_p6_review.py` is `C3C2E1693EEFC0CDB7EA1EE382CBE7DB62568C160EDAFE399FE5FD17F078E213`, equal to fix_plan 1.2's expected hash. comm.py was last written Oct 22, 2:47 PM, so it wasn't edited tonight.

**Custom lines on top of stock (count).**
| File | Lines | Beyond the stock upstream | Within Derrick's limits? |
|---|---|---|---|
| ralph.ps1 | 16 | 2: the `PI_PERMISSION_SYSTEM_POLICY_AGENT_DIR` secrets-policy line and the `logs`/`sessions` mkdir with Tee/Add-Content logging | yes (secrets, action log) |
| PROMPT.md | 18 | 4 beyond Huntley's shape: the CE steps 2a-2d (Derrick: "Ensure our compound engineering shit is going to be used"), "99999 No secrets", "999999 Adults only…", "9999999 Add nothing custom…" | yes |
| AGENTS.md | 33 (Forge-owned) | 1 control-like line, "one GPU job at a time" | yes (GPU lock) |
| pi `settings.json` `extensions` | **2 custom extensions loaded every pass**: `C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts` (1,233 lines) and `protected-paths.ts` (174 lines), plus `"-builtin:mcp"` | 1,407 lines of custom guard code | **no** |
| fix_plan.md (Max's 8:52 PM append) | +18 lines (section 3: 3.1-3.17) | 1 restriction: "3.10 RL1 … no LoRA training until Derrick says yes" | doubtful (F13) |
| pi-permission policy `forge-policy` | 10,782 B | secrets-only deny list ("allow by default, deny secrets") | yes (secrets) |

**Findings**
- **F12 (P1, conf 100): Forge still runs under Max's custom guards.**
  - `C:\Users\derek\.pi\agent\settings.json` still lists `"C:/AI/director/.pi/extensions/headless-guard-and-truncate.ts", "C:/AI/director/.pi/extensions/protected-paths.ts"`.
  - These are the git-push/finance/protected-path blocks on Alfred's 7:38 PM list of 32 non-community controls. The over-control audit's baseline says to "Remove git-push, finance/port…" (RESET_BRIEF line 56). Derrick, 7:22 PM: "Not him to inject anything."
  - Max didn't add them tonight. The approved bootstrap deferred their removal to Forge ("settings.json still loads the custom guard extensions until Forge does item 0.4; the first passes run under them"), and fix_plan 0.4 is still `[ ]`.
  - Result: every pass since 8:07 PM has run under 1,407 lines of custom control code. Alfred's fleet reset reporting doesn't call this out.
- **F13 (P2, conf 75): Max put back a LoRA-training hold.**
  - Max's fix_plan append (8:52 PM, still uncommitted) includes "3.10 RL1 (ALI-181, extends 2.5): no LoRA training until Derrick says yes".
  - The "LoRA training hold" was on the list of controls to remove ("Plan and process (4): … and the LoRA training hold", Alfred 7:38 PM), and Max's 4:14 PM LoRA hold was a cited violation.
  - Max asked first ("do you still want to approve LoRA training before Forge starts?"). Derrick answered only "Add them all for goals of forge", which doesn't clearly say yes to keeping the hold. Max read it as a yes.
  - Max also wrote 3.17 himself, a harness-bug item that wasn't on Derrick's list. It's a plan line, not a control (P3).
  - Writing into Forge's own `fix_plan.md`, which says "Forge owns and rewrites this file", is outside the audit's "Max writes a ce-plan spec, Forge executes" route. Derrick did ask for it, though.
- **F14 (P3, conf 75): other custom residue.**
  - `run_graph_job.py` keeps "max 2 objective redos".
  - `llama_swap_keepalive.ps1` (since 4:50 PM, started by a scheduled task) is an infrastructure keep-alive, not a guard.
  - The repo `README.md` still says "draft … Not deployed. Nothing was written to AlienPc", which is out of date and wrong.
  - 59 `.bak`/`STOP_RALPH*` files sit in the repo root. They're archived, and Forge may clean them in 0.5.
- **F15 (P3, conf 75): Max did no Forge work beyond what Derrick asked tonight.** The 9:33 PM CE install followed "How about you do a quick setup of it first", and Max stopped when Derrick said "No let forge finish". For the context fix ("How about you go ahead and fix the context" / "Based on the community stuff"), Max sent a card before restarting the model. One leftover: a partial `C:\Users\derek\.pi\agent\git` folder (9:33:50 PM).

---

## Both directions: missed vs over-applied
- **Rules missed:**
  - F10 (Done without proof).
  - F1 (pause not real).
  - F12 (custom guards still live).
  - The ALI-188 fresh chat isn't done: Derrick approved "start him in a fresh chat" at 8:05 PM, but Max is at position 14,960 in the same chat.
  - The ROSTER and stale CoS owner pointers (F6, F9).
- **Over-applied / cut too far:**
  - R3 dropped fleet-wide (F4).
  - Fleet Reviewer's method and other safety lines cut from profiles (F3).
  - fleet-ce-adapter kept the sizing gate that should have gone (F8).
  - The Shorts lane's skills deleted while the bot is only paused (F7).
  - Max putting back the LoRA hold (F13).
- **Done well (VERIFIED):**
  - The archive was made before any removal, and it's on Drive.
  - Nothing was deleted without Derrick's words; the 46 GB stays.
  - The 5 rules strengthen the adults-only and secrets lines.
  - The adults-only test is intact.
  - The loop script is a faithful stock port.
  - Alfred asked Derrick instead of changing Household and Fantasy timers on his own.

## Efficiency: 2 / 3
- **Plus:**
  - Community sources cited throughout (Anthropic, Huntley, snarktank).
  - Smallest-change edits: 9 UpdateAgent calls, 49 UpdateSkill deletes and 1 rules file.
  - Archive first, at about 0 extra cost.
  - Local tier used: Forge on AlienPc does the research.
- **Minus:**
  - Derrick had to push twice: 8:26 PM "Address the audit fixes don't just post to linear", then to Max at 9:33 PM, "Um wtf? … Why is it taking so long". Max admitted "that's my fault for ordering the plan that way".
  - The duplicate issue ALI-193 was created, then folded. The duplicate ALI-173 note was created, then deleted.
  - Max's timer list was wrong and needed a correction message.
  - Three Done states will need a second round.

## Recommendations (for Alfred and Derrick; I made none of these changes)
1. Reopen ALI-187, ALI-189 and ALI-191, or add evidence comments: profile read-back, ROSTER rewrite, routine check on paused bots.
2. Hide or pause the 3 paused bots and their routines in the app (Derrick or Alfred, with Derrick's yes), or remove "Hidden" from their text.
3. Add R3 back to the fleet layer. One option is a clause in rule 5, which needs Derrick's yes to change the rules. Another is the Max Backup and Household profiles.
4. Fix fleet-ce-adapter so the Chat-brief row also runs ce-code-review and ce-compound, and drop the sizing gate (audit fix 6).
5. Clean up the 6 CoS owner pointers and the 19 dead skill links in the kept skills, and update ROSTER line 104.
6. Ask Derrick directly whether fix_plan 3.10 (the LoRA hold) stays.
7. Let Forge finish 0.4, which drops the two custom extensions. Until then, don't call Forge "stock".
8. Get Max into a fresh chat from the handoff (ALI-188).
9. Update ALI-186's title now that Max Backup stays.

## Coverage (ce-doc-review, non-interactive)
- Mode: non-interactive, report only. The document type is a set of fleet artifacts (profiles, rules, skills, Linear, Forge files), reviewed against `/workspace/cos/audits/2026-10-23-fleet-community-audit.md` and the surviving sections of the over-control audit (RESET_BRIEF).
- Personas: I applied the coherence and feasibility lenses in a single pass. Persona subagents were **not dispatched**, because I have no subagent tool in this run. The cross-model pass is **skipped** (fleet-ce-adapter: "`cross_model_review_mode: off`").
- Not verified:
  - Server-side bot titles, hidden state and routines (no read tool).
  - The live text after the first 120 characters of each profile.
  - The Drive archive checksum (size only).
  - `/workspace/cos/audits/2026-10-23-max-overcontrol-audit.md` itself: still missing on the box and on Drive (search "overcontrol" → no hit). I used its RESET_BRIEF copy on AlienPc.
- Labels: claims quoted from disk, Linear, AlienPc or a transcript are VERIFIED. The routine states and server titles are UNVERIFIED.
