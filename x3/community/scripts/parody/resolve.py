"""Resolver for H3 parody pipeline (U2 + U3 stills gate).

Resolves requested identities against Malcolm INDEX mirror and local RefMods,
enforcing good/bad/fence rules, slot stacking, >8 truncation, and stills gate.
"""

from __future__ import annotations

import json
from pathlib import Path
import os
# AI root (/home/evo/AI). Not resolve(): after the mono switchover the part folders are symlinks into the mono clone (S1b).
_AI_ROOT = Path(os.environ.get("EVO_AI_ROOT") or ("/home/evo/AI" if os.path.isdir("/home/evo/AI") else Path(__file__).resolve().parents[3]))
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

DEFAULT_APPROVED_STILLS_DIR = _AI_ROOT / "5slock" / "approved_characters"
RENDER_APPROVED_STILLS_DIR = _AI_ROOT / "render" / "stills" / "approved_characters"
_HOME_RENDER_APPROVED_STILLS_DIR = Path("~/AI/render/stills/approved_characters").expanduser()
KD17_REFMOD_STRENGTHS: Tuple[float, float, float] = (1.0, 1.0, 0.80)
NAS_APPROVED_STILLS_DIR = Path(r"\\NAS4CBE37.local\home\AlienPc-approved\approved_characters")
# PixlStash vault.db lives in 5slock/libraries and every picture file_path is relative to it.
PIXLSTASH_IMAGES_DIR = _AI_ROOT / "5slock" / "libraries"
GROK_FLOW_LIBRARIES_DIR = _AI_ROOT / "5slock" / "libraries"
APPROVED_IMAGE_POOLS: Tuple[Path, ...] = tuple(
    dict.fromkeys((
        DEFAULT_APPROVED_STILLS_DIR,
        RENDER_APPROVED_STILLS_DIR,
        _HOME_RENDER_APPROVED_STILLS_DIR,
        NAS_APPROVED_STILLS_DIR,
        # Derrick Nov 12 + "yes change it wtf" (Alfred t520u, Nov 16 2026): PixlStash catalog and
        # Grok/Flow exports are acceptable stills. Only the 18+ check applies (t2086u).
        PIXLSTASH_IMAGES_DIR,
        GROK_FLOW_LIBRARIES_DIR,
    ))
)
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


_REFMOD_SUBJECT_RE = re.compile(r"^minimaxh3_(?:oc_)?(.+?)_v\d+(?:_|$)")


def find_refmods_for_name(norm_name: str, refmods_dir: Path) -> List[Path]:
    """Find local .safetensors RefMod files matching a normalized name.

    A file matches exactly when the name equals a leading run of its underscore tokens, so "testachar" keeps both
    minimaxh3_testachar_v1_refmod and the variant minimaxh3_testachar_alt_v1_refmod (KD17 stacking), and
    "gabrielleaplin" matches minimaxh3_gabrielle_aplin_v1_refmod, while a short name like "ava" never matches
    "avaaddams". Substring matching is only a fallback for names of 6+ characters when nothing matched exactly.
    """
    exact: List[Path] = []
    partial: List[Path] = []
    if not norm_name or not refmods_dir.is_dir():
        return exact

    for f in sorted(refmods_dir.glob("*.safetensors")):
        fname_norm = _normalize_key(f.stem)
        m = _REFMOD_SUBJECT_RE.match(f.stem.lower())
        tokens = [_normalize_key(t) for t in m.group(1).split("_")] if m else []
        prefixes = {"".join(tokens[:k]) for k in range(1, len(tokens) + 1)}
        if norm_name in prefixes or fname_norm == norm_name:
            exact.append(f)
        elif len(norm_name) >= 6 and norm_name in ("".join(tokens) or fname_norm):
            partial.append(f)
    return exact if exact else partial


