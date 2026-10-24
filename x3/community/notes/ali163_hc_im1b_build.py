#!/usr/bin/env python
"""ali163_hc_im1b_build.py - fix_plan 2.1b (ALI-163): stage the next HC clip-3 render as ONE variable.

The variable is the PROMPT. Baseline = the rendered r3b / BQ1c graph (seed 51130003, 3 ref slots on c0 and
c1), the one clean same-seed A/B on this box (C:/AI/community/notes/hc_lessons_20261023.md L3). The new
prompt text is the official MiniMax Ref2VA rewrite already committed in
C:/AI/community/notes/im1_prompts.md for id ali147_pool_hc_r3i_s51130003, written to
C:/AI/community/notes/prompt_guide_20261024.md (350-500-word description, six sections, At MM:SS.mmm beats,
canon camera wording, <Video 1> continuation line, face crops cited inside <Subject N>).

Nothing here touches the GPU: it builds graph bytes, checks them offline, and stages p7/JOB_REQUEST.json.
Measured on 2026-10-24: ralph.ps1 and chain.ps1 contain no p7/JOB_REQUEST consumer (grep of both files = 0
hits), so a staged request is inert inside a pass; the AGENTS.md render line and the 2026-10-23 bakeoff
ledger ("Staged request (written, not rendered)") define the pattern.

Reproduce:
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_im1b_build.py --build
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_im1b_build.py --check
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/ali163_hc_im1b_build.py --selftest
Offline static check + non-vacuity control are the clone of run_graph_job.static_check published in
C:/AI/community/notes/ali163_hc_r4g2_build.py check 11 (h3_schema/_args/scan copied from there, cited).
"""
import os, sys, re, json, copy, hashlib

C = "C:/AI/community"
COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
H3_SRC = os.path.join(COMFY, "comfy_extras", "nodes_minimax_h3.py")
COMFY_IN = os.path.join(COMFY, "input")
COMFY_OUT = os.path.join(COMFY, "output", "community")
BUDGET_PATH = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
sys.path.insert(0, os.path.join(C, "scripts"))
from comm import guard_ok                                    # the adults-only gate every render must clear

BASE_ID = "ali147_pool_hc_r3b_s51130003"                     # rendered, gate ok, seed 51130003
NEW_ID = "ali147_pool_hc_r3i_s51130003"                      # staged by this builder
SEED = 51130003
FRAMES, FRAMES_TOL, REQ_MINUTES, EST_MIN = 243, 33, 60, 15    # 243 f clip; batch tolerance; request timeout; per-job budget estimate
BASE_SHA = "ce01686e03909d04be500bb8a186230011c71d12668d2a0fb4686f60809df9f7"
KEEPER = os.path.join(C, "p7", "graphs", BASE_ID + ".baseline.api.json")
GOUT = os.path.join(C, "p7", "graphs", NEW_ID + ".api.json")
ROUT = os.path.join(C, "runs", NEW_ID, "request.api.json")
REQ = os.path.join(C, "p7", "JOB_REQUEST.json")
MAN = os.path.join(C, "notes", "ali163_hc_im1b_manifest.json")
PROMPTS_MD = os.path.join(C, "notes", "im1_prompts.md")
MODEL_REQ = os.path.join(C, "p7", "jobs", "request_iter07.json")
ALLOWED_DIFF = {"c0.prompt", "c1.prompt", "save.filename_prefix"}   # the prompt, and the prefix that carries the id
SECTIONS = {"c0": ["subject_definitions", "summary", "retention_analysis", "detailed_description",
                   "overall_soundscape", "non_diegetic_music"],
            "c1": ["subject_definitions", "summary", "retention_analysis", "integrated_multimodal_description",
                   "overall_soundscape", "non_diegetic_music"]}
MAIN_FIELD = {"c0": "detailed_description", "c1": "integrated_multimodal_description"}
WORDS = {"c0": (350, 500), "c1": (350, 550)}     # guide floor 350; c1 is a continuation task (ref guide 229, 242)
CAM_WORDS = r"Static Shot|Arc Shot|Push In|Pedestal Down|Pull Out|Truck|Pan|Tilt"
BANNED_IN_MANIFEST = ("keep", "best", "better", "winner", "prettier", "nicer", "ranking")
# built from pieces so this file never contains the literals it greps for (a self-reference would make
# ck_nogpu fire on its own source and the check would be worthless)
NO_GPU_TOKENS = ("url" + "open", "ur" + "lib.request", "127.0.0.1:" + "8080", "127.0.0.1:" + "10004",
                 ":8" + "188", "comfy" + "_ctl", "llama" + "-swap", "gpu" + "_guard",
                 "sock" + "et.", "requ" + "ests.", "subpro" + "cess")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---- schema reader + static scan, copied from notes/ali163_hc_r4g2_build.py check 11 (see header) ----
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


