r"""make_render.py - one-command render for Forge (plan 40_projects/max-fix-tests/plans/2026-10-30-fast-one-command-render-pipeline-plan.md).

Usage:
  python make_render.py still|video [<still id>|pick] [count] [--words "short prompt"] [--seconds 5] [--wait] [--dry-run]
Defaults: still count 4, video count 2, video 5 s (frames = seconds*24+4). Each output gets its own seed from
C:\AI\community\render\seed_counter.txt. `pick` = next approved still (approved_characters INDEX.csv order) not in
C:\AI\community\render\used.txt (the pick is appended there). approved_characters is read only.
Still default (Derrick 1:16 AM CT Oct 31, S2): templates\flux_stills_s2_kv.api.json then flux_stills_s2_bfs.api.json
(two batches; see still_s2). Still --words: write them per the FLUX prompt skill
alienpc-stills-pose-edit-prompting (C:\Users\derek\.pi\agent\skills\alienpc-stills-pose-edit-prompting\SKILL.md): change -> keep -> light/style. Old single-pass still template (still used for video candidate stills):
templates\bfs_klein9b.api.json (fields changed: picture1_body.image, picture2_head.image = the
approved still, noise.noise_seed, save.filename_prefix, positive.text only if --words).
Video template: runs\strip_tease_20261030_bedroom01\<tag>\request.api.json via make_b2_request.py (img.image,
noise.noise_seed, save.filename_prefix, c0.length, c0.prompt only if --words).
Video (Derrick 7:22 PM CT): per video, 2 varied-pose stills are rendered first, scored against the approved still
(InsightFace buffalo_l w600k_r50 cosine sim, CPU, ComfyUI venv), the better one is staged 768x1344 for the video.
Submits with run_queue.py --detach under gpu-render.lock; GPU busy (rc 7) = wait and retry every 5 s.
Prints QUEUED <tag>, then (with --wait) DONE <file paths> or FAILED <reason>.
Rollback: delete this file, agent-shared\prompts\render.md and C:\AI\community\render\.
"""
import argparse, copy, csv, glob, json, math, os, re, subprocess, sys, time

ROOT = r"C:\AI\community"
SCRIPTS = os.path.join(ROOT, "scripts")
APPROVED = r"\\NAS4CBE37.local\home\AlienPc-approved\approved_characters"
STATE = os.path.join(ROOT, "render")
COMFY_IN = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input"
STILL_TPL = os.path.join(ROOT, "templates", "flux_stills_s2_bfs.api.json")
VIDEO_DIR = os.path.join(ROOT, "runs", "strip_tease_20261030_bedroom01")
# FLUX stills default = S2 (Derrick 1:16 AM CT Oct 31: "Adopt S2 as the FLUX stills workflow now"): pass 1 Klein 9B-KV fp8
# + FluxKVCache (redo arm A3), pass 2 BFS head LoRA 0.5 on the pass-1 output (redo arm S2). Frozen from
# runs\flux_redo_20261030_A3 / _S2; see templates\flux_stills_s2.README.md. Video candidate stills keep STILL_TPL.
S2_KV_TPL = os.path.join(ROOT, "templates", "flux_stills_s2_kv.api.json")
S2_BFS_TPL = os.path.join(ROOT, "templates", "flux_stills_s2_bfs.api.json")
# Fallback pass-1 prompt when no --words; same order as the FLUX prompt skill alienpc-stills-pose-edit-prompting
# (C:\Users\derek\.pi\agent\skills\alienpc-stills-pose-edit-prompting\SKILL.md): change (pose, angle, scene) -> keep (face, hair) -> light/style.
S2_PROMPT = "Show the woman from image 1 {pose}, full body. Keep the same face, hairstyle and hair color. Natural light, photoreal."
PY = sys.executable
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")
POLL = 3
# Stills without --words: one entry per still, no repeats within a request (rotated by seed). Same wording as the
# bfs_klein9b template prompt; only the pose / camera angle / setting part differs from it.
VARIETY = [
    "sitting on the edge of a bed, front view, in a softly lit bedroom",
    "kneeling on a rug, three-quarter view, in a bright living room",
    "lying on her side on white sheets, high angle view, in a sunlit bedroom",
    "standing with her back turned and looking over her shoulder, side view, on a balcony at sunset",
    "walking toward the camera, front view, in a hotel hallway",
    "standing with one hand on her hip, low angle view, in a white photo studio",
    "sitting on a bathroom counter, three-quarter view, in a marble bathroom",
    "leaning against a window, side view, in a city apartment at night",
    "sitting cross-legged on a sofa, high angle view, in a cozy living room",
    "standing in a doorway, low angle three-quarter view, in a rustic cabin",
    "lying on her back on a lounge chair, side view, beside a pool",
    "kneeling on a bed, front view, in a dim bedroom with warm lamp light",
]
VARIETY_TPL = ("head_swap: start with Picture 1 as the base image for the body, keeping her body, skin tone and outfit, "
               "and show her {pose}. remove the head from Picture 1 completely and replace it with the head from Picture 2, "
               "strictly preserving the hair, eye color, nose structure of Picture 2. copy the direction of the eye, "
               "head rotation, micro expressions from Picture 1, high quality, sharp details, 4k.\n")


