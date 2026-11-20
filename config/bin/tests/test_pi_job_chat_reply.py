"""L9: chat_reply emits MEDIA:<local clip> and DONE does not wait on QNAP."""
from __future__ import annotations

import importlib.util
import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PI_JOB = ROOT / "config" / "bin" / "pi-job"


def load_pi_job():
    loader = SourceFileLoader("pi_job", str(PI_JOB))
    spec = importlib.util.spec_from_loader("pi_job", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


@pytest.fixture
def pi_job():
    return load_pi_job()


def _make_run(tmp_path: Path, *, with_clip: bool = True, with_upscale: bool = True) -> Path:
    crun = tmp_path / "hermes_20261119_130049_render_d7aa"
    clip_dir = crun / "clip"
    clip_dir.mkdir(parents=True)
    clip = clip_dir / "clip.mp4"
    if with_clip:
        clip.write_bytes(b"fake-mp4")
    ok = {"clip": "clip/clip.mp4"}
    if with_upscale:
        ok["upscale"] = {"method": "RTX VideoSuperRes 2x ULTRA"}
    (clip_dir / "render_ok.json").write_text(json.dumps(ok), encoding="utf-8")
    return crun


def test_upscaled_clip_resolves_local_file(tmp_path, pi_job):
    crun = _make_run(tmp_path)
    got = pi_job._upscaled_clip(crun)
    assert got == (crun / "clip" / "clip.mp4").resolve()


def test_render_final_done_without_qnap_copy(tmp_path, pi_job):
    crun = _make_run(tmp_path)
    state, detail = pi_job._render_final(crun)
    assert state == "DONE"
    assert detail.endswith(f"/{crun.name}/clip/clip.mp4")
    assert "<video>" not in detail


def test_render_final_publishing_if_upscale_ok_but_file_missing(tmp_path, pi_job):
    crun = _make_run(tmp_path, with_clip=False)
    state, detail = pi_job._render_final(crun)
    assert state == "PUBLISHING"
    assert "local clip" in detail


def test_chat_reply_has_media_line_not_video_tag(tmp_path, monkeypatch, pi_job):
    crun = _make_run(tmp_path)
    job_id = "20261119-130049-render-d7aa"
    run_dir = tmp_path / "runs" / job_id
    run_dir.mkdir(parents=True)
    (run_dir / "meta.json").write_text(
        json.dumps({"role": "render", "run_name": crun.name}), encoding="utf-8"
    )
    (run_dir / "status").write_text("status=RENDER_QUEUED\n", encoding="utf-8")
    monkeypatch.setattr(pi_job, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(pi_job, "COMMUNITY_RUNS", crun.parent)
    state, text = pi_job._render_report(job_id)
    assert state == "DONE"
    assert f"MEDIA:{(crun / 'clip' / 'clip.mp4').resolve()}" in text
    assert "<video>" not in text
    assert "--- chat_reply (paste verbatim) ---" in text
    assert "[Open the 2x video](" in text


def test_run_pi_thinking_medium_on_alienpc_low_on_x3(pi_job, tmp_path, monkeypatch):
    """Swift on AlienPc codes with thinking medium (Derrick t2766s9752); the X3 fallback keeps low."""
    seen = []

    class _P:
        returncode = 0

    def fake_run(cmd, **kw):
        seen.append((kw["env"].get("FORGE_MODEL"), cmd[cmd.index("--thinking") + 1]))
        return _P()

    monkeypatch.setattr(pi_job.subprocess, "run", fake_run)
    monkeypatch.delenv("PI_JOB_FORCE_X3", raising=False)
    monkeypatch.setattr(pi_job, "_alienpc_gate_idle", lambda: True)
    rc, where = pi_job._run_pi(tmp_path, "60", "reply done", str(tmp_path), None)
    assert (rc, where) == (0, "alienpc") and seen[-1] == ("alienpc/coding_swift15_iq3s_esp", "medium")
    monkeypatch.setenv("PI_JOB_FORCE_X3", "1")
    rc, where = pi_job._run_pi(tmp_path, "60", "reply done", str(tmp_path), None)
    assert where == "x3" and seen[-1] == (None, "low")

def test_timeout_min_flag_and_defaults(pi_job, monkeypatch):
    started = {}
    monkeypatch.setattr(pi_job, "_start_detached", lambda role, target, prompt, **kw: started.update(role=role, **kw) or 0)
    assert pi_job.main(["code", "--timeout-min", "180", "/tmp", "task"]) == 0
    assert started["role"] == "code" and started["timeout_min"] == 180
    assert pi_job.main(["review", "/tmp", "task"]) == 0
    assert started["timeout_min"] is None
    with pytest.raises(SystemExit):
        pi_job.main(["code", "--timeout-min", "600", "/tmp", "task"])
    assert pi_job._job_timeout_s({}, 3600) == "3600"
    assert pi_job._job_timeout_s({"timeout_s": 10800}, 3600) == "10800"
    assert pi_job._timeout_note(0, {}, 3600) == ""
    assert "timed_out_after=180m" in pi_job._timeout_note(124, {"timeout_s": 10800}, 3600)
