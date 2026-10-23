r"""ALI-147 FINAL summary self-check (read-only, CPU only; writes only its report).

Verifies notes/ali147_summary.md against the FINAL line's checklist: file exists,
all five arms named, the Matrix/Failures/Appendix sections, no empty table cells,
no TBD/TODO placeholders, the METHOD_ONLY + KEEP-is-Derrick labels, the
CTRL-by-driver note. Then it verifies the summary's claims against the files, not
against hardcoded values: every render/sbs under runs/ is named (summary paths are
written with the declared `runs\` shorthand, so strings are compared as relpaths),
every quoted `... CT ...` log line appears verbatim in a real status.log / dip.log
/ p7 *.out (live or .failed-*), the numbers come from each objective.json, the
live p7 logs are clean while the .failed-20261022 archive holds the STUCK/JOB
error evidence, and the RS0/RS1 evidence gap is STATED in the summary (those files
are absent, so the check asserts the stated gap, not the files).

Report: notes/ali147-summary-check-20261022.txt. No GPU, no render, no writes
anywhere else.
"""
import datetime
import glob
import hashlib
import json
import os
import re

SUM = r"C:\AI\community\notes\ali147_summary.md"
RUNS = r"C:\AI\community\runs"
JOBS = r"C:\AI\community\p7\jobs"
REPORT = r"C:\AI\community\notes\ali147-summary-check-20261022.txt"
ARMS = ["ali147_pool_ctrl_s51080000", "ali147_pool_fix1_s51080000",
        "ali147_pool_fix5_s51080000", "ali147_pool_dip_s51080000",
        "ali147_pool_fix4_s51080000"]
GRAPH_ARMS = ARMS[:3] + ARMS[4:]

buf, fails = [], []


def p(msg):
    print(msg)
    buf.append(str(msg))


def chk(ok, label, detail=""):
    p(("PASS " if ok else "FAIL ") + label + ("" if not detail else ""))
    if detail:
        p("   " + detail)
    if not ok:
        fails.append(label)


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


