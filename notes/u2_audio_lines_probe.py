import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
t = open(r"C:\AI\community\skills\h3-prompting\SKILL.md", encoding="utf-8").read()
for b in re.findall(r"(?s)```.*?```", t):
    t = t.replace(b, "")
for i, l in enumerate(t.split("\n")):
    if "overall_soundscape" in l or "non_diegetic_music" in l:
        print("%3d %s" % (i + 1, ascii(l[:170])))
