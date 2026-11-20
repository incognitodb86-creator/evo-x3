#!/usr/bin/env python3
"""REA C6: color match and master assembly for the parody remake.

Samples frames from rendered clips with ffmpeg (one subprocess per frame),
computes per-channel RGB statistics, derives an ffmpeg ``lutrgb`` expression
that pulls a clip's color distribution toward the reference clip, and builds
the single ffmpeg call that concatenates the clips with hard cuts, trims
padded shots, and mixes optional background music under the dialogue.

stdlib + numpy only; ffmpeg/ffprobe run as subprocesses.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

FPS = 24
STD_FLOOR = 1.0
MEAN_TOL = 2.0
RATIO_LO = 0.95
RATIO_HI = 1.05
FRAME_EPS = 0.05
CRF = 16

Stats = Tuple[np.ndarray, np.ndarray]


def _fmt(x: float) -> str:
    """Compact fixed-point formatting: 2.500000 -> 2.5, -14.0 -> -14."""
    text = f"{float(x):.6f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def probe_video(path: str) -> Tuple[float, int, int]:
    """Return (duration_sec, width, height) for a clip, read from ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration"
        ":format=duration",
        "-of", "json", str(path),
    ]
    info = json.loads(subprocess.check_output(cmd, text=True))
    streams = info.get("streams") or []
    if not streams:
        raise ValueError(f"ffprobe found no video stream in {path}")
    stream = streams[0]
    width = int(stream["width"])
    height = int(stream["height"])

    duration = _to_float((info.get("format") or {}).get("duration"))
    if duration is None:
        duration = _to_float(stream.get("duration"))
    if duration is None:
        rate = _parse_rate(stream.get("r_frame_rate"))
        frames = stream.get("nb_frames")
        if rate and frames is not None:
            try:
                duration = float(int(frames)) / rate
            except (TypeError, ValueError):
                duration = None
    if duration is None or duration <= 0:
        raise ValueError(f"ffprobe gave no usable duration for {path}")
    return duration, width, height


def _to_float(raw: Any) -> Optional[float]:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if value == value else None  # NaN guard


def _parse_rate(raw: Any) -> Optional[float]:
    if raw in (None, "", "0/0"):
        return None
    text = str(raw)
    if "/" in text:
        num, _, den = text.partition("/")
    else:
        num, den = text, "1"
    try:
        top, bottom = float(num), float(den)
    except ValueError:
        return None
    if bottom <= 0:
        return None
    rate = top / bottom
    return rate if rate > 0 else None


def sample_times(duration: float, n: int) -> List[float]:
    """Evenly spread sample times over a clip duration (centers of n bins)."""
    if n <= 0:
        return []
    dur = float(duration)
    if not dur > 0:
        return [0.0] * n
    cap = max(0.0, dur - FRAME_EPS)
    step = dur / n
    return [min((k + 0.5) * step, cap) for k in range(n)]


