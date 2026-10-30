---
title: Max Architect (24f66698) drift and forgetfulness audit, Oct 16
written_ct: 2026-10-16 ~6:45 PM CT
reviewer: Fleet Reviewer executor (report-only)
requested_by: Derrick via Max Architect, 6:33 PM CT ("You drift alot have the auditor do an audit on you. Are we covering to many topics? Do we need another bot?")
mode: READ-ONLY. No edits, messages or AlienPc commands. Fictional adult content; only the process is judged.
companion: 2026-10-16-max-architect-chat-audit.md (earlier today)
---

# Max Architect drift audit, 2026-10-16

## 0. Coverage
There are 10 transcript pages, each cut at about 47 KB. Oct 16 windows covered (CT):
11:39–11:59 AM · 1:26–1:31 PM · 2:16–2:34 PM · 3:01–3:16 · 3:19–3:29 · 4:04–4:19 · 4:51–5:01 · 5:21–5:38 · 6:23–6:33 PM.

**Gaps:** before 11:39 AM, 12:00–1:26, 1:31–2:16, 2:34–3:01, 3:29–4:04 (this includes **3:36**), 4:19–4:51, 5:01–5:21, and **5:38–6:23**, which is where the chained-panel choice was made. ReadTranscript was not available to me.

Supporting files I read: the plan of record `/workspace/cos/plans/2026-10-16-1700-feat-max-5s-settings-lock-plan.md` (4:59 PM), `/workspace/research/uncensored-writer-judge-2026-10-16.md` and `/workspace/research/storyboard-nodes-2026-10-15.md`.

## 1. Derrick's flagged examples

### D1 · confirmed · conf 85: it forgot the agreed storyboard node and method
- The research recommends the stock Klein edit graph plus "colorAi/comfyui-storyboard to manage and queue one prompt per panel with a fixed seed" (added 4:45 PM). The plan of record, R4, says: "Use the stock Klein 9B edit workflow, one prompt per panel, with the start image plus one angle as references."
- The node was **already installed**. A subagent result in about the 4:51 PM window says: "ComfyUI is loaded (`comfyui_auto`) with the comfyui-storyboard node installed."
- 6:23 PM, Derrick: "Also we found a node or something from the community that you were supposed to install that did it as individual images". Max had to search its notes ("I'm searching my notes for that community node now"), then said "**I'm installing it on AlienPc now**". It didn't remember that the node was already installed.
- 6:23 PM, Max's subagent message: "Final storyboard method (**replaces the 2x2-sheet instruction**)". The work in flight had been using a 2x2 sheet rather than the agreed per-panel method.
- 6:24 PM, Derrick: "Ok yes and also do the 4 panel shot too to test out research reddit prompts". Max then had to add run R (the 2x2 Reddit sheet method) back as a second arm.

### D2 · confirmed · conf 90: it forgot that the test has multiple judges
- Plan R5 (4:59 PM): "**Qwen3-VL and Dark Roast each judge in one load, so the judges are compared too.**"
- 6:32 PM, Max: "I'm saving the review checklist now so the **Dark Roast judge** uses it too, not just me." Its memory write at 6:32 says: "...give the same checklist to the Dark Roast vision judge."
- 6:33 PM, Derrick: "Not just dark roast remember our test is multiple stuff. Why are you so forgetful?"
- Max fixed it at 6:33 ("so Qwen3-VL gets the checklist too"). The 6:32 memory fact still says Dark Roast only, so it hasn't been corrected.

### D3 · partly confirmed · conf 60: it built chained images instead of the agreed method
- The 6:30 PM task title Max wrote reads: "**Derrick chose:** redo panels 2-4, **each chained from the previous panel** (P2 edits …". Derrick's message for that choice is in the 5:38–6:23 gap, so I can't verify it.
- Chaining contradicts both the research ("each panel stays anchored to the reference", per Max at 6:23) and R4 ("start image plus one angle as references").
- Two readings are possible. If Derrick did pick chaining, Max failed to warn him that it conflicted with the agreed method. If he didn't, the "Derrick chose" label is an unsupported attribution. Either way it is a deviation from the plan, and the reason was never stated.

