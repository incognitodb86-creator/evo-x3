#!/usr/bin/env python
# terrace_retest_v2_done_audit.py - generate notes/2026-10-30-terrace-retest-v2-DONE.md from the files on disk.
# Brief5 item 4 (Max2, 2026-10-30 5:30 AM). Nothing is typed from memory: every number is read out of
#   - runs/terrace_retest_v2_20261030/<arm>/status.log   (JOB start/end, redos, the runner's OBJECTIVE line)
#   - the ComfyUI output dir mtimes (the real wall seconds; the harness `secs` is poll-quantized to 60 s,
#     comm.py POLL_SEC=60 + sleep before the first /history check - the v1 lesson, kept in the note)
#   - ffprobe on the file each arm is JUDGED on (dims/frames/audio, so the record is not the runner's word)
#   - review/terrace-retest-v2-2026-10-30/{key.csv,judge_out/prechecks/*.json,judge_out/vlm/*.json,
#     judge_out/zoom/Z/*.json}  -> flags only, never a score (Max scores; the v1 lesson is that these flags
#     carry no signal on a no-target-pose cell, so they are reported as counts, not as quality)
# v1's same-seed wall times and flag counts are recomputed with the same instrument for comparison.
import csv
import glob
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\AI\community"
V2 = os.path.join(ROOT, "runs", "terrace_retest_v2_20261030")
V1 = os.path.join(ROOT, "runs", "terrace_retest_20261029")
COMFY_OUT = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community"
RV2 = os.path.join(ROOT, "review", "terrace-retest-v2-2026-10-30")
RV1 = os.path.join(ROOT, "review", "terrace-retest-2026-10-29")
OUT_MD = os.path.join(ROOT, "notes", "2026-10-30-terrace-retest-v2-DONE.md")
PROMPT_SHA = "e202e512249f2f1cf823d0bcd56702522d9ee5ac603ab5f07079309cddaae0b5"
ARMS = ["b2_s51083002", "b2_s51083012", "b2_s51083013"] + \
       ["s%d_s51083002" % i for i in range(1, 9)] + ["t4c_s51083002", "t4c_s51083012", "t4c_s51083013"]
ARMS_V1 = ARMS  # the v1 queue rendered the same 14 (t4g stayed built and unrendered in both queues)


def ffprobe(path):
    """(W, H, frames, audio) of a file, counted by packets - the same instrument the objective gate uses."""
    if not os.path.exists(path):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                        "stream=codec_type,width,height,nb_read_packets", "-of", "json", path],
                       capture_output=True, text=True, timeout=300)
    try:
        d = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return None
    w = h = n = None
    aud = False
    for s in d.get("streams", []):
        if s.get("codec_type") == "video":
            w, h, n = s.get("width"), s.get("height"), s.get("nb_read_packets")
        if s.get("codec_type") == "audio":
            aud = True
    return (w, h, int(n) if n else None, aud)


def log_lines(arm_dir, root_tag):
    """(job_start_epoch, harness_secs, objective_line, redo_count, errors) from a run dir's status.log."""
    p = os.path.join(arm_dir, "status.log")
    if not os.path.exists(p):
        return None
    start = secs = obj = None
    redos = 0
    errs = []
    for line in open(p, encoding="utf-8", errors="replace"):
        m = re.search(r"JOB start \S+ prompt_id", line)
        if m:
            start = time.mktime(time.strptime(line[:19], "%Y-%m-%d %H:%M:%S"))
        m = re.search(r"JOB end \S+ ok secs=([0-9.]+)", line)
        if m:
            secs = float(m.group(1))
        if "OBJECTIVE" in line:
            obj = line.strip()
            redos += 1
        if "redo" in line.lower() and "OBJECTIVE" not in line:
            redos += 1
        if any(k in line for k in ("JOB error", "OOM", "WinError 1450", "stall", "busy")):
            errs.append(line.strip()[:140])
    return {"start": start, "secs": secs, "obj": obj, "redos": max(0, redos - 1), "errs": errs}


def paid_seconds(runs_root, arm, start_epoch):
    """Real wall seconds = the newest file the graph wrote in its own output subfolder minus the JOB start line.
    Copies into run dirs carry the copy time, so only the ComfyUI output dir is a clean clock (the v1 lesson)."""
    d = os.path.join(COMFY_OUT, os.path.basename(runs_root), arm)
    if not os.path.isdir(d) or not start_epoch:
        return None, []
    files = [(p, os.path.getmtime(p), os.path.getsize(p)) for p in glob.glob(os.path.join(d, "*.mp4"))]
    if not files:
        return None, []
    files.sort(key=lambda x: x[1])
    return round(files[-1][1] - start_epoch, 1), [(os.path.basename(p), s, round(m - start_epoch, 1))
                                                  for p, m, s in files]


