#!/usr/bin/env python3
"""Presence check against the saved object_info dump (a LIST of node class names).
Usage: objinfo_has.py NodeA NodeB ...
Prints present/absent for each, plus any partial matches, so a 'not registered' claim is never
made from a fuzzy grep. Rebuild the dump with probe_nodes.py first if it is stale.
"""
import json
import sys

DUMP = r"C:\AI\community\notes\objinfo_20261028.json"
names = json.load(open(DUMP, encoding="utf-8"))
if isinstance(names, dict):
    names = list(names)
low = {str(n).lower(): n for n in names}
print(f"dump entries: {len(names)}")
for want in sys.argv[1:]:
    exact = want.lower() in low
    subs = [low[k] for k in low if want.lower() in k]
    print(f"{want:38} present_exact={exact} partial={subs[:6]}")
