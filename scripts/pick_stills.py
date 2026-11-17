#!/usr/bin/env python3
"""Batch still picker for the render lane (PixlStash API, one call for a whole batch).

Community way: same PixlStash endpoints and fields as the per-clip curl in
render AGENTS.md step 1; adapted to fire every query concurrently so the
chat pays one model round-trip instead of one per search (render-chat audit,
2026-11-16: 7 serial searches cost ~6 min at ~7 tok/s decode).

Usage:
  pick_stills.py --search "woman sundress beach sunset" --search "two women couch" \
                 --character FCSydny --character FCMegan [--limit 5]
Output: one JSON line per query:
  {"query": ..., "kind": "search|character", "candidates": [{id,file_path,width,height},...]}
Only these four fields are printed (AGENTS.md: no captions, no browsing contents).
Key comes from $PIXL_KEY env; never printed.
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "http://127.0.0.1:9537"
CHARACTER_IDS = {"FCSydny": 1, "FCMegan": 2}  # AGENTS.md step 1
FIELDS = ("id", "file_path", "width", "height")


def fetch(url: str, key: str, timeout: float):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def run_query(kind: str, value: str, limit: int, key: str, timeout: float):
    if kind == "search":
        url = f"{API}/api/v1/pictures/search?{urllib.parse.urlencode({'query': value, 'limit': limit})}"
    else:
        url = f"{API}/api/v1/pictures?{urllib.parse.urlencode({'character_id': value, 'limit': limit, 'offset': 0})}"
    try:
        rows = fetch(url, key, timeout)
        cands = [{f: r.get(f) for f in FIELDS} for r in rows]
        return {"query": value, "kind": kind, "candidates": cands}
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        return {"query": value, "kind": kind, "error": f"{type(e).__name__}: {e}"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--search", action="append", default=[], metavar="WORDS",
                    help="semantic scene search, repeat once per clip (short scene words)")
    ap.add_argument("--character", action="append", default=[], metavar="NAME_OR_ID",
                    help="character name (FCSydny, FCMegan) or numeric character_id, repeatable")
    ap.add_argument("--limit", type=int, default=5, help="candidates per query (default 5)")
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    key = os.environ.get("PIXL_KEY")
    if not key:
        print("error: PIXL_KEY not in env", file=sys.stderr)
        return 2
    if not args.search and not args.character:
        ap.print_usage(sys.stderr)
        print("error: pass at least one --search or --character", file=sys.stderr)
        return 2

    jobs = [("search", q) for q in args.search]
    for c in args.character:
        cid = CHARACTER_IDS.get(c, c)
        jobs.append(("character", str(cid)))

    results = []
    with cf.ThreadPoolExecutor(max_workers=min(8, len(jobs))) as ex:
        futs = [ex.submit(run_query, kind, val, args.limit, key, args.timeout) for kind, val in jobs]
        for f in cf.as_completed(futs):
            results.append(f.result())

    # keep input order
    order = {(k, str(v)): i for i, (k, v) in enumerate(jobs)}
    results.sort(key=lambda r: order.get((r["kind"], r["query"]), 99))
    failed = 0
    for r in results:
        if "error" in r:
            failed += 1
        print(json.dumps(r, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
