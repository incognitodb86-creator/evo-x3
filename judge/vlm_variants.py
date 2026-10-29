"""vlm_variants.py - audit2 experiment (2026-10-29): persona / persona+rubric / worst-frame zoom variants of vlm_judge.
Same model, inputs and schema as vlm_judge.py; flags only, never KEEPs. Rubric written once from generic defect
definitions before any variant was scored (not tuned on p15v2). Usage: vlm_variants.py --variants A,B,C,Z [--match p15v2_]
"""
import argparse, json, os, sys, time
from pathlib import Path
import cv2, numpy as np
from PIL import Image
import vlm_judge as vj

PERSONA = ("You are a senior video QA reviewer at a VFX studio. You review AI-generated clips of fictional adult "
           "characters for technical defects only, never for taste or content. You are skeptical: a clip passes a check only "
           "if the frames clearly support it. You compare every frame against the reference START IMAGE, look at hands, "
           "limbs, contact areas and background edges up close, and you report a defect whenever you see one, even a brief one.")
RUBRIC = """DEFECT RUBRIC (what each failure looks like):
- anatomy_defect: limbs or bodies melting together, a shapeless flesh blob where body parts should be, extra or missing arms/legs/hands/feet, limbs detaching or floating, malformed hands or genitals. FAIL example: "frame 6: her left arm sinks into his shoulder and a third hand appears". PASS example: "all frames show two separate bodies with four arms and four legs, hands intact".
- same_scene: the room or setting changes from the START IMAGE: different walls, furniture, lighting, or new objects appearing in the background. FAIL example: "from frame 4 the plain wall behind them has become a window with curtains". PASS example: "same bed, wall and lamp in every frame".
- start_kept: frame 1 does not continue the START IMAGE: a different pose, camera framing or outfit from the first frame, or a hard cut early on. FAIL example: "frame 1 already shows a different pose and camera angle than the start image". PASS example: "frame 1 matches the start pose and framing, then motion begins".
- target_reached: motion stalls: bodies stay frozen in the start pose, drift apart, or end in a different pose than the target. FAIL example: "frames 1-8 look nearly identical; the start pose is never left". PASS example: "by frame 8 the bodies are in the target pose and in contact".
- same_people: identity or outfit drift: a character changes sex, face, body type or skin tone, or clothing appears/disappears. FAIL example: "from frame 5 the man has long hair and breasts". PASS example: "both characters keep the same face, build and clothing state throughout"."""

def ask_variant(job, variant):
    tag = job["tag"]; start = Image.open(vj.INPUT / job["guides"][0]["image"]).convert("RGB")
    grid, last = vj.storyboard(vj.RUNS / tag / f"{tag}.mp4")
    prompt_txt = (vj.PROMPTS / job["prompt_file"]).read_text(encoding="utf-8", errors="replace")[:3000]
    q = "\n".join(f'- "{k}": {v[0]}' for k, v in vj.CHECKS.items())
    text = ("You are a strict technical QA checker for AI-generated video of fictional adult characters. Judge only visible "
            "technical defects. Image 1 is the START IMAGE the clip must begin from. Image 2 is a storyboard of 8 frames from "
            "the clip in time order (numbered 1-8, row by row; frame 8 is the last frame). Image 3 is the last frame at full size.\n"
            f"TARGET POSE by the end: {vj.POSES.get(job['pose'], job['pose'])}.\nINTENDED PROMPT (excerpt):\n{prompt_txt}\n\n"
            "For same_scene, same_people and start_kept compare ONLY with the START IMAGE; the prompt text can describe the "
            "people or setting wrongly, so ignore it for those three checks. Use the prompt only for target_reached.\n"
            + (RUBRIC + "\n\n" if variant == "C" else "") +
            f"Answer each check with yes or no and a short reason (max 25 words) citing frame numbers:\n{q}")
    content = [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": vj.b64(start)}},
               {"type": "image_url", "image_url": {"url": vj.b64(grid, 1792)}}, {"type": "image_url", "image_url": {"url": vj.b64(last)}}]
    msgs = ([{"role": "system", "content": PERSONA}] if variant in ("B", "C") else []) + [{"role": "user", "content": content}]
    return post(msgs, vj.SCHEMA)

def worst_frames(mp4, k=2):
    """CPU temporal differencing: indices of the k frames with the largest change vs the previous frame (64px gray)."""
    cap = cv2.VideoCapture(str(mp4)); prev, d, i = None, [], 0
    while True:
        ok, f = cap.read()
        if not ok: break
        g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (64, 36)).astype(np.float32)
        d.append(0.0 if prev is None else float(np.abs(g - prev).mean())); prev = g; i += 1
    cap.release(); d = np.array(d); d[:3] = 0  # ignore the first frames
    idx = []
    for j in np.argsort(-d):
        if all(abs(j - x) > 24 for x in idx): idx.append(int(j))
        if len(idx) == k: break
    return sorted(idx), [round(float(d[x]), 2) for x in sorted(idx)]

