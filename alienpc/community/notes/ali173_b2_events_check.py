r"""ALI-173 B2 - validate C:/AI/community/runs/bakeoff_gpu_events.jsonl (2026-10-23, CPU only, no LLM).

The ledger is prose for a human; this file is the machine gate for the events line the B2 task asks for
("`C:/AI/community/runs/bakeoff_gpu_events.jsonl` exists with the job id and the render_start/render_pass
pair"). Schema = notes/bakeoff_gpu_events.md, six keys per line:

  event    one of request_staged, precheck_pass, render_start, render_pass, render_fail,
           gpu_window_open, gpu_window_close
  iter     ^loop\d\d$
  ts       ISO-8601 to the second
  job_id   ^[a-z0-9_]+_s\d+$      (underscores REQUIRED: ali173_cont_hc1_s51140001, ali147_pool_hc_r3b_s51130001)
  sha256   64 lowercase hex, and it must equal hashlib.sha256 of the graph file named for that job
  status   ok / fail / blocked

Missing file is a loud rc 2 (B1's rule: never report an empty pass). Every rule has a probe in
--selftest that must FAIL, because a validator that accepts a 65-hex sha, an uppercase sha, `iter=loop1`,
`job_id=loop01`, a 5-key line, or a sha that is not the graph's, is decoration (Learnings: a green check
that cannot fail is worthless). Exit 0 = every line is schema-clean and the graph hashes match.
"""
import hashlib, json, os, re, sys, tempfile

EVENTS = r"C:\AI\community\runs\bakeoff_gpu_events.jsonl"
GRAPH = r"C:\AI\community\runs\%s\request.api.json"
KEYS = ["event", "iter", "ts", "job_id", "sha256", "status"]
EVENTS_OK = {"request_staged", "precheck_pass", "render_start", "render_pass", "render_fail",
             "gpu_window_open", "gpu_window_close"}
RE_ITER = re.compile(r"^loop\d\d$")
RE_JOB = re.compile(r"^[a-z0-9_]+_s\d+$")
RE_SHA = re.compile(r"^[0-9a-f]{64}$")
RE_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
STATUS_OK = {"ok", "fail", "blocked"}


def check_line(o):
    """Return a list of faults for one parsed object ([] = clean)."""
    f = []
    if sorted(o.keys()) != sorted(KEYS):
        f.append(f"keys must be exactly {KEYS}, got {sorted(o.keys())}")
        return f
    if o["event"] not in EVENTS_OK:
        f.append(f"event {o['event']!r} not in {sorted(EVENTS_OK)}")
    if not RE_ITER.match(str(o["iter"])):
        f.append(f"iter {o['iter']!r} !~ {RE_ITER.pattern}")
    if not RE_TS.match(str(o["ts"])):
        f.append(f"ts {o['ts']!r} is not ISO-8601 seconds")
    if not RE_JOB.match(str(o["job_id"])):
        f.append(f"job_id {o['job_id']!r} !~ {RE_JOB.pattern}")
    if not RE_SHA.match(str(o["sha256"])):
        f.append(f"sha256 {o['sha256']!r} is not 64 lowercase hex")
    if o["status"] not in STATUS_OK:
        f.append(f"status {o['status']!r} not in {sorted(STATUS_OK)}")
    return f


def check_file(path, want_job=None):
    if not os.path.exists(path):
        return ["MISSING FILE - the events file does not exist, it is not an empty pass: " + path]
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    faults, jobs = [], []
    for n, l in enumerate(lines, 1):
        try:
            o = json.loads(l)
        except Exception as e:
            faults.append(f"line {n}: not JSON ({e})")
            continue
        faults += [f"line {n}: {x}" for x in check_line(o)]
        jobs.append(o.get("job_id"))
        if RE_SHA.match(str(o.get("sha256", ""))) and RE_JOB.match(str(o.get("job_id", ""))):
            g = GRAPH % o["job_id"]
            if not os.path.exists(g):
                faults.append(f"line {n}: the graph file the sha must be of is absent: {g}")
            elif hashlib.sha256(open(g, "rb").read()).hexdigest() != o["sha256"]:
                faults.append(f"line {n}: sha256 is not the sha256 of {g}")
    if not lines:
        faults.append("the events file has 0 lines - a vacuous pass")
    if want_job and want_job not in jobs:
        faults.append(f"no line names the job id {want_job}")
    return faults


