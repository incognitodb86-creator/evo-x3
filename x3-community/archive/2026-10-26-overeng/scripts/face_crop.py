"""face_crop.py - crop one woman's face from her approved start still into ComfyUI input\\community\\hc (Max, 2026-10-23, ALI-163 R4G2).
Derrick 2026-10-23 1:42 PM CT: "Yes, let Forge crop each woman's face from her start still and use it as the reference".

Forge runs this; Forge never edits it (pi-permissions + ralph $Prot). Needs only Pillow (already installed).

  python C:/AI/community/scripts/face_crop.py --src <start still> --box x,y,w,h --out HC3_w1_face.png [--size 512] [--margin 0.6] [--force]
  python C:/AI/community/scripts/face_crop.py --src <start still> --auto --out HC3_w1_face.png      (largest face, OpenCV Haar; only if cv2 is installed)

--box   face box in source pixels (from the CPU face detector Forge already uses).
--margin  extra context on each side, as a fraction of the box's longer side (0.6 = forehead, hair and chin in frame).
--size  output side in px, 400-550 (square, LANCZOS).
Writes ONLY a .png/.jpg/.jpeg/.webp whose name contains "_face", directly inside C:\\Users\\derek\\HardcoreNSFW-TestRuntime\\ComfyUI\\input\\community\\hc
(no subfolders, no "..", no other folder). Never overwrites unless --force. The source is opened read-only. Prints one JSON line; logs to notes\\face_crop.log.
"""
import argparse, json, os, re, sys, time

HC = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"
LOG = r"C:\AI\community\notes\face_crop.log"
NAME_OK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*_face[A-Za-z0-9._-]*\.(png|jpg|jpeg|webp)$", re.I)


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} CT {msg}"
    print(line, file=sys.stderr)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def refuse(msg, rc=2):
    log("REFUSED " + msg)
    print(json.dumps({"ok": False, "error": msg}))
    sys.exit(rc)


def dest_for(name):
    if not NAME_OK.match(name or ""):
        refuse(f"--out must be a plain file name containing '_face' and ending .png/.jpg/.jpeg/.webp (got {name!r}); it is always written into {HC}")
    hc = os.path.realpath(HC)
    d = os.path.realpath(os.path.join(hc, name))
    if os.path.dirname(d).lower() != hc.lower():
        refuse(f"--out resolves outside {HC}: {d}")
    return d


def auto_box(path):
    try:
        import cv2
    except ImportError:
        refuse("--auto needs OpenCV (cv2), which is not installed; pass --box x,y,w,h from the CPU face detector instead")
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        refuse(f"cv2 could not read {path}")
    cc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cc.detectMultiScale(img, 1.1, 5, minSize=(48, 48))
    if len(faces) == 0:
        refuse("--auto found no face; pass --box")
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return int(x), int(y), int(w), int(h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--box")
    g.add_argument("--auto", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("--margin", type=float, default=0.6)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not 400 <= a.size <= 550:
        refuse(f"--size must be 400-550 px (got {a.size})")
    if not 0.0 <= a.margin <= 2.0:
        refuse(f"--margin must be 0-2 (got {a.margin})")
    dest = dest_for(a.out)
    if os.path.exists(dest) and not a.force:
        refuse(f"{dest} exists; pass --force to replace your own crop")
    if not os.path.isfile(a.src):
        refuse(f"--src not found: {a.src}")
    from PIL import Image
    with Image.open(a.src) as im:
        im.load()
        W, H = im.size
        if a.box:
            try:
                x, y, w, h = [int(round(float(v))) for v in a.box.split(",")]
            except ValueError:
                refuse(f"--box must be x,y,w,h (got {a.box!r})")
        else:
            x, y, w, h = auto_box(a.src)
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > W or y + h > H:
            refuse(f"--box {x},{y},{w},{h} is outside the {W}x{H} image")
        side = int(round(max(w, h) * (1 + 2 * a.margin)))
        side = min(side, W, H)
        cx, cy = x + w / 2, y + h / 2
        l = int(round(min(max(cx - side / 2, 0), W - side)))
        t = int(round(min(max(cy - side / 2, 0), H - side)))
        crop = im.crop((l, t, l + side, t + side)).convert("RGB")
        out = crop.resize((a.size, a.size), Image.LANCZOS)
        ext = os.path.splitext(dest)[1].lower()
        kw = {"quality": 95} if ext in (".jpg", ".jpeg", ".webp") else {}
        out.save(dest, **kw)
    res = {"ok": True, "out": dest, "src": a.src, "src_size": [W, H], "face_box": [x, y, w, h], "crop_box": [l, t, side, side],
           "out_px": a.size, "upscaled": side < a.size, "bytes": os.path.getsize(dest)}
    log("WROTE " + json.dumps(res))
    print(json.dumps(res))


if __name__ == "__main__":
    main()
