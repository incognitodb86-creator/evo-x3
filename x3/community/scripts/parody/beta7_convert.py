"""Shared 10Eros-Max Beta 7 prompt converter & pre-flight validator (W3a, U56 Decision #1).

Converts official 6-section Ref2VA or 3-section Base MiniMax-H3 prompts (from duckyshell,
pytraveler, ref2va-27b, REA-Video, or Hermes) into Beta 7 compliant text:
- Removes `integrated_multimodal_description:` (maps to `detailed_description:` in 4-section
  Render mode, or strips it in header-free plain mode).
- Folds `overall_soundscape:` (and other labeled sound headers) into plain diegetic sound
  sentences appended to the end of the description.
- Drops `non_diegetic_music:` (and other labeled music headers).
- Omits `<Picture N>` tags for subjects supplied via `ComfyUI-MiniMaxH3Mod` RefMods.
- Validates against `U56 Decision #1` banned headers, Markdown leakage, refusal/policy/youth
  stops, `<d>` tag balance, `[Shot N]` timestamps, 1-indexed asset tags, and `wp_lint.lint`.

Reuses regexes and section splitting from `build_request.py` and `wp_lint.py` without copying.
"""
from __future__ import annotations

import argparse
import os
import json
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br
import wp_lint

RENDER_LEAD_SECTIONS: tuple[str, ...] = ("subject_definitions", "summary", "retention_analysis")

# U56 Decision #1 banned headers (Beta 7 rejects official H3 multimodal/audio headers).
BANNED_HEADER_RE = re.compile(
    r"(?im)^\s*(?:#+\s*|\*\*)?(integrated_multimodal_description|overall_soundscape|non_diegetic_music|"
    r"diegetic[ _]sound(?:scape)?|soundscape|sound|audio|music)\s*(?:\*\*)?\s*:",
)
_MARKDOWN_FENCE_RE = re.compile(r"```")
_MARKDOWN_HEADING_RE = re.compile(r"(?m)^\s*#{1,6}\s+\S")
_MARKDOWN_BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")
_NONE_SOUND_RE = re.compile(r"(?i)^(?:none|n/?a|no\s+(?:sound|audio|music)|silence\s+only)\.?$")
_SHOT_HEADER_RE = re.compile(
    r"\[Shot\s*(\d+)\]\s*(?:At\s+(?:(\d{1,2}):)?(\d{1,2}(?:\.\d+)?)(?=\s|,|$))?",
    re.IGNORECASE,
)
_ZERO_ASSET_TAG_RE = re.compile(r"<(?:Picture|Video|Audio|Subject)\s+0>", re.IGNORECASE)
_D_TAG_RE = re.compile(r"</?d>", re.IGNORECASE)


def _strip_markdown_wrappers(text: str) -> str:
    """Remove code fences and simple bold/heading wrappers without altering dialogue tags."""
    out = re.sub(r"```[a-zA-Z0-9_-]*\s*\n?", "", text or "")
    out = out.replace("```", "")
    # Strip markdown heading prefixes like `## overall_soundscape:` -> `overall_soundscape:`
    out = re.sub(r"(?m)^\s*#{1,6}\s+", "", out)
    # Strip markdown bold `**text**` -> `text`
    out = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", out)
    return out.strip()


def _normalize_sound_sentences(sound_blocks: Sequence[str]) -> str:
    """Turn soundscape blocks into clean plain diegetic sentences."""
    parts: list[str] = []
    for block in sound_blocks:
        for raw_line in (block or "").splitlines():
            line = re.sub(r"^\s*[-*•]\s+", "", raw_line).strip()
            if not line or _NONE_SOUND_RE.match(line):
                continue
            if line[-1] not in ".?!":
                line += "."
            parts.append(line)
    return " ".join(parts).strip()


