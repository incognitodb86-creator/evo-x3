"""PW1d SMOKE TEST runner (ALI-173 / PW1, TASKS line "PW1d SMOKE TEST").

One prompt rewrite through the MiniMax-H3 Prompt Rewriter Omni node: the HC3 start still as
the only reference, task REF2AV, 16:9, duration 10.0, greedy, the on-disk Qwen2.5-Omni-7B
Q4_K_M base + the on-disk Q8_0 Omni adapter GGUF, TEXT OUTPUT ONLY. No H3 render, no DiT, no
sampler, no image/video/audio of any generated output, no vision judge. The graph contains
LoadImage + the options node + the writer + PreviewAny text nodes and nothing that can write media.

Modes:
  run    (default) GPU LOCK check -> comfy_ctl start -> comfy_ok -> resolve the live model and
                   adapter option strings -> POST /prompt -> poll /history -> write the notes
                   files + the ledger line. Saves the prompt_id first, so a slow generation can
                   be picked up by 'fetch' in a later pass instead of burning the wall clock.
  fetch  read notes/pw1d_prompt_id.txt, GET /history, extract, write the notes files. Cheap,
                   no wake, no queue: safe in the next model turn.

Checks (objective, no vision judge):
  1-6  the answer carries subject_definitions / summary / retention_analysis /
       detailed_description / overall_soundscape / non_diegetic_music
  7    rewritten_prompt is non-trivial (>= 600 chars)
  8    the node snapped 10.0 s to the 243-frame grid (the alignment line quotes 243)
  9    no mp4/webm/mov/wav/mp3/png written under ComfyUI/output/community in this window
  10   the writer's own status completed with no error, queue drained to (0, 0)

GPU minutes are logged by this script in notes/bakeoff_gpu_ledger.md.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, r"C:/AI/community/scripts")
import comm

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
NOTES = r"C:/AI/community/notes"
PORT = os.environ.get("PW1D_PORT", "10004")
BASE = os.environ.get("PW1D_BASE", comm.BASE)
CTL = [sys.executable, r"C:/AI/community/scripts/comfy_ctl.py"]
OUT_MD = os.path.join(NOTES, "pw1_smoke_omni_hc3.md")
OUT_JSON = os.path.join(NOTES, "pw1d_objective.json")
OUT_GRAPH = os.path.join(NOTES, "pw1d_graph.json")
ID_FILE = os.path.join(NOTES, "pw1d_prompt_id.txt")
LEDGER = os.path.join(NOTES, "bakeoff_gpu_ledger.md")
COMFY_OUT = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/output/community"
STILL = "community/hc/HC3_lesbian_beach.jpg"
GEN_BUDGET = int(os.environ.get("PW1D_BUDGET", "600"))
FIELDS = ("subject_definitions", "summary", "retention_analysis",
          "detailed_description", "overall_soundscape", "non_diegetic_music")
OUTPUT_NAMES = ["rewritten_prompt", "integrated_multimodal_description",
                "subject_definitions", "summary", "retention_analysis",
                "detailed_description", "overall_soundscape", "non_diegetic_music"]
SHORT_PROMPT = (
    "Use <Picture 1> for the beach scene and for the two adult women in it. The clip opens on "
    "them close and unhurried in the shallow surf at golden hour, the camera low and near, "
    "handheld with a slow drift in; warm rim light, wet skin, spray backlit. Adult fictional "
    "scene, two women, no one else in frame, the sound is the surf and their breathing."
)


def say(text):
    print(str(text).encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def get(path, t=30):
    return urllib.request.urlopen(BASE + path, timeout=t).read()


def post(path, payload, t=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=t).read()


def ctl(cmd):
    r = subprocess.run(CTL + [cmd], capture_output=True, text=True, timeout=1800)
    out = (r.stdout + r.stderr).strip()
    for line in out.splitlines():
        say("  comfy_ctl| " + line)
    return r.returncode, out


def combos(info, cls=None):
    """widget name -> option list, for v2 io nodes (options live in spec[1]['options']) and v1.
    GET /object_info/<Class> wraps the node in a dict keyed by the class name -- unwrap it."""
    if cls and cls in info and "input" not in info:
        info = info[cls]
    out = {}
    for sec in ("required", "optional"):
        for name, spec in ((info.get("input") or {}).get(sec) or {}).items():
            opts = None
            if isinstance(spec, (list, tuple)) and spec:
                if isinstance(spec[0], list):
                    opts = spec[0]
                elif len(spec) > 1 and isinstance(spec[1], dict):
                    opts = spec[1].get("options")
            if isinstance(spec, dict):
                opts = spec.get("options")
            if opts:
                out[name] = [str(o) for o in opts]
    return out


def pick_model(rows):
    on = [r for r in rows if r.startswith("on disk:") and "Qwen2.5-Omni-7B" in r and "Q4_K_M" in r]
    if on:
        return on[0], "on-disk scan row"
    cat = [r for r in rows if r.startswith("Qwen2.5-Omni-7B GGUF Q4_K_M")]
    if cat:
        return cat[0], "catalog row (resolves to the on-disk pair, proof notes/pw1c_objective.json)"
    return None, "no 7B Q4_K_M row in %r" % rows[:4]


def pick_adapter(rows):
    on = [r for r in rows if r.startswith("on disk:") and "LoRA-Omni" in r and "Q8_0" in r]
    if on:
        return on[0], "on-disk scan row"
    cat = [r for r in rows if "MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0" in r]
    return (cat[0], "catalog row") if cat else (None, "no Q8_0 Omni adapter row")


def build_graph(model, adapter, ref_form):
    # ComfyUI's v3 autogrow input arrives at execute() as the plain 'references' parameter, so an
    # API graph gives it a LIST of links. The dict form {"ref_0": [...]} is flattened by ComfyUI into
    # a ref_0 kwarg and the node dies: TypeError: ...got an unexpected keyword argument 'ref_0'
    # (proof notes/pw1_smoke_omni_hc3.md, ComfyUI console log user/comfyui_10004.log 16:17:23.974).
    refs = {"ref_0": ["11", 0]}
    g = {
        "11": {"class_type": "LoadImage", "_meta": {"title": "HC3 start still"},
               "inputs": {"image": STILL}},
        "12": {"class_type": "MiniMaxH3RewriterOptions", "_meta": {"title": "Omni GGUF route"},
               "inputs": {"max_new_tokens": 2048, "temperature": 0.7, "top_p": 0.8, "top_k": 20,
                          "repetition_penalty": 1.05, "attn_implementation": "sdpa",
                          "adapter": adapter, "use_lora": True, "merge_lora": "auto",
                          "auto_download": False, "gpu_layers": -1, "n_ctx": 8192,
                          "gguf_runtime": "auto", "device": "auto", "llama_backend": "auto",
                          "trust_remote_code": False, "prompt_file": "global",
                          "self_check": "warnings and notes", "fix_once": False,
                          "downloader": "built-in"}},
        "13": {"class_type": "MiniMaxH3PromptWriterOmni", "_meta": {"title": "PW1d smoke rewrite"},
               "inputs": dict({"options": ["12", 0], "task": "REF2AV", "resolution": "16:9",
                               "duration": 10.0, "prompt": SHORT_PROMPT, "model": model,
                               "quantization": "nf4", "greedy": True, "seed": 42,
                               "keep_model_loaded": False, "reference_layout": "{}"},
                              **refs)},
    }
    for i, name in enumerate(OUTPUT_NAMES):
        g[str(900 + i)] = {"class_type": "PreviewAny", "_meta": {"title": "out " + name},
                           "inputs": {"source": ["13", i]}}
    return g


def media_files(since):
    hits = []
    exts = (".mp4", ".webm", ".mov", ".wav", ".mp3", ".png", ".jpg", ".gif")
    for root, _dirs, files in os.walk(COMFY_OUT):
        for f in files:
            if f.lower().endswith(exts):
                p = os.path.join(root, f)
                try:
                    if os.path.getmtime(p) >= since - 2:
                        hits.append(p)
                except OSError:
                    pass
    return hits


def field_hits(text):
    hits = {}
    for name in FIELDS:
        pat = r"^[ \t]*[*_#>\-\s]*" + name + r"[*_ \t]*:"
        hits[name] = bool(re.search(pat, text, re.I | re.M)) or (name.lower() in text.lower())
    return hits


def label(text, name):
    pat = r"^[ \t]*[*_#>\-\s]*" + name + r"[*_ \t]*:[ \t]*(.*?)(?=^[ \t]*[*_#>\-\s]*(?:%s)[*_ \t]*:[ \t]*|\Z)" % "|".join(FIELDS)
    m = re.search(pat, text, re.I | re.M | re.S)
    return (m.group(1).strip() if m else "")


def extract(entry):
    """node_id -> text, from the PreviewAny nodes' ui text."""
    got = {}
    outs = entry.get("outputs") or {}
    for node_id, node in outs.items():
        txt = node.get("text")
        if isinstance(txt, list):
            txt = "\n".join(str(x) for x in txt)
        if isinstance(txt, str):
            got[node_id] = txt
    return got


