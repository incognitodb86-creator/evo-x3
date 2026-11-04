r"""run_queue.py - THE reusable render-queue template (simplify plan S4 + S8, 2026-10-30).

Renders every clip in a run's order file back to back in ONE GPU window:
  once per batch : pytest gate, take gpu-render.lock (held = rc 7 GPU_BUSY), unload the LLM, wake comfyui_auto
  submit (one at a time) : at most MAX_IN_FLIGHT = 1 clip in ComfyUI at a time (FIX 3, 2026-11-03: was submit all
                   up front; up-front submit risked losing queued jobs when llama-swap swapped/killed ComfyUI).
                   Submits the next clip right after the current one settles (minimal gap between jobs).
                   Guards every prompt string, keep-alive touch, static check, then POST /prompt (comm.submit).
                   ComfyUI renders at most one prompt at a time, protecting the queue if swapped out.
  collect        : every QPOLL_SEC (3 s) one GET /comfyui/queue; a prompt that left the queue is read from /history
                   (comm.fetch) and gets its OBJECTIVE check as it finishes (ffprobe size/frames/audio, black/freeze;
                   PNG + size for stills). The per-job timeout (JOB_TIMEOUT) counts from when ComfyUI starts the job,
                   not from submit. A prompt gone from both queue and history (comfyui_auto restarted) is "evicted"
                   and, like a stall, is looked for on disk first (never re-rendered if its output landed)
  retry          : clips that failed or stalled get exactly one unchanged retry, submitted together as a second
                   wave after the first, then are logged FAIL and skipped (phase 2 S8, 2026-10-30)
  at the end     : unload comfyui_auto and release the lock in `finally` (also on error and Ctrl-C), then log
                   "BATCH closed rc=<n> reason=<why> done=<ok>/<queued>" (phase 2 S13)
A file named STOP in the run dir halts the batch: no more submits or collecting, ComfyUI's pending queue is cleared
(POST /queue {"clear": true}) and the running prompt interrupted (POST /interrupt). Results append to <run>/_render_queue.log
in the same START/DONE format as the per-test queue scripts, so runs stay comparable.
It reuses comm.py (submit/fetch/run) and run_graph_job.py helpers.
job_type "still" (flux Phase 1, Derrick 2026-10-30 2:52 PM CT): an order entry with "job_type": "still" (and its
expected "size": "WxH") is an image job: the same guard, lock, STOP, retry and log lines, but its check is PNG output
+ size only (no frames/audio/black-freeze/contact sheet) and its prompt is read from the Klein edit text node
(CLIPTextEncode titled "positive"). Entries without job_type are H3 video clips, unchanged.

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
QPOLL_SEC = 3        # collect poll inside a batch (lock held, comfyui_auto kept loaded, so a poll is no extra wake)
JOB_TIMEOUT = 3600   # per job, counted from when ComfyUI starts it (was from submit with one job at a time)
EVICT_MISSES = 10    # polls a prompt may be in neither /queue nor /history before it counts as evicted (~30 s)
MAX_IN_FLIGHT = 1    # at most ONE prompt of this batch in ComfyUI at a time (FIX 3a, 2026-11-03)
QUEUE_TIMEOUT_STOPPING = 10  # short /queue timeout (s) after repeated timeouts indicate ComfyUI stopping (FIX 3b)


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


def guard_graph(g, require_adult=True):  # Derek 2026-11-03 6:15 AM CT: require_adult is the default
    """Adults-only gate. Every prompt string must pass comm.guard_ok; with require_adult, at least one must state an adult.
    A malformed graph fails (fail closed). Thin bool wrapper over comm.guard_reason - the reason is what to log."""
    return comm.guard_reason(g, require_adult)[0]


def still_prompt(g):
    """job_type still: the Klein edit prompt = CLIPTextEncode titled 'positive' (else the first CLIPTextEncode)."""
    enc = [n for n in g.values() if n.get("class_type") == "CLIPTextEncode"]
    pos = [n for n in enc if n.get("_meta", {}).get("title") == "positive"] or enc
    return pos[0]["inputs"].get("text", "") if pos else ""


def still_done(run_dir, job, tag, f, g0, size, t0, retry, slog):
    """job_type still: PNG output + size check only, then the same render_ok.json and DONE line shape as a clip."""
    if job.get("size"):
        size = tuple(int(x) for x in str(job["size"]).lower().split("x"))
    p = rgj.probe(f)
    why = [] if p["bytes"] > 0 else ["0-byte file"]
    if not f.lower().endswith(".png"): why.append("not a png (%s)" % os.path.basename(f))
    if (p["w"], p["h"]) != size: why.append("size %sx%s != %dx%d" % (p["w"], p["h"], size[0], size[1]))
    if why:
        qlog(run_dir, "FAIL pos=%d tag=%s objective %s" % (job["pos"], tag, "; ".join(why))); return False
    slog("OBJECTIVE ok %s still png size=%sx%s bytes=%d" % (tag, p["w"], p["h"], p["bytes"]))
    outs = [os.path.join(OUT_ROOT, tag, x) for x in os.listdir(os.path.join(OUT_ROOT, tag))] if os.path.isdir(os.path.join(OUT_ROOT, tag)) else []
    wall = (max(map(os.path.getmtime, outs)) - t0) if outs else None
    prompt = still_prompt(g0)
    json.dump({"tag": tag, "pos": job["pos"], "arm": job.get("arm"), "scene": job.get("scene"), "seed": job.get("seed"),
               "job_type": "still", "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
               "image_sha256": hashlib.sha256(open(f, "rb").read()).hexdigest(), "image": os.path.relpath(f, run_dir),
               "bytes": p["bytes"], "w": p["w"], "h": p["h"], "wall_seconds_output_mtime": round(wall, 1) if wall else None,
               "rendered_at": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": retry, "driver": "run_queue.py"},
              open(os.path.join(run_dir, tag, "render_ok.json"), "w", encoding="utf-8"), indent=1)
    qlog(run_dir, "DONE pos=%d tag=%s ok %dx%d still png wall=%ss bytes=%d retry=%s" % (job["pos"], tag, p["w"], p["h"],
         ("%.1f" % wall) if wall else "?", p["bytes"], retry))
    return True


def prepare(run_dir, job, retry, slog):
    """START line + the per-clip checks before a submit. Returns the graph, or None after logging the FAIL."""
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    graph = os.path.join(d, "request.api.json")
    qlog(run_dir, "START pos=%d tag=%s arm=%s scene=%s seed=%s%s" % (job["pos"], tag, job.get("arm"), job.get("scene"),
         job.get("seed"), " (the one allowed unchanged retry)" if retry else ""))
    if not os.path.exists(graph):
        qlog(run_dir, "FAIL pos=%d tag=%s no graph" % (job["pos"], tag)); return None
    g0 = json.load(open(graph, encoding="utf-8"))
    ok, why = comm.guard_reason(g0)  # adults-only guard before EVERY clip
    if not ok:
        qlog(run_dir, "GATE-FAIL pos=%d tag=%s adults guard: %s" % (job["pos"], tag, why)); return None
    if not rgj.wake(slog):   # keep-alive touch of /comfyui/system_stats (ttl 300) + unload any LLM swapped in
        qlog(run_dir, "FAIL pos=%d tag=%s ComfyUI down" % (job["pos"], tag)); return None
    bad = rgj.static_check(g0)
    if bad:
        qlog(run_dir, "FAIL pos=%d tag=%s static %s" % (job["pos"], tag, " | ".join(bad[:4]))); return None
    return g0


def render_clip(run_dir, job, frames, size, retry, slog):
    """One clip, ONE render attempt, submit and wait (single-job path; the batch uses run_wave)."""
    g0 = prepare(run_dir, job, retry, slog)
    if g0 is None:
        return False
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    t0 = time.time()
    out, t_att = {}, time.time()
    s = comm.run(copy.deepcopy(g0), tag, meta(job, retry), d, logfile=os.path.join(d, "status.log"), timeout=JOB_TIMEOUT, out=out)
    return finish(run_dir, job, frames, size, retry, slog, s, out, g0, t0, t_att)


def meta(job, retry):
    return {"run": job["tag"], "attempt": int(retry), "label": "METHOD_ONLY", "plan": "run_queue"}


def disk_output(run_dir, tag, since):
    """Evict/stall disk fallback for run_queue jobs (fix 2026-10-31, backup run_queue.py.bak-0735). Their SaveImage/SaveVideo
    prefix is community/<run>/<tag>, so ComfyUI writes FLAT files output/community/<run>/<tag>_00001_.png|.mp4;
    rgj.collect_from_disk only looks in output/community/<tag>/ and missed all 9 landed Klein N12 stills (06:59 evict).
    Exact '<tag>_NNNNN_' match (E1 never matches E11), mtime >= submit-5 s; newest wins. None if nothing landed."""
    import glob
    d = os.path.join(OUT_ROOT, os.path.basename(os.path.normpath(run_dir)))
    pat = re.compile(re.escape(tag) + r"_\d{5}_?\.(png|mp4)$", re.I)
    try:
        pats = [
            os.path.join(glob.escape(d), glob.escape(tag) + "_*"),
            os.path.join(glob.escape(d), glob.escape(tag), glob.escape(tag) + "_*"),
        ]
        cands = [p for p_pat in pats for p in glob.glob(p_pat)]
        c = [p for p in cands
             if pat.match(os.path.basename(p)) and os.path.getmtime(p) >= since - 5]
    except OSError:
        return None
    return max(c, key=os.path.getmtime) if c else None


# --- (c) 2026-11-02 (brief 2026-11-02-2010): prompt_ids saved at submit, harvested before any re-submit ---------------
PIDS_FILE = "_prompt_ids.json"


def expected_prefix(g):
    """filename_prefix of the graph's SaveVideo/SaveImage node (where ComfyUI will write the output), else None."""
    for n in (g or {}).values():
        if n.get("class_type") in ("SaveVideo", "SaveImage") and isinstance(n.get("inputs", {}).get("filename_prefix"), str):
            return n["inputs"]["filename_prefix"]
    return None


