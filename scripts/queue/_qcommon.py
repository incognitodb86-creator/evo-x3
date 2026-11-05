r"""_qcommon.py - shared bits for the queue\queue_*.py scripts. Reuses make_render.py (APPROVED, counters,
approved_stills, submit pattern) and run_queue.py. Nothing here talks to ComfyUI except through run_queue.py
--detach (only when a script is run with --go). --dry-run never takes the GPU lock, bumps a counter or copies a file.
"""
import json, os, subprocess, sys, time, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
sys.path.insert(0, SCRIPTS)
import make_render as mr  # noqa: E402  (APPROVED, STATE, counter, approved_stills, COMFY_IN, PY)

ROOT = mr.ROOT
RUNS = os.path.join(ROOT, "runs")
MODELS = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models"
TEMPLATE = os.path.join(ROOT, "templates", "flux_stills_s2_bfs.api.json")
PY = mr.PY


def peek(name, start):
    p = os.path.join(mr.STATE, name)
    return int(open(p).read().strip()) if os.path.exists(p) else start


def model_path(kind, name):
    """kind: 'unet' (diffusion_models or unet) | 'lora' | 'clip' (text_encoders or clip) | 'vae'."""
    dirs = {"unet": ["diffusion_models", "unet"], "lora": ["loras"], "clip": ["text_encoders", "clip"], "vae": ["vae"]}[kind]
    for d in dirs:
        p = os.path.join(MODELS, d, name)
        if os.path.isfile(p):
            return p
    return None


def graph_files(g):
    """(kind, name) for every model/LoRA file a graph loads."""
    out = []
    for n in g.values():
        i, c = n.get("inputs", {}), n.get("class_type")
        if c == "UNETLoader": out.append(("unet", i["unet_name"]))
        elif c.startswith("LoraLoader"): out.append(("lora", i["lora_name"]))
        elif c == "CLIPLoader": out.append(("clip", i["clip_name"]))
        elif c == "VAELoader": out.append(("vae", i["vae_name"]))
    return out


def check_graph_files(graphs):
    """Return a sorted list of 'MISSING <kind> <name>' for every model file any graph needs."""
    miss = set()
    for g in graphs:
        for kind, name in graph_files(g):
            if not model_path(kind, name):
                miss.add("MISSING %s %s (looked in %s)" % (kind, name, MODELS))
    return sorted(miss)


def new_run_dir(test, go):
    """Date-first run dir like make_render: runs\\YYYY-MM-DD_<test>_NNNN (shared run_counter.txt). Dry run: peek only,
    and build under %TEMP% so nothing lands in runs\\."""
    if go:
        n = mr.counter("run_counter.txt")
        run = "%s_%s_%04d" % (time.strftime("%Y-%m-%d"), test, n)
        d = os.path.join(RUNS, run); os.makedirs(d)
    else:
        n = peek("run_counter.txt", 1)
        run = "%s_%s_%04d" % (time.strftime("%Y-%m-%d"), test, n)
        d = os.path.join(tempfile.gettempdir(), "queue_dry", run); os.makedirs(d, exist_ok=True)
    return run, d


def write_jobs(run_dir, jobs, order_name="_render_order.json", header=None):
    """jobs: [{'tag','graph', order fields...}] -> <run_dir>\\<tag>\\request.api.json + order file."""
    order = []
    for i, j in enumerate(jobs, 1):
        d = os.path.join(run_dir, j["tag"]); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "request.api.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(j["graph"], f, indent=1, ensure_ascii=False)
        order.append(dict({k: v for k, v in j.items() if k != "graph"}, pos=i))
    body = dict(header or {}); body["order"] = order
    p = os.path.join(run_dir, order_name)
    json.dump(body, open(p, "w", encoding="utf-8"), indent=1)
    return p


def run_queue_dry(run_dir, order_file):
    r = subprocess.run([PY, os.path.join(SCRIPTS, "run_queue.py"), "--run-dir", run_dir, "--queue", order_file, "--dry-run"],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode, (r.stdout + r.stderr).strip()


def _log(run_dir):
    p = os.path.join(run_dir, "_render_queue.log")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def submit(run_dir, order_file, size):
    """Same as make_render.submit, plus --queue: run_queue.py --detach (it takes C:\\AI\\locks\\gpu-render.lock);
    rc 7 GPU busy = wait 5 s and launch again. Returns the log offset once the batch is open or closed."""
    while True:
        off = len(_log(run_dir))
        r = subprocess.run([PY, os.path.join(SCRIPTS, "run_queue.py"), "--run-dir", run_dir, "--queue", order_file,
                            "--size", size, "--detach"], capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            sys.exit("FAILED run_queue --detach rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))
        while True:
            time.sleep(mr.POLL)
            t = _log(run_dir)[off:]
            if "BATCH closed rc=7" in t:
                time.sleep(5); break
            if "BATCH open" in t or "BATCH closed" in t:
                print("QUEUED %s (%s)" % (os.path.basename(run_dir), os.path.basename(order_file)), flush=True)
                return off


def wait_closed(run_dir, off):
    """Block until this batch logs BATCH closed; return its rc."""
    import re
    while True:
        m = re.search(r"BATCH closed rc=(\d+)", _log(run_dir)[off:])
        if m:
            return int(m.group(1))
        time.sleep(mr.POLL)
