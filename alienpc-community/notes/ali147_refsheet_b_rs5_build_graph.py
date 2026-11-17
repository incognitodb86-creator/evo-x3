r"""ali147_refsheet_b_rs5_build_graph.py - ALI-147 RS5 (REFSHEET_B, arm 5b): build arm 5b from the REFSHEET (arm 5) graph.

Task line, C:\Users\derek\5slock\ralph-community\TASKS.md, RS5 (2026-10-22):
  "Build REFSHEET_B (arm 5b) from the RS3 graph (corrected by Max Architect 2026-10-22: chunk 1 node c0 is ALREADY
   MiniMaxH3ReferenceToVideo with ref_image_1 = the start still; do not swap any node). Only add the sheet to c0 as its
   own reference: c0 `ref_images.ref_image_2` = the same `sheet` LoadImage node as RS3 (image
   'community/RS016_portrait_1152x2016.png' in ComfyUI\input), and `ref_image_size` match -> max. Chunk 1's prompt (c0)
   gets the subject_definitions block with `<Picture 2>` for the sheet, plus TenStrip's scene line for `<Picture 1>`
   (both in the plan, arm 5b). Chunk 2 (c1) stays exactly as in RS3; seed 51080000; save filename_prefix = the new id
   ali147_pool_refsheet_b_s51080000. Check: graph_diff.txt vs REFSHEET shows only c0's ref_image_2 (+ its LoadImage
   node if a new one is needed), c0 ref_image_size, c0 prompt and filename_prefix; static object_info check passes
   (ref_images.ref_image_2 exists on MiniMaxH3ReferenceToVideo)."

WHY IT IS BUILDABLE NOW: RS3's block was the sheet's placement. Derek's Option A copy exists -
  C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png
  sha256 da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a (the RS1 hash), 1152x2016 (PIL), and the REFSHEET
  arm rendered from it (481 frames, notes\ali147_refsheet_rs4_verify.md). This script re-verifies all three before writing.

WHAT THIS SCRIPT DOES (one graph write + prompt dumps in notes for reading; everything else read-only; no GPU, no network,
no render, no job request - RS6 is the next line):
  writes C:\AI\community\runs\ali147_pool_refsheet_b_s51080000\request.api.json  (arm 5b, in RS3's exact byte format)
  writes C:\AI\community\notes\ali147_refsheet_b_prompt_c0_new.txt               (the new chunk-1 prompt, for reading)
  reads  runs\ali147_pool_refsheet_s51080000\request.api.json (RS3, = the graph that rendered: cmp with its .api.json),
         the base segment-1 chunk-1 prompt text (provenance), the placed sheet (hash + PIL), the ComfyUI input tree,
         specs\extender_object_info.json (LoadImage schema), comfy_extras\nodes_minimax_h3.py (the built-in's inputs:
         ref_images.ref_image_1/.ref_image_2/.ref_image_3 + ref_image_size options - built-ins are not in the snapshot).

THE ARM, exactly four deltas over RS3 (all of them on c0 / save):
  1. c0 `ref_images.ref_image_2` = ["sheet", 0]  - the same LoadImage node RS3 added; no new node is needed.
  2. c0 `ref_image_size` "match" -> "max"         - the sheet's short edge (1152) is above 1024, so max keeps it near
     native 1152 instead of squeezing to 1024 (node tooltip, nodes_minimax_h3.py:358-363). The start still is 768x1344,
     so match already squeezed it to 768 on c0; that is unchanged by this arm, it is RS3's own c1 treatment applied to c0.
  3. c0 `prompt` = the new subject_definitions block + "\n\n" + RS3's c0 text from "summary:" ONWARD, byte-identical.
     The block keeps the existing `<Subject 1>` line, widens it to "<Picture 1> and <Picture 2>" (the guide's
     multi-source form, guides\VIDEO_PROMPT_WRITING_GUIDE_ref_en.md section 2.1), adds the TenStrip scene line naming
     what <Picture 1> provides, and adds the <Picture 2> sheet-role line (what the sheet provides and what it must not
     give). Wording is authored from this prompt's own vocabulary (balcony railing, warm wall light from the left,
     cooler ambient light, shallow depth of field, three-quarter medium shot) - no new scene facts. The summary,
     retention_analysis, detailed_description, overall_soundscape and non_diegetic_music lines are NOT touched, so the
     only prompt delta is the block the task asks for (the sheet is bound in subject_definitions only).
  4. save `filename_prefix` = "community/ali147_pool_refsheet_b_s51080000/ali147_pool_refsheet_b_s51080000".
  c1 (chunk 2) stays byte-identical to RS3 (ref_image_1 = the sheet, ref_image_size max, block + continuation text);
  the start still string, seed 51080000, c0 length 243 and win1 238/22 stay as they are.

graph_diff.txt is produced by the existing tool, not a new script (specs\ali147.md:103), run by hand after this script:
  git -C C:\AI\community\runs diff --no-index --output=...\ali147_pool_refsheet_b_s51080000\graph_diff.txt ^
      "ali147_pool_refsheet_s51080000\request.api.json" "ali147_pool_refsheet_b_s51080000\request.api.json"
"""
import glob
import hashlib
import json
import os
import re
import sys

