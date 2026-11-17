import os, json, hashlib
C = "C:/AI/community"
SRC = C + "/runs/p7_r2_c3_pmot_full_pool/p7_r2_c3_pmot_full_pool_seg3.api.json"
ARM = C + "/runs/ali147_pool_promptv2_seg3_s51080002"
DST = ARM + "/request.api.json"
P0 = C + "/specs/prompt_v2/v2_seg3_c0_r2v.txt"
P1 = C + "/specs/prompt_v2/v2_seg3_c1_t2va.txt"
PREFIX = "community/ali147_pool_promptv2_seg3_s51080002/ali147_pool_promptv2_seg3_s51080002"
RPT = C + "/notes/ali147-pv22-build-20261022.txt"
L = []
ok = [True]
def p(s):
    L.append(str(s))
def sha(b):
    return hashlib.sha256(b).hexdigest()
def chk(cond, label):
    p(("PASS " if cond else "FAIL ") + label)
    if not cond:
        ok[0] = False
raw = open(SRC, "rb").read()
src_text = raw.decode("utf-8")
g = json.loads(src_text)
p0 = open(P0, "rb").read().decode("utf-8")
p1 = open(P1, "rb").read().decode("utf-8")
chk(len(p0) == 4358, "p0 chars 4358 (got %d)" % len(p0))
chk(sha(p0.encode()) == "ad77122b96f4ad474a6329a72b556f3372a80cb010e68a6c3ea10fe48a53763b", "p0 sha256 == SHA256SUMS v2_seg3_c0_r2v")
chk(len(p1) == 2903, "p1 chars 2903 (got %d)" % len(p1))
chk(sha(p1.encode()) == "2e3905ee2272a9d7ff0ab47d5db1765e4fa456ba4aa5ae2798e3fac404cfb383", "p1 sha256 == SHA256SUMS v2_seg3_c1_t2va")
old = {"c0.prompt": g["c0"]["inputs"]["prompt"], "c1.prompt": g["c1"]["inputs"]["prompt"], "save.filename_prefix": g["save"]["inputs"]["filename_prefix"]}
p("source c0.prompt chars %d sha256 %s" % (len(old["c0.prompt"]), sha(old["c0.prompt"].encode())))
p("source c1.prompt chars %d sha256 %s" % (len(old["c1.prompt"]), sha(old["c1.prompt"].encode())))
p("source filename_prefix %r" % old["save.filename_prefix"])
g["c0"]["inputs"]["prompt"] = p0
g["c1"]["inputs"]["prompt"] = p1
g["save"]["inputs"]["filename_prefix"] = PREFIX
new = json.dumps(g, indent=1, ensure_ascii=True).replace("\n", "\r\n").encode("utf-8")
os.makedirs(ARM, exist_ok=True)
open(DST, "wb").write(new)
p("wrote %s bytes %d sha256 %s" % (DST, len(new), sha(new)))
chk(sha(raw) == "c5b6726c1d5870f597ba51fcf65499d489be9a1755ebf1905ab8fac5960e8fec", "source seg3 api.json sha256 c5b6726c (10910 B)")
# format self-check: reserialized canonical == file with CRLF folded
chk(new.decode("utf-8").replace("\r\n", "\n") == json.dumps(json.loads(new.decode("utf-8")), indent=1, ensure_ascii=True), "file is canonical json.dumps(indent=1, ensure_ascii=True)")
chk(new.count(b"\n") == new.count(b"\r\n") and not new.endswith(b"\n"), "pure CRLF, no trailing newline (accepted arm request shape)")
rj = json.loads(new.decode("utf-8"))
chk(rj == g, "reparse == built graph")
chk(rj["c0"]["inputs"]["prompt"] == p0 and rj["c1"]["inputs"]["prompt"] == p1, "prompts verbatim in the graph")
chk(rj["save"]["inputs"]["filename_prefix"] == PREFIX, "filename_prefix = " + PREFIX)
chk(rj["noise"]["inputs"]["noise_seed"] == 51080002, "seed stays 51080002 (base seg3 seed)")
# node-level fairness
src = json.loads(src_text)
diffnodes = [k for k in sorted(src) if json.dumps(src[k], sort_keys=True) != json.dumps(rj[k], sort_keys=True)]
chk(sorted(src.keys()) == sorted(rj.keys()), "node key set unchanged (25 nodes)")
chk(diffnodes == ["c0", "c1", "save"], "differing nodes exactly ['c0','c1','save'] (got %s)" % json.dumps(diffnodes))
changed = {}
for k in diffnodes:
    changed[k] = [ik for ik in sorted(src[k]["inputs"]) if json.dumps(src[k]["inputs"][ik], sort_keys=True) != json.dumps(rj[k]["inputs"][ik], sort_keys=True)]
    if sorted(src[k]["inputs"].keys()) != sorted(rj[k]["inputs"].keys()):
        p("NOTE input key set changed on " + k)
