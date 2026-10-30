r"""run_queue.py - THE reusable render-queue template (simplify plan S4 + S8, 2026-10-30).

Renders every clip in a run's order file back to back in ONE GPU window:
  once per batch : pytest gate, gpu_guard IDLE, take gpu-render.lock, unload the LLM, wake comfyui_auto
  every clip     : comm.guard_ok on every prompt string, wake/keep-alive touch (/comfyui/system_stats, also unloads
                   any LLM that got swapped in), static check, render with run_graph_job's redo rule, OBJECTIVE check
                   (ffprobe size/frames/audio, black/freeze), one unchanged whole-clip retry, second failure stops
  at the end     : unload comfyui_auto and release the lock in `finally` (also on error and Ctrl-C)
A file named STOP in the run dir halts the batch after the clip in flight. Results append to <run>/_render_queue.log
in the same START/DONE format as the per-test queue scripts, so runs stay comparable.
It reuses comm.py and run_graph_job.py helpers; it does not change them.

Usage:
  python scripts\run_queue.py --run-dir <run dir> [--queue <run dir>\_render_order.json] [--resume] [--dry-run]
        [--frames 124] [--size 768x1344]
--resume skips tags with a "DONE ... ok" line in _render_queue.log. --dry-run lists what would render and makes no
lock, GPU or HTTP call. Exit: 0 all done, 1 stopped by STOP file, 5 a clip failed twice, 7 GPU busy, 4 ComfyUI down.
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


def guard_graph(g):
    return all(comm.guard_ok(s) for n in g.values() for s in comm.prompt_strings(n.get("inputs", {})))


def render_clip(run_dir, job, frames, size, retry, slog):
    """One clip inside the open GPU window: run_graph_job's per-attempt loop, minus its lock/wake/unload."""
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
    seeds = [k for k, n in g0.items() if n["class_type"] == "RandomNoise"]
    t0 = time.time()
    for att in range(3):  # run_graph_job redo rule: objective failures only, redo 1 same seed, redo 2 seed+1
        g, t = copy.deepcopy(g0), (tag if att == 0 else "%s_redo%d" % (tag, att))
        if att == 2:
            for k in seeds: g[k]["inputs"]["noise_seed"] = int(g[k]["inputs"]["noise_seed"]) + 1
        if att: slog("REDO %d/2 %s" % (att, tag))
        out, t_att = {}, time.time()
        s = comm.run(g, t, {"run": tag, "attempt": att, "label": "METHOD_ONLY", "plan": "run_queue"}, d,
                     logfile=os.path.join(d, "status.log"), timeout=3600, out=out)
        if not s and out.get("outcome") in ("stalled", "evicted", "submit_stall"):
            src = rgj.collect_from_disk(t, t_att, slog)
            if not src:  # a stall is never re-queued (RENDER-TIMEOUT rule)
                qlog(run_dir, "FAIL pos=%d tag=%s stall %s prompt_id=%s" % (job["pos"], tag, out["outcome"], out.get("prompt_id"))); return False
            dst = os.path.join(d, t + os.path.splitext(src)[1]); shutil.copyfile(src, dst); s = {"file": dst}
        if not s:
            slog("OBJECTIVE FAIL %s JOB error" % t); continue
        p, bf = rgj.probe(s["file"]), rgj.blackfreeze(s["file"])
        why = [] if p["bytes"] > 0 else ["0-byte file"]
        if (p["w"], p["h"]) != size: why.append("size %sx%s" % (p["w"], p["h"]))
        if p["frames"] != frames: why.append("frames %d != %d" % (p["frames"], frames))
        if not p["audio"]: why.append("no audio stream")
        why += ["detect " + x for x in bf]
        if why:
            slog("OBJECTIVE FAIL %s %s" % (t, "; ".join(why))); continue
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
    qlog(run_dir, "FAIL pos=%d tag=%s objective failure after 2 redos" % (job["pos"], tag))
    return False


def main():
    ap = argparse.ArgumentParser(description="reusable batch render queue (one GPU window per batch)")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--queue", help="order file (default <run-dir>/_render_order.json): {'order': [{pos, tag, arm, scene, seed}]}")
    ap.add_argument("--resume", action="store_true", help="skip tags already DONE ok in _render_queue.log")
    ap.add_argument("--dry-run", action="store_true", help="list the clips; no lock, GPU or HTTP call")
    ap.add_argument("--frames", type=int, default=124)
    ap.add_argument("--size", default="768x1344")
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    q = json.load(open(a.queue or os.path.join(run_dir, "_render_order.json"), encoding="utf-8"))
    jobs = q["order"] if isinstance(q, dict) else q
    done = done_tags(run_dir) if a.resume else set()
    todo = [j for j in jobs if j["tag"] not in done]
    size = tuple(int(x) for x in a.size.lower().split("x"))
    print("queue %d clips, %d already DONE ok, %d to render" % (len(jobs), len(jobs) - len(todo), len(todo)))
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
    if not rgj.gpu_idle(slog) or not rgj.gpu_lock(slog, "run_queue " + os.path.basename(run_dir)):
        qlog(run_dir, "GATE-FAIL batch gpu not idle or lock held"); return 7
    rc = 0
    try:
        if not rgj.wake(slog):  # unload the LLM once, wake ComfyUI once
            qlog(run_dir, "FAIL batch ComfyUI down"); rc = 4; return rc
        qlog(run_dir, "BATCH open: %d clips, lock held, comfyui_auto kept loaded" % len(todo))
        for j in todo:
            if os.path.exists(os.path.join(run_dir, "STOP")):
                qlog(run_dir, "STOP file seen: halted before pos=%d tag=%s" % (j["pos"], j["tag"])); rc = 1; break
            if not render_clip(run_dir, j, a.frames, size, False, slog) and not render_clip(run_dir, j, a.frames, size, True, slog):
                qlog(run_dir, "STOP queue: %s failed twice (one unchanged retry used)" % j["tag"]); rc = 5; break
    except KeyboardInterrupt:
        qlog(run_dir, "INTERRUPTED (Ctrl-C)"); rc = 130
    finally:
        try: rgj.post(comm.LS + "/api/models/unload/comfyui_auto", 300); slog("UNLOAD comfyui_auto")
        except Exception as e: slog("unload note %s" % str(e)[:120])
        rgj.gpu_unlock(slog)
        qlog(run_dir, "BATCH closed rc=%d: comfyui_auto unloaded, lock released" % rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
