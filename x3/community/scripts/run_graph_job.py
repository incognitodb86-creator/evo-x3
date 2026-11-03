r"""run_graph_job.py - harness runner for one prepared ComfyUI API graph (ALI-147 handoff to Forge, ALI-160).
Called by ralph.ps1 job kind "graph"; Forge never runs it itself. Usage:
  python -u run_graph_job.py <arm_dir> <tag> [--frames N] [--frames-tol T] [--timeout S] [--max-redo 2]
Input: <arm_dir>\request.api.json. Uses comm.run (status.log JOB start/end lines) unchanged.
Redo rule (Derrick / max-DECISIONS 2026-10-22 3:46 PM CT): only OBJECTIVE failures redo, max 2 (redo 1 same seed, redo 2 seed+1):
JOB error (incl. node_errors at submit), ffprobe frame count / missing audio / 0-byte, black or frozen frames. No judge here.
RENDER-TIMEOUT (2026-10-26) - a client stall is NOT an objective failure, so it is never re-queued, and a render that
landed on disk is collected instead of re-rendered. Measured cost of the old behaviour: 7 JOB starts for
ali163_hc15_bd002_s51150021 (2026-10-24 21:52:58, 23:32:53, 2026-10-25 00:14:58, 00:53:12, 01:32:46, 02:13:22,
02:54:11), 18.2-19.2 min each, 7 byte-identical mp4s in ComfyUI output (sha256 b8d0b7b8...), 0 "JOB end" lines in
300 lines of its status.log = ~2.2 GPU-hours for one clip, and that is what llama-swap's own doc warns about:
"Avoid using many simultaneous client retries as a capacity control: they create more queued work"
(docs/kb/guides/routing/capacity-and-queues.md, saved notes/web/rt_ls_capacity-and-queues.txt:16-20).
The exclusive GPU window is now the box's published mechanism: gpu_guard.ps1 must report IDLE (rc 0) before
queueing, and C:/AI/director/scripts/gpu_lock.ps1 -Acquire/-Release holds C:/AI/locks/gpu-render.lock under this
process's PID for the whole window (gpu_guard.ps1:6,126-128 counts a live PID as BUSY; the lock's own header said
"NOT used by any render script yet"). The lock makes comfy_ctl.py stop/restart refuse and every gate say BUSY.
ComfyUI: every call goes through llama-swap's documented /comfyui/ passthrough (docs/kb/guides/
upstreams/comfyui.md, wired to the reserved comfyui_auto); no port is hard-coded because
llama-swap assigns it (--port ${PORT}); never /upstream. Unloaded after via
POST /api/models/unload/comfyui_auto. Exit: 0 ok, 2 static check, 3 adults-only guard, 4 ComfyUI down, 5 objective
fail after redos, 6 client stall (prompt_id recorded, job NOT re-queued - collect it, do not re-render), 7 GPU busy
(gate BUSY or the lock is held by a live PID)."""
import os, sys, json, copy, time, argparse, subprocess, urllib.request, glob, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import comm
LS = comm.LS
# CA2 0.2 community USAGE audit (2026-10-24, commit d4d975b): llama-swap docs/kb/guides/upstreams/comfyui.md makes
# the client base its dedicated /comfyui/ passthrough, and the port is llama-swap-assigned: the live
# C:/AI/director/config/llama-swap.yaml has startPort 10001, every cmd uses --port ${PORT}, and the
# literal 10004 appears 0 times in it. The old COMFY = "http://127.0.0.1:10004" was a DERIVED port
# (7-member alphabetical order), and this box's own gpu_guard.ps1:12-13 resolves ComfyUI's port from
# the main.py command line with a 10002/10003 fallback - so the port is not a constant to bake in.
# Address the documented route; llama-swap proxies it to comfyui_auto and blocks on readiness.
COMFY = LS + "/comfyui"; comm.BASE = COMFY
GPU_LOCK_PS = r"C:\AI\director\scripts\gpu_lock.ps1"; GPU_GUARD_PS = r"C:\AI\director\scripts\gpu_guard.ps1"
def post(u, t=120): return urllib.request.urlopen(urllib.request.Request(u, data=b"", method="POST"), timeout=t).read()
# RENDER-TIMEOUT (2026-10-26): the box's published GPU-window mechanism (C:/AI/director/scripts/gpu_lock.ps1 +
# gpu_guard.ps1). gpu_guard exits 0 = IDLE, 3 = BUSY, and honours a lock file whose first number is a live PID.
def ps_run(file, *args):
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", file, *args],
                           capture_output=True, text=True, timeout=300)
        return r.returncode, (r.stdout + r.stderr).strip().replace("\n", " | ")
    except Exception as e:
        return 9, f"{os.path.basename(file)} run error {str(e)[:120]}"
