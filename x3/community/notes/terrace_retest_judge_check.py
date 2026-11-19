#!/usr/bin/env python
# terrace_retest_judge_check.py - run the existing judge tools over the terrace-retest clips, flags only.
# Brief3 item 2: "Judge (qwen3vl + Z zoom) flag-only after each clip; T4c on its _raw file. No scoring."
# Max's judge scripts are NOT edited: this driver imports them and points their manifest/runs/prompt/
# output paths at this run. Layout they require: <runs>/<tag>/<tag>.mp4 + a manifest job per tag.
# T4c is judged on the raw pre-post file (768x1344, before RTX and before the graph's post-processing),
# as the accepted plan states; the processed 920x1616 file is kept for the record only.
# It also writes the blinded review pack Derek scores: review/terrace-retest-2026-10-29/pack/<id>.mp4
# with the arm key in key.csv, to be opened only after the scores are in.
# Usage: C:\AI\community\judge\.venv\Scripts\python.exe notes\terrace_retest_judge_check.py [--vlm] [--pack]
import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"C:\AI\community")
RUNS = ROOT / "runs" / "terrace_retest_20261029"
STAGE = ROOT / "review" / "terrace-retest-2026-10-29"
JRUNS, JPROMPTS, JOUT = STAGE / "judge_runs", STAGE / "judge_prompts", STAGE / "judge_out"
MANIFEST = STAGE / "judge_manifest.json"
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))
STILL = "community/TERRACE2_768x1344.png"
B2JSON = ROOT / "runs" / "terrace_dom_q5guide_20261028_s51083007" / "request.api.json"
POSE = ("this cell has no target pose - the terrace scene from the start image continues as prompted; "
        "the target_reached check is not applicable here and its answer is not used as a flag")
ARMS = [d.name for d in sorted(RUNS.iterdir()) if (d / "request.api.json").exists()]
JUDGED = {}  # arm -> (source mp4, judged pixel size)


def clip_for(arm):
    d = RUNS / arm
    if (d / (arm + "_raw.mp4")).exists():  # T4c family: judge the pre-post file
        return d / (arm + "_raw.mp4"), "768x1344 raw (pre-RTX, pre-post-process)"
    mp = sorted(d.glob("terrace_retest_*.mp4"))
    if not mp:
        return None, None
    return mp[0], "768x1344"


def build():
    for p in (JRUNS, JPROMPTS, JOUT, STAGE / "pack"):
        p.mkdir(parents=True, exist_ok=True)
    b2 = json.load(open(B2JSON, encoding="utf-8"))
    b2_prompt = b2["c0"]["inputs"]["prompt"]
    (JPROMPTS / "b2_prompt.txt").write_text(b2_prompt, encoding="utf-8")
    jobs, key = [], []
    for i, arm in enumerate(ARMS, 1):
        src, size = clip_for(arm)
        if not src:
            continue
        tag = "tr29_" + arm
        d = JRUNS / tag
        d.mkdir(exist_ok=True)
        dst = d / (tag + ".mp4")
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)
        pf = "s8_prompt.txt" if arm.startswith("s8_") else "b2_prompt.txt"
        if arm.startswith("s8_"):
            g = json.load(open(RUNS / arm / "request.api.json", encoding="utf-8"))
            (JPROMPTS / "s8_prompt.txt").write_text(g["c0"]["inputs"]["prompt"], encoding="utf-8")
        jobs.append({"tag": tag, "guides": [{"image": STILL}], "refs": [STILL], "prompt_file": pf,
                     "pose": POSE, "arm": arm, "judged_file": str(src), "judged_size": size})
        JUDGED[arm] = (str(src), size)
        # blinded pack: neutral ids, key.csv opened only after scoring
        pid = "a%02d" % i
        pk = STAGE / "pack" / (pid + ".mp4")
        if not pk.exists() or pk.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, pk)
        key.append({"pack_id": pid, "arm": arm, "judged_file": os.path.basename(src),
                    "judged_as": size, "bytes": src.stat().st_size})
    MANIFEST.write_text(json.dumps({"jobs": jobs}, indent=1), encoding="utf-8")
    with open(STAGE / "key.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
    print("staged %d clips (T4c judged on _raw), manifest %s, pack %d files, key %s"
          % (len(jobs), MANIFEST, len(key), STAGE / "key.csv"))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vlm", action="store_true", help="run vlm_judge (takes the GPU lock)")
    ap.add_argument("--zoom", action="store_true", help="run only the worst-frame zoom (Max's recommended FLAG tier addition)")
    ap.add_argument("--frames", type=int, default=16)
    a = ap.parse_args()
    jobs = build()
    tags = {j["tag"] for j in jobs}

    import prechecks
    prechecks.MANIFEST, prechecks.RUNS, prechecks.OUT = MANIFEST, JRUNS, JOUT / "prechecks"
    prechecks.OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for j in jobs:
        try:
            r = prechecks.run(j, a.frames)
        except Exception as e:  # noqa: BLE001
            r = {"tag": j["tag"], "flags": [], "error": repr(e)[:200]}
        (prechecks.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
        rows.append({"tag": j["tag"],
                     **{f"{m}_{s}": r.get(m, {}).get(s) for m in ("dino", "clip")
                        for s in ("start_min", "start_last", "prev_min")},
                     "cuts_adaptive": r.get("cuts_adaptive"), "flags": ";".join(r.get("flags", [])),
                     "info": ";".join(r.get("info", [])), "error": r.get("error", "")})
        print("precheck", j["tag"], r.get("flags") or "ok", flush=True)
    with open(prechecks.OUT / "prechecks_tr29.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def patch_judge_paths():
        import vlm_judge as vj
        vj.MANIFEST, vj.RUNS, vj.PROMPTS = MANIFEST, JRUNS, JPROMPTS
        return vj

    if a.zoom:
        import runpy
        vj = patch_judge_paths()
        vj.OUT = JOUT / "zoom"
        vj.OUT.mkdir(parents=True, exist_ok=True)
        # vlm_variants' own driver is under if __name__ == "__main__", so run it as a script with argv set
        sys.argv = ["vlm_variants.py", "--variants", "Z", "--match", "tr29_", "--out", str(JOUT / "zoom")]
        runpy.run_path(str(JUDGE_DIR / "vlm_variants.py"), run_name="__main__")
        return 0

    summary = {r["tag"]: r for r in rows}
    if a.vlm:
        vj = patch_judge_paths()
        vj.OUT = JOUT / "vlm"
        vj.OUT.mkdir(parents=True, exist_ok=True)
        vj.take_gpu()
        try:
            for j in jobs:
                try:
                    r, grid = vj.ask(j)
                    grid.save(vj.OUT / (j["tag"] + "_grid.jpg"), quality=85)
                except Exception as e:  # noqa: BLE001
                    r = {"tag": j["tag"], "flags": [], "error": repr(e)[:250]}
                (vj.OUT / (j["tag"] + ".json")).write_text(json.dumps(r, indent=1), encoding="utf-8")
                s = summary.setdefault(j["tag"], {"tag": j["tag"]})
                s["vlm_flags"] = ";".join(r.get("flags", []))
                s["vlm_answers"] = {k: v["answer"] for k, v in (r.get("answers") or {}).items()}
                print("vlm", j["tag"], r.get("flags", r.get("error")), flush=True)
        finally:
            vj.release_gpu()
    (STAGE / "judge_flags.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("flags summary:", STAGE / "judge_flags.json")
    for t, r in sorted(summary.items()):
        print("%-26s precheck=%-22s vlm=%s" % (t, r.get("flags", ""), r.get("vlm_flags", "-")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
