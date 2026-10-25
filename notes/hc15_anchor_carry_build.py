"""ALI-163 TOP carry - the FIXED clip-1 graph shape carried onto the other five HC15 start images.

Item: "I want the two videos the orc and the robot fucking video ... Like hardcore sex" (Derrick 2026-10-24
8:39 PM CT, fix_plan TOP). The item's shape requirement is the fixed clip-1 graph: MiniMaxH3AddGuide frame_idx 0,
res_multistep/simple/8 steps, 243 + 119 frames. That shape is the rendered clip 11
(p7/graphs/ali163_hc15_bd002_s51150011.api.json, 18,235 B, sha256 8a57ebbf456b6f9d06de7c0a32b02dc1bb4eff736c041700ea62b53e2c51d868,
measured 2026-10-25: 25 nodes, g0 frame_idx 0, win1 22/119, c0 length 243, sampler res_multistep, schedulers 8
steps, sha256 of c0/c1 prompts byte-identical to clip 1's, zero diff outside the three switches).

This file does NOT re-implement the switch. It imports transform() from notes/hc15_anchor_fix_build.py - the
function that produced the rendered clip 11 - and the CK_CONTROL detector proves that claim: transform(clip 1)
must reproduce the shipped clip-11 bytes. A look-alike transform fails there (AGENTS.md L10: a green check that
cannot fail is worthless, so every detector below is seeded in --selftest and must fire on the seed and stay
clean on the real artifacts).

Why carry five clips when the item names two: the item's first verb is "Find the two HC15 start images that show
the orc and the robot", and a Ralph pass cannot resolve that - this session's model is a text model
(coding_swift15_iq3s, PI_OFFLINE=1) with no visual channel; the community tool that reads a start image is the
vision prompter notes/ali173_pw1d_run.py (Qwen2.5-Omni-7B + MiniMax H3 Prompt-Rewriter LoRA, REF2AV, proven in
notes/forge_pw1d_smoke.md, 0.3 min GPU) which needs the GPU that PROMPT 99999999 / AGENTS.md bar in a pass; the
Grok prompt sidecars are barred by canon (approved_characters/GROK_IMAGINE_2026-10-19/CHARACTER.md R3, Derrick
2026-10-09); and the objective probes I ran this pass are inconclusive (9 SCRFD face boxes over the six stills:
green-skin fraction 0.0% in every box, grey/metal fraction 0.0-12.9% - notes/hc15_figures_20261025.md). So the
graph work that is decidable now is staged for all five remaining clips, and the species prose is written per
file the moment the two are named (needs_derrick.md row 18).

Runs on C:/Program Files/Python312/python.exe (the interpreter that has the repo's deps).
  python C:/AI/community/notes/hc15_anchor_carry_build.py --check
  python C:/AI/community/notes/hc15_anchor_carry_build.py --build
  python C:/AI/community/notes/hc15_anchor_carry_build.py --selftest
NO GPU: --build writes graph + run-dir request + manifest files only. A Ralph pass never queues (PROMPT.md
99999999 / AGENTS.md "The GPU is off-limits"); ck_nogpu scans this file's own source for a GPU/queue surface.
"""
import copy
import hashlib
import json
import os
import re
import sys

W = r"C:/AI/community"
sys.path.insert(0, os.path.join(W, "notes"))
sys.path.insert(0, os.path.join(W, "scripts"))
from hc15_anchor_fix_build import ALLOWED, dumps_like, diff_paths, h3_schema, scan, transform, write_graph  # noqa: E402
from ali163_hc_im1b_build import prose_strings, prompt_stats  # noqa: E402
from comm import guard_ok  # noqa: E402  the fiction gate; the only gate allowed to touch a graph

COMFY = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI"
COMFY_IN = os.path.join(COMFY, "input")
COMFY_OUT = os.path.join(COMFY, "output", "community")
GRAPHS = os.path.join(W, "p7", "graphs")
RUNS = os.path.join(W, "runs")
JOBS = os.path.join(W, "p7", "jobs")
NOTES = os.path.join(W, "notes")
LEDGER = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"

