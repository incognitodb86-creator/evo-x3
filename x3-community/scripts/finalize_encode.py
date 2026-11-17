#!/usr/bin/env python3
"""finalize_encode.py - the second half of the A/B/C post step: crf-18 encode + the deliverable names.

Spec: C:/AI/community/notes/ab_q4_q5_brief_2026-10-28.md:
  raw render untouched as *_raw.mp4; RTX 1.2x ULTRA; then ffmpeg -c:v libx264 -preset slow -crf 18 -c:a copy
  as *_final.mp4. If RTX fails, deliver the crf-18 encode of the RAW and say so.
The ffmpeg build the box already uses for frame work is the winget Gyan.FFmpeg 8.0.1 bin
(the path p6_review.py used); a runtime ffmpeg path does not exist on this box. Every resolved path is
reported by the probe output so the record shows which binary ran.
ffprobe reports the delivered files (size, bitrate, frames, audio) so the message to Derek carries numbers.

Usage: finalize_encode.py <run_dir> <arm_tag> [rtx_out.mp4]
"""
import json
import os
import subprocess
import sys

import shutil
_FFD = r"C:\Users\derek\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
FF = (os.path.join(_FFD, "ffmpeg.exe") if os.path.exists(os.path.join(_FFD, "ffmpeg.exe"))
      else shutil.which("ffmpeg") or "ffmpeg")
FP = (os.path.join(_FFD, "ffprobe.exe") if os.path.exists(os.path.join(_FFD, "ffprobe.exe"))
      else shutil.which("ffprobe") or "ffprobe")
C_OUT = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output"
RUN, TAG = sys.argv[1], sys.argv[2]
RTX = sys.argv[3] if len(sys.argv) > 3 else ""


def probe(p):
    o = subprocess.run([FP, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", p],
                       capture_output=True, text=True).stdout
    d = json.loads(o)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), {})
    return {"bytes": os.path.getsize(p), "dur": float(d["format"].get("duration", 0)),
            "kbps": float(d["format"].get("bit_rate", 0)) / 1000,
            "wh": f'{v.get("width")}x{v.get("height")}', "fps": v.get("r_frame_rate"),
            "nb_frames": v.get("nb_frames"), "vcodec": v.get("codec_name"),
            "acodec": a.get("codec_name"), "apresent": bool(a)}


def encode(src, dst):
    r = subprocess.run([FF, "-y", "-v", "error", "-stats", "-i", src, "-c:v", "libx264", "-preset", "slow",
                        "-crf", "18", "-c:a", "copy", dst], capture_output=True, text=True)
    print(f"ffmpeg rc={r.returncode} {os.path.basename(dst)}")
    if r.returncode:
        print(r.stdout[-800:], r.stderr[-800:])
    return r.returncode == 0


raw = os.path.join(RUN, f"{TAG}.mp4")
assert os.path.exists(raw), raw
if os.path.abspath(raw) != os.path.abspath(os.path.join(RUN, f"{TAG}_raw.mp4")):
    import shutil
    shutil.copy2(raw, os.path.join(RUN, f"{TAG}_raw.mp4"))

rtx_ok = bool(RTX) and os.path.exists(RTX)
if rtx_ok:
    import shutil
    shutil.copy2(RTX, os.path.join(RUN, f"{TAG}_rtx12.mp4"))
    enc = encode(os.path.join(RUN, f"{TAG}_rtx12.mp4"), os.path.join(RUN, f"{TAG}_final.mp4"))
    delivered = f"{TAG}_final.mp4 via RTX 1.2x ULTRA + libx264 slow crf 18" if enc else ""
if not rtx_ok or not enc:
    enc = encode(raw, os.path.join(RUN, f"{TAG}_final.mp4"))
    delivered = f"{TAG}_final.mp4 = crf-18 of the RAW (RTX not applied)"

print("deliverables in", RUN)
for f in (f"{TAG}_raw.mp4", f"{TAG}_final.mp4"):
    p = os.path.join(RUN, f)
    if os.path.exists(p):
        d = probe(p)
        print(f"  {f}  {d['bytes']:,} B  {d['dur']:.3f}s  {d['wh']} @ {d['fps']}  v={d['vcodec']} "
              f"a={d['acodec']} ({d['apresent']})  {d['kbps']:.0f} kbps  frames={d['nb_frames']}")
print("DELIVERED:", delivered or "ENCODE FAIL")
sys.exit(0 if enc else 1)
