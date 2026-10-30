r"""run_queue.py - THE reusable render-queue template (simplify plan S4 + S8, 2026-10-30).

Renders every clip in a run's order file back to back in ONE GPU window:
  once per batch : pytest gate, take gpu-render.lock (held = rc 7 GPU_BUSY), unload the LLM, wake comfyui_auto
  every clip     : comm.guard_ok on every prompt string, wake/keep-alive touch (/comfyui/system_stats, also unloads
                   any LLM that got swapped in), static check, ONE render attempt, OBJECTIVE check
                   (ffprobe size/frames/audio, black/freeze); a failed or stalled clip gets exactly one unchanged
                   retry, then is logged FAIL and skipped (phase 2 S8, 2026-10-30: was up to 6 renders per clip)
  at the end     : unload comfyui_auto and release the lock in `finally` (also on error and Ctrl-C), then log
                   "BATCH closed rc=<n> reason=<why> done=<ok>/<queued>" (phase 2 S13)
A file named STOP in the run dir halts the batch after the clip in flight. Results append to <run>/_render_queue.log
in the same START/DONE format as the per-test queue scripts, so runs stay comparable.
It reuses comm.py and run_graph_job.py helpers; it does not change them.

Usage:
  python scripts\run_queue.py --run-dir <run dir> [--queue <run dir>\_render_order.json] [--resume] [--dry-run]
        [--frames 124] [--size 768x1344] [--detach]
--resume skips tags with a "DONE ... ok" line in _render_queue.log. --dry-run lists what would render and makes no
lock, GPU or HTTP call.
--detach (phase 2 S11): relaunch this same command through WMI (Win32_Process.Create), so the batch runs outside the
caller's process tree and job object and survives the pi/herdr pane closing; prints the batch PID and returns at once.
Output goes to <run dir>\_run_queue.out.log. Forge launch line (then end the turn; no waits or checks):
  C:\AI\director\.venv\Scripts\python.exe C:\AI\community\scripts\run_queue.py --run-dir <run dir> [--resume] --detach
Exit (also logged as BATCH closed rc=<n> reason=<why>): 0 every queued clip has a DONE ok line, 1 STOP file,
2 pytest gate failed, 4 ComfyUI down, 5 a clip failed twice (others still rendered), 6 batch ended with clips
missing a DONE ok line, 7 GPU busy (lock held), 8 uncaught error (reason names it), 9 a previous batch opened and
never closed (killed/unknown; reported at the next start), 130 Ctrl-C. A kill cannot log itself: the next start
reports it.
"""
import argparse, copy, hashlib, json, os, re, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comm
import run_graph_job as rgj

ROOT = r"C:\AI\community"
PY = sys.executable
PYTEST_FILES = [os.path.join("scripts", "tests", "test_p6_review.py"), os.path.join("scripts", "tests", "test_guard_scope.py")]
ACTIONS = os.path.join(ROOT, "notes", "actions.log")
OUT_ROOT = os.path.join(comm.C, "output", "community")


def qlog(run_dir, line):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S-05:00")
    print(ts, line, flush=True)
    with open(os.path.join(run_dir, "_render_queue.log"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (ts, line))
    with open(ACTIONS, "a", encoding="utf-8") as f:
        f.write("%s run_queue %s: %s\n" % (ts, os.path.basename(run_dir), line))


def done_tags(run_dir):
    p = os.path.join(run_dir, "_render_queue.log")
    if not os.path.exists(p):
        return set()
    return set(re.findall(r" DONE pos=\d+ tag=(\S+) ok ", open(p, encoding="utf-8").read()))


def ok_count(run_dir, jobs):
    d = done_tags(run_dir)
    return sum(1 for j in jobs if j["tag"] in d)


def unclosed_batch(run_dir):
    """S13: the last 'BATCH open' line with no 'BATCH closed' after it = a batch that was killed (a kill can't log)."""
    p = os.path.join(run_dir, "_render_queue.log")
    if not os.path.exists(p):
        return None
    last_open = None
    for line in open(p, encoding="utf-8"):
        if " BATCH open" in line:
            last_open = line.split(" ", 1)[0]
        elif " BATCH closed" in line:
            last_open = None
    return last_open


def detach(argv, run_dir):
    """S11: start this command again via WMI so its parent is WmiPrvSE, not the caller (pane) process tree."""
    args = [a for a in argv if a != "--detach"]
    out = os.path.join(run_dir, "_run_queue.out.log")
    cmd = 'cmd.exe /c ""%s" "%s" %s > "%s" 2>&1"' % (PY, os.path.abspath(__file__), " ".join('"%s"' % a for a in args), out)
    ps = ("$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$env:RQ_CMD; "
          "CurrentDirectory='%s'}; \"$($r.ReturnValue) $($r.ProcessId)\"" % ROOT)
    r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True,
                       env=dict(os.environ, RQ_CMD=cmd), timeout=120)
    parts = (r.stdout or "").split()
    if r.returncode or len(parts) < 2 or parts[0] != "0":
        print("detach FAILED rc=%s %s %s" % (r.returncode, r.stdout.strip(), r.stderr.strip()[:300])); return 8
    print("detached batch: cmd.exe PID %s (outside this process tree); output %s; log %s" % (
        parts[1], out, os.path.join(run_dir, "_render_queue.log")))
    return 0