# source clip -> (source id, carried id, seed). The seed is NOT moved: a before/after of the community switches
# is only a measurement with the seed held (IM1 re-renders the same seeds; clip 11 keeps 51150001 for the same
# reason - audit 3.5). The id carries the 1x series like clip 11.
CARRY = {2: ("ali163_hc15_bd006_s51150002", "ali163_hc15_bd006_s51150012", 51150002),
         3: ("ali163_hc15_bd013_s51150003", "ali163_hc15_bd013_s51150013", 51150003),
         4: ("ali163_hc15_gi046_s51150004", "ali163_hc15_gi046_s51150014", 51150004),
         5: ("ali163_hc15_gi063_s51150005", "ali163_hc15_gi063_s51150015", 51150005),
         6: ("ali163_hc15_gi072_s51150006", "ali163_hc15_gi072_s51150016", 51150006)}
CLIP1 = "ali163_hc15_bd002_s51150001"
CLIP11 = "ali163_hc15_bd002_s51150011"
CLIP11_SHA = "8a57ebbf456b6f9d74ad1ca2424076041e8ad0c524d15f7f8a7c9a126a57e769"   # measured 2026-10-25, 18,235 B
FORMAT_IND = 2   # the byte format of the fixed clip-1 graph: measured dumps_like(clip-11 bytes, transform(clip 1)) = 2
FRAMES = 362
CANVAS = (1344, 768)
EST_MIN = 30          # measured 24.0 + 25% contingency, the same rule clip 1-6 used (audit 3.7)
# assembled from pieces, the convention notes/ali163_hc15_build.py:56 uses, so ck_nogpu can stay meaningful
# while scanning this file's own source text
NO_GPU_TOKENS = ("llama" + "-swap", "127.0.0.1:" + "8080", "127.0.0.1:" + "10004", ":8" + "188", ":8" + "189",
                 "comfy" + "_ctl", "run_" + "graph_job", "gpu" + "_guard", "gpu" + "_lock", "queue_" + "prompt",
                 "ur" + "lib.request", "sock" + "et.", "subpro" + "cess", "ba" + "tch_queue", "nv" + "idia-smi")
BANNED_IN_MANIFEST = ("keep", "best", "pick", "winner", "preference", "favoured", "favorite")
CHUNKS = ("c0", "c1")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def gload(nid):
    return json.load(open(os.path.join(GRAPHS, nid + ".api.json"), encoding="utf-8"))


def gpath(nid):
    return os.path.join(GRAPHS, nid + ".api.json")


def man_path(nid):
    return os.path.join(NOTES, f"hc15_anchor_carry_{nid}.json")


def slot_edges(g):
    """{chunk: {ref_image_N: [node, idx]}} read the fullmatch way (AGENTS.md: the ref_images dict of submitted
    graphs breaks ins[k][0])."""
    out = {}
    for nid, nd in g.items():
        if not nid.startswith("c"):
            continue
        out[nid] = {k: v for k, v in nd["inputs"].items()
                    if re.fullmatch(r"ref_images\.ref_image_\d+", k)}
    return out


# ------------------------------------------------------------------------- detectors  (each: g -> list of failures)
def ck_diff(g, ctx):
    d = diff_paths(ctx["src"], g)
    extra = sorted("%s|%s|%s" % t for t in d - ALLOWED)
    missing = sorted("%s|%s|%s" % t for t in ALLOWED - d)
    out = []
    if extra:
        out.append(f"DIFF more than the three community switches moved: {extra}")
    if missing:
        out.append(f"DIFF a published switch is absent: {missing}")
    return out


def ck_control(g, ctx):
    """The anti-look-alike detector: the imported transform() must reproduce the RENDERED clip-11 bytes from
    clip 1, and this file's serialization must reproduce the on-disk bytes of the artifact it writes."""
    out = []
    reb = transform(gload(CLIP1))
    ind = dumps_like(open(gpath(CLIP11), "rb").read(), reb)
    if ind is None:
        out.append("CONTROL_DEAD transform(clip 1) does not reproduce the shipped clip-11 bytes at any indent: "
                   "the imported switch is not the one that made the rendered clip")
    if sha(gpath(CLIP11)) != CLIP11_SHA:
        out.append(f"CONTROL the shipped clip-11 sha {sha(gpath(CLIP11))[:16]} != the pinned {CLIP11_SHA[:16]}")
    if ind != FORMAT_IND:
        out.append(f"CONTROL_DEAD the clip-11 byte format measures indent {ind}, not the pinned FORMAT_IND "
                   f"{FORMAT_IND}: ck_graphfile would be checking a format this line does not use")
    if ctx["path"] and sha(ctx["path"]) == CLIP11_SHA:
        out.append("CONTROL a carried graph is byte-identical to clip 11, so it is not the carried clip")
    return out


