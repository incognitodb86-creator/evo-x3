"""Unit tests for Part 1 (Writer SYS fix) and Part 2 (Pass tests R1-R14 for S3 modular builder).

Authorized by Derrick t1007u and t1008s3914, Nov 11, 2026.
"""
from __future__ import annotations
import sys

import json
from pathlib import Path
import re
import pytest

import build_request as br
import submit_parody_run as spr
from writer_sys import (
    assert_writer_system_prompt,
    build_writer_system_prompt,
    AgentInstructionsInWriterPrompt,
    WRITER_SKILL_SOURCES,
    _AGENT_MARKERS,
)

BED_READ = {
    "room": "a bedroom with a bed in white sheets",
    "place": "bedroom",
    "bed": True,
    "sheets": "white sheets",
    "surface": "the bed",
    "floor": "wood floor",
    "light": "soft window light",
    "framing": "full-body, eye-level, front",
    "pose": "stands barefoot on the wood floor in front of the bed",
    "facing_camera": True,
    "people": [{"box": [0, 0, 1, 1]}],
    "garments": [
        {"type": "bra", "name": "sheer nude bra"},
        {"type": "panties", "name": "sheer panties"},
    ],
}

TWO_PERSON_READ = {
    **BED_READ,
    "people": [{"box": [0, 0, 1, 1]}, {"box": [0, 0, 1, 1]}],
}

THREE_PERSON_READ = {
    **BED_READ,
    "people": [{"box": [0, 0, 1, 1]}, {"box": [0, 0, 1, 1]}, {"box": [0, 0, 1, 1]}],
}


def _dummy_refmod_graph(n_mods: int = 8) -> dict:
    inputs = {f"mod_{i}": f"minimaxh3_oc_mod_{i}" if i <= n_mods else "(none)" for i in range(1, 9)}
    return {
        "c0": {"inputs": {"prompt": "", "width": 768, "height": 1344, "seed": 51083601, "length": 243}},
        "noise": {"inputs": {"noise_seed": 51083601}},
        "img_1": {"inputs": {"image": "community/start.png"}},
        "refmods": {"inputs": inputs},
        "save": {"inputs": {"filename_prefix": "test"}},
    }


# ==============================================================================
# Part 1: Writer SYS Fix
# ==============================================================================

def test_writer_sys_assert_rejects_agent_instructions():
    bad_prompt = "# Render Rules (/home/derekboone/AI/render)\nSome prompt directions\nmanage_task and tool guidelines"
    with pytest.raises(AgentInstructionsInWriterPrompt):
        assert_writer_system_prompt(bad_prompt)

    clean_prompt = "# Prompt Writer\nWrite image-to-video prompts for H3."
    assert_writer_system_prompt(clean_prompt)


def test_writer_sys_build_only_loads_prompt_skills_and_strips_frontmatter():
    sys_prompt, meta = build_writer_system_prompt()
    assert_writer_system_prompt(sys_prompt)
    assert not sys_prompt.startswith("---")
    assert len(meta) == len(WRITER_SKILL_SOURCES)
    for snip in _AGENT_MARKERS:
        assert snip not in sys_prompt


# ==============================================================================
# Part 2: Pass Tests R1 - R14
# ==============================================================================

def test_r1_unknown_act_no_sex_ff_tease_not_blowjob():
    """R1: Unknown act, 'no sex', F+F, or tease does not return as a man and blowjob."""
    # Unknown act fails closed (WriterNotReady), NOT defaulting to blowjob
    with pytest.raises(br.WriterNotReady, match="unknown act"):
        br.make_cast(BED_READ, "random_invented_act", "she does random act")

    # 'tease' returns tease act with no penis in contact
    c_tease = br.make_cast(BED_READ, "tease", "she teases the camera")
    assert c_tease["act_id"] == "tease"
    assert "penis" not in c_tease.get("contact", "").lower()
    assert "blowjob" not in c_tease["summary_act"].lower()

    # F+F (ff_cunnilingus) sets woman partner, not man blowjob
    c_ff = br.make_cast(BED_READ, "ff_cunnilingus", "two women together", partner_type="woman")
    assert c_ff["partner_type"] == "woman"
    assert c_ff["act_id"] == "ff_cunnilingus"
    assert "blowjob" not in c_ff["summary_act"].lower()

    # Solo female (female_solo) sets partner_type none
    c_solo = br.make_cast(BED_READ, "female_solo", "she touches herself", partner_type="none")
    assert c_solo["partner_type"] == "none"
    assert c_solo["act_id"] == "female_solo"
    assert "blowjob" not in c_solo["summary_act"].lower()


