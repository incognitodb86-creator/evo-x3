
"""Take or clear the AlienPc one-line lease. Usage: rv30_lease.py take|clear"""
from __future__ import annotations
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

LEASE = Path(r"C:\AI\locks\alienpc-lease.txt")
LOCK = Path(r"C:\AI\locks\gpu-render.lock")

def now_ct() -> str:
    return datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %H:%M:%S CT")

cmd = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
LEASE.parent.mkdir(parents=True, exist_ok=True)
if cmd == "take":
    existing = LEASE.read_text(encoding="utf-8").strip() if LEASE.exists() else ""
    if existing:
        print("LEASE_BLOCKED", existing)
        raise SystemExit(3)
    if LOCK.exists():
        print("LOCK_PRESENT", LOCK.read_text(encoding="utf-8", errors="replace")[:200])
        raise SystemExit(3)
    line = f"Max | REA-Video hotel_vlm2 30s validation | {now_ct()}\n"
    LEASE.write_text(line, encoding="utf-8")
    print("LEASE_TAKEN", line.strip())
elif cmd == "clear":
    bak = LEASE.read_text(encoding="utf-8").strip() if LEASE.exists() else ""
    LEASE.write_text("", encoding="utf-8")
    print("LEASE_CLEARED", "bak=", bak)
else:
    print("usage: take|clear")
    raise SystemExit(2)
