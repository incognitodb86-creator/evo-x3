"""R4G probe 2: how the built-in MiniMaxH3 nodes declare reference-image inputs and handle zero refs.
Read-only source inspection (no GPU, no ComfyUI call).
"""
import re

P = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/comfy_extras/nodes_minimax_h3.py"
L = open(P, encoding="utf-8").read().splitlines()
print("file", P, len(L), "lines")

cls = {}
for i, l in enumerate(L):
    m = re.match(r"^class (\w+)", l)
    if m:
        cls[m.group(1)] = i
print("classes:", {k: v + 1 for k, v in sorted(cls.items(), key=lambda kv: kv[1])})

for name in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo"):
    a = cls[name]
    b = min([v for v in cls.values() if v > a] + [len(L)])
    print("=" * 100)
    print("CLASS", name, "lines", a + 1, "-", b)
    seg = L[a:b]
    # print INPUT_TYPES block and every line mentioning ref_image / ref_pack / generation_mode
    for j, l in enumerate(seg):
        if "INPUT_TYPES" in l or "ref_image" in l or "ref_pack" in l or "generation_mode" in l or "Autogrow" in l or "def " in l or "required" in l or "optional" in l:
            print("%5d| %s" % (a + j + 1, l.rstrip()))

print("=" * 100)
print("all ref_image lines in file:")
for i, l in enumerate(L):
    if "ref_image" in l:
        print("%5d| %s" % (i + 1, l.rstrip()[:180]))
