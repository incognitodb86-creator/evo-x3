r"""queue_flux_replan.py - FLUX full replan Phases 2, 3, 4, 5, 7 and the deliverable set (brain
40_projects/flux2-overnight/plans/2026-10-30-flux-full-replan.md, approved by Derrick 2:32 PM CT Oct 30; restored by
Derrick 1:25 AM CT Oct 31). Arms, counts, seeds and settings are the plan's own (arm defs: flux-edit-ce-plan-2026-10-28.md
KTD1/KTD2 and the window 1/1b/1c/2 rows). Anything the plans leave unspecified is printed as a GAP and not built.
Phase 6 is queue_storyboard.py.

Inputs = Phase 1's own 30 stills and hand head crops (ComfyUI input community/flux_p1_20261030/<id>_body.*, _head.png)
and Phase 1's request files (the L graph), so every arm runs on the same inputs as L.
Seeds are the plan's fixed seeds (KTD2), so no counter is bumped for seeds; --go takes one run number.

  py queue_flux_replan.py --phase 2            dry run (default; builds under %TEMP%, no lock, no ComfyUI, no counters)
  py queue_flux_replan.py --phase 2 --go       submit, one batch per output size, via run_queue.py --detach
Derrick 2:32 PM CT: "Run Phase 2 only if Phase 1 passes" (C8-R). Phase 1's C8-R result is not recorded; that call is his.
"""
import argparse, copy, csv, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _qcommon as q  # noqa: E402

TEST = "flux_replan"
P1_RUN = "flux_p1_20261030"
P1_DIR = os.path.join(q.RUNS, P1_RUN)
SEEDS = (432262096973493, 20261028)  # KTD2

GAPS = {
    "2": [],
    "3": ["CROP arm (core crop -> BFS -> stitch): the plans give no context size, crop/stitch node set or graph; not built",
          "ANGLE arm: needs Forge's angle-matched head ref per still from the approved folder (skip if none); no picks exist; not built",
          "P-B1 head-mask composite (CPU): runs on the best arms' outputs after Phase 2; mask grow/feather px not set in the plans; no head_boxes.csv in flux_p1_20261030 (picks.csv has crop_box_px for the head crops only); not built",
          "B2 SetLatentNoiseMask round: only if B1 seams > 3; not built"],
    "4": ["Phase 4 runs only if the best arm is still < 6/30 after Phases 2-3 (KTD7); unknown until they are scored",
          "P-C crop+refine at denoise 0.35 needs hand head boxes (head_boxes.csv) and a core-node crop/refine/composite graph; neither exists; not built"],
    "5": ["Pose manifest missing: which 2 characters and which 6 poses (CC0 + Sexinfo sources) are not picked",
          "DWPose skeletons (P1, P10), pose-reference images (P2), TripleView/QuadView refs (P6) not made",
          "P8-P14 slot texts (physics, LIMB_CENSUS, LATERALITY, FLOOR_FOOTER, TOKEN_ORDER) not written",
          "Pass bar C8-P: Derrick sets it before Phase 5 runs (Q11)",
          "~400 jobs (P0-P7 ~216 + P8-P14 168-216) per the plan; not built"],
    "7": ["T1 official Klein 9B distilled edit template (no LoRA): job count per arm not given (phase total ~120-180); template not on AlienPc as an API graph",
          "T3 grid-split blueprint is part of storyboard S5 (queue_storyboard.py)",
          "T4 SDPose only if DWPose fails >= 3/12 in Phase 5 (unknown)",
          "T5 Smart Character Swap: probe first (graph not on AlienPc; a node-by-node face-detector check is required before its go)",
          "T2 MediaPipe face boxes: scoring only, no GPU jobs",
          "Pass bar: +6 vs best arm; best arm not known yet"],
    "deliver": ["Deliverable set: >=3 at 9:16 + >=3 at 16:9, single and multi, from the best available arm, labelled (~12-24 jobs)",
                "Which stills, which arm (S2 is the adopted stills workflow since 1:16 AM CT Oct 31; replan says 'best available arm') and the pose/scene for each are not picked; not built",
                "Not gated on G-KEEP; Derrick picks KEEP"],
}


