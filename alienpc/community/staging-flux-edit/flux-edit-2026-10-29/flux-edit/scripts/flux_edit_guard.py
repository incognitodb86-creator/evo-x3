"""U4 minors guard, fail-closed (R1, R3, KTD11, card C6).

- check_graph: guard_ok on EVERY string anywhere in the API graph; any hit raises GuardStop (the run stops).
- AllowList: sha256 allow-list, hash-chained JSONL. Classes: approved / derived / pose_skeleton.
  Only the driver writes it (AllowListWriter; a static test enforces that). A hand edit breaks the chain = stop.
- check_image: sha256 must be listed, class known, derived parents all listed; Klein graphs take approved/derived only.
- Optional detector hook: anything but "adult" (unsure, other, exception) stops. None = no detector, not a stop.
Any error inside the guard is a stop.
"""
import hashlib
import json
import os
import re

CLASSES = ("approved", "derived", "pose_skeleton")
KIND_ALLOWED = {"klein": ("approved", "derived"), "read": CLASSES}

# Same rule as live comm.py guard_ok (ALI-80); parity is checked against the box mirror by AST in tests.
EXC = ['cowgirl', 'girlfriend', 'eighteen', 'kidnap', 'old-school', 'childhood']
BAD = {'girl', 'teen', 'school', 'schoolgirl', 'underage', 'minor', 'kid', 'child', 'loli', 'children'}


class GuardStop(Exception):
    pass


def guard_ok(t):
    t = t.lower()
    for e in EXC:
        t = t.replace(e, ' ')
    if 'barely legal' in t:
        return False
    for w in re.split(r"[^a-z]+", t):
        if w in BAD or (w.endswith('s') and w[:-1] in BAD) or w in ('schoolgirls', 'minors', 'teens', 'kids', 'girls'):
            return False
    return True


def _strings(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _strings(k, f"{path}/key")
            yield from _strings(v, f"{path}/{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _strings(v, f"{path}[{i}]")


def check_graph(graph):
    """Every string in the graph (inputs, titles, keys) must pass guard_ok. Hit or malformed graph = GuardStop."""
    try:
        if not isinstance(graph, dict) or not graph:
            raise GuardStop("graph is empty or not a dict")
        for path, s in _strings(graph):
            if not guard_ok(s):
                raise GuardStop(f"guard-stop keyword hit at {path}")
    except GuardStop:
        raise
    except Exception as e:  # fail-closed
        raise GuardStop(f"guard error {e!r}")
    return True


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _chain(prev, rec):
    return hashlib.sha256((prev + json.dumps(rec, sort_keys=True)).encode()).hexdigest()


class AllowList:
    """Read side. Missing file, broken chain, unknown class or bad JSON = GuardStop."""

    def __init__(self, path):
        self.path = path
        self.entries = {}
        if not os.path.isfile(path):
            raise GuardStop(f"allow-list missing: {path}")
        prev = "genesis"
        try:
            with open(path, encoding="utf-8") as f:
                for n, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    rec = {k: row[k] for k in ("sha256", "cls", "parents", "path")}
                    if row.get("chain") != _chain(prev, rec):
                        raise GuardStop(f"allow-list chain broken at line {n} (hand edit?)")
                    if rec["cls"] not in CLASSES:
                        raise GuardStop(f"unknown class {rec['cls']!r} at line {n}")
                    prev = row["chain"]
                    self.entries.setdefault(rec["sha256"], rec)  # first entry wins
        except GuardStop:
            raise
        except Exception as e:
            raise GuardStop(f"allow-list unreadable: {e!r}")
        self.last = prev

    def check_sha(self, sha, kind):
        if kind not in KIND_ALLOWED:
            raise GuardStop(f"unknown graph kind {kind!r}")
        e = self.entries.get(sha)
        if e is None:
            raise GuardStop(f"sha256 {sha[:12]} not on allow-list")
        if e["cls"] not in KIND_ALLOWED[kind]:
            raise GuardStop(f"class {e['cls']} not allowed in a {kind} graph")
        if e["cls"] == "derived":
            if not e["parents"]:
                raise GuardStop(f"derived {sha[:12]} has no parents")
            for p in e["parents"]:
                if p not in self.entries:
                    raise GuardStop(f"derived {sha[:12]} parent {p[:12]} not listed")
        return e


def check_image(path, kind, allow, detector=None):
    """Fail-closed image gate. Returns sha256. kind: 'klein' (graph input) or 'read' (scorer, scripts)."""
    try:
        sha = sha256_file(path)
        allow.check_sha(sha, kind)
        if detector is not None:
            verdict = detector(path)
            if verdict != "adult":
                raise GuardStop(f"detector verdict {verdict!r} (unsure or other = stop)")
        return sha
    except GuardStop:
        raise
    except Exception as e:
        raise GuardStop(f"image check error {e!r}")


class AllowListWriter:
    """Write side. Use ONLY from flux_edit_run.py (static test). Appends one chained JSONL line per image."""

    def __init__(self, path):
        self.path = path
        self.prev = AllowList(path).last if os.path.isfile(path) else "genesis"

    def add(self, sha, cls, parents=(), src_path=""):
        if cls not in CLASSES:
            raise GuardStop(f"refusing unknown class {cls!r}")
        if cls == "derived" and not parents:
            raise GuardStop("derived entry needs parents")
        rec = {"sha256": sha, "cls": cls, "parents": list(parents), "path": str(src_path)}
        ch = _chain(self.prev, rec)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(rec, chain=ch), sort_keys=True) + "\n")
        self.prev = ch
        return ch
