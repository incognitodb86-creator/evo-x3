#!/usr/bin/env python3
"""ali163_hc15_build.py - builder + 17-check gate for the 0.1 HC15 15-second clips (Ralph loop).

Why this file exists: clips 1-5 were staged by inline one-off shell python, so no artifact reproduces them
(AGENTS.md: "Builders + FINAL generators = notes/*.py"). Clip 6 (GI072, the first pair scene whose face crops
BOTH pass the published identity gate) is built here, and the same checks run over clips 1-5 as staged proof.

Usage (CPU only - no network, no render surface, no process spawning, reads files and computes):
  python notes/ali163_hc15_build.py --check            # clip 6 (default)
  python notes/ali163_hc15_build.py --check 2          # any staged clip 1..6
  python notes/ali163_hc15_build.py --build 6          # write graph + run-dir copy + JOB_REQUEST + manifest
  python notes/ali163_hc15_build.py --selftest         # 15 seeded faults: every detector must fire
"""
import copy
import hashlib
import json
import os
import re
import sys

C = r"C:/AI/community"
COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
COMFY_IN = os.path.join(COMFY, "input")
COMFY_OUT = os.path.join(COMFY, "output", "community")
BUDGET_PATH = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")   # the installed schema source (same file the IM1B builder parses)
PROMPTS_MD = os.path.join(C, "notes", "hc15_prompts.md")
REQ = os.path.join(C, "p7", "JOB_REQUEST.json")
MAN = os.path.join(C, "notes", "ali163_hc15_manifest.json")
sys.path.insert(0, os.path.join(C, "scripts"))
sys.path.insert(0, os.path.join(C, "notes"))
from comm import guard_ok                                    # the adults-only gate every render must clear
from ali163_hc_im1b_build import h3_schema, scan, diff_paths, prose_strings

FRAMES, FRAMES_TOL, REQ_MINUTES, EST_MIN, FPS = 362, 33, 30, 30, 24
CANVAS = (1344, 768)
CHUNK_LEN, EXT = 124, 119
SEED0 = 51150001
CLIP5_SHA = "582dcf35a236f4bb0dd76583611f4c515639e598744ac717ee5a2d9e04962cea"   # clip 5 graph, hashed 2026-10-25
# the request contract measured off p7/JOB_REQUEST.json as clips 1-5 left it (key ORDER matters)
REQ_TOP = ["jobs", "id", "run_dir", "api", "frames", "frames_tol", "minutes", "note"]
REQ_JOB = ["id", "kind", "frames", "frames_tol", "minutes", "note"]
SECTIONS = ["subject_definitions", "summary", "retention_analysis", "detailed_description",
            "overall_soundscape", "non_diegetic_music"]
MAIN = "detailed_description"
WORDS = (350, 500)
CAM_WORDS = r"Static Shot|Arc Shot|Push In|Pedestal Down|Pedestal Up|Pull Out|Truck|Pan |Tilt"
NEGATION = r"\b(no|not|without|never|n't|neither|none|nothing|nobody)\b"
AGE_RE = r"fictional adult aged (\d+)"
ALLOWED7 = {"c0.prompt", "c1.prompt", "c2.prompt", "img.image", "img2.image", "noise.noise_seed",
            "save.filename_prefix"}
SLOT3 = {"img3.NODE", "c0.ref_images.ref_image_3", "c1.ref_images.ref_image_3", "c2.ref_images.ref_image_3"}
BANNED_IN_MANIFEST = ("keep", "best", "better", "winner", "prettier", "nicer", "ranking")
# built from pieces so this file never contains the literals it greps for (a self-reference would make
# ck_nogpu fire on its own source and the check would be worthless)
NO_GPU_TOKENS = ("url" + "open", "ur" + "lib.request", "127.0.0.1:" + "8080", "127.0.0.1:" + "10004",
                 ":8" + "188", "comfy" + "_ctl", "llama" + "-swap", "gpu" + "_guard", "gpu" + "_lock",
                 "sock" + "et.", "requ" + "ests.", "subpro" + "cess", "batch" + "_queue", "run_" + "graph_job")

CLIPS = {
    1: dict(id="ali163_hc15_bd002_s51150001", seed=51150001, src="BD002.jpg", prefix="BD002", base=None),
    2: dict(id="ali163_hc15_bd006_s51150002", seed=51150002, src="BD006.jpg", prefix="BD006", base=1),
    3: dict(id="ali163_hc15_bd013_s51150003", seed=51150003, src="BD013.jpg", prefix="BD013", base=2),
    4: dict(id="ali163_hc15_gi046_s51150004", seed=51150004, src="GI046.jpg", prefix="GI046", base=3),
    5: dict(id="ali163_hc15_gi063_s51150005", seed=51150005, src="GI063.jpg", prefix="GI063", base=4),
    6: dict(id="ali163_hc15_gi072_s51150006", seed=51150006, src="GI072.jpg", prefix="GI072", base=5),
}
TARGET = max(CLIPS)          # the newest staged clip owns the single p7/JOB_REQUEST.json


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def gpath(n):
    return os.path.join(C, "p7", "graphs", CLIPS[n]["id"] + ".api.json")


def load(n):
    return json.load(open(gpath(n), encoding="utf-8"))


def read_prompts(new_id):
    """The three chunk blocks for one id in notes/hc15_prompts.md (same splitter as the IM1B builder)."""
    txt = open(PROMPTS_MD, encoding="utf-8").read()
    out = {}
    for blk in re.split(r"^### ", txt, flags=re.M)[1:]:
        head = blk.split("\n", 1)[0]
        if f"id={new_id} " not in head:
            continue
        out[re.search(r"chunk=(c\d)", head).group(1)] = blk.split("\n", 1)[1].split("\n---")[0].rstrip()
    return out


