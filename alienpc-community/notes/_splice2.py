p = "C:/AI/community/notes/card_vl2_patch_base.py"
lines = open(p, encoding="utf-8").read().split("\n")
idx = [i for i, l in enumerate(lines) if l.rstrip().endswith("never shared.''')")]
assert len(idx) == 1, idx
lines[idx[0]] = lines[idx[0]].rstrip() + ")"
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
import py_compile
py_compile.compile(p, doraise=True)
print("fixed paren balance; the patch script compiles")
