# 2026-10-29 T4 stock simple v2 - RENDER DONE

Run dir: `C:/AI/community/runs/terrace_dom_q5stockv2_20261028_s51083011`
Brief: `notes/2026-10-28-max-brief-T4-stock-simple-v2.md` (T4 = stock
`H3_Turbo_2Pass_ErosMax_b7_simple_v2.json` at stock defaults, deviations (a)-(e) + one extra raw save)
Earlier status note for this arm (kept): `notes/2026-10-28-T4-stock-v2-DONE.md` (that one stopped at
"graph not built yet"; this note is the render).

## Result

| | file | ffprobe |
|---|---|---|
| stock graph's own output | `terrace_dom_q5stockv2_20261028_s51083011.mp4` | 243 f, 24 fps, 10.125 s, audio yes, **1424x1072**, 14,886,551 B |
| native pre-post-process (brief extra) | `terrace_dom_q5stockv2_20261028_s51083011_raw.mp4` | 243 f, 24 fps, 10.125 s, audio yes, **1184x896**, 5,285,085 B |

One GPU window, one attempt, no redo: `06:36:12 -> 06:40:42 CT`, gpu_guard IDLE before queue,
`gpu_lock` ACQUIRED pid 21284 / RELEASED, `JOB end ... ok secs=240.1`,
prompt_id `76f3b2f3-3e48-428b-b092-e7d9ed13eb36`, `OBJECTIVE ok ... frames=243 audio=True`,
runner exit 0, comfyui_auto unloaded, lock released. `objective.json` +
`..._stills_contact.png` in the run dir (no vision used - judging is Derek's, per the standing rule).
Youth guard: `t4_guard.py` = same pinned gate as `comm.run` - 3 prompt strings, 0 failures, PASS,
run before the window. Static gate (`t4_static.py` = `run_graph_job.static_check` against live
`/object_info`, no submit): 0 problems.

QNAP `/pi-drop/`: both files `Copied (new)`, size-verified against local
(14,886,551 and 5,285,085 bytes, identical).

## The graph

`request.api.json` = 43 nodes = the stock workflow converted to a flat API graph (40) + the one
extra output the brief asks for (2) + `CreateVideo` (1). Converter: `t4_ui2api3.py` (subgraphs
expanded - a subgraph instance is transparent, the virtual output node is `definition.outputNode.id`
= -20; widgets mapped by position from the live `/object_info`; mode 4 bypass routed through,
mode 2 mute dropped, rgthree relays applied; graph built lazily from the sinks).

`graph_diff.txt` compares **stock as shipped** vs **submitted**, joined by UI node reference (api
ids are walk-order and shift). It lists all 6 changed parameters, the 3 added nodes, the 184
parameters verbatim unchanged, the frame math, and the conversion notes.

Deviations, all of them (brief letters):

- (a) ui 9 `LoadImage`: `mode` 4 (bypassed) → 0, `image` `example.png` →
  `community/TERRACE2_768x1344.png` (the file B2 used). Consequence in the graph: the R2V
  `ref_images.ref_image_0` socket, fed by nothing in stock, is now wired to that node.
- (b) ui 2 prompt: `<Prompt>` → the bytes of `runs/terrace_dom_q5guide_20261028_s51083007/prompt_seg0.txt`
  read by path, 13,128 chars, sha256 `fcad1c379bf097f3…` = the same prompt B2 rendered.
- (c) ui 59 `Seed (rgthree)`: `-1` → `51083002`; the frontend control set to `fixed` (the API graph
  carries the literal seed - the control widget has no API counterpart).
- (d) ui 17 `PrimitiveFloat` Duration `15` → `10.0`. The graph has no frame-count input; its own
  formula (`ComfyMathExpression` in the two-pass subgraph,
  `max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17`) gives 361 at 15 s and **243 at 10.0 s**.
  Verified in the render: 243 frames / 10.125 s.
- (e) ui 73 prefix → `community/terrace_dom_q5stockv2_20261028_s51083011/terrace_dom_q5stockv2_20261028_s51083011`.
- extra save only: `raw_cv` CreateVideo (fps 24) + `raw_save` SaveVideo
  (`<prefix>_raw`, format/codec auto, same encoding as B2's proven SaveVideo) wired to the
  generator's own `VAEDecode` IMAGE and `VAEDecodeAudio` outputs - i.e. before
  `RTXVideoSuperResolution` (ui 39) and before `LokkenVideoPostProcessing`.

Everything else is stock as shipped: beta 7 model + its stock dials, 8 steps pass 1 / 3 steps
pass 2, sigma shift 12 video / 3 audio, VSA `selection: "vsa"` + `selection.keep_percent: 10`,
`minimax_h3_latent_upscaler_3d_fp16`, RTX 1.2x scale ULTRA, `LokkenVideoPostProcessing`
crf 18 / preset medium / grain 0.005, preview path skipped, H3PowerLoraStack + ADALN entries as
the file ships them, `format: "mp4"` + `format.codec: "auto"` on the stock SaveVideo.

## What the stock graph's own defaults do (the comparison caveat for T4-vs-B2)

The stock file's resolution chain is **not** driven by the start image:

- `ResolutionSelector` (ui in the two-pass subgraph) = `aspect_ratio "4:3 (Standard)"`,
  `megapixels 0.3`, `multiple 32` → pass 1 samples 4:3 at 0.3 MP;
- `MinimaxH3LatentUpscaler3D` `mode "megapixels"`, `mode.megapixels 1.0`, `align 32` → pass 2
  lands on **1184x896** (37x28 latent, 1.06 MP - the next aligned size above 1.0 MP);
- `RTXVideoSuperResolution` `scale by multiplier 1.2` → **1424x1072**;
- `LokkenVideoPostProcessing` crf 18 / preset medium writes the file.

So from a 768x1344 portrait start image the stock UI renders a **4:3 landscape** clip. That is the
graph's own default (the brief allowed no resolution deviation, so I did not touch it), and it means
**T4 and B2 are not pixel-comparable**: B2 is 768x1344 portrait. If a res-matched stock cell is
wanted, that is a new brief item (aspect ratio from the input image, or 768x1344 explicit).

Cost, one clip, full stock chain (2-pass + latent upscale + RTX + post-process encode + two saves):
**240.1 s** at 0.3 MP / 8 steps then 1.0 MP / 3 steps. For scale: B2's 8-step single-pass
768x1344 243 f was 360.2 s and T3's 12-step 2-pass was ~420 s. The stock chain is the cheapest
per finished clip measured so far on this cell, and its own post-processing (crf 18 + grain 0.005)
is inside the graph, not added by me.

## Toolchain findings (worth keeping)

1. **Dynamic combo v3 is dotted in the API, nested in the UI.** The stock UI stores
   `[key, <that option's params...>]`; the API prompt wants `"selection": "vsa"` plus
   `"selection.keep_percent": 10` (proven by B2's graph). My first T4 attempt used the nested
   frontend form `{"key":..., "inputs":{...}}` → it *passed* `/prompt` validation and then died at
   runtime: `BlockSparseAttention.execute() missing 1 required positional argument: 'selection'`
   (2 attempts, same failure, both paid at 60 s each). Fixed in `t4_ui2api3.py`.
2. **All-caps custom types are link sockets.** `H3PowerLoraStack.adaln_modality` is type
   `H3_MODALITY`; the UI carries a stored dict for the unconnected socket, and sending it is not
   the graph's effective behaviour (the stored entry is `on=false`, and the installed node has no
   widget on that socket). The converter now treats non-`COMFY_` all-caps types as pure links, and
   `graph_diff.txt` records every value the installed build has no parameter for.
3. **A 2-SaveVideo graph breaks the harness copy rule.** `comm.run` copies `files[0]` of the
   prompt history into `<run_dir>/<tag>.mp4`, and with two saves that is the *raw* clip (mine, by
   execution order). `t4_collect.py` places both files from ComfyUI's output dir by prefix, so
   `<tag>.mp4` = the stock encode path and `<tag>_raw.mp4` = the native clip. `objective.json`
   probed the raw (243 f, audio) - the gate result is the same for both.
4. **`run_graph_job.py` JOB-error path has a NameError** (line 141, `res["attempts"].append(dict(p, ...))`
   with `p` unbound when the job errored). It exits 1 after the `finally`, and the `finally` does
   unload comfyui_auto and release `gpu-render.lock` correctly, so the box is left IDLE. Not fixed
   (community script, outside this brief); flagged here.
5. Length: this graph exposes duration, not frames. Any future cell that wants an exact frame count
   should set the duration so the graph's own formula lands on it (10.0 s → 243), not edit the
   expression.

## Files in the run dir (this arm's audit)

`t4_ui2api3.py` (converter, final), `t4_ui2api.py` (v2, kept for history), `t4_build.py`
(deviations + asserts + graph_diff), `t4_guard.py`, `t4_static.py`, `t4_collect.py`,
`t4_bsa.py` / `t4_dump.py` / `t4_trace_up.py` / `t4_def_nodes.py` / `t4_grep_wf.py` /
`t4_search.py` (inspectors), `t4_validate.py` / `t4_watch.py` (submit probes),
`t4_ui_modified.json` (stock + the 7 widget edits, for provenance),
`_ui2api/api_stock.json|api_T4.json|*.map.json|*.audit.txt|*.flags.txt|api_T4_refs.json`,
`graph_diff.txt`, `request.api.json`, `status.log`, `objective.json`,
`terrace_dom_q5stockv2_20261028_s51083011.mp4`, `..._raw.mp4`, `..._stills_contact.png`.

## Not done

- No judging (no vision on images/video without permission).
- No T5: the brief stops after T4.
