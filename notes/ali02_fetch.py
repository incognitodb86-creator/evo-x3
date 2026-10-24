#!/usr/bin/env python3
r"""Self-setup 0.2: fetch the PRIMARY sources behind the research notes.

Wraps scripts/web_fetch.py (which picks a check-safe extension) over the URL
list in ali02_sources.json. Idempotent: an existing save is skipped unless
--force. Prints name / http status / bytes so a 403/404 is visible in the log.
Read-only web (GET only), no GPU, no ComfyUI/llama-swap call.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

PY = sys.executable
FETCH = r"C:/AI/community/scripts/web_fetch.py"
SOURCES = r"C:/AI/community/notes/ali02_sources.json"
OUT = r"C:/AI/community/notes/web"


def load():
    return json.load(open(SOURCES, encoding="utf-8"))


def fetch_one(item, force):
    path = os.path.join(OUT, item["name"])
    ext = os.path.splitext(path)[1].lstrip(".")
    if os.path.exists(path) and not force:
        return (item["name"], "cached", os.path.getsize(path))
    # web_fetch chooses its own extension, so ask for the stem only
    stem = os.path.splitext(item["name"])[0]
    cmd = [PY, FETCH, "--url", item["url"], "--name", stem, "--dir", OUT]
    if force:
        cmd.append("--force")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    saved = []
    for cand in (stem + ".json", stem + ".html", stem + ".txt", stem + ".md"):
        if os.path.exists(os.path.join(OUT, cand)):
            saved.append((cand, os.path.getsize(os.path.join(OUT, cand))))
    out = (r.stdout or "").strip() + (r.stderr or "").strip()
    status = "?"
    for tok in ("200", "403", "404", "500", "502", "503"):
        if tok in out:
            status = tok
            break
    if saved:
        return (saved[0][0], status, saved[0][1])
    return (item["name"], "FAIL:" + status + " " + out[:120], 0)


def main():
    force = "--force" in sys.argv
    items = load()
    os.makedirs(OUT, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(lambda it: fetch_one(it, force), items))
    ok = sum(1 for n, s, b in rows if b > 0)
    for name, status, size in rows:
        print("  %-46s %-10s %10d" % (name, str(status), size))
    print("saved %d / %d" % (ok, len(rows)))
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
