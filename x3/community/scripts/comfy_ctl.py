"""comfy_ctl.py - Forge's ComfyUI start / stop / restart / status (Max, 2026-10-23, ALI-173).
Approval: Derrick 2026-10-23 1:07 PM CT "Yes, add 120 GPU min and 10 jobs for the bakeoff and let Forge restart and call ComfyUI itself".
ComfyUI (comfyui_auto) is a llama-swap member in the exclusive "main" group with Forge's own model, so:
  start   = GET http://127.0.0.1:8080/comfyui/ (llama-swap's documented wake route; it swaps the LLM out), then wait for comfy_ok
  stop    = refused while a render runs (gpu_guard.ps1 BUSY = ComfyUI queue / render process / GPU lock); else
            POST http://127.0.0.1:8080/api/models/unload/comfyui_auto (llama-swap runs comfy_graceful_stop.ps1, which also waits for the queue)
  restart = stop, then start, then comfy_ok (needed after installing custom nodes)
  status  = comfy_ok (GET http://127.0.0.1:8080/comfyui/system_stats, llama-swap route), ComfyUI /queue counts, gpu_guard verdict, llama-swap /running
Exit: 0 ok (prints COMFY_OK on start/restart), 3 refused (render running), 4 ComfyUI down after start/restart, 2 usage.
Never /upstream. This file is harness-owned (Max): Forge must not edit it."""
import json, subprocess, sys, time, urllib.request
LS = "http://127.0.0.1:8080"; COMFY = LS + "/comfyui"
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"; LOG = r"C:\AI\community\notes\comfy_ctl.log"
def log(m):
    line = time.strftime("%Y-%m-%d %H:%M:%S CT ") + m
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f: f.write(line + "\n")
    except OSError: pass
def get(u, t=10): return urllib.request.urlopen(u, timeout=t).read()
def comfy_ok():
    try: get(COMFY + "/system_stats"); return True
    except Exception: return False
def queue():
    try:
        q = json.loads(get(COMFY + "/queue")); return len(q.get("queue_running", [])), len(q.get("queue_pending", []))
    except Exception: return None
def guard():
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", GUARD], capture_output=True, text=True, timeout=120)
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    except Exception as e: return 9, [f"guard error {e}"]
def busy():
    q = queue()
    if q and sum(q) > 0: return f"ComfyUI queue running={q[0]} pending={q[1]}"
    rc, out = guard()
    return None if rc == 0 else f"gpu_guard rc={rc} {out[0][:200]}"
def running():
    try: return [x.get("model") for x in json.loads(get(LS + "/running")).get("running", [])]
    except Exception as e: return [f"unreadable: {e}"]
def stop():
    why = busy()
    if why: log(f"REFUSED stop/restart: render running ({why})"); return 3
    if "comfyui_auto" not in running() and not comfy_ok(): log("stop: ComfyUI not loaded"); return 0
    log("stop: POST /api/models/unload/comfyui_auto")
    urllib.request.urlopen(urllib.request.Request(LS + "/api/models/unload/comfyui_auto", data=b"", method="POST"), timeout=1900).read()
    for _ in range(60):
        if not comfy_ok(): log("stop: ComfyUI down"); return 0
        time.sleep(5)
    log("stop: ComfyUI still answering after 300 s"); return 4
def start():
    if not comfy_ok():
        log("start: GET /comfyui/ (llama-swap wake; swaps the LLM out)")
        try: get(LS + "/comfyui/", 900)
        except Exception as e: log(f"start: wake note {str(e)[:160]}")
    for _ in range(72):
        if comfy_ok(): log(f"COMFY_OK {COMFY} running={running()}"); return 0
        time.sleep(5)
    log("COMFY_DOWN after 360 s"); return 4
def status():
    log(f"status: comfy_ok={comfy_ok()} queue={queue()} guard={guard()} running={running()}"); return 0
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "status": sys.exit(status())
    if cmd == "start": sys.exit(start())
    if cmd == "stop": sys.exit(stop())
    if cmd == "restart":
        rc = stop()
        sys.exit(rc if rc else start())
    print(__doc__); sys.exit(2)
