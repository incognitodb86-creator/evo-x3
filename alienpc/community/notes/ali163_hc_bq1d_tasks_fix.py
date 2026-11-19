"""BQ1d TASKS.md integrity repair (CPU only).

Two defects found by my own gate in the BQ1d pass:
 1) the previous Ralph pass appended result text to the FINAL line through a NON-RAW python
    string, so 'notes\ali163...' became 'notes<bell>li163...' (4 bells) and 'notes\body...'
    became 'notes<backspace>ody...'; the paths in that result text were unreadable.
 2) my first insert rewrote the file with LF endings while git HEAD is CRLF.
This repairs only the control characters (each becomes '/', the path target is unchanged) and
restores CRLF everywhere. Line count, the 18 unchecked lines, the BQ1d tick + result and the
5 BQ1-template lines are verified before/after; nothing else is touched.
"""
import io
import re

P = "C:/Users/derek/5slock/ralph-community/TASKS.md"

raw = io.open(P, encoding="utf-8", newline="").read()          # no newline translation
crlf = raw.count("\r\n")
lines = raw.split("\r\n") if "\r\n" in raw else raw.split("\n")
lines = [l.replace("\r", "") for l in lines]

before_ctrl = [(i + 1, [ord(c) for c in l if 0 < ord(c) < 32]) for i, l in enumerate(lines)
               if any(0 < ord(c) < 32 for c in l)]
fixed = []
for l in lines:
    out = ""
    for c in l:
        if 0 < ord(c) < 32:
            out += "/"
        else:
            out += c
    fixed.append(out)

text = "\r\n".join(fixed)
after_ctrl = [(i + 1, [ord(c) for c in l if 0 < ord(c) < 32]) for i, l in enumerate(text.split("\r\n"))
              if any(0 < ord(c) < 32 for c in l)]
gates = [("no control chars (ord 1-31) anywhere", not after_ctrl, str(before_ctrl)[:200]),
         ("line count unchanged", len(fixed) == len(lines), f"{len(fixed)} vs {len(lines)}"),
         ("CRLF restored on every line break", text.count("\r\n") == len(fixed) - 1,
          f"crlf={text.count(chr(13) + chr(10))} lines={len(fixed) - 1}"),
         ("18 unchecked lines, BQ1d is [x]", text.count("\r\n- [ ] ") == 18
          and "- [x] BQ1d SIDE-BY-SIDE" in text, f"open={text.count(chr(10) + '- [ ] ')}"),
         ("BQ1d result + 5 HB template lines present",
          all(s in text for s in ["- DONE 2026-10-23 ~17:45 CT", "HB0 CONTROL + the BQ1 TEMPLATE line"])
          and text.count("BQ1 TEMPLATE (BQ1d 2026-10-23, ticked)") == 4),
         ("no eaten-path artefacts (notesody / notesli163 / notesody_quality)",
          not any(s in text for s in ["notesody", "notesli163", "notesody_quality"])),
         ("the repaired FINAL result text now names the real builder path",
          "builder notes/ali163_hc_final_sheet.py" in text),
         ("BQ1d is the only newly ticked line (R6R/HB1-5/B4 stay open)",
          all(re.match(r"^- \[ \] " + k, text, re.M) for k in ["R6R ", "HB1 ", "HB2 ", "HB3 ", "HB4 ",
                                                               "HB5 ", "B4 ", "B4c ", "B4d ", "B4e ",
                                                               "B4f ", "B2 ", "PW1 ", "FINAL "]))]
io.open(P, "w", encoding="utf-8", newline="").write(text)
bad = [g for g in gates if not g[1]]
for g in gates:
    n = g[0]
    ok = g[1]
    det = g[2] if len(g) > 2 else ""
    print(("PASS " if ok else "FAIL ") + n + ("  [" + str(det)[:200] + "]" if det else ""))
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(g[0] for g in bad))
raise SystemExit(0 if not bad else 1)
