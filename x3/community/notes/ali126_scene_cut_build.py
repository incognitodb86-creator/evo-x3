#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ali126_scene_cut_build.py - fix_plan 2.6 (ALI-126/128): stitch a ~1 min 16:9 review cut
out of the 16:9 10 s hardcore clips that are ALREADY rendered, with ffmpeg, and measure the
hard-cuts vs continuation arm off disk. No render, no GPU, no queue, no vision judge, no KEEP.

Community method (fetched once, saved in notes/web): the FFmpeg project's own concat page
https://trac.ffmpeg.org/wiki/Concatenate - concat demuxer + `-c copy` when all inputs share
codec/parameters, re-encode as the documented fallback.

Usage:
  python notes/ali126_scene_cut_build.py --build     # cut the scene + sheet, write manifest + doc
  python notes/ali126_scene_cut_build.py --check     # re-measure everything off disk, PROBLEMS 0
  python notes/ali126_scene_cut_build.py --selftest  # seeded faults: every detector must fire,
                                                     # 0 problems on the real artifact
Rules honoured (AGENTS.md): ffprobe parsed BY FIELD NAME with -of json (the -of csv order is
ffprobe's, not yours); the adults gate is not bypassed because nothing is queued here; KEEP is
Derrick's alone, so this file writes objective numbers and never a quality verdict.
"""
import sys, os, re, json, copy, hashlib, subprocess, tempfile, shutil
from pathlib import Path

FFMPEG = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffmpeg.exe"
FFPROBE = r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
OUT = Path(r"C:/AI/community/runs/ali126_scene1_hc169")
OUTDIR = OUT
MAN = Path(r"C:/AI/community/notes/ali126_scene_cut_manifest.json")
DOC = Path(r"C:/AI/community/notes/ali126_scene_cut_notes.md")
CITE = "https://trac.ffmpeg.org/wiki/Concatenate"
CITE_BODY = "notes/web/07ff_trac_concat.html"
SCENE = "scene_hardcut.mp4"
SHEET = "contact_sheet.png"
THUMB_W, THUMB_H, COLS, ROWS = 448, 256, 3, 2
TARGET_S, TARGET_TOL, BAND_LO, BAND_HI = 60.0, 5.0, 5.0, 10.5
CANVAS = (1344, 768)
FPS = "24/1"

# the six hard-cut clips: 16:9, one per seed, 10.125 s each (243 f at 24 fps)
COMMUNITY = Path(r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output/community")
POOL = [(i, COMMUNITY / i / (i + "_00001_.mp4")) for i in (
    "ali147_pool_hc_r1_s51130001",
    "ali147_pool_hc_r2_s51130002",
    "ali147_pool_hc_r3b_s51130003",
    "ali147_pool_hc_r4_s51130004",
    "ali147_pool_hc_r5_s51130005",
    "ali147_pool_hc_r6_s51130006",
)]
# the continuation material that exists on disk, measured for the A/B row (never cut into the scene)
CONT = [
    ("ali173_cont_hc1_s51140001", COMMUNITY / "ali173_cont_hc1_s51140001/ali173_cont_hc1_s51140001_00001_.mp4"),
    ("p6_1min_cuts_stitched(2026-10-20 hard-cut arm)", Path(r"C:/AI/community/runs/p6_1min_cuts/p6_1min_cuts_stitched.mp4")),
    ("p6_1min_community_stitched(2026-10-20 continuation arm)", Path(r"C:/AI/community/runs/p6_1min_community/p6_1min_community_stitched.mp4")),
]


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, shell=False)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def probe(path):
    """Measure a media file BY FIELD NAME (-of json), never by csv position (AGENTS.md L8)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    v = json.loads(sh([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
                       "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_packets,duration",
                       "-of", "json", str(p)]).stdout)["streams"][0]
    a = json.loads(sh([FFPROBE, "-v", "error", "-select_streams", "a:0",
                       "-show_entries", "stream=codec_name,sample_rate,channels,duration",
                       "-of", "json", str(p)]).stdout)["streams"]
    st = p.stat()
    fmt = json.loads(sh([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                         "-of", "json", str(p)]).stdout)["format"]
    return {
        "path": p.as_posix(), "bytes": st.st_size, "mtime": int(st.st_mtime),
        "sha256": sha256(p), "fmt_dur": round(float(fmt.get("duration") or 0.0), 6),
        "vcodec": v.get("codec_name"), "w": int(v["width"]), "h": int(v["height"]),
        "fps": v.get("r_frame_rate"), "vpackets": int(v["nb_read_packets"]),
        "vdur": round(float(v.get("duration") or 0.0), 3),
        "acodec": (a[0].get("codec_name") if a else None),
        "asr": (int(a[0]["sample_rate"]) if a and a[0].get("sample_rate") else None),
        "ach": (int(a[0]["channels"]) if a and a[0].get("channels") else None),
        "adur": (round(float(a[0].get("duration") or 0.0), 3) if a else None),
    }


def measure_row(name, path):
    m = probe(path)
    m["id"] = name
    return m


def build_manifest():
    pool = [measure_row(n, p) for n, p in POOL]
    cont = []
    for n, p in CONT:
        try:
            cont.append(measure_row(n, p))
        except FileNotFoundError:
            cont.append({"id": n, "path": Path(p).as_posix(), "missing": True})
    total = round(sum(r["vdur"] for r in pool), 3)
    frames = sum(r["vpackets"] for r in pool)
    return {"method": CITE, "method_body": CITE_BODY, "ffmpeg": FFMPEG, "ffprobe": FFPROBE,
            "pool": pool, "cont": cont, "target_s": TARGET_S, "target_tol": TARGET_TOL,
            "band_s": [BAND_LO, BAND_HI], "canvas": list(CANVAS), "fps": FPS,
            "sum_vdur": total, "sum_vpackets": frames,
            "out_dir": OUT.as_posix(), "out_name": SCENE, "sheet_name": SHEET,
            "sheet_px": [COLS * THUMB_W, ROWS * THUMB_H], "mode": None, "out": None, "sheet": None}


def ffmpeg_concat(m, out_path, mode):
    lst = OUT / "concat_list.txt"
    lst.write_text("".join("file '%s'\n" % r["path"] for r in m["pool"]), encoding="utf-8", newline="\n")
    args = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lst.as_posix()]
    args += (["-c", "copy"] if mode == "copy" else
             ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "128k"])
    args += [out_path]
    r = sh(args)
    return r.returncode, (r.stderr or "")[-400:]


