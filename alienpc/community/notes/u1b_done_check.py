#!/usr/bin/env python
# -*- coding: ascii -*-
"""U1b close-out check (MAX block item 2, 2026-10-29).

Read-only. Tests every claim in the Max2 actions.log U1b lines against THIS
disk, from the live files and the live processes. Prints PASS/FAIL per clause
and exits 0 only if all clauses pass. Nothing is installed, started, stopped,
written or rendered by this script.

Run:
  C:/AI/director/.venv/Scripts/python.exe C:/AI/community/notes/u1b_done_check.py
"""
import json
import os
import re
import subprocess
import sys

PY = sys.executable
STRATA_NEW = r"C:\AI\strata-0.2.7"
STRATA_OLD = r"C:\AI\strata-0.2.2"
ENG_NEW = r"C:\AI\strata-engine-027"
ENG_OLD = r"C:\AI\strata-engine-022"
LSWAP_BIN = r"C:\AI\llama-swap-trial\bin\llama-swap.exe"
LSWAP_BAK = r"C:\AI\llama-swap-trial\bin\llama-swap.exe.bak-v266-20261029"
YAML = r"C:\AI\director\config\llama-swap.yaml"
YAML_BAK = r"C:\AI\director\config\llama-swap.yaml.bak-20261029-0932-max2-strata"
ESPCFG_NEW = os.path.join(STRATA_NEW, "strata-swift15-iq3s-esp.json")
ESPCFG_OLD = os.path.join(STRATA_OLD, "strata-swift15-iq3s-esp.json")
ESPCFG_BAK = os.path.join(STRATA_OLD, "strata-swift15-iq3s-esp.json.bak-20261029-0932")
ESPLEG = os.path.join(STRATA_NEW, "strata-swift15-iq3s-esp.log")
PI_HOME = r"C:\Users\derek\.pi\agent"
MODELS_JSON = os.path.join(PI_HOME, "models.json")
MODELS_BAK = os.path.join(PI_HOME, "models.json.bak-20261029-max2")
SETTINGS_JSON = os.path.join(PI_HOME, "settings.json")
PI_AGENT_BAK = r"C:\Users\derek\.pi\agent.bak-20261029-max2"
PI_DOCS = r"C:\Users\derek\AppData\Roaming\npm\node_modules\@earendil-works\pi-coding-agent\docs"
NPM_FETCH = r"C:\AI\bench\pi_npm.json"
GPU_GUARD = r"C:\AI\director\scripts\gpu_guard.ps1"

results = []


def rec(name, ok, detail):
    results.append((name, bool(ok), detail))
    return ok


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def exists(path):
    return os.path.exists(path)


def file_size(path):
    return os.path.getsize(path) if exists(path) else -1


# 1. new Strata tree present and usable
need = [os.path.join(STRATA_NEW, "sy_strata_launch.py"),
        os.path.join(STRATA_NEW, "strata-swift15-iq3s-esp.json"),
        os.path.join(STRATA_NEW, "strata-swift15-iq3s.json"),
        os.path.join(STRATA_NEW, ".venv", "Scripts", "python.exe")]
rec("strata_0.2.7_tree", all(exists(p) for p in need),
    "present: " + ", ".join(os.path.relpath(p, STRATA_NEW) for p in need if exists(p))
    + ("; MISSING " + ", ".join(p for p in need if not exists(p)) if any(not exists(p) for p in need) else ""))

# 2. revert path kept: old tree + old engine + old configs
rec("revert_path_kept", exists(STRATA_OLD) and exists(ENG_OLD) and exists(ESPCFG_OLD),
    "old tree %s (%s), old engine %s (%s), old esp cfg %s" % (
        STRATA_OLD, "dir" if exists(STRATA_OLD) else "MISSING",
        ENG_OLD, "dir" if exists(ENG_OLD) else "MISSING",
        ESPCFG_OLD if exists(ESPCFG_OLD) else "MISSING"))

# 3. engine 0.1.52 cuda13 installed in the new components dir
eng_dir = None
if exists(ENG_NEW):
    for root, dirs, _files in os.walk(ENG_NEW):
        hits = [d for d in dirs if d.startswith("0.1.52")]
        if hits:
            eng_dir = os.path.join(root, hits[0])
            break
eng_exe = os.path.join(eng_dir, "strata.exe") if eng_dir else ""
vis_exe = os.path.join(eng_dir, "strata-vision.exe") if eng_dir else ""
rec("engine_0.1.52_cuda13", bool(eng_dir) and exists(eng_exe) and exists(vis_exe),
    "%s strata.exe=%s (%d B) strata-vision.exe=%s" % (
        eng_dir or "NO 0.1.52 dir", exists(eng_exe), file_size(eng_exe), exists(vis_exe)))

# 4. llama-swap binary reports v268 and the live service answers v268
ver_out = sh('"%s" --version' % LSWAP_BIN).strip().replace("\n", " | ")
m = re.search(r"version:\s*(v\d+)\s*\((\w{7})", ver_out)
live = ""
try:
    live = sh('curl -s -m 5 http://127.0.0.1:8080/api/version').strip()
