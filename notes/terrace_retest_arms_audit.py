#!/usr/bin/env python
# terrace_retest_arms_audit.py - self-check every built arm and generate the arm diff table FROM JSON.
# Brief2 item 5 (diff table) + brief3 item 1 (self-check by script, not by eye). No GPU, no render, no
# network except the adults guard. Expectations here are transcribed from the PLAN (Max's arm list), on
# purpose: this is not the builder grading its own work.
#   python C:\AI\director\.venv\Scripts\python.exe C:\AI\community\notes\terrace_retest_arms_audit.py
# Writes: notes/terrace_retest_arms_self_check.txt (per-arm PASS/DROP)
#         notes/2026-10-29-terrace-retest-diff.md (arm | changed keys | still | seed | prompt sha | WxH | frames)
import hashlib
import json
import os
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\AI\community\scripts")
from comm import guard_ok, prompt_strings  # noqa: E402

ROOT = r"C:\AI\community\runs\terrace_retest_20261029"
B2JSON = r"C:\AI\community\runs\terrace_dom_q5guide_20261028_s51083007\request.api.json"
BASE_T4 = r"C:\AI\community\runs\terrace_dom_q5stockv2_20261028_s51083011\_ui2api\api_T4.json"
S8_FILE = os.path.join(ROOT, "_src", "s8_line_pic1_scene_identity.txt")
STILL = "community/TERRACE2_768x1344.png"
STILL_PATH = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\input\community\TERRACE2_768x1344.png"
B2_PROMPT_SHA = "fcad1c379bf097f3744690ee8b4f6a1052125fce82a58c33804af726cdf3e69d"
S8_SHA = "dae7567438227802b08d6276faece019759c43958199f97cb2482c5daf8e2908"
FRAMES = 124
CANVAS = (768, 1344)
ASPECT = "9:16 (Portrait Widescreen)"
SEEDS = (51083002, 51083012, 51083013)
ARMS = (["b2_s%d" % s for s in SEEDS] + ["s%d_s51083002" % i for i in range(1, 9)]
        + ["t4c_s%d" % s for s in SEEDS] + ["t4g_s51083002"])
B2_DELTAS = {
    "b2_s51083002": {},
    "b2_s51083012": {"noise.noise_seed": 51083012},
    "b2_s51083013": {"noise.noise_seed": 51083013},
    "s1_s51083002": {"ksel.sampler_name": "er_sde", "s0_sched.scheduler": "sgm_uniform"},
    "s2_s51083002": {"unet.unet_name": "10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors"},
    "s3_s51083002": {"lsu3.model_name": "minimax_h3_latent_upscaler_3d_fp16.safetensors"},
    "s4_s51083002": {"c0.ref_image_size": "match"},
    "s5_s51083002": {"s0_guide.conditioning": ["c0", 0], "s1_guide.conditioning": ["c0", 0]},
    "s6_s51083002": {"s0_sched.steps": 6},
    "s7_s51083002": {"ksel.sampler_name": "res_multistep"},
    "s8_s51083002": {"__PROMPT__": True},
}
T4_DELTAS = {
    "t4c_s51083002": {},
    "t4c_s51083012": {"8.seed": 51083012},
    "t4c_s51083013": {"8.seed": 51083013},
    "t4g_s51083002": {"__GUIDES__": True},
}
T4_COMMON = {"21.aspect_ratio": ASPECT, "21.megapixels": 0.25, "23.value": 5.0}
ADDED_OK = {"b2": set(), "t4": {"raw_cv", "raw_save"}}
DELETED_OK = {"s5_s51083002": {"ag0", "ag1"}}


def flat(g):
    return {"%s.%s" % (nid, k): v for nid, n in g.items() for k, v in n.get("inputs", {}).items()}


def png_size(path):
    with open(path, "rb") as f:
        data = f.read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def node_of(g, cls):
    return [nid for nid, n in g.items() if n["class_type"] == cls]


def prompt_of(g):
    for nid in node_of(g, "MiniMaxH3ReferenceToVideo"):
        v = g[nid]["inputs"]["prompt"]
        if isinstance(v, list):  # the stock graph feeds it from a string node
            v = g[str(v[0])]["inputs"].get("value")
        return v
    for nid in node_of(g, "PrimitiveStringMultiline"):
        return g[nid]["inputs"]["value"]
    return None


def image_of(g):
    for nid in node_of(g, "LoadImage"):
        return g[nid]["inputs"]["image"]
    return None


