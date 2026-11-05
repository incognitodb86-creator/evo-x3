"""Submit and execute H3 parody runs under GPU lock (U8).

Builds resolved request, saves run record, submits via run_graph_job / comfy-render
under C:\\AI\\locks\\gpu-render.lock, and verifies final delivery of:
- clip.mp4
- prompt.txt
- assets.json
- request.api.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
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
from run_record import RUNS_ROOT, save_run_record, verify_run_artifacts


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

    index_dir = Path(r"C:\AI\community\index\h3-known-characters")
    refmods_dir = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
    aliases_path = PARODY_DIR / "aliases.json"

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
    prefix = f"community/{run_name}/clip"

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

    # 6. Execute render via run_graph_job.py
    run_graph_py = SCRIPTS_DIR / "run_graph_job.py"
    cmd = [
        sys.executable,
        "-u",
        str(run_graph_py),
        str(run_dir),
        "clip",
        "--frames",
        str(frames),
    ]

    print(f"Submitting render job: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    if proc.returncode != 0:
        raise RuntimeError(f"run_graph_job.py failed with returncode {proc.returncode}")

    # 7. Verify all R8 artifacts present
    checks = verify_run_artifacts(run_dir, require_clip=True)
    all_ok = all(checks.values())
    print(f"Artifact verification: {checks}")

    return {
        "success": all_ok,
        "run_dir": str(run_dir),
        "checks": checks,
        "artifacts": {k: str(v) for k, v in artifacts.items()},
        "resolved": resolved,
    }


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
    return 0 if res.get("dry_run") or res.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
