"""ALI-163 HC1 read-only pick scan: PIL size, aspect, sha256, manifest source name."""
import csv, hashlib, json, os
from PIL import Image

ROOT = r"C:\Users\derek\5slock\approved_characters"
CAND = {
    "FLOW_BLONDE_DARK_PAIRS_2026-10-19": ["BD002", "BD004", "BD006", "BD007", "BD013", "BD076"],
    "GROK_IMAGINE_2026-10-19": ["GI046", "GI063", "GI072", "GI076", "GI097"],
    "GROK_IMAGINE_2026-10-19b": ["GI102", "GI107", "GI113", "GI114", "GI150", "GI171", "GI173"],
}

for folder, names in CAND.items():
    mpath = os.path.join(ROOT, folder, "MANIFEST.csv")
    rows = {}
    with open(mpath, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows[os.path.splitext(row["new_name"])[0]] = row
    for nm in names:
        p = os.path.join(ROOT, folder, nm + ".jpg")
        if not os.path.exists(p):
            print(nm, "MISSING")
            continue
        with Image.open(p) as im:
            w, h, mode, fmt = im.size[0], im.size[1], im.mode, im.format
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        row = rows.get(nm, {})
        src = os.path.basename(row.get("source_path", ""))
        print(json.dumps({
            "id": nm, "folder": folder, "path": p.replace("\\", "/"),
            "wh": f"{w}x{h}", "aspect": round(w / h, 4), "ok170_185": 1.70 <= round(w / h, 4) <= 1.85,
            "mode": mode, "fmt": fmt, "sha256": sha,
            "manifest_sha_match": sha == row.get("sha256", ""),
            "source_name": os.path.splitext(src)[0],
        }))
