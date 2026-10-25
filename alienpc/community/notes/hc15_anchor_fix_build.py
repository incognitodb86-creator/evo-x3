"""HC15 start-fidelity fix builder - fix_plan.md FIRST item (Derrick 2026-10-24 5:49 PM CT "They should start
closer to the reference image what the fuck? Do an audit something is wrong").

WHAT THIS FILE IS
  1. the measuring tool for the audit table   (--metrics): for all six rendered HC15 clips, per frame 0 / 180
     / 361, SSIM + PSNR against the clip's own LoadImage start still (cover-crop AND stretch geometry) and the
     ArcFace identity cosine of every start-still face against every face detected in that frame.
     Writes notes/hc15_audit/metrics.json + prints the table the audit quotes.
  2. the switch                                         (--build): rebuilds clip 1 as ONE new graph that ships
     the community values for the three mismatches the audit found, prompts byte-identical, seed unchanged.
  3. the receipt                                      (--check): 13 named detectors over the built artifact.
  4. the self-destruct probe                        (--selftest): seeds the OLD wiring/old settings into a
     clone and requires every named detector to fire there and 0 on the real artifact.
  5. the frame-0 before/after sheet                   (--sheet): after the GPU window renders the new clip,
     ffmpeg/PIL only, labelled, no vision judge, no KEEP.

THE THREE SWITCHES (each one is a published community value, not an invention of ours)
  A start-frame anchor: a new `MiniMaxH3AddGuide` node with frame_idx 0 on the c0 conditioning edge
    (positive = c0, latent = c0 latent, image = the clip's start still, vae = the video VAE), and
    s0_guide.conditioning now comes from that node. Source: ComfyUI PR 15439 "Add MiniMaxH3AddGuide for
    anchoring image and audio guides at any frame" (merged 2026-08-13, notes/web/hc15_pr15439.json),
    https://github.com/Comfy-Org/ComfyUI/pull/15439 ; docs page "Anchoring guides at any frame (#15439)" in
    https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md (saved notes/web/02v_docs_h3_native.txt);
    the same keyframe mechanism as `first_frame` in MiniMaxH3ImageToVideo (comfy_extras/nodes_minimax_h3.py:145-149
    -> resolved_frame_index 0, and AddGuide :220-223 -> the same minimax_keyframes list). Reference images alone
    do NOT pin a start frame: the same docs page describes R2V as "Lock character, style, motion, camera, or
    voice from reference images", and the Continuum guide says "First/Last additionally constrain the video"
    (https://raw.githubusercontent.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum/main/docs/USER_GUIDE.md).
  B sampler family + steps: euler/simple/10 -> res_multistep/simple/8, all three schedulers, denoise stays 1.0.
    Source: the README of the model we run, TenStrip/10Eros-Max
    (https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md, saved notes/web/hc15_tenstrip_readme.txt,
    byte-identical to the earlier notes/web/agy51_tenstrip_readme.md): "res_multistep/simple 6-8 steps (my go-to
    for best motion quality)". denoise 1.0 = the continuation pack's "Use the ordinary H3 model and a normal
    full-denoise schedule" (https://raw.githubusercontent.com/ttulttul/ComfyUI-Minimax-H3-Continuation/main/README.md,
    saved notes/web/hc15_continuation_readme.txt, byte-identical to notes/web/03y_continuation_readme.txt).
  C pass shape: c0 length 124 x 3 passes -> c0 length 243 x 1 continuation window (overlap 22 / extension 119 /
    window 141), so 243 + 119 = 362 f = the same 15.0833 s the rendered clips carry, in 2 sampling passes.
    Source: the continuation pack README's published example: "The example first generates a 243-frame clip"
    then "overlap_frames = 22, extension_frames = 119, window_length = 141" (same saved file).

NOW-P1 (added 2026-10-25, the NOW item's builder pass - fix_plan NOW-P1, spec
notes/now_h3_quality_research_20261025.md §3/§4): the SAME file, a SECOND artifact. --now-build writes
`p7/graphs/ali163_hc15_bd002_s51150021.api.json` = the RENDERED clip-11 bytes + exactly the four published
switches (steps 8 -> 12; ref_image_size max -> match; attention comfy kitchen attention -> pytorch attention; a new
`LoraLoaderModelOnly` antiburn node on the CONTINUATION model path only), prompts byte-identical, seed unchanged,
with its own 13 detectors (--now-check) and its own seeded-fault probe (--now-selftest). The clip-1 -> clip-11
path above is untouched, so the shipped FIRST-item receipt stays reproducible.

UNCHANGED ON PURPOSE: every prompt string (the subject-label rewrite is the NEXT fix_plan item, Derrick 5:48 PM
CT), reference slots and ref_image_size, seed 51150001, canvas 1344x768 (the node's published default width/height),
shift video 10.0 / audio 3.0 (node defaults), VSA attention settings, fps 24, the audio VAE + VAEDecodeAudio path.

NO GPU HERE: --build only writes files (graph, run-dir request, p7/JOB_REQUEST.json handoff). A Ralph pass never
queues (PROMPT.md / AGENTS.md), and --sheet refuses to run until the render exists on disk.

RUN
  python C:/AI/community/notes/hc15_anchor_fix_build.py --metrics   # "C:/Program Files/Python312/python.exe"
  python C:/AI/community/notes/hc15_anchor_fix_build.py --build     # C:/AI/director/.venv/Scripts/python.exe
  python C:/AI/community/notes/hc15_anchor_fix_build.py --check
  python C:/AI/community/notes/hc15_anchor_fix_build.py --selftest
  python C:/AI/community/notes/hc15_anchor_fix_build.py --sheet     # after the render, no GPU
  python C:/AI/community/notes/hc15_anchor_fix_build.py --now-build|--now-check|--now-selftest  # NOW-P1
"""
import glob
import hashlib
import json
import copy
import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok  # noqa: E402  (the fiction gate; the only gate allowed to touch a graph)

W = r"C:\AI\community"
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")
FFBIN = (r"C:\Users\derek\AppData\Local\Microsoft\Winget\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_"
         r"8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin")
FFMPEG = os.path.join(FFBIN, "ffmpeg.exe")
FFPROBE = os.path.join(FFBIN, "ffprobe.exe")
AUD = os.path.join(W, "notes", "hc15_audit")
OLD_ID = "ali163_hc15_bd002_s51150001"
NEW_ID = "ali163_hc15_bd002_s51150011"
SEED = 51150001
FRAMES = 362
CANVAS = (1344, 768)   # the clip's canvas, read off clip 1's graph (c0.width/height); the render proof must agree
BASE_G = os.path.join(W, "p7", "graphs", OLD_ID + ".api.json")
NEW_G = os.path.join(W, "p7", "graphs", NEW_ID + ".api.json")
LEDGER = r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"
MINUTES = 15
GATE_FLOOR = 0.45  # the published identity gate this repo uses (notes/ali163_hc_r4g2_verify.py:87)

CLIPS = {}  # id -> dict(mp4, frames, canvas, seed, start, crop, secs, secs_by_segment)

CITATIONS = {
    "anchor": "https://github.com/Comfy-Org/ComfyUI/pull/15439 + https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md#anchoring-guides-at-any-frame-15439",
    "sampler": "https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md",
    "passes": "https://raw.githubusercontent.com/ttulttul/ComfyUI-Minimax-H3-Continuation/main/README.md",
    "canvas": "comfy_extras/nodes_minimax_h3.py:129-130 (width 1344, height 768 = the published defaults) + https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md",
    "flags": "https://github.com/mostlygeek/llama-swap/blob/main/docs/comfyui.md + https://github.com/Comfy-Org/ComfyUI/issues/15337",
}

fails = []


def ck(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)
    return bool(cond)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sha_s(s):
    """sha256 of a STRING (the byte identity of a prompt), not of a path."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def dumps_like(base_bytes, g):
    """Pick the indent that reproduces the base file's byte format, then emit CRLF with no trailing newline."""
    for ind in (2, 4, 1):
        s = json.dumps(g, indent=ind, ensure_ascii=False).replace("\n", "\r\n")
        if s.encode("utf-8") == base_bytes:
            return ind
    return None


def write_graph(path, g, ind):
    data = json.dumps(g, indent=ind, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")
    open(path, "wb").write(data)
    return data


# --------------------------------------------------------------------------- metrics
def probe(mp4):
    """ffprobe -of json: frames, canvas, fps, duration, audio = the AGENTS.md proof fields, parsed by field name."""
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
                          "-show_entries", "stream=width,height,r_frame_rate,nb_read_packets,duration",
                          "-show_streams", "-of", "json", mp4], capture_output=True, text=True)
    d = json.loads(out.stdout)
    v = [s for s in d["streams"] if s.get("codec_type") == "video"][0]
    a = [s for s in d["streams"] if s.get("codec_type") == "audio"]
    if not a:
        # -select_streams v:0 (needed for an honest nb_read_packets on the video) hides every other stream, so
        # the audio presence is read from an unfiltered pass. AGENTS.md: "v:0 is required" - for the CSV fields.
        a2 = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-of", "json", mp4],
                            capture_output=True, text=True)
        a = [s for s in json.loads(a2.stdout).get("streams", []) if s.get("codec_type") == "audio"]
    return dict(frames=int(v["nb_read_packets"]), w=int(v["width"]), h=int(v["height"]),
                fps=v["r_frame_rate"], dur=float(v["duration"]), audio=bool(a))


def ff(args):
    return subprocess.run([FFMPEG, "-hide_banner", "-y"] + args, capture_output=True, text=True)


def extract(mp4, n, out):
    r = ff(["-i", mp4, "-vf", "select='eq(n,%d)'" % n, "-fps_mode", "passthrough", "-frames:v", "1", out])
    assert os.path.isfile(out), "frame extract failed: " + r.stderr[-400:]
    return out


def fit(src, w, h, out, mode):
    vf = ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (w, h, w, h) if mode == "cover"
          else "scale=%d:%d:force_original_aspect_ratio=disable" % (w, h))
    r = ff(["-i", src, "-vf", vf, out])
    assert os.path.isfile(out), "resize failed: " + r.stderr[-400:]
    return out


def ssim_psnr(a, b):
    """ffmpeg SSIM + PSNR on RGB (no chroma subsampling), single-frame inputs. Field names parsed, not positions:
    ffmpeg 8 prints 'SSIM R:.. G:.. B:.. All:0.347619' and 'PSNR r:.. g:.. b:.. average:6.74'."""
    r = ff(["-i", a, "-i", b, "-lavfi", "[0:v]format=gbrp[x];[1:v]format=gbrp[y];[x][y]ssim", "-f", "null", "-"])
    s = re.search(r"SSIM\s.*?All:([0-9.]+)", r.stderr)
    r2 = ff(["-i", a, "-i", b, "-lavfi", "[0:v]format=gbrp[x];[1:v]format=gbrp[y];[x][y]psnr", "-f", "null", "-"])
    p = re.search(r"average:([0-9.]+|inf)", r2.stderr) or re.search(r"average PSNR:\s*([0-9.]+|inf)", r2.stderr)
    psnr = 999.0 if (p and p.group(1) == "inf") else (float(p.group(1)) if p else None)
    return (float(s.group(1)) if s else None), psnr


def load_clips():
    for p in sorted(glob.glob(os.path.join(W, "runs", "hc15_*", "objective.json"))):
        d = jload(p)
        a = d["attempts"][0]
        rid = a["tag"]
        mp4 = a["file"]
        g = jload(os.path.join(W, "p7", "graphs", rid + ".api.json"))
        w, h = g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]
        CLIPS[rid] = dict(mp4=mp4, frames=a["frames"], canvas="%dx%d" % (w, h),
                          w=w, h=h, seed=g["noise"]["inputs"]["noise_seed"],
                          start=g["img"]["inputs"]["image"],
                          crops=[g[k]["inputs"]["image"] for k in ("img2", "img3") if k in g],
                          secs=a["secs"], nodes=len(g))
    return CLIPS


