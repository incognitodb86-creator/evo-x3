"""REA-Video `breakdown.json` -> MiniMax-H3 10Eros-Max Beta 7 bridge (RV2).

Consumes structured `breakdown.json` from `rea-video decompose`, snaps shots onto the
24 FPS `17k+5` frame grid (`124f/192f/243f/362f`, <= 15s cumulative audio), creates
audio-stripped `ffmpeg -an -c:v copy` proxies for motion-only `<Video N>` clips, binds
`--refmod <subject=mod_file>` slots (`mod_1..mod_8`) while omitting `<Picture N>` tags
for RefMod-bound subjects, calls EVO-X3 `llama-swap`, and enforces `U56 Decision #1`
via the shared `scripts/parody/beta7_convert.py` converter and pre-flight validator.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

H3_FPS = 24
H3_MIN_FRAMES = 56
H3_DEFAULT_MAX_FRAMES = 243
H3_HARD_MAX_FRAMES = 362
H3_MAX_AUDIO_SECONDS = 15.0
MAX_REFMOD_SLOTS = 8
DEFAULT_LLAMA_SWAP_URL = "http://127.0.0.1:8080/v1"
DEFAULT_MODEL = "flash-next-uncensored-v2"
PROFILE_MODELS: dict[str, str] = {
    "default": DEFAULT_MODEL,
    "ref2va-27b": "ref2va-27b",
}

BETA7_SYSTEM_PROMPT = (
    "You compile MiniMax-H3 10Eros-Max Beta 7 prompts (U56 Decision #1). "
    "Output one plain header-free English prompt starting with [Shot 1] and its camera sentence. "
    "Never emit integrated_multimodal_description:, overall_soundscape:, or non_diegetic_music: headers. "
    "Never emit Markdown, code fences, or policy/governance notes. "
    "Use <d>[English] spoken line.</d> for dialogue and close with 1-3 plain diegetic sound sentences. "
    "Every person is an adult (18+)."
)

_BETA7_MOD_CACHE: ModuleType | None = None


class BridgeValidationError(ValueError):
    """Raised when a compiled Beta 7 prompt fails U56 Decision #1 pre-flight validation."""

    def __init__(self, message: str, validation: dict[str, Any]) -> None:
        super().__init__(message)
        self.validation = validation


@dataclass(frozen=True)
class RefModBinding:
    slot: str
    subject: str
    picture_index: int | None
    file: str


@dataclass(frozen=True)
class ShotPack:
    pack_index: int
    frames: int
    duration_s: float
    shots: list[dict[str, Any]]
    video_clips: list[str]
    keyframes: list[str]
    audio_stems: list[str]
    audio_duration_s: float


def load_beta7_convert() -> ModuleType:
    """Import the shared `scripts/parody/beta7_convert.py` module without duplicating rules."""
    global _BETA7_MOD_CACHE
    if _BETA7_MOD_CACHE is not None:
        return _BETA7_MOD_CACHE

    env_dir = os.environ.get("BETA7_CONVERT_DIR")
    candidates = [
        Path(env_dir) / "beta7_convert.py" if env_dir else None,
        Path(__file__).resolve().parents[3] / "parody" / "beta7_convert.py",
    ]
    target = next((p for p in candidates if p is not None and p.is_file()), None)
    if target is None:
        raise FileNotFoundError("Could not locate shared scripts/parody/beta7_convert.py")

    parody_dir = str(target.parent)
    if parody_dir not in sys.path:
        sys.path.insert(0, parody_dir)

    spec = importlib.util.spec_from_file_location("beta7_convert", target)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load spec for {target}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _BETA7_MOD_CACHE = mod
    return mod


def snap_frames(seconds: float, *, max_frames: int = H3_DEFAULT_MAX_FRAMES) -> int:
    """Snap a duration in seconds up onto the 24 FPS 17k+5 grid (`124f/192f/243f/362f`)."""
    if seconds <= 0:
        raise ValueError(f"duration must be positive, got {seconds}")
    cap = min(int(max_frames), H3_HARD_MAX_FRAMES)
    if cap < H3_MIN_FRAMES:
        raise ValueError(f"max_frames must be >= {H3_MIN_FRAMES}, got {cap}")
    raw = max(H3_MIN_FRAMES, math.ceil(seconds * H3_FPS))
    while raw % 17 != 5:
        raw += 1
    if raw > cap:
        raise ValueError(
            f"duration {seconds:.3f}s ({raw} aligned frames) exceeds ceiling {cap}f ({cap / H3_FPS:.2f}s)"
        )
    return raw


