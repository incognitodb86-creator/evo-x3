#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ali27_review_loop_build.py - fix_plan 2.7: the unattended assembly half of
"approved stills -> clips -> a review cut for Derrick", written to ONE folder he can open,
with NO human step between the render output and the review folder.

No render, no GPU, no queue, no vision judge, no KEEP (KEEPWORD detector). The render segment
of the chain needs a GPU window (AGENTS.md + PROMPT 99999999), so this file emits
notes/ali27_window_plan.json for that window and NEVER writes p7/JOB_REQUEST.json, which
fix_plan 2.1b owns (one owner per artifact). CLOBBER pins that.

What is new vs 2.6 (notes/ali126_scene_cut_build.py, six hardcoded paths):
  * a SCANNER: every clip under ComfyUI/output/community, selected by shape, not by hand;
  * a PROVEN proof of the stills->clips chain by CONTENT HASH: a clip's graph is read
    (runs/<id>/<id>.api.json, gitignored, or p7/graphs/), its LoadImage inputs are hashed and
    matched byte-for-byte against the sha256 index of C:/Users/derek/5slock/approved_characters.
    A clip whose start still matches no approved still is EXCLUDED from the cut, with a reason.
  * the adults gate (scripts/comm.py guard_ok) over EVERY prompt-bearing string of each clip's
    graph, not only key `prompt` (the L11 key-scope gap); a graph that refuses excludes its clip;
  * a deterministic per-seed selection rule, recorded (no silent drop);
  * the adults gate over EVERY prompt-bearing string, and the receipt's own verdict: the manifest's problems/rc
    are re-measured by the CLAIMS detector, and --build takes the verdict AFTER every artifact is on disk, with the
    findings named in the receipt. Measured 2026-10-25 (fix_plan 1.4): the shipped order called check(m) BEFORE it
    wrote the table, so the receipt shipped problems=11 TABLE findings measured against the PREVIOUS build's table
    and stayed red for five passes while --check on the same folder read 0 - the per-pass review_folder_flags row
    reads the receipt, so every pass logged TEST_FAIL off a number that measured the builder's own write order.
    A verdict taken from a write order is not a measurement (L10).
  * a standing review folder + a per-pass gate (--check / --selftest).

Community method: the FFmpeg project's own concat page
https://trac.ffmpeg.org/wiki/Concatenate - concat demuxer + `-c copy` when every input shares
codec/parameters (equality is MEASURED here before the cut, not assumed). Saved body:
notes/web/07ff_trac_concat.html.

Usage:
  python notes/ali27_review_loop_build.py --scan      # lineage table to stdout
  python notes/ali27_review_loop_build.py --build     # cut + sheet + table + manifest
  python notes/ali27_review_loop_build.py --window    # the GPU window's queue (never queued here)
  python notes/ali27_review_loop_build.py --check     # re-measure off disk; PROBLEMS 0 VERDICT CLEAN
  python notes/ali27_review_loop_build.py --selftest  # seeded faults: all fire, 0 on the real tree
"""
import sys, os, re, json, copy, hashlib, importlib.util, subprocess
from pathlib import Path

FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
APPROVED = Path(r"C:/Users/derek/5slock/approved_characters")
COMFY_IN = Path(r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input")
COMFY_OUT = Path(r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output/community")
RUNS = Path(r"C:/AI/community/runs")
GRAPHS = Path(r"C:/AI/community/p7/graphs")
REQUEST = r"C:/AI/community/p7/JOB_REQUEST.json"          # owner = fix_plan 2.1b; never written here
REVIEW = Path(r"C:/AI/community/review/hc169")
MAN = Path(r"C:/AI/community/notes/ali27_review_loop_manifest.json")
WINDOW = Path(r"C:/AI/community/notes/ali27_window_plan.json")
COMM = Path(r"C:/AI/community/scripts/comm.py")
CITE = "https://trac.ffmpeg.org/wiki/Concatenate"
CITE_BODY = "notes/web/07ff_trac_concat.html"
CUT = "review_cut.mp4"
SHEET = "contact_sheet.png"
TABLE = "review_table.md"
CONCAT = "concat_list.txt"      # the concat demuxer list, kept so the cut is re-buildable by hand
THUMB_W, THUMB_H = 448, 256
CANVAS = (1344, 768)          # 16:9, both a multiple of 32 (AGENTS.md: 468 % 32 = 20 is unreachable)
FPS = "24/1"
MIN_WORDS = 6                 # "prompt-bearing string" = 6+ words, the 2.1b census rule
# word-boundary list: "keep" is NOT in it, because this file must state that Derrick picks the
# clips himself; every word here is an evaluation this builder is not allowed to make.
KEEPWORDS = ("best", "winner", "winning", "preferred", "superior", "greatest", "beautiful",
             "gorgeous", "excellent", "verdict", "ranking", "ranked", "scored", "quality")
WRITES = [str(REVIEW / CUT), str(REVIEW / SHEET), str(REVIEW / TABLE), str(MAN), str(WINDOW),
          str(REVIEW / "concat_list.txt")]   # the builder's whole write surface; CLOBBER checks this

def sh(args):
    return subprocess.run(args, capture_output=True, text=True, shell=False)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()

def probe(path):
    """Media facts BY FIELD NAME (-of json); the -of csv order is ffprobe's, not ours (AGENTS.md L8)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    v = json.loads(sh([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
                       "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_packets,duration",
                       "-of", "json", str(p)]).stdout)["streams"][0]
    a = json.loads(sh([FFPROBE, "-v", "error", "-select_streams", "a:0",
                       "-show_entries", "stream=codec_name,sample_rate,channels,duration",
                       "-of", "json", str(p)]).stdout).get("streams", [])
    fmt = json.loads(sh([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                         "-of", "json", str(p)]).stdout)["format"]
    st = p.stat()
    return {"path": p.as_posix(), "bytes": st.st_size, "mtime": int(st.st_mtime), "sha256": sha256(p),
            "fmt_dur": round(float(fmt.get("duration") or 0.0), 6), "vcodec": v.get("codec_name"),
            "w": int(v["width"]), "h": int(v["height"]), "fps": v.get("r_frame_rate"),
            "vpackets": int(v["nb_read_packets"]), "vdur": round(float(v.get("duration") or 0.0), 3),
            "acodec": (a[0].get("codec_name") if a else None),
            "asr": (int(a[0]["sample_rate"]) if a and a[0].get("sample_rate") else None),
            "ach": (int(a[0]["channels"]) if a and a[0].get("channels") else None)}

