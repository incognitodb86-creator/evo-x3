"""Tests for rea_shot_plan (REA C2) -- offline, no audio or network fixtures."""

from __future__ import annotations

import pytest

import build_request as br
import flux_still as fs
import rea_shot_plan as rsp


# --- 1) plan_frames ---------------------------------------------------------

def test_plan_frames_short_shot_pads_to_the_floor():
    # 1.2 s = 29 frames, below the 56-frame floor: render the floor, trim to 29
    assert rsp.plan_frames(1.2) == [{"frames": 56, "trim_to_frames": 29}]


def test_plan_frames_single_aligned_clip():
    parts = rsp.plan_frames(6.583)
    assert len(parts) == 1
    assert parts[0]["frames"] == 158
    assert parts[0]["frames"] % 17 == 5
    # already on the grid, so nothing to trim
    assert "trim_to_frames" not in parts[0]


def test_plan_frames_single_clip_trims_when_aligned_is_larger():
    parts = rsp.plan_frames(6.0)  # 144 frames -> aligned 158
    assert parts == [{"frames": 158, "trim_to_frames": 144}]


def test_plan_frames_splits_long_shot_with_continuation():
    parts = rsp.plan_frames(14.0)
    assert len(parts) == 2
    for p in parts:
        assert 56 <= p["frames"] <= br.SINGLE_CLIP_MAX_FRAMES
        assert p["frames"] % 17 == 5
    assert parts[0]["suffix"] == "a"
    assert parts[0]["continue_from"] is None
    assert parts[1]["suffix"] == "b"
    assert parts[1]["continue_from"] == "a"
    assert sum(p["trim_to_frames"] for p in parts) == round(14.0 * br.H3_FPS)


def test_plan_frames_three_parts_chain_suffixes():
    parts = rsp.plan_frames(30.0)
    assert [p["suffix"] for p in parts] == ["a", "b", "c"]
    assert [p["continue_from"] for p in parts] == [None, "a", "b"]
    assert all(p["frames"] <= br.SINGLE_CLIP_MAX_FRAMES for p in parts)
    assert sum(p["trim_to_frames"] for p in parts) == round(30.0 * br.H3_FPS)


def test_plan_frames_beat_inside_window_moves_the_cut():
    plain = rsp.plan_frames(14.0)
    aligned = rsp.plan_frames(14.0, [9.9])  # 9.9 s -> frame 238, 5 frames from the 243 cut
    assert plain[0]["trim_to_frames"] == br.SINGLE_CLIP_MAX_FRAMES
    assert aligned[0]["trim_to_frames"] == int(round(9.9 * br.H3_FPS))
    assert aligned[0]["frames"] <= br.SINGLE_CLIP_MAX_FRAMES
    assert sum(p["trim_to_frames"] for p in aligned) == round(14.0 * br.H3_FPS)


def test_plan_frames_beat_outside_window_is_ignored():
    # 8.0 s -> frame 192 is 51 frames (2.1 s) from the cut, outside +-1.0 s
    parts = rsp.plan_frames(14.0, [8.0])
    assert parts[0]["trim_to_frames"] == br.SINGLE_CLIP_MAX_FRAMES


def test_plan_frames_beats_are_absolute_seconds_from_shot_start():
    parts = rsp.plan_frames(14.0, [30.0], shot_start=20.0)
    assert parts[0]["trim_to_frames"] == int(round((30.0 - 20.0) * br.H3_FPS))
    assert parts[1]["continue_from"] == "a"


def test_plan_frames_rejects_bad_seconds():
    for bad in (0.0, -1.0, None):
        with pytest.raises(ValueError):
            rsp.plan_frames(bad)


# --- 2) camera_vocab --------------------------------------------------------

@pytest.mark.parametrize("move,expected", [
    ("static", "held static"),
    ("locked-off tripod shot", "held static"),
    ("slow push in", "slow push-in with medium amplitude"),
    ("quick zoom-in on her face", "fast push-in with medium amplitude"),
    ("gentle dolly out", "slow pull-back with medium amplitude"),
    ("fast wide pan left", "fast pan-left with large amplitude"),
    ("subtle tilt up", "slow tilt-up with small amplitude"),
    ("sweeping orbit", "medium orbit with large amplitude"),
    ("handheld shaky", "medium handheld with medium amplitude"),
    ("whip pan right", "fast pan-right with medium amplitude"),
    ("slow slight pull back", "slow pull-back with small amplitude"),
    ("dolly out", "medium pull-back with medium amplitude"),
    ("a floating blob of nothing", "held static"),
    ("", "held static"),
])
def test_camera_vocab(move, expected):
    assert rsp.camera_vocab(move) == expected


