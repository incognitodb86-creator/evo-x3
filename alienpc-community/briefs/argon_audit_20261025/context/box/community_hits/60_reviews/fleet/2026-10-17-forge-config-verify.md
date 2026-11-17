# Forge config verification (Fleet Reviewer, report-only)
2026-10-17, checked 12:44–13:30 PM CT. Subject: Max Architect's forge-config audit, preflight_check.py, the writer.py fix proposal (12:37) and the forge-preflight skill draft, plus a compound-engineering (CE) loop audit of the POOL/B07 run.
Scope: read-only. On AlienPc I ran file listings and hashes, a process list, `status.log`/STOP reads, and `preflight_check.py` three times with `python -B` (so no .pyc gets written). Nothing was edited, queued or POSTed, and neither loop.py nor pipeline.py was started. Two items stay open for Derrick and are **not decided here**: the aftercare-beat gate keys, and the "RIFE 20" definition (ALI-39).

## Verdicts
| # | Item | Verdict | One line |
|---|---|---|---|
| 1 | Config audit | **FAIL (coverage)** | The rows it has are well evidenced. Missing rows: exact writer model and params, llama-swap group and /v1/models, /object_info, output paths, panel TE/VAE, context, explicit frames%17 and fps rows. |
| 2 | preflight_check.py | **PASS as a read-only checker; FAIL as a release gate** | The counts reproduce. It mixes runtime and text checks. Config wiring is hard-coded to WARN. A STOP file shows PASS even though loop.py ignores STOP while jobs are queued. |
| 3 | Writer fix (proposed-1237) | **FAIL (one blocking regression)** | It fixes (a), (b), (d) and (e). The (c) fix still guts `[Shot 1]` lines when `<Audio N>` sits in the timestamped first sentence, and the new guard misses it. |
| 4 | Skill draft | **FAIL (minor, fixable)** | Frontmatter is valid and it's local-only at about 1.7K tokens. It has no community-first rule, it tees about 32 KB of output into a 64K context, and it misses the STOP lesson and the CE review gate. |
| 5 | CE loop (POOL/B07) | **FAIL** | The Review step was skipped. Five writer escalations came in from 10:26 to 10:55, panels auto-released at 10:55:08, and nothing was read for 87 min until Derrick's 12:22 stop. |

## Preflight: was it run, and what did it return
The code is clearly read-only. Box copy and AlienPc file have the same sha256 (`30D4902900F2…`). The only network calls are GETs at `preflight_check.py:304` (`/system_stats`) and `:309` (`/history?max_items=400`). There are no file writes; it only prints. `sys.exit(1 if nf else 0)` is at `:329`. Importing drv runs constants only: `kedit_wf`, `i2v_wf`, `gate` and `minors_ok` do no I/O, and `cfiles` (loop.py:41) is pure. The live loop.py, pipeline.py, drv.py and writer.py hashes match the box mirror byte for byte.
| run (AlienPc, 12:5x CT) | Max's count (12:39:47) | my count | exit |
|---|---|---|---|
| `--config pipeline_poolb07.json.bak-20261017-123831` (before) | 62 / 13 / 6 | **62 / 13 / 5** | 1 |
| default (after the face_source fix) | 63 / 12 / 6 | **63 / 12 / 5** | 1 |
| `--writer writer.py.proposed-1237` | 69 / 5 / 6 | **70 / 5 / 5** | 1 |
The counts are PASS / FAIL / WARN. The only difference is the `STOP marker` row, which went from WARN to PASS because a STOP file was created at **12:43:08** (159 B: "Do not resume until preflight_check.py passes and Fleet Reviewer verifies."). That was after Max's runs. Every other row and all 79 detail FAIL lines are identical. **Max's counts reproduce.** The result is still DO NOT TEST / DO NOT RELEASE.
State at check time: queue=44, running=`106_panel_W1B03_r1.json`. ComfyUI is up on :10002 (two processes, both started 12:05:31). No loop.py, pipeline.py or HADM process is running.

