# ALI-13 / ALI-143 27B timing test. Temporary llama-swap entry, removed at the end (config hash verified vs backup).
import sys, os, json, time, hashlib, shutil, urllib.request
sys.path.insert(0, r"C:\AI\community\scripts"); from comm import *
CFG = r"C:\AI\director\config\llama-swap.yaml"; BAK = CFG + ".bak-20261020-27b"
OUT = os.path.join(W, "t27b"); LF = os.path.join(OUT, "t27b.log"); os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
NAME = "tmp_27b_timing"
ARGS = ("-m C:\\AI\\models\\RVN-Qwen3.8-27B-Heretic-GSQ-RCO-IQ3_XXS-mtp.gguf --alias heretic-qwen3.8-27b-iq3xxs-mtp --host 127.0.0.1 --port ${PORT} "
        "-ngl all --fit off -fa on -np 1 -b 512 -ub 512 -c 65536 -ctk q8_0 -ctv q8_0 --spec-type draft-mtp,ngram-mod --spec-draft-n-max 5 "
        "-ctkd q8_0 -ctvd q8_0 --jinja --chat-template-file C:\\AI\\models\\templates\\froggeric-qwen-v22.5.jinja --reasoning-format deepseek "
        "--reasoning-budget 2000 --metrics")
BLOCK = f"""
  {NAME}:
    cmd: 'C:\\AI\\vlm\\llama.cpp\\llama-server.exe {ARGS}'
    cmdStop: 'taskkill /T /F /PID ${{PID}}'
    checkEndpoint: /health
    ttl: 0
    unloadTimeout: 15
"""
MEMBER_ANCHOR = "            - comfyui_longvideo\n"
def add():
    shutil.copy2(CFG, BAK); orig = open(CFG, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in orig else "\n"
    a = MEMBER_ANCHOR.replace("\n", nl); assert orig.count(a) == 1
    new = orig.replace(a, a + f"            - {NAME}{nl}", 1).rstrip("\r\n") + nl + BLOCK.replace("\n", nl)
    open(CFG, "w", encoding="utf-8", newline="").write(new); log(f"CFG add {NAME} (backup {BAK} sha {sha(BAK)[:12]})", LF)
def remove():
    shutil.copy2(BAK, CFG)  # restore exact pre-test bytes
    ok = sha(BAK) == sha(CFG); log(f"CFG removed {NAME}; config == backup: {ok}", LF); return ok
def wait_ls(name, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            m = http(LS + "/v1/models", timeout=10)
            if any(x.get("id") == name for x in m.get("data", [])): return time.time() - t0
        except Exception: pass
        time.sleep(2)
    raise RuntimeError("llama-swap did not reload")
def chat(model, prompt, n=400):
    t0 = time.time()
    r = http(LS + "/v1/chat/completions", {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": n, "temperature": 0.6}, timeout=900)
    dt = time.time() - t0; u = r.get("usage", {}); tm = r.get("timings", {})
    return dt, u, tm, (r["choices"][0]["message"].get("content") or "").split("</think>")[-1].strip()
res = {}
try:
    log("27B START", LF); http(LS + "/unload", timeout=120)
    add(); log(f"reload secs={wait_ls(NAME):.1f}", LF)
    P = ("Write one short image-to-video prompt (40-60 words, present tense) for this shot: an adult woman stands in a quiet courtyard, "
         "smiles at the camera and turns slowly. Include one camera line and one sound line. Output only the prompt.")
    dt, u, tm, txt = chat(NAME, P); res["cold_load_plus_first_reply_s"] = round(dt, 1); res["first_usage"] = u; res["first_timings"] = tm
    log(f"COLD load+reply {dt:.1f}s usage={u} gen_tok_s={tm.get('predicted_per_second')} prompt_tok_s={tm.get('prompt_per_second')}", LF)
    dt, u, tm, txt2 = chat(NAME, "Count from 1 to 200 separated by commas. Output only the numbers.", 800)
    res["warm_reply_s"] = round(dt, 1); res["warm_timings"] = tm
    log(f"WARM reply {dt:.1f}s gen_tok_s={tm.get('predicted_per_second')} draft_acc={tm.get('draft_n_accepted')}/{tm.get('draft_n')}", LF)
    # swap 27B -> ComfyUI, tiny render with the 27B-written prompt
    t0 = time.time(); ensure_comfy(LF); res["swap_27b_to_comfy_s"] = round(time.time() - t0, 1)
    log(f"SWAP 27B->ComfyUI {res['swap_27b_to_comfy_s']}s", LF)
    if not guard_ok(txt): txt = "The adult woman from the start image smiles at the camera in a quiet courtyard. Static shot. Sound: quiet ambience."
    open(os.path.join(OUT, "prompt_27b.txt"), "w", encoding="utf-8").write(txt)
    img = stage("FD006", 416, 736)
    g = build("i2v", [txt], img, 416, 736, 29, 8, 51050001, "community/t27b_tiny")
    r = run(g, "t27b_tiny_render_416x736_29f_8st", {"phase": "27B test", "prompt_by": NAME}, OUT, LF)
    res["tiny_render"] = r and {"secs": r["secs"], "file": r["file"]}
    # swap ComfyUI -> 27B
    t0 = time.time(); dt, u, tm, _ = chat(NAME, "Reply with the single word: ready", 20)
    res["swap_comfy_to_27b_plus_reply_s"] = round(time.time() - t0, 1); log(f"SWAP ComfyUI->27B+reply {res['swap_comfy_to_27b_plus_reply_s']}s", LF)
    # Strata reference on same tasks
    http(LS + "/unload", timeout=120)
    dt, u, tm, _ = chat("coding_sc117_strata", P); res["strata_cold_plus_reply_s"] = round(dt, 1); res["strata_first_timings"] = tm
    dt, u, tm, _ = chat("coding_sc117_strata", "Count from 1 to 200 separated by commas. Output only the numbers.", 800)
    res["strata_warm_reply_s"] = round(dt, 1); res["strata_warm_timings"] = tm; res["strata_warm_usage"] = u
    log(f"STRATA cold {res['strata_cold_plus_reply_s']}s warm {dt:.1f}s timings={tm} usage={u}", LF)
except Exception as e:
    log(f"27B ERROR {e!r}", LF); res["error"] = repr(e)
finally:
    try: http(LS + "/unload", timeout=120)
    except Exception: pass
    res["config_restored"] = remove()
    json.dump(res, open(os.path.join(OUT, "t27b_result.json"), "w"), indent=1)
    log("27B DONE", LF)
