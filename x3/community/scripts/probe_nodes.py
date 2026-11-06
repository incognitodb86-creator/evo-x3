#!/usr/bin/env python3
"""Capture a fingerprinted live ComfyUI /object_info dump - the dumper objinfo_has.py documents.

Wakes comfyui_auto through the existing run_graph_job.wake() path (the documented llama-swap /comfyui/
passthrough; no new HTTP client), GETs /object_info ONCE, saves the raw JSON to
notes\\objinfo\\object_info_<YYYYMMDD>.json, and prints the byte size, SHA256 and class-count fingerprint.

Usage (PYTHONIOENCODING=utf-8, from C:\\AI\\community\\scripts):
  python probe_nodes.py                       # capture only, no lease (ComfyUI assumed awake)
  python probe_nodes.py --lease --note "why"  # take/release C:\\AI\\locks\\gpu-render.lock around it
  python probe_nodes.py --lease --free --log <path>   # + free weights, unload comfyui_auto, poll /running empty
  python probe_nodes.py --out <path>          # explicit dump path

This is a model load, not a render: never submits a graph, never queues, prints no prompt text
(object_info is node metadata only). Verify names from the saved dump with objinfo_has.py --dump <path>,
and rebuild the index docs with notes\\objinfo\\_make_index.py <path>.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_graph_job as rg  # noqa: E402  (route constants + wake/gpu helpers, stdlib only)
import comm  # noqa: E402

DIR = r"C:\AI\community\notes\objinfo"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(DIR, "object_info_%s.json" % datetime.date.today().strftime("%Y%m%d")))
    ap.add_argument("--lease", action="store_true", help="take/release the GPU lock file around the capture")
    ap.add_argument("--note", default="probe_nodes object_info capture (model load, no render)")
    ap.add_argument("--free", action="store_true", help="free weights + unload comfyui_auto afterwards, poll /running empty")
    ap.add_argument("--log", default=None, help="log file for the free/unload lines (a real path, not a callable)")
    ns = ap.parse_args()

    def log(s):
        print("   " + s, flush=True)

    def get(u):
        """Report an admin route as measured: comm.running() is the documented llama-swap /running route, while
        /api/models/running answers 404 on this build (measured 2026-11-05 22:05 CT), so it is printed, never assumed."""
        try:
            return comm.http(u, timeout=30)
        except Exception as e:
            return "GET %s -> %s" % (u, e)

    if ns.lease and not rg.gpu_lock(log, ns.note):
        print("GPU_BUSY: lock not acquired, nothing touched"); return 7
    rc = 0
    try:
        if not rg.wake(log):
            print("WAKE FAILED: comfyui_auto never answered /system_stats"); rc = 8
        else:
            raw = urllib.request.urlopen(rg.COMFY + "/object_info", timeout=180).read()
            with open(ns.out, "wb") as fh:
                fh.write(raw)
            oi = json.loads(raw)
            print("saved: %s" % ns.out)
            print("bytes: %d" % len(raw))
            print("sha256: %s" % hashlib.sha256(raw).hexdigest())
            print("class_count (top-level keys): %d" % len(oi))
            print("comfy_loaded: %s" % comm.comfy_loaded())
            print("running_after_wake: %s" % comm.running())
        if ns.free:
            print("free_comfy(%r) -> %s" % (ns.log, comm.free_comfy(ns.log)))
            print("unload_post: %s" % comm.http(comm.LS + "/api/models/unload/comfyui_auto", timeout=180, method="POST"))
            for _ in range(60):
                r = comm.running()
                if isinstance(r, dict) and not (r.get("running") or []):
                    break
                time.sleep(5)
            print("running_after_unload: %s" % comm.running())
            print("api_models_running: %s" % get(comm.LS + "/api/models/running"))
    finally:
        if ns.lease:
            rg.gpu_unlock(log)
    return rc


if __name__ == "__main__":
    sys.exit(main())
