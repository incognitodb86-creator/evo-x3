"""PV2-1 tick state check (read-only). Prints every open/blocked task line head in TASKS.md."""
import io

P = r"C:/Users/derek/5slock/ralph-community/TASKS.md"
lines = io.open(P, encoding="utf-8-sig").read().splitlines()
open_lines = [l for l in lines if l.startswith("- [ ]")]
block_lines = [l for l in lines if l.startswith("- [!]")]
done = [l for l in lines if l.startswith("- [x]")]
print("done %d  open %d  blocked %d" % (len(done), len(open_lines), len(block_lines)))
print("first open task:", open_lines[0][:120] if open_lines else "NONE -> COMPLETE")
for l in open_lines[1:]:
    print("  open:", l[:80])
for l in block_lines:
    print("  blocked:", l[:80])
pv2 = [l for l in lines if l.startswith("- [") and l.startswith("- [x] PV2-1")]
print("PV2-1 ticked:", bool(pv2))
