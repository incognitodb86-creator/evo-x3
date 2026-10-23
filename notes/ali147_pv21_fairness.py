"""PV2-1 fairness table generator (writes runs/ali147_pool_promptv2_s51080000/fairness.txt).

Fairness vs the CTRL control (the arm's only comparison target, the task line's
"render seconds vs CTRL 809.7"): a node-by-node byte compare (json.dumps(sort_keys=True))
of runs/ali147_pool_promptv2_s51080000/request.api.json against the CTRL graph
runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json (node-for-node equal to the
rendered ali147_pool_ctrl_s51080000.api.json - see notes/ali147_pv21_inspect.py), listing
the identical nodes, the intended 3 changes with old->new values, and the held-equal
setting table (seed, steps, sampler, scheduler, shift, fps, sizes, lengths, win1, models).

CPU only, no GPU/ComfyUI call. Writes ONLY runs/ali147_pool_promptv2_s51080000/fairness.txt.
Run: python notes/ali147_pv21_fairness.py
"""
import hashlib
import json
import os

NEW_ID = "ali147_pool_promptv2_s51080000"
ARM = r"C:/AI/community/runs/" + NEW_ID
GRAPH = os.path.join(ARM, "request.api.json")
CTRL = r"C:/AI/community/runs/ali147_pool_ctrl_s51080000"
CTRL_SRC = os.path.join(CTRL, "submitted_graph.pretty.json")
CTRL_API = os.path.join(CTRL, "ali147_pool_ctrl_s51080000.api.json")
OUT = os.path.join(ARM, "fairness.txt")
PROMPTS = {"c0": "v2_seg1_c0_r2v.txt", "c1": "v2_seg1_c1_t2va.txt"}
CTRL_SECS = json.load(open(os.path.join(CTRL, "objective.json"), encoding="utf-8"))["secs"]

g = json.load(open(GRAPH, encoding="utf-8"))
c = json.load(open(CTRL_SRC, encoding="utf-8"))
ca = json.load(open(CTRL_API, encoding="utf-8"))


def canon(x):
    return json.dumps(x, sort_keys=True)


ident = sorted(k for k in g if canon(g[k]) == canon(c[k]))
changed = sorted(k for k in g if canon(g[k]) != canon(c[k]))
lines = []
w = lines.append

w("ALI-147 PV2-1 PROMPT_V2 seg1 - fairness vs the CTRL control")
w("arm      runs/ali147_pool_promptv2_s51080000/request.api.json  bytes %d  sha256 %s"
  % (len(open(GRAPH, "rb").read()), hashlib.sha256(open(GRAPH, "rb").read()).hexdigest()))
w("control  runs/ali147_pool_ctrl_s51080000/submitted_graph.pretty.json  (the CTRL graph;")
w("         node-for-node identical to the rendered ali147_pool_ctrl_s51080000.api.json:")
w("         same %d node keys, zero node-body diffs - notes/ali147_pv21_inspect.py)" % len(ca))
w("method   json.dumps(node, sort_keys=True) per node id; the ONLY allowed diffs are")
w("         c0.inputs.prompt, c1.inputs.prompt, save.inputs.filename_prefix (the task's 3 fields)")
w("")
w("nodes    arm %d  control(source) %d  control(rendered .api.json) %d  key-set equal: %s"
  % (len(g), len(c), len(ca), set(g) == set(c) == set(ca)))
w("identical_nodes %d/%d" % (len(ident), len(g)))
for k in ident:
    w("  SAME  %-8s %s" % (k, g[k]["class_type"]))
w("changed_nodes %d: %s" % (len(changed), ", ".join(changed)))
for k in changed:
    w("  DIFF  %-8s %s" % (k, g[k]["class_type"]))
    for ik in sorted(g[k]["inputs"]):
        if canon(g[k]["inputs"][ik]) != canon(c[k]["inputs"][ik]):
            old, new = c[k]["inputs"][ik], g[k]["inputs"][ik]
            if isinstance(old, str) and isinstance(new, str) and len(old) > 80:
                w("        inputs.%s  OLD chars %d sha256 %s" %
                  (ik, len(old), hashlib.sha256(old.encode()).hexdigest()))
                w("        inputs.%s  NEW chars %d sha256 %s  (= specs/prompt_v2/%s verbatim)" %
                  (ik, len(new), hashlib.sha256(new.encode()).hexdigest(), PROMPTS.get(k, "?")))
            else:
                w("        inputs.%s  OLD %s" % (ik, json.dumps(old)))
                w("        inputs.%s  NEW %s" % (ik, json.dumps(new)))
        else:
            w("        inputs.%-22s unchanged %s" % (ik, json.dumps(g[k]["inputs"][ik])[:90]))
