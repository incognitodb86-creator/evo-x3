"""R2 probe 8 (read-only): what face/vision tooling exists on this box.
Probe 7 raised AttributeError: module 'cv2' has no attribute 'CascadeClassifier'.
"""
import importlib
import importlib.util
import os

for mod in ("cv2", "numpy", "mediapipe", "dlib", "insightface", "facenet_pytorch", "torch",
            "torchvision", "ultralytics", "mtcnn", "retinaface", "face_recognition", "skimage",
            "PIL", "imageio", "scenedetect"):
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError):
        spec = None
    print("%-18s spec=%s" % (mod, spec.origin if spec else None))

cv2 = importlib.import_module("cv2")
print("cv2 file:", getattr(cv2, "__file__", None), "version:", getattr(cv2, "__version__", "?"))
names = [n for n in dir(cv2) if "ascade" in n or "Face" in n or "detect" in n.lower()]
print("cv2 face/detect attrs:", names[:30])
print("cv2.data:", getattr(getattr(cv2, "data", None), "haarcascades", None))
