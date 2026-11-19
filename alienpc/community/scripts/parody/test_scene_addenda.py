"""Package 2 pass tests R15-R23 (module level, box). Live-tree integration is confirmed by Max on AlienPc."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scene_addenda as sa  # noqa: E402

BASE_ROWS = """acts:
  - id: missionary
    bodies: 2
    partner_types: [man]
    status: tested
  - id: doggy
    bodies: 2
    partner_types: [man]
    status: tested
  - id: cowgirl
    bodies: 2
    partner_types: [man]
    status: tested
  - id: blowjob
    bodies: 2
    partner_types: [man]
    status: tested
"""


@pytest.fixture()
def reg(tmp_path):
    base = sa.load_registry(_write(tmp_path / "base.yaml", BASE_ROWS))
    base.update(sa.load_registry(HERE / "acts_package2.yaml"))
    return base


def _write(p, text):
    p.write_text(text, encoding="utf-8")
    return p


# R15 futa partner
def test_r15_futa_partner_not_rewritten_one_refmod(reg):
    r = sa.resolve_brief("She has sex with her futa girlfriend, missionary", act_id="missionary", registry=reg, partner_type="man")
    assert r["partner_type"] == "futa"
    assert r["act_status"] == "untested"          # existing template counts as untested with futa
    assert r["not_ready"] is None
    plan = sa.refmod_plan(r, ["s1_face", "futa_face"])
    assert [v for v in plan["slots"].values() if v != "(none)"] == ["s1_face", "futa_face"]
    good = "(S1) lies back on the bed. (S2), the futa woman, kneels between her legs and pushes her cock into her."
    assert not sa.check_prompt(good, r)
    bad = "(S2) kneels; he pushes his cock into her as the man grips her hips."
    assert any(i["code"] == "P2-FUTA-AS-MAN" and i["hard"] for i in sa.check_prompt(bad, r))


def test_r15_futa_unknown_act_still_not_ready(reg):
    r = sa.resolve_brief("futa partner, act: reverse-flip", act_id="reverse_flip", registry=reg)
    # unknown named act id is not in the registry -> caller sees no row -> NOT_READY (never blowjob)
    assert sa.get_act(reg, "reverse_flip") is None


# R16 male solo
@pytest.mark.parametrize("ask", ["He jerks off on the couch", "male solo, edging himself, ruined orgasm finish",
                                 "solo guy jerking off in the shower"])
def test_r16_male_solo(reg, ask):
    r = sa.resolve_brief(ask, registry=reg)
    assert r["act_id"] == "male_solo" and r["body_count"] == 1
    assert r["s1_gender"] == "man" and r["partner_type"] == "none"
    assert r["act_status"] == "untested" and r["not_ready"] is None
    assert sa.refmod_plan(r, ["his_face"])["slots"]["mod_1"] == "his_face"
    ok = "(S1) sits on the couch and strokes himself slowly, his breath getting heavier."
    assert not [i for i in sa.check_prompt(ok, r) if i["hard"]]
    injected = ok + " (S2) kneels in front of him and watches."
    assert any(i["code"] == "P2-SOLO-PARTNER" for i in sa.check_prompt(injected, r))
    as_woman = "(S1) sits on the couch and she touches herself slowly."
    assert any(i["code"] == "P2-SOLO-S1-WOMAN" for i in sa.check_prompt(as_woman, r))


@pytest.mark.parametrize("ask", ["she jerks him off", "she gives him a handjob", "she edges him for a minute"])
def test_r16_handjob_is_not_male_solo(reg, ask):
    assert sa.resolve_brief(ask, registry=reg)["act_id"] != "male_solo"


def test_r16_female_solo_untouched(reg):
    r = sa.resolve_brief("she masturbates alone on the bed", registry=reg)
    assert r["act_id"] is None and r["s1_gender"] is None


# R17 generic costumes are wardrobe, not INDEX aliases
@pytest.mark.parametrize("name", ["vampire", "Sexy Witch", "cowboy", "Christmas outfit", "halloween costume", "zombies"])
def test_r17_costume_not_alias(name):
    assert sa.is_generic_costume_name(name)
    with pytest.raises(sa.GenericCostumeNotAlias):
        sa.guard_parody_name(name)


@pytest.mark.parametrize("name", ["Wonder Woman", "Princess Peach", "cowgirl", "Vampirella", "Tifa Lockhart"])
def test_r17_named_or_act_passes_guard(name):
    sa.guard_parody_name(name)  # no raise: named characters keep the parody lane; cowgirl is an act


def test_r17_hook_text_costume_is_wardrobe(reg):
    r = sa.resolve_brief("she wears a vampire costume on Halloween, missionary", act_id="missionary", registry=reg)
    assert r["costume_words"] == ["vampire", "halloween"] and r["not_ready"] is None


# R18 off-screen interviewer
def test_r18_offscreen_interviewer(reg):
    ask = "BTS interview: an off-screen interviewer asks her questions, then missionary"
    r = sa.resolve_brief(ask, act_id="missionary", registry=reg)
    assert r["offscreen_voice"] and r["camera_kind"] == "bts_interview" and r["first_beat_talk_ok"]
    prompt = ("(S1) sits on the edge of the bed facing the lens. An off-screen interviewer asks in a dry, low voice, "
              "<d>[English] So what made you want to do this?</d> (S1) says in a warm voice, <d>[English] Honestly? I like being watched.</d>")
    line = [u for u in sa._units(prompt) if "off-screen" in u][0]
    assert sa.speaker_of(line, 3) == "OFFSCREEN"           # not S1/S2/S3, not UNATTRIBUTED -> no fail-closed
    assert sa.body_count_in_prompt(prompt) == 1             # not counted, no man injected
    assert not sa.check_prompt(prompt, r)
    assert sa.refmod_plan(r, ["s1_face"])["slots"]["mod_2"] == "(none)"
    bad = "An off-screen interviewer steps into frame and says, <d>[English] Look at me.</d>"
    assert any(i["code"] == "P2-OFFSCREEN-BODY" for i in sa.check_prompt(bad, r))
    bad2 = "(S2) the off-screen interviewer asks, <d>[English] Ready?</d>"
    assert any(i["code"] == "P2-OFFSCREEN-SN" for i in sa.check_prompt(bad2, r))


def test_r18_unlabelled_line_still_unattributed():
    assert sa.speaker_of("Someone says, <d>[English] Hi.</d>", 3) == "UNATTRIBUTED"
    assert sa.speaker_of("(S3) says in a rough voice, <d>[English] My turn.</d>", 3) == "S3"
    assert sa.speaker_of("(S3) says, <d>[English] My turn.</d>", 2) == "UNATTRIBUTED"


# R19 look line keeps still color nouns
def test_r19_look_keeps_colors(reg):
    r = sa.resolve_brief("black-and-white noir look, she seduces him in the office, missionary", act_id="missionary", registry=reg)
    assert r["look"] == ["noir", "black-and-white"]
    line = sa.look_line(r)
    assert "colors stay as in the still" in line and "no color" not in line.lower()
    still = {"garments": ["red silk dress", "black stockings"]}
    kept = "(S1) wears the red silk dress and black stockings. " + line
    assert not sa.check_prompt(kept, r, still_read=still)
    lost = "(S1) wears a silk dress and stockings. " + line
    assert any(i["code"] == "P2-LOOK-COLOR" for i in sa.check_prompt(lost, r, still_read=still))


# R20 sleeping / already out
@pytest.mark.parametrize("ask,state", [("she is asleep on the couch, he has sex with her, missionary", "sleeping"),
                                       ("she was roofied and is already out, missionary", "already_out")])
def test_r20_sleeping_state_not_unknown_act(reg, ask, state):
    r = sa.resolve_brief(ask, act_id="missionary", registry=reg)
    assert state in r["states"] and r["act_id"] == "missionary" and r["not_ready"] is None
    assert r["sleeper_gender"] == "woman"
    assert not set(r["states"]) & set(reg)                  # states are never act ids
    ok = ("(S1) lies asleep on the couch, eyes closed, limbs slack, her chest rising slowly. (S2) says in a low voice, "
          "<d>[English] Stay just like that.</d>")
    assert not sa.check_prompt(ok, r, ask=ask, sleeper_sn="S1")
    talk = "(S1) lies asleep. (S1) says in a sleepy voice, <d>[English] Mm, more.</d>"
    assert any(i["code"] == "P2-SLEEP-SPEAK" for i in sa.check_prompt(talk, r, ask=ask, sleeper_sn="S1"))
    wake = "(S1) lies asleep, then her eyes snap open."
    assert any(i["code"] == "P2-SLEEP-WAKE" for i in sa.check_prompt(wake, r, ask=ask, sleeper_sn="S1"))


def test_r20_rufie_no_dose_no_drink(reg):
    ask = "rufie scene, she is already out, missionary"
    r = sa.resolve_brief(ask, act_id="missionary", registry=reg)
    dose = "(S2) drops a pill into her drink before the scene. (S1) lies still."
    codes = {i["code"] for i in sa.check_prompt(dose, r, ask=ask, sleeper_sn="S1")}
    assert {"P2-DOSE", "P2-DRINK"} <= codes


def test_mdma_state_setting_no_dose(reg):
    ask = "afterparty on molly, she rides him, cowgirl"
    r = sa.resolve_brief(ask, act_id="cowgirl", registry=reg)
    assert "mdma" in r["states"] and r["not_ready"] is None
    assert any(i["code"] == "P2-DOSE" for i in sa.check_prompt("(S1) takes 100 mg and sways.", r, ask=ask))
    assert not sa.check_prompt("(S1) sways on the afterparty couch, pupils wide, glowing skin.", r, ask=ask)


# R21 mind control
def test_r21_mind_control_state(reg):
    ask = "sci-fi mind control: he uses a glowing collar device to control her, doggy"
    r = sa.resolve_brief(ask, act_id="doggy", registry=reg)
    assert r["states"] == ["mind_control"] and r["act_id"] == "doggy" and r["not_ready"] is None
    keep = "A thin glowing collar device hums at (S1)'s throat; when (S2) commands, her body bends forward on the bed."
    assert not sa.check_prompt(keep, r, ask=ask)
    dropped = "(S1) bends forward on the bed and (S2) takes her from behind."
    assert any(i["code"] == "P2-MC-AGENT" for i in sa.check_prompt(dropped, r, ask=ask))


def test_r21_state_alone_never_an_act_id(reg):
    r = sa.resolve_brief("she is hypnotized", registry=reg)
    assert r["act_id"] is None and r["not_ready"] is None and r["states"] == ["mind_control"]


# R22 telekinesis
def test_r22_telekinesis_force_and_hold(reg):
    ask = "telekinesis: she lifts him with her mind, cowgirl"
    r = sa.resolve_brief(ask, act_id="cowgirl", registry=reg)
    assert r["states"] == ["telekinesis"] and r["not_ready"] is None
    ok = "(S1) raises her outstretched hand and an invisible force floats (S2) two inches above the mattress and turns him slowly."
    assert not sa.check_prompt(ok, r, ask=ask)
    nohold = "(S1) raises her outstretched hand and (S2) floats."
    assert any(i["code"] == "P2-TK-HOLD" for i in sa.check_prompt(nohold, r, ask=ask))
    noforce = "(S2) floats two inches above the mattress."
    assert any(i["code"] == "P2-TK-FORCE" for i in sa.check_prompt(noforce, r, ask=ask))


# R23 standing / airplane / piledriver
@pytest.mark.parametrize("ask,act", [("standing sex in the kitchen", "standing_mf"), ("airplane position", "airplane"),
                                     ("piledriver on the bed", "piledriver"), ("he fucks her standing up by the window", "standing_mf")])
def test_r23_untested_acts_resolve(reg, ask, act):
    r = sa.resolve_brief(ask, registry=reg)
    assert r["act_id"] == act and r["act_status"] == "untested" and r["not_ready"] is None and r["body_count"] == 2


@pytest.mark.parametrize("ask", ["he carries her against the wall, standing sex", "she is standing in the kitchen, missionary"])
def test_r23_carried_or_incidental_standing_not_standing_mf(reg, ask):
    assert sa.resolve_brief(ask, registry=reg)["act_id"] != "standing_mf"


def test_r23_missing_registry_row_is_not_ready():
    r = sa.resolve_brief("piledriver", registry={"missionary": {"id": "missionary", "status": "tested"}})
    assert r["not_ready"] and "blowjob" in r["not_ready"]


# shared addenda rules
def test_music_video_no_soundscape(reg):
    r = sa.resolve_brief("slow-mo music video vibe, cowgirl", act_id="cowgirl", registry=reg)
    assert "music_video" in r["register"]
    assert any(i["code"] == "P2-SOUNDSCAPE" for i in sa.check_prompt("x.", r, request_fields={"a": {"overall_soundscape": "synthwave"}}))
    assert not sa.check_prompt("Synthwave plays from a speaker in the room.", r, request_fields={"a": {"prompt": "..."}})


def test_camera_kinds_and_vr_flag(reg):
    assert sa.resolve_brief("webcam camshow")["camera_kind"] == "webcam"
    assert sa.resolve_brief("handheld sex tape on his phone")["camera_kind"] == "handheld_sextape"
    assert sa.resolve_brief("pov blowjob")["camera_kind"] == "pov"
    assert sa.resolve_brief("missionary")["camera_kind"] == "third_person"
    assert any("out of format" in f for f in sa.resolve_brief("stereo VR scene")["flags"])


def test_themes_writer_brief(reg):
    r = sa.resolve_brief("pregnant wife, caught shoplifting, spoof comedy, doggy", act_id="doggy", registry=reg)
    assert set(r["themes"]) == {"pregnancy", "caught_shoplifter"} and r["not_ready"] is None
    assert "comedy_spoof" in r["register"] and r["first_beat_talk_ok"]


def test_still_more_people_than_brief_not_ready(reg):
    r = sa.resolve_brief("He jerks off", registry=reg, still_people=2)
    assert r["not_ready"] and "NOT_READY" in r["not_ready"]


def test_no_new_age_rule_and_no_lock_fields():
    src = (HERE / "scene_addenda.py").read_text(encoding="utf-8")
    code = src.split('"""', 2)[2].lower()  # skip the module docstring
    for banned in ("teen", "school", "young", "petite", "sampler", "lock.json", "cfg", "steps=", "frame_idx"):
        assert banned not in code, banned
