"""Prompt builder and REF2VA request builder for H3 parody pipeline (U5).

Wraps make_b2_request.py pattern, populating all 8 loader slots on b2_refmod.api.json
(or KEEP b2.api.json in two-pass mode), constructing a Malcolm-compliant prompt,
preserving KEEP dials, and enforcing adults-only guard + Cond provenance (FG-2/FG-11).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as make_b2_build

DEFAULT_REFMOD_TEMPLATE = Path(r"C:\AI\community\templates\b2_refmod.api.json")
DEFAULT_REFLORA_TEMPLATE = Path(r"C:\AI\community\templates\b2_reflora.api.json")
DEFAULT_B2_TEMPLATE = Path(r"C:\AI\community\templates\b2.api.json")
DEFAULT_REFLORA_2PASS_TEMPLATE = Path(r"C:\AI\community\templates\b2_reflora_2pass.api.json")
DEFAULT_APPROVED_POOL = Path(r"C:\Users\derek\5slock\approved_characters")
DEFAULT_COMFY_INPUT = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input")
CHUNK = 1 << 20


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def resolve_cond_provenance(
    image: Optional[str],
    cond_source: Optional[str],
    *,
    approved_pool: Path = DEFAULT_APPROVED_POOL,
    comfy_input: Path = DEFAULT_COMFY_INPUT,
    stage_cond: bool = False,
    require: bool = True,
) -> Dict[str, Any]:
    """FG-2 / FG-11: gate Cond through approved_characters + SHA256(ComfyUI/input).

    Returns dict with cond_source_path, cond_input_name, cond_sha256 (or empty if
    Cond not required and not supplied).
    """
    from resolve import validate_stills

    if not image and not cond_source:
        if require:
            raise ValueError(
                "parody run requires Cond (--image and/or --cond-source from approved_characters); "
                "missing Cond blocks (R10 / FG-11)."
            )
        return {"cond_source_path": None, "cond_input_name": None, "cond_sha256": None}

    pool = Path(approved_pool)
    if cond_source:
        src_raw = Path(cond_source)
    else:
        # --image alone: only accept if that basename exists inside approved_characters
        cand = None
        basename = Path(image).name
        # Prefer exact relative path under pool if --image looks like a pool-relative path
        direct = pool / image
        if direct.is_file():
            cand = direct
        else:
            hits = list(pool.rglob(basename)) if pool.is_dir() else []
            # refuse sydney via validate_stills; also fail closed if 0 or >1
            hits = [h for h in hits if "sydney" not in str(h).lower()]
            if len(hits) == 1:
                cand = hits[0]
            elif len(hits) > 1:
                raise ValueError(
                    f"--image {image!r} matches multiple approved_characters files; "
                    "pass --cond-source with the exact pool path."
                )
        if cand is None:
            raise ValueError(
                f"--image {image!r} is not resolvable inside approved_characters ({pool}); "
                "pass --cond-source <approved_characters path> (FG-2 fail-closed)."
            )
        src_raw = cand

    validated = validate_stills([str(src_raw)], pool)
    src = Path(validated[0])
    input_name = Path(image).name if image else src.name
    # Keep any relative subdir from --image (e.g. community/foo.jpg) for LoadImage
    if image and (Path(image).parent.as_posix() not in ("", ".")):
        input_name = Path(image).as_posix().replace("\\", "/")
    else:
        input_name = src.name

    dest = Path(comfy_input) / Path(input_name).name
    # When --image carries a subdir, LoadImage uses that relative name; file still lives
    # at ComfyUI/input/<basename> OR ComfyUI/input/<subdir>/<name>. Prefer basename at root
    # for staging; if image has subdir, stage to that relative path under input.
    if image and "/" in image.replace("\\", "/"):
        dest = Path(comfy_input) / Path(image.replace("\\", "/"))

    src_sha = _sha256_file(src)

    if stage_cond:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        staged_sha = _sha256_file(dest)
        if staged_sha != src_sha:
            raise ValueError(
                f"staged Cond SHA256 mismatch: pool={src_sha} input={staged_sha} ({dest})"
            )
    else:
        if not dest.is_file():
            raise ValueError(
                f"ComfyUI/input Cond missing: {dest}. Pass --stage-cond to copy from "
                f"validated pool file {src}, or stage it manually (FG-2)."
            )
        dest_sha = _sha256_file(dest)
        if dest_sha != src_sha:
            raise ValueError(
                f"Cond SHA256 mismatch: pool {src}={src_sha} vs ComfyUI/input {dest}={dest_sha} (FG-2)."
            )

    # LoadImage name: prefer the --image string when provided (ComfyUI/input-relative)
    load_name = image.replace("\\", "/") if image else Path(input_name).name
    return {
        "cond_source_path": str(src),
        "cond_input_name": load_name,
        "cond_sha256": src_sha,
    }


# R23 camera line, verbatim; 24 fps is the box's clip rate (R8: beat ranges total the clip).
CAMERA_LINE = "The camera holds a static shot."
FPS = 24.0


def _shot_end_clock(frames: int) -> str:
    """End clock of `[Shot 1]` = frames / fps, e.g. 124 -> `00:05.167` (R8)."""
    millis = int(round(int(frames) / FPS * 1000))
    return f"{millis // 60000:02d}:{(millis // 1000) % 60:02d}.{millis % 1000:03d}"


def _speech_sentence(name: str, words: str) -> str:
    """R37 speech form: the subject label keeps identity, `(S1)` is the speaker, inside `<d>` only
    the language tag and the words, punctuation limited to `, . ? !`, statements ending in `.`."""
    text = " ".join(str(words).split())
    for ch in "~–—…'*\"()[]|/\\;:":
        text = text.replace(ch, "")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise ValueError("dialogue is empty after the R37 punctuation strip")
    if not text.endswith((".", "?", "!")):
        text += "."
    return (
        f"<Subject 1> {name} (S1) keeps her eyes on the lens, chin level, and says, "
        f"<d>[English] {text}</d> Her lips and jaw shape each word and return to rest between the "
        f"phrases, breath moving visibly through her nose."
    )


def format_parody_prompt(
    resolved: Dict[str, Any],
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
    frames: int = 124,
    cond_wired: bool = False,
) -> str:
    r"""Format the five-section H3-Max paste (R5) for the INDEX + RefMod parody lane.

    Shape: `h3-prompting` R5-R9, R11, R14, R16-R17, R23-R28 and R32-R42 of
    `h3-max-ref2va-prompt`, plus `h3-parody-identity`: the identity binding is the INDEX name +
    the resolved biometric description in `subject_definitions`, and the installed RefMod is cited
    in the RefMod route's own form `<Subject 1> is the woman in <Video 1>.` (REFMODS.md:464-487).
    On this box that label is fed by `MiniMaxH3RefModsLoader` + `MiniMaxH3RefModApply`
    (conditioning); `ref_videos` is not wired - the same deviation `C:\AI\community\runs\rv_20261105\CARD.md` states.

    Labels only for what the graph feeds (R33, R42): `<Picture 1>` only when `cond_wired` (the
    builder calls `reflora.add_cond_picture`, which wires `ref_images.ref_image_1`); exactly one
    `<Video 1>`; no `<Picture N>` face-identity clause (parody lane item 3). `audio_ref` is kept
    for caller compatibility and emits no `<Audio N>`, because no builder path wires `ref_audios`.

    Default is no speech (R37): the `(S1)` ID and the `<d>` block appear only when `dialogue` is given.
    """
    character = resolved.get("character")
    actor = resolved.get("actor")
    names = resolved.get("names", [])
    primary_name = character or actor or (names[0] if names else "Subject")

    desc = resolved.get("description")
    if not desc or not str(desc).strip():
        raise ValueError(
            f"Resolved identity for '{primary_name}' is missing 'description'. "
            "A concrete biometric description is required."
        )

    # summary: the scene line, the R16 entry transition, adults-only stated once (R5 item 2, R21).
    # No R3 policy prose and no negatives in the body (R3, R24).
    if scene:
        setting = " ".join(str(scene).split())
        if not setting.endswith((".", "?", "!")):
            setting += "."
    else:
        setting = (f"<Subject 1> {primary_name} stands behind a service counter at night, in the light "
                   "and framing of the start frame.")
    scene_summary = (
        f"{setting} <Subject 1> {primary_name} settles into position facing the camera, stays squared to "
        "the lens with her face in frame the whole time, and holds the last frame in the same stance "
        "with her shoulders moving on her breath. One adult performer, adults-only."
    )

    # subject_definitions: RefMod citation, identity binding described in full once (R28), and the
    # Cond prose anchor only when the graph wires ref_image_1 (R36).
    subject_lines = [
        "<Subject 1> is the woman in <Video 1>.",
        f"<Subject 1> {primary_name}, a fictional adult, canon age 28, {str(desc).strip()}, "
        "the only person in the clip",
    ]
    if cond_wired:
        subject_lines.append("<Picture 1> is the start frame of [Shot 1] for setting, light and framing")

    # R11 lead-ins with R35 role scope; `(Sx)` never appears here; new action is not a fidelity loss.
    retention_lines = [
        "<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe"
    ]
    if cond_wired:
        retention_lines.append(
            "<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - setting, light, framing"
        )

    # R39 style opening built from the start image's text records (the resolved description, R14),
    # the R23 camera line verbatim, then the timed beat (R8, R16, R17). The `<Picture 1>` citation in
    # the style line only rides when the graph feeds ref_image_1 (R42 gate item 1).
    if cond_wired:
        style = (
            f"The target video is a realistic photographic portrait of {primary_name} with the same "
            "light, setting and framing as <Picture 1>, shot at eye level with a shallow depth of field "
            "and fine film grain."
        )
        entry = "begins in the standing position of the start frame"
    else:
        style = (
            f"The target video is a realistic photographic portrait of {primary_name}, lit by the "
            "practical lights of the room at eye level, with a shallow depth of field and fine film grain."
        )
        entry = "stands facing the camera"
    beat = (
        f"[Shot 1] 00:00.000 - {_shot_end_clock(frames)} <Subject 1> {primary_name} {entry}, weight "
        "even on both feet, hands resting lightly at her sides, chin level, eyes on the lens, and she "
        "settles square to the camera inside the first two seconds. PRIMARY MOTION - small steady "
        "upper-body sway, about one gentle cycle every three seconds, a few centimetres of travel, "
        "shoulders and hips staying on the frame line, her face staying in the same light. She keeps her "
        "gaze on the lens, and her chest rises and falls on the last frame."
    )
    sounds = (
        "Her voice sits close and dry in the foreground, recorded in the room with the camera. The room "
        "tone is a low hum of ventilation, with a soft glass clink on the counter and her shoes shifting "
        "once on the tile."
    )

    detail_lines = [style, CAMERA_LINE, beat]
    if dialogue:
        # Speech rides inside [Shot 1] (R37); plain real-sound sentences close the section (R7, R26).
        detail_lines.append(_speech_sentence(primary_name, dialogue))

    prompt = (
        "subject_definitions:\n" + "\n".join(subject_lines)
        + "\n\nsummary:\n[reference generation] " + scene_summary
        + "\n\nretention_analysis:\n" + "\n".join(retention_lines)
        + "\n\ndetailed_description:\n" + "\n".join(detail_lines) + "\n" + sounds
    )

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


def verify_keep_dials(graph: Dict[str, Any], two_pass: bool = False) -> None:
    """Verify frozen KEEP dials on REF2VA 10strip eros beta7 int8HQ graph."""
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

    if two_pass:
        for nid in ("ag0", "ag1", "lsu3", "p2sched", "s1_guide"):
            if nid not in graph:
                raise ValueError(f"Two-pass graph missing {nid!r}.")
        if graph["p2sched"]["inputs"].get("steps") != 3:
            raise ValueError("Two-pass p2sched.steps drifted (expected 3).")
        if float(graph["p2sched"]["inputs"].get("denoise", 0)) != 0.4:
            raise ValueError("Two-pass p2sched.denoise drifted (expected 0.4).")
        if graph["p2sched"]["inputs"].get("scheduler") != "beta":
            raise ValueError("Two-pass p2sched.scheduler drifted (expected beta).")


def build_parody_request(
    resolved: Dict[str, Any],
    seed: int,
    prefix: str,
    frames: int = 124,
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    audio_ref: Optional[str] = None,
    template_path: Optional[Path] = None,
    image: Optional[str] = None,
    cond_source: Optional[str] = None,
    graph_mode: str = "single-pass",
    stage_cond: bool = False,
    approved_pool: Path = DEFAULT_APPROVED_POOL,
    comfy_input: Path = DEFAULT_COMFY_INPUT,
    require_cond: bool = True,
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """Build request API graph and prompt text for a parody run.

    ``graph_mode``:
      - ``single-pass`` (default): frozen ``b2_refmod.api.json`` (+ RefLoRA graft when hybrids).
      - ``two-pass``: KEEP ``b2.api.json`` + RefMod (+ RefLoRA graft) with AddGuide / 2x upscale / beta refine.

    Cond is required on BOTH hybrid and RefMod-only branches when ``require_cond`` (FG-11 / R10).

    Returns:
        (graph_dict, prompt_str, cond_meta)
    """
    mode = (graph_mode or "single-pass").strip().lower().replace("_", "-")
    if mode not in ("single-pass", "two-pass"):
        raise ValueError(f"graph_mode must be 'single-pass' or 'two-pass', got {graph_mode!r}")

    if template_path is None:
        template_path = DEFAULT_B2_TEMPLATE if mode == "two-pass" else DEFAULT_REFMOD_TEMPLATE
    template_path = Path(template_path)

    cond_meta = resolve_cond_provenance(
        image=image,
        cond_source=cond_source,
        approved_pool=approved_pool,
        comfy_input=comfy_input,
        stage_cond=stage_cond,
        require=require_cond,
    )
    cond_image = cond_meta.get("cond_input_name")

    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    prompt = format_parody_prompt(
        resolved, dialogue=dialogue, scene=scene, audio_ref=audio_ref,
        frames=frames, cond_wired=bool(cond_image),
    )

    graph = make_b2_build(
        tpl,
        prompt=prompt,
        seed=seed,
        prefix=prefix,
        frames=frames,
        refmod=None,
        lora=None,
    )

    hybrids = (resolved.get("reflora") or {}).get("hybrids") or []
    two_pass = mode == "two-pass"

    if two_pass:
        from reflora import (
            add_cond_picture,
            derive_refmod_2pass_graph,
            frozen_diff_2pass,
            graft_reflora_2pass,
            verify_reflora_graph,
        )
        # If template was raw b2 (no refmods), graft RefMod nodes first.
        if "refmods" not in graph:
            # Re-derive from the KEEP b2 template body we loaded
            with open(DEFAULT_B2_TEMPLATE, "r", encoding="utf-8") as f:
                b2_tpl = json.load(f)
            base_b2 = make_b2_build(
                b2_tpl, prompt=prompt, seed=seed, prefix=prefix, frames=frames,
                refmod=None, lora=None,
            )
            graph = derive_refmod_2pass_graph(base_b2)
        populate_refmod_slots(graph, resolved.get("refmod_slots", {}))
        if hybrids:
            graph = graft_reflora_2pass(graph, hybrids)
            if cond_image:
                graph = add_cond_picture(graph, cond_image)
            verify_reflora_graph(graph, json.loads(DEFAULT_B2_TEMPLATE.read_text(encoding="utf-8")),
                                 len(hybrids), two_pass=True)
        else:
            if cond_image:
                graph = add_cond_picture(graph, cond_image)
            drift = frozen_diff_2pass(graph, json.loads(DEFAULT_B2_TEMPLATE.read_text(encoding="utf-8")))
            if drift:
                raise ValueError("two-pass RefMod-only frozen_diff_2pass: " + " | ".join(drift))
    else:
        populate_refmod_slots(graph, resolved.get("refmod_slots", {}))
        if hybrids:
            from reflora import add_cond_picture, graft_reflora, verify_reflora_graph
            if not cond_image:
                raise ValueError("RefLoRA arm requires an approved Cond still (--image); missing Cond blocks (R10).")
            base = graph
            graph = add_cond_picture(graft_reflora(base, hybrids), cond_image)
            verify_reflora_graph(graph, tpl, len(hybrids), two_pass=False)
        elif cond_image:
            from reflora import add_cond_picture
            graph = add_cond_picture(graph, cond_image)

    verify_keep_dials(graph, two_pass=two_pass)
    # Stash cond meta on resolved-facing side via return
    return graph, prompt, cond_meta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build H3 parody request graph")
    parser.add_argument("--arm-dir", required=True, help="Directory to write request.api.json and prompt.txt")
    parser.add_argument("--seed", type=int, default=51083601, help="Noise seed")
    parser.add_argument("--prefix", required=True, help="Filename prefix, e.g. community/parody_01/clip_01")
    parser.add_argument("--frames", type=int, default=124, help="Total frames (must satisfy (f-5)%17==0)")
    parser.add_argument("--dialogue", help="Optional spoken line")
    parser.add_argument("--scene", help="Optional scene summary")
    parser.add_argument("--template", default=None, help="Template JSON path override")
    parser.add_argument("--graph-mode", choices=("single-pass", "two-pass"), default="single-pass",
                        help="single-pass=b2_refmod (community); two-pass=KEEP b2.api.json Lokken refine")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--image", help="ComfyUI/input-relative Cond name, e.g. hoot_start.jpg")
    parser.add_argument("--cond-source", help="Absolute/relative path inside approved_characters (FG-2)")
    parser.add_argument("--stage-cond", action="store_true",
                        help="Copy validated --cond-source into ComfyUI/input and verify SHA256")
    parser.add_argument("--refmod-only", "--disable-reflora", dest="refmod_only", action="store_true",
                        help="Skip RefLoRA lookup (Arm A RefMod-only even if hybrid is on disk)")
    parser.add_argument("--name", action="append", dest="names", help="Subject name(s)")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True,
                        help="Biometric/wardrobe description")
    parser.add_argument("--tone", default="parody", help="Tone (parody, adult, etc.)")

    args = parser.parse_args(argv)

    from resolve import resolve_identities
    from reflora import DEFAULT_REFLORA_DIR
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
        reflora_dir=None if args.refmod_only else DEFAULT_REFLORA_DIR,
    )

    graph, prompt, cond_meta = build_parody_request(
        resolved=resolved,
        seed=args.seed,
        prefix=args.prefix,
        frames=args.frames,
        dialogue=args.dialogue,
        scene=args.scene,
        template_path=Path(args.template) if args.template else None,
        image=args.image,
        cond_source=args.cond_source,
        graph_mode=args.graph_mode,
        stage_cond=args.stage_cond,
    )
    resolved["cond"] = cond_meta

    arm_dir = Path(args.arm_dir)
    arm_dir.mkdir(parents=True, exist_ok=True)

    req_file = arm_dir / "request.api.json"
    prompt_file = arm_dir / "prompt.txt"
    cond_file = arm_dir / "cond_meta.json"

    if req_file.exists() and not args.force:
        print(f"Error: {req_file} exists (use --force)", file=sys.stderr)
        return 3

    req_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    prompt_file.write_text(prompt, encoding="utf-8")
    cond_file.write_text(json.dumps(cond_meta, indent=2), encoding="utf-8")
    print(f"Wrote {req_file} and {prompt_file} (frames={args.frames}, seed={args.seed}, "
          f"graph_mode={args.graph_mode}, refmod_only={args.refmod_only})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
