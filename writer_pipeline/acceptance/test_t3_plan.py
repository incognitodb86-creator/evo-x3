"""T3 long-scene plan invariants (dry, no writer calls)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import t3_plan


def test_t3_plan_meets_long_scene_spec():
    p = t3_plan.build_plan()
    assert 285 <= p["total_seconds"] <= 315
    assert p["n"] >= 20
    assert p["genre"]
    assert "BEDROOM" in p["still"] or "bed" in p["surface"].lower()
    roles = [c["role"] for c in p["clips"]]
    assert roles.count("strip") == 1
    assert "finish" in roles and roles[-1] == "aftercare"
    nude_from = next(c["clip"] for c in p["clips"] if c["role"] == "strip")
    for c in p["clips"]:
        if c["clip"] > nude_from:
            assert "strips the slip" not in c["ask"] and "strap fall" not in c["ask"]
        for k in ("wardrobe", "pose", "screen_side", "contact", "frames", "surface", "genre"):
            assert c.get(k) not in (None, ""), (c["name"], k)
        assert c["frames"] in t3_plan.LEGAL
        assert c["surface"] == "the bed"
        # cowgirl is only planned on the bed
        if c["position"] == "cowgirl":
            assert "bed" in c["surface"]