def h3_schema(src=H3_SRC):
    txt = open(src, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'node_id="(\w+)",', txt):
        cls, start = m.group(1), m.end()
        end = txt.find("outputs=[", start)
        blk = txt[start:end if end > 0 else start + 4000]
        req, opt = set(), set()
        for im in re.finditer(r'io\.\w+\.Input\("(\w+)"', blk):
            pre = blk[:im.start()]
            depth = pre.count("(") - pre.count(")") + pre.count("[") - pre.count("]")
            if depth != 1:
                continue
            (opt if "optional=True" in _args(blk, im.end()) else req).add(im.group(1))
        if req:
            out[cls] = (req, opt)
    return out


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


# ---- inputs ----
def read_prompts(path=PROMPTS_MD, new_id=NEW_ID):
    txt = open(path, encoding="utf-8").read()
    out = {}
    for blk in re.split(r"^### ", txt, flags=re.M)[1:]:
        head = blk.split("\n", 1)[0]
        if f"id={new_id} " not in head:
            continue
        chunk = re.search(r"chunk=(c\d)", head).group(1)
        body = blk.split("\n", 1)[1].split("\n---")[0].rstrip()
        out[chunk] = body
    return out


def build_graph(base, prompts, new_id=NEW_ID):
    g = copy.deepcopy(base)
    g["c0"]["inputs"]["prompt"] = prompts["c0"]
    g["c1"]["inputs"]["prompt"] = prompts["c1"]
    g["save"]["inputs"]["filename_prefix"] = f"community/{new_id}/{new_id}"
    return g


def diff_paths(a, b):
    """paths (node.input, 'inputs' elided) whose values differ between two graphs, incl. added/removed nodes
    and class changes. The rendered r3b graph and this staged graph must differ on the ALLOWED_DIFF set only."""
    out = []
    for nid in sorted(set(a) | set(b)):
        if nid not in a or nid not in b:
            out.append(f"{nid}.NODE")
            continue
        if a[nid]["class_type"] != b[nid]["class_type"]:
            out.append(f"{nid}.class_type")
        for k in sorted(set(a[nid]["inputs"]) | set(b[nid]["inputs"])):
            if a[nid]["inputs"].get(k) != b[nid]["inputs"].get(k):
                out.append(f"{nid}.{k}")
    return out


def prose_strings(g):
    """EVERY long string input in the graph, under any key. comm.py:154-157 hands guard_ok only key 'prompt',
    so this census is the fix for the key-scope gap measured in fix_plan 1.2 (AGENTS.md L11)."""
    out = []
    for nid, n in g.items():
        for k, v in n["inputs"].items():
            if isinstance(v, str) and len(v.split()) >= 6:
                out.append((nid, k, v))
    return out


def prompt_stats(text, chunk):
    secs = re.findall(r"^([a-z_]+):$", text, flags=re.M)
    main = MAIN_FIELD[chunk]
    m = re.search(rf"^{main}:\n(.*?)(?=^\w[\w_]*:$)", text, flags=re.M | re.S)
    body = m.group(1) if m else ""
    return {"sections": secs, "main_field": main, "main_words": len(body.split()),
            "words": len(text.split()), "beats": len(re.findall(r"At \d\d:\d\d\.\d\d\d", text)),
            "camera_moves": sorted(set(re.findall(CAM_WORDS, text))),
            "amplitude": "amplitude" in text, "speed": "speed" in text,
            "video1": "<Video 1>" in text, "picture1_first_frame": "<Picture 1>" in text}


# ---- checks: each returns ["TAG detail", ...] ----
def ck_base(g, ctx):
    ok = sha(ctx["keeper"]) == ctx["base_sha"]
    if os.path.isfile(os.path.join(C, "runs", BASE_ID, "request.api.json")):
        ok = ok and sha(os.path.join(C, "runs", BASE_ID, "request.api.json")) == ctx["base_sha"]
    return [] if ok else [f"BASE baseline keeper bytes are not the rendered graph (sha {sha(ctx['keeper'])[:16]})"]


