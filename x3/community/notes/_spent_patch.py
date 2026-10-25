"""Patch the TOP builder so a spent TOP id carries a measured render receipt instead of an unrendered claim.

Measured facts (this pass, off disk):
  C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output/community/ali163_hc15_gi046_s51150031/
      ali163_hc15_gi046_s51150031_00001_.mp4  8087674 B  2026-10-25 04:04  1344x768 24/1 362 f
      sha256 ade76d01fabd94e5d60f40f4be0cf3b5c9d1488bf274b54afa46861b51e9e7e4
  p7/jobs/ali163_hc15_gi046_s51150031.result.json is ABSENT; runs/<id>/status.log ends in poll-warn
  timeouts 04:15-04:23 CT. The graph's prose was rewritten for card fidelity AFTER that render, so the
  mp4 is not a render of the current prose record; take B (ali163_hc15_gi046_s51150032) is the free id
  for the GI046 still, so the armed pair becomes GI046 take B then GI063 take A (Max's row-18 order
  holds: GI046 first).
"""
P = r"C:/AI/community/notes/hc15_anchor_carry_build.py"
src = open(P, encoding="utf-8").read()

REC = '''
def top_render_receipt(nid):
    """the disk truth about a TOP id: the video ComfyUI wrote, measured (bytes, sha256, stamp). None = the
    id is free. A manifest of a spent id has to carry this receipt and stop calling itself id-free."""
    d = os.path.join(COMFY_OUT, nid)
    if not os.path.isdir(d):
        return None
    vids = sorted(f for f in os.listdir(d) if f.lower().endswith((".mp4", ".webm", ".gif", ".png")))
    if not vids:
        return None
    p = os.path.join(d, vids[0])
    st = os.stat(p)
    return {"file": p.replace("\\\\", "/"), "bytes": st.st_size, "sha256": sha(p),
            "written": time.strftime("%Y-%m-%d %H:%M:%S CT", time.localtime(st.st_mtime)),
            "queue_result": os.path.isfile(os.path.join(JOBS, nid + ".result.json"))}


def note_of(m):
    return str((m or {}).get("note", ""))


def arm_armed(m):
    return bool(((m or {}).get("arm") or {}).get("armed"))


def top_note(nid, g, m, f):'''

IDFREE_OLD = '''def ck_idfree(g, ctx):
    out = []
    nid = ctx["id"]
'''

IDFREE_NEW = '''def ck_idfree(g, ctx):
    """an unrendered id only: no mp4, no result.json, no ComfyUI output dir. A TOP id whose render is
    DECLARED (TOP_RENDERS) and byte-matches the manifest receipt is spent-on-the-record: it carries a
    render receipt (ck_top_manifest verifies it), so id-free is not the property it claims. A declared
    render whose receipt does not match the video on disk is a FAIL, and a spent id never gets armed."""
    nid = ctx["id"]
    if ctx.get("top") and nid in TOP_RENDERS:
        rec = top_render_receipt(nid)
        man = json.load(open(man_path(nid), encoding="utf-8")) if os.path.isfile(man_path(nid)) else {}
        mr = man.get("rendered") or {}
        if rec and all(mr.get(k) == rec[k] for k in ("file", "bytes", "sha256", "written")):
            return []
        return ["IDFREE %s is a declared render (TOP_RENDERS) and the manifest receipt %s does not match "
                "the video on disk %s" % (nid, mr, rec)]
    out = []
'''

MAN_OLD = '''    mp4, res, out_dir = (os.path.join(RUNS, ctx["id"], ctx["id"] + ".mp4"),
                         os.path.join(JOBS, ctx["id"] + ".result.json"), os.path.join(COMFY_OUT, ctx["id"]))
    if os.path.isfile(mp4) or os.path.isfile(res) or os.path.isdir(out_dir):
        out.append(f"TOP-MANIFEST claims an unrendered id, and it is spent (mp4 {os.path.isfile(mp4)}, "
                   f"result {os.path.isfile(res)}, output dir {os.path.isdir(out_dir)})")
'''

