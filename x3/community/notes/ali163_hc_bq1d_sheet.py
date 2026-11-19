"""BQ1d side-by-side contact sheet (CPU only, NO vision judge, NO model call, 0 GPU minutes).

writes notes/body_quality_r3b_vs_r3r_contact.png for Derrick's own comparison:
  row A = CONTROL r3r ali147_pool_hc_r3r_s51130003 (face-crop refs only, start still NOT in graph)
  row B = BQ1b   r3b ali147_pool_hc_r3b_s51130003 (start still = Picture 1 body/scene on c0+c1,
          the 2 face crops face-only) - the Max REWIRE
  5 stamps per clip at the SAME timestamps (0.50 / 2.60 / 5.00 / 7.40 / 9.60 s), plus a
  reference row (approved start still + the 2 face crops) and a label cell per clip carrying
  id / seed / still / refs / ok / rc / WxH / fps / packets / audio / m4a / wall / sha8 -
  all read from notes/ali163_hc_bq1d_objective.json (data, not memory).
A missing stamp paints a red MISSING block AND fails the gate, so the sheet can never
silently hide a gap. No image is opened, shown or judged by a model.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

FR = "C:/AI/community/notes/bq1d_frames"
OBJ = "C:/AI/community/notes/ali163_hc_bq1d_objective.json"
OUT = "C:/AI/community/notes/body_quality_r3b_vs_r3r_contact.png"
TS = [0.50, 2.60, 5.00, 7.40, 9.60]
ROWS = [
    ("ali147_pool_hc_r3r_s51130003",
     "A  CONTROL  r3r  (BQ1 defect: face crops only, NO start still in the graph)"),
    ("ali147_pool_hc_r3b_s51130003",
     "B  BQ1b REWIRED  r3b  (start still = Picture 1 body/scene, crops = face-only)"),
]
REFS = [("REF_still_HC3_lesbian_beach.png", "approved start still HC3_lesbian_beach.jpg (1792x1008)"),
        ("REF_w1_face.png", "face crop HC3_w1_face.png (512)"),
        ("REF_w2_face.png", "face crop HC3_w2_face.png (512)")]
FW, FH, GAP, LAB = 336, 192, 6, 470

obj = {r["id"]: r for r in json.load(open(OBJ, encoding="utf-8"))}


def font(size):
    for p in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default(size)


f_t, f_lab, f_ts = font(21), font(14), font(15)
row_h = FH + 44
W = LAB + 5 * (FW + GAP) + GAP
H = 46 + 24 + row_h * len(ROWS) + GAP * len(ROWS) + 30 + (FH + 24) + 34
img = Image.new("RGB", (W, H), (16, 16, 16))
d = ImageDraw.Draw(img)
d.text((10, 6), "BQ1 (ALI-184) body-quality A/B 2026-10-23 - HC3 GI173 - seed 51130003 - "
                "1344x768 / 24 fps / 243 f (124+119) - euler 10 steps shift 10/3, single pass",
       fill=(235, 235, 235), font=f_t)
d.text((10, 26), "stamps at the SAME timestamps in both rows - objective checks only, "
                 "NO vision judge, KEEP is Derrick's; review = this sheet + ffprobe/hashes",
       fill=(200, 200, 200), font=f_ts)
x0 = LAB
for i, t in enumerate(TS):
    d.text((x0 + i * (FW + GAP) + GAP, 46 + 4), f"t = {t:.2f} s", fill=(255, 210, 120), font=f_ts)

pasted, missing = 0, []
y = 46 + 24 + GAP
for cid, title in ROWS:
    r = obj[cid]
    v = r["video"]
    aud = [l for l in r["mp4_streams"]["lines"] if ",audio" in l]
    d.rectangle([0, y, W, y + row_h], fill=(28, 28, 30))
    stills = sorted({s["image"] for n in r["ref_slots"].values() for s in n["slots"]
                     if not s["image"].endswith("_face.png")})
    crops = sorted({s["image"] for n in r["ref_slots"].values() for s in n["slots"]
                    if s["image"].endswith("_face.png")})
    lines = [title, "id   " + cid, "seed " + str(r["seed"]),
             "still " + (stills[0] if stills else "NONE - not in the graph"),
             "refs " + ", ".join(x.split("/")[-1] for x in crops),
             "slots " + " + ".join(f"{k}:{len(n['slots'])}" for k, n in sorted(r["ref_slots"].items()))
             + " " + str({n["ref_image_size"] for n in r["ref_slots"].values()}),
             f"ok={r['ok']} rc={r['rc']} wall={r['wall_min']}m  {v['w']}x{v['h']} {v['fps']} "
             f"f={v['packets']}/{r['expected_frames']}",
             "audio " + ",".join(aud) + f" m4a={r.get('m4a_bytes')}B",
             f"mp4 sha {r['mp4_sha256'][:12]}  graph sha {r['graph_sha256'][:12]}"]
    ty = y + 4
    for ln in lines:
        d.text((8, ty), ln[:64], fill=(225, 225, 225), font=f_lab)
        ty += 19
    for i in range(5):
        fp = os.path.join(FR, f"{cid}_f{i}.png")
        px = LAB + GAP + i * (FW + GAP)
        if not os.path.exists(fp):
            missing.append(fp)
            d.rectangle([px, y + 22, px + FW, y + 22 + FH], fill=(90, 20, 20))
            d.text((px + 6, y + 22 + FH // 2 - 10), "MISSING STAMP", fill=(255, 200, 200), font=f_ts)
            continue
        with Image.open(fp) as im:
            img.paste(im.convert("RGB").resize((FW, FH)), (px, y + 22))
        pasted += 1
    y += row_h + GAP

d.rectangle([0, y, W, y + FH + 30], fill=(24, 30, 24))
d.text((8, y + 4), "REFERENCES (the approved pick + the face crops every later HB arm must use)",
       fill=(210, 235, 210), font=f_ts)
rx = LAB + GAP
for fname, cap in REFS:
    fp = os.path.join(FR, fname)
    if not os.path.exists(fp):
        missing.append(fp)
        d.rectangle([rx, y + 24, rx + FW, y + 24 + FH], fill=(90, 20, 20))
        d.text((rx + 6, y + 24 + FH // 2 - 10), "MISSING REF", fill=(255, 200, 200), font=f_ts)
        rx += FW + GAP
        continue
    with Image.open(fp) as im:
        im = im.convert("RGB")
        im.thumbnail((FW, FH))
        img.paste(im, (rx, y + 24))
    d.text((rx, y + 24 + FH + 2), cap[:52], fill=(200, 220, 200), font=f_lab)
    pasted += 1
    rx += FW + GAP
y += FH + 30

d.text((8, y + 4), "ONE VARIABLE = the ref wiring (same seed, same scene, same frames). "
                   "r3b graph = notes/ali163_hc_bq1_build.py (BQ1b template, prompts "
                   "notes/hc_r3b_c0.txt + _c1.txt); facts notes/ali163_hc_bq1d_objective.json",
       fill=(200, 200, 200), font=f_ts)
img.save(OUT)

# ---- self-check: the file must exist, be big, and contain every stamp (no silent gap)
gates = [("PNG written", os.path.exists(OUT) and os.path.getsize(OUT) > 150_000,
          f"{os.path.getsize(OUT)} bytes"),
         ("13 images pasted (2 clips x 5 stamps + 3 refs)", pasted == 13, f"pasted={pasted}"),
         ("no MISSING block (every stamp + ref on disk)", not missing, ";".join(missing)[:200]),
         ("sheet is a readable RGB image of the planned size",
          Image.open(OUT).size == (W, H) and Image.open(OUT).mode == "RGB",
          f"{Image.open(OUT).size}")]
bad = [g for g in gates if not g[1]]
for n, ok_, det in gates:
    print(("PASS " if ok_ else "FAIL ") + n + ("  [" + str(det) + "]" if det else ""))
print("WROTE", OUT, (W, H), os.path.getsize(OUT), "bytes  GATES",
      len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED")
raise SystemExit(0 if not bad else 1)
