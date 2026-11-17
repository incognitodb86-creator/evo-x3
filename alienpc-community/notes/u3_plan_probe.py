import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
t = open(r"C:\AI\community\notes\2026-10-29-forge-cleanup-plan.md", encoding="utf-8-sig").read()
i = t.index("U3 Sydney")
print(t[i - 30:i + 2100])
print("=== reviews referenced by the chat-tone plan (T-1..T-6) ===")
import os
for base in (r"C:\AI\community\60_reviews\max", r"C:\AI\community"):
    for f in sorted(os.listdir(base)):
        if "chat-tone" in f or "pi-instructions-audit" in f:
            print(os.path.join(base, f))
