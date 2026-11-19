"""R4G probe 15: how are the r1/r2 reference slots wired (key names + value shapes)?"""
import json

for tag, p in (("r1", r"C:\AI\community\runs\ali147_pool_hc_r1_s51130001\request.api.json"),
               ("r2", r"C:\AI\community\runs\ali147_pool_hc_r2_s51130002\request.api.json")):
    g = json.loads(open(p, encoding="utf-8").read().replace("\r\n", "\n"))
    print("=", tag, "nodes", len(g))
    for nid in ("c0", "c1"):
        ins = g[nid]["inputs"]
        print(f" {nid} class {g[nid]['class_type']} ref_image_size {ins.get('ref_image_size', '-')}")
        for k, v in sorted(ins.items()):
            if "ref" in k.lower():
                print(f"   {k} = {json.dumps(v)}")
    for nid, node in sorted(g.items()):
        if node["class_type"] in ("LoadImage", "LoadImageFromDirectory", "VHS_VideoCombine", "LoadVideo"):
            print(f"  loader {nid} {node['class_type']} {json.dumps(node['inputs'])[:160]}")
