# Fleet Reviewer: did Max follow Derrick's direction on Forge? Fri 2026-10-23

**Verdict: PARTLY. On restrictions it FAILS until the 1:50 PM change lands. On "Forge does it all" it is PARTIAL.**

- Max kept or added narrow rules after 11:09 AM.
- He reported the 11:49 AM "community permissions" switch as applied while the pi-permission layer still blocked ordinary reads. That is what timed out Forge's 1:17–1:37 PM pass.
- He kept diagnosing and building tools himself after 12:31 PM.
- The 1:50 PM hazard-only switch is the right direction, but it is still being applied. As written, it also drops two real limits: the youth-guard file and network egress.

**About this audit**
- Reviewer: Fleet Reviewer (bc9b71d5). Subject: Max Architect (24f66698). Written about 2:00 PM CT. Report only.
- Requested by Derrick ("Audit max", 1:51 PM CT) and by Max (1:50 PM CT).
- Limits I kept: box only, Linear read-only, no edits outside this report. I opened no Imagine sidecar and judged no image.

**Sources**
- Max transcript pages in `/workspace/agent-tools/max-tx-1023/` (cited as `tx/<page>:<line>`).
- `/workspace/cos/plans/max-DECISIONS.md` rows 161–165.
- Linear ALI-163 and ALI-173 comments.
- Box staging copies of Forge's files in `/workspace/forge-comm/`:
  - `pi-permissions.jsonc`, 13:13: the state after the 11:49 and 1:07 switches.
  - `rf/pi-permissions.jsonc` and `rf/ralph.ps1`, 13:46–13:48: the 1:41 "readfix".
  - `rf/face_crop.py`.
  - `ali163_community_*.diff`.
- These are the files Max's executor staged and pushed. AlienPc itself was not read. Anything that exists only on AlienPc is quoted through Linear and capped at 50.

**My Oct 22 audit is not on the box.** `/workspace/cos/audits/2026-10-22-fleet-reviewer-max-day-audit.md`, its addendum, and commits e961db9 and c2fc583 are all gone. The box was restored from an older snapshot (about 7:39 AM on 10-23; see `max-DECISIONS.md:132`). I cite it from my own record only.

**What Derrick's 11:07 and 11:09 replied to**
- **11:07 "Yes do it"** (`tx/156b97aa:12`). It answers Max's 10:48 proposal: "a read-only permission for Forge to open the README files of the video plugins". The 11:06 stall report had not yet been relayed. Max read it the same way (`tx/156b97aa:13`).
- **11:09, first message.** A card answer: "Yes, let Forge copy its reference sheets into input".
- **11:09, second message, "Yes don't be so restrictive to forge wtf"** (`tx/156b97aa:24`). It came seconds after Max's narrow card on the same subject. The card offered "Yes, sheet files only" or "No, hold the redo". Max had briefed: "Add the narrowest guard copy-item rule: one literal file per call … No wildcards" (`tx/156b97aa:21`).
- **The context.** The 10:58 stop was ralph.ps1's scope check firing on a new file Forge made: "new file outside scope: C:\Users\derek\5slock\ralph-community\p7\JOB_REQUEST.json" (`tx/156b97aa:11`).

## Ranked findings, each with a fix Max can apply now

