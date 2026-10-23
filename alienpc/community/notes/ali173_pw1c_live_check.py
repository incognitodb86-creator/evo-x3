"""PW1c REGISTER (live half): ask the running ComfyUI what the prompt-rewriter nodes list.

One GET of /object_info (several MB) is parsed IN PROCESS and only the rewriter rows are
printed, so the context never sees the raw graph dump (the old guard rule "never request the
raw /object_info" is kept by filtering, not by skipping the check).

Uses: this script must run in the SAME tool call that woke ComfyUI (llama-swap swaps Forge's
model turn out the moment ComfyUI loads, so the answer has to be captured before the next
model turn). GPU minutes: the wake only (no DiT, no render, no sampler) - logged by the
caller in notes/bakeoff_gpu_ledger.md.

Checks (objective):
  1. the Omni node class is registered: MiniMaxH3PromptWriterOmni
  2. its 'model' combo names the Qwen2.5-Omni-7B base that is on disk
  3. the Q8_0 Omni adapter GGUF is listed somewhere in the pack's widgets
  4. the '(no Qwen2.5-Omni base found' sentinel is NOT in any list
  5. 'on disk:' rows exist (the scan ran at import)
"""
import json
import sys
import urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "10004"
BASE = "http://127.0.0.1:" + PORT
OUT = r"C:/AI/community/notes/pw1c_live_objective.json"
NEEDLE = ("Qwen2.5-Omni-7B", "LoRA-Omni", "on disk:", "ollama:", "no Qwen2.5-Omni")
sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
rep = {"port": PORT, "checks": [], "rows": [], "nodes": []}


def get(path, t=90):
    return urllib.request.urlopen(BASE + path, timeout=t).read()


def chk(name, ok, note=""):
    rep["checks"].append({"name": name, "ok": bool(ok), "note": str(note)[:300]})
    line = ("PASS " if ok else "FAIL ") + name + ("  " + str(note)[:200] if note else "")
    print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def say(text):
    print(str(text).encode("ascii", "backslashreplace").decode("ascii"), flush=True)


try:
    stats = json.loads(get("/system_stats", 30))
    sysinfo = stats.get("system")
    one = sysinfo[0] if isinstance(sysinfo, list) and sysinfo else (sysinfo or {})
    devs = stats.get("devices") or one.get("devices") or []
    rep["system_stats"] = {"os": one.get("os"), "python": one.get("python_version"),
                           "comfyui": one.get("comfyui_version"),
                           "devices": [d.get("name") for d in devs if isinstance(d, dict)]}
    print("system_stats: %s" % json.dumps(rep["system_stats"], ensure_ascii=True)[:300], flush=True)
except Exception as e:
    rep["system_stats_error"] = str(e)
    print("system_stats: %s" % e, flush=True)

try:
    q = json.loads(get("/queue", 30))
    print("queue: running=%d pending=%d"
          % (len(q.get("queue_running", [])), len(q.get("queue_pending", []))), flush=True)
    rep["queue"] = {"running": len(q.get("queue_running", [])), "pending": len(q.get("queue_pending", []))}
except Exception as e:
    rep["queue_error"] = str(e)

raw = get("/object_info", 180)
info = json.loads(raw)
rep["object_info_bytes"] = len(raw)
rep["node_classes"] = len(info)
print("object_info: %d bytes, %d node classes" % (len(raw), len(info)), flush=True)

h3 = sorted(k for k in info if "MiniMax" in k)
rep["minimax_nodes"] = h3
print("MiniMaxH3 nodes registered (%d): %s" % (len(h3), ", ".join(h3)), flush=True)

