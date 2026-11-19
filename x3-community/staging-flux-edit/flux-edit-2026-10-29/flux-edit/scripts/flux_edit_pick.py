"""U2 picker: 30 fresh body stills + 1 canary + one head-ref source per target character (R1, R2, t69u).

Source: APPROVED_DIR/<ID>/<still>, minus E10, any folder starting "_" (_needs_derrick, _dropped), real-named IDs.
Every candidate needs an annotation row (cast, characters, target, angle, adult=Y). Missing/inconsistent
annotation = UNSURE = the whole pick STOPS (never defaulted to single cast). Excluded co-stars reject the still.
Any image used in the 10-17 run (sha256 or path) is rejected. Bodies must be exactly 768x1344 or 1344x768.
Fewer than 30 eligible bodies + 1 canary, or a missed quota, = STOP with the real counts. Seeded, deterministic.
Head crops: crop_head() does PIL crop only, on an MA-given box. Min crop size is a NEEDS_DEREK note, never a gate.
"""
import csv
import os
import random

from PIL import Image

import config
import flux_edit_guard

EXTS = (".png", ".jpg", ".jpeg", ".webp")
ANGLES = ("front", "three-quarter", "side", "profile", "back")
ANGLE_PREF = {"profile": 0, "side": 0, "three-quarter": 1, "back": 2, "front": 3}
PICK_COLS = ["role", "path", "sha256", "w", "h", "aspect", "cast", "characters", "target", "angle", "class", "parents"]
HEAD_COLS = ["character", "source_path", "source_sha256", "angle", "crop_box", "crop_w", "crop_h", "crop_sha256",
             "crop_note"]


class PickStop(Exception):
    def __init__(self, msg, rows=()):
        super().__init__(msg)
        self.rows = list(rows)


def _norm(p):
    return p.replace("\\", "/").strip().lower()


def read_lines(path, what):
    if not path or not os.path.isfile(path):
        raise PickStop(f"required {what} file missing: {path!r}")
    with open(path, encoding="utf-8") as f:
        return [x.strip() for x in f if x.strip() and not x.startswith("#")]


def load_prior(path):
    shas, paths = set(), set()
    for ln in read_lines(path, "10-17 run list"):
        sha, _, p = ln.partition(",")
        shas.add(sha.strip().lower())
        if p:
            paths.add(_norm(p))
            paths.add(_norm(p).split("/")[-1])
    return shas, paths


def load_annotations(path):
    if not path or not os.path.isfile(path):
        raise PickStop(f"annotations file missing: {path!r}")
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        k = _norm(r.get("path", ""))
        if k in out:
            raise PickStop(f"duplicate annotation row {k}")
        out[k] = r
    return out


def scan(approved_dir, real_named, annotations, prior):
    """Return (candidates, rejected, unsure). Candidate dict has every picks.csv field except role."""
    if not os.path.isdir(approved_dir):
        raise PickStop(f"approved folder missing: {approved_dir}")
    excluded_ids = set(config.EXCLUDED_IDS) | set(real_named)
    approved_ids = set()
    rejected, unsure, cands = [], [], []
    for cid in sorted(os.listdir(approved_dir)):
        full = os.path.join(approved_dir, cid)
        if not os.path.isdir(full):
            continue
        if cid.startswith("_") or cid in excluded_ids:
            rejected.append((cid + "/", "excluded folder (E10/_needs_derrick/_dropped/real-named)"))
            continue
        approved_ids.add(cid)
    p_sha, p_path = prior
    for cid in sorted(approved_ids):
        for root, dirs, files in os.walk(os.path.join(approved_dir, cid)):
            dirs[:] = sorted(d for d in dirs if not d.startswith("_"))
            for fn in sorted(files):
                if not fn.lower().endswith(EXTS):
                    continue
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, approved_dir).replace(os.sep, "/")
                sha = flux_edit_guard.sha256_file(full)
                if sha in p_sha or _norm(rel) in p_path or _norm(fn) in p_path:
                    rejected.append((rel, "used in 10-17 run"))
                    continue
                a = annotations.get(_norm(rel))
                if a is None:
                    unsure.append((rel, "no annotation row (UNSURE)"))
                    continue
                chars = [c.strip() for c in (a.get("characters") or "").split(";") if c.strip()]
                cast, target = (a.get("cast") or "").strip(), (a.get("target") or "").strip()
                angle = (a.get("angle") or "").strip()
                if (a.get("adult") or "").strip().upper() != "Y":
                    unsure.append((rel, "adult != Y (UNSURE)"))
                    continue
                if not chars or cast not in ("single", "multi") or (cast == "single") != (len(chars) == 1) \
                        or target not in chars or angle not in ANGLES or cid not in chars:
                    unsure.append((rel, "annotation inconsistent (UNSURE)"))
                    continue
                bad = [c for c in chars if c not in approved_ids]
                if bad:
                    rejected.append((rel, f"character not on approved list: {';'.join(bad)}"))
                    continue
                with Image.open(full) as im:
                    w, h = im.size
                cands.append({"path": rel, "sha256": sha, "w": w, "h": h, "aspect": config.ASPECTS.get((w, h), "other"),
                              "cast": cast, "characters": ";".join(chars), "target": target, "angle": angle,
                              "class": "approved", "parents": ""})
    return cands, rejected, unsure