def gpu_idle(log):
    rc, out = ps_run(GPU_GUARD_PS); log(f"gpu_guard rc={rc} {out[:200]}"); return rc == 0
def gpu_lock(log, note):
    rc, out = ps_run(GPU_LOCK_PS, "-Acquire", "-Owner", str(os.getpid()), "-Note", note)
    log(f"gpu_lock acquire rc={rc} {out[:140]}"); return rc == 0
def gpu_unlock(log):
    rc, out = ps_run(GPU_LOCK_PS, "-Release", "-Owner", str(os.getpid())); log(f"gpu_lock release rc={rc} {out[:140]}")
def collect_from_disk(tag, since, log):
    """A paid render must never be re-rendered. When comfyui_auto died, its history died with it, but the graph's own
    SaveVideo wrote the clip where the graph's subfolder says: ComfyUI output/community/<tag>/. Measured 2026-10-25:
    the gi046_s51150031 clip (8,087,674 B) sits there with mtime 04:04:52 while the run dir has no mp4 and
    p7/jobs/...result.json was never written. Returns the newest media file written at/after `since`, else None."""
    d = os.path.join(comm.C, "output", "community", tag)
    try:
        pats = [os.path.join(d, "*"), os.path.join(d, tag, "*")]
        cands = [p for p_pat in pats for p in glob.glob(p_pat)
                 if p.lower().endswith((".mp4", ".png")) and os.path.getmtime(p) >= since - 5]
    except OSError:
        return None
    return max(cands, key=os.path.getmtime) if cands else None
# ALI-163 R3 harness fix (2026-10-23, backup run_graph_job.py.bak-20261023-hcimg): a graph job can be an IMAGE job
# (Klein 9B reference-sheet edit -> SaveImage -> .png). The objective gate below is a VIDEO gate (audio stream, exact frame
# count, blackdetect/freezedetect, timed contact sheet), so an honest sheet render failed as "no audio stream" and went STUCK
# after 2 redos. Video jobs are untouched: CreateVideo/SaveVideo write .mp4, so this branch only fires on these extensions.
# Image gate = ffprobe decodes it, reports a size, exactly 1 packet, bytes > 0. No judge, no quality redo (unchanged rule).
IMG_EXT = (".png",)  # Max review 2026-10-23: .png image jobs only (the sheet path); other image types stay on the video gate
def comfy_ok():
    try: urllib.request.urlopen(COMFY + "/system_stats", timeout=10).read(); return True
    except Exception: return False
def wake(log):
    r = comm.running(); names = [x.get("model") for x in (r.get("running") or [])] if isinstance(r, dict) else []
    for n in names:
        if n and n != "comfyui_auto": log(f"UNLOAD LLM {n}"); post(f"{LS}/api/models/unload/{n}")
    if not comfy_ok():
        # docs/comfyui.md: GET to the exact route root is IN the fixed ignore set and "returns 404
        # while the model is not loaded", so it cannot wake anything; a non-ignored path "starts it
        # as usual" and llama-swap blocks up to healthCheckTimeout (1200 in the live config). So the
        # root GET is gone and the poll below runs on a starting path (/system_stats) for 240 x 5 s.
        log("wake: GET /comfyui/ is ignored by llama-swap (docs/comfyui.md); polling /comfyui/system_stats")
    for _ in range(240):
        if comfy_ok(): return True
        time.sleep(5)
    return False
# Face-detection ban (director plan L7/17/238): no graph may hold a face detector, identity model or auto-crop, and no
# graph may load a banned model file (models\pulid\pulid_flux2_klein_v2.safetensors stays on disk, never loaded).
# Lifted for the flux stills plan ONLY for face_sim (C-ID) and T2 MediaPipe face boxes (Derrick 2026-10-30 2:34 PM CT:
# "Yes, lift the face-detection ban for the flux stills plan too, keep face_sim and T2"); neither is in BANNED.
BANNED = ("insightface", "reactor", "pulid", "instantid", "faceid", "auraface", "facedetailer", "ultralytics",
          "bbox_detector", "segm_detector", "autocropfaces", "faceanalysis", "faceswap", "facerestore",
          "face_yolo", "yolov8n-face", "yolov8s-face", "yolo-face", "yolo_face", "faceyolo")  # face-only yolo (audit FP-1):
# pose detectors such as DWPose's yolox_l.onnx stay allowed; any other "*face*yolo*" name is caught by banned_nodes()
def banned_nodes(g):
    bad = []
    for k, n in g.items():
        ct = str(n.get("class_type", "")).lower()
        bad += [f"{k}: banned class {n.get('class_type')} ({w})" for w in BANNED if w in ct][:1]
        bad += [f"{k}.{a}: banned model {v} (face yolo)" for a, v in n.get("inputs", {}).items() if isinstance(v, str)
                and "face" in v.lower() and "yolo" in v.lower() and not any(w in v.lower() for w in BANNED)][:1]
        bad += [f"{k}.{a}: banned model {v} ({w})" for a, v in n.get("inputs", {}).items() if isinstance(v, str)
                for w in BANNED if w in v.lower() and v.lower().endswith((".safetensors", ".pt", ".pth", ".onnx", ".bin", ".ckpt"))][:1]
    return bad
