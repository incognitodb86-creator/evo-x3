"""ALI-163 FINAL contact sheet (CPU only, no vision judge, no model calls).

notes/hc_redo_20261023_contact.png
  row 0 = clip 1 OLD (ali147_pool_hc_c1_s51100001, 481 f / 20.04 s)
  row 1 = clip 1 NEW (ali147_pool_hc_r1_s51130001, 243 f / 10.125 s)  <- same timestamps as row 0
  rows 2..6 = the other R-clips (r2, r3, r4, r5, r6), 5 evenly spaced frames each
Frames come from notes/hc_final_frames/<id>_f<n>.png (extracted by notes/ali163_hc_final_media.ps1
at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s, shared across rows).
Label cell = id + seed + start still + reference image(s) from the graph.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont

FR = "C:/AI/community/notes/hc_final_frames"
OBJ = "C:/AI/community/notes/ali163_hc_final_objective.json"
OUT = "C:/AI/community/notes/hc_redo_20261023_contact.png"
TS = [0.50, 2.60, 5.00, 7.40, 9.60]
ROWS = [
    "ali147_pool_hc_c1_s51100001",
    "ali147_pool_hc_r1_s51130001",
    "ali147_pool_hc_r2_s51130002",
    "ali147_pool_hc_r3_s51130003",
    "ali147_pool_hc_r4_s51130004",
    "ali147_pool_hc_r5_s51130005",
    "ali147_pool_hc_r6_s51130006",
]
PICK = {
    "ali147_pool_hc_c1_s51100001": "HC1 BD004 (pair)",
    "ali147_pool_hc_r1_s51130001": "HC1 BD004 (pair)",
    "ali147_pool_hc_r2_s51130002": "HC2 BD007 (pair)",
    "ali147_pool_hc_r3_s51130003": "HC3 GI173 (pair)",
    "ali147_pool_hc_r4_s51130004": "HC4 GI107 (solo)",
    "ali147_pool_hc_r5_s51130005": "HC5 GI150 (solo)",
    "ali147_pool_hc_r6_s51130006": "HC6 BD076 (pair)",
}
TITLE = {
    "ali147_pool_hc_c1_s51100001": "row0 clip1 OLD (481 f, 20.04 s, no sheet refs)",
    "ali147_pool_hc_r1_s51130001": "row1 clip1 NEW (243 f, sheet refs)",
    "ali147_pool_hc_r2_s51130002": "clip2 NEW (243 f, sheet refs)",
    "ali147_pool_hc_r3_s51130003": "clip3 (face-crop refs) NO RENDER",
    "ali147_pool_hc_r4_s51130004": "clip4 (face-crop refs)",
    "ali147_pool_hc_r5_s51130005": "clip5 (face-crop refs)",
    "ali147_pool_hc_r6_s51130006": "clip6 (face-crop refs)",
}

FW, FH, GAP, LAB = 320, 183, 6, 430
obj = {r["id"]: r for r in json.load(open(OBJ, encoding="utf-8"))}


def font(size):
    for p in ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default(size)


f_big, f_lab, f_ts = font(22), font(15), font(16)
row_h = max(FH + 34, 150)
W = LAB + 5 * (FW + GAP) + GAP
H = 40 + 26 + len(ROWS) * (row_h + GAP) + 30
img = Image.new("RGB", (W, H), (16, 16, 16))
d = ImageDraw.Draw(img)
d.text((10, 8), "ALI-163 hc redo contact sheet 2026-10-23 - 5 frames per row at t = "
                "0.50/2.60/5.00/7.40/9.60 s (rows 0-1 same timestamps) - objective only, no vision judge",
       fill=(235, 235, 235), font=f_ts)
x0 = LAB
for i, t in enumerate(TS):
    d.text((x0 + i * (FW + GAP) + GAP, 40), f"t={t:.2f}s", fill=(255, 210, 120), font=f_ts)

y = 40 + 26 + GAP
for cid in ROWS:
    r = obj[cid]
    d.rectangle([0, y, W, y + row_h], fill=(28, 28, 30))
    lines = [TITLE[cid], r["id"], "seed " + str((r.get("seed") or [None])[0]),
             "still " + PICK[cid]]
    refs = r.get("refs") or []
    lines.append("ref1 " + str(refs[0]) if refs else "ref1 -")
    if len(refs) > 1:
        lines.append("ref2 " + str(refs[1]))
    v = r.get("video") or {}
    lines.append(f"ok={r.get('ok')} rc={r.get('rc')} {v.get('w')}x{v.get('h')} "
                 f"{v.get('fps')} f={v.get('packets')}/{r['expected_frames']}")
    lines.append("m4a=" + str(r.get("m4a_exists")) + " " + str(r.get("audio_stream")))
    ty = y + 4
    for ln in lines:
        d.text((8, ty), ln[:58], fill=(225, 225, 225), font=f_lab)
        ty += 20
    if not r.get("mp4_exists"):
        d.rectangle([LAB + GAP, y, LAB + GAP + 5 * (FW + GAP), y + row_h], fill=(60, 20, 20))
        d.text((LAB + GAP + 10, y + row_h // 2 - 22),
               "NO RENDER: result.json rc=2 static-check fail (no mp4, no frames)",
               fill=(255, 200, 200), font=f_ts)
        d.text((LAB + GAP + 10, y + row_h // 2 + 2),
               "graph since fixed (iter 03 builder); job id spent - re-render needs a new id + a cap slot (Max/Derrick)",
               fill=(255, 200, 200), font=f_lab)
    else:
        for i in range(5):
            fp = os.path.join(FR, f"{cid}_f{i}.png")
            if not os.path.exists(fp):
                continue
            with Image.open(fp) as im:
                im = im.convert("RGB").resize((FW, FH))
            img.paste(im, (LAB + GAP + i * (FW + GAP), y + 22))
    y += row_h + GAP

d.text((10, y + 4), "METHOD_ONLY. Face-lock rows 3-6 = face crops from the approved start still "
                    "(R4G2); row 0-1 refs per the graph. Review = contact sheet + ffprobe/hashes; KEEP is Derrick's.",
       fill=(200, 200, 200), font=f_ts)
img.save(OUT)
print("WROTE", OUT, img.size, os.path.getsize(OUT), "bytes")
