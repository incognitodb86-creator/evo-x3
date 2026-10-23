# ALI-163 R3: write p7\JOB_REQUEST.json (trailing newline, the accepted shape) for the sheet job. One job only.
import json, os
P = "C:/Users/derek/5slock/ralph-community/p7/JOB_REQUEST.json"
req = {"jobs": [{"id": "ali147_pool_hc_sheet_s51120000", "kind": "graph", "frames": 0, "frames_tol": 0, "minutes": 180}]}
raw = json.dumps(req, indent=1) + "\n"          # accepted shape: json.dumps default + trailing newline
os.makedirs(os.path.dirname(P), exist_ok=True)   # ralph.ps1:121 New-Item -Force makes p7 at run time; it is absent between batches
open(P, "w", encoding="utf-8", newline="\n").write(raw)
d = open(P, "rb").read()
print("bytes", len(d), "sha256", __import__("hashlib").sha256(d).hexdigest())
print("jobs", len(json.loads(d.decode())["jobs"]), "trailing newline", d.endswith(b"\n"))
print(d.decode())