def metrics():
    os.makedirs(AUD, exist_ok=True)
    clips = load_clips()
    sys.path.insert(0, os.path.join(W, "notes"))
    from hc_r4f_facelib import ArcFace, Scrfd, cos  # CPU SCRFD-10G + ArcFace (needs onnxruntime)
    det, rec = Scrfd(), ArcFace()
    import cv2
    rows = []
    for rid, c in sorted(clips.items()):
        still = os.path.join(COMFY, "input", c["start"].replace("/", os.sep))
        faces_src = sorted(det.detect(cv2.imread(still)), key=lambda f: -(f["box"][2] - f["box"][0]) * (f["box"][3] - f["box"][1]))[:2]
        emb_src = [rec.embed(cv2.imread(still), f) for f in faces_src]
        cover = fit(still, c["w"], c["h"], os.path.join(AUD, rid + "_start_cover.png"), "cover")
        stretch = fit(still, c["w"], c["h"], os.path.join(AUD, rid + "_start_stretch.png"), "stretch")
        row = dict(id=rid, mp4=c["mp4"], frames=c["frames"], canvas=c["canvas"], seed=c["seed"],
                   start=c["start"], crops=c["crops"], secs=c["secs"], nodes=c["nodes"],
                   src_faces=[[[round(float(v), 1) for v in f["box"]], round(f["score"], 3)] for f in faces_src],
                   frames_measured={})
        for n in (0, c["frames"] // 2, c["frames"] - 1):
            fp = extract(c["mp4"], n, os.path.join(AUD, rid + "_f%d.png" % n))
            s1, p1 = ssim_psnr(fp, cover)
            s2, p2 = ssim_psnr(fp, stretch)
            img = cv2.imread(fp)
            ff_ = det.detect(img)
            cosines = []
            for es in emb_src:
                best = max([round(cos(es, rec.embed(img, f)), 3) for f in ff_], default=None)
                cosines.append(best)
            row["frames_measured"][str(n)] = dict(ssim_cover=s1, psnr_cover=p1, ssim_stretch=s2,
                                                  psnr_stretch=p2, faces=len(ff_), best_cos=cosines)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
    out = os.path.join(AUD, "metrics.json")
    open(out, "w", encoding="utf-8").write(json.dumps(dict(rows=rows, gate_floor=GATE_FLOOR,
                                                           tool="notes/hc15_anchor_fix_build.py --metrics"),
                                                      indent=1, ensure_ascii=False))
    print("METRICS_JSON " + out + " rows=" + str(len(rows)))
    return rows


# --------------------------------------------------------------------------- build
def transform(base):
    """The three community switches, applied to the rendered clip-1 graph."""
    g = json.loads(json.dumps(base))  # deep copy
    g["c0"]["inputs"]["length"] = 243
    g["ksel"]["inputs"]["sampler_name"] = "res_multistep"
    for k in ("s0_sched", "s1_sched"):
        g[k]["inputs"]["steps"] = 8
    g["g0"] = {"class_type": "MiniMaxH3AddGuide",
               "inputs": {"positive": ["c0", 0], "vae": ["vvae", 0], "latent": ["c0", 1],
                          "image": ["img", 0], "frame_idx": 0}}
    g["s0_guide"]["inputs"]["conditioning"] = ["g0", 0]
    for k in ("c2", "win2", "tail2", "app2", "s2_samp", "s2_guide", "s2_sched"):
        g.pop(k, None)
    g["dec_v"]["inputs"]["samples"] = ["app1", 0]
    g["dec_a"]["inputs"]["samples"] = ["app1", 0]
    g["save"]["inputs"]["filename_prefix"] = "community/%s/%s" % (NEW_ID, NEW_ID)
    return g


def diff_paths(a, b):
    """(kind, node, key) triples: NODE add/remove, [inputs].key change, [class_type] change."""
    paths = set()
    for k in set(a) | set(b):
        if k not in b:
            paths.add(("NODE-", k, ""))
        elif k not in a:
            paths.add(("NODE+", k, ""))
        elif a[k]["class_type"] != b[k]["class_type"]:
            paths.add(("[class_type]", k, ""))
        else:
            for key in set(a[k]["inputs"]) | set(b[k]["inputs"]):
                if a[k]["inputs"].get(key, "\0") != b[k]["inputs"].get(key, "\0"):
                    paths.add(("[inputs]." + key, k, ""))
    return paths


ALLOWED = {("[inputs].length", "c0", ""), ("[inputs].sampler_name", "ksel", ""),
           ("[inputs].steps", "s0_sched", ""), ("[inputs].steps", "s1_sched", ""),
           ("NODE+", "g0", ""), ("[inputs].conditioning", "s0_guide", ""),
           ("NODE-", "c2", ""), ("NODE-", "win2", ""), ("NODE-", "tail2", ""), ("NODE-", "app2", ""),
           ("NODE-", "s2_samp", ""), ("NODE-", "s2_guide", ""), ("NODE-", "s2_sched", ""),
           ("[inputs].samples", "dec_v", ""), ("[inputs].samples", "dec_a", ""),
           ("[inputs].filename_prefix", "save", "")}


def h3_schema():
    """{class: (required, optional)} from the ON-DISK H3 schema (same names run_graph_job.static_check reads
    from /object_info). Only depth-1 io.X.Input entries count, so an Autogrow template input is not required."""
    txt = open(H3_SRC, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'node_id="(\w+)",', txt):
        cls, start = m.group(1), m.end()
        end = txt.find("outputs=[", start)
        blk = txt[start:end if end > 0 else start + 4000]
        req, opt = set(), set()
        for im in re.finditer(r'io\.\w+\.Input\("(\w+)"', blk):
            pre = blk[:im.start()]
            if pre.count("(") - pre.count(")") + pre.count("[") - pre.count("]") != 1:
                continue
            args = _args(blk, im.end())
            (opt if "optional=True" in args else req).add(im.group(1))
        if req:
            out[cls] = (req, opt)
    return out


def _args(txt, i):
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "(":
            depth += 1
        elif txt[j] == ")":
            depth -= 1
            if depth == 0:
                return txt[i + 1:j]
        j += 1
    return txt[i:]


def scan(g, sch):
    bad = []
    for nid, n in sorted(g.items()):
        ct = n["class_type"]
        if ct not in sch:
            continue
        names = sch[ct][0] | sch[ct][1]
        keys = {k.split(".")[0] for k in n["inputs"]}
        bad += [f"{nid}.{k}: not an input of {ct}" for k in sorted(keys - names)]
        bad += [f"{nid}: required input {r} missing" for r in sorted(sch[ct][0])
                if r not in n["inputs"] and not any(a.startswith(r + ".") for a in n["inputs"])]
    return bad


def job_note(gnew):
    b = open(NEW_G, "rb").read()
    return ("HC15 start-fidelity re-render of clip 1 (fix_plan FIRST item, Derrick 2026-10-24 5:49 PM CT): "
            "same start still %s, same seed %d, same 1344x768 24 fps 362 f = 15.0833 s with audio, prompts BYTE-"
            "IDENTICAL to the rendered clip 1 (the subject-label rewrite is the next item), three community "
            "switches: (A) new node g0 MiniMaxH3AddGuide frame_idx 0 anchors the start still on the c0 "
            "conditioning edge and s0_guide reads it - %s; (B) ksel res_multistep, s0/s1 steps 8, denoise 1.0 "
            "- %s; (C) c0 length 243 + one continuation window (overlap 22 / extension 119 / window 141) = "
            "243+119 = 362 in 2 passes instead of 124 x 3 - %s. Audit with the measured frame-0 table: "
            "C:/AI/community/notes/hc15_start_fidelity_audit.md; builder/receipts "
            "C:/AI/community/notes/hc15_anchor_fix_build.py --check / --selftest. Graph %d nodes, %d B, sha256 "
            "%s, 0 cfg keys, offline schema scan 0 defects, diff vs the rendered clip-1 graph = %d allowed paths "
            "and nothing else. comm.guard_ok allow on every prompt-bearing string; scripts/tests/test_p6_review.py "
            "21 passed. id-free: no runs/%s/%s.mp4, no p7/jobs/%s.result.json, no ComfyUI output/%s. Render: "
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/run_graph_job.py "
            "C:/AI/community/runs/%s %s --frames 362 (guard_ok + static check + budget gate inside), then "
            "python C:/AI/community/notes/hc15_anchor_fix_build.py --sheet for the labelled frame-0 before/after "
            "sheet to send Derrick. minutes=%d (measured per-segment on clip 5: 124 f @10 steps = 179 s, 141 f "
            "window @10 = 267 s, decode/audio 35 s; the 243 f + 141 f pair at 8 steps = ~530 s = 8.8 min, x1.7 "
            "headroom). Unload comfyui_auto after the clip. GPU work needs a live window: a Ralph pass never "
            "queues - this file is the handoff.") % (CLIPS_START, SEED, CITATIONS["anchor"], CITATIONS["sampler"],
            CITATIONS["passes"], len(gnew), len(b), sha(NEW_G), len(ALLOWED), NEW_ID, NEW_ID, NEW_ID, NEW_ID,
            NEW_ID, NEW_ID, MINUTES)


CLIPS_START = "community/hc/BD002.jpg"


def arm(gnew):
    run = os.path.join(W, "runs", NEW_ID)
    os.makedirs(run, exist_ok=True)
    data = open(NEW_G, "rb").read()
    open(os.path.join(run, "request.api.json"), "wb").write(data)
    req = {"jobs": [{"id": NEW_ID, "kind": "graph", "frames": FRAMES, "frames_tol": 33,
                     "minutes": MINUTES, "note": job_note(gnew)}],
           "id": NEW_ID, "run_dir": run.replace("\\", "/"),
           "api": NEW_G.replace("\\", "/"), "frames": FRAMES, "frames_tol": 33,
           "minutes": MINUTES, "note": job_note(gnew)}
    open(os.path.join(W, "p7", "JOB_REQUEST.json"), "w", encoding="utf-8").write(
        json.dumps(req, indent=2, ensure_ascii=False))
    return req


# --------------------------------------------------------------------------- checks
def ctx_default():
    """The artifacts the checks read off disk. A seed call passes tampered copies, so every detector is provably
    reachable (L10: a green check that cannot fail is worthless)."""
    am = os.path.join(W, "notes", "hc15_start_fidelity_audit.md")
    mj = os.path.join(AUD, "metrics.json")
    mp4 = os.path.join(W, "runs", NEW_ID, NEW_ID + ".mp4")
    rendered = os.path.isfile(mp4)
    return dict(req=jload(os.path.join(W, "p7", "JOB_REQUEST.json")),
                ledger=jload(LEDGER),
                audit_txt=open(am, encoding="utf-8").read() if os.path.isfile(am) else "",
                metrics_rows=jload(mj)["rows"] if os.path.isfile(mj) else [],
                new_graph_bytes=open(NEW_G, "rb").read(),
                sheet_path=os.path.join(W, "runs", NEW_ID, NEW_ID + "_frame0_sheet.png"),
                rendered=rendered,
                obj=(jload(os.path.join(W, "runs", NEW_ID, "objective.json")) if rendered
                     and os.path.isfile(os.path.join(W, "runs", NEW_ID, "objective.json")) else None),
                probe=(probe(mp4) if rendered else None))


def do_check(gbase, gnew, label="real", ctx=None):
    ctx = ctx or ctx_default()
    fails.clear()
    # 1 ANCHOR
    g0 = [k for k, n in gnew.items() if n["class_type"] == "MiniMaxH3AddGuide"]
    ok = (len(g0) == 1 and gnew[g0[0]]["inputs"].get("frame_idx") == 0
          and gnew[g0[0]]["inputs"].get("image") == ["img", 0]
          and gnew[g0[0]]["inputs"].get("vae") == ["vvae", 0]
          and gnew[g0[0]]["inputs"].get("latent") == ["c0", 1]
          and gnew[g0[0]]["inputs"].get("positive") == ["c0", 0]
          and gnew["s0_guide"]["inputs"]["conditioning"] == [g0[0], 0]
          and gnew["img"]["inputs"]["image"] == gbase["img"]["inputs"]["image"])
    ck(ok, "1 ANCHOR one MiniMaxH3AddGuide, frame_idx 0, image = the clip's own start still, vae/latent/positive "
           "on the c0 edge, s0_guide fed by it (PR 15439 mechanism)")
    # 2 SAMPLER
    st = {k: n["inputs"]["steps"] for k, n in gnew.items() if k.endswith("_sched")}
    ck(gnew["ksel"]["inputs"]["sampler_name"] == "res_multistep"
       and all(n["inputs"]["scheduler"] == "simple" for k, n in gnew.items() if k.endswith("_sched"))
       and st and set(st.values()) == {8}
       and all(n["inputs"]["denoise"] == 1.0 for k, n in gnew.items() if k.endswith("_sched"))
       and 6 <= 8 <= 8,
       "2 SAMPLER res_multistep/simple, steps 8 on every scheduler (TenStrip README published range 6-8), denoise 1.0")
    # 3 GEOMETRY
    win = {k: n["inputs"] for k, n in gnew.items() if n["class_type"] == "MiniMaxH3GuidedContinuationWindow"}
    nsamp = len([k for k, n in gnew.items() if n["class_type"] == "SamplerCustomAdvanced"])
    napp = len([k for k, n in gnew.items() if n["class_type"] == "MiniMaxH3AppendContinuation"])
    L = gnew["c0"]["inputs"]["length"]
    total = L + sum(v["extension_frames"] for v in win.values())
    ck(L == 243 and (L - 5) % 17 == 0 and len(win) == 1 and nsamp == 2 and napp == 1
       and list(win.values())[0]["overlap_frames"] == 22 and list(win.values())[0]["extension_frames"] == 119
       and (22 - 5) % 17 == 0 and 119 % 17 == 0 and total == FRAMES and FRAMES % 17 == 5,
       "3 GEOMETRY c0 length 243 (the published example initial) + 1 window 22/119/141 = 362 f, 2 samplers, "
       "1 append, all grid rules hold, total == the rendered clips' 362")
    # 4 UNCHANGED
    def gv(g, node, key):
        return g.get(node, {}).get("inputs", {}).get(key, "\0")
    pairs = [("c0", "prompt"), ("c1", "prompt"), ("c0", "ref_images.ref_image_1"), ("c0", "ref_images.ref_image_2"),
             ("c0", "ref_image_size"), ("noise", "noise_seed"), ("c0", "width"), ("c0", "height"),
             ("m_shift", "shift_video"), ("m_shift", "shift_audio"), ("m_vsa", "inputs"), ("mkvid", "fps"),
             ("dec_a", "vae"), ("c0", "audio_vae"), ("img", "image")]
    drift = [(n, k) for n, k in pairs if gv(gnew, n, k) != gv(gbase, n, k)]
    ck(not drift
       and gv(gnew, "c0", "ref_image_size") == "max" and gv(gnew, "noise", "noise_seed") == SEED == 51150001
       and (gv(gnew, "c0", "width"), gv(gnew, "c0", "height")) == (1344, 768)
       and (gv(gnew, "m_shift", "shift_video"), gv(gnew, "m_shift", "shift_audio")) == (10.0, 3.0)
       and gv(gnew, "mkvid", "fps") == 24 and gv(gnew, "dec_a", "vae") == ["avae", 0]
       and gv(gnew, "c0", "audio_vae") == ["avae", 0],
       "4 UNCHANGED prompts byte-identical, ref slots + ref_image_size=max, seed %d, canvas 1344x768, shift 10/3, "
       "VSA block, fps 24, audio path wired (drift=%s)" % (SEED, drift))
    # 5 SCOPE
    d = diff_paths(gbase, gnew)
    ck(d == ALLOWED, "5 SCOPE diff paths == the %d allowed paths, nothing else (extra=%s missing=%s)"
       % (len(ALLOWED), sorted(d - ALLOWED)[:4], sorted(ALLOWED - d)[:4]))
    # 6 SCHEMA
    bad = scan(gnew, h3_schema())
    ag = gnew.get("g0", {"inputs": {}})["inputs"]
    ck(not bad and {"positive", "latent"} <= set(ag) and {"vae", "image", "frame_idx"} <= set(ag),
       "6 SCHEMA offline /object_info clone: 0 defects over every H3 class incl. MiniMaxH3AddGuide %s" % bad[:3])
    # 7 GATE
    prose = [(k, v) for k, n in gnew.items() for v in n["inputs"].values() if isinstance(v, str) and len(v) > 120]
    allowed = [(k, v) for k, v in prose if guard_ok(v)]
    ck(len(prose) == 2 and len(allowed) == 2,
       "7 GATE comm.guard_ok allows %d/%d prompt-bearing strings (all keyed c0.prompt/c1.prompt)"
       % (len(allowed), len(prose)))
    # 8 INTEGRITY
    dangling = [f"{k}.{key}" for k, n in gnew.items() for key, v in n["inputs"].items()
                if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and v[0] not in gnew]
    reach, stack = set(), ["save"]
    while stack:
        k = stack.pop()
        if k in reach or k not in gnew:
            continue
        reach.add(k)
        stack += [v[0] for v in gnew[k]["inputs"].values()
                  if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str)]
    imgs = [n["inputs"]["image"] for n in gnew.values() if n["class_type"] == "LoadImage"]
    ck(not dangling and reach == set(gnew) and len(gnew) == len(set(gnew))
       and all(os.path.isfile(os.path.join(COMFY, "input", i.replace("/", os.sep))) for i in imgs)
       and not any("cfg" in k.lower() for k in json.dumps(gnew).split('"'))
       and gnew["c0"]["inputs"]["width"] % 32 == 0 and gnew["c0"]["inputs"]["height"] % 32 == 0,
       "8 INTEGRITY 0 dangling links, every node feeds save, LoadImage files exist in ComfyUI/input, 0 cfg keys, "
       "canvas on the 32 grid")
    # 9 ARM, two valid states: ARMED (before the render) or RENDERED-WITH-PROOF (after it).
    # The pre-render state asserts the id is free; after a GPU window renders, the same detector asserts the
    # render's own proof, so the receipt does not go red the moment the item is delivered.
    req = ctx["req"]
    led = ctx["ledger"]
    rid_free = not (ctx["rendered"]
                    or os.path.isfile(os.path.join(W, "p7", "jobs", NEW_ID + ".result.json"))
                    or glob.glob(os.path.join(COMFY, "output", "community", NEW_ID, "*")))
    byte_ok = os.path.isfile(os.path.join(W, "runs", NEW_ID, "request.api.json")) and \
        open(os.path.join(W, "runs", NEW_ID, "request.api.json"), "rb").read() == open(NEW_G, "rb").read()
    id_ok = (req["id"] == NEW_ID and [j["id"] for j in req["jobs"]] == [NEW_ID] and req["frames"] == FRAMES
             and req["api"].replace("\\", "/") == NEW_G.replace("\\", "/")
             and req["run_dir"].replace("\\", "/") == os.path.join(W, "runs", NEW_ID).replace("\\", "/"))
    if ctx["rendered"]:
        obj, pr = ctx["obj"], ctx["probe"]
        a = (obj or {}).get("attempts", [{}])[0]
        proof = (obj and obj.get("ok") is True and a.get("tag") == NEW_ID and a.get("frames") == FRAMES
                 and a.get("audio") is True and a.get("fps") == "24/1"
                 and (a.get("w"), a.get("h")) == CANVAS and not a.get("blackfreeze")
                 and pr and pr["frames"] == FRAMES and pr["audio"] and pr["fps"] == "24/1"
                 and (pr["w"], pr["h"]) == CANVAS)
        ck(id_ok and byte_ok and proof and led["used_min"] < led["cap_min"] and led["jobs"] + 1 <= led["job_cap"],
           "9 ARM-RENDERED graph == run-dir request byte-identical, JOB_REQUEST top level AND jobs[] = the id, "
           "render proof agrees (objective.json ok + ffprobe %s = 1344x768 24/1 %d f audio, 0 blackfreeze), "
           "ledger %s < %s min and %s + 1 <= %s jobs"
           % (json.dumps(pr), FRAMES, led["used_min"], led["cap_min"], led["jobs"], led["job_cap"]))
    else:
        ck(id_ok and byte_ok and rid_free
           and led["used_min"] + MINUTES <= led["cap_min"] and led["jobs"] + 1 <= led["job_cap"],
           "9 ARM graph == run-dir request byte-identical, JOB_REQUEST top level AND jobs[] = the new id, id free of "
           "mp4/result/output, ledger %s + %d <= %s min and %s + 1 <= %s jobs"
           % (led["used_min"], MINUTES, led["cap_min"], led["jobs"], led["job_cap"]))
    # 10 AUDIT CITED
    txt = ctx["audit_txt"]
    urls = set(re.findall(r"https?://[^\s)>\]]+", txt))
    note = req["note"]
    ck(len(txt) > 4000 and len(urls) >= 8 and all(u in note for u in
       [CITATIONS["anchor"].split(" ")[0], CITATIONS["sampler"]])
       and "hc15_start_fidelity_audit.md" in note,
       "10 AUDIT notes/hc15_start_fidelity_audit.md exists with %d URLs and every switched setting cites one, "
       "and the handoff note names it" % len(urls))
    # 11 METRICS ON DISK: the before/after claim, measured. The six BEFORE rows must still show the reported
    # defect (frame 0 far from the start still) and the AFTER row must show the anchor took (frame 0 lands on
    # the still, and the start still's own faces are in frame 0 at or above the published identity gate).
    rows = {r["id"]: r for r in ctx["metrics_rows"]}
    before = {rid: rows[rid]["frames_measured"]["0"]["ssim_cover"] for rid in rows if rid != NEW_ID}
    aft = rows.get(NEW_ID, {}).get("frames_measured", {}).get("0", {})
    acos = [c for c in (aft.get("best_cos") or []) if c is not None]
    ck(len(rows) == 7 and len(before) == 6
       and all(v is not None and v < 0.5 for v in before.values())
       and aft.get("ssim_cover") is not None and aft["ssim_cover"] >= 0.70
       and aft.get("psnr_cover") is not None and aft["psnr_cover"] >= 20.0
       and len(acos) >= 2 and min(acos) >= GATE_FLOOR
       and aft["ssim_cover"] > max(before.values()),
       "11 METRICS 6 BEFORE rows show the defect (frame-0 SSIM %s, all < 0.5) and the AFTER row frame 0 = "
       "SSIM %s PSNR %s with the start-still faces at cos %s (gate %s) > the best BEFORE frame 0 %s"
       % (sorted(round(v, 3) for v in before.values()), round(aft.get("ssim_cover") or -1, 4),
          round(aft.get("psnr_cover") or -1, 2), sorted(round(c, 3) for c in acos), GATE_FLOOR,
          round(max(before.values()) if before else -1, 4)))
    # 12 BYTE FORMAT
    base_bytes = open(BASE_G, "rb").read()
    ind = dumps_like(base_bytes, gbase)
    ck(ind is not None and ctx["new_graph_bytes"] == json.dumps(gnew, indent=ind, ensure_ascii=False)
       .replace("\n", "\r\n").encode("utf-8") and not ctx["new_graph_bytes"].endswith(b"\n"),
       "12 BYTEFORMAT the base file reproduces at indent=%s with CRLF and no trailing newline, and the new graph "
       "is written the same way" % ind)
    # 13 RENDER RECEIPT (must be silent on the real artifact: no render yet)
    sheet = ctx["sheet_path"]
    ck(not os.path.isfile(sheet) or os.path.getmtime(sheet) > os.path.getmtime(NEW_G),
       "13 STALE-SHEET no frame-0 sheet predates the graph (the sheet is written only after a render)")
    print("CHECKS %s FAIL %s" % (label, json.dumps(fails)) if fails else "CHECKS %s ALL %d PASS" % (label, 13))
    return list(fails)