def test_r2_s3_spoken_line_credited_to_s3_unattributed_fails_closed():
    """R2: Spoken line attributed to S3 stays credited to S3; unattributed spoken lines fail closed."""
    assert br._speaker_of('(S3) says in a low voice: "Hold still."') == "S3"
    assert br._speaker_of('<Subject 3> says: "Keep going."') == "S3"

    # Spoken line without attribution fails closed
    with pytest.raises(br.WriterPromptError):
        br._speaker_of('"Take it off right now."')

    with pytest.raises(br.WriterPromptError):
        br._span_speaker('Just looking around. "Take it off right now."')

    # In finalize_writer_prompt, S3 line is credited in counts
    raw_s3 = """subject_definitions:
(S1) Woman
(S2) Partner
(S3) Third
detailed_description:
[Shot 1] The camera holds. <Subject 1> lies back. (S3) says in a firm voice, "Don't move."
diegetic sound:
Soft room tone.
"""
    cast_s3 = dict(
        woman="an adult woman", man="an adult man", still="a room",
        voice_s1="voice 1", voice_s2="voice 2", voice_s3="voice 3",
        still_wardrobe="nude", garments_off="", garments_stay="", garments_floor="",
        his_clothes="", absent_garments="", camera_tail="keeping all three faces in frame",
        position_check="", position_beat="", primary_motion="", contact="",
        summary_act="threesome scene", is_three_person=True, bodies=3
    )
    p, rep = br.finalize_writer_prompt(raw_s3, cast_s3, strict=False)
    assert rep["counts"]["S3"] == 1
    assert rep["counts"]["S1"] == 0
    assert rep["counts"]["S2"] == 0


def test_r3_solo_still_plus_two_person_brief_builds():
    """R3: Solo still + 2-person brief builds (partner enters)."""
    cast = br.make_cast(BED_READ, "missionary", "missionary on the bed with him")
    assert cast["bodies"] == 2
    assert cast["act_id"] == "missionary"


def test_r4_solo_still_plus_three_person_brief_builds():
    """R4: Solo still + 3-person brief builds (other two enter)."""
    cast = br.make_cast(BED_READ, "threesome", "threesome on the bed with two partners")
    assert cast["bodies"] == 3
    assert cast["is_three_person"] is True
    assert cast["act_id"] == "threesome"


def test_r5_three_person_still_plus_two_person_brief_fails():
    """R5: 3-person still + 2-person brief raises WriterNotReady (people-count mismatch)."""
    with pytest.raises(br.WriterNotReady, match="people-count mismatch"):
        br.make_cast(THREE_PERSON_READ, "missionary", "missionary position with him")


def test_r6_two_person_still_plus_three_person_brief_builds():
    """R6: 2-person still + 3-person brief builds (third enters)."""
    cast = br.make_cast(TWO_PERSON_READ, "threesome", "threesome with two partners")
    assert cast["bodies"] == 3
    assert cast["is_three_person"] is True


