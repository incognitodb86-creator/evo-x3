r"""ALI-173 B2 - keep C:/AI/community/runs/<id>/request.api.json in place (2026-10-23, CPU only, no LLM).

Why this file exists: the harness runs a graph job out of C:\\AI\\community\\runs\\<id>\\request.api.json
(ralph.ps1:284), but `runs/` is gitignored (C:/AI/community/.gitignore:10), so the graph the B2 job needs
is on disk and in no commit. ralph.ps1 has no `git clean` (grep 'clean -fdx' = 0 hits) so it survives
iterations, and the scope check does not touch a community-repo path - the ways to lose it are a manual
clean, a disk image swap, or a hand-edited file. The durable copy is
C:/AI/community/notes/ali173_b2_graph_ali173_cont_hc1_s51140001.json, committed.

Behaviour, in this order:
  - durable copy missing -> REFUSE (rc 2): there is nothing to restore from, re-run
    notes/ali173_b2_cont_build.py;
  - runs/<id>/request.api.json missing -> copy it in (status CREATED);
  - present and byte-identical -> OK;
  - present and semantically identical (json.loads equal) -> OK, a re-format is not a change;
  - present and semantically different -> REFUSE (rc 2) and name the keys/nodes that differ. It never
    overwrites, because the live file may be the one a running job is reading.

No schema check here: run_graph_job.static_check runs on every job submission and
notes/ali173_b2_static_offline.py runs it offline. Exit 0 = the job's graph file is present and matches
the durable copy.
"""
import hashlib, json, os, shutil, sys

ID = "ali173_cont_hc1_s51140001"
DURABLE = r"C:\AI\community\notes\ali173_b2_graph_ali173_cont_hc1_s51140001.json"
LIVE = r"C:\AI\community\runs\ali173_cont_hc1_s51140001\request.api.json"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def diff(a, b):
    out = []
    for k in sorted(set(a) | set(b)):
        if k not in a:
            out.append(f"node {k} only in the live file")
        elif k not in b:
            out.append(f"node {k} only in the durable copy")
        elif a[k] != b[k]:
            keys = sorted({x for x in list(a[k].get("inputs", {})) + list(b[k].get("inputs", {}))}
                          - {"meta"} | set())
            out.append(f"node {k} differs (class_type {a[k].get('class_type')} vs {b[k].get('class_type')}; "
                       f"changed inputs: {[x for x in keys if a[k].get('inputs', {}).get(x) != b[k].get('inputs', {}).get(x)]})")
    return out


def main():
    if not os.path.exists(DURABLE):
        print(f"REFUSE: no durable graph copy at {DURABLE} - re-run notes/ali173_b2_cont_build.py")
        return 2
    if not os.path.exists(LIVE):
        os.makedirs(os.path.dirname(LIVE), exist_ok=True)
        shutil.copyfile(DURABLE, LIVE)
        print(f"CREATED {LIVE} from the durable copy sha={sha(LIVE)[:16]}")
        return 0
    a, b = json.load(open(LIVE, encoding="utf-8")), json.load(open(DURABLE, encoding="utf-8"))
    if sha(LIVE) == sha(DURABLE):
        print(f"OK byte-identical nodes={len(a)} sha={sha(LIVE)[:16]}")
        return 0
    if a == b:
        print(f"OK json-equal (formatting differs) nodes={len(a)} live_sha={sha(LIVE)[:16]} "
              f"durable_sha={sha(DURABLE)[:16]}")
        return 0
    print("REFUSE: the live graph differs from the durable copy, not overwriting a file a job may be reading")
    for line in diff(a, b)[:12]:
        print("  " + line)
    return 2


def selftest():
    """The three paths above must be proved, not asserted (B2 rule: 1 self-destruct each).

    A restore script that prints OK when the durable copy is missing, or after the live graph was
    edited by hand, is worse than nothing at 3 AM: the job would run a graph nobody validated.
    Runs in a temp dir, so the real runs/ path is never touched.
    """
    import importlib, tempfile

    me = importlib.import_module(__name__ if __name__ != "__main__" else "ali173_b2_restore_graph")
    g = json.load(open(me.DURABLE, encoding="utf-8"))
    tmp = tempfile.mkdtemp(prefix="b2restore")
    ok = True
    for name, make in (("durable copy missing -> REFUSE", "no-durable"),
                       ("live graph missing -> CREATED", "no-live"),
                       ("live graph edited (one input key added) -> REFUSE", "edited"),
                       ("live graph byte-identical -> OK", "clean")):
        d = os.path.join(tmp, name.split()[0])
        os.makedirs(os.path.join(d, "runs", ID), exist_ok=True)
        os.makedirs(os.path.join(d, "notes"), exist_ok=True)
        durable = os.path.join(d, "notes", "g.json")
        live = os.path.join(d, "runs", ID, "request.api.json")
        if make != "no-durable":
            json.dump(g, open(durable, "w", encoding="utf-8"))
        if make in ("edited", "clean"):
            c = json.loads(json.dumps(g))
            if make == "edited":
                c["312"]["inputs"]["seed"] = 999
            json.dump(c, open(live, "w", encoding="utf-8"))
        me.DURABLE, me.LIVE = durable, live
        rc = me.main()
        want = {"no-durable": 2, "no-live": 0, "edited": 2, "clean": 0}[make]
        tag = "FIRED" if rc == want else "SILENT"
        ok = ok and rc == want
        print(f"PROBE {tag:6s} {name:52s} rc={rc} (want {want})")
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv[1:] else main())
