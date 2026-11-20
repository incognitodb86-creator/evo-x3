"""Tests for rea_color_match (REA C6) -- mocked ffmpeg/ffprobe, synthetic frames.

No real ffmpeg/ffprobe binaries and no disk video fixtures: subprocess.run and
subprocess.check_output are patched, frames are synthetic numpy arrays.
"""

import json
import re
import subprocess

import numpy as np
import pytest

import rea_color_match as rcm

WIDTH, HEIGHT, DURATION = 8, 6, 4.0

CHANNEL_EXPR = re.compile(
    r"([rgb])='clip\(\(val([+-][\d.]+)\)\*([\d.]+)([+-][\d.]+),0,255\)'"
)


class FakeFfmpeg:
    """Stand-in for ffprobe (check_output) and ffmpeg (run)."""

    def __init__(self, width=WIDTH, height=HEIGHT, duration=DURATION):
        self.width = width
        self.height = height
        self.duration = duration
        self.levels = {}      # path -> list of solid levels, cycled per call
        self.seen = {}        # path -> call count
        self.runs = []
        self.probes = []

    def set_levels(self, path, levels):
        self.levels[str(path)] = list(levels)

    # ffprobe -------------------------------------------------------------
    def check_output(self, cmd, text=False, **kwargs):
        self.probes.append([str(c) for c in cmd])
        payload = {
            "streams": [{
                "width": self.width,
                "height": self.height,
                "r_frame_rate": "24/1",
                "nb_frames": str(int(self.duration * 24)),
            }],
            "format": {"duration": f"{self.duration:.3f}"},
        }
        return json.dumps(payload) if text else json.dumps(payload).encode()

    # ffmpeg --------------------------------------------------------------
    def run(self, cmd, *args, **kwargs):
        cmd = [str(c) for c in cmd]
        self.runs.append(cmd)
        stdout = b""
        if "rawvideo" in cmd:
            path = cmd[cmd.index("-i") + 1]
            levels = self.levels.get(path) or [128]
            idx = self.seen.get(path, 0)
            self.seen[path] = idx + 1
            level = levels[idx % len(levels)]
            stdout = np.full((self.height, self.width, 3), level, dtype=np.uint8).tobytes()
        return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr=b"")

    def frame_runs(self):
        return [c for c in self.runs if "rawvideo" in c]

    def master_runs(self):
        return [c for c in self.runs if "rawvideo" not in c]


@pytest.fixture
def fake(monkeypatch):
    ff = FakeFfmpeg()
    monkeypatch.setattr(rcm.subprocess, "check_output", ff.check_output)
    monkeypatch.setattr(rcm.subprocess, "run", ff.run)
    return ff


# --- channel_stats ---------------------------------------------------------

def test_channel_stats_solid_color():
    frames = [np.full((4, 5, 3), (10, 20, 30), dtype=np.uint8) for _ in range(2)]
    mean, std = rcm.channel_stats(frames)
    assert mean.shape == (3,) and std.shape == (3,)
    assert np.allclose(mean, [10.0, 20.0, 30.0])
    assert np.allclose(std, 0.0)


def test_channel_stats_mix_of_solids_spans_frames():
    a = np.zeros((2, 2, 3), dtype=np.uint8)
    b = np.full((2, 2, 3), 100, dtype=np.uint8)
    mean, std = rcm.channel_stats([a, b])
    assert np.allclose(mean, 50.0)
    assert np.allclose(std, 50.0)


def test_channel_stats_empty():
    mean, std = rcm.channel_stats([])
    assert np.allclose(mean, 0.0) and np.allclose(std, 0.0)


# --- transfer_expr ---------------------------------------------------------

def _parse_channels(expr):
    # "(val-40)*2+128" means out = (val - 40) * 2 + 128
    parsed = {ch: (-float(m), float(g), float(a))
              for ch, m, g, a in CHANNEL_EXPR.findall(expr)}
    assert set(parsed) == {"r", "g", "b"}
    return parsed


