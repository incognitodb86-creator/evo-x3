"""ALI-163 R3V probe 2: does a LoadImage string exist for the 10 sheets AS SAVED
in ComfyUI\\output? Uses the REAL folder_paths functions on this box (CPU only,
import only, no network, no GPU, no writes).
"""
import os
import sys

CUI = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
SHEETS = os.path.join(CUI, "output", "community", "hc_sheets")
names = sorted(f for f in os.listdir(SHEETS) if f.lower().endswith(".png"))
print("sheets:", len(names))

sys.path.insert(0, CUI)
try:
    import folder_paths as fpm  # noqa
    ok_import = True
except Exception as e:  # pragma: no cover
    ok_import = False
    print("IMPORT FAIL", type(e).__name__, e)

if ok_import:
    # the way main.py does it (main.py:162 output, :175 input, :510 temp)
    fpm.set_output_directory(os.path.join(CUI, "output"))
    fpm.set_input_directory(os.path.join(CUI, "input"))
    fpm.set_temp_directory(os.path.join(CUI, "temp"))
    print("get_input_directory() =", fpm.get_input_directory())
    print("get_output_directory() =", fpm.get_output_directory())
    cands = []
    cands.append(("placed pick (known-good precedent)", "community/hc/HC1_Two_women_in_studio_editorial.jpg"))
    cands.append(("input subfolder, no suffix", "community/hc_sheets/HC4_00001_.png"))
    cands.append(("absolute output path", os.path.join(SHEETS, "HC4_00001_.png")))
    cands.append(("suffix no space", "community/hc_sheets/HC4_00001_.png[output]"))
    cands.append(("suffix + space", "community/hc_sheets/HC4_00001_.png [output]"))
    cands.append(("suffix + space, input form", "community/hc/HC1_Two_women_in_studio_editorial.jpg [input]"))
    for label, s in cands:
        try:
            p = fpm.get_annotated_filepath(s)
            print("RESOLVED %-26s -> %s | isfile=%s" % (label, p, os.path.isfile(p)))
        except Exception as e:
            print("RAISED   %-26s -> %s: %s" % (label, type(e).__name__, e))
    print()
    print("=== per-sheet test: '<relpath> [output]' (the suffix+space form) ===")
    good = 0
    for n in names:
        s = "community/hc_sheets/" + n + " [output]"
        try:
            p = fpm.get_annotated_filepath(s)
            f = os.path.isfile(p)
            good += 1 if f else 0
            print("%-28s isfile=%-5s -> %s" % (n, f, p))
        except Exception as e:
            print("%-28s RAISED %s: %s" % (n, type(e).__name__, e))
    print("resolving sheets: %d/%d" % (good, len(names)))
    print("annotated_filepath('x[output]') strips to:", repr(fpm.annotated_filepath("abc.png[output]")))
    print("annotated_filepath('x [output]') strips to:", repr(fpm.annotated_filepath("abc.png [output]")))

mn = open(os.path.join(CUI, "main.py"), encoding="utf-8", errors="replace").read().splitlines()
print("\n--- main.py 150-180 (dir defaults) ---")
for i in range(149, 180):
    print(":%d %s" % (i + 1, mn[i].rstrip()))
nd = open(os.path.join(CUI, "nodes.py"), encoding="utf-8", errors="replace").read().splitlines()
print("\n--- nodes.py 1795-1830 (LoadImage tail) ---")
for i in range(1794, 1830):
    print(":%d %s" % (i + 1, nd[i].rstrip()))
print("\n--- nodes.py LoadImage mapping entries ---")
for i, L in enumerate(nd):
    if '"LoadImage"' in L:
        print(":%d %s" % (i + 1, L.rstrip()))
