"""RS7 report verification (read-only, CPU only, no GPU/ComfyUI/llama-swap call).

Prints the measured values the RS7 report (ralph-community\notes\ali147_REPORT_rs7.md) claims, so the
report can be checked line by line: mp4 bytes/sha256/frame counts, objective.json secs, the status.log
JOB/OBJECTIVE lines, contact sheets, the two sbs_*.mp4 files, the sheet image, and the live FIX4
clips_json state. Writes nothing.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

FFPROBE = (r"C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/Gyan.FFmpeg_"
           r"Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe")
RUNS = r"C:/AI/community/runs"
ARMS = ["ali147_pool_ctrl_s51080000", "ali147_pool_fix1_s51080000",
        "ali147_pool_fix5_s51080000", "ali147_pool_refsheet_s51080000",
        "ali147_pool_refsheet_b_s51080000"]
DIP = "ali147_pool_dip_s51080000"
DIP_FILES = ["base_reenc.mp4", "dipblack.mp4", "dipwhite.mp4"]
SBS = [(r"ali147_pool_refsheet_s51080000/sbs_fix1_refsheet.mp4", "1bf55ff01b9fd5b56c0f5b8ae81e1d0286e71d5f5fd3d455a9c4696953247392"),
       (r"ali147_pool_refsheet_b_s51080000/sbs_refsheet_refsheetb.mp4", "05565b1cb7b4162179d94123c5c2cd5c051d6ef210e8fa3af786ff8d3fe0a537")]
SHEET_SRC = r"C:/Users/derek/5slock/approved_characters/REF_SHEETS_2026-10-19/RS016_portrait_1152x2016.png"
SHEET_IN = (r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/"
            r"RS016_portrait_1152x2016.png")
STILL_IN = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input/community/POOL_768x1344.png"
STILL_SRC = r"C:/Users/derek/5slock/approved_characters/POOL/COND_POOL_BIKINI_PORTRAIT.jpg"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def probe(p):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
         "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height",
         "-of", "csv=p=0", p],
        capture_output=True, text=True).stdout.strip().replace("\n", " | ")
    return out


def dur(p):
    return subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()


def aud(p):
    return subprocess.run(
        [FFPROBE, "-v", "error", "-select_streams", "a:0", "-show_entries",
         "stream=codec_name,sample_rate,channels", "-of", "csv=p=0", p],
        capture_output=True, text=True).stdout.strip()


print("=== rendered arms ===")
for arm in ARMS:
    d = os.path.join(RUNS, arm)
    mp4 = os.path.join(d, arm + ".mp4")
    print("\n## " + arm)
    print("mp4 exists=%s bytes=%s" % (os.path.exists(mp4), os.path.getsize(mp4) if os.path.exists(mp4) else "-"))
    if os.path.exists(mp4):
        print("mp4 sha256=" + sha(mp4))
        print("ffprobe=" + probe(mp4))
        print("dur=%s audio=%s" % (dur(mp4), aud(mp4)))
    obj = os.path.join(d, "objective.json")
    if os.path.exists(obj):
        j = json.load(open(obj, encoding="utf-8"))
        att = j.get("attempts")
        print("objective ok=%s secs=%s attempts=%s blackfreeze=%s" % (
            j.get("ok"), [a.get("secs") for a in att] if isinstance(att, list) else j.get("secs"),
            len(att) if isinstance(att, list) else "n/a", j.get("blackfreeze")))
    st = os.path.join(d, "status.log")
    if os.path.exists(st):
        txt = open(st, encoding="utf-8", errors="replace").read().splitlines()
        print("status.log lines=%d" % len(txt))
        for ln in txt:
            if re.search(r"JOB start|JOB end|OBJECTIVE|JOB error|REDO|STUCK|UNLOAD", ln):
                print("  " + ln)
        print("grep JOB error|CLIP_SKIP|redo|STUCK count=%d" % len(
            [l for l in txt if re.search(r"JOB error|CLIP_SKIP|[Rr]edo|STUCK|clip_skip", l)]))
    cs = os.path.join(d, arm + "_stills_contact.png")
    print("contact exists=%s bytes=%s" % (os.path.exists(cs), os.path.getsize(cs) if os.path.exists(cs) else "-"))
    for extra in ("request.api.json", arm + ".api.json"):
        p = os.path.join(d, extra)
        print("  %s exists=%s bytes=%s mtime=%s" % (extra, os.path.exists(p),
              os.path.getsize(p) if os.path.exists(p) else "-",
              time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(p))) if os.path.exists(p) else "-"))

print("\n=== graph provenance (cmp request.api.json vs <id>.api.json) ===")
for arm in ARMS:
    a = os.path.join(RUNS, arm, "request.api.json")
    b = os.path.join(RUNS, arm, arm + ".api.json")
    if os.path.exists(a) and os.path.exists(b):
        same = open(a, "rb").read() == open(b, "rb").read()
        print("%s identical=%s" % (arm, same))

print("\n=== DIP ===")
dl = os.path.join(RUNS, DIP, "dip.log")
for ln in open(dl, encoding="utf-8", errors="replace").read().splitlines():
    if re.search(r"DIP start|DIP end|segment frames|\.mp4", ln):
        print("  " + ln)
for f in DIP_FILES:
    p = os.path.join(RUNS, DIP, f)
    print("%s bytes=%s sha=%s" % (f, os.path.getsize(p), sha(p)))
    print("  ffprobe=" + probe(p) + " dur=" + dur(p) + " audio=" + aud(p))

print("\n=== sbs files (Max/harness) ===")
for rel, claimed in SBS:
    p = os.path.join(RUNS, rel)
    if os.path.exists(p):
        m = sha(p)
        print("%s bytes=%s sha=%s match=%s" % (rel, os.path.getsize(p), m, m == claimed))
        print("  ffprobe=" + probe(p) + " dur=" + dur(p))
    else:
        print("%s MISSING" % rel)

print("\n=== reference assets ===")
for label, p in [("sheet approved", SHEET_SRC), ("sheet comfy input", SHEET_IN),
                 ("start still comfy input", STILL_IN), ("start still approved", STILL_SRC)]:
    if os.path.exists(p):
        print("%s bytes=%s sha=%s size=%s" % (label, os.path.getsize(p), sha(p),
              __import__("PIL.Image", fromlist=["open"]).open(p).size))
    else:
        print("%s MISSING %s" % (label, p))

print("\n=== FIX4 live state ===")
d4 = os.path.join(RUNS, "ali147_pool_fix4_s51080000")
rq = os.path.join(d4, "request.api.json")
print("request.api.json bytes=%s mtime=%s" % (os.path.getsize(rq),
      time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(rq)))))
g = json.load(open(rq, encoding="utf-8"))
ext = [v for v in g.values() if v.get("class_type") == "MiniMaxH3Extender"]
cj = ext[0]["inputs"]["clips_json"]
print("clips_json type=%s" % type(cj).__name__)
d = json.loads(cj) if isinstance(cj, str) else cj
print("version=%s nclips=%d" % (d.get("version"), len(d["clips"])))
print("validated=%s" % [c.get("validated") for c in d["clips"]])
print("durations=%s" % [c.get("duration") for c in d["clips"]])
print("seeds=%s" % [c.get("seed") for c in d["clips"]])
print("mp4 in fix4 dir=%s" % [f for f in os.listdir(d4) if f.endswith(".mp4")])
st4 = os.path.join(d4, "status.log")
for ln in open(st4, encoding="utf-8", errors="replace").read().splitlines():
    if re.search(r"JOB start|JOB end|OBJECTIVE|REDO|STUCK", ln):
        print("  " + ln[:220])
res = r"C:/AI/community/p7/jobs/ali147_pool_fix4_s51080000.result.json"
print("fix4 result.json exists=%s" % os.path.exists(res))
if os.path.exists(res):
    print("  " + json.dumps(json.load(open(res, encoding="utf-8")))[:400])

print("\nDONE")
