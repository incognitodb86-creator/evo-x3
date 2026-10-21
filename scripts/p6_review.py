# P7 review step (Derek 2026-10-20, "Forge job prep"): LOCAL-ONLY review + ranking of finished community videos.
#   ffmpeg frame sampling -> cheap CPU metrics (numpy/cv2, no GPU) -> local VLM judge through llama-swap with a FIXED rubric
#   (absolute 1-10 per dimension + short reasons, JSON) + swapped-order pairwise comparisons -> ranked list (.md + .json).
# Never renders, never calls ComfyUI, never sends anything off the machine. Calls gpu_guard.ps1 FIRST and refuses (exit 3) when BUSY.
# Run by the Ralph harness (ralph-community\ralph.ps1 P7 job runner) between iterations - never by Forge (headless guard blocks p6*.py).
# usage:
#   python p6_review.py rank --preset p6 [--out C:\AI\community\runs\P6_RANKING] [--judge qwen3vl_judge] [--no-model]
#   python p6_review.py rank --cand RUN[:segN] --cand ... --out <prefix>
#   python p6_review.py compare --pair PARENT=CHILD [--pair ...] --out <prefix>     (PARENT/CHILD = RUN or RUN:segN)
#   python p6_review.py checkshots <shots.json> <job_id>                            (harness pre-render validation; exit 0 ok / 4 bad)
# exit codes: 0 ok, 2 usage/input error, 3 refused (GPU busy / lock held / adults-only guard), 4 checkshots rejected, 5 judge failure
import argparse, base64, datetime, io, json, math, os, re, shutil, subprocess, sys, time, urllib.error, urllib.request

W = r"C:\AI\community"
RUNS = os.path.join(W, "runs"); SHOTS = os.path.join(W, "shots"); SCRIPTS = os.path.join(W, "scripts")
FFD = r"C:\Users\derek\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
FFMPEG = os.path.join(FFD, "ffmpeg.exe") if os.path.exists(os.path.join(FFD, "ffmpeg.exe")) else (shutil.which("ffmpeg") or "ffmpeg")
FFPROBE = os.path.join(FFD, "ffprobe.exe") if os.path.exists(os.path.join(FFD, "ffprobe.exe")) else (shutil.which("ffprobe") or "ffprobe")
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
LOCK = r"C:\AI\director\scripts\gpu_lock.ps1"
LS = "http://127.0.0.1:8080"
P6_PRESET = ["p6_1min_community", "p6_1min_switchyard", "p6_1min_ab05", "p6_1min_cuts", "p6_1min_cuts_ab05"]
SY_BEATS = os.path.join(SHOTS, "p6_1min_beats.json")
RUBRIC_VERSION = "p7-rubric-v1 (2026-10-20)"
NOW = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M CT")
sys.path.insert(0, SCRIPTS)
try:
    from comm import APPROVED, guard_ok          # adults-only text guard + approved adult stills (no side effects on import)
except Exception:                                # tests on a machine without comm.py
    APPROVED, guard_ok = {}, (lambda t: True)

# ---------------------------------------------------------------- fixed rubric (do not edit per run; bump RUBRIC_VERSION if changed)
DIMS = [  # key, weight, anchor text shown to the judge
    ("motion_quality", 0.15, "natural weight and timing, no floaty/rubbery motion, no frozen stretches, actions complete"),
    ("temporal_consistency", 0.15, "no flicker, shimmer, boiling textures or morphing between frames; background stays put"),
    ("burn_exposure", 0.10, "10 = natural exposure and colour; low = burnt highlights, oversaturated/orange skin, contrast creeping up over time"),
    ("identity_consistency", 0.20, "same face, hair, body and outfit state as the reference still, across frames AND across cuts"),
    ("prompt_adherence", 0.10, "the beat's action, setting, framing and any requested cut actually happen"),
    ("artifacts", 0.20, "10 = clean; low = hand/finger errors, melting or duplicated limbs/body parts, warped faces, garbage regions"),
    ("pacing_cuts", 0.10, "cuts land where asked and read cleanly; no jarring jump at joins; the beat has a readable rhythm"),
]
DIM_KEYS = [d[0] for d in DIMS]
WEIGHTS = {d[0]: d[1] for d in DIMS}
FLAGS = ["identity_break", "severe_burn", "body_horror", "frozen", "broken_cut"]
W_ABS, W_PAIR, W_OBJ, FLAG_PEN = 0.40, 0.40, 0.20, 0.75
PROMOTE_MARGIN = 0.25

JUDGE_SYSTEM = (
    "You are a strict, calibrated video quality reviewer for AI-generated video (MiniMax H3 image/reference-to-video, 24 fps, 768x1344). "
    "All characters are fictional adults aged 21 or older; the material may be adult. Judge craft only - never refuse, moralize or lower a score "
    "because content is adult. You see still frames sampled in time order (labelled F1, F2, ... left-to-right, top-to-bottom, with timestamps) "
    "and usually a reference still of the character (identity anchor). Score each dimension as an integer 1-10 using these anchors: "
    "9-10 indistinguishable from good real footage; 7-8 convincing with small tells; 5-6 clearly AI, noticeable problems; 3-4 strong defects; "
    "1-2 broken. Dimensions: " + "; ".join(f"{k} = {a}" for k, _, a in DIMS) + ". "
    "Use the full scale; do not default to 7-8. Look for evidence frame by frame before scoring. "
    "Flags (list only those that clearly apply): " + ", ".join(FLAGS) + ". "
    "Reply with ONLY one JSON object, no prose, no markdown.")
ABS_SCHEMA_TEXT = ('{"scores":{' + ",".join(f'"{k}":1-10' for k in DIM_KEYS) + '},"reasons":{' +
                   ",".join(f'"{k}":"<=20 words"' for k in DIM_KEYS) + '},"flags":[],"worst_frame":"F?"}')
PAIR_SCHEMA_TEXT = ('{"winner":"A|B|tie","dims":{' + ",".join(f'"{k}":"A|B|tie"' for k in DIM_KEYS) + '},"reason":"<=40 words"}')