def load_pids(run_dir):
    p = os.path.join(run_dir, PIDS_FILE)
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_pid(run_dir, tag, pid, prefix, retry):
    """Written right after each POST /prompt, so a driver/Shell death or an eviction never loses the prompt_id."""
    d = load_pids(run_dir)
    d[tag] = {"prompt_id": pid, "tag": tag, "expected_prefix": prefix, "submitted_at": time.time(),
              "submitted_at_ct": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": bool(retry)}
    tmp = os.path.join(run_dir, PIDS_FILE + ".tmp")
    json.dump(d, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, os.path.join(run_dir, PIDS_FILE))


def prefix_output(prefix, since):
    """Disk look-up by the saved expected prefix: output/<prefix>_NNNNN_.ext, flat or one folder down. Newest wins."""
    import glob
    if not prefix:
        return None
    base = os.path.join(comm.C, "output", *prefix.replace("\\", "/").split("/"))
    stem = os.path.basename(base)
    pat = re.compile(re.escape(stem) + r"_\d{5}_?\.(png|mp4)$", re.I)
    pats = [glob.escape(base) + "_*", os.path.join(glob.escape(base), glob.escape(stem) + "_*")]
    try:
        c = [p for pp in pats for p in glob.glob(pp) if pat.match(os.path.basename(p)) and os.path.getmtime(p) >= since - 5]
    except OSError:
        return None
    return max(c, key=os.path.getmtime) if c else None


def harvest(run_dir, jobs, frames, size, slog, queue_ids=None):
    """Before submitting, look for each job's earlier prompt_id: still in ComfyUI's queue -> adopt it (collect, do not
    re-submit); in /history -> collect; gone -> look on disk by the expected prefix. Returns (to_submit, adopted, done)
    where adopted = {prompt_id: entry} for run_wave to keep collecting."""
    rec = load_pids(run_dir)
    if not rec:
        return list(jobs), {}, []
    if queue_ids is None:
        try:
            q = comm.http(comm.BASE + "/queue", timeout=comm.POLL_TIMEOUT)
            queue_ids = {x[1] for x in q.get("queue_running", []) + q.get("queue_pending", [])}
        except Exception as ex:
            slog("harvest warn queue %s" % str(ex)[:120]); queue_ids = set()
    todo, adopted, done = [], {}, []
    for j in jobs:
        r = rec.get(j["tag"])
        if not r or not r.get("prompt_id"):
            todo.append(j); continue
        pid, d = r["prompt_id"], os.path.join(run_dir, j["tag"])
        e = {"job": j, "out": {}, "t_att": r.get("submitted_at", 0), "t0": r.get("submitted_at", 0),
             "log": os.path.join(d, "status.log"), "g0": json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))}
        if pid in queue_ids:
            qlog(run_dir, "HARVEST pos=%d tag=%s prompt_id=%s still in ComfyUI queue - adopted, not re-submitted" % (j["pos"], j["tag"], pid))
            adopted[pid] = e; continue
        s = None
        try:
            s = comm.fetch(pid, j["tag"], meta(j, False), d, e["t0"], e["log"], e["out"])
        except Exception as ex:
            slog("harvest warn history %s %s" % (j["tag"], str(ex)[:120]))
        if s is comm.PENDING or s is None and not e["out"]:
            s = None
            src = prefix_output(r.get("expected_prefix"), e["t_att"]) or disk_output(run_dir, j["tag"], e["t_att"])
            if src:
                comm.outcome(e["out"], "evicted", pid, note="harvested from disk by expected prefix")
        if s or e["out"].get("outcome") == "evicted":
            qlog(run_dir, "HARVEST pos=%d tag=%s prompt_id=%s collected from %s - not re-submitted" % (
                j["pos"], j["tag"], pid, "history" if s else "disk"))
            if settle(run_dir, e, s, frames, size, False, slog):
                done.append(j); continue
        todo.append(j)
    return todo, adopted, done


