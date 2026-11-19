"""MAX item 3 step 1: back up the handoff note before editing it (the .pi/.git rollback for a tracked file is
history, but the brief says back up before each edit, so a byte copy is written next to it).

Prints the sha8 of the backup and the live file so the close-out can prove the backup is the pre-edit bytes.
"""
import hashlib
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
SRC = r"C:\Users\derek\5slock\ralph-community\notes\2026-10-28-handoff-from-max.md"
BAK = SRC + ".bak-20261029-item3"
data = open(SRC, "rb").read()
if not __import__("os").path.exists(BAK):
    shutil.copy2(SRC, BAK)
print("backup %s (%d B, sha8=%s)" % (BAK, len(open(BAK, "rb").read()),
                                     hashlib.sha256(open(BAK, "rb").read()).hexdigest()[:8]))
print("live  %s (%d B, sha8=%s)" % (SRC, len(data), hashlib.sha256(data).hexdigest()[:8]))
print("backup matches the live pre-edit bytes:", hashlib.sha256(open(BAK, "rb").read()).digest()
      == hashlib.sha256(data).digest())
