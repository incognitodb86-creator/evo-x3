r"""ALI-173 B2 CONTINUUM SCENE - builder + offline self-checks (2026-10-23, CPU only).

One arm graph: ComfyUI-H3-Continuum V3.9 (H3ContinuumSamplerV39) doing the CHUNKING itself,
on the same HC1 start still, the same beta6 int8 checkpoint, euler/simple, steps 10, shift
10/3, 24 fps, 1024x576 16:9, chunks 2 x 5.0 s -> assembly target 240 frames (= 10.0 s, the
batch's "240 = 10s"), seed 51140001 = the job id.

WHY 1024x576 AND NOT 832x468: Continuum Manual size must be a multiple of 32
(v3/resolution.py H3_CANVAS_MULTIPLE=32, _manual_dimension RAISES otherwise) and 468 % 32 =
20, so 832x468 is unreachable in this arm; 1024x576 is the other size the batch spec allows.

WHY NO NEGATIVE PROMPT IN THIS ARM: H3ContinuumSamplerV39 has no negative / CFG / CFGGuider
input (its required inputs are model, clip, video_vae, sampler, sigmas, sequence_prompt + the
run/size widgets; the optional list has first/last frame, refs, driving audio, audio_vae). The
README states the model is guidance-free (no CFG, no negative); the extension's own prompt rule
is "negative prompts go in the prose (No: X, Y, Z)", so the HC1 negative block is appended to
sequence_prompt as a `no:` line and the asymmetry is recorded in the ledger.

Sources, all read on this box:
  live schema  C:\AI\community\notes\ali173_b2_object_info_full.json (+ ali173_b2_obj_*.json),
               dumped from :10004 /object_info on 2026-10-23 18:12 CT by notes/ali173_b2_objinfo.py
  extension    ComfyUI\custom_nodes\ComfyUI-H3-Continuum (3.10.2): v3/resolution.py (canvas 32),
               hardening.py:83-88 (target_frames == chunks * chunk_seconds * fps),
               v3/assembly.py (exact_total_duration -> enforce_total_frames(target_frames)),
               temporal.py (frame counts are 17k+5), examples/workflows/MiniMax_H3_Continuum_V39.json
  prompt       C:\AI\community\notes\hc_c1_c0.txt (the approved HC1 v2 pair, c0 half), BQ1 wording
  graph shapes C:\AI\community\notes\ali163_hc_bq1_build.py (attention/shift keys proven on this box)

SELF-DESTRUCT PROBES (Learnings rule "a green check that cannot fail is worthless"): probes()
rebuilds the graph in memory with ten deliberate faults and prints the detector verdicts; every
detector must fire on its fault and every detector must stay silent on the real graph.

NO SPARSE ATTENTION IN THIS GRAPH (finding of this pass, probes prove both halves): the bakeoff
updated ComfyUI to 0.19.2 and the H3 attention nodes changed shape. ModelAttentionBackend now
offers only 'pytorch attention' / 'comfy kitchen attention' (the r3b value 'sparse_blocks',
sparse_size and max_dims are GONE), and BlockSparseAttention's `selection` is
COMFY_DYNAMICCOMBO_V3 whose per-method inputs (sol-attn -> tau, sla/vsa -> keep_percent) are
nested, not top-level: passing tau = "not an input" (static_check rc 2, probe 5), omitting it =
the method's own required input is missing. Consequence for the whole loop: the frozen r3b
request.api.json is schema-STALE on 0.19.2 (nodes 10/11) and must be re-verified before any
HB redo clones it; the community copy of this graph lives in C:\AI\community\runs\<id>\ because
ralph-community\runs\ is gitignored and a `git clean -fdx` at relaunch wipes every graph.
"""
import json, os, re, subprocess, sys, time

