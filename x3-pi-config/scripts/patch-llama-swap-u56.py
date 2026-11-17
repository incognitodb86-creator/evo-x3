#!/usr/bin/env python3
"""Targeted, idempotent patch of the live llama-swap.yaml (stdlib only, keeps comments and every other line).

Changes only:
  - flash-next-uncensored: concurrencyLimit -> 4, adds -e HALOGEN_VISION_TOWER=/models/qwen38-flash-next-vision.hgn if not already set,
    and adds useModelName + filters.setParamsByID "flash-next-uncensored-sub" (reasoning_effort: low), matching flash-next-sub.
  - joycaption, ref2va-27b: ttl -> 300 so ~26 GiB of GTT is released after 5 idle minutes.

Usage: patch-llama-swap-u56.py <in.yaml> <out.yaml>
Exit 0 = wrote out.yaml (possibly unchanged), 2 = refused (structure not as expected; edit by hand).
"""
import re
import sys

MODEL_RE = re.compile(r'^  "?([A-Za-z0-9_.-]+)"?:\s*(#.*)?$')


def blocks(lines):
    """Yield (name, start, end) for each model under the top-level models: key."""
    in_models = False
    cur = None
    for i, ln in enumerate(lines):
        if re.match(r"^models:\s*(#.*)?$", ln):
            in_models = True
            continue
        if in_models and ln.strip() and not ln.startswith(" ") and not ln.startswith("#"):
            if cur:
                yield cur[0], cur[1], i
                cur = None
            in_models = False
            continue
        if in_models:
            m = MODEL_RE.match(ln)
            if m:
                if cur:
                    yield cur[0], cur[1], i
                cur = (m.group(1), i)
    if cur:
        yield cur[0], cur[1], len(lines)


def find_block(lines, name):
    for n, s, e in blocks(lines):
        if n == name:
            return s, e
    return None


def set_scalar(lines, s, e, key, value):
    pat = re.compile(rf"^(    ){re.escape(key)}:\s*\S+(\s*#.*)?$")
    for i in range(s + 1, e):
        if pat.match(lines[i]):
            lines[i] = f"    {key}: {value}\n"
            return lines
    anchor = next((i for i in range(s + 1, e) if lines[i].startswith("    checkEndpoint:")), e)
    lines.insert(anchor, f"    {key}: {value}\n")
    return lines


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    lines = open(sys.argv[1], encoding="utf-8").read().splitlines(keepends=True)
    changes = []

    b = find_block(lines, "flash-next-uncensored")
    if not b:
        print("REFUSE: flash-next-uncensored block not found")
        return 2
    lines = set_scalar(lines, b[0], b[1], "concurrencyLimit", 4)
    changes.append("flash-next-uncensored.concurrencyLimit=4")
    s, e = find_block(lines, "flash-next-uncensored")
    body = "".join(lines[s:e])
    if "HALOGEN_VISION_TOWER=" not in body:
        ck_idx = next((i for i in range(s + 1, e) if "HALOGEN_CHECKPOINT=" in lines[i]), None)
        if ck_idx is not None:
            indent = re.match(r"^(\s*)", lines[ck_idx]).group(1)
            lines.insert(ck_idx + 1, f"{indent}-e HALOGEN_VISION_TOWER=/models/qwen38-flash-next-vision.hgn\n")
            changes.append("flash-next-uncensored.HALOGEN_VISION_TOWER=/models/qwen38-flash-next-vision.hgn")
            s, e = find_block(lines, "flash-next-uncensored")
            body = "".join(lines[s:e])
    if '"flash-next-uncensored-sub"' not in body:
        if re.search(r"^    filters:", body, re.M):
            print("REFUSE: flash-next-uncensored already has a filters: block; add flash-next-uncensored-sub by hand")
            return 2
        add = []
        if not re.search(r"^    useModelName:", body, re.M):
            add.append('    useModelName: "flash-next-uncensored"\n')
        add += [
            "    filters:\n",
            "      setParamsByID:\n",
            '        "flash-next-uncensored-sub":\n',
            "          reasoning_effort: low\n",
        ]
        anchor = next((i for i in range(s + 1, e) if lines[i].startswith("    checkEndpoint:")), e)
        lines[anchor:anchor] = add
        changes.append("flash-next-uncensored-sub alias added")

    for name in ("joycaption", "ref2va-27b"):
        b = find_block(lines, name)
        if not b:
            changes.append(f"{name}: not present, skipped")
            continue
        lines = set_scalar(lines, b[0], b[1], "ttl", 300)
        changes.append(f"{name}.ttl=300")

    open(sys.argv[2], "w", encoding="utf-8", newline="\n").write("".join(lines))
    print("PATCHED: " + "; ".join(changes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
