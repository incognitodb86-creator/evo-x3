#!/usr/bin/env python3
"""MEM1 2026-10-23: no-loss check for the AGENTS.md Learnings merge.

Every bullet line that existed in AGENTS.md before MEM1 must be present VERBATIM in
notes/forge-learnings.md (the append-only history). Anything missing gets appended there, then
re-read from disk and verified.

Self-destruct probes (loop 07 taught me that a check which cannot fail is worthless):
  P0 the extracted pre-MEM1 bullet count must be the real number (17 in this block) - a slicing
     bug in the first version of this script silently produced 0 bullets and printed OK;
  P1 a sentinel bullet that is not in the history MUST be reported missing;
  P2 after appending, the same line MUST be found.
"""
import io
import sys

PRE = "C:/AI/community/notes/AGENTS.md.pre-mem1-20261023"
HIST = "C:/AI/community/notes/forge-learnings.md"
TS = "2026-10-23T19:03"
TAG = "- MEM1 2026-10-23 (dropped from the AGENTS.md 15-line list by the merge, verbatim): "
SENTINEL = "MEM1 SENTINEL BULLET THAT IS NOT IN THE HISTORY 0x7E21"


def lines(p):
    return io.open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n").split("\n")


def pre_bullets():
    L = lines(PRE)
    idx = next(i for i, l in enumerate(L) if l.startswith("## Learnings"))
    return [l.strip() for l in L[idx + 1:] if l.strip().startswith("- ")]


def preserved(b, blob):
    """A pre-MEM1 bullet counts as kept if it is in the history verbatim, or as a line carrying the
    same text after the MEM1 dropped-from-AGENTS tag (the tag replaces the leading '- ')."""
    return b in blob or (TAG + b[2:]) in blob


def missing(bullets, blob):
    return [b for b in bullets if not preserved(b, blob)]


def main():
    bullets = pre_bullets()
    print(f"pre-MEM1 Learnings bullets: {len(bullets)}")
    if len(bullets) < 15:
        print("FAIL P0: extraction produced too few bullets - the slicing is broken, the check would be vacuous")
        return 1

    blob = "\n".join(lines(HIST))

    # P1: the missing-test must discriminate
    probe_list = bullets + ["- " + SENTINEL]
    miss = missing(probe_list, blob)
    if "- " + SENTINEL not in miss:
        print("FAIL P1: sentinel reported as FOUND - the missing-test never discriminates")
        return 1
    print("PROBE P1 OK: a line absent from the history is reported missing")

    real_missing = missing(bullets, blob)
    print(f"missing from history: {len(real_missing)} of {len(bullets)}")
    for m in real_missing:
        print("  MISSING:", m[:120])

    if real_missing:
        add = ["", f"## AGENTS.md Learnings bullets dropped by the MEM1 merge {TS} (verbatim, append-only)",
               "The merged <=15-line list is C:/Users/derek/5slock/AGENTS.md; these lines had no room in it, so the"]
        add += [TAG + b[2:] for b in real_missing]
        with io.open(HIST, "a", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(add) + "\n")
        print(f"appended {len(real_missing)} line(s) to {HIST}")

        blob2 = "\n".join(lines(HIST))
        still = [b for b in real_missing if not preserved(b, blob2)]
        if still:
            print("FAIL P2: appended lines not found on re-read:", [s[:60] for s in still])
            return 1
        print(f"PROBE P2 OK: all {len(real_missing)} appended line(s) verified on re-read from disk")

    left = missing(bullets, "\n".join(lines(HIST)))
    print(f"VERIFIED no-loss: {len(bullets) - len(left)}/{len(bullets)} pre-MEM1 bullets are verbatim in "
          f"{HIST}; remaining missing: {len(left)}")
    if left:
        for l in left:
            print("  STILL MISSING:", l[:120])
        return 1
    print("OK no-loss check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
