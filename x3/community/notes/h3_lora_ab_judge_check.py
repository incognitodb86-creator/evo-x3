#!/usr/bin/env python
# h3_lora_ab_judge_check.py - the L6 flag tier for runs/h3_lora_ab_20261102 (2026-11-02), FLAGS ONLY.
# Max's judge scripts are NOT edited (same driver pattern as notes/bj_pov_judge_check.py and
# notes/terrace_retest_v2_judge_check.py): this file imports them and points MANIFEST/RUNS/PROMPTS/OUT at
# this run, because the layout they require is <runs>/<tag>/<tag>.mp4 + one manifest job per tag.
# No scoring by this lane; no quality claim. Derek gives the only KEEP.
#
# The three cells move one axis each (LoRA file + strength on the model chain); prompt bytes, seed,
# dials, canvas, refs and 124 frames are the a02 base's, so the flags are comparable across the cells
# and against the Oct 30 a01/a02/a03 rows.
#
# INSTRUMENT CAVEAT (stated in the output, the honest reading, not a quality claim): the graph has THREE
# ref slots (ref_image_1 = her close crop as the start frame, ref_image_2/3 = face crops), so prechecks'
# static_no_transition check is not applicable (it is defined for one-ref transition clips) and
# vlm_judge's target_reached question is about a named target pose this family does not have.
# Signal here = anatomy_defect, same_scene, same_people, start_kept, and the precheck DINO thresholds.
#
# The pack stage writes the blinded pack Derek scores: pack/<id>.mp4 with neutral ids from a DOCUMENTED
# shuffle (PACK_RNG_SEED below) and key.csv, which he opens only after the scores are in.
#
# Usage (prechecks are CPU only):
#   C:\AI\community\judge\.venv\Scripts\python.exe notes\h3_lora_ab_judge_check.py            # prechecks + stage
#   ... --vlm      # the VLM flag tier, qwen3vl_judge; takes gpu-render.lock, unloads that model only
#   ... --pack     # build the blinded pack + key.csv (no model, no GPU)
import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"C:\AI\community")
RUNS = ROOT / "runs" / "h3_lora_ab_20261102"
ORDER = RUNS / "_render_order.json"
STAGE = ROOT / "review" / "h3-lora-ab-2026-11-02"
JRUNS, JPROMPTS, JOUT = STAGE / "judge_runs", STAGE / "judge_prompts", STAGE / "judge_out"
MANIFEST = STAGE / "judge_manifest.json"
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))
PREFIX = "h3lora_ab_"
START_IMG = "community/bj_pov_20261030/her_close_768x1344.png"   # graph node "img" = ref_image_1
FACE_A = "community/bj_pov_20261030/face_a.png"
FACE_B = "community/bj_pov_20261030/face_b.png"
PACK_RNG_SEED = "h3-lora-ab-2026-11-02"   # documented: python random.seed(str) -> sha512, stable across runs
POSE = ("this cell has no named target pose: the a02 composition from the START IMAGE continues as prompted "
        "(her face is the start frame, the act is the prompted motion). The target_reached question is about a "
        "target pose the family does not have; judge anatomy, scene/people continuity and start continuity.")
CAVEAT = ("three-ref graph: prechecks' static_no_transition is not applicable (defined for one-ref transition "
          "clips) and vlm_judge's target_reached names a target pose this family does not have. Signal = "
          "anatomy_defect, same_scene, same_people, start_kept, and the DINO/CLIP thresholds.")
FACE_DIR = JOUT  # face_curve_*.json written by notes/bj_pov_face_curve.py via the L6 driver


def cells():
    return json.loads(ORDER.read_text(encoding="utf-8"))["order"]