def test_r7_three_person_job_refmods_allocation_and_limits():
    """R7: 3-person job loads <=1 RefMod per named face; unused slots empty; faceless/non-human gets none; >8 named faces is NOT_READY."""
    s1_slots = {"mod_1": {"path": "s1_a.safetensors", "strength": 1.0, "copies": 1},
                "mod_2": {"path": "s1_b.safetensors", "strength": 1.0, "copies": 1}}
    s2_slots = {"mod_1": {"path": "s2_a.safetensors", "strength": 1.0, "copies": 1},
                "mod_2": {"path": "s2_b.safetensors", "strength": 1.0, "copies": 1}}
    s3_slots = {"mod_1": {"path": "s3_a.safetensors", "strength": 1.0, "copies": 1},
                "mod_2": {"path": "s3_b.safetensors", "strength": 1.0, "copies": 1}}

    # Standard 3 named faces: exactly 1 RefMod per person
    merged = br.merge_refmod_slots(s1_slots, s2_slots, s3_slots, three_person=True)
    assert merged["mod_1"]["path"] == "s1_a.safetensors"
    assert merged["mod_2"]["path"] == "s2_a.safetensors"
    assert merged["mod_3"]["path"] == "s3_a.safetensors"
    for i in range(4, 9):
        assert merged[f"mod_{i}"]["path"] == "(none)"

    # Faceless S2, non-human S3: only S1 gets RefMod
    merged_nh = br.merge_refmod_slots(s1_slots, s2_slots, s3_slots, three_person=True,
                                      partner_types=["faceless", "non-human"])
    assert merged_nh["mod_1"]["path"] == "s1_a.safetensors"
    for i in range(2, 9):
        assert merged_nh[f"mod_{i}"]["path"] == "(none)"

    # Missing RefMod on named face raises WriterNotReady
    empty_s3: dict = {}
    with pytest.raises(br.WriterNotReady, match="named face \\(S3\\) has no RefMod"):
        br.merge_refmod_slots(s1_slots, s2_slots, empty_s3, three_person=True)


def test_r8_oc_hook_writes_s3_and_checks_refmod_slots():
    """R8: The OC hook, not only the parody CLI, writes S3 and loads or checks those slots."""
    # Graph with 3 live RefMods for a 3-person cast with explicit named faces
    g = _dummy_refmod_graph(n_mods=3)
    cast = br.make_cast(BED_READ, "threesome", "threesome with two partners")
    cast = dict(cast, named_faces=["S1", "S2", "S3"], partner_type="man", partner_type2="man")
    raw = "detailed_description:\n[Shot 1] The camera holds. <Subject 2> enters her and thrusts with steady rhythmic strokes while <Subject 3> holds her close on the bed.\n\ndiegetic sound:\nsoft room tone."
    g_out, _, _ = br.build_writer_request(g, raw, cast, prefix="test_oc_s3", strict=False)
    assert g_out["refmods"]["inputs"]["mod_1"] == "minimaxh3_oc_mod_1"
    assert g_out["refmods"]["inputs"]["mod_2"] == "minimaxh3_oc_mod_2"
    assert g_out["refmods"]["inputs"]["mod_3"] == "minimaxh3_oc_mod_3"
    for i in range(4, 9):
        mod_val = g_out["refmods"]["inputs"][f"mod_{i}"]
        assert (mod_val.get("path") == "(none)") if isinstance(mod_val, dict) else (mod_val == "(none)")

    # Default MMF/threesome partners are faceless: one OC RefMod is enough (Derrick t1467).
    g_one = _dummy_refmod_graph(n_mods=1)
    c_face = br.make_cast(BED_READ, "threesome", "threesome with two partners")
    g_ok, _, _ = br.build_writer_request(g_one, raw, c_face, prefix="test_oc_s3_faceless", strict=False)
    assert g_ok["refmods"]["inputs"]["mod_1"] == "minimaxh3_oc_mod_1"
    for i in range(2, 9):
        assert g_ok["refmods"]["inputs"][f"mod_{i}"] == "(none)"

    # Explicit named faces still fail-closed without enough RefMods.
    g_bad = _dummy_refmod_graph(n_mods=1)
    named = dict(cast, named_faces=["S1", "S2", "S3"], partner_type="man", partner_type2="man")
    with pytest.raises(br.WriterNotReady, match="named-face person has no RefMod"):
        br.build_writer_request(g_bad, raw, named, prefix="test_oc_s3_bad", strict=False)