def validate_stills(stills: List[str], approved_dir: Optional[Path]) -> List[str]:
    """Validate still image paths against approved pool and security constraints.

    Enforces:
    - Containment within approved_characters pool (U3 / KD10).

    Args:
        stills: List of still image file path strings.
        approved_dir: Approved characters pool directory. None uses DEFAULT_APPROVED_STILLS_DIR.

    Returns:
        List of validated resolved path strings.

    Raises:
        ValueError: If a still file does not exist.
    """
    valid_paths: List[str] = []
    if not stills:
        return valid_paths

    pool_dir = DEFAULT_APPROVED_STILLS_DIR if approved_dir is None else approved_dir
    app_dir_res = pool_dir.resolve()
    for s in stills:
        p = Path(s).resolve()
        # Sydney path block dropped (Derrick t2084u, Nov 16 2026).

        # Pool containment dropped (Derrick t2086u, Nov 16 2026): the only policy check is 18+.
        if not p.is_file():
            raise ValueError(f"Still file does not exist: {s}")

        valid_paths.append(str(p))

    return valid_paths


def validate_reference_images(
    images: Optional[List[str]],
    pools: Optional[Tuple[Path, ...]] = None,
) -> List[str]:
    """U2: --image gate (LANE_IMAGE_RULES.md). Image paths must exist; bare names are looked up in the pools.

    Accepts a full path, or a sub-path / filename relative to a pool. Rejects > 4 images
    (MAX_REFERENCE_IMAGES), missing files, and non-image extensions.
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
        cand = Path(raw).expanduser() if raw.startswith("~") else Path(raw)
        tries = [cand] if cand.is_absolute() or str(cand).startswith("\\\\") else [pl / cand for pl in pool_list]
        found = None
        for t in tries:
            try:
                rp = t.resolve()
            except OSError:
                continue
            # Pool containment dropped (Derrick t2086u): any existing image path is accepted;
            # bare names are still looked up inside the pools for convenience.
            if rp.is_file():
                found = rp
                break
        if found is None:
            raise ValueError(f"--image '{raw}' not found (absolute path, or name inside a pool)")
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

    # 3. Match against INDEX rows (exact matches sort ahead of substring matches so "Fox" / "Megan Fox" never picks "Jamie Foxx" first)
    exact_index_rows: List[Dict[str, Any]] = []
    partial_index_rows: List[Dict[str, Any]] = []
    for c_name, role in expanded_candidates:
        norm_c = _normalize_key(c_name)
        if not norm_c:
            continue
        for r in index_rows:
            norm_char = _normalize_key(r["character"])
            norm_act = _normalize_key(r["actor"])
            is_exact = (norm_c == norm_char or norm_c == norm_act)
            is_sub = (not is_exact and len(norm_c) >= 5 and (norm_c in norm_char or norm_c in norm_act))
            if is_exact or is_sub:
                bucket = exact_index_rows if is_exact else partial_index_rows
                if r not in exact_index_rows and r not in partial_index_rows:
                    bucket.append(r)
                    # If matched character, also add its actor if not present
                    if r["actor"] and r["actor"] != r["character"]:
                        actor_cand = (r["actor"], "actor")
                        if actor_cand not in expanded_candidates:
                            expanded_candidates.append(actor_cand)
    matched_index_rows: List[Dict[str, Any]] = exact_index_rows + [r for r in partial_index_rows if r not in exact_index_rows]

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


# --- OC / INDEX / PixlStash RefMod picker (moved from submit_parody_run.py in U55) ---
_PARODY_DIR = Path(__file__).resolve().parent
_REPO_AI_ROOT = _PARODY_DIR.parents[2]
INDEX_DIR = _REPO_AI_ROOT / "community" / "index" / "h3-known-characters"


def _resolve_refmods_dir() -> Path:
    """Resolve the host's H3 RefMods directory without falling back to a missing repo-relative path."""
    env_dir = os.environ.get("H3_REFMODS_DIR")
    if env_dir:
        return Path(env_dir)
    if os.name == "nt":
        candidates = [
            Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods"),
            Path(r"C:\AI\comfy-alienpc\models\refmods"),
        ]
    else:
        candidates = []
        if os.environ.get("EVO_AI_ROOT"):
            candidates.append(Path(os.environ["EVO_AI_ROOT"]) / "comfy-alienpc" / "models" / "refmods")
        candidates.extend([
            Path("/home/evo/AI/comfy-alienpc/models/refmods"),
            Path.home() / "AI" / "comfy-alienpc" / "models" / "refmods",
            _REPO_AI_ROOT / "comfy-alienpc" / "models" / "refmods",
        ])
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def check_refmods_dir(refmods_dir: Optional[Path] = None) -> Path:
    """Raise a clear host-aware error if the H3 RefMods directory is missing."""
    d = Path(refmods_dir or REFMODS_DIR)
    if not d.is_dir():
        raise FileNotFoundError(f"H3 REFMODS_DIR missing on host ({os.name}): {d}")
    return d