def _omit_picture_tags(text: str, omit_pictures: set[int]) -> str:
    """Remove `<Picture N>` tags for RefMod-bound indices and clean adjacent punctuation/spaces."""
    if not omit_pictures or not text:
        return text
    out = text
    for idx in sorted(omit_pictures):
        # Remove optional parenthetical wrapper like `(<Picture 1>)` or bare `<Picture 1>`
        out = re.sub(rf"\(\s*<Picture\s+{idx}>\s*\)", "", out, flags=re.IGNORECASE)
        out = re.sub(rf"<Picture\s+{idx}>", "", out, flags=re.IGNORECASE)
    # Clean up double spaces and orphaned punctuation introduced by tag removal
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\s+([,.;:?!])", r"\1", out)
    out = re.sub(r"([(\[])\s+", r"\1", out)
    out = re.sub(r",\s*,+", ",", out)
    out = re.sub(r"(?m)^[ \t]+|[ \t]+$", "", out)
    return out


def convert_to_beta7(
    raw: str,
    *,
    omit_pictures: Iterable[int] | None = None,
    mode: str = "auto",
) -> tuple[str, dict[str, Any]]:
    """Convert an H3 prompt into Beta 7 format (header-free plain or 4-section Render).

    Args:
        raw: Input prompt text (6-section Ref2VA, 3-section Base, 4-section Render, or plain).
        omit_pictures: 1-based `<Picture N>` indices supplied by RefMods to omit.
        mode: `"auto"` (keeps Render's 4 headers if `subject_definitions`/`summary`/
            `retention_analysis` are present; otherwise header-free plain), `"plain"`
            (always header-free), or `"render"` (4-section Render headers).

    Returns:
        `(converted_text, report_dict)`
    """
    if mode not in ("auto", "plain", "render"):
        raise ValueError(f"mode must be 'auto', 'plain', or 'render', got {mode!r}")

    cleaned = _strip_markdown_wrappers(raw or "")
    secs = br.split_writer_sections(cleaned)

    removed_headers: list[str] = []
    folded_sound_headers: list[str] = []
    dropped_music_headers: list[str] = []

    desc_chunks: list[str] = []
    for key in ("detailed_description", "integrated_multimodal_description"):
        if key in secs:
            if key == "integrated_multimodal_description":
                removed_headers.append(key)
            for chunk in secs[key]:
                if chunk.strip():
                    desc_chunks.append(chunk.strip())
    if not desc_chunks and "_lead" in secs:
        desc_chunks.extend(c.strip() for c in secs["_lead"] if c.strip())

    sound_blocks: list[str] = []
    for key, vals in secs.items():
        if key in br._SOUND_HEADERS:
            folded_sound_headers.append(key)
            sound_blocks.extend(vals)
        elif key in br._MUSIC_HEADERS:
            dropped_music_headers.append(key)

    description = " ".join(desc_chunks).strip()
    sound_tail = _normalize_sound_sentences(sound_blocks)
    if sound_tail:
        if description and description[-1] not in ".?!":
            description += "."
        if sound_tail.lower() not in description.lower():
            description = f"{description} {sound_tail}".strip() if description else sound_tail

    has_render_lead = any(k in secs for k in RENDER_LEAD_SECTIONS)
    emit_render = (mode == "render") or (mode == "auto" and has_render_lead)

    if emit_render:
        out_blocks: list[str] = []
        for k in RENDER_LEAD_SECTIONS:
            if secs.get(k):
                body = secs[k][0].strip()
                out_blocks.append(f"{k}:\n{body}" if "\n" in body else f"{k}: {body}")
        if description:
            out_blocks.append(f"detailed_description: {description}")
        if secs.get("continuation"):
            cont = secs["continuation"][0].strip()
            if cont:
                out_blocks.append(f"continuation: {cont}")
        result = "\n\n".join(out_blocks).strip()
    else:
        if "detailed_description" in secs:
            removed_headers.append("detailed_description")
        for k in RENDER_LEAD_SECTIONS:
            if k in secs:
                removed_headers.append(k)
        result = description

    omit_set = {int(i) for i in (omit_pictures or ()) if int(i) >= 1}
    if omit_set:
        result = _omit_picture_tags(result, omit_set)

    report: dict[str, Any] = {
        "mode_used": "render" if emit_render else "plain",
        "removed_headers": sorted(set(removed_headers)),
        "folded_sound_headers": sorted(set(folded_sound_headers)),
        "dropped_music_headers": sorted(set(dropped_music_headers)),
        "omitted_pictures": sorted(omit_set),
    }
    return result, report