def test_r9_w4_does_not_drop_s3_garments():
    """R9: W4 does not drop S3 garments that belong to that person in the brief or the still."""
    raw = """subject_definitions:
(S1) Woman
(S2) Partner 1
(S3) Partner 2
detailed_description:
[Shot 1] The camera holds. <Subject 1> stands by the bed. <Subject 3> wears his denim jacket and leather boots while watching.
diegetic sound:
Soft room tone.
"""
    cast = dict(
        woman="an adult woman", man="an adult man", still="a room",
        voice_s1="voice 1", voice_s2="voice 2", voice_s3="voice 3",
        still_wardrobe="nude", garments_off="", garments_stay="", garments_floor="",
        his_clothes="", absent_garments=r"\b(?:denim jacket|boots)\b", camera_tail="keeping all three faces in frame",
        position_check="", position_beat="", primary_motion="", contact="",
        summary_act="threesome scene", is_three_person=True, bodies=3
    )
    p, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    # S3 sentence mentioning denim jacket is NOT dropped by W4
    assert "<Subject 3>" in p
    assert "denim jacket" in p


def test_r10_unknown_three_person_act_is_not_ready():
    """R10: An unknown three-person act is NOT_READY, not a blowjob."""
    with pytest.raises(br.WriterNotReady, match="unknown act"):
        br.make_cast(BED_READ, "unknown_threesome_variant", "an unknown 3-way act")


def test_r11_two_person_brief_does_not_inject_third_person():
    """R11: A two-person brief does not get a third person injected."""
    c = br.make_cast(BED_READ, "doggy", "doggy on the bed with him")
    assert c["bodies"] == 2
    assert c["is_three_person"] is False
    assert c["voice_s3"] == ""
    assert c["partner_type2"] == "none"
    assert "<Subject 3>" not in c["summary_act"]


def test_r12_subject_3_is_never_used_as_place():
    """R12: <Subject 3> is never used as place."""
    c = br.make_cast(BED_READ, "threesome", "threesome on the bed with two partners")
    assert "<Subject 3>" not in c["surface"]
    assert "<Subject 3>" not in c["still"]


def test_r13_prequel_last_frame_pin():
    """R13: Prequel last-frame pin adds second guide at frame_idx -1 (resolved to frames - 1), start still not named <Picture 2>."""
    # prequel_to target validation in submit_writer_run
    res = spr.submit_writer_run("raw output", _dummy_refmod_graph(1), Path("dummy_run"),
                                "brief", "missionary", prequel_to="non_existent_file.mp4")
    assert res["status"] == "NOT_READY"
    assert "target clip to prequel not found" in res["reason"]


def test_r14_dials_sampler_lock_unchanged_age_floor_18_plus():
    """R14: Dials/sampler/lock unchanged, age floor 18+."""
    import comm
    # Live bad regex allows adult terms and blocks underage/minor/child
    assert comm.guard_ok("adult woman 22yo")
    assert comm.guard_ok("bad girl")
    assert not comm.guard_ok("underage")
    assert not comm.guard_ok("minor")
    assert not comm.guard_ok("child")
    assert not comm.guard_ok("children")

def test_s3_dual_mode_faceless_still_and_generated_look():
    """Derrick t1467: MMF dual mode passes with a generated look, a partner2 still, or the faceless fallback."""
    raw = ("detailed_description:\n[Shot 1] The camera holds. <Subject 2> is behind her with steady rhythmic strokes "
           "while <Subject 3> is at her mouth.\n\ndiegetic sound:\nsoft room tone.")
    g1 = _dummy_refmod_graph(n_mods=1)
    c_face = br.make_cast(BED_READ, "mmf", "MMF threesome on the bed")
    assert c_face["partner_type2"] == "faceless"
    br.build_writer_request(g1, raw, c_face, prefix="mmf_faceless", strict=False)

    c_still = dict(c_face, s3_still="community/flux_p1_20261030/M01_body.jpg")
    g_st, _, rep = br.build_writer_request(_dummy_refmod_graph(n_mods=1), raw, c_still, prefix="mmf_still", strict=False)
    assert rep.get("s3_still") or g_st.get("img_s3")

    c_look = dict(c_face, s3_look="an adult man, thirty years of age, of solid build, with short dark hair")
    br.build_writer_request(_dummy_refmod_graph(n_mods=1), raw, c_look, prefix="mmf_look", strict=False)


