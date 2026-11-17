"""ALI-147 FINAL summary probe (read-only, CPU only).

Collects, for each ALI-147 arm, the objective evidence the summary needs:
mp4 path / bytes / sha256, ffprobe packets + duration + audio, objective.json,
status.log (dip.log for DIP) JOB lines, p7 result.json, contact sheet,
and the failure history (*.failed-20261022 files, STUCK / redo mentions).

Writes notes/ali147-summary-20261022.txt. No GPU, no ComfyUI, no llama-swap,
no render, no ffmpeg encode - ffprobe only.
"""
import hashlib
import json
import os
import subprocess

FF = (r"C:\Users\derek\AppData\Local\Microsoft\Winget\Packages\Gyan.FFmpeg_"
      r"Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe")
RUNS = r"C:\AI\community\runs"
JOBS = r"C:\AI\community\p7\jobs"
BASE = os.path.join(RUNS, "p7_r2_c3_pmot_full_pool")
OUT = r"C:\AI\community\notes\ali147-summary-20261022.txt"

ARMS = [
    ("CTRL", "ali147_pool_ctrl_s51080000", ["ali147_pool_ctrl_s51080000.mp4"]),
    ("FIX1", "ali147_pool_fix1_s51080000", ["ali147_pool_fix1_s51080000.mp4"]),
    ("FIX5", "ali147_pool_fix5_s51080000", ["ali147_pool_fix5_s51080000.mp4"]),
    ("DIP", "ali147_pool_dip_s51080000",
     ["base_reenc.mp4", "dipblack.mp4", "dipwhite.mp4"]),
    ("FIX4", "ali147_pool_fix4_s51080000", ["ali147_pool_fix4_s51080000.mp4"]),
    ("REFSHEET", "ali147_pool_refsheet_s51080000",
     ["ali147_pool_refsheet_s51080000.mp4"]),
    ("REFSHEET_B", "ali147_pool_refsheet_b_s51080000",
     ["ali147_pool_refsheet_b_s51080000.mp4"]),
]

KEYS_STATUS = ("JOB start", "JOB end", "OBJECTIVE", "UNLOAD", "COMFY", "error",
               "STUCK", "redo", "SKIP")