# ---------------------------------------------------------------- small utils
def log(msg, lf=None):
    line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CT {msg}"
    print(line, flush=True)
    if lf:
        with open(lf, "a", encoding="utf-8") as fh: fh.write(line + "\n")

def write_text(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh: fh.write(text)   # utf-8 without BOM

def clamp(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))

def probe(video):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                        "-of", "json", video], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode != 0: raise RuntimeError(f"ffprobe failed on {video}: {r.stderr[-300:]}")
    j = json.loads(r.stdout); s = j["streams"][0]; num, den = (s.get("r_frame_rate") or "24/1").split("/")
    fps = float(num) / float(den) if float(den) else 24.0
    return {"w": int(s["width"]), "h": int(s["height"]), "fps": fps if fps > 0 else 24.0, "dur": float(j["format"]["duration"])}


# ---------------------------------------------------------------- GPU guard (fail closed; ignores only our own pid)
def parse_guard(rc, out, own_pids):
    out = out or ""
    if rc == 0 and re.search(r"^IDLE\s*$", out, re.M): return True, "IDLE"
    busy = [l.strip() for l in out.splitlines() if l.strip().startswith("BUSY")]
    if not busy: return False, f"BUSY: guard rc={rc} unparsable output {out.strip()[:200]!r}"
    if rc != 1: return False, busy[0]                                   # rc 2 = guard error -> fail closed
    reasons = [x.strip() for x in busy[0].split(":", 1)[1].split(";") if x.strip()]
    keep = [x for x in reasons if not any(re.search(rf"\bpid {p}\b", x) for p in own_pids)]
    return (len(keep) == 0), ("IDLE (only this review process matched)" if not keep else "BUSY: " + "; ".join(keep))

def run_guard(nohttp=False, runner=subprocess.run):
    args = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD] + (["-NoHttp"] if nohttp else [])
    try: r = runner(args, capture_output=True, text=True, timeout=90)
    except Exception as e: return False, f"BUSY: guard could not run ({e})"
    return parse_guard(r.returncode, r.stdout, {os.getpid(), os.getppid()})

def parse_util(outputs):
    """nvidia-smi 'util, mem' csv lines -> (mean util %, max mem MiB); unparsable -> (100, 0) = fail closed."""
    u, m = [], []
    for o in outputs:
        try: a, b = [float(x) for x in o.strip().splitlines()[0].split(",")[:2]]; u.append(a); m.append(b)
        except Exception: return 100.0, 0.0
    return (sum(u) / len(u), max(m)) if u else (100.0, 0.0)

def gpu_util(samples=5, runner=subprocess.run):
    """gpu_guard does not see llama-swap model work (benches, another agent's chat): sample real GPU load before taking the GPU."""
    outs = []
    for i in range(samples):
        try: outs.append(runner(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout)
        except Exception: outs.append("")
        if i < samples - 1: time.sleep(1)
    return parse_util(outs)

def process_table(runner=subprocess.run):
    r = runner(["powershell.exe", "-NoProfile", "-Command", "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"],
               capture_output=True, text=True, timeout=90)
    rows = json.loads(r.stdout); rows = rows if isinstance(rows, list) else [rows]
    return {int(x["ProcessId"]): (int(x.get("ParentProcessId") or 0), x.get("CommandLine") or "") for x in rows}

def inside_agent(table, pid):
    """True when any ancestor is the pi coding agent (Forge). Only the Ralph harness may start a model review, never Forge itself."""
    seen = set()
    while pid and pid not in seen and len(seen) < 40:
        seen.add(pid); ppid, cl = table.get(pid, (0, ""))
        if re.search(r"pi-coding-agent|@earendil-works", cl, re.I): return True
        pid = ppid
    return False

def lock(action, runner=subprocess.run):
    r = runner(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", LOCK, "-" + action, "-Owner", str(os.getpid()),
                "-Note", "p6_review"], capture_output=True, text=True, timeout=60)
    return r.returncode == 0, (r.stdout or "").strip()


# ---------------------------------------------------------------- candidates (run dirs written by batch_queue.py / sy_1min.py)
_SHOT_CACHE = None
def find_shot(sid):
    global _SHOT_CACHE
    if _SHOT_CACHE is None:
        _SHOT_CACHE = {}
        for f in sorted(os.listdir(SHOTS)) if os.path.isdir(SHOTS) else []:
            if not f.endswith(".json"): continue
            try: data = json.load(open(os.path.join(SHOTS, f), encoding="utf-8"))
            except Exception: continue
            if isinstance(data, list):
                for s in data:
                    if isinstance(s, dict) and "id" in s: _SHOT_CACHE.setdefault(s["id"], s)
    return _SHOT_CACHE.get(sid)

def beats_of(entry):
    sid = entry.get("id") or entry.get("tag")
    sh = find_shot(sid) or entry
    return [b for b in [sh.get("beat")] + list(sh.get("chunks") or []) if b]

def resolve(spec, runs_dir=None):
    """spec = RUN or RUN:segN -> dict(name, video, segments[(file, t0, t1, beats)], image, kind)."""
    runs_dir = runs_dir or RUNS
    run, _, seg = spec.partition(":")
    if not re.fullmatch(r"p[67]_[a-z0-9_]+", run) or (seg and not re.fullmatch(r"seg[1-9]", seg)):
        raise ValueError(f"bad candidate spec {spec!r} (want p6_xxx / p7_xxx, optional :segN)")
    rd = os.path.join(runs_dir, run)
    rj = os.path.join(rd, "results.json")
    res = json.load(open(rj, encoding="utf-8")) if os.path.exists(rj) else []
    if seg:
        m = [r for r in res if str(r.get("id") or r.get("tag") or "").endswith("_" + seg)]
        if not m: raise ValueError(f"{spec}: no {seg} in {rj}")
        e = m[0]; video = e["file"]; d = probe(video)["dur"]
        return {"name": spec, "video": video, "image": e.get("image"), "kind": "segment",
                "segments": [{"file": video, "t0": 0.0, "t1": d, "beats": beats_of(e)}]}
    video = os.path.join(rd, f"{run}_stitched.mp4")
    if not os.path.exists(video): raise ValueError(f"{spec}: missing {video}")
    segs, t = [], 0.0
    for e in res:
        f = e.get("file")
        if not f or not os.path.exists(f): continue
        d = probe(f)["dur"]; segs.append({"file": f, "t0": t, "t1": t + d, "beats": beats_of(e)}); t += d
    image = next((e.get("image") for e in res if e.get("image") in APPROVED), None) or "D15"
    if run == "p6_1min_switchyard" or not segs or not all(s["beats"] for s in segs):
        # Switchyard cells carry no beat text: use the shared 6-beat file and equal windows over the whole minute
        beats = json.load(open(SY_BEATS, encoding="utf-8"))["beats"] if os.path.exists(SY_BEATS) else ["(beat text unavailable)"]
        dur = probe(video)["dur"]; n = len(beats)
        cells = segs
        segs = [{"file": None, "t0": dur * i / n, "t1": dur * (i + 1) / n, "beats": [b]} for i, b in enumerate(beats)]
        return {"name": spec, "video": video, "image": image, "kind": "full", "segments": segs,
                "seams": [c["t1"] for c in cells[:-1]]}
    return {"name": spec, "video": video, "image": image, "kind": "full", "segments": segs, "seams": [s["t1"] for s in segs[:-1]]}