| # | Sev | Conf | Finding | Verbatim evidence | Fix now |
|---|---|---|---|---|---|
| 1 | P1 | 75 | **The 11:49 "community permissions" switch only changed one layer.** The headless guard went to denylist mode. The pi-permission layer that Forge's tools actually go through kept bash at "ask" (a deny in headless runs) and kept the chain, pipe, redirect and newline floors. All 12 denies that timed out R4G at 1:37 came from that layer. Max's 12:52 ALI-163 comment, "Hazard denylist (Forge sessions only)", overstates what was applied. | `/workspace/forge-comm/pi-permissions.jsonc:14` `"bash": "ask"`; `:347` `"*": "ask"`; `:458` `"*;*": "deny"`; `:461` `"*\n*": "deny"`; `:475` `"*\|*node*": "deny"`; `:479` `"*>/*": "deny"`. The same lines are still present after the 1:41 readfix (`rf/pi-permissions.jsonc:463-484`). `tx/4502847f:26`: "all 12 came from pi-permission-system". | In the 1:50 change, set Forge's pi profile to default-allow for bash, read and edit/write inside the work roots. Delete the `*;*`, `*&&*`, `*\n*`, `*\|*node*` and `*>/*` floors. Keep one hazard list as the source of truth and mirror it into the other layers. Test it by replaying all 12 commands denied between 1:17 and 1:37; every one must pass. Correct DECISIONS row 163 and the 12:52 comment to say "headless guard only; pi layer stayed narrow until <time>". |
| 2 | P1 | 75 | **Narrow rules kept or added after 11:09.** See the full list in the next section. Six of the ten guard against no hazard. | `tx/156b97aa:21` "Add the narrowest guard copy-item rule: one literal file per call"; `tx/156b97aa:15` "Do NOT change the copy-item rule for sheet placement (output → input); that's a gate change awaiting Derrick's card"; `tx/4502847f:27` "Apply your proposed fixes A, B, the smaller C, and E … Leave every write and hazard rule as it is". | Apply the 1:50 hazard-only list in one pass. Then remove the friction rules R1, R3, R4, R6, R8 and R9 below. Keep R7 (GPU lock) and R10 (Forge can't edit its own guard). |
| 3 | P2 | 75 | **After 12:31, Max kept doing work Forge should do.** See the timeline in section 2. Max admitted it at 1:48: "I diagnosed that timeout myself when Forge should have" (`tx/24ecfc18:7`). | `max-DECISIONS.md:164`: "four 14-byte '404: Not Found' stubs … I renamed them". `/workspace/forge-comm/rf/face_crop.py:1-4`: "(Max, 2026-10-23, ALI-163 R4G2) … Forge runs this; Forge never edits it". | Finish the 1:48 self-diagnosis setup (denies.log plus a SELF-DIAGNOSE section in PROMPT.md). Take `face_crop.py` out of `$Prot` (`rf/ralph.ps1:114`) so Forge owns it. From now on, Max only applies hazard-list GUARD_REQUESTs and edits PROMPT/TASKS "signs" (ghuntley's tuning model). |
| 4 | P2 | 75 | **The scope check stops the whole loop on a harmless new file.** KScope treats any new untracked file outside TASKS.md, STOP_RALPH and `notes\*` as a violation and writes STOP_RALPH. That caused the 10:58 stop. The 11:07 fix added a path line to PROMPT.md but left the check unchanged. Separately, the py_compile check on changed `.py` files also fires on `notes\web\*.py` stubs, which contributed to the 12:50 TIMEOUT. | `rf/ralph.ps1:8` "scope check: ralph-community may only change TASKS.md, STOP_RALPH, notes\*"; `:105` "new file outside scope (left in place, review it)"; `:7` "py_compile on changed .py … (failure -> STOP_RALPH)". | Change it to log and move the file to `notes\stray\`, and keep STOP only for changes to tracked harness files (ralph.ps1, PROMPT.md, guard). Limit the py_compile check to `C:\AI\community\scripts\`. |
| 5 | P2 | 50 | **Over-correction: the youth guard isn't on the 1:50 deny list.** The 1:50 override allows "writes anywhere under C:\AI". Its DENY list doesn't name `comm.py`, the minors/youth guard. Today `comm.py` is protected only after the fact, by ralph's `$Prot` restore (`rf/ralph.ps1:114` "except comm.py (youth guard)"). That is good, but it is not a pre-block. This is my Oct 22 youth-guard concern; it stays open. | `tx/24ecfc18:26` (1:50 brief): "writes anywhere under C:\AI … DENY only these: …" (no comm.py). | Add explicit edit/write denies for `C:/AI/community/scripts/comm.py` and its test to the hazard list. Keep the `$Prot` entry as a second check. Add one allowed and one blocked test. |
| 6 | P2 | 50 | **Over-correction: the 1:50 override drops the network limit Derrick approved.** "Any shell command" with no network rule removes the 11:49-approved read-only web, which was curl GET to six domains. Community practice keeps network egress limited even in loose setups (sources below). The override also has no rule against spending quota: nothing stops Forge running an Antigravity/agy CLI or a paid API. | `tx/24ecfc18:26`: "ALLOW by default: … any shell command, including ; && \| newlines …". ALI-163, 12:52 PM CT: "curl.exe GET only to github.com, raw.githubusercontent.com, huggingface.co, docs.comfy.org, civitai.com and reddit.com". | Keep the network rule in the hazard list: GET only, those domains plus localhost services. Deny POST, upload, `-d`, `-F`, `-T` and other hosts. Deny `agy`/Antigravity and paid API endpoints (quota or money needs a card). |
| 7 | P3 | 50 | **Over-correction: smaller hazard gaps in the 1:50 list.** It has no plaid pattern, only `.env`, rclone and tokens. KEEP isn't mentioned, though writes into approved_characters are denied. "Writes anywhere under C:\AI" includes other lanes' trees (`C:\AI\director`, `C:\AI\security`). Overwriting files is not covered by the delete rule. | `tx/24ecfc18:26` (1:50 brief). | Add `*plaid*` to the secrets denies. Add a PROMPT/TASKS line: "KEEP is Derrick's; never write keep markers or keep folders". Limit writes to `C:\AI\community`, ComfyUI `input` and `output`, and the loop's notes, which matches Claude Code's "working directory" default. Archive with `Move-Item` and never delete. |
| 8 | P2 | 75 | **Linear status is stale.** ALI-163 and ALI-173 are both **Backlog** while Forge works them. ALI-163's last comment is the 1:41 readfix *plan*. No "applied" comment yet for the readfix, the 1:42 face crop, the 1:48 self-diagnosis or the 1:50 override. No quota % is recorded (rule 8); only GPU minutes are. | Linear list_issues: ALI-163 "Backlog", last updated 1:41 PM CT; ALI-173 "Backlog". | Move ALI-163 to In Progress now, and ALI-173 when B1 starts. Post one "applied" comment covering 1:41–1:50 with the test counts. Add expected and actual quota %. |
| 9 | P3 | 50 | **Rule 7 (live check before claiming "running").** Most relaunches cite a PID plus an "iter 01 start" line about 6 s after launch. That is not the 60–120 s check rule 7 asks for. Done correctly: 10:47 "launched but not yet checked", then the 10:50 recheck (Max admitted it came late); 11:19 with an 11:25 recheck; 11:38 with a check at 11:40. The 1:19 message "Forge restarted … 1:17 PM" had no recheck reported. | ALI-163, 1:19 PM CT: "Relaunched: PID 14380 at 1:17:41 PM CT … iter 01 running". | Every relaunch comment should carry a check at +60–120 s (PID alive, a new log line, no error), or say "launched, not yet verified". |
| 10 | P3 | 75 | **Too many STOP/relaunch cycles for config changes.** Graceful stops at 10:30, 11:31, 12:05 and 1:08, plus the 10:58 scope stop and timeouts at 12:50 and 1:37. The loop was idle from 12:09 to 12:30. Only 2 redo clips rendered between 10:07 and 1:50. | Lease lines 11:31, 12:05, 1:08 (`/workspace/cos/status/2026-10-05-alienpc-shell-lease.md`); ALI-163, 12:30 PM CT batch watch: "sat idle from 12:09 to 12:30". | Make the 1:50 change the last permission edit of the day. Batch any further config changes into one boundary, and let Forge's GUARD_REQUESTs queue up. |

**Superseded:**
- My Oct 22 finding E-1 ("scope widened past 'small script bugs'") is superseded by Derrick's 11:09 AM, 12:31 PM and 1:48 PM words.
- The git-push concern is **closed**. Push is denied in every version: `pi-permissions.jsonc:361` and `:411` `"git push*": "deny"`, the headless `denySubcommands` list, and the 1:50 list.
- The youth-guard concern **stays open** as finding 5.

## 1. Restrictions kept or added after 11:09: hazard or friction?

| # | Restriction | When | Hazard or friction |
|---|---|---|---|
| R1 | Copy rule "one literal file per call … No wildcards", sheet files only (`tx/156b97aa:21`) | 11:09, widened minutes later at 11:09 (`tx/156b97aa:24` onward) | Friction. Copying output to input inside ComfyUI is not a hazard. |
| R2 | Copy widened but still limited to images from output/approved into input, never into approved_characters | 11:19 (DECISIONS 161) | The approved_characters part guards a real hazard (KEEP/approved). The rest is friction. |
| R3 | Scope check: STOP_RALPH on any new untracked file (`rf/ralph.ps1:105`) | Kept all day | Mostly friction. Changes to tracked harness files are a real hazard. |
| R4 | py_compile STOP on any changed `.py`, including notes (`rf/ralph.ps1:7`) | Kept; tripped at 12:50 | Friction for notes. Fine for `scripts\`. |
| R5 | "git add/commit replaced with '[!] Max: commit'"; no web ("community sources now means the local copies"); the bash chain deny kept, with only the AGENTS line rewritten | 11:38 (ALI-163, 11:40 PM CT, rows 3 and 10) | Friction. Superseded at 12:28–12:52 by commits and web GET. |
| R6 | pi layer: bash "ask" plus the `*;*`, `*&&*`, `*\n*`, `*\|*node*`, `*>/*` floors; `edit`/`write` C:/AI/* and HardcoreNSFW-TestRuntime denies added; file writes pinned to C:/AI/community | 12:28 (`ali163_community_pi-permissions.diff`: "Writes do NOT widen") | **Friction, and it caused the 1:37 timeout** (finding 1). |
| R7 | ComfyUI restart only via Max's `comfy_ctl.py` (Forge can't edit it); `/api/*`, `/interrupt`, `/free` and process kills blocked | 1:17 | **Real hazard.** Don't kill a running render (GPU lock). Keep it. |
| R8 | Readfix limited to A, B, the smaller C and E; "the other bash rules stay"; D (write into input) skipped | 1:41 (`tx/4502847f:27`) | Friction. |
| R9 | Face crop writes only `*_face*` into `input\community\hc` through Max's `face_crop.py`, which is in `$Prot` | 1:42–1:46 (`rf/face_crop.py:1-4`) | Friction. Cropping one's own input image is not a hazard. |
| R10 | "ralph.ps1, PROMPT and permission files stay Max's" (DECISIONS 164) | 12:51 | **Real hazard.** An agent must not edit its own guard. Matches Derrick's 1:48 split. Keep it. |

## 2. Max's own work after 12:31 ("let forge do it all" / "You direct", `tx/18721358:21`)

| Time (CT) | What Max did himself | Should have been |
|---|---|---|
| ~12:50 | Diagnosed iter 01's TIMEOUT and renamed four 404 stubs (DECISIONS 164) | Forge (self-diagnosis) |
| 1:07–1:17 | Wrote a new harness script, `comfy_ctl.py`, and rewrote the bakeoff B-lines | Partly Max's (guard/GPU lock). Forge could have drafted the script. |
| 1:14 | Searched his own notes and answered Derrick's model question before queuing R4H (`tx/4502847f:5`, RecallMemory + rg) | Minor. A quick recall is fine; the research went to Forge (R4H). |
| 1:39–1:40 | His executor read Forge's session file and diagnosed the 12 denies (`tx/4502847f:23-26`) | **Forge.** Derrick objected at 1:48. |
| 1:41 | Chose and applied guard fixes A, B, the smaller C and E | Max's role (guard), but it should have been hazard-only per 11:09 and 11:49 |
| 1:42–1:46 | Wrote `face_crop.py` and `r4g2.py`, inserted R4G2 into TASKS.md, and protected the script from Forge | Forge writes the crop step. Max only grants the write path. |
| 1:48–1:50 | Designed denies.log, SELF-DIAGNOSE and the hazard-only list | Max's role per 1:48. Correct. |

Before 12:31 (context only, not scored as a miss), Max did these himself. Each was either directly asked of Max or set up under the 9:56 relayed "Forge needs to be able to do this automously":
- He moved the stray request.
- He narrowed and committed Forge's `run_graph_job.py` patch (11:19).
- He ran the 11:13 Forge audit and the 11:53 pipeline research.
- He started a 12:25 prompt audit, which he stopped at 12:31.

## 3. Does Forge's setup match community practice?

**Ralph loop: mostly yes.**
- PROMPT/TASKS loop, one item per pass, backpressure from the whole `scripts\tests` folder (11:40, row 4), and a breaker at 3 in a row like frankbria/ralph-claude-code.
- Forge commits its own work in `C:\AI\community` (12:52).
- ghuntley's model has the operator tune Ralph with "signs" in the prompt ("Each time Ralph does something bad, Ralph gets tuned - like a guitar"; https://ghuntley.com/ralph/). That is exactly Derrick's 1:48 split.

**Self-diagnosis: not yet.**
- denies.log and SELF-DIAGNOSE were ordered at 1:48 and aren't in the box copies (`rf/prompt_now.md`, 13:50, has no SELF-DIAGNOSE).

**Hazard-only permissions: not yet.**
- As of 13:48 Forge sits behind four overlapping layers: the pi-permission system, the headless guard, protected-paths, and ralph's KScope/`$Prot`. The pi layer is still deny-by-pattern (finding 1).
- Community setups use one boundary that limits files, credentials and network, not command shapes:
  - pi.dev: "Safety comes from limiting the files, credentials, processes, and network services Pi can access and affect" (https://pi.dev/docs/latest/security).
  - pi's author: "pi runs in full YOLO mode … Since we cannot solve this trifecta … pi just gives in" (https://mariozechner.at/posts/2025-11-30-pi-coding-agent/).
  - Claude Code's sandbox writes go to "The working directory, a per-user temp directory, and directories you've added", reads cover "most of the machine", and network is limited to allowed domains (https://code.claude.com/docs/en/sandboxing).
- All of these were fetched with HTTP 200 at about 1:57 PM CT. The Codex security page (https://developers.openai.com/codex/security) also returned 200, but it renders with JavaScript, so its text is unverified and I don't cite it.

**What matching community would look like:** one default-allow profile with writes limited to the work roots, a network domain allowlist, a secrets deny, no guard self-edit, no push or force, no deletes (archive instead), and the GPU lock.

## 4. Over-correction check (1:50 override, as briefed in `tx/24ecfc18:26`)

| Hazard to keep | In the 1:50 list? | Status |
|---|---|---|
| Youth guard (comm.py) | No. Only ralph `$Prot` restores it after the fact. | **Open (finding 5)** |
| KEEP is Derrick's alone | Partly: writes into approved_characters are denied | Add a KEEP line (finding 7) |
| No deletes (archive instead) | Recursive deletes and deletes outside `C:\AI\community\tmp` are denied | OK. Overwriting is not covered (finding 7). |
| No quota or money spend | Installs and downloads need a card. agy and paid APIs are not covered. | **Gap (finding 6)** |
| No secrets (.env, plaid) | .env, rclone and tokens are covered. No plaid pattern. | Gap, P3 (finding 7) |
| git push | Denied | Closed |
| Network egress | Dropped ("any shell command") | **Gap (finding 6)** |

## 5. Rule 7 and Linear
See findings 8 and 9. Comment quality is high: approvals are quoted verbatim, every change has a backup and a diff, and the test counts are given. Status fields and quota % are what's missing.

## Efficiency: 1 / 3
- Seven loop interruptions: 4 staged stops, 1 scope stop and 2 timeouts.
- About 21 minutes idle.
- 2 redo clips in about 3¾ hours.
- Max spent four permission rounds (11:07, 11:09, 11:49→12:28, 1:41) before reaching the hazard-only list Derrick asked for at 11:09.
- Forge's own research and diagnosis output, when it was allowed to run, was good: R1, R2 and R4F.

## Needs Derrick
1. **Network under "loose restrictions".** Keep Forge's web as GET-only to GitHub, Hugging Face, ComfyUI docs, Civitai and Reddit (approved 11:49)? Or open all outbound network? The 1:50 override would open it. I recommend keeping the domain list.
2. **Write scope.** All of `C:\AI`, including other lanes' trees such as `C:\AI\director`? Or only `C:\AI\community` plus ComfyUI input/output? I recommend the latter, which is the community default.

No card is needed for the youth-guard deny or the quota deny. Both are standing hard rules (canon lock and rule 6).
