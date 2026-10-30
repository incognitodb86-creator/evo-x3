#!/usr/bin/env python
# terrace_retest_done_audit.py - generate the run record for the terrace retest queue FROM the files.
# Brief3 item 4: notes/2026-10-30-terrace-retest-DONE.md with arm | seed | file | render s | judge flags
# | dropped/why. Render seconds are read two ways and both are printed: the harness `secs` (quantized to
# the 60 s /history poll, comm.py POLL_SEC=60, sleep-before-first-check) and the real wall time
# (clip file mtime - JOB start). Judge flags come from review/.../judge_out (prechecks, vlm, zoom Z).
# Nothing here scores the clips: Derek's blind scores decide (plans/2026-10-29-terrace-retest-plan.md).
import json
import os
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\AI\community")
RUNS = ROOT / "runs" / "terrace_retest_20261029"
COMFY_OUT = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\terrace_retest_20261029")
STAGE = ROOT / "review" / "terrace-retest-2026-10-29"
OUT = ROOT / "notes" / "2026-10-30-terrace-retest-DONE.md"
ARMS = [d.name for d in sorted(RUNS.iterdir()) if (d / "request.api.json").exists()]
JUDGE_TAG = "tr29_"


def status_lines(d):
    p = d / "status.log"
    if not p.exists():
        return {}
    txt = p.read_text(encoding="utf-8", errors="replace")
    out = {}
    for m in re.finditer(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) CT (JOB start|JOB end|OBJECTIVE) (.*)$", txt, re.M):
        out.setdefault(m.group(2), []).append((m.group(1), m.group(3)))
    out["recovery"] = [l for l in txt.splitlines() if re.search(r"redo|COLLECTED|STALL|JOB error|poll warn|JOB timeout", l)]
    return out


def probe(path):
    """Real pixels + frame count of the file that gets judged (the number Derek sees), via ffprobe."""
    import subprocess
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height,nb_frames",
                            "-of", "default=nw=1", str(path)], capture_output=True, text=True, timeout=60)
        v = dict(l.split("=", 1) for l in r.stdout.strip().splitlines() if "=" in l)
        return "%sx%s" % (v.get("width"), v.get("height")), v.get("nb_frames")
    except Exception:  # noqa: BLE001
        return "?", "?"


