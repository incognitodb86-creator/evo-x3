# ce-plan-stage review: ALI-101 GMD allmedia scan paging patch

- **Reviewer:** Fleet Reviewer (bc9b71d5). Report only: nothing edited, loaded, sent or posted.
- **Owner under review:** Max Architect Backup (e5485fa9). Also reviewed: AlienPc Local AI (4f7cac4f) partial edits.
- **When:** 2026-10-19, 3:00–3:06 PM CT (America/Chicago)
- **Cadence:** standing rule 8, after ce-plan
- **Linear:** ALI-101, status **Todo**, created 2:59:47 PM CT (`createdBy: Derrick D`, the shared account). No project, no labels. Related to ALI-99. One comment, 3:00:18 PM CT.
- **Inputs read:** plan `/workspace/cos/plans/2026-10-19-gmd-scan-paging-patch.md`; probe `/workspace/cos/audits/2026-10-19-gmd-page31-probe.json`; partial diff `/workspace/cos/audits/2026-10-19-gmd-paging-partial-patch.diff`; source `/workspace/gmd-dl-ext` (git); store build `Fork-5/Default/Extensions/niebmpj…/2.5.6_0`; backup `/workspace/gmd-dl-ext.bak-20261019-paging`; Chrome Web Store page; upstream GitHub issues page.
- **Not read:** no Imagine media, prompts or sidecars. Download trees were checked by counts and sizes only.
- **Verdict:** **GO WITH EDITS.** The direction is right: a small local patch, since no upstream fix exists. But nothing may be built or loaded until the P0 edits are made, and **the edits that are still happening must stop now** (F2).
- **Efficiency score:** **1 / 3**

---

## (a) Is the paging bug real?

**The code defect is real (P1 · conf 100).** One failed page ends the whole scan, and the partial list then replaces the stored one. The defect is identical in the 2.5.4 source and in the **2.5.6 store build that Fork-5 actually runs**.

2.5.6 store build, `src/grok-assets.js:162–189`:

> `const maxRetries = 3;` … `await sleep(Math.min(1000 * Math.pow(2, attempt - 1), 8000));` … `if (!page) break;`

So one page gets 4 attempts about 7 s apart, and then the scan stops. `listGeneratedAssets` throws on any non-OK status (`throw Object.assign(new Error('HTTP ' + res.status)…`). The throttle defaults are `throttleMs = 600, maxThrottleMs = 2500` (2.5.6 `grok-assets.js:130–131`), and the user can't change them. In 2.5.6 `content.js`, the allmedia path still calls `await saveState(state);` after a partial scan. The only partial warning is `'No assets collected (allmedia)'`, which fires only when zero assets come back.

**The probe matches the "1,799 at page 31" story, but it doesn't prove the cause (P2 · conf 75).**

- Every one of pages 1–36 has `"status": 200`, `"n": 60` and `"next": true`.
- Page 30's last item is `"last": "2026-10-12T12:08:25.464Z"`. 30 pages × 60 = 1,800, which fits "1,799 items (Oct 12–19)".
- Page 31 loads fine at 900 ms (`"p": 31, "status": 200`), so the cursor is followed and no page is bad.

What the probe does **not** show:

- It never reproduces a failure at 600 ms, so "rate limit" is an inference. The plan's pace claim is reasonable, but nothing shows an HTTP 429.
- **"9 runs today end `pages: 30, errors: 1`" has no evidence on disk.** I searched `/workspace/cos` status, audits, plans and logs and found no GMD log export. The claim exists only in the plan. Confidence for this sub-claim is 50.
- The plan says the Oct 15 scans found about 20k images and 9k videos at the same 600 ms pace. So today's limit depends on context. A likely factor is that the scan shares the session with the running ALI-99 downloads and with 9 back-to-back reruns (conf 50).

**Side effect the plan doesn't flag (P1 · conf 75).** Each partial Generate List rewrote `grok_video_downloader` with the 1,799-item list. So the ALI-99 "Continue" queue probably covers only Oct 12–19 now, not the whole library. That fits the dump stalling at 14:08 (see (d)).