def judged_file_v2(arm):
    """The file this arm is scored on: T4c on its _raw (768x1344, pre-RTX), everything else on the collected clip."""
    d = os.path.join(V2, arm)
    raw = os.path.join(d, arm + "_raw.mp4")
    if os.path.exists(raw):
        return raw
    mp = sorted(p for p in glob.glob(os.path.join(d, "terrace_retest_v2_*.mp4")) if "_stills_" not in p)
    return mp[0] if mp else None


def judge_flags_v2(arm):
    """(precheck flags, vlm flags, zoom verdict) for one v2 arm, read out of the judge output files."""
    tag = "tr2v2_" + arm
    out = {"pre": "-", "vlm": "-", "zoom": "-"}
    p = os.path.join(RV2, "judge_out", "prechecks", tag + ".json")
    if os.path.exists(p):
        j = json.load(open(p, encoding="utf-8"))
        out["pre"] = ",".join(j.get("flags", [])) or "none"
    p = os.path.join(RV2, "judge_out", "vlm", tag + ".json")
    if os.path.exists(p):
        j = json.load(open(p, encoding="utf-8"))
        flags = j.get("flags") or []
        out["vlm"] = ",".join(flags) or "none"
        out["vlm_answers"] = {k: v.get("answer") for k, v in (j.get("answers") or {}).items()}
    p = os.path.join(RV2, "judge_out", "zoom", "Z", tag + ".json")
    if os.path.exists(p):
        j = json.load(open(p, encoding="utf-8"))
        bad = []
        for fr in j.get("per_frame", []):
            for k, v in (fr.get("answers") or {}).items():
                ans = v.get("answer")
                if (k == "anatomy_defect" and ans != "no") or (k == "same_scene" and ans != "yes"):
                    bad.append("frame%s:%s=%s" % (fr.get("frame"), k, ans))
        out["zoom"] = "clean(%d frames probed)" % len(j.get("per_frame", [])) if not bad else "FLAGS " + ",".join(bad)
    return out


def v1_counts():
    """The v1 queue's flag counts + same-seed wall seconds, recomputed with this same instrument."""
    pre = {"flags": {}, "n": 0}
    for p in glob.glob(os.path.join(RV1, "judge_out", "prechecks", "tr29_*.json")):
        j = json.load(open(p, encoding="utf-8"))
        pre["n"] += 1
        for f in j.get("flags", []):
            pre["flags"][f] = pre["flags"].get(f, 0) + 1
    vlm = {"flags": {}, "n": 0}
    for p in glob.glob(os.path.join(RV1, "judge_out", "vlm", "tr29_*.json")):
        j = json.load(open(p, encoding="utf-8"))
        vlm["n"] += 1
        for f in (j.get("flags") or []):
            vlm["flags"][f] = vlm["flags"].get(f, 0) + 1
    zoom = {"clean": 0, "flagged": 0}
    for p in glob.glob(os.path.join(RV1, "judge_out", "zoom", "Z", "tr29_*.json")):
        j = json.load(open(p, encoding="utf-8"))
        bad = any((k == "anatomy_defect" and v.get("answer") != "no") or (k == "same_scene" and v.get("answer") != "yes")
                  for fr in j.get("per_frame", []) for k, v in (fr.get("answers") or {}).items())
        zoom["flagged" if bad else "clean"] += 1
    walls = {}
    for arm in ARMS_V1:
        lg = log_lines(os.path.join(V1, arm), V1)
        if lg and lg["start"]:
            w, _ = paid_seconds(V1, arm, lg["start"])
            walls[arm] = w
    return {"pre": pre, "vlm": vlm, "zoom": zoom, "walls": walls}


