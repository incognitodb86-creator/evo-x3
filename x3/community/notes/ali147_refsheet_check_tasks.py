import io
p = r"C:\Users\derek\5slock\ralph-community\TASKS.md"
lines = io.open(p, encoding="utf-8").read().split("\n")
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    if s.startswith("BLOCKED:") or s.startswith("- [") or s == "STOP_RALPH":
        head = s[:60]
        print("line %d len=%d %s" % (i, len(ln), head))
print("file_lines", len(lines))