def pil(path):
    img = __import__("PIL.Image", fromlist=["open"]).open(path)
    return img.size, img.mode, img.format


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(path, sel):
    args = [FF, "-v", "error", "-select_streams", sel, "-count_packets",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate,"
            "avg_frame_rate,nb_read_packets,sample_rate,channels,duration",
            "-of", "csv=p=0", path]
    r = subprocess.run(args, capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def ffdur(path):
    args = [FF, "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", path]
    r = subprocess.run(args, capture_output=True, text=True)
    return r.stdout.strip()


def txt(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def load(path):
    raw = txt(path)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return {"_unparsed": str(exc), "_raw": raw}


lines = []


def w(s=""):
    lines.append(s)
    print(s)


w("ALI-147 FINAL summary probe - read-only evidence dump")
w("CTRL render note: runs/ali147_pool_ctrl_s51080000 was rendered by the driver"
  " (status.log line tagged 'recorded by ali147_record_ctrl.py'), NOT by this"
  " Ralph loop; it has no request.api.json and no p7 result.json.")

for name, arm, vids in ARMS:
    d = os.path.join(RUNS, arm)
    w("")
    w("=" * 78)
    w("ARM %s  folder=%s  exists=%s" % (name, d, os.path.isdir(d)))
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        w("  file %s %s %s" % ("DIR " if os.path.isdir(p) else "FILE",
                               fn, os.path.getsize(p) if os.path.isfile(p) else "-"))
    for v in vids:
        p = os.path.join(d, v)
        if not os.path.exists(p):
            w("  MP4 MISSING %s" % v)
            continue
        w("  MP4 %s bytes=%d sha256=%s" % (p, os.path.getsize(p), sha256(p)))
        w("      fmt duration=%s" % ffdur(p))
        for row in ffprobe(p, "v:0"):
            w("      v: %s" % row)
        for row in ffprobe(p, "a:0"):
            w("      a: %s" % row)
    obj = load(os.path.join(d, "objective.json"))
    if obj is not None:
        w("  objective.json ok=%s" % obj.get("ok"))
        if isinstance(obj.get("secs"), (int, float)):
            w("  objective.json secs=%s (flat, driver form)" % obj.get("secs"))
        for i, at in enumerate(obj.get("attempts", []) or []):
            w("  objective.json attempt[%d] secs=%s frames=%s audio=%s "
              "dur=%s bytes=%s blackfreeze=%s"
              % (i, at.get("secs"), at.get("frames"), at.get("audio"),
                 at.get("duration"), at.get("bytes"), at.get("blackfreeze")))
        for k in ("frames", "duration", "bytes", "audio", "contact_sheet",
                  "sha256", "blackfreeze", "file"):
            if k in obj:
                w("  objective.json %s=%s" % (k, obj[k]))
        w("  objective.json n_attempts=%d redos=%d"
          % (len(obj.get("attempts", []) or []) or (1 if obj.get("secs") else 0),
             max(0, len(obj.get("attempts", []) or []) - 1)))
    else:
        w("  objective.json ABSENT (DIP is not a run_graph_job job: no "
          "objective.json; render secs = 0, CPU ffmpeg only)")
    for log in ("status.log", "dip.log"):
        t = txt(os.path.join(d, log))
        w("  %s %s" % (log, "ABSENT" if t is None else "bytes=%d" % len(t.encode())))
        if t:
            for ln in t.splitlines():
                if any(k in ln for k in KEYS_STATUS) or log == "dip.log":
                    w("      | %s" % ln)
    for log in ("ffmpeg_cmd.txt",):
        t = txt(os.path.join(d, log))
        if t:
            w("  %s bytes=%d (first 400 chars)" % (log, len(t.encode())))
            w("      | %s" % t[:400].replace("\n", " | "))
    for sub in ("failed-20261022",):
        sd = os.path.join(d, sub)
        if os.path.isdir(sd):
            w("  %s/ contents: %s" % (sub, sorted(os.listdir(sd))))
    for suf in (".out", ".err.out", ".result.json",
                ".out.failed-20261022", ".err.out.failed-20261022",
                ".result.json.failed-20261022"):
        p = os.path.join(JOBS, arm + suf)
        if not os.path.exists(p):
            continue
        w("  p7/jobs%s bytes=%d" % (arm + suf, os.path.getsize(p)))
        if suf.endswith(".result.json"):
            rj = load(p)
            if isinstance(rj, dict):
                w("      result ok=%s rc=%s started=%s finished=%s wall_min=%s "
                  "budget_used_min=%s budget_cap_min=%s note=%s"
                  % (rj.get("ok"), rj.get("rc"), rj.get("started"),
                     rj.get("finished"), rj.get("wall_min"),
                     rj.get("budget_used_min"), rj.get("budget_cap_min"),
                     rj.get("note")))
                w("      result outputs=%s" % rj.get("outputs"))
        else:
            for ln in (txt(p) or "").splitlines():
                if any(k in ln for k in ("JOB", "OBJECTIVE", "STUCK", "redo",
                                         "error", "Error", "rc=", "dip")):
                    w("      | %s" % ln)
    for sheet in sorted(fn for fn in os.listdir(d) if fn.endswith(".png")):
        p = os.path.join(d, sheet)
        w("  CONTACT %s bytes=%d sha256=%s" % (p, os.path.getsize(p), sha256(p)))

w("")
w("=" * 78)
w("BASE minute (the control for DIP and FIX4), read-only")
for fn in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, fn)
    if os.path.isfile(p):
        w("  file %s %d" % (fn, os.path.getsize(p)))
for v in ("p7_r2_c3_pmot_full_pool_seg1.mp4", "p7_r2_c3_pmot_full_pool_seg2.mp4",
          "p7_r2_c3_pmot_full_pool_seg3.mp4",
          "p7_r2_c3_pmot_full_pool_stitched.mp4"):
    p = os.path.join(BASE, v)
    if not os.path.exists(p):
        w("  MP4 MISSING %s" % v)
        continue
    w("  MP4 %s bytes=%d sha256=%s dur=%s" % (p, os.path.getsize(p), sha256(p),
                                              ffdur(p)))
    for row in ffprobe(p, "v:0"):
        w("      v: %s" % row)
out_txt = txt(os.path.join(JOBS, "p7_r2_c3_pmot_full_pool.out")) or ""
w("  base run .out lines mentioning secs/JOB:")
for ln in out_txt.splitlines():
    if "secs" in ln or "JOB" in ln:
        w("      | %s" % ln)

w("")
w("=" * 78)
w("Existence checks for referenced evidence files")
for p in (r"C:\AI\community\notes\ali147_REPORT_rs7.md",
          r"C:\AI\community\notes\ali147-fix4-proof-verify-20261022.txt",
          r"C:\AI\community\notes\ali147_refsheet_rs4_verify.md",
          r"C:\AI\community\notes\ali147_refsheet_b_rs6_verify.md",
          r"C:\AI\community\runs\ali147_pool_fix1_s51080000\PROOF.md",
          r"C:\AI\community\runs\ali147_pool_fix5_s51080000\PROOF.md",
          r"C:\AI\community\runs\ali147_pool_dip_s51080000\PROOF.md",
          r"C:\AI\community\runs\ali147_pool_fix4_s51080000\PROOF.md",
          r"C:\AI\community\runs\ali147_pool_fix4_s51080000\fairness.txt",
          r"C:\AI\community\logs\p7_budget.json",
          r"C:\Users\derek\5slock\ralph-community\logs\p7_budget.json",
          r"C:\AI\community\notes\ali147_summary.md"):
    w("  %s exists=%s size=%s"
      % (p, os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else "-"))
w("")
w("=" * 78)
w("Identity / reference images (read-only, PIL + sha256)")
for p in (r"C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_BIKINI_PORTRAIT.jpg",
          r"C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_PORTRAIT.jpg",
          r"C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_PORTRAIT_v2.jpg",
          r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community"
          r"\RS016_portrait_1152x2016.png",
          r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community"
          r"\POOL_768x1344.png"):
    if not os.path.exists(p):
        w("  IMAGE ABSENT %s" % p)
        continue
    size, mode, fmt_ = pil(p)
    w("  IMAGE %s bytes=%d sha256=%s PIL=%s mode=%s format=%s"
      % (p, os.path.getsize(p), sha256(p), size, mode, fmt_))
w("  approved_characters\\POOL listing: %s"
  % sorted(os.listdir(r"C:\Users\derek\5slock\approved_characters\POOL")))
for p in (r"C:\AI\community\runs\RS0_lowres_resolution_probe",
          r"C:\AI\community\runs\RS1_lowres_pool_sheet",
          r"C:\AI\community\notes\ali147_report_rs7.md",
          r"C:\AI\community\notes\ali147_rs1_lowres_build.py",
          r"C:\AI\community\notes\ali147_rs1_lowres_selfcheck.py"):
    w("  RS-artifact %s exists=%s" % (p, os.path.exists(p)))

for d in (RUNS,):
    w("  sbs files under runs: %s"
      % [os.path.join(r, f) for r, _s, fs in os.walk(d) for f in fs
         if f.startswith("sbs_")])

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines) + "\n")
print("WROTE %s bytes=%d" % (OUT, os.path.getsize(OUT)))
