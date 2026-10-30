#!/usr/bin/env python
# bj_pov_judge_check.py - run Max's judge tools over the POV oral cell, FLAGS ONLY (2026-10-30).
# No scoring by this lane; Derek gives the only KEEP.
# Max's judge scripts are NOT edited: this driver imports them and repoints MANIFEST/RUNS/PROMPTS/OUT
# at this run. Layout they require: <runs>/<tag>/<tag>.mp4 + a manifest job per tag.
#
# INSTRUMENT CAVEAT, stated in the output too (this is the honest reading, not a quality claim):
# vlm_judge's same_scene / same_people / start_kept questions compare the frames with the START IMAGE.
# This cell's start image is a first-person shot of the man's lap with NO woman in it, and the clip's
# job is to bring her into frame, so same_people and start_kept are expected to answer "no" by design.
# The checks that carry signal on this cell: anatomy_defect (melt, malformed genitals/hands),
# target_reached (oral contact in the last frame), and the precheck DINO jump threshold.
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"C:\AI\community")
RUNDIR = ROOT / "runs" / "bj_pov_20261030" / "b1_s51083020"
CLIP = RUNDIR / "bj_pov_b1_s51083020.mp4"
PROMPT_OF_RECORD = Path(r"C:/Users/derek/sydney/prompts/bj_pov_cell1_20261030.txt")
START_IMG = "community/bj_pov_20261030/start_pov_768x1344.png"
FACE_A = "community/bj_pov_20261030/face_a.png"
FACE_B = "community/bj_pov_20261030/face_b.png"
STAGE = ROOT / "review" / "bj-pov-2026-10-30"
JRUNS, JPROMPTS, JOUT = STAGE / "judge_runs", STAGE / "judge_prompts", STAGE / "judge_out"
MANIFEST = STAGE / "judge_manifest.json"
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))
TAG = "bjpov_b1_s51083020"
POSE = ("the act is oral, not a target pose: by the last frame the woman's mouth is on the man's shaft with "
        "deep oral contact and the motion is still running; judge anatomy and the contact, and treat the "
        "start-image comparison checks as not applicable (the start image is the man's own lap and contains "
        "no woman, and the clip's task is to bring her into frame)")
CAVEAT = ("start-image comparison checks (same_scene, same_people, start_kept) are not applicable to this "
          "cell: the start image is a first-person lap shot with no woman in it and the clip must add her. "
          "Signal here = anatomy_defect, target_reached, and the precheck jump threshold.")


def build():
    for p in (JRUNS, JPROMPTS, JOUT):
        p.mkdir(parents=True, exist_ok=True)
    (JPROMPTS / "bj_pov_prompt.txt").write_text(
        PROMPT_OF_RECORD.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    d = JRUNS / TAG
    d.mkdir(exist_ok=True)
    dst = d / (TAG + ".mp4")
    if not dst.exists() or dst.stat().st_size != CLIP.stat().st_size:
        shutil.copyfile(CLIP, dst)
    jobs = [{"tag": TAG, "guides": [{"image": START_IMG}],
             "refs": [START_IMG, FACE_A, FACE_B], "prompt_file": "bj_pov_prompt.txt",
             "pose": POSE, "arm": "b1_s51083020", "judged_file": str(CLIP),
             "judged_size": "768x1344", "instrument_caveat": CAVEAT}]
    MANIFEST.write_text(json.dumps({"jobs": jobs}, indent=1), encoding="utf-8")
    print("staged 1 clip, manifest", MANIFEST, "refs=%d" % len(jobs[0]["refs"]))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vlm", action="store_true", help="run vlm_judge (takes the GPU lock)")
    ap.add_argument("--zoom", action="store_true", help="worst-frame zoom tier (vlm_variants Z)")
    ap.add_argument("--frames", type=int, default=16)
    a = ap.parse_args()
    jobs = build()

    import prechecks
    prechecks.MANIFEST, prechecks.RUNS, prechecks.OUT = MANIFEST, JRUNS, JOUT / "prechecks"
    prechecks.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for j in jobs:
        r = prechecks.run(j, a.frames)
        (prechecks.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
        rows.append({"tag": j["tag"],
                     **{f"{m}_{s}": r.get(m, {}).get(s) for m in ("dino", "clip")
                        for s in ("start_min", "start_last", "prev_min")},
                     "cuts_adaptive": r.get("cuts_adaptive"), "transition": r.get("transition"),
                     "flags": ";".join(r.get("flags", [])), "info": ";".join(r.get("info", []))})
        print("precheck", j["tag"], r.get("flags") or "ok",
              "dino_prev_min=%.3f dino_start_last=%.3f" % (r["dino"]["prev_min"], r["dino"]["start_last"]),
              flush=True)

    def patch():
        import vlm_judge as vj
        vj.MANIFEST, vj.RUNS, vj.PROMPTS = MANIFEST, JRUNS, JPROMPTS
        return vj

    if a.zoom:
        import runpy
        vj = patch()
        vj.OUT = JOUT / "zoom"
        vj.OUT.mkdir(parents=True, exist_ok=True)
        sys.argv = ["vlm_variants.py", "--variants", "Z", "--match", TAG, "--out", str(JOUT / "zoom")]
        runpy.run_path(str(JUDGE_DIR / "vlm_variants.py"), run_name="__main__")
        return 0

    summary = {r["tag"]: r for r in rows}
    if a.vlm:
        vj = patch()
        vj.OUT = JOUT / "vlm"
        vj.OUT.mkdir(parents=True, exist_ok=True)
        vj.take_gpu()
        try:
            for j in jobs:
                r, grid = vj.ask(j)
                grid.save(vj.OUT / (j["tag"] + "_grid.jpg"), quality=85)
                (vj.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
                s = summary.setdefault(j["tag"], {"tag": j["tag"]})
                s["vlm_flags"] = ";".join(r.get("flags", []))
                s["vlm_answers"] = {k: v["answer"] for k, v in (r.get("answers") or {}).items()}
                s["vlm_reasons"] = {k: v["reason"] for k, v in (r.get("answers") or {}).items()}
                s["instrument_caveat"] = CAVEAT
                print("vlm", j["tag"], r.get("flags"), flush=True)
                for k, v in (r.get("answers") or {}).items():
                    print("   %-15s %-3s %s" % (k, v["answer"], v["reason"][:160]))
        finally:
            vj.release_gpu()
    (STAGE / "judge_flags.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("flags summary:", STAGE / "judge_flags.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