def test_transfer_expr_dark_clip_moves_to_reference():
    rng = np.random.default_rng(7)
    dark = np.clip(rng.normal(40.0, 8.0, size=(64, 64, 3)), 0, 255).astype(np.uint8)
    bright = np.clip(rng.normal(128.0, 32.0, size=(64, 64, 3)), 0, 255).astype(np.uint8)
    src = rcm.channel_stats([dark])
    ref = rcm.channel_stats([bright])

    expr = rcm.transfer_expr(src, ref)
    assert expr is not None and expr.startswith("lutrgb=")

    parsed = _parse_channels(expr)
    out = dark.astype(np.float64)
    for i, ch in enumerate("rgb"):
        mean, gain, add = parsed[ch]
        # the expression keeps the documented math
        assert mean == pytest.approx(src[0][i], abs=1e-3)
        assert gain == pytest.approx(ref[1][i] / src[1][i], rel=1e-3)
        assert add == pytest.approx(ref[0][i], abs=1e-3)
        out[..., i] = np.clip((out[..., i] - mean) * gain + add, 0, 255)

    # the same math in numpy lands on the reference mean
    assert np.allclose(out.mean(axis=(0, 1)), ref[0], atol=2.0)
    assert out.mean() > dark.mean() + 50


def test_transfer_expr_std_floor_and_clip():
    # zero-variance source: std floor of 1.0 keeps the gain finite
    src = (np.array([30.0, 30.0, 30.0]), np.array([0.0, 0.0, 0.0]))
    ref = (np.array([128.0, 128.0, 128.0]), np.array([0.0, 0.0, 0.0]))
    expr = rcm.transfer_expr(src, ref)
    assert expr is not None
    for mean, gain, add in _parse_channels(expr).values():
        assert gain == pytest.approx(1.0)
        assert mean == pytest.approx(30.0)
        assert add == pytest.approx(128.0)
    assert expr.count(",0,255)") == 3


def test_transfer_expr_identical_stats_returns_none():
    stats = (np.array([90.0, 100.0, 110.0]), np.array([20.0, 20.0, 20.0]))
    assert rcm.transfer_expr(stats, stats) is None
    near = (np.array([91.0, 101.0, 109.0]), np.array([20.4, 19.6, 20.0]))
    assert rcm.transfer_expr(near, stats) is None


def test_transfer_expr_keeps_clip_when_only_std_differs():
    src = (np.array([90.0, 90.0, 90.0]), np.array([10.0, 10.0, 10.0]))
    ref = (np.array([90.5, 90.5, 90.5]), np.array([30.0, 30.0, 30.0]))
    assert rcm.transfer_expr(src, ref) is not None


# --- build_master_cmd ------------------------------------------------------

def _clip(path, trim=None, lut=None):
    return {"path": str(path), "trim_to_frames": trim, "lut": lut}


def test_build_master_cmd_two_clips_hard_cut():
    clips = [
        _clip("a.mp4", trim=48),
        _clip("b.mp4", lut="lutrgb=r='clip((val-30)*2+128,0,255)'"),
    ]
    cmd = rcm.build_master_cmd(clips, "master.mp4")
    joined = " ".join(cmd)

    assert cmd[0] == "ffmpeg"
    assert cmd.count("-i") == 2
    assert "concat=n=2:v=1:a=1" in joined
    assert "xfade" not in joined
    assert "trim=end_frame=48" in joined
    assert "setpts=PTS-STARTPTS" in joined
    assert "atrim=end=2" in joined          # 48 frames / 24 fps
    assert "asetpts=PTS-STARTPTS" in joined
    assert "amix" not in joined
    assert "volume=" not in joined
    assert "lutrgb=" in joined
    # trimmed clip gets labels, plain audio goes straight into concat
    assert "[v0][a0][v1][1:a]concat=n=2" in joined
    for token in (["-c:v", "libx264"], ["-crf", "16"], ["-pix_fmt", "yuv420p"],
                  ["-r", "24"], ["-c:a", "aac"], ["-b:a", "192k"]):
        assert cmd[cmd.index(token[0]):cmd.index(token[0]) + 2] == token
    assert cmd[-1] == "master.mp4"