def _check_d_balance(text: str) -> str | None:
    depth = 0
    for m in _D_TAG_RE.finditer(text or ""):
        tok = m.group(0).lower()
        if tok == "<d>":
            depth += 1
            if depth > 1:
                return "nested <d> dialogue tag"
        else:
            depth -= 1
            if depth < 0:
                return "stray </d> closing tag without opening <d>"
    if depth != 0:
        return "unclosed <d> dialogue tag"
    return None


REF2VA_SIX_SECTIONS: tuple[str, ...] = (
    "subject_definitions",
    "summary",
    "retention_analysis",
    "detailed_description",
    "overall_soundscape",
    "non_diegetic_music",
)
_SIX_SECTION_ALIASES = {"integrated_multimodal_description": "detailed_description"}
_SIX_SECTION_RE = re.compile(
    r"(?im)^[ \t]*(?:#+[ \t]*|\*\*)?("
    + "|".join(list(REF2VA_SIX_SECTIONS) + list(_SIX_SECTION_ALIASES))
    + r")(?:\*\*)?[ \t]*:?[ \t]*"
)
_SUBJECT_TAG_RE = re.compile(r"<Subject\s+(\d+)>", re.IGNORECASE)
_SUBJECT_SPEAKER_RE = re.compile(r"<Subject\s+(\d+)>\s*\(S(\d+)\)", re.IGNORECASE)
_SPEAKER_TAG_RE = re.compile(r"\(S(\d+)\)")
_FEM_PERSON_RE = re.compile(r"\b(?:woman|female|she|her|hers)\b", re.IGNORECASE)
_MASC_PERSON_RE = re.compile(r"\b(?:man|male|he|him|his)\b", re.IGNORECASE)
REGEN_CODES = frozenset({"filler_lines", "speaker_tag_mismatch"})


def _config_yaml_candidates() -> list[Path]:
    here = Path(__file__).resolve()
    paths: list[Path] = []
    env = os.environ.get("WP_HOME")
    if env:
        paths.append(Path(env) / "config.yaml")
    # x3/community/scripts/parody/this.py -> x3/render/writer_pipeline/config.yaml
    if len(here.parents) >= 4:
        paths.append(here.parents[3] / "render" / "writer_pipeline" / "config.yaml")
    return paths


def load_filler_lines(cfg: dict[str, Any] | None = None) -> list[str]:
    """Return the existing writer-pipeline filler_lines list. Never invent a new list."""
    if cfg and cfg.get("filler_lines"):
        return [str(x) for x in cfg["filler_lines"]]
    for path in _config_yaml_candidates():
        if not path.is_file():
            continue
        m = re.search(r"(?m)^\s*filler_lines:\s*(\[.*\])\s*$", path.read_text(encoding="utf-8"))
        if m:
            return list(json.loads(m.group(1)))
    return []


def six_section_report(text: str) -> dict[str, Any]:
    """Official 6-section Ref2VA completeness (W1 scoring / validator gap).

    `integrated_multimodal_description` counts as the official name of `detailed_description`.
    """
    seen: set[str] = set()
    for m in _SIX_SECTION_RE.finditer(text or ""):
        key = m.group(1).lower()
        seen.add(_SIX_SECTION_ALIASES.get(key, key))
    present = [k for k in REF2VA_SIX_SECTIONS if k in seen]
    return {
        "sections_present": present,
        "six_section_complete": all(k in seen for k in REF2VA_SIX_SECTIONS),
        "missing_sections": [k for k in REF2VA_SIX_SECTIONS if k not in seen],
    }