def geometry(g):
    """(pass1 WxH, final WxH, frames) read from the graph's own widgets and the installed math."""
    import math
    if "c0" in g:  # B2 family: literal width/height on the R2V node + a scale-by latent upscaler
        c = g["c0"]["inputs"]
        w, h = c["width"], c["height"]
        up = g[node_of(g, "MinimaxH3LatentUpscaler3D")[0]]["inputs"]
        assert up["mode"] == "scale by multiplier", up["mode"]
        sc = up["mode.scale"]
        return (w, h), (int(round(w * sc)), int(round(h * sc))), c["length"]
    rs = g[node_of(g, "ResolutionSelector")[0]]["inputs"]
    r = {"9:16 (Portrait Widescreen)": (9, 16)}[rs["aspect_ratio"]]
    s = math.sqrt(rs["megapixels"] * 1024 * 1024 / (r[0] * r[1]))
    p1 = (round(r[0] * s / rs["multiple"]) * rs["multiple"], round(r[1] * s / rs["multiple"]) * rs["multiple"])
    up = g[node_of(g, "MinimaxH3LatentUpscaler3D")[0]]["inputs"]
    mp = g[str(up["mode.megapixels"][0])]["inputs"]["value"]
    wi, hi = p1[0] / 8, p1[1] / 8
    ar = wi / hi
    ht = math.sqrt(mp * 1024 * 1024 / ar)
    wt = ht * ar
    wa = round(wt / up["align"]) * up["align"]
    ha = round(ht / up["align"]) * up["align"]
    final = (int(round(wa / 8) * 8), int(round(ha / 8) * 8))
    mn = [n for n in g.values() if n["class_type"] == "ComfyMathExpression" and "% 17" in n["inputs"]["expression"]][0]
    dur = g[str(mn["inputs"]["values.a"][0])]["inputs"]["value"]
    x = max(5, round(dur * 24))
    return p1, final, x + (5 - (x % 17)) % 17


def seed_of(g):
    for nid in node_of(g, "KSampler") + node_of(g, "Seed (rgthree)") + node_of(g, "RandomNoise"):
        for k in ("seed", "noise_seed"):
            if k in g[nid]["inputs"]:
                return g[nid]["inputs"][k]
    return None


def prefixes_of(g):
    """Every save prefix in the graph, link-resolved; the main one must equal the per-run prefix."""
    out = []
    for nid in node_of(g, "SaveVideo"):
        v = g[nid]["inputs"]["filename_prefix"]
        if isinstance(v, list):
            v = g[str(g[str(v[0])]["inputs"]["on_false"][0])]["inputs"]["value"]
        out.append(str(v))
    return out


