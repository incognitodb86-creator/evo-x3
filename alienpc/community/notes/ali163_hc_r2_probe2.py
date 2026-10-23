"""R2 probe 2 (read-only): focused params for the face-lock relevant nodes."""
import hashlib
import json
import os

RUNS = r"C:\AI\community\runs"
GRAPHS = {
    "HC1": "ali147_pool_hc_c1_s51100001",
    "HC2": "ali147_pool_hc_c2_s51100002",
    "PV2": "ali147_pool_promptv2_s51080000",
    "RS4": "ali147_pool_refsheet_s51080000",
    "RS6": "ali147_pool_refsheet_b_s51080000",
}
NODES = ["img", "sheet", "c0", "c1", "win1", "app1", "tail1", "noise", "mkvid", "save"]
SKIP = ("prompt",)


def scal(v):
    if isinstance(v, str) and len(v) > 90:
        return "len=%d" % len(v)
    return v


for tag, d in GRAPHS.items():
    path = os.path.join(RUNS, d, "request.api.json")
    with open(path, "rb") as fh:
        g = json.loads(fh.read().decode("utf-8-sig"))
    print("=" * 76)
    print(tag, d)
    for nid in NODES:
        if nid not in g:
            continue
        n = g[nid]
        print("  %s  %s" % (nid, n["class_type"]))
        for k, v in sorted(n["inputs"].items()):
            if k == "prompt" or k.startswith("prompt_"):
                print("      %s = <<len %s>>" % (k, len(v) if isinstance(v, str) else v))
                continue
            print("      %s = %s" % (k, scal(v)))
    # prompt sha + presence of sound / subject lines
    for nid in ("c0", "c1"):
        for k, v in sorted(g[nid]["inputs"].items()):
            if (k == "prompt" or k.startswith("prompt_")) and isinstance(v, str):
                low = v.lower()
                print("      %s.%s len=%d sha=%s picture=%d subjectdef=%d sound=%d dyn=%d" % (
                    nid, k, len(v), hashlib.sha256(v.encode()).hexdigest()[:16], v.count("<Picture"),
                    low.count("subject_definitions"), low.count("overall_soundscape"), low.count("dynamic video")))
                for line in v.split("\n"):
                    s = line.strip()
                    if s.lower().startswith(("subject_definitions", "overall_soundscape", "non_diegetic_music", "summary")):
                        print("         | %s" % s[:260])
                print("         HEAD: %s" % v[:220].replace("\n", " "))
