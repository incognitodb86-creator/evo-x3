r"""run_queue.py - THE reusable render-queue template (simplify plan S4 + S8, 2026-10-30).

Renders every clip in a run's order file back to back in ONE GPU window:
  once per batch : pytest gate, take gpu-render.lock (held = rc 7 GPU_BUSY), unload the LLM, wake comfyui_auto
  post-pass      : RTX 2x of every finished clip by default (--no-upscale to skip); a failed post-pass is
                   rc 9 with the count in the reason and the raw clip kept (the 2x is the deliverable)
  submit (one at a time) : at most MAX_IN_FLIGHT = 1 clip in ComfyUI at a time (FIX 3, 2026-11-03: was submit all
                   up front; up-front submit risked losing queued jobs when llama-swap swapped/killed ComfyUI).
                   Submits the next clip right after the current one settles (minimal gap between jobs).
                   Guards every prompt string, keep-alive touch, static check, then POST /prompt (comm.submit).
                   ComfyUI renders at most one prompt at a time, protecting the queue if swapped out.
  collect        : every QPOLL_SEC (3 s) one GET /comfyui/queue; a prompt that left the queue is read from /history
                   (comm.fetch) and gets its OBJECTIVE check as it finishes (ffprobe size/frames/audio, black/freeze;
                   PNG + size for stills). The per-job timeout (JOB_TIMEOUT) counts from when ComfyUI starts the job,
                   not from submit. A prompt gone from both queue and history (comfyui_auto restarted) is "evicted"
                   and, like a stall, is looked for on disk first (never re-rendered if its output landed)
  retry          : clips that failed or stalled get exactly one unchanged retry, submitted together as a second
                   wave after the first, then are logged FAIL and skipped (phase 2 S8, 2026-10-30)
  at the end     : free ComfyUI's models (POST /free) and, unless --keep-comfy-process is set, unload
                   comfyui_auto; then release the lock in `finally` (also on error and Ctrl-C), and log
                   "BATCH closed rc=<n> reason=<why> done=<ok>/<queued>: <comfyui_auto unloaded | comfyui_auto kept loaded>"
                   (phase 2 S13)
  --keep-comfy-process (chain mode, keep-comfy-part1, 2026-11-15): the end-of-batch llama-swap unload of
                   comfyui_auto is what forces a ~40 s process wake before the next one-clip batch, and a chained
                   run pays that per clip. With this flag the finally block still calls comm.free_comfy
                   (POST /free unload_models+free_memory, so the VRAM is handed back) and skips ONLY the
                   POST /api/models/unload/comfyui_auto, i.e. llama-swap keeps the process alive. Default OFF:
                   normal runs are unchanged. The caller must keep comfyui_auto's ttl (300 s idle in
                   llama-swap.yaml) from expiring between batches; scripts/queue/chain_queue.py pings it during
                   the still_read/writer gap.
  post-pass      : (card t286s1226, Derrick 2026-11-06) every video clip with a DONE ok line is upscaled 2x by RTX
                   VideoSuperRes ULTRA at its native fps (no RIFE), AFTER its OBJECTIVE check passed on the raw render
                   and AFTER comfyui_auto is unloaded, still inside the same gpu-render.lock window (~1.4 GB VRAM).
                   <tag>/<tag>.mp4 becomes the 2x clip (audio stream copied bit-identically); the raw render is kept as
                   <tag>/<tag>_raw.mp4; render_ok.json gains an "upscale" block. Logged "UPSCALE ok ..." / "UPSCALE FAIL
                   ..." (a failure keeps the raw clip and does not change rc). Stills and 1-frame outputs are skipped.
                   --no-upscale turns the post-pass off.
A file named STOP in the run dir halts the batch: no more submits or collecting, ComfyUI's pending queue is cleared
(POST /queue {"clear": true}) and the running prompt interrupted (POST /interrupt). Results append to <run>/_render_queue.log
in the same START/DONE format as the per-test queue scripts, so runs stay comparable.
It reuses comm.py (submit/fetch/run) and run_graph_job.py helpers.
job_type "still" (flux Phase 1, Derrick 2026-10-30 2:52 PM CT): an order entry with "job_type": "still" (and its
expected "size": "WxH") is an image job: the same guard, lock, STOP, retry and log lines, but its check is PNG output
+ size only (no frames/audio/black-freeze/contact sheet) and its prompt is read from the Klein edit text node
(CLIPTextEncode titled "positive"). Entries without job_type are H3 video clips, unchanged.

Usage:
  python scripts\run_queue.py --run-dir <run dir> [--queue <run dir>\_render_order.json] [--resume] [--dry-run]
        [--frames 124] [--size 768x1344] [--detach] [--no-upscale] [--keep-comfy-process]
--resume skips tags with a "DONE ... ok" line in _render_queue.log. --dry-run lists what would render and makes no
lock, GPU or HTTP call.
--frames/--size (item 10, 2026-11-04): the clip objective check compares the probe against the frames and canvas the
submitted graph states (the MiniMaxH3ReferenceToVideo node's length/width/height), because the graph is what was
submitted. A flag that differs from the graph logs one "NOTE pos=.. tag=.. cli frames=.. size=.. vs graph .." line and
is then ignored; the flag is used only where the graph states no literal value. Stills jobs keep their own size check.
--detach (phase 2 S11): relaunch this same command through WMI (Win32_Process.Create), so the batch runs outside the
caller's process tree and job object and survives the pi/herdr pane closing; prints the batch PID and returns at once.
Output goes to <run dir>\_run_queue.out.log. Forge launch line (then end the turn; no waits or checks):
  /home/derekboone/AI/director/.venv/Scripts/python.exe /home/derekboone/AI/community/scripts/run_queue.py --run-dir <run dir> [--resume] --detach
Exit (also logged as BATCH closed rc=<n> reason=<why>): 0 every queued clip has a DONE ok line, 1 STOP file,
2 pytest gate failed, 4 ComfyUI down, 5 a clip failed twice (others still rendered), 6 batch ended with clips
missing a DONE ok line, 7 GPU busy (lock held), 8 uncaught error (reason names it), 9 a previous batch opened and
never closed (killed/unknown; reported at the next start), 130 Ctrl-C. A kill cannot log itself: the next start
reports it.
"""
import argparse, copy, datetime, hashlib, json, os, re, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comm
import run_graph_job as rgj

# B2-10 (2026-11-06): a 3-clip long-form run is a set of clip cells, and the plan fixes the
# cell dir name form: c<2 digits>_s<seed>. The queue is the tool that reads a run's
# _render_order.json, so the tag is checked there. A run turns the rule on by declaring
# "cell_contract": true in its order file (the long-clip runs do); in such a run a tag outside
# the form is a FAIL line and the clip is not submitted. Runs that do not declare it are unchanged.
CELL_RE = re.compile(r"^c\d{2}_s\d{6,}$")
_CELL_CONTRACT = False  # set by main() from the order file; prepare() enforces the tag form

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
PYTEST_FILES = [os.path.join("scripts", "tests", "test_p6_review.py"), os.path.join("scripts", "tests", "test_guard_scope.py")]
ACTIONS = os.path.join(ROOT, "notes", "actions.log")
OUT_ROOT = os.path.join(comm.C, "output", "community")
QPOLL_SEC = 3        # collect poll inside a batch (lock held, comfyui_auto kept loaded, so a poll is no extra wake)
JOB_TIMEOUT = 3600   # per job, counted from when ComfyUI starts it (was from submit with one job at a time)
EVICT_MISSES = 10    # polls a prompt may be in neither /queue nor /history before it counts as evicted (~30 s)
MAX_IN_FLIGHT = 1    # at most ONE prompt of this batch in ComfyUI at a time (FIX 3a, 2026-11-03)
QUEUE_TIMEOUT_STOPPING = 10  # short /queue timeout (s) after repeated timeouts indicate ComfyUI stopping (FIX 3b)