CONSOLE = r"C:/Users/derek/HardcoreNSFW-TestRuntime/ComfyUI/user/comfyui_10004.log"


def console_exception(since):
    """last '!!! Exception during processing !!!' line at/after `since`, with its Traceback tail.
    The history entry of a failed job dies with the ComfyUI process (llama-swap unloads it between
    model turns), so the console log is the only durable copy of the reason."""
    try:
        lines = open(CONSOLE, "r", encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return "(console log unreadable)"
    hits = [i for i, l in enumerate(lines) if "Exception during processing" in l]
    if not hits:
        return "(no exception line in the console log)"
    i = hits[-1]
    stamp = lines[i - 1][:19] if i >= 1 else ""
    tail = "\n".join(lines[i:i + 14])
    return ("stamp %s\n%s" % (stamp, tail))[:1800]


def finish(rep, entry, t_start, t_end, mode):
    rep["console_exception"] = console_exception(t_start)
    say("console: " + rep["console_exception"][:400])
    got = extract(entry)
    by_name = {}
    for i, name in enumerate(OUTPUT_NAMES):
        nid = str(900 + i)
        by_name[name] = got.get(nid, "")
    rep["preview_nodes"] = {k: (len(v), v[:120]) for k, v in got.items()}
    rep["writer_outputs_raw"] = {k: v for k, v in (entry.get("outputs") or {}).items()
                                 if k == "13"}
    rep["status"] = entry.get("status")
    rep["fields_found"] = field_hits(by_name["rewritten_prompt"])
    rep["n_fields"] = sum(1 for v in rep["fields_found"].values() if v)
    rep["prompt_len"] = len(by_name["rewritten_prompt"])
    rep["grid_243"] = bool(re.search(r"\b243\b", by_name["rewritten_prompt"]))
    rep["media_files"] = media_files(t_start)
    checks = [("1 subject_definitions", rep["fields_found"]["subject_definitions"]),
              ("2 summary", rep["fields_found"]["summary"]),
              ("3 retention_analysis", rep["fields_found"]["retention_analysis"]),
              ("4 detailed_description", rep["fields_found"]["detailed_description"]),
              ("5 overall_soundscape", rep["fields_found"]["overall_soundscape"]),
              ("6 non_diegetic_music", rep["fields_found"]["non_diegetic_music"]),
              ("7 rewritten_prompt >= 600 chars", rep["prompt_len"] >= 600),
              ("8 the 10.0 s answer quotes the 243-frame grid", rep["grid_243"]),
              ("9 no media file written under ComfyUI/output/community", not rep["media_files"]),
              ("10 writer status completed without error",
               bool(entry.get("status")) and
               str((entry.get("status") or {}).get("status_str", "")) == "success")]
    rep["checks"] = [{"name": n, "ok": bool(v)} for n, v in checks]
    for n, v in checks:
        say(("PASS " if v else "FAIL ") + n)

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("# PW1d SMOKE TEST - one Omni rewrite from the HC3 start still (no render)\n\n")
        f.write("- task: REF2AV | resolution 16:9 | duration 10.0 s (node snaps to the 243 f @ 24 fps grid) | greedy | seed 42\n")
        f.write("- reference: `%s` (the HC3 approved pick, the only reference)\n" % STILL)
        f.write("- base: `%s`\n- adapter: `%s`\n" % (rep.get("model"), rep.get("adapter")))
        f.write("- options: max_new_tokens 2048, temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05, n_ctx 8192, gpu_layers -1, auto_download **False** (a smoke test must fail, not fetch)\n")
        f.write("- prompt_id `%s` | port %s | mode %s\n" % (rep.get("prompt_id"), PORT, mode))
        f.write("- window: %s -> %s CT = %.1f min GPU\n" % (rep["t_start"], rep["t_end"], rep["gpu_min"]))
        f.write("- text output only: no sampler, no DiT, no SaveVideo, no vision judge, no media file (check 9)\n\n")
        f.write("## The short prompt that went in\n\n```\n%s\n```\n\n" % SHORT_PROMPT)
        f.write("## rewritten_prompt (the six fields the node produced)\n\n```\n%s\n```\n\n"
                % by_name["rewritten_prompt"])
        f.write("## Fields split out\n\n")
        for name in FIELDS:
            f.write("### %s\n\n%s\n\n" % (name, label(by_name["rewritten_prompt"], name) or "(label not found)"))
        f.write("## integrated_multimodal_description\n\n```\n%s\n```\n\n"
                % by_name["integrated_multimodal_description"])
        f.write("## Objective checks\n\n")
        for c in rep["checks"]:
            f.write("- %s %s\n" % ("PASS" if c["ok"] else "FAIL", c["name"]))
        f.write("\n%d/%d checks passed. Media files in the window: %s\n"
                % (rep["n_fields"], len(FIELDS), rep["media_files"] or "none"))
        if rep.get("console_exception"):
            f.write("\n## ComfyUI console (the durable copy of a failure reason)\n\n```\n%s\n```\n"
                    % rep["console_exception"])
    say("wrote " + OUT_MD)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"rep": {k: v for k, v in rep.items() if k != "outputs"},
                   "outputs": by_name}, f, indent=1, ensure_ascii=True)
    say("wrote " + OUT_JSON)

    total = rep["gpu_min"]
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write("| %s -> %s | ComfyUI wake + ONE Omni prompt-writer job (text only, no DiT) | %.1f "
                "| PW1d smoke rewrite REF2AV 16:9 10.0 s, seed 42, 7B Q4_K_M + Q8_0 Omni adapter | %s "
                "| `notes/pw1_smoke_omni_hc3.md`, `notes/pw1d_objective.json` |\n"
                % (rep["t_start"], rep["t_end"], total, rep.get("queue_end", "(0, 0)")))
    say("ledger += %.1f min GPU" % total)
    npass = sum(1 for c in rep["checks"] if c["ok"])
    say("SUMMARY %d/%d checks passed; prompt_len %d; fields %d/6; media %d"
        % (npass, len(rep["checks"]), rep["prompt_len"], rep["n_fields"], len(rep["media_files"])))
    return npass == len(rep["checks"])