def load_guard():
    """Load scripts/comm.py by path (the adults gate; importing it opens no socket)."""
    spec = importlib.util.spec_from_file_location("forge_comm", str(COMM))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.guard_ok

def _approved_index():
    """sha256 -> approved relative paths, over every .jpg/.png under approved_characters."""
    idx = {}
    for f in sorted(APPROVED.rglob("*")):
        if f.is_file() and f.suffix.lower() in (".jpg", ".jpeg", ".png"):
            try:
                idx.setdefault(sha256(f), []).append(f.relative_to(APPROVED).as_posix())
            except OSError:
                pass
    return idx

def find_graph(cid):
    for cand in (RUNS / cid / (cid + ".api.json"), GRAPHS / (cid + ".api.json")):
        if cand.is_file():
            return cand
    return None

def graph_strings(g):
    """EVERY string input of 6+ words in a graph, across all keys (the L11 key-scope fix)."""
    out = []
    for node in g.values():
        for k, v in (node.get("inputs") or {}).items():
            if isinstance(v, str) and len(v.split()) >= MIN_WORDS:
                out.append((str(node.get("class_type", "?")) + "." + k, v))
    return out

def graph_scalars(g):
    seed = canvas = frames = None
    for node in g.values():
        for k, v in (node.get("inputs") or {}).items():
            if seed is None and k in ("noise_seed", "seed") and isinstance(v, (int, float)):
                seed = int(v)
            if k == "width" and isinstance(v, int):
                canvas = [v, None]
            if k == "height" and isinstance(v, int) and canvas and canvas[1] is None:
                canvas[1] = v
            if frames is None and k in ("frames", "length", "target_frames") and isinstance(v, int):
                frames = v
    return seed, canvas, frames


# scan() is the same measurement every mode needs, and --selftest runs check() once per seed (18x).
# A per-process memo keeps the gate rows inside their time budget; each subprocess still measures from
# disk, and the cached object is deep-copied out so no caller can mutate the shared rows.
_CACHE = {}

def approved_index():
    if "app" not in _CACHE:
        _CACHE["app"] = _approved_index()
    return _CACHE["app"]

def scan():
    if "scan" not in _CACHE:
        _CACHE["scan"] = _scan()
    return copy.deepcopy(_CACHE["scan"])

