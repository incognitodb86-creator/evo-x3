"""Bridge-local subject counting, oral-speech, lip-sync, and redaction helpers.

These wrap official parody validators without modifying ``build_request.py`` or ``x3/``.
"""

from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

_MALE_RE = re.compile(r"\b(?:men|man|male|he|him|his)\b", re.IGNORECASE)
_FEMALE_RE = re.compile(r"\b(?:women|woman|female|she|her|hers)\b", re.IGNORECASE)
_TWO_RE = re.compile(
    r"\b(?:two (?:adults|people|persons|figures)|a (?:woman|man) and an? (?:man|woman)|couple)\b",
    re.IGNORECASE,
)
_AUDIO_REF_RE = re.compile(
    r"(?i)(?:^|[_\s./-])(?:audio|voice|vocal)s?(?:$|[_\s./-])"
)
_AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
_FEMALE_NAMES = frozenset({"alice", "ada", "emma", "sydney", "sydny"})
_MALE_NAMES = frozenset({"bob", "adam", "john", "jensen"})

# Supplement only (anatomy / euphemism). Official verb-class regex stays in build_request.
_ORAL_NOUN_RE = re.compile(
    r"\b(?:lips?|tongue|shaft|penis|oral|mouth)\b",
    re.IGNORECASE,
)
_D_BLOCK_RE = re.compile(r"<d\b[^>]*>[\s\S]*?</d>", re.IGNORECASE)
_SPEAKER_BEFORE_RE = re.compile(
    r"(?:\(S([123])\)|<Subject\s+([123])>)\s*(?:[^.<]{0,80})?$",
    re.IGNORECASE,
)
_SPEAKER_INSIDE_RE = re.compile(r"\(S([123])\)|<Subject\s+([123])>", re.IGNORECASE)
_LIPSYNC_RE = re.compile(
    r"\b(?:lip[- ]?sync\w*|mouths? the (?:line|words)|articulat\w+|"
    r"(?:lips?|mouth|jaw)\b(?:\s+\w+){0,6}\s+(?:move|moves|moving|part|parts|open|opens|sync\w*)|"
    r"(?:move|moves|moving|part|parts|open|opens)\b(?:\s+\w+){0,6}\s+(?:lips?|mouth|jaw))\b",
    re.IGNORECASE,
)
LIPSYNC_CLAUSE = "Their lips and jaw move in time with the spoken line."
FOLEY_CLOSE = (
    "Soft room tone fills the space. Fabric shifts against the bedding. "
    "A faint latch clicks down the hall."
)

_POLICY_CATEGORIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("age_play_or_minor", re.compile(r"age[- ]?play|minors?|underage", re.I)),
    ("age_numeral", re.compile(r"18\+", re.I)),
    ("likeness_or_celebrity", re.compile(r"real[- ]person|likeness|celebrity", re.I)),
    ("index_voice", re.compile(r"INDEX voice", re.I)),
    ("adults_only_disclaimer", re.compile(r"adults? only|all adults", re.I)),
    ("rule_code", re.compile(r"\bR\d{1,2}\b|rule\s+R\d{1,2}|h3-prompting", re.I)),
    ("guardrail_or_policy", re.compile(
        r"(?:safety|adults?|content|system)\s+guards?|guardrails?|content\s+policy|"
        r"safety\s+policy|the\s+policy|(?:safety|content)\s+rules?",
        re.I,
    )),
    ("meta_prompt", re.compile(
        r"prompt\s+rules?|(?:the|this)\s+prompt|prompt\s+(?:maintains|complies|adheres|format|rule|instructions?)",
        re.I,
    )),
    ("timestamps", re.compile(r"timestamps?", re.I)),
)


def is_audio_refmod(subject: str, file: str) -> bool:
    name = Path(file).name
    if Path(file).suffix.lower() in _AUDIO_SUFFIXES:
        return True
    return bool(_AUDIO_REF_RE.search(subject) or _AUDIO_REF_RE.search(name))


def default_lint_ctx(*, clip_seconds: float | None = None) -> dict[str, Any]:
    """Always-non-None lint context so convert/validate never run without one."""
    slots: dict[str, Any] = {}
    if clip_seconds is not None:
        slots["clip_seconds"] = clip_seconds
    return {
        "cfg": {},
        "ask": "compile a MiniMax-H3 10Eros-Max Beta 7 prompt",
        "cast": {},
        "kind": "talk",
        "clip_seconds": clip_seconds,
        "slots": slots,
    }


