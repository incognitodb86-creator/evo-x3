# Build ONE cell graph exactly the way the current Switchyard video path does (director.video_jobs.build_i2v_graph with the
# live config + preset resolution). Read-only use of Switchyard code: imports it, changes nothing, does not start its runner.
# usage (director venv): python sy_graph.py IMAGE_NAME PROMPT_FILE SEED LABEL OUT_JSON
import sys, json
sys.path.insert(0, r"C:\AI\director\src")
from pathlib import Path
from director.config import load_settings
from director import video_jobs as vj
s = load_settings(Path(r"C:\AI\director\config\director.live.yaml"), Path(r"C:\AI\director"))
eff, preset, params = vj._resolve_render_plan(s.video, {"frames": 124})  # live cfg frames=103 fails its own grid check; jobs pass 124 (pipeline_defaults clip.frames)
image, pf, seed, label, out = sys.argv[1:6]
g = vj.build_i2v_graph(eff, image=image, prompt=Path(pf).read_text(encoding="utf-8").strip(), seed=int(seed), length=params.frames,
                       steps=eff.steps, shift=eff.shift, label=label, width=params.width, height=params.height,
                       ref_images=[image], sampler=eff.sampler, keep_audio=eff.keep_audio, gen_fps=eff.gen_fps,
                       audio_shift=eff.audio_shift, add_guide=True)
json.dump({"graph": g, "eff": {"preset": preset.name, "steps": eff.steps, "shift": eff.shift, "audio_shift": eff.audio_shift, "sampler": eff.sampler,
           "frames": params.frames, "w": params.width, "h": params.height, "gen_fps": eff.gen_fps, "keep_audio": eff.keep_audio,
           "rife": eff.rife_multiplier, "out_fps": eff.out_fps}}, open(out, "w"), indent=1)
print("OK", preset.name, eff.steps, eff.shift, params.frames, params.width, params.height, eff.keep_audio)