def fail(msg):
    print("FAILED %s" % msg, flush=True); sys.exit(1)


def counter(name, n=1, start=1):
    """Atomically reserve n values from STATE\\<name> (lock file via O_EXCL). Returns the first value."""
    os.makedirs(STATE, exist_ok=True)
    path, lock = os.path.join(STATE, name), os.path.join(STATE, name + ".lock")
    t0 = time.time()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); break
        except FileExistsError:
            if time.time() - t0 > 30:  # stale lock from a killed run
                try: os.remove(lock)
                except OSError: pass
            time.sleep(0.1)
    try:
        cur = int(open(path).read().strip()) if os.path.exists(path) else start
        with open(path + ".tmp", "w") as f: f.write(str(cur + n))
        os.replace(path + ".tmp", path)
        return cur
    finally:
        os.close(fd); os.remove(lock)


def approved_stills():
    """[(id, absolute file)] in INDEX.csv order (first image file per row), else file order."""
    idx, out = os.path.join(APPROVED, "INDEX.csv"), []
    if os.path.exists(idx):
        for row in csv.DictReader(open(idx, encoding="utf-8")):
            for f in (row.get("files") or "").split(";"):
                f = f.strip()
                if f.lower().endswith(IMG_EXT) and not f.startswith("("):
                    p = os.path.join(APPROVED, f.replace("/", os.sep))
                    if os.path.isfile(p):
                        out.append((row["id"].strip(), p)); break
    else:
        for p in sorted(glob.glob(os.path.join(APPROVED, "**", "*"), recursive=True)):
            if p.lower().endswith(IMG_EXT):
                out.append((os.path.splitext(os.path.basename(p))[0], p))
    return out


def inside_approved(p):
    a, p = os.path.realpath(APPROVED), os.path.realpath(p)
    return os.path.commonpath([a, p]) == a and os.path.isfile(p)


def resolve_still(name, dry):
    pool = approved_stills()
    if name == "pick":
        used_p = os.path.join(STATE, "used.txt")
        used = set(l.strip() for l in open(used_p, encoding="utf-8")) if os.path.exists(used_p) else set()
        for sid, p in pool:
            if sid not in used:
                if not dry:
                    os.makedirs(STATE, exist_ok=True)
                    with open(used_p, "a", encoding="utf-8") as f: f.write(sid + "\n")
                return sid, p
        fail("no unused approved still left (see %s)" % used_p)
    for sid, p in pool:
        if sid.lower() == name.lower():
            return sid, p
    p = name if os.path.isabs(name) else os.path.join(APPROVED, name)
    if inside_approved(p):
        return re.sub(r"[^A-Za-z0-9]+", "_", os.path.splitext(os.path.basename(p))[0]), os.path.realpath(p)
    fail("still %r does not resolve inside approved_characters" % name)