REFMODS_DIR = _resolve_refmods_dir()
ALIASES_PATH = _PARODY_DIR / "aliases.json"
_CONTINUATION_VOICE_SUFFIX = "_23s"
def _mod_stem(value: str) -> str:
    v = Path(str(value)).name
    return v[:-12] if v.lower().endswith(".safetensors") else v



_OC_KEY_RE = re.compile(r"(?i)minimaxh3_oc_([^_]+)_")
_OC_VER_RE = re.compile(r"(?i)_v(\d+)_")


def _keep_highest_oc_version(stems: Sequence[str]) -> List[str]:
    """When multiple versions (v1, v2) of the same OC key appear in stems, keep only the highest version.

    A voice RefMod trimmed to fit a continuation beat's cond_audio cap (`<name>_23s`,
    build_request.CONTINUATION_VOICE_REFMOD_SUFFIX) is a DERIVED copy of a reference that exists in full form:
    build_request._continuation_voice_refmods wires it on one continuation beat from that beat's own layout.
    It is never a character's voice reference for a base beat - two audio RefMods there pack
    2*(1000+920)=3840 rows against the 2000 a voice reference carries, the over-cap family of the live c2_samp
    failure (2026-11-15, [2000,32] vs [2130,32]). So a trim is dropped exactly when the file it was cut from is
    in the same list; a list with only a trim keeps it (a character whose full reference is not installed).
    """
    max_ver: Dict[str, int] = {}
    for s in stems:
        m = _OC_KEY_RE.search(s)
        if m:
            vm = _OC_VER_RE.search(s)
            ver = int(vm.group(1)) if vm else 0
            k = m.group(1).lower()
            if ver > max_ver.get(k, -1):
                max_ver[k] = ver
    out: List[str] = []
    for s in stems:
        m = _OC_KEY_RE.search(s)
        if m:
            vm = _OC_VER_RE.search(s)
            ver = int(vm.group(1)) if vm else 0
            k = m.group(1).lower()
            if ver < max_ver.get(k, 0):
                continue
        out.append(s)
    trim = _CONTINUATION_VOICE_SUFFIX
    drop = {s for s in out if str(s).endswith(trim) and str(s)[: -len(trim)] in out}
    return [s for s in out if s not in drop]