def finish(run_dir, job, frames, size, retry, slog, s, out, g0, t0, t_att):
    """After a job ends (or stalls/evicts): disk fallback, then the OBJECTIVE check and the DONE line."""
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    t = tag
    if not s and out.get("outcome") in ("stalled", "evicted", "submit_stall"):
        src = prefix_output(expected_prefix(g0), t_att) or disk_output(run_dir, t, t_att) or rgj.collect_from_disk(t, t_att, slog)
        if not src:
            qlog(run_dir, "FAIL pos=%d tag=%s stall %s prompt_id=%s" % (job["pos"], tag, out["outcome"], out.get("prompt_id"))); return False
        dst = os.path.join(d, t + os.path.splitext(src)[1])
        try:
            if os.path.exists(dst): os.remove(dst)
            os.link(src, dst)
        except OSError:
            shutil.copyfile(src, dst)
        s = {"file": dst}
    if not s:
        qlog(run_dir, "FAIL pos=%d tag=%s job error (%s)" % (job["pos"], tag, out.get("outcome"))); return False
    if job.get("job_type") == "still":
        return still_done(run_dir, job, tag, s["file"], g0, size, t0, retry, slog)
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


def stop_seen(run_dir):
    return os.path.exists(os.path.join(run_dir, "STOP"))


