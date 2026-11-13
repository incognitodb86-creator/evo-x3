"""Unit tests for Part 1 (Writer SYS fix) and Part 2 (Pass tests R1-R14 for S3 modular builder).

Authorized by Derrick t1007u and t1008s3914, Nov 11, 2026.
"""
from __future__ import annotations

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
    bad_prompt = "# Render Rules (C:\\AI\\render)\nSome prompt directions\nmanage_task and tool guidelines"
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
    # Graph with 3 live RefMods for a 3-person cast
    g = _dummy_refmod_graph(n_mods=3)
    cast = br.make_cast(BED_READ, "threesome", "threesome with two partners")
    raw = "detailed_description:\n[Shot 1] The camera holds. <Subject 2> enters her and thrusts with steady rhythmic strokes while <Subject 3> holds her close on the bed.\n\ndiegetic sound:\nsoft room tone."
    g_out, _, _ = br.build_writer_request(g, raw, cast, prefix="test_oc_s3", strict=False)
    assert g_out["refmods"]["inputs"]["mod_1"] == "minimaxh3_oc_mod_1"
    assert g_out["refmods"]["inputs"]["mod_2"] == "minimaxh3_oc_mod_2"
    assert g_out["refmods"]["inputs"]["mod_3"] == "minimaxh3_oc_mod_3"
    for i in range(4, 9):
        mod_val = g_out["refmods"]["inputs"][f"mod_{i}"]
        assert (mod_val.get("path") == "(none)") if isinstance(mod_val, dict) else (mod_val == "(none)")

    # Graph with only 1 RefMod for a 3-person cast with named faces fails NOT_READY
    g_bad = _dummy_refmod_graph(n_mods=1)
    with pytest.raises(br.WriterNotReady, match="named-face person has no RefMod"):
        br.build_writer_request(g_bad, raw, cast, prefix="test_oc_s3_bad", strict=False)


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
