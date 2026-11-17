"""RS6 pre-request check for REFSHEET_B (read-only, CPU only, no GPU call).

Validates runs/ali147_pool_refsheet_b_s51080000/request.api.json the way the harness
run_graph_job.py will at render time: adults-only guard on every prompt string
(scripts/comm.guard_ok), every LoadImage string resolving inside ComfyUI\\input
(folder_paths.get_annotated_filepath rule) with its sha256 recorded, and the arm
invariants: seed 51080000, steps 10, euler/simple, shift 10/3, 768x1344, 24 fps,
c0 length 243 + win1 238/22, c0 ref_image_1 = start still and ref_image_2 = the sheet,
ref_image_size max, save filename_prefix = the new id.

Fairness vs the parent arm REFSHEET: every node that is not c0 (the only intended
change) or save (filename_prefix) must be byte-identical, and the node key set identical.

Writes nothing, prints only. Run: python notes/ali147_refsheet_b_rs6_precheck.py
"""
import os, sys, json, hashlib

SCRIPTS = r"C:/AI/community/scripts"
ARM = r"C:/AI/community/runs/ali147_pool_refsheet_b_s51080000"
PARENT = r"C:/AI/community/runs/ali147_pool_refsheet_s51080000/request.api.json"
GRAPH = ARM + "/request.api.json"
COMFY_INPUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
SHEET_SHA = "da0b6a0b0c313e468cb225c7ca0e46dd97321722764aee9d7e76c7297b5caa4a"
STILL_SHA = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"
sys.path.insert(0, SCRIPTS)
import comm  # noqa: E402  adults-only guard lives here (scripts/comm.py, not edited)

fails = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def canon(node):
    return json.dumps(node, sort_keys=True)


g = json.load(open(GRAPH, encoding="utf-8"))
p = json.load(open(PARENT, encoding="utf-8"))
print("nodes", len(g), "parent_nodes", len(p), "bytes", os.path.getsize(GRAPH))

# 1) adults-only guard on every prompt string
prompts = [(k, n["inputs"]["prompt"]) for k, n in g.items() if isinstance(n["inputs"].get("prompt"), str)]
print("prompt_nodes", len(prompts), [k for k, _ in prompts])
for k, s in prompts:
    ok = comm.guard_ok(s)
    print("guard", k, "OK" if ok else "GUARD_HIT", "len", len(s),
          "sha256", hashlib.sha256(s.encode()).hexdigest())
    chk(ok, "guard_ok on " + k)

# 2) fairness vs REFSHEET: identical node set, only c0 + save may differ
chk(set(g) == set(p), "node key set identical to REFSHEET (no new node)")
diff = [k for k in g if canon(g[k]) != canon(p[k])]
print("differing_nodes", sorted(diff))
chk(sorted(diff) == ["c0", "save"], "only c0 (the one change) and save (filename_prefix) differ")

# 3) c0 = the arm's single change, in full
c0 = g["c0"]["inputs"]
print("c0 class", g["c0"]["class_type"])
for key in sorted(c0):
    if key != "prompt":
        print("  c0.", key, "=", json.dumps(c0[key])[:200])
chk(g["c0"]["class_type"] == "MiniMaxH3ReferenceToVideo", "c0 class MiniMaxH3ReferenceToVideo")
chk(c0["ref_images.ref_image_1"] == ["img", 0], "c0 ref_image_1 = start still node img")
chk(c0["ref_images.ref_image_2"] == ["sheet", 0], "c0 ref_image_2 = sheet node (reused from REFSHEET)")
chk(c0["ref_image_size"] == "max", "c0 ref_image_size max")
chk("ref_images.ref_image_3" not in c0, "c0 has no ref_image_3")
chk(c0["length"] == 243 and c0["width"] == 768 and c0["height"] == 1344, "c0 length 243 / 768x1344")
chk("<Picture 1>" in g["c0"]["inputs"]["prompt"] and "<Picture 2>" in g["c0"]["inputs"]["prompt"],
    "c0 prompt binds <Picture 1> (start still) and <Picture 2> (sheet)")
chk("subject_definitions:" in g["c0"]["inputs"]["prompt"], "c0 prompt starts with a subject_definitions block")
chk(g["c0"]["inputs"]["prompt"].split("summary:")[0] != p["c0"]["inputs"]["prompt"].split("summary:")[0]
    and g["c0"]["inputs"]["prompt"].split("summary:")[1] == p["c0"]["inputs"]["prompt"].split("summary:")[1],
    "c0 prompt: subject_definitions block only, tail from 'summary:' byte-identical to REFSHEET")