def stop_comfy(run_dir, slog, n_open):
    """STOP: drop everything still queued in ComfyUI and interrupt the running prompt."""
    for path, body in (("/queue", {"clear": True}), ("/interrupt", {})):
        try: comm.http(comm.BASE + path, body, timeout=60); slog("STOP POST %s ok" % path)
        except Exception as e: slog("STOP POST %s note %s" % (path, str(e)[:120]))
    qlog(run_dir, "STOP file seen: stopped collecting with %d submitted clip(s) unfinished; ComfyUI queue cleared and running prompt interrupted" % n_open)


def settle(run_dir, e, s, frames, size, retry, slog):
    """finish() for one submitted job; an error is a failed attempt, as in attempt()."""
    try:
        return finish(run_dir, e["job"], frames, size, retry, slog, s, e["out"], e["g0"], e.get("started", e["t0"]), e["t_att"])
    except Exception as ex:
        qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (e["job"]["pos"], e["job"]["tag"], type(ex).__name__, str(ex)[:160].replace("\n", " ")))
        return False


def run_wave(run_dir, jobs, frames, size, retry, slog, adopt=None):
    """Submit clips to ComfyUI one at a time (MAX_IN_FLIGHT = 1), then collect each as it finishes.
    adopt = {prompt_id: entry} from harvest(): jobs already in ComfyUI's queue, collected without a re-submit.
    Returns (failed jobs, stopped)."""
    failed, live = [], dict(adopt or {})
    pending = list(jobs)
    queue_timeouts = 0
    stopping = False
    while pending or live:
        if stop_seen(run_dir):
            if pending:
                qlog(run_dir, "STOP file seen: halted before submitting pos=%d tag=%s" % (pending[0]["pos"], pending[0]["tag"]))
            stop_comfy(run_dir, slog, len(live)); return failed, True
        while len(live) < MAX_IN_FLIGHT and pending:
            j = pending.pop(0)
            if stop_seen(run_dir):
                qlog(run_dir, "STOP file seen: halted before submitting pos=%d tag=%s" % (j["pos"], j["tag"]))
                stop_comfy(run_dir, slog, len(live)); return failed, True
            d = os.path.join(run_dir, j["tag"])
            e = {"job": j, "out": {}, "t_att": time.time(), "log": os.path.join(d, "status.log")}
            try:
                e["g0"] = prepare(run_dir, j, retry, slog)
                if e["g0"] is None:
                    failed.append(j); continue
                e["t0"] = time.time()
                pid = comm.submit(copy.deepcopy(e["g0"]), j["tag"], meta(j, retry), d, logfile=e["log"], out=e["out"])
            except Exception as ex:
                qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (j["pos"], j["tag"], type(ex).__name__, str(ex)[:160].replace("\n", " ")))
                failed.append(j); continue
            if pid is None:  # guard hit, POST rejected or submit stall: settled now, exactly as the one-job path does
                if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(j)
                continue
            try: save_pid(run_dir, j["tag"], pid, expected_prefix(e["g0"]), retry)
            except Exception as ex: slog("prompt_ids note %s" % str(ex)[:120])
            live[pid] = e
            slog("QUEUE submitted pos=%d tag=%s prompt_id=%s (in-flight %d/%d)" % (j["pos"], j["tag"], pid, len(live), MAX_IN_FLIGHT))
        if not live:
            break
        time.sleep(QPOLL_SEC)
        q_timeout = QUEUE_TIMEOUT_STOPPING if stopping else comm.POLL_TIMEOUT
        try:
            q = comm.http(comm.BASE + "/queue", timeout=q_timeout)
            queue_timeouts = 0
            if stopping:
                stopping = False
                slog("comfyui_auto answered /queue; stopping state cleared")
            running = {x[1] for x in q.get("queue_running", [])}
            pending_ids = {x[1] for x in q.get("queue_pending", [])}
        except Exception as ex:
            queue_timeouts += 1
            slog("poll warn queue %s" % str(ex)[:160])
            if queue_timeouts >= 2 or comm.comfy_stopping():
                if not stopping:
                    stopping = True
                    slog("comfyui_auto looks like it is being stopped (%d /queue timeouts)" % queue_timeouts)
                # While comfyui_auto is stopping, ComfyUI may finish rendering or output already landed
                for pid, e in list(live.items()):
                    src = prefix_output(expected_prefix(e["g0"]), e["t_att"]) or disk_output(run_dir, e["job"]["tag"], e["t_att"]) or rgj.collect_from_disk(e["job"]["tag"], e["t_att"], slog)
                    if src:
                        slog("DISCOVERY pos=%d tag=%s prompt_id=%s found output on disk during /queue timeout" % (e["job"]["pos"], e["job"]["tag"], pid))
                        comm.outcome(e["out"], "evicted", pid, note="found output on disk during comfyui stop/stall")
                        if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                        del live[pid]
            if comm.comfy_loaded() is False:  # same rule as comm.run: the history went with the process
                for pid, e in list(live.items()):
                    comm.log(f"poll stop {e['job']['tag']} comfyui_auto is not running: prompt_id {pid} is in no live history", e["log"])
                    comm.outcome(e["out"], "evicted", pid, note="history lost with the comfyui_auto process")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
            continue
        now = time.time()
        for pid, e in list(live.items()):
            tag = e["job"]["tag"]
            if pid in running:
                if "started" not in e:
                    e["started"] = now; comm.log(f"JOB running {tag} prompt_id={pid} queued={now - e['t0']:.0f}s", e["log"])
                elif now - e["started"] > JOB_TIMEOUT:
                    comm.log(f"JOB timeout {tag}", e["log"])
                    try:
                        comm.http(comm.BASE + "/interrupt", data={}, timeout=10, method="POST")
                        comm.http(comm.BASE + "/queue", data={"delete": [pid]}, timeout=10, method="POST")
                        comm.log(f"JOB cancelled via /interrupt and /queue delete {tag} prompt_id={pid}", e["log"])
                    except Exception as ex_cancel:
                        comm.log(f"JOB cancel error {tag}: {ex_cancel}", e["log"])
                    comm.outcome(e["out"], "stalled", pid, note=f"no history {JOB_TIMEOUT}s after ComfyUI started it; cancelled via /interrupt; the render may have landed in ComfyUI output")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
                continue
            if pid in pending_ids:
                if now - e["t0"] > 900:
                    comm.log(f"JOB pending timeout {tag} (>15m unstarted)", e["log"])
                    try:
                        comm.http(comm.BASE + "/interrupt", data={}, timeout=10, method="POST")
                        comm.http(comm.BASE + "/queue", data={"delete": [pid]}, timeout=10, method="POST")
                        comm.log(f"JOB cancelled via /interrupt and /queue delete {tag} prompt_id={pid}", e["log"])
                    except Exception as ex_cancel:
                        comm.log(f"JOB cancel error {tag}: {ex_cancel}", e["log"])
                    comm.outcome(e["out"], "stalled", pid, note="no progress for >15m in queue; cancelled via /interrupt")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
                continue
            try:
                s = comm.fetch(pid, tag, meta(e["job"], retry), os.path.join(run_dir, tag), e.get("started", e["t0"]), e["log"], e["out"])
            except Exception as ex:
                comm.log(f"poll warn {tag} {ex}", e["log"]); continue
            if s is comm.PENDING:
                e["miss"] = e.get("miss", 0) + 1
                if e["miss"] < EVICT_MISSES:
                    continue
                comm.log(f"poll stop {tag} prompt_id {pid} is in neither /queue nor /history (comfyui_auto restarted?)", e["log"])
                comm.outcome(e["out"], "evicted", pid, note="history lost with the comfyui_auto process")
                s = None
            if not settle(run_dir, e, s, frames, size, retry, slog): failed.append(e["job"])
            del live[pid]
    return failed, False