def _scan():
    """Lineage: approved-still hash index -> LoadImage in the clip's graph -> the clip's mp4."""
    guard = load_guard()
    app = approved_index()
    rows, dropped = [], []
    for d in sorted(COMFY_OUT.iterdir()):
        if not d.is_dir():
            continue
        cid = d.name
        mp4 = d / (cid + "_00001_.mp4")
        if not mp4.is_file():
            continue
        r = probe(mp4)
        r["id"] = cid
        if (r["w"], r["h"]) != CANVAS:
            dropped.append(dict(id=cid, reason="NOT_16x9 %dx%d" % (r["w"], r["h"])))
            continue
        if r["fps"] != FPS:
            dropped.append(dict(id=cid, reason="FPS " + str(r["fps"])))
            continue
        if not r["acodec"]:
            dropped.append(dict(id=cid, reason="NO_AUDIO"))
            continue
        gp = find_graph(cid)
        if gp is None:
            dropped.append(dict(id=cid, reason="GRAPH_GONE no proof of the start still"))
            continue
        g = json.loads(gp.read_text(encoding="utf-8"))
        seed, canvas, frames = graph_scalars(g)
        stills, approved, crops, viol = [], [], [], []
        for node in g.values():
            if node.get("class_type") == "LoadImage":
                name = (node.get("inputs") or {}).get("image")
                if not isinstance(name, str):
                    continue
                f = COMFY_IN / name.replace("\\", "/")
                if not f.is_file():
                    viol.append(name + " (input file absent)")
                    continue
                hit = app.get(sha256(f))
                if hit:
                    approved.append(hit[0])
                    stills.append({"input": name, "sha256": sha256(f), "approved": hit[0]})
                elif re.search(r"face|crop", name, re.I):
                    crops.append(name)      # BQ1 slots 2/3 = face crops, derived from a still (AGENTS.md L7)
                else:
                    viol.append(name)       # a full-frame reference that is not an approved still
        strs = graph_strings(g)
        refusals = sorted(set(k for k, v in strs if not guard(v)))
        row = dict(r)
        row.update(graph=gp.as_posix(), graph_src=("runs(gitignored)" if gp.parent == RUNS else "p7/graphs"),
                   seed=seed, graph_canvas=canvas, graph_frames=frames,
                   stills=stills, approved=approved, crops=crops, ref_violations=viol,
                   gate_strings=len(strs), gate_refusals=refusals)
        rows.append(row)
    # deterministic per-seed selection: the newest mtime is retained, tie -> last id in sorted order.
    by_seed, dupes = {}, []
    for r in sorted(rows, key=lambda x: (x["mtime"] or 0, x["id"])):
        s = r["seed"]
        if s in by_seed:
            dupes.append({"seed": s, "retained": r["id"], "dropped": by_seed[s],
                          "reason": "superseded by a newer render of the same seed"})
        by_seed[s] = r["id"]
    keep = set(by_seed.values())
    for r in rows:
        if r["id"] not in keep:
            dropped.append(dict(id=r["id"], reason="DUPE_SEED seed %s (retained %s)" % (r["seed"], by_seed[r["seed"]])))
    scene = sorted([r for r in rows if r["id"] in keep and r["approved"] and not r["ref_violations"]
                    and not r["gate_refusals"]], key=lambda x: ((x["seed"] if x["seed"] is not None else 0), x["id"]))
    excl = list(dropped)
    for r in rows:
        if r["id"] in keep and not (r["approved"] and not r["ref_violations"] and not r["gate_refusals"]):
            why = []
            if not r["approved"]:
                why.append("no approved start still in the graph (LoadImage slots: "
                           + ",".join(r["crops"] + r["ref_violations"]) + ")")
            if r["ref_violations"]:
                why.append("unapproved full-frame reference: " + ",".join(r["ref_violations"]))
            if r["gate_refusals"]:
                why.append("adults gate refused " + ",".join(r["gate_refusals"]))
            excl.append(dict(id=r["id"], reason="; ".join(why)))
    return {"canvas": list(CANVAS), "fps": FPS, "min_words": MIN_WORDS,
            "approved_images": sum(len(v) for v in app.values()),
            "approved_roots": len({p.split("/")[0] for v in app.values() for p in v}),
            "scene": scene, "excluded": sorted(excl, key=lambda x: (x["reason"], x["id"])),
            "dupe_resolution": sorted(dupes, key=lambda x: (str(x["seed"]), x["dropped"])),
            "order_rule": "per seed the newest mtime is retained (tie -> the last id in sorted order); "
                          "the scene is ordered by (seed, id)",
            "method": CITE, "method_body": CITE_BODY, "writes": WRITES,
            "comm": str(COMM), "approved_root": str(APPROVED)}

def sheet_layout(n):
    """Tile grid for n clips; returns (positions, extent). xstack's canvas is the max tile
    extent, not cols*W, so the sheet check must expect the extent the layout really produces."""
    c = 3 if n <= 9 else 4
    nrow = (n + c - 1) // c
    pos, k = [], 0
    for y in range(nrow):
        for x in range(c):
            if k < n:
                pos.append((x * THUMB_W, y * THUMB_H))
            k += 1
    ext = (max(p[0] for p in pos) + THUMB_W, max(p[1] for p in pos) + THUMB_H)
    return pos, ext

def cols_n(n):
    c = 3 if n <= 9 else 4
    return c, (n + c - 1) // c

def ffmpeg_concat(paths, out_path, mode):
    lst = REVIEW / "concat_list.txt"
    lst.write_text("".join("file '%s'\n" % p for p in paths), encoding="utf-8", newline="\n")
    args = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst.as_posix()]
    args += (["-c", "copy"] if mode == "copy" else
             ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "128k"])
    args += [out_path]
    r = sh(args)
    return r.returncode, (r.stderr or "")[-400:]

def make_sheet(rows):
    tdir = REVIEW / "thumbs"
    tdir.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for i, r in enumerate(rows):
        t = tdir / ("thumb_%02d.png" % i)
        rr = sh([FFMPEG, "-y", "-ss", str(round(r["vdur"] / 2.0, 3)), "-i", r["path"], "-frames:v", "1",
                 "-vf", "scale=%d:%d" % (THUMB_W, THUMB_H), "-an", t.as_posix()])
        if rr.returncode != 0:
            return None, (rr.stderr or "")[-300:]
        thumbs.append(t)
    c, nrow = cols_n(len(thumbs))
    pos, ext = sheet_layout(len(thumbs))
    layout = "|".join("%d_%d" % (x, y) for x, y in pos)
    ins = []
    for t in thumbs:
        ins += ["-i", t.as_posix()]
    fc = "[%s]xstack=inputs=%d:layout=%s[out]" % ("][".join(str(i) for i in range(len(thumbs))), len(thumbs), layout)
    rr = sh([FFMPEG, "-y"] + ins + ["-filter_complex", fc, "-map", "[out]", "-frames:v", "1",
                                    (REVIEW / SHEET).as_posix()])
    if rr.returncode != 0:
        return None, "xstack failed", None
    return REVIEW / SHEET, "xstack inputs=%d layout=%s" % (len(thumbs), layout), ext

