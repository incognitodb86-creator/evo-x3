"""ALI-147 FIX4_GRAPH builder + offline self-check (Forge Ralph, 2026-10-22).

CPU-only, offline. Reads the base run's three submitted API graphs and
specs/extender_object_info.json, writes
C:/AI/community/runs/ali147_pool_fix4_s51080000/request.api.json, then self-checks:
  json parse, every class_type + every input name in extender_object_info.json,
  all schema-required inputs present, 6 clips seed 51080000 seed_mode fixed,
  total frames within 24 of 1443, SaveVideo prefix present, Extender settings,
  model chain byte-identical to seg1, prompt provenance + sha256 of each prompt.
No GPU, no network, no ComfyUI call. Run: python <this file>
"""
import copy
import hashlib
import json
import os
import sys

BASE_DIR = r"C:/AI/community/runs/p7_r2_c3_pmot_full_pool"
BASE_API = BASE_DIR + "/p7_r2_c3_pmot_full_pool_%s.api.json"
OUT_DIR = r"C:/AI/community/runs/ali147_pool_fix4_s51080000"
OUT_FILE = OUT_DIR + "/request.api.json"
SPEC = r"C:/Users/derek/5slock/ralph-community/specs/extender_object_info.json"
SEED = 51080000
PREFIX = "community/ali147_pool_fix4_s51080000/ali147_pool_fix4_s51080000"
IMG = "community/POOL_768x1344.png"
SEGS = ["seg1", "seg2", "seg3"]
# per-segment chunk frames in the base run: chunk 1 = 243, chunk 2 = 238 (24 fps)
CHUNK_FRAMES = {"c0": 243, "c1": 238}
TARGET_FRAMES = 1443
TOL = 24
CHAIN_NODES = ["unet", "m_attn", "m_vsa", "m_shift", "clip", "vvae", "avae", "img"]

fails = []


def check(ok, label, detail=""):
    print(("PASS  " if ok else "FAIL  ") + label + (("  " + detail) if detail else ""))
    if not ok:
        fails.append(label)


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


base = {s: load(BASE_API % s) for s in SEGS}
spec = load(SPEC)


def sd_block(seg):
    """The chunk-1 subject_definitions block of that segment's c0 prompt."""
    p = base[seg]["c0"]["inputs"]["prompt"]
    head, sep, tail = p.partition("\n\nsummary:")
    assert sep, "no summary: separator in %s c0" % seg
    assert head.startswith("subject_definitions:\n"), "c0 block shape %s" % seg
    assert "<Picture 1>" in head, "c0 block has no <Picture 1> in %s" % seg
    return head


# clip order: seg1 c0, seg1 c1, seg2 c0, seg2 c1, seg3 c0, seg3 c1
clips = []
prompts = []
prompt_src = []
for seg in SEGS:
    blk = sd_block(seg)
    for chunk in ["c0", "c1"]:
        src = base[seg][chunk]["inputs"]["prompt"]
        if chunk == "c0":
            final = src  # already starts with its subject_definitions block
        else:
            final = blk + "\n\n" + src  # plan: add the block only where it is missing
        prompts.append(final)
        prompt_src.append("%s_%s" % (seg, chunk))
        clips.append({
            "id": "clip_%d" % (len(clips) + 1),
            "name": "%s_%s" % (seg, chunk),
            "prompt": final,
            "seed": SEED,
            "seed_mode": "fixed",
            "duration": round(CHUNK_FRAMES[chunk] / 24.0, 6),
            "validated": True,
            "color_adjustment": {"saturation": 100.0, "contrast": 100.0, "brightness": 100.0},
            "loras": [],
            "local_refs": {"version": 1, "images": [], "videos": [], "audios": []},
            "first_frame": None,
            "last_frame": None,
            "guides": [],
            "first_source": "manual",
        })
clips_json = json.dumps({"version": 2, "clips": clips}, ensure_ascii=True, separators=(",", ":"))
refs_json = json.dumps({"version": 2, "refs": [None] * 9}, separators=(",", ":"))

