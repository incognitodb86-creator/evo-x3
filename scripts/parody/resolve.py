"""Resolver for H3 parody pipeline (U2 + U3 stills gate).

Resolves requested identities against Malcolm INDEX mirror and local RefMods,
enforcing good/bad/fence rules, slot stacking, >8 truncation, and stills gate.
FG-3: exact ``minimaxh3_<id>_v<N>_refmod`` token match + ambiguity block.
FG-9: refuse symlinks and junctions on stills.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_APPROVED_STILLS_DIR = Path(r"C:\Users\derek\5slock\approved_characters")
KD17_REFMOD_STRENGTHS: Tuple[float, float, float] = (1.0, 1.0, 0.80)

# Exact asset filename (shared with reflora.parse_ref_asset_name)
REF_ASSET_RE = re.compile(
    r"^minimaxh3_([a-z0-9]+)_v(\d+)_(refmod|reflora)\.safetensors$",
    re.IGNORECASE,
)


def _normalize_key(name: str) -> str:
    """Normalize string for case-insensitive exact matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _name_tokens(name: str) -> set:
    """Individual word tokens from a display name (fallback INDEX match)."""
    return {_normalize_key(t) for t in re.split(r"[^A-Za-z0-9]+", name) if t and _normalize_key(t)}


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_j = getattr(path, "is_junction", None)
    if callable(is_j):
        try:
            return bool(is_j())
        except OSError:
            return False
    return False


BANNED_GENERICS: Tuple[str, ...] = (
    "exact likeness",
    "distinctive facial features",
    "natural authentic human appearance",
)


def validate_biometric_description(bio: Optional[str]) -> str:
    """Validate biometric / wardrobe description against empty and generic-only inputs."""
    if bio is None:
        raise ValueError("Biometric description / bio is required: cannot be None.")

    text = str(bio).strip()
    if not text:
        raise ValueError("Biometric description / bio is required: cannot be empty or whitespace.")

    norm = re.sub(r"[^\w\s]", " ", text.lower())
    norm_words = norm.split()
    norm_clean = " ".join(norm_words)

    for banned in BANNED_GENERICS:
        banned_norm = " ".join(re.sub(r"[^\w\s]", " ", banned.lower()).split())
        if norm_clean == banned_norm:
            raise ValueError(
                f"Biometric description matches banned generic phrase alone: {text!r}. "
                "Must provide concrete biometric/wardrobe details."
            )

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
    """Parse INDEX.md and INDEX_BAD.md into a list of row dicts."""
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


def parse_ref_asset_name(filename: str) -> Optional[Tuple[str, int, str]]:
    m = REF_ASSET_RE.match(Path(filename).name)
    if not m:
        return None
    return m.group(1).lower(), int(m.group(2)), m.group(3).lower()


def find_refmods_for_name(
    norm_name: str,
    refmods_dir: Path,
    version: Optional[int] = None,
) -> List[Path]:
    """Find RefMod files whose ``<id>`` token equals ``norm_name`` exactly (FG-3).

    Raises ValueError on ambiguous multi-version / multi-id hits without an explicit pin.
    """
    if not refmods_dir.is_dir() or not norm_name:
        return []

    by_id: Dict[str, List[Tuple[int, Path]]] = {}
    for f in refmods_dir.glob("*.safetensors"):
        parsed = parse_ref_asset_name(f.name)
        if parsed is None:
            continue
        file_id, ver, kind = parsed
        if kind != "refmod":
            continue
        if file_id != norm_name:
            continue
        by_id.setdefault(file_id, []).append((ver, f))

    if not by_id:
        return []

    # Exact id equality => at most one id key
    versions = sorted(by_id[norm_name], key=lambda t: t[0])
    if version is not None:
        matched = [p for v, p in versions if v == version]
        if not matched:
            raise ValueError(
                f"no RefMod for id {norm_name!r} version v{version} under {refmods_dir}"
            )
        return matched

    distinct_vers = sorted({v for v, _ in versions})
    if len(distinct_vers) > 1:
        names = [p.name for _, p in versions]
        raise ValueError(
            f"ambiguous RefMod versions for id {norm_name!r}: {distinct_vers} "
            f"({', '.join(names)}); pin an explicit version"
        )
    return [versions[0][1]]


