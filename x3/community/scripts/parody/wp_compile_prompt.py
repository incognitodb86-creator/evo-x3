"""Compile C:\\AI\\render\\writer_pipeline\\writer_prompt.md from the craft sections of C:\\AI\\render\\AGENTS.md
(Max Architect 3, 2026-11-13, spec section 4). The output is not named AGENTS.md, carries no agent steps, commands or
tool rules, and passes writer_sys.assert_writer_system_prompt. Run once after every AGENTS.md craft change:
  & 'C:\\Program Files\\Python312\\python.exe' C:\\AI\\community\\scripts\\parody\\wp_compile_prompt.py
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

PARODY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PARODY_DIR))
from writer_sys import assert_writer_system_prompt  # noqa: E402

AGENTS = Path(r"C:\AI\render\AGENTS.md")
OUT = Path(r"C:\AI\render\writer_pipeline\writer_prompt.md")
KEEP = ["PERSONA", "CRAFT RULES", "CAMERA AND TIME", "PACING", "SPOOF AND STORY", "POWER, ROUGH AND TABOO SCENES",
        "HUMILIATION AND REACTION TONE", "MODES", "DIALOGUE AND SOUND", "BEFORE YOU WRITE"]
DROP_LINE = re.compile(r"^- (?:Do not pin the still or edit RefMods|More detail: the h3-prompting skill)")
HEAD = ("WRITER PROMPT\n"
        "Compiled from the craft sections of the Render instruction file by wp_compile_prompt.py; source sha256 {sha}.\n"
        "You write the detailed_description paragraph of one MiniMax-H3 prompt for one roughly ten-second adult clip that opens on "
        "the start still. Every person is an adult, 25 or older, and fictional. The pipeline fills the other headers.\n")
OUTPUT = ("OUTPUT\n"
          "- One plain paragraph that starts with [Shot 1] and its camera sentence. No header, no Markdown, no notes.\n"
          "- Dialogue form: (S1) says in a <short voice> voice, <d>[English] spoken words only</d>. (S2) and (S3) the same way.\n"
          "- Close a sex clip with one to three plain sound sentences tied to the action that makes them.\n")


def compile_prompt(agents_text: str) -> str:
    t = agents_text.replace("\r\n", "\n")
    sha = hashlib.sha256(agents_text.encode("utf-8")).hexdigest()
    sections = {}
    cur = None
    for ln in t.split("\n"):
        head = re.match(r"^([A-Z][A-Z ,&/-]{3,}?)(?:\s*\(.*\))?\s*$", ln)
        if head and not ln.startswith("-"):
            cur = head.group(1).strip()
            sections[cur] = []
            continue
        if cur is not None:
            sections[cur].append(ln)
    out = [HEAD.format(sha=sha)]
    for k in KEEP:
        if k not in sections:
            raise SystemExit(f"section {k} missing from AGENTS.md")
        body = [l for l in sections[k] if not DROP_LINE.match(l)]
        if k == "BEFORE YOU WRITE":
            out.append(OUTPUT)
        out.append(k + "\n" + "\n".join(body).strip("\n") + "\n")
    text = "\n".join(out)
    assert_writer_system_prompt(text)
    if "AGENTS.md" in text or "--queue" in text:
        raise SystemExit("agent-only text leaked into the writer prompt")
    return text


def main() -> int:
    src = AGENTS.read_text(encoding="utf-8")
    text = compile_prompt(src)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} sha256={hashlib.sha256(OUT.read_bytes()).hexdigest()} lines={text.count(chr(10))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