def test_camera_vocab_only_uses_h3_words():
    speeds = {"slow", "medium", "fast"}
    amps = {"small", "medium", "large"}
    for move in ("slow big orbit", "rapid tilt down", "whip pan left", "static"):
        words = rsp.camera_vocab(move)
        if words == "held static":
            continue
        assert words.split()[0] in speeds
        assert words.split()[-2] in amps


# --- 3) build_cast_lock -----------------------------------------------------

def _shots():
    return [
        {"id": "s1", "seconds": 1.2, "camera": "slow push in"},
        {"id": "s2", "seconds": 14.0, "camera": "sweeping orbit", "beats": [9.9]},
    ]


def test_cast_lock_parody_lane_blocks_audio_ref():
    lock = rsp.build_cast_lock(["FC Sydny", "FC Megan"], None, "parody", "9:16", _shots())
    assert lock["lane"] == "parody"
    assert lock["h3_identity"]["allow_audio_ref"] is False
    assert lock["h3_identity"]["names"] == ["FC Sydny", "FC Megan"]
    assert lock["canvas"] == [768, 1344]
    assert lock["aspect"] == "9:16"


def test_cast_lock_oc_lane_for_fcsydny_allows_audio_ref():
    lock = rsp.build_cast_lock(None, "FCSydny", "parody", "16:9", [])
    assert lock["lane"] == "oc"
    assert lock["h3_identity"]["allow_audio_ref"] is True
    assert lock["canvas"] == [1344, 768]
    assert lock["flux_identity"]["refmod"] is None
    # case-insensitive
    assert rsp.build_cast_lock(None, "fcmegan", "", "9:16", [])["lane"] == "oc"


def test_cast_lock_flux_naming_matches_flux_still():
    lock = rsp.build_cast_lock(["FC Sydny"], None, "parody", "9:16", [])
    refmod, stack = fs._hybrid_stack_for_name("FC Sydny")
    assert lock["flux_identity"]["refmod"] == refmod == "fk9_fcsydny_v1_refmod"
    assert lock["flux_identity"]["lora"] == stack["name"] == "klein9/fk9_fcsydny_v1_prodigy.safetensors"


def test_cast_lock_shot_overrides_carry_parts_and_camera_words():
    lock = rsp.build_cast_lock(["FC Sydny"], None, "parody", "9:16", _shots())
    overrides = lock["shot_overrides"]
    assert [o["shot_id"] for o in overrides] == ["s1", "s2"]
    assert overrides[0]["parts"] == [{"frames": 56, "trim_to_frames": 29}]
    assert overrides[0]["camera_h3_vocab"] == "slow push-in with medium amplitude"
    assert len(overrides[1]["parts"]) == 2
    assert overrides[1]["parts"][0]["trim_to_frames"] == int(round(9.9 * br.H3_FPS))
    assert overrides[1]["camera_h3_vocab"] == "medium orbit with large amplitude"


def test_cast_lock_rejects_empty_cast_and_bad_aspect():
    with pytest.raises(ValueError):
        rsp.build_cast_lock([], "", "parody", "9:16", [])
    with pytest.raises(ValueError):
        rsp.build_cast_lock(None, None, "oc", "9:16", [])
    with pytest.raises(ValueError):
        rsp.build_cast_lock(["FC Sydny"], None, "parody", "4:5", [])
    with pytest.raises(ValueError):
        rsp.build_cast_lock(["FC Sydny"], None, "parody", "9x16", [])


# --- 4) write_batch_card ----------------------------------------------------

def test_batch_card_has_one_row_per_part(tmp_path):
    shots = [
        {"id": "s1", "seconds": 1.2, "camera": "static"},
        {"id": "s2", "seconds": 14.0, "camera": "slow push in"},
        {"id": "s3", "seconds": 6.583, "camera": "orbit"},
    ]
    lock = rsp.build_cast_lock(["FC Sydny"], None, "parody", "9:16", shots)
    expected_parts = sum(len(o["parts"]) for o in lock["shot_overrides"])
    path = rsp.write_batch_card(tmp_path / "batch", lock, shots)
    assert path.name == "batch_card.md"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    rows = [ln for ln in text.splitlines()
            if ln.startswith("| ") and "---" not in ln and not ln.startswith("| shot |")]
    assert len(rows) == expected_parts == 4
    assert "Reply GO to run this batch." in text
    assert "| s2a |" in text and "| s2b |" in text
    # no prompt prose in the card
    assert "prompt" not in text.lower()
