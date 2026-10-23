"""R4G probe 4: the built-in MiniMaxH3ReferenceToVideo / ImageToVideo input contract
(autogrow ref_images) + how a dict-valued `ref_images` key behaves.
Read-only source inspection; no GPU, no ComfyUI call.
"""
import re

P = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/comfy_extras/nodes_minimax_h3.py"
L = open(P, encoding="utf-8").read().splitlines()
print("file lines", len(L))
cls = {}
for i, l in enumerate(L):
    m = re.match(r"^class (\w+)", l)
    if m:
        cls[m.group(1)] = i
print("classes:", sorted(cls.items(), key=lambda kv: kv[1]))

for name in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo"):
    if name not in cls:
        print("!! missing", name)
        continue
    a = cls[name]
    b = min([v for v in cls.values() if v > a] + [len(L)])
    print("=" * 110)
    print("CLASS", name, "lines", a + 1, "-", b, "(%d lines)" % (b - a))
    seg = L[a:b]
    for j, l in enumerate(seg):
        s = l.rstrip()
        if any(t in s for t in ("INPUT_TYPES", "ref_image", "ref_pack", "generation_mode", "Autogrow", "def ", "required", "optional", "io.", "RETURN", "OUTPUT", "min_items", "max_items", "prefix")):
            print("%5d| %s" % (a + j + 1, s[:200]))
