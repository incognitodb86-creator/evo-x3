# ALI-147 RS3 (REFSHEET, arm 5) - graph built, sheet PLACEMENT pending (Forge, 2026-10-22, read-only + in-scope writes; no GPU, no render, no job request)

## The live task line (TASKS.md, verbatim, now marked `[!]`)
```
- [!] RS3 Build REFSHEET (arm 5) from FIX1's submitted graph (`runs\ali147_pool_fix1_s51080000\request.api.json`). Change only chunk 2's `MiniMaxH3ReferenceToVideo` node: `ref_image_1` = the sheet; `ref_image_size` match → max. Then the chunk-2 prompt: prepend the 2-line subject_definitions block from the plan (or, if the prompt already binds `<Picture 1>`, replace only that line). Seed 51080000, chunk 1 and every other node byte-identical. Check: `graph_diff.txt` (git diff --no-index vs FIX1) shows exactly those 3 changes; static object_info check passes.
```
The RS1/RS2 lines and the archived TASKS backups (e.g. `TASKS.md.bak-2026-10-22-071951`) add the parts this iteration
also honoured: "the sheet is the face-panel + full-body-row image, 3:2 panels, 768x512 per panel - NOT the start still,
NOT the 768x1344 PNG", "Verify its dimensions with PIL and its sha256 with certutil BEFORE building", "Build the sheet
first (RS1/RS2); the placement needs a decision", "Do NOT write p7\JOB_REQUEST.json this task".

