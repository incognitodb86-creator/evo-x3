"""MAX block items 2-3 (Max brief 10:50 CT, Derrick's go 10:48 CT) - START + item 2.

Item 2: git rm the 12 files 8a0707e added for the failed small-helper job 2, and commit that as a NEW commit.
No reset, no amend, no rebase, no force-push - 8a0707e stays in history, the removal is a normal commit on top.

Append-only on notes/actions.log: this appends after the last line and never rewrites the file, so blank
separators in the log stay as they are (the earlier records used a filtered join; not repeated here).

Verifies before committing: every target is tracked, exists, is clean vs HEAD, and was ADDED by 8a0707e.
"""
import datetime
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REPO = r"C:\Users\derek\5slock\ralph-community"
LOG = r"C:\AI\community\notes\actions.log"
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
ADDER = "8a0707e"
TARGETS = ["notes/sh_job2_audit.py", "notes/sh_job2_collect.py", "notes/sh_job2_dump_sheet.py",
           "notes/sh_job2_llm.py", "notes/sh_job2_metrics.py", "notes/2026-10-28-small-helper-job2-DONE.md",
           "notes/2026-10-28-p15v2-scoring-rows.csv", "notes/2026-10-28-p15v2-scoring-rows.json",
           "notes/2026-10-28-p15v2-scoring-rows-run1-copy.csv", "notes/2026-10-28-p15v2-scoring-rows-run1-copy.json",
           "notes/2026-10-28-p15v2-scoring-rows-run2-select.csv", "notes/2026-10-28-p15v2-scoring-rows-run2-select.json"]
MSG = ("Remove the failed small-helper job-2 files (MAX block item 2, Max brief 10:50 CT on Derrick's go 10:48 CT)\n\n"
       "git rm of the 12 files %s added on Oct 28: notes/sh_job2_audit.py, sh_job2_collect.py, sh_job2_dump_sheet.py,\n"
       "sh_job2_llm.py, sh_job2_metrics.py, notes/2026-10-28-small-helper-job2-DONE.md and the p15v2 scoring-rows\n"
       "csv/json set (rows, run1-copy, run2-select). The job is closed as a failure; the files stay in history at\n"
       "%s - this is a new commit on top, no reset, no amend, no rebase, no force-push." % (ADDER, ADDER))

START = ("%s | MAX items 2-3 START (Max brief 10:50 CT, Derrick's go 10:48 CT) | item 2: git rm the 12 job-2 files "
         "%s added, new commit only (no reset/amend/rebase/force-push); item 3: fix notes\\2026-10-28-handoff-from-max.md "
         "section 4 so the edits already committed in %s and 95658b8 are not called uncommitted (backup first, then "
         "commit) | no GPU, no render, no model load, no queue" % (NOW, ADDER, ADDER))


def git(*a):
    q = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
    out = (q.stdout or "") + (q.stderr or "")
    return q.returncode, out.strip()


def append_log(line):
    data = open(LOG, "rb").read()
    if line[:19] in data.decode("utf-8"):
        print("actions.log: this START already present (idempotent)")
        return
    if not data.endswith(b"\r\n"):
        data += b"\r\n"
    open(LOG, "wb").write(data + (line + "\r\n").encode("utf-8"))
    print("actions.log: START appended (append-only, %d B -> %d B)" % (len(data), len(data) + len(line) + 2))


lines = [l for l in open(LOG, "rb").read().decode("utf-8").split("\r\n") if l.strip()]
if not any("MAX items 2-3 START" in l for l in lines):
    append_log(START)

# verify the 12 targets
bad = []
for t in TARGETS:
    rc, tracked = git("ls-files", "--", t)
    rc, st = git("status", "--porcelain", "--", t)
    rc, added = git("show", "--name-status", "--format=", ADDER)
    was = [l for l in added.split("\n") if l.split("\t")[-1] == t]
    ok = bool(tracked.strip()) and os.path.exists(os.path.join(REPO, t)) and not st.strip() \
        and was and was[0].startswith("A")
    print("%-58s tracked=%s exists=%s clean=%s added-by-8a0707e=%s"
          % (t, bool(tracked.strip()), os.path.exists(os.path.join(REPO, t)), not st.strip(),
             bool(was and was[0].startswith("A"))))
    if not ok:
        bad.append(t)
assert len(TARGETS) == 12, "the list must be exactly the 12 files in the brief"
if bad:
    print("REFUSING to commit, preconditions failed for: %s" % bad)
    sys.exit(1)

# idempotent: is the removal already committed?
rc, log = git("log", "--oneline", "-3")
if "Remove the failed small-helper job-2 files" in log:
    rc, sha = git("log", "--format=%H", "-1", "--grep=Remove the failed small-helper job-2 files")
    print("item 2 already committed (idempotent): %s" % sha)
    sys.exit(0)

rc, out = git("rm", "--", *TARGETS)
print("git rm rc=%d" % rc)
print("\n".join(out.split("\n")[:14]))
rc, out = git("diff", "--cached", "--name-status")
staged = out.split("\n")
assert len(staged) == 12 and all(l.startswith("D") for l in staged), "staged set is not 12 deletions: %r" % staged
rc, out = git("commit", "-q", "-m", MSG)
print("commit rc=%d %s" % (rc, out))
rc, sha = git("log", "--format=%h %H", "-1")
print("NEW COMMIT:", sha)
rc, out = git("show", "--stat", "--oneline", "HEAD")
print("\n".join(out.split("\n")[:6]))
rc, out = git("status", "--porcelain")
print("working tree after the commit (Max's files must stay):")
print("\n".join(l for l in out.split("\n") if l.startswith(" M")))
missing = [t for t in TARGETS if os.path.exists(os.path.join(REPO, t))]
print("files still on disk after git rm (must be none):", missing or "none")
print("history intact: 8a0707e still reachable ->", git("merge-base", "--is-ancestor", ADDER, "HEAD")[0] == 0)
sys.exit(0)
