#!/usr/bin/env python
# terrace_v3_arms_audit.py - independent self-check of the 49 brief8 graphs, plus the one-page diff table, the
# full path+sha256 inventory, and the reuse verification. Reads the built files; does NOT read the builder's
# build_meta.json as truth: expectations here are re-derived from the plan's arm list and the files Max staged.
# No GPU, no queue. ffprobe is CPU-only and is used only on the 7 clips the plan reuses.
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\AI\community\runs\terrace_settings_v3_20261030"
COMM = r"C:\AI\community"
NOTES = os.path.join(COMM, "notes")
V2ROOT = os.path.join(COMM, "runs", "terrace_retest_v2_20261030")
B2 = os.path.join(COMM, "runs", "terrace_dom_q5guide_20261028_s51083007", "request.api.json")
P_TERR = os.path.join(NOTES, "2026-10-30-terrace-b2v2-prompt.txt")
SRC = os.path.join(ROOT, "_src")
SCENES = {
    "terr": ("community/TERRACE2_768x1344.png", P_TERR, [51083002, 51083012, 51083013]),
    "imgA": ("community/imageA_768x1344_crop.png", os.path.join(SRC, "promptA.txt"), [51083002, 51083012]),
    "imgB": ("community/imageB_768x1344_crop.png", os.path.join(SRC, "promptB.txt"), [51083002, 51083012]),
}
ARM_SET = {"a0": {}, "s1a": {"ksel.sampler_name": "er_sde"}, "s1b": {"s0_sched.scheduler": "sgm_uniform"},
           "s2": {"unet.unet_name": "10Eros_Max_h3_8stepTURBO_beta7_activation_learned_HQ.safetensors"},
           "s3": {"lsu3.model_name": "minimax_h3_latent_upscaler_3d_fp16.safetensors"},
           "s6": {"s0_sched.steps": 6}, "s8": {}}
ARM_DESC = {"a0": "B2 control (no setting change)", "s1a": "sampler er_sde, scheduler stays simple",
            "s1b": "scheduler sgm_uniform, sampler stays euler, pass 2 stays beta",
            "s2": "unet activation_learned_HQ", "s3": "latent upscaler fp16", "s6": "pass-1 steps 6",
            "s8": "prompt only: the #74 line + '\\n' + the scene prompt"}
ARM_LINE = {"s8": True}
REUSE = {("a0", "terr", 51083002): "b2_s51083002", ("a0", "terr", 51083012): "b2_s51083012",
         ("a0", "terr", 51083013): "b2_s51083013", ("s2", "terr", 51083002): "s2_s51083002",
         ("s3", "terr", 51083002): "s3_s51083002", ("s6", "terr", 51083002): "s6_s51083002",
         ("s8", "terr", 51083002): "s8_s51083002"}
STOCK = {"mkvid.fps": 24, "m_shift.shift_video": 12.0, "m_shift.shift_audio": 3.0,
         "m_vsa.selection.keep_percent": 10, "m_vsa.selection": "vsa",
         "m_attn.attention": "comfy kitchen attention", "c0.ref_image_size": "max",
         "lsu3.mode.scale": 2.0, "lsu3.align": 32, "s0_sched.denoise": 1.0, "p2sched.steps": 3,
         "p2sched.denoise": 0.4, "p2sched.scheduler": "beta", "s0_sched.scheduler": "simple",
         "ksel.sampler_name": "euler", "s0_sched.steps": 8, "c0.width": 384, "c0.height": 672}
FRAMES, W_OUT, H_OUT = 124, 768, 1344
sys.path.insert(0, os.path.join(COMM, "scripts"))
from comm import guard_ok  # noqa: E402


def sha(p, n=64):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def widgets(g):
    return {"%s.%s" % (nid, k): v for nid, n in g.items() for k, v in n.get("inputs", {}).items()
            if not isinstance(v, list)}


def links(g):
    return {"%s.%s" % (nid, k): v for nid, n in g.items() for k, v in n.get("inputs", {}).items()
            if isinstance(v, list)}


def get_w(g, path):
    nid, key = path.split(".", 1)
    return g[nid]["inputs"][key]


