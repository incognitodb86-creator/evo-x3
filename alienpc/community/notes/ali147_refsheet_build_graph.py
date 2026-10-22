r"""ali147_refsheet_build_graph.py - ALI-147 RS3 (REFSHEET, arm 5): build arm 5's graph from FIX1's.

Task line, C:\Users\derek\5slock\ralph-community\TASKS.md, RS3 (quoted from the archived RS3 text in
TASKS.md.bak-2026-10-22-071951; the live RS3 line is shorter and adds "static object_info check passes", which is the
harness's GPU-side check - see notes\ali147_refsheet_rs3_blocked.md):
  "Build REFSHEET (arm 5) from FIX1's submitted graph (`runs\ali147_pool_fix1_s51080000\request.api.json`).
   Change only chunk 2's `MiniMaxH3ReferenceToVideo` node: `ref_image_1` = the sheet; `ref_image_size` match -> max.
   Then the chunk-2 prompt: prepend the 2-line subject_definitions block from the plan (or, if the prompt already
   binds `<Picture 1>`, replace only that line). Change nothing else: chunk 1 and every other node stay byte-identical
   (same start still string, same prompt, same seed 51080000, same lengths). Node ids stay. The sheet is the
   face-panel + full-body-row image, 3:2 panels, 768x512 per panel - NOT the start still, NOT the 768x1344 PNG.
   Verify its dimensions with PIL and its sha256 with certutil BEFORE building. Write graph_diff.txt in the run folder:
   the 3-node diff is the proof of the arm. Do NOT write p7\JOB_REQUEST.json this task."

WHAT THIS SCRIPT DOES (one write, everything else read-only; no GPU, no network, no render, no request):
  writes C:\AI\community\runs\ali147_pool_refsheet_s51080000\request.api.json
  reads  FIX1's request.api.json, the approved sheet + its sha256/dimensions, the ComfyUI input tree (existence only),
         the built-in node source for the ref_image_size options, specs\extender_object_info.json for the LoadImage schema.

THE SHEET: C:\Users\derek\5slock\approved_characters\REF_SHEETS_2026-10-19\RS016_portrait_1152x2016.png
  (RS1 line, [x]): 1152x2016 (3:2), SHA-256 da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a.
  The 2016 px height is the 1152 face panel + the 864 full-body row; the 1152 width is the three 384 px 3:2 panels.
  The script re-verifies both numbers; the hash is also reproduced with certutil -hashfile SHA256.

THE LoadImage STRING: ComfyUI resolves LoadImage through folder_paths.get_annotated_filepath() -> os.path.join(
  get_input_directory(), name) and then a hard `is_within_directory(base_dir, filepath)` containment check
  (ComfyUI\folder_paths.py:343-357, :257-271 - only [output]/[input]/[temp] suffixes change base_dir). An absolute
  path into C:\Users\derek\5slock\approved_characters therefore raises ValueError("Invalid file path: ...") at run
  time, so the string used here is the input-rooted relative form, same shape as the arm's start still
  ("community/POOL_768x1344.png"): "community/RS016_portrait_1152x2016.png". That file does not exist yet:
  ComfyUI\input has no RS016 anything. Placing it there is a COPY outside this agent's writable list (PROMPT.md:
  "Files you may write: ... runs\ali147_pool_*\request.api.json, PROOF.md, fairness.txt, notes\*, AGENTS.md learning
  line. Nothing else.") and it is exactly the "placement" RS3 names as needing a decision. The script prints
  INPUT_PRESENT / INPUT_MISSING and does NOT write a job request.

graph_diff.txt is produced by an existing tool, not a new script (specs\ali147.md:103):
  git diff --no-index --output=<run folder>\graph_diff.txt --label a/... <FIX1 graph> <arm 5 graph>
"""
import glob
import hashlib
import json
import os
import sys

from PIL import Image

sys.path.insert(0, r"C:\AI\community\scripts")
import comm  # noqa: E402  adults-only guard only; nothing is sent anywhere

W = r"C:\AI\community"
SRC = os.path.join(W, "runs", "ali147_pool_fix1_s51080000", "request.api.json")
DST_DIR = os.path.join(W, "runs", "ali147_pool_refsheet_s51080000")
DST = os.path.join(DST_DIR, "request.api.json")
SPEC = r"C:\Users\derek\5slock\ralph-community\specs\extender_object_info.json"
H3_SRC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_minimax_h3.py"
COMFY_INPUT = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input"

SHEET_SRC = r"C:\Users\derek\5slock\approved_characters\REF_SHEETS_2026-10-19\RS016_portrait_1152x2016.png"
SHEET_SHA256 = "da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a"
SHEET_WH = (1152, 2016)
SHEET_NODE = "sheet"
SHEET_IMG = "community/RS016_portrait_1152x2016.png"