## (b) Community first

- **Upstream fix:** none found. The GitHub issues page shows "No results matched your search" (0 issues). The Chrome Web Store page says **Version 2.5.6, Updated September 14, 2026**, which is what Fork-5 has, so no newer build exists. The store text mentions "Smart 429 Rate-Limit Handling" and "partial scan auto-recovery" (v2.3.6), but the 2.5.6 code above still breaks after 4 attempts. **Confirmed.**
- **Fork:** I found none, and neither did the plan.
- **Smallest fix:** the plan's three changes are the right size: a slower base throttle, a long per-page backoff on the same token, and not overwriting a larger stored list. **Missing zero-code step 0 (P2 · conf 50):** run Generate List once with downloads stopped and no reruns for about 15 minutes before it. Oct 15 succeeded at the same pace. If that run clears page 31, no patch is needed now.
- **Custom LOC:**

| Version | Size |
|---|---|
| Plan | "Estimated diff ≤40 LOC" |
| Local AI working tree, live at 3:04 PM CT | `content.js` **+40/−3**, `src/grok-assets.js` **+101/−18**, plus a new `test/paging-retry.test.js` of **76 lines**. That is **141 production lines added** and 217 including the test, about 3.5× the plan's budget. |

  Local AI's extra scope beyond the plan: Retry-After parsing, a 5-step backoff up to 180 s with a 300 s cap, and a union merge by asset id.
- **Patching a third-party paid extension in place (P2 · conf 75):** this is an unpacked fork of a PRO, license-checked extension (`host_permissions` include `https://api.lemonsqueezy.com/*`). An unpacked build **gets no store auto-updates**, so every upstream release means a manual rebase, and the license check on an unpacked build is untested. The plan says "plus an upstream bug report". **Filing that report is posting externally, so it is Derrick-only** and the plan doesn't say so.

## (c) Live check: has anything been edited already?

**Yes, and edits continued after the claimed 2:59 PM pause (P0 · conf 100).**

- `/workspace/gmd-dl-ext` was turned into a git repo at **2:57:39 PM CT**. Its single commit is `90bc7bd baseline GMD 2.5.4 (pre paging fix)`.
- `git status`: `M content.js`, `M src/grok-assets.js`, `?? test/`.
- File mtimes (CT):

| Time | File |
|---|---|
| 2:58:53 | `src/grok-assets.js` |
| 2:59:08 | `content.js` |
| 2:59:26 | `test/paging-retry.test.js` |
| 2:59:39 | partial diff saved to audits (11,689 B) |
| **3:03:50** | **`src/grok-assets.js`, `content.js` (again)** |
| **3:04:13** | **`test/paging-retry.test.js` (again, now 76 lines)** |

- Between my 3:00 and 3:04 samples, `git diff --numstat` moved from `43/3 · 80/18` to `40/3 · 101/18`. The audits diff file no longer matches the working tree (`HUNKS_DIFFER`).
- Backup's comment says: "AlienPc Local AI started editing `/workspace/gmd-dl-ext` before the plan was posted, and paused at 2:59 PM CT when I asked." **That isn't true on disk.** Someone edited at 3:03–3:04 PM CT, after the plan and Linear issue were posted and while this review was running. I couldn't identify the process from the box.
- **Nothing is loaded yet.** Fork-5 Preferences show `location: 1`, `path: 'niebmpjbnghbfnjbbeajlndkjpgpamhi/2.5.6_0'`, `from_webstore: True`. Chrome's command line has no `--load-extension`. Fork-5 Chrome was **relaunched at 2:56:17 PM CT**, with its working directory in `/workspace/gmd-dl-ext`.
- **Backup is a pristine 2.5.4 copy, not 2.5.6.** `diff -rq` between the backup and the working tree shows only `content.js`, `src/grok-assets.js` and `test/`. The backup matches the baseline (manifest `"version": "2.5.4"`, mtimes 2026-10-17).

