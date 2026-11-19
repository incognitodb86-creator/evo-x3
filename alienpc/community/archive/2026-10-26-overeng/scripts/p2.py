import sys, os, json; sys.path.insert(0, r"C:\AI\community\scripts"); from comm import *
OUT = os.path.join(W, "p2"); LF = os.path.join(OUT, "p2.log"); os.makedirs(OUT, exist_ok=True)
log("P2 START", LF); ensure_comfy(LF)
img_c = stage("FD006", 416, 736)
canary = "The adult woman from the start image stands still in the courtyard and smiles softly at the camera. Static shot, soft daylight. Sound: quiet ambience."
g = build("i2v", [canary], img_c, 416, 736, 29, 8, 51050001, "community/p2_canary")
r = run(g, "p2_canary_vsa_416x736_29f_8st", {"phase": "P2", "arm": "canary", "vsa": True}, OUT, LF)
vsa = r is not None
if not vsa:
    log("VSA canary failed -> retry dense", LF)
    g = build("i2v", [canary], img_c, 416, 736, 29, 8, 51050001, "community/p2_canary", vsa=False)
    r = run(g, "p2_canary_dense_416x736_29f_8st", {"phase": "P2", "arm": "canary", "vsa": False}, OUT, LF)
    if r is None: log("P2 FAIL canary", LF); sys.exit(1)
prompt = open(r"C:\Users\derek\5slock\runs\ali80-6clip-20261019\prompts\clip2_short.txt", encoding="utf-8").read().strip()
img = stage("FD006", 768, 1344)
meta = {"phase": "P2", "image": "FD006 (ALI-80 approved)", "prompt_file": "ali80 prompts/clip2_short.txt", "w": 768, "h": 1344,
        "frames": 124, "steps": 10, "sampler": "euler/simple", "shift": "10/3", "vsa": vsa, "seed": 51050001, "unet": UNET}
g = build("i2v", [prompt], img, 768, 1344, 124, 10, 51050001, "community/p2_clip2_short")
r = run(g, "p2_clip2_short_768x1344_124f_10st_" + ("vsa" if vsa else "dense"), meta, OUT, LF)
log("P2 " + ("PASS" if r else "FAIL"), LF)