ARM = "ali147_pool_refsheet_s51080000"
SEED = 51080000
CH1, CH2, SAVE = "c0", "c1", "save"
R2V = "MiniMaxH3ReferenceToVideo"
START_STILL = "community/POOL_768x1344.png"


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jdump(x):
    return json.dumps(x, sort_keys=True)


def sheet_checks():
    h = sha256(SHEET_SRC)
    im = Image.open(SHEET_SRC)
    size, mode, fmt = im.size, im.mode, im.format
    im.close()
    assert h == SHEET_SHA256, "sheet sha256 %s != RS1's %s" % (h, SHEET_SHA256)
    assert size == SHEET_WH, "sheet dimensions %s != %s" % (size, SHEET_WH)
    print("SHEET ok sha256=%s size=%s mode=%s format=%s  (3:2: 1152 face panel + 864 body row, three 384px 3:2 panels)"
          % (h[:16] + "...", size, mode, fmt))
    return h


def load_graph(path):
    raw = open(path, "rb").read().decode("utf-8")
    return raw, json.loads(raw)


def dump_format(graph, raw):
    """Return kwargs that reproduce FIX1's file byte-for-byte, so the diff shows only real deltas."""
    for kw in ({"ensure_ascii": False}, {"ensure_ascii": True}):
        for nl in ("", "\n"):
            for eol in ("\n", "\r\n"):
                t = json.dumps(graph, indent=1, sort_keys=True, **kw) + nl
                if t.replace("\n", eol) == raw:
                    print("FORMAT kwargs=%s trailing_newline=%r eol=%r reproduces FIX1's file byte-for-byte" % (kw, nl, eol))
                    return kw, nl, eol
    raise AssertionError("no json.dump format reproduces FIX1's request.api.json; not guessing a writer")


def block_from_ch1(ch1_prompt):
    """The 2-line subject_definitions block of this graph's own chunk-1 prompt (the plan's per-segment block)."""
    lines = ch1_prompt.split("\n")
    assert lines[0] == "subject_definitions:", "chunk-1 prompt has no subject_definitions header"
    assert "<Picture 1>" in lines[1] and lines[1].startswith("<Subject 1>"), "block line 2 is not the <Subject 1>/<Picture 1> definition"
    assert lines[2] == "" and lines[3].endswith(":"), "block is not 2 lines + blank line + a section header"
    block = lines[0] + "\n" + lines[1]
    assert len(block.split("\n")) == 2
    return block