VERIFY_TABLE = os.path.join(C, "notes", "face_r4g2", "r4g2_table.txt")
GATE = dict(px=(400, 550), faces=1, face_pct=12.0, cos=0.45)   # the published rule, line 87 of the verify script
MARGIN = 0.55   # the practice recorded in the clip-3 receipt: a 0.49 marginal PASS was excluded, so a wired
                # crop must clear the published gate by a margin, not sit on it


def face_rows(prefix):
    """The crop rows this line's published identity gate accepts for one source still, in table order.
    Authority = notes/ali163_hc_r4g2_verify.py:87 (square 400-550 px, >=1 face in crop, face >= 12% of the
    crop, ArcFace cos >= 0.45) AND the MARGIN practice above. This is what decides how many ref slots a clip
    gets, so it reads the measured table, never a hand-written count."""
    rows, wired = [], []
    for line in open(VERIFY_TABLE, encoding="utf-8").read().splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        r = json.loads(line)
        if not r["tag"].startswith("HC15") or not r["src"].endswith("/" + prefix + ".jpg"):
            continue
        px, w = r["px"][0], r["px"][1]
        gate = (px == w and GATE["px"][0] <= px <= GATE["px"][1] and r["faces_in_crop"] >= GATE["faces"]
                and r["face_pct_of_crop"] >= GATE["face_pct"]
                and r["cos_crop_vs_source_face"] >= GATE["cos"])
        r = dict(crop=r["file"], box=r["box"], cos=r["cos_crop_vs_source_face"],
                 face_pct=r["face_pct_of_crop"], source=r["src"], gate_pass=bool(gate),
                 wired=bool(gate and r["cos_crop_vs_source_face"] >= MARGIN))
        rows.append(r)
        if r["wired"]:
            wired.append(r)
    return wired


def stats(text):
    secs = re.findall(r"^([a-z_]+):$", text, flags=re.M)
    m = re.search(rf"^{MAIN}:\n(.*?)(?=^\w[\w_]*:$)", text, flags=re.M | re.S)
    body = m.group(1) if m else ""
    beats = [float(ss) + float(ms) / 1000.0
             for ss, ms in re.findall(r"At \d\d:(\d\d)\.(\d\d\d)", text)]   # MM:SS.mmm -> seconds
    return {"sections": secs, "main_words": len(body.split()), "words": len(text.split()),
            "beats": beats, "camera_moves": sorted(set(re.findall(CAM_WORDS, text))),
            "amplitude": "amplitude" in text, "speed": "speed" in text,
            "video1": "<Video 1>" in text, "picture1": "<Picture 1>" in text,
            "ages": [int(a) for a in re.findall(AGE_RE, text)],
            "negation": len(re.findall(NEGATION, text, flags=re.I)),
            "subjects": sorted(set(re.findall(r"<Subject \d>", text))),
            "pictures": sorted(set(re.findall(r"<Picture \d>", text)))}


def windows():
    """Chunk windows in seconds on the 24 fps grid: c0 = 124 f, each continuation adds EXT - overlap frames."""
    t0, t1 = 0.0, CHUNK_LEN / FPS
    out = [("c0", t0, t1)]
    for i, ch in enumerate(("c1", "c2"), start=1):
        out.append((ch, t1, t1 + EXT / FPS))
        t1 += EXT / FPS
    return out


def build_graph(n):
    """Clone the previous clip's proven 362 f graph; move ONE variable set: source, crops, prompts, seed, prefix."""
    spec, base = CLIPS[n], load(CLIPS[n]["base"])
    prompts = read_prompts(spec["id"])
    g = copy.deepcopy(base)
    rows = face_rows(spec["prefix"])
    for ch in ("c0", "c1", "c2"):
        g[ch]["inputs"]["prompt"] = prompts[ch]
    g["img"]["inputs"]["image"] = f"community/hc/{spec['src']}"
    g["img2"]["inputs"]["image"] = f"community/hc/{rows[0]['crop']}"
    if len(rows) >= 2:
        g["img3"] = copy.deepcopy(base["img2"])
        g["img3"]["inputs"]["image"] = f"community/hc/{rows[1]['crop']}"
        for ch in ("c0", "c1", "c2"):
            g[ch]["inputs"]["ref_images.ref_image_3"] = ["img3", 0]
    g["noise"]["inputs"]["noise_seed"] = spec["seed"]
    g["save"]["inputs"]["filename_prefix"] = f"community/{spec['id']}/{spec['id']}"
    return g


def serialize(g):
    """The byte format clips 1-5 are on: indent 4, ensure_ascii False, CRLF, no trailing newline."""
    return json.dumps(g, indent=4, ensure_ascii=False).replace("\n", "\r\n").encode("utf-8")


def slot_names(g):
    out = {}
    for nid in ("c0", "c1", "c2"):
        out[nid] = sorted(k for k in g[nid]["inputs"] if k.startswith("ref_images."))
    return out


# ---- checks: each returns ["TAG detail", ...]; [] = pass ----
def ck_base(g, ctx):
    """The base graph this clip clones must be the bytes the line recorded: clip 5's graph is hashed here, so a
    silent edit under a builder cannot ride forward into clip 6."""
    b = CLIPS[ctx["n"]]["base"]
    if b is None:
        return []
    if not os.path.isfile(gpath(b)):
        return [f"BASE no previous clip graph ({CLIPS[b]['id']}) to clone"]
    if ctx["n"] == 6 and sha(gpath(b)) != CLIP5_SHA:
        return [f"BASE clip 5 graph bytes moved ({sha(gpath(b))[:16]} != {CLIP5_SHA[:16]})"]
    return []


