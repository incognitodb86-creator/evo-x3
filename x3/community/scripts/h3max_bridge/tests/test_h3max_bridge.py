"""Offline unit tests for h3max_bridge (RV2, mocked llama-swap and ffmpeg)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from h3max_bridge import (
    BridgeValidationError,
    apply_bridge_gates,
    bind_refmods_for_shots,
    compile_prompt_via_llm,
    count_onscreen_people,
    export_breakdown,
    filter_shots,
    normalize_breakdown,
    pack_shots,
    parse_refmods,
    parse_shot_ids,
    compile_prompt_offline,
    redact_validation,
    slice_long_shots,
    snap_frames,
    strip_video_audio,
)
from h3max_bridge import h3max_bridge as hb


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


def test_parse_shot_ids_accepts_numbers_and_canonical_ids() -> None:
    assert parse_shot_ids("49, 29") == ["shot_049", "shot_029"]
    assert parse_shot_ids("shot_007,8") == ["shot_007", "shot_008"]


def test_filter_and_voice_slice_hotel_style_shots() -> None:
    breakdown = {
        "audio": {"voice": {"segments": [[10.0, 14.0], [21.0, 25.0]]}},
        "shots": [
            {"id": "shot_001", "index": 1, "start": 0.0, "end": 4.0, "duration": 4.0, "talk_share": 0.0},
            {
                "id": "shot_029",
                "index": 29,
                "start": 0.0,
                "end": 30.0,
                "duration": 30.0,
                "talk_share": 0.2,
                "vlm": {"description": "An adult man stands in a hotel corridor."},
                "assets": {"first_frame": "shots/shot_029_first.jpg"},
            },
        ],
    }
    filtered = filter_shots(breakdown, parse_shot_ids("29"))
    assert [s["id"] for s in filtered["shots"]] == ["shot_029"]
    sliced = slice_long_shots(filtered, max_frames=362, mode="voice")
    shot = sliced["shots"][0]
    assert shot["duration"] <= 362 / 24 + 1e-9
    # voice at 21-25 should beat the 10-14 window after start 0; window should cover 21-25
    assert shot["start"] <= 21.0
    assert shot["end"] >= 25.0
    norm = normalize_breakdown(sliced, audio_stem=Path("vocals.wav"))
    nshot = norm["shots"][0]
    assert "adult man" in nshot["description"]
    assert nshot["keyframe"].endswith("shot_029_first.jpg")
    assert nshot["audio_stems"] == ["vocals.wav"]
    assert nshot["audio_duration"] <= 15.0
    packs = pack_shots(norm, max_frames=362)
    assert len(packs) == 1
    assert packs[0].frames == 362


def test_pack_shots_caps_362f_audio_just_over_15s() -> None:
    breakdown = {
        "shots": [
            {
                "start": 0.0,
                "end": 15.083,
                "duration": 15.083,
                "audio_stems": ["vocals.wav"],
                "audio_duration": 15.083,
            }
        ]
    }
    packs = pack_shots(breakdown, max_frames=362)
    assert len(packs) == 1
    assert packs[0].frames == 362
    assert packs[0].audio_duration_s <= 15.0


def test_tile_long_shots_covers_full_duration() -> None:
    breakdown = {"shots": [{"id": "shot_010", "start": 0.0, "end": 40.0, "duration": 40.0}]}
    tiled = slice_long_shots(breakdown, max_frames=362, mode="tile")
    shots = tiled["shots"]
    assert len(shots) == 3
    assert abs(sum(s["duration"] for s in shots) - 40.0) < 1e-9
    assert shots[0]["start"] == 0.0
    assert shots[-1]["end"] == 40.0
    packs = pack_shots(normalize_breakdown(tiled), max_frames=362)
    assert len(packs) == 3


def test_compile_prompt_offline_is_ready() -> None:
    breakdown = {
        "shots": [
            {
                "id": "shot_001",
                "start": 0.0,
                "end": 8.0,
                "duration": 8.0,
                "talk_share": 0.4,
                "vlm": {"description": "An adult woman and an adult man talk beside a hotel window at night."},
            }
        ]
    }
    packs = pack_shots(normalize_breakdown(breakdown), max_frames=243)
    text, conv, val = compile_prompt_offline(packs[0], refmods=parse_refmods(["S1=a.safetensors", "S2=b.safetensors"]))
    assert val["status"] == "READY"
    assert "<d>" not in text  # no ASR lines: foley only, no canned dialogue
    assert "I'm right here" not in text
    assert "[Shot 1]" in text
    assert "<Picture 1>" not in text
    assert conv.get("lint_ctx_passed") is True


def _shot(description: str, **extra: Any) -> dict[str, Any]:
    row = {"id": "shot_001", "start": 0.0, "end": 8.0, "duration": 8.0, "vlm": {"description": description}}
    row.update(extra)
    return row


def test_two_person_and_single_man_refmod_binding() -> None:
    refs = parse_refmods(
        [
            "Alice=alice_v.safetensors",
            "Bob=bob_v.safetensors",
            "Alice=alice_voice_audio.safetensors",
        ]
    )
    assert refs[0].kind == "visual"
    assert refs[1].kind == "visual"
    assert refs[2].kind == "audio"
    assert refs[2].picture_index is None

    two = _shot("An adult woman and an adult man talk beside a hotel window at night.", layers_n=1, faces=0.5)
    people = count_onscreen_people(two)
    assert people["n"] == 2
    assert people["male_hits"] >= 1
    assert people["female_hits"] >= 1
    bound, report = bind_refmods_for_shots(refs, [two])
    assert report["people_n"] == 2
    assert report["visual_bound"] == 2
    assert report["audio_n"] == 1
    by_subj = {r.subject: r for r in bound if r.kind == "visual"}
    assert by_subj["Alice"].picture_index == 1
    assert by_subj["Bob"].picture_index == 2
    assert [r.picture_index for r in bound if r.kind == "audio"] == [None]

    one = _shot("An adult man stands alone in a hotel corridor.", layers_n=1, talk_share=0.2, speech={"lines": []})
    people = count_onscreen_people(one)
    assert people["n"] == 1
    assert people["male_hits"] >= 1
    assert people["female_hits"] == 0
    bound, report = bind_refmods_for_shots(refs, [one])
    assert report["people_n"] == 1
    assert report["visual_bound"] == 1
    visuals = [r for r in bound if r.kind == "visual" and r.picture_index is not None]
    assert len(visuals) == 1
    assert visuals[0].subject == "Bob"
    alice = next(r for r in bound if r.subject == "Alice" and r.kind == "visual")
    assert alice.picture_index is None

    packs = pack_shots(normalize_breakdown({"shots": [one]}), max_frames=243)
    text, conv, val = compile_prompt_offline(packs[0], refmods=refs)
    assert val["status"] == "READY"
    assert "(S2)" not in text
    assert "I'm right here" not in text
    assert "<d>" not in text
    assert "Bob" in text
    assert conv.get("lint_ctx_passed") is True
    assert conv.get("bind_report", {}).get("visual_bound") == 1


def test_no_canned_dialogue_when_speech_lines_empty() -> None:
    shot = _shot(
        "An adult woman and an adult man talk beside a hotel window at night.",
        talk_share=0.4,
        speech={"lines": []},
    )
    packs = pack_shots(normalize_breakdown({"shots": [shot]}), max_frames=243)
    text, conv, val = compile_prompt_offline(
        packs[0], refmods=parse_refmods(["Alice=a.safetensors", "Bob=b.safetensors"])
    )
    assert val["status"] == "READY"
    assert "<d>" not in text
    assert "I'm right here" not in text
    assert "Alice" in text and "Bob" in text
    assert "(S1)" in text and "(S2)" in text


def test_oral_noun_untagged_dialogue_is_muted() -> None:
    raw = (
        "[Shot 1] Locked close-up in a hotel interior. "
        "Her lips and tongue are on his shaft. "
        "<d>[English] Let me take care of you.</d> Soft room tone."
    )
    gates = apply_bridge_gates(raw)
    assert gates["oral_context"] is True
    assert gates["d_muted"] == 1
    assert gates["untagged_muted"] == 1
    assert gates["d_kept"] == 0
    assert "<d>" not in gates["text"]
    assert "Let me take care of you" not in gates["text"]


def test_policy_word_category_logged_on_writer_failure(tmp_path: Path) -> None:
    def bad_post(url: str, payload: dict[str, Any], headers: dict[str, str], timeout_s: float) -> dict[str, Any]:
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            "[Shot 1] Locked medium shot. Two adults sit quietly. "
                            "This uses a celebrity likeness. Soft room tone."
                        )
                    }
                }
            ]
        }

    packs = pack_shots({"shots": [{"start": 0.0, "end": 5.0, "description": "Walk on pier."}]})
    with pytest.raises(BridgeValidationError) as exc_info:
        compile_prompt_via_llm(packs[0], http_post=bad_post)
    redacted = getattr(exc_info.value, "redacted", None) or redact_validation(exc_info.value.validation)
    assert "policy_word" in redacted["codes"]
    assert "likeness_or_celebrity" in redacted["policy_word_categories"]
    # raw matched phrase must not be stored in the redacted record
    assert "note" not in json.dumps(redacted["violations"])

    breakdown_path = tmp_path / "breakdown.json"
    breakdown_path.write_text(
        json.dumps({"shots": [{"start": 0.0, "end": 5.0, "description": "Two adults sit in a cafe.", "speech": {"lines": []}}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"
    with pytest.raises(BridgeValidationError):
        export_breakdown(breakdown_path, out_dir, http_post=bad_post, skip_video_proxies=True)
    manifest = json.loads((out_dir / "h3max_manifest.json").read_text(encoding="utf-8"))
    pre = manifest["clips"][0]["writer_preflight"]
    assert "policy_word" in pre["codes"]
    assert "likeness_or_celebrity" in pre["policy_word_categories"]
    assert "note" not in json.dumps(pre.get("violations") or [])


def test_offline_fallback_always_passes_lint_ctx(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Any] = []
    mod = hb.load_beta7_convert()
    real = mod.convert_and_validate

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        seen.append(kwargs.get("lint_ctx"))
        return real(*args, **kwargs)

    monkeypatch.setattr(mod, "convert_and_validate", wrapped)
    packs = pack_shots(
        normalize_breakdown(
            {"shots": [_shot("An adult woman stands by a window.", talk_share=0.2, speech={"lines": []})]}
        ),
        max_frames=243,
    )
    text, conv, val = compile_prompt_offline(packs[0], refmods=parse_refmods(["Alice=a.safetensors"]))
    assert val["status"] == "READY"
    assert seen, "convert_and_validate was not called"
    assert all(ctx is not None for ctx in seen)
    assert all(isinstance(ctx, dict) and "cfg" in ctx for ctx in seen)
    assert conv.get("lint_ctx_passed") is True
    assert "<d>" not in text
