#!/usr/bin/env python
# terrace_v3_render_queue.py - brief8 Step B: render the 42 new clips in the drawn order, one GPU job at a time.
# The brief5/brief3 rule set, per job, exactly as Max's CHECKED note re-states it:
#   gpu_guard IDLE + no C:/AI/locks/gpu-render.lock  ->  pre-render pytest (test_p6_review.py + test_guard_scope.py)
#   ->  comm.guard_ok on every prompt string of that graph  ->  run_graph_job.py <run dir> <tag> --frames 124
#   ->  objective read-back: the collected mp4 exists, ffprobe says 768x1344 / 124 frames / audio present.
# The exit code is never the verdict: run_graph_job.py holds the GPU window and the adults guard itself, so this
# driver reads the result back out of the run dir and the ComfyUI output dir. Nothing is ever changed to make an arm
# pass: on a failure the driver does ONE unchanged retry (same graph, same seed), and a second failure stops the
# queue and records it, per the plan's failure rule. Wall seconds come from the ComfyUI output dir mtimes, because
# the harness 'secs' is poll-quantized (comm.POLL_SEC=60) and the copy into the run dir carries the copy time.
# Resumable by design: a job is skipped only if its render_ok.json exists, its recorded prompt sha256 equals the
# prompt in the CURRENT graph (so the S8 rebuild forces a re-render), and the clip re-verifies by ffprobe.
# Usage: python notes\terrace_v3_render_queue.py [--limit 8] [--jobs tag,tag] [--start 1] [--max-jobs-seconds N]
import argparse
import glob
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\AI\community"
RUNS = os.path.join(ROOT, "runs", "terrace_settings_v3_20261030")
ORDER = os.path.join(RUNS, "_render_order.json")
PY = r"C:\AI\director\.venv\Scripts\python.exe"
PYTEST_FILES = [os.path.join("scripts", "tests", "test_p6_review.py"),
                os.path.join("scripts", "tests", "test_guard_scope.py")]
RUNNER = os.path.join(ROOT, "scripts", "run_graph_job.py")
GPU_GUARD_PS = r"C:\AI\director\scripts\gpu_guard.ps1"
GPU_LOCK = r"C:\AI\locks\gpu-render.lock"
ACTIONS = os.path.join(ROOT, "notes", "actions.log")
QLOG = os.path.join(RUNS, "_render_queue.log")
OUT_ROOT = os.path.join(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output", "community",
                        "terrace_settings_v3_20261030")
FRAMES, W, H = 124, 768, 1344


