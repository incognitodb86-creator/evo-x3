#!/usr/bin/env python3
"""ali08 - item 0.8: every row of `git status` has a decided fate, and a measurement proves the tree is clean.

L8 (AGENTS.md): "ANY untracked file dies at the boundary: 5 read mid-pass 2026-10-24 were gone at build time".
A row sitting in `git status` is therefore one of two things - work that must become durable, or generated litter
in a surface a human reads. `git add -A` cannot tell them apart, and 0.8's 28 rows prove it: 20 of them are
`--ab-selftest` probe output inside notes/hc15_audit, the folder Derrick reads for metrics and contact sheets
(NOW-P2 kept its seeds inside in-memory clones and wrote nothing; the 2.7b LITTER row calls the same shape red),
while 6 are the briefs the fix_plan MAX block cites as evidence, and 1 is a gitlink with no .gitmodules.

So this file carries the disposition of every row as DATA and verifies it against disk. `--note` writes
notes/git_status_cleanup_20261025.md FROM that same data, so the note and the gate cannot drift.

Checks (7 groups, 11 claims; each one is seeded in --selftest, and must be 0 on the real tree):
  1  CLEAN     `git status --porcelain` is 0 rows in the two repos this item writes in (`C:/AI/community`,
               `ralph-community`); `C:/AI/director`'s count is measured and printed as out-of-scope context.
  2  LEDGER    the 28 rows measured at 15:0x CT are all dispositioned, and every disposition resolves:
               2a COMMIT  a committed path is in `git ls-files` at its recorded bytes/sha; the AGY watchdog's live
                          append log (briefs/agy_monitor.out.txt, the ForgeAgyMonitor task) is checked grow-only,
                          because it was written 2 minutes before this was measured - a sha there fails on its next run.
               2b DROP    the 20 ab_seed_*.json are gone from disk and from the index.
               2c MOVE    briefs/agy_monitor.md.pre-20261025.bak is gone and its bytes are tracked at the recorded
                          sha256 (that file is in NO commit: briefs/agy_monitor.md entered git only at e791bb6, the
                          MONITOR commit, whose blob is a different 1,456 B - git history was not the backup here).
               2d UNTRACK the gitlink is out of the index and the tree is declared ignored by a rule carrying a reason.
  3  ZIP       the tracked zip's bytes/sha match the record, and the index blob == the HEAD blob == the disk bytes.
  4  NO-WRITE  hc15_anchor_fix_build.py's ab_selftest() writes nothing under notes/ and opens a temp dir, and
               notes/hc15_audit carries 0 ab_seed_* files (the OLD wiring, restored in a clone, must fire).
  5  TREE==ZIP a fresh unzip of that zip is byte-identical to the unpacked extension Chrome loads, for every path
               in the recorded per-file tree manifest (this is what makes removing the gitlink lossless).
  6  RECORD    the recorded `git status` of the extracted zip tree matches what that tree says now (it runs on
               the pristine extraction, before the mutating replay).
  7  PATCH     the recorded 2026-10-24 diff applies to the clean inner HEAD tree and reproduces the 4 patched
               files of the live tree byte-for-byte (code that lived only in a work copy becomes replayable).

No GPU, no queue, no network, no LLM, no score, no pick. Reads + a temp dir. Exit 0 = every seed fires and the
real tree is clean.
"""
from __future__ import annotations
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ali02_citation_check import ignore_rule, is_tracked   # one source of truth for tracking + ignore rules

W = r"C:/AI/community"
CLEAN_REPOS = (W, r"C:/Users/derek/5slock/ralph-community")   # the two repos 0.8 writes in
INFO_REPOS = (r"C:/AI/director",)                            # measured, never a finding of this item
SNAP = "notes/gmd_ext_20261024"
BUILDER = os.path.join(W, "notes", "hc15_anchor_fix_build.py")
AUD = os.path.join(W, "notes", "hc15_audit")
NOTE = os.path.join(W, "notes", "git_status_cleanup_20261025.md")
MEASURED = "2026-10-25 15:05-15:15 CT (box clock; fix_plan MAX lines run ahead of it - needs_derrick row 27b)"

# --- the 28 rows of `git status --porcelain` in C:/AI/community at the start of 0.8, verbatim ---
SEED_ROWS = ["incoming/gmd-dl-ext-2.5.6"] + [
    "briefs/" + f for f in ("agy_audit_20261025.md", "agy_audit_20261025.out.txt", "agy_audit_20261025_report.md",
                            "agy_audit_run.ps1", "agy_monitor.md.pre-20261025.bak", "agy_monitor.out.txt",
                            "agy_monitor_run.ps1")] + [
    "notes/hc15_audit/ab_seed_%02d.json" % i for i in range(20)]

