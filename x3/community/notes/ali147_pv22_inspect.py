import os, json, hashlib, re
C = "C:/AI/community"
RUNS = C + "/runs"
BASE = RUNS + "/p7_r2_c3_pmot_full_pool"
SRC = BASE + "/p7_r2_c3_pmot_full_pool_seg3.api.json"
ARM = RUNS + "/ali147_pool_promptv2_seg3_s51080002"
PROMPTS = C + "/specs/prompt_v2"
OUT = C + "/notes/ali147-pv22-inspect-20261022.txt"
L = []
def p(s):
    L.append(str(s))
def sha(b):
    return hashlib.sha256(b).hexdigest()
def files(d):
    if not os.path.isdir(d):
        p("MISSING DIR " + d)
        return
    for n in sorted(os.listdir(d)):
        fp = os.path.join(d, n)
        p("  %12d  %s" % (os.path.getsize(fp) if os.path.isfile(fp) else -1, n))
p("== listing " + BASE)
files(BASE)
p("== listing " + PROMPTS)
files(PROMPTS)
p("== listing " + RUNS + "/ali147_pool_promptv2_s51080000")
files(RUNS + "/ali147_pool_promptv2_s51080000")
p("== arm dir exists: " + str(os.path.isdir(ARM)))
if os.path.isdir(ARM):
    files(ARM)
p("== p7 dir")
files(C + "/p7")
p("== p7 jobs")
files(C + "/p7/jobs")
p("== SRC " + SRC)
if not os.path.isfile(SRC):
    p("SRC MISSING")
else:
    raw = open(SRC, "rb").read()
    p("bytes %d sha256 %s" % (len(raw), sha(raw)))
    p("CRLF %d LF %d trailing_newline %s" % (raw.count(b"\r\n"), raw.count(b"\n"), raw.endswith(b"\n")))
    p("first 260: " + repr(raw[:260]))
    p("last 120: " + repr(raw[-120:]))
    g = json.loads(raw.decode("utf-8"))
    p("top-level type %s" % type(g).__name__)
    if isinstance(g, dict):
        p("top keys: %s" % json.dumps(list(g.keys())))
        nodes = g
        if "prompt" in g and isinstance(g["prompt"], dict):
            nodes = g["prompt"]
            p("wrapped prompt payload, prompt keys: %s" % json.dumps(list(g["prompt"].keys())))
        for k in sorted(nodes):
            n = nodes[k]
            if not isinstance(n, dict):
                p("  node %s not dict: %r" % (k, n))
                continue
            p("  node %-6s %-34s inputs=%s" % (k, n.get("class_type"), json.dumps(sorted(n.get("inputs", {}).keys()))))
        for k in sorted(nodes):
            n = nodes[k]
            if not isinstance(n, dict):
                continue
            for ik, iv in n.get("inputs", {}).items():
                if isinstance(iv, str) and len(iv) > 0:
                    tag = "STR"
                    if len(iv) > 60:
                        tag = "PROMPT-LEN-%d" % len(iv)
                    p("  str %s.%s %s sha256 %s head %r" % (k, ik, tag, sha(iv.encode()), iv[:70]))
        txt = json.dumps(g)
        for m in re.finditer(r"51080\d+", txt):
            p("seed-like %s at %d" % (m.group(0), m.start()))
        for k in sorted(nodes):
            n = nodes[k]
            if not isinstance(n, dict):
                continue
            ct = n.get("class_type")
            if ct in ("RandomNoise", "BasicScheduler", "BasicSampler", "KSampler", "SamplerCustom", "CustomSampler", "SaveVideo", "LoadImage", "MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo", "MiniMaxH3Extender", "MiniMaxH3PromptPackBridge", "MiniMaxH3MotionContextDiskFinalDecode", "ModelAttentionBackend", "BlockSparseAttention", "MiniMaxH3SigmaShift", "UNETLoader", "VAELoader", "CLIPLoader"):
                p("  detail %s %s %s" % (k, ct, json.dumps(n.get("inputs", {}))[:600]))
    # indentation probe
    for ind in (0, 1, 2, 4):
        for nl in ("\n", "\r\n"):
            s = json.dumps(g, indent=ind, ensure_ascii=True)
            cand = s.replace("\n", nl)
            if cand.encode("utf-8") == raw:
                p("EXACT FORMAT MATCH indent=%d newline=%r" % (ind, nl))
            if (cand + nl).encode("utf-8") == raw:
                p("EXACT FORMAT MATCH indent=%d newline=%r WITH trailing" % (ind, nl))
    seg = open(SRC.replace("seg3", "seg1"), "rb").read()
    p("seg1 api.json bytes %d sha256 %s" % (len(seg), sha(seg)))
    g1 = json.loads(seg.decode("utf-8"))
    p("seg1 nodes %s" % json.dumps(sorted(g1.keys())))
    p("seg3 nodes %s" % json.dumps(sorted(g.keys())))
    p("common %s" % json.dumps(sorted(set(g.keys()) & set(g1.keys()))))
    for k in sorted(set(g.keys()) & set(g1.keys())):
        a = json.dumps(g1[k], sort_keys=True)
        b = json.dumps(g[k], sort_keys=True)
        p("  node %s %s" % (k, "IDENTICAL" if a == b else "DIFFERS len %d vs %d" % (len(a), len(b))))
p("== SHA256SUMS.txt")
su = PROMPTS + "/SHA256SUMS.txt"
if os.path.isfile(su):
    b = open(su, "rb").read()
    p("bytes %d sha256 %s" % (len(b), sha(b)))
    for ln in b.decode("utf-8").splitlines():
        p("  " + ln)
for n in ("v2_seg3_c0_r2v.txt", "v2_seg3_c1_t2va.txt"):
    fp = PROMPTS + "/" + n
    b = open(fp, "rb").read()
    p("prompt %s bytes %d sha256 %s crlf %d trailing_nl %s" % (n, len(b), sha(b), b.count(b"\r\n"), b.endswith(b"\n")))
    p("  chars %d head %r tail %r" % (len(b.decode("utf-8")), b.decode("utf-8")[:120], b.decode("utf-8")[-120:]))
open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
print("REPORT " + OUT)
