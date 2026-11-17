# ALI-147 RS5 (REFSHEET_B, arm 5b) - graph built (Forge, 2026-10-22, CPU-only; no GPU, no render, no job request)

## The live task line (TASKS.md, verbatim)
```
- [ ] RS5 Build REFSHEET_B (arm 5b) from the RS3 graph (corrected by Max Architect 2026-10-22: chunk 1 node c0 is ALREADY MiniMaxH3ReferenceToVideo with ref_image_1 = the start still; do not swap any node). Only add the sheet to c0 as its own reference: c0 `ref_images.ref_image_2` = the same `sheet` LoadImage node as RS3 (image "community/RS016_portrait_1152x2016.png" in ComfyUI\input), and `ref_image_size` match -> max. Chunk 1's prompt (c0) gets the subject_definitions block with `<Picture 2>` for the sheet, plus TenStrip's scene line for `<Picture 1>` (both in the plan, arm 5b). Chunk 2 (c1) stays exactly as in RS3; seed 51080000; save filename_prefix = the new id ali147_pool_refsheet_b_s51080000. Check: graph_diff.txt vs REFSHEET shows only c0's ref_image_2 (+ its LoadImage node if a new one is needed), c0 ref_image_size, c0 prompt and filename_prefix; static object_info check passes (ref_images.ref_image_2 exists on MiniMaxH3ReferenceToVideo).
```

## RS3's block is closed - measured, not assumed
Derek took Option A. `C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png`
now exists: `certutil.exe -hashfile ... SHA256` = `da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a`
(= RS1's approved-sheet hash), PIL = `(1152, 2016) RGB PNG`, and `glob(ComfyUI\input\**\RS016*)` = 1. The REFSHEET arm
rendered from it (`cmp ali147_pool_refsheet_s51080000.api.json request.api.json` = silent, notes\ali147_refsheet_rs4_verify.md).
So arm 5b needs no placement decision and no graph-side workaround.

## What this iteration wrote
- `C:\AI\community\runs\ali147_pool_refsheet_b_s51080000\request.api.json` - arm 5b, 26 nodes, 12,144 bytes, built from
  RS3's `runs\ali147_pool_refsheet_s51080000\request.api.json` and written in that file's exact byte format
  (`json.dumps(..., indent=1, sort_keys=True, ensure_ascii=False)`, CRLF, no trailing newline - the builder proves that
  format reproduces the source file byte-for-byte before writing, so the diff shows only real deltas).
- `C:\AI\community\runs\ali147_pool_refsheet_b_s51080000\graph_diff.txt` - the required check artifact, made with the
  existing tool, not a new script (specs\ali147.md:103):
  `git -C C:\AI\community\runs diff --no-index --output=<run folder>\graph_diff.txt "ali147_pool_refsheet_s51080000\request.api.json" "ali147_pool_refsheet_b_s51080000\request.api.json"`
  (exit 1 = differences found). It shows **only** the four listed deltas, all on `c0`/`save`:
  1. `c0.prompt` - the subject_definitions block only (everything from `\n\nsummary:` on is byte-identical);
  2. `c0.ref_image_size` `match` -> `max`;
  3. `c0.ref_images.ref_image_2` = `["sheet", 0]` - RS3's existing LoadImage node, **no new node** (the task's
     "+ its LoadImage node if a new one is needed" branch does not apply);
  4. `save.filename_prefix` -> `community/ali147_pool_refsheet_b_s51080000/ali147_pool_refsheet_b_s51080000`.
  Builder + self-check: `C:\AI\community\notes\ali147_refsheet_b_rs5_build_graph.py` (py_compile ok, run prints
  `ALL CHECKS PASS`). Read-only probes: `notes\ali147_refsheet_b_rs5_probe_h3.py`,
  `notes\ali147_refsheet_b_rs5_probe_sidecar.py`; prompt text dumps for reading:
  `notes\ali147_refsheet_b_prompt_c0.txt` (source), `notes\ali147_refsheet_b_prompt_c0_new.txt` (arm 5b).
- `p7\JOB_REQUEST.json` untouched (this line asks for no job; RS6 is the render line). No status.log, no mp4,
  no PROOF.md, no fairness.txt written here.

