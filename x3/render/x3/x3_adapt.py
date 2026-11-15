"""One-time EVO-X3 adaptations beyond paths (Max Architect 2026-11-15). Idempotent."""
from pathlib import Path
import os
os.chdir(os.path.expanduser("~/AI"))
def sub(path, old, new):
    p = Path(path); t = p.read_text(encoding="utf-8")
    if new in t: print("already", path); return
    assert old in t, (path, old[:70])
    p.write_text(t.replace(old, new, 1), encoding="utf-8"); print("edited", path)
# 1 wp_llm: pi provider on the X3 is x3-local
sub("community/scripts/parody/wp_llm.py",
    '        v = d["providers"]["llama-swap"].get("apiKey")',
    '        provs = d["providers"]  # EVO-X3 2026-11-15: pi provider is x3-local; AlienPc: llama-swap\n'
    '        v = (provs.get("llama-swap") or provs.get("x3-local") or {}).get("apiKey")')
# 2 submit_parody_run: no local queue route on the X3
p = Path("community/scripts/parody/submit_parody_run.py"); raw = p.read_bytes(); t = raw.decode("utf-8")
nl = "\r\n" if "\r\n" in t else "\n"
old = "python = str(QUEUE_PYTHON) if QUEUE_PYTHON.is_file() else sys.executable"
if "EVO-X3 2026-11-15: no local" not in t:
    out = []; n = 0
    for line in t.splitlines(keepends=True):
        if old in line:
            ind = line[:len(line) - len(line.lstrip())]
            out.append(ind + 'if os.name != "nt":  # EVO-X3 2026-11-15: no local ComfyUI/run_queue route; renders stay on AlienPc' + nl)
            out.append(ind + '    raise RuntimeError("X3: --queue is not wired through run_queue.py; after Derrick\'s yes use "' + nl)
            out.append(ind + '                       "~/AI/render/x3/queue-remote.sh <run_dir> (AlienPc ComfyUI over the tailnet)")' + nl)
            n += 1
        out.append(line)
    p.write_text("".join(out), encoding="utf-8"); print("queue guards", n)
assert "\nimport os" in t
# 3 writer pipeline config -> X3 llama-swap
sub("render/writer_pipeline/config.yaml",
    "endpoint: http://127.0.0.1:8085/v1      # GPU lock gate -> llama-swap; requests wait while a render holds the GPU lock",
    "endpoint: http://127.0.0.1:8080/v1      # EVO-X3 llama-swap (loopback; key read in-process from pi models.json x3-local). AlienPc used the :8085 GPU-lock gate")
sub("render/writer_pipeline/config.yaml", "model_alias: gemma4_heretic_poly_think  #",
    "model_alias: gemma4-heretic  # EVO-X3: Gemma 4 26B A4B Heretic Q8_0 llama.cpp Vulkan (AlienPc: gemma4_heretic_poly_think).")
# 4 AGENTS.md launch line
sub("render/AGENTS.md",
    "--model llama-swap/gemma4_heretic_poly_think --thinking medium (not the default coding model); pipeline config uses model_alias gemma4_heretic_poly_think",
    "--model x3-local/gemma4-heretic (EVO-X3; launcher ~/AI/render/x3/render-pi.sh); pipeline config uses model_alias gemma4-heretic")
sub("render/AGENTS.md", ".pi\\agent\\pi-permissions.jsonc", ".pi/agent/pi-permissions.jsonc")
# 5 wp_llm: pi-style "!command" apiKey (X3 models.json uses "!cat ~/.config/evo-x3/llm-key"); key read in-process, never printed
sub("community/scripts/parody/wp_llm.py",
    '        if isinstance(v, str) and v:\n            return os.environ.get(v, v)',
    '        if isinstance(v, str) and v.startswith("!"):  # EVO-X3 2026-11-15: pi resolves "!cmd" keys; do the same\n'
    '            cmd = v[1:].strip()\n'
    '            if cmd.startswith("cat ") and " " not in cmd[4:].strip():\n'
    '                return Path(os.path.expanduser(cmd[4:].strip())).read_text(encoding="utf-8").strip() or None\n'
    '            import subprocess\n'
    '            return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout.strip() or None\n'
    '        if isinstance(v, str) and v:\n            return os.environ.get(v, v)')
