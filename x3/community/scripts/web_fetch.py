#!/usr/bin/env python3
r"""HF2 (ALI-163, 2026-10-23): fetch a read-only web body and save it under an
extension that CANNOT trip the harness check.

Why this exists
---------------
Every iteration the harness runs `python -m json.tool` over EVERY file matching
C:/AI/community/notes/web/*.json.  A body that is not JSON saved with a .json
extension is a loop bomb: reddit.com/search.json answers 403 with an HTML body,
and proxy/mirror pages come back "Blocked" as HTML with HTTP 200.  On
2026-10-23 16:59:37 that stopped the loop
(CHECK FAIL: json.tool ...\notes\web\reddit_anatomy.json: Expecting value: line 1
column 1 (char 0) -> STOP_RALPH).

The rule this tool enforces
--------------------------
`<name>.json` is written ONLY when `json.loads()` accepts the bytes.  Anything
else lands as `<name>.html` (markup-looking body) or `<name>.txt`, and a
non-200 response is stamped in the name (`<name>.403.txt`, the pattern the
older `notes/web/if_*.404.txt` saves already used).  So a web save can never
again be a fake .json.

Usage
-----
  python C:/AI/community/scripts/web_fetch.py --url <url> --name <name>
      [--dir C:/AI/community/notes/web] [--ext auto|json|html|txt]
      [--timeout 30] [--force] [--print-body]

  python C:/AI/community/scripts/web_fetch.py --from notes/web/foo.json
      re-classify a body that is already on disk and re-save it under the right
      extension (renames the original away, so the *.json glob stops matching).

`--from` needs no network, which makes the whole rule testable offline
(scripts/tests/test_web_fetch.py).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_DIR = "C:/AI/community/notes/web"
UA = "Mozilla/5.0 (forge-community-ralph; read-only research fetch)"
KNOWN_EXT = ("json", "html", "htm", "txt", "md")


def http_get(url: str, timeout: float = 30.0) -> tuple[int, bytes]:
    """Return (status, body). Non-200 HTTP responses return their body too."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return int(r.status), r.read()
    except urllib.error.HTTPError as e:
        return int(e.code), e.read()


def decode(body: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return body.decode(enc)
        except UnicodeDecodeError:
            continue
    return body.decode("latin-1", "replace")


def is_json_text(text: str) -> bool:
    """True only when the standard-library parser accepts the whole body.

    This is the same parser the harness check runs (`python -m json.tool`),
    so a file this tool calls .json passes that check by construction.
    """
    try:
        json.loads(text)
    except Exception:
        return False
    return True


def is_html_text(text: str) -> bool:
    head = text[:2048].lstrip().lower()
    if head.startswith(("<!doctype html", "<html", "<?xml", "<svg", "<!ENTITY")):
        return True
    return head.startswith("<") and ("<html" in head or "<body" in head or "<div" in head)


def classify(status: int, body: bytes) -> tuple[str, str, str]:
    """(ext, name_suffix, reason). ext in {json, html, txt}."""
    text = decode(body)
    if not (200 <= int(status) < 300):
        return "txt", ".%s" % int(status), "HTTP %s is not a success body" % status
    if not text.strip():
        return "txt", ".empty", "empty body"
    if is_json_text(text):
        return "json", "", "json.loads accepted"
    if is_html_text(text):
        return "html", "", "body is markup, not JSON (json.tool would fail)"
    return "txt", "", "body is not JSON"


def split_name(name: str) -> str:
    """Strip a trailing known extension so callers can pass 'reddit_anatomy.json'."""
    base, ext = os.path.splitext(os.path.basename(name))
    if ext.lower().lstrip(".") in KNOWN_EXT:
        return base
    return os.path.basename(name)


def target_path(dirpath: str, name: str, ext: str, suffix: str = "") -> str:
    return os.path.join(dirpath, "%s%s.%s" % (split_name(name), suffix, ext))


def save(dirpath: str, name: str, body: bytes, status: int = 200,
         ext: str = "auto", force: bool = True) -> tuple[str, str]:
    """Save `body` under the safe extension. Returns (path, reason)."""
    cext, suffix, reason = classify(status, body)
    if ext != "auto":
        if ext == "json" and status in (200,) and not is_json_text(decode(body)):
            raise SystemExit("REFUSING to write .json: json.loads rejects the body "
                             "(that is exactly the HF2 loop bomb)")
        cext = "html" if ext in ("html", "htm") else ("txt" if ext == "txt" else "json")
        suffix = ""
    os.makedirs(dirpath, exist_ok=True)
    path = target_path(dirpath, name, cext, suffix)
    if os.path.exists(path) and not force:
        n = 2
        while os.path.exists(target_path(dirpath, name, cext, "%s-%d" % (suffix, n))):
            n += 1
        path = target_path(dirpath, name, cext, "%s-%d" % (suffix, n))
    with open(path, "wb") as f:
        f.write(body)
    return path, reason


def reclassify(dirpath: str, src: str, force: bool = True) -> tuple[str, str]:
    """Re-save a body that is already on disk under the correct extension."""
    with open(src, "rb") as f:
        body = f.read()
    stem = split_name(src)
    status = 200
    base, _, tail = stem.rpartition(".")
    if base and tail.isdigit() and len(tail) == 3:
        status, stem = int(tail), base
    path, reason = save(dirpath, stem, body, status=status, force=force)
    if os.path.abspath(path) != os.path.abspath(src):
        os.remove(src)
    return path, reason


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url")
    ap.add_argument("--name", help="file stem for the save (extension is chosen for you)")
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--ext", default="auto", choices=["auto", "json", "html", "htm", "txt"])
    ap.add_argument("--from", dest="frm", help="reclassify an existing saved body")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--force", action="store_true", help="overwrite an existing target")
    ap.add_argument("--print-body", action="store_true")
    a = ap.parse_args(argv)

    if a.frm:
        path, reason = reclassify(a.dir, a.frm, force=True)
        print("RECLASSIFIED %s -> %s (%s)" % (a.frm, path, reason))
        return 0

    if not a.url:
        ap.error("--url is required (or use --from to reclassify a saved body)")
    status, body = http_get(a.url, timeout=a.timeout)
    name = a.name or ("fetch_%d" % status)
    path, reason = save(a.dir, name, body, status=status, ext=a.ext, force=a.force)
    print("HTTP %s -> %s (%s, %d bytes)" % (status, path, reason, len(body)))
    if a.print_body:
        sys.stdout.write(decode(body)[:4000])
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
