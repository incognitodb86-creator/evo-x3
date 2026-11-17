"""RS4 pre-request check (read-only, CPU only, no GPU call).
Validates the REFSHEET graph the way run_graph_job.py will: adults-only guard on every
prompt string, the sheet LoadImage resolving inside ComfyUI\\input, and the one-variable
invariants (seed 51080000, 768x1344, 24 fps, steps 10, lengths 243 / win1, c0 refs).
Writes nothing; prints only. Run: python notes/ali147_refsheet_rs4_precheck.py
"""
import os, sys, json

SCRIPTS = r"C:/AI/community/scripts"
GRAPH = r"C:/AI/community/runs/ali147_pool_refsheet_s51080000/request.api.json"
COMFY_INPUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/input"
sys.path.insert(0, SCRIPTS)
import comm  # noqa: E402  adults-only guard lives here (scripts/comm.py, not edited)

g = json.load(open(GRAPH, encoding="utf-8"))
prompts = [(k, n["inputs"]["prompt"]) for k, n in g.items() if isinstance(n["inputs"].get("prompt"), str)]
print("prompt_nodes", len(prompts), [k for k, _ in prompts])
for k, p in prompts:
    print("guard", k, "OK" if comm.guard_ok(p) else "GUARD_HIT", "len", len(p), "sha256", __import__("hashlib").sha256(p.encode()).hexdigest())
for k in ("c0", "c1"):
    n = g[k]["inputs"]
    print(k, "class", g[k]["class_type"], "ref_image_size", n["ref_image_size"],
          "ref_image_1", n["ref_images.ref_image_1"], "length", n["length"],
          "w", n["width"], "h", n["height"], "vae", n["vae"], "audio_vae", n["audio_vae"])
for k in ("img", "sheet"):
    name = g[k]["inputs"]["image"]
    path = os.path.join(COMFY_INPUT, name.replace("/", os.sep))
    print(k, "LoadImage", name, "inside_input", os.path.normpath(path).startswith(os.path.normpath(COMFY_INPUT)),
          "exists", os.path.exists(path), "bytes", os.path.getsize(path) if os.path.exists(path) else None)
print("noise_seed", g["noise"]["inputs"]["noise_seed"], "steps", g["s0_sched"]["inputs"]["steps"], g["s1_sched"]["inputs"]["steps"],
      "sampler", g["ksel"]["inputs"]["sampler_name"], "scheduler", g["s0_sched"]["inputs"]["scheduler"],
      "fps", g["mkvid"]["inputs"]["fps"], "shift", g["m_shift"]["inputs"]["shift_video"], g["m_shift"]["inputs"]["shift_audio"])
print("frames_target", 243 + 238 + 22 - 22, "= c0 length 243 + win1 extension_frames", g["win1"]["inputs"]["extension_frames"],
      "overlap_frames", g["win1"]["inputs"]["overlap_frames"])
print("save_prefix", g["save"]["inputs"]["filename_prefix"])
print("nodes", len(g))
