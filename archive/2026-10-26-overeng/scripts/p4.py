# P4 (ALI-126) chaining test at draft size: 10 s vs 5 s chunks, latent continuation vs hard cut, Anti-Burn 0.5 on chunk 2+ vs off.
import sys, os, json, subprocess
sys.path.insert(0, r"C:\AI\community\scripts"); from comm import *; import prompt_writer as pw
OUT = os.path.join(W, "p4"); LF = os.path.join(OUT, "p4.log"); PD = os.path.join(OUT, "prompts"); os.makedirs(PD, exist_ok=True)
FF = r"C:\Users\derek\AppData\Local\Microsoft\Winget\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
W_, H_, STEPS, SEED = 576, 1024, 8, 51060000   # D3 draft (0.59 MP), 8 steps for drafts
NOTE = "adult woman, dark hair slicked back, metallic geometric top, black photo studio, hard key light"
B = ["She slowly lifts the metallic top off over her head, tosses it aside and turns her bare upper body toward the key light, holding eye contact.",
     "She steps closer to the camera, tilts her head back and runs both hands up through her slicked-back hair, then smiles.",
     "She turns in a slow full circle under the key light, hands on her hips, looking back over her shoulder at the camera.",
     "She sits down on a black studio stool, crosses her legs, leans forward with her elbows on her knees and laughs softly."]
log("P4 START", LF)
# prompts first (LLM), then unload, then render
def P(i, secs, beat, prev=None, cut=False):
    sh = {"id": f"p4_b{i}_{secs}s" + ("_cut" if cut else ""), "image_note": NOTE, "beat": beat + (" Use two [Shot N] segments with a hard cut to a closer angle halfway." if cut else ""), "prev_beat": prev}
    return pw.write(sh, "short", secs, PD, logfile=LF)
p5 = [P(i, 5, B[i], B[i-1] if i else None) for i in range(4)]
p10 = [P(0, 10, B[0] + " " + B[1], cut=True), P(1, 10, B[2] + " " + B[3], B[0] + " " + B[1], cut=True)]
pcut2 = P(9, 10, B[2] + " " + B[3], cut=True)   # independent second clip (hard cut join, no continuation)
ensure_comfy(LF)
img = stage("FD003", W_, H_)
f10, f5 = frames_for(10), frames_for(5)
runs = [
 ("p4_A10_cont_noAB",  build("i2v", p10, img, W_, H_, f10, STEPS, SEED, "community/p4", ext_frames=238)),
 ("p4_A10_cont_AB05",  build("i2v", p10, img, W_, H_, f10, STEPS, SEED, "community/p4", ext_frames=238, antiburn=0.5)),
 ("p4_B5_cont_noAB",   build("i2v", p5, img, W_, H_, f5, STEPS, SEED, "community/p4", ext_frames=119)),
 ("p4_B5_cont_AB05",   build("i2v", p5, img, W_, H_, f5, STEPS, SEED, "community/p4", ext_frames=119, antiburn=0.5)),
 ("p4_C10_cut_part1",  build("i2v", [p10[0]], img, W_, H_, f10, STEPS, SEED, "community/p4")),
 ("p4_C10_cut_part2",  build("i2v", [pcut2], img, W_, H_, f10, STEPS, SEED + 1, "community/p4")),
]
res = {}
for tag, g in runs:
    meta = {"phase": "P4", "w": W_, "h": H_, "steps": STEPS, "seed": SEED, "vsa": True, "shift": "10/3", "sampler": "euler/simple",
            "antiburn": 0.5 if "AB05" in tag else None, "chunks": sum(1 for k in g if k.startswith("win")) + 1}
    r = run(g, tag, meta, OUT, LF); res[tag] = r and {"secs": r["secs"], "file": r["file"]}
# hard-cut join of C parts (D18 ffmpeg concat)
if res.get("p4_C10_cut_part1") and res.get("p4_C10_cut_part2"):
    lst = os.path.join(OUT, "c_concat.txt")
    open(lst, "w").write("".join(f"file '{res[k]['file']}'\n" for k in ("p4_C10_cut_part1", "p4_C10_cut_part2")))
    out = os.path.join(OUT, "p4_C10_cut_joined.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=False)
    res["p4_C10_cut_joined"] = {"file": out, "exists": os.path.exists(out)}
json.dump(res, open(os.path.join(OUT, "p4_result.json"), "w"), indent=1)
log("P4 DONE " + json.dumps({k: (v or {}).get("secs") for k, v in res.items()}), LF)