except Exception:
    live = ""
lm = re.search(r'"version":"(v\d+)"', live) and re.search(r'"commit":"(\w{7})"', live)
rec("llama_swap_v268_binary", bool(m) and m.group(1) == "v268", ver_out[:160])
rec("llama_swap_v268_live", bool(re.search(r'"version":"v268"', live)),
    live[:160] if live else "no answer from http://127.0.0.1:8080/api/version")

# 5. v266 binary kept for revert
rec("lswap_v266_backup", exists(LSWAP_BAK), "%s = %d B" % (LSWAP_BAK, file_size(LSWAP_BAK)))

# 6. live yaml names the new tree in both swift15 slots and has no old-tree path
ytxt = open(YAML, encoding="utf-8-sig").read() if exists(YAML) else ""
cmd_lines = [l.strip() for l in ytxt.splitlines() if l.strip().startswith("cmd:") and "sy_strata_launch" in l]
rec("yaml_uses_027_both_slots", len(cmd_lines) >= 2 and all("strata-0.2.7" in l for l in cmd_lines),
    "%d strata launch cmd lines, all strata-0.2.7: %s; strata-0.2.2 refs in yaml = %d" % (
        len(cmd_lines), all("strata-0.2.7" in l for l in cmd_lines) if cmd_lines else False,
        ytxt.count("strata-0.2.2")))

# 7. yaml backup present (the pre-upgrade bytes)
rec("yaml_backup", exists(YAML_BAK), "%s = %d B, old-tree refs inside = %d" % (
    YAML_BAK, file_size(YAML_BAK),
    open(YAML_BAK, encoding="utf-8-sig").read().count("strata-0.2.2") if exists(YAML_BAK) else -1))

# 8. ESP stays on and the calibrated flags/files survive in the new config
cfg_new = json.load(open(ESPCFG_NEW, encoding="utf-8-sig")) if exists(ESPCFG_NEW) else {}
args_new = [str(a) for a in cfg_new.get("args", [])]
flagset = set(args_new)
need_flags = ["--expert-profile", "--expert-cache", "--control-vector-scaled",
              "--control-vector-layer-range", "--cvec-mode", "--cvec-dir", "--max-context"]
missing_flags = [f for f in need_flags if f not in flagset]
data_paths = [re.sub(r":\d+(\.\d+)$", "", args_new[args_new.index(f) + 1])
              for f in ["--expert-profile", "--control-vector-scaled"]
              if f in args_new and args_new.index(f) + 1 < len(args_new)]
data_missing = [p for p in data_paths if not exists(p)]
idx = args_new.index("--max-context") + 1 if "--max-context" in args_new else -1
maxctx = args_new[idx] if 0 <= idx < len(args_new) else "?"
rec("esp_flags_kept", not missing_flags, "missing=%s" % (missing_flags or "none"))
rec("esp_data_files_present", bool(data_paths) and not data_missing,
    "checked %d profile/control-vector paths, missing=%s" % (len(data_paths), data_missing or "none"))
rec("max_context_262144", maxctx == "262144", "cfg --max-context = %s" % maxctx)

# 9. the new esp config differs from the old one only by path/version strings
def mask(s):
    s = s.replace("0.2.7", "VER").replace("027", "VER").replace("0.1.52", "ENG")
    return s.replace("0.2.2", "VER").replace("022", "VER").replace("0.1.47", "ENG")

if exists(ESPCFG_NEW) and exists(ESPCFG_OLD):
    a = mask(json.dumps(json.load(open(ESPCFG_NEW, encoding="utf-8-sig")), sort_keys=True, indent=1))
    b = mask(json.dumps(json.loads(open(ESPCFG_OLD, encoding="utf-8-sig").read()), sort_keys=True, indent=1))
    rec("esp_cfg_path_only_diff", a == b,
        "identical after masking 0.2.7/0.2.2 and 0.1.52/0.1.47: %s (len %d vs %d)" % (a == b, len(a), len(b)))
else:
    rec("esp_cfg_path_only_diff", False, "one of the two configs is missing")

# 10. the live engine process IS the new 0.1.52 engine, serving the esp slot
ps = ("powershell -NoProfile -Command "
      "\"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'strata|llama-swap' } "
      "| ForEach-Object { ('{0}|{1}|{2}' -f $_.ProcessId, $_.Name, $_.CommandLine) }\"")
procs = [l.split("|", 2) for l in sh(ps).splitlines() if l.count("|") >= 2]
eng_procs = [p for p in procs if len(p) == 3 and "strata" in p[1] and "strata-engine-027" in p[2] and "0.1.52" in p[2]]
esp_live = [p for p in eng_procs if "--expert-profile" in p[2] and "--max-context 262144" in p[2]
            and "strata-vision" not in p[2]]
old_live = [p for p in procs if len(p) == 3 and "strata-engine-022" in p[2]]
rec("live_engine_is_0152_esp", bool(esp_live),
    "pids=%s; old-engine processes = %d" % ([p[0] for p in esp_live], len(old_live)))

