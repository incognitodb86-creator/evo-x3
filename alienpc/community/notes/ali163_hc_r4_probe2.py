import hashlib, os
from PIL import Image

PICK = r"C:\Users\derek\5slock\approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\BD004.jpg"
PLACED = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc\HC1_Two_women_in_studio_editorial.jpg"
OUTDIR = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\output\community\hc_sheets"
INPDIR = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\hc"

EXPECT = {
    "HC1_w1_blonde_00001_.png": ("022cd65e0c3360ba44fba19067ccf11521e3f48450bad481bea7146a4f775c76", 2464826),
    "HC1_w2_darkhair_00001_.png": ("8336fa03aab3de285711605e485f338fd6f2373e7a38397193ea378da3eeca6d", 2759840),
}

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

for p in (PICK, PLACED):
    im = Image.open(p)
    print("PICK/PLACED", p)
    print("   bytes", os.path.getsize(p), "sha", sha(p), "size", im.size, "mode", im.mode)

print()
for name, (want, wantb) in EXPECT.items():
    op = os.path.join(OUTDIR, name)
    ip = os.path.join(INPDIR, name)
    im = Image.open(op)
    print(name)
    print("   out bytes", os.path.getsize(op), "sha", sha(op), "size", im.size, "mode", im.mode,
          "match_sha", sha(op) == want, "match_bytes", os.path.getsize(op) == wantb)
    print("   in exists", os.path.exists(ip), ("in bytes %d sha %s" % (os.path.getsize(ip), sha(ip))) if os.path.exists(ip) else "")

print()
print("input dir now:")
for n in sorted(os.listdir(INPDIR)):
    fp = os.path.join(INPDIR, n)
    print("  ", n, os.path.getsize(fp), sha(fp)[:16])
