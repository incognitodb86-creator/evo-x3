"""Resolver for H3 parody pipeline (U2 + U3 stills gate).

Resolves requested identities against Malcolm INDEX mirror and local RefMods,
enforcing good/bad/fence rules, slot stacking, >8 truncation, and stills gate.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple


def _normalize_key(name: str) -> str:
    """Normalize string for fuzzy/case-insensitive matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_index_files(index_dir: Path) -> List[Dict[str, Any]]:
    """Parse INDEX.md and INDEX_BAD.md into a list of row dicts.

    Args:
        index_dir: Directory containing INDEX.md and INDEX_BAD.md.

    Returns:
        List of character dictionaries with keys:
            - character: character name
            - actor: real actor name
            - franchise: franchise / show
            - clips: list of clip filenames
            - date_added: date string
            - status: "good", "onthefence", or "bad"
    """
    rows: List[Dict[str, Any]] = []

    index_main = index_dir / "INDEX.md"
    if index_main.is_file():
        current_status = "good"
        for line in index_main.read_text(encoding="utf-8").splitlines():
            line_str = line.strip()
            if line_str.startswith("## Folder: `good`"):
                current_status = "good"
            elif line_str.startswith("## Folder: `onthefence`"):
                current_status = "onthefence"
            elif line_str.startswith("|") and not line_str.startswith("| :---") and not line_str.startswith("| Character"):
                parts = [p.strip() for p in line_str.split("|")[1:-1]]
                if len(parts) >= 5:
                    char_name = re.sub(r"^\*+|\*+$", "", parts[0]).strip()
                    actor_name = parts[1].strip()
                    franchise = parts[2].strip()
                    clips = [c.strip() for c in parts[3].split("<br>") if c.strip()]
                    date_added = parts[4].strip()
                    rows.append({
                        "character": char_name,
                        "actor": actor_name,
                        "franchise": franchise,
                        "clips": clips,
                        "date_added": date_added,
                        "status": current_status,
                    })

    index_bad = index_dir / "INDEX_BAD.md"
    if index_bad.is_file():
        for line in index_bad.read_text(encoding="utf-8").splitlines():
            line_str = line.strip()
            if line_str.startswith("|") and not line_str.startswith("| :---") and not line_str.startswith("| Character"):
                parts = [p.strip() for p in line_str.split("|")[1:-1]]
                if len(parts) >= 5:
                    char_name = re.sub(r"^\*+|\*+$", "", parts[0]).strip()
                    actor_name = parts[1].strip()
                    franchise = parts[2].strip()
                    clips = [c.strip() for c in parts[3].split("<br>") if c.strip()]
                    date_added = parts[4].strip()
                    rows.append({
                        "character": char_name,
                        "actor": actor_name,
                        "franchise": franchise,
                        "clips": clips,
                        "date_added": date_added,
                        "status": "bad",
                    })

    return rows


def load_aliases(aliases_path: Optional[Path]) -> Dict[str, str]:
    """Load alias mapping from JSON file if present."""
    if aliases_path and aliases_path.is_file():
        try:
            data = json.loads(aliases_path.read_text(encoding="utf-8"))
            return {_normalize_key(k): v for k, v in data.items()}
        except Exception:
            return {}
    return {}


def find_refmods_for_name(norm_name: str, refmods_dir: Path) -> List[Path]:
    """Find local .safetensors RefMod files matching normalized name."""
    matches: List[Path] = []
    if not refmods_dir.is_dir():
        return matches

    for f in refmods_dir.glob("*.safetensors"):
        fname_norm = _normalize_key(f.stem)
        # Check if name is part of filename, e.g. "emiliaclarke" in "minimaxh3_emiliaclarke_v1_refmod"
        if norm_name in fname_norm:
            matches.append(f)
    return matches


def validate_stills(stills: List[str], approved_dir: Optional[Path]) -> List[str]:
    """Validate still image paths against approved pool and security constraints.

    Enforces:
    - Rejection of any path referencing Sydney (FP-10).
    - Containment within approved_characters pool (U3 / KD10).

    Args:
        stills: List of still image file path strings.
        approved_dir: Path to approved characters pool directory.

    Returns:
        List of validated resolved path strings.

    Raises:
        ValueError: If a still path violates security or pool containment.
    """
    valid_paths: List[str] = []
    if not stills:
        return valid_paths

    for s in stills:
        p = Path(s).resolve()
        # Sydney isolation rule: never touch Sydney assets
        if "sydney" in str(p).lower() or p.name.upper() == "SYDNEY":
            raise ValueError(f"Sydney paths are strictly prohibited: {s}")

        if approved_dir is not None:
            app_dir_res = approved_dir.resolve()
            try:
                # Check containment
                p.relative_to(app_dir_res)
            except ValueError:
                raise ValueError(
                    f"Still path '{s}' is not within the approved_characters pool: '{approved_dir}'"
                )

        if not p.is_file():
            raise ValueError(f"Still file does not exist: {s}")

        valid_paths.append(str(p))

    return valid_paths


