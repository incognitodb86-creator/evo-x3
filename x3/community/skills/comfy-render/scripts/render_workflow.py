"""Single workflow render script for comfy-render skill (U9 / P6c).

Loads exported API JSON template, sets inputs per request, and calls ComfyUI
via http://127.0.0.1:8080/upstream/comfyui_auto reusing comm.py.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

# Add community scripts to path for comm and make_b2_request
SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import comm
from make_b2_request import build as build_b2_graph


DEFAULT_TEMPLATE = Path(r"C:\AI\community\templates\b2.api.json")


def prepare_request(
    template_path: Path,
    prompt: str,
    seed: int,
    prefix: str,
    frames: int = 124,
    image: str = "",
    lora: str = "",
    strength: float = 0.7,
    refmod: str = "",
) -> dict:
    """Load template and inject per-request parameters."""
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    # Use make_b2_request's proven builder
    graph = build_b2_graph(
        tpl,
        prompt=prompt,
        seed=seed,
        image=image if image else None,
        prefix=prefix,
        frames=frames,
        refmod=refmod if refmod else None,
        lora=lora if lora else None,
        strength=strength,
    )
    return graph


def submit_render(graph: dict, prefix: str, frames: int, dry_run: bool = False) -> dict:
    """Submit graph to ComfyUI via comm.py route."""
    if dry_run:
        return {"dry_run": True, "nodes": len(graph), "prefix": prefix, "frames": frames}

    # Verify adults guard
    prompt_text = ""
    for node in graph.values():
        if isinstance(node, dict) and "inputs" in node and "prompt" in node["inputs"]:
            prompt_text = str(node["inputs"]["prompt"])
            break

    if prompt_text and not comm.guard_ok(prompt_text):
        raise ValueError("Prompt failed adults-only guard check")

    # Queue through comm.py (POST /prompt via /upstream/comfyui_auto)
    res = comm.http(f"{comm.BASE}/prompt", data={"prompt": graph}, timeout=comm.SUBMIT_TIMEOUT)
    return res


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Submit single render workflow via comfy-render")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="API JSON template path")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt", help="Prompt text")
    src.add_argument("--prompt-file", help="Path to prompt text file")
    parser.add_argument("--seed", type=int, default=42, help="Noise seed")
    parser.add_argument("--image", default="", help="Input image relative path in ComfyUI/input")
    parser.add_argument("--lora", default="", help="Face LoRA filename")
    parser.add_argument("--strength", type=float, default=0.7, help="LoRA model strength")
    parser.add_argument("--refmod", default="", help="RefMod name")
    parser.add_argument("--frames", type=int, default=124, help="Total frames")
    parser.add_argument("--prefix", required=True, help="Output filename prefix")
    parser.add_argument("--dry-run", action="store_true", help="Build and validate without submitting")
    args = parser.parse_args(argv)

    if args.prompt is not None:
        prompt_str = args.prompt
    else:
        with open(args.prompt_file, "r", encoding="utf-8") as f:
            prompt_str = f.read()

    graph = prepare_request(
        template_path=Path(args.template),
        prompt=prompt_str,
        seed=args.seed,
        prefix=args.prefix,
        frames=args.frames,
        image=args.image,
        lora=args.lora,
        strength=args.strength,
        refmod=args.refmod,
    )

    result = submit_render(graph, prefix=args.prefix, frames=args.frames, dry_run=args.dry_run)
    print("comfy-render result:", json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
