# ALI-147 FIX4_PROOF - blocked: UI-only (card C4) - diagnostics (Forge, 2026-10-22, read-only, CPU only)

No PROOF.md and no fairness.txt: `p7\jobs\ali147_pool_fix4_s51080000.result.json` is
`ok=false` `rc=5` note `run_graph_job rc=5 (objective failure after 2 redos: STUCK, flagged for Derrick)`
(started 2026-10-22T17:35:59, finished 17:37:07, wall_min 1.1, budget_used_min 243.6).
`runs\ali147_pool_fix4_s51080000\` holds NO mp4 and NO contact sheet - the file list is
`request.api.json` (41,906 B, 17:34), the three submitted copies
`ali147_pool_fix4_s51080000.api.json` / `_redo1.api.json` / `_redo2.api.json` (41,904 B each, 17:36-17:37),
`status.log`, `objective.json`. `objective.json` = `"attempts": []` and three `fails` entries,
each `"why": ["JOB error"]` (tag, `_redo1`, `_redo2`). Nothing was rendered, so every PROOF.md field
(frames / duration / bytes / audio / render secs / contact sheet / seam frames) would be invented.

## The three attempts (status.log, quoted)
- `2026-10-22 17:35:59 CT UNLOAD LLM coding_swift15_iq3s_esp`
- `2026-10-22 17:36:51 CT JOB start ali147_pool_fix4_s51080000 prompt_id=256f4f0f-ac8c-4dae-a2c6-bc10b9b59dce`
- `2026-10-22 17:36:56 CT JOB error ali147_pool_fix4_s51080000 secs=5.1` node_id `ext` node_type `MiniMaxH3Extender`,
  `executed: ["vvae","m_vsa","ppack","avae","m_attn","clip","rpack","m_shift","unet","img"]`,
  `exception_type: RuntimeError`, message quoted below
- `17:36:56 CT OBJECTIVE FAIL ... JOB error` / `REDO 1/2 ... (objective failure; same seed)`
- `17:36:56 CT JOB start ..._redo1 prompt_id=b9765954-...` -> `17:37:01 CT JOB error ..._redo1 secs=5.1` with `executed: []`
- `17:37:01 CT REDO 2/2 ... (objective failure; seed+1)` -> `17:37:02 CT JOB start ..._redo2 prompt_id=202ae497-...` -> `17:37:07 CT JOB error ..._redo2 secs=5.1` `executed: []`
- `2026-10-22 17:37:07 CT STUCK ali147_pool_fix4_s51080000 objective failure after 2 redos - flagged for Derrick`
- `2026-10-22 17:37:07 CT UNLOAD comfyui_auto (POST /api/models/unload)`

Same text in all three, verbatim:

```
MiniMax H3 Extender: Ref2VA clip 1 is marked Validated but its disk cache is missing. Refusing to
rerender a validated clip. Uncheck Validated explicitly if you want this clip rendered again.
```

GPU cost of the STUCK arm: 3 x 5.1 s of node execution (16 s end to end); the model chain and both
bridges DID run in attempt 1, so the harness `object_info` static check and ComfyUI validation passed.
This is not a headless graph-format rejection and no node_errors.

## Root cause (deterministic, reproduced by a read-only probe, not a transient)
`C:\AI\community\notes\ali147_fix4_refsheet_probe.py` (run this iteration, read-only) prints, from
`request.api.json`: the Extender node id is `ext`; `clips_json` is a 6-clip payload whose clip objects
carry the keys `['color_adjustment','duration','first_frame','first_source','guides','id','last_frame',
'local_refs','loras','name','prompt','seed','seed_mode','validated']` and **`"validated": true` on all 6
clips** (`'validated'` substring count 6). That key came from the FIX4_GRAPH schema/example copy
(`specs\extender_object_info.json` / the shipped `Workflow\MiniMax_Extender.json` clip cards).

In the Extender, `validated` is the clip-card **Validated checkbox** - a UI-side property of the clip card,
serialised into `clips_json` on export - and its rule is a hard invariant, quoted from
`ComfyUI_MiniMax_H3_Extender\extender.py`:

- lines 6104-6107: `# Never silently turn a user-validated clip back into an active clip.` /
  `# The loop below enforces the hard invariant: Validated=True can only be reused from disk; if its`
  `# cache is missing we stop with an explicit error instead of falling through to the sampler.`
