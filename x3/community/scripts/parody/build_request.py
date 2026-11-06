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
from typing import Any, Dict, List, Optional

# Add community scripts to path for make_b2_request and comm
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as make_b2_build

DEFAULT_REFMOD_TEMPLATE = Path(r"C:\AI\community\templates\b2_refmod.api.json")


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


def format_parody_prompt(
    resolved: Dict[str, Any],
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
    lighting: Optional[str] = None,
) -> str:
    """Format prompt adhering to Malcolm sample block standards and adults-only guard.

    KTD1: caller scene action goes into detailed_description (no fixed standing pose) and a
    repeated 'featuring' clause is collapsed. KTD2: voice label prefers the named character,
    <d> holds spoken words only, and an empty dialogue renders a silent clip.
    """
    character = resolved.get("character")
    actor = resolved.get("actor")
    names = resolved.get("names", [])
    primary_name = character or actor or (names[0] if names else "Subject")
    voice_name = character or actor or primary_name

    desc = resolved.get("description")
    if not desc or not str(desc).strip():
        raise ValueError(
            f"Resolved identity for '{primary_name}' is missing 'description'. "
            "A concrete biometric description is required."
        )
    desc = dedupe_satire_tone(dedupe_featuring(str(desc).strip()))

    spoken = validate_spoken_dialogue(dialogue)
    scene_text = str(scene).strip() if scene and str(scene).strip() else None
    scene_summary = scene_text or f"{primary_name} stands calmly, looking into the camera before delivering a statement"
    scene_action = (scene_text or DEFAULT_SCENE_ACTION).rstrip().rstrip(".").rstrip()
    lighting_text = str(lighting).strip().rstrip(".") if lighting and str(lighting).strip() else None
    if lighting_text:
        scene_line = f"{scene_action}, {lighting_text}"
    elif scene_implies_lighting(scene_action):
        scene_line = scene_action
    else:
        scene_line = f"{scene_action}, {DEFAULT_LIGHTING}"

    audio_timbre_line = ""
    if audio_ref:
        audio_timbre_line = "\n<Audio 1> is the voice-timbre reference for <Subject 1>."

    if spoken:
        non_speaking = "none"
        speech_block = (
            "<scenedirect>\n"
            f"(S1): <d>[English in {voice_name}'s natural speaking voice] {spoken}</d>\n"
            "</scenedirect>\n"
            "She holds eye contact, gives a small nod at the end, and stops talking. "
            "Her mouth movements stop completely after the sentence. "
            "Her speaking voice, accent and cadence are the one natural voice she uses in this scene, "
            "used consistently in every clip of this character."
        )
        voice_line = "quiet room ambience, soft natural room tone; the single close-micd human voice in the foreground."
    else:
        non_speaking = "(S1)"
        speech_block = "She does not speak; her lips stay closed and relaxed for the whole shot."
        voice_line = "quiet room ambience, soft natural room tone; no spoken voice."

    prompt = f"""subject_definitions:
(S1) {primary_name} - an adult performer, age 28+, {desc}{audio_timbre_line}

summary:
(S1) {scene_summary}. Adult cast, adults-only, fictional 18+ adult scene. Non-speaking characters: {non_speaking}. No singing, no rapping, no songs, no music, no narration, no voice-over.

detailed_description:
[static medium shot, eye level, 50mm lens, shallow depth of field]
(S1) {scene_line}. Camera locked off, no zoom, no pan.
{speech_block}

overall_soundscape:
{voice_line}
no_dubs: no extra dubbing, no studio VO, no dubbing actors, no voice actors.
No music, no songs, no score, no soundtrack."""

    # Validate against adults guard
    if not comm.guard_ok(prompt):
        raise ValueError(f"Prompt failed comm.guard_ok check:\n{prompt}")

    return prompt


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
) -> Tuple[Dict[str, Any], str]:
    """Build request API graph and prompt text for a parody run.

    Returns:
        (graph_dict, prompt_str)
    """
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    prompt = format_parody_prompt(resolved, dialogue=dialogue, scene=scene, audio_ref=audio_ref)

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

    # Populate all 8 slots from resolved
    populate_refmod_slots(graph, resolved.get("refmod_slots", {}))

    # Verify KEEP dials
    verify_keep_dials(graph)

    return graph, prompt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build H3 parody request graph")
    parser.add_argument("--arm-dir", required=True, help="Directory to write request.api.json and prompt.txt")
    parser.add_argument("--seed", type=int, default=51083601, help="Noise seed")
    parser.add_argument("--prefix", required=True, help="Filename prefix, e.g. community/parody_01/clip_01")
    parser.add_argument("--frames", type=int, default=124, help="Total frames (must satisfy (f-5)%17==0)")
    parser.add_argument("--dialogue", help="Optional spoken line")
    parser.add_argument("--scene", help="Optional scene summary")
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
    from resolve import resolve_identities
    index_dir = Path(r"C:\AI\community\index\h3-known-characters")
    refmods_dir = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
    aliases_path = Path(__file__).parent / "aliases.json"

    req_dict = {
        "names": args.names or [],
        "character": args.character,
        "actor": args.actor,
        "tone": args.tone,
        "length_s": int(args.frames / 24),
        "description": args.description,
    }

    resolved = resolve_identities(
        req_dict,
        index_dir=index_dir,
        refmods_dir=refmods_dir,
        aliases_path=aliases_path,
    )

    graph, prompt = build_parody_request(
        resolved=resolved,
        seed=args.seed,
        prefix=args.prefix,
        frames=args.frames,
        dialogue=args.dialogue,
        scene=args.scene,
        template_path=Path(args.template),
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
    print(f"Wrote {req_file} and {prompt_file} (frames={args.frames}, seed={args.seed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
