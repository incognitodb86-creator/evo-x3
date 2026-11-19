"""ALI-163 R4F face library - CPU-only SCRFD face detection + ArcFace identity embedding.

Models already on disk (no download, no GPU, no ComfyUI .venv, no installs):
  detector : C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI\\models\\insightface\\models\\antelopev2\\scrfd_10g_bnkps.onnx
  embedder : ...\\antelopev2\\glintr100.onnx
`insightface` is NOT installed in C:\\AI\\qa_gate_venv and cv2.FaceDetectorYN rejects this export
(it asks for 12 outputs, the insightface export has 9), so the decode follows the local insightface-style
implementation shipped in C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI\\custom_nodes\\comfyui-reactor-node\\
reactor_core\\inswap.py (SCRFD.forward/detect, distance2bbox/distance2kps, ARCFACE_STD_POINTS, norm_crop,
ArcFaceONNX.get; that file is a local copy of deepinsight/insightface model_zoo maths -
https://github.com/deepinsight/insightface). Preprocessing matches it: blob mean 127.5, scale 1/128 for
SCRFD, 1/127.5 for ArcFace, swapRB=True, 5-point landmark -> 112x112 similarity-transform crop.
"""
import cv2
import numpy as np
import onnxruntime as ort

DET = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\insightface\models\antelopev2\scrfd_10g_bnkps.onnx"
REC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\insightface\models\antelopev2\glintr100.onnx"

STRIDES = [8, 16, 32]
ARCFACE_STD_POINTS = np.array([[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
                               [41.5493, 92.3655], [70.7299, 92.2041]], dtype=np.float32)


def _sess(path):
    so = ort.SessionOptions()
    so.log_severity_level = 3
    return ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])


def distance2bbox(points, distance, max_shape=None):
    x1 = points[:, 0] - distance[:, 0]
    y1 = points[:, 1] - distance[:, 1]
    x2 = points[:, 0] + distance[:, 2]
    y2 = points[:, 1] + distance[:, 3]
    if max_shape is not None:
        x1 = np.clip(x1, 0, max_shape[1])
        y1 = np.clip(y1, 0, max_shape[0])
        x2 = np.clip(x2, 0, max_shape[1])
        y2 = np.clip(y2, 0, max_shape[0])
    return np.stack([x1, y1, x2, y2], axis=-1)


def distance2kps(points, distance, max_shape=None):
    preds = []
    for i in range(0, distance.shape[1], 2):
        px = points[:, i % 2] + distance[:, i]
        py = points[:, i % 2 + 1] + distance[:, i + 1]
        if max_shape is not None:
            px = np.clip(px, 0, max_shape[1])
            py = np.clip(py, 0, max_shape[0])
        preds.append(px)
        preds.append(py)
    return np.stack(preds, axis=-1)


def norm_crop(img, landmark, image_size=112):
    M, _ = cv2.estimateAffinePartial2D(np.asarray(landmark, dtype=np.float32), ARCFACE_STD_POINTS)
    return cv2.warpAffine(img, M, (image_size, image_size), borderValue=0.0)


def _nms(dets, nms_thresh=0.4):
    """IoU NMS on (x1,y1,x2,y2,score) rows - as in the reactor/insightface SCRFD.nms."""
    x1, y1, x2, y2, scores = dets[:, 0], dets[:, 1], dets[:, 2], dets[:, 3], dets[:, 4]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        ovr = (w * h) / (areas[i] + areas[order[1:]] - w * h)
        order = order[np.where(ovr <= nms_thresh)[0] + 1]
    return keep
