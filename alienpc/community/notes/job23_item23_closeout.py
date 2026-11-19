"""MAX block items 2-3 close-out (Max brief 10:50 CT, Derrick's go 10:48 CT).

Ticks items 2 and 3 on their own single physical lines with the commit SHAs as evidence, appends one DONE line to
C:/AI/community/notes/actions.log (append-only, no rewriting of existing lines) and one line to
ralph-community/notes/progress.md. Backs up fix_plan.md first. Verifies after writing: 2 ticks, 1 line each, the
plan's line count and Max's other lines unchanged, no new non-ASCII, and the cited commits exist with the
file sets claimed. Idempotent.
"""
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
REPO = r"C:\Users\derek\5slock\ralph-community"
PLAN = Path(REPO + r"\fix_plan.md")
BAK = PLAN.with_name("fix_plan.md.bak-20261029-item23-tick")
LOG = Path(r"C:\AI\community\notes\actions.log")
PROG = Path(REPO + r"\notes\progress.md")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
RM_SHA = "9cae06e"
FIX_SHA = "987e49f"
ADDER = "8a0707e"
L67 = "95658b8"
TARGETS = ["notes/sh_job2_audit.py", "notes/sh_job2_collect.py", "notes/sh_job2_dump_sheet.py",
           "notes/sh_job2_llm.py", "notes/sh_job2_metrics.py", "notes/2026-10-28-small-helper-job2-DONE.md",
           "notes/2026-10-28-p15v2-scoring-rows.csv", "notes/2026-10-28-p15v2-scoring-rows.json",
           "notes/2026-10-28-p15v2-scoring-rows-run1-copy.csv", "notes/2026-10-28-p15v2-scoring-rows-run1-copy.json",
           "notes/2026-10-28-p15v2-scoring-rows-run2-select.csv", "notes/2026-10-28-p15v2-scoring-rows-run2-select.json"]
HANDBAK = REPO + r"\notes\2026-10-28-handoff-from-max.md.bak-20261029-item3"
HANDBAK_SHA8 = "71dfa47c"

TICK2 = ('  2. [x] job-2 file removal DONE %s: commit %s = git rm of exactly the 12 files %s added on Oct 28 '
         '(notes/sh_job2_audit.py, sh_job2_collect.py, sh_job2_dump_sheet.py, sh_job2_llm.py, sh_job2_metrics.py, '
         'notes/2026-10-28-small-helper-job2-DONE.md, notes/2026-10-28-p15v2-scoring-rows.csv/.json, '
         '-run1-copy.csv/.json, -run2-select.csv/.json); preconditions checked before staging (each target tracked, '
         'present, clean vs HEAD, and name-status A in %s), staged set = exactly 12 D entries, git show --name-status '
         '%s = 12 D and nothing else; NO reset, amend, rebase or force-push (git merge-base --is-ancestor %s HEAD = '
         'true, 8a0707e stays reachable, every byte recoverable with git show %s:<path>); Max\'s AGENTS.md/PROMPT.md/'
         'ralph.ps1 working-tree pair left untouched; no GPU, no render, no model load, no queue; script '
         'C:/AI/community/notes/job23_item2_record.py') % (NOW, RM_SHA, ADDER, ADDER, RM_SHA, ADDER, ADDER)

TICK3 = ('  3. [x] handoff-from-max.md section 4 FIXED DONE %s: commit %s on notes/2026-10-28-handoff-from-max.md, '
         'backup notes/2026-10-28-handoff-from-max.md.bak-20261029-item3 (sha8 %s = the measured pre-edit bytes, '
         '10536 B). The three Oct 28 "uncommitted" claims are corrected to the commits that contain the work: %s '
         '(M AGENTS.md, fix_plan.md, notes/p15_driver.py, notes/bk26_writer_batch.py; A the Oct 28 DONE notes, the '
         '.bak-20261028* files, sh_job2_*.py, verify_no_word_band_20261028.py and the p15v2 scoring-rows files) and '
         '%s (the line-67 writer-skill job). Proved against HEAD, not asserted: git grep -c word_count HEAD -- '
         'notes/p15_driver.py notes/bk26_writer_batch.py = 0 hits, "/ 80.0" present in both files, git grep -n '
         '"Word Count" HEAD -- notes/p15_writer_skill.md = no match. The section names the new removal commit %s for '
         'the job-2 set, keeps the Oct 28 disk inventory (sizes, backup names) as history, and labels the current '
         'M AGENTS.md / M PROMPT.md / M ralph.ps1 as a separate later Max edit, not the Oct 28 work and not '
         'Forge\'s to commit. No GPU, no render; script C:/AI/community/notes/job23_item3_backup.py') % (
    NOW, FIX_SHA, HANDBAK_SHA8, ADDER, L67, RM_SHA)

