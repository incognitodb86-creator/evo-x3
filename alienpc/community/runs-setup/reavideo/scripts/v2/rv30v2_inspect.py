"""Structural inspect of v2 manifest. Counts/categories only; no prompt prose."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

MANIFEST = Path(sys.argv[1])
BREAKDOWN = Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json")
man = json.loads(MANIFEST.read_text(encoding="utf-8"))
bd = json.loads(BREAKDOWN.read_text(encoding="utf-8"))
by_id = {s.get("id"): s for s in bd.get("shots") or []}
D_RE = re.compile(r"<d\b[^>]*>[\s\S]*?</d>", re.I)

def speech_n(shot: dict) -> int:
    sp = shot.get("speech") or {}
    raw = sp.get("lines") if isinstance(sp, dict) else shot.get("lines") or []
    n = 0
    for item in raw or []:
        if isinstance(item, dict) and str(item.get("text") or "").strip():
            n += 1
        elif isinstance(item, str) and item.strip():
            n += 1
    return n

out = {"clips": []}
# bind shot ids in requested order: clip 1 ~ 058, clip 2 ~ 029 when those were the only shots
shot_order = ["shot_058", "shot_029"]
for i, c in enumerate(man.get("clips") or []):
    prompt = c.get("prompt") or ""
    conv = c.get("conversion") or {}
    val = c.get("validation") or {}
    pre = c.get("writer_preflight")
    sid = shot_order[i] if i < len(shot_order) else None
    shot = by_id.get(sid) or {}
    s_lines = speech_n(shot)
    d_blocks = D_RE.findall(prompt)
    canned = "I'm right here" in prompt
    row = {
        "clip_index": c.get("clip_index"),
        "shot_id": sid,
        "frames": c.get("frames"),
        "duration_s": c.get("duration_s"),
        "validation_status": val.get("status"),
        "lint_ctx_passed": bool(conv.get("lint_ctx_passed") or (val.get("redacted") or {}).get("lint_ran")),
        "offline_fallback": bool(conv.get("offline_fallback") or c.get("offline_fallback")),
        "writer_preflight_codes": (pre or {}).get("codes") if isinstance(pre, dict) else None,
        "writer_preflight_policy_categories": (pre or {}).get("policy_word_categories") if isinstance(pre, dict) else None,
        "redacted_codes": (val.get("redacted") or {}).get("codes"),
        "speech_lines_n": s_lines,
        "d_count": len(d_blocks),
        "canned_fallback_line": canned,
        "invented_d_without_asr": bool(d_blocks) and s_lines == 0,
        "s1_count": len(re.findall(r"\(S1\)|<Subject\s+1>", prompt, flags=re.I)),
        "s2_count": len(re.findall(r"\(S2\)|<Subject\s+2>", prompt, flags=re.I)),
        "bind_report": conv.get("bind_report"),
        "bridge_gates": conv.get("bridge_gates") or val.get("bridge_gates"),
        "prompt_chars": len(prompt),
    }
    out["clips"].append(row)

out["all_ready"] = all(c["validation_status"] == "READY" and c.get("prompt_chars", 0) > 0 for c in out["clips"])
out["no_canned"] = all(not c["canned_fallback_line"] for c in out["clips"])
out["no_invented_d"] = all(not c["invented_d_without_asr"] for c in out["clips"])
out["lint_ctx_all"] = all(c["lint_ctx_passed"] for c in out["clips"])
print(json.dumps(out, indent=2))
# do not hard-fail inspect; caller decides
