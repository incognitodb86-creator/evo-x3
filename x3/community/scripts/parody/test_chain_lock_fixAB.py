"""Max Architect, Derrick t271s933 (2026-11-15): chained-clip Fix A (wardrobe from the tracked scene state, never the
last-frame read; W5 overrides need frame evidence) and Fix B (subject and set words fixed from the clip-1 read)."""
import build_request as br

ASK = "[reference generation] He rolls her onto her back, climbs onto the bed between her thighs and enters her."

# clip_22 of overnight_5min_rough_20261114: the last-frame read that brought the panties back and rewrote her bio
LAST = {"read": {"room": "an indoor setting with dim lighting", "place": "indoor", "bed": False, "sheets": "",
                 "surface": "the floor", "floor": "unknown", "light": "dim and warm", "framing": "close-up",
                 "pose": "kneels on the floor while being touched by another person", "facing_camera": False,
                 "garments": [{"type": "panties", "name": "panties", "look": "dark brown"}],
                 "hair": "not visible", "skin": "glowing, oily skin", "build": "athletic and muscular builds", "people": 2},
        "how": "chain last-frame vision_read"}
FIRST = {"read": {"room": "a dim bedroom", "place": "beside a tall bed", "bed": True, "sheets": "grey sheets",
                  "surface": "the bed", "floor": "wooden floor", "light": "window light from the left and a lamp",
                  "pose": "stands beside the bed", "people": 2,
                  "garments": [{"type": "camisole", "name": "camisole", "look": "black"},
                               {"type": "panties", "name": "panties", "look": "black"}],
                  "hair": "long wavy dark brown hair", "skin": "fair skin", "build": "a slim build with natural curves"}}


def test_fix_a_removed_garment_never_returns_from_last_frame():
    cast = br.make_cast(LAST, "missionary", ASK, continued=True, inherited_garments={"panties": "off", "top": "off"})
    assert [g["key"] for g in cast["inventory"]] == []
    assert "panties" not in cast["still_garments"] and "panties" not in cast["still_wardrobe"]
    _, state, _ = br.track_state(["<Subject 2> thrusts into her, his hips flush."], cast)
    assert all(v == "off" for v in state["garments"].values())
    assert br._w5_covered_garments(cast, state) == []


def test_fix_a_end_state_carries_off_garments_to_next_clip():
    # the previous clip's final state must still say 'off' even when this clip's read no longer shows the garment
    cast = br.make_cast(dict(LAST, read=dict(LAST["read"], garments=[])), "missionary", ASK, continued=True,
                        inherited_garments={"panties": "off"})
    _, state, _ = br.track_state(["<Subject 2> thrusts into her, his hips flush."], cast)
    assert state["garments"].get("panties") == "off"


def test_fix_a_tracked_on_garment_kept_with_scene_name():
    cast = br.make_cast(LAST, "missionary", ASK, continued=True, scene_read=FIRST,
                        inherited_garments={"camisole": "on", "panties": "off"})
    assert [g["key"] for g in cast["inventory"]] == ["top"]  # camisole tracks under the top key
    assert "black camisole" in cast["still_garments"]


def test_fix_a_w5_override_needs_frame_evidence(tmp_path):
    corr = {"removed": [{"type": "panties", "name": "panties", "look": "dark brown"}], "why": "false positive"}
    doc = {"read": dict(LAST["read"], garments=[]), "stale_garment_correction": corr}
    assert [g["name"] for g in br._unwrap_still_read(doc)["garments"]] == ["panties"]
    crop = tmp_path / "w5_crop.jpg"
    crop.write_bytes(b"jpg")
    doc_ok = dict(doc, stale_garment_correction=dict(corr, evidence=str(crop)))
    assert br._unwrap_still_read(doc_ok)["garments"] == []


def test_fix_b_subject_and_set_locked_from_clip1():
    cast = br.make_cast(LAST, "missionary", ASK, continued=True, scene_read=FIRST, inherited_garments={"panties": "off"})
    for bad in ("not visible", "muscular", "oily"):
        assert bad not in cast["woman"], cast["woman"]
    assert "long wavy dark brown hair" in cast["woman"] and "fair skin" in cast["woman"]
    assert cast["still_bed"] is True
    assert "unknown" not in cast["garments_floor"] and "unknown" not in cast["still"]
    text, rep = br.apply_still_facts("She slides up the bed until her head rests on the pillows, and the mattress rebounds.",
                                     cast["still_read"])
    assert "floor" not in text and "unknown" not in text, text


def test_fix_b_unchained_clip_still_reads_its_own_still():
    cast = br.make_cast(LAST, "missionary", ASK)
    assert "panties" in cast["still_garments"]