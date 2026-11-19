"""EVO-X3 remote mode for run_queue.py (consolidation plan P1b, Max Architect 2026-11-16).

AlienPc keeps ComfyUI; the X3 queues over the tailnet through AlienPc's Tailscale Serve :8446
(-> llama-swap 127.0.0.1:8080/upstream/comfyui_auto). enable() rebinds the Windows-only pieces of
comm.py / run_graph_job.py / run_queue.py, so run_queue's batch logic (guards, waves, retry, STOP,
timeouts, /interrupt + /queue delete, DONE/FAILED lines) is reused unchanged:
  comm.BASE / rgj.COMFY      -> COMFY_API (default https://alienpc.tailf242b2.ts.net:8446)
  comm.submit                -> uploads every LoadImage/LoadAudio/LoadVideo input first (POST /upload/image,
                                subfolder kept, overwrite=true); a missing local input fails the clip, nothing posted
  comm.fetch                 -> /history then GET /view?type=output into <run>/<tag>/ (no hard-link to ComfyUI\\output)
  comm.running               -> {"error": ...}: llama-swap admin routes are not exposed through :8446, so
                                comfy_loaded() is None (unknown) and the JOB/pending timeouts decide stalls
  free_comfy / mark_collected / LLM unload -> no-op: AlienPc llama-swap TTL + comfy_graceful_stop.ps1 own the process
  gpu_lock.ps1               -> ~/AI/locks/gpu-render.lock (fcntl flock + PID line; single submitter on the X3)
  detach (WMI)               -> systemd-run --user --unit render-batch-<run>
  RTX upscale post-pass      -> deferred (decision D5: AlienPc ComfyUI step, not wired yet); logged, rc unaffected
No secrets: :8446 has no key (scoped by the Tailscale grant), so nothing is read or sent.
"""
import email.utils, json, mimetypes, os, re, shlex, subprocess, sys, time, urllib.parse, urllib.request, uuid
try:
    import fcntl
except ImportError:
    fcntl = None  # Windows host testing; lock_acquire uses msvcrt when fcntl is unavailable
    import msvcrt

API = os.environ.get("COMFY_API", "https://alienpc.tailf242b2.ts.net:8446").rstrip("/")
HOME = os.path.expanduser("~")
LOCK = os.path.join(HOME, "AI", "locks", "gpu-render.lock")
INPUT_ROOTS = [p for p in os.environ.get("RQ_INPUT_ROOTS", "").split(os.pathsep) if p] + [
    os.path.join(HOME, "AI", "comfy-alienpc", "input")]
LOAD_KEYS = {"image", "audio", "video", "file"}
MEDIA_RE = re.compile(r"\.(png|jpe?g|webp|bmp|gif|wav|mp3|flac|ogg|m4a|aac|mp4|webm|mov|mkv)$", re.I)
_lock_fh = None
_UPLOAD_CACHE = {}  # (api, abs_path, subfolder) -> {"size", "mtime_ns", "name", "subfolder"}
_UPLOAD_CACHE_FILE = "_remote_uploads.json"


def _upload_sig(local_path):
    st = os.stat(local_path)
    return st.st_size, st.st_mtime_ns


def _upload_cache_key(item):
    return (API, os.path.abspath(item["local"]), item.get("subfolder") or "")


