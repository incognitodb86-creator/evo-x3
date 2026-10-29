"""U2 FIX-pass close-out record (idempotent).

Max said the 10:26 tick was premature, so this script REWRITES the MAX item-1 tick line in fix_plan.md with the
fix-pass evidence (one physical line, CRLF preserved, Max's spec lines untouched), appends one DONE line to
notes/actions.log and one line to ralph-community/notes/progress.md. Verifies after writing: exactly one tick
line, one physical line, item/line counts unchanged, no new non-ASCII in the appended records.

Nothing is installed, rendered, loaded or queued.
"""
import datetime
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
PLAN = Path(r"C:\Users\derek\5slock\ralph-community\fix_plan.md")
BAK = PLAN.with_name("fix_plan.md.bak-20261029-u2fix-tick")
LOG = Path(r"C:\AI\community\notes\actions.log")
PROG = Path(r"C:\Users\derek\5slock\ralph-community\notes\progress.md")
CHECK = r"C:\AI\community\notes\u2_check.py"
NOTE = r"C:\AI\community\notes\2026-10-29-U2-prompt-skill-merge-DONE.md"
MAXV = r"C:\Users\derek\5slock\ralph-community\notes\2026-10-29-max-U2-verify-FAIL.md"
MARK = "after Max verify 10:29 CT FAIL"

TICK = ("  1. [x] U2 prompt-skill merge DONE %s (%s - the 10:26 CT tick was premature, Max: \"Do not tick item 1 "
        "yet\"): h3-prompting\\SKILL.md is the single home for prompt rules (R1-R31) + references\\examples_"
        "archived.md (the 2 p15 few-shots, character-for-character, LF); ref2va-prompt 8635->3029 B, "
        "h3-ref2va-prompt-chain 3533->3029 B and alienpc-hardcore-i2v-director 19545->19269 B are pointers - "
        "**0 of 2304 home-rule 5-word shingles appear in any pointer** and none of Max's key phrases (does not pin "
        "frame 0 / zoom out / only if loaded / unique seed per cell) appears in any pointer; the Max-TE lane rule now "
        "lives in exactly one skill (the director); director references\\max-i2v-prompt-improve-v1.md is marked "
        "HISTORY (R7 deletes its overall_soundscape/non_diegetic_music blocks) and writers are no longer sent there as "
        "a live guide; R26 is vocabulary-only (no R7 repeat), R22 + Example 1 state the slap as positives (R24), "
        "Example 2 carries the full R11 clause, the \"~10 KB each\" claim is corrected to the measured 9,749 B, and "
        "SKILL.md.mid-20261029-u2-examples moved out of the skill folder to notes\\; PROMPT.md L16 repointed to 7 "
        "existing paths; check %s v2 exit 0 = ALL CLAUSES PASS (46/46) incl. the phrase-level duplicate scan of both "
        "skill trees, the audio-block supersession scan of every skill references/*.md, the restored "
        "no-scripts/runs/p7/p3/specs clause, 10 backups sha-verified, youth guard 26 passed, gpu_guard IDLE; evidence "
        "%s + Max's verify %s; actions.log START/FIX/DONE. [Max's spec lines kept below unchanged.]") % (NOW, MARK,
                                                                                                          CHECK, NOTE,
                                                                                                          MAXV)

DONE = ("%s | U2 prompt-skill merge DONE (FIX pass, %s) | Max's 5 fix items closed: director L122-128 -> one line "
        "(R6/R15/R23), director L56 + L95-96 stop sending writers to references\\max-i2v-prompt-improve-v1.md (the "
        "file now carries a HISTORY header naming R7 + HF #77), L63 -> (R31), Max-TE lane rule kept in the director "
        "only; ref2va L21-25 -> (R6)/(R28) + TE pointer, chain L62-68/L78 -> (R29); h3 R26 made vocabulary-only, "
        "Example 2 full R11 clause, R22 + Example 1 rewritten as positives, \"~10 KB each\" -> measured 9,749 B, "
        "R5 no longer restates R16, the false 'both notes roots' p15 claim corrected; SKILL.md.mid snapshot moved to "
        "C:\\AI\\community\\notes\\. u2_check.py v2 (Max item 5): 5-word shingle duplicate scan over both skill trees "
        "and supporting files (masks paths/skill names/R-cites, drops function-word runs), Max's 4 key phrases, "
        "internal home duplication, audio supersession scan of skill references, audio test on sentences with "
        "block/history/nothing removed from the pass list, restored no-scripts/runs/p7/p3/specs clause, u2fix backups "
        "by sha prefix -> exit 0 ALL CLAUSES PASS (46/46). Sizes: h3 SKILL.md 28753 B, director 19269 B (-276 vs "
        "pre-U2), ref2va 3029 B, chain 3029 B. Backups .bak-20261029-u2fix x5 (sha8 5a293990/47e69734/612ec3b3/"
        "3e534e78/54f8c402). No GPU, no render, no model load, no queue; gpu_guard IDLE. Note %s" % (NOW, MARK, NOTE))