def sha256_file(path):
    """(d) 2026-11-02: clip_sha256 from the clip bytes, same digest as run_queue.py:235 (was written as "")."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def backfill_clip_sha(key_csv=None, runs=None):
    """(d) fill empty clip_sha256 cells in an existing key.csv from <runs>/<cell>/<cell>.mp4. CPU only, no rescoring;
    every other column is left byte-for-byte as it was. Returns the number of rows filled."""
    key_csv, runs = Path(key_csv or STAGE / "key.csv"), Path(runs or RUNS)
    with open(key_csv, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        fields, rows = rd.fieldnames, list(rd)
    n = 0
    for r in rows:
        if not r.get("clip_sha256"):
            src = runs / r["cell"] / (r["cell"] + ".mp4")
            r["clip_sha256"] = sha256_file(src)
            n += 1
    with open(key_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return n


def face_summary(cell):
    p = FACE_DIR / ("face_curve_%s.json" % cell)
    if not p.exists():
        return {}
    s = json.loads(p.read_text(encoding="utf-8"))["summary"]
    return {"face_probed": s["sampled"], "face_frames": s["frames_with_face"],
            "first_face_frame": s["first_face_frame"], "arcface_cos_mean": s["arcface_cos_mean"],
            "arcface_cos_min": s["arcface_cos_min"]}


def stage():
    for p in (JRUNS, JPROMPTS, JOUT, STAGE / "pack"):
        p.mkdir(parents=True, exist_ok=True)
    jobs = []
    for j in cells():
        cell = j["tag"]
        src = RUNS / cell / (cell + ".mp4")
        assert src.exists(), "no clip for %s" % cell
        graph = json.loads((RUNS / cell / (cell + ".api.json")).read_text(encoding="utf-8"))
        assert graph["img"]["inputs"]["image"] == START_IMG, "start image moved in %s graph" % cell
        tag = PREFIX + cell
        d = JRUNS / tag
        d.mkdir(exist_ok=True)
        dst = d / (tag + ".mp4")
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)
        pf = "%s_prompt.txt" % cell
        (JPROMPTS / pf).write_text(graph["c0"]["inputs"]["prompt"], encoding="utf-8")
        jobs.append({"tag": tag, "cell": cell, "guides": [{"image": START_IMG}],
                     "refs": [START_IMG, FACE_A, FACE_B], "prompt_file": pf, "pose": POSE,
                     "lora": j["lora"], "strength_model": j["strength_model"], "seed": j["seed"],
                     "prompt_sha256": j["prompt_sha256"], "judged_file": str(src),
                     "judged_size": "768x1344", "instrument_caveat": CAVEAT})
    MANIFEST.write_text(json.dumps({"jobs": jobs, "instrument_caveat": CAVEAT}, indent=1), encoding="utf-8")
    print("staged %d clips, manifest %s" % (len(jobs), MANIFEST), flush=True)
    return jobs


def run_prechecks(jobs, frames):
    import prechecks
    prechecks.MANIFEST, prechecks.RUNS, prechecks.OUT = MANIFEST, JRUNS, JOUT / "prechecks"
    prechecks.OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for j in jobs:
        r = prechecks.run(j, frames)
        (prechecks.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
        out[j["tag"]] = {"tag": j["tag"], "cell": j["cell"],
                         **{f"{m}_{s}": r.get(m, {}).get(s) for m in ("dino", "clip")
                            for s in ("start_min", "start_last", "prev_min")},
                         "cuts_adaptive": r.get("cuts_adaptive"), "cuts_content": r.get("cuts_content"),
                         "transition": r.get("transition"), "flags": r.get("flags", []),
                         "info": r.get("info", []), "instrument_caveat": CAVEAT}
        print("precheck %s dino_prev_min=%.3f dino_start_last=%.3f cuts=%s/%s flags=%s"
              % (j["tag"], r["dino"]["prev_min"], r["dino"]["start_last"], r["cuts_adaptive"],
                 r["cuts_content"], r.get("flags") or "none"), flush=True)
    return out


def run_vlm(jobs):
    import vlm_judge as vj
    vj.MANIFEST, vj.RUNS, vj.PROMPTS = MANIFEST, JRUNS, JPROMPTS
    vj.OUT = JOUT / "vlm"
    vj.OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    vj.take_gpu()
    try:
        for j in jobs:
            r, grid = vj.ask(j)
            grid.save(vj.OUT / (j["tag"] + "_grid.jpg"), quality=85)
            (vj.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
            out[j["tag"]] = {"tag": j["tag"], "cell": j["cell"], "secs": r.get("secs"),
                             "flags": r.get("flags", []),
                             "answers": {k: v["answer"] for k, v in (r.get("answers") or {}).items()},
                             "reasons": {k: v["reason"] for k, v in (r.get("answers") or {}).items()},
                             "instrument_caveat": CAVEAT}
            print("vlm %s %.1fs flags=%s" % (j["tag"], r.get("secs") or -1, r.get("flags") or "none"), flush=True)
            for k, v in (r.get("answers") or {}).items():
                print("   %-15s %-3s %s" % (k, v["answer"], v["reason"][:150]))
    finally:
        vj.release_gpu()
    return out


def build_pack(summary):
    """Blinded pack: ids from the documented shuffle, key.csv opened after the scores are in."""
    order = [c["tag"] for c in cells()]
    shuffled = list(order)
    random.seed(PACK_RNG_SEED)
    random.shuffle(shuffled)
    rows = []
    for i, cell in enumerate(shuffled, 1):
        src = RUNS / cell / (cell + ".mp4")
        pid = "a%02d" % i
        pk = STAGE / "pack" / (pid + ".mp4")
        if not pk.exists() or pk.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, pk)
        j = next(x for x in cells() if x["tag"] == cell)
        row = {"pack_id": pid, "cell": cell, "lora": j["lora"], "strength_model": j["strength_model"],
               "bytes": src.stat().st_size, "seed": j["seed"], "prompt_sha256": j["prompt_sha256"][:16],
               "clip_sha256": sha256_file(src), "packaged_as": pid + ".mp4"}
        row.update(face_summary(cell))
        s = summary.get(PREFIX + cell, {})
        row["precheck_flags"] = ";".join(s.get("flags", []))
        row["vlm_flags"] = ";".join(summary.get(PREFIX + cell, {}).get("vlm_flags", []))
        rows.append(row)
    fields = list(rows[0])
    with open(STAGE / "key.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("pack %d clips, ids from seed %r, key %s" % (len(rows), PACK_RNG_SEED, STAGE / "key.csv"))
    for r in rows:
        print("  %s -> %s (%d B)" % (r["packaged_as"], r["cell"], r["bytes"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vlm", action="store_true", help="VLM flag tier (takes gpu-render.lock)")
    ap.add_argument("--pack", action="store_true", help="build the blinded pack + key.csv")
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--backfill-sha", action="store_true", help="(d) only fill empty clip_sha256 in key.csv; no judge, no GPU")
    a = ap.parse_args()
    if a.backfill_sha:
        print("clip_sha256 backfilled rows:", backfill_clip_sha())
        return 0
    jobs = stage()
    summary = run_prechecks(jobs, a.frames)
    if a.vlm:
        v = run_vlm(jobs)
        for t, r in v.items():
            summary[t].update({"vlm_flags": r["flags"], "vlm_answers": r["answers"], "vlm_reasons": r["reasons"]})
    (STAGE / "judge_flags.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("flags summary:", STAGE / "judge_flags.json")
    if a.pack:
        build_pack(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