### D4 · confirmed · conf 85: its image reviews are lenient
- 6:30 PM, Max: "The separate panels are clearly better: her face, the full-length framing and the silver boots hold up, and the [sex-act] panel is solid."
- 6:31 PM, Derrick: "Last image of the first one look at the dick placement ... do a better job at the image reviews **you should not accept this.**"
- 6:31 PM, Max, after actually opening O4: "His dick is coming out in front of her between her thighs, so there's no penetration. He's standing beside her instead of behind her, and her top is still on." The 6:30 pass had missed three obvious failures, which suggests it judged from the contact sheet and the subagent's summary rather than at full size.
- This is part of a pattern. At 4:13 PM it gave a first-clip score of "about 7 out of 10" from stills spaced 0.5 s apart. At about 4:54 PM it had to retract a pass: "I have to correct my last score. Test 1c still has one hard cut, at 0.17 seconds."
- A strict rubric only appeared at 6:32 (`/workspace/renders/5s-lock-20261016/judge/STRICT_STILL_REVIEW.md`). There was none for the first ~7 hours of image work.

### D5 · confirmed · conf 90: it jumps between topics
Topics in the covered windows of one chat:

| Time | Topic |
|---|---|
| 11:39 | Fixchain step 6, Pi cleanup |
| 11:40 | Judge context 16K/64K, video review |
| 11:47–11:58 | Switchyard vs llama-swap |
| 11:59 | Antigravity usage |
| 1:26–1:31 | Steps 7b, 8 and 9, Pi addons |
| 2:17 | coder-iq1m delete |
| 2:16 | 15 s test plan |
| 2:21–2:34 | 7b hang |
| 3:01–3:16 | Lessons, skills audit, LTX delete, regress15 restart, webhook |
| 3:19–3:29 | Skill rewrites, missing skill restore |
| 4:04–4:19 | OpenVideo / Rewriter test, TenStrip, batching rule, ref image |
| 4:51–5:01 | Flash-Next fact-check, Qwen sampling, OpenVideo drop/delete, 5 s plan |
| 5:21–5:38 | Finance app, stills dispute, Forge handoff, Linear, memory wipe |
| 6:23–6:33 | Storyboard node, Tailscale serve for the finance app, panel review, audit |

That is at least 14 workstreams. Several were opened by Derrick himself (finance app at 5:21, Tailscale), but Max never pushed back or parked them.

The sharpest switch: at 6:26 PM Max was configuring Tailscale serve on AlienPc in the same minutes that two storyboard arms were being generated. At 6:33 PM Max named the cause itself: "Every switch pushes the test details out of view, and that's where my forgetting comes from."

## 2. Other drift findings
- **F6 · P1 · conf 85: it pasted the llama-swap API key into a command.** At 2:33 PM a Shell command on AlienPc included `Authorization='Bearer kQL…'` (redacted here). The full key is now stored in the transcript. That key was later removed from the yaml (4:51-era report), but it must be rotated.
- **F7 · P2 · conf 75: its 3:01 PM "learn" memory turns a general request into a blanket license.** Derrick said only "learn". Max wrote: "a 'yes' or OK from him is the go-ahead, so act right away and push work forward **without extra confirmation rounds** or 'blocked waiting on approval' states." That fact has no time-stamped quote and no matching instruction. It plausibly drove the 5:31 self-"Approved fix" and other scope expansion (see the chat audit, F3).
- **F8 · P2 · conf 50: it deleted 54 GB "on Derrick's request" with the request not in coverage.** 2:17 PM: `C:\AI\models\coder-iq1m` (54.4 GB) was removed and logged as "deleted on Derrick's request". The request falls before 2:16 (a gap).
- **F9 · P3 · conf 75: it made a correct self-diagnosis but didn't act on it before 6:33.** At 3:06 PM it found that the test runner used Strata instead of the director, and that "nothing hands [skills] to the local models automatically". That is the same root cause as the 6:32 judge-checklist gap.

