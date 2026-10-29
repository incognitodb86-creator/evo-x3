"""U2 close-out record (idempotent).

1. backup fix_plan.md -> fix_plan.md.bak-20261029-u2-tick, then tick MAX item 1 on ITS OWN physical line
   (the loop reads one line per item; fix_plan.md is CRLF - read/write bytes, join CRLF, one line per tick).
   Max's spec text (the 3 continuation lines) is kept unchanged under the tick.
2. append ONE DONE line to C:/AI/community/notes/actions.log.
3. append one line to ralph-community/notes/progress.md.

Verifies after writing: the tick is a single line, item count/line count unchanged, files ASCII-clean,
and prints the evidence it wrote. Nothing is installed, rendered or restarted.
"""
import datetime
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
PLAN = Path(r"C:\Users\derek\5slock\ralph-community\fix_plan.md")
BAK = PLAN.with_name("fix_plan.md.bak-20261029-u2-tick")
LOG = Path(r"C:\AI\community\notes\actions.log")
PROG = Path(r"C:\Users\derek\5slock\ralph-community\notes\progress.md")
CHECK = r"C:\AI\community\notes\u2_check.py"
NOTE = r"C:\AI\community\notes\2026-10-29-U2-prompt-skill-merge-DONE.md"

TICK = ("  1. [x] U2 prompt-skill merge DONE %s: h3-prompting\\SKILL.md is the single home for prompt rules "
        "(R1-R31, output-only-prompt, adults-only 18+, audio per TenStrip HF #77 = no overall_soundscape / "
        "non_diegetic_music block, plain cues at the end, 4 examples) + references\\examples_archived.md (the 2 "
        "p15 few-shots verbatim, read on demand); ref2va-prompt 8635->3030 B, h3-ref2va-prompt-chain 3533->3122 B, "
        "director prompt sections 19545->19112 B are short pointers to the home; PROMPT.md L16 dead "
        "p15_writer_batch.py/p15_driver.ps1 repointed to 7 existing paths; check %s exit 0 = ALL CLAUSES PASS "
        "(31/31) incl. each rule string in exactly one skill (31/31 unique across 14 skill-package files), 5 "
        "backups sha-verified, youth guard 26 passed, gpu_guard IDLE; evidence %s + notes\\actions.log START/DONE. "
        "[Max's spec lines kept below unchanged.]") % (NOW, CHECK, NOTE)

def nonascii(path):
    """Lines containing non-ASCII characters (baseline taken BEFORE any write, so pre-existing text in
    Max's/loop history is not attributed to this record; my appended lines are checked ASCII-clean)."""
    return [l for l in path.read_bytes().decode("utf-8").split("\r\n") if not all(ord(c) < 128 for c in l)]


BASE = {p: len(nonascii(p)) for p in (LOG, PROG, PLAN)}

# --- 1. fix_plan.md tick ---------------------------------------------------------------------------
raw = PLAN.read_bytes()
if not BAK.exists():
    BAK.write_bytes(raw)
    print("backup -> %s (%d B)" % (BAK, len(raw)))
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert text.count("\n") == len(lines) - 1, "expected pure CRLF"
idx = [i for i, l in enumerate(lines) if l.startswith("  1. [ ] U2 prompt-skill merge:")]
done = [i for i, l in enumerate(lines) if l.startswith("  1. [x] U2 prompt-skill merge DONE")]
assert len(idx) + len(done) == 1, "expected exactly one U2 item, got %r / %r" % (idx, done)
if idx:
    i = idx[0]
    assert lines[i + 1].startswith("     ") and lines[i + 4] == "- Stop after U2.", "MAX block shape changed"
    before = lines[i]
    lines[i] = TICK
    assert "\n" not in TICK and len(lines) == len(text.split("\r\n")), "tick must stay one physical line"
    PLAN.write_bytes("\r\n".join(lines).encode("utf-8"))
    print("ticked item 1 on one physical line (len %d -> %d chars)" % (len(before), len(lines[i])))
else:
    print("already ticked (idempotent): line %d" % (done[0] + 1))

