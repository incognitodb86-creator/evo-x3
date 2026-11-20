"""REA-Video to MiniMax-H3 10Eros-Max Beta 7 bridge package (RV2)."""

from __future__ import annotations

from h3max_bridge.h3max_bridge import (
    BridgeValidationError,
    RefModBinding,
    ShotPack,
    compile_prompt_offline,
    compile_prompt_via_llm,
    export_breakdown,
    filter_shots,
    normalize_breakdown,
    pack_shots,
    parse_refmods,
    parse_shot_ids,
    slice_long_shots,
    snap_frames,
    strip_video_audio,
)

__all__ = [
    "BridgeValidationError",
    "RefModBinding",
    "ShotPack",
    "compile_prompt_offline",
    "compile_prompt_via_llm",
    "export_breakdown",
    "filter_shots",
    "normalize_breakdown",
    "pack_shots",
    "parse_refmods",
    "parse_shot_ids",
    "slice_long_shots",
    "snap_frames",
    "strip_video_audio",
    "__version__",
]
__version__ = "0.1.0"