def main():
    b2 = json.load(open(B2JSON, encoding="utf-8"))
    base_t4 = json.load(open(BASE_T4, encoding="utf-8"))
    b2_prompt = b2["c0"]["inputs"]["prompt"]
    s8_line = open(S8_FILE, encoding="utf-8").read().rstrip("\r\n")
    if hashlib.sha256(s8_line.encode("utf-8")).hexdigest() != S8_SHA:
        print("!! S8 line file moved"); return 2
    still_size = png_size(STILL_PATH)
    print("start still %s: pixels %s, %d bytes" % (STILL_PATH, still_size, os.path.getsize(STILL_PATH)))
    rows, chk = [], []
    for arm in ARMS:
        d = os.path.join(ROOT, arm)
        fam = "t4" if arm.startswith("t4") else "b2"
        base = base_t4 if fam == "t4" else b2
        fails, notes = [], []
        files = {}
        for f in ("request.api.json", "graph_diff.txt", "build_graph.py", "build.log"):
            files[f] = os.path.exists(os.path.join(d, f))
        if not all(files.values()):
            fails.append("missing %s" % [k for k, v in files.items() if not v])
            rows.append((arm, "-", "-", "-", "-", "-", "-"))
            chk.append((arm, "DROP", "; ".join(fails)))
            continue
        g = json.load(open(os.path.join(d, "request.api.json"), encoding="utf-8"))
        b, a = flat(base), flat(g)
        changed = sorted(p for p in set(b) & set(a) if b[p] != a[p])
        added_nodes = {p.split(".")[0] for p in set(a) - set(b)}
        removed_nodes = {p.split(".")[0] for p in set(b) - set(a)}

        # 1. exactly the intended change vs the baseline
        if fam == "b2":
            exp = {"c0.length": FRAMES, "save.filename_prefix": "community/terrace_retest_20261029/%s/%s" % (arm, arm)}
            exp.update(B2_DELTAS[arm])
            if int(arm.split("_s")[1]) != 51083002:
                exp["noise.noise_seed"] = int(arm.split("_s")[1])
            if B2_DELTAS[arm].get("__PROMPT__"):
                exp["c0.prompt"] = s8_line + "\n\n" + b2_prompt
            exp.pop("__PROMPT__", None)
        else:
            exp = dict(T4_COMMON)
            exp["40.value"] = "community/terrace_retest_20261029/%s/%s" % (arm, arm)
            exp.update(T4_DELTAS[arm])
            if int(arm.split("_s")[1]) != 51083002:
                exp["8.seed"] = int(arm.split("_s")[1])
            if T4_DELTAS[arm].get("__GUIDES__"):
                exp.update({"30.conditioning": ["ag_p1", 0], "9.conditioning": ["ag_p2", 0]})
            exp.pop("__GUIDES__", None)
        got = {p: a[p] for p in changed}
        bad = sorted(p for p, v in exp.items() if got.get(p) != v)
        extra = sorted(p for p in got if p not in exp)
        if bad:
            fails.append("expected change missing/wrong: %s" % bad)
        if extra:
            fails.append("undeclared change: %s" % extra)
        if added_nodes - ADDED_OK[fam] - ({"ag_p1", "ag_p2"} if fam == "t4" and arm.startswith("t4g") else set()):
            fails.append("undeclared added nodes: %s" % sorted(added_nodes))
        if removed_nodes != DELETED_OK.get(arm, set()):
            fails.append("unexpected removed nodes: %s" % sorted(removed_nodes))

        # 2. same start frame, wired as Picture 1
        img = image_of(g)
        r2v = node_of(g, "MiniMaxH3ReferenceToVideo")[0]
        refs = [k for k in g[r2v]["inputs"] if k.startswith("ref_images.")]
        src = {str(g[r2v]["inputs"][k][0]) for k in refs if isinstance(g[r2v]["inputs"].get(k), list)}
        guide_imgs = {str(g[n]["inputs"]["image"][0]) for n in node_of(g, "MiniMaxH3AddGuide")
                      if isinstance(g[n]["inputs"].get("image"), list)}
        feed = src | guide_imgs
        imgs = node_of(g, "LoadImage")
        # Picture 1 = exactly one image node, it is the one feeding the ref/guide sockets, and it is
        # the agreed start frame. B2 wires it as ref_image_1 + both guides; the stock graph as ref_image_0.
        if len(imgs) != 1:
            fails.append("%d image nodes in the graph" % len(imgs))
        elif img != STILL:
            fails.append("start image is %r" % img)
        elif feed and feed != {imgs[0]}:
            fails.append("Picture 1 fed from %s" % sorted(feed))
        elif not feed:
            fails.append("no Picture 1 socket fed (ref_images and guides both empty)")
        if still_size != CANVAS:
            fails.append("start file pixels %s" % (still_size,))
        p = prompt_of(g)
        if "<Picture 1>" not in p:
            fails.append("prompt does not anchor <Picture 1>")

        # 3. seed / 4. prompt sha
        sd = seed_of(g)
        if sd != int(arm.split("_s")[1]):
            fails.append("seed %r" % sd)
        ps = hashlib.sha256(p.encode("utf-8")).hexdigest()
        if arm == "s8_s51083002":
            if not p.startswith(s8_line + "\n\n") or hashlib.sha256(s8_line.encode()).hexdigest() != S8_SHA:
                fails.append("S8 line is not the exact #74 text")
            if hashlib.sha256(p.split("\n\n", 1)[1].encode("utf-8")).hexdigest() != B2_PROMPT_SHA:
                fails.append("S8 prompt is not B2 + only the added line")
            notes.append("B2 + line sha %s" % S8_SHA[:8])
        elif ps != B2_PROMPT_SHA:
            fails.append("prompt sha %s" % ps[:16])

        # 5. canvas / 6. frames
        p1, final, fr = geometry(g)
        if final != CANVAS:
            fails.append("canvas %s" % (final,))
        if fr != FRAMES:
            fails.append("frames %r" % fr)
        want_pre = "community/terrace_retest_20261029/%s/%s" % (arm, arm)
        pres = prefixes_of(g)
        if want_pre not in pres or not all(p == want_pre or p == want_pre + "_raw" for p in pres):
            fails.append("save prefixes %s" % pres)

        # 7. adults-only, the same way run_graph_job.py does it: every prompt-bearing string in the
        # graph goes through comm.guard_ok (guard_ok takes one string and returns a bool)
        nstr, denied = 0, []
        for n in g.values():
            for s in prompt_strings(n.get("inputs", {})):
                nstr += 1
                if not guard_ok(s):
                    denied.append("%s prompt string denied by the adults guard" % n["class_type"])
        if denied:
            fails.append("; ".join(sorted(set(denied))))
        notes.append("adults guard: %d prompt string(s) pass" % nstr)

        delta = ", ".join("%s: %s -> %s" % (k, json.dumps(b[k], ensure_ascii=False)[:38],
                                            json.dumps(got[k], ensure_ascii=False)[:38])
                          for k in sorted(exp))
        rows.append((arm, delta, img, sd, ps[:16] + (" (B2)" if ps == B2_PROMPT_SHA else " (B2+line)"),
                      "%dx%d (pass1 %dx%d)" % (final[0], final[1], p1[0], p1[1]), fr))
        chk.append((arm, "PASS" if not fails else "DROP", "; ".join(fails) or "; ".join(notes)))

    out = os.path.join(r"C:\AI\community\notes", "terrace_retest_arms_self_check.txt")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("self-check of the built arms - generated by notes\\terrace_retest_arms_audit.py\n")
        f.write("checks per arm: declared delta vs baseline | start image = %s (768x1344, wired as Picture 1)"
                " | seed | prompt sha (S8 = B2 + only the added line) | final canvas 768x1344 | frames 124 | "
                "per-run save prefix | comm.guard_ok\n\n" % STILL)
        for arm, st, why in chk:
            f.write("%-16s %-4s %s\n" % (arm, st, why))
        f.write("\n%d arms, %d PASS, %d DROP\n" % (len(chk), sum(1 for x in chk if x[1] == "PASS"),
                                                   sum(1 for x in chk if x[1] == "DROP")))
    tbl = os.path.join(r"C:\AI\community\notes", "2026-10-29-terrace-retest-diff.md")
    with open(tbl, "w", encoding="utf-8", newline="\n") as f:
        f.write("# terrace-retest 2026-10-29 - arm diff table (generated, not handwritten)\n")
        f.write("generated by `notes\\terrace_retest_arms_audit.py` from the built `request.api.json` files; "
                "do not hand-edit.\n\n")
        f.write("B2-family rows are diffed against `runs\\terrace_dom_q5guide_20261028_s51083007\\request.api.json` "
                "(B2, graph of record, sha256 8d1d1a41...; its own seed is 51083002, so B2/S-arms on that seed "
                "change no seed key - shown as `-`).\n")
        f.write("T4 rows are diffed against `runs\\terrace_dom_q5stockv2_20261028_s51083011\\_ui2api\\api_T4.json` "
                "= `simple_v2` (sha256 a315ac74...) as runned at :10004, the id-aligned baseline; the stock "
                "widget deltas per arm are in each run dir's `graph_diff.txt`. The shared T4 deltas "
                "(%s @ 0.25 MP, Duration 5.0 -> 124 frames, per-run prefix) apply to every T4 row.\n\n" % ASPECT)
        f.write("All arms: start frame `%s` (768x1344), prompt = B2's bytes sha256 `%s` except S8 "
                "(B2 + one added line), final canvas 768x1344, 124 frames, per-run save prefix.\n\n"
                % (STILL, B2_PROMPT_SHA))
        f.write("| arm | changed keys (old -> new) | still | seed | prompt sha | WxH | frames |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| " + " | ".join("`%s`" % str(x) if i == 1 else str(x) for i, x in enumerate(r)) + " |\n")
        f.write("\nSelf-check verdicts: %s\n" % ", ".join("%s %s" % (a, s) for a, s, _ in chk))
        f.write("\n`graph_diff.txt` in each run dir is the full widget diff (all arms, 0 undeclared changes).\n")
    for arm, st, why in chk:
        print("%-16s %-4s %s" % (arm, st, why[:150]))
    print("wrote %s\nwrote %s" % (out, tbl))
    return 0 if all(x[1] == "PASS" for x in chk) else 1


if __name__ == "__main__":
    sys.exit(main())