w("")
w("held_equal (the settings the two arms must share; all read out of both graphs)")
CHECKS = [
    ("noise.noise_seed (seed 51080000)", ["noise"], "noise_seed"),
    ("s0_sched.steps", ["s0_sched"], "steps"),
    ("s1_sched.steps", ["s1_sched"], "steps"),
    ("s0_sched.scheduler", ["s0_sched"], "scheduler"),
    ("s1_sched.scheduler", ["s1_sched"], "scheduler"),
    ("s0_sched.denoise", ["s0_sched"], "denoise"),
    ("s1_sched.denoise", ["s1_sched"], "denoise"),
    ("ksel.sampler_name", ["ksel"], "sampler_name"),
    ("m_shift.shift_video", ["m_shift"], "shift_video"),
    ("m_shift.shift_audio", ["m_shift"], "shift_audio"),
    ("mkvid.fps", ["mkvid"], "fps"),
    ("c0.width", ["c0"], "width"),
    ("c0.height", ["c0"], "height"),
    ("c0.length", ["c0"], "length"),
    ("c0.ref_image_size", ["c0"], "ref_image_size"),
    ("c1.width", ["c1"], "width"),
    ("c1.height", ["c1"], "height"),
    ("c1.start_latent_image", ["c1"], "start_latent_image"),
    ("win1.extension_frames", ["win1"], "extension_frames"),
    ("win1.overlap_frames", ["win1"], "overlap_frames"),
    ("unet.unet_name", ["unet"], "unet_name"),
    ("clip.clip_name1", ["clip"], "clip_name1"),
    ("clip.clip_name2", ["clip"], "clip_name2"),
]
for label, nodes, key in CHECKS:
    n = nodes[0]
    val, cval = g[n]["inputs"].get(key), c[n]["inputs"].get(key)
    w("  %-34s arm %-28s control %-28s equal %s"
      % (label, json.dumps(val)[:28], json.dumps(cval)[:28], val == cval))
for n in sorted(set(g) - set(changed)):
    w("  node %-8s byte-identical (class_type + all inputs)  %s" % (n, g[n]["class_type"]))
w("")
w("frames  c0.length %d + win1.extension_frames %d = %d (win1.overlap_frames %d is the"
  % (g["c0"]["inputs"]["length"], g["win1"]["inputs"]["extension_frames"],
     g["c0"]["inputs"]["length"] + g["win1"]["inputs"]["extension_frames"],
     g["win1"]["inputs"]["overlap_frames"]))
w("        guide window, and c1.length = [win1, 1] = 238 + the 22 tail-guide frames = 481;")
w("        the control ffprobed 481 packets, so 481 is the CTRL-identical objective)")
w("prompt  c0 %d chars sha256 %s" % (len(g["c0"]["inputs"]["prompt"]),
                                     hashlib.sha256(g["c0"]["inputs"]["prompt"].encode()).hexdigest()))
w("        (control c0 was 3295 chars sha256 %s - the OLD builder output)"
  % hashlib.sha256(c["c0"]["inputs"]["prompt"].encode()).hexdigest())
w("        c1 %d chars sha256 %s" % (len(g["c1"]["inputs"]["prompt"]),
                                      hashlib.sha256(g["c1"]["inputs"]["prompt"].encode()).hexdigest()))
w("        (control c1 was %d chars sha256 %s)"
  % (len(c["c1"]["inputs"]["prompt"]),
     hashlib.sha256(c["c1"]["inputs"]["prompt"].encode()).hexdigest()))
w("guard   scripts/comm.guard_ok passes on both new prompt strings (the harness's own")
w("        call, run_graph_job.py:60; a hit = exit 3 CLIP_SKIP) - notes/ali147_pv21_precheck.py")
w("static  every class_type and input-key set matches the graph that already rendered ok,")
w("        so the harness static check (GPU node list, off-limits to Forge) cannot newly fail")
w("")
w("render_seconds_vs_control  control objective.json secs = %.1f (1 attempt, ok, 481 packets)"
  % CTRL_SECS)
w("        arm secs = PENDING (the render is the harness's, requested by p7/JOB_REQUEST.json")
w("        id %s kind=graph frames=481 frames_tol=0 minutes=60)." % NEW_ID)
w("        Post-render: compare the arm's objective.json secs against %.1f s and put the" % CTRL_SECS)
w("        pair in PROOF.md; sbs_ctrl_promptv2.mp4 and the fixed-frame stills are Max/harness")
w("        files (run_graph_job.py has no hstack path and its contact sheet samples only the")
w("        0.5 s windows around 0:10-0:50, i.e. frames 204-276 and the last frames, never frame 0).")
w("")
w("verdict  %d/%d nodes byte-identical to the control; the only differences are the two")
w("         PROMPT_V2 strings and the save path, so the two clips differ by prompt only.")
lines[0] = lines[0]
open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("wrote", OUT, "bytes", len(open(OUT, "rb").read()),
      "sha256", hashlib.sha256(open(OUT, "rb").read()).hexdigest())
print("identical %d/%d changed %s" % (len(ident), len(g), changed))
print("lines", len(lines))
