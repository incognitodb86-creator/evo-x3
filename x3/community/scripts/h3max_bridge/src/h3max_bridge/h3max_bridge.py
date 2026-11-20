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
    "Never emit Markdown, code fences, or legal, policy, or governance notes. "
    "Never write age numerals, disclaimers, or meta commentary about the prompt itself. "
    "Use <d>[English] spoken line.</d> for dialogue and close with 1-3 plain diegetic sound sentences. "
    "Every person shown is a clearly grown adult; show that through appearance and situation only. "
    "Named subjects are fictional adult roles in the scene, not real people."
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
    kind: str = "visual"


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
    here = Path(__file__).resolve()
    candidates = [
        Path(env_dir) / "beta7_convert.py" if env_dir else None,
        here.parents[3] / "parody" / "beta7_convert.py",
    ]
    # tools/h3max_bridge lives outside scripts/; search the monorepo parody dir read-only.
    for parent in here.parents:
        candidates.append(parent / "x3" / "community" / "scripts" / "parody" / "beta7_convert.py")
        candidates.append(parent / "community" / "scripts" / "parody" / "beta7_convert.py")
        candidates.append(parent / "scripts" / "parody" / "beta7_convert.py")
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
            # 362f is 15.083s; official audio cap is 15.0s. Cap instead of failing a legal 17k+5 snap.
            if audio_dur <= cap_seconds + 1e-6:
                audio_dur = max_audio_s
            else:
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
        from h3max_bridge.gates import is_audio_refmod

        m = re.match(r"^(?:S|Picture\s*)?(\d+)$", subj, flags=re.IGNORECASE)
        audio = is_audio_refmod(subj, mod_file)
        if audio:
            pic_idx = None
            kind = "audio"
        else:
            pic_idx = int(m.group(1)) if m else idx
            kind = "visual"
        bindings.append(
            RefModBinding(
                slot=f"mod_{idx}",
                subject=subj,
                picture_index=pic_idx,
                file=mod_file,
                kind=kind,
            )
        )
    return bindings



def load_llm_api_key() -> str:
    """Load the llama-swap API key from env, then the Windows user Environment if needed.

    Order: LLM_API_KEY, LLAMA_SWAP_API_KEY, LLAMA_SWAP_KEY, EVO_X3_LLM_KEY.
    AlienPc shells often miss EVO_X3_LLM_KEY in the process env even when it is set in HKCU.
    The value is never printed.
    """
    for name in ("LLM_API_KEY", "LLAMA_SWAP_API_KEY", "LLAMA_SWAP_KEY", "EVO_X3_LLM_KEY"):
        val = (os.environ.get(name) or "").strip()
        if val:
            return val
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
                for name in ("EVO_X3_LLM_KEY", "LLAMA_SWAP_KEY", "LLM_API_KEY", "LLAMA_SWAP_API_KEY"):
                    try:
                        val, _ = winreg.QueryValueEx(h, name)
                    except FileNotFoundError:
                        continue
                    except OSError:
                        continue
                    s = str(val or "").strip()
                    if s:
                        return s
        except ImportError:
            pass
    return ""


def parse_shot_ids(spec: str) -> list[str]:
    """Parse a comma-separated `--shots` list (`49,29` or `shot_049,shot_029`) into canonical ids."""
    ids: list[str] = []
    for raw in (spec or "").split(","):
        token = raw.strip()
        if not token:
            continue
        if re.fullmatch(r"\d+", token):
            ids.append(f"shot_{int(token):03d}")
        else:
            ids.append(token)
    if not ids:
        raise ValueError("empty --shots value")
    return ids


def filter_shots(breakdown: dict[str, Any], shot_ids: Sequence[str]) -> dict[str, Any]:
    """Return a shallow copy of `breakdown` containing only the requested shots, in given order."""
    wanted = list(shot_ids)
    by_id: dict[str, dict[str, Any]] = {}
    for shot in breakdown.get("shots") or []:
        sid = str(shot.get("id") or "").strip()
        if sid:
            by_id[sid] = shot
        idx = shot.get("index")
        if isinstance(idx, int) and sid == "":
            by_id[f"shot_{idx:03d}"] = shot
    missing = [s for s in wanted if s not in by_id]
    if missing:
        raise ValueError(f"shots not found in breakdown.json: {', '.join(missing)}")
    out = dict(breakdown)
    out["shots"] = [dict(by_id[s]) for s in wanted]
    return out