DONE = ("%s | MAX items 2-3 DONE | item 2: commit %s = git rm of the 12 job-2 files %s added "
        "(sh_job2_{audit,collect,dump_sheet,llm,metrics}.py, 2026-10-28-small-helper-job2-DONE.md, "
        "2026-10-28-p15v2-scoring-rows .csv/.json + run1-copy + run2-select); new commit only, history intact "
        "(git merge-base --is-ancestor %s HEAD = true). item 3: commit %s on notes/2026-10-28-handoff-from-max.md "
        "section 4 (backup .bak-20261029-item3 sha8 %s): the three Oct 28 uncommitted claims now name %s and %s, "
        "proved by git grep on HEAD (0 word_count hits, / 80.0 present, no Word Count self-check line), the removal "
        "commit %s is cited, the Oct 28 inventory stays as history, and Max's current AGENTS.md/PROMPT.md/ralph.ps1 "
        "edit is marked as his, not Oct 28 work. No GPU, no render, no model load, no queue. Ticked items 2-3 in "
        "fix_plan.md in the record commit that follows this line" % (NOW, RM_SHA, ADDER, ADDER, FIX_SHA,
                                                                     HANDBAK_SHA8, ADDER, L67, RM_SHA))

PROG_LINE = ("- %s MAX block items 2-3 DONE (Max brief 10:50 CT, Derrick's go 10:48 CT). Item 2: the 12 files %s "
             "added for the failed small-helper job 2 are removed by the NEW commit `%s` (git rm, no reset/amend/"
             "rebase/force-push; `%s` is still an ancestor and every file is recoverable with `git show %s:<path>`). "
             "Item 3: `notes/2026-10-28-handoff-from-max.md` section 4 no longer calls committed work uncommitted - "
             "the score-band edits (`notes/p15_driver.py`, `notes/bk26_writer_batch.py`), the Oct 28 `AGENTS.md` "
             "edits, the job-2 note, `sh_job2_*.py` and the p15v2 scoring-rows files are cited as `%s`, the line-67 "
             "job as `%s`, proved by `git grep` on HEAD (0 `word_count` hits, `/ 80.0` present, no `Word Count` "
             "self-check), with the removal commit `%s` named; backup `notes/2026-10-28-handoff-from-max.md."
             "bak-20261029-item3` (sha8 %s). MAX item 4 (U3) follows in its own record. No GPU, no render, no model "
             "load; Max's working tree untouched." % (NOW, ADDER, RM_SHA, ADDER, ADDER, ADDER, L67, RM_SHA,
                                                      HANDBAK_SHA8))


def nonascii(path):
    return [l for l in path.read_bytes().decode("utf-8").split("\r\n") if not all(ord(c) < 128 for c in l)]


def git(*a):
    q = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True)
    return ((q.stdout or "") + (q.stderr or "")).strip()


BASE = {p: len(nonascii(p)) for p in (LOG, PROG, PLAN)}

