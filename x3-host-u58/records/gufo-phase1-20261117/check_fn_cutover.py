#!/usr/bin/env python3
"""check_fn_cutover.py — exit 0 iff yaml-outside-FN is unchanged and X3 name/window checks pass.
Usage:
  python3 check_fn_cutover.py --yaml /etc/evo-x3/llama-swap.yaml \
      --backup /etc/evo-x3/llama-swap.yaml.bak-<fresh-stamp> \
      --json FILE [FILE ...]
Requires: Python 3, PyYAML (Fedora: python3-pyyaml), jq is not required.
"""
import argparse, json, re, sys, difflib
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Need PyYAML. On Fedora: sudo dnf install python3-pyyaml")

FN_KEYS = ("flash-next", "flash-next-uncensored")

def yaml_without_fn(path):
    d = yaml.safe_load(Path(path).read_text())
    models = d.get("models") or {}
    for k in FN_KEYS:
        models.pop(k, None)
    return yaml.safe_dump(d, sort_keys=True)

def flash_next_context(yaml_path):
    text = Path(yaml_path).read_text()
    # Official flash-next block: from the "flash-next": key to the next top-level model or EOF,
    # skipping flash-next-sub / flash-next-uncensored if they appear first as aliases inside.
    m = re.search(r'(?m)^  "flash-next":\s*\n', text)
    if not m:
        return None
    rest = text[m.end():]
    stop = re.search(r'(?m)^  "(?!flash-next-sub)[^"]+":\s*$', rest)
    block = rest[:stop.start()] if stop else rest
    cm = re.search(r'--context\s+(\d+)', block)
    return cm.group(1) if cm else None

def walk_models(obj, found):
    if isinstance(obj, dict):
        if "id" in obj and str(obj["id"]).startswith("flash-next"):
            found.append(obj)
        for v in obj.values():
            walk_models(v, found)
    elif isinstance(obj, list):
        for v in obj:
            walk_models(v, found)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--yaml", required=True)
    ap.add_argument("--backup", required=True)
    ap.add_argument("--json", nargs="*", default=[])
    ap.add_argument("--allow-rule8", action="store_true", help="U2: record RULE8 hits but do not fail; U5b must run without this flag")
    args = ap.parse_args()
    fail = 0

    a = yaml_without_fn(args.backup).splitlines(True)
    b = yaml_without_fn(args.yaml).splitlines(True)
    diff = list(difflib.unified_diff(a, b, fromfile="backup-without-fn", tofile="live-without-fn"))
    if diff:
        print("YAML_OUTSIDE_FN_DIFF")
        sys.stdout.writelines(diff)
        fail += 1
    else:
        print("YAML_OUTSIDE_FN_OK")

    ctx = flash_next_context(args.yaml)
    print(f"YAML_FLASH_NEXT_CONTEXT {ctx or 'MISSING'}")
    if not ctx:
        fail += 1

    for f in args.json:
        path = Path(f)
        if not path.is_file():
            print(f"ABSENT {f}")
            if f != "/home/evo/AI/render/.pi/agent/models.json":
                fail += 1
            continue
        data = json.loads(path.read_text())
        found = []
        walk_models(data, found)
        found.sort(key=lambda o: str(o.get("id")))
        print(f"FILE {f}")
        for o in found:
            i, w, n = o.get("id"), o.get("contextWindow"), o.get("name") or ""
            print(f"  {i} contextWindow={w} name={n}")
            if i in FN_KEYS and ctx and str(w) != str(ctx):
                print(f"  MISMATCH contextWindow {i} {w} != yaml {ctx}")
                fail += 1
            if re.search(r"halogen|\bhgn\b", n, re.I):
                print(f"  RULE8 display name still has Halogen/HGN: {i}")
                if not args.allow_rule8:
                    fail += 1
    print("RESULT", "FAIL" if fail else "PASS", f"fails={fail}")
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