from PIL import Image

sys.path.insert(0, r"C:\AI\community\scripts")
import comm  # noqa: E402  adults-only guard only; nothing is sent anywhere

W = r"C:\AI\community"
SRC_DIR = os.path.join(W, "runs", "ali147_pool_refsheet_s51080000")
SRC = os.path.join(SRC_DIR, "request.api.json")
DST_DIR = os.path.join(W, "runs", "ali147_pool_refsheet_b_s51080000")
DST = os.path.join(DST_DIR, "request.api.json")
NOTES = os.path.join(W, "notes")
SPEC = r"C:\Users\derek\5slock\ralph-community\specs\extender_object_info.json"
H3_SRC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_extras\nodes_minimax_h3.py"
COMFY_INPUT = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input"
BASE_C0_TXT = os.path.join(W, "runs", "p7_r2_c3_pmot_full_pool", "prompts",
                           "p7_r2_c3_pmot_full_pool_seg1_c0_long_r2v.txt")

SHEET_NODE = "sheet"
SHEET_IMG = "community/RS016_portrait_1152x2016.png"
SHEET_SHA256 = "da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a"
SHEET_WH = (1152, 2016)
START_STILL = "community/POOL_768x1344.png"
BASE_C0_SHA = "7b4b22bb170fbcb85dce706ef746a862d49fa14142c1a704a672d4819b77f889"  # seg1 c0, unchanged in REFSHEET

ARM = "ali147_pool_refsheet_b_s51080000"
SEED = 51080000
C0, C1, SAVE = "c0", "c1", "save"
R2V = "MiniMaxH3ReferenceToVideo"

# the new subject_definitions block (4 lines: header + 3 definition lines), then a blank line, then RS3's own text.
NEW_BLOCK = "\n".join([
    "subject_definitions:",
    "<Subject 1> is the adult woman shown in <Picture 1> and <Picture 2>, with long straight blonde hair worn loose past her shoulders, blue eyes, slim toned lightly tanned skin, and a wet sheer champagne-beige scoop-neck bikini top with matching low-rise bottoms.",
    "<Picture 1> is the start still of the same adult woman at a dark metal balcony railing at night, in a three-quarter medium shot with warm wall light from the left, cooler ambient light from the open balcony side and a shallow depth of field; it gives her appearance for the opening frame, while the environment, camera movement, lighting and action are composed freely for the target shot.",
    "<Picture 2> is the reference sheet for <Subject 1>, a face panel above a full-body front, side and back row; it gives only her face, hair, eyes, build and proportions, and gives no scene, background, lighting, camera, wardrobe state, pose or action.",
])

SECTIONS = ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:",
            "overall_soundscape:", "non_diegetic_music:"]


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha256_eol_normalized_text(p):
    """Hash of the file's text with CRLF/CR folded to LF and trailing newlines stripped. Measured (probe
    notes\ali147_refsheet_b_rs5_probe_sidecar.py): the base-run prompt sidecars are CRLF and end with one trailing
    newline, so their raw-byte hash (3314 bytes, 2ee9ad0c...) is NOT the graph prompt's hash; the EOL-folded,
    right-stripped text (3295 chars, 7b4b22bb...) is exactly the graph's c0 prompt string."""
    t = open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def jdump(x):
    return json.dumps(x, sort_keys=True)