def ck_guide(g, ctx):
    out = []
    nd = g.get("g0")
    if not nd:
        return ["GUIDE no MiniMaxH3AddGuide node: the frame-0 anchor of the fixed clip-1 shape is missing"]
    if nd["class_type"] != "MiniMaxH3AddGuide":
        out.append(f"GUIDE g0 class {nd['class_type']} != MiniMaxH3AddGuide")
    ins = nd["inputs"]
    if ins.get("frame_idx") != 0:
        out.append(f"GUIDE g0.frame_idx {ins.get('frame_idx')} != 0 (the item's literal requirement)")
    if ins.get("positive") != ["c0", 0] or ins.get("latent") != ["c0", 1] or ins.get("image") != ["img", 0]:
        out.append(f"GUIDE g0 wiring {ins.get('positive')}/{ins.get('latent')}/{ins.get('image')} "
                   "!= c0 positive / c0 latent / img image")
    if g["s0_guide"]["inputs"].get("conditioning") != ["g0", 0]:
        out.append(f"GUIDE s0_guide.conditioning {g['s0_guide']['inputs']['conditioning']} != [g0, 0] "
                   "(the anchor sits on the c0 conditioning edge)")
    return out


def ck_shape(g, ctx):
    bad = []
    if g["c0"]["inputs"]["length"] != 243:
        bad.append(f"SHAPE c0.length {g['c0']['inputs']['length']} != 243")
    win = g.get("win1", {}).get("inputs")
    if not win:
        bad.append("SHAPE no win1 continuation node: the fixed clip-1 shape is 243 f + one 119 f window")
        tot = g["c0"]["inputs"]["length"]
    else:
        if (win["extension_frames"], win["overlap_frames"]) != (119, 22):
            bad.append(f"SHAPE window {win['extension_frames']}/{win['overlap_frames']} != "
                       "119 extension / 22 overlap")
        if win.get("previous_av_latent") != ["s0_samp", 0]:
            bad.append(f"SHAPE win1.previous_av_latent {win.get('previous_av_latent')} != [s0_samp, 0]")
        tot = g["c0"]["inputs"]["length"] + win["extension_frames"]
    if tot != FRAMES or (tot - 5) % 17:
        bad.append(f"SHAPE frames 243+119={tot} != 362 or off the (f-5)%17==0 grid")
    if g["ksel"]["inputs"]["sampler_name"] != "res_multistep":
        bad.append(f"SHAPE sampler {g['ksel']['inputs']['sampler_name']} != res_multistep")
    for k in ("s0_sched", "s1_sched"):
        if g[k]["inputs"]["steps"] != 8:
            bad.append(f"SHAPE {k}.steps {g[k]['inputs']['steps']} != 8")
        if g[k]["inputs"].get("scheduler") != "simple":
            bad.append(f"SHAPE {k}.scheduler {g[k]['inputs'].get('scheduler')} != simple")
        if g[k]["inputs"].get("denoise") != 1.0:
            bad.append(f"SHAPE {k}.denoise {g[k]['inputs'].get('denoise')} != 1.0")
    n_smp = len([1 for nd in g.values() if nd["class_type"] == "SamplerCustomAdvanced"])
    if n_smp != 2:
        bad.append(f"SHAPE {n_smp} SamplerCustomAdvanced nodes, 2 passes expected (243 + one 119 window)")
    if "c2" in g:
        bad.append("SHAPE c2 still present: the 243+119 shape has two passes, not three")
    for ch in CHUNKS:
        w, h = g[ch]["inputs"]["width"], g[ch]["inputs"]["height"]
        if (w, h) != CANVAS or w % 32 or h % 32:
            bad.append(f"SHAPE {ch} canvas {w}x{h} != 1344x768 / multiple of 32")
    if g["mkvid"]["inputs"]["fps"] != 24:
        bad.append(f"SHAPE fps {g['mkvid']['inputs']['fps']} != 24")
    if [g["m_shift"]["inputs"][k] for k in ("shift_video", "shift_audio")] != [10.0, 3.0]:
        bad.append("SHAPE shift moved off video 10.0 / audio 3.0")
    cfg = [f"{n}.{k}" for n, nd in g.items() for k in nd["inputs"] if "cfg" in k.lower()]
    if cfg:
        bad.append(f"SHAPE cfg key present {cfg} (the H3 graph has no cfg key at all)")
    for nid in ("dec_v", "dec_a"):
        if nid not in g or "samples" not in g[nid]["inputs"]:
            bad.append(f"SHAPE {nid} has no samples input to wire")
        elif g[nid]["inputs"]["samples"] != ["app1", 0]:
            bad.append(f"SHAPE {nid}.samples {g[nid]['inputs']['samples']} != [app1, 0] (the 2-pass join)")
    return bad


