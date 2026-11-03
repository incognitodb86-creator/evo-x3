"""Stage (a) first-frame A/B (brief 2026-11-02-2010). No render. Arm A reuses the existing c1 clip (Derek's brief:
reuse, no render); arm B c1_kf = base JSON with only c0.inputs.prompt + save.filename_prefix changed."""
import json, os, hashlib, shutil, sys
BASE = r"C:\AI\community\runs\h3_lora_ab_20261102\c1_face_lora_07"
RUN = r"C:\AI\community\runs\h3_firstframe_ab_20261102"
KF = r"C:\AI\fleet-brain\30_handoff\briefs\2026-11-02-2010-h3-prompt-c1-c2-c3-keyframe.txt"
sha = lambda b: hashlib.sha256(b).hexdigest()
g = json.load(open(os.path.join(BASE, "c1_face_lora_07.api.json"), encoding="utf-8"))
old_p = g["c0"]["inputs"]["prompt"]
assert sha(old_p.encode()).upper().startswith("D73B6036EBC927BD"), "base prompt sha mismatch"
kf_bytes = open(KF, "rb").read()
assert sha(kf_bytes).upper().startswith("92D6D662"), "keyframe txt sha mismatch"
kf = kf_bytes.decode("utf-8").replace("\r\n", "\n").rstrip("\n")
os.makedirs(os.path.join(RUN, "c1_orig"), exist_ok=True)
os.makedirs(os.path.join(RUN, "c1_kf"), exist_ok=True)
a = json.loads(json.dumps(g)); a["save"]["inputs"]["filename_prefix"] = "community/h3_firstframe_ab_20261102/c1_orig/c1_orig"
b = json.loads(json.dumps(g)); b["c0"]["inputs"]["prompt"] = kf
b["save"]["inputs"]["filename_prefix"] = "community/h3_firstframe_ab_20261102/c1_kf/c1_kf"
for tag, gg in (("c1_orig", a), ("c1_kf", b)):
    json.dump(gg, open(os.path.join(RUN, tag, "request.api.json"), "w", encoding="utf-8"), indent=1)
# diff gate
diffs = []
for k in set(a) | set(b):
    if a.get(k, {}).get("class_type") != b.get(k, {}).get("class_type"): diffs.append((k, "class_type"))
    ia, ib = a.get(k, {}).get("inputs", {}), b.get(k, {}).get("inputs", {})
    for f in set(ia) | set(ib):
        if ia.get(f) != ib.get(f): diffs.append((k, f))
diffs.sort()
ok = diffs == [("c0", "prompt"), ("save", "filename_prefix")]
# c1_orig vs base: only prefix
d0 = sorted((k, f) for k in g for f in g[k]["inputs"] if g[k]["inputs"][f] != a[k]["inputs"][f])
ok = ok and d0 == [("save", "filename_prefix")]
shutil.copy2(os.path.join(BASE, "c1_face_lora_07.mp4"), os.path.join(RUN, "c1_orig", "c1_orig.mp4"))
clip_sha = sha(open(os.path.join(RUN, "c1_orig", "c1_orig.mp4"), "rb").read())
gate = {"gate": "PASS" if ok else "FAIL", "c1_orig_vs_c1_kf": ["%s.inputs.%s" % x for x in diffs],
        "c1_orig_vs_base": ["%s.inputs.%s" % x for x in d0],
        "c1_orig_prompt_sha256": sha(old_p.encode()), "c1_kf_prompt_sha256": sha(kf.encode()),
        "keyframe_txt_sha256": sha(kf_bytes), "c1_orig_clip_reused_from": os.path.join(BASE, "c1_face_lora_07.mp4"),
        "c1_orig_clip_sha256": clip_sha}
json.dump(gate, open(os.path.join(RUN, "_diff_gate.json"), "w", encoding="utf-8"), indent=1)
seed = None
for k, n in g.items():
    for f in ("seed", "noise_seed"):
        if isinstance(n["inputs"].get(f), int): seed = n["inputs"][f]
order = {"run": "h3_firstframe_ab_20261102",
 "plan": "brief 2026-11-02-2010 (a): first-frame prompt A/B on c1. Arm A c1_orig = existing c1_face_lora_07 clip REUSED (no render, per Derek's brief). Arm B c1_kf = same graph, only c0.inputs.prompt -> 2026-11-02-2010-h3-prompt-c1-c2-c3-keyframe.txt (+ filename_prefix). 1 render (budget 2).",
 "status": "STAGED, NOT QUEUED (GPU not idle at staging)", "frames": 124, "n_jobs": 1,
 "base_graph": BASE + r"\c1_face_lora_07.api.json",
 "reused": {"tag": "c1_orig", "clip": "c1_orig\\c1_orig.mp4", "clip_sha256": clip_sha, "prompt_sha256": sha(old_p.encode())},
 "order": [{"pos": 1, "tag": "c1_kf", "arm": "c1_kf", "scene": "a02_pov_cell4", "seed": seed, "frames": 124,
            "lora": "FC_SYDNEY_h3_face_v1.safetensors", "strength_model": 0.7, "prompt_sha256": sha(kf.encode())}]}
json.dump(order, open(os.path.join(RUN, "_render_order.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(gate, indent=1)); print("seed", seed)
sys.exit(0 if ok and seed == 51083021 else 3)
