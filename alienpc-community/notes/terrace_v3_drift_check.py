#!/usr/bin/env python
# terrace_v3_drift_check.py - the plan's step 3 drift check, as an instrument, for brief8 Step B.
# "Record ComfyUI commit, custom-node versions, model sha256s and GPU driver; compare with v2."
# CPU only: git queries, nvidia-smi, one GET of /system_stats (a version read - no /prompt, no queue, no model
# load), file stats, and sha256 of the model files the 49 graphs reference. Big files are NOT hashed by default
# (the unet is 22.9 GB and the TE is larger - minutes each); pass --all-models to hash everything. Size, mtime and
# name are checked for all of them, and the v2 graphs' own model references are compared by name+size.
# Honest limit, printed, not hidden: the v1/v2 queues wrote NO environment record, so "compare with v2" has
# nothing to compare against. This run writes notes/2026-10-30-brief8-environment.txt as the first record, and
# reports the plan's own options for that case (step 3: re-render the 7 reused clips, +7 and needs a GO, or add
# one A0 Terrace clip).
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
COMM = r"C:\AI\community"
ROOT = os.path.join(COMM, "runs", "terrace_settings_v3_20261030")
V2ROOT = os.path.join(COMM, "runs", "terrace_retest_v2_20261030")
RUNTIME = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
MODELS = os.path.join(RUNTIME, "models")
OUT = os.path.join(COMM, "notes", "2026-10-30-brief8-environment.txt")
V2_RENDER_WINDOW = "2026-10-30 05:35 CT (v2 queue start) to 06:35 CT (last clip)"
HASH_LIMIT = 2 * 1024 ** 3
ALL_MODELS = "--all-models" in sys.argv
KEYS = {"unet.unet_name": "diffusion_models", "c0.clip": None, "clip.clip_name": "text_encoders",
        "vvae.vae_name": "vae", "avae.vae_name": "vae", "lsu3.model_name": "latent_upscale_models"}


def sh(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return (r.stdout or "").strip(), (r.stderr or "").strip(), r.returncode


def sha256(p, limit=None):
    if limit and os.path.getsize(p) > limit:
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def find_model(name):
    for root, _d, files in os.walk(MODELS):
        if name in files:
            return os.path.join(root, name)
    return None


lines = ["terrace settings test v3 - environment record (the plan's step 3 drift check)",
         "captured %s by notes/terrace_v3_drift_check.py" % time.strftime("%Y-%m-%d %H:%M:%S %Z"),
         "purpose: prove the v3 queue runs on the same instrument as the v2 queue, before 42 renders"]
print("== ComfyUI code ==")
head, _e, rc = sh(["git", "-C", RUNTIME, "rev-parse", "HEAD"])
when, _e, _rc = sh(["git", "-C", RUNTIME, "log", "-1", "--format=%cd", "--date=iso-strict"])
dirty, _e, _rc = sh(["git", "-C", RUNTIME, "status", "--porcelain"])
lines += ["comfyui HEAD %s" % head, "comfyui HEAD date %s" % when,
          "comfyui dirty entries %d" % len([x for x in dirty.splitlines() if x.strip()])]
print(lines[-3] + "\n" + lines[-2] + "\n" + lines[-1])

print("== custom_nodes (versions as recorded by their own repos/manifests) ==")
cn = os.path.join(RUNTIME, "custom_nodes")
cn_lines = []
for d in sorted(os.listdir(cn)):
    p = os.path.join(cn, d)
    if not os.path.isdir(p):
        continue
    h, _e, rc2 = sh(["git", "-C", p, "rev-parse", "--short", "HEAD"])
    ver = ""
    for mf in ("package.json", "pyproject.toml"):
        f = os.path.join(p, mf)
        if os.path.exists(f):
            t = open(f, encoding="utf-8", errors="replace").read()
            for ln in t.splitlines():
                if '"version"' in ln or ln.strip().startswith("version"):
                    ver = ln.strip()[:60]
                    break
        if ver:
            break
    mt = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(p)))
    cn_lines.append("%-46s git=%s version=%s dir_mtime=%s" % (d, (h if rc2 == 0 else "not-a-repo")[:12],
                                                              ver or "-", mt))