def match_index_rows(query: str, index_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Exact normalized character/actor match; word-token fallback blocks on ambiguity (FG-3)."""
    norm_q = _normalize_key(query)
    if not norm_q:
        return []

    exact = [
        r for r in index_rows
        if norm_q == _normalize_key(r["character"]) or norm_q == _normalize_key(r["actor"])
    ]
    if exact:
        return exact

    hits: List[Dict[str, Any]] = []
    for r in index_rows:
        tokens = _name_tokens(r["character"]) | _name_tokens(r["actor"])
        if norm_q in tokens:
            hits.append(r)

    # Distinct rows by (character, actor)
    uniq: List[Dict[str, Any]] = []
    seen = set()
    for r in hits:
        key = (_normalize_key(r["character"]), _normalize_key(r["actor"]))
        if key not in seen:
            seen.add(key)
            uniq.append(r)

    if len(uniq) > 1:
        labels = [f"{r['character']} / {r['actor']}" for r in uniq[:8]]
        raise ValueError(
            f"ambiguous INDEX match for {query!r}: {len(uniq)} rows ({', '.join(labels)}"
            f"{'...' if len(uniq) > 8 else ''}); use the full character or actor name"
        )
    return uniq


def validate_stills(stills: List[str], approved_dir: Optional[Path]) -> List[str]:
    """Validate still image paths against approved pool and security constraints.

    Enforces:
    - Rejection of any path referencing Sydney (FP-10).
    - Containment within approved_characters pool (U3 / KD10).
    - Non-symlink / non-junction (FG-9).
    """
    valid_paths: List[str] = []
    if not stills:
        return valid_paths

    pool_dir = DEFAULT_APPROVED_STILLS_DIR if approved_dir is None else Path(approved_dir)
    if _is_link_or_junction(pool_dir):
        raise ValueError(f"Approved stills pool is a symlink/junction (refused): {pool_dir}")
    app_dir_res = pool_dir.resolve()
    for s in stills:
        raw = Path(s)
        if _is_link_or_junction(raw):
            raise ValueError(f"Still path is a symlink/junction (refused): {s}")
        # Sydney isolation: check the raw string before resolve
        if "sydney" in str(raw).lower() or raw.name.upper() == "SYDNEY":
            raise ValueError(f"Sydney paths are strictly prohibited: {s}")
        p = raw.resolve()
        if "sydney" in str(p).lower() or p.name.upper() == "SYDNEY":
            raise ValueError(f"Sydney paths are strictly prohibited: {s}")
        if _is_link_or_junction(p):
            raise ValueError(f"Still path resolves to a symlink/junction (refused): {s}")

        try:
            p.relative_to(app_dir_res)
        except ValueError:
            raise ValueError(
                f"Still path '{s}' is not within the approved_characters pool: '{pool_dir}'"
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
    reflora_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Resolve normalized request against INDEX and RefMods.

    When ``reflora_dir`` is given, matching local ``*_reflora`` hybrids are selected
    (INDEX + RefMod + RefLoRA); absent hybrids keep the INDEX + RefMod fallback; a present
    but invalid hybrid raises (RefLoRA arm R8 / KTD4).
    """
    index_rows = load_index_files(index_dir)
    aliases = load_aliases(aliases_path)

    validated_stills = validate_stills(request.get("stills", []), approved_stills_dir)

    names = request.get("names", [])
    character_input = request.get("character")
    actor_input = request.get("actor")
    version_pin = request.get("refmod_version")  # optional int

    candidates: List[str] = []
    for n in names:
        if n not in candidates:
            candidates.append(n)
    if character_input and character_input not in candidates:
        candidates.append(character_input)
    if actor_input and actor_input not in candidates:
        candidates.append(actor_input)

    expanded_candidates: List[Tuple[str, str]] = []
    for c in candidates:
        norm_c = _normalize_key(c)
        expanded_candidates.append((c, "character" if c == character_input else "query"))
        if norm_c in aliases:
            resolved_actor = aliases[norm_c]
            if resolved_actor not in [ec[0] for ec in expanded_candidates]:
                expanded_candidates.append((resolved_actor, "actor"))

    matched_index_rows: List[Dict[str, Any]] = []
    for c_name, role in list(expanded_candidates):
        rows = match_index_rows(c_name, index_rows)
        for r in rows:
            if r not in matched_index_rows:
                matched_index_rows.append(r)
                if r["actor"] and r["actor"] != r["character"]:
                    actor_cand = (r["actor"], "actor")
                    if actor_cand not in expanded_candidates:
                        expanded_candidates.append(actor_cand)

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

    if best_status == "good":
        mode = "native_face_voice"
    elif best_status in ("bad", "onthefence"):
        mode = "native_voice_refmod_look"
    else:
        mode = "native_voice_refmod_look"

    matched_refmods: List[Tuple[Path, str, str]] = []
    for c_name, role in expanded_candidates:
        norm_c = _normalize_key(c_name)
        c_status = "bad"
        for r in matched_index_rows:
            if norm_c == _normalize_key(r["character"]) or norm_c == _normalize_key(r["actor"]):
                c_status = r["status"]
                break

        files = find_refmods_for_name(norm_c, refmods_dir, version=version_pin)
        for f in files:
            if not any(f == m[0] for m in matched_refmods):
                matched_refmods.append((f, role, c_status))

    def _refmod_sort_key(item: Tuple[Path, str, str]) -> Tuple[int, int]:
        role_weight = 1 if item[1] == "character" else 0
        stat_weight = status_priority.get(item[2], 0)
        return (role_weight, stat_weight)

    sorted_refmods = sorted(matched_refmods, key=_refmod_sort_key, reverse=True)
    kept_refmods = sorted_refmods[:8]
    dropped_refmods = sorted_refmods[8:]

    if reflora_dir is not None:
        from reflora import select_reflora
        reflora = select_reflora([str(m[0]) for m in kept_refmods], Path(reflora_dir))
        keep_set = set(reflora["standalone_kept"])
        budget_drop = set(reflora["standalone_dropped_for_budget"])
        dropped_refmods = dropped_refmods + [m for m in kept_refmods if str(m[0]) in budget_drop]
        kept_refmods = [m for m in kept_refmods if str(m[0]) in keep_set]
    else:
        reflora = {"enabled": False, "hybrids": [], "fallback_reason": "reflora lookup not requested"}

    slots: Dict[str, Dict[str, Any]] = {}
    for i in range(1, 9):
        slot_key = f"mod_{i}"
        if i - 1 < len(kept_refmods):
            rf_path, _, _ = kept_refmods[i - 1]
            strength = KD17_REFMOD_STRENGTHS[min(i - 1, len(KD17_REFMOD_STRENGTHS) - 1)]
            slots[slot_key] = {"path": str(rf_path), "strength": strength, "copies": 1}
        else:
            slots[slot_key] = {"path": "(none)", "strength": 1.0, "copies": 1}

    raw_bio = request.get("description") or request.get("bio")
    valid_bio = validate_biometric_description(raw_bio)

    primary_name = candidates[0] if candidates else "subject"
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
        "reflora": reflora,
        "identity_layers": ["INDEX"] + (["RefMod"] if (kept_refmods or reflora.get("enabled")) else []) + (["RefLoRA"] if reflora.get("enabled") else []),
    }