def log(line):
    """One line in the queue log and one in notes/actions.log, both timestamped - the brief says log every step."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    with open(QLOG, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (ts, line))
    with open(ACTIONS, "a", encoding="utf-8") as f:
        f.write("%s Forge brief8 Step B: %s\n" % (ts, line))


def sh(args, cwd=ROOT, timeout=3000):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def load_comm():
    spec = importlib.util.spec_from_file_location("comm", os.path.join(ROOT, "scripts", "comm.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["comm"] = m
    spec.loader.exec_module(m)
    return m


def gate_gpu():
    rc, out = sh(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                  "-File", GPU_GUARD_PS], timeout=300)
    held = os.path.exists(GPU_LOCK)
    txt = out.strip().replace("\n", " | ")[:120]
    print("  gate gpu_guard: rc=%d %s lock_present=%s" % (rc, txt, held))
    return rc == 0 and not held


def gate_pytest():
    rc, out = sh([PY, "-m", "pytest", *PYTEST_FILES, "-q", "--no-header", "-p", "no:cacheprovider"], timeout=900)
    tail = [l for l in out.strip().splitlines() if l.strip()]
    print("  gate pytest: %s (rc=%d)" % (tail[-1] if tail else "no output", rc))
    return rc == 0


def gate_guard(comm, graph):
    g = json.load(open(graph, encoding="utf-8"))
    n, denied = 0, []
    for node in g.values():
        for s in comm.prompt_strings(node.get("inputs", {})):
            n += 1
            if not comm.guard_ok(s):
                denied.append(node.get("class_type"))
    print("  gate adults guard: %d prompt string(s), denied=%s" % (n, denied or "none"))
    return not denied


def prompt_sha(graph):
    g = json.load(open(graph, encoding="utf-8"))
    p = next(n["inputs"]["prompt"] for n in g.values() if n.get("class_type") == "MiniMaxH3ReferenceToVideo")
    return hashlib.sha256(p.encode("utf-8")).hexdigest()


def ffprobe(path):
    rc, out = sh(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path],
                 timeout=180)
    j = json.loads(out or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = [s for s in j.get("streams", []) if s.get("codec_type") == "audio"]
    fr = int(v.get("nb_frames") or 0)
    if not fr:
        dur = float(j.get("format", {}).get("duration") or 0)
        num, _, den = (v.get("avg_frame_rate") or "0/1").partition("/")
        fr = int(round(dur * (float(num) / float(den or 1))))
    return int(v.get("width") or 0), int(v.get("height") or 0), fr, bool(a)


def verify(job_dir, tag):
    """Objective read-back: the collected clip, its pixels/frames/audio, the ComfyUI-side file, and the wall clock."""
    mp4s = sorted(glob.glob(os.path.join(job_dir, "*.mp4")))
    out_dir = os.path.join(OUT_ROOT, tag)
    produced = []
    if os.path.isdir(out_dir):
        produced = sorted([(os.path.getmtime(p), p, os.path.getsize(p)) for p in glob.glob(os.path.join(out_dir, "*"))
                           if os.path.isfile(p)])
    if not mp4s:
        return {"ok": False, "why": "no collected mp4 in the run dir", "produced": [os.path.basename(p) for _m, p, _s in produced]}
    p = mp4s[-1]
    w, h, fr, aud = ffprobe(p)
    ok = (w, h) == (W, H) and fr == FRAMES and aud
    newest = produced[-1] if produced else None
    return {"ok": ok, "clip": p, "clip_sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
            "w": w, "h": h, "frames": fr, "audio": aud, "bytes": os.path.getsize(p),
            "comfyui_out": os.path.relpath(newest[1], OUT_ROOT) if newest else None,
            "comfyui_mtime": newest[0] if newest else None,
            "why": "" if ok else "ffprobe %sx%s/%df audio=%s" % (w, h, fr, aud)}


def render_one(comm, pos, job, retry=False):
    tag = job["tag"]
    job_dir = os.path.join(RUNS, tag)
    graph = os.path.join(job_dir, "request.api.json")
    print("=== pos %d %s tag=%s (arm %s, scene %s, seed %d, frames %d) ==="
          % (pos, "RETRY" if retry else "JOB", tag, job["arm"], job["scene"], job["seed"], FRAMES))
    log("START pos=%d tag=%s arm=%s scene=%s seed=%d%s" % (pos, tag, job["arm"], job["scene"], job["seed"],
                                                            " (the one allowed unchanged retry)" if retry else ""))
    if not os.path.exists(graph):
        print("  FAIL: no graph"); log("FAIL pos=%d tag=%s no graph" % (pos, tag)); return None
    if not gate_gpu():
        print("  GATE FAIL: gpu"); log("GATE-FAIL pos=%d tag=%s gpu not idle" % (pos, tag)); return None
    if not gate_pytest():
        print("  GATE FAIL: pytest"); log("GATE-FAIL pos=%d tag=%s pytest" % (pos, tag)); return None
    if not gate_guard(comm, graph):
        print("  GATE FAIL: adults guard"); log("GATE-FAIL pos=%d tag=%s adults guard" % (pos, tag)); return None
    t0 = time.time()
    rc, out = sh([PY, "-u", RUNNER, job_dir, tag, "--frames", str(FRAMES)], timeout=3000)
    runner_secs = time.time() - t0
    key = [l for l in out.strip().splitlines()
           if any(k in l for k in ("OBJECTIVE", "JOB start", "JOB end", "SKIP", "CLIP_SKIP", "ERROR", "Traceback",
                                   "redo", "busy", "stall", "OOM", "WinError"))]
    for l in key[-10:]:
        print("  runner |", l[:180])
    print("  runner rc=%d wall-call=%.1f s (the runner's own secs is poll-quantized; the real wall is the output mtime)"
          % (rc, runner_secs))
    v = verify(job_dir, tag)
    wall = (v["comfyui_mtime"] - t0) if v.get("comfyui_mtime") else None
    if v["ok"] and rc == 0:
        marker = {"tag": tag, "pos": pos, "arm": job["arm"], "scene": job["scene"], "seed": job["seed"],
                  "frames": FRAMES, "prompt_sha256": prompt_sha(graph), "clip_sha256": v["clip_sha256"],
                  "clip": os.path.relpath(v["clip"], RUNS), "bytes": v["bytes"], "w": v["w"], "h": v["h"],
                  "audio": True, "wall_seconds_output_mtime": round(wall, 1) if wall else None,
                  "runner_rc": rc, "rendered_at": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": retry}
        json.dump(marker, open(os.path.join(job_dir, "render_ok.json"), "w", encoding="utf-8"), indent=1)
        print("  OK %dx%d %df audio yes, %.1f s, %d B" % (v["w"], v["h"], v["frames"], wall or -1, v["bytes"]))
        log("DONE pos=%d tag=%s ok %dx%d %df audio yes wall=%ss bytes=%d retry=%s"
            % (pos, tag, v["w"], v["h"], v["frames"], ("%.1f" % wall) if wall else "?", v["bytes"], retry))
        return marker
    json.dump({"tag": tag, "pos": pos, "runner_rc": rc, "why": v.get("why") or ("runner rc %d" % rc),
               "verified": v, "at": time.strftime("%Y-%m-%d %H:%M:%S CT")},
              open(os.path.join(job_dir, "render_fail.json"), "w", encoding="utf-8"), indent=1)
    print("  FAIL %s: %s" % (tag, v.get("why") or ("runner rc %d" % rc)))
    log("FAIL pos=%d tag=%s %s" % (pos, tag, v.get("why") or ("runner rc %d" % rc)))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8, help="jobs per call (the queue is resumable)")
    ap.add_argument("--jobs", help="explicit comma-separated tags (ignores the order for those)")
    a = ap.parse_args()
    order = json.load(open(ORDER, encoding="utf-8"))
    jobs = order["order"]
    if a.jobs:
        want = set(a.jobs.split(","))
        jobs = [j for j in jobs if j["tag"] in want]
    comm = load_comm()
    done, todo = [], []
    for j in jobs:
        d = os.path.join(RUNS, j["tag"])
        m = os.path.join(d, "render_ok.json")
        if os.path.exists(m):
            mk = json.load(open(m, encoding="utf-8"))
            v = verify(d, j["tag"])
            if v["ok"] and mk.get("prompt_sha256") == prompt_sha(os.path.join(d, "request.api.json")):
                done.append((j["pos"], j["tag"], "skip (already rendered, clip verifies, prompt matches the "
                                                 "current graph)"))
                continue
            done.append((j["pos"], j["tag"], "marker exists but does not verify - will render"))
        todo.append(j)
    print("order has %d jobs; %d already verified, %d to render; this call takes up to %d"
          % (len(jobs), len(done), len(todo), a.limit))
    for pos, tag, why in done:
        print("  pos %2d %-22s %s" % (pos, tag, why))
    if not todo:
        print("ALL RENDERED - nothing to do")
        return 0
    failed = []
    for j in todo[:a.limit]:
        r = render_one(comm, j["pos"], j)
        if r is None:
            print("  -> the one allowed UNCHANGED retry (same graph, same seed)")
            r = render_one(comm, j["pos"], j, retry=True)
        if r is None:
            failed.append(j["tag"])
            print("  STOP: %s failed twice; per the plan a second failure stops the queue for that arm and Max "
                  "reports. Nothing was changed to make it pass." % j["tag"])
            log("STOP queue: %s failed twice (one unchanged retry used)" % j["tag"])
            break
    rendered = [j["tag"] for j in todo[:a.limit] if os.path.exists(os.path.join(RUNS, j["tag"], "render_ok.json"))]
    total_ok = sum(1 for j in jobs if os.path.exists(os.path.join(RUNS, j["tag"], "render_ok.json")))
    print("\nthis call: %d of %d attempted rendered, %d failed twice, %d jobs left in the queue"
          % (len(rendered), min(a.limit, len(todo)), len(failed), len(todo) - min(a.limit, len(todo))))
    print("queue total: %d/%d clips carry a verified render_ok.json (each one re-verified by ffprobe on a re-run)"
          % (total_ok, len(jobs)))
    if total_ok < len(jobs):
        print("next call: python notes\\terrace_v3_render_queue.py (it resumes at the first job without a marker)")
    return 5 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
