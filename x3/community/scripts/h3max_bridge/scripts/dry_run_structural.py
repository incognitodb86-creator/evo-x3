#!/usr/bin/env python3
"""Structural dry-run for h3max_bridge (counts/flags only; no prompt or VLM prose)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Allow running from a tools/ checkout
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Structural dry-run (counts/flags only).")
    ap.add_argument("breakdown", type=Path)
    ap.add_argument("--shots", default="shot_058,shot_029")
    ap.add_argument("--refmod", action="append", default=[])
    ap.add_argument("--max-frames", type=int, default=362)
    args = ap.parse_args(argv)

    from h3max_bridge import (
        compile_prompt_offline,
        filter_shots,
        normalize_breakdown,
        pack_shots,
        parse_refmods,
        parse_shot_ids,
        slice_long_shots,
    )
    from h3max_bridge.gates import structural_report

    breakdown = json.loads(args.breakdown.read_text(encoding="utf-8"))
    ids = parse_shot_ids(args.shots)
    selected = filter_shots(breakdown, ids)
    selected = slice_long_shots(selected, max_frames=args.max_frames, mode="start")
    selected = normalize_breakdown(selected)
    refs = parse_refmods(args.refmod or ["Alice=alice_v.safetensors", "Adam Jensen=adam_v.safetensors", "Alice=alice_voice_audio.safetensors"])
    by_id = {str(s.get("id")): s for s in selected["shots"]}
    reports = []
    for sid in ids:
        shot = by_id.get(sid)
        if shot is None:
            reports.append({"shot_id": sid, "error": "missing"})
            continue
        packs = pack_shots({"shots": [shot]}, max_frames=args.max_frames)
        text, conv, val = compile_prompt_offline(packs[0], refmods=refs)
        from h3max_bridge.gates import bind_refmods_for_shots
        bound, bind_rep = bind_refmods_for_shots(refs, [shot])
        reports.append(
            structural_report(
                shot_id=sid,
                shot=shot,
                refmods=bound,
                prompt=text,
                gates=conv.get("bridge_gates") or {},
                validation_redacted=val.get("redacted"),
            )
            | {
                "validation_status": val.get("status"),
                "offline": True,
                "lint_ctx_passed": conv.get("lint_ctx_passed"),
                "bind_report_people_n": (conv.get("bind_report") or {}).get("people_n"),
                "bind_report_visual_bound": (conv.get("bind_report") or {}).get("visual_bound"),
                "bind_report_audio_n": (conv.get("bind_report") or {}).get("audio_n"),
                "d_invented": "<d>" in (text or ""),
                "canned_fallback_line": "I'm right here" in (text or ""),
            }
        )
    sys.stdout.write(json.dumps({"reports": reports}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