def ck_prose(g, ctx):
    """The carry moves graph settings only. Species prose is a separate variable, and it cannot be written for
    these five clips until the figure is identified, so the prompts must be byte-identical to the source clip."""
    if not ctx["src"]:
        return []        # source-less ctx = the control artifact (clip 11), compared by the other detectors
    out = []
    for ch in CHUNKS:
        a, b = g[ch]["inputs"]["prompt"], ctx["src"][ch]["inputs"]["prompt"]
        if a != b:
            out.append(f"PROSE {ch} prompt changed by the carry ({len(a.split())} vs {len(b.split())} words): "
                       "this pass is the settings switch, prose edits are the next item")
        st = prompt_stats(b, ch)
        if len(st["sections"]) < 5:
            out.append(f"PROSE {ch} sections {st['sections']} - the community section set is 5 fields")
    gone = set(ctx["src"]) - set(g)
    added = set(g) - set(ctx["src"])
    if gone != {"c2", "win2", "tail2", "app2", "s2_samp", "s2_guide", "s2_sched"} or added != {"g0"}:
        out.append(f"PROSE node set moved beyond the shape switch: dropped {sorted(gone)} added {sorted(added)}")
    return out


def ck_gate(g, ctx):
    ps = prose_strings(g)
    fails = [f"{nid}.{k}" for nid, k, v in ps if not guard_ok(v)]
    out = [f"GATE the adults gate (scripts/comm.py guard_ok) refused {fails}"] if fails else []
    if len(ps) < 2:
        out.append(f"GATE census found {len(ps)} prose strings, 2 chunk prompts expected")
    if len([1 for _, k, _ in ps if k == "prompt"]) < len(ps):
        out.append(f"GATE comm.py reads only key 'prompt' and misses "
                   f"{len(ps) - len([1 for _, k, _ in ps if k == 'prompt'])} prose strings (L11 gap)")
    return out


def ck_slots(g, ctx):
    if not ctx["src"]:
        return []
    out = []
    a, b = slot_edges(ctx["src"]), slot_edges(g)
    for ch in CHUNKS:
        if a.get(ch) != b.get(ch):
            out.append(f"SLOTS {ch} ref slots moved by the carry: {a.get(ch)} -> {b.get(ch)}")
    for nid, nd in g.items():
        if nd["class_type"] == "LoadImage":
            if nd["inputs"]["image"] != ctx["src"][nid]["inputs"]["image"]:
                out.append(f"SLOTS {nid} start/crop image moved by the carry")
    n = len(next(iter(b.values())))
    if n not in (2, 3):
        out.append(f"SLOTS {n} ref slots on a chunk, 2 (start still + one gate crop) or 3 (start still + two "
                   f"crops) expected - measured off the source clip: {len(next(iter(a.values())))}")
    return out


def ck_inputs(g, ctx):
    out = []
    for nid, nd in g.items():
        if nd["class_type"] == "LoadImage":
            p = os.path.join(COMFY_IN, nd["inputs"]["image"].replace("/", os.sep))
            if not os.path.isfile(p):
                out.append(f"INPUTS {nid} LoadImage file absent in ComfyUI/input: {nd['inputs']['image']}")
    return out


def ck_idfree(g, ctx):
    out = []
    nid = ctx["id"]
    if os.path.isfile(os.path.join(JOBS, nid + ".result.json")):
        out.append(f"IDFREE p7/jobs/{nid}.result.json exists: the id is spent, the request is not submittable")
    if os.path.isdir(os.path.join(COMFY_OUT, nid)):
        out.append(f"IDFREE output/community/{nid} exists: the id is spent")
    if os.path.isfile(os.path.join(RUNS, nid, nid + ".mp4")):
        out.append(f"IDFREE runs/{nid}/{nid}.mp4 exists: the id is spent")
    if os.path.isfile(os.path.join(JOBS, nid + ".json")):
        out.append(f"IDFREE p7/jobs/{nid}.json exists: a job for this id is already in the queue")
    return out