W = r"C:\AI\community"
R = r"C:\Users\derek\5slock\ralph-community"
COMFY = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
NOTES = os.path.join(W, "notes")
ID = "ali173_cont_hc1_s51140001"
SEED = 51140001
FPS = 24.0
CHUNKS = 2
CHUNK_SECONDS = 5.0
TARGET_FRAMES = 240            # round(2 * 5.0 * 24) - hardening.py refuses any other number
W_, H_ = 1024, 576
MODEL = "10Eros_Max_h3_8stepTURBO_beta6_int8.safetensors"
STILL = "community/hc/HC1_Two_women_in_studio_editorial.jpg"
SHEET1 = "community/hc/HC1_w1_blonde_00001_.png"
SHEET2 = "community/hc/HC1_w2_darkhair_00001_.png"
REF_SLOT = re.compile(r"reference_image_\d+")
# the GPU guard the harness calls: C:\AI\director\scripts\gpu_guard.ps1, NO arguments (ralph.ps1:51,77),
# rc 0 = IDLE. The first version of this file pointed at a .pi\guard\gpu_guard.mjs path that does not
# exist; there is no such file on this box.
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"
BUDGET = os.path.join(R, "logs", "p7_budget.json")
FULL = os.path.join(NOTES, "ali173_b2_object_info_full.json")
PROMPT_FILE = os.path.join(NOTES, "hc_c1_c0.txt")
# ralph.ps1:284 resolves the run dir as "$C\runs\$id" with $C = C:\AI\community, so the graph lives in
# the COMMUNITY repo (that is where r3b's graph lives). ralph-community\runs\ is never read by the
# harness, it is gitignored there too (.gitignore:13), and a NEW file in ralph-community gets moved to
# _removed by the scope check (ralph.ps1:96) - so there is exactly ONE output dir.
# DURABILITY, checked 2026-10-23: C:\AI\community\runs\ is gitignored (C:/AI/community/.gitignore:10), so
# the graph is on disk but NOT in git, and ralph.ps1 contains NO git clean (grep 'clean -fdx' = 0 hits;
# the scope restore is `git checkout --` on TRACKED ralph-community files, ralph.ps1:110). An untracked
# runs/ file therefore survives iterations, but neither git nor the harness can restore it - re-running
# this builder is the restore, and notes/bakeoff_gpu_events.jsonl carries the graph's sha256.
OUT = os.path.join(W, "runs", ID)
NO_LINE = ("\nno:\ncelebrities, real people, public figures, minors, underage, blood, scat, age play, "
           "bestiality, drugs, watermark, text overlay, logos, extra limbs, deformed hands, frozen frame, "
           "black frames, identity swap, camera cuts, two shots, cuts, scene change\n")


def prompt_text():
    base = open(PROMPT_FILE, encoding="utf-8").read().strip()
    return base + NO_LINE


