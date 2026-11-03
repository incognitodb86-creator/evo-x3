"""FLX-01 phase gate (plan v3 section 3, V3-5). CPU only: reads a CSV, writes _gate.txt. No GPU, no model call.

Usage: flux_phase_gate.py --phase N --run-dir <dir> [--jobs J] [--report-only]
  --run-dir  the run dir that holds the score CSV being gated (phase N-1's run; for phase 1 close-out, phase 1's own run).
  --jobs     the job count the CSV must cover (default: the PHASE_JOBS table below).
rc 0 GATE PASS (or --report-only), rc 2 GATE FAIL. The bar, the counts and the checked path go to <run-dir>\\_gate.txt.
"""
import argparse, csv, datetime, os, sys

CHECKS = ("Identity", "Face", "Hands", "Contact", "Wardrobe", "OverallQuality")
PHASE_JOBS = {1: 61, 2: 61, 3: None, 4: 30, 5: None, 6: None, 7: None, 8: None}  # None: pass --jobs
HANDS_BAR = 6  # plan v3 table, phase 4: hands < 6/30 (KTD7); hand flags = rows with Hands = no
BAR_TEXT = {
    1: "none; scored as a copy test, counts recorded (report-only)",
    2: "Phase 1 scores.csv present with >= job-count rows",
    3: "Phase 2 scores.csv present with >= job-count rows AND a named winner (winner.txt non-empty in the run dir); "
       "pose manifest check is queue_flux_replan.py's job",
    4: "Phase 3 scores.csv present with >= job-count rows AND hand flags (Hands=no) < %d" % HANDS_BAR,
    5: "Phase 3 winner recorded + pose manifest complete + C8-P bar set by Derrick (not machine-checkable here)",
    6: "Deliverables done + C8-S bar set by Derrick (not machine-checkable here)",
    7: "Phase 6 scored + guard_graph banned-class check per probe (not machine-checkable here)",
    8: "G-SWITCH-EDITS trigger met + model on disk (not machine-checkable here)",
}

def yes(v):
    return str(v).strip().lower() in ("y", "yes", "1", "true", "pass")

def evaluate(phase, run_dir, jobs=None):
    """Return (ok, lines). Pure apart from reading files in run_dir."""
    path = os.path.join(run_dir, "scores.csv")
    jobs = jobs if jobs is not None else PHASE_JOBS.get(phase)
    lines = ["phase: %d" % phase, "bar: %s" % BAR_TEXT.get(phase, "unknown phase"), "checked: %s" % path]
    if phase not in BAR_TEXT:
        return False, lines + ["GATE FAIL: unknown phase %r" % phase]
    if not os.path.isfile(path):
        return False, lines + ["rows: 0", "GATE FAIL: scores.csv missing"]
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    lines.append("rows: %d" % len(rows))
    lines.append("jobs required: %s" % jobs)
    counts = {c: sum(1 for r in rows if yes(r.get(c, ""))) for c in CHECKS}
    lines.append("yes counts: " + ", ".join("%s %d/%d" % (c, counts[c], len(rows)) for c in CHECKS))
    if jobs is None:
        return False, lines + ["GATE FAIL: job count unknown for phase %d (pass --jobs)" % phase]
    if len(rows) < jobs:
        return False, lines + ["GATE FAIL: %d rows < %d jobs" % (len(rows), jobs)]
    if phase in (1, 2):
        return True, lines + ["GATE PASS"]
    if phase == 3:
        w = os.path.join(run_dir, "winner.txt")
        if not (os.path.isfile(w) and open(w, encoding="utf-8").read().strip()):
            return False, lines + ["GATE FAIL: no named winner (%s missing or empty)" % w]
        return True, lines + ["GATE PASS"]
    if phase == 4:
        flags = len(rows) - counts["Hands"]
        lines.append("hand flags: %d (bar < %d)" % (flags, HANDS_BAR))
        if flags >= HANDS_BAR:
            return False, lines + ["GATE FAIL: Phase 4 NOT RUN, hand flags %d >= %d" % (flags, HANDS_BAR)]
        return True, lines + ["GATE PASS"]
    return False, lines + ["GATE FAIL: phase %d bar needs Derrick's written bar; this tool does not pass it" % phase]

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--jobs", type=int)
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.run_dir):
        print("GATE FAIL: run dir missing: %s" % a.run_dir); return 2
    ok, lines = evaluate(a.phase, a.run_dir, a.jobs)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S local")
    out = ["flux_phase_gate %s" % stamp] + lines + (["mode: report-only (rc 0 regardless)"] if a.report_only else [])
    with open(os.path.join(a.run_dir, "_gate.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))
    return 0 if (ok or a.report_only) else 2

if __name__ == "__main__":
    sys.exit(main())