## The new c0 subject_definitions block (verbatim, 4 lines; the rest of the prompt is byte-identical)
```
subject_definitions:
<Subject 1> is the adult woman shown in <Picture 1> and <Picture 2>, with long straight blonde hair worn loose past her shoulders, blue eyes, slim toned lightly tanned skin, and a wet sheer champagne-beige scoop-neck bikini top with matching low-rise bottoms.
<Picture 1> is the start still of the same adult woman at a dark metal balcony railing at night, in a three-quarter medium shot with warm wall light from the left, cooler ambient light from the open balcony side and a shallow depth of field; it gives her appearance for the opening frame, while the environment, camera movement, lighting and action are composed freely for the target shot.
<Picture 2> is the reference sheet for <Subject 1>, a face panel above a full-body front, side and back row; it gives only her face, hair, eyes, build and proportions, and gives no scene, background, lighting, camera, wardrobe state, pose or action.
```
Prompt: 3,295 -> 3,951 chars (block 920 + blank line + the unchanged 3,029-char tail); sha256 `afa3cf3e9c12ffad...`
(full, for the future fairness.txt). Source c0 = the base segment-1 chunk-1 text, sha256 `7b4b22bb170f...` (unchanged in
REFSHEET, so the arm's base prompt is the base-run text - the provenance check is in the builder).

Provenance of the wording (the plan's arm 5b text is on the box, not on this PC, so the two named components are
authored to the local rules, from this prompt's own vocabulary - no new scene facts):
- `<Picture i>` = reference-image ordinal i, per the node's own docstring (`nodes_minimax_h3.py:246-249` "Ordinals are
  1-based per type, so the prompt refers to them as <Picture i>"), so `ref_image_1` (the start still) = `<Picture 1>`
  and `ref_image_2` (the sheet) = `<Picture 2>`.
- Multi-source subject line and "state what each asset provides": `C:\AI\community\guides\VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`
  section 2.1 ("<Subject 1> is the woman whose appearance comes from <Picture 1> and whose walking motion comes from <Video 1>")
  and section 2 (one line per item; a label keeps the same meaning in every section).
- The scene line + the "use it only for X; pose and framing come from <Picture 1>" sheet-role line follow the TenStrip
  form in this repo (`C:\Users\derek\5slock\part2_1018\_dry_archive_0650\graphs\S-solo_c08.json`: a scene line under
  `subject_definitions:`, `<Subject 1> ... from <Picture 1>/<Picture 2>: ...`, then `<Picture 2> is a frame from Shot 1:
  use it only for her face, hair and the room; pose and framing come from <Picture 1>`).
- The `<Picture 1>` line deliberately repeats the summary's own claim ("uses <Picture 1> only as appearance guidance while
  freely composing the environment and camera") so the sections stay consistent; the sheet line states what it must not
  give. The sheet is bound **only** in `subject_definitions` - `summary`, `retention_analysis`, `detailed_description`,
  `overall_soundscape`, `non_diegetic_music` are untouched, which keeps arm 5b's delta to exactly what the line asks.
  Consequence stated, not worked around: `retention_analysis` has no `<Picture 2>` row (adding one is a prompt-section
  change the line does not ask for).

## Builder self-checks (all printed PASS)
- source arm is RS3: `c0`/`c1` both `MiniMaxH3ReferenceToVideo` (nothing swapped), `c0.ref_image_1 = ["img",0]`
  (the start still `community/POOL_768x1344.png`), `c0.ref_image_size = match`, no `ref_image_2` yet,
  `c1.ref_image_1 = ["sheet",0]` + `max`, sheet node string exact, `c0.prompt` = base seg1 c0 text.
- deltas: node set identical (no new node); 24 of 26 nodes byte-identical (every node except `c0`, `save`, incl. `c1`);
  `c0` input deltas exactly `{prompt, ref_image_size, ref_images.ref_image_2}`; `save` delta exactly `{filename_prefix}`;
  `c0` `clip/vae/audio_vae/width/height/length` and `length = 243` unchanged; `win1` 238/22 unchanged;
  RandomNoise seed set = {51080000}; start-still string unchanged.
- prompt: only the block changed (the tail from `summary:` is byte-identical); all six section headers present exactly
  once; every `<Picture 2>` occurrence lies inside `subject_definitions`; `<Picture 1>` count +1 (the scene line),
  `<Subject 1>` count +1 (the sheet-role line); base text provenance re-checked (see the sidecar note below).
- adults-only guard (`comm.guard_ok`) passes on every prompt string in the graph.
- sheet placement re-verified at write time: the LoadImage string resolves inside `ComfyUI\input` and the file is the
  approved sheet (sha256 + PIL).
- `ref_images.ref_image_2` exists on the class (the task's static-check clause), read from the built-in's own schema:
  `io.Autogrow.Input("ref_images", ... TemplatePrefix(input=io.Image.Input("ref_image", ...), prefix="ref_image_",
  min=0, max=9))` (`nodes_minimax_h3.py:269-272`) - the flat graph keys are therefore `ref_images.ref_image_1..9`;
  `ref_image_size` options `["match", "max"]` at :267. Built-ins are not in `specs\extender_object_info.json`
  (Extender nodes only), the known ALI-147 rule; `LoadImage` inputs are checked against that snapshot.

## Findings (stated, not worked around)
1. **The static object_info check is the renderer's.** The live line's "static object_info check passes" is the harness
   check (GET 127.0.0.1:10004/object_info, STATIC_FAIL on an unknown class). `:10004` is the GPU, off-limits here, so
   the clause closes at RS6; the offline equivalent above is the evidence I can produce.
2. **`max` on c0 is the slow path.** The node tooltip (:268): "'max' uses the reference pipeline's 2048px short edge for
   best identity fidelity. Reference tokens ride through every sampling step, so 'max' can be several times slower."
   The sheet's short edge is 1152 (> 1024), which is exactly why the task asks for `max`. c0's `length` is 243 frames,
   and RS4's chunk-2 `max` render cost 902.7 s vs FIX1's 857.5 s (+5.3%) for 481 frames, so arm 5b's chunk 1 is the
   first `max` reference in this pool test; RS6's render seconds are the number to watch (RS6's check names it).
3. **Two references on one node = a new sampling cost, and a fair-comparison caveat.** With `ref_image_2` on c0, chunk 1
   now conditions on 2 images; every other arm conditions chunk 1 on 1. That is the arm's variable, as specified.
   Frames stay 243 + 238 = 481 for the 2-chunk pool graph (unchanged by an input image), and the base graph's c0
   `length`, `seed`, `win1` 238/22 and the start-still string are untouched.
4. **Prompt-sidecar hashes**: `runs\p7_r2_c3_pmot_full_pool\prompts\*_long_r2v.txt` are CRLF and end with a trailing
   newline, so `certutil`/raw-byte sha256 (3,314 B, `2ee9ad0c...`) never matches the graph prompt string; the
   EOL-folded, right-stripped text (3,295 chars, `7b4b22bb...`) is exactly the stored string. The builder hashes it
   that way and prints both.
5. `ref_image_size` on c0 (`max`) and the sheet on c0 are the *only* differences from REFSHEET; REFSHEET's c1 is
   untouched, so the pair (REFSHEET, REFSHEET_B) isolates "the sheet also guides chunk 1 / the opening frame".
6. GPU calls: none. No llama-swap, no ComfyUI, no Strata, no render script, no vision judge, no request, no copy.

## Next line (not this task)
RS6 "Render REFSHEET_B (GPU). Check: as RS4 for `ali147_pool_refsheet_b_s51080000`, plus `sbs_refsheet_refsheetb.mp4`
and stills at frame 0 (opening, since chunk 1 changed)." Per AGENTS.md the render line is requested as
`{"jobs":[{"id":"ali147_pool_refsheet_b_s51080000","kind":"graph","frames":481,"frames_tol":0,"minutes":60}]}` and the
line stays `- [ ]` for the next iteration; RS6's named `sbs_refsheet_refsheetb.mp4` and the frame-0 stills are
Max/harness artifacts (`run_graph_job.py` has no hstack path and its contact sheet for a 20.04 s clip never covers
frame 0) - the RS4 precedent says that half comes back `[!]` for Max, not worked around.