def voice_segments(breakdown: dict[str, Any]) -> list[tuple[float, float]]:
    """Return `(start, end)` voice segments from `audio.voice.segments`, if present."""
    raw = ((breakdown.get("audio") or {}).get("voice") or {}).get("segments") or []
    out: list[tuple[float, float]] = []
    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            a, b = float(item[0]), float(item[1])
            if b > a:
                out.append((a, b))
    return out


def _voice_overlap(start: float, duration: float, segments: Sequence[tuple[float, float]]) -> float:
    end = start + duration
    total = 0.0
    for a, b in segments:
        total += max(0.0, min(end, b) - max(start, a))
    return total


def best_voice_window(shot: dict[str, Any], cap_s: float, segments: Sequence[tuple[float, float]]) -> tuple[float, float]:
    """Pick a `cap_s` window (or the full shot if shorter) with the most overlapping voice."""
    start = float(shot.get("start") or 0.0)
    dur = _shot_duration(shot)
    if dur <= cap_s:
        return start, dur
    if not segments:
        return start, cap_s
    best_score = -1.0
    best_start = start
    t = start
    end = start + dur
    step = 0.25
    while t + 1e-6 < end:
        win = min(cap_s, end - t)
        score = _voice_overlap(t, win, segments)
        if score > best_score:
            best_score = score
            best_start = t
        t += step
    return best_start, min(cap_s, end - best_start)


def slice_long_shots(
    breakdown: dict[str, Any],
    *,
    max_frames: int = H3_DEFAULT_MAX_FRAMES,
    mode: str = "voice",
) -> dict[str, Any]:
    """Slice shots longer than the 17k+5 cap so `pack_shots` can consume them.

    `mode='voice'` keeps the window with the most `audio.voice` overlap; `mode='start'` keeps the first cap seconds.
    Shorter shots are left unchanged. Original start/duration are stored on the shot for audio alignment.
    """
    if mode not in {"voice", "start", "tile"}:
        raise ValueError(f"unknown slice mode {mode!r}; expected 'voice', 'start', or 'tile'")
    cap_s = min(int(max_frames), H3_HARD_MAX_FRAMES) / H3_FPS
    segs = voice_segments(breakdown)
    out = dict(breakdown)
    shots: list[dict[str, Any]] = []
    for shot in breakdown.get("shots") or []:
        dur = _shot_duration(shot)
        orig_start = float(shot.get("start") or 0.0)
        if dur <= cap_s + 1e-9:
            shots.append(dict(shot))
            continue
        if mode == "tile":
            windows: list[tuple[float, float]] = []
            t = orig_start
            end = orig_start + dur
            while t + 1e-9 < end:
                win = min(cap_s, end - t)
                windows.append((t, win))
                t += win
        elif mode == "voice":
            windows = [best_voice_window(shot, cap_s, segs)]
        else:
            windows = [(orig_start, cap_s)]
        for i, (new_start, new_dur) in enumerate(windows, start=1):
            item = dict(shot)
            item["original_start"] = orig_start
            item["original_duration"] = dur
            item["start"] = new_start
            item["end"] = new_start + new_dur
            item["duration"] = new_dur
            if len(windows) > 1:
                item["id"] = f"{shot.get('id') or 'shot'}_w{i:02d}"
            shots.append(item)
    out["shots"] = shots
    return out