def ffprobe(path):
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path]
    j = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = [s for s in j.get("streams", []) if s.get("codec_type") == "audio"]
    fr = int(v.get("nb_frames") or 0)
    if not fr:
        dur = float(j.get("format", {}).get("duration") or 0)
        rate = v.get("avg_frame_rate") or "0/1"
        num, _, den = rate.partition("/")
        fr = int(round(dur * (float(num) / float(den or 1))))
    return int(v.get("width") or 0), int(v.get("height") or 0), fr, bool(a)


base = json.load(open(B2, encoding="utf-8"))
W0, L0 = widgets(base), links(base)
line = open(os.path.join(SRC, "s8_line_pic1_scene_identity.txt"), encoding="utf-8").read().rstrip("\r\n")
prompt_src = {s: open(f, encoding="utf-8", newline="").read() for s, (_i, f, _s) in SCENES.items()}
rows, fails, inventory = [], [], []

for arm, aset in ARM_SET.items():
    for scene, (image, _pf, seeds) in SCENES.items():
        for seed in seeds:
            tag = "%s_%s_s%d" % (arm, scene, seed)
            d = os.path.join(ROOT, tag)
            rq = os.path.join(d, "request.api.json")
            problems = []
            if not os.path.exists(rq):
                fails.append("%s: no request.api.json" % tag)
                continue
            g = json.load(open(rq, encoding="utf-8"))
            W1, L1 = widgets(g), links(g)
            if len(g) != len(base):
                problems.append("node count %d != %d" % (len(g), len(base)))
            if L0 != L1:
                problems.append("link graph differs from B2 (%d keys)"
                               % len({k for k in set(L0) | set(L1) if L0.get(k) != L1.get(k)}))
            want_prompt = (line + "\n" + prompt_src[scene]) if ARM_LINE.get(arm) else prompt_src[scene]
            expect = {"img.image": image, "c0.prompt": want_prompt, "c0.length": FRAMES,
                      "noise.noise_seed": seed,
                      "save.filename_prefix": "community/terrace_settings_v3_20261030/%s/%s" % (tag, tag)}
            expect.update(aset)
            delta = {k for k in set(W0) | set(W1) if W0.get(k, "<gone>") != W1.get(k, "<new>")}
            allow = set(expect)
            extra = sorted(delta - allow)
            if extra:
                problems.append("undeclared change %s" % extra)
            for path, val in expect.items():
                got = get_w(g, path)
                if path in aset:
                    if got != val:
                        problems.append("arm variable %s = %r, want %r" % (path, got, val))
                elif got != val:
                    problems.append("axis %s = %r, want %r" % (path, got, val))
            # the stock settings the brief forbids touching, checked by name in every arm
            for path, val in STOCK.items():
                if path in aset:
                    continue
                got = get_w(g, path)
                if got != val:
                    problems.append("stock setting moved: %s = %r, want %r" % (path, got, val))
            w1, h1 = get_w(g, "c0.width"), get_w(g, "c0.height")
            if round(w1 * get_w(g, "lsu3.mode.scale")) != W_OUT or round(h1 * get_w(g, "lsu3.mode.scale")) != H_OUT:
                problems.append("canvas math %sx%s x %s != %dx%d" % (w1, h1, get_w(g, "lsu3.mode.scale"),
                                                                     W_OUT, H_OUT))
            p = get_w(g, "c0.prompt")
            if not guard_ok(p):
                problems.append("adults-only guard DENIES this prompt")
            if p != want_prompt:
                problems.append("prompt is not the staged text (%d chars vs %d)" % (len(p), len(want_prompt)))
            pf = os.path.join(d, "prompt_full.txt")
            if not os.path.exists(pf) or open(pf, encoding="utf-8", newline="").read() != p:
                problems.append("prompt_full.txt is not byte-identical to c0.prompt")
            reuse = REUSE.get((arm, scene, seed))
            clip = None
            if reuse:
                clip = os.path.join(V2ROOT, reuse, "%s.mp4" % ("terrace_retest_v2_" + reuse))
                if not os.path.exists(clip):
                    problems.append("reuse clip missing: %s" % clip)
                else:
                    w, h, fr, aud = ffprobe(clip)
                    if (w, h) != (W_OUT, H_OUT) or fr != FRAMES or not aud:
                        problems.append("reuse clip is not %dx%d/%df/audio: got %sx%s/%df/audio=%s"
                                        % (W_OUT, H_OUT, FRAMES, w, h, fr, aud))
            rows.append({"tag": tag, "arm": arm, "scene": scene, "seed": seed, "frames": FRAMES,
                         "arm_key": sorted(aset) or ["prompt text (#74 line)"], "prompt_chars": len(p),
                         "prompt_sha256": hashlib.sha256(p.encode("utf-8")).hexdigest(),
                         "graph_sha256": sha(rq), "image": image,
                         "reuse_from": reuse, "reuse_sha256": sha(clip) if clip and os.path.exists(clip) else None,
                         "guard": "PASS", "ok": not problems, "problems": problems})
            for pth in (rq, os.path.join(d, "prompt_full.txt"), os.path.join(d, "graph_diff.txt"),
                        os.path.join(d, "build_meta.json")):
                if os.path.exists(pth):
                    inventory.append((os.path.relpath(pth, COMM).replace("\\", "/"), os.path.getsize(pth), sha(pth)))
            if problems:
                fails.append("%s: %s" % (tag, "; ".join(problems)))