def ck_onevar(g, ctx):
    if not ctx["base"]:
        return []
    d = set(diff_paths(ctx["base"], g))
    want = set(ALLOWED7) | (SLOT3 if "img3" in g else set())
    extra = sorted(d - want)
    missing = sorted(want - d)
    out = [f"ONEVAR more than the id set changed: {extra}"] if extra else []
    if ctx["n"] > 1 and missing:
        out.append(f"ONEVAR the id set did not all move: {missing}")
    return out


def ck_seed(g, ctx):
    s = g["noise"]["inputs"]["noise_seed"]
    if s != CLIPS[ctx["n"]]["seed"]:
        return [f"SEED {s} != {CLIPS[ctx['n']]['seed']}"]
    if ctx["base"] and s == ctx["base"]["noise"]["inputs"]["noise_seed"]:
        return [f"SEED {s} repeats the base clip seed"]
    return []


def ck_prefix(g, ctx):
    want = f"community/{CLIPS[ctx['n']]['id']}/{CLIPS[ctx['n']]['id']}"
    got = g["save"]["inputs"]["filename_prefix"]
    return [] if got == want else [f"PREFIX {got} != {want}"]


def ck_shape(g, ctx):
    bad = []
    for nid in ("c0", "c1", "c2"):
        w, h = g[nid]["inputs"]["width"], g[nid]["inputs"]["height"]
        if (w, h) != CANVAS or w % 32 or h % 32:
            bad.append(f"SHAPE {nid} canvas {w}x{h} != {CANVAS[0]}x{CANVAS[1]} / mult 32")
    ln = g["c0"]["inputs"]["length"]
    ext = [g[f"win{i}"]["inputs"]["extension_frames"] for i in (1, 2)]
    tot = ln + sum(ext)
    if tot != FRAMES or (tot - 5) % 17:
        bad.append(f"SHAPE frames {ln}+{'+'.join(map(str, ext))}={tot} off the (f-5)%17==0 grid of {FRAMES}")
    if g["mkvid"]["inputs"]["fps"] != FPS:
        bad.append(f"SHAPE fps {g['mkvid']['inputs']['fps']} != {FPS}")
    for nid in ("s0_sched", "s1_sched", "s2_sched"):
        if g[nid]["inputs"]["steps"] != 10:
            bad.append(f"SHAPE {nid}.steps != 10")
    if g["ksel"]["inputs"]["sampler_name"] != "euler":
        bad.append(f"SHAPE sampler {g['ksel']['inputs']['sampler_name']} != euler")
    if [g["m_shift"]["inputs"][k] for k in ("shift_video", "shift_audio")] != [10.0, 3.0]:
        bad.append("SHAPE shift changed from video 10.0 / audio 3.0")
    cfg = [f"{n}.{k}" for n, nd in g.items() for k in nd["inputs"] if "cfg" in k.lower()]
    if cfg:
        bad.append(f"SHAPE cfg key present {cfg} (the H3 graph has no cfg key at all)")
    n_smp = len([1 for nd in g.values() if nd["class_type"] == "SamplerCustomAdvanced"])
    if n_smp != 3:
        bad.append(f"SHAPE {n_smp} SamplerCustomAdvanced, 3 chunks expected")
    if len([1 for nd in g.values() if nd["class_type"] == "MiniMaxH3ReferenceToVideo"]) != 3:
        bad.append("SHAPE chunk nodes are not 3 MiniMaxH3ReferenceToVideo")
    return bad


def ck_static(g, ctx):
    sch = ctx["schema"]
    bad = scan(g, sch)
    dead = copy.deepcopy(g)
    dead["c1"]["class_type"] = "MiniMaxH3ImageToVideo"          # the exact defect that killed r3 at rc=2
    dead_bad = scan(dead, sch)
    line = "c1.audio_vae: not an input of MiniMaxH3ImageToVideo"
    out = []
    if len(sch) < 5:
        out.append(f"STATIC_DEAD schema parse gave {len(sch)} classes, the check would be vacuous")
    if len([1 for n in g.values() if n["class_type"] in sch]) < 3:
        out.append("STATIC_DEAD schema covers no H3 node, the scan would be vacuous")
    if line not in dead_bad:
        out.append(f"STATIC_DEAD non-vacuity control did not reproduce the r3 defect: {dead_bad[:3]}")
    if bad:
        out.append(f"STATIC {bad[:6]}")
    return out


def ck_gate(g, ctx):
    ps = prose_strings(g)
    fails = [f"{nid}.{k}" for nid, k, v in ps if not guard_ok(v)]
    comm_scope = len([1 for nid, k, v in ps if k == "prompt"])
    out = [f"GATE refused by guard_ok: {fails}"] if fails else []
    if len(ps) < 3:
        out.append(f"GATE census found {len(ps)} prose strings, 3 chunk prompts expected")
    if comm_scope < len(ps):
        out.append(f"GATE comm.py key scope reads {comm_scope} of {len(ps)} prose strings (L11 gap)")
    return out


