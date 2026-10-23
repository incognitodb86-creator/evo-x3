"""PV2-1 graph build (CPU only, no GPU/ComfyUI call, no render).

Copy the CTRL graph runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json into
runs/ali147_pool_promptv2_s51080000/request.api.json with EXACTLY three edits:
  c0.inputs.prompt     = the exact text of specs/prompt_v2/v2_seg1_c0_r2v.txt
  c1.inputs.prompt     = the exact text of specs/prompt_v2/v2_seg1_c1_t2va.txt
  save.filename_prefix = community/ali147_pool_promptv2_s51080000/ali147_pool_promptv2_s51080000
Nothing else (seed 51080000 is already the CTRL seed and is not touched).

Method: raw line-targeted replacement, so every other byte of the file is untouched
(the source is indent=1 + CRLF, the same shape as the arm request.api.json files that
rendered byte-identically through the harness). Self-checks after writing:
  - the parsed graph is canonical json.dumps(indent=1, ensure_ascii=True) + the source tail
  - the node key set is identical to the source and the differing node set is exactly
    ['c0', 'c1', 'save']; within them only the one intended input key differs
  - c0/c1 prompt strings == the file bytes decoded UTF-8, sha256 == SHA256SUMS values

Writes only runs/ali147_pool_promptv2_s51080000/request.api.json.
Run: python notes/ali147_pv21_build_graph.py
"""
import json
import hashlib
import os

SRC = r"C:/AI/community/runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json"
DST_DIR = r"C:/AI/community/runs/ali147_pool_promptv2_s51080000"
DST = DST_DIR + "/request.api.json"
NEW_ID = "ali147_pool_promptv2_s51080000"
P0 = r"C:/AI/community/specs/prompt_v2/v2_seg1_c0_r2v.txt"
P1 = r"C:/AI/community/specs/prompt_v2/v2_seg1_c1_t2va.txt"
EDITS = [("c0", "prompt", P0), ("c1", "prompt", P1)]

raw_src = open(SRC, "rb").read()
text_src = raw_src.decode("utf-8")
tail = "\r\n}"                                   # the file ends "}CRLF}" -> the tail after the last line
assert text_src.endswith(tail), repr(text_src[-8:])
body = text_src[: -len(tail)]
lines = body.split("\r\n")

fails = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_value(path):
    raw = open(path, "rb").read()
    txt = raw.decode("utf-8")
    chk(raw.count(b"\r\n") == 0 and not txt.endswith("\n"),
        os.path.basename(path) + " has no CRLF and no trailing newline (verbatim text is safe)")
    return txt


new_prompt = {("c0", "prompt"): new_value(P0), ("c1", "prompt"): new_value(P1)}
prefix = "community/%s/%s" % (NEW_ID, NEW_ID)

node = None
hits = {}
out = list(lines)
for i, line in enumerate(lines):
    if line.startswith(' "') and line.endswith('": {'):
        node = line.strip()[1:].split('"', 1)[0]
        continue
    if node in ("c0", "c1", "save") and line.startswith('   "'):
        key = line[4:].split('"', 1)[0]
        if (node, key) in new_prompt and (node, key) not in hits:
            new = json.dumps(new_prompt[(node, key)], ensure_ascii=True)
            hits[(node, key)] = i
        elif (node, key) == ("save", "filename_prefix") and (node, key) not in hits:
            new = json.dumps(prefix, ensure_ascii=True)
            hits[(node, key)] = i
        else:
            continue
        indent = line[: len(line) - len(line.lstrip())]
        comma = "," if line.rstrip().endswith(",") else ""
        out[i] = '%s"%s": %s%s' % (indent, key, new, comma)

chk(sorted(hits) == [("c0", "prompt"), ("c1", "prompt"), ("save", "filename_prefix")],
    "3 target lines found, one each: " + json.dumps({("%s.%s" % k): hits[k] for k in sorted(hits)}))

new_text = "\r\n".join(out) + tail
os.makedirs(DST_DIR, exist_ok=True)
with open(DST, "wb") as f:
    f.write(new_text.encode("utf-8"))

# ---- self-checks on the file we just wrote ----
raw = open(DST, "rb").read()
g = json.loads(raw.decode("utf-8"))
s = json.loads(text_src)
print("wrote", DST, "bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest())
chk(raw == new_text.encode("utf-8"), "file bytes == the intended bytes (UTF-8, CRLF, no trailing newline)")
canon = json.dumps(g, indent=1, ensure_ascii=True)
chk(new_text.replace("\r\n", "\n") == canon, "file text is canonical json.dumps(indent=1, ensure_ascii=True)")
chk(list(g) == list(s), "node key order identical to the CTRL source")
chk(set(g) == set(s), "node key set identical to the CTRL source (%d nodes)" % len(g))
diff = [k for k in g if json.dumps(g[k], sort_keys=True) != json.dumps(s[k], sort_keys=True)]
print("differing_nodes", sorted(diff))
chk(sorted(diff) == ["c0", "c1", "save"], "only c0, c1, save differ (nothing else)")
for k in diff:
    keys = [ik for ik in g[k]["inputs"]
            if json.dumps(g[k]["inputs"][ik], sort_keys=True) != json.dumps(s[k]["inputs"][ik], sort_keys=True)]
    chk(keys == (["prompt"] if k in ("c0", "c1") else ["filename_prefix"]),
        "%s: only inputs.%s changed (keys %s)" % (k, keys[0] if keys else "?", keys))
chk(g["c0"]["inputs"]["prompt"] == new_prompt[("c0", "prompt")],
    "c0 prompt == v2_seg1_c0_r2v.txt text exactly")
chk(g["c1"]["inputs"]["prompt"] == new_prompt[("c1", "prompt")],
    "c1 prompt == v2_seg1_c1_t2va.txt text exactly")
chk(sha(g["c0"]["inputs"]["prompt"]) == "889c543a13cfb3d0e37c20198a2d03cc3d9e4b32934ad2ce71b37b359d3175b6",
    "c0 prompt sha256 == SHA256SUMS 889c543a...")
chk(sha(g["c1"]["inputs"]["prompt"]) == "655e92a8f668f51e74bececce3471bcc32492bfdd1ade7377b456b65eec17d2b",
    "c1 prompt sha256 == SHA256SUMS 655e92a8...")
chk(g["c1"]["inputs"]["prompt"] != s["c1"]["inputs"]["prompt"], "c1 prompt really changed (was CTRL's)")
chk(g["save"]["inputs"]["filename_prefix"] == prefix, "save filename_prefix = " + prefix)
chk(g["noise"]["inputs"]["noise_seed"] == 51080000, "seed stays 51080000 (untouched)")
chk(g["c0"]["inputs"]["length"] == 243 and g["c0"]["inputs"]["width"] == 768
    and g["c0"]["inputs"]["height"] == 1344, "c0 length 243 / 768x1344 unchanged")
chk(g["c1"]["inputs"]["length"] == ["win1", 1], "c1 length stays [win1, 1]")
chk(g["win1"]["inputs"]["extension_frames"] == 238 and g["win1"]["inputs"]["overlap_frames"] == 22,
    "win1 stays 238/22 (243 + 238 + 0 = 481)")
chk(raw.count(b"\n") == raw.count(b"\r\n") and not raw.endswith(b"\n"),
    "file is pure CRLF with no trailing newline (same shape as the source)")
print("ALL CHECKS PASS" if not fails else "FAILS " + json.dumps(fails))
