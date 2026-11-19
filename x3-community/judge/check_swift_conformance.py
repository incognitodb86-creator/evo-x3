"""One-off check for the 2026-10-29 Swift test note (not wired into anything): does every Swift answer conform to the
same schema the Qwen runs used? Reports per-record conformance, p_defect (logprobs) coverage, and answer-value counts."""
import json
from pathlib import Path

CHECKS = ["same_scene", "same_people", "start_kept", "target_reached", "anatomy_defect"]
ZCHECKS = ["same_scene", "anatomy_defect"]
BASE = Path(__file__).parent / "out"


def check_obj(o, checks):
    bad = []
    if set(o) != set(checks): bad.append(f"keys {sorted(set(o) ^ set(checks))}")
    for k in checks:
        v = o.get(k) or {}
        if set(v) != {"answer", "reason"}: bad.append(f"{k} fields {sorted(set(v) ^ {'answer', 'reason'})}")
        if v.get("answer") not in ("yes", "no"): bad.append(f"{k} answer={v.get('answer')!r}")
        if not isinstance(v.get("reason"), str) or len(v.get("reason", "")) > 200: bad.append(f"{k} reason len {len(v.get('reason', ''))}")
    return bad


for name, checks, nested in (("swift_a", CHECKS, False), ("swift_z/Z", ZCHECKS, True), ("vlm", CHECKS, False), ("audit2/Z", ZCHECKS, True)):
    d = BASE / name
    recs = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(d.glob("p15v2_*.json"))]
    probs = answers = calls = viol = 0
    for r in recs:
        blocks = [(pf.get("answers"), pf.get("p_defect"), pf.get("finish")) for pf in r.get("per_frame", [])] if nested else [(r.get("answers"), r.get("p_defect"), r.get("finish"))]
        for ans, pd, fin in blocks:
            calls += 1
            answers += len(ans or {})
            viol += len(check_obj(ans or {}, checks))
            probs += 1 if pd and len(pd) == len(checks) else 0
        if not nested and r.get("finish") not in ("stop",): print("  finish", r["tag"], r.get("finish"))
    print(f"{name:12s} records {len(recs):2d} calls {calls:3d} answers {answers:4d} schema violations {viol}  p_defect full coverage {probs}/{calls}  parse-direct {sum(1 for r in recs for b in ([r] if not nested else r.get('per_frame', [])) if b.get('parse') == 'direct')}/{calls}")