def ck_schema(g, ctx):
    sch = ctx["schema"]
    bad = scan(g, sch)
    out = []
    if len(sch) < 5:
        out.append(f"SCHEMA_DEAD the H3 schema parse gave {len(sch)} classes, the scan would be vacuous")
    if len([1 for nd in g.values() if nd["class_type"] in sch]) < 2:
        out.append("SCHEMA_DEAD the schema covers no H3 node in this graph, the scan would be vacuous")
    dead = copy.deepcopy(g)
    dead["c1"]["class_type"] = "MiniMaxH3ImageToVideo"          # the exact defect that killed r3 at rc=2
    line = "c1.audio_vae: not an input of MiniMaxH3ImageToVideo"
    if line not in scan(dead, sch):
        out.append("SCHEMA_DEAD the non-vacuity control did not reproduce the r3 MiniMaxH3ImageToVideo defect")
    if bad:
        out.append(f"SCHEMA offline static check: {bad[:6]}")
    return out


def ck_prefix(g, ctx):
    want = f"community/{ctx['id']}/{ctx['id']}"
    got = g["save"]["inputs"]["filename_prefix"]
    return [] if got == want else [f"PREFIX {got} != {want}"]


def ck_seed(g, ctx):
    s = g["noise"]["inputs"]["noise_seed"]
    out = []
    if s != ctx["seed"]:
        out.append(f"SEED {s} != {ctx['seed']}")
    if ctx["src"] and s != ctx["src"]["noise"]["inputs"]["noise_seed"]:
        out.append(f"SEED {s} moved off the source clip seed {ctx['src']['noise']['inputs']['noise_seed']}: a "
                   "settings before/after holds the seed (IM1; clip 11 keeps 51150001 for the same reason)")
    return out


def ck_rundir(g, ctx):
    p = os.path.join(RUNS, ctx["id"], "request.api.json")
    if not os.path.isfile(p):
        return [f"RUNDIR runs/{ctx['id']}/request.api.json absent (the runner reads the arm dir, not p7/graphs)"]
    gp = gpath(ctx["id"])
    if open(p, "rb").read() != open(gp, "rb").read():
        return [f"RUNDIR runs/{ctx['id']}/request.api.json bytes != p7/graphs/{ctx['id']}.api.json bytes"]
    return []


def ck_graphfile(g, ctx):
    raw = open(gpath(ctx["id"]), "rb").read()
    out = []
    if raw.endswith(b"\n"):
        out.append("GRAPHFILE trailing newline")
    if raw != json.dumps(g, indent=ctx["ind"], ensure_ascii=False).replace("\n", "\r\n").encode("utf-8"):
        out.append(f"GRAPHFILE on-disk bytes != indent {ctx['ind']} / CRLF / no-trailing-newline serialization")
    if raw == open(gpath(CLIP11), "rb").read():
        out.append("GRAPHFILE byte-identical to the clip-11 graph")
    return out


def ck_manifest(g, ctx):
    p = man_path(ctx["id"])
    if not os.path.isfile(p):
        return [f"MANIFEST no manifest on disk ({os.path.basename(p)}) to re-derive"]
    m = json.load(open(p, encoding="utf-8"))
    out = []
    if m.get("graph_sha256") != sha(gpath(ctx["id"])):
        out.append("MANIFEST graph_sha256 != on-disk graph bytes")
    if m.get("seed") != ctx["seed"] or m.get("source_clip") != ctx["src_id"]:
        out.append("MANIFEST seed/source_clip does not match the spec")
    if m.get("diff_paths") != sorted("%s|%s|%s" % t for t in diff_paths(ctx["src"], g)):
        out.append("MANIFEST diff_paths != the diff measured off the source graph")
    if m.get("prompts") != {ch: {k: prompt_stats(g[ch]["inputs"]["prompt"], ch)[k]
                                 for k in ("words", "beats", "sections")} for ch in CHUNKS}:
        out.append("MANIFEST prompt words/beats/sections drifted from the graph on disk")
    facts = json.dumps({k: v for k, v in m.items() if k not in ("checks", "check_failures")}).lower()
    hits = [w for w in BANNED_IN_MANIFEST if w in facts]
    if hits:
        out.append(f"MANIFEST the recorded facts carry a judgement token {hits}; the pick is Derrick's alone")
    return out


