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


def validate_beta7(
    text: str,
    *,
    clip_seconds: float | None = None,
    refmod_pictures: Iterable[int] | None = None,
    lint_ctx: dict[str, Any] | None = None,
    minimal_lint: bool = True,
) -> dict[str, Any]:
    """Pre-flight validator for Beta 7 prompts (`U56 Decision #1`).

    Returns dict with `status` (`"READY"` or `"NOT_READY"`), `header_violations`,
    `violations`, and optional `lint` (from `wp_lint.lint`).
    """
    body = (text or "").strip()
    violations: list[dict[str, str]] = []
    header_violations: list[str] = []

    if not body:
        violations.append({"code": "empty", "note": "empty prompt text"})
        return {"status": "NOT_READY", "header_violations": [], "violations": violations, "lint": None}

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

    # 8. Optional wp_lint.lint integration
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
