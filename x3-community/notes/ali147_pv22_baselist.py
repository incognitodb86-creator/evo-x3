# -*- coding: utf-8 -*-
# ALI-147 PV2-2 (read-only): list the base run dir (find/grep skip it via .gitignore, so use os.listdir)
# and report every .mp4 with size + hash target, so fairness.txt / PROOF.md name the real control files.
import os
BASE = "C:/AI/community/runs/p7_r2_c3_pmot_full_pool"
rows = []
for x in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, x).replace("\\", "/")
    if os.path.isfile(p):
        rows.append((os.path.getsize(p), p))
for s, p in rows:
    print("%11d  %s" % (s, p))
print("mp4 files:")
for s, p in rows:
    if p.endswith(".mp4"):
        print("  %d  %s" % (s, p))
DIP = "C:/AI/community/runs/ali147_pool_dip_s51080000"
if os.path.isdir(DIP):
    print("DIP dir:")
    for x in sorted(os.listdir(DIP)):
        q = os.path.join(DIP, x).replace("\\", "/")
        if os.path.isfile(q):
            print("  %11d  %s" % (os.path.getsize(q), q))
