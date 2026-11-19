"""BQ1d objective check (CPU only, NO vision judge, NO ComfyUI port call, 0 GPU minutes).

Side-by-side A/B for the BQ1 rewire (ALI-184, Max's REWIRE 4:51 PM CT):
  CONTROL r3r ali147_pool_hc_r3r_s51130003 = face-crop refs only, the approved start still
            is NOT in the graph at all (the BQ1 body defect)
  BQ1b   r3b ali147_pool_hc_r3b_s51130003 = rewired: start still = ref_image_1 (body/scene,
            <Picture 1>) on c0 AND c1, the two face crops = face-only refs, no ImageToVideo

Per clip it reads: p7/jobs/<id>.result.json (ok/rc/wall/budget), runs/<id>/status.log
(JOB start / JOB end / OBJECTIVE quoted with CT times, 'JOB error' + 'CLIP_SKIP' counts),
the mp4 (ffprobe -count_packets -> WxH, fps, nb_read_packets; audio stream; bytes + sha256),
the demuxed <id>.m4a (bytes, sha256, codec/sr/ch/duration), and the graph (seed, the
ref_images.ref_image_N wiring read with fullmatch, ref_image_size, c0/c1 class_type,
c0/c1 width/height, c0 length + win1 extension_frames, SamplerCustomAdvanced count,
the overall_soundscape: line).

Writes notes/ali163_hc_bq1d_objective.json, prints a table + a gate block.
Checks 15-17 are a self-destruct probe: the r3r wiring is restored into a clone of the
r3b graph and the detectors MUST fire there and NOT on the real graph - a green check that
cannot fail is worthless (AGENTS.md). No writes under runs/.
"""
import collections
import hashlib
import json
import os
import re
import subprocess

BIN = ("C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/"
       "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin")
FFPROBE = BIN + "/ffprobe.exe"
FFMPEG = BIN + "/ffmpeg.exe"
RUNS = "C:/AI/community/runs"
JOBS = "C:/AI/community/p7/jobs"
OUT = "C:/AI/community/notes/ali163_hc_bq1d_objective.json"
PROBE_GRAPH = "C:/AI/community/notes/ali163_hc_bq1d_probe_graph.json"
EXP_FRAMES, EXP_W, EXP_H, EXP_FPS = 243, 1344, 768, "24/1"
EXP_SEED, EXP_C0_LEN, EXP_EXT = [51130003], 124, [119]
STILL = "community/hc/HC3_lesbian_beach.jpg"
CROPS = ("community/hc/HC3_w1_face.png", "community/hc/HC3_w2_face.png")
CLIPS = [
    ("CONTROL r3r (face crops only, start still NOT in the graph)",
     "ali147_pool_hc_r3r_s51130003", "HC3 GI173"),
    ("BQ1b r3b (start still = Picture 1 body/scene, crops = face-only refs)",
     "ali147_pool_hc_r3b_s51130003", "HC3 GI173"),
]