def installed_oc_refmod_keys(refmods_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Map oc_* keys (poolclub, poolblonde) to installed RefMod stems (highest v<N> pair per key)."""
    d = Path(refmods_dir or REFMODS_DIR)
    keys: Dict[str, List[str]] = {}
    if not d.is_dir():
        return keys
    for f in sorted(d.glob("*.safetensors")):
        m = _OC_KEY_RE.search(f.stem)
        if m:
            keys.setdefault(m.group(1).lower(), []).append(f.stem)
    for k, stems in list(keys.items()):
        keys[k] = _keep_highest_oc_version(stems)
    return keys


def oc_keys_in_text(*parts: Optional[str]) -> List[str]:
    blob = " ".join(p for p in parts if p).replace("\\", "/").lower()
    if not blob:
        return []
    found: List[str] = []
    for k in installed_oc_refmod_keys():
        token = r"(?:^|[/_\s-])%s(?:[/_\s-]|$)"
        if re.search(r"(?i)" + (token % ("oc[_-]?" + re.escape(k))), blob) or re.search(
            r"(?i)" + (token % re.escape(k)), blob
        ):
            found.append(k)
    return found



# Exact path components (case-insensitive) that resolve to an OC key.
# Not substring matches. Do not alias SYDNEY or ORC_POOL_EDGE.
_OC_PATH_COMPONENT_ALIASES = {
    "pool": "poolclub",  # approved_characters\POOL -> trained trigger FCSydny
    "fcmegan": "meganfox",  # approved_characters\FCMegan -> minimaxh3_meganfox_v1_refmod
}

_PIXLSTASH_VAULTS = (
    _AI_ROOT / "5slock" / "libraries" / "vault.db",
)
_STILL_LIBRARY_ROOTS = (
    _AI_ROOT / "render" / "stills" / "approved_characters",
    _AI_ROOT / "5slock" / "libraries",
)


def _norm_fs(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lower()


def _still_path_parts(still_image: Optional[str]) -> List[str]:
    if not still_image:
        return []
    rel = _norm_fs(still_image)
    roots = [
        *(str(r) for r in _STILL_LIBRARY_ROOTS),
        "/home/evo/ai/render/stills/approved_characters",
        "/home/evo/ai/5slock/libraries",
        "/home/derekboone/ai/render/stills/approved_characters",
        "/home/derekboone/ai/5slock/libraries",
    ]
    for root in roots:
        prefix = _norm_fs(root).rstrip("/") + "/"
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    return [p for p in rel.split("/") if p]


def _safetensors_metadata(path: Path) -> Dict[str, Any]:
    """Read the safetensors JSON header only (no tensor load)."""
    try:
        with path.open("rb") as f:
            n = int.from_bytes(f.read(8), "little")
            if n <= 0 or n > 4_000_000:
                return {}
            raw = f.read(n)
        header = json.loads(raw.decode("utf-8"))
        meta = header.get("__metadata__") or {}
        if not isinstance(meta, dict):
            return {}
        out: Dict[str, Any] = {}
        for k, v in meta.items():
            if isinstance(v, str):
                try:
                    out[k] = json.loads(v)
                except Exception:
                    out[k] = v
            else:
                out[k] = v
        return out
    except Exception:
        return {}


def trained_oc_subject_keys(refmods_dir: Optional[Path] = None) -> Dict[str, str]:
    """Map a normalized trained subject_name (e.g. fcsydny) to an OC key (poolclub).

    Prefers top-level subject_name over nested refmod_meta.subject_name.
    """
    d = Path(refmods_dir or REFMODS_DIR)
    mapping: Dict[str, str] = {}
    if not d.is_dir():
        return mapping
    for f in d.glob("minimaxh3_oc_*_refmod_visual.safetensors"):
        m = _OC_KEY_RE.search(f.stem)
        if not m:
            continue
        key = m.group(1).lower()
        meta = _safetensors_metadata(f)
        top = meta.get("subject_name")
        if not isinstance(top, str):
            top = ""
        nested = ""
        rm = meta.get("refmod_meta")
        if isinstance(rm, dict):
            nested = rm.get("subject_name") or ""
        if not isinstance(nested, str):
            nested = ""
        subject = (top.strip() or nested.strip())
        if subject:
            mapping[_norm_ident(subject)] = key
    return mapping


def oc_keys_from_path_components(still_image: Optional[str]) -> List[str]:
    found: List[str] = []
    for part in _still_path_parts(still_image):
        alias = _OC_PATH_COMPONENT_ALIASES.get(part.lower())
        if alias and alias not in found:
            found.append(alias)
    return found


def pixlstash_character_names_for_still(still_image: Optional[str]) -> List[str]:
    """PixlStash character names tagged on this still. Empty if the vault is missing."""
    if not still_image:
        return []
    rel = "/".join(_still_path_parts(still_image))
    candidates = {_norm_fs(still_image)}
    try:
        resolved = Path(still_image)
        if resolved.exists():
            candidates.add(_norm_fs(str(resolved.resolve())))
    except Exception:
        pass
    if rel:
        for root in _STILL_LIBRARY_ROOTS:
            candidates.add(_norm_fs(str(root / rel)))
        candidates.add(_norm_fs(rel))
    names: List[str] = []
    import sqlite3
    base_name = Path(_norm_fs(still_image)).name.lower()
    rel_low = rel.lower()
    for vault in _PIXLSTASH_VAULTS:
        if not vault.is_file():
            continue
        try:
            con = sqlite3.connect("file:%s?mode=ro" % vault.as_posix(), uri=True)
            cur = con.cursor()
            if rel_low and base_name:
                rows = cur.execute(
                    """
                    SELECT c.name, p.file_path
                    FROM face f
                    JOIN character c ON c.id = f.character_id
                    JOIN picture p ON p.id = f.picture_id
                    WHERE f.character_id IS NOT NULL
                      AND (LOWER(REPLACE(p.file_path, char(92), '/')) = ?
                           OR LOWER(REPLACE(p.file_path, char(92), '/')) LIKE ?
                           OR LOWER(p.file_path) LIKE ?)
                    """,
                    (rel_low, "%/" + rel_low, "%" + base_name),
                ).fetchall()
            elif base_name:
                rows = cur.execute(
                    """
                    SELECT c.name, p.file_path
                    FROM face f
                    JOIN character c ON c.id = f.character_id
                    JOIN picture p ON p.id = f.picture_id
                    WHERE f.character_id IS NOT NULL
                      AND (p.file_path = ? OR LOWER(p.file_path) LIKE ?)
                    """,
                    (rel, "%" + base_name),
                ).fetchall()
            else:
                rows = []
            con.close()
        except Exception:
            continue
        for name, fpath in rows:
            if not name:
                continue
            fp = _norm_fs(fpath)
            if fp in candidates or (rel and (fp.endswith("/" + rel.lower()) or fp == rel.lower())):
                if name not in names:
                    names.append(name)
        if names:
            return names
    return names


def oc_keys_from_trained_subjects(*names: Optional[str]) -> List[str]:
    mapping = trained_oc_subject_keys()
    if not mapping:
        return []
    found: List[str] = []
    for name in names:
        if not name:
            continue
        key = mapping.get(_norm_ident(name))
        if key and key not in found:
            found.append(key)
    return found


def oc_keys_for_still_and_names(still_image: Optional[str] = None, *name_parts: Optional[str]) -> List[str]:
    """OC keys from path tokens, the POOL folder alias, trained triggers, and PixlStash tags."""
    found: List[str] = []

    def add(keys: List[str]) -> None:
        for k in keys:
            if k and k not in found:
                found.append(k)

    add(oc_keys_in_text(still_image, *name_parts))
    add(oc_keys_from_path_components(still_image))
    add(oc_keys_from_trained_subjects(*name_parts))
    mapping = trained_oc_subject_keys()
    if mapping:
        for part in _still_path_parts(still_image):
            for token in (part, Path(part).stem):
                key = mapping.get(_norm_ident(token))
                if key and key not in found:
                    found.append(key)
    add(oc_keys_from_trained_subjects(*pixlstash_character_names_for_still(still_image)))
    return found


def _is_writer_lane_refmod(stem: str) -> bool:
    return bool(_mod_stem(stem))


def _stems_for_character_name(name: str) -> List[str]:
    if not (name or "").strip():
        return []
    norm_q = re.sub(r"[^a-z0-9]", "", name.lower())
    files = (find_refmods_for_name(norm_q, REFMODS_DIR) or []) if norm_q else []
    if not files and norm_q:
        alias_target = _OC_PATH_COMPONENT_ALIASES.get(norm_q) or (load_aliases(ALIASES_PATH) or {}).get(norm_q)
        if alias_target:
            alias_norm = re.sub(r"[^a-z0-9]", "", alias_target.lower())
            files = (find_refmods_for_name(alias_norm, REFMODS_DIR) or []) if alias_norm else []
    stems = [_mod_stem(getattr(f, "stem", f)) for f in files]
    key = trained_oc_subject_keys().get(_norm_ident(name))
    if key:
        for s in installed_oc_refmod_keys().get(key, []):
            if s not in stems:
                stems.append(s)
    return _keep_highest_oc_version(stems)



def _norm_ident(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _name_matches_field(name: str, field: str) -> bool:
    n, f = _norm_ident(name), _norm_ident(field)
    if not n or not f:
        return False
    if n == f:
        return True
    # Token match, but skip short fragments ("the", "of").
    return n in f.split() and len(n) >= 4


def is_oc_name(name: Optional[str]) -> bool:
    """True for an OC (FCSydny, FCMegan, an installed oc_* key or trained OC subject), never a named INDEX parody."""
    n = (name or "").strip()
    if not n:
        return False
    return bool(re.match(r"(?i)^fc[a-z0-9_]{3,}$", n)) or _norm_ident(n) in installed_oc_refmod_keys() or _norm_ident(n) in trained_oc_subject_keys()


def _is_voice_refmod(stem: str) -> bool:
    return "_refmod_audio" in _mod_stem(str(stem)).lower()


def index_named_identity(name: Optional[str]) -> bool:
    """True when the name is a character INDEX or aliases entry, not an installed OC key."""
    if not (name or "").strip():
        return False
    n = _norm_ident(name)
    if n in installed_oc_refmod_keys() or n in trained_oc_subject_keys():
        return False
    try:
        aliases = load_aliases(ALIASES_PATH) or {}
        for k, v in aliases.items():
            if _name_matches_field(n, k) or _name_matches_field(n, v):
                return True
        for row in load_index_files(INDEX_DIR) or []:
            if _name_matches_field(n, str(row.get("character") or "")) or _name_matches_field(n, str(row.get("actor") or "")):
                return True
    except Exception:
        return False
    return False


def resolve_writer_refmods(
    still_image: Optional[str] = None,
    character: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Pick installed visual/audio RefMods for the writer hook across OC, INDEX, and PixlStash tags.

    Uses aliases + INDEX + local RefMod files (all adult RefMods and voice refs allowed), trained
    RefMod triggers (e.g. FCSydny), PixlStash character tags, or approved POOL path components.
    Never guesses a likeness from a bare still filename, and never reuses the previous run's RefMods.
    Stills are not passed to validate_stills (writer stills may live outside approved_characters).
    """
    out: Dict[str, Any] = {"stems": [], "source": None, "reason": None, "index": None, "trigger": None}
    char = (character or "").strip() or None
    name_list = [n for n in (list(names) if names else []) if str(n).strip()]

    def _oc_trigger(stems: Sequence[str]) -> Optional[str]:
        """The trained RefMod trigger word (e.g. FCSydny) of the visual RefMod just attached, from its own
        safetensors subject_name. Only for minimaxh3_oc_* files; None for INDEX/celebrity RefMods."""
        d = Path(REFMODS_DIR)
        for s in stems:
            stem = _mod_stem(str(s))
            if not re.search(r"(?i)^minimaxh3_oc_", stem):
                continue
            f = d / (stem + ".safetensors")
            if not f.is_file():
                continue
            subj = _safetensors_metadata(f).get("subject_name")
            if isinstance(subj, str) and subj.strip():
                return subj.strip()
        return None

    def _resolve_names(targets: Sequence[str]) -> List[str]:
        found: List[str] = []
        seen: set = set()
        for n in targets:
            for s in _stems_for_character_name(str(n)):
                if _is_voice_refmod(s) and not is_oc_name(str(n)):  # U56: named parodies carry no voice ref
                    continue
                if _is_writer_lane_refmod(s) and s not in seen:
                    seen.add(s)
                    found.append(s)
        try:
            tlist = [str(n).strip() for n in targets if str(n).strip()]
            req = {
                "names": tlist,
                "character": tlist[0] if tlist else "",
                "actor": "",
                "tone": "",
                "length_s": 10,
                "description": "adult figure with eyes, hair, and outfit",
            }
            resolved = resolve_identities(req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
            loaded = [_mod_stem(x) for x in (resolved.get("loaded_refmods") or [])]
            if not any(is_oc_name(str(n)) for n in tlist):  # U56: named parodies carry no voice ref
                loaded = [x for x in loaded if not _is_voice_refmod(x)]
            out["index"] = {
                "index_status": resolved.get("index_status"),
                "index_flag": resolved.get("index_flag"),
                "loaded": loaded,
            }
            for s in loaded:
                if _is_writer_lane_refmod(s) and s not in seen:
                    seen.add(s)
                    found.append(s)
        except Exception as e:
            out["index_error"] = f"{type(e).__name__}: {e}"
        return _keep_highest_oc_version(found)

    if char or name_list:
        targets = ([char] if char else []) + [n for n in name_list if n != char]
        matched = _resolve_names(targets)
        if matched:
            out["stems"] = matched
            out["source"] = "character"
            out["trigger"] = _oc_trigger(matched)
            return out
        who = char or (name_list[0] if name_list else "named identity")
        if not Path(REFMODS_DIR).is_dir():
            out["reason"] = f"missing H3 REFMODS_DIR on host ({os.name}): {REFMODS_DIR}"
        else:
            out["reason"] = f"no local RefMod installed for '{who}' in {REFMODS_DIR}"
        return out

    keys = oc_keys_for_still_and_names(still_image, char, " ".join(str(n) for n in name_list))
    if keys:
        inst = installed_oc_refmod_keys()
        stems: List[str] = []
        seen: set = set()
        for k in keys:
            for s in inst.get(k, []):
                if s not in seen:
                    seen.add(s)
                    stems.append(s)
            if not inst.get(k):
                for s in _stems_for_character_name(k):
                    if _is_writer_lane_refmod(s) and s not in seen:
                        seen.add(s)
                        stems.append(s)
        if stems:
            out["stems"] = _keep_highest_oc_version(stems)
            out["source"] = "still_path"
            out["trigger"] = _oc_trigger(out["stems"])
            return out

    tagged = pixlstash_character_names_for_still(still_image)
    if tagged:
        matched = _resolve_names(tagged)
        if matched:
            out["stems"] = matched
            out["source"] = "pixlstash"
            out["trigger"] = _oc_trigger(matched)
            return out

    still_id = detect_still_identity(still_image)
    if still_id.get("names"):
        matched = _resolve_names(still_id["names"])
        if matched:
            out["stems"] = matched
            out["source"] = still_id.get("source") or "still_meta"
            out["trigger"] = _oc_trigger(matched)
            return out

    out["reason"] = (
        "no RefMod matched this still via installed files, the trained trigger, "
        "the POOL folder, a PixlStash character tag, or the character name; "
        "will not reuse the previous run's RefMods. Pass a still tagged or filed as the character "
        "(for example FCSydny / poolclub or poolblonde), or pass --character <name>."
    )
    return out


# --- Flux / ComfyUI PNG metadata & sidecar identity handoff to H3Max ---
_NON_IDENTITY_FLUX_LORA_RE = re.compile(
    r"(?i)(?:refcontrol|bfs_head|ms_real|snofs|tripleview|quadview|realism|stomach_bulge|anatomy|consistency|turbo|detail)"
)


def extract_comfy_png_prompt(still_image: Optional[str]) -> Optional[Dict[str, Any]]:
    """Read ComfyUI's embedded workflow JSON from a PNG `prompt` text chunk (pure stdlib, no PIL required)."""
    if not still_image:
        return None
    p = Path(still_image)
    if not p.is_file() or p.suffix.lower() != ".png":
        return None
    try:
        import struct, zlib
        data = p.read_bytes()
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        pos, n = 8, len(data)
        while pos + 8 <= n:
            length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
            chunk = data[pos + 8:pos + 8 + length]
            pos += 12 + length
            if ctype == b"tEXt":
                sep = chunk.find(b"\x00")
                if sep > 0 and chunk[:sep] == b"prompt":
                    parsed = json.loads(chunk[sep + 1:].decode("utf-8", errors="replace"))
                    if isinstance(parsed, dict):
                        return parsed
            elif ctype == b"iTXt":
                sep = chunk.find(b"\x00")
                if sep > 0 and chunk[:sep] == b"prompt":
                    rest = chunk[sep + 1:]
                    if len(rest) >= 2:
                        comp_flag = rest[0]
                        # skip comp_method(1), lang\0, translated_kw\0
                        i = 2
                        for _ in range(2):
                            z = rest.find(b"\x00", i)
                            i = (z + 1) if z >= 0 else len(rest)
                        raw_txt = zlib.decompress(rest[i:]) if comp_flag == 1 else rest[i:]
                        parsed = json.loads(raw_txt.decode("utf-8", errors="replace"))
                        if isinstance(parsed, dict):
                            return parsed
            elif ctype == b"IEND":
                break
    except Exception:
        return None
    return None


def names_from_flux_refmod_or_lora(filename: Optional[str]) -> List[str]:
    """Extract a celebrity/character lookup token from a Klein9/H3 RefMod or Klein9 celeb LoRA filename."""
    if not filename:
        return []
    s = str(filename).strip().replace("\\", "/")
    if not s or s.lower() in ("(none)", "none"):
        return []
    stem = Path(s).stem
    if _NON_IDENTITY_FLUX_LORA_RE.search(stem):
        return []
    # Strip known prefixes/suffixes: klein9_, fk9_, minimaxh3_, oc_, _v1, _v2, _prodigy, _refmod, _visual, _audio
    cleaned = re.sub(r"(?i)^(?:klein9|fk9|flux2?klein9?|minimaxh3|h3)[_-]+", "", stem)
    cleaned = re.sub(r"(?i)^oc[_-]+", "", cleaned)
    cleaned = re.sub(r"(?i)(?:[_-]+(?:v\d+(?:\.\d+)?|prodigy|refmod|visual|audio|alt|lora|klein9|rank\d+|step\d+))+$", "", cleaned)
    cleaned = cleaned.strip("_- ")
    if len(cleaned) < 3:
        return []
    spaced = re.sub(r"[_-]+", " ", cleaned).strip()
    out: List[str] = [spaced]
    compact = re.sub(r"[^a-zA-Z0-9]", "", cleaned)
    if compact and compact.lower() != spaced.lower():
        out.append(compact)
    return out


def detect_still_identity(still_image: Optional[str]) -> Dict[str, Any]:
    """Detect celeb/character identity embedded in a Flux sidecar (`flux_meta.json`), ComfyUI PNG `prompt` chunk,
    or PixlStash character tag so H3Max automatically picks up the same celeb + INDEX character + visual RefMod."""
    empty: Dict[str, Any] = {
        "names": [], "character": None, "actor": None, "source": None,
        "flux_refmods": [], "flux_loras": [],
    }
    if not still_image:
        return empty
    p = Path(still_image)

    # 1. Adjacent flux_meta.json sidecar (<still>.flux_meta.json or <still_dir>/flux_meta.json)
    sidecars = [p.with_suffix(".flux_meta.json"), Path(str(p) + ".flux_meta.json"), p.parent / "flux_meta.json"]
    for sc in sidecars:
        if sc.is_file():
            try:
                meta = json.loads(sc.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(meta, dict):
                continue
            names: List[str] = []
            for k in ("character", "actor"):
                v = str(meta.get(k) or "").strip()
                if v and v not in names:
                    names.append(v)
            for n in (meta.get("names") or []):
                v = str(n or "").strip()
                if v and v not in names:
                    names.append(v)
            f_mods = [str(x).strip() for x in (meta.get("refmods") or []) if str(x or "").strip()]
            f_loras = [str(x.get("name") if isinstance(x, dict) else x).strip() for x in (meta.get("loras") or []) if x]
            for fn in f_mods + f_loras:
                for nm in names_from_flux_refmod_or_lora(fn):
                    if nm not in names:
                        names.append(nm)
            if names or f_mods or f_loras:
                return {
                    "names": names,
                    "character": str(meta.get("character") or "").strip() or None,
                    "actor": str(meta.get("actor") or "").strip() or None,
                    "source": "flux_meta",
                    "flux_refmods": f_mods,
                    "flux_loras": f_loras,
                }

    # 2. ComfyUI PNG `prompt` metadata (Klein9RefModsLoader / MiniMaxH3RefModsLoader / LoraLoaderModelOnly)
    graph = extract_comfy_png_prompt(still_image)
    if isinstance(graph, dict):
        f_mods, f_loras, names = [], [], []
        for node in graph.values():
            if not isinstance(node, dict):
                continue
            ct = str(node.get("class_type") or "")
            inp = node.get("inputs") or {}
            if ct in ("Klein9RefModsLoader", "MiniMaxH3RefModsLoader"):
                for i in range(1, 9):
                    m = str(inp.get(f"mod_{i}") or "").strip()
                    st = float(inp.get(f"strength_{i}", 1.0) or 0.0)
                    if m and m.lower() != "(none)" and st > 0:
                        f_mods.append(m)
            elif ct in ("LoraLoaderModelOnly", "LoraLoader"):
                ln = str(inp.get("lora_name") or "").strip()
                st = float(inp.get("strength_model", 1.0) or 0.0)
                if ln and ln.lower() != "(none)" and st > 0:
                    f_loras.append(ln)
        for fn in f_mods + f_loras:
            for nm in names_from_flux_refmod_or_lora(fn):
                if nm not in names:
                    names.append(nm)
        if names:
            return {
                "names": names, "character": None, "actor": None, "source": "comfy_png",
                "flux_refmods": f_mods, "flux_loras": f_loras,
            }

    # 3. PixlStash character tag (works for celebrities as well as OCs)
    tagged = pixlstash_character_names_for_still(still_image)
    if tagged:
        return {
            "names": list(tagged), "character": tagged[0], "actor": None, "source": "pixlstash",
            "flux_refmods": [], "flux_loras": [],
        }

    return empty