**The base is the wrong version (P0 · conf 100).** The plan says "Fork-5 runs the store build v2.5.6. The patch needs an unpacked load of `/workspace/gmd-dl-ext`". But that tree's manifest says `"version": "2.5.4"`, and `diff -rq` against the 2.5.6 store directory lists **14 differing files**: `content.js`, `popup.js`, `src/grok-assets.js`, `src/utils.js`, `src/content-utils.js`, `offscreen.js`, `manifest.json`, locales and more. Loading it would **downgrade Fork-5 from 2.5.6 to 2.5.4** under the same ID. That means 2.5.4 code reading storage written by 2.5.6, and losing the 2.5.5/2.5.6 fixes (Collections API and others). The line numbers in the plan (`content.js:1549`, `:1695`) are 2.5.4 lines; in 2.5.6 the allmedia call sits near line 2012. **The patch must be rebuilt on a copy of `2.5.6_0` (minus `_metadata`).**

**Lane (P1 · conf 100).** The roster defines AlienPc Local AI as:

> `Local LLM director & coding agent; **not the AlienPc executor**`

The GMD dump is Imagine/Max-lane work on the box, and ALI-99 names Backup as owner ("Derrick confirmed via Alfred 2026-10-19 12:35 PM CT that the Imagine/GMD dump is Backup's"). Local AI editing the extension before any visible plan breaks rules 4, 5 and 6:

> `6. Reversible work inside the stated goal proceeds without asking, as long as it is in a Linear issue/plan Derrick can see before it starts.`

The edits are reversible: they're uncommitted in git and a backup exists. So the harm is process, not data. Choosing the builder is correctly left to Derrick, and both the plan and the comment say so.

## (d) Risk to the running dump

- **The dump is not growing right now (P1 · conf 100), so ALI-99's lease is stale.** Two samples about 2 minutes apart:

| Sample | Time (CT) | Files | Bytes | `.crdownload` |
|---|---|---|---|---|
| T1 | 3:02:01 | 85,573 | 40,128,873,399 | 0 |
| T2 | 3:04:19 | 85,573 | 40,128,873,399 | 0 |

  The newest file is from **2:08 PM CT**. The lease still says `"state": "RUNNING"` with `last_verify: 'no_growth_90s'`. The resume log's last entries are `RESUME chrome=False age=2959s` / `startDownload {"ok": false}` / `VERIFY no growth` (1:58–2:00 PM CT). "RUNNING" is false under rule 7. This makes a reload less risky than if downloads were in flight, but the plan and ALI-99 should say "stalled", not "running".
- **Storage loss on reload (P0 · conf 75).** The plan says "Rollback: re-enable the store build", and the comment says "**disable** the store copy, don't remove it, because removing it wipes its storage". Chrome can't hold two installs with the same ID. A Stack Overflow answer on this exact case says an unpacked build with the same ID "will replace the old extension from the web store because the id will be the same. Its data will be kept." The Chrome docs (storage.local) say data is "cleared when the extension is removed".
  - So after an unpacked load, **there is no store copy left to re-enable**.
  - Rolling back by uninstalling and reinstalling from the store **wipes `grok_video_downloader` and all download history**, which would then cause mass re-downloads and `(1)` duplicates.
  - The safe rollback is to load an **unpacked copy of the pristine 2.5.6** (same key, same ID), which keeps the data.
  - Back up `Local Extension Settings/niebmpj…` (13 MB now) **with Chrome stopped** so the LevelDB copy is consistent. The plan has the backup but doesn't say Chrome must be stopped.
  - I didn't test this on the box, so confidence is 75.
- **Duplicates (P2 · conf 75).** History lives in separate keys from the queue, so a fresh full list should skip what's already downloaded. The plan's acceptance even says "the new `* (N).*` duplicate count stays near 0". But files downloaded through other sources or namespaces may be missing from the allmedia history, and Chrome would save those again as `(1)`. Count today: **8,145 `(1)` files** in the tree, almost all from Oct 17, and **0 new since 12:45 PM CT**. The plan needs a pre-Start check: after the full Generate List, compare the popup's "need" count with the expected missing count, and **don't press Start if need is close to the library total**.
- **Rollback:** planned, but wrong as written (above).
- **Test plan before the live run (P1 · conf 100):** the plan has only live acceptance ("One Generate List … completes with `errors: 0`"). There's no pre-live gate. Local AI's mocked test (`node test/paging-retry.test.js`, no network) exists, but the plan doesn't adopt it. The plan needs this order: unit test passes → step-0 zero-code scan → load the patched 2.5.6 → one Generate List with **Start held** → review counts → Start.
- **Disk:** `df` shows 26G free (80%), and the plan floor is 8G. The nested 13G tree is untouched and flagged only. OK.