# RTX 2x ULTRA post-pass (card t286s1226, Derrick 2026-11-06). nvvfx/torch live in ComfyUI's venv, not in the
# venv that runs this queue, so the frame loop runs there as a child process (frame by frame, never the whole clip in RAM).
UPSCALE_PY = os.environ.get("RQ_UPSCALE_PY", os.path.join(os.path.dirname(ROOT), "comfy-alienpc", ".venv", "Scripts", "python.exe"))
UPSCALE_TIMEOUT = 1800
# t2571u (Derrick 2026-11-19): X3 renders keep only the upscaled video. remote_upscale.enable sets this, so after a
# verified UPSCALE ok the raw clip is deleted (a failed post-pass still keeps it). AlienPc's local runs are unchanged.
DELETE_RAW_AFTER_UPSCALE = False
_UPSCALE_SRC = r"""
import json, subprocess, sys, time
import torch, nvvfx
src, dst = sys.argv[1], sys.argv[2]
t0 = time.time()
o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                               "stream=codec_type,width,height,r_frame_rate,color_range,color_space,"
                               "color_transfer,color_primaries",
                               "-of", "json", src], capture_output=True, text=True, check=True).stdout)
v = [x for x in o["streams"] if x.get("codec_type") == "video"][0]
has_audio = any(x.get("codec_type") == "audio" for x in o["streams"])
W, H, fps = int(v["width"]), int(v["height"]), v["r_frame_rate"]
# F5 (2026-11-08): keep the source's own colour labels through the post-pass. The frame loop decodes to rgb24
# (the format nvvfx wants) and re-encodes yuv420p, and libx264 writes no colour tags of its own, so the 2x
# file used to arrive with every label unknown (measured 2026-11-08 on a real run: raw tv/bt709/iec61966-2-1/
# bt709 -> clip.mp4 all unknown; reproduced in that same rgb24 shape with CPU ffmpeg in
# runs/skills-forge-repair-2026-11-08-181650/probe_f5_labels.sh). The source's tags are stated three times,
# which is what ffmpeg's measured behaviour needs: on the source decoder (that is how its pixels are labelled,
# and so how they convert into RGB), on the RGB input of the encoder process (the labels the decoded frames
# carry, so RGB->YUV converts back the same way), and on the encoder output (the tags in the file it writes).
# Measured: all four labels in the 2x file match the source; a source with no labels stays unlabelled, because
# no flag is built from an unknown value. Only ffmpeg's existing colour options are used.
_color = [x for field, flag in (("color_range", "-color_range"), ("color_space", "-colorspace"),
                                ("color_transfer", "-color_trc"), ("color_primaries", "-color_primaries"))
          for x in (lambda s: [flag, s] if s and s.lower() not in
                    ("", "unknown", "unspecified", "unrecognized", "unregistered", "none", "n/a") else [])
          (str(v.get(field) or "").strip())]
OW, OH = 2 * W, 2 * H
dec = subprocess.Popen(["ffmpeg", "-v", "error", *_color, "-i", src, "-map", "0:v:0", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
cmd = ["ffmpeg", "-y", "-v", "error", *_color, "-f", "rawvideo", "-pix_fmt", "rgb24",
       "-s", "%dx%d" % (OW, OH), "-r", fps, "-i", "-"]
cmd += (["-i", src, "-map", "0:v:0", "-map", "1:a:0", "-c:a", "copy"] if has_audio else ["-map", "0:v:0"])
cmd += ["-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p"]
cmd += _color + ["-movflags", "+faststart", dst]
enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n, fb = 0, W * H * 3
with nvvfx.VideoSuperRes(nvvfx.effects.QualityLevel.ULTRA) as sr:
    sr.output_width, sr.output_height = OW, OH
    sr.load()
    while True:
        buf = dec.stdout.read(fb)
        if len(buf) < fb:
            break
        x = torch.frombuffer(bytearray(buf), dtype=torch.uint8).view(H, W, 3).cuda().permute(2, 0, 1).float().div_(255.0).contiguous()
        y = torch.from_dlpack(sr.run(x).image)
        enc.stdin.write(y.clamp(0, 1).mul(255.0).round().to(torch.uint8).permute(1, 2, 0).contiguous().cpu().numpy().tobytes())
        n += 1
enc.stdin.close()
rce, rcd = enc.wait(), dec.wait()
if rce or rcd or n == 0:
    sys.exit("upscale ffmpeg rc enc=%s dec=%s frames=%d" % (rce, rcd, n))
print(json.dumps({"frames": n, "in": "%dx%d" % (W, H), "out": "%dx%d" % (OW, OH), "fps": fps, "audio": has_audio,
                  "color_labels": " ".join(_color),
                  "peak_torch_mib": round(torch.cuda.max_memory_allocated() / 2 ** 20), "secs": round(time.time() - t0, 2)}))
"""


