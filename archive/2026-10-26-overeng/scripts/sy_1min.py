# P6 comparison: ~1-minute video on the CURRENT Switchyard path (its own graph builder + live config: REF2VA + AddGuide frame 0,
# 124 frames/cell, chained by the previous cell's last frame like its h3_extender kind), rendered on the same stock ComfyUI, ffmpeg concat.
import sys, os, json, subprocess
sys.path.insert(0, r"C:\AI\community\scripts"); from comm import *; import prompt_writer as pw
from batch_queue import stitch, contact_sheet, FFD
DPY = r"C:\AI\director\.venv\Scripts\python.exe"
OUT = os.path.join(W, "runs", "p6_1min_switchyard"); PD = os.path.join(OUT, "prompts"); LF = os.path.join(OUT, "run.log"); os.makedirs(PD, exist_ok=True)
beats = json.load(open(os.path.join(W, "shots", "p6_1min_beats.json"), encoding="utf-8"))
N = 12; prompts = []
log("SY1MIN START", LF)
for i in range(N):
    b = beats["beats"][i // 2]
    sh = {"id": f"sy_c{i:02d}", "image_note": beats["note"], "beat": b + (" (first half of this beat)" if i % 2 == 0 else " (second half: complete the action)"),
          "prev_beat": beats["beats"][(i - 1) // 2] if i else None}
    prompts.append(pw.write(sh, "short", 5, PD, logfile=LF))
ensure_comfy(LF)
img = stage("D15", 768, 1344); done = []
for i in range(N):
    pf = os.path.join(PD, f"sy_c{i:02d}_short.txt"); gj = os.path.join(OUT, f"sy_c{i:02d}.sy.json")
    r = subprocess.run([DPY, os.path.join(W, "scripts", "sy_graph.py"), img, pf, str(51090000 + i), f"community/p6_sy/sy_c{i:02d}", gj], capture_output=True, text=True)
    if r.returncode != 0: log(f"SY graph build failed c{i}: {r.stderr[-600:]}", LF); break
    d = json.load(open(gj)); g = d["graph"]
    res = run(g, f"sy_c{i:02d}", {"phase": "P6", "path": "switchyard", "eff": d["eff"], "image": img, "seed": 51090000 + i}, OUT, LF)
    if not res: break
    done.append(res)
    nxt = f"community/sy_last_c{i:02d}.png"
    subprocess.run([os.path.join(FFD, "ffmpeg.exe"), "-v", "error", "-y", "-sseof", "-0.2", "-i", res["file"], "-update", "1", "-frames:v", "1",
                    os.path.join(C, "input", nxt)], capture_output=True)
    img = nxt
files = [d["file"] for d in done]
json.dump(done, open(os.path.join(OUT, "results.json"), "w"), indent=1)
contact_sheet(files, os.path.join(OUT, "contact_sheet.png"), os.path.join(OUT, "notes.md"), {"run": "p6_1min_switchyard", "when": time.strftime("%Y-%m-%d %H:%M CT")})
ok, err = stitch(files, os.path.join(OUT, "p6_1min_switchyard_stitched.mp4"))
log(f"SY1MIN DONE cells={len(done)}/{N} total_secs={sum(d['secs'] for d in done):.0f} stitched={ok} {err}", LF)
