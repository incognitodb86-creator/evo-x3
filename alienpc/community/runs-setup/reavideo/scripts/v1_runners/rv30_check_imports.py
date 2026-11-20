
import os, sys
root = r"C:\Users\derek\AppData\Local\Temp\rv30_stage"
sys.path[:0] = [
    root + r"\scripts\h3max_bridge\src",
    root + r"\scripts\parody",
    root + r"\scripts",
]
os.environ["BETA7_CONVERT_DIR"] = root + r"\scripts\parody"
import yaml, beta7_convert, build_request, wp_lint
from h3max_bridge import export_breakdown
print("IMPORT_OK", hasattr(beta7_convert, "run_with_single_regen"))