raw = open(SUM, "rb").read()
text = raw.decode("utf-8")
p("summary %s bytes=%d sha256=%s lines=%d local time=%s"
  % (SUM, len(raw), hashlib.sha256(raw).hexdigest(), len(text.splitlines()),
     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
chk(os.path.exists(SUM), "notes/ali147_summary.md exists")
for a in ARMS:
    chk(a in text, "arm named: %s (count=%d)" % (a, text.count(a)))
chk("METHOD_ONLY" in text, "METHOD_ONLY label present")
chk("KEEP is Derrick" in text, "KEEP-is-Derrick line present")
chk("rendered by the driver" in text, "CTRL-by-driver note present")
for k in ("render secs", "ffprobe", "contact sheet", "dip.log", "status.log",
          "bytes", "duration", "failures", "STUCK", "redo"):
    chk(k.lower() in text.lower(), "required column/term present: %s" % k)
for sec in ("# Matrix", "### CTRL", "### FIX1", "### FIX5", "### DIP",
            "### FIX4", "## Failures", "## Appendix", "## Method notes"):
    chk(sec in text, "section present: %s" % sec)

empty = [ln for ln in text.splitlines()
         if ln.strip().startswith("|") and re.search(r"\|\s*\|", ln)]
chk(not empty, "no empty table cells (found %d)" % len(empty),
    "\n".join("EMPTY-CELL: %s" % ln[:140] for ln in empty[:6]))
for pad in ("TBD", "TODO", "FIXME", "placeholder"):
    chk(pad.lower() not in text.lower(), "no %s placeholder" % pad)

mp4s = sorted(glob.glob(os.path.join(RUNS, "**", "ali147_pool_*.mp4"),
                        recursive=True))
rel = [os.path.relpath(pth, RUNS) for pth in mp4s]
chk(len(mp4s) == len(set(mp4s)), "no duplicate mp4 path (n=%d)" % len(mp4s),
    "mp4s: %s" % rel)
missing_mp4 = [r for r in rel if r not in text]
chk(not missing_mp4, "every render under runs/ is named in the summary",
    "missing: %s" % missing_mp4)

sbs = sorted(glob.glob(os.path.join(RUNS, "**", "sbs_*"), recursive=True))
relsbs = [os.path.relpath(pth, RUNS) for pth in sbs]
missing_sbs = [r for r in relsbs if r not in text]
chk(not missing_sbs, "every sbs under runs/ is named in the summary",
    "sbs: %s missing: %s" % (relsbs, missing_sbs))

logs = []
for pat in ("**/status.log", "**/dip.log"):
    logs += glob.glob(os.path.join(RUNS, pat), recursive=True)
live_out = sorted(glob.glob(os.path.join(JOBS, "*.out")))
arch_out = sorted(glob.glob(os.path.join(JOBS, "*.out.failed-*")))
logs += live_out + arch_out
union = "\n".join(read(f) for f in logs)
quoted = [ln.strip() for ln in text.splitlines()
          if re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} CT ", ln)]
elided = [q for q in quoted if re.search(r"\u2026|\.\.\.", q)]
union_lines = union.splitlines()


def verbatim(q):
    """A quoted log line must start a real log line; every long comma-delimited
    fragment after an elision marker (...) must appear verbatim in a real log."""
    parts = re.split(r"\u2026|\.\.\.", q)
    head = parts[0]
    if not any(ln.startswith(head) for ln in union_lines):
        return False, "prefix not in any log: %s" % head[:160]
    for frag in parts[1:]:
        for sub in frag.split(", "):
            if len(sub.strip()) >= 25 and sub not in union:
                return False, "fragment not verbatim: %s" % sub[:160]
    return True, ""


bad = []
for q in quoted:
    ok, why = verbatim(q)
    if not ok:
        bad.append(why)
chk(not bad,
    "every quoted log line (%d total, %d with elisions) is verbatim in a real log"
    % (len(quoted), len(elided)),
    "\n".join(bad[:8]))
last_dip = read(os.path.join(RUNS, ARMS[3], "dip.log")).strip().splitlines()[-1].strip()
chk(last_dip in text, "the real dip.log last line is quoted exactly",
    "last line: %s" % last_dip)

failpat = re.compile(r"JOB error|STUCK|OBJECTIVE FAIL|clip_skip|CLIP_SKIP")
live_hits = [(os.path.basename(f), len(failpat.findall(read(f)))) for f in live_out
             if failpat.search(read(f))]
chk(not live_hits, "no failure lines in any LIVE p7 *.out",
    "live hits: %s" % live_hits)
arch_hits = [(os.path.basename(f), len(failpat.findall(read(f))))
             for f in arch_out if failpat.search(read(f))]
chk(any(n for _, n in arch_hits),
    "the .failed-20261022 archive carries the STUCK/JOB-error evidence",
    "archive hits: %s" % arch_hits)

for a in GRAPH_ARMS:
    oj = os.path.join(RUNS, a, "objective.json")
    d = json.loads(read(oj))
    att = d.get("attempts") or [d]
    secs = att[0].get("secs", d.get("secs"))
    frames = att[0].get("frames", d.get("frames"))
    nbytes = att[0].get("bytes", d.get("bytes"))
    sheet = att[0].get("contact_sheet", d.get("contact_sheet"))
    sheet_b = os.path.getsize(sheet) if sheet and os.path.exists(sheet) else -1
    needles = ["%r" % secs, "{:,}".format(nbytes), "frames=%s" % frames]
    absent = [n for n in needles if n not in text]
    if sheet_b > 0 and "{:,}".format(sheet_b) not in text:
        absent.append("sheet bytes %s" % sheet_b)
    chk(not absent, "numbers for %s come from objective.json and are stated "
        "(secs=%s bytes=%s frames=%s sheet=%s B)"
        % (a, secs, nbytes, frames, sheet_b), "not stated: %s" % absent)
for name, size in (("base_reenc.mp4", 0), ("dipblack.mp4", 0), ("dipwhite.mp4", 0)):
    pth = os.path.join(RUNS, ARMS[3], name)
    chk("{:,}".format(os.path.getsize(pth)) in text,
        "DIP output bytes stated: %s" % name,
        "actual %s B" % os.path.getsize(pth))
chk("1443" in text, "DIP frame count 1443 stated")

rs1 = os.path.join(RUNS, "RS1_lowres_pool_sheet", "PROOF.md")
chk(not os.path.exists(rs1), "RS1 PROOF.md is absent on disk (documented gap)")
chk("RS1_lowres_pool_sheet" in text and "not on disk" in text,
    "the summary states the RS0/RS1 evidence gap instead of citing it as evidence")
for pth in (os.path.join(RUNS, ARMS[3], "dip.log"),
            os.path.join(RUNS, ARMS[3], "ffmpeg_cmd.txt")):
    chk(os.path.exists(pth), "cited evidence exists: %s" % pth)
chk(not os.path.exists(os.path.join(RUNS, ARMS[3], "objective.json")),
    "DIP has no objective.json (as the summary states)")
p("ALL CHECKS PASS" if not fails else "FAILURES: %s" % fails)
open(REPORT, "w", encoding="utf-8", newline="\r\n").write(
    "\r\n".join(buf) + "\r\n")
print("WROTE %s bytes=%d" % (REPORT, os.path.getsize(REPORT)))
