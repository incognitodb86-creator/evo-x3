"""Request parser for H3 parody pipeline (U1).

Parses plain text chat or structured fields into a normalized request dictionary.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union


def parse_request(input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Parse chat string or fields dictionary into a normalized parody request.

    Args:
        input_data: Either a plain chat string (e.g. "Daenerys parody, 10s")
            or a dictionary with structured fields.

    Returns:
        Normalized dictionary with keys:
            - names: list of identity strings
            - character: optional character name
            - actor: optional actor name
            - tone: tone string (e.g. "parody", "adult")
            - length_s: video duration in seconds (default: 10)
            - stills: list of still image paths (default: [])

    Raises:
        ValueError: If no identity name is provided.
    """
    if isinstance(input_data, dict):
        names: List[str] = []
        if "names" in input_data and input_data["names"]:
            if isinstance(input_data["names"], list):
                names.extend([str(n).strip() for n in input_data["names"] if str(n).strip()])
            else:
                names.append(str(input_data["names"]).strip())

        character = input_data.get("character")
        if character and str(character).strip():
            character = str(character).strip()
            if character not in names:
                names.append(character)
        else:
            character = None

        actor = input_data.get("actor")
        if actor and str(actor).strip():
            actor = str(actor).strip()
            if actor not in names:
                names.append(actor)
        else:
            actor = None

        tone = str(input_data.get("tone", "parody")).strip().lower()
        if not tone:
            tone = "parody"

        try:
            length_s = int(input_data.get("length_s", 10))
        except (ValueError, TypeError):
            length_s = 10

        stills_raw = input_data.get("stills", [])
        if isinstance(stills_raw, list):
            stills = [str(s).strip() for s in stills_raw if str(s).strip()]
        elif stills_raw:
            stills = [str(stills_raw).strip()]
        else:
            stills = []

        if not names:
            raise ValueError("Missing identity name in request: at least one character or actor must be specified.")

        return {
            "names": names,
            "character": character,
            "actor": actor,
            "tone": tone,
            "length_s": length_s,
            "stills": stills,
        }

    if isinstance(input_data, str):
        text = input_data.strip()
        if not text:
            raise ValueError("Missing identity name in request: input text is empty.")

        # Extract duration if present, e.g. "10s", "5s", "15 seconds"
        length_s = 10
        m_len = re.search(r"\b(\d+)\s*(?:s|sec|seconds?)\b", text, re.IGNORECASE)
        if m_len:
            length_s = int(m_len.group(1))
            # Remove length token from consideration
            text = text[:m_len.start()] + text[m_len.end():]

        # Extract tone if present, e.g. "adult", "satirical", "parody", "dramatic"
        tone = "parody"
        for t_opt in ["adult", "satirical", "parody", "humorous", "serious", "dramatic"]:
            if re.search(rf"\b{t_opt}\b", text, re.IGNORECASE):
                tone = t_opt
                break

        # Remove common request keywords to isolate name
        clean_text = re.sub(r"\b(parody|video|clip|make|run|generate|render|of|a|an|the|please|for)\b", "", text, flags=re.IGNORECASE)
        # Split on commas, semicolons, 'and'
        parts = re.split(r"[,;&]|\band\b", clean_text, flags=re.IGNORECASE)
        names = [p.strip() for p in parts if p.strip()]

        if not names:
            raise ValueError("Missing identity name in request: could not parse name from chat text.")

        character = names[0] if len(names) >= 1 else None

        return {
            "names": names,
            "character": character,
            "actor": None,
            "tone": tone,
            "length_s": length_s,
            "stills": [],
        }

    raise TypeError(f"Expected str or dict for input_data, got {type(input_data).__name__}")