chk(changed == {"c0": ["prompt"], "c1": ["prompt"], "save": ["filename_prefix"]}, "changed inputs exactly prompt/prompt/filename_prefix (got %s)" % json.dumps(changed))
# line-level diff
sln = src_text.split("\r\n")
nln = new.decode("utf-8").split("\r\n")
chk(len(sln) == len(nln), "same line count (%d vs %d)" % (len(sln), len(nln)))
idx = [i for i in range(min(len(sln), len(nln))) if sln[i] != nln[i]]
p("differing line indices %s" % json.dumps(idx))
chk(len(idx) == 3, "exactly 3 changed lines")
for (node, key, oval, nval) in (("c0", "prompt", old["c0.prompt"], p0), ("c1", "prompt", old["c1.prompt"], p1), ("save", "filename_prefix", old["save.filename_prefix"], PREFIX)):
    eo = json.dumps(oval)[1:-1]
    en = json.dumps(nval)[1:-1]
    hit = [i for i in idx if ("\"%s\": \"%s\"," % (key, eo)) in sln[i] or sln[i].strip() == ("\"%s\": \"%s\"," % (key, eo))]
    p("target %s.%s source-line hits %s" % (node, key, json.dumps(hit)))
    chk(len(hit) == 1 and en in nln[hit[0]] and eo not in nln[hit[0]], "line %d = %s.%s new value only" % (hit[0] if hit else -1, node, key))
# settings held equal (copied from source by construction, verified on the built graph)
chk(rj["unet"]["inputs"]["unet_name"] == src["unet"]["inputs"]["unet_name"], "checkpoint unchanged")
chk(rj["m_attn"]["inputs"]["attention"] == "comfy kitchen attention", "m_attn attention 'comfy kitchen attention' unchanged (NOT vsa)")
chk(json.dumps(rj["m_vsa"], sort_keys=True) == json.dumps(src["m_vsa"], sort_keys=True), "VSA patch node identical (selection vsa, keep_percent %s)" % rj["m_vsa"]["inputs"]["selection.keep_percent"])
for n in ("s0_sched", "s1_sched"):
    chk(rj[n]["inputs"]["steps"] == 10 and rj[n]["inputs"]["scheduler"] == "simple" and rj[n]["inputs"]["denoise"] == 1.0, n + " steps 10 / simple / denoise 1.0")
chk(rj["m_shift"]["inputs"]["shift_video"] == 10.0 and rj["m_shift"]["inputs"]["shift_audio"] == 3.0, "sigma shift 10/3")
chk(rj["ksel"]["inputs"]["sampler_name"] == "euler", "sampler euler")
chk(rj["c0"]["inputs"]["width"] == 768 and rj["c0"]["inputs"]["height"] == 1344 and rj["c1"]["inputs"]["width"] == 768 and rj["c1"]["inputs"]["height"] == 1344, "768x1344 on c0/c1")
chk(rj["mkvid"]["inputs"]["fps"] == 24, "CreateVideo fps 24")
chk(rj["c0"]["inputs"]["length"] == 243 and rj["win1"]["inputs"]["extension_frames"] == 238, "c0 length 243 + win1 extension 238 = 481")
chk(rj["c1"]["inputs"]["length"] == ["win1", 1], "c1.length = ['win1', 1] (238)")
chk(rj["win1"]["inputs"]["overlap_frames"] == src["win1"]["inputs"]["overlap_frames"], "win1.overlap_frames unchanged (%s)" % rj["win1"]["inputs"]["overlap_frames"])
chk(rj["c0"]["inputs"]["ref_image_size"] == "match", "c0 ref_image_size match (unchanged)")
chk(rj["c0"]["inputs"]["ref_images.ref_image_1"] == ["img", 0], "c0 ref_images.ref_image_1 = ['img', 0] (unchanged)")
chk(rj["img"]["inputs"]["image"] == "community/POOL_768x1344.png", "LoadImage string unchanged")
chk(len([1 for n in rj.values() if isinstance(n.get("inputs", {}).get("prompt"), str)]) == 2, "only c0/c1 carry prompt strings")
open(RPT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
print("ALL CHECKS PASS" if ok[0] else "CHECKS FAILED")
print("REPORT " + RPT)
