
"""Objective QA of rendered packs, concat to one landscape MP4, write a facts json. No prompt text."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

RUN = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\run")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\reavideo_val_30s.mp4")

def ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])
    return json.loads(r.stdout)

def video_audio_info(path: Path) -> dict:
    data = ffprobe(path)
    v = next(s for s in data["streams"] if s.get("codec_type") == "video")
    astreams = [s for s in data["streams"] if s.get("codec_type") == "audio"]
    dur = float(v.get("duration") or data.get("format", {}).get("duration") or 0)
    fps_txt = v.get("avg_frame_rate") or v.get("r_frame_rate") or "0/1"
    num, den = fps_txt.split("/") if "/" in fps_txt else (fps_txt, "1")
    fps = float(num) / float(den or 1)
    w, h = int(v["width"]), int(v["height"])
    # black/freeze detect over first 2s and whole clip
    black = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-vf", "blackdetect=d=0.4:pic_th=0.98", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    black_hits = [line for line in (black.stderr or "").splitlines() if "black_start" in line]
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "width": w,
        "height": h,
        "landscape": w > h,
        "fps": round(fps, 3),
        "duration_s": round(dur, 3),
        "video_codec": v.get("codec_name"),
        "audio_streams": len(astreams),
        "audio_codec": astreams[0].get("codec_name") if astreams else None,
        "black_detect_hits": len(black_hits),
        "ok_canvas": (w, h) == (1344, 768),
        "ok_fps": abs(fps - 24) < 0.1,
        "ok_audio": len(astreams) >= 1,
        "ok_size": path.stat().st_size > 10000,
    }

# find pack mp4s
order = json.loads((RUN / "_render_order.json").read_text(encoding="utf-8"))
clips = []
for job in order["order"]:
    tag = job["tag"]
    # common locations
    cands = [
        RUN / tag / f"{tag}.mp4",
        RUN / tag / "clip.mp4",
    ]
    found = next((p for p in cands if p.is_file()), None)
    if found is None:
        # search
        hits = list((RUN / tag).glob("*.mp4")) if (RUN / tag).is_dir() else []
        found = hits[0] if hits else None
    if found is None:
        raise SystemExit(f"MISSING_MP4 {tag}")
    info = video_audio_info(found)
    info["tag"] = tag
    clips.append(info)

# concat
OUT.parent.mkdir(parents=True, exist_ok=True)
lst = OUT.with_suffix(".concat.txt")
lst.write_text("".join(f"file '{c['path'].replace(chr(92), '/')}'\n" for c in clips), encoding="utf-8")
# re-encode if codecs differ, else stream copy. Use concat demuxer + copy first.
r = subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(OUT)],
    capture_output=True, text=True,
)
if r.returncode != 0:
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", str(OUT)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("CONCAT_FAIL", r.stderr[-500:])
        raise SystemExit(2)

final = video_audio_info(OUT)
facts = {
    "clips": clips,
    "concat": final,
    "pass": all([
        final["ok_canvas"], final["landscape"], final["ok_fps"], final["ok_audio"],
        final["ok_size"], final["black_detect_hits"] == 0,
        25.0 <= final["duration_s"] <= 35.0,
        all(c["ok_canvas"] and c["ok_audio"] and c["ok_size"] and c["landscape"] for c in clips),
    ]),
}
(OUT.parent / "qa_facts.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
print(json.dumps(facts, indent=2))
if not facts["pass"]:
    raise SystemExit(3)