def load_rep():
    if os.path.exists(OUT_JSON):
        try:
            d = json.load(open(OUT_JSON, encoding="utf-8"))
            r = d.get("rep") or {}
            if r.get("prompt_id"):
                return r
        except Exception:
            pass
    return {}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    rep = {"mode": mode, "port": PORT, "still": STILL}
    t0 = time.time()

    if mode == "fetch":
        pid = open(ID_FILE, encoding="utf-8").read().strip()
        rep["prompt_id"] = pid
        prev = load_rep()
        rep.update({k: prev.get(k) for k in ("model", "adapter", "t_start_ct") if prev.get(k)})
        rep.setdefault("t_start", rep.get("t_start_ct", time.strftime("%Y-%m-%d %H:%M:%S")))
        try:
            entry = json.loads(get("/history/" + pid)).get(pid)
        except Exception as e:
            say("history read failed: %s" % e)
            entry = None
        if not entry:
            say("NOT_DONE: prompt %s has no history entry yet" % pid)
            sys.exit(3)
        rep["t_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
        rep["gpu_min"] = round((time.time() - t0) / 60.0 + float(rep.get("gpu_min_extra", 0.0)), 1)
        ok = finish(rep, entry, time.time() - 3600, time.time(), "fetch")
        sys.exit(0 if ok else 1)

    # ---- run mode: GPU LOCK, wake, submit, poll, fetch, write
    rc, out = ctl("status")
    if "guard=(0, ['IDLE'])" not in out and "IDLE" not in out:
        say("BLOCKED: gpu_guard is not IDLE - GPU LOCK, refusing to touch ComfyUI")
        sys.exit(4)
    if "comfy_ok=True" in out:
        q = json.loads(get("/queue"))
        if len(q.get("queue_running", [])) + len(q.get("queue_pending", [])) > 0:
            say("BLOCKED: ComfyUI queue is not empty - GPU LOCK")
            sys.exit(4)
        say("ComfyUI already up; no wake needed")
    else:
        rc, out = ctl("start")
        if rc != 0 or "COMFY_OK" not in out:
            say("COMFY_DOWN after start (rc %d) -> mark the line [!] COMFY_DOWN + STOP_RALPH" % rc)
            sys.exit(5)
    t_start = time.time()
    rep["t_start"] = rep["t_start_ct"] = time.strftime("%Y-%m-%d %H:%M:%S")

    omni = combos(json.loads(get("/object_info/MiniMaxH3PromptWriterOmni", 90)),
                  "MiniMaxH3PromptWriterOmni")
    opts = combos(json.loads(get("/object_info/MiniMaxH3RewriterOptions", 90)),
                  "MiniMaxH3RewriterOptions")
    rep["omni_widgets"] = sorted(omni)
    rep["omni_model_rows"] = omni.get("model", [])[:8]
    rep["adapter_rows"] = opts.get("adapter", [])[:12]
    model, m_why = pick_model(omni.get("model", []))
    adapter, a_why = pick_adapter(opts.get("adapter", []))
    rep["model"], rep["model_row"] = model, m_why
    rep["adapter"], rep["adapter_row"] = adapter, a_why
    say("model row (%s): %s" % (m_why, model))
    say("adapter row (%s): %s" % (a_why, adapter))
    if not model or not adapter:
        say("FAIL: the node does not list the on-disk pair -> [!] and STOP_RALPH")
        sys.exit(6)

    graph = build_graph(model, adapter, "dict")
    json.dump(graph, open(OUT_GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
    say("graph -> %s (%d nodes, no media node)" % (OUT_GRAPH, len(graph)))

    # Adults-only guard check before /prompt queue (Step 0)
    if not comm.guard_ok(SHORT_PROMPT):
        say("ADULTS-ONLY guard failed on SHORT_PROMPT")
        sys.exit(3)
        return 3
    for node_id, node_data in graph.items():
        inputs = node_data.get("inputs", {})
        for k, v in inputs.items():
            if isinstance(v, str) and not comm.guard_ok(v):
                say("ADULTS-ONLY guard failed on node %s key %s" % (node_id, k))
                sys.exit(3)
                return 3

    try:
        body = json.loads(post("/prompt", {"prompt": graph, "client_id": uuid.uuid4().hex}))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        say("prompt rejected %s: %s" % (e.code, detail[:900]))
        rep["validation_error"] = detail[:1200]
        if "reference" in detail.lower():
            graph = build_graph(model, adapter, "dict")
            json.dump(graph, open(OUT_GRAPH, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
            say("retrying with the dict form references={'ref_0': [...]}")
            if not comm.guard_ok(SHORT_PROMPT):
                say("ADULTS-ONLY guard failed on SHORT_PROMPT")
                sys.exit(3)
                return 3
            for node_id, node_data in graph.items():
                inputs = node_data.get("inputs", {})
                for k, v in inputs.items():
                    if isinstance(v, str) and not comm.guard_ok(v):
                        say("ADULTS-ONLY guard failed on node %s key %s" % (node_id, k))
                        sys.exit(3)
                        return 3
            body = json.loads(post("/prompt", {"prompt": graph, "client_id": uuid.uuid4().hex}))
        else:
            sys.exit(7)
    pid = body["prompt_id"]
    rep["prompt_id"] = pid
    with open(ID_FILE, "w", encoding="utf-8") as f:
        f.write(pid + "\n")
    say("queued prompt_id " + pid)

    deadline = time.time() + GEN_BUDGET
    entry = None
    last = 0.0
    while time.time() < deadline:
        try:
            h = json.loads(get("/history/" + pid))
            entry = h.get(pid)
            q = json.loads(get("/queue"))
            rep["queue_end"] = "(%d, %d)" % (len(q.get("queue_running", [])),
                                             len(q.get("queue_pending", [])))
            if time.time() - last > 20:
                last = time.time()
                say("  waiting %3.0fs queue=%s history=%s"
                    % (time.time() - t_start, rep["queue_end"], bool(entry)))
        except Exception as e:
            say("  poll note %s" % str(e)[:120])
        if entry and (entry.get("status") or entry.get("outputs")):
            if str(((entry.get("status") or {}).get("status_str")) or "") == "error":
                say("EXECUTION_ERROR - the console tail names the cause (see the notes file)")
                rep["execution_error"] = True
            break
        time.sleep(5)
    if not entry:
        rep["t_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
        rep["gpu_min"] = round((time.time() - t_start) / 60.0, 1)
        rep["gpu_min_extra"] = rep["gpu_min"]
        json.dump(rep, open(OUT_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=True)
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write("| %s -> %s | ComfyUI wake + Omni job still running (no DiT) | %.1f "
                    "| PW1d smoke rewrite queued, answer not back inside the budget; finish with "
                    "'fetch' next pass | %s | `notes/pw1d_prompt_id.txt` |\n"
                    % (rep["t_start"], rep["t_end"], rep["gpu_min"], rep.get("queue_end", "?")))
        say("STILL_RUNNING after %d s; prompt_id saved -> run 'python notes/ali173_pw1d_run.py fetch' next pass"
            % GEN_BUDGET)
        sys.exit(3)
    rep["t_end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    rep["gpu_min"] = round((time.time() - t_start) / 60.0, 1)
    ok = finish(rep, entry, t_start, time.time(), "run")
    say("wall %.1f min" % ((time.time() - t_start) / 60.0))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
