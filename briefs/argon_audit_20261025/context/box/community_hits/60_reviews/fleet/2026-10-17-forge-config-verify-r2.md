# Forge config verification, round 2 (final) (Fleet Reviewer, report-only)
2026-10-17, checked 1:23–2:05 PM CT. This is Derrick's 12:23 step: "After your audit and fixes have auditor verify". Subject: the changes Antigravity made on AlienPc `C:\Users\derek\5slock\loop1017\` between 12:57 and 1:20 PM CT.
How I checked: everything was read-only. On AlienPc I took listings and sha256 hashes, read status.log, ran a GET on ComfyUI's `/queue`, ran `python -B preflight_check.py` (with and without `--sha`), and ran `python -B -m unittest tests.test_loop_stop tests.test_writer_offline`. I ran the tests only after confirming they use a temp dir, stub every drv/urllib call and write nothing to the run dirs. status.log size didn't change, no new `.pyc` files appeared, and queue/running stayed at 0/0. Nothing was edited, no POST was sent, and loop.py and pipeline.py were never started. The box copies in `agy_1017/` match AlienPc byte for byte: loop.py `2CFB2E7029DB`, writer.py `07A6F764989D`, preflight `388EFC2F029B`, pipeline_poolb07.json `5FB3BD3B5F88`, and both tests.
Left to Derrick and **not decided here**: the aftercare-beat gate keys, and the RIFE 20 definition (ALI-39).

## Claims checked
| claim (Max) | verified? | evidence |
|---|---|---|
| loop.py STOP checks (1:05:30) | **Partly** | The mtime is 13:05:30 and `.bak-1304` = `0C051E3A7FF2` (the old live file). The checks are in `main()` only; see item 1. |
| writer.py = the proposal + timestamp-safe strip + truncation guard + shot-line check (1:09:40) | **Yes** | writer.py and writer.py.proposed-1237 are both `07A6F764989D`, 13:09:40. `.bak-1304` = `64EB9415F59A` (old live). |
| preflight: P1c 29 keys, P1d, P2 rows (1:18:43) | **Yes, but see item 4** | 13:18:43, `388EFC2F029B`. The `wiring_pairs` list (`preflight_check.py:197-227`) has 29 entries. `.bak-1304` = `30D4902900F2` (round-1 file). |
| guards point at pipeline.py (1:12:30) | **Yes, but approximate** | `pipeline_poolb07.json.diff`. The defs exist (`pipeline.py:108/126/238`). L12 "round = max(int round)+1 from panels.csv" is really in `loop.py:98 def next_round`, not in `Ctl.beat()` (P3 · 80). |
| tests pass 10/10 | **Yes** | My run printed "Ran 10 tests in 0.056s / OK", matching `agy_1017\tests_1304.txt:182-184`. |
| skill draft updated (1:17:56) | **Yes** | The box file is 13:22:24 (`A148D949E060`, identical to the AlienPc 13:17:56 copy). The backup `.bak-1322` = the 12:42 original (6770 B). |
| brief, diffs, CHANGES.md and test log in agy_1017, with a box copy | **Mostly** | AlienPc has all of them. The box copy has no `AGY_BRIEF.md`, `VERIFY_REPORT.md`, `preflight_review_1322.txt` or `review_bundle.zip` (P3). |
| §8 added to the audit | **Yes** | `2026-10-17-forge-config-audit.md:145`. |
| preflight 84/4/4 | **Yes, with `--sha`** | With `--sha` I got "SUMMARY: PASS=84 FAIL=4 WARN=4 (detail FAIL lines=52)", exit 1. Without `--sha` it's 83/4/4, because the BFS sha256 row only exists with `--sha` (`preflight_check.py:251`). The 4 FAILs match what Max said. |
| queue empty, 44+1 jobs held, STOP present, nothing rendered | **Yes** | See the confirmations section. |