def resolve_identities(
    request: Dict[str, Any],
    index_dir: Path,
    refmods_dir: Path,
    approved_stills_dir: Optional[Path] = None,
    aliases_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Resolve normalized request against INDEX and RefMods.

    Args:
        request: Normalized request dict from request.py.
        index_dir: Directory containing INDEX.md and INDEX_BAD.md.
        refmods_dir: Directory containing *.safetensors RefMod files.
        approved_stills_dir: Approved pool directory for stills gate.
        aliases_path: Path to aliases.json.

    Returns:
        Resolved dictionary with mode, INDEX rows, RefMod slots (1..8), description.
    """
    index_rows = load_index_files(index_dir)
    aliases = load_aliases(aliases_path)

    # 1. Validate stills (U3)
    validated_stills = validate_stills(request.get("stills", []), approved_stills_dir)

    # 2. Gather candidate identities
    names = request.get("names", [])
    character_input = request.get("character")
    actor_input = request.get("actor")

    candidates: List[str] = []
    for n in names:
        if n not in candidates:
            candidates.append(n)
    if character_input and character_input not in candidates:
        candidates.append(character_input)
    if actor_input and actor_input not in candidates:
        candidates.append(actor_input)

    # Expand aliases (KD2 stacking)
    expanded_candidates: List[Tuple[str, str]] = []  # (name, role: "character" | "actor" | "query")
    for c in candidates:
        norm_c = _normalize_key(c)
        expanded_candidates.append((c, "character" if c == character_input else "query"))
        if norm_c in aliases:
            resolved_actor = aliases[norm_c]
            if resolved_actor not in [ec[0] for ec in expanded_candidates]:
                expanded_candidates.append((resolved_actor, "actor"))

    # 3. Match against INDEX rows
    matched_index_rows: List[Dict[str, Any]] = []
    for c_name, role in expanded_candidates:
        norm_c = _normalize_key(c_name)
        for r in index_rows:
            norm_char = _normalize_key(r["character"])
            norm_act = _normalize_key(r["actor"])
            if norm_c == norm_char or norm_c == norm_act or norm_c in norm_char or norm_c in norm_act:
                if r not in matched_index_rows:
                    matched_index_rows.append(r)
                    # If matched character, also add its actor if not present
                    if r["actor"] and r["actor"] != r["character"]:
                        actor_cand = (r["actor"], "actor")
                        if actor_cand not in expanded_candidates:
                            expanded_candidates.append(actor_cand)

    # Determine overall INDEX status
    # Priority: if a character is explicitly requested and matched in index, its status governs.
    # Otherwise: good > onthefence > bad > none
    status_priority = {"good": 3, "onthefence": 2, "bad": 1}
    best_status = "none"
    if matched_index_rows:
        if character_input:
            char_norm = _normalize_key(character_input)
            char_matches = [r for r in matched_index_rows if char_norm == _normalize_key(r["character"])]
            if char_matches:
                best_status = char_matches[0]["status"]
        if best_status == "none":
            statuses = [r["status"] for r in matched_index_rows]
            sorted_statuses = sorted(statuses, key=lambda s: status_priority.get(s, 0), reverse=True)
            best_status = sorted_statuses[0]

    # Mode determination (KD9, KD13, KD15)
    if best_status == "good":
        mode = "native_face_voice"
    elif best_status in ("bad", "onthefence"):
        mode = "native_voice_refmod_look"
    else:
        mode = "native_voice_refmod_look"  # Not in INDEX treated as bad per KD15

    # 4. Find RefMod files
    matched_refmods: List[Tuple[Path, str, str]] = []  # (path, role, status)
    for c_name, role in expanded_candidates:
        norm_c = _normalize_key(c_name)
        # Find index status for this specific candidate if any
        c_status = "bad"
        for r in matched_index_rows:
            if norm_c == _normalize_key(r["character"]) or norm_c == _normalize_key(r["actor"]):
                c_status = r["status"]
                break

        files = find_refmods_for_name(norm_c, refmods_dir)
        for f in files:
            if not any(f == m[0] for m in matched_refmods):
                matched_refmods.append((f, role, c_status))

    # 5. Over 8 RefMods truncation (KD14):
    # Keep character matches first, then fill with highest INDEX status (good > fence > bad), drop rest
    def _refmod_sort_key(item: Tuple[Path, str, str]) -> Tuple[int, int]:
        role_weight = 1 if item[1] == "character" else 0
        stat_weight = status_priority.get(item[2], 0)
        return (role_weight, stat_weight)

    sorted_refmods = sorted(matched_refmods, key=_refmod_sort_key, reverse=True)
    kept_refmods = sorted_refmods[:8]
    dropped_refmods = sorted_refmods[8:]

    # Build 8 fixed loader slots (F3)
    slots: Dict[str, Dict[str, Any]] = {}
    for i in range(1, 9):
        slot_key = f"mod_{i}"
        if i - 1 < len(kept_refmods):
            rf_path, _, _ = kept_refmods[i - 1]
            slots[slot_key] = {"path": str(rf_path), "strength": 1.0}
        else:
            slots[slot_key] = {"path": "(none)", "strength": 1.0}

    # 6. Build written identity description (KD3)
    primary_name = candidates[0] if candidates else "subject"
    char_part = f"character {character_input}" if character_input else ""
    actor_part = f"actor {actor_input}" if actor_input else ""
    parts = [p for p in [char_part, actor_part] if p]
    id_spec = f"featuring {primary_name}" + (f" ({', '.join(parts)})" if parts else "")
    description = f"{id_spec}, distinctive facial features, exact likeness and vocal timbre, styled in {request.get('tone', 'parody')} tone."

    return {
        "names": names,
        "character": character_input,
        "actor": actor_input,
        "tone": request.get("tone", "parody"),
        "length_s": request.get("length_s", 10),
        "mode": mode,
        "index_status": best_status,
        "index_flag": "index:none" if best_status == "none" else f"index:{best_status}",
        "index_rows": matched_index_rows,
        "description": description,
        "refmod_slots": slots,
        "loaded_refmods": [str(m[0]) for m in kept_refmods],
        "dropped_refmods": [str(m[0]) for m in dropped_refmods],
        "stills": validated_stills,
    }