def ck_onevar(g, ctx):
    d = diff_paths(ctx["base"], g)
    extra = [p for p in d if p not in ALLOWED_DIFF]
    return [] if not extra else [f"ONEVAR more than the prompt changed: {extra}"]


def ck_seed(g, ctx):
    s = g["noise"]["inputs"]["noise_seed"]
    return [] if s == ctx["seed"] == ctx["base"]["noise"]["inputs"]["noise_seed"] else [f"SEED {s} != {ctx['seed']}"]


def ck_shape(g, ctx):
    bad = []
    for nid in ("c0", "c1"):
        w, h = g[nid]["inputs"]["width"], g[nid]["inputs"]["height"]
        if w % 32 or h % 32:
            bad.append(f"SHAPE canvas {w}x{h} not a multiple of 32")
    ln, ext = g["c0"]["inputs"]["length"], g["win1"]["inputs"]["extension_frames"]
    tot = ln + ext
    if tot != ctx["frames"] or (tot - 5) % 17:
        bad.append(f"SHAPE frames {ln}+{ext}={tot} off the (f-5)%17==0 grid of {ctx['frames']}")
    if g["mkvid"]["inputs"]["fps"] != 24:
        bad.append("SHAPE fps != 24")
    for nid, want in (("s0_sched", 10), ("s1_sched", 10)):
        if g[nid]["inputs"]["steps"] != want:
            bad.append(f"SHAPE {nid}.steps != {want}")
    if g["ksel"]["inputs"]["sampler_name"] != ctx["base"]["ksel"]["inputs"]["sampler_name"]:
        bad.append("SHAPE sampler changed")
    if [g["m_shift"]["inputs"][k] for k in ("shift_video", "shift_audio")] != [10.0, 3.0]:
        bad.append("SHAPE shift changed")
    return bad


def ck_static(g, ctx):
    sch = ctx["schema"]
    bad = scan(g, sch)
    n_h3 = len([n for n in g.values() if n["class_type"] in sch])
    dead = copy.deepcopy(g)
    dead["c1"]["class_type"] = "MiniMaxH3ImageToVideo"          # the exact defect that killed r3 at rc=2
    dead_bad = scan(dead, sch)
    line = "c1.audio_vae: not an input of MiniMaxH3ImageToVideo"
    out = []
    if len(sch) < 5:
        out.append(f"STATIC_DEAD schema parse gave {len(sch)} classes, the check would be vacuous")
    if n_h3 < 3:
        out.append(f"STATIC_DEAD only {n_h3} H3 nodes covered by the schema")
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
    if len(ps) < 2:
        out.append(f"GATE census found only {len(ps)} prose strings, expected the two chunk prompts")
    if comm_scope < 2:
        out.append(f"GATE comm.py key scope sees {comm_scope} of {len(ps)} strings, so the graph has text the gate cannot read")
    return out


def ck_format(g, ctx):
    out = []
    for chunk in ("c0", "c1"):
        st = prompt_stats(g[chunk]["inputs"]["prompt"], chunk)
        lo, hi = WORDS[chunk]
        if st["sections"] != SECTIONS[chunk]:
            out.append(f"FORMAT {chunk} sections {st['sections']} != {SECTIONS[chunk]}")
        if not (lo <= st["main_words"] <= hi):
            out.append(f"FORMAT {chunk} {st['main_field']} words {st['main_words']} outside {lo}-{hi}")
        if st["beats"] < 3:
            out.append(f"FORMAT {chunk} beats {st['beats']} < 3 (At MM:SS.mmm)")
        if not st["camera_moves"] or not (st["amplitude"] and st["speed"]):
            out.append(f"FORMAT {chunk} missing canon camera wording {st['camera_moves']}")
        if chunk == "c1" and not st["video1"]:
            out.append("FORMAT c1 has no <Video 1> continuation line")
        if chunk == "c0" and not st["picture1_first_frame"]:
            out.append("FORMAT c0 does not cite <Picture 1>")
    return out


