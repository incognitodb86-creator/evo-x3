import os, json, hashlib, glob
C = "C:/AI/community"
NAME = "ali147_pool_promptv2_seg3_s51080002"
REQ = C + "/p7/JOB_REQUEST.json"
MODEL = C + "/p7/jobs/request_iter07.json"
def sha(b):
    return hashlib.sha256(b).hexdigest()
raw = open(MODEL, "rb").read().decode("utf-8")
old = "ali147_pool_promptv2_s51080000"
assert raw.count(old) == 1, "model id count"
new = raw.replace(old, NAME)
assert new.endswith("\n") and new.count("\n") == 1, "model trailing newline"
obj = json.loads(new)
assert list(obj.keys()) == ["jobs"], json.dumps(list(obj.keys()))
assert len(obj["jobs"]) == 1, "one job only"
job = obj["jobs"][0]
assert job == {"id": NAME, "kind": "graph", "frames": 481, "frames_tol": 0, "minutes": 60}, json.dumps(job)
b = new.encode("utf-8")
open(REQ, "wb").write(b)
chk = open(REQ, "rb").read()
print("wrote %s bytes %d sha256 %s" % (REQ, len(chk), sha(chk)))
print("content: " + repr(chk.decode("utf-8")))
print("model  : " + repr(raw))
print("bytes differ from model (id length): %d" % (len(chk) - len(open(MODEL, "rb").read())))
print("same shape as model: %s" % (chk.decode("utf-8").replace(NAME, old) == raw))
print("parsed job: " + json.dumps(json.loads(chk.decode("utf-8"))["jobs"][0]))
print("model job : " + json.dumps(json.loads(raw)["jobs"][0]))
print("p7 jobs request_iter files: " + json.dumps(sorted(os.path.basename(x) for x in glob.glob(C + "/p7/jobs/request_iter*.json"))))