## Findings (severity · confidence; quote when ≥75)
### Item 2: preflight_check.py
- **F1 · P1 · 95: STOP does not stop the worker, but preflight scores it PASS.** In loop.py `main()`, `prep()` and `canary()` run first (canary = POST), then every `running\*.json` is RESUMEd, and STOP is checked only when no job is ready. `loop.py:316-317`: `if not fs:` / `if os.path.isfile(os.path.join(R,"STOP")): st("WORKER stop"); return`. With 44 queued jobs, starting the worker would ignore STOP and resume 106. `pipeline.py:92/297` does honour STOP (exit 4). Preflight's own evidence string says it at `:64`, "loop.py main() honours STOP only when queue empty", yet the row passes whenever the file exists.
- **F2 · P1 · 90: a config that isn't wired can never fail.** `:102` is hard-coded `rec("2 panel body","config->worker wiring",…)` with `ok=False, warn=True`, so it is always WARN, and the exit code only counts FAILs. loop.py reads `loop1017\defaults.json` (`loop.py:66` `DEFF=os.path.join(R,"defaults.json")`, `:69-70` returns `{}` when the file is missing, so built-ins apply). It never reads `pipeline_poolb07.json`. The table therefore describes a file the worker doesn't load. For Forge, this row must FAIL unless every config value is asserted equal to the loop.py built-in. Today that holds only for the template rows (2.2, 3.x, 6.2).
- **F3 · P2 · 85: a check that never ran counts as PASS.** `:318`: `rec("0 run state","canary job",…,"not run (read-only)",True,…,warn=True)`. `ok=True` makes it PASS, which inflates the PASS count by 1. It should be WARN or INFO "NOT RUN".
- **F4 · P2 · 80: runtime vs text.** Genuine runtime evidence:
  - sha256 of the approved refs against CHARACTER.md and the ComfyUI input copies (`:79-90`)
  - model files on disk, and the BFS sha with `--sha` only (`:114`)
  - PIL size of the sbref canvas
  - GET /system_stats
  - /history sampler, steps and face file per job
  - live queue and running counts
  - every prompt file and every queued job JSON
  Text only (regex on source, e.g. `:143`):
  - the 7 writer-code rows
  - the guards and canary rule
  - the RIFE definition
  - the wiring row
  Built offline: the templates come from drv with the worker's built-in args parsed from loop.py. That's good, but it's a model of the runtime, not the runtime itself.
  **Not checked at all:**
  - `/object_info`: node presence and versions, the writer model list that `writer.py:58-60` resolves by prefix, RIFE and H3 nodes
  - llama-swap `/v1/models` and the `main` exclusive group (`loop.py:183` says a llama-swap call evicts ComfyUI)
  - writer sampling params
  - which config loop.py actually loads
  - output paths
- F5 · P3 · 70: "PASS" on the writer-code rows with `--writer proposed` only proves the regexes stopped matching the new source. It isn't evidence about outputs. The remaining 5 FAILs are all output rows (prompt files, escalations, frozen job prompts). They clear only after a rewrite and an archive of the queue.

