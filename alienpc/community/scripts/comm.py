# Community-path helper (ALI-52 P2-P6). Stock ComfyUI API only; Switchyard untouched.
import json, os, re, sys, time, shutil, urllib.request, urllib.error, datetime, hashlib
W = r"C:\AI\community"
C = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI"
LS = "http://127.0.0.1:8080"
BASE = LS + "/comfyui"
UNET = "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors"
TE = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VVAE = "minimax_h3_video_vae_int8_convrot.safetensors"
AVAE = "minimax_h3_audio_vae_fp32.safetensors"
ANTIBURN = "h3_antiburn_universal_v1.safetensors"
# RENDER-TIMEOUT (2026-10-26): llama-swap queues a request behind a model start, and its own budget for that is
# healthCheckTimeout (1200 in the live C:/AI/director/config/llama-swap.yaml:5); the published rule is "set client
# timeouts high enough for the queue and load time" (docs/kb/guides/routing/capacity-and-queues.md, saved body
# C:/AI/community/notes/web/rt_ls_capacity-and-queues.txt:16-20). Measured with the old 60 s / 30 s: the POST /prompt
# died at 60 s while llama-swap was starting comfyui_auto (briefs/agy_monitor.log 2026-10-24 22:36, "TimeoutError:
# timed out at comm.run BASE/prompt" for ali163_hc15_bd002_s51150021), and a 5 s /history poll is itself a comfyui
# wake, so poller and LLM caller ping-pong the GPU (C:/AI/director/logs/comfy-graceful-stop.log = ~90 s cycles of
# "stop after 0s" for a fresh PID across the night of 2026-10-24/25).
SUBMIT_TIMEOUT = 1200   # = live healthCheckTimeout; the /prompt POST waits behind a comfyui_auto start
POLL_TIMEOUT = 120      # one /history read; ComfyUI answers slowly while it renders
POLL_SEC = 60           # every /comfyui request is a wake, so the cadence sits above the measured ~90 s start
LOG = os.path.join(W, "community.log")

def log(s, logfile=None):
    line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} CT {s}"
    print(line, flush=True)
    for f in {LOG, logfile} - {None}:
        open(f, "a", encoding="utf-8").write(line + "\n")

def http(url, data=None, timeout=60, method=None):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None,
                               headers={"Content-Type": "application/json"}, method=method)
    raw = urllib.request.urlopen(r, timeout=timeout).read()
    try: return json.loads(raw)
    except Exception: return raw.decode("utf-8", "replace")

# --- adults-only guard (same rule as ALI-80 run_all.py) ---
EXC = ['cowgirl','girlfriend','eighteen','kidnap','old-school','childhood']
BAD = {'girl','teen','school','schoolgirl','underage','minor','kid','child','loli','children'}
def guard_ok(t):
    t = t.lower()
    for e in EXC: t = t.replace(e, ' ')
    if 'barely legal' in t: return False
    for w in re.split(r"[^a-z]+", t):
        if w in BAD or (w.endswith('s') and w[:-1] in BAD) or w in ('schoolgirls','minors','teens','kids','girls'): return False
    return True

PROMPT_KEYS = ("prompt", "text", "prompt_1", "prompt_2", "prompt_3", "prompt_4", "prompt_5", "prompt_6", "clips_json", "sequence_prompt", "value")

def prompt_strings(inputs):
    """Yield all prompt-bearing string values from node inputs."""
    if not isinstance(inputs, dict):
        return
    for k in PROMPT_KEYS:
        v = inputs.get(k)
        if isinstance(v, str):
            yield v

APPROVED = {  # ALI-80 approved adult stills only
 "D15": r"C:\Users\derek\5slock\approved_characters\D15\D15_Woman_in_bikini.jpg",
 "FD006": r"C:\Users\derek\5slock\approved_characters\FLOW_DARKHAIR_2026-10-19\FD006.jpg",
 "FD003": r"C:\Users\derek\5slock\approved_characters\FLOW_DARKHAIR_2026-10-19\FD003.jpg",
 "D12": r"C:\Users\derek\5slock\approved_characters\D12\D12_Woman_posing_in_bikini.jpg",
 "POOL": r"C:\Users\derek\5slock\approved_characters\POOL\COND_POOL_BIKINI_PORTRAIT.jpg",  # pool-20261021: Derek-approved (approved_characters\INDEX.csv id POOL); P7 fixed still from 2026-10-21
}

