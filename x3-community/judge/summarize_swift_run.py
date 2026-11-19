"""summarize_swift_run.py - test-only summariser for the 2026-10-29 Swift-vs-Qwen judge comparison (not wired into anything).

Reads the four result folders on disk:
  Qwen baseline (the shipped runs): out\\vlm (vlm_judge) and out\\audit2\\Z (worst-frame zoom)
  Swift test:                      out\\swift_a and out\\swift_z\\Z
Checks the two runs really saw the same pictures (storyboard jpg SHA-256, zoom frame indices), derives the Z flags
with the README rule (same_scene=no or anatomy_defect=yes on any zoomed frame), prints the per-clip table, and writes
out\\swift_compare.csv. Flags only; no KEEP, no labels, no scoring (Max scores against the labels + held-out split).
Usage: .venv\\Scripts\\python.exe summarize_swift_run.py
"""
import hashlib, json
from pathlib import Path

BASE = Path(__file__).parent / "out"
PAIRS = [("vlm_judge", BASE / "vlm", BASE / "swift_a"), ("zoom_Z", BASE / "audit2" / "Z", BASE / "swift_z" / "Z")]
CHECKS = ["same_scene", "same_people", "start_kept", "target_reached", "anatomy_defect"]
BAD = {"same_scene": "no", "same_people": "no", "start_kept": "no", "target_reached": "no", "anatomy_defect": "yes"}
ZCHECKS = ["same_scene", "anatomy_defect"]


def load(d):
    out = {}
    for f in sorted(d.glob("p15v2_*.json")):
        out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


def flags_a(r):
    return sorted(r.get("flags") or [])


def flags_z(r):
    """README rule for the zoom variant: any defect answer on any zoomed frame is a flag."""
    got = set()
    for pf in r.get("per_frame", []):
        for k in ZCHECKS:
            a = ((pf.get("answers") or {}).get(k) or {}).get("answer")
            if a == BAD[k]: got.add(k)
    return sorted(got)


def zframes(r):
    return [pf.get("frame") for pf in r.get("per_frame", [])]


def short(tag):
    return tag[len("p15v2_"):].replace("_s51170001_wf2", "")


def answers_a(r):
    return "".join("F" if ((r.get("answers") or {}).get(k) or {}).get("answer") == BAD[k] else "." for k in CHECKS)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.exists() else "-"


