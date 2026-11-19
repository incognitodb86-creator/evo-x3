import io
p = r"C:\Users\derek\5slock\AGENTS.md"
raw = io.open(p, encoding="utf-8").read()
lines = raw.split("\n")
print("parts", len(lines), "endswith_newline", raw.endswith("\n"))
for i, ln in enumerate(lines, 1):
    print(i, len(ln), repr(ln[:45]))
