"""One-shot: keep the HERETIC-LABEL receipt's quoted row byte-identical to the plan.

The receipt's job is to carry the row's record. The row text lives in the sheet and is emitted verbatim,
and this pass edited it twice (the anchor sentence was false of the row that landed). Hand-copying the row
into the receipt is how drift starts, so this script pastes the row straight out of `fix_plan.md` between
the two markers the receipt carries, and prints a hash of what it wrote so the record is checkable.
"""
import hashlib
import io
import re

RC = "C:/Users/derek/5slock/ralph-community"
PLAN = RC + "/fix_plan.md"
RECEIPT = RC + "/notes/plans/receipts/HERETIC-LABEL-L164.md"
HEAD = "<!-- body verbatim from the emitted row -->"
TAIL = "\n\n## The fault, read off the file\n"

plan = io.open(PLAN, encoding="utf-8", newline="").read()
rows = [ln for ln in plan.split("\n") if "**HERETIC-LABEL**" in ln]
assert len(rows) == 1, "expected exactly one plan row, got %d" % len(rows)
row = rows[0].rstrip("\r")
assert row.startswith("- [x] **HERETIC-LABEL**"), "the plan row is not the ticked row: %r" % row[:40]
assert "CK-ATTN-L161.md" in row and "3.18 REFUSAL-TEST row" not in row, "the plan row is not the corrected text"

rcp = io.open(RECEIPT, encoding="utf-8", newline="").read()
i = rcp.index(HEAD) + len(HEAD)
j = rcp.index(TAIL)
new = rcp[:i] + "\n" + row + rcp[j:]
io.open(RECEIPT, "w", encoding="utf-8", newline="").write(new)
print("receipt body synced from fix_plan.md: %d B, sha256 %s" % (len(row), hashlib.sha256(row.encode()).hexdigest()[:16]))