def guard_graph(g):
    return all(comm.guard_ok(s) for n in g.values() for s in comm.prompt_strings(n.get("inputs", {})))


def render_clip(run_dir, job, frames, size, retry, slog):
    """One clip, ONE render attempt inside the open GPU window (S8: the caller gives exactly one unchanged retry)."""
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    graph = os.path.join(d, "request.api.json")
    qlog(run_dir, "START pos=%d tag=%s arm=%s scene=%s seed=%s%s" % (job["pos"], tag, job.get("arm"), job.get("scene"),
         job.get("seed"), " (the one allowed unchanged retry)" if retry else ""))
    if not os.path.exists(graph):
        qlog(run_dir, "FAIL pos=%d tag=%s no graph" % (job["pos"], tag)); return False
    g0 = json.load(open(graph, encoding="utf-8"))
    if not guard_graph(g0):  # adults-only guard before EVERY clip
        qlog(run_dir, "GATE-FAIL pos=%d tag=%s adults guard" % (job["pos"], tag)); return False
    if not rgj.wake(slog):   # keep-alive touch of /comfyui/system_stats (ttl 300) + unload any LLM swapped in
        qlog(run_dir, "FAIL pos=%d tag=%s ComfyUI down" % (job["pos"], tag)); return False
    bad = rgj.static_check(g0)
    if bad:
        qlog(run_dir, "FAIL pos=%d tag=%s static %s" % (job["pos"], tag, " | ".join(bad[:4]))); return False
    t0 = time.time()
    t = tag  # same graph, same seed, same tag: the retry is unchanged
    out, t_att = {}, time.time()
    s = comm.run(copy.deepcopy(g0), t, {"run": tag, "attempt": int(retry), "label": "METHOD_ONLY", "plan": "run_queue"}, d,
                 logfile=os.path.join(d, "status.log"), timeout=3600, out=out)
    if not s and out.get("outcome") in ("stalled", "evicted", "submit_stall"):
        src = rgj.collect_from_disk(t, t_att, slog)
        if not src:
            qlog(run_dir, "FAIL pos=%d tag=%s stall %s prompt_id=%s" % (job["pos"], tag, out["outcome"], out.get("prompt_id"))); return False
        dst = os.path.join(d, t + os.path.splitext(src)[1]); shutil.copyfile(src, dst); s = {"file": dst}
    if not s:
        qlog(run_dir, "FAIL pos=%d tag=%s job error (%s)" % (job["pos"], tag, out.get("outcome"))); return False
    p, bf = rgj.probe(s["file"]), rgj.blackfreeze(s["file"])
    why = [] if p["bytes"] > 0 else ["0-byte file"]
    if (p["w"], p["h"]) != size: why.append("size %sx%s" % (p["w"], p["h"]))
    if p["frames"] != frames: why.append("frames %d != %d" % (p["frames"], frames))
    if not p["audio"]: why.append("no audio stream")
    why += ["detect " + x for x in bf]
    if why:
        qlog(run_dir, "FAIL pos=%d tag=%s objective %s" % (job["pos"], tag, "; ".join(why))); return False
    slog("OBJECTIVE ok %s frames=%d size=%sx%s audio=True bytes=%d" % (t, p["frames"], p["w"], p["h"], p["bytes"]))
    rgj.contact_sheet(s["file"], os.path.join(d, tag + "_stills_contact.png"), p["duration"])
    outs = [os.path.join(OUT_ROOT, t, f) for f in os.listdir(os.path.join(OUT_ROOT, t))] if os.path.isdir(os.path.join(OUT_ROOT, t)) else []
    wall = (max(map(os.path.getmtime, outs)) - t0) if outs else None
    prompt = next((n["inputs"].get("prompt", "") for n in g0.values() if n.get("class_type") == "MiniMaxH3ReferenceToVideo"), "")
    json.dump({"tag": tag, "pos": job["pos"], "arm": job.get("arm"), "scene": job.get("scene"), "seed": job.get("seed"),
               "frames": frames, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
               "clip_sha256": hashlib.sha256(open(s["file"], "rb").read()).hexdigest(), "clip": os.path.relpath(s["file"], run_dir),
               "bytes": p["bytes"], "w": p["w"], "h": p["h"], "audio": True, "wall_seconds_output_mtime": round(wall, 1) if wall else None,
               "rendered_at": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": retry, "driver": "run_queue.py"},
              open(os.path.join(d, "render_ok.json"), "w", encoding="utf-8"), indent=1)
    qlog(run_dir, "DONE pos=%d tag=%s ok %dx%d %df audio yes wall=%ss bytes=%d retry=%s" % (job["pos"], tag, p["w"], p["h"],
         p["frames"], ("%.1f" % wall) if wall else "?", p["bytes"], retry))
    return True


def attempt(run_dir, job, frames, size, retry, slog):
    """One attempt; an error inside it (e.g. the 11:19 keep-alive TimeoutError) is a failed attempt, not a silent batch death."""
    try:
        return render_clip(run_dir, job, frames, size, retry, slog)
    except Exception as e:
        qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (job["pos"], job["tag"], type(e).__name__, str(e)[:160].replace("\n", " ")))
        return False


