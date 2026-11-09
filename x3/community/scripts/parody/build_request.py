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

# Add community scripts to path for make_b2_request and comm
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as make_b2_build

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
STATIC_CAMERA_TAIL = "Camera locked off, no zoom, no pan."
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
CONTINUATION_NODE_TYPES = frozenset({
    "MiniMaxH3GuidedContinuationWindow",
    "MiniMaxH3LatentTailGuide",
    "MiniMaxH3AppendContinuation",
})
# Prompt rule for a continuation beat: inherit the previous beat's closing state, never reset to the photo.
CONTINUATION_LEAD_IN = (
    "The shot continues from the last seen moment: the same framing, the same standing pose, the same "
    "wardrobe and the same room lighting, and {sub} is still in the same place at the same distance from "
    "the camera. At first there is only natural micro-motion - a breath, a slow blink, a small shift of "
    "weight - before this action. {Sub} keeps {poss} exact voice, accent and signature vocal timbre. "
    "The camera does not change angle and the shot never resets to a starting photo."
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
def continuation_layout(base_frames: int, extension_frames: int,
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


def continuation_scene(scene: Optional[str], pronoun: Optional[str] = None) -> str:
    """Continuation-beat scene text: the inherited closing state first, then the caller's action."""
    pr = _pronoun(pronoun)
    lead = CONTINUATION_LEAD_IN.format(sub=pr["subj"].lower(), Sub=pr["subj"], poss=pr["poss"])
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
    use = "use" if S == "They" else "uses"
    vt = voice_target or "their exact voice"
    if spoken:
        if end_action:
            first = f"{_format_end_action(S, end_action)}. "
        else:
            first = f"{S} hold{s} eye contact, give{s} a small nod at the end, and stop{s} talking. "
        return (
            f"{pre}{first}{Poss} mouth movements stop completely after the sentence. "
            f"{S} {use} {vt}, accent, and signature vocal timbre consistently throughout the entire clip."
        )
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
    if two:
        name2, voice2 = _subject_name(resolved2)
        desc2 = _ensure_vocal_timbre(_subject_desc(resolved2, name2))
        vt2 = _voice_target(resolved2, voice2)
        pr2 = _pronoun(pronoun2)
    spoken = validate_spoken_dialogue(dialogue)
    spoken2 = validate_spoken_dialogue(dialogue2) if two else None

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
    cam_tail = "" if camera_moves(cam) else f" {STATIC_CAMERA_TAIL}"

    audio_timbre_line = "\n<Audio 1> is the voice-timbre reference for <Subject 1>." if audio_ref else ""

    subj_lines = f"(S1) {primary_name} - an adult performer, age 28+, {desc}{audio_timbre_line}"
    if two:
        subj_lines += f"\n(S2) {name2} - an adult performer, age 28+, {desc2}"

    silent = []
    if not spoken:
        silent.append("(S1)")
    if two and not spoken2:
        silent.append("(S2)")
    non_speaking = ", ".join(silent) if silent else "none"

    label1 = "(S1)" if two else ""
    blocks = []
    d_lines = []
    if spoken:
        d_lines.append(f"(S1): <d>[English, using {vt1} and signature vocal timbre] {spoken}</d>")
    if spoken2:
        d_lines.append(f"(S2): <d>[English, using {vt2} and signature vocal timbre] {spoken2}</d>")
    if d_lines:
        blocks.append("<scenedirect>\n" + "\n".join(d_lines) + "\n</scenedirect>")
    blocks.append(_speaker_lines(label1, pr1, spoken, end_action, voice_target=vt1))
    if two:
        blocks.append(_speaker_lines("(S2)", pr2, spoken2, None, voice_target=vt2))
    speech_block = "\n".join(blocks)

    n_voices = int(bool(spoken)) + int(bool(spoken2))
    amb = (ambience or "").strip().rstrip(".;,") or "quiet room ambience, soft natural room tone"
    if n_voices == 2:
        voice_line = (f"{amb}; two close-micd human voices in the foreground, "
                      "one speaker at a time.")
    elif n_voices == 1:
        voice_line = f"{amb}; the single close-micd human voice in the foreground."
    else:
        voice_line = f"{amb}; no spoken voice."

    s_prefix = "" if two else "(S1) "

    prompt = f"""subject_definitions:
{subj_lines}

summary:
{s_prefix}{scene_summary}. Non-speaking characters: {non_speaking}. No singing, no rapping, no songs, no music, no narration, no voice-over.

detailed_description:
[{cam}]
{s_prefix}{scene_line}.{cam_tail}
{speech_block}

overall_soundscape:
{voice_line}
no_dubs: no extra dubbing, no studio VO, no dubbing actors, no voice actors.
No music, no songs, no score, no soundtrack."""

    # Validate against adults guard (guard_ok + an adult statement, same as run_queue's gate)
    if not comm.guard_ok(prompt) or not comm.adult_stated(prompt):
        raise ValueError(f"Prompt failed comm.guard_ok check:\n{prompt}")

    return prompt


def merge_refmod_slots(slots1: Dict[str, Any], slots2: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """U4: up to 4 S1 + 4 S2 RefMods into mod_1..mod_8 (spare slots go to whichever subject has more)."""
    def live(slots):
        out = []
        for i in range(1, 9):
            info = (slots or {}).get(f"mod_{i}", {})
            if info.get("path") and info.get("path") != "(none)":
                out.append(dict(info))
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


def inject_reference_images(graph: Dict[str, Any], staged: Sequence[str]) -> None:
    """U2 (t289u): the --image start frame is a MiniMaxH3AddGuide keyframe at frame_idx 0 (in-memory graph only).

    img_1 LoadImage -> add_guide(positive=c0.0, latent=c0.1, vae=vvae, image=img_1, frame_idx=0), and the
    conditioning chain becomes c0 -> add_guide -> refapply -> s0_guide. c0 gets NO ref_images input, so Qwen
    encodes text only and minimax_refs belong to the RefMod(s); RefModApply copies the conditioning dict, so
    the minimax_keyframes set here survive it. One start image per clip: more than one fails closed.
    """
    if not staged:
        return
    if len(staged) > 1:
        raise ValueError("--image is the frame-0 start image (MiniMaxH3AddGuide): pass exactly one per clip")
    if graph.get("refapply", {}).get("inputs", {}).get("conditioning") != ["c0", 0]:
        raise ValueError("template drift: refapply.conditioning is not ['c0', 0]; refusing to wire add_guide")
    rel = str(staged[0]).replace("\\", "/")
    if not rel.startswith("community/"):
        rel = "community/" + rel.split("/")[-1]
    graph["img_1"] = {"_meta": {"title": "Start image (approved_characters)"},
                      "class_type": "LoadImage", "inputs": {"image": rel}}
    graph["add_guide"] = {"_meta": {"title": "Frame-0 start image keyframe"},
                          "class_type": "MiniMaxH3AddGuide",
                          "inputs": {"positive": ["c0", 0], "latent": ["c0", 1], "vae": ["vvae", 0],
                                     "image": ["img_1", 0], "frame_idx": 0}}
    graph["refapply"]["inputs"]["conditioning"] = ["add_guide", 0]


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


def add_continuation_beat(cumulative: Dict[str, Any], beat: Dict[str, Any], layout: Dict[str, Any],
                          index: int) -> Dict[str, Any]:
    """(c) 2026-11-06: wire one native latent-tail continuation beat into the cumulative graph.

    Node chain as installed and as scripts/comm.py:build wires it: GuidedContinuationWindow(previous, 22 hidden,
    +N) -> LatentTailGuide -> BasicGuider + SamplerCustomAdvanced(window) -> AppendContinuation(overlap tokens,
    transition 0). The beat's RefModApply sits between its text node and the tail guide, as beat 1's does, so
    identity conditions every sampled beat. Only the appended latent reaches the decoders: one mp4, no stitching.
    `index` is the 1-based beat number.
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
    if any(n.get("class_type") in ("MiniMaxH3AddGuide", "LoadImage") for n in beat.values()):
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
    g[f"c{n}_tail"] = {
        "_meta": {"title": f"Beat {n}: native latent-tail guide (frame 0, no VAE round trip)"},
        "class_type": "MiniMaxH3LatentTailGuide",
        "inputs": {"positive": [f"c{n}_refapply", 0], "previous_av_latent": prev_latent,
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


def _split_frames(total: int, parts: int) -> List[int]:
    """Split `total` frames over `parts` windows as evenly as whole frames allow (largest remainder first)."""
    if parts <= 0:
        return []
    base, rem = divmod(int(total), parts)
    return [base + (1 if i < rem else 0) for i in range(parts) if base + (1 if i < rem else 0) > 0]


def plan_beat_windows(beats_frames: Sequence[float], base_max_frames: Optional[int] = None,
                      overlap_frames: int = CONTINUATION_OVERLAP_FRAMES) -> Dict[str, Any]:
    """(F1 2026-11-08) Duration-honouring window plan for a native continuation chain.

    Why: one window per beat silently clamped long beats. No continuation window can add more than
    CONTINUATION_WINDOW_MAX_FRAMES - overlap_frames new frames, so a 60 s ask over 2 beats asked for 2 x 30 s
    and produced 243 + 221 = 464 f (19.33 s). The installed nodes already repeat the native continuation
    window to grow one clip (the 1348 f / 56.17 s and 566 f / 23.58 s runs are that mechanism), so a beat
    that needs more time is served by REPEATING that window - never by clamping the beat, never by a second
    stitched clip, and with no new node, input, flag, gate, script, graph, model, sampler, seed, size, fps,
    voice reference, RefLoRA, 2-pass, post-pass, prompt rule, or test harness.

    `beats_frames` is what each beat was ASKED for, in frames (unclamped: a 30 s beat is 720/24 = 360 f, not
    243 f). Beat order and meaning are kept: window 1 is beat 1's base generation, every later window belongs
    to one named beat, in beat order.

    The rule, from the installed caps only: a beat gets one window per the time it asks for - beat 1 opens
    with its base generation (capped at the single-clip ceiling like any clip) plus ceil(left / cap_ext)
    continuation windows, every later beat ceil(ask / cap_ext), where cap_ext =
    CONTINUATION_WINDOW_MAX_FRAMES - overlap_frames (221 f at stock overlap), and a left under one grid step
    (17 f) needs no window at all because the base window's own grid rounding covers it. The frames a beat
    asks for are split evenly over its windows (_split_frames); no window's ask exceeds cap_ext, and the base
    window is grid-snapped through the existing single-clip path. _layout_chain then rounds each window with
    snap_h3_frames/continuation_layout's existing nearest-grid search, so the reported total is the actual
    CUMULATIVE legal H3 grid (e.g. 708 f for 60 s over 2 beats), never a chosen frame count like 1433f.
    Every ask needs at least one window per beat, so a 2 x 8 s (379 f) or 3 x 8 s (566 f) ask keeps its
    validated one-window-per-beat shape exactly.

    Returns {"windows": [{"beat_index", "beat_number", "is_base", "want_frames"}], "chain": the layout of
    those windows, "requested_total_frames", "windows_per_beat", "base_max_frames", "window_max_frames",
    "overlap_frames", "fps"}.
    """
    cap_base = min(int(base_max_frames if base_max_frames is not None else SINGLE_CLIP_MAX_FRAMES),
                   H3_HARD_MAX_FRAMES)
    cap_base = snap_h3_frames(cap_base / float(H3_FPS), max_frames=cap_base)  # base ceiling, on-grid (243)
    cap_ext = CONTINUATION_WINDOW_MAX_FRAMES - int(overlap_frames)            # new frames per later window (221)
    if cap_ext < 17:
        raise ValueError("overlap leaves no room for a continuation window")
    asks = [max(H3_MIN_FRAMES, int(round(float(x)))) for x in beats_frames]
    if not asks:
        raise ValueError("no beats to plan")

    windows: List[Dict[str, Any]] = []
    windows_per_beat: List[int] = []
    for i, ask in enumerate(asks):
        left = ask
        if not windows:   # beat 1 opens with the base single generation, capped and grid-snapped like any clip
            base = snap_h3_frames(min(ask, cap_base) / float(H3_FPS), max_frames=cap_base)
            windows.append({"beat_index": i, "beat_number": i + 1, "is_base": True, "want_frames": base})
            left = ask - base
        # a leftover below one grid step (17 f) is already covered by the base window's own grid rounding,
        # so it needs no extra window: the pre-F1 one-window-per-beat shape is kept exactly.
        repeats = (left + cap_ext - 1) // cap_ext if left >= 17 else 0
        for frames in _split_frames(left, repeats):
            windows.append({"beat_index": i, "beat_number": i + 1, "is_base": False, "want_frames": frames})
        windows_per_beat.append(1 + repeats)
    return {"windows": windows, "requested_total_frames": sum(asks), "windows_per_beat": windows_per_beat,
            "chain": _layout_chain([w["want_frames"] for w in windows], overlap_frames),
            "base_max_frames": cap_base, "window_max_frames": CONTINUATION_WINDOW_MAX_FRAMES,
            "overlap_frames": int(overlap_frames), "fps": H3_FPS}


def plan_continuation_chain(requested_frames: Sequence[int],
                            overlap_frames: int = CONTINUATION_OVERLAP_FRAMES) -> List[Dict[str, Any]]:
    """Frame plan for N beats in one graph: one native generation, then one continuation window per extra beat.

    Beat 1 is a normal single generation (its length is capped at SINGLE_CLIP_MAX_FRAMES like any clip). Each
    later beat's base is the CUMULATIVE latent built so far - only the sampled window is capped, never the
    cumulative latent - and its extension is the length closest to what that beat asked for that both fits the
    window ceiling and joins on the audio grid. Every returned layout is exact; the caller wires them in order.
    Ties in that closest-length choice go to the LONGER extension: it lands nearer the total the caller asked for.

    F1 (2026-11-08): a 2-entry request is read as what its two beats ASKED for, and plan_beat_windows gives
    each of them the windows its length needs by repeating the installed native continuation window (the 60 s
    / 2-beat ask that used to come out as 243 + 221 = 464 f now gets the windows that carry it). Only that
    2-entry form is expanded: 3+ entries already mean "one window per beat" (a 6 x 243 f request reaches
    1348 f = 56.17 s, the shape the 2026-11-07 run proved), and plan_cells asks for its windows explicitly,
    so a caller that planned its own windows is never re-planned. The cumulative latent is never capped; only
    the sampled window is.
    """
    req = [int(x) for x in requested_frames]
    if len(req) < 2:
        raise ValueError("a continuation chain needs at least two beats")
    if len(req) == 2 and int(overlap_frames) == CONTINUATION_OVERLAP_FRAMES:
        # F1: honour the requested length by repeating the native window (see plan_beat_windows) instead of
        # clamping the request to what one base + one continuation window can sample.
        _plan = plan_beat_windows(req, overlap_frames=overlap_frames)
        if len(_plan["windows"]) > len(req):
            req = [w["want_frames"] for w in _plan["windows"]]
    return _layout_chain(req, overlap_frames)


def build_continuation_request(resolved: Dict[str, Any], seed: int, prefix: str, beats: Sequence[Dict[str, Any]],
                              frames: Optional[int] = None, overlap_frames: int = CONTINUATION_OVERLAP_FRAMES,
                              **kwargs) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """(c) 2026-11-06 (brief t224x214): one graph, N beats, native latent-tail continuation, no concatenation.

    Beat 1 carries the start photo and its own frames; every later beat continues the cumulative latent, has no
    start photo, and re-applies its RefMod conditioning. A beat spec is {scene, dialogue, camera, frames,
    pronoun, end_action, images, summary_text}; `frames` is the beat-1 default. kwargs go to every beat's prompt
    build (shared dials: image_role, resolved2, pronoun2, lighting, ...).

    Returns (graph, prompt_all, plan) with the exact frame math per beat in plan["beats"].
    """
    if not beats:
        raise ValueError("no beats to build")
    if len(beats) == 1:
        raise ValueError("one beat is a single shot: use build_parody_request")
    # kwargs are the shared dials the caller wants applied to every beat (pronoun, image_role, lighting, ...);
    # a beat spec overrides them for its own beat. No key is ever passed to the single-beat builder twice.
    shared = dict(kwargs)
    shared.update({k: v for k, v in beats[0].items() if v is not None})
    shared.setdefault("frames", frames)
    chain = plan_continuation_chain([int(b.get("frames") or shared["frames"]) for b in beats], overlap_frames)
    graph, first_prompt = build_parody_request(
        resolved, seed=seed, prefix=prefix, frames=chain[0]["frames"],
        **{k: v for k, v in shared.items() if k != "frames"})
    prompts = [first_prompt]
    plan: List[Dict[str, Any]] = [chain[0]]
    # More windows than scenes means the last scene text keeps running (same as the shared-anchor path).
    for i, step in enumerate(chain[1:], start=2):
        beat_kwargs = {k: v for k, v in shared.items() if k not in ("frames", "images")}
        beat_kwargs.update({k: v for k, v in beats[min(i - 1, len(beats) - 1)].items() if v is not None})
        beat_kwargs.update(continuation=True, images=None, frames=step["layout"]["window_frames"])
        beat_graph, prompt = build_parody_request(resolved, seed=seed, prefix=prefix, **beat_kwargs)
        graph = add_continuation_beat(graph, beat_graph, step["layout"], i)
        plan.append(step)
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
        scene = continuation_scene(scene, pronoun)

    staged = list(images or [])
    prompt = format_parody_prompt(
        resolved, dialogue=dialogue, scene=scene, audio_ref=audio_ref, lighting=lighting,
        camera=camera, pronoun=pronoun, end_action=end_action, summary_text=summary_text,
        image_count=len(staged), image_role=image_role,
        resolved2=resolved2, dialogue2=dialogue2, pronoun2=pronoun2, ambience=ambience,
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

    # Populate all 8 slots from resolved (S1, plus S2 merged 4+4)
    slots = merge_refmod_slots(resolved.get("refmod_slots", {}), (resolved2 or {}).get("refmod_slots")) \
        if resolved2 is not None else resolved.get("refmod_slots", {})
    populate_refmod_slots(graph, slots)

    inject_reference_images(graph, staged)

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
    parser.add_argument("--image", action="append", default=[], help="Optional single approved_characters start image (AddGuide frame 0; more than one is rejected)")
    parser.add_argument("--image-role", default=DEFAULT_IMAGE_ROLE)
    parser.add_argument("--template", default=str(DEFAULT_REFMOD_TEMPLATE), help="Template JSON path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    # Request specification args
    parser.add_argument("--name", action="append", dest="names", help="Subject name(s)")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True, help="Biometric/wardrobe description")
    parser.add_argument("--tone", default="parody", help="Tone (parody, adult, etc.)")

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
