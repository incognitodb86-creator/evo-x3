"""G1 (fix_plan MAX block; brief 2026-10-31-0654, Derrick 6:53 AM CT): remove ONLY the age/school words from the
Negative lines of runs\\sslcaio_20261030 (request.api.json + _inputs\\prompts). Backup .bak-0654 first. Never adds words.
--check: no write, prints guard per job."""
import json, os, re, shutil, sys, glob
sys.path.insert(0, r"C:\AI\community\scripts")
import comm, run_queue
RUN = r"C:\AI\community\runs\sslcaio_20261030"
NEG = re.compile(r"(Negative\s*:)([^\n]*)", re.I)
removed = []

def clean_line(m, where):
    head, body = m.group(1), m.group(2)
    items = [x for x in re.split(r"(,)", body)]
    parts = body.split(",")
    keep = [p for p in parts if comm.guard_ok(p)]
    drop = [p.strip() for p in parts if not comm.guard_ok(p)]
    if drop: removed.append((where, drop))
    out = ",".join(keep)
    return head + out

def clean_text(t, where):
    return NEG.sub(lambda m: clean_line(m, where), t)

def walk(o, where):
    if isinstance(o, dict): return {k: walk(v, where) for k, v in o.items()}
    if isinstance(o, list): return [walk(v, where) for v in o]
    if isinstance(o, str) and "egative" in o: return clean_text(o, where)
    return o

def jobs():
    out = []
    for f in ("_order_ss.json", "_order_lc.json", "_order_aio.json"):
        for j in json.load(open(os.path.join(RUN, f), encoding="utf-8"))["order"]:
            out.append(j["tag"])
    return out

check = "--check" in sys.argv
if not check:
    files = [os.path.join(RUN, t.replace("/", os.sep), "request.api.json") for t in jobs()]
    files += [p for p in glob.glob(os.path.join(RUN, "_inputs", "prompts", "**", "*"), recursive=True) if os.path.isfile(p) and not ".bak" in p]
    changed = []
    for p in files:
        raw = open(p, encoding="utf-8").read()
        if p.endswith(".json"):
            new = json.dumps(walk(json.loads(raw), p), indent=1, ensure_ascii=False)
            if json.loads(new) == json.loads(raw): continue
        else:
            new = clean_text(raw, p)
            if new == raw: continue
        if not os.path.exists(p + ".bak-0654"): shutil.copy2(p, p + ".bak-0654")
        open(p, "w", encoding="utf-8", newline="").write(new)
        changed.append(p)
    print("files changed:", len(changed))
    for p in changed: print("  ", os.path.relpath(p, RUN))
    words = sorted({w.lower() for _, d in removed for w in d})
    print("distinct negative items removed:", len(words))
ok = 0; tj = jobs()
for t in tj:
    g = json.load(open(os.path.join(RUN, t.replace("/", os.sep), "request.api.json"), encoding="utf-8"))
    r = run_queue.guard_graph(g); ok += r
    print("guard", t, r)
print("GUARD %d/%d" % (ok, len(tj)))
sys.exit(0 if ok == len(tj) else 4)
