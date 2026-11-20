"""REA C4-C7 tests for rea_parody_remake (plan + status + flux + build + queue + assemble) -- offline: canned
vision read, monkeypatched onset probe, mocked flux_still, subprocess.run and time.sleep."""

from __future__ import annotations

import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import build_request as br
import flux_still as fs
import rea_parody_remake as rr
import render_writer_pipeline as wp

ADULT_READ = {"read": {"people": 1, "description": "a woman in a silk robe on a velvet couch", "garments": ["robe"]}}
YOUTH_READ = {"read": {"people": 1, "description": "a little girl waving on the couch", "garments": []}}


def _click_wav(path, seconds=22.0, sr=16000, every=0.5):
    """16-bit mono click track: a short click every `every` seconds."""
    n = int(seconds * sr)
    samples = [0] * n
    step = int(every * sr)
    for i in range(0, n, step):
        for k in range(min(90, n - i)):
            samples[i + k] = int(12000 * math.sin(2 * math.pi * 1800 * k / sr))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))


def _breakdown():
    return {
        "shots": [
            {"id": "shot_001", "start": 0.0, "end": 6.583, "camera": "slow push in",
             "sfx": ["page turn"]},
            {"id": "shot_002", "start": 6.583, "end": 20.583, "camera": "orbit"},
        ],
        "speech": {"lines": [
            {"start": 0.5, "end": 5.0, "text": " ".join(f"w{i}" for i in range(31))},
            {"start": 7.0, "end": 9.0, "text": "only three words"},
            {"start": 60.0, "end": 61.0, "text": "out of every window"},
        ]},
    }


@pytest.fixture
def runs_root(tmp_path, monkeypatch):
    root = tmp_path / "runs"
    root.mkdir()
    monkeypatch.setenv("REA_RUNS_ROOT", str(root))
    return root


@pytest.fixture
def rea_dir(tmp_path):
    """Fake rea-video decomposition folder: breakdown.json, two JPEG keyframes, a click track."""
    from PIL import Image

    rea = tmp_path / "rea_source"
    (rea / "shots").mkdir(parents=True)
    (rea / "stems").mkdir()
    (rea / "breakdown.json").write_text(json.dumps(_breakdown()), encoding="utf-8")
    for sid in ("shot_001", "shot_002"):
        Image.new("RGB", (64, 96), (180, 40, 40)).save(rea / "shots" / f"{sid}_first.jpg", format="JPEG")
    _click_wav(rea / "stems" / "music.wav")
    return rea


@pytest.fixture
def canned(monkeypatch):
    """Stub _ensure_still_read_raw: writes a canned read as still_read.json and counts calls per shot dir."""
    calls = []

    def fake(shot_dir, still, still_read_src, client, cfg, log):
        calls.append(shot_dir)
        (shot_dir / "still_read.json").write_text(json.dumps(fake.read), encoding="utf-8")
        return json.loads(json.dumps(fake.read))

    fake.read = ADULT_READ
    fake.calls = calls
    monkeypatch.setattr(wp, "_ensure_still_read_raw", fake)
    return fake


@pytest.fixture
def probe(monkeypatch):
    """Stub rea_onset_probe.probe so no audio analysis runs in the suite."""
    seen = []

    def fake_probe(wav_path, shots=None):
        seen.append({"wav": wav_path, "shots": list(shots or [])})
        by_shot = [
            {"id": "shot_001", "beats": [1.0, 2.5, 4.0], "strongest": 2.5},
            # 16.667 s is 1 frame from the plain 243-frame cut inside shot_002 (start 6.583 s)
            {"id": "shot_002", "beats": [9.9, 16.667], "strongest": 16.667},
        ]
        return {"source": wav_path, "sr": 16000, "bpm": 120.0, "onsets": [1.0, 2.5, 4.0, 9.9, 16.667],
                "shots": by_shot}

    monkeypatch.setattr(rr.rea_onset_probe, "probe", fake_probe)
    return seen


def _argv(batch, rea_dir, *extra):
    return ["plan", str(batch), "--rea-dir", str(rea_dir), "--names", "Sydney Sweeney as Star", *extra]


def _briefs(batch):
    return {p.parent.name: json.loads(p.read_text(encoding="utf-8"))
            for p in (batch / "shots").glob("*/shot_brief.json")}


# --- plan --------------------------------------------------------------------

