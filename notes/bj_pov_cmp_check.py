#!/usr/bin/env python
# bj_pov_cmp_check.py - the three POV oral cells through Max's judge tools, FLAGS ONLY (2026-10-30).
# b1 = his POV start frame, she enters the frame.        b4 = her close-up as the start frame (his penis from words).
# b5 = b1 + her H3 face LoRA at 0.7 (prompt bytes and seed identical to b1).
# Max's scripts are NOT edited; MANIFEST/RUNS/PROMPTS/OUT are repointed here. Layout they need:
# <runs>/<tag>/<tag>.mp4 + one manifest job per tag. No scores here; Derek gives the only KEEP.
#
# Instrument caveat (stated per job in the manifest and in the summary):
# vlm_judge compares frames to the START IMAGE. b1's start image has no woman in it and the clip's
# job is to bring her in, so same_people/start_kept answer "no" by design there. The checks that
# carry signal on this family: anatomy_defect, target_reached, and the precheck jump threshold.
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"C:\AI\community")
STAGE = ROOT / "review" / "bj-pov-2026-10-30"
JRUNS, JPROMPTS, JOUT = STAGE / "judge_runs", STAGE / "judge_prompts", STAGE / "judge_out"
MANIFEST = STAGE / "cmp_manifest.json"
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))
IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
CELLS = [
    {"tag": "bjpov_b1", "run": "b1_s51083020", "start": "community/bj_pov_20261030/start_pov_768x1344.png",
     "prompt": "C:/Users/derek/sydney/prompts/bj_pov_cell1_20261030.txt",
     "pose": "oral: by the last frame her mouth is on his shaft with deep oral contact, motion still running",
     "caveat": "start image is the man's own lap and shows no woman; the clip's job is to bring her in, "
               "so same_scene/same_people/start_kept are not applicable on this cell"},
    {"tag": "bjpov_b4", "run": "b4_s51083021", "start": "community/bj_pov_20261030/her_close_768x1344.png",
     "prompt": "C:/Users/derek/sydney/prompts/bj_pov_cell4_20261030.txt",
     "pose": "oral: by the last frame her mouth is on his shaft with deep oral contact, motion still running, "
             "her face large in the upper frame",
     "caveat": "the man is not in the start image at all; his penis enters from the lower frame edge, so a "
               "missing-man answer on same_people is the design of this cell, not a break"},
    {"tag": "bjpov_b5_lora", "run": "b5_s51083020_lora", "start": "community/bj_pov_20261030/start_pov_768x1344.png",
     "prompt": "C:/Users/derek/sydney/prompts/bj_pov_cell1_20261030.txt",
     "pose": "oral: by the last frame her mouth is on his shaft with deep oral contact, motion still running",
     "caveat": "same as b1: the start image has no woman in it; this cell differs from b1 by the face LoRA only"},
]
REFS = ["community/bj_pov_20261030/face_a.png", "community/bj_pov_20261030/face_b.png"]


def build():
    for p in (JRUNS, JPROMPTS, JOUT):
        p.mkdir(parents=True, exist_ok=True)
    jobs = []
    for c in CELLS:
        src = ROOT / "runs" / "bj_pov_20261030" / c["run"] / ("bj_pov_" + c["run"] + ".mp4")
        d = JRUNS / c["tag"]
        d.mkdir(exist_ok=True)
        dst = d / (c["tag"] + ".mp4")
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)
        pf = c["tag"] + "_prompt.txt"
        (JPROMPTS / pf).write_text(Path(c["prompt"]).read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
        jobs.append({"tag": c["tag"], "guides": [{"image": c["start"]}],
                     "refs": [c["start"]] + REFS, "prompt_file": pf, "pose": c["pose"],
                     "arm": c["run"], "judged_file": str(src), "judged_size": "768x1344",
                     "instrument_caveat": c["caveat"]})
    MANIFEST.write_text(json.dumps({"jobs": jobs}, indent=1), encoding="utf-8")
    print("staged %d cells: %s" % (len(jobs), ", ".join(j["tag"] for j in jobs)))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vlm", action="store_true")
    ap.add_argument("--frames", type=int, default=16)
    a = ap.parse_args()
    jobs = build()

    import prechecks
    prechecks.MANIFEST, prechecks.RUNS, prechecks.OUT = MANIFEST, JRUNS, JOUT / "cmp_prechecks"
    prechecks.OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for j in jobs:
        r = prechecks.run(j, a.frames)
        (prechecks.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
        summary[j["tag"]] = {"precheck_flags": r["flags"], "dino_prev_min": r["dino"]["prev_min"],
                             "dino_start_last": r["dino"]["start_last"], "cuts_adaptive": r["cuts_adaptive"],
                             "cuts_content": r["cuts_content"]}
        print("precheck %-16s flags=%s prev_min=%.3f start_last=%.3f cuts=%d/%d"
              % (j["tag"], r["flags"] or "none", r["dino"]["prev_min"], r["dino"]["start_last"],
                 r["cuts_adaptive"], r["cuts_content"]), flush=True)

    if a.vlm:
        import vlm_judge as vj
        vj.MANIFEST, vj.RUNS, vj.PROMPTS = MANIFEST, JRUNS, JPROMPTS
        vj.OUT = JOUT / "cmp_vlm"
        vj.OUT.mkdir(parents=True, exist_ok=True)
        vj.take_gpu()
        try:
            for j in jobs:
                r, grid = vj.ask(j)
                grid.save(vj.OUT / (j["tag"] + "_grid.jpg"), quality=85)
                (vj.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
                s = summary.setdefault(j["tag"], {})
                s["vlm_flags"] = r.get("flags", [])
                s["vlm_answers"] = {k: v["answer"] for k, v in (r.get("answers") or {}).items()}
                s["vlm_reasons"] = {k: v["reason"] for k, v in (r.get("answers") or {}).items()}
                print("vlm %-16s %s" % (j["tag"], r.get("flags")), flush=True)
                for k, v in (r.get("answers") or {}).items():
                    print("   %-15s %-3s %s" % (k, v["answer"], v["reason"][:150]))
        finally:
            vj.release_gpu()
    (STAGE / "cmp_flags.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("summary:", STAGE / "cmp_flags.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
