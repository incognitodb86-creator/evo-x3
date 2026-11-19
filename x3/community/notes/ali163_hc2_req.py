"""ALI-163 HC2: write p7/JOB_REQUEST.json (trailing newline) + graph_diff vs the PV2 source, then verify."""
import json, os, subprocess, hashlib
W = r"C:\AI\community"
ID = "ali147_pool_hc_c2_s51100002"
SRC = os.path.join(W, "runs", "ali147_pool_promptv2_s51080000", "request.api.json")
DST = os.path.join(W, "runs", "ali147_pool_hc_c2_s51100002", "request.api.json")
REQ = os.path.join(W, "p7", "JOB_REQUEST.json")
DIFF = os.path.join(W, "notes", "ali163_hc2_graph_diff.txt")
fails = []

def ck(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

job = {"jobs": [{"id": ID, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}]}
raw = (json.dumps(job) + "\n").encode("utf-8")
open(REQ, "wb").write(raw)
print("JOB_REQUEST bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest())
ck(open(REQ, "rb").read() == raw and raw.endswith(b"\n"), "JOB_REQUEST written with trailing newline")
ck(json.loads(open(REQ, encoding="utf-8").read()) == job, "JOB_REQUEST parses to exactly that one job")
r = subprocess.run(["python", "-m", "json.tool", REQ], capture_output=True, text=True)
ck(r.returncode == 0, "python -m json.tool JOB_REQUEST.json")
r = subprocess.run(["python", "-m", "json.tool", DST], capture_output=True, text=True)
ck(r.returncode == 0, "python -m json.tool request.api.json")
r = subprocess.run(["git", "-C", W, "diff", "--no-index", "--output=" + DIFF, SRC, DST],
                   capture_output=True, text=True)
ck(r.returncode == 1, f"git diff --no-index exit 1 (diff found) rc={r.returncode}")
d = open(DIFF, encoding="utf-8", errors="replace").read()
rem = sum(1 for L in d.split("\n") if L.startswith("-") and not L.startswith("---"))
add = sum(1 for L in d.split("\n") if L.startswith("+") and not L.startswith("+++"))
hunks = d.count("@@")
print("graph_diff hunks", hunks, "removed", rem, "added", add)
for key in ('"width": 768', '"width": 1344', '"height": 768', '"height": 1344',
            'community/hc/HC2_Two_women_in_passionate_embrace.jpg', '"noise_seed": 51100002',
            'community/ali147_pool_hc_c2_s51100002/ali147_pool_hc_c2_s51100002',
            'overall_soundscape', 'non_diegetic_music'):
    ck(key in d, f"graph_diff contains {key}")
print("ALL CHECKS PASS" if not fails else "CHECKS FAIL " + json.dumps(fails))
