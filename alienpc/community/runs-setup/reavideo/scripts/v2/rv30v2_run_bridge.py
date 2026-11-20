"""Compile the v2 30s validation manifest via h3max_bridge 0.2.0. No prompt/stem print."""
from __future__ import annotations
import json, os, sys
from pathlib import Path

def load_evo_key() -> str:
    v = (os.environ.get("EVO_X3_LLM_KEY") or os.environ.get("LLM_API_KEY") or "").strip()
    if v:
        return v
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            val, _ = winreg.QueryValueEx(h, "EVO_X3_LLM_KEY")
            return str(val or "").strip()
    return ""

key = load_evo_key()
if not key:
    print("NOT_READY missing EVO_X3_LLM_KEY")
    raise SystemExit(2)
os.environ["EVO_X3_LLM_KEY"] = key
os.environ.setdefault("LLM_API_KEY", key)

stems_path = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
stems = json.loads(stems_path.read_text(encoding="utf-8"))
fc = stems.get("fcsydny_visual")
aj = stems.get("adam_jensen_visual")
fc_audio = stems.get("fcsydny_audio")
if not fc or not aj:
    print("NOT_READY missing visual stems")
    raise SystemExit(2)

from h3max_bridge import __version__, export_breakdown

specs = [f"FCSydny={fc}", f"Adam Jensen={aj}"]
if fc_audio:
    specs.append(f"FCSydny={fc_audio}")

breakdown = Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json")
audio = Path(r"C:\Users\derek\forge\reavideo\out\hotel14sav80\stems\vocals.wav")
manifest = export_breakdown(
    breakdown,
    out_dir,
    refmod_specs=specs,
    max_frames=362,
    base_url="https://evo-x3-1.tailf242b2.ts.net/v1",
    model="flash-next-uncensored-v2",
    shot_ids=["shot_058", "shot_029"],
    slice_long="voice",
    audio_stem=audio if audio.is_file() else None,
    skip_video_proxies=True,
    timeout_s=300.0,
    fallback_offline=True,
)
print(json.dumps({
    "bridge_version": __version__,
    "clips": len(manifest["clips"]),
    "out_dir": str(out_dir),
    "fps": manifest.get("fps"),
    "profile": manifest.get("profile"),
    "model_requested": "flash-next-uncensored-v2",
    "shots": ["shot_058", "shot_029"],
    "slice_long": "voice",
    "max_frames": 362,
    "refmod_spec_n": len(specs),
}, indent=2))
