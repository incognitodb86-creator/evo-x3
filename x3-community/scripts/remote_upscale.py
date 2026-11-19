"""X3 remote mode: the RTX 2x post-pass as ONE ComfyUI job on AlienPc (Derrick t2564u, option A; replaces D5 "deferred").

run_queue.upscale_done keeps all of its rules (only DONE-ok video clips without an "upscale" block, exact 2x size, same
frames/fps/audio, <tag>.mp4 swapped only after the check, <tag>_raw.mp4 kept, pi-drop gets only the 2x clip). Only the
frame loop moves: instead of nvvfx in a local venv (AlienPc), the raw clip is uploaded to AlienPc ComfyUI and run through
the official ComfyUI_Nvidia_VFX_Nodes video workflow (decode -> RTXVideoSuperResolution scale 2.0 ULTRA -> encode).
Encode matches AlienPc's own post-pass: libx264 crf 16 yuv420p at the source's own fps (VHS h264-mp4 format), audio kept.
No secrets: :8446 has no key (scoped by the Tailscale grant).
"""
import json, os, subprocess, time, uuid
import urllib.error, urllib.request

import remote_comfy as rc

INPUT_NAME = "x3_rtx2x_input.mp4"   # AlienPc ComfyUI input/ (t2571u)
OUT_SUBDIR = "community/rtx2x"   # AlienPc ComfyUI output/community/rtx2x/ (render outputs live under output/community/)


def _fps(src):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=r_frame_rate", "-of", "json", src],
                                  capture_output=True, text=True, check=True).stdout)
    n, d = o["streams"][0]["r_frame_rate"].split("/")
    f = float(n) / float(d)
    return int(f) if f.is_integer() else f


def graph(name, fps, prefix):
    """API graph per the node's example workflow (rtx_video_upscale.json) with VHS load/combine for crf/pix_fmt control."""
    return {
        "1": {"class_type": "VHS_LoadVideo", "inputs": {
            "video": name, "force_rate": 0, "custom_width": 0, "custom_height": 0,
            "frame_load_cap": 0, "skip_first_frames": 0, "select_every_nth": 1}},
        "2": {"class_type": "RTXVideoSuperResolution", "inputs": {
            "images": ["1", 0], "resize_type": "scale by multiplier", "resize_type.scale": 2.0,
            "quality": "ULTRA", "strength": 1.0, "image_encoding": "8-bit RGB"}},
        "3": {"class_type": "VHS_VideoCombine", "inputs": {
            "images": ["2", 0], "audio": ["1", 2], "frame_rate": fps, "loop_count": 0,
            "filename_prefix": prefix, "format": "video/h264-mp4", "pix_fmt": "yuv420p", "crf": 16,
            "save_metadata": False, "trim_to_audio": False, "pingpong": False, "save_output": True}},
    }


def _post_prompt(g):
    body = json.dumps({"prompt": g, "client_id": "x3-rtx2x-" + uuid.uuid4().hex[:8]}).encode()
    req = urllib.request.Request(rc.API + "/prompt", data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=120).read())["prompt_id"]
    except urllib.error.HTTPError as e:
        raise RuntimeError("POST /prompt %d %s" % (e.code, e.read().decode("utf-8", "replace")[:400]))


def upscale_clip(src, dst, timeout=1800):
    """Same contract as run_queue.upscale_clip: write the 2x clip to dst, return an info dict, raise on failure."""
    t0 = time.time()
    run, tag = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(src)))), os.path.basename(os.path.dirname(src))
    # t2571u: one fixed input name, overwritten by each upscale (the GPU lock serialises jobs), so AlienPc's ComfyUI
    # input folder holds at most one X3 clip; ComfyUI's API has no delete. VHS_LoadVideo keys its cache on path+mtime,
    # so an overwrite is always re-read.
    name = INPUT_NAME
    with open(src, "rb") as fh:   # rc.upload names the file after the local basename (clip.mp4); send our own name
        body, ct = rc._multipart({"subfolder": "", "type": "input", "overwrite": "true"}, name, fh.read())
    urllib.request.urlopen(urllib.request.Request(rc.API + "/upload/image", data=body, headers={"Content-Type": ct},
                                                  method="POST"), timeout=300).read()
    fps = _fps(src)
    pid = _post_prompt(graph(name, fps, "%s/%s_%s_2x" % (OUT_SUBDIR, run, tag)))
    deadline = t0 + timeout
    while True:
        if time.time() > deadline:
            raise RuntimeError("ComfyUI prompt %s not finished after %ds" % (pid, timeout))
        time.sleep(5)
        try:
            h = json.loads(urllib.request.urlopen("%s/history/%s" % (rc.API, pid), timeout=30).read())
        except Exception:
            continue
        if pid in h and (h[pid].get("status") or {}).get("completed") is not None:
            break
        if pid in h and (h[pid].get("status") or {}).get("status_str") in ("success", "error"):
            break
    st = h[pid].get("status") or {}
    files = [f for o in (h[pid].get("outputs") or {}).values() for k in ("gifs", "videos", "images") for f in o.get(k, [])
             if str(f.get("filename", "")).lower().endswith(".mp4")]
    if st.get("status_str") != "success" or not files:
        errs = [m for m in st.get("messages", []) if m and m[0] == "execution_error"]
        raise RuntimeError("ComfyUI prompt %s %s %s" % (pid, st.get("status_str"), json.dumps(errs)[:300]))
    f = ([x for x in files if x["filename"].endswith("-audio.mp4")] or files)[-1]   # VHS returns the muxed file last
    n = rc.download(f.get("subfolder", ""), f["filename"], dst)
    if n <= 0:
        raise RuntimeError("ComfyUI prompt %s output %s is empty" % (pid, f["filename"]))
    return {"prompt_id": pid, "comfy_output": "alienpc:output/%s/%s" % (f.get("subfolder", ""), f["filename"]),
            "comfy_input": "alienpc:input/" + name, "fps": fps, "bytes": n, "secs": round(time.time() - t0, 1),
            "graph": "VHS_LoadVideo -> RTXVideoSuperResolution(scale 2.0, ULTRA) -> VHS_VideoCombine(h264-mp4 crf16 yuv420p)"}


def enable(rq, upscale_done):
    """Put the real post-pass back (remote_comfy.enable set the D5 'deferred' stub) with the ComfyUI frame loop."""
    rq.upscale_clip = upscale_clip
    rq.DELETE_RAW_AFTER_UPSCALE = True   # t2571u: X3 renders keep only the upscaled clip
    rq.upscale_done = upscale_done