def _load_run_upload_cache(run_dir):
    if not run_dir:
        return {}
    p = os.path.join(run_dir, _UPLOAD_CACHE_FILE)
    if not os.path.isfile(p):
        return {}
    try:
        data = json.load(open(p, encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_run_upload_cache(run_dir, data):
    if not run_dir:
        return
    try:
        os.makedirs(run_dir, exist_ok=True)
        p = os.path.join(run_dir, _UPLOAD_CACHE_FILE)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
        os.replace(tmp, p)
    except OSError:
        pass


def _invalidate_upload_cache(items, run_dir=None):
    disk = _load_run_upload_cache(run_dir)
    dirty = False
    for it in items:
        k = _upload_cache_key(it)
        _UPLOAD_CACHE.pop(k, None)
        dk = f"{k[0]}|{k[1]}|{k[2]}"
        if dk in disk:
            disk.pop(dk, None)
            dirty = True
    if dirty:
        _save_run_upload_cache(run_dir, disk)


def upload_cached(item, run_dir=None, force=False, timeout=None):
    """Upload `item` unless the same (path, size, mtime_ns, subfolder) was already uploaded.
    Returns (response_dict, reused_bool)."""
    k = _upload_cache_key(item)
    size, mtime_ns = _upload_sig(item["local"])
    dk = f"{k[0]}|{k[1]}|{k[2]}"
    if not force:
        ent = _UPLOAD_CACHE.get(k)
        if ent is None and run_dir:
            ent = _load_run_upload_cache(run_dir).get(dk)
            if isinstance(ent, dict):
                _UPLOAD_CACHE[k] = ent
        if isinstance(ent, dict) and ent.get("size") == size and ent.get("mtime_ns") == mtime_ns and ent.get("name"):
            return {"name": ent["name"], "subfolder": ent.get("subfolder", "")}, True
    try:
        r = upload(item) if timeout is None else upload(item, timeout=timeout)
    except Exception:
        _invalidate_upload_cache([item], run_dir=run_dir)
        raise
    ent = {"path": k[1], "size": size, "mtime_ns": mtime_ns,
           "name": r.get("name") or os.path.basename(item["local"]),
           "subfolder": r.get("subfolder", item.get("subfolder", ""))}
    _UPLOAD_CACHE[k] = ent
    if run_dir:
        disk = _load_run_upload_cache(run_dir)
        disk[dk] = ent
        _save_run_upload_cache(run_dir, disk)
    return r, False


def input_files(g):
    """[(node_id, class_type, key, value)] for every Load* node input that names a ComfyUI input file."""
    g = g.get("prompt", g) if isinstance(g, dict) else {}
    out = []
    for nid, n in g.items():
        ct = str(n.get("class_type", ""))
        if "load" not in ct.lower():
            continue
        for k, v in (n.get("inputs") or {}).items():
            if k in LOAD_KEYS and isinstance(v, str) and MEDIA_RE.search(v.split(" [")[0]):
                out.append((nid, ct, k, v.split(" [")[0]))
    return out


def resolve(name, run_dir=None):
    roots = ([run_dir] if run_dir else []) + INPUT_ROOTS
    for r in roots:
        for cand in (os.path.join(r, name), os.path.join(r, os.path.basename(name))):
            if os.path.isfile(cand):
                return cand
    return None


def upload_plan(g, run_dir=None):
    """[{name, subfolder, local, bytes, kind}] or raises FileNotFoundError naming every missing input."""
    plan, missing, seen = [], [], set()
    for _nid, ct, k, name in input_files(g):
        if name in seen:
            continue
        seen.add(name)
        loc = resolve(name, run_dir)
        if not loc:
            missing.append(name); continue
        sub = os.path.dirname(name).replace("\\", "/")
        plan.append({"name": name, "subfolder": sub, "local": loc, "bytes": os.path.getsize(loc),
                     "kind": "audio" if k == "audio" or "audio" in ct.lower() else k})
    if missing:
        raise FileNotFoundError("missing local input(s): " + ", ".join(missing))
    return plan


def _multipart(fields, fname, data):
    b = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="image"; filename="{os.path.basename(fname)}"\r\n'
                 f'Content-Type: {ctype}\r\n\r\n'.encode() + data + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    return b"".join(parts), "multipart/form-data; boundary=" + b


def upload(item, timeout=300):
    """POST /upload/image (ComfyUI saves any bytes there, audio included; LoadAudio's widget uses the same route)."""
    with open(item["local"], "rb") as f:
        body, ct = _multipart({"subfolder": item["subfolder"], "type": "input", "overwrite": "true"}, item["local"], f.read())
    r = urllib.request.Request(API + "/upload/image", data=body, headers={"Content-Type": ct}, method="POST")
    return json.loads(urllib.request.urlopen(r, timeout=timeout).read())


def download(subfolder, filename, dst, timeout=900, not_before=None):
    """GET /view into dst. With not_before (epoch s), refuse a file whose Last-Modified is older or missing."""
    q = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder or "", "type": "output"})
    tmp = dst + ".part"
    with urllib.request.urlopen(API + "/view?" + q, timeout=timeout) as r:
        if not_before is not None:
            lm = r.headers.get("Last-Modified") if getattr(r, "headers", None) is not None else None
            ts = email.utils.parsedate_to_datetime(lm).timestamp() if lm else None
            if ts is None or ts < not_before:
                raise ValueError(f"stale or undated output {filename} (Last-Modified={lm})")
        _stream(r, tmp)
    os.replace(tmp, dst)
    return os.path.getsize(dst)