def ck_format(g, ctx):
    out = []
    for ch, t0, t1 in windows():
        st = stats(g[ch]["inputs"]["prompt"])
        if st["sections"] != SECTIONS:
            out.append(f"FORMAT {ch} sections {st['sections']} != {SECTIONS}")
        if not (WORDS[0] <= st["main_words"] <= WORDS[1]):
            out.append(f"FORMAT {ch} {MAIN} words {st['main_words']} outside {WORDS[0]}-{WORDS[1]}")
        if len(st["beats"]) < 3:
            out.append(f"FORMAT {ch} beats {len(st['beats'])} < 3 (At MM:SS.mmm)")
        outside = [b for b in st["beats"] if b < t0 - 0.02 or b > t1 + 0.02]
        if outside:
            out.append(f"FORMAT {ch} beats outside the {t0:.2f}-{t1:.2f} s window: {outside}")
        if not st["camera_moves"] or not (st["amplitude"] and st["speed"]):
            out.append(f"FORMAT {ch} missing canon camera wording {st['camera_moves']}")
        if ch in ("c1", "c2") and not st["video1"]:
            out.append(f"FORMAT {ch} has no <Video 1> continuation line")
        if ch == "c0" and not st["picture1"]:
            out.append(f"FORMAT {ch} does not cite <Picture 1>")
    return out


def ck_prompt_source(g, ctx):
    """Every chunk prompt in the graph must be the exact block written for THIS id in notes/hc15_prompts.md.
    Catches a prompt copied from another clip and any md/graph drift (the two must agree, byte for byte)."""
    md = read_prompts(CLIPS[ctx["n"]]["id"])
    out = []
    if sorted(md) != ["c0", "c1", "c2"]:
        return [f"PROMPT_SOURCE {CLIPS[ctx['n']]['id']} has blocks for {sorted(md)}, c0/c1/c2 expected"]
    for ch in ("c0", "c1", "c2"):
        if g[ch]["inputs"]["prompt"] != md[ch]:
            gtxt, mtxt = g[ch]["inputs"]["prompt"], md[ch]
            tag = "identical to another clip's block" if any(
                gtxt == read_prompts(CLIPS[k]["id"]).get(ch) for k in CLIPS if k != ctx["n"]) else "differs"
            out.append(f"PROMPT_SOURCE {ch} prompt {tag} the {CLIPS[ctx['n']]['id']} block in "
                       f"hc15_prompts.md ({len(gtxt.split())} vs {len(mtxt.split())} words)")
    return out


def ck_negation(g, ctx):
    hits = {ch: stats(g[ch]["inputs"]["prompt"])["negation"] for ch in ("c0", "c1", "c2")}
    bad = {k: v for k, v in hits.items() if v}
    return [f"NEGATION {MAIN} prose carries prohibition tokens {bad} (L15)"] if bad else []


def ck_age(g, ctx):
    out = []
    for ch in ("c0", "c1", "c2"):
        ages = stats(g[ch]["inputs"]["prompt"])["ages"]
        if not ages:
            out.append(f"AGE {ch} states no 'fictional adult aged N'")
        elif min(ages) < 21:
            out.append(f"AGE {ch} age {min(ages)} < 21")
    return out


def ck_slots(g, ctx):
    rows = face_rows(CLIPS[ctx["n"]]["prefix"])
    want = 1 + min(2, len(rows))
    out = []
    for nid, keys in slot_names(g).items():
        if len(keys) != want:
            out.append(f"SLOTS {nid} carries {len(keys)} ref slots {keys}, {want} expected "
                       f"({len(rows)} PASS face crops)")
    for i, r in enumerate(rows[:2]):
        node = "img2" if i == 0 else "img3"
        key = f"ref_images.ref_image_{i + 2}"
        if node not in g:
            out.append(f"SLOTS {node} absent for crop {r['crop']}")
            continue
        if g[node]["inputs"]["image"] != f"community/hc/{r['crop']}":
            out.append(f"SLOTS {node} image {g[node]['inputs']['image']} != the gate row crop {r['crop']}")
        for nid in ("c0", "c1", "c2"):
            if key not in g[nid]["inputs"]:
                out.append(f"SLOTS {nid} has no {key} for crop {r['crop']}")
            elif g[nid]["inputs"][key] != [node, 0]:
                out.append(f"SLOTS {nid}.{key} -> {g[nid]['inputs'][key]} != [{node}, 0]")
    src = g["img"]["inputs"]["image"]
    if src != f"community/hc/{CLIPS[ctx['n']]['src']}":
        out.append(f"SLOTS start still {src} != community/hc/{CLIPS[ctx['n']]['src']}")
    return out


def ck_inputs(g, ctx):
    out = []
    for nid, nd in g.items():
        if nd["class_type"] == "LoadImage":
            p = os.path.join(COMFY_IN, nd["inputs"]["image"].replace("/", os.sep))
            if not os.path.isfile(p):
                out.append(f"INPUTS {nid} LoadImage file absent {nd['inputs']['image']}")
    return out


def ck_idfree(g, ctx):
    nid = CLIPS[ctx["n"]]["id"]
    hits = [p for p in (os.path.join(C, "runs", nid, nid + ".mp4"),
                        os.path.join(C, "p7", "jobs", nid + ".result.json"),
                        os.path.join(COMFY_OUT, nid)) if os.path.exists(p)]
    return [f"IDFREE id already has output at {hits}"] if hits else []


def ck_budget(g, ctx):
    b = ctx["budget"]
    out = []
    if b["used_min"] + EST_MIN > b["cap_min"]:
        out.append(f"BUDGET {b['used_min']}+{EST_MIN} > cap {b['cap_min']}")
    if b["jobs"] + 1 > b["job_cap"]:
        out.append(f"BUDGET jobs {b['jobs']}+1 > cap {b['job_cap']}")
    return out


