"""ALI-163 FINAL objective check (CPU only, read-only + m4a ffprobe).

Per clip: result.json ok/rc, status.log JOB start / JOB end lines quoted with CT times,
count of 'JOB error' / 'CLIP_SKIP', ffprobe -count_packets (WxH, fps, nb_read_packets),
audio stream, the extracted <id>.m4a (bytes, sha256, codec, sr, ch, duration), mp4 bytes/sha256,
render secs, the overall_soundscape: line, refs (LoadImage strings) and seed.
Writes notes/ali163_hc_final_objective.json and prints a table. No writes under runs/.
"""
import csv
import hashlib
import json
import os
import re
import subprocess

FFPROBE = (
    "C:/Users/derek/AppData/Local/Microsoft/Winget/Packages/"
    "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin/ffprobe.exe"
)
RUNS = "C:/AI/community/runs"
JOBS = "C:/AI/community/p7/jobs"
OUT = "C:/AI/community/notes/ali163_hc_final_objective.json"

CLIPS = [
    # (label, id, pick, expected frames, note)
    ("clip1 OLD", "ali147_pool_hc_c1_s51100001", "HC1 BD004", 481, "old batch (481 f)"),
    ("clip2 OLD", "ali147_pool_hc_c2_s51100002", "HC2 BD007", 481, "old batch (481 f)"),
    ("clip1 NEW", "ali147_pool_hc_r1_s51130001", "HC1 BD004", 243, "R4"),
    ("clip2 NEW", "ali147_pool_hc_r2_s51130002", "HC2 BD007", 243, "R5"),
    ("clip3", "ali147_pool_hc_r3_s51130003", "HC3 GI173", 243, "R6"),
    ("clip4", "ali147_pool_hc_r4_s51130004", "HC4 GI107", 243, "R7"),
    ("clip5", "ali147_pool_hc_r5_s51130005", "HC5 GI150", 243, "R8"),
    ("clip6", "ali147_pool_hc_r6_s51130006", "HC6 BD076", 243, "R9"),
]


