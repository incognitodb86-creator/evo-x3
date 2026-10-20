# SETTINGS_CHECK.md - C2 TenStrip settings check (ALI-52, D10 + evidence)

Run: 2026-10-20, Ralph community-switch loop, one-task iteration C2. No GPU job, no render, no download, no install.

Required values (Derrick 2026-10-20 10:30 AM CT, TenStrip):
- shift: video 10 / audio 3
- steps: 10 for finals, 8 for drafts
- sampler euler + scheduler simple (never res_multistep / karras as a default)
- attention: VSA (BlockSparseAttention selection "vsa"), never SLA
- never Eros_beta6mix_Lora stacked on the beta6 checkpoint

## Files searched
- C:\AI\community\scripts\*.py (11 live scripts + their .bak-20261020-* backups)
- C:\AI\community\shots\*.json (p5_3shot.json, p6_pairs.json, p6_1min_community.json, p6_1min_beats.json)
- C:\AI\community\p3\*.json (Community_H3_I2V_beta6.app.json)
- pipeline_defaults.json - REAL PATH: C:\Users\derek\5slock\loop1017\pipeline_defaults.json
  (the path in the task line, C:\Users\derek\5slock\runs\loop1017\pipeline_defaults.json, does not exist; only one copy of the file exists under 5slock)
- grep patterns: shift / steps / sampler / scheduler / attention / VSA / SLA (\b word-bounded) / beta6mix / res_multistep / karras / Eros

## Result: no leftover to fix
Every live file in the four named sets already carries the required values. The earlier fix pass (C:\AI\community\scripts\settings_fix.py, logged in C:\AI\community\settings_fix.log lines 2-12) already applied them; this pass re-verified them value by value. **Zero edits, so no .bak-20261020-ralph was needed for any in-scope file.** (Only TASKS.md was ticked - see the backup note at the end.)

## Every hit, with file:line and the value it has now

### C:\AI\community\scripts\comm.py (the graph builder all community renders use)
| line | setting | value now | verdict |
|---|---|---|---|
| 7 | UNET | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors | ok (beta6 base - so beta6mix must never stack) |
| 68 | LoRA guard | `if "beta6mix" in name.lower(): raise ValueError("never stack Eros_beta6mix_Lora on beta6")` | ok, hard block |
| 72 | ModelAttentionBackend | attention "comfy kitchen attention" | ok |
| 73-75 | BlockSparseAttention | selection "vsa", keep_percent 10, start_percent 0.2, end_percent 1.0, min_tokens 12288, extra_tokens 256 | ok - VSA, no SLA anywhere |
| 77 | MiniMaxH3SigmaShift | shift_video 10.0, shift_audio 3.0 | ok |
| 84 | KSamplerSelect | sampler_name "euler" | ok |
| 87 | BasicScheduler | scheduler "simple", steps passed in by caller, denoise 1.0 | ok |
| 110-111 | build() | steps is a parameter (no hidden default), vsa=True default | ok |

### C:\AI\community\scripts\batch_queue.py
| line | setting | value now | verdict |
|---|---|---|---|
| 22 | steps | `sh.get("steps", 10)` - default 10 = finals | ok |

### C:\AI\community\scripts\p3_appmode.py (generator for the App Mode json)
| line | setting | value now | verdict |
|---|---|---|---|
| 43 | BasicScheduler widgets | ["simple", 10, 1] | ok |
| 44 | MiniMaxH3SigmaShift widgets | [10, 3] | ok |
| 45-46 | attention | ["comfy kitchen attention"] + BlockSparseAttention[0] = "vsa" | ok |
| 61-65 | named inputs | euler / simple+10 / shift 10+3 / vsa keep 10 start 0.2 / comfy kitchen attention | ok |
| 70-75, 79 | self-checks | asserts each of the six values in both widgets_values and widgets_values_named, incl. steps == 10 | ok |
| 82 | LoRA guard | `assert "beta6mix" not in json.dumps(j).lower()` | ok |
| 85 | attention guard | `assert all(s == "vsa" ...)` "VSA required, not SLA" | ok |
| 91-96 | community_note | states 10 steps (8 drafts), shift 10/3, VSA keep 10 start 0.2, never beta6mix | ok |

