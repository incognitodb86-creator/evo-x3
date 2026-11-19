"""Synthetic, non-photographic test images only (flat colour, gradients, rectangles). No people, ever (R1)."""
from PIL import Image, ImageDraw


def make(path, w, h, seed=0):
    im = Image.new("RGB", (w, h), ((seed * 37) % 256, (seed * 91) % 256, (seed * 53) % 256))
    d = ImageDraw.Draw(im)
    d.rectangle([w // 4, h // 4, w // 2, h // 2], fill=((seed * 13) % 256, 200, 40))
    im.save(path)
    return path