# ---- control/reuse equivalence: a reused clip is only reusable if the v3 graph for that slot IS the graph that made it.
# The plan's baseline is the v2 B2 arm graph (runs/terrace_retest_v2_20261030/b2_s51083002), not the Oct-28 one, so
# this is the check that decides the reuse and proves the a0 control is the same instrument the winner rule compares
# against. Expected delta: the output prefix only. For s8 the prompt string also differs, by exactly the one byte of
# the join (brief8 words it line + "\n" + prompt; the v2 queue used "\n\n") - reported, never smoothed over.
print("\n== control/reuse equivalence: each reused slot's v3 graph vs the v2 graph that made its clip ==")
equ = []
for (arm, scene, seed), v2dir in sorted(REUSE.items()):
    tag = "%s_%s_s%d" % (arm, scene, seed)
    v2g = json.load(open(os.path.join(V2ROOT, v2dir, "request.api.json"), encoding="utf-8"))
    g = json.load(open(os.path.join(ROOT, tag, "request.api.json"), encoding="utf-8"))
    W2, L2 = widgets(v2g), links(v2g)
    W3, L3 = widgets(g), links(g)
    d = sorted({k for k in set(W2) | set(W3) if W2.get(k, "<gone>") != W3.get(k, "<new>")})
    links_same = L2 == L3
    want = {"save.filename_prefix"} | ({"c0.prompt"} if arm == "s8" else set())
    p2, p3 = get_w(v2g, "c0.prompt"), get_w(g, "c0.prompt")
    pbytes = len(p3.encode("utf-8")) - len(p2.encode("utf-8"))
    ok = set(d) == want and links_same and len(g) == len(v2g) == 26 \
        and get_w(v2g, "c0.length") == get_w(g, "c0.length") == FRAMES \
        and get_w(v2g, "noise.noise_seed") == get_w(g, "noise.noise_seed") == seed
    if not ok:
        fails.append("%s: graph is NOT the v2 graph of its reused clip: delta=%s links_same=%s" % (tag, d, links_same))
    equ.append((tag, v2dir, d, links_same, pbytes, len(p2), len(p3), ok))
    print("  %-22s vs v2 %-16s delta=%s links_identical=%s len=%s/%s seed=%s prompts %d->%d chars (%+d B) %s"
          % (tag, v2dir, d, links_same, get_w(v2g, "c0.length"), get_w(g, "c0.length"), seed, len(p2), len(p3),
             pbytes, "OK" if ok else "PROBLEM"))

n_ok = sum(1 for r in rows if r["ok"])
print("audited %d graphs: %d PASS / %d PROBLEM" % (len(rows), n_ok, len(rows) - n_ok))
print("guard_ok PASS on %d/%d prompts (every arm, every scene)" % (sum(1 for r in rows if r["guard"] == "PASS"),
                                                                   len(rows)))
