"""Submit and execute H3 parody runs under GPU lock (U8 + dynamic U1-U4, 2026-11-06).

Builds resolved request, saves run record, writes a run_queue manifest, and submits through
run_queue.py --detach. run_queue owns gpu-render.lock; rc 7 means GPU busy.

Dynamic options (all optional; omitted = the locked 124f 768x1344 single clip as before):
  --seconds / --frames   single shot up to SINGLE_CLIP_MAX_FRAMES (H3 grid snap); longer asks require 2+
                         --beat scenes
  --beat (2+)            two or more --beat scenes build ONE native latent-tail continuation graph
                         (tag "clip"), not stitched cells
  --aspect / --size      canvas (9:16 default, 16:9, 1:1, 4:3, 3:4)
  --camera / --pronoun / --end-action / --summary
  --image [--image-at]   approved_characters reference image (frame-0 AddGuide start image first; pass --image-at <sec>
                         for additional timed pins across single-shot or multi-beat continuation; never sydney paths)
  --beat-new-shot        1-based beat index (2+) that opens as an intentional C 'new shot' cut (new room or pose)
  --name2 ... --dialogue2  optional second subject (S2)
  --wait [--qnap-put]    block until BATCH closed, copy/stitch clip.mp4, upload pi-drop/<run>.mp4, and print
                         final_mp4 + qnap_path in the JSON - one call, no PowerShell polling loop

Writer hook (dynsafe 2026-11-11, Derrick t903u; Python API only, no CLI flag): submit_writer_run() is Render's production
path for a free-text OC writer prompt. Writer output (or a write() callable, gated with one retry) -> still read
(vision facts) -> make_cast -> build_writer_request (dynamic safeguards, writer repair loop max 2) -> queue. Any hard
stop writes <run_dir>/clip_NOT_READY.txt + build_report.json and nothing is submitted.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence, Union, Tuple

# Add community scripts to path
PARODY_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PARODY_DIR.parent
_AI_ROOT = SCRIPTS_DIR.parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br
from build_request import DEFAULT_REFMOD_TEMPLATE, build_parody_request
import scene_addenda
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities, validate_reference_images
from run_record import RUNS_ROOT, save_run_record

INDEX_DIR = SCRIPTS_DIR.parent / "index" / "h3-known-characters"
REFMODS_DIR = _AI_ROOT / "comfy-alienpc" / "models" / "refmods"
ALIASES_PATH = PARODY_DIR / "aliases.json"
RUN_QUEUE_PY = SCRIPTS_DIR / "run_queue.py"
STITCH_PY = SCRIPTS_DIR / "queue" / "take_chain_stitch.py"
PI_QNAP_PY = SCRIPTS_DIR / "pi_qnap.py"
COMFY_OUT_COMMUNITY = _AI_ROOT / "comfy-alienpc" / "output" / "community"
QUEUE_PYTHON = _AI_ROOT / "director" / ".venv" / "Scripts" / "python.exe"
QUEUE_TAG = "clip"
GPU_BUSY_RC = 7
WAIT_POLL_SEC = 5
WAIT_TIMEOUT_SEC = 3 * 3600
_BATCH_RE = re.compile(r" BATCH closed rc=(\d+)\b")


def queue_outcome(run_dir: Path) -> Optional[Dict[str, Any]]:
    """Read the newest BATCH closed rc from a detached run_queue log."""
    log = Path(run_dir) / "_render_queue.log"
    if not log.is_file():
        return None
    matches = _BATCH_RE.findall(log.read_text(encoding="utf-8"))
    if not matches:
        return None
    rc = int(matches[-1])
    return {"rc": rc, "gpu_busy": rc == GPU_BUSY_RC}


def _batch_count(run_dir: Path) -> int:
    log = Path(run_dir) / "_render_queue.log"
    return len(_BATCH_RE.findall(log.read_text(encoding="utf-8"))) if log.is_file() else 0


def wait_for_batch(run_dir: Path, since_count: int, timeout: float = WAIT_TIMEOUT_SEC,
                   poll: float = WAIT_POLL_SEC) -> int:
    """Block until a NEW 'BATCH closed rc=N' line lands in <run_dir>/_render_queue.log; return N."""
    log = Path(run_dir) / "_render_queue.log"
    deadline = time.time() + timeout
    while time.time() < deadline:
        if log.is_file():
            found = _BATCH_RE.findall(log.read_text(encoding="utf-8"))
            if len(found) > since_count:
                return int(found[-1])
        time.sleep(poll)
    raise TimeoutError(f"no new 'BATCH closed' line in {log} within {timeout:.0f}s")


def _newest(paths: List[Path]) -> Optional[Path]:
    paths = [p for p in paths if p.is_file()]
    return max(paths, key=lambda p: p.stat().st_mtime) if paths else None


def find_tag_mp4(run_dir: Path, tag: str) -> Optional[Path]:
    """<run_dir>/<tag>/<tag>.mp4 (run_queue copy), <run_dir>/<tag>.mp4, else the newest ComfyUI output for that tag."""
    local = Path(run_dir) / tag / f"{tag}.mp4"
    if local.is_file():
        return local
    direct = Path(run_dir) / f"{tag}.mp4"
    if direct.is_file():
        return direct
    out = COMFY_OUT_COMMUNITY / Path(run_dir).name
    return _newest(list(out.glob(f"{tag}_*.mp4")) + list((out / tag).glob(f"{tag}_*.mp4")))


def objective_lines(run_dir: Path) -> List[str]:
    log = Path(run_dir) / "status.log"
    if not log.is_file():
        return []
    return [ln.strip() for ln in log.read_text(encoding="utf-8", errors="replace").splitlines() if "OBJECTIVE" in ln]


def finalize_clip(
    run_dir: Path,
    tags: Sequence[str],
    python: str,
    prequel_to: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """After BATCH closed rc=0: single clip -> copy to clip.mp4; cells -> ensure each cell mp4, stitch, copy.

    If prequel_to is provided: stitch the rendered prequel clip in front of the named existing clip
    [prequel_clip.mp4, existing_clip.mp4] using take_chain_stitch.py, copy the stitched film to clip.mp4.
    """
    run_dir = Path(run_dir)
    final = run_dir / "clip.mp4"
    if prequel_to:
        target_mp4 = Path(prequel_to).resolve()
        if not target_mp4.is_file():
            raise FileNotFoundError(f"target clip to prequel not found: {target_mp4}")
        if len(tags) == 1:
            src = find_tag_mp4(run_dir, tags[0])
            if not src:
                raise FileNotFoundError(f"no rendered mp4 for tag {tags[0]} in {run_dir}")
            prequel_mp4 = run_dir / f"{tags[0]}.mp4"
            if src.resolve() != prequel_mp4.resolve():
                shutil.copyfile(src, prequel_mp4)
        else:
            for t in tags:
                cell_mp4 = run_dir / t / f"{t}.mp4"
                if not cell_mp4.is_file():
                    src = find_tag_mp4(run_dir, t)
                    if not src:
                        raise FileNotFoundError(f"no rendered mp4 for cell {t} - refusing to stitch a partial chain")
                    cell_mp4.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, cell_mp4)
            r0 = subprocess.run([python, str(STITCH_PY), str(run_dir), "--name", "prequel_cells"],
                                capture_output=True, text=True, timeout=900)
            prequel_film = run_dir / "_stitch" / "prequel_cells.mp4"
            if r0.returncode != 0 or not prequel_film.is_file():
                raise RuntimeError(f"prequel cells stitch failed: {(r0.stdout + r0.stderr).strip()[-400:]}")
            prequel_mp4 = run_dir / "prequel_stitched.mp4"
            shutil.copyfile(prequel_film, prequel_mp4)

        r = subprocess.run(
            [python, str(STITCH_PY), str(run_dir), "--clips", str(prequel_mp4), str(target_mp4), "--name", "stitched"],
            capture_output=True, text=True, timeout=900,
        )
        stitch_out = (r.stdout + r.stderr).strip()
        print(stitch_out)
        film = run_dir / "_stitch" / "stitched.mp4"
        if r.returncode != 0 or not film.is_file():
            raise RuntimeError(f"take_chain_stitch.py failed rc={r.returncode}: {stitch_out[-400:]}")
        shutil.copyfile(film, final)
        return {
            "final_mp4": str(final),
            "stitched": True,
            "prequel_to": str(target_mp4),
            "clips": [str(prequel_mp4), str(target_mp4)],
            "stitch_proof": [ln for ln in stitch_out.splitlines() if ln.startswith(("PROOF film", "STITCH"))],
        }

    if len(tags) == 1:
        src = find_tag_mp4(run_dir, tags[0])
        if not src:
            raise FileNotFoundError(f"no rendered mp4 for tag {tags[0]} in {run_dir}")
        shutil.copyfile(src, final)
        return {"final_mp4": str(final), "stitched": False}
    for t in tags:
        cell_mp4 = run_dir / t / f"{t}.mp4"
        if not cell_mp4.is_file():
            src = find_tag_mp4(run_dir, t)
            if not src:
                raise FileNotFoundError(f"no rendered mp4 for cell {t} - refusing to stitch a partial chain")
            cell_mp4.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, cell_mp4)
    r = subprocess.run([python, str(STITCH_PY), str(run_dir), "--name", "stitched"],
                       capture_output=True, text=True, timeout=900)
    stitch_out = (r.stdout + r.stderr).strip()
    print(stitch_out)
    film = run_dir / "_stitch" / "stitched.mp4"
    if r.returncode != 0 or not film.is_file():
        raise RuntimeError(f"take_chain_stitch.py failed rc={r.returncode}: {stitch_out[-400:]}")
    shutil.copyfile(film, final)
    return {"final_mp4": str(final), "stitched": True,
            "stitch_proof": [ln for ln in stitch_out.splitlines() if ln.startswith(("PROOF film", "STITCH"))]}


def qnap_put(final_mp4: Path, run_name: str, python: str) -> Dict[str, Any]:
    dest = f"pi-drop/{run_name}.mp4"
    r = subprocess.run([python, str(PI_QNAP_PY), "put", str(final_mp4), dest],
                       capture_output=True, text=True, timeout=3600)
    return {"qnap_rc": r.returncode, "qnap_path": dest if r.returncode == 0 else None,
            "qnap_log": (r.stdout + r.stderr).strip()[-300:]}


def _resolve(name, character, actor, tone, frames, description):
    # Package 2 R17: generic costume words are wardrobe, never INDEX aliases.
    scene_addenda.guard_parody_name(name)
    scene_addenda.guard_parody_name(character)
    req = {
        "names": [name] if name else [],
        "character": character,
        "actor": actor,
        "tone": tone,
        "length_s": int(round(frames / 24)),
        "description": str(description).strip(),
    }
    resolved = resolve_identities(req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
    # KTD3 / R8: fail closed before any run artifact when a non-good identity has no local RefMod.
    if resolved.get("index_status") != "good" and not resolved.get("loaded_refmods"):
        who = character or actor or name
        raise ValueError(
            f"No local RefMod installed for '{who}' ({resolved.get('index_flag')}) in {REFMODS_DIR}; "
            "refusing to queue a render without identity assets (install a RefMod or use an INDEX good identity)."
        )
    return resolved


def plan_cells(
    seconds: Optional[float],
    scene: Optional[str],
    dialogue: Optional[str],
    camera: Optional[str],
    beats: Optional[Sequence[str]],
    beat_dialogues: Optional[Sequence[str]],
    beat_cameras: Optional[Sequence[str]],
    beat_seconds: Optional[Sequence[float]],
    max_frames: int,
) -> Optional[List[Dict[str, Any]]]:
    """U1: None for a single clip, else the ordered shared-anchor cell list [{scene, dialogue, camera, frames}]."""
    beats = [b for b in (beats or []) if b and str(b).strip()]
    max_s = max_frames / float(br.H3_FPS)
    if len(beats) <= 1 and not (seconds and seconds > max_s):
        return None
    if len(beats) <= 1:
        n = int(math.ceil(float(seconds) / max_s))
        base = beats[0] if beats else scene
        beats = [base] * n
    n = len(beats)
    per = (float(seconds) / n) if seconds else None
    cells = []
    for i, b in enumerate(beats):
        bd = list(beat_dialogues or [])
        bc = list(beat_cameras or [])
        bs = list(beat_seconds or [])
        d = bd[i] if i < len(bd) else (dialogue if i == 0 else None)
        c = bc[i] if i < len(bc) else camera
        s = bs[i] if i < len(bs) else per
        frames = br.snap_h3_frames(s, max_frames=max_frames) if s else 124
        cells.append({"scene": b, "dialogue": d, "camera": c, "frames": frames})
    return cells


def submit_parody_job(
    name: str,
    character: Optional[str] = None,
    actor: Optional[str] = None,
    description: Optional[str] = None,
    tone: str = "parody",
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    seed: int = 51083601,
    frames: Optional[int] = None,
    slug: Optional[str] = None,
    run_dir_override: Optional[Path] = None,
    dry_run: bool = False,
    template_path: Path = DEFAULT_REFMOD_TEMPLATE,
    seconds: Optional[float] = None,
    aspect: Optional[str] = None,
    size: Optional[str] = None,
    camera: Optional[str] = None,
    pronoun: Optional[str] = None,
    end_action: Optional[str] = None,
    summary: Optional[str] = None,
    images: Optional[Sequence[str]] = None,
    image_role: Optional[str] = None,
    beats: Optional[Sequence[str]] = None,
    beat_dialogues: Optional[Sequence[str]] = None,
    beat_cameras: Optional[Sequence[str]] = None,
    beat_seconds: Optional[Sequence[float]] = None,
    name2: Optional[str] = None,
    character2: Optional[str] = None,
    actor2: Optional[str] = None,
    description2: Optional[str] = None,
    dialogue2: Optional[str] = None,
    pronoun2: Optional[str] = None,
    name3: Optional[str] = None,
    character3: Optional[str] = None,
    actor3: Optional[str] = None,
    description3: Optional[str] = None,
    dialogue3: Optional[str] = None,
    pronoun3: Optional[str] = None,
    partner_type2: Optional[str] = None,
    ambience: Optional[str] = None,
    wait: bool = False,
    qnap: bool = False,
    wait_timeout: float = WAIT_TIMEOUT_SEC,
    image_pools: Optional[Sequence[Path]] = None,
    image_input_dir: Optional[Path] = None,
    image_times: Optional[Sequence[Any]] = None,
    beat_new_shots: Optional[Sequence[Any]] = None,
    prequel_to: Optional[Union[str, Path]] = None,
    keep_comfy_process: bool = False,
) -> Dict[str, Any]:
    """Execute full parody pipeline from request to verified artifacts."""
    if run_dir_override is not None and not Path(run_dir_override).is_absolute():
        raise ValueError(f"--run-dir must be an absolute path: {run_dir_override}")
    if not description or not str(description).strip():
        raise ValueError("Biometric description (--description) is required for submit.")
    for _nm in (name, character, name2, character2, name3, character3):
        scene_addenda.guard_parody_name(_nm)

    target_prequel_mp4: Optional[Path] = None
    if prequel_to:
        target_prequel_mp4 = Path(prequel_to).resolve()
        if not target_prequel_mp4.is_file():
            raise FileNotFoundError(f"target clip to prequel not found: {target_prequel_mp4}")

    # 0. Length + canvas (validated before anything touches disk)
    max_frames = br.SINGLE_CLIP_MAX_FRAMES
    _nb = [b for b in (beats or []) if b and str(b).strip()]
    is_multi_beat = len(_nb) > 1
    _cap_s = max_frames / float(br.H3_FPS)
    if frames is None and seconds and float(seconds) > _cap_s and not is_multi_beat:
        raise ValueError(
            f"--seconds {float(seconds):g} is longer than one shot ({_cap_s:.1f}s): pass 2 or more --beat scenes, "
            "one distinct action per beat, or lower --seconds to fit one shot.")
    if frames is not None:
        frames = br.validate_single_clip_frames(frames)
    width, height = br.resolve_canvas(aspect, size)

    cells: Optional[List[Dict[str, Any]]] = None
    beat_specs: Optional[List[Dict[str, Any]]] = None
    chain_preview: Optional[List[Dict[str, Any]]] = None

    if is_multi_beat:
        raw_ns = list(beat_new_shots or [])
        if raw_ns and all(isinstance(x, bool) for x in raw_ns):
            ns_set = {idx + 1 for idx, flag in enumerate(raw_ns) if flag}
        else:
            ns_set = {int(x) for x in raw_ns}
        beat_specs = []
        for i, b in enumerate(_nb):
            bd = list(beat_dialogues or [])
            bc = list(beat_cameras or [])
            bs = list(beat_seconds or [])
            d = bd[i] if i < len(bd) else (dialogue if i == 0 else None)
            c = bc[i] if i < len(bc) else camera
            if i < len(bs) and bs[i]:
                f = br.snap_h3_frames(bs[i], max_frames=max_frames)
            elif seconds:
                f = br.snap_h3_frames(float(seconds) / len(_nb), max_frames=max_frames)
            elif frames is not None:
                f = frames
            else:
                f = None
            beat_specs.append({"scene": b, "dialogue": d, "camera": c, "frames": f,
                               "new_shot": (i + 1) in ns_set})
        chain_req = [
            int(s["frames"] or br.DEFAULT_CONTINUATION_BASE_FRAMES)
            for s in beat_specs
        ]
        chain_preview = br._layout_chain(chain_req)
        total_frames = chain_preview[-1]["frames"]
    else:
        cells = plan_cells(
            seconds, scene, dialogue, camera, beats, beat_dialogues, beat_cameras, beat_seconds, max_frames)
        if cells is None:
            if frames is None:
                frames = br.snap_h3_frames(seconds, max_frames=max_frames) if seconds else 124
            if beats:
                scene = [b for b in beats if b][0] if any(beats) else scene
        total_frames = sum(c["frames"] for c in cells) if cells else frames
        if cells and int(seed) < 100000:
            raise ValueError("multi-cell runs need a seed of at least 6 digits (cell dir form c01_s<seed>)")

    # 1. Resolve identities (S1 + optional S2), images gate
    resolved = _resolve(name, character, actor, tone, total_frames, description)
    resolved2 = None
    if name2 or character2 or actor2:
        if not description2 or not str(description2).strip():
            raise ValueError("--description2 is required when a second subject (--name2) is given.")
        resolved2 = _resolve(name2, character2, actor2, tone, total_frames, description2)
    resolved3 = None
    if name3 or character3 or actor3:
        if not description3 or not str(description3).strip():
            raise ValueError("--description3 is required when a third subject (--name3) is given.")
        resolved3 = _resolve(name3, character3, actor3, tone, total_frames, description3)
    valid_images = validate_reference_images(list(images or []), pools=tuple(image_pools) if image_pools else None) \
        if images else []

    # 2. Plan C2V continuation (single clip never chains; cells are stitched; 2+ beats use native continuation)
    chain_plan = None
    if not is_multi_beat:
        chain_plan = plan_c2v_chain(total_length_s=(cells[0]["frames"] if cells else frames) / 24,
                                    clip_frames=(cells[0]["frames"] if cells else frames))

    # 3. Determine run folder
    if run_dir_override:
        run_dir = Path(run_dir_override)
        if not run_dir.is_absolute():
            raise ValueError(f"--run-dir must be an absolute path: {run_dir_override}")
        run_name = run_dir.name
    else:
        ident_slug = slug or (character or actor or name).lower().replace(" ", "_")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"parody_{ident_slug}_{ts}"
        run_dir = RUNS_ROOT / run_name

    # 4. Build every graph in memory first (guard + KEEP dials fail before run_dir exists)
    staged = br.stage_reference_images(valid_images, image_input_dir) if valid_images else []
    common = dict(resolved=resolved, template_path=template_path, width=width, height=height,
                  pronoun=pronoun, end_action=end_action, images=staged, image_role=image_role,
                  resolved2=resolved2, pronoun2=pronoun2, ambience=ambience,
                  resolved3=resolved3, pronoun3=pronoun3, partner_type2=partner_type2)
    jobs: List[Dict[str, Any]] = []
    continuation = None
    if cells is None and not is_multi_beat:
        graph, prompt = build_parody_request(
            seed=seed, prefix=f"community/{run_name}/{QUEUE_TAG}", frames=frames, dialogue=dialogue,
            scene=scene, camera=camera, summary_text=summary, dialogue2=dialogue2,
            dialogue3=dialogue3, image_times=image_times, **common)
        jobs.append({"tag": QUEUE_TAG, "graph": graph, "prompt": prompt, "seed": seed, "frames": frames})
    elif is_multi_beat:
        assert beat_specs is not None and chain_preview is not None
        # (c) 2026-11-06 (brief t224x214) + argon-low Section C: a 2+ --beat list is ONE continuation graph, not N clips.
        # Map clip-level --image / --image-at times to Beat 1 (frame 0 + optional beat-1 pins) and Beat 2..N guides.
        b1_imgs, b1_times, mapped_guides = br.map_clip_images_to_beats(staged, image_times, chain_preview)
        req_frames = frames if (seconds is None and not beat_seconds and frames is not None) else None
        mapped_beats: List[Dict[str, Any]] = []
        for i, c in enumerate(beat_specs):
            b_idx = i + 1
            spec = dict(c)
            if i == 0:
                spec["images"] = b1_imgs if b1_imgs else None
                spec["image_times"] = b1_times if b1_times else None
            else:
                spec["images"] = None
                if b_idx in mapped_guides:
                    spec["beat_guides"] = mapped_guides[b_idx]
            mapped_beats.append(spec)
        graph, prompt, continuation = br.build_continuation_request(
            resolved=resolved, seed=seed, prefix=f"community/{run_name}/{QUEUE_TAG}",
            beats=mapped_beats,
            frames=req_frames, width=width, height=height, template_path=template_path,
            pronoun=pronoun, end_action=end_action, image_role=image_role, resolved2=resolved2,
            pronoun2=pronoun2, summary_text=summary, dialogue2=dialogue2, dialogue3=dialogue3,
            resolved3=resolved3, pronoun3=pronoun3, partner_type2=partner_type2, ambience=ambience)
        jobs.append({"tag": QUEUE_TAG, "graph": graph, "prompt": prompt, "seed": seed,
                     "frames": continuation["total_frames"]})
    else:
        for i, c in enumerate(cells):
            tag = f"c{i + 1:02d}_s{int(seed) + i}"
            g, p = build_parody_request(
                seed=int(seed) + i, prefix=f"community/{run_name}/{tag}", frames=c["frames"],
                dialogue=c["dialogue"], scene=c["scene"], camera=c["camera"],
                summary_text=summary if i == 0 else None, dialogue2=dialogue2 if i == 0 else None,
                dialogue3=dialogue3 if i == 0 else None, **common)
            jobs.append({"tag": tag, "graph": g, "prompt": p, "seed": int(seed) + i, "frames": c["frames"]})

    run_dir.mkdir(parents=True, exist_ok=True)
    if len(jobs) == 1:
        prompt_all = jobs[0]["prompt"]
    else:
        prompt_all = "\n\n".join(f"=== {j['tag']} ({j['frames']}f) ===\n{j['prompt']}" for j in jobs)
    total_frames = sum(j["frames"] for j in jobs)
    record_plan = continuation if continuation is not None else (chain_plan if len(jobs) == 1 else {
        "is_chained": False, "mode": "shared_anchor_cells", "clip_count": len(jobs),
        "cells": [{"tag": j["tag"], "frames": j["frames"], "seed": j["seed"]} for j in jobs],
        "total_frames": total_frames,
    })

    # 5. Save run record (request.api.json, prompt.txt, assets.json)
    artifacts = save_run_record(
        run_dir=run_dir,
        resolved=resolved,
        prompt=prompt_all,
        graph=jobs[0]["graph"],
        chain_plan=record_plan,
        clip_source=None,
    )

    for j in jobs:
        jd = run_dir / j["tag"]
        jd.mkdir(parents=True, exist_ok=True)
        (jd / "request.api.json").write_text(json.dumps(j["graph"], indent=2, ensure_ascii=False), encoding="utf-8")
        if len(jobs) > 1:
            (jd / "prompt.txt").write_text(j["prompt"], encoding="utf-8")
    order: Dict[str, Any] = {
        "order": [{
            "pos": i + 1,
            "tag": j["tag"],
            "arm": "parody",
            "scene": character or actor or name,
            "seed": j["seed"],
        } for i, j in enumerate(jobs)]
    }
    if len(jobs) > 1:
        order = {"cell_contract": True, **order}
    order_file = run_dir / "_render_order.json"
    order_file.write_text(json.dumps(order, indent=2, ensure_ascii=False), encoding="utf-8")

    summary_info = {
        "run_name": run_name,
        "frames": [j["frames"] for j in jobs],
        "total_frames": total_frames,
        "size": f"{width}x{height}",
        "tags": [j["tag"] for j in jobs],
        "images": staged,
    }
    if target_prequel_mp4:
        summary_info["prequel_to"] = str(target_prequel_mp4)
        summary_info["prequel_stitch"] = True

    if dry_run:
        print(f"[DRY-RUN] Parody request prepared at {run_dir}")
        print(f"  Mode:         {resolved.get('mode')}")
        print(f"  INDEX status: {resolved.get('index_status')}")
        print(f"  RefMods:      {resolved.get('loaded_refmods')}")
        print(f"  Frames:       {summary_info['frames']} size={summary_info['size']}")
        return {
            "dry_run": True,
            "run_dir": str(run_dir),
            "artifacts": {k: str(v) for k, v in artifacts.items()},
            "resolved": resolved,
            **summary_info,
        }

    # 6. Submit through the shared queue route. Detach returns after the batch PID is created.
    if os.name != "nt":  # EVO-X3 2026-11-15: no local ComfyUI/run_queue route; renders stay on AlienPc
        raise RuntimeError("X3: --queue is not wired through run_queue.py; after Derrick's yes use "
                           "~/AI/render/x3/queue-remote.sh <run_dir> (AlienPc ComfyUI over the tailnet)")
    python = str(QUEUE_PYTHON) if QUEUE_PYTHON.is_file() else sys.executable
    since = _batch_count(run_dir)
    cmd = [
        python,
        "-u",
        str(RUN_QUEUE_PY),
        "--run-dir",
        str(run_dir),
        "--size",
        f"{width}x{height}",
        "--frames",
        str(jobs[0]["frames"]),
        "--detach",
    ]
    if keep_comfy_process:  # chained mode (keep-comfy-part1, 2026-11-15): only when the caller asked
        cmd.append("--keep-comfy-process")

    print(f"Submitting render queue: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    base = {
        "returncode": proc.returncode,
        "run_dir": str(run_dir),
        "queue_order": str(order_file),
        "queue_log": str(run_dir / "_render_queue.log"),
        "artifacts": {k: str(v) for k, v in artifacts.items()},
        "resolved": resolved,
        **summary_info,
    }
    if proc.returncode == GPU_BUSY_RC:
        return dict(base, submitted=False, detached=False, gpu_busy=True)
    if proc.returncode != 0:
        raise RuntimeError(f"run_queue.py --detach failed with returncode {proc.returncode}")
    res = dict(base, submitted=True, detached=True, gpu_busy=False)
    if not wait:
        return res

    # 7. --wait: block on the detached batch, then finalize clip.mp4 (+ stitch) and optionally upload.
    t0 = time.time()
    rc = wait_for_batch(run_dir, since, timeout=wait_timeout)
    res.update(batch_rc=rc, gpu_busy=(rc == GPU_BUSY_RC), wait_seconds=round(time.time() - t0, 1),
               objective=objective_lines(run_dir), final_mp4=None, qnap_path=None)
    if rc != 0:
        return res
    res.update(finalize_clip(run_dir, [j["tag"] for j in jobs], python, prequel_to=target_prequel_mp4))
    if qnap:
        res.update(qnap_put(Path(res["final_mp4"]), run_name, python))
    return res


# --- writer hook ----------------------------------------------------------------------------------------------------
# Writer runs accept all adult RefMods and voice refs (OC, PixlStash-tagged, or INDEX character/celebrity RefMods);
# every person in the clip is an adult 18+.
OC_WRITER_FICTIONAL_REFMODS = frozenset({"minimaxh3_adamjensen_v1_refmod"})


def _writer_refmods_ok(graph: Dict[str, Any]) -> List[str]:
    """Problems with the base graph's RefMods ([] = OK)."""
    mods = [v for k, v in (graph.get("refmods", {}).get("inputs") or {}).items()
            if k.startswith("mod_") and isinstance(v, str) and v and v != "(none)"]
    if not mods:
        return ["base graph has no RefMods"]
    return []