def windows_of(cand):
    """one window per beat: each segment span split evenly across its beats. -> [(seg_index, t0, t1, beat)]"""
    out = []
    for si, s in enumerate(cand["segments"]):
        n = max(1, len(s["beats"])); span = (s["t1"] - s["t0"]) / n
        for bi in range(n): out.append((si, s["t0"] + bi * span, s["t0"] + (bi + 1) * span, s["beats"][bi] if s["beats"] else ""))
    return out


# ---------------------------------------------------------------- frame extraction (ffmpeg) + contact sheets (PIL)
def extract_frames(video, t0, t1, n, out_dir, tag, width=320):
    """n frames evenly spread over (t0, t1), skipping 0.25 s at each edge (joins/cuts). Returns [(png, timestamp)]."""
    os.makedirs(out_dir, exist_ok=True)
    a, b = t0 + 0.25, max(t0 + 0.30, t1 - 0.25)
    ts = [a + (b - a) * (k + 0.5) / n for k in range(n)]
    out = []
    for k, t in enumerate(ts):
        p = os.path.join(out_dir, f"{tag}_{k + 1:02d}.png")
        r = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf", f"scale={width}:-2", p],
                           capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(p): out.append((p, t))
    if not out: raise RuntimeError(f"ffmpeg extracted no frames from {video} [{t0:.2f},{t1:.2f}]")
    return out