def test_plan_two_shots_isolated_dirs_with_own_files(runs_root, rea_dir, canned, probe, capsys):
    batch = runs_root / "rea_b1"
    assert rr.main(_argv(batch, rea_dir)) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == f"READY plan {batch} shots=2 parts=3"

    for i, sid in enumerate(("shot_001", "shot_002")):
        shot_dir = batch / "shots" / sid
        assert (shot_dir / "_inputs" / f"{sid}_first.jpg").is_file()
        assert (shot_dir / "raw_still_read.json").is_file()
        assert not (shot_dir / "still_read.json").exists()  # renamed for the later H3 build
        assert not (shot_dir / "clip_NOT_READY.txt").exists()
        # isolation: no other shot's artifacts leaked into this shot dir
        assert [p.name for p in (shot_dir / "_inputs").iterdir()] == [f"{sid}_first.jpg"]
        assert len(canned.calls) == 2
        assert canned.calls[i] == shot_dir

    assert (batch / "parody_cast_lock.json").is_file()
    card = (batch / "batch_card.md").read_text(encoding="utf-8")
    assert "Reply GO to run this batch." in card and "| shot_002a |" in card

    # onsets were probed from the stems and saved into the batch dir, not into the REA folder
    assert (batch / "onset_beats.json").is_file()
    assert not (rea_dir / "onset_beats.json").exists()
    assert len(probe) == 1 and probe[0]["wav"].endswith("stems/music.wav")

    briefs = _briefs(batch)
    assert set(briefs) == {"shot_001", "shot_002"}
    assert briefs["shot_001"]["seed"] == rr.SEED_BASE
    assert briefs["shot_002"]["seed"] == rr.SEED_BASE + 1
    assert briefs["shot_001"]["seed"] != briefs["shot_002"]["seed"]


def test_plan_shot_brief_contents(runs_root, rea_dir, canned, probe):
    batch = runs_root / "rea_b2"
    assert rr.main(_argv(batch, rea_dir)) == 0
    briefs = _briefs(batch)

    b1, b2 = briefs["shot_001"], briefs["shot_002"]
    assert b1["seconds"] == pytest.approx(6.583) and b1["shot_id"] == "shot_001"
    assert len(b1["parts"]) == 1 and b1["parts"][0]["frames"] % 17 == 5
    # 14.0 s: two parts, and the 16.667 s beat (absolute) moves the cut
    assert len(b2["parts"]) == 2
    assert [p["suffix"] for p in b2["parts"]] == ["a", "b"]
    assert b2["parts"][0]["trim_to_frames"] == int(round((16.667 - 6.583) * br.H3_FPS))
    assert b2["camera_h3_vocab"] == "medium orbit with medium amplitude"  # plain "orbit", no speed/amplitude words
    assert b1["camera_h3_vocab"] == "slow push-in with medium amplitude"
    assert b1["beats"] == [1.0, 2.5, 4.0] and b2["beats"] == [9.9, 16.667]
    assert b1["sfx"] == ["page turn"] and b2["sfx"] == []
    assert len(b1["dialogue"].split()) == 25  # cut to 25 words
    assert b2["dialogue"] == "only three words"


def test_plan_youth_cue_stops_the_batch(runs_root, rea_dir, canned, probe, capsys):
    canned.read = YOUTH_READ
    batch = runs_root / "rea_b3"
    assert rr.main(_argv(batch, rea_dir)) == 3
    out = capsys.readouterr().out
    assert "NOT_READY 18+ gate shot_001:" in out
    assert (batch / "shots" / "shot_001" / "clip_NOT_READY.txt").is_file()
    # the remaining shot never got a vision read, and no later stage ran for the batch
    assert [c.name for c in canned.calls] == ["shot_001"]
    assert not (batch / "shots" / "shot_002" / "raw_still_read.json").exists()
    assert not (batch / "parody_cast_lock.json").exists()
    assert not (batch / "batch_card.md").exists()


def test_plan_missing_keyframe_not_ready_for_whole_batch(runs_root, rea_dir, canned, probe, capsys):
    (rea_dir / "shots" / "shot_002_first.jpg").unlink()
    (rea_dir / "shots" / "shot_001_first.jpg").rename(rea_dir / "shots" / "alt_first.jpg")
    bd = _breakdown()
    bd["shots"][0]["keyframe"] = "shots/alt_first.jpg"
    (rea_dir / "breakdown.json").write_text(json.dumps(bd), encoding="utf-8")
    batch = runs_root / "rea_b4"
    assert rr.main(_argv(batch, rea_dir)) == 3
    assert "NOT_READY keyframe shot_002" in capsys.readouterr().out
    assert canned.calls == []


def test_plan_cast_lock_parody_and_oc(runs_root, rea_dir, canned, probe):
    batch = runs_root / "rea_b5"
    assert rr.main(_argv(batch, rea_dir)) == 0
    lock = json.loads((batch / "parody_cast_lock.json").read_text(encoding="utf-8"))
    assert lock["lane"] == "parody"
    assert lock["h3_identity"]["allow_audio_ref"] is False

    batch2 = runs_root / "rea_b6"
    assert rr.main(["plan", str(batch2), "--rea-dir", str(rea_dir), "--character", "FCSydny"]) == 0
    lock2 = json.loads((batch2 / "parody_cast_lock.json").read_text(encoding="utf-8"))
    assert lock2["lane"] == "oc"
    assert lock2["h3_identity"]["allow_audio_ref"] is True


def test_plan_shot_selection_subset(runs_root, rea_dir, canned, probe, capsys):
    batch = runs_root / "rea_b7"
    argv = ["plan", str(batch), "--rea-dir", str(rea_dir), "--character", "FCMegan",
            "--shots", "shot_002", "--aspect", "16:9"]
    assert rr.main(argv) == 0
    assert capsys.readouterr().out.strip().endswith("shots=1 parts=2")
    assert [c.name for c in canned.calls] == ["shot_002"]
    lock = json.loads((batch / "parody_cast_lock.json").read_text(encoding="utf-8"))
    assert lock["canvas"] == [1344, 768]


