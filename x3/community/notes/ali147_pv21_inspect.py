import json, hashlib, os

CTRL_DIR = r"C:/AI/community/runs/ali147_pool_ctrl_s51080000"
PRETTY = os.path.join(CTRL_DIR, "submitted_graph.pretty.json")
API = os.path.join(CTRL_DIR, "ali147_pool_ctrl_s51080000.api.json")
PROMPT_DIR = r"C:/AI/community/specs/prompt_v2"


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def load(p):
    return json.loads(open(p, "rb").read().decode("utf-8"))


a = load(PRETTY)
b = load(API)
print("pretty nodes", len(a), "api nodes", len(b))
print("key sets equal:", sorted(a) == sorted(b), "sym:", sorted(set(a) ^ set(b)))
diff = [k for k in a if json.dumps(a[k], sort_keys=True) != json.dumps(b.get(k), sort_keys=True)]
print("node bodies differing:", diff)
print("key order identical:", list(a) == list(b))
print()
for k, v in a.items():
    print(k, v["class_type"], sorted(v["inputs"].keys()))
print()
for k, v in a.items():
    if v["class_type"] in ("SaveVideo", "SaveImage", "SaveAnimatedWEBP"):
        print("SAVE NODE", k, json.dumps(v, indent=1, sort_keys=True))
    if v["class_type"] in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo"):
        ins = v["inputs"]
        for ik, iv in ins.items():
            if isinstance(iv, str) and len(iv) > 80:
                print("COND NODE", k, v["class_type"], "input", ik, "len", len(iv), "sha256", sha(iv))
            elif ik == "seed":
                print("COND NODE", k, "seed", iv)
            elif ik in ("width", "height", "length", "steps", "sampler_name", "scheduler", "denoise", "ref_image_size"):
                print("COND NODE", k, ik, iv)
print()
for n in ("v2_seg1_c0_r2v.txt", "v2_seg1_c1_t2va.txt"):
    p = os.path.join(PROMPT_DIR, n)
    raw = open(p, "rb").read()
    txt = raw.decode("utf-8")
    print(n, "bytes", len(raw), "sha256", sha(raw), "chars", len(txt), "CRLF", raw.count(b"\r\n"),
          "endsNL", txt.endswith("\n"), "ascii", raw.decode("ascii", "ignore") == txt)
print()
print("objective.json:", open(os.path.join(CTRL_DIR, "objective.json")).read())
print("status.log:", open(os.path.join(CTRL_DIR, "status.log")).read())