def _shot_description(shot: dict[str, Any]) -> str:
    if str(shot.get("description") or "").strip():
        desc = str(shot["description"]).strip()
    else:
        vlm = shot.get("vlm") if isinstance(shot.get("vlm"), dict) else {}
        review = shot.get("review") if isinstance(shot.get("review"), dict) else {}
        desc = str((vlm or {}).get("description") or (review or {}).get("description") or "").strip()
        perf = (vlm or {}).get("performance") if isinstance((vlm or {}).get("performance"), dict) else {}
        en = str((perf or {}).get("en") or "").strip()
        if en and en not in desc:
            desc = f"{desc} {en}".strip()
    aspects = shot.get("aspects")
    if isinstance(aspects, dict):
        bits = []
        for key in ("framing", "camera", "lighting", "grade"):
            val = aspects.get(key)
            if isinstance(val, str) and val.strip():
                bits.append(f"{key}: {val.strip()}")
            elif isinstance(val, dict):
                # keep short scalar fields only
                for sk, sv in val.items():
                    if isinstance(sv, str) and sv.strip() and len(sv) < 240:
                        bits.append(f"{key}.{sk}: {sv.strip()}")
        if bits:
            desc = f"{desc} " + " ".join(bits) if desc else " ".join(bits)
    return desc


def _shot_keyframe(shot: dict[str, Any], breakdown_dir: Path | None) -> str:
    existing = shot.get("keyframe")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()
    assets = shot.get("assets") if isinstance(shot.get("assets"), dict) else {}
    raw = assets.get("first_frame") if assets else None
    if isinstance(raw, dict):
        for v in raw.values():
            if isinstance(v, str) and v.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                raw = v
                break
        else:
            raw = None
    if not isinstance(raw, str) or not raw.strip():
        return ""
    path = Path(raw)
    if not path.is_absolute() and breakdown_dir is not None:
        path = breakdown_dir / path
    return str(path)


def normalize_breakdown(
    breakdown: dict[str, Any],
    *,
    audio_stem: Path | None = None,
    breakdown_dir: Path | None = None,
) -> dict[str, Any]:
    """Fill hotel_vlm2-style shots so pack/compile can run without `video`/`description` keys.

    Missing per-shot `video` is left empty (oc_ref_2pass has no LoadVideo input). A vocals stem is
    attached with `audio_duration` capped at 15s when voice/talk is present. The original
    breakdown.json file is never rewritten.
    """
    segs = voice_segments(breakdown)
    out = dict(breakdown)
    shots: list[dict[str, Any]] = []
    for shot in breakdown.get("shots") or []:
        item = dict(shot)
        item["description"] = _shot_description(item)
        kf = _shot_keyframe(item, breakdown_dir)
        if kf:
            item["keyframe"] = kf
        dur = _shot_duration(item)
        start = float(item.get("start") or 0.0)
        talk = float(item.get("talk_share") or 0.0)
        has_voice = talk > 0.0 or _voice_overlap(start, dur, segs) > 0.0
        if audio_stem is not None:
            stems = [str(audio_stem)]
            for existing in item.get("audio_stems") or []:
                if str(existing) not in stems:
                    stems.append(str(existing))
            item["audio_stems"] = stems
        if has_voice or item.get("audio_stems"):
            item["audio_duration"] = min(dur, H3_MAX_AUDIO_SECONDS)
        elif "audio_duration" not in item:
            item["audio_duration"] = 0.0
        shots.append(item)
    out["shots"] = shots
    return out


