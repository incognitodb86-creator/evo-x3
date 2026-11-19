"""Raw llama-swap writer system prompt: prompt skills only, never Render agent instructions.

Last Updated: 2026-11-11

~/AI/render/AGENTS.md is the Render *agent* instruction file (tool calls, hook commands, GPU lock, QNAP). When it is
pasted into a raw writer call (no tools), writers answer with an agent preamble, a refusal or a fake tool call and stop
short (fn_swift_bakeoff_rerun_20261111). The Render agent keeps AGENTS.md as its own instructions and then calls the
hook; a raw writer call gets only the prompt skills below.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"
WRITER_SKILL_SOURCES: Tuple[Path, ...] = (
    SKILLS_ROOT / "h3-parody-identity" / "SKILL.md",
    SKILLS_ROOT / "h3-prompting" / "SKILL.md",
    SKILLS_ROOT / "h3-prompting" / "references" / "motion-contact-anatomy.md",
    SKILLS_ROOT / "h3-prompting" / "references" / "wording.md",
)
# Markers that only appear in agent instruction files (AGENTS.md / GEMINI.md), never in a prompt skill.
_AGENT_FILE_NAMES = {"agents.md", "gemini.md", "claude.md"}
_AGENT_MARKERS = ("# Render Rules", "## Prompt Writer Rules", str(Path(__file__).resolve().parents[3] / "locks" / "gpu-render.lock"), "pi_qnap.py")


class AgentInstructionsInWriterPrompt(ValueError):
    """A raw writer system prompt would carry agent instructions (AGENTS.md)."""


def is_agent_instruction_file(path: Path) -> bool:
    """True for agent instruction files that must never enter a raw writer system prompt."""
    return Path(path).name.lower() in _AGENT_FILE_NAMES


def assert_writer_system_prompt(text: str) -> None:
    """Raise when a raw writer system prompt contains Render agent instructions."""
    hits = [m for m in _AGENT_MARKERS if m in (text or "")]
    if hits:
        raise AgentInstructionsInWriterPrompt(f"raw writer system prompt carries agent instructions: {hits}")


def build_writer_system_prompt(sources: Optional[Sequence[Path]] = None, note: str = "") -> Tuple[str, List[Dict[str, object]]]:
    """Concatenate the prompt skills (front matter stripped) for a raw writer call. Returns (text, source metadata).

    Any AGENTS.md / GEMINI.md source is refused, and the result is checked for agent-only markers."""
    parts: List[str] = []
    meta: List[Dict[str, object]] = []
    for p in (sources or WRITER_SKILL_SOURCES):
        p = Path(p)
        if is_agent_instruction_file(p):
            raise AgentInstructionsInWriterPrompt(f"{p} is an agent instruction file, not a prompt skill")
        b = p.read_bytes()
        t = b.decode("utf-8-sig")
        meta.append({"path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest().upper()})
        if p.name == "SKILL.md" and t.startswith("---"):
            e = t.find("\n---", 3)
            t = t[e + 4:].lstrip("\n") if e != -1 else t
        parts.append(f"===== {p} =====\n{t}")
    text = "\n\n".join(parts) + (f"\n\n{note}" if note else "")
    assert_writer_system_prompt(text)
    return text, meta
