"""prechecks.py - deterministic pre-gate for p15-style i2v clips (CPU only).

Per clip:
  * PySceneDetect AdaptiveDetector + ContentDetector, stock defaults -> cut counts.
  * VBench-style consistency: DINOv2 (subject) and CLIP (background) cosine similarity of
    every sampled frame to the START IMAGE and to the previous frame. Reports min / mean / last.
Writes out/<tag>.json per clip and out/prechecks.csv. Flags only; never KEEPs.
Usage: .venv\\Scripts\\python.exe prechecks.py [--match p15v2_] [--frames 16]
"""
import argparse, csv, json, sys
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image
from scenedetect import detect, AdaptiveDetector, ContentDetector
from transformers import AutoImageProcessor, AutoModel, CLIPModel, CLIPProcessor

MANIFEST = Path(r"C:\Users\derek\5slock\ralph-community\notes\p15v2_manifest.json")
RUNS = Path(r"C:\AI\community\runs")
INPUT = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input")
OUT = Path(__file__).parent / "out"
DINO_ID, CLIP_ID = "facebook/dinov2-small", "openai/clip-vit-base-patch32"
# Thresholds tuned on the 36 p15v2 clips (see README). A clip is flagged if ANY rule fires.
#   jump:   DINO min frame-to-previous-frame similarity < 0.82  (abrupt change: start abandoned, scene/identity swap)
#   static: transition clips only (start image = OG still, one ref): DINO last-frame-to-start > 0.76
#           (the clip never left the start pose, so the target pose was not reached)
#   Cuts (AdaptiveDetector) are reported as info only: on p15v2 they fired on 3 good clips and 0 bad ones.
TH = {"dino_prev_min": 0.82, "dino_start_last_static": 0.76}

torch.set_grad_enabled(False)
dproc, dino = AutoImageProcessor.from_pretrained(DINO_ID), AutoModel.from_pretrained(DINO_ID).eval()
cproc, clip = CLIPProcessor.from_pretrained(CLIP_ID), CLIPModel.from_pretrained(CLIP_ID).eval()

def embed(imgs):
    d = dino(**dproc(images=imgs, return_tensors="pt")).last_hidden_state[:, 0]
    c = clip.get_image_features(**cproc(images=imgs, return_tensors="pt"))
    c = c if torch.is_tensor(c) else c.pooler_output
    n = lambda t: torch.nn.functional.normalize(t.float(), dim=-1)
    return n(d), n(c)

def sample_frames(mp4, k):
    cap = cv2.VideoCapture(str(mp4)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    for i in np.linspace(0, n - 1, k).round().astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok: frames.append(Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
    cap.release(); return frames, n

def stats(e, ref):
    s, p = (e @ ref).tolist(), [float(e[i] @ e[i - 1]) for i in range(1, len(e))]
    r = lambda x: round(x, 4)
    return {"start_min": r(min(s)), "start_mean": r(sum(s) / len(s)), "start_last": r(s[-1]),
            "prev_min": r(min(p)), "prev_mean": r(sum(p) / len(p)), "per_frame_start": [r(x) for x in s]}

def flags(rec):
    f = []
    if rec["dino"]["prev_min"] < TH["dino_prev_min"]: f.append("jump")
    if rec["transition"] and rec["dino"]["start_last"] > TH["dino_start_last_static"]: f.append("static_no_transition")
    return f

def run(job, k):
    tag = job["tag"]; mp4 = RUNS / tag / f"{tag}.mp4"
    start = INPUT / job["guides"][0]["image"]
    frames, n = sample_frames(mp4, k)
    imgs = [Image.open(start).convert("RGB")] + frames
    d, c = embed(imgs)
    rec = {"tag": tag, "mp4": str(mp4), "start_image": str(start), "n_frames": n, "sampled": len(frames),
           "cuts_adaptive": max(0, len(detect(str(mp4), AdaptiveDetector())) - 1),
           "cuts_content": max(0, len(detect(str(mp4), ContentDetector())) - 1),
           "dino": stats(d[1:], d[0]), "clip": stats(c[1:], c[0]), "transition": len(job["refs"]) == 1}
    rec["info"] = ["cut_detected"] if rec["cuts_adaptive"] else []
    rec["flags"] = flags(rec); return rec

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--match", default="p15v2_"); ap.add_argument("--frames", type=int, default=16)
    a = ap.parse_args(); OUT.mkdir(exist_ok=True)
    jobs = [j for j in json.loads(MANIFEST.read_text())["jobs"] if a.match in j["tag"]]
    rows = []
    for j in jobs:
        r = run(j, a.frames); (OUT / f"{r['tag']}.json").write_text(json.dumps(r, indent=1))
        rows.append({"tag": r["tag"], "cuts_adaptive": r["cuts_adaptive"], "cuts_content": r["cuts_content"],
                     **{f"{m}_{s}": r[m][s] for m in ("dino", "clip") for s in ("start_min", "start_mean", "start_last", "prev_min")},
                     "flags": ";".join(r["flags"]), "info": ";".join(r["info"])})
        print(r["tag"], rows[-1]["flags"] or "ok", flush=True)
    with open(OUT / "prechecks.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
