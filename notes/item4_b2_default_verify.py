"""item 4 (2026-10-29): verify the new default graph is byte-identical to B2's request.api.json.
CPU only: sha256 compare + JSON parse + the keys the runner is allowed to change."""
import hashlib, json

B2 = r"C:/AI/community/runs/terrace_dom_q5guide_20261028_s51083007/request.api.json"
NEW = r"C:/AI/community/p7/graphs/default_b2_terrace_dom_q5guide_s51083007.api.json"

a = open(B2, "rb").read()
b = open(NEW, "rb").read()
print("bytes", len(a), len(b), "equal" if a == b else "DIFFER")
print("sha256", hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())
g = json.loads(b.decode("utf-8"))
print("nodes", len(g))
print("c0.length", g["c0"]["inputs"]["length"], "ref_image_size", g["c0"]["inputs"]["ref_image_size"])
print("unet", g["unet"]["inputs"]["unet_name"])
print("prefix (per-run key, unchanged in the default)", g["save"]["inputs"]["filename_prefix"])
