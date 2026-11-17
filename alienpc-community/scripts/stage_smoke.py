#!/usr/bin/env python3
"""stage_smoke.py - make the throwaway tiny clip the RTX node is tested on (the brief's smoke test).

24 frames at 256x448 with a tone: small enough to prove the RTX path (VHS load -> RTXVideoSuperResolution
-> CreateVideo -> SaveVideo) end to end in seconds, with audio present so the audio path is covered too.
Written into ComfyUI's input dir because VHS_LoadVideo lists files from there.
"""
import os
import shutil
import subprocess

FFD = r"C:\Users\derek\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
FF = os.path.join(FFD, "ffmpeg.exe") if os.path.exists(os.path.join(FFD, "ffmpeg.exe")) else shutil.which("ffmpeg")
FP = os.path.join(FFD, "ffprobe.exe") if os.path.exists(os.path.join(FFD, "ffprobe.exe")) else shutil.which("ffprobe")
DST = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\rtx_smoke_in.mp4"
print("ffmpeg:", FF)
r = subprocess.run([FF, "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc2=size=256x448:rate=24:duration=1",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-shortest", "-pix_fmt", "yuv420p",
                    "-c:v", "libx264", "-crf", "28", "-c:a", "aac", "-b:a", "64k", DST],
                   capture_output=True, text=True)
print("stage rc=", r.returncode, r.stderr[-200:])
p = subprocess.run([FP, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", DST],
                   capture_output=True, text=True)
d = __import__("json").loads(p.stdout)
v = next(s for s in d["streams"] if s["codec_type"] == "video")
a = [s for s in d["streams"] if s["codec_type"] == "audio"]
print(f"staged {DST}\n  {os.path.getsize(DST)} B  {v['width']}x{v['height']} {v['r_frame_rate']} "
      f"nb_frames={v.get('nb_frames')} dur={d['format'].get('duration')} audio_streams={len(a)}")
