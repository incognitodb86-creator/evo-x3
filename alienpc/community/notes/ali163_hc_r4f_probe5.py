# ALI-163 R4F probe 5: authoritative input inventory for the four rendered HC clips.
# The submitted graph bytes live inside C:\AI\community\p7\jobs\<id>.job_request.json (field "submitted_graph"),
# so the LoadImage strings are recoverable even though notes/*submitted_graph.pretty.json copies are gone
# (ComfyUI input + output trees were reorganised 16:25-16:57 CT 2026-10-23: the *_sheet2_* pngs and the
# Hardcore10/11_start.png stills referenced by the r1/r2 graphs are no longer on disk).
import json, os, hashlib

JOBS = r"C:\AI\community\p7\jobs"
IDS = ["ali147_pool_hc_r1_s51130001", "ali147_pool_hc_r2_s51130002",
       "ali147_pool_hc_c1_s51100001", "ali147_pool_hc_c2_s51100002",
       "ali147_pool_hc_r1", "ali147_pool_hc_r2"]
INP = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input"

for jid in IDS:
    p = os.path.join(JOBS, jid + ".job_request.json")
    r = os.path.join(JOBS, jid + ".result.json")
    if not os.path.exists(p):
        print("\n%s  NO job_request" % jid)
        continue
    d = json.load(open(p, encoding="utf-8"))
    g = d.get("submitted_graph")
    if isinstance(g, str):
        g = json.loads(g)
    print("\n== %s" % jid)
    print("  api=%s prompt_id=%s" % (d.get("api"), d.get("prompt_id")))
    if g:
        for nid, nd in sorted(g.items(), key=lambda kv: int(kv[0])):
            t = nd.get("class_type")
            if t in ("LoadImage", "LoadImageMask", "LoadVideo"):
                s = nd["inputs"].get("image")
                exists = os.path.exists(os.path.join(INP, str(s).replace("/", "\\"))) if s else None
                print("  node %s %s image=%s  on_disk=%s" % (nid, t, s, exists))
            if t == "WanImageToVideo":
                print("  node %s WanImageToVideo length=%s" % (nid, nd["inputs"].get("length")))
            if t == "MiniMaxH3ReferenceToVideo" or t == "MiniMaxH3ImageToVideo":
                print("  node %s %s seed=%s" % (nid, t, nd["inputs"].get("seed")))
        h = hashlib.sha256(json.dumps(g, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        print("  canonical sha256 (separators ,:) =", h)
    if os.path.exists(r):
        rr = json.load(open(r, encoding="utf-8"))
        print("  result ok=%s status=%s sha256=%s dur_s=%s err=%s" %
              (rr.get("ok"), rr.get("status"), rr.get("sha256"), rr.get("dur_s"), str(rr.get("error"))[:60]))
        if rr.get("submitted_graph_sha256"):
            print("  result submitted_graph_sha256 =", rr["submitted_graph_sha256"])