## (e) Quota and approvals

- **Quota** is stated as "0% paid model (code edit + CDP)". That's plausible for either builder. OK.
- **Derrick's quote is unverified (P1 · conf 100 that it's unverified).** The plan and the issue cite: "Yes, plan the GMD scan patch on Linear first, then build after review." Searching `/workspace` and `/home/box/agent-data` for that phrase finds it **only** in the plan file. The Linear `createdBy: Derrick D` is the shared bot account, not Derrick's own words. Treat it as RELAYED and unverified. Even taken at face value, it authorizes **planning, then building after review**. It does not cover loading the extension, which the plan itself lists as Derrick-only, and that's correct.
- **Derrick-only list is mostly right:** loading the unpacked extension, disk cleanup, the nested tree. **Missing from it:** filing the upstream bug report (external post), choosing the builder (named in the comment but not in the plan's list), and keeping an unpacked fork of a paid extension long-term instead of waiting for upstream.
- **WIP:** ALI-101 is left in Todo because the project is at its 3/3 cap. That's correct under rule 4. But the issue has no project or labels, so it's invisible to the per-lane WIP count. It should get project "AlienPc Local LLM Setup" (or the Imagine lane) and `bot:max`.

---

## Findings summary

| ID | Sev | Conf | Finding |
|---|---|---|---|
| F1 | P0 | 100 | Patch base is the **2.5.4** source, but Fork-5 runs **2.5.6** (14 files differ). An unpacked load would downgrade the extension. |
| F2 | P0 | 100 | Edits continued at 3:03–3:04 PM CT, after the claimed 2:59 pause and after the plan was posted. Out of lane (Local AI) or unattributed; unreviewed. |
| F3 | P0 | 75 | Rollback "re-enable the store build" won't work: a same-ID unpacked load replaces the store copy, and uninstall/reinstall wipes the queue and history. |
| F4 | P1 | 100 | Scan defect confirmed in 2.5.6 (`if (!page) break;`, 4 tries about 7 s, partial `saveState`). |
| F5 | P1 | 75 | Partial lists have already overwritten the ALI-99 queue (likely 1,799 items only). Not flagged in the plan. |
| F6 | P1 | 100 | No test gate before the live run. Acceptance is live-only. |
| F7 | P1 | 100 | AlienPc Local AI is out of lane for box GMD work; rule 6 requires the plan to be visible before work starts. |
| F8 | P1 | 100 | Derrick's 2:59 PM quote is unverifiable on disk (relayed). It doesn't cover the load. |
| F9 | P1 | 100 | Dump stalled since 2:08 PM CT while the ALI-99 lease says RUNNING (rule 7). |
| F10 | P2 | 75 | "Rate limit at 600 ms" and "9 runs end at page 30" are inferred, not evidenced. The probe never reproduces the failure. |
| F11 | P2 | 50 | Missing zero-code step 0: scan once with downloads stopped (Oct 15 worked at the same pace). |
| F12 | P2 | 75 | Unpacked fork of a paid, license-checked extension: no auto-updates, manual rebase each release, untested license behavior. Upstream bug report is an external post, so Derrick-only. |
| F13 | P2 | 100 | Size drift: plan ≤40 LOC vs. working tree +141 production lines (+217 with test). Two builders duplicating work. |
| F14 | P3 | 100 | ALI-101 has no project or labels, so it isn't counted against the lane's WIP. |
| — | — | 100 | **Fiction / minors: N/A** (scan paging). No over-refusal. R3 respected: paths, counts and sizes only. |

## Efficiency score: 1 / 3

| Criterion | Evidence |
|---|---|
| Community reuse | **Good.** Upstream issues (0) and the store version (2.5.6, Sep 14) checked. Local patch justified. |
| Smallest fix | **Weak.** Plan says ≤40 LOC; actual tree is +141 production lines. No zero-code step 0. |
| Rounds vs budget | **Weak.** Work started before the plan, two builders in parallel, edits continued after the pause. |
| Quota % | Stated as 0%. OK. |
| Local tier | Local AI used for code. Fine for quota, but out of lane. |

---

## Required edits (before any build or load)

1. **Stop all edits to `/workspace/gmd-dl-ext` now.** Backup confirms in Linear who edited at 3:03–3:04 PM CT. Leave the working tree as is (reversible) until Derrick picks the builder.
2. **Rebase onto 2.5.6.** Copy `Fork-5/…/niebmpj…/2.5.6_0` to a new working directory (drop `_metadata`) and git-init it as `baseline GMD 2.5.6`. Re-cite line numbers against 2.5.6. The 2.5.4 tree is not to be loaded.
3. **Fix the rollback.** The rollback is to load the pristine unpacked 2.5.6 copy (same key and ID). Never uninstall, never "remove", and never reinstall from the store. Back up `Local Extension Settings/niebmpj…` **with Fork-5 Chrome stopped**, and confirm the ID on `chrome://extensions` before the first Generate List.
4. **Test gate:**
   1. Run `node test/paging-retry.test.js` (mocked) and confirm it passes.
   2. Step 0: one store-build Generate List with downloads stopped (zero code). If it clears page 31, stop here and don't patch.
   3. Otherwise, after Derrick OKs the load: one Generate List with **Start held**, then post the image/video totals, `errors`, and the need count.
   4. Press Start only if the need count is plausible: well below the total, and matching the missing estimate.
5. **Scope:** pick one patch spec and one LOC cap. Suggested: the plan's three changes, ≤60 production LOC, Retry-After optional, keep-old over union-merge unless Derrick wants merge. Record expected and actual LOC on the issue.
6. **Correct the record.** Mark the ALI-99 lease as stalled, not RUNNING (no growth since 2:08 PM CT). Note that partial scans replaced the queue. Add a project and `bot:max` to ALI-101. Mark the 2:59 PM quote as relayed unless Derrick confirms it.
7. **Derrick-only list:** add the upstream bug report (external post), the builder choice, and keeping a long-term unpacked fork.

## Escalations (Derrick-only)

1. **Out-of-lane / post-pause edits:** AlienPc Local AI, or an unattributed actor, kept editing GMD source at 3:03–3:04 PM CT after the "paused at 2:59" claim.
2. **Builder choice:** Backup or AlienPc Local AI, plus which LOC budget.
3. **Loading the unpacked extension** into Fork-5 (store build to unpacked 2.5.6+patch), and accepting no auto-updates afterward.
4. **Upstream bug report** to tomsonlee150/GrokMediaDownloader or [redacted-email] (external post).
5. **Confirm or deny** the relayed 2:59 PM CT approval quote.
6. Still open from ALI-99: the routine `gmd-fork-5-auto-resume` (delete or keep paused), the nested 13G tree, disk.

---

## Live snapshot (CT)

- Fork-5 @ 9227: up. Relaunched 2:56:17 PM. Store build 2.5.6 loaded (`location: 1`). Open tabs: `grok.com/imagine/saved` and the GMD service worker.
- GMD extension storage: 13 MB.
- Library: 85,573 files, 40.13 GB, no growth from 3:02 to 3:04 PM, newest file 2:08 PM. `.crdownload`: 0. `(1)` files since 12:45 PM: 0.
- Nested tree: 13G, untouched.
- Disk: 100G/125G used, 26G free.

## Report meta

- `/workspace/cos/brain-staging/60_reviews/fleet/2026-10-19-ali-101-gmd-scan-paging-plan-review.md`
- Identical copy: `/workspace/cos/audits/2026-10-19-ali-101-gmd-scan-paging-plan-review.md`
- Commits by `Fleet Reviewer <fleet-reviewer@local>`, local only, never pushed.