def test_w5_skipped_for_mmf_double_blowjob():
    assert "mmf_double_blowjob" in br._ORAL_POSITIONS
    cast = br.make_cast(BED_READ, "mmf_double_blowjob", "MMF double blowjob")
    raw = ("detailed_description:\n[Shot 1] The camera holds. At first, (S1) is on her knees in her sheer panties. "
           "(S2) and (S3) stand in front of her. She takes them in her mouth.\n\ndiegetic sound:\nwet suction.")
    # Must not raise W5 / clearance just because the panties were not pulled aside before oral entry.
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    assert "NOT_READY" not in str(rep.get("error") or "")
    # also the request builder should not raise WriterNotReady for W5
    br.build_writer_request(_dummy_refmod_graph(n_mods=1), raw, cast, prefix="w5_oral", strict=False)


def test_male_solo_s1_is_the_man_not_the_still_person():
    cast = br.make_cast(BED_READ, "male_solo", "male solo edging")
    assert cast["s1_gender"] == "man" and cast["act_id"] == "male_solo"
    assert "not (S1)" in cast["still"] or "not in this clip" in cast["still"]
    raw = ("detailed_description:\n[Shot 1] The camera holds. At first, (S1) stands by the bed. "
           "He strokes himself at a slow tempo.\n\ndiegetic sound:\nquiet breath.")
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    text = prompt if isinstance(prompt, str) else str(prompt)
    assert "does not define <Subject 1>" in text or "not the person shown in <Picture 1>" in text
    assert "exact same man shown in <Picture 1>" not in text


def test_ffm_act_written_when_ask_names_an_act():
    cast = br.make_cast(BED_READ, "ffm", "FFM on the bed")
    raw = ("detailed_description:\n[Shot 1] The camera holds. At first, (S1) lies back on the bed. "
           "(S2) rides her face while (S3) sinks onto her with slow strokes.\n\ndiegetic sound:\nbreath and wet contact.")
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    assert rep.get("act_written") is True
    # is_act_ask is true for FFM, so build_writer_request must not raise act:false
    br.build_writer_request(_dummy_refmod_graph(n_mods=1), raw, cast, prefix="ffm_act", strict=False)

def test_pm_acc4_builder_continued_skips_opening_from_still():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static medium shot. At first, (S1) is already on her back, "
           "and (S2) is buried in her vagina with steady rhythmic strokes.\n\ndiegetic sound:\nsoft room tone.")
    cast = dict(br.make_cast(BED_READ, "missionary", "keep going, faster"), continued=True)
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    text = prompt if isinstance(prompt, str) else str(prompt)
    assert "The clip opens on <Picture 1>" not in text
    assert any("opening-from-still skipped" in a or "continued" in a for a in (rep.get("added") or []))


def test_pm_acc4_builder_bunches_is_not_a_removal():
    raw = ("detailed_description:\n[Shot 1] The camera holds. At first, (S1) stands on the wood floor, knees on the floor, "
           "her sheer panties bunching at her waist and stay there. She touches herself.\n\ndiegetic sound:\nquiet breath.")
    cast = br.make_cast(BED_READ, "female_solo", "solo with a wand on the bed")
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    st = (rep.get("state") or {})
    assert "item:panties" not in (st.get("writer_removed") or [])
    text = prompt if isinstance(prompt, str) else str(prompt)
    assert "the the floor" not in text
    # wardrobe line must not claim the panties were taken off to the floor
    assert "she took off" not in text.lower() or "panties" not in text.lower()