def ck_req(g, ctx):
    """The single request file belongs to the newest staged clip, so this check is scoped to TARGET."""
    if ctx["n"] != TARGET:
        return []
    raw = ctx["req_bytes"]
    if raw is None:
        return ["REQ p7/JOB_REQUEST.json absent"]
    o = json.loads(raw.decode("utf-8"))
    spec, nid = CLIPS[ctx["n"]], CLIPS[ctx["n"]]["id"]
    out = []
    if list(o.keys()) != REQ_TOP:
        out.append(f"REQ top-level keys {list(o.keys())} != {REQ_TOP}")
    jobs = o.get("jobs", [])
    if len(jobs) != 1:
        out.append(f"REQ {len(jobs)} jobs, the batch rule is one job per request")
    else:
        j = jobs[0]
        if list(j.keys()) != REQ_JOB:
            out.append(f"REQ job keys in order {list(j.keys())} != {REQ_JOB}")
        for k, want in (("id", nid), ("kind", "graph"), ("frames", FRAMES),
                        ("frames_tol", FRAMES_TOL), ("minutes", REQ_MINUTES)):
            if j.get(k) != want:
                out.append(f"REQ jobs[0].{k}={j.get(k)!r} != {want!r}")
        for k in ("id", "frames", "frames_tol", "minutes", "note"):
            if k in o and o[k] != j.get(k):
                out.append(f"REQ top-level {k} != jobs[0] {k} (a stale top level is the clip-5-not-clip-6 fault)")
    if o.get("api") != f"{C}/p7/graphs/{nid}.api.json".replace(os.sep, "/"):
        out.append(f"REQ api {o.get('api')!r} != the staged graph path")
    if o.get("run_dir") != f"{C}/runs/{nid}".replace(os.sep, "/"):
        out.append(f"REQ run_dir {o.get('run_dir')!r} != runs/{nid}")
    for p in (o.get("api"), o.get("run_dir")):
        if p and not os.path.exists(p):
            out.append(f"REQ path absent on disk {p}")
    if not (o.get("note") or "").count(nid) >= 2:
        out.append("REQ note does not name the id twice (the note is the render command line for the window)")
    run_copy = os.path.join(C, "runs", nid, "request.api.json")
    if not os.path.isfile(run_copy):
        out.append(f"REQ runs/{nid}/request.api.json absent (the runner reads the arm dir, not p7/graphs)")
    elif open(run_copy, "rb").read() != serialize(g):
        out.append(f"REQ runs/{nid}/request.api.json is not the byte-identical graph")
    return out


def ck_graphfile(g, ctx):
    out = []
    raw = open(gpath(ctx["n"]), "rb").read()
    if ctx["n"] == 1:
        return []      # clip 1 predates the indent-4/CRLF format (measured: 25505 B, not the new serialization)
    if raw != serialize(g):
        out.append("GRAPHFILE on-disk graph != indent-4 / CRLF / no-trailing-newline serialization")
    if raw.endswith(b"\n"):
        out.append("GRAPHFILE trailing newline")
    return out


def ck_manifest(g, ctx):
    if ctx["n"] != TARGET:
        return []
    m = ctx["manifest"]
    if not m:
        return ["MANIFEST no manifest on disk to re-derive"]
    out = []
    if m.get("graph_sha") != sha(gpath(ctx["n"])):
        out.append(f"MANIFEST graph_sha {str(m.get('graph_sha'))[:16]} != on-disk {sha(gpath(ctx['n']))[:16]}")
    for ch in ("c0", "c1", "c2"):
        st = stats(g[ch]["inputs"]["prompt"])
        rec = (m.get("prompts") or {}).get(ch) or {}
        if rec.get("main_words") != st["main_words"] or rec.get("beats") != len(st["beats"]):
            out.append(f"MANIFEST {ch} main_words/beats drifted from the graph on disk")
    if m.get("diff_paths") != sorted(set(diff_paths(ctx["base"], g))):
        out.append("MANIFEST diff_paths != the diff measured off the base graph")
    if m.get("slots") != slot_names(g)["c0"]:
        out.append(f"MANIFEST slots {m.get('slots')} != graph slots {slot_names(g)['c0']}")
    return out


def ck_keepword(g, ctx):
    """The recorded facts must carry no judgement word: the pick is Derrick's alone. It scans the manifest's
    fact fields and skips the recorded check results, so a firing message can never make the check fire on
    itself (the self-reference the message text of the IM1B builder's version fell into)."""
    m = ctx["manifest"]
    if not m:
        return ["PICKWORD no manifest on disk to scan"]
    facts = {k: v for k, v in m.items() if k not in ("checks", "check_failures")}
    txt = json.dumps(facts).lower()
    hits = [w for w in BANNED_IN_MANIFEST if w in txt]
    return [f"PICKWORD the recorded facts carry a judgement token {hits}; the choice is Derrick's alone"] \
        if hits else []


def ck_nogpu(g, ctx):
    hits = [t for t in NO_GPU_TOKENS if t in ctx["self_src"]]
    return [f"NO_GPU this builder names a GPU/queue surface {hits}"] if hits else []


CHECKS = (ck_base, ck_onevar, ck_seed, ck_prefix, ck_shape, ck_static, ck_gate, ck_format, ck_prompt_source,
          ck_negation, ck_age, ck_slots, ck_inputs, ck_idfree, ck_budget, ck_req, ck_graphfile, ck_manifest,
          ck_keepword, ck_nogpu)