# --- batch dir validation ----------------------------------------------------

def test_batch_dir_outside_runs_root_is_refused(runs_root, rea_dir, canned, capsys):
    outside = runs_root.parent / "rea_elsewhere"
    assert rr.main(_argv(outside, rea_dir)) == 2
    assert "NOT_READY batch_dir" in capsys.readouterr().out
    assert canned.calls == []

    (runs_root / "b1").mkdir()
    assert rr.main(_argv(runs_root / "b1", rea_dir)) == 2  # wrong prefix
    assert rr.main(_argv("rea_relative", rea_dir)) == 2  # not absolute
    assert not (runs_root / "b1" / "shots").exists()


def test_plan_needs_names_or_character(runs_root, rea_dir, canned, capsys):
    assert rr.main(["plan", str(runs_root / "rea_b8"), "--rea-dir", str(rea_dir)]) == 2
    assert "NOT_READY cast" in capsys.readouterr().out


# --- status ------------------------------------------------------------------

def test_status_prints_both_shots(runs_root, rea_dir, canned, probe, capsys):
    batch = runs_root / "rea_b9"
    assert rr.main(_argv(batch, rea_dir)) == 0
    capsys.readouterr()
    (batch / "shots" / "shot_002" / "flux_prompt.txt").write_text("p", encoding="utf-8")
    (batch / "shots" / "shot_002" / "build_report.json").write_text(
        json.dumps({"status": "READY"}), encoding="utf-8")

    assert rr.main(["status", str(batch)]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("shot_001 ") and lines[1].startswith("shot_002 ")
    assert "raw_still_read=yes" in lines[0] and "flux_prompt=no" in lines[0]
    assert "flux_prompt=yes" in lines[1] and "build=READY" in lines[1]
    assert "edited=no" in lines[1] and "render_ok=no" in lines[1] and "prose=no" in lines[1]


def test_status_empty_batch(runs_root, capsys):
    batch = runs_root / "rea_b10"
    (batch / "shots").mkdir(parents=True)
    assert rr.main(["status", str(batch)]) == 0
    assert "shots=0" in capsys.readouterr().out


# --- flux (C5) -----------------------------------------------------------------

@pytest.fixture
def flux_mocks(monkeypatch):
    """Stub flux_still.build_flux_still / queue_flux_still: record kwargs, hand back a READY rep / a still."""
    state = {"builds": [], "queues": []}

    def fake_build(run_dir, prompt_text, mode="t2i", **kw):
        Path(run_dir).mkdir(parents=True, exist_ok=True)
        state["builds"].append({"run_dir": Path(run_dir), "prompt": prompt_text, "mode": mode, **kw})
        return {"status": "READY", "mode": mode, "seed": kw.get("seed")}

    def fake_queue(run_dir, **kw):
        state["queues"].append(Path(run_dir))
        still = Path(run_dir) / "still" / "still.png"
        still.parent.mkdir(parents=True, exist_ok=True)
        still.write_bytes(b"fake png bytes")
        return {"rc": 0, "still": str(still)}

    monkeypatch.setattr(fs, "build_flux_still", fake_build)
    monkeypatch.setattr(fs, "queue_flux_still", fake_queue)
    return state


def _flux_batch(runs_root, rea_dir, canned, probe, name):
    """A planned batch whose two shots have Hermes flux prompts."""
    batch = runs_root / name
    assert rr.main(_argv(batch, rea_dir)) == 0
    for sid in ("shot_001", "shot_002"):
        (batch / "shots" / sid / "flux_prompt.txt").write_text(f"flux prompt {sid}", encoding="utf-8")
    return batch


def test_flux_queue_without_yes_derrick_exits_3_with_no_calls(runs_root, rea_dir, canned, probe, flux_mocks, capsys):
    batch = _flux_batch(runs_root, rea_dir, canned, probe, "rea_f1")
    assert rr.main(["flux", str(batch), "--queue"]) == 3
    assert "--queue requires --yes-derrick" in capsys.readouterr().out
    assert flux_mocks["builds"] == [] and flux_mocks["queues"] == []
    assert not (batch / "shots" / "shot_001" / "_inputs" / "shot_001_edited.png").exists()


def test_flux_dry_run_one_call_per_shot_with_mode_and_seed(runs_root, rea_dir, canned, probe, flux_mocks, capsys):
    batch = _flux_batch(runs_root, rea_dir, canned, probe, "rea_f2")
    # the cast lock's shot override can force the pose template for one shot
    lock = json.loads((batch / "parody_cast_lock.json").read_text(encoding="utf-8"))
    lock["shot_overrides"][1]["flux_mode"] = "new_pose"
    (batch / "parody_cast_lock.json").write_text(json.dumps(lock), encoding="utf-8")
    capsys.readouterr()

    assert rr.main(["flux", str(batch)]) == 0
    builds = flux_mocks["builds"]
    assert [b["run_dir"] for b in builds] == [batch / "shots" / "shot_001" / "flux",
                                              batch / "shots" / "shot_002" / "flux"]
    assert [b["mode"] for b in builds] == ["rea_edit", "rea_pose"]  # new_pose override wins
    assert [b["seed"] for b in builds] == [rr.SEED_BASE, rr.SEED_BASE + 1]  # the shot briefs' seeds
    assert all(b["dry_run"] is True for b in builds)
    assert [b["prompt"] for b in builds] == ["flux prompt shot_001", "flux prompt shot_002"]
    assert builds[0]["width"] == 768 and builds[0]["height"] == 1344  # the cast lock canvas
    assert builds[0]["image"] == str(batch / "shots" / "shot_001" / "_inputs" / "shot_001_first.jpg")
    assert builds[0]["names"] == ["Sydney Sweeney as Star"] and builds[0]["character"] is None
    assert flux_mocks["queues"] == []  # dry run never queues
    assert "READY flux" in capsys.readouterr().out


def test_flux_hybrid_cast_lock_passes_085_07_and_prodigy_lora(runs_root, rea_dir, canned, probe, flux_mocks):
    batch = _flux_batch(runs_root, rea_dir, canned, probe, "rea_f3")
    lock = json.loads((batch / "parody_cast_lock.json").read_text(encoding="utf-8"))
    lock["hybrid"] = True
    (batch / "parody_cast_lock.json").write_text(json.dumps(lock), encoding="utf-8")

    assert rr.main(["flux", str(batch)]) == 0
    for b in flux_mocks["builds"]:
        assert b["refmod_strength"] == 0.85
        assert b["retention"] == "partially_preserved (0.7)"
        assert b["loras"] == [{"name": lock["flux_identity"]["lora"], "strength": 0.60}]
        assert b["loras"][0]["name"].endswith("_prodigy.safetensors")
        assert b["refmods"] == [lock["flux_identity"]["refmod"]]


def test_flux_missing_prompt_skips_shot_and_other_continues(runs_root, rea_dir, canned, probe, flux_mocks, capsys):
    batch = _flux_batch(runs_root, rea_dir, canned, probe, "rea_f4")
    (batch / "shots" / "shot_001" / "flux_prompt.txt").unlink()
    capsys.readouterr()

    assert rr.main(["flux", str(batch)]) == 3
    out = capsys.readouterr().out
    assert "NOT_READY shot_001 flux_prompt.txt missing" in out
    assert [b["run_dir"].parent.name for b in flux_mocks["builds"]] == ["shot_002"]


def test_flux_queue_copies_still_to_inputs_edited(runs_root, rea_dir, canned, probe, flux_mocks):
    batch = _flux_batch(runs_root, rea_dir, canned, probe, "rea_f5")
    assert rr.main(["flux", str(batch), "--queue", "--yes-derrick"]) == 0
    assert [q.name for q in flux_mocks["queues"]] == ["flux", "flux"]
    assert flux_mocks["builds"][0]["dry_run"] is False
    for sid in ("shot_001", "shot_002"):
        edited = batch / "shots" / sid / "_inputs" / f"{sid}_edited.png"
        assert edited.is_file() and edited.read_bytes() == b"fake png bytes"
        assert [p.name for p in (batch / "shots" / sid / "_inputs").iterdir() if "edited" in p.name] == [f"{sid}_edited.png"]


# --- build (C5) ----------------------------------------------------------------

@pytest.fixture
def proc(monkeypatch):
    """Stub subprocess.run: record the argv, write a canned build_report.json into the shot dir (cmd[2])."""
    state = {"calls": [], "fail": {}}  # fail: {shot_id: reason}

    def fake_run(cmd, *args, **kwargs):
        cmd = [str(c) for c in cmd]
        state["calls"].append(cmd)
        shot_dir = Path(cmd[2])
        if shot_dir.name in state["fail"]:
            report = {"status": "NOT_READY", "reason": state["fail"][shot_dir.name]}
        else:
            report = {"status": "READY"}
        (shot_dir / "build_report.json").write_text(json.dumps(report), encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(rr.subprocess, "run", fake_run)
    return state


def _buildable_batch(runs_root, rea_dir, canned, probe, flux_mocks, name):
    """Planned + flux-queued batch with Hermes prose for both shots (edited stills in _inputs)."""
    batch = _flux_batch(runs_root, rea_dir, canned, probe, name)
    assert rr.main(["flux", str(batch), "--queue", "--yes-derrick"]) == 0
    for sid in ("shot_001", "shot_002"):
        (batch / "shots" / sid / "hermes_prose.txt").write_text(f"prose for {sid}", encoding="utf-8")
    return batch


def test_build_parody_passes_prose_file_and_names_never_queue_flags(runs_root, rea_dir, canned, probe,
                                                                    flux_mocks, proc):
    batch = _buildable_batch(runs_root, rea_dir, canned, probe, flux_mocks, "rea_b11")
    # Hermes set the position in the brief when it wrote the prose
    brief_p = batch / "shots" / "shot_002" / "shot_brief.json"
    brief = json.loads(brief_p.read_text(encoding="utf-8"))
    brief["position"] = "mission"
    brief_p.write_text(json.dumps(brief), encoding="utf-8")

    assert rr.main(["build", str(batch)]) == 0
    assert len(proc["calls"]) == 2
    for cmd, sid in zip(proc["calls"], ("shot_001", "shot_002")):
        shot_dir = batch / "shots" / sid
        assert cmd[0] == sys.executable and cmd[1].endswith("render_writer_pipeline.py")
        assert cmd[2] == str(shot_dir)
        assert cmd[cmd.index("--prose-file") + 1] == str(shot_dir / "hermes_prose.txt")
        assert cmd[cmd.index("--still") + 1] == str(shot_dir / "_inputs" / f"{sid}_edited.png")
        assert cmd[cmd.index("--still-mode") + 1] == "guide"
        assert cmd[cmd.index("--position") + 1] == ("talk" if sid == "shot_001" else "mission")
        assert cmd[cmd.index("--ask") + 1] == f"rea remake {sid}"
        assert cmd[cmd.index("--frames") + 1] == str(_briefs(batch)[sid]["parts"][0]["frames"])
        assert cmd[cmd.index("--aspect") + 1] == "9:16"
        assert cmd[cmd.index("--names") + 1] == "Sydney Sweeney as Star"
        assert "--character" not in cmd
        for banned in ("--queue", "--yes-derrick", "--fix-once"):
            assert banned not in cmd


def test_build_not_ready_prints_stuck_and_records_both_shots(runs_root, rea_dir, canned, probe,
                                                             flux_mocks, proc, capsys):
    batch = _buildable_batch(runs_root, rea_dir, canned, probe, flux_mocks, "rea_b12")
    proc["fail"]["shot_001"] = "lint: beat map mismatch"
    capsys.readouterr()

    assert rr.main(["build", str(batch)]) == 3
    out = capsys.readouterr().out
    assert "STUCK shot_001 lint: beat map mismatch" in out
    assert "STUCK shot_002" not in out
    records = json.loads((batch / "build_status.json").read_text(encoding="utf-8"))
    assert {r["id"] for r in records} == {"shot_001", "shot_002"}
    by_id = {r["id"]: r for r in records}
    assert by_id["shot_001"]["status"] == "NOT_READY"
    assert by_id["shot_001"]["reason"] == "lint: beat map mismatch"
    assert by_id["shot_002"]["status"] == "READY"
    assert all(set(r) == {"id", "status", "reason"} for r in records)


def test_build_parody_args_have_no_audio_or_voice_flags(runs_root, rea_dir, canned, probe, flux_mocks, proc):
    batch = _buildable_batch(runs_root, rea_dir, canned, probe, flux_mocks, "rea_b13")
    assert rr.main(["build", str(batch)]) == 0
    for cmd in proc["calls"]:
        assert [a for a in cmd if "audio" in a.lower() or "voice" in a.lower()] == []


def test_build_skips_shots_without_still_or_prose(runs_root, rea_dir, canned, probe, flux_mocks, proc):
    batch = _buildable_batch(runs_root, rea_dir, canned, probe, flux_mocks, "rea_b14")
    (batch / "shots" / "shot_002" / "hermes_prose.txt").unlink()
    assert rr.main(["build", str(batch)]) == 0
    assert [cmd[2] for cmd in proc["calls"]] == [str(batch / "shots" / "shot_001")]
    records = json.loads((batch / "build_status.json").read_text(encoding="utf-8"))
    assert [r["id"] for r in records] == ["shot_001"]


# --- queue + assemble (C7) -----------------------------------------------------

QUEUE_SCRIPT = "/stub/queue-remote.sh"


class FakeRender:
    """One stubbed subprocess surface for queue-remote.sh, ffprobe and ffmpeg, plus the mocked sleep.

    `bash <script> <shot_dir> --yes-derrick` arms a shot; that shot's 2x `clip/render_ok.json` then shows up
    after N mocked sleeps (`ready`, None = never, so the watch times out). ffprobe answers with a fixed
    size/duration and ffmpeg answers the rawvideo probes with solid colors, so the color pass runs on synthetic
    pixels; the single master call just writes its output file the way ffmpeg would.
    """

    WIDTH, HEIGHT, DURATION = 8, 6, 4.0

    def __init__(self):
        self.queue_cmds = []      # {"shot", "cmd", "prior_ok": shots that already had a 2x when queued}
        self.masters = []         # the ffmpeg master argv (everything that is not a frame decode)
        self.frame_calls = []     # the ffmpeg rawvideo frame-decode argv
        self.probes = []          # the ffprobe argv
        self.levels = {}          # clip path -> solid RGB level (default 128)
        self.ready = {}           # shot id -> mocked sleeps before its 2x lands
        self.default_ready = 0    # 0 = there on the first check; None = the render never finishes
        self.fail_rc = {}         # shot id -> queue-remote.sh returncode
        self.sleeps = []          # every interval the watch asked to sleep
        self.max_pending = 0      # how many renders were outstanding at once
        self._pending = {}

    # --- ffmpeg (frame decodes + the master) and queue-remote.sh --------------
    def run(self, cmd, *args, **kwargs):
        cmd = [str(c) for c in cmd]
        if cmd and cmd[0] == "bash":
            return self._queue(cmd)
        stdout = b""
        if "rawvideo" in cmd:
            self.frame_calls.append(cmd)
            path = cmd[cmd.index("-i") + 1]
            level = int(self.levels.get(path, 128))
            stdout = np.full((self.HEIGHT, self.WIDTH, 3), level, dtype=np.uint8).tobytes()
        else:
            self.masters.append(cmd)
            Path(cmd[-1]).write_bytes(b"fake master mp4")
        return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr=b"")

    # --- ffprobe --------------------------------------------------------------
    def check_output(self, cmd, text=False, **kwargs):
        self.probes.append([str(c) for c in cmd])
        payload = {"streams": [{"width": self.WIDTH, "height": self.HEIGHT, "r_frame_rate": "24/1",
                                "nb_frames": str(int(self.DURATION * 24))}],
                   "format": {"duration": f"{self.DURATION:.3f}"}}
        return json.dumps(payload) if text else json.dumps(payload).encode()

    # --- the mocked time.sleep: renders land as the watch keeps polling --------
    def sleep(self, seconds):
        self.sleeps.append(float(seconds))
        for shot_dir in list(self._pending):
            self._pending[shot_dir] -= 1
            if self._pending[shot_dir] <= 0:
                del self._pending[shot_dir]
                self._finish(shot_dir)

    def _queue(self, cmd):
        shot_dir = Path(cmd[2])
        prior = sorted(p.name for p in shot_dir.parent.glob("shot_*")
                       if (p / "clip" / "render_ok.json").is_file())
        self.queue_cmds.append({"shot": shot_dir.name, "cmd": cmd, "prior_ok": prior})
        if self.fail_rc.get(shot_dir.name):
            return subprocess.CompletedProcess(cmd, int(self.fail_rc[shot_dir.name]),
                                               stdout="", stderr="refused: run dir is not READY")
        waits = self.ready.get(shot_dir.name, self.default_ready)
        if waits == 0:
            self._finish(shot_dir)
        elif waits:
            self._pending[shot_dir] = waits
            self.max_pending = max(self.max_pending, len(self._pending))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    def _finish(self, shot_dir):
        clip_dir = shot_dir / "clip"
        clip_dir.mkdir(parents=True, exist_ok=True)
        (clip_dir / "clip.mp4").write_bytes(b"fake 1x mp4")
        (clip_dir / "clip_2x.mp4").write_bytes(b"fake 2x mp4")
        (clip_dir / "render_ok.json").write_text(
            json.dumps({"clip": "clip/clip_2x.mp4", "upscale": {"scale": 2, "out": "clip/clip_2x.mp4"}}),
            encoding="utf-8")


@pytest.fixture
def media(monkeypatch):
    """Route queue-remote.sh, ffmpeg, ffprobe and time.sleep through one fake (rr and rcm share subprocess)."""
    fake = FakeRender()
    monkeypatch.setenv("REA_QUEUE_REMOTE", QUEUE_SCRIPT)
    monkeypatch.setattr(rr.subprocess, "run", fake.run)
    monkeypatch.setattr(rr.subprocess, "check_output", fake.check_output)
    monkeypatch.setattr(rr.time, "sleep", fake.sleep)
    return fake


def _built_batch(runs_root, rea_dir, canned, probe, name):
    """A planned batch whose two shots have READY build reports (no render ran yet)."""
    batch = runs_root / name
    assert rr.main(_argv(batch, rea_dir)) == 0
    (batch / "build_status.json").write_text(json.dumps(
        [{"id": sid, "status": "READY", "reason": ""} for sid in ("shot_001", "shot_002")]), encoding="utf-8")
    return batch


def _queued_batch(runs_root, rea_dir, canned, probe, media, name):
    """A built batch whose two shots rendered their 2x clips through the `queue` stage."""
    batch = _built_batch(runs_root, rea_dir, canned, probe, name)
    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 0
    media.masters = []  # the assemble tests only look at the master call
    return batch


def _queue_records(batch):
    return json.loads((batch / "queue_status.json").read_text(encoding="utf-8"))


def _clip2x(batch, sid):
    return batch / "shots" / sid / "clip" / "clip_2x.mp4"


def _inputs(cmd):
    return [cmd[i + 1] for i, a in enumerate(cmd) if a == "-i"]


def _filter_of(cmd):
    return cmd[cmd.index("-filter_complex") + 1]


# --- queue (C7) -----------------------------------------------------------------

def test_queue_watch_defaults_match_the_plan():
    assert rr.QUEUE_REMOTE_SCRIPT == "/home/evo/AI/render/x3/queue-remote.sh"
    assert rr.QUEUE_POLL_SEC == 15.0 and rr.QUEUE_TIMEOUT_SEC == 40 * 60
    assert rr.queue_wait_params() == (15.0, 40 * 60.0)
    assert rr.publish_dir() == Path(rr.PUBLISH_DIR)


def test_queue_without_yes_derrick_exits_3_with_zero_calls(runs_root, rea_dir, canned, probe, media, capsys):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q1")
    assert rr.main(["queue", str(batch)]) == 3
    assert "--yes-derrick is required" in capsys.readouterr().out
    assert media.queue_cmds == [] and media.masters == []
    assert not (batch / "queue_status.json").exists()


def test_queue_two_ready_shots_in_order_one_at_a_time(runs_root, rea_dir, canned, probe, media, capsys):
    media.ready = {"shot_001": 1, "shot_002": 1}  # each 2x lands on the second check
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q2")
    capsys.readouterr()

    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 0
    assert [c["shot"] for c in media.queue_cmds] == ["shot_001", "shot_002"]
    for c, sid in zip(media.queue_cmds, ("shot_001", "shot_002")):
        assert c["cmd"] == ["bash", QUEUE_SCRIPT, str(batch / "shots" / sid), "--yes-derrick"]
    # one at a time: shot_002 was only submitted once shot_001's 2x was on disk, and nothing ran in parallel
    assert media.queue_cmds[0]["prior_ok"] == []
    assert media.queue_cmds[1]["prior_ok"] == ["shot_001"]
    assert media.max_pending == 1
    assert media.sleeps == [15.0, 15.0]  # the default 15 s poll

    records = _queue_records(batch)
    assert [r["id"] for r in records] == ["shot_001", "shot_002"]
    assert all(set(r) == {"id", "status", "clip"} and r["status"] == "DONE" for r in records)
    assert records[0]["clip"] == str(_clip2x(batch, "shot_001"))  # render_ok.json's "clip", not the 1x
    assert (batch / "shots" / "shot_001" / "clip" / "clip_2x.mp4").is_file()
    assert "READY queue" in capsys.readouterr().out


def test_queue_never_queues_a_shot_with_clip_not_ready(runs_root, rea_dir, canned, probe, media):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q3")
    (batch / "shots" / "shot_001" / "clip_NOT_READY.txt").write_text("NOT_READY 18+ gate shot_001\n",
                                                                    encoding="utf-8")
    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 0
    assert [c["shot"] for c in media.queue_cmds] == ["shot_002"]
    assert [r["id"] for r in _queue_records(batch)] == ["shot_002"]


def test_queue_skips_a_shot_whose_build_is_not_ready(runs_root, rea_dir, canned, probe, media):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q4")
    (batch / "build_status.json").write_text(json.dumps([
        {"id": "shot_001", "status": "NOT_READY", "reason": "lint: beat map mismatch"},
        {"id": "shot_002", "status": "READY", "reason": ""}]), encoding="utf-8")
    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 0
    assert [c["shot"] for c in media.queue_cmds] == ["shot_002"]


def test_queue_refuses_without_build_status(runs_root, rea_dir, canned, probe, media, capsys):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q5")
    (batch / "build_status.json").unlink()
    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 2
    assert "run build first" in capsys.readouterr().out
    assert media.queue_cmds == []


def test_queue_skips_a_shot_already_done_in_queue_status(runs_root, rea_dir, canned, probe, media):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q6")
    (batch / "queue_status.json").write_text(json.dumps(
        [{"id": "shot_001", "status": "DONE", "clip": str(_clip2x(batch, "shot_001"))}]), encoding="utf-8")
    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 0
    assert [c["shot"] for c in media.queue_cmds] == ["shot_002"]  # never queued twice
    assert [r["id"] for r in _queue_records(batch)] == ["shot_001", "shot_002"]  # the old DONE entry survived


def test_queue_timeout_marks_fail_and_continues(runs_root, rea_dir, canned, probe, media, monkeypatch, capsys):
    monkeypatch.setenv("REA_QUEUE_POLL_SEC", "1")
    monkeypatch.setenv("REA_QUEUE_TIMEOUT_SEC", "3")
    media.default_ready = None  # the 2x never lands
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q7")
    capsys.readouterr()

    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 3
    assert [c["shot"] for c in media.queue_cmds] == ["shot_001", "shot_002"]  # FAIL did not stop the batch
    assert media.sleeps == [1.0, 1.0, 1.0, 1.0]  # the env poll interval, not the 15 s default
    records = _queue_records(batch)
    assert [r["status"] for r in records] == ["FAIL", "FAIL"]
    assert records[0]["clip"] is None
    out = capsys.readouterr().out
    assert "FAIL clip shot_001" in out and "FAIL clip shot_002" in out


def test_queue_waits_for_the_upscale_object_not_just_render_ok(runs_root, rea_dir, canned, probe, media):
    media.default_ready = None
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q8")
    media.ready = {"shot_002": 0}
    ok = batch / "shots" / "shot_001" / "clip" / "render_ok.json"
    ok.parent.mkdir(parents=True, exist_ok=True)
    ok.write_text(json.dumps({"clip": "clip/clip.mp4"}), encoding="utf-8")  # a 1x-only render_ok

    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 3
    by_id = {r["id"]: r for r in _queue_records(batch)}
    assert by_id["shot_001"]["status"] == "FAIL" and by_id["shot_002"]["status"] == "DONE"


def test_queue_submit_failure_marks_fail_without_waiting(runs_root, rea_dir, canned, probe, media, capsys):
    media.fail_rc = {"shot_001": 3}
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q9")
    capsys.readouterr()

    assert rr.main(["queue", str(batch), "--yes-derrick"]) == 3
    assert media.queue_cmds[0]["shot"] == "shot_001" and len(media.queue_cmds) == 2
    assert media.sleeps == []  # a refused submit is reported at once, the watch never runs
    assert "FAIL clip shot_001" in capsys.readouterr().out


def test_queue_shot_option_queues_only_that_shot(runs_root, rea_dir, canned, probe, media, capsys):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_q10")
    assert rr.main(["queue", str(batch), "--yes-derrick", "--shot", "shot_002"]) == 0
    assert [c["shot"] for c in media.queue_cmds] == ["shot_002"]
    assert [r["id"] for r in _queue_records(batch)] == ["shot_002"]

    assert rr.main(["queue", str(batch), "--yes-derrick", "--shot", "shot_999"]) == 3
    assert "NOT_READY queue" in capsys.readouterr().out


# --- assemble (C7) ---------------------------------------------------------------

def test_assemble_one_ffmpeg_with_both_clips_in_order_and_the_pad_trim(runs_root, rea_dir, canned, probe,
                                                                      media, capsys):
    batch = _queued_batch(runs_root, rea_dir, canned, probe, media, "rea_a1")
    media.levels[str(_clip2x(batch, "shot_001"))] = 60
    media.levels[str(_clip2x(batch, "shot_002"))] = 200
    capsys.readouterr()

    assert rr.main(["assemble", str(batch)]) == 0
    assert len(media.masters) == 1
    cmd = media.masters[0]
    assert _inputs(cmd) == [str(_clip2x(batch, "shot_001")), str(_clip2x(batch, "shot_002"))]  # shot order
    assert cmd[-1] == str(batch / "final_2x.mp4")

    f = _filter_of(cmd)
    assert "concat=n=2:v=1:a=1" in f and "xfade" not in f
    # shot_001 renders exactly its 158 frames; the two-part 14.0 s shot renders 243+107 and is trimmed to 336
    assert f.count("trim=end_frame") == 1 and "trim=end_frame=336" in f and "atrim=end=14," in f
    assert f.count("lutrgb") == 1 and "[1:v]lutrgb" in f  # only the second clip is matched to the first
    assert "amix" not in f and "volume=" not in f  # no music without --bgm
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-2] == f"DONE assemble {batch / 'final_2x.mp4'}"
    assert out[-1] == f"MEDIA:{batch / 'final_2x.mp4'}"


