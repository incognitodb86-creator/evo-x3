#!/usr/bin/env python3
"""Check which prompt marker substrings a file contains, on whitespace-normalized text."""
import sys
p = open(sys.argv[1], encoding="utf-8").read()
n = " ".join(p.split()).lower()
for m in sys.argv[2:]:
    print(("OK   " if m.lower() in n else "MISS "), m)
