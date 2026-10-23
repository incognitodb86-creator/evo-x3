"""R4G probe 16: cfg / sampling knobs in the four new graphs (CPU, read-only)."""
import json

P = r"C:\AI\community\runs"
IDS = ["ali147_pool_hc_r3_s51130003", "ali147_pool_hc_r4_s51130004",
       "ali147_pool_hc_r5_s51130005", "ali147_pool_hc_r6_s51130006"]

for i in IDS:
    g = json.loads(open(P + "\\" + i + "\\request.api.json", encoding="utf-8").read().replace("\r\n", "\n"))
    print("=", i)
    for nid in sorted(g):
        ins = g[nid]["inputs"]
        hits = {k: v for k, v in ins.items() if isinstance(v, (int, float, str)) and (
            "cfg" in k.lower() or "denoise" in k.lower() or "shift" in k.lower()
            or k in ("scheduler_name", "sampler_name", "steps", "multiplier", "enable_vsa",
                     "weight", "unscale_nope", "q_k_norm", "add_noise_entry", "audio_vae",
                     "image_size", "frame_rate", "total_frames", "extension_frames", "fps"))}
        if hits:
            print(f"  {nid:5s} {g[nid]['class_type']:34s} {json.dumps(hits)}")