def read_frame(mp4, i):
    cap = cv2.VideoCapture(str(mp4)); cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read(); cap.release()
    if not ok: raise RuntimeError(f"frame {i} not decoded from {mp4}")
    return Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))

ZCHECKS = {"same_scene": ("Is the background/location in Image 2 the same place as in Image 1 (same walls, furniture, lighting; no new objects or structures)?", "no"),
           "anatomy_defect": ("In Image 2, is any body malformed: limbs or bodies melted together, a shapeless flesh blob, extra or missing limbs, detached or floating parts, malformed hands or genitals?", "yes")}
ZSCHEMA = {"type": "object", "additionalProperties": False, "required": list(ZCHECKS),
           "properties": {k: vj.SCHEMA["properties"]["same_scene"] for k in ZCHECKS}}

def ask_zoom(job, wf=None):
    """Reference-anchored, worst-frame zoom: start image vs each of the 2 most-changed frames, full size."""
    tag = job["tag"]; mp4 = vj.RUNS / tag / f"{tag}.mp4"; start = Image.open(vj.INPUT / job["guides"][0]["image"]).convert("RGB")
    idx, diffs = wf or worst_frames(mp4); res = []
    for i in idx:
        text = ("Technical QA of an AI-generated video frame of fictional adult characters. Image 1 is the START IMAGE (reference). "
                f"Image 2 is frame {i} of the clip, the moment with the biggest visual change. Compare Image 2 against Image 1 region by "
                "region (background left/right/top, each person's head, arms, hands, legs, contact area). Answer each check yes or no "
                "with a short reason (max 25 words):\n" + "\n".join(f'- "{k}": {v[0]}' for k, v in ZCHECKS.items()))
        msgs = [{"role": "user", "content": [{"type": "text", "text": text}, {"type": "image_url", "image_url": {"url": vj.b64(start)}},
                                             {"type": "image_url", "image_url": {"url": vj.b64(read_frame(mp4, i), 1344)}}]}]
        ans, probs, fin = post(msgs, ZSCHEMA, ZCHECKS); res.append({"frame": i, "answers": ans, "p_defect": probs, "finish": fin})
    return {"frames": idx, "diffs": diffs, "per_frame": res}

def post(msgs, schema, checks=None):
    body = {"model": vj.MODEL, "temperature": 0.0, "seed": 42, "max_tokens": 2048, "logprobs": True, "top_logprobs": 10,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_schema", "json_schema": {"name": "clip_checks", "strict": True, "schema": schema}},
            "messages": msgs}
    import urllib.request
    res = json.loads(urllib.request.urlopen(urllib.request.Request(f"{vj.URL}/v1/chat/completions", json.dumps(body).encode(),
                     {"Content-Type": "application/json"}), timeout=900).read())
    ans = json.loads(res["choices"][0]["message"]["content"])
    saved = vj.CHECKS
    if checks: vj.CHECKS = checks
    try: probs = vj.answer_probs(res, ans)
    finally: vj.CHECKS = saved
    return ans, probs, res["choices"][0].get("finish_reason")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--match", default="p15v2_"); ap.add_argument("--variants", default="A,B,C,Z")
    a = ap.parse_args(); base = Path(__file__).parent / "out" / "audit2"
    jobs = [j for j in json.loads(vj.MANIFEST.read_text())["jobs"] if a.match in j["tag"]]
    wf = {j['tag']: worst_frames(vj.RUNS / j['tag'] / f"{j['tag']}.mp4") for j in jobs} if 'Z' in a.variants else {}  # CPU, before the lock
    vj.take_gpu(); t0 = time.time()
    try:
        for v in a.variants.split(","):
            od = base / v; od.mkdir(parents=True, exist_ok=True); tv = time.time()
            for j in jobs:
                try:
                    if v == "Z": r = ask_zoom(j, wf[j["tag"]])
                    else:
                        ans, probs, fin = ask_variant(j, v)
                        r = {"answers": ans, "p_defect": probs, "finish": fin,
                             "flags": [k for k, (_, bad) in vj.CHECKS.items() if ans[k]["answer"] == bad]}
                except Exception as e:
                    r = {"error": repr(e)[:300]}
                r["tag"] = j["tag"]; (od / f"{j['tag']}.json").write_text(json.dumps(r, indent=1))
                print(v, j["tag"], r.get("flags", r.get("error", "zoom")), flush=True)
            print(f"[variant {v}] {time.time() - tv:.0f} s", flush=True)
    finally:
        vj.release_gpu(); print(f"[TOTAL under lock] {time.time() - t0:.0f} s")
