"""patch_novelty.py - audit2 CPU experiment: DINOv2 patch-level novelty vs the START IMAGE.
For each sampled frame, every DINOv2 patch token is matched to its most similar start-image patch; novelty = 1 - that
cosine. Reports per clip the max over frames of (a) mean novelty of all patches, (b) border patches only (background
proxy), (c) the 95th-percentile patch (localized blobs/new objects). Flags only. Writes out/audit2/patch_novelty.csv.
"""
import csv, json
from pathlib import Path
import numpy as np, torch
from PIL import Image
import prechecks as pc
OUT = Path(__file__).parent / "out" / "audit2"; OUT.mkdir(parents=True, exist_ok=True)
def tokens(imgs):
    t = pc.dino(**pc.dproc(images=imgs, return_tensors="pt")).last_hidden_state[:, 1:]
    return torch.nn.functional.normalize(t.float(), dim=-1)
rows = []
for j in json.loads(pc.MANIFEST.read_text())["jobs"]:
    if "p15v2_" not in j["tag"]: continue
    frames, _ = pc.sample_frames(pc.RUNS / j["tag"] / f"{j['tag']}.mp4", 16)
    tk = tokens([Image.open(pc.INPUT / j["guides"][0]["image"]).convert("RGB")] + frames)
    g = int(round(tk.shape[1] ** 0.5)); m = torch.zeros(g, g, dtype=torch.bool); m[:2] = m[-2:] = True; m[:, :2] = m[:, -2:] = True; m = m.flatten()
    nov = 1 - (tk[1:] @ tk[0].T).max(-1).values  # frames x patches
    rows.append({"tag": j["tag"], "nov_mean_max": round(float(nov.mean(1).max()), 4),
                 "nov_border_max": round(float(nov[:, m].mean(1).max()), 4),
                 "nov_p95_max": round(float(torch.quantile(nov, 0.95, dim=1).max()), 4)})
    print(rows[-1], flush=True)
with open(OUT / "patch_novelty.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