def upscale_clip(src, dst, timeout=UPSCALE_TIMEOUT):
    """RTX VideoSuperRes 2x ULTRA of one mp4 at its own fps into dst (audio copied as-is). Returns the child's JSON."""
    r = subprocess.run([UPSCALE_PY, "-c", _UPSCALE_SRC, src, dst], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("upscale rc=%d %s" % (r.returncode, (r.stderr or r.stdout).strip()[-300:].replace("\n", " ")))
    lines = [x for x in (r.stdout or "").splitlines() if x.startswith("{")]
    return json.loads(lines[-1]) if lines else {}


def upscale_done(run_dir, jobs, slog):
    """Post-pass: every video job with a DONE ok line and a render_ok.json without an "upscale" block (so a --resume
    never upscales twice). The raw clip already passed OBJECTIVE; the 2x file is checked against it (exactly 2x size,
    same frames, fps and audio presence) before <tag>.mp4 is swapped. Returns (ok, failed) counts."""
    done, n_ok, n_fail = done_tags(run_dir), 0, 0
    for j in jobs:
        tag = j["tag"]
        if j.get("job_type") == "still" or tag not in done:
            continue
        okp = os.path.join(run_dir, tag, "render_ok.json")
        if not os.path.exists(okp):
            continue
        meta_ok = json.load(open(okp, encoding="utf-8"))
        if meta_ok.get("upscale") or meta_ok.get("job_type") == "still":
            continue
        clip = os.path.join(run_dir, meta_ok.get("clip") or os.path.join(tag, tag + ".mp4"))
        if not clip.lower().endswith(".mp4") or not os.path.exists(clip):
            continue
        p0 = rgj.probe(clip)
        if p0["frames"] <= 1:
            qlog(run_dir, "UPSCALE skip pos=%d tag=%s single frame" % (j["pos"], tag)); continue
        tmp, raw = clip[:-4] + ".rtx.tmp.mp4", clip[:-4] + "_raw.mp4"
        t = time.time()
        try:
            info = upscale_clip(clip, tmp)
            p1 = rgj.probe(tmp)
            why = [] if p1["bytes"] > 0 else ["0-byte file"]
            if (p1["w"], p1["h"]) != (2 * p0["w"], 2 * p0["h"]): why.append("size %sx%s" % (p1["w"], p1["h"]))
            if p1["frames"] != p0["frames"]: why.append("frames %d != %d" % (p1["frames"], p0["frames"]))
            if p1["fps"] != p0["fps"]: why.append("fps %s != %s" % (p1["fps"], p0["fps"]))
            if p1["audio"] != p0["audio"]: why.append("audio %s != %s" % (p1["audio"], p0["audio"]))
            if why:
                raise RuntimeError("check " + "; ".join(why))
        except Exception as e:
            if os.path.exists(tmp): os.remove(tmp)
            n_fail += 1
            qlog(run_dir, "UPSCALE FAIL pos=%d tag=%s %s (raw clip kept)" % (j["pos"], tag, str(e)[:200].replace("\n", " ")))
            continue
        if os.path.exists(raw): os.remove(raw)
        os.replace(clip, raw)   # comm.fetch hard-links <tag>.mp4 to ComfyUI's output: the raw name keeps that link
        os.replace(tmp, clip)   # the 2x clip is a new file; ComfyUI's output is never rewritten
        el = time.time() - t
        meta_ok["upscale"] = {"method": "RTX VideoSuperRes 2x ULTRA (nvvfx), native fps, no RIFE", "card": "t286s1226",
                              "raw_clip": os.path.relpath(raw, run_dir), "raw_sha256": meta_ok.get("clip_sha256"),
                              "raw_w": p0["w"], "raw_h": p0["h"], "raw_bytes": p0["bytes"], "fps": p1["fps"],
                              "frames": p1["frames"], "elapsed_s": round(el, 1), "child": info}
        meta_ok.update({"clip_sha256": hashlib.sha256(open(clip, "rb").read()).hexdigest(), "w": p1["w"], "h": p1["h"],
                        "bytes": p1["bytes"]})
        if DELETE_RAW_AFTER_UPSCALE:   # t2571u: the 2x passed every check above, so the raw clip goes
            os.remove(raw)
            meta_ok["upscale"]["raw_clip"] = None
            meta_ok["upscale"]["raw_deleted"] = "t2571u: only the upscaled clip is kept"
        json.dump(meta_ok, open(okp, "w", encoding="utf-8"), indent=1)
        n_ok += 1
        copy_to_pi_drop(run_dir, tag, clip, slog)   # t2554: only the 2x clip goes to pi-drop
        qlog(run_dir, "UPSCALE ok pos=%d tag=%s %dx%d->%dx%d fps=%s frames=%d audio=%s bytes=%d elapsed=%.1fs raw=%s" % (
            j["pos"], tag, p0["w"], p0["h"], p1["w"], p1["h"], p1["fps"], p1["frames"], "yes" if p1["audio"] else "no",
            p1["bytes"], el, "deleted" if DELETE_RAW_AFTER_UPSCALE else os.path.basename(raw)))
    return n_ok, n_fail


def upscale_only(run_dir, jobs):
    """--upscale-only (t2565u): the 2x post-pass alone on a finished run, with no render, under the same GPU lock."""
    slog = lambda m: comm.log(m, os.path.join(run_dir, "status.log"))
    lrc, lout = rgj.ps_run(rgj.GPU_LOCK_PS, "-Acquire", "-Owner", str(os.getpid()), "-Note", "upscale-only " + os.path.basename(run_dir))
    slog("gpu_lock acquire rc=%d %s" % (lrc, lout[:140]))
    if lrc != 0:
        qlog(run_dir, "UPSCALE-ONLY not started: GPU lock rc=%d %s" % (lrc, lout[:140]))
        return 7 if lrc == 1 else 8
    n_ok = n_fail = 0
    try:
        if not rgj.wake(slog):
            qlog(run_dir, "UPSCALE-ONLY FAIL ComfyUI down"); return 4
        n_ok, n_fail = upscale_done(run_dir, jobs, slog)
    finally:
        rgj.gpu_unlock(slog)
        qlog(run_dir, "UPSCALE-ONLY closed ok=%d fail=%d, lock released" % (n_ok, n_fail))
    return 9 if n_fail else 0


def qlog(run_dir, line):
    """One log line: ISO-8601 local wall-clock with the real UTC offset (F12 2026-11-08), then the text.

    The offset comes from the machine clock (this box runs America/Chicago: -06:00 standard, -05:00 daylight),
    not a written '-05', so a line states the time it was written at. Line format, files and targets unchanged.
    """
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    print(ts, line, flush=True)
    with open(os.path.join(run_dir, "_render_queue.log"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (ts, line))
    with open(ACTIONS, "a", encoding="utf-8") as f:
        f.write("%s run_queue %s: %s\n" % (ts, os.path.basename(run_dir), line))


def done_tags(run_dir):
    p = os.path.join(run_dir, "_render_queue.log")
    if not os.path.exists(p):
        return set()
    return set(re.findall(r" DONE pos=\d+ tag=(\S+) ok ", open(p, encoding="utf-8").read()))


def ok_count(run_dir, jobs):
    d = done_tags(run_dir)
    return sum(1 for j in jobs if j["tag"] in d)


def unclosed_batch(run_dir):
    """S13: the last 'BATCH open' line with no 'BATCH closed' after it = a batch that was killed (a kill can't log)."""
    p = os.path.join(run_dir, "_render_queue.log")
    if not os.path.exists(p):
        return None
    last_open = None
    for line in open(p, encoding="utf-8"):
        if " BATCH open" in line:
            last_open = line.split(" ", 1)[0]
        elif " BATCH closed" in line:
            last_open = None
    return last_open


def detach(argv, run_dir):
    """S11: start this command again via WMI so its parent is WmiPrvSE, not the caller (pane) process tree."""
    args = [a for a in argv if a != "--detach"]
    out = os.path.join(run_dir, "_run_queue.out.log")
    cmd = 'cmd.exe /c ""%s" "%s" %s > "%s" 2>&1"' % (PY, os.path.abspath(__file__), " ".join('"%s"' % a for a in args), out)
    ps = ("$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine=$env:RQ_CMD; "
          "CurrentDirectory='%s'}; \"$($r.ReturnValue) $($r.ProcessId)\"" % ROOT)
    r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True,
                       env=dict(os.environ, RQ_CMD=cmd), timeout=120)
    parts = (r.stdout or "").split()
    if r.returncode or len(parts) < 2 or parts[0] != "0":
        print("detach FAILED rc=%s %s %s" % (r.returncode, r.stdout.strip(), r.stderr.strip()[:300])); return 8
    print("detached batch: cmd.exe PID %s (outside this process tree); output %s; log %s" % (
        parts[1], out, os.path.join(run_dir, "_render_queue.log")))
    return 0


def guard_graph(g, require_adult=True):  # Derek 2026-11-03 6:15 AM CT: require_adult is the default
    """Adults-only gate. Every prompt string must pass comm.guard_ok; with require_adult, at least one must state an adult.
    A malformed graph fails (fail closed). Thin bool wrapper over comm.guard_reason - the reason is what to log."""
    return comm.guard_reason(g, require_adult)[0]


def still_prompt(g):
    """job_type still: the Klein edit prompt = CLIPTextEncode titled 'positive' (else the first CLIPTextEncode)."""
    enc = [n for n in g.values() if n.get("class_type") == "CLIPTextEncode"]
    pos = [n for n in enc if n.get("_meta", {}).get("title") == "positive"] or enc
    return pos[0]["inputs"].get("text", "") if pos else ""


def prompt_behind(g, value):
    """The prompt STRING behind a node input: plain text, or the text of the node a link points to.
    A writer-routed graph wires c0.prompt as ["pw", 0] (measured 2026-11-04, runs/pw_strip_20261104c:
    hashing that value crashed the journal step with "'list' object has no attribute 'encode'", which
    marked a clip that had rendered well as failed). Returns (text, note); text is "" when it cannot be
    resolved - never an exception, the caller logs the note."""
    if isinstance(value, str):
        return value, ("empty prompt string" if not value else "")
    if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
        n = g.get(value[0]) if isinstance(g, dict) else None
        if not isinstance(n, dict):
            return "", "link to node %s which is not in the graph" % value[0]
        for _k, s in comm.prompt_items(n.get("inputs") or {}):
            return s, ""
        return "", "link to node %s (%s) which carries no prompt-bearing key" % (value[0], n.get("class_type"))
    return "", "prompt input is neither text nor a node link (%s)" % type(value).__name__


def prompt_sha(g, value):
    """(sha256 of the prompt text behind an input, ""); ("unresolved", why) when it cannot be read.
    The sha a journal needs is of the TEXT, so it matches the sha the builder tool reports."""
    t, note = prompt_behind(g, value)
    if not t:
        return "unresolved", (note or "no prompt text")
    return hashlib.sha256(t.encode("utf-8")).hexdigest(), ""


def still_done(run_dir, job, tag, f, g0, size, t0, retry, slog):
    """job_type still: PNG output + size check only, then the same render_ok.json and DONE line shape as a clip."""
    if job.get("size"):
        size = tuple(int(x) for x in str(job["size"]).lower().split("x"))
    p = rgj.probe(f)
    why = [] if p["bytes"] > 0 else ["0-byte file"]
    if not f.lower().endswith(".png"): why.append("not a png (%s)" % os.path.basename(f))
    if (p["w"], p["h"]) != size: why.append("size %sx%s != %dx%d" % (p["w"], p["h"], size[0], size[1]))
    if why:
        qlog(run_dir, "FAIL pos=%d tag=%s objective %s" % (job["pos"], tag, "; ".join(why))); return False
    slog("OBJECTIVE ok %s still png size=%sx%s bytes=%d" % (tag, p["w"], p["h"], p["bytes"]))
    outs = [os.path.join(OUT_ROOT, tag, x) for x in os.listdir(os.path.join(OUT_ROOT, tag))] if os.path.isdir(os.path.join(OUT_ROOT, tag)) else []
    wall = (max(map(os.path.getmtime, outs)) - t0) if outs else None
    psha, pnote = prompt_sha(g0, still_prompt(g0))
    if pnote:
        qlog(run_dir, "NOTE pos=%d tag=%s prompt_sha256 unresolved: %s" % (job["pos"], tag, pnote))
    json.dump({"tag": tag, "pos": job["pos"], "arm": job.get("arm"), "scene": job.get("scene"), "seed": job.get("seed"),
               "job_type": "still", "prompt_sha256": psha,
               "image_sha256": hashlib.sha256(open(f, "rb").read()).hexdigest(), "image": os.path.relpath(f, run_dir),
               "bytes": p["bytes"], "w": p["w"], "h": p["h"], "wall_seconds_output_mtime": round(wall, 1) if wall else None,
               "rendered_at": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": retry, "driver": "run_queue.py"},
              open(os.path.join(run_dir, tag, "render_ok.json"), "w", encoding="utf-8"), indent=1)
    qlog(run_dir, "DONE pos=%d tag=%s ok %dx%d still png wall=%ss bytes=%d retry=%s" % (job["pos"], tag, p["w"], p["h"],
         ("%.1f" % wall) if wall else "?", p["bytes"], retry))
    return True


def prepare(run_dir, job, retry, slog):
    """START line + the per-clip checks before a submit. Returns the graph, or None after logging the FAIL."""
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    if _CELL_CONTRACT and not CELL_RE.match(str(tag)):
        qlog(run_dir, "FAIL pos=%d tag=%s cell_contract=true: this run's tags must be clip cell dirs "
                      "(the cNN_sNNNNNNNN form of the long-clip plan); clip not submitted"
             % (job["pos"], tag))
        return None
    graph = os.path.join(d, "request.api.json")
    qlog(run_dir, "START pos=%d tag=%s arm=%s scene=%s seed=%s%s" % (job["pos"], tag, job.get("arm"), job.get("scene"),
         job.get("seed"), " (the one allowed unchanged retry)" if retry else ""))
    if not os.path.exists(graph):
        qlog(run_dir, "FAIL pos=%d tag=%s no graph" % (job["pos"], tag)); return None
    g0 = json.load(open(graph, encoding="utf-8"))
    ok, why = comm.guard_reason(g0)  # adults-only guard before EVERY clip
    if not ok:
        qlog(run_dir, "GATE-FAIL pos=%d tag=%s adults guard: %s" % (job["pos"], tag, why)); return None
    if not rgj.wake(slog):   # keep-alive touch of /comfyui/system_stats (ttl 300) + unload any LLM swapped in
        qlog(run_dir, "FAIL pos=%d tag=%s ComfyUI down" % (job["pos"], tag)); return None
    bad = rgj.static_check(g0)
    if bad:
        qlog(run_dir, "FAIL pos=%d tag=%s static %s" % (job["pos"], tag, " | ".join(bad[:4]))); return None
    return g0


def render_clip(run_dir, job, frames, size, retry, slog):
    """One clip, ONE render attempt, submit and wait (single-job path; the batch uses run_wave)."""
    g0 = prepare(run_dir, job, retry, slog)
    if g0 is None:
        return False
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    t0 = time.time()
    out, t_att = {}, time.time()
    s = comm.run(copy.deepcopy(g0), tag, meta(job, retry), d, logfile=os.path.join(d, "status.log"), timeout=JOB_TIMEOUT, out=out)
    return finish(run_dir, job, frames, size, retry, slog, s, out, g0, t0, t_att)


def meta(job, retry):
    return {"run": job["tag"], "attempt": int(retry), "label": "METHOD_ONLY", "plan": "run_queue"}


def disk_output(run_dir, tag, since):
    """Evict/stall disk fallback for run_queue jobs (fix 2026-10-31, backup run_queue.py.bak-0735). Their SaveImage/SaveVideo
    prefix is community/<run>/<tag>, so ComfyUI writes FLAT files output/community/<run>/<tag>_00001_.png|.mp4;
    rgj.collect_from_disk only looks in output/community/<tag>/ and missed all 9 landed Klein N12 stills (06:59 evict).
    Exact '<tag>_NNNNN_' match (E1 never matches E11), mtime >= submit-5 s; newest wins. None if nothing landed."""
    import glob
    d = os.path.join(OUT_ROOT, os.path.basename(os.path.normpath(run_dir)))
    pat = re.compile(re.escape(tag) + r"_\d{5}_?\.(png|mp4)$", re.I)
    try:
        pats = [
            os.path.join(glob.escape(d), glob.escape(tag) + "_*"),
            os.path.join(glob.escape(d), glob.escape(tag), glob.escape(tag) + "_*"),
        ]
        cands = [p for p_pat in pats for p in glob.glob(p_pat)]
        c = [p for p in cands
             if pat.match(os.path.basename(p)) and os.path.getmtime(p) >= since - 5]
    except OSError:
        return None
    return max(c, key=os.path.getmtime) if c else None


# --- (c) 2026-11-02 (brief 2026-11-02-2010): prompt_ids saved at submit, harvested before any re-submit ---------------
PIDS_FILE = "_prompt_ids.json"


def expected_prefix(g):
    """filename_prefix of the graph's SaveVideo/SaveImage node (where ComfyUI will write the output), else None."""
    for n in (g or {}).values():
        if n.get("class_type") in ("SaveVideo", "SaveImage") and isinstance(n.get("inputs", {}).get("filename_prefix"), str):
            return n["inputs"]["filename_prefix"]
    return None


def graph_expect(g):
    """(frames, (w, h)) as the submitted graph asks for, from the MiniMaxH3ReferenceToVideo node's
    length/width/height; None for a value the graph does not state as a literal. The graph is the truth
    of what was submitted; --frames/--size are only what the caller asked for (item 10, 2026-11-04).

    KEEP Lokken two-pass (b2): c0 is 384x672 then MinimaxH3LatentUpscaler3D mode.scale=2.0 -> final
    768x1344. Multiply by any LatentUpscaler3D scale so OBJECTIVE matches the saved mp4 (FG U5)."""
    n = None
    for _ct in ("MiniMaxH3ReferenceToVideo", "MiniMaxH3ImageToVideo", "EmptyMiniMaxH3LatentAV"):
        n = next((x for x in (g or {}).values() if x.get("class_type") == _ct), None)
        if n is not None:
            break
    i = (n or {}).get("inputs", {})
    num = lambda v: int(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    f, w, h = num(i.get("length")), num(i.get("width")), num(i.get("height"))
    if f is not None and f >= 1:
        while f % 17 != 5:
            f += 1
    # (c) 2026-11-06 brief t224x214 (Derrick): a continuation graph's truth is the CUMULATIVE latent, not the
    # first beat. Each MiniMaxH3GuidedContinuationWindow adds extension_frames visible frames (its 22-frame
    # overlap is hidden context and is trimmed by MiniMaxH3AppendContinuation), so OBJECTIVE must expect
    # beat 1 + every extension; the mp4 carries the whole clip. (Parity with validate_graph in
    # scripts/run_graph_job.py.)
    for node in (g or {}).values():
        if node.get("class_type") == "MiniMaxH3GuidedContinuationWindow":
            ext = num((node.get("inputs") or {}).get("extension_frames"))
            f = None if ext is None else (f + ext if f is not None else None)
    if w and h:
        scale = 1.0
        for node in (g or {}).values():
            if node.get("class_type") == "MinimaxH3LatentUpscaler3D":
                inp = node.get("inputs", {})
                s = inp.get("mode.scale", inp.get("scale", 1.0))
                if isinstance(s, (int, float)) and not isinstance(s, bool) and s > 0:
                    scale *= float(s)
        if scale != 1.0:
            w, h = int(round(w * scale)), int(round(h * scale))
    return f, (w, h) if w and h else None


def load_pids(run_dir):
    p = os.path.join(run_dir, PIDS_FILE)
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_pid(run_dir, tag, pid, prefix, retry):
    """Written right after each POST /prompt, so a driver/Shell death or an eviction never loses the prompt_id."""
    d = load_pids(run_dir)
    d[tag] = {"prompt_id": pid, "tag": tag, "expected_prefix": prefix, "submitted_at": time.time(),
              "submitted_at_ct": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": bool(retry)}
    tmp = os.path.join(run_dir, PIDS_FILE + ".tmp")
    json.dump(d, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, os.path.join(run_dir, PIDS_FILE))


def prefix_output(prefix, since):
    """Disk look-up by the saved expected prefix: output/<prefix>_NNNNN_.ext, flat or one folder down. Newest wins."""
    import glob
    if not prefix:
        return None
    base = os.path.join(comm.C, "output", *prefix.replace("\\", "/").split("/"))
    stem = os.path.basename(base)
    pat = re.compile(re.escape(stem) + r"_\d{5}_?\.(png|mp4)$", re.I)
    pats = [glob.escape(base) + "_*", os.path.join(glob.escape(base), glob.escape(stem) + "_*")]
    try:
        c = [p for pp in pats for p in glob.glob(pp) if pat.match(os.path.basename(p)) and os.path.getmtime(p) >= since - 5]
    except OSError:
        return None
    return max(c, key=os.path.getmtime) if c else None


def harvest(run_dir, jobs, frames, size, slog, queue_ids=None):
    """Before submitting, look for each job's earlier prompt_id: still in ComfyUI's queue -> adopt it (collect, do not
    re-submit); in /history -> collect; gone -> look on disk by the expected prefix. Returns (to_submit, adopted, done)
    where adopted = {prompt_id: entry} for run_wave to keep collecting."""
    rec = load_pids(run_dir)
    if not rec:
        return list(jobs), {}, []
    if queue_ids is None:
        try:
            q = comm.http(comm.BASE + "/queue", timeout=comm.POLL_TIMEOUT)
            queue_ids = {x[1] for x in q.get("queue_running", []) + q.get("queue_pending", [])}
        except Exception as ex:
            slog("harvest warn queue %s" % str(ex)[:120]); queue_ids = set()
    todo, adopted, done = [], {}, []
    for j in jobs:
        r = rec.get(j["tag"])
        if not r or not r.get("prompt_id"):
            todo.append(j); continue
        pid, d = r["prompt_id"], os.path.join(run_dir, j["tag"])
        e = {"job": j, "out": {}, "t_att": r.get("submitted_at", 0), "t0": r.get("submitted_at", 0),
             "log": os.path.join(d, "status.log"), "g0": json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))}
        if pid in queue_ids:
            qlog(run_dir, "HARVEST pos=%d tag=%s prompt_id=%s still in ComfyUI queue - adopted, not re-submitted" % (j["pos"], j["tag"], pid))
            adopted[pid] = e; continue
        s = None
        try:
            s = comm.fetch(pid, j["tag"], meta(j, False), d, e["t0"], e["log"], e["out"])
        except Exception as ex:
            slog("harvest warn history %s %s" % (j["tag"], str(ex)[:120]))
        if s is comm.PENDING or s is None and not e["out"]:
            s = None
            src = prefix_output(r.get("expected_prefix"), e["t_att"]) or disk_output(run_dir, j["tag"], e["t_att"])
            if src:
                comm.outcome(e["out"], "evicted", pid, note="harvested from disk by expected prefix")
        if s or e["out"].get("outcome") == "evicted":
            qlog(run_dir, "HARVEST pos=%d tag=%s prompt_id=%s collected from %s - not re-submitted" % (
                j["pos"], j["tag"], pid, "history" if s else "disk"))
            if settle(run_dir, e, s, frames, size, False, slog):
                done.append(j); continue
        todo.append(j)
    return todo, adopted, done



PI_DROP = os.environ.get("PI_DROP", "/mnt/qnap/derek-homes/derek.boone86@gmail.com/pi-drop")


def copy_to_pi_drop(run_dir, tag, src, slog):
    """Copy a finished clip to Derrick's QNAP pi-drop so he can watch it from his PC. Never fails the job."""
    try:
        rel = os.path.relpath(os.path.abspath(run_dir), os.path.expanduser("~/AI/community/runs"))
        name = (os.path.basename(os.path.abspath(run_dir)) if rel.startswith("..") else rel).replace(os.sep, "_")
        if tag != "clip":
            name += "_" + tag
        dst = os.path.join(PI_DROP, name + ".mp4")
        shutil.copyfile(src, dst)
        slog("PI_DROP copied %s" % dst)
    except Exception as e:  # QNAP down or not mounted: keep the local clip, just note it
        slog("PI_DROP skip %s: %s" % (tag, e))

def finish(run_dir, job, frames, size, retry, slog, s, out, g0, t0, t_att):
    """After a job ends (or stalls/evicts): disk fallback, then the OBJECTIVE check and the DONE line."""
    tag, d = job["tag"], os.path.join(run_dir, job["tag"])
    t = tag
    if not s and out.get("outcome") in ("stalled", "evicted", "submit_stall"):
        src = prefix_output(expected_prefix(g0), t_att) or disk_output(run_dir, t, t_att) or rgj.collect_from_disk(t, t_att, slog)
        if not src:
            qlog(run_dir, "FAIL pos=%d tag=%s stall %s prompt_id=%s" % (job["pos"], tag, out["outcome"], out.get("prompt_id"))); return False
        dst = os.path.join(d, t + os.path.splitext(src)[1])
        try:
            if os.path.exists(dst): os.remove(dst)
            os.link(src, dst)
        except OSError:
            shutil.copyfile(src, dst)
        s = {"file": dst}
    if not s:
        qlog(run_dir, "FAIL pos=%d tag=%s job error (%s)" % (job["pos"], tag, out.get("outcome"))); return False
    if job.get("job_type") == "still":
        return still_done(run_dir, job, tag, s["file"], g0, size, t0, retry, slog)
    gf, gs = graph_expect(g0)
    ef, es = gf or frames, gs or size
    if (ef, es) != (frames, size):
        qlog(run_dir, "NOTE pos=%d tag=%s cli frames=%s size=%sx%s vs graph frames=%s size=%sx%s (graph is the authority)" % (
            job["pos"], tag, frames, size[0], size[1], ef, es[0], es[1]))
    p, bf = rgj.probe(s["file"]), rgj.blackfreeze(s["file"])
    why = [] if p["bytes"] > 0 else ["0-byte file"]
    if (p["w"], p["h"]) != es: why.append("size %sx%s" % (p["w"], p["h"]))
    if p["frames"] != ef: why.append("frames %d != %d" % (p["frames"], ef))
    if not p["audio"]: why.append("no audio stream")
    why += ["detect " + x for x in bf]
    if why:
        qlog(run_dir, "FAIL pos=%d tag=%s objective %s" % (job["pos"], tag, "; ".join(why))); return False
    slog("OBJECTIVE ok %s frames=%d size=%sx%s audio=True bytes=%d" % (t, p["frames"], p["w"], p["h"], p["bytes"]))
    # t2554 (Derrick 2026-11-19): pi-drop gets only the RTX-upscaled clip, copied in upscale_done after UPSCALE ok
    rgj.contact_sheet(s["file"], os.path.join(d, tag + "_stills_contact.png"), p["duration"])
    outs = [os.path.join(OUT_ROOT, t, f) for f in os.listdir(os.path.join(OUT_ROOT, t))] if os.path.isdir(os.path.join(OUT_ROOT, t)) else []
    wall = (max(map(os.path.getmtime, outs)) - t0) if outs else None
    psha, pnote = prompt_sha(g0, next((n["inputs"].get("prompt", "") for n in g0.values()
                                      if n.get("class_type") == "MiniMaxH3ReferenceToVideo"), ""))
    if pnote:
        qlog(run_dir, "NOTE pos=%d tag=%s prompt_sha256 unresolved: %s" % (job["pos"], tag, pnote))
    json.dump({"tag": tag, "pos": job["pos"], "arm": job.get("arm"), "scene": job.get("scene"), "seed": job.get("seed"),
               "frames": frames, "prompt_sha256": psha,
               "clip_sha256": hashlib.sha256(open(s["file"], "rb").read()).hexdigest(), "clip": os.path.relpath(s["file"], run_dir),
               "bytes": p["bytes"], "w": p["w"], "h": p["h"], "audio": True, "wall_seconds_output_mtime": round(wall, 1) if wall else None,
               "rendered_at": time.strftime("%Y-%m-%d %H:%M:%S CT"), "retry": retry, "driver": "run_queue.py"},
              open(os.path.join(d, "render_ok.json"), "w", encoding="utf-8"), indent=1)
    qlog(run_dir, "DONE pos=%d tag=%s ok %dx%d %df audio yes wall=%ss bytes=%d retry=%s" % (job["pos"], tag, p["w"], p["h"],
         p["frames"], ("%.1f" % wall) if wall else "?", p["bytes"], retry))
    return True


def attempt(run_dir, job, frames, size, retry, slog):
    """One attempt; an error inside it (e.g. the 11:19 keep-alive TimeoutError) is a failed attempt, not a silent batch death."""
    try:
        return render_clip(run_dir, job, frames, size, retry, slog)
    except Exception as e:
        qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (job["pos"], job["tag"], type(e).__name__, str(e)[:160].replace("\n", " ")))
        return False


def stop_seen(run_dir):
    return os.path.exists(os.path.join(run_dir, "STOP"))


def stop_comfy(run_dir, slog, n_open):
    """STOP: drop everything still queued in ComfyUI and interrupt the running prompt."""
    for path, body in (("/queue", {"clear": True}), ("/interrupt", {})):
        try: comm.http(comm.BASE + path, body, timeout=60); slog("STOP POST %s ok" % path)
        except Exception as e: slog("STOP POST %s note %s" % (path, str(e)[:120]))
    qlog(run_dir, "STOP file seen: stopped collecting with %d submitted clip(s) unfinished; ComfyUI queue cleared and running prompt interrupted" % n_open)


def settle(run_dir, e, s, frames, size, retry, slog):
    """finish() for one submitted job; an error is a failed attempt, as in attempt()."""
    try:
        return finish(run_dir, e["job"], frames, size, retry, slog, s, e["out"], e["g0"], e.get("started", e["t0"]), e["t_att"])
    except Exception as ex:
        qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (e["job"]["pos"], e["job"]["tag"], type(ex).__name__, str(ex)[:160].replace("\n", " ")))
        return False