def sheet_checks():
    """RS3's block, re-checked read-only: the placed copy is the approved sheet and ComfyUI can load it."""
    placed = os.path.join(COMFY_INPUT, SHEET_IMG.replace("/", os.sep))
    assert os.path.exists(placed), "sheet not in ComfyUI\\input: %s" % placed
    h = sha256(placed)
    assert h == SHEET_SHA256, "placed sheet sha256 %s != RS1's %s" % (h, SHEET_SHA256)
    im = Image.open(placed)
    size, mode, fmt = im.size, im.mode, im.format
    im.close()
    assert size == SHEET_WH, "placed sheet %s != %s" % (size, SHEET_WH)
    print("SHEET PLACEMENT ok (RS3's block is closed): %s sha256=%s size=%s mode=%s format=%s"
          % (placed, h[:16] + "...", size, mode, fmt))
    return h


def dump_format(graph, raw):
    """Return kwargs that reproduce RS3's file byte-for-byte, so the diff shows only real deltas."""
    for kw in ({"ensure_ascii": False}, {"ensure_ascii": True}):
        for nl in ("", "\n"):
            for eol in ("\n", "\r\n"):
                t = json.dumps(graph, indent=1, sort_keys=True, **kw) + nl
                if t.replace("\n", eol) == raw:
                    print("FORMAT kwargs=%s trailing_newline=%r eol=%r reproduces the REFSHEET file byte-for-byte" % (kw, nl, eol))
                    return kw, nl, eol
    raise AssertionError("no json.dump format reproduces the REFSHEET request.api.json; not guessing a writer")


def new_prompt(old):
    """Replace ONLY the subject_definitions block (header + its <Subject 1> line) of RS3's c0 prompt."""
    lines = old.split("\n")
    assert lines[0] == "subject_definitions:", "c0 prompt has no subject_definitions header"
    assert lines[1].startswith("<Subject 1>") and "<Picture 1>" in lines[1], "c0 block line 2 is not the <Subject 1>/<Picture 1> definition"
    assert lines[2] == "" and lines[3] == "summary:", "c0 block is not header + one line + blank + summary:"
    head, tail = old.split("\n\n", 1)
    assert tail.startswith("summary:"), "c0 prompt tail does not start at summary:"
    assert "<Picture 2>" not in old, "the source prompt already binds <Picture 2>"
    p = NEW_BLOCK + "\n\n" + tail
    for s in SECTIONS:
        n = (1 if p.startswith(s + "\n") else 0) + p.count("\n" + s)
        assert n == 1, "section %s appears %d times in the new prompt" % (s, n)
    body = p.split("\n\n", 1)[1]
    assert body == tail, "everything after subject_definitions moved"
    i2 = [m.start() for m in re.finditer("<Picture 2>", p)]
    assert i2 and all(i < p.index("\n\nsummary:") for i in i2), "<Picture 2> bound outside subject_definitions"
    assert p.count("<Picture 1>") == old.count("<Picture 1>") + 1, "the scene line must add exactly one <Picture 1> binding"
    assert p.count("<Subject 1>") == old.count("<Subject 1>") + 1, "the sheet-role line must add exactly one <Subject 1> reference"
    assert comm.guard_ok(p), "adults-only guard rejects the new c0 prompt"
    return p


