#!/usr/bin/env python
# terrace_retest_v2_judge_check.py - run Max's judge tools over the terrace-retest v2 clips, FLAGS ONLY.
# Brief5 item 2 (Max2, 2026-10-30 5:30 AM): "Judges flag-only per clip (prechecks, vlm_judge,
# vlm_variants --variants Z); T4c judged on its _raw. No scoring by Forge; Max scores."
# Max's judge scripts are NOT edited: this driver imports them and points their manifest/runs/prompt/output paths
# at this run. Layout they require: <runs>/<tag>/<tag>.mp4 + a manifest job per tag.
# Copy of notes\terrace_retest_judge_check.py (v1) repointed to runs/terrace_retest_v2_20261030, with the prompt
# of record = notes/2026-10-30-terrace-b2v2-prompt.txt (Subject 2 clearly willing), so the VLM is shown the prompt
# that was actually submitted.
# Pack note for the score: the neutral ids follow the same sorted arm order as the v1 pack, so aNN here and the
# same aNN in review/terrace-retest-2026-10-29/pack are the SAME arm and seed - the only difference between the
# two packs is the prompt. key.csv is opened only after the scores are in.
# Usage: C:\AI\community\judge\.venv\Scripts\python.exe notes\terrace_retest_v2_judge_check.py            # prechecks
#        ... --vlm     # the VLM flag tier (takes the GPU lock)
#        ... --zoom    # the worst-frame zoom tier (vlm_variants Z)
import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"C:\AI\community")
RUNS = ROOT / "runs" / "terrace_retest_v2_20261030"
STAGE = ROOT / "review" / "terrace-retest-v2-2026-10-30"
JRUNS, JPROMPTS, JOUT = STAGE / "judge_runs", STAGE / "judge_prompts", STAGE / "judge_out"
MANIFEST = STAGE / "judge_manifest.json"
JUDGE_DIR = ROOT / "judge"
sys.path.insert(0, str(JUDGE_DIR))
STILL = "community/TERRACE2_768x1344.png"
PROMPT_V2 = ROOT / "notes" / "2026-10-30-terrace-b2v2-prompt.txt"
PREFIX = "terrace_retest_v2_"
TAG = "tr2v2_"
POSE = ("this cell has no target pose - the terrace scene from the start image continues as prompted; "
        "the target_reached check is not applicable here and its answer is not used as a flag")
ARMS = [d.name for d in sorted(RUNS.iterdir()) if (d / "request.api.json").exists()]
JUDGED = {}  # arm -> (source mp4, judged pixel size)


def clip_for(arm):
    d = RUNS / arm
    if (d / (arm + "_raw.mp4")).exists():  # T4c family: judge the pre-post file, as the accepted plan says
        return d / (arm + "_raw.mp4"), "768x1344 raw (pre-RTX, pre-post-process)"
    mp = sorted(p for p in d.glob(PREFIX + "*.mp4") if "_stills_" not in p.name)
    if not mp:
        return None, None
    return mp[0], "768x1344"


def build():
    for p in (JRUNS, JPROMPTS, JOUT, STAGE / "pack"):
        p.mkdir(parents=True, exist_ok=True)
    (JPROMPTS / "b2v2_prompt.txt").write_text(
        PROMPT_V2.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    jobs, key = [], []
    for i, arm in enumerate(ARMS, 1):
        src, size = clip_for(arm)
        if not src:
            continue
        tag = TAG + arm
        d = JRUNS / tag
        d.mkdir(exist_ok=True)
        dst = d / (tag + ".mp4")
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dst)
        pf = "s8_prompt.txt" if arm.startswith("s8_") else "b2v2_prompt.txt"
        if arm.startswith("s8_"):
            g = json.load(open(RUNS / arm / "request.api.json", encoding="utf-8"))
            (JPROMPTS / "s8_prompt.txt").write_text(g["c0"]["inputs"]["prompt"], encoding="utf-8")
        jobs.append({"tag": tag, "guides": [{"image": STILL}], "refs": [STILL], "prompt_file": pf,
                     "pose": POSE, "arm": arm, "judged_file": str(src), "judged_size": size})
        JUDGED[arm] = (str(src), size)
        pid = "a%02d" % i
        pk = STAGE / "pack" / (pid + ".mp4")
        if not pk.exists() or pk.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, pk)
        key.append({"pack_id": pid, "arm": arm, "judged_file": os.path.basename(src),
                    "judged_as": size, "bytes": src.stat().st_size})
    MANIFEST.write_text(json.dumps({"jobs": jobs}, indent=1), encoding="utf-8")
    with open(STAGE / "key.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0]))
        w.writeheader()
        w.writerows(key)
    print("staged %d clips (T4c on _raw), manifest %s, pack %d files, key %s"
          % (len(jobs), MANIFEST, len(key), STAGE / "key.csv"))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vlm", action="store_true", help="run vlm_judge (takes the GPU lock)")
    ap.add_argument("--zoom", action="store_true", help="run only the worst-frame zoom tier")
    ap.add_argument("--frames", type=int, default=16)
    a = ap.parse_args()
    jobs = build()

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
    with open(prechecks.OUT / "prechecks_tr2v2.csv", "w", newline="", encoding="utf-8") as fh:
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
        sys.argv = ["vlm_variants.py", "--variants", "Z", "--match", TAG, "--out", str(JOUT / "zoom")]
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
        print("%-28s precheck=%-22s vlm=%s" % (t, r.get("flags", ""), r.get("vlm_flags", "-")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
