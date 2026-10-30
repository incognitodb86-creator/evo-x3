# Fleet Reviewer: Max Architect morning audit, Mon 2026-10-19 (CT)

Reviewer: Fleet Reviewer (report only). Subject: Max Architect `24f66698-f52b-4dec-8325-db7c59b71f03`, Max-lane work about 8:36–9:16 AM CT.
Trigger (relayed by Max, not verified): Derrick 9:14 AM CT "make sure linear is updated and when your done get everythign audited".
Written 2026-10-19 about 9:50 AM CT. Nothing was edited, sent, posted or stamped. No Imagine prompts or sidecars were opened. This is not a KEEP or PASS on any Max content.

---

## ESCALATIONS (top of report)

**E1. Approvals could not be checked against Derrick's own words (process gap; it affects every row below).**
The `ReadTranscript` tool is not in this session. `GetDynamicTools` has no `cursor` namespace, and a pattern search for "transcript" finds nothing. The transcript store on the box (`/home/box/agent-data/agent-transcripts/`) has nothing newer than 2026-10-18. So **none of the 9 Max approvals is verified**. The approvals table gives the wording Max recorded and the question Max recorded, both from Max's own files. Under the rules those count as agent claims only. To close this, re-run step 1 with ReadTranscript available.

**E2. A gate change went beyond the approved question (P1, confidence 75).**
The question Max recorded for 9:12 was: "Retire the judges, face/hand gates, writer model and 98-check preflight from the default path (archived, not deleted)?" (`max-DECISIONS.md` row 83). The edits also retired gates that the question does not name:
- The LOCKED 2026-10-06 pre-Derrick auto-CAPA rule in `alienpc-local-video-ops/SKILL.md` changed from "if no candidate clears every check (Max full-size review AND every calibrated judge) → CAPA + HOLD" to "if no candidate clears review (Derrick's eye review; the Max full-size review + calibrated-judge gate is retired 2026-10-19) → CAPA + HOLD from Derrick's eyes". That **retires Max's own full-size review before Derrick sees anything**. The question did not name that review, and it is the pre-Derrick surface gate the T4 pack (`10_packs/max/quality-stamp-before-derricks-eyes.md`) still requires. The new text is also circular: it holds candidates "from Derrick's eyes" until they clear "Derrick's eye review".
- `alienpc-max-movie-director/SKILL.md` line 58 now says: "(2026-10-19: strict still review / face-drift gates are retired from the default path…)". The question never mentioned the strict still review.
- The "aftercare keyword gate" and "48-beat sheets" were also retired. The question does not name either (lower impact; see F6).
Standing rule 6 says to ask before "changing a gate". Retiring Max's full-size and strict still review needs its own yes from Derrick, or a revert to the backups. I made no change.

No other unapproved launch was found. Nothing ran on AlienPc: `ListMachines` shows AlienPc `connected: false`, and every AlienPc-config mirror on the box is unchanged except the loop1017 snapshot (F8).

---

## Summary
- **Verdict: PROCEED WITH FIXES.** This is not "STOP: wrong approach". The direction (one start image, a short literal prompt, H3 NSFW LoRAs, pick by eye, the stock ComfyUI API) is well sourced. The test is correctly on hold for Omni. Nothing ran on AlienPc, and no running claims were made.
- **Efficiency: 2/3.** Strong community reuse and small text edits. Against that: 4 research reports and 7 Derrick cards in about 40 minutes, no quota % on either issue, and no local tier used.
- **Top findings:** E1 approvals unverifiable (process). E2/F1 gate retirement beyond the question (P1). F2 the writer-LLM retirement was approved on a one-sided summary; the 10Eros author says the opposite (P1). F3 the new default path names no minors check (P1, 50). F4 the 768x1344 "at the edge" error is still in an approved ALI-80 instruction (P2).
- **Alfred "Keep them": UNVERIFIED.** Alfred's pages saved on the box stop at 9:06 AM CT. The 8:57 "All 7" is verified from those pages.

---

## 1. Approvals

