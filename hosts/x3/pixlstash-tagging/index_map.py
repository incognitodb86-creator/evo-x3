#!/usr/bin/env python3
"""Read-only actor/alias -> character mapping using the community parody INDEX.

Maps celebrity `person <Name>` names to linked `character <Character>` names
from INDEX.md / INDEX_BAD.md and aliases.json, while skipping installed OC keys
so OCs never receive celebrity character tags.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys
import threading
from typing import Iterable

_COMMUNITY_CANDIDATES = (
    Path("/home/derekboone/AI/community"),
    Path("/home/evo/AI/community"),
)
_REFMODS_CANDIDATES = (
    Path("/home/derekboone/AI/comfy-alienpc/models/refmods"),
    Path("/home/evo/AI/comfy-alienpc/models/refmods"),
)


def _pick_readable_dir(candidates: Iterable[Path]) -> Path:
    for cand in candidates:
        try:
            if cand.is_dir() and os.access(cand, os.R_OK | os.X_OK):
                return cand
        except OSError:
            continue
    raise FileNotFoundError(f"No readable directory among: {', '.join(str(c) for c in candidates)}")


def _import_parody_modules(parody_dir: Path):
    parody_str = str(parody_dir)
    if parody_str not in sys.path:
        sys.path.insert(0, parody_str)
    import resolve  # type: ignore

    return resolve, resolve


def normalize_alnum(name: str) -> str:
    """Lowercase alphanumeric normalization matching resolve._normalize_key."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def normalize_ident(name: str) -> str:
    """Lowercase space-delimited alphanumeric normalization matching _norm_ident."""
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


class IndexMapper:
    """In-memory actor/alias -> character lookup with OC exclusion."""

    def __init__(
        self,
        community_dir: Path | None = None,
        refmods_dir: Path | None = None,
    ) -> None:
        comm = community_dir or _pick_readable_dir(_COMMUNITY_CANDIDATES)
        refs = refmods_dir or _pick_readable_dir(_REFMODS_CANDIDATES)
        parody_dir = comm / "scripts" / "parody"
        index_dir = comm / "index" / "h3-known-characters"
        aliases_path = parody_dir / "aliases.json"

        resolve_mod, parody_mod = _import_parody_modules(parody_dir)
        self._index_rows = resolve_mod.load_index_files(index_dir)
        self._aliases: dict[str, str] = resolve_mod.load_aliases(aliases_path) or {}

        installed_oc = parody_mod.installed_oc_refmod_keys(refs) or {}
        trained_oc = parody_mod.trained_oc_subject_keys(refs) or {}

        oc_raw_keys = list(installed_oc.keys()) + list(trained_oc.keys())
        self._oc_alnum: set[str] = {normalize_alnum(k) for k in oc_raw_keys if normalize_alnum(k)}
        self._oc_ident: set[str] = {normalize_ident(k) for k in oc_raw_keys if normalize_ident(k)}

        self._actor_to_chars: dict[str, list[str]] = {}
        self._actor_char_seen: dict[str, set[str]] = {}
        for row in self._index_rows:
            actor = str(row.get("actor") or "").strip()
            char_name = re.sub(r"\s+", " ", str(row.get("character") or "").strip())
            if not actor or not char_name:
                continue
            actor_keys: list[str] = []
            full_key = normalize_alnum(actor)
            if full_key:
                actor_keys.append(full_key)
            if "," in actor:
                for part in actor.split(","):
                    part_key = normalize_alnum(part.strip())
                    if len(part_key) >= 3 and part_key not in actor_keys:
                        actor_keys.append(part_key)
            char_dedup = char_name.lower()
            for akey in actor_keys:
                seen = self._actor_char_seen.setdefault(akey, set())
                if char_dedup not in seen:
                    seen.add(char_dedup)
                    self._actor_to_chars.setdefault(akey, []).append(char_name)

    def is_oc_name(self, name: str) -> bool:
        an = normalize_alnum(name)
        idn = normalize_ident(name)
        if not an:
            return False
        return an in self._oc_alnum or idn in self._oc_ident

    def map_person_to_characters(self, person_name: str) -> list[str]:
        """Return linked character names for an actor/alias, or [] for OCs / unmatched."""
        an = normalize_alnum(person_name)
        if not an or self.is_oc_name(person_name):
            return []

        lookup_keys = [an]
        if an in self._aliases:
            alias_target = self._aliases[an]
            if self.is_oc_name(alias_target):
                return []
            alias_an = normalize_alnum(alias_target)
            if alias_an and alias_an not in lookup_keys:
                lookup_keys.append(alias_an)

        out: list[str] = []
        seen_chars: set[str] = set()
        for key in lookup_keys:
            for ch in self._actor_to_chars.get(key, ()):
                ch_key = ch.lower()
                if ch_key not in seen_chars:
                    seen_chars.add(ch_key)
                    out.append(ch)
        return out


_MAPPER_LOCK = threading.Lock()
_DEFAULT_MAPPER: IndexMapper | None = None


def get_mapper() -> IndexMapper:
    global _DEFAULT_MAPPER
    if _DEFAULT_MAPPER is None:
        with _MAPPER_LOCK:
            if _DEFAULT_MAPPER is None:
                _DEFAULT_MAPPER = IndexMapper()
    return _DEFAULT_MAPPER


def is_oc_name(name: str) -> bool:
    return get_mapper().is_oc_name(name)


def map_person_to_characters(person_name: str) -> list[str]:
    return get_mapper().map_person_to_characters(person_name)
