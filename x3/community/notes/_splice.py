import io
p = "C:/AI/community/notes/card_vl2_patch_base.py"
lines = open(p, encoding="utf-8").read().split("\n")
assert lines[140].startswith("E.append(('''    add(f\"record:"), lines[140]
assert lines[142].endswith(")"), lines[142]
new = open("C:/AI/community/notes/_entry_record_line.txt", encoding="utf-8").read().rstrip("\n").split("\n")
lines[140:143] = new
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
import py_compile
py_compile.compile(p, doraise=True)
print("spliced and compiles")