def policy_word_category(text: str) -> str:
    blob = text or ""
    for name, pat in _POLICY_CATEGORIES:
        if pat.search(blob):
            return name
    return "policy_word_other"


def redact_validation(validation: dict[str, Any] | None) -> dict[str, Any]:
    """Copy a validation report, replacing phrase notes with code/category only."""
    src = dict(validation or {})
    redacted: list[dict[str, Any]] = []
    categories: list[str] = []
    for item in src.get("violations") or []:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "")
        row: dict[str, Any] = {"code": code}
        if code == "policy_word":
            cat = policy_word_category(str(item.get("note") or ""))
            row["category"] = cat
            categories.append(cat)
        elif code.startswith("wp_lint:"):
            row["lint_code"] = code.split(":", 1)[-1]
        redacted.append(row)
    out = {
        "status": src.get("status"),
        "header_violations": list(src.get("header_violations") or []),
        "violations": redacted,
        "codes": [v["code"] for v in redacted],
        "policy_word_categories": categories,
        "not_ready_reason": src.get("not_ready_reason"),
        "lint_ran": src.get("lint") is not None,
    }
    return out


def shot_text_blob(shot: dict[str, Any]) -> str:
    parts: list[str] = []
    vlm = shot.get("vlm") if isinstance(shot.get("vlm"), dict) else {}
    perf = vlm.get("performance") if isinstance((vlm or {}).get("performance"), dict) else {}
    review = shot.get("review") if isinstance(shot.get("review"), dict) else {}
    for value in (
        shot.get("description"),
        (vlm or {}).get("description"),
        (vlm or {}).get("en"),
        (perf or {}).get("en"),
        (review or {}).get("description"),
        shot.get("who"),
        (vlm or {}).get("who"),
    ):
        if value:
            parts.append(str(value))
    return " ".join(parts)


def count_onscreen_people(shot: dict[str, Any]) -> dict[str, Any]:
    """Count people from VLM/description language. ``layers_n`` and ``faces`` are not head counts."""
    blob = shot_text_blob(shot)
    male = len(_MALE_RE.findall(blob))
    female = len(_FEMALE_RE.findall(blob))
    two_cue = bool(_TWO_RE.search(blob))
    n = 2 if (two_cue or (male > 0 and female > 0)) else 1
    return {
        "n": n,
        "male_hits": male,
        "female_hits": female,
        "two_cue": two_cue,
        "layers_n": shot.get("layers_n"),
        "faces": shot.get("faces"),
    }


def infer_subject_gender(subject: str) -> str:
    s = (subject or "").strip().lower()
    if _FEMALE_RE.search(s) or any(re.search(rf"\b{re.escape(n)}\b", s) for n in _FEMALE_NAMES):
        return "female"
    if _MALE_RE.search(s) or any(re.search(rf"\b{re.escape(n)}\b", s) for n in _MALE_NAMES):
        return "male"
    return "unknown"