def pick(cands, seed=config.SEEDS[1], n=config.N_BODIES, k=config.MIN_PER_ASPECT):
    pool = [c for c in cands if c["aspect"] != "other"]
    rng = random.Random(seed)
    pool.sort(key=lambda c: c["sha256"])
    rng.shuffle(pool)
    canary = next((c for c in pool if c["angle"] == "front" and c["cast"] == "single"), None) \
        or next((c for c in pool if c["angle"] == "front"), None)
    if canary is None:
        raise PickStop("no front-angle still at an exact size for the canary")
    rest = sorted((c for c in pool if c is not canary), key=lambda c: ANGLE_PREF[c["angle"]])
    counts = {"eligible_bodies": len(rest), "9:16": sum(c["aspect"] == "9:16" for c in rest),
              "16:9": sum(c["aspect"] == "16:9" for c in rest), "single": sum(c["cast"] == "single" for c in rest),
              "multi": sum(c["cast"] == "multi" for c in rest)}
    if len(rest) < n:
        raise PickStop(f"only {len(rest)} eligible bodies (+1 canary), need {n}: recount, no generation", [counts])
    if counts["9:16"] < k or counts["16:9"] < k or counts["single"] < 1 or counts["multi"] < 1:
        raise PickStop(f"quota not met {counts} (need >={k} per aspect, >=1 single, >=1 multi)", [counts])
    chosen = []
    quotas = [("aspect", "9:16", k), ("aspect", "16:9", k), ("cast", "single", 1), ("cast", "multi", 1)]
    for field, val, q in quotas:
        for c in rest:
            if sum(x[field] == val for x in chosen) >= q:
                break
            if c not in chosen and c[field] == val:
                chosen.append(c)
    for c in rest:
        if len(chosen) >= n:
            break
        if c not in chosen:
            chosen.append(c)
    return canary, chosen


def pick_head_sources(cands, bodies, canary, seed=config.SEEDS[1]):
    used = {c["sha256"] for c in bodies} | {canary["sha256"]}
    targets = sorted({c["target"] for c in bodies} | {canary["target"]})
    rng = random.Random(seed)
    out, missing = {}, []
    for t in targets:
        pool = sorted((c for c in cands if c["cast"] == "single" and c["target"] == t and c["sha256"] not in used),
                      key=lambda c: c["sha256"])
        rng.shuffle(pool)
        pool.sort(key=lambda c: c["angle"] != "front")
        if not pool:
            missing.append(t)
        else:
            out[t] = pool[0]
    if missing:
        raise PickStop(f"no head-ref source (single cast, not a body/canary) for {missing}")
    return out


def crop_head(src, box, out_path):
    """PIL crop only (no generation). Returns (w, h, sha256, note). Min size is a NEEDS_DEREK note, never a gate."""
    x, y, w, h = box
    with Image.open(src) as im:
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > im.width or y + h > im.height:
            raise PickStop(f"crop box {box} outside {im.size}")
        im.crop((x, y, x + w, y + h)).save(out_path, format="PNG", optimize=False)
    m = config.NEEDS_DEREK["HEAD_CROP_MIN_PX"]
    note = f"NEEDS_DEREK placeholder min {m}px: {'below' if min(w, h) < m else 'at/above'} (not a gate)"
    return w, h, flux_edit_guard.sha256_file(out_path), note


def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow({c: r.get(c, "") for c in cols})


def run(approved_dir, annotations_csv, real_named_file, prior_file, out_dir, seed=config.SEEDS[1]):
    os.makedirs(out_dir, exist_ok=True)
    real_named = read_lines(real_named_file, "real-named list")  # required file; may be empty
    cands, rejected, unsure = scan(approved_dir, real_named, load_annotations(annotations_csv), load_prior(prior_file))
    write_csv(os.path.join(out_dir, "rejected.csv"), ["path", "reason"],
              [{"path": p, "reason": r} for p, r in rejected + unsure])
    if unsure:
        raise PickStop(f"{len(unsure)} still(s) UNSURE (annotation missing/inconsistent): stop, see rejected.csv", unsure)
    canary, bodies = pick(cands, seed)
    heads = pick_head_sources(cands, bodies, canary, seed)
    rows = [dict(canary, role="canary")] + [dict(b, role="body") for b in bodies]
    write_csv(os.path.join(out_dir, "picks.csv"), PICK_COLS, rows)
    write_csv(os.path.join(out_dir, "head_refs.csv"), HEAD_COLS,
              [{"character": t, "source_path": c["path"], "source_sha256": c["sha256"], "angle": c["angle"],
                "crop_box": "PENDING_MA", "crop_note": "MA proposes the box (U2 step 2)"} for t, c in sorted(heads.items())])
    return rows, heads


def verify_picks(picks_csv, approved_dir):
    """Re-hash every pick before freezing/using. Missing file or sha mismatch = stop with the list."""
    with open(picks_csv, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = []
    for r in rows:
        p = os.path.join(approved_dir, r["path"])
        if not os.path.isfile(p):
            bad.append((r["path"], "missing"))
        elif flux_edit_guard.sha256_file(p) != r["sha256"]:
            bad.append((r["path"], "sha256 changed"))
    if bad:
        raise PickStop(f"{len(bad)} picked file(s) missing or changed", bad)
    return rows


if __name__ == "__main__":
    import sys
    try:
        rows, heads = run(config.require("APPROVED_DIR"), config.require("ANNOTATIONS"), config.require("REAL_NAMED"),
                          config.require("PRIOR_RUN"), os.path.join(config.require("ROOT"), "inputs"))
        print(f"picked {len(rows) - 1} bodies + 1 canary, {len(heads)} head-ref sources")
    except PickStop as e:
        print("STOP:", e)
        for r in e.rows:
            print("  ", r)
        sys.exit(2)