def test_assemble_bgm_mixes_the_rea_stems_at_minus_14(runs_root, rea_dir, canned, probe, media):
    batch = _queued_batch(runs_root, rea_dir, canned, probe, media, "rea_a2")
    assert rr.main(["assemble", str(batch), "--bgm"]) == 0
    cmd = media.masters[0]
    assert _inputs(cmd)[-1] == str(rea_dir / "stems" / "music.wav")  # the rea_dir recorded in the cast lock
    f = _filter_of(cmd)
    assert "amix=inputs=2" in f and "volume=-14dB" in f


def test_assemble_bgm_refuses_when_no_rea_dir_is_recorded(runs_root, rea_dir, canned, probe, media, capsys):
    batch = _queued_batch(runs_root, rea_dir, canned, probe, media, "rea_a3")
    lock = json.loads((batch / "parody_cast_lock.json").read_text(encoding="utf-8"))
    lock.pop("rea_dir", None)
    (batch / "parody_cast_lock.json").write_text(json.dumps(lock), encoding="utf-8")
    assert rr.main(["assemble", str(batch), "--bgm"]) == 2
    assert "NOT_READY assemble bgm" in capsys.readouterr().out
    assert media.masters == []


def test_assemble_without_done_shots_is_not_ready(runs_root, rea_dir, canned, probe, media, capsys):
    batch = _built_batch(runs_root, rea_dir, canned, probe, "rea_a4")
    assert rr.main(["assemble", str(batch)]) == 2
    assert "no DONE shots" in capsys.readouterr().out
    assert media.masters == []