def _graph_img1(graph: Dict[str, Any]) -> str:
    return str(((graph.get("img_1") or {}).get("inputs") or {}).get("image") or "").strip()


def _graph_mod_values(graph: Dict[str, Any]) -> List[str]:
    return [v for k, v in (graph.get("refmods", {}).get("inputs") or {}).items()
            if k.startswith("mod_") and isinstance(v, str) and v and v != "(none)"]


def _mod_stem(value: str) -> str:
    v = Path(str(value)).name
    return v[:-12] if v.lower().endswith(".safetensors") else v


def _clear_refmod_slots(graph: Dict[str, Any]) -> None:
    inp = (graph.setdefault("refmods", {})).setdefault("inputs", {})
    for k in list(inp):
        if k.startswith("mod_"):
            inp[k] = "(none)"


def _set_refmod_slots(graph: Dict[str, Any], stems: Sequence[str]) -> None:
    _clear_refmod_slots(graph)
    inp = graph["refmods"]["inputs"]
    for i, stem in enumerate(list(stems)[:8], 1):
        inp[f"mod_{i}"] = _mod_stem(stem)


_OC_KEY_RE = re.compile(r"(?i)minimaxh3_oc_([^_]+)_")
_OC_VER_RE = re.compile(r"(?i)_v(\d+)_")


