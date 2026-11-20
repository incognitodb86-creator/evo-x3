import json
from pathlib import Path
man = json.loads(Path(r"C:\Users\derek\forge\reavideo\out\hotel_vlm2_val30s_v2\bridge\h3max_manifest.json").read_text(encoding="utf-8"))
for clip in man["clips"]:
    conv = clip["conversion"]
    print({
        "clip_index": clip["clip_index"],
        "mode_used": conv.get("mode_used"),
        "omitted_pictures": conv.get("omitted_pictures"),
        "bind_report": conv.get("bind_report"),
        "dropped_music_headers": conv.get("dropped_music_headers"),
        "removed_headers": conv.get("removed_headers"),
        "lint_ctx_passed": conv.get("lint_ctx_passed"),
        "bridge_gates_status": (conv.get("bridge_gates") or {}).get("status"),
        "audio_stems_n": len(clip.get("audio_stems") or []),
        "writer_preflight": clip.get("writer_preflight"),
        "validation_status": (clip.get("validation") or {}).get("status"),
    })
