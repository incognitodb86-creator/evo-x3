"""R4F probe: check the cv2.FaceDetectorYN / FaceRecognizerSF API on one image (CPU, read-only)."""
import cv2
import numpy as np

D = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\insightface\models\antelopev2\scrfd_10g_bnkps.onnx"
R = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\insightface\models\antelopev2\glintr100.onnx"
IMG = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc\HC1_Two_women_in_studio_editorial.jpg"

det = cv2.FaceDetectorYN.create(D, "", (768, 768), 0.5, 0.4, 5000)
img = cv2.imread(IMG)
print("img", img.shape)
H, W = img.shape[:2]
det.setInputSize((W, H))
out = det.detect(img)
print("detect returns", type(out), len(out) if isinstance(out, tuple) else "")
n, f = out
print("n=", n, "faces arr", None if f is None else (type(f), np.asarray(f).shape, np.asarray(f).dtype))
if f is not None:
    row = np.asarray(f)[0].astype(np.float32)
    rec = cv2.FaceRecognizerSF.create(R, "")
    a = rec.AlignFace(img, row)
    print("AlignFace ->", type(a), None if a is None else np.asarray(a).shape)
    al = np.asarray(a)
    g = rec.GetFeature(al)
    print("GetFeature ->", type(g), np.asarray(g).shape)
    g2 = np.asarray(g).reshape(-1)
    print("norm", float(np.linalg.norm(g2)), "first3", g2[:3])
    b = np.asarray(f)[1].astype(np.float32)
    al2 = np.asarray(rec.AlignFace(img, b))
    g3 = np.asarray(rec.GetFeature(al2)).reshape(-1)
    print("cross cos", float(rec.Calcos(np.asarray(g), np.asarray(g3))))
