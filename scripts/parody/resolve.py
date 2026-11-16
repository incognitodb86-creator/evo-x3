"""Resolver for H3 parody pipeline (U2 + U3 stills gate).

Resolves requested identities against Malcolm INDEX mirror and local RefMods,
enforcing good/bad/fence rules, slot stacking, >8 truncation, and stills gate.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_APPROVED_STILLS_DIR = Path(__file__).resolve().parents[3] / "5slock" / "approved_characters"
KD17_REFMOD_STRENGTHS: Tuple[float, float, float] = (1.0, 1.0, 0.80)
NAS_APPROVED_STILLS_DIR = Path(r"\\NAS4CBE37.local\home\AlienPc-approved\approved_characters")
APPROVED_IMAGE_POOLS: Tuple[Path, ...] = (DEFAULT_APPROVED_STILLS_DIR, NAS_APPROVED_STILLS_DIR)
REFERENCE_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
MAX_REFERENCE_IMAGES = 4


def _normalize_key(name: str) -> str:
    """Normalize string for fuzzy/case-insensitive matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


BANNED_GENERICS: Tuple[str, ...] = (
    "exact likeness",
    "distinctive facial features",
    "natural authentic human appearance",
)


def validate_biometric_description(bio: Optional[str]) -> str:
    """Validate biometric / wardrobe description against empty and generic-only inputs.

    Args:
        bio: Input description string.

    Returns:
        Cleaned, non-empty description string containing concrete biometric/wardrobe details.

    Raises:
        ValueError: If bio is missing/empty, matches banned generics alone,
            or contains only generic phrasing without concrete details.
    """
    if bio is None:
        raise ValueError("Biometric description / bio is required: cannot be None.")

    text = str(bio).strip()
    if not text:
        raise ValueError("Biometric description / bio is required: cannot be empty or whitespace.")

    norm = re.sub(r"[^\w\s]", " ", text.lower())
    norm_words = norm.split()
    norm_clean = " ".join(norm_words)

    # 1. Exact match to banned generic phrases alone
    for banned in BANNED_GENERICS:
        banned_norm = " ".join(re.sub(r"[^\w\s]", " ", banned.lower()).split())
        if norm_clean == banned_norm:
            raise ValueError(
                f"Biometric description matches banned generic phrase alone: {text!r}. "
                "Must provide concrete biometric/wardrobe details."
            )

    # 2. Check if residual after removing banned phrases and generic filler words is empty
    residual = norm_clean
    extended_banned = list(BANNED_GENERICS) + [
        "exact likeness and vocal timbre",
        "distinctive facial features and vocal timbre",
        "natural authentic human appearance",
        "authentic human appearance",
        "natural human appearance",
        "natural vocal timbre",
        "vocal timbre",
    ]
    for banned in sorted(extended_banned, key=len, reverse=True):
        banned_norm = " ".join(re.sub(r"[^\w\s]", " ", banned.lower()).split())
        residual = residual.replace(banned_norm, " ")

    filler_words = {
        "and", "with", "the", "a", "an", "of", "in", "to", "for", "styled", "tone",
        "features", "appearance", "likeness", "facial", "vocal", "timbre", "natural",
        "authentic", "exact", "distinctive", "human", "alone", "only", "just",
    }
    residual_tokens = [w for w in residual.split() if w not in filler_words]
    if not residual_tokens:
        raise ValueError(
            f"Biometric description contains only generic phrasing without concrete details: {text!r}."
        )

    return text


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
        approved_dir: Approved characters pool directory. None uses DEFAULT_APPROVED_STILLS_DIR.

    Returns:
        List of validated resolved path strings.

    Raises:
        ValueError: If a still path violates security or pool containment.
    """
    valid_paths: List[str] = []
    if not stills:
        return valid_paths

    pool_dir = DEFAULT_APPROVED_STILLS_DIR if approved_dir is None else approved_dir
    app_dir_res = pool_dir.resolve()
    for s in stills:
        p = Path(s).resolve()
        # Sydney isolation rule: never touch Sydney assets
        if "sydney" in str(p).lower() or p.name.upper() == "SYDNEY":
            raise ValueError(f"Sydney paths are strictly prohibited: {s}")

        try:
            # Check containment; omitted approved_dir still fails closed to the default pool.
            p.relative_to(app_dir_res)
        except ValueError:
            raise ValueError(
                f"Still path '{s}' is not within the approved_characters pool: '{pool_dir}'"
            )

        if not p.is_file():
            raise ValueError(f"Still file does not exist: {s}")

        valid_paths.append(str(p))

    return valid_paths


def validate_reference_images(
    images: Optional[List[str]],
    pools: Optional[Tuple[Path, ...]] = None,
) -> List[str]:
    """U2: --image gate (LANE_IMAGE_RULES.md). Every image must live inside an approved_characters pool.

    Accepts a full path, or a sub-path / filename relative to a pool. Rejects > 4 images
    (MAX_REFERENCE_IMAGES), any path that mentions 'sydney' (case-insensitive), anything outside
    the pools, missing files, and non-image extensions.
    build_request.py wires --image as a single frame-0 AddGuide start image (0 or 1 per clip).
    """
    if not images:
        return []
    imgs = [str(x).strip() for x in images if x and str(x).strip()]
    if len(imgs) > MAX_REFERENCE_IMAGES:
        raise ValueError(f"at most {MAX_REFERENCE_IMAGES} --image references per clip (got {len(imgs)})")
    pool_list = tuple(Path(x) for x in (pools if pools is not None else APPROVED_IMAGE_POOLS))
    out: List[str] = []
    for raw in imgs:
        if "sydney" in raw.lower():
            raise ValueError(f"Sydney paths are strictly prohibited as reference images: {raw}")
        cand = Path(raw)
        tries = [cand] if cand.is_absolute() or str(cand).startswith("\\\\") else [pl / cand for pl in pool_list]
        found = None
        for t in tries:
            try:
                rp = t.resolve()
            except OSError:
                continue
            if "sydney" in str(rp).lower():
                raise ValueError(f"Sydney paths are strictly prohibited as reference images: {raw}")
            inside = False
            for pl in pool_list:
                try:
                    rp.relative_to(pl.resolve())
                    inside = True
                    break
                except (ValueError, OSError):
                    continue
            if not inside:
                if cand.is_absolute():
                    raise ValueError(
                        f"--image '{raw}' is not inside an approved_characters pool "
                        f"({', '.join(str(x) for x in pool_list)})"
                    )
                continue
            if rp.is_file():
                found = rp
                break
        if found is None:
            raise ValueError(f"--image '{raw}' not found inside an approved_characters pool")
        if found.suffix.lower() not in REFERENCE_IMAGE_EXTS:
            raise ValueError(f"--image '{raw}' must be one of {', '.join(REFERENCE_IMAGE_EXTS)}")
        out.append(str(found))
    return out


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
            strength = KD17_REFMOD_STRENGTHS[min(i - 1, len(KD17_REFMOD_STRENGTHS) - 1)]
            slots[slot_key] = {"path": str(rf_path), "strength": strength, "copies": 1}
        else:
            slots[slot_key] = {"path": "(none)", "strength": 1.0, "copies": 1}

    # 6. Build written identity description (KD3)
    raw_bio = request.get("description") or request.get("bio")
    valid_bio = validate_biometric_description(raw_bio)

    primary_name = candidates[0] if candidates else "subject"
    # MA-6: strip trailing period on bio before appending ", styled in ... tone."
    valid_bio = valid_bio.rstrip().rstrip(".")
    # Same-name celebrity: (actor X) not (character X, actor X)
    same_name = (
        bool(character_input)
        and bool(actor_input)
        and _normalize_key(character_input) == _normalize_key(actor_input)
        and _normalize_key(character_input) == _normalize_key(primary_name)
    )
    if same_name:
        parts = [f"actor {actor_input}"]
    else:
        char_part = f"character {character_input}" if character_input else ""
        actor_part = f"actor {actor_input}" if actor_input else ""
        parts = [p for p in [char_part, actor_part] if p]
    id_spec = f"featuring {primary_name}" + (f" ({', '.join(parts)})" if parts else "")
    description = f"{id_spec}, {valid_bio}, styled in {request.get('tone', 'parody')} tone."

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
