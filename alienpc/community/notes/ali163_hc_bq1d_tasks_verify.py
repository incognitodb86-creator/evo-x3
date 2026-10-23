"""BQ1d TASKS.md VERIFIER - READ-ONLY, writes nothing (2026-10-23 ~18:20 CT).

Checks the live ralph-community\TASKS.md after the BQ1d tick, the 5 BQ1-template lines and the
pre-existing control-char repair:
1 BQ1d is [x] and its result text carries the objective facts (id, seed, 243 packets, audio, sha,
  sheet path, 1344x768, 124+119, 0 JOB error / 0 CLIP_SKIP) + the disclosure of repaired paths
2 exactly 5 BQ1-template lines: the HB0 control note under the HB parent + HB1/HB2/HB3/HB4-TEMPLATE
  (the HB parent is '- HB HARDCORE ...', NOT '- [ ]', so a startswith('- [ ] HB HARDCORE') anchor
  silently inserts nothing - measured, and the reason my first pass was 1 line short)
3 every template line names the builder, the start-still slot, the face-crop slots and 'no vision judge'
4 the 4 builder paths read notes/ali163_hc_final_* and no eaten form (notes/li163, notes+bell) remains
5 0 control chars inside line text (CRLF-aware), CRLF on every break, no lone LF
6 open-task ids vs git HEAD: BQ1d closed and nothing of Max's open line lost (Max's own adds/removes listed)
Usage: python notes/ali163_hc_bq1d_tasks_verify.py
"""
import io
import re
import subprocess

P = "C:/Users/derek/5slock/ralph-community/TASKS.md"
MARK = "BQ1 TEMPLATE LINE (BQ1d 2026-10-23):"
CR = chr(13)
LF = chr(10)
HEAD = subprocess.run(["git", "-C", "C:/Users/derek/5slock/ralph-community", "show", "HEAD:TASKS.md"],
                      capture_output=True, text=True, encoding="utf-8").stdout

raw = io.open(P, encoding="utf-8", newline="").read()
lines = raw.split(CR + LF)
bq = [l for l in lines if l.startswith("- [x] BQ1d ")]
tmpl = [l for l in lines if MARK in l and re.match(r"^ *(HB0 CONTROL|HB[1-4]-TEMPLATE)\b", l.strip())]
ctrl = [(i + 1, sorted({ord(c) for c in (l[:-1] if l.endswith(CR) else l) if 0 < ord(c) < 32}))
        for i, l in enumerate(raw.split(LF))
        if any(0 < ord(c) < 32 for c in (l[:-1] if l.endswith(CR) else l))]


def ids(text):
    return {l.split("]")[1].split()[0] for l in text.splitlines()
            if l.startswith("- [ ]") and l.split("]")[1].split()}
    # the 2-space sub-lines are notes, not tasks; a '- [ ]' line with no token is ignored


gates = [
    ("BQ1d is [x] with its result text (1 line, 'DONE', 16 required facts)",
     len(bq) == 1 and "DONE" in bq[0] and all(k in bq[0] for k in [
         "ali147_pool_hc_r3b_s51130003", "seed 51130003", "243 packets", "audio aac 32000 Hz 2ch",
         "sha8 d125b8fe", "body_quality_r3b_vs_r3r_contact.png", "1344x768", "124+119",
         "0 JOB error", "0 CLIP_SKIP", "wall=8.8m", "ce01686e", "22/22", "21/21", "4/4",
         "notes/ali163_hc_bq1d_objective.json", "audio aac 32000 Hz 2ch", "wall=8.8m",
         "0 GPU minutes", "10 steps", "shift 10/3", "euler"]),
     f"len={len(bq[0]) if bq else 0}"),
    ("the BQ1d line discloses the repaired pre-existing paths",
     bool(bq) and "disclosed in notes/self_diagnosis.md" in bq[0]
     and "mangled path strings" in bq[0]
     and "escape trap" in bq[0] and "No task text of Max's was changed" in bq[0]),
    ("5 BQ1-template lines (HB0 CONTROL + HB1/HB2/HB3/HB4-TEMPLATE)",
     len(tmpl) == 5 and {t.strip().split()[0] for t in tmpl} ==
     {"HB0", "HB1-TEMPLATE", "HB2-TEMPLATE", "HB3-TEMPLATE", "HB4-TEMPLATE"},
     str(sorted(t.strip().split()[0] for t in tmpl))),
    ("the 4 ARM template lines: start-still slot + face-crop slots + BQ1 builder + no-vision-judge; the "
     "HB0 CONTROL note names the OLD wiring, the sheet and no-vision-judge (it has no builder - 0 new jobs)\n"
     "  NOTE: select by the LINE TAG, never by 'TEMPLATE' in t - the shared marker text itself contains "
     "'BQ1 TEMPLATE LINE', so that filter catches the HB0 line too (measured: arm n = 5 = a FALSE fail)",
     all("face crop" in t and "no vision judge" in t.lower() for t in tmpl)
     and all(k in t for t in tmpl if re.match(r"^ *HB[1-4]-TEMPLATE\b", t.strip())
             for k in ("ref_image_1", "ref_image_2", "notes/ali163_hc_bq1_build.py"))
     and any("NO start still" in t and "body_quality_r3b_vs_r3r_contact.png" in t
             for t in tmpl if re.match(r"^ *HB0 CONTROL\b", t.strip())),
     f"arm={sum(1 for t in tmpl if re.match(r'^ *HB[1-4]-TEMPLATE', t.strip()))} "
     f"ctl={sum(1 for t in tmpl if re.match(r'^ *HB0 CONTROL', t.strip()))}"),
    ("the 4 builder paths read notes/ali163_hc_final_* and no eaten form remains",
     all(("notes/ali163_hc_final_" + s) in raw for s in ("sheet.py", "objective.json", "check.py",
                                                         "media.ps1"))
     and "notes/li163" not in raw and "notes" + chr(7) not in raw,
     f"final={raw.count('notes/ali163_hc_final_')}"),
    ("0 control chars inside line text (CRLF-aware)", not ctrl, str(ctrl)[:150]),
    ("CRLF on every break, no lone LF", raw.count(LF) == raw.count(CR + LF),
     f"crlf={raw.count(CR + LF)} lf={raw.count(LF)}"),
    ("open-task ids: BQ1d closed, no Max open line lost (his adds listed)",
     not (ids(HEAD) - ids(raw) - {"BQ1d"}),
     f"gone={sorted(ids(HEAD) - ids(raw))} new={sorted(ids(raw) - ids(HEAD))}"),
]
bad = [g[0] for g in gates if not g[1]]
for g in gates:
    print(("PASS " if g[1] else "FAIL ") + g[0] + ("  [" + str(g[2])[:190] + "]" if len(g) > 2 else ""))
print("lines", len(lines), "open", len(re.findall(r"^- \[ \] ", raw, re.M)),
      "checked", len(re.findall(r"^- \[x\] ", raw, re.M)))
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(bad))
raise SystemExit(0 if not bad else 1)