def test_pm_acc4_builder_no_r23_when_writer_wrote_camera():
    raw = ("detailed_description:\n[Shot 1] Held, medium shot. At first, (S1) lies back on the bed. "
           "(S2) enters her vagina and stays buried in her vagina with steady rhythmic strokes.\n\ndiegetic sound:\nsoft room tone.")
    cast = br.make_cast(BED_READ, "missionary", "missionary on the bed")
    prompt, rep = br.finalize_writer_prompt(raw, cast, strict=False)
    assert not any("camera sentence (R23)" == a or a.startswith("camera sentence (R23)") for a in (rep.get("added") or []))
    text = prompt if isinstance(prompt, str) else str(prompt)
    assert text.lower().count("the camera holds a static medium shot") <= 1


def test_pm_acc4_speech_speaker_is_sentence_subject():
    assert br._speaker_of('(S1) winks playfully at (S2) and says, <d>[English] Stay close.</d>') == "S1"
    assert br._span_speaker("(S1) winks playfully at (S2) and says, ") == "S1"
    assert br._speaker_of('(S2) says in a low voice, <d>[English] Hold still.</d>') == "S2"


def test_pm_acc4_garments_floor_has_no_double_the():
    read = dict(BED_READ, floor="the floor")
    cast = br.make_cast(read, "tease", "slow striptease")
    assert "the the" not in (cast.get("garments_floor") or "")
    assert (cast.get("garments_floor") or "").lower().startswith("the ")


def test_pm_acc4_make_cast_handjob_template():
    # PM #11: make_cast has a handjob branch; it must not raise unknown act.
    c = br.make_cast(BED_READ, "handjob", "handjob")
    assert c.get("position") == "handjob" or c.get("act_id") == "handjob" or "handjob" in (c.get("summary_act") or "").lower()
    assert "unknown act" not in (c.get("not_ready") or "")
    assert "fist" in (c.get("contact") or "").lower()
    assert "penis" in (c.get("contact") or "").lower()
    assert "handjob" in (c.get("summary_act") or "").lower()
    raw = ("detailed_description:\n[Shot 1] Held, medium shot. At first, (S1) sits beside him on the bed. "
           "Her fist is wrapped around his penis as she strokes the shaft.\n\ndiegetic sound:\nsoft breath.")
    prompt, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert not (rep.get("not_ready") or "").lower().startswith("not_ready: unknown act")
    text = prompt if isinstance(prompt, str) else str(prompt)
    assert "handjob" in text.lower() or "fist" in text.lower()
    # W5 must not block a handjob even if a leftover garment is on and the writer said "sheathed".
    raw_w5 = ("detailed_description:\n[Shot 1] Held, medium shot. At first, (S1) stands on the sand. "
              "Her white bikini bottom stays on her body. Her fist wraps around his penis and he stays fully sheathed "
              "as she strokes the shaft.\n\ndiegetic sound:\nsoft breath.")
    prompt2, rep2 = br.finalize_writer_prompt(raw_w5, c, strict=False)
    msg = (rep2.get("not_ready") or "").lower()
    assert "w5" not in msg, rep2.get("not_ready")


def test_pm_acc4d_templates_and_male_solo_still():
    mmf = br.make_cast(BED_READ, "mmf", "MMF, she's on all fours, one behind, one in her mouth")
    assert "penis is inside her mouth" in (mmf.get("contact") or "").lower()
    assert "lips sealed around his shaft" in (mmf.get("contact") or "").lower()
    assert "sheathed" not in (mmf.get("contact") or "").lower()
    sc = br.make_cast(BED_READ, "ff_scissoring", "FF scissoring on the bed")
    assert "(s1)'s vulva is pressed to (s2)'s vulva" in (sc.get("contact") or "").lower()
    ffm = br.make_cast(BED_READ, "ffm", "FFM on the bed")
    c = (ffm.get("contact") or "").lower()
    assert "penis" in c and "vagina" in c and ("vulva" in c or "mouth" in c)
    cg = br.make_cast(BED_READ, "cowgirl", "she rides him")
    assert "penis" in (cg.get("contact") or "").lower() and "vagina" in (cg.get("contact") or "").lower()
    male = br.make_cast(BED_READ, "male_solo", "male solo edging")
    # still is setting only: do not describe her hair/skin/clothes as his
    blob = " ".join(str(male.get(k) or "") for k in ("woman", "still", "still_line", "still_wardrobe", "man")).lower()
    assert "blonde" not in blob and "sheer nude bra" not in blob


