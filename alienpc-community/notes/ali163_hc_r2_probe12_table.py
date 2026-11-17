"""R2 probe 12 (read-only): the one evidence table R2 quotes.
Graph keys + prompt metrics for HC1 / HC2 / RS4 / RS6 / PV2, and the placed reference files.
No GPU, no image/video opened, nothing written outside notes\.
"""
import hashlib
import json
import os

RUNS = r"C:\AI\community\runs"
ARMS = {
    "HC1": "ali147_pool_hc_c1_s51100001",
    "HC2": "ali147_pool_hc_c2_s51100002",
    "RS4": "ali147_pool_refsheet_s51080000",
    "RS6": "ali147_pool_refsheet_b_s51080000",
    "PV2": "ali147_pool_promptv2_s51080000",
}


def stat(txt):
    return dict(chars=len(txt), words=len(txt.split()),
                sha=hashlib.sha256(txt.encode()).hexdigest()[:16],
                pict=txt.count("<Picture"), subj=txt.count("<Subject"),
                sound=("overall_soundscape:" in txt),
                subjdef=("subject_definitions:" in txt),
                integrated=("integrated_multimodal_description" in txt))


def subdef(txt):
    i = txt.find("subject_definitions:")
    if i < 0:
        return None
    seg = txt[i:i + 600]
    for key in ("summary:", "retention_analysis:", "detailed_description:", "integrated_multimodal_description"):
        j = seg.find(key)
        if j > 0:
            seg = seg[:j]
    return seg.strip()


for tag, d in ARMS.items():
    p = os.path.join(RUNS, d, "request.api.json")
    g = json.loads(open(p, "rb").read().decode("utf-8-sig"))
    print("=" * 78)
    print("%s %s  nodes=%d" % (tag, d, len(g)))
    for nid in sorted(g):
        c = g[nid]["class_type"]
        if c in ("LoadImage", "SaveVideo", "VHS_VideoCombine"):
            for k, v in g[nid]["inputs"].items():
                if k in ("image", "filename_prefix", "name"):
                    print("   %s(%s).%s = %s" % (nid, c, k, v))
    for nid in ("c0", "c1", "win1", "app1", "tail1", "noise", "m_ck", "m_shift", "m_vsa", "m_attn"):
        if nid not in g:
            print("   MISSING NODE %s" % nid)
            continue
        n = g[nid]
        inp = n["inputs"]
        keys = {}
        for k in ("width", "height", "length", "ref_image_size", "overlap_frames", "extension_frames",
                  "window_length", "noise_seed", "ckpt_name", "model_name", "unet_name", "selection",
                  "selection.keep_percent", "scheduler", "sampler_name", "steps", "denoise"):
            if k in inp and not isinstance(inp[k], list):
                keys[k] = inp[k]
        refs = {k: (v[0] if isinstance(v, list) else v) for k, v in inp.items() if k.startswith("ref_image") and k != "ref_image_size"}
        print("   %s(%s) %s refs=%s" % (nid, n["class_type"], json.dumps(keys, sort_keys=True), json.dumps(refs, sort_keys=True)))
        if "prompt" in inp:
            print("      prompt %s" % json.dumps(stat(inp["prompt"])))
            sd = subdef(inp["prompt"])
            if sd:
                print("      subject_definitions -> %s" % sd.replace("\n", " | "))
    for f in ("objective.json",):
        fp = os.path.join(RUNS, d, f)
        if os.path.exists(fp):
            o = json.loads(open(fp, encoding="utf-8").read())
            a = o["attempts"][0] if "attempts" in o else o
            print("   objective: ok=%s frames=%s %sx%s fps=%s audio=%s dur=%s secs=%s blackfreeze=%s"
                  % (o.get("ok"), a.get("frames"), a.get("w"), a.get("h"), a.get("fps"), a.get("audio"),
                     a.get("duration"), a.get("secs"), a.get("blackfreeze")))