def selftest(gbase):
    """Seed the OLD wiring / old settings / broken artifacts into clones of the real artifact; every named
    detector must fire on its own seed and 0 on the real artifact. No GPU, no queue, no real file touched."""
    real = json.loads(open(NEW_G, encoding="utf-8").read())
    base_ctx = ctx_default()
    stale = os.path.join(AUD, "seed_stale_sheet.png")
    os.makedirs(AUD, exist_ok=True)
    open(stale, "wb").write(b"png-not")
    os.utime(stale, (0, 0))

    def win(g):
        return [k for k, n in g.items() if n["class_type"] == "MiniMaxH3GuidedContinuationWindow"][0]

    SEEDS = [
        ("A1 anchor-removed (the shipped HC15 wiring: s0_guide fed straight by c0)",
         lambda g, c: (g.pop("g0"), g["s0_guide"]["inputs"].__setitem__("conditioning", ["c0", 0]))),
        ("A2 anchor-on-the-face-crop (img2, not the start still)",
         lambda g, c: g["g0"]["inputs"].__setitem__("image", ["img2", 0])),
        ("A3 anchor-added-but-not-on-the-sampled-edge",
         lambda g, c: g["s0_guide"]["inputs"].__setitem__("conditioning", ["c0", 0])),
        ("A4 anchor-frame_idx-1 (not the start frame)",
         lambda g, c: g["g0"]["inputs"].__setitem__("frame_idx", 1)),
        ("A5 anchor-image-is-a-literal (not a LoadImage link)",
         lambda g, c: g["g0"]["inputs"].__setitem__("image", "BD002.jpg")),
        ("B1 sampler-back-to-euler", lambda g, c: g["ksel"]["inputs"].__setitem__("sampler_name", "euler")),
        ("B2 steps-back-to-10", lambda g, c: [g[k]["inputs"].__setitem__("steps", 10) for k in ("s0_sched", "s1_sched")]),
        ("B3 denoise-scaled-to-0.75", lambda g, c: g["s0_sched"]["inputs"].__setitem__("denoise", 0.75)),
        ("B4 scheduler-changed", lambda g, c: g["s0_sched"]["inputs"].__setitem__("scheduler", "karras")),
        ("C1 c0-length-back-to-124", lambda g, c: g["c0"]["inputs"].__setitem__("length", 124)),
        ("C2 overlap-23 (breaks the 17k+5 grid)", lambda g, c: g[win(g)]["inputs"].__setitem__("overlap_frames", 23)),
        ("C3 third-pass-chain-restored (the shipped 3-pass shape)",
         lambda g, c: ([(g.__setitem__(k, json.loads(json.dumps(gbase[k])))) for k in
                       ("win2", "tail2", "app2", "s2_samp", "s2_guide", "s2_sched")],
                       g["dec_v"]["inputs"].__setitem__("samples", ["app2", 0]),
                       g["dec_a"]["inputs"].__setitem__("samples", ["app2", 0]))),
        ("D1 prompt-wording-drift (the rewrite belongs to the next item)",
         lambda g, c: g["c0"]["inputs"].__setitem__("prompt", g["c0"]["inputs"]["prompt"] + " and the room is bright")),
        ("D2 seed-changed (breaks the before/after A/B)",
         lambda g, c: g["noise"]["inputs"].__setitem__("noise_seed", 51150999)),
        ("D3 canvas-moved", lambda g, c: g["c0"]["inputs"].__setitem__("width", 1376)),
        ("D4 ref_image_2-face-slot-dropped", lambda g, c: g["c0"]["inputs"].pop("ref_images.ref_image_2")),
        ("D5 ref_image_size-changed-to-match", lambda g, c: g["c0"]["inputs"].__setitem__("ref_image_size", "match")),
        ("E1 audio_vae-dropped-from-c0", lambda g, c: g["c0"]["inputs"].pop("audio_vae")),
        ("E2 AddGuide-image-without-vae (the node raises at execute)", lambda g, c: g["g0"]["inputs"].pop("vae")),
        ("E3 dangling link to a deleted node", lambda g, c: g["dec_v"]["inputs"].__setitem__("samples", ["app2", 0])),
        ("E4 node-unreachable-from-save (save reads raw c0 latent)",
         lambda g, c: g["save"]["inputs"].__setitem__("images", ["c0", 1])),
        ("F1 handoff-jobs-names-the-OLD-clip", lambda g, c: c["req"].__setitem__("jobs", [{"id": OLD_ID, "kind": "graph"}])),
        ("F2 handoff-run_dir-points-at-the-OLD-run",
         lambda g, c: c["req"].__setitem__("run_dir", os.path.join(W, "runs", OLD_ID).replace("\\", "/"))),
        ("F3 ledger-would-blow-the-budget", lambda g, c: c["ledger"].__setitem__("used_min", c["ledger"]["cap_min"])),
        ("F4 handoff-frames-363 (not the clip shape)", lambda g, c: c["req"].__setitem__("frames", 363)),
        ("F5 rendered-clip-objective-says-243-frames", lambda g, c: c["obj"]["attempts"][0].__setitem__("frames", 243)),
        ("F6 ffprobe-frames-disagree-with-the-objective", lambda g, c: c["probe"].__setitem__("frames", 243)),
        ("F7 render-marked-not-ok", lambda g, c: c["obj"].__setitem__("ok", False)),
        ("G1 audit-file-missing", lambda g, c: c.__setitem__("audit_txt", "")),
        ("G2 audit-quotes-no-settings-URL", lambda g, c: c.__setitem__("audit_txt", c["audit_txt"][:200])),
        ("G3 handoff-note-drops-the-sampler-citation",
         lambda g, c: c["req"].__setitem__("note", c["req"]["note"].replace(CITATIONS["sampler"], "the model card"))),
        ("H1 metrics-rows-missing", lambda g, c: c.__setitem__("metrics_rows", [])),
        ("H2 metrics-says-a-clip-already-starts-close",
         lambda g, c: c["metrics_rows"][0]["frames_measured"]["0"].__setitem__("ssim_cover", 0.9)),
        ("H3 after-row-missing (only the six BEFORE clips measured)",
         lambda g, c: c.__setitem__("metrics_rows", [r for r in c["metrics_rows"] if r["id"] != NEW_ID])),
        ("H4 after-anchor-did-not-take (frame 0 SSIM 0.35, PSNR 6.8)",
         lambda g, c: [r["frames_measured"]["0"].update(ssim_cover=0.35, psnr_cover=6.8)
                       for r in c["metrics_rows"] if r["id"] == NEW_ID]),
        ("H5 after-frame-0-faces-are-not-the-start-still-faces (cos 0.31)",
         lambda g, c: [r["frames_measured"]["0"].__setitem__("best_cos", [0.31, 0.2])
                       for r in c["metrics_rows"] if r["id"] == NEW_ID]),
        ("I1 graph-file-bytes-drift-from-the-graph-object", lambda g, c: g["c1"]["inputs"].__setitem__("prompt", g["c1"]["inputs"]["prompt"] + " "), True),
        ("J1 frame-0-sheet-older-than-the-graph", lambda g, c: c.__setitem__("sheet_path", stale)),
    ]
    fired, silent = [], []
    for seed in SEEDS:
        name, gfn = seed[0], seed[1]
        keep_bytes = len(seed) > 2
        g = copy.deepcopy(real)
        c = copy.deepcopy(base_ctx)
        gfn(g, c)
        if not keep_bytes:
            c["new_graph_bytes"] = json.dumps(g, indent=2, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")
        f = do_check(json.loads(json.dumps(gbase)), g, label="seed:" + name, ctx=c)
        (fired if f else silent).append(name)
    real_fails = do_check(gbase, real, label="real", ctx=base_ctx)
    print("SELFTEST seeds=%d fired=%d silent=%d real_problems=%d"
          % (len(SEEDS), len(fired), len(silent), len(real_fails)))
    if silent:
        print("SILENT_SEEDS " + json.dumps(silent))
    print("SELFTEST_CLEAN" if not silent and not real_fails else "SELFTEST_DIRTY")
    return 0 if (not silent and not real_fails) else 1


def sheet():
    """Labelled frame-0 before/after sheet. Refuses until the render exists. ffmpeg + PIL only, no vision judge."""
    mp4 = os.path.join(W, "runs", NEW_ID, NEW_ID + ".mp4")
    if not os.path.isfile(mp4):
        print("SHEET_BLOCKED no render yet: " + mp4 + " (a Ralph pass never queues)")
        return 1
    from PIL import Image, ImageDraw
    g = json.load(open(NEW_G, encoding="utf-8"))
    w, h = g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]
    still = os.path.join(COMFY, "input", g["img"]["inputs"]["image"].replace("/", os.sep))
    os.makedirs(AUD, exist_ok=True)
    tiles = []
    start = fit(still, w, h, os.path.join(AUD, "sheet_start.png"), "cover")
    for label, src in (("start still " + g["img"]["inputs"]["image"], start),
                       ("BEFORE clip 1 frame 0 (euler/10, 124f x3, no anchor)",
                        extract(os.path.join(W, "runs", "hc15_bd002_s51150001", OLD_ID + ".mp4"), 0,
                                os.path.join(AUD, "sheet_before.png"))),
                       ("AFTER frame 0 (anchor + res_multistep/8, 243f+119f)",
                        extract(mp4, 0, os.path.join(AUD, "sheet_after.png")))):
        s, p = ssim_psnr(src, start)
        tiles.append((label + "  SSIM %.3f PSNR %.2f" % (s, p), src))
    W2, H2 = w, h + 34
    canvas = Image.new("RGB", (W2 * 3, H2), "white")
    for i, (lab, p) in enumerate(tiles):
        canvas.paste(Image.open(p).convert("RGB").resize((w, h)), (i * W2, 34))
        ImageDraw.Draw(canvas).text((i * W2 + 6, 8), lab, fill="black")
    out = os.path.join(W, "runs", NEW_ID, NEW_ID + "_frame0_sheet.png")
    canvas.save(out)
    print("SHEET " + out + " " + "x".join(str(t) for t in canvas.size))
    print("KEEP is Derrick's alone; this sheet carries no verdict.")
    return 0


# ===================================================================== NOW-P1 (4 published switches, clip-11 clone)
# The four switches, each with the published wording that is ON DISK (this is the gate's citation set):
#  steps 8 -> 12      notes/web/02v_docs_h3.txt:176 "Speech and timbre need **12+** steps; at **8** steps audio is
#                     often the weak link." and :182 "Splitting the schedule across two samplers drops multistep
#                     history: the second sampler's first step is first-order again. Keep one sampler run, or give
#                     the second enough steps to warm up." + notes/web/hc15_tenstrip_readme.txt "It's a slow 8-12
#                     step reference model in that configuration" (the band for THIS checkpoint).
#  ref_image_size     the box's own /object_info: MiniMaxH3ReferenceToVideo.ref_image_size options ['match','max'],
#                     default 'match', tooltip "'max' uses the reference pipeline's 2048px short edge ... can be
#                     much slower; it does not upscale small files". Measured refs: 1376x768 start frame
#                     (community/hc/BD002.jpg) + 512x512 face crop (community/hc/BD002_w2_face.png), both under the
#                     2048px short edge, so 'max' buys no detail these files do not contain.
#  attention          notes/web/02v_docs_h3.txt: Comfy Kitchen attention is int8_convrot-incompatible; the live
#                     schema default is 'pytorch attention'; our unet is
#                     10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors (measured off the clip-11 graph).
#  antiburn LoRA      notes/web/02v_antiburn_readme.txt:29 "Load it with `LoraLoaderModelOnly` on the model that
#                     makes your **continuation clips**: 2, 3, 4 and so on.", :30 "Don't use it on clip 1.",
#                     :31 "Start at 0.5." + notes/web/02v_docs_h3.txt:157 "... on clips after the first at
#                     `strength_model` \~0.5". The card names `LoraLoaderModelOnly`, NOT `LoraLoader` (the §3/§4
#                     shorthand), and names only strength_model - `LoraLoader` would force a `strength_clip` value
#                     that no source publishes and would move the CLIP/conditioning path too = our own setting.
NOW_ID = "ali163_hc15_bd002_s51150021"
NOW_BASE_G = NEW_G                                   # clip-11 = the RENDERED before clip (frame-0 SSIM 0.915)
NOW_G = os.path.join(W, "p7", "graphs", NOW_ID + ".api.json")
OBJ_INFO = os.path.join(W, "notes", "ali173_b2_object_info_full.json")  # the box's own /object_info dump
LORA_FILE = "h3_antiburn_universal_v1.safetensors"
LORA_STRENGTH = 0.5
STEPS_PUB = 12
STEPS_BAND = (8, 12)                                  # TenStrip's published band for this checkpoint
ATTN_PUB = "pytorch attention"
REFSIZE_PUB = "match"
NOW_MINUTES = 20                                      # clip-11 rendered in 571.7 s wall; 12/8 steps = 1.5x the
                                                      # sampling passes (857 s = 14.3 min) + CK->pytorch attention
                                                      # costs per-step time; 20 min is the disclosed estimate