def main():
    ap = argparse.ArgumentParser(description="reusable batch render queue (one GPU window per batch)")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--queue", help="order file (default <run-dir>/_render_order.json): {'order': [{pos, tag, arm, scene, seed}]}")
    ap.add_argument("--resume", action="store_true", help="skip tags already DONE ok in _render_queue.log")
    ap.add_argument("--dry-run", action="store_true", help="list the clips; no lock, GPU or HTTP call")
    ap.add_argument("--frames", type=int, default=124)
    ap.add_argument("--size", default="768x1344")
    ap.add_argument("--detach", action="store_true", help="relaunch outside the caller's process tree (WMI) and return")
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    if a.detach:
        return detach(sys.argv[1:], run_dir)
    q = json.load(open(a.queue or os.path.join(run_dir, "_render_order.json"), encoding="utf-8"))
    jobs = q["order"] if isinstance(q, dict) else q
    done = done_tags(run_dir) if a.resume else set()
    todo = [j for j in jobs if j["tag"] not in done]
    size = tuple(int(x) for x in a.size.lower().split("x"))
    print("queue %d clips, %d already DONE ok, %d to render" % (len(jobs), len(jobs) - len(todo), len(todo)))
    stale = unclosed_batch(run_dir)
    if stale:
        msg = "BATCH closed rc=9 reason=killed/unknown (batch opened %s never logged a close; found at the next start) done=%d/%d" % (
            stale, ok_count(run_dir, jobs), len(jobs))
        if a.dry_run: print("would log: " + msg)
        else: qlog(run_dir, msg)
    if a.dry_run:
        for j in todo:
            print("  pos %2d %s" % (j["pos"], j["tag"]))
        print("dry run: no lock, GPU or HTTP call made")
        return 0
    if not todo:
        return 0
    slog = lambda m: comm.log(m, os.path.join(run_dir, "status.log"))
    r = subprocess.run([PY, "-m", "pytest", *PYTEST_FILES, "-q", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        qlog(run_dir, "GATE-FAIL batch pytest rc=%d" % r.returncode); return 2
    # #18: the lock alone decides (a live PID in gpu-render.lock = GPU_BUSY rc 7); gpu_guard pre-check dropped 2026-10-30
    if not rgj.gpu_lock(slog, "run_queue " + os.path.basename(run_dir)):
        qlog(run_dir, "GPU_BUSY batch: gpu-render.lock held by a live PID - nothing queued (rc 7)"); return 7
    rc, reason, failed = 0, "all queued clips DONE ok", []
    try:
        if not rgj.wake(slog):  # unload the LLM once, wake ComfyUI once
            rc, reason = 4, "ComfyUI down at batch start"
            qlog(run_dir, "FAIL batch ComfyUI down"); return rc
        qlog(run_dir, "BATCH open: %d clips, lock held, comfyui_auto kept loaded" % len(todo))
        for j in todo:
            if os.path.exists(os.path.join(run_dir, "STOP")):
                qlog(run_dir, "STOP file seen: halted before pos=%d tag=%s" % (j["pos"], j["tag"]))
                rc, reason = 1, "STOP file before pos=%d" % j["pos"]; break
            if not attempt(run_dir, j, a.frames, size, False, slog) and not attempt(run_dir, j, a.frames, size, True, slog):
                qlog(run_dir, "FAIL pos=%d tag=%s failed twice (one unchanged retry used) - skipped" % (j["pos"], j["tag"]))
                failed.append(j["tag"])
        if failed and rc == 0:
            rc, reason = 5, "%d clip(s) failed twice: %s" % (len(failed), " ".join(failed))
    except KeyboardInterrupt:
        qlog(run_dir, "INTERRUPTED (Ctrl-C)"); rc, reason = 130, "Ctrl-C"
    except BaseException as e:  # S13: the 11:19 batch died here on a TimeoutError and still logged rc=0
        rc, reason = 8, "error %s: %s" % (type(e).__name__, str(e)[:160].replace("\n", " "))
        qlog(run_dir, "ERROR batch %s" % reason)
    finally:
        try: rgj.post(comm.LS + "/api/models/unload/comfyui_auto", 300); slog("UNLOAD comfyui_auto")
        except Exception as e: slog("unload note %s" % str(e)[:120])
        rgj.gpu_unlock(slog)
        n_ok = ok_count(run_dir, jobs)
        if rc == 0 and n_ok < len(jobs):  # never rc=0 while a queued clip lacks a DONE ok line
            rc, reason = 6, "ended with %d queued clip(s) missing a DONE ok line" % (len(jobs) - n_ok)
        qlog(run_dir, "BATCH closed rc=%d reason=%s done=%d/%d: comfyui_auto unloaded, lock released" % (rc, reason, n_ok, len(jobs)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
