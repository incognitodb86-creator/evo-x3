# ALI-163 R3 harness-fix dry run (CPU only, no ComfyUI, no network): prove the new image branch.
# Imports run_graph_job (module import has no side effects: it only sets constants) and re-runs the
# exact gate from main() on a real PNG (SaveImage output shape) and a real mp4 (video shape).
import os, sys
sys.path.insert(0, r"C:\AI\community\scripts")
import run_graph_job as R, comm
print("IMG_EXT", R.IMG_EXT)
def gate(f, frames_req, tol):
    img = os.path.splitext(f)[1].lower() in R.IMG_EXT
    p = R.probe(f); bf = [] if img else R.blackfreeze(f)
    why = []
    if p["bytes"] <= 0: why.append("0-byte file")
    if img:
        if not (p["w"] and p["h"]): why.append("image unreadable (ffprobe reported no size)")
        elif p["frames"] != 1: why.append(f"image packet count {p['frames']} != 1")
    else:
        if not p["audio"]: why.append("no audio stream")
        if frames_req and abs(p["frames"] - frames_req) > tol: why.append(f"frames {p['frames']} != {frames_req}+-{tol}")
    why += [f"detect {x}" for x in bf]
    return img, p, why
PNG = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\RS016_portrait_1152x2016.png"
MP4 = r"C:\AI\community\runs\ali147_pool_hc_c1_s51100001\ali147_pool_hc_c1_s51100001.mp4"
for f, fr, tol in ((PNG, 0, 0), (MP4, 481, 0), (MP4, 243, 0)):
    img, p, why = gate(f, fr, tol)
    print("FILE", os.path.basename(f), "req_frames", fr, "-> image branch:", img, "objective:", p)
    print("   ->", "OK" if not why else "FAIL " + "; ".join(why))
print("guard on a sheet prompt:", comm.guard_ok("reference sheet of the same adult woman, face close-up panel, front, side, back and three-quarter views, plain grey studio background, photorealistic"))
