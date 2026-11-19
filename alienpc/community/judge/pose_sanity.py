"""pose_sanity.py - audit2 CPU experiment: MediaPipe PoseLandmarker (full, up to 2 poses) on 16 sampled frames.
Anatomy proxy after HuM-Eval (keypoint confidence as structural validity, arXiv 2604.25361) and HumanScore
(bone-length stability, arXiv 2604.20157). Per clip: start-image pose count, min/mean per-frame landmark visibility,
frames with fewer poses than the start image, and max relative change of shoulder-hip (torso) length. Flags only.
Writes out/audit2/pose_sanity.csv.
"""
import csv, json
from pathlib import Path
import numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import prechecks as pc
OUT = Path(__file__).parent / "out" / "audit2"; OUT.mkdir(parents=True, exist_ok=True)
det = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(Path(__file__).parent / "models" / "pose_landmarker_full.task")),
    num_poses=2, min_pose_detection_confidence=0.3))
def run(img):
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(img.convert("RGB"))))
    vis = [float(np.mean([l.visibility for l in p])) for p in r.pose_landmarks]
    torso = [float(np.hypot((p[11].x + p[12].x - p[23].x - p[24].x) / 2, (p[11].y + p[12].y - p[23].y - p[24].y) / 2)) for p in r.pose_landmarks]
    return len(vis), (np.mean(vis) if vis else 0.0), (max(torso) if torso else 0.0)
rows = []
for j in json.loads(pc.MANIFEST.read_text())["jobs"]:
    if "p15v2_" not in j["tag"]: continue
    frames, _ = pc.sample_frames(pc.RUNS / j["tag"] / f"{j['tag']}.mp4", 16)
    n0, v0, t0 = run(pc.Image.open(pc.INPUT / j["guides"][0]["image"]))
    res = [run(f) for f in frames]; n = [r[0] for r in res]; v = [r[1] for r in res]; t = [r[2] for r in res if r[2] > 0]
    rows.append({"tag": j["tag"], "poses_start": n0, "poses_min": min(n), "frames_fewer_poses": sum(x < max(n0, 1) for x in n),
                 "vis_min": round(min(v), 4), "vis_mean": round(float(np.mean(v)), 4),
                 "torso_change": round((max(t) - min(t)) / max(t), 4) if t else 1.0})
    print(rows[-1], flush=True)
with open(OUT / "pose_sanity.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