def graph():
    p = prompt_text()
    g = {
        "147": {"class_type": "UNETLoader", "inputs": {"unet_name": MODEL, "weight_dtype": "default"}},
        "251": {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": ["147", 0], "shift_video": 10.0,
                                                                "shift_audio": 3.0}},
        "142": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                                                       "type": "minimax", "device": "default"}},
        "135": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}},
        "136": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "139": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "153": {"class_type": "BasicScheduler", "inputs": {"model": ["251", 0], "scheduler": "simple",
                                                           "steps": 10, "denoise": 1.0}},
        "188": {"class_type": "PrimitiveStringMultiline", "inputs": {"value": p}},
        "317": {"class_type": "LoadImage", "inputs": {"image": STILL}},
        "345": {"class_type": "LoadImage", "inputs": {"image": SHEET1}},
        "346": {"class_type": "LoadImage", "inputs": {"image": SHEET2}},
        "348": {"class_type": "H3ContinuumReferenceImagesV39", "inputs": {
            "reference_use": "All chunks",
            **{f"reference_r{i}_chunks": "off" for i in range(1, 10)},
            "reference_image_1": ["317", 0], "reference_image_2": ["345", 0], "reference_image_3": ["346", 0]}},
        "312": {"class_type": "H3ContinuumSamplerV39", "inputs": {
            "model": ["251", 0], "clip": ["142", 0], "video_vae": ["135", 0], "sampler": ["139", 0],
            "sigmas": ["153", 0], "sequence_prompt": ["188", 0],
            "prompt_mode": "Fixed", "chunks": CHUNKS, "chunk_seconds": CHUNK_SECONDS,
            "aspect": "Auto from First Image", "preset": "Custom", "custom_mp": round(W_ * H_ / 1e6, 3),
            "continuity": "Balanced \u2014 22 frames", "base_seed": SEED, "audio_continuity": True,
            "diagnostics": "Basic", "reroll_from_chunk": "Auto", "reroll_nonce": 0,
            "strict_compatibility": False, "debug": False, "show_preview": False,
            "run_storage": "Off", "run_name": "", "reference_size": "Match Output", "project_id": "",
            "video_reference_size": "Efficient - 0.4 MP", "continuation_backend": "Standard",
            "generation_mode": "Full Run", "review_action": "Continue / Next", "take_group": 0,
            "take_revision_id": "", "take_action": "Automatic", "size_source": "Manual",
            "width": W_, "height": H_,
            "first_frame": ["317", 0], "audio_vae": ["136", 0], "reference_images": ["348", 0]}},
        "344": {"class_type": "H3DecodeCacheHelper", "inputs": {
            "cache_mode": "Auto", "ram_budget_mb": 512, "disk_budget_gb": 8, "reset_token": 0,
            "video_samples": ["312", 0], "video_vae": ["135", 0], "audio_samples": ["312", 1],
            "audio_vae": ["136", 0]}},
        "306": {"class_type": "H3ContinuumAssembleSeamV35", "inputs": {
            "images": ["344", 0], "audio": ["344", 1], "assembly_plan": ["312", 2],
            "driving_audio": ["312", 4], "exact_total_duration": True, "audio_seam": "Auto",
            "video_seam": "Auto", "buffer_backend": "Auto", "diagnostics": "Basic"}},
        "228": {"class_type": "CreateVideo", "inputs": {"images": ["306", 0], "audio": ["306", 1],
                                                        "fps": FPS, "bit_depth": 8, "color_space": "sRGB",
                                                        "codec": "none"}},
        "191": {"class_type": "SaveVideo", "inputs": {"video": ["228", 0], "format": "auto", "codec": "auto",
                                                      "filename_prefix": f"community/{ID}/{ID}"}},
    }
    return g


def request():
    # ralph.ps1 RunJobs, graph branch (lines 199-297): kind MUST be "graph" and the only keys it reads are
    # id / kind / frames / frames_tol / minutes (minutes clamped 30..180; it becomes the per-attempt
    # timeout minutes*20 s, --max-redo 2). Proven shape on this box = p7/jobs/request_iter09.skipped.json:
    # {"jobs":[{"id":"ali147_pool_promptv2_seg3_s51080002","kind":"graph","frames":481,"frames_tol":0,"minutes":60}]}.
    return {"jobs": [{"id": ID, "kind": "graph", "frames": TARGET_FRAMES, "frames_tol": 33, "minutes": 60,
                      "note":
                f"ALI-173 B2 CONTINUUM SCENE: H3ContinuumSamplerV39 (ComfyUI-H3-Continuum 3.10.2) chunks the clip "
                f"itself - {CHUNKS} x {CHUNK_SECONDS} s = {TARGET_FRAMES} f assembly target, {W_}x{H_} 16:9, "
                f"euler/simple steps 10, shift 10/3, beta6 int8, seed {SEED}, HC1 start still + 2 per-woman sheets "
                f"as Continuum reference_image_1/2/3, one pass, no negative input in this node (no: prose line)."}]}