Method: I tried ReadTranscript; it was not available (E1). As a fallback I read two Alfred transcript pages that another agent had saved earlier (`/workspace/agent-tools/4e4c5e74-7d31-4507-8146-4ecf93b0d6a2.txt` and `/workspace/agent-tools/7d47ffd0-2410-479c-aafb-80a0964b4653.txt`, saved 9:08 AM CT, positions 248–339 of 340). There are no saved pages for Max. I saved the Linear reads to `/workspace/agent-tools/48026169-c631-4da3-9b14-a9889e6b7b4b.txt` (ALI-80), `d74e37a6-1a40-4f59-876b-a10278e8b4e7.txt` (ALI-80 comments), `73c3fbb2-a920-4d19-821f-b2b0e0dfd1e8.txt` (ALI-13) and `f5ab94b5-5a27-4f4f-99c8-dea8467c4d40.txt` (ALI-13 comments).

| Time CT | Wording as Max recorded it | Verified? | What was offered (per Max's files) | Change made | In scope? |
|---|---|---|---|---|---|
| 8:43 | "Yes, download all 3" | **No** (no transcript) | The 3-row "Downloads needed" table in the video community review: MysticXXX v4, HMNSFW AIO V2.5, HMMisDog | Those 3 files saved to `/workspace/max-loras/` at 8:43:49–8:43:53 | Yes. Exactly the 3 offered, all sha256 matching the source (section 5) |
| 8:54 | "Yes, add them to ALI-80" | **No** | The community gap-check items | ALI-80 comment at 8:54 with 4 settings items plus a pending-downloads list | Yes, but the comment has two errors: F4 (resolution) and F9 (it calls clip 5 an "AIO arm") |
| 8:55 | "yes download all lora" | **No** | The 8:54 "Pending Derrick" list: Anti-Burn, HMPenis, Blowjob v3 (RIFE is listed too but is not a LoRA) | Anti-Burn, PenisV2 and Blowjob v3 saved at 8:56 | Yes. 3 LoRAs, RIFE correctly left out |
| 9:04 | "i want community settings, if i made any descision that odesn match communit best pracitces we should change it" | **No** | Typed message (Max quotes it the same way in 3 files) | 24-row overrides table, DECISIONS row 81, ALI-80/ALI-13 comments at 9:10/9:11. No pack or canon wording changed (packs and canon last changed Oct 17) | Mostly. Past Derrick rows are marked "Superseded" without editing them, and gate items went to a card (good). V1 and V12 are overstated (F2) |
| 9:05 | "Not yet" | **No** | Per Max: config edits and a 27B timing test on AlienPc. The exact question text is not recorded anywhere | No AlienPc config edited (offline; box mirrors unchanged). One box snapshot edited (F8) | Yes for AlienPc. The snapshot edit is a gray area (F8) |
| 9:08 | "Yes, wait for Omni" | **No** | Hold the ALI-80 test until the FastH3 Omni-based 10Eros (Omni expected Oct 20) | DECISIONS row 82; ALI-80 9:10 comment says ON HOLD | Yes. Both sources checked (HF #68, #69) |
| 9:12 | "Yes, retire them" | **No** | Recorded question: "Retire the judges, face/hand gates, writer model and 98-check preflight from the default path (archived, not deleted)?" | 4 SKILL.md files and the loop1017 `pipeline_defaults.json` edited at 9:15–9:16, backups `.bak-20261019`; DECISIONS row 83; ALI-80 9:16 comment | **Partly.** Goes beyond the question (E2/F1, F6). "Archived" is inaccurate (F5) |
| 9:13 | "we can go ahead and do the 27b test" | **No** | Typed message (lifts the 9:05 hold for the 27B test only) | ALI-13 comment at 9:13: test plan, "when it's online" | Yes. Plan only. AlienPc offline, so nothing launched and no running claim (rule 7 met). No DECISIONS row (F10) |
| 9:14 | "make sure linear is updated and when your done get everythign audited" | **No** | Typed message | ALI-80 comment at 9:16; this audit | Yes |

### Alfred "Keep them" (about 9:12 AM CT): **UNVERIFIED**
- Alfred's pages saved on the box end at position 339 of 340, with the last messages around 9:06 AM CT. They hold no 9:12 message, so I could neither confirm nor deny "Keep them". ReadTranscript was not available.
- **Verified from the saved page:** 8:57 AM CT `"[Answering your question t25s3: \"Which of these should I put in a Linear plan and apply?\"]\nAll 7"`. The widget offered `"All 7"`, `"1–4 only (Max/review rules)"`, `"5–7 only (cleanup)"`, `"None for now"`, plus custom text.
- Context: on the same page, Alfred's message at about 9:06 says "6 of the 7 efficiency fixes are applied". `max-architect`'s profile.json changed at 9:06, and the rules file before commit e974b40 said "wording pending his confirm". So the profile edits were applied under "All 7" before "Keep them". If "Keep them" was said, it was an after-the-fact confirmation. Its exact quote and the question it answered remain unverified.

---

## 2. Findings (severity / confidence)

**F1 — P1 / 75 — The gate retirement went beyond the 9:12 question (see E2).** Evidence, verbatim from the diff of `alienpc-local-video-ops/SKILL.md` against `.bak-20261019`:
`< …if no candidate clears every check (Max full-size review AND every calibrated judge) → CAPA + HOLD from Derrick's eyes…`
`> …if no candidate clears review (Derrick's eye review; the Max full-size review + calibrated-judge gate is retired 2026-10-19) → CAPA + HOLD from Derrick's eyes…`
The same paragraph keeps "Contact/Hands stills are never soft", while the hand/limb gate is now retired, so the two contradict each other.

**F2 — P1 / 75 — V12 (writer LLM) and V1 (prompt length) were presented as community consensus, but the author of the exact model we use says the opposite.** From the 10Eros page (https://civarchive.com/models/2851079?modelVersionId=3294059), verbatim: "100% use some kind of LLM enhancer; Grok is the one I use since he has a skill preset for reference prompting." The author's reply in the comments: "Don't use i2v, use reference… Fully change the prompt with an enhancer… Don't manually prompt from scratch." The video community review quotes the "longer and more embellished" line but leaves these out. Override V12 says "Short hand-written prompts beat LLM-long", citing two indexed Reddit comments, and that is what Derrick approved at 9:12. Separately, the HF thread the review cites (https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/28) carries a community REF2VA system prompt with "`detailed_description`: **350-500 English words**", which is our own skill default. So V1's statement that our 350–500-word REF2VA rule conflicts with the community is wrong for REF2VA mode. The real conflict is I2VA vs REF2VA (split S1), plus our 795–931-word face-block prompts, which really are over-long. Fix: list V12 and the REF2VA length as split items for Derrick.

**F3 — P1 / 50 — The new default path names no minors check.** The retired 98-check preflight held an automated minors check (`audits/2026-10-17-forge-config-audit-files/preflight_check.py:246`, "minors guard on every prompt"). Its replacement (V13) is "saved API workflow + `POST /prompt` node_errors + `GET /object_info`", and none of the four retirement notes restates the minors check. The guard still exists in `loop.py` and as a stage in max-movie-director, and the canon is linked as the floor. But the new simple path (Forge posting hand-written prompts straight to `/prompt`) does not run `loop.py`, and the short matrix-cell "Preflight" list has no minors line. Under canon v2.3.0 rule 4 / 6 the minors check is always on, so it should be named in the new default path.

**F4 — P2 / 75 — The 768x1344 error (known correction confirmed) reached an approved Linear instruction.** 768 × 1344 = 1,032,192 px = **0.984 MP in ComfyUI units** (1 MP = 1024²), or 1.03 MP in decimal units. The official MiniMax guide (https://platform.minimax.io/docs/guides/local-deploy-h3) says: "use `0.98` megapixels… or set `1344 × 768` directly… Do not use the `1.0` megapixel step: it resolves to `1376 × 768`, above the H3-Base 768 × 1344 pixel-area limit". The gap check took its "≈1.03 MP" from shinshin86's doc, which says "total area capped at 768×1344 px (~1.03 MP)". So 768x1344 **is** the cap, allowed and native, not "at the edge". It did drive a decision: the ALI-80 comment of 8:54 AM CT, which Derrick approved ("add them to ALI-80"), says verbatim "4. **Resolution guard:** keep each clip at or under ~0.98 MP. 768x1344 is at the edge, so use a size the guide lists." The repeatability audit then treated "Resolution kept under ~0.98 MP" as today's decision, and later corrected it itself (C5). Override S4 leaves the number to Derrick. The ALI-80 comment was never corrected. No file or setting was changed because of the error.

**F5 — P2 / 75 — "Archived" is inaccurate.** `MOVED.txt` says verbatim: "No files moved on 2026-10-19: no file in the searched skill/pack folders exists purely for the retired gates; gate text was edited out of the default path instead". Yet ALI-80 (9:16), DECISIONS row 83 and all four skill notes say "archived, not deleted (/workspace/cos/_archive/retired-gates-2026-10-19/)". The judge scripts and rubrics are still where they were. The honest wording is: retired in place, with backups `*.bak-20261019`.

**F6 — P2 / 50 — Other items retired that the question did not name:** the "aftercare keyword gate" (Derrick had only dropped the keyword requirement for aftercare beats, Oct 17 2:03 PM CT) and "48-beat sheets" (a structural default, not a gate), now "4–6 shots". Both are low risk and in the spirit of V12, but neither was named in the 9:12 question.

**F7 — P2 / 75 — Conflicting defaults are still live elsewhere.** Verbatim evidence:
- 8 other `pipeline_defaults.json` copies were not edited. **Max says 6; there are 8.** Six are byte-identical (sha 094b8472…, the same as the edited file's backup): `audits/2026-10-17-forge-config-audit-files/agy_1017/`, `renders/5s-lock-20261016/loop1017/{scripts,live,.}/`, `audit1224/`, `agyfix1017/after/`. Two more differ: `scripts-snapshot/loop1017/deployed-20261017-0425/` (9812a1d9…) and `renders/5s-lock-20261016/loop1017/pipeline_defaults.alienpc-0912.json` (939c8a79…, writer.mode `test_arm`). All 8 still read `"production gate unchanged…"`, `production_fd 0.35`, and 6 have `writer.mode "production"`. The `live/` copy is the riskiest.
- The edited `pipeline_defaults.json` still carries guard L5 `"face gate never clears alone; a strict review verdict is required"`.
- `alienpc-stills-pose-edit-prompting/SKILL.md` was not edited and still has "## Judge harness (vision models)" and "Calibrate before every judged batch". `references/strict-still-review.md:14-15` still has the ArcFace check 8: "FAIL if… the face metric is above the acceptable band".
- `alienpc-hardcore-i2v-director/SKILL.md:67`: "`detailed_description` ~350–500 words — never paste the short intent card into Max TE" (conflicts with V1).
- `alienpc-community-matrix-cell/SKILL.md` preflight: "1-min path prefer **r2v/REF2VA first**" (conflicts with V1 / the official I2V decision).
- `alienpc-max-movie-director/SKILL.md:58` still lists "face pass (e.g. head swap)" as a stage (conflicts with V14).
- Pack `10_packs/max/production-defaults-st8-dynamic-vram.md:27`: "use the v2 face-block prompt" (conflicts with V1; pack wording needs Derrick).
- Pack `quality-stamp-before-derricks-eyes.md` still requires a "stills six-check table" stamp (conflicts with F1).
- `/workspace/forge-video-skills/*` (the copy Forge reads) is not re-synced. It still has judge, preflight and ":8189 production" text (repeatability audit G5 / C4).
- `queue_dynvram.py:11` `SHIFTV = … "12.0"` and the ST6+RIFE20 references are unchanged. That is expected (setting-only items, AlienPc on hold), but DECISIONS row 81 already calls them "Superseded", so files and decisions disagree until they are applied.

**F8 — P2 / 50 — A functional value was changed in a mirror of AlienPc config during the "Not yet" hold.** The loop1017 `pipeline_defaults.json` (its status line: "IN USE by pipeline.py") changed `writer.mode` from `"production"` to `"retired-2026-10-19"`, plus gate and candidate status strings. It is a box snapshot ("AlienPc copy unchanged"), and the 9:12 approval covers retiring the writer. But the exact 9:05 question is not recorded, so I cannot confirm whether box mirrors of AlienPc config were inside "Not yet". The JSON still parses. The edit is uncommitted in the `/workspace/cos` repo.

**F9 — P2 / 75 — Smaller ALI-80 inconsistencies.** The 8:54 comment says verbatim "1. **Clips 4 and 5 (AIO arm):** use the AIO card's settings, Euler/Simple, 12 steps, shift 6". But clip 5 is the HMMisDog arm, whose card is 8 steps, shift 6 (https://civarchive.com/models/2924146?modelVersionId=3308736: "Steps: 8 Shift: 6"). Override V3 gets this right. The ALI-80 description still says "current settings: beta6 int8, Euler 8 steps, shift 10", does not list batch-2 downloads, and does not mention the hold. Status is still "In Progress" while on hold.

**F10 — P2 / 75 — Linear and the decision log fall short of standing rules 4 and 8.** None of the 5 comments (ALI-80 at 8:54, 9:10, 9:16; ALI-13 at 9:11, 9:13) names the bot. All are authored "Derrick D" with `onBehalfOf: None`, while rule 4 says "name the bot in the comment". ALI-80 was created at 8:46 AM CT, after the 8:43 downloads (rule 4: "create/update the issue before work"). No issue records expected or actual quota % (rule 8). `max-DECISIONS.md` has no rows for 8:43, 8:54, 8:55 or 9:13 (the 27B go). Override S9 still says "Test is on hold (Derrick 9:05 'Not yet')", which the 9:13 message makes stale.

**F11 — P2 / 75 — A mis-cited key claim.** The video community review's main gap ("never loaded an H3 NSFW concept/position LoRA") cites `part2_1018/part2_run.py` notes line 107: "H3 concept LoRA files on AlienPc (mystic_v4, anatomy enhancer, pose LoRAs): not in our files". Line 107 of that file is `"9": {"class_type": "BasicScheduler", …}`, and `rg -i mystic part2_1018/` finds nothing. The claim may still be true, but this source does not support it. Override V6 repeats the citation.

**F12 — P2 / 50 — A LoRA variant risk was not flagged.** The MysticXXX v4 page (https://civarchive.com/models/2856467?modelVersionId=3266628) offers a separate `MysticXXX_MMH3-V4-ref2va.safetensors`. A widely repeated comment there says V4 "Cannot be used" on the ref2va model and "Works, but character consistency is lost" on hybrid models. The 10Eros author calls beta6 "essentially a true hybrid, i.e. just a Reference model". So the FL2VA Mystic file we downloaded may not suit REF2VA-mode beta6 runs. Getting the ref2va variant would be a new download, so it needs a card.

**F13 — P3 / 75 — Repeatability-audit accuracy.** The header says "(2026-10-19, ~9:20 AM CT)", but the file mtime is 09:03. It says "`loop1017` is a git repo (box snapshot …, 67 commits)", but `scripts-snapshot/loop1017/.git` does not exist; the folder sits inside the `/workspace/cos` repo, which has 68 commits.

**F14 — P3 / 50 — F2 (sampling) cites DETAILS.md for "Qwen thinking defaults 1.0 / 0.95 / 20".** In DETAILS.md those values appear as benchmark sampling settings (lines 125, 128), not as a stated recommendation. They are probably correct from the Qwen model card, but the Strata source does not state them as a recommendation.

**F15 — P3 / 50 — No ce-plan or ce-code-review receipt for Max's skill edits** (rule 3; Max's own profile item 4 also needs "links a ce-plan file"). There is no 2026-10-19 Max ce-plan in `cos/plans/` or `cos/audits/`; the only ce-code-review today is Alfred's. The edits are text-only, but the rule names skill/config engineering work.

**F16 — P3 / 50 — Reddit quotes can't be checked.** Reddit blocks both WebFetch and curl (302). The review already marks those quotes "(indexed)"; they stay at 50.

### Fiction rules (checked in both directions)
- **Rules missed:** F3 (no minors check named in the new default path). Everything else was followed: templates say "adult woman" / "adult couple", and the briefs cite canon v2.3.0.
- **Rules over-applied:** none found. There was no refusal based on a label, a lookalike or a hunch, and no fiction-based lane-wide HOLD. The 9:08 hold is Derrick's own model-quality decision, not a fiction hold. The H3 licence note was correctly "flagged, not judged". Retiring the ArcFace bands fits canon rule 2 ("Never judge identity from a face").
- **Identity LoRAs:** none. All 6 in `/workspace/max-loras/` are concept, motion or tool LoRAs (anatomy, sex motion, pose, anti-burn, anatomy part, act). None is a person or celebrity identity LoRA.

---

## 3. Sources spot-check (WebFetch, read live today)
| Source | Supports the claim? |
|---|---|
| HF TenStrip/10Eros-Max discussion #68 | **Yes.** Owner: "There's something causing a motion frame rate drop randomly… use the new FastH3 Omni one when it comes out". Workarounds ("dynamic video, fluid natural motions", res_multistep/lcm/euler, bypass sparse attn) are there. |
| HF discussion #69 | **Yes.** "TenStrip will change the base for Eros as soon as FastH3 Omni is released tomorrow… will probably make many of the previous turbos/tricks obsolete" (posted about 8 h before today's read, so Oct 20). |
| civarchive 2851079 (10Eros) | **Yes for the quoted lines** ("100% be loading mystic_v4…", "1 additional lora at 0.5…", "Jamming like 10 motions…", "true hybrid, i.e. just a Reference model", "not good to run on smaller cards", 8-12 steps, 10/3). **Omitted counter-points:** see F2. |
| civarchive 2834417 (AIO) | **Yes.** "Sampler - Euler Scheduler - Simple Steps - 12 Shift - 6 Turbo LoRA - Strength 0.5"; "0.5 - 0.9"; "maybe a low strength penis/pussy LoRA"; 82.05 MB; sha matches. Note: the card assumes a separate Turbo LoRA at 0.5 on a base model, not a TURBO merge. |
| civarchive 2924146 (HMMisDog) | **Yes.** Euler/Simple 8, shift 6, no trigger; sha matches. |
| civarchive 2856467 (Mystic v4) | **Yes.** "Recommended strength: 0.2 – 1"; sha matches. See F12. |
| civarchive 2849923 (HMPenis v2) | **Yes.** sha matches. Trigger `HMPenis`, which is missing from MANIFEST (V7 already covers this). |
| HF Imagineer13/H3-Anti-Burn-LoRA | **Yes.** `LoraLoaderModelOnly`, clips 2+, start 0.5, not on clip 1; sha matches. |
| docs.comfy.org minimax-h3-native | **Yes.** 1344×768 native, 17k+5, I2V opens at 1:1 / 0.4 MP, `first_frame` stretched / `last_frame` center-cropped. |
| platform.minimax.io local-deploy-h3 | **Yes.** 0.98 MP / 1344×768; 1.0 MP → 1376×768 above the limit; licence excludes US/EU/UK/KR. |
| shinshin86 comfy-agent prompting doc (raw) | **Yes.** "124… One shot, one action beat. 2–5 sentences"; "Do not re-describe…"; and the ~1.03 MP line behind F4. |
| HF MiniMax-H3 discussion #28 | **Yes for "2-3 segments / 1-3 sentences".** But it is a user-posted system prompt (a reply calls it "all wrong… RTFM"), and the same thread has the 350–500-word REF2VA rule (F2). |
| civitai 2920367 | **Yes.** "Turbo is already baked into 10Eros. Do not add LightX2V…"; "BasicGuider — no negative prompt, no CFG". |
| kingsclaw blog (ComfyUI automation) | **Yes.** `POST /prompt`, `/history/{id}`, `/queue`, no webhook. |
| GitHub Niko1221/Strata #3110 | **Yes.** "~14.7 GB of VRAM and ~44 GB of RAM", Linux, "Not tested: Windows". |
| Strata DETAILS.md (raw) | **Yes.** tool_call_recovery "98.3%… 92.9%" on 1,462 turns; GPU vision "~1.4 GB of VRAM"; CPU reader under 24 GB; prevent_sleep; expert_profile_save; "Run with highest privileges"; ~24x slower start; `--calibrate` 15-30 min. Sampling caveat in F14. |
| Pi settings.md (raw) | **Yes.** defaultThinkingLevel default `"medium"`; httpIdleTimeoutMs `300000`; provider maxRetries `0`; compaction 16384/20000. |
| Reddit 1wbpwcq and other Reddit threads | **Not checkable** (blocked). Already marked "indexed" (F16). |

Claims with no source: the beta6-on-16-GB VRAM figure ("15.0-15.8 GB of 16.3") is box-internal, so fine. The "never loaded an NSFW LoRA" claim has a broken citation (F11). The rest of the overrides table cites a source or a file line.

---

## 4. Consistency (files ↔ Linear)
- **Agree:** the ON HOLD for Omni (DECISIONS 82, overrides header, ALI-80 at 9:10); no AlienPc change (all files and comments); the V11–V13 list (DECISIONS 83 = ALI-80 9:16 = skill notes); the Forge F-items (overrides §B = ALI-13 9:11).
- **Disagree:** F4 (ALI-80 8:54 vs S4); F5 ("archived" vs MOVED.txt); F7 (8 old pipeline_defaults copies, stills skill, hardcore-director line 67, matrix-cell REF2VA-first, packs, Forge copy); F9 (clip 5 label; stale description); F10 (S9 still says 27B on hold; no 9:13 DECISIONS row).
- **DECISIONS diff vs backups:** `.bak-20261019-0905` → `.bak-20261019-0913` adds rows 81 (9:04) and 82 (9:08). `.bak-0913` → current adds row 83 (9:12). No old rows were rewritten. Good.

## 5. LoRAs — sha256 re-run (all match MANIFEST and the source pages)
| File | sha256 (re-run) | Match |
|---|---|---|
| MysticXXX_MMH3-V4.safetensors | fc3e856d…3068afba | MANIFEST ✓, CivArchive ✓ |
| HMNSFW-AIO-V2.5.safetensors | a07732a8…5951a9d2d | ✓ / ✓ |
| hm_nsfw_mis_doggy_only_v16_r32_384_minimax-h3_epoch170.safetensors | efa6e4de…3de5d707 | ✓ / ✓ |
| h3_antiburn_universal_v1.safetensors | 8f76dc3c…6120d0f154 | ✓ / HF ✓ |
| PenisV2_minimax-h3_epoch60.safetensors | 017dd1ad…ac1f1b3 | ✓ / ✓ |
| MM-H3 - Blowjob v3.safetensors | fbb93a67…99277d53 | ✓ (source page not re-opened) |
No identity LoRAs.

## 6. Max checklist
| Item | Result |
|---|---|
| Community source cited? | **Yes**, widely, with F2 (one-sided), F11 (broken cite) and F14 (weak cite) |
| Smallest fix? | **Mostly.** Text notes plus status strings, no new scripts or daemons. The 24-row table is big but is a list, not a build |
| Custom lines added | **18 changed lines** (skills: 12 `>` lines across 4 files; pipeline_defaults: 6). Of those, **4 are new lines** (2 top notes, 1 matrix-cell note, 1 JSON key); the rest rewrite existing lines |
| Local setup mirrors a known community setup? | **Planned, not yet** (official H3 I2V template, stock `/prompt`+`/history`, card LoRA settings). On hold for Omni / AlienPc offline |
| ce-plan / ce-code-review receipt? | **No** (F15) |
| Linear updated? | **Yes**, ALI-80 at 8:54, 9:10, 9:16 and ALI-13 at 9:11, 9:13. But no bot named, description stale, no quota % (F9, F10) |
| Quota/approval needed and obtained? | Approvals **claimed, not verified** (E1). Gate scope exceeded (F1). Quota % **not recorded** |
| Running claims live-checked? | **N/A, correct.** No "running" claim was made. The 27B test is a plan and AlienPc is offline (`connected: false`) |

## 7. Efficiency score: **2 / 3**
- Community reuse: high (official template, stock API, card settings, community LoRAs, latent chaining, Anti-Burn).
- Smallest fix: yes for the edits; the research volume was large.
- Rounds vs budget: 4 research reports (8:41, 8:53, 9:02, 9:03 CT) that partly overlap (resolution and AIO settings were researched twice), and 7 Derrick cards in about 40 minutes. At most 2 parallel workers looks to have been respected (two reports finished about a minute apart).
- Quota % expected vs actual: **not recorded** on ALI-80 or ALI-13 (rule 8).
- Local tier used: **no.** AlienPc was offline; all research and diffing ran on the paid tier.

## 8. Done correctly
- The downloads match the approvals one for one. All sha256s are recorded and re-verified, and none is an identity LoRA.
- The ALI-80 test was put on hold for Omni, with sources (#68/#69) checked and true.
- "Not yet" was respected: no AlienPc config was touched, and no 27B test was launched or claimed to be running.
- Gate items were sent to a card (V11–V13) instead of being self-approved. Old DECISIONS rows were left intact, and backups were made before every edit.
- Pack and canon wording were not edited.
- The minors guard is kept in the movie-director stages and through the canon links. No fiction over-refusal.
- The repeatability audit caught the units error on its own (C5) and flagged the resolution as a Derrick pick.

## 9. Required fixes (for Max; none applied by me)
1. **F1/E2:** Restore the "Max full-size review" wording in the local-video-ops CAPA paragraph and the "strict still review" in max-movie-director from `.bak-20261019`, or get Derrick's explicit yes to retire them. Also fix the circular "HOLD from Derrick's eyes until Derrick's eye review" wording and the "Contact/Hands never soft" contradiction.
2. **F3:** Add one line to the new default path (the V13 replacement and the matrix-cell preflight): "minors text guard (canon v2.3.0 rule 4) runs on every prompt before `POST /prompt`."
3. **F4/F9:** Post a correction on ALI-80: 768x1344 = 0.98 ComfyUI-MP, the guide's native cap, so it is allowed; clip 5 is MisDog (8 steps / shift 6), not AIO. Update the description (hold, batch-2 LoRAs).
4. **F5:** Change "archived" to "retired in place (text), backups `*.bak-20261019`; no files moved" in DECISIONS row 83, ALI-80 and the 4 skill notes.
5. **F7:** List the 8 unedited `pipeline_defaults.json` copies (not 6) and mark them superseded or archive them with backups. Mark the stills-pose-edit judge harness and strict-still-review check 8 as retired or optional. Re-sync or point `/workspace/forge-video-skills`. Remove guard L5 or mark it retired.
6. **F10:** Name the bot in Linear comments. Add expected and actual quota % to ALI-80 and ALI-13. Add DECISIONS rows for 8:43, 8:54, 8:55 and 9:13. Update override S9.
7. **F11/F13/F14:** Fix the part2_run.py citation, the repeatability-audit timestamp and the "67 commits" line, and the DETAILS sampling citation.
8. **F15:** File a short ce-plan / ce-code-review receipt for the skill and JSON edits.
9. Re-run approval verification with ReadTranscript (E1), for both Max and Alfred's "Keep them".

## 10. Only Derrick can decide
1. Whether to also retire **Max's full-size / strict still review** before clips reach him (F1). It is not covered by "Yes, retire them" as recorded.
2. Whether to keep the **writer-LLM retirement (V12)** and the I2VA move now that the 10Eros author's "100% use some kind of LLM enhancer… Don't manually prompt from scratch" is on the table (F2). Also REF2VA vs I2VA (S1).
3. **Resolution:** 768x1344 (= 0.98 MP, native cap) vs 768x1120 vs ~0.6 MP (S4, F4).
4. Pack wording changes to match the overrides: production-defaults "v2 face-block prompt" and the quality-stamp "six-check table" (F7). Pack edits need his explicit yes.
5. Whether to download the **MysticXXX v4 ref2va** variant for REF2VA-mode beta6/Omni runs (F12).
6. Forge context size 64K / 96K / 128K (S7); the Strata update channel (F9); calibrate (F8); Windows policy (F7, admin).
7. The H3 licence territory note (US/EU/UK/KR excluded), verified on the MiniMax guide.
