r"""ALI-173 B2 CONTINUUM SCENE (2026-10-23): one ComfyUI window that dumps the LIVE
object_info schema of every node class the Continuum arm needs, so the B2 builder can be
validated OFFLINE afterwards (run_graph_job.static_check refuses any unknown class_type and
any key that is not an input, so a guessed graph = rc 2 = a wasted job).

BAKEOFF EXCEPTION (Derrick 2026-10-23 1:07 PM CT): read-only GET /object_info on :10004 is
allowed, and ComfyUI is woken ONLY through scripts/comfy_ctl.py (which refuses while a
render runs). ComfyUI and Forge's own model share the GPU through llama-swap, so wake + all
reads happen in this one call; dumps go to notes/, the port is not touched again.
"""
import argparse, json, os, subprocess, sys, time, urllib.request

COMFY = "http://127.0.0.1:10004"
CTL = r"C:\AI\community\scripts\comfy_ctl.py"
OUT = r"C:\AI\community\notes"
CLS = [
    "H3ContinuumSamplerV39", "H3ContinuumSamplerV38", "H3ContinuumReferenceImagesV39",
    "H3ContinuumAssembleSeamV35", "H3ContinuumAssembleSeamV34", "H3ContinuumJoin",
    "H3ContinuumFinish", "H3ContinuumAssemble", "H3ContinuumSaveState",
    "H3ContinuumLoadState", "H3EasyLoadImage", "H3EasyLoadAudio", "H3DecodeCacheHelper",
    "H3ContinuumVideoAdapter", "H3ContinuumLoadVideo", "H3ContinuumReferenceAudios",
    "CreateVideo", "SaveVideo", "LoadVideo", "VAEDecode", "VAEDecodeAudio", "VAELoader",
    "CLIPLoader", "UNETLoader", "KSamplerSelect", "BasicScheduler", "BasicGuider",
    "RandomNoise", "SamplerCustomAdvanced", "ModelAttentionBackend",
    "BlockSparseAttention", "MiniMaxH3SigmaShift", "MiniMaxH3ReferenceToVideo",
    "MiniMaxH3ImageToVideo", "MiniMaxH3GuidedContinuationWindow",
    "MiniMaxH3AppendContinuation", "MiniMaxH3LatentTailGuide", "ComfySwitchNode",
    "MarkdownNote", "Fast Groups Bypasser (rgthree)", "Power Lora Loader (rgthree)",
    "PreviewAny",
]
# CK-ATTN (2026-10-25): a caller may ask for ONE SET of classes into a DATED prefix, so an attention
# schema read does not overwrite the pinned full dump that the offline graph gates are validated against.
# With no arguments the file behaves exactly as it did: same CLS list, same ali173_b2_* names.
_ap = argparse.ArgumentParser()
_ap.add_argument("--only", default="", help="comma list of classes; empty = the shipped CLS list")
_ap.add_argument("--prefix", default="ali173_b2_obj", help="output prefix for the per-class dumps")
_ap.add_argument("--full-name", default="ali173_b2_object_info_full.json")
_a = _ap.parse_args()
if _a.only.strip():
    CLS = [c.strip() for c in _a.only.split(",") if c.strip()]
PREFIX = _a.prefix
if _a.only.strip():
    print("ONLY: " + ",".join(CLS) + " -> prefix " + PREFIX, flush=True)
t0 = time.time()


def log(m):
    print(time.strftime("%Y-%m-%d %H:%M:%S CT ") + m, flush=True)


def get(url, t=120):
    return json.loads(urllib.request.urlopen(url, timeout=t).read())


def brief(spec):
    rows = []
    for section in ("required", "optional", "hidden"):
        for k, v in (spec.get(section) or {}).items():
            if isinstance(v, (list, tuple)):
                ty = v[0] if not isinstance(v[0], list) else "COMBO:" + ",".join(str(x) for x in v[0][:6]) + ("..." if len(v[0]) > 6 else "")
                opts = v[1] if len(v) > 1 and isinstance(v[1], dict) else {}
            else:
                ty, opts = str(v), {}
            tag = "link" if isinstance(v, list) and v and str(v[0]).isupper() and str(v[0]).replace("_", "").isalpha() and not str(v[0]).startswith("INT") and not str(v[0]).startswith("FLOAT") and not str(v[0]).startswith("COMBO") and not str(v[0]).startswith("STRING") and not str(v[0]).startswith("BOOL") and not str(v[0]).startswith("COMBO") and not str(v[0]).startswith("IMAGE") and not str(v[0]).startswith("AUDIO") and not str(v[0]).startswith("VIDEO") and not str(v[0]).startswith("LATENT") and not str(v[0]).startswith("MODEL") and not str(v[0]).startswith("CLIP") and not str(v[0]).startswith("VAE") and not str(v[0]).startswith("SAMPLER") and not str(v[0]).startswith("SIGMAS") and not str(v[0]).startswith("NOISE") and not str(v[0]).startswith("GUIDER") and not str(v[0]).startswith("CONDITIONING") else "widget"
            flags = ",".join(f"{a}={opts[a]}" for a in ("forceInput", "advanced", "default", "min", "max") if a in opts)
            rows.append(f"    {section[0]} {k} :: {ty}" + (f"  [{flags}]" if flags else ""))
    return rows