def _keep_highest_oc_version(stems: Sequence[str]) -> List[str]:
    """When multiple versions (v1, v2) of the same OC key appear in stems, keep only the highest version.

    A voice RefMod trimmed to fit a continuation beat's cond_audio cap (`<name>_23s`,
    build_request.CONTINUATION_VOICE_REFMOD_SUFFIX) is a DERIVED copy of a reference that exists in full form:
    build_request._continuation_voice_refmods wires it on one continuation beat from that beat's own layout.
    It is never a character's voice reference for a base beat - two audio RefMods there pack
    2*(1000+920)=3840 rows against the 2000 a voice reference carries, the over-cap family of the live c2_samp
    failure (2026-11-15, [2000,32] vs [2130,32]). So a trim is dropped exactly when the file it was cut from is
    in the same list; a list with only a trim keeps it (a character whose full reference is not installed).
    """
    max_ver: Dict[str, int] = {}
    for s in stems:
        m = _OC_KEY_RE.search(s)
        if m:
            vm = _OC_VER_RE.search(s)
            ver = int(vm.group(1)) if vm else 0
            k = m.group(1).lower()
            if ver > max_ver.get(k, -1):
                max_ver[k] = ver
    out: List[str] = []
    for s in stems:
        m = _OC_KEY_RE.search(s)
        if m:
            vm = _OC_VER_RE.search(s)
            ver = int(vm.group(1)) if vm else 0
            k = m.group(1).lower()
            if ver < max_ver.get(k, 0):
                continue
        out.append(s)
    trim = br.CONTINUATION_VOICE_REFMOD_SUFFIX
    drop = {s for s in out if str(s).endswith(trim) and str(s)[: -len(trim)] in out}
    return [s for s in out if s not in drop]