def selftest():
    """Probes: each fault must be CAUGHT (rc/faults non-empty), the clean line must pass."""
    global GRAPH
    tmp = tempfile.mkdtemp(prefix="b2events")
    GRAPH = os.path.join(tmp, "runs", "%s", "request.api.json")   # the probes re-hash temp files, not the live graph
    gdir = os.path.join(tmp, "runs", "ali173_cont_hc1_s51140001")
    os.makedirs(gdir)
    graph = os.path.join(gdir, "request.api.json")
    open(graph, "w", encoding="utf-8").write('{"1": {"class_type": "X"}}')
    sha = hashlib.sha256(open(graph, "rb").read()).hexdigest()
    clean = {"event": "request_staged", "iter": "loop07", "ts": "2026-10-23T18:30:25",
             "job_id": "ali173_cont_hc1_s51140001", "sha256": sha, "status": "ok"}
    probes = [("clean line -> accepted", [clean], 0),
              ("65-hex sha -> rejected", [dict(clean, sha256=sha + "a")], 1),
              ("63-hex sha -> rejected", [dict(clean, sha256=sha[:-1])], 1),
              ("UPPERCASE sha -> rejected", [dict(clean, sha256=sha.upper())], 1),
              ("iter=loop1 -> rejected", [dict(clean, iter="loop1")], 1),
              ("job_id=loop01 -> rejected", [dict(clean, job_id="loop01")], 1),
              ("dashed job_id -> rejected", [dict(clean, job_id="ali173-cont-hc1-s51140001")], 1),
              ("unknown event -> rejected", [dict(clean, event="render_done")], 1),
              ("5-key line -> rejected", [{k: v for k, v in clean.items() if k != "status"}], 1),
              ("7-key line -> rejected", [dict(clean, note="hi")], 1),
              ("sha of a DIFFERENT graph -> rejected", [dict(clean, sha256="0" * 64)], 1)]
    ok = True
    for name, objs, want in probes:
        p = os.path.join(tmp, name.split()[0] + ".jsonl")
        with open(p, "w", encoding="utf-8") as fh:
            for o in objs:
                fh.write(json.dumps(o) + "\n")
        fl = check_file(p, want_job="ali173_cont_hc1_s51140001")
        good = (len(fl) == 0) if want == 0 else (len(fl) > 0)
        ok = ok and good
        print(f"PROBE {'FIRED ' if good else 'SILENT'} {name:42s} faults={len(fl)}")
    fl = check_file(os.path.join(tmp, "absent.jsonl"))
    good = any(x.startswith("MISSING FILE") for x in fl)
    ok = ok and good
    print(f"PROBE {'FIRED ' if good else 'SILENT'} missing file -> loud, not an empty pass   faults={len(fl)}")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    bad = check_file(EVENTS, want_job="ali173_cont_hc1_s51140001")
    n = len([l for l in open(EVENTS, encoding="utf-8").read().splitlines() if l.strip()]) if os.path.exists(EVENTS) else 0
    print(f"events lines={n} file={EVENTS}")
    for x in bad:
        print("  FAULT " + x)
    pair = [l for l in (open(EVENTS, encoding="utf-8").read().splitlines() if os.path.exists(EVENTS) else [])
            if '"render_start"' in l] and [l for l in (open(EVENTS, encoding="utf-8").read().splitlines()
                                                       if os.path.exists(EVENTS) else []) if '"render_pass"' in l]
    print(f"render_start/render_pass pair present: {bool(pair[0]) if pair else False} / "
          f"{bool(pair[1]) if len(pair) > 1 else False}  (due when the harness runs the job)")
    print("VERDICT:", "EVENTS SCHEMA CLEAN" if not bad else f"{len(bad)} FAULT(S)")
    sys.exit(0 if not bad else 1)
