import os
CUI = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
for c in ["nodes.py", os.path.join("comfy_extras", "nodes.py"), os.path.join("comfy_extras", "nodes_load_image.py"), "folder_paths.py", "execution.py", "server.py"]:
    p = os.path.join(CUI, c)
    if os.path.isfile(p):
        txt = open(p, encoding="utf-8", errors="replace").read()
        print("FILE %s %d B classLoadImage=%s get_annotated=%s is_within=%s get_input_dir=%s" % (
            c, os.path.getsize(p), "class LoadImage" in txt, "def get_annotated_filepath" in txt,
            "def is_within_directory" in txt, "def get_input_directory" in txt))
    else:
        print("MISSING " + c)
print("comfy_extras files with LoadImage:", [f for f in os.listdir(os.path.join(CUI, "comfy_extras")) if "load" in f.lower()])
