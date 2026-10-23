"""PV2-1 request write: p7/JOB_REQUEST.json for the PROMPT_V2 seg1 render (CPU only).

One job, kind=graph, id=ali147_pool_promptv2_s51080000, frames=481, frames_tol=0,
minutes=60 (ralph.ps1 clamps minutes to 30..180 and uses timeout = minutes*20 s; the
CTRL control rendered in 809.7 s = 13.5 min, so 60 is ample pre-job budget).

Byte shape = the accepted RS6 graph request archived as p7/jobs/request_iter02.json
(json.dumps with spaces after colons, LF, trailing newline), with only the id and the
numbers changed. Self-checks: the file is absent before writing, the written bytes
equal the expected string exactly, it parses to exactly one job, and key order matches
the accepted request.

Writes only C:/AI/community/p7/JOB_REQUEST.json.
Run: python notes/ali147_pv21_write_request.py
"""
import hashlib
import json
import os

REQ = r"C:/AI/community/p7/JOB_REQUEST.json"
MODEL = r"C:/AI/community/p7/jobs/request_iter02.json"   # the accepted RS6 graph request
NEW_ID = "ali147_pool_promptv2_s51080000"

fails = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


chk(not os.path.exists(REQ), "p7/JOB_REQUEST.json is absent before writing (the harness consumes it at exit)")
model = open(MODEL, encoding="utf-8").read()
old_id = json.loads(model)["jobs"][0]["id"]
expected = model.replace(old_id, NEW_ID)
chk(model.count(old_id) == 1, "the accepted request names its id exactly once: " + old_id)
chk(expected != model and json.loads(expected)["jobs"][0]["id"] == NEW_ID,
    "the expected text is the accepted form with only the id swapped")

job = {"id": NEW_ID, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}
text = json.dumps({"jobs": [job]}) + "\n"
chk(text == expected, "the bytes I am about to write == the accepted RS6 graph request with only the id changed")
chk(text.endswith("}\n") and "\r" not in text and text.count("\n") == 1, "single line, LF, one trailing newline")

with open(REQ, "wb") as f:
    f.write(text.encode("utf-8"))

raw = open(REQ, "rb").read()
print("wrote", REQ, "bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest())
print("bytes", repr(raw))
chk(raw == text.encode("utf-8"), "file bytes == the intended bytes")
j = json.loads(raw.decode("utf-8"))
chk(sorted(j) == ["jobs"] and len(j["jobs"]) == 1, "exactly one job, top key 'jobs' only")
chk(list(j["jobs"][0]) == ["id", "kind", "frames", "frames_tol", "minutes"],
    "job key order matches the accepted request (id, kind, frames, frames_tol, minutes)")
g = json.load(open(r"C:/AI/community/runs/%s/request.api.json" % NEW_ID, encoding="utf-8"))
chk(os.path.exists(r"C:/AI/community/runs/%s/request.api.json" % NEW_ID),
    "the graph the job points at exists (ralph.ps1:268 gate)")
chk(not os.path.exists(r"C:/AI/community/runs/%s/%s.mp4" % (NEW_ID, NEW_ID)),
    "no mp4 yet (ralph.ps1:269 'already rendered' gate clear)")
chk(g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"] == job["frames"],
    "frames=%d == c0 length 243 + win1 extension 238 (frames_tol 0)" % job["frames"])
chk(json.loads(model)["jobs"][0]["frames"] == 481 and json.loads(model)["jobs"][0]["minutes"] == 60,
    "481/0/60 matches the accepted 481-frame graph request (only the id differs)")
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
