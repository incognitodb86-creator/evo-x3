"""One-off: write the skill's supporting examples file with pure LF line endings.

Reason: the two p15 few-shots are copied out of a CRLF file (ralph-community's convention). The U2 check
verifies them byte-for-byte, so the copy is stored LF-normalized and the check normalizes the source the same
way. Content is unchanged - only line endings. Verified after writing: both fenced blocks present, CRLF count 0.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REF = Path(r"C:\AI\community\skills\h3-prompting\references\examples_archived.md")
raw = REF.read_bytes()
new = raw.replace(b"\r\n", b"\n")
REF.write_bytes(new)
print("bytes %d -> %d ; CRLF %d -> %d" % (len(raw), len(new), raw.count(b"\r\n"), new.count(b"\r\n")))

p15 = Path(r"C:\Users\derek\5slock\ralph-community\notes\p15_writer_skill.md").read_text(encoding="utf-8")
p15 = p15.replace("\r\n", "\n")
blocks = re.findall(r"```text\n(.*?)```", p15, flags=re.S)
t = REF.read_text(encoding="utf-8")
hit = [i + 1 for i, b in enumerate(blocks) if b.strip() in t]
heads = re.findall(r"(?m)^## Archived Example [AB] ", t)
print("p15 few-shots reproduced verbatim (LF-normalized) in the supporting file: %s of %d" % (hit, len(blocks)))
print("archived-example headings:", len(heads))
ok = len(hit) == len(blocks) == 2 and len(heads) == 2 and new.count(b"\r\n") == 0
print("VERDICT: %s" % ("OK" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