# --- 2. actions.log DONE line ----------------------------------------------------------------------
DONE = ("%s | U2 prompt-skill merge DONE | files: C:\\AI\\community\\skills\\h3-prompting\\SKILL.md (single home, "
        "R1-R31) + references\\examples_archived.md (2 p15 few-shots verbatim); "
        "C:\\Users\\derek\\.pi\\agent\\skills\\{ref2va-prompt,h3-ref2va-prompt-chain,alienpc-hardcore-i2v-director}"
        "\\SKILL.md -> pointers (-6.4 KB); C:\\Users\\derek\\5slock\\ralph-community\\PROMPT.md L16 repointed "
        "(7 existing paths); backups .bak-20261029-u2 x5 + .mid snapshot; audio rule from TenStrip HF #77 saved to "
        "notes\\web\\tenstrip_hf77_audio_20261029.md; check %s exit 0 ALL CLAUSES PASS (31/31, each rule string in "
        "exactly one skill); youth guard 26 passed; gpu_guard IDLE, no GPU/render/model load; note %s; "
        "stop after U2 per MAX block" % (NOW, CHECK, NOTE))
lines_log = LOG.read_bytes().decode("utf-8").split("\r\n")
if not any("U2 prompt-skill merge DONE" in l for l in lines_log):
    LOG.write_bytes(("\r\n".join([l for l in lines_log if l != ""] + [DONE]) + "\r\n").encode("utf-8"))
    print("actions.log: appended DONE line")
else:
    print("actions.log: DONE line already present (idempotent)")

# --- 3. progress.md -------------------------------------------------------------------------------
PROG_LINE = ("- %s U2 prompt-skill merge DONE (MAX block item 1, stop after U2): `C:/AI/community/skills/"
             "h3-prompting/SKILL.md` is the single home for prompt rules (R1-R31, output-only-prompt, adults-only "
             "18+, audio per TenStrip HF #77 - no `overall_soundscape:` / `non_diegetic_music:` block, plain cues "
             "at the end; the 2 archived p15 few-shots are verbatim in the skill's `references/"
             "examples_archived.md`), and `ref2va-prompt`, `h3-ref2va-prompt-chain` and the director's prompt "
             "sections are short pointers to it (-6.4 KB of duplicated rule text out of the .pi skills). PROMPT.md "
             "L16 no longer names dead scripts. Check `C:/AI/community/notes/u2_check.py` exit 0 = ALL CLAUSES PASS "
             "(31/31), each rule string in exactly one skill; youth guard 26 passed; gpu_guard IDLE (no GPU, no "
             "render). U3-U5 NOT started. Note: `C:/AI/community/notes/2026-10-29-U2-prompt-skill-merge-DONE.md`"
             % NOW)
plines = PROG.read_bytes().decode("utf-8").split("\r\n")
if not any("U2 prompt-skill merge DONE" in l for l in plines):
    PROG.write_bytes(("\r\n".join([l for l in plines if l != ""] + [PROG_LINE]) + "\r\n").encode("utf-8"))
    print("progress.md: appended 1 line")
else:
    print("progress.md: line already present (idempotent)")

# --- verify ----------------------------------------------------------------------------------------
ok = True
t2 = PLAN.read_bytes().decode("utf-8")
l2 = t2.split("\r\n")
tick = [l for l in l2 if l.startswith("  1. [x] U2 prompt-skill merge DONE")]
unticked = [l for l in t2.split("\r\n") if re.match(r"^  \d+\. \[ \]", l)]
ok &= len(tick) == 1 and "\n" not in tick[0] and len(l2) == len(text.split("\r\n"))
ok &= "     ref2va-prompt, h3-ref2va-prompt-chain" in t2 and "- Stop after U2." in t2
ok &= sum(1 for l in LOG.read_bytes().decode("utf-8").split("\r\n")
          if "U2 prompt-skill merge DONE" in l) == 1
for s in (TICK, DONE, PROG_LINE):
    a = all(ord(c) < 128 for c in s)
    ok &= a
    print("appended record ASCII-clean: %s" % a)
for p in (LOG, PROG, PLAN):
    body = p.read_bytes()
    now = len(nonascii(p))
    print("%s: %d B, non-ASCII lines=%d (baseline before this record: %d)" % (p.name, len(body), now, BASE[p]))
    ok &= now == BASE[p]
print("ticks in plan: 1 ticked U2, %d unticked items remain (MAX block items 2-5 = U3/U4/U5/other, not started)"
      % len(unticked))
print("VERDICT: %s" % ("ALL RECORDS WRITTEN AND VERIFIED" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