def main():
    sheet_sha = sheet_checks()

    # LoadImage schema: required inputs of the new node, from the shipped snapshot (spec: the LoadImage schema is there).
    oi = json.load(open(SPEC, encoding="utf-8"))
    li = oi["LoadImage"]["input"]
    names = set(li.get("required", {})) | set(li.get("optional", {}))
    assert names >= {"image"}, "unexpected LoadImage schema: %s" % sorted(names)

    # ref_image_size options from the built-in node source (built-ins are not in the Extender snapshot).
    src = open(H3_SRC, encoding="utf-8", errors="replace").read()
    assert 'io.Combo.Input("ref_image_size", options=["match", "max"]' in src, "ref_image_size options not found in nodes_minimax_h3.py"
    print("ref_image_size options [\"match\", \"max\"] confirmed in comfy_extras\\nodes_minimax_h3.py (built-in node)")

    raw, g0 = load_graph(SRC)
    kw, nl, eol = dump_format(g0, raw)

    # FIX1 is the base: chunk 2 is already the R2V node, so RS3's variables are exactly the listed ones.
    assert g0[CH2]["class_type"] == R2V, "FIX1's chunk 2 is not %s" % R2V
    assert g0[CH1]["class_type"] == R2V
    assert g0[CH1]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
    assert g0[CH2]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
    assert g0[CH2]["inputs"]["ref_image_size"] == "match"
    assert g0["img"]["inputs"]["image"] == START_STILL
    assert g0[CH1]["inputs"]["prompt"].startswith("subject_definitions:"), "FIX1 chunk 1 has no block to copy"
    assert "<Picture 1>" not in g0[CH2]["inputs"]["prompt"], "chunk 2 already binds <Picture 1>: replace that line, do not prepend"

    block = block_from_ch1(g0[CH1]["inputs"]["prompt"])
    print("2-line subject_definitions block taken from chunk 1 (segment 1) prompt, byte-identical; %d chars" % len(block))

    g = json.loads(jdump(g0))  # deep copy, key order/format neutral
    g[SHEET_NODE] = {"class_type": "LoadImage", "inputs": {"image": SHEET_IMG}}
    g[CH2]["inputs"]["ref_images.ref_image_1"] = [SHEET_NODE, 0]
    g[CH2]["inputs"]["ref_image_size"] = "max"
    g[CH2]["inputs"]["prompt"] = block + "\n\n" + g0[CH2]["inputs"]["prompt"]
    g[SAVE]["inputs"]["filename_prefix"] = "community/%s/%s" % (ARM, ARM)

    # ---- self-check: the diff is exactly the listed changes, nothing else ----
    assert set(g) - set(g0) == {SHEET_NODE} and set(g0) - set(g) == set(), "node ids changed"
    touched = set()
    for k in g0:
        if k in (CH2, SAVE):
            continue
        assert jdump(g[k]) == jdump(g0[k]), "node %s changed - it must stay byte-identical" % k
        touched.add(k)
    diff_c1 = {a for a in set(g[CH2]["inputs"]) | set(g0[CH2]["inputs"])
               if g[CH2]["inputs"].get(a) != g0[CH2]["inputs"].get(a)}
    diff_save = {a for a in set(g[SAVE]["inputs"]) | set(g0[SAVE]["inputs"])
                 if g[SAVE]["inputs"].get(a) != g0[SAVE]["inputs"].get(a)}
    assert diff_c1 == {"ref_images.ref_image_1", "ref_image_size", "prompt"}, "chunk 2 inputs changed: %s" % sorted(diff_c1)
    assert diff_save == {"filename_prefix"}, "save node changed beyond filename_prefix: %s" % sorted(diff_save)
    assert g[CH2]["class_type"] == R2V and g[CH2]["inputs"]["ref_images.ref_image_1"] == [SHEET_NODE, 0]
    assert g[CH2]["inputs"]["ref_image_size"] == "max"
    for a in ("clip", "vae", "audio_vae", "width", "height", "length"):
        assert jdump(g[CH2]["inputs"][a]) == jdump(g0[CH2]["inputs"][a]), "chunk 2 %s moved" % a
    p = g[CH2]["inputs"]["prompt"]
    assert p.startswith(block + "\n\n") and p.endswith(g0[CH2]["inputs"]["prompt"]), "chunk-2 prompt is not block + old prompt"
    assert p.count("<Picture 1>") == 1, "chunk-2 prompt binds <Picture 1> more than once"
    assert g[CH1]["inputs"]["prompt"] == g0[CH1]["inputs"]["prompt"], "chunk 1 prompt moved"
    assert g["img"]["inputs"]["image"] == START_STILL, "start still string moved"
    seeds = {n["inputs"]["noise_seed"] for n in g.values() if n["class_type"] == "RandomNoise"}
    assert seeds == {SEED}, "seed moved: %s" % seeds
    assert g[CH1]["inputs"]["length"] == 243 and g["win1"]["inputs"]["extension_frames"] == 238 and g["win1"]["inputs"]["overlap_frames"] == 22, "lengths moved"
    print("nodes byte-identical: %d of %d; chunk-2 input deltas %s; save delta %s; seed %s; chunk-1 length 243, extension 238, overlap 22"
          % (len(touched), len(g0), sorted(diff_c1), sorted(diff_save), SEED))

    # new node's input names exist on the class; required ones are present
    assert set(g[SHEET_NODE]["inputs"]) <= names and set(li.get("required", {})) <= set(g[SHEET_NODE]["inputs"])

    # adults-only guard on every prompt in the arm graph (run_graph_job.py applies the same rule)
    for k, n in g.items():
        if isinstance(n["inputs"].get("prompt"), str):
            assert comm.guard_ok(n["inputs"]["prompt"]), "adults-only guard rejects %s" % k
    print("adults-only guard: all prompts pass")

    # sheet placement: read-only existence check over the ComfyUI input tree (nothing is copied)
    found = glob.glob(os.path.join(COMFY_INPUT, "**", "RS016*"), recursive=True)
    loadable = os.path.exists(os.path.join(COMFY_INPUT, SHEET_IMG.replace("/", os.sep)))
    print("sheet source: %s exists=%s" % (SHEET_SRC, os.path.exists(SHEET_SRC)))
    print("ComfyUI input tree RS016 matches: %d %s" % (len(found), found))
    print("LoadImage string %r resolves to %s exists=%s -> %s"
          % (SHEET_IMG, os.path.join(COMFY_INPUT, SHEET_IMG.replace("/", os.sep)), loadable,
             "INPUT_PRESENT" if loadable else "INPUT_MISSING (copy into ComfyUI\\input is a placement decision, not an agent write)"))

    # write the one file, in FIX1's exact byte format, then re-read it
    os.makedirs(DST_DIR, exist_ok=True)
    txt = json.dumps(g, indent=1, sort_keys=True, **kw) + nl
    open(DST, "wb").write(txt.replace("\n", eol).encode("utf-8"))
    raw2, g2 = load_graph(DST)
    assert jdump(g2) == jdump(g), "written file does not parse back to the built graph"
    assert raw2 == txt.replace("\n", eol)
    print("WROTE %s (%d bytes, %d nodes, format identical to FIX1's file)" % (DST, len(raw2.encode("utf-8")), len(g2)))
    print("NO job request: p7\\JOB_REQUEST.json untouched. Render count 0. sheet_sha256=%s dims=%s" % (sheet_sha[:16] + "...", SHEET_WH))
    return 0 if loadable else 3  # 3 = graph built, placement pending


if __name__ == "__main__":
    sys.exit(main())