def test_assemble_publish_skips_cleanly_when_renders_dir_is_missing(runs_root, rea_dir, canned, probe, media,
                                                                   monkeypatch, tmp_path, capsys):
    assert rr.PUBLISH_DIR == "/srv/renders"
    monkeypatch.setenv("REA_PUBLISH_DIR", str(tmp_path / "missing" / "renders"))
    batch = _queued_batch(runs_root, rea_dir, canned, probe, media, "rea_a5")
    capsys.readouterr()

    assert rr.main(["assemble", str(batch), "--publish"]) == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert any("publish skipped" in line for line in out)
    assert out[-1] == f"MEDIA:{batch / 'final_2x.mp4'}"
    assert not (tmp_path / "missing").exists()  # nothing was created or half-copied


def test_assemble_publish_copies_the_master_when_the_dir_is_writable(runs_root, rea_dir, canned, probe, media,
                                                                    monkeypatch, tmp_path, capsys):
    pub = tmp_path / "renders"
    pub.mkdir()
    monkeypatch.setenv("REA_PUBLISH_DIR", str(pub))
    batch = _queued_batch(runs_root, rea_dir, canned, probe, media, "rea_a6")

    assert rr.main(["assemble", str(batch), "--publish"]) == 0
    dest = pub / "rea_a6_final_2x.mp4"
    assert dest.is_file() and dest.read_bytes() == (batch / "final_2x.mp4").read_bytes()
    assert f"PUBLISHED {dest}" in capsys.readouterr().out