# --- recorded identities (measured off disk in the window above; the gate re-measures every one) ---
ZIP = {"path": "incoming/gmd-dl-ext-2.5.6.zip", "bytes": 21935298,
       "sha256": "cf15deb6d0bbba02f9964942e812beb0ea7272c0278d13ac118a2d2d7fcf9b20",
       "blob": "c4c0ef01928aae34f5cc1831dc7ce8f2136d5dec",
       "inner_head": "eaa2b819f189021bc224afd7b7e11c7e8d2ccd52", "tree_files": 229,
       "note": "fix_plan.md:133 (item 2.0c) records this path as `zip sha256 cf15deb6...9b20` - it MATCHES the "
               "bytes on disk, re-measured here, so the plan row is accurate and the zip is the durable identity"}
BAK = {"src": "briefs/agy_monitor.md.pre-20261025.bak", "dst": "notes/briefs-snapshots-2026-10-25/agy_monitor_pre-MONITOR.md",
       "bytes": 1808, "sha256": "f3c6cb60e3d3ee47ccc5a0d195415337d91ae849fc45900baa8e8212023ce329"}
# tracked by this item: bytes + sha256 at recording time. "grow" = a live log another task appends to (floor only).
FILES = {
    "briefs/agy_audit_20261025.md": {"bytes": 4006, "sha256": "216af3237cc0d84bc39dd01a6ca589bddf731a0045b814dc6fc81d85adba8b3f",
                                     "why": "the brief the MAX block cites (Antigravity audit, Derrick 2026-10-25 8:14 AM CT)"},
    "briefs/agy_audit_20261025_report.md": {"bytes": 9568, "sha256": "52dafa788f68b8588f2639087af281c9d665f7901fd882fa8cb6b0c9c745a6a6",
                                            "why": "the report fix_plan names as Max's read of Antigravity's report"},
    "briefs/agy_audit_20261025.out.txt": {"bytes": 17060, "sha256": "71d1d46f3ec82a457fe42cbba1e4209519aac56a0c8c8fdc8c6f620308e78dcf",
                                          "why": "its run record - briefs/agy_llamaswap_setup_20261024.out.txt is the tracked precedent"},
    "briefs/agy_audit_run.ps1": {"bytes": 452, "sha256": "d28e2fafd3b755b408748401fbf3fec1556570c536d05893af4e879bb702b041",
                                 "why": "the exact agy command that ran the brief (precedent: briefs/agy_llamaswap_run.ps1)"},
    "briefs/agy_monitor_run.ps1": {"bytes": 443, "sha256": "39295c34cb2692c26b14c23848f6fb258e33118e6324ad8b3484d6fb06bdab29",
                                   "why": "the ForgeAgyMonitor scheduled-task action payload (a running task's command is an artifact)"},
    "briefs/agy_monitor.out.txt": {"bytes": 44046, "sha256": None, "grow": True,
                                   "why": "the watchdog's append-only log, written 2026-10-25 15:12:12 CT while ForgeAgyMonitor=Ready; "
                                          "a fixed sha would fail on its next run, so the record is a floor + monotonic growth"},
    BAK["dst"]: {"bytes": BAK["bytes"], "sha256": BAK["sha256"], "why": "the pre-MONITOR monitor brief: 1,808 B that exist in NO commit"},
    SNAP + "/inner_head.txt": {"bytes": 301, "sha256": "783d8a3fc51ca98c5a6d309bfbe69bb4462c9f70ee9dda3cb7cd0fc86f37fa3e",
                               "why": "the inner repo's HEAD (sha, author, date, subject) before the gitlink left the index"},
    SNAP + "/inner_status.txt": {"bytes": 127, "sha256": "8f09a992b0a84d395dd59482d329fa0a5d445fbc906e8af9d63117a7bf3575a4",
                                 "why": "the 6 rows that tree reports - the 2026-10-24 work state, now a record"},
    SNAP + "/working-2026-10-24.diff": {"bytes": 21416, "sha256": "c4ad29040531ea06da105ea055140837001425fa1a7f204bd7e786d8268b398d",
                                        "why": "185 insertions (prompt-cache incremental resume, caps 20000/16000 -> 80000/70000): "
                                               "the only copy of that code was a Chrome work copy"},
    SNAP + "/test_prompt-cache-incremental.test.js": {"bytes": 5433, "sha256": "16f35972ef0353b4b4846a98c73d240a111d588a5cd48ef1713600c4a2246362",
                                                     "why": "the test for that patch, untracked in the inner repo = L8 litter"},
    SNAP + "/tree_manifest.json": {"bytes": 39230, "sha256": "0246a5621ea265da5f5ca109f82bb7c4cd71e7a7189cce8c61d107df18c1de8a",
                                   "why": "path + bytes + sha256 of all 229 files of the installed extension (the 0.3 MANIFEST shape)"},
}
DISPOSITIONS = [
    (ZIP["path"], "keep-tracked", "already tracked at 21,935,298 B; 0.8 re-measures the sha256 and confirms "
                                  "fix_plan 2.0c's recorded `cf15deb6...9b20` against the bytes on disk"),
    ("incoming/gmd-dl-ext-2.5.6", "untrack+ignore", "gitlink with no .gitmodules, inner repo has no remote, so no clone restores it; "
                                                     "the zip == this tree byte-for-byte (check 8), so the tree is a work copy"),
    (BAK["src"], "move", "AGENTS.md bars .bak in a git repo, and here git history is NOT the backup: the bytes move to "
                         + BAK["dst"] + " and the .bak is deleted"),
] + [(p, "commit", FILES[p]["why"]) for p in FILES] + [
    ("notes/hc15_audit/ab_seed_%02d.json" % i, "drop", "--ab-selftest probe output; the builder now writes seeds in a temp dir "
     "(check 11), so this file regenerates on demand and is not an artifact") for i in range(20)
] + [
    ("notes/ali08_git_clean_check.py", "commit", "this gate (0.8's measurement)"),
    ("notes/git_status_cleanup_20261025.md", "commit", "the per-file disposition record, generated from the data above"),
    ("notes/gmd_ext_20261024.md", "commit", "what the 2026-10-24 extension patch is, and how to rebuild/verify the tree"),
    (".gitignore", "commit", "the one new ignore rule and its reason"),
    ("notes/ali02_citation_check.py", "commit", "0.7's S3 seed borrowed ab_seed_00.json; it now seeds its own fixture"),
    ("notes/hc15_anchor_fix_build.py", "commit", "ab_selftest writes its seeds in a temp dir and removes them"),
]
CLASSES = ("commit", "drop", "move", "untrack+ignore", "keep-tracked")


