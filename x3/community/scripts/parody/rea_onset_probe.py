#!/usr/bin/env python3
"""REA C1: spectral-flux onset probe for a parody music track.

Reads a 16-bit PCM WAV, computes a spectral-flux onset envelope, detects
onset peaks, estimates BPM (60-180) via autocorrelation, and optionally maps
detected onsets onto shot windows from a breakdown JSON.

stdlib + numpy only.
"""

from __future__ import annotations

import argparse
import json
import os
import wave

import numpy as np

FRAME = 2048
HOP = 512
MIN_GAP_SEC = 0.1
BPM_LO = 60.0
BPM_HI = 180.0


def _read_wav(path):
    """Open a 16-bit PCM WAV and return (int16 samples, sr, n_channels)."""
    with wave.open(path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    samples = np.frombuffer(raw, dtype="<i2")
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels)
    return samples, wf.getframerate(), n_channels


def load_wav_mono(path):
    """Load a 16-bit PCM WAV as mono float32 in -1..1.

    Returns (samples, sr).
    """
    data, sr, n_channels = _read_wav(path)
    mono = data.mean(axis=1) if data.ndim == 2 else data
    return (mono / 32768.0).astype(np.float32), sr


def onset_envelope(samples, sr):
    """Half-wave-rectified spectral flux envelope, normalized to 0..1.

    Frame 2048, hop 512, Hann window. Returns (env, times).
    """
    x = np.asarray(samples, dtype=np.float64).ravel()
    n = x.size
    if n == 0:
        return np.zeros(0, dtype=np.float64), np.zeros(0, dtype=np.float64)

    pad = (-n) % HOP
    if pad:
        x = np.concatenate([x, np.zeros(pad)])

    n_frames = 1 + (x.size - FRAME) // HOP if x.size >= FRAME else 1
    win = np.hanning(FRAME)

    if x.size >= FRAME:
        idx = np.arange(FRAME)[None, :] + HOP * np.arange(n_frames)[:, None]
        frames = x[idx] * win
        mags = np.abs(np.fft.rfft(frames, axis=1))
    else:
        frame = np.zeros(FRAME)
        frame[: x.size] = x
        mags = np.abs(np.fft.rfft(frame * win))[None, :]

    flux = np.diff(mags, axis=0, prepend=np.zeros((1, mags.shape[1])))
    env = np.maximum(flux, 0.0).sum(axis=1)

    peak = env.max()
    if peak > 0:
        env = env / peak
    times = (np.arange(env.size) * HOP + FRAME / 2.0) / sr
    return env, times


def detect_onsets(env, times):
    """Pick envelope peaks above mean+1*std with a 0.1 s minimum gap.

    Returns onset times in seconds, rounded to 3 decimals, ascending.
    """
    env = np.asarray(env, dtype=np.float64)
    times = np.asarray(times, dtype=np.float64)
    if env.size == 0:
        return []
    thresh = env.mean() + env.std()
    if thresh <= 0:
        return []

    cand = [i for i in range(1, env.size - 1)
            if env[i] > thresh and env[i] >= env[i - 1] and env[i] >= env[i + 1]]

    # convert the minimum gap to a count of envelope frames
    if times.size > 1:
        frame_dt = float(times[1] - times[0])
        min_gap_frames = max(1, int(np.ceil(MIN_GAP_SEC / frame_dt)))
    else:
        min_gap_frames = 1

    picked = []
    last = -10**9
    for i in cand:
        if i - last >= min_gap_frames:
            picked.append(i)
            last = i
        elif env[i] > env[last]:
            picked[-1] = i
            last = i

    return [round(float(times[i]), 3) for i in picked]


def estimate_bpm(env, sr, hop=HOP):
    """Estimate BPM from autocorrelation of the envelope, limited to 60-180.

    Returns float BPM or None.
    """
    env = np.asarray(env, dtype=np.float64)
    if env.size < 4:
        return None
    e = env - env.mean()
    denom = float(e @ e)
    if denom <= 0:
        return None
    acf = np.correlate(e, e, mode="full")[e.size - 1:]
    acf = acf / denom

    frame_rate = float(sr) / float(hop)
    lo_lag = max(2, int(np.floor(frame_rate * 60.0 / BPM_HI)))
    hi_lag = min(acf.size - 1, int(np.ceil(frame_rate * 60.0 / BPM_HI * 2.0)))
    if hi_lag <= lo_lag:
        return None

    best = int(np.argmax(acf[lo_lag:hi_lag + 1])) + lo_lag
    if acf[best] <= 0:
        return None
    bpm = 60.0 * frame_rate / best
    if bpm < BPM_LO or bpm > BPM_HI:
        return None
    return float(bpm)


def probe(wav_path, shots=None):
    """Probe a WAV file for onsets/BPM and per-shot beat assignments.

    Returns dict with keys "source", "sr", "bpm", "onsets", "shots".
    """
    samples, sr = load_wav_mono(wav_path)
    env, times = onset_envelope(samples, sr)
    onsets = detect_onsets(env, times)
    bpm = estimate_bpm(env, sr)

    out = {
        "source": str(wav_path),
        "sr": int(sr),
        "bpm": bpm,
        "onsets": onsets,
        "shots": [],
    }
    if shots:
        for sh in shots:
            sid = sh.get("id")
            beg = sh.get("start")
            end = sh.get("end")
            beats = [t for t in onsets if beg is not None and end is not None
                     and beg <= t < end]
            strongest = None
            if beg is not None and end is not None and env.size:
                inside = (times >= beg) & (times < end)
                if np.any(inside):
                    sub = np.where(inside, env, -1.0)
                    strongest = round(float(times[int(np.argmax(sub))]), 3)
            out["shots"].append({"id": sid, "beats": beats, "strongest": strongest})
    return out


def _load_shots(breakdown_path):
    with open(breakdown_path, "r", encoding="utf-8") as fh:
        bd = json.load(fh)
    shots = []
    for sh in bd.get("shots", []):
        sid = sh.get("id", sh.get("shot_id"))
        start = sh.get("start")
        end = sh.get("end")
        if sid is None or start is None or end is None:
            continue
        shots.append({"id": sid, "start": float(start), "end": float(end)})
    return shots


def _resolve_input(path):
    if os.path.isdir(path):
        for name in ("stems/music.wav", "stems/original.wav"):
            cand = os.path.join(path, name)
            if os.path.isfile(cand):
                return cand
        raise SystemExit(f"no stems/music.wav or stems/original.wav under {path}")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="REA onset probe")
    ap.add_argument("wav", help="WAV file or run directory")
    ap.add_argument("--breakdown", default=None, help="breakdown.json path")
    ap.add_argument("-o", "--out", default="onset_beats.json")
    args = ap.parse_args(argv)

    wav_path = _resolve_input(args.wav)
    shots = _load_shots(args.breakdown) if args.breakdown else None
    result = probe(wav_path, shots=shots)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"DONE {args.out} bpm={result['bpm']} onsets={len(result['onsets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