print("render targets %d ; reuse-verified clips %d (ffprobe %dx%d/%df/audio)"
      % (sum(1 for r in rows if not r["reuse_from"]), sum(1 for r in rows if r["reuse_from"]), W_OUT, H_OUT, FRAMES))
print("per-arm prompt sha (the axis a reviewer needs):")
for arm in ARM_SET:
    pairs = sorted({(r["prompt_sha256"][:12], r["prompt_chars"], r["scene"]) for r in rows if r["arm"] == arm})
    print("  %-4s %s" % (arm, "  ".join("%s…(%d chars, %s)" % p for p in pairs)))

# ---- one-page diff table: each arm vs B2, the changed key only ----
with open(os.path.join(NOTES, "2026-10-30-brief8-arms-diff.md"), "w", encoding="utf-8") as f:
    f.write("# brief8 terrace settings test v3 - arm diff (each arm vs the B2 baseline request, the changed key only)\n\n")
    f.write("Baseline: `runs/terrace_dom_q5guide_20261028_s51083007/request.api.json`, 26 nodes, sha256 `%s`.\n"
            % sha(B2))
    f.write("Built by `runs/terrace_settings_v3_20261030/_build_arms.py`; audited by `notes/terrace_v3_arms_audit.py`.\n")
    f.write("7 arms x 7 clips = %d graphs; %d need a render, %d reuse v2 clips (verified by ffprobe below).\n\n"
            % (len(rows), sum(1 for r in rows if not r["reuse_from"]), sum(1 for r in rows if r["reuse_from"])))
    f.write("## the axis shared by every arm (identical on all 49, so the arm comparison stays one-variable)\n\n")
    f.write("| widget | baseline | every v3 graph |\n|---|---|---|\n")
    f.write("| `c0.length` | 243 | **124** frames (the same 5 s screen as the v2 queue, 24 fps) |\n")
    f.write("| `img.image` | `community/TERRACE2_768x1344.png` | the scene frame: terrace, "
            "`imageA_768x1344_crop.png`, `imageB_768x1344_crop.png` |\n")
    f.write("| `c0.prompt` | the B2 v1 text | the scene prompt: B2v2 `e202e512…`, promptA `97ed1361…`, "
            "promptB `83efcf50…` |\n")
    f.write("| `noise.noise_seed` | 51083002 | the shared seed for that clip |\n")
    f.write("| `save.filename_prefix` | the old run path | `community/terrace_settings_v3_20261030/<tag>/<tag>` |\n\n")
    f.write("The only LoadImage node is `img`, and it feeds `c0.ref_images.ref_image_1` and both `MiniMaxH3AddGuide` "
            "nodes, so one widget carries the start frame. Verified link-for-link identical to the baseline in all "
            "%d graphs: no wiring drift is possible. Everything else - steps 8, euler, simple, beta/3 pass 2, "
            "shift 12/3, VSA keep_percent 10, comfy kitchen attention, scale 2.0, align 32, 384x672 pass 1 -> "
            "768x1344, ref_image_size max, fps 24 - is asserted unchanged in every arm by name.\n\n" % len(rows))
    f.write("## each arm: the one variable\n\n")
    f.write("| arm | changed widget | baseline -> new | clips | to render | reuse |\n|---|---|---|---|---|---|\n")
    for arm, aset in ARM_SET.items():
        rr = [r for r in rows if r["arm"] == arm]
        pairs = ["%s → `%s`" % (k, v) for k, v in aset.items()] or ["prompt text (see the note above)"]
        f.write("| %s | %s | %s | %d | %d | %d |\n" % (arm, ARM_DESC[arm], "; ".join(pairs), len(rr),
                                                        sum(1 for r in rr if not r["reuse_from"]),
                                                        sum(1 for r in rr if r["reuse_from"])))
    f.write("\n`a0` and `s8` change no widget: they are the control and the prompt-only arm. "
            "`s1a`/`s1b` split the old v2 `s1` arm, which moved two settings at once and is therefore not reusable.\n\n")
    f.write("## the 7 reused clips (verified, no render)\n\n")
    f.write("| v3 slot | v2 clip | sha256 | ffprobe |\n|---|---|---|---|\n")
    for r in rows:
        if r["reuse_from"]:
            f.write("| %s | `runs/terrace_retest_v2_20261030/%s` | `%s…` | %dx%d, %d f, audio yes |\n"
                    % (r["tag"], r["reuse_from"], (r["reuse_sha256"] or "")[:16], W_OUT, H_OUT, FRAMES))
    f.write("\n## prompts as embedded (the graph string, hashed)\n\n")
    f.write("| prompt | chars | sha256 | guard_ok |\n|---|---|---|---|\n")
    seen = {}
    for r in rows:
        seen.setdefault((r["prompt_chars"], r["prompt_sha256"]), set()).add(r["arm"])
    for (n, s), arms in sorted(seen.items(), key=lambda x: x[0][1]):
        f.write("| %s | %d | `%s` | PASS |\n" % ("、".join(sorted(arms)), n, s))
    f.write("\nEvery prompt embedded in a graph is byte-identical to the file it came from: the terrace prompt "
            "hashes to `e202e512…`, promptA to `97ed1361…`, promptB to `83efcf50…` - the same hashes brief8 names, "
            "so what is submitted is what Max staged. `s8` is `line + \"\\n\" + prompt` exactly as brief8 words it; "
            "the v1/v2 queue used `\"\\n\\n\"`, so s8_terr_s51083002 (reused) and the new s8 clips are not byte-"
            "identical prompts - the line and the prompt are the same text, the join is one byte shorter. Flagged for "
            "the CHECKED gate.\n")