graph = {}
for node in CHAIN_NODES:  # byte-for-byte copy of the base graph's model chain
    graph[node] = copy.deepcopy(base["seg1"][node])

graph["rpack"] = {
    "class_type": "MiniMaxH3ReferencePackBridge",
    "inputs": {"ref_1": ["img", 0]},
}
graph["ppack"] = {
    "class_type": "MiniMaxH3PromptPackBridge",
    "inputs": {"prompt_%d" % (i + 1): p for i, p in enumerate(prompts)},
}
graph["ext"] = {
    "class_type": "MiniMaxH3Extender",
    "inputs": {
        "model": ["m_shift", 0],
        "clip": ["clip", 0],
        "vae": ["vvae", 0],
        "audio_vae": ["avae", 0],
        "prompt_pack": ["ppack", 0],
        "ref_pack": ["rpack", 0],
        "run_mode": "full_batch",
        "generation_mode": "ref2va",
        "motion_context": True,
        "refine_enabled": False,
        "refine_scale": 1.5,
        "refine_steps": 4,
        "refine_denoise": 0.3,
        "resolution_mode": "manual",
        "width": 768,
        "height": 1344,
        "megapixels": 0.4,
        "ref_image_size": "match",
        "steps": 10,
        "sampler_name": "euler",
        "scheduler": "simple",
        "denoise": 1.0,
        "context_length": "22",
        "audio_context_length": 0,
        "clips_json": clips_json,
        "refs_json": refs_json,
    },
}
graph["dec"] = {
    "class_type": "MiniMaxH3MotionContextDiskFinalDecode",
    "inputs": {
        "cache": ["ext", 0],
        "vae": ["vvae", 0],
        "audio_vae": ["avae", 0],
        "fps": 24.0,
        "filename_prefix": "ali147_pool_fix4_s51080000_decode",
        "output_directory": "",
        "codec": "H.264",
        "crf": 17,
        "preset": "fast",
        "audio_bitrate": "192k",
        "autoplay": False,
        "auto_save_project": False,
        "save_individual_clips": False,
    },
}
graph["save"] = {
    "class_type": "SaveVideo",
    "inputs": {
        "video": ["dec", 0],
        "filename_prefix": PREFIX,
        "format": "auto",
        "codec": "auto",
    },
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as fh:
    json.dump(graph, fh, indent=1, ensure_ascii=True)
    fh.write("\n")

print("wrote %s (%d nodes, %d bytes)" % (OUT_FILE, len(graph), os.path.getsize(OUT_FILE)))
print()

# ---------------- self-checks ----------------
raw = open(OUT_FILE, encoding="utf-8").read()
doc = json.loads(raw)
check(True, "check1 json.tool: file parses")


def allowed_names(node):
    """required + optional + every nested dynamic-combo key and its input names."""
    io = spec[node]["input"]
    names = set(io.get("required", {})) | set(io.get("optional", {}))
    keys = set()

    def walk(opts):
        for opt in opts:
            if not isinstance(opt, dict) or "key" not in opt:
                continue
            keys.add(opt["key"])
            sub = opt.get("inputs", {})
            for section in ("required", "optional"):
                for k, v in sub.get(section, {}).items():
                    names.add(k)
                    if isinstance(v, list) and len(v) > 1 and isinstance(v[1], dict) and "options" in v[1]:
                        keys.add(k)
                        walk(v[1]["options"])

    for section in ("required", "optional"):
        for k, v in io.get(section, {}).items():
            if isinstance(v, list) and len(v) > 1 and isinstance(v[1], dict) and "options" in v[1]:
                opts = v[1]["options"]
                if isinstance(opts, list):
                    walk(opts)
    return names, keys


bad_class = [n for n, c in doc.items() if c["class_type"] not in spec]
check(not bad_class, "check2 every class_type in extender_object_info.json", str(bad_class))
bad_in, miss_req = [], []
for n, c in doc.items():
    names, keys = allowed_names(c["class_type"])
    io = spec[c["class_type"]]["input"]
    for k in c["inputs"]:
        head, _, sub = k.partition(".")
        if head not in io.get("required", {}) and head not in io.get("optional", {}):
            bad_in.append("%s.%s" % (n, k))
        if sub and sub not in (keys | names):
            bad_in.append("%s.%s(nested)" % (n, k))
    for k in io.get("required", {}):
        if k not in c["inputs"]:
            miss_req.append("%s.%s" % (n, k))
check(not bad_in, "check3 every input name in extender_object_info.json", str(bad_in))
check(not miss_req, "check3b every schema-required input present", str(miss_req))

cj = json.loads(doc["ext"]["inputs"]["clips_json"])
fr = sum(c["duration"] * 24 for c in cj["clips"])
check(len(cj["clips"]) == 6, "check4 six clips", str(len(cj["clips"])))
check(all(c["seed"] == SEED and c["seed_mode"] == "fixed" for c in cj["clips"]),
      "check4 seed 51080000 + seed_mode fixed on every clip")
check(abs(fr - TARGET_FRAMES) <= TOL, "check5 total frames within %d of %d" % (TOL, TARGET_FRAMES),
      "sum(duration*24)=%.4f  per-clip=%s" % (fr, [round(c["duration"] * 24, 3) for c in cj["clips"]]))
check(PREFIX in raw and doc["save"]["inputs"]["filename_prefix"] == PREFIX,
      "check6 SaveVideo prefix string present", PREFIX)

want = {"run_mode": "full_batch", "generation_mode": "ref2va", "motion_context": True,
        "refine_enabled": False, "resolution_mode": "manual", "width": 768, "height": 1344,
        "steps": 10, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
        "context_length": "22", "audio_vae": ["avae", 0], "model": ["m_shift", 0],
        "vae": ["vvae", 0], "clip": ["clip", 0], "prompt_pack": ["ppack", 0], "ref_pack": ["rpack", 0]}
bad_sett = {k: doc["ext"]["inputs"].get(k) for k, v in want.items() if doc["ext"]["inputs"].get(k) != v}
check(not bad_sett, "check7 Extender settings match the spec", str(bad_sett))

chain_ok = all(doc[n] == base["seg1"][n] for n in CHAIN_NODES)
check(chain_ok, "check8 model chain byte-identical to seg1")

prov = []
for i, (src, p) in enumerate(zip(prompt_src, prompts)):
    seg, chunk = src.split("_")
    basep = base[seg][chunk]["inputs"]["prompt"]
    if chunk == "c0":
        ok = p == basep
    else:
        ok = p.endswith(basep) and p.startswith("subject_definitions:\n") and p.count("subject_definitions:") == 1
    prov.append((i + 1, src, ok, len(p), hashlib.sha256(p.encode()).hexdigest(),
                 hashlib.sha256(basep.encode()).hexdigest()))
check(all(x[2] for x in prov), "check9 prompt provenance: c0 verbatim, c1 = own-segment block + verbatim text")
print()
print("prompt pack (clip index, base source, final len, final sha256, base sha256):")
for idx, src, ok, ln, h, bh in prov:
    print("  clip_%d %s ok=%s len=%d sha256=%s base_sha256=%s" % (idx, src, ok, ln, h[:16], bh[:16]))
print("  full sha256s:")
for idx, src, ok, ln, h, bh in prov:
    print("   clip_%d %s final=%s base=%s" % (idx, src, h, bh))
print()
print("ref_image: %s" % doc["img"]["inputs"]["image"])
print("ref sha (file bytes): ", end="")
p_path = None
for root in [r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"]:
    cand = os.path.join(root, IMG.replace("/", os.sep))
    if os.path.exists(cand):
        p_path = cand
print((hashlib.sha256(open(p_path, "rb").read()).hexdigest()) if p_path else "input dir not readable here")
print()
print("RESULT:", "ALL CHECKS PASS" if not fails else "FAILURES: %s" % fails)
sys.exit(1 if fails else 0)
