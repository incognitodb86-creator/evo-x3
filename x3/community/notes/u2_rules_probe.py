import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


def norm_text(t):
    t = t.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", t).strip()


def parse_rules(text):
    blocks = re.findall(r"(?ms)^\*\*(R\d+) - (.*?)(?=\n\n\*\*R\d+ - |\n\n## |\Z)", text)
    return [(rid, norm_text(body)) for rid, body in blocks]


t = open(r"C:\AI\community\skills\h3-prompting\SKILL.md", encoding="utf-8").read()
p = parse_rules(t)
print("count", len(p))
print("ids", [r[0] for r in p])
d = dict(p)
print("keys in dict:", sorted(d.keys())[:40])
print("has R7:", "R7" in d, "| len R7 text:", len(d.get("R7", "")))
print("R7 head:", ascii(d.get("R7", "")[:200]))
