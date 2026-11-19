"""PV2-1 pre-request check for PROMPT_V2 seg1 (read-only, CPU only; no GPU/ComfyUI/
llama-swap call, no render, no run_graph_job.py).

Validates runs/ali147_pool_promptv2_s51080000/request.api.json the way the harness
run_graph_job.py will at render time:
  1. the adults-only guard on every prompt string (scripts/comm.guard_ok, the same call
     run_graph_job.py:60 makes; a hit = exit 3 CLIP_SKIP)
  2. the static check by equivalence: every class_type and every input key is identical
     to the CTRL graph that already rendered ok (specs/extender_object_info.json only
     covers Extender nodes, and the live node list is a GPU call), so nothing new is asked
  3. every LoadImage string resolves inside ComfyUI\\input with its sha256
  4. arm invariants: seed 51080000, steps 10 euler/simple, shift 10/3, 768x1344, 24 fps,
     c0 length 243 + win1 238/22 -> 481 frames, save filename_prefix = the new id
  5. fairness vs CTRL: identical node key set, the differing node set is exactly
     ['c0','c1','save'], and inside them only prompt / prompt / filename_prefix
  6. the two prompts are the PROMPT_V2 files verbatim (sha256 == specs/prompt_v2/SHA256SUMS.txt)
  7. the job id is accepted by the ralph.ps1 gates PARSED from the live file (a hardcoded
     copy proves nothing), the id is free, and logs/p7_budget.json has room for ~16 min
  8. graph_diff.txt exists and shows 3 removed + 3 added lines

Writes only notes/. Run: python notes/ali147_pv21_precheck.py
"""
import hashlib
import json
import os
import re
import sys

SCRIPTS = r"C:/AI/community/scripts"
RUNS = r"C:/AI/community/runs"
NEW_ID = "ali147_pool_promptv2_s51080000"
ARM = os.path.join(RUNS, NEW_ID)
GRAPH = os.path.join(ARM, "request.api.json")
CTRL_DIR = os.path.join(RUNS, "ali147_pool_ctrl_s51080000")
CTRL_SRC = os.path.join(CTRL_DIR, "submitted_graph.pretty.json")
CTRL_API = os.path.join(CTRL_DIR, "ali147_pool_ctrl_s51080000.api.json")
PROMPT_DIR = r"C:/AI/community/specs/prompt_v2"
COMFY_INPUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
RALPH = r"C:/Users/derek/5slock/ralph-community/ralph.ps1"
BUDGET = r"C:/Users/derek/5slock/ralph-community/logs/p7_budget.json"
JOBS = r"C:/AI/community/p7/jobs"
EXPECT = {"v2_seg1_c0_r2v.txt": "889c543a13cfb3d0e37c20198a2d03cc3d9e4b32934ad2ce71b37b359d3175b6",
          "v2_seg1_c1_t2va.txt": "655e92a8f668f51e74bececce3471bcc32492bfdd1ade7377b456b65eec17d2b"}
sys.path.insert(0, SCRIPTS)
import comm  # noqa: E402  adults-only guard lives here (scripts/comm.py, not edited)