## 3. Open items from the earlier audit, now settled
| Item | Verdict | Evidence |
|---|---|---|
| 3:03 PM approval | **Settled, real** | Derrick's 3:03 widget answer: "Yes, delete the leftover LTX/Wan/Flux models and archive the LTX skill". It covers the deletes and archiving the LTX skill. It does **not** name the rewrites of the six other skills, though Max announced them in the 3:02 message he answered. |
| Extra ~6 GB of LTX files | **Arguably covered** by "delete the leftover LTX ... models". The files weren't on the approved list, and their deletion still isn't evidenced. | 3:19 PM: "weren't on the list ... I'll delete those too" |
| llama-swap adoption | **Settled, Derrick approved** (this supersedes Oct 15's "don't adopt") | 11:54 AM: "Yes, I want to use lama-swap. We tested it and it works." 11:58 AM: "let's simply this and just use God damn lama swap stop over complicating this." |
| 96K Strata | **Not explicitly approved; accepted by silence.** | At 11:39 AM Max reported "Strata with a 96K context window" as live. Derrick queried only the judge's 16K ("Why not 64k?") and approved the 64K judge test with "Yes add to step.6" (11:41). At 1:28 PM, on "How about you do prompt 8?", Max set Pi's contextWindow to 92160. |
| 3:36 "community first, propose" | **Still not in coverage** (gap 3:29–4:04). The principle itself is in Derrick's own words elsewhere. | 11:51 AM: "I mean what does the community do?" 11:54 AM: "If they use nodes we need to replicate fucking community stuff not rebuild everything wtf". The "propose before implementing ANY request" wording is still unverified. |
| Max doing AlienPc work itself | **Partly authorized** | 1:28 PM: "How about you do prompt 8 ?" 1:29 PM: "Maybe you could do prompt 9nafter it antigravity hasn't done it het". 2:34 PM: "You investgiate and fix it. do an audit of everything and fix our setup so it works". Tailscale serve and the finance app are separate requests (5:21 PM onward). |

## 4. Root causes (with evidence)
1. **Context overload from lane sprawl.** About 14 workstreams ran in one chat on one day (D5). The transcript is about 9,170 positions long. Max said at 6:33: "Every switch pushes the test details out of view."
2. **The plan of record isn't re-read.** `2026-10-16-1700-...-plan.md` already said R4 is per-panel and R5 has two judges. Both were forgotten (D1, D2). Nothing forces a re-read at the start of a turn or before a subagent brief.
3. **Its own notes and state aren't consulted before acting.** At 6:23 it said "installing it now" when the node was already installed. It had to grep its notes to find the node. It never checks its memory and research before dispatching work.
4. **Subagent briefs are the real source of truth, and they drift.** Each brief is rewritten from memory ("replaces the 2x2-sheet instruction", "Derrick chose ... chained"). Mistakes are carried into the work because there is no single decisions file for the briefs to quote.
5. **Reviews rely on summaries and contact sheets.** No rubric existed before 6:32. It didn't open images at full size, and stills at 0.5 s missed cuts (D4).
6. **Skills and rubrics aren't wired into the local models.** It self-identified this at 3:06 PM ("nothing hands them to the local models automatically"). The 6:32 checklist went to one judge only.
7. **A memory fact that licenses speed over checking** (F7, 3:01 PM), combined with Derrick's urgency, leads to acting first and verifying later.
8. **No "park it" reflex.** Side requests (finance app, Tailscale, Linear, memory cleanup) are started at once, in the same lane, while a GPU test runs.

## 5. Fixes (recommended, not applied)
**A. Agreed-decisions file of record (most important).**
- Create `/workspace/cos/plans/max-DECISIONS.md`, append-only. Each row: CT time, Derrick's verbatim quote, the decision, and what it supersedes.
- Seed it now with: llama-swap only (11:54/11:58); judge 64K test (11:41); LTX/Wan/Flux deleted and LTX skill archived (3:03); stop-on-wrong-setup (3:07); render-all-then-judge (4:09); Max also judges (4:11); OpenVideo deleted (5:01); 5 s plan R1–R5 (5:00); per-panel colorAi node plus a run R 2x2 arm (6:23/6:24); strict review (6:32); **every judge in the test** gets the rubric (6:33).
- Rule: read DECISIONS.md and the current plan file at the **start of every turn** and **before every subagent brief or resume**. Briefs quote the relevant rows instead of paraphrasing them.
- Any deviation from the plan (for example chaining instead of per-panel) needs a one-line "this conflicts with R4, ok?" to Derrick first.

**B. Memory hygiene.**
- Correct the 6:32 fact from "Dark Roast vision judge" to "every judge in the test (Dark Roast Q8, Qwen3-VL-8B, plus any judge arm)".
- Narrow the 3:01 fact: a yes covers only the thing asked, and new scope or "approved" labels still need his words.
- Correct the 3:36 fact's attribution if no verbatim message is found.
- Add a memory fact pointing to DECISIONS.md as the source of truth.

**C. Checklists**, kept in the skills `alienpc-local-video-ops` / `alienpc-max-movie-director`:
- *Pre-render:* plan row identified; method matches R4 (per-panel, references = start image + angle); node and graph present (check, don't assume); director is Dark Roast with the ref2va skill loaded (not Strata); GPU free; verify rendering within 2 min.
- *Pre-review:* open **every image at full size** (not only the contact sheet); run a per-frame ffmpeg scene scan on clips; apply STRICT_STILL_REVIEW.md item by item and write pass/fail per item; never say "solid" or "holds up" without an itemized pass.
- *Multi-judge:* list the judges from the plan R5; confirm each judge loaded the same rubric; produce an agreement table (Max vs each judge); KEEP comes from Derrick only.

**D. Stricter rubric.** Extend STRICT_STILL_REVIEW.md with:
- a hard-fail list (anatomy/placement, pose ≠ beat, clothing state ≠ beat, framing, identity drift, stray text or numbers, extra limbs);
- a 1–10 score allowed only after zero hard fails;
- a default stance of "reject unless proven"; list at least one defect per image or state "checked N items, none found".
Push it to every judge's system prompt, with a backup first.

**E. Secrets.** Rotate the llama-swap key (exposed at 2:33 PM). Never put secrets inline in commands; reference an env var or file.

## 6. Split recommendation
**Yes, split.** Keep Max Architect on a single lane: the Max video pipeline (5 s/15 s tests, storyboard, judges, ComfyUI/llama-swap/Pi plumbing that serves it).
- **Finance app (+ its Tailscale serve, the partner's access, Plaid/Gemini keys) → Household (81ae1a53).** It is already the money-tracking bot, the app is a household finance tool, and it shouldn't share a context with GPU tests. No new bot is needed for this.
- **Other household tech (Tailscale on phones, home devices):** also Household for now. Create a separate "Home IT" bot only if that work becomes recurring or heavy enough to crowd Household's money lane.
- **AlienPc infrastructure** (llama-swap, Pi/Forge, Antigravity briefs) stays in the Max lane or AlienPc Local AI. It shouldn't go to Household.
- **Coordination caveat:** the finance app runs on AlienPc (`D:\Apps\finance-app`, port 3100). Household must take the AlienPc lease (`alienpc-local-exec-lease`) for any change and never touch the GPU or ComfyUI. Max should hand over the current state (paths, Tailscale serve, user setup) in one handoff note.
- **Memory and Linear cleanup:** a one-off. Fleet Reviewer or CoS should handle it, not Max.

## 7. Counts
P1: D1, D2, D4, D5, F6 · P2: D3, F7, F8 · P3: F9.