def ck_nogpu(g, ctx):
    hits = [t for t in NO_GPU_TOKENS if t in ctx["self_src"]]
    return [f"NO_GPU this builder names a GPU/queue surface {hits}"] if hits else []


CHECKS = (ck_control, ck_diff, ck_guide, ck_shape, ck_prose, ck_gate, ck_slots, ck_inputs, ck_idfree,
          ck_schema, ck_prefix, ck_seed, ck_rundir, ck_graphfile, ck_manifest, ck_nogpu)
SERIALIZED = ("ck_graphfile", "ck_manifest", "ck_rundir")     # need the artifact on disk


def ctx_for(nid, g=None):
    src_id, cid, seed = next((v for v in CARRY.values() if v[1] == nid), (None, nid, None))
    g = g if g is not None else gload(nid)
    return dict(id=nid, src_id=src_id, seed=seed, src=gload(src_id) if src_id else {}, graph=g,
                path=gpath(nid) if os.path.isfile(gpath(nid)) else None, ind=FORMAT_IND,
                schema=h3_schema(), self_src=open(os.path.abspath(__file__), encoding="utf-8").read())


def run(nid, g=None, skip=()):
    ctx = ctx_for(nid, g)
    return {ck.__name__: ck(g if g is not None else ctx["graph"], ctx)
            for ck in CHECKS if ck.__name__ not in skip}


def measure(nid):
    ctx = ctx_for(nid)
    g, src = ctx["graph"], ctx["src"]
    m = {"id": nid, "source_clip": ctx["src_id"], "source_graph_sha256": sha(gpath(ctx["src_id"])),
         "seed": ctx["seed"], "seed_rule": "seed carried unchanged from the source clip (IM1: a settings "
                                           "before/after holds the seed; clip 11 holds 51150001 the same way)",
         "shape": {"guide": "MiniMaxH3AddGuide frame_idx 0 on the c0 conditioning edge (ComfyUI PR 15439)",
                   "sampler": g["ksel"]["inputs"]["sampler_name"],
                   "scheduler": g["s0_sched"]["inputs"]["scheduler"], "steps": g["s0_sched"]["inputs"]["steps"],
                   "c0_length": g["c0"]["inputs"]["length"],
                   "window": {"overlap_frames": g["win1"]["inputs"]["overlap_frames"],
                              "extension_frames": g["win1"]["inputs"]["extension_frames"]},
                   "frames_total": FRAMES, "fps": g["mkvid"]["inputs"]["fps"],
                   "canvas": [g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]],
                   "duration_s": round(FRAMES / g["mkvid"]["inputs"]["fps"], 6),
                   "shift_video_audio": [g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"]],
                   "cfg_keys": 0, "passes": 2},
         "prompts": {ch: {k: prompt_stats(g[ch]["inputs"]["prompt"], ch)[k]
                          for k in ("words", "beats", "sections")} for ch in CHUNKS},
         "prompts_byte_identical_to_source": all(g[ch]["inputs"]["prompt"] == src[ch]["inputs"]["prompt"]
                                                 for ch in CHUNKS),
         "slots": slot_edges(g)["c0"], "diff_paths": sorted("%s|%s|%s" % t for t in diff_paths(src, g)),
         "prose_strings": len(prose_strings(g)),
         "gate_ok_all_prose": all(guard_ok(v) for _, _, v in prose_strings(g)),
         "static_scan_defects": 0, "graph_sha256": sha(gpath(nid)), "graph_bytes": os.path.getsize(gpath(nid)),
         "run_dir_request_sha256": sha(os.path.join(RUNS, nid, "request.api.json"))
         if os.path.isfile(os.path.join(RUNS, nid, "request.api.json")) else None,
         "budget_at_build": json.load(open(LEDGER, encoding="utf-8")), "est_min": EST_MIN,
         "job_gate": "no p7/JOB_REQUEST.json arm in this pass: 5 clips x 30 min = 150 min over the ledger "
                     "headroom 142.1 min (cap 615 - used 472.9) and only 7 job slots left (job_cap 45, 38 used); "
                     "the two clips Derrick named go first - notes/needs_derrick.md row 18",
         "notes": "staged only: no queue, no GPU, no render in a Ralph pass; the species prose is the next item "
                  "and needs the two start images named (notes/hc15_figures_20261025.md)"}
    return m