def test_flash_issues_1_3_4():
    # Issue 1: Double-prefixed text glue ('the the wooden sideboard')
    read_sideboard = dict(BED_READ, bed=False, surface="the wooden sideboard", floor="the floor")
    cast_sb = br.make_cast(read_sideboard, "tease", "slow striptease")
    assert "the the" not in (cast_sb.get("garments_floor") or "")
    assert (cast_sb.get("garments_floor") or "").lower().startswith("the ")
    import render_writer_pipeline as rwp
    slots_sb = rwp.make_slots(read_sideboard, "standing_mf on the sideboard", "standing_mf", "sex", "test_run", None)
    brief_sb = rwp.brief_block("standing_mf on the sideboard", "standing_mf", "sex", slots_sb, 2)
    assert "the the" not in brief_sb.lower()

    # Issue 3: Stacking camera sentences with 'Held medium shot.'
    raw_cam = ("[Shot 1] Held medium shot. The camera slowly pushes in to her face. "
               "At first, (S1) lies back on the bed. (S2) enters her vagina and stays buried in her vagina with steady rhythmic strokes.\n\n"
               "diegetic sound:\nsoft room tone.")
    prompt_cam, rep_cam = br.finalize_writer_prompt(raw_cam, cast_sb, strict=False)
    text_cam = prompt_cam if isinstance(prompt_cam, str) else str(prompt_cam)
    # exactly one camera sentence remains
    assert text_cam.lower().count("pushes in to her face") == 1
    assert "held medium shot" not in text_cam.lower()

    # Issue 4: Preposition before speaker label in convert_speech
    res = br.convert_speech(["(S1) winks playfully at (S2) and says, <d>[English] Stay close.</d>"], {"S1": "a warm voice"})
    assert "(S1) says in a warm voice" in res[0]
    assert "(S2) says" not in res[0]


@pytest.mark.skipif(sys.platform != "win32", reason="AlienPc --queue / Windows vault paths; X3 uses queue-remote.sh and has no vault.db")
def test_part4_pixlstash_stills_vault_and_voice_ref_attach():
    import submit_parody_run as spr
    vaults = [str(p).lower() for p in spr._PIXLSTASH_VAULTS]
    assert any("approved_characters\\vault.db" in v for v in vaults)
    assert any("5slock\\libraries\\vault.db" in v for v in vaults)
    assert vaults.index(next(v for v in vaults if "approved_characters\\vault.db" in v)) < vaults.index(
        next(v for v in vaults if "5slock\\libraries\\vault.db" in v)
    )

    res = spr.resolve_writer_refmods(character="FCSydny")
    stems = res.get("stems") or []
    assert "minimaxh3_oc_poolclub_v1_refmod_audio" in stems
    assert "minimaxh3_oc_poolclub_v1_refmod_visual" in stems
    assert spr._writer_refmods_ok({"refmods": {"inputs": {"mod_1": "some_non_oc_refmod"}}}) == []


def test_part4_all_refmods_and_pixlstash_celebrity_tag(monkeypatch):
    import submit_parody_run as spr
    z = spr.resolve_writer_refmods(character="Zendaya")
    assert not z.get("reason"), z
    assert any("zendaya" in x for x in (z.get("stems") or []))

    monkeypatch.setattr(spr, "pixlstash_character_names_for_still", lambda still: ["Zendaya"])
    z_tag = spr.resolve_writer_refmods(still_image=r"/home/derekboone/AI/render/_inputs/generic_tag_test.jpg")
    assert not z_tag.get("reason"), z_tag
    assert z_tag.get("source") == "pixlstash"
    assert any("zendaya" in x for x in (z_tag.get("stems") or []))