### C:\AI\community\scripts\p2.py / p4.py / t27b.py (already-run probes, values left exactly as run)
| line | setting | value now | verdict |
|---|---|---|---|
| p2.py:6,11 | canary | 416x736, 29 frames, 8 steps | smoke test, not a final or a draft deliverable - left as run (P2 evidence) |
| p2.py:17-18 | P2 clip | 768x1344, 124 frames, steps 10, euler/simple, shift 10/3, VSA | ok final |
| p4.py:6 | D3 draft arm | 576x1024 (0.59 MP), STEPS = 8 | ok - 8 steps is the draft rule; p4.py:33 meta records shift 10/3 euler/simple vsa |
| t27b.py:62 | 27B timing probe | 416x736, 29 frames, 8 steps | timing probe only, not a deliverable - left as run |

### C:\AI\community\scripts\p6.py, prompt_writer.py, sy_1min.py, sy_graph.py, settings_fix.py
- p6.py: no sampling values of its own; it calls batch_queue with the shot lists - ok.
- prompt_writer.py: prompt word ranges only, no sampling values - ok.
- sy_1min.py: no sampling values; it shells out to sy_graph.py - ok.
- sy_graph.py:12-16: steps / shift / sampler / audio_shift come from the live Switchyard config (`_resolve_render_plan`), nothing hardcoded, read-only import of Switchyard - ok. Its values are the ones settings_fix.py:32 set in director.live.yaml line 176 (video.steps 8 -> 10, settings_fix.log line 12). director.live.yaml itself is not in C2's file list and could not be re-read this pass (tool policy blocks reading outside the working dir except C:\AI\community); evidence is the settings_fix.log line.
- settings_fix.py:12-26, 32, 35-39: the fixer itself (targets the four ComfyUI\user workflow jsons + director.live.yaml + pipeline_defaults.json). Not re-run here - Ralph must not edit ComfyUI\user or any live workflow.

### C:\AI\community\scripts\p1_freeze.ps1 (not a .py, listed for completeness)
- line 30: frozen model list = 10Eros beta6 int8 UNET, qwen3vl_32b H3 TE, H3 video/audio VAEs, MysticXXX, HMNSFW-AIO-V2.5, mis_doggy, h3_antiburn. No Eros_beta6mix_Lora in the list - ok, untouched.

### C:\AI\community\shots\p5_3shot.json
- lines 13, 26, 39: `"steps": 8` with lines 11-12/24-25/37-38 `"w": 576, "h": 1024` (0.59 MP) -> these are the D3 draft shots. ok (8 = draft rule).

### C:\AI\community\shots\p6_pairs.json
- lines 13, 26, 39, 52, 65, 78, 91, 104, 117, 130, 143, 156: `"steps": 10`, each with `"w": 768, "h": 1344` -> all 12 finals ok.
- no `loras` key in any shot -> nothing stacked on beta6. no shift/sampler/scheduler/attention key -> inherits comm.py (10/3, euler/simple, VSA). ok.

### C:\AI\community\shots\p6_1min_community.json
- lines 17, 35, 53: `"steps": 10` with 768x1344 -> finals ok; `"antiburn": null` (no LoRA stack).

### C:\AI\community\shots\p6_1min_beats.json
- no sampling keys at all - ok.

