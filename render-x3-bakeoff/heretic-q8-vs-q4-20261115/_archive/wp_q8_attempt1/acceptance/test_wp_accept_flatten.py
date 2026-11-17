"""Flatten pick.json onto a summary row even when writer_output.txt is missing (f5 youth block)."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wp_accept as wa  # noqa: E402


def test_apply_pick_to_row_youth_block_without_writer_output(tmp_path):
    rd = tmp_path / "f5_youth_seed"
    rd.mkdir()
    pk = {
        "run": "f5_youth_seed",
        "ask": "tiny teen fairy rides him",
        "position": "cowgirl",
        "kind": "sex",
        "status": "NOT_READY",
        "warnings": [],
        "not_ready_reason": "youth hint in the ask: 'teen' (every person is an adult, 18+)",
        "seconds": 0.0,
        "llm_seconds": 0,
    }
    (rd / "pick.json").write_text(json.dumps(pk), encoding="utf-8")
    (rd / "clip_NOT_READY.txt").write_text("NOT_READY: youth hint in the ask: 'teen'", encoding="utf-8")
    row = {"case": "f5_youth_seed"}
    wa.apply_pick_to_row(row, rd)
    assert row["status"] == "NOT_READY"
    assert row["seconds"] == 0.0
    assert "teen" in (row.get("not_ready_reason") or "")
    assert "youth" in (row.get("not_ready_msg") or "").lower()
    assert "lines" not in row  # no writer_output.txt


def test_apply_pick_to_row_keeps_prose_fields_when_writer_output_exists(tmp_path):
    rd = tmp_path / "ok"
    rd.mkdir()
    pk = {
        "status": "READY",
        "mode": "sex",
        "overlays": [],
        "act_id": "handjob",
        "pick": "cand_1",
        "pick_score": 80,
        "pick_pass": True,
        "pick_hard": [],
        "warnings": [],
        "seconds": 12.0,
        "builds": [{"status": "READY"}],
        "build_added": ["PRIMARY MOTION label"],
        "candidates": {"cand_1": {"pass": True}},
    }
    (rd / "pick.json").write_text(json.dumps(pk), encoding="utf-8")
    (rd / "writer_output.txt").write_text(
        "detailed_description:\n[Shot 1] The camera holds. She sits beside him.\n",
        encoding="utf-8",
    )
    row = {"case": "lf24_handjob"}
    wa.apply_pick_to_row(row, rd)
    assert row["status"] == "READY" and row["score"] == 80 and row["act"] == "handjob"
    assert row["first_build"] == "READY"
    assert row["builder_primary_added"] is True
    assert row.get("opening")