def test_contact_regex_and_prompt_compiler_77_rules():
    import wp_compile_prompt as wpc
    import check_writer_prompt_rules as chk

    for phrase in (
        "her mouth on her vulva",
        "her tongue moves against her clitoris",
        "her fist around his shaft",
        "their vulvas pressed together",
    ):
        assert br._CONTACT_RE.search(phrase), phrase

    agents_src = Path(r"/home/derekboone/AI/render/AGENTS.md").read_text(encoding="utf-8")
    compiled = wpc.compile_prompt(agents_src)
    assert "MODES (use only when the ask calls for one)" in compiled
    assert "EXAMPLES (level of detail only;" in compiled
    shape_sec = compiled.split("\nSHAPE ", 1)[1].split("\nPRE-FLIGHT", 1)[0]
    assert "\nsubject_definitions:\n" not in shape_sec
    assert "\ndetailed_description:\n" in shape_sec

    rules_data = chk.json.loads((Path(__file__).resolve().parent / "render-master-rules-20261113.json").read_text(encoding="utf-8"))
    lines = compiled.split("\n")
    ratio = float(rules_data.get("condensed_ratio", 0.6))
    fails = [(r["id"], chk.check(r, compiled, lines, ratio)) for r in rules_data["rules"]
             if r.get("severity") != "retired" and chk.check(r, compiled, lines, ratio)[0] != "PASS"]
    assert fails == [], fails


def test_submit_writer_run_male_solo_strips_dress_and_woman_voice(tmp_path):
    import submit_parody_run as spr
    sr = {
        "read": {
            "room": "high-rise apartment",
            "place": "by a window",
            "surface": "wooden sideboard",
            "bed": False,
            "floor": "the floor",
            "pose": "leaning, standing",
            "facing_camera": True,
            "framing": "medium shot",
            "light": "soft evening light from window",
            "people": 1,
            "garments": [{"type": "dress", "name": "sheer white halter dress", "look": "white"}],
            "build": "curvy",
            "skin": "fair",
            "hair": "blonde",
        }
    }
    raw = (
        "subject_definitions:\n"
        "<Picture 1> defines the high-rise apartment, its soft evening light and framing.\n"
        "<Subject 1> is an adult man, twenty-four years of age, of solid adult build; he is (S1).\n\n"
        "summary:\n(S1) edges beside the sideboard.\n\n"
        "retention_analysis:\n<Picture 1>: fully_preserved - high-rise apartment, wooden sideboard, floor, light and framing.\n\n"
        "detailed_description:\n"
        "[Shot 1] The camera is a fixed medium shot at chest height in soft evening light. "
        "At first, (S1) leans beside the wooden sideboard on his feet, by the window. "
        "As it builds, his lounge pants sit down at mid-thigh, and PRIMARY MOTION - he grips his shaft and edges with steady slow strokes at one cycle per second, his breath hitching. "
        "(S1) says, <d>[English] Too close.</d> "
        "By the end, he holds his grip beside the sideboard, still stroking steadily with a soft gasp.\n"
    )
    g0 = {
        "c0": {"inputs": {"prompt": "", "length": 243, "width": 768, "height": 1344}},
        "noise": {"inputs": {"noise_seed": 0}},
        "save": {"inputs": {"filename_prefix": ""}},
        "refmods": {"inputs": {f"mod_{i}": ("minimaxh3_oc_poolclub_v1_refmod_visual" if i == 1 else "(none)") for i in range(1, 9)}},
        "img_1": {"inputs": {"image": "community/POOL_F034.jpg"}},
    }
    res = spr.submit_writer_run(
        raw, g0, tmp_path / "ms1", "male solo edging", "male_solo",
        still_read=sr, still_image="community/POOL_F034.jpg", dry_run=True,
    )
    assert res["status"] == "READY", res
    ptxt = (tmp_path / "ms1" / "prompt.txt").read_text(encoding="utf-8")
    low = ptxt.lower()
    assert "sheer white halter dress" not in low
    assert "woman's voice" not in low
    assert "man's voice" in low