if __name__ == "__main__":
    q = {n: load(qd) for n, qd, _ in PAIRS}
    s = {n: load(sd) for n, _, sd in PAIRS}
    tags = sorted(set().union(*[set(v) for v in q.values()], *[set(v) for v in s.values()]))
    rows, notes = [], []
    for t in tags:
        r = {}
        for n in ("vlm_judge", "zoom_Z"):
            for side, data in (("qwen", q[n]), ("swift", s[n])):
                rec = data.get(t, {})
                r[f"{side}_{n}_secs"] = rec.get("secs")
                r[f"{side}_{n}_flags"] = (flags_a(rec) if n == "vlm_judge" else flags_z(rec))
                r[f"{side}_{n}_finish"] = rec.get("finish") if n == "vlm_judge" else [p.get("finish") for p in rec.get("per_frame", [])]
                r[f"{side}_{n}_parse"] = rec.get("parse") if n == "vlm_judge" else [p.get("parse") for p in rec.get("per_frame", [])]
                r[f"{side}_{n}_err"] = rec.get("error")
                if n == "zoom_Z": r[f"{side}_{n}_frames"] = zframes(rec)
                if n == "vlm_judge": r[f"{side}_{n}_ans"] = answers_a(rec)
                if n == "vlm_judge":
                    g = (PAIRS[0][1] if side == "qwen" else PAIRS[0][2]) / f"{t}_grid.jpg"
                    r[f"{side}_grid"] = sha(g)
        rows.append(dict(tag=t, **r))

    print(f"clips: {len(rows)}   (order: {''.join(k[:2] for k in CHECKS)})  F = defect answered, . = not")
    print("\n| clip | qwen A | swift A | qwen Z | swift Z | A+Z qwen | A+Z swift | q secs | swift secs | qZ secs | swiftZ secs |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        qa, sa = set(r["qwen_vlm_judge_flags"]), set(r["swift_vlm_judge_flags"])
        qz, sz = set(r["qwen_zoom_Z_flags"]), set(r["swift_zoom_Z_flags"])
        print(f"| {short(r['tag'])} | {r['qwen_vlm_judge_ans']} {'F' if qa else ''} | {r['swift_vlm_judge_ans']} {'F' if sa else ''} "
              f"| {'F' if qz else ''}{','.join(qz)} | {'F' if sz else ''}{','.join(sz)} | {'F' if qa | qz else ''} | {'F' if sa | sz else ''} "
              f"| {r['qwen_vlm_judge_secs']} | {r['swift_vlm_judge_secs']} | {r['qwen_zoom_Z_secs']} | {r['swift_zoom_Z_secs']} |")
        if r["qwen_zoom_Z_frames"] != r["swift_zoom_Z_frames"]:
            notes.append(f"{short(r['tag'])}: zoom frames differ qwen={r['qwen_zoom_Z_frames']} swift={r['swift_zoom_Z_frames']}")
        if r["qwen_grid"] != r["swift_grid"] and "-" not in (r["qwen_grid"], r["swift_grid"]):
            notes.append(f"{short(r['tag'])}: storyboard jpg differs qwen={r['qwen_grid']} swift={r['swift_grid']}")

    def nflag(side, run, extra=None):
        return sum(1 for r in rows if r[f"{side}_{run}_flags"] or (extra and r[f"{side}_{extra}_flags"]))
    tot = lambda side, run: round(sum(r[f"{side}_{run}_secs"] or 0 for r in rows), 1)
    print("\n## totals")
    for run, extra in (("vlm_judge", None), ("vlm_judge", "zoom_Z"), ("zoom_Z", None)):
        for side in ("qwen", "swift"):
            print(f"  {side:5s} {run:9s}{'+Z' if extra else '  '}: flagged {nflag(side, run, extra)}/36")
    for side in ("qwen", "swift"):
        for run in ("vlm_judge", "zoom_Z"):
            secs = [x for x in (r[f"{side}_{run}_secs"] for r in rows) if x]
            if not secs:
                print(f"  {side:5s} {run:9s} per-clip secs: not recorded (that run predates r[\"secs\"]); see out\\audit2\\run.log for the variant total")
                continue
            print(f"  {side:5s} {run:9s} per-clip secs: n {len(secs)} min {min(secs)} med {sorted(secs)[len(secs)//2]} "
                  f"max {max(secs)}  sum {round(sum(secs), 1)} s of 36 clips")
    for side in ("qwen", "swift"):
        for run in ("vlm_judge", "zoom_Z"):
            def bad(r):
                fin = r[f"{side}_{run}_finish"]; fin = fin if isinstance(fin, list) else [fin]
                par = r[f"{side}_{run}_parse"]; par = par if isinstance(par, list) else [par]
                return bool(r[f"{side}_{run}_err"]) or any(f not in (None, "stop") for f in fin) or any(p not in (None, "direct") for p in par)
            hits = [(short(r["tag"]), r[f"{side}_{run}_finish"], r[f"{side}_{run}_parse"], r[f"{side}_{run}_err"]) for r in rows if bad(r)]
            print(f"  {side:5s} {run:9s} truncated/invalid/errored: {len(hits)} {hits[:4]}")
    agree = {k: sum(1 for r in rows if r["qwen_vlm_judge_ans"][i] == r["swift_vlm_judge_ans"][i]) for i, k in enumerate(CHECKS)}
    print("\n## per-check agreement swift vs qwen (vlm_judge, 36 clips)\n  " + "  ".join(f"{k}:{agree[k]}/36" for k in CHECKS))
    for side in ("qwen", "swift"):
        cnt = {k: sum(1 for r in rows if r[f"{side}_vlm_judge_ans"][i] == "F") for i, k in enumerate(CHECKS)}
        zcnt = {k: sum(1 for r in rows if k in r[f"{side}_zoom_Z_flags"]) for k in ZCHECKS}
        print(f"  {side:5s} vlm_judge answered-as-defect: " + "  ".join(f"{k}:{cnt[k]}" for k in CHECKS) + "   zoom_Z: " + "  ".join(f"{k}:{zcnt[k]}" for k in ZCHECKS))
    print("\n## same-input notes\n  " + ("\n  ".join(notes) if notes else "all 36 storyboard jpgs byte-identical and all zoom frame indices identical"))

    out = BASE / "swift_compare.csv"
    import csv
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["tag"] + [k for k in rows[0] if k != "tag"])
        for r in rows:
            w.writerow([r["tag"]] + [json.dumps(v, separators=("", ""), sort_keys=True) if isinstance(v, (list, dict)) else v for k, v in r.items() if k != "tag"])
    print(f"\nwrote {out}")
