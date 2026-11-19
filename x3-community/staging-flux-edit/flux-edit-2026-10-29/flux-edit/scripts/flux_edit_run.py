"""U5 driver: plain Python, NO LLM calls (KTD8). Runs the pre-registered Phase A job list unattended.

Order: lock (foreign lock = HOLD) -> disk floor -> build + guard every graph (zero POSTs on any stop) ->
wait until llama-swap /running shows no LLM request in flight -> unload LLMs -> wake by polling
<LS>/comfyui/system_stats (<=420 s) -> comfy_ok (0.38.x) -> LoRA name from /object_info -> canary gate ->
jobs in arm blocks (300 s timeout, eviction = JOB error + re-wake + canary + one resubmit as <tag>_r1,
same failure class twice = harness-suspect stop, disk floor before every job, split after a block when the
projection overruns) -> unload comfyui_auto -> release own lock -> DONE.txt.
status.log lines: JOB start/end/error/timeout (+ CLIP_SKIP/SKIP are parsed as not-real, R6; never written here).
"""
import csv
import json
import os
import re
import shutil
import time
import urllib.error
import urllib.request

from PIL import Image

import config
import flux_edit_guard as guard
import flux_edit_workflow as wf

CANARY_SEED = config.SEEDS[0]


class Stop(Exception):
    pass


# ---------- status.log / R6 ----------
LINE = re.compile(r"^(?:\S+ \S+ )?(JOB start|JOB end|JOB error|JOB timeout|CLIP_SKIP|SKIP) (\S+)(.*)$")


def parse_log(path):
    st = {}
    if not os.path.isfile(path):
        return st
    with open(path, encoding="utf-8") as f:
        for ln in f:
            m = LINE.match(ln.strip())
            if not m:
                continue
            kind, tag, rest = m.groups()
            s = st.setdefault(tag, {"pid": None, "ok": False, "bad": False})
            if kind == "JOB start":
                pm = re.search(r"prompt_id=(\S+)", rest)
                s["pid"] = pm.group(1) if pm else None
            elif kind == "JOB end" and rest.strip().startswith("ok"):
                s["ok"] = True
            elif kind in ("JOB error", "JOB timeout", "CLIP_SKIP", "SKIP") or kind == "JOB end":
                s["bad"] = True
    return st


def is_real(st, tag):
    s = st.get(tag)
    return bool(s and s["pid"] and s["ok"] and not s["bad"])


def real_rows(st, tags):
    """A row is real when its tag (or its single eviction resubmit <tag>_r1) is real per R6."""
    return sum(1 for t in tags if is_real(st, t) or is_real(st, t + "_r1"))


# ---------- job plan ----------
def job_tag(panel, arm, seed):
    return f"{panel}_bfs_{arm}_s{seed}"


def load_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def plan_jobs(inputs_dir, approved_dir, window):
    if window not in config.WINDOW_ARMS:
        raise Stop(f"unknown window {window}")
    picks = load_csv(os.path.join(inputs_dir, "picks.csv"))
    heads = {h["character"]: h for h in load_csv(os.path.join(inputs_dir, "head_refs.csv"))}
    canary = [r for r in picks if r["role"] == "canary"]
    bodies = [r for r in picks if r["role"] == "body"]
    if len(canary) != 1 or len(bodies) != config.N_BODIES:
        raise Stop(f"picks.csv needs 1 canary + {config.N_BODIES} bodies, has {len(canary)} + {len(bodies)}")

    def head_for(row, arm):
        h = heads.get(row["target"])
        if h is None:
            raise Stop(f"no head ref for {row['target']}")
        if arm == "L-FULL":
            return os.path.join(approved_dir, h["source_path"]), h["source_sha256"]
        if not h.get("crop_sha256"):
            raise Stop(f"head crop for {row['target']} pending (MA box not cropped yet)")
        return os.path.join(inputs_dir, "head_refs", f"{row['target']}_head.png"), h["crop_sha256"]

    def job(panel, row, arm, seed, block):
        hp, hs = head_for(row, arm)
        return {"tag": job_tag(panel, arm, seed), "panel": panel, "arm": arm, "seed": seed, "block": block,
                "body": os.path.join(approved_dir, row["path"]), "body_sha": row["sha256"], "head": hp,
                "head_sha": hs, "units": config.ARM_UNITS[arm], "wh": (int(row["w"]), int(row["h"]))}

    jobs = [job("canary", canary[0], "L", CANARY_SEED, "canary")]
    for arm in config.WINDOW_ARMS[window]:
        for seed in config.SEEDS:
            for i, row in enumerate(bodies, 1):
                jobs.append(job(f"p{i:02d}", row, arm, seed, arm))
    return jobs


