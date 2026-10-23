"""BQ1d: scan ralph-community\TASKS.md line by line, CRLF-AWARE (2026-10-23 ~18:10 CT).

Lesson being fixed: my first gate scanned `text.split("\n")` and tested every char with
0 < ord < 32, so the trailing CR of every CRLF line looked like a control char = a FALSE fail.
A real defect = a control char (1-31) INSIDE the line text, i.e. after stripping that line's
own trailing CR. Reports the char code and the surrounding text; 0 hits = the file is clean.
Read-only. Usage: python notes/ali163_hc_bq1d_ctrlscan.py [path ...]
"""
import io
import sys

CR = chr(13)
paths = sys.argv[1:] or ["C:/Users/derek/5slock/ralph-community/TASKS.md"]
total = 0
for p in paths:
    raw = io.open(p, encoding="utf-8", newline="").read()
    crlf = raw.count(CR + "\n")
    lone = raw.count(CR) - crlf
    hits = []
    for i, line in enumerate(raw.split("\n")):
        body = line[:-1] if line.endswith(CR) else line
        for j, c in enumerate(body):
            if 0 < ord(c) < 32:
                hits.append((i + 1, j, ord(c), body[max(0, j - 40):j + 40]))
    total += len(hits) + lone
    print(p.replace("\\", "/"))
    print("  lines", raw.count("\n") + 1, "CRLF", crlf, "lone CR", lone,
          "control chars inside lines", len(hits))
    for h in hits[:8]:
        print(f"  line {h[0]} col {h[1]} ord {h[2]} ...{h[3]!r}")
print("TOTAL DEFECTS", total, "->", "CLEAN" if total == 0 else "NEEDS REPAIR")
raise SystemExit(0 if total == 0 else 1)