# --- ticks ---------------------------------------------------------------------------------------------
raw = PLAN.read_bytes()
if not BAK.exists():
    BAK.write_bytes(raw)
    print("backup -> %s (%d B)" % (BAK, len(raw)))
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert text.count("\n") == len(lines) - 1, "expected pure CRLF"
for n, tick, marker in ((2, TICK2, "job-2 file removal DONE"), (3, TICK3, "handoff-from-max.md section 4 FIXED DONE")):
    idx = [i for i, l in enumerate(lines) if l.startswith("  %d. [ ] " % n)]
    done = [i for i, l in enumerate(lines) if l.startswith("  %d. [x] " % n) and marker in l]
    assert len(idx) + len(done) == 1, "item %d: expected exactly one line, got %r/%r" % (n, idx, done)
    if idx:
        i = idx[0]
        assert "\n" not in tick
        lines[i] = tick
        print("ticked item %d on one physical line (%d chars)" % (n, len(tick)))
    else:
        print("item %d already ticked (idempotent): line %d" % (n, done[0] + 1))
assert len(lines) == len(text.split("\r\n")), "line count changed"
PLAN.write_bytes("\r\n".join(lines).encode("utf-8"))

# --- actions.log + progress.md ---------------------------------------------------------------------------
ltext = LOG.read_bytes().decode("utf-8")
if "MAX items 2-3 DONE" not in ltext:
    d = ltext.encode("utf-8")
    if not d.endswith(b"\r\n"):
        d += b"\r\n"
    LOG.write_bytes(d + (DONE + "\r\n").encode("utf-8"))
    print("actions.log: DONE appended (append-only)")
else:
    print("actions.log: DONE already present (idempotent)")

ptext = PROG.read_bytes().decode("utf-8")
if "MAX block items 2-3 DONE" not in ptext:
    d = ptext.encode("utf-8")
    if not d.endswith(b"\r\n"):
        d += b"\r\n"
    PROG.write_bytes(d + (PROG_LINE + "\r\n").encode("utf-8"))
    print("progress.md: appended 1 line")
else:
    print("progress.md: line already present (idempotent)")

# --- verify -----------------------------------------------------------------------------------------------
ok = True
t2 = PLAN.read_bytes().decode("utf-8")
l2 = t2.split("\r\n")
ticks = [l for l in l2 if re.match(r"^  [23]\. \[x\] ", l)]
unticked = [l for l in l2 if re.match(r"^  \d+\. \[ \]", l)]
ok &= len(ticks) == 2 and all("\n" not in t for t in ticks)
ok &= len(l2) == len(text.split("\r\n"))
ok &= any(l.startswith("  4. [ ] U3 Sydney talk session") for l in l2) and "- Stop after item 4." in t2
ok &= RM_SHA in t2 and FIX_SHA in t2
for s in (TICK2, TICK3, DONE, PROG_LINE):
    ok &= all(ord(c) < 128 for c in s)
for p in (LOG, PROG, PLAN):
    now = len(nonascii(p))
    print("%s: %d B, non-ASCII lines=%d (baseline %d)" % (p.name, len(p.read_bytes()), now, BASE[p]))
    ok &= now == BASE[p]
rm_files = git("show", "--name-status", "--format=", RM_SHA).split("\n")
print("commit %s file ops: %d, all D=%s" % (RM_SHA, len([f for f in rm_files if f.strip()]),
                                            all(f.startswith("D") for f in rm_files if f.strip())))
ok &= len([f for f in rm_files if f.strip()]) == 12
ok &= all(f.split("\t")[-1] in TARGETS for f in rm_files if f.strip())
fx_files = [f.split("\t")[-1] for f in git("show", "--name-status", "--format=", FIX_SHA).split("\n") if f.strip()]
print("commit %s touches: %s" % (FIX_SHA, fx_files))
ok &= fx_files == ["notes/2026-10-28-handoff-from-max.md"]
ok &= git("merge-base", "--is-ancestor", ADDER, "HEAD") == ""
ok &= os.path.exists(HANDBAK) and __import__("hashlib").sha256(open(HANDBAK, "rb").read()).hexdigest()[:8] == HANDBAK_SHA8
missing_on_disk = [t for t in TARGETS if os.path.exists(os.path.join(REPO, t))]
print("removed files back on disk (must be none):", missing_on_disk or "none")
ok &= not missing_on_disk
print("plan state: %d items ticked (2,3), %d unticked (item 4 = U3, next)" % (len(ticks), len(unticked)))
print("VERDICT: %s" % ("ALL RECORDS WRITTEN AND VERIFIED" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
