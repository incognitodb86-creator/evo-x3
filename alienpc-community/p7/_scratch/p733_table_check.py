import re
p = r"C:\AI\community\runs\P7_LEADERBOARD.md"
lines = open(p, encoding="utf-8").read().split("\n")
# find the History table header to learn the column count
hdr_i, sep_i, ncols = None, None, None
for i, l in enumerate(lines):
    if l.strip().startswith("| round | slot | job id"):
        hdr_i = i
        ncols = len(l.rstrip().split("|")) - 2
        sep_i = i + 1
        break
print("header line", hdr_i + 1, "cols", ncols)
bad = 0
i = sep_i + 1
while i < len(lines) and lines[i].lstrip().startswith("|"):
    cells = len(lines[i].rstrip().split("|")) - 2
    if cells != ncols:
        bad += 1
        print("BAD", i + 1, "cells", cells, lines[i][:90])
    i += 1
print("history rows checked:", i - sep_i - 1, "bad:", bad)