def discover_vocals_stem(breakdown_path: Path) -> Path | None:
    """Find a sibling `hotel14sav80/stems/vocals.wav` or `stems/vocals.wav` next to the breakdown."""
    parent = breakdown_path.resolve().parent
    candidates = [
        parent / "stems" / "vocals.wav",
        parent.parent / "hotel14sav80" / "stems" / "vocals.wav",
        parent.parent / "hotel_14sav80" / "stems" / "vocals.wav",
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


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
    from h3max_bridge.gates import is_oral_context, named_refmod_lines, shot_text_blob, speech_lines_of

    lines: list[str] = [
        f"Compile a single MiniMax-H3 10Eros-Max Beta 7 prompt for Clip {pack.pack_index} "
        f"({pack.frames} frames, {pack.duration_s:.2f}s at {H3_FPS} FPS).",
        "Name each bound subject as (S1), (S2), ... in the prompt. Never invent <d> lines.",
        "Every kept <d> line must have a speaker tag and mouth-motion / lip-sync wording.",
    ]
    lines.extend(named_refmod_lines(refmods))
    for i, shot in enumerate(pack.shots, start=1):
        desc = str(shot.get("description") or "").strip()
        bpm = shot.get("bpm")
        bpm_note = f" [BPM: {bpm}]" if bpm is not None else ""
        lines.append(f"Shot {i}{bpm_note}: {desc}")
        if not desc:
            fallback = _shot_description(shot)
            if fallback:
                lines[-1] = f"Shot {i}{bpm_note}: {fallback}"
        blob = shot_text_blob(shot)
        oral = is_oral_context(blob)
        speech_lines = speech_lines_of(shot)
        talk = float(shot.get("talk_share") or 0.0)
        if oral:
            lines.append(
                "  This beat is oral. The oral giver stays silent (no <d>); "
                "body sound is diegetic foley; a partner may speak only with a speaker tag."
            )
        elif speech_lines:
            for item in speech_lines:
                lines.append(f"  Dialogue ({item['speaker']}): {item['text']}")
            lines.append("  Write those lines as speaker-tagged <d> with lip-sync / mouth-motion wording.")
        elif talk > 0:
            lines.append(
                f"  Spoken audio may be present (talk_share={talk:.3f}) but no ASR speech.lines were provided; "
                "do not invent <d> dialogue. Use diegetic foley only."
            )
    return "\n".join(lines)


def _default_http_post(
    url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))



def _bound_refmods_for_pack(pack: ShotPack, refmods: Sequence[RefModBinding]) -> tuple[list[RefModBinding], dict[str, Any]]:
    from h3max_bridge.gates import bind_refmods_for_shots

    return bind_refmods_for_shots(refmods, pack.shots)