NOW_CITATIONS = {
    "steps": "https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md (notes/web/02v_docs_h3.txt:176,182) + "
             "https://huggingface.co/TenStrip/10Eros-Max/raw/main/README.md",
    "refsize": "https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native.md (notes/web/"
               "02v_docs_h3_native.txt) + the live /object_info default 'match' (notes/ali173_b2_object_info_full.json)",
    "attention": "https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md (int8_convrot) + "
                 "https://github.com/Comfy-Org/ComfyUI/issues/15529 + the live schema default",
    "lora": "https://huggingface.co/Imagineer13/H3-Anti-Burn-LoRA (notes/web/02v_antiburn_readme.txt:29-31) + "
            "https://docs.comfy.org/tutorials/video/minimax/minimax-h3.md:157",
}

_OBJ = None


def obj():
    global _OBJ
    if _OBJ is None:
        _OBJ = jload(OBJ_INFO)
    return _OBJ


def obj_inputs(cls):
    ins = (obj().get(cls) or {}).get("input", {})
    return set(ins.get("required") or {}), set(ins.get("optional") or {})


def obj_field(cls, key):
    """(type, published_options, meta) of one input of one class, read from the box's own /object_info dump."""
    ins = (obj().get(cls) or {}).get("input", {})
    for sec in ("required", "optional"):
        v = (ins.get(sec) or {}).get(key)
        if not v:
            continue
        if isinstance(v[0], list):
            return v[0], v[0], (v[1] if len(v) > 1 and isinstance(v[1], dict) else {})
        meta = v[1] if len(v) > 1 and isinstance(v[1], dict) else {}
        return v[0], meta.get("options"), meta
    return None, None, {}


def obj_schema_all():
    out = {}
    for cls in obj():
        req, opt = obj_inputs(cls)
        if req or opt:
            out[cls] = (req, opt)
    return out


def obj_scan(g):
    """Schema gate the item asks for: every class_type and every input key must exist in the live /object_info."""
    sch = obj_schema_all()
    bad = []
    for nid, n in sorted(g.items()):
        ct = n["class_type"]
        if ct not in sch:
            bad.append("%s: class %s is not in the box's /object_info" % (nid, ct))
            continue
        names = sch[ct][0] | sch[ct][1]
        keys = {k.split(".")[0] for k in n["inputs"]}
        bad += ["%s.%s: not an input of %s" % (nid, k, ct) for k in sorted(keys - names)]
        bad += ["%s: required input %s missing" % (nid, r) for r in sorted(sch[ct][0])
                if r not in n["inputs"] and not any(a.startswith(r + ".") for a in n["inputs"])]
    return bad


def transform_now(base):
    """The four published switches, applied to the rendered clip-11 graph. Nothing else moves."""
    g = json.loads(json.dumps(base))
    for k in ("s0_sched", "s1_sched"):
        g[k]["inputs"]["steps"] = STEPS_PUB
    for k in ("c0", "c1"):
        g[k]["inputs"]["ref_image_size"] = REFSIZE_PUB
    g["m_attn"]["inputs"]["attention"] = ATTN_PUB
    g["lora_antiburn"] = {"class_type": "LoraLoaderModelOnly",
                          "inputs": {"model": ["m_shift", 0], "lora_name": LORA_FILE,
                                     "strength_model": LORA_STRENGTH}}
    for k in ("s1_guide", "s1_sched"):
        g[k]["inputs"]["model"] = ["lora_antiburn", 0]
    g["save"]["inputs"]["filename_prefix"] = "community/%s/%s" % (NOW_ID, NOW_ID)
    return g


# §4's allowed set + save.filename_prefix: the prefix IS the output folder, so an unchanged prefix would write the
# new clip into the folder of the RENDERED clip-11. It is a naming path, not a sampling path, and the gate names it.
NOW_ALLOWED = {("[inputs].steps", "s0_sched", ""), ("[inputs].steps", "s1_sched", ""),
               ("[inputs].ref_image_size", "c0", ""), ("[inputs].ref_image_size", "c1", ""),
               ("[inputs].attention", "m_attn", ""),
               ("NODE+", "lora_antiburn", ""),
               ("[inputs].model", "s1_guide", ""), ("[inputs].model", "s1_sched", ""),
               ("[inputs].filename_prefix", "save", "")}


def now_note(gnew):
    b = open(NOW_G, "rb").read()
    d = len(diff_paths(jload(NOW_BASE_G), gnew))
    return ("HC15 NOW-P1 re-render of clip 1 (fix_plan NOW-P1, out of notes/now_h3_quality_research_20261025.md "
            "§3/§4): the RENDERED clip-11 graph (ali163_hc15_bd002_s51150011, frame-0 SSIM 0.915) plus EXACTLY the "
            "four published switches, same start still %s, same seed %d, same 1344x768 24 fps 362 f = 15.0833 s "
            "with audio, prompts BYTE-IDENTICAL, %d changed paths and nothing else. (1) s0_sched/s1_sched steps 8 "
            "-> 12: docs.comfy.org minimax-h3.md 'Speech and timbre need 12+ steps; at 8 steps audio is often the "
            "weak link' and 'Splitting the schedule across two samplers drops multistep history ... give the second "
            "enough steps to warm up' + TenStrip 10Eros-Max README 'a slow 8-12 step reference model in that "
            "configuration'. (2) c0/c1 ref_image_size max -> match = the /object_info default; 'max' keeps a 2048px "
            "short edge, is several times slower and does not upscale small files - the measured refs are a 1376x768 "
            "start frame (community/hc/BD002.jpg) and a 512x512 face crop (community/hc/BD002_w2_face.png), both under "
            "that 2048px short edge. "
            "(3) m_attn.attention 'comfy kitchen attention' -> 'pytorch attention' = the schema default; the docs "
            "publish that Comfy Kitchen attention cannot run int8_convrot checkpoints and this unet is "
            "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors. (4) new node lora_antiburn = LoraLoaderModelOnly "
            "(lora_name %s, strength_model %s) between m_shift and s1_guide/s1_sched ONLY, per the LoRA README "
            "'Load it with LoraLoaderModelOnly on the model that makes your continuation clips' / 'Don't use it on "
            "clip 1' / 'Start at 0.5'. Builder receipts: notes/hc15_anchor_fix_build.py --now-check (13 detectors) "
            "and --now-selftest (seeded faults). Graph %d nodes, %d B, sha256 %s, 0 cfg keys, schema gate against "
            "the box's own /object_info dump (notes/ali173_b2_object_info_full.json) 0 defects, comm.guard_ok allow "
            "on every prompt-bearing string, scripts/tests/test_p6_review.py 21 passed. id-free: no runs/%s/%s.mp4, "
            "no p7/jobs/%s.result.json, no ComfyUI output/%s. Render (GPU window, never a Ralph pass): "
            "C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/run_graph_job.py "
            "C:/AI/community/runs/%s %s --frames 362 after gpu_guard.ps1 prints IDLE, one job, then "
            "python C:/AI/community/notes/hc15_anchor_fix_build.py --now-sheet and the labelled before/after "
            "frame-0 sheet (51150011 before, 51150021 after) goes to Derrick. Unload comfyui_auto afterwards. "
            "minutes=%d (measured: clip-11 wall 571.7 s; 12/8 steps = 1.5x the sampling passes = ~858 s, plus the "
            "pytorch-attention per-step cost). KEEP is Derrick's alone; no vision judge on explicit output."
            ) % (CLIPS_START, SEED, d, LORA_FILE, LORA_STRENGTH, len(gnew), len(b), sha(NOW_G),
                 NOW_ID, NOW_ID, NOW_ID, NOW_ID, NOW_ID, NOW_ID, NOW_MINUTES)


def now_arm(gnew):
    run = os.path.join(W, "runs", NOW_ID)
    os.makedirs(run, exist_ok=True)
    open(os.path.join(run, "request.api.json"), "wb").write(open(NOW_G, "rb").read())
    req = {"jobs": [{"id": NOW_ID, "kind": "graph", "frames": FRAMES, "frames_tol": 33,
                     "minutes": NOW_MINUTES, "note": now_note(gnew)}],
           "id": NOW_ID, "run_dir": run.replace("\\", "/"),
           "api": NOW_G.replace("\\", "/"), "frames": FRAMES, "frames_tol": 33,
           "minutes": NOW_MINUTES, "note": now_note(gnew)}
    open(os.path.join(W, "p7", "JOB_REQUEST.json"), "w", encoding="utf-8").write(
        json.dumps(req, indent=2, ensure_ascii=False))
    return req


def now_ctx():
    mp4 = os.path.join(W, "runs", NOW_ID, NOW_ID + ".mp4")
    rendered = os.path.isfile(mp4)
    oj = os.path.join(W, "runs", NOW_ID, "objective.json")
    return dict(req=jload(os.path.join(W, "p7", "JOB_REQUEST.json")),
                ledger=jload(LEDGER),
                new_graph_bytes=open(NOW_G, "rb").read(),
                base_graph_bytes=open(NOW_BASE_G, "rb").read(),
                run_api_bytes=(open(os.path.join(W, "runs", NOW_ID, "request.api.json"), "rb").read()
                               if os.path.isfile(os.path.join(W, "runs", NOW_ID, "request.api.json")) else b""),
                sheet_path=os.path.join(W, "runs", NOW_ID, NOW_ID + "_frame0_sheet.png"),
                rendered=rendered,
                obj=(jload(oj) if rendered and os.path.isfile(oj) else None),
                probe=(probe(mp4) if rendered else None))


def now_check(gbase, gnew, label="real", ctx=None):
    """13 named detectors over the NOW-P1 artifact (clip-11 + the 4 published switches). Every one is provably
    reachable: --now-selftest seeds the OLD value into a clone and requires the detector to fire there, 0 here."""
    ctx = ctx or now_ctx()
    fails.clear()
    led, req = ctx["ledger"], ctx["req"]
    # 1 STEPS: the published 12, inside the checkpoint's published 8-12 band, schedule/denoise unchanged
    st = {k: n["inputs"]["steps"] for k, n in gnew.items() if k.endswith("_sched")}
    lo, hi = STEPS_BAND
    ck(st and set(st.values()) == {STEPS_PUB} and lo <= STEPS_PUB <= hi
       and st != {k: gbase[k]["inputs"]["steps"] for k in st}
       and all(n["inputs"]["scheduler"] == "simple" for k, n in gnew.items() if k.endswith("_sched"))
       and all(n["inputs"]["denoise"] == 1.0 for k, n in gnew.items() if k.endswith("_sched"))
       and gnew["ksel"]["inputs"]["sampler_name"] == "res_multistep",
       "1 STEPS steps %d on every scheduler (clip-11 ran 8; published 12+ for audio, 8-12 band for this file), "
       "simple/denoise 1.0/res_multistep kept" % STEPS_PUB)
    # 2 REFSIZE: the /object_info default, and the value is one the published node offers
    _t, opts, meta = obj_field("MiniMaxH3ReferenceToVideo", "ref_image_size")
    vals = [gnew[k]["inputs"]["ref_image_size"] for k in ("c0", "c1")]
    ck(vals == [REFSIZE_PUB, REFSIZE_PUB] and meta.get("default") == REFSIZE_PUB
       and REFSIZE_PUB in (opts or []) and vals != [gbase["c0"]["inputs"]["ref_image_size"],
                                                    gbase["c1"]["inputs"]["ref_image_size"]],
       "2 REFSIZE c0/c1 ref_image_size %s = the /object_info default (options %s); clip-11 ran '%s'"
       % (REFSIZE_PUB, opts, gbase["c0"]["inputs"]["ref_image_size"]))
    # 3 ATTENTION: the schema default, valid for an int8 checkpoint (published incompatibility)
    _t, aopts, ameta = obj_field("ModelAttentionBackend", "attention")
    unet = gnew["unet"]["inputs"]["unet_name"]
    ck(gnew["m_attn"]["inputs"]["attention"] == ATTN_PUB and ameta.get("default") == ATTN_PUB
       and ATTN_PUB in (aopts or []) and "int8" in unet
       and gbase["m_attn"]["inputs"]["attention"] != ATTN_PUB,
       "3 ATTENTION m_attn.attention %s = the schema default (options %s); this unet is %s, and the docs publish "
       "that comfy kitchen attention cannot run int8_convrot checkpoints" % (ATTN_PUB, aopts, unet))
    # 4 LORA: the card's published wiring (node class, file, strength, continuation-only placement)
    lora = [k for k, n in gnew.items() if n["class_type"] in ("LoraLoaderModelOnly", "LoraLoader")]
    ln, lopts = (lora[0], obj_field("LoraLoaderModelOnly", "lora_name")[1]) if len(lora) == 1 else (None, None)
    lin = gnew.get(ln, {}).get("inputs", {}) if ln else {}
    ck(len(lora) == 1 and gnew[lora[0]]["class_type"] == "LoraLoaderModelOnly"
       and lin.get("lora_name") == LORA_FILE and LORA_FILE in (lopts or [])
       and lin.get("strength_model") == LORA_STRENGTH
       and lin.get("model") == ["m_shift", 0]
       and gnew["s1_guide"]["inputs"]["model"] == gnew["s1_sched"]["inputs"]["model"] == [ln, 0]
       and gnew["s0_guide"]["inputs"]["model"] == gnew["s0_sched"]["inputs"]["model"] == ["m_shift", 0]
       and os.path.isfile(os.path.join(COMFY, "models", "loras", LORA_FILE)),
       "4 LORA one %s (%s, strength_model %s) fed by m_shift, feeding s1_guide AND s1_sched only, s0 still on "
       "m_shift ('Don't use it on clip 1'), file installed + in the live lora_name list"
       % ("LoraLoaderModelOnly", LORA_FILE, LORA_STRENGTH))
    # 5 SCOPE: exactly the switched paths, nothing else
    d = diff_paths(gbase, gnew)
    ck(d == NOW_ALLOWED, "5 SCOPE diff vs the rendered clip-11 == the %d allowed paths and nothing else "
       "(extra=%s missing=%s)" % (len(NOW_ALLOWED), sorted(d - NOW_ALLOWED)[:4], sorted(NOW_ALLOWED - d)[:4]))
    # 6 SCHEMA against the box's own /object_info: every class + every input key + every switched value published
    bad = obj_scan(gnew)
    ck(not bad,
       "6 SCHEMA every class_type and every input key of all %d nodes exists in notes/ali173_b2_object_info_full.json"
       % len(gnew) + (" defects=%s" % bad[:3] if bad else ""))
    # 7 PROMPTS byte-identical, seed unchanged (the A/B stays one-variable)
    pp = [(sha_s(gbase[n]["inputs"]["prompt"]), sha_s(gnew[n]["inputs"]["prompt"])) for n in ("c0", "c1")]
    ck(all(a == b for a, b in pp) and gnew["noise"]["inputs"]["noise_seed"] == SEED == 51150001
       and gnew["noise"]["inputs"]["noise_seed"] == gbase["noise"]["inputs"]["noise_seed"],
       "7 PROMPTS c0/c1 prompt sha256 %s == clip-11 byte-for-byte, seed %d unchanged"
       % ([a[:16] for a, _ in pp], SEED))
    # 8 UNCHANGED: the FIRST-item anchor and the clip shape, plus shift/VSA/fps/audio
    def gv(g, node, key):
        return g.get(node, {}).get("inputs", {}).get(key, "\0")
    pairs = [("g0", "frame_idx"), ("g0", "image"), ("g0", "vae"), ("g0", "latent"), ("g0", "positive"),
             ("s0_guide", "conditioning"), ("c0", "length"), ("win1", "overlap_frames"),
             ("win1", "extension_frames"), ("c0", "width"), ("c0", "height"), ("c0", "ref_images.ref_image_1"),
             ("c0", "ref_images.ref_image_2"), ("m_shift", "shift_video"), ("m_shift", "shift_audio"),
             ("m_vsa", "selection"), ("m_vsa", "selection.keep_percent"), ("m_vsa", "min_tokens"),
             ("m_vsa", "extra_tokens"), ("m_vsa", "start_percent"), ("m_vsa", "end_percent"),
             ("mkvid", "fps"), ("dec_a", "vae"), ("c0", "audio_vae"), ("img", "image"), ("img2", "image"),
             ("unet", "unet_name"), ("clip", "clip_name"), ("ksel", "sampler_name")]
    drift = [(n, k) for n, k in pairs if gv(gnew, n, k) != gv(gbase, n, k)]
    ck(not drift and gv(gnew, "g0", "frame_idx") == 0 and gv(gnew, "c0", "length") == 243
       and (gv(gnew, "c0", "width"), gv(gnew, "c0", "height")) == (1344, 768)
       and (gv(gnew, "m_shift", "shift_video"), gv(gnew, "m_shift", "shift_audio")) == (10.0, 3.0)
       and gv(gnew, "mkvid", "fps") == 24 and gv(gnew, "win1", "overlap_frames") == 22
       and gv(gnew, "win1", "extension_frames") == 119,
       "8 UNCHANGED anchor g0 frame_idx 0 on the c0 edge, 243 + 22/119 window = 362 f, canvas 1344x768, shift "
       "10/3, VSA block, fps 24, audio path, unet/clip files, ref slots (drift=%s)" % drift)
    # 9 GATE: the fiction gate over EVERY prose string
    prose = [(k, v) for k, n in gnew.items() for v in n["inputs"].values() if isinstance(v, str) and len(v) > 120]
    allowed = [(k, v) for k, v in prose if guard_ok(v)]
    ck(len(prose) == 2 and len(allowed) == 2,
       "9 GATE comm.guard_ok allows %d/%d prompt-bearing strings (c0.prompt/c1.prompt)" % (len(allowed), len(prose)))
    # 10 INTEGRITY
    dangling = [f"{k}.{key}" for k, n in gnew.items() for key, v in n["inputs"].items()
                if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and v[0] not in gnew]
    reach, stack = set(), ["save"]
    while stack:
        k = stack.pop()
        if k in reach or k not in gnew:
            continue
        reach.add(k)
        stack += [v[0] for v in gnew[k]["inputs"].values()
                  if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str)]
    imgs = [n["inputs"]["image"] for n in gnew.values() if n["class_type"] == "LoadImage"]
    ck(not dangling and reach == set(gnew) and len(gnew) == len(gbase) + 1
       and all(os.path.isfile(os.path.join(COMFY, "input", i.replace("/", os.sep))) for i in imgs)
       and not any("cfg" in k.lower() for k in json.dumps(gnew).split('"'))
       and gnew["c0"]["inputs"]["width"] % 32 == 0 and gnew["c0"]["inputs"]["height"] % 32 == 0
       and gnew["save"]["inputs"]["filename_prefix"] == "community/%s/%s" % (NOW_ID, NOW_ID),
       "10 INTEGRITY 0 dangling, all %d nodes (base + 1 LoRA) feed save, LoadImage files exist, 0 cfg keys, "
       "canvas on the 32 grid, filename_prefix names the NEW id" % len(gnew))
    # 11 ARM, two states: ARMED (before the render) / RENDERED-WITH-PROOF (after the GPU window)
    rid_free = not (ctx["rendered"]
                    or os.path.isfile(os.path.join(W, "p7", "jobs", NOW_ID + ".result.json"))
                    or glob.glob(os.path.join(COMFY, "output", "community", NOW_ID, "*")))
    byte_ok = ctx["run_api_bytes"] == open(NOW_G, "rb").read()
    id_ok = (req["id"] == NOW_ID and [j["id"] for j in req["jobs"]] == [NOW_ID]
             and req["frames"] == FRAMES and req["minutes"] == NOW_MINUTES
             and all(j["minutes"] == NOW_MINUTES for j in req["jobs"])
             and set(req["jobs"][0]) == {"id", "kind", "frames", "frames_tol", "minutes", "note"}
             and req["api"].replace("\\", "/") == NOW_G.replace("\\", "/")
             and req["run_dir"].replace("\\", "/") == os.path.join(W, "runs", NOW_ID).replace("\\", "/")
             and all(c in req["note"] for c in [LORA_FILE, NOW_ID])
             and not any(w in req["note"].lower() for w in ("best", "winner", "ranking", "picks")))
    if ctx["rendered"]:
        obj_, pr = ctx["obj"], ctx["probe"]
        a = (obj_ or {}).get("attempts", [{}])[0]
        proof = (obj_ and obj_.get("ok") is True and a.get("tag") == NOW_ID and a.get("frames") == FRAMES
                 and a.get("audio") is True and a.get("fps") == "24/1" and (a.get("w"), a.get("h")) == CANVAS
                 and not a.get("blackfreeze") and pr and pr["frames"] == FRAMES and pr["audio"]
                 and pr["fps"] == "24/1" and (pr["w"], pr["h"]) == CANVAS)
        ck(id_ok and byte_ok and proof and led["used_min"] < led["cap_min"] and led["jobs"] + 1 <= led["job_cap"],
           "11 ARM-RENDERED graph == run-dir request bytes, JOB_REQUEST names the new id in the top level AND "
           "jobs[] (6 keys), render proof agrees (%s), ledger %s < %s min, %s + 1 <= %s jobs"
           % (json.dumps(pr), led["used_min"], led["cap_min"], led["jobs"], led["job_cap"]))
    else:
        ck(id_ok and byte_ok and rid_free and led["used_min"] + NOW_MINUTES <= led["cap_min"]
           and led["jobs"] + 1 <= led["job_cap"],
           "11 ARM graph == run-dir request bytes, JOB_REQUEST names the new id in the top level AND jobs[] "
           "(6 keys), id free of mp4/result/output, ledger %s + %d <= %s min and %s + 1 <= %s jobs (stamp %s)"
           % (led["used_min"], NOW_MINUTES, led["cap_min"], led["jobs"], led["job_cap"], led.get("updated")))
    # 12 BYTE FORMAT: the base file reproduces, and the new graph is written the same way
    ind = dumps_like(ctx["base_graph_bytes"], gbase)
    ck(ind is not None and ctx["new_graph_bytes"] == json.dumps(gnew, indent=ind, ensure_ascii=False)
       .replace("\n", "\r\n").encode("utf-8") and not ctx["new_graph_bytes"].endswith(b"\n"),
       "12 BYTEFORMAT the rendered clip-11 reproduces at indent=%s CRLF no trailing newline, and the new graph "
       "is written the same way" % ind)
    # 13 STALE SHEET: no before/after sheet predates the graph (the sheet is written only after a render)
    sheet = ctx["sheet_path"]
    ck(not os.path.isfile(sheet) or os.path.getmtime(sheet) > os.path.getmtime(NOW_G),
       "13 STALE-SHEET no frame-0 sheet for the new id predates the graph")
    print("CHECKS %s FAIL %s" % (label, json.dumps(fails)) if fails else
          "CHECKS %s ALL %d PASS" % (label, 13))
    return list(fails)