def _stream(r, tmp):
    with open(tmp, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            f.write(chunk)


def lock_acquire(note):
    """0 = acquired, 1 = held by a live PID (GPU busy), 9 = lock error. Same contract as gpu_lock.ps1 -Acquire."""
    global _lock_fh
    try:
        os.makedirs(os.path.dirname(LOCK), exist_ok=True)
        fh = open(LOCK, "a+")
        try:
            if fcntl is not None:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                fh.seek(0)
                if os.path.getsize(LOCK) == 0:
                    fh.write(" ")
                    fh.flush()
                    fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        except (BlockingIOError, OSError):
            fh.close(); return 1, "held"
        fh.seek(0); fh.truncate(); fh.write("%d %s %s\n" % (os.getpid(), time.strftime("%Y-%m-%dT%H:%M:%S"), note)); fh.flush()
        _lock_fh = fh
        return 0, "acquired " + LOCK
    except Exception as e:
        return 9, "lock error %s" % str(e)[:120]


def lock_release():
    global _lock_fh
    if _lock_fh:
        try:
            if fcntl is not None:
                _lock_fh.seek(0); _lock_fh.truncate(); fcntl.flock(_lock_fh, fcntl.LOCK_UN); _lock_fh.close()
            else:
                _lock_fh.seek(0)
                try:
                    msvcrt.locking(_lock_fh.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
                _lock_fh.seek(0); _lock_fh.truncate(); _lock_fh.close()
        finally:
            _lock_fh = None
        return 0, "released"
    return 0, "not held"


def remote_idle(timeout=20, logfile=None, comm_mod=None):
    """Check /system_stats (in AlienPc llama-swap ignorePaths) before /queue so an unloaded ComfyUI
    (409) is treated as idle without waking comfyui_auto. Returns True when loaded and /queue is empty,
    None when unloaded (409), or False when busy/unreachable."""
    try:
        with urllib.request.urlopen(API + "/system_stats", timeout=timeout) as resp:
            if getattr(resp, "status", 200) != 200:
                return False
            raw_stats = resp.read()
    except urllib.error.HTTPError as e:
        return None if e.code == 409 else False
    except Exception:
        return False
    if comm_mod is not None and raw_stats:
        try:
            st = json.loads(raw_stats)
            if hasattr(comm_mod, "check_launch_argv"):
                comm_mod.check_launch_argv(st, logfile)
        except ValueError:
            pass
    try:
        q = json.loads(urllib.request.urlopen(API + "/queue", timeout=timeout).read())
        return not (q.get("queue_running") or q.get("queue_pending"))
    except urllib.error.HTTPError as e:
        return None if e.code == 409 else False
    except Exception:
        return False


def remote_view_harvest(prefix, local_comfy_root, since=None, timeout=300):
    """Recover an evicted render over GET /view when unambiguous (_00001_ present, _00002_ absent).
    With since (attempt start), the file must be no older than since - 5 s, the same rule as run_queue.prefix_output,
    so an earlier attempt's output under the same prefix is never adopted."""
    if not prefix:
        return None
    norm = prefix.replace("\\", "/").strip("/")
    subf, stem = (os.path.dirname(norm), os.path.basename(norm))
    if not stem:
        return None
    for ext in (".mp4", ".png"):
        q2 = urllib.parse.urlencode({"filename": f"{stem}_00002_{ext}", "subfolder": subf, "type": "output"})
        try:
            with urllib.request.urlopen(API + "/view?" + q2, timeout=15) as r2:
                if getattr(r2, "status", 200) == 200:
                    return None  # ambiguous multi-file prefix on remote output dir; skip blind harvest
        except Exception:
            pass
        fname = f"{stem}_00001_{ext}"
        dst_dir = os.path.join(local_comfy_root, "output", *([p for p in subf.split("/") if p]))
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, fname)
        try:
            n = download(subf, fname, dst, timeout=timeout, not_before=None if since is None else since - 5)
            if n > 0:
                return dst
        except Exception:
            if os.path.exists(dst + ".part"):
                try:
                    os.remove(dst + ".part")
                except OSError:
                    pass
    return None


def enable(rq):
    """Rebind run_queue (module rq) and its comm / run_graph_job imports for the X3."""
    comm, rgj = rq.comm, rq.rgj
    root = os.path.join(HOME, "AI", "community")
    comm.W = root; comm.LOG = os.path.join(root, "community.log")
    comm.BASE = API; rgj.COMFY = API
    comm.C = os.path.join(HOME, "AI", "comfy-alienpc")   # local stub tree only: disk harvest finds nothing remote
    comm.LS = "remote-llama-swap-admin-not-exposed"; rgj.LS = comm.LS
    comm.GPU_LOCK_FILE = LOCK; comm.GPU_COLLECTED_FILE = LOCK + ".collected"
    comm.running = lambda: {"error": "remote mode: llama-swap admin routes are not exposed through :8446"}
    comm.free_comfy = lambda logfile=None: comm.log("COMFY free skipped (remote: AlienPc llama-swap ttl + graceful stop own the process)", logfile)
    comm.mark_collected = lambda pid=None, path=None: None
    rq.OUT_ROOT = os.path.join(comm.C, "output", "community")

    def _post(u, t=120):
        raise RuntimeError("remote mode: %s not exposed through :8446 (no-op)" % u.split("/api/")[-1][:60])
    rgj.post = _post

    orig_ps_run = rgj.ps_run
    def ps_run(file, *args):
        if file == rgj.GPU_LOCK_PS:
            if "-Acquire" in args:
                rc, msg = lock_acquire(" ".join(args[-2:]))
                if rc == 0:
                    wait_cap = max(0, int(os.environ.get("RQ_REMOTE_BUSY_WAIT_SEC", "0") or 0))
                    poll_s = max(1, int(os.environ.get("RQ_REMOTE_BUSY_POLL_SEC", "15") or 15))
                    deadline = time.monotonic() + wait_cap
                    while True:
                        idle = remote_idle(comm_mod=comm)
                        if idle is not False:
                            break
                        if time.monotonic() >= deadline:
                            lock_release(); return 1, "AlienPc ComfyUI /queue busy or unreadable"
                        time.sleep(min(poll_s, max(1.0, deadline - time.monotonic())))
                return rc, msg
            if "-Release" in args:
                return lock_release()
        return orig_ps_run(file, *args)
    rgj.ps_run = ps_run

    orig_wake = rgj.wake
    def wake(log):
        ok = orig_wake(log)
        if ok:
            try:
                st = comm.http(API + "/system_stats", timeout=15)
                if hasattr(comm, "check_launch_argv"):
                    comm.check_launch_argv(st)
            except Exception as ex:
                if "ARGV_MISMATCH" in str(ex):
                    raise
        return ok
    rgj.wake = wake

    orig_prefix_output = getattr(rq, "prefix_output", None)
    if callable(orig_prefix_output):
        def prefix_output(prefix, since):
            hit = orig_prefix_output(prefix, since)
            if hit:
                return hit
            return remote_view_harvest(prefix, comm.C, since=since)
        rq.prefix_output = prefix_output

    orig_submit = comm.submit
    def submit(g, tag, meta, outdir, logfile=None, out=None):
        run_dir = os.path.dirname(outdir)
        try:
            plan = upload_plan(g, run_dir)
        except FileNotFoundError as e:
            comm.log(f"JOB error {tag} {e}; nothing posted", logfile)
            return comm.outcome(out, "node_error", note=str(e)[:300])

        def _do_uploads(force=False):
            reused_any = False
            for it in plan:
                try:
                    r, reused = upload_cached(it, run_dir=run_dir, force=force)
                    if reused:
                        reused_any = True
                        comm.log(f"UPLOAD_SKIP {tag} {it['kind']} {it['name']} {it['bytes']}B (unchanged -> {r.get('subfolder','')}/{r.get('name')})", logfile)
                    else:
                        comm.log(f"UPLOAD {tag} {it['kind']} {it['name']} {it['bytes']}B -> {r.get('subfolder','')}/{r.get('name')}", logfile)
                except Exception as e:
                    comm.log(f"JOB error {tag} upload {it['name']} failed: {str(e)[:200]}; nothing posted", logfile)
                    return None, comm.outcome(out, "node_error", note="upload failed: " + it["name"])
            return reused_any, None

        reused_any, err = _do_uploads(force=False)
        if reused_any is None:
            return err
        sub_out = out if out is not None else {}
        pid = orig_submit(g, tag, meta, outdir, logfile, sub_out)
        if pid is None and reused_any and sub_out.get("outcome") == "node_error":
            comm.log(f"UPLOAD_RETRY {tag} queue rejected after cached upload; forcing fresh upload", logfile)
            _invalidate_upload_cache(plan, run_dir=run_dir)
            reused_retry, err2 = _do_uploads(force=True)
            if reused_retry is None:
                return err2
            sub_out.clear()
            pid = orig_submit(g, tag, meta, outdir, logfile, sub_out)
        return pid
    comm.submit = submit

    def fetch(pid, tag, meta, outdir, t0, logfile=None, out=None):
        h = comm.http(f"{API}/history/{pid}", timeout=comm.POLL_TIMEOUT)
        if pid not in h: return comm.PENDING
        st = h[pid].get("status", {}); outs = h[pid].get("outputs", {})
        files = [(f.get("subfolder"), f.get("filename")) for o in outs.values() for k in ("images", "gifs", "videos") for f in o.get(k, [])]
        dt = time.time() - t0
        if st.get("status_str") == "success" and files:
            sub, name = files[0]
            os.makedirs(outdir, exist_ok=True)
            dst = os.path.join(outdir, tag + os.path.splitext(name)[1])
            n = download(sub, name, dst)
            if dst.lower().endswith(".mp4") and callable(getattr(rq, "extract_last_frame", None)):
                rq.extract_last_frame(dst, os.path.join(outdir, "last_frame.png"))
            side = dict(meta, tag=tag, secs=round(dt, 1), comfy_output="alienpc:output/%s/%s" % (sub or "", name), file=dst,
                        bytes=n, prompt_id=pid, finished=time.strftime('%Y-%m-%d %H:%M CT'))
            json.dump(side, open(dst + ".json", "w", encoding="utf-8"), indent=1)
            comm.log(f"JOB end {tag} ok secs={dt:.1f} file={dst} (downloaded {n}B via /view)", logfile); return side
        msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
        comm.log(f"JOB error {tag} secs={dt:.1f} {json.dumps(msgs)[:1500]}", logfile)
        return comm.outcome(out, "node_error", pid, note=json.dumps(msgs)[:300])
    comm.fetch = fetch

    def detach(argv, run_dir):
        args = [a for a in argv if a != "--detach"]
        out = os.path.join(run_dir, "_run_queue.out.log")
        unit = "render-batch-" + re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(run_dir))[:80]
        # systemd-run --user does not inherit this shell's environment: forward the knobs the batch reads.
        env = [f"--setenv={k}={v}" for k, v in sorted(os.environ.items()) if k.startswith("RQ_") or k == "COMFY_API"]
        cmd = ["systemd-run", "--user", "--collect", "--unit", unit, "--working-directory", root,
               "--property", "StandardOutput=append:" + out, "--property", "StandardError=append:" + out, *env,
               rq.PY, "-u", os.path.abspath(rq.__file__), *args]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode:
            print("detach FAILED rc=%s %s" % (r.returncode, (r.stdout + r.stderr).strip()[:300])); return 8
        print("detached batch: systemd user unit %s; output %s; log %s" % (unit, out, os.path.join(run_dir, "_render_queue.log")))
        return 0
    rq.detach = detach

    def upscale_done(run_dir, jobs, slog):
        rq.qlog(run_dir, "UPSCALE deferred (X3 remote mode, decision D5: the 2x post-pass runs on AlienPc and is not wired yet); clips stay at the render size")
        return 0, 0
    rq.upscale_done = upscale_done


