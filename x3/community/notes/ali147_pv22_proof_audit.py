# -*- coding: utf-8 -*-
# ALI-147 PV2-2 (read-only): PROOF.md literal-hash audit - no hardcoded expected hashes.
# Every 58..70-char hex token inside runs/ali147_pool_promptv2_seg3_s51080002/PROOF.md must be
# (a) exactly 64 chars (the AGENTS.md POOL literal is a 63-char truncation = a known FALSE-fail trap)
# and (b) equal to a hash MEASURED here from the file it names. Any token that matches nothing = a
# transcription error in my own PROOF.md.
import re, os, glob, json, hashlib

C = "C:/AI/community"
ARM = C + "/runs/ali147_pool_promptv2_seg3_s51080002"
SPEC = C + "/specs/prompt_v2"
BASE = C + "/runs/p7_r2_c3_pmot_full_pool"
COMFY_IN = "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
PROOF = ARM + "/PROOF.md"

def sha(b):
    return hashlib.sha256(b).hexdigest()

measured = {}
def add(name, path):
    with open(path, "rb") as f:
        measured[sha(f.read())] = name + " (" + os.path.basename(path) + ")"

add("source seg3 graph", BASE + "/p7_r2_c3_pmot_full_pool_seg3.api.json")
add("arm graph", ARM + "/request.api.json")
add("graph_diff", ARM + "/graph_diff.txt")
add("fairness", ARM + "/fairness.txt")
for n in ("v2_seg3_c0_r2v.txt", "v2_seg3_c1_t2va.txt"):
    add("prompt file", SPEC + "/" + n)
src = json.loads(open(BASE + "/p7_r2_c3_pmot_full_pool_seg3.api.json", "rb").read().decode("utf-8"))
for k in ("c0", "c1"):
    measured[sha(src[k]["inputs"]["prompt"].encode("utf-8"))] = "base graph %s.prompt (string hash)" % k
add("POOL still", os.path.join(COMFY_IN, "community", "POOL_768x1344.png"))
add("base seg3 mp4", BASE + "/p7_r2_c3_pmot_full_pool_seg3.mp4")
add("base stitched mp4", BASE + "/p7_r2_c3_pmot_full_pool_stitched.mp4")
add("JOB_REQUEST", C + "/p7/JOB_REQUEST.json")
add("p7 request model", C + "/p7/jobs/request_iter07.json")

raw = open(PROOF, encoding="utf-8").read()
toks = re.findall(r"[0-9a-f]{58,70}", raw)
bad = []
for t in sorted(set(toks)):
    if len(t) != 64:
        bad.append(("NOT_64_CHARS len=%d" % len(t), t))
    elif t not in measured:
        # is it a prefix of a measured hash (i.e. truncated in my text) or a typo at one position?
        near = [n for h, n in measured.items() if t[:24] == h[:24]]
        bad.append(("UNMEASURED" + (" near=" + json.dumps(near) if near else ""), t))
print("PROOF.md %d B, hex tokens %d (distinct %d)" % (len(raw.encode("utf-8")), len(toks), len(set(toks))))
for t in sorted(set(toks)):
    print("  ok  %s = %s" % (t, measured.get(t, "?")))
for r, t in bad:
    print("  BAD %s %s" % (r, t))
print("ALL HASH LITERALS IN PROOF.md ARE 64 CHARS AND EQUAL A MEASURED FILE" if not bad else "HASH LITERAL PROBLEMS " + json.dumps(bad))
