"""verify_cell.py - audit one run cell against what I claimed in its note (v1, 2026-10-28).

Reads the graph, the objective sidecar, the mp4 sidecar and status.log, and checks every factual
claim made in notes/2026-10-28-terrace-dom-DONE.md: model, sampler, steps, shift, VSA, attention,
ref_image_size, canvas, length, fps, seed, cond, prompt identity (graph prompt == prompt_seg0.txt),
frames, duration, bytes, render seconds, contact sheet presence, and the QNAP size if given.
usage: python verify_cell.py <run_dir> [qnap_bytes|-] [frames]
Expected frames = the [frames] argument, else the request's c0.length (frames are set per run by the plan).
The seed / still / render-secs / single-pass checks are specific to the 2026-10-28 terrace_dom cell.
"""
import sys, os, json, hashlib, re

D = sys.argv[1]
qbytes = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "-" else None
tag = os.path.basename(D)
rows = []


def chk(name, ok, detail=""):
    rows.append((name, bool(ok), detail))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else "MISSING"


g = json.load(open(os.path.join(D, "request.api.json"), encoding="utf-8"))
i = lambda k, f: g[k]["inputs"].get(f)
F = int(sys.argv[3]) if len(sys.argv) > 3 else i("c0", "length")
mp4 = os.path.join(D, tag + ".mp4")
mp4j = json.load(open(mp4 + ".json", encoding="utf-8")) if os.path.exists(mp4 + ".json") else {}
obj = json.load(open(os.path.join(D, "objective.json"), encoding="utf-8")) if os.path.exists(os.path.join(D, "objective.json")) else {}
status = open(os.path.join(D, "status.log"), encoding="utf-8", errors="replace").read()
prompt_file = open(os.path.join(D, "prompt_seg0.txt"), encoding="utf-8").read().strip()

chk("model = beta7 int8HQ", i("unet", "unet_name") == "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors", i("unet", "unet_name"))
chk("euler/simple, 8 steps, denoise 1", i("ksel", "sampler_name") == "euler" and i("s0_sched", "scheduler") == "simple"
    and i("s0_sched", "steps") == 8 and i("s0_sched", "denoise") == 1.0,
    "%s/%s steps=%s" % (i("ksel", "sampler_name"), i("s0_sched", "scheduler"), i("s0_sched", "steps")))
chk("shift 12/3", i("m_shift", "shift_video") == 12.0 and i("m_shift", "shift_audio") == 3.0,
    "%s/%s" % (i("m_shift", "shift_video"), i("m_shift", "shift_audio")))
chk("VSA keep_percent 10 (90% sparsity)", i("m_vsa", "selection") == "vsa" and i("m_vsa", "selection.keep_percent") == 10,
    "%s/%s" % (i("m_vsa", "selection"), i("m_vsa", "selection.keep_percent")))
chk("comfy kitchen attention", i("m_attn", "attention") == "comfy kitchen attention", i("m_attn", "attention"))
chk("ref_image_size = max", i("c0", "ref_image_size") == "max", i("c0", "ref_image_size"))
chk("canvas 768x1344, length %s, fps 24" % F, (i("c0", "width"), i("c0", "height"), i("c0", "length")) == (768, 1344, F)
    and i("mkvid", "fps") == 24, "%sx%s len=%s fps=%s" % (i("c0", "width"), i("c0", "height"), i("c0", "length"), i("mkvid", "fps")))
chk("seed 51083002", i("noise", "noise_seed") == 51083002, i("noise", "noise_seed"))
chk("cond = TERRACE2 staged still", i("img", "image") == "community/TERRACE2_768x1344.png", i("img", "image"))
chk("graph prompt == prompt_seg0.txt", str(i("c0", "prompt")).strip() == prompt_file,
    "graph %d chars / file %d chars" % (len(str(i("c0", "prompt"))), len(prompt_file)))
chk("no loras / no upscale / no RIFE", not any(n["class_type"] in ("LoraLoaderModelOnly",) for n in g.values())
    and not any(t in n["class_type"] for n in g.values() for t in ("Upscal", "RIFE", "SLA", "Cache", "Spectrum")))
chk("single chunk (no continuation nodes)", not any(n["class_type"] in ("MiniMaxH3GuidedContinuationWindow",
    "MiniMaxH3AppendContinuation", "MiniMaxH3LatentTailGuide") for n in g.values()))
chk("mp4 exists, non-empty", os.path.exists(mp4) and os.path.getsize(mp4) > 0,
    os.path.getsize(mp4) if os.path.exists(mp4) else "missing")
a = (obj.get("attempts") or [{}])[-1] if isinstance(obj, dict) else {}
chk("objective: %s frames, 768x1344, 24 fps, audio, %s s, bytes = mp4" % (F, round(F / 24, 6)),
    a.get("frames") == F and a.get("w") == 768 and a.get("h") == 1344 and a.get("fps") == "24/1"
    and a.get("audio") is True and abs(float(a.get("duration", 0)) - F / 24) < 1e-3
    and os.path.exists(mp4) and a.get("bytes") == os.path.getsize(mp4),
    "frames=%s %sx%s fps=%s audio=%s dur=%s bytes=%s" % (a.get("frames"), a.get("w"), a.get("h"),
    a.get("fps"), a.get("audio"), a.get("duration"), a.get("bytes")))
chk("objective: no black/frozen frames flagged", isinstance(obj, dict) and ("blackfreeze" not in obj or obj["blackfreeze"] == []),
    "blackfreeze=%s" % (obj.get("blackfreeze") if isinstance(obj, dict) else "n/a"))
chk("mp4.json: 1 attempt, secs 360.2, comfy_output names the real render",
    mp4j.get("attempt") == 0 and mp4j.get("secs") == 360.2 and "terrace_dom_20261028_s51083002" in str(mp4j.get("comfy_output")),
    "attempt=%s secs=%s" % (mp4j.get("attempt"), mp4j.get("secs")))
m = re.search(r"JOB end \S+ ok secs=([\d.]+)", status)
chk("render secs = 360.2 in status.log", m and float(m.group(1)) == 360.2, m.group(1) if m else "no JOB end line")
chk("no re-queue / no error in status.log", "error" not in status.lower() and status.count("JOB start") == 1,
    "JOB start x%d" % status.count("JOB start"))
chk("contact sheet exists", os.path.exists(os.path.join(D, tag + "_stills_contact.png")))
if qbytes is not None:
    chk("QNAP copy size matches local", qbytes == os.path.getsize(mp4), "qnap=%d local=%d" % (qbytes, os.path.getsize(mp4)))

print("=== cell audit:", tag)
for n, ok, d in rows:
    print("  %-46s %s %s" % (n, "ok" if ok else "FAIL", d))
print("=== verdict:", "all checks pass" if all(r[1] for r in rows) else "%d FAIL" % sum(1 for r in rows if not r[1]))
print("prompt words=%d chars=%d  graph sha=%s  prompt sha=%s" %
      (len(prompt_file.split()), len(prompt_file), sha(os.path.join(D, "request.api.json")), sha(os.path.join(D, "prompt_seg0.txt"))))
for kws in ("face", "slap", "not into it", "flat", "unsmiling", "PRIMARY MOTION", "[Shot 1]", "reference generation"):
    print("  prompt contains %-22s %s" % (repr(kws), kws.lower() in prompt_file.lower()))