base_rows, adapter_rows, ondisk, sentinel = [], [], [], []
for cls in h3:
    inp = ((info[cls].get("input") or {}).get("required") or {})
    opt = ((info[cls].get("input") or {}).get("optional") or {})
    rep["nodes"].append({"class": cls, "widgets": sorted(list(inp) + list(opt))})
    for wname, spec in list(inp.items()) + list(opt.items()):
        opts = None
        if isinstance(spec, (list, tuple)) and spec:
            if isinstance(spec[0], list):
                opts = spec[0]                     # classic v1 node: options are the first element
            elif len(spec) > 1 and isinstance(spec[1], dict):
                opts = spec[1].get("options")      # v2 io node: ["COMBO", {"options": [...] }]
        if isinstance(spec, dict):
            opts = spec.get("options")
        if not opts:
            continue
        if cls == "MiniMaxH3PromptWriterOmni" and wname == "model":
            rep["omni_model_row_count"] = len(opts)
            rep["omni_model_rows"] = [str(o) for o in opts]
            say("MiniMaxH3PromptWriterOmni.model rows: %d" % len(opts))
            for o in opts[:14]:
                say("   " + str(o)[:170])
        for o in opts:
            s = str(o)
            if not any(n.lower() in s.lower() for n in NEEDLE):
                continue
            row = {"class": cls, "widget": wname, "option": s}
            adapter_rows.append(row)
            if s.lower().startswith("on disk:"):
                ondisk.append(row)
            if "Qwen2.5-Omni-7B" in s:
                base_rows.append(row)
            if "no Qwen2.5-Omni base found" in s.lower():
                sentinel.append(row)

rep["rows"] = adapter_rows
rep["on_disk_rows"] = ondisk
print("\n-- rows naming the Omni base (%d)" % len(base_rows))
for r in base_rows[:12]:
    say("   %s.%s = %s" % (r["class"], r["widget"], r["option"]))
print("-- 'on disk:' rows the nodes list (%d)" % len(ondisk))
for r in ondisk[:12]:
    say("   %s.%s = %s" % (r["class"], r["widget"], r["option"]))
print("-- other Omni/adapter rows (%d)" % len(adapter_rows))
for r in adapter_rows[:14]:
    say("   %s.%s = %s" % (r["class"], r["widget"], r["option"]))

chk("1 Omni node class registered", "MiniMaxH3PromptWriterOmni" in info)
omni = "MiniMaxH3PromptWriterOmni"
omni_models = [str(o) for o in rep.get("omni_model_rows", [])]
chk("2 Omni node model list names the Qwen2.5-Omni-7B base",
    any("Qwen2.5-Omni-7B" in o for o in omni_models),
    "; ".join(o[:60] for o in omni_models if "Qwen2.5-Omni-7B" in o)[:200])
chk("2b the 7B base row is NOT marked 'wrong size for the adapter'",
    not any("Qwen2.5-Omni-7B" in o and "wrong size" in o for o in omni_models),
    [o[:90] for o in omni_models if "wrong size" in o])
ad = [r for r in adapter_rows if "Q8_0" in r["option"] and "LoRA-Omni" in r["option"]]
chk("3 the Q8_0 Omni adapter GGUF is listed by the nodes", bool(ad),
    ("%s.%s = %s" % (ad[0]["class"], ad[0]["widget"], ad[0]["option"][:90])) if ad else "no adapter row")
chk("4 no '(no Qwen2.5-Omni base found' sentinel", not sentinel, sentinel[:1])
chk("5 at least one 'on disk:' row in the pack's widgets", bool(ondisk), "%d rows" % len(ondisk))
scanned = [o for o in omni_models if o.startswith("on disk:") and "Qwen2.5-Omni-7B" in o]
rep["scanned_7b_rows_in_omni_list"] = scanned
say("note: the scanned 7B row is deduped against the catalog entry it names "
    "(model_sections.copy_of), so it is not a second row; offline proof in "
    "notes/pw1c_objective.json")

rep["pass"] = all(c["ok"] for c in rep["checks"])
print("\nSUMMARY %d/%d live checks passed"
      % (sum(1 for c in rep["checks"] if c["ok"]), len(rep["checks"])))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, indent=1, ensure_ascii=False)
print("dump -> " + OUT)
sys.exit(0 if rep["pass"] else 1)
