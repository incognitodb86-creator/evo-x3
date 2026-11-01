"""Place FLUX plan v3 in the brain and add the status line v2 needs (MF-6).

Forge, 2026-10-31 21:4x CT. Byte-precise: the brain files are UTF-8 (no BOM) with the bytes the
author used; this script reads bytes, changes only the named place, and re-reads to prove it.
Writes under C:/AI/fleet-brain are not allowed for the write/edit tool (policy), so this is the
brain-sync path AGENTS.md prescribes. No file is deleted.
"""
import glob
import os
import sys

SRC = r"C:\AI\community\plans\2026-10-31-2135-flux-full-replan-v3.md"
DST = r"C:\AI\fleet-brain\40_projects\flux2-overnight\plans\2026-10-31-flux-full-replan-v3.md"
V2 = r"C:\AI\fleet-brain\40_projects\flux2-overnight\plans\2026-10-30-flux-full-replan.md"
ANCHOR = "**Status 2026-10-31 1:27 AM CT (corrected):**"
NEW_PARA = (
    "\n**Status 2026-10-31 9:35 PM CT (Forge, on Derrick's ask \"Check gitea and the flux test plan "
    "double check it and update for community best and then execute all phases\"):** superseded for "
    "build order, gates and arm wiring by plans/2026-10-31-flux-full-replan-v3.md (lane copy "
    "C:\\AI\\community\\plans\\2026-10-31-2135-flux-full-replan-v3.md): that file records the verified "
    "per-phase state on the box, the machine-enforced gates (flux_phase_gate.py), S2 as the reference "
    "arm, new prompts and poses for Phases 3+ (the near-copy cause), one 12-job calibration of the four "
    "S2 settings that sit below the current community card values, the corrected Phase 6 download size "
    "(C13 331.4 MB + C15 165.7 MB + C16 79.7 MB = 0.58 GB, not 3.6 GB), and FLUX 3 Image Klein added "
    "to Phase 8's candidate list. This file stays the source of truth for the arm tables, the decision "
    "log and the KTD cards. Nothing is cut by v3.\n"
)

if not os.path.isfile(SRC):
    sys.exit("BLOCKER missing " + SRC)
data = open(SRC, "rb").read()
if b"\r\n" not in data:
    data = data.replace(b"\n", b"\r\n")  # match the brain's markdown convention
open(DST, "wb").write(data)
print("WROTE %s (%d bytes)" % (DST, len(open(DST, "rb").read())))

raw = open(V2, "rb").read().decode("utf-8")
if v3_marker := ("2026-10-31-flux-full-replan-v3.md" in raw):
    print("v2 already carries a v3 pointer, left untouched")
else:
    lines = raw.split("\r\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith(ANCHOR)]
    if len(idx) != 1:
        sys.exit("BLOCKER anchor count=%d in v2, expected 1" % len(idx))
    lines.insert(idx[0] + 1, NEW_PARA.strip("\r\n"))
    open(V2, "wb").write("\r\n".join(lines).encode("utf-8"))
    check = open(V2, "rb").read().decode("utf-8")
    assert "2026-10-31-flux-full-replan-v3.md" in check, "pointer missing after write"
    assert check.count(ANCHOR) == 1, "anchor count changed"
    print("v2 status line inserted after the 1:27 AM status paragraph; file %d bytes" % len(check.encode()))

# MF-6 asks for a status line on the klein9b-kv-bfs plan too; find it by name if it exists.
cands = glob.glob(r"C:\AI\fleet-brain\40_projects\**\*kv*bfs*", recursive=True) + \
        glob.glob(r"C:\AI\fleet-brain\40_projects\**\*kv-bfs*", recursive=True)
print("kv-bfs plan candidates: %s" % (cands or "none in the brain (not touched)"))