def p1_cells():
    """[(id, seed, graph)] from Phase 1's L requests (canary excluded), plus picks rows."""
    picks = {r["id"]: r for r in csv.DictReader(open(os.path.join(P1_DIR, "picks.csv"), encoding="utf-8"))}
    out = []
    for p in sorted(glob.glob(os.path.join(P1_DIR, "**", "p1_L_*_s*.request.json"), recursive=True)
                    + glob.glob(os.path.join(P1_DIR, "**", "p1_L_*", "request.api.json"), recursive=True)):
        g = json.load(open(p, encoding="utf-8"))
        g = {k: v for k, v in g.items() if k.isdigit()}
        sid = g["7"]["inputs"]["image"].split("/")[-1].split("_body")[0]
        seed = g["20"]["inputs"]["noise_seed"]
        if sid in picks and seed in SEEDS and (sid, seed) not in [(a, b) for a, b, _ in out]:
            out.append((sid, seed, g))
    return picks, out


def arm_graph(g, arm, prefix, sid):
    g = copy.deepcopy(g)
    lora, samp, sched = g["2"]["inputs"], g["18"]["inputs"], g["19"]
    if arm == "E":
        samp["sampler_name"] = "euler"
    elif arm == "CTRL":
        lora["strength_model"] = 0.0
    elif arm in ("E8", "ES10"):
        samp["sampler_name"] = "euler"
        g["19"] = {"_meta": {"title": "scheduler"}, "class_type": "BasicScheduler",
                   "inputs": {"model": ["2", 0], "scheduler": "simple", "steps": 8 if arm == "E8" else 10, "denoise": 1.0}}
    elif arm == "L-FULL":
        g["8"]["inputs"]["image"] = g["7"]["inputs"]["image"]  # full approved still as the head ref
    elif arm in ("STR08", "STR12", "L05"):
        lora["strength_model"] = {"STR08": 0.8, "STR12": 1.2, "L05": 0.5}[arm]
    g["24"]["inputs"]["filename_prefix"] = prefix
    return g


def str_subset(picks, ids=None):
    """C-STR 6-body subset: first 9:16, first 16:9, first multi in panel order, then the next of each (plan wording:
    'then the next in panel order'; read as the next of each kind)."""
    order = [i for i in picks if ids is None or i in ids]  # the 30 panels, canary excluded
    tests = (lambda r: r["aspect"] == "9:16", lambda r: r["aspect"] == "16:9", lambda r: r["cast"] == "multi")
    pick = []
    for _ in range(2):  # first of each kind, then the next of each kind; a body is used once
        for t in tests:
            pick += [i for i in order if t(picks[i]) and i not in pick][:1]
    return pick


