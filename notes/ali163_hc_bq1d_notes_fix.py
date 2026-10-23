"""BQ1d notes/self_diagnosis.md repair (CPU only, idempotent, 2026-10-23 ~18:05 CT).

The write-encoding trap damaged this file in EARLIER passes (my own append was clean):
- line 40: 5 bells 'notes<BEL>li163_hc_final_*' (the \a escape ate the 'a' of ali163)
- line 55: 'minimax_h3_rewriteruntime<BS>10310-cuda' (a \b-style escape ate the 'b' separator)
- line 96: 'notes\web<BEL>eddit_anatomy.json' (HF2's own line, \r-style escape ate the 'r')
Repair: every control char in line text becomes '/', then the three letters the escapes EATED are
restored, so the paths read notes/ali163_hc_final_*, minimax_h3_rewriter/runtime/10310-cuda and
notes/web/reddit_anatomy.json. Scans are CRLF-aware (a line's own trailing CR is not a defect -
measured: a naive scan flags every CRLF line = a FALSE fail).
Gates: 0 control chars, 0 lone CR, the 3 repaired path forms, line count kept, CRLF count kept,
byte delta < 40, the BQ1d entry untouched. Self-destruct probe at the bottom.
"""
import io

P = "C:/AI/community/notes/self_diagnosis.md"
CR = chr(13)
MENDS = [("notes/li163", "notes/ali163"),                     # \a ate the 'a'
         ("rewriter" + CR + "untime", "rewriter/runtime"),    # \r ate the 'r'
         ("\\web" + CR + "eddit", "/web/reddit")]              # HF2's line: 'notes\web\reddit...' ate the 'r'


def scan(text):
    out = []
    for i, raw in enumerate(text.split("\n")):
        line = raw[:-1] if raw.endswith(CR) else raw          # CRLF-aware
        codes = sorted({ord(c) for c in line if 0 < ord(c) < 32})
        if codes:
            out.append((i + 1, codes))
        if CR in line:
            out.append((i + 1, "LONE-CR"))
    return out


raw = io.open(P, encoding="utf-8", newline="").read()
before = scan(raw)
lines = raw.split("\n")
fixed = ["".join("/" if 0 < ord(c) < 32 and c not in CR + "\n" else c for c in l) for l in lines]
for a, b in MENDS:
    fixed = [l.replace(a, b) for l in fixed]
text = "\n".join(fixed)
after = scan(text)
gates = [("0 control chars and 0 lone CR in line text", not after, str(before)[:240]),
         ("line count unchanged (every pre-existing line kept)", len(fixed) == len(lines),
          f"{len(fixed)}"),
         ("the 4 eaten builder paths read notes/ali163_hc_final_* (>=5 total)",
          text.count("notes/ali163_hc_final_") >= 5 and "notes/li163" not in text,
          f"final={text.count('notes/ali163_hc_final_')} broken={text.count('notes/li163')}"),
         ("the rewriter runtime path reads minimax_h3_rewriter/runtime/10310-cuda",
          "minimax_h3_rewriter/runtime/10310-cuda" in text),
         ("HF2's reddit_anatomy path has no eaten-letter residue (line 96)",
          "web/reddit_anatomy.json" in text and "web" + CR not in text
          and "notes" + chr(7) not in text and "notes" + chr(8) not in text,
          f"ok={text.count('web/reddit_anatomy.json')} residue={text.count('web' + CR)}"),
         ("byte delta < 40 B (only control chars replaced + 3 letters restored)",
          abs(len(text) - len(raw)) < 40, f"{len(raw)} -> {len(text)}"),
         ("CRLF count kept (no line ending eaten)", raw.count(CR + "\n") == text.count(CR + "\n"),
          f"{raw.count(CR + chr(10))} -> {text.count(CR + chr(10))}"),
         ("the BQ1d entry is present and untouched",
          "BQ1d pass (ALI-163, ticked BQ1d, 1 tick, 0 denies" in text
          and "notes/ali163_hc_bq1d_check.py 22/22 gates" in text)]
if "--probe" in __import__("sys").argv:
    lines2 = list(lines)
    for i, l in enumerate(lines2):                       # restore ONE damage form in a clone
        lines2[i] = l.replace("notes/ali163_hc_final_sheet.py", "notes" + chr(7) + "li163_hc_final_sheet.py")
    d = scan("\n".join(lines2))
    print("PROBE: re-injecting ONE bell in self_diagnosis.md must FIRE the scan")
    print("  fired:", d, "->", "PASS the scan catches real damage" if d else
          "SELF-DESTRUCT: scan is blind, gate worthless")
    raise SystemExit(0 if d else 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(text)
bad = [g[0] for g in gates if not g[1]]
for g in gates:
    print(("PASS " if g[1] else "FAIL ") + g[0] + ("  [" + str(g[2])[:200] + "]" if len(g) > 2 else ""))
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(bad))
raise SystemExit(0 if not bad else 1)
