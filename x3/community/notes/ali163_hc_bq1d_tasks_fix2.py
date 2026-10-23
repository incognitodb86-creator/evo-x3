"""BQ1d TASKS.md repair, round 2 (CPU only) - IDEMPOTENT.

The 4 bells in the FINAL line's result text were 'notes\\ali163...' eaten to 'notes<bell>li163...'
by a previous Ralph pass (they are in git HEAD too). Round 1 turned each bell into '/', which left
'notes/li163...' (the bell ate the 'a' itself). This restores the 4 builder paths and verifies,
against git HEAD: line count 94 + my 5 BQ1d template lines, the open-task id set = HEAD's minus
BQ1d only, no control chars in any line text, CRLF on every break.
Re-running is safe (the checks are on the end state, not on the number of replacements).

NOTE: Max edited TASKS.md during this pass (the R6R line is now '- [x] R6R: re-request ...' and the
B4c-B4f lines are gone), so every read here is read-modify-write of the CURRENT file and the
spot-check keys are taken from the live file, never from an older read.
"""
import io
import re
import subprocess

P = "C:/Users/derek/5slock/ralph-community/TASKS.md"
BROKEN = ["notes/li163_hc_final_sheet.py", "notes/li163_hc_final_objective.json",
          "notes/li163_hc_final_check.py", "notes/li163_hc_final_media.ps1",
          "notes" + chr(7) + "li163_hc_final_sheet.py", "notes" + chr(7) + "li163_hc_final_objective.json",
          "notes" + chr(7) + "li163_hc_final_check.py", "notes" + chr(7) + "li163_hc_final_media.ps1"]
GOOD = ["notes/ali163_hc_final_sheet.py", "notes/ali163_hc_final_objective.json",
        "notes/ali163_hc_final_check.py", "notes/ali163_hc_final_media.ps1"]

t = io.open(P, encoding="utf-8", newline="").read()
head = subprocess.run(["git", "show", "HEAD:TASKS.md"], cwd="C:/Users/derek/5slock/ralph-community",
                      capture_output=True).stdout.decode("utf-8")
for a, b in zip(BROKEN[:4], GOOD):
    t = t.replace(a, b)
t = t.replace("notes" + chr(7) + "li163", "notes/ali163")

# idempotent disclosure on the BQ1d result line (the repair touches another line's result text)
DISC = (" Also repaired in this pass: 4 builder paths in the FINAL line's result text were eaten by the "
        "same escape trap (git HEAD carries them as 'notes<bell>li163_hc_final_*'); they now read "
        "notes/ali163_hc_final_{sheet,objective,check,media}.*, verified by "
        "notes/ali163_hc_bq1d_tasks_fix2.py and disclosed in notes/self_diagnosis.md. No task text of "
        "Max's was changed, only those 4 mangled path strings + the 5 BQ1-template lines.")
if DISC not in t:
    ls = t.split("\r\n")
    for i, l in enumerate(ls):
        if l.startswith("- [x] BQ1d SIDE-BY-SIDE"):
            ls[i] = l + DISC
    t = "\r\n".join(ls)

lines = t.split("\r\n")
ctrl = [(i + 1, [ord(c) for c in l if 0 < ord(c) < 32]) for i, l in enumerate(lines)
        if any(0 < ord(c) < 32 for c in l)]
open_now = set(re.findall(r"^- \[ \] ([A-Za-z0-9]+)\b", t, re.M))
open_head = set(re.findall(r"^- \[ \] ([A-Za-z0-9]+)\b", head, re.M))
gates = [("the 4 eaten builder paths read notes/ali163_hc_final_* (4/4)",
          all(t.count(g) >= 1 for g in GOOD), " ".join(f"{g.split('/')[-1]}={t.count(g)}" for g in GOOD)),
         ("no broken form left (notes/li163 or bell form)", not any(b in t for b in BROKEN)),
         ("no control chars (ord 1-31) in any line text", not ctrl, str(ctrl)[:140]),
         ("CRLF on every break, no lone LF", t.count("\r\n") == t.count("\n") == 98,
          f"crlf={t.count(chr(13)+chr(10))} lf={t.count(chr(10))}"),
         ("open-task ids = HEAD minus BQ1d only",
          open_now == (open_head - {"BQ1d"}) and "BQ1d" in open_head,
          f"added={sorted(open_now - open_head)} removed={sorted(open_head - open_now)}"),
         ("BQ1d [x] + DONE result + disclosure + 5 BQ1-template lines (HB0 note + HB1-4)",
          "- [x] BQ1d SIDE-BY-SIDE" in t and "- DONE 2026-10-23 ~17:45 CT" in t
          and "disclosed in notes/self_diagnosis.md" in t
          and t.count("BQ1 TEMPLATE (BQ1d 2026-10-23, ticked)") == 4
          and "HB0 CONTROL + the BQ1 TEMPLATE line" in t),
         ("line count = HEAD 94 + 5 = 99", len(lines) == head.count("\r\n") + 1 + 5, f"{len(lines)}"),
         ("live-file spot checks (Max's current text survived my read-modify-write)",
          all(k in t for k in ["- [ ] FINAL REOPENED (Max 3:16 PM CT", "- [ ] HB1 27B VISION PROMPTER",
                               "- [ ] HB5 SCORE", "- [x] R6R: re-request ali147_pool_hc_r3",
                               "- [ ] RL1 ", "- [ ] RF1 ", "- [ ] RA1 ", "- [x] R9 REDO clip 6 from pick HC6"]),
          "keys taken from the live file, not an old read")]
io.open(P, "w", encoding="utf-8", newline="").write(t)
bad = [g[0] for g in gates if not g[1]]
for g in gates:
    print(("PASS " if g[1] else "FAIL ") + g[0] + ("  [" + str(g[2])[:170] + "]" if len(g) > 2 else ""))
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(bad))
raise SystemExit(0 if not bad else 1)