def sh(*args):
    r = subprocess.run(list(args), capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def probe_video(mp4):
    rc, out, err = sh(
        FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets",
        "-show_entries", "stream=nb_read_packets,r_frame_rate,width,height",
        "-of", "csv=p=0", mp4,
    )
    parts = out.split(",")
    return {"rc": rc, "w": parts[0], "h": parts[1], "fps": parts[2],
            "packets": parts[3], "err": err[:200]}


def probe_audio(f):
    rc, out, err = sh(
        FFPROBE, "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,sample_rate,channels:format=duration",
        "-of", "csv=p=0", f,
    )
    return {"rc": rc, "lines": [l for l in out.splitlines() if l], "err": err[:200]}


def audio_in_mp4(mp4):
    rc, out, err = sh(FFPROBE, "-v", "error", "-select_streams", "a:0",
                       "-show_entries", "stream=codec_name,channels,sample_rate",
                       "-of", "csv=p=0", mp4)
    return out


def sound_line(graph):
    """Return the longest 'overall_soundscape:' line found in any graph text input."""
    best = ""
    for node in graph.values():
        if not isinstance(node, dict):
            continue
        for val in node.get("inputs", {}).values():
            if not isinstance(val, str):
                continue
            for i, line in enumerate(val.splitlines()):
                s = line.strip()
                if not s.startswith("overall_soundscape:"):
                    continue
                body = s[len("overall_soundscape:"):].strip()
                j = i + 1
                while not body and j < len(val.splitlines()):
                    nxt = val.splitlines()[j].strip()
                    if not nxt:
                        break
                    body = (body + " " + nxt).strip()
                    j += 1
                cand = "overall_soundscape: " + body
                if len(cand) > len(best):
                    best = cand
    return best[:400]


rows = []
for label, cid, pick, exp_frames, note in CLIPS:
    d = os.path.join(RUNS, cid)
    res_p = os.path.join(JOBS, cid + ".result.json")
    row = {"label": label, "id": cid, "pick": pick, "note": note,
           "expected_frames": exp_frames}
    row["result_exists"] = os.path.exists(res_p)
    if row["result_exists"]:
        r = json.load(open(res_p, encoding="utf-8"))
        row.update({"ok": r.get("ok"), "rc": r.get("rc"), "started": r.get("started"),
                    "finished": r.get("finished"), "wall_min": r.get("wall_min"),
                    "note_rc": r.get("note"), "budget_used_min": r.get("budget_used_min")})
    # status.log quotes + error greps
    sl = os.path.join(d, "status.log")
    if os.path.exists(sl):
        lines = open(sl, encoding="utf-8").read().splitlines()
        row["job_start"] = [l for l in lines if "JOB start" in l]
        row["job_end"] = [l for l in lines if "JOB end" in l]
        row["objective_line"] = [l for l in lines if "OBJECTIVE" in l]
        row["job_error_grep"] = sum(1 for l in lines if "JOB error" in l)
        row["clip_skip_grep"] = sum(1 for l in lines if "CLIP_SKIP" in l)
        row["status_tail"] = lines[-6:]
    mp4 = os.path.join(d, cid + ".mp4")
    row["mp4"] = mp4
    row["mp4_exists"] = os.path.exists(mp4)
    if row["mp4_exists"]:
        row["mp4_bytes"] = os.path.getsize(mp4)
        row["mp4_sha256"] = sha256(mp4)
        row["video"] = probe_video(mp4)
        row["audio_stream"] = audio_in_mp4(mp4)
        mj = os.path.join(d, cid + ".mp4.json")
        if os.path.exists(mj):
            j = json.load(open(mj, encoding="utf-8"))
            row["render_secs"] = j.get("secs")
            row["finished_ct"] = j.get("finished")
            row["prompt_id"] = j.get("prompt_id")
        m4a = os.path.join(d, cid + ".m4a")
        row["m4a"] = m4a
        row["m4a_exists"] = os.path.exists(m4a)
        if row["m4a_exists"]:
            row["m4a_bytes"] = os.path.getsize(m4a)
            row["m4a_sha256"] = sha256(m4a)
            row["m4a_probe"] = probe_audio(m4a)
    # graph: seed, refs, sound line, frames
    gp = os.path.join(d, "request.api.json")
    if os.path.exists(gp):
        g = json.load(open(gp, encoding="utf-8"))
        row["seed"] = [v["inputs"].get("noise_seed") for v in g.values()
                       if isinstance(v, dict) and "noise_seed" in v.get("inputs", {})]
        row["refs"] = [v["inputs"].get("image") for v in g.values()
                       if isinstance(v, dict) and v.get("class_type") == "LoadImage"]
        row["soundscape"] = sound_line(g)
        row["width"] = [v["inputs"].get("width") for k, v in g.items()
                        if re.fullmatch(r"c[01]", k) and isinstance(v, dict)]
        row["height"] = [v["inputs"].get("height") for k, v in g.items()
                         if re.fullmatch(r"c[01]", k) and isinstance(v, dict)]
        row["ext_frames"] = [v["inputs"].get("extension_frames") for k, v in g.items()
                             if isinstance(v, dict) and "extension_frames" in v.get("inputs", {})]
    rows.append(row)

json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
print("WROTE", OUT)
hdr = ["id", "ok", "rc", "WxH", "fps", "packets", "exp", "aud", "m4a", "m4a_dur", "frames_s", "seed"]
print(" | ".join(hdr))
for r in rows:
    v = r.get("video", {})
    m4 = r.get("m4a_probe", {}).get("lines", [])
    dur = next((l.split(",")[-1] for l in m4 if l.startswith("format") or "," in l and not l.startswith("audio")), "")
    print(" | ".join([
        r["id"], str(r.get("ok")), str(r.get("rc")),
        f"{v.get('w')}x{v.get('h')}", str(v.get("fps")), str(v.get("packets")),
        str(r["expected_frames"]), str(r.get("audio_stream")),
        str(r.get("m4a_exists")), dur,
        str(r.get("render_secs")), str(r.get("seed")),
    ]))
print()
for r in rows:
    print(r["id"], "JOBERROR=", r.get("job_error_grep"), "CLIPSKIP=", r.get("clip_skip_grep"),
          "m4a_probe=", r.get("m4a_probe", {}).get("lines"),
          "soundscape=", (r.get("soundscape") or "")[:80])