def main():
    sheet_sha = sheet_checks()

    # the built-in's own inputs (built-ins are not in the Extender snapshot, the known ALI-147 rule):
    # ref_images is an Autogrow group with prefix "ref_image_", min 0, max 9 -> the flat API keys are
    # ref_images.ref_image_1 .. ref_images.ref_image_9, so ref_image_2 is a real input on c0. The class docstring
    # states the label mapping this arm's prompt relies on: "Ordinals are 1-based per type, so the prompt refers to
    # them as <Picture i>" - i.e. ref_image_1 = <Picture 1> (the start still), ref_image_2 = <Picture 2> (the sheet).
    src = open(H3_SRC, encoding="utf-8", errors="replace").read()
    for n in ('io.Autogrow.Input("ref_images", optional=True',
              'input=io.Image.Input("ref_image"',
              'prefix="ref_image_", min=0, max=9',
              'io.Combo.Input("ref_image_size", options=["match", "max"]',
              'Ordinals are 1-based per type, so the prompt refers to them as'):
        assert n in src, "not found in nodes_minimax_h3.py: %s" % n
    assert "<Picture i> / <Video k> / <Audio j>." in src, "the <Picture i> = ref-image-ordinal mapping is not in the node docstring"
    print("MiniMaxH3ReferenceToVideo: ref_images autogrow prefix ref_image_ 1..9 (so ref_images.ref_image_2 is a real input), "
          "ref_image_size options [\"match\", \"max\"], and <Picture i> = ref image ordinal i - all confirmed in comfy_extras\\nodes_minimax_h3.py")

    # LoadImage schema from the shipped snapshot (the sheet node is reused as-is, so this is a re-check, not a change)
    oi = json.load(open(SPEC, encoding="utf-8"))
    li = oi["LoadImage"]["input"]
    names = set(li.get("required", {})) | set(li.get("optional", {}))
    assert names >= {"image"}

    raw, g0 = open(SRC, "rb").read().decode("utf-8"), None
    g0 = json.loads(raw)

    # the source arm: RS3 exactly as built, and as rendered (its .api.json cmp's clean, notes\ali147_refsheet_rs4_verify.md)
    assert g0[C0]["class_type"] == R2V and g0[C1]["class_type"] == R2V, "chunk nodes are not both R2V - do not swap anything"
    assert g0[C0]["inputs"]["ref_images.ref_image_1"] == ["img", 0], "c0 ref_image_1 is not the start still"
    assert g0[C0]["inputs"].get("ref_images.ref_image_2") is None, "c0 already has ref_image_2"
    assert g0[C0]["inputs"]["ref_image_size"] == "match", "c0 ref_image_size is not match"
    assert g0[C1]["inputs"]["ref_images.ref_image_1"] == [SHEET_NODE, 0], "c1 is not the REFSHEET child (ref_image_1 = sheet)"
    assert g0[C1]["inputs"]["ref_image_size"] == "max", "c1 ref_image_size is not max"
    assert g0[SHEET_NODE]["class_type"] == "LoadImage" and g0[SHEET_NODE]["inputs"] == {"image": SHEET_IMG}
    assert g0["img"]["inputs"]["image"] == START_STILL
    p0 = g0[C0]["inputs"]["prompt"]
    assert hashlib.sha256(p0.encode()).hexdigest() == BASE_C0_SHA, "c0 prompt is not the base segment-1 chunk-1 text"
    assert sha256_eol_normalized_text(BASE_C0_TXT) == BASE_C0_SHA, "base seg1 c0 sidecar hash moved; provenance re-check failed"
    print("base seg1 chunk-1 sidecar (EOL-normalised) sha256 %s = the graph's c0 prompt (raw-byte hash %s, the file is CRLF)"
          % (sha256_eol_normalized_text(BASE_C0_TXT)[:16] + "...", sha256(BASE_C0_TXT)[:16] + "..."))
    print("source arm ok: c0 = base seg1 chunk-1 text (sha %s..., %d chars), c1 = REFSHEET child, sheet node = %r"
          % (BASE_C0_SHA[:16], len(p0), SHEET_IMG))

    kw, nl, eol = dump_format(g0, raw)

    g = json.loads(jdump(g0))  # deep copy, key order/format neutral
    g[C0]["inputs"]["ref_images.ref_image_2"] = [SHEET_NODE, 0]
    g[C0]["inputs"]["ref_image_size"] = "max"
    g[C0]["inputs"]["prompt"] = new_prompt(p0)
    g[SAVE]["inputs"]["filename_prefix"] = "community/%s/%s" % (ARM, ARM)

    # ---- self-check: the diff is exactly the four listed deltas, nothing else ----
    assert set(g) == set(g0), "the node set changed (no new LoadImage is needed - the sheet node is reused)"
    untouched = 0
    for k in g0:
        if k in (C0, SAVE):
            continue
        assert jdump(g[k]) == jdump(g0[k]), "node %s changed - it must stay byte-identical to REFSHEET" % k
        untouched += 1
    d_c0 = {a for a in set(g[C0]["inputs"]) | set(g0[C0]["inputs"]) if g[C0]["inputs"].get(a) != g0[C0]["inputs"].get(a)}
    d_save = {a for a in set(g[SAVE]["inputs"]) | set(g0[SAVE]["inputs"]) if g[SAVE]["inputs"].get(a) != g0[SAVE]["inputs"].get(a)}
    assert d_c0 == {"ref_images.ref_image_2", "ref_image_size", "prompt"}, "c0 input deltas: %s" % sorted(d_c0)
    assert d_save == {"filename_prefix"}, "save delta: %s" % sorted(d_save)
    assert g[C0]["class_type"] == R2V and g[C0]["inputs"]["ref_images.ref_image_1"] == ["img", 0]
    assert g[C0]["inputs"]["ref_images.ref_image_2"] == [SHEET_NODE, 0]
    assert g[C0]["inputs"]["ref_image_size"] == "max"
    for a in ("clip", "vae", "audio_vae", "width", "height", "length"):
        assert jdump(g[C0]["inputs"][a]) == jdump(g0[C0]["inputs"][a]), "c0 %s moved" % a
    assert g[C0]["inputs"]["length"] == 243, "c0 length moved"
    assert g[C1]["inputs"]["prompt"] == g0[C1]["inputs"]["prompt"], "c1 prompt moved - chunk 2 stays exactly as in RS3"
    assert g["img"]["inputs"]["image"] == START_STILL, "the start still string moved"
    seeds = {n["inputs"]["noise_seed"] for n in g.values() if n["class_type"] == "RandomNoise"}
    assert seeds == {SEED}, "seed moved: %s" % seeds
    assert g["win1"]["inputs"]["extension_frames"] == 238 and g["win1"]["inputs"]["overlap_frames"] == 22, "win1 moved"
    print("nodes byte-identical to REFSHEET: %d of %d (only c0 and save move); c0 deltas %s; save delta %s"
          % (untouched, len(g0), sorted(d_c0), sorted(d_save)))
    print("c1 untouched: ref_image_1=%s ref_image_size=%s; seed %s; c0 length 243, extension 238, overlap 22"
          % (g[C1]["inputs"]["ref_images.ref_image_1"], g[C1]["inputs"]["ref_image_size"], SEED))

    # prompt provenance
    np = g[C0]["inputs"]["prompt"]
    assert np.startswith(NEW_BLOCK + "\n\n")
    assert np.endswith(p0.split("\n\n", 1)[1])
    open(os.path.join(NOTES, "ali147_refsheet_b_prompt_c0_new.txt"), "w", encoding="utf-8", newline="\n").write(np)
    print("new c0 prompt: %d -> %d chars (block %d + blank + unchanged tail %d); sha256 %s"
          % (len(p0), len(np), len(NEW_BLOCK), len(np) - len(NEW_BLOCK) - 2,
             hashlib.sha256(np.encode()).hexdigest()[:16] + "..."))
    print("  old block (removed, 2 lines): %s" % p0.split("\n")[1][:60] + " ...")

    for k, n in g.items():
        if isinstance(n["inputs"].get("prompt"), str):
            assert comm.guard_ok(n["inputs"]["prompt"]), "adults-only guard rejects %s" % k
    print("adults-only guard: all prompts pass")

    # placement, again at write time (read-only; nothing is copied here)
    print("LoadImage string %r resolves inside ComfyUI\\input: %s"
          % (SHEET_IMG, os.path.exists(os.path.join(COMFY_INPUT, SHEET_IMG.replace("/", os.sep)))))
    print("ComfyUI input tree RS016 matches: %d" % len(glob.glob(os.path.join(COMFY_INPUT, "**", "RS016*"), recursive=True)))

    os.makedirs(DST_DIR, exist_ok=True)
    txt = json.dumps(g, indent=1, sort_keys=True, **kw) + nl
    open(DST, "wb").write(txt.replace("\n", eol).encode("utf-8"))
    raw2, g2 = open(DST, "rb").read().decode("utf-8"), None
    g2 = json.loads(raw2)
    assert jdump(g2) == jdump(g), "written file does not parse back to the built graph"
    assert raw2 == txt.replace("\n", eol)
    print("WROTE %s (%d bytes, %d nodes, byte format identical to the REFSHEET file)" % (DST, len(raw2.encode("utf-8")), len(g2)))
    print("NO job request: p7\\JOB_REQUEST.json untouched (RS6 is the next line). Render count 0. sheet_sha256=%s" % sheet_sha[:16] + "...")
    print("ALL CHECKS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
