# ALI-163 R4F probe 4: how to sample N indexed frames from the mp4s in this venv (no ffmpeg subprocess, no GPU).
# imageio 2.37 + imageio-ffmpeg are installed in C:\AI\qa_gate_venv (see notes/env_qa_gate.txt).
import time, sys
import imageio.v3 as iio
import numpy as np

paths = [r"C:\AI\community\runs\ali147_pool_hc_r1_s51130001\ali147_pool_hc_r1_s51130001.mp4",
         r"C:\AI\community\runs\ali147_pool_hc_r1.mp4"]
for p in paths:
    t = time.time()
    try:
        meta = iio.immeta(p, plugin="FFMPEG")
        print(p.split("\\")[-1], "meta fps=%s frames~%s dur=%s" % (meta.get("fps"), meta.get("frames"), meta.get("duration")), "%.1fs" % (time.time() - t))
    except Exception as e:
        print(p.split("\\")[-1], "immeta FAIL", type(e).__name__, str(e)[:150])
    t = time.time()
    try:
        fr = iio.imread(p, plugin="FFMPEG", index=[0, 100, 200])
        print("  imread index list ->", np.shape(fr), "%.1fs" % (time.time() - t))
    except Exception as e:
        print("  imread index list FAIL", type(e).__name__, str(e)[:200], "%.1fs" % (time.time() - t))
    t = time.time()
    try:
        n = 0
        for f in iio.imiter(p, plugin="FFMPEG"):
            n += 1
        print("  imiter frames=%d shape=%s %.1fs" % (n, np.shape(f), time.time() - t))
    except Exception as e:
        print("  imiter FAIL", type(e).__name__, str(e)[:150], "%.1fs" % (time.time() - t))