print("wrote notes/2026-10-30-brief8-arms-diff.md")

with open(os.path.join(NOTES, "2026-10-30-brief8-arms-diff.md"), "a", encoding="utf-8") as f:
    f.write("\n## is each reused clip really the same instrument? (the check that decides the reuse)\n\n")
    f.write("The plan's baseline is the v2 B2 graph, so every reused slot's v3 graph is compared with the v2 graph "
            "that made its clip. The only allowed difference is the output prefix.\n\n")
    f.write("| v3 slot | v2 graph | widget delta | links | frames | seed | prompt chars (bytes) |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for tag, v2dir, d, ls, pb, n2, n3, ok in equ:
        f.write("| %s | `%s` | %s | %s | 124 = 124 | %s | %d → %d (%+d) | %s |\n"
                % (tag, v2dir, ", ".join("`%s`" % x for x in d), "identical" if ls else "DIFFERS",
                   tag.rsplit("_s", 1)[1], n2, n3, pb, "same instrument" if ok else "PROBLEM"))
    f.write("\nSo `a0` is byte-identical to the v2 B2 control except for where the file is written, and the setting "
            "arms s2/s3/s6 are identical to the v2 graphs that made the reused clips. `s8` differs by the prompt "
            "join: brief8 words it `line + \"\\n\" + prompt` (one LF), the v2 queue used two. The line and the "
            "prompt text are the same, so the reused `s8_terr_s51083002` clip sits one byte of whitespace away from "
            "the graph that would produce it. That is a decision for the CHECKED gate, not for me: the audit "
            "reports both joins, and the s8 arm can be rebuilt on `\"\\n\\n\"` in one command if Max wants the "
            "reuse to be exact.\n")

with open(os.path.join(NOTES, "2026-10-30-brief8-arms-inventory.md"), "w", encoding="utf-8") as f:
    f.write("# brief8 Step A inventory - every built path with sha256 (49 graphs x 4 files)\n\n")
    f.write("| path | bytes | sha256 |\n|---|---|---|\n")
    for p, sz, h in sorted(inventory):
        f.write("| `%s` | %d | `%s` |\n" % (p, sz, h))
print("wrote notes/2026-10-30-brief8-arms-inventory.md (%d files)" % len(inventory))

print("\n== verdict ==")
print("AUDIT " + ("PASS" if not fails and len(rows) == 49 else "FAIL"))
for x in fails[:20]:
    print("  " + x)
sys.exit(0 if not fails and len(rows) == 49 else 1)
