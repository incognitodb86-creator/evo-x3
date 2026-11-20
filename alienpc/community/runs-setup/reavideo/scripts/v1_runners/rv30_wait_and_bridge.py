
"""Wait for X3 llama-swap concurrency to free, then run h3max_bridge. Do not evict the loaded model."""
from __future__ import annotations
import json, os, ssl, sys, time, urllib.error, urllib.request, runpy

def load_evo_key():
    v = (os.environ.get("EVO_X3_LLM_KEY") or "").strip()
    if v:
        return v
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
        val, _ = winreg.QueryValueEx(h, "EVO_X3_LLM_KEY")
    return str(val or "").strip()

key = load_evo_key()
if not key:
    print("NOT_READY missing EVO_X3_LLM_KEY")
    raise SystemExit(2)

ctx = ssl._create_unverified_context()
headers = {"Authorization": "Bearer " + key, "Content-Type": "application/json"}
base = "https://evo-x3-1.tailf242b2.ts.net"
payload = {
    "model": "ref2va-27b-heretic-q4",
    "temperature": 0,
    "max_tokens": 8,
    "messages": [{"role": "user", "content": "Reply with the single word OK."}],
}

def ping():
    data = json.dumps(payload).encode()
    req = urllib.request.Request(base + "/v1/chat/completions", data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")[:200]
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, raw[:240].replace(key, "<REDACTED>")
    except Exception as e:
        return "ERR", f"{type(e).__name__}: {e}"

# backoff: 0, 30, 45, 60, 90, 90, 90, 90  (~8 min of waiting after first immediate try)
waits = [0, 30, 45, 60, 90, 90, 90, 90]
ok = False
for i, w in enumerate(waits, start=1):
    if w:
        print(f"WAIT {w}s before ping {i}/{len(waits)}", flush=True)
        time.sleep(w)
    status, body = ping()
    print(f"PING {i} status={status} body={body[:180]}", flush=True)
    if status == 200:
        ok = True
        break
    if status != 429 and status != "ERR":
        # unexpected; still retry a bit
        continue

if not ok:
    print("NOT_READY X3 llama-swap still at concurrency_limit after retries; did not evict loaded model")
    raise SystemExit(3)

# Launch the real bridge
root = r"C:\Users\derek\AppData\Local\Temp\rv30_stage"
sys.path[:0] = [
    root + r"\scripts\h3max_bridge\src",
    root + r"\scripts\parody",
    root + r"\scripts",
]
os.environ["BETA7_CONVERT_DIR"] = root + r"\scripts\parody"
os.environ["EVO_X3_LLM_KEY"] = key
os.environ["LLM_API_KEY"] = key
sys.argv = [
    "rv30_run_bridge.py",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\stems.json",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\bridge",
]
print("START_BRIDGE", flush=True)
runpy.run_path(root + r"\runners\rv30_run_bridge.py", run_name="__main__")
