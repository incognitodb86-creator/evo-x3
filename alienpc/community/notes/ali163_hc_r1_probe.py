r"""ALI-163 R1 research probe (read-only, CPU, no GPU calls, no render).

Prints the facts R1 cites about clip length and reference/face-lock settings:
  - the graph shape of the two HC clips (481 frames) and the two ALI-147 ref-sheet arms
  - per-node length / ref_image_size / ref_images / width / height / seed
  - prompt section sizes (word counts) for the HC1 prompts
  - the p7 budget file (budget left for the R-clips)
  - grid math for the candidate lengths (17k+5)
Writes nothing.
"""
import hashlib
import json
import os

RUNS = r"C:\AI\community\runs"
GRAPHS = [
    "ali147_pool_hc_c1_s51100001",
    "ali147_pool_hc_c2_s51100002",
    "ali147_pool_promptv2_s51080000",
    "ali147_pool_refsheet_s51080000",
    "ali147_pool_refsheet_b_s51080000",
]
KEYS = ("length", "width", "height", "fps", "ref_image_size", "ref_images", "image",
        "noise_seed", "seed", "steps", "sampler_name", "scheduler", "extension_frames",
        "overlap_frames", "window_length", "unet_name", "filename_prefix", "shift_video",
        "shift_audio", "frames")


def brief(node):
    out = {}
    for k, v in node.get("inputs", {}).items():
        if k in KEYS:
            out[k] = v if not isinstance(v, dict) else json.dumps(v, sort_keys=True)
    return out


def prompt_sections(text):
    parts = {}
    for chunk in text.split("\n\n"):
        head = chunk.split(":", 1)[0].strip().split("\n")[0]
        parts[head] = len(chunk.split())
    return parts


def main():
    for arm in GRAPHS:
        path = os.path.join(RUNS, arm, "request.api.json")
        print("=" * 70)
        print("ARM", arm, "exists", os.path.exists(path))
        if not os.path.exists(path):
            continue
        raw = open(path, "rb").read()
        print("bytes", len(raw), "sha256", hashlib.sha256(raw).hexdigest())
        graph = json.loads(raw.decode("utf-8-sig"))
        print("nodes", len(graph))
        for nid in sorted(graph):
            node = graph[nid]
            info = brief(node)
            print(" ", nid, node["class_type"], json.dumps(info, sort_keys=True, ensure_ascii=False)[:400])
        for nid in sorted(graph):
            p = graph[nid].get("inputs", {}).get("prompt")
            if isinstance(p, str):
                print("  prompt", nid, "chars", len(p), "words", len(p.split()),
                      "sections", json.dumps(prompt_sections(p), ensure_ascii=False))

    print("=" * 70)
    budget = r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json"
    print("BUDGET", budget, json.dumps(json.load(open(budget, encoding="utf-8-sig")), sort_keys=True))

    print("=" * 70)
    print("GRID (frames-5)%17==0 and seconds at 24 fps")
    for frames in (107, 124, 141, 158, 175, 192, 209, 226, 243, 260, 277, 294, 311, 328, 345, 362, 481):
        print("  ", frames, "on_grid", (frames - 5) % 17 == 0, "sec", round(frames / 24.0, 3))
    print("  extension rules: overlap 17k+5 (22), extension multiple of 17 (119), window 22+119=141")
    print("  candidate split: 124 base + 119 appended (22 hidden overlap, 141 window) = 243 total")
    print("  current clip shape: 243 base + 238 appended (22 overlap, 260 window) = 481 total")


if __name__ == "__main__":
    main()
