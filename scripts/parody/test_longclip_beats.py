"""U2 long-clip beat sheet reference validation.

Tests beat sheet fields, planning rules, routing links, and dial isolation.
Synthetic checks only. No GPU, network, or live effects.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import unittest


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"U2 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

REPO_ROOT = Path(r"C:\AI\community")
BEAT_SHEET_REF = REPO_ROOT / "skills" / "h3-prompting" / "references" / "longclip-beat-sheet.md"


class TestLongclipBeats(unittest.TestCase):
    """Validation tests for the long-clip beat sheet reference."""

    def setUp(self) -> None:
        self.assertTrue(BEAT_SHEET_REF.exists(), f"Missing beat sheet reference: {BEAT_SHEET_REF}")
        self.content = BEAT_SHEET_REF.read_text(encoding="utf-8")

    def test_beat_sheet_required_fields_present(self) -> None:
        """All 8 required beat sheet fields are documented."""
        required_fields = [
            "clip/shot id",
            "primary beat",
            "opening/ending state",
            "identity/wardrobe/location/prop anchors",
            "camera continuity vs cut",
            "dialogue boundaries",
            "frame budget",
            "method",
        ]
        content_lower = self.content.lower()
        # 2026-11-06: "dialogue boundaries" was split into spoken_dialogue + ambient_sfx so stage
        # cues never leak into <d>[English] ...</d>; either form documents the boundary.
        if "dialogue boundaries" not in content_lower and "spoken_dialogue" in content_lower \
                and "ambient_sfx" in content_lower:
            required_fields.remove("dialogue boundaries")
        for field in required_fields:
            self.assertIn(field, content_lower, f"Missing required field: {field}")

    def test_beat_sheet_methods_specified(self) -> None:
        """All 3 execution methods are specified: in-clip [Shot N], planned cut, C2V."""
        self.assertIn("in-clip [Shot N]", self.content)
        self.assertIn("planned cut", self.content)
        self.assertIn("C2V", self.content)

    def test_beat_sheet_core_planning_rules(self) -> None:
        """Core planning rules: prefer in-clip [Shot N], don't restate finished actions, 1 primary beat."""
        content_lower = self.content.lower()
        self.assertIn("prefer in-clip", content_lower)
        self.assertIn("don't restate finished actions", content_lower)
        self.assertIn("one primary beat per clip", content_lower)

    def test_beat_sheet_c2v_unproven_marking(self) -> None:
        """C2V runtime is explicitly marked UNPROVEN (native A/V carry unproven)."""
        self.assertIn("UNPROVEN", self.content)
        self.assertTrue(
            "unproven" in self.content.lower() or "native a/v carry is unproven" in self.content.lower(),
            "C2V runtime must be explicitly marked UNPROVEN",
        )

    def test_beat_sheet_routing_and_no_copied_dials(self) -> None:
        """Links to h3-hc-render and LANE_IMAGE_RULES without copying dials or image rules."""
        # Must link to h3-hc-render/SKILL.md
        self.assertIn("skills/h3-hc-render/SKILL.md", self.content)
        # Must link to LANE_IMAGE_RULES.md
        self.assertIn("LANE_IMAGE_RULES.md", self.content)

        # Must not copy render dial settings like beta7 specific steps/shifts
        dial_patterns = [
            r"steps\s*[:=]\s*8",
            r"shift\s*[:=]\s*7\.0",
            r"vsa\s*[:=]",
        ]
        for pattern in dial_patterns:
            self.assertIsNone(
                re.search(pattern, self.content, re.IGNORECASE),
                f"Found copied render dial matching {pattern} in beat sheet",
            )


if __name__ == "__main__":
    unittest.main()
