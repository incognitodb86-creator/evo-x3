import os
CUI = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
fp = open(os.path.join(CUI, "folder_paths.py"), encoding="utf-8", errors="replace").read().splitlines()
print("--- folder_paths.py imports (top 40 lines) ---")
for i, L in enumerate(fp[:40]):
    print(":%d %s" % (i + 1, L))
print("--- set_input/output/temp directory + get_* ---")
for i, L in enumerate(fp):
    if L.startswith("def ") and ("directory" in L):
        print(":%d %s" % (i + 1, L.rstrip()))
print("--- nodes.py LoadImage validate / essentials ---")
nd = open(os.path.join(CUI, "nodes.py"), encoding="utf-8", errors="replace").read().splitlines()
start = None
for i, L in enumerate(nd):
    if L.startswith("class LoadImage"):
        start = i
    if start is not None and i >= start and i <= start + 90:
        if "validate" in L or "get_annotated_filepath" in L or "NODE_CLASS_MAPPINGS" in L:
            print(":%d %s" % (i + 1, L.rstrip()))
for i, L in enumerate(nd):
    if "validate_image_file_existence" in L:
        print("HIT :%d %s" % (i + 1, L.rstrip()))
        for j in range(i, min(i + 12, len(nd))):
            print("    :%d %s" % (j + 1, nd[j].rstrip()))
        break
print("--- main.py set_*_directory calls ---")
mn = open(os.path.join(CUI, "main.py"), encoding="utf-8", errors="replace").read().splitlines()
for i, L in enumerate(mn):
    if "set_input_directory" in L or "set_output_directory" in L or "set_temp_directory" in L:
        print(":%d %s" % (i + 1, L.rstrip()))
