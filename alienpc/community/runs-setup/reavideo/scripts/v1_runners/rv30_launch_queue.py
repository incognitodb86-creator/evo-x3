
import subprocess, sys
run_dir = r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\run"
cmd = [
    sys.executable,
    r"C:\AI\community\scripts\run_queue.py",
    "--run-dir", run_dir,
    "--size", "1344x768",
    "--frames", "362",
    "--no-upscale",
    "--keep-comfy-process",
]
print("QUEUE_CMD", " ".join(cmd), flush=True)
raise SystemExit(subprocess.call(cmd))
