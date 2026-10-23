"""R2 probe 3 (read-only): <Picture N> labels vs supplied reference slots, prompt
lengths vs the v2 spec files, and the reference-slot inventory per graph."""
import glob
import hashlib
import json
import os
import re

RUNS = r"C:\AI\community\runs"
SPEC = r"C:\AI\community\specs\prompt_v2"
GRAPHS = {
    "HC1": "ali147_pool_hc_c1_s51100001",
    "HC2": "ali147_pool_hc_c2_s51100002",
    "PV2": "ali147_pool_promptv2_s51080000",
    "RS4": "ali147_pool_refsheet_s51080000",
    "RS6": "ali147_pool_refsheet_b_s51080000",
}

print("== v2 spec prompt file sizes ==")
for f in sorted(glob.glob(os.path.join(SPEC, "*.txt"))):
    raw = open(f, "rb").read()
    txt = raw.decode("utf-8-sig", "replace")
    print("%-46s bytes=%-6d chars=%-6d pictures=%s" % (
        os.path.basename(f), len(raw), len(txt.rstrip("\r\n")),
        sorted(set(re.findall(r"<Picture\s*\d+>", txt)))))

print()
print("== graphs: reference slots vs <Picture N> labels ==")
for tag, d in GRAPHS.items():
    g = json.loads(open(os.path.join(RUNS, d, "request.api.json"), "rb").read().decode("utf-8-sig"))
    slots = {}
    for nid, n in g.items():
        refs = {k: v for k, v in n["inputs"].items() if k.startswith("ref_images.")}
        if refs:
            slots[nid] = (sorted(refs), [r[0] for r in refs.values()], n["inputs"].get("ref_image_size"))
    print("--", tag, d)
    print("   ref slots:", slots)
    for nid in ("c0", "c1"):
        p = g[nid]["inputs"]["prompt"]
        labels = sorted(set(re.findall(r"<Picture\s*\d+>", p)), key=lambda s: int(re.search(r"\d+", s).group()))
        subs = sorted(set(re.findall(r"<Subject\s*\d+>", p)), key=lambda s: int(re.search(r"\d+", s).group()))
        nrefs = len(slots.get(nid, ([], [], None))[0])
        dangling = [l for l in labels if int(re.search(r"\d+", l).group()) > nrefs]
        print("   %s len=%d sha=%s refs=%d labels=%s dangling=%s subjects=%s" % (
            nid, len(p), hashlib.sha256(p.encode()).hexdigest()[:12], nrefs, labels, dangling, subs))
        sd = p.split("summary:")[0]
        print("      subject_definitions block: %d chars, %d <Picture>, %d <Subject>" % (
            len(sd), len(re.findall(r"<Picture\s*\d+>", sd)), len(re.findall(r"<Subject\s*\d+>", sd))))
        for line in sd.split("\n"):
            s = line.strip()
            if s.startswith("<Subject"):
                print("        %s" % s[:300])
