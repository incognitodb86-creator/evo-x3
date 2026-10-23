r"""run_graph_job.py - harness runner for one prepared ComfyUI API graph (ALI-147 handoff to Forge, ALI-160).
Called by ralph.ps1 job kind "graph"; Forge never runs it itself. Usage:
  python -u run_graph_job.py <arm_dir> <tag> [--frames N] [--frames-tol T] [--timeout S] [--max-redo 2]
Input: <arm_dir>\request.api.json. Uses comm.run (status.log JOB start/end lines) unchanged.
Redo rule (Derrick / max-DECISIONS 2026-10-22 3:46 PM CT): only OBJECTIVE failures redo, max 2 (redo 1 same seed, redo 2 seed+1):
JOB error (incl. node_errors at submit), ffprobe frame count / missing audio / 0-byte, black or frozen frames. No judge here.
ComfyUI: woken via llama-swap's documented /comfyui/ route, then addressed on its own port; never /upstream. Unloaded after via
POST /api/models/unload/comfyui_auto. Exit: 0 ok, 2 static check, 3 adults-only guard, 4 ComfyUI down, 5 objective fail after redos."""
import os, sys, json, copy, time, argparse, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import comm
LS = comm.LS; COMFY = "http://127.0.0.1:10004"; comm.BASE = COMFY
def post(u, t=120): return urllib.request.urlopen(urllib.request.Request(u, data=b"", method="POST"), timeout=t).read()
# ALI-163 R3 harness fix (2026-10-23, backup run_graph_job.py.bak-20261023-hcimg): a graph job can be an IMAGE job
# (Klein 9B reference-sheet edit -> SaveImage -> .png). The objective gate below is a VIDEO gate (audio stream, exact frame
# count, blackdetect/freezedetect, timed contact sheet), so an honest sheet render failed as "no audio stream" and went STUCK
# after 2 redos. Video jobs are untouched: CreateVideo/SaveVideo write .mp4, so this branch only fires on these extensions.
# Image gate = ffprobe decodes it, reports a size, exactly 1 packet, bytes > 0. No judge, no quality redo (unchanged rule).
IMG_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".webp")
def comfy_ok():
    try: urllib.request.urlopen(COMFY + "/system_stats", timeout=10).read(); return True
    except Exception: return False
def wake(log):
    r = comm.running(); names = [x.get("model") for x in (r.get("running") or [])] if isinstance(r, dict) else []
    for n in names:
        if n and n != "comfyui_auto": log(f"UNLOAD LLM {n}"); post(f"{LS}/api/models/unload/{n}")
    if not comfy_ok():
        try: urllib.request.urlopen(LS + "/comfyui/", timeout=900).read()
        except Exception as e: log(f"COMFY wake note {str(e)[:160]}")
    for _ in range(60):
        if comfy_ok(): return True
        time.sleep(5)
    return False
def static_check(g):
    oi = json.loads(urllib.request.urlopen(COMFY + "/object_info", timeout=120).read()); bad = []
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
    """stills every 0.5 s in +-1.5 s windows around 0:10/0:20/0:30/0:40/0:50 (inside the clip); no judging."""
    ts = sorted({round(m + d * 0.5, 2) for m in (10, 20, 30, 40, 50) for d in range(-3, 4) if 0 <= m + d * 0.5 <= dur - 0.05})
    if not ts: return None
    sel = "+".join(f"between(t\\,{t - 0.02:.2f}\\,{t + 0.02:.2f})" for t in ts); cols = 7; rows = (len(ts) + cols - 1) // cols
    vf = f"select='{sel}',scale=256:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile={cols}x{rows}:padding=4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", f, "-vf", vf, "-vsync", "vfr", "-frames:v", "1", out], capture_output=True, text=True)
    return out if r.returncode == 0 and os.path.exists(out) else None
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("arm_dir"); ap.add_argument("tag"); ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--frames-tol", type=int, default=0); ap.add_argument("--timeout", type=int, default=3600); ap.add_argument("--max-redo", type=int, default=2); a = ap.parse_args()
    D = a.arm_dir; SL = os.path.join(D, "status.log"); log = lambda m: comm.log(m, SL)
    g0 = json.load(open(os.path.join(D, "request.api.json"), encoding="utf-8"))
    for n in g0.values():
        p = n["inputs"].get("prompt")
        if isinstance(p, str) and not comm.guard_ok(p): log(f"CLIP_SKIP {a.tag} adults-only guard"); return 3
    if not wake(log): log(f"COMFY_DOWN {a.tag}"); return 4
    bad = static_check(g0)
    if bad: log(f"STATIC_FAIL {a.tag} " + " | ".join(bad[:8])); return 2
    seeds = [k for k, n in g0.items() if n["class_type"] == "RandomNoise"]; res = {"tag": a.tag, "attempts": []}; rc = 5
    try:
        for att in range(a.max_redo + 1):
            g = copy.deepcopy(g0); tag = a.tag if att == 0 else f"{a.tag}_redo{att}"
            if att == 2:
                for k in seeds: g[k]["inputs"]["noise_seed"] = int(g[k]["inputs"]["noise_seed"]) + 1
            if att: log(f"REDO {att}/{a.max_redo} {a.tag} (objective failure; {'seed+1' if att == 2 else 'same seed'})")
            if not comfy_ok() and not wake(log): log(f"COMFY_DOWN {tag}"); rc = 4; break
            s = comm.run(g, tag, {"run": a.tag, "attempt": att, "label": "METHOD_ONLY", "plan": "ALI-147"}, D, logfile=SL, timeout=a.timeout)
            why = []
            if not s: why = ["JOB error"]
            else:
                img = os.path.splitext(s["file"])[1].lower() in IMG_EXT
                p = probe(s["file"]); bf = [] if img else blackfreeze(s["file"])
                if p["bytes"] <= 0: why.append("0-byte file")
                if img:
                    if not (p["w"] and p["h"]): why.append("image unreadable (ffprobe reported no size)")
                    elif p["frames"] != 1: why.append(f"image packet count {p['frames']} != 1")
                else:
                    if not p["audio"]: why.append("no audio stream")
                    if a.frames and abs(p["frames"] - a.frames) > a.frames_tol: why.append(f"frames {p['frames']} != {a.frames}+-{a.frames_tol}")
                why += [f"detect {x}" for x in bf]
                res["attempts"].append(dict(p, tag=tag, file=s["file"], secs=s["secs"], blackfreeze=bf, image=img))
            if not why:
                cs = None if img else contact_sheet(s["file"], os.path.join(D, a.tag + "_stills_contact.png"), p["duration"])
                res.update(ok=True, file=s["file"], contact_sheet=cs, image=img); log(f"OBJECTIVE ok {tag} image={img} frames={p['frames']} size={p['w']}x{p['h']} audio={p['audio']} dur={p['duration']:.3f} bytes={p['bytes']} contact={cs}"); rc = 0; break
            log(f"OBJECTIVE FAIL {tag} " + "; ".join(why)); res.setdefault("fails", []).append({"tag": tag, "why": why})
        else:
            log(f"STUCK {a.tag} objective failure after {a.max_redo} redos - flagged for Derrick")
    finally:
        try: post(f"{LS}/api/models/unload/comfyui_auto", 300); log("UNLOAD comfyui_auto (POST /api/models/unload)")
        except Exception as e: log(f"unload note {str(e)[:120]}")
        json.dump(res, open(os.path.join(D, "objective.json"), "w", encoding="utf-8"), indent=1)
    return rc
if __name__ == "__main__": sys.exit(main())