def dry_report(rq, run_dir, jobs):
    """Remote dry run: per clip, the graph checks and the upload list. Only GET /system_stats (an ignored path that
    never wakes ComfyUI) is called, and only with --probe; nothing is uploaded or posted."""
    comm = rq.comm
    bad = 0
    for j in jobs:
        gp = os.path.join(run_dir, j["tag"], "request.api.json")
        if not os.path.exists(gp):
            print("  %s: FAIL no graph %s" % (j["tag"], gp)); bad += 1; continue
        g = json.load(open(gp, encoding="utf-8"))
        g = g.get("prompt", g)
        ok, why = comm.guard_reason(g)
        try:
            plan = upload_plan(g, run_dir)
            up = "; ".join("%s %s (%dB from %s)" % (p["kind"], p["name"], p["bytes"], p["local"]) for p in plan) or "none"
        except FileNotFoundError as e:
            up = "FAIL " + str(e); bad += 1
        if not ok: bad += 1
        print("  %s: guard %s; nodes %d; uploads: %s" % (j["tag"], "ok" if ok else "FAIL " + why, len(g), up))
    print("remote: %s (POST /upload/image overwrite=true, POST /prompt, GET /history, GET /view into <run>/<tag>/)" % API)
    print("lock: %s (flock); detach: systemd-run --user; upscale: deferred to AlienPc (D5)" % LOCK)
    return bad