def units(jobs):
    return sum(j["units"] for j in jobs)


def budget_ok(n_units):
    return n_units * config.BUDGET_S_PER_UNIT <= config.WINDOW_S - config.WAKE_MAX_S


def should_split(warm_secs, remaining_units, now, window_end):
    if len(warm_secs) < config.WARM_JOBS_BEFORE_PROJECTION:
        return False
    mean = sum(warm_secs) / len(warm_secs)
    return now + mean * remaining_units > window_end - config.SPLIT_MARGIN_S


# ---------- llama-swap / ComfyUI HTTP ----------
class Http:
    def __init__(self, ls_url, comfy_path="/comfyui"):
        if not ls_url:
            raise Stop("llama-swap URL not configured (env FLUX_EDIT_LS_URL)")
        self.ls = ls_url.rstrip("/")
        self.comfy = self.ls + comfy_path
        self.calls = []

    def req(self, url, data=None, timeout=30, method=None):
        self.calls.append((method or ("POST" if data is not None else "GET"), url))
        body = json.dumps(data).encode() if data is not None else None
        r = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
        try:
            return json.loads(raw)
        except Exception:
            return raw.decode("utf-8", "replace")


IN_FLIGHT_KEYS = ("inflight", "in_flight", "activeRequests", "active_requests", "requests_in_flight")
BUSY_STATES = ("starting", "busy", "stopping", "loading")


def llm_state(running):
    """Return (busy, loaded_llms). Unknown /running shape = Stop (fail-closed; shape is unverified)."""
    if not isinstance(running, dict) or not isinstance(running.get("running"), list):
        raise Stop(f"/running shape unknown: {str(running)[:200]}")
    busy, loaded = False, []
    for e in running["running"]:
        if not isinstance(e, dict) or "model" not in e:
            raise Stop(f"/running entry unknown: {e!r}")
        if e["model"] == "comfyui_auto":
            continue
        loaded.append(e["model"])
        if str(e.get("state", "")).lower() in BUSY_STATES or any((e.get(k) or 0) > 0 for k in IN_FLIGHT_KEYS):
            busy = True
    return busy, loaded


