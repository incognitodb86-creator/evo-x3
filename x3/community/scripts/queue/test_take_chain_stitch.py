"""Unit tests for take_chain_stitch.py explicit clips stitch path (CPU only, no GPU)."""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import take_chain_stitch as tcs


def _make_dummy_mp4(path: pathlib.Path, duration: float = 2.0, w: int = 320, h: int = 240) -> None:
    """Build a tiny test mp4 with matching audio/video stream facts via ffmpeg."""
    r = subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "lavfi", "-i", f"testsrc=duration={duration:g}:size={w}x{h}:rate=24",
        "-f", "lavfi", "-i", f"anullsrc=duration={duration:g}:channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path),
    ], capture_output=True, text=True)
    assert r.returncode == 0, f"ffmpeg failed: {r.stderr}"


def test_explicit_clips_stitch_cli(tmp_path: pathlib.Path) -> None:
    c1 = tmp_path / "clip1.mp4"
    c2 = tmp_path / "clip2.mp4"
    _make_dummy_mp4(c1, duration=2.0)
    _make_dummy_mp4(c2, duration=2.0)

    out_dir = tmp_path / "_stitch"
    r = subprocess.run([
        sys.executable, str(pathlib.Path(tcs.__file__)),
        str(tmp_path), "--clips", str(c1), str(c2), "--name", "stitched_test",
    ], capture_output=True, text=True)
    assert r.returncode == 0, f"stitch failed: {r.stderr}\n{r.stdout}"
    film = out_dir / "stitched_test.mp4"
    assert film.is_file()
    assert film.stat().st_size > 0
    assert "STITCH OK cells=2" in r.stdout


def test_explicit_clips_stitch_api(tmp_path: pathlib.Path) -> None:
    c1 = tmp_path / "part_a.mp4"
    c2 = tmp_path / "part_b.mp4"
    _make_dummy_mp4(c1, duration=1.5)
    _make_dummy_mp4(c2, duration=1.5)

    out_dir = tmp_path / "custom_out"
    film = tcs.stitch_clips([c1, c2], out_dir, name="joined_film", xfade=0.06)
    assert film.is_file()
    assert film.name == "joined_film.mp4"
    assert film.stat().st_size > 0


def test_explicit_clips_missing_clip_fails(tmp_path: pathlib.Path) -> None:
    c1 = tmp_path / "exists.mp4"
    c2 = tmp_path / "missing.mp4"
    _make_dummy_mp4(c1, duration=1.0)

    with pytest.raises(SystemExit) as exc:
        tcs.explicit_clips([c1, c2])
    assert "MISSING CLIP" in str(exc.value)


def test_explicit_clips_fewer_than_two_fails(tmp_path: pathlib.Path) -> None:
    c1 = tmp_path / "only_one.mp4"
    _make_dummy_mp4(c1, duration=1.0)

    with pytest.raises(SystemExit) as exc:
        tcs.explicit_clips([c1])
    assert "need at least 2 clips" in str(exc.value)
