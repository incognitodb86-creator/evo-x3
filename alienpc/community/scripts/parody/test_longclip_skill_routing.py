"""U5 skill routing, beat sheet pointers, and missing file checks.

Synthetic inspection only. No GPU, network, or live effects.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"U5 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

REPO_ROOT = Path(r"C:\AI\community")
H3_PROMPTING_SKILL = REPO_ROOT / "skills" / "h3-prompting" / "SKILL.md"
BEAT_SHEET_REF = REPO_ROOT / "skills" / "h3-prompting" / "references" / "longclip-beat-sheet.md"
VIDEO_RENDER_SKILL = REPO_ROOT / "skills" / "video-render" / "SKILL.md"

FORBIDDEN_FILES = [
    REPO_ROOT / "scripts" / "parody" / "reflora.py",
    REPO_ROOT / "scripts" / "parody" / "resolve.py",
    REPO_ROOT / "scripts" / "parody" / "build_request.py",
    REPO_ROOT / "scripts" / "parody" / "run_record.py",
    REPO_ROOT / "scripts" / "parody" / "submit_parody_run.py",
    REPO_ROOT / "scripts" / "parody" / "test_parody_reflora.py",
    REPO_ROOT / "skills" / "h3-parody-identity" / "SKILL.md",
]


class TestLongclipSkillRouting(unittest.TestCase):
    """Test suite for skill routing, pointers, and file boundaries."""

    def test_h3_prompting_skill_has_pointer_to_beat_sheet(self) -> None:
        """skills/h3-prompting/SKILL.md has pointer to longclip-beat-sheet.md with C2V marked UNPROVEN."""
        self.assertTrue(H3_PROMPTING_SKILL.exists(), f"Missing {H3_PROMPTING_SKILL}")
        content = H3_PROMPTING_SKILL.read_text(encoding="utf-8")

        self.assertIn("longclip-beat-sheet.md", content)
        # Check that C2V runtime is marked UNPROVEN in the pointer line
        pointer_lines = [line for line in content.splitlines() if "longclip-beat-sheet.md" in line]
        self.assertTrue(len(pointer_lines) >= 1)
        self.assertIn("UNPROVEN", pointer_lines[0])

    def test_video_render_skill_reported_missing_and_not_created(self) -> None:
        """skills/video-render/SKILL.md does not exist on this box and is reported MISSING without being created."""
        self.assertFalse(
            VIDEO_RENDER_SKILL.exists(),
            "skills/video-render/SKILL.md was unexpectedly created; brief requires reporting MISSING instead of creating.",
        )

    def test_beat_sheet_reference_target_exists(self) -> None:
        """The referenced longclip-beat-sheet.md file exists and is valid markdown."""
        self.assertTrue(BEAT_SHEET_REF.exists())
        text = BEAT_SHEET_REF.read_text(encoding="utf-8")
        self.assertIn("# Long-Clip Beat Sheet", text)

    def test_forbidden_reflora_files_untouched(self) -> None:
        """Forbidden RefLoRA and template files remain untouched."""
        for path in FORBIDDEN_FILES:
            if path.exists():
                text = path.read_text(encoding="utf-8", errors="ignore")
                # Ensure longclip setup helpers are not leaked into Max's reflora files
                self.assertNotIn("bridge_parody_stitch", text)
                self.assertNotIn("allocate_compensated_clips", text)


if __name__ == "__main__":
    unittest.main()
