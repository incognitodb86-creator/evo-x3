#!/usr/bin/env python3
"""Presence check against a saved ComfyUI object_info dump (a dict of node classes, or a LIST of class names).

Usage: objinfo_has.py [--dump <path>] [--json-out <path>] NodeA NodeB ...

--dump defaults to today's dump notes\\objinfo\\object_info_<YYYYMMDD>.json, falling back to the newest
object_info_*.json in that folder; --json-out writes the checked names as JSON so a test can consume them.
Prints present/absent for each name plus any partial matches, so a 'not registered' claim is never made from a
fuzzy grep. A dump is a saved GET of /object_info through the llama-swap comfyui route (the same route
run_graph_job.static_check uses); rebuild the index docs with notes\\objinfo\\_make_index.py <dump>."""
import argparse
import datetime
import glob
import json
import os
import sys

DIR = r"C:\AI\community\notes\objinfo"


def default_dump() -> str:
    """Today's dump if it exists, else the newest dated dump in the objinfo folder."""
    today = os.path.join(DIR, "object_info_%s.json" % datetime.date.today().strftime("%Y%m%d"))
    if os.path.exists(today):
        return today
    cands = sorted(glob.glob(os.path.join(DIR, "object_info_*.json")))
    return cands[-1] if cands else today


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dump", default=default_dump(), help="saved object_info dump (default: today's)")
    ap.add_argument("--json-out", default=None, help="also write the checked names as JSON here")
    ap.add_argument("names", nargs="*", help="node class names to check")
    ns = ap.parse_args()

    names = json.load(open(ns.dump, encoding="utf-8"))
    if isinstance(names, dict):
        names = list(names)
    low = {str(n).lower(): n for n in names}
    print(f"dump: {ns.dump}")
    print(f"dump entries: {len(names)}")
    results = []
    for want in ns.names:
        exact = want.lower() in low
        subs = [low[k] for k in low if want.lower() in k]
        print(f"{want:38} present_exact={exact} partial={subs[:6]}")
        results.append({"name": want, "present_exact": exact, "partial": subs})
    if ns.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(ns.json_out)), exist_ok=True)
        with open(ns.json_out, "w", encoding="utf-8") as fh:
            json.dump({"dump": ns.dump, "entries": len(names), "checked": results},
                      fh, indent=1, sort_keys=True)
        print(f"json-out: {ns.json_out}")
    return 0 if all(r["present_exact"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
