#!/usr/bin/env python3
r"""ali07_merge_shadowed_lists.py - fix the SHADOW defect 0.2 shipped (fix_plan 0.2, 2026-10-26).

ali02_self_setup_rows_a.py / _b.py / _c.py each assign BLOCKED twice at module level, so the
FIRST list is bound and then thrown away: 36 blocked rows reach self_setup_20261023.md and 26
never do, while the builder's --check stays green. The builder now has an AST SHADOW detector
(ali02_self_setup_build.py:check_shadow) that fails on it; this script is the mechanical fix:

  - keep the FIRST BLOCKED list where it is (its leading comment stays),
  - append the later lists' ELEMENTS into it, element spans taken from the AST (the tuples are
    multi-line, so counting source lines is not counting entries),
  - delete the later assignments (element lines + their leading comment block),
  - drop exact duplicate elements (identical normalized element source),
  - print before/after element counts so the change is auditable.

Nothing between the two assignments is touched: ROWS / ROWS_SETTINGS / ROWS_HC and helper
functions live in the same files and must survive, so the edit is AST line-ranges, not a splice.
Dry run by default; --write to apply (then py_compile proves the result parses).
Idempotent: one BLOCKED assignment = untouched. Read/write only under C:/AI/community/notes.
"""
from __future__ import annotations

import ast
import io
import os
import py_compile
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ("ali02_self_setup_rows_a.py", "ali02_self_setup_rows_b.py", "ali02_self_setup_rows_c.py")


def blocked_assignments(src, name):
    tree = ast.parse(src, name)
    return [n for n in tree.body
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BLOCKED"
                                                 for t in n.targets)
            and isinstance(n.value, (ast.List, ast.Tuple))]


def leading_comment(lines, node):
    """Contiguous '#' lines directly above an assignment (provenance to preserve)."""
    i = node.lineno - 2
    out = []
    while i >= 0 and lines[i].lstrip().startswith("#"):
        out.insert(0, lines[i])
        i -= 1
    return out


def elts(node):
    return list(node.value.elts)


def span_src(lines, e):
    return [l.rstrip() for l in lines[e.lineno - 1:e.end_lineno]]


def key_of(src_lines):
    return " ".join(l.strip() for l in src_lines if l.strip()).rstrip(",").replace(" ", "")


def merge(path, write):
    name = os.path.basename(path)
    with io.open(path, encoding="utf-8", newline="") as f:
        src = f.read()
    nl = "\r\n" if "\r\n" in src else "\n"
    lines = src.split(nl)
    nodes = blocked_assignments(src, name)
    if len(nodes) < 2:
        print("%-32s 1 BLOCKED assignment - untouched" % name)
        return
    first, rest = nodes[0], nodes[1:]
    seen = {key_of(span_src(lines, e)) for e in elts(first)}
    add, dupes, discarded = [], 0, 0
    for n in rest:
        cmt = leading_comment(lines, n)
        block = []
        for e in elts(n):
            discarded += 1
            s = span_src(lines, e)
            if key_of(s) in seen:
                dupes += 1
                continue
            seen.add(key_of(s))
            block += s
        add += (["# " + c.lstrip().lstrip("#").strip() if c.strip().startswith("##") else c
                 for c in cmt] if cmt else []) + block
    out = list(lines)
    for n in rest:                                  # delete later assignments, descending
        cmt = leading_comment(lines, n)
        del out[n.lineno - 1 - len(cmt): n.value.end_lineno]
    close = first.value.end_lineno - 1
    if not out[close].strip().startswith("]"):
        print("%-32s MERGE ABORT: line %d is %r, expected the closing ']'"
              % (name, close + 1, out[close].strip()[:40]))
        return
    note = ["    # merged 2026-10-26 by notes/ali07_merge_shadowed_lists.py: the later BLOCKED",
            "    # assignment(s) shadowed these entries, so they never reached the deliverable",
            "    # while --check stayed green (builder check_shadow now fails on that)."]
    out[close:close] = note + add
    total = len(elts(first)) + discarded - dupes
    print("%-32s shadowed %d lists: live %d + discarded %d -> %d entries (dropped %d duplicate(s))"
          % (name, len(nodes), len(elts(first)), discarded, total, dupes))
    if write:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(nl.join(out))
        py_compile.compile(path, doraise=True)
        print("   written + py_compile ok")


def main() -> int:
    if "--write" not in sys.argv[1:]:
        print("dry run - pass --write to apply")
    for name in FILES:
        merge(os.path.join(HERE, name), "--write" in sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
