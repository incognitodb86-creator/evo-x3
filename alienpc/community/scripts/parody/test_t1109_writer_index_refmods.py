"""Max Architect 3, Derrick t1107u/t1109u: off-still partner clothes and INDEX/OC RefMod attach."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_request as br
import submit_parody_run as s

STAGE_HDR = (
    "subject_definitions:\n(S1) test.\nsummary:\n[keyframe completion] test.\n"
    "retention_analysis:\nThe prompt maintains strict adherence to the brief.\n"
    "detailed_description:\n"
)

HER_ONLY = {
    "room": "a diner booth",
    "place": "diner",
    "bed": False,
    "sheets": "",
    "surface": "the booth seat",
    "floor": "tiled floor",
    "light": "warm diner light",
    "framing": "full-body, eye-level, front",
    "pose": "sits in the booth",
    "facing_camera": True,
    "garments": [
        {"type": "bikini top", "name": "a sports bra"},
        {"type": "bikini bottoms", "name": "orange bikini bottoms"},
    ],
    "people": 1,
}


def _raw(extra: str) -> str:
    return (
        STAGE_HDR
        + "At first she sits in the booth exactly as <Picture 1> shows. "
        + extra
        + " She lowers onto her back on the booth seat. He enters her and thrusts deep. Her moans rise."
    )


def test_t1109_make_cast_does_not_invent_shirt_and_trousers_on_clothed_her_only_still():
    c = br.make_cast(HER_ONLY, "missionary", "she has sex with him, position: missionary")
    assert c["his_clothes"] == ""
    assert c["still_people"] == 1
    assert c["off_still_s2"] is True
    assert "once he enters" in c["camera_tail"]
    assert "shirt and trousers" not in (c["his_clothes"] or "")


def test_t1109_writer_named_partner_clothes_become_canonical_line():
    c = br.make_cast(HER_ONLY, "missionary", "she has sex with him, position: missionary")
    raw = _raw(
        "A tall adult man of solid build walks in from the aisle, wearing a navy shirt and dark trousers. "
        "He pulls his shirt off over his head, his trousers; they drop to the tiled floor. "
    )
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert "pulls off his shirt and trousers" in p
    assert p.count("pulls off his shirt and trousers") == 1
    assert "He is not in <Picture 1>" in p
    assert "fully_preserved - his face, build and skin stay the same man throughout" not in p
    assert "enters during the clip" in p
    assert not any("the start still does not show the partner" in i for i in rep.get("issues", []))


def test_t1109_unnamed_partner_clothes_are_not_invented_and_undefined_partner_is_not_ready():
    c = br.make_cast(HER_ONLY, "missionary", "she has sex with him, position: missionary")
    raw = _raw("")  # act only; no look, clothes, or entrance
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert "shirt and trousers" not in p
    assert "pulls off his shirt" not in p
    assert any("the start still does not show the partner" in i for i in rep.get("issues", []))
    assert rep.get("off_still_undefined") is True
    assert br.packed_split_is_safe(rep) is False
    with pytest.raises(br.WriterPromptError, match="does not show the partner"):
        br.finalize_writer_prompt(raw, c, strict=True)


def test_t1109_third_person_off_still_must_be_defined():
    ask = "she has a threesome with two adult men, position: threesome"
    try:
        c = br.make_cast(HER_ONLY, "threesome", ask)
    except br.WriterNotReady as e:
        pytest.skip("threesome make_cast not available: " + str(e))
    if not c.get("off_still_s3") and int(c.get("bodies") or 0) < 3:
        pytest.skip("cast is not three-person")
    raw = _raw("A tall adult man of solid build walks in from the aisle, wearing a navy shirt.")
    _p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    if c.get("off_still_s3"):
        assert any("third person" in i for i in rep.get("issues", []))


def test_t1109_prepare_graph_does_not_keep_previous_run_refmods():
    tpl = json.loads(Path(s.DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
    s._set_refmod_slots(tpl, [
        "minimaxh3_oc_poolclub_v1_refmod_visual",
        "minimaxh3_oc_poolclub_v1_refmod_audio",
    ])
    tpl["img_1"] = {"inputs": {"image": r"C:\AI\render\run\old\poolclub_start.png"}}
    _g, rep = s.prepare_writer_base_graph(tpl, still_image=r"C:\AI\render\_inputs\hoot_start.jpg")
    assert rep.get("reason")
    assert "will not reuse the previous run" in rep["reason"]


def test_t1109_prepare_graph_attaches_oc_refmod_from_still_path():
    keys = s.installed_oc_refmod_keys()
    assert "poolclub" in keys, "poolclub OC RefMods must be installed for this test"
    tpl = json.loads(Path(s.DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
    s._set_refmod_slots(tpl, [
        "minimaxh3_oc_poolblonde_v2_refmod_visual",
        "minimaxh3_oc_poolblonde_v2_refmod_audio",
    ])
    tpl["img_1"] = {"inputs": {"image": r"C:\AI\render\run\old\blonde_start.png"}}
    g, rep = s.prepare_writer_base_graph(
        tpl, still_image=r"C:\AI\render\_inputs\oc_poolclub_diner.jpg",
    )
    assert not rep.get("reason"), rep
    assert rep.get("template") is True
    stems = " ".join(rep.get("stems") or [])
    assert "poolclub" in stems
    assert "poolblonde" not in stems
    assert s._graph_img1(g).endswith("oc_poolclub_diner.jpg")


def test_t1109_prepare_graph_character_name_attaches_oc_and_index_celebrity_refmods():
    keys = s.installed_oc_refmod_keys()
    assert "poolblonde" in keys
    tpl = json.loads(Path(s.DEFAULT_REFMOD_TEMPLATE).read_text(encoding="utf-8"))
    _g, rep = s.prepare_writer_base_graph(
        tpl,
        still_image=r"C:\AI\render\_inputs\generic_start.jpg",
        character="poolblonde",
    )
    assert not rep.get("reason"), rep
    assert any("poolblonde" in x for x in (rep.get("stems") or []))

    _g2, rep2 = s.prepare_writer_base_graph(
        tpl,
        still_image=r"C:\AI\render\_inputs\generic_start.jpg",
        character="daenerys",
    )
    assert not rep2.get("reason"), rep2
    assert any("emiliaclarke" in x for x in (rep2.get("stems") or []))

    _g3, rep3 = s.prepare_writer_base_graph(
        tpl,
        still_image=r"C:\AI\render\_inputs\generic_start.jpg",
        character="nonexistent_character_xyz",
    )
    assert rep3.get("reason")
    assert "no local RefMod installed" in rep3["reason"]
    assert "will not attach a real-person RefMod" not in rep3["reason"]


def test_t1125_trained_subject_fcsydny_maps_to_poolclub():
    m = s.trained_oc_subject_keys()
    assert m.get("fcsydny") == "poolclub"


def test_t1125_pool_folder_still_attaches_fcsydny_poolclub_refmod():
    keys = s.installed_oc_refmod_keys()
    assert "poolclub" in keys, "poolclub OC RefMods must be installed for this test"
    still = r"C:\Users\derek\5slock\approved_characters\POOL\flow_more_2026-10-19\POOL_F009.jpg"
    out = s.resolve_writer_refmods(still_image=still)
    assert not out.get("reason"), out
    stems = " ".join(out.get("stems") or [])
    assert "poolclub" in stems
    assert "poolblonde" not in stems
    junction = r"C:\AI\render\stills\approved_characters\POOL\flow_more_2026-10-19\POOL_F009.jpg"
    out2 = s.resolve_writer_refmods(still_image=junction)
    assert not out2.get("reason"), out2
    assert any("poolclub" in x for x in (out2.get("stems") or []))


def test_t1125_orc_pool_edge_and_hoot_are_not_folder_aliases():
    out = s.resolve_writer_refmods(
        still_image=r"C:\Users\derek\5slock\approved_characters\ORC_POOL_EDGE\not_a_real_still.jpg",
    )
    stems = " ".join(out.get("stems") or [])
    assert "poolclub" not in stems
    assert out.get("reason")
    out2 = s.resolve_writer_refmods(still_image=r"C:\AI\render\_inputs\hoot_start.jpg")
    assert out2.get("reason")
    assert "poolclub" not in " ".join(out2.get("stems") or [])


def test_t1125_character_fcsydny_and_deadpool_attach_refmods():
    out = s.resolve_writer_refmods(
        still_image=r"C:\AI\render\_inputs\generic_start.jpg",
        character="FCSydny",
    )
    assert not out.get("reason"), out
    assert any("poolclub" in x for x in (out.get("stems") or []))
    out2 = s.resolve_writer_refmods(
        still_image=r"C:\AI\render\_inputs\generic_start.jpg",
        character="Deadpool",
    )
    assert not out2.get("reason"), out2
    assert any("ryanreynolds" in x for x in (out2.get("stems") or []))


def test_t1125_pixlstash_tag_attaches_poolclub(monkeypatch):
    monkeypatch.setattr(s, "pixlstash_character_names_for_still", lambda still: ["FCSydny"])
    still = r"C:\Users\derek\5slock\approved_characters\FLOW_BLONDE_DARK_PAIRS_2026-10-19\fake.jpg"
    out = s.resolve_writer_refmods(still_image=still)
    assert not out.get("reason"), out
    assert any("poolclub" in x for x in (out.get("stems") or []))
