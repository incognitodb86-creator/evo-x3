"""extras.py - experimental CPU features (background ring CLIP, optical-flow motion). Writes out/extras.csv."""
import csv, json
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
MANIFEST = Path(r"C:\Users\derek\5slock\ralph-community\notes\p15v2_manifest.json")
RUNS, INPUT = Path(r"C:\AI\community\runs"), Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input")
OUT = Path(__file__).parent / "out"
torch.set_grad_enabled(False)
cp, cm = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32"), CLIPModel.from_pretrained("openai/clip-vit-base-patch32").eval()

def ring(img):  # grey out the central 60% x 70% so CLIP sees mostly background
    a = np.array(img).copy(); h, w = a.shape[:2]
    a[int(h*.15):int(h*.85), int(w*.2):int(w*.8)] = 127; return Image.fromarray(a)

def emb(imgs):
    e = cm.get_image_features(**cp(images=imgs, return_tensors="pt"))
    e = e if torch.is_tensor(e) else e.pooler_output
    return torch.nn.functional.normalize(e.float(), dim=-1)

rows = []
for job in json.loads(MANIFEST.read_text())["jobs"]:
    tag = job["tag"]; cap = cv2.VideoCapture(str(RUNS / tag / f"{tag}.mp4")); frames = []
    while True:
        ok, f = cap.read()
        if not ok: break
        frames.append(cv2.resize(f, None, fx=0.25, fy=0.25) if len(frames) % 4 == 0 else None)
    cap.release(); frames = [f for f in frames if f is not None]
    g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    mag = [float(np.linalg.norm(cv2.calcOpticalFlowFarneback(g[i-1], g[i], None, .5, 3, 15, 3, 5, 1.2, 0), axis=2).mean()) for i in range(1, len(g))]
    n = len(mag); idx = np.linspace(0, len(frames)-1, 16).round().astype(int)
    start = Image.open(INPUT / job["guides"][0]["image"]).convert("RGB").resize(Image.fromarray(frames[0]).size)
    e = emb([ring(start)] + [ring(Image.fromarray(cv2.cvtColor(frames[i], cv2.COLOR_BGR2RGB))) for i in idx])
    s = (e[1:] @ e[0]).tolist(); p = [float(e[i] @ e[i-1]) for i in range(2, len(e))]
    rows.append({"tag": tag, "bg_start_min": round(min(s), 4), "bg_start_last": round(s[-1], 4), "bg_prev_min": round(min(p), 4),
                 "flow_mean": round(np.mean(mag), 3), "flow_last_third": round(np.mean(mag[2*n//3:]), 3), "flow_p10": round(float(np.percentile(mag, 10)), 3)})
    print(rows[-1], flush=True)
with open(OUT / "extras.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
