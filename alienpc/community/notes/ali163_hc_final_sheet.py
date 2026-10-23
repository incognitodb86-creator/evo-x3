"""ALI-163 FINAL contact sheet (CPU only, no vision judge, no model calls).

notes/hc_redo_20261023_contact.png
  row 0 = clip 1 OLD (ali147_pool_hc_c1_s51100001, 481 f / 20.04 s)
  row 1 = clip 1 NEW (ali147_pool_hc_r1_s51130001, 243 f / 10.125 s)  <- same timestamps as row 0
  rows 2..8 = the other R-clips (r2, r3 [no render], r3r, r3b, r4, r5, r6), 5 evenly spaced frames each
  r3r = the R6R re-render of clip 3 (face crops only); r3b = the BQ1c rewire (start still + face crops)
Frames come from notes/hc_final_frames/<id>_f<n>.png (extracted by notes/ali163_hc_final_media.ps1
at t = 0.50 / 2.60 / 5.00 / 7.40 / 9.60 s, shared across rows).
Label cell = id + seed + start still + reference image(s) from the graph.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageStat

FR = "C:/AI/community/notes/hc_final_frames"
OBJ = "C:/AI/community/notes/ali163_hc_final_objective.json"
OUT = "C:/AI/community/notes/hc_redo_20261023_contact.png"
TS = [0.50, 2.60, 5.00, 7.40, 9.60]
ROWS = [
    "ali147_pool_hc_c1_s51100001",
    "ali147_pool_hc_r1_s51130001",
    "ali147_pool_hc_r2_s51130002",
    "ali147_pool_hc_r3_s51130003",
    "ali147_pool_hc_r3r_s51130003",
    "ali147_pool_hc_r3b_s51130003",
    "ali147_pool_hc_r4_s51130004",
    "ali147_pool_hc_r5_s51130005",
    "ali147_pool_hc_r6_s51130006",
]
PICK = {
    "ali147_pool_hc_c1_s51100001": "HC1 BD004 (pair)",
    "ali147_pool_hc_r1_s51130001": "HC1 BD004 (pair)",
    "ali147_pool_hc_r2_s51130002": "HC2 BD007 (pair)",
    "ali147_pool_hc_r3_s51130003": "HC3 GI173 (pair)",
    "ali147_pool_hc_r3r_s51130003": "HC3 GI173 (pair)",
    "ali147_pool_hc_r3b_s51130003": "HC3 GI173 (pair)",
    "ali147_pool_hc_r4_s51130004": "HC4 GI107 (solo)",
    "ali147_pool_hc_r5_s51130005": "HC5 GI150 (solo)",
    "ali147_pool_hc_r6_s51130006": "HC6 BD076 (pair)",
}
TITLE = {
    "ali147_pool_hc_c1_s51100001": "row0 clip1 OLD (481 f, 20.04 s, no sheet refs)",
    "ali147_pool_hc_r1_s51130001": "row1 clip1 NEW (243 f, sheet refs)",
    "ali147_pool_hc_r2_s51130002": "clip2 NEW (243 f, sheet refs)",
    "ali147_pool_hc_r3_s51130003": "clip3 (face-crop refs) NO RENDER rc=2",
    "ali147_pool_hc_r3r_s51130003": "clip3 R6R re-render (face crops only, no start still)",
    "ali147_pool_hc_r3b_s51130003": "clip3 BQ1c rewire (start still + 2 face crops)",
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


def fit(s):
    """clip a label to the 430 px label column (measured, not char-counted) so it never runs under the frames"""
    if d.textlength(s, font=f_lab) <= LAB - 16:
        return s
    while s and d.textlength(s + "...", font=f_lab) > LAB - 16:
        s = s[:-1]
    return s + "..."


row_h = max(FH + 34, 150)
W = LAB + 5 * (FW + GAP) + GAP
H = 40 + 26 + len(ROWS) * (row_h + GAP) + 46
img = Image.new("RGB", (W, H), (16, 16, 16))
d = ImageDraw.Draw(img)
d.text((10, 8), "ALI-163 hc redo contact sheet 2026-10-23 (FINAL reopened: rows for r3r + r3b added) - "
                f"5 frames per row at t = {'/'.join(f'{t:.2f}' for t in TS)} s (rows 0-1 same timestamps) - "
                f"{len(ROWS)} rows - objective only, no vision judge",
       fill=(235, 235, 235), font=f_ts)
x0 = LAB
for i, t in enumerate(TS):
    d.text((x0 + i * (FW + GAP) + GAP, 40), f"t={t:.2f}s", fill=(255, 210, 120), font=f_ts)

y = 40 + 26 + GAP
placed = []
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
        d.text((8, ty), fit(ln), fill=(225, 225, 225), font=f_lab)
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
    placed.append((cid, y, bool(r.get("mp4_exists"))))
    y += row_h + GAP

FOOT = [
    "METHOD_ONLY. clip-3 rows: r3 = rc=2 static fail (no render), r3r = the R6R re-render "
    "(face crops only; the start still is NOT in that graph - Max 4:51 PM CT), r3b = the BQ1c rewire "
    "(start still back in c0+c1 + the 2 face crops).",
    "Review = contact sheet + ffprobe -count_packets + ffmpeg stream copy + sha256. No vision judge. KEEP is Derrick's.",
]
d.text((10, y + 4), FOOT[0], fill=(200, 200, 200), font=f_ts)
d.text((10, y + 24), FOOT[1], fill=(200, 200, 200), font=f_ts)
img.save(OUT)
print("WROTE", OUT, img.size, os.path.getsize(OUT), "bytes")

# ---- self-check (pure PIL, no vision judge): every rendered row must show 5 real cells ----
# A missing/duplicate frame = a flat (near-zero stdev) cell = THIS fires. Verified on the real sheet.
prob = Image.open(OUT)
probL = prob.convert("L")
bad = []
for cid, ry, has_mp4 in placed:
    if has_mp4:
        for i in range(5):
            cell = probL.crop((LAB + GAP + i * (FW + GAP) + 2, ry + 24,
                               LAB + GAP + i * (FW + GAP) + FW - 2, ry + 24 + FH - 4))
            st = ImageStat.Stat(cell)
            if st.stddev[0] < 5.0:
                bad.append((cid, i, round(st.stddev[0], 2), "rendered row cell is flat (missing frame?)"))
    else:
        # NO-RENDER row: the frames band must be the red panel, not frames. Text-free top strip of the panel.
        cell = prob.convert("RGB").crop((LAB + GAP + 4, ry + 2, LAB + GAP + 5 * (FW + GAP) - 4, ry + 18))
        mr, mg, mb = ImageStat.Stat(cell).mean
        if not (mr > 40 and mr > mg + 15 and mr > mb + 15):
            bad.append((cid, "panel", [round(x, 1) for x in (mr, mg, mb)],
                        "NO-RENDER row frames band is not the red panel"))
if bad:
    print("SHEET_SELF_CHECK FAIL", bad)
    raise SystemExit(1)
print(f"SHEET_SELF_CHECK PASS: {len(placed)} rows, "
      f"{sum(1 for _, _, h in placed if h)} rendered rows x 5 cells all non-flat, "
      f"{sum(1 for _, _, h in placed if not h)} NO-RENDER row(s) show the panel")
