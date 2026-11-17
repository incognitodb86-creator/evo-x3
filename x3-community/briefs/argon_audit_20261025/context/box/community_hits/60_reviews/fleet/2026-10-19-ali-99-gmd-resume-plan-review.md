# ce-plan-stage review: ALI-99 GMD auto-resume Continue Download

- **Reviewer:** Fleet Reviewer (bc9b71d5) — report only; no edits to bots/skills/packs/Drive/lane/Linear/browser
- **Author under review:** Max Architect Backup (e5485fa9-f7d3-4e61-b030-f8597ce1eab9)
- **When:** 2026-10-19 ~12:41 PM CT (America/Chicago)
- **Cadence:** standing rule 8 after ce-plan (ALI-81)
- **Linear:** [ALI-99](https://linear.app/alienpc/issue/ALI-99/gmd-auto-resume-continue-download-after-box-host-upgrade-kills-chrome) — status **In Progress**, assignee/delegate null, labels `bot:max`, createdBy Derrick D, 0 comments, 0 attachments, related ALI-81
- **Plan artifact:** Linear description only (no `/workspace/cos/plans/*ALI-99*` file; `rg` for ALI-99/GMD resume under plans found none). No ce-plan receipt comment.
- **Verdict:** **GO WITH EDITS**
- **Efficiency score:** **2 / 3**

---

## Method and coverage

Read-only sources (VERIFIED this pass):

- Linear `get_issue` + `list_comments` (empty) on ALI-99; `list_issues` In Progress on project "AlienPc Local LLM Setup"
- Standing rules `/workspace/cos/brain-staging/10_packs/fleet/derricks-standing-rules.md`
- Skills: `imagine-dump-ops`, `imagine-drive-port-originals` (skim), `gemini-spark-cdp-reuse` (CDP reuse pattern), `box-chrome-resource-capa` (Fork-5 UNBAN)
- Roster `/workspace/cos/brain-staging/01_roster/ROSTER.md` + Backup carry-over
- GMD unpacked source `/workspace/gmd-dl-ext` (manifest, `content.js`, `popup.js`, `background.js`, `_locales/en/messages.json`) — **no media / no Imagine prompts / no sidecars opened**
- Path/size listing only under `/home/box/Downloads/grok_downloads` (du, find names sizes, `.crdownload` count)
- Live CDP: `ss`/`pgrep`/`curl 127.0.0.1:9227/json/{version,list}`; Extension dirs under Fork-5 vs imagine-dl
- Community: Chrome Web Store + GitHub `tomsonlee150/GrokMediaDownloader` README (Continue Download / resume progress); Chrome `chrome.downloads.resume` / auto-resumption docs (insufficient alone for GMD queue)
- Fiction: pack pointer to fiction-cond-lock v2.3.0; content-floor decision 2026-10-14 (minors-only) — mechanism N/A

Did **not**: edit Linear, touch extension/browser state, open files under `grok_downloads` conversation trees beyond path/count/size, send/post anything.

---

## What is good

1. **Community-first (rule 1):** Plan correctly rejects a custom downloader and reuses GMD’s own **Continue Download** + persisted queue. Upstream docs (v2.2.6+) advertise resume progress and “Continue Download” after interruption.
2. **Extension facts match the plan:** `STORAGE_KEY = 'grok_video_downloader'`, history Sets, `grok_interrupted_keys`, popup `btnContinueDownload` / `resumeInfo`, content `action: 'startDownload'` → `startAutoDownload()` with history skip. Popup hint: “Already downloaded files will be skipped.”
3. **Constraints are right-sized:** never delete; never clear history; same paths; nested duplicate tree **flag only**; no Generate List unless state missing; prefer event wake over timer (matches Derrick 2026-10-19 ~8:52 CT: dislike timer routines).
4. **Seat evidence supports Fork-5:** GMD `niebmpjbnghbfnjbbeajlndkjpgpamhi` installed on Fork-5 with **8.7M** Local Extension Settings (queue/history). imagine-dl profile has **no** `niebmp*` extension dir. Live 9227 shows GMD popup + `https://grok.com/imagine/saved/...` open.
5. **Rule 7 hygiene:** Plan does not claim the dump is “running”; acceptance asks for verify evidence in a Linear comment.
6. **Fiction / minors:** N/A for a resume mechanism on existing library paths. No over-refusal: adult library resume is in-scope under content floor = minors-only. R3 (never read Imagine prompts) respected by this review and by the plan’s path-only dump style.

---

## Findings

### F1 · P1 · conf 100 · Resume **trigger** is unspecified (biggest hole before build)

Plan step 2: “trigger GMD **Continue/startDownload** against the saved state” — no mechanism named (CDP? popup click? content-script message? debugger?).

Evidence (popup path requires confirm):

> `popup.js:1409` — `if (!confirm(confirmMsg)) {`  
> `popup.js:1419` — `sendMessageToContentScript(tab.id, { action: 'startDownload' });`  
> `popup.js:835-838` — button text Continue vs Start from `hasPartialDownload`

Evidence (content API exists and skips history):

> `content.js:13` — `const STORAGE_KEY = 'grok_video_downloader';`  
> `content.js:4040-4042` — `startDownload` → `startAutoDownload()`  
> `content.js:2273-2275` — filters with `!hist.has(img.id)` / `filterVideosForHdPriority`

Evidence (plan itself flags computerUse fragility):

> ALI-99 description: `computerUse often refuses gallery Start — resume path must not depend on clicking gallery thumbnails`

**Required edit:** Name one primary trigger that does **not** click gallery thumbnails. Prefer: after Fork-5 up + tab on `grok.com/imagine/saved`, send `{action:'startDownload'}` into the content script (same as popup after confirm), **or** document popup Continue + how confirm is auto-accepted. Forbid driving the signed-in gallery UI by hand. Cap new glue (see F2).

### F2 · P1 · conf 100 · Custom glue budget and event source not written; timer risk remains

Plan prefers “event-style wake (agent on handback / post-upgrade detect)” and “one thin babysit check only while a dump is marked RUNNING,” but does not name the event, the detector, or a line/file budget.

Standing rules:

> `2. Smallest sufficient fix. No over-engineering, no new daemons, scripts or routines unless asked.`  
> `8. … No ad-hoc checks or routines unless asked; prefer event triggers over timers.`

Derrick (relayed in prior FR review of ALI-81, verbatim from Alfred transcript):

> `routines are always expensive, what about webhooks? i dont like timer routines they waste usage`

**Required edit:** Explicitly: (a) no new chat timer routine; (b) wake = post-upgrade / handback / CDP 9227 down→up once; (c) babysit only while Linear/status marks dump RUNNING; (d) expected custom LOC ≤ N (suggest ≤80) listing files; (e) expected vs actual quota % on the issue (likely ~0% if shell/CDP only — still write it).

### F3 · P1 · conf 100 · No plan file / no Linear comment receipt; build already “In Progress”

`list_comments` = []. No attachment. No `/workspace/cos/plans/` file for ALI-99. Status flipped Todo→In Progress at create+28s. Description says “Research in progress → build after this issue is visible.”

Rule 4: Linear is plan of record (satisfied). Rule 3/8 still expect a reviewable ce-plan surface; F1–F2 edits should land as a Linear comment (and optional thin `plans/2026-10-19-ali-99-gmd-resume.md`) **before** implementing glue.

**Required edit:** Owner posts a short plan comment with F1–F2 answers + stop condition + quota %; keep status In Progress only while actively working (project already at **3/3** In Progress: ALI-99, ALI-80, ALI-13 — at the rule-4 cap).

### F4 · P2 · conf 100 · Disk pressure; nested tree correctly flag-only

Evidence:

> `du`: conversations tree **36G**; nested `conversations/grok_downloads/conversations` **13G**  
> `df /`: **102G/125G used (81%), 24G avail**  
> `.crdownload` count under grok_downloads: **0** (live check)

Plan correctly: “Flag only — cleanup needs a later Derrick approval card.”

**Required edit:** Add abort/pause if avail drops below a named floor (e.g. 8G) during resume; do not auto-clean nested tree or `.crdownload` without Derrick.

### F5 · P2 · conf 100 · Lane ownership: Backup named by Derrick on the issue; ROSTER still says Backup is idle

ALI-99 description:

> `Owner: Max Architect Backup (e5485fa9) — Derrick confirmed via Alfred 2026-10-19 12:35 PM CT that the Imagine/GMD dump is Backup's.`

`createdBy: Derrick D` on the issue. Roster:

> `Max Architect Backup … Idle unless Derrick asks take-over or primary hands work.`

imagine-dump-ops / browser-seats still name **Max lane owner (primary)** for dump method. Backup doing this dump is consistent with Derrick’s issue text, but ROSTER/carry-over are stale.

**Required edit (plan comment):** Cite this Linear issue as the take-over grant for ALI-99 only; do not expand Backup into other Max work. Roster refresh is separate (Derrick or primary).

### F6 · P2 · conf 100 · Live Chrome already up — do not invent a “killed / need relaunch” claim without recheck

Live-checked ~12:40 PM CT:

- CDP **9227** listening; Chrome pid **679961**; `--user-data-dir=/home/box/chrome-profile/Fork-5`
- Tabs: GMD `popup.html`, `https://grok.com/imagine/saved/e3dacbd0-…`, GMD service worker
- Profile Fork-5 mtime today; GMD storage 8.7M present (profile survived upgrade, as plan claimed)

Plan problem cites host upgrades `fcbae14` ~10:44 AM CT and `9d2ac1b` ~12:30 PM CT killing Chrome. Chrome is **currently** alive; dump resume may still be needed, but relaunch may already be done.

**Required edit:** Resume procedure starts with probe `9227/json/list`; relaunch only if down. After any “resumed” claim, rule-7 live check 60–120s (progress in logs / conversation dir mtime growth / no error) — never say “running” from launch alone.

### F7 · P2 · conf 75 · History-skip after crash is real but not perfect; plan should name interrupt reconcile

Evidence (interrupted downloads removed from history so they retry):

> `background.js:70-76` — on `interrupted`, `recordInterruptedKey(started.historyKey)`  
> `content.js:80-96` — on history load, delete keys in `grok_interrupted_keys` from history Set

Confidence 75 (not 100 on end-to-end after host kill): did not dump chrome.storage contents or simulate kill. Partial files: 0 `.crdownload` now; Chrome native resume is orthogonal and does **not** advance GMD’s queue — plan’s preference for extension Continue remains correct.

**Required edit:** On resume: never Reset/Clear history; leave any `.crdownload` alone; rely on GMD interrupt keys + history Sets; acceptance = counts grow only for missing items (no mass `(1)` duplicates).

### F8 · P3 · conf 100 · Fiction / minors bidirectional check

- Minors/CSAM hard stop: **N/A** to download-resume mechanism (no new generation, no prompt read).
- Over-refusal check: plan does **not** invent identity/fiction refusals; good. Resume of adult Imagine library is allowed under 2026-10-14 content floor (minors-only).
- R3: plan and this review stay on paths/sizes/hashes only.

No edit required.

### F9 · P3 · conf 100 · Community alternatives checked; plan is still the smallest fit

- GMD Continue (extension-native) — **chosen**; verified in repo + store/docs.
- Chrome `chrome.downloads.resume` / native auto-resumption — helps in-flight browser downloads only; does not reload GMD’s `grok_video_downloader` queue.
- systemd/supervisor Chrome babysit — can relaunch browser but still needs Continue trigger (F1); new daemon conflicts with rule 2 unless Derrick asks.
- Third-party “Retry Maniac” / DownloadResumer — redundant with GMD history + Continue.

No edit required beyond F1 wiring to GMD Continue.

---

## Efficiency score (0–3) with evidence

| Criterion | Score contribution | Evidence |
|---|---|---|
| Community reuse | Strong | GMD Continue + storage queue; GitHub README “Button shows Continue Download after interruption”; local source matches |
| Smallest fix | Partial | Right approach; trigger + LOC budget missing (F1–F2) |
| Rounds vs budget | OK | First ce-plan review; no third-round yet |
| Quota % expected vs actual | Missing | Not on issue; mark 0% expected if no paid model |
| Local tier | N/A | Ops/CDP; no Forge/Antigravity named |

**Total: 2 / 3** — drop to 1 if build adds a timer routine or gallery computerUse path; rise to 3 after F1–F2 edits land with ≤80 LOC event-driven glue and a Linear receipt.

---

## Verdict

**GO WITH EDITS** — approach is correct (extension-native Continue, no custom downloader, no deletes). Do **not** implement until F1–F3 edits are in a Linear comment (and optional plans file). Then build; Fleet Reviewer reviews again at Done (rule 8).

Not **STOP: wrong approach** — community Continue is the right primitive.  
Not **NO-GO** — holes are plan completeness, not direction.  
Not plain **GO** — trigger/event/LOC unspecified at P1.

---

## Required edits (owner: Max Architect Backup)

1. Specify resume trigger (non-gallery): content-script `startDownload` or documented popup Continue + confirm handling; CDP open `grok.com/imagine/saved` only as tab host.
2. No timer routine; event = post-upgrade/handback/CDP down→up; babysit only while RUNNING; custom LOC ≤80 with file list; quota % on issue.
3. Linear comment = ce-plan receipt (answers above + stop condition + acceptance checks). Optional thin file under `/workspace/cos/plans/`.
4. Probe 9227 before relaunch; rule-7 verify after resume.
5. Disk floor abort; nested 13G remains flag-only.
6. Never clear GMD history / never delete; interrupt-key + history skip only.

---

## Derrick-only items

1. **Delete / merge** the nested duplicate tree `…/conversations/grok_downloads/conversations/` (~13G) — plan correctly waits; needs an approval card.
2. **Disk cleanup / KEEP** if 24G free is not enough for remaining dump — irreversible deletes need yes.
3. **ROSTER update** if Backup is standing Imagine/GMD owner beyond ALI-99 (issue grants this card; roster still says Backup idle).
4. **Long-term seat:** install/migrate GMD onto `imagine-dl` vs keep Fork-5 as dump seat (skills prefer named imagine-dl; live queue is on Fork-5).
5. Any **new daemon / always-on routine** or **money/quota gate** beyond reversible Linear-visible work.

---

## Live snapshot at review (America/Chicago)

- Time: 2026-10-19 ~12:40 PM CT  
- Fork-5 @ 9227: **UP** (pid 679961)  
- GMD extension storage on Fork-5: **8.7M**  
- Open: GMD popup + `grok.com/imagine/saved/…`  
- `.crdownload` under grok_downloads: **0**  
- AlienPc project In Progress: **ALI-99, ALI-80, ALI-13** (3/3 cap)

---

## Report meta

- Written: `/workspace/cos/brain-staging/60_reviews/fleet/2026-10-19-ali-99-gmd-resume-plan-review.md`  
- Identical copy: `/workspace/cos/audits/2026-10-19-ali-99-gmd-resume-plan-review.md`  
- Author for commits: `Fleet Reviewer <fleet-reviewer@local>` — local only, never push  
