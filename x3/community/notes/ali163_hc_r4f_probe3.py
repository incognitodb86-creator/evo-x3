# ALI-163 R4F probe 3: why does cv2.imread return None in this venv? Test imread vs imdecode fallback.
import cv2, numpy as np, os
paths = [r"C:\AI\community\notes\face_r4f\r1_f01.png",
         r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc\hardcore1_start.png",
         r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc\HC1_sheet2_woman1.png"]
print("cv2", cv2.__version__)
for p in paths:
    print(p, "exists=", os.path.exists(p), "size=", os.path.getsize(p) if os.path.exists(p) else None)
    img = cv2.imread(p)
    print("  imread ->", None if img is None else img.shape)
    if img is None:
        buf = np.fromfile(p, dtype=np.uint8)
        img2 = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        print("  imdecode ->", None if img2 is None else img2.shape)
