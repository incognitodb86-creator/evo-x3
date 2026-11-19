"""Talk-only act (Derrick t204u): --position talk, no injected contact/PRIMARY MOTION; doggy unchanged."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_request as br  # noqa: E402


def _still(people=1):
    return {
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
        "people": people,
        "garments": [
            {"type": "bra", "name": "sheer nude bra"},
            {"type": "panties", "name": "sheer panties"},
        ],
        "build": "slender adult build",
        "skin": "matte skin",
        "hair": "long blonde hair",
    }


TALK1 = """subject_definitions:
<Picture 1> is the reference image defining the exact appearance, face and hairstyle of <Subject 1>, and the bedroom, its soft window light and the opening framing.
<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, twenty-four years of age, long blonde hair; she is (S1), and <Audio 1> defines her voice timbre.
summary:
<Subject 1> stays standing in the bedroom as in <Picture 1> and delivers a short spoof line.
retention_analysis:
<Subject 1>: fully_preserved - face, hair and body from <Picture 1>. <Picture 1>: fully_preserved - the bedroom, the light and the opening framing.
detailed_description:
[Shot 1] The camera holds a static medium shot at eye level. At first, <Subject 1> stands barefoot on the wood floor exactly as in <Picture 1>, her weight on both planted feet. She tips her chin toward the lens. (S1) says in a dry, amused voice, <d>[English] You're late, detective.</d> Soft room tone, a floorboard creak under her heel.
"""

TALK2 = """subject_definitions:
<Picture 1> is the reference image defining the exact appearance, face and hairstyle of <Subject 1>, and the bedroom, its soft window light and the opening framing.
<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, twenty-four years of age, long blonde hair; she is (S1), and <Audio 1> defines her voice timbre.
<Subject 2> is an adult man, twenty-eight years of age, of solid build, in a dark shirt and trousers, who enters from the left; he is (S2).
summary:
<Subject 1> stays standing as in <Picture 1> and trades spoof banter with <Subject 2>.
retention_analysis:
<Subject 1>: fully_preserved - face, hair and body from <Picture 1>. <Picture 1>: fully_preserved - the bedroom, the light and the opening framing.
detailed_description:
[Shot 1] The camera holds a static medium two-shot at eye level. At first, <Subject 1> stands barefoot on the wood floor exactly as in <Picture 1>, her weight on both planted feet. <Subject 2> walks in from the left and stops a step away, hands at his sides. (S2) says in a low, even voice, <d>[English] You coming in, or what.</d> (S1) says in a dry, amused voice, <d>[English] Give me a minute, pal.</d> A floorboard creak, soft room tone.
"""

DOGGY_NO_CONTACT = """subject_definitions:
<Picture 1> is the reference image defining the exact appearance, face and hairstyle of <Subject 1>, and the bedroom, its soft window light and the opening framing.
<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, twenty-four years of age, long blonde hair; she is (S1), and <Audio 1> defines her voice timbre.
<Subject 2> is an adult man, twenty-eight years of age, of solid build, in a dark shirt and trousers, who enters from the left; he is (S2).
summary:
<Subject 1> braces on the bed and takes <Subject 2> from behind.
retention_analysis:
<Subject 1>: fully_preserved - face, hair and body from <Picture 1>. <Picture 1>: fully_preserved - the bedroom, the light and the opening framing.
detailed_description:
[Shot 1] The camera holds a static medium two-shot at hip height. At first, <Subject 1> stands barefoot on the wood floor exactly as in <Picture 1>. She turns, plants both palms on the bed and bends forward, her weight on her arms and planted feet, and pulls the sheer panties aside at the back, between the cheeks, where they stay. <Subject 2> walks in from the left, steps in close so his hips meet hers at the mattress height, and grips her hips. PRIMARY MOTION - continuous deep doggy thrust, about one full cycle every half second, full-depth travel; her breasts sway with each stroke. (S2) says in a low, hoarse voice, <d>[English] Hold still.</d> (S1) says in a tight voice, <d>[English] Don't ease up.</d> The mattress creaks, her ragged breath.
"""


def test_talk_one_body_ready_no_injected_contact_or_pm():
    c = br.make_cast(_still(1), "talk", "spoof banter, talk only, no sex")
    assert c["act_id"] == "talk"
    assert c["beat_kind"] == "talk"
    assert c["bodies"] == 1
    assert c["partner_type"] == "none"
    assert c.get("primary_motion") == ""
    assert c.get("contact") == ""
    final, rep = br.finalize_writer_prompt(TALK1, c, strict=False)
    assert not rep.get("not_ready")
    issues = [i for i in (rep.get("issues") or []) if str(i).startswith("NOT_READY")]
    assert issues == [], issues
    added = " ".join(rep.get("added") or [])
    assert "contact geometry" not in added.lower()
    assert "PRIMARY MOTION" not in added
    assert "PRIMARY MOTION" not in final
    assert "fully inside" not in final.lower()
    assert "fully sheathed" not in final.lower()


def test_talk_two_bodies_s2_dialogue_ready():
    c = br.make_cast(_still(1), "talk", "spoof banter with <Subject 2>, talk only, no sex")
    assert c["act_id"] == "talk"
    assert c["beat_kind"] == "talk"
    assert c["bodies"] == 2
    assert c["partner_type"] != "none"
    final, rep = br.finalize_writer_prompt(TALK2, c, strict=False)
    assert not rep.get("not_ready")
    issues = [i for i in (rep.get("issues") or []) if str(i).startswith("NOT_READY")]
    assert issues == [], issues
    added = " ".join(rep.get("added") or [])
    assert "contact geometry" not in added.lower()
    assert "PRIMARY MOTION" not in added
    assert "PRIMARY MOTION" not in final
    assert "(S2)" in final and "<d>" in final
    assert "fully inside" not in final.lower()


def test_doggy_still_injects_contact_when_writer_omits_it():
    c = br.make_cast(_still(1), "doggy", "doggy from behind")
    assert c["act_id"] == "doggy"
    assert c["beat_kind"] == "act"
    assert c.get("contact")
    final, rep = br.finalize_writer_prompt(DOGGY_NO_CONTACT, c, strict=False)
    added = " ".join(rep.get("added") or [])
    assert "contact geometry line (R19)" in added
    assert "fully inside" in final.lower() or "fully sheathed" in final.lower() or "his penis" in final.lower()