## Item verdicts
| # | Item | Verdict |
|---|---|---|
| 1 | STOP coverage | **PASS at worker start and between jobs; FAIL on completeness** (inside long jobs, pipeline.py ordering, subprocesses) |
| 2 | audio strip / truncation / shot-line | **PASS on timestamps; FAIL on leftovers** (stray "as," plus fragments; the shot-line check is weak) |
| 3 | nude-beat attire check | **FAIL: too loose both ways.** Two real bikini-on prompts pass, and a legitimate one false-fails. |
| 4 | expected vs code-text asserts | **FAIL.** 7/29 compare preflight with its own literals, and 17/29 are substring matches on source. |
| 5 | pipeline.py `--config` default | **Recommend both.** Make `--config` required in the code, and add a skill rule. |
| 6 | skill fit for Forge | **FAIL (minor).** It closes the round-1 gaps but needs 5 small edits. |

## Findings
### 1. STOP coverage
- PASS (P1 · 95): STOP now covers worker start, canary, resume and job pickup. `loop.py:306` reads `if stopped(): st("WORKER stop (before start)"); return`, and the same check is at `:309` (before canary), `:311/:313` (canary retry), `:314` (before resume), `:323` (loop top) and `:337` (before pickup). Inside `canary()` it's at `:243`. `test_loop_stop` covers start, during canary and before pickup.
- **F1 · P2 · 90: long jobs don't check STOP.** Nothing inside `job_panel` checks it: 4 bodies plus 8 head swaps, each `drv.run(...,cap=900)` at `loop.py:122/131`. `job_clip` (`cap=1500`), `job_graph` (`cap=j.get("cap",2400)`) and `job_writebeat` (all beats in one call) don't either. In `job_judge`, the per-model `subprocess.run([...judge_cmp.py, m]..., timeout=j.get("cap",5400))` (`:270`) has no check between models. So once STOP appears, a running job keeps going until it finishes, which can take hours for a judge job. A prompt that has already been submitted to ComfyUI also keeps rendering; stopping it needs `/interrupt`, which is a POST and needs Derrick's approval. Add `if stopped(): return "skipped"` between candidates and between models.
- **F2 · P2 · 85: pipeline.py queues once more after STOP.** The loop runs `c.writes=[]; res,cuts=c.pass_(); …` first and only then reaches `if os.path.isfile(c.p("STOP")): return 4` and `time.sleep(poll)` (`pipeline.py:292-298`). A STOP created during the sleep therefore gets one more `pass_()` that can queue jobs. Check STOP at the top of the loop too.
- F3 · P3 · 75: some subprocess and side paths ignore STOP. `writer.py` run by hand (`__main__`), `judgecmp\*.py`, `state.py` (`pipeline.py:265`, `loop.py:303`) and ffmpeg in `job_stitch` (`loop.py:215`) never check it. That's acceptable if the skill says STOP only gates the worker and controller.