def run_wave(run_dir, jobs, frames, size, retry, slog, adopt=None):
    """Submit clips to ComfyUI one at a time (MAX_IN_FLIGHT = 1), then collect each as it finishes.
    adopt = {prompt_id: entry} from harvest(): jobs already in ComfyUI's queue, collected without a re-submit.
    Returns (failed jobs, stopped)."""
    failed, live = [], dict(adopt or {})
    pending = list(jobs)
    queue_timeouts = 0
    stopping = False
    while pending or live:
        if stop_seen(run_dir):
            if pending:
                qlog(run_dir, "STOP file seen: halted before submitting pos=%d tag=%s" % (pending[0]["pos"], pending[0]["tag"]))
            stop_comfy(run_dir, slog, len(live)); return failed, True
        while len(live) < MAX_IN_FLIGHT and pending:
            j = pending.pop(0)
            if stop_seen(run_dir):
                qlog(run_dir, "STOP file seen: halted before submitting pos=%d tag=%s" % (j["pos"], j["tag"]))
                stop_comfy(run_dir, slog, len(live)); return failed, True
            d = os.path.join(run_dir, j["tag"])
            e = {"job": j, "out": {}, "t_att": time.time(), "log": os.path.join(d, "status.log")}
            try:
                e["g0"] = prepare(run_dir, j, retry, slog)
                if e["g0"] is None:
                    failed.append(j); continue
                e["t0"] = time.time()
                pid = comm.submit(copy.deepcopy(e["g0"]), j["tag"], meta(j, retry), d, logfile=e["log"], out=e["out"])
            except Exception as ex:
                qlog(run_dir, "FAIL pos=%d tag=%s error %s: %s" % (j["pos"], j["tag"], type(ex).__name__, str(ex)[:160].replace("\n", " ")))
                failed.append(j); continue
            if pid is None:  # guard hit, POST rejected or submit stall: settled now, exactly as the one-job path does
                if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(j)
                continue
            try: save_pid(run_dir, j["tag"], pid, expected_prefix(e["g0"]), retry)
            except Exception as ex: slog("prompt_ids note %s" % str(ex)[:120])
            live[pid] = e
            slog("QUEUE submitted pos=%d tag=%s prompt_id=%s (in-flight %d/%d)" % (j["pos"], j["tag"], pid, len(live), MAX_IN_FLIGHT))
        if not live:
            break
        time.sleep(QPOLL_SEC)
        q_timeout = QUEUE_TIMEOUT_STOPPING if stopping else comm.POLL_TIMEOUT
        try:
            q = comm.http(comm.BASE + "/queue", timeout=q_timeout)
            queue_timeouts = 0
            if stopping:
                stopping = False
                slog("comfyui_auto answered /queue; stopping state cleared")
            running = {x[1] for x in q.get("queue_running", [])}
            pending_ids = {x[1] for x in q.get("queue_pending", [])}
        except Exception as ex:
            queue_timeouts += 1
            slog("poll warn queue %s" % str(ex)[:160])
            if queue_timeouts >= 2 or comm.comfy_stopping():
                if not stopping:
                    stopping = True
                    slog("comfyui_auto looks like it is being stopped (%d /queue timeouts)" % queue_timeouts)
                # While comfyui_auto is stopping, ComfyUI may finish rendering or output already landed
                for pid, e in list(live.items()):
                    src = prefix_output(expected_prefix(e["g0"]), e["t_att"]) or disk_output(run_dir, e["job"]["tag"], e["t_att"]) or rgj.collect_from_disk(e["job"]["tag"], e["t_att"], slog)
                    if src:
                        slog("DISCOVERY pos=%d tag=%s prompt_id=%s found output on disk during /queue timeout" % (e["job"]["pos"], e["job"]["tag"], pid))
                        comm.outcome(e["out"], "evicted", pid, note="found output on disk during comfyui stop/stall")
                        if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                        del live[pid]
            if comm.comfy_loaded() is False:  # same rule as comm.run: the history went with the process
                for pid, e in list(live.items()):
                    comm.log(f"poll stop {e['job']['tag']} comfyui_auto is not running: prompt_id {pid} is in no live history", e["log"])
                    comm.outcome(e["out"], "evicted", pid, note="history lost with the comfyui_auto process")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
            continue
        now = time.time()
        for pid, e in list(live.items()):
            tag = e["job"]["tag"]
            if pid in running:
                if "started" not in e:
                    e["started"] = now; comm.log(f"JOB running {tag} prompt_id={pid} queued={now - e['t0']:.0f}s", e["log"])
                elif now - e["started"] > JOB_TIMEOUT:
                    comm.log(f"JOB timeout {tag}", e["log"])
                    try:
                        comm.http(comm.BASE + "/interrupt", data={}, timeout=10, method="POST")
                        comm.http(comm.BASE + "/queue", data={"delete": [pid]}, timeout=10, method="POST")
                        comm.log(f"JOB cancelled via /interrupt and /queue delete {tag} prompt_id={pid}", e["log"])
                    except Exception as ex_cancel:
                        comm.log(f"JOB cancel error {tag}: {ex_cancel}", e["log"])
                    comm.outcome(e["out"], "stalled", pid, note=f"no history {JOB_TIMEOUT}s after ComfyUI started it; cancelled via /interrupt; the render may have landed in ComfyUI output")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
                continue
            if pid in pending_ids:
                if now - e["t0"] > 900:
                    comm.log(f"JOB pending timeout {tag} (>15m unstarted)", e["log"])
                    try:
                        comm.http(comm.BASE + "/interrupt", data={}, timeout=10, method="POST")
                        comm.http(comm.BASE + "/queue", data={"delete": [pid]}, timeout=10, method="POST")
                        comm.log(f"JOB cancelled via /interrupt and /queue delete {tag} prompt_id={pid}", e["log"])
                    except Exception as ex_cancel:
                        comm.log(f"JOB cancel error {tag}: {ex_cancel}", e["log"])
                    comm.outcome(e["out"], "stalled", pid, note="no progress for >15m in queue; cancelled via /interrupt")
                    if not settle(run_dir, e, None, frames, size, retry, slog): failed.append(e["job"])
                    del live[pid]
                continue
            try:
                s = comm.fetch(pid, tag, meta(e["job"], retry), os.path.join(run_dir, tag), e.get("started", e["t0"]), e["log"], e["out"])
            except Exception as ex:
                comm.log(f"poll warn {tag} {ex}", e["log"]); continue
            if s is comm.PENDING:
                e["miss"] = e.get("miss", 0) + 1
                if e["miss"] < EVICT_MISSES:
                    continue
                comm.log(f"poll stop {tag} prompt_id {pid} is in neither /queue nor /history (comfyui_auto restarted?)", e["log"])
                comm.outcome(e["out"], "evicted", pid, note="history lost with the comfyui_auto process")
                s = None
            if not settle(run_dir, e, s, frames, size, retry, slog): failed.append(e["job"])
            del live[pid]
    return failed, False