# ---------- driver ----------
class Driver:
    def __init__(self, run_dir, inputs_dir, approved_dir, allow_path, window, http=None, lock_path=None,
                 comfy_input=None, comfy_output=None, disk_free_gb=None, clock=time.monotonic, sleep=time.sleep,
                 poll_s=2.0, llm_wait_s=config.LLM_IDLE_WAIT_S, wake_s=config.WAKE_MAX_S,
                 job_timeout_s=config.JOB_TIMEOUT_S, window_s=config.WINDOW_S, detector=None):
        self.run_dir, self.inputs, self.approved, self.allow_path = run_dir, inputs_dir, approved_dir, allow_path
        self.window, self.http, self.lock_path = window, http, lock_path
        self.cin, self.cout = comfy_input, comfy_output
        self.disk_free_gb = disk_free_gb or (lambda: shutil.disk_usage(run_dir).free / 2 ** 30)
        self.clock, self.sleep, self.poll_s = clock, sleep, poll_s
        self.llm_wait_s, self.wake_s, self.job_timeout_s, self.window_s = llm_wait_s, wake_s, job_timeout_s, window_s
        self.detector = detector
        self.log_path = os.path.join(run_dir, "status.log")
        self.evictions, self.fail_classes, self.own_lock = 0, {}, False
        os.makedirs(run_dir, exist_ok=True)

    def log(self, msg):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

    def note(self, fname, msg):
        with open(os.path.join(self.run_dir, fname), "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    # --- allow-list seeding (the ONLY writer of the allow-list) ---
    def seed_allowlist(self):
        w = guard.AllowListWriter(self.allow_path)
        have = guard.AllowList(self.allow_path).entries if os.path.isfile(self.allow_path) else {}
        for r in load_csv(os.path.join(self.inputs, "picks.csv")):
            self._add_checked(w, have, os.path.join(self.approved, r["path"]), r["sha256"], "approved", ())
        for h in load_csv(os.path.join(self.inputs, "head_refs.csv")):
            self._add_checked(w, have, os.path.join(self.approved, h["source_path"]), h["source_sha256"], "approved", ())
            if h.get("crop_sha256"):
                self._add_checked(w, have, os.path.join(self.inputs, "head_refs", f"{h['character']}_head.png"),
                                  h["crop_sha256"], "derived", (h["source_sha256"],))

    @staticmethod
    def _add_checked(w, have, path, sha, cls, parents):
        if guard.sha256_file(path) != sha:
            raise Stop(f"sha256 on disk != csv for {path}")
        if sha not in have:
            w.add(sha, cls, parents, os.path.basename(path))
            have[sha] = True

    # --- lock / disk ---
    def take_lock(self):
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        with os.fdopen(fd, "w") as f:
            f.write(f"flux_edit_run pid={os.getpid()}\n")
        self.own_lock = True
        return True

    def release_lock(self):
        if self.own_lock and os.path.isfile(self.lock_path):
            os.remove(self.lock_path)
        self.own_lock = False

    def check_disk(self, floor):
        free = self.disk_free_gb()
        if free < floor:
            raise Stop(f"disk floor: {free:.1f} GB free < {floor} GB (C7)")

    # --- graphs ---
    def staged_name(self, sha, path):
        return f"flux_edit/{sha[:16]}{os.path.splitext(path)[1].lower()}"

    def build_graph(self, job, allow, lora_name):
        for p, s in ((job["body"], job["body_sha"]), (job["head"], job["head_sha"])):
            if guard.check_image(p, "klein", allow, self.detector) != s:
                raise guard.GuardStop(f"sha256 mismatch for {p}")
        return wf.build(job["arm"], self.staged_name(job["body_sha"], job["body"]),
                        self.staged_name(job["head_sha"], job["head"]), job["seed"], lora_name,
                        f"flux_edit/{job['tag']}")

    def stage(self, job):
        for p, s in ((job["body"], job["body_sha"]), (job["head"], job["head_sha"])):
            dst = os.path.join(self.cin, *self.staged_name(s, p).split("/"))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.isfile(dst):
                shutil.copyfile(p, dst)
            if guard.sha256_file(dst) != s:
                raise Stop(f"staged copy sha mismatch {dst}")

    def dry_run(self):
        allow = guard.AllowList(self.allow_path)
        jobs = plan_jobs(self.inputs, self.approved, self.window)
        out = os.path.join(self.run_dir, "dryrun")
        os.makedirs(out, exist_ok=True)
        for j in jobs:
            g = self.build_graph(j, allow, wf.PINS["lora"]["name"])
            with open(os.path.join(out, j["tag"] + ".api.json"), "w", encoding="utf-8") as f:
                json.dump(g, f, indent=1)
        return jobs

    # --- wake ---
    def wait_llm_idle_and_unload(self):
        t0 = self.clock()
        while True:
            busy, loaded = llm_state(self.http.req(self.http.ls + "/running", timeout=10))
            if not busy:
                break
            if self.clock() - t0 > self.llm_wait_s:
                raise Stop("LLM request still in flight after wait; window not quiet")
            self.sleep(self.poll_s)
        for m in loaded:
            self.log(f"UNLOAD LLM {m}")
            self.http.req(f"{self.http.ls}/api/models/unload/{m}", data={}, timeout=120)

    def wake(self):
        t0 = self.clock()
        url = self.http.comfy + "/system_stats"
        while True:
            try:
                st = self.http.req(url, timeout=60)
                if isinstance(st, dict) and "system" in st:
                    break
            except (urllib.error.URLError, OSError, ValueError):
                pass
            if self.clock() - t0 > self.wake_s:
                raise Stop(f"ComfyUI did not wake within {self.wake_s} s via {url}")
            self.sleep(self.poll_s)
        ver = str(st["system"].get("comfyui_version", ""))
        self.note("preflight.txt", f"wake path {config.get('COMFY_PATH') or '/comfyui'}/system_stats ok; version {ver}")
        if not ver.startswith(config.COMFY_VERSION_PREFIX):
            raise Stop(f"comfy_ok failed: version {ver!r} is not {config.COMFY_VERSION_PREFIX}x")
        return ver

    def lora_name(self):
        oi = self.http.req(self.http.comfy + "/object_info/LoraLoaderModelOnly", timeout=60)
        try:
            opts = oi["LoraLoaderModelOnly"]["input"]["required"]["lora_name"][0]
        except Exception:
            raise Stop("object_info LoraLoaderModelOnly shape unknown")
        try:
            return wf.pick_lora_option(opts)
        except SystemExit as e:
            raise Stop(str(e))

    # --- one job ---
    def submit(self, job, graph, tag):
        with open(os.path.join(self.run_dir, tag + ".api.json"), "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=1)
        res = self.http.req(self.http.comfy + "/prompt", data={"prompt": graph, "client_id": "flux-edit"}, timeout=60)
        pid = res.get("prompt_id") if isinstance(res, dict) else None
        if not pid:
            self.log(f"JOB error {tag} post-rejected {str(res)[:300]}")
            return None
        self.log(f"JOB start {tag} prompt_id={pid}")
        return pid

    def harvest(self, job, tag, pid, allow_w):
        """Poll /history then /queue. Returns 'ok' or a failure class ('evicted', 'timeout', 'exec:<x>', 'wh')."""
        t0 = self.clock()
        while True:
            h = self.http.req(f"{self.http.comfy}/history/{pid}", timeout=30)
            if isinstance(h, dict) and pid in h:
                return self._finish(job, tag, pid, h[pid], self.clock() - t0, allow_w)
            q = self.http.req(self.http.comfy + "/queue", timeout=30)
            ids = [x[1] for k in ("queue_running", "queue_pending") for x in (q.get(k, []) if isinstance(q, dict)
                                                                              else [])]
            if pid not in ids:
                self.log(f"JOB error {tag} evicted")
                return "evicted"
            if self.clock() - t0 > self.job_timeout_s:
                self.log(f"JOB timeout {tag}")
                return "timeout"
            self.sleep(self.poll_s)

    def _finish(self, job, tag, pid, hist, secs, allow_w):
        st = hist.get("status", {})
        files = [f for o in hist.get("outputs", {}).values() for f in o.get("images", [])]
        if st.get("status_str") != "success" or not files:
            msgs = [m for m in st.get("messages", []) if m and m[0] == "execution_error"]
            cls = "exec:" + (str(msgs[0][1].get("node_type")) if msgs else "no-output")
            self.log(f"JOB error {tag} {cls}")
            with open(os.path.join(self.run_dir, tag + ".history.json"), "w", encoding="utf-8") as f:
                json.dump(hist, f, indent=1)
            return cls
        src = os.path.join(self.cout, files[0].get("subfolder", ""), files[0]["filename"])
        dst = os.path.join(self.run_dir, "phaseA_bfs", tag + ".png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        with Image.open(dst) as im:
            wh = im.size
        if tuple(wh) != tuple(job["wh"]):
            self.log(f"JOB error {tag} wh {wh[0]}x{wh[1]} != {job['wh'][0]}x{job['wh'][1]}")
            return "wh"
        osha = guard.sha256_file(dst)
        allow_w.add(osha, "derived", (job["body_sha"], job["head_sha"]), os.path.basename(dst))  # only at JOB end
        side = {"tag": tag, "arm": job["arm"], "seed": job["seed"], "template": wf.NAME,
                "template_version": wf.VERSION, "workflow_api_sha256": guard.sha256_file(
                    os.path.join(self.run_dir, tag + ".api.json")), "body_sha256": job["body_sha"],
                "head_sha256": job["head_sha"], "out_sha256": osha, "out_wh": list(wh), "secs": round(secs, 1),
                "prompt_id": pid}
        with open(dst[:-4] + ".json", "w", encoding="utf-8") as f:
            json.dump(side, f, indent=1)
        self.log(f"JOB end {tag} ok secs={secs:.1f}")
        return "ok"

    def run_one(self, job, graph, allow_w, tag=None, pid=None):
        tag = tag or job["tag"]
        if pid is None:
            pid = self.submit(job, graph, tag)
            if pid is None:
                return "post"
        return self.harvest(job, tag, pid, allow_w)

    def canary(self, jobs, graphs, allow_w, n):
        tag = jobs[0]["tag"] + (f"_c{n}" if n else "")
        r = self.run_one(jobs[0], graphs[jobs[0]["tag"]], allow_w, tag=tag)
        st = parse_log(self.log_path)
        self.note("canary.txt", f"{tag} result={r} real={is_real(st, tag)}")
        if r != "ok" or not is_real(st, tag):
            raise Stop(f"canary {tag} failed ({r}); harness triage before any job")

    def fail(self, job, cls, graph):
        if cls == "evicted":
            return
        self.fail_classes.setdefault(cls, []).append(job["tag"])
        if len(self.fail_classes[cls]) >= 2:
            dump = {"class": cls, "tags": self.fail_classes[cls], "body_sha": job["body_sha"],
                    "head_sha": job["head_sha"], "wh": job["wh"], "prompt": [n["inputs"].get("text") for n in
                                                                              graph.values() if n["class_type"] ==
                                                                              "CLIPTextEncode"]}
            with open(os.path.join(self.run_dir, "harness_suspect.json"), "w", encoding="utf-8") as f:
                json.dump(dump, f, indent=1)
            raise Stop(f"harness suspect: failure class {cls} twice ({self.fail_classes[cls]})")

    # --- whole window ---
    def run(self):
        if not self.take_lock():
            self.log(f"HOLD foreign lock present: {self.lock_path} (untouched)")
            return "HOLD"
        result = "STOP"
        try:
            result = self._run()
        except (Stop, guard.GuardStop) as e:
            self.log(f"STOP {e}")
            result = f"STOP {e}"
        finally:
            try:
                if self.http and self.own_lock:
                    self.http.req(f"{self.http.ls}/api/models/unload/comfyui_auto", data={}, timeout=120)
            except Exception as e:  # noqa: BLE001 - unload failure is reported, not hidden
                self.log(f"WARN unload comfyui_auto failed {e!r}")
            self.release_lock()
            self.write_done(result)
        return result

    def _run(self):
        self.check_disk(config.DISK_START_GB)
        allow = guard.AllowList(self.allow_path)
        allow_w = guard.AllowListWriter(self.allow_path)
        jobs = plan_jobs(self.inputs, self.approved, self.window)
        if not budget_ok(units(jobs)):
            raise Stop(f"{units(jobs)} job-units exceed the {config.BUDGET_S_PER_UNIT} s/unit budget; split first")
        self.jobs = jobs
        graphs = {j["tag"]: self.build_graph(j, allow, wf.PINS["lora"]["name"]) for j in jobs}  # guard all, 0 POSTs
        self.wait_llm_idle_and_unload()
        self.wake()
        lora = self.lora_name()
        graphs = {j["tag"]: self.build_graph(j, allow, lora) for j in jobs}
        for j in jobs:
            self.stage(j)
        st = parse_log(self.log_path)
        n_canary = sum(1 for t in st if t.startswith(jobs[0]["tag"]))
        self.canary(jobs, graphs, allow_w, n_canary)
        window_end = self.clock() + self.window_s - self.wake_s
        warm, block = [], None
        todo = [j for j in jobs[1:]]
        for i, j in enumerate(todo):
            if block is not None and j["block"] != block and should_split(
                    warm, units(todo[i:]), self.clock(), window_end):
                self.log(f"SPLIT after block {block}: {len(todo) - i} jobs left for a resume window")
                return "SPLIT"
            block = j["block"]
            st = parse_log(self.log_path)
            tag, r1 = j["tag"], j["tag"] + "_r1"
            if is_real(st, tag) or is_real(st, r1):
                continue
            s, s1 = st.get(tag), st.get(r1)
            if s1 is not None and not (s1["pid"] and not s1["ok"] and not s1["bad"]):
                continue  # the one resubmit already ran and failed (strict R6)
            if s is not None and s["bad"] and not self._was_evicted(tag):
                continue  # strict R6: a failed tag is not retried
            self.check_disk(config.DISK_STOP_GB)
            guard.check_graph(graphs[tag])
            t0 = self.clock()
            if s1 is not None:
                r = self.run_one(j, graphs[tag], allow_w, tag=r1, pid=s1["pid"])  # resume the resubmit
            elif s is not None and s["pid"] and not s["ok"] and not s["bad"]:
                r = self.run_one(j, graphs[tag], allow_w, pid=s["pid"])  # resume: harvest /history first
            elif s is not None:
                r = "evicted-before"  # evicted in an earlier window; this window already woke + ran its canary
            else:
                r = self.run_one(j, graphs[tag], allow_w)
            if r == "evicted":
                self.evictions += 1
                if self.evictions >= 2:
                    raise Stop("second eviction: stop and report")
                self.wait_llm_idle_and_unload()
                self.wake()
                self.canary(jobs, graphs, allow_w, n_canary + self.evictions)
            if r in ("evicted", "evicted-before"):
                r = self.run_one(j, graphs[tag], allow_w, tag=r1)
                if r == "evicted":
                    raise Stop("second eviction: stop and report")
            if r == "ok":
                warm.append((self.clock() - t0) / j["units"])
            else:
                self.fail(j, r, graphs[j["tag"]])
        return "COMPLETE"

    def _was_evicted(self, tag):
        if not os.path.isfile(self.log_path):
            return False
        with open(self.log_path, encoding="utf-8") as f:
            return any(re.search(rf" JOB error {re.escape(tag)} evicted$", ln.rstrip()) for ln in f)

    def write_done(self, result):
        st = parse_log(self.log_path)
        jobs = getattr(self, "jobs", [])
        tags = [j["tag"] for j in jobs[1:]]
        starts = sum(1 for t, s in st.items() if s["pid"])
        last = ""
        if os.path.isfile(self.log_path):
            with open(self.log_path, encoding="utf-8") as f:
                lines = f.read().splitlines()
                last = lines[-1] if lines else ""
        with open(os.path.join(self.run_dir, "DONE.txt"), "w", encoding="utf-8") as f:
            f.write(f"result: {result}\nwindow: {self.window}\nJOB start lines (tags): {starts}\n"
                    f"real non-skip rows: {real_rows(st, tags)} of {len(tags)} (status.log)\nlast log line: {last}\n")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="flux-edit Phase A driver (no LLM)")
    ap.add_argument("--window", choices=sorted(config.WINDOW_ARMS), required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed-allowlist", action="store_true")
    a = ap.parse_args()
    root = config.require("ROOT")
    run_dir = os.path.join(root, f"window_{a.window}")
    kw = dict(run_dir=run_dir, inputs_dir=os.path.join(root, "inputs"), approved_dir=config.require("APPROVED_DIR"),
              allow_path=os.path.join(root, "allow_list.jsonl"), window=a.window)
    if a.seed_allowlist:
        Driver(**kw).seed_allowlist()
    if a.dry_run:
        print(f"dry-run wrote {len(Driver(**kw).dry_run())} api.json, zero POSTs")
        return
    d = Driver(**kw, http=Http(config.require("LS_URL"), config.get("COMFY_PATH") or "/comfyui"),
               lock_path=config.require("LOCK_PATH"), comfy_input=config.require("COMFY_INPUT"),
               comfy_output=config.require("COMFY_OUTPUT"))
    print(d.run())


if __name__ == "__main__":
    main()