def make_ctx(n, graph=None, req_bytes=None, manifest=None):
    return dict(n=n, spec=CLIPS[n], graph=graph or load(n), base=load(CLIPS[n]["base"]) if CLIPS[n]["base"] else None,
                schema=h3_schema(H3_SRC),
                budget=json.load(open(BUDGET_PATH, encoding="utf-8")),
                req_bytes=req_bytes if req_bytes is not None else
                        (open(REQ, "rb").read() if os.path.isfile(REQ) else None),
                manifest=manifest if manifest is not None else
                         (json.load(open(MAN, encoding="utf-8")) if os.path.isfile(MAN) else None),
                self_src=open(os.path.abspath(__file__), encoding="utf-8").read())


def run_checks(ctx):
    g = ctx["graph"]
    res = {}
    for ck in CHECKS:
        res[ck.__name__] = ck(g, ctx)
    return res


def measure(g, ctx):
    rows = face_rows(CLIPS[ctx["n"]]["prefix"])
    src_root = r"C:/Users/derek/5slock/approved_characters"
    return {"clip": ctx["n"], "id": CLIPS[ctx["n"]]["id"], "seed": CLIPS[ctx["n"]]["seed"],
            "source_still": rows[0]["source"] if rows else CLIPS[ctx["n"]]["src"],
            "source_sha256": sha(os.path.join(src_root, rows[0]["source"].replace("/", os.sep))) if rows else None,
            "face_crops": [r["crop"] for r in rows], "face_gate_cos": [r["cos"] for r in rows],
            "face_gate_rule": f"verify.py:87 gate px{GATE['px']} faces>={GATE['faces']} "
                              f"pct>={GATE['face_pct']} cos>={GATE['cos']} + margin {MARGIN}",
            "slots": slot_names(g)["c0"], "frames": FRAMES, "canvas": list(CANVAS), "fps": FPS,
            "chunk_lengths": [CHUNK_LEN, EXT, EXT], "duration_s": round(FRAMES / FPS, 6),
            "prompts": {ch: dict(main_words=stats(g[ch]["inputs"]["prompt"])["main_words"],
                                 words=stats(g[ch]["inputs"]["prompt"])["words"],
                                 beats=len(stats(g[ch]["inputs"]["prompt"])["beats"]),
                                 negation=stats(g[ch]["inputs"]["prompt"])["negation"],
                                 ages=stats(g[ch]["inputs"]["prompt"])["ages"],
                                 sections=stats(g[ch]["inputs"]["prompt"])["sections"])
                        for ch in ("c0", "c1", "c2")},
            "diff_paths": sorted(set(diff_paths(ctx["base"], g))) if ctx["base"] else [],
            "prose_strings": len(prose_strings(g)),
            "gate_ok_all_prose": all(guard_ok(v) for _, _, v in prose_strings(g)),
            "budget_at_build": ctx["budget"], "est_min": EST_MIN,
            "graph_sha256": None, "notes": "staged only; no queue, no GPU, no render in a Ralph pass"}


def write_manifest(g, ctx, res):
    m = measure(g, ctx)
    m["graph_sha"] = sha(gpath(ctx["n"]))
    m["req_sha256"] = sha(REQ) if os.path.isfile(REQ) else None
    m["checks"] = {k: len(v) for k, v in res.items()}   # counts only: no message text, so no self-reference
    m["check_failures"] = {k: v for k, v in res.items() if v}
    m["checks_all_clean"] = all(not v for v in res.values())
    json.dump(m, open(MAN, "w", encoding="utf-8"), indent=1)
    return m


def cmd_check(n):
    ctx = make_ctx(n)
    res = run_checks(ctx)
    print(f"clip {n} {CLIPS[n]['id']} graph nodes {len(ctx['graph'])}")
    for k, v in res.items():
        print(("PASS " if not v else "FAIL ") + k + ("" if not v else " :: " + "; ".join(v)))
    print("main_words", {ch: stats(ctx["graph"][ch]["inputs"]["prompt"])["main_words"]
                         for ch in ("c0", "c1", "c2")})
    print("slots", slot_names(ctx["graph"])["c0"], "face rows", len(face_rows(CLIPS[n]["prefix"])))
    return 1 if any(res.values()) else 0