def test_build_master_cmd_plain_clips_concat_raw_streams():
    joined = " ".join(rcm.build_master_cmd([_clip("a.mp4"), _clip("b.mp4")], "m.mp4"))
    assert "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[catv][cata]" in joined
    assert "trim" not in joined and "lutrgb" not in joined


def test_build_master_cmd_bgm_adds_amix_and_volume():
    clips = [_clip("a.mp4"), _clip("b.mp4")]
    cmd = rcm.build_master_cmd(clips, "master.mp4", bgm="music.wav")
    joined = " ".join(cmd)
    assert cmd.count("-i") == 3
    assert "music.wav" in cmd
    assert "amix" in joined
    assert "volume=-14dB" in joined
    assert "[cata][bgmvol]amix=inputs=2" in joined
    assert cmd[cmd.index("-map") + 1] == "[catv]"
    assert "[aout]" in cmd


def test_build_master_cmd_bgm_db_override():
    clips = [_clip("a.mp4")]
    joined = " ".join(rcm.build_master_cmd(clips, "m.mp4", bgm="m.wav", bgm_db=-12))
    assert "volume=-12dB" in joined


def test_build_master_cmd_needs_a_clip():
    with pytest.raises(ValueError):
        rcm.build_master_cmd([], "m.mp4")


# --- sample_frames ---------------------------------------------------------

def test_sample_frames_one_subprocess_per_frame(fake):
    fake.set_levels("a.mp4", [10, 60, 120, 180, 240])
    frames = rcm.sample_frames("a.mp4", n=5)
    assert len(frames) == 5
    assert len(fake.frame_runs()) == 5
    assert len(fake.probes) == 1
    for i, frame in enumerate(frames):
        assert frame.shape == (HEIGHT, WIDTH, 3)
        assert frame.dtype == np.uint8
        assert np.all(frame == [10, 60, 120, 180, 240][i])

    first = fake.frame_runs()[0]
    assert first[first.index("-ss") + 1] == "0.4"
    assert first.index("-ss") < first.index("-i")
    assert first[first.index("-frames:v") + 1] == "1"
    assert first[first.index("-f") + 1] == "rawvideo"
    assert first[first.index("-pix_fmt") + 1] == "rgb24"

    times = [float(c[c.index("-ss") + 1]) for c in fake.frame_runs()]
    assert times == sorted(times) and len(set(times)) == 5
    assert all(0.0 <= t < DURATION for t in times)


def test_sample_frames_zero(fake):
    assert rcm.sample_frames("a.mp4", n=0) == []
    assert fake.runs == []


# --- CLI -------------------------------------------------------------------

def test_cli_dry_run_prints_command(fake, capsys):
    fake.set_levels("a.mp4", [30, 34, 38, 42, 46])
    fake.set_levels("b.mp4", [140, 150, 160, 170, 180])
    code = rcm.main(["master.mp4", "a.mp4", "b.mp4", "--trim", "0=48",
                     "--bgm", "music.wav", "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert out.startswith("ffmpeg ")
    assert "concat=n=2:v=1:a=1" in out
    assert "xfade" not in out
    assert "trim=end_frame=48" in out
    assert "volume=-14dB" in out and "amix" in out
    assert "-crf 16" in out and "-r 24" in out
    assert out.rstrip().endswith("master.mp4")
    # only the non-reference clip gets a lut
    assert out.count("lutrgb=") == 1
    # dry run never runs the master
    assert fake.master_runs() == []
    assert len(fake.frame_runs()) == 10


def test_cli_dry_run_default_no_bgm(fake, capsys):
    code = rcm.main(["m.mp4", "a.mp4", "--dry-run"])
    assert code == 0
    out = capsys.readouterr().out
    assert "concat=n=1:v=1:a=1" in out
    assert "amix" not in out and "volume=" not in out


def test_cli_runs_master(fake, capsys):
    code = rcm.main(["master.mp4", "a.mp4", "b.mp4"])
    assert code == 0
    assert len(fake.master_runs()) == 1
    master = fake.master_runs()[0]
    assert master[-1] == "master.mp4"
    assert "-crf" in master
    out = capsys.readouterr().out
    assert out.startswith("DONE master.mp4")
