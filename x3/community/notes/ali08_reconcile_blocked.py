#!/usr/bin/env python3
r"""ali08_reconcile_blocked.py - revive-and-validate the BLOCKED rows the SHADOW defect hid.

0.2's row modules each assigned BLOCKED twice, so 26 blocked entries were bound and thrown
away (notes/ali07_merge_shadowed_lists.py merged them). The revived entries had never been
checked, and 13 of them fail the builder's own rules: they pair a claim with a stamp written
by a DIFFERENT URL, cite a stamp whose URL is in no fetch manifest, use a 200 body as if it
were a refusal, or repeat a live row with a made-up URL (the manyfaces/llama-swap row is the
0.4 fabrication).

Rule, applied mechanically here: a blocked row is only as good as the fetch record behind it.
  - stamp must be on disk;
  - if the stamp's name is in a fetch manifest, the URL column is set to the manifest URL
    (same rule the fact rows already follow - the URL column is never typed by hand), and the
    claim is kept only when its host agrees with the manifest host, else dropped;
  - a stamp in no manifest = an orphan: dropped, and listed in the artifact as an orphan stamp;
  - a 200 body cited as the "stamp" becomes kind 'no-answer' (a body that fails to answer);
  - exact duplicates (same normalized claim + stamp) collapse to one.

Writes the kept rows back into each module's single BLOCKED list, prints the outcome table,
and saves the table to notes/ali07_blocked_reconcile_20261026.txt as the audit artifact.
Run the builder --check and --selftest right after: SHADOW must stay silent and no BLOCKED
problem may remain. Dry run by default; --write to apply.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ali02_self_setup_build as B  # noqa: E402  (reuse the manifest loader + STAMP regex)
import ali02_self_setup_rows_a as A  # noqa: E402
import ali02_self_setup_rows_b as Bm  # noqa: E402
import ali02_self_setup_rows_c as C  # noqa: E402

MODULES = {"a": A, "b": Bm, "c": C}
# Hand adjudication of the rows whose URL the reconciler rewrites (the stamp is the only
# fetch record, so the URL column follows the stamp). Mechanical host matching cannot tell
# "same site, different node" from "the claim's target", so each such row is judged by hand
# here and the reason is printed into the audit artifact. A revived claim is KEPT only when
# the stamp really records a fetch of the thing the claim is about.
DROP_LIST = [
    ("04y_reg_extender.404.txt", "modelscope", "the 404 records the video-lab-extender slug, not comfyui-modelscope-download: no fetch record for this claim"),
    ("04y_reg_extender.404.txt", "ComfyUI itself", "the 404 records the video-lab-extender slug, so it says nothing about the comfyui node's install count"),
    ("02v_hauhau_27b.401-10.txt", "Heretic", "the 401 records Qwen3.8-27B-Uncensored-Vision, a different repo: no fetch record for the Heretic card"),
    ("04x_hf_arcface_api.401-2.txt", "pyiqa", "the 401 records mirceaganghf/arcface, unrelated to the laion-aes/pyiqa numbers"),
    ("02v_minimax_disc28_page.401.txt", "MiniMaxAI", "the 401 records a MiniMax/H3-1031-AIO discussion, not MiniMaxAI/MiniMax-H3 discussion 28"),
    ("04y_reg_facecons.404.txt", "58 installs", "the fetched slug is a guess (comfyui-faceconsistency); the 58-installs figure has no record behind it"),
]
FILES = {k: os.path.join(HERE, "ali02_self_setup_rows_%s.py" % k) for k in MODULES}
ARTIFACT = os.path.join(HERE, "ali07_blocked_reconcile_20261026.txt")


def norm(s):
    return " ".join(str(s).split()).lower()


def host(url):
    return urlparse(url).netloc.lower().replace("www.", "")


def reconcile(man):
    rows, table = [], []
    for k, mod in MODULES.items():
        for e in mod.BLOCKED:
            claim, url, stamp = e[0], e[1], e[2]
            kind = e[3] if len(e) > 3 else "refused"
            rows.append((k, claim, url, stamp, kind))
    kept = {}
    for k, claim, url, stamp, kind in rows:
        base = os.path.basename(stamp)
        path = os.path.join(HERE, "web", base)
        nkey = (norm(claim), base)
        rec = (k, claim, url, stamp, kind)
        if not os.path.isfile(path):
            table.append(("DROP", "stamp not on disk", rec))
            continue
        got = man.get(base)
        if got is None:
            table.append(("DROP", "orphan stamp: no manifest URL wrote %s" % base, rec))
            continue
        if got != url:
            if host(got) != host(url):
                table.append(("DROP", "claim is about %s, the stamp records a fetch of %s"
                              % (host(url), host(got)), rec))
                continue
            url = got
            table.append(("REWRITE", "URL set to the manifest URL that wrote %s" % base, rec))
        if not B.STAMP.search(base):
            if kind == "refused":
                kind = "no-answer"
                table.append(("REWRITE", "%s is a 200 body, not a refusal: kind -> no-answer" % base, rec))
        rec = (k, claim, url, stamp, kind)
        drop = None
        for base2, sub, why in DROP_LIST:
            if base == base2 and sub.lower() in norm(claim):
                drop = why
                break
        if drop:
            table.append(("DROP", "hand: " + drop, rec))
            continue
        nkey2 = (norm(claim), norm(url), base)
        if nkey2 in kept:
            table.append(("DUPE", "same claim + URL + stamp after the rewrite", rec))
            continue
        kept[nkey2] = rec
    out = []
    for (nclaim, nurl, stamp), rec in kept.items():
        out.append(rec)
    return out, table


def render_list(entries):
    out = ["BLOCKED = ["]
    for _k, claim, url, stamp, kind in entries:
        out.append("    (%r," % claim)
        out.append("     %r," % url)
        out.append("     %r," % stamp)
        out.append("     %r)," % kind)
    out.append("]")
    return out


def main() -> int:
    write = "--write" in sys.argv[1:]
    man = B.load_manifest()
    kept, table = reconcile(man)
    lines = ["ali07_blocked_reconcile_20261026.txt - revive-and-validate of the shadowed BLOCKED lists",
             "input: %d entries (live + revived) -> kept %d" %
             (sum(len(m.BLOCKED) for m in MODULES.values()), len(kept)), ""]
    for act, why, rec in table:
        lines.append("%-8s %s | %s | %s | %s | %s" % (act, rec[0], rec[1][:60], rec[2][:60],
                                                       os.path.basename(rec[3]), why[:80]))
    lines += ["", "KEPT:"]
    for rec in sorted(kept, key=lambda r: (r[0], r[3])):
        lines.append("  %s  %-34s %s" % (rec[0], os.path.basename(rec[3]), rec[1][:64]))
    txt = "\n".join(lines) + "\n"
    print("\n".join(lines[:2]))
    for act, why, rec in table:
        print("%-8s %s | %s | %s" % (act, rec[0], os.path.basename(rec[3]), why[:78]))
    if write:
        with io.open(ARTIFACT, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        for k, path in FILES.items():
            with io.open(path, encoding="utf-8", newline="") as f:
                src = f.read()
            nl = "\r\n" if "\r\n" in src else "\n"
            lines2 = src.split(nl)
            starts = [i for i, l in enumerate(lines2) if l.startswith("BLOCKED = [")]
            if len(starts) != 1:
                print("ABORT %s: %d BLOCKED assignments - run ali07_merge first"
                      % (os.path.basename(path), len(starts)))
                return 1
            st = starts[0]
            en = next(i for i in range(st + 1, len(lines2)) if lines2[i].strip() == "]")
            mine = [r for r in kept if r[0] == k]
            head = lines2[:st]
            tail = lines2[en + 1:]
            body = ["# BLOCKED: sources this audit could not verify. ONE list only - see",
                    "# notes/ali07_blocked_reconcile_20261026.txt for what was dropped and why."] + \
                render_list(mine)
            with io.open(path, "w", encoding="utf-8", newline="") as f:
                f.write(nl.join(head + body + tail))
            import py_compile
            py_compile.compile(path, doraise=True)
            print("rewrote %s: %d blocked entries" % (os.path.basename(path), len(mine)))
        print("wrote %s" % ARTIFACT)
    else:
        print("dry run - pass --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
