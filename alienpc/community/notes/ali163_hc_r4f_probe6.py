# ALI-163 R4F probe 6: shape of a submitted job file + its result (keys, graph location, LoadImage strings).
import json, os, gzip, base64, hashlib
JOBS = r"C:\AI\community\p7\jobs"
for jid in ["ali147_pool_hc_r1_s51130001", "ali147_pool_hc_sheet_s51120000"]:
    for suf in [".json", ".result.json"]:
        p = os.path.join(JOBS, jid + suf)
        print("\n==== %s  exists=%s size=%s" % (p, os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else None))
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        for k, v in d.items():
            s = json.dumps(v) if not isinstance(v, str) else v
            print("  key=%s type=%s len=%s head=%s" % (k, type(v).__name__, len(s), s[:160].replace("\n", " ")))
