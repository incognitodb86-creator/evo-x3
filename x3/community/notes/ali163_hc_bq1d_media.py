"""BQ1d frame media (CPU ffmpeg only, NO GPU, NO ComfyUI port call, NO vision judge).

Extracts the 5 shared stamps per clip for notes/body_quality_r3b_vs_r3r_contact.png at the
SAME timestamps used by every ALI-163 sheet (0.50 / 2.60 / 5.00 / 7.40 / 9.60 s of the
10.125 s clips) into notes/bq1d_frames/<id>_f<i>.png, copies the 3 reference images (the
approved start still + the 2 face crops) into the same folder, and prints an objective
frame table: PIL size, mean brightness (a black/blank frame must FAIL the gate), bytes,
sha256, plus the non-vacuity probes (same t across clips MUST differ = two renders;
early vs late in one clip MUST differ = motion). Exit 1 on any gate fail.
"""
import hashlib
import os
import subprocess

from PIL import Image, ImageStat

BIN = ("C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/"
       "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin")
FFMPEG = BIN + "/ffmpeg.exe"
RUNS = "C:/AI/community/runs"
FR = "C:/AI/community/notes/bq1d_frames"
TS = [0.50, 2.60, 5.00, 7.40, 9.60]
IDS = ["ali147_pool_hc_r3r_s51130003", "ali147_pool_hc_r3b_s51130003"]
REFS = [("REF_still_HC3_lesbian_beach.png",
         "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc/HC3_lesbian_beach.jpg"),
        ("REF_w1_face.png",
         "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc/HC3_w1_face.png"),
        ("REF_w2_face.png",
         "C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/hc/HC3_w2_face.png")]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


os.makedirs(FR, exist_ok=True)
rows = []
for cid in IDS:
    mp4 = os.path.join(RUNS, cid, cid + ".mp4")
    for i, t in enumerate(TS):
        out = os.path.join(FR, f"{cid}_f{i}.png")
        r = subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", mp4,
                            "-frames:v", "1", out], capture_output=True, text=True)
        if r.returncode != 0:
            print("FFMPEG FAIL", cid, t, r.stderr[:200])
            raise SystemExit(1)
        with Image.open(out) as im:
            im = im.convert("L")
            mean = ImageStat.Stat(im).mean[0]
        rows.append({"id": cid, "i": i, "t": t, "file": out, "size": Image.open(out).size,
                     "bytes": os.path.getsize(out), "sha": sha(out), "mean": round(mean, 1)})

for name, src in REFS:
    out = os.path.join(FR, name)
    if not os.path.exists(out):
        with Image.open(src) as im:
            im.convert("RGB").save(out, "PNG")
    with Image.open(out) as im:
        sz, mode = im.size, im.mode
    rows.append({"id": "REF", "file": out, "size": sz, "mode": mode,
                 "bytes": os.path.getsize(out), "sha": sha(out)})

gates = []
for r in rows:
    if r["id"] == "REF":
        gates.append((f"ref on disk {os.path.basename(r['file'])} {r['size']}",
                      r["bytes"] > 1000 and min(r["size"]) >= 256, f"{r['size']} {r['mode']}"))
        continue
    gates.append((f"{r['id'].split('_')[3]} f{r['i']} t={r['t']}s frame {r['size']} non-black",
                  tuple(r["size"]) == (1344, 768) and 8.0 < r["mean"] < 245.0,
                  f"mean={r['mean']} bytes={r['bytes']}"))
byk = {(r["id"], r["i"]): r for r in rows if r["id"] != "REF"}
for i in range(len(TS)):
    a, b = byk[(IDS[0], i)], byk[(IDS[1], i)]
    gates.append((f"stamp {i} (t={TS[i]}s) r3r vs r3b frames DIFFER (two distinct renders)",
                  a["sha"] != b["sha"], f"{a['sha'][:8]} vs {b['sha'][:8]}"))
for cid in IDS:
    gates.append((f"{cid.split('_')[3]} f0 vs f4 frames DIFFER (motion inside the clip)",
                  byk[(cid, 0)]["sha"] != byk[(cid, 4)]["sha"],
                  f"{byk[(cid, 0)]['sha'][:8]} vs {byk[(cid, 4)]['sha'][:8]}"))
gates.append(("10 stamps + 3 refs written (2 clips x 5 stamps, no gap)",
              len([r for r in rows if r["id"] != "REF"]) == 10
              and len([r for r in rows if r["id"] == "REF"]) == 3, "count"))

print("file | size | bytes | mean | sha8")
for r in rows:
    print(" | ".join([os.path.basename(r["file"]), str(r["size"]), str(r["bytes"]),
                      str(r.get("mean", "")), r["sha"][:8]]))
print()
bad = [g for g in gates if not g[1]]
for n, ok, det in gates:
    print(("PASS " if ok else "FAIL ") + n + ("  [" + str(det) + "]" if det else ""))
print()
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(g[0] for g in bad))
raise SystemExit(0 if not bad else 1)
