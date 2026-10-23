"""R4G probe 11: exact pick filenames in ComfyUI\\input\\community\\hc + byte-identity vs approved sources (read-only)."""
import hashlib
import os

COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
APPROVED = r"C:\Users\derek\5slock\approved_characters"
d = os.path.join(COMFY, "input", "community", "hc")
print("DIR", d, os.path.isdir(d))
for n in sorted(os.listdir(d)):
    p = os.path.join(d, n)
    print("  %-58s %8d  %s" % (n, os.path.getsize(p), hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]))
print("=" * 100)
src = {
    "HC3": ("GROK_IMAGINE_2026-10-19b", "GI173.jpg"),
    "HC4": ("GROK_IMAGINE_2026-10-19b", "GI107.jpg"),
    "HC5": ("GROK_IMAGINE_2026-10-19b", "GI150.jpg"),
    "HC6": ("FLOW_BLONDE_DARK_PAIRS_2026-10-19", "BD076.jpg"),
}
for k, (folder, name) in src.items():
    sp = os.path.join(APPROVED, folder, name)
    sh = hashlib.sha256(open(sp, "rb").read()).hexdigest() if os.path.isfile(sp) else "MISSING"
    print(k, "approved source", os.path.basename(sp), "sha", sh[:16])
    for n in sorted(os.listdir(d)):
        if n.startswith(k + "_"):
            ip = os.path.join(d, n)
            ih = hashlib.sha256(open(ip, "rb").read()).hexdigest()
            print("    placed:", n, "identical" if ih == sh else "DIFFERENT", ih[:16])