def stage(key, w, h):
    """Center-crop an approved still to the output aspect (D9/TenStrip: ref aspect == output) and stage it in ComfyUI input."""
    from PIL import Image
    src = APPROVED[key]
    os.makedirs(os.path.join(C, "input", "community"), exist_ok=True)
    name = f"community/{key}_{w}x{h}.png"
    dst = os.path.join(C, "input", name)
    if not os.path.exists(dst):
        im = Image.open(src).convert("RGB"); iw, ih = im.size
        ta = w / h
        if iw / ih > ta: nw = int(ih * ta); box = ((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih)
        else: nh = int(iw / ta); box = (0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh)
        im.crop(box).resize((w, h), Image.LANCZOS).save(dst)
    return name

def frames_for(sec):  # 17k+5 grid at 24 fps
    k = max(0, round((sec * 24 - 5) / 17)); return 17 * k + 5

def _model_chain(g, loras=(), vsa=True, prefix="m", attention="pytorch attention"):
    if "unet" not in g:  # one shared loader (never load the UNET twice)
        g["unet"] = {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}}
    src = ["unet", 0]
    for i, (name, s) in enumerate(loras):
        if "beta6mix" in name.lower(): raise ValueError("never stack Eros_beta6mix_Lora on beta6")
        g[f"{prefix}_lora{i}"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": src, "lora_name": name, "strength_model": float(s)}}
        src = [f"{prefix}_lora{i}", 0]
    if vsa:
        g[f"{prefix}_attn"] = {"class_type": "ModelAttentionBackend", "inputs": {"model": src, "attention": attention}}  # ALI-157: A/B arm
        g[f"{prefix}_vsa"] = {"class_type": "BlockSparseAttention", "inputs": {"model": [f"{prefix}_attn", 0],
            "selection": "vsa", "selection.keep_percent": 10, "start_percent": 0.2, "end_percent": 1.0,
            "dense_blocks": "", "min_tokens": 12288, "extra_tokens": 256, "sink_conditioning": "exact_kv_and_rows", "verbose": False}}
        src = [f"{prefix}_vsa", 0]
    g[f"{prefix}_shift"] = {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": src, "shift_video": 12.0, "shift_audio": 3.0}}
    return [f"{prefix}_shift", 0]

def _common(g):
    g["clip"] = {"class_type": "CLIPLoader", "inputs": {"clip_name": TE, "type": "minimax", "device": "default"}}
    g["vvae"] = {"class_type": "VAELoader", "inputs": {"vae_name": VVAE}}
    g["avae"] = {"class_type": "VAELoader", "inputs": {"vae_name": AVAE}}
    g["ksel"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}

def _sample(g, tag, model, cond, latent, steps, noise):
    g[f"{tag}_sched"] = {"class_type": "BasicScheduler", "inputs": {"model": model, "scheduler": "simple", "steps": steps, "denoise": 1.0}}
    g[f"{tag}_guide"] = {"class_type": "BasicGuider", "inputs": {"model": model, "conditioning": cond}}
    g[f"{tag}_samp"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": noise, "guider": [f"{tag}_guide", 0],
        "sampler": ["ksel", 0], "sigmas": [f"{tag}_sched", 0], "latent_image": latent}}
    return [f"{tag}_samp", 0]

def _decode_save(g, latent, prefix):
    g["dec_v"] = {"class_type": "VAEDecode", "inputs": {"samples": latent, "vae": ["vvae", 0]}}
    g["dec_a"] = {"class_type": "VAEDecodeAudio", "inputs": {"samples": latent, "vae": ["avae", 0]}}
    g["mkvid"] = {"class_type": "CreateVideo", "inputs": {"images": ["dec_v", 0], "audio": ["dec_a", 0], "fps": 24}}
    g["save"] = {"class_type": "SaveVideo", "inputs": {"video": ["mkvid", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}}

def first_pass(g, mode, prompt, img, w, h, length, steps, model):
    """mode 'i2v' (first_frame) or 'r2v' (reference image)."""
    g["img"] = {"class_type": "LoadImage", "inputs": {"image": img}}
    if mode == "i2v":
        g["c0"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["clip", 0], "vae": ["vvae", 0], "prompt": prompt,
            "width": w, "height": h, "length": length, "first_frame": ["img", 0]}}
    else:
        g["c0"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {"clip": ["clip", 0], "vae": ["vvae", 0], "audio_vae": ["avae", 0],
            "prompt": prompt, "width": w, "height": h, "length": length, "ref_image_size": "max", "ref_images.ref_image_1": ["img", 0]}}
    return _sample(g, "s0", model, ["c0", 0], ["c0", 1], steps, ["noise", 0])

def build(mode, prompts, img, w, h, first_len, steps, seed, prefix, ext_frames=119, overlap=22,
          loras=(), vsa=True, antiburn=None, attention="pytorch attention"):
    """prompts[0] = first chunk; prompts[1:] = continuation chunks (latent-tail continuation, ttulttul nodes).
    antiburn: strength for Anti-Burn LoRA on chunk 2+ only (None = off)."""
    g = {}; _common(g)
    g["noise"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": int(seed)}}
    m0 = _model_chain(g, loras, vsa, "m", attention)
    mc = m0
    if antiburn and len(prompts) > 1:
        mc = _model_chain(g, tuple(loras) + ((ANTIBURN, antiburn),), vsa, "mab", attention)
    lat = first_pass(g, mode, prompts[0], img, w, h, first_len, steps, m0)
    for i, p in enumerate(prompts[1:], start=1):
        g[f"win{i}"] = {"class_type": "MiniMaxH3GuidedContinuationWindow", "inputs": {"previous_av_latent": lat,
            "overlap_frames": overlap, "extension_frames": ext_frames}}
        g[f"c{i}"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": {"clip": ["clip", 0], "vae": ["vvae", 0], "prompt": p,
            "width": w, "height": h, "length": [f"win{i}", 1]}}
        g[f"tail{i}"] = {"class_type": "MiniMaxH3LatentTailGuide", "inputs": {"positive": [f"c{i}", 0], "previous_av_latent": lat,
            "target_av_latent": [f"win{i}", 0], "overlap_video_tokens": [f"win{i}", 2], "overlap_audio_tokens": [f"win{i}", 3]}}
        smp = _sample(g, f"s{i}", mc, [f"tail{i}", 0], [f"win{i}", 0], steps, ["noise", 0])
        g[f"app{i}"] = {"class_type": "MiniMaxH3AppendContinuation", "inputs": {"previous_av_latent": lat, "sampled_window": smp,
            "overlap_video_tokens": [f"win{i}", 2], "overlap_audio_tokens": [f"win{i}", 3],
            "transition_video_tokens": [f"win{i}", 4], "transition_audio_tokens": [f"win{i}", 5]}}
        lat = [f"app{i}", 0]
    _decode_save(g, lat, prefix)
    return g

def running():
    try: return http(LS + "/running", timeout=10)
    except Exception as e: return {"error": str(e)}

def comfy_loaded():
    """True only when llama-swap answers /running and comfyui_auto is in it. /running is the documented admin route
    (README, saved C:/AI/community/notes/web/rt_llamaswap_readme.txt:57 "`/running` - list currently running models"),
    so unlike a /comfyui/... path it never wakes a model. None = /running unreadable: never conclude, keep polling."""
    r = running()
    if not isinstance(r, dict) or "error" in r: return None
    return any(x.get("model") == "comfyui_auto" for x in (r.get("running") or []))

def outcome(out, kind, pid=None, note=""):
    """RENDER-TIMEOUT: comm.run keeps its contract (side dict on success, None on failure) and records WHY it failed
    in the caller's dict, so the runner can tell a node error (an objective failure, so the redo rule applies) from
    a client stall: a stall means the render may already be running and paid for, and llama-swap's own doc says client
    retries "create more queued work" (notes/web/rt_ls_capacity-and-queues.txt:16-20). Kinds: guard, node_error,
    submit_stall, evicted, stalled. Returns None so every call site stays a one-line `return outcome(...)`."""
    if isinstance(out, dict):
        out["outcome"] = kind
        if pid: out["prompt_id"] = pid
        if note: out["note"] = note
    return None

def ensure_comfy(logfile=None):
    """GPU sharing: make sure no LLM is loaded, then wake ComfyUI through llama-swap."""
    r = running(); names = [x.get("model") for x in (r.get("running") or [])] if isinstance(r, dict) else []
    if any(n and n != "comfyui_auto" for n in names):
        log(f"UNLOAD LLM(s) {names}", logfile)
        for n in names:  # ALI-154: documented POST /api/models/unload/:model_id (llama-swap README), not legacy GET /unload
            if n and n != "comfyui_auto": http(LS + "/api/models/unload/" + n, timeout=120, method="POST")
    t0 = time.time()
    st = http(BASE + "/system_stats", timeout=300)
    log(f"COMFY ready v{st['system']['comfyui_version']} wait={time.time()-t0:.0f}s vram_free={st['devices'][0].get('vram_free',0)/2**30:.1f}GiB", logfile)

PENDING = "pending"  # fetch(): the prompt_id is not in /history yet

def submit(g, tag, meta, outdir, logfile=None, out=None):
    """Guard + save <tag>.api.json + POST /prompt. Returns the prompt_id, or None (the reason is in `out`; a guard
    hit leaves `out` empty, as run() always did). run_queue.py calls this for every job of a batch up front."""
    os.makedirs(outdir, exist_ok=True)
    for n in g.values():
        for s in prompt_strings(n.get("inputs", {})):
            if not guard_ok(s):
                log(f"SKIP {tag} adults-only guard hit", logfile); return None
    json.dump(g, open(os.path.join(outdir, tag + ".api.json"), "w", encoding="utf-8"), indent=1)
    try:
        res = http(BASE + "/prompt", {"prompt": g, "client_id": "community-ali52",
                   "extra_data": {"extra_pnginfo": {"workflow": {"api_prompt": g, "community": meta}}}},
                   timeout=SUBMIT_TIMEOUT)
    except urllib.error.HTTPError as e:
        log(f"JOB error {tag} POST {e.code} {e.read()[:1500]!r}", logfile)
        return outcome(out, "node_error", note="POST /prompt rejected: " + str(e.code))
    except Exception as e:
        # a client-side stall on the submit says nothing about the server: llama-swap queues /prompt behind a model
        # start, so the job may be running. Never re-POST on this outcome - that is how one clip cost 7 full renders.
        log(f"JOB submit-stall {tag} {str(e)[:160]} (submit timeout {SUBMIT_TIMEOUT}s; the job may be running server-side)", logfile)
        return outcome(out, "submit_stall", note=str(e)[:160])
    pid = res.get("prompt_id"); log(f"JOB start {tag} prompt_id={pid}", logfile)
    return pid

def fetch(pid, tag, meta, outdir, t0, logfile=None, out=None):
    """ONE /history/<pid> read (raises if the read fails). PENDING = not finished yet; side dict = success (output
    copied next to the request, .json side file written); None = node error (recorded in `out`)."""
    h = http(f"{BASE}/history/{pid}", timeout=POLL_TIMEOUT)
    if pid not in h: return PENDING
    st = h[pid].get("status", {}); outs = h[pid].get("outputs", {})
    files = [(f.get("subfolder"), f.get("filename")) for o in outs.values() for k in ("images", "gifs", "videos") for f in o.get(k, [])]
    dt = time.time() - t0
    if st.get("status_str") == "success" and files:
        src = os.path.join(C, "output", files[0][0] or "", files[0][1])
        dst = os.path.join(outdir, tag + os.path.splitext(src)[1])
        shutil.copyfile(src, dst)
        side = dict(meta, tag=tag, secs=round(dt, 1), comfy_output=src, file=dst, prompt_id=pid,
                    finished=datetime.datetime.now().strftime('%Y-%m-%d %H:%M CT'))
        json.dump(side, open(dst + ".json", "w", encoding="utf-8"), indent=1)
        log(f"JOB end {tag} ok secs={dt:.1f} file={dst}", logfile); return side
    msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
    log(f"JOB error {tag} secs={dt:.1f} {json.dumps(msgs)[:1500]}", logfile)
    return outcome(out, "node_error", pid, note=json.dumps(msgs)[:300])

def run(g, tag, meta, outdir, logfile=None, poll=POLL_SEC, timeout=7200, out=None):
    """One job, submit then wait (submit() + fetch() every `poll` s). Batches use run_queue.py's up-front queue."""
    t0 = time.time()
    pid = submit(g, tag, meta, outdir, logfile, out)
    if pid is None: return None
    while time.time() - t0 < timeout:
        time.sleep(poll)
        try: r = fetch(pid, tag, meta, outdir, t0, logfile, out)
        except Exception as e:
            log(f"poll warn {tag} {e}", logfile)
            if comfy_loaded() is False:
                # comfyui_auto is gone: the next wake is a FRESH process with an EMPTY history, so this prompt_id can
                # never be answered. Measured 2026-10-25: ComfyUI stopped at 04:04:54, 2 s after the gi046_s51150031
                # clip was written at 04:04:52, and this loop went on warning for 19 more minutes (status.log 04:23:29).
                log(f"poll stop {tag} comfyui_auto is not running: prompt_id {pid} is in no live history", logfile)
                return outcome(out, "evicted", pid, note="history lost with the comfyui_auto process")
            continue
        if r is PENDING: continue
        return r
    log(f"JOB timeout {tag}", logfile)
    return outcome(out, "stalled", pid, note=f"no history in {timeout}s; the render may have landed in ComfyUI output")

def llm(system, user, max_tokens=3000, temperature=0.6, model="coding_swift15_iq3s_esp"):
    body = {"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": max_tokens, "temperature": temperature}
    r = http(LS + "/v1/chat/completions", body, timeout=1200)
    return (r["choices"][0]["message"].get("content") or "").split("</think>")[-1].strip()