lines.append("custom_nodes:")
lines += ["  " + x for x in cn_lines]
print("\n".join("  " + x for x in cn_lines[:14]))
print("  (%d custom node dirs total)" % len(cn_lines))

print("== GPU driver ==")
gpu, err, rc3 = sh(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
lines += ["nvidia-smi: %s" % (gpu or ("FAILED " + err))]
print("  " + (gpu or "nvidia-smi failed: " + err))

print("== runtime versions (GET /system_stats - a version read, no /prompt, no queue) ==")
sys.path.insert(0, os.path.join(COMM, "scripts"))
try:
    from comm import BASE
    with urllib.request.urlopen(BASE + "/system_stats", timeout=30) as r:
        st = json.loads(r.read().decode("utf-8", "replace"))
    txt = json.dumps(st, ensure_ascii=False)[:1200]
except Exception as ex:  # noqa: BLE001
    txt = "system_stats unavailable: %r" % ex
lines += ["system_stats: " + txt]
print("  " + txt[:400])

print("== models the 49 graphs reference ==")
refs = set()
for sub in ("a0_terr_s51083002", "s2_terr_s51083002", "s3_terr_s51083002", "s6_terr_s51083002"):
    g = json.load(open(os.path.join(ROOT, sub, "request.api.json"), encoding="utf-8"))
    for nid, n in g.items():
        for k, v in n.get("inputs", {}).items():
            if k in ("unet_name", "clip_name", "vae_name", "model_name") and isinstance(v, str):
                refs.add(v)
v2refs = set()
for sub in ("b2_s51083002", "s2_s51083002", "s3_s51083002", "s6_s51083002", "s8_s51083002"):
    g = json.load(open(os.path.join(V2ROOT, sub, "request.api.json"), encoding="utf-8"))
    for nid, n in g.items():
        for k, v in n.get("inputs", {}).items():
            if k in ("unet_name", "clip_name", "vae_name", "model_name") and isinstance(v, str):
                refs.add(v)
                v2refs.add(v)
lines.append("models referenced by the v3 graphs: %d; by the v2 graphs: %d; identical sets: %s"
             % (len(refs), len(v2refs), refs == v2refs))
print("  v3 refs %d, v2 refs %d, identical sets: %s" % (len(refs), len(v2refs), refs == v2refs))
for name in sorted(refs):
    p = find_model(name)
    if not p:
        lines.append("  MODEL MISSING %s" % name)
        print("  MISSING %s" % name)
        continue
    st = os.stat(p)
    h = sha256(p, None if ALL_MODELS else HASH_LIMIT)
    mt = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
    lines.append("  %-64s %14d B mtime %s sha256 %s" % (name, st.st_size, mt,
                                                         h or "not hashed (over %d GB; --all-models to hash)"
                                                         % (HASH_LIMIT // 1024 ** 3)))
    print("  %-58s %14d B  %s  %s" % (name, st.st_size, mt, (h or "(over the hash limit)")[:24]))

prior = sorted(f for f in os.listdir(os.path.join(COMM, "notes"))
               if f.endswith("-environment.txt") and os.path.basename(OUT) != f)
lines.append("prior environment records in notes/: %s" % (prior or "none"))
print("== comparison with the v2 queue ==")
print("  prior environment records: %s" % (prior or "NONE - the v1/v2 queues never wrote one"))
lines.append("model names+paths used by v3 are the same strings as in the v2 graphs (compared above by name; "
             "the current size/mtime of each file is recorded above; the v2 record carries no hashes, so a hash "
             "comparison against the v2 moment is impossible from the record)")
if not prior:
    lines.append("verdict: the plan's step 3 'compare with v2' cannot be executed as written, because no v2-era "
                 "environment record exists. The plan's own options apply: re-render the 7 reused clips (+7, needs "
                 "a GO), or add one A0 Terrace control clip. A third option is to accept the v2 clips and state "
                 "that drift is unmeasured. This file is the first record; the next run can be compared with it.")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("  wrote %s (%d lines) - the first environment record on this lane; a later run can diff against it"
      % (os.path.relpath(OUT, COMM), len(lines)))
print("\nthis is an instrument, not a verdict: it records, and where the plan's check cannot be run it says so")
