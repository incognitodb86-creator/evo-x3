"""U7 blind scoring (KTD12, C8-R). No ComfyUI, no LLM, CPU only.

build_sheets: one contact sheet per panel. Tiles = every real output (R6) of every arm/seed + the UNEDITED still as
one more blind arm "ORIG", shuffled under random codes (seeded). The head ref is shown labelled. show_original=False
by default: a labelled original next to a blind ORIG tile would give that code away. key.csv is written apart.
tally: joins MA's review.csv with the key. A panel is usable for an arm when >=1 of its codes passes all five checks.
Counts per arm, per aspect (9:16 / 16:9) and per cast (single / multi), Wilson 95%, paired tables vs ORIG and vs L,
and whether the arm reaches the C8 bar (6/30). Output never uses the words reserved for Derek (R5).
"""
import csv
import json
import math
import os
import random
import string

from PIL import Image, ImageDraw

import config
import flux_edit_guard as guard
import flux_edit_run as run

CHECKS = ("identity", "rotation", "no_artifact", "body_unchanged", "strict_rest")
TILE_H = 384


def _codes(rng, n, used):
    out = []
    while len(out) < n:
        c = "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        if c not in used:
            used.add(c)
            out.append(c)
    return out


def _tile(path, label):
    with Image.open(path) as im:
        im = im.convert("RGB")
        w = max(1, round(im.width * TILE_H / im.height))
        t = im.resize((w, TILE_H))
    canvas = Image.new("RGB", (w, TILE_H + 24), "white")
    canvas.paste(t, (0, 24))
    ImageDraw.Draw(canvas).text((4, 4), label, fill="black")
    return canvas


def _sheet(tiles, out):
    W = sum(t.width for t in tiles) + 8 * (len(tiles) + 1)
    H = max(t.height for t in tiles) + 16
    s = Image.new("RGB", (W, H), "white")
    x = 8
    for t in tiles:
        s.paste(t, (x, 8))
        x += t.width + 8
    s.save(out, format="PNG")  # PIL writes no text chunks unless asked: no tag/arm metadata leaks


def real_outputs(run_dirs, arms):
    """{(panel, arm, seed): path} for tags that are real per R6 in their own status.log."""
    out = {}
    for rd in run_dirs:
        st = run.parse_log(os.path.join(rd, "status.log"))
        for t in st:
            if not run.is_real(st, t) or t.startswith("canary"):
                continue
            base = t[:-3] if t.endswith("_r1") else t
            panel, _, rest = base.partition("_bfs_")
            arm, _, seed = rest.rpartition("_s")
            p = os.path.join(rd, "phaseA_bfs", t + ".png")
            if arm in arms and os.path.isfile(p):
                out[(panel, arm, seed)] = p
    return out


