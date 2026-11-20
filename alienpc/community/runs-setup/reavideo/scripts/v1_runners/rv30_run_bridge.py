
"""Compile the 30s validation manifest via h3max_bridge against the already-loaded X3 model."""
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

stems_path = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\stems.json")
out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s\bridge")
stems = json.loads(stems_path.read_text(encoding="utf-8"))
fc = stems.get("fcsydny_visual")
aj = stems.get("adam_jensen_visual")
if not fc or not aj:
    print("NOT_READY missing visual stems")
    raise SystemExit(2)

from h3max_bridge import export_breakdown

breakdown = Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2\breakdown.json")
audio = Path(r"C:\Users\derek\forge\reavideo\out\hotel14sav80\stems\vocals.wav")
manifest = export_breakdown(
    breakdown,
    out_dir,
    refmod_specs=[f"FCSydny={fc}", f"Adam Jensen={aj}"],
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
# public summary: no prompts, no stems, no adult text
public = {
    "clips": len(manifest["clips"]),
    "out_dir": str(out_dir),
    "fps": manifest.get("fps"),
    "profile": manifest.get("profile"),
    "model_used": "flash-next-uncensored-v2",
    "reason_not_flash_next": "none; flash-next-uncensored-v2 was loaded and ready",
    "shots": ["shot_058", "shot_029"],
    "slice_long": "voice",
    "max_frames": 362,
    "clip_meta": [
        {
            "clip_index": c.get("clip_index"),
            "frames": c.get("frames"),
            "duration_s": c.get("duration_s"),
            "audio_duration_s": c.get("audio_duration_s"),
            "validation_status": (c.get("validation") or {}).get("status"),
            "prompt_chars": len(c.get("prompt") or ""),
            "has_d_tag": "<d>" in (c.get("prompt") or ""),
            "offline_fallback": bool((c.get("conversion") or {}).get("offline_fallback")),
            "audio_stems": bool(c.get("audio_stems")),
            "keyframe_count": len(c.get("keyframes") or []),
        }
        for c in manifest["clips"]
    ],
}
print(json.dumps(public, indent=2))