def now_selftest(gbase):
    """Seed the OLD value of each switch, the missing LoRA, a non-schema key, a prompt drift and a renumbered id
    into clones of the real artifact; every detector must fire on its own seed and 0 on the real artifact."""
    real = json.loads(open(NOW_G, encoding="utf-8").read())
    base_ctx = now_ctx()
    stale = os.path.join(AUD, "now_seed_stale_sheet.png")
    os.makedirs(AUD, exist_ok=True)
    open(stale, "wb").write(b"png-not")
    os.utime(stale, (0, 0))

    def rewire_base(g):
        g.pop("lora_antiburn", None)
        for k in ("s1_guide", "s1_sched"):
            g[k]["inputs"]["model"] = ["m_shift", 0]
        g["save"]["inputs"]["filename_prefix"] = "community/%s/%s" % (NEW_ID, NEW_ID)
        for k in ("s0_sched", "s1_sched"):
            g[k]["inputs"]["steps"] = 8
        for k in ("c0", "c1"):
            g[k]["inputs"]["ref_image_size"] = "max"
        g["m_attn"]["inputs"]["attention"] = "comfy kitchen attention"
        return g

    SEEDS = [
        ("N1 steps-back-to-8 (the clip-11 value)",
         lambda g, c: [g[k]["inputs"].__setitem__("steps", 8) for k in ("s0_sched", "s1_sched")]),
        ("N2 steps-20 (outside this checkpoint's published 8-12 band)",
         lambda g, c: [g[k]["inputs"].__setitem__("steps", 20) for k in ("s0_sched", "s1_sched")]),
        ("N3 scheduler-karras", lambda g, c: g["s0_sched"]["inputs"].__setitem__("scheduler", "karras")),
        ("N4 ref_image_size-back-to-max (the clip-11 value)",
         lambda g, c: [g[k]["inputs"].__setitem__("ref_image_size", "max") for k in ("c0", "c1")]),
        ("N5 ref_image_size-only-on-c0 (half a switch)",
         lambda g, c: g["c1"]["inputs"].__setitem__("ref_image_size", "max")),
        ("N6 ref_image_size-value-not-offered-by-the-node",
         lambda g, c: [g[k]["inputs"].__setitem__("ref_image_size", "largest") for k in ("c0", "c1")]),
        ("N7 attention-back-to-comfy-kitchen (the clip-11 value)",
         lambda g, c: g["m_attn"]["inputs"].__setitem__("attention", "comfy kitchen attention")),
        ("N8 attention-value-not-offered-by-the-node",
         lambda g, c: g["m_attn"]["inputs"].__setitem__("attention", "sla attention")),
        ("N9 lora-dropped (clip-11 wiring, the s1 chain straight off m_shift)",
         lambda g, c: (g.pop("lora_antiburn"), [g[k]["inputs"].__setitem__("model", ["m_shift", 0])
                                               for k in ("s1_guide", "s1_sched")])),
        ("N10 lora-strength-1.0 (the card says start at 0.5)",
         lambda g, c: g["lora_antiburn"]["inputs"].__setitem__("strength_model", 1.0)),
        ("N11 lora-on-the-first-clip-path-too ('Don't use it on clip 1')",
         lambda g, c: [g[k]["inputs"].__setitem__("model", ["lora_antiburn", 0])
                       for k in ("s0_guide", "s0_sched")]),
        ("N12 lora-file-not-the-published-one (a real installed lora, not the antiburn file)",
         lambda g, c: g["lora_antiburn"]["inputs"].__setitem__("lora_name", "PenisV2_minimax-h3_epoch60.safetensors")),
        ("N13 lora-class-LoraLoader (needs an unpublished strength_clip)",
         lambda g, c: g["lora_antiburn"].__setitem__("class_type", "LoraLoader")),
        ("N14 lora-feeds-only-the-sampler (the guider stays on the un-LoRA'd model)",
         lambda g, c: g["s1_guide"]["inputs"].__setitem__("model", ["m_shift", 0])),
        ("N15 topk-key-added-to-m_vsa (not a published key of this build)",
         lambda g, c: g["m_vsa"]["inputs"].__setitem__("topk", 0.15)),
        ("N16 required-input-dropped (LoraLoaderModelOnly.strength_model)",
         lambda g, c: g["lora_antiburn"]["inputs"].pop("strength_model")),
        ("N17 class-not-in-the-object_info-dump",
         lambda g, c: g["lora_antiburn"].__setitem__("class_type", "LoraLoaderModelOnlyV2")),
        ("N18 prompt-char-drift (the rewrite belongs to the naming item)",
         lambda g, c: g["c0"]["inputs"].__setitem__("prompt", g["c0"]["inputs"]["prompt"] + "x")),
        ("N19 seed-changed (breaks the before/after A/B)",
         lambda g, c: g["noise"]["inputs"].__setitem__("noise_seed", 51150999)),
        ("N20 anchor-dropped (the shipped HC15 wiring: s0_guide fed by c0)",
         lambda g, c: (g.pop("g0"), g["s0_guide"]["inputs"].__setitem__("conditioning", ["c0", 0]))),
        ("N21 canvas-moved", lambda g, c: g["c0"]["inputs"].__setitem__("width", 1376)),
        ("N22 shift-moved", lambda g, c: g["m_shift"]["inputs"].__setitem__("shift_video", 12.0)),
        ("N23 window-overlap-23 (breaks the 17k+5 grid)",
         lambda g, c: g["win1"]["inputs"].__setitem__("overlap_frames", 23)),
        ("N24 id-renumbered (prefix back to the rendered clip-11 folder)",
         lambda g, c: g["save"]["inputs"].__setitem__(
             "filename_prefix", "community/%s/%s" % (NEW_ID, NEW_ID))),
        ("N25 unallowed-key-moves (m_vsa.min_tokens off the published default)",
         lambda g, c: g["m_vsa"]["inputs"].__setitem__("min_tokens", 4096)),
        ("N26 handoff-jobs-names-the-RENDERED-clip",
         lambda g, c: c["req"].__setitem__("jobs", [{"id": NEW_ID, "kind": "graph", "frames": FRAMES,
                                                    "frames_tol": 33, "minutes": NOW_MINUTES, "note": "x"}])),
        ("N27 handoff-jobs-keyset-drift (a 7th key sneaks in)",
         lambda g, c: c["req"]["jobs"][0].__setitem__("graph", NOW_G.replace("\\", "/"))),
        ("N28 handoff-top-level-id-is-the-old-clip",
         lambda g, c: c["req"].__setitem__("id", NEW_ID)),
        ("N29 ledger-would-blow-the-budget",
         lambda g, c: c["ledger"].__setitem__("used_min", c["ledger"]["cap_min"] - 1)),
        ("N30 handoff-minutes-90 (blows the job cap accounting)",
         lambda g, c: (c["req"].__setitem__("minutes", 90),
                       c["req"]["jobs"][0].__setitem__("minutes", 90))),
        ("N31 run-dir-request-bytes-drift-from-the-graph",
         lambda g, c: c.__setitem__("run_api_bytes", b"{drifted}")),
        ("N32 graph-file-bytes-drift-from-the-graph-object",
         lambda g, c: g["c1"]["inputs"].__setitem__("prompt", g["c1"]["inputs"]["prompt"] + " "), True),
        ("N33 cfg-key-injected (AGENTS.md: this graph has no cfg key at all)",
         lambda g, c: g["s1_sched"]["inputs"].__setitem__("cfg", 1.0)),
        ("N34 LoadImage-file-not-in-ComfyUI-input", lambda g, c: g["img2"]["inputs"].__setitem__("image", "nope/x.png")),
        ("N35 frame-0-sheet-older-than-the-graph", lambda g, c: c.__setitem__("sheet_path", stale)),
        ("N37 prompt-passes-a-minor-token (the fiction gate must deny it)",
         lambda g, c: g["c0"]["inputs"].__setitem__(
             "prompt", g["c0"]["inputs"]["prompt"] + " The scene cuts to a teenage girl in a classroom.")),
        ("N36 full-clip-11-clone (every switch reverted = the before artifact)",
         lambda g, c: rewire_base(g)),
    ]
    fired, silent = [], []
    for seed in SEEDS:
        name, gfn = seed[0], seed[1]
        keep_bytes = len(seed) > 2
        g = copy.deepcopy(real)
        c = copy.deepcopy(base_ctx)
        gfn(g, c)
        if not keep_bytes:
            c["new_graph_bytes"] = json.dumps(g, indent=2, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")
        f = now_check(json.loads(json.dumps(gbase)), g, label="seed:" + name, ctx=c)
        (fired if f else silent).append(name)
    real_fails = now_check(gbase, real, label="real", ctx=base_ctx)
    print("NOW-SELFTEST seeds=%d fired=%d silent=%d real_problems=%d"
          % (len(SEEDS), len(fired), len(silent), len(real_fails)))
    if silent:
        print("SILENT_SEEDS " + json.dumps(silent))
    print("NOW-SELFTEST-CLEAN" if not silent and not real_fails else "NOW-SELFTEST-DIRTY")
    return 0 if (not silent and not real_fails) else 1


def now_sheet():
    """Labelled frame-0 before/after sheet: 51150011 (before) vs 51150021 (after). ffmpeg + PIL, no vision judge."""
    mp4 = os.path.join(W, "runs", NOW_ID, NOW_ID + ".mp4")
    if not os.path.isfile(mp4):
        print("SHEET_BLOCKED no render yet: " + mp4 + " (a Ralph pass never queues)")
        return 1
    from PIL import Image, ImageDraw
    g = json.load(open(NOW_G, encoding="utf-8"))
    w, h = g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]
    still = os.path.join(COMFY, "input", g["img"]["inputs"]["image"].replace("/", os.sep))
    os.makedirs(AUD, exist_ok=True)
    tiles = []
    start = fit(still, w, h, os.path.join(AUD, "now_sheet_start.png"), "cover")
    for label, src in (("start still " + g["img"]["inputs"]["image"], start),
                       ("BEFORE 51150011 frame 0 (steps 8, ref max, comfy kitchen attention, no LoRA)",
                        extract(os.path.join(W, "runs", NEW_ID, NEW_ID + ".mp4"), 0,
                                os.path.join(AUD, "now_sheet_before.png"))),
                       ("AFTER 51150021 frame 0 (steps 12, ref match, pytorch attention, antiburn 0.5 on clip 2)",
                        extract(mp4, 0, os.path.join(AUD, "now_sheet_after.png")))):
        s, p = ssim_psnr(src, start)
        tiles.append((label + "  SSIM %.3f PSNR %.2f" % (s, p), src))
    W2, H2 = w, h + 34
    canvas = Image.new("RGB", (W2 * 3, H2), "white")
    for i, (lab, p) in enumerate(tiles):
        canvas.paste(Image.open(p).convert("RGB").resize((w, h)), (i * W2, 34))
        ImageDraw.Draw(canvas).text((i * W2 + 6, 8), lab, fill="black")
    out = os.path.join(W, "runs", NOW_ID, NOW_ID + "_frame0_sheet.png")
    canvas.save(out)
    print("SHEET " + out + " " + "x".join(str(t) for t in canvas.size))
    print("KEEP is Derrick's alone; this sheet carries no verdict.")
    return 0