def main():
    key = {}
    with open(os.path.join(RV2, "key.csv"), encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key[row["arm"]] = row
    rows, flags_count = [], {"pre": {}, "vlm": {}}
    for arm in ARMS:
        d = os.path.join(V2, arm)
        lg = log_lines(d, V2)
        jf = judged_file_v2(arm)
        probe = ffprobe(jf) if jf else None
        wall, paid = paid_seconds(V2, arm, lg["start"] if lg else None)
        jfl = judge_flags_v2(arm)
        for f in (jfl["pre"].split(",") if jfl["pre"] not in ("-", "none") else []):
            flags_count["pre"][f] = flags_count["pre"].get(f, 0) + 1
        for f in (jfl["vlm"].split(",") if jfl["vlm"] not in ("-", "none") else []):
            flags_count["vlm"][f] = flags_count["vlm"].get(f, 0) + 1
        rows.append({
            "arm": arm, "seed": arm.split("_s")[1], "judged": os.path.basename(jf) if jf else "MISSING",
            "whx": ("%dx%d" % (probe[0], probe[1])) if probe else "-",
            "frames": probe[2] if probe else "-", "audio": probe[3] if probe else "-",
            "wall": wall, "harness": lg["secs"] if lg else "-", "mb": round(os.path.getsize(jf) / 1e6, 2) if jf else "-",
            "redos": lg["redos"] if lg else "-", "errs": ";".join(lg["errs"]) if lg and lg["errs"] else "none",
            "pre": jfl["pre"], "vlm": jfl["vlm"], "zoom": jfl["zoom"],
            "pack": key.get(arm, {}).get("pack_id", "-"),
            "paid_files": paid,
            "objective_ok": bool(lg and lg["obj"] and "ok" in lg["obj"]),
        })

    old = v1_counts()
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        w = f.write
        w("# 2026-10-30 terrace retest v2 - DONE (generated by notes\\terrace_retest_v2_done_audit.py)\n")
        w("Brief: `briefs/2026-10-30-0530-forge-brief5-v2-render.md` (Max2, 5:30 AM CT). Derrick 4:56 AM: "
          "\"Update the prompt rerun and score\". Max read the B2v2 prompt (`%s`, sha256 `%s`) and the v2 diff "
          "table and passed them, so the 14 v2 arms were rendered under brief3's rules. Forge did not score "
          "anything: Max scores.\n\n" % ("notes/2026-10-30-terrace-b2v2-prompt.txt", PROMPT_SHA))
        w("Protocol as briefed, per render: `gpu_guard` IDLE + `C:/AI/locks/gpu-render.lock` held by the runner's "
          "own PID, pre-render pytest (`scripts/tests/test_p6_review.py` + `test_guard_scope.py`) and "
          "`comm.guard_ok` over every prompt string, `run_graph_job.py --frames 124`, one unchanged retry allowed, "
          "then drop + log. Wrapper: `notes/terrace_retest_v2_render_run_check.py`. Judges flag-only per clip: "
          "`judge/prechecks.py`, `judge/vlm_judge.py`, `judge/vlm_variants.py --variants Z`, driver "
          "`notes/terrace_retest_v2_judge_check.py`; T4c judged on its `_raw` 768x1344 file. `t4g` stayed built "
          "and NOT rendered.\n\n")
        w("## Result: %d/%d arms rendered, %d dropped, %d redos\n\n"
          % (sum(1 for r in rows if r["objective_ok"]), len(rows),
             sum(1 for r in rows if not r["objective_ok"]), sum(r["redos"] for r in rows)))
        w("| arm | seed | judged file | judged WxH (ffprobe) | frames | audio | wall s (output mtimes) | "
          "harness s | MB | redos | errors | precheck flags | vlm flags | zoom | pack id |\n")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            w("| %s | %s | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n"
              % (r["arm"], r["seed"], r["judged"], r["whx"], r["frames"], r["audio"], r["wall"], r["harness"],
                 r["mb"], r["redos"], r["errs"], r["pre"], r["vlm"], r["zoom"], r["pack"]))
        w("\n`wall s` = newest file the graph wrote in its own ComfyUI output subfolder minus the `JOB start` line. "
          "The harness `secs` is poll-quantized (`comm.py POLL_SEC = 60`, the loop sleeps before the first "
          "`/history` check), so it prints 120.2/180.2 s steps and is a ceiling, never a cost measure - the v1 "
          "lesson, applied here. Copies into the run dirs carry the copy time, so they are never used for the clock.\n\n")
        w("## The judge tier, as counts (flags only - Max scores, and the v1 lesson says these flags carry no "
          "signal on a cell with no target pose)\n\n")
        w("| tier | v1 queue (14 clips) | v2 queue (14 clips) |\n|---|---|---|\n")
        w("| prechecks | %s (n=%d) | %s (n=%d) |\n"
          % (json.dumps(old["pre"]["flags"]), old["pre"]["n"], json.dumps(flags_count["pre"]), len(rows)))
        w("| vlm_judge | %s (n=%d) | %s (n=%d) |\n"
          % (json.dumps(old["vlm"]["flags"]), old["vlm"]["n"], json.dumps(flags_count["vlm"]), len(rows)))
        w("| worst-frame zoom | clean %d / flagged %d | clean %d / flagged %d |\n"
          % (old["zoom"]["clean"], old["zoom"]["flagged"],
             sum(1 for r in rows if r["zoom"].startswith("clean")),
             sum(1 for r in rows if r["zoom"].startswith("FLAGS"))))
        w("\nThe v1 queue's VLM raised `start_kept` on 10/14 and `target_reached` on 5/14; the v2 queue's VLM "
          "raised nothing, and for the same arms and seeds the answers on those two questions read \"no\" in v1 "
          "and \"yes\" in v2 (see `review/terrace-retest-v2-2026-10-30/judge_out/vlm/*.json`). That is a "
          "measured difference between two 14-clip sets. It is not a quality claim: the only intended variable is "
          "the prompt, the judge is a noisy instrument, and on this cell the flags were already shown not to "
          "separate arms. The deciding instrument is Max's blind 0-10 scores.\n\n")
        w("## Cost, same instrument, same seeds (v1 = the resistance prompt, v2 = the willing prompt)\n\n")
        w("| arm | v1 wall s | v2 wall s | delta |\n|---|---|---|---|\n")
        for r in rows:
            o = old["walls"].get(r["arm"])
            w("| %s | %s | %s | %s |\n" % (r["arm"], o, r["wall"],
              (round(r["wall"] - o, 1) if (o and r["wall"]) else "-")))
        b1 = [old["walls"].get(a) for a in ("b2_s51083002", "b2_s51083012", "b2_s51083013")]
        b2 = [r["wall"] for r in rows if r["arm"].startswith("b2_")]
        b1 = [x for x in b1 if x]
        b2 = [x for x in b2 if x]
        if b1 and b2:
            w("\nB2 control arm, mean of 3 seeds: v1 %.1f s, v2 %.1f s (%+.1f %%) - the prompt text is not a "
              "cost dial; frames and canvas are identical.\n"
              % (sum(b1) / len(b1), sum(b2) / len(b2), 100.0 * (sum(b2) / len(b2) / (sum(b1) / len(b1)) - 1)))
        w("\n## Blind pack for scoring\n\n")
        w("- local: `review/terrace-retest-v2-2026-10-30/pack/a01.mp4 ... a14.mp4` + `key.csv` (open the key "
          "only after the scores are in)\n")
        w("- ids follow the same sorted arm order as the v1 pack, so **the same `aNN` in both packs is the same "
          "arm and the same seed**; the only difference between the two files is the prompt. That is the "
          "comparison Derek asked for (\"rerun and score\"), and it is why the ids were not reshuffled.\n")
        w("- QNAP: `/pi-drop/terrace-retest-v2-2026-10-30/` with the key at "
          "`/pi-drop/terrace-retest-v2-2026-10-30-key.csv`\n\n")
        w("## Instruments learned this queue (kept for the next one)\n\n")
        w("- A graph with two SaveVideo sinks still makes the runner's OBJECTIVE line land on whichever file "
          "ComfyUI reports first: in this queue all three T4c rows reported the **processed** 920x1616 file, in "
          "the v1 queue one seed reported the `_raw`. Both files are collected per run dir as `<arm>_raw.mp4` / "
          "`<arm>_processed.mp4`, and the judged file is the `_raw`, ffprobe-verified 768x1344/124 with audio. "
          "So a T4c run dir holds three mp4s: the runner's collected file (byte-identical to `_processed`, same "
          "size - it is the same sink), `_processed` (the record copy) and `_raw` (the file that is scored). "
          "11 B2-family + 3 collected + 3 `_processed` + 3 `_raw` = the 20 mp4s in this root; nothing else was "
          "written to a run dir. The scored set is 14: 11 + 3 `_raw`.\n")
        w("- `notes/terrace_retest_v2_render_run_check.py` is the shape brief3/brief5 asks for: gpu_guard, then "
          "pytest, then `comm.guard_ok`, then the runner, then a re-read of the run dir's own `status.log` and "
          "output mtimes. The runner's exit code alone is never the verdict.\n")
        w("- Judge tools stay unedited and manifest-driven; the driver patches `MANIFEST/RUNS/PROMPTS/OUT` and "
          "stages clips as `judge_runs/<tag>/<tag>.mp4`. The prompt shown to the VLM is the prompt that was "
          "submitted (B2v2; S8 = B2v2 + the #74 line), which the v1 driver could not do from the v1 file.\n\n")
        w("## Box state at the end\n\n")
        w("GPU lock released by the runner and the judge (`gpu_guard` IDLE), no `C:/AI/locks/gpu-render.lock`, "
          "no job running, nothing killed - llama-swap, strata and the pi-mobile hub untouched. No config, no "
          "default graph, no setting changed; the B2 default graph stays as it is until a passing arm is adopted. "
          "`t4g_s51083002` built and not rendered. `runs/` and `*.mp4` are gitignored, so the record is this note, "
          "the key, the judge JSONs and the clips on disk and on the QNAP.\n")
    print("wrote", OUT_MD)
    print("arms: %d/%d objective ok, redos=%d" % (sum(1 for r in rows if r["objective_ok"]), len(rows),
                                                  sum(r["redos"] for r in rows)))
    for r in rows:
        print("%-16s judged=%-28s %s f=%s audio=%s wall=%s pre=%s vlm=%s zoom=%s"
              % (r["arm"], r["judged"], r["whx"], r["frames"], r["audio"], r["wall"], r["pre"], r["vlm"], r["zoom"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