def build_sheets(run_dirs, inputs_dir, approved_dir, allow_path, out_dir, arms=("L", "E", "CTRL", "E8", "L-FULL"),
                 seed=config.SEEDS[1], show_original=False):
    allow = guard.AllowList(allow_path)
    picks = [r for r in run.load_csv(os.path.join(inputs_dir, "picks.csv")) if r["role"] == "body"]
    heads = {h["character"]: h for h in run.load_csv(os.path.join(inputs_dir, "head_refs.csv"))}
    outs = real_outputs(run_dirs, arms)
    rng = random.Random(seed)
    sheets, keydir = os.path.join(out_dir, "sheets"), os.path.join(out_dir, "key_NOT_FOR_SCORER")
    os.makedirs(sheets, exist_ok=True)
    os.makedirs(keydir, exist_ok=True)
    key, review, used = [], [], set()
    for i, row in enumerate(picks, 1):
        panel = f"p{i:02d}"
        orig = os.path.join(approved_dir, row["path"])
        items = [("ORIG", "-", orig)] + [(a, s, p) for (pn, a, s), p in sorted(outs.items()) if pn == panel]
        for _, _, p in items:
            guard.check_image(p, "read", allow)
        codes = _codes(rng, len(items), used)
        order = list(zip(codes, items))
        rng.shuffle(order)
        h = heads[row["target"]]
        hp = os.path.join(inputs_dir, "head_refs", f"{row['target']}_head.png") if h.get("crop_sha256") \
            else os.path.join(approved_dir, h["source_path"])
        guard.check_image(hp, "read", allow)
        tiles = [_tile(hp, "HEAD REF")]
        if show_original:
            tiles.append(_tile(orig, "ORIGINAL (labelled: ORIG code is NOT blind)"))
        tiles += [_tile(p, code) for code, (_, _, p) in order]
        _sheet(tiles, os.path.join(sheets, f"{panel}.png"))
        for code, (arm, sd, p) in order:
            key.append({"code": code, "panel": panel, "arm": arm, "seed": sd, "file": os.path.basename(p),
                        "aspect": row["aspect"], "cast": row["cast"]})
            review.append(dict({"code": code, "panel": panel}, **{c: "" for c in CHECKS}))
    with open(os.path.join(keydir, "key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0]))
        w.writeheader()
        w.writerows(key)
    with open(os.path.join(out_dir, "review_blank.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["code", "panel", *CHECKS])
        w.writeheader()
        w.writerows(sorted(review, key=lambda r: (r["panel"], r["code"])))
    return key


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def tally(review_csv, key_csv, n_panels=config.N_BODIES):
    key = {r["code"]: r for r in run.load_csv(key_csv)}
    usable = {}  # arm -> set(panel)
    panels_meta, seen = {}, {}
    for r in run.load_csv(review_csv):
        k = key.get(r["code"])
        if k is None:
            raise ValueError(f"code {r['code']} not in key")
        vals = [r[c].strip().upper() for c in CHECKS]
        if any(v not in ("Y", "N") for v in vals):
            raise ValueError(f"code {r['code']} has an unscored check")
        panels_meta[k["panel"]] = (k["aspect"], k["cast"])
        seen.setdefault(k["arm"], set()).add(k["panel"])
        if all(v == "Y" for v in vals):
            usable.setdefault(k["arm"], set()).add(k["panel"])
    rep = {"n_panels": n_panels, "bar": f"{config.C8_BAR}/{n_panels}", "arms": {}, "paired": {},
           "notes": {k: f"{v} NEEDS_DEREK placeholder, not gating" for k, v in config.NEEDS_DEREK.items()}}
    for arm in sorted(seen):
        u = usable.get(arm, set())
        by = lambda i, v: sum(1 for p in u if panels_meta[p][i] == v)  # noqa: E731
        rep["arms"][arm] = {"usable_panels": len(u), "scored_panels": len(seen[arm]), "wilson95": wilson(len(u), n_panels),
                            "reaches_bar": "yes" if len(u) >= config.C8_BAR else "no",
                            "per_aspect": {a: by(0, a) for a in ("9:16", "16:9")},
                            "per_cast": {c: by(1, c) for c in ("single", "multi")}}
    allp = sorted(panels_meta)
    for x, y in [(a, "ORIG") for a in sorted(seen) if a != "ORIG"] + [(a, "L") for a in sorted(seen) if a not in ("L", "ORIG")]:
        if y not in seen:
            continue
        ux, uy = usable.get(x, set()), usable.get(y, set())
        rep["paired"][f"{x}_vs_{y}"] = {"both": sum(p in ux and p in uy for p in allp),
                                       f"only_{x}": sum(p in ux and p not in uy for p in allp),
                                       f"only_{y}": sum(p in uy and p not in ux for p in allp),
                                       "neither": sum(p not in ux and p not in uy for p in allp)}
    return rep


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("sheets"); b.add_argument("--out", required=True); b.add_argument("run_dirs", nargs="+")
    t = sub.add_parser("tally"); t.add_argument("review_csv"); t.add_argument("key_csv")
    a = ap.parse_args()
    root = config.require("ROOT")
    if a.cmd == "sheets":
        n = len(build_sheets(a.run_dirs, os.path.join(root, "inputs"), config.require("APPROVED_DIR"),
                             os.path.join(root, "allow_list.jsonl"), a.out))
        print(f"{n} blind codes written")
    else:
        print(json.dumps(tally(a.review_csv, a.key_csv), indent=1))
