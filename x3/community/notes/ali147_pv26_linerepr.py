import io
p = r"C:/Users/derek/5slock/ralph-community/TASKS.md"
raw = open(p, "rb").read()
lines = raw.split(b"\n")
for i, ln in enumerate(lines, 1):
    if b"PV2-6" in ln:
        print(i, len(ln))
        print(repr(ln[:120]))
        print("TAIL", repr(ln[-200:]))