def ck_inputs(g, ctx):
    out = []
    for nid in ("img", "img2", "img3"):
        rel = g[nid]["inputs"]["image"]
        p = os.path.join(COMFY_IN, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            out.append(f"INPUTS {nid} LoadImage file absent {rel}")
    return out


def ck_idfree(g, ctx):
    nid = ctx["new_id"]
    hits = [p for p in (os.path.join(C, "runs", nid, nid + ".mp4"),
                        os.path.join(C, "p7", "jobs", nid + ".result.json"),
                        os.path.join(COMFY_OUT, nid)) if os.path.exists(p)]
    return [f"IDFREE id already has output at {hits}"] if hits else []


def ck_budget(g, ctx):
    b = ctx["budget"]
    out = []
    if b["used_min"] + ctx["est_min"] > b["cap_min"]:
        out.append(f"BUDGET {b['used_min']}+{ctx['est_min']} > cap {b['cap_min']}")
    if b["jobs"] + 1 > b["job_cap"]:
        out.append(f"BUDGET jobs {b['jobs']}+1 > cap {b['job_cap']}")
    return out


def ck_req(g, ctx):
    raw = ctx["req_bytes"]
    if raw is None:
        return ["REQ p7/JOB_REQUEST.json not written"]
    o = json.loads(raw.decode("utf-8"))
    model = json.loads(open(MODEL_REQ, encoding="utf-8").read())
    out = []
    if list(o.keys()) != ["jobs"]:
        out.append(f"REQ top-level keys {list(o.keys())} != ['jobs']")
    jobs = o.get("jobs", [])
    if len(jobs) != 1:
        out.append(f"REQ {len(jobs)} jobs, the batch rule is one job per request")
    else:
        j = jobs[0]
        if sorted(j.keys()) != sorted(model["jobs"][0].keys()):
            out.append(f"REQ keys {sorted(j.keys())} != harness model keys")
        if j.get("id") != ctx["new_id"] or j.get("frames") != ctx["frames"] or j.get("frames_tol") != FRAMES_TOL:
            out.append(f"REQ job {j.get('id')}/{j.get('frames')}/{j.get('frames_tol')} != {ctx['new_id']}/{ctx['frames']}/{FRAMES_TOL}")
    return out


def ck_manifest(g, ctx):
    out = []
    m = ctx["manifest"]
    if not m:
        return ["MANIFEST no manifest on disk to re-derive"]
    if m.get("graph_sha") != sha(GOUT):
        out.append(f"MANIFEST graph_sha {str(m.get('graph_sha'))[:16]} != on-disk {sha(GOUT)[:16]}")
    for chunk in ("c0", "c1"):
        st = prompt_stats(g[chunk]["inputs"]["prompt"], chunk)
        rec = (m.get("prompts") or {}).get(chunk) or {}
        if rec.get("main_words") != st["main_words"] or rec.get("beats") != st["beats"]:
            out.append(f"MANIFEST {chunk} word/beat counts drifted from the graph on disk")
    return out


def ck_keepword(g, ctx):
    txt = json.dumps(ctx["manifest"]).lower()
    hits = [w for w in BANNED_IN_MANIFEST if w in txt]
    return [f"KEEPWORD manifest records a pick word {hits}; the pick is Derrick's alone"] if hits else []


def ck_nogpu(g, ctx):
    hits = [t for t in NO_GPU_TOKENS if t in ctx["self_src"]]
    return [f"NO_GPU this builder names a GPU/queue surface {hits}"] if hits else []


CHECKS = (ck_base, ck_onevar, ck_seed, ck_shape, ck_static, ck_gate, ck_format, ck_inputs,
          ck_idfree, ck_budget, ck_req, ck_manifest, ck_keepword, ck_nogpu)


def make_ctx(write=False):
    prompts = read_prompts()
    if set(prompts) != {"c0", "c1"}:
        raise SystemExit(f"PROMPTS {PROMPTS_MD} gave chunks {sorted(prompts)}, expected c0 and c1")
    base = json.loads(open(KEEPER, encoding="utf-8").read())
    g = build_graph(base, prompts)
    data = (json.dumps(g, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if write:
        os.makedirs(os.path.dirname(GOUT), exist_ok=True)
        os.makedirs(os.path.dirname(ROUT), exist_ok=True)
        for p in (GOUT, ROUT):
            open(p, "wb").write(data)
        req = {"jobs": [{"id": NEW_ID, "kind": "graph", "frames": FRAMES, "frames_tol": FRAMES_TOL,
                         "minutes": REQ_MINUTES,
                         "note": ("ALI-163 2.1b ONE VARIABLE = THE PROMPT: byte-clone of the rendered r3b/BQ1c "
                                  f"graph (seed {SEED}, 3 ref slots on c0 and c1, 1344x768, 243 f, euler, steps 10, "
                                  f"shift 10/3) with only c0/c1 prompt and filename_prefix changed; prompts are the "
                                  "official Ref2VA six-section rewrite in notes/im1_prompts.md (350-500 word main "
                                  "field, At MM:SS.mmm beats, canon camera wording, <Video 1> continuation). "
                                  "comm.guard_ok passed over every string input; offline static check clean. "
                                  "graph sha256 " + hashlib.sha256(data).hexdigest())}]}
        req_bytes = (json.dumps(req, indent=4) + "\n").encode("utf-8")
        open(REQ, "wb").write(req_bytes)
    else:
        req_bytes = open(REQ, "rb").read() if os.path.isfile(REQ) else None
        data = open(GOUT, "rb").read()
        g = json.loads(data.decode("utf-8"))
    man = json.loads(open(MAN, encoding="utf-8").read()) if os.path.isfile(MAN) else {}
    b = json.loads(open(BUDGET_PATH, encoding="utf-8").read())
    return dict(base=base, g=g, keeper=KEEPER, base_sha=BASE_SHA, seed=SEED, frames=FRAMES,
                est_min=EST_MIN, new_id=NEW_ID, schema=h3_schema(), budget=b, req_bytes=req_bytes,
                manifest=man, self_src=open(os.path.abspath(__file__), encoding="utf-8").read())


def build_manifest(g, ctx):
    ps = prose_strings(g)
    data = open(GOUT, "rb").read()
    b = ctx["budget"]
    req = json.loads(ctx["req_bytes"].decode("utf-8"))
    return {
        "item": "2.1b", "mission": "ALI-163", "new_id": NEW_ID, "base_id": BASE_ID,
        "base_sha": ctx["base_sha"], "graph_sha": hashlib.sha256(data).hexdigest(), "graph_bytes": len(data),
        "node_count": len(g), "diff_paths": sorted(diff_paths(ctx["base"], g)),
        "seed": g["noise"]["inputs"]["noise_seed"],
        "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
        "frames": g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"],
        "frames_grid_ok": (g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"] - 5) % 17 == 0,
        "fps": g["mkvid"]["inputs"]["fps"], "steps": [g["s0_sched"]["inputs"]["steps"], g["s1_sched"]["inputs"]["steps"]],
        "sampler": g["ksel"]["inputs"]["sampler_name"],
        "shift": [g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"]],
        "prompts": {c: prompt_stats(g[c]["inputs"]["prompt"], c) for c in ("c0", "c1")},
        "baseline_prompts": {c: prompt_stats(ctx["base"][c]["inputs"]["prompt"], c) for c in ("c0", "c1")},
        "gate": {"prose_strings": len(ps), "checked": len(ps), "comm_key_scope": len([1 for n, k, v in ps if k == "prompt"]),
                 "failed": [f"{n}.{k}" for n, k, v in ps if not guard_ok(v)],
                 "key_scope_source": "C:/AI/community/scripts/comm.py:154-157 reads input key prompt only (fix_plan 1.2)"},
        "static": {"h3_nodes": len([n for n in g.values() if n["class_type"] in ctx["schema"]]),
                   "schema_classes": len(ctx["schema"]), "defects": scan(g, ctx["schema"]),
                   "nonvacuity_line": "c1.audio_vae: not an input of MiniMaxH3ImageToVideo",
                   "nonvacuity_seen": "c1.audio_vae: not an input of MiniMaxH3ImageToVideo" in scan(
                       {**{k: v for k, v in g.items()}, "c1": {**g["c1"], "class_type": "MiniMaxH3ImageToVideo"}}, ctx["schema"]),
                   "source": "schema parsed from comfy_extras/nodes_minimax_h3.py; clone of run_graph_job.static_check "
                             "published in notes/ali163_hc_r4g2_build.py check 11"},
        "inputs": [{"node": n, "image": g[n]["inputs"]["image"],
                    "bytes": os.path.getsize(os.path.join(COMFY_IN, g[n]["inputs"]["image"].replace("/", os.sep))),
                    "sha16": sha(os.path.join(COMFY_IN, g[n]["inputs"]["image"].replace("/", os.sep)))[:16]}
                   for n in ("img", "img2", "img3")],
        "idfree": {"runs_mp4": os.path.exists(os.path.join(C, "runs", NEW_ID, NEW_ID + ".mp4")),
                   "p7_result": os.path.exists(os.path.join(C, "p7", "jobs", NEW_ID + ".result.json")),
                   "comfy_out": os.path.exists(os.path.join(COMFY_OUT, NEW_ID))},
        "budget": {"used_min": b["used_min"], "cap_min": b["cap_min"], "jobs": b["jobs"], "job_cap": b["job_cap"],
                   "est_min": EST_MIN, "headroom_min": round(b["cap_min"] - b["used_min"] - EST_MIN, 1),
                   "headroom_jobs": b["job_cap"] - b["jobs"] - 1, "path": BUDGET_PATH},
        "request": {"bytes": len(ctx["req_bytes"]), "sha16": hashlib.sha256(ctx["req_bytes"]).hexdigest()[:16],
                    "jobs": len(req["jobs"]), "id": req["jobs"][0]["id"], "frames": req["jobs"][0]["frames"],
                    "frames_tol": req["jobs"][0]["frames_tol"], "minutes": req["jobs"][0]["minutes"]},
        "picks_recorded": 0, "picks_note": "the pick is Derrick's alone; nothing here ranks a clip",
        "gpu_contact": "none: no socket, no queue, no GPU command in this builder (NO_GPU check)",
    }


def run(g, ctx):
    probs = []
    for fn in CHECKS:
        probs += fn(g, ctx)
    return probs


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "--check").lower()
    if mode == "--selftest":
        return selftest()
    if mode == "--build":
        if os.path.exists(REQ):
            raise SystemExit(f"REFUSE {REQ} already exists; a request is only submittable while it is absent")
        ctx = make_ctx(write=True)
        man = build_manifest(ctx["g"], ctx)
        open(MAN, "w", encoding="utf-8").write(json.dumps(man, indent=2, sort_keys=True) + "\n")
        ctx["manifest"] = man
        ctx["req_bytes"] = open(REQ, "rb").read()
    else:
        ctx = make_ctx(write=False)
    probs = run(ctx["g"], ctx)
    m = ctx["manifest"]
    if mode == "--build":
        print(f"wrote {GOUT} {m['graph_bytes']} B sha {m['graph_sha'][:16]}")
        print(f"wrote {ROUT}")
        print(f"wrote {REQ} jobs={m['request']['jobs']} id={m['request']['id']} frames={m['request']['frames']}")
        print(f"wrote {MAN}")
    print(f"one-variable diff = {m['diff_paths']}")
    for c in ("c0", "c1"):
        p, q = m["prompts"][c], m["baseline_prompts"][c]
        print(f"{c}: main {p['main_field']} {q['main_words']} -> {p['main_words']} words; "
              f"beats {q['beats']} -> {p['beats']}; camera {p['camera_moves']}; <Video 1> {p['video1']}")
    print(f"gate: {m['gate']['checked']} prose strings checked, comm key scope {m['gate']['comm_key_scope']}, "
          f"failed {m['gate']['failed']}")
    print(f"static: {m['static']['h3_nodes']} H3 nodes / {m['static']['schema_classes']} schema classes, "
          f"defects {m['static']['defects']}, non-vacuity seen {m['static']['nonvacuity_seen']}")
    print(f"budget: used {m['budget']['used_min']}/{m['budget']['cap_min']} min, jobs {m['budget']['jobs']}/"
          f"{m['budget']['job_cap']}, headroom {m['budget']['headroom_min']} min / {m['budget']['headroom_jobs']} jobs")
    print(f"PROBLEMS {len(probs)} VERDICT {'CLEAN' if not probs else 'RED'}")
    for p in probs:
        print("  " + p)
    return 0 if not probs else 1


def selftest():
    ctx = make_ctx(write=False)
    real = run(ctx["g"], ctx)
    seeds = []

    def case(tag, mut, allowed=()):
        c = copy.deepcopy(ctx)
        g = copy.deepcopy(c["g"])
        mut(g, c)
        probs = run(g, c)
        hit = any(p.split()[0] == tag for p in probs)
        extra = [p for p in probs if p.split()[0] not in (tag,) + tuple(allowed)]
        seeds.append((tag, hit, probs, extra))

    def steps(g, c):
        g["s0_sched"]["inputs"]["steps"] = 20
    case("ONEVAR", steps, allowed=("SHAPE",))      # a steps change is BOTH a second variable and a shape break

    def sd(g, c):
        g["noise"]["inputs"]["noise_seed"] = 51130004
    case("SEED", sd, allowed=("ONEVAR",))

    def canvas(g, c):
        g["c0"]["inputs"]["height"] = 468
    case("SHAPE", canvas, allowed=("ONEVAR",))

    def frames(g, c):
        g["c0"]["inputs"]["length"] = 125
    case("SHAPE", frames, allowed=("ONEVAR",))

    def vacuous(g, c):
        c["schema"] = {}
    case("STATIC_DEAD", vacuous)

    def banned_prompt(g, c):
        g["c1"]["inputs"]["prompt"] += " The scene is a schoolgirl in uniform."
    case("GATE", banned_prompt)

    def banned_other_key(g, c):
        g["save"]["inputs"]["filename_prefix"] = ("community/ali147_pool_hc_r3i_s51130003/the schoolgirl "
                                                  "and the minors pose together on the terrace")
    case("GATE", banned_other_key)

    def noformat(g, c):
        g["c0"]["inputs"]["prompt"] = re.sub(r"At \d\d:\d\d\.\d\d\d, ", "", g["c0"]["inputs"]["prompt"])
        g["c0"]["inputs"]["prompt"] = g["c0"]["inputs"]["prompt"].replace("summary:\n", "summary_removed:\n")
    case("FORMAT", noformat, allowed=("MANIFEST",))   # a prompt change must also break the manifest re-derivation

    def missing_input(g, c):
        g["img3"]["inputs"]["image"] = "community/hc/NO_SUCH_CROP.png"
    case("INPUTS", missing_input, allowed=("ONEVAR",))  # swapping a LoadImage file is also a second variable

    def used_id(g, c):
        c["new_id"] = BASE_ID
        o = json.loads(c["req_bytes"].decode("utf-8"))
        o["jobs"][0]["id"] = BASE_ID
        c["req_bytes"] = json.dumps(o).encode("utf-8")
    case("IDFREE", used_id)

    def over_budget(g, c):
        c["budget"] = dict(c["budget"], used_min=610.0)
    case("BUDGET", over_budget)

    def two_jobs(g, c):
        o = json.loads(c["req_bytes"].decode("utf-8"))
        o["jobs"].append(dict(o["jobs"][0]))
        c["req_bytes"] = json.dumps(o).encode("utf-8")
    case("REQ", two_jobs)

    def tamper(g, c):
        c["manifest"] = dict(c["manifest"], graph_sha="0" * 64)
    case("MANIFEST", tamper)

    def verdict_word(g, c):
        c["manifest"] = dict(c["manifest"], picks_note="the best clip of the batch")
    case("KEEPWORD", verdict_word)

    def net(g, c):
        c["self_src"] = c["self_src"] + ("\nimport ur" + "lib.request\nur" + "lib.request.url"
                                         + "open('http://127.0.0.1:" + "10004/prompt')\n")
    case("NO_GPU", net)

    import tempfile
    seed_keeper = os.path.join(tempfile.mkdtemp(prefix="im1b_seed_"), "drift.api.json")

    def base_drift(g, c):
        open(seed_keeper, "wb").write(b"x")
        c["keeper"] = seed_keeper
    case("BASE", base_drift)

    fired = [t for t, hit, p, x in seeds if hit]
    leaky = [(t, p) for t, hit, p, x in seeds if not hit]
    collateral = [(t, x) for t, hit, p, x in seeds if hit and x]
    for t, hit, p, x in seeds:
        print(f"seed {t}: fired={'yes' if hit else 'NO '} problems={len(p)} unexpected={x[:2]} {p[:1]}")
    os.remove(seed_keeper) if os.path.exists(seed_keeper) else None
    print(f"SELFTEST seeds={len(seeds)} fired={len(fired)} silent={len(leaky)} "
          f"collateral={len(collateral)} real_tree_problems={len(real)}")
    for t, p in leaky + collateral:
        print(f"  DEFECT {t}: {p}")
    for p in real:
        print(f"  REAL {p}")
    return 0 if not leaky and not collateral and not real and len(fired) == len(seeds) else 1


if __name__ == "__main__":
    sys.exit(main())
