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
    if n_voices == 2:
        voice_line = ("quiet room ambience, soft natural room tone; two close-micd human voices in the foreground, "
                      "one speaker at a time.")
    elif n_voices == 1:
        voice_line = "quiet room ambience, soft natural room tone; the single close-micd human voice in the foreground."
    else:
        voice_line = "quiet room ambience, soft natural room tone; no spoken voice."

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
) -> Tuple[Dict[str, Any], str]:
    """Build request API graph and prompt text for a parody run (one clip / one cell).

    `images` are already-staged ComfyUI input names ('community/<file>'). The template on disk is never written.

    Returns:
        (graph_dict, prompt_str)
    """
    frames = validate_single_clip_frames(frames)
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    staged = list(images or [])
    prompt = format_parody_prompt(
        resolved, dialogue=dialogue, scene=scene, audio_ref=audio_ref, lighting=lighting,
        camera=camera, pronoun=pronoun, end_action=end_action, summary_text=summary_text,
        image_count=len(staged), image_role=image_role,
        resolved2=resolved2, dialogue2=dialogue2, pronoun2=pronoun2,
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
    parser.add_argument("--end-action", help="What the subject does as the line ends")
    parser.add_argument("--image", action="append", default=[], help="approved_characters reference image (1..4)")
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
