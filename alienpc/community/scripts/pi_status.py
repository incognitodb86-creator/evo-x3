"""pi_status.py - READ-ONLY status for Pi / Pi mobile (Grok Bot, 2026-10-28, Derek: "read-only status wrapper for llama-swap, ComfyUI and GPU").
Only GETs llama-swap /running and ComfyUI /system_stats + /queue, runs gpu_guard.ps1 (read-only verdict), nvidia-smi query, and lists the newest runs.
Never wakes ComfyUI (no /comfyui/ wake route), never unloads, never POSTs, never touches /upstream. Exit 0 always."""
import json, os, subprocess, time, urllib.request
LS = "http://127.0.0.1:8080"; COMFY_PORT = next((p for p in (10002, 10003) if __import__("socket").socket().connect_ex(("127.0.0.1", p)) == 0), 10002); COMFY = "http://127.0.0.1:%d" % COMFY_PORT  # gpu_guard.ps1:12-13 port order; read-only, never the /comfyui wake route
RUNS = r"C:\AI\community\runs"; GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
def get(u, t=6): return urllib.request.urlopen(u, timeout=t).read()
def j(u):
    try: return json.loads(get(u))
    except Exception as e: return {"error": str(e)[:120]}
print("llama-swap running:", [x.get("model") for x in j(LS + "/running").get("running", [])] if "error" not in j(LS + "/running") else j(LS + "/running"))
sysd = j(COMFY + "/system_stats"); print("ComfyUI :%d:" % COMFY_PORT, "down" if "error" in sysd else "up")
if "error" not in sysd:
    q = j(COMFY + "/queue"); print("ComfyUI queue: running=%s pending=%s" % (len(q.get("queue_running", [])), len(q.get("queue_pending", []))))
try:
    r = subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-File",GUARD],capture_output=True,text=True,timeout=120)
    print("gpu_guard rc=%s %s" % (r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]))
except Exception as e: print("gpu_guard error", e)
try:
    print("nvidia-smi:", subprocess.run(["nvidia-smi","--query-gpu=utilization.gpu,memory.used,memory.total","--format=csv,noheader"],capture_output=True,text=True,timeout=15).stdout.strip())
except Exception as e: print("nvidia-smi error", e)
try:
    d = sorted((os.path.join(RUNS,n) for n in os.listdir(RUNS) if os.path.isdir(os.path.join(RUNS,n))), key=os.path.getmtime, reverse=True)[:5]
    print("newest runs:")
    for p in d: print("  %s  %s" % (time.strftime("%m-%d %H:%M", time.localtime(os.path.getmtime(p))), os.path.basename(p)))
except Exception as e: print("runs error", e)