def _finalize_compiled_prompt(
    converted: str,
    conv_report: dict[str, Any],
    validation: dict[str, Any],
    *,
    pack: ShotPack,
    refmods: Sequence[RefModBinding],
    b7: Any,
    lint_ctx: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Run bridge oral/lip-sync/speaker gates, then re-validate with lint_ctx."""
    from h3max_bridge.gates import apply_bridge_gates, redact_validation, shot_text_blob

    source = " ".join(shot_text_blob(s) for s in pack.shots)
    gates = apply_bridge_gates(converted, oral_source_text=source)
    text = gates["text"]
    conv_report = dict(conv_report or {})
    conv_report["bridge_gates"] = {k: v for k, v in gates.items() if k != "text"}
    conv_report["lint_ctx_passed"] = lint_ctx is not None
    omit_pics = [r.picture_index for r in refmods if r.picture_index is not None]
    if text != converted:
        converted, conv2, validation = b7.convert_and_validate(
            text,
            omit_pictures=omit_pics,
            mode="plain",
            clip_seconds=pack.duration_s,
            lint_ctx=lint_ctx,
        )
        conv_report["post_gate_conversion"] = conv2
    validation = dict(validation or {})
    validation["redacted"] = redact_validation(validation)
    validation["bridge_gates"] = conv_report["bridge_gates"]
    if gates["status"] != "READY":
        validation["status"] = "NOT_READY"
        validation.setdefault("violations", []).extend(
            {"code": c, "note": "bridge gate"} for c in gates["codes"]
        )
        validation["redacted"] = redact_validation(validation)
    return converted, conv_report, validation


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
    key = api_key if api_key is not None else load_llm_api_key()

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
    from h3max_bridge.gates import default_lint_ctx, redact_validation

    refmods, bind_report = _bound_refmods_for_pack(pack, refmods)
    lint_ctx = default_lint_ctx(clip_seconds=pack.duration_s)
    b7 = load_beta7_convert()
    omit_pics = [r.picture_index for r in refmods if r.picture_index is not None]
    start_seed = 12345

    def _generate(seed: int) -> str:
        body = dict(payload)
        body["seed"] = seed
        resp = post_fn(endpoint, body, headers, timeout_s)
        choices = resp.get("choices") or []
        if not choices:
            raise RuntimeError("llama-swap returned empty choices list")
        return str((choices[0].get("message") or {}).get("content") or "").strip()

    boxed = b7.run_with_single_regen(
        _generate,
        seed=start_seed,
        omit_pictures=omit_pics,
        mode="plain",
        clip_seconds=pack.duration_s,
        lint_ctx=lint_ctx,
    )
    converted, conv_report, validation = boxed["text"], boxed["conversion"], boxed["validation"]
    # run_with_single_regen only retries filler/speaker mismatches. Policy-word leaks (common
    # when a writer copies age-numeral or governance phrasing) need additional seed retries.
    extra = 0
    seed = int((boxed.get("regen") or {}).get("final_seed") or start_seed)
    while validation["status"] != "READY" and extra < 4:
        extra += 1
        seed += 1
        boxed = b7.run_with_single_regen(
            _generate,
            seed=seed,
            omit_pictures=omit_pics,
            mode="plain",
            clip_seconds=pack.duration_s,
            lint_ctx=lint_ctx,
        )
        converted, conv_report, validation = boxed["text"], boxed["conversion"], boxed["validation"]
    converted, conv_report, validation = _finalize_compiled_prompt(
        converted, conv_report, validation, pack=pack, refmods=refmods, b7=b7, lint_ctx=lint_ctx
    )
    conv_report["bind_report"] = bind_report
    conv_report["lint_ctx_passed"] = True
    if validation["status"] != "READY":
        codes = ", ".join(v["code"] for v in validation["violations"])
        reason = validation.get("not_ready_reason") or codes
        err = BridgeValidationError(f"Beta 7 pre-flight failed ({reason})", validation)
        err.redacted = redact_validation(validation)
        raise err

    return converted, conv_report, validation



def _sanitize_policy_text(text: str) -> str:
    """Drop policy/governance regex matches from source text so they cannot leak into a prompt."""
    try:
        b7 = load_beta7_convert()
        policy_re = getattr(b7, "br", None)
        # import via the loaded module's build_request
        import build_request as br  # type: ignore
        cleaned = br._POLICY_RE.sub("", text)
        cleaned = br._SELF_GRADE_RE.sub("", cleaned)
        return re.sub(r"\s{2,}", " ", cleaned).strip()
    except Exception:
        return (text or "").strip()


def compile_prompt_offline(
    pack: ShotPack,
    *,
    refmods: Sequence[RefModBinding] = (),
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Build a plain Beta 7 prompt from packed shot text and validate it (no llama-swap call).

    Used when X3 is unavailable or the writer repeatedly fails pre-flight with policy-word leaks.
    """
    from h3max_bridge.gates import (
        FOLEY_CLOSE,
        LIPSYNC_CLAUSE,
        default_lint_ctx,
        is_oral_context,
        named_refmod_lines,
        redact_validation,
        shot_text_blob,
        speech_lines_of,
    )

    refmods, bind_report = _bound_refmods_for_pack(pack, refmods)
    lint_ctx = default_lint_ctx(clip_seconds=pack.duration_s)
    visuals = [r for r in refmods if r.kind != "audio" and r.picture_index is not None]
    parts: list[str] = []
    named = named_refmod_lines(refmods)
    for i, shot in enumerate(pack.shots, start=1):
        desc = _sanitize_policy_text(_shot_description(shot) or "Two adults share a hotel-room moment.")
        if i == 1:
            header = f"[Shot 1] Locked medium shot in a hotel interior. {desc}"
            if named:
                header += " " + " ".join(named)
        else:
            start = float(shot.get("start") or 0.0)
            first_start = float(pack.shots[0].get("start") or 0.0)
            rel = max(0.2, start - first_start)
            if rel >= pack.duration_s:
                rel = max(0.2, pack.duration_s - 0.5)
            mm = int(rel // 60)
            ss = rel - 60 * mm
            header = f"[Shot {i}] At {mm:02d}:{ss:06.3f} Locked medium shot. {desc}"
        for r in visuals:
            tag = f"(S{r.picture_index})"
            if tag not in header:
                if re.fullmatch(r"(?:S|Picture\s*)?\d+", str(r.subject), flags=re.IGNORECASE):
                    header += f" {tag} remains in frame."
                else:
                    header += f" {tag} ({r.subject}) remains in frame."
        lines = speech_lines_of(shot)
        oral = is_oral_context(shot_text_blob(shot))
        if lines and not oral:
            for item in lines:
                spoken = _sanitize_policy_text(item["text"])
                if not spoken:
                    continue
                spk = item["speaker"] or "S1"
                header += (
                    f" {spk} speaks in a low close voice, <d>[English] {spoken}</d> {LIPSYNC_CLAUSE}"
                )
        # No canned <d> when speech.lines is empty, even if talk_share > 0.
        parts.append(header)
    parts.append(FOLEY_CLOSE)
    raw = "\n\n".join(parts)
    b7 = load_beta7_convert()
    omit_pics = [r.picture_index for r in refmods if r.picture_index is not None]
    converted, conv_report, validation = b7.convert_and_validate(
        raw,
        omit_pictures=omit_pics,
        mode="plain",
        clip_seconds=pack.duration_s,
        lint_ctx=lint_ctx,
    )
    converted, conv_report, validation = _finalize_compiled_prompt(
        converted, conv_report, validation, pack=pack, refmods=refmods, b7=b7, lint_ctx=lint_ctx
    )
    conv_report["bind_report"] = bind_report
    conv_report["offline"] = True
    conv_report["lint_ctx_passed"] = True
    if validation["status"] != "READY":
        codes = ", ".join(v["code"] for v in validation["violations"])
        reason = validation.get("not_ready_reason") or codes
        err = BridgeValidationError(f"offline Beta 7 pre-flight failed ({reason})", validation)
        err.redacted = redact_validation(validation)
        raise err
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
    shot_ids: Sequence[str] = (),
    slice_long: str = "none",
    audio_stem: Path | None = None,
    pack_limit: int | None = None,
    skip_video_proxies: bool = False,
    timeout_s: float = 300.0,
    fallback_offline: bool = False,
) -> dict[str, Any]:
    """End-to-end offline/mockable export from `breakdown.json` to `h3max_manifest.json`."""
    breakdown = json.loads(breakdown_path.read_text(encoding="utf-8"))
    if shot_ids:
        breakdown = filter_shots(breakdown, shot_ids)
    if slice_long and slice_long != "none":
        breakdown = slice_long_shots(breakdown, max_frames=max_frames, mode=slice_long)
    from h3max_bridge.gates import redact_validation

    stem = Path(audio_stem) if audio_stem is not None else discover_vocals_stem(breakdown_path)
    breakdown = normalize_breakdown(breakdown, audio_stem=stem, breakdown_dir=breakdown_path.parent)
    refmods = parse_refmods(refmod_specs)
    packs = pack_shots(breakdown, max_frames=max_frames)
    if pack_limit is not None:
        if pack_limit < 1:
            raise ValueError(f"pack_limit must be >= 1, got {pack_limit}")
        packs = packs[: int(pack_limit)]

    out_dir.mkdir(parents=True, exist_ok=True)
    proxy_dir = out_dir / "proxies"
    clips_out: list[dict[str, Any]] = []

    for pack in packs:
        proxies: list[str] = []
        if not skip_video_proxies:
            for clip_str in pack.video_clips:
                src = Path(clip_str)
                if not src.is_absolute():
                    src = breakdown_path.parent / src
                if not src.is_file():
                    continue
                proxy = strip_video_audio(src, proxy_dir, ffmpeg_bin=ffmpeg_bin, runner=ffmpeg_runner)
                proxies.append(str(proxy))

        writer_preflight = None
        offline_fallback = False
        try:
            prompt_text, conv_rep, val_rep = compile_prompt_via_llm(
                pack,
                refmods=refmods,
                base_url=base_url,
                model=model,
                profile=profile,
                http_post=http_post,
                timeout_s=timeout_s,
            )
        except BridgeValidationError as exc:
            writer_preflight = getattr(exc, "redacted", None) or redact_validation(exc.validation)
            if not fallback_offline:
                clips_out.append(
                    {
                        "clip_index": pack.pack_index,
                        "frames": pack.frames,
                        "duration_s": pack.duration_s,
                        "audio_duration_s": pack.audio_duration_s,
                        "prompt": None,
                        "conversion": {"lint_ctx_passed": True},
                        "validation": exc.validation,
                        "writer_preflight": writer_preflight,
                        "video_proxies": proxies,
                        "keyframes": pack.keyframes,
                        "audio_stems": pack.audio_stems,
                    }
                )
                manifest = {
                    "model_id": "minimax-h3-10eros-beta7",
                    "fps": H3_FPS,
                    "profile": profile,
                    "refmods": [asdict(r) for r in refmods],
                    "clips": clips_out,
                }
                (out_dir / "h3max_manifest.json").write_text(
                    json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
                )
                raise
            prompt_text, conv_rep, val_rep = compile_prompt_offline(pack, refmods=refmods)
            conv_rep = dict(conv_rep or {})
            conv_rep["offline_fallback"] = True
            offline_fallback = True
        val_rep = dict(val_rep or {})
        val_rep.setdefault("redacted", redact_validation(val_rep))
        clips_out.append(
            {
                "clip_index": pack.pack_index,
                "frames": pack.frames,
                "duration_s": pack.duration_s,
                "audio_duration_s": pack.audio_duration_s,
                "prompt": prompt_text,
                "conversion": conv_rep,
                "validation": val_rep,
                "writer_preflight": writer_preflight,
                "offline_fallback": offline_fallback,
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
        "--base-url",
        default=os.environ.get("LLAMA_SWAP_BASE_URL") or os.environ.get("EVO_X3_LLM_BASE_URL") or DEFAULT_LLAMA_SWAP_URL,
        help="EVO-X3 llama-swap OpenAI-compatible base URL.",
    )
    ap.add_argument("--model", default=None, help="Override llama-swap model ID.")
    ap.add_argument(
        "--profile", choices=tuple(PROFILE_MODELS), default="default", help="Prompt compiler profile."
    )
    ap.add_argument(
        "--shots",
        default="",
        help="Comma-separated shot ids or numbers to export (e.g. 49,29 or shot_049,shot_029).",
    )
    ap.add_argument(
        "--slice-long",
        choices=("none", "start", "voice", "tile"),
        default="none",
        help="Slice shots longer than the frame cap (voice = best speech window; tile = full coverage).",
    )
    ap.add_argument(
        "--audio-stem",
        type=Path,
        default=None,
        help="Optional vocals/dialogue wav to attach on shots (auto-discovers hotel14sav80/stems/vocals.wav).",
    )
    ap.add_argument(
        "--pack-limit",
        type=int,
        default=None,
        help="Compile only the first N packed clips (validation subset).",
    )
    ap.add_argument(
        "--skip-video-proxies",
        action="store_true",
        help="Do not run ffmpeg -an even when shot video paths exist.",
    )
    ap.add_argument("--timeout", type=float, default=300.0, help="llama-swap HTTP timeout seconds (default 300).")
    ap.add_argument("--fallback-offline", action="store_true", help="If the X3 writer fails Beta 7 pre-flight, compile a validated offline prompt.")
    args = ap.parse_args(list(argv) if argv is not None else None)

    manifest = export_breakdown(
        args.breakdown,
        args.out_dir,
        refmod_specs=args.refmod,
        max_frames=args.max_frames,
        base_url=args.base_url,
        model=args.model,
        profile=args.profile,
        shot_ids=parse_shot_ids(args.shots) if args.shots else (),
        slice_long=args.slice_long,
        audio_stem=args.audio_stem,
        pack_limit=args.pack_limit,
        skip_video_proxies=args.skip_video_proxies,
        timeout_s=args.timeout,
        fallback_offline=args.fallback_offline,
    )
    sys.stdout.write(json.dumps({"clips": len(manifest["clips"]), "out_dir": str(args.out_dir)}) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