fails = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def sha_bytes(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def canon(x):
    return json.dumps(x, sort_keys=True)


raw = open(GRAPH, "rb").read()
g = json.loads(raw.decode("utf-8"))
c = json.loads(open(CTRL_SRC, "rb").read().decode("utf-8"))
ca = json.loads(open(CTRL_API, "rb").read().decode("utf-8"))
print("graph", GRAPH)
print("bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest(), "nodes", len(g))

# 1) adults-only guard on every prompt string (the harness's exact call)
prompts = [(k, n["inputs"]["prompt"]) for k, n in g.items() if isinstance(n["inputs"].get("prompt"), str)]
print("prompt_nodes", len(prompts), [k for k, _ in prompts])
chk(sorted(k for k, _ in prompts) == ["c0", "c1"], "exactly the 2 conditioning nodes carry prompt strings")
for k, s in prompts:
    ok = comm.guard_ok(s)
    print("guard", k, "OK" if ok else "GUARD_HIT", "chars", len(s),
          "sha256", hashlib.sha256(s.encode("utf-8")).hexdigest())
    chk(ok, "comm.guard_ok passes for " + k + " (no CLIP_SKIP / exit 3)")

# 2) static check by equivalence with the CTRL graph that already rendered ok
chk(set(g) == set(c), "node key set identical to the CTRL source graph (%d nodes)" % len(g))
chk(set(g) == set(ca), "node key set identical to the CTRL .api.json that rendered (481 frames ok)")
chk(sorted((n["class_type"], tuple(sorted(n["inputs"]))) for n in g.values())
    == sorted((n["class_type"], tuple(sorted(n["inputs"]))) for n in ca.values()),
    "every class_type and input-key set matches the rendered CTRL graph (static check by equivalence)")

# 3) LoadImage resolves inside ComfyUI\input
for k in sorted([k for k, n in g.items() if n["class_type"] == "LoadImage"]):
    name = g[k]["inputs"]["image"]
    path = os.path.normpath(os.path.join(COMFY_INPUT, name.replace("/", os.sep)))
    inside = path.startswith(os.path.normpath(COMFY_INPUT))
    exists = os.path.exists(path)
    digest = sha_bytes(path) if exists else None
    print("LoadImage", k, repr(name), "path", path, "inside_input", inside, "exists", exists,
          "bytes", os.path.getsize(path) if exists else None, "sha256", digest)
    chk(inside and exists, k + " resolves inside ComfyUI\\input (no 'Invalid file path')")
    chk(len(STILL_SHA) == 64, "STILL_SHA literal is 64 hex chars (a 63-char typo is a FALSE FAIL trap)")
    chk(digest == STILL_SHA, k + " sha256 == the graphs' start still 9cf9ff95...")
chk(g["c0"]["inputs"]["ref_images.ref_image_1"] == ["img", 0], "c0 ref_image_1 = the start still node")
chk("ref_images.ref_image_2" not in g["c0"]["inputs"], "c0 has no ref_image_2 (no sheet in this arm)")
chk(g["c0"]["class_type"] == "MiniMaxH3ReferenceToVideo" and g["c1"]["class_type"] == "MiniMaxH3ImageToVideo",
    "chunk 1 = MiniMaxH3ReferenceToVideo, chunk 2 = MiniMaxH3ImageToVideo (as CTRL)")

# 4) arm invariants
chk(g["noise"]["inputs"]["noise_seed"] == 51080000, "seed 51080000 (the task's 'Seed 51080000')")
chk(g["s0_sched"]["inputs"]["steps"] == 10 and g["s1_sched"]["inputs"]["steps"] == 10, "steps 10 on both schedulers")
chk(g["s0_sched"]["inputs"]["scheduler"] == "simple" and g["s1_sched"]["inputs"]["scheduler"] == "simple", "scheduler simple")
chk(g["s0_sched"]["inputs"]["denoise"] == 1.0, "denoise 1.0")
chk(g["ksel"]["inputs"]["sampler_name"] == "euler", "sampler euler")
chk(g["m_shift"]["inputs"]["shift_video"] == 10 and g["m_shift"]["inputs"]["shift_audio"] == 3, "shift 10/3")
chk(canon(g["m_attn"]) == canon(c["m_attn"]) and canon(g["m_attn"]["inputs"]) == canon(ca["m_attn"]["inputs"]),
    "m_attn attention backend " + json.dumps(g["m_attn"]["inputs"].get("attention")) +
    " is byte-identical to the rendered CTRL graph (not edited, value taken from CTRL)")
chk(g["mkvid"]["inputs"]["fps"] == 24, "fps 24")
chk(g["c0"]["inputs"]["length"] == 243 and g["c0"]["inputs"]["width"] == 768
    and g["c0"]["inputs"]["height"] == 1344, "c0 length 243 / 768x1344")
chk(g["c1"]["inputs"]["length"] == ["win1", 1] and g["c1"]["inputs"]["width"] == 768
    and g["c1"]["inputs"]["height"] == 1344, "c1 length = [win1, 1] / 768x1344")
chk(g["win1"]["inputs"]["extension_frames"] == 238 and g["win1"]["inputs"]["overlap_frames"] == 22,
    "win1 238/22 -> 243 + 238 = 481 frames (the request's frames=481, frames_tol=0)")
chk(g["save"]["inputs"]["filename_prefix"] == "community/%s/%s" % (NEW_ID, NEW_ID),
    "save filename_prefix = the new id")
chk(g["save"]["inputs"]["format"] == "auto" and g["save"]["inputs"]["codec"] == "auto", "save format/codec auto")

# 5) fairness vs CTRL
diff = [k for k in g if canon(g[k]) != canon(c[k])]
print("differing_nodes_vs_CTRL", sorted(diff))
chk(sorted(diff) == ["c0", "c1", "save"], "only c0, c1, save differ from the CTRL graph")
for k, want in (("c0", ["prompt"]), ("c1", ["prompt"]), ("save", ["filename_prefix"])):
    keys = [ik for ik in g[k]["inputs"] if canon(g[k]["inputs"][ik]) != canon(c[k]["inputs"][ik])]
    chk(keys == want, "%s: exactly inputs.%s changed" % (k, want[0]))
chk(canon(g["s0_guide"]) == canon(c["s0_guide"]) and canon(g["s1_guide"]) == canon(c["s1_guide"]),
    "guiders unchanged (conditioning wiring is CTRL's)")
chk(canon(g["m_vsa"]) == canon(c["m_vsa"]) and canon(g["unet"]) == canon(c["unet"])
    and canon(g["clip"]) == canon(c["clip"]) and canon(g["vvae"]) == canon(c["vvae"])
    and canon(g["avae"]) == canon(c["avae"]), "model chain (unet/m_attn/m_vsa/m_shift/clip/vaels) byte-identical to CTRL")
chk(canon(g["tail1"]) == canon(c["tail1"]) and canon(g["app1"]) == canon(c["app1"]),
    "continuation nodes (tail1/app1/win1) byte-identical to CTRL")

# 6) prompts are the PROMPT_V2 files verbatim, matching SHA256SUMS.txt
sums = {}
for line in open(os.path.join(PROMPT_DIR, "SHA256SUMS.txt"), encoding="utf-8"):
    m = re.match(r"^([0-9a-f]{64})\s+\*?\s*(\S+)\s*$", line.strip())
    if m:
        sums[m.group(2)] = m.group(1)
print("SHA256SUMS entries", len(sums))
for node, fname in (("c0", "v2_seg1_c0_r2v.txt"), ("c1", "v2_seg1_c1_t2va.txt")):
    p = os.path.join(PROMPT_DIR, fname)
    fbytes = open(p, "rb").read()
    txt = fbytes.decode("utf-8")
    digest = sha_bytes(p)
    print(node, fname, "file bytes", len(fbytes), "sha256", digest)
    chk(digest == sums.get(fname) == EXPECT[fname], fname + " sha256 == SHA256SUMS.txt and the PV2-0 record")
    chk(g[node]["inputs"]["prompt"] == txt, node + " prompt == the file text verbatim (chars %d)" % len(txt))
    chk(g[node]["inputs"]["prompt"] != c[node]["inputs"]["prompt"], node + " prompt differs from CTRL's")
    ctrl_tail = c[node]["inputs"]["prompt"].split("summary:")
    new_tail = txt.split("summary:")
    print(node, "CTRL sections", len(ctrl_tail), "new sections", len(new_tail),
          "CTRL chars", len(c[node]["inputs"]["prompt"]), "new chars", len(txt))
print("control prompt sha256", {k: hashlib.sha256(c[k]["inputs"]["prompt"].encode()).hexdigest()[:16]
                               for k in ("c0", "c1")})

# 7) harness gates, parsed from the live ralph.ps1
ps1 = open(RALPH, encoding="utf-8").read()
pats = re.findall(r"\$id -notmatch '(\^[^']+)'", ps1)
print("live ralph.ps1 id patterns", pats)
chk(len(pats) >= 2, "parsed the live id gates out of ralph.ps1 (%d patterns)" % len(pats))
for p in pats:
    chk(re.match(p, NEW_ID) is not None, "id %s accepted by live pattern %s" % (NEW_ID, p))
chk(not os.path.exists(os.path.join(JOBS, NEW_ID + ".result.json")),
    "no p7\\jobs\\%s.result.json (ralph.ps1:185 id-already-used gate clear)" % NEW_ID)
for rel in ("status.log", "objective.json", "request.api.json", NEW_ID + ".mp4", NEW_ID + ".api.json"):
    chk(os.path.exists(os.path.join(ARM, rel)) if rel == "request.api.json"
        else not os.path.exists(os.path.join(ARM, rel)),
        "arm folder: request.api.json present / no " + rel + " (id free, graph ready)")
b = json.load(open(BUDGET, encoding="utf-8"))
print("p7_budget", b)
est = 809.7 / 60.0
chk(b["used_min"] + est < b["cap_min"] and b["jobs"] + 1 <= b["job_cap"],
    "budget has room: used %.1f + ~%.1f < cap %s, jobs %s+1 <= %s"
    % (b["used_min"], est, b["cap_min"], b["jobs"], b["job_cap"]))

# 8) graph_diff
gd = os.path.join(ARM, "graph_diff.txt")
dlines = open(gd, encoding="utf-8").read().split("\n")
minus = [l for l in dlines if l.startswith("-") and not l.startswith("---")]
plus = [l for l in dlines if l.startswith("+") and not l.startswith("+++")]
print("graph_diff bytes", os.path.getsize(gd), "removed", len(minus), "added", len(plus),
      "sha256", sha_bytes(gd))
chk(len(minus) == 3 and len(plus) == 3, "graph_diff shows exactly 3 removed + 3 added lines (c0/c1 prompt, filename_prefix)")

print("CTRL control render secs", json.load(open(os.path.join(CTRL_DIR, "objective.json")))["secs"])
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
