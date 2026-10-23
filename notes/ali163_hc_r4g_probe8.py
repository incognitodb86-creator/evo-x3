"""R4G probe 8: list the approved source folders for the 4 remaining picks (names + sizes only).
Read-only listing; no writes.
"""
import os

BASE = r"C:/Users/derek/Civitai_RightFlow_Flow_2026-10-19"
for folder in ("GROK_IMAGINE_2026-10-19b", "FLOW_BLONDE_DARK_PAIRS_2026-10-19"):
    d = os.path.join(BASE, folder)
    print("=" * 100)
    print("FOLDER", d, "exists", os.path.isdir(d))
    if not os.path.isdir(d):
        continue
    for n in sorted(os.listdir(d)):
        p = os.path.join(d, n)
        print("  %-46s %10d" % (n, os.path.getsize(p) if os.path.isfile(p) else -1))