# 4) c1 untouched vs REFSHEET (chunk 2 stays as arm 5)
chk(canon(g["c1"]) == canon(p["c1"]), "c1 (chunk 2) byte-identical to REFSHEET")
c1 = g["c1"]["inputs"]
print("c1 ref_image_size", c1["ref_image_size"], "ref_image_1", c1["ref_images.ref_image_1"],
      "ref_image_2" in c1, "length", c1["length"])
chk("ref_images.ref_image_2" not in c1, "c1 has no ref_image_2 (arm 5b adds the sheet to c0 only)")

# 5) every LoadImage resolves inside ComfyUI\\input, with the expected sha256
for k in sorted([k for k, n in g.items() if n["class_type"] == "LoadImage"]):
    name = g[k]["inputs"]["image"]
    path = os.path.normpath(os.path.join(COMFY_INPUT, name.replace("/", os.sep)))
    inside = path.startswith(os.path.normpath(COMFY_INPUT))
    exists = os.path.exists(path)
    digest = sha256(path) if exists else None
    print("LoadImage", k, repr(name), "path", path, "inside_input", inside, "exists", exists,
          "bytes", os.path.getsize(path) if exists else None, "sha256", digest)
    chk(inside and exists, k + " resolves inside ComfyUI\\input (no 'Invalid file path')")
    if k == "sheet":
        chk(digest == SHEET_SHA, "sheet sha256 == RS1's da0b6a0b...")
    if k == "img":
        chk(digest == STILL_SHA, "start still sha256 == the graphs' 9cf9ff95... node image")

# 6) held-equal settings vs the parent arm
for k in ("noise", "s0_sched", "s1_sched", "ksel", "m_shift", "mkvid", "win1", "save"):
    for key in sorted(g[k]["inputs"]):
        if canon(g[k]["inputs"][key]) != canon(p[k]["inputs"][key]):
            print("DELTA", k, key, json.dumps(g[k]["inputs"][key]), "vs parent", json.dumps(p[k]["inputs"][key]))
chk(g["noise"]["inputs"]["noise_seed"] == 51080000, "seed 51080000")
chk(g["s0_sched"]["inputs"]["steps"] == 10 and g["s1_sched"]["inputs"]["steps"] == 10, "steps 10 on both schedulers")
chk(g["s0_sched"]["inputs"]["scheduler"] == "simple" and g["s1_sched"]["inputs"]["scheduler"] == "simple", "scheduler simple")
chk(g["ksel"]["inputs"]["sampler_name"] == "euler", "sampler euler")
chk(g["m_shift"]["inputs"]["shift_video"] == 10 and g["m_shift"]["inputs"]["shift_audio"] == 3, "shift 10/3")
chk(g["mkvid"]["inputs"]["fps"] == 24, "fps 24")
chk(g["win1"]["inputs"]["extension_frames"] == 238 and g["win1"]["inputs"]["overlap_frames"] == 22,
    "win1 238/22 (frames 243 + 238 - 22 = 459 + the 22 tail guide frames = 481)")
chk(g["save"]["inputs"]["filename_prefix"] == "community/ali147_pool_refsheet_b_s51080000/ali147_pool_refsheet_b_s51080000",
    "save filename_prefix = the new id")

# 7) job-id freedom (no prior run of this id -> no failed-<date> move needed)
for rel in ("status.log", "objective.json", "ali147_pool_refsheet_b_s51080000.mp4",
            "ali147_pool_refsheet_b_s51080000.api.json"):
    chk(not os.path.exists(os.path.join(ARM, rel)), "arm folder has no " + rel + " (id free)")
for rel in (r"C:/AI/community/p7/jobs/ali147_pool_refsheet_b_s51080000.result.json",):
    chk(not os.path.exists(rel), "no " + rel)

print("frames_target", 243 + g["win1"]["inputs"]["extension_frames"] - g["win1"]["inputs"]["overlap_frames"] + g["win1"]["inputs"]["overlap_frames"])
print("graph_diff.txt exists", os.path.exists(ARM + "/graph_diff.txt"),
      "bytes", os.path.getsize(ARM + "/graph_diff.txt") if os.path.exists(ARM + "/graph_diff.txt") else None)
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
