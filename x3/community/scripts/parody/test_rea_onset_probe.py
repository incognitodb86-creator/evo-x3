"""Tests for rea_onset_probe (REA C1) -- synthetic audio only, no disk fixtures."""

import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

import rea_onset_probe as rop

SR = 22050
HERE = Path(__file__).resolve().parent


def _write_wav(path, samples, sr=SR):
    x = np.asarray(samples)
    if x.ndim == 1:
        x = x[:, None]
    clip = np.clip(np.round(x * 32767.0), -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(clip.shape[1])
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(clip.tobytes())


def _click_track(n_beats=16, period=0.5, sr=SR, dur=8.0, amp=0.8):
    x = np.zeros(int(dur * sr))
    n = int(0.005 * sr)
    t = np.arange(n) / sr
    burst = (amp * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float64)
    true_times = []
    for k in range(n_beats):
        i = int(round(k * period * sr))
        if i + n <= x.size:
            x[i:i + n] += burst
            true_times.append(i / sr)
    return x, true_times


def test_click_track_bpm_and_onsets(tmp_path):
    x, true_times = _click_track()
    p = tmp_path / "clicks.wav"
    _write_wav(p, x)
    samples, sr = rop.load_wav_mono(str(p))
    assert samples.dtype == np.float32
    assert sr == SR
    env, times = rop.onset_envelope(samples, sr)
    assert env.size == times.size
    assert env.max() == pytest.approx(1.0)
    bpm = rop.estimate_bpm(env, sr)
    assert bpm is not None and 115.0 <= bpm <= 125.0
    onsets = rop.detect_onsets(env, times)
    assert len(onsets) >= 12
    for t in onsets:
        assert min(abs(t - tt) for tt in true_times) <= 0.05


def test_silence(tmp_path):
    p = tmp_path / "silence.wav"
    _write_wav(p, np.zeros(int(2.0 * SR)))
    samples, sr = rop.load_wav_mono(str(p))
    env, times = rop.onset_envelope(samples, sr)
    assert rop.detect_onsets(env, times) == []
    assert rop.estimate_bpm(env, sr) is None


def test_stereo_to_mono(tmp_path):
    x, _ = _click_track(n_beats=8, dur=4.0)
    p = tmp_path / "stereo.wav"
    _write_wav(p, np.stack([x, x * 0.5], axis=1))
    samples, sr = rop.load_wav_mono(str(p))
    assert samples.ndim == 1
    assert sr == SR
    env, times = rop.onset_envelope(samples, sr)
    assert len(rop.detect_onsets(env, times)) >= 6


def test_probe_shot_windows(tmp_path):
    x, _ = _click_track()
    p = tmp_path / "clicks.wav"
    _write_wav(p, x)
    shots = [
        {"id": "s1", "start": 0.0, "end": 2.0},
        {"id": "s2", "start": 2.0, "end": 4.0},
        {"id": "s3", "start": 5.95, "end": 6.1},
    ]
    result = rop.probe(str(p), shots=shots)
    assert set(result) >= {"source", "sr", "bpm", "onsets", "shots"}
    assert result["sr"] == SR
    by_id = {s["id"]: s for s in result["shots"]}
    for sid, lo, hi in (("s1", 0.0, 2.0), ("s2", 2.0, 4.0), ("s3", 5.95, 6.1)):
        beats = by_id[sid]["beats"]
        assert beats, sid
        assert all(lo <= b < hi for b in beats)
    assert not (set(by_id["s1"]["beats"]) & set(by_id["s2"]["beats"]))
    assert by_id["s3"]["strongest"] is None or 5.95 <= by_id["s3"]["strongest"] < 6.1


def test_cli_writes_json(tmp_path):
    x, _ = _click_track(dur=4.0, n_beats=8)
    wav = tmp_path / "music.wav"
    _write_wav(wav, x)
    breakdown = tmp_path / "breakdown.json"
    breakdown.write_text(json.dumps({
        "shots": [
            {"id": "a", "start": 0.0, "end": 1.0},
            {"shot_id": "b", "start": 1.0, "end": 2.0},
            {"id": "c", "start": 2.0},
        ]
    }))
    out = tmp_path / "onset_beats.json"
    proc = subprocess.run(
        [sys.executable, str(HERE / "rea_onset_probe.py"), str(wav),
         "--breakdown", str(breakdown), "-o", str(out)],
        capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["sr"] == SR
    assert isinstance(data["bpm"], float)
    assert [s["id"] for s in data["shots"]] == ["a", "b"]
    assert all(len(s["beats"]) == 0 or 0.0 <= min(s["beats"]) for s in data["shots"])
    assert proc.stdout.startswith("DONE ")