def _infer_person(text: str) -> str | None:
    fem = len(_FEM_PERSON_RE.findall(text or ""))
    masc = len(_MASC_PERSON_RE.findall(text or ""))
    if fem > masc and fem:
        return "her"
    if masc > fem and masc:
        return "him"
    return None


def _declared_subjects(text: str) -> dict[int, dict[str, Any]]:
    """Map subject number -> {speaker, person} from <Subject N> definitions."""
    body = text or ""
    found = list(_SUBJECT_TAG_RE.finditer(body))
    out: dict[int, dict[str, Any]] = {}
    for i, m in enumerate(found):
        n = int(m.group(1))
        end = found[i + 1].start() if i + 1 < len(found) else len(body)
        chunk = body[m.start():end]
        sm = re.match(r"<Subject\s+(\d+)>\s*(?:\(S(\d+)\))?", chunk, flags=re.IGNORECASE)
        speaker = int(sm.group(2)) if sm and sm.group(2) else n
        out[n] = {"speaker": speaker, "person": _infer_person(chunk), "decl": chunk[:240]}
    return out


def check_speaker_tags(text: str) -> list[dict[str, str]]:
    """(S#) must match a declared <Subject #> with the same number and the right person."""
    body = text or ""
    violations: list[dict[str, str]] = []
    subjects = _declared_subjects(body)
    for m in _SUBJECT_SPEAKER_RE.finditer(body):
        n, s = int(m.group(1)), int(m.group(2))
        if n != s:
            violations.append({
                "code": "speaker_tag_mismatch",
                "note": f"<Subject {n}> is tagged (S{s}); speaker tags must use the same number",
            })
        elif subjects and n not in subjects:
            violations.append({
                "code": "speaker_tag_mismatch",
                "note": f"(S{s}) is paired with undeclared <Subject {n}>",
            })
    if subjects:
        declared_speakers = set(subjects)
        for spk in {int(m.group(1)) for m in _SPEAKER_TAG_RE.finditer(body)}:
            if spk not in declared_speakers:
                violations.append({
                    "code": "speaker_tag_mismatch",
                    "note": f"(S{spk}) has no declared <Subject {spk}>",
                })
        # Gendered cue next to a tag that belongs to the other person.
        for m in re.finditer(r"(?s)[^.]{0,200}\(S(\d+)\)[^.<]{0,80}<d>", body, flags=re.IGNORECASE):
            spk = int(m.group(1))
            cue = _infer_person(m.group(0))
            person = (subjects.get(spk) or {}).get("person")
            if cue and person and cue != person:
                violations.append({
                    "code": "speaker_tag_mismatch",
                    "note": f"(S{spk}) is declared as {person}, but the line is written as {cue}",
                })
    # Deduplicate identical notes
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    for v in violations:
        if v["note"] in seen:
            continue
        seen.add(v["note"])
        uniq.append(v)
    return uniq


def check_filler_lines(text: str, *, cfg: dict[str, Any] | None = None, ask: str = "") -> list[dict[str, str]]:
    """Reuse wp_lint's stock-talk matcher and the existing filler_lines list."""
    fillers = [wp_lint.norm(f) for f in load_filler_lines(cfg)]
    if not fillers:
        return []
    ask_n = wp_lint.norm(ask or "")
    dd = wp_lint.get_dd(text) or (text or "")
    out: list[dict[str, str]] = []
    for line in wp_lint.spoken_lines(dd):
        if any(f and re.search(r"(?<!\w)" + re.escape(f) + r"(?!\w)", line) for f in fillers) and line not in ask_n:
            out.append({"code": "filler_lines", "note": f"line '{line}' is stock talk; write a line about the still"})
            break
    return out


def _not_ready_reason(violations: Sequence[dict[str, str]]) -> str | None:
    if not violations:
        return None
    codes = [v.get("code") or "" for v in violations]
    for code in ("filler_lines", "speaker_tag_mismatch", "six_section_incomplete", "youth_hint"):
        if code in codes:
            return code
    return codes[0]


def violation_codes(val: dict[str, Any]) -> set[str]:
    return {str(v.get("code") or "") for v in (val.get("violations") or [])}