def detectors(g, full, tag="real"):
    """every detector appends 'PROBLEM ...'; the real graph must produce ZERO."""
    out = []
    P = out.append
    for nid, n in g.items():
        ct = n["class_type"]
        if ct not in full:
            P(f"PROBLEM [{tag}] unknown class_type {ct} (node {nid})")
            continue
        spec = full[ct]["input"]
        # EXACTLY the harness gate's name set (run_graph_job.static_check:38 = required | optional,
        # no "hidden"), so a graph that passes this passes static_check.
        known = set(x for s in ("required", "optional") for x in (spec.get(s) or {}))
        for k in n["inputs"]:
            if k not in known and k.split(".")[0] not in known:
                P(f"PROBLEM [{tag}] {ct} node {nid} key {k} is not an input")
        for r in spec.get("required") or {}:
            if r not in n["inputs"] and not any(k.startswith(r + ".") for k in n["inputs"]):
                P(f"PROBLEM [{tag}] {ct} node {nid} missing required input {r}")
        for k, v in n["inputs"].items():
            if isinstance(v, list) and (len(v) != 2 or str(v[0]) not in g):
                P(f"PROBLEM [{tag}] node {nid} key {k} bad link {v}")
    for nid, n in g.items():                                     # slot bounds (static_check does not check these)
        for k, v in n["inputs"].items():
            if isinstance(v, list) and str(v[0]) in g and full.get(g[str(v[0])]["class_type"]):
                src = g[str(v[0])]
                n_out = len(full[src["class_type"]].get("output") or [])
                if int(v[1]) >= n_out:
                    P(f"PROBLEM [{tag}] node {nid} key {k} links slot {v[1]} of {src['class_type']} (only {n_out} outputs)")
    s = (g.get("312") or {}).get("inputs") or {}
    if not s:
        P(f"PROBLEM [{tag}] no H3ContinuumSamplerV39 node 312 in the graph")
        return out
    if int(round(s["chunks"] * s["chunk_seconds"] * FPS)) != TARGET_FRAMES:
        P(f"PROBLEM [{tag}] assembly target {round(s['chunks'] * s['chunk_seconds'] * FPS)} f != {TARGET_FRAMES} f "
          f"(hardening.py: target_frames must equal chunks * chunk_seconds * fps)")
    if s["size_source"] != "Manual" or s["width"] % 32 or s["height"] % 32:
        P(f"PROBLEM [{tag}] size not Manual/32-aligned: {s['size_source']} {s['width']}x{s['height']}")
    if not (1.70 <= s["width"] / s["height"] <= 1.85):
        P(f"PROBLEM [{tag}] aspect {s['width'] / s['height']:.3f} outside the 1.70-1.85 batch gate")
    if s["base_seed"] != SEED:
        P(f"PROBLEM [{tag}] base_seed {s['base_seed']} != the {SEED} suffix of the id")
    refs = (g.get("348") or {}).get("inputs")
    if refs is None:
        P(f"PROBLEM [{tag}] the Continuum reference node 348 is gone (B2 mandates 3 reference slots)")
    else:
        slots = sorted(k for k in refs if REF_SLOT.fullmatch(k))
        wired = [k for k in slots if isinstance(refs.get(k), list)]
        if len(wired) != 3:
            P(f"PROBLEM [{tag}] Continuum reference slots wired = {wired} (B2 wants 3: start still + 2 sheets)")
    if g["191"]["inputs"]["filename_prefix"] != f"community/{ID}/{ID}":
        P(f"PROBLEM [{tag}] save prefix {g['191']['inputs']['filename_prefix']} != community/{ID}/{ID}")
    p = g["188"]["inputs"]["value"]
    if len(p) < 1500 or "overall_soundscape:" not in p or "non_diegetic_music:" not in p:
        P(f"PROBLEM [{tag}] sequence_prompt too short / missing v2 blocks (len {len(p)})")
    if "minors" not in p or "fictional adult" not in p:
        P(f"PROBLEM [{tag}] content-lock words missing from the prompt")
    for f, d in ((MODEL, "diffusion_models"),
                 ("qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "text_encoders"),
                 ("minimax_h3_video_vae_int8_convrot.safetensors", "vae"),
                 ("minimax_h3_audio_vae_fp32.safetensors", "vae")):
        if not os.path.isfile(os.path.join(COMFY, "models", d, f)):
            P(f"PROBLEM [{tag}] model file not on disk: models/{d}/{f}")
    for img in (STILL, SHEET1, SHEET2):
        if not os.path.isfile(os.path.join(COMFY, "input", img.replace("/", os.sep))):
            P(f"PROBLEM [{tag}] input image not on disk: input/{img}")
    return out


def probes(g, full):
    """self-destruct: each clone must make at least one detector fire."""
    import copy
    cases = {
        "drop the reference node": lambda d: (d.pop("348"), d["312"]["inputs"].pop("reference_images")),
        "chunk_seconds 5.5 (breaks the assembly target)": lambda d: d["312"]["inputs"].__setitem__("chunk_seconds", 5.5),
        "height 468 (not 32-aligned)": lambda d: d["312"]["inputs"].__setitem__("height", 468),
        "bogus key on the sampler (proves this arm has NO negative input)": lambda d: d["312"]["inputs"].__setitem__("negative_prompt", "x"),
        "sparse attention keys from the old 0.17.2 schema": lambda d: d.__setitem__("11", {"class_type": "BlockSparseAttention",
            "inputs": {"model": ["251", 0], "max_kernel_size": 9, "min_sparse_ratio": 0.7, "use_cudnn": False}}),
        "dynamic-combo sub-key tau on BlockSparseAttention": lambda d: d.__setitem__("11", {"class_type": "BlockSparseAttention",
            "inputs": {"model": ["251", 0], "selection": "sol-attn", "tau": 1.3, "start_percent": 0.2,
                        "end_percent": 1.0, "dense_blocks": "", "min_tokens": 12288, "extra_tokens": 256,
                        "sink_conditioning": "exact_kv_and_rows", "verbose": False}}),
        "unknown class H3ContinuumSamplerV40": lambda d: d["312"].__setitem__("class_type", "H3ContinuumSamplerV40"),
        "seed 1234": lambda d: d["312"]["inputs"].__setitem__("base_seed", 1234),
        "save prefix into the ComfyUI root": lambda d: d["191"]["inputs"].__setitem__("filename_prefix", "video/x"),
        "bad slot index (sigmas slot 5)": lambda d: d["312"]["inputs"].__setitem__("sigmas", ["153", 5]),
    }
    rows = []
    for name, mut in cases.items():
        d = copy.deepcopy(g)
        mut(d)
        fired = detectors(d, full, tag="probe")
        rows.append((name, bool(fired), (fired[0][:120] if fired else "")))
    return rows


def main():
    full = json.load(open(FULL, encoding="utf-8"))
    g = graph()
    probs = detectors(g, full)
    print(f"DETECTORS on the real graph: {len(probs)}")
    for m in probs:
        print("  " + m)
    for name, fired, first in probes(g, full):
        print(f"PROBE {'FIRED ' if fired else 'SILENT'} {name}" + (f" -> {first}" if fired else ""))
    os.makedirs(OUT, exist_ok=True)
    # ensure_ascii=True keeps both files pure ASCII (the continuity option carries an em dash), so a
    # locale-dependent reader can never trip the harness CHECK.
    with open(os.path.join(OUT, "request.api.json"), "w", encoding="utf-8") as f:
        json.dump(g, f, indent=1, ensure_ascii=True)
    with open(os.path.join(OUT, "JOB_REQUEST.staged.json"), "w", encoding="utf-8") as f:
        json.dump(request(), f, indent=1, ensure_ascii=True)
    print(f"graph nodes={len(g)} -> {OUT}")
    # run_graph_job.static_check(g) is the harness gate; it takes the graph DICT and GETs
    # /object_info, i.e. it needs ComfyUI awake. detectors() above is its offline clone (same three
    # rules: class in object_info, every key is an input, every required input present) plus slot
    # bounds / frame math / 32-px canvas / seed / ref slots / files-on-disk, checked against the
    # live 18:12 CT dump, so this builder stays CPU-only and re-runnable with ComfyUI asleep.
    print(f"budget now: {json.load(open(BUDGET, encoding='utf-8'))}")
    return 0 if (not probs and all(fired for _, fired, _ in probes(g, full))) else 1


if __name__ == "__main__":
    sys.exit(main())
