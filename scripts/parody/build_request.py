"""Prompt builder and REF2VA request builder for H3 parody pipeline (U5).

Wraps make_b2_request.py pattern, populating all 8 loader slots on b2_refmod.api.json
(or KEEP b2.api.json in two-pass mode), constructing a Malcolm-compliant prompt,
preserving KEEP dials, and enforcing adults-only guard + Cond provenance (FG-2/FG-11).

Graph modes: single-pass = the frozen b2_refmod.api.json; two-pass = the KEEP b2.api.json
Lokken refine (+ RefLoRA graft on the whole model line when a hybrid resolves);
two-pass-parody (B2-4) = b2_parody_2pass.api.json, the per-pass dials (--pass1-lora-strength
0.0 voice-protected / --pass2-lora-strength 1.0). --unet swaps the model between the two beta7
checkpoints (the A/B); it is validated against BETA7_UNET_ALLOWLIST before anything is written.
B2-5: in two-pass-parody a start photo is OPTIONAL - with neither --image nor --cond-source the
graph carries no LoadImage and no MiniMaxH3AddGuide and the RefMod/RefLoRA conditioning is the
only identity feed; a photo in any mode keeps the approved_characters + SHA256 gate (FG-2/FG-11).
B2-6: the named-actress paste carries NO guard/meta boilerplate (no canon-age clause, no adults-only
meta line, no (character, actor) parenthetical, no tone label); the identity text is the resolved
bio of the named subject and nothing else, and the adults-only compliance lives in run_record.json
(run_record.py). The builder still refuses a guard failure (raise, never a softened prompt).
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
# B2-4: the dedicated two-pass PARODY graph (pass-1 model line voice-protected at LoRA 0.0,
# the LoRA half on the pass-2 model line, the reference half on the conditioning of both passes).
DEFAULT_PARODY_2PASS_TEMPLATE = Path(r"C:\AI\community\templates\b2_parody_2pass.api.json")
# B2-4 --unet override (`t179u`): the A/B model swap. Exactly the two beta7 checkpoints on disk,
# bare filenames in ComfyUI\models\diffusion_models\ (no path traversal, no download).
BETA7_UNET_ALLOWLIST: Tuple[str, ...] = (
    "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors",
    "10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors",
)
DEFAULT_UNET = BETA7_UNET_ALLOWLIST[0]
# B2-4 per-pass RefLoRA dials (pack example: 0.0 = the no-patch passthrough, 1.0 = the applied half).
DEFAULT_PASS1_LORA_STRENGTH = 0.0
DEFAULT_PASS2_LORA_STRENGTH = 1.0
DEFAULT_APPROVED_POOL = Path(r"C:\Users\derek\5slock\approved_characters")
DEFAULT_COMFY_INPUT = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input")
CHUNK = 1 << 20


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def validate_unet_name(value: Any) -> str:
    """B2-4 `--unet`: accept ONLY the two beta7 checkpoints, reject everything else (fail closed).

    Called before any file is written. Bare filename only (no directory part) so the value cannot
    traverse out of ComfyUI\\models\\diffusion_models\\, and no download is ever implied.
    """
    name = str(value or "").strip()
    if not name:
        raise ValueError(f"unet dial: empty value, expected one of {', '.join(BETA7_UNET_ALLOWLIST)}")
    if name.replace("\\", "/").rstrip("/") != Path(name).name:
        raise ValueError(f"unet dial: {name!r} must be a bare filename in models\\diffusion_models\\, "
                         "no path")
    if name not in BETA7_UNET_ALLOWLIST:
        raise ValueError(f"UNET dial drifted: expected one of the two beta7 checkpoints "
                         f"{', '.join(BETA7_UNET_ALLOWLIST)}, got {name}")
    return name


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

    B2-6 (the clean named-actress paste). No guard/meta boilerplate: no canon-age clause, no
    "one adult performer"-style meta line, no `(character ..., actor ...)` parenthetical, no tone
    label. `<Subject 1>` is the INDEX name + the resolved bio and nothing else - one full
    description (R28), never another woman's facial caption on a named actress - and the bio is
    where the adult age lives (see the guard at the end). No `overall_soundscape:` /
    `non_diegetic_music:` block (R7/R32): the audio stays the plain room-tone/voice sentences the
    R39/R40 shape needs, with no named songs and no score. Adults-only compliance is a RECORD, not
    paste text: `run_record.py` writes `guard_ok` / `adult_stated` / tone / character / actor /
    `description_sha256` into `run_record.json`.
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

    # summary: the scene line and the R16 entry transition. No R3 policy prose, no negatives in the
    # body (R3, R24), and no compliance meta line (B2-6): adults-only is recorded, not pasted.
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
        "with her shoulders moving on her breath."
    )

    # subject_definitions: RefMod citation, identity binding described in full once (R28), and the
    # Cond prose anchor only when the graph wires ref_image_1 (R36). B2-6: the identity text is the
    # resolved bio ONLY - no canon-age clause, no tone label, no (character, actor) parenthetical,
    # and no second caption (one full description per R28). The adult age is part of the bio.
    subject_lines = [
        "<Subject 1> is the woman in <Video 1>.",
        f"<Subject 1> {primary_name}, {str(desc).strip()}, the only person in the clip",
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

    # B2-6: the builder still refuses a guard failure - it never softens the paste to pass, and the
    # message carries NO prompt text (the block's record rule). Two fail-closed checks:
    #  1. `comm.guard_ok` - no minor-coded word anywhere in the paste.
    #  2. `comm.adult_stated` - the paste must state one adult age, because run_queue.py's per-clip
    #     gate (`comm.guard_reason(g0)`, `require_adult=True` at run_queue.py:192) reads THIS string
    #     out of the graph before every submit. The age lives in the resolved bio (R28), which is the
    #     only identity text this lane pastes, so a bio without an 18+ age blocks the build here
    #     instead of dying as GATE-FAIL at submit time.
    if not comm.guard_ok(prompt):
        raise ValueError(
            f"prompt for '{primary_name}' failed comm.guard_ok: a minor-coded word is present in the "
            "scene/dialogue/description text (no prompt text printed; see comm._BAD_RE)"
        )
    if not comm.adult_stated(prompt):
        raise ValueError(
            f"prompt for '{primary_name}' states no adult age (comm.adult_stated is False): the "
            "resolved --description must state the subject's adult age (18+ as an age, e.g. "
            "'a woman of 28 years'), because run_queue.py's per-clip adults gate requires one adult "
            "statement in the built paste; compliance metadata is recorded in run_record.json "
            "(run_record.py), never pasted (B2-6)"
        )

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


def verify_keep_dials(graph: Dict[str, Any], two_pass: bool = False,
                     cond_wired: bool = True) -> None:
    """Verify frozen KEEP dials on REF2VA 10strip eros beta7 int8HQ graph.

    ``cond_wired=False`` is the B2-5 no-photo two-pass shape: the two ``MiniMaxH3AddGuide`` nodes
    are intentionally absent (no guide image to add), so they are not required here -
    ``verify_parody_2pass_graph(cond_wired=False)`` is the guard that checks that shape.
    """
    if "unet" not in graph:
        raise ValueError("Graph missing 'unet' node.")
    # B2-4: the A/B model swap is the only KEEP dial allowed to change, so this guard is the two
    # beta7 checkpoints as an allowlist (fail closed, same "UNET dial drifted" message shape).
    unet_name = graph["unet"]["inputs"].get("unet_name", "")
    if unet_name not in BETA7_UNET_ALLOWLIST:
        raise ValueError(f"UNET dial drifted: expected one of the two beta7 checkpoints "
                         f"{', '.join(BETA7_UNET_ALLOWLIST)}, got {unet_name}")

    if "s0_sched" not in graph:
        raise ValueError("Graph missing 's0_sched' node.")
    steps = graph["s0_sched"]["inputs"].get("steps")
    if steps != 8:
        raise ValueError(f"Scheduler steps drifted: expected 8, got {steps}")

    if "refapply" not in graph:
        raise ValueError("Graph missing 'refapply' node.")

    if two_pass:
        required = ("lsu3", "p2sched", "s1_guide") if not cond_wired else (
            "ag0", "ag1", "lsu3", "p2sched", "s1_guide")
        for nid in required:
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
    objinfo_dump: Optional[Path] = None,
    unet_name: Optional[str] = None,
    pass1_lora_strength: Optional[float] = None,
    pass2_lora_strength: Optional[float] = None,
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """Build request API graph and prompt text for a parody run.

    ``graph_mode``:
      - ``single-pass`` (default): frozen ``b2_refmod.api.json`` (+ RefLoRA graft when hybrids).
      - ``two-pass``: KEEP ``b2.api.json`` + RefMod (+ RefLoRA graft) with AddGuide / 2x upscale / beta refine.
      - ``two-pass-parody`` (B2-4): ``b2_parody_2pass.api.json`` shape - the pass-1 model line stays
        the raw base beta7 model (voice-protected) at ``pass1_lora_strength`` 0.0, the LoRA half rides
        the pass-2 model line at ``pass2_lora_strength``, the reference half is applied ONCE on the
        conditioning of BOTH passes, CLIP stays native.

    Cond is required on BOTH hybrid and RefMod-only branches when ``require_cond`` (FG-11 / R10).
    B2-5 exception, the named-parody lane only: in ``two-pass-parody`` with NEITHER ``--image`` nor
    ``--cond-source`` the run is a no-photo clip (``require=False``), the builder drops the
    ``LoadImage`` and BOTH ``MiniMaxH3AddGuide`` nodes (``reflora.drop_cond_picture``), and the
    RefMod/RefLoRA conditioning injection is the only identity feed, feeding both guiders. Passing a
    photo in any mode keeps the FG-2 pool + SHA256 gate and the AddGuide/``<Picture 1>`` shape.

    ``objinfo_dump``: saved object_info capture used by the offline class check (B2-3) that runs
    next to ``verify_keep_dials``; default = the freshest capture in notes/objinfo.

    ``unet_name`` (B2-4 ``t179u``): the A/B model swap, validated against ``BETA7_UNET_ALLOWLIST``
    before anything is written; default ``DEFAULT_UNET`` (int8HQ), i.e. what the templates carry.
    Only the BUILT request changes, never the committed template.

    ``pass1_lora_strength`` / ``pass2_lora_strength``: the per-pass RefLoRA dials (defaults
    ``DEFAULT_PASS1_LORA_STRENGTH`` 0.0 / ``DEFAULT_PASS2_LORA_STRENGTH`` 1.0). Passing either one
    on ``two-pass`` selects the parody graph, because the per-pass dials only exist in that shape.

    Returns:
        (graph_dict, prompt_str, cond_meta)
    """
    mode = (graph_mode or "single-pass").strip().lower().replace("_", "-")
    p1 = DEFAULT_PASS1_LORA_STRENGTH if pass1_lora_strength is None else float(pass1_lora_strength)
    p2 = DEFAULT_PASS2_LORA_STRENGTH if pass2_lora_strength is None else float(pass2_lora_strength)
    explicit_dials = pass1_lora_strength is not None or pass2_lora_strength is not None
    if mode == "two-pass" and explicit_dials:
        mode = "two-pass-parody"
    if mode not in ("single-pass", "two-pass", "two-pass-parody"):
        raise ValueError("graph_mode must be 'single-pass', 'two-pass' or 'two-pass-parody', "
                         f"got {graph_mode!r}")
    parody = mode == "two-pass-parody"

    if template_path is None:
        if parody:
            template_path = DEFAULT_PARODY_2PASS_TEMPLATE
        elif mode == "two-pass":
            template_path = DEFAULT_B2_TEMPLATE
        else:
            template_path = DEFAULT_REFMOD_TEMPLATE
    template_path = Path(template_path)

    # B2-5: in the named-parody lane a photo is optional. "No photo" means neither flag was given,
    # so the requirement is dropped for exactly that case; any supplied photo still goes through
    # resolve_cond_provenance (approved_characters + SHA256, FG-2/FG-11) unchanged, and the other
    # graph modes keep requiring Cond.
    has_standalone_refmod = bool(resolved.get("loaded_refmods"))
    has_hybrid = bool((resolved.get("reflora") or {}).get("hybrids"))
    no_photo_parody = bool(
        (parody or (mode == "two-pass" and not has_hybrid and has_standalone_refmod))
        and not image and not cond_source
    )
    cond_meta = resolve_cond_provenance(
        image=image,
        cond_source=cond_source,
        approved_pool=approved_pool,
        comfy_input=comfy_input,
        stage_cond=stage_cond,
        require=require_cond and not no_photo_parody,
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
    two_pass = mode in ("two-pass", "two-pass-parody")

    if parody:
        from reflora import (
            LOADER_CLASS,
            add_cond_picture,
            derive_parody_2pass_graph,
            drop_cond_picture,
            verify_parody_2pass_graph,
        )
        if not hybrids:
            if not resolved.get("loaded_refmods"):
                raise ValueError(
                    "two-pass parody without RefLoRA requires at least one resolved standalone RefMod; "
                    "neither a RefLoRA hybrid nor a standalone RefMod resolved for this subject")
            from reflora import derive_refmod_2pass_graph, frozen_diff_2pass, frozen_diff_no_photo
            b2_tpl = json.loads(DEFAULT_B2_TEMPLATE.read_text(encoding="utf-8"))
            base_b2 = make_b2_build(b2_tpl, prompt=prompt, seed=seed, prefix=prefix, frames=frames,
                                    refmod=None, lora=None)
            graph = derive_refmod_2pass_graph(base_b2)
            populate_refmod_slots(graph, resolved.get("refmod_slots", {}))
            if cond_image:
                graph = add_cond_picture(graph, cond_image)
                drift = frozen_diff_2pass(graph, b2_tpl)
            else:
                graph = drop_cond_picture(graph)
                drift = frozen_diff_no_photo(graph, b2_tpl)
            if drift:
                raise ValueError("two-pass-parody RefMod-only frozen_diff: " + " | ".join(drift))
        else:
            hyb = {"lora_name": str(hybrids[0]["lora_name"]),
                   "members": str(hybrids[0].get("member_selection") or "all")}
            b2_tpl = json.loads(DEFAULT_B2_TEMPLATE.read_text(encoding="utf-8"))
            verify_kwargs = {"pass1_lora_strength": p1, "pass2_lora_strength": p2,
                             "cond_wired": bool(cond_image)}
            try:
                # --template plumbing: `graph` is the template file with this run's prompt/seed/prefix/
                # frames applied by make_b2_build above; use it as-is when it verifies at the run's dials.
                verify_parody_2pass_graph(graph, b2_tpl, **verify_kwargs)
            except ValueError:
                # dials/shape the committed template does not carry (a non-default dial, or the no-photo
                # shape of B2-5): regenerate from the LIVE b2.api.json.
                base_b2 = make_b2_build(b2_tpl, prompt=prompt, seed=seed, prefix=prefix, frames=frames,
                                        refmod=None, lora=None)
                graph = derive_parody_2pass_graph(base_b2, hyb, pass1_lora_strength=p1,
                                                 pass2_lora_strength=p2)
            for node in graph.values():
                if node.get("class_type") == LOADER_CLASS:
                    node["inputs"]["reflora_name"] = hyb["lora_name"]
                    node["inputs"]["members"] = hyb["members"]
            populate_refmod_slots(graph, resolved.get("refmod_slots", {}))
            if cond_image:
                graph = add_cond_picture(graph, cond_image)
            else:
                graph = drop_cond_picture(graph)
            verify_parody_2pass_graph(graph, b2_tpl, **verify_kwargs)
    elif two_pass:
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
            from reflora import drop_cond_picture, frozen_diff_no_photo
            b2_tpl = json.loads(DEFAULT_B2_TEMPLATE.read_text(encoding="utf-8"))
            if cond_image:
                graph = add_cond_picture(graph, cond_image)
                drift = frozen_diff_2pass(graph, b2_tpl)
            else:
                if not resolved.get("loaded_refmods"):
                    raise ValueError("two-pass no-photo RefMod-only requires at least one resolved standalone RefMod")
                graph = drop_cond_picture(graph)
                drift = frozen_diff_no_photo(graph, b2_tpl)
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

    # B2-4 --unet (t179u): the A/B model swap, in the BUILT request only (the committed templates
    # keep the int8HQ placeholder). Validated before any file is written, and verify_keep_dials
    # below checks the same allowlist, so an unaccepted checkpoint never reaches a request.
    effective_unet = validate_unet_name(unet_name) if unet_name is not None else DEFAULT_UNET
    graph.setdefault("unet", {}).setdefault("inputs", {})["unet_name"] = effective_unet
    # B2-6: record WHICH template this request came from, by path + SHA256 (a hash, never prompt
    # text), so run_record.json can carry the template SHA256 B2-7/B2-10 ask for and the two
    # hash-locked frozen templates are provably untouched by any run.
    resolved["parody_template"] = {"path": str(template_path), "sha256": _sha256_file(template_path)}
    rec = resolved.setdefault("reflora", {})
    if isinstance(rec, dict):
        rec["unet_name"] = effective_unet
        rec["unet_allowlist"] = list(BETA7_UNET_ALLOWLIST)
        if parody and hybrids:
            rec["parody_dials"] = {
                "pass1_lora_strength": p1, "pass2_lora_strength": p2,
                "start_photo": bool(cond_image),
                "pass1_model": ("base beta7 model, voice-protected (lora_strength 0.0 = the pack's "
                                "no-patch passthrough, raw m_shift)" if p1 <= 0.0
                                else "reflora_p1 at lora_strength {0:g}".format(p1)),
                "pass2_model": "reflora_p2 at lora_strength {0:g}".format(p2),
                # B2-5: with no start photo there is no AddGuide, so record where the ONE injection
                # really feeds - the record must describe the built graph, not the template.
                "conditioning_injection": (
                    "refapply(retention 1.0) -> reflora_apply_1 (refs only) -> ag0 + ag1"
                    if cond_image else
                    "refapply(retention 1.0) -> reflora_apply_1 (refs only) -> s0_guide + s1_guide "
                    "(no start photo: no LoadImage, no MiniMaxH3AddGuide)"),
                "clip": "native (c0.clip = clip node, no LoRA on the text encoder)",
            }
    verify_keep_dials(graph, two_pass=two_pass, cond_wired=bool(cond_image))
    # B2-3: the same unknown-class check submit-time static_check() does, run offline against the
    # saved object_info capture, so a --dry-run build fails closed on CPU (the U5 b2 arm died at
    # submit on lsu3 / a .disabled pack). No HTTP: only file reads.
    from reflora import offline_class_check
    missing_classes = offline_class_check(graph, objinfo_dump)
    if missing_classes:
        raise ValueError("graph not renderable on this ComfyUI (offline class check): "
                         + " | ".join(missing_classes))
    # Stash cond meta on resolved-facing side via return
    return graph, prompt, cond_meta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build H3 parody request graph")
    parser.add_argument("--arm-dir", required=True, help="Directory to write request.api.json and prompt.txt")
    parser.add_argument("--seed", type=int, default=51083601, help="Noise seed")
    parser.add_argument("--prefix", required=True, help="Filename prefix, e.g. community/parody_01/clip_01")
    parser.add_argument("--frames", type=int, default=124,
                        help="Total frames (must satisfy (f-5)%%17==0; %% is escaped for argparse)")
    parser.add_argument("--dialogue", help="Optional spoken line")
    parser.add_argument("--scene", help="Optional scene summary")
    parser.add_argument("--template", default=None, help="Template JSON path override")
    parser.add_argument("--graph-mode", choices=("single-pass", "two-pass", "two-pass-parody"),
                        default="single-pass",
                        help="single-pass=b2_refmod (community); two-pass=KEEP b2.api.json Lokken "
                             "refine; two-pass-parody=b2_parody_2pass.api.json (B2-4 per-pass dials, "
                             "pass 1 voice-protected). Passing --pass1-lora-strength or "
                             "--pass2-lora-strength with two-pass selects two-pass-parody.")
    parser.add_argument("--unet", default=None, metavar="SAFETENSORS",
                        help="A/B model swap (t179u): a bare diffusion_models filename, accepted set "
                             "= the two beta7 checkpoints "
                             f"{', '.join(BETA7_UNET_ALLOWLIST)}; default {DEFAULT_UNET}")
    parser.add_argument("--pass1-lora-strength", type=float, default=None,
                        help="two-pass-parody: LoRA half on the pass-1 model line; default "
                             f"{DEFAULT_PASS1_LORA_STRENGTH} = the pack's no-patch passthrough, so "
                             "pass 1 samples the base beta7 model and the native voice stays intact")
    parser.add_argument("--pass2-lora-strength", type=float, default=None,
                        help="two-pass-parody: LoRA half on the pass-2 model line; default "
                             f"{DEFAULT_PASS2_LORA_STRENGTH} (the pack example)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--image", help="ComfyUI/input-relative Cond name, e.g. hoot_start.jpg; "
                        "optional in --graph-mode two-pass-parody: with no --cond-source either the "
                        "clip is built with NO start photo (identity = RefMod + RefLoRA conditioning)")
    parser.add_argument("--cond-source", help="Absolute/relative path inside approved_characters (FG-2); "
                        "optional in --graph-mode two-pass-parody (omit both Cond flags for a "
                        "no-photo clip)")
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
    parser.add_argument("--objinfo-dump", default=None,
                        help="object_info capture for the offline class check "
                             "(default notes/objinfo/object_info_20261105.json)")

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
        objinfo_dump=Path(args.objinfo_dump) if args.objinfo_dump else None,
        unet_name=args.unet,
        pass1_lora_strength=args.pass1_lora_strength,
        pass2_lora_strength=args.pass2_lora_strength,
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
          f"graph_mode={args.graph_mode}, refmod_only={args.refmod_only}, "
          f"unet={graph['unet']['inputs']['unet_name']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
