"""U2 FIX pass (Max verify 10:29 CT): log START, make .bak-20261029-u2fix of every file about to be edited,
and move the intermediate SKILL.md snapshot out of the skill folder (a skill folder holds SKILL.md + references,
not loop snapshots).

Idempotent: refuses to overwrite an existing u2fix backup (the first one is the true pre-fix bytes) and skips a
move already done. Prints sizes so the later check can verify the backups by sha prefix.
"""
import datetime
import hashlib
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
SUF = ".bak-20261029-u2fix"

TARGETS = [
    r"C:\AI\community\skills\h3-prompting\SKILL.md",
    r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\SKILL.md",
    r"C:\Users\derek\.pi\agent\skills\alienpc-hardcore-i2v-director\references\max-i2v-prompt-improve-v1.md",
    r"C:\Users\derek\.pi\agent\skills\ref2va-prompt\SKILL.md",
    r"C:\Users\derek\.pi\agent\skills\h3-ref2va-prompt-chain\SKILL.md",
]
MID = r"C:\AI\community\skills\h3-prompting\SKILL.md.mid-20261029-u2-examples"
MID_NEW = r"C:\AI\community\notes\SKILL.md.mid-20261029-u2-examples"
LOG = r"C:\AI\community\notes\actions.log"

START = ("%s | U2 FIX START (MAX block item 1, after Max verify 10:29 CT FAIL in "
         "C:\\Users\\derek\\5slock\\ralph-community\\notes\\2026-10-29-max-U2-verify-FAIL.md) | fix list: director "
         "restatements L122-128/L56/L95-96/L63/L93, ref2va L21-25/L27, chain L62-68/L78, h3 R26 vs R7 + Example 2 "
         "R11 clause + R22/Example 1 positives + KB claim, move SKILL.md.mid snapshot to notes\\, tighten u2_check "
         "(references scan, drop block/history/nothing, key-phrase paraphrase catch, scripts-untouched) | file edits "
         "only, no GPU, no render, no model load, no queue" % NOW)
lines = [l for l in open(LOG, "rb").read().decode("utf-8").split("\r\n") if l.strip()]
if not any("U2 FIX START" in l for l in lines):
    open(LOG, "wb").write(("\r\n".join(lines + [START]) + "\r\n").encode("utf-8"))
    print("actions.log: FIX START appended")
else:
    print("actions.log: FIX START already present (idempotent)")

ok = True
for p in TARGETS:
    b = p + SUF
    if not os.path.exists(p):
        print("MISSING target:", p)
        ok = False
        continue
    data = open(p, "rb").read()
    if os.path.exists(b):
        print("exists (kept): %s %d B sha8=%s" % (os.path.basename(b), len(data),
                                                  hashlib.sha256(open(b, "rb").read()).hexdigest()[:8]))
        continue
    open(b, "wb").write(data)
    print("backup %s (%d B, sha8=%s)" % (b, len(data), hashlib.sha256(data).hexdigest()[:8]))

if os.path.exists(MID):
    shutil.move(MID, MID_NEW)
    print("moved mid snapshot: %s -> %s (%d B)" % (MID, MID_NEW, len(open(MID_NEW, "rb").read())))
elif os.path.exists(MID_NEW):
    print("mid snapshot already in notes\\ (idempotent): %d B" % len(open(MID_NEW, "rb").read()))
else:
    print("mid snapshot not found in either place", MID, MID_NEW)
    ok = False

print("VERDICT: %s" % ("READY" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