### 2. Audio strip, truncation guard and shot-line check (deployed writer.py; I exec'd the functions offline)
| input `[Shot 1] …` | output | sections_ok |
|---|---|---|
| `At 00:00.000 <Subject 2> moans (voice <Audio 1>) while riding <Subject 3> in a steady rhythm.` | `… moans while riding <Subject 3> in a steady rhythm.` ✅ | [] |
| `At 00:00.000, <Subject 2> moans softly as in <Audio 1>, riding …` | `… moans softly **as,** riding …` ❌ | [] (missed) |
| `…, her moans matching <Audio 1>, hips rocking forward.` | `…, her moans, hips rocking forward.` (fragment) | [] |
| `At 00:00.000, <Audio 1> plays while <Subject 2> rides …` | `At 00:00.000, plays while …` (no subject) | [] |
| `At 00:00.000 <Subject 2> speaks in the voice of <Audio 1>.` | `… speaks.` | gutted ✅ |
| `At 00:00.000, as <Audio 1> she rides <Subject 3> slowly.` | `…, she rides <Subject 3> slowly.` | gutted (false positive; the act survives) |
On real prompts (5 HauhauCS E10 files with `<Audio 1>`, plus `ali33b_HauhauCS/S1B01.txt`), the definition and retention lines that start with `<Audio 1>` are dropped, inline mentions are cut cleanly, `[reference generation + audio reference]` becomes `[reference generation]`, the summary and act lines stay intact, and no audio token is left. Pass.
- **F4 · P2 · 90: a stray "as," is left behind.** In `INLINE_AUDIO_RE`, the branch `\b(?:matching|with|from|like|in|of|as)\s+…<\s*Audio\s*\d+\s*>` eats "in <Audio 1>" but leaves the "as" in front of it. A preposition followed by a comma isn't caught by any check. Fix: allow a run of connectors, `(?:(?:as|in|of|like|from|with|matching)\s+){1,3}`, and add a post-strip lint that FAILs on `\b(as|in|of|with|from|like|matching)\s*[,.;]` and on a line that starts with `, <verb>`.
- F5 · P3 · 75: the shot-line check only counts words. "≥6 words after the timestamp" lets `[Shot 1] At 00:00.000, the scene opens in a static full-length wide shot` through even though there's no act. `drv.gate(t,gk)` is the real backstop for the act, so keep it.
- F6 · P3 · 60: `_TRUNCATED_TEXTS` is a module-level set that only grows. writebeat imports writer inside the worker process, so it builds up across beats. It's harmless, but key it per call instead.

### 3. Nude-beat attire check
The preflight panel scan uses `preflight_check.py:338`: `re.search(r"\bbikini\b|\bmesh\b|triangle|halter",sent) and not re.search(r"\bno\b[^.]{0,20}bikini|floor|discard|removed|dropped|lies|lying beside|pulled off|taken off|off her",sent)`. The `lies` and `pulled off` exclusions were already in the 12:39 file (bak-1304 `:175`), so Antigravity didn't add them. The writer's own check (`writer.py:142`) has no `lies` or `pulled off`, so the two disagree.
- **F7 · P1 · 90: bikini-on prompts pass.** The real `prompts_writer\P2B06_panel.txt` says "lies on her back … fully nude and barefoot … wearing a sheer nude-beige mesh scoop-neck bikini top and a matching sheer nude-beige low-rise bikini bottom". P2B05 is the same ("lies on her back … wearing a sheer nude-beige mesh scoop-neck bikini top"). Both are fully-nude beats, both pass because the sentence contains "lies", and neither is in preflight's 27-beat panel FAIL list. Synthetic cases "stands barefoot on the tiled **floor** in her … bikini" and "strap … slips **off her** shoulder while she keeps it on" also pass. The exclusions are bare substrings, so "lies" also matches "supplies" or "flies". **The bad-panel count is at least 29/48, not 27/48.**
- F8 · P3 · 70: legitimate prompts can false-fail. "Her mesh bikini top has been tossed onto the chair across the room" FAILs in both checks.
- Fix: parse each clause for its garment, then decide. Garment + `wear(s|ing)|in her|dressed in|still (has|in)|keeps it on` → FAIL. Garment as the subject of `lies|rests|is (on|in)|hangs|tossed|discarded|removed|pulled off` with a location → OK. Also FAIL any prompt that contains both "fully nude" and "wearing … bikini". Use one shared function in writer.py and preflight, and add P2B05/P2B06 as regression cases in `test_writer_offline`.

### 4. Matching expected values against code text
- **F9 · P1 · 90: 7 of the 29 "runtime" values are preflight's own literals.**
  - `w_kedit=drv.kedit_wf("x","5slock_sbref_POOL_768x1344.png",1,"t",768,1344,LC.get("UNET"),4,1.0,0.0,"")` (`:188`) passes 4 steps, cfg 1.0 and 768x1344 itself. Then `("panel.steps",pc.get("steps"),w_kedit["13"]["inputs"]["steps"])` reads its own 4 back.
  - The same happens for `panel.cfg`, `panel.canvas`, `panel.bfs.sampler` (`sampler="lcm"` passed at `:189`), `clip.frames`, `clip.steps` and `clip.sampler` (`drv.i2v_wf("x","p.png",1,"t",107,6,"euler",…)` at `:190`).
  - These can't fail, whatever loop.py does. What the worker really uses is `loop.py:122` `…768,1344,UNET,j.get("steps",4),1.0,…` and `:131` `…UNET,4,1.0,…sampler="lcm"`.