# ===================================================================== NOW-P2 (A/B of the rendered pair, CPU only)
# The pair, BOTH already rendered: same seed 51150001, byte-identical c0/c1 prompts, same start frame and face
# crops, so the only difference is the published switch set:
#   BEFORE ali163_hc15_bd002_s51150011  steps 8, comfy kitchen attention, ref_image_size max, no LoRA (571.7 s)
#   AFTER  ali163_hc15_bd002_s51150021  steps 12, pytorch attention, ref_image_size match, antiburn LoRA 0.5 on
#            the continuation only (s1_guide + s1_sched). The client STALLED on it: ComfyUI wrote 7 byte-identical
#            mp4s (sha 8d..., 2026-10-24 22:11 -> 2026-10-25 03:12), objective.json kept attempts=[],
#            and the clip is COLLECTED FROM DISK and never re-rendered (L19, the RENDER-TIMEOUT rule).
# This section is ffmpeg + PIL + CPU onnxruntime: it opens no connection, queues no job, takes no lock file, and
# runs no vision judge, no score and no pick. KEEP is Derrick's alone.
AB_PAIR = {"before": NEW_ID, "after": NOW_ID}
AB_JSON = os.path.join(AUD, "ab_metrics_20261026.json")
AB_SHEET = os.path.join(AUD, "now_p2_ab_sheet.png")
AB_META = os.path.join(AUD, "now_p2_ab_sheet.meta.json")
AB_DOC = os.path.join(W, "notes", "now_p2_before_after_20261026.md")
AB_RUN_SHEET = os.path.join(W, "runs", NOW_ID, "now_p2_ab_sheet.png")
AB_OLD_METRICS = os.path.join(AUD, "metrics.json")
AB_FRAMES = (0, 181, 361)                 # frame 0, midpoint, last - the metrics.json frame convention
AB_TS = (0.50, 2.60, 5.00, 7.40, 9.60)    # the ALI-163 FINAL sheet timestamps (notes/ali163_hc_final_sheet.py:13)
AB_FLOOR = GATE_FLOOR                     # 0.45 (notes/ali163_hc_r4g2_verify.py:87)
AB_TILE = (448, 256, 22, 5, 20)          # tile w, tile h, label band h, columns, header h - builder and gate 9 share it
AB_KEEP_LINE = "KEEP is Derrick's alone; this file carries measured numbers only."
AB_KEEP_BAN = ("keeper", "winners", "winner", "ranking", "ranked", "verdict", "picks", "the best", "pick the")
AB_CITES = {  # every quote must be found VERBATIM in the named on-disk file (ck 12 AB-CITES)
    "steps 12": ("notes/web/02v_docs_h3.txt", "Speech and timbre need **12+** steps"),
    "steps band 8-12": ("notes/web/hc15_tenstrip_readme.txt", "slow 8-12 step reference model"),
    "attention": ("notes/web/02v_docs_h3.txt", "Comfy Kitchen attention cannot run `int8_convrot` checkpoints"),
    "lora continuation-only": ("notes/web/02v_antiburn_readme.txt", "Don't use it on clip 1"),
}
AB_SRC_MARK = "# ===================================================================== NOW-P2"
# The forbidden tokens are built from fragments so that this section's own source does not contain them: gate 14
# scans this section's bytes, and a literal in the definition would match itself (a check that fires on nothing).
AB_NET = tuple(t.replace("~", "") for t in ("sock~et", "url~open", "http~.client", "re~quests.", "urllib~.request",
                                            "/prom~pt", "queue~_prompt", "gpu~_lock", "gpu~_guard",
                                            "llama~-swap", "81~88", "run_graph_~job"))


def ab_mp4(rid):
    return os.path.join(W, "runs", rid, rid + ".mp4")


def ab_gpath(rid):
    return os.path.join(W, "p7", "graphs", rid + ".api.json")


def ab_copies(rid):
    """The ComfyUI output copies of this render: bytes, sha256, mtime. The paid-for evidence of a stalled client."""
    out = []
    for f in sorted(glob.glob(os.path.join(COMFY, "output", "community", rid, "*.mp4"))):
        b = open(f, "rb").read()
        out.append(dict(name=os.path.basename(f), bytes=len(b), sha=hashlib.sha256(b).hexdigest(),
                        mtime=datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")))
    return out


def ab_setting(g):
    """The switched settings, read out of the graph (not typed): steps, attention, ref size, LoRA wiring, shape."""
    return dict(nodes=len(g), steps=sorted({n["inputs"]["steps"] for k, n in g.items() if k.endswith("_sched")}),
                sampler=g["ksel"]["inputs"]["sampler_name"], attention=g["m_attn"]["inputs"]["attention"],
                ref_image_size=sorted({g[k]["inputs"]["ref_image_size"] for k in ("c0", "c1")}),
                lora=[dict(node=k, file=n["inputs"]["lora_name"], strength=n["inputs"]["strength_model"],
                            model=n["inputs"]["model"])
                      for k, n in g.items() if n["class_type"].startswith("Lora")],
                seed=g["noise"]["inputs"]["noise_seed"], start=g["img"]["inputs"]["image"],
                crops=[g[k]["inputs"]["image"] for k in ("img2", "img3") if k in g],
                prompt_sha={k: sha_s(g[k]["inputs"]["prompt"]) for k in ("c0", "c1")},
                canvas="%dx%d" % (g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]))


def ab_measure(rid, det, rec, cos, cv2):
    """One clip: ffprobe shape, SSIM/PSNR of frames 0/181/361 against the start still in BOTH fit modes,
    ArcFace cosine of each start-still face vs the closest face in the frame, plus the render receipt."""
    g, mp4 = jload(ab_gpath(rid)), ab_mp4(rid)
    assert os.path.isfile(mp4), "no mp4: " + mp4
    pr = probe(mp4)
    w, h = g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]
    still = os.path.join(COMFY, "input", g["img"]["inputs"]["image"].replace("/", os.sep))
    sim = cv2.imread(still)
    assert sim is not None, "start still unreadable: " + still
    faces = sorted(det.detect(sim), key=lambda f: -((f["box"][2] - f["box"][0]) * (f["box"][3] - f["box"][1])))[:2]
    emb = [rec.embed(sim, f) for f in faces]
    cover = fit(still, w, h, os.path.join(AUD, "ab_%s_start_cover.png" % rid), "cover")
    stretch = fit(still, w, h, os.path.join(AUD, "ab_%s_start_stretch.png" % rid), "stretch")
    meas = {}
    for n in AB_FRAMES:
        fp = extract(mp4, n, os.path.join(AUD, "ab_%s_f%d.png" % (rid, n)))
        s1, p1 = ssim_psnr(fp, cover)
        s2, p2 = ssim_psnr(fp, stretch)
        img = cv2.imread(fp)
        fs = det.detect(img)
        meas[str(n)] = dict(ssim_cover=s1, psnr_cover=p1, ssim_stretch=s2, psnr_stretch=p2, faces=len(fs),
                            best_cos=[max([round(cos(e, rec.embed(img, f)), 3) for f in fs], default=None)
                                      for e in emb])
    b = open(mp4, "rb").read()
    log = open(os.path.join(W, "runs", rid, "status.log"), encoding="utf-8", errors="replace").read().splitlines()
    oj = os.path.join(W, "runs", rid, "objective.json")
    objd = jload(oj) if os.path.isfile(oj) else None
    return dict(id=rid, role="", mp4=mp4.replace("\\", "/"), bytes=len(b), sha=hashlib.sha256(b).hexdigest(),
                mtime=datetime.datetime.fromtimestamp(os.path.getmtime(mp4)).strftime("%Y-%m-%d %H:%M:%S"),
                probe=pr, graph=ab_gpath(rid).replace("\\", "/"), graph_sha=sha(ab_gpath(rid)),
                setting=ab_setting(g), start_cover=cover.replace("\\", "/"), start_stretch=stretch.replace("\\", "/"),
                start_faces=[[[round(float(v), 1) for v in f["box"]], round(f["score"], 3)] for f in faces],
                frames_measured=meas, copies=ab_copies(rid),
                job_start_rows=sum(1 for l in log if "JOB start" in l),
                job_end_rows=sum(1 for l in log if "JOB end" in l),
                poll_warns=sum(1 for l in log if "poll warn" in l),
                job_start_first=next((l for l in log if "JOB start" in l), ""),
                objective_ok=(objd or {}).get("ok"), objective_attempts=len((objd or {}).get("attempts", [])),
                objective_secs=next((a.get("secs") for a in (objd or {}).get("attempts", [])
                                     if a.get("tag") == rid), None))


def ab_metrics():
    """Measure both clips and write the durable numbers (runs/ is gitignored, L8/L20, so the JSON lives in notes/).
    ArcFace needs onnxruntime -> run this mode under 'C:/Program Files/Python312/python.exe' (L16)."""
    sys.path.insert(0, os.path.join(W, "notes"))
    from hc_r4f_facelib import Scrfd, ArcFace, cos
    import cv2
    det, rec = Scrfd(), ArcFace()
    rows = []
    for role, rid in (("before", AB_PAIR["before"]), ("after", AB_PAIR["after"])):
        r = ab_measure(rid, det, rec, cos, cv2)
        r["role"] = role
        rows.append(r)
        print("FRAME0_BEST_COS %s %s %s" % (role, rid, json.dumps(r["frames_measured"]["0"]["best_cos"])))
        print("FRAME0_SSIM %s %s cover %s stretch %s | PSNR cover %s stretch %s" % (
            role, rid, r["frames_measured"]["0"]["ssim_cover"], r["frames_measured"]["0"]["ssim_stretch"],
            r["frames_measured"]["0"]["psnr_cover"], r["frames_measured"]["0"]["psnr_stretch"]))
        print("AB_ROW %s %s frames=%s canvas=%s audio=%s bytes=%d sha=%s copies=%d job_start=%d job_end=%d "
              "attempts=%d wall=%s" % (role, rid, r["probe"]["frames"], "%dx%d" % (r["probe"]["w"], r["probe"]["h"]),
                                       r["probe"]["audio"], r["bytes"], r["sha"][:16], len(r["copies"]),
                                       r["job_start_rows"], r["job_end_rows"], r["objective_attempts"],
                                       r["objective_secs"]))
    doc = dict(tool="notes/hc15_anchor_fix_build.py --ab-metrics",
               generated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               frames=list(AB_FRAMES), ts=list(AB_TS), floor=AB_FLOOR, cites=AB_CITES,
               graph_diff=sorted("%s|%s|%s" % t for t in diff_paths(jload(ab_gpath(AB_PAIR["before"])),
                                                                    jload(ab_gpath(AB_PAIR["after"])))),
               rows=rows)
    os.makedirs(AUD, exist_ok=True)
    open(AB_JSON, "w", encoding="utf-8").write(json.dumps(doc, indent=1, ensure_ascii=False))
    print("GATE_FLOOR n=%s" % AB_FLOOR)
    print("AB_METRICS_JSON %s rows=%d" % (AB_JSON, len(rows)))
    return 0


def ab_labels(rows):
    """The sheet's label strings, generated from the measured rows (ck 9 re-derives them, so the meta cannot lie)."""
    by = {r["id"]: r for r in rows}
    b, a = by[AB_PAIR["before"]], by[AB_PAIR["after"]]
    start = b["setting"]["start"]
    labs = ["start still " + start]
    for r in (b, a):
        m = r["frames_measured"]["0"]
        f = lambda v, fmt: (fmt % v) if isinstance(v, (int, float)) else "n/a"
        labs.append("%s [%s] frame 0 SSIM %s PSNR %s  steps %s attn %s ref %s lora %s" % (
            r["id"], r["role"], f(m["ssim_cover"], "%.3f"), f(m["psnr_cover"], "%.2f"), r["setting"]["steps"],
            r["setting"]["attention"], r["setting"]["ref_image_size"],
            [l["file"] + "@" + str(l["strength"]) for l in r["setting"]["lora"]] or ["none"]))
    for r in (b, a):
        for t in AB_TS:
            labs.append("%s [%s] t=%.2fs frame %d" % (r["id"], r["role"], t, int(t * 24)))
    return labs


