"""Prepare Job A run folder: copy request.api.json, tighten prompt, retarget prefix, write order file."""
from __future__ import annotations
import datetime
import json
from pathlib import Path

SRC = Path(r"C:\AI\community\runs\parody_oc_poolblonde_pose_test_20261110_035735")
RUNS = Path(r"C:\AI\community\runs")
PROMPT = Path(r"C:\AI\community\runs\_job_a_tighter_pool_prompt.txt")
SEED = 51083601

def main() -> None:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"parody_oc_poolblonde_pose_test_v2_{ts}"
    run_dir = RUNS / name
    clip_dir = run_dir / "clip"
    if run_dir.exists():
        raise SystemExit(f"run dir already exists: {run_dir}")
    clip_dir.mkdir(parents=True)
    prompt = PROMPT.read_text(encoding="utf-8").strip() + "\n"
    src_graph = (SRC / "request.api.json").read_text(encoding="utf-8")
    graph = json.loads(src_graph)
    old_prompt = graph["c0"]["inputs"]["prompt"]
    old_prefix = graph["save"]["inputs"]["filename_prefix"]
    seed = graph["noise"]["inputs"]["noise_seed"]
    if seed != SEED:
        raise SystemExit(f"unexpected seed {seed}")
    graph["c0"]["inputs"]["prompt"] = prompt
    new_prefix = f"community/{name}/clip"
    graph["save"]["inputs"]["filename_prefix"] = new_prefix
    text = json.dumps(graph, indent=2, ensure_ascii=False) + "\n"
    (run_dir / "request.api.json").write_text(text, encoding="utf-8")
    (clip_dir / "request.api.json").write_text(text, encoding="utf-8")
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    order = {
        "order": [
            {"pos": 1, "tag": "clip", "arm": "parody", "scene": "Pool Blonde", "seed": SEED}
        ]
    }
    (run_dir / "_render_order.json").write_text(
        json.dumps(order, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    src = json.loads(src_graph)
    new = json.loads((clip_dir / "request.api.json").read_text(encoding="utf-8"))
    src["c0"]["inputs"]["prompt"] = new["c0"]["inputs"]["prompt"]
    src["save"]["inputs"]["filename_prefix"] = new["save"]["inputs"]["filename_prefix"]
    if src != new:
        raise SystemExit("graph changed beyond prompt text and filename_prefix")
    if new["noise"]["inputs"]["noise_seed"] != SEED:
        raise SystemExit("seed drifted")
    print(json.dumps({
        "run_dir": str(run_dir),
        "run_name": name,
        "seed": SEED,
        "old_prefix": old_prefix,
        "new_prefix": new_prefix,
        "old_prompt_chars": len(old_prompt),
        "new_prompt_chars": len(prompt),
    }, indent=2))

if __name__ == "__main__":
    main()
