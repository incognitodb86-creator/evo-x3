"""R4G probe 13: base ksel / m_shift / m_vsa / m_attn / s0_sched / s1_sched / app1 / unet inputs (read-only)."""
import json
import os

p = os.path.join(r"C:/AI/community", "runs", "ali147_pool_refsheet_b_s51080000", "request.api.json")
g = json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
for nid in ("ksel", "m_shift", "m_vsa", "m_attn", "s0_sched", "s1_sched", "s0_guide", "s1_guide", "app1", "unet", "noise", "clip"):
    print("==", nid, g[nid]["class_type"], json.dumps(g[nid]["inputs"], sort_keys=True)[:420])
print("classes:", sorted({v["class_type"] for v in g.values()}))
