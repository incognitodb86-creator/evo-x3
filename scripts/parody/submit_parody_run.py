"""Submit and execute H3 parody runs under GPU lock (U8 + dynamic U1-U4, 2026-11-06).

Builds resolved request, saves run record, writes a run_queue manifest, and submits through
run_queue.py --detach. run_queue owns gpu-render.lock; rc 7 means GPU busy.

Dynamic options (all optional; omitted = the locked 124f 768x1344 single clip as before):
  --seconds / --frames   single shot up to SINGLE_CLIP_MAX_FRAMES (H3 grid snap); longer asks or several
                         --beat args build shared-anchor cells c01_s<seed>, c02_s<seed+1>, ... rendered in one
                         GPU window and stitched (take_chain_stitch.py) into one clip.mp4
  --aspect / --size      canvas (9:16 default, 16:9, 1:1, 4:3, 3:4)
  --camera / --pronoun / --end-action / --summary
  --image (1..4)         approved_characters reference images only (never sydney paths)
  --name2 ... --dialogue2  optional second subject (S2)
  --wait [--qnap-put]    block until BATCH closed, copy/stitch clip.mp4, upload pi-drop/<run>.mp4, and print
                         final_mp4 + qnap_path in the JSON - one call, no PowerShell polling loop
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Sequence

# Add community scripts to path
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PARODY_DIR = SCRIPTS_DIR / "parody"
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import build_request as br
from build_request import DEFAULT_REFMOD_TEMPLATE, build_parody_request
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities, validate_reference_images
from run_record import RUNS_ROOT, save_run_record

INDEX_DIR = Path(r"C:\AI\community\index\h3-known-characters")
REFMODS_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
ALIASES_PATH = PARODY_DIR / "aliases.json"
RUN_QUEUE_PY = SCRIPTS_DIR / "run_queue.py"
STITCH_PY = SCRIPTS_DIR / "queue" / "take_chain_stitch.py"
PI_QNAP_PY = SCRIPTS_DIR / "pi_qnap.py"
COMFY_OUT_COMMUNITY = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community")
QUEUE_PYTHON = Path(r"C:\AI\director\.venv\Scripts\python.exe")
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
    """<run_dir>/<tag>/<tag>.mp4 (run_queue copy) else the newest ComfyUI output for that tag."""
    local = Path(run_dir) / tag / f"{tag}.mp4"
    if local.is_file():
        return local
    out = COMFY_OUT_COMMUNITY / Path(run_dir).name
    return _newest(list(out.glob(f"{tag}_*.mp4")) + list((out / tag).glob(f"{tag}_*.mp4")))


def objective_lines(run_dir: Path) -> List[str]:
    log = Path(run_dir) / "status.log"
    if not log.is_file():
        return []
    return [ln.strip() for ln in log.read_text(encoding="utf-8", errors="replace").splitlines() if "OBJECTIVE" in ln]


def finalize_clip(run_dir: Path, tags: Sequence[str], python: str) -> Dict[str, Any]:
    """After BATCH closed rc=0: single clip -> copy to clip.mp4; cells -> ensure each cell mp4, stitch, copy."""
    run_dir = Path(run_dir)
    final = run_dir / "clip.mp4"
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
    wait: bool = False,
    qnap: bool = False,
    wait_timeout: float = WAIT_TIMEOUT_SEC,
    image_pools: Optional[Sequence[Path]] = None,
    image_input_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute full parody pipeline from request to verified artifacts."""
    if not description or not str(description).strip():
        raise ValueError("Biometric description (--description) is required for submit.")

    # 0. Length + canvas (validated before anything touches disk)
    max_frames = br.SINGLE_CLIP_MAX_FRAMES
    if frames is not None:
        frames = br.validate_single_clip_frames(frames)
    width, height = br.resolve_canvas(aspect, size)
    cells = None if frames is not None and not (beats and len([b for b in beats if b]) > 1) else plan_cells(
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
    valid_images = validate_reference_images(list(images or []), pools=tuple(image_pools) if image_pools else None) \
        if images else []

    # 2. Plan C2V continuation (single clip never chains; cells are stitched instead)
    chain_plan = plan_c2v_chain(total_length_s=(cells[0]["frames"] if cells else frames) / 24,
                                clip_frames=(cells[0]["frames"] if cells else frames))

    # 3. Determine run folder
    if run_dir_override:
        run_dir = Path(run_dir_override)
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
                  resolved2=resolved2, pronoun2=pronoun2)
    jobs: List[Dict[str, Any]] = []
    if cells is None:
        graph, prompt = build_parody_request(
            seed=seed, prefix=f"community/{run_name}/{QUEUE_TAG}", frames=frames, dialogue=dialogue,
            scene=scene, camera=camera, summary_text=summary, dialogue2=dialogue2, **common)
        jobs.append({"tag": QUEUE_TAG, "graph": graph, "prompt": prompt, "seed": seed, "frames": frames})
    else:
        for i, c in enumerate(cells):
            tag = f"c{i + 1:02d}_s{int(seed) + i}"
            g, p = build_parody_request(
                seed=int(seed) + i, prefix=f"community/{run_name}/{tag}", frames=c["frames"],
                dialogue=c["dialogue"], scene=c["scene"], camera=c["camera"],
                summary_text=summary if i == 0 else None, dialogue2=dialogue2 if i == 0 else None, **common)
            jobs.append({"tag": tag, "graph": g, "prompt": p, "seed": int(seed) + i, "frames": c["frames"]})

    run_dir.mkdir(parents=True, exist_ok=True)
    if len(jobs) == 1:
        prompt_all = jobs[0]["prompt"]
    else:
        prompt_all = "\n\n".join(f"=== {j['tag']} ({j['frames']}f) ===\n{j['prompt']}" for j in jobs)
    record_plan = chain_plan if len(jobs) == 1 else {
        "is_chained": False, "mode": "shared_anchor_cells", "clip_count": len(jobs),
        "cells": [{"tag": j["tag"], "frames": j["frames"], "seed": j["seed"]} for j in jobs],
        "total_frames": total_frames,
    }

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
    res.update(finalize_clip(run_dir, [j["tag"] for j in jobs], python))
    if qnap:
        res.update(qnap_put(Path(res["final_mp4"]), run_name, python))
    return res