class Scrfd:
    """SCRFD-10G (bnkps, 9 flat outputs: scores x3, bbox x3, kps x3)."""

    def __init__(self, thr=0.5, input_size=(640, 640)):
        self.s = _sess(DET)
        self.iname = self.s.get_inputs()[0].name
        self.onames = [o.name for o in self.s.get_outputs()]
        self.thr = thr
        self.input_size = input_size
        self.center_cache = {}

    def _centers(self, h, w, stride):
        key = (h, w, stride)
        if key not in self.center_cache:
            ac = np.stack(np.mgrid[:h, :w][::-1], axis=-1).astype(np.float32)
            ac = (ac * stride).reshape(-1, 2)
            ac = np.stack([ac] * 2, axis=1).reshape(-1, 2)
            self.center_cache[key] = ac
        return self.center_cache[key]

    def detect(self, img, thr=None, input_size=None, max_num=0):
        thr = self.thr if thr is None else thr
        tw, th = self.input_size if input_size is None else input_size
        ih, iw = img.shape[:2]
        im_ratio = float(ih) / iw
        model_ratio = float(th) / tw
        if im_ratio > model_ratio:
            nh, nw = th, int(th / im_ratio)
        else:
            nw, nh = tw, int(tw * im_ratio)
        det_scale = float(nh) / ih
        resized = cv2.resize(img, (nw, nh))
        canvas = np.zeros((th, tw, 3), dtype=np.uint8)
        canvas[:nh, :nw, :] = resized
        blob = cv2.dnn.blobFromImage(canvas, 1.0 / 128.0, (tw, th), (127.5, 127.5, 127.5), swapRB=True)
        outs = self.s.run(self.onames, {self.iname: blob})
        sc_l, bb_l, kp_l = [], [], []
        for idx, st in enumerate(STRIDES):
            sc = np.asarray(outs[idx]).ravel()
            bb = np.asarray(outs[idx + 3], dtype=np.float32).reshape(-1, 4) * st
            kp = np.asarray(outs[idx + 6], dtype=np.float32).reshape(-1, 10) * st
            h, w = th // st, tw // st
            ac = self._centers(h, w, st)
            pos = np.where(sc >= thr)[0]
            if pos.size == 0:
                continue
            sc_l.append(sc[pos])
            bb_l.append(distance2bbox(ac, bb)[pos])
            kp_l.append(distance2kps(ac, kp).reshape(ac.shape[0], -1, 2)[pos])
        if not sc_l:
            return []
        scores = np.concatenate([s.ravel() for s in sc_l])
        bboxes = np.vstack(bb_l) / det_scale
        kpss = np.vstack([k.reshape(k.shape[0], -1, 2) for k in kp_l]) / det_scale
        pre = np.hstack((bboxes, scores[:, None])).astype(np.float32)
        order = scores.argsort()[::-1]
        pre, kpss = pre[order], kpss[order]
        keep = _nms(pre, 0.4)
        det = pre[keep]
        kpss = kpss[keep]
        if max_num > 0 and det.shape[0] > max_num:
            areas = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
            cx = (det[:, 0] + det[:, 2]) / 2 - iw / 2.0
            cy = (det[:, 1] + det[:, 3]) / 2 - ih / 2.0
            offsets = np.sqrt(cx ** 2 + cy ** 2)
            idx = np.argsort(-(areas * 0.65 + offsets * 0.35))[:max_num]
            det, kpss = det[idx], kpss[idx]
        out = []
        for i in range(det.shape[0]):
            b = det[i, :4]
            out.append({"box": [float(v) for v in b], "score": float(det[i, 4]),
                        "area": float((b[2] - b[0]) * (b[3] - b[1])),
                        "kps": [[float(x), float(y)] for x, y in kpss[i]]})
        out.sort(key=lambda d: -d["area"])
        return out


class ArcFace:
    def __init__(self):
        self.s = _sess(REC)
        inp = self.s.get_inputs()[0]
        self.iname = inp.name
        self.oname = self.s.get_outputs()[0].name
        self.hw = tuple(int(v) for v in inp.shape[2:4])

    def embed(self, img, face):
        aimg = norm_crop(img, face["kps"], image_size=self.hw[0])
        blob = cv2.dnn.blobFromImage(aimg, 1.0 / 127.5, (self.hw[1], self.hw[0]),
                                     (127.5, 127.5, 127.5), swapRB=True)
        f = np.asarray(self.s.run([self.oname], {self.iname: blob})[0]).reshape(-1).astype(np.float32)
        return f / max(np.linalg.norm(f), 1e-9)


def cos(a, b):
    return float(np.dot(a, b))


def mean_emb(embs):
    m = np.mean(np.stack(embs), axis=0)
    return m / max(np.linalg.norm(m), 1e-9)