## What RS3 produced this iteration
- `C:\AI\community\runs\ali147_pool_refsheet_s51080000\request.api.json` - arm 5 built from FIX1's graph
  (`runs\ali147_pool_fix1_s51080000\request.api.json`, byte-identical to that arm's `submitted_graph.pretty.json`,
  confirmed with `cmp`, silent). 26 nodes, 11,424 bytes, written in FIX1's exact byte format
  (`json.dumps(..., indent=1, sort_keys=True, ensure_ascii=False)`, CRLF, no trailing newline - the builder proves that
  format reproduces FIX1's file byte-for-byte before writing, so the diff shows only real deltas).
- `C:\AI\community\runs\ali147_pool_refsheet_s51080000\graph_diff.txt` - made with an existing tool, not a new script
  (specs\ali147.md:103 "graph_diff.txt comes from an existing JSON diff tool (no new script, rule 2)"):
  `git -C C:\AI\community\runs diff --no-index --output=<run folder>\graph_diff.txt "ali147_pool_fix1_s51080000\submitted_graph.pretty.json" "ali147_pool_refsheet_s51080000\request.api.json"`
  (exit 1 = differences found). It shows exactly the arm:
  1. `c1.ref_images.ref_image_1` `["img",0]` -> `["sheet",0]` (the sheet, NOT the start still, NOT the 768x1344 PNG);
  2. `c1.ref_image_size` `match` -> `max`;
  3. `c1.prompt` = the 2-line `subject_definitions` block prepended (chunk 2's prompt did not bind `<Picture 1>`, so the
     prepend branch applies, not the replace-the-line branch);
  plus the new `sheet` LoadImage node (the source of `ref_image_1`) and `save.filename_prefix` ->
  `community/ali147_pool_refsheet_s51080000/ali147_pool_refsheet_s51080000`.
- Builder + self-check: `C:\AI\community\notes\ali147_refsheet_build_graph.py` (py_compile ok, run: all checks printed,
  exit 3 = "graph built, placement pending"). It asserts: only the `sheet` id added; every node except `c1`/`save`
  byte-identical (23 of 25); `c1` input deltas exactly `{ref_images.ref_image_1, ref_image_size, prompt}`; `save` delta
  exactly `{filename_prefix}`; `c1` class_type still `MiniMaxH3ReferenceToVideo` with `clip/vae/audio_vae/width/height/length`
  links untouched; chunk-1 prompt, start-still string (`community/POOL_768x1344.png`), seed 51080000, length 243,
  `win1` extension_frames 238 / overlap_frames 22 unchanged; the new prompt = block + old prompt with exactly one
  `<Picture 1>`; `LoadImage` input names validated against `specs\extender_object_info.json`; `ref_image_size` options
  `["match","max"]` confirmed in `ComfyUI\comfy_extras\nodes_minimax_h3.py:267` (built-ins are not in the Extender
  snapshot); adults-only guard (`comm.guard_ok`) passes on every prompt.

## The 2-line subject_definitions block (verbatim, byte-identical to this graph's chunk-1 block)
```
subject_definitions:
<Subject 1> is the adult woman shown in <Picture 1>, with long straight blonde hair worn loose past her shoulders, blue eyes, slim toned lightly tanned skin, and a wet sheer champagne-beige scoop-neck bikini top with matching low-rise bottoms.
```
In arm 5 `<Picture 1>` = the reference sheet, which is what the block binds. Taken from the segment's own chunk-1 prompt
(the per-segment reading documented in `notes\ali147-fix4-graph-20261022.md`: a block is copied from the segment's c0).

## The sheet, verified before building (RS1's numbers re-checked)
- path `C:\Users\derek\5slock\approved_characters\REF_SHEETS_2026-10-19\RS016_portrait_1152x2016.png`
- PIL: size `(1152, 2016)`, mode `RGB`, format `PNG`. Geometry is self-consistent with the approved 3:2 rule:
  2016 = the 1152 face panel (full width) + the 864 full-body row; 1152 = three 384 px 3:2 panels (768x512 scaled to 384x256).
- SHA-256 (two tools): `certutil.exe -hashfile ... SHA256` and python hashlib both =
  `da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a` - identical to the RS1 line's recorded hash.
- MANIFEST row 016: `016,21,standing,standing front, standing side, standing back,,,RS016.jpg` (front / left-profile / back;
  no walking, no sitting); `CHARACTER.md`: blonde with long straight hair past shoulders, blue eyes, slim toned, light tan.
- Approved source `RS016.jpg` = 1024x1024, sha256 `0399555b4411a65ed59d26866125c2a5f0946244837dd16de991662e748f2386` (not a sheet).
- RS1's rule: use the sheet as it is. No generation, no crop, no edit, no copy made by Forge.

## Why the arm cannot be requested as-is: the sheet is outside ComfyUI's reachable input (the "placement" decision)
`LoadImage.load_image` resolves its string through `folder_paths.get_annotated_filepath()` (ComfyUI\nodes.py:1764).
`get_annotated_filepath` -> `annotated_filepath()` recognises only the `[output]` / `[input]` / `[temp]` suffixes, else
`base_dir = get_input_directory()`, then `filepath = os.path.abspath(os.path.join(base_dir, name))` and a hard
`is_within_directory(base_dir, filepath)` containment check that raises `ValueError("Invalid file path: {!r}")`
(ComfyUI\folder_paths.py:257-271 and :343-357). So:
- an **absolute** string into `C:\Users\derek\5slock\approved_characters\...` raises at run time:
  `ValueError: Invalid file path: 'C:\Users\derek\5slock\approved_characters\REF_SHEETS_2026-10-19\RS016_portrait_1152x2016.png'`
  (and the `/view` endpoint answers 404 for the same reason);
- `LoadImage.INPUT_TYPES` lists only top-level files of the input dir (`os.listdir` + `isfile`), and this ComfyUI's
  `validate_prompt` does not check COMBO values, which is why the arm's `community/POOL_768x1344.png` sub-path is legal;
- the input dir is `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input` (it contains `community\POOL_768x1344.png`;
  `C:\Users\derek\5slock\community` does not exist, so no remap is in play; `extra_model_paths.yaml` maps model folders
  only, and `get_input_directory()` is a single directory).
- `glob(ComfyUI\input\**\RS016*)` = **0 matches**. There is no loadable sheet anywhere in the input tree.

The graph therefore uses the only string form that can load, mirroring the arm's start still:
`"image": "community/RS016_portrait_1152x2016.png"`. It resolves to
`C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png`, which does not exist.

RS1's forward note offered two routes: "RS3 must either use an absolute/"input"-rooted LoadImage string (the only
allowed node-value change, kept in graph_diff.txt) or get a copy placed under ComfyUI\input - RS1 forbade copying here."
The first route is now measured, not assumed: an **absolute** string fails `is_within_directory` and raises
`ValueError: Invalid file path: ...` at run time, and the **"input"-rooted** string needs the file inside
`ComfyUI\input`, where no RS016 exists. So the node-value change alone cannot make the sheet readable; only the copy
(not allowed for Forge) can. That is the whole block - one `copy` by you closes RS3 with no graph edit.

Placing it there is a **copy** - and PROMPT.md's writable list is "TASKS.md, p7\JOB_REQUEST.json,
runs\ali147_pool_*\request.api.json, PROOF.md, fairness.txt, notes\*, AGENTS.md learning line. Nothing else.", with
moves allowed only by the failed-job rule. So the placement is Derek's call, exactly as the archived RS3 line says
(`TASKS.md.bak-2026-10-22-071951`): "Build the sheet first (RS1/RS2); the placement needs a decision."

The other open item on the live line, "static object_info check passes", is the harness static check (GET
127.0.0.1:10004/object_info, writes STATIC_FAIL on an unknown class - AGENTS.md). That is a ComfyUI call, i.e. GPU-side,
so it is off-limits to Forge and runs at render time. Offline here: `LoadImage` inputs checked against
`specs\extender_object_info.json` (only `image`, required, present), and the built-in `MiniMaxH3ReferenceToVideo` +
`ref_image_size` options read from `ComfyUI\comfy_extras\nodes_minimax_h3.py:252-282` (built-ins are not in the
Extender snapshot - the known ALI-147 rule).

## Task bookkeeping for this iteration
- `TASKS.md`: RS3 marked `[!]`, one indented `BLOCKED:` line (1477 chars, under the 1500 cap), `STOP_RALPH` appended as
  the last line. At the start of this iteration TASKS.md had **no** STOP_RALPH line (the harness clears it between runs).
- `p7\JOB_REQUEST.json`: untouched (last write 17:34 by FIX4_REQ). No `runs\ali147_pool_refsheet_s51080000\status.log`,
  no mp4, no PROOF.md, no fairness.txt written here - those belong to RS4.
- RS4 (render) and RS5/RS6 left as `- [ ]`; nothing was requested, so the loop stops on the placement decision.

## For the decision (no action taken by Forge)
- Option A (one copy by you, no graph edit needed): copy the approved sheet to
  `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png` and verify the copy's
  SHA-256 equals `da0b6a0b...` (the RS1 hash) before the first render. Then this task's file needs no change, and a
  separate REFSHEET_REQ line can request `{"jobs":[{"id":"ali147_pool_refsheet_s51080000","kind":"graph","frames":1443,"frames_tol":24,"minutes":180}]}`
  (1443 = FIX1's frame count; note `ref_image_size: max` is the 2048 px short-edge path, "can be several times slower"
  per the node's own tooltip, so the 180 min budget is the number to watch).
- Option B (a name of your choosing): if the copy lands under a different name/folder inside `ComfyUI\input`, the
  `sheet` node's string is the one line to change - it stays the only sheet-reference delta.
- Not available to Forge: copying, writing outside the listed paths, driving the UI, or any GPU call (ComfyUI `:10004`
  `object_info` was NOT called, so the harness static check stays the renderer's first word).

## Face-crop facts for RS5 (no decision made here; RS2 says the builder must not guess)
- RS5 needs a square face crop with >=50% margin around the face. In this file the face panel occupies the full-width
  top square `x 0-1152, y 0-1152`; the body row is `y 1152-2016` with three 3:2 panels at `x 0-384`, `384-768`, `768-1152`.
  A crop equal to the whole face panel is the only square in the file that is not a scaled-up crop of a body panel.
- `analysis.subject_crop()` with `face_crop=auto` picks "the first valid non-empty crop, sorted by path" over
  `<path>_crops\` images. With the sheet as a single file, `auto` can only produce one crop of that one image
  (validity needs subject pixels >=10% and an edge-inset mean std dev >=10), i.e. the 1152x2016 sheet / a crop of the
  sheet, not the face panel. So for RS5 `face_crop=` must be an explicit `L,T,R,B` (Derek's number, RS2), not `auto`.
- RS5 will need its own `sheet_b` LoadImage node for `ref_image_2` (shared side), plus `ref_image_1` = the start still
  with `max`, and chunk 1's `prompt` unchanged with no `<Picture 1>` tag.