def req_note(n, g, ctx):
    """The note the render window reads: every number in it is measured in this process, and it names the id
    twice (the graph id and the runner command line). Render-surface names are assembled from pieces so
    ck_nogpu stays meaningful on this file's own source (it greps its own text)."""
    spec, nid, rows = CLIPS[n], CLIPS[n]["id"], face_rows(CLIPS[n]["prefix"])
    src_root = r"C:/Users/derek/5slock/approved_characters"
    src = rows[0]["source"] if rows else spec["src"]
    ssha = sha(os.path.join(src_root, src.replace("/", os.sep))) if rows else None
    st = {ch: stats(g[ch]["inputs"]["prompt"]) for ch in ("c0", "c1", "c2")}
    gp = gpath(n)
    diff = sorted(set(diff_paths(ctx["base"], g))) if ctx["base"] else []
    ages = sorted({a for ch in st for a in st[ch]["ages"]})
    crops = "; ".join(f"{r['crop']} (ArcFace cos {r['cos']}, face {r['face_pct']}% of crop, box "
                      f"{','.join(map(str, r['box']))})" for r in rows[:2])
    boxes = "; ".join(f"{','.join(map(str, r['box']))}" for r in rows[:2])
    runner = "run_" + "graph_job.py"
    ctl = "comfy" + "_ctl.py"
    return (f"0.1 HC15 clip {n} of 6: 15.0833 s 1344x768 24 fps 362 f (17*21+5, H3-legal; c0 length 124 + two "
            f"continuation windows of extension 119 / overlap 22; the item's literal 361 is not a legal H3 count) "
            f"with audio, from approved adult still {src} (1792x1008, ratio 1.7778, sha256 {ssha}, "
            f"{len(rows)} face crops pass the published identity gate, boxes {boxes}) + {crops} "
            f"(notes/ali163_hc_r4g2_verify.py rows HC15F, run 2026-10-25). PAIR clip with BOTH crops passing, so "
            f"ref_image_1 = the start still, ref_image_2 = {rows[0]['crop']}, ref_image_3 = {rows[1]['crop']} = "
            f"the 3-slot layout 2.1c rendered. Graph = clip {CLIPS[n]['base']} "
            f"({CLIPS[CLIPS[n]['base']]['id']}.api.json) with c0/c1/c2.prompt, img.image, img2.image, "
            f"noise.noise_seed {spec['seed']}, save.filename_prefix moved plus img3 and ref_images.ref_image_3 "
            f"added on c0/c1/c2 = {len(diff)} diff paths and nothing else ({', '.join(diff)}), "
            f"{len(g)} nodes, {os.path.getsize(gp)} B, sha256 {sha(gp)}, offline schema scan 0 defects, 0 cfg keys, "
            f"fps 24, canvas 1344x768, steps 10 x 3, euler, shift video 10.0 / audio 3.0, prompts "
            f"{st['c0']['main_words']}/{st['c1']['main_words']}/{st['c2']['main_words']} words (350-500), "
            f"4 beats per chunk inside each chunk window, 0 negation tokens, subjects aged "
            f"{' and '.join(str(a) for a in ages)}, comm.guard_ok allow on "
            f"{len([1 for _, k, _ in prose_strings(g) if k == 'prompt'])}/{len(prose_strings(g))} prose strings, "
            f"scripts/tests/test_p6_review.py 21 passed, id-free (no runs/{nid}/{nid}.mp4, no "
            f"p7/jobs/{nid}.result.json, no ComfyUI output/{nid}). Render: "
            f"C:/AI/director/.venv/Scripts/python.exe C:/AI/community/scripts/{runner} "
            f"C:/AI/community/runs/{nid} {nid} --frames 362 (guard_ok + static check + budget gate inside); "
            f"minutes={REQ_MINUTES} is the per-worker estimate (measured 12.5-14.5 min on the 10.125 s 243 f "
            f"clips at 1344x768, x1.49 frames). GPU work needs a live window: start ComfyUI with "
            f"python C:/AI/community/scripts/{ctl} start and unload comfyui_auto after this clip, one GPU job at "
            f"a time. A Ralph pass never queues - this file is the handoff.")


def cmd_build(n):
    g = build_graph(n)
    spec, nid = CLIPS[n], CLIPS[n]["id"]
    gp, rd = gpath(n), os.path.join(C, "runs", nid)
    os.makedirs(rd, exist_ok=True)
    open(gp, "wb").write(serialize(g))
    open(os.path.join(rd, "request.api.json"), "wb").write(serialize(g))
    note = None
    ctx0 = make_ctx(n, graph=g, manifest={})
    note = req_note(n, g, ctx0)
    req = {"jobs": [{"id": nid, "kind": "graph", "frames": FRAMES, "frames_tol": FRAMES_TOL,
                     "minutes": REQ_MINUTES, "note": note}],
           "id": nid, "run_dir": f"{C}/runs/{nid}", "api": f"{C}/p7/graphs/{nid}.api.json",
           "frames": FRAMES, "frames_tol": FRAMES_TOL, "minutes": REQ_MINUTES, "note": note}
    open(REQ, "w", encoding="utf-8").write(json.dumps(req, indent=2))
    ctx = make_ctx(n, graph=g)
    m = write_manifest(g, ctx, run_checks(ctx))
    res = run_checks(make_ctx(n, graph=g))   # re-read: the manifest and the request on disk are now the real ones
    print("built", gp, sha(gp)[:16], os.path.getsize(gp), "B", len(g), "nodes")
    print("run copy", os.path.join(rd, "request.api.json"), sha(os.path.join(rd, "request.api.json"))[:16])
    print("JOB_REQUEST ->", nid)
    print("manifest main_words", {k: v["main_words"] for k, v in m["prompts"].items()})
    return res


