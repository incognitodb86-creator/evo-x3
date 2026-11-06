"""Submit and execute H3 parody runs under GPU lock (U8).

Builds resolved request, saves run record, writes a one-clip run_queue manifest, and
submits through run_queue.py --detach. run_queue owns gpu-render.lock; rc 7 means GPU busy.
The detached batch later writes clip output and its result to _render_queue.log.
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

# Add community scripts to path
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PARODY_DIR = SCRIPTS_DIR / "parody"
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

from build_request import DEFAULT_REFMOD_TEMPLATE, build_parody_request
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities
from run_record import RUNS_ROOT, save_run_record

INDEX_DIR = Path(r"C:\AI\community\index\h3-known-characters")
REFMODS_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
ALIASES_PATH = PARODY_DIR / "aliases.json"
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
    template_path: Path = DEFAULT_REFMOD_TEMPLATE,
) -> Dict[str, Any]:
    """Execute full parody pipeline from request to verified artifacts."""
    if not description or not str(description).strip():
        raise ValueError("Biometric description (--description) is required for submit.")

    index_dir = INDEX_DIR
    refmods_dir = REFMODS_DIR
    aliases_path = ALIASES_PATH

    # 1. Resolve identity
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
        index_dir=index_dir,
        refmods_dir=refmods_dir,
        aliases_path=aliases_path,
    )

    # KTD3 / R8: fail closed before any run artifact when a non-good identity has no local RefMod.
    if resolved.get("index_status") != "good" and not resolved.get("loaded_refmods"):
        who = character or actor or name
        raise ValueError(
            f"No local RefMod installed for '{who}' ({resolved.get('index_flag')}) in {refmods_dir}; "
            "refusing to queue a render without identity assets (install a RefMod or use an INDEX good identity)."
        )

    # 2. Plan C2V continuation if needed
    chain_plan = plan_c2v_chain(total_length_s=frames / 24, clip_frames=frames)

    # 3. Determine run folder and prefix
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

    # 4. Build request graph and prompt
    graph, prompt = build_parody_request(
        resolved=resolved,
        seed=seed,
        prefix=prefix,
        frames=frames,
        dialogue=dialogue,
        scene=scene,
        template_path=template_path,
    )

    # 5. Save initial run record (request.api.json, prompt.txt, assets.json)
    artifacts = save_run_record(
        run_dir=run_dir,
        resolved=resolved,
        prompt=prompt,
        graph=graph,
        chain_plan=chain_plan,
        clip_source=None,
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
        }]
    }
    order_file = run_dir / "_render_order.json"
    order_file.write_text(json.dumps(order, indent=2, ensure_ascii=False), encoding="utf-8")

    if dry_run:
        print(f"[DRY-RUN] Parody request prepared at {run_dir}")
        print(f"  Mode:         {resolved.get('mode')}")
        print(f"  INDEX status: {resolved.get('index_status')}")
        print(f"  RefMods:      {resolved.get('loaded_refmods')}")
        print(f"  Frames:       {frames}")
        return {
            "dry_run": True,
            "run_dir": str(run_dir),
            "artifacts": {k: str(v) for k, v in artifacts.items()},
            "resolved": resolved,
        }

    # 6. Submit through the shared queue route. Detach returns after the batch PID is created.
    python = str(QUEUE_PYTHON) if QUEUE_PYTHON.is_file() else sys.executable
    cmd = [
        python,
        "-u",
        str(RUN_QUEUE_PY),
        "--run-dir",
        str(run_dir),
        "--frames",
        str(frames),
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
    }
    if proc.returncode == GPU_BUSY_RC:
        return dict(base, submitted=False, detached=False, gpu_busy=True)
    if proc.returncode != 0:
        raise RuntimeError(f"run_queue.py --detach failed with returncode {proc.returncode}")

    return dict(base, submitted=True, detached=True, gpu_busy=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Submit H3 parody render job")
    parser.add_argument("--name", required=True, help="Identity / celeb name")
    parser.add_argument("--character", help="Character name")
    parser.add_argument("--actor", help="Actor name")
    parser.add_argument("--description", "--bio", dest="description", required=True, help="Biometric/wardrobe description (required)")
    parser.add_argument("--tone", default="parody", help="Tone")
    parser.add_argument("--dialogue", help="Dialogue line")
    parser.add_argument("--scene", help="Scene summary")
    parser.add_argument("--seed", type=int, default=51083601, help="Seed")
    parser.add_argument("--frames", type=int, default=124, help="Frames")
    parser.add_argument("--slug", help="Optional run slug")
    parser.add_argument("--run-dir", help="Direct run directory override")
    parser.add_argument("--dry-run", action="store_true", help="Validate and prepare without submitting")
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
    )
    print(json.dumps(res, indent=2))
    if res.get("gpu_busy"):
        return GPU_BUSY_RC
    return 0 if res.get("dry_run") or res.get("submitted") else 1


if __name__ == "__main__":
    sys.exit(main())