def main():
    ap = argparse.ArgumentParser(description="reusable batch render queue (one GPU window per batch)")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--queue", help="order file (default <run-dir>/_render_order.json): {'order': [{pos, tag, arm, scene, seed[, job_type, size]}]}")
    ap.add_argument("--resume", action="store_true", help="skip tags already DONE ok in _render_queue.log")
    ap.add_argument("--dry-run", action="store_true", help="list the clips; no lock, GPU or HTTP call")
    ap.add_argument("--frames", type=int, default=124)
    ap.add_argument("--size", default="768x1344")
    ap.add_argument("--detach", action="store_true", help="relaunch outside the caller's process tree (WMI) and return")
    ap.add_argument("--no-upscale", action="store_true",
                    help="skip the default RTX VideoSuperRes 2x ULTRA post-pass (card t286s1226); clips stay at the render size")
    ap.add_argument("--keep-comfy-process", action="store_true",
                    help="chained mode: at batch close still free ComfyUI's models (POST /free) but skip only the "
                         "llama-swap unload of comfyui_auto, so the next one-clip batch does not pay the process wake. "
                         "Default off: a normal run unloads comfyui_auto in finally as before.")
    ap.add_argument("--remote", action="store_true",
                    help="EVO-X3: queue on AlienPc ComfyUI over the tailnet (Serve :8446; scripts/remote_comfy.py). Implied on Linux.")
    ap.add_argument("--upscale-only", action="store_true",
                    help="t2565u: run only the RTX 2x post-pass on a finished run (no render), under the GPU lock")
    ap.add_argument("--probe", action="store_true", help="with --dry-run --remote: one GET /system_stats (ignored path, never wakes ComfyUI)")
    a = ap.parse_args()
    run_dir = os.path.abspath(a.run_dir)
    remote = a.remote or os.name != "nt"  # consolidation P1b 2026-11-16: the X3 has no local ComfyUI
    if remote:
        import remote_comfy
        local_upscale_done = upscale_done
        remote_comfy.enable(sys.modules[__name__])
        import remote_upscale  # t2564u: the 2x post-pass runs as one AlienPc ComfyUI job (was D5 "deferred")
        remote_upscale.enable(sys.modules[__name__], local_upscale_done)
    if a.detach:
        return detach(sys.argv[1:], run_dir)
    q = json.load(open(a.queue or os.path.join(run_dir, "_render_order.json"), encoding="utf-8"))
    jobs = q["order"] if isinstance(q, dict) else q
    global _CELL_CONTRACT  # B2-10: the long-clip plan declares the cell contract in its order file
    _CELL_CONTRACT = bool(q.get("cell_contract")) if isinstance(q, dict) else False
    if a.upscale_only and not a.dry_run:
        return upscale_only(run_dir, jobs)
    done = done_tags(run_dir) if a.resume else set()
    todo = [j for j in jobs if j["tag"] not in done]
    size = tuple(int(x) for x in a.size.lower().split("x"))
    print("queue %d clips, %d already DONE ok, %d to render" % (len(jobs), len(jobs) - len(todo), len(todo)))
    stale = unclosed_batch(run_dir)
    if stale:
        msg = "BATCH closed rc=9 reason=killed/unknown (batch opened %s never logged a close; found at the next start) done=%d/%d" % (
            stale, ok_count(run_dir, jobs), len(jobs))
        if a.dry_run: print("would log: " + msg)
        else: qlog(run_dir, msg)
    if a.dry_run:
        if _CELL_CONTRACT:
            bad_tags = [str(j["tag"]) for j in jobs if not CELL_RE.match(str(j["tag"]))]
            print("cell_contract=true: %d/%d tags are clip cell dirs (%s)%s"
                  % (len(jobs) - len(bad_tags), len(jobs), CELL_RE.pattern,
                     "; these would FAIL: " + ",".join(bad_tags) if bad_tags else ""))
        for j in todo:
            print("  pos %2d %s" % (j["pos"], j["tag"]))
        print("prompt_ids on file: %d (%s)" % (len(load_pids(run_dir)), PIDS_FILE))
        print("post-pass: %s" % ("off (--no-upscale)" if a.no_upscale else "RTX 2x as one AlienPc ComfyUI job (t2564u)" if remote else "RTX VideoSuperRes 2x ULTRA at native fps on every video clip"))
        print("comfy process: %s" % ("kept loaded at batch close (--keep-comfy-process: /free still runs, llama-swap unload skipped)"
                                     if a.keep_comfy_process else "unloaded at batch close (default)"))
        if remote:
            nbad = remote_comfy.dry_report(sys.modules[__name__], run_dir, todo)
            if a.probe:
                try:
                    comm.http(remote_comfy.API + "/system_stats", timeout=15); print("probe: :8446 reachable, ComfyUI loaded")
                except Exception as e:
                    print("probe: :8446 answered %s" % str(e)[:160])
            print("dry run: no lock, upload or POST made%s" % ("; %d clip(s) would FAIL" % nbad if nbad else ""))
            return 0  # same rc contract as the local dry run; FAIL lines above name any clip that would fail
        print("dry run: no lock, GPU or HTTP call made")
        return 0
    if not todo:
        return 0
    slog = lambda m: comm.log(m, os.path.join(run_dir, "status.log"))
    if _CELL_CONTRACT:
        bad_tags = [str(j["tag"]) for j in jobs if not CELL_RE.match(str(j["tag"]))]
        qlog(run_dir, "cell_contract=true: %d/%d tags are clip cell dirs (%s)%s"
             % (len(jobs) - len(bad_tags), len(jobs), CELL_RE.pattern,
                "; these FAIL: " + ",".join(bad_tags) if bad_tags else ""))
    r = subprocess.run([PY, "-m", "pytest", *PYTEST_FILES, "-q", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        qlog(run_dir, "GATE-FAIL batch pytest rc=%d" % r.returncode)
        qlog(run_dir, "BATCH closed rc=2 reason=pytest gate failed (pytest rc=%d) done=%d/%d: nothing queued" % (r.returncode, ok_count(run_dir, jobs), len(jobs)))
        return 2
    # #18: the lock alone decides (a live PID in gpu-render.lock = GPU_BUSY rc 7); gpu_guard pre-check dropped 2026-10-30
    # gpu_lock.ps1 -Acquire: exit 0 = acquired, exit 1 = HELD by a live PID (busy); anything else = the lock tool failed
    lrc, lout = rgj.ps_run(rgj.GPU_LOCK_PS, "-Acquire", "-Owner", str(os.getpid()), "-Note", "run_queue " + os.path.basename(run_dir))
    slog("gpu_lock acquire rc=%d %s" % (lrc, lout[:140]))
    if lrc == 1:
        qlog(run_dir, "GPU_BUSY batch: gpu-render.lock held by a live PID - nothing queued (rc 7)")
        qlog(run_dir, "BATCH closed rc=7 reason=GPU busy (gpu-render.lock held by a live PID) done=%d/%d: nothing queued" % (ok_count(run_dir, jobs), len(jobs)))
        return 7
    if lrc != 0:
        qlog(run_dir, "ERROR batch lock tool error: gpu_lock.ps1 rc=%d %s" % (lrc, lout[:140]))
        qlog(run_dir, "BATCH closed rc=8 reason=lock tool error (gpu_lock.ps1 rc=%d) done=%d/%d: nothing queued" % (lrc, ok_count(run_dir, jobs), len(jobs)))
        return 8
    rc, reason, failed = 0, "all queued clips DONE ok", []
    try:
        if not rgj.wake(slog):  # unload the LLM once, wake ComfyUI once
            rc, reason = 4, "ComfyUI down at batch start"
            qlog(run_dir, "FAIL batch ComfyUI down"); return rc
        qlog(run_dir, "BATCH open: %d clips, lock held, comfyui_auto kept loaded" % len(todo))
        adopted = {}
        if a.resume or stale:  # (c) a resumed or killed batch: collect earlier prompt_ids before any re-submit
            todo, adopted, _h = harvest(run_dir, todo, a.frames, size, slog)
        first, stopped = run_wave(run_dir, todo, a.frames, size, False, slog, adopt=adopted)
        if first and not stopped:
            again, stopped = run_wave(run_dir, first, a.frames, size, True, slog)
            for j in again:
                qlog(run_dir, "FAIL pos=%d tag=%s failed twice (one unchanged retry used) - skipped" % (j["pos"], j["tag"]))
                failed.append(j["tag"])
        if stopped:
            rc, reason = 1, "STOP file"
        if failed and rc == 0:
            rc, reason = 5, "%d clip(s) failed twice: %s" % (len(failed), " ".join(failed))
    except KeyboardInterrupt:
        qlog(run_dir, "INTERRUPTED (Ctrl-C)"); rc, reason = 130, "Ctrl-C"
    except BaseException as e:  # S13: the 11:19 batch died here on a TimeoutError and still logged rc=0
        rc, reason = 8, "error %s: %s" % (type(e).__name__, str(e)[:160].replace("\n", " "))
        qlog(run_dir, "ERROR batch %s" % reason)
    finally:
        comm.mark_collected()  # (c) graceful-stop may stop comfyui_auto now: every output this batch will collect is in
        try: comm.free_comfy(os.path.join(run_dir, "_render_queue.log"))  # B2-1 (2026-11-05): free_comfy wants a log PATH, the same path qlog() writes; slog (a function) raised TypeError and line 629 swallowed it
        except Exception as e: slog("free_comfy note %s" % str(e)[:120])
        # --keep-comfy-process (chain mode, 2026-11-15): comm.free_comfy above always runs; only the llama-swap
        # unload of comfyui_auto is skipped, so the process stays warm for the next batch in the chain.
        if a.keep_comfy_process:
            slog("KEEP comfyui_auto (--keep-comfy-process: /free ran, llama-swap unload skipped)")
        else:
            try: rgj.post(comm.LS + "/api/models/unload/comfyui_auto", 300); slog("UNLOAD comfyui_auto")
            except Exception as e: slog("unload note %s" % str(e)[:120])
        if a.no_upscale:
            qlog(run_dir, "UPSCALE skipped (--no-upscale): clips stay at the render size")
        elif rc != 130:  # post-pass inside the lock window, after comfyui_auto freed the VRAM (never on Ctrl-C)
            try:
                # F2 (2026-11-08): the 2x post-pass is the requested default deliverable, so its counts reach
                # rc/reason instead of only the log: a failed post-pass stops --wait / --qnap-final reporting a
                # run as delivered (rc 9 = post-pass failure, a code of its own, not GPU_BUSY rc 7). upscale_done
                # keeps the raw clip, --no-upscale asks for no post-pass and stays rc 0, a batch whose
                # post-passes all succeed is unchanged, and the failure is named in the closing BATCH line.
                n_up_ok, n_up_fail = upscale_done(run_dir, jobs, slog)
                if n_up_fail and rc == 0:
                    rc, reason = 9, ("%d of %d clips failed the requested 2x post-pass (raw clips kept)"
                                     % (n_up_fail, n_up_ok + n_up_fail))
                    qlog(run_dir, "UPSCALE batch %s" % reason)
            except Exception as e:
                qlog(run_dir, "UPSCALE FAIL batch error %s: %s (raw clips kept)" % (type(e).__name__, str(e)[:160]))
                if rc == 0:
                    rc, reason = 9, "post-pass error %s (raw clips kept)" % type(e).__name__
        try: rgj.gpu_unlock(slog)
        except Exception as e: slog("unlock note %s" % str(e)[:120])
        try: n_ok = ok_count(run_dir, jobs)
        except Exception as e:
            n_ok = 0; slog("ok_count note %s" % str(e)[:120])
        if rc == 0 and n_ok < len(jobs):  # never rc=0 while a queued clip lacks a DONE ok line
            rc, reason = 6, "ended with %d queued clip(s) missing a DONE ok line" % (len(jobs) - n_ok)
        # the closing line never claims an unload that --keep-comfy-process skipped
        tail = "comfyui_auto kept loaded" if a.keep_comfy_process else "comfyui_auto unloaded"
        qlog(run_dir, "BATCH closed rc=%d reason=%s done=%d/%d: %s, lock released" % (rc, reason, n_ok, len(jobs), tail))
    return rc


if __name__ == "__main__":
    sys.exit(main())