def static_check(g):
    bad = banned_nodes(g)
    oi = json.loads(urllib.request.urlopen(COMFY + "/object_info", timeout=120).read())
    for k, n in g.items():
        ct = n.get("class_type")
        if ct not in oi: bad.append(f"{k}: unknown class {ct}"); continue
        spec = oi[ct]["input"]; names = set(spec.get("required", {})) | set(spec.get("optional", {}))
        bad += [f"{k}.{a}: not an input of {ct}" for a in n["inputs"] if a.split(".")[0] not in names]
        bad += [f"{k}: required input {r} missing" for r in spec.get("required", {}) if r not in n["inputs"] and not any(a.startswith(r + ".") for a in n["inputs"])]
        bad += [f"{k}.{a}: links missing node {v[0]}" for a, v in n["inputs"].items() if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str) and v[0] not in g]
    return bad
def probe(f):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate,nb_read_packets", "-of", "json", f], capture_output=True, text=True).stdout or "{}")
    v = [s for s in o.get("streams", []) if s.get("codec_type") == "video"]; a = [s for s in o.get("streams", []) if s.get("codec_type") == "audio"]
    return {"frames": int(v[0]["nb_read_packets"]) if v else 0, "w": v[0].get("width") if v else None, "h": v[0].get("height") if v else None,
            "fps": v[0].get("r_frame_rate") if v else None, "audio": bool(a), "duration": float(o.get("format", {}).get("duration", 0) or 0), "bytes": int(o.get("format", {}).get("size", 0) or 0)}
