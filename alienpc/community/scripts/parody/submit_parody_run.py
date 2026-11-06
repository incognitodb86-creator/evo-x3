"""Submit and execute H3 parody runs under GPU lock (U8).

Builds resolved request, saves run record, writes a one-clip run_queue manifest, and
submits through run_queue.py --detach. run_queue owns gpu-render.lock; rc 7 means GPU busy.
Supports --graph-mode, --cond-source, --refmod-only for U5 A/B/B-2pass/D arms.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, Optional

SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PARODY_DIR = SCRIPTS_DIR / "parody"
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

from build_request import DEFAULT_REFMOD_TEMPLATE, build_parody_request
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities
from reflora import DEFAULT_REFLORA_DIR
from run_record import RUNS_ROOT, save_run_record

INDEX_DIR = Path(r"C:\AI\community\index\h3-known-characters")
REFMODS_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
ALIASES_PATH = PARODY_DIR / "aliases.json"
REFLORA_DIR = DEFAULT_REFLORA_DIR
RUN_QUEUE_PY = SCRIPTS_DIR / "run_queue.py"
QUEUE_PYTHON = Path(r"C:\AI\director\.venv\Scripts\python.exe")
QUEUE_TAG = "clip"
GPU_BUSY_RC = 7


def queue_outcome(run_dir: Path) -> Optional[Dict[str, Any]]:
    """Read the newest BATCH closed rc from a detached run_queue log."""
    log = Path(run_dir) / "_render_queue.log"
    if not log.is_file():
        return None
    matches = re.findall(r" BATCH closed rc=(\d+)\b", log.read_text(encoding="utf-8"))
    if not matches:
        return None
    rc = int(matches[-1])
    return {"rc": rc, "gpu_busy": rc == GPU_BUSY_RC}


def submit_parody_job(
    name: str,
    character: Optional[str] = None,
    actor: Optional[str] = None,
    description: Optional[str] = None,
    tone: str = "parody",
    dialogue: Optional[str] = None,
    scene: Optional[str] = None,
    seed: int = 51083601,
    frames: int = 124,
    slug: Optional[str] = None,
    run_dir_override: Optional[Path] = None,
    dry_run: bool = False,
    template_path: Optional[Path] = None,
    image: Optional[str] = None,
    cond_source: Optional[str] = None,
    graph_mode: str = "single-pass",
    stage_cond: bool = False,
    refmod_only: bool = False,
    require_cond: bool = True,
    wait: bool = False,
    size: str = "768x1344",
    objinfo_dump: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute full parody pipeline from request to verified artifacts."""
    if not description or not str(description).strip():
        raise ValueError("Biometric description (--description) is required for submit.")

    req_dict = {
        "names": [name] if name else [],
        "character": character,
        "actor": actor,
        "tone": tone,
        "length_s": int(round(frames / 24)),
        "description": str(description).strip(),
    }
    resolved = resolve_identities(
        req_dict,
        index_dir=INDEX_DIR,
        refmods_dir=REFMODS_DIR,
        aliases_path=ALIASES_PATH,
        reflora_dir=None if refmod_only else REFLORA_DIR,
    )

    chain_plan = plan_c2v_chain(total_length_s=frames / 24, clip_frames=frames)

    if run_dir_override:
        run_dir = Path(run_dir_override)
        run_name = run_dir.name
    else:
        ident_slug = slug or (character or actor or name).lower().replace(" ", "_")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"parody_{ident_slug}_{ts}"
        run_dir = RUNS_ROOT / run_name

    run_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"community/{run_name}/{QUEUE_TAG}"

    graph, prompt, cond_meta = build_parody_request(
        resolved=resolved,
        seed=seed,
        prefix=prefix,
        frames=frames,
        dialogue=dialogue,
        scene=scene,
        template_path=template_path,
        image=image,
        cond_source=cond_source,
        graph_mode=graph_mode,
        stage_cond=stage_cond,
        require_cond=require_cond,
        objinfo_dump=objinfo_dump,
    )
    resolved["cond"] = cond_meta

    artifacts = save_run_record(
        run_dir=run_dir,
        resolved=resolved,
        prompt=prompt,
        graph=graph,
        chain_plan=chain_plan,
        clip_source=None,
        cond_meta=cond_meta,
    )

    queue_job_dir = run_dir / QUEUE_TAG
    queue_job_dir.mkdir(parents=True, exist_ok=True)
    (queue_job_dir / "request.api.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    order = {
        "order": [{
            "pos": 1,
            "tag": QUEUE_TAG,
            "arm": "parody",
            "scene": character or actor or name,
            "seed": seed,
            "graph_mode": graph_mode,
            "refmod_only": refmod_only,
        }]
    }
    order_file = run_dir / "_render_order.json"
    order_file.write_text(json.dumps(order, indent=2, ensure_ascii=False), encoding="utf-8")

    if dry_run:
        print(f"[DRY-RUN] Parody request prepared at {run_dir}")
        print(f"  Mode:         {resolved.get('mode')}")
        print(f"  INDEX status: {resolved.get('index_status')}")
        print(f"  RefMods:      {resolved.get('loaded_refmods')}")
        print(f"  Layers:       {resolved.get('identity_layers')}")
        print(f"  RefLoRA:      {[h['lora_name'] for h in (resolved.get('reflora') or {}).get('hybrids', [])]}")
        print(f"  graph_mode:   {graph_mode}")
        print(f"  refmod_only:  {refmod_only}")
        print(f"  Cond:         {cond_meta}")
        print(f"  Frames:       {frames}")
        return {
            "dry_run": True,
            "run_dir": str(run_dir),
            "artifacts": {k: str(v) for k, v in artifacts.items()},
            "resolved": resolved,
            "cond": cond_meta,
            "graph_mode": graph_mode,
            "refmod_only": refmod_only,
        }

    python = str(QUEUE_PYTHON) if QUEUE_PYTHON.is_file() else sys.executable
    cmd = [
        python, "-u", str(RUN_QUEUE_PY),
        "--run-dir", str(run_dir),
        "--frames", str(frames),
        "--size", str(size or "768x1344"),
    ]
    if not wait:
        cmd.append("--detach")

    print(f"Submitting render queue: {' '.join(cmd)}")
    # Detach returns after WMI spawn (~seconds). --wait runs the full batch in-foreground
    # (can be 10-40+ min per clip on beta7); no timeout so Forge can sequence arms A->D.
    timeout = None if wait else 180
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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
        "cond": cond_meta,
        "graph_mode": graph_mode,
        "refmod_only": refmod_only,
    }
    if proc.returncode == GPU_BUSY_RC:
        return dict(base, submitted=False, detached=False, gpu_busy=True)
    if proc.returncode != 0:
        raise RuntimeError(f"run_queue.py --detach failed with returncode {proc.returncode}")

    return dict(base, submitted=True, detached=(not wait), waited=bool(wait), gpu_busy=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Submit H3 parody render job")
    parser.add_argument("--name", required=True, help="Identity / celeb name")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True,
                        help="Biometric/wardrobe description (required)")
    parser.add_argument("--tone", default="parody", help="Tone")
    parser.add_argument("--dialogue", help="Dialogue line")
    parser.add_argument("--scene", help="Scene summary")
    parser.add_argument("--seed", type=int, default=51083601, help="Seed")
    parser.add_argument("--frames", type=int, default=124, help="Frames")
    parser.add_argument("--slug", help="Optional run slug")
    parser.add_argument("--run-dir", help="Direct run directory override")
    parser.add_argument("--dry-run", action="store_true", help="Validate and prepare without submitting")
    parser.add_argument("--image", help="ComfyUI/input-relative Cond name (e.g. hoot_start.jpg)")
    parser.add_argument("--cond-source",
                        help="Path inside approved_characters for Cond provenance (FG-2)")
    parser.add_argument("--stage-cond", action="store_true",
                        help="Copy validated Cond into ComfyUI/input and verify SHA256")
    parser.add_argument("--graph-mode", choices=("single-pass", "two-pass"), default="single-pass",
                        help="single-pass=b2_refmod; two-pass=KEEP b2.api.json Lokken refine")
    parser.add_argument("--refmod-only", "--disable-reflora", dest="refmod_only", action="store_true",
                        help="Skip RefLoRA lookup (Arm A even when hybrid is on disk)")
    parser.add_argument("--wait", action="store_true",
                        help="Run run_queue in foreground (no --detach) until BATCH closed; sequence arms cleanly")
    parser.add_argument("--size", default="768x1344",
                        help="Objective size for run_queue (default 768x1344; two-pass upscales to this)")
    parser.add_argument("--template", default=None, help="Optional template path override")
    parser.add_argument("--objinfo-dump", default=None,
                        help="object_info capture for the offline class check "
                             "(default notes/objinfo/object_info_20261105.json)")
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
        template_path=Path(args.template) if args.template else None,
        image=args.image,
        cond_source=args.cond_source,
        graph_mode=args.graph_mode,
        stage_cond=args.stage_cond,
        refmod_only=args.refmod_only,
        wait=args.wait,
        size=args.size,
        objinfo_dump=Path(args.objinfo_dump) if args.objinfo_dump else None,
    )
    print(json.dumps(res, indent=2, default=str))
    if res.get("gpu_busy"):
        return GPU_BUSY_RC
    return 0 if res.get("dry_run") or res.get("submitted") else 1


if __name__ == "__main__":
    sys.exit(main())