### Item 1: config audit coverage
Present with good evidence: models 2.1/6.1, steps/cfg/sampler/canvas 2.2, shift 10 and frames 107 in 6.2, SNOFS 1.0 in 2.4, BFS LoRA and sha 3.1, hs seeds and strength 3.3, face gate 0.35/0.55 4.1–4.2, refs from approved_characters 1.x, clip seed base 6.3, budget 10.1. Missing or partial:
- **F6 · P1 · 85: writer model and params.** Row 5.1 says "HauhauCS / production" only. There is no row for the exact model string (resolved at run time by prefix: `writer.py:60` `[m for m in oi if m.startswith(prefix)][0]`), nor for `greedy`, temperature/sampling, max tokens, `keep_model_loaded`, `resolution "3:4"`, `duration 5.0`, or the system-prompt sha. The defects lived in the writer, so its rows matter most.
- F7 · P2 · 80: no llama-swap group or `/v1/models` row, no context-size row (writer ctx; Forge 64K), no output-path rows (prompts_writer, done/errored/skipped/held, panels.csv/clips.csv, render out), and no `/object_info` row.
- F8 · P2 · 75: there's no panel text encoder or VAE row, although the clip TE and VAEs are in preflight. Judge model identity: 8.1 has "apply=false" only, with no model or endpoint (advisory, so low risk).
- F9 · P3 · 90: there's no explicit `frames%17==5` assert. 107%17=5 holds, so the value is right; add the row. fps: there's no row for base fps or playback fps outside RIFE. 7.2 correctly leaves "RIFE 20" (42.6 fps vs Derrick's 10/10 "RIFE back up to 24 fps") open as **ALI-39 for Derrick**.
- F10 · P3 · 70: the audit doesn't explain how the 768x1344 panel becomes the 768x1120 clip canvas (crop or resize). Add a row.
- F11 · P3 · 80: §1 says "42/48 beats are nude", but only **40** beats' `s1` contain "fully nude". The 42 includes "nude-beige" fabric (`specs/beats_poolb07.json`).

### Item 3: writer.py.proposed-1237 (not applied; live AlienPc `writer.py` LastWriteTime **10:17:08**, 11915 B, sha `64EB9415F59A`, same as the box mirror)
| check | verdict | evidence |
|---|---|---|
| (a) invented Picture/`<Audio 1>` | PASS (static) | RULES adds "the ONLY asset is <Picture 1> … never write <Audio 1>". The new `panel_refs()` rejects image N≥2, image-1 pose refs and clip syntax. Run on today's 48 panel prompts it flags **29/48** (audit: 27). |
| (b) bikini on nude beats | PASS (static) | `panel_sys` uses `ward=b.get("s1")` plus "She is fully nude: no bikini…", and `panel_refs` adds a nude-beat attire check. `still_text()` strips the clip anchor: 18 beats whose `start` is only "Both adults begin in the exact pose of <Picture 1>." fall back to `pic` with Subject names mapped. |
| (c) strip_audio gutting (W2B08/W2B12 null) | **FAIL** | see F12 |
| (d) greedy no-op retry | PASS (static, untested) | `greedy=(att==0)`. It isn't verified that the node's sampling honours `seed` when greedy=False. |
| (e) raw attempts saved | PASS | `open(out[:-4]+".attempt%d.raw.txt"…).write(raw or "")` |
| drop HADM | PASS | No HADM in writer, loop or pipeline. The preflight `HADM anatomy detector` row passes, and DECISIONS has the 12:32 row. The 11:51 HADM row still reads "applying" (P3: mark it superseded). |
- **F12 · P1 · 85: the clause-level regex still guts the act line.** The new line is `t=re.sub(r"(?i)[,;]?[^,;.\n]*<\s*Audio\s*\d+\s*>[^,;.\n]*","",t)`. `[^,;.]` stops at the "." inside the H3 timestamp `00:00.000`. I tested it on a synthetic `[Shot 1] At 00:00.000 <Subject 2> moans (voice <Audio 1>) while riding <Subject 3>.` and got `[Shot 1] At 00:00.` back: the act is gone. `sections_ok()` passes it, because it only checks that the text contains "[shot 1]" and that summary is non-empty. Fix: strip only the `<Audio N>` token plus an adjacent "voice/audio of/as in" phrase. Make `sections_ok` require the `[Shot 1]` line to have more than N words after its timestamp, and diff action-word counts before and after the strip.
- F13 · P2 · 70: a regression risk that's accepted. E10's `PANEL_SYS` is no longer byte-identical: PANEL_RULES replaces RULES, against the 10:27 comment "E10 beats … keep PANEL_SYS byte-identical". That's fine while E10 stays dropped (9:54 "No drop e10 do the others"), but note it in the diff.
- F14 · P3 · 75: there's a wrong time in the code. The `strip_audio` comment says "10:27 CT", but the same code was already in the box mirror at 10:15:03 and on AlienPc at 10:17:08, and writebeat jobs ran it from 10:18:25. The audit §6 repeats "(10:27)".
- Not tested at runtime: no prompt was rewritten with the proposal (correct, per the 12:32 brief). An acceptance run is needed before production. See the gate below.

### Item 4: skill draft (/workspace/cos/drafts/forge-preflight-config-check.SKILL.md, 12:42:25)
- PASS on these:
  - frontmatter is valid (name, description; `status:` is an extra key)
  - 67 lines, about 970 words, about 1.7K tokens
  - local-only, with no box or web dependency apart from the Fleet Reviewer handoff
  - clear rule, run, table, prompt scan, stop and canary sections
  - quotes Derrick 12:23 verbatim
- F15 · P2 · 85: **no community-first rule.** `research-core/SKILL.md:19` says "Reuse an existing tool or skill before building one", and `solutions/2026-10-16-overengineering…:26` says "Community first … Write custom code only for gaps". Add a line: prefer stock checks such as ComfyUI `/object_info`, node defaults from the upstream README, llama-swap `/v1/models`, and send any new assert through review.
- F16 · P2 · 80: context budget. `| Tee-Object` prints the whole report (about 32 KB, roughly 8–10K tokens; the saved outputs are 31.4–32.0 KB) into Forge's 64K context. Tee to the file, and print only `^(SUMMARY|FAIL|WARN)`.
- F17 · P2 · 80: lessons missing from the skill:
  - the worker ignores STOP while jobs are queued, and running\ jobs auto-RESUME (F1)
  - a not-run canary must not count as PASS (F3)
  - unwired config is a FAIL for handoff (F2)
  - "a prompt-generator change needs a sample read of its outputs (≥4 beats per character, including nude and aftercare) and a review receipt before release" (the CE gate below)
  - the regex trap with timestamp periods (F12)
- F18 · P3 · 60: the "Fixes: … make one reversible edit" step reads as an executor task. Per Derrick 12:25, "you are oversite. Not execute", so say which agent does it.

### Item 5: CE-loop audit of Max (POOL/B07)
Timeline (AlienPc status.log and file mtimes, CT):
- 09:36 writer promoted. `writer_winner.json` says: "Caveat: its prompt invented <Audio 1>/audio reference - not in assets." It was promoted on the E10 W2 arm only.
- 09:54 DECISIONS row: "No drop e10 do the others".
- 10:15–10:17 code deployed (writer, loop and pipeline at 10:17:08).
- 10:17:48 worker start, 10:17:49 canary ok.
- 10:18:25–10:55:08: 48 writebeat jobs. 5 errored, each with an ESCALATE file (10:26 P1B11, 10:28 P2B02, 10:29 W2B02, 10:33 W2B08, 10:55 W2B12).
- **10:55:08 `JOB start 101_panel_P1B01_r1.json`**, the same second the last escalation landed.
- 6 panel jobs ran until **12:22:38 "STOP controller+worker stopped by Max Architect (Derrick 12:22 'stop the queue and get it right')"**.

| CE step | Done? | Evidence |
|---|---|---|
| Plan | Partial | There was a decision row (9:54) but no written acceptance criteria for using the writer on new characters or nude beats. Promotion rested on 3 E10 clips of one beat with a known defect. |
| Work | Yes | per-character `panel_sys`/`briefs`, the strip_audio patch, the writebeat queue |
| **Review** | **Skipped** | No prompt file was read before release. There was no ce-code-review receipt for the writer diff, and 5 escalations were left open while panels released. ce-work says: "Code review must actually happen before shipping … Never substitute a mental self-review". |
| Fix | Only after Derrick | 12:22 stop, then the audit and fixes |
| Lessons | Stated, not yet encoded | Max [16]: "The misses happened because I skipped a check…" The skill draft encodes some of it. |
What Max should have caught before release (each is visible in files he owned):
- writer bugs: 27/48 bad panels, 25/48 bad clips, 5 null clip prompts
- the line-delete `strip_audio`
- the stale E10 `face_source` text (fixed 12:38)
- `guards[].where` = `run_scene.py`, which doesn't exist (`pipeline_poolb07.json:121-166`); his own 12:22 executor brief also listed "run_scene.py (controller)"
- the config not read by the worker
- no STOP file and STOP semantics: the 12:22 stop killed processes but left 106 in running\ to auto-RESUME
Repeats after delivery (each item gives my source and delivery time, then what Max did):
- **R1 · P1 · 85: acceptance test.** Full-setup fix 4 (delivered 08:08): "Writer stage in pipeline.py, plus an acceptance test against the hand-written baseline (4 beats, same seeds)". The writer stage shipped (approved 8:09). POOL/B07 has 0 hand-written prompts (audit 5.1), so no acceptance or output check happened before 48 beats went to production.
- **R2 · P2 · 80: review gate.** Full-setup fix 11 (08:08): "Review gate for new evaluators and edge-case tests before they run as loop jobs". The new writer path ran straight as loop jobs.
- R3 · P2 · 75: evidence before claims. In conduct-audit-2's pre-send checklist (08:54), item 1 reads "Every 'done/running/tested/picked/fixed' names a file and its real … row count". The 10:27 strip_audio "fix" was never checked against outputs (audit §6 row 137), and the comment time is wrong (F14).
- R4 · P3 · 60: the stop check used `http://127.0.0.1:8189/queue` ("comfy unreachable"). ComfyUI is on :10002. The conclusion (processes dead) was still right.
- Not repeated: the health check and canary held, with the 10:17:49 canary ok.
- Coverage limit: there are no transcript pages for 09:30–12:20 on the box, only the 12:43 page, so I can't confirm Max's messages to Derrick from 10:55 to 12:20.
- F19 · P2 · 60: there's no DECISIONS row for the 09:36 writer promotion. Full-setup fix 4 marked the writer choice "Needs Derrick: Yes". The approval may have come in chat, but I can't see it.

**Gate to add (proposal; Derrick or Max to approve).** Before any queue release or worker start, all of these must hold:
1. Archive or hold queue\ and running\ jobs whose prompts predate the current writer or prompt sha.
2. `preflight_check.py` exits 0. Its report must be newer than every code, config and prompt mtime, with F1–F3 fixed so STOP, canary and wiring can't pass falsely.
3. There's a ce-code-review receipt, or an explicit skip state, for every diff to writer.py, loop.py, pipeline.py or drv.py.
4. For any new or changed prompt generator, a reviewer reads ≥4 outputs per character, covering a nude beat, a partnered beat and a solo or aftercare beat. Use Derrick's gate keys once he decides them.
5. 0 open ESCALATE files for queued beats.
6. Fleet Reviewer signs off.
pipeline.py should refuse release (exit 3) unless `preflight_<hhmm>.txt` passes and `REVIEW_OK.json` carries the writer and loop shas.

## Fixes required before Forge runs
1. **P0:** move all 44 queued jobs and running\106 to a held dir. The STOP file alone doesn't protect a worker start (F1). 27/44 carry frozen bad prompts. This is reversible, but someone has to approve it.
2. **P1:** loop.py checks STOP at the top of `main()` and the loop, before canary or RESUME. This is a code change and needs approval.
3. **P1:** fix the F12 regex and harden `sections_ok`. Then apply writer.py with a backup, rewrite all 48 beats with `--force`, and re-run preflight until the output rows have 0 FAILs. Do the sample read per the gate.
4. **P1:** wire the config or assert it (F2). Either loop.py reads pipeline_poolb07.json, or preflight asserts every config key against the loop.py built-ins, and the wiring row becomes FAIL when they don't match.
5. **P2:** add the missing rows (F6–F10): writer model, params and system sha; /object_info; llama-swap /v1/models and group; context; output paths; panel TE/VAE; frames%17; fps.
6. **P2:** point `guards[].where` at real `pipeline.py` functions, make the canary row NOT-RUN instead of PASS, and fix the "42/48 nude" count and the 10:27 time.
7. **P2:** skill fixes F15–F17.
8. **Derrick decides:** the aftercare-beat gate keys and RIFE 20 (ALI-39). Not decided here.

## Note for the parent (untrusted-content check)
Nothing in the fenced tool output asked for an action.