MAN_NEW = '''    mp4, res, out_dir = (os.path.join(RUNS, ctx["id"], ctx["id"] + ".mp4"),
                         os.path.join(JOBS, ctx["id"] + ".result.json"), os.path.join(COMFY_OUT, ctx["id"]))
    rec, mr = top_render_receipt(ctx["id"]), m.get("rendered")
    if rec:
        # spent: the receipt must be on the manifest, true off disk, declared, and never armed
        if ctx["id"] not in TOP_RENDERS:
            out.append("TOP-MANIFEST %s is rendered (a video is in the output dir) with no declared render "
                       "row in TOP_RENDERS: a manifest cannot call a spent id staged" % ctx["id"])
        if not isinstance(mr, dict) or any(mr.get(k) != rec[k] for k in ("file", "bytes", "sha256", "written")):
            out.append("TOP-MANIFEST render receipt %s != the video on disk %s (bytes/sha256/stamp are "
                       "measured, so a receipt cannot be softer than the file)" % (mr, rec))
        elif mr.get("prose") != TOP_RENDERS.get(ctx["id"], {}).get("prose"):
            out.append("TOP-MANIFEST render receipt does not state which prose the render ran (the "
                       "before/after rule: a render row names the prose it renders)")
        if isinstance(mr, dict) and not str(mr.get("keep", "")).strip():
            out.append("TOP-MANIFEST render receipt must state that KEEP is Derrick's alone")
        if arm_armed(m):
            out.append("TOP-MANIFEST arms %s and it is spent - the request must carry a free id" % ctx["id"])
        if str(rec["bytes"]) not in note_of(m):
            out.append("TOP-MANIFEST note does not quote the spent render (mp4 bytes) the manifest carries")
    elif os.path.isfile(mp4) or os.path.isfile(res) or os.path.isdir(out_dir):
        out.append(f"TOP-MANIFEST claims an unrendered id, and it is spent (mp4 {os.path.isfile(mp4)}, "
                   f"result {os.path.isfile(res)}, output dir {os.path.isdir(out_dir)})")
    elif mr:
        out.append("TOP-MANIFEST carries a render receipt %s and the id is free on disk" % mr)
'''

PAIRS = [
    ("import sys\n", "import sys\nimport time\n"),
    (
        'TOP_ORDER = [TOP["GI046"]["take_a"], TOP["GI063"]["take_a"]]      # the arm: take A of each named still, in order',
        '# The arm is the two FREE ids in Max\'s row-18 order (GI046 first). GI046 take A is spent (see\n'
        '# TOP_RENDERS), so the GI046 slot in the queue is take B; GI063 take A is free.\n'
        'TOP_ORDER = [TOP["GI046"]["take_b"], TOP["GI063"]["take_a"]]\n'
        '# A TOP id is spent the moment the ComfyUI output dir carries a video. The row below is the declared\n'
        '# statement about WHICH prose that render ran; file/bytes/sha256/stamp are measured off disk by\n'
        '# top_render_receipt(), so a receipt cannot be softer than the file (L10). KEEP stays Derrick\'s.\n'
        'TOP_RENDERS = {TOP["GI046"]["take_a"]: {\n'
        '    "prose": "the shipped pre-card-fidelity prose: the record was rewritten by TOP-SCENE on 2026-10-27 "\n'
        '             "and this mp4 predates the rewrite, so it is NOT a render of the current prose record",\n'
        '    "keep": "KEEP is Derrick\'s alone; no vision judge, no score, no keep by the forge",\n'
        '    "shape": "1344x768 24/1 362 f measured by ffprobe -select_streams v:0",\n'
        '    "queue": "p7/jobs/<id>.result.json is absent and runs/<id>/status.log ends in poll-warn timeouts "\n'
        '             "04:15-04:23 CT: the id is spent by file evidence, not by a queue receipt",\n'
        '    "record": "notes/needs_derrick.md row 25"}}'
    ),
    ("def top_note(nid, g, m, f):", REC),
    (IDFREE_OLD, IDFREE_NEW),
    (MAN_OLD, MAN_NEW),
]

for old, new in PAIRS:
    n = src.count(old)
    assert n == 1, ("anchor count", n, old[:80])
    src = src.replace(old, new, 1)

open(P, "w", encoding="utf-8", newline="\n").write(src)
print("patched: TOP_ORDER/TOP_RENDERS + top_render_receipt + ck_idfree + ck_top_manifest receipt rules")
