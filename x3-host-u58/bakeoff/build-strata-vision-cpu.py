#!/usr/bin/env python3
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("polysetup", "/srv/bakeoff/src/PolyStrata/setup.py")
S = importlib.util.module_from_spec(spec)
sys.modules["polysetup"] = S
print("importing setup.py ...", flush=True)
spec.loader.exec_module(S)
print("get_llama_cpp(vision=True) ...", flush=True)
llama = S.get_llama_cpp(vision=True)
print("llama", llama, flush=True)
eng = S.ROOT / "engine-poly"
stamp = eng / "BUILD.json"
meta = json.loads(stamp.read_text())
vsrc = S.source_hash(S.VISION_SOURCES)
print("vsrc", vsrc, "BUILD backup already made", flush=True)
S.build_vision_cpu(eng, stamp, meta, llama, vsrc, portable=False)
print("DONE", (eng / S.VEXE).exists(), (eng / S.VEXE), flush=True)
