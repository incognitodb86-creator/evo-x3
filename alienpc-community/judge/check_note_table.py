"""One-off integrity check for the note table (test only): re-reads the note's markdown table and re-derives every
column from the JSON files, then reports any mismatch in answers, flag marks, flags named, or per-clip seconds."""
import json, re
from pathlib import Path

BASE = Path(__file__).parent / "out"
NOTE = Path(r"C:\AI\community\notes\2026-10-29-swift-judge-test.md")
CHECKS = ["same_scene", "same_people", "start_kept", "target_reached", "anatomy_defect"]
BAD = {"same_scene": "no", "same_people": "no", "start_kept": "no", "target_reached": "no", "anatomy_defect": "yes"}


def load(d):
    return {f.stem[len("p15v2_"):].replace("_s51170001_wf2", ""): json.loads(f.read_text(encoding="utf-8"))
            for f in sorted((BASE / d).glob("p15v2_*.json"))}


qa, sa, qz, sz = load("vlm"), load("swift_a"), load("audit2/Z"), load("swift_z/Z")


def pat(r):
    return "".join("F" if ((r.get("answers") or {}).get(k) or {}).get("answer") == BAD[k] else "." for k in CHECKS)


def zf(r):
    out = []
    for pf in r.get("per_frame", []):
        for k in ("same_scene", "anatomy_defect"):
            if ((pf.get("answers") or {}).get(k) or {}).get("answer") == BAD[k] and k not in out: out.append(k)
    return out


bad = []
rows = [l for l in NOTE.read_text(encoding="utf-8").splitlines() if l.startswith("| ") and l.count("|") >= 11]
seen = set()
for l in rows:
    c = [x.strip() for x in l.strip("|").split("|")]
    if not re.match(r"^[ab]_w\d", c[0]): continue
    seen.add(c[0])
    t = c[0]
    exp = [pat(qa[t]) + (" F" if qa[t].get("flags") else ""), pat(sa[t]) + (" F" if sa[t].get("flags") else ""),
           ("F " + ",".join(zf(qz[t])) if zf(qz[t]) else ""), ("F " + ",".join(zf(sz[t])) if zf(sz[t]) else ""),
           "F" if (qa[t].get("flags") or zf(qz[t])) else "", "F" if (sa[t].get("flags") or zf(sz[t])) else "",
           str(qa[t]["secs"]), str(sa[t]["secs"]), str(sz[t]["secs"])]
    got = [c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9]]
    for i, (e, g) in enumerate(zip(exp, got)):
        e = re.sub(r"\s*,\s*", ",", e).replace("F ", "F")
        g = re.sub(r"\s*,\s*", ",", g).replace("F ", "F")
        if e != g: bad.append(f"{t} col{i}: note={g!r} data={e!r}")
missing = (set(qa) | set(sa)) - seen
print("note table rows:", len(seen), " clips on disk:", len(set(qa) | set(sa)), " clips not in the note:", sorted(missing))
print("mismatches:", len(bad))
print("\n".join(bad[:20]))
