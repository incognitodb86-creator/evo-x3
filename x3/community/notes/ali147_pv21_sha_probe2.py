"""PV2-1 one-off probe 2: compare the SHA literal in notes/ali147_pv21_precheck.py
against the real file hash, character by character. Read-only.
Run: python notes/ali147_pv21_sha_probe2.py
"""
import hashlib
import re

PRE = r"C:/AI/community/notes/ali147_pv21_precheck.py"
IMG = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/POOL_768x1344.png"

src = open(PRE, encoding="utf-8").read()
lits = re.findall(r'STILL_SHA = "([0-9a-f]+)"', src)
print("literals found in precheck", [(l, len(l)) for l in lits])
real = hashlib.sha256(open(IMG, "rb").read()).hexdigest()
print("real", real, len(real))
for l in lits:
    print("literal==real", l == real, "first_diff",
          next((i for i, (a, b) in enumerate(zip(l, real)) if a != b), None))
    for i, (a, b) in enumerate(zip(l, real)):
        if a != b:
            print("  idx", i, "literal", repr(a), repr(real[max(0, i - 6):i + 6]),
                  "file", repr(b))
