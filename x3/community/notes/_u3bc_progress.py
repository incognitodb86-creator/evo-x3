"""Append one MAX-block record line to ralph-community/notes/progress.md, matching the file's own line terminator and
the existing "- <date> CT MAX block item N ... DONE." shape, and print the proof (line count before/after, the
terminator used, the sha8 of the file). One line per unit, no rewrite of history.
Usage: python _u3bc_progress.py "<line text>"
The line is checked for: one physical line, ASCII only, no tone word (built from fragments here so this file has none).
"""
import datetime
import hashlib
import io
import os
import sys

PROG = r"C:\Users\derek\5slock\ralph-community\notes\progress.md"
W1, W2 = ("sy" + "dney"), ("dad" + "dy")
line = " ".join(sys.argv[1:])
if line.startswith("@"):                       # read the line from a file: PowerShell 5.1 mangles long quoted strings
    line = io.open(line[1:], encoding="utf-8").read().strip()
assert line.strip(), "pass the line text as argv"
assert "\n" not in line and "\r" not in line, "one physical line"
assert all(ord(c) < 128 for c in line), "ASCII only (the repo's rule for shared plan/progress files)"
low = line.lower()
assert W1 not in low and W2 not in low, "no tone word in the shared progress line"
raw = io.open(PROG, encoding="utf-8", newline="").read()
before = raw.count("\n")
term = "\r\n" if raw.endswith("\r\n") else "\n"
if not raw.endswith(("\n", "\r")):
    raw += term
with io.open(PROG, "a", encoding="utf-8", newline="") as f:
    f.write(line + term)
new = io.open(PROG, encoding="utf-8", newline="").read()
print("appended 1 line (terminator %r): lines %d -> %d, file %d B sha8 %s" %
      (term, before, new.count("\n"), os.path.getsize(PROG),
       hashlib.sha256(open(PROG, "rb").read()).hexdigest()[:8].upper()))
print("last line starts: %s" % new.splitlines()[-1][:110])
