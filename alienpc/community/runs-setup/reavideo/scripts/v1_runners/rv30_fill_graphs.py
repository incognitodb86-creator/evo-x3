
"""Fill landscape oc_ref (1344x768, 16:9 1-pass) graphs from the validation manifest. Does not print prompts."""
from __future__ import annotations
import copy, json, sys
from pathlib import Path

TEMPLATE = Path(r"C:\AI\community\templates\oc_ref.api.json")
MANIFEST = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\bridge\h3max_manifest.json")
STEMS = Path(sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\stems.json")
RUN = Path(sys.argv[3] if len(sys.argv) > 3 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\run")
SEED = 51083601
WIDTH, HEIGHT = 1344, 768

stems_doc = json.loads(STEMS.read_text(encoding="utf-8"))
stems = [s for s in stems_doc.get("stems") or [] if s]
# strip extension if a filename leaked in
stems = [s[:-12] if s.lower().endswith(".safetensors") else s for s in stems]
if len(stems) < 2:
    print("NOT_READY need two visual RefMod stems")
    raise SystemExit(2)

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
clips = manifest.get("clips") or []
if not clips:
    print("NOT_READY empty manifest")
    raise SystemExit(2)
graph0 = json.loads(TEMPLATE.read_text(encoding="utf-8"))

# half canvas for 2-pass lsu3 scale 2.0
def c0_canvas(graph, width, height):
    lsu = graph.get("lsu3") if isinstance(graph.get("lsu3"), dict) else None
    scale = 0.0
    if lsu and str(lsu.get("class_type") or "") in {"MinimaxH3LatentUpscaler3D", "MiniMaxH3LatentUpscaler3D"}:
        inp = lsu.get("inputs") or {}
        try:
            scale = float(inp.get("mode.scale") or inp.get("scale") or 0)
        except (TypeError, ValueError):
            scale = 0.0
    if scale == 2.0:
        t_w = (graph.get("c0") or {}).get("inputs", {}).get("width")
        t_h = (graph.get("c0") or {}).get("inputs", {}).get("height")
        if t_w == width and t_h == height:
            return int(width), int(height)
        return int(width) // 2, int(height) // 2
    return int(width), int(height)

RUN.mkdir(parents=True, exist_ok=True)
order = []
for clip in clips:
    idx = int(clip["clip_index"])
    tag = f"pack{idx:02d}"
    prompt = (clip.get("prompt") or "").strip()
    if not prompt:
        print(f"NOT_READY empty prompt for {tag}")
        raise SystemExit(2)
    if "<d>" not in prompt:
        print(f"NOT_READY {tag} prompt has no <d> dialogue tag")
        raise SystemExit(2)
    frames = int(clip["frames"])
    g = copy.deepcopy(graph0)
    c0 = g["c0"]["inputs"]
    cw, ch = c0_canvas(g, WIDTH, HEIGHT)
    c0["prompt"] = prompt
    c0["width"] = cw
    c0["height"] = ch
    c0["length"] = frames
    # drop empty start-image link so LoadImage is not required
    if "ref_images.ref_image_1" in c0:
        del c0["ref_images.ref_image_1"]
    if "img_1" in g:
        del g["img_1"]
    if "refmods" in g:
        for i in range(1, 9):
            g["refmods"]["inputs"][f"mod_{i}"] = stems[i - 1] if i <= len(stems) else "(none)"
    if "noise" in g:
        g["noise"]["inputs"]["noise_seed"] = int(SEED)
    if "save" in g:
        g["save"]["inputs"]["filename_prefix"] = f"community/{RUN.name}/{tag}"
    tag_dir = RUN / tag
    tag_dir.mkdir(parents=True, exist_ok=True)
    (tag_dir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    (tag_dir / "request.api.json").write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    order.append({"pos": idx, "tag": tag, "arm": "oc_ref", "scene": "val30s", "seed": SEED})

(RUN / "_render_order.json").write_text(json.dumps({"order": order}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "status": "READY",
    "run_dir": str(RUN),
    "template": str(TEMPLATE),
    "clips": len(order),
    "tags": [j["tag"] for j in order],
    "frames": [int(c["frames"]) for c in clips],
    "c0_canvas": list(c0_canvas(graph0, WIDTH, HEIGHT)),
    "final_canvas": [WIDTH, HEIGHT],
    "refmod_slots": len(stems),
    "img_1_removed": True,
}, indent=2))
