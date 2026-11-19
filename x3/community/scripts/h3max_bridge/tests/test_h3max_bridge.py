"""Offline unit tests for h3max_bridge (RV2, mocked llama-swap and ffmpeg)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from h3max_bridge import (
    BridgeValidationError,
    compile_prompt_via_llm,
    export_breakdown,
    pack_shots,
    parse_refmods,
    snap_frames,
    strip_video_audio,
)


def test_snap_frames_17k_plus_5_grid() -> None:
    assert snap_frames(5.0) == 124
    assert snap_frames(5.16) == 124
    assert snap_frames(8.0) == 192
    assert snap_frames(10.0) == 243
    assert snap_frames(15.0, max_frames=362) == 362
    for f in (124, 192, 243, 362):
        assert (f - 5) % 17 == 0

    with pytest.raises(ValueError, match="exceeds ceiling"):
        snap_frames(11.0, max_frames=243)


def test_pack_shots_splits_by_frame_and_audio_ceiling() -> None:
    breakdown = {
        "shots": [
            {
                "start": 0.0,
                "end": 4.5,
                "video": "s1.mp4",
                "keyframe": "k1.png",
                "audio_stems": ["v1.wav"],
                "audio_duration": 4.5,
            },
            {
                "start": 4.5,
                "end": 9.0,
                "video": "s2.mp4",
                "keyframe": "k2.png",
                "audio_stems": ["v1.wav"],
                "audio_duration": 4.5,
            },
            {
                "start": 9.0,
                "end": 14.0,
                "video": "s3.mp4",
                "keyframe": "k3.png",
                "audio_stems": ["v2.wav"],
                "audio_duration": 5.0,
            },
        ]
    }
    packs = pack_shots(breakdown, max_frames=243, max_audio_s=15.0)
    assert len(packs) == 2
    assert packs[0].frames == 226  # 9.0s = 216f -> snapped up to 226f (17*13+5)
    assert (packs[0].frames - 5) % 17 == 0
    assert packs[1].frames == 124  # 5.0s = 120f -> snapped up to 124f (17*7+5)


def test_strip_video_audio_invokes_ffmpeg_an_copy(tmp_path: Path) -> None:
    seen: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        seen.append(cmd)
        Path(cmd[-1]).write_bytes(b"proxy")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    src = tmp_path / "shot_01.mp4"
    src.write_bytes(b"raw")
    out = strip_video_audio(src, tmp_path / "proxies", runner=fake_run)
    assert out.name == "shot_01_noaudio.mp4"
    assert out.is_file()
    assert seen == [["ffmpeg", "-y", "-i", str(src), "-an", "-c:v", "copy", str(out)]]


def test_parse_refmods_slots_and_limits() -> None:
    refs = parse_refmods(["S1=alice_v1.safetensors", "S2=bob_v2.safetensors"])
    assert [(r.slot, r.subject, r.picture_index, r.file) for r in refs] == [
        ("mod_1", "S1", 1, "alice_v1.safetensors"),
        ("mod_2", "S2", 2, "bob_v2.safetensors"),
    ]
    with pytest.raises(ValueError, match="at most 8"):
        parse_refmods([f"S{i}=m{i}.safetensors" for i in range(1, 10)])


def test_export_breakdown_strips_banned_headers_and_refmod_picture(tmp_path: Path) -> None:
    breakdown_path = tmp_path / "breakdown.json"
    (tmp_path / "shot1.mp4").write_bytes(b"mp4")
    breakdown_path.write_text(
        json.dumps(
            {
                "shots": [
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "video": "shot1.mp4",
                        "keyframe": "kf1.png",
                        "description": "Two adults talk beside a rain-streaked cafe window.",
                        "bpm": 92,
                        "speech": {"lines": [{"speaker": "S1", "text": "You brought the wrong folder."}]},
                        "audio_stems": ["stems/voice_S1.wav"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    llm_calls: list[dict[str, Any]] = []

    def fake_post(
        url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float
    ) -> dict[str, Any]:
        llm_calls.append({"url": url, "payload": payload})
        # Return an official 3-section H3 prompt with banned headers and <Picture 1> to verify conversion
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "integrated_multimodal_description:\n"
                            "[Shot 1] Static medium two-shot inside a warm cafe. "
                            "At first, (S1) (<Picture 1>) rests her hands around a mug "
                            "and says in a steady voice, "
                            "<d>[English] You brought the wrong folder.</d> "
                            "(S2) (<Picture 2>) taps the envelope on the wooden table.\n\n"
                            "overall_soundscape:\n"
                            "Rain patters softly on the glass window.\n\n"
                            "non_diegetic_music:\n"
                            "Acoustic guitar score."
                        )
                    }
                }
            ]
        }

    def fake_ffmpeg(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        Path(cmd[-1]).write_bytes(b"noaudio")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    out_dir = tmp_path / "out"
    manifest = export_breakdown(
        breakdown_path,
        out_dir,
        refmod_specs=["S1=alice_v1.safetensors"],
        ffmpeg_runner=fake_ffmpeg,
        http_post=fake_post,
    )

    assert len(llm_calls) == 1
    assert llm_calls[0]["url"] == "http://127.0.0.1:8080/v1/chat/completions"
    assert manifest["model_id"] == "minimax-h3-10eros-beta7"
    assert manifest["refmods"][0]["slot"] == "mod_1"
    clip = manifest["clips"][0]
    assert clip["frames"] == 124
    assert clip["validation"]["status"] == "READY"
    assert clip["validation"]["header_violations"] == []
    prompt = clip["prompt"]
    assert "integrated_multimodal_description:" not in prompt.lower()
    assert "overall_soundscape:" not in prompt.lower()
    assert "non_diegetic_music:" not in prompt.lower()
    assert "acoustic guitar" not in prompt.lower()
    assert "Rain patters softly on the glass window." in prompt
    assert "<Picture 1>" not in prompt
    assert "<Picture 2>" in prompt
    assert (out_dir / "h3max_manifest.json").is_file()


def test_compile_prompt_rejects_bad_timestamps_and_policy_leak() -> None:
    packs = pack_shots({"shots": [{"start": 0.0, "end": 5.0, "description": "Walk on pier."}]})

    def bad_ts_post(
        url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float
    ) -> dict[str, Any]:
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "[Shot 1] At 00:00.000 Medium shot. "
                            "[Shot 2] At 00:09.000 She turns around."
                        )
                    }
                }
            ]
        }

    with pytest.raises(BridgeValidationError) as exc_info:
        compile_prompt_via_llm(packs[0], http_post=bad_ts_post)
    codes = {v["code"] for v in exc_info.value.validation["violations"]}
    assert "shot1_timestamp" in codes
    assert "shot_timestamp" in codes