def main(argv=None) -> int:
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
    parser.add_argument("--seconds", type=float, help="Length in seconds (single shot up to the measured ceiling, else stitched cells)")
    parser.add_argument("--aspect", help="9:16 (default), 16:9, 1:1, 4:3, 3:4, portrait, landscape, widescreen, square")
    parser.add_argument("--size", help="Explicit canvas WxH (multiples of 32, 256..2048)")
    parser.add_argument("--camera", help="Camera framing/motion; motion words drop 'Camera locked off'")
    parser.add_argument("--pronoun", default="she", choices=["she", "he", "they"])
    parser.add_argument("--end-action", help="What the subject does as the line ends (replaces the stock nod)")
    parser.add_argument("--image", action="append", default=[], help="approved_characters reference image (repeat 1..4)")
    parser.add_argument("--image-role", default=br.DEFAULT_IMAGE_ROLE, help="What <Picture N> anchors")
    parser.add_argument("--beat", action="append", default=[], help="Scene beat per cell (repeat for multi-cut)")
    parser.add_argument("--beat-dialogue", action="append", default=[], help="Spoken line per beat")
    parser.add_argument("--beat-camera", action="append", default=[], help="Camera per beat")
    parser.add_argument("--beat-seconds", action="append", type=float, default=[], help="Seconds per beat")
    parser.add_argument("--name2", help="Second subject name")
    parser.add_argument("--character2")
    parser.add_argument("--actor2")
    parser.add_argument("--description2", help="Second subject biometric/wardrobe description")
    parser.add_argument("--dialogue2", help="Second subject spoken words only")
    parser.add_argument("--pronoun2", default="she", choices=["she", "he", "they"])
    parser.add_argument("--slug", help="Optional run slug")
    parser.add_argument("--run-dir", help="Direct run directory override")
    parser.add_argument("--dry-run", action="store_true", help="Validate and prepare without submitting")
    parser.add_argument("--wait", action="store_true", help="Block until the batch closes and write <run_dir>/clip.mp4")
    parser.add_argument("--qnap-put", action="store_true", help="With --wait: upload clip.mp4 to pi-drop/<run>.mp4")
    parser.add_argument("--wait-timeout", type=float, default=WAIT_TIMEOUT_SEC)
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
        wait=args.wait,
        qnap=args.qnap_put,
        wait_timeout=args.wait_timeout,
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
