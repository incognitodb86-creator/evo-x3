"""R4G probe 6: structure of the existing R4F audit file (headings + size), and the F-list of the research note.
Read-only.
"""
p = r"C:/AI/community/notes/hc_prompt_face_audit_20261023.md"
t = open(p, encoding="utf-8").read()
lines = t.splitlines()
print("AUDIT bytes(utf8)=%d lines=%d" % (len(t.encode("utf-8")), len(lines)))
for i, l in enumerate(lines):
    if l.startswith("#"):
        print("%5d| %s" % (i + 1, l[:170]))
print("=" * 100)
print("last 12 lines of audit:")
for l in lines[-12:]:
    print("   ", l[:200])
print("=" * 100)
p2 = r"C:/AI/community/notes/hc_face_research_20261023.md"
t2 = open(p2, encoding="utf-8").read()
print("RESEARCH bytes=%d lines=%d" % (len(t2.encode("utf-8")), t2.count("\n") + 1))
print("headings:")
for i, l in enumerate(t2.splitlines()):
    if l.startswith("#"):
        print("%5d| %s" % (i + 1, l[:170]))
