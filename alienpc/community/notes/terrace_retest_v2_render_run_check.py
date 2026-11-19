#!/usr/bin/env python
# terrace_retest_v2_render_run_check.py - one v2 arm through the full brief5 gate, then the runner, then the check.
# Brief5 (Max2, 2026-10-30 5:30 AM): "same rules as brief3: pre-render pytest
# (scripts/tests/test_p6_review.py + test_guard_scope.py) and comm.guard_ok before each render, gpu_guard IDLE +
# C:/AI/locks/gpu-render.lock, run_graph_job.py --frames 124, one unchanged retry on failure then drop + log."
# run_graph_job.py already holds the box's GPU window (gpu_guard + gpu_lock under its own PID) and the adults guard at
# submit; this wrapper adds the two gates the brief names, runs the job for ONE arm, and reads the objective result
# back out of the run dir instead of trusting the exit code alone. It never edits a setting to make an arm pass:
# on a failure it reports, and the caller decides about the single unchanged retry.
# Usage: python notes\terrace_retest_v2_render_run_check.py --arm b2_s51083002 [--retry] [--skip-pytest]
import argparse
import glob
import importlib.util
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\AI\community"
RUNS = os.path.join(ROOT, "runs", "terrace_retest_v2_20261030")
PY = r"C:\AI\director\.venv\Scripts\python.exe"
PYTEST_FILES = [os.path.join("scripts", "tests", "test_p6_review.py"),
                os.path.join("scripts", "tests", "test_guard_scope.py")]
RUNNER = os.path.join(ROOT, "scripts", "run_graph_job.py")
FRAMES = 124
GPU_GUARD_PS = r"C:\AI\director\scripts\gpu_guard.ps1"
GPU_LOCK = r"C:\AI\locks\gpu-render.lock"
OUT_ROOT = os.path.join(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output", "community",
                        "terrace_retest_v2_20261030")


def load_comm():
    spec = importlib.util.spec_from_file_location("comm", os.path.join(ROOT, "scripts", "comm.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["comm"] = m
    spec.loader.exec_module(m)
    return m


def gate_pytest():
    r = subprocess.run([PY, "-m", "pytest", *PYTEST_FILES, "-q", "--no-header", "-p", "no:cacheprovider"],
                       cwd=ROOT, capture_output=True, text=True, timeout=900)
    tail = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()]
    print("pytest:", tail[-1] if tail else "no output", "(rc=%d)" % r.returncode)
    return r.returncode == 0


def gate_guard(comm, graph_path):
    g = json.load(open(graph_path, encoding="utf-8"))
    n, denied = 0, []
    for node in g.values():
        for s in comm.prompt_strings(node.get("inputs", {})):
            n += 1
            if not comm.guard_ok(s):
                denied.append(node.get("class_type"))
    print("adults guard: %d prompt string(s), denied=%s" % (n, denied or "none"))
    return not denied


def gate_gpu():
    r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-File", GPU_GUARD_PS], capture_output=True, text=True, timeout=300)
    out = (r.stdout + r.stderr).strip().replace("\n", " | ")
    print("gpu_guard: rc=%d %s" % (r.returncode, out[:160]))
    held = os.path.exists(GPU_LOCK)
    if held:
        print("!! %s exists: %s" % (GPU_LOCK, open(GPU_LOCK, encoding="utf-8").read().strip()[:120]))
    return r.returncode == 0 and not held


def objective_lines(arm_dir, tag):
    """Read the runner's own lines out of the run dir's status.log: JOB start/end, redos, the collected file."""
    p = os.path.join(arm_dir, "status.log")
    if not os.path.exists(p):
        return []
    keep = []
    for line in open(p, encoding="utf-8", errors="replace"):
        if any(k in line for k in ("JOB start", "JOB end", "redo", "OBJECTIVE", "stall", "guard", "ERROR", "busy")):
            keep.append(line.rstrip("\n"))
    return keep[-8:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--retry", action="store_true", help="this call is the one allowed unchanged retry")
    ap.add_argument("--skip-pytest", action="store_true", help="only for the retry: the gate already passed this turn")
    a = ap.parse_args()
    arm_dir = os.path.join(RUNS, a.arm)
    graph = os.path.join(arm_dir, "request.api.json")
    tag = "terrace_retest_v2_" + a.arm
    if not os.path.exists(graph):
        print("no graph at %s" % graph)
        return 2
    print("=== %s %s (tag %s, frames %d) ===" % ("RETRY " if a.retry else "ARM", a.arm, tag, FRAMES))
    print("job start %s" % time.strftime("%Y-%m-%d %H:%M:%S CT"))
    comm = load_comm()
    if not gate_gpu():
        print("GATE FAIL: gpu")
        return 3
    if not a.skip_pytest and not gate_pytest():
        print("GATE FAIL: pytest")
        return 3
    if not gate_guard(comm, graph):
        print("GATE FAIL: adults guard")
        return 3

    start = time.time()
    r = subprocess.run([PY, "-u", RUNNER, arm_dir, tag, "--frames", str(FRAMES)],
                       cwd=ROOT, capture_output=True, text=True, timeout=3000)
    for line in (r.stdout + r.stderr).strip().splitlines():
        print(line)
    print("runner rc=%d after %.1f s (runner secs are poll-quantized - see the record note)"
          % (r.returncode, time.time() - start))

    mp4s = sorted(glob.glob(os.path.join(arm_dir, "*.mp4")))
    out_dir = os.path.join(OUT_ROOT, a.arm)
    real = []
    if os.path.isdir(out_dir):
        real = [(os.path.basename(p), os.path.getsize(p), os.path.getmtime(p)) for p in glob.glob(os.path.join(out_dir, "*"))]
        real.sort(key=lambda x: x[2])
    print("collected in the run dir: %s" % ([os.path.basename(p) for p in mp4s] or "none"))
    print("ComfyUI output dir %s: %s" % (out_dir, [(n, s, time.strftime("%H:%M:%S", time.localtime(m))) for n, s, m in real] or "none"))
    for line in objective_lines(arm_dir, tag):
        print("status.log |", line)
    ok = r.returncode == 0 and mp4s
    print("=== %s %s ===" % ("OK" if ok else "FAIL", a.arm))
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
