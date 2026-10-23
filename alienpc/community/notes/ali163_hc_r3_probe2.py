# ALI-163 R3 probe 2 (read-only): where is the flux2/Qwen text encoder, and Klein render timings on disk.
import os, json, re
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
M = os.path.join(C, "models")
hits = []
for root, dirs, files in os.walk(M):
    depth = os.path.relpath(root, M).count(os.sep)
    if depth >= 3:
        dirs[:] = []
    for f in files:
        low = f.lower()
        if "qwen" in low or "flux2" in low or "klein" in low:
            hits.append((os.path.relpath(os.path.join(root, f), M), os.path.getsize(os.path.join(root, f))))
print("== model files matching qwen/flux2/klein")
for n, s in sorted(hits):
    print(f"   {n}  {s}")
print("== CLIPLoader exact path check (kedit_wf node 3)")
p = os.path.join(M, "clip", "qwen_3_8b_fp8mixed.safetensors")
print("   exists:", os.path.isfile(p))
print("== python interpreters")
for p in (r"C:\Users\derek\director\.venv\Scripts\python.exe", r"C:\AI\director\.venv\Scripts\python.exe"):
    print("  ", p, os.path.isfile(p))
print("== Klein render timings in 5slock logs (loop logs)")
pat = re.compile(r"(KLEIN|SBREF|kedit|KLEIN_OUT|secs|elapsed|took)", re.I)
base = r"C:\Users\derek\5slock"
cands = []
for root, dirs, files in os.walk(base):
    if root.count(os.sep) - base.count(os.sep) >= 2:
        dirs[:] = []
    for f in files:
        if f.lower().endswith((".log", ".json", ".md")) and ("log" in f.lower() or "klein" in f.lower() or "sb" in f.lower()):
            cands.append(os.path.join(root, f))
print("   candidate log files:", len(cands))
for f in cands[:25]:
    print("   ", f, os.path.getsize(f))
print("== storyboard_e10 Klein outputs (proof the graph path ran on this box)")
sb = os.path.join(base, "storyboard_e10")
for d in sorted(os.listdir(sb))[:40] if os.path.isdir(sb) else []:
    fp = os.path.join(sb, d)
    if os.path.isdir(fp):
        png = [x for x in os.listdir(fp) if x.lower().endswith(".png")]
        print("   ", d, "png count", len(png), png[:2])
