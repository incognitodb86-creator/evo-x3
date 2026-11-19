"""Offline schema tests for RV1 user capability YAML (minimax-h3-10eros-beta7)."""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VIDEO_YAML = REPO_ROOT / "agent-shared" / "rea-video" / "capabilities" / "models" / "video.yaml"
PROMPTING_YAML = REPO_ROOT / "agent-shared" / "rea-video" / "capabilities" / "prompting.yaml"

ALLOWED_TOP_KEYS = {
    "id",
    "name",
    "vendor",
    "category",
    "release",
    "status",
    "access",
    "primitives",
    "limits",
    "audio",
    "strengths",
    "weaknesses",
    "cost",
    "license",
    "regions_excluded",
    "sources",
    "verified",
    "confidence",
    "probe_scores",
    "notes",
}
REQUIRED_TOP_KEYS = {
    "id",
    "name",
    "vendor",
    "category",
    "status",
    "access",
    "primitives",
    "license",
    "sources",
    "verified",
    "confidence",
}


def test_video_yaml_matches_rea_video_schema() -> None:
    data = yaml.safe_load(VIDEO_YAML.read_text(encoding="utf-8"))
    assert isinstance(data, dict) and isinstance(data.get("models"), list)
    entries = [m for m in data["models"] if m.get("id") == "minimax-h3-10eros-beta7"]
    assert len(entries) == 1
    entry = entries[0]

    assert REQUIRED_TOP_KEYS.issubset(entry.keys())
    assert set(entry.keys()).issubset(ALLOWED_TOP_KEYS)
    assert re.match(r"^[a-z0-9][a-z0-9.\-]*$", entry["id"])
    assert entry["category"] == "video"
    assert entry["status"] in {"ga", "preview", "limited", "deprecated", "shutdown"}
    assert set(entry["access"]).issubset({"app", "api", "api-aggregator", "open-weights"})
    assert entry["confidence"] in {"high", "medium", "low"}
    assert re.match(r"^\d{4}-\d{2}$", str(entry["release"]))
    assert re.match(r"^\d{4}-\d{2}-\d{2}$", str(entry["verified"]["date"]))
    assert entry["verified"]["basis"] in {"probe", "user", "vendor", "third-party", "knowledge"}
    assert all(str(u).startswith(("http://", "https://")) for u in entry["sources"])

    limits = entry["limits"]
    assert limits["duration_s"]["max"] == 15.08
    assert limits["audio_s"]["max"] == 15.0
    assert limits["refs"]["image"] == 9
    assert limits["refs"]["video"] == 3
    assert limits["refs"]["audio"] == 3


def test_prompting_yaml_has_beta7_entry() -> None:
    data = yaml.safe_load(PROMPTING_YAML.read_text(encoding="utf-8"))
    spec = data["models"]["minimax-h3-10eros-beta7"]
    assert spec["basis"] == "user"
    assert "header-free" in spec["structure"].lower()
    assert "beta7_convert.py" in spec["structure"]
    assert "mod_1..mod_8" in spec["references"]