- lines 6317-6323 (`full_batch`, Ref2VA): `if bool(cfg.get("validated", False)):` /
  `if not existing or current_desc is None: raise RuntimeError(... Ref2VA clip {i+1} is marked Validated ...)`

The on-disk cache for this node id is empty because it is a new project. `cache\chain_extender_ext.json`
(the namespace is derived from the node id: `chain_extender_<id>` -> `chain_extender_ext`,
`owner_id "extender_ext"`, `build "motion-context-disk-v3.0.13"`) is 882 bytes, created_at 1792708613.43
= **2026-10-22 17:36:53 -0500 CT** (inside attempt 1) and updated_at 1792708622.14 = 17:37:02 CT (redo 2),
with `"segments": []`, `"final_frame_count": 0`, `"geometry": null`; `chain_extender_ext.h3cache` is 11 bytes
and `chain_extender_ext.audio.h3cache` 10 bytes. So clip 1 is marked Validated with zero cached segments,
the invariant fires, and every attempt fails in 5.1 s. The sibling namespaces `chain_extender_1` /
`chain_extender_8` (Oct 15 / Oct 17, with real `.h3cache` + `*.final.video\ref2va_*.mp4`) are the UI-built
example projects - the state a Validated card normally points at.

So the card C4 condition is met as written in the plan: the Extender is UI-driven and its per-clip
Validated state is what stops the headless run. Per the plan and PROMPT.md I drove no UI, and the
harness redos (2, objective "JOB error") are exhausted -> STUCK, flagged for Derrick.

## What would fix it, for Derrick's decision (Forge made no graph edit this iteration)
Option A (no UI, graph-file only, ~1 flag per clip): set `"validated": false` on all 6 clips inside
`C:\AI\community\runs\ali147_pool_fix4_s51080000\request.api.json` - the exact equivalent of the error's
own instruction "Uncheck Validated explicitly if you want this clip rendered again", and
`request.api.json` is in Forge's writable list. Then apply the failed-job rule (move
`p7\jobs\ali147_pool_fix4_s51080000.result.json` / `.out` / `.err.out` and the run outputs to
`*.failed-20261022` / `runs\ali147_pool_fix4_s51080000\failed-20261022\`, move never delete) and
re-request the identical graph job `{"jobs":[{"id":"ali147_pool_fix4_s51080000","kind":"graph",
"frames":1443,"frames_tol":24,"minutes":180}]}`. A graph edit + re-request is a FIX4_GRAPH/FIX4_REQ
action, not a FIX4_PROOF action, so it needs a task line or Derrick's go-ahead.
Option B (card C4 as written): Derrick builds/validates the 6 clip cards in the UI himself; Forge drives no UI.
If Option A is approved, the clip lengths still need the grid-aligned values (the 5+17k grid finding and
the 243 + 5x260 = 1543 raw -> 1433 after five 22-frame Motion Context seams fallback are in
`C:\AI\community\notes\ali147-fix4-graph-20261022.md`); the as-built durations 10.125 / 9.916667 s are
expected to land near 1348 frames, outside `frames_tol` 24 of 1443.
A third possibility to name for what it is: if a full_batch run REQUIRES at least one Validated card plus a
real cache, then the Extender cannot be driven headless from a cold project at all, and FIX4 is card C4 -
Derrick's pick (build the cards, or drop fix 4).

METHOD_ONLY. No quality judgment here; the run produced no frames. KEEP is Derrick's only.
