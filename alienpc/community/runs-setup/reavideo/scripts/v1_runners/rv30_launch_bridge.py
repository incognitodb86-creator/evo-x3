
import os, runpy, sys
root = r"C:\Users\derek\AppData\Local\Temp\rv30_stage"
sys.path[:0] = [
    root + r"\scripts\h3max_bridge\src",
    root + r"\scripts\parody",
    root + r"\scripts",
]
os.environ["BETA7_CONVERT_DIR"] = root + r"\scripts\parody"
sys.argv = [
    "rv30_run_bridge.py",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\stems.json",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\bridge",
]
runpy.run_path(root + r"\runners\rv30_run_bridge.py", run_name="__main__")