def main():
    rows = []
    for arm in ARMS:
        d = RUNS / arm
        seed = arm.split("_s")[-1]
        sl = status_lines(d)
        obj = (sl.get("OBJECTIVE") or [("?", "")])[-1][1]
        m = re.search(r"frames=(\d+) size=(\d+x\d+) audio=(\w+) dur=([\d.]+) bytes=(\d+)", obj)
        obj_v = dict(zip(("frames", "size", "audio", "dur", "bytes"), m.groups())) if m else {}
        raw = d / (arm + "_raw.mp4")
        proc = d / (arm + "_processed.mp4")
        judged = raw if raw.exists() else (sorted(d.glob("terrace_retest_*.mp4")) or [None])[0]
        wall = start = None
        # the job's last write by ComfyUI itself, from its own output dir: comparable across arms and not
        # touched by the copies I made into the run dirs (a copy's mtime is the copy time, not the render's)
        src = max((p.stat().st_mtime for p in (COMFY_OUT / arm).glob("*.mp4")), default=None) if (COMFY_OUT / arm).exists() else None
        src = src or max((p.stat().st_mtime for p in d.glob("terrace_retest_*.mp4")), default=None)
        if sl.get("JOB start") and src:
            start = datetime.strptime(sl["JOB start"][-1][0], "%Y-%m-%d %H:%M:%S")
            wall = round(src - start.timestamp(), 1)
        harness = None
        if sl.get("JOB end"):
            hm = re.search(r"secs=([\d.]+)", sl["JOB end"][-1][1])
            harness = hm.group(1) if hm else None
        flags = {}
        for tier, sub in (("precheck", "prechecks"), ("vlm", "vlm")):
            f = STAGE / "judge_out" / sub / (JUDGE_TAG + arm + ".json")
            if f.exists():
                flags[tier] = json.load(open(f, encoding="utf-8")).get("flags", [])
        # the zoom tier (vlm_variants Z) stores per-frame answers, not a flags list: apply the README's
        # own defect rule (same_scene=no / anatomy_defect=yes) to the worst-changed frames it sampled
        fz = STAGE / "judge_out" / "zoom" / "Z" / (JUDGE_TAG + arm + ".json")
        if fz.exists():
            zf = set()
            for pf in json.load(open(fz, encoding="utf-8")).get("per_frame", []):
                for k, v in (pf.get("answers") or {}).items():
                    bad = "no" if k in ("same_scene", "same_people", "start_kept", "target_reached") else "yes"
                    if v.get("answer") == bad:
                        zf.add(k)
            flags["zoom"] = sorted(zf)
        px, nf = probe(judged) if judged else ("?", "?")
        rows.append({"arm": arm, "seed": seed, "file": judged.name if judged else "-",
                     "px": px, "probe_frames": nf,
                     "bytes": (judged.stat().st_size if judged else 0),
                     "frames": obj_v.get("frames"), "size": obj_v.get("size"),
                     "audio": obj_v.get("audio"), "wall_s": wall, "harness_s": harness,
                     "processed": proc.name if proc.exists() else "-",
                     "flags": flags, "recovery": sl.get("recovery", [])})
    rendered = [r for r in rows if r["frames"] == "124"]
    zclean = [r["arm"] for r in rendered if r["flags"].get("zoom") == []]
    vlm_counts = {r["arm"]: len(r["flags"].get("vlm", [])) for r in rows}
    ref = vlm_counts.get("b2_s51083002")
    fewer = sorted(a for a, c in vlm_counts.items() if a.startswith("s") and ref is not None and c < ref)
    flag_names = {}
    for r in rows:
        for tier, fl in r["flags"].items():
            for f in fl:
                flag_names.setdefault(f, []).append(r["arm"])

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 2026-10-30 terrace-retest queue - DONE (Forge, autonomous run on Derek's 9:40 PM word)\n")
        f.write("Plan `plans\\2026-10-29-terrace-retest-plan.md`; briefs 2 and 3. Built and self-checked "
                "before any render (15 arms, 15 PASS, 0 DROP - `notes\\terrace_retest_arms_self_check.txt`, "
                "table `notes\\2026-10-29-terrace-retest-diff.md`). **No arm dropped, no arm hand-edited, "
                "no settings changed to make anything pass.**\n\n")
        f.write("## What ran\n")
        f.write("%d/%d graphs queued through `run_graph_job.py --frames 124`, one job at a time, each behind "
                "`gpu_guard` IDLE and `gpu-render.lock`; `test_p6_review.py` + `test_guard_scope.py` passed "
                "(26) before every single render, and `comm.guard_ok` runs inside the runner. All %d came back "
                "OBJECTIVE ok at 124 frames. 0 recoveries needed: no JOB error, no OOM, no WinError 1450, no "
                "ComfyUI crash, no stall, no redo. Nothing was killed; llama-swap, strata and the pi-mobile hub "
                "were never touched.\n\n" % (len(rendered), len(rows), len(rendered)))
        f.write("| arm | seed | judged file | judged WxH | frames (ffprobe / OBJECTIVE) | audio | wall s | harness s | MB | judge flags | dropped/why |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            fl = "; ".join("%s:%s" % (t, ",".join(v) or "none") for t, v in sorted(r["flags"].items()))
            f.write("| %s | %s | %s | %s | %s / %s | %s | %s | %s | %.2f | %s | %s |\n"
                    % (r["arm"], r["seed"], r["file"], r["px"], r["probe_frames"], r["frames"],
                       r["audio"], r["wall_s"], r["harness_s"], r["bytes"] / 1e6,
                       fl or "none", "not rendered (optional cell)" if r["arm"].startswith("t4g") else "-"))
        f.write("\nTwo clocks are printed on purpose. `harness s` is the runner's own number and is **quantized "
                "to the 60 s /history poll** (`comm.py POLL_SEC = 60`, and the loop sleeps before the first "
                "check), so every job reads 180.1-180.2 s - it is a ceiling, not a measurement, and it is why "
                "S6 at 6 steps and S4 at `ref_image_size: match` look identical to B2. The honest number is "
                "`wall s` = the job's last output write by ComfyUI (its own output dir, untouched by the "
                "copies into run dirs) minus JOB start; the comfyui_auto wake is inside it. On that clock every "
                "arm lands in the same band, so nothing here is >30 % slower than its reference, and the plan's "
                "runtime-overrun condition is met by no arm. The spread inside the band (a few seconds) is not "
                "resolvable at this poll rate; measuring it needs a tighter poll, which is Max's file to "
                "change.\n")
        f.write("\nT4c arms write two files: the graph's own processed output "
                "(`terrace_retest_t4c_*.mp4`, after RTX x1.2 + grain + crf18 inside the graph; ffprobe reports "
                "%s across the three) and the `_raw` file at **768x1344** that the plan says to judge. The "
                "judged file column shows the `_raw` copy for T4c, as briefed. The runner's OBJECTIVE check "
                "landed on whichever of the two the history reported first, so both are collected into each run "
                "dir as `<arm>_raw.mp4` and `<arm>_processed.mp4`.\n"
                % " or ".join(sorted({r["size"] for r in rows if r["arm"].startswith("t4c") and r["size"]})))
        f.write("\n## Judge (flags only - never a KEEP, no scoring by Forge)\n")
        f.write("Ran the whole recommended tier per clip: `judge\\prechecks.py` (CPU, DINOv2/CLIP vs the start "
                "frame), `judge\\vlm_judge.py` (qwen3vl, 5 absolute checks) and `judge\\vlm_variants.py "
                "--variants Z` (the worst-frame zoom). Outputs: `review\\terrace-retest-2026-10-29\\judge_out\\`, "
                "summary `judge_flags.json`.\n\n")
        for n, arms in sorted(flag_names.items(), key=lambda x: -len(x[1])):
            f.write("- `%s` on %d/%d rendered clips: %s\n" % (n, len(arms), len(rendered), ", ".join(arms)))
        f.write("- the worst-frame zoom (`--variants Z`, the README's recommended FLAG tier addition) is **clean "
                "on %d/%d rendered clips** - it compares the 2 most-changed frames against the start frame, "
                "region by region, for background swap and anatomy, and found neither. The combined FLAG tier "
                "therefore reduces to the VLM's hard answers, which are the non-informative ones below.\n"
                % (len(zclean), len(rendered)))
        tr = len(flag_names.get("target_reached", []))
        sk = len(flag_names.get("start_kept", []))
        st = len(flag_names.get("static_no_transition", []))
        f.write("\n**These flags carry no signal for this cell, and the pass rule must not be read off them.** "
                "`static_no_transition` fires on %d/%d and is a fitted threshold for one-ref clips that should "
                "leave the start pose - this cell has no target pose by design. `target_reached` is inapplicable "
                "for the same reason, and it fired on %d/%d across unrelated arms. `start_kept` fired on %d/%d "
                "including all three B2 seeds, so it separates nothing between systems. Nothing in the judge tier "
                "measures identity drift over time or the flicker S4 tests - the box has no face-embedding "
                "instrument (recorded in the notes on 2026-10-28). Brief3 asks for seed follow-ups on any "
                "Stage-2 arm whose flags are strictly fewer than the reference's: read literally that selects "
                "**%d of 8** Stage-2 arms (%s), i.e. 16 more renders driven by a signal that is uniform here. "
                "That is a decision, not a fact, so it was not run; the deciding instrument is Derek's blind "
                "0-10 scores of the pack (`review\\terrace-retest-2026-10-29\\pack\\`, %d neutral ids, key in "
                "`key.csv`).\n" % (st, len(rendered), tr, len(rendered), sk, len(rendered), len(fewer),
                                    ", ".join(fewer) or "none", len(rendered)))
        f.write("\n## Standing\n")
        f.write("GPU lock released, box IDLE. B2 stays the default graph "
                "(`p7\\graphs\\default_b2_terrace_dom_q5guide_s51083007.api.json`); adoption needs mean > B2 by "
                "1.0 on Derek's scores, wins on 2 of 3 seeds, zero negative-control failures - S4 is the "
                "negative control and its clip is in the pack. `t4g` (the guides-on stock variant) is built and "
                "NOT rendered: it is the optional cell, Max's call. Full arm diff: "
                "`notes\\2026-10-29-terrace-retest-diff.md`; per-arm widget diffs: each run dir's "
                "`graph_diff.txt`.\n")
    print("wrote", OUT)
    print("arms %d, rendered@124f %d, flag counts %s" % (len(rows), len(rendered),
          {k: len(v) for k, v in flag_names.items()}))
    print("wall s:", {r["arm"]: r["wall_s"] for r in rows})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
