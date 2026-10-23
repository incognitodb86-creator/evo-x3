#!/usr/bin/env python3
r"""HF2 pre-check: sweep C:/AI/community/notes/web for *.json files that
`python -m json.tool` would reject, i.e. the exact condition that stops the Ralph
loop (CHECK FAIL -> STOP_RALPH, 2026-10-23 16:59:37 on notes\web\reddit_anatomy.json).

Run it BEFORE ending a research pass:

  python C:/AI/community/scripts/check_web_saves.py            # exit 0 = clean, 1 = offenders
  python C:/AI/community/scripts/check_web_saves.py --fix      # rename offenders to .html/.txt
  python C:/AI/community/scripts/check_web_saves.py --fix --dry

The renamer is collision-safe and never touches non-.json files. The detector is
proven non-vacuous in scripts/tests/test_web_fetch.py (it MUST fire on a planted
non-JSON .json, and must stay silent on a valid one - a green check that cannot
fail is worthless).
"""

from __future__ import annotations

import argparse
import json
import os

DEFAULT_DIR = "C:/AI/community/notes/web"


def json_ok(path: str) -> bool:
    """Same acceptance test as the harness check: json.load over the whole file."""
    try:
        with open(path, "rb") as f:
            json.load(f)
    except Exception:
        return False
    return True


def sweep(dirpath: str) -> list[str]:
    if not os.path.isdir(dirpath):
        return []
    return sorted(p for p in (os.path.join(dirpath, n) for n in os.listdir(dirpath))
                  if p.lower().endswith(".json") and not json_ok(p))


def looks_html(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(2048).decode("utf-8", "replace").lstrip().lower()
    except OSError:
        return False
    return head.startswith(("<!doctype html", "<html", "<?xml", "<svg")) or (
        head.startswith("<") and ("<html" in head or "<body" in head or "<div" in head))


def fix(dirpath: str, dry: bool = False) -> list[str]:
    moved = []
    for path in sweep(dirpath):
        ext = ".html" if looks_html(path) else ".txt"
        base = os.path.splitext(path)[0]
        dst = base + ext
        n = 2
        while os.path.exists(dst):
            dst = "%s-%d%s" % (base, n, ext)
            n += 1
        moved.append("%s -> %s" % (path, dst))
        if not dry:
            os.rename(path, dst)
    return moved


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--fix", action="store_true", help="rename offenders out of the *.json glob")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)

    bad = sweep(a.dir)
    if not bad:
        n_json = sum(1 for n in os.listdir(a.dir) if n.lower().endswith(".json")) if os.path.isdir(a.dir) else 0
        print("CLEAN: %s - every *.json parses (json.tool-safe), %d checked" % (a.dir, n_json))
        return 0
    print("BAD: %d *.json file(s) in %s fail json.tool:" % (len(bad), a.dir))
    for p in bad:
        print("  BAD %s" % p)
    if a.fix:
        for line in fix(a.dir, dry=a.dry):
            print("  %s" % line)
        left = sweep(a.dir)
        print("AFTER FIX: %d remaining" % len(left))
        return 0 if not left else 1
    print("FIX: python C:/AI/community/scripts/check_web_saves.py --fix   (or save web bodies "
          "with scripts/web_fetch.py, which picks the extension from the body)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
