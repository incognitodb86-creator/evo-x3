import re
import statistics
import time
from pathlib import Path

for f in (r"C:\AI\strata-0.2.2\strata-swift15-iq3s-esp.log",
          r"C:\AI\strata-0.2.7\strata-swift15-iq3s-esp.log"):
    p = Path(f)
    if not p.exists():
        print("--- %s MISSING" % f)
        continue
    c = p.read_text(encoding="utf-8", errors="replace")
    prompts = [int(m.group(1)) for m in re.finditer(r"prompt (\d+) tokens = ", c)]
    rates = [float(m.group(1)) for m in re.finditer(r"prompt \d+ tokens = .*? in \d+ ms \((\d+\.\d) tok/s\)", c)]
    dec = [float(m.group(1)) for m in re.finditer(r"generated in \d+ ms \((\d+\.\d) tok/s\)", c)]
    print("--- %s (%d B, mtime %s)" % (f, p.stat().st_size, __import__("time").strftime(
        "%Y-%m-%d %H:%M", __import__("time").localtime(p.stat().st_mtime))))
    print("    cuda-init-fail: %d | vision-on-CPU: %d | low-VRAM warn: %d" % (
        len(re.findall(r"failed to initialize CUDA", c)),
        len(re.findall(r"strata-vision: on the CPU", c)),
        len(re.findall(r"WARNING: only \d+ MiB of VRAM free", c))))

    def band(name, vals):
        if not vals:
            print("    %s: no samples" % name)
            return
        print("    %s: n=%d min=%.1f median=%.1f p90=%.1f max=%.1f" % (
            name, len(vals), min(vals), statistics.median(vals),
            sorted(vals)[int(len(vals) * 0.9) - 1] if len(vals) >= 10 else max(vals), max(vals)))

    print("    prompts=%d max_prompt=%d" % (len(prompts), max(prompts) if prompts else 0))
    band("prefill tok/s", rates)
    band("decode tok/s", dec)
