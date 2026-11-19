# ALI-173 BAKEOFF - B2 CONTINUUM SCENE findings (2026-10-23, loop 07)

Builder `C:/AI/community/notes/ali173_b2_cont_build.py` - graph `C:/AI/community/runs/ali173_cont_hc1_s51140001/request.api.json` (17 nodes).
Pre-submit gate `C:/AI/community/notes/ali173_b2_req_check.py` - schema gate `C:/AI/community/notes/ali173_b2_static_offline.py`.
GPU window: `notes/bakeoff_gpu_ledger.md`.

## 1. The live schema, and the six classes that do not exist here

`GET http://127.0.0.1:10004/object_info` on 2026-10-23 18:12 CT = 2605 classes, full dump
`notes/ali173_b2_object_info_full.json` + per-class dumps `notes/ali173_b2_obj_<Class>.json`.
This is the ComfyUI-H3-Continuum **3.10.2** install (`__init__.py __version__ = "3.10.2"`); README =
"MiniMax H3 Continuum V3.10 - native 10-second generation, 720p54, audio".

Requested classes that are **not installed**: `H3ContinuumAssembleSeamV34`, `H3ContinuumJoin`,
`H3ContinuumFinish`, `H3ContinuumAssemble`, `H3ContinuumSaveState`, `H3ContinuumLoadState`,
`MarkdownNote`, `Fast Groups Muter (rgthree)`. V3.10.2's seam node is
**`H3ContinuumAssembleSeamV35`** (that is what the graph uses); state save/load and the
markdown/group nodes simply are not in this build, so no B2 graph may reference them - an unknown
`class_type` is `rc 2` in the harness (`run_graph_job.py:173`).

## 2. The Continuum V39 widget order, read from the official example

`examples/workflows/MiniMax_H3_Continuum_V39.json` = 32 nodes / 39 links. Mapped by position against
the live schema (`notes/ali173_b2_read_example.py`) - 29 of 32 nodes map cleanly; the mismatches are
the ones that matter:

- `H3ContinuumReferenceImagesV39`: example carries 11 `widgets_values`, schema has 10 inputs
  (`reference_image_1..9` + `reference_keep_in_window`). The extra value is a UI-only leftover:
  **wire the reference images as links, not widgets**, which is what the graph does.
- `H3EasyLoadImage`: example carries 2 values, schema has 1 (`image`) - **`image` is a STRING path
  relative to the ComfyUI `input/` directory** (`nodes_load_image.py:101 INPUT_TYPES`, `:243
  class LoadImage`), not a `File` widget.
- `SpectrumApplyMiniMaxH3` is **absent from `object_info`** (it belongs to the old ComfyUI-Model-Debug-
  Suite / 0.17.2 world), so it cannot be used.

## 3. Continuum frame and size math (from the extension source)

- `constants.py:16-18` `FPS = 24.0`, `AUDIO_SAMPLE_RATE = 32_000`, `AUDIO_LATENT_FPS = 40.0`;
  `CHUNK_SECONDS_DEFAULT = 5.0` (`constants.py:150`).
- `v3/hardening.py:86-89` requires `target_frames == len(chunks) * chunk_seconds * fps` exactly, so
  2 x 5.0 s x 24 = **240 frames** is the only legal assembly target for this shape.