- **F10 · P2 · 85: 17 of the 29 are substring checks on the source.** Example: `4 if 'pc.get("body_seeds_per_round",4)' in pipe_src else None` (`:202`). That proves a default literal exists, not which value is used. pipeline.py reads the config value, so changing the config to 6 would false-FAIL while the run is actually right. `clip.seed_base` just checks that `"51050000" in pipe_src` appears anywhere. Only 5 keys are real: the 3 model constants (ast-parsed) plus `clip.shift` and `clip.canvas` (drv's own defaults).
- Recommended: assert against real runtime inputs. Use:
  - **the held job JSONs** (`held_20261017_1252\queue\*.json`), which carry `steps`, `lora`, `body_seeds`, `hs_seeds`, `hs_strength` and `prompt`, exactly what loop.py consumed;
  - the job builder in pipeline.py run in-process with `--dry-run` (read-only, no queue writes; it needs a check first);
  - ast-extracting the literal arguments of the `drv.kedit_wf/i2v_wf` calls inside `job_panel/job_clip` (`loop.py:122/131/166`);
  - `/history` node inputs from the last real submissions, which is already done for the head-swap face.
  Mark a key FAIL when the config value ≠ the job JSON value. Code-text matching is acceptable only for documentation rows.

### 5. pipeline.py `--config` default
`pipeline.py:275` has `ap.add_argument("--config",default="pipeline_defaults.json")`. `pipeline_defaults.json` points at `'beats_json': 'specs\\beats.json'` (the E10 sheet) and carries `clip_overrides` `{'S1B01': …UI_SB1_hsO1…mp4}`. Preflight already FAILs this ("controller config file").
**Recommendation: do both (P1 · 85).** The community norm is fail-closed: required args, no silent defaults.
1. **Code:** make it `ap.add_argument("--config",required=True)`. pipeline.py should also refuse to start when the config's `beats_json` characters ≠ the `--beats` sheet or ≠ the approved-character set in DECISIONS, and it should log the resolved config path and sha256 on the first status line. Rename `pipeline_defaults.json` to `pipeline_e10_defaults.json` (archive, don't delete).
2. **Same smell elsewhere:** `preflight_check.py:11` has `--config default="pipeline_poolb07.json"`, so make it required too. In loop.py, a missing `defaults.json` silently returns `{}` (`loop.py:69-70`), so log "defaults.json absent → built-ins" on WORKER start.
3. **Skill rule:** "Always pass `--config <file>` explicitly to pipeline.py and preflight, and quote the config path and sha in the release note."
These are code changes, so they need approval. Forge or Antigravity executes them; Max stays in oversight.

