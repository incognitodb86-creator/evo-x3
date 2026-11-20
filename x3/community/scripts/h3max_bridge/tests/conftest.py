"""Locate shared parody validators (read-only) for h3max_bridge unit tests."""

from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve()
_CANDIDATES = [
    _HERE.parents[2] / "parody",  # x3/community/scripts/parody
    _HERE.parents[1] / "parody",
]
for parent in _HERE.parents:
    _CANDIDATES.append(parent / "x3" / "community" / "scripts" / "parody")
    _CANDIDATES.append(parent / "community" / "scripts" / "parody")

for cand in _CANDIDATES:
    if (cand / "beta7_convert.py").is_file():
        os.environ.setdefault("BETA7_CONVERT_DIR", str(cand))
        break