def render_table(m):
    s = m["scene"]
    L = ["# review cut - fix_plan 2.7 (ali27) - objective numbers only", "",
         "Generated by `notes/ali27_review_loop_build.py --build`. Derrick picks the clips himself; this",
         "file carries measured numbers only (the gate rejects evaluative wording, 0 such words here).",
         "Method: %s (concat demuxer, `-c %s`), saved body %s." % (CITE, m["mode"], CITE_BODY), "",
         "Cut: `%s` - %dx%d, %s fps, %d packets, %.3f s, %s audio %s Hz %sch, %d bytes, sha256 %s." % (
             (REVIEW / CUT).as_posix(), m["out"]["w"], m["out"]["h"], m["out"]["fps"], m["out"]["vpackets"],
             m["out"]["vdur"], m["out"]["acodec"], m["out"]["asr"], m["out"]["ach"], m["out"]["bytes"],
             m["out"]["sha256"][:16]),
         "Contact sheet: `%s` (%dx%d px, %d tiles)." % ((REVIEW / SHEET).as_posix(),
             m["sheet"]["w"], m["sheet"]["h"], len(s)),
         "Order rule: %s." % m["order_rule"], "",
         "| # | clip | seed | approved start still (sha256 byte-match) | f | dur s | canvas | fps | audio | sha256-16 | gate strings |",
         "|--|-------|------|--------------------------------------|----|---------|--------|-----|-------|-----------|--------------|"]
    for i, r in enumerate(s):
        L.append("| %d | %s | %s | %s | %d | %.3f | %dx%d | %s | %s | %s | %d |" % (
            i + 1, r["id"], r["seed"], "<br>".join(r["approved"]), r["vpackets"], r["vdur"],
            r["w"], r["h"], r["fps"], "%s %s" % (r["acodec"], r["asr"]), r["sha256"][:16], r["gate_strings"]))
    L += ["", "Sum of clips: %d packets, %.3f s. Cut: %d packets, %.3f s (concat -c copy, no re-encode)." % (
        m["sum_vpackets"], m["sum_vdur"], m["out"]["vpackets"], m["out"]["vdur"]),
        "", "Excluded from the cut (measured, never dropped silently): %d" % len(m["excluded"])]
    for e in m["excluded"]:
        L.append("- `%s` - %s" % (e["id"], e["reason"]))
    if m["dupe_resolution"]:
        L += ["", "Per-seed selection (the rule, applied):"]
        for d in m["dupe_resolution"]:
            L.append("- seed %s: retained `%s`, dropped `%s` - %s" % (d["seed"], d["retained"], d["dropped"], d["reason"]))
    L.append("")
    return "\n".join(L)

