"""R4G probe 14: why does check 6 (sampling/audio) and check 8 (wording) fail? Prints the base and new node inputs."""
import json
import os

W = r"C:\AI\community"
BASE = os.path.join(W, "runs", "ali147_pool_refsheet_b_s51080000", "request.api.json")
NEW = os.path.join(W, "runs", "ali147_pool_hc_r5_s51130005", "request.api.json")


def load(p):
    return json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))


b, n = load(BASE), load(NEW)
for nid in ("unet", "ksel", "s0_sched", "s0_samp", "s1_sched", "s1_samp", "m_shift", "m_vsa",
            "dec_a", "dec_v", "mkvid", "tail1", "avae", "vvae", "c0", "c1", "win1", "sheet", "img"):
    for tag, g in (("base", b), ("new", n)):
        if nid in g:
            print(f"{tag} {nid} {g[nid]['class_type']} {json.dumps(g[nid]['inputs'], ensure_ascii=True)[:420]}")
    print("-")
print("samplers base", sorted(k for k, v in b.items() if v["class_type"].startswith("KSampler")))
print("samplers new ", sorted(k for k, v in n.items() if v["class_type"].startswith("KSampler")))
print("new classes", sorted({v["class_type"] for v in n.values()}))