def decode_frame(path: str, t: float, width: int, height: int) -> np.ndarray:
    """Decode one RGB frame at time t with a single ffmpeg subprocess."""
    cmd = [
        "ffmpeg", "-v", "error", "-ss", _fmt(t), "-i", str(path),
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    raw = proc.stdout or b""
    want = int(width) * int(height) * 3
    if len(raw) < want:
        raise RuntimeError(
            f"no frame at t={_fmt(t)} for {path} "
            f"(got {len(raw)} bytes, want {want}): "
            f"{(proc.stderr or b'').decode('utf-8', 'replace').strip()}"
        )
    return np.frombuffer(raw[:want], dtype=np.uint8).reshape(height, width, 3)


def sample_frames(mp4: str, n: int = 5) -> List[np.ndarray]:
    """Sample n frames spread evenly over the clip; one ffmpeg call per frame.

    Returns a list of HxWx3 uint8 arrays (RGB).
    """
    if n <= 0:
        return []
    duration, width, height = probe_video(mp4)
    frames = []
    for t in sample_times(duration, n):
        frames.append(decode_frame(mp4, t, width, height))
    return frames


def channel_stats(frames: Sequence[np.ndarray]) -> Stats:
    """Per-channel mean and std over all sampled frames.

    Returns (mean[3], std[3]) as float64 arrays in channel order R, G, B.
    """
    if len(frames) == 0:
        return (
            np.zeros(3, dtype=np.float64),
            np.zeros(3, dtype=np.float64),
        )
    flat = np.concatenate(
        [np.asarray(f, dtype=np.float64).reshape(-1, 3) for f in frames], axis=0
    )
    return (flat.mean(axis=0), flat.std(axis=0))


def _chan_expr(src_mean: float, src_std: float,
               ref_mean: float, ref_std: float) -> str:
    """One lutrgb channel expression: clip((val-mean)*gain+ref_mean,0,255)."""
    gain = max(float(ref_std), STD_FLOOR) / max(float(src_std), STD_FLOOR)
    mean_term = "-" + _fmt(abs(src_mean)) if src_mean >= 0 else "+" + _fmt(abs(src_mean))
    add_term = "+" + _fmt(ref_mean) if ref_mean >= 0 else "-" + _fmt(abs(ref_mean))
    return f"clip((val{mean_term})*{_fmt(gain)}{add_term},0,255)"


def transfer_expr(src_stats: Stats, ref_stats: Stats) -> Optional[str]:
    """ffmpeg lutrgb filter string matching a clip to the reference stats.

    Each channel maps out = (val - src_mean) * (ref_std / src_std) + ref_mean,
    clipped to 0..255, with a std floor of 1.0. Returns None when the clip is
    already close enough: every channel mean differs by < 2 and every std
    ratio sits inside 0.95..1.05.
    """
    src_mean = np.asarray(src_stats[0], dtype=np.float64).ravel()
    src_std = np.asarray(src_stats[1], dtype=np.float64).ravel()
    ref_mean = np.asarray(ref_stats[0], dtype=np.float64).ravel()
    ref_std = np.asarray(ref_stats[1], dtype=np.float64).ravel()

    gain = (np.maximum(ref_std, STD_FLOOR) / np.maximum(src_std, STD_FLOOR))
    if (np.all(np.abs(ref_mean - src_mean) < MEAN_TOL)
            and np.all(gain >= RATIO_LO) and np.all(gain <= RATIO_HI)):
        return None

    chans = "rgb"
    parts = [
        f"{c}='{_chan_expr(src_mean[i], src_std[i], ref_mean[i], ref_std[i])}'"
        for i, c in enumerate(chans)
    ]
    return "lutrgb=" + ":".join(parts)


def build_master_cmd(clips: List[Dict[str, Any]], out_path: str,
                     bgm: Optional[str] = None,
                     bgm_db: float = -14.0) -> List[str]:
    """Build the single ffmpeg call that assembles the master.

    Each clip dict has "path", "trim_to_frames" (int or None) and "lut"
    (str or None). Clips are concatenated with hard cuts (no xfade); optional
    background music is ducked with volume=<bgm_db>dB and mixed under the
    concatenated audio with amix.
    """
    if len(clips) == 0:
        raise ValueError("build_master_cmd needs at least one clip")

    cmd: List[str] = ["ffmpeg", "-y", "-v", "error"]
    for clip in clips:
        cmd += ["-i", str(clip["path"])]

    bgm_index = len(clips)
    if bgm:
        cmd += ["-i", str(bgm)]

    chains: List[str] = []
    concat_in: List[str] = []
    for i, clip in enumerate(clips):
        trim_to = clip.get("trim_to_frames")

        v_filters: List[str] = []
        if clip.get("lut"):
            v_filters.append(str(clip["lut"]))
        if trim_to:
            v_filters.append(f"trim=end_frame={int(trim_to)}")
            v_filters.append("setpts=PTS-STARTPTS")
        if v_filters:
            chains.append(f"[{i}:v]{','.join(v_filters)}[v{i}]")
            v_label = f"[v{i}]"
        else:
            v_label = f"[{i}:v]"

        a_filters: List[str] = []
        if trim_to:
            a_filters.append(f"atrim=end={_fmt(int(trim_to) / FPS)}")
            a_filters.append("asetpts=PTS-STARTPTS")
        if a_filters:
            chains.append(f"[{i}:a]{','.join(a_filters)}[a{i}]")
            a_label = f"[a{i}]"
        else:
            a_label = f"[{i}:a]"

        concat_in.append(v_label)
        concat_in.append(a_label)

    chains.append(
        "".join(concat_in)
        + f"concat=n={len(clips)}:v=1:a=1[catv][cata]"
    )

    audio_out = "[cata]"
    if bgm:
        chains.append(f"[{bgm_index}:a]volume={_fmt(bgm_db)}dB[bgmvol]")
        chains.append(
            "[cata][bgmvol]amix=inputs=2:duration=first:normalize=0[aout]"
        )
        audio_out = "[aout]"

    cmd += ["-filter_complex", ";".join(chains)]
    cmd += ["-map", "[catv]", "-map", audio_out]
    cmd += [
        "-c:v", "libx264", "-crf", str(CRF),
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k",
    ]
    cmd.append(str(out_path))
    return cmd


def _parse_trims(raw: Sequence[str], n_clips: int) -> Dict[int, int]:
    trims: Dict[int, int] = {}
    for item in raw:
        idx_text, sep, frames_text = str(item).partition("=")
        if not sep:
            raise SystemExit(f"--trim expects INDEX=FRAMES, got {item!r}")
        try:
            idx = int(idx_text.strip())
            frames = int(frames_text.strip())
        except ValueError:
            raise SystemExit(f"--trim expects INDEX=FRAMES, got {item!r}")
        if not 0 <= idx < n_clips:
            raise SystemExit(f"--trim index {idx} out of range (0..{n_clips - 1})")
        if frames <= 0:
            raise SystemExit(f"--trim frames must be positive, got {frames}")
        trims[idx] = frames
    return trims


def build_clips(paths: Sequence[str], trims: Optional[Dict[int, int]] = None,
                n_frames: int = 5) -> List[Dict[str, Any]]:
    """Sample each clip and derive its lut; the first clip is the reference."""
    trims = trims or {}
    clips: List[Dict[str, Any]] = []
    ref_stats: Optional[Stats] = None
    for i, path in enumerate(paths):
        stats = channel_stats(sample_frames(path, n=n_frames))
        if i == 0:
            ref_stats = stats
            lut = None
        else:
            lut = transfer_expr(stats, ref_stats)
        clips.append({
            "path": str(path),
            "trim_to_frames": trims.get(i),
            "lut": lut,
        })
    return clips


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="REA color match and master assembly (hard-cut concat)")
    ap.add_argument("out", help="output master mp4")
    ap.add_argument("clips", nargs="+",
                    help="clip mp4s; the first one is the color reference")
    ap.add_argument("--trim", action="append", default=[], metavar="I=N",
                    help=f"trim clip index I to N frames (repeatable)")
    ap.add_argument("--bgm", default=None, help="background music file")
    ap.add_argument("--bgm-db", dest="bgm_db", type=float, default=-14.0,
                    help="background music volume in dB (default -14)")
    ap.add_argument("--frames", type=int, default=5,
                    help="frames sampled per clip for color stats (default 5)")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true",
                    help="print the ffmpeg command and exit 0")
    args = ap.parse_args(argv)

    trims = _parse_trims(args.trim, len(args.clips))
    clips = build_clips(args.clips, trims=trims, n_frames=args.frames)
    cmd = build_master_cmd(clips, args.out, bgm=args.bgm, bgm_db=args.bgm_db)

    if args.dry_run:
        print(" ".join(cmd))
        return 0

    subprocess.run(cmd, check=True)
    print(f"DONE {args.out} clips={len(clips)} "
          f"luts={sum(1 for c in clips if c['lut'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
