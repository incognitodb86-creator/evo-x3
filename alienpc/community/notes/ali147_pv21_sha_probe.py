"""PV2-1 one-off probe: why does the LoadImage sha256 compare fail in the precheck?
Prints certutil-equivalent hashlib sha256 of the graph's LoadImage strings and a
character-level diff against the expected constant (no ';' in python -c, so a file).
Read-only. Run: python notes/ali147_pv21_sha_probe.py
"""
import hashlib
import json
import os

GRAPH = r"C:/AI/community/runs/ali147_pool_promptv2_s51080000/request.api.json"
COMFY_INPUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
EXPECT = "9cf9ff95f2d6f2fb3882219a8d98995b673e78a80001d7a41af1755cc918d075"

g = json.load(open(GRAPH, encoding="utf-8"))
for k, n in g.items():
    if n["class_type"] != "LoadImage":
        continue
    name = n["inputs"]["image"]
    path = os.path.normpath(os.path.join(COMFY_INPUT, name.replace("/", os.sep)))
    raw = open(path, "rb").read()
    d = hashlib.sha256(raw).hexdigest()
    print("node", k, "image", repr(name), "path", path)
    print("bytes", len(raw), "mode/format hint", raw[:8])
    print("digest", d, "len", len(d))
    print("expect", EXPECT, "len", len(EXPECT))
    print("equal", d == EXPECT)
    print("first_diff_index", next((i for i, (a, b) in enumerate(zip(d, EXPECT)) if a != b), None))
    for i, (a, b) in enumerate(zip(d, EXPECT)):
        if a != b:
            print("  at", i, "got", repr(a), "want", repr(b), "context got", d[max(0, i - 8):i + 8],
                  "want", EXPECT[max(0, i - 8):i + 8])
