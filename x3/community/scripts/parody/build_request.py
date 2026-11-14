"""Prompt builder and REF2VA request builder for H3 parody pipeline (U5).

Wraps make_b2_request.py pattern, populating all 8 loader slots on b2_refmod.api.json,
constructing a Malcolm-compliant prompt, preserving KEEP dials, and enforcing
adults-only guard constraints.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import sys
import hashlib
import math
import shutil
from typing import Any, Dict, List, Optional, Sequence, Tuple
import yaml

# Add community scripts to path for make_b2_request and comm
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as make_b2_build

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

from writer_sys import assert_writer_system_prompt, AgentInstructionsInWriterPrompt
import scene_addenda

DEFAULT_REFMOD_TEMPLATE = Path(r"C:\AI\community\templates\b2_refmod.api.json")
COMFY_INPUT_COMMUNITY = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community")

# --- U1: H3 frame grid + single-clip ceiling -------------------------------------------------
H3_FPS = 24
H3_HARD_MAX_FRAMES = 362  # TenStrip / H3-Max trained single-clip limit ((362 - 5) % 17 == 0, 15.08 s)
H3_MIN_FRAMES = 56
# Measured on the 16 GB RTX 5080 (2026-11-06 probe, Derrick t271u): 124f = 2m52s, 243f = 5m29s (linear,
# ~1.35 s/frame), 362f spilled to shared RAM at 15.8/16.3 GB and ran >15 min (ruled FAIL). Single shots cap at
# 243f (10.125 s); longer --seconds asks auto-split into shared-anchor cells (c01_s.., c02_s..) stitched into one clip.mp4.
SINGLE_CLIP_MAX_FRAMES = 243

# --- U3: canvas presets ----------------------------------------------------------------------
ASPECT_PRESETS: Dict[str, Tuple[int, int]] = {
    "9:16": (768, 1344), "portrait": (768, 1344),
    "16:9": (1344, 768), "landscape": (1344, 768), "widescreen": (1344, 768),
    "1:1": (1024, 1024), "square": (1024, 1024),
    "4:3": (1152, 864),
    "3:4": (864, 1152),
}
DEFAULT_CANVAS = (768, 1344)

# --- U4: camera + pronouns -------------------------------------------------------------------
DEFAULT_CAMERA = "static medium shot, eye level, 50mm lens, shallow depth of field"
STATIC_CAMERA_TAIL = ""  # static holds are written as a positive sentence; no no-zoom stack
_CAMERA_MOTION_RE = re.compile(
    r"\b(push(?:es|ing)?|pull(?:s|ing)?|pans?|panning|tilts?|tilting|track(?:s|ing)?|dolly|dollies|dollying|"
    r"handheld|hand-held|orbit(?:s|ing)?|crane|craning|zoom(?:s|ing)?|follow(?:s|ing)?|move|moves|moving|"
    r"sweep(?:s|ing)?|arc(?:s|ing)?)\b",
    re.IGNORECASE,
)

# --- (c) 2026-11-06 (brief t224x214): native latent-tail continuation ------------------------------
# Multi-beat used to render one INDEPENDENT clip per beat and concat them: a hard cut at every join. The path
# the installed nodes give instead, inside ONE graph, is GuidedContinuationWindow -> LatentTailGuide ->
# SamplerCustomAdvanced -> AppendContinuation (same shape as scripts/comm.py:build, which has no RefMod). The
# window's 22-frame head is hidden motion context trimmed from video AND audio by the append node, transition
# tokens 0, so the visible output is base + extension frames with no hidden overlap in it.
CONTINUATION_OVERLAP_FRAMES = 22
CONTINUATION_WINDOW_MAX_FRAMES = SINGLE_CLIP_MAX_FRAMES  # every sampled window stays <= 243 frames on 16 GB
DEFAULT_CONTINUATION_BASE_FRAMES = 192
DEFAULT_CONTINUATION_EXTENSION_FRAMES = 187
CONTINUATION_NODE_TYPES = frozenset({
    "MiniMaxH3GuidedContinuationWindow",
    "MiniMaxH3LatentTailGuide",
    "MiniMaxH3AppendContinuation",
})
# Prompt rule for a continuation beat: inherit the previous beat's closing state, never reset to the photo.
# dynsafe (2026-11-11, Derrick via Prompt maker brief item 1): {state} is the previous beat's actual closing pose and
# wardrobe (beat_closer), never a hardcoded standing pose.
CONTINUATION_LEAD_IN = (
    "The shot continues from the last seen moment: the same framing, {state}, "
    "the same room lighting, and {sub} is still in the same place at the same distance from "
    "the camera. At first there is only natural micro-motion - a breath, a slow blink, a small shift of "
    "weight - before this action. {Sub} keeps {poss} exact voice, accent and signature vocal timbre. "
    "The camera does not change angle and the shot never resets to a starting photo."
)
CONTINUATION_LEAD_IN_DYNAMIC = (
    "The shot continues from the last seen moment: {state}, and the shot never resets to a starting photo. "
    "{Sub} keeps {poss} exact voice, accent and signature vocal timbre."
)
_CONTINUATION_CUT_RE = re.compile(
    r"(?i)\b(?:new shot|hard cut|cuts?\s+to|camera\s+cuts?|scene\s+cuts?|"
    r"in\s+(?:another|a\s+different|the\s+next)\s+room)\b"
)
_CONTINUATION_WALK_RE = re.compile(
    r"(?i)\b(?:walks?|steps?|strolls?|crosses?|moves?\s+(?:into|across|toward|towards|over\s+to)|"
    r"heads?\s+(?:into|toward|towards)|enters?\s+the|kneels?|sits?\s+down|lies?\s+(?:down|back)|"
    r"gets?\s+(?:up|down|onto)|climbs?\s+onto|lowers?\s+(?:herself|himself|onto)|turns?\s+(?:and|toward|towards))\b"
)
_PLACE_WORD_RE = re.compile(
    r"(?i)\b(bedroom|bathroom|shower|kitchen|hallway|corridor|living\s+room|parlor|lounge|bar|diner|booth|"
    r"office|study|balcony|terrace|patio|garden|pool|beach|stage|studio|gym|locker\s+room|car|backseat|"
    r"elevator|stairwell|rooftop|alley|street|forest|cabin|tent|yacht|deck|cellar|attic|barn|warehouse|club)\b"
)
PRONOUNS: Dict[str, Dict[str, str]] = {
    "she": {"subj": "She", "obj": "her", "poss": "her", "Poss": "Her", "s": "s", "does": "does", "es": "es"},
    "he": {"subj": "He", "obj": "him", "poss": "his", "Poss": "His", "s": "s", "does": "does", "es": "es"},
    "they": {"subj": "They", "obj": "them", "poss": "their", "Poss": "Their", "s": "", "does": "do", "es": ""},
}
DEFAULT_IMAGE_ROLE = "composition, wardrobe, pose, and setting reference"
SUMMARY_LONG_CHARS = 180


_STAGE_CUE_RE = re.compile(
    r"(\bt\s*=\s*\d|\b\d{1,2}:\d{2}|</?\s*d\s*>|`|\bno\s+speech\b|\broom\s+tone\b)",
    re.IGNORECASE,
)
_FEATURING_RE = re.compile(r"\bfeaturing\s+", re.IGNORECASE)
DEFAULT_SCENE_ACTION = "faces the camera with relaxed, natural body language"
DEFAULT_LIGHTING = "late afternoon ambient lighting, soft key on face, subtle fill"
# R6: scene text that already implies lighting suppresses the stock late-afternoon lighting.
_LIGHTING_CUE_RE = re.compile(
    r"\b(neon|lit|lighting|lamp|lamps|2\s*am|midnight|dark|sunlight|daylight|bulb|bulbs|glow|candle|"
    r"candlelight|moonlit|moonlight|spotlight|backlit|fluorescent|dusk|dawn|sunset|sunrise)\b",
    re.IGNORECASE,
)
# R7: satire/parody tone clause ("styled in (a) satirical adult parody tone").
_TONE_CLAUSE_RE = re.compile(
    r"\s*,?\s*styled in (?:an? )?(?:[a-z-]+ ){0,4}?parody tone\b\.?",
    re.IGNORECASE,
)


def validate_spoken_dialogue(dialogue: Optional[str]) -> Optional[str]:
    """KTD2: return the spoken words only, None for a silent clip; raise on stage/SFX/timestamp cues."""
    if dialogue is None:
        return None
    text = str(dialogue).strip()
    if not text:
        return None
    m = _STAGE_CUE_RE.search(text)
    if m:
        raise ValueError(
            f"Dialogue must be spoken words only; found stage/SFX cue {m.group(0)!r} in {text!r}. "
            "Leave dialogue empty for a silent clip."
        )
    return text


def dedupe_featuring(desc: str) -> str:
    """KTD1: keep the first 'featuring' and drop any repeated 'featuring ' prefixes after it."""
    seen: List[bool] = []

    def _keep_first(m: "re.Match[str]") -> str:
        if seen:
            return ""
        seen.append(True)
        return m.group(0)

    return _FEATURING_RE.sub(_keep_first, desc)


def scene_implies_lighting(scene_action: Optional[str]) -> bool:
    """R6: True when the scene text already carries a lighting cue (neon, 2 AM, bulb, dark, ...)."""
    return bool(scene_action and _LIGHTING_CUE_RE.search(str(scene_action)))


def dedupe_satire_tone(text: str) -> str:
    """R7: keep only the last (canonical, resolver-appended) parody tone clause."""
    matches = list(_TONE_CLAUSE_RE.finditer(text))
    if len(matches) <= 1:
        return text
    out = text
    for m in reversed(matches[:-1]):
        out = out[: m.start()] + out[m.end():]
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ",", out)
    out = re.sub(r"^\s*,\s*", "", out)
    if matches[-1].group(0).lstrip(" ,").lower().startswith("styled") and not re.search(r",\s*styled in", out, re.IGNORECASE):
        out = re.sub(r"\s+(styled in )", r", \1", out, count=1, flags=re.IGNORECASE)
    return out.strip()


def snap_h3_frames(seconds: float, fps: int = H3_FPS, min_frames: int = H3_MIN_FRAMES,
                   max_frames: Optional[int] = None) -> int:
    """U1: nearest H3-grid length ((frames - 5) % 17 == 0) for `seconds`, clamped to [min_frames, max_frames]
    (default max = SINGLE_CLIP_MAX_FRAMES)."""
    if seconds is None or float(seconds) <= 0:
        raise ValueError(f"seconds must be positive, got {seconds!r}")
    max_frames = min(int(max_frames if max_frames is not None else SINGLE_CLIP_MAX_FRAMES), H3_HARD_MAX_FRAMES)
    k = int(round((float(seconds) * fps - 5) / 17.0))
    lo = int(math.ceil((min_frames - 5) / 17.0))
    hi = (max_frames - 5) // 17
    k = max(lo, min(hi, k))
    return 5 + 17 * k


def validate_single_clip_frames(frames: int) -> int:
    """U1: single-clip ceiling (SINGLE_CLIP_MAX_FRAMES = 243 on 16 GB) and positivity."""
    f = int(frames)
    cap = min(int(SINGLE_CLIP_MAX_FRAMES), H3_HARD_MAX_FRAMES)
    if f < 1:
        raise ValueError(f"frames must be positive, got {f}")
    if f > cap:
        raise ValueError(
            f"{f} frames exceeds the single-clip ceiling of {cap} frames ({cap / H3_FPS:.3f} s on 16 GB VRAM); "
            "use --seconds / --beat to build shared-anchor cells stitched into one clip instead."
        )
    return f


# --- (c) 2026-11-06 (brief t224x214): latent-tail continuation frame arithmetic ----------------
# The nodes enforce the rest at queue time (continuation_nodes.py): the 17k + 5 grid, extension_frames as a
# multiple of 17, the 40 Hz audio boundary (a window latent at the boundary or boundary + 1), the overlap trim
# and the join. Ours is the 16 GB sampled-window ceiling measured on this card, and the base/extension split.
def continuation_layout(base_frames: int = DEFAULT_CONTINUATION_BASE_FRAMES,
                        extension_frames: int = DEFAULT_CONTINUATION_EXTENSION_FRAMES,
                        overlap_frames: int = CONTINUATION_OVERLAP_FRAMES) -> Dict[str, Any]:
    """Frame arithmetic for one latent-tail window: the visible clip is base_frames + extension_frames.

    The window's overlap_frames head is generated as hidden motion context and trimmed from video AND audio by
    MiniMaxH3AppendContinuation with transition tokens 0, so no hidden overlap reaches the output and the
    completed latent is kept as-is. Only the sampled window is capped, never the cumulative latent.
    """
    base, ext, overlap = int(base_frames), int(extension_frames), int(overlap_frames)
    if base % 17 != 5 or overlap % 17 != 5:  # the same grid the nodes validate
        raise ValueError(f"base and overlap frames must satisfy the MiniMax H3 17k + 5 grid, got {base}/{overlap}")
    if ext < 17 or ext % 17:
        raise ValueError(f"extension_frames must be at least 17 and a multiple of 17, got {ext}")
    window, total = overlap + ext, base + ext
    if window > CONTINUATION_WINDOW_MAX_FRAMES:
        raise ValueError(
            f"continuation window {window} frames exceeds the sampled-window ceiling of "
            f"{CONTINUATION_WINDOW_MAX_FRAMES} frames ({CONTINUATION_WINDOW_MAX_FRAMES / H3_FPS:.3f} s on 16 GB)"
        )
    return {
        "mode": "native_latent_tail_continuation",
        "base_frames": base, "extension_frames": ext, "overlap_frames": overlap,
        "window_frames": window, "total_frames": total, "fps": H3_FPS,
        "base_seconds": round(base / H3_FPS, 4), "window_seconds": round(window / H3_FPS, 4),
        "total_seconds": round(total / H3_FPS, 4),
        "sampled_window_max_frames": CONTINUATION_WINDOW_MAX_FRAMES,
    }


def beat_closer(beat: Optional[Dict[str, Any]], pronoun: Optional[str] = None) -> Dict[str, str]:
    """dynsafe: the closing pose and wardrobe of one beat spec - its end_action, else the last sentence of its scene;
    the wardrobe is the last garment-removal sentence of the scene (if any). Empty strings when unknown."""
    b = beat or {}
    sub = _pronoun(pronoun or b.get("pronoun"))["subj"].lower()
    sents = [x.strip().rstrip(".") for x in re.split(r"(?<=[.!?])\s+", str(b.get("scene") or "").strip()) if x.strip()]

    def own(x: str) -> str:
        x = x.strip().rstrip(".")
        if not x:
            return ""
        return x[:1].lower() + x[1:] if re.match(r"(?i)(?:she|he|they|her|his|their|<Subject)\b", x) else f"{sub} {x[:1].lower() + x[1:]}"
    pose = own(str(b.get("end_action") or "")) or (own(sents[-1]) if sents else "")
    garm = "|".join(r for _, r in _GARMENT_KEYS)
    wear = next((own(x) for x in reversed(sents) if _REMOVE_VERB_RE.search(x) and re.search(garm, x, re.I)), "")
    places = [m.group(1).lower() for m in _PLACE_WORD_RE.finditer(str(b.get("scene") or ""))]
    return {"pose": pose, "wardrobe": wear if wear != pose else "", "place": places[-1] if places else ""}


def _beat_changes_view_or_place(scene: Optional[str], camera: Optional[str] = None,
                                new_shot: bool = False) -> bool:
    """True when the continuation beat names a camera move, a timed cut, or a walk into the next pose or room."""
    if new_shot or camera_moves(camera):
        return True
    s = str(scene or "")
    if not s.strip():
        return False
    if camera_moves(s) or _CONTINUATION_CUT_RE.search(s) or _CONTINUATION_WALK_RE.search(s):
        return True
    return bool(re.search(r"\[Shot\s*[2-9]\d*\]|\bAt\s+\d{1,2}:\d{2}", s, re.I))


def continuation_scene(scene: Optional[str], pronoun: Optional[str] = None,
                       closer: Optional[Dict[str, str]] = None,
                       camera: Optional[str] = None,
                       new_shot: bool = False) -> str:
    """Continuation-beat scene text: the inherited closing state first, then the caller's action. dynsafe: the state is
    the previous beat's real closing pose and wardrobe (closer); without one, 'the pose and wardrobe the previous beat
    ended on' - never a fixed standing pose. When the beat names a camera move, cut, or walk, replace same-framing /
    camera-does-not-change-angle / same-room with CONTINUATION_LEAD_IN_DYNAMIC."""
    pr = _pronoun(pronoun)
    c = closer or {}
    state = (f"the same pose the previous beat ended on ({c['pose']})" if c.get("pose") else "the same pose the previous beat ended on")
    state += (f" and the wardrobe as it was left ({c['wardrobe']})" if c.get("wardrobe") else
              " and the same wardrobe state the previous beat ended on")
    tpl = CONTINUATION_LEAD_IN_DYNAMIC if _beat_changes_view_or_place(scene, camera, new_shot=new_shot) else CONTINUATION_LEAD_IN
    lead = tpl.format(sub=pr["subj"].lower(), Sub=pr["subj"], poss=pr["poss"], state=state)
    action = str(scene).strip() if scene and str(scene).strip() else DEFAULT_SCENE_ACTION
    return f"{lead} {action}"


def resolve_canvas(aspect: Optional[str] = None, size: Optional[str] = None) -> Tuple[int, int]:
    """U3: (width, height) from --size WxH (multiples of 32, 256..2048) or an --aspect preset; default 768x1344."""
    if size:
        m = re.fullmatch(r"\s*(\d+)\s*[xX*]\s*(\d+)\s*", str(size))
        if not m:
            raise ValueError(f"--size must look like WxH (e.g. 1344x768), got {size!r}")
        w, h = int(m.group(1)), int(m.group(2))
        for v in (w, h):
            if v % 32 or not 256 <= v <= 2048:
                raise ValueError(f"--size {w}x{h}: each side must be a multiple of 32 within 256..2048")
        return w, h
    if aspect:
        key = str(aspect).strip().lower()
        if key not in ASPECT_PRESETS:
            raise ValueError(f"unknown --aspect {aspect!r}; choose one of {', '.join(ASPECT_PRESETS)}")
        return ASPECT_PRESETS[key]
    return DEFAULT_CANVAS


def camera_moves(camera: Optional[str]) -> bool:
    """U4: True when the camera text names camera motion (push, dolly, pan, orbit, handheld, ...)."""
    return bool(camera and _CAMERA_MOTION_RE.search(str(camera)))


def _pronoun(p: Optional[str]) -> Dict[str, str]:
    key = (p or "she").strip().lower()
    if key not in PRONOUNS:
        raise ValueError(f"--pronoun must be she, he, or they (got {p!r})")
    return PRONOUNS[key]


def concise_summary(scene_text: str) -> str:
    """Prompt tweak: long/multi-sentence scenes get their first sentence in summary (never truncated mid-sentence)."""
    text = scene_text.strip()
    sentences = [x for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    if len(text) > SUMMARY_LONG_CHARS or len(sentences) > 1:
        return sentences[0].strip()
    return text


def _clean_end(text: str) -> str:
    return str(text).strip().rstrip(".").rstrip()


def _format_end_action(subj: str, end_action: str) -> str:
    """MA-6: turn --end-action into a clean '{She|He|They} <phrase>' clause (no double subject)."""
    rest = _clean_end(end_action)
    # Drop a leading subject pronoun the caller already typed.
    rest = re.sub(r"^(She|He|They)\s+", "", rest, count=1, flags=re.IGNORECASE).strip()
    if re.match(r"^[Aa]n?\s+", rest):
        verb = "give" if subj == "They" else "gives"
        return f"{subj} {verb} {rest[0].lower() + rest[1:] if rest[:1].isupper() else rest}"
    if rest[:1].isupper() and (len(rest) == 1 or not rest[1].isupper()):
        # Leading uppercase verb -> lowercase after pronoun ("Holds..." -> "holds...")
        rest = rest[0].lower() + rest[1:]
    return f"{subj} {rest}"



_SHOT_SCALE_RE = re.compile(
    r"\b(medium-wide shot|medium wide shot|medium shot|wide shot|close-up|close shot|long shot|waist-up shot)\b",
    re.IGNORECASE,
)
_SHOT_HEIGHT_RE = re.compile(
    r"\b(hip height|eye[- ]level|chest[- ]level|waist height)\b",
    re.IGNORECASE,
)
_SHOT_LENS_RE = re.compile(r"\b(\d+)\s*mm\s+lens\b", re.IGNORECASE)
_HOLDS_RE = re.compile(r"The camera holds\s+([^.]*?)\.", re.IGNORECASE)
_VOCAL_TIMBRE_CUE_RE = re.compile(
    r"(?:signature\s+)?vocal timbre,\s*(a\s+.+?)(?=,\s*(?:wearing|styled|dressed|in a\b|in the\b)\b|[.;]|$)",
    re.IGNORECASE | re.DOTALL,
)


def _header_from_camera_sentence(scene: str, fallback: str) -> str:
    """Derive a compact [cam] header from a written 'The camera holds ...' sentence.

    Prevents DEFAULT_CAMERA (eye-level medium) from contradicting a hold already
    written in the scene. Amplitude/speed are not copied into the header.
    """
    m = _HOLDS_RE.search(scene or "")
    if not m:
        return fallback
    sent = m.group(1)
    parts: list[str] = []
    if re.search(r"\bstatic\b", sent, re.IGNORECASE):
        parts.append("static")
    sm = _SHOT_SCALE_RE.search(sent)
    if sm:
        scale = re.sub(r"\s+", " ", sm.group(1).lower()).replace("medium wide shot", "medium-wide shot")
        parts.append(scale)
    hm = _SHOT_HEIGHT_RE.search(sent)
    if hm:
        height = re.sub(r"\s+", " ", hm.group(1).lower()).replace("eye-level", "eye level")
        if height == "chest level":
            height = "chest-level"
        parts.append(height)
    lm = _SHOT_LENS_RE.search(sent)
    if lm:
        parts.append(f"{lm.group(1)}mm lens")
    if "shallow depth of field" in (fallback or "").lower():
        parts.append("shallow depth of field")
    if len(parts) <= (1 if parts and parts[0] == "static" else 0):
        return fallback
    if parts and parts[0] == "static" and len(parts) > 1:
        return ", ".join([f"{parts[0]} {parts[1]}", *parts[2:]])
    return ", ".join(parts)


def _cue_from_description(description: str) -> Optional[str]:
    if not description:
        return None
    m = _VOCAL_TIMBRE_CUE_RE.search(description)
    if not m:
        return None
    cue = re.sub(r"\s+", " ", m.group(1)).strip().rstrip(".,;:")
    return cue or None


# Short concrete pitch/texture/pace cues for the speaking line (outside <d>).
# Keyed by (actor, character), case-insensitive. Unknown pairs get no description.
VOICE_QUALITY: Dict[Tuple[str, str], str] = {
    ("sydney sweeney", "cassie howard"): "a low, soft, breathy voice with light vocal fry, unhurried",
    ("emilia clarke", "daenerys targaryen"): "a crisp British RP contralto cadence and calm authority",
}


def _norm_identity(value: Optional[str]) -> str:
    return str(value or "").strip().lower()


def _voice_quality(resolved: Dict[str, Any]) -> Optional[str]:
    """Return a short voice-quality cue from resolved data if present, else the known-pair dict."""
    for key in ("voice_quality", "voice_description", "vocal_description"):
        raw = resolved.get(key)
        if raw and str(raw).strip():
            return str(raw).strip().rstrip(".,;:")
    actor = _norm_identity(resolved.get("actor"))
    character = _norm_identity(resolved.get("character"))
    if actor and character:
        known = VOICE_QUALITY.get((actor, character))
        if known:
            return known
    return _cue_from_description(str(resolved.get("description") or ""))


def _spoken_d_line(sid: str, vt: str, spoken: str, quality: Optional[str]) -> str:
    cue = f", {quality}" if quality else ""
    return f"{sid} says in {vt} with signature vocal timbre{cue}: <d>[English] {spoken}</d>"


def _voice_target(resolved: Dict[str, Any], voice_name: str) -> str:
    """Prefer '{actor}'s exact {character} voice' when both differ; else '{voice_name}'s exact voice'."""
    character = resolved.get("character")
    actor = resolved.get("actor")
    if (
        character
        and actor
        and str(character).strip()
        and str(actor).strip()
        and str(character).strip().lower() != str(actor).strip().lower()
    ):
        return f"{actor}'s exact {character} voice"
    return f"{voice_name}'s exact voice"


def _ensure_vocal_timbre(desc: str) -> str:
    """Inject the vocal-timbre anchor after the featuring (...) prefix when missing."""
    if "vocal timbre" in desc.lower():
        return desc
    m = re.match(r"(featuring\s+.+?(?:\([^)]*\))?),\s*", desc, re.IGNORECASE | re.DOTALL)
    if m:
        return f"{m.group(1)}, distinctive facial features, exact likeness and vocal timbre, {desc[m.end():]}"
    return f"distinctive facial features, exact likeness and vocal timbre, {desc}"


def _speaker_lines(
    label: str,
    pr: Dict[str, str],
    spoken: Optional[str],
    end_action: Optional[str],
    voice_target: Optional[str] = None,
) -> str:
    """Post-speech / silent lines for one subject with clean pronoun grammar."""
    S, poss, Poss, s, does = pr["subj"], pr["poss"], pr["Poss"], pr["s"], pr["does"]
    pre = f"{label} " if label else ""
    if spoken:
        if end_action:
            first = f"{_format_end_action(S, end_action)}. "
        else:
            first = f"{S} hold{s} eye contact, give{s} a small nod at the end, and stop{s} talking. "
        return f"{pre}{first}{Poss} mouth movements stop completely after the sentence."
    line = f"{pre}{S} {does} not speak; {poss} lips stay closed and relaxed for the whole shot."
    if end_action:
        line += f" {_format_end_action(S, end_action)}."
    return line


def _subject_name(resolved: Dict[str, Any]) -> Tuple[str, str]:
    character = resolved.get("character")
    actor = resolved.get("actor")
    names = resolved.get("names", []) or []
    primary = character or actor or (names[0] if names else "Subject")
    return primary, character or actor or primary


def _subject_desc(resolved: Dict[str, Any], primary: str) -> str:
    desc = resolved.get("description")
    if not desc or not str(desc).strip():
        raise ValueError(
            f"Resolved identity for '{primary}' is missing 'description'. "
            "A concrete biometric description is required."
        )
    return dedupe_satire_tone(dedupe_featuring(str(desc).strip()))


def _format_diegetic_sound(ambience: Optional[str], n_voices: int) -> str:
    """Plain 1-4 sentence diegetic sound tail. No official H3 overall_soundscape header."""
    amb = (ambience or "").strip().rstrip(".;,") or "quiet room ambience, soft natural room tone"
    amb_sent = amb[:1].upper() + amb[1:] if amb else amb
    if n_voices >= 3:
        voice = "with three close-micd human voices in the foreground, one speaker at a time"
    elif n_voices == 2:
        voice = "with two close-micd human voices in the foreground, one speaker at a time"
    elif n_voices == 1:
        voice = "with the single close-micd human voice in the foreground"
    else:
        voice = "with no spoken voice"
    return (
        f"{amb_sent}, {voice}. "
        "No extra dubbing, no studio VO, no dubbing actors, no voice actors."
    )


def format_parody_prompt(
    resolved: Dict[str, Any],
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
    lighting: Optional[str] = None,
    camera: Optional[str] = None,
    pronoun: Optional[str] = None,
    end_action: Optional[str] = None,
    summary_text: Optional[str] = None,
    image_count: int = 0,
    image_role: Optional[str] = None,
    resolved2: Optional[Dict[str, Any]] = None,
    dialogue2: Optional[str] = None,
    pronoun2: Optional[str] = None,
    ambience: Optional[str] = None,
    resolved3: Optional[Dict[str, Any]] = None,
    dialogue3: Optional[str] = None,
    pronoun3: Optional[str] = None,
) -> str:
    """Format prompt adhering to Malcolm sample block standards and adults-only guard.

    KTD1: caller scene action goes into detailed_description (no fixed standing pose) and a
    repeated 'featuring' clause is collapsed. KTD2: voice label prefers the named character,
    <d> holds spoken words only, and an empty dialogue renders a silent clip.
    U2 (t289u): an --image is a frame-0 MiniMaxH3AddGuide keyframe, never named in the text. image_count and
    image_role are accepted for API compatibility only: no <Picture N>, [reference generation] or
    retention_analysis, so Qwen sees the same text-only prompt as a run without --image (voice fidelity).
    U4: --camera, --pronoun, --end-action, optional (S2). No word caps anywhere (t263u).
    """
    primary_name, voice_name = _subject_name(resolved)
    desc = _ensure_vocal_timbre(_subject_desc(resolved, primary_name))
    vt1 = _voice_target(resolved, voice_name)
    pr1 = _pronoun(pronoun)

    two = resolved2 is not None
    three = resolved3 is not None
    multi = two or three
    if two:
        name2, voice2 = _subject_name(resolved2)
        desc2 = _ensure_vocal_timbre(_subject_desc(resolved2, name2))
        vt2 = _voice_target(resolved2, voice2)
        pr2 = _pronoun(pronoun2)
    if three:
        name3, voice3 = _subject_name(resolved3)
        desc3 = _ensure_vocal_timbre(_subject_desc(resolved3, name3))
        vt3 = _voice_target(resolved3, voice3)
        pr3 = _pronoun(pronoun3)
    spoken = validate_spoken_dialogue(dialogue)
    spoken2 = validate_spoken_dialogue(dialogue2) if two else None
    spoken3 = validate_spoken_dialogue(dialogue3) if three else None

    scene_text = str(scene).strip() if scene and str(scene).strip() else None
    if summary_text and str(summary_text).strip():
        scene_summary = _clean_end(summary_text)
    elif scene_text:
        scene_summary = _clean_end(concise_summary(scene_text))
    else:
        scene_summary = f"{primary_name} stands calmly, looking into the camera before delivering a statement"
    scene_action = (scene_text or DEFAULT_SCENE_ACTION).rstrip().rstrip(".").rstrip()
    lighting_text = str(lighting).strip().rstrip(".") if lighting and str(lighting).strip() else None
    if lighting_text:
        scene_line = f"{scene_action}, {lighting_text}"
    elif scene_implies_lighting(scene_action):
        scene_line = scene_action
    else:
        scene_line = f"{scene_action}, {DEFAULT_LIGHTING}"

    cam = _clean_end(camera) if camera and str(camera).strip() else DEFAULT_CAMERA
    cam = cam.strip("[]").strip()
    explicit = bool(camera and str(camera).strip() and cam != DEFAULT_CAMERA.strip("[]").strip())
    if not explicit:
        cam = _header_from_camera_sentence(scene_action, cam)
    cam_tail = f" {STATIC_CAMERA_TAIL}" if STATIC_CAMERA_TAIL else ""

    audio_timbre_line = "\n<Audio 1> is the voice-timbre reference for <Subject 1>." if audio_ref else ""

    subj_lines = f"(S1) {primary_name} - {desc}{audio_timbre_line}"
    if two:
        subj_lines += f"\n(S2) {name2} - {desc2}"
    if three:
        subj_lines += f"\n(S3) {name3} - {desc3}"

    silent = []
    if not spoken:
        silent.append("(S1)")
    if two and not spoken2:
        silent.append("(S2)")
    if three and not spoken3:
        silent.append("(S3)")
    non_speaking = ", ".join(silent) if silent else "none"

    label1 = "(S1)" if multi else ""
    blocks = []
    d_lines = []
    if spoken:
        d_lines.append(_spoken_d_line("(S1)", vt1, spoken, _voice_quality(resolved)))
    if spoken2:
        d_lines.append(_spoken_d_line("(S2)", vt2, spoken2, _voice_quality(resolved2)))
    if spoken3:
        d_lines.append(_spoken_d_line("(S3)", vt3, spoken3, _voice_quality(resolved3)))
    if d_lines:
        blocks.append("<scenedirect>\n" + "\n".join(d_lines) + "\n</scenedirect>")
    blocks.append(_speaker_lines(label1, pr1, spoken, end_action, voice_target=vt1))
    if two:
        blocks.append(_speaker_lines("(S2)", pr2, spoken2, None, voice_target=vt2))
    if three:
        blocks.append(_speaker_lines("(S3)", pr3, spoken3, None, voice_target=vt3))
    speech_block = "\n".join(blocks)

    n_voices = int(bool(spoken)) + int(bool(spoken2)) + int(bool(spoken3))
    sound_tail = _format_diegetic_sound(ambience, n_voices)

    s_prefix = "" if multi else "(S1) "

    prompt = f"""subject_definitions:
{subj_lines}

summary:
{s_prefix}{scene_summary}. Non-speaking characters: {non_speaking}.

detailed_description:
[{cam}]
{s_prefix}{scene_line}.{cam_tail}
{speech_block}

{sound_tail}"""

    # Validate against adults guard (guard_ok + an adult statement, same as run_queue's gate)
    if not comm.guard_ok(prompt):
        raise ValueError(f"Prompt failed comm.guard_ok check:\n{prompt}")

    return prompt


# --- 2026-11-11 builder fix (Derrick t825u, Prompt maker writer-test FINAL): writer-output finalizer ------------
# A free-text writer prompt (OC RefMod lane) goes through finalize_writer_prompt() before it is embedded in c0.
# It strips what the writer test showed the writers paste (labeled sound/music headers, render dials, policy and
# "no" lists, self-grading retention text, absent inputs, duplicate blocks, then/after/next, quoted speech and
# ellipses, "locked" next to a push-in), and rebuilds the R5 sections with the
# R6 tag, R11 clauses + hand line, R12 wardrobe end state, R16 opening-from-still beat, R17 primary motion with
# tempo, R19 contact line, OC speech form (<d>, 1-2 lines per speaker) and one R23 camera sentence, then gates
# leg / facing / surface consistency. Library function only (no CLI flag); rule wording from h3-prompting R1-R31.
# pmfix4 (Derrick t39u/t40u/t839s3396, round 3): pySBD sentence units with atomic <d> lines and a silent-drop invariant,
# a wardrobe/position state tracker that writes the wardrobe line from the end state, a lint + targeted writer repair
# loop (max 2 rounds, via the comm.llm writer path), one closed camera-move set with one end framing, one OC speech form
# with a per-clip speech budget, raw-text opener detection. No skin-wording filter (the writer's skin words stay as
# written), no length cap, no age/youth word gate.
# dynsafe (2026-11-11, Derrick t903u; Prompt maker research render-builder-dynamic-safeguards-2026-11-11.md): the five
# leftover limits are now safeguards, not templates. The still's facts are the reference, the writer's sentence is the
# default, the builder flags conflicts, repairs at noun level, sends anything bigger back to the writer, and inserts
# template text only where the writer left a gap. Camera: a hold or pull-out stays (no forced push-in / two-shot).
# Skin: flag-only (report 'skin_unrequested'), lighting sentences untouched. Pose: the writer's opener and the still's
# pose win; no forced lying-down BJ or forced undress; one bridge sentence only when the writer has no move. Garments:
# the still's own garment phrases are the inventory. Setting: no bedroom default; no still read = NOT_READY.
from typing import Callable

class WriterPromptError(ValueError):
    """The writer prompt cannot be built (consistency gate)."""


class WriterNotReady(WriterPromptError):
    """dynsafe hard stop: the clip is NOT_READY (no still read, act missing, minor descriptor, unfixed conflict)."""


R11_PICTURE = "<Picture 1> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 1>"
R11_SUBJECT = ("<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of "
               "this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity")
R11_HAND = "HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, no melt, merge or extra digit"
TASK_TAG = "[reference generation]"

_SECTION_RE = re.compile(
    r"^\s*(?:#+\s*|\*\*)?(subject_definitions|summary|retention_analysis|detailed_description|continuation|"
    r"integrated_multimodal_description|overall_soundscape|non_diegetic_music|diegetic[ _]sound(?:scape)?|"
    r"soundscape|sound|audio|music)\s*(?:\*\*)?\s*:\s*",
    re.IGNORECASE | re.MULTILINE,
)
_SOUND_HEADERS = {"overall_soundscape", "diegetic sound", "diegetic_sound", "diegetic soundscape",
                  "diegetic_soundscape", "soundscape", "sound", "audio"}
_MUSIC_HEADERS = {"non_diegetic_music", "music"}
_DIAL_RE = re.compile(
    r"\b(seed|\d{2,4}\s*(?:f|frames)\b|\d{3,4}\s*[x×]\s*\d{3,4}|9:16|16:9|aspect|fps|beta7|int8|1-pass|one-pass|"
    r"sampler|euler|\d+\s*steps\b|cfg\b|sigma ?shift|lora|refmod(?:s)?\b|minimaxh3_|technical\s*:|cell \d+ of \d+|"
    r"\d+(?:\.\d+)?\s*-?\s*seconds?\b|10eros|h3-max|ref2va|ref2av|comfy)",
    re.IGNORECASE,
)
_POLICY_RE = re.compile(
    r"\b(?:age[- ]?play|minors?|underage|18\+|real[- ]person|likeness|celebrity|INDEX voice|"
    r"adults? only|all adults|R\d{1,2}|h3-prompting|"
    r"(?:safety|adults?|content|system)\s+guards?|guardrails?|"
    r"content\s+policy|safety\s+policy|the\s+policy|"
    r"rule\s+R\d{1,2}|prompt\s+rules?|(?:safety|content)\s+rules?|"
    r"(?:the|this)\s+prompt|prompt\s+(?:maintains|complies|adheres|format|rule|instructions?)|"
    r"timestamps?)\b",
    re.IGNORECASE,
)
_SELF_GRADE_RE = re.compile(
    r"\b(adheren|respected|complies|compliance|maintains strict|is followed|rules?\s+(?:is|are)\s+(?:respected|followed|complied|adhered|observed|met)|as required|"
    r"single shot, no timestamps|per the brief|the brief)\b",
    re.IGNORECASE,
)
_NEGATION_START_RE = re.compile(r"^\s*(no|never|without|do not|don't|nothing|avoid|not)\b", re.IGNORECASE)
_NEGATION_LIST_RE = re.compile(r"\bno\s+[\w-]+(?:\s+[\w-]+)?\s*(?:,|\band\b|\bor\b)\s*no\b", re.IGNORECASE)
_NEGATION_CLAUSE_RE = re.compile(
    r",?\s*\b(?:with no|without any|without|never|no)\s+(?:cuts?|freeze|freezing|pause|pauses|music|score|"
    r"soundtrack|narration|text|logos?|zoom|pan|tilt|other people|extra people|reset|resets|jump)\b[^.,;]*",
    re.IGNORECASE,
)
_ABSENT_REF_RE = re.compile(r"<(?:Video \d+|Picture [2-9]\d*|Audio [2-9]\d*|Subject [4-9]\d*|Shot Reference \d+)>|fully_copy",
                            re.IGNORECASE)
_MUSIC_RE = re.compile(r"\b(music|score|soundtrack|song|melody|beat drops|bass line|synth)\b", re.IGNORECASE)
_CAMERA_MOVE_RE = re.compile(r"\b(push(?:es|ing)?[- ]in|pull(?:s|ing)?[- ](?:out|back)|dolly|dollies|zoom(?:s|ing)?|track(?:s|ing)?|"
                             r"arc(?:s|ing)?|pan(?:s|ning)?|tilt(?:s|ing)?|truck(?:s|ing)?|pedestal|crane)\b", re.IGNORECASE)
_CAMERA_STATIC_RE = re.compile(r"\b(locked|locked-off|static|holds? (?:a |the )?(?:static|steady|fixed)|fixed framing|tripod)\b",
                               re.IGNORECASE)
_STANDING_RE = re.compile(r"\b(stand|stands|standing)\b", re.IGNORECASE)
_TEMPO_RE = re.compile(r"\b(per second|every (?:half )?second|cycle|bpm|tempo|strokes? a second|beats? a second)\b", re.IGNORECASE)
_CONTACT_RE = re.compile(
    r"(?=.*\b(?:penis|vagina|anus|mouth|vulva|vulvas|clitoris|clit|shaft|lips|fist|tongue|fingers)\b)"
    r"(?=.*\b(?:inside her|inside her mouth|fully sheathed|hips flush|flush against|buried in her|deep in her|sheathed|"
    r"vulva (?:is )?(?:pressed to|against) (?:\(S[123]\)'s |<Subject [123]>'s |her )?vulva|vulvas? pressed together|(?:wrapped )?around his (?:penis|shaft)|"
    r"(?:mouth|lips|tongue) (?:is |moves |presses |sealed )?(?:on|against|over) (?:the other woman's |her |\(S[123]\)'s |<Subject [123]>'s )?(?:vulva|clitoris|clit))\b)",
    re.IGNORECASE | re.DOTALL,
)
_CAMERA_SENTENCE_RE = re.compile(r"^\s*(?:\[Shot \d+\]\s*)?(?:the |a |one )?(?:camera|lens|\d{2,3}\s?mm|shot on|framing|(?:held,?\s+)?(?:medium|full|wide|tight)(?:[- ](?:full|wide|close))?[- ]shot|(?:medium )?close-up|low[- ]angle|high[- ]angle|eye[- ]level|static medium shot|the held medium shot)\b", re.I)
_LABELS = [
    (re.compile(r"(?<![(<\w])S1(?![)\w])"), "(S1)"),
    (re.compile(r"(?<![(<\w])S2(?![)\w])"), "(S2)"),
    (re.compile(r"(?<![(<\w])S3(?![)\w])"), "(S3)"),
    (re.compile(r"\bPool Blonde\b", re.I), "<Subject 1>"),
    (re.compile(r"\bAdam(?: Jensen)?\b|\bJensen\b"), "<Subject 2>"),
    (re.compile(r"\[(Subject|Audio|Picture) (\d+)\]"), r"<\1 \2>"),
    (re.compile(r"\(S([123])\)\s*<Audio 1>\s*(?:\([^)]*\))?\s*:?\s*"), r"(S\1) "),
    (re.compile(r"^\s*(?:ambient|ambience|sound|sounds|audio|sfx|foley|dialogue|speech)\s*:\s*", re.I), ""),
]
_D_RE = re.compile(r"<d>(.*?)</d>", re.IGNORECASE | re.DOTALL)
_QUOTE_RE = re.compile(r"[\"“]([^\"”]{2,240})[\"”]")

_LEG_CATEGORIES = {
    "legs over his shoulders": re.compile(r"\b(legs|ankles|calves|feet|heels)\b[^.]{0,30}\b(over|on|onto|against) his shoulders\b", re.I),
    "legs wrapped around him": re.compile(r"\b(legs|thighs|ankles|heels)\b[^.]{0,30}\b(wrap\w*|lock\w*|hook\w*|cross\w*)\b[^.]{0,20}\b(around|behind) (his|him)\b", re.I),
    "thighs around his head": re.compile(r"\bthighs\b[^.]{0,20}\b(clamp|squeeze|grip)\w*\b[^.]{0,10}\bhis head\b", re.I),
}
_FACING = {
    "facing him": re.compile(r"\b(facing him|face[- ]to[- ]face|chest to chest|eyes locked on his)\b", re.I),
    "facing away": re.compile(r"\b(facing away|back to him|her back to his chest|reverse)\b", re.I),
}
_FLOOR_BODY_RE = re.compile(r"(?:\b(?:she|he|they)\b|<Subject [123]>|\(S[123]\))\s+(?:\w+\s+){0,3}?(?:lies|lie|kneels|kneel|drops to all fours|straddles)\b[^.;]{0,40}\b(?:on|across|onto) the (?:wood(?:en)? |bare )?floor\b", re.I)


_RETENTION_LINE_RE = re.compile(r"(fully_preserved|partially_preserved|attribute_transfer|weak_reference|\(appears in \[Shot \d+\]\))", re.I)
_HAND_COPY_RE = re.compile(r",?\s*HAND ANATOMY HARD-LOCKED[^;.]*[;.]?", re.I)
_PHASE_LABEL_RE = re.compile(r"(?:^|(?<=[.!?]\s))\s*(?:First[- ]frame anchor|Action onset|Continuous development|Result(?: and reaction)?)\s*:\s*", re.I)
_PRIMARY_RE = re.compile(r"primary motion\s*[-—–:]", re.I)
# dynsafe (limit 3): the opener is pose-generic (stand / kneel / sit / lie / lean), not stand-only
# Max Architect 3, Derrick t1437s5374 (2026-11-13): c1b: a continued clip's inherited pose ('on her hands and knees', 'bent forward') is an opener pose too
_POSE_WORDS = r"(?:stand|stands|standing|kneel|kneels|kneeling|sit|sits|sitting|lie|lies|lying|lean|leans|leaning|crouch\w*|perch\w*|on (?:her )?hands and knees|on all fours|on her back|bent forward|bends? forward|straddl\w*)"
_OPENER_RE = re.compile(r"\b(?:first-frame anchor|at first|the opening frame|opens? (?:on|locked on))\b[^.]*\b" + _POSE_WORDS + r"|"
                        r"\b" + _POSE_WORDS + r"\b[^.]{0,80}\b(?:<Picture 1>|the still|the photograph|exactly as)|"
                        r"^(?:\[Shot \d+\]\s*)?<Subject 1> " + _POSE_WORDS + r" facing the (?:lens|camera)\b|"
                        r"^(?:\[Shot \d+\]\s*)?At first,?\s+(?:<Subject 1>|\(S1\)|she\b)", re.I)
_STAND_SENT_RE = re.compile(r"\b(stand|stands|standing)\b", re.I)
_GARMENT_RE = re.compile(r"\b(bra|panties|thong|briefs|knickers|lingerie|garter\w*|stocking\w*|thigh-highs?|choker|set)\b", re.I)
_HIS_CLOTHES_RE = re.compile(r"\b((?:his )?(?:dark )?trousers visible|stays? bunched (?:at|around|about) his (?:knees|ankles|thighs|shins)[^,;.]*|pulls? (?:his|the) (?:black )?(?:t-)?shirt[^,;.]*|"
                             r"hauls? the (?:black )?(?:t-)?shirt[^,;.]*|drops? his trousers|his hand reaching to his waistband[^,;.]*|"
                             r"pulling them down|leaving them in a heap|unbuckl\w*[^,;.]*|unzip\w*[^,;.]*|his trousers;?)\b", re.I)
_PENETRATION_RE = re.compile(r"\b(sheathed|fully seated|inside her|enters her|enters|seats fully|astride)\b", re.I)
_ORPHAN_RE = re.compile(r"^(?:It|They|This|These)\b")
_DANGLING_RE = re.compile(r",\s*his trousers;|\b(?:one\s+)?(?:continuous|single)\s*\.", re.I)
_ABSENT_GARMENT_RE: Optional["re.Pattern[str]"] = None  # set per call from cast["absent_garments"]

# _ASIDE_RE: pull-aside wording that clears the join without being an undress beat (W5 matcher).
# Includes "to one side" so a repair that paraphrases "aside" still counts, and is not treated as undress.
_ASIDE_RE = re.compile(r"(?i)\b(?:aside|to one side)\b")
_ASIDE_OBJ = r"(?:it|them|the [\w -]+|her [\w -]+)"
_REMOVE_VERB_RE = re.compile(r"\b(peel\w*|slip\w*|pop(?:s|ping)? free|roll\w* (?:down|off)|pool\w* at|unclip\w*|unhook\w*|unclasp\w*|"
                             r"pulled aside|pulled to one side|hangs open|kick\w* (?:free|off|away)|takes? off|took off|strip\w*|remov\w*|slid\w* (?:down|off)|"
                             r"slides? (?:it|them|the [\w ]+) (?:down|off)|drops? (?:it|them)|steps? out of|tugs? (?:it|them|the [\w ]+) (?:down|off)|"
                             r"lets? (?:it|them) (?:fall|drop)|falls? (?:away|to the floor)|discard\w*|toss\w*|"
                             # pmfix4 (Prompt maker v2 review fix 2)
                             # Max Architect 3, Derrick t1132u/t1134u: also credit slides/pulls/tugs ... aside or to one side
                             r"releas\w*|comes? off|slid(?:e|es|ing)? " + _ASIDE_OBJ + r" (?:aside|to one side)|pull\w* " + _ASIDE_OBJ + r" (?:aside|to one side)|tugs? " + _ASIDE_OBJ + r" (?:aside|to one side)|lands? on the floor|land(?:s|ing)? [^,;.]*\bon the [\w ]*floor|over (?:her|his) head|held [^,]* by her fingers)\b", re.I)
def _join_cleared_still_on(plain: str) -> bool:
    """Pull-aside or slide-up / bunched clear the join; the garment stays on (not an undress beat).

    'Tosses it aside' / 'peels off ... tosses it aside' is a discard, not a pull-aside.
    """
    if not (plain or "").strip():
        return False
    if re.search(
        r"(?i)\b(?:toss\w*|throw\w*|fling\w*|cast\w*|chuck\w*|drop(?:s|ped|ping)?)\s+(?:\w+\s+){0,4}aside\b",
        plain,
    ):
        return False
    if re.search(r"(?i)\b(?:takes? off|took off|peels? off|strips? off|removes?)\b", plain) and not re.search(
        r"(?i)\b(?:pull\w*|slid\w*|tug\w*|hook\w*)\s+(?:it|them|(?:the|her) [\w -]+)\s+(?:aside|to one side|up)\b",
        plain,
    ):
        return False
    if _ASIDE_RE.search(plain):
        return True
    if re.search(r"(?i)\bslid(?:e|es|ing)?\s+(?:it|them|(?:the|her) [\w -]+)\s+up\b", plain):
        return True
    if re.search(r"(?i)\b(?:bunches and stays|hiked up|pushed up to her)\b", plain):
        return True
    return False


def _not_an_undress_beat(plain: str) -> bool:
    """Join-clearing motion, including 'hangs open', is not taking the garment off.
    'bunches at her waist' / 'bunches around her waist' is gathered-on, not a removal (PM acc4 #5)."""
    if _join_cleared_still_on(plain) or re.search(r"(?i)\bhangs open\b", plain or ""):
        return True
    return bool(re.search(
        r"(?i)\bbunch(?:es|ing|ed)?\s+(?:up\s+)?(?:around|at|to)\s+(?:her\s+)?(?:waist|midriff|hips|ribs)\b",
        plain or ""))


def _w5_covered_garments(cast: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    """Join garments still on and not pulled aside / slid up (W5)."""
    aside = set(state.get("writer_aside") or [])
    return [g["name"] for g in _cast_items(cast) if (g["key"] in _JOIN_KEYS or g.get("slot") == "full-body")
            and state["garments"].get(g["key"]) == "on" and g["key"] not in aside]


_MOVE_SOUND_RE = re.compile(r"\b(walks?|steps?|sits?|turns?|kneels?|lowers?|climbs?|crawls?|settles?|lies|lying|straddl\w*|"
                            r"room tone|creak\w*|slap\w*|rustl\w*|hum|grunt\w*|whisper\w*|moan\w*|gasp\w*|breath\w*|exhale\w*)\b", re.I)
_SPEECH_VERB = (r"(?:says?|said|growls?|moans?|whispers?|answers?|gasps?|pants?|begs?|groans?|snarls?|breathes?|murmurs?|rasps?|"
                r"orders?|commands?|grunts?|hisses?|urges?|demands?|tells? (?:her|him)|speaks?|calls? out)")
_MOUTH_MOVES_RE = re.compile(r"(?i)\b(?:Her|His|Their) mouth moves as (?:<Subject [123]>|\(S[123]\))[^:<\x00]*:\s*")
_MATCHING_RE = re.compile(r"(?i),?\s*matching (?:the vocal (?:texture|timbre) of <Audio 1>|his character reference|<Audio 1>)")
_TEN_SEC_RE = re.compile(r"(?i)\s*(?:across|for|over|through)?\s*(?:the\s+)?(?:full\s+)?(?:ten|10)[- ]seconds?\b")
_NEG_MAP = [
    (re.compile(r"(?i)\bdoes not slow\b|\bdoesn't slow\b|\bnever slows\b"), "holds its pace"),
    (re.compile(r"(?i)\bnothing settled\b"), "everything still moving"),
    (re.compile(r"(?i)\bnot yet begun\b"), "about to begin"),
    (re.compile(r"(?i),?\s*with nothing new added\b"), ""),
]
_NEG_WORD_RE = re.compile(r"(?i)\b(?:not|never|nothing|no)\b")
_W5_CLEAR_CLAUSE_RE = re.compile(
    r"(?i)(?:,\s*)?so nothing covers (?:her vulva or his penis|his penis or her vulva|the join|her vulva|his penis)")
_DASH_COMMA_RE = re.compile(r"\s*[—–]\s*,")
_CAM_ECHO_RE = re.compile(r"(?i),?\s*the camera still in its [^,.;]*")
_THROAT_RE = re.compile(r"(?i)\b(?:hand|fingers?|palm) (?:slides?|wraps?|closes?|moves?) (?:up )?(?:to|around|on) her throat\b|\b(?:grips?|squeezes?|holds?|chokes?) her throat\b")
_DOGGY_BACK_RE = re.compile(r"(?i)\bpresses her back (?:down )?(?:against|into|to) the (?:mattress|sheets|bed)")
_PUBIC_RE = re.compile(r"(?i)\bpubic bone press\w* (?:against |into )?her lower back")
_ABSENT_SPAN_RE = re.compile(r"(?i)\bin (?:the |a )?(?:sheer )?(?:beige |nude |white |black )?(?:chemise|blouse|slip dress|nightgown|robe)"
                             r"[^;.]*?(?=,\s*(?:hands|weight|bare|exactly|facing)|;|\.|$)")
# pmfix5 (B): light skin rule. Redness nobody asked for goes clause by clause; gloss goes only when the brief/ask does
# not mention oil, wet, sweat or similar. No default matte cue.
_REDNESS_RE = re.compile(r"(?i)\bflush(?:ed|ing)? (?:red|pink|crimson|scarlet)\b|\bflush(?:es)? (?:rises?|rising|spreads?|spreading|creeps?|climbs?)\b|"
                         r"\bflush (?:rising|spreading|across|over|on|down)\b|"
                         r"\b(?:skin|face|cheeks?|chest|neck|throat|back|shoulders?|breasts?|thighs?|buttocks?|ears?)\b[^,;.]{0,25}\b(?:is |are |looks? )?flushed\b|"
                         r"\bflushed (?:skin|face|cheeks?|chest|neck)\b|\b(?:her|his) face (?:is |looks )?flushed\b|"
                         r"\b(?:leav\w*|leaves?) (?:\w+ )?red marks?\b|\bred (?:marks?|welts?|blotch\w*|patch\w*|handprints?|hand-?prints?|streaks?|lines?|blush)\b|"
                         r"\bblotch\w*\b|\b(?:redden\w*|pinken\w*)\b|\b(?:skin|cheeks?|hip|buttocks?|ass)\b[^,;.]{0,25}\b(?:red|pink|crimson|scarlet)\b")
_REDNESS_ASK_RE = re.compile(r"(?i)\b(?:flush\w*|blush\w*|red|redd\w*|marks?|welts?|spank\w*|slap marks?|handprints?)\b")
_GLOSS_RE = re.compile(r"(?i)\b(?:glisten\w*|sheen|glossy|gloss|oiled|oily|shiny|shine|shining|slick with (?:sweat|oil)|sweat-?slick\w*|dewy|sweat\w*|wet and shiny)\b")
_GLOSS_BODY_RE = re.compile(r"(?i)\b(?:skin|shoulders?|chest|breasts?|back|thighs?|hips?|body|bodies|belly|stomach|buttocks?|arms?|legs?|neck|face|forehead|collarbones?)\b")
_GLOSS_ASK_RE = re.compile(r"(?i)\b(?:oil\w*|wet|sweat\w*|glisten\w*|sheen|gloss\w*|shiny|slick|damp|dewy|lotion|lube\w*)\b")
_AN_RE = re.compile(r"\b([Aa]) (?=(?:[aeio](?!ne\b|nce\b)[\w-]|eye))")
_PRON_COMMA_RE = re.compile(r"\b([Hh]e|[Ss]he),\s+(?=[a-z]+s\b)")
_SUMMARY_STRIP_RE = re.compile(r"(?i)<Subject 2> strips her [^;.]*?(?=\s+and\b|[;.])")
_OPENER_LIST_RES = (re.compile(r"(?i)\bin (?:the |a )?sheer [^;.]*?\b(?:stockings|choker)\b(?:,? and (?:a |the )?(?:thigh-high stockings|stockings|choker)\b)?"),
                    re.compile(r"(?i),?\s*the sheer [^;.]*?\b(?:stockings|choker)\b(?=\s+exactly as)"))
_FRAGMENT_START_RE = re.compile(r"^(?:At first,\s*and\b|Exactly as in\b|[a-z])")
_SUBJECT_WORD_RE = re.compile(r"(?i)\b(?:she|he|her|his|the|their|both|all|its)\b|<Subject [123]>|\(S[123]\)")
_TAIL_ITEM_RE = re.compile(r"^(?:and\s+)?(?:her\s+|his\s+)?[a-z]+$")
# camera: one closed set of moves (MiniMax hosted list / Wan I2V / Reddit H3: one motivated move per short clip)
# dynsafe (limit 1): the full official verb list (base-en.txt 4.3): arc and zoom are official, a hold is a valid shot
CAMERA_MOVES = ("push in", "pull out", "zoom", "pan", "tilt", "truck", "pedestal", "arc", "tracking", "static")
_CAM_SYNONYMS = [
    (re.compile(r"(?i)\b(?:dolly|dollies|dollying|creeps?|creeping|moves?|moving|drifts?|drifting) (?:slowly )?(?:in|closer|forward)\b"), "pushes in"),
    (re.compile(r"(?i)\b(?:dolly|dollies|dollying|pulls?|pulling|draws?|drawing) (?:slowly )?(?:out|back)\b"), "pulls out"),
    (re.compile(r"(?i)\b(?:orbits?|orbiting)\b"), "arcs"),
    (re.compile(r"(?i)\blocked[- ]off\b|\blocked\b(?= (?:shot|frame|camera|framing))"), "static"),
]
_CAM_CLASS = [
    ("push in", re.compile(r"(?i)\bpush(?:es|ing)?[- ]in\b|\bpush-in\b")),
    ("pull out", re.compile(r"(?i)\bpull(?:s|ing)?[- ](?:out|back)\b|\bpull-out\b")),
    ("zoom", re.compile(r"(?i)\bzoom(?:s|ing)?\b")),
    ("pan", re.compile(r"(?i)\bpan(?:s|ning)?\b")),
    ("tilt", re.compile(r"(?i)\btilt(?:s|ing)?\b")),
    ("truck", re.compile(r"(?i)\btruck(?:s|ing)?\b")),
    ("pedestal", re.compile(r"(?i)\bpedestal\w*\b|\bcrane\w*\b")),
    ("arc", re.compile(r"(?i)\barc(?:s|ing)?\b")),
    ("tracking", re.compile(r"(?i)\btrack(?:s|ing)?\b")),
]
_STILL_ACTS = ("missionary", "doggy", "blowjob")  # stationary acts: a track needs a moving subject (E30a)
_WIDE_END_RE = re.compile(r"(?i)\b(?:wide|long|full|full-body|extreme wide)[- ](?:body )?shot\b|\bfull-body\b|\bwide framing\b")
_END_FRAME_RE = re.compile(r"(?i)\b(?:stops? at|ends? (?:on|moving|at)|ending (?:on|at)|final framing|settl(?:es?|ing) (?:on|into)|arriv(?:es?|ing) at|"
                           r"to a [\w -]*two-shot|(?:into|to|toward|towards) (?:a |an )?[\w ,-]*?(?:shot|close-up|framing|angle|view))\b")  # dynsafe: arriving at / angle / view end framings
_ACT_RE = re.compile(r"(?i)\b(?:thrust\w*|strokes?|stroking|rides?|riding|pump\w*|grind\w*|bounc(?:es|ing) (?:on|up|down|in)\w*)\b")  # 'warm bounce off the floor' is light
_STAND_ASSERT_RE = re.compile(r"(?i)(?:\bshe\b|<Subject 1>)\s+(?:\w+\s+){0,2}?(?:stands|is standing|stands up)\b")
_MOVE_LEVEL_RE = re.compile(r"(?i)\b(walks?|steps? (?:to|toward|onto)|sits?|turns? (?:to|toward)|kneels?|climbs?|crawls?|lowers?)\b")


def _protect_d(text: str) -> Tuple[str, List[str]]:
    spans: List[str] = []

    def keep(m):
        spans.append(m.group(0))
        return f"\x00{len(spans) - 1}\x00"
    return _D_RE.sub(keep, text), spans


def _restore_d(text: str, spans: Sequence[str]) -> str:
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


_SEG = None
_TOKEN_RE = re.compile(r"<(?:Subject|Picture|Audio) \d+>|\(S[12](?:,\s*S[12])?\)|\[Shot \d+\]|\x00\d+\x00")


def _segmenter():
    """pySBD (rule-based sentence boundary detection, Golden Rules tested) - one instance per process."""
    global _SEG
    if _SEG is None:
        import pysbd
        _SEG = pysbd.Segmenter(language="en", clean=False)
    return _SEG


def _sentences(text: str) -> List[str]:
    """Sentence units. <d> placeholders, <Subject N>/<Picture N>/<Audio N>, (S1)/(S2) and [Shot N] are opaque tokens for
    pySBD; a spoken line closes its unit, so '(S1) says ..., <d>..</d> (S2) says ..., <d>..</d> The thrusts ...' is three
    units and the cap can never take a neighbour with it."""
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    if _D_RE.search(text):  # callers usually protect <d> first; protect here too so a spoken line is never split
        prot, spans = _protect_d(text)
        return [_restore_d(u, spans) for u in _sentences(prot)]
    toks: List[str] = []

    def keep(m):
        toks.append(m.group(0))
        return f"QTK{len(toks) - 1}Q"
    prot = _TOKEN_RE.sub(keep, text)
    units: List[str] = []
    for s in _segmenter().segment(prot):
        s = s.strip()
        if not s:
            continue
        cut = 0
        for m in re.finditer(r"QTK(\d+)Q", s):
            if not toks[int(m.group(1))].startswith("\x00"):
                continue
            nxt = s[m.end():]
            mm = re.match(r"[\"”]?[.,!?]*\s+(?=[A-Z\"“]|QTK)", nxt)
            if mm and nxt[mm.end():].strip():
                units.append(s[cut:m.end() + mm.end()].strip())
                cut = m.end() + mm.end()
        rest = s[cut:].strip()
        if rest:
            units.append(rest)
    return [re.sub(r"QTK(\d+)Q", lambda m: toks[int(m.group(1))], u) for u in units]


def split_writer_sections(raw: str) -> Dict[str, List[str]]:
    """Split writer output into labeled sections; duplicate copies of a section keep only the first."""
    text = re.sub(r"```[a-zA-Z]*", "", raw or "").replace("`", "")
    out: Dict[str, List[str]] = {}
    marks = list(_SECTION_RE.finditer(text))
    if not marks:
        return {"detailed_description": [text.strip()]}
    lead = text[: marks[0].start()].strip()
    if lead:
        out.setdefault("_lead", []).append(lead)
    for i, m in enumerate(marks):
        name = m.group(1).lower().replace("_", " ") if m.group(1).lower().startswith("diegetic") else m.group(1).lower()
        body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)].strip()
        out.setdefault(name, []).append(body)
    return out


def _fix_transitions(s: str) -> str:
    s = re.sub(r"\bnext to\b", "beside", s, flags=re.I)
    s = re.sub(r"^(?:then|next|afterwards?|after that)\s*,?\s+", "", s, flags=re.I)
    s = re.sub(r",?\s*\b(?:and )?then\b,?\s*", ", ", s, flags=re.I)
    s = re.sub(r"\bafterwards?\b,?\s*", "", s, flags=re.I)
    s = re.sub(r"\bafter\b", "once", s, flags=re.I)
    s = re.sub(r"\bnext\b", "following", s, flags=re.I)
    s = re.sub(r"\s+,", ",", s)
    s = re.sub(r",\s*,", ",", s)
    return s[:1].upper() + s[1:] if s else s


def _clean_d_span(span: str) -> str:
    inner = _D_RE.match(span).group(1).strip()
    inner = re.sub(r"^\[English\]\s*", "", inner, flags=re.I)
    inner = re.sub(r"\s*(?:\.\.\.|…)\s*(?=\w)", ", ", inner)  # mid-line ellipsis -> comma (H3 guide punctuation)
    inner = inner.replace("…", ".").replace("...", ".").replace("—", ", ").replace("–", ", ")
    inner = re.sub(r"\s*,\s*", ", ", inner).strip(" ,")
    inner = re.sub(r"\.{2,}", ".", inner)
    if inner and inner[-1] not in ".?!":
        inner += "."
    return f"<d>[English] {inner}</d>"


def _subject_speaker_label(text: str) -> Optional[str]:
    """The sentence subject, never an (Sx) after at/to/toward (PM acc4 #7 / Derrick t251s854)."""
    for m in re.finditer(r"\(S([123])\)|<Subject ([123])>", text or ""):
        if re.search(r"(?i)\b(?:at|to|toward|towards|with|for|from)\s+$", text[:m.start()]):
            continue
        return "S" + (m.group(1) or m.group(2))
    return None


def _speaker_of(sentence: str) -> str:
    if scene_addenda.is_offscreen_voice_sentence(sentence):
        return "OFFSCREEN"
    subj = _subject_speaker_label(sentence)
    if subj:
        return subj
    lead = re.split(r'\x00|["\u201c]', sentence)[0]
    he = len(re.findall(r"\b(he|his|him)\b", lead, re.I))
    she = len(re.findall(r"\b(she|her)\b", lead, re.I))
    if he > 0 and she == 0:
        return "S2"
    if she > 0 and he == 0:
        return "S1"
    raise WriterPromptError("A spoken line cannot be attributed to a speaker; failing closed")


def _span_speaker(before: str) -> str:
    """Speaker of a spoken line: the nearest (S1)/(S2)/(S3) or <Subject N> before it, else pronouns of the lead."""
    if scene_addenda.is_offscreen_voice_sentence(before):
        return "OFFSCREEN"
    subj = _subject_speaker_label(before)
    if subj:
        return subj
    lead = before[-160:]
    he = len(re.findall(r"\b(he|his|him)\b", lead, re.I))
    she = len(re.findall(r"\b(she|her)\b", lead, re.I))
    if he > 0 and she == 0:
        return "S2"
    if she > 0 and he == 0:
        return "S1"
    raise WriterPromptError(f"A spoken line cannot be attributed to a speaker (no (S1)/(S2)/(S3) or <Subject N> label near line); failing closed")


def speech_budget(cast: Dict[str, Any]) -> int:
    """Per-clip spoken-word budget: ~2.5 words per second of clip across speakers (our starting value, unverified)."""
    return int(round(float(cast.get("clip_seconds", 10.0)) * float(cast.get("speech_wps", 2.5))))


def _speech_form(spk: str, voices: Dict[str, str], span: str) -> str:
    """The one H3-guide OC form for every spoken line (h3-prompting SKILL.md: '(S1) ... says in a ... voice, <d>[English] ...</d>')."""
    voice = voices.get(spk)
    if not voice:  # Max Architect 3, Derrick t1437s5374 (2026-11-13): #5: no placeholder voice line for a partner with no voice (talk, absent (S2))
        return f"({spk}) says, {_clean_d_span(span)}"
    return f"({spk}) says in {voice}, {_clean_d_span(span)}"


_PREP_BEHIND = r"(?<!\bat )(?<!\bto )(?<!\bwith )(?<!\bfor )(?<!\bfrom )(?<!\btoward )(?<!\btowards )"
_LEAD_RE = re.compile(r"(?:,?\s*(?:and\s+)?)?" + _PREP_BEHIND + r"(?:\(S[123]\)\s*|<Subject [123]>\s*|\b(?:she|he|they)\s+)?(?:[\w-]+\s+){0,2}?\b" + _SPEECH_VERB +
                      r"\b(?:[^<\x00]|<(?:Audio|Subject|Picture) \d+>(?:'s)?)*$", re.I)  # pmfix5: crosses <Audio 1> (A_03/F_03 double lead)
_AUDIO_LEAD_RE = re.compile(r"(?i)\bin <Audio 1>(?:'s voice)?(?: with signature vocal timbre)?(?: as <Subject [123]>)?,?\s*")
_DOUBLE_LEAD_RE = re.compile(r"\(S[123]\) says in[^<]*\(S[123]\) says in")


def _speech_form_with_tone(spk: str, voices: Dict[str, str], span: str, tone: str = "") -> str:
    voice = voices.get(spk) or (OC_VOICE_S1 if spk == "S1" else OC_VOICE_S2)
    if tone:
        tone_words = [w for w in re.findall(r"[a-z-]+", tone.lower()) if w not in ("a", "an", "the", "voice", "and", "with", "in")]
        if tone_words and any(w not in voice.lower() for w in tone_words):
            voice = f"{voice}, {tone} tone"
    return f"({spk}) says in {voice}, {_clean_d_span(span)}"


def convert_speech(sentences: List[str], voices: Dict[str, str], max_lines: int = 2,
                   counts: Optional[Dict[str, int]] = None, ledger: Optional[List[Dict[str, Any]]] = None,
                   budget: Optional[int] = None) -> List[str]:
    """Quotes -> <d>; every spoken line is rendered in one form, '(Sx) says in <cast voice>, <d>[English] words</d>'.
    Caps: max_lines per speaker (nearest label) and a per-clip word budget. A capped line drops alone (its own lead
    goes with it, the surrounding text stays) and is written to the ledger with its reason."""
    counts = counts if counts is not None else {"S1": 0, "S2": 0, "S3": 0}
    counts.setdefault("_words", 0)
    ledger = ledger if ledger is not None else []
    out: List[str] = []
    for s in sentences:
        s = _QUOTE_RE.sub(lambda m: f"<d>[English] {m.group(1).strip()}</d>", s)
        s = _MOUTH_MOVES_RE.sub("", s)
        s = _MATCHING_RE.sub("", s)
        if "<d>" not in s.lower():
            out.append(s)
            continue
        pieces: List[str] = []
        pos = 0
        for m in _D_RE.finditer(s):
            seg = _AUDIO_LEAD_RE.sub("", s[pos:m.start()])
            spk = _span_speaker(s[:m.start()])
            words = re.sub(r"^\[English\]\s*", "", m.group(1).strip(), flags=re.I)
            n = len(words.split())
            lm = _LEAD_RE.search(seg)
            pre = seg[:lm.start()] if lm else seg
            pre = re.sub(r"(?:\(S[123]\)|<Audio 1>(?:'s voice)?|<Subject [123]>)\s*[:,]?\s*$", "", pre).rstrip(" :,;")
            tone_m = re.search(r"(?i)\bin\s+(?:a|an)\s+([^,;:.]+?)\s+voice\b", seg[lm.start():] if lm else seg)
            tone_str = tone_m.group(1).strip() if tone_m else ""
            bare = re.sub(r"\((?!S[123]\))[^)]*\)|<(?:Audio|Subject) \d+>(?:'s voice)?|\(S[123]\)|[\s:,'-]", "", pre)
            if spk == "OFFSCREEN":
                # Package 2 R18: narrated off-screen voice is not a subject, not credited, not counted.
                form = f"An off-screen voice says, {_clean_d_span(m.group(0))}"
                ledger.append({"line": words, "speaker": "OFFSCREEN", "kept": True, "reason": ""})
                if len(bare) > 12:
                    joiner = " " if pre.rstrip().endswith((".", "!", "?")) else ", and "
                    pieces.append(pre.rstrip() + joiner + form)
                else:
                    pieces.append((" " if pieces else "") + form)
                pos = m.end()
                continue
            reason = None
            if counts.get(spk, 0) + 1 > max_lines:
                reason = f"speech cap: {spk} already has {max_lines} lines"
            elif budget is not None and counts["_words"] + n > budget:
                reason = f"speech budget: {counts['_words']}+{n} words > {budget}"
            if reason:
                ledger.append({"line": words, "speaker": spk, "kept": False, "reason": reason})
                if len(bare) > 12:
                    pieces.append(pre + ("" if pre.endswith((".", "!", "?")) else "."))
                pos = m.end()
                continue
            counts[spk] = counts.get(spk, 0) + 1
            counts["_words"] += n
            ledger.append({"line": words, "speaker": spk, "kept": True, "reason": ""})
            if len(bare) > 12:
                joiner = " " if pre.rstrip().endswith((".", "!", "?")) else ", and "
                pieces.append(pre.rstrip() + joiner + _speech_form_with_tone(spk, voices, m.group(0), tone_str))
            else:
                pieces.append((" " if pieces else "") + _speech_form_with_tone(spk, voices, m.group(0), tone_str))
            pos = m.end()
        s = " ".join(p.strip() for p in pieces if p.strip()) + s[pos:]
        s = re.sub(r"(</d>)\s*[\"”]?\s*[.,]+(?=\s|$)", r"\1", s)
        s = re.sub(r"\s{2,}", " ", s).strip(" ,;")
        if len(_D_RE.sub("", s).split()) < 2 and "<d>" not in s:
            continue
        s = s[:1].upper() + s[1:]
        out.append(s)
    return out


def _is_policy(s: str) -> bool:
    plain = _D_RE.sub("", s)
    return bool(_POLICY_RE.search(plain) or _SELF_GRADE_RE.search(plain))


def _normalize_labels(s: str) -> str:
    for rx, sub in _LABELS:
        s = rx.sub(sub, s)
    return s


_CTX: Dict[str, Any] = {}  # per-call cast context for the sentence helpers (set in finalize_writer_prompt)


def _set_ctx(cast: Dict[str, Any]) -> None:
    sc = _scene(cast)
    words = set()
    for g in (still_facts(cast["still_read"])["garments"] if cast.get("still_read") else []):
        words |= set(re.findall(r"[a-z-]+", g["name"].lower()))
    _CTX.clear()
    _CTX.update(position=cast.get("position"), throat_contact=bool(cast.get("throat_contact")), **_skin_asks(cast))
    _CTX.update(still_bed=sc["bed"], surface=sc["surface"], pad_phrase=sc["pad_phrase"], still_words=words,
                skin_flags=[], camera_flags=[], ref_pictures=[s3_picture(cast)] if cast.get("s3_still") else [])


def refmod_people(mods: List[Any]) -> int:
    """(3) Derrick t247s837: one character = its audio + visual RefMods; count distinct characters."""
    names = set()
    for m in mods:
        n = str(m.get("path") if isinstance(m, dict) else m)
        n = re.sub(r"(?i)[\\/]", "/", n).split("/")[-1]
        n = re.sub(r"(?i)\.(?:safetensors|pt|bin)$", "", n)
        names.add(re.sub(r"(?i)(?:_refmod)?_(?:audio|visual|video|face)(?:_[\w-]*)?$", "", n))
    return len(names)


def s3_picture(cast: Dict[str, Any]) -> int:
    """Max Architect 3, Derrick t1440 (MMF S3, 2026-11-13): the S3 reference still is the next ref_images slot after <Picture 1> (the node numbers pictures by
    wired slot order), so it is <Picture 2> unless cast['s3_picture'] says otherwise."""
    # (4) Derrick t247s837: computed from the refs wired before it (slot after the last one), never a free override
    return 1 + max(1, int(cast.get("refs_wired_before_s3") or 1))


def _skin_asks(cast: Dict[str, Any]) -> Dict[str, bool]:
    """pmfix5 (B): what the brief/ask says about skin. cast['brief'] (or 'ask') is the user's text; cast['skin'] may say it
    too. dynsafe: the still read's skin field is a still fact (e.g. 'glossy tanned skin' keeps gloss unflagged)."""
    ask = " ".join(str(cast.get(k) or "") for k in ("brief", "ask", "skin")) + " " + str((cast.get("still_read") or {}).get("skin") or "")
    return {"redness_asked": bool(_REDNESS_ASK_RE.search(ask)), "gloss_asked": bool(_GLOSS_ASK_RE.search(ask))}


def _is_fragment(s: str) -> bool:
    """Subjectless leftovers after a clause drop ('At first, and brief from ...', 'draw them down ...')."""
    plain = _D_RE.sub("", s).strip()
    if not plain:
        return "<d>" not in s
    clauses = re.split(r"[,;:]", plain)
    first = clauses[0]
    if len(first.split()) <= 3 and len(clauses) > 1:  # 'At first, <Subject 1> stands ...': the adverbial is not the clause
        first += " " + clauses[1]
    return bool(_FRAGMENT_START_RE.match(plain)) or not _SUBJECT_WORD_RE.search(first)


# frs16 S1 (Fleet Reviewer 2026-11-11): the W4 absent-garment list is her wardrobe check only. A lexicon word whose nearest
# possessive in its clause is 'his' / 'their' / <Subject 2/3>'s ('<Subject 2> pulls off his t-shirt and jeans') is the partner's clothes,
# never W4, and never takes her undress sentence with it.
_POSS_RE = re.compile(r"(?i)\b(her|his|their)\b|<Subject ([123])>'s|\(S([123])\)'s|\b(?:partner|man|captor|master)'s\b")


def _partner_garment(text: str, start: int) -> bool:
    """True when the garment word at text[start:] belongs to the partner (S2 or S3): the nearest possessive or subject
    before it in its clause refers to the partner (walking back over comma-separated items); no possessive = hers."""
    cut = max(text.rfind(c, 0, start) for c in ";.:!?")
    clause = text[cut + 1:start]
    subjs = list(re.finditer(r"(?:<Subject ([123])>|\(S([123])\))", clause))
    if subjs:
        last_s = subjs[-1].group(1) or subjs[-1].group(2)
        after_s = clause[subjs[-1].end():]
        poss_after = list(_POSS_RE.finditer(after_s))
        if poss_after:
            m = poss_after[-1]
            return (m.group(1) or "").lower() in ("his", "their") or m.group(2) in ("2", "3") or m.group(3) in ("2", "3") or bool(re.search(r"(?i)partner|man|captor|master", m.group(0)))
        if last_s in ("2", "3"):
            return True
    for part in reversed(clause.split(",")):
        poss = list(_POSS_RE.finditer(part))
        if poss:
            m = poss[-1]
            return (m.group(1) or "").lower() in ("his", "their") or m.group(2) in ("2", "3") or m.group(3) in ("2", "3") or bool(re.search(r"(?i)partner|man|captor|master", m.group(0)))
        if len(part.split()) > 3:
            return False
    return False


def _his_garment(text: str, start: int) -> bool:
    return _partner_garment(text, start)


def _hers_text(text: str, rx: Optional["re.Pattern[str]"] = None) -> str:
    """text with the partner's absent-list garment words blanked, for the W4 (her absent garment) search only."""
    rx = rx or _ABSENT_GARMENT_RE
    if not rx:
        return text
    out, last = [], 0
    for m in rx.finditer(text):
        if _partner_garment(text, m.start()):
            out += [text[last:m.start()], "_" * (m.end() - m.start())]
            last = m.end()
    return "".join(out) + text[last:]


class _HersAbsent:
    """An absent-garment matcher that ignores the man's clothes (clause drops for W4 keep his clauses)."""

    def __init__(self, rx: "re.Pattern[str]"):
        self.rx, self.pattern = rx, rx.pattern

    def search(self, text: str):
        return self.rx.search(_hers_text(text, self.rx))


# frs16 S2: penetration of the join for the finalized W5 gate ('<Subject 2> enters at frame right' is not penetration)
_JOIN_PEN_RE = re.compile(r"(?i)\b(?:sheathed|fully seated|seats fully|inside her|(?:enters|sinks into|slides into|pushes into|thrusts into) her\b(?! mouth| throat)"
                         r"|(?:thrusts?|pushes|slides|sinks|drives) (?:deep |all the way |hard )?into her\b(?! mouth| throat| cleavage)"
                         r"|(?:buried|deep) (?:deep )?in her\b(?! mouth| throat| cleavage| hair))")  # c1a: 'thrusts deep into her', 'buried in her'
# Max Architect 3, Derrick t1437s5374 (2026-11-13): #7: no-entry acts are exempt from the W5 join gate (titjob always; finish when nothing enters her)
_ORAL_POSITIONS = ("blowjob", "titjob", "mmf_double_blowjob")
_NOPEN_POSITIONS = ("finish", "handjob")
_STAY_ON_RE = re.compile(r"(?i)\b(?:stays?|remains?|kept|left|staying) on\b")
_TAIL_FALL_RE = re.compile(r"(?i)^(?:and\s+)?(?:where\s+)?(?:they|it)\s+(?:drops?|falls?|lands?|pools?|stays?|lies?)\b")


def _drop_clauses(s: str, rx: "re.Pattern[str]", guard: bool = True) -> str:
    """Drop only the comma/semicolon clauses whose plain text (outside <d>) matches rx; keep the rest. A dropped clause
    takes a bare one-word list tail with it ('..., and cheeks'), never a real clause ('eyes half-lidded'). Returns ''
    when nothing usable is left (or, with guard, only a subjectless fragment)."""
    prot, spans = _protect_d(s)
    end = prot[-1] if prot and prot[-1] in ".!?" else ""
    parts = re.split(r"(?<=[,;.])\s+", prot.rstrip(".!?"))
    kept: List[str] = []
    tail = False
    dropped_first = False
    prefix = ""
    for i, p in enumerate(parts):
        p_plain = _D_RE.sub("", _restore_d(p, spans))
        ctx_plain = prefix + p_plain
        # NB1: when checking _HersAbsent, evaluate on the clause prefix since the last ';' so partner appositives
        # like '(S3), a petite woman in a silk camisole, kneels' keep their partner owner across commas.
        if isinstance(rx, _HersAbsent):
            hers_ctx = _hers_text(ctx_plain, rx.rx)
            hit = bool(rx.rx.search(hers_ctx[len(prefix):]))
        else:
            hit = bool(rx.search(p_plain))
        if hit:
            tail = True
            dropped_first = dropped_first or i == 0
            if p.rstrip().endswith((";", ".")):
                prefix = ""
            continue
        if tail and _TAIL_ITEM_RE.match(p.strip(" ,;.")):
            continue
        if tail and (rx is _HIS_CLOTHES_RE or rx is _ABSENT_GARMENT_RE or isinstance(rx, _HersAbsent)) and re.search(r"\b(them|it)\b", p) and (
                _REMOVE_VERB_RE.search(p) or re.search(r"\bin a heap\b|\b(?:down|off)\b", p)):
            continue
        if tail and (rx is _ABSENT_GARMENT_RE or isinstance(rx, _HersAbsent)) and _TAIL_FALL_RE.match(p.strip()):
            continue  # frs16 S1: '..., and they drop to the floor' goes with its absent-garment clause
        tail = False
        kept.append(p)
        prefix = "" if p.rstrip().endswith((";", ".")) else (ctx_plain + " ")
    if not kept:
        return ""
    out = " ".join(kept).rstrip(" ,;")
    out = _restore_d(out, spans)
    if dropped_first:
        out = re.sub(r"^(?:and|but|while|as)\s+(?=(?:he|she|his|her|their|<Subject [12]>)\b)", "", out, flags=re.I)
        out = re.sub(r"^(he|she|his|her|their)\b", lambda m: m.group(1).capitalize(), out)
    if guard and dropped_first and _is_fragment(out):
        return ""
    out = out[:1].upper() + out[1:]
    return out + end


def _unpaired_dash(t: str) -> str:
    """pmfix5: an unpaired em dash in a sentence becomes a comma (F_01)."""
    if t.count("—") % 2 == 1:
        i = t.rfind("—")
        t = re.sub(r",\s*,", ",", t[:i].rstrip(" ,") + ", " + t[i + 1:].lstrip(" ,"))
    return t


def _drop_skin_clauses(s: str, rx: "re.Pattern[str]", body: bool = False) -> str:
    """pmfix5 (B): drop only the clauses carrying unrequested skin redness/gloss. When the dropped clause was the subject
    clause, the next expression clause keeps its owner ('Her face is flushed, eyes half-lidded' -> 'Her eyes half-lidded')."""
    if body:
        rx = re.compile(r"(?=[^,;.]*(?:" + _GLOSS_RE.pattern.replace("(?i)", "") + r"))(?=[^,;.]*(?:" +
                        _GLOSS_BODY_RE.pattern.replace("(?i)", "") + "))", re.I)
        if not rx.search(_D_RE.sub("", s)):
            return s
    prot, _ = _protect_d(s)
    first = re.split(r"(?<=[,;.])\s+", prot.rstrip(".!?"))[0]
    out = _drop_clauses(s, rx, guard=False)
    if not out:
        return "".join(f"({_span_speaker(s[:m.start()])}) says, {m.group(0)} " for m in _D_RE.finditer(s)).strip()
    if rx.search(first) and not _SUBJECT_WORD_RE.search(re.split(r"[,;:]", _D_RE.sub("", out))[0]):
        owner = "His" if re.match(r"(?i)\s*(?:his|he)\b", first) else "Her"
        out = owner + " " + out[:1].lower() + out[1:]
    return out


_SKIN_ACTION_RE = re.compile(r"(?i)\b(?:slap\w*|spank\w*|grip\w*|squeez\w*|bit(?:e|es|ing)|pinch\w*|chok\w*|smack\w*|grab\w*)\b")
_LIGHT_SENT_RE = re.compile(r"(?i)\b(?:light|lights|lit|lighting|glow\w*|rim|specular|bounce|lamp\w*|neon|candle\w*|sunlight|daylight|"
                            r"backlit|spotlight|shadow\w*|highlight\w*|key light|fill)\b")


def _flag_skin(s: str) -> None:
    """dynsafe (limit 2, flag-only default Derrick accepted on t903u): never delete skin words. A lighting or camera sentence
    is out of scope. Otherwise unrequested redness (not tied to a written action) and unrequested gloss bound to a body
    noun within 3 words are logged in _CTX['skin_flags'] -> build_report 'skin_unrequested'."""
    plain = _D_RE.sub("", s)
    if _CAMERA_SENTENCE_RE.search(plain) or _LIGHTING_CUE_RE.search(plain) or _LIGHT_SENT_RE.search(plain):
        return
    flags = _CTX.setdefault("skin_flags", [])
    seen = {(f["phrase"], f["text"]) for f in flags}

    def add(kind: str, phrase: str) -> None:
        if (phrase, plain[:120]) not in seen:
            seen.add((phrase, plain[:120]))
            flags.append({"code": "skin_unrequested", "kind": kind, "phrase": phrase, "text": plain[:120]})
    if not _CTX.get("redness_asked") and not _SKIN_ACTION_RE.search(plain):
        for m in _REDNESS_RE.finditer(plain):
            add("redness", m.group(0))
    if not _CTX.get("gloss_asked"):
        body = _GLOSS_BODY_RE.pattern.replace("(?i)", "")
        for m in _GLOSS_RE.finditer(plain):
            w = re.escape(m.group(0))
            if re.search(r"(?i)(?:" + body + r")\W+(?:[\w-]+\W+){0,3}?" + w + r"|" + w + r"\W+(?:[\w-]+\W+){0,3}?(?:" + body + r")", plain):
                add("gloss", m.group(0))


def _scaffold(s: str) -> str:
    """Wording scaffold that needs no judgment: dash artifacts, 'ten seconds', camera echoes, mid-sentence negations
    (mapped to positive wording first), pose and throat wording the brief does not ask for. Outside <d> only."""
    prot, spans = _protect_d(s)
    prot = _DASH_COMMA_RE.sub(",", prot)
    prot = _PRIMARY_RE.sub("PRIMARY MOTION -", prot)  # its label dash is not a prose dash
    prot = _unpaired_dash(prot)
    # dynsafe (limit 5): the oak -> wood floor swap is gone (a still noun is never overwritten)
    if "briefs" not in _CTX.get("still_words", ()):
        prot = re.sub(r"\bbra and briefs\b", "bra and panties", prot)
    prot = re.sub(r";\s*,", ";", prot)  # dynsafe grammar pass
    prot = _PRON_COMMA_RE.sub(r"\1 ", prot)
    prot = _AN_RE.sub(lambda m: m.group(1) + "n ", prot)
    prot = _TEN_SEC_RE.sub("", prot)
    for rx, rep in _NEG_MAP:
        prot = rx.sub(rep, prot)
    if _CTX.get("position") == "doggy":
        prot = _DOGGY_BACK_RE.sub("presses her chest down to " + _CTX.get("pad_phrase", "the surface beneath her"), prot)
    s = _restore_d(prot, spans)
    if not _CAMERA_SENTENCE_RE.search(_D_RE.sub("", s)):
        s = _CAM_ECHO_RE.sub("", s)
    if s:
        _flag_skin(s)  # dynsafe: flag, never delete (lighting sentences are skipped inside)
    if not s:
        return ""
    if not _CTX.get("throat_contact") and _THROAT_RE.search(_D_RE.sub("", s)):
        s = _drop_clauses(s, _THROAT_RE) or ""
    holds: List[str] = []
    def _hold_w5(m: "re.Match[str]") -> str:
        holds.append(m.group(0))
        return f" __W5CLEAR{len(holds) - 1}__ "
    if s and _W5_CLEAR_CLAUSE_RE.search(_D_RE.sub("", s)):
        s = _W5_CLEAR_CLAUSE_RE.sub(_hold_w5, s)
    if s and _NEG_WORD_RE.search(_D_RE.sub("", s)) and not _NEGATION_START_RE.match(_D_RE.sub("", s)):
        s = _drop_clauses(s, _NEG_WORD_RE) or ""
    for i, chunk in enumerate(holds):
        s = (s or "").replace(f" __W5CLEAR{i}__ ", chunk)
    return s


def _strip_sentence(s: str) -> Optional[str]:
    s = _normalize_labels(s)
    s = _PHASE_LABEL_RE.sub("", s).strip()
    s = re.sub(r",?\s*HAND ANATOMY HARD-LOCKED[^;.]*;\s*", "; ", s)   # keep the separator (G_01 run-on)
    s = _HAND_COPY_RE.sub("", s).strip()
    s = _DANGLING_RE.sub(".", s)
    _single_body = (
        int(_CTX.get("bodies") or 2) < 2
        or _CTX.get("act_id") == "male_solo"
        or _CTX.get("s1_gender") == "man"
        or str(_CTX.get("partner_type") or "").lower() == "none"
    )
    if not _single_body:
        s = re.sub(r"\s+in (?:his )?(?:dark |black )?(?:trousers|jeans|pants)\b", "", s, flags=re.I)
        if _HIS_CLOTHES_RE.search(_D_RE.sub("", s)):
            s = _drop_clauses(s, _HIS_CLOTHES_RE)
    if not s.strip():
        return None
    s = _scaffold(s)
    if not s.strip():
        return None
    plain = _D_RE.sub("", s)
    if _RETENTION_LINE_RE.search(plain):
        return None
    if _ABSENT_GARMENT_RE and _ABSENT_GARMENT_RE.search(_hers_text(plain)):
        s = _drop_clauses(s, _HersAbsent(_ABSENT_GARMENT_RE))
        plain = _D_RE.sub("", s)
        if not s.strip() or _ABSENT_GARMENT_RE.search(_hers_text(plain)) or len(plain.split()) < 3:
            return None
    _ref_plain = plain
    for _n in _CTX.get("ref_pictures") or []:  # MMF S3 still: its <Picture N> is a real wired reference, not an absent one
        _ref_plain = re.sub(rf"(?i)<Picture {int(_n)}>", "", _ref_plain)
    _tags = [m.group(0) for m in _ABSENT_REF_RE.finditer(_ref_plain)]
    if _tags and all(re.fullmatch(r"<(?:Picture|Audio|Subject) \d+>", t) for t in _tags):
        # (6) Derrick t247s837: strip only the unwired tag (with its 'from/in/following' lead), keep the sentence
        for t in set(_tags):
            s = re.sub(r"(?i)\s*,?\s*(?:(?:as )?(?:shown |seen )?(?:in|from|following|like|matching|per|of) (?:the )?)?" + re.escape(t), "", s)
        s = re.sub(r"\s+([,.;:])", r"\1", s).strip()
        plain = _D_RE.sub("", s)
        _ref_plain = plain
        if len(plain.split()) < 3:
            return None
    if _DIAL_RE.search(plain) or _is_policy(s) or _ABSENT_REF_RE.search(_ref_plain) or _MUSIC_RE.search(plain):
        return None
    if _NEGATION_START_RE.match(plain) or _NEGATION_LIST_RE.search(plain):
        return None
    s, spans = _protect_d(s)
    s = _NEGATION_CLAUSE_RE.sub("", s)
    s = s.replace("…", ", ").replace("...", ", ")
    s = re.sub(r"\[Shot\s*\d+\]\s*(?:\([^)]*\)|at\s+\d[\d:.]*\s*,?)?\s*", "", s, flags=re.I)
    s = re.sub(r"^\s*(?:beat|phase)\s*\d+\s*[:.-]\s*", "", s, flags=re.I)
    s = _PRIMARY_RE.sub("PRIMARY MOTION -", s)
    s = _DASH_COMMA_RE.sub(",", _fix_transitions(s.strip()))  # 'her — then pulls' -> 'her, pulls'
    s = _unpaired_dash(s)
    s = re.sub(r",\s*and\s*(?=[.;!?]|$)", "", s)  # dynsafe grammar pass: no dangling ', and' after a cut
    s = re.sub(r",\s*and\s*,", ",", s)
    s = _restore_d(s, spans)
    s = re.sub(r"\s{2,}", " ", s).strip(" ,;")
    if not s or ("<d>" not in s and len(_D_RE.sub("", s).split()) < 3):
        return None
    s = re.sub(r"(</d>)\s*[\"”]?\s*[.,]+$", r"\1", s)
    if s[-1] not in ".!?>":
        s += "."
    return s


def _cam_classes(s: str) -> List[str]:
    return [name for name, rx in _CAM_CLASS if rx.search(s)]


def _resolve_camera(sentences: List[str], camera_tail: str) -> List[str]:
    """One camera sentence with one official move or a hold. dynsafe (limit 1): the writer's move stays as written (a hold
    stays a hold, a pull-out stays a pull-out, no forced two-shot). Repairs are noun level only: a second move clause goes,
    and only the missing framing items (her face, his face, the join) are appended. Real problems are flagged in
    _CTX['camera_flags'] (track on a stationary act, pull-out ending wider than a medium shot, no end framing)."""
    cams = [i for i, s in enumerate(sentences) if "<d>" not in s and _CAMERA_SENTENCE_RE.search(s)]
    moving = [i for i in cams if _CAMERA_MOVE_RE.search(sentences[i])]
    keep = moving[0] if moving else (cams[0] if cams else None)
    out = []
    for i, s in enumerate(sentences):
        if i not in cams or i == keep:
            out.append(s)
            continue
        prot, spans = _protect_d(s)
        if ";" in prot:
            rest = prot.split(";", 1)[1].strip()
            if len(rest.split()) >= 3:
                rest = _strip_sentence(_restore_d(rest[:1].upper() + rest[1:], spans))
                if rest and not _is_fragment(rest):
                    out.append(rest)
    if keep is None:
        return out
    k = out.index(sentences[keep])
    cam = sentences[keep]
    for rx, rep in _CAM_SYNONYMS:
        cam = rx.sub(rep, cam)
    flags = _CTX.setdefault("camera_flags", [])
    standing_open = any(_OPENER_RE.search(_D_RE.sub("", x)) and _STAND_SENT_RE.search(_D_RE.sub("", x)) for x in out if x != sentences[keep])
    mv = re.search(r"(?i)\bpush(?:es|ing)?[- ]in\b", cam)
    if standing_open and mv and re.search(r"(?i)\bon the bed\b|\btwo-shot\b", cam[:mv.start()]):
        cam = re.sub(r"(?i)^((?:\[Shot 1\] )?The camera) starts [^;]*;\s*the camera (pushes in)", r"\1 \2 from the standing frame of <Picture 1>", cam)
    cam = re.sub(r"(?i)\btheir upper bod(?:y|ies)\b", "their bodies down to the join", cam)  # G_03: framing that keeps the join
    classes = _cam_classes(cam)  # dynsafe: no 'frames the bed' prefix; a framing sentence without 'camera' stays as written
    if classes:
        # keep the first move; clauses that start a different move go
        first = classes[0]
        others = [rx for name, rx in _CAM_CLASS if name != first]
        if len(set(classes)) > 1:
            other_rx = re.compile("|".join(r.pattern.replace("(?i)", "") for r in others), re.I)
            parts = re.split(r"(?<=[,;])\s+", cam.rstrip("."))
            seen_first = False
            kept_parts = []
            for p in parts:
                if dict(_CAM_CLASS)[first].search(p):
                    seen_first = True
                if seen_first and other_rx.search(p) and not dict(_CAM_CLASS)[first].search(p):
                    continue
                kept_parts.append(p)
            cam = " ".join(kept_parts).rstrip(" ,;") + "."
        cam = re.sub(r"\b(locked[- ]off|locked|static)\s+", "", cam, flags=re.I)
    body = " ".join(out)
    low_tail = (camera_tail or "").lower()
    _solo_man = _CTX.get("s1_gender") == "man" or _CTX.get("act_id") == "male_solo"
    items = ["his face"] if _solo_man else ["her face"]
    late_partner = bool(re.search(r"(?i)\bonce (?:he|she|her partner|his partner|everyone) enters\b", camera_tail))
    if "both faces" in low_tail and not late_partner:
        items = ["both faces"]  # #6 futa/woman partner: never append 'his face'
    elif ("all three faces" in low_tail or "all faces" in low_tail) and not late_partner:
        items = ["all three faces"] if "all three faces" in low_tail else ["all faces"]
    elif "his face" in low_tail and not late_partner:
        if any(p in low_tail for p in ("her face", "both faces", "all three faces", "all faces")):
            if "his face" not in items:
                items.append("his face")
    if "join" in low_tail:
        items.append("the join")
    if re.search(r"(?i)his face (?:stays|is|remains) out of (?:the )?frame", body) and "his face" in items:
        items.remove("his face")
    has_end = bool(_END_FRAME_RE.search(cam))
    pos = _CTX.get("position")
    if classes and classes[0] == "tracking" and pos in _STILL_ACTS:
        flags.append({"code": "K1", "why": "track on a stationary act (a track follows a moving subject)", "text": cam[:120]})
    if classes and classes[0] == "pull out":
        mv = _CAM_CLASS[1][1].search(cam)
        if mv and _WIDE_END_RE.search(cam[mv.end():]) and pos in _STILL_ACTS:
            flags.append({"code": "K2", "why": "pull-out ends wider than a medium shot during the act", "text": cam[:120]})
    if classes and re.search(r"(?i)\blarge amplitude\b", cam) and pos in _STILL_ACTS:
        flags.append({"code": "K3", "why": "large amplitude on a sex beat (flag only)", "text": cam[:120]})
    # dynsafe (brief item 3): flag, never rewrite, a move or focus that would crop a named face, lose its headroom or
    # throw it off the sharp plane; nothing is forced into a close-up
    if re.search(r"(?i)\b(?:extreme close-up|close-up|macro|tight)\b[^.;]{0,40}\b(?:on|of)\s+(?:the join|her (?:hips|thighs|crotch|buttocks|hands?|feet)|his (?:hands?|hips)|the (?:hands?|hips|thighs))\b", cam):
        flags.append({"code": "K5", "why": "close framing on a body part would crop the named faces", "text": cam[:120]})
    if re.search(r"(?i)\b(?:rack(?:s|ing)? focus|focus (?:racks?|pulls?|shifts?) (?:to|onto)|shallow (?:depth of field|focus)[^.;]{0,30}\b(?:on|to) (?:the join|her hands?|his hands?|the hands?))\b", cam):
        flags.append({"code": "K6", "why": "focus insert would throw a named face off the sharp plane", "text": cam[:120]})
    if re.search(r"(?i)\b(?:from the neck down|head (?:cropped|out of frame)|crops? (?:her|his) (?:head|face)|cuts? off (?:her|his) (?:head|face)|no headroom)\b", cam):
        flags.append({"code": "K7", "why": "framing crops a named face or leaves no headroom", "text": cam[:120]})
    if classes and not has_end:
        flags.append({"code": "K4", "why": "camera move has no end framing (missing framing items appended only)", "text": cam[:120]})
    # NB6: do not append a camera tail onto the writer's camera sentence (no stacked 'keeping' or 'the join' on no-contact).
    cam = re.sub(r"(?i),\s*keeping ([^,]+?) in frame,\s*keeping\b", r", keeping \1 and", cam)  # A_01 doubled 'keeping'
    cam = re.sub(r"(?i),?\s*and that framing is the final framing", "", cam)
    out[k] = cam if cam.endswith(".") else cam + "."
    return out


def _garment_retention(cast: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    """dynsafe: the garment retention line follows the end state - removed items are partially_preserved (its / their by
    count), kept items fully_preserved. No garments = no line."""
    names = {g["key"]: g["name"] for g in _cast_items(cast)}
    aside_keys = set(state.get("writer_aside") or [])
    off = [names[k] for k, v in state["garments"].items() if v == "off" and k in names]
    aside = [names[k] for k, v in state["garments"].items() if v == "on" and k in aside_keys and k in names]
    on = [names[k] for k, v in state["garments"].items() if v == "on" and k not in aside_keys and k in names]

    def join(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    out = []
    if off:
        pl = _plural(off)
        out.append(f"The {join(off)} of <Picture 1>: partially_preserved - {'their' if pl else 'its'} removal is an action in the story, "
                   f"so the bodies that become bare are the same bodies the photograph shows; {'they lie' if pl else 'it lies'} on "
                   f"{cast['garments_floor']} and {'stay' if pl else 'stays'} there")
    if aside:
        pl = _plural(aside)
        _aid = (_CTX.get("act_id") or _CTX.get("position") or "").lower()
        if _aid in ("handjob", "blowjob", "oral", "titjob", "mmf_double_blowjob"):
            out.append(f"The {join(aside)} of <Picture 1>: partially_preserved - {'they stay' if pl else 'it stays'} on her body, adjusted as she works")
        else:
            out.append(f"The {join(aside)} of <Picture 1>: partially_preserved - {'they stay' if pl else 'it stays'} on her body, pulled aside or slid up so the join is clear")
    if on:
        pl = _plural(on)
        out.append(f"The {join(on)} of <Picture 1>: fully_preserved - {'they stay' if pl else 'it stays'} on her body as the photograph shows")
    return out


def check_writer_consistency(text: str) -> List[str]:
    """Leg position, facing direction and surface must each stay one thing per clip."""
    plain = _D_RE.sub("", text)
    issues: List[str] = []
    legs = [k for k, rx in _LEG_CATEGORIES.items() if rx.search(plain)]
    if len(legs) > 1:
        issues.append("leg position changes: " + " / ".join(legs))
    facing = [k for k, rx in _FACING.items() if rx.search(plain)]
    if len(facing) > 1:
        issues.append("facing conflict: " + " / ".join(facing))
    if _CTX.get("still_bed", True) is False and re.search(r"\b(bed|mattress|sheets?)\b", plain, re.I):
        issues.append(f"surface conflict: no bed in the start image; keep them on {_CTX.get('surface', 'the floor')}")
    elif _FLOOR_BODY_RE.search(plain) and re.search(r"\b(bed|mattress|sheets?)\b", plain, re.I):
        issues.append("surface conflict: bodies on the floor and on the bed")
    if _CTX.get("position") == "doggy" and _DOGGY_BACK_RE.search(plain):
        issues.append("doggy pose conflict: presses her back against the mattress")
    return issues


_GARMENT_KEYS = [
    # lingerie (unchanged); a bikini top tracks like the bra, bikini bottoms like the panties (Derrick t856s3457)
    ("bra", r"\bbra\b|\bbralette\b|\bbikini top\b"), ("panties", r"\b(?:panties|panty|thong|knickers|briefs|bottoms)\b|\bbikini (?:bottoms?|briefs)\b"),
    ("garter belt", r"\bgarter\w*(?: belt| clips?)?\b|\bbelt\b"),
    ("stockings", r"\bstocking\w*\b|\bthigh-highs?\b"), ("choker", r"\bchoker\b"),
    # pmfix5 garments: everyday clothes (his clothes are the builder's his_clothes line and never match: 'his ...' is excluded)
    ("swimsuit", r"\b(?:swimsuit|one-piece|bathing suit|monokini|swimming costume)\b"),
    ("dress", r"(?<!his )\b(?:sun|slip |mini|maxi |party |cocktail )?dress\b(?! (?:shirt|shoes))|\bgown\b"),
    ("top", r"(?<!his )(?<!bikini )\b(?:crop |tank |halter |tube |tied |knit |sheer |lace |silk |white |black )?top\b(?! of\b)|(?<!his )\b(?:t-shirt|tee|shirt|blouse|tank|camisole|cami)\b"),
    ("skirt", r"\b(?:mini)?skirt\b"),
    ("shorts", r"(?<!his )\b(?:shorts|hot pants)\b"),
    ("pants", r"(?<!his )\b(?:jeans|leggings|yoga pants)\b|\b(?:her|the|tight|white|black|blue) (?:pants|trousers)\b"),
    ("jacket", r"(?<!his )\b(?:jacket|cardigan|robe|blazer|coat|hoodie|kimono|sweater)\b"),
    ("shoes", r"\b(?:shoes|boots|sandals|sneakers|pumps|stilettos|high heels)\b|\b(?:kick\w*|slip\w*|tak\w*|pull\w*|step\w*) (?:off|out of) (?:her |the )?(?:[\w-]+ )?heels\b|"
               r"\b(?:white|black|red|nude|strappy|stiletto|platform|clear|silver|gold|pink|beige|patent|lace-up) heels\b|"
               r"\bheels\b(?! (?:press|dig|lock|hook|rest|drag|slide|push|brace))(?=[^,;.]{0,40}\b(?:off|on her feet|stay on)\b)"),
]


def _items(spec: str) -> List[str]:
    return [x.strip() for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", spec or "") if x.strip()]


def _garment_key(name: str) -> Optional[str]:
    for key, rx in _GARMENT_KEYS:
        if re.search(rx, name, re.I):
            return key
    return None


# --- stillfacts (2026-11-11, Derrick t51u/t52u; Prompt maker fixes #2 and #5): the setting and clothes come from the still --
_TYPE_ALIAS = {"thong": "panties", "bikini top": "bra", "bikini bottom": "panties", "bikini bottoms": "panties",
               "bottom": "panties", "bottoms": "panties", "bra top": "bra", "one-piece": "swimsuit", "heels": "shoes",
               "boots": "shoes", "garter": "garter belt", "garters": "garter belt", "jeans": "pants", "robe": "jacket"}
_GENERIC_TYPES = ("", "other", "lingerie", "top", "clothing", "outfit")
_KEY_NOUNS = {
    "bra": r"bra top|bra|bralette|bikini top", "panties": r"bikini bottoms?|bottoms|panties|panty|thong|knickers|briefs",
    "garter belt": r"garter belt|garters?|suspenders", "stockings": r"stockings|thigh-highs?|fishnets", "choker": r"choker",
    "swimsuit": r"swimsuit|one-piece|bathing suit", "dress": r"sundress|dress|gown", "top": r"t-shirt|tank top|crop top|top|tee|shirt|blouse|camisole|cami",
    "skirt": r"skirt", "shorts": r"shorts", "pants": r"jeans|leggings|pants|trousers",
    "jacket": r"jacket|cardigan|robe|blazer|coat|hoodie|kimono|sweater", "shoes": r"high heels|heels|shoes|boots|sandals|sneakers|pumps|stilettos"}
_ADJ = r"(?:(?!(?:her|his|the|and|or|with|of|from|off|on|in|to|a|an|as|at|by|over|under|down|up|now|then|still)\b)[\w-]+\s+)"


def garment_type_key(gtype: Optional[str], name: Optional[str]) -> Optional[str]:
    """The tracker key for one vision-read garment. A generic type ('other', 'top', '') is mapped by its name, so
    'black mesh strappy bottom with garter straps' is panties and 'black mesh strappy bra top' is a bra."""
    t, n = (gtype or "").strip().lower(), (name or "").strip()
    by_name = "panties" if re.search(r"(?i)\bbottoms?\b", n) and not re.search(r"(?i)\b(?:swimsuit|one-piece)\b", n) else _garment_key(n)
    if t in _GENERIC_TYPES:
        return by_name or (t if t in _KEY_NOUNS else None)
    if t in _KEY_NOUNS:
        return t
    return _TYPE_ALIAS.get(t) or by_name


# dynsafe (limit 4): the still's own garment phrases are the inventory; the slot only drives coverage.
_SLOT_OF_KEY = {"bra": "top", "top": "top", "panties": "bottom", "shorts": "bottom", "pants": "bottom", "skirt": "bottom",
                "swimsuit": "full-body", "dress": "full-body", "jacket": "outerwear", "stockings": "legwear",
                "garter belt": "accessory", "choker": "accessory", "shoes": "footwear"}
_COVER_SLOTS = ("top", "bottom", "full-body", "outerwear")
_JOIN_KEYS = ("panties", "swimsuit", "pants", "shorts")  # garments that cover the join
# known-garment lexicon for W4: absent list is closed (lexicon minus anything sharing a head word / key with the still)
_GARMENT_LEXICON = ("chemise", "slip dress", "nightgown", "nightie", "blouse", "camisole", "bodysuit", "teddy", "robe",
                    "kimono", "corset", "bustier", "bra", "bralette", "panties", "thong", "knickers", "briefs", "g-string",
                    "garter belt", "garters", "garter", "suspenders", "stockings", "thigh-highs", "fishnets", "choker",
                    "bikini", "swimsuit", "one-piece", "sundress", "dress", "gown", "skirt", "miniskirt", "shorts", "jeans",
                    "leggings", "cardigan", "blazer", "hoodie", "sweater", "the sheer fabric")


def _article(name: str) -> str:
    """dynsafe grammar: 'a/an' by sound for one item, none for a plural (stockings, thigh-highs, heels)."""
    n = name.strip()
    head = _head(n)
    if re.search(r"(?i)^(?:a|an|the|her|his)\s", n):
        return n
    if head.endswith("s") and not head.endswith(("ss", "us", "is")):
        return n
    return ("an " if re.match(r"(?i)[aeio]|u(?!ni|se|su)", n) else "a ") + n


def garment_inventory(read: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every vision-read garment (type 'other' included) with its still phrase, tracker key and coverage slot."""
    out = []
    for g in still_facts(read)["garments"]:
        key = g["key"]
        slot = _SLOT_OF_KEY.get(key or "", "")
        if not slot:
            slot = "bottom" if re.search(r"(?i)\b(?:bottoms?|thong|briefs|panty|panties)\b", g["name"]) else "accessory"
        out.append({"name": g["name"], "type": g["type"], "look": g.get("look", ""), "key": key, "slot": slot})
    return out


def absent_garment_pattern(read: Optional[Dict[str, Any]]) -> Optional[str]:
    """W4 regex: lexicon garments the still does not show. None when the read has no garment list (wardrobe_unverified)."""
    inv = garment_inventory(read)
    if not inv:
        return None
    words = set()
    for g in inv:
        words |= set(re.findall(r"[a-z-]+", (g["name"] + " " + g.get("look", "")).lower()))
        words.add(_head(g["name"]))
    keys = {g["key"] for g in inv if g["key"]}
    stems = {w.rstrip("s") for w in words}
    absent = []
    for lex in _GARMENT_LEXICON:
        if lex == "the sheer fabric":
            if not (words & {"sheer", "lace", "mesh", "silk", "satin", "chiffon", "translucent", "fabric"}):
                absent.append("the sheer fabric")
            continue
        lk = _garment_key(lex)
        if {w.rstrip("s") for w in re.findall(r"[a-z-]+", lex)} & stems or (lk and lk in keys):
            continue
        absent.append(re.escape(lex).replace("\\ ", " "))
    if not absent:
        return None
    return r"\b(" + "|".join(absent) + r")\b"



def _unwrap_still_read(read: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Accept a flat vision read or the phone-path wrap {read, how, source, source_sha256}."""
    r = read or {}
    inner = r.get("read")
    if not isinstance(inner, dict):
        return r
    fact_keys = (
        "garments", "surface", "pose", "room", "setting", "place", "floor",
        "bed", "people", "light", "hair", "skin", "build", "props", "sheets",
    )
    if any(k in inner for k in fact_keys) and not any(k in r for k in fact_keys):
        return inner
    return r


def still_facts(read: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Normalize one structured vision read (setting, garments with name/type, her starting pose, props, light)."""
    r = _unwrap_still_read(read)
    bed = bool(r.get("bed"))
    surface = (r.get("surface") or ("the bed" if bed else "the floor")).strip()
    if not re.match(r"(?i)(?:the|a|an|her|his)\b", surface):
        surface = "the " + surface
    garments = []
    raw_garments = list(r.get("garments") or [])
    raw_people = r.get("people")
    people_list = raw_people if isinstance(raw_people, list) else []
    for p in people_list:
        if isinstance(p, dict):
            raw_garments.extend(p.get("garments") or [])
    for g in raw_garments:
        g = {"name": g, "type": "", "look": ""} if isinstance(g, str) else dict(g)
        name = (g.get("name") or "").strip()
        look = (g.get("look") or "").strip()
        if not name:
            continue
        # NB11: split compound lingerie sets (e.g. 'sheer beige bra and high-waist panty with garters') into top & bottom.
        parts = [name]
        if re.search(r"\band\b", name, re.I):
            cand = [x.strip() for x in re.split(r"\s+and\s+", name, maxsplit=1, flags=re.I) if x.strip()]
            if len(cand) == 2:
                k0, k1 = _garment_key(cand[0]), _garment_key(cand[1])
                if k0 and k1 and k0 != k1:
                    parts = cand
        for part in parts:
            full_name = part
            if look and "," not in look and len(look.split()) <= 3 and look.lower() not in part.lower() and len(part.split()) <= 2:
                full_name = f"{look} {part}"
            garments.append({"name": full_name, "type": (g.get("type") or "").strip().lower(),
                             "look": look, "key": garment_type_key(None if len(parts) > 1 else g.get("type"), full_name)})
    props = r.get("props") or []
    if isinstance(props, str):
        props = [x.strip() for x in re.split(r"[,;]", props) if x.strip()]
    restraints = r.get("restraints") or []
    if isinstance(restraints, str):
        restraints = [x.strip() for x in re.split(r"[,;]", restraints) if x.strip()]
    toys = r.get("toys") or []
    if isinstance(toys, str):
        toys = [x.strip() for x in re.split(r"[,;]", toys) if x.strip()]
    people = people_list if isinstance(raw_people, list) else ([{}] * raw_people if isinstance(raw_people, int) else [])
    pose = (r.get("pose") or (people[0].get("position") if people and isinstance(people[0], dict) else "") or "").strip()
    return {"setting": (r.get("room") or r.get("setting") or r.get("place") or "").strip(), "place": (r.get("place") or "").strip(),
            "bed": bed, "surface": surface, "sheets": (r.get("sheets") or "").strip() if bed else "",
            "floor": (r.get("floor") or "").strip(), "garments": garments, "pose": pose,
            "props": [p for p in props if p], "restraints": [x for x in restraints if x],
            "toys": [x for x in toys if x], "people": people, "light": (r.get("light") or "").strip()}


NEUTRAL_SETTING = "the setting shown in <Picture 1>"


def _scene(cast: Dict[str, Any]) -> Dict[str, Any]:
    """Setting words for the builder's own lines, from the still read (or explicit cast keys). dynsafe (limit 5): no
    bedroom default. Without a read the words are neutral ('the setting shown in <Picture 1>'); production never gets
    here without a read (build_writer_request raises NOT_READY first). bed is None when unknown."""
    f = still_facts(cast["still_read"]) if cast.get("still_read") else None
    bed = cast.get("still_bed", f["bed"] if f else None)
    surface = cast.get("surface") or (f["surface"] if f else ("the bed" if bed else ""))
    setting = cast.get("setting") or (f["setting"] if f else "") or NEUTRAL_SETTING
    if not f and not surface:
        return {"bed": bed, "surface": "the surface shown in <Picture 1>", "pad": "hip", "pad_phrase": "the surface beneath her",
                "setting": setting, "anchor": f"{setting}, its surfaces, the light and the opening framing", "neutral": True}
    floor = (f or {}).get("floor") or ""
    floor_noun = re.sub(r"(?i)^(?:(?:the|a|an)\s+)+", "", floor).strip()
    bits = [setting] + (["the bed and its sheets"] if bed else [surface]) + ([f"the {floor_noun}"] if floor_noun and floor_noun.lower() not in surface.lower() else [])
    anchor = re.sub(r"(?i)\bthe\s+the\b", "the", ", ".join(bits) + ", the light and the opening framing")
    return {"bed": bed, "surface": surface, "pad": "mattress" if bed else re.sub(r"(?i)^(?:the|a|an)\s+", "", surface),
            "pad_phrase": "the mattress" if bed else surface, "setting": setting,
            "anchor": anchor}


def still_facts_block(read: Optional[Dict[str, Any]]) -> str:
    """A short must-keep facts block for the writer brief, built from the vision read."""
    f = still_facts(read)
    lines = ["Must-keep facts from <Picture 1> (use these nouns; do not invent another room, surface or garment):"]
    if f["setting"]:
        lines.append(f"- Setting: {f['setting']}.")
    lines.append(f"- Bed: {'yes' + (', ' + f['sheets'] if f['sheets'] else '') + '.' if f['bed'] else 'none in the image. No bed, mattress or sheets; the bodies stay on ' + f['surface'] + '.'}")
    if f["garments"]:
        lines.append("- She wears: " + "; ".join(g["name"] for g in f["garments"]) + ". Nothing else.")
    if f["pose"]:
        lines.append(f"- Her starting pose: she {re.sub(r'(?i)^she ', '', f['pose'])}.")
    if f["props"]:
        lines.append("- Props: " + ", ".join(f["props"]) + ".")
    if f["light"]:
        lines.append(f"- Light: {f['light']}.")
    return "\n".join(lines)


def _head(name: str) -> str:
    n = re.split(r"(?i)\s+(?:with|and)\s+", name.strip())[0]
    return n.split()[-1].lower() if n.split() else ""


def apply_still_facts(text: str, read: Optional[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
    """Check written text against the still: swap wrong setting / garment nouns for the still's own nouns (outside <d>
    lines) and count which still nouns the text keeps. Returns (text, {"swaps", "hits", "misses"})."""
    f = still_facts(read)
    prot, spans = _protect_d(text or "")
    swaps: List[List[str]] = []

    def sub(rx: str, new: Any, flags: int = re.I) -> None:
        nonlocal prot
        def go(m):
            out = new(m) if callable(new) else m.expand(new)
            if out and m.group(0)[:1].isupper() and out[:1].islower():
                out = out[0].upper() + out[1:]
            if out != m.group(0):
                swaps.append([m.group(0), out])
            return out
        prot = re.sub(rx, go, prot, flags=flags)

    surf = f["surface"]
    if not f["bed"]:
        sub(r"\bmattress height\b", re.sub(r"(?i)^(?:the|a|an)\s+", "", surf) + " height")
        sub(r"\b(?:the |her )?(?:edge of the )?(?:bed ?sheets|sheets)\b", surf)
        sub(r"\b(?:the |her |a )?(?:edge of the )?(?:bed|mattress)\b(?!room)", surf)
        if not re.search(r"(?i)\bbedroom\b", f["setting"]):
            sub(r"\b(?:the |a |her )?bedroom\b", "the " + (f["place"] or "room"))
    if f["floor"] and not re.search(r"(?i)\b(?:wood|oak|hardwood|parquet)", f["floor"]):
        fl_noun = re.sub(r"(?i)^(?:the|a|an)\s+", "", f["floor"]).strip()
        if fl_noun:
            sub(r"\b(?:the )?(?:dark |polished |bare )?(?:wood(?:en)?|oak|hardwood|parquet) floor\b", "the " + fl_noun)
    by_key: Dict[str, str] = {}
    for g in f["garments"]:
        if g["key"]:
            by_key.setdefault(g["key"], g["name"])
    for key, name in by_key.items():
        nouns = _KEY_NOUNS.get(key)
        if not nouns:
            continue
        def keep_or_swap(m, name=name):
            phrase = (m.group(2) + m.group(3) + (m.group(4) or "")).lower()
            words = set(re.findall(r"[\w-]+", name.lower()))
            if phrase == name.lower() or set(re.findall(r"[\w-]+", phrase)) <= words:
                return m.group(0)
            return f"{m.group(1)} {name}"
        sub(r"\b(her)\s+(" + _ADJ + r"{0,3}?)(" + nouns + r")((?:\s+(?:bottoms?|top))?)\b", keep_or_swap)
    out = _restore_d(prot, spans)
    plain = _D_RE.sub("", out).lower()
    nouns = [g["name"] for g in f["garments"]] + ([f["place"]] if f["place"] else []) + f["props"] + [surf]
    hits, misses = [], []
    for n in nouns:
        h = re.sub(r"(?i)^(?:the|a|an)\s+", "", n).lower() if n in (f["place"], surf) else _head(n)
        (hits if h and re.search(r"\b" + re.escape(h) + r"\b", plain) else misses).append(n)
    return out, {"swaps": swaps, "hits": hits, "misses": misses}


_PLACE_RE = re.compile(r"(?i)\b(?:falls? to|lands? on|drops? (?:it |them )?(?:to|onto|on)|took off[^,.;]{0,40}(?:on|onto|to)|stays? on)\s+((?:the|her|a)\s+(?!(?:side|way|end|knees|back|thighs|hips|ankles|feet|body|head|shoulders?|arms?|legs?|waist|chest|breasts?|lap|neck|hands?)\b)[\w -]{2,40}?)(?=\s*(?:[,.;]|$|\band\b|\bbeside\b|\bwhere\b))")


def _cast_items(cast: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Tracked garments: the still inventory (make_cast) or, for a hand-written cast, garments_off / garments_stay."""
    out: List[Dict[str, Any]] = []
    seen = set()
    keyrx = dict(_GARMENT_KEYS)
    if cast.get("inventory") is not None:
        for g in cast["inventory"]:
            k = g.get("key") or ("item:" + _head(g["name"]))
            if k in seen:
                continue
            seen.add(k)
            head = _head(g["name"])
            rx = keyrx.get(g.get("key")) or (r"\b" + re.escape(head) + r"s?\b")
            # Credit a short still name ("strappy bottom" from "black mesh strappy bottom with garter straps").
            words = re.split(r"(?i)\s+(?:with|and)\s+", (g["name"] or "").strip())[0].split()
            if len(words) >= 2:
                short = " ".join(words[-2:])
                if short.lower() not in ((g["name"] or "").strip().lower(), head.lower()):
                    rx += r"|\b" + re.escape(short) + r"s?\b"
            rx += r"|\b" + re.escape(g["name"]) + r"\b"  # frs16 S2: the still's own phrase (the builder swaps writer nouns to it)
            out.append({"key": k, "name": g["name"], "rx": rx,
                        "off": g.get("slot") in _COVER_SLOTS, "stay": False, "slot": g.get("slot") or ""})
        return out
    for names, off in ((_items(cast.get("garments_off", "")), True), (_items(cast.get("garments_stay", "")), False)):
        for n in names:
            k = _garment_key(n)
            if k and k not in seen:
                seen.add(k)
                out.append({"key": k, "name": n, "rx": keyrx[k], "off": off, "stay": not off, "slot": _SLOT_OF_KEY.get(k, "")})
    return out


def _match_inherited_garment(item: Dict[str, Any], inherited: Dict[str, str]) -> Optional[str]:
    """Match a still inventory item against inherited garment states (aside/up/off/on) from the prior clip."""
    if not inherited:
        return None
    k = str(item.get("key") or "")
    name = str(item.get("name") or "").lower()
    k_short = k[5:] if k.startswith("item:") else k
    name_key = _garment_key(name) or ""
    for ik, st in inherited.items():
        iks = str(ik or "").strip()
        ikl = iks.lower()
        ik_short = ikl[5:] if ikl.startswith("item:") else ikl
        if iks == k or ik_short == k_short.lower() or (name_key and ik_short == name_key) or (name_key and _garment_key(ik_short) == name_key):
            return str(st).lower()
        if len(ik_short) >= 3 and re.search(rf"(?i)\b{re.escape(ik_short)}\b", name):
            return str(st).lower()
    return None


def track_state(sentences: List[str], cast: Dict[str, Any], repair: bool = True, keep: Sequence[str] = ()
                ) -> Tuple[List[str], Dict[str, Any], List[Dict[str, Any]]]:
    """Walk the writer's body sentences in order with a wardrobe + position state (start: the still - every still garment
    on, standing). The builder's wardrobe line is the single removal, so any writer removal of a garment is a second
    removal (W1); a removal after penetration is W2; removing a garment that stays on is W3; removing a garment the
    still does not have is W4; a pose that goes back to standing after the move toward the bed is P1.
    With repair, a violating sentence that also carries movement, sound or speech loses only the offending clauses;
    any other violating sentence goes whole, with an It/They orphan right after it."""
    # dynsafe (limit 3): undress is a writer or ask decision. A writer removal is valid the first time (W1 = the
    # writer removes it again); the builder removes the remaining cover garments only when cast['undress'] (the ask
    # names undress, or a hand-written cast without an ask). W3 only for a hand-written garments_stay list.
    items = _cast_items(cast)
    off_items = [g["key"] for g in items if g["off"]]
    stay_items = [g["key"] for g in items if g["stay"]]
    item_rx = [(g["key"], g["rx"]) for g in items]
    state: Dict[str, Any] = {
        "garments": {g["key"]: "on" for g in items},
        "level": 0,
        "act": False,
        "writer_removed": [],
        "builder_removed": [],
        "writer_aside": [],
        "prior_aside": [],
        "prior_off": [],
    }
    if cast.get("continued") and isinstance(cast.get("inherited_garments"), dict):
        inh = cast["inherited_garments"]
        for g in items:
            st = _match_inherited_garment(g, inh)
            if st and re.search(r"\b(?:aside|slid|pulled|pushed|hiked|bunched|up)\b", st):
                state["writer_aside"].append(g["key"])
                state["prior_aside"].append(g["key"])
            elif st and re.search(r"\b(?:off|removed|floor|dropped|taken off)\b", st):
                state["garments"][g["key"]] = "off"
                state["prior_off"].append(g["key"])
    absent = re.compile(cast["absent_garments"], re.I) if cast.get("absent_garments") else None
    move_rx = re.compile(cast.get("move_check") or cast.get("position_check") or r"$^", re.I)
    out: List[str] = []
    violations: List[Dict[str, Any]] = []
    drop_orphan = False
    for i, s in enumerate(sentences):
        plain = _D_RE.sub("", s)
        if drop_orphan and _ORPHAN_RE.match(plain):
            violations.append({"code": "W0", "idx": i, "text": s[:120], "fix": "orphan of a dropped removal, dropped"})
            continue
        drop_orphan = False
        codes = []
        if _REMOVE_VERB_RE.search(plain) and not _not_an_undress_beat(plain):
            named = [k for k, rx in item_rx if re.search(rx, plain, re.I)] or [k for k, rx in _GARMENT_KEYS if re.search(rx, plain, re.I)]
            for k in named:
                if k in stay_items:
                    codes.append(("W3", f"{k} stays on her body"))
                elif state["garments"].get(k) == "off":
                    codes.append(("W1", f"{k} removed twice (the writer already removed it)"))
                if state["act"] and not any(c == "W2" for c, _ in codes):
                    codes.append(("W2", "garment removed after penetration"))
            if absent and absent.search(_hers_text(plain, absent)):  # frs16 S1: his clothes are never W4
                codes.append(("W4", "removes a garment the still does not have"))
        stand_back = state["level"] >= 1 and _STAND_ASSERT_RE.search(plain) and not _OPENER_RE.search(plain)
        if stand_back:
            codes.append(("P1", "pose goes back to standing"))
        if codes:
            carries = bool(_MOVE_SOUND_RE.search(re.sub(r"\b(?:takes? off|steps? out of)\b", "", plain)) or "<d>" in s)
            carries = carries or s in keep  # the writer's opener is never dropped whole, only trimmed
            fixed = s
            if repair:
                if any(c in ("W1", "W2", "W3", "W4") for c, _ in codes) and carries:
                    rx = re.compile(r"(?=.*(?:" + "|".join(r for _, r in _GARMENT_KEYS) + (("|" + absent.pattern) if absent else "") +
                                    r"|\b(?:it|them)\b))(?=.*" + _REMOVE_VERB_RE.pattern + ")", re.I)
                    fixed = _drop_clauses(s, rx)
                    if fixed and _REMOVE_VERB_RE.search(_D_RE.sub("", fixed)) and re.search(
                            "|".join(r for _, r in _GARMENT_KEYS), _D_RE.sub("", fixed), re.I):
                        fixed = ""
                elif any(c == "P1" for c, _ in codes) and carries:
                    fixed = s  # needs the writer (lint P1): keep it, the repair loop rewrites it
                else:
                    fixed = ""
            for c, why in codes:
                violations.append({"code": c, "idx": i, "text": s[:160], "fix": ("clause dropped" if fixed and fixed != s else
                                   "sentence dropped" if not fixed else "kept (writer repair)") if repair else "none", "why": why})
            if not fixed and s in keep:
                fixed = s
            if not fixed:
                if "<d>" in s:  # never drop a spoken line with a removal sentence: keep the speech unit alone
                    fixed = " ".join(f"({_span_speaker(s[:m.start()])}) {m.group(0)}" for m in _D_RE.finditer(s))
                else:
                    drop_orphan = True
                    continue
            s = fixed
            plain = _D_RE.sub("", s)
        hit = [k for k, rx in item_rx if re.search(rx, plain, re.I)]
        if _REMOVE_VERB_RE.search(plain):
            # dynsafe: the writer's own noun for a still garment ('halter top' for the still's 'strappy bra top') maps to
            # the one inventory item in the same slot, so the wardrobe line never keeps on what the writer took off
            for gk, grx in _GARMENT_KEYS:
                if gk not in hit and re.search(grx, plain, re.I) and _SLOT_OF_KEY.get(gk):
                    same = [k for k, _ in item_rx if _SLOT_OF_KEY.get(k) == _SLOT_OF_KEY[gk] and k not in hit and k not in stay_items]
                    if len(same) == 1:
                        hit.append(same[0])
            # frs16 S1: a still garment named only in a retention clause ('the stockings stay on her legs') is not removed
            cl = re.split(r"[,;]", plain)
            def stay_only(k: str) -> bool:
                named_in = [c for c in cl if re.search(dict(item_rx)[k], c, re.I) or re.search(dict(_GARMENT_KEYS).get(k, r"$^"), c, re.I)]
                return bool(named_in) and all(_STAY_ON_RE.search(c) and not _REMOVE_VERB_RE.search(c) for c in named_in)
            hit = [k for k in hit if not stay_only(k)]
        if not hit and _join_cleared_still_on(plain) and re.search(
                r"(?i)\b(?:pull\w*|slid\w*|tug\w*|hook\w*|push\w*)\s+(?:it|them)\s+(?:aside|to one side|up)\b", plain):
            # #4 (r09): 'pulls it aside' credits the one join garment still on
            jk = [g["key"] for g in items if (g["key"] in _JOIN_KEYS or g.get("slot") == "full-body")
                  and state["garments"].get(g["key"]) == "on" and g["key"] not in (state.get("writer_aside") or [])]
            if len(jk) == 1:
                hit = jk
        for k, rx in item_rx:
            if k in hit and state["garments"].get(k) == "on" and _join_cleared_still_on(plain):
                if k not in state.setdefault("writer_aside", []):
                    state["writer_aside"].append(k)  # pull-aside / slide-up: stays on, credits W5
                continue
            if _REMOVE_VERB_RE.search(plain) and k in hit and state["garments"].get(k) == "on":
                if _not_an_undress_beat(plain):
                    continue
                state["garments"][k] = "off"
                state["writer_removed"].append(k)
                pm = [m.group(1) for m in _PLACE_RE.finditer(plain)]
                state.setdefault("places", {})[k] = pm[-1] if pm else ""
                if _SLOT_OF_KEY.get(k) == "outerwear" or k == "jacket":
                    pass  # taking off a jacket is not a full undress beat
                elif plain.strip() not in state.setdefault("undress_text", []):
                    state["undress_text"].append(plain.strip())
        if move_rx.search(plain):
            state["level"] = max(state["level"], 2)
        elif _MOVE_LEVEL_RE.search(plain):
            state["level"] = max(state["level"], 1)
        if _PENETRATION_RE.search(plain) or _ACT_RE.search(plain):
            state["act"] = True
        out.append(s)
    if cast.get("undress", True) and not (cast.get("dynamic_pose") and state["act"]):
        for k in off_items:  # gap fill: the ask (or a hand-written cast) wants her undressed and the writer left it out
            if state["garments"][k] == "on":
                state["garments"][k] = "off"
                state["builder_removed"].append(k)
    return out, state, violations


def _plural(xs: Sequence[str]) -> bool:
    return len(xs) != 1 or bool(re.search(r"(?i)[^s]s$", _head(xs[0])))


def writer_named_his_clothes(raw: str, floor: str, subject: str = "<Subject 2>") -> str:
    """Build the canonical partner-undress line from garments the writer actually named (t1104u/t1109u).

    Returns "" when the writer named none — the builder must not invent a shirt and trousers.
    """
    if not (raw or "").strip():
        return ""
    nouns = (
        "t-shirt", "tee-shirt", "polo", "hoodie", "sweater", "jumper", "jacket", "blazer",
        "trousers", "boxers", "briefs", "shorts", "jeans", "slacks", "chinos", "pants",
        "shirt", "coat", "vest", "belt", "tie", "underwear",
    )
    undress = re.compile(
        r"(?i)\b(?:pulls?|takes?|strips?|drops?|removes?|unbuttons?|unzips?|shrugs?|kicks?)\b"
        r"|\b(?:off over his|off his|from his)\b"
    )
    subj = re.compile(r"(?i)\b(?:he|his|<subject 2>|\(s2\)|the man)\b")
    found: List[str] = []
    seen: set = set()
    landing_sent = ""
    for sent in re.split(r"(?<=[.!?])\s+", raw):
        if not subj.search(sent) or not undress.search(sent):
            continue
        if re.search(r"(?i)\b(?:she|her|<subject 1>|\(s1\))\b", sent) and not re.search(
            r"(?i)\b(?:he|his|<subject 2>|\(s2\))\b", sent
        ):
            continue
        hit_this = False
        for n in sorted(nouns, key=len, reverse=True):
            if n == "shirt" and ("t-shirt" in seen or "tee-shirt" in seen):
                continue
            rx = r"(?i)(?<![tT]-)\bshirts?\b" if n == "shirt" else (r"(?i)\b" + re.escape(n) + r"s?\b")
            if re.search(rx, sent):
                key = "t-shirt" if n in ("t-shirt", "tee-shirt") else ("pants" if n in ("pants", "slacks", "chinos") else n)
                if key not in seen:
                    seen.add(key)
                    found.append("t-shirt" if n in ("t-shirt", "tee-shirt") else n)
                hit_this = True
        if hit_this and not landing_sent and re.search(
            r"(?i)\b(?:ankles?|knees?|pool(?:s|ed)? at)\b", sent
        ):
            landing_sent = sent.strip().rstrip(".")
    if not found:
        return ""
    if landing_sent:
        s = re.sub(r"(?i)^(?:\[Shot \d+\]\s*)?(?:Then,?\s+)*", "", landing_sent)
        s = re.sub(r"(?i)^(?:<Subject [12]>|he|the man)\b", subject, s, count=1)
        if not re.match(re.escape(subject) + r"\b", s):
            s = f"{subject} " + (s[:1].lower() + s[1:] if s else s)
        return s
    # Pull-aside / clearance of his garment ("pulls his trousers aside") is not a floor removal.
    removed_only = []
    for item in found:
        aside_hit = re.search(rf"(?i)\bhis\s+(?:[\w-]+\s+){{0,2}}{re.escape(item)}\b[^.;\n]*?\b(?:aside|to one side)\b", raw)
        drop_hit = re.search(
            rf"(?i)\b(?:pulls?|takes?|strips?|peels?|drops?|kicks?|steps?|pools?|slides?|tugs?|pushes?)\s+(?:off\s+)?his\s+(?:[\w-]+\s+){{0,2}}{re.escape(item)}\b[^.;\n]*?\b(?:off|down|floor|ankles?|knees?|bed|chair|couch|sand|ground)\b|\bhis\s+(?:[\w-]+\s+){{0,2}}{re.escape(item)}\b[^.;\n]*?\b(?:off|drops?|pools?)\b",
            raw,
        )
        if aside_hit and not drop_hit:
            continue
        removed_only.append(item)
    found = removed_only
    if not found:
        return ""
    prefer = [
        "t-shirt", "shirt", "polo", "hoodie", "sweater", "jumper", "jacket", "blazer", "coat", "vest",
        "trousers", "jeans", "slacks", "chinos", "pants", "shorts", "boxers", "briefs", "underwear", "belt", "tie",
    ]
    found = [n for n in prefer if n in found] + [n for n in found if n not in prefer]
    floor = re.sub(r"(?i)\bthe\s+the\b", "the", (floor or "the floor").strip()) or "the floor"
    if len(found) == 1:
        pl = _plural([found[0]])
        return f"{subject} pulls off his {found[0]}, and {'they drop' if pl else 'it drops'} to {floor} and {'stay' if pl else 'stays'} there"
    join = f"{found[0]} and {found[1]}" if len(found) == 2 else ", ".join(found[:-1]) + " and " + found[-1]
    return f"{subject} pulls off his {join}, and they drop to {floor} and stay there"


def writer_defined_missing_person(raw: str, subject: int = 2) -> bool:
    """True when the writer defined an off-still partner or third person (look, clothes, or entrance)."""
    if not (raw or "").strip():
        return False
    if subject == 3:
        who = re.compile(r"(?i)(?:<subject 3>|\(s3\)|\b(?:the (?:other )?man|the (?:other )?woman|a third)\b)")
    else:
        who = re.compile(r"(?i)(?:<subject 2>|\(s2\)|\b(?:he|his|the man|the woman|her partner)\b)")
    # "He enters her" is the act, not an entrance into the scene.
    enter = re.compile(
        r"(?i)\b(?:walks? in|comes? in|steps? in|arrives|comes? into|walks? into|steps? into|"
        r"enters? the|enters? from|is not in <picture 1>|not in the (?:still|photograph|photo))\b"
    )
    look = re.compile(
        r"(?i)\b(?:wearing|wears|dressed|hair|beard|stubble|build|tall|short|"
        r"shirt|t-shirt|trousers|pants|jeans|hoodie|jacket|coat|shorts|sweater|"
        r"adult (?:man|woman)|in his (?:twenties|thirties)|of (?:solid|slender) (?:adult )?build)\b"
    )
    for sent in re.split(r"(?<=[.!;?])\s+", raw):
        if not who.search(sent):
            continue
        if enter.search(sent) or look.search(sent):
            return True
    return False


def wardrobe_line(cast: Dict[str, Any], state: Dict[str, Any]) -> str:
    """R12 wardrobe line written from the tracked end state (names from the still inventory or the cast). dynsafe: the
    builder's 'She takes off ...' clause only names what it removes as a gap fill; items the writer removed are named
    with their end state; items kept on are a retention clause. No removal at all = a retention line only."""
    names = {g["key"]: g["name"] for g in _cast_items(cast)}
    prior_aside = set(state.get("prior_aside") or [])
    writer_aside = set(state.get("writer_aside") or [])
    all_aside = prior_aside | writer_aside
    prior_off = set(state.get("prior_off") or [])
    builder_off = [names[k] for k in state.get("builder_removed", [k for k, v in state["garments"].items() if v == "off"]) if k in names and k not in prior_off]
    writer_off = [names[k] for k in state.get("writer_removed", []) if k in names]
    kept_aside = [names[k] for k in state.get("prior_aside", []) if k in names and state["garments"].get(k) == "on"]
    on = [names[k] for k, v in state["garments"].items() if v == "on" and k in names and k not in all_aside]

    def join(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    parts = []
    if builder_off:
        pl = _plural(builder_off)
        parts.append(f"She takes off the {join(builder_off)}, and {'they fall' if pl else 'it falls'} to {cast['garments_floor']} and {'stay' if pl else 'stays'} there")
    places = state.get("places", {})
    by_place: Dict[str, List[str]] = {}
    for k in [k for k in state.get("writer_removed", []) if k in names]:
        # dynsafe (brief item 4): a removed garment lands on a named surface and stays there - the writer's own place
        # when it named one, else the still's floor/surface (garments_floor); lint W6 asks the writer to name it
        by_place.setdefault(places.get(k) or cast["garments_floor"], []).append(names[k])
    for where, xs in by_place.items():
        parts.append(("the " if parts else "The ") + f"{join(xs)} she took off {'stay' if _plural(xs) else 'stays'} on {where}")
    prev_off = [names[k] for k in state.get("prior_off", []) if k in names]
    if prev_off:
        pl = _plural(prev_off)
        parts.append(("the " if parts else "The ") + f"{join(prev_off)} she took off before {'stay' if pl else 'stays'} on {cast['garments_floor']}")
    if kept_aside:
        pl = _plural(kept_aside)
        parts.append(("and the " if parts else "Her ") + f"{join(kept_aside)} {'stay' if pl else 'stays'} pulled aside")
    if on:
        pl = _plural(on)
        lead = ("while the " if parts else "Her ") if builder_off and not writer_off else ("and the " if parts else "Her ")
        parts.append(f"{lead}{join(on)} {'stay' if pl else 'stays'} on her body")
    his = (cast.get("his_clothes") or "").strip()
    if not parts:
        return f"{his[:1].upper()}{his[1:]}." if his else ""
    line = parts[0] + "".join((", " + p) for p in parts[1:])
    return line + (f"; {his}." if his else ".")


_GENERIC_GARMENT_NOUNS = ("top", "tops", "bottom", "bottoms", "set", "lingerie", "outfit", "heels", "shoes", "boots", "sandals",
                          "bikini", "dress", "skirt", "shorts", "jeans")
_LIST_STOP_RE = re.compile(r"(?i)\b(?:front|middle|centre|center|place|position|room|light|frame|time|one|the still|<Picture)\b")


def _swap_opener_list(s: str, still_garments: str, heads: Sequence[str], absent: Optional["re.Pattern[str]"]) -> str:
    """dynsafe (limit 4): in the writer's opener, keep a garment list that names every still item (by head noun or a noun
    of the same key, e.g. thong for panties) and invents none; otherwise swap ONLY that noun phrase for the still's list
    (no fixed lingerie order, no dangling ', and'). `heads` are per-item regex alternatives."""
    if not still_garments or not heads:
        return s
    heads = [h.replace("?", "") for h in heads]
    alts = {a for h in heads for a in h.split("|") if a}
    gn = "|".join(sorted({re.escape(a) for a in alts} | {re.escape(x) for x in _GARMENT_LEXICON if x != "the sheer fabric"} |
                         set(_GENERIC_GARMENT_NOUNS), key=len, reverse=True))
    gn_rx = re.compile(r"(?i)\b(?:" + gn + r")s?\b")
    for m in re.finditer(r"(?i)\bin\s+|,\s+(?=(?:the|her)\s)", s):
        start = m.end()
        comma = m.group(0).startswith(",")
        stop = re.search(r"[;.]|\x00", s[start:])
        seg = s[start: start + (stop.start() if stop else len(s) - start)]
        chunks = list(re.finditer(r"[^,]+?(?=,\s*(?:and\s+)?|\s+and\s+|$)", seg))
        if not chunks:
            continue
        first = chunks[0].group(0)
        if len(first.split()) > 7 or _LIST_STOP_RE.search(first) or not gn_rx.search(first):
            continue
        end = start
        for c in chunks:
            txt = c.group(0)
            hits = list(gn_rx.finditer(txt))
            if not hits:
                break
            end = start + c.start() + hits[-1].end()
        writer_list = s[start:end]
        have_all = all(re.search(r"(?i)\b(?:" + "|".join(re.escape(a) for a in h.split("|") if a) + r")s?\b", writer_list) for h in heads)
        if have_all and not (absent and absent.search(writer_list)):
            return s
        out = (s[:m.start()] + " in " + still_garments + s[end:]) if comma else (s[:start] + still_garments + s[end:])
        out = re.sub(r",\s*and\s*(?=[,.;])", "", out)
        return re.sub(r"\s{2,}", " ", out)
    return s


def _pose_kind(text: str) -> Optional[str]:
    m = re.search(r"(?i)\b(stand|kneel|sit|lie|lies|lying|lean|crouch)\w*", text or "")
    if not m:
        return None
    w = m.group(1).lower()
    return {"lies": "lie", "lying": "lie"}.get(w, w)


def _man_pose(text: str) -> Optional[str]:
    m = re.search(r"(?i)(?:<Subject 2>|\(S2\)|\bhe\b)\s+(?:[\w-]+\s+){0,3}?(stands?|standing|kneels?|kneeling|lies|lying|sits?|sitting)\b", text or "")
    return _pose_kind(m.group(1)) if m else None


# Max Architect 3, Derrick t1437s5374 #2: the builder's move-in beat and the writer's own move name the same pose
_MOVE_PAIRS = [
    (r"\bknee(?:s|ls?|ling)\b", r"\b(?:kneel\w*|(?:drops?|sinks?|goes|gets?|lowers? herself|comes? down) (?:down )?(?:to|on|onto) her knees|on her knees)\b"),
    (r"\bhands and knees\b|\ball fours\b", r"\bhands and knees\b|\ball fours\b"),
    (r"\bon her back\b|\blies back\b", r"\bon her back\b|\blies back\b|\blying back\b|\blower\w* (?:\w+ ){0,2}onto (?:her|the) back\b"),  # (2) Derrick t247s837
    (r"\bstraddl\w*|\bastride\b", r"\bstraddl\w*|\bastride\b"),
    (r"\bbends? (?:forward|over)\b|\bbent (?:forward|over)\b", r"\bbend\w* (?:forward|over)\b|\bbent (?:forward|over)\b"),
]


_WAIST_SURFACE_RE = re.compile(r"(?i)\b(?:sideboard|table|counter|desk|dresser|vanity|bar|kitchen island|washing machine|piano)\b")


def _same_move(beat: str, text: str) -> bool:
    return any(re.search(a, beat or "", re.I) and re.search(b, text or "", re.I) for a, b in _MOVE_PAIRS)


def transition_beat(cast: Dict[str, Any], writer_text: str = "") -> str:
    """dynsafe (limit 3): one short bridge from the still pose to the act pose, used only when the writer wrote no move.
    Built from the still's pose and the writer's own man pose (standing / kneeling / lying), never a fixed lie-back."""
    if str(cast.get("partner_type") or "").lower() == "none" or int(cast.get("bodies") or 2) < 2:
        return ""
    pos = cast.get("position")
    still = _pose_kind(cast.get("still_pose") or "")
    man = _man_pose(writer_text)
    surf = cast.get("surface") or _scene(cast)["surface"]
    if pos == "blowjob":
        man = man or "stand"
        lead = {"stand": "<Subject 2> stands in front of her", "kneel": "<Subject 2> kneels upright in front of her",
                "lie": f"<Subject 2> lies back on {surf}", "sit": "<Subject 2> sits in front of her"}.get(man, "<Subject 2> stands in front of her")
        if man == "lie":
            her = "she kneels between his spread thighs"
        elif still == "kneel":
            her = "she stays on her knees and shifts forward between his legs"
        else:
            her = f"she sinks to her knees on {surf} in front of him"
        return f"{lead}, and {her}, one hand wrapping around the base of his penis."
    if pos == "missionary":
        her = f"She stays on her back on {surf}" if still == "lie" else f"She lowers onto her back on {surf}"
        return her + ", and <Subject 2> kneels between her spread thighs, his forearms bracing beside her ribs."
    if pos in ("cowgirl", "reverse cowgirl", "reverse_cowgirl", "riding"):
        facing = " facing his feet" if pos in ("reverse cowgirl", "reverse_cowgirl") else ""
        return f"<Subject 2> lies back on {surf}, and she swings a knee over and straddles his hips{facing}."
    if pos == "doggy":
        her = (f"From her kneel she leans forward onto her hands and knees on {surf}" if still == "kneel"
               else f"She gets down onto {surf} and settles onto her hands and knees")
        him = "stands behind her" if man == "stand" else "kneels behind her"
        return her + f", and <Subject 2> {him} and grips her hips with both hands."
    if pos == "threesome":
        return f"<Subject 2> and <Subject 3> position with <Subject 1> on {surf}."
    if pos == "mmf":
        return f"<Subject 2> and <Subject 3> position around <Subject 1> on {surf}."
    if pos == "ffm":
        return f"<Subject 1> and <Subject 2> position with <Subject 3> on {surf}."
    if pos == "mmf_double_blowjob":
        return f"<Subject 2> and <Subject 3> position in front of <Subject 1> on {surf}, and she sinks to her knees between them."
    return cast.get("position_beat", "")


_ORAL_ACT_RE = re.compile(r"(?i)\b(?:suck\w*|bob(?:s|bing)?|in her mouth|into her mouth|lips (?:slide|seal|wrap|close)\w*|deepthroat\w*|"
                          r"blow ?job|licks? (?:his|the) (?:shaft|length|tip|glans)|takes? him (?:in|into) her mouth)\b")
_MINOR_RE = re.compile(r"(?i)\b(?:underage|minors?|child|children)\b")  # the queue stop words; no youth/age gate added

# --- oralfoley (2026-11-11, Derrick via Prompt maker: "Yes send all revised riles"): every check below is a FLAG or a
# NOT_READY / send-back. The builder never strips or rewrites her dialogue and never inserts his thrust, his lines or foley.
_MOUTH_FREE_RE = re.compile(r"(?i)\b(?:pulls?|slides?|draws?|lifts?|eases?|pops?)\s+(?:her (?:mouth|lips|head)\s+)?(?:off|away from|free of)\s+"
                            r"(?:him|his (?:penis|cock|shaft|glans|tip))\b|\bmouth (?:comes |slides |pops )?(?:free|off him)\b|"
                            r"\breleases? (?:him|his (?:penis|cock|shaft)) from her (?:mouth|lips)\b|\bwith a wet pop\b")
_D_STAGE_RE = re.compile(r"(?i)\*[^*]+\*|\((?!English\))[^)]*\)|\[(?!English\])[^\]]*\]")
_D_INTERJECTION_RE = re.compile(r"(?i)^[\W\s]*(?:(?:m{2,}h*|a+h+|o+h+|u+h+|u+n+g+h*|n+g+h+|h+a+h+|o{2,}h*|hn+g*|gl[uo]+k+|ga+h+|mm+)[\W\s]*)+$")
_STOCK_TALK_RE = re.compile(r"(?i)\bfuck me harder\b|\btake it\b[.!,]?\s*don'?t you (?:dare )?stop\b|\bdon'?t you (?:dare )?stop\b")
_BODY_SOUND_RE = re.compile(r"(?i)\b(?:moan\w*|gasp\w*|groan\w*|pant\w*|breath\w*|slap\w*|smack\w*|wet\w*|creak\w*|squeak\w*|"
                            r"gag\w*|suction|slurp\w*|whimper\w*|grunt\w*|squelch\w*|cr(?:y|ies) out|sob\w*|hiss\w*)\b")
_TALK_ASK_RE = re.compile(r"(?i)\b(?:talk\w*|dirty|moan\w*|nois\w*|sounds?|says?|tells?|beg\w*|scream\w*)\b")
_COWGIRL_RE = re.compile(r"(?i)\b(?:(?:reverse )?cowgirl|riding|rides? him|rides? his)\b")
_RISE_RE = re.compile(r"(?i)\b(?:rises?|rising|lifts? (?:herself|up|her hips)|raises? (?:herself|her hips)|comes? up|pushes? up off)\b")
_SINK_RE = re.compile(r"(?i)\b(?:sinks?|sinking|drops?|dropping|comes? (?:back )?down|lowers? herself|slams? (?:herself )?down|drives? (?:herself )?down|grinds? down)\b")
_HIS_LIFT_RE = re.compile(r"(?i)\b(?:his (?:hips|pelvis)|he)\b[^.;]{0,50}?\b(?:lift\w*|rise\w*|rising|drives? up\w*|thrusts? up\w*|buck\w*|"
                          r"surg\w* up|push\w* up|pump\w* up)\b")
_LIFT_MEASURE_RE = re.compile(r"(?i)\b(?:off the [\w -]{2,25}|clear of the [\w -]{2,25}|\d+(?:\.\d+)?\s*(?:cm|centimet\w*|inch\w*|in)\b|"
                              r"an inch|a few inches|a few centimet\w*|a hand'?s? (?:width|breadth))")
_MEET_RE = re.compile(r"(?i)\b(?:meet\w*|into her|up into her|as she (?:sinks|drops|comes down|lowers|slams))\b")


def _oc_cast(cast: Dict[str, Any]) -> bool:
    """oralfoley rule 3 scope: OC / Cond stills only, never a real-person likeness, named parody or parody voice form."""
    return not (cast.get("index_voice") or cast.get("real_person") or cast.get("parody") or cast.get("named_parody"))


def audio_act_checks(units: Sequence[str], cast: Dict[str, Any], act_written: bool) -> List[Dict[str, Any]]:
    """oralfoley rules 1, 3, 5, 6 on the ordered prompt units. Returns {code, idx, why, hard}; hard = NOT_READY / send
    back, soft = flag. Nothing is rewritten here.
    D1 her (S1) <d> while her mouth is on him; D2 foley / moan / stage cue inside <d>; D3 'no speech' written into the prompt;
    D4 OC stock dirty-talk line; A1 explicit clip with no talk and no body sound; R1 cowgirl PRIMARY MOTION without her rise
    and sink plus a measurable lift of his pelvis meeting her descent."""
    out: List[Dict[str, Any]] = []
    oral = False
    for i, u in enumerate(units):
        ev = sorted([(m.start(), "on") for m in _ORAL_ACT_RE.finditer(_D_RE.sub(lambda x: " " * len(x.group(0)), u))] +
                    [(m.start(), "off") for m in _MOUTH_FREE_RE.finditer(_D_RE.sub(lambda x: " " * len(x.group(0)), u))] +
                    [(m.start(), "d") for m in _D_RE.finditer(u)])
        for pos, kind in ev:
            if kind == "on":
                oral = True
            elif kind == "off":
                oral = False
            elif oral:
                giver = cast.get("oral_giver")
                if not giver:
                    if re.search(r"(?:<Subject 2>|\(S2\))\s+[^.;]{0,40}?(?:" + _ORAL_ACT_RE.pattern.replace("(?i)", "") + ")", u):
                        giver = "S2"
                    elif re.search(r"(?:<Subject 3>|\(S3\))\s+[^.;]{0,40}?(?:" + _ORAL_ACT_RE.pattern.replace("(?i)", "") + ")", u):
                        giver = "S3"
                    else:
                        giver = "S1"
                if _span_speaker(u[:pos]) == giver:
                    out.append({"code": "D1", "idx": i, "hard": True,
                                "why": f"the oral giver ({giver}) spoken line sits while mouth is on partner; giver stays silent on the oral beat, side is "
                                       "diegetic foley (wet suction, a gag on the deep stroke, breath through nose); partner may speak"})
        for m in _D_RE.finditer(u):
            words = re.sub(r"(?i)^\s*\[English\]\s*", "", m.group(1))
            if _D_STAGE_RE.search(words) or _D_INTERJECTION_RE.match(words) or not words.strip():
                out.append({"code": "D2", "idx": i, "hard": True,
                            "why": "moans, foley or stage cues inside <d>; only [English] and the verbatim spoken words go in <d>, "
                                   "body sound goes in plain diegetic sentences"})
            if _oc_cast(cast) and _STOCK_TALK_RE.search(words):
                out.append({"code": "D4", "idx": i, "hard": True,
                            "why": "stock dirty-talk line ('Fuck me harder' / 'Take it. Don't you stop.'); write a fresh, crude line "
                                   "for this exact stroke, spoken to the other adult"})
        if re.search(r"(?i)\bno speech\b", _D_RE.sub("", u)):
            out.append({"code": "D3", "idx": i, "hard": True, "why": "the words 'no speech' are written into the prompt; leave silence unwritten"})
    plain_all = " ".join(_D_RE.sub("", u) for u in units)
    if act_written and not any(_D_RE.search(u) for u in units) and not _BODY_SOUND_RE.search(plain_all):
        out.append({"code": "A1", "idx": None, "hard": bool(_TALK_ASK_RE.search(cast.get("ask") or "")),
                    "why": "explicit clip with no talk and no body sound; the builder does not invent audio"})
    if cast.get("position") in ("cowgirl", "reverse cowgirl", "reverse_cowgirl", "riding") or _COWGIRL_RE.search(cast.get("ask") or ""):
        pm = [(i, u) for i, u in enumerate(units) if "<d>" not in u and _PRIMARY_RE.search(u)]
        ok = any(_RISE_RE.search(u) and _SINK_RE.search(u) and _HIS_LIFT_RE.search(u) and _LIFT_MEASURE_RE.search(u) and _MEET_RE.search(u)
                 for _, u in pm)
        if not ok:
            out.append({"code": "R1", "idx": pm[0][0] if pm else None, "hard": True,
                        "why": "cowgirl PRIMARY MOTION must name her rise and her sink and a measurable lift of his pelvis off the "
                               "surface meeting her descent; the builder does not write his thrust"})
    return out


_AGE_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "twenty-one": 21, "twenty-two": 22,
    "twenty-three": 23, "twenty-four": 24, "twenty-five": 25, "twenty-six": 26,
    "twenty-seven": 27, "twenty-eight": 28, "twenty-nine": 29, "thirty": 30,
    "thirty-one": 31, "thirty-two": 32, "thirty-three": 33, "thirty-four": 34,
    "thirty-five": 35, "thirty-six": 36, "thirty-seven": 37, "thirty-eight": 38,
    "thirty-nine": 39, "forty": 40, "forty-one": 41, "forty-two": 42, "forty-three": 43,
    "forty-four": 44, "forty-five": 45, "fifty": 50, "sixty": 60,
}


def _adult_age_ok(text: str) -> bool:
    """Keep a writer biometric line only when every named age is 18+ (or no numeric age is present)."""
    ages = [int(m.group(1)) for m in re.finditer(r"\b(\d{1,3})\s*(?:-?\s*years?\b|yo\b|y\.?o\.?)", text or "", re.I)]
    # Longest phrases first so 'twenty-four' is not also counted as 'four' or 'twenty'.
    for word, n in sorted(_AGE_WORDS.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(word) + r"\b", text or "", re.I):
            ages.append(n)
            break
    return all(a >= 18 for a in ages)


def _writer_subject_bios(raw: str) -> Dict[str, str]:
    """Prefer the writer's R11 biometric / age clauses over the builder's default twenties / twenty-six lines."""
    out: Dict[str, str] = {}
    if not (raw or "").strip():
        return out
    m_sec = re.search(
        r"(?is)\bsubject_definitions:\s*\n(.*?)(?=\n(?:summary|retention_analysis|detailed_description|diegetic sound)\s*:|\Z)",
        raw,
    )
    sec = m_sec.group(1) if m_sec else raw
    m1 = (
        re.search(
            r"(?is)(?:complete fidelity|<Picture 1>)\s*;\s*((?:an|the) adult (?:wo)?man,[^;\n]+?)\s*;\s*(?:she|he) is \(S1\)",
            sec,
        )
        or re.search(
            r"(?im)^<Subject 1> is (an adult man,[^;\n]+?)\s*(?:;\s*|\s*,?\s*\band\b\s+)he is \(S1\)",
            sec,
        )
    )
    if m1 and _adult_age_ok(m1.group(1)):
        bio = " ".join(m1.group(1).split()).rstrip(" ,;")
        if re.search(r"(?i)\ban adult man\b", bio):
            out["s1_man"] = bio
        else:
            out["woman"] = bio
    for idx, man_key, partner_key in ((2, "man", "partner"), (3, "man3", "partner3")):
        m = re.search(
            rf"(?im)^<Subject {idx}> is ([^\n]+?)\s*(?:;\s*|\s*,?\s*\band\b\s+)(?:he|she|it) is \(S{idx}\)",
            sec,
        )
        if m and _adult_age_ok(m.group(1)):
            bio = " ".join(m.group(1).split()).rstrip(" ,;")
            if re.search(r"(?i)\bexact same\b[^;\n]*\bshown in <Picture", bio):
                continue
            if re.search(r"(?i)\b(?:an adult |the )?(?:woman|futa)\b", bio):
                out[partner_key] = bio
            else:
                out[man_key] = bio
    return out


# Style-only lints are warnings, not stops (t1355). R1 and D4 are hard stops again (Derrick t179s554, 2026-11-13).
# Warnings go to report["warnings"] and never block. Still blocking: R1, D4, minor descriptor, packed beats, W5, D1,
# A1 on a talk ask, hard scene addenda, off-still partner undefined, missing sections, unknown act, people count,
# speaker attribution, silent drops, and P2-DOSE / P2-DRINK safety.
_STYLE_WARN_CODES = frozenset({"D2", "D3"})
_STYLE_WARN_PREFIXES = ("transition word left", "quoted speech left outside <d>", "double speech lead",
                        "INDEX voice wording on an OC cast", "leg position changes", "facing conflict",
                        "surface conflict", "doggy pose conflict")


_SHOT_HDR_RE = re.compile(r"\[Shot\s*(\d+)\]\s*")
_SHOT_CLOCK_RE = re.compile(r"(?i)^At\s+(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\s*,\s*")


def split_shots(desc: str, clip_seconds: float) -> Tuple[str, List[Tuple[int, str, str]], Optional[str]]:
    """B1 (Max Architect 3, Derrick (long-scene spec, Prompt maker t243s804, 2026-11-13)): split a multi-shot body into the master ([Shot 1] text) and later shots
    (n, 'MM:SS.mmm', body). Rules (R8): N counts up from 2, clocks increase, first cut >= 1.5 s, last cut <= clip - 2.0 s,
    every shot >= 2.0 s. Returns (master, shots, error)."""
    hs = list(_SHOT_HDR_RE.finditer(desc))
    later = [m for m in hs if int(m.group(1)) >= 2]
    if not later:
        return desc, [], None
    master = desc[:later[0].start()].rstrip()
    shots: List[Tuple[int, str, str]] = []
    prev_t, err = 0.0, None
    for i, m in enumerate(later):
        body = desc[m.end():(later[i + 1].start() if i + 1 < len(later) else len(desc))].strip()
        c = _SHOT_CLOCK_RE.match(body)
        n = int(m.group(1))
        if n != i + 2:
            err = err or f"shot numbers must count up from 2 (got [Shot {n}])"
        if not c:
            err = err or f"[Shot {n}] needs a clock 'At MM:SS.mmm, the camera cuts to ...'"
            shots.append((n, "", body))
            continue
        t = int(c.group(1)) * 60 + int(c.group(2)) + int((c.group(3) or "0").ljust(3, "0")) / 1000.0
        if i == 0 and t < 1.5:
            err = err or f"first cut at {t:.3f}s is before 1.5 s"
        if t - prev_t < 2.0:
            err = err or f"[Shot {n}] at {t:.3f}s leaves the shot before it under 2.0 s"
        if t > clip_seconds - 2.0:
            err = err or f"[Shot {n}] at {t:.3f}s is later than clip length {clip_seconds:.3f}s - 2.0 s"
        prev_t = t
        shots.append((n, f"{int(t // 60):02d}:{t % 60:06.3f}", body[c.end():]))
    return master, shots, err


_FINAL_RAW_ACT_RE = re.compile(
    r"(?i)\b(?:standing_mf|ff_scissoring|ff_cunnilingus|prone_bone|mf_anal|male_solo|female_solo|mmf_double_blowjob)\b|\b(?:ffm|mmf)\s+clip\b"
)
_FINAL_COMMA_GLUE_RE = re.compile(
    r"\(S[123]\)\s*,\s+(?:kneels|stands|lies|sits|leans|straddles|thrusts|strokes|pulls|grabs|grips|bends|enters|climbs|drops|rides|laps|sucks)\b"
)


def lint_final_prompt(full: str) -> List[str]:
    """Item 16: hard final-text check on the built prompt."""
    errs: List[str] = []
    if re.search(r"(?i)\bthe\s+the\b", full):
        errs.append("double article 'the the'")
    dd_m = re.search(r"(?is)\bdetailed_description:\s*\n(.*)\Z", full)
    dd_part = dd_m.group(1) if dd_m else full
    if re.search(r"<Subject\s+\d+>", dd_part):
        errs.append("<Subject N> tag in detailed_description")
    if re.search(r"(?i)previous clip's end pose", full):
        errs.append("placeholder \"previous clip's end pose\" in prompt")
    if re.search(r"(?i)\bsays\s*,\s*\(S\b|\bsays\s*,\s*\(S\d\)", full):
        errs.append("malformed 'says, (S' speech glue")
    if _FINAL_RAW_ACT_RE.search(full):
        errs.append("raw act_id in built prompt")
    if _FINAL_COMMA_GLUE_RE.search(dd_part):
        errs.append("'(Sn), <verb>' comma glue in detailed_description")
    return errs


def finalize_writer_prompt(raw: str, cast: Dict[str, Any], strict: bool = True) -> Tuple[str, Dict[str, Any]]:
    """Turn one free-text writer prompt into the R5 paste for an OC RefMod clip that opens on <Picture 1>.

    cast keys: woman, man (biometric lines), voice_s1, voice_s2 (OC voice descriptions, "a ... voice"),
    still (what <Picture 1> shows: place and framing), still_wardrobe, garments_off, garments_stay, garments_floor
    (where removed clothing lies), his_clothes, position_beat, primary_motion, contact, camera_tail, summary_act.
    """
    global _ABSENT_GARMENT_RE
    _ABSENT_GARMENT_RE = re.compile(cast["absent_garments"], re.I) if cast.get("absent_garments") else None
    _set_ctx(cast)
    report: Dict[str, Any] = {"stripped": [], "added": [], "flags": []}
    # Max Architect 3, Derrick t1104u/t1109u: partner undress only in clothes the writer named.
    _solo_man = (
        cast.get("s1_gender") == "man"
        or (cast.get("act_id") or cast.get("position")) == "male_solo"
        or str(cast.get("partner_type") or "").lower() == "none"
        or int(cast.get("bodies") or 2) < 2
    )
    if not _solo_man and not (cast.get("his_clothes") or "").strip():
        filled = writer_named_his_clothes(raw, cast.get("garments_floor") or "the floor")
        if filled:
            cast = dict(cast, his_clothes=filled)
            report["added"].append("his_clothes from writer-named partner garments")
    # P1 rework: do not copy writer's subject_definitions into cast; source from cast/beat_card and validate S2/S3 clauses.
    _youth_check_re = re.compile(
        r"(?i)\b(?:child\w*|kids?|teen\w*|tween|underage|under-age|minor|loli\w*|shota\w*|schoolgirl|little girl|"
        r"little boy|young girl|young boy|preteen|pre-teen|pubescent|adolescent|juvenile)\b"
    )
    for _pk in ("man", "partner", "man3", "partner3"):
        _pval = str(cast.get(_pk) or "").strip()
        if _pval and (not _adult_age_ok(_pval) or _MINOR_RE.search(_pval) or _youth_check_re.search(_pval)):
            raise WriterNotReady(f"NOT_READY: partner definition {_pk!r} failed adult age / youth lint")
    if cast.get("still_read"):
        raw, report["still_facts"] = apply_still_facts(raw, cast["still_read"])
    secs = split_writer_sections(raw)
    for name in list(secs):
        if len(secs[name]) > 1:
            report["stripped"].append(f"duplicate {name} block x{len(secs[name]) - 1}")
    desc_raw = (secs.get("detailed_description") or secs.get("integrated_multimodal_description") or [""])[0]
    if not desc_raw.strip():
        # writer dropped the detailed_description header: the shot starts at the first [Shot 1] in any section
        for k, v in secs.items():
            m = re.search(r"(?m)^\s*\[Shot 1\]", v[0])
            if m:
                desc_raw = v[0][m.start():]
                secs[k] = [v[0][:m.start()]] + v[1:]
                report["stripped"].append(f"missing detailed_description header: [Shot 1] recovered from {k}")
                break
        else:
            for k, v in secs.items():
                lines = v[0].splitlines()
                last = max((i for i, ln in enumerate(lines) if _RETENTION_LINE_RE.search(ln)), default=None)
                if last is not None and "\n".join(lines[last + 1:]).strip():
                    desc_raw = "\n".join(lines[last + 1:])
                    report["stripped"].append(f"missing detailed_description header: action after retention lines of {k}")
                    break
            else:
                desc_raw = (secs.get("_lead") or [""])[0]
    desc_raw = "\n".join(ln for ln in desc_raw.splitlines() if not _RETENTION_LINE_RE.search(ln))
    later_shots: List[Tuple[int, str, str]] = []
    if str(cast.get("shots") or "single").lower() == "multi":  # B1: later shots pass through; single = today's collapse
        desc_raw, later_shots, shot_err = split_shots(desc_raw, float(cast.get("clip_seconds", 10.125)))
        if shot_err:
            raise WriterNotReady("NOT_READY: shot syntax: " + shot_err)
        if later_shots:
            report["shots"] = [{"shot": n, "at": t} for n, t, _ in later_shots]
    sound_raw = " ".join(b for k, v in secs.items() if k in _SOUND_HEADERS for b in v[:1])
    if sound_raw:
        report["stripped"].append("labeled sound header -> plain end-of-beat sound sentences (R7)")
    if any(k in _MUSIC_HEADERS for k in secs):
        report["stripped"].append("music header dropped")
    for k in ("subject_definitions", "retention_analysis"):
        if k in secs:
            report["stripped"].append(f"writer {k} replaced by builder R11/R12 block")
    voices = {"S1": cast.get("voice_s1", OC_VOICE_S1), "S2": cast.get("voice_s2", OC_VOICE_S2),
              "S3": cast.get("voice_s3", "a low, firm adult voice")}
    still_garments = cast.get("still_garments") or (re.search(r"\bin (a .*?)(?:, facing|$)", cast.get("still_wardrobe", "")) or [None, ""])[1]
    opener_holder: Dict[str, Optional[str]] = {"text": None}
    to_quote = lambda b: _QUOTE_RE.sub(lambda m: f"<d>[English] {m.group(1).strip()}</d>", b)

    def clean(block: str, body: bool = False) -> List[str]:
        """Strip one section sentence by sentence (pySBD units). For the body, the writer's opener is found on the RAW
        sentence (before any garment trimming): its garment list becomes the still's cast list, it is kept once, and a
        second opener goes. A removal of a garment the still does not have drops the whole sentence and its It/They
        orphan. A dropped sentence never takes a spoken line with it (the line is kept as its own unit)."""
        kept: List[str] = []
        prot, spans = _protect_d(block)
        dropped_prev = False
        for s in _sentences(prot):
            s = _restore_d(s, spans)
            plain = _D_RE.sub("", s)
            if dropped_prev and _ORPHAN_RE.match(plain):
                report["stripped"].append("orphan: " + s[:80])
                continue
            why = None
            if body and _OPENER_RE.search(_normalize_labels(plain)):
                if opener_holder["text"] is None:
                    # NB1: never overwrite (S2)/(S3)'s attire in the opener with <Picture 1>'s garments.
                    _pm_op = re.search(r"(,\s*(?:and\s+)?|;\s*)(?=\(S[23]\)|<Subject\s+[23]>)", s)
                    _s_her, _s_tail = (s[:_pm_op.start()], s[_pm_op.start():]) if _pm_op else (s, "")
                    _s_her = _ABSENT_SPAN_RE.sub("in " + still_garments, _s_her) if still_garments else _s_her
                    if still_garments:  # dynsafe: keep a complete writer list, else swap only that noun phrase
                        inv = cast.get("inventory") or [{"name": x, "key": _garment_key(x)} for x in _items(still_garments)]
                        heads = ["|".join([_head(g["name"])] + (_KEY_NOUNS[g["key"]].split("|") if g.get("key") in _KEY_NOUNS else []))
                                 for g in inv]
                        s2 = _swap_opener_list(_s_her, still_garments, heads, _ABSENT_GARMENT_RE)
                        if s2 != _s_her:
                            report["stripped"].append("opener garment list swapped for the still's list: " + s[:80])
                        _s_her = re.sub(r"(?i)\bin (in " + re.escape(still_garments) + ")", r"\1", s2)
                    s = _s_her + _s_tail
                    c = _strip_sentence(s)
                    if c and not _is_fragment(c):
                        opener_holder["text"] = c
                        kept.append(c)
                        dropped_prev = False
                        continue
                else:
                    why = "second writer opener (keep exactly one)"
            if not why and body and _ABSENT_GARMENT_RE and _ABSENT_GARMENT_RE.search(plain) and (
                    _REMOVE_VERB_RE.search(plain) or re.search(r"(?i)\bover her head\b", plain)):
                if not _ABSENT_GARMENT_RE.search(_hers_text(plain)):
                    # frs16 S1: only the partner's clothes match the absent list ('his t-shirt and jeans'): not W4.
                    # W4 does not drop S3 garments that belong to that person in the brief or the still.
                    is_s3_clothes = bool(re.search(r"(?:<Subject 3>|\(S3\))", s))
                    if is_s3_clothes:
                        pass
                    else:
                        t = _drop_clauses(s, _ABSENT_GARMENT_RE)
                        if t and not _ABSENT_GARMENT_RE.search(_D_RE.sub("", t)):
                            if t != s:
                                report["stripped"].append("his clothes clause (absent-list word, not W4; sentence kept): " + s[:80])
                            s, plain = t, _D_RE.sub("", t)
                        elif not t:
                            why = "his clothes only (the builder's his_clothes line is his undress)"
                else:
                    why = "removal of a garment the still does not have"
                    if any(re.search(g["rx"], _hers_text(plain), re.I) for g in _cast_items(cast)):
                        # frs16 S1: the sentence also undresses a still garment: drop only the absent-garment clause,
                        # never her undress of the garments the still shows
                        t = _drop_clauses(s, _HersAbsent(_ABSENT_GARMENT_RE))
                        if t and not _ABSENT_GARMENT_RE.search(_hers_text(_D_RE.sub("", t))):
                            report["stripped"].append("absent-garment clause dropped (still-garment undress kept): " + s[:80])
                            s, plain, why = t, _D_RE.sub("", t), None
            if why == "removal of a garment the still does not have" and _MOVE_SOUND_RE.search(plain) and "<d>" not in s:
                # a sound or movement sentence loses only the removal clauses, never the whole sentence (F_03 room tone)
                garm = "|".join(r for _, r in _GARMENT_KEYS)
                rx = re.compile(r"(?:" + _ABSENT_GARMENT_RE.pattern + r")|(?=.*(?:" + garm + r"|\b(?:it|them|they)\b))(?=.*" +
                                _REMOVE_VERB_RE.pattern + ")", re.I)
                t = _drop_clauses(s, rx)
                if t and not _ABSENT_GARMENT_RE.search(_D_RE.sub("", t)):
                    report["stripped"].append("removal clauses of an absent garment (sentence kept): " + s[:80])
                    s, why = t, None
            c = None if why else _strip_sentence(s)
            if c is not None and c != s and _FRAGMENT_START_RE.match(_D_RE.sub("", c).strip()):
                why, c = "subjectless leftover", None
            if c is None:
                report["stripped"].append((why + ": " if why else "") + s[:90])
                for m in _D_RE.finditer(s):  # salvage the spoken line as its own unit
                    kept.append(f"({_span_speaker(s[:m.start()])}) says, {m.group(0)}")
                    report["stripped"].append("spoken line kept from a dropped sentence: " + m.group(1)[:40])
                dropped_prev = True
                continue
            dropped_prev = False
            kept.append(c)
        return kept

    desc_q, sound_q = to_quote(desc_raw), to_quote(sound_raw)
    speech_in = [re.sub(r"^\[English\]\s*", "", x.strip(), flags=re.I) for x in _D_RE.findall(desc_q) + _D_RE.findall(sound_q)]
    ledger: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {"S1": 0, "S2": 0, "S3": 0}
    budget = speech_budget(cast)
    max_lines = max(1, int(round(float(cast.get("clip_seconds", 10.0)) / 5.0)))  # B2: lines per speaker scale with length
    body = convert_speech(clean(desc_q, body=True), voices, max_lines=max_lines, counts=counts, ledger=ledger, budget=budget)
    report["counts"] = counts
    opener = opener_holder["text"]
    if opener is not None:
        opener = next((x for x in body if _OPENER_RE.search(_D_RE.sub("", x))), None)
    body = _resolve_camera(body, cast["camera_tail"])
    def _has_writer_camera(s: str) -> bool:
        plain = _D_RE.sub("", s)
        return bool(_CAMERA_SENTENCE_RE.search(plain) or re.search(
            r"(?i)\b(?:the camera\b|held,?\s+medium(?:[- ]close)?\s+shot|held medium shot|the held medium shot|a fixed [^.]*\bangle|static medium shot)\b",
            plain))
    cams = [s for s in body if "<d>" not in s and _has_writer_camera(s)]
    if not cams:
        body.insert(0, f"The camera holds a static medium shot at hip height, {cast['camera_tail']}.")  # dynsafe: no surface noun
        report["added"].append("camera sentence (R23)")
    else:
        body.remove(cams[0])
        body.insert(0, cams[0])
    cam, rest = body[0], body[1:]
    pms = [i for i, x in enumerate(rest) if "<d>" not in x and _PRIMARY_RE.search(x)]
    motion = ""
    if not cast.get("primary_motion", "x"):
        report["flags"].append({"code": "pm_writer_only", "why": "no builder PRIMARY MOTION for this position; the writer's line is used as written"})
    elif pms and _TEMPO_RE.search(rest[pms[0]]):
        rest = [x for i, x in enumerate(rest) if i not in pms[1:]]
        if len(pms) > 1:
            report["stripped"].append(f"extra PRIMARY MOTION x{len(pms) - 1}")
    else:
        # Max Architect 3, Derrick t1437s5374 #3: the writer's own tempo sentence gets the label, never a second stock tempo
        tz = next((i for i, x in enumerate(rest) if "<d>" not in x and _TEMPO_RE.search(x) and not _CAMERA_SENTENCE_RE.search(x)
                   and (_ACT_RE.search(x) or _PENETRATION_RE.search(x) or _ORAL_ACT_RE.search(x) or not cast.get("contact"))), None)
        if tz is not None and not pms:
            lead = re.match(r"(?i)\s*(?:as it builds,\s*)?", rest[tz])
            rest[tz] = rest[tz][:lead.end()] + "PRIMARY MOTION - " + rest[tz][lead.end():]
            report["added"].append("PRIMARY MOTION label on the writer's tempo sentence (R17)")
        else:
            rest = [x for i, x in enumerate(rest) if i not in pms]
            motion = f"PRIMARY MOTION - {cast['primary_motion']}."
            report["added"].append("PRIMARY MOTION with tempo (R17)" + (" (writer's had no tempo)" if pms else ""))
    rest, state, violations = track_state(rest, cast, keep=[opener] if opener else [])
    if opener and opener not in rest:
        opener = next((x for x in rest if _OPENER_RE.search(_D_RE.sub("", x))), None)
    report["violations"] = violations
    report["state"] = state
    mv_rx = re.compile(cast.get("move_check") or cast.get("position_check") or r"$^", re.I)
    mv_hits = [x for x in rest if "<d>" not in x and x != opener and mv_rx.search(_D_RE.sub("", x))]
    if len(mv_hits) >= 2:  # pmfix5: one position sentence; a short repeat goes (G_02 'Weight shifts forward onto hands and knees.')
        short = min(mv_hits, key=lambda x: len(x.split()))
        if len(short.split()) <= 8:
            rest.remove(short)
            report["stripped"].append("position repeat: " + short[:80])
    text_body = _D_RE.sub("", " ".join(rest))
    pt = str(cast.get("partner_type") or "man").lower()
    b_kind = cast.get("beat_kind", "act")
    if b_kind in ("dance", "tease", "transformation", "talk"):
        report["act_written"] = False
    else:
        _aid = str(cast.get("act_id") or cast.get("position") or "")
        _ffm_ok = _aid in ("ffm", "mmf", "mmf_double_blowjob", "threesome") and (
            _ACT_RE.search(text_body) or _ORAL_ACT_RE.search(text_body) or _PENETRATION_RE.search(text_body)
            or re.search(r"(?i)(?:<Subject [123]>|\(S[123]\)).{0,80}(?:mouth|tongue|fingers?|scissor|straddl|rides?|thrust|pumps?|sucks?)", text_body)
        )
        report["act_written"] = bool(state.get("act") or _ORAL_ACT_RE.search(text_body) or _ffm_ok)

    beat = transition_beat(cast, text_body) if cast.get("dynamic_pose") else cast["position_beat"]
    contact = ""
    act_ent = cast.get("act_entry") or (get_act(cast.get("position", "")) if cast.get("position") else None)
    all_shots_plain = " ".join([text_body] + [_D_RE.sub("", b) for _, _, b in later_shots])
    has_contact = bool(_CONTACT_RE.search(all_shots_plain) or (cast.get("continued") and _PENETRATION_RE.search(all_shots_plain)))
    if pt == "man" and b_kind == "act" and (act_ent or cast.get("position") is None):
        contact = "" if has_contact else cast.get("contact", "")
    if contact:
        report["added"].append("contact geometry line (R19)")
    wardrobe = wardrobe_line(cast, state)
    if wardrobe:
        report["added"].append("wardrobe line from the tracked end state (R12)")
    has_move = bool(re.search(cast.get("move_check") or cast.get("position_check", r"$^"), text_body, re.I))
    has_move = has_move or _same_move(cast.get("position_beat") or "", text_body)  # #2: no second move-in sentence
    if re.search(r"(?i)\bkneel", beat or "") and _WAIST_SURFACE_RE.search(str(cast.get("surface") or _scene(cast)["surface"] or "")):
        has_move = True  # (2) Derrick t247s837: never a kneel move-in on a waist-high surface
        report["stripped"].append("kneel move-in skipped (waist-high surface)")

    def is_act(x: str) -> bool:
        if "<d>" in x and not _D_RE.sub("", x).strip(" ,.():S12says"):
            return False
        if _CAMERA_SENTENCE_RE.search(_D_RE.sub("", x)) or re.search(r"(?i)\bthe camera\b|\bthe lens\b", x):
            return False  # 'thrusts still running' inside camera text is not the act (F_02)
        return bool(_ACT_RE.search(x) or _PENETRATION_RE.search(x))
    act_at = next((i for i, x in enumerate(rest) if is_act(x)), len(rest))
    writer_opener = rest.index(opener) if opener in rest else None
    # c1b/mmf2 (Derrick t1437s5374): a continued clip opens mid-act, so its 'At first' opener may itself be the act sentence
    mid_act = writer_opener is not None and writer_opener == act_at and bool(re.match(r"(?i)\s*At first\b", _D_RE.sub("", rest[writer_opener])))
    continued = bool(cast.get("continued"))
    if writer_opener is not None and (writer_opener < act_at or mid_act or continued):
        stands = [i for i, x in enumerate(rest[:act_at]) if _STAND_SENT_RE.search(_D_RE.sub("", x))]
        anchor = max([writer_opener] + stands)
        report["added"].append("writer opener kept (builder opener skipped)" + (" (opens mid-act)" if mid_act else "")
                               + (" (continued)" if continued else ""))
        strip_like = b_kind in ("tease", "strip") or cast.get("position") in ("tease", "strip")  # (1) Derrick t247s837
        extra = [wardrobe] if wardrobe and not strip_like else []
        rest = rest[:writer_opener + 1] + extra + rest[writer_opener + 1:]
        if not continued and not has_move and not mid_act:
            rest.insert(anchor + 1 + len(extra), beat)
    elif continued:
        # PM acc4 #1 / Derrick t251s854: never add the opening-from-still sentence or move-in beat on a continued run
        report["added"].append("continued: opening-from-still skipped")
        strip_like = b_kind in ("tease", "strip") or cast.get("position") in ("tease", "strip")
        extra = [wardrobe] if wardrobe and not strip_like else []
        rest = extra + rest
    else:
        if writer_opener is not None:
            rest.pop(writer_opener)  # exactly one opening: the writer's came after the act, the builder's goes first
            report["stripped"].append("writer opener after the act start dropped")
        if cast.get("dynamic_pose") and not cast.get("still_pose"):
            report["not_ready"] = "no writer opener and no pose fact in the still read"
        opening = f"The clip opens on <Picture 1>: <Subject 1> {cast['still_wardrobe']}."
        report["added"].append("opening-from-still sentence (R14/R16)")
        strip_like = b_kind in ("tease", "strip") or cast.get("position") in ("tease", "strip")
        rest = [opening] + ([wardrobe] if wardrobe and not strip_like else []) + ([] if has_move else [beat]) + rest
    if not continued and not has_move:
        report["added"].append("move-into-position beat (R16/R23a)")
    act_at = next((i for i, x in enumerate(rest) if is_act(x) and x not in (beat,)), len(rest))
    seq = [cam] + rest[:act_at] + [x for x in (motion, contact) if x] + rest[act_at:]
    if wardrobe and strip_like and wardrobe not in seq:  # (1): a strip's end-state wardrobe line follows the PRIMARY sentence
        pi = next((i for i, x in enumerate(seq) if "PRIMARY MOTION" in x), None)
        seq.insert(pi + 1 if pi is not None else len(seq), wardrobe)
    sound_all = convert_speech(clean(sound_q), voices, max_lines=max_lines, counts=counts, ledger=ledger, budget=budget) if sound_raw else []
    spoken = [c for c in sound_all if "<d>" in c]
    sound = [c for c in sound_all if "<d>" not in c][:3]
    seq = seq[:-1] + spoken + seq[-1:] if spoken and len(seq) > 1 else seq + spoken
    seq += sound
    detailed = "[Shot 1] " + " ".join(seq)
    detailed = re.sub(r"\s{2,}", " ", detailed)
    # silent-drop invariant: every input spoken line is either in the prompt or in the ledger with a reason
    out_lines = [re.sub(r"^\[English\]\s*", "", x.strip(), flags=re.I) for x in _D_RE.findall(detailed)]
    dropped = [e for e in ledger if not e["kept"]]
    report["speech"] = {"in": len(speech_in), "kept": len(out_lines), "dropped": dropped, "budget_words": budget}
    norm = lambda x: re.sub(r"[^\w]+", " ", x.replace("’", "'")).strip().lower()
    missing = [x for x in speech_in if norm(x) not in [norm(y) for y in out_lines] and norm(x) not in [norm(e["line"]) for e in dropped]]
    if len(speech_in) != len(out_lines) + len(dropped) or missing:
        raise WriterPromptError(f"silent drop: {len(speech_in)} spoken lines in, {len(out_lines)} kept, {len(dropped)} dropped "
                                f"with a reason; missing {missing[:3]}")
    shot_text: Dict[int, str] = {}
    for n, t, body_n in later_shots:  # B1: each later shot keeps its header, clock, camera sentence, lines and sounds
        units = convert_speech(clean(to_quote(body_n)), voices, max_lines=max_lines, counts=counts, ledger=ledger, budget=budget)
        txt = " ".join(units).strip()
        if not txt:
            raise WriterNotReady(f"NOT_READY: shot syntax: [Shot {n}] has no text left after cleaning")
        shot_text[n] = txt
        detailed += f" [Shot {n}] At {t}, " + txt[:1].lower() + txt[1:]
    # NB7: never leave <Subject N> tags in detailed_description prose.
    detailed = re.sub(r"<Subject ([123])>", r"(S\1)", detailed)
    detailed = re.sub(r"(?i)\bthe\s+the\b", "the", detailed)
    summary_src = (secs.get("summary") or [""])[0]
    summary_kept = [s for s in clean(re.sub(r"^\s*\[[^\]]+\]\s*", "", summary_src)) if "<d>" not in s][:2]
    summary_kept = [_PRON_COMMA_RE.sub(r"\1 ", _SUMMARY_STRIP_RE.sub("<Subject 1> takes off her clothes", x)) for x in summary_kept]
    # NB4: never ship raw act_ids in summary; use summary_act plus scenario and consent clause.
    _RAW_ACT_SUM_RE = re.compile(r"(?i)\b(?:standing_mf|ff_scissoring|ff_cunnilingus|prone_bone|mf_anal|male_solo|female_solo|mmf_double_blowjob)\b|\b(?:ffm|mmf)\s+clip\b")
    if summary_kept and not any(_RAW_ACT_SUM_RE.search(x) for x in summary_kept):
        summary = f"{TASK_TAG} " + " ".join(summary_kept)
    else:
        summary = f"{TASK_TAG} " + (cast.get("summary_act") or "")
    _scen_bits = [str(x).replace("_", " ") for x in ((cast.get("themes") or []) + (cast.get("look") or [])) if x]
    if cast.get("role") and str(cast["role"]).lower() not in summary.lower():
        _scen_bits.append(str(cast["role"]))
    for _sb in _scen_bits[:2]:
        if _sb.lower() not in summary.lower():
            summary = summary.rstrip(".") + f" ({_sb})."
    if (cast.get("states") or cast.get("themes") or cast.get("role")) and not re.search(r"(?i)\bconsent", summary):
        summary = summary.rstrip(".") + "; all characters are consenting adults."
    summary = re.sub(r"(?i)\bthe\s+the\b", "the", summary)
    _male_solo = (cast.get("s1_gender") == "man" or (cast.get("act_id") or cast.get("position")) == "male_solo")
    if _male_solo:
        subject_definitions_lines = [
            f"<Picture 1> is the start still of the setting only, and {_scene(cast)['setting']}, its light and the opening framing: {cast['still']}. It does not define <Subject 1>.",
            f"<Subject 1> is {cast.get('man') or 'an adult man, twenty-four years of age, of solid adult build'}; he is (S1). He is not the person shown in <Picture 1>, and that person is not in this clip.",
        ]
    else:
        subject_definitions_lines = [
            f"{R11_PICTURE}, and {_scene(cast)['setting']}, its light and the opening framing: {cast['still']}.",
            f"{R11_SUBJECT}; {cast['woman']}; she is (S1), and <Audio 1> defines her voice timbre.",
        ]
    off_s2 = bool(cast.get("off_still_s2"))
    off_s3 = bool(cast.get("off_still_s3")) and not cast.get("s3_in_frame")  # acc4: continued MMF, S3 is in the inherited frame
    is_3p_scene = cast.get("is_three_person") or cast.get("bodies", 2) >= 3
    if (pt == "man" or (is_3p_scene and pt == "faceless")) and cast.get("man") and (cast.get("s1_gender") != "man" and (cast.get("act_id") or cast.get("position")) != "male_solo"):
        extra = " He is not in <Picture 1>; he enters during the clip." if off_s2 else ""
        subject_definitions_lines.append(f"<Subject 2> is {cast['man']}; he is (S2).{extra}")
    elif pt in ("woman", "futa") and (cast.get("partner") or cast.get("man")):
        extra = " She is not in <Picture 1>; she enters during the clip." if off_s2 else ""
        subject_definitions_lines.append(f"<Subject 2> is {cast.get('partner') or cast['man']}; she is (S2).{extra}")
    elif pt == "non-human" and cast.get("man") and (cast.get("act_id") or cast.get("position")) != "male_solo":
        pr2 = "it" if "no face" in cast["man"] else "he"  # G1-G4: look text only, no RefMod
        extra = f" {pr2.capitalize()} is not in <Picture 1>; {pr2} enters during the clip." if off_s2 else ""
        subject_definitions_lines.append(f"<Subject 2> is {cast['man']}; {pr2} is (S2), the same creature for the whole clip.{extra}")
    if is_3p_scene:
        pt3 = str(cast.get("partner_type2") or "man").lower()
        desc3 = (
            (cast.get("partner3") or cast.get("man3") or "an adult woman, twenty-two years of age, of slender build")
            if pt3 in ("woman", "futa")
            else (cast.get("man3") or cast.get("partner3") or "an adult man, twenty-four years of age, of solid adult build")
        )
        pron3 = "she" if pt3 == "woman" else "he"
        extra3 = f" {pron3.capitalize()} is not in <Picture 1>; {pron3} enters during the clip." if off_s3 else ""
        if cast.get("s3_still"):  # MMF S3 reference still (wired as ref_images slot s3_picture)
            n3 = s3_picture(cast)
            look3 = re.sub(r"^an? adult (?:man|woman),?\s*", "", desc3)
            subject_definitions_lines.append(f"<Picture {n3}> is the reference image defining the exact visual appearance, identity, "
                                             f"face and hairstyle of <Subject 3>.")
            subject_definitions_lines.append(f"<Subject 3> is the exact same {'adult woman' if pt3 == 'woman' else 'adult man'} shown in "
                                             f"<Picture {n3}>, {look3}; {pron3} is (S3).{extra3}"
                                             + (f" {pron3.capitalize()} follows <Picture {n3}>." if off_s3 else ""))
        else:
            subject_definitions_lines.append(f"<Subject 3> is {desc3}; {pron3} is (S3).{extra3}")
    subject_definitions_lines.append(R11_HAND)
    subject_definitions = "\n".join(subject_definitions_lines)

    retention_lines = [
        (
            "<Subject 1> (appears in [Shot 1]): fully_preserved - his face, hairstyle, body and skin stay as defined in <Subject 1> in every phase"
            if (cast.get("s1_gender") == "man" or (cast.get("act_id") or cast.get("position")) == "male_solo")
            else "<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure are kept from <Picture 1> in every phase"
        ),
    ]
    if (pt in ("man", "woman", "futa") or (is_3p_scene and pt == "faceless")) and cast.get("man") and (cast.get("s1_gender") != "man" and (cast.get("act_id") or cast.get("position")) != "male_solo"):
        if off_s2:
            retention_lines.append(
                "<Subject 2> (enters during the clip): he is not in <Picture 1>; keep the look the writer named once he is in frame"
                if pt in ("man", "faceless") else
                "<Subject 2> (enters during the clip): she is not in <Picture 1>; keep the look the writer named once she is in frame"
            )
        else:
            retention_lines.append(
                "<Subject 2> (appears in [Shot 1]): fully_preserved - his face, build and skin stay the same man throughout"
                if pt in ("man", "faceless") else
                "<Subject 2> (appears in [Shot 1]): fully_preserved - her face, build and skin stay the same woman throughout"
            )
    elif pt == "non-human" and cast.get("man") and (cast.get("act_id") or cast.get("position")) != "male_solo":
        # G2: never 'the same man' for a creature; the look text is the only anchor (G4: no RefMod)
        retention_lines.append(
            "<Subject 2> (" + ("enters during the clip" if off_s2 else "appears in [Shot 1]") + "): fully_preserved - " +
            ("its form, size and texture stay the same throughout" if "no face" in cast["man"]
             else "his face, form, size and skin stay the same creature throughout, exactly as named in subject_definitions"))
    if is_3p_scene:
        pt3 = str(cast.get("partner_type2") or "man").lower()
        if cast.get("s3_still"):
            retention_lines.append(f"<Subject 3> ({'enters during the clip' if off_s3 else 'appears in [Shot 1]'}): fully_preserved - "
                                   f"{'her' if pt3 == 'woman' else 'his'} face, body and figure follow <Picture {s3_picture(cast)}>")
        elif off_s3:
            retention_lines.append(
                "<Subject 3> (enters during the clip): " +
                ("she is not in <Picture 1>; keep the look the writer named once she is in frame" if pt3 == "woman"
                 else "he is not in <Picture 1>; keep the look the writer named once he is in frame")
            )
        else:
            retention_lines.append(
                "<Subject 3> (appears in [Shot 1]): fully_preserved - " +
                ("her face, build and skin stay the same woman throughout" if pt3 == "woman" else "his face, build and skin stay the same man throughout")
            )
    retention_lines.extend([
        "<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - " + _scene(cast)["anchor"],
        (
            "<Audio 1> (voice of (S1)): attribute_transfer - his spoken lines take their voice timbre from <Audio 1>"
            if (cast.get("s1_gender") == "man" or (cast.get("act_id") or cast.get("position")) == "male_solo")
            else "<Audio 1> (voice of (S1)): attribute_transfer - her spoken lines take their voice timbre from <Audio 1>"
        ),
    ] + _garment_retention(cast, state))
    retention = "\n".join(retention_lines)
    retention = re.sub(r"(?i)\bthe\s+the\b", "the", retention)
    final = (f"subject_definitions:\n{subject_definitions}\n\nsummary:\n{summary}\n\n"
             f"retention_analysis:\n{retention}\n\ndetailed_description:\n{detailed}\n")
    _final_errs = lint_final_prompt(final)
    if _final_errs:
        report["final_lint"] = _final_errs
        if strict:
            report["not_ready"] = (report.get("not_ready", "") + "; " if report.get("not_ready") else "") + \
                "final lint: " + "; ".join(_final_errs)
    # dynsafe (brief item 2): one primary beat per short window. A real undress (not a pull-aside) plus the act in one
    # single-shot clip is packed: split it into two briefs or send it back; never compressed, never template-filled.
    # A nude or near-nude start still (no cover garments in the inventory) needs no undress beat and stays one clip.
    if cast.get("dynamic_pose"):
        has_cover = bool(cast.get("garments_off") or [g for g in _cast_items(cast) if g.get("off") or g.get("slot") in _COVER_SLOTS])
        undress_sents = list(state.get("undress_text", []))
        if has_cover and report.get("act_written") and (undress_sents or state.get("builder_removed") or cast.get("undress")):
            report["packed_beats"] = {
                "why": "one short clip packs two primary beats (undress and the act)",
                "split": [f"beat 1: she undresses from <Picture 1> ({'; '.join(x[:80] for x in undress_sents) or 'the ask names undress'}), "
                          "and the clothes land on a named surface and stay there",
                          f"beat 2 (continuation from beat 1's closing pose and wardrobe): {cast.get('ask') or 'the act'}"]}
            report["not_ready"] = (report.get("not_ready", "") + "; " if report.get("not_ready") else "") + \
                "packed beats - split into two briefs or send back to the writer"
    # frs16 S2 (Fleet Reviewer 2026-11-11): W5 on the finalized, post-strip state (not only the raw draft). This path has no
    # repair writer after finalize, so a garment that still covers the join at penetration is NOT_READY.
    if cast.get("undress") is False:
        covered = _w5_covered_garments(cast, state)
        if covered and cast.get("position") not in _ORAL_POSITIONS and cast.get("position") != "handjob" and _JOIN_PEN_RE.search(text_body):
            report["w5_final"] = {"covered": covered}
            report["not_ready"] = (report.get("not_ready", "") + "; " if report.get("not_ready") else "") + \
                "W5 " + _LINT_CODES["W5"].format(items=" and ".join(covered)) + " (finalized state, unrepaired)"
    # oralfoley: flags / NOT_READY only, on the final ordered units (the writer's own lines, nothing rewritten)
    checks = audio_act_checks(seq, cast, bool(report.get("act_written")))
    report["audio_checks"] = checks
    report.setdefault("warnings", [])
    for c in checks:
        if c["hard"] and c["code"] in _STYLE_WARN_CODES:
            report["warnings"].append(f"{c['code']} {c['why']}")
            report["flags"].append({"code": c["code"], "why": c["why"]})
        elif c["hard"]:
            report["not_ready"] = (report.get("not_ready", "") + "; " if report.get("not_ready") else "") + f"{c['code']} {c['why']}"
        else:
            report["flags"].append({"code": c["code"], "why": c["why"]})
    addenda_resolved = {
        "act_id": cast.get("act_id") or cast.get("position"),
        "partner_type": pt,
        "states": cast.get("states") or [],
        "look": cast.get("look") or [],
        "register": cast.get("register") or [],
        "offscreen_voice": bool(cast.get("offscreen_voice")),
        "s1_gender": cast.get("s1_gender"),
        "body_count": cast.get("bodies"),
        "sleeper_gender": cast.get("sleeper_gender"),
        "flags": list(cast.get("addenda_flags") or []),
    }
    sleeper_sn = None
    if {"sleeping", "already_out"} & set(addenda_resolved["states"]):
        sleeper_sn = "S2" if addenda_resolved.get("sleeper_gender") == "man" else "S1"
        if (cast.get("act_id") or cast.get("position")) == "male_solo":
            sleeper_sn = "S1"
    addenda_checks = scene_addenda.check_prompt(
        final, addenda_resolved, ask=cast.get("ask") or "", still_read=cast.get("still_read"),
        sleeper_sn=sleeper_sn, request_fields=cast.get("request_fields"),
    )
    report["addenda_checks"] = addenda_checks
    for c in addenda_checks:
        if c["hard"]:
            report["not_ready"] = (report.get("not_ready", "") + "; " if report.get("not_ready") else "") + f"{c['code']} {c['why']}"
        else:
            report["flags"].append({"code": c["code"], "why": c["why"]})
    if re.search(r"(?i)\bno speech\b", desc_raw + " " + sound_raw) and not any(c["code"] == "D3" for c in checks):
        report["flags"].append({"code": "D3", "why": "the draft wrote 'no speech'; the existing negation cleanup kept it out of the "
                                                     "prompt - leave silence unwritten"})
    if sound_raw:
        report["flags"].append({"code": "S6", "why": "labeled overall_soundscape / sound header in the draft; body sound belongs as one to "
                                                     "three plain diegetic sentences at the end of the shot (the header label is not used)"})
    if any(k in _MUSIC_HEADERS for k in secs):
        report["flags"].append({"code": "M6", "why": "non_diegetic_music header in the draft; score would bury the body sounds"})
    if _MUSIC_RE.search(desc_raw) and not _MUSIC_RE.search(cast.get("ask") or ""):
        report["flags"].append({"code": "M7", "why": "unrequested music / score in the description would bury the body sounds"})
    report["skin_unrequested"] = list(_CTX.get("skin_flags", []))
    report["flags"] += list(_CTX.get("camera_flags", []))
    if cast.get("still_read") is not None and not cast.get("inventory"):
        report["flags"].append({"code": "wardrobe_unverified", "why": "the still read lists no garments; writer's nouns kept"})
    if cast.get("dynamic_pose") and not cast.get("still_pose"):
        report["flags"].append({"code": "pose_unverified", "why": "the still read has no pose; writer's opener kept"})
    issues = check_writer_consistency(detailed)
    if report.get("not_ready"):
        issues.append("NOT_READY: " + report["not_ready"])
    off_s2 = bool(cast.get("off_still_s2"))
    off_s3 = bool(cast.get("off_still_s3")) and not cast.get("s3_in_frame")  # acc4: continued MMF, S3 is in the inherited frame
    if off_s2 and not writer_defined_missing_person(raw, subject=2):
        issues.append(
            "NOT_READY: the start still does not show the partner; the writer must define how they look, "
            "what they are wearing, and how they enter"
        )
        report["off_still_undefined"] = True
    if off_s3 and not writer_defined_missing_person(raw, subject=3):
        issues.append(
            "NOT_READY: the start still does not show the third person; the writer must define how they look, "
            "what they are wearing, and how they enter"
        )
        report["off_still_undefined"] = True
    if _MINOR_RE.search(final):
        issues.append("NOT_READY: minor descriptor in the prompt")
    left = [w for w in ("then", "afterwards", "after", "next") if re.search(rf"\b{w}\b", _D_RE.sub("", final), re.I)]
    if left:
        issues.append("transition word left: " + ", ".join(left))
    if re.search(r"[\"“”]", _D_RE.sub("", detailed)):
        issues.append("quoted speech left outside <d>")
    for u in _sentences(detailed):
        if _DOUBLE_LEAD_RE.search(u):
            issues.append("double speech lead: " + u[:80])
        if not cast.get("index_voice") and re.search(r"(?i)signature vocal timbre", u):
            issues.append("INDEX voice wording on an OC cast: " + u[:80])
    report["warnings"] += [i for i in issues if i.startswith(_STYLE_WARN_PREFIXES)]
    issues = [i for i in issues if not i.startswith(_STYLE_WARN_PREFIXES)]
    report["issues"] = issues
    if strict and issues:
        raise WriterPromptError("writer prompt failed the consistency gate: " + "; ".join(issues))
    if shot_text:  # B1: retention names every shot a subject appears in
        def _appears(m: "re.Match[str]") -> str:
            k = int(m.group(1))
            ns = [1] + [n for n, x in sorted(shot_text.items())
                        if re.search(rf"\(S{k}\)|<Subject {k}>" + (r"|\b(?:she|her)\b" if k == 1 else ""), x)]
            return f"<Subject {k}> (appears in " + ", ".join(f"[Shot {n}]" for n in ns) + ")"
        final = re.sub(r"<Subject (\d)> \(appears in \[Shot 1\]\)", _appears, final)
    return final, report


# --- lint + targeted repair loop (Self-Refine / VPO style; the deterministic lint is the judge) -------------------------
REPAIR_TEMPLATE = (
    "Rewrite ONLY the numbered sentences below from your detailed_description. Each has the problem named under it. "
    "Fix only that problem; keep the people, the position, the act and any <d> line word for word. "
    "Reply with one line per sentence in the form [n] new sentence, and nothing else.\n\n{items}")
_LINT_CODES = {"P1": "the pose goes back to standing after she has moved toward the bed; keep her in the pose she has reached",
               "C1": "the leg position changes inside one clip; keep one leg position for the whole clip",
               "C2": "the facing direction changes inside one clip; keep one facing direction",
               "C3": "the bodies are on the floor and on the bed; keep them on one surface, {surface}, as the start image shows",
               "X1": "this body contact contradicts the position; describe contact the position allows",
               "K1": ("a tracking shot follows a moving subject and this act is stationary; use an arc with small amplitude at slow "
                      "speed or a static hold, keeping her face and the join in frame"),
               "K2": "end the pull-out at a medium shot that keeps the join and her face",
               "O1": "the opening pose contradicts <Picture 1>; open on <Picture 1>: she {pose}",
               "W5": "her {items} still covers the join here; she pulls it aside or takes it off before he enters her",
               "W6": "name the surface the removed garment lands on and that it stays there"}


def _desc_span(raw: str) -> Tuple[int, int]:
    m = re.search(r"(?im)^\s*(?:#+\s*|\*\*)?detailed_description\s*(?:\*\*)?\s*:\s*", raw or "")
    start = m.end() if m else 0
    nxt = None
    for mm in _SECTION_RE.finditer(raw or ""):
        if mm.start() > start:
            nxt = mm.start()
            break
    return start, nxt if nxt is not None else len(raw or "")


def lint_writer_prompt(raw: str, cast: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Issues the builder cannot repair deterministically, each tied to a raw detailed_description sentence index."""
    global _ABSENT_GARMENT_RE
    _ABSENT_GARMENT_RE = re.compile(cast["absent_garments"], re.I) if cast.get("absent_garments") else None
    _set_ctx(cast)
    a, b = _desc_span(raw)
    prot, spans = _protect_d(raw[a:b])
    units = [_restore_d(s, spans) for s in _sentences(prot)]
    issues: List[Dict[str, Any]] = []
    _, lint_state, viol = track_state(units, cast, repair=False)
    for v in viol:
        if v["code"] == "P1":
            issues.append({"code": "P1", "idx": v["idx"], "text": units[v["idx"]], "why": _LINT_CODES["P1"]})
    groups = [("C1", _LEG_CATEGORIES), ("C2", _FACING)]
    for code, cats in groups:
        hits = {k: [i for i, u in enumerate(units) if rx.search(_D_RE.sub("", u))] for k, rx in cats.items()}
        hits = {k: v for k, v in hits.items() if v}
        if len(hits) > 1:
            main = max(hits, key=lambda k: len(hits[k]))
            for k, idxs in hits.items():
                if k != main:
                    issues += [{"code": code, "idx": i, "text": units[i], "why": _LINT_CODES[code] + f" ({main})"} for i in idxs]
    sc = _scene(cast)
    if sc["bed"] is False:  # stillfacts: no bed in the still -> bed / mattress / sheets are the conflict (None = unknown)
        issues += [{"code": "C3", "idx": i, "text": u, "why": f"there is no bed in the start image; keep them on {sc['surface']}"}
                   for i, u in enumerate(units) if re.search(r"\b(bed|mattress|sheets?)\b", _D_RE.sub("", u), re.I)]
    elif any(re.search(r"\b(bed|mattress|sheets?)\b", u, re.I) for u in units):
        issues += [{"code": "C3", "idx": i, "text": u, "why": _LINT_CODES["C3"].format(surface=sc["surface"])}
                   for i, u in enumerate(units) if _FLOOR_BODY_RE.search(_D_RE.sub("", u))]
    if cast.get("position") == "doggy":
        issues += [{"code": "X1", "idx": i, "text": u, "why": _LINT_CODES["X1"] + " (hands and knees)"} for i, u in enumerate(units)
                   if _PUBIC_RE.search(u)]
    # dynsafe lint (sent to the writer repair loop, never rewritten by the builder): K1 track on a stationary act, K2
    # pull-out ending wide during the act, O1 opener pose contradicts the still, W5 a garment still covers the join
    pos = cast.get("position")
    for i, u in enumerate(units):
        pu = _D_RE.sub("", u)
        if "<d>" in u or not _CAMERA_SENTENCE_RE.search(pu):
            continue
        cl = _cam_classes(pu)
        if cl and cl[0] == "tracking" and pos in _STILL_ACTS:
            issues.append({"code": "K1", "idx": i, "text": u, "why": _LINT_CODES["K1"]})
        if cl and cl[0] == "pull out" and pos in _STILL_ACTS:
            mv = _CAM_CLASS[1][1].search(pu)
            if mv and _WIDE_END_RE.search(pu[mv.end():]):
                issues.append({"code": "K2", "idx": i, "text": u, "why": _LINT_CODES["K2"]})
    still_kind = _pose_kind(cast.get("still_pose") or "")
    if still_kind:
        op = next(((i, u) for i, u in enumerate(units) if _OPENER_RE.search(_normalize_labels(_D_RE.sub("", u)))), None)
        if op:
            wk = _pose_kind(_D_RE.sub("", op[1]))
            still_kinds = {_pose_kind(m.group(0)) for m in re.finditer(r"(?i)\b(?:stand|kneel|sit|lie|lies|lying|lean|crouch)\w*", cast["still_pose"])}
            if wk and wk not in still_kinds and not {wk, still_kind} <= {"stand", "lean"}:
                issues.append({"code": "O1", "idx": op[0], "text": op[1],
                               "why": _LINT_CODES["O1"].format(pose=re.sub(r"(?i)^she\s+", "", cast["still_pose"]))})
    for v_i, u in enumerate(units):
        pu = _D_RE.sub("", u)
        if _REMOVE_VERB_RE.search(pu) and not _not_an_undress_beat(pu) and any(
                re.search(g["rx"], pu, re.I) for g in _cast_items(cast)):
            nxt = _D_RE.sub("", units[v_i + 1]) if v_i + 1 < len(units) else ""
            if not (_PLACE_RE.search(pu) or re.search(r"(?i)\b(?:on|onto) the\b", nxt)):
                issues.append({"code": "W6", "idx": v_i, "text": u, "why": _LINT_CODES["W6"]})
    for c in audio_act_checks([_QUOTE_RE.sub(lambda m: f"<d>[English] {m.group(1).strip()}</d>", u) for u in units], cast,
                              bool(lint_state.get("act") or _ORAL_ACT_RE.search(" ".join(units)))):
        if c["code"] != "A1" and units:
            k = c["idx"] if c["idx"] is not None else len(units) - 1  # R1 with no PRIMARY MOTION: the writer adds it at the end
            issues.append({"code": c["code"], "idx": k, "text": units[k], "why": c["why"]})
    if cast.get("undress") is False:
        covered = _w5_covered_garments(cast, lint_state)
        pen = next((i for i, u in enumerate(units) if _PENETRATION_RE.search(_D_RE.sub("", u))), None)
        if (cast.get("position") in _ORAL_POSITIONS or cast.get("position") == "handjob" or
                (cast.get("position") in _NOPEN_POSITIONS and not any(
                _JOIN_PEN_RE.search(_D_RE.sub("", u)) for u in units))):
            covered = []  # #7
        if covered and pen is not None:
            issues.append({"code": "W5", "idx": pen, "text": units[pen],
                           "why": _LINT_CODES["W5"].format(items=" and ".join(covered))})
    seen, uniq = set(), []
    for it in sorted(issues, key=lambda x: x["idx"]):
        if it["idx"] not in seen:
            seen.add(it["idx"])
            uniq.append(it)
    return uniq, units


def repair_writer_output(raw: str, cast: Dict[str, Any], writer: Callable[[str], str], max_rounds: int = 2
                         ) -> Tuple[str, Dict[str, Any]]:
    """Send the writer only the broken sentences plus the reason, up to max_rounds; splice the rewrites in and keep
    every other sentence byte-identical (a reply that changes an unflagged sentence is rejected)."""
    log: Dict[str, Any] = {"rounds": [], "remaining": []}
    for rnd in range(1, max_rounds + 1):
        issues, units = lint_writer_prompt(raw, cast)
        if not issues:
            break
        items = "\n".join(f"[{it['idx']}] {it['text']}\nProblem: {it['why']}" for it in issues)
        reply = writer(REPAIR_TEMPLATE.format(items=items)) or ""
        want = {it["idx"] for it in issues}
        new = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"(?m)^\s*\[(\d+)\]\s*(.+?)\s*$", reply)}
        extra = sorted(set(new) - want)
        got = {i: t for i, t in new.items() if i in want and t}
        entry = {"round": rnd, "asked": sorted(want), "got": sorted(got), "ignored_unflagged": extra, "accepted": False}
        if got:
            a, b = _desc_span(raw)
            desc = raw[a:b]
            pos = 0
            pieces = []
            for i, u in enumerate(units):
                j = desc.find(u, pos) if u in desc[pos:] else -1
                if j < 0:
                    pieces = None
                    break
                pieces.append(desc[pos:j])
                pieces.append(got.get(i, u))
                pos = j + len(u)
            if pieces is not None:
                new_desc = "".join(pieces) + desc[pos:]
                new_raw = raw[:a] + new_desc + raw[b:]
                _, new_units = lint_writer_prompt(new_raw, cast)
                old_keep = [u for i, u in enumerate(units) if i not in got]
                if all(u in new_units for u in old_keep):
                    raw = new_raw
                    entry["accepted"] = True
                else:
                    entry["reject"] = "an unflagged sentence changed"
            else:
                entry["reject"] = "could not locate the sentences in the raw text"
        log["rounds"].append(entry)
    log["remaining"] = [{k: v for k, v in it.items() if k != "text"} for it in lint_writer_prompt(raw, cast)[0]]
    return raw, log


def comm_writer(system: str, **kw: Any) -> Callable[[str], str]:
    """The existing writer call path (comm.llm, GPU-lock gated) as a repair-loop writer."""
    assert_writer_system_prompt(system)
    return lambda user: comm.llm(system, user, **kw)


# --- stillfacts fix 1 (Prompt maker #1): refusal gate + one retry; a refusal never becomes a prompt -------------------
class WriterRefusal(WriterPromptError):
    """The writer refused or wrote no prompt; the clip is NOT_READY."""


_REFUSAL_RE = re.compile(
    r"\bI\s+(?:can(?:'|\u2019|no)?t|cannot|won(?:'|\u2019)t|will not)\s+write\b|\bI(?:'|\u2019)m not able to\b|\bI am not able to\b"
    r"|\bunable to (?:write|generate|create|produce|provide|help|comply|do that|fulfil\w*)\b|\bnon-explicit version\b|\blet me know which\b",
    re.I)
_ACT_ASK_RE = re.compile(r"\b(?:sex|fuck\w*|missionary|doggy\w*|cowgirl|blow ?job|bj|oral|suck\w*|deepthroat\w*|penetrat\w*"
                         r"|rides? him|position|threesome|three[- ]?way|mmf|ffm)\b", re.I)
_NEGATED_ACT_RE = re.compile(
    r"\b(?:no|without|never|zero|not?|non[- ])\s*(?:sex|penetrat\w*|fuck\w*|intercourse|oral|blow ?job)\b",
    re.I)


def is_act_ask(ask: Optional[str]) -> bool:
    """True when the user brief asks for a sex act ('no sex' is not a sex ask)."""
    if not ask:
        return False
    cleaned = _NEGATED_ACT_RE.sub("", str(ask))
    return bool(_ACT_ASK_RE.search(cleaned))
_DESC_HEAD_RE = re.compile(r"(?im)^\s*(?:#+\s*|\*\*)?(?:detailed_description|integrated_multimodal_description)\s*(?:\*\*)?\s*:")
MIN_WRITER_TOKENS = 400


def writer_gate(raw: str, cast: Optional[Dict[str, Any]] = None, completion_tokens: Optional[int] = None,
                ask: Optional[str] = None) -> List[str]:
    """Reasons the writer output is not a prompt ([] = pass): a refusal phrase (outside <d> lines), no
    detailed_description / integrated_multimodal_description, fewer than 400 completion tokens (when known), or
    act:false after the build when the ask names an act (needs cast)."""
    reasons: List[str] = []
    plain = _D_RE.sub("", raw or "")
    m = _REFUSAL_RE.search(plain)
    if m:
        reasons.append(f"refusal phrase: {m.group(0)!r}")
    if not _DESC_HEAD_RE.search(raw or ""):
        reasons.append("missing detailed_description / integrated_multimodal_description")
    if completion_tokens is not None and completion_tokens < MIN_WRITER_TOKENS:
        reasons.append(f"only {completion_tokens} completion tokens (< {MIN_WRITER_TOKENS})")
    ask = ask if ask is not None else (cast or {}).get("ask")
    if cast is not None and ask and is_act_ask(ask) and not reasons:
        try:
            _, rep = finalize_writer_prompt(raw, dict(cast), strict=False)
            if not rep.get("act_written", (rep.get("state") or {}).get("act")):
                reasons.append("act:false although the ask names an act")
        except WriterPromptError as e:
            reasons.append(f"builder could not finalize: {e}")
    return reasons


def gated_write(write: Callable[[], Any], cast: Optional[Dict[str, Any]] = None, ask: Optional[str] = None,
                retries: int = 1) -> Tuple[Optional[str], Dict[str, Any]]:
    """Call write() (returns raw, or (raw, completion_tokens)); on a gate hit retry once. Returns (raw, log), or
    (None, log) with log['status'] == 'NOT_READY' after the second failure. Drivers call this around the writer."""
    log: Dict[str, Any] = {"status": None, "attempts": []}
    for n in range(retries + 1):
        out = write()
        raw, ct = out if isinstance(out, tuple) else (out, None)
        reasons = writer_gate(raw, cast, completion_tokens=ct, ask=ask)
        log["attempts"].append({"n": n + 1, "reasons": reasons, "completion_tokens": ct, "chars": len(raw or "")})
        if not reasons:
            log["status"] = "OK"
            return raw, log
    log["status"] = "NOT_READY"
    return None, log


def build_writer_request(base_graph: Dict[str, Any], raw: str, cast: Dict[str, Any], prefix: str,
                         seed: int = 51083601, frames: int = SINGLE_CLIP_MAX_FRAMES,
                         width: int = DEFAULT_CANVAS[0], height: int = DEFAULT_CANVAS[1],
                         strict: bool = True, writer: Optional[Callable[[str], str]] = None,
                         writer_system: Optional[str] = None, repair_rounds: int = 2
                         ) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """Embed a finalized writer prompt into a copy of an existing OC RefMod graph (c0 prompt, seed, size, prefix).
    With writer (a callable) or writer_system (uses comm.llm), lint issues go back to the writer first (max 2 rounds)."""
    hard = writer_gate(raw)  # stillfacts fix 1: a refusal / no description is NOT_READY, never a prompt
    if hard:
        raise WriterRefusal("NOT_READY: " + "; ".join(hard))
    if not cast.get("still_read"):  # dynsafe (limits 3 + 5): no still facts = NOT_READY, never a bedroom fallback
        raise WriterNotReady("NOT_READY: no still read (vision facts) for <Picture 1>; the builder has no bedroom fallback")
    validate_hook_ask(cast.get("position", ""), cast.get("ask", ""))
    if "states" not in cast or "offscreen_voice" not in cast:
        _br = scene_addenda.resolve_brief(
            cast.get("ask") or "", act_id=cast.get("act_id") or cast.get("position"),
            registry=load_acts_registry(), partner_type=cast.get("partner_type"),
        )
        if _br.get("not_ready"):
            raise WriterNotReady("NOT_READY: " + _br["not_ready"])
        if _br.get("partner_type") and not cast.get("partner_type"):
            cast["partner_type"] = _br["partner_type"]
        cast.setdefault("states", list(_br.get("states") or []))
        cast.setdefault("look", list(_br.get("look") or []))
        cast.setdefault("register", list(_br.get("register") or []))
        cast.setdefault("offscreen_voice", bool(_br.get("offscreen_voice")))
        cast.setdefault("s1_gender", _br.get("s1_gender"))
        cast.setdefault("sleeper_gender", _br.get("sleeper_gender"))
        cast.setdefault("addenda_flags", list(_br.get("flags") or []))
        cast.setdefault("look_line", scene_addenda.look_line(_br))
    repair_log = None
    if writer is None and writer_system:
        assert_writer_system_prompt(writer_system)
        writer = comm_writer(writer_system)
    if writer is not None:
        raw, repair_log = repair_writer_output(raw, cast, writer, max_rounds=repair_rounds)
        unfixed = [it for it in repair_log["remaining"] if it["code"] in ("C1", "C2", "C3")]
        if unfixed:
            raise WriterNotReady(f"NOT_READY: conflicts still unfixed after {repair_rounds} writer-repair rounds: " +
                                 "; ".join(f"{it['code']} {it.get('why', '')}" for it in unfixed))
    cast = dict(cast, clip_seconds=cast.get("clip_seconds", validate_single_clip_frames(frames) / 24.0))
    prompt, report = finalize_writer_prompt(raw, cast, strict=strict)
    if cast.get("ask") and is_act_ask(cast["ask"]) and not report.get("act_written"):
        raise WriterNotReady("NOT_READY: act:false although the ask names an act")
    if repair_log is not None:
        report["repair"] = repair_log
    report["lint"] = [{k: v for k, v in it.items() if k != "text"} for it in lint_writer_prompt(raw, cast)[0]]
    g = copy.deepcopy(base_graph)
    g["c0"]["inputs"].update({"prompt": prompt.strip(), "length": validate_single_clip_frames(frames),
                              "width": width, "height": height})
    g["noise"]["inputs"]["noise_seed"] = seed
    g["save"]["inputs"]["filename_prefix"] = prefix
    if cast.get("s3_still"):  # Max Architect 3, Derrick t1440 (MMF S3, 2026-11-13): S3 reference still on c0 (multiref_test_20261113 wiring)
        if "img_1" not in g:
            raise WriterNotReady("NOT_READY: an S3 reference still needs img_1 (<Picture 1>) wired first")
        g["img_s3"] = {"class_type": "LoadImage", "inputs": {"image": str(cast["s3_still"])}, "_meta": {"title": "S3 reference still"}}
        g["c0"]["inputs"]["ref_images.ref_image_1"] = ["img_1", 0]
        _wired = [int(k.rsplit("_", 1)[1]) for k in g["c0"]["inputs"] if re.fullmatch(r"ref_images\.ref_image_\d+", k)]
        if max(_wired) + 1 != s3_picture(cast):  # (4): the prompt's <Picture N> must be the next wired slot
            raise WriterNotReady(f"NOT_READY: S3 still would be ref slot {max(_wired) + 1}, prompt says <Picture {s3_picture(cast)}>")
        g["c0"]["inputs"][f"ref_images.ref_image_{s3_picture(cast)}"] = ["img_s3", 0]
        report["s3_still"] = {"image": str(cast["s3_still"]), "picture": s3_picture(cast)}
    # RefMod handling: 3-person and partner_type checks
    req_bodies = cast.get("bodies", 3 if _THREE_BODY_ASK_RE.search(f"{cast.get('position', '')} {cast.get('ask', '')}") else 2)
    is_3p = req_bodies >= 3 or bool(_THREE_BODY_ASK_RE.search(f"{cast.get('position', '')} {cast.get('ask', '')}"))
    if "refmods" in g and "inputs" in g["refmods"]:
        inputs = g["refmods"]["inputs"]
        if is_3p:
            pt2 = str(cast.get("partner_type") or "man").lower()
            pt3 = str(cast.get("partner_type2") or "faceless").lower()
            if cast.get("s3_still") and pt3 in ("man", "woman", "faceless", ""):
                pt3 = "still"  # (5) a still-S3 face rides on its <Picture N>, not a RefMod
            # Derrick t1440 / t1467: generated look or no still -> faceless fallback. Generic man/woman
            # partners are not named-face RefMod subjects unless the caller listed named_faces.
            if not cast.get("named_faces"):
                if pt2 in ("man", "woman"):
                    pt2 = "faceless"
                if pt3 in ("man", "woman"):
                    pt3 = "faceless"
            named_faces = ["S1"]
            if pt2 not in ("none", "non-human", "faceless"):
                named_faces.append("S2")
            if pt3 not in ("none", "non-human", "faceless", "still"):
                named_faces.append("S3")
            if cast.get("named_faces"):
                named_faces = list(cast["named_faces"])
            if len(named_faces) > 8:
                raise WriterNotReady(f"NOT_READY: more named faces ({len(named_faces)}) than 8 RefMod slots")
            live_mods = [inputs[f"mod_{i}"] for i in range(1, 9) if inputs.get(f"mod_{i}") and inputs[f"mod_{i}"] != "(none)"]
            if refmod_people(live_mods) < len(named_faces):  # (3) Derrick t247s837: people, not audio+visual slots
                raise WriterNotReady("NOT_READY: named-face person has no RefMod and was not marked non-human or faceless")
            for i in range(1, 9):
                k = f"mod_{i}"
                if i <= len(named_faces):
                    inputs[k] = live_mods[i - 1]
                else:
                    inputs[k] = "(none)"
        else:
            pt = str(cast.get("partner_type") or "man").lower()
            if pt in ("none", "non-human", "faceless"):
                for i in range(2, 9):
                    k = f"mod_{i}"
                    if k in inputs:
                        inputs[k] = "(none)"
    return g, prompt, report


# --- argon-low Section B: writer hook automatic 2-beat native continuation for packed undress-plus-act ----------------
DEFAULT_WRITER_UNDRESS_FRAMES = 124
DEFAULT_WRITER_ACT_EXT_FRAMES = 187


def size_undress_beat_frames(cast: Optional[Dict[str, Any]] = None, state: Optional[Dict[str, Any]] = None,
                             garment_count: Optional[int] = None, lying_down: Optional[bool] = None,
                             nude_still: Optional[bool] = None, requested_frames: Optional[int] = None) -> int:
    """Size beat 1 (undress) on the H3 grid (<= 243f): 0 for a nude/near-nude still, 124f floor for 1 standing
    garment, or sized up (192f/243f) when 2+ garments / lying-down removal or explicit beat1_frames are given."""
    c = cast or {}
    st = state or {}
    if nude_still is True:
        return 0
    if nude_still is None and c:
        has_cover = bool(c.get("garments_off") or [g for g in _cast_items(c) if g.get("off") or g.get("slot") in _COVER_SLOTS])
        if not has_cover and c.get("still_read") is not None:
            return 0
    req = requested_frames or c.get("undress_frames") or c.get("beat1_frames")
    if req is not None:
        return validate_single_clip_frames(int(req))
    if lying_down is None and c:
        lying_down = (_pose_kind(c.get("still_pose") or "") == "lie" or
                      bool(re.search(r"\b(?:lying|lies\s+back|on\s+her\s+back)\b", " ".join(st.get("undress_text", [])), re.I)))
    if garment_count is not None:
        if garment_count <= 0:
            return 0
        if garment_count >= 3:
            return SINGLE_CLIP_MAX_FRAMES
        if garment_count == 2 or lying_down:
            return 192
        return DEFAULT_WRITER_UNDRESS_FRAMES
    removed = list(st.get("writer_removed") or st.get("builder_removed") or [])
    if len(removed) >= 3:
        return SINGLE_CLIP_MAX_FRAMES
    if lying_down:
        return 192
    if c.get("size_undress_by_garments") and len(removed) >= 2:
        return 192
    return DEFAULT_WRITER_UNDRESS_FRAMES


def packed_split_is_safe(report: Dict[str, Any]) -> bool:
    """True when the ONLY consistency-gate reason in `report` is 'packed beats' and the split briefs are complete."""
    pb = report.get("packed_beats")
    if not pb or not isinstance(pb.get("split"), list) or len(pb["split"]) < 2:
        return False
    if not all(isinstance(s, str) and s.strip() for s in pb["split"][:2]):
        return False
    if not report.get("act_written"):
        return False
    st = report.get("state") or {}
    if not (st.get("undress_text") or st.get("writer_removed") or st.get("builder_removed")):
        return False
    if report.get("w5_final"):
        return False
    if any(c.get("hard") for c in report.get("audio_checks", [])):
        return False
    other_issues = [
        i for i in report.get("issues", [])
        if i != "NOT_READY: packed beats - split into two briefs or send back to the writer"
    ]
    return not other_issues


def build_writer_continuation_request(
    base_graph: Dict[str, Any],
    raw: str,
    cast: Dict[str, Any],
    prefix: str,
    seed: int = 51083601,
    base_frames: Optional[int] = None,
    extension_frames: int = DEFAULT_WRITER_ACT_EXT_FRAMES,
    overlap_frames: int = CONTINUATION_OVERLAP_FRAMES,
    width: int = DEFAULT_CANVAS[0],
    height: int = DEFAULT_CANVAS[1],
    drep: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """Build ONE 2-beat native latent-tail continuation graph from a packed undress-plus-act writer draft.

    Beat 1 (undress, default 124f or sized on H3 grid <= 243f) carries the start still at frame 0 via AddGuide.
    Beat 2 (act, default +187f extension, 311f total visible) continues from beat 1's sampled latent tail, opens
    already bare per R12 without restating removed clothes as worn, and re-applies the shared RefMods.
    """
    if drep is None:
        _, drep = finalize_writer_prompt(raw, dict(cast), strict=False)
    if not packed_split_is_safe(drep):
        raise WriterPromptError("packed beats split is incomplete or unsafe: " + "; ".join(drep.get("issues", [])))
    state = drep.get("state") or {}
    b1_frames = validate_single_clip_frames(base_frames) if base_frames is not None else size_undress_beat_frames(cast, state)
    layout = continuation_layout(b1_frames, int(extension_frames), int(overlap_frames))

    # Build Beat 1 (undress from <Picture 1> to bare/end-state wardrobe on the named surface)
    undress_sents = list(state.get("undress_text") or [])
    cast1 = dict(
        cast,
        dynamic_pose=False,
        undress=True,
        position="undress",
        position_beat="",
        primary_motion="",
        contact="",
        summary_act=f"<Subject 1> takes off the {cast.get('garments_off') or 'clothes'} and leaves them on {cast.get('garments_floor') or cast.get('surface')}.",
        clip_seconds=b1_frames / float(H3_FPS),
    )
    b1_desc = (
        "detailed_description:\n[Shot 1] The camera holds a static medium shot at hip height, "
        f"{cast['camera_tail']}. The clip opens on <Picture 1>: <Subject 1> {cast['still_wardrobe']}. "
        + (" ".join(undress_sents) if undress_sents else wardrobe_line(cast, state))
    )
    prompt1, rep1 = finalize_writer_prompt(b1_desc, cast1, strict=False)

    # Build Beat 2 (continuation from beat 1's closing pose and bare wardrobe: opens already bare, no start photo)
    prompt2_full, _ = finalize_writer_prompt(raw, dict(cast, clip_seconds=layout["window_frames"] / float(H3_FPS)), strict=False)
    closer = {
        "pose": f"she stands beside {cast.get('surface') or 'the surface'} after undressing",
        "wardrobe": (f"she is bare except for the {cast['garments_stay']} and the {cast.get('garments_off') or 'clothes'} "
                     f"she took off stay on {cast.get('garments_floor') or cast.get('surface')}"
                     if cast.get("garments_stay") else
                     f"she is completely bare and the {cast.get('garments_off') or 'clothes'} she took off stay on "
                     f"{cast.get('garments_floor') or cast.get('surface')}"),
    }
    stay_clause = f"Her {cast['garments_stay']} stay on her body" if cast.get("garments_stay") else "She is completely bare"
    off_clause = (f"the {cast['garments_off']} she took off in the previous beat stay on {cast.get('garments_floor') or cast.get('surface')}"
                  if cast.get("garments_off") else "her removed clothes stay where they fell")
    his = (cast.get("his_clothes") or "").strip()
    bare_wardrobe = f"{stay_clause}, and {off_clause}" + (f"; {his}." if his else ".")

    # Strip Beat 1's still-opening and garment-removal sentences from Beat 2 so Beat 2 opens already bare (R12/A.3)
    secs2 = split_writer_sections(prompt2_full)
    desc2 = (secs2.get("detailed_description") or [""])[0].strip()
    desc2_body = re.sub(r"^\s*\[Shot\s*1\]\s*", "", desc2)
    prot2, spans2 = _protect_d(desc2_body)
    b2_units = [_restore_d(s, spans2) for s in _sentences(prot2)]
    b2_kept: List[str] = []
    for u in b2_units:
        pu = _D_RE.sub("", u)
        if _OPENER_RE.search(_normalize_labels(pu)):
            continue
        if _REMOVE_VERB_RE.search(pu) and not _ASIDE_RE.search(pu) and not re.search(r"(?i)<Subject 2>|\bhe\b", pu):
            continue
        if "she took off" in pu.lower() and "<subject 2>" in pu.lower():
            b2_kept.append(bare_wardrobe)
            continue
        b2_kept.append(u)
    if bare_wardrobe not in b2_kept:
        b2_kept.insert(1 if b2_kept else 0, bare_wardrobe)
    lead2 = continuation_scene(
        " ".join(b2_kept), "she", closer=closer,
        camera=b2_kept[0] if b2_kept and _CAMERA_SENTENCE_RE.search(_D_RE.sub("", b2_kept[0])) else None,
    )
    subj2 = "\n".join([
        f"<Subject 1> is the exact same woman from beat 1, preserving her face, hairstyle, body, skin and figure with complete fidelity; {cast['woman']}; she is (S1), and <Audio 1> defines her voice timbre.",
        f"<Subject 2> is {cast['man']}; he is (S2).",
        R11_HAND,
    ])
    sum2 = f"{TASK_TAG} <Subject 1>, already bare from beat 1, continues into {cast.get('position') or 'the act'} with <Subject 2>."
    ret2 = "\n".join([
        "<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure continue from beat 1",
        "<Subject 2> (appears in [Shot 1]): fully_preserved - his face, build and skin stay the same man throughout",
        "<Audio 1> (voice of (S1)): attribute_transfer - her spoken lines take their voice timbre from <Audio 1>",
    ])
    prompt2 = (f"subject_definitions:\n{subj2}\n\nsummary:\n{sum2}\n\n"
               f"retention_analysis:\n{ret2}\n\ndetailed_description:\n[Shot 1] {lead2}\n")

    g1 = copy.deepcopy(base_graph)
    # Ensure minimal stub graphs used in unit tests have the continuation nodes (`refapply`, `s0_samp`, `s0_sep`, `c0` class_type)
    g1.setdefault("c0", {"inputs": {}}).setdefault("class_type", "MiniMaxH3ReferenceToVideo")
    g1.setdefault("refmods", {"inputs": {}}).setdefault("class_type", "MiniMaxH3RefModsLoader")
    if "refapply" not in g1:
        g1["refapply"] = {"class_type": "MiniMaxH3RefModApply",
                          "inputs": {"conditioning": ["c0", 0], "mods": ["refmods", 0], "retention": 1.0}}
    else:
        g1["refapply"].setdefault("class_type", "MiniMaxH3RefModApply")
        g1["refapply"].setdefault("inputs", {"conditioning": ["c0", 0], "mods": ["refmods", 0], "retention": 1.0})
    g1.setdefault("s0_samp", {"class_type": "SamplerCustomAdvanced", "inputs": {}})
    g1.setdefault("s0_sep", {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["s0_samp", 0]}})
    g1["c0"]["inputs"].update({"prompt": prompt1.strip(), "length": b1_frames, "width": width, "height": height, "fps": H3_FPS})
    g1["noise"]["inputs"]["noise_seed"] = seed
    g1["save"]["inputs"]["filename_prefix"] = prefix

    g2 = copy.deepcopy(g1)
    for k in [nid for nid, node in g2.items() if node.get("class_type") in ("MiniMaxH3AddGuide", "LoadImage") or nid == "img_1"]:
        del g2[k]
    g2["refapply"]["inputs"]["conditioning"] = ["c0", 0]
    g2["c0"]["inputs"].update({"prompt": prompt2.strip(), "length": layout["window_frames"],
                               "width": width, "height": height, "fps": H3_FPS})

    # t105u-t110u: Non-human or faceless partner: load only her RefMod on all beats
    pt = str(cast.get("partner_type") or "man").lower()
    if pt in ("none", "non-human", "faceless"):
        for sub_g in (g1, g2):
            if "refmods" in sub_g and "inputs" in sub_g["refmods"]:
                inputs = sub_g["refmods"]["inputs"]
                for i in range(2, 9):
                    k = f"mod_{i}"
                    if k in inputs:
                        inputs[k] = "(none)"

    g = add_continuation_beat(g1, g2, layout, 2)
    prompt_all = f"===== beat 1 =====\n{prompt1.strip()}\n\n===== beat 2 =====\n{prompt2.strip()}\n"
    cont_plan = {
        "mode": "native_latent_tail_continuation",
        "clip_count": 2,
        "beats": [
            {"index": 1, "is_continuation": False, "frames": b1_frames},
            {"index": 2, "is_continuation": True, "frames": layout["total_frames"], "layout": layout},
        ],
        "base_frames": b1_frames,
        "extension_frames": layout["extension_frames"],
        "overlap_frames": layout["overlap_frames"],
        "window_frames": layout["window_frames"],
        "total_frames": layout["total_frames"],
        "total_seconds": layout["total_seconds"],
        "fps": H3_FPS,
        "stitched": False,
        "packed_beats": drep.get("packed_beats"),
        "beat1_report": rep1,
        "beat2_report": drep,
    }
    return g, prompt_all, cont_plan


# --- dynsafe: still read + cast for production (moved from runs/expanded_writer_test_20261111/_ewt_run.py) --------------
VISION_READ_PROMPT = (
    "Describe this start still for a video prompt writer. Judge only what you see. Reply with JSON only, with these keys: "
    "\"room\" (short phrase for the place, e.g. 'a bedroom with a bed in grey sheets' or 'a sunny beach with white sand'), "
    "\"place\" (one or two words, e.g. 'bedroom', 'beach', 'living room', 'kitchen', 'studio'), "
    "\"bed\" (true/false), \"sheets\" (the bed linen if there is a bed, e.g. 'grey sheets', else ''), "
    "\"surface\" (the best surface in view for lying or kneeling on, with 'the', e.g. 'the bed', 'the sofa', 'the rug', 'the sand', 'the floor'), "
    "\"floor\" (what is underfoot, e.g. 'wood floor', 'carpet', 'tile floor', 'sand', 'grass'), "
    "\"light\" (short phrase), \"framing\" (e.g. 'full-body, eye-level, front'), "
    "\"pose\" (third person, starting with a verb, place and posture only, no clothing, e.g. 'stands barefoot on the carpet in front of the bed'), "
    "\"facing_camera\" (true/false), "
    "\"garments\": [{\"type\": one of 'bra','panties','thong','bikini top','bikini bottoms','swimsuit','dress','top','skirt','shorts','pants','jacket','shoes','garter belt','stockings','choker','other', "
    "\"name\": short garment name, e.g. 'yellow sundress' or 'black lace bra', \"look\": colour and material, e.g. 'black lace'}] (empty list if she is nude), "
    "\"hair\" (e.g. 'long wavy blonde hair'), \"skin\" (e.g. 'fair skin'), \"build\" (e.g. 'a slim adult build with natural curves'), "
    "\"people\" (number of people visible)")
OC_MAN = ("an adult man, twenty-six years of age, of solid adult build with working forearms and adult weight, the same man "
          "for the whole clip")
OC_VOICE_S1 = "a low, warm adult woman's voice with a slightly husky edge, tight and breathy with the effort"
OC_VOICE_S2 = "a contrasting deep, steady adult man's voice, low and hoarse"
OC_VOICE_S2_WOMAN = "a contrasting low, steady adult woman's voice, smoky and firm"  # #6 futa/woman partner
# long-scene spec G1-G4 (Derrick, Prompt maker t243s804/t243s811): creature partners are non-human (her RefMod only, look text only - G4: no creature RefMod yet)
_CREATURE_RE = re.compile(r"(?i)\b(orcs?|ogres?|trolls?|goblins?|monsters?|demons?|aliens?|minotaurs?|werewol(?:f|ves)|"
                          r"centaurs?|tentacles?|tentacled|creatures?|elf|elves|elven)\b")
_CREATURE_LOOKS = {
    "orc": "an adult male orc, towering and heavily muscled, with green skin, small lower tusks and coarse black hair",
    "troll": "an adult male troll, huge and broad, with grey-green hide and heavy brows",
    "ogre": "an adult male ogre, huge and broad, with thick grey skin",
    "goblin": "an adult male goblin, wiry, with green skin and pointed ears",
    "elf": "an adult male elf, tall and lean, with pointed ears and long pale hair",
    "alien": "an adult male alien, tall and lean, with smooth blue-grey skin and large dark eyes",
    "demon": "an adult male demon, tall and muscular, with red skin and curved horns",
    "minotaur": "an adult male minotaur, a huge bull-headed humanoid with dark hide",
    "werewolf": "an adult male werewolf, huge, with dark fur and a wolf's head",
    "centaur": "an adult male centaur, a muscular man's torso on a horse's body",
    "tentacle": "a mass of thick, slick tentacles with no face",
}
OC_VOICE_NONHUMAN = "a deep, rough, guttural non-human voice"  # G3


def creature_look(ask: str) -> str:
    m = _CREATURE_RE.search(ask or "")
    if not m:
        return "an adult non-human male partner"
    w = m.group(1).lower().rstrip("s")
    w = {"elve": "elf", "elven": "elf", "werewolve": "werewolf", "tentacled": "tentacle", "creature": "monster"}.get(w, w)
    return _CREATURE_LOOKS.get(w, f"an adult male {w}, huge and inhuman")


_UNDRESS_ASK_RE = re.compile(
    r"(?i)\b(?:undress(?:es|ed|ing)?|strip(?:s|ped|ping|tease)?|naked|nude|topless|bottomless|"
    r"clothes off|takes?\s+(?:off\s+)?(?:her|his|their)?\s*(?:clothes|lingerie|underwear|garments)(?:\s+off)?|"
    r"get(?:s|ting)? undressed)\b"
)
# t105u-t110u: fail closed on the hook for group sex >3 bodies and three-body asks (FFM/MMF)
_GROUP_GT3_ASK_RE = re.compile(
    r"(?i)\b(?:gang[- ]?bang|orgy|orgies|foursome|bukkake|(?:five|six|seven|eight|[5-9]|\d{2,})[- ]?(?:some|way)|"
    r"group[- ]?sex(?:\s+with\s+(?:more\s+than\s+3|[4-9]|\d{2,})\s+bodies)?)\b"
)
_THREE_BODY_ASK_RE = re.compile(
    r"(?i)\b(?:ffm|mmf|f/f/m|m/m/f|f\+f\+m|m\+m\+f|threesome|three[- ]?way|menage[- ](?:a[- ])?trois)\b"
)


def validate_hook_ask(position: str, ask: Optional[str]) -> None:
    """Fail closed on group sex >3 bodies (gangbang, orgy, foursome, bukkake)."""
    comb = f"{position} {ask or ''}"
    m_gt3 = _GROUP_GT3_ASK_RE.search(comb)
    if m_gt3:
        raise WriterNotReady(f"NOT_READY: group sex with >3 bodies ({m_gt3.group(0)!r}) is not supported; failing closed on the hook")



def _parse_json_reply(text: str) -> Dict[str, Any]:
    t = re.sub(r"```(?:json)?", "", (text or "").split("</think>")[-1])
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b <= a:
        raise WriterNotReady("NOT_READY: the vision read is not JSON")
    try:
        return json.loads(t[a:b + 1])
    except ValueError as e:
        raise WriterNotReady(f"NOT_READY: the vision read is not JSON ({e})")


def vision_read(image: Any, chat: Callable[[List[Dict[str, Any]]], str]) -> Dict[str, Any]:
    """One structured read of the start still (setting, bed, surface, floor, light, framing, pose, garments, hair, skin,
    build, people). `chat(messages) -> reply text` is the caller's vision model call (the EWT used the native Swift
    vision on llama-swap); this function loads no model itself. Any failure is NOT_READY."""
    import base64
    import io
    from PIL import Image
    im = image if hasattr(image, "save") else Image.open(image)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG")
    url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    reply = chat([{"role": "user", "content": [{"type": "text", "text": VISION_READ_PROMPT},
                                               {"type": "image_url", "image_url": {"url": url}}]}])
    read = _parse_json_reply(reply)
    if not isinstance(read, dict) or not (read.get("room") or read.get("place") or read.get("surface")):
        raise WriterNotReady("NOT_READY: the vision read has no setting")
    return read


_ACTS_CACHE: Optional[Dict[str, Any]] = None


def load_acts_registry(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the acts registry from acts.yaml (cached)."""
    global _ACTS_CACHE
    if _ACTS_CACHE is not None and path is None:
        return _ACTS_CACHE
    p = path or (Path(__file__).parent / "acts.yaml")
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    _ACTS_CACHE = data.get("acts", {})
    return _ACTS_CACHE


_CAM_KIND_MAP = {
    "third_person": "third-person",
    "third-person": "third-person",
    "pov": "POV",
    "POV": "POV",
    "close_up": "close-up",
    "close-up": "close-up",
    "webcam": "webcam",
    "handheld_sextape": "handheld_sextape",
    "bts_interview": "bts_interview",
}


def _infer_package2_act(position: str, ask: str, partner_type: str = "man") -> Optional[str]:
    """If the hook position is not in the registry, let package 2 name male_solo / standing_mf / airplane / piledriver."""
    if position and position != "undress" and get_act(position):
        return None
    brief = scene_addenda.resolve_brief(
        " ".join(x for x in (position, ask) if x).strip(),
        act_id=None, registry=load_acts_registry(), partner_type=partner_type,
    )
    if brief.get("act_id") and get_act(brief["act_id"]):
        return brief["act_id"]
    return None


def get_act(name_or_alias: str) -> Optional[Dict[str, Any]]:
    """Look up an act in acts.yaml by id or alias."""
    if not name_or_alias:
        return None
    acts = load_acts_registry()
    target = name_or_alias.strip().lower()
    if target in acts:
        return acts[target]
    for act_id, entry in acts.items():
        if target == act_id.lower():
            return entry
        aliases = [a.lower() for a in entry.get("aliases", [])]
        if target in aliases:
            return entry
    return None


def make_cast(read: Optional[Dict[str, Any]], position: str, ask: str, man: str = OC_MAN, voice_s1: str = OC_VOICE_S1,
              voice_s2: str = OC_VOICE_S2, voice_s3: str = "a low, firm adult voice", partner_type: str = "man",
              partner_type2: Optional[str] = None, role: Optional[str] = None,
              beat_kind: Optional[str] = None, camera_kind: Optional[str] = None,
              continued: bool = False, inherited_garments: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """The OC writer cast from one still read (moved from the EWT driver). dynsafe: every garment (type 'other' too) is
    kept under the still's own phrase; nothing is renamed to a fixed lingerie word; no garment = wardrobe_unverified (no
    raise); undress only when the ask names it; the setting, surface and pose come from the read (no bedroom / room /
    'stands' defaults); the pose bridge is built in finalize from the still pose and the writer's own act pose."""
    if not read:
        raise WriterNotReady("NOT_READY: no still read (vision facts) for <Picture 1>")
    validate_hook_ask(position, ask)
    if (position == "male_solo") or (_infer_package2_act(position, ask, partner_type) == "male_solo"):
        _src0 = dict(_unwrap_still_read(read))
        _src0.update({"hair": "", "skin": "", "build": "", "pose": "", "garments": [], "facing_camera": False, "people": 0})
        read = dict(read, read=_src0) if isinstance(read, dict) and isinstance(read.get("read"), dict) else _src0
    f = still_facts(read)
    inv = garment_inventory(read)

    def join(xs):
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    names = [g["name"] for g in inv]
    off = [g["name"] for g in inv if g["slot"] in _COVER_SLOTS]
    stay = [g["name"] for g in inv if g["slot"] not in _COVER_SLOTS]
    still_garments = join([_article(n) for n in names]) if names else ""
    bed = f["bed"]
    surface = f["surface"]
    sheets = f["sheets"] or surface
    sheets = sheets if re.match(r"(?i)(?:the|a|an|her)\b", sheets) else "the " + sheets
    pad = "mattress" if bed else re.sub(r"(?i)^(?:the|a|an)\s+", "", surface)
    _clean_surf = lambda s: re.sub(r'^(?:(?:the|a|an)\s+)+', '', (s or '').strip(), flags=re.I)
    def _the(s: str) -> str:
        s = re.sub(r"\s+", " ", (s or "").strip())
        s = re.sub(r"(?i)\bthe\s+the\b", "the", s)
        if s and not re.match(r"(?i)(?:the|a|an|her|his)\b", s):
            s = "the " + s
        return s
    floor = _clean_surf(f["floor"])
    at_floor = "the " + (floor + " beside the bed" if bed and floor else floor or _clean_surf(surface) or "floor")
    at_floor = re.sub(r"(?i)\bthe\s+the\b", "the", at_floor)
    pose = f["pose"].rstrip(".")
    pose = re.sub(r"(?i)^she\s+", "", pose)
    facing = ", facing the camera" if read.get("facing_camera") and "facing" not in pose else ""
    still_bits = [f["setting"] or NEUTRAL_SETTING]
    if f["light"]:
        still_bits.append(f"lit by {f['light']}")
    if read.get("framing"):
        still_bits.append(f"framed {read['framing']}")
    if (position == "male_solo") or (_infer_package2_act(position, ask, partner_type) == "male_solo"):
        still_line = ", ".join(still_bits) + ". This clip is male solo: (S1) is the man. The person shown in the start still is not (S1) and is not in this clip"
    else:
        still_line = ", ".join(still_bits) + (f", with <Subject 1> {pose}{facing}" if pose else ", with <Subject 1> exactly as shown")
    wear = f" in {still_garments}" if still_garments else ""
    src = _unwrap_still_read(read)
    woman_bits = ["an adult woman in her twenties"] + [x for x in (src.get("build"), src.get("skin"), src.get("hair")) if x]
    if (position == "male_solo") or (_infer_package2_act(position, ask, partner_type) == "male_solo"):
        woman_bits = []
        still_garments = ""
        wear = ""
        # still_line already setting-only; do not attach her hair, skin or clothes
        src = {**src, "hair": "", "skin": "", "build": "", "pose": "", "garments": []}
    undress = bool(_UNDRESS_ASK_RE.search(ask or ""))

    act_entry = get_act(position)
    if position != "undress" and not act_entry:
        inferred = _infer_package2_act(position, ask, partner_type)
        if inferred:
            position = inferred
            act_entry = get_act(inferred)
    if position != "undress" and not act_entry:
        raise WriterNotReady(f"NOT_READY: unknown act {position!r}")

    act_id = act_entry.get("id", position) if act_entry else position
    act_pts = act_entry.get("partner_types", ["man"]) if act_entry else ["man"]
    if partner_type == "man" and act_pts == ["none"]:
        partner_type = "none"
    elif partner_type == "man" and act_pts == ["woman"]:
        partner_type = "woman"

    pt = str(partner_type or "man").lower()
    if pt == "man":
        if re.search(r"\bnon[- ]human\b", ask or "", re.I) or _CREATURE_RE.search(ask or ""):  # G1
            pt = "non-human"
        elif re.search(r"\bfaceless\b", ask or "", re.I):
            pt = "faceless"

    is_3p_act = (act_entry.get("bodies", 2) == 3) if act_entry else False
    is_3p_ask = bool(_THREE_BODY_ASK_RE.search(f"{position} {ask or ''}"))
    is_3p = is_3p_act or is_3p_ask
    req_bodies = 3 if is_3p else (act_entry.get("bodies", 2) if act_entry else 2)
    is_ffm = (act_id == "ffm") or bool(re.search(r"(?i)\b(?:ffm|two (?:women|girls)|another (?:woman|girl))\b", ask or ""))

    pt2 = str(partner_type2 if partner_type2 is not None else ("woman" if is_ffm else ("faceless" if is_3p else "none"))).lower()
    if pt2 == "man":
        if re.search(r"\bnon[- ]human\b", ask or "", re.I):
            pt2 = "non-human"
        elif re.search(r"\bfaceless\b", ask or "", re.I):
            pt2 = "faceless"

    b_kind = beat_kind or ("undress" if position == "undress" else (
        "dance" if act_id in ("dance", "twerk") else (
            "tease" if act_id in ("tease", "strip") else (
                "talk" if act_id == "talk" else "act"
            )
        )
    ))

    c_kind = camera_kind or (act_entry.get("default_camera") if act_entry else None) or "third-person"
    if c_kind == "POV":
        cam_tail = "keeping her face in frame, partner POV"
    elif c_kind == "close-up":
        cam_tail = "close-up, keeping her face in frame"
    elif is_3p:
        cam_tail = "keeping all three faces in frame"
    elif pt in ("none", "non-human", "faceless"):
        cam_tail = "keeping her face in frame"
    elif pt == "woman":
        cam_tail = "keeping both faces in frame"
    else:
        cam_tail = "keeping her face, his face and the join in frame"

    people = f.get("people") or []
    still_people = len(people) if people else None
    brief = scene_addenda.resolve_brief(
        ask or "", act_id=act_id, registry=load_acts_registry(),
        partner_type=pt, still_people=still_people,
    )
    if brief.get("not_ready"):
        # live people-count checks below keep the "people-count mismatch" wording
        _nr = brief["not_ready"]
        if "still shows" not in _nr or "brief asks for" not in _nr:
            raise WriterNotReady("NOT_READY: " + _nr)
    if brief.get("partner_type"):
        pt = str(brief["partner_type"]).lower()
    if brief.get("body_count") is not None and not is_3p:
        req_bodies = int(brief["body_count"])
    # Derrick t204u: talk-only spoof/parody. Bodies follow the still and ask (1-3).
    # A 1-body talk clip is partner_type none so finalize does not invent S2.
    if act_id == "talk":
        still_n = still_people if still_people is not None else 1
        ask_txt = ask or ""
        if (_THREE_BODY_ASK_RE.search(ask_txt)
                or re.search(r"\(S3\)|<Subject 3>", ask_txt, re.I)):
            req_bodies = 3
        elif (re.search(r"\(S2\)|<Subject 2>", ask_txt, re.I)
              or re.search(r"(?i)\bfuta(?:nari)?s?\b", ask_txt)
              or still_n >= 2):
            req_bodies = min(3, max(2, still_n))
        else:
            req_bodies = min(3, max(1, still_n))
        is_3p = req_bodies >= 3
        if req_bodies == 1:
            pt = "none"
    ck_brief = brief.get("camera_kind")
    if ck_brief and ck_brief not in ("third_person", "third-person"):
        c_kind = _CAM_KIND_MAP.get(ck_brief, ck_brief)
    _no_join_cam = (b_kind in ("dance", "tease", "strip", "talk", "undress", "transformation")
                    or act_id in ("female_solo", "male_solo", "talk", "dance", "tease", "strip", "undress"))
    if c_kind == "POV":
        cam_tail = "keeping her face in frame, partner POV"
    elif c_kind == "close-up":
        cam_tail = "close-up, keeping her face in frame"
    elif c_kind == "webcam":
        cam_tail = "webcam, keeping her face in frame"
    elif c_kind == "handheld_sextape":
        cam_tail = "handheld, keeping her face in frame"
    elif c_kind == "bts_interview":
        cam_tail = "keeping her face in frame"
    elif is_3p:
        cam_tail = "keeping all three faces in frame"
    elif pt in ("none", "non-human", "faceless") and act_id == "male_solo":
        cam_tail = "keeping his face in frame"
    elif pt in ("none", "non-human", "faceless") or _no_join_cam:
        cam_tail = "keeping both faces in frame" if pt in ("woman", "futa") else "keeping her face in frame"
    elif is_3p and still_people is not None and still_people < 3:
        cam_tail = "keeping her face in frame, and all faces in frame once everyone is in the shot"
    elif still_people is not None and still_people < 2 and pt == "man":
        cam_tail = "keeping her face in frame, and his face and the join in frame once he enters"
    elif still_people is not None and still_people < 2 and pt in ("woman", "futa"):
        cam_tail = "keeping her face in frame, and both faces in frame once her partner enters"
    elif pt in ("woman", "futa"):
        cam_tail = "keeping both faces in frame"
    else:
        cam_tail = "keeping her face, his face and the join in frame"
    if people:
        if pt == "none" and len(people) > 1:
            raise WriterNotReady(f"NOT_READY: people-count mismatch: solo ask requires 1 person but still has {len(people)}")
        if len(people) > req_bodies:
            raise WriterNotReady(f"NOT_READY: people-count mismatch: act {position} requires {req_bodies} bodies but still has {len(people)}")

    s1_gender = brief.get("s1_gender") or ("man" if act_id == "male_solo" else "woman")
    woman_desc_bits = (
        (["an adult man in his twenties"] + [x for x in (src.get("build"), src.get("skin"), src.get("hair")) if x])
        if s1_gender == "man" else woman_bits
    )
    woman_line_src = woman_desc_bits

    base = dict(
        woman=", ".join(woman_line_src[:-1]) + (", and " + woman_line_src[-1] if len(woman_line_src) > 1 else woman_line_src[0]) if len(woman_line_src) > 1 else woman_line_src[0],
        man=(
            (man if (pt == "man" or (is_3p and not is_ffm and pt == "faceless")) else ("an adult woman, twenty-two years of age, of slender build" if pt in ("woman", "futa") else ""))
            if s1_gender != "man" else (man or "an adult man, twenty-four years of age, of solid adult build")
        ),
        voice_s1=("a deep, steady adult man's voice, low and hoarse" if (s1_gender == "man" or act_id == "male_solo") and voice_s1 == OC_VOICE_S1 else voice_s1),
        voice_s2=voice_s2 if (pt in ("man", "woman", "futa") or (is_3p and not is_ffm and pt == "faceless")) and act_id != "male_solo" else "",
        voice_s3=voice_s3 if (is_3p and pt2 not in ("none", "non-human")) else "",
        still=still_line,
        still_wardrobe=(f"{pose}{wear}{facing}" if pose else f"is shown exactly as in <Picture 1>{wear}"),
        still_garments=still_garments, still_pose=pose, still_read=read, inventory=inv,
        garments_off=join(off) if off else "", garments_stay=join(stay) if stay else "", garments_floor=at_floor,
        # Max Architect 3, Derrick t1104u/t1109u: never invent partner clothes from her still inventory.
        # finalize_writer_prompt fills his_clothes from garments the writer actually named; empty if none.
        his_clothes="",
        still_people=still_people,
        off_still_s2=bool(still_people is not None and still_people < 2 and pt in ("man", "woman", "futa") and req_bodies >= 2),
        off_still_s3=bool((is_3p or req_bodies >= 3) and still_people is not None and still_people < 3),
        absent_garments=absent_garment_pattern(read),
        camera_tail=cam_tail, position=position, ask=ask,
        dynamic_pose=True, undress=undress, surface=surface, still_bed=bed,
        partner_type=pt, partner_type2=pt2, role=role, beat_kind=b_kind, camera_kind=c_kind,
        continued=bool(continued),
        inherited_garments=dict(inherited_garments or {}),
        act_id=act_id, act_entry=act_entry, act_status=act_entry.get("status", "untested") if act_entry else "tested",
        is_three_person=is_3p, bodies=req_bodies,
        s1_gender=s1_gender, states=list(brief.get("states") or []),
        themes=list(brief.get("themes") or []), look=list(brief.get("look") or []),
        register=list(brief.get("register") or []), offscreen_voice=bool(brief.get("offscreen_voice")),
        sleeper_gender=brief.get("sleeper_gender"), addenda_flags=list(brief.get("flags") or []),
        look_line=scene_addenda.look_line(brief), first_beat_talk_ok=bool(brief.get("first_beat_talk_ok")),
    )

    if is_ffm and pt2 in ("woman", "futa"):
        base["partner3"] = "an adult woman, twenty-two years of age, of slender build"

    _waist = bool(_WAIST_SURFACE_RE.search(surface))
    if act_id == "missionary":
        _m_contact = (
            f"His penis is fully inside her vagina with their hips flush on every stroke; he stands at the edge of {surface} with his feet planted on {at_floor}, and her back rests on {surface}."
            if _waist else
            f"His penis is fully inside her vagina with their hips flush on every stroke; his knees and forearms carry his weight into the {pad}, and her heels press into {sheets}."
        )
        base.update(position_check=r"\b(lies|lying|lowers) (?:back )?onto her back|on her back\b",
            move_check=r"\b(lies|lie|lying|lowers?|lays?)\b[^.]{0,40}\b(back|onto (?:her|the) (?:back|sheets|mattress|pillows|forearms|elbows))|\bon her back\b",
            primary_motion="continuous deep frontal thrust, about one full cycle per second, full depth travel, hips staying in contact",
            contact=_m_contact,
            summary_act=f"<Subject 1> lies back on {surface} and takes <Subject 2> in the missionary position.")
    elif act_id == "doggy":
        _d_contact = (
            f"His penis is fully inside her vagina from behind with his hips flush against her buttocks on every stroke; her forearms brace on {surface} and both stand with feet planted on {at_floor}."
            if _waist else
            f"His penis is fully inside her vagina from behind with his hips flush against her buttocks on every stroke; her palms and knees carry her weight into the {pad}."
        )
        base.update(position_check=r"\bhands and knees\b|\ball fours\b",
            move_check=r"\bhands and knees\b|\ball fours\b|\bkneels? on (?:the|her) [\w -]{2,30}?\b(?:mattress|bed|sofa|rug|floor|sand|carpet|stage)\b|\bbends? (?:over|forward)\b",
            primary_motion="continuous deep rear thrust, about one full cycle per second, full depth travel, his hips meeting her buttocks on each stroke",
            contact=_d_contact,
            summary_act=f"<Subject 1> gets on her hands and knees on {surface} and takes <Subject 2> from behind in the doggy position.")
    elif act_id in ("cowgirl", "reverse cowgirl", "reverse_cowgirl", "riding"):  # oralfoley rule 5: the writer names both bodies' motion
        base.update(position_check=r"\b(?:straddl\w*|astride|rides?|riding|on top of him)\b",
            move_check=r"\b(?:straddl\w*|astride|climbs? (?:on top of|onto) him|swings? (?:a|her) (?:leg|knee) over|lowers? herself onto him)\b",
            primary_motion="",
            contact=f"His penis is inside her vagina as she sits astride his hips, her knees planted on {sheets} on either side of him.",
            summary_act=f"<Subject 1> straddles <Subject 2> on {surface} and rides him in the {position} position.")
    elif act_id in ("blowjob", "oral"):  # blowjob: the man's pose follows the writer (standing by default), never a forced lie-back
        base.update(position_check=r"\bkneel\w*\b|\bon her knees\b|\bbetween his (?:legs|knees|thighs)\b",
            move_check=r"\bkneel\w*\b|\bon her knees\b|\bbetween his (?:spread )?(?:legs|knees|thighs)\b|\bsinks? (?:down )?to her knees\b",
            primary_motion="continuous head bobbing, about one full cycle per second, her lips sliding down his shaft to half depth and back up to the glans",
            contact="His penis is in her mouth with her lips sealed around the shaft on every stroke; her hand grips the base.",
            summary_act="<Subject 1> gives <Subject 2> a blowjob.")
    elif act_id == "spooning":
        base.update(position_check=r"\b(?:on her side|side-lying|spooning|curled together)\b",
            move_check=r"\b(?:curls? on her side|lies? on her side|settles? on her side)\b",
            primary_motion="slow rhythmic rear thrust, about one full cycle per second, hips staying aligned",
            contact=f"His penis is fully inside her from behind as both lie curled on their sides on {surface}.",
            summary_act=f"<Subject 1> and <Subject 2> lie on their sides in the spooning position on {surface}.")
    elif act_id == "prone_bone":
        base.update(position_check=r"\b(?:face down|prone|flat on her stomach|on her stomach)\b",
            move_check=r"\b(?:lies? flat on her stomach|lowers? onto her stomach)\b",
            primary_motion="continuous deep downward rear thrust, about one full cycle per second, hips flush against her buttocks",
            contact=f"His penis is fully inside her from behind with her body pressed flat against {surface}.",
            summary_act=f"<Subject 1> lies face down on {surface} and takes <Subject 2> from behind in the prone bone position.")
    elif act_id == "titjob":
        base.update(position_check=r"\b(?:between her breasts|cleavage|breasts? pressed around)\b",
            move_check=r"\b(?:kneels? in front of him|sits? in front of him)\b",
            primary_motion="continuous sliding motion between her breasts, about one full cycle per second",
            contact="His penis is pressed between her breasts as her hands squeeze her cleavage firmly around the shaft.",
            summary_act=f"<Subject 1> gives <Subject 2> a titjob on {surface}.")
    elif act_id == "handjob":
        base.update(position_check=r"\b(?:fist wrapped around|strok\w* (?:his )?(?:shaft|penis|cock)|hand ?job)\b",
            move_check=r"\b(?:kneels? in front of him|sits? (?:beside|next to|in front of) him)\b",
            primary_motion="continuous stroking of his shaft with her fist, about one full cycle per second",
            contact="Her fist is wrapped around his penis as she strokes the shaft.",
            summary_act=f"<Subject 1> gives <Subject 2> a handjob on {surface}.")
    elif act_id == "finish":
        base.update(position_check=r"\b(?:cumshot|facial|creampie|finish|spills?)\b",
            move_check=r"\b(?:pulls? out|bucks?|spasms?)\b",
            primary_motion="spasming hip contractions that slow to a trembling stop",
            contact="He finishes as his hips press close, releasing onto her skin.",
            summary_act=f"<Subject 2> finishes on {surface} with <Subject 1>.")
    elif act_id == "female_solo":
        base.update(position_check=r"\b(?:fingers?|wand|vibrat\w*|touches? herself)\b",
            move_check=r"\b(?:touches? herself|fingers? herself|wand|vibrator)\b",
            primary_motion="rhythmic circular movement against her clitoris, about one full cycle per second",
            contact="",
            summary_act=f"<Subject 1> touches herself on {surface}.")
    elif act_id == "ff_cunnilingus":
        base.update(position_check=r"\b(?:between her thighs|cunnilingus|oral|laps?|licks?)\b",
            move_check=r"\b(?:kneels? between her thighs|settles between her thighs)\b",
            primary_motion="steady rhythmic lapping, about one full cycle per second",
            contact="Her face is between her thighs as her tongue moves against her clitoris.",
            summary_act=f"<Subject 2> gives <Subject 1> cunnilingus on {surface}.")
    elif act_id == "ff_scissoring":
        base.update(position_check=r"\b(?:scissoring|tribbing|legs? entangled|vulvas pressed)\b",
            move_check=r"\b(?:intertwines? her legs|presses? her hips)\b",
            primary_motion="synchronized circular hip grind, about one full cycle per second, pelvises staying flush",
            contact="(S1)'s vulva is pressed to (S2)'s vulva as their pelvises grind in synchronized circular motion.",
            summary_act=f"<Subject 1> and <Subject 2> scissor together on {surface}.")
    elif act_id == "mf_anal":
        base.update(position_check=r"\b(?:anal|from behind|hands and knees)\b",
            move_check=r"\b(?:hands and knees|all fours)\b",
            primary_motion="steady continuous rear thrust, about one full cycle per second, his hips meeting her buttocks on each stroke",
            contact=f"His penis is fully inside her anus from behind with his hips flush against her buttocks on every stroke; her palms and knees carry her weight into {pad}.",
            summary_act=f"<Subject 1> takes <Subject 2> in the anal doggy position on {surface}.")
    elif act_id == "bondage":
        base.update(position_check=r"\b(?:bound|restrained|strapped|cuffs?|ropes?|tied)\b",
            move_check=r"\b(?:pulls? against|arches? against|restrained)\b",
            primary_motion="continuous rhythmic motion while her wrists remain secured",
            contact="Her wrists are secured to the frame by restraints as he controls her hips.",
            summary_act=f"<Subject 1> is restrained in bondage on {surface} with <Subject 2>.")
    elif act_id == "dance":
        base.update(position_check=r"\b(?:twerk\w*|dance\w*|hips? sway\w*|gyrat\w*|bounc\w*)\b",
            move_check=r"\b(?:twerk\w*|dance\w*|sway\w*|gyrat\w*)\b",
            primary_motion="rhythmic hip drops and pelvic rotations, about one full cycle per second",
            contact="",
            summary_act=f"<Subject 1> dances on {surface}.")
    elif act_id == "tease":
        base.update(position_check=r"\b(?:tease\w*|slowly peel\w*|strips?|unfasten\w*)\b",
            move_check=r"\b(?:tease\w*|strips?|slides?)\b",
            primary_motion="slow deliberate movement as she slides the garment down",
            contact="",
            summary_act=f"<Subject 1> teases the camera on {surface}.")
    elif act_id == "threesome":
        base.update(position_check=r"\b(?:threesome|three[- ]way|all three)\b",
            move_check=r"\b(?:threesome|three[- ]way|rhythmic|thrusting|touching)\b",
            primary_motion="continuous rhythmic contact and movement among all three adults",
            contact=f"<Subject 1>, <Subject 2>, and <Subject 3> maintain continuous physical contact on {surface}.",
            summary_act=f"<Subject 1>, <Subject 2>, and <Subject 3> engage in a threesome on {surface}.")
    elif act_id == "mmf":
        base.update(position_check=r"\b(?:mmf|double penetration|two men|both men)\b",
            move_check=r"\b(?:mmf|thrusting|penetration|moving)\b",
            primary_motion="synchronized rhythmic movement between <Subject 1>, <Subject 2>, and <Subject 3>",
            contact=f"<Subject 2>'s penis is inside her mouth, her lips sealed around his shaft; <Subject 3> is behind her on {surface}.",
            summary_act=f"<Subject 1>, <Subject 2>, and <Subject 3> engage in an MMF scene on {surface}.")
    elif act_id == "ffm":
        base.update(position_check=r"\b(?:ffm|two women|both women)\b",
            move_check=r"\b(?:ffm|rhythmic|moving|embracing)\b",
            primary_motion="continuous fluid motion and intimate contact between all three adults",
            contact=f"<Subject 2>'s penis is inside <Subject 1>'s vagina; <Subject 3>'s mouth is on <Subject 1>'s vulva, on {surface}.",
            summary_act=f"<Subject 1>, <Subject 2>, and <Subject 3> engage in an FFM scene on {surface}.")
    elif act_id == "mmf_double_blowjob":
        base.update(oral_giver="S1",
            position_check=r"\b(?:double blowjob|both penises|oral|sucking)\b",
            move_check=r"\b(?:bobbing|caressing|sucking|moving)\b",
            primary_motion="steady alternating oral and manual attention on <Subject 2> and <Subject 3>",
            contact=f"<Subject 1> is positioned between <Subject 2> and <Subject 3> on {surface}, holding and caressing both.",
            summary_act=f"<Subject 1> performs a double blowjob for <Subject 2> and <Subject 3> on {surface}.")
    elif act_id == "male_solo":
        base.update(position_check=r"\b(?:strokes? himself|grips? his shaft|jerks? off|jacks? off|edges?)\b",
            move_check=r"\b(?:strokes?|grips?|edges?)\b",
            primary_motion="slow strokes that speed up, about one full cycle per second",
            contact="",
            summary_act=f"<Subject 1> strokes himself on {surface}.")
    elif act_id == "standing_mf":
        base.update(position_check=r"\b(?:standing|both (?:on their )?feet|feet (?:planted|on the floor))\b",
            move_check=r"\b(?:standing|feet planted|on their feet)\b",
            primary_motion="continuous hip thrusts, about one full cycle per second, both feet planted",
            contact=f"His penis is fully inside her vagina; both of them are standing with their feet on the floor on {surface}.",
            summary_act=f"<Subject 1> and <Subject 2> have sex standing on {surface}.")
    elif act_id == "airplane":
        base.update(position_check=r"\b(?:airplane|legs (?:held|up and out)|thighs)\b",
            move_check=r"\b(?:holds? her thighs|legs (?:held|up))\b",
            primary_motion="continuous hip thrusts, about one full cycle per second, her legs held up and out",
            contact="His penis is fully inside her vagina; he holds her thighs with her legs up and out.",
            summary_act=f"<Subject 2> holds <Subject 1> in the airplane position on {surface}.")
    elif act_id == "piledriver":
        base.update(position_check=r"\b(?:piledriver|pile driver|hips raised|over her shoulders)\b",
            move_check=r"\b(?:hips raised|over her shoulders|drives down)\b",
            primary_motion="downward thrusts, about one full cycle per second, her hips raised over her shoulders",
            contact="His penis is fully inside her vagina; her hips are raised over her shoulders.",
            summary_act=f"<Subject 2> takes <Subject 1> in the piledriver position on {surface}.")
    elif position == "undress":
        base.update(position_check=r"$^",
            move_check=r"$^",
            primary_motion="",
            contact="",
            summary_act="<Subject 1> takes off her clothes.")
    elif act_id == "talk":
        # Derrick t204u: talk-only. No contact or PRIMARY MOTION, and none is injected.
        base.update(position_check=r"$^",
            move_check=r"$^",
            primary_motion="",
            contact="",
            summary_act=f"<Subject 1> talks on {surface}.")
    else:
        raise WriterNotReady(f"NOT_READY: unknown act {position!r}")

    if pt != "man":
        base["his_clothes"] = ""
        if pt == "woman" and base.get("voice_s2") == OC_VOICE_S2:
            base["voice_s2"] = OC_VOICE_S2_WOMAN  # #6: a woman partner never gets the man's voice line
        if pt != "futa" and "penis" in base.get("contact", "").lower():
            base["contact"] = ""
        if pt == "non-human" and _CREATURE_RE.search(ask or "") and act_id != "male_solo":
            # G1-G4: a creature partner is described (look text only, no RefMod) and can speak unless it has no face
            look = creature_look(ask)
            base["man"] = look
            base["voice_s2"] = "" if "no face" in look else OC_VOICE_NONHUMAN
            base["camera_tail"] = "keeping her face in frame" if "no face" in look else "keeping both faces in frame"
        elif pt in ("none", "non-human", "faceless"):
            if act_id != "male_solo":
                base["man"] = ""
            base["voice_s2"] = ""
            base["camera_tail"] = "keeping his face in frame" if act_id == "male_solo" else "keeping her face in frame"
            if pt == "none" and act_id != "male_solo":
                base["summary_act"] = f"<Subject 1> is on {surface}."
        elif pt == "futa":
            # R15: S2 keeps she/her and one RefMod; never rewritten to a man.
            if not base.get("man"):
                base["man"] = "an adult woman, twenty-two years of age, of slender build"
            if not base.get("voice_s2") or base.get("voice_s2") == OC_VOICE_S2:
                base["voice_s2"] = voice_s2 if voice_s2 != OC_VOICE_S2 else OC_VOICE_S2_WOMAN  # #6
            base["camera_tail"] = "keeping both faces in frame"

    base["position_beat"] = transition_beat(base, "")
    if undress:
        base["summary_act"] = "<Subject 1> takes off her clothes, and " + base["summary_act"][:1].lower() + base["summary_act"][1:]
        base["summary_act"] = base["summary_act"].replace("and <subject 1>", "and she", 1)
    return base


def merge_refmod_slots(slots1: Dict[str, Any], slots2: Optional[Dict[str, Any]] = None,
                       slots3: Optional[Dict[str, Any]] = None,
                       three_person: bool = False,
                       partner_types: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """U4: up to 4 S1 + 4 S2 RefMods into mod_1..mod_8 (spare slots go to whichever subject has more).
    For 3-person (or when slots3 is given): at most 1 RefMod per named face, unused slots empty (none),
    faceless/non-human get none. >8 named faces is NOT_READY.
    """
    def live(slots):
        out = []
        for i in range(1, 9):
            info = (slots or {}).get(f"mod_{i}", {})
            if info.get("path") and info.get("path") != "(none)":
                out.append(dict(info))
        return out

    if three_person or slots3 is not None:
        pts = list(partner_types or ["man", "man"])
        pt2 = pts[0] if len(pts) > 0 else "man"
        pt3 = pts[1] if len(pts) > 1 else "man"

        named_subjects = [
            ("S1", slots1, True),
            ("S2", slots2, pt2 not in ("none", "non-human", "faceless")),
            ("S3", slots3, pt3 not in ("none", "non-human", "faceless", "still")),
        ]

        named_faces = [s for s, sl, is_named in named_subjects if is_named]
        if len(named_faces) > 8:
            raise WriterNotReady(f"NOT_READY: more named faces ({len(named_faces)}) than 8 RefMod slots")

        merged = []
        for s, sl, is_named in named_subjects:
            if not is_named:
                continue
            l = live(sl)
            if not l:
                raise WriterNotReady(f"NOT_READY: named face ({s}) has no RefMod and was not marked non-human or faceless")
            merged.append(l[0])

        out: Dict[str, Any] = {}
        for i in range(1, 9):
            out[f"mod_{i}"] = merged[i - 1] if i - 1 < len(merged) else {"path": "(none)", "strength": 1.0, "copies": 1}
        return out

    a = live(slots1)
    if not slots2:
        merged = a[:8]
    else:
        seen = {x["path"] for x in a}
        b = [x for x in live(slots2) if x["path"] not in seen]
        b_keep = b[:4]
        a_keep = a[: 8 - len(b_keep)]
        b_keep = b[: 8 - len(a_keep)]
        merged = a_keep + b_keep
    out: Dict[str, Any] = {}
    for i in range(1, 9):
        out[f"mod_{i}"] = merged[i - 1] if i - 1 < len(merged) else {"path": "(none)", "strength": 1.0, "copies": 1}
    return out


MIN_GUIDE_SEPARATION_SEC = 0.5
NEW_SHOT_MAX_PIN_SEC = 0.5


def snap_still_token_frame(sec: float, fps: int = H3_FPS) -> int:
    """Snap a clip-relative second to the nearest zero-based still-token index `17*k`."""
    s = float(sec)
    if s <= 0.0:
        return 0
    return 17 * max(1, int(round((s * fps) / 17.0)))


MID_ACT_FRAME_RE = re.compile(
    r"(?:\b|_)(?:mid[-_]?act|mid[-_]?frame|mid[-_]?scene|midact|midframe)\b|"
    r"(?:\b|_)(?:frame|f)[-_]0*([1-9]\d*)\b",
    re.IGNORECASE,
)


def validate_target_opening_pose(
    image: Union[str, Path],
    frame_idx: Optional[int] = None,
    is_opening_pose: Optional[bool] = None,
) -> None:
    """Validate that an image used for a prequel last-frame pin is the target clip's opening pose (frame 0).

    Rejects mid-act frames, frame indices > 0, or paths marked as mid-act.
    """
    if is_opening_pose is False:
        raise ValueError(
            f"mid-act frame is not accepted as the last-frame pin image ({image}): "
            "the last-frame pin must be the existing clip's opening pose (frame 0)"
        )
    if frame_idx is not None and frame_idx != 0:
        raise ValueError(
            f"mid-act frame (frame_idx={frame_idx}) is not accepted as the last-frame pin image ({image}): "
            "the last-frame pin must be the existing clip's opening pose (frame 0)"
        )
    img_str = str(image).replace("\\", "/")
    stem = Path(img_str).stem.lower()
    if MID_ACT_FRAME_RE.search(stem) or MID_ACT_FRAME_RE.search(img_str):
        raise ValueError(
            f"mid-act frame is not accepted as the last-frame pin image ({image}): "
            "the last-frame pin must be the existing clip's opening pose (frame 0)"
        )


def _is_last_frame_spec(val: Any) -> bool:
    """True if val indicates the clip's last sampled frame ('end', -1, or '-1')."""
    if isinstance(val, (int, float)):
        return val == -1 or val == -1.0
    if isinstance(val, str):
        s = val.strip().lower()
        return s in ("end", "-1", "-1.0")
    return False


def _parse_image_at_arg(v: Any) -> Any:
    s = str(v).strip().lower()
    if s in ("end", "-1", "-1.0"):
        return "end"
    try:
        val = float(s)
        if val == -1.0:
            return "end"
        return val
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid --image-at value: {v!r} (expected seconds, -1, or 'end')")


def normalize_beat1_image_times(
    staged: Sequence[str],
    image_times: Optional[Sequence[Any]],
    frames: int,
    fps: int = H3_FPS,
) -> List[float]:
    """Validate and return clip-relative times (seconds) for Beat 1's `staged` reference images.

    First `--image` is frame 0 (`0.0s`, required if any later pin is set). Later images require an explicit
    `image_times` entry within `[0, frames / fps)`, strictly increasing and at least `0.5s` apart.
    Accepts `end`, `-1`, or `'-1'` as the last sampled frame (`frames - 1`), resolved to seconds before return.
    """
    n = len(staged)
    if n == 0:
        if image_times:
            raise ValueError("--image-at requires a matching --image (frame-0 start image first)")
        return []

    raw_items = list(image_times or [])
    last_frame = frames - 1
    last_sec = float(last_frame) / float(fps)

    if n == 1:
        if not raw_items:
            return [0.0]
        if len(raw_items) != 1:
            raise ValueError(f"1 --image passed but {len(raw_items)} --image-at times given")
        item = raw_items[0]
        if _is_last_frame_spec(item):
            validate_target_opening_pose(staged[0])
            return [last_sec]
        try:
            val = float(item)
        except (ValueError, TypeError):
            raise ValueError(f"invalid --image-at value: {item!r}")
        if abs(val) <= 1e-6:
            return [0.0]
        if abs(val - last_sec) <= 1e-6:
            validate_target_opening_pose(staged[0])
            return [last_sec]
        raise ValueError(f"first --image must be the frame-0 start image (0.0s), got {val:g}s")

    if not raw_items:
        raise ValueError(
            "--image is the frame-0 start image (MiniMaxH3AddGuide): pass --image-at <sec> for each additional pin"
        )

    parsed_items: List[float] = []
    for idx, item in enumerate(raw_items):
        if _is_last_frame_spec(item):
            if idx != len(raw_items) - 1:
                raise ValueError(
                    f"--image-at {item!r} (last-frame pin) is only valid on the final pin, got at index {idx + 1}"
                )
            parsed_items.append(last_sec)
        else:
            try:
                parsed_items.append(float(item))
            except (ValueError, TypeError):
                raise ValueError(f"invalid --image-at value: {item!r}")

    if len(parsed_items) == n - 1:
        times = [0.0] + parsed_items
    elif len(parsed_items) == n:
        if abs(parsed_items[0]) > 1e-6:
            raise ValueError(f"first --image must be the frame-0 start image (0.0s), got {parsed_items[0]:g}s")
        times = [0.0] + parsed_items[1:]
    else:
        raise ValueError(
            f"{n} --image paths require {n - 1} (or {n} including 0.0s) --image-at times; got {len(raw_items)}"
        )

    max_sec = frames / float(fps)
    for idx, t in enumerate(times):
        if t < 0.0 or t >= max_sec or int(round(t * fps)) >= frames:
            raise ValueError(
                f"--image-at {t:g}s (pin {idx + 1}) is outside beat 1's sampled length ({frames}f / {max_sec:.3f}s)"
            )
        if idx > 0:
            if t <= times[idx - 1]:
                raise ValueError(f"--image-at times must be strictly increasing, got {times}")
            if (t - times[idx - 1]) < (MIN_GUIDE_SEPARATION_SEC - 1e-9):
                raise ValueError(
                    f"--image-at pins {times[idx - 1]:g}s and {t:g}s are closer than {MIN_GUIDE_SEPARATION_SEC}s"
                )

    if times and abs(times[-1] - last_sec) < 1e-6:
        validate_target_opening_pose(staged[-1])

    return times


def inject_reference_images(
    graph: Dict[str, Any],
    staged: Sequence[str],
    image_times: Optional[Sequence[Any]] = None,
    frames: Optional[int] = None,
    snap_token_grid: bool = False,
    frame_indices: Optional[Sequence[int]] = None,
) -> None:
    """U2 (t289u) + argon-low C.2 (A): chain 1..N MiniMaxH3AddGuide keyframes on Beat 1 (in-memory graph only).

    First `--image` is frame 0 (`img_1` -> `add_guide` with `frame_idx=0`). Each later `--image` at `sec` wires
    `img_k` -> `add_guide_k(positive=prev_guide, latent=c0.1, vae=vvae, image=img_k, frame_idx=round(sec*fps))`
    (or `17*k` when `snap_token_grid=True`), and `refapply.conditioning` points to the last guide in the chain.
    Accepts `frame_indices` or `image_times` with `-1` or `'end'` to pin the last sampled frame (`frames - 1`).
    `c0` stays text-only (no `ref_images`).
    """
    if not staged:
        if image_times or frame_indices:
            raise ValueError("--image-at requires a frame-0 --image first")
        return
    c0_len = int(frames or graph.get("c0", {}).get("inputs", {}).get("length") or DEFAULT_CONTINUATION_BASE_FRAMES)
    resolved_indices: Optional[List[int]] = None
    if frame_indices is not None:
        if len(frame_indices) != len(staged):
            raise ValueError(f"{len(staged)} --image paths require {len(staged)} frame_indices, got {len(frame_indices)}")
        resolved_indices = [c0_len - 1 if idx == -1 else int(idx) for idx in frame_indices]
        times = [float(idx) / float(H3_FPS) for idx in resolved_indices]
    else:
        times = normalize_beat1_image_times(staged, image_times, frames=c0_len, fps=H3_FPS)

    if graph.get("refapply", {}).get("inputs", {}).get("conditioning") != ["c0", 0]:
        raise ValueError("template drift: refapply.conditioning is not ['c0', 0]; refusing to wire add_guide")
    prev_cond: List[Any] = ["c0", 0]
    used_frames: List[int] = []
    for k, (raw_rel, sec) in enumerate(zip(staged, times), start=1):
        rel = str(raw_rel).replace("\\", "/")
        if not rel.startswith("community/"):
            rel = "community/" + rel.split("/")[-1]
        img_id = f"img_{k}"
        guide_id = "add_guide" if k == 1 else f"add_guide_{k}"
        is_last_pin = (k == len(staged))
        is_end_frame = (abs(sec - (c0_len - 1) / float(H3_FPS)) < 1e-5)
        if resolved_indices is not None:
            f_idx = resolved_indices[k - 1]
            if f_idx == c0_len - 1:
                validate_target_opening_pose(staged[k - 1])
        elif k == 1 and abs(sec) < 1e-6:
            f_idx = 0
        elif is_last_pin and is_end_frame:
            f_idx = c0_len - 1
            validate_target_opening_pose(staged[-1])
        elif snap_token_grid:
            f_idx = snap_still_token_frame(sec, fps=H3_FPS)
            if f_idx >= c0_len:
                f_idx = int(round(sec * H3_FPS))
        else:
            f_idx = int(round(sec * H3_FPS))
        if f_idx < 0 or f_idx >= c0_len:
            raise ValueError(f"AddGuide frame_idx {f_idx} is outside beat 1's sampled length ({c0_len} frames)")
        if used_frames and f_idx <= used_frames[-1]:
            raise ValueError(f"AddGuide frame_idx {f_idx} collides with prior pin at frame {used_frames[-1]}")
        used_frames.append(f_idx)
        graph[img_id] = {
            "_meta": {"title": "Start image (approved_characters)" if k == 1 and f_idx == 0 else f"Pinned image {k} at {sec:g}s"},
            "class_type": "LoadImage",
            "inputs": {"image": rel},
        }
        graph[guide_id] = {
            "_meta": {"title": "Frame-0 start image keyframe" if k == 1 and f_idx == 0 else f"Frame-{f_idx} keyframe ({sec:g}s)"},
            "class_type": "MiniMaxH3AddGuide",
            "inputs": {
                "positive": prev_cond,
                "latent": ["c0", 1],
                "vae": ["vvae", 0],
                "image": [img_id, 0],
                "frame_idx": f_idx,
            },
        }
        prev_cond = [guide_id, 0]
    graph["refapply"]["inputs"]["conditioning"] = prev_cond


def stage_reference_images(paths: Sequence[str], input_dir: Optional[Path] = None) -> List[str]:
    """U2: copy validated approved_characters images into ComfyUI input/community; returns 'community/<file>' names."""
    dest_dir = Path(input_dir) if input_dir else COMFY_INPUT_COMMUNITY
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = []
    for p in paths:
        src = Path(p)
        digest = hashlib.sha256(src.read_bytes()).hexdigest()[:10]
        stem = re.sub(r"[^A-Za-z0-9_-]+", "_", src.stem)[:60]
        name = f"parody_ref_{digest}_{stem}{src.suffix.lower()}"
        dst = dest_dir / name
        if not dst.exists():
            shutil.copyfile(src, dst)
        out.append(f"community/{name}")
    return out


def populate_refmod_slots(graph: Dict[str, Any], refmod_slots: Dict[str, Any]) -> None:
    """Populate exactly 8 slots in the MiniMaxH3RefModsLoader node."""
    if "refmods" not in graph or "inputs" not in graph["refmods"]:
        raise ValueError("Graph template lacks 'refmods' node with inputs.")

    inputs = graph["refmods"]["inputs"]
    for i in range(1, 9):
        slot_key = f"mod_{i}"
        strength_key = f"strength_{i}"
        copies_key = f"copies_{i}"

        slot_info = refmod_slots.get(slot_key, {})
        raw_path = slot_info.get("path", "(none)")
        strength = float(slot_info.get("strength", 1.0))
        copies = int(slot_info.get("copies", 1))

        if raw_path and raw_path != "(none)":
            mod_val = Path(raw_path).stem
        else:
            mod_val = "(none)"

        inputs[slot_key] = mod_val
        inputs[strength_key] = strength
        inputs[copies_key] = copies


def verify_keep_dials(graph: Dict[str, Any]) -> None:
    """Verify frozen KEEP dials on REF2VA 10strip eros beta7 int8HQ 8-step TURBO graph."""
    if "unet" not in graph:
        raise ValueError("Graph missing 'unet' node.")
    unet_name = graph["unet"]["inputs"].get("unet_name", "")
    if "10Eros_Max_h3_8stepTURBO_beta7_int8HQ" not in unet_name:
        raise ValueError(f"UNET dial drifted: expected 10Eros beta7 int8HQ, got {unet_name}")

    if "s0_sched" not in graph:
        raise ValueError("Graph missing 's0_sched' node.")
    steps = graph["s0_sched"]["inputs"].get("steps")
    if steps != 8:
        raise ValueError(f"Scheduler steps drifted: expected 8, got {steps}")

    if "refapply" not in graph:
        raise ValueError("Graph missing 'refapply' node.")


def _validate_continuation_place_transition(scene: Optional[str], prior_closer: Optional[Dict[str, str]],
                                            new_shot: bool = False) -> None:
    """argon-low C.4: two different places must be a C cut (`new_shot=True` or cut wording), never a same-space walk."""
    s = str(scene or "")
    if not s.strip():
        return
    prev_place = str((prior_closer or {}).get("place") or "").strip().lower()
    cur_places = [m.group(1).lower() for m in _PLACE_WORD_RE.finditer(s)]
    if not cur_places:
        return
    # Also detect two different places inside the same beat sentence ("walks from the bedroom into the kitchen")
    distinct_in_beat = list(dict.fromkeys(cur_places))
    has_walk = bool(_CONTINUATION_WALK_RE.search(s))
    has_cut = bool(new_shot or _CONTINUATION_CUT_RE.search(s))
    if len(distinct_in_beat) >= 2 and has_walk and not _CONTINUATION_CUT_RE.search(s):
        raise ValueError(
            f"continuation beat names two different places ({distinct_in_beat[0]!r} -> {distinct_in_beat[-1]!r}) "
            "as a walk: two different places must be a C 'new shot' cut, never a walk"
        )
    if prev_place and cur_places[0] != prev_place:
        if has_walk:
            raise ValueError(
                f"continuation beat changes room ({prev_place!r} -> {cur_places[0]!r}) with a walk verb: "
                "two different places must be a C 'new shot' cut, never a walk"
            )
        if not has_cut:
            raise ValueError(
                f"continuation beat changes room ({prev_place!r} -> {cur_places[0]!r}) without 'new_shot=True' or cut wording"
            )


def add_continuation_beat(cumulative: Dict[str, Any], beat: Dict[str, Any], layout: Dict[str, Any],
                          index: int, beat_guides: Optional[Sequence[Dict[str, Any]]] = None,
                          new_shot: bool = False) -> Dict[str, Any]:
    """(c) 2026-11-06 + argon-low C.3/C.4: wire one native latent-tail continuation beat into the cumulative graph.

    Node chain as installed and as scripts/comm.py:build wires it: GuidedContinuationWindow(previous, 22 hidden,
    +N) -> [optional AddGuide at frame_idx >= overlap_frames] -> LatentTailGuide -> BasicGuider +
    SamplerCustomAdvanced(window) -> AppendContinuation(overlap tokens, transition 0). The beat's RefModApply sits
    between its text node and the tail guide, as beat 1's does, so identity conditions every sampled beat. Only the
    appended latent reaches the decoders: one mp4, no stitching. `index` is the 1-based beat number.
    """
    if index < 2:
        raise ValueError(f"beat {index} is not a continuation: beat 1 is a single generation, index must be >= 2")
    for nid in (f"c{index}_gen", f"c{index}_append"):
        if nid in cumulative:
            raise ValueError(f"beat {index} is already wired in this graph ({nid}); beats are added in order")
    if index > 2 and f"c{index - 1}_append" not in cumulative:
        raise ValueError(f"beat {index} needs beat {index - 1}'s appended latent (c{index - 1}_append) first")
    for nid in ("c0", "refmods", "refapply"):
        if beat.get(nid, {}).get("class_type") != {"c0": "MiniMaxH3ReferenceToVideo",
                                                   "refmods": "MiniMaxH3RefModsLoader",
                                                   "refapply": "MiniMaxH3RefModApply"}[nid]:
            raise ValueError(f"template drift: beat graph is missing a plain '{nid}' node")
    overlap_f = int(layout["overlap_frames"])
    window_f = int(layout["window_frames"])
    # Reject any pre-existing frame-0 start image or guide inside the hidden overlap (< overlap_frames) on `beat`
    for node in beat.values():
        if node.get("class_type") == "MiniMaxH3AddGuide":
            f_idx = int((node.get("inputs") or {}).get("frame_idx", 0))
            if f_idx < overlap_f:
                raise ValueError("continuation beat must not carry the start image: the latent tail guides frame 0 "
                                 f"(guide at frame_idx={f_idx} is inside the {overlap_f}-frame hidden overlap)")
        elif node.get("class_type") == "LoadImage" and not beat_guides:
            raise ValueError("continuation beat must not carry the start image: the latent tail guides frame 0")
    if beat["refapply"]["inputs"].get("conditioning") != ["c0", 0]:
        raise ValueError("template drift: beat refapply.conditioning is not ['c0', 0]")
    # Beat 2 continues beat 1's SAMPLED AV latent: its SamplerCustomAdvanced (s0_samp) output 0, as the installed
    # guided_continuation.json wires all three previous_av_latent inputs; c0 output 1 is the UNSAMPLED latent.
    # Every later beat continues the latent its previous beat appended. The latent tail guides frame 0, so no
    # start photo is wired here.
    prev_latent = ["s0_samp", 0] if index == 2 else [f"c{index - 1}_append", 0]
    base = cumulative.get("c0", {}).get("inputs", {})
    if (base.get("width"), base.get("height"), base.get("fps")) != (
            beat["c0"]["inputs"].get("width"), beat["c0"]["inputs"].get("height"),
            beat["c0"]["inputs"].get("fps")):
        raise ValueError("canvas/fps drift between beats: the appended latent must be one continuous clip")
    if cumulative.get("refmods", {}).get("inputs") != beat["refmods"]["inputs"]:
        raise ValueError("RefMod drift between beats: every beat must carry the same identity RefMod")

    g = copy.deepcopy(cumulative)
    n = str(index)
    g[f"c{n}"] = copy.deepcopy(beat["c0"])
    g[f"c{n}"]["_meta"] = {"title": f"Beat {n}: continuation text and RefMod chain (no start photo)"}
    g[f"c{n}"]["inputs"]["length"] = [f"c{n}_gen", 1]  # the node docs: connect window_length to length
    g[f"c{n}_gen"] = {
        "_meta": {"title": f"Beat {n}: guided continuation window ({layout['overlap_frames']} hidden, "
                           f"+{layout['extension_frames']} new frames)"},
        "class_type": "MiniMaxH3GuidedContinuationWindow",
        "inputs": {"previous_av_latent": prev_latent, "overlap_frames": layout["overlap_frames"],
                   "extension_frames": layout["extension_frames"]},
    }
    # one RefMod load per graph, one RefModApply per beat, its mods link left on the shared loader
    g[f"c{n}_refapply"] = copy.deepcopy(beat["refapply"])
    g[f"c{n}_refapply"]["_meta"] = {"title": f"Beat {n}: RefMod retention 1.0 on the continuation beat"}
    g[f"c{n}_refapply"]["inputs"]["conditioning"] = [f"c{n}", 0]

    # argon-low C.3 (B) + C.4 (C): optional AddGuide keyframe(s) on the continuation beat at frame_idx >= overlap_frames
    tail_positive: List[Any] = [f"c{n}_refapply", 0]
    guides = list(beat_guides or [])
    if guides:
        prev_sec: Optional[float] = None
        for k, gs in enumerate(guides, start=1):
            raw_img = gs.get("image")
            if not raw_img or not str(raw_img).strip():
                raise ValueError(f"beat {n} guide {k} is missing 'image'")
            rel = str(raw_img).replace("\\", "/")
            if not rel.startswith("community/"):
                rel = "community/" + rel.split("/")[-1]
            if "frame_idx" in gs and gs["frame_idx"] is not None and "sec" not in gs:
                f_idx = int(gs["frame_idx"])
                if f_idx == -1:
                    f_idx = window_f - 1
                sec_new = (f_idx - overlap_f) / float(H3_FPS)
            else:
                if "sec" not in gs or gs["sec"] is None:
                    raise ValueError(f"beat {n} guide {k} requires 'sec' (seconds into the new part of the beat)")
                if _is_last_frame_spec(gs["sec"]):
                    f_idx = window_f - 1
                    sec_new = (f_idx - overlap_f) / float(H3_FPS)
                else:
                    sec_new = float(gs["sec"])
                    f_idx = overlap_f + int(round(sec_new * H3_FPS))
            if f_idx == window_f - 1:
                validate_target_opening_pose(rel)
            if f_idx < overlap_f or sec_new < -1e-9:
                raise ValueError(
                    f"beat {n} guide frame_idx {f_idx} (sec_into_new_part={sec_new:g}s) is inside the "
                    f"{overlap_f}-frame hidden overlap (must be >= {overlap_f})"
                )
            if f_idx >= window_f:
                raise ValueError(
                    f"beat {n} guide frame_idx {f_idx} (sec_into_new_part={sec_new:g}s) is outside window_frames={window_f}"
                )
            if k == 1:
                if new_shot:
                    if sec_new > (NEW_SHOT_MAX_PIN_SEC + 1e-9):
                        raise ValueError(
                            f"beat {n} is a 'new shot' (C mode) cut: first pin must be in the first "
                            f"{NEW_SHOT_MAX_PIN_SEC}s of the beat, got {sec_new:g}s"
                        )
                else:
                    if sec_new < (MIN_GUIDE_SEPARATION_SEC - 1e-9):
                        raise ValueError(
                            f"beat {n} is a continuing beat (B mode): pin at {sec_new:g}s is in the first "
                            f"{MIN_GUIDE_SEPARATION_SEC}s of the new part (pass new_shot=True for a C cut, or "
                            f"pin >= {MIN_GUIDE_SEPARATION_SEC}s into the beat so the tail transition settles)"
                        )
            if prev_sec is not None and (sec_new - prev_sec) < (MIN_GUIDE_SEPARATION_SEC - 1e-9):
                raise ValueError(
                    f"beat {n} guide pins {prev_sec:g}s and {sec_new:g}s are closer than {MIN_GUIDE_SEPARATION_SEC}s"
                )
            prev_sec = sec_new
            img_id = f"c{n}_img" if len(guides) == 1 else f"c{n}_img_{k}"
            guide_id = f"c{n}_guide" if k == 1 else f"c{n}_guide_{k}"
            g[img_id] = {
                "_meta": {"title": f"Beat {n}: guide image {k} ({sec_new:g}s into new part)"},
                "class_type": "LoadImage",
                "inputs": {"image": rel},
            }
            g[guide_id] = {
                "_meta": {"title": f"Beat {n}: AddGuide keyframe at window frame {f_idx}"},
                "class_type": "MiniMaxH3AddGuide",
                "inputs": {
                    "positive": tail_positive,
                    "latent": [f"c{n}_gen", 0],
                    "vae": ["vvae", 0],
                    "image": [img_id, 0],
                    "frame_idx": f_idx,
                },
            }
            tail_positive = [guide_id, 0]

    g[f"c{n}_tail"] = {
        "_meta": {"title": f"Beat {n}: native latent-tail guide (frame 0, no VAE round trip)"},
        "class_type": "MiniMaxH3LatentTailGuide",
        "inputs": {"positive": tail_positive, "previous_av_latent": prev_latent,
                   "target_av_latent": [f"c{n}_gen", 0], "overlap_video_tokens": [f"c{n}_gen", 2],
                   "overlap_audio_tokens": [f"c{n}_gen", 3]},
    }
    g[f"c{n}_sched"] = {"_meta": {"title": f"Beat {n}: KEEP 8 steps / simple scheduler"},
                        "class_type": "BasicScheduler",
                        "inputs": {"denoise": 1.0, "model": ["m_shift", 0], "scheduler": "simple", "steps": 8}}
    g[f"c{n}_guider"] = {"_meta": {"title": f"Beat {n}: guider on the RefMod'd, tail-guided conditioning"},
                         "class_type": "BasicGuider",
                         "inputs": {"conditioning": [f"c{n}_tail", 0], "model": ["m_shift", 0]}}
    g[f"c{n}_samp"] = {"_meta": {"title": f"Beat {n}: sample the window"},
                       "class_type": "SamplerCustomAdvanced",
                       "inputs": {"guider": [f"c{n}_guider", 0], "latent_image": [f"c{n}_gen", 0],
                                  "noise": ["noise", 0], "sampler": ["ksel", 0],
                                  "sigmas": [f"c{n}_sched", 0]}}
    g[f"c{n}_append"] = {
        "_meta": {"title": f"Beat {n}: trim the hidden overlap, append the new video and audio tokens"},
        "class_type": "MiniMaxH3AppendContinuation",
        "inputs": {"previous_av_latent": prev_latent, "sampled_window": [f"c{n}_samp", 0],
                   "overlap_video_tokens": [f"c{n}_gen", 2], "overlap_audio_tokens": [f"c{n}_gen", 3],
                   "transition_video_tokens": [f"c{n}_gen", 4], "transition_audio_tokens": [f"c{n}_gen", 5]},
    }
    if g.get("s0_sep", {}).get("class_type") != "LTXVSeparateAVLatent":
        raise ValueError("template drift: no s0_sep LTXVSeparateAVLatent to rewire to the appended latent")
    g["s0_sep"]["inputs"]["av_latent"] = [f"c{n}_append", 0]  # decoders/save stay as they are
    return g


def _layout_chain(requested_frames: Sequence[int], overlap_frames: int = CONTINUATION_OVERLAP_FRAMES) -> List[Dict[str, Any]]:
    """Lay out exactly these windows: one base generation, then one continuation window per entry.

    Entry 1 is the base single generation (capped at SINGLE_CLIP_MAX_FRAMES like any clip). Each later entry's
    base is the CUMULATIVE latent built so far - only the sampled window is capped, never the cumulative latent -
    and its extension is the length closest to what that entry asked for that both fits the window ceiling and
    joins on the audio grid. Every returned layout is exact; the caller wires them in order. Ties in that
    closest-length choice go to the LONGER extension: it lands nearer the total the caller asked for.
    """
    req = [int(x) for x in requested_frames]
    if len(req) < 2:
        raise ValueError("a continuation chain needs at least two beats")
    base = validate_single_clip_frames(req[0])
    plans: List[Dict[str, Any]] = [{"index": 1, "is_continuation": False, "frames": base}]
    cumulative = base
    cap_ext = CONTINUATION_WINDOW_MAX_FRAMES - overlap_frames
    for i, want in enumerate(req[1:], start=2):
        cum_target = cumulative + max(17, int(want))
        best: Optional[Tuple[Tuple[int, int], int]] = None
        for ext in range(cap_ext - cap_ext % 17, 16, -17):
            key = (abs(cumulative + ext - cum_target), -ext)
            if best is None or key < best[0]:
                best = (key, ext)
        if best is None:
            raise ValueError(
                f"no continuation from {cumulative} frames fits the {CONTINUATION_WINDOW_MAX_FRAMES} frame "
                f"sampled-window ceiling (largest extension {cap_ext} frames)"
            )
        layout = continuation_layout(cumulative, best[1], overlap_frames)
        plans.append({"index": i, "is_continuation": True, "frames": layout["total_frames"], "layout": layout})
        cumulative = layout["total_frames"]
    return plans


def map_clip_images_to_beats(
    staged: Sequence[str],
    image_times: Optional[Sequence[Any]],
    chain: Sequence[Dict[str, Any]],
    fps: int = H3_FPS,
) -> Tuple[List[str], List[float], Dict[int, List[Dict[str, Any]]]]:
    """Map clip-level `(staged, image_times)` onto Beat 1 `(images, image_times)` and Beat 2..N `beat_guides`.

    Beat 1 covers `[0, base_frames / fps)`. Beat `i` (`i >= 2`) covers `[prev_total / fps, cur_total / fps)` with
    `sec_into_new_part = clip_sec - (prev_total / fps)`. Fails closed if a later image has no time, if any time
    is outside `[0, total_seconds)`, or if two times are closer than `MIN_GUIDE_SEPARATION_SEC` (`0.5s`).
    Accepts `end`, `-1`, or `'-1'` as the last sampled frame of the clip.
    """
    n = len(staged)
    if n == 0:
        if image_times:
            raise ValueError("--image-at requires a matching --image (frame-0 start image first)")
        return [], [], {}
    total_frames = int(chain[-1]["frames"])
    last_clip_frame = total_frames - 1
    last_clip_sec = float(last_clip_frame) / float(fps)
    raw_items = list(image_times or [])
    if n == 1:
        if not raw_items:
            times = [0.0]
        elif len(raw_items) == 1:
            if _is_last_frame_spec(raw_items[0]):
                validate_target_opening_pose(staged[0])
                times = [last_clip_sec]
            else:
                try:
                    val = float(raw_items[0])
                except (ValueError, TypeError):
                    raise ValueError(f"invalid --image-at value: {raw_items[0]!r}")
                if abs(val) <= 1e-6:
                    times = [0.0]
                elif abs(val - last_clip_sec) <= 1e-6:
                    validate_target_opening_pose(staged[0])
                    times = [last_clip_sec]
                else:
                    raise ValueError(f"first --image must be the frame-0 start image (0.0s), got {val:g}s")
        else:
            raise ValueError(f"1 --image passed but {len(raw_items)} --image-at times given")
    else:
        if not raw_items:
            raise ValueError(
                "--image is the frame-0 start image (MiniMaxH3AddGuide): pass --image-at <sec> for each additional pin"
            )
        parsed_items: List[float] = []
        for idx, item in enumerate(raw_items):
            if _is_last_frame_spec(item):
                if idx != len(raw_items) - 1:
                    raise ValueError(f"--image-at {item!r} (last-frame pin) is only valid on the final pin")
                parsed_items.append(last_clip_sec)
            else:
                try:
                    parsed_items.append(float(item))
                except (ValueError, TypeError):
                    raise ValueError(f"invalid --image-at value: {item!r}")

        if len(parsed_items) == n - 1:
            times = [0.0] + parsed_items
        elif len(parsed_items) == n:
            if abs(parsed_items[0]) > 1e-6:
                raise ValueError(f"first --image must be the frame-0 start image (0.0s), got {parsed_items[0]:g}s")
            times = [0.0] + parsed_items[1:]
        else:
            raise ValueError(
                f"{n} --image paths require {n - 1} (or {n} including 0.0s) --image-at times; got {len(raw_items)}"
            )

    total_sec = total_frames / float(fps)
    for idx, t in enumerate(times):
        if t < 0.0 or t >= total_sec or int(round(t * fps)) >= total_frames:
            raise ValueError(
                f"--image-at {t:g}s (pin {idx + 1}) is outside the clip's total length ({total_frames}f / {total_sec:.3f}s)"
            )
        if idx > 0:
            if t <= times[idx - 1]:
                raise ValueError(f"--image-at times must be strictly increasing, got {times}")
            if (t - times[idx - 1]) < (MIN_GUIDE_SEPARATION_SEC - 1e-9):
                raise ValueError(
                    f"--image-at pins {times[idx - 1]:g}s and {t:g}s are closer than {MIN_GUIDE_SEPARATION_SEC}s"
                )

    if times and abs(times[-1] - last_clip_sec) < 1e-6:
        validate_target_opening_pose(staged[-1])

    base_frames = int(chain[0]["frames"])
    base_sec = base_frames / float(fps)
    b1_imgs: List[str] = []
    b1_times: List[float] = []
    beat_guides: Dict[int, List[Dict[str, Any]]] = {}
    for img, t in zip(staged, times):
        if t < base_sec and int(round(t * fps)) < base_frames:
            b1_imgs.append(img)
            b1_times.append(t)
            continue
        placed = False
        prev_f = base_frames
        for step in chain[1:]:
            b_idx = int(step["index"])
            cur_f = int(step["frames"])
            start_s = prev_f / float(fps)
            end_s = cur_f / float(fps)
            if t < end_s and int(round(t * fps)) < cur_f:
                sec_into = max(0.0, round(t - start_s, 6))
                beat_guides.setdefault(b_idx, []).append({"image": img, "sec": sec_into, "clip_sec": t})
                placed = True
                break
            prev_f = cur_f
        if not placed:
            raise ValueError(f"--image-at {t:g}s could not be mapped to any beat in chain (total {total_sec:.3f}s)")
    return b1_imgs, b1_times, beat_guides


def build_continuation_request(resolved: Dict[str, Any], seed: int, prefix: str, beats: Sequence[Dict[str, Any]],
                              frames: Optional[int] = None, overlap_frames: int = CONTINUATION_OVERLAP_FRAMES,
                              **kwargs: Any) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """(c) 2026-11-06 (brief t224x214) + argon-low Section C: one graph, N beats, native latent-tail continuation.

    Beat 1 carries the start photo (plus any Beat-1 timed AddGuide pins) and its own frames; every later beat
    continues the cumulative latent, has no frame-0 start photo (though it may carry `beat_guides` at
    `frame_idx >= overlap_frames`), and re-applies its RefMod conditioning. A beat spec is `{scene, dialogue,
    camera, frames, pronoun, end_action, images, image_times, beat_guides, new_shot, summary_text}`; `frames` is
    the beat-1 default. kwargs go to every beat's prompt build (shared dials: image_role, resolved2, pronoun2,
    lighting, ...).

    Returns `(graph, prompt_all, plan)` with the exact frame math per beat in `plan["beats"]`.
    """
    if not beats:
        raise ValueError("no beats to build")
    if len(beats) == 1:
        raise ValueError("one beat is a single shot: use build_parody_request")
    # kwargs are the shared dials the caller wants applied to every beat (pronoun, image_role, lighting, ...);
    # a beat spec overrides them for its own beat. No key is ever passed to the single-beat builder twice.
    shared = dict(kwargs)
    shared.update({k: v for k, v in beats[0].items() if v is not None and k not in ("beat_guides", "new_shot")})
    shared.setdefault("frames", frames)
    req_frames = [
        int(b.get("frames") or shared.get("frames") or DEFAULT_CONTINUATION_BASE_FRAMES)
        for b in beats
    ]
    chain = _layout_chain(req_frames, overlap_frames)
    graph, first_prompt = build_parody_request(
        resolved, seed=seed, prefix=prefix, frames=chain[0]["frames"],
        **{k: v for k, v in shared.items() if k not in ("frames", "beat_guides", "new_shot")})
    prompts = [first_prompt]
    plan: List[Dict[str, Any]] = [chain[0]]
    for i, step in enumerate(chain[1:], start=2):
        b_spec = beats[i - 1]
        new_shot = bool(b_spec.get("new_shot", False))
        b_guides = b_spec.get("beat_guides")
        beat_kwargs = {k: v for k, v in shared.items() if k not in ("frames", "images", "image_times", "beat_guides", "new_shot")}
        beat_kwargs.update({k: v for k, v in b_spec.items() if v is not None and k not in ("beat_guides", "images", "image_times")})
        beat_kwargs.update(continuation=True, images=None, image_times=None, frames=step["layout"]["window_frames"],
                           prior_closer=beat_closer(beats[i - 2], beat_kwargs.get("pronoun")),
                           new_shot=new_shot)
        beat_graph, prompt = build_parody_request(resolved, seed=seed, prefix=prefix, **beat_kwargs)
        graph = add_continuation_beat(graph, beat_graph, step["layout"], i, beat_guides=b_guides, new_shot=new_shot)
        step_info = dict(step)
        if new_shot:
            step_info["new_shot"] = True
        if b_guides:
            step_info["beat_guides"] = list(b_guides)
        plan.append(step_info)
        prompts.append(prompt)
    prompt_all = "\n\n".join(f"===== beat {k} =====\n{p}" for k, p in enumerate(prompts, start=1))
    total = plan[-1]["frames"]
    return graph, prompt_all, {
        "mode": "native_latent_tail_continuation",
        "clip_count": len(plan),
        "beats": plan,
        "total_frames": total,
        "total_seconds": round(total / H3_FPS, 4),
        "fps": H3_FPS,
        "stitched": False,
    }


def build_parody_request(
    resolved: Dict[str, Any],
    seed: int,
    prefix: str,
    frames: int = 124,
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
    template_path: Path = DEFAULT_REFMOD_TEMPLATE,
    width: Optional[int] = None,
    height: Optional[int] = None,
    camera: Optional[str] = None,
    pronoun: Optional[str] = None,
    end_action: Optional[str] = None,
    summary_text: Optional[str] = None,
    images: Optional[Sequence[str]] = None,
    image_role: Optional[str] = None,
    resolved2: Optional[Dict[str, Any]] = None,
    dialogue2: Optional[str] = None,
    pronoun2: Optional[str] = None,
    lighting: Optional[str] = None,
    continuation: bool = False,
    ambience: Optional[str] = None,
    prior_closer: Optional[Dict[str, str]] = None,
    image_times: Optional[Sequence[Any]] = None,
    new_shot: bool = False,
    frame_indices: Optional[Sequence[int]] = None,
    partner_type: Optional[str] = None,
    resolved3: Optional[Dict[str, Any]] = None,
    dialogue3: Optional[str] = None,
    pronoun3: Optional[str] = None,
    partner_type2: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Build request API graph and prompt text for a parody run (one clip / one cell).

    `images` are already-staged ComfyUI input names ('community/<file>'). The template on disk is never written.
    `continuation=True` builds a beat that continues a completed latent: the scene text inherits the previous
    beat's closing state and the start photo is refused (the latent tail guides frame 0).

    Returns:
        (graph_dict, prompt_str)
    """
    frames = validate_single_clip_frames(frames)
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    if continuation:
        if images:
            raise ValueError("a continuation beat has no start image: the latent tail guides frame 0 "
                             "(MiniMaxH3LatentTailGuide rejects any guide inside the overlap)")
        _validate_continuation_place_transition(scene, prior_closer, new_shot=new_shot)
        scene = continuation_scene(scene, pronoun, closer=prior_closer, camera=camera, new_shot=new_shot)

    staged = list(images or [])
    prompt = format_parody_prompt(
        resolved, dialogue=dialogue, scene=scene, audio_ref=audio_ref, lighting=lighting,
        camera=camera, pronoun=pronoun, end_action=end_action, summary_text=summary_text,
        image_count=len(staged), image_role=image_role,
        resolved2=resolved2, dialogue2=dialogue2, pronoun2=pronoun2, ambience=ambience,
        resolved3=resolved3, dialogue3=dialogue3, pronoun3=pronoun3,
    )

    # Use make_b2_request.build as foundation
    graph = make_b2_build(
        tpl,
        prompt=prompt,
        seed=seed,
        prefix=prefix,
        frames=frames,
        refmod=None,  # We will populate all 8 slots explicitly below
        lora=None,
    )

    if width or height:
        w, h = int(width or DEFAULT_CANVAS[0]), int(height or DEFAULT_CANVAS[1])
        graph["c0"]["inputs"]["width"] = w
        graph["c0"]["inputs"]["height"] = h

    # Populate all 8 slots from resolved (S1, plus S2/S3 merged)
    pt = str(partner_type or "").lower()
    pt2 = str(partner_type2 or "").lower()
    if resolved3 is not None:
        slots = merge_refmod_slots(
            resolved.get("refmod_slots", {}),
            (resolved2 or {}).get("refmod_slots"),
            (resolved3 or {}).get("refmod_slots"),
            three_person=True,
            partner_types=[pt or "man", pt2 or "man"]
        )
    elif pt in ("none", "non-human", "faceless"):
        slots = resolved.get("refmod_slots", {})
    else:
        slots = merge_refmod_slots(resolved.get("refmod_slots", {}), (resolved2 or {}).get("refmod_slots")) \
            if resolved2 is not None else resolved.get("refmod_slots", {})
    populate_refmod_slots(graph, slots)

    inject_reference_images(graph, staged, image_times=image_times, frames=frames, frame_indices=frame_indices)

    # Verify KEEP dials
    verify_keep_dials(graph)

    return graph, prompt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build H3 parody request graph")
    parser.add_argument("--arm-dir", required=True, help="Directory to write request.api.json and prompt.txt")
    parser.add_argument("--seed", type=int, default=51083601, help="Noise seed")
    parser.add_argument("--prefix", required=True, help="Filename prefix, e.g. community/parody_01/clip_01")
    parser.add_argument("--frames", type=int, default=None, help="Total frames (H3 grid (f-5)%%17==0, max 243)")
    parser.add_argument("--seconds", type=float, help="Clip length in seconds (snapped onto the H3 grid)")
    parser.add_argument("--dialogue", help="Optional spoken line")
    parser.add_argument("--scene", help="Optional scene (rich, multi-sentence welcome; never truncated)")
    parser.add_argument("--summary", help="Optional short summary line (default: first sentence of --scene)")
    parser.add_argument("--camera", help="Camera framing/motion (default static medium shot, 50mm)")
    parser.add_argument("--aspect", help="9:16 (default), 16:9, 1:1, 4:3, 3:4, portrait, landscape, widescreen, square")
    parser.add_argument("--size", help="Explicit canvas WxH (multiples of 32, 256..2048)")
    parser.add_argument("--pronoun", default="she", choices=["she", "he", "they"])
    parser.add_argument("--ambience", help="Soundscape ambience phrase (default: quiet room ambience, soft natural room tone)")
    parser.add_argument("--end-action", help="What the subject does as the line ends")
    parser.add_argument("--image", action="append", default=[],
                        help="approved_characters reference image (frame-0 start image first; pass --image-at <sec> for each additional pin)")
    parser.add_argument("--image-at", action="append", type=_parse_image_at_arg, default=[],
                        help="Clip time in seconds for each additional --image pin (at least 0.5s apart, within beat 1 length; accept -1 or 'end' for last frame)")
    parser.add_argument("--image-role", default=DEFAULT_IMAGE_ROLE)
    parser.add_argument("--template", default=str(DEFAULT_REFMOD_TEMPLATE), help="Template JSON path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    # Request specification args
    parser.add_argument("--name", action="append", dest="names", help="Subject name(s)")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True, help="Biometric/wardrobe description")
    parser.add_argument("--tone", default="parody", help="Tone (parody, adult, etc.)")
    parser.add_argument("--name3", help="Third subject name")
    parser.add_argument("--character3", help="Third character name")
    parser.add_argument("--actor3", help="Third actor name")
    parser.add_argument("--description3", help="Third subject biometric/wardrobe description")
    parser.add_argument("--dialogue3", help="Third subject spoken words only")
    parser.add_argument("--pronoun3", default="she", choices=["she", "he", "they"])

    args = parser.parse_args(argv)

    # Import resolve from same package
    from resolve import resolve_identities, validate_reference_images
    index_dir = Path(r"C:\AI\community\index\h3-known-characters")
    refmods_dir = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
    aliases_path = Path(__file__).parent / "aliases.json"

    if args.frames is not None:
        frames = args.frames
    elif args.seconds is not None:
        frames = snap_h3_frames(args.seconds, max_frames=SINGLE_CLIP_MAX_FRAMES)
    else:
        frames = 124
    w, h = resolve_canvas(args.aspect, args.size)

    req_dict = {
        "names": args.names or [],
        "character": args.character,
        "actor": args.actor,
        "tone": args.tone,
        "length_s": int(frames / 24),
        "description": args.description,
    }

    resolved = resolve_identities(
        req_dict,
        index_dir=index_dir,
        refmods_dir=refmods_dir,
        aliases_path=aliases_path,
    )
    resolved3 = None
    if args.name3 or args.character3 or args.actor3:
        req_dict3 = {
            "names": [args.name3] if args.name3 else [],
            "character": args.character3,
            "actor": args.actor3,
            "tone": args.tone,
            "length_s": int(frames / 24),
            "description": args.description3 or "",
        }
        resolved3 = resolve_identities(
            req_dict3,
            index_dir=index_dir,
            refmods_dir=refmods_dir,
            aliases_path=aliases_path,
        )
    staged = stage_reference_images(validate_reference_images(args.image)) if args.image else []

    graph, prompt = build_parody_request(
        resolved=resolved,
        seed=args.seed,
        prefix=args.prefix,
        frames=frames,
        dialogue=args.dialogue,
        scene=args.scene,
        template_path=Path(args.template),
        width=w,
        height=h,
        camera=args.camera,
        pronoun=args.pronoun,
        end_action=args.end_action,
        summary_text=args.summary,
        images=staged,
        image_role=args.image_role,
        ambience=args.ambience,
        image_times=args.image_at,
        resolved3=resolved3,
        dialogue3=args.dialogue3,
        pronoun3=args.pronoun3,
    )

    arm_dir = Path(args.arm_dir)
    arm_dir.mkdir(parents=True, exist_ok=True)

    req_file = arm_dir / "request.api.json"
    prompt_file = arm_dir / "prompt.txt"

    if req_file.exists() and not args.force:
        print(f"Error: {req_file} exists (use --force)", file=sys.stderr)
        return 3

    req_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"Wrote {req_file} and {prompt_file} (frames={frames}, size={w}x{h}, seed={args.seed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
