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
import sys
from typing import Any, Dict, List, Optional, Tuple

# Add community scripts to path for make_b2_request and comm
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as make_b2_build

DEFAULT_REFMOD_TEMPLATE = Path(r"C:\AI\community\templates\b2_refmod.api.json")
# Committed derived template (reflora.derive_reflora_template(b2_refmod)); documentation +
# fixture anchor. Requests are grafted from the frozen b2_refmod so dials have one source.
DEFAULT_REFLORA_TEMPLATE = Path(r"C:\AI\community\templates\b2_reflora.api.json")


def format_parody_prompt(
    resolved: Dict[str, Any],
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
) -> str:
    """Format prompt adhering to Malcolm sample block standards and adults-only guard."""
    character = resolved.get("character")
    actor = resolved.get("actor")
    names = resolved.get("names", [])
    primary_name = character or actor or (names[0] if names else "Subject")
    voice_name = actor or character or primary_name

    desc = resolved.get("description")
    if not desc or not str(desc).strip():
        raise ValueError(
            f"Resolved identity for '{primary_name}' is missing 'description'. "
            "A concrete biometric description is required."
        )

    scene_summary = scene or f"{primary_name} stands calmly, looking into the camera before delivering a statement"
    dialogue_text = dialogue or "I have a message for everyone listening, and I will only say it once."

    audio_timbre_line = ""
    if audio_ref:
        audio_timbre_line = "\n<Audio 1> is the voice-timbre reference for <Subject 1>."

    prompt = f"""subject_definitions:
(S1) {primary_name} - an adult performer, age 28+, {desc}{audio_timbre_line}

summary:
(S1) {scene_summary}. Adult cast, adults-only, fictional 18+ adult scene. Non-speaking characters: none. No singing, no rapping, no songs, no music, no narration, no voice-over.

detailed_description:
[static medium shot, eye level, 50mm lens, shallow depth of field]
(S1) stands in position, late afternoon ambient lighting, soft key on face, subtle fill. Camera locked off, no zoom, no pan.
<scenedirect>
(S1): <d>[English in {voice_name}'s natural speaking voice] {dialogue_text}</d>
</scenedirect>
She holds eye contact, gives a small nod at the end, and stops talking. Her mouth movements stop completely after the sentence. Her speaking voice, accent and cadence are the one natural voice she uses in this scene, used consistently in every clip of this character.

overall_soundscape:
quiet room ambience, soft natural room tone; the single close-micd human voice in the foreground.
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
    image: Optional[str] = None,
) -> Tuple[Dict[str, Any], str]:
    """Build request API graph and prompt text for a parody run.

    ``image`` is the approved Cond still as a ComfyUI/input-relative name
    (e.g. ``community/X_768x1344.png``); it is wired to the REF2VA Picture input.
    When the resolver selected RefLoRA hybrids, Cond is required (R10) and the graph gets
    one Load H3 RefLoRA + Apply per hybrid on top of the frozen B2 RefMod template.

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

    hybrids = (resolved.get("reflora") or {}).get("hybrids") or []
    if hybrids:
        from reflora import add_cond_picture, graft_reflora, verify_reflora_graph
        if not image:
            raise ValueError("RefLoRA arm requires an approved Cond still (--image); missing Cond blocks (R10).")
        base = graph
        graph = add_cond_picture(graft_reflora(base, hybrids), image)
        verify_reflora_graph(graph, tpl, len(hybrids))
    elif image:
        from reflora import add_cond_picture
        graph = add_cond_picture(graph, image)

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
    parser.add_argument("--image", help="Approved Cond still inside ComfyUI/input, e.g. community/X_768x1344.png")

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
    from reflora import DEFAULT_REFLORA_DIR

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
        reflora_dir=DEFAULT_REFLORA_DIR,
    )

    graph, prompt = build_parody_request(
        resolved=resolved,
        seed=args.seed,
        prefix=args.prefix,
        frames=args.frames,
        dialogue=args.dialogue,
        scene=args.scene,
        template_path=Path(args.template),
        image=args.image,
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