def build(phase, run):
    picks, cells = p1_cells()
    if phase == "2":
        arms = [("E", None), ("CTRL", None), ("E8", None), ("L-FULL", None), ("ES10", {SEEDS[0]}), ("STR08", "sub"), ("STR12", "sub")]
    elif phase == "3":
        arms = [("L05", None)]
    else:
        return picks, cells, []
    sub = str_subset(picks, {c[0] for c in cells})
    sys.path.insert(0, q.SCRIPTS)
    import make_bfs_request as mb  # 1 MP output size, as Phase 1 and queue_klein_explicit
    jobs = []
    for arm, only in arms:
        for sid, seed, g in cells:
            if only == "sub" and sid not in sub: continue
            if isinstance(only, set) and seed not in only: continue
            tag = "p%s_%s_%s_s%d" % (phase, arm, sid, seed)
            r = picks[sid]
            jobs.append(dict(tag=tag, arm=arm, scene=sid, still=sid, seed=seed, job_type="still",
                             size="%dx%d" % mb.expected_size(int(r["w"]), int(r["h"])), aspect=r["aspect"], cast=r["cast"],
                             graph=arm_graph(g, arm, "community/%s/%s" % (run, tag), sid)))
    return picks, cells, jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", choices=["2", "3", "4", "5", "7", "deliver"], required=True)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    go = a.go and not a.dry_run
    problems = []
    if not os.path.isfile(os.path.join(P1_DIR, "picks.csv")):
        sys.exit("BLOCKER missing %s\\picks.csv (Phase 1 inputs)" % P1_DIR)
    test = "%s_p%s" % (TEST, a.phase)
    run, run_dir = q.new_run_dir(test, go and a.phase in ("2", "3"))
    picks, cells, jobs = build(a.phase, run)
    gaps = GAPS[a.phase]
    if a.phase == "2":
        gaps = gaps + ["Derrick 2:32 PM CT: 'Run Phase 2 only if Phase 1 passes' (C8-R); Phase 1's C8-R count is not recorded (MF-6: near-copies)",
                       "L-FULL on multi-character stills: the full still holds both characters' heads (plan does not say which still to use for multi)",
                       "STR08/STR12 subset read as first 9:16, first 16:9, first multi, then the next of each, in picks.csv panel order (canary out): %s" % ",".join(str_subset(picks, {c[0] for c in cells})),
                       "ES10 one-seed vs two-seed unit is open (OQ21, Derrick)", "Pass bar C8 (+6 vs L and meets C8-R) needs Phase 1 L scored"]
    if len(cells) != 60: problems.append("expected 60 Phase 1 L cells (30 stills x 2 seeds), found %d" % len(cells))
    for sid in {j["still"] for j in jobs}:
        for kind in ("body", "head"):
            hits = glob.glob(os.path.join(q.mr.COMFY_IN, "community", P1_RUN, "%s_%s.*" % (sid, kind)))
            if not hits: problems.append("MISSING ComfyUI input community/%s/%s_%s.*" % (P1_RUN, sid, kind))
    problems += q.check_graph_files([j["graph"] for j in jobs])
    try:
        import run_queue as rq
        bad = [j["tag"] for j in jobs if not rq.guard_graph(j["graph"])]
        if bad: problems.append("run_queue.guard_graph refuses: %s" % ", ".join(bad))
    except Exception as e:
        problems.append("NOTE guard_graph not checked (%s)" % str(e)[:80])

    from collections import Counter
    print("%s %s phase=%s run=%s jobs=%d %s" % ("GO" if go else "DRY", TEST, a.phase, run, len(jobs),
          dict(Counter(j["arm"] for j in jobs))))
    for g in gaps: print("GAP " + g)
    for p in problems: print(("BLOCKER " if not p.startswith("NOTE") else "") + p)
    if not jobs:
        print("NOT BUILT: phase %s has no ready jobs (gaps above)" % a.phase); return 2
    orders = []
    for size in sorted({j["size"] for j in jobs}):
        js = [j for j in jobs if j["size"] == size]
        o = q.write_jobs(run_dir, js, "_order_p%s_%s.json" % (a.phase, size),
                         header=dict(run=run, test=test, phase=a.phase, plan="2026-10-30-flux-full-replan.md", inputs=P1_RUN))
        rc, out = q.run_queue_dry(run_dir, o)
        print("--- size %s jobs=%d run_queue --dry-run rc=%d" % (size, len(js), rc)); print(out[-1500:])
        orders.append((o, size))
    if not go:
        print("DRY RUN: nothing submitted, no lock, no ComfyUI, no counter bump (built in %s)" % run_dir)
        return 1 if any(not p.startswith("NOTE") for p in problems) else 0
    if any(not p.startswith("NOTE") for p in problems): sys.exit("FAILED blockers above; nothing submitted")
    for o, size in orders:
        off = q.submit(run_dir, o, size)
        rc = q.wait_closed(run_dir, off)
        print("BATCH %s closed rc=%d" % (size, rc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
