"""ALI-163 R4 read-only post-write verification of the written request + graph."""
import json, os, hashlib, re

W = r"C:\AI\community"
ID = "ali147_pool_hc_r1_s51130001"
req_p = os.path.join(W, "p7", "JOB_REQUEST.json")
g_p = os.path.join(W, "runs", ID, "request.api.json")

d = open(req_p, "rb").read()
print("JOB_REQUEST", req_p, len(d), "bytes sha256", hashlib.sha256(d).hexdigest())
print("  crlf_only", d.count(b"\n") == d.count(b"\r\n"), "trailing_newline", d.endswith(b"\r\n"))
print("  parsed", json.loads(d))

d2 = open(g_p, "rb").read()
print("graph", g_p, len(d2), "bytes sha256", hashlib.sha256(d2).hexdigest())
print("  crlf_only", d2.count(b"\n") == d2.count(b"\r\n"), "trailing_newline", d2.endswith(b"\n"))
G = json.loads(d2.decode("utf-8").replace("\r\n", "\n"))
print("  nodes", len(G))
print("  noise", G["noise"]["inputs"], "save", G["save"]["inputs"]["filename_prefix"])
for nid in ("img", "sheet", "sheet2"):
    print(" ", nid, G[nid]["class_type"], G[nid]["inputs"])
for nid in ("c0", "c1"):
    i = G[nid]["inputs"]
    print(" ", nid, G[nid]["class_type"], i["width"], "x", i["height"], "len", i.get("length"),
          "ref_image_size", i["ref_image_size"], "ref_images", i["ref_images"], "prompt_chars", len(i["prompt"]))
print("  win1", G["win1"]["inputs"])
print("  mkvid fps", G["mkvid"]["inputs"].get("fps"), "tail1", G["tail1"]["inputs"])
print("  seed nodes", [k for k, v in G.items() if any("seed" in kk.lower() for kk in v["inputs"])])
print("  budget", json.load(open(r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json", encoding="utf-8")))
tasks = open(r"C:\Users\derek\5slock\ralph-community\TASKS.md", encoding="utf-8").read()
print("  R4 ticked", "[x] R4" in tasks, "| open lines", len(re.findall(r"^- \[ \]", tasks, flags=re.M)))