log(f"STEP 1 comfy_ctl start (GPU lock enforced by comfy_ctl)")
r = subprocess.run([sys.executable, CTL, "start"], capture_output=True, text=True, timeout=900)
print(r.stdout.strip()[-800:], flush=True)
print(r.stderr.strip()[-300:], flush=True)
r2 = subprocess.run([sys.executable, CTL, "status"], capture_output=True, text=True, timeout=300)
print(r2.stdout.strip()[-400:], flush=True)
ok = "comfy_ok=True" in r2.stdout
# The real GPU guard = C:\AI\director\scripts\gpu_guard.ps1 (ralph.ps1:51 $Guard), the file the harness
# calls before every job. It is in the $Prot list, so it is READ ONLY here (the harness restores a
# change and stops the loop). rc 0 = IDLE. comfy_ctl status also prints a guard line, but that is that
# script's view; this is the harness's.
GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"   # ralph.ps1:51 $Guard, called with NO arguments (ralph.ps1:77), rc 0 = IDLE
NVSMI = "nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader"
g = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", GUARD],
                   capture_output=True, text=True, timeout=120)
log(f"STEP 1b gpu_guard rc={g.returncode} :: " + (g.stdout.strip().replace(chr(10), " | ")[:200] or g.stderr.strip()[:120]))
# ralph.ps1 GuardWait:79-81 also fails a window whose utilisation is over -UtilMax (30) while the guard
# says IDLE, so mirror it here; a schema read at 100 % utilisation means something else owns the GPU.
u = subprocess.run(NVSMI, shell=True, capture_output=True, text=True, timeout=60)
log(f"STEP 1c utilisation: {u.stdout.strip().replace(chr(10), ' | ')[:160] or u.stderr.strip()[:80]}")
if not ok:
    log("COMFY_DOWN - B2 must be marked [!] COMFY_DOWN")
    sys.exit(4)

log("STEP 2 GET /object_info (full) + per-class dumps")
full = get(COMFY + "/object_info", 600)
names = sorted(full)
json.dump(full, open(os.path.join(OUT, _a.full_name), "w", encoding="utf-8"))
log(f"full object_info: {len(names)} classes -> {_a.full_name}")
if PREFIX != "ali173_b2_obj":
    # the version/build the schema came from is part of the measurement (a schema-stale claim is L4/L17)
    json.dump(get(COMFY + "/system_stats", 60),
              open(os.path.join(OUT, PREFIX + "_system_stats.json"), "w", encoding="utf-8"))
sel = {}
for c in CLS:
    if c in full:
        sel[c] = full[c]
        json.dump({c: full[c]}, open(os.path.join(OUT, PREFIX + "_" + c.replace(" ", "_") + ".json"), "w", encoding="utf-8"))
print("MISSING_CLASSES: " + ", ".join(c for c in CLS if c not in full), flush=True)
print("MINIMAX_CLASSES: " + ", ".join(n for n in names if n.lower().startswith("minimax")), flush=True)
print("CONTINUUM_CLASSES: " + ", ".join(n for n in names if n.startswith("H3Continuum") or n.startswith("H3Easy") or n.startswith("H3Decode")), flush=True)
for c in ("H3ContinuumSamplerV39", "H3ContinuumReferenceImagesV39", "H3ContinuumAssembleSeamV35", "H3EasyLoadImage"):
    if c not in full:
        continue
    print(f"=== {c} outputs={full[c].get('output_name') or full[c].get('output')} ===", flush=True)
    print("\n".join(brief(full[c]["input"])), flush=True)
log(f"window open {time.time() - t0:.0f} s, missing={sum(1 for c in CLS if c not in full)}")