### C:\AI\community\p3\Community_H3_I2V_beta6.app.json (the App Mode form)
| line | setting | value now | verdict |
|---|---|---|---|
| 134, 146, 1040, 1044 | UNETLoader x2 | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors | ok, both loaders are beta6 |
| 825 / 828 | KSamplerSelect | widgets ["euler"] / sampler_name "euler" | ok |
| 869-871 / 874-876 | BasicScheduler | widgets ["simple", 10, 1] / scheduler "simple", steps 10, denoise 1 | ok (finals) |
| 1477-1479 / 1488-1491 | BlockSparseAttention | widgets ["vsa", 10, 0.2, 1, ...] / selection "vsa", keep_percent 10, start_percent 0.2, end_percent 1 | ok - VSA, no SLA |
| 1544 / 1547 | ModelAttentionBackend | "comfy kitchen attention" | ok |
| 1586-1587 / 1590-1591 | MiniMaxH3SigmaShift | widgets [10, 3] / shift_video 10, shift_audio 3 | ok |
| - | LoraLoaderModelOnly | no such node in the file | ok - nothing stacked on beta6 |
| 1977 | community_note | states the full recipe incl. "8 for drafts" and "Never stack Eros_beta6mix_Lora on beta6" | ok |
| 214, 217 | stock template description text | still says "FastVideo FastH3 8-Step V2 ... 8 sampling steps" | prose only, not a setting - NOT changed; flagged for C7 Runbook (the community_note at 1977 states the real model/settings) |
| 341 | "resolution_steps": 32 | size-widget rounding step, not sampling steps | not a setting, left alone |

### C:\Users\derek\5slock\loop1017\pipeline_defaults.json (clip block = the video recipe)
| line | setting | value now | verdict |
|---|---|---|---|
| 93 | clip.model | 10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors | ok |
| 94 | clip.steps | 10 | ok (finals; drafts are set per shot at 8) |
| 95 | clip.sampler | euler | ok |
| 96 | clip.shift | 10 | ok |
| 109 | clip.audio_shift | 3 | ok |
| 110 | clip.scheduler | simple | ok |
| 111 | clip.settings_fix note | states 10 steps (8 drafts), shift 10/3, euler/simple, VSA keep 10 start 0.2, never beta6mix | ok |
| 43 | panel.steps 4 | FLUX-Klein panel still tool | not video sampling; panel is enabled=false (line 20-22) - unchanged |
| 58 | panel.bfs.sampler lcm | panel face-fix tool | not video sampling; bfs enabled=false (line 55-57) - unchanged |
| 118 | "steps8" inside an evidence string | text | not a setting |
| 121-123 | candidate `would_set clip.options.sampler = res_multistep` | `"apply": false` | not applied, sampler stays euler - ok |
| - | clip block has NO attention key | VSA is enforced in comm.py:73-75 and the app json; loop1017 clip graphs are built by Switchyard's own builder | nothing to fix in this file; noted for C3 (which edits this file) and C7 |

## Backups
- No in-scope file was edited, so no `<name>.bak-20261020-ralph` was created for any of them (backups are for edits).
- TASKS.md (ticked per the loop rules): the existing TASKS.md.bak-20261020-ralph from the C1 pass was left untouched so the original snapshot survives; the pre-C2 state was saved as TASKS.md.bak-20261020-ralph-c2.

## Check evidence (C2 check = file exists + py_compile passes + JSON parses)
- py_compile: `python -m py_compile C:/AI/community/scripts/comm.py batch_queue.py prompt_writer.py p6.py p3_appmode.py settings_fix.py sy_1min.py sy_graph.py p2.py p4.py t27b.py` (forward-slash paths) -> exit 0, no output. All 11 live scripts compile.
- JSON parse: `python -m json.tool --compact <file> 1>NUL` -> exit 0, no error for all six: shots/p5_3shot.json, shots/p6_pairs.json, shots/p6_1min_community.json, shots/p6_1min_beats.json, p3/Community_H3_I2V_beta6.app.json, loop1017/pipeline_defaults.json.
- SLA / beta6mix sweep: the only matches for `SLA` (word-bounded) and `beta6mix` in the whole scope are the guards and asserts that forbid them (comm.py:68, p3_appmode.py:82, 85, settings_fix.py:14-15, the app json community_note). No live setting uses SLA or stacks beta6mix.