def _shot_duration(shot: dict[str, Any]) -> float:
    if "duration" in shot and shot["duration"] is not None:
        return float(shot["duration"])
    if "start" in shot and "end" in shot:
        return max(0.0, float(shot["end"]) - float(shot["start"]))
    raise ValueError(f"shot missing duration or start/end: {shot!r}")


def pack_shots(
    breakdown: dict[str, Any],
    *,
    max_frames: int = H3_DEFAULT_MAX_FRAMES,
    max_audio_s: float = H3_MAX_AUDIO_SECONDS,
) -> list[ShotPack]:
    """Pack `breakdown.json` shots into 17k+5 clips respecting frame and <= 15s audio ceilings."""
    shots = list(breakdown.get("shots") or [])
    if not shots:
        raise ValueError("breakdown.json contains no shots")

    cap_frames = min(int(max_frames), H3_HARD_MAX_FRAMES)
    cap_seconds = cap_frames / H3_FPS
    packs: list[ShotPack] = []

    cur_shots: list[dict[str, Any]] = []
    cur_dur = 0.0
    cur_audio_dur = 0.0

    def _flush() -> None:
        if not cur_shots:
            return
        frames = snap_frames(cur_dur, max_frames=cap_frames)
        videos = [str(s["video"]) for s in cur_shots if s.get("video")]
        keyframes = [str(s["keyframe"]) for s in cur_shots if s.get("keyframe")]
        stems: list[str] = []
        for s in cur_shots:
            for st in s.get("audio_stems") or []:
                if str(st) not in stems:
                    stems.append(str(st))
        packs.append(
            ShotPack(
                pack_index=len(packs) + 1,
                frames=frames,
                duration_s=round(frames / H3_FPS, 3),
                shots=list(cur_shots),
                video_clips=videos,
                keyframes=keyframes,
                audio_stems=stems,
                audio_duration_s=round(cur_audio_dur, 3),
            )
        )

    for shot in shots:
        dur = _shot_duration(shot)
        audio_dur = float(shot.get("audio_duration", dur if shot.get("audio_stems") else 0.0))
        if dur > cap_seconds:
            raise ValueError(
                f"single shot duration {dur:.3f}s exceeds max clip ceiling {cap_seconds:.2f}s ({cap_frames}f)"
            )
        if audio_dur > max_audio_s:
            raise ValueError(f"single shot audio duration {audio_dur:.3f}s exceeds {max_audio_s:.2f}s limit")

        if cur_shots and (cur_dur + dur > cap_seconds or cur_audio_dur + audio_dur > max_audio_s):
            _flush()
            cur_shots = []
            cur_dur = 0.0
            cur_audio_dur = 0.0

        cur_shots.append(shot)
        cur_dur += dur
        cur_audio_dur += audio_dur

    _flush()
    return packs


def parse_refmods(specs: Sequence[str]) -> list[RefModBinding]:
    """Parse `--refmod <subject=mod_file>` args into ordered `mod_1..mod_8` bindings."""
    if len(specs) > MAX_REFMOD_SLOTS:
        raise ValueError(f"at most {MAX_REFMOD_SLOTS} RefMods (mod_1..mod_8) are supported, got {len(specs)}")

    bindings: list[RefModBinding] = []
    for idx, raw in enumerate(specs, start=1):
        if "=" not in raw:
            raise ValueError(f"invalid --refmod value {raw!r}; expected <subject=mod_file>")
        subj, mod_file = (part.strip() for part in raw.split("=", 1))
        if not subj or not mod_file:
            raise ValueError(f"invalid --refmod value {raw!r}; subject and mod_file must be non-empty")
        m = re.match(r"^(?:S|Picture\s*)?(\d+)$", subj, flags=re.IGNORECASE)
        pic_idx = int(m.group(1)) if m else idx
        bindings.append(
            RefModBinding(
                slot=f"mod_{idx}",
                subject=subj,
                picture_index=pic_idx,
                file=mod_file,
            )
        )
    return bindings