def main():
    ap = argparse.ArgumentParser(description="reusable batch render queue (one GPU window per batch)")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--queue", help="order file (default <run-dir>/_render_order.json): {'order': [{pos, tag, arm, scene, seed[, job_type, size]}]}")
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
        print("prompt_ids on file: %d (%s)" % (len(load_pids(run_dir)), PIDS_FILE))
        print("dry run: no lock, GPU or HTTP call made")
        return 0
    if not todo:
        return 0
    slog = lambda m: comm.log(m, os.path.join(run_dir, "status.log"))
    r = subprocess.run([PY, "-m", "pytest", *PYTEST_FILES, "-q", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        qlog(run_dir, "GATE-FAIL batch pytest rc=%d" % r.returncode)
        qlog(run_dir, "BATCH closed rc=2 reason=pytest gate failed (pytest rc=%d) done=%d/%d: nothing queued" % (r.returncode, ok_count(run_dir, jobs), len(jobs)))
        return 2
    # #18: the lock alone decides (a live PID in gpu-render.lock = GPU_BUSY rc 7); gpu_guard pre-check dropped 2026-10-30
    # gpu_lock.ps1 -Acquire: exit 0 = acquired, exit 1 = HELD by a live PID (busy); anything else = the lock tool failed
    lrc, lout = rgj.ps_run(rgj.GPU_LOCK_PS, "-Acquire", "-Owner", str(os.getpid()), "-Note", "run_queue " + os.path.basename(run_dir))
    slog("gpu_lock acquire rc=%d %s" % (lrc, lout[:140]))
    if lrc == 1:
        qlog(run_dir, "GPU_BUSY batch: gpu-render.lock held by a live PID - nothing queued (rc 7)")
        qlog(run_dir, "BATCH closed rc=7 reason=GPU busy (gpu-render.lock held by a live PID) done=%d/%d: nothing queued" % (ok_count(run_dir, jobs), len(jobs)))
        return 7
    if lrc != 0:
        qlog(run_dir, "ERROR batch lock tool error: gpu_lock.ps1 rc=%d %s" % (lrc, lout[:140]))
        qlog(run_dir, "BATCH closed rc=8 reason=lock tool error (gpu_lock.ps1 rc=%d) done=%d/%d: nothing queued" % (lrc, ok_count(run_dir, jobs), len(jobs)))
        return 8
    rc, reason, failed = 0, "all queued clips DONE ok", []
    try:
        if not rgj.wake(slog):  # unload the LLM once, wake ComfyUI once
            rc, reason = 4, "ComfyUI down at batch start"
            qlog(run_dir, "FAIL batch ComfyUI down"); return rc
        qlog(run_dir, "BATCH open: %d clips, lock held, comfyui_auto kept loaded" % len(todo))
        adopted = {}
        if a.resume or stale:  # (c) a resumed or killed batch: collect earlier prompt_ids before any re-submit
            todo, adopted, _h = harvest(run_dir, todo, a.frames, size, slog)
        first, stopped = run_wave(run_dir, todo, a.frames, size, False, slog, adopt=adopted)
        if first and not stopped:
            again, stopped = run_wave(run_dir, first, a.frames, size, True, slog)
            for j in again:
                qlog(run_dir, "FAIL pos=%d tag=%s failed twice (one unchanged retry used) - skipped" % (j["pos"], j["tag"]))
                failed.append(j["tag"])
        if stopped:
            rc, reason = 1, "STOP file"
        if failed and rc == 0:
            rc, reason = 5, "%d clip(s) failed twice: %s" % (len(failed), " ".join(failed))
    except KeyboardInterrupt:
        qlog(run_dir, "INTERRUPTED (Ctrl-C)"); rc, reason = 130, "Ctrl-C"
    except BaseException as e:  # S13: the 11:19 batch died here on a TimeoutError and still logged rc=0
        rc, reason = 8, "error %s: %s" % (type(e).__name__, str(e)[:160].replace("\n", " "))
        qlog(run_dir, "ERROR batch %s" % reason)
    finally:
        comm.mark_collected()  # (c) graceful-stop may stop comfyui_auto now: every output this batch will collect is in
        try: comm.free_comfy(slog)
        except Exception as e: slog("free_comfy note %s" % str(e)[:120])
        try: rgj.post(comm.LS + "/api/models/unload/comfyui_auto", 300); slog("UNLOAD comfyui_auto")
        except Exception as e: slog("unload note %s" % str(e)[:120])
        try: rgj.gpu_unlock(slog)
        except Exception as e: slog("unlock note %s" % str(e)[:120])
        try: n_ok = ok_count(run_dir, jobs)
        except Exception as e:
            n_ok = 0; slog("ok_count note %s" % str(e)[:120])
        if rc == 0 and n_ok < len(jobs):  # never rc=0 while a queued clip lacks a DONE ok line
            rc, reason = 6, "ended with %d queued clip(s) missing a DONE ok line" % (len(jobs) - n_ok)
        qlog(run_dir, "BATCH closed rc=%d reason=%s done=%d/%d: comfyui_auto unloaded, lock released" % (rc, reason, n_ok, len(jobs)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