def sh(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def probe_video(mp4):
    rc, out, err = sh(FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
                      "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height",
                      "-of", "csv=p=0", mp4)
    p = out.split(",")
    return {"rc": rc, "w": p[0], "h": p[1], "fps": p[2], "packets": p[3], "err": err[:200]}


def probe_streams(f):
    rc, out, err = sh(FFPROBE, "-v", "error", "-show_entries",
                      "stream=codec_type,codec_name,sample_rate,channels:format=duration",
                      "-of", "csv=p=0", f)
    return {"rc": rc, "lines": [l for l in out.splitlines() if l], "err": err[:200]}


def audio_lines(probe):
    """ffprobe csv=p=0 prints codec_name BEFORE codec_type, so an audio stream line is
    'aac,audio,32000,2': match on ',audio' (startswith('audio') was the tool bug here)."""
    return [l for l in probe.get("lines", []) if ",audio" in l]


def ref_slots(graph):
    """node id -> {class_type, primary, slots:[{slot, node, image}]} for ref_images.ref_image_N."""
    out = {}
    for nid, n in sorted(graph.items()):
        if not isinstance(n, dict):
            continue
        ins = n.get("inputs", {})
        keys = [k for k in ins if re.fullmatch(r"ref_images\.ref_image_\d+", k)]
        if not keys:
            continue
        slots = []
        for k in sorted(keys, key=lambda s: int(re.search(r"(\d+)$", s).group(1))):
            v = ins[k]
            src = v[0] if isinstance(v, list) else None
            slots.append({"slot": k, "node": src,
                          "image": (graph.get(src, {}).get("inputs", {}) or {}).get("image")})
        prim = ins.get("image")
        out[nid] = {"class_type": n.get("class_type"), "slots": slots,
                    "primary": prim if isinstance(prim, str) else None,
                    "ref_image_size": ins.get("ref_image_size")}
    return out


def sound_line(graph):
    best = ""
    for n in graph.values():
        if not isinstance(n, dict):
            continue
        for val in n.get("inputs", {}).values():
            if not isinstance(val, str):
                continue
            lines = val.splitlines()
            for i, line in enumerate(lines):
                s = line.strip()
                if not s.startswith("overall_soundscape:"):
                    continue
                body = s[len("overall_soundscape:"):].strip()
                j = i + 1
                while not body and j < len(lines):
                    nxt = lines[j].strip()
                    if not nxt:
                        break
                    body = (body + " " + nxt).strip()
                    j += 1
                cand = "overall_soundscape: " + body
                if len(cand) > len(best):
                    best = cand
    return best[:400]


def static_defects(graph):
    """Offline clone of run_graph_job.static_check (the r3 rc=2 class): audio_vae on an
    ImageToVideo (only ReferenceToVideo has it), and a ref slot pointing at a missing node."""
    d = []
    for nid, n in graph.items():
        if not isinstance(n, dict):
            continue
        ct = n.get("class_type", "")
        ins = n.get("inputs", {})
        if ct.endswith("ImageToVideo") and not ct.endswith("ReferenceToVideo") \
                and "audio_vae" in ins:
            d.append(f"{nid} {ct} carries audio_vae (STATIC_FAIL rc=2 class, r3 2026-10-23 14:15 CT)")
        for k, v in ins.items():
            if isinstance(v, list) and v and isinstance(v[0], str) and v[0] not in graph:
                d.append(f"{nid}.{k} -> missing node {v[0]}")
    for nid, n in graph.items():
        if not isinstance(n, dict):
            continue
        for k, v in n.get("inputs", {}).items():
            if isinstance(v, list) and v and isinstance(v[0], str) and v[0] not in graph:
                d.append(f"{nid}.{k} -> dangling node id {v[0]}")
    return sorted(set(d))


rows = []
for label, cid, pick in CLIPS:
    d = os.path.join(RUNS, cid)
    gp = os.path.join(d, "request.api.json")
    g = json.load(open(gp, encoding="utf-8"))
    row = {"label": label, "id": cid, "pick": pick, "expected_frames": EXP_FRAMES}
    r = json.load(open(os.path.join(JOBS, cid + ".result.json"), encoding="utf-8"))
    row.update({k: r.get(k) for k in ("ok", "rc", "started", "finished", "wall_min", "note",
                                      "budget_used_min", "budget_cap_min")})
    lines = open(os.path.join(d, "status.log"), encoding="utf-8").read().splitlines()
    row["job_start"] = [l for l in lines if "JOB start" in l]
    row["job_end"] = [l for l in lines if "JOB end" in l]
    row["objective_line"] = [l for l in lines if "OBJECTIVE" in l]
    row["job_error_grep"] = sum(1 for l in lines if "JOB error" in l)
    row["clip_skip_grep"] = sum(1 for l in lines if "CLIP_SKIP" in l)
    mp4 = os.path.join(d, cid + ".mp4")
    row["mp4"], row["mp4_exists"] = mp4, os.path.exists(mp4)
    row["mp4_bytes"], row["mp4_sha256"] = os.path.getsize(mp4), sha256(mp4)
    row["video"] = probe_video(mp4)
    row["mp4_streams"] = probe_streams(mp4)
    m4a = os.path.join(d, cid + ".m4a")
    row["m4a"] = m4a
    if not os.path.exists(m4a):
        sh(FFMPEG, "-y", "-loglevel", "error", "-i", mp4, "-vn", "-c:a", "copy", m4a)
    row["m4a_exists"] = os.path.exists(m4a)
    if row["m4a_exists"]:
        row["m4a_bytes"], row["m4a_sha256"] = os.path.getsize(m4a), sha256(m4a)
        row["m4a_probe"] = probe_streams(m4a)
    row["graph_bytes"], row["graph_sha256"] = os.path.getsize(gp), sha256(gp)
    row["seed"] = sorted({v["inputs"].get("noise_seed") for v in g.values()
                          if isinstance(v, dict) and "noise_seed" in v.get("inputs", {})})
    row["ref_slots"] = ref_slots(g)
    row["loadimage"] = sorted({v["inputs"]["image"] for v in g.values()
                               if isinstance(v, dict) and v.get("class_type") == "LoadImage"
                               and isinstance(v["inputs"].get("image"), str)})
    row["c_class"] = {k: g[k]["class_type"] for k in sorted(g) if re.fullmatch(r"c[01]", k)}
    row["wh"] = {k: [g[k]["inputs"].get("width"), g[k]["inputs"].get("height")]
                 for k in sorted(g) if re.fullmatch(r"c[01]", k)}
    row["c0_length"] = g["c0"]["inputs"].get("length")
    row["ext_frames"] = sorted({v["inputs"].get("extension_frames") for v in g.values()
                                if isinstance(v, dict)
                                and v["inputs"].get("extension_frames") is not None})
    row["sampler_custom_advanced"] = sum(1 for v in g.values()
                                         if isinstance(v, dict)
                                         and v.get("class_type") == "SamplerCustomAdvanced")
    row["sampler_name"] = [v["inputs"].get("sampler_name") for v in g.values()
                           if isinstance(v, dict) and v.get("class_type") == "KSamplerSelect"]
    row["shift"] = {v["inputs"].get("shift_video"): v["inputs"].get("shift_audio")
                    for v in g.values() if isinstance(v, dict)
                    and v.get("class_type") == "MiniMaxH3SigmaShift"}
    row["steps"] = sorted({v["inputs"].get("steps") for v in g.values()
                           if isinstance(v, dict) and "steps" in v.get("inputs", {})
                           and v["inputs"].get("steps") is not None})
    row["soundscape"] = sound_line(g)
    row["static_defects"] = static_defects(g)
    row["node_count"] = len(g)
    row["class_counts"] = dict(collections.Counter(
        v.get("class_type") for v in g.values() if isinstance(v, dict)))
    rows.append(row)

json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
print("WROTE", OUT, os.path.getsize(OUT), "bytes")

# ---------------------------------------------------------------- gate block
gates = []


def gate(name, cond, detail=""):
    gates.append((name, bool(cond), detail))


by = {r["id"]: r for r in rows}
r3r = by["ali147_pool_hc_r3r_s51130003"]
r3b = by["ali147_pool_hc_r3b_s51130003"]
for r in rows:
    v, tag = r["video"], r["id"].split("_")[3]
    aud = audio_lines(r["mp4_streams"])
    m4aud = audio_lines(r.get("m4a_probe", {}))
    gate(f"{tag} result.json ok=True rc=0 (no redo)", r["ok"] is True and r["rc"] == 0,
         f"ok={r['ok']} rc={r['rc']} wall={r['wall_min']}m budget_after={r['budget_used_min']}")
    gate(f"{tag} status.log exactly 1 JOB start + 1 JOB end ok, 0 JOB error, 0 CLIP_SKIP",
         len(r["job_start"]) == 1 and len(r["job_end"]) == 1 and " ok " in r["job_end"][0]
         and r["job_error_grep"] == 0 and r["clip_skip_grep"] == 0,
         f"start={len(r['job_start'])} end={len(r['job_end'])} "
         f"JOBERROR={r['job_error_grep']} CLIPSKIP={r['clip_skip_grep']}")
    gate(f"{tag} ffprobe 1344x768 24/1 fps 243 packets (10.125 s)",
         (v["w"], v["h"], v["fps"], v["packets"]) ==
         (str(EXP_W), str(EXP_H), EXP_FPS, str(EXP_FRAMES)),
         f"{v['w']}x{v['h']} {v['fps']} packets={v['packets']}")
    gate(f"{tag} audio stream in the mp4 + demuxed m4a probes as audio (audio is part of the test)",
         len(aud) >= 1 and r["m4a_exists"] and r["m4a_bytes"] > 1000 and len(m4aud) >= 1,
         f"mp4={aud} m4a={r.get('m4a_bytes')}B {m4aud}")
    gate(f"{tag} graph: 1344x768 on c0+c1, seed {EXP_SEED}, 124+119 f, euler, 10 steps, "
         f"shift 10/3, 2 SamplerCustomAdvanced (single pass)",
         all(x == [EXP_W, EXP_H] for x in r["wh"].values()) and r["seed"] == EXP_SEED
         and r["c0_length"] == EXP_C0_LEN and r["ext_frames"] == EXP_EXT
         and r["sampler_name"] == ["euler"] and r["steps"] == [10]
         and list(r["shift"].items()) == [(10.0, 3.0)] and r["sampler_custom_advanced"] == 2,
         f"wh={r['wh']} seed={r['seed']} len={r['c0_length']} ext={r['ext_frames']} "
         f"{r['sampler_name']} steps={r['steps']} shift={r['shift']} SCA={r['sampler_custom_advanced']}")
    gate(f"{tag} overall_soundscape: line present in a prompt",
         r["soundscape"].startswith("overall_soundscape:"), r["soundscape"][:60])
    gate(f"{tag} offline static_check clean (no audio_vae on an ImageToVideo, no dangling link)",
         not r["static_defects"], "; ".join(r["static_defects"])[:120])

# ---- the BQ1 rewire itself, as detectors ---------------------------------
def slot_images(r):
    return {nid: [s["image"] for s in n["slots"]] for nid, n in r["ref_slots"].items()}


gate("r3b: the approved start still is ref_image_1 on c0 AND c1 (Max's REWIRE)",
     {"c0", "c1"} <= set(r3b["ref_slots"])
     and all(n["slots"][0]["image"] == STILL for n in r3b["ref_slots"].values()),
     str(slot_images(r3b)))
gate("r3b: the two face crops stay face-only refs (ref_image_2/3, ref_image_size=match)",
     all({s["image"] for s in n["slots"][1:]} == set(CROPS) and n["ref_image_size"] == "match"
         for n in r3b["ref_slots"].values()),
     str(slot_images(r3b)) + " sizes=" + str({n["ref_image_size"] for n in r3b["ref_slots"].values()}))
gate("r3b: c0 AND c1 are MiniMaxH3ReferenceToVideo (3 ref slots each)",
     set(r3b["c_class"].values()) == {"MiniMaxH3ReferenceToVideo"}
     and all(len(n["slots"]) == 3 for n in r3b["ref_slots"].values()),
     f"{r3b['c_class']} slots={[len(n['slots']) for n in r3b['ref_slots'].values()]}")
gate("CONTROL r3r: the start still is NOT in the graph at all (the BQ1 body defect, proved)",
     STILL not in r3r["loadimage"]
     and STILL not in [x for v in slot_images(r3r).values() for x in v],
     f"loadimage={r3r['loadimage']} slots={slot_images(r3r)}")
gate("A/B fairness: same seed 51130003, same pick HC3, same 124+119 f, same 1344x768, "
     "one variable = the ref wiring",
     r3r["seed"] == r3b["seed"] == EXP_SEED and r3r["pick"] == r3b["pick"]
     and r3r["c0_length"] == r3b["c0_length"] and r3r["ext_frames"] == r3b["ext_frames"]
     and r3r["wh"] == r3b["wh"] and r3r["mp4_sha256"] != r3b["mp4_sha256"]
     and r3r["graph_sha256"] != r3b["graph_sha256"])

# ---- self-destruct probe (checks 15-17): restore the r3r wiring in an r3b clone
clone = json.loads(json.dumps(json.load(open(os.path.join(RUNS, r3b["id"],
                                                           "request.api.json"), encoding="utf-8"))))
clone["c0"]["inputs"]["ref_images.ref_image_1"] = ["img2", 0]
clone["c0"]["inputs"]["ref_images.ref_image_2"] = ["img3", 0]
clone["c0"]["inputs"].pop("ref_images.ref_image_3", None)
clone["c1"]["class_type"] = "MiniMaxH3ImageToVideo"   # keeps audio_vae = the r3 rc=2 defect
for k in list(clone["c1"]["inputs"]):
    if k.startswith("ref_images."):
        clone["c1"]["inputs"].pop(k)
del clone["img"]
clone["c0"]["inputs"]["ref_images.ref_image_3"] = ["img", 0]   # dangling id on purpose
json.dump(clone, open(PROBE_GRAPH, "w", encoding="utf-8"))
pr = {"ref_slots": ref_slots(clone),
      "loadimage": sorted({v["inputs"]["image"] for v in clone.values()
                           if isinstance(v, dict) and v.get("class_type") == "LoadImage"}),
      "static_defects": static_defects(clone)}
pr_slot_imgs = [x["image"] for n in pr["ref_slots"].values() for x in n["slots"]]
gate("SELF-DESTRUCT 15: r3r wiring restored in a clone -> the start-still detector FIRES there",
     STILL not in pr["loadimage"] and STILL not in pr_slot_imgs,
     f"probe_loadimage={pr['loadimage']}")
gate("SELF-DESTRUCT 16: the SAME detector does NOT fire on the real r3b graph",
     STILL in r3b["loadimage"] and all(n["slots"][0]["image"] == STILL
                                       for n in r3b["ref_slots"].values()))
gate("SELF-DESTRUCT 17: audio_vae-on-ImageToVideo + dangling-link detectors fire on the clone "
     "and are silent on both real graphs",
     len(pr["static_defects"]) >= 2 and not r3b["static_defects"] and not r3r["static_defects"],
     "probe=" + "; ".join(pr["static_defects"])[:180])
os.remove(PROBE_GRAPH)

print()
print("id | ok | rc | WxH | fps | packets | audio | m4aB | seed | steps/shift | wall_min | graph_sha8")
for r in rows:
    v = r["video"]
    print(" | ".join([r["id"], str(r["ok"]), str(r["rc"]), f"{v['w']}x{v['h']}", v["fps"],
                      v["packets"],
                      ";".join(audio_lines(r["mp4_streams"])),
                      str(r.get("m4a_bytes")), str(r["seed"]),
                      f"{r['steps']}/{list(r['shift'].items())}", str(r["wall_min"]),
                      r["graph_sha256"][:8]]))
print()
for r in rows:
    print(r["id"], "nodes=", r["node_count"], "mp4_sha8=", r["mp4_sha256"][:8],
          "m4a_sha8=", str(r.get("m4a_sha256"))[:8])
    for line in r["job_start"] + r["job_end"] + r["objective_line"]:
        print("   ", line[:150])
    for nid, n in sorted(r["ref_slots"].items()):
        print("    REF", nid, n["class_type"], "size=", n["ref_image_size"],
              [(s["slot"], s["image"]) for s in n["slots"]])
    print("    SOUNDScape:", r["soundscape"][:120])
print()
bad = [g for g in gates if not g[1]]
for name, ok_, detail in gates:
    print(("PASS " if ok_ else "FAIL ") + name + ("  [" + detail + "]" if detail else ""))
print()
print("GATES", len(gates) - len(bad), "/", len(gates),
      "ALL CHECKS PASS" if not bad else "CHECKS FAILED: " + "; ".join(g[0] for g in bad))
raise SystemExit(0 if not bad else 1)