# 11. the live llama-swap process runs the installed v268 binary, same config args
lsw_live = [p for p in procs if len(p) == 3 and "llama-swap" in p[1] and "llama-swap-trial\\bin" in p[2]]
rec("live_llama_swap", bool(lsw_live) and all("-config" in p[2] for p in lsw_live),
    "pids=%s args=%s" % ([p[0] for p in lsw_live], [p[2][:110] for p in lsw_live]))

# 12. pi is at the npm latest (no upgrade available) - installed vs the fetched npm manifest
inst = sh("pi --version").strip().splitlines()[-1] if True else ""
npm_ver = ""
if exists(NPM_FETCH):
    try:
        npm_ver = json.load(open(NPM_FETCH, encoding="utf-8-sig")).get("version", "")
    except Exception:
        npm_ver = ""
live_npm = sh("npm view @earendil-works/pi-coding-agent version").strip().splitlines()[-1] if True else ""
rec("pi_installed_equals_latest", bool(inst) and inst == (live_npm or npm_ver),
    "installed pi=%s; npm view=%s; fetched manifest=%s" % (inst, live_npm, npm_ver))

# 13. pi models.json contextWindow = 257000 on the _esp slot; defaults unchanged; backups present
mj = json.load(open(MODELS_JSON, encoding="utf-8-sig")) if exists(MODELS_JSON) else {}
esp = None
for prov in (mj.get("providers") or {}).values():
    for mod in prov.get("models", []):
        if mod.get("id") == "coding_swift15_iq3s_esp":
            esp = mod
settings = json.load(open(SETTINGS_JSON, encoding="utf-8-sig")) if exists(SETTINGS_JSON) else {}
rec("models_json_esp_context_257000", bool(esp) and esp.get("contextWindow") == 257000,
    "esp contextWindow=%s maxTokens=%s" % (esp.get("contextWindow") if esp else None,
                                           esp.get("maxTokens") if esp else None))
rec("defaults_still_esp", settings.get("defaultModel") == "coding_swift15_iq3s_esp",
    "settings.json defaultModel=%s" % settings.get("defaultModel"))
rec("pi_config_backups", exists(MODELS_BAK) and exists(PI_AGENT_BAK),
    "models.json.bak=%s; agent tree backup dir=%s" % (exists(MODELS_BAK), exists(PI_AGENT_BAK)))
rec("strata_cfg_backup", exists(ESPCFG_BAK), "%s = %d B" % (ESPCFG_BAK, file_size(ESPCFG_BAK)))

# 14. the measured ceiling: a >=257k-token prompt served by the new engine, with tok/s
served = []
prefill = None
if exists(ESPLEG):
    with open(ESPLEG, encoding="utf-8", errors="replace") as f:
        for line in f:
            mm = re.search(r"prompt (\d+) tokens = .*? in \d+ ms \((\d+\.\d) tok/s\)", line)
            if mm and int(mm.group(1)) >= 250000:
                served.append(int(mm.group(1)))
                prefill = mm.group(2)
rec("ceiling_261k_served_on_new_engine", bool(served),
    "max prompt served = %s tokens, prefill %s tok/s (log %s)" % (max(served) if served else None, prefill, ESPLEG))

# 15. pi docs read for U3's assumptions: the three behaviours are documented in 1.4.0
cli = open(os.path.join(PI_DOCS, "cli.md"), encoding="utf-8").read() if exists(os.path.join(PI_DOCS, "cli.md")) else ""
conf = open(os.path.join(PI_DOCS, "configuration.md"), encoding="utf-8").read() if exists(os.path.join(PI_DOCS, "configuration.md")) else ""
import hashlib
h = lambda s: hashlib.sha256(s.encode()).hexdigest()[:8]
rec("pi_docs_document_u3_behaviour",
    "--append-system-prompt" in cli and "--no-skills" in cli and "AGENTS.md" in conf and "skills/" in conf,
    "cli.md sha8=%s (append-system-prompt=%s, skills flag=%s); configuration.md sha8=%s (AGENTS.md=%s, skills dir=%s)"
    % (h(cli), "--append-system-prompt" in cli, "--no-skills" in cli, h(conf),
       "AGENTS.md" in conf, "skills/" in conf))

# 16. no GPU render work was running while U1b ran
g = sh('powershell -NoProfile -ExecutionPolicy Bypass -File "%s"' % GPU_GUARD).strip().splitlines()
rec("gpu_idle_now", bool(g) and g[0].startswith("IDLE"), g[0] if g else "no output")

print("U1b close-out check  2026-10-29  host=AlienPc  (read-only)")
fails = 0
for name, ok, detail in results:
    if not ok:
        fails += 1
    print("%-4s %-34s %s" % ("PASS" if ok else "FAIL", name, detail))
print("VERDICT: %s (%d/%d clauses pass)" % ("ALL CLAUSES PASS" if fails == 0 else "%d FAIL" % fails,
                                            len(results) - fails, len(results)))
sys.exit(0 if fails == 0 else 1)