def strip_video_audio(
    src_video: Path,
    proxy_dir: Path,
    *,
    ffmpeg_bin: str = "ffmpeg",
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
) -> Path:
    """Create a stream-copied audio-stripped proxy (`ffmpeg -an -c:v copy`) for `<Video N>`."""
    proxy_dir.mkdir(parents=True, exist_ok=True)
    dst = proxy_dir / f"{src_video.stem}_noaudio{src_video.suffix or '.mp4'}"
    cmd = [ffmpeg_bin, "-y", "-i", str(src_video), "-an", "-c:v", "copy", str(dst)]
    run_fn = runner or subprocess.run
    proc = run_fn(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg -an failed for {src_video} (rc={proc.returncode}): {proc.stderr.strip()}")
    return dst


def _build_llm_user_prompt(pack: ShotPack, refmods: Sequence[RefModBinding]) -> str:
    lines: list[str] = [
        f"Compile a single MiniMax-H3 10Eros-Max Beta 7 prompt for Clip {pack.pack_index} "
        f"({pack.frames} frames, {pack.duration_s:.2f}s at {H3_FPS} FPS).",
    ]
    if refmods:
        omitted = ", ".join(
            f"<Picture {r.picture_index}> ({r.subject} via {r.slot})" for r in refmods if r.picture_index
        )
        lines.append(f"RefMod-bound subjects (OMIT their <Picture N> tags): {omitted}.")
    for i, shot in enumerate(pack.shots, start=1):
        desc = str(shot.get("description") or "").strip()
        bpm = shot.get("bpm")
        bpm_note = f" [BPM: {bpm}]" if bpm is not None else ""
        lines.append(f"Shot {i}{bpm_note}: {desc}")
        speech = shot.get("speech") or {}
        speech_lines = speech.get("lines") if isinstance(speech, dict) else shot.get("lines") or []
        for item in speech_lines or []:
            if isinstance(item, dict):
                spk = item.get("speaker") or "S1"
                txt = str(item.get("text") or "").strip()
                if txt:
                    lines.append(f"  Dialogue ({spk}): {txt}")
            elif isinstance(item, str) and item.strip():
                lines.append(f"  Dialogue: {item.strip()}")
    return "\n".join(lines)


def _default_http_post(
    url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def compile_prompt_via_llm(
    pack: ShotPack,
    *,
    refmods: Sequence[RefModBinding] = (),
    base_url: str = DEFAULT_LLAMA_SWAP_URL,
    model: str | None = None,
    profile: str = "default",
    api_key: str | None = None,
    timeout_s: float = 120.0,
    http_post: Callable[[str, dict[str, Any], dict[str, str], float], dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Call EVO-X3 `llama-swap`, convert with `beta7_convert.py`, and validate strictly."""
    if profile not in PROFILE_MODELS:
        raise ValueError(f"unknown profile {profile!r}; expected one of {sorted(PROFILE_MODELS)}")
    chosen_model = model or PROFILE_MODELS[profile]
    endpoint = base_url.rstrip("/") + "/chat/completions"
    key = (
        api_key
        if api_key is not None
        else (os.environ.get("LLM_API_KEY") or os.environ.get("LLAMA_SWAP_API_KEY") or "")
    )

    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    payload: dict[str, Any] = {
        "model": chosen_model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": BETA7_SYSTEM_PROMPT},
            {"role": "user", "content": _build_llm_user_prompt(pack, refmods)},
        ],
    }

    post_fn = http_post or _default_http_post
    resp = post_fn(endpoint, payload, headers, timeout_s)
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError("llama-swap returned empty choices list")
    raw_prompt = str((choices[0].get("message") or {}).get("content") or "").strip()

    b7 = load_beta7_convert()
    omit_pics = [r.picture_index for r in refmods if r.picture_index is not None]
    converted, conv_report = b7.convert_to_beta7(raw_prompt, omit_pictures=omit_pics, mode="plain")
    validation = b7.validate_beta7(converted, clip_seconds=pack.duration_s, refmod_pictures=omit_pics)
    if validation["status"] != "READY":
        codes = ", ".join(v["code"] for v in validation["violations"])
        raise BridgeValidationError(f"Beta 7 pre-flight failed ({codes})", validation)

    return converted, conv_report, validation


def export_breakdown(
    breakdown_path: Path,
    out_dir: Path,
    *,
    refmod_specs: Sequence[str] = (),
    max_frames: int = H3_DEFAULT_MAX_FRAMES,
    base_url: str = DEFAULT_LLAMA_SWAP_URL,
    model: str | None = None,
    profile: str = "default",
    ffmpeg_bin: str = "ffmpeg",
    ffmpeg_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    http_post: Callable[[str, dict[str, Any], dict[str, str], float], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """End-to-end offline/mockable export from `breakdown.json` to `h3max_manifest.json`."""
    breakdown = json.loads(breakdown_path.read_text(encoding="utf-8"))
    refmods = parse_refmods(refmod_specs)
    packs = pack_shots(breakdown, max_frames=max_frames)

    out_dir.mkdir(parents=True, exist_ok=True)
    proxy_dir = out_dir / "proxies"
    clips_out: list[dict[str, Any]] = []

    for pack in packs:
        proxies: list[str] = []
        for clip_str in pack.video_clips:
            src = Path(clip_str)
            if not src.is_absolute():
                src = breakdown_path.parent / src
            proxy = strip_video_audio(src, proxy_dir, ffmpeg_bin=ffmpeg_bin, runner=ffmpeg_runner)
            proxies.append(str(proxy))

        prompt_text, conv_rep, val_rep = compile_prompt_via_llm(
            pack,
            refmods=refmods,
            base_url=base_url,
            model=model,
            profile=profile,
            http_post=http_post,
        )
        clips_out.append(
            {
                "clip_index": pack.pack_index,
                "frames": pack.frames,
                "duration_s": pack.duration_s,
                "audio_duration_s": pack.audio_duration_s,
                "prompt": prompt_text,
                "conversion": conv_rep,
                "validation": val_rep,
                "video_proxies": proxies,
                "keyframes": pack.keyframes,
                "audio_stems": pack.audio_stems,
            }
        )

    manifest: dict[str, Any] = {
        "model_id": "minimax-h3-10eros-beta7",
        "fps": H3_FPS,
        "profile": profile,
        "refmods": [asdict(r) for r in refmods],
        "clips": clips_out,
    }
    (out_dir / "h3max_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Export REA-Video breakdown.json to MiniMax-H3 Beta 7 manifest.")
    ap.add_argument("breakdown", type=Path, help="Path to rea-video breakdown.json.")
    ap.add_argument(
        "-o", "--out-dir", type=Path, required=True, help="Output directory for proxies and manifest."
    )
    ap.add_argument(
        "--refmod", action="append", default=[], help="Bind RefMod slot: <subject=mod_file> (up to 8)."
    )
    ap.add_argument(
        "--max-frames", type=int, default=H3_DEFAULT_MAX_FRAMES, help="17k+5 frame ceiling (default 243)."
    )
    ap.add_argument(
        "--base-url", default=DEFAULT_LLAMA_SWAP_URL, help="EVO-X3 llama-swap OpenAI-compatible base URL."
    )
    ap.add_argument("--model", default=None, help="Override llama-swap model ID.")
    ap.add_argument(
        "--profile", choices=tuple(PROFILE_MODELS), default="default", help="Prompt compiler profile."
    )
    args = ap.parse_args(list(argv) if argv is not None else None)

    manifest = export_breakdown(
        args.breakdown,
        args.out_dir,
        refmod_specs=args.refmod,
        max_frames=args.max_frames,
        base_url=args.base_url,
        model=args.model,
        profile=args.profile,
    )
    sys.stdout.write(json.dumps({"clips": len(manifest["clips"]), "out_dir": str(args.out_dir)}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
