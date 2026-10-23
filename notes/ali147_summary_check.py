"""ALI-147 FINAL summary self-check (read-only, CPU only).

Checks notes/ali147_summary.md against the FINAL line's checklist: file exists,
all five arms named, no empty table cells, no TBD/TODO placeholders, the
METHOD_ONLY + KEEP-is-Derrick labels, the CTRL-by-driver note, plus the
supporting facts the file asserts (sbs files, duplicate-mp4 check, JOB-error
grep over live p7 logs, RS1 PROOF existence, local time).
"""
import datetime
import glob
import hashlib
import os
import re

SUM = r"C:\AI\community\notes\ali147_summary.md"
RUNS = r"C:\AI\community\runs"
JOBS = r"C:\AI\community\p7\jobs"
ARMS = ["ali147_pool_ctrl_s51080000", "ali147_pool_fix1_s51080000",
        "ali147_pool_fix5_s51080000", "ali147_pool_dip_s51080000",
        "ali147_pool_fix4_s51080000"]

fails = []


def chk(ok, label):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        fails.append(label)


raw = open(SUM, "rb").read()
text = raw.decode("utf-8")
print("summary %s bytes=%d sha256=%s lines=%d"
      % (SUM, len(raw), hashlib.sha256(raw).hexdigest(), len(text.splitlines())))
chk(os.path.exists(SUM), "notes/ali147_summary.md exists")
for a in ARMS:
    chk(a in text, "arm named: %s (count=%d)" % (a, text.count(a)))
chk("METHOD_ONLY" in text, "METHOD_ONLY label present")
chk("KEEP is Derrick" in text, "KEEP-is-Derrick line present")
chk("rendered by the driver" in text, "CTRL-by-driver note present")
for k in ("render secs", "ffprobe", "contact sheet", "dip.log", "status.log",
          "bytes", "duration", "failures", "STUCK", "redo"):
    chk(k.lower() in text.lower(), "required column/term present: %s" % k)

empty = [ln for ln in text.splitlines()
         if ln.strip().startswith("|") and re.search(r"\|\s*\|", ln)]
chk(not empty, "no empty table cells (found %d)" % len(empty))
for ln in empty[:6]:
    print("   EMPTY-CELL: %s" % ln[:140])
for pad in ("TBD", "TODO", "FIXME", "placeholder"):
    chk(pad.lower() not in text.lower(), "no %s placeholder" % pad)
for sec in ("# Matrix", "### CTRL", "### FIX1", "### FIX5", "### DIP",
            "### FIX4", "## Failures", "## Appendix", "## Method notes"):
    chk(sec in text, "section present: %s" % sec)

mp4s = sorted(glob.glob(os.path.join(RUNS, "**", "ali147_pool_*.mp4"),
                        recursive=True))
chk(len(mp4s) == len(set(mp4s)), "no duplicate mp4 path (n=%d)" % len(mp4s))
print("   mp4s: %s" % [p.replace(RUNS + os.sep, "") for p in mp4s])
chk(all(p in text for p in mp4s), "every render under runs/ is listed in the summary")

sbs = sorted(glob.glob(os.path.join(RUNS, "**", "sbs_*"), recursive=True))
print("   sbs files: %s" % [os.path.relpath(p, RUNS) for p in sbs])
chk(all(p in text for p in sbs), "every sbs under runs/ is stated in the summary")

pats = re.compile(r"JOB error|CLIP_SKIP|STUCK|CLIP_SKIP|clip_skip|redo")
hits = []
for f in sorted(glob.glob(os.path.join(JOBS, "*.out"))):
    body = open(f, "r", encoding="utf-8", errors="replace").read()
    n = len(pats.findall(body))
    if n:
        hits.append((os.path.basename(f), n))
print("   live p7 *.out hits for JOB error|CLIP_SKIP|STUCK|clip_skip|redo: %s"
      % hits)
chk(hits == [("ali147_pool_fix4_s51080000.out", 1)],
    "live logs: only the expected redo-context line in fix4 .out (5 redos)")
live_stuck = [os.path.basename(f) for f in glob.glob(os.path.join(JOBS, "*.out"))
              if "STUCK" in open(f, "r", encoding="utf-8", errors="replace").read()]
chk(live_stuck == [], "no STUCK in any live p7 *.out (got %s)" % live_stuck)
rs1 = os.path.join(RUNS, "RS1_lowres_pool_sheet", "PROOF.md")
chk(os.path.exists(rs1), "RS1 PROOF.md cited path exists")
chk(os.path.exists(os.path.join(RUNS, "ali147_pool_dip_s51080000", "dip.log")),
    "DIP dip.log exists (the log the summary quotes)")
chk(os.path.exists(os.path.join(RUNS, "ali147_pool_dip_s51080000",
                                "ffmpeg_cmd.txt")),
    "DIP ffmpeg_cmd.txt exists (command evidence)")
for p in (os.path.join(RUNS, a, "objective.json") for a in ARMS[:3] + ARMS[4:]):
    chk(os.path.exists(p), "objective.json exists: %s" % p)
chk(not os.path.exists(os.path.join(RUNS, ARMS[3], "objective.json")),
    "DIP has no objective.json (as the summary states)")
print("local time: %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))
print("ALL CHECKS PASS" if not fails else "FAILURES: %s" % fails)