def g(repo, args, binary=False):
    if binary:
        return subprocess.run(["git", "-C", repo] + args, capture_output=True).stdout          # raw bytes
    return subprocess.run(["git", "-C", repo] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def status_rows(repo):
    r = g(repo, ["status", "--porcelain"])
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def rows_of(disp):
    return [d[0] for d in disp]


def clean_check(repos=CLEAN_REPOS):
    """The rows 0.8 owns. `C:/AI/director` is in INFO_REPOS: this item writes no file there, and it carried 322
    rows before the pass began (its own runtime trees), so a gate that failed on it would be reporting someone
    else's surface - the count is printed, never a finding. L17: the scope of a rule IS part of the rule."""
    return {r: status_rows(r) for r in repos if status_rows(r)}


def info_rows():
    return {r: len(status_rows(r)) for r in INFO_REPOS}


def commit_ok(p, rec):
    """Tracked, and the bytes on disk carry the recorded identity (grow-only for a live append log)."""
    abs_p = os.path.join(W, p.replace("/", os.sep))
    if not is_tracked(abs_p):
        return "not in git ls-files"
    if not os.path.isfile(abs_p):
        return "tracked but not on disk"
    n = os.path.getsize(abs_p)
    if rec.get("grow"):
        return None if n >= rec["bytes"] else "shrank below the recorded floor %d" % rec["bytes"]
    if n != rec["bytes"]:
        return "bytes %d != recorded %d" % (n, rec["bytes"])
    if rec.get("sha256") and sha(abs_p) != rec["sha256"]:
        return "sha256 != recorded"
    return None


def untrack_check(path, rule, gi_lines, in_index):
    """2d. Pure over recorded + measured inputs, so every half of the rule can be seeded: out of the index, an
    exact ignore rule, a reason line that says why, and the durable record named (checks 3/5 prove the zip
    reproduces the tree, so removing the gitlink loses nothing)."""
    bad = []
    if in_index:
        bad.append("UNTRACK %s: still in the index" % path)
    if not rule:
        bad.append("UNTRACK %s: git declares it not ignored" % path)
    elif path + "/" not in gi_lines:
        bad.append("UNTRACK %s: .gitignore carries no exact rule for it" % path)
    elif not any(l.startswith("#") and "zip IS this tree" in l for l in gi_lines):
        bad.append("UNTRACK %s: the ignore rule carries no reason line" % path)
    return bad


def dispositions(disp=DISPOSITIONS, bak=BAK, gi_path=os.path.join(W, ".gitignore")):
    """One line per disposition: what the record claims, re-measured against disk."""
    ident = dict(FILES)
    ident[ZIP["path"]] = {"bytes": ZIP["bytes"], "sha256": ZIP["sha256"]}
    gi = open(gi_path, encoding="utf-8").read().split("\n")
    bad = []
    for p, cls, why in disp:
        if cls not in CLASSES:
            bad.append("2 LEDGER %s: class %s is not one of %s" % (p, cls, CLASSES))
            continue
        abs_p = os.path.join(W, p.replace("/", os.sep))
        if cls in ("commit", "keep-tracked"):
            rec = ident.get(p)
            if rec is None:
                if not (is_tracked(abs_p) and os.path.isfile(abs_p)):
                    bad.append("2a COMMIT %s: not tracked / not on disk" % p)
            else:
                r = commit_ok(p, rec)
                if r:
                    bad.append("2a COMMIT %s: %s" % (p, r))
        elif cls == "drop":
            if os.path.exists(abs_p) or is_tracked(abs_p):
                bad.append("2b DROP %s: still on disk or in the index" % p)
        elif cls == "move":
            tgt = os.path.join(W, bak["dst"].replace("/", os.sep))
            rec = {"bytes": bak["bytes"], "sha256": bak["sha256"]}
            if os.path.exists(abs_p):
                bad.append("2c MOVE %s: the .bak is still in the tree" % p)
            if not p.endswith(".pre-20261025.bak"):
                bad.append("2c MOVE %s: the row names no .bak source" % p)
            r = commit_ok(bak["dst"], rec) if os.path.isfile(tgt) else "target not tracked/on disk"
            if r:
                bad.append("2c MOVE %s -> %s: %s" % (p, bak["dst"], r))
        elif cls == "untrack+ignore":
            bad += untrack_check(p, ignore_rule(os.path.join(abs_p, "content.js")), gi,
                                 bool(g(W, ["ls-files", "--", p]).stdout.strip()))
    missing = [p for p in SEED_ROWS if p not in rows_of(disp)]
    if missing:
        bad.append("2 LEDGER %s of the 28 measured rows are not dispositioned (%s)" % (len(missing), missing[:2]))
    unknown = [p for p, c, _ in disp if not (os.path.lexists(os.path.join(W, p.replace("/", os.sep)))
                                             or is_tracked(os.path.join(W, p.replace("/", os.sep)))
                                             or c in ("drop", "move"))]
    if unknown:
        bad.append("2 LEDGER %d disposition rows name a path that is neither on disk nor tracked (%s)"
                   % (len(unknown), unknown[:2]))
    return bad


def zip_check(rec=ZIP):
    p = os.path.join(W, rec["path"].replace("/", os.sep))
    bad = []
    if os.path.getsize(p) != rec["bytes"] or sha(p) != rec["sha256"]:
        bad.append("ZIP bytes/sha256 do not match the record")
    blob = g(W, ["ls-files", "-s", "--", rec["path"]]).stdout.split()
    head = g(W, ["cat-file", "blob", "HEAD:" + rec["path"]], binary=True)
    if len(blob) < 2 or blob[1] != rec["blob"]:
        bad.append("the index blob is not the recorded one")
    elif hashlib.sha256(head).hexdigest() != rec["sha256"]:
        bad.append("the HEAD blob bytes != the working copy (the zip moved under git)")
    return bad


def unzip_to(tmp):
    ex = os.path.join(tmp, "gmd-dl-ext-2.5.6")
    zipfile.ZipFile(os.path.join(W, ZIP["path"].replace("/", os.sep))).extractall(tmp)
    return ex


def tree_manifest():
    man = json.load(open(os.path.join(W, SNAP, "tree_manifest.json"), encoding="utf-8"))
    return man["meta"], {r["path"]: r for r in man["rows"]}


def tree_check(rows, live=W, ex=None):
    """Every recorded path: bytes + sha256 equal in the live tree AND in a fresh unzip of the tracked zip."""
    bad = []
    live_root = os.path.join(live, "incoming/gmd-dl-ext-2.5.6".replace("/", os.sep))
    for p, r in sorted(rows.items()):
        for root, tag in ((live_root, "live"), (ex, "zip")):
            f = os.path.join(root, p.replace("/", os.sep))
            if not os.path.isfile(f):
                bad.append("%s missing in %s: %s" % (tag, os.path.basename(root), p))
            elif os.path.getsize(f) != r["bytes"] or sha(f) != r["sha256"]:
                bad.append("%s bytes/sha differ from the record: %s" % (tag, p))
    return bad[:6]


def patch_check(diff_bytes, ex, live_root=None):
    """Replay: clean the inner HEAD tree, apply the recorded diff, require the 4 patched files == live bytes."""
    live_root = live_root or os.path.join(W, "incoming/gmd-dl-ext-2.5.6".replace("/", os.sep))
    for args in (["-c", "core.autocrlf=false", "checkout", "--", "."], ["clean", "-fd", "-q"]):
        if g(ex, args).returncode != 0:
            return ["replay setup failed: git %s" % " ".join(args)]
    pf = os.path.join(os.path.dirname(ex), "recorded.diff")
    open(pf, "wb").write(diff_bytes)
    if g(ex, ["-c", "core.autocrlf=false", "apply", "--check", pf]).returncode != 0:
        return ["the recorded diff does not apply to the clean inner HEAD tree (%s)" % ZIP["inner_head"][:12]]
    if g(ex, ["-c", "core.autocrlf=false", "apply", pf]).returncode != 0:
        return ["git apply failed on the clean tree"]
    bad = []
    for f in ("content.js", "src/grok-assets.js", "src/utils.js", "test/run-all.sh"):
        a, b = os.path.join(ex, f.replace("/", os.sep)), os.path.join(live_root, f.replace("/", os.sep))
        if not (os.path.isfile(a) and os.path.isfile(b) and sha(a) == sha(b)):
            bad.append("replayed %s != the live file" % f)
    return bad


def record_check(recorded, ex):
    now = g(ex, ["status", "--porcelain"]).stdout
    return [] if now == recorded else ["the extracted zip tree's status != the recorded status rows"]


def no_write_check(src=None, old_line='open(os.path.join(AUD, "ab_seed_%02d.json" % i), "w", encoding="utf-8")'):
    """The static half of check 11: ab_selftest must write nothing under notes/ and must open a temp dir.
    `src` is a source clone, so the OLD wiring can be restored and the detector proven to fire there."""
    src = src if src is not None else open(BUILDER, encoding="utf-8").read()
    i = src.index("def ab_selftest(")
    body = src[i:src.index("\ndef main(")]
    bad = []
    if "tempfile.mkdtemp" not in body:
        bad.append("ab_selftest opens no temp dir")
    if re.search(r'os\.path\.join\(\s*AUD\s*,\s*"ab_seed', body):
        bad.append("ab_selftest writes an ab_seed file under notes/ (the 0.8 litter shape)")
    litter = sorted(f for f in os.listdir(AUD) if f.startswith("ab_seed")) if os.path.isdir(AUD) else []
    if litter:
        bad.append("notes/hc15_audit carries %d ab_seed files: %s" % (len(litter), litter[:2]))
    return bad


def clean_report():
    rows = clean_check()
    info = info_rows()
    if info:
        print("INFO out-of-scope row counts " + json.dumps(info, sort_keys=True) +
              " - measured, never a finding of 0.8 (no file of this item lives in those repos)")
    return [{"repo": r, "rows": len(v)} for r, v in sorted(rows.items())]


CK = [("1 CLEAN", lambda a: clean_report()),
      ("2 LEDGER", lambda a: dispositions()),
      ("3 ZIP", lambda a: zip_check()),
      ("4 NO-WRITE", lambda a: no_write_check())]
HEAVY = [("5 TREE==ZIP", lambda a: tree_check(a["rows"], ex=a["ex"])),
         # RECORD runs on the PRISTINE extracted tree; PATCH is the mutating check (checkout + clean + apply),
         # so the order is part of the measurement, not an implementation detail.
         ("6 RECORD", lambda a: record_check(a["recorded"], a["ex"])),
         ("7 PATCH", lambda a: patch_check(a["diff"], a["ex"]))]


def build_heavy():
    man, rows = tree_manifest()
    tmp = tempfile.mkdtemp(prefix="ali08_probe_")
    try:
        ex = unzip_to(tmp)
        return {"rows": rows, "ex": ex, "man": man,
                "diff": open(os.path.join(W, SNAP, "working-2026-10-24.diff"), "rb").read(),
                "recorded": open(os.path.join(W, SNAP, "inner_status.txt"), encoding="utf-8").read()}
    finally:
        pass


def check_all(label="", heavy=True):
    fails = []
    for name, fn in CK:
        got = fn(None)
        print(("FAIL " + name + " " + json.dumps(got, ensure_ascii=False)[:400]) if got else "PASS " + name)
        fails += [(name, g) for g in got]
    art = build_heavy() if heavy else None
    if heavy:
        try:
            for name, fn in HEAVY:
                got = fn(art)
                print(("FAIL " + name + " " + json.dumps(got, ensure_ascii=False)[:400]) if got else "PASS " + name)
                fails += [(name, g) for g in got]
        finally:
            shutil.rmtree(os.path.dirname(art["ex"]), ignore_errors=True)
    n = len(CK) + (len(HEAVY) if heavy else 0)
    print("CHECKS %s %s" % (label, ("ALL %d PASS" % n) if not fails else "FAIL %d: %s" % (len(fails), [f[0] for f in fails])))
    return fails


def selftest():
    """Every detector must fire on its own seed, and 0 on the real tree (L10: a green check that cannot fail
    is worthless). Seeds mutate the RECORDED data - a stale record is exactly the fault 0.8 exists to catch -
    and, for the two filesystem detectors, write one file each and delete it in a finally."""
    real = check_all(label="real")
    fired, silent = [], []

    def seed(name, got):
        (fired if got else silent).append(name + (" " + json.dumps(got, ensure_ascii=False)[:160] if got else ""))

    def seed_neg(name, got):
        # negative control: the detector MUST stay silent here, so silence is the seed firing and any
        # finding is the fault. Counted in the same list so a pass cannot hide a detector that always fires.
        seed(name + " [negative control]",
             ["stays silent on the real artifact, as required"] if not got else ["UNEXPECTED: " + x for x in got])
    # 1 CLEAN: a stray untracked file in the repo is exactly the row 0.8 cleans
    stray = os.path.join(W, "notes", "zz_08_gate_seed_untracked.txt")
    try:
        open(stray, "w", encoding="utf-8").write("0.8 selftest seed - deleted in a finally\n")
        seed("1 CLEAN stray-file", clean_check((W,)).get(W))
    finally:
        os.remove(stray)
    # 2 LEDGER: a dropped disposition row, an unknown class
    d = list(DISPOSITIONS)
    del d[3]
    seed("2 LEDGER row dropped", [x for x in dispositions(d) if x.startswith("2 LEDGER")])
    d = [(p, "committee", w) for p, _, w in DISPOSITIONS[:4]]
    seed("2 LEDGER bad class", [x for x in dispositions(d) if "class" in x])
    # 2a COMMIT: a stale sha, a size drift
    k = "briefs/agy_audit_20261025_report.md"
    seed("2a COMMIT stale sha", commit_ok(k, dict(FILES[k], sha256="0" * 64)))
    k2 = "briefs/agy_monitor_run.ps1"
    seed("2a COMMIT bytes drift", commit_ok(k2, dict(FILES[k2], bytes=FILES[k2]["bytes"] + 1)))
    seed("2a COMMIT grow floor", commit_ok("briefs/agy_monitor.out.txt", dict(FILES["briefs/agy_monitor.out.txt"],
                                                                            bytes=os.path.getsize(os.path.join(W, "briefs/agy_monitor.out.txt")) + 10)))
    # 2b DROP: the litter restored
    litter = os.path.join(AUD, "ab_seed_00.json")
    try:
        open(litter, "w", encoding="utf-8").write("{}\n")
        seed("2b DROP litter restored", [x for x in dispositions() if x.startswith("2b DROP")])
    finally:
        os.remove(litter)
    # 2c MOVE: a stale recorded sha, and a .bak that came back
    seed("2c MOVE stale sha", [x for x in dispositions([d for d in DISPOSITIONS if d[1] == "move"],
                                                       bak=dict(BAK, sha256="0" * 64)) if x.startswith("2c")])
    seed("2c MOVE target missing", [x for x in dispositions([d for d in DISPOSITIONS if d[1] == "move"],
                                                           bak=dict(BAK, dst="notes/zz_no_target.md"))
                                    if x.startswith("2c")])
    # 2d UNTRACK: pure over its inputs, so every half of the rule is provable
    gi = [l for l in open(os.path.join(W, ".gitignore"), encoding="utf-8").read().split("\n")]
    seed("2d UNTRACK back in the index", untrack_check("incoming/gmd-dl-ext-2.5.6", "x", gi, True))
    seed("2d UNTRACK no ignore rule", untrack_check("incoming/gmd-dl-ext-2.5.6", "", gi, False))
    seed("2d UNTRACK no exact rule", untrack_check("incoming/gmd-dl-ext-2.5.6", "x", [l for l in gi if not l.endswith("gmd-dl-ext-2.5.6/")], False))
    seed("2d UNTRACK reason line gone", untrack_check("incoming/gmd-dl-ext-2.5.6", "x",
                                                      [l for l in gi if "zip IS this tree" not in l], False))
    # the negative control: the real rule + reason must read CLEAN, so the detector is not just always-firing
    seed_neg("2d UNTRACK rule+reason", untrack_check("incoming/gmd-dl-ext-2.5.6",
                                                     "1:.gitignore:24:gmd-dl-ext-2.5.6/\tC:/AI/community/incoming/gmd-dl-ext-2.5.6/content.js",
                                                     gi, False))
    # 4 NO-WRITE: the OLD wiring restored in a source clone
    src = open(BUILDER, encoding="utf-8").read()
    old = src.replace('open(os.path.join(tmp, "ab_seed_%02d.json" % i), "w", encoding="utf-8")',
                      'open(os.path.join(AUD, "ab_seed_%02d.json" % i), "w", encoding="utf-8")')
    seed("4 NO-WRITE old AUD wiring", [x for x in no_write_check(old) if "under notes/" in x])
    seed("4 NO-WRITE no temp dir", [x for x in no_write_check(src.replace("tempfile.mkdtemp", "no_tempfile"))
                                    if "no temp dir" in x])
    try:
        art = build_heavy()
        try:
            # 3 ZIP: a stale recorded sha
            seed("3 ZIP stale sha", zip_check(dict(ZIP, sha256="0" * 64)))
            man, rows = tree_manifest()
            rows = dict(rows)
            one = sorted(rows)[0]
            rows[one] = dict(rows[one], sha256="0" * 64)
            seed("5 TREE==ZIP one file tampered", tree_check(rows, ex=art["ex"]))
            rows2 = {"zz/not_a_file.js": {"bytes": 1, "sha256": "0" * 64}}
            seed("5 TREE==ZIP manifest file missing", tree_check(rows2, ex=art["ex"]))
            # 7 PATCH: drop the last hunk
            seed("7 PATCH truncated diff", patch_check(b"\n@@".join(art["diff"].split(b"\n@@")[:-1]),
                                                       unzip_to(os.path.dirname(art["ex"]) + "_2")))
            # 6 RECORD: a status row dropped
            seed("6 RECORD status row dropped", record_check(art["recorded"].split("\n", 2)[2], art["ex"]))
        finally:
            shutil.rmtree(os.path.dirname(art["ex"]), ignore_errors=True)
            shutil.rmtree(os.path.dirname(art["ex"]) + "_2", ignore_errors=True)
    except Exception as e:
        silent.append("HEAVY seed pass crashed: %r" % (e,))
    need = 21  # measured 2026-10-25: 20 fault seeds + 1 negative control; a seed that stops firing fails the gate
    print("\nseeds fired=%d silent=%d (need >=%d silent=0; real-tree problems=%d)" % (len(fired), len(silent), need, len(real)))
    for s in silent:
        print("SILENT_SEED " + s)
    print("ALI08_SELFTEST " + ("OK" if not silent and not real else
                               "DIRTY silent=%d real=%d" % (len(silent), len(real))))
    return 0 if (not silent and not real) else 1


def write_note(path=NOTE):
    """The disposition record, generated FROM the data the gate checks - the note cannot drift from the gate."""
    L = ["# 0.8 - every row of `git status`, decided per file (measured %s)" % MEASURED, "",
         "`C:/AI/community` carried **28** rows in `git status --porcelain` when 0.8 started: 1 modified gitlink, "
         "7 untracked `briefs/` files, 20 untracked `notes/hc15_audit/ab_seed_*.json`. L8 is the rule that makes "
         "this an item: any untracked file dies at the pass boundary, so a row is either work that must become "
         "durable or litter a generator must stop writing. `git add -A` would commit the 20 probe files into the "
         "surface Derrick reads and leave the gitlink's real defect in place. Every row below was opened.", "",
         "Classes: `commit` = the artifact, tracked and re-measured at its bytes/sha256; `drop` = generated probe "
         "output, deleted, and the generator now writes it to a temp dir; `move` = bytes that exist in no commit "
         "moved to a snapshot path; `untrack+ignore` = a work copy, out of the index, ignored, with its durable "
         "record named and verified; `keep-tracked` = already tracked, identity re-measured.", "",
         "| path | class | what the record claims | how the gate proves it |", "|---|---|---|---|"]
    proof = {"commit": "in `git ls-files`, bytes + sha256 equal the record (the AGY watchdog log: grow-only, "
                       "it is appended by the ForgeAgyMonitor task)",
             "keep-tracked": "bytes + sha256 equal the record; the index blob == HEAD blob == disk",
             "drop": "absent from disk and from the index, and `notes/hc15_audit` holds 0 `ab_seed*` files",
             "move": "the `.bak` is gone, the snapshot path is tracked at the recorded sha256",
             "untrack+ignore": "not in the index, `git check-ignore` resolves the rule, `.gitignore` carries the "
                               "reason line, and the zip reproduces the whole tree byte-for-byte"}
    for p, cls, why in DISPOSITIONS:
        L.append("| `%s` | %s | %s | %s |" % (p, cls, why.replace("|", "/"), proof[cls].replace("|", "/")))
    L += ["", "## The three non-obvious calls",
          "1. **The gitlink is not a submodule.** `incoming/gmd-dl-ext-2.5.6` is in the index as mode 160000 at "
          "`%s`, the repo has **no `.gitmodules`**, and the inner repo has **no remote** - so no clone of "
          "C:/AI/community can restore it, and every write inside the unpacked extension is a permanent ` M` row. "
          "Measured: a fresh unzip of the tracked `%s` (%s B, sha256 `%s`) is byte-identical to the unpacked tree "
          "for all %d files (the only byte that ever differs is `.git/index`, which any `git status` rewrites), so "
          "the zip IS the durable record and the tree is a work copy. `%s`" % (
              ZIP["inner_head"], ZIP["path"], "{:,}".format(ZIP["bytes"]), ZIP["sha256"], ZIP["tree_files"], ZIP["note"]) + ".",
          "2. **The 2026-10-24 code changes lived only in a Chrome work copy.** The inner repo's working tree "
          "carries 185 insertions over its HEAD (prompt-cache incremental resume via `grok_prompt_conv_done`, "
          "`PROMPT_CACHE_MAX_ENTRIES/PRUNE_TO` 20000/16000 -> 80000/70000 after a 31.6k-asset library evicted "
          "entries it had just fetched) plus an untracked 5,433 B test. All of it is now in `%s/`: the HEAD line, "
          "the 6 status rows, the full diff, the test, and a 229-file per-path manifest. The gate proves the diff "
          "**replays**: clean the inner HEAD tree, `git apply` the recorded diff, and the 4 patched files match "
          "the live tree byte-for-byte (seed: drop the last hunk, the detector fires)." % SNAP,
          "3. **The `.bak` was not redundant.** AGENTS.md bars `.bak` copies in a git repo because git history is "
          "the backup, so 0.8 checked: `briefs/agy_monitor.md` entered the repo only at `e791bb6` (the MONITOR "
          "commit), whose blob is a different 1,456 B, and the file does not exist in its parent. The pre-MONITOR "
          "brief - %d B, sha256 `%s` - is in **no commit**. Its bytes move to `%s`; the `.bak` is deleted. "
          "Nothing was thrown away." % (BAK["bytes"], BAK["sha256"], BAK["dst"]),
          "", "## What the 20 seed files are",
          "`notes/hc15_anchor_fix_build.py --ab-selftest` seeds 20 faults into clones of the NOW-P2 A/B artifacts. "
          "2.2 kept its seeds inside `graph_state()` clones and wrote nothing; NOW-P2 wrote 20 JSONs next to the "
          "metrics and the contact sheet, i.e. in the human-reviewed surface (the 2.7b LITTER row calls the same "
          "shape red, review_folder_flags MANIFEST_UNCLEAN problems=11). The builder now writes every seed - the "
          "JSONs and the blank-sheet PNG - into a `tempfile.mkdtemp` it removes in a `finally`; the seeds still "
          "fire 20/20 and the real tree stays clean. 0.7's plan gate borrowed `ab_seed_00.json` as its untracked-"
          "path fixture; that seed now writes and deletes its own `notes/zz_08_seed_untracked.json`.",
          "", "## The briefs",
          "6 files are committed: the audit brief, its report (`fix_plan` names it as Max's read of Antigravity's "
          "report), the two run records, the two `agy` runner scripts. 8 files in `briefs/` are already tracked, "
          "2 of them `.out.txt` run records, so this is the folder's own convention, not a new one. "
          "`agy_monitor.out.txt` is the watchdog's append-only log: measured at 44,046 B, written 2026-10-25 "
          "15:12:12 CT while the `ForgeAgyMonitor` task sits `Ready`, so the gate records it as a floor and "
          "requires growth - a fixed sha would fail on the next scheduled run. `*.log` is already ignored "
          "(`.gitignore:15`), which is why the four `.log` siblings never appeared as rows.",
          "", "## A citation whose root is wrong (found while running the standing gates)",
          "`rt_window_probe.py` - the RENDER-TIMEOUT gate - is tracked at **"
          "C:/Users/derek/5slock/ralph-community/notes/rt_window_probe.py** (16,066 B, 13 checks, `--check` CLEAN "
          "this pass). 21 citations use the relative `notes/rt_window_probe.py`, which resolves from "
          "ralph-community's cwd, and **1** cites `C:/AI/community/notes/rt_window_probe.py` - a path that does not "
          "exist (`git log --all` in C:/AI/community: 0 rows). The two repos each have their own `notes/`, so a "
          "relative citation is a choice of repo (L3's cwd-relative class, L4's cite-only-what-you-read). 0.8 "
          "corrects the one wrong-root string in `notes/plans/render-timeout.md:37` and writes its own commands "
          "with the absolute ralph-community root.",
          "", "## Done-when, measured",
          "`python C:/AI/community/notes/ali08_git_clean_check.py` -> all 7 checks pass (the 11 claims above), and "
          "`git status --porcelain` is 0 rows in `C:/AI/community` and `ralph-community` (`C:/AI/director`'s count "
          "is printed as out-of-scope context); "
          "`--selftest` fires 21 seeds = 20 faults + 1 negative control (a stray file moves the row count 0 -> 1, a dropped disposition row, an "
          "unknown class, a stale sha, a size drift, a grow-floor regression, litter restored, a `.bak` that came "
          "back, a missing move target, an ignore rule with no exact pattern / no reason line / a re-tracked "
          "gitlink, the OLD `AUD`-writing `ab_selftest` restored in a clone, a no-temp-dir builder, a stale zip "
          "sha, a tampered tree file, a manifest row naming a missing file, a truncated patch, a status record "
          "with a row dropped) and 0 problems on the real tree.", ""]
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("WROTE %s (%d B, %d disposition rows)" % (path, os.path.getsize(path), len(DISPOSITIONS)))
    return 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if mode == "--check":
        return 1 if check_all(label="real") else 0
    if mode == "--selftest":
        return selftest()
    if mode == "--note":
        return write_note()
    print("usage: ali08_git_clean_check.py [--check|--selftest|--note]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