def contact_sheet(frames, out_path, cols=3, label=True):
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(p).convert("RGB") for p, _ in frames]
    w, h = ims[0].size; rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0)); d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype("arial.ttf", max(14, w // 16))
    except Exception: font = ImageFont.load_default()
    for i, (im, (_, t)) in enumerate(zip(ims, frames)):
        x, y = (i % cols) * w, (i // cols) * h; sheet.paste(im.resize((w, h)), (x, y))
        if label:
            txt = f"F{i + 1} {t:.1f}s"; d.rectangle([x, y, x + 9 * len(txt) + 8, y + 24], fill=(0, 0, 0)); d.text((x + 4, y + 3), txt, fill=(255, 255, 0), font=font)
    sheet.save(out_path, quality=88)
    return out_path

def ref_image(key, out_dir, width=320):
    src = APPROVED.get(key or "")
    if not src or not os.path.exists(src): return None
    from PIL import Image
    im = Image.open(src).convert("RGB"); im = im.resize((width, int(im.size[1] * width / im.size[0])))
    p = os.path.join(out_dir, f"ref_{key}.jpg"); os.makedirs(out_dir, exist_ok=True); im.save(p, quality=88); return p


# ---------------------------------------------------------------- cheap objective metrics (CPU only)
def _decode(video, w, h, pix, fps=None):
    import numpy as np
    vf = (f"fps={fps}," if fps else "") + f"scale={w}:{h}:flags=area"
    r = subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-threads", "2", "-i", video, "-vf", vf, "-f", "rawvideo", "-pix_fmt", pix, "-"], capture_output=True)
    if r.returncode != 0: raise RuntimeError(f"ffmpeg decode failed {video}: {r.stderr[-300:]!r}")
    c = 1 if pix == "gray" else 3; n = len(r.stdout) // (w * h * c)
    a = np.frombuffer(r.stdout[: n * w * h * c], dtype=np.uint8)
    return a.reshape((n, h, w) if c == 1 else (n, h, w, c))

def compute_metrics(video, seams=(), spans=None):
    """VBench-flavoured, model-free metrics. spans = [(t0,t1)] segments for within-segment drift (default whole video)."""
    import numpy as np, cv2
    info = probe(video); fps = info["fps"]
    gw = 96; gh = max(2, int(round(gw * info["h"] / info["w"] / 2)) * 2)
    g = _decode(video, gw, gh, "gray").astype(np.float32)                       # native fps, tiny
    T = len(g)
    if T < 4: raise RuntimeError(f"too few frames in {video}")
    d1 = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))                            # motion / frame change, len T-1
    med = float(np.median(d1)); thr = max(15.0, 4.0 * med + 8.0)
    cut_idx = []
    for i in np.where(d1 > thr)[0]:
        if not cut_idx or i - cut_idx[-1] > 6: cut_idx.append(int(i))
    seam_idx = [int(round(s * fps)) - 1 for s in seams]
    excl = set()
    for i in cut_idx + seam_idx:
        excl.update(range(i - 2, i + 3))
    keep1 = np.array([i not in excl for i in range(T - 1)])
    d2 = np.abs(g[2:] - 2 * g[1:-1] + g[:-2]).mean(axis=(1, 2))                 # temporal 2nd difference (flicker / boiling)
    keep2 = np.array([(i not in excl) and (i + 1 not in excl) for i in range(T - 2)])
    y = g.mean(axis=(1, 2)); k = 9
    ma = np.convolve(np.pad(y, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    hp = (y - ma)[1:-1]
    lum_flicker = float(np.std(hp[keep2])) if keep2.any() else 0.0
    motion = float(d1[keep1].mean()) if keep1.any() else 0.0
    tex_flicker = float(d2[keep2].mean() / (motion + 1e-3)) if keep2.any() else 0.0
    freeze = float((d1[keep1] < 0.25).mean()) if keep1.any() else 0.0
    seam_ratio = max([float(d1[i] / (med + 1e-3)) for i in seam_idx if 0 <= i < len(d1)] or [0.0])
    # colour / burn / sharpness at 3 fps, 288 wide
    cw = 288; ch = max(2, int(round(cw * info["h"] / info["w"] / 2)) * 2)
    rgb = _decode(video, cw, ch, "rgb24", fps=3)
    ts = (np.arange(len(rgb)) + 0.5) / 3.0
    sat, clip, sharp, lab_ab = [], [], [], []
    for fr in rgb:
        hsv = cv2.cvtColor(fr, cv2.COLOR_RGB2HSV); s = hsv[..., 1].astype(np.float32) / 255; v = hsv[..., 2].astype(np.float32) / 255
        sat.append(float(s.mean())); clip.append(float(((v > 0.98) | ((s > 0.85) & (v > 0.85))).mean()))
        gray = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY); sharp.append(float(cv2.Laplacian(gray, cv2.CV_32F).var()))
        lab = cv2.cvtColor(fr, cv2.COLOR_RGB2LAB).astype(np.float32); lab_ab.append((float(lab[..., 1].mean()), float(lab[..., 2].mean())))
    sat, clip, sharp = np.array(sat), np.array(clip), np.array(sharp); lab_ab = np.array(lab_ab)
    spans = spans or [(0.0, info["dur"])]
    # drift is measured WITHIN shots: split each segment at detected cuts (an intended cut to a close-up is not drift); shots < 3 s skipped
    cut_t = sorted(set([(i + 1) / fps for i in cut_idx] + list(seams)))
    shots = []
    for (a, b) in spans:
        edges = [a] + [t for t in cut_t if a + 0.5 < t < b - 0.5] + [b]
        shots += [(x, y) for x, y in zip(edges[:-1], edges[1:]) if y - x >= 3.0]
    seg = []
    for (a, b) in shots:
        q = (b - a) * 0.25; e = (ts >= a) & (ts < a + q); l = (ts > b - q) & (ts <= b)
        if e.sum() == 0 or l.sum() == 0: continue
        seg.append({"t0": round(a, 2), "t1": round(b, 2),
                    "sat_drift": float(sat[l].mean() / (sat[e].mean() + 1e-6) - 1),
                    "clip_late": float(clip[l].mean()),
                    "sharp_drift": float(sharp[l].mean() / (sharp[e].mean() + 1e-6) - 1),
                    "color_drift_ab": float(np.linalg.norm(lab_ab[l].mean(axis=0) - lab_ab[e].mean(axis=0)))})
    m = {"frames": T, "fps": fps, "duration": round(info["dur"], 3), "cuts_detected": len(cut_idx),
         "cut_times": [round((i + 1) / fps, 2) for i in cut_idx], "motion": round(motion, 3), "lum_flicker": round(lum_flicker, 3),
         "tex_flicker": round(tex_flicker, 3), "freeze_frac": round(freeze, 3), "seam_ratio": round(seam_ratio, 2),
         "sat_mean": round(float(sat.mean()), 4), "clip_frac": round(float(clip.mean()), 4), "sharpness": round(float(sharp.mean()), 1),
         "sat_drift_max": round(max([s["sat_drift"] for s in seg] or [0.0]), 4), "clip_late_max": round(max([s["clip_late"] for s in seg] or [0.0]), 4),
         "sharp_drift_min": round(min([s["sharp_drift"] for s in seg] or [0.0]), 4),
         "color_drift_max": round(max([s["color_drift_ab"] for s in seg] or [0.0]), 3), "shots": seg}
    m["objective_score"], m["objective_penalties"] = objective_score(m)
    return m

def objective_score(m):
    """0-10 heuristic from the metrics above (thresholds are first-pass; see research doc). Lower is worse."""
    pen = {
        "lum_flicker": clamp((m["lum_flicker"] - 0.4) / 1.6) * 2.0,
        "tex_flicker": clamp((m["tex_flicker"] - 1.15) / 0.35) * 1.5,   # P6 clips measured 1.14-1.26
        "burn_sat_drift": clamp((m["sat_drift_max"] - 0.05) / 0.25) * 2.0,
        "burn_clip": clamp((m["clip_late_max"] - 0.01) / 0.05) * 1.5,
        "blur_drift": clamp((-m["sharp_drift_min"] - 0.10) / 0.40) * 1.0,
        "color_drift": clamp((m["color_drift_max"] - 3.0) / 9.0) * 1.0,
        "freeze": clamp((m["freeze_frac"] - 0.10) / 0.40) * 1.5,
        "seam_jump": clamp((m["seam_ratio"] - 3.0) / 7.0) * 0.5,
    }
    return round(max(0.0, 10.0 - sum(pen.values())), 2), {k: round(v, 2) for k, v in pen.items()}


# ---------------------------------------------------------------- judge client (llama-swap OpenAI API, local model only)
def b64(path):
    mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

def http_chat(model, system, parts, max_tokens=900, timeout=900):
    body = {"model": model, "temperature": 0.0, "top_p": 1.0, "max_tokens": max_tokens, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": parts}]}
    def post(b):
        req = urllib.request.Request(LS + "/v1/chat/completions", data=json.dumps(b).encode(), headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    try: r = post(body)
    except urllib.error.HTTPError as e:
        if e.code != 400: raise
        body.pop("response_format"); r = post(body)                  # server without json mode
    return (r["choices"][0]["message"].get("content") or "").split("</think>")[-1].strip()

def parse_json_reply(text):
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip(), flags=re.I | re.M)
    i = t.find("{")
    if i < 0: raise ValueError("no JSON object in reply")
    obj, _ = json.JSONDecoder().raw_decode(t[i:])
    if not isinstance(obj, dict): raise ValueError("reply JSON is not an object")
    return obj

def norm_abs(obj):
    sc = obj.get("scores", obj); rs = obj.get("reasons", {}) or {}
    scores = {}
    for k in DIM_KEYS:
        v = sc.get(k)
        if isinstance(v, dict): v = v.get("score")
        try: scores[k] = int(round(clamp(float(v), 1, 10)))
        except (TypeError, ValueError): scores[k] = None
    flags = [f for f in (obj.get("flags") or []) if f in FLAGS]
    return {"scores": scores, "reasons": {k: str(rs.get(k, ""))[:200] for k in DIM_KEYS}, "flags": flags,
            "worst_frame": str(obj.get("worst_frame", ""))[:8]}

def norm_pair(obj):
    w = str(obj.get("winner", "tie")).strip().upper()
    w = w if w in ("A", "B") else "TIE"
    dims = {k: (str((obj.get("dims") or {}).get(k, "tie")).strip().upper()) for k in DIM_KEYS}
    dims = {k: (v if v in ("A", "B") else "TIE") for k, v in dims.items()}
    return {"winner": w, "dims": dims, "reason": str(obj.get("reason", ""))[:300]}

class Judge:
    def __init__(self, model, chat=None, lf=None):
        self.model, self.chat, self.lf = model, (chat or http_chat), lf
        self.calls = 0; self.asks = 0; self.failures = 0; self.secs = 0.0
    def ask(self, parts, normalizer, max_tokens=900):
        last = None; self.asks += 1
        for attempt in range(2):
            t0 = time.time(); self.calls += 1
            try:
                txt = self.chat(self.model, JUDGE_SYSTEM, parts if attempt == 0 else parts + [{"type": "text", "text": "Return ONLY the JSON object."}], max_tokens)
                self.secs += time.time() - t0
                return normalizer(parse_json_reply(txt))
            except Exception as e:
                self.secs += time.time() - t0; last = e; log(f"judge reply unusable (attempt {attempt + 1}): {e}", self.lf)
        self.failures += 1
        return None

def T(text): return {"type": "text", "text": text}
def I(path): return {"type": "image_url", "image_url": {"url": b64(path)}}


# ---------------------------------------------------------------- ranking maths (no model needed)
def weighted(scores):
    got = [(WEIGHTS[k], v) for k, v in scores.items() if v is not None]
    return round(sum(w * v for w, v in got) / sum(w for w, _ in got), 3) if got else None

def aggregate_abs(window_cards, global_card):
    """per dim: 0.6 * mean over windows + 0.4 * global call; video abs = 0.7 * weighted + 0.3 * weakest window (weakest-link)."""
    per_dim = {}
    for k in DIM_KEYS:
        wv = [c["scores"][k] for c in window_cards if c and c["scores"].get(k) is not None]
        gv = global_card["scores"].get(k) if global_card else None
        if wv and gv is not None: per_dim[k] = round(0.6 * sum(wv) / len(wv) + 0.4 * gv, 3)
        elif wv: per_dim[k] = round(sum(wv) / len(wv), 3)
        else: per_dim[k] = gv
    wscores = [weighted(c["scores"]) for c in window_cards if c]
    wscores = [x for x in wscores if x is not None]
    base = weighted(per_dim)
    if base is None: return per_dim, None, None
    weakest = min(wscores) if wscores else base
    return per_dim, round(0.7 * base + 0.3 * weakest, 3), weakest

def count_flags(window_cards, global_card):
    """a flag counts when the global call raises it or at least 2 windows do."""
    c = {}
    for card in window_cards:
        for f in (card or {}).get("flags", []): c[f] = c.get(f, 0) + 1
    out = {f for f, n in c.items() if n >= 2}
    out |= set((global_card or {}).get("flags", []))
    return sorted(out)

def pair_outcome(first, second):
    """first: judge on (A=x, B=y); second: judge on (A=y, B=x). -> score for x in {1, 0.5, 0}, consistent flag."""
    if first is None or second is None:
        return 0.5, False
    a = {"A": 1.0, "B": 0.0, "TIE": 0.5}[first["winner"]]
    b = {"A": 0.0, "B": 1.0, "TIE": 0.5}[second["winner"]]     # swapped: x is B in the second call
    if a == b: return a, a != 0.5
    return (a + b) / 2, False                                     # disagreement across orders -> position bias -> split

def bradley_terry(names, results, iters=500, prior=0.5):
    """results: list of (x, y, score_for_x). MM algorithm with a 0.5-win prior against a virtual average player."""
    p = {n: 1.0 for n in names}
    wins = {n: prior for n in names}; games = {}
    for x, y, s in results:
        wins[x] += s; wins[y] += 1 - s
        games[(x, y)] = games.get((x, y), 0) + 1; games[(y, x)] = games.get((y, x), 0) + 1
    for _ in range(iters):
        new = {}
        for i in names:
            den = 2 * prior / (p[i] + 1.0)
            for j in names:
                if j != i and games.get((i, j)): den += games[(i, j)] / (p[i] + p[j])
            new[i] = wins[i] / den if den else p[i]
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new)); p = {k: v / g for k, v in new.items()}
    field = {i: (sum(p[i] / (p[i] + p[j]) for j in names if j != i) / max(1, len(names) - 1)) for i in names}
    return p, field

def composite(abs_score, pair_score, obj_score, flags):
    parts = [(W_ABS, abs_score), (W_PAIR, pair_score), (W_OBJ, obj_score)]
    got = [(w, v) for w, v in parts if v is not None]
    if not got: return None
    return round(sum(w * v for w, v in got) / sum(w for w, _ in got) - FLAG_PEN * min(2, len(flags)), 3)

def rank_rows(rows):
    """rows: dicts with composite/pairwise/abs. Sort: composite desc, pairwise desc, abs desc, name."""
    key = lambda r: (-(r.get("composite") if r.get("composite") is not None else -99), -(r.get("pairwise") or 0), -(r.get("abs") or 0), r["name"])
    out = sorted(rows, key=key)
    for i, r in enumerate(out, 1): r["rank"] = i
    return out

def verdict(parent, child, pair_consistent_child_win, margin=PROMOTE_MARGIN):
    """PROMOTE when the child beats its parent: consistent pairwise win + composite >= parent + margin, or a big composite gain;
    never when the child raises more hard flags than the parent."""
    if child.get("composite") is None or parent.get("composite") is None: return "NO_DATA"
    if len(child.get("flags", [])) > len(parent.get("flags", [])): return "KEEP_PARENT"
    delta = child["composite"] - parent["composite"]
    if pair_consistent_child_win and delta >= margin: return "PROMOTE"
    if delta >= 3 * margin: return "PROMOTE"
    return "KEEP_PARENT"


# ---------------------------------------------------------------- review pipeline
def review(cands, out_prefix, judge_model, use_model, lf, frames_per_window=6, global_frames=12, chat=None, pairs_only=None):
    work = out_prefix + "_work"; os.makedirs(work, exist_ok=True)
    judge = Judge(judge_model, chat=chat, lf=lf) if use_model else None
    labels = {c["name"]: f"V{i + 1}" for i, c in enumerate(cands)}           # blind labels in sheets/files; names never shown to the judge
    rows = {}
    for c in cands:
        lab = labels[c["name"]]; d = os.path.join(work, lab); os.makedirs(d, exist_ok=True)
        texts = [b for s in c["segments"] for b in s["beats"]]
        if not all(guard_ok(t) for t in texts): raise PermissionError(f"adults-only guard hit in beat text of {c['name']}")
        log(f"metrics {c['name']} ({c['video']})", lf)
        spans = [(s["t0"], s["t1"]) for s in c["segments"] if s.get("file")] if c["kind"] == "full" else None
        m = compute_metrics(c["video"], seams=c.get("seams", ()), spans=spans)
        wins = windows_of(c); wsheets = []
        for wi, (si, a, b, beat) in enumerate(wins):
            fr = extract_frames(c["video"], a, b, frames_per_window, d, f"w{wi + 1:02d}")
            wsheets.append(contact_sheet(fr, os.path.join(d, f"w{wi + 1:02d}_sheet.jpg"), cols=3))
        gfr = extract_frames(c["video"], 0.0, probe(c["video"])["dur"], global_frames, d, "g", width=240)
        gsheet = contact_sheet(gfr, os.path.join(d, "global_sheet.jpg"), cols=4)
        ref = ref_image(c.get("image"), work)
        rows[c["name"]] = {"name": c["name"], "label": lab, "video": c["video"], "kind": c["kind"], "metrics": m, "objective": m["objective_score"],
                           "windows": [{"seg": si + 1, "t0": round(a, 2), "t1": round(b, 2), "beat": beat, "sheet": s} for (si, a, b, beat), s in zip(wins, wsheets)],
                           "global_sheet": gsheet, "ref": ref, "abs": None, "pairwise": None, "flags": [], "dims": None}
    if judge:
        for c in cands:
            r = rows[c["name"]]; cards = []
            for w in r["windows"]:
                parts = [T(f"Rubric {RUBRIC_VERSION}. Absolute review of ONE window ({w['t0']:.1f}-{w['t1']:.1f} s) of one video. "
                           f"Intended beat for this window: {w['beat']}\n" + ("Image 1 = reference still (identity anchor). Image 2 = " if r["ref"] else "Image 1 = ") +
                           f"{frames_per_window} frames in time order. Reply JSON: {ABS_SCHEMA_TEXT}")]
                if r["ref"]: parts.append(I(r["ref"]))
                parts.append(I(w["sheet"]))
                card = judge.ask(parts, norm_abs); w["judge"] = card; cards.append(card)
            beats = " | ".join(f"{i + 1}) {w['beat']}" for i, w in enumerate(r["windows"]))
            parts = [T(f"Rubric {RUBRIC_VERSION}. Absolute review of the WHOLE video ({r['metrics']['duration']:.0f} s), {global_frames} frames spread over it. "
                       f"Focus on identity/outfit consistency across cuts and joins, pacing, and drift over time (burn, blur, colour). Beats in order: {beats}\n" +
                       ("Image 1 = reference still. Image 2 = frames." if r["ref"] else "Image 1 = frames.") + f" Reply JSON: {ABS_SCHEMA_TEXT}")]
            if r["ref"]: parts.append(I(r["ref"]))
            parts.append(I(r["global_sheet"]))
            gcard = judge.ask(parts, norm_abs); r["global_judge"] = gcard
            r["dims"], r["abs"], r["weakest_window"] = aggregate_abs(cards, gcard)
            r["flags"] = count_flags(cards, gcard)
            seg_scores = {}
            for w, card in zip(r["windows"], cards):
                if card and weighted(card["scores"]) is not None: seg_scores.setdefault(w["seg"], []).append(weighted(card["scores"]))
            r["segment_scores"] = {k: round(sum(v) / len(v), 3) for k, v in seg_scores.items()}
            r["weakest_segment"] = min(r["segment_scores"], key=r["segment_scores"].get) if r["segment_scores"] else None
        names = [c["name"] for c in cands]
        todo = pairs_only or [(x, y) for i, x in enumerate(names) for y in names[i + 1:]]
        pres = []; pair_log = []
        for x, y in todo:
            rx, ry = rows[x], rows[y]
            beats = " | ".join(f"{i + 1}) {w['beat']}" for i, w in enumerate(rx["windows"]))
            def ask(a, b):
                parts = [T(f"Rubric {RUBRIC_VERSION}. PAIRWISE: two videos made from the same plan; decide which is better overall and per dimension. "
                           f"Beats in order: {beats}\n" + ("Image 1 = reference still. Image 2 = video A frames. Image 3 = video B frames. " if rx["ref"] else
                           "Image 1 = video A frames. Image 2 = video B frames. ") + f"Say tie only if truly equal. Reply JSON: {PAIR_SCHEMA_TEXT}")]
                if rx["ref"]: parts.append(I(rx["ref"]))
                parts += [I(a["global_sheet"]), I(b["global_sheet"])]
                return judge.ask(parts, norm_pair, max_tokens=600)
            first, second = ask(rx, ry), ask(ry, rx)
            s, consistent = pair_outcome(first, second)
            pres.append((x, y, s)); pair_log.append({"x": x, "y": y, "score_x": s, "consistent": consistent, "xy": first, "yx": second})
        strength, field = bradley_terry(names, pres)
        for n in names: rows[n]["pairwise"] = round(10 * field[n], 3); rows[n]["bt_strength"] = round(strength[n], 4)
    else:
        pair_log = []
    for r in rows.values(): r["composite"] = composite(r["abs"], r["pairwise"], r["objective"], r["flags"])
    ranked = rank_rows(list(rows.values()))
    meta = {"rubric": RUBRIC_VERSION, "when": NOW(), "judge": judge_model if judge else None, "model_used": bool(judge),
            "calls": judge.calls if judge else 0, "asks": judge.asks if judge else 0, "judge_failures": judge.failures if judge else 0, "judge_secs": round(judge.secs, 1) if judge else 0,
            "weights": {"abs": W_ABS, "pairwise": W_PAIR, "objective": W_OBJ, "flag_penalty": FLAG_PEN}, "dims": WEIGHTS}
    return ranked, pair_log, meta

def write_report(path_prefix, title, ranked, pair_log, meta, extra=None):
    data = dict(meta, title=title, ranking=ranked, pairs=pair_log, top3=[r["name"] for r in ranked[:3]], **(extra or {}))
    write_text(path_prefix + ".json", json.dumps(data, indent=1))
    L = [f"# {title}", "", f"Generated {meta['when']} by `C:\\AI\\community\\scripts\\p6_review.py` - rubric {meta['rubric']}, judge `{meta['judge']}` "
         f"({meta['calls']} calls, {meta['judge_failures']} failures, {meta['judge_secs']:.0f} s). Local only: ffmpeg + CPU metrics + local VLM via llama-swap.", ""]
    if not meta["model_used"]: L += ["**PREVIEW (--no-model): objective metrics only; no VLM scores, no pairwise. Not a final ranking.**", ""]
    L += ["composite = 0.40 x absolute VLM (weighted dims, 0.7 mean + 0.3 weakest window) + 0.40 x pairwise (Bradley-Terry field win-rate x10, "
          "swapped-order, inconsistent orders = split) + 0.20 x objective (0-10) - 0.75 per hard flag (max 2).", "",
          "| rank | candidate | composite | abs VLM | pairwise | objective | flags | weakest seg |", "|---|---|---|---|---|---|---|---|"]
    f = lambda v: "-" if v is None else f"{v:.2f}"
    for r in ranked:
        L.append(f"| {r['rank']} | `{r['name']}` | {f(r['composite'])} | {f(r['abs'])} | {f(r['pairwise'])} | {f(r['objective'])} | {', '.join(r['flags']) or '-'} | {r.get('weakest_segment') or '-'} |")
    if extra and extra.get("verdicts"):
        L += ["", "## Verdicts (child vs parent)", ""] + [f"- `{v['child']}` vs `{v['parent']}`: **{v['verdict']}** (composite {f(v['child_composite'])} vs {f(v['parent_composite'])}, pairwise consistent child win={v['consistent_child_win']})" for v in extra["verdicts"]]
    L += ["", "## Dimensions (1-10, higher is better)", "", "| candidate | " + " | ".join(DIM_KEYS) + " |", "|---|" + "---|" * len(DIM_KEYS)]
    for r in ranked:
        L.append(f"| `{r['name']}` | " + " | ".join(f((r.get('dims') or {}).get(k)) for k in DIM_KEYS) + " |")
    L += ["", "## Objective metrics (CPU, no model)", "", "| candidate | lum_flicker | tex_flicker | sat_drift_max | clip_late_max | sharp_drift_min | color_drift_max | freeze | seam_ratio | cuts | motion |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in ranked:
        m = r["metrics"]; L.append(f"| `{r['name']}` | {m['lum_flicker']} | {m['tex_flicker']} | {m['sat_drift_max']} | {m['clip_late_max']} | {m['sharp_drift_min']} | {m['color_drift_max']} | {m['freeze_frac']} | {m['seam_ratio']} | {m['cuts_detected']} | {m['motion']} |")
    if meta["model_used"]:
        L += ["", "## Judge reasons (global call)", ""]
        for r in ranked:
            g = r.get("global_judge") or {}
            L.append(f"- `{r['name']}`: " + "; ".join(f"{k}: {v}" for k, v in (g.get("reasons") or {}).items() if v)[:900])
    write_text(path_prefix + ".md", "\n".join(L) + "\n")


# ---------------------------------------------------------------- checkshots (harness pre-render validation of Forge's p7 shot lists)
ALLOWED_KEYS = {"id", "image", "image_note", "beat", "chunks", "chunk_secs", "mode", "arm", "secs", "seed", "w", "h", "steps", "antiburn"}
def check_shots(path, job_id):
    bad = []
    if not re.fullmatch(r"p7_[a-z0-9_]{3,48}", job_id or ""): return [f"bad job id {job_id!r}"]
    if os.path.normcase(os.path.abspath(path)) != os.path.normcase(os.path.join(SHOTS, job_id + ".json")): bad.append("shots file must be C:\\AI\\community\\shots\\<job_id>.json")
    try: shots = json.load(open(path, encoding="utf-8"))
    except Exception as e: return [f"unreadable JSON: {e}"]
    if not isinstance(shots, list) or not 1 <= len(shots) <= 3: return ["shot list must be a JSON array of 1-3 shots"]
    for i, s in enumerate(shots):
        p = f"shot {i + 1}"
        if not isinstance(s, dict): bad.append(f"{p}: not an object"); continue
        extra = set(s) - ALLOWED_KEYS
        if extra: bad.append(f"{p}: keys not allowed {sorted(extra)} (no loras / new fields)")
        if not re.fullmatch(re.escape(job_id) + r"_seg[1-3]", str(s.get("id", ""))): bad.append(f"{p}: id must be {job_id}_seg1..3")
        if s.get("image") not in APPROVED: bad.append(f"{p}: image must be an approved still key {sorted(APPROVED)}")
        if (s.get("w"), s.get("h")) != (768, 1344): bad.append(f"{p}: w/h must be 768x1344 (finals size)")
        if not isinstance(s.get("steps"), int) or not 8 <= s["steps"] <= 12: bad.append(f"{p}: steps must be an int 8-12")
        if not isinstance(s.get("seed"), int) or not 0 < s["seed"] < 2 ** 31: bad.append(f"{p}: seed must be a positive int")
        ab = s.get("antiburn")
        if ab is not None and not (isinstance(ab, (int, float)) and 0 < ab <= 1.0): bad.append(f"{p}: antiburn must be null or 0-1")
        if s.get("mode") != "r2v": bad.append(f"{p}: mode must stay r2v (P6 segments are all r2v)")
        if s.get("arm") not in ("long_r2v", "short"): bad.append(f"{p}: arm must be long_r2v or short")
        if s.get("secs") != 10 or s.get("chunk_secs", 10) != 10: bad.append(f"{p}: secs/chunk_secs must be 10 (238-frame continuation finding)")
        ch = s.get("chunks", [])
        if not isinstance(ch, list) or len(ch) > 1 or not all(isinstance(x, str) for x in ch): bad.append(f"{p}: chunks must be a list of at most 1 string")
        texts = [s.get("beat"), s.get("image_note")] + (ch if isinstance(ch, list) else [])
        if not all(isinstance(t, str) and 0 < len(t) <= 1500 for t in texts[:2]): bad.append(f"{p}: beat and image_note must be non-empty strings <= 1500 chars")
        if not all(guard_ok(t) for t in texts if isinstance(t, str)): bad.append(f"{p}: adults-only guard hit")
    return bad


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="local P6/P7 video review + ranking")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("rank", "compare"):
        s = sub.add_parser(name)
        s.add_argument("--out", default=None); s.add_argument("--judge", default="qwen3vl_judge", choices=["qwen3vl_judge", "vl_judge", "coding_sc117_strata"])
        s.add_argument("--no-model", action="store_true", help="CPU metrics + frames only; no llama-swap call (guard runs with -NoHttp)")
        s.add_argument("--frames", type=int, default=6); s.add_argument("--title", default=None)
        if name == "rank": s.add_argument("--preset", choices=["p6"]); s.add_argument("--cand", action="append", default=[])
        else: s.add_argument("--pair", action="append", default=[], help="PARENT=CHILD")
    c = sub.add_parser("checkshots"); c.add_argument("shots"); c.add_argument("job_id")
    a = ap.parse_args(argv)
    if a.cmd == "checkshots":
        bad = check_shots(a.shots, a.job_id)
        print("OK" if not bad else "BAD: " + " | ".join(bad)); return 0 if not bad else 4
    out = a.out or (os.path.join(RUNS, "P6_RANKING") if a.cmd == "rank" else None)
    if not out: print("--out is required for compare"); return 2
    lf = out + ".log"
    ok, why = run_guard(nohttp=a.no_model)
    log(f"gpu_guard: {why}", lf)
    if not ok and not a.no_model:
        log("REFUSED: GPU busy - nothing reviewed (run again when gpu_guard says IDLE)", lf); return 3
    if not a.no_model:
        try: agent = inside_agent(process_table(), os.getpid())
        except Exception as e: agent = True; log(f"process table unreadable ({e}) - failing closed", lf)
        if agent:
            log("REFUSED: started from inside the pi agent (Forge). Model reviews run only from the Ralph harness between iterations.", lf); return 3
        util, mem = gpu_util(); log(f"gpu util {util:.0f}% mem {mem:.0f} MiB", lf)
        if util > 30:
            log(f"REFUSED: GPU busy with work gpu_guard cannot see (util {util:.0f}%, e.g. a llama-swap bench) - nothing reviewed", lf); return 3
    locked = False
    try:
        if not a.no_model:
            locked, msg = lock("Acquire"); log(f"gpu lock: {msg}", lf)
            if not locked: log("REFUSED: could not take C:\\AI\\locks\\gpu-render.lock", lf); return 3
        if a.cmd == "rank":
            specs = (P6_PRESET if a.preset == "p6" else []) + a.cand
            if len(specs) < 2: print("need --preset p6 or >= 2 --cand"); return 2
            cands = [resolve(s) for s in specs]
            ranked, plog, meta = review(cands, out, a.judge, not a.no_model, lf, frames_per_window=a.frames)
            write_report(out, a.title or "P6 ranking - five one-minute videos", ranked, plog, meta)
        else:
            pairs = [p.split("=", 1) for p in a.pair]
            if not pairs or any(len(p) != 2 for p in pairs): print("need --pair PARENT=CHILD"); return 2
            allr, alll, verdicts, meta = [], [], [], None
            for i, (pa, ch) in enumerate(pairs, 1):
                cands = [resolve(pa), resolve(ch)]
                ranked, plog, meta = review(cands, f"{out}_pair{i}", a.judge, not a.no_model, lf, frames_per_window=a.frames)
                byn = {r["name"]: r for r in ranked}
                cw = any(p["x"] == pa and p["y"] == ch and p["consistent"] and p["score_x"] == 0.0 for p in plog)
                verdicts.append({"parent": pa, "child": ch, "verdict": verdict(byn[pa], byn[ch], cw), "consistent_child_win": cw,
                                 "parent_composite": byn[pa]["composite"], "child_composite": byn[ch]["composite"],
                                 "child_weakest_segment": byn[ch].get("weakest_segment")})
                allr += ranked; alll += plog
            write_report(out, a.title or "P7 comparison", rank_rows(allr), alll, meta, extra={"verdicts": verdicts})
        log(f"DONE -> {out}.md / .json", lf)
        if meta and meta["model_used"] and meta["judge_failures"] > 0.25 * max(1, meta["asks"]):
            log(f"JUDGE FAILURE: {meta['judge_failures']}/{meta['asks']} replies unusable - ranking written but not trustworthy", lf); return 5
        return 0
    except PermissionError as e:
        log(f"REFUSED: {e}", lf); return 3
    except (ValueError, FileNotFoundError) as e:
        log(f"INPUT ERROR: {e}", lf); return 2
    finally:
        if locked:   # only when WE hold the GPU: never unload while someone else's render may be running
            try: urllib.request.urlopen(LS + "/unload", timeout=120).read(); log("llama-swap unload (judge released)", lf)
            except Exception as e: log(f"unload warn {e}", lf)
            log(f"gpu lock: {lock('Release')[1]}", lf)

if __name__ == "__main__":
    sys.exit(main())
