
import runpy, sys
sys.argv = [
    "rv30_fill_graphs.py",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\bridge\h3max_manifest.json",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\stems.json",
    r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\run",
]
runpy.run_path(
    r"C:\Users\derek\AppData\Local\Temp\rv30_stage\runners\rv30_fill_graphs.py",
    run_name="__main__",
)