def blackfreeze(f):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f, "-vf", "blackdetect=d=1.0:pix_th=0.10,freezedetect=n=-60dB:d=2", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [l.split("] ", 1)[-1] for l in e.splitlines() if "black_start" in l or "freeze_start" in l][:6]
def contact_sheet(f, out, dur):
    """stills every second across the clip per Derrick brief; no judging."""
    if dur <= 25:
        ts = [float(s) for s in range(int(dur) + 1) if s <= dur - 0.05]
        cols = 4
    else:
        ts = sorted({round(m + d * 0.5, 2) for m in (10, 20, 30, 40, 50) for d in range(-3, 4) if 0 <= m + d * 0.5 <= dur - 0.05})
        cols = 7
    if not ts: return None
    sel = "+".join(f"between(t\\,{t - 0.02:.2f}\\,{t + 0.02:.2f})" for t in ts); rows = (len(ts) + cols - 1) // cols
    vf = f"select='{sel}',scale=256:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}:padding=4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", f, "-vf", vf, "-vsync", "vfr", "-frames:v", "1", out], capture_output=True, text=True)
    return out if r.returncode == 0 and os.path.exists(out) else None
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("arm_dir"); ap.add_argument("tag"); ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--frames-tol", type=int, default=0); ap.add_argument("--timeout", type=int, default=3600); ap.add_argument("--max-redo", type=int, default=2); a = ap.parse_args()
    D = a.arm_dir; SL = os.path.join(D, "status.log"); log = lambda m: comm.log(m, SL)
    t_start = time.time()
    g0 = json.load(open(os.path.join(D, "request.api.json"), encoding="utf-8"))
    for n in g0.values():
        for s in comm.prompt_strings(n.get("inputs", {})):
            if not comm.guard_ok(s): log(f"CLIP_SKIP {a.tag} adults-only guard"); return 3
    # RENDER-TIMEOUT (2026-10-26): every OFFLINE check runs before the GPU window is taken. The window is held by
    # C:/AI/locks/gpu-render.lock, and gpu_guard.ps1:6,126-128 counts a live PID in that file as BUSY, so an early
    # return that skips -Release would leave the box saying BUSY forever and block every later render.
    seeds = [k for k, n in g0.items() if n["class_type"] == "RandomNoise"]; res = {"tag": a.tag, "attempts": []}; rc = 5
    if not gpu_idle(log): log(f"GPU_BUSY {a.tag} gpu_guard is not IDLE - nothing queued"); return 7
    if not gpu_lock(log, f"run_graph_job {a.tag}"): log(f"GPU_BUSY {a.tag} gpu-render.lock held by a live PID - nothing queued"); return 7
    if not wake(log): log(f"COMFY_DOWN {a.tag}"); gpu_unlock(log); return 4
    try:
        bad = static_check(g0)
        if bad: log(f"STATIC_FAIL {a.tag} " + " | ".join(bad[:8])); return 2
        for att in range(a.max_redo + 1):
            g = copy.deepcopy(g0); tag = a.tag if att == 0 else f"{a.tag}_redo{att}"
            if att == 2:
                for k in seeds: g[k]["inputs"]["noise_seed"] = int(g[k]["inputs"]["noise_seed"]) + 1
            if att: log(f"REDO {att}/{a.max_redo} {a.tag} (objective failure; {'seed+1' if att == 2 else 'same seed'})")
            if not comfy_ok() and not wake(log): log(f"COMFY_DOWN {tag}"); rc = 4; break
            out = {}
            t_att = time.time()
            s = comm.run(g, tag, {"run": a.tag, "attempt": att, "label": "METHOD_ONLY", "plan": "ALI-147"}, D, logfile=SL, timeout=a.timeout, out=out)
            why = []
            oc = out.get("outcome", "ok")
            if not s and oc in ("stalled", "evicted", "submit_stall"):
                src = collect_from_disk(tag, t_att, log)
                if src:
                    dst = os.path.join(D, tag + os.path.splitext(src)[1])
                    shutil.copyfile(src, dst)
                    s = {"file": dst, "secs": round(time.time() - t_att, 1), "collected_from_disk": True, "src": src}
                    json.dump(dict(meta={"run": a.tag, "attempt": att}, tag=tag, file=dst, src=src, prompt_id=out.get("prompt_id"),
                                   outcome=oc, collected_from_disk=True, finished=time.strftime("%Y-%m-%d %H:%M CT")),
                              open(dst + ".json", "w", encoding="utf-8"), indent=1)
                    log(f"COLLECTED {tag} {src} (outcome={oc} prompt_id={out.get('prompt_id','none')}: the render landed, the history did not survive)")
            if not s:
                if oc in ("stalled", "evicted", "submit_stall"):
                    # RENDER-TIMEOUT: the client stopped seeing the job, which is not an objective failure, so the
                    # published redo rule does not apply. Re-queueing is what burned 7 identical 18-19 min renders.
                    res["stall"] = {"tag": tag, "outcome": oc, "prompt_id": out.get("prompt_id"), "note": out.get("note", ""),
                                    "collect_path": os.path.join(comm.C, "output", "community", tag)}
                    log(f"STALL {tag} outcome={oc} prompt_id={out.get('prompt_id','none')} - NOT re-queued; collect from {res['stall']['collect_path']} or re-check history"); rc = 6; break
                why = ["JOB error"]
            else:
                img = a.frames == 0 and os.path.splitext(s["file"])[1].lower() in IMG_EXT  # image gate only for frames-0 requests
                p = probe(s["file"]); bf = [] if img else blackfreeze(s["file"])
                if p["bytes"] <= 0: why.append("0-byte file")
                if img:
                    if not (p["w"] and p["h"]): why.append("image unreadable (ffprobe reported no size)")
                    elif p["frames"] != 1: why.append(f"image packet count {p['frames']} != 1")
                else:
                    if not p["audio"]: why.append("no audio stream")
                    if a.frames and abs(p["frames"] - a.frames) > a.frames_tol: why.append(f"frames {p['frames']} != {a.frames}+-{a.frames_tol}")
                why += [f"detect {x}" for x in bf]
                res["attempts"].append(dict(p, tag=tag, file=s["file"], secs=s["secs"], blackfreeze=bf, image=img, outcome=oc,
                                            collected_from_disk=bool(s.get("collected_from_disk"))))
            if not why:
                cs = None if img else contact_sheet(s["file"], os.path.join(D, a.tag + "_stills_contact.png"), p["duration"])
                res.update(ok=True, file=s["file"], contact_sheet=cs, image=img); log(f"OBJECTIVE ok {tag} image={img} frames={p['frames']} size={p['w']}x{p['h']} audio={p['audio']} dur={p['duration']:.3f} bytes={p['bytes']} contact={cs}"); rc = 0; break
            log(f"OBJECTIVE FAIL {tag} " + "; ".join(why)); res.setdefault("fails", []).append({"tag": tag, "why": why})
        else:
            log(f"STUCK {a.tag} objective failure after {a.max_redo} redos - flagged for Derrick")
    finally:
        try: post(f"{LS}/api/models/unload/comfyui_auto", 300); log("UNLOAD comfyui_auto (POST /api/models/unload)")
        except Exception as e: log(f"unload note {str(e)[:120]}")
        gpu_unlock(log)   # RENDER-TIMEOUT: release C:/AI/locks/gpu-render.lock so the gate opens for the next job
        json.dump(res, open(os.path.join(D, "objective.json"), "w", encoding="utf-8"), indent=1)
    return rc
if __name__ == "__main__": sys.exit(main())