def installed_oc_refmod_keys(refmods_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    """Map oc_* keys (poolclub, poolblonde) to installed RefMod stems (highest v<N> pair per key)."""
    d = Path(refmods_dir or REFMODS_DIR)
    keys: Dict[str, List[str]] = {}
    if not d.is_dir():
        return keys
    for f in sorted(d.glob("*.safetensors")):
        m = _OC_KEY_RE.search(f.stem)
        if m:
            keys.setdefault(m.group(1).lower(), []).append(f.stem)
    for k, stems in list(keys.items()):
        keys[k] = _keep_highest_oc_version(stems)
    return keys


def oc_keys_in_text(*parts: Optional[str]) -> List[str]:
    blob = " ".join(p for p in parts if p).replace("\\", "/").lower()
    if not blob:
        return []
    found: List[str] = []
    for k in installed_oc_refmod_keys():
        token = r"(?:^|[/_\s-])%s(?:[/_\s-]|$)"
        if re.search(r"(?i)" + (token % ("oc[_-]?" + re.escape(k))), blob) or re.search(
            r"(?i)" + (token % re.escape(k)), blob
        ):
            found.append(k)
    return found



# Exact path components (case-insensitive) that resolve to an OC key.
# Not substring matches. Do not alias SYDNEY or ORC_POOL_EDGE.
_OC_PATH_COMPONENT_ALIASES = {
    "pool": "poolclub",  # approved_characters\POOL -> trained trigger FCSydny
    "fcmegan": "meganfox",  # approved_characters\FCMegan -> minimaxh3_meganfox_v1_refmod
}

_PIXLSTASH_VAULTS = (
    _AI_ROOT / "5slock" / "approved_characters" / "vault.db",
    _AI_ROOT / "5slock" / "libraries" / "vault.db",
)
_STILL_LIBRARY_ROOTS = (
    _AI_ROOT / "5slock" / "approved_characters",
    _AI_ROOT / "render" / "stills" / "approved_characters",
)


def _norm_fs(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lower()


def _still_path_parts(still_image: Optional[str]) -> List[str]:
    if not still_image:
        return []
    rel = _norm_fs(still_image)
    for root in _STILL_LIBRARY_ROOTS:
        prefix = _norm_fs(str(root)).rstrip("/") + "/"
        if rel.startswith(prefix):
            rel = rel[len(prefix):]
            break
    return [p for p in rel.split("/") if p]


def _safetensors_metadata(path: Path) -> Dict[str, Any]:
    """Read the safetensors JSON header only (no tensor load)."""
    try:
        with path.open("rb") as f:
            n = int.from_bytes(f.read(8), "little")
            if n <= 0 or n > 4_000_000:
                return {}
            raw = f.read(n)
        header = json.loads(raw.decode("utf-8"))
        meta = header.get("__metadata__") or {}
        if not isinstance(meta, dict):
            return {}
        out: Dict[str, Any] = {}
        for k, v in meta.items():
            if isinstance(v, str):
                try:
                    out[k] = json.loads(v)
                except Exception:
                    out[k] = v
            else:
                out[k] = v
        return out
    except Exception:
        return {}


def trained_oc_subject_keys(refmods_dir: Optional[Path] = None) -> Dict[str, str]:
    """Map a normalized trained subject_name (e.g. fcsydny) to an OC key (poolclub).

    Prefers top-level subject_name over nested refmod_meta.subject_name.
    """
    d = Path(refmods_dir or REFMODS_DIR)
    mapping: Dict[str, str] = {}
    if not d.is_dir():
        return mapping
    for f in d.glob("minimaxh3_oc_*_refmod_visual.safetensors"):
        m = _OC_KEY_RE.search(f.stem)
        if not m:
            continue
        key = m.group(1).lower()
        meta = _safetensors_metadata(f)
        top = meta.get("subject_name")
        if not isinstance(top, str):
            top = ""
        nested = ""
        rm = meta.get("refmod_meta")
        if isinstance(rm, dict):
            nested = rm.get("subject_name") or ""
        if not isinstance(nested, str):
            nested = ""
        subject = (top.strip() or nested.strip())
        if subject:
            mapping[_norm_ident(subject)] = key
    return mapping


def oc_keys_from_path_components(still_image: Optional[str]) -> List[str]:
    found: List[str] = []
    for part in _still_path_parts(still_image):
        alias = _OC_PATH_COMPONENT_ALIASES.get(part.lower())
        if alias and alias not in found:
            found.append(alias)
    return found


def pixlstash_character_names_for_still(still_image: Optional[str]) -> List[str]:
    """PixlStash character names tagged on this still. Empty if the vault is missing."""
    if not still_image:
        return []
    rel = "/".join(_still_path_parts(still_image))
    candidates = {_norm_fs(still_image)}
    try:
        resolved = Path(still_image)
        if resolved.exists():
            candidates.add(_norm_fs(str(resolved.resolve())))
    except Exception:
        pass
    if rel:
        for root in _STILL_LIBRARY_ROOTS:
            candidates.add(_norm_fs(str(root / rel)))
        candidates.add(_norm_fs(rel))
    names: List[str] = []
    import sqlite3
    for vault in _PIXLSTASH_VAULTS:
        if not vault.is_file():
            continue
        try:
            con = sqlite3.connect("file:%s?mode=ro" % vault.as_posix(), uri=True)
            cur = con.cursor()
            rows = cur.execute(
                """
                SELECT c.name, p.file_path
                FROM face f
                JOIN character c ON c.id = f.character_id
                JOIN picture p ON p.id = f.picture_id
                WHERE f.character_id IS NOT NULL
                """
            ).fetchall()
            con.close()
        except Exception:
            continue
        for name, fpath in rows:
            if not name:
                continue
            fp = _norm_fs(fpath)
            if fp in candidates or (rel and (fp.endswith("/" + rel.lower()) or fp == rel.lower())):
                if name not in names:
                    names.append(name)
        if names:
            return names
    return names


def oc_keys_from_trained_subjects(*names: Optional[str]) -> List[str]:
    mapping = trained_oc_subject_keys()
    if not mapping:
        return []
    found: List[str] = []
    for name in names:
        if not name:
            continue
        key = mapping.get(_norm_ident(name))
        if key and key not in found:
            found.append(key)
    return found


def oc_keys_for_still_and_names(still_image: Optional[str] = None, *name_parts: Optional[str]) -> List[str]:
    """OC keys from path tokens, the POOL folder alias, trained triggers, and PixlStash tags."""
    found: List[str] = []

    def add(keys: List[str]) -> None:
        for k in keys:
            if k and k not in found:
                found.append(k)

    add(oc_keys_in_text(still_image, *name_parts))
    add(oc_keys_from_path_components(still_image))
    add(oc_keys_from_trained_subjects(*name_parts))
    mapping = trained_oc_subject_keys()
    if mapping:
        for part in _still_path_parts(still_image):
            for token in (part, Path(part).stem):
                key = mapping.get(_norm_ident(token))
                if key and key not in found:
                    found.append(key)
    add(oc_keys_from_trained_subjects(*pixlstash_character_names_for_still(still_image)))
    return found


def _is_writer_lane_refmod(stem: str) -> bool:
    return bool(_mod_stem(stem))


def _stems_for_character_name(name: str) -> List[str]:
    from resolve import find_refmods_for_name, load_aliases
    if not (name or "").strip():
        return []
    norm_q = re.sub(r"[^a-z0-9]", "", name.lower())
    files = (find_refmods_for_name(norm_q, REFMODS_DIR) or []) if norm_q else []
    if not files and norm_q:
        alias_target = _OC_PATH_COMPONENT_ALIASES.get(norm_q) or (load_aliases(ALIASES_PATH) or {}).get(norm_q)
        if alias_target:
            alias_norm = re.sub(r"[^a-z0-9]", "", alias_target.lower())
            files = (find_refmods_for_name(alias_norm, REFMODS_DIR) or []) if alias_norm else []
    stems = [_mod_stem(getattr(f, "stem", f)) for f in files]
    key = trained_oc_subject_keys().get(_norm_ident(name))
    if key:
        for s in installed_oc_refmod_keys().get(key, []):
            if s not in stems:
                stems.append(s)
    return _keep_highest_oc_version(stems)



def _norm_ident(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _name_matches_field(name: str, field: str) -> bool:
    n, f = _norm_ident(name), _norm_ident(field)
    if not n or not f:
        return False
    if n == f:
        return True
    # Token match, but skip short fragments ("the", "of").
    return n in f.split() and len(n) >= 4


def index_named_identity(name: Optional[str]) -> bool:
    """True when the name is a character INDEX or aliases entry, not an installed OC key."""
    if not (name or "").strip():
        return False
    n = _norm_ident(name)
    if n in installed_oc_refmod_keys() or n in trained_oc_subject_keys():
        return False
    try:
        from resolve import load_aliases, load_index_files
        aliases = load_aliases(ALIASES_PATH) or {}
        for k, v in aliases.items():
            if _name_matches_field(n, k) or _name_matches_field(n, v):
                return True
        for row in load_index_files(INDEX_DIR) or []:
            if _name_matches_field(n, str(row.get("character") or "")) or _name_matches_field(n, str(row.get("actor") or "")):
                return True
    except Exception:
        return False
    return False


def resolve_writer_refmods(
    still_image: Optional[str] = None,
    character: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Pick installed visual/audio RefMods for the writer hook across OC, INDEX, and PixlStash tags.

    Uses aliases + INDEX + local RefMod files (all adult RefMods and voice refs allowed), trained
    RefMod triggers (e.g. FCSydny), PixlStash character tags, or approved POOL path components.
    Never guesses a likeness from a bare still filename, and never reuses the previous run's RefMods.
    Stills are not passed to validate_stills (writer stills may live outside approved_characters).
    """
    out: Dict[str, Any] = {"stems": [], "source": None, "reason": None, "index": None, "trigger": None}
    char = (character or "").strip() or None
    name_list = [n for n in (list(names) if names else []) if str(n).strip()]

    def _oc_trigger(stems: Sequence[str]) -> Optional[str]:
        """The trained RefMod trigger word (e.g. FCSydny) of the visual RefMod just attached, from its own
        safetensors subject_name. Only for minimaxh3_oc_* files; None for INDEX/celebrity RefMods."""
        d = Path(REFMODS_DIR)
        for s in stems:
            stem = _mod_stem(str(s))
            if not re.search(r"(?i)^minimaxh3_oc_", stem):
                continue
            f = d / (stem + ".safetensors")
            if not f.is_file():
                continue
            subj = _safetensors_metadata(f).get("subject_name")
            if isinstance(subj, str) and subj.strip():
                return subj.strip()
        return None

    def _resolve_names(targets: Sequence[str]) -> List[str]:
        found: List[str] = []
        seen: set = set()
        for n in targets:
            for s in _stems_for_character_name(str(n)):
                if _is_writer_lane_refmod(s) and s not in seen:
                    seen.add(s)
                    found.append(s)
        try:
            tlist = [str(n).strip() for n in targets if str(n).strip()]
            req = {
                "names": tlist,
                "character": tlist[0] if tlist else "",
                "actor": "",
                "tone": "",
                "length_s": 10,
                "description": "adult figure with eyes, hair, and outfit",
            }
            resolved = resolve_identities(req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
            loaded = [_mod_stem(x) for x in (resolved.get("loaded_refmods") or [])]
            out["index"] = {
                "index_status": resolved.get("index_status"),
                "index_flag": resolved.get("index_flag"),
                "loaded": loaded,
            }
            for s in loaded:
                if _is_writer_lane_refmod(s) and s not in seen:
                    seen.add(s)
                    found.append(s)
        except Exception as e:
            out["index_error"] = f"{type(e).__name__}: {e}"
        return _keep_highest_oc_version(found)

    if char or name_list:
        targets = ([char] if char else []) + [n for n in name_list if n != char]
        matched = _resolve_names(targets)
        if matched:
            out["stems"] = matched
            out["source"] = "character"
            out["trigger"] = _oc_trigger(matched)
            return out
        who = char or (name_list[0] if name_list else "named identity")
        out["reason"] = f"no local RefMod installed for '{who}' in {REFMODS_DIR}"
        return out

    keys = oc_keys_for_still_and_names(still_image, char, " ".join(str(n) for n in name_list))
    if keys:
        inst = installed_oc_refmod_keys()
        stems: List[str] = []
        seen: set = set()
        for k in keys:
            for s in inst.get(k, []):
                if s not in seen:
                    seen.add(s)
                    stems.append(s)
            if not inst.get(k):
                for s in _stems_for_character_name(k):
                    if _is_writer_lane_refmod(s) and s not in seen:
                        seen.add(s)
                        stems.append(s)
        if stems:
            out["stems"] = _keep_highest_oc_version(stems)
            out["source"] = "still_path"
            out["trigger"] = _oc_trigger(out["stems"])
            return out

    tagged = pixlstash_character_names_for_still(still_image)
    if tagged:
        matched = _resolve_names(tagged)
        if matched:
            out["stems"] = matched
            out["source"] = "pixlstash"
            out["trigger"] = _oc_trigger(matched)
            return out

    out["reason"] = (
        "no RefMod matched this still via installed files, the trained trigger, "
        "the POOL folder, a PixlStash character tag, or the character name; "
        "will not reuse the previous run's RefMods. Pass a still tagged or filed as the character "
        "(for example FCSydny / poolclub or poolblonde), or pass --character <name>."
    )
    return out


def prepare_writer_base_graph(
    graph: Dict[str, Any],
    still_image: Optional[str] = None,
    character: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Start from the live locked template when the graph is a previous run or has no still, then attach RefMods."""
    still = (still_image or "").strip() or None
    char = (character or "").strip() or None
    name_list = [n for n in (list(names) if names else []) if str(n).strip()]
    report: Dict[str, Any] = {"template": False, "injected_still": False, "stems": [], "source": None}
    img = _graph_img1(graph)
    mods = _graph_mod_values(graph)
    mods_ok = bool(mods) and all(_is_writer_lane_refmod(m) for m in mods)
    keys = oc_keys_for_still_and_names(still) if still else []
    blob = " ".join(mods).lower()
    mods_match_keys = bool(keys) and all(k in blob for k in keys)

    def _pin_still(g: Dict[str, Any]) -> Dict[str, Any]:
        if not still:
            return g
        # The locked template has no img_1: inject AddGuide at frame 0. A director graph that
        # already has img_1 just gets the new still path; do not re-wire add_guide on a test stub.
        if "img_1" in g:
            g.setdefault("img_1", {}).setdefault("inputs", {})["image"] = still
            report["injected_still"] = True
            return g
        br.inject_reference_images(g, [still], frame_indices=[0])
        report["injected_still"] = True
        return g

    # Explicit character / names always go through the INDEX + OC resolver.
    if char or name_list:
        picked = resolve_writer_refmods(still_image=still, character=char, names=name_list)
        if picked.get("reason") and not picked.get("stems"):
            report["reason"] = picked["reason"]
            report["index"] = picked.get("index")
            return graph, report
        graph = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        report["template"] = True
        report["template_path"] = str(DEFAULT_REFMOD_TEMPLATE)
        graph = _pin_still(graph)
        _set_refmod_slots(graph, picked.get("stems") or [])
        report["stems"] = list(picked.get("stems") or [])
        report["source"] = picked.get("source")
        report["index"] = picked.get("index")
        return graph, report

    # Still path names an OC character the current slots do not already have: rematch.
    if keys and not mods_match_keys:
        picked = resolve_writer_refmods(still_image=still)
        if picked.get("reason") and not picked.get("stems"):
            report["reason"] = picked["reason"]
            report["index"] = picked.get("index")
            return graph, report
        graph = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        report["template"] = True
        report["template_path"] = str(DEFAULT_REFMOD_TEMPLATE)
        graph = _pin_still(graph)
        _set_refmod_slots(graph, picked.get("stems") or [])
        report["stems"] = list(picked.get("stems") or [])
        report["source"] = picked.get("source")
        report["index"] = picked.get("index")
        return graph, report

    # Copied previous run: the start still changed, the path names no OC character, do not keep the last RefMods.
    img_mismatch = bool(still and img and Path(img).name.lower() != Path(still).name.lower())
    if img_mismatch and not keys:
        picked = resolve_writer_refmods(still_image=still)
        if picked.get("stems"):
            graph = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
            report["template"] = True
            report["template_path"] = str(DEFAULT_REFMOD_TEMPLATE)
            graph = _pin_still(graph)
            _set_refmod_slots(graph, picked["stems"])
            report["stems"] = list(picked["stems"])
            report["source"] = picked.get("source")
            report["index"] = picked.get("index")
            return graph, report
        report["reason"] = picked.get("reason") or (
            "the start still changed and no RefMod matched the new still; will not reuse the previous run's RefMods"
        )
        report["index"] = picked.get("index")
        return graph, report

    if mods_ok:
        graph = _pin_still(graph)
        report["stems"] = [_mod_stem(m) for m in mods]
        report["source"] = "existing"
        return graph, report

    if not mods:
        picked = resolve_writer_refmods(still_image=still, character=char, names=name_list)
        if picked.get("reason") and not picked.get("stems"):
            report["reason"] = picked["reason"]
            report["index"] = picked.get("index")
            return graph, report
        graph = json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        report["template"] = True
        report["template_path"] = str(DEFAULT_REFMOD_TEMPLATE)
        graph = _pin_still(graph)
        _set_refmod_slots(graph, picked.get("stems") or [])
        report["stems"] = list(picked.get("stems") or [])
        report["source"] = picked.get("source")
        return graph, report

    if still and "img_1" not in graph:
        graph = _pin_still(graph)
    report["stems"] = [_mod_stem(m) for m in mods]
    report["source"] = "existing"
    return graph, report


def _normalize_comfy_still(still: Optional[str]) -> Optional[str]:
    """Normalize a writer start-still path to a ComfyUI input-relative path for LoadImage."""
    if not (isinstance(still, str) and still.strip()):
        return still
    s = still.strip()
    norm = s.replace("\\", "/")
    comfy_in = br.COMFY_INPUT_COMMUNITY.parent
    for marker in ("stills/comfy_input/",):
        idx = norm.lower().find(marker)
        if idx >= 0:
            rel = norm[idx + len(marker):].lstrip("/")
            if rel and (comfy_in / rel).is_file():
                return rel
    p = Path(s)
    if p.is_file():
        try:
            rel = p.resolve().relative_to(comfy_in.resolve())
            return rel.as_posix()
        except ValueError:
            staged = br.stage_reference_images([str(p)])
            if staged:
                return staged[0]
    return s


def submit_writer_run(
    raw: Any,
    base_graph: Any,
    run_dir: Path,
    ask: str,
    position: str,
    still_image: Optional[str] = None,
    still_read: Optional[Dict[str, Any]] = None,
    still_path: Optional[str] = None,
    vision: Optional[Any] = None,
    writer: Optional[Any] = None,
    seed: int = 51083601,
    frames: int = br.SINGLE_CLIP_MAX_FRAMES,
    cast_overrides: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
    prequel_to: Optional[Union[str, Path]] = None,
    character: Optional[str] = None,
    names: Optional[Sequence[str]] = None,
    partner_type2: Optional[str] = None,
    partner_type: Optional[str] = None,
    continued: bool = False,
    keep_comfy_process: bool = False,
) -> Dict[str, Any]:
    """Render's production hook for a free-text OC writer prompt: after the writer call, before graph submit.

    raw          the writer's output text, or a write() callable (returns raw or (raw, completion_tokens)); a callable
                 goes through br.gated_write (refusal / no description / act:false -> one retry -> NOT_READY)
    base_graph   an OC RefMod graph (dict or request.api.json path) built on the locked template; only c0 prompt,
                 length, size, seed, save prefix and img_1 change - sampling and dials are untouched
    still_read   the structured vision read of <Picture 1>; or pass still_path + vision (chat(messages) -> text) and the
                 builder reads it (br.vision_read). No read = NOT_READY (no bedroom fallback)
    writer       optional repair callable (user text -> reply) for the lint repair loop (max 2 rounds)
    Fails closed: on any hard stop writes <run_dir>/clip_NOT_READY.txt and build_report.json and submits nothing.
    frs16 (Fleet Reviewer S3/S4/S6, 2026-11-11): any exception before the queue call (bad base graph, no c0, pysbd / PIL
    import, a failed or timed-out run_queue.py) is NOT_READY too, never a bare traceback; a dry run writes a DRY_RUN marker
    and no _render_order.json; a missing or empty still path (img_1) is NOT_READY."""
    run_dir = Path(run_dir)
    tag = QUEUE_TAG
    report: Dict[str, Any] = {"hook": "submit_parody_run.submit_writer_run", "builder": None, "builder_sha256": None,
                              "ask": ask, "position": position, "seed": seed, "frames": frames, "status": None,
                              "submitted": False, "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S CT")}

    def write_report() -> None:
        (run_dir / "build_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    def not_ready(reason: str, diag: Optional[str] = None) -> Dict[str, Any]:
        report.update(status="NOT_READY", reason=reason)
        try:
            run_dir.mkdir(parents=True, exist_ok=True)
            body = f"NOT_READY: {reason}\n" + (f"\n--- non-strict diagnostic build (NOT for render) ---\n{diag}\n" if diag else "")
            (run_dir / f"{tag}_NOT_READY.txt").write_text(body, encoding="utf-8")
            write_report()
        except Exception as e:  # still NOT_READY (the caller exits 3); the files could not be written
            report["report_write_error"] = f"{type(e).__name__}: {e}"
        return dict(report, run_dir=str(run_dir))

    def body() -> Dict[str, Any]:
        nonlocal raw, still_read, position
        run_dir.mkdir(parents=True, exist_ok=True)
        bpath = Path(br.__file__)
        report.update(builder=str(bpath), builder_sha256=hashlib.sha256(bpath.read_bytes()).hexdigest().upper())
        graph0 = json.loads(Path(base_graph).read_text(encoding="utf-8")) if not isinstance(base_graph, dict) else base_graph
        # Max Architect 3, Derrick t1109u: start from the live locked template when the graph still or
        # RefMods belong to a previous run; attach the matching OC RefMod via still path or character INDEX.
        # Do not run approved_characters-only validate_stills on writer stills.
        still_for_ref = (still_image or still_path or "").strip() or None
        graph0, attach = prepare_writer_base_graph(
            graph0, still_image=still_for_ref, character=character, names=names,
        )
        report["refmods"] = {k: attach.get(k) for k in ("template", "template_path", "injected_still", "stems", "source", "index", "trigger") if k in attach}
        if attach.get("reason"):
            return not_ready(attach["reason"])
        bad = _writer_refmods_ok(graph0)
        if bad:
            return not_ready("; ".join(bad))
        if isinstance(still_for_ref, str) and still_for_ref and "img_1" not in graph0:
            br.inject_reference_images(graph0, [still_for_ref], frame_indices=[0])
        if prequel_to:
            target_path = Path(prequel_to).resolve()
            if not target_path.is_file():
                return not_ready(f"target clip to prequel not found: {target_path}")
            report["prequel_to"] = str(target_path)
            report["prequel_stitch"] = True
        try:
            if still_read is None and vision is not None and still_path:
                still_read = br.vision_read(still_path, vision)
            if not still_read:
                return not_ready("no still read (vision facts) for <Picture 1>; the builder has no bedroom fallback")
            still_people = None
            if isinstance(still_read, dict) and still_read.get("people"):
                still_people = len(still_read["people"]) if isinstance(still_read["people"], list) else still_read["people"]
            hook_act = (br.get_act(position) or {}).get("id") if position else None
            brief = scene_addenda.resolve_brief(
                ask or "", act_id=hook_act, registry=br.load_acts_registry(),
                still_people=still_people if isinstance(still_people, int) else None,
            )
            if not hook_act and brief.get("act_id") and br.get_act(brief["act_id"]):
                position = brief["act_id"]
                report["position"] = position
            if brief.get("not_ready"):
                _nr = brief["not_ready"]
                if "still shows" not in _nr or "brief asks for" not in _nr:
                    return not_ready(_nr)
            report["scene_addenda"] = {
                k: brief.get(k) for k in (
                    "act_id", "partner_type", "states", "camera_kind", "offscreen_voice",
                    "look", "register", "flags", "s1_gender",
                )
            }
            mk = {}
            if brief.get("partner_type"):
                mk["partner_type"] = brief["partner_type"]
            if partner_type:  # router overlay (non-human creature partner) beats the brief's default
                mk["partner_type"] = partner_type
            if partner_type2:  # Max Architect 3, Derrick t1437s5374: MMF third person faceless (writer-run --partner-type2)
                mk["partner_type2"] = partner_type2
            if (cast_overrides or {}).get("s3_still"):  # (5) Derrick t247s837: S3 with a still keeps face (via its Picture) and voice
                mk["partner_type2"] = "still"
            ck = brief.get("camera_kind")
            if ck and ck not in ("third_person", "third-person"):
                mk["camera_kind"] = br._CAM_KIND_MAP.get(ck, ck)
            if continued or mk.get("continued"):
                mk["continued"] = True
            if isinstance((cast_overrides or {}).get("inherited_garments"), dict):
                mk["inherited_garments"] = dict(cast_overrides["inherited_garments"])
            if continued and isinstance((cast_overrides or {}).get("scene_read"), dict):
                mk["scene_read"] = cast_overrides["scene_read"]  # Max Architect, Derrick t271s933: Fix B clip-1 lock
            _is_male_solo = (brief.get("s1_gender") == "man") or ((hook_act or brief.get("act_id") or position) == "male_solo")
            if _is_male_solo and isinstance(still_read, dict):
                # Strip female wardrobe/hair/skin/build/pose/people so apply_still_facts & _garment_retention emit setting only.
                _sr_in = still_read.get("read") if isinstance(still_read.get("read"), dict) else still_read
                _sr_clean = dict(_sr_in)
                _sr_clean.update({"hair": "", "skin": "", "build": "", "pose": "", "garments": [], "facing_camera": False, "people": 0})
                still_read = dict(still_read, read=_sr_clean) if isinstance(still_read.get("read"), dict) else _sr_clean
            cast = br.make_cast(still_read, position, ask, **mk)
            if _is_male_solo and not (cast_overrides or {}).get("voice_s1"):
                cast["voice_s1"] = "a deep, steady adult man's voice, low and hoarse"
            cast.update({k: v for k, v in (cast_overrides or {}).items() if k != "scene_read"})
            # The trained RefMod trigger word of the attached OC visual RefMod (Derrick 2026-11-14): the builder
            # names it once in the <Subject 1> line. INDEX/celebrity RefMods have no trained trigger -> nothing added.
            if attach.get("trigger"):
                cast["refmod_trigger"] = str(attach["trigger"]).strip()
            report["still_read"] = still_read
            if callable(raw):
                raw, gate_log = br.gated_write(raw, cast=dict(cast), ask=ask)
                report["writer_gate"] = gate_log
                if raw is None:
                    return not_ready("writer gate failed twice: " + "; ".join(
                        r for a in gate_log["attempts"] for r in a["reasons"]))
            if not raw or not str(raw).strip():
                return not_ready("no writer output")
            (run_dir / "writer_output.txt").write_text(str(raw), encoding="utf-8")
            c0 = graph0["c0"]["inputs"]
            g, prompt, rep = br.build_writer_request(graph0, str(raw), cast, prefix=f"community/{run_dir.name}/{tag}", seed=seed,
                                                     frames=frames, width=int(c0.get("width") or br.DEFAULT_CANVAS[0]),
                                                     height=int(c0.get("height") or br.DEFAULT_CANVAS[1]), strict=True, writer=writer)
        except br.WriterPromptError as e:
            diag = None
            drep = None
            try:
                if still_read and isinstance(raw, str):
                    diag, drep = br.finalize_writer_prompt(raw, dict(br.make_cast(still_read, position, ask), **(cast_overrides or {})), strict=False)
                    if drep.get("packed_beats"):
                        report["packed_beats"] = drep["packed_beats"]
                        (run_dir / "split_briefs.json").write_text(json.dumps(drep["packed_beats"], indent=2, ensure_ascii=False), encoding="utf-8")
                    report["flags"] = drep.get("flags", [])
            except Exception as e2:  # diagnostic only
                diag = f"(non-strict build also failed: {e2})"
            # argon-low Section B: when a short clip is refused ONLY because it packs undress + the act and the
            # two split briefs are complete and safe, automatically build and submit ONE 2-beat native latent-tail
            # continuation job (beat 1 = 124f default or sized <= 243f, beat 2 = +187f extension, 311f total visible,
            # start still on beat 1 only). Never submit two separate single-clip jobs.
            if drep and br.packed_split_is_safe(drep) and not prequel_to:
                c0 = graph0["c0"]["inputs"]
                g, prompt, rep = br.build_writer_continuation_request(
                    graph0, str(raw), cast, prefix=f"community/{run_dir.name}/{tag}", seed=seed,
                    width=int(c0.get("width") or br.DEFAULT_CANVAS[0]),
                    height=int(c0.get("height") or br.DEFAULT_CANVAS[1]), drep=drep,
                )
                report["frames"] = rep["total_frames"]
                report["continuation"] = {k: rep[k] for k in ("mode", "clip_count", "base_frames", "extension_frames",
                                                               "overlap_frames", "window_frames", "total_frames", "total_seconds")}
            else:
                return not_ready(str(e), diag)
        # frs16 S6: the OC writer lane always opens on the start still; no path = NOT_READY (never the base graph's old img_1)
        if not (isinstance(still_image, str) and still_image.strip()):
            return not_ready("no start-still path for img_1 (<Picture 1>); pass the still under ComfyUI input, e.g. community/x.png")
        if Path(still_image.strip()).is_absolute() and not Path(still_image.strip()).is_file():
            return not_ready(f"start still file not found: {still_image}")
        if "img_1" not in g:
            return not_ready("base graph has no img_1 start-image node for <Picture 1>")
        g["img_1"]["inputs"]["image"] = (_normalize_comfy_still(still_image) or still_image).strip()
        report.update(status="READY", chars=len(prompt), prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest().upper(),
                      build=rep)
        (run_dir / f"{tag}_NOT_READY.txt").unlink(missing_ok=True)
        jd = run_dir / tag
        jd.mkdir(parents=True, exist_ok=True)
        (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        (jd / "request.api.json").write_text(json.dumps(g, indent=2, ensure_ascii=False), encoding="utf-8")
        (run_dir / "cast.json").write_text(json.dumps({k: v for k, v in cast.items() if k != "still_read"}, indent=2, ensure_ascii=False), encoding="utf-8")
        order_file = run_dir / "_render_order.json"
        marker = run_dir / "DRY_RUN"
        if dry_run:
            # frs16 S4: a dry dir is never a pre-built queue dir: DRY_RUN marker, no _render_order.json (run_queue.py's default order)
            if order_file.exists():
                order_file.unlink()
            marker.write_text("dry run of submit_writer_run: built for review only, never queue this dir\n", encoding="utf-8")
            report["dry_run"] = True
            write_report()
            return dict(report, run_dir=str(run_dir), prompt_path=str(run_dir / "prompt.txt"))
        if marker.exists():
            marker.unlink()
        order = {"order": [{"pos": 1, "tag": tag, "arm": "oc_writer", "scene": position, "seed": seed}]}
        order_file.write_text(json.dumps(order, indent=2), encoding="utf-8")
        if os.name != "nt":  # EVO-X3 2026-11-15: no local ComfyUI/run_queue route; renders stay on AlienPc
            raise RuntimeError("X3: --queue is not wired through run_queue.py; after Derrick's yes use "
                               "~/AI/render/x3/queue-remote.sh <run_dir> (AlienPc ComfyUI over the tailnet)")
        python = str(QUEUE_PYTHON) if QUEUE_PYTHON.is_file() else sys.executable
        q_frames = rep.get("total_frames") if isinstance(rep, dict) and rep.get("total_frames") else g["c0"]["inputs"]["length"]
        cmd = [python, "-u", str(RUN_QUEUE_PY), "--run-dir", str(run_dir), "--size",
               f"{g['c0']['inputs']['width']}x{g['c0']['inputs']['height']}", "--frames", str(q_frames), "--detach"]
        if keep_comfy_process:  # chained mode (keep-comfy-part1, 2026-11-15): only when the caller asked
            cmd.append("--keep-comfy-process")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            report["queue_rc"] = "timeout"
            return not_ready("run_queue.py --detach did not return within 180 s; not confirmed queued - check "
                             f"{run_dir / '_render_queue.log'} and the GPU lock before any retry")
        report.update(queue_rc=proc.returncode, submitted=proc.returncode == 0, gpu_busy=proc.returncode == GPU_BUSY_RC,
                      queue_log=str(run_dir / "_render_queue.log"))
        if proc.returncode not in (0, GPU_BUSY_RC):
            return not_ready(f"run_queue.py --detach failed with returncode {proc.returncode}; nothing queued")
        try:
            write_report()
        except Exception as e:  # queued already: report it, never turn a submitted clip into NOT_READY
            report["report_write_error"] = f"{type(e).__name__}: {e}"
        return dict(report, run_dir=str(run_dir))

    try:
        return body()
    except Exception as e:  # frs16 S3: fail closed with clip_NOT_READY.txt (exit 3 in the AGENTS call), never a traceback
        if report.get("submitted"):
            report["post_queue_error"] = f"{type(e).__name__}: {e}"
            return dict(report, run_dir=str(run_dir))
        return not_ready(f"hook error before the queue call, nothing queued ({type(e).__name__}: {e})")


def _s3_overrides(look: Optional[str], still: Optional[str], s2_look: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """MMF/FFM S2/S3: man/partner & man3/partner3 from beat card look; s3_still = the reference still, which must exist."""
    o: Dict[str, Any] = {}
    if s2_look:
        s2l = s2_look.strip().rstrip(".")
        if re.search(r"(?i)\b(?:woman|futa)\b", s2l):
            o["partner"] = s2l
        else:
            o["man"] = s2l
    if look:
        s3l = look.strip().rstrip(".")
        o["man3"] = s3l
        if re.search(r"(?i)\b(?:woman|futa)\b", s3l):
            o["partner3"] = s3l
    if still:
        p = Path(still)
        if not p.is_absolute():
            p = br.COMFY_INPUT_COMMUNITY.parent / still
        if not p.is_file():
            raise FileNotFoundError(f"S3 reference still not found: {still}")
        o["s3_still"] = still.strip()
    return o or None


def _writer_run_cli(argv) -> int:
    """Short Render entry (Max Architect 3, 2026-11-13 t1343u/t1345u): python submit_parody_run.py writer-run <run_dir>
    --ask "..." --position doggy --still <path> --character FCSydny [--queue]. Reads writer_output.txt and
    still_read.json from run_dir; base.api.json is optional (Max Architect 3, 2026-11-13, Derrick t1355): when it is
    missing the live locked template DEFAULT_REFMOD_TEMPLATE is loaded read-only (never written). Dry run unless
    --queue. Exit 0 READY, 3 NOT_READY (never a bare traceback)."""
    ap = argparse.ArgumentParser(prog="submit_parody_run.py writer-run")
    ap.add_argument("run_dir")
    ap.add_argument("--ask", required=True)
    ap.add_argument("--position", default="")
    ap.add_argument("--still", default=None)
    ap.add_argument("--character", default=None)
    ap.add_argument("--names", nargs="+", default=None, help="character/celebrity names for RefMod resolution")
    ap.add_argument("--partner-type2", default=None, choices=["man", "woman", "none", "non-human", "faceless", "still"])
    # Max Architect 3, Derrick t1440 (MMF S3): a generated S3 look, an S3 reference still, an optional frame cap for VRAM
    ap.add_argument("--s3-in-frame", action="store_true", help="continued clip: S3 is already in the inherited frame (no 'enters')")
    ap.add_argument("--continued", action="store_true", help="this clip continues a previous clip (skip opening-from-still)")
    ap.add_argument("--inherited-garments", default=None, help="JSON map of garment key -> prior state (aside/up/off/on) for continued clips")
    ap.add_argument("--scene-read", default=None, help="clip-1 still_read.json a continued clip keeps its cast and set from (default: run dir still_read.start.json)")
    ap.add_argument("--s2-look", default=None, help="S2 description from beat card, e.g. 'an adult man, thirty years of age, ...'")
    ap.add_argument("--s3-look", default=None, help="S3 description, e.g. 'an adult man, thirty years of age, ...'")
    ap.add_argument("--partner2-still", default=None, help="S3 reference still under ComfyUI input (community/x.jpg) or a full path")
    ap.add_argument("--frames", type=int, default=None, help="frame-count cap (VRAM: two reference stills peak near 15.4/16.3 GB)")
    ap.add_argument("--shots", default=None, choices=["single", "multi"], help="B1: multi keeps the writer's [Shot N] cuts (default single)")
    ap.add_argument("--partner-type", default=None, choices=["man", "woman", "futa", "none", "non-human", "faceless"])
    ap.add_argument("--queue", action="store_true", help="Actually queue (only when Derrick said to queue)")
    # keep-comfy-part1 (2026-11-15): chained runs pass this through to run_queue.py, which keeps the
    # comfyui_auto PROCESS alive at batch close (POST /free still runs). Default off: normal runs unchanged.
    ap.add_argument("--keep-comfy-process", action="store_true",
                    help="With --queue: run_queue.py skips only the llama-swap unload of comfyui_auto at batch "
                         "close, so the next clip in a chain does not pay the ~40 s process wake")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        print("NOT_READY submitted=False bad writer-run arguments (see usage above)")
        return 3
    d = Path(a.run_dir)
    if not d.is_absolute():
        print(f"NOT_READY submitted=False run_dir must be an absolute path: {a.run_dir}")
        return 3
    if not (a.still or "").strip():
        print("NOT_READY submitted=False start still missing: pass --still '<the start still path>'")
        return 3
    if Path(a.still.strip()).is_absolute() and not Path(a.still.strip()).is_file():
        print(f"NOT_READY submitted=False start still not found: {a.still}")
        return 3
    try:
        missing = [n for n in ("writer_output.txt", "still_read.json") if not (d / n).is_file()]
        if missing:
            print("NOT_READY submitted=False missing file(s) in run dir: " + ", ".join(missing))
            return 3
        # base.api.json optional: fall back to an in-memory copy of the locked template (read-only).
        base = d / "base.api.json"
        base_graph = str(base) if base.is_file() else json.loads(Path(DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
        inh_garments = None
        if getattr(a, "inherited_garments", None):
            inh_garments = json.loads(a.inherited_garments)
        elif a.continued and (d / "slots.json").is_file():
            try:
                _sl = json.loads((d / "slots.json").read_text(encoding="utf-8"))
                _ig = ((_sl.get("inherited") or {}).get("garments")) if isinstance(_sl, dict) else None
                if isinstance(_ig, dict) and _ig:
                    inh_garments = _ig
            except Exception:
                inh_garments = None
        # Max Architect, Derrick t271s933 (2026-11-15) Fix B: a chained clip keeps the scene's clip-1 read
        # (--scene-read, else the chain's still_read.start.json in the run dir).
        scene_read = None
        _scene_p = Path(a.scene_read) if getattr(a, "scene_read", None) else d / "still_read.start.json"
        if a.continued and _scene_p.is_file():
            scene_read = json.loads(_scene_p.read_text(encoding="utf-8"))
        r = submit_writer_run((d / "writer_output.txt").read_text(encoding="utf-8"), base_graph, d,
                              a.ask, a.position, still_image=(a.still or None),
                              still_read=json.loads((d / "still_read.json").read_text(encoding="utf-8")),
                              dry_run=not a.queue, character=(a.character or None), names=(a.names or None),
                              partner_type2=(a.partner_type2 or None),
                              cast_overrides=dict(_s3_overrides(a.s3_look, a.partner2_still, getattr(a, "s2_look", None)) or {}, **({"shots": a.shots} if a.shots else {}),
                                                  **({"s3_in_frame": True} if a.s3_in_frame else {}),
                                                  **({"inherited_garments": inh_garments} if isinstance(inh_garments, dict) and inh_garments else {}),
                                                  **({"scene_read": scene_read} if isinstance(scene_read, dict) else {}))
                              or None, partner_type=(a.partner_type or None), continued=bool(getattr(a, "continued", False)),
                              **({"frames": br.validate_single_clip_frames(a.frames)} if a.frames else {}),
                              **({"keep_comfy_process": True} if a.keep_comfy_process else {}))
    except Exception as e:
        print(f"NOT_READY submitted=False hook error: {type(e).__name__}: {e}")
        return 3
    print(r.get("status"), "submitted=%s" % r.get("submitted"), "gpu_busy=%s" % r.get("gpu_busy"), r.get("reason", ""))
    return 0 if r.get("status") == "READY" else 3


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv and argv[0] == "writer-run":
        return _writer_run_cli(argv[1:])
    parser = argparse.ArgumentParser(description="Submit H3 parody render job")
    parser.add_argument("--name", required=True, help="Identity / celeb name")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True, help="Biometric/wardrobe description (required, no word cap)")
    parser.add_argument("--tone", default="parody", help="Tone")
    parser.add_argument("--dialogue", help="Spoken words only")
    parser.add_argument("--scene", help="Scene (rich multi-sentence text welcome; never truncated)")
    parser.add_argument("--summary", help="Optional short summary line (default: first sentence of a long --scene)")
    parser.add_argument("--seed", type=int, default=51083601, help="Seed")
    parser.add_argument("--frames", type=int, default=None, help="Exact single-clip frames (H3 grid, max 243 on 16 GB)")
    parser.add_argument("--seconds", type=float, help="Length in seconds (single shot up to the measured ceiling of 243 frames / ~10.1s; longer asks require 2+ --beat)")
    parser.add_argument("--aspect", help="9:16 (default), 16:9, 1:1, 4:3, 3:4, portrait, landscape, widescreen, square")
    parser.add_argument("--size", help="Explicit canvas WxH (multiples of 32, 256..2048)")
    parser.add_argument("--camera", help="Camera framing/motion; motion words drop 'Camera locked off'")
    parser.add_argument("--pronoun", default="she", choices=["she", "he", "they"])
    parser.add_argument("--end-action", help="What the subject does as the line ends (replaces the stock nod)")
    parser.add_argument("--image", action="append", default=[],
                        help="approved_characters reference image (frame-0 AddGuide start image first; pass --image-at <sec> for each additional pin)")
    parser.add_argument("--image-at", action="append", type=br._parse_image_at_arg, default=[],
                        help="Clip time in seconds for each additional --image pin (at least 0.5s apart, mapped to its beat; accept -1 or 'end' for last frame)")
    parser.add_argument("--image-role", default=br.DEFAULT_IMAGE_ROLE, help="What <Picture N> anchors")
    parser.add_argument("--prequel-to", help="Existing mp4 to stitch this prequel in front of [prequel, existing]")
    parser.add_argument("--beat", action="append", default=[], help="Scene beat (repeat 2+ for one native continuation graph, not stitched cells)")
    parser.add_argument("--beat-dialogue", action="append", default=[], help="Spoken line per beat")
    parser.add_argument("--beat-camera", action="append", default=[], help="Camera per beat")
    parser.add_argument("--beat-seconds", action="append", type=float, default=[], help="Seconds per beat")
    parser.add_argument("--beat-new-shot", action="append", type=int, default=[],
                        help="1-based beat index (2+) that opens with an intentional C 'new shot' cut (new room or pose)")
    parser.add_argument("--name2", help="Second subject name")
    parser.add_argument("--character2")
    parser.add_argument("--actor2")
    parser.add_argument("--description2", help="Second subject biometric/wardrobe description")
    parser.add_argument("--dialogue2", help="Second subject spoken words only")
    parser.add_argument("--pronoun2", default="she", choices=["she", "he", "they"])
    parser.add_argument("--name3", help="Third subject name")
    parser.add_argument("--character3")
    parser.add_argument("--actor3")
    parser.add_argument("--description3", help="Third subject biometric/wardrobe description")
    parser.add_argument("--dialogue3", help="Third subject spoken words only")
    parser.add_argument("--pronoun3", default="she", choices=["she", "he", "they"])
    parser.add_argument("--partner-type2", choices=["man", "woman", "none", "non-human", "faceless", "still"],
                        help="Partner type for S3")
    parser.add_argument("--ambience", help="Soundscape ambience phrase (default: quiet room ambience, soft natural room tone)")
    parser.add_argument("--slug", help="Optional run slug")
    parser.add_argument("--run-dir", help="Direct run directory override")
    parser.add_argument("--dry-run", action="store_true", help="Validate and prepare without submitting")
    parser.add_argument("--wait", action="store_true", help="Block until the batch closes and write <run_dir>/clip.mp4")
    parser.add_argument("--qnap-put", action="store_true", help="With --wait: upload clip.mp4 to pi-drop/<run>.mp4")
    parser.add_argument("--wait-timeout", type=float, default=WAIT_TIMEOUT_SEC)
    # keep-comfy-part1 (2026-11-15): same flag as run_queue.py; only passed through when set.
    parser.add_argument("--keep-comfy-process", action="store_true",
                        help="run_queue.py keeps the comfyui_auto process loaded at batch close "
                             "(POST /free still runs); for chained runs. Default off: normal run unloads.")
    args = parser.parse_args(argv)

    res = submit_parody_job(
        name=args.name,
        character=args.character,
        actor=args.actor,
        description=args.description,
        tone=args.tone,
        dialogue=args.dialogue,
        scene=args.scene,
        seed=args.seed,
        frames=args.frames,
        slug=args.slug,
        run_dir_override=Path(args.run_dir) if args.run_dir else None,
        dry_run=args.dry_run,
        seconds=args.seconds,
        aspect=args.aspect,
        size=args.size,
        camera=args.camera,
        pronoun=args.pronoun,
        end_action=args.end_action,
        summary=args.summary,
        images=args.image,
        image_role=args.image_role,
        beats=args.beat,
        beat_dialogues=args.beat_dialogue,
        beat_cameras=args.beat_camera,
        beat_seconds=args.beat_seconds,
        name2=args.name2,
        character2=args.character2,
        actor2=args.actor2,
        description2=args.description2,
        dialogue2=args.dialogue2,
        pronoun2=args.pronoun2,
        name3=args.name3,
        character3=args.character3,
        actor3=args.actor3,
        description3=args.description3,
        dialogue3=args.dialogue3,
        pronoun3=args.pronoun3,
        partner_type2=args.partner_type2,
        ambience=args.ambience,
        wait=args.wait,
        qnap=args.qnap_put,
        wait_timeout=args.wait_timeout,
        image_times=args.image_at,
        beat_new_shots=args.beat_new_shot,
        prequel_to=args.prequel_to,
        keep_comfy_process=args.keep_comfy_process,
    )
    if args.wait and not args.dry_run:
        r = res.get("resolved") or {}
        res["resolved"] = {k: r.get(k) for k in ("mode", "index_status", "index_flag", "loaded_refmods")}
    print(json.dumps(res, indent=2))
    if res.get("gpu_busy"):
        return GPU_BUSY_RC
    if args.wait and not args.dry_run:
        ok = res.get("batch_rc") == 0 and res.get("final_mp4")
        if args.qnap_put:
            ok = ok and res.get("qnap_path")
        return 0 if ok else 1
    return 0 if res.get("dry_run") or res.get("submitted") else 1


if __name__ == "__main__":
    sys.exit(main())