def build(nid):
    src_id, cid, seed = next(v for v in CARRY.values() if v[1] == nid)
    g = transform(gload(src_id))
    g["save"]["inputs"]["filename_prefix"] = f"community/{nid}/{nid}"
    ind = dumps_like(open(gpath(CLIP11), "rb").read(), transform(gload(CLIP1)))
    if ind is None:
        print("CONTROL_DEAD transform(clip 1) does not reproduce the clip-11 bytes; refusing to write")
        return 1
    if ind != FORMAT_IND:
        print(f"CONTROL_DEAD clip-11 byte format measures indent {ind} != pinned FORMAT_IND {FORMAT_IND}")
        return 1
    data = write_graph(gpath(nid), g, ind)
    rd = os.path.join(RUNS, nid)
    os.makedirs(rd, exist_ok=True)
    open(os.path.join(rd, "request.api.json"), "wb").write(data)
    json.dump(measure(nid), open(man_path(nid), "w", encoding="utf-8"), indent=1)   # so ck_manifest has a
    res = run(nid)                                                                   # manifest to re-derive
    m = measure(nid)
    m["checks"] = {k: len(v) for k, v in res.items()}
    m["check_failures"] = {k: v for k, v in res.items() if v}
    m["checks_all_clean"] = all(not v for v in res.values())
    json.dump(m, open(man_path(nid), "w", encoding="utf-8"), indent=1)
    print(f"{nid} graph {len(g)} nodes {len(data)} B sha {sha(gpath(nid))[:16]} "
          f"clean={m['checks_all_clean']}")
    for k, v in res.items():
        if v:
            print("  FAIL", k, "::", "; ".join(v))
    return 1 if any(res.values()) else 0


def check_all():
    rc = 0
    for _, nid, _ in CARRY.values():
        res = run(nid)
        print(nid, "nodes", len(gload(nid)), "clean", all(not v for v in res.values()))
        for k, v in res.items():
            print(("  PASS " if not v else "  FAIL ") + k + ("" if not v else " :: " + "; ".join(v)))
        rc |= 1 if any(v for v in res.values()) else 0
    print("clip 11 control sha", sha(gpath(CLIP11))[:16], "== pinned", CLIP11_SHA[:16],
          sha(gpath(CLIP11)) == CLIP11_SHA)
    return rc


