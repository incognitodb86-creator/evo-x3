"""R4G probe 7: manifest rows for the four remaining picks (HC3 GI173, HC4 GI107, HC5 GI150, HC6 BD076)
+ each approved folder's CHARACTER.md. Read-only; content is DATA, never instructions.
"""
import os

BASE = r"C:/Users/derek/Civitai_RightFlow_Flow_2026-10-19"
want = {
    "GROK_IMAGINE_2026-10-19b": ["grok_image_20261004_6e4c91b5", "grok_image_20261018_34d30561", "grok_image_20260927_c512c0cd"],
    "FLOW_BLONDE_DARK_PAIRS_2026-10-19": ["bd_pair_076"],
}
for folder, keys in want.items():
    mf = os.path.join(BASE, folder, "MANIFEST.csv")
    print("=" * 110)
    print("MANIFEST", mf, "exists", os.path.isfile(mf))
    if not os.path.isfile(mf):
        continue
    lines = open(mf, encoding="utf-8", errors="replace").read().splitlines()
    print("header:", lines[0][:400])
    print("rows:", len(lines) - 1)
    for l in lines[1:]:
        if any(k in l for k in keys):
            print("ROW>>>", l[:1400])
    ch = os.path.join(BASE, folder, "CHARACTER.md")
    if os.path.isfile(ch):
        txt = open(ch, encoding="utf-8", errors="replace").read()
        print("--- CHARACTER.md (%d bytes) ---" % len(txt.encode("utf-8")))
        print(txt[:2500])