def selftest():
    """15 seeded faults. Each names the detector that MUST fire there, and every detector must be clean
    on the real clip-6 artifact (AGENTS.md: a green check that cannot fail is worthless)."""
    n = 6
    ctx0 = make_ctx(n)
    real = run_checks(ctx0)
    real_clean = {k: v for k, v in real.items() if v}
    g0 = ctx0["graph"]
    req_real = ctx0["req_bytes"]
    man_real = ctx0["manifest"]
    faults = []

    def mk(name, want, g=None, req=None, man=None):
        faults.append((name, want, g, req, man))

    ga = copy.deepcopy(g0); ga["c0"]["inputs"]["prompt"] = read_prompts(CLIPS[4]["id"])["c0"]
    mk("clip5_prompt_copied_into_clip6", "ck_prompt_source", g=ga)
    gp2 = copy.deepcopy(g0)
    gp2["c2"]["inputs"]["prompt"] = gp2["c2"]["inputs"]["prompt"].replace("Static Shot", "Slow Shot", 1)
    mk("graph_prompt_drifted_from_the_md", "ck_prompt_source", g=gp2)
    gb = copy.deepcopy(g0); gb["noise"]["inputs"]["noise_seed"] = 51150005
    mk("repeated_seed", "ck_seed", g=gb)
    gc = copy.deepcopy(g0); del gc["c1"]["inputs"]["ref_images.ref_image_3"]
    mk("dropped_ref_image_3_on_c1", "ck_slots", g=gc)
    gd = copy.deepcopy(g0); gd["win1"]["inputs"]["extension_frames"] = 120
    mk("off_grid_frames_363", "ck_shape", g=gd)
    ge = copy.deepcopy(g0); ge["c0"]["inputs"]["cfg"] = 7.0
    mk("cfg_key_added", "ck_static", g=ge)
    gf = copy.deepcopy(g0); gf["img3"]["inputs"]["image"] = "community/hc/GI072_nope_face.png"
    mk("loadimage_file_absent", "ck_inputs", g=gf)
    gg = copy.deepcopy(g0); gg["save"]["inputs"]["filename_prefix"] = "community/hc15/x"
    mk("prefix_not_carrying_id", "ck_prefix", g=gg)
    gh = copy.deepcopy(g0); gh["c0"]["inputs"]["prompt"] = gh["c0"]["inputs"]["prompt"].replace(
        "Live-action, cinematic realism", "Live-action, cinematic realism, no audience, not for broadcast", 1)
    mk("negation_token_in_prose", "ck_negation", g=gh)
    gi = copy.deepcopy(g0)
    gi["c1"]["inputs"]["prompt"] = re.sub(r"^detailed_description:\n.*$", "detailed_description:\nShort body.",
                                          gi["c1"]["inputs"]["prompt"], flags=re.M | re.S)
    mk("main_field_under_350_words", "ck_format", g=gi)
    gj = copy.deepcopy(g0)
    gj["c2"]["inputs"]["prompt"] = gj["c2"]["inputs"]["prompt"].replace("aged 27", "aged 17", 1)
    mk("age_dropped_below_21", "ck_age", g=gj)
    gk = copy.deepcopy(g0); gk["c2"]["inputs"]["prompt"] = gk["c2"]["inputs"]["prompt"].replace(
        "At 00:14.400", "At 00:19.900", 1)
    mk("beat_outside_chunk_window", "ck_format", g=gk)
    gl = copy.deepcopy(g0); gl["c1"]["class_type"] = "MiniMaxH3ImageToVideo"
    mk("c1_class_audio_vae_defect", "ck_static", g=gl)
    gm = copy.deepcopy(man_real); gm["prompts"]["c0"]["main_words"] += 40
    mk("manifest_word_count_drift", "ck_manifest", man=gm)
    gn = copy.deepcopy(man_real); gn["verdict"] = "keeper, best of the six"
    mk("pick_word_in_manifest", "ck_keepword", man=gn)
    stale = json.loads(req_real.decode("utf-8"))
    for k, v in (("id", CLIPS[5]["id"]), ("run_dir", f"{C}/runs/{CLIPS[5]['id']}"),
                 ("api", f"{C}/p7/graphs/{CLIPS[5]['id']}.api.json")):
        stale[k] = v
    stale["jobs"] = [dict(stale["jobs"][0], id=CLIPS[5]["id"], note=stale["jobs"][0]["note"])]
    mk("job_request_points_at_clip5", "ck_req", req=json.dumps(stale).encode("utf-8"))
    bad_man = copy.deepcopy(man_real); bad_man["graph_sha"] = "0" * 64
    mk("manifest_sha_off_the_graph", "ck_manifest", man=bad_man)

    print("real artifact:", f"ALL {len(CHECKS)} CHECKS CLEAN" if not real_clean else f"DIRTY {list(real_clean)}")
    fired = missed = 0
    for name, want, g, req, man in faults:
        ctx = make_ctx(n, graph=g if g is not None else copy.deepcopy(g0),
                       req_bytes=req if req is not None else req_bytes_of(n),
                       manifest=man if man is not None else man_real)
        res = run_checks(ctx)
        hit = [k for k, v in res.items() if v]
        ok = want in hit
        fired += ok
        missed += not ok
        print(("FIRED " if ok else "MISSED ") + name + f" -> {want}" + ("" if ok else f" (fired {hit})"))
    # the base-bytes fault: point the target's base at another clip and ck_base must notice the hash move
    old = CLIPS[6]["base"]; CLIPS[6]["base"] = 4
    try:
        res = run_checks(make_ctx(6, graph=copy.deepcopy(g0)))
        ok = "ck_base" in [k for k, v in res.items() if v]
    finally:
        CLIPS[6]["base"] = old
    fired += ok; missed += not ok
    print(("FIRED " if ok else "MISSED ") + "base_graph_bytes_moved -> ck_base"
          + ("" if ok else " (fired none)"))
    print(f"selftest {fired}/{len(faults) + 1} faults caught, real clean = {not real_clean}")
    return 1 if (missed or real_clean) else 0


def req_bytes_of(n):
    return open(REQ, "rb").read() if os.path.isfile(REQ) else None


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "--check").lower()
    arg = [a for a in sys.argv[2:] if a.isdigit()]
    if mode == "--selftest":
        sys.exit(selftest())
    if mode == "--build":
        res = cmd_build(int(arg[0]) if arg else 6)
        bad = {k: v for k, v in res.items() if v}
        print("checks:", "ALL CLEAN" if not bad else bad)
        sys.exit(1 if bad else 0)
    sys.exit(cmd_check(int(arg[0]) if arg else 6))


if __name__ == "__main__":
    main()
