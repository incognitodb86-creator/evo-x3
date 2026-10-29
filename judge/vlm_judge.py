"""vlm_judge.py - absolute (not pairwise) per-check VLM judge for p15-style i2v clips.

Sends the existing qwen3vl_judge model (llama-swap OpenAI endpoint) the start image, the intended
prompt/target pose, and a 2x4 storyboard of 8 evenly spaced frames (last frame included). Asks one
yes/no question per failure type, forced to a JSON schema (llama.cpp response_format json_schema),
so the answer cannot be truncated. Technical defects only. Flags only; Derrick gives the only KEEP.
GPU etiquette: gpu_guard IDLE -> gpu_lock.ps1 -Acquire (waits while held) -> judge -> unload -> release.
Usage: .venv\\Scripts\\python.exe vlm_judge.py [--match p15v2_]
"""
import argparse, base64, io, json, os, subprocess, sys, time, urllib.request
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw

MANIFEST = Path(r"C:\Users\derek\5slock\ralph-community\notes\p15v2_manifest.json")
PROMPTS = Path(r"C:\Users\derek\5slock\ralph-community\notes\p15_prompts")
RUNS, INPUT = Path(r"C:\AI\community\runs"), Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input")
OUT = Path(__file__).parent / "out" / "vlm"
URL, MODEL = "http://127.0.0.1:8080", "qwen3vl_judge"
GUARD, LOCK = r"C:\AI\director\scripts\gpu_guard.ps1", r"C:\AI\director\scripts\gpu_lock.ps1"
POSES = {"gi102_missionary": "missionary position (one partner lying on their back, the other on top facing them)",
         "gi201_against_wall": "standing position against a wall"}
CHECKS = {  # key: (question, answer that is a defect)
    "same_scene": ("Is the location/background in the frames the same place as in the START IMAGE (no swap to a different room or setting)?", "no"),
    "same_people": ("Are the people in the frames the same characters as in the START IMAGE (same number, same body types, hair, skin tone, sex characteristics; nobody replaced or turned into someone else)?", "no"),
    "start_kept": ("Does frame 1 continue directly from the START IMAGE (same pose, framing, clothing/props), instead of jumping to a different pose or composition?", "no"),
    "target_reached": ("Look at Image 3 (the last frame, full size). Are the two bodies clearly in the TARGET POSE, in contact, with the act visibly happening? Answer no if they are separated, static in the start pose, or in a different pose.", "no"),
    "anatomy_defect": ("Is there any anatomy or fusion defect in any frame or in Image 3 (merged or melted bodies, extra or missing limbs, malformed genitals or hands, blob-like shapes)?", "yes"),
}
SCHEMA = {"type": "object", "additionalProperties": False, "required": list(CHECKS),
          "properties": {k: {"type": "object", "additionalProperties": False, "required": ["answer", "reason"],
                             "properties": {"answer": {"type": "string", "enum": ["yes", "no"]},
                                            "reason": {"type": "string", "maxLength": 200}}} for k in CHECKS}}

def ps(script, *args):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script, *args], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

def take_gpu():
    while True:
        rc, out = ps(GUARD)
        if rc == 0 and "IDLE" in out:
            rc, out = ps(LOCK, "-Acquire", "-Owner", str(os.getpid()), "-Note", "judge_vlm_p15v2")
            if rc == 0: print("[GPU_LOCK]", out); return
        print("[GPU busy, waiting 60 s]", out[:120], flush=True); time.sleep(60)

def release_gpu():
    try: urllib.request.urlopen(urllib.request.Request(f"{URL}/api/models/unload/{MODEL}"), timeout=60).read()
    except Exception: urllib.request.urlopen(f"{URL}/unload", timeout=60).read()
    print("[GPU_LOCK]", ps(LOCK, "-Release", "-Owner", str(os.getpid()))[1])

def b64(img, maxside=1024):
    img = img.copy(); img.thumbnail((maxside, maxside)); buf = io.BytesIO(); img.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def storyboard(mp4, k=8):
    cap = cv2.VideoCapture(str(mp4)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); tiles = []
    for i in np.linspace(0, n - 1, k).round().astype(int):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i)); ok, f = cap.read()
        if ok:
            t = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)); t.thumbnail((448, 448)); tiles.append(t)
    last = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)); cap.release(); w, h = tiles[0].size
    grid = Image.new("RGB", (w * 4, h * 2))
    for j, t in enumerate(tiles):
        grid.paste(t, ((j % 4) * w, (j // 4) * h))

    d = ImageDraw.Draw(grid)
    for j in range(len(tiles)): d.rectangle([(j % 4) * w, (j // 4) * h, (j % 4) * w + 34, (j // 4) * h + 22], fill="black"); d.text(((j % 4) * w + 6, (j // 4) * h + 4), str(j + 1), fill="white")
    return grid, last

def ask(job):
    tag = job["tag"]; start = Image.open(INPUT / job["guides"][0]["image"]).convert("RGB")
    grid, last = storyboard(RUNS / tag / f"{tag}.mp4")
    prompt_txt = (PROMPTS / job["prompt_file"]).read_text(encoding="utf-8", errors="replace")[:3000]
    q = "\n".join(f'- "{k}": {v[0]}' for k, v in CHECKS.items())
    text = ("You are a strict technical QA checker for AI-generated video of fictional adult characters. Judge only visible "
            "technical defects. Image 1 is the START IMAGE the clip must begin from. Image 2 is a storyboard of 8 frames from "
            "the clip in time order (numbered 1-8, row by row; frame 8 is the last frame). Image 3 is the last frame at full size.\n"
            f"TARGET POSE by the end: {POSES.get(job['pose'], job['pose'])}.\nINTENDED PROMPT (excerpt):\n{prompt_txt}\n\n"
            "For same_scene, same_people and start_kept compare ONLY with the START IMAGE; the prompt text can describe the "
            "people or setting wrongly, so ignore it for those three checks. Use the prompt only for target_reached.\n"
            f"Answer each check with yes or no and a short reason (max 25 words) citing frame numbers:\n{q}")
    body = {"model": MODEL, "temperature": 0.0, "max_tokens": 2048,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "clip_checks", "strict": True, "schema": SCHEMA}},
            "messages": [{"role": "user", "content": [{"type": "text", "text": text},
                         {"type": "image_url", "image_url": {"url": b64(start)}},
                         {"type": "image_url", "image_url": {"url": b64(grid, 1792)}},
                         {"type": "image_url", "image_url": {"url": b64(last)}}]}]}
    t0 = time.time()
    res = json.loads(urllib.request.urlopen(urllib.request.Request(f"{URL}/v1/chat/completions", json.dumps(body).encode(),
                     {"Content-Type": "application/json"}), timeout=900).read())
    ans = json.loads(res["choices"][0]["message"]["content"])
    flags = [k for k, (_, bad) in CHECKS.items() if ans[k]["answer"] == bad]
    return {"tag": tag, "secs": round(time.time() - t0, 1), "finish": res["choices"][0].get("finish_reason"),
            "answers": ans, "flags": flags}, grid

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--match", default="p15v2_"); a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [j for j in json.loads(MANIFEST.read_text())["jobs"] if a.match in j["tag"]]
    take_gpu(); t0 = time.time()
    try:
        for j in jobs:
            r, grid = ask(j); grid.save(OUT / f"{j['tag']}_grid.jpg", quality=85)
            (OUT / f"{j['tag']}.json").write_text(json.dumps(r, indent=1))
            print(j["tag"], r["secs"], r["flags"] or "ok", flush=True)
    finally:
        release_gpu(); print(f"[TOTAL under lock] {time.time() - t0:.0f} s")