def stage_image(sid, src, video):
    """Copy (read only source) into ComfyUI input\\community\\render. Video gets a 768x1344 cover crop like B2 runs."""
    from PIL import Image
    d = os.path.join(COMFY_IN, "community", "render"); os.makedirs(d, exist_ok=True)
    if video:
        name = "%s_768x1344.png" % sid
        im = Image.open(src).convert("RGB")
        s = max(768 / im.width, 1344 / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        l, t = (im.width - 768) // 2, (im.height - 1344) // 2
        im.crop((l, t, l + 768, t + 1344)).save(os.path.join(d, name))
        return "community/render/" + name, (768, 1344)
    name = "%s%s" % (sid, os.path.splitext(src)[1].lower())
    with open(src, "rb") as a, open(os.path.join(d, name), "wb") as b: b.write(a.read())
    w, h = Image.open(src).size
    k = math.sqrt(1024 * 1024 / (w * h))  # ResizeImageMaskNode 1 MP, then the Flux2 latent floors to 16
    return "community/render/" + name, (round(w * k) // 16 * 16, round(h * k) // 16 * 16)


def node(g, title):
    return next(k for k, v in g.items() if v.get("_meta", {}).get("title") == title)


def diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in set(a) | set(b):
            out += diff(a.get(k), b.get(k), "%s.%s" % (path, k) if path else k)
        return out
    return [] if a == b else [path]


def video_template():
    reqs = sorted(glob.glob(os.path.join(VIDEO_DIR, "*", "request.api.json")))
    if not reqs: fail("no video template under %s" % VIDEO_DIR)
    return reqs[0]


def build(a, run, run_dir, sid, src, stage_src=None):
    """stage_src = per-video picked still files (video flow); else the approved still for every job."""
    tags, order, checks = [], [], []
    image, size = stage_image(sid, src, a.kind == "video")
    seed0 = counter("seed_counter.txt", a.count, start=70000001)
    frames = a.seconds * 24 + 4
    for i in range(a.count):
        seed = seed0 + i
        tag = "%s_%s_s%d" % ("rs" if a.kind == "still" else "rv", sid, seed)
        d = os.path.join(run_dir, tag); os.makedirs(d, exist_ok=True)
        prefix = "community/%s/%s" % (run, tag)
        if a.kind == "still":
            tpl = json.load(open(STILL_TPL, encoding="utf-8"))
            g = copy.deepcopy(tpl)
            g[node(g, "picture1_body")]["inputs"]["image"] = image
            g[node(g, "picture2_head")]["inputs"]["image"] = image
            g[node(g, "noise")]["inputs"]["noise_seed"] = seed
            g[node(g, "save")]["inputs"]["filename_prefix"] = prefix
            if a.words: g[node(g, "positive")]["inputs"]["text"] = a.words
            else:  # vary pose/angle/setting: consecutive seeds -> distinct entries within a request (count <= 12)
                g[node(g, "positive")]["inputs"]["text"] = VARIETY_TPL.format(pose=VARIETY[seed % len(VARIETY)])
            json.dump(g, open(os.path.join(d, "request.api.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            allowed = {"7.inputs.image", "8.inputs.image", "20.inputs.noise_seed", "24.inputs.filename_prefix", "5.inputs.text"}
            order.append({"pos": i + 1, "tag": tag, "arm": "render", "scene": sid, "seed": seed, "job_type": "still",
                          "size": "%dx%d" % size, "still": sid})
        else:
            if stage_src:
                image, size = stage_image("%s_pick%d_s%d" % (sid, i + 1, seed), stage_src[i], True)
            vt = video_template(); tpl = json.load(open(vt, encoding="utf-8"))
            cmd = [PY, os.path.join(SCRIPTS, "make_b2_request.py"), "--arm-dir", d, "--seed", str(seed), "--image", image,
                   "--prefix", prefix, "--frames", str(frames), "--template", vt, "--force"]
            cmd += ["--prompt", a.words] if a.words else ["--prompt", tpl["c0"]["inputs"]["prompt"]]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode: fail("make_b2_request rc=%d %s" % (r.returncode, (r.stderr or r.stdout).strip()[:200]))
            g = json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))
            allowed = {"img.inputs.image", "noise.inputs.noise_seed", "save.inputs.filename_prefix", "c0.inputs.length", "c0.inputs.prompt"}
            order.append({"pos": i + 1, "tag": tag, "arm": "render", "scene": sid, "seed": seed, "still": sid})
        ch = sorted(diff(tpl, g)); bad = [c for c in ch if c not in allowed]
        if bad: fail("non-whitelisted field(s) changed: %s" % ", ".join(bad))
        checks.append((tag, ch)); tags.append(tag)
    json.dump({"run": run, "kind": a.kind, "still": sid, "source": src, "order": order},
              open(os.path.join(run_dir, "_render_order.json"), "w", encoding="utf-8"), indent=1)
    return tags, checks, frames, size


def s2_build(a, seed0, runs, sid, src, image, size):
    """S2 stills: pass 1 (KV) jobs in runs[0], pass 2 (BFS 0.5) jobs in runs[1] reading the pass-1 PNG.
    runs = [(run, run_dir), (run, run_dir)]. Returns (tags1, tags2, size2, checks)."""
    kv, bfs = json.load(open(S2_KV_TPL, encoding="utf-8")), json.load(open(S2_BFS_TPL, encoding="utf-8"))
    k = math.sqrt(1024 * 1024 / (size[0] * size[1]))
    size2 = (round(size[0] * k) // 16 * 16, round(size[1] * k) // 16 * 16)  # pass 2 resizes the pass-1 output to 1 MP
    tags1, tags2, checks, o1, o2 = [], [], [], [], []
    for i in range(a.count):
        seed = seed0 + i
        t1, t2 = "rs_%s_s%d_kv" % (sid, seed), "rs_%s_s%d" % (sid, seed)
        (r1, d1), (r2, d2) = runs
        g1 = copy.deepcopy(kv)
        g1["7"]["inputs"]["image"] = image
        g1["20"]["inputs"]["noise_seed"] = seed
        g1["24"]["inputs"]["filename_prefix"] = "community/%s/%s" % (r1, t1)
        g1["5"]["inputs"]["text"] = a.words or S2_PROMPT.format(pose=VARIETY[seed % len(VARIETY)])
        g2 = copy.deepcopy(bfs)
        g2["7"]["inputs"]["image"] = "community/%s/%s_00001_.png [output]" % (r1, t1)
        g2["8"]["inputs"]["image"] = image  # head = the approved still (no head crops for the pool)
        g2["20"]["inputs"]["noise_seed"] = seed
        g2["24"]["inputs"]["filename_prefix"] = "community/%s/%s" % (r2, t2)
        for d, t, g, tpl, ok in ((d1, t1, g1, kv, {"7.inputs.image", "20.inputs.noise_seed", "24.inputs.filename_prefix", "5.inputs.text"}),
                                 (d2, t2, g2, bfs, {"7.inputs.image", "8.inputs.image", "20.inputs.noise_seed", "24.inputs.filename_prefix"})):
            os.makedirs(os.path.join(d, t), exist_ok=True)
            json.dump(g, open(os.path.join(d, t, "request.api.json"), "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
            ch = sorted(diff(tpl, g)); bad = [c for c in ch if c not in ok]
            if bad: fail("non-whitelisted field(s) changed: %s" % ", ".join(bad))
            checks.append((t, ch))
        o1.append({"pos": i + 1, "tag": t1, "arm": "s2_kv", "scene": sid, "seed": seed, "job_type": "still", "size": "%dx%d" % size, "still": sid})
        o2.append({"pos": i + 1, "tag": t2, "arm": "s2_bfs", "scene": sid, "seed": seed, "job_type": "still", "size": "%dx%d" % size2, "still": sid})
        tags1.append(t1); tags2.append(t2)
    for (r, d), o in zip(runs, (o1, o2)):
        json.dump({"run": r, "kind": "still_s2", "still": sid, "source": src, "order": o},
                  open(os.path.join(d, "_render_order.json"), "w", encoding="utf-8"), indent=1)
    return tags1, tags2, size2, checks


def still_s2(a, sid, src):
    """FLUX stills default (S2): pass 1 KV batch, wait for it, then pass 2 BFS batch."""
    image, size = stage_image(sid, src, False)
    seed0 = counter("seed_counter.txt", a.count, start=70000001)
    runs = []
    for p in ("kv", "bfs"):
        r = "%s_render_%04d%s" % (time.strftime("%Y-%m-%d"), counter("run_counter.txt"), "_dry" if a.dry_run else "")
        d = os.path.join(ROOT, "runs", r); os.makedirs(d); runs.append((r, d))
    tags1, tags2, size2, checks = s2_build(a, seed0, runs, sid, src, image, size)
    if a.dry_run:
        for tag, ch in checks: print("DRY %s changed: %s" % (tag, ", ".join(ch)))
        rc = 0
        for _, d in runs:
            r = subprocess.run([PY, os.path.join(SCRIPTS, "run_queue.py"), "--run-dir", d, "--dry-run"], capture_output=True, text=True, cwd=ROOT)
            print(r.stdout.strip()); rc = rc or r.returncode
        return rc
    print("QUEUED %s (S2 pass 1 KV: %s, still %s)" % (runs[0][0], ", ".join(tags1), sid), flush=True)
    off = submit(runs[0][1], 124, size)
    m = None
    while not m:
        m = re.search(r"BATCH closed rc=(\d+)", log_text(runs[0][1])[off:]); time.sleep(POLL) if not m else None
    if m.group(1) != "0": fail("S2 pass 1 rc=%s (see %s)" % (m.group(1), runs[0][1]))
    print("QUEUED %s (S2 pass 2 BFS 0.5: %s)" % (runs[1][0], ", ".join(tags2)), flush=True)
    off = submit(runs[1][1], 124, size2)
    return wait_done(runs[1][1], tags2, off) if a.wait else 0


def log_text(run_dir):
    p = os.path.join(run_dir, "_render_queue.log")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def submit(run_dir, frames, size):
    """Launch run_queue --detach; on rc 7 (GPU busy) wait 5 s and launch again. Returns once the batch is open
    or closed (log offset of that launch)."""
    while True:
        off = len(log_text(run_dir))
        r = subprocess.run([PY, os.path.join(SCRIPTS, "run_queue.py"), "--run-dir", run_dir, "--frames", str(frames),
                            "--size", "%dx%d" % size, "--detach"], capture_output=True, text=True, cwd=ROOT)
        if r.returncode: fail("run_queue --detach rc=%d %s" % (r.returncode, (r.stdout + r.stderr).strip()[:200]))
        while True:
            time.sleep(POLL)
            t = log_text(run_dir)[off:]
            if "BATCH closed rc=7" in t:
                time.sleep(5); break  # GPU busy: line up and retry
            if "BATCH open" in t or "BATCH closed" in t:
                return off


RUNS = os.path.join(ROOT, "runs")


def to_jpg(png):
    """Metadata-free JPG copy next to a PNG (the phone hub blocks PNGs: they embed prompt/workflow)."""
    from PIL import Image
    j = os.path.splitext(png)[0] + ".jpg"
    Image.open(png).convert("RGB").save(j, "JPEG", quality=92)  # no exif/info passed = none written
    return j


def media(path):
    """/media/<path under runs, forward slashes> for the 7878 phone hub (.jpg/.mp4 only)."""
    if path.lower().endswith(".png"): path = to_jpg(path)
    return "/media/" + os.path.relpath(path, RUNS).replace(os.sep, "/") + "  " + path


def wait_done(run_dir, tags, off, suffix=""):
    while True:
        t = log_text(run_dir)[off:]
        m = re.search(r"BATCH closed rc=(\d+) reason=(.*)", t)
        if m:
            files = []
            for tag in tags:
                files += [f for f in glob.glob(os.path.join(run_dir, tag, tag + "*"))
                          if f.lower().endswith((".png", ".mp4")) and "contact" not in f.lower()]
            if m.group(1) == "0":
                print("DONE" + suffix + "\n" + "\n".join(media(f) for f in sorted(files)), flush=True); return 0
            print("FAILED rc=%s %s%s" % (m.group(1), m.group(2).strip(), (" (landed: %s)" % " ".join(sorted(files))) if files else ""), flush=True)
            return 1
        time.sleep(POLL)


FACE_PY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\.venv\Scripts\python.exe"  # has insightface + onnxruntime
FACE_CODE = r"""
import sys, json, cv2, numpy as np
from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))
def emb(p):
    f = app.get(cv2.imread(p))
    if not f: return None
    f = max(f, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    return f.normed_embedding
ref = emb(sys.argv[1]); out = {}
for p in sys.argv[2:]:
    e = emb(p); out[p] = None if (e is None or ref is None) else float(np.dot(ref, e))
print(json.dumps(out))
"""


def face_scores(ref, cands):
    """InsightFace buffalo_l (w600k_r50 ArcFace) cosine sim of the largest face vs the approved still; CPU only.
    None = no face found (in the candidate or the reference)."""
    import tempfile
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="mr_face_")
    def png(p):  # cv2 cannot read some jpg/webp variants; normalise to png
        q = os.path.join(tmp, os.path.basename(p) + ".png"); Image.open(p).convert("RGB").save(q); return q
    m = {png(c): c for c in cands}
    r = subprocess.run([FACE_PY, "-c", FACE_CODE, png(ref), *m], capture_output=True, text=True)
    try:
        raw = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        print("NOTE face scoring failed: %s" % (r.stderr or r.stdout).strip()[-200:], flush=True); return {c: None for c in cands}
    return {m[k]: v for k, v in raw.items()}


def video_flow(a, sid, src):
    """Per video: 2 varied-pose stills, keep the better face match to the approved still, then the video from it."""
    sa = argparse.Namespace(kind="still", count=2 * a.count, words=a.words, seconds=a.seconds)
    run = "%s_render_%04d" % (time.strftime("%Y-%m-%d"), counter("run_counter.txt"))
    run_dir = os.path.join(ROOT, "runs", run); os.makedirs(run_dir)
    tags, _, frames, size = build(sa, run, run_dir, sid, src)
    print("QUEUED %s (%d candidate stills for %d video(s), still %s)" % (run, len(tags), a.count, sid), flush=True)
    off = submit(run_dir, frames, size)
    while not re.search(r"BATCH closed rc=\d+", log_text(run_dir)[off:]): time.sleep(POLL)
    files = [next(iter(glob.glob(os.path.join(run_dir, t, t + "*.png"))), None) for t in tags]
    scores = face_scores(src, [f for f in files if f])
    picks, notes = [], []
    for i in range(a.count):
        pair = [f for f in files[2 * i:2 * i + 2] if f]
        scored = [f for f in pair if scores.get(f) is not None]
        if scored:
            best = max(scored, key=lambda f: scores[f]); picks.append(best)
            notes.append("video %d picked %s face_sim=%.3f (others: %s)" % (i + 1, best, scores[best],
                         ", ".join("%s=%s" % (os.path.basename(f), "%.3f" % scores[f] if scores.get(f) is not None else "no face") for f in pair if f != best)))
        else:
            picks.append(src); notes.append("video %d: no face found in candidates (%s), fell back to the approved still %s" % (
                i + 1, ", ".join(os.path.basename(f) for f in pair) or "none rendered", src))
    for n in notes: print("PICK " + n, flush=True)
    for f in files:
        if f: print("CANDIDATE " + media(f), flush=True)
    run2 = "%s_render_%04d" % (time.strftime("%Y-%m-%d"), counter("run_counter.txt"))
    run_dir2 = os.path.join(ROOT, "runs", run2); os.makedirs(run_dir2)
    vtags, _, frames, size = build(a, run2, run_dir2, sid, src, stage_src=picks)
    print("QUEUED %s (%s, %d x video, still %s)" % (run2, ", ".join(vtags), len(vtags), sid), flush=True)
    off = submit(run_dir2, frames, size)
    if not a.wait: return 0
    rc = wait_done(run_dir2, vtags, off, suffix=" (" + "; ".join(notes) + ")")
    return rc


def main():
    ap = argparse.ArgumentParser(description="one-command still/video render")
    ap.add_argument("kind", choices=["still", "video"])
    ap.add_argument("still", nargs="?", default="pick")
    ap.add_argument("count", nargs="?", type=int)
    ap.add_argument("--words", help="still: pass-1 prompt written per the alienpc-stills-pose-edit-prompting skill (change -> keep -> light/style)")
    ap.add_argument("--seconds", type=int, default=5)
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.count is None: a.count = 4 if a.kind == "still" else 2
    if a.count < 1 or a.seconds < 1: fail("count and seconds must be positive")
    if a.count > (4 if a.kind == "still" else 2): fail("needs Derrick's GO")
    sid, src = resolve_still(a.still, a.dry_run)
    if a.kind == "video" and not a.dry_run:
        return video_flow(a, sid, src)
    if a.kind == "still":
        return still_s2(a, sid, src)
    run = "%s_render_%04d" % (time.strftime("%Y-%m-%d"), counter("run_counter.txt"))
    if a.dry_run: run += "_dry"
    run_dir = os.path.join(ROOT, "runs", run); os.makedirs(run_dir)
    tags, checks, frames, size = build(a, run, run_dir, sid, src)
    if a.dry_run:
        for tag, ch in checks: print("DRY %s changed: %s" % (tag, ", ".join(ch)))
        r = subprocess.run([PY, os.path.join(SCRIPTS, "run_queue.py"), "--run-dir", run_dir, "--dry-run"], capture_output=True, text=True, cwd=ROOT)
        print(r.stdout.strip()); return r.returncode
    print("QUEUED %s (%s, %d x %s, still %s)" % (run, ", ".join(tags), len(tags), a.kind, sid), flush=True)
    off = submit(run_dir, frames, size)
    return wait_done(run_dir, tags, off) if a.wait else 0


if __name__ == "__main__":
    sys.exit(main())