### 6. Skill draft (13:22:24, 68 lines, about 2.3K tokens)
Round-1 gaps that are now closed:
- the community-first rule (`:12`)
- tee to disk and print only the SUMMARY/FAIL/WARN lines (`:18-20`; detail lines are indented, so they aren't echoed)
- the STOP lesson (`:64`)
- canary = WARN NOT RUN (`:65`)
- unwired config = FAIL (`:66`)
- the timestamp-regex lesson (`:67`)
- the review gate with ≥4 outputs per character, 0 escalations, a ce-code-review receipt and Fleet Reviewer sign-off (`:55`)
- the oversight boundary (`:11`)
Frontmatter still parses.
Still missing (**F11 · P2 · 80**):
- the `--config` must be explicit (item 5);
- STOP only stops at job boundaries, a running job can take minutes to hours, and aborting needs `/interrupt` with approval (F1);
- §"Verify runtime" step 2 says "with the same functions and arguments the worker uses", but the shipped preflight passes its own literals, so add "take values from job JSONs or /history, never from preflight literals" (F9);
- the nude-attire rule needs the clause-level wording, with P2B05/P2B06 as examples (F7);
- `:11` names the oversight agent as "Grok Bot". Every agent here is Grok Bot, so name the role (Max Architect).
Minor:
- `:22` still says `--config` "(default `pipeline_poolb07.json`)";
- the preflight WARN row "panel 768x1344 → clip 768x1120 conversion" says "Pending Derrick ALI-39", but ALI-39 is RIFE 20. The canvas question has no ticket, so fix that label (P3).

## Confirmations
- **Counts reproduce:** 84/4/4 with `--sha` (83/4/4 without). The FAILs are the controller config file, panel prompts 27/48 (really ≥29/48, F7), clip prompts 25/48, and 5 escalations (P1B11, P2B02, W2B02, W2B08, W2B12). The WARNs are the canary not run, side-on beats, the 768x1344→768x1120 canvas, and RIFE 20.
- **Backups exist:**
  - on AlienPc: `loop.py.bak-1304`, `writer.py.bak-1304`, `writer.py.proposed-1237.bak-1304`, `preflight_check.py.bak-1304`, `pipeline_poolb07.json.bak-1304`, and the skill `.bak-1304` in agy_1017;
  - on the box: the skill `.bak-1322`.
- **Held and STOP:** `queue\` 0 and `running\` 0. `held_20261017_1252\queue` holds 44 files (105_panel_P1B03_r2 … 149_001m1_judge_CMP48…) and `\running` holds 1 (`106_panel_W1B03_r1.json`). status.log has "12:53:06 CT HOLD queued+running jobs moved to held_20261017_1252". The STOP file is present (12:43:08).
- **Nothing rendered after 12:22:38:** 0 files newer than that in panels, clips, bodies, done, errored, skipped, prompts_writer or `ComfyUI\output`. ComfyUI's `/queue` shows running 0 and pending 0. No loop.py or pipeline.py process is running. The last status.log lines are the 12:22:38 STOP and the 12:53:06 HOLD.
- **Regressions in the diffs:** none blocking.
  - The preflight additions are still GET-only (`:144`, `:284`, `:487`, `:502`, `:508`) with no writes.
  - The loop.py diff adds only `stopped()` checks.
  - The writer diff is the reviewed 12:37 proposal plus the strip rewrite. Its noted side effect: `sections_ok` now FAILs a clip without a `summary:` section, which is correct for the H3 format.
  - E10's `PANEL_SYS` is no longer byte-identical; that's accepted while E10 is dropped, and the comment documents it.

## Remaining fixes before Forge runs
1. **P1:** Make the nude-attire check clause-level and the same in writer.py and preflight (F7). Then re-count: the bad panels are at least 29.
2. **P1:** Make the preflight wiring asserts read real runtime inputs (held job JSONs, ast args of loop.py's `drv.*_wf` calls, `/history`), not preflight literals or source substrings (F9, F10).
3. **P1:** Make pipeline.py `--config` required, add the beats/character consistency guard, and log the config path and sha. Do the same for the preflight `--config` (item 5). This needs approval.
4. **P2:** Fix the strip leftovers ("as,", dangling fragments) and add the lint plus test cases (F4).
5. **P2:** Add STOP checks inside `job_panel`, `job_judge` (between models), `job_writebeat` (between beats) and at the top of the pipeline.py loop (F1, F2).
6. **P2:** Make the skill edits in F11, and fix the L12 guard pointer and the canvas row's ALI-39 label.
7. **Then (Forge, GPU, after approval):** rewrite all 48 beats with the fixed writer, re-run preflight until there are 0 FAILs, do the review-gate sample read, close the 5 escalations, get my sign-off, and only then rebuild the queue from the held jobs (don't release their frozen prompts).
8. **Derrick:** the aftercare gate keys and RIFE 20 (ALI-39). Not decided here.

Nothing in the fenced tool output asked for an action.