def needs_regenerate(val: dict[str, Any]) -> bool:
    return bool(violation_codes(val) & REGEN_CODES)


def validate_beta7(
    text: str,
    *,
    clip_seconds: float | None = None,
    refmod_pictures: Iterable[int] | None = None,
    lint_ctx: dict[str, Any] | None = None,
    minimal_lint: bool = True,
    require_six_sections: bool = False,
) -> dict[str, Any]:
    """Pre-flight validator for Beta 7 prompts (`U56 Decision #1`).

    Returns dict with `status` (`"READY"` or `"NOT_READY"`), `header_violations`,
    `violations`, optional `lint` (from `wp_lint.lint`), `sections_present`,
    `six_section_complete`, and `not_ready_reason`.
    """
    body = (text or "").strip()
    violations: list[dict[str, str]] = []
    header_violations: list[str] = []
    six = six_section_report(body)

    if not body:
        violations.append({"code": "empty", "note": "empty prompt text"})
        return {
            "status": "NOT_READY",
            "header_violations": [],
            "violations": violations,
            "lint": None,
            "sections_present": [],
            "six_section_complete": False,
            "not_ready_reason": "empty",
        }

    # 1. Banned Beta 7 headers (U56 Decision #1)
    for m in BANNED_HEADER_RE.finditer(body):
        hdr = m.group(1).lower()
        if hdr not in header_violations:
            header_violations.append(hdr)
            violations.append({"code": "banned_header", "note": f"banned Beta 7 header: {hdr}:"})

    # 2. Markdown leakage
    if _MARKDOWN_FENCE_RE.search(body) or _MARKDOWN_HEADING_RE.search(body) or _MARKDOWN_BOLD_RE.search(body):
        violations.append({"code": "markdown_leakage", "note": "Markdown formatting (fences, headings, or bold) is banned"})

    # 3. Refusal, policy/governance disclaimer, self-grading, and 18+ youth stops (reused from build_request & wp_lint)
    plain = br._D_RE.sub("", body)
    if (m := br._REFUSAL_RE.search(plain)):
        violations.append({"code": "refusal", "note": f"refusal phrase: {m.group(0)!r}"})
    if (m := br._POLICY_RE.search(plain)):
        violations.append({"code": "policy_word", "note": f"policy/governance phrase: {m.group(0)!r}"})
    if (m := br._SELF_GRADE_RE.search(plain)):
        violations.append({"code": "self_grade", "note": f"self-grading phrase: {m.group(0)!r}"})
    if (m := (wp_lint.YOUTH_RE.search(body) or wp_lint.UNDER18_AGE_RE.search(body))):
        violations.append({"code": "youth_hint", "note": f"18+ hard stop: {m.group(0)!r}"})

    # 4. Dialogue tag balance
    if (d_err := _check_d_balance(body)):
        violations.append({"code": "dialogue_tags", "note": d_err})

    # 5. Zero-indexed asset tags
    if (m := _ZERO_ASSET_TAG_RE.search(body)):
        violations.append({"code": "zero_indexed_asset", "note": f"asset tags are 1-indexed, found {m.group(0)}"})

    # 6. RefMod-bound <Picture N> omission check
    for idx in sorted({int(i) for i in (refmod_pictures or ()) if int(i) >= 1}):
        if re.search(rf"<Picture\s+{idx}>", body, flags=re.IGNORECASE):
            violations.append({
                "code": "refmod_picture_tag",
                "note": f"<Picture {idx}> must be omitted because subject {idx} is supplied via RefMod",
            })

    # 7. [Shot N] timestamp rules
    prev_t = 0.0
    for sm in _SHOT_HEADER_RE.finditer(body):
        sn = int(sm.group(1))
        has_ts = sm.group(3) is not None
        if sn == 1 and has_ts:
            violations.append({"code": "shot1_timestamp", "note": "[Shot 1] must not carry an At MM:SS.mmm timestamp"})
        elif sn >= 2 and has_ts:
            t_sec = (int(sm.group(2) or 0) * 60.0) + float(sm.group(3))
            if t_sec <= 0.0 or t_sec <= prev_t:
                violations.append({
                    "code": "shot_timestamp",
                    "note": f"[Shot {sn}] timestamp {t_sec:.3f}s must be > {prev_t:.3f}s",
                })
            elif clip_seconds is not None and t_sec >= float(clip_seconds):
                violations.append({
                    "code": "shot_timestamp",
                    "note": f"[Shot {sn}] timestamp {t_sec:.3f}s must be < clip duration {float(clip_seconds):.3f}s",
                })
            prev_t = t_sec

    # 8. Official 6-section completeness (hard only when scoring raw Ref2VA)
    if require_six_sections and not six["six_section_complete"]:
        missing = ", ".join(six["missing_sections"])
        violations.append({
            "code": "six_section_incomplete",
            "note": f"Ref2VA output is missing section(s): {missing}",
        })

    # 9. Speaker tags must match declared <Subject #> (same number, right person)
    violations.extend(check_speaker_tags(body))

    # 10. Existing filler_lines lint (same list and matcher as wp_lint)
    lint_cfg = ((lint_ctx or {}).get("cfg") or None)
    ask = str((lint_ctx or {}).get("ask") or "")
    violations.extend(check_filler_lines(body, cfg=lint_cfg, ask=ask))

    # 11. Optional wp_lint.lint integration
    lint_result: dict[str, Any] | None = None
    if lint_ctx is not None:
        lint_result = wp_lint.lint(body, lint_ctx, minimal=minimal_lint)
        for iss in lint_result.get("issues") or []:
            if iss.get("code") == "audio_header_beta7":
                if "audio_header_beta7" not in header_violations:
                    header_violations.append("audio_header_beta7")
                violations.append({"code": "audio_header_beta7", "note": str(iss.get("note", ""))})
            elif iss.get("hard"):
                violations.append({"code": f"wp_lint:{iss.get('code')}", "note": str(iss.get("note", ""))})

    status = "READY" if not violations else "NOT_READY"
    return {
        "status": status,
        "header_violations": header_violations,
        "violations": violations,
        "lint": lint_result,
        "sections_present": six["sections_present"],
        "six_section_complete": six["six_section_complete"],
        "not_ready_reason": _not_ready_reason(violations) if status == "NOT_READY" else None,
    }


