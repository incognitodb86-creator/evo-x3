"""RP3 tests: exact last_frame.png extraction via ffprobe frame count and chain_start_still() reuse/fallback."""
import importlib
import json
import os
import sys
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
PARODY = SCRIPTS / "parody"
for p in (SCRIPTS, PARODY):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import run_queue as rq
import render_writer_pipeline as rwp


def test_extract_last_frame_selects_exact_last_index(tmp_path):
    mp4 = tmp_path / "clip.mp4"
    mp4.write_bytes(b"fake-mp4")
    out = tmp_path / "last_frame.png"
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "ffprobe" in os.path.basename(cmd[0]).lower():
            return mock.Mock(returncode=0, stdout=json.dumps({"streams": [{"nb_read_frames": "124"}]}), stderr="")
        # ffmpeg call: create the output file
        Path(cmd[-1]).write_bytes(b"\x89PNG\r\n\x1a\nlastframe")
        return mock.Mock(returncode=0, stdout=b"", stderr=b"")

    with mock.patch.object(rq.subprocess, "run", side_effect=fake_run):
        res = rq.extract_last_frame(str(mp4), str(out))

    assert res == str(out)
    assert out.is_file()
    assert len(calls) == 2
    assert "-count_frames" in calls[0]
    assert "select=eq(n\\,123)" in calls[1]
    assert calls[1][-1] == str(out)


def test_extract_last_frame_falls_back_to_nb_frames_and_handles_failure(tmp_path):
    mp4 = tmp_path / "clip.mp4"
    mp4.write_bytes(b"fake-mp4")
    out = tmp_path / "last_frame.png"
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "ffprobe" in os.path.basename(cmd[0]).lower():
            return mock.Mock(returncode=0, stdout=json.dumps({"streams": [{"nb_read_frames": "N/A", "nb_frames": "49"}]}), stderr="")
        Path(cmd[-1]).write_bytes(b"pngbytes")
        return mock.Mock(returncode=0, stdout=b"", stderr=b"")

    with mock.patch.object(rq.subprocess, "run", side_effect=fake_run):
        res = rq.extract_last_frame(str(mp4), str(out))
    assert res == str(out)
    assert "select=eq(n\\,48)" in calls[1]

    # Failure returns None without raising
    with mock.patch.object(rq.subprocess, "run", return_value=mock.Mock(returncode=1, stdout="", stderr="err")):
        assert rq.extract_last_frame(str(mp4), str(tmp_path / "missing.png")) is None


def test_chain_start_still_uses_last_frame_png_when_present(tmp_path):
    prev_run = tmp_path / "prev"
    clip_dir = prev_run / "clip"
    clip_dir.mkdir(parents=True)
    (clip_dir / "clip.mp4").write_bytes(b"mp4")
    lf = clip_dir / "last_frame.png"
    lf.write_bytes(b"\x89PNGexact")
    run_dir = tmp_path / "next"
    run_dir.mkdir()
    events = []

    with mock.patch.object(rwp.subprocess, "run") as mrun:
        got = rwp.chain_start_still(prev_run, "/fallback/still.png", run_dir, lambda e, d=None: events.append((e, d)))

    assert got == str(lf)
    assert not mrun.called
    assert any(e == "chain_last_frame" and d.get("prev_last_frame") == str(lf) for e, d in events)


def test_chain_start_still_falls_back_to_ffmpeg_sseof_when_no_last_frame(tmp_path):
    prev_run = tmp_path / "prev"
    clip_dir = prev_run / "clip"
    clip_dir.mkdir(parents=True)
    mp4 = clip_dir / "clip.mp4"
    mp4.write_bytes(b"mp4")
    run_dir = tmp_path / "next"
    run_dir.mkdir()
    calls = []

    def fake_ffmpeg(cmd, **kwargs):
        calls.append(cmd)
        Path(cmd[-1]).write_bytes(b"\x89PNGfallback")
        return mock.Mock(returncode=0)

    with mock.patch.object(rwp.subprocess, "run", side_effect=fake_ffmpeg):
        got = rwp.chain_start_still(prev_run, "/fallback/still.png", run_dir, lambda *a: None)

    expected = run_dir / "start_still_from_prev.png"
    assert got == str(expected)
    assert len(calls) == 1
    assert "-sseof" in calls[0] and "-0.1" in calls[0]
    assert str(mp4) in calls[0]
