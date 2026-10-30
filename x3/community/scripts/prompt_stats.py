"""Per-section and per-beat word counts for a REF2VA prompt file (post-write self-check:
the tested rule is 60-120 words per beat and a 350-500 word detailed_description)."""
import re, sys

t = open(sys.argv[1], encoding="utf-8").read()
secs = re.split(r"(?m)^(?=[a-z_]+:$)", t)
print("total words:", len([w for w in t.split() if w]))
for s in secs:
    if not s.strip():
        continue
    name = s.split(":", 1)[0].strip()
    print("  %-24s %5d words" % (name, len(s.split(":", 1)[1].split())))
for b in re.finditer(r"(?ms)BEAT ([A-Z]+),\s*([0-9.]+-[0-9.]+)s[^\n]*\n?:\s*(.*?)(?=\nBEAT [A-Z]+,|\nEnd the clip|$)", t):
    print("  BEAT %-5s %-10s %4d words" % (b.group(1), b.group(2), len(b.group(3).split())))
dd = [s for s in secs if s.startswith("detailed_description:")]
if dd:
    tail = len(re.split(r"(?ms)BEAT [A-Z]+,", dd[0])[-1].split())
    print("  trailing (post-last-beat) text:", tail, "words")