def convert_and_validate(
    raw: str,
    *,
    omit_pictures: Iterable[int] | None = None,
    mode: str = "auto",
    clip_seconds: float | None = None,
    lint_ctx: dict[str, Any] | None = None,
    require_six_sections: bool = False,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    converted, conv = convert_to_beta7(raw, omit_pictures=omit_pictures, mode=mode)
    val = validate_beta7(
        converted,
        clip_seconds=clip_seconds,
        refmod_pictures=omit_pictures,
        lint_ctx=lint_ctx,
        require_six_sections=require_six_sections,
    )
    return converted, conv, val


def run_with_single_regen(
    generate,
    *,
    seed: int | None = 0,
    omit_pictures: Iterable[int] | None = None,
    mode: str = "auto",
    clip_seconds: float | None = None,
    lint_ctx: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call generate(seed), convert, and validate. On filler_lines or speaker_tag_mismatch,
    regenerate once with seed+1. If it still hits, keep the second result and mark NOT_READY.
    """
    first_seed = 0 if seed is None else int(seed)
    raw = generate(first_seed)
    converted, conv, val = convert_and_validate(
        raw, omit_pictures=omit_pictures, mode=mode, clip_seconds=clip_seconds, lint_ctx=lint_ctx
    )
    regen: dict[str, Any] = {"attempted": False, "seed": first_seed, "final_seed": first_seed, "first_codes": []}
    if needs_regenerate(val):
        new_seed = first_seed + 1
        raw = generate(new_seed)
        first_codes = sorted(violation_codes(val) & REGEN_CODES)
        converted, conv, val = convert_and_validate(
            raw, omit_pictures=omit_pictures, mode=mode, clip_seconds=clip_seconds, lint_ctx=lint_ctx
        )
        regen = {
            "attempted": True,
            "seed": first_seed,
            "final_seed": new_seed,
            "first_codes": first_codes,
        }
    return {
        "raw": raw,
        "text": converted,
        "conversion": conv,
        "validation": val,
        "regen": regen,
    }


def score_ref2va_output(
    raw: str,
    *,
    omit_pictures: Iterable[int] | None = None,
    clip_seconds: float | None = None,
    lint_ctx: dict[str, Any] | None = None,
    generate=None,
    seed: int | None = None,
    mode: str = "auto",
) -> dict[str, Any]:
    """Scoring path: six-section check on the raw official output, then convert + validate.

    When `generate` is given, the filler/speaker regenerate-once rule is applied first.
    """
    regen = {"attempted": False, "seed": seed, "final_seed": seed, "first_codes": []}
    if generate is not None:
        boxed = run_with_single_regen(
            generate,
            seed=0 if seed is None else seed,
            omit_pictures=omit_pictures,
            mode=mode,
            clip_seconds=clip_seconds,
            lint_ctx=lint_ctx,
        )
        raw = boxed["raw"]
        converted, conv, val = boxed["text"], boxed["conversion"], boxed["validation"]
        regen = boxed["regen"]
    else:
        converted, conv, val = convert_and_validate(
            raw, omit_pictures=omit_pictures, mode=mode, clip_seconds=clip_seconds, lint_ctx=lint_ctx
        )
    six = six_section_report(raw)
    status = "READY" if val["status"] == "READY" and six["six_section_complete"] else "NOT_READY"
    if not six["six_section_complete"]:
        reason = "six_section_incomplete"
    elif val["status"] != "READY":
        reason = val.get("not_ready_reason") or _not_ready_reason(val.get("violations") or [])
    else:
        reason = None
    return {
        "status": status,
        "not_ready_reason": reason,
        "raw": raw,
        "text": converted,
        "conversion": conv,
        "validation": val,
        "sections_present": six["sections_present"],
        "six_section_complete": six["six_section_complete"],
        "missing_sections": six["missing_sections"],
        "regen": regen,
    }



def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Convert MiniMax-H3 prompts to Beta 7 format and validate (U56 Decision #1).")
    ap.add_argument("input", nargs="?", default="-", help="Input prompt file path, or '-' for stdin.")
    ap.add_argument("-o", "--output", default=None, help="Output file path (default: stdout).")
    ap.add_argument("--mode", choices=("auto", "plain", "render"), default="auto", help="Output header mode.")
    ap.add_argument("--omit-picture", type=int, action="append", default=[], help="1-based <Picture N> index supplied via RefMod.")
    ap.add_argument("--clip-seconds", type=float, default=None, help="Clip duration in seconds for [Shot N] timestamp validation.")
    ap.add_argument("--validate", action="store_true", help="Run Beta 7 pre-flight validation and exit 2 on NOT_READY.")
    ap.add_argument("--json", action="store_true", help="Emit JSON result (converted text + conversion/validation report).")
    args = ap.parse_args(list(argv) if argv is not None else None)

    raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    converted, conv_rep = convert_to_beta7(raw, omit_pictures=args.omit_picture, mode=args.mode)
    val_rep = (
        validate_beta7(converted, clip_seconds=args.clip_seconds, refmod_pictures=args.omit_picture)
        if args.validate
        else None
    )

    if args.json:
        payload: dict[str, Any] = {"text": converted, "conversion": conv_rep}
        if val_rep is not None:
            payload["validation"] = val_rep
        out_str = json.dumps(payload, indent=2) + "\n"
    else:
        out_str = converted + ("\n" if converted and not converted.endswith("\n") else "")

    if args.output:
        Path(args.output).write_text(out_str, encoding="utf-8")
    else:
        sys.stdout.write(out_str)

    if val_rep is not None and val_rep["status"] != "READY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