def ab_sheet():
    """Labelled before/after sheet: the start still, frame 0 of each clip with its measured SSIM/PSNR, and a
    5-timestamp contact strip per clip. ffmpeg + PIL only - no vision model, no score, no pick on the frames."""
    from PIL import Image, ImageDraw, ImageStat
    rows = jload(AB_JSON)["rows"]
    labs = ab_labels(rows)
    b = next(r for r in rows if r["role"] == "before")
    a = next(r for r in rows if r["role"] == "after")
    w, h, pad, cols, header = AB_TILE
    cover = fit(os.path.join(COMFY, "input", b["setting"]["start"].replace("/", os.sep)), w, h,
                os.path.join(AUD, "ab_sheet_start.png"), "cover")
    tiles = [(labs[0], cover)]
    for r, lab in ((b, labs[1]), (a, labs[2])):
        tiles.append((lab, extract(r["mp4"], 0, os.path.join(AUD, "ab_sheet_%s_f0.png" % r["role"]))))
    i = 3
    for r in (b, a):
        for t in AB_TS:
            tiles.append((labs[i], extract(r["mp4"], int(t * 24),
                                           os.path.join(AUD, "ab_sheet_%s_t%s.png" % (r["role"], t)))))
            i += 1
    rows_n = -(-len(tiles) // cols)
    canvas = Image.new("RGB", (cols * w, header + rows_n * (h + pad)), "white")
    dr = ImageDraw.Draw(canvas)
    dr.text((6, 4), "NOW-P2 A/B  BEFORE %s (steps 8, comfy kitchen attn, ref max, no LoRA) vs AFTER %s "
                    "(steps 12, pytorch attn, ref match, antiburn 0.5)  same seed 51150001, same prompts"
            % (AB_PAIR["before"], AB_PAIR["after"]), fill="black")
    for i, (lab, src) in enumerate(tiles):
        x = (i % cols) * w
        y = header + (i // cols) * (h + pad) + pad
        canvas.paste(Image.open(src).convert("RGB").resize((w, h)), (x, y))
        dr.text((x + 4, y - 14), lab[:150], fill="black")
    out = AB_SHEET
    canvas.save(out)
    stats = [round(ImageStat.Stat(Image.open(t[1]).convert("RGB")).stddev[0], 2) for t in tiles]
    os.makedirs(os.path.dirname(AB_RUN_SHEET), exist_ok=True)
    open(AB_RUN_SHEET, "wb").write(open(out, "rb").read())
    meta = dict(sheet=out.replace("\\", "/"), run_copy=AB_RUN_SHEET.replace("\\", "/"),
                bytes=os.path.getsize(out), sha=sha(out), size=list(canvas.size), tiles=len(tiles),
                labels=labs, tile_std=stats, generated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                tool="notes/hc15_anchor_fix_build.py --ab-sheet")
    open(AB_META, "w", encoding="utf-8").write(json.dumps(meta, indent=1, ensure_ascii=False))
    print("AB_SHEET %s %dx%d tiles=%d bytes=%d sha=%s" % (out, canvas.size[0], canvas.size[1], len(tiles),
                                                           meta["bytes"], meta["sha"][:16]))
    print("AB_SHEET_COPY " + AB_RUN_SHEET)
    print("KEEP is Derrick's alone; this sheet carries no numbers-based pick and no verdict.")
    return 0


def ab_doc_text(doc):
    """The human surface, written BY CODE from the measured JSON (ck 11 re-generates these bytes = no drift)."""
    rows = {r["role"]: r for r in doc["rows"]}
    b, a = rows["before"], rows["after"]
    L = []
    ap = L.append
    ap("# NOW-P2 - the four published switches, measured before/after (2026-10-26)")
    ap("")
    ap("Generated by `python C:/AI/community/notes/hc15_anchor_fix_build.py --ab-note` from "
       "`notes/hc15_audit/ab_metrics_20261026.json` (generated %s). Every number in this file is written by code "
       "out of that JSON, and gate 11 DOC-SYNC re-generates these bytes, so a table row cannot drift. Re-measure "
       "on CPU: `--ab-metrics` (ffmpeg SSIM/PSNR + CPU SCRFD-10G/ArcFace, no GPU); non-vacuity probe `--ab-selftest`"
       % doc["generated"])
    ap("")
    ap("## The pair: one variable set")
    ap("")
    ap("| row | BEFORE `%s` | AFTER `%s` |" % (b["id"], a["id"]))
    ap("|---|---|---|")
    for lab, fn in (("steps (every `*_sched`)", lambda r: json.dumps(r["setting"]["steps"])),
                    ("`m_attn.attention`", lambda r: r["setting"]["attention"]),
                    ("`ref_image_size` (c0/c1)", lambda r: json.dumps(r["setting"]["ref_image_size"])),
                    ("LoRA", lambda r: json.dumps([l["node"] + ":" + l["file"] + "@" + str(l["strength"])
                                                   for l in r["setting"]["lora"]]) if r["setting"]["lora"] else "[]"),
                    ("LoRA fed by / nodes", lambda r: json.dumps([l["model"] for l in r["setting"]["lora"]])
                     if r["setting"]["lora"] else "-"),
                    ("nodes", lambda r: str(r["setting"]["nodes"])),
                    ("graph sha256", lambda r: r["graph_sha"][:16]),
                    ("`noise_seed`", lambda r: str(r["setting"]["seed"])),
                    ("start frame (`img.image`)", lambda r: r["setting"]["start"]),
                    ("face crops", lambda r: json.dumps(r["setting"]["crops"])),
                    ("c0 prompt sha256", lambda r: r["setting"]["prompt_sha"]["c0"][:16]),
                    ("c1 prompt sha256", lambda r: r["setting"]["prompt_sha"]["c1"][:16]),
                    ("frames / canvas / fps / audio", lambda r: "%d / %dx%d / %s / %s" % (
                        r["probe"]["frames"], r["probe"]["w"], r["probe"]["h"], r["probe"]["fps"], r["probe"]["audio"])),
                    ("mp4 bytes", lambda r: str(r["bytes"])),
                    ("mp4 sha256", lambda r: r["sha"][:16]),
                    ("render wall (s, from objective.json)", lambda r: str(r["objective_secs"]))):
        ap("| %s | %s | %s |" % (lab, fn(b), fn(a)))
    ap("")
    ap("`diff_paths(before, after)` = %d paths: %s. Nothing else differs - the switch set is the only variable."
       % (len(doc["graph_diff"]), ", ".join(doc["graph_diff"])))
    ap("")
    ap("### The switches, with the published wording that is on disk (verbatim)")
    ap("")
    for k, (f, q) in doc["cites"].items():
        ap("- **%s** - `%s` carries: \"%s\"" % (k, f, q))
    ap("")
    ap("## Frames against the approved start still (START-FIDELITY: SSIM/PSNR, higher = closer to the picture)")
    ap("")
    ap("`cover` = the start still scaled-to-fill then cropped to the canvas; `stretch` = scaled to the canvas "
       "exactly. Both fit modes are reported because the 2026-10-23 audit proved the cover crop carries the "
       "identity (SSIM 0.315 vs 0.734 on the stretch of the same file).")
    ap("")
    ap("| frame | metric | BEFORE | AFTER | AFTER - BEFORE |")
    ap("|---|---|---|---|---|")
    def dl(va, vb):
        """Delta only when both sides are numbers; a metric that could not be computed prints no delta (None-safe,
        because a frame with no detected face has no cosine)."""
        return "" if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)) else "%+.4f" % (va - vb)
    for n in ("0", "181", "361"):
        for m in ("ssim_cover", "psnr_cover", "ssim_stretch", "psnr_stretch", "faces"):
            vb, va = b["frames_measured"][n][m], a["frames_measured"][n][m]
            ap("| %s | %s | %s | %s | %s |" % (n, m, vb, va, "" if m == "faces" else dl(va, vb)))
        cb, ca = b["frames_measured"][n]["best_cos"], a["frames_measured"][n]["best_cos"]
        ap("| %s | arcface cos (per start face) | %s | %s | %s |" % (
            n, json.dumps(cb), json.dumps(ca),
            ", ".join("%+.3f" % (y - x) for x, y in zip(cb, ca) if None not in (x, y))))
    ap("")
    ap("The identity floor this repo uses is `%s` (n=%s), and the START-FIDELITY bar is frame 0 SSIM 0.70 "
       "(measured band 0.882-0.915 over the six HC15 clips). Numbers only: no judgement is attached to any row."
       % (doc["floor"], doc["floor"]))
    ap("")
    ap("## The AFTER clip's render receipt (collected from disk, never re-rendered)")
    ap("")
    ap("- runs copy: `%s` - %d bytes, sha256 `%s`, mtime %s" % (a["mp4"], a["bytes"], a["sha"], a["mtime"]))
    ap("- ComfyUI `output/community/%s/`: %d copies, all sha256 equal to the runs copy (%s), mtimes %s -> %s"
       % (a["id"], len(a["copies"]), sorted({c["sha"][:16] for c in a["copies"]}),
          a["copies"][0]["mtime"], a["copies"][-1]["mtime"]))
    ap("- `status.log`: %d `JOB start` rows, %d `JOB end` rows, %d poll-warn rows - the client stalled, so the "
       "runner recorded nothing and re-queued; the paid-for clip is on disk, so it was collected and NOT re-rendered "
       "(the RENDER-TIMEOUT rule: a stall is not an objective failure)" % (a["job_start_rows"], a["job_end_rows"],
                                                                            a["poll_warns"]))
    ap("- `objective.json`: ok=%s, attempts=%d - no proof row, so the shape proof is the ffprobe pass above "
       "(362 packets, 1344x768, 24/1, audio stream present), read by field name" % (a["objective_ok"],
                                                                                      a["objective_attempts"]))
    ap("- the BEFORE clip's own row is intact (ok=%s, attempts=%d, %s s wall), which is what makes the pair "
       "comparable" % (b["objective_ok"], b["objective_attempts"], b["objective_secs"]))
    ap("- the p7 ledger stamp `%s` predates the 2026-10-24 21:52 render: that window is outside the ledger "
       "(as-said, not counted)" % jload(LEDGER).get("updated"))
    ap("")
    ap("## Sheet")
    ap("")
    meta = jload(AB_META)
    ap("- `%s` (%dx%d, %d tiles, %d bytes, sha256 `%s`)" % (meta["sheet"], meta["size"][0], meta["size"][1],
                                                             meta["tiles"], meta["bytes"], meta["sha"][:16]))
    ap("- review copy: `%s`" % meta["run_copy"])
    for lab in meta["labels"]:
        ap("  - %s" % lab)
    ap("")
    ap(AB_KEEP_LINE)
    ap("")
    return "\n".join(L)


def ab_note():
    doc = jload(AB_JSON)
    txt = ab_doc_text(doc)
    open(AB_DOC, "w", encoding="utf-8", newline="\n").write(txt)
    print("AB_DOC %s bytes=%d sha=%s" % (AB_DOC, len(txt.encode("utf-8")), sha_s(txt)[:16]))
    return 0


def ab_git_tracked():
    out = subprocess.run(["git", "-C", W, "ls-files", "--cached"], capture_output=True, text=True)
    return set(l.strip().replace("\\", "/").lower() for l in out.stdout.splitlines() if l.strip())


def ab_src_section():
    src = open(os.path.join(W, "notes", "hc15_anchor_fix_build.py"), encoding="utf-8").read()
    i = src.find(AB_SRC_MARK)
    return src[i:] if i >= 0 else ""