PROG_LINE = ("- %s U2 prompt-skill merge DONE (FIX pass after Max's verify FAIL at 10:29 CT; MAX block item 1, stop "
             "after U2): the 10:26 tick was premature and is rewritten with the fix evidence. Home stays "
             "`C:/AI/community/skills/h3-prompting/SKILL.md` (R1-R31); the director's restated rule sentences are cut "
             "to cites (R6/R15/R23/R31/R2), its history pack `references/max-i2v-prompt-improve-v1.md` is marked "
             "HISTORY (R7 deletes its `overall_soundscape:` blocks) and is no longer sent to writers as a live guide; "
             "`ref2va-prompt` 3,029 B and `h3-ref2va-prompt-chain` 3,029 B point at the home; the Max-TE lane rule "
             "lives in exactly one skill. Inside the home: R26 is vocabulary-only (no R7 repeat), R22 and Example 1 "
             "state the slap as positives, Example 2 carries the full R11 clause, the example-size claim is corrected "
             "to the measured 9,749 B, and the 36 KB mid snapshot moved to `C:/AI/community/notes/`. "
             "`C:/AI/community/notes/u2_check.py` v2 - phrase-level duplicate scan (5-word shingles over both skill "
             "trees + supporting files), Max's four key phrases, internal-duplication and audio-supersession scans, "
             "restored no-scripts/runs/p7/p3/specs clause - exits 0 = ALL CLAUSES PASS (46/46): 0 of 2,304 rule "
             "shingles in any pointer, youth guard 26 passed, gpu_guard IDLE. U3-U5 NOT started. Note: "
             "`C:/AI/community/notes/2026-10-29-U2-prompt-skill-merge-DONE.md`" % NOW)


def nonascii(path):
    return [l for l in path.read_bytes().decode("utf-8").split("\r\n") if not all(ord(c) < 128 for c in l)]


BASE = {p: len(nonascii(p)) for p in (LOG, PROG, PLAN)}

# --- 1. fix_plan.md: rewrite the tick line -------------------------------------------------------------
raw = PLAN.read_bytes()
if not BAK.exists():
    BAK.write_bytes(raw)
    print("backup -> %s (%d B)" % (BAK, len(raw)))
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert text.count("\n") == len(lines) - 1, "expected pure CRLF"
idx = [i for i, l in enumerate(lines) if l.startswith("  1. [x] U2 prompt-skill merge DONE")]
assert len(idx) == 1, "expected exactly one ticked U2 item, got %r" % idx
i = idx[0]
assert lines[i + 1].startswith("     ") and lines[i + 4] == "- Stop after U2.", "MAX block shape changed"
if MARK in lines[i]:
    print("plan tick already carries the fix evidence (idempotent): line %d" % (i + 1))
else:
    assert "\n" not in TICK
    old_len = len(lines[i])
    lines[i] = TICK
    assert len(lines) == len(text.split("\r\n")), "tick must stay one physical line"
    PLAN.write_bytes("\r\n".join(lines).encode("utf-8"))
    print("plan tick rewritten on one physical line (%d -> %d chars)" % (old_len, len(TICK)))

# --- 2. actions.log ----------------------------------------------------------------------------------
llines = [l for l in LOG.read_bytes().decode("utf-8").split("\r\n") if l.strip()]
if not any("U2 prompt-skill merge DONE (FIX pass" in l for l in llines):
    LOG.write_bytes(("\r\n".join(llines + [DONE]) + "\r\n").encode("utf-8"))
    print("actions.log: appended the FIX-pass DONE line")
else:
    print("actions.log: FIX-pass DONE line already present (idempotent)")

# --- 3. progress.md ----------------------------------------------------------------------------------
plines = [l for l in PROG.read_bytes().decode("utf-8").split("\r\n") if l.strip()]
if not any("U2 prompt-skill merge DONE (FIX pass" in l for l in plines):
    PROG.write_bytes(("\r\n".join(plines + [PROG_LINE]) + "\r\n").encode("utf-8"))
    print("progress.md: appended 1 line")
else:
    print("progress.md: FIX-pass line already present (idempotent)")

# --- verify ------------------------------------------------------------------------------------------
ok = True
t2 = PLAN.read_bytes().decode("utf-8")
l2 = t2.split("\r\n")
ticks = [l for l in l2 if l.startswith("  1. [x] U2 prompt-skill merge DONE")]
unticked = [l for l in l2 if re.match(r"^  \d+\. \[ \]", l)]
ok &= len(ticks) == 1 and MARK in ticks[0] and "\n" not in ticks[0]
ok &= len(l2) == len(text.split("\r\n")) and lines[i + 1:i + 4] == l2[i + 1:i + 4]
ok &= "- Stop after U2." in t2
ok &= sum(1 for l in LOG.read_bytes().decode("utf-8").split("\r\n")
          if "U2 prompt-skill merge DONE (FIX pass" in l) == 1
for s in (TICK, DONE, PROG_LINE):
    a = all(ord(c) < 128 for c in s)
    ok &= a
print("appended records ASCII-clean:", all(all(ord(c) < 128 for c in s) for s in (TICK, DONE, PROG_LINE)))
for p in (LOG, PROG, PLAN):
    now = len(nonascii(p))
    print("%s: %d B, non-ASCII lines=%d (baseline before this record: %d)" % (p.name, len(p.read_bytes()),
                                                                              now, BASE[p]))
    ok &= now == BASE[p]
print("plan items: %d ticked (U2), %d unticked (MAX block items 2-5 = U3/U4/U5, NOT started)"
      % (len(ticks), len(unticked)))
print("VERDICT: %s" % ("ALL RECORDS WRITTEN AND VERIFIED" if ok else "PROBLEM"))
sys.exit(0 if ok else 1)