def build():
    REVIEW.mkdir(parents=True, exist_ok=True)
    m = scan()
    s = m["scene"]
    if len(s) < 2:
        print("BUILD_FAIL scene has %d clips; nothing to cut" % len(s))
        return 2
    eq = {(r["w"], r["h"], r["fps"], r["vcodec"], r["acodec"], r["asr"], r["ach"]) for r in s}
    mode = "copy" if len(eq) == 1 else "reencode"
    out_path = (REVIEW / CUT).as_posix()
    rc, err = 1, ""
    for cand in ([mode] if mode == "copy" else ["copy", "reencode"]):
        rc, err = ffmpeg_concat([r["path"] for r in s], out_path, cand)
        if rc == 0:
            mode = cand
            break
    if rc != 0:
        print("BUILD_FAIL concat rc=%s %s" % (rc, err))
        return 2
    m["mode"] = mode
    m["out"] = probe(out_path)
    sheet, note, ext = make_sheet(s)
    if sheet is None:
        print("BUILD_FAIL sheet %s" % note)
        return 2
    m["sheet"] = probe(sheet.as_posix())
    m["sheet_note"] = note
    m["sheet_extent"] = list(ext)
    m["sum_vpackets"] = sum(r["vpackets"] for r in s)
    m["sum_vdur"] = round(sum(r["vdur"] for r in s), 3)
    m["table"] = str(REVIEW / TABLE)
    # Write every artifact FIRST (manifest with problems/rc = "PENDING", which claims nothing), then take the
    # verdict with the same check() that --check runs - on the disk state - and only then write it into the
    # receipt, naming every finding. See the header: the shipped order measured before the table existed.
    m["findings"] = []
    m["problems"] = "PENDING"
    m["rc"] = "PENDING"
    MAN.write_text(json.dumps(m, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    (REVIEW / TABLE).write_text(render_table(m), encoding="utf-8", newline="\n")
    P = check()
    m["findings"] = P
    m["problems"] = len(P)
    m["rc"] = 0 if not P else 1
    MAN.write_text(json.dumps(m, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print("BUILT mode=%s clips=%d cut=%s f=%d dur=%.3f %dx%d bytes=%d sheet=%dx%d" % (
        mode, len(s), m["out"]["path"], m["out"]["vpackets"], m["out"]["vdur"], m["out"]["w"],
        m["out"]["h"], m["out"]["bytes"], m["sheet"]["w"], m["sheet"]["h"]))
    for p in P:
        print("PROBLEM " + p)
    print("VERDICT problems=%d %s manifest=%s" % (len(P), "CLEAN" if not P else "RED", MAN.as_posix()))
    return 0 if not P else 1

def window_plan():
    """The GPU window's queue: every graph on disk whose clip is not in the review scene, with reason.
    This file NEVER queues and NEVER writes p7/JOB_REQUEST.json (owner = fix_plan 2.1b)."""
    m = scan()
    in_scene = {r["id"] for r in m["scene"]}
    excl = {e["id"]: e["reason"] for e in m["excluded"]}
    rows = []
    for base in (RUNS, GRAPHS):
        if not base.is_dir():
            continue
        for gp in sorted(base.rglob("*.api.json")):
            cid = gp.name[:-len(".api.json")]
            mp4 = COMFY_OUT / cid / (cid + "_00001_.mp4")
            if cid in in_scene:
                continue
            g = json.loads(gp.read_text(encoding="utf-8"))
            seed, canvas, frames = graph_scalars(g)
            rows.append({"id": cid, "graph": gp.as_posix(), "seed": seed, "canvas": canvas,
                         "frames": frames, "mp4": mp4.is_file(),
                         "reason": excl.get(cid, ("mp4 absent - render it in a GPU window"
                                                  if not mp4.is_file() else "not in the 16:9 review scene"))})
    out = {"note": "for a GPU render window only; this builder never queues, never calls ComfyUI/llama-swap, "
                   "and never writes " + REQUEST,
           "window_jobs": sorted(rows, key=lambda x: x["id"]), "scene_clips": sorted(in_scene)}
    WINDOW.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    print("WINDOW jobs=%d scene_clips=%d -> %s (queued by a window, not by this file)" % (
        len(rows), len(in_scene), WINDOW.as_posix()))
    return 0

# ---------------- checks: every claim is re-measured off disk, never trusted ----------------
def check(m=None):
    P = []
    m = m or json.loads(MAN.read_text(encoding="utf-8"))
    live = scan()
    s = m["scene"]
    ids = [r["id"] for r in s]
    if len(ids) < 2:
        P.append("MISSING scene has %d clips" % len(ids))
    # 1 MISSING + 2 SHA + 3 CANVAS/AUDIO on every input, on the CLAIMS and on the DISK probe
    eq, eqc = set(), set()
    for r in s:
        eqc.add((r["w"], r["h"], r["fps"], r["vcodec"], r["acodec"], r["asr"], r["ach"]))
        if not r["acodec"]:
            P.append("AUDIO %s manifest row carries no audio stream" % r["id"])
        if not Path(r["path"]).is_file():
            P.append("MISSING %s %s" % (r["id"], r["path"]))
            continue
        p = probe(r["path"])
        for k in ("sha256", "bytes", "vpackets", "vdur", "w", "h", "fps", "vcodec", "acodec"):
            if p[k] != r[k]:
                P.append("SHA/MEASURE %s %s claim=%s disk=%s" % (r["id"], k, r.get(k), p[k]))
        if not p["acodec"]:
            P.append("AUDIO %s has no audio stream (the 2.7 goal is clips WITH audio)" % r["id"])
        eq.add((p["w"], p["h"], p["fps"], p["vcodec"], p["acodec"], p["asr"], p["ach"]))
        if (p["w"], p["h"]) != tuple(m["canvas"]) or p["fps"] != m["fps"]:
            P.append("CANVAS %s %dx%d %s != %s %s" % (r["id"], p["w"], p["h"], p["fps"],
                                                       "%dx%d" % CANVAS, FPS))
    if len(eq) > 1:
        P.append("CANVAS inputs are not parameter-identical on disk, so concat -c copy is invalid: %r" % (sorted(eq, key=repr),))
    if len(eqc) > 1:
        P.append("CANVAS manifest rows are not parameter-identical: %r" % (sorted(eqc, key=repr),))
    # 4 DUPE: the scene must carry one clip per seed (the selection rule resolved it)
    seeds = [r["seed"] for r in s]
    if len(set(seeds)) != len(seeds) or None in seeds:
        P.append("DUPE scene has %d clips over %d seeds" % (len(s), len(set(seeds))))
    # 5 APPROVAL: re-derive the hash join from disk, do not trust the manifest
    app = approved_index()
    for r in s:
        try:
            g = json.loads(Path(r["graph"]).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            P.append("MISSING graph %s for %s (provenance cannot be re-derived)" % (r["graph"], r["id"]))
            continue
        live_app, live_bad = [], []
        for node in g.values():
            if node.get("class_type") == "LoadImage":
                nm = (node.get("inputs") or {}).get("image")
                f = COMFY_IN / str(nm).replace("\\", "/")
                hit = app.get(sha256(f)) if f.is_file() else None
                if hit:
                    live_app.append(hit[0])
                elif not re.search(r"face|crop", str(nm), re.I):
                    live_bad.append(str(nm))
        if not live_app or live_bad:
            P.append("APPROVAL %s approved=%r ref_violations=%r" % (r["id"], live_app, live_bad))
        if sorted(live_app) != sorted(r["approved"]):
            P.append("APPROVAL %s manifest %r != disk %r" % (r["id"], sorted(r["approved"]), sorted(live_app)))
        # 6 GATE: re-run the adults gate over EVERY prompt-bearing string
        guard = load_guard()
        strs = graph_strings(g)
        ref = sorted(set(k for k, v in strs if not guard(v)))
        if ref:
            P.append("GATE %s adults gate refused %r" % (r["id"], ref))
        if len(strs) == 0:
            P.append("GATE %s graph exposes 0 prompt-bearing strings, nothing was gated" % r["id"])
    # 7 MATH + SHA + CANVAS on the cut; 8 STALE
    cut = Path(m["out"]["path"]) if m.get("out") else REVIEW / CUT
    if not cut.is_file():
        P.append("MISSING cut %s" % cut)
    else:
        c = probe(cut)
        for k in ("sha256", "bytes", "vpackets", "vdur", "w", "h", "fps", "acodec"):
            if m["out"][k] != c[k]:
                P.append("SHA/MEASURE cut %s claim=%s disk=%s" % (k, m["out"].get(k), c[k]))
        if c["vpackets"] != m["sum_vpackets"]:
            P.append("MATH cut packets %d != sum of clips %d" % (c["vpackets"], m["sum_vpackets"]))
        if abs(c["vdur"] - m["sum_vdur"]) > 0.5:
            P.append("MATH cut duration %.3f != sum of clips %.3f" % (c["vdur"], m["sum_vdur"]))
        if c["w"] != CANVAS[0] or c["h"] != CANVAS[1] or c["fps"] != FPS:
            P.append("CANVAS cut %dx%d %s" % (c["w"], c["h"], c["fps"]))
        if not c["acodec"]:
            P.append("AUDIO cut has no audio stream")
        if m["mode"] == "copy" and c["vcodec"] != s[0]["vcodec"]:
            P.append("CANVAS mode=copy but the cut codec %s != inputs %s" % (c["vcodec"], s[0]["vcodec"]))
        newest = max([r["mtime"] for r in s] + [0])
        if c["mtime"] < newest:
            P.append("STALE cut mtime %d < newest input mtime %d (folder is not built from current clips)" % (c["mtime"], newest))
        if int(m["out"].get("mtime") or 0) < newest:
            P.append("STALE manifest claims a cut mtime %s older than its newest input %d" % (
                m["out"].get("mtime"), newest))
    # 9 SHEET: tiles == clips, and the px == the extent the tile layout really produces
    pos, ext = sheet_layout(len(s))
    if not Path(m["sheet"]["path"]).is_file():
        P.append("MISSING sheet %s" % m["sheet"]["path"])
    else:
        p = probe(m["sheet"]["path"])
        if (p["w"], p["h"]) != tuple(ext):
            P.append("SHEET %dx%d != tile-grid extent %dx%d for %d tiles" % (
                p["w"], p["h"], ext[0], ext[1], len(s)))
        if list(m.get("sheet_extent") or []) != list(ext):
            P.append("SHEET manifest extent %r != %r for %d tiles" % (m.get("sheet_extent"), list(ext), len(s)))
    # 10 TABLE: rows == clips and the bytes on disk equal the manifest's table
    tab = Path(m["table"])
    if not tab.is_file():
        P.append("MISSING table %s" % tab)
    else:
        txt = tab.read_text(encoding="utf-8")
        n = sum(1 for ln in txt.split("\n") if ln.startswith("| ") and ".mp4" not in ln and "clip" not in ln.split("|")[1])
        body = [ln for ln in txt.split("\n") if ln.startswith("| ") and ln.split("|")[1].strip().isdigit()]
        if len(body) != len(s):
            P.append("TABLE %d data rows != %d clips" % (len(body), len(s)))
        for r in s:
            if r["id"] not in txt:
                P.append("TABLE clip %s not named in the table" % r["id"])
        if txt != render_table(m):
            P.append("TABLE table bytes != render_table(manifest) (stale doc)")
    # 11 KEEPWORD: no verdict words in the durable text. `findings` is detector OUTPUT, not prose about a clip, and
    # the KEEPWORD finding's own sentence contains "verdict", so a self-reference would be permanent red (L10).
    blob = (json.dumps({k: v for k, v in m.items() if k not in ("scene", "excluded", "findings")}) +
            (tab.read_text(encoding="utf-8") if tab.is_file() else "")).lower()
    hits = sorted({w for w in KEEPWORDS if re.search(r"\b%s\b" % w, blob)})
    if hits:
        P.append("KEEPWORD verdict words in the durable text %r (KEEP is Derrick's alone)" % (hits,))
    # 12 CLOBBER: the builder's write surface must never include the 2.1b request artifact
    if REQUEST in list(m.get("writes", [])) + [str(x) for x in m.get("writes", [])]:
        P.append("CLOBBER builder write surface includes %s (owner = fix_plan 2.1b)" % REQUEST)
    # 14 LITTER: the standing folder is Derrick's surface, so only the artifacts may live in it.
    # The selftest writes probe files, and a per-pass gate that litters the human folder is a defect (found
    # 2026-10-24: two probe files survived a gate run), so this class is probed, not promised.
    allow = {CUT, SHEET, TABLE, CONCAT, "thumbs"}
    litter = sorted(x.name for x in REVIEW.iterdir() if x.name not in allow)
    if litter:
        P.append("LITTER %s in %s (only the cut, sheet, table, concat list and thumbs belong here)" % (
            ",".join(litter), REVIEW.as_posix()))

    # 13 ORDER: order is a function of (seed, id) only, never of scan order. A rotation of the
    # disk rows, re-sorted by the documented key, must land back on the manifest order.
    perm = live["scene"][1:] + live["scene"][:1]
    resort = sorted(perm, key=lambda r: ((r["seed"] if r["seed"] is not None else 0), r["id"]))
    if [r["id"] for r in resort] != ids:
        P.append("ORDER scene order is not reproducible from a re-ordered input list")
    if [r["id"] for r in live["scene"]] != ids:
        P.append("ORDER manifest order %r != disk order %r" % (ids, [r["id"] for r in live["scene"]]))
    # 15 CLAIMS: the receipt's verdict must equal THIS measurement. base = the findings before the self-claim check,
    # so the detector is idempotent. A "PENDING" claim makes no claim (--build's intermediate write).
    def _claim(v):
        return v if isinstance(v, int) and not isinstance(v, bool) else None
    base = list(P)
    want_rc = 0 if not base else 1
    if _claim(m.get("problems")) is not None and _claim(m.get("problems")) != len(base):
        P.append("CLAIMS the manifest says problems=%s and this measurement makes %d: %r" % (
            m.get("problems"), len(base), base[:2]))
    if _claim(m.get("rc")) is not None and _claim(m.get("rc")) != want_rc:
        P.append("CLAIMS the manifest says rc=%s and this measurement makes rc=%d" % (m.get("rc"), want_rc))
    return P

def render_check(m):
    return check(m)

def check_main():
    m = json.loads(MAN.read_text(encoding="utf-8"))
    P = check(m)
    print("clips=%d packets=%d dur=%.3f mode=%s approved_imgs=%d excluded=%d dupes=%d" % (
        len(m["scene"]), m["sum_vpackets"], m["sum_vdur"], m["mode"], m["approved_images"],
        len(m["excluded"]), len(m["dupe_resolution"])))
    for r in m["scene"]:
        print("  %-34s seed=%s %dx%d f=%d %.3fs %s sha=%s approved=%s" % (
            r["id"], r["seed"], r["w"], r["h"], r["vpackets"], r["vdur"], r["acodec"],
            r["sha256"][:16], ",".join(Path(a).name for a in r["approved"])))
    for p in P:
        print("PROBLEM " + p)
    print("PROBLEMS %d VERDICT %s" % (len(P), "CLEAN" if not P else "RED"))
    return 0 if not P else 1

# ---------------- seeded faults: each must fire on a clone and stay silent on the real tree ----------------
def seeds(m):
    """Yield (name, mutated_manifest, expected_token). Each fault is a real fault class."""
    out = []
    d = copy.deepcopy(m)
    d["scene"][0]["path"] = (COMFY_OUT / "no_such_clip_xyz" / "no_such_clip_xyz_00001_.mp4").as_posix()
    out.append(("MISSING", d, "MISSING"))
    d = copy.deepcopy(m)
    d["scene"][1]["sha256"] = "0" * 64
    out.append(("SHA_CLIP", d, "SHA/MEASURE"))
    d = copy.deepcopy(m)
    d["out"]["sha256"] = "0" * 64
    out.append(("SHA_CUT", d, "SHA/MEASURE"))
    d = copy.deepcopy(m)
    d["sum_vpackets"] = d["sum_vpackets"] + 7
    out.append(("MATH_PACKETS", d, "MATH"))
    d = copy.deepcopy(m)
    d["sum_vdur"] = d["sum_vdur"] + 30.0
    out.append(("MATH_DURATION", d, "MATH"))
    d = copy.deepcopy(m)
    d["scene"][0]["w"] = 1024
    d["scene"][0]["h"] = 576
    out.append(("CANVAS_MIXED", d, "CANVAS"))
    d = copy.deepcopy(m)
    d["scene"][0]["acodec"] = None
    out.append(("AUDIO_STRIPPED", d, "AUDIO"))
    d = copy.deepcopy(m)
    d["scene"][0]["approved"] = ["MADE_UP/Fake.jpg"]
    out.append(("APPROVAL_FABRICATED", d, "APPROVAL"))
    d = copy.deepcopy(m)
    g = json.loads(Path(d["scene"][0]["graph"]).read_text(encoding="utf-8"))
    for nid, node in g.items():
        if node.get("class_type") == "LoadImage":
            node["inputs"]["image"] = "community/hc/HC1_w1_blonde_00001_.png"
            break
    Path(REVIEW / "ali27_ref_probe.api.json").write_text(json.dumps(g), encoding="utf-8", newline="\n")
    d["scene"][0]["graph"] = str(REVIEW / "ali27_ref_probe.api.json")
    out.append(("APPROVAL_REF_VIOLATION", d, "APPROVAL"))
    d = copy.deepcopy(m)
    d["scene"][1]["seed"] = d["scene"][0]["seed"]
    out.append(("DUPE_SEED", d, "DUPE"))
    d = copy.deepcopy(m)
    d["sheet"]["path"] = (REVIEW / "no_sheet_xyz.png").as_posix()
    out.append(("SHEET_MISSING", d, "MISSING"))
    d = copy.deepcopy(m)
    d["sheet_extent"] = [d["sheet_extent"][0] + THUMB_W, d["sheet_extent"][1]]
    out.append(("SHEET_EXTENT", d, "SHEET"))
    d = copy.deepcopy(m)
    d["table"] = str(REVIEW / "review_table.md") + ".xyz"
    out.append(("TABLE_MISSING", d, "MISSING"))
    d = copy.deepcopy(m)
    dtxt = Path(REVIEW / TABLE).read_text(encoding="utf-8") + "\nthe best take, a winner and a ranking\n"
    Path(REVIEW / "ali27_keepword_probe.md").write_text(dtxt, encoding="utf-8", newline="\n")
    d["table"] = str(REVIEW / "ali27_keepword_probe.md")
    out.append(("KEEPWORD", d, "KEEPWORD"))
    d = copy.deepcopy(m)
    d["out"]["mtime"] = 0
    out.append(("STALE_CUT", d, "STALE"))
    (REVIEW / "ali27_litter_probe.txt").write_text("selftest litter" + chr(10), encoding="utf-8",
                                                   newline="" + chr(10))
    out.append(("LITTER", copy.deepcopy(m), "LITTER"))
    d = copy.deepcopy(m)
    d["writes"] = list(d["writes"]) + [REQUEST]
    out.append(("CLOBBER_REQUEST", d, "CLOBBER"))
    d = copy.deepcopy(m)
    d["scene"] = list(reversed(d["scene"]))
    out.append(("ORDER_DRIFT", d, "ORDER"))
    d = copy.deepcopy(m)
    d["scene"] = d["scene"][:1]
    out.append(("TABLE_ROWS", d, "TABLE"))
    # CLAIMS: the receipt's own verdict, in both directions. The first seed IS the shipped 2026-10-25 fault: a clean
    # folder whose receipt claims problems=11 (the builder measured before writing its own table). The second is a
    # green claim on a red artifact - the class L10 names.
    d = copy.deepcopy(m)
    d["problems"] = 11
    d["rc"] = 1
    out.append(("CLAIMS_INFLATED", d, "CLAIMS"))
    d = copy.deepcopy(m)
    d["out"]["mtime"] = 0            # a real fault: STALE fires, so a 0/0 claim on it is a false green
    d["problems"] = 0
    d["rc"] = 0
    out.append(("CLAIMS_GREEN_ON_RED", d, "CLAIMS"))
    return out

def selftest():
    m = json.loads(MAN.read_text(encoding="utf-8"))
    fired, silent = [], []
    nseed = len(seeds(m))          # count FIRST: seeds() writes two probe files into the review folder
    for name, mut, token in seeds(m):
        P = check(mut)
        if name == "LITTER":
            (REVIEW / "ali27_litter_probe.txt").unlink(missing_ok=True)
        if any(p.startswith(token) for p in P):
            fired.append(name)
        else:
            silent.append((name, P[:2]))
    # the probe files seeds() writes are selftest litter: the review folder is the human surface, so
    # nothing but the three artifacts + thumbs may live there. Counted before, removed before the real-tree
    # check, so the real-tree verdict measures the folder this run leaves behind (LITTER caught 2 files
    # that a gate run left there on 2026-10-24).
    for f in REVIEW.glob("ali27_*probe*"):
        f.unlink()
    real = check(m)
    print("SELFTEST_CLEAN seeds=%d fired=%d silent=%d real_tree_problems=%d" % (
        nseed, len(fired), len(silent), len(real)))
    for n, P in silent:
        print("SILENT %s -> %r" % (n, P))
    for p in real:
        print("REAL %s" % p)
    print("fired: " + ",".join(fired))
    return 0 if (not silent and not real) else 1

def scan_main():
    m = scan()
    print("approved images=%d roots=%d clips_16x9_with_audio=%d scene=%d excluded=%d dupes=%d" % (
        m["approved_images"], m["approved_roots"], len(m["scene"]) + len(m["excluded"]),
        len(m["scene"]), len(m["excluded"]), len(m["dupe_resolution"])))
    for r in m["scene"]:
        print("  KEEP %-34s seed=%s %dx%d f=%d %.3fs gate=%d approved=%s" % (
            r["id"], r["seed"], r["w"], r["h"], r["vpackets"], r["vdur"], r["gate_strings"],
            ",".join(Path(a).name for a in r["approved"])))
    for e in m["excluded"]:
        print("  OUT  %-34s %s" % (e["id"], e["reason"]))
    for d in m["dupe_resolution"]:
        print("  DUPE seed=%s retained=%s dropped=%s" % (d["seed"], d["retained"], d["dropped"]))
    return 0

if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "--scan"
    sys.exit({"--scan": scan_main, "--build": build, "--check": check_main,
              "--window": window_plan, "--selftest": selftest}.get(a, scan_main)())