def bind_refmods_for_shots(
    refmods: Sequence[Any],
    shots: Sequence[dict[str, Any]],
) -> tuple[list[Any], dict[str, Any]]:
    """Keep audio RefMods out of Picture slots; bind at most one visual per on-screen person."""
    counts = [count_onscreen_people(s) for s in shots] or [ {"n": 1, "male_hits": 0, "female_hits": 0, "two_cue": False} ]
    n = max(int(c["n"]) for c in counts)
    male_needed = any(c["male_hits"] > 0 and c["female_hits"] == 0 and not c["two_cue"] for c in counts) and n == 1
    female_needed = any(c["female_hits"] > 0 and c["male_hits"] == 0 and not c["two_cue"] for c in counts) and n == 1
    both_needed = n >= 2

    tagged: list[Any] = []
    for r in refmods:
        kind = "audio" if (getattr(r, "kind", None) == "audio" or is_audio_refmod(r.subject, r.file)) else "visual"
        tagged.append(replace(r, kind=kind, picture_index=None if kind == "audio" else r.picture_index))

    visuals = [r for r in tagged if r.kind != "audio"]
    audios = [r for r in tagged if r.kind == "audio"]

    selected: list[Any] = []
    if male_needed or female_needed:
        want = "male" if male_needed else "female"
        preferred = [r for r in visuals if infer_subject_gender(r.subject) == want]
        fallback = [r for r in visuals if infer_subject_gender(r.subject) == "unknown"]
        pool = preferred or fallback
        selected = pool[:1]
    elif both_needed:
        # Prefer one female + one male when we can tell; otherwise first n visuals.
        female_v = [r for r in visuals if infer_subject_gender(r.subject) == "female"]
        male_v = [r for r in visuals if infer_subject_gender(r.subject) == "male"]
        unknown_v = [r for r in visuals if infer_subject_gender(r.subject) == "unknown"]
        pick: list[Any] = []
        if female_v:
            pick.append(female_v[0])
        if male_v:
            pick.append(male_v[0])
        for r in unknown_v + visuals:
            if len(pick) >= n:
                break
            if r not in pick:
                pick.append(r)
        selected = pick[:n]
    else:
        selected = visuals[:n]

    selected_ids = {id(r) for r in selected}
    numbered: list[Any] = []
    pic = 1
    for r in tagged:
        if r.kind == "audio":
            numbered.append(replace(r, picture_index=None, kind="audio"))
        elif id(r) in selected_ids:
            numbered.append(replace(r, picture_index=pic, kind="visual"))
            pic += 1
        else:
            numbered.append(replace(r, picture_index=None, kind="visual"))

    report = {
        "people_n": n,
        "visual_bound": sum(1 for r in numbered if r.kind == "visual" and r.picture_index is not None),
        "visual_unbound": sum(1 for r in numbered if r.kind == "visual" and r.picture_index is None),
        "audio_n": len(audios),
        "shot_counts": counts,
    }
    return numbered, report


def speech_lines_of(shot: dict[str, Any]) -> list[dict[str, str]]:
    speech = shot.get("speech") or {}
    raw = speech.get("lines") if isinstance(speech, dict) else shot.get("lines") or []
    out: list[dict[str, str]] = []
    for item in raw or []:
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if text:
                out.append({"speaker": str(item.get("speaker") or "S1"), "text": text})
        elif isinstance(item, str) and item.strip():
            out.append({"speaker": "S1", "text": item.strip()})
    return out


def oral_noun_hits(text: str) -> list[str]:
    found = sorted({m.group(0).lower() for m in _ORAL_NOUN_RE.finditer(text or "")})
    return found


def official_oral_hit(text: str) -> bool:
    try:
        from h3max_bridge.h3max_bridge import load_beta7_convert

        b7 = load_beta7_convert()
        br = getattr(b7, "br", None)
        if br is None:
            import build_request as br  # type: ignore
        pat = getattr(br, "_ORAL_ACT_RE", None)
        return bool(pat and pat.search(text or ""))
    except Exception:
        return False


def is_oral_context(text: str) -> bool:
    return official_oral_hit(text) or bool(_ORAL_NOUN_RE.search(text or ""))


def _block_speaker(prefix: str, block: str) -> str | None:
    m = _SPEAKER_BEFORE_RE.search(prefix)
    if m:
        return f"S{m.group(1) or m.group(2)}"
    m2 = _SPEAKER_INSIDE_RE.search(block)
    if m2:
        return f"S{m2.group(1) or m2.group(2)}"
    return None


def apply_bridge_gates(text: str, *, oral_source_text: str = "") -> dict[str, Any]:
    """Mute oral-giver / untagged <d> on oral beats; require speaker tags and lip-sync on kept lines."""
    original = text or ""
    oral = is_oral_context(original) or is_oral_context(oral_source_text)
    official_talk = False
    official_d1: list[str] = []
    try:
        import wp_lint  # type: ignore
        import build_request as br  # type: ignore

        official_talk = bool(wp_lint.oral_mouth_talk(original))
        units = re.split(r"\n+", original)
        checks = br.audio_act_checks(units, {"oral_giver": None}, True)
        official_d1 = [str(c.get("code")) for c in checks if c.get("code") == "D1"]
        if official_talk or official_d1:
            oral = True
    except Exception:
        pass

    muted = 0
    kept = 0
    untagged_muted = 0
    pieces: list[str] = []
    last = 0
    for m in _D_BLOCK_RE.finditer(original):
        pieces.append(original[last:m.start()])
        block = m.group(0)
        speaker = _block_speaker(original[:m.start()], block)
        drop = False
        if oral:
            # Giver defaults to S1; untagged lines are treated as the giver and muted.
            if speaker is None or speaker == "S1":
                drop = True
                muted += 1
                if speaker is None:
                    untagged_muted += 1
        elif speaker is None:
            drop = True
            muted += 1
            untagged_muted += 1
        if drop:
            last = m.end()
            continue
        kept += 1
        pieces.append(block)
        last = m.end()
    pieces.append(original[last:])
    out = "".join(pieces)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()

    lipsync_added = False
    if kept > 0 and not _LIPSYNC_RE.search(out):
        out = out.rstrip() + " " + LIPSYNC_CLAUSE
        lipsync_added = True

    remaining = list(_D_BLOCK_RE.finditer(out))
    untagged_remaining = 0
    for m in remaining:
        if _block_speaker(out[:m.start()], m.group(0)) is None:
            untagged_remaining += 1

    ready = untagged_remaining == 0
    return {
        "text": out,
        "oral_context": oral,
        "official_oral_mouth_talk": official_talk,
        "official_d1_codes": official_d1,
        "oral_noun_hits": oral_noun_hits(original + " " + oral_source_text),
        "d_muted": muted,
        "d_kept": kept,
        "untagged_muted": untagged_muted,
        "untagged_remaining": untagged_remaining,
        "lipsync_added": lipsync_added,
        "lipsync_present": bool(kept and (_LIPSYNC_RE.search(out) or lipsync_added)),
        "status": "READY" if ready else "NOT_READY",
        "codes": [] if ready else ["untagged_dialogue"],
    }