- `v3/resolution.py:28 H3_CANVAS_MULTIPLE = 32`; `_manual_dimension` (100-106) raises unless the
  Manual width/height is an int, a multiple of 32, and 32..16384. **`832x468` is unreachable**
  (468 % 32 = 20), so the 16:9 arm is `1024x576` (0.589 MP, inside the README's "Balanced 0.60 MP for
  final renders" band, aspect 1.778 inside the 1.70-1.85 gate). Presets are Draft 0.30 MP /
  Balanced 0.60 MP / Native 768 / Custom; the graph uses Manual 1024x576 so the size is exact.
- Continuity presets: `Fast - 5 frames`, `Balanced - 22 frames`, `Strong - 39 frames`
  (`constants.py:108-110`); the graph uses Balanced.

## 4. The ComfyUI 0.19.2 update broke the frozen r3b sparse-attention block (bakeoff consequence)

The bakeoff updated ComfyUI to **0.19.2** (`notes/ali173_b2_object_info_full.json`, `system_stats`).
Against the live schema:

- `ModelAttentionBackend` (node 10 of the frozen r3b graph) now offers
  `attention=["pytorch attention", "comfy kitchen attention"]`; **`sparse_blocks`, `sparse_size` and
  `max_dims` are gone** - those keys were valid on 0.17.2, so r3b's nodes 10/11 are **schema-STALE**:
  the harness `static_check` (rc 2) rejects them today.
- `BlockSparseAttention`'s `selection` is `COMFY_DYNAMICCOMBO_V3`
  (`method_defs = {sol-attn: [tau], sla/vsa: [keep_percent]}`, `comfy/quant_ops/block_sparse_attention.py:826,842`).
  The method-specific inputs are **nested**: a top-level `tau` key = "not an input" = rc 2. Proven by
  probes in `ali173_b2_cont_build.py`.

The B2 graph therefore wires `UNETLoader -> MiniMaxH3SigmaShift` directly (no sparse nodes) and records
the loss as a delta. **HB1-HB4 must re-verify r3b's nodes 10/11 before submitting any clone.**

## 5. Negative prompt: this arm has no place to put one

`H3ContinuumSamplerV39` (required `model, clip, video_vae, sampler, sigmas, sequence_prompt` + the
run/size widgets; optional first/last frame, refs, driving audio, `audio_vae`) has **no negative, no
CFG, no CFGGuider** - the README says the model is guidance-free. `CFGGuider` + `NAGuidance` exist in
`object_info` and carry the negative (per the AGENTS.md H3 note), and the r3b arm uses them; the
Continuum arm cannot, so the HC1 negative block is appended to `sequence_prompt` as a `no:` prose line
(the extension's own rule, `constants.py:409-414 CONTINUITY_RULES_TEXT`). The delta is asymmetric by
design and recorded here, not fixed by a kludge.

## 6. Gates, with their self-destructs

- **Builder gate** (`ali173_b2_cont_build.py`, rc 0): 0 problems on the real graph; 10/10 probes fired
  - drop the ref node, `chunk_seconds 5.5`, `height 468`, a `negative_prompt` key on the Continuum
  sampler, r3b's old sparse-attention keys, the dynamic-combo sub-key `tau`, an unknown class, seed
  1234, a save prefix outside `community/ali173_cont_hc1_s51140001/`, and a bad link slot.
- **Harness schema gate, offline** (`ali173_b2_static_offline.py`): serves the captured live schema in
  place of `:10004` (a stub that answered every URL would make the gate pass anything, so every
  non-`/object_info` URL raises) and runs the **real** `run_graph_job.static_check`. Real graph = OK;
  probes: bad key / missing required / unknown class / dangling link all **REJECTED**;
  `chunk_seconds 5.5` **PASSED** - the harness gate is blind to Continuum's frame math, which is why
  the builder gate owns it. Verdict line names that blind spot.
- **Pre-submit gate** (`ali173_b2_req_check.py`): parses the id gates out of `ralph.ps1` (line 202
  allow-gate accepts `ali173_cont_hc1_s51140001`; the two deny lists do not hit it), the request shape
  (`kind=graph`, `frames 240`, `frames_tol 33`, `minutes 60` -> per-attempt timeout 1200 s with
  `--max-redo 2`, the shape proven by `p7/jobs/request_iter09.skipped.json`), the arm preconditions
  (graph present, `runs/<id>/<id>.mp4` absent, `p7/jobs/<id>.result.json` absent), the budget vs the
  `param()` caps (467.5 < 615 min, 37 < 45 jobs), and `TASKS.md` naming + ticking the id
  (`ReqTicked`, ralph.ps1:307). The caps must be read from the `param(` line: a loose
  `GpuCapMin[^=]*=` search runs past the line into prose and captured 375 on the first run; the tick
  check is per-line, and both are probed.

## 7. Render state and graph durability

The job is **requested, not rendered**: `C:/AI/community/p7/JOB_REQUEST.json` staged at ~18:35 CT
(`kind=graph`, `frames 240`, `frames_tol 33`, `minutes 60`), `p7/jobs/ali173_cont_hc1_s51140001.result.json`
does not exist. Proof (objective.json, ffprobe, labelled contact sheet) and the ledger's render line are
due next pass. No vision judgement is made here - KEEP is Derrick's.

Durability: `C:/AI/community/runs/` is gitignored, so the graph the job reads is not in any commit, and
`ralph.ps1` has no `git clean` (grep = 0 hits) - it survives iterations but nothing restores it. The
durable copy is **`notes/ali173_b2_graph_ali173_cont_hc1_s51140001.json`** (committed, sha256
`1efecedd53549c5e05887985f352a18d5897ca8587588af39b67052bfabd2088`, the value written to
`runs/bakeoff_gpu_events.jsonl`), and `python C:/AI/community/notes/ali173_b2_restore_graph.py` re-copies
it into `runs/<id>/request.api.json` (it refuses, rc 2, if the live file differs semantically, so it can
never overwrite a graph a running job is reading; `--selftest` = 4/4 probes fired).
