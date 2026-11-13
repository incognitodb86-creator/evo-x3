#!/usr/bin/env python3
"""Check a compiled Render writer_prompt.md against the master rule list (stdlib only).

Usage: check_writer_prompt_rules.py <rules.json> <writer_prompt.md> [--quiet]

Per rule: PASS, MISSING (a check regex not found), FORBIDDEN (a forbidden phrase found),
or CONDENSED (warning: checks pass, but a detail_check is missing or the matched lines are
(lines hit by checks + detail_checks) are shorter than condensed_ratio x the canonical restore_text). Exit 1 on any hard MISSING/FORBIDDEN,
2 on bad input, else 0. Owner: Prompt maker (Render). Approved: Derrick t261u.
"""
import hashlib
import json
import re
import sys

FLAGS = re.I | re.M


def check(rule, text, lines, ratio):
    found = [f for f in rule.get("forbidden", []) if f.lower() in text.lower()]
    if found:
        return "FORBIDDEN", "found: " + " | ".join(repr(f) for f in found)
    missing = [c for c in rule.get("checks", []) if not re.search(c, text, FLAGS)]
    if missing:
        return "MISSING", "not found: " + " | ".join(repr(m) for m in missing)
    why = [d for d in rule.get("detail_checks", []) if not re.search(d, text, FLAGS)]
    if why:
        return "CONDENSED", "detail missing: " + " | ".join(repr(d) for d in why)
    if rule.get("checks"):
        pats = rule["checks"] + rule.get("detail_checks", [])
        hit = {i for i, ln in enumerate(lines) for c in pats if re.search(c, ln, FLAGS)}
        have = sum(len(lines[i].strip()) for i in hit)
        want = len(rule.get("restore_text", ""))
        if want and have < ratio * want:
            return "CONDENSED", f"section {have} chars < {int(ratio * 100)}% of canonical {want}"
    return "PASS", ""


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in argv
    if len(args) != 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        doc = json.load(open(args[0], encoding="utf-8"))
        raw = open(args[1], "rb").read()
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    text = raw.decode("utf-8").replace("\r\n", "\n")
    lines = text.split("\n")
    ratio = float(doc.get("condensed_ratio", 0.6))
    counts = {"PASS": 0, "CONDENSED": 0, "MISSING": 0, "FORBIDDEN": 0}
    hard_fail = []
    for r in doc["rules"]:
        if r.get("severity") == "retired":
            continue
        st, why = check(r, text, lines, ratio)
        counts[st] += 1
        sev = r.get("severity", "hard")
        if st in ("MISSING", "FORBIDDEN") and sev == "hard":
            hard_fail.append(r["id"])
        if not quiet or st != "PASS":
            tag = st if st != "CONDENSED" else "CONDENSED(warn)"
            print(f"{r['id']} {tag:<16} {sev:<4} {r['title']}" + (f"  [{why}]" if why else ""))
    sha = hashlib.sha256(raw).hexdigest()[:12]
    soft = counts["MISSING"] + counts["FORBIDDEN"] - len(hard_fail)
    print(f"SUMMARY rules={len(doc['rules'])} PASS={counts['PASS']} CONDENSED={counts['CONDENSED']} "
          f"MISSING={counts['MISSING']} FORBIDDEN={counts['FORBIDDEN']} hard_fail={len(hard_fail)} soft_fail={soft} "
          f"prompt_sha256={sha} result={'FAIL' if hard_fail else 'OK'}")
    if hard_fail:
        print("HARD FAIL: " + " ".join(hard_fail))
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