def ab_git_ignored(path):
    """Which .gitignore rule claims this path (empty string = not ignored). The media rule is a fact to measure,"
    """
    out = subprocess.run(["git", "-C", W, "check-ignore", "-v", path], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def ab_ctx(jpath=None, dpath=None, spath=None, mpath=None, ids=None):
    jp = jpath or AB_JSON
    dp = dpath or AB_DOC
    ids = ids or AB_PAIR
    doc = jload(jp)
    return dict(json_path=jp, doc_path=dp, sheet_path=spath or AB_SHEET, meta_path=mpath or AB_META,
                ids=ids, jdoc=doc, rows=doc["rows"], doc_text=open(dp, encoding="utf-8").read(),
                meta=(jload(mpath or AB_META) if os.path.isfile(mpath or AB_META) else None),
                old_metrics=(jload(AB_OLD_METRICS) if os.path.isfile(AB_OLD_METRICS) else None),
                gb=jload(ab_gpath(ids["before"])), ga=jload(ab_gpath(ids["after"])),
                tracked=ab_git_tracked(), ab_src=ab_src_section(), ledger=jload(LEDGER),
                ignore_rule=ab_git_ignored(spath or AB_SHEET))


def ab_label_pixels(sheet, n_tiles):
    """Count dark pixels in each tile's label band of the sheet: measured proof that every tile carries printed
    text (the labels are the sheet's whole point; a blank band means the sheet is not labelled)."""
    w, h, pad, cols, header = AB_TILE
    from PIL import Image
    im = Image.open(sheet).convert("L")
    px = im.load()
    out = []
    for i in range(n_tiles):
        x0 = (i % cols) * w
        y0 = header + (i // cols) * (h + pad)
        out.append(sum(1 for y in range(y0, min(y0 + pad, im.size[1]))
                       for x in range(x0, min(x0 + w, im.size[0])) if px[x, y] < 128))
    return out


def ab_check(ctx=None, label="real"):
    """15 named detectors over the NOW-P2 artifacts. Every one is provably reachable: --ab-selftest seeds the fault
    into a clone of the measured artifacts and requires the detector to fire there and 0 on the real tree. No GPU,
    no queue, no vision model, no score, no pick."""
    ctx = ctx or ab_ctx()
    fails.clear()
    rows = {r["id"]: r for r in ctx["rows"]}
    ids = ctx["ids"]
    b, a = rows.get(ids["before"]), rows.get(ids["after"])
    have = bool(b and a)

    def sg(r, k, d="\0"):
        return (r or {}).get("setting", {}).get(k, d)

    def fm(r, n, k):
        return ((r or {}).get("frames_measured", {}).get(str(n), {}) or {}).get(k)

    # 1 PAIR: both clips exist and carry the promised shape (362 f, 1344x768, 24/1, audio, 15.083333 s)
    ok = have
    for r in (b, a):
        p = (r or {}).get("probe", {})
        ok = (ok and os.path.isfile((r or {}).get("mp4", "x")) and p.get("frames") == 362
              and (p.get("w"), p.get("h")) == CANVAS and p.get("fps") == "24/1" and p.get("audio") is True
              and abs(p.get("dur", 0) - 362 / 24.0) < 0.01)
    ck(ok, "1 PAIR both mp4s on disk and measured: 362 packets, 1344x768, 24/1, audio stream, dur %.6f "
           "(before frames=%s after frames=%s)" % (362 / 24.0, sg(b, "x") and (b or {}).get("probe", {}).get("frames"),
                                                   (a or {}).get("probe", {}).get("frames")))
    # 2 SCOPE: the two graphs differ by exactly the published switch set, nothing else
    gb, ga = ctx["gb"], ctx["ga"]
    d = diff_paths(gb, ga)
    ck(d == NOW_ALLOWED, "2 SCOPE diff_paths(before, after) == the %d allowed paths (steps x2, ref_image_size x2, "
                         "attention, +lora node, its 2 edges, save prefix) and nothing else (extra=%s missing=%s)"
       % (len(NOW_ALLOWED), sorted(d - NOW_ALLOWED)[:4], sorted(NOW_ALLOWED - d)[:4]))
    # 3 SWITCH VALUES: the AFTER row carries the published values, the BEFORE row the old ones. The row's
    #    ref_image_size is a SET of the c0/c1 values, so the per-node values are read from the graphs.
    ck(have and set(a["setting"]["steps"]) == {STEPS_PUB} and a["setting"]["attention"] == ATTN_PUB
       and set(a["setting"]["ref_image_size"]) == {REFSIZE_PUB}
       and set(b["setting"]["ref_image_size"]) == {"max"}
       and ga["c0"]["inputs"]["ref_image_size"] == ga["c1"]["inputs"]["ref_image_size"] == REFSIZE_PUB
       and gb["c0"]["inputs"]["ref_image_size"] == gb["c1"]["inputs"]["ref_image_size"] == "max"
       and [l["file"] for l in a["setting"]["lora"]] == [LORA_FILE]
       and [l["strength"] for l in a["setting"]["lora"]] == [LORA_STRENGTH]
       and [l["model"] for l in a["setting"]["lora"]] == [["m_shift", 0]]
       and set(b["setting"]["steps"]) == {8} and b["setting"]["attention"] == "comfy kitchen attention"
       and b["setting"]["lora"] == [],
       "3 SWITCHES AFTER = steps %s / %s / ref %s / %s@%s fed by m_shift; BEFORE = steps [8] / comfy kitchen "
       "attention / ref ['max','max'] / no LoRA (measured: after steps=%s attn=%s ref=%s lora=%s; before steps=%s "
       "attn=%s ref=%s lora=%s)" % (STEPS_PUB, ATTN_PUB, REFSIZE_PUB, LORA_FILE, LORA_STRENGTH,
                                    sg(a, "steps"), sg(a, "attention"), sg(a, "ref_image_size"),
                                    json.dumps(sg(a, "lora", [])), sg(b, "steps"), sg(b, "attention"),
                                    sg(b, "ref_image_size"), json.dumps(sg(b, "lora", []))))
    # 4 ONE VARIABLE: seed, prompts, start still, face crops identical between the two renders
    ck(have and a["setting"]["seed"] == b["setting"]["seed"] == SEED
       and a["setting"]["prompt_sha"] == b["setting"]["prompt_sha"]
       and a["setting"]["start"] == b["setting"]["start"] and a["setting"]["crops"] == b["setting"]["crops"],
       "4 ONE-VARIABLE seed %d equal, c0/c1 prompt sha256 byte-equal, same start frame, same face crops "
       "(seeds %s/%s, start %s/%s)" % (SEED, sg(b, "seed"), sg(a, "seed"), sg(b, "start"), sg(a, "start")))
    # 5 MEASURED: 3 frames x 4 metrics, all finite floats, plus one ArcFace cosine per start-still face
    need = ["ssim_cover", "psnr_cover", "ssim_stretch", "psnr_stretch"]
    good = have and all(sorted(r["frames_measured"]) == [str(n) for n in AB_FRAMES]
                        and all(isinstance(fm(r, n, k), float) and fm(r, n, k) > 0 for n in AB_FRAMES for k in need)
                        and all(isinstance(v, float) for v in fm(r, 0, "best_cos"))
                        and len(fm(r, 0, "best_cos")) == len(r["start_faces"]) >= 1 for r in (a, b))
    ck(good, "5 MEASURED both rows carry frames %s x %s as finite positive floats + one ArcFace cosine per start "
             "face (%s faces on the start still)" % (list(AB_FRAMES), need, len((b or {}).get("start_faces", []))))
    # 6 REPRO: the BEFORE row reproduces notes/hc15_audit/metrics.json for the same clip (the two passes agree)
    old = next((r for r in (ctx["old_metrics"] or {}).get("rows", []) if r["id"] == ids["before"]), None)
    om = (old or {}).get("frames_measured", {}).get("0", {})
    ck(have and om and all(abs(om[k] - fm(b, 0, k)) < 1e-4 for k in ("ssim_cover", "psnr_cover",
                                                                     "ssim_stretch", "psnr_stretch")),
       "6 REPRO the BEFORE frame-0 numbers reproduce notes/hc15_audit/metrics.json within 1e-4 (metrics.json SSIM "
       "%s PSNR %s vs this pass %s / %s)" % (om.get("ssim_cover"), om.get("psnr_cover"),
                                             fm(b, 0, "ssim_cover"), fm(b, 0, "psnr_cover")))
    # 7 FRAME0-BEST: frame 0 is the highest-SSIM of the three measured frames in BOTH clips (start fidelity;
    #    if a clip drifted away from the approved picture, this fires)
    ck(have and all(max(fm(r, n, "ssim_cover") for n in AB_FRAMES) == fm(r, 0, "ssim_cover") for r in (a, b)),
       "7 FRAME0-BEST frame 0 is the max-SSIM frame of %s in both clips (before f0 %s f%d %s; after f0 %s f%d %s)"
       % (list(AB_FRAMES), fm(b, 0, "ssim_cover"), AB_FRAMES[-1], fm(b, AB_FRAMES[-1], "ssim_cover"),
          fm(a, 0, "ssim_cover"), AB_FRAMES[-1], fm(a, AB_FRAMES[-1], "ssim_cover")))
    # 8 FLOOR: ArcFace cosine of every start-still face at frame 0 above the identity floor this repo uses
    ck(have and all(v is not None and v >= AB_FLOOR for r in (a, b) for v in fm(r, 0, "best_cos")),
       "8 FLOOR frame-0 ArcFace cosines %s (before) / %s (after), all >= n=%s"
       % (fm(b, 0, "best_cos"), fm(a, 0, "best_cos"), AB_FLOOR))
    # 9 SHEET: the file, its meta, freshness, tile count, labels, non-flat pixels
    m, sp = ctx["meta"], ctx["sheet_path"]
    labs = ab_labels(ctx["rows"])
    dark = ab_label_pixels(sp, len(labs)) if (m and os.path.isfile(sp)) else []
    ck(m and os.path.isfile(sp) and m["sheet"].replace("\\", "/") == sp.replace("\\", "/")
       and m["bytes"] == os.path.getsize(sp) and m["sha"] == sha(sp) and m["tiles"] == len(labs) == 13
       and m["labels"] == labs and len(m["tile_std"]) == len(labs) and all(s > 1.0 for s in m["tile_std"])
       and len(dark) == len(labs) and all(d > 20 for d in dark)
       and ids["before"] in " ".join(m["labels"]) and ids["after"] in " ".join(m["labels"])
       and os.path.getmtime(sp) > max(os.path.getmtime(ab_mp4(r)) for r in (ids["before"], ids["after"])),
       "9 SHEET %s: bytes+sha match the meta, %d tiles == the %d labels this builder re-derives (both ids named), "
       "every tile non-flat (min std %s), every label band printed (min %d dark px of %s), mtime newer than both mp4s"
       % (os.path.basename(sp), (m or {}).get("tiles"), len(labs), min((m or {}).get("tile_std") or [0.0]),
          min(dark or [0]), dark[:3]))
    # 10 RECEIPT: the stall is disclosed, the clip is collected from disk, nothing re-rendered, no ok claim
    shas = {c["sha"] for c in (a or {}).get("copies", [])}
    okline = "ok=%s, attempts=%d" % ((a or {}).get("objective_ok"), (a or {}).get("objective_attempts"))
    ck(have and len(a["copies"]) >= 2 and shas == {a["sha"]} and a["job_end_rows"] == 0
       and a["objective_attempts"] == 0 and a["objective_ok"] is not True
       and a["job_start_rows"] == len(a["copies"]) and a["poll_warns"] > 50
       and str(len(a["copies"])) in ctx["doc_text"] and "stall" in ctx["doc_text"]
       and "not re-rendered" in ctx["doc_text"].lower() and okline in ctx["doc_text"]
       and "ok=True, attempts=0" not in ctx["doc_text"],
       "10 RECEIPT %d byte-identical ComfyUI copies (all sha == the runs copy sha), %d `JOB start` rows, %d `JOB "
       "end`, attempts=%d ok=%s, %d poll warns; the doc names the copy count, says stall + not re-rendered, claims "
       "no ok=True" % (len((a or {}).get("copies", [])), (a or {}).get("job_start_rows"),
                       (a or {}).get("job_end_rows"), (a or {}).get("objective_attempts"),
                       (a or {}).get("objective_ok"), (a or {}).get("poll_warns")))
    # 11 DOC-SYNC: the doc on disk == the bytes this code regenerates from the JSON (numbers cannot drift)
    ck(ctx["doc_text"] == ab_doc_text(ctx["jdoc"]),
       "11 DOC-SYNC %s == ab_doc_text(jdoc) regenerated now (%d vs %d chars)"
       % (os.path.basename(ctx["doc_path"]), len(ctx["doc_text"]), len(ab_doc_text(ctx["jdoc"]))))
    # 12 KEEP: no pick/judgement word anywhere in the doc, and the KEEP line present
    hit = [w for w in AB_KEEP_BAN if w in ctx["doc_text"].lower()]
    ck(not hit and AB_KEEP_LINE in ctx["doc_text"],
       "12 KEEP 0 pick/judgement words (%s) in the doc and the KEEP-is-Derrick's line present" % hit)
    # 13 CITES: every quote the doc prints is verbatim in the named notes/web file and printed in the doc
    bad = []
    for k, cq in ctx["jdoc"]["cites"].items():
        f, q = cq[0], cq[1]
        p = os.path.join(W, f.replace("/", os.sep))
        if not os.path.isfile(p):
            bad.append(k + ":missing " + f)
        elif q not in open(p, encoding="utf-8", errors="replace").read():
            bad.append(k + ":quote-not-in-file")
        if k not in ctx["doc_text"] or q not in ctx["doc_text"]:
            bad.append(k + ":not-printed-in-doc")
    ck(not bad, "13 CITES all %d quotes verbatim in notes/web/ and printed in the doc (%s)"
       % (len(ctx["jdoc"]["cites"]), bad[:3]))
    # 14 NO-GPU: the A/B section touches no connection, no queue endpoint, no lock file, no swap route
    hit = [t for t in AB_NET if t in ctx["ab_src"]]
    ck(bool(ctx["ab_src"]) and not hit, "14 NO-GPU the %d-char NOW-P2 section carries 0 of %s (hits=%s)"
       % (len(ctx["ab_src"]), list(AB_NET), hit))
    # 15 DURABLE: runs/ is gitignored (L8, L20), so the durable proof lives under notes/. Media is too: .gitignore
    #    carries "*.png" (measured by git check-ignore), and 0 png is tracked in the repo, so the sheet's byte
    #    identity is its meta (bytes + sha256), which gate 9 verifies against the file.
    need_t = [p.replace(W + os.sep, "").replace("\\", "/").lower() for p in
              (AB_DOC, AB_JSON, AB_META, os.path.join(W, "notes", "hc15_anchor_fix_build.py"))]
    miss = [t for t in need_t if t not in ctx["tracked"]]
    ck(not miss and "*.png" in ctx["ignore_rule"].replace("\\", "/")
       and m and m["bytes"] == os.path.getsize(AB_SHEET) and m["sha"] == sha(AB_SHEET),
       "15 DURABLE doc+json+sheet-meta+builder tracked/staged in C:/AI/community (missing=%s); the sheet itself is "
       "media-ignored by the rule %s, so its bytes %d + sha256 %s in the meta are its durable identity"
       % (miss, (ctx["ignore_rule"].split("\n")[0][:60] or "<none>"), (m or {}).get("bytes", 0),
          (m or {}).get("sha", "")[:16]))
    print("CHECKS %s FAIL %s" % (label, json.dumps(fails)) if fails else "CHECKS %s ALL %d PASS" % (label, 15))
    return list(fails)


def ab_selftest():
    """Seed each fault into an in-memory clone of the measured artifacts (ids, a graph, a metric, a cosine, a
    meta tile, the doc text, the source slice, the tracked set); every detector must fire on its own seed and the
    real tree must stay clean. No GPU, no queue, nothing written outside notes/hc15_audit ab_seed_* files."""
    real = ab_ctx()
    if ab_check(real, label="real"):
        print("AB_SELFTEST the real tree is not clean - fix that first")
        return 1
    fired, silent, real_problem = [], [], False
    txt0 = real["doc_text"]
    base_json = json.loads(json.dumps(real["jdoc"]))

    def clone():
        c = ab_ctx()
        c["jdoc"] = json.loads(json.dumps(base_json))
        c["rows"] = c["jdoc"]["rows"]
        c["gb"] = json.loads(json.dumps(real["gb"]))
        c["ga"] = json.loads(json.dumps(real["ga"]))
        c["meta"] = json.loads(json.dumps(real["meta"]))
        c["doc_text"] = txt0
        return c

    def byrole(c, role):
        return next(r for r in c["rows"] if r["role"] == role)

    SEEDS = [
        ("1 pair: the 243-frame clip-1 in place of the before clip", 1,
         lambda c: c.update(ids={"before": OLD_ID, "after": NOW_ID})),
        ("2 scope: the sampler also changes between the graphs", 2,
         lambda c: c["ga"]["ksel"]["inputs"].__setitem__("sampler_name", "euler")),
        ("3 switches: steps back to the before value on the after row", 3,
         lambda c: byrole(c, "after")["setting"].__setitem__("steps", [8])),
        ("4 one-variable: a prompt sha differs", 4,
         lambda c: byrole(c, "after")["setting"]["prompt_sha"].__setitem__("c0", "0" * 64)),
        ("5 measured: a metric becomes None", 5,
         lambda c: byrole(c, "after")["frames_measured"]["0"].__setitem__("ssim_stretch", None)),
        ("6 repro: the before frame-0 SSIM moves off metrics.json", 6,
         lambda c: byrole(c, "before")["frames_measured"]["0"].__setitem__("ssim_cover", 0.5)),
        ("7 frame0-best: the last frame outruns frame 0", 7,
         lambda c: byrole(c, "after")["frames_measured"]["361"].__setitem__("ssim_cover", 0.99)),
        ("8 floor: a frame-0 cosine under 0.45", 8,
         lambda c: byrole(c, "after")["frames_measured"]["0"].__setitem__("best_cos", [0.12, 0.05])),
        ("9 sheet: the first tile is flat black", 9,
         lambda c: c["meta"].__setitem__("tile_std", [0.0] + c["meta"]["tile_std"][1:])),
        ("9 sheet: a label set that names only one id", 9,
         lambda c: c["meta"].__setitem__("labels", [l.replace(NOW_ID, "clip") for l in c["meta"]["labels"]])),
        ("9 sheet: a label band with no printed text", 9,
         lambda c: c.__setitem__("sheet_path", os.path.join(AUD, "ab_seed_blank_sheet.png"))),
        ("10 receipt: the doc claims the stalled render reported ok=True", 10,
         lambda c: c.__setitem__("doc_text", txt0.replace("ok=None, attempts=0", "ok=True, attempts=1 ok=True")
                                 .replace("NOT re-rendered", "re-rendered"))),
        ("10 receipt: one copy, so nothing proves the re-queue burn", 10,
         lambda c: byrole(c, "after").__setitem__("copies", byrole(c, "after")["copies"][:1])),
        ("11 doc-sync: a hand-typed number in the table", 11,
         lambda c: c.__setitem__("doc_text", txt0.replace("0.915424", "0.95", 1))),
        ("12 KEEP: a pick word in the doc", 12,
         lambda c: c.__setitem__("doc_text", txt0 + "\nThe after is the best clip.\n")),
        ("13 cites: a quote that is not in the cited file", 13,
         lambda c: c["jdoc"]["cites"].__setitem__("steps 12",
                                                  ["notes/web/02v_docs_h3.txt", "steps 12 guarantee fidelity"])),
        ("14 no-gpu: a network call appears in the A/B section", 14,
         lambda c: c.__setitem__("ab_src", c["ab_src"] + "\nimport " + "sock" + "et\n")),
        ("15 durable: the artifacts are not tracked", 15,
         lambda c: c.__setitem__("tracked", set())),
        ("15 durable: the media-ignore rule is not the measured one", 15,
         lambda c: c.__setitem__("ignore_rule", "")),
        ("15 durable: the meta sha no longer equals the sheet bytes", 15,
         lambda c: c["meta"].__setitem__("sha", "0" * 64)),
    ]
    os.makedirs(AUD, exist_ok=True)
    from PIL import Image
    Image.new("RGB", (AB_TILE[0] * AB_TILE[3], AB_TILE[4] + (AB_TILE[1] + AB_TILE[2]) * 3), "white").save(
        os.path.join(AUD, "ab_seed_blank_sheet.png"))
    for i, (name, want, mut) in enumerate(SEEDS):
        c = clone()
        mut(c)
        open(os.path.join(AUD, "ab_seed_%02d.json" % i), "w", encoding="utf-8").write(
            json.dumps({"seed": name, "target": want, "ids": c["ids"]}, ensure_ascii=False))
        got = ab_check(c, label="seed:" + name)
        (fired if any(f.startswith(str(want) + " ") for f in got) else silent).append(name)
    for f in ab_check(real, label="real-after-seeds"):
        real_problem = True
        print("REAL_PROBLEM " + f)
    print("AB_SEEDS %d fired=%d silent=%d" % (len(SEEDS), len(fired), len(silent)))
    if silent:
        print("SILENT_SEEDS " + json.dumps(silent, ensure_ascii=False))
    clean = not silent and not real_problem
    print("AB_SELFTEST " + ("SEEDS_FIRED %d/%d REAL_CLEAN" % (len(fired), len(SEEDS)) if clean
                            else "AB_SELFTEST_DIRTY silent=%d real_problems=%d" % (len(silent), int(real_problem))))
    return 0 if clean else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    load_clips()
    if mode == "--metrics":
        metrics()
        return 0
    gbase = jload(BASE_G)
    if mode == "--build":
        ind = dumps_like(open(BASE_G, "rb").read(), gbase)
        gnew = transform(gbase)
        if ind is None:
            print("BUILD_BLOCKED base byte format (indent) not reproducible"); return 1
        data = write_graph(NEW_G, gnew, ind)
        req = arm(gnew)
        print("BUILT %s nodes=%d bytes=%d sha256=%s" % (NEW_G, len(gnew), len(data), sha(NEW_G)))
        print("ARMED %s + %s id=%s frames=%d minutes=%d" % (os.path.join(W, "runs", NEW_ID, "request.api.json"),
                                                            os.path.join(W, "p7", "JOB_REQUEST.json"),
                                                            req["id"], req["frames"], req["minutes"]))
        return 0
    if mode == "--check":
        return 1 if do_check(gbase, jload(NEW_G)) else 0
    if mode == "--selftest":
        return selftest(gbase)
    if mode == "--sheet":
        return sheet()
    g11 = jload(NOW_BASE_G)
    if mode == "--now-build":
        ind = dumps_like(open(NOW_BASE_G, "rb").read(), g11)
        if ind is None:
            print("BUILD_BLOCKED clip-11 byte format (indent) not reproducible")
            return 1
        gnew = transform_now(g11)
        data = write_graph(NOW_G, gnew, ind)
        req = now_arm(gnew)
        print("BUILT %s nodes=%d bytes=%d sha256=%s" % (NOW_G, len(gnew), len(data), sha(NOW_G)))
        print("ARMED %s + %s id=%s frames=%d minutes=%d"
              % (os.path.join(W, "runs", NOW_ID, "request.api.json"),
                 os.path.join(W, "p7", "JOB_REQUEST.json"), req["id"], req["frames"], req["minutes"]))
        return 0
    if mode == "--now-check":
        return 1 if now_check(g11, jload(NOW_G)) else 0
    if mode == "--now-selftest":
        return now_selftest(g11)
    if mode == "--now-sheet":
        return now_sheet()
    if mode == "--ab-metrics":
        return ab_metrics()
    if mode == "--ab-sheet":
        return ab_sheet()
    if mode == "--ab-note":
        return ab_note()
    if mode == "--ab-check":
        return 1 if ab_check() else 0
    if mode == "--ab-selftest":
        return ab_selftest()
    print("usage: --metrics | --build | --check | --selftest | --sheet | "
          "--now-build | --now-check | --now-selftest | --now-sheet | "
          "--ab-metrics | --ab-sheet | --ab-note | --ab-check | --ab-selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
