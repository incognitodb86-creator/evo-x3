r"""ali147_refsheet_b_rs5_dump_prompts.py - read-only helper for ALI-147 RS5 (REFSHEET_B, arm 5b).

Writes the two prompt strings of the REFSHEET (arm 5) graph out as plain text so they can be read in full, and prints
their sha256 + lengths. Reads: runs\ali147_pool_refsheet_s51080000\request.api.json. Writes: notes\*_prompt_c0.txt /
_prompt_c1.txt. No GPU, no network, no graph written.
"""
import hashlib
import json
import os

SRC = r"C:\AI\community\runs\ali147_pool_refsheet_s51080000\request.api.json"
OUT = r"C:\AI\community\notes"

g = json.load(open(SRC, encoding="utf-8"))
for node in ("c0", "c1"):
    p = g[node]["inputs"]["prompt"]
    dst = os.path.join(OUT, "ali147_refsheet_b_prompt_%s.txt" % node)
    open(dst, "w", encoding="utf-8", newline="\n").write(p)
    print("%s len=%d sha256=%s -> %s" % (node, len(p), hashlib.sha256(p.encode()).hexdigest(), dst))
print("ref_image_1 c0=%s c1=%s ref_image_size c0=%s c1=%s" % (
    g["c0"]["inputs"]["ref_images.ref_image_1"], g["c1"]["inputs"]["ref_images.ref_image_1"],
    g["c0"]["inputs"]["ref_image_size"], g["c1"]["inputs"]["ref_image_size"]))
print("sheet node=%s" % g["sheet"]["inputs"])
print("save prefix=%s" % g["save"]["inputs"]["filename_prefix"])
print("c0 length=%s c1 length=%s win1=%s" % (g["c0"]["inputs"]["length"], g["c1"]["inputs"]["length"],
                                             g["win1"]["inputs"]))