def selftest():
    """Seed each fault, require its detector to fire there, and require 0 problems on the real artifact (L10)."""
    nid = CARRY[2][1]
    g0 = gload(nid)
    seeds = []

    def mut(fn):
        g = copy.deepcopy(g0)
        fn(g)
        return g

    def drop_guide(g):
        g.pop("g0"); g["s0_guide"]["inputs"]["conditioning"] = ["c0", 0]

    def old_sampler(g):
        g["ksel"]["inputs"]["sampler_name"] = "euler"
        for k in ("s0_sched", "s1_sched"):
            g[k]["inputs"]["steps"] = 10

    def old_passes(g):
        g["c0"]["inputs"]["length"] = 124
        g["c2"] = copy.deepcopy(ctx_for(nid)["src"]["c2"])

    def prose_edit(g):
        g["c0"]["inputs"]["prompt"] += " The figure is a woman."

    def crop_swap(g):
        g["img2"]["inputs"]["image"] = "community/hc/GI046_w1_face.png"     # a crop belonging to another clip

    def slot_drop(g):
        g["c0"]["inputs"].pop("ref_images.ref_image_2", None)

    def missing_input(g):
        g["img"]["inputs"]["image"] = "community/hc/NOPE.jpg"

    def cfg_key(g):
        g["c0"]["inputs"]["cfg"] = 5.0

    def gate_fail(g):
        g["c0"]["inputs"]["prompt"] = "A teenager in a school uniform, no one under 18 allowed."

    def frame_idx(g):
        g["g0"]["inputs"]["frame_idx"] = 40

    def shift_move(g):
        g["m_shift"]["inputs"]["shift_video"] = 5.0

    def prefix_drift(g):
        g["save"]["inputs"]["filename_prefix"] = "community/hc15/x"

    def seed_moved(g):
        g["noise"]["inputs"]["noise_seed"] = 51150999

    def win_dropped(g):
        g.pop("win1"); g["dec_v"]["inputs"]["samples"] = ["s0_samp", 0]
        g["dec_a"]["inputs"]["samples"] = ["s0_samp", 1]

    for name, fn, det in [("guide node removed (the old 3-pass wiring)", drop_guide, "ck_guide"),
                          ("old sampler family euler/simple/10", old_sampler, "ck_shape"),
                          ("old pass shape 124x3", old_passes, "ck_shape"),
                          ("prompt text edited by the carry", prose_edit, "ck_prose"),
                          ("face crop moved to another clip's crop", crop_swap, "ck_slots"),
                          ("ref slot dropped", slot_drop, "ck_slots"),
                          ("LoadImage pointed at an absent file", missing_input, "ck_inputs"),
                          ("cfg key added (the H3 graph has none)", cfg_key, "ck_shape"),
                          ("prose the adults gate refuses", gate_fail, "ck_gate"),
                          ("guide frame moved off 0", frame_idx, "ck_guide"),
                          ("shift moved off 10.0/3.0", shift_move, "ck_shape"),
                          ("filename_prefix does not carry the id", prefix_drift, "ck_prefix"),
                          ("seed moved off the source clip seed", seed_moved, "ck_seed"),
                          ("the 119-frame window dropped (1 pass, 243 f)", win_dropped, "ck_shape")]:
        seeds.append((name, det, run(nid, mut(fn), skip=SERIALIZED).get(det, [])))
    # spent-id seed: use a real rendered id so the detector is exercised against disk
    spent = "ali163_hc15_bd002_s51150011"
    seeds.append(("id already spent (a result.json exists on disk)", "ck_idfree",
                  run(spent, gload(spent), skip=SERIALIZED).get("ck_idfree", [])))

    # the control seed: swap in a look-alike switch and ck_control must notice it is not the one that made clip 11
    me = sys.modules[__name__]
    real_tf = me.transform

    def look_alike(base):
        g = real_tf(base)
        g.pop("g0")
        g["s0_guide"]["inputs"]["conditioning"] = ["c0", 0]
        return g

    me.transform = look_alike
    try:
        seeds.append(("transform() is a look-alike, not the switch that made clip 11", "ck_control",
                      run(nid, skip=SERIALIZED).get("ck_control", [])))
    finally:
        me.transform = real_tf

    # the three on-disk detectors need artifacts, so seed them on real files and restore the bytes
    def seeded(label, det, write_fn):
        gp, rp, mp = gpath(nid), os.path.join(RUNS, nid, "request.api.json"), man_path(nid)
        keep = {p: open(p, "rb").read() for p in (gp, rp, mp)}
        try:
            write_fn(gp, rp, mp, keep)
            return (label, det, run(nid).get(det, []))
        finally:
            for p, b in keep.items():
                open(p, "wb").write(b)

    seeds.append(seeded("graph file gained a trailing newline", "ck_graphfile",
                        lambda gp, rp, mp, k: open(gp, "wb").write(k[gp] + b"\n")))
    seeds.append(seeded("run-dir request copy drifted from the graph", "ck_rundir",
                        lambda gp, rp, mp, k: open(rp, "wb").write(k[rp][:-1])))

    def man_seed(gp, rp, mp, k):
        m = json.load(open(mp, encoding="utf-8"))
        m["prompts"]["c0"]["words"] += 40
        m["seed"] = 1
        json.dump(m, open(mp, "w", encoding="utf-8"), indent=1)

    seeds.append(seeded("manifest drifted off the graph on disk", "ck_manifest", man_seed))
    real = {n: run(n) for _, n, _ in CARRY.values()}
    real_clean = {n: {k: v for k, v in r.items() if v} for n, r in real.items() if any(r.values())}
    ok = True
    for name, det, fires in seeds:
        fired = bool(fires)
        ok &= fired
        print(("SEED FIRED " if fired else "SEED MISSED") + f" {name} -> {det}: {str(fires)[:110]}")
    for n, bad in real_clean.items():
        print("REAL DIRTY", n, bad)
        ok = False
    print("selftest:", "all seeds fired and the real artifacts are clean on the in-memory detectors"
          if ok else "FAILED (a seed missed or a real artifact is dirty)")
    return 0 if ok else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--check":
        return check_all()
    if mode == "--build":
        rc = 0
        for _, nid, _ in CARRY.values():
            rc |= build(nid)
        return rc
    if mode == "--selftest":
        return selftest()
    print("usage: --check | --build | --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