def named_refmod_lines(refmods: Sequence[Any]) -> list[str]:
    lines: list[str] = []
    visuals = [r for r in refmods if r.kind != "audio" and r.picture_index is not None]
    audios = [r for r in refmods if r.kind == "audio"]
    unbound = [r for r in refmods if r.kind != "audio" and r.picture_index is None]
    if visuals:
        bits = []
        for r in visuals:
            label = f"(S{r.picture_index})"
            # If the subject is already S1/S2, do not also write a bare S1/S2 name (wp_lint bare_label).
            if re.fullmatch(r"(?:S|Picture\s*)?\d+", str(r.subject), flags=re.IGNORECASE):
                bits.append(f"{label} is bound as a visual via {r.slot}; omit <Picture {r.picture_index}>")
            else:
                bits.append(f"{label} is {r.subject} (visual via {r.slot}; omit <Picture {r.picture_index}>)")
        lines.append("Bound on-screen subjects: " + ", ".join(bits) + ".")
    if audios:
        lines.append(
            "Voice/audio RefMods (not visual, no Picture tags): "
            + ", ".join(f"{r.subject} via {r.slot}" for r in audios)
            + "."
        )
    if unbound:
        lines.append(
            f"{len(unbound)} extra visual RefMod(s) were not bound because they exceed the on-screen person count."
        )
    return lines


def structural_report(
    *,
    shot_id: str,
    shot: dict[str, Any],
    refmods: Sequence[Any],
    prompt: str,
    gates: dict[str, Any],
    validation_redacted: dict[str, Any] | None = None,
) -> dict[str, Any]:
    people = count_onscreen_people(shot)
    bound = [r for r in (refmods or []) if getattr(r, "kind", None) != "audio" and getattr(r, "picture_index", None) is not None]
    return {
        "shot_id": shot_id,
        "talk_share": shot.get("talk_share"),
        "faces": shot.get("faces"),
        "layers_n": shot.get("layers_n"),
        "speech_lines_n": len(speech_lines_of(shot)),
        "people": people,
        "visual_bound_n": len(bound),
        "visual_subjects": [r.subject for r in bound],
        "audio_refmod_n": sum(1 for r in (refmods or []) if getattr(r, "kind", None) == "audio"),
        "d_count": len(_D_BLOCK_RE.findall(prompt or "")),
        "s_tags": {
            "s1": len(re.findall(r"\(S1\)|<Subject\s+1>", prompt or "", flags=re.I)),
            "s2": len(re.findall(r"\(S2\)|<Subject\s+2>", prompt or "", flags=re.I)),
        },
        "gates": {
            "oral_context": gates.get("oral_context"),
            "d_muted": gates.get("d_muted"),
            "d_kept": gates.get("d_kept"),
            "untagged_muted": gates.get("untagged_muted"),
            "lipsync_present": gates.get("lipsync_present"),
            "official_oral_mouth_talk": gates.get("official_oral_mouth_talk"),
            "official_d1_codes": gates.get("official_d1_codes"),
            "oral_noun_hit_n": len(gates.get("oral_noun_hits") or []),
        },
        "validation": validation_redacted,
    }