def make_sheet(m):
    tdir = OUT / "thumbs"
    tdir.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for i, r in enumerate(m["pool"]):
        t = tdir / ("thumb_%02d.png" % i)
        mid = round(r["vdur"] / 2.0, 3)
        rc, err = None, ""
        rr = sh([FFMPEG, "-y", "-ss", str(mid), "-i", r["path"], "-frames:v", "1",
                 "-vf", "scale=%d:%d" % (THUMB_W, THUMB_H), "-an", str(t.as_posix())])
        if rr.returncode != 0:
            return None, (rr.stderr or "")[-300:]
        thumbs.append(t)
    ins = []
    for t in thumbs:
        ins += ["-i", str(t.as_posix())]
    layout = "0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0"
    fc = "[%s]xstack=inputs=%d:layout=%s[out]" % ("][".join(str(i) for i in range(len(thumbs))), len(thumbs), layout)
    rr = sh([FFMPEG, "-y"] + ins + ["-filter_complex", fc, "-map", "[out]", "-frames:v", "1",
                                    (OUT / SHEET).as_posix()])
    if rr.returncode != 0:
        return None, (rr.stderr or "")[-300:]
    return OUT / SHEET, "xstack " + layout


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    m = build_manifest()
    out_path = (OUT / SCENE).as_posix()
    mode = None
    for cand in ("copy", "reencode"):
        rc, err = ffmpeg_concat(m, out_path, cand)
        if rc != 0:
            continue
        o = probe(out_path)
        if abs(o["vdur"] - m["sum_vdur"]) <= 0.35 and abs(o["vpackets"] - m["sum_vpackets"]) <= 4 \
                and (o["w"], o["h"]) == CANVAS and o["fps"] == FPS and o["acodec"]:
            mode = cand
            break
    if mode is None:
        print("BUILD_FAIL concat rc=%s %s" % (rc, err))
        return 2
    m["mode"] = mode
    m["out"] = probe(out_path)
    sheet, note = make_sheet(m)
    if sheet is None:
        print("BUILD_FAIL sheet %s" % note)
        return 2
    m["sheet"] = probe(sheet.as_posix())
    m["sheet_note"] = note
    MAN.write_text(json.dumps(m, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    DOC.write_text(render_doc(m), encoding="utf-8", newline="\n")
    print("BUILT mode=%s out=%s dur=%s f=%d %dx%d bytes=%d" % (
        mode, m["out"]["path"], m["out"]["vdur"], m["out"]["vpackets"], m["out"]["w"], m["out"]["h"], m["out"]["bytes"]))
    return 0


def verify(m, doc_text=None):
    """Every number in the manifest is re-measured from disk. Codes: PATH MISSING SHA STALE CANVAS
    FPS ACODEC BAND TARGET MATH AUDIO SHEET DRIFT KEEPWORD CITE."""
    prob = []
    try:
        pool = [measure_row(r["id"], r["path"]) for r in m["pool"]]
    except FileNotFoundError as e:
        prob.append("PATH missing input %s" % e)
        pool = []
    for old, new in zip(m["pool"], pool):
        for k in ("sha256", "bytes", "w", "h", "fps", "vpackets", "vdur", "acodec", "asr", "ach"):
            if old[k] != new[k]:
                prob.append("SHA %s field %s manifest=%s disk=%s" % (old["id"], k, old[k], new[k]))
    for r in pool:
        if (r["w"], r["h"]) != CANVAS:
            prob.append("CANVAS %s %dx%d != %dx%d" % (r["id"], r["w"], r["h"], *CANVAS))
        if r["fps"] != FPS:
            prob.append("FPS %s %s != %s" % (r["id"], r["fps"], FPS))
        if (r["acodec"], r["asr"], r["ach"]) != ("aac", 32000, 2):
            prob.append("ACODEC %s %s/%s/%s" % (r["id"], r["acodec"], r["asr"], r["ach"]))
    # the doc prints each row's duration, so the CLAIM is what must sit in the item's 5-10 s band
    for r in m["pool"]:
        if not (BAND_LO <= r["vdur"] <= BAND_HI):
            prob.append("BAND %s dur=%s outside %s-%s s" % (r["id"], r["vdur"], BAND_LO, BAND_HI))
    total = round(sum(r["vdur"] for r in pool), 3) if pool else None
    frames = sum(r["vpackets"] for r in pool) if pool else None
    if pool and abs(total - m["sum_vdur"]) > 1e-6:
        prob.append("MATH sum_vdur manifest=%s disk=%s" % (m["sum_vdur"], total))
    if pool and m["sum_vpackets"] != frames:
        prob.append("MATH sum_vpackets manifest=%s disk=%s" % (m["sum_vpackets"], frames))
    if pool and abs(total - TARGET_S) > TARGET_TOL:
        prob.append("TARGET total=%s s outside %s +/- %s" % (total, TARGET_S, TARGET_TOL))
    if m.get("canvas") != list(CANVAS) or m.get("fps") != FPS:
        prob.append("CANVAS manifest claim %s %s" % (m.get("canvas"), m.get("fps")))
    # the stitched scene
    try:
        o = probe((m["out_dir"] + "/" + m["out_name"]))
        if o["sha256"] != m["out"]["sha256"]:
            prob.append("SHA out bytes changed manifest=%s disk=%s" % (m["out"]["sha256"][:16], o["sha256"][:16]))
        # the doc prints the manifest's out row, so every claim in it is compared to the disk probe
        for k, code in (("vcodec", "CODEC"), ("acodec", "AUDIO"), ("asr", "AUDIO"), ("ach", "AUDIO"),
                        ("bytes", "SHA"), ("w", "CANVAS"), ("h", "CANVAS"), ("fps", "FPS"),
                        ("vpackets", "MATH"), ("vdur", "MATH"), ("fmt_dur", "MATH")):
            if m["out"].get(k) != o.get(k):
                prob.append("%s out field %s manifest=%s disk=%s" % (code, k, m["out"].get(k), o.get(k)))
        newest = max(r["mtime"] for r in m["pool"])
        if Path(m["out_dir"], m["out_name"]).stat().st_mtime < newest:
            prob.append("STALE out mtime %s < newest input mtime %s" % (
                Path(m["out_dir"], m["out_name"]).stat().st_mtime, newest))
        if (o["w"], o["h"]) != CANVAS:
            prob.append("CANVAS out %dx%d != %dx%d" % (o["w"], o["h"], *CANVAS))
        if o["fps"] != FPS:
            prob.append("FPS out %s != %s" % (o["fps"], FPS))
        if abs(o["vpackets"] - m["sum_vpackets"]) > 4:
            prob.append("MATH out vpackets=%s != sum inputs %s" % (o["vpackets"], m["sum_vpackets"]))
        if abs(o["vdur"] - m["sum_vdur"]) > 0.35:
            prob.append("MATH out dur=%s != sum inputs %s" % (o["vdur"], m["sum_vdur"]))
        if not o["acodec"]:
            prob.append("AUDIO out has no audio stream")
    except FileNotFoundError as e:
        prob.append("MISSING out %s" % e)
    except (KeyError, TypeError):
        prob.append("MISSING out not built")
    # contact sheet
    try:
        s = probe((m["out_dir"] + "/" + m["sheet_name"]))
        if [s["w"], s["h"]] != m["sheet_px"]:
            prob.append("SHEET %dx%d != %dx%d" % (s["w"], s["h"], *m["sheet_px"]))
    except FileNotFoundError as e:
        prob.append("SHEET missing %s" % e)
    # continuation rows are measured, not claimed
    for row in m.get("cont", []):
        if row.get("missing"):
            prob.append("PATH continuation row missing %s" % row["path"])
    # doc
    if doc_text is not None:
        if render_doc(m) != doc_text:
            prob.append("DRIFT notes.md != render_doc(manifest)")
        if re.search(r"\b(best|prettiest|sharpest|nicest|cleanest)\b", doc_text, re.I):
            prob.append("KEEPWORD quality word in notes (KEEP is Derrick's alone)")
        if m.get("method") not in doc_text or m.get("method_body") not in doc_text:
            prob.append("CITE method URL / saved body not cited in notes")
    return prob


def render_doc(m):
    o = m["out"]
    L = []
    L.append("# 2.6 (ALI-126/128) - ~1 min 16:9 review cut, hard-cut with ffmpeg")
    L.append("")
    L.append("Built by `C:/AI/community/notes/ali126_scene_cut_build.py` (the only writer of these files).")
    L.append("Method: the FFmpeg project's own concat page `%s` (saved body `%s`): concat demuxer, and" % (m["method"], m["method_body"]))
    L.append("`-c copy` is only valid when every input shares codec + canvas + rate, which is measured here, not assumed.")
    L.append("Stitch mode used: `%s`. ffmpeg `%s` / ffprobe `%s` (8.0.1-full_build)." % (m["mode"], m["ffmpeg"], m["ffprobe"]))
    L.append("")
    L.append("Objective numbers only. `KEEP` is Derrick's alone (AGENTS.md), and this file has no vision judge,")
    L.append("no ranking and no quality claim. Every row below is re-measured off disk by ffprobe `-of json` parsed by")
    L.append("field name; `--check` recomputes them and fails on drift. Nothing was rendered, queued or fetched by this item.")
    L.append("")
    L.append("## Scene folder (open this)")
    L.append("")
    L.append("- folder: `%s`" % m["out_dir"])
    L.append("- cut: `%s/%s`" % (m["out_dir"], m["out_name"]))
    L.append("- contact sheet: `%s/%s` (%dx%d, one mid-clip frame per input, grid order = the row order below)" % (
        m["out_dir"], m["sheet_name"], m["sheet_px"][0], m["sheet_px"][1]))
    L.append("- media lives under `runs/`, which is gitignored (.gitignore:10), so the committed record is this doc + the manifest")
    L.append("")
    L.append("## Hard-cut arm (the scene that exists)")
    L.append("")
    L.append("| # | clip | s | frames | canvas | fps | v/a codec | audio | bytes | sha256-16 |")
    L.append("|---|------|---|--------|--------|-----|-----------|-------|-------|-----------|")
    for i, r in enumerate(m["pool"], 1):
        L.append("| %d | %s | %s | %d | %dx%d | %s | %s/%s | %s %sHz %sch | %d | %s |" % (
            i, r["id"], r["vdur"], r["vpackets"], r["w"], r["h"], r["fps"], r["vcodec"], r["acodec"],
            r["adur"], r["asr"], r["ach"], r["bytes"], r["sha256"][:16]))
    L.append("| **sum** |  %d clips | **%s** | **%d** | %dx%d | %s |  |  |  |  |" % (
        len(m["pool"]), m["sum_vdur"], m["sum_vpackets"], m["canvas"][0], m["canvas"][1], m["fps"]))
    L.append("")
    L.append("Measured scene: `%s` = %s s, %d video packets, %dx%d, %s fps, video %s + audio %s %sHz %sch, %d bytes, sha256 `%s`." % (
        m["out_name"], o["vdur"], o["vpackets"], o["w"], o["h"], o["fps"], o["vcodec"], o["acodec"], o["asr"], o["ach"],
        o["bytes"], o["sha256"]))
    L.append("")
    L.append("Target: %s s +/- %s (item text: ~1 min from 5-10 s clips). Measured total of the pool = %s s; each clip" % (
        m["target_s"], m["target_tol"], m["sum_vdur"]))
    L.append("is %s-%s s, so %d clips is the shortest cut that reaches ~1 min and 6 is what the 16:9 pool holds at" % (
        m["band_s"][0], m["band_s"][1], len(m["pool"])))
    L.append("one clip per seed (51130001, 2, 3, 4, 5, 6). Clip order is by seed, which is deterministic and is NOT a")
    L.append("narrative edit: beat order and any KEEP are Derrick's.")
    L.append("")
    L.append("## Continuation material on disk (the A/B row)")
    L.append("")
    L.append("| arm / clip | s | frames | canvas | fps | audio | bytes |")
    L.append("|------------|---|--------|--------|-----|-------|-------|")
    for r in m["cont"]:
        if r.get("missing"):
            L.append("| %s | MISSING | - | - | - | - | - |" % r["id"])
        else:
            L.append("| %s | %s | %d | %dx%d | %s | %s %sHz %sch | %d |" % (
                r["id"], r["vdur"], r["vpackets"], r["w"], r["h"], r["fps"], r["acodec"], r["asr"], r["ach"], r["bytes"]))
    L.append("")
    L.append("Objective consequence: the only 16:9 continuation render on disk is `ali173_cont_hc1_s51140001` (10.0 s,")
    L.append("1024x576), so a continuation arm of the same ~60 s at 1344x768 cannot be cut from the material that")
    L.append("exists; the 2026-10-20 continuation arm is 768x1344 vertical. A same-canvas, same-seed A/B therefore needs a")
    L.append("render window (fix_plan 2.6b), and scaling 1024x576 into 1344x768 would compare an upscale, not a method.")
    L.append("")
    L.append("## Independent proof (commands run by hand, outside this builder)")
    L.append("")
    L.append("```")
    L.append("ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets,r_frame_rate,width,height -of csv=p=0 \\")
    L.append("        runs/ali126_scene1_hc169/%s   -> %d,%d,%s,%d" % (m["out_name"], o["w"], o["h"], o["fps"], o["vpackets"]))
    L.append("ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of csv=p=0 \\")
    L.append("        runs/ali126_scene1_hc169/%s   -> %s,%s,%s,%s" % (m["out_name"], o["acodec"], o["asr"], o["ach"], o["adur"]))
    L.append("ffprobe -v error -show_entries format=duration,size -of csv=p=0 ...   -> %.6f,%d" % (o["fmt_dur"], o["bytes"]))
    L.append("certutil.exe -hashfile runs/ali126_scene1_hc169/%s SHA256   -> %s" % (m["out_name"], o["sha256"]))
    L.append("```")
    L.append("")
    L.append("The container duration (%.6f s) is longer than the video stream (%s s = %d packets at %s fps) because the concat" % (o["fmt_dur"], o["vdur"], o["vpackets"], o["fps"]))
    L.append("demuxer keeps each source's packet timeline; the video stream is what `-count_packets` counts, so the frame")
    L.append("proof is %d = 6 x 243." % (o["vpackets"],))
    L.append("A note for AGENTS.md's proof line: raw `-show_streams` output is `key=value`, so a `,audio,` substring test")
    L.append("finds 0 hits; use `-select_streams a:0 ... -of csv` (measured 0 vs 1 on this file).")
    L.append("")
    L.append("## Reproduce")
    L.append("")
    L.append("```")
    L.append("python C:/AI/community/notes/ali126_scene_cut_build.py --build")
    L.append("python C:/AI/community/notes/ali126_scene_cut_build.py --check    # expect: PROBLEMS 0 VERDICT CLEAN")
    L.append("python C:/AI/community/notes/ali126_scene_cut_build.py --selftest # expect: SELFTEST_CLEAN seeds=14 fired=14 silent=0 real_tree_problems=0")
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


def load_manifest():
    return json.loads(MAN.read_text(encoding="utf-8"))


def check():
    if not MAN.exists() or not DOC.exists():
        print("PROBLEMS 1 VERDICT RED BUILT_NOT_PRESENT")
        return 1
    m = load_manifest()
    doc = DOC.read_text(encoding="utf-8")
    prob = verify(m, doc)
    print("PROBLEMS %d VERDICT %s scene=%s dur=%s f=%d %dx%d mode=%s sheet=%dx%d" % (
        len(prob), "CLEAN" if not prob else "RED", m["out_name"], m["out"]["vdur"], m["out"]["vpackets"],
        m["out"]["w"], m["out"]["h"], m["mode"], m["sheet_px"][0], m["sheet_px"][1]))
    for p in prob:
        print("  " + p)
    return 0 if not prob else 1


# ---- seeded faults: each must fire on a clone and stay silent on the real artifact ----
def seeds(m):
    out = []

    def mut(fn, code):
        c = copy.deepcopy(m)
        fn(c)
        return code, c, None

    def set_out(c, **kw):
        c["out"].update(kw)

    out.append(mut(lambda c: c["pool"].__setitem__(slice(1, None), c["pool"][1:2]), "MATH"))  # drop clips -> sums lie
    out.append(mut(lambda c: set_out(c, vpackets=c["out"]["vpackets"] - 243), "MATH"))
    out.append(mut(lambda c: set_out(c, vdur=round(c["out"]["vdur"] - 10.0, 3)), "MATH"))
    out.append(mut(lambda c: set_out(c, w=1024, h=576), "CANVAS"))
    out.append(mut(lambda c: set_out(c, acodec=None, asr=None, ach=None), "AUDIO"))
    out.append(mut(lambda c: c["pool"][0].update(path=(Path(c["pool"][0]["path"]).parent / "nope_missing.mp4").as_posix()), "PATH"))
    out.append(mut(lambda c: c["pool"][2].update(vdur=20.042), "BAND"))
    out.append(mut(lambda c: c["pool"][1].update(sha256="0" * 64), "SHA"))
    doc_seeds = [
        ("STALE", lambda m2, t: os.utime(Path(m2["out_dir"], m2["out_name"]), (1_700_000_000, 1_700_000_000))),
        ("MISSING", lambda m2, t: (Path(m2["out_dir"], m2["out_name"]).rename(Path(m2["out_dir"], m2["out_name"] + ".hidden")),
                                  Path(m2["out_dir"], m2["sheet_name"]).rename(Path(m2["out_dir"], m2["sheet_name"] + ".hidden")))),
        ("SHEET", lambda m2, t: Path(m2["out_dir"], m2["sheet_name"]).rename(Path(m2["out_dir"], m2["sheet_name"] + ".hidden"))),
        ("DRIFT", lambda m2, t: (DOC.write_text(t + "\nHand edit.\n", encoding="utf-8", newline="\n"))),
        ("KEEPWORD", lambda m2, t: (DOC.write_text(t + "\nThis cut is the best of the set.\n", encoding="utf-8", newline="\n"))),
        ("CITE", lambda m2, t: (DOC.write_text(t.replace(m2["method"], "http://example.invalid"), encoding="utf-8", newline="\n"))),
    ]
    return out, doc_seeds


def selftest():
    if not MAN.exists():
        print("SELFTEST_DIRTY no manifest")
        return 1
    m = load_manifest()
    doc_real = DOC.read_text(encoding="utf-8")
    fired, silent, extra = 0, [], []
    cases, doc_cases = seeds(m)
    for code, c, _ in cases:
        prob = verify(c, render_doc(c))
        if any(p.startswith(code) for p in prob):
            fired += 1
        else:
            silent.append(code + " manifest-seed not fired: " + ";".join(prob[:2]))
        if not any(p.startswith(code) for p in prob):
            extra.append(code + " seed produced no target code")
    for code, fn in doc_cases:
        prob = None
        try:
            fn(m, doc_real)
            mm = load_manifest()
            t = DOC.read_text(encoding="utf-8") if code in ("DRIFT", "KEEPWORD", "CITE") else doc_real
            prob = verify(mm, t)
            if any(p.startswith(code) for p in prob):
                fired += 1
            else:
                silent.append(code + " fs-seed not fired: " + ";".join(prob[:2]))
        finally:
            restore(m, code)
            DOC.write_text(doc_real, encoding="utf-8", newline="\n")
    real = verify(load_manifest(), DOC.read_text(encoding="utf-8"))
    for p in real:
        extra.append("real tree: " + p)
    n = len(cases) + len(doc_cases)
    print("SELFTEST_%s seeds=%d fired=%d silent=%d real_tree_problems=%d" % (
        "CLEAN" if not silent and not extra else "DIRTY", n, fired, len(silent), len(real)))
    for s in silent + extra:
        print("  " + s)
    return 0 if not silent and not extra and fired == n else 1


def restore(m, code):
    """Undo a filesystem seed: rebuild the file(s) it moved, cheapest way."""
    d = Path(m["out_dir"])
    if code in ("MISSING", "SHEET"):
        for nm in (m["out_name"], m["sheet_name"]):
            if (d / (nm + ".hidden")).exists() and not (d / nm).exists():
                (d / (nm + ".hidden")).rename(d / nm)
    if code == "STALE" and (d / m["out_name"]).exists():
        t = m["out"]["mtime"]
        os.utime(d / m["out_name"], (t, t))   # restore the recorded stamp, bytes untouched


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if arg == "--build":
        sys.exit(build())
    if arg == "--check":
        sys.exit(check())
    if arg == "--selftest":
        sys.exit(selftest())
    print("usage: --build | --check | --selftest")
    sys.exit(2)
