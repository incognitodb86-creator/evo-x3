"""Unit tests for the 2026-11-11 writer-output finalizer in build_request.py (Derrick t825u, writer-test FINAL)."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import build_request as br  # noqa: E402

CAST = dict(
    woman="an adult woman, twenty-two years of age, with long blonde hair",
    man="an adult man, twenty-six years of age, of solid adult build",
    voice_s1="a low, warm adult woman's voice",
    voice_s2="a contrasting deep, steady adult man's voice",
    still="a bedroom with a bed in white sheets and a wood floor",
    still_wardrobe="stands barefoot on the wood floor in front of the bed in a sheer nude bra, a garter belt, sheer panties and thigh-high stockings, facing the camera",
    garments_off="sheer nude bra and sheer panties",
    garments_off_check=[r"\bbra\b", r"\b(panties|thong)\b"],
    garments_floor="the wood floor beside the bed",
    garments_stay="garter belt and thigh-high stockings",
    his_clothes="<Subject 2> pulls off his shirt and trousers, and they drop to the floor beside the bed and stay there",
    absent_garments=r"\bchemise\b",
    camera_tail="keeping her face, his face and the join in frame",
    position_check=r"\bon her back\b",
    position_beat="She lowers onto her back on the white sheets, and <Subject 2> kneels between her thighs.",
    primary_motion="continuous deep frontal thrust, about one full cycle per second, full depth travel",
    contact="His penis is fully inside her vagina with their hips flush on every stroke.",
    summary_act="<Subject 1> lies back on the bed and takes <Subject 2> in the missionary position.",
)

# dynsafe: a bedroom still read for build_writer_request (production needs a still read; no bedroom fallback)
BED_READ = {"room": "a bedroom with a bed in white sheets", "place": "bedroom", "bed": True, "sheets": "white sheets",
            "surface": "the bed", "floor": "wood floor", "light": "soft window light", "framing": "full-body, eye-level, front",
            "pose": "stands barefoot on the wood floor in front of the bed", "facing_camera": True,
            "garments": [{"type": "bra", "name": "sheer nude bra"}, {"type": "garter belt", "name": "garter belt"},
                         {"type": "panties", "name": "sheer panties"}, {"type": "stockings", "name": "thigh-high stockings"}]}

RAW = """subject_definitions:
(S1) Pool Blonde (RefMod minimaxh3_oc_poolblonde_v2): Adult woman, 18+. Never age-play.
summary:
[keyframe completion] A 10-second clip, seed 51083601, 243 frames, 768x1344, locked 1-pass beta7_int8HQ. No minors, no real-person likeness.
retention_analysis:
The prompt maintains strict adherence to the brief. The "No timestamp" rule is respected.
detailed_description:
[Shot 1] The camera holds a locked medium shot. The camera slowly pushes in toward the bed. She stands by the bed and peels off the sheer chemise. She then lies on her back, and he kneels between her thighs. After that he thrusts hard. She says "Fuck... harder, daddy." He growls "Take it." She gasps "More." She moans "Yes." She begs "Again." No cuts, no freeze, no music. <Video 1> continues the motion.
diegetic sound:
The mattress creaks with each thrust. Skin slaps on skin.
non_diegetic_music:
A slow synth bed.
detailed_description:
[Shot 1] duplicate copy.
"""


def build(raw=RAW, **kw):
    return br.finalize_writer_prompt(raw, CAST, **kw)


def test_sections_and_tag():
    p, _ = build()
    heads = re.findall(r"^(subject_definitions|summary|retention_analysis|detailed_description):", p, re.M)
    assert heads == ["subject_definitions", "summary", "retention_analysis", "detailed_description"]
    assert re.search(r"^summary:\n\[reference generation\] ", p, re.M)
    assert "[keyframe completion]" not in p


def test_r11_clauses_and_hand_line_verbatim():
    p, _ = build()
    assert br.R11_PICTURE in p and br.R11_SUBJECT in p and br.R11_HAND in p
    assert "<Subject 1> (appears in [Shot 1]): fully_preserved" in p
    assert "<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved" in p


def test_strips_dials_policy_selfgrading_absent_refs_music():
    p, rep = build()
    low = p.lower()
    for bad in ("seed", "768x1344", "243 frames", "beta7", "age-play", "minors", "likeness", "adherence",
                "respected", "<video 1>", "diegetic sound:", "no cuts", "minimaxh3_"):
        assert bad not in low, bad
    assert "non_diegetic_music:" in low and any("non_diegetic_music" in w for w in rep["warnings"])
    assert any("duplicate detailed_description" in s for s in rep["stripped"])
    assert "duplicate copy" not in p


def test_sound_header_becomes_plain_end_sentences():
    p, rep = build()
    desc = p.split("detailed_description:\n", 1)[1]
    assert "Skin slaps on skin." in desc
    assert "The mattress creaks with each thrust." in desc
    assert "non_diegetic_music:" in desc and any("non_diegetic_music" in w for w in rep["warnings"])


def test_transition_words_removed():
    p, _ = build()
    plain = re.sub(r"<d>.*?</d>", "", p)
    for w in ("then", "after", "afterwards", "next"):
        assert not re.search(rf"\b{w}\b", plain, re.I), w


def test_speech_converted_to_d_with_oc_form_and_capped():
    p, _ = build()
    lines = re.findall(r"<d>\[English\] (.*?)</d>", p)
    assert "Fuck, harder, daddy." in lines and "Take it." in lines
    assert len(lines) == 5  # U52: convert_speech keeps all spoken lines (no silent/cap drops)
    assert '"' not in re.sub(r"<d>.*?</d>", "", p.split("detailed_description:")[1])
    assert "(S1) says in a low, warm adult woman's voice, <d>" in p
    assert "(S2) says in a contrasting deep, steady adult man's voice, <d>" in p
    assert "..." not in p and "…" not in p


def test_one_camera_sentence_no_locked_with_push_in():
    p, _ = build()
    desc = p.split("detailed_description:\n", 1)[1]
    cams = [s for s in re.split(r"(?<=[.!?])\s+", desc) if re.search(r"^(?:\[Shot 1\] )?The camera\b", s)]
    assert len(cams) == 1
    assert "pushes in" in cams[0] and "locked" not in cams[0]
    assert "keeping" not in cams[0]
    assert desc.startswith("[Shot 1] The camera")


def test_adds_opening_wardrobe_motion_contact():
    p, rep = build()
    assert "The clip opens on <Picture 1>: (S1) stands barefoot" in p
    assert "they fall to the wood floor beside the bed and stay there" in p
    assert "garter belt and thigh-high stockings stay on her body" in p
    assert "PRIMARY MOTION - continuous deep frontal thrust, about one full cycle per second" in p
    assert "fully inside her vagina" in p
    assert "chemise" not in p.split("detailed_description:")[1]


def test_position_beat_added_when_writer_opens_in_position_only():
    raw = "detailed_description:\n[Shot 1] He thrusts hard into her."
    p, rep = br.finalize_writer_prompt(raw, CAST)
    assert CAST["position_beat"].replace("<Subject 2>", "(S2)") in p
    assert any("move-into-position" in a for a in rep["added"])


def test_consistency_gate_legs():
    raw = ("detailed_description:\n[Shot 1] She lies on her back. Her legs wrap around his waist. "
           "Her ankles rest over his shoulders as he thrusts.")
    _, rep = br.finalize_writer_prompt(raw, CAST)  # Render cleanup step 4 (Max Architect 3, 2026-11-13, Derrick t1355): style lint is a warning, not a stop
    assert any("leg position" in w for w in rep["warnings"]) and not rep["issues"]


def test_consistency_gate_facing_and_surface():
    assert any("facing" in i for i in br.check_writer_consistency("She rides him facing him. She turns facing away."))
    assert any("surface" in i for i in br.check_writer_consistency("She kneels on the wood floor. He lies on the bed."))
    assert br.check_writer_consistency("She lies on her back on the bed, facing him.") == []
    assert br.check_writer_consistency("The bra and panties lie in a heap on the wood floor. She lies on the bed.") == []


def test_build_writer_request_sets_graph_fields():
    g0 = {"c0": {"inputs": {"prompt": "old", "length": 124, "width": 1, "height": 1}},
          "noise": {"inputs": {"noise_seed": 1}}, "save": {"inputs": {"filename_prefix": "x"}}, "other": {"inputs": {}}}
    with pytest.raises(br.WriterNotReady, match="minor"):
        br.build_writer_request(g0, RAW, dict(CAST, still_read=BED_READ), prefix="community/t/F_01")
    clean_raw = RAW.replace("No minors, no real-person likeness.", "Adult scene.")
    g, prompt, _ = br.build_writer_request(g0, clean_raw, dict(CAST, still_read=BED_READ), prefix="community/t/F_01")
    assert g["c0"]["inputs"]["prompt"] == clean_raw.strip() == prompt.strip()
    assert (g["c0"]["inputs"]["length"], g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]) == (243, 768, 1344)
    assert g["noise"]["inputs"]["noise_seed"] == 51083601
    assert g["save"]["inputs"]["filename_prefix"] == "community/t/F_01"
    assert g0["c0"]["inputs"]["prompt"] == "old"


def test_missing_detailed_header_recovers_shot_from_retention():
    raw = ("summary:\nA clip.\nretention_analysis:\n`<Subject 1>` (appears in [Shot 1]): fully_preserved - face.\n\n"
           "[Shot 1]\nShe rides him on her back with heavy strokes, and Adam grips her hips.")
    p, rep = br.finalize_writer_prompt(raw, CAST)
    assert "heavy strokes" in p.split("detailed_description:")[1]
    assert "`" not in p and "Adam" not in p


def test_no_word_gate_on_descriptive_words():
    raw = RAW.replace("Skin slaps on skin.", "Her small waist twists. Good girl, she hears.")
    p, _ = build(raw)
    assert "small waist twists" in p



# --- 2026-11-11 pmfix3 (Derrick t833u): Prompt maker's top 3 builder fixes ---------------------------------------
DOGGY = dict(CAST, position_check=r"\bhands and knees\b|\ball fours\b",
             move_check=r"\bhands and knees\b|\ball fours\b|\bkneels? on the mattress\b",
             position_beat="She climbs onto the bed and settles onto her hands and knees.")
MISS = dict(CAST, move_check=r"\b(lies|lie|lying|lowers?|lays?)\b[^.]{0,40}\b(back|onto (?:her|the) (?:back|sheets|mattress|pillows|forearms|elbows))")


def desc_of(p):
    return p.split("detailed_description:\n", 1)[1]


def test_fix1_writer_opener_kept_and_position_beat_after_last_standing_sentence():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "At first she stands exactly as <Picture 1> shows, beside the bed. She stands still for a breath. "
           "He thrusts into her with deep strokes.")
    p, rep = br.finalize_writer_prompt(raw, CAST)
    d = desc_of(p)
    assert "The clip opens on <Picture 1>" not in d
    assert any("builder opener skipped" in a for a in rep["added"])
    assert d.index("She stands still for a breath.") < d.index(CAST["position_beat"].replace("<Subject 2>", "(S2)")) < d.index("deep strokes")


def test_fix1_position_beat_skipped_when_writer_already_moves():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "At first she stands exactly as the still shows. She lies back onto the pillows, and he thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, MISS)
    assert MISS["position_beat"] not in p
    assert not any("move-into-position" in a for a in rep["added"])


def test_fix1_doggy_move_check_matches_kneels_on_the_mattress():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "She turns to the bed and kneels on the mattress, and he thrusts deep from behind.")
    p, _ = br.finalize_writer_prompt(raw, DOGGY)
    assert DOGGY["position_beat"] not in p


def test_fix2_wardrobe_line_is_single_source():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "She hooks her thumbs into the stocking tops and peels the sheer stockings down her calves. "
           "It lands in a pile on the floor. They stay there. "
           "He kneels between her spread thighs in dark trousers, his hands on her knees. "
           "He pulls his shirt off over his head, his trousers; "
           "He enters her and thrusts deep. She slides the panties down her thighs and kicks them away.")
    p, rep = br.finalize_writer_prompt(raw, CAST)
    d = desc_of(p)
    assert "peels the sheer stockings" not in d
    assert "It lands" not in d and "They stay there" not in d  # orphans of a dropped sentence
    assert "He kneels between her spread thighs, his hands on her knees." in d  # clause dropped, sentence kept
    assert "dark trousers" not in d and "his trousers;" not in d and "pulls his shirt" not in d
    assert "slides the panties down" not in d  # removal after penetration never survives
    assert d.count("stay on her body") == 1 and d.count("pulls off his shirt and trousers") == 1
    assert any(v["code"] == "W2" for v in rep["violations"])  # pmfix4: the tracker logs removal after penetration


A02_EXCERPT = """detailed_description:
[Shot 1] The camera holds a low rear three-quarter mid-shot at hip height, keeping her face and both faces readable.
She kneels on the mattress on her hands and knees, and he thrusts deep from behind. (S1) says in a low, soft, breathy voice: <d>[English] Fuck me deeper.</d> (S2) says in a low, rough male voice: <d>[English] Take it. Don't close.</d> The thrusts become rougher, his hips snapping forward. (S1) says in a low, soft, breathy voice: <d>[English] Use me.</d> (S2) says in a low, rough male voice: <d>[English] Good girl. All the way.</d> The camera keeps the two-shot to the last frame. By the end the strokes keep their full rhythm, the clip ending mid-thrust.
"""


def test_fix3_a02_regression_all_four_spoken_lines_and_closing_text_survive():
    p, _ = br.finalize_writer_prompt(A02_EXCERPT, DOGGY)
    lines = re.findall(r"<d>\[English\] (.*?)</d>", p)
    assert lines == ["Fuck me deeper.", "Take it. Don't close.", "Use me.", "Good girl. All the way."]
    assert "the clip ending mid-thrust" in p
    assert "The thrusts become rougher" in p


def test_fix3_a02_real_writer_output_keeps_four_lines():
    raw_path = Path(__file__).resolve().parents[2] / "runs" / "oc_10pos_20261111" / "writer_test_pipeline" / "A" / "02_doggy" / "writer_output.txt"
    if not raw_path.exists():
        pytest.skip("A_02 writer output not on this machine")
    p, _ = br.finalize_writer_prompt(raw_path.read_text(encoding="utf-8"), DOGGY, strict=False)
    lines = re.findall(r"<d>\[English\] (.*?)</d>", p)
    for want in ("Fuck me deeper.", "Use me.", "Good girl. All the way."):
        assert want in lines
    assert len(lines) == 4


def test_fix3_cap_drops_only_the_surplus_line():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "He thrusts deep. (S1) says in a voice: <d>[English] One.</d> (S1) says in a voice: <d>[English] Two.</d> "
           "Her hips rise to meet him, and (S1) says in a voice: <d>[English] Three.</d> Her thighs shake.")
    p, _ = br.finalize_writer_prompt(raw, CAST)
    assert re.findall(r"<d>\[English\] (.*?)</d>", p) == ["One.", "Two.", "Three."]
    assert "Her hips rise to meet him" in p and "Her thighs shake." in p


def test_fix3_shot_recovery_only_at_line_start_and_no_retention_in_action():
    raw = ("summary:\nA clip.\nretention_analysis:\n<Subject 1> (appears in [Shot 1]): fully_preserved - face.\n"
           "<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - room.\n"
           "[Shot 1] The camera holds a static two-shot keeping both faces. He thrusts deep with heavy strokes.")
    p, _ = br.finalize_writer_prompt(raw, CAST)
    d = desc_of(p)
    assert "heavy strokes" in d and "fully_preserved" not in d and "appears in" not in d
    raw2 = ("retention_analysis:\n<Subject 1> (appears in [Shot 1]): fully_preserved - face.\n"
            "He thrusts deep with heavy strokes.")
    p2, _ = br.finalize_writer_prompt(raw2, CAST)
    assert "heavy strokes" in desc_of(p2) and "fully_preserved - face" not in desc_of(p2)


def test_fix3_primary_motion_case_insensitive_keep_one():
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "Primary motion - continuous deep thrust, one full cycle every half second. He drives in. "
           "PRIMARY MOTION — slow grind, two cycles per second.")
    p, _ = br.finalize_writer_prompt(raw, CAST)
    assert len(re.findall(r"(?i)primary motion", p)) == 1
    assert "one full cycle every half second" in p and "slow grind" not in p
    raw2 = raw.replace(", one full cycle every half second", "").replace(", two cycles per second", "")
    p2, _ = br.finalize_writer_prompt(raw2, CAST)
    assert len(re.findall(r"(?i)primary motion", p2)) == 1 and CAST["primary_motion"] in p2


def test_fix3_strips_hand_copies_and_phase_labels_keeps_skin_words_as_written():
    # pmfix5 (Derrick t851u): skin words the brief asks for stay exactly as written (here the brief asks for sweat and flush)
    raw = ("detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "
           "Action onset: She grips his shoulders, HAND ANATOMY HARD-LOCKED - exactly five separate fingers, readable knuckles, "
           "no melt, merge or extra digit; his hand braces flat. Continuous development: He thrusts deep, hips flush, "
           "her skin flushing red across her chest. Sweat makes her glisten, her thighs wet and shiny, a sheen on her belly. "
           "Her wet skin trembles, his hips driving with a wet skin-on-skin slap.")
    p, _ = br.finalize_writer_prompt(raw, dict(CAST, brief="sweaty, flushed skin"))
    d = desc_of(p)
    assert "HAND ANATOMY" not in d and "Action onset" not in d and "Continuous development" not in d
    assert "She grips his shoulders; his hand braces flat." in d  # separator kept (G_01 run-on)
    for kept in ("flushing red", "glisten", "wet and shiny", "a sheen on her belly", "Her wet skin trembles", "hips flush"):
        assert kept in d, kept
    assert "damp skin with visible pores" not in d
    assert p.count(br.R11_HAND) == 1


def test_fix3_extra_camera_sentence_keeps_action_after_semicolon_and_closing_kept():
    raw = A02_EXCERPT.replace(
        "The camera keeps the two-shot to the last frame. By the end",
        "The camera holds its rear mid-shot, the lens on the join; the motion is continuous, his pelvis driving in, her skin shiny. "
        "The end state is mid-motion: her hair over her face, the chemise crumpled on the sheets, his hand tight on her hip. By the end")
    p, _ = br.finalize_writer_prompt(raw, DOGGY)
    d = desc_of(p)
    assert "The motion is continuous, his pelvis driving in, her skin shiny." in d  # dynsafe: unrequested gloss is flagged, not cut
    assert "his hand tight on her hip" in d and "chemise" not in d
    assert len(re.findall(r"(?i)\bthe camera holds its rear\b", d)) == 0


# --- 2026-11-11 pmfix4 (Derrick t39u/t40u/t839s3396): round 3 -------------------------------------------------------
import importlib.metadata


def _cast(**kw):
    return dict(CAST, still_garments="a sheer nude bra, a garter belt, sheer panties, thigh-high stockings and a choker",
                absent_garments=r"\b(chemise|slip dress|nightgown|robe|blouse)\b|\bthe sheer fabric\b", **kw)


HDR = "detailed_description:\n[Shot 1] The camera holds a static two-shot keeping both faces. "


# item 1: wardrobe + position tracker
def test_tracker_codes_and_repairs():
    sents = ["She walks the two steps to the bed, weight rolling onto each foot, and unclips the stockings from the garter belt.",
             "She unclasps the bra and lets it drop to the floor.", "It lands in a heap.",
             "She lowers onto her back on the white sheets.", "He enters her and thrusts deep.",
             "She peels the panties down her thighs.", "She stands up beside the bed."]
    out, state, viol = br.track_state(sents, _cast(garments_stay="garter belt, thigh-high stockings and choker", move_check=MISS["move_check"]))
    codes = [(v["code"], v["idx"]) for v in viol]
    # dynsafe: the writer's first removal is valid (W1 only for a second removal by the writer); W2/W3/P1 unchanged
    assert ("W3", 0) in codes and ("W2", 5) in codes and ("P1", 6) in codes and not any(c == "W1" for c, _ in codes)
    assert out[0] == "She walks the two steps to the bed, weight rolling onto each foot."  # clause-level: the walk stays
    assert "She unclasps the bra and lets it drop to the floor." in out and "It lands in a heap." in out
    assert "She peels the panties down her thighs." not in out and "She stands up beside the bed." not in out
    assert state["garments"] == {"bra": "off", "panties": "off", "garter belt": "on", "stockings": "on", "choker": "on"}
    assert state["writer_removed"] == ["bra"] and state["builder_removed"] == ["panties"]  # hand-written cast: gap fill
    assert state["act"] and state["level"] == 2


def test_wardrobe_line_written_from_end_state():
    state = {"garments": {"bra": "off", "panties": "off", "garter belt": "on", "stockings": "on", "choker": "on"}}
    line = br.wardrobe_line(_cast(garments_stay="garter belt, thigh-high stockings and choker"), state)
    assert line.startswith("She takes off the sheer nude bra and sheer panties, and they fall to")
    assert "while the garter belt, thigh-high stockings and choker stay on her body" in line


def test_regress_with_speech_is_kept_for_writer_repair_and_linted():
    raw = HDR + ("She lowers onto her back on the white sheets. He thrusts deep. "
                 "She stands beside the bed, and (S1) says in a voice: <d>[English] Use me.</d>")
    issues, units = br.lint_writer_prompt(raw, _cast())
    assert [i["code"] for i in issues] == ["P1"] and "stands beside the bed" in issues[0]["text"]


# item 2: pySBD units, per-line cap, silent-drop invariant
def test_pysbd_installed_and_used():
    assert importlib.metadata.version("pysbd") == "0.3.4"
    units = br._sentences('He thrusts deep. (S1) says in a voice: <d>[English] Take it. Don\'t close.</d> (S2) says, '
                          '<d>[English] Good girl. All the way.</d> The thrusts become rougher.')
    assert units == ["He thrusts deep.", "(S1) says in a voice: <d>[English] Take it. Don't close.</d>",
                     "(S2) says, <d>[English] Good girl. All the way.</d>", "The thrusts become rougher."]


def test_speech_budget_drops_whole_lines_from_the_end_with_reason():
    raw = HDR + ("He thrusts deep. (S1) says in a voice: <d>[English] Use my cunt and go deeper right now, daddy.</d> "
                 "(S2) says in a voice: <d>[English] Take every inch of it and do not stop moving.</d> Her thighs shake.")
    p, rep = br.finalize_writer_prompt(raw, _cast(clip_seconds=6))  # 15-word budget
    assert len(rep["speech"]["dropped"]) == 0 and rep["speech"]["kept"] == 2
    assert "Her thighs shake." in p


def test_silent_drop_raises(monkeypatch):
    real = br.convert_speech

    def lossy(sentences, voices, **kw):
        out = real(sentences, voices, **kw)
        return [re.sub(r"<d>.*?</d>", "", s) if "Use me" in s else s for s in out]  # loses a line without a reason
    monkeypatch.setattr(br, "convert_speech", lossy)
    with pytest.raises(br.WriterPromptError, match="silent drop"):
        br.finalize_writer_prompt(A02_EXCERPT, DOGGY)


def test_spoken_line_in_a_dropped_sentence_is_kept():
    raw = HDR + "He thrusts deep. She tugs the chemise over her head and gasps, \"Don't stop.\" Her thighs shake."
    p, rep = br.finalize_writer_prompt(raw, _cast())
    assert "<d>[English] Don't stop.</d>" in p and "chemise" not in p


# item 3: lint + repair loop with a mocked writer
def test_repair_loop_rewrites_only_flagged_sentences():
    raw = HDR + "She lowers onto her back on the white sheets. He thrusts deep, fast and hard. She stands beside the bed, breathing hard."
    calls = []

    def writer(msg):
        calls.append(msg)
        idx = re.search(r"\[(\d+)\] She stands", msg).group(1)
        return f"[{idx}] She arches on the sheets, breathing hard.\n[0] CHANGED CAMERA."
    fixed, log = br.repair_writer_output(raw, _cast(), writer)
    assert len(calls) == 1 and "Problem:" in calls[0] and "He thrusts deep" not in calls[0]
    assert "She arches on the sheets, breathing hard." in fixed and "She stands beside" not in fixed
    assert "The camera holds a static two-shot keeping both faces." in fixed and "CHANGED CAMERA" not in fixed
    assert log["rounds"][0]["accepted"] and log["rounds"][0]["ignored_unflagged"] == [0] and log["remaining"] == []


def test_repair_loop_caps_at_two_rounds_and_build_request_uses_it():
    raw = HDR + "She lowers onto her back on the white sheets. He thrusts deep. She stands beside the bed, breathing hard."
    calls = []
    fixed, log = br.repair_writer_output(raw, _cast(), lambda m: calls.append(m) or "nothing useful")
    assert len(calls) == 2 and len(log["rounds"]) == 2 and log["remaining"][0]["code"] == "P1"
    base = {"c0": {"inputs": {"prompt": "", "length": 243, "width": 1, "height": 1}}, "noise": {"inputs": {"noise_seed": 0}},
            "save": {"inputs": {"filename_prefix": ""}}}
    g, prompt, rep = br.build_writer_request(base, raw, _cast(still_read=BED_READ), "x", frames=243, strict=True,
                                             writer=lambda m: re.sub(r"(?s).*?\[(\d+)\].*", r"[\1] She arches on the sheets.", m))
    assert rep["repair"]["rounds"][0]["accepted"] and "She arches on the sheets." in prompt and rep["lint"] == []


# quick wins: camera, dialogue form; skin untouched (see test above)
def test_camera_synonyms_one_move_one_end_framing():
    raw = ("detailed_description:\n[Shot 1] The camera dollies in slowly from a wide shot, then pans left across the room, "
           "into a tight mid-shot between her knees. He thrusts deep.")
    d = desc_of(br.finalize_writer_prompt(raw, CAST)[0])
    cam = d.split(". ", 1)[0]
    assert "pushes in" in cam and "pans" not in cam and "dollies" not in cam
    # dynsafe: the writer's own end framing stays (no forced two-shot); NB6: no camera tail appended
    assert "into a tight mid-shot between her knees" in cam and "stops at" not in cam and "two-shot" not in cam
    assert "keeping her face, his face and the join in frame" not in cam


def test_camera_tail_only_when_missing_and_his_face_out_of_frame():
    raw = HDR.replace("holds a static two-shot keeping both faces", "pushes in slowly and stops at a two-shot on the join") + \
        "He thrusts deep while his face stays out of frame."
    d = desc_of(br.finalize_writer_prompt(raw, CAST)[0])
    cam = d.split(". ", 1)[0]
    assert cam.count("stops at") == 1 and "his face" not in cam


def test_dialogue_one_comma_form_mouth_moves_and_matching_collapsed():
    raw = HDR + ("He thrusts deep. Her mouth moves as <Subject 1>, voice low, tight: (S1) says in a breathy voice matching the vocal "
                 "texture of <Audio 1>: <d>[English] Harder.</d> He growls, \"Take it.\"")
    p, _ = br.finalize_writer_prompt(raw, CAST)
    assert "Her mouth moves as" not in p and "matching" not in p
    assert f"(S1) says in {CAST['voice_s1']}, breathy tone, <d>[English] Harder.</d>" in p
    assert f"(S2) says in {CAST['voice_s2']}, <d>[English] Take it.</d>" in p
    assert ": <d>" not in desc_of(p)


# Prompt maker v2 review, next top 3
def test_pm_opener_detected_on_raw_text_with_absent_garment_rewritten_once():
    raw = HDR + ("At first, <Subject 1> stands facing the camera on the wood floor in the sheer chemise, garter belt, stockings, "
                 "and brief from <Picture 1>, hands at her sides, weight on her left foot. "
                 "She lowers onto her back on the white sheets. At first she stands exactly as <Picture 1> shows, smiling. He thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, _cast())
    d = desc_of(p)
    assert "The clip opens on <Picture 1>" not in d and "chemise" not in d and "At first, and" not in d
    assert ("At first, (S1) stands facing the camera on the wood floor in a sheer nude bra, a garter belt, sheer panties, "
            "thigh-high stockings and a choker, hands at her sides") in d
    assert d.count("At first") == 1 and any("second writer opener" in s for s in rep["stripped"])


def test_pm_thrusts_in_camera_text_do_not_move_the_opener():
    raw = ("detailed_description:\n[Shot 1] The camera pushes in slowly; it ends moving, thrusts still running at full tempo. "
           "The camera keeps her face readable as the thrusts land. At first she stands exactly as <Picture 1> shows her. "
           "She lowers onto her back on the white sheets. He thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, _cast())
    assert "The clip opens on <Picture 1>" not in p and any("writer opener kept" in a for a in rep["added"])


def test_pm_absent_garment_removal_whole_sentence_and_orphan_dropped_blouse_and_sheer_fabric():
    raw = HDR + ("She lowers onto her back on the white sheets. She pulls the sheer fabric over her head in one motion. "
                 "It leaves her hands and lands in a small heap. She unbuttons the blouse and lets it fall. He thrusts deep.")
    d = desc_of(br.finalize_writer_prompt(raw, _cast())[0])
    assert "sheer fabric" not in d and "It leaves her hands" not in d and "blouse" not in d and "He thrusts deep." in d


def test_pm_wider_removal_verbs_and_clause_level_for_sound():
    raw = HDR + ("She lowers onto her back on the white sheets. He thrusts deep. "
                 "The room tone is a low hum, the garter clips releasing, skin slapping skin, his low grunt. "
                 "The sheer stockings stay on her legs, tops held at mid-thigh by her fingers, released. "
                 "The sheer bra comes off, her shoulders pulling free.")
    d = desc_of(br.finalize_writer_prompt(raw, _cast())[0])
    assert "The room tone is a low hum, skin slapping skin, his low grunt." in d
    assert "held at mid-thigh" not in d and "The sheer bra comes off" not in d


def test_pm_scaffold_dash_ten_seconds_negations_doggy_back_throat_pubic():
    raw = HDR + ("She kneels on the mattress on her hands and knees. He thrusts deep across the full ten seconds — , the tempo does not slow. "
                 "His hand slides to her throat, and he presses her back against the mattress, his hips snapping forward. "
                 "His pubic bone presses against her lower back. By the end nothing settled, the strokes still landing.")
    p, rep = br.finalize_writer_prompt(raw, dict(_cast(position="doggy"), move_check=DOGGY["move_check"]))
    d = desc_of(p)
    assert "ten seconds" not in d and "—" not in d and "—," not in br._strip_sentence("The camera holds behind her — then pulls out slowly.") and "does not slow" not in d and "holds its pace" in d
    assert "throat" not in d and "presses her chest down to the surface beneath her" in d and "everything still moving" in d  # dynsafe: no mattress default
    issues, _ = br.lint_writer_prompt(raw, dict(_cast(position="doggy")))
    assert any(i["code"] == "X1" for i in issues)
    raw2 = raw.replace("By the end", "Her hand closes around her throat. By the end")
    p2, _ = br.finalize_writer_prompt(raw2.replace("His hand slides to her throat, and he", "He"),
                                      dict(_cast(position="doggy", throat_contact=True), move_check=DOGGY["move_check"]))
    assert "throat" in desc_of(p2)


def test_pm_sound_sentence_with_absent_garment_removal_keeps_its_sound():
    raw = HDR + ("She lowers onto her back on the white sheets. He thrusts deep. "
                 "The room tone of quiet curtains runs under everything; the mattress creaks, skin slapping skin, the sheer fabric "
                 "hissing softly as it slides down her thighs, the garter clips clicking small as they unclip, the bra and briefs "
                 "landing with a soft whisper on the oak floor, his low grunt on the hard drives.")
    d = desc_of(br.finalize_writer_prompt(raw, _cast())[0])
    assert "the mattress creaks, skin slapping skin, his low grunt on the hard drives." in d
    assert "sheer fabric" not in d and "unclip" not in d and "landing with a soft whisper" not in d


# ---- pmfix5: Prompt maker v3 review fixes 1-3 + light skin rule
def _desc5(raw_desc, **kw):
    raw = raw_desc if raw_desc.startswith("detailed_description:") else "detailed_description:\n" + raw_desc
    p, rep = br.finalize_writer_prompt(raw, _cast(**kw), strict=False)
    return desc_of(p), p, rep


def test_pm5_lead_crosses_audio_token_no_double_lead_and_no_index_timbre():
    d, p, rep = _desc5("[Shot 1] The camera holds a static two-shot keeping both faces. "
                       "She lowers onto her back on the white sheets. "
                       "(S1) says in <Audio 1>'s voice with signature vocal timbre, a low, soft, breathy voice, unhurried, <d>[English] Fuck me harder.</d> "
                       "(S1) says in <Audio 1> as <Subject 1>, a low voice with light vocal fry, \"Deeper.\"")
    assert "signature vocal timbre" not in p and "<Audio 1> as" not in d
    assert not br._DOUBLE_LEAD_RE.search(d)
    assert d.count("(S1) says in a low, warm adult woman's voice") == 2
    assert not [i for i in rep["issues"] if "lead" in i or "INDEX" in i]


def test_pm5_gate_flags_double_lead_and_index_timbre_on_oc():
    assert br._DOUBLE_LEAD_RE.search("(S1) says in a low voice, and (S1) says in a warm voice, <d>[English] Hi.</d>")
    assert br._LEAD_RE.search("(S1) says in <Audio 1> as <Subject 1>, a low voice, ")


def test_dynsafe_pull_out_and_hold_stay_as_written():
    # dynsafe (limit 1): a pull-out stays a pull-out and a hold stays a hold; only the missing framing items are appended
    d, _, _ = _desc5("[Shot 1] The camera opens on the still — waist-up, then pulls out with small amplitude at slow speed to a medium shot. "
                     "She lowers onto her back on the white sheets.")
    cam = d.split(". ")[0]
    assert "pulls out with small amplitude at slow speed to a medium shot" in cam and "pushes in" not in cam
    assert "two-shot" not in cam and "—" not in cam
    d2, _, _ = _desc5("[Shot 1] The camera holds a waist-up mid-shot at bed height, both faces readable. She lowers onto her back on the white sheets. "
                      "His face stays out of frame.")
    cam2 = d2.split(". ")[0]
    assert cam2.startswith("[Shot 1] The camera holds a waist-up mid-shot at bed height, both faces readable")
    assert "pushes in" not in cam2 and "two-shot" not in cam2 and "his face" not in cam2


def test_pm5_camera_starting_on_the_bed_starts_from_the_standing_frame():
    d, _, _ = _desc5("[Shot 1] The camera starts low at knee height, a medium two-shot waist-up on the bed; the camera pushes in with small "
                     "amplitude at slow speed to a tight two-shot, and that framing is the final framing. "
                     "At first she stands exactly as <Picture 1> shows her, weight on her left foot. She lowers onto her back on the white sheets.")
    assert "The camera pushes in from the standing frame of <Picture 1> with small amplitude" in d
    assert "on the bed;" not in d.split(". ")[0] and "final framing" not in d


def test_pm5_camera_echo_keeping_collapsed_and_upper_bodies_keep_the_join():
    cams = br._resolve_camera(["The camera pushes in to a low two-shot, keeping her face and the join in frame, keeping his face in frame.",
                               "She lowers onto her back."], "keeping her face, his face and the join in frame")
    assert ", keeping her face and the join and his face in frame" in cams[0] and cams[0].count("keeping") == 1
    cams = br._resolve_camera(["The camera pushes in to a chest-height two-shot with their upper bodies and faces.", "She rides."],
                              "keeping her face, his face and the join in frame")
    assert "upper bodies" not in cams[0] and "down to the join" in cams[0]


def test_pm5_opener_cast_list_swapped_without_absent_garment():
    d, _, _ = _desc5(HDR + "<Subject 1> stands facing the lens on the floor in the sheer beige bra, gartered panties, and thigh-high stockings, "
                     "bare feet on the wood. She lowers onto her back on the white sheets.")
    assert "in a sheer nude bra, a garter belt, sheer panties, thigh-high stockings and a choker, bare feet" in d
    assert "beige" not in d and "gartered" not in d
    d2, _, _ = _desc5(HDR + "The opening frame: she stands on the floor, gaze on the lens, the sheer nude mesh bra, garter belt, thong and sheer "
                      "thigh-high stockings exactly as the photograph shows them. She lowers onto her back on the white sheets.")
    assert "thong" not in d2 and "in a sheer nude bra, a garter belt, sheer panties, thigh-high stockings and a choker exactly as" in d2


def test_pm5_polish_floor_briefs_an_pronoun_comma_and_position_repeat():
    d, p, _ = _desc5("[Shot 1] The camera opens at a eye-level shot, keeping both faces. She stands exactly as <Picture 1> shows her. "
                     "Weight shifts forward onto hands and knees. She climbs onto the bed and settles onto her hands and knees, palms in the sheets. "
                     "He, mounts behind her and thrusts deep. The bra and briefs lie on the oak floor beside the bed.",
                     position="doggy", position_check=r"\bhands and knees\b", move_check=r"\bhands and knees\b")
    assert "an eye-level" in d and "bra and panties lie on the oak floor" in d  # dynsafe: the oak -> wood swap is gone
    assert "He mounts behind her" in d and "Weight shifts forward onto hands and knees." not in d
    assert "settles onto her hands and knees" in d


def test_pm5_summary_he_strips_her_becomes_she_takes_off():
    raw = ("summary:\n<Subject 2> strips her sheer lingerie off and lays her down. He, mounts her.\n\n" + HDR +
           "She lowers onto her back on the white sheets.")
    p, _ = br.finalize_writer_prompt(raw, _cast(), strict=False)
    summ = p.split("summary:")[1].split("retention_analysis")[0]
    assert "strips her" not in summ and "<Subject 1> takes off her clothes and lays her down" in summ
    assert "He mounts her" in summ


def test_pm5_primary_motion_em_dash_label_is_kept_as_the_one_motion():
    d, _, rep = _desc5(HDR + "She lowers onto her back on the white sheets. He enters her. "
                       "PRIMARY MOTION — continuous deep thrust, about one full cycle per second, full depth travel.")
    assert d.count("PRIMARY MOTION") == 1 and "PRIMARY MOTION - continuous deep thrust" in d


# (B) light skin rule
def test_skin_unrequested_redness_flagged_not_stripped():
    # dynsafe (limit 2, flag-only): nothing is deleted; undirected redness is flagged, redness tied to a written action is not
    d, _, rep = _desc5(HDR + "She lowers onto her back on the white sheets. He enters her. "
                       "Her face is flushed, eyes half-lidded, jaw set, gaze locked to his. "
                       "By the end she rides the rhythm hard, hips meeting his, eyes wet with effort, the struck skin of her hip red. "
                       "His hand gripping her hip leaves red marks, her skin flushing red across her chest, back, and cheeks, her mouth open.")
    assert "Her face is flushed, eyes half-lidded, jaw set, gaze locked to his." in d
    assert "leaves red marks" in d and "hip red" in d and "eyes wet with effort" in d
    flagged = [f["phrase"] for f in rep["skin_unrequested"]]
    assert any("flushed" in x for x in flagged) and not any("red marks" in x for x in flagged)  # grip -> cause and effect
    assert all(f["code"] == "skin_unrequested" for f in rep["skin_unrequested"])


def test_skin_contact_flush_is_not_skin():
    d, _, _ = _desc5(HDR + "She lowers onto her back on the white sheets. He thrusts, hips flush against her pelvis on every stroke.")
    assert "hips flush against her pelvis" in d


def test_skin_gloss_flagged_unless_asked_lighting_untouched():
    body = (HDR + "She lowers onto her back on the white sheets. He enters her. "
            "Soft daylight falls across her back, a faint sheen on damp skin at the collarbone. Her inner thighs are wet and shiny, her skin glistens. "
            "Hair sticks to the damp skin at her temples.")
    d, _, rep = _desc5(body)
    # dynsafe: the light sentence is out of scope (kept whole, not flagged); the body gloss is kept and flagged
    assert "Soft daylight falls across her back, a faint sheen on damp skin at the collarbone." in d
    assert "Her inner thighs are wet and shiny, her skin glistens." in d and "sticks to the damp skin at her temples" in d
    flagged = [f for f in rep["skin_unrequested"] if f["kind"] == "gloss"]
    assert flagged and not any("daylight" in f["text"] for f in flagged)
    d2, _, rep2 = _desc5(body, brief="she has sex with him, oiled up, position: missionary")
    assert "sheen" in d2 and "glistens" in d2 and "wet and shiny" in d2 and not rep2["skin_unrequested"]
    d3, _, _ = _desc5(HDR + "She lowers onto her back on the white sheets. Her cheeks flush red.", brief="leave red marks, spank her")
    assert "flush red" in d3


def test_skin_no_default_matte_cue_added():
    d, p, _ = _desc5(HDR + "She lowers onto her back on the white sheets.")
    assert "matte" not in d and "pores" not in d


# ---- pmfix5 garments (Derrick t856s3457): wider clothing list in the tracker
@pytest.mark.parametrize("name,key", [
    ("white bikini top", "bra"), ("black lace bralette", "bra"), ("red bikini bottoms", "panties"), ("bikini bottom", "panties"),
    ("sheer nude bra", "bra"), ("black thong", "panties"), ("garter belt", "garter belt"), ("thigh-high stockings", "stockings"),
    ("velvet choker", "choker"), ("black one-piece swimsuit", "swimsuit"), ("blue swimsuit", "swimsuit"),
    ("yellow sundress", "dress"), ("red silk dress", "dress"), ("satin gown", "dress"),
    ("white crop top", "top"), ("grey t-shirt", "top"), ("silk blouse", "top"), ("black tank top", "top"), ("button shirt", "top"),
    ("denim skirt", "skirt"), ("pleated miniskirt", "skirt"), ("denim shorts", "shorts"),
    ("blue jeans", "pants"), ("black leggings", "pants"), ("leather jacket", "jacket"), ("wool cardigan", "jacket"), ("silk robe", "jacket"),
    ("high heels", "shoes"), ("ankle boots", "shoes"), ("white sneakers", "shoes"),
])
def test_garment_keys_wide(name, key):
    assert br._garment_key(name) == key


def test_garment_keys_do_not_fire_on_his_clothes_or_pose_words():
    for text in ("he pulls off his shirt", "his jacket hangs open", "she climbs on top of him", "the top of the bed",
                 "her heels press into the sheets", "she pants hard"):
        named = [k for k, rx in br._GARMENT_KEYS if re.search(rx, text, re.I)]
        assert not named, (text, named)


def test_tracker_and_wardrobe_line_for_a_sundress_and_heels():
    c = dict(_cast(), garments_off="yellow sundress", garments_stay="white heels", garments_floor="the beach towel",
              still_garments="a yellow sundress and white heels", absent_garments=r"\b(chemise|robe)\b",
              move_check=MISS["move_check"])
    sents = ["She pulls the yellow sundress over her head and drops it on the sand.", "She lowers onto her back on the towel.",
             "He enters her and thrusts deep.", "She kicks off her heels."]
    out, state, viol = br.track_state(sents, c)
    codes = [(v["code"], v["idx"]) for v in viol]
    assert ("W3", 3) in codes and ("W2", 3) in codes and not any(c == "W1" for c, _ in codes)  # dynsafe: writer's removal valid
    assert state["garments"] == {"dress": "off", "shoes": "on"} and state["writer_removed"] == ["dress"]
    line = br.wardrobe_line(c, state)
    assert line.startswith("The yellow sundress she took off stays on the sand, and the white heels stay on her body;")  # brief item 4


def test_tracker_bikini_top_like_bra_bottoms_like_panties():
    c = dict(_cast(), garments_off="white bikini top and white bikini bottoms", garments_stay="", still_garments="a white bikini",
              move_check=MISS["move_check"])
    out, state, viol = br.track_state(["She unties the white bikini top and lets it drop.", "She slides the bikini bottoms down her thighs."], c)
    assert [v["code"] for v in viol] == []  # dynsafe: the writer's own removals are valid
    assert state["garments"] == {"bra": "off", "panties": "off"} and state["builder_removed"] == []
    assert br.wardrobe_line(c, state).startswith(f"The white bikini top and white bikini bottoms she took off stay on {c['garments_floor']}")


@pytest.mark.parametrize("off,key", [("blue jeans", "pants"), ("white crop top", "top"), ("denim skirt", "skirt"),
                                     ("denim shorts", "shorts"), ("leather jacket", "jacket"), ("black one-piece swimsuit", "swimsuit")])
def test_tracker_second_removal_flags_each_new_key(off, key):
    c = dict(_cast(), garments_off=off, garments_stay="", still_garments="a " + off, move_check=MISS["move_check"])
    out, state, viol = br.track_state([f"She peels off the {off} and tosses it aside.", f"She peels off the {off} again."], c)
    assert [v["code"] for v in viol] == ["W1"] and state["garments"] == {key: "off"}  # dynsafe: W1 = the writer removes it twice


# --- stillfacts round (Derrick t51u/t52u): refusal gate + one retry, still-facts block and swap ---------------------
F01_REFUSAL = """I can't write a prompt for this scene.

The attached start image shows the woman in lingerie on a stage/pole setting. That's fine as an opening composition, and I can describe her getting into position (R16) before the act, per your rules.

But I'm not able to generate explicit sexual content - I can't write out the missionary sex scene itself with the physical detail this lane requires.

If you'd like, I can:
- Write a non-explicit version of the prompt for this same start image (her on the pole, moving toward him, tension, no explicit act).
- Describe her getting into position and stop before the primary motion.

Let me know which, and I'll write it to `prompt.txt`.
"""
POLE_READ = {"room": "a dimly lit stage with a pole", "place": "stage", "bed": False, "sheets": "", "surface": "the stage floor",
             "floor": "dark floor", "light": "dramatic purple and red spotlighting",
             "pose": "stands beside a pole with one hand gripping it, hips tilted to the side", "props": ["a chrome pole"],
             "garments": [{"type": "top", "name": "black mesh strappy bra top"},
                          {"type": "other", "name": "black mesh strappy bottom with garter straps"},
                          {"type": "stockings", "name": "black fishnet thigh-high stockings"}]}
ASK = "she has sex with him, position: missionary"


def test_sf_gate_flags_the_real_f01_refusal_and_build_refuses_it():
    why = br.writer_gate(F01_REFUSAL)
    assert any(w.startswith("refusal phrase") for w in why)
    assert any("missing detailed_description" in w for w in why)
    with pytest.raises(br.WriterRefusal, match="NOT_READY"):
        br.build_writer_request({"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}, F01_REFUSAL, CAST, "x/y")


@pytest.mark.parametrize("phrase", ["I can't write that.", "I'm not able to do this.", "I am unable to write this scene.",
                                    "Here is a non-explicit version.", "Let me know which one you want."])
def test_sf_gate_each_refusal_phrase(phrase):
    assert any(w.startswith("refusal phrase") for w in br.writer_gate(HDR + phrase))


def test_sf_gate_ignores_spoken_lines_and_passes_a_real_prompt():
    assert br.writer_gate(HDR + 'She gasps <d>I\'m not able to stop, let me know which way.</d> He thrusts.') == []
    assert br.writer_gate(RAW, CAST, completion_tokens=1200, ask=ASK) == []


def test_sf_gate_short_output_and_act_false():
    assert any("completion tokens" in w for w in br.writer_gate(RAW, completion_tokens=158))
    tame = HDR + "She stands by the bed and smiles at him. He watches her from the doorway."
    assert any(w.startswith("act:false") for w in br.writer_gate(tame, CAST, completion_tokens=900, ask=ASK))
    assert br.writer_gate(tame, CAST, completion_tokens=900, ask="she poses for him") == []


def test_sf_gated_write_retries_once_then_not_ready():
    seq = iter([(F01_REFUSAL, 158), (RAW, 1300)])
    raw, log = br.gated_write(lambda: next(seq), CAST, ask=ASK)
    assert raw == RAW and log["status"] == "OK" and len(log["attempts"]) == 2
    calls = []
    raw, log = br.gated_write(lambda: calls.append(1) or (F01_REFUSAL, 158), CAST, ask=ASK)
    assert raw is None and log["status"] == "NOT_READY" and len(calls) == 2


def test_sf_garment_type_other_by_name_and_bottoms():
    assert br.garment_type_key("other", "black mesh strappy bottom with garter straps") == "panties"
    assert br.garment_type_key("top", "black mesh strappy bra top") == "bra"
    assert br.garment_type_key("top", "white crop top") == "top"
    assert br.garment_type_key("bottoms", "denim bikini bottoms") == "panties"
    assert br.garment_type_key("other", "black leather choker") == "choker"
    assert br._garment_key("she slides her bottoms down her thighs") == "panties"


def test_sf_facts_block_no_bed_and_no_extra_age_line():
    b = br.still_facts_block(POLE_READ)
    assert "a dimly lit stage with a pole" in b and "No bed, mattress or sheets" in b and "the stage floor" in b
    assert "black mesh strappy bra top; black mesh strappy bottom with garter straps; black fishnet thigh-high stockings" in b
    assert "she stands beside a pole" in b and "a chrome pole" in b and "18+" not in b


def test_sf_apply_swaps_bed_and_garment_nouns_keeps_d_lines():
    t = ('She kneels on the bed in her lace bra, the sheets bunched under her knees. <d>Get on the bed.</d> '
         'Her black lace panties slide down, her fishnet stockings stay on, and the wood floor creaks under the mattress.')
    out, rep = br.apply_still_facts(t, POLE_READ)
    assert "<d>Get on the bed.</d>" in out
    plain = br._D_RE.sub("", out)
    assert not re.search(r"\b(bed|mattress|sheets)\b", plain)
    assert "her black mesh strappy bra top" in out and "Her black mesh strappy bottom with garter straps" in out
    assert "her fishnet stockings" in out  # a subset of the still's own name is kept
    assert "the dark floor" in out and "wood floor" not in out
    assert rep["swaps"] and "black mesh strappy bra top" in rep["hits"] and "a chrome pole" in rep["misses"]
    assert "a chrome pole" in br.apply_still_facts("Her hand grips the pole.", POLE_READ)[1]["hits"]
    assert br.apply_still_facts("The mattress dips.", POLE_READ)[0] == "The stage floor dips."


def test_sf_no_bed_still_drives_builder_lines_and_c3():
    c = dict(CAST, still_read=POLE_READ)
    p, rep = br.finalize_writer_prompt(RAW, c, strict=False)
    assert "and a dimly lit stage with a pole, its light" in p
    assert "fully_preserved - a dimly lit stage with a pole, the stage floor, the dark floor, the light" in p
    assert "the bedroom, the bed and its sheets" not in p and rep["still_facts"]["swaps"]
    issues, units = br.lint_writer_prompt(RAW, dict(CAST, still_bed=False, surface="the stage floor"))
    c3 = [i for i in issues if i["code"] == "C3"]
    assert c3 and all("no bed in the start image; keep them on the stage floor" in i["why"] for i in c3)


def test_sf_no_read_is_neutral_never_bedroom_and_c3_repair_text_follows_still():
    p, _ = build(strict=False)
    head = p.split("detailed_description:")[0]
    assert "the bedroom" not in head and "the bed and its sheets" not in head  # dynsafe (limit 5): no bedroom fallback
    assert "the setting shown in <Picture 1>" in head
    assert "keep them on the bed" not in br._LINT_CODES["C3"]
    assert "on one surface, the bed" in br._LINT_CODES["C3"].format(surface="the bed")


# --- dynsafe (2026-11-11, Derrick t903u): dynamic safeguards from Prompt maker's research ---------------------------
KNEEL_READ = {"room": "a living room with a grey sofa and black ropes hanging from a beam", "place": "living room", "bed": False,
              "sheets": "", "surface": "the parquet floor", "floor": "parquet floor", "light": "warm lamp light",
              "framing": "full-body, eye-level, front", "pose": "kneels on the parquet floor gripping two black ropes",
              "facing_camera": True, "skin": "glossy tanned skin",
              "garments": [{"type": "dress", "name": "cream satin slip dress"}]}
BJ_ASK = "she gives him a blowjob"
STAGE_HDR = "detailed_description:\n[Shot 1] The camera holds a static medium shot at hip height, keeping her face in frame. "


def _stage_cast(position="missionary", ask=ASK, read=POLE_READ):
    return br.make_cast(read, position, ask)


def test_dynsafe_make_cast_uses_still_nouns_and_keeps_type_other():
    c = _stage_cast()
    names = [g["name"] for g in c["inventory"]]
    assert names == ["black mesh strappy bra top", "black mesh strappy bottom with garter straps", "black fishnet thigh-high stockings"]
    assert c["still_garments"] == ("a black mesh strappy bra top, a black mesh strappy bottom with garter straps and "
                                   "black fishnet thigh-high stockings")  # article by number: no 'a ... stockings'
    absent = re.compile(c["absent_garments"], re.I)
    assert absent.search("chemise") and not absent.search("garter") and not absent.search("thong") and not absent.search("stockings")
    assert c["undress"] is False and c["still_bed"] is False and c["surface"] == "the stage floor"
    assert "bedroom" not in " ".join(str(v) for k, v in c.items() if isinstance(v, str))
    assert br.make_cast(KNEEL_READ, "doggy", ASK)["inventory"][0]["slot"] == "full-body"


def test_dynsafe_no_still_read_is_not_ready():
    with pytest.raises(br.WriterNotReady, match="no still read"):
        br.make_cast(None, "missionary", ASK)
    g0 = {"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}
    with pytest.raises(br.WriterNotReady, match="NOT_READY: no still read"):
        br.build_writer_request(g0, RAW, CAST, prefix="x")  # no bedroom fallback in production


def test_dynsafe_refusal_still_fails_closed_with_a_read():
    g0 = {"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}
    with pytest.raises(br.WriterRefusal, match="NOT_READY"):
        br.build_writer_request(g0, F01_REFUSAL, _stage_cast(), prefix="x")


def test_dynsafe_hold_and_pull_out_kept_on_a_production_cast():
    raw = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the stage floor. He thrusts deep."
    p, rep = br.finalize_writer_prompt(raw, _stage_cast())
    cam = desc_of(p).split(". ")[0]
    assert cam.startswith("[Shot 1] The camera holds a static medium shot at hip height, keeping her face")
    assert "pushes in" not in cam and "two-shot" not in cam
    raw2 = raw.replace("holds a static medium shot at hip height, keeping her face in frame",
                       "pulls out with small amplitude at slow speed to a wide shot")
    p2, rep2 = br.finalize_writer_prompt(raw2, _stage_cast())
    assert "pulls out with small amplitude at slow speed to a wide shot" in p2 and "pushes in" not in desc_of(p2).split(". ")[0]
    assert any(f["code"] == "K2" for f in rep2["flags"])
    assert any(i["code"] == "K2" for i in br.lint_writer_prompt(raw2, _stage_cast())[0])


def test_dynsafe_track_on_still_act_flagged_arc_accepted():
    raw = STAGE_HDR.replace("holds a static medium shot at hip height, keeping her face in frame",
                            "tracks to her right side with small amplitude at slow speed") + \
        "She lowers onto her back on the stage floor. He thrusts deep."
    p, rep = br.finalize_writer_prompt(raw, _stage_cast())
    assert "tracks to her right side" in p and any(f["code"] == "K1" for f in rep["flags"])
    assert any(i["code"] == "K1" for i in br.lint_writer_prompt(raw, _stage_cast())[0])
    raw2 = raw.replace("tracks to her right side", "arcs to her right side")
    p2, rep2 = br.finalize_writer_prompt(raw2, _stage_cast())
    assert "arcs to her right side" in p2 and not any(f["code"] == "K1" for f in rep2["flags"])


def test_dynsafe_skin_still_glossy_is_a_fact_not_a_flag():
    raw = STAGE_HDR + "At first she kneels gripping the ropes exactly as <Picture 1> shows. Her glossy skin glistens on her shoulders. He thrusts deep."
    _, rep = br.finalize_writer_prompt(raw, _stage_cast("doggy", read=KNEEL_READ), strict=False)
    assert not [f for f in rep["skin_unrequested"] if f["kind"] == "gloss"]


def test_dynsafe_blowjob_standing_man_kept_no_lie_back_no_forced_undress():
    raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows, one hand on the chrome. "
           "<Subject 2> stands with feet planted on the stage floor. She sinks down: both knees press into the stage floor. "
           "She takes him into her mouth and sucks slowly, her lips sliding down his shaft.")
    c = _stage_cast("blowjob", BJ_ASK)
    p, rep = br.finalize_writer_prompt(raw, c)
    d = desc_of(p)
    assert "lies back" not in p and "takes off" not in d.lower()
    assert "stay on her body" in d and "black mesh strappy bra top" in d
    assert "fully_preserved - they stay on her body" in p and "partially_preserved - their removal" not in p
    assert "The clip opens on <Picture 1>" not in d and rep["act_written"]
    assert "takes off her clothes" not in p.split("summary:")[1].split("retention_analysis")[0]


def test_dynsafe_bridge_only_when_writer_has_no_move_and_follows_man_pose():
    c = _stage_cast("blowjob", BJ_ASK)
    raw = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She sucks him slowly, her lips sliding down his shaft."
    d = desc_of(br.finalize_writer_prompt(raw, c)[0])
    assert "(S2) stands in front of her, and she sinks to her knees on the stage floor in front of him" in d
    raw_lying = raw.replace("She sucks him", "<Subject 2> lies on his back on the stage floor. She sucks him")
    assert "<Subject 2> lies back on the stage floor, and she kneels between his spread thighs" in br.transition_beat(c, raw_lying)
    ck = _stage_cast("blowjob", BJ_ASK, read=KNEEL_READ)
    assert "she stays on her knees" in br.transition_beat(ck, "")


def test_dynsafe_kneeling_opener_kept_and_opener_pose_lint():
    c = _stage_cast("doggy", read=KNEEL_READ)
    raw = (STAGE_HDR + "At first, <Subject 1> lowers her arms and releases the black ropes. She leans forward onto her hands and knees "
           "on the parquet floor. He kneels behind her and thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, c)
    d = desc_of(p)
    assert "At first, (S1) lowers her arms and releases the black ropes." in d and "The clip opens on" not in d
    assert any("builder opener skipped" in a for a in rep["added"])
    bad = raw.replace("At first, <Subject 1> lowers her arms and releases the black ropes.",
                      "At first she stands exactly as <Picture 1> shows.")
    issues, _ = br.lint_writer_prompt(bad, c)
    assert any(i["code"] == "O1" and "kneels on the parquet floor" in i["why"] for i in issues)


def test_dynsafe_writer_removal_named_once_and_exposure_lint():
    c = _stage_cast()
    raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She takes off the black mesh halter top and "
           "the mesh thong bottom with its garter straps, and they drop to the stage floor. She lowers onto her back on the stage floor. "
           "He enters her and thrusts deep.")
    with pytest.raises(br.WriterPromptError, match="packed beats"):  # brief item 2: undress + act in one short clip
        br.finalize_writer_prompt(raw, c)
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert rep["packed_beats"]["split"][0].startswith("beat 1: she undresses") and "beat 2" in rep["packed_beats"]["split"][1]
    d = desc_of(p)
    assert "She takes off the black mesh halter top" in d  # the writer's removal is kept (no W1 / W4)
    assert ("The black mesh strappy bra top and black mesh strappy bottom with garter straps she took off stay on the stage floor"
            in d)  # brief item 4 + the writer's 'halter top' maps to the still's top slot (never kept on)
    assert not [v for v in rep["violations"] if v["code"] in ("W1", "W4")]
    assert "black fishnet thigh-high stockings stay on her body" in d
    kept_on = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the stage floor. He enters her and thrusts deep."
    issues, _ = br.lint_writer_prompt(kept_on, c)
    assert any(i["code"] == "W5" and "garter straps" in i["why"] for i in issues)


def test_dynsafe_opener_list_swaps_only_the_noun_phrase():
    c = _stage_cast()
    raw = (STAGE_HDR + "At first she stands beside the pole in a black mesh strappy bra, and thigh-high sheer black stockings exactly as "
           "<Picture 1> shows. She lowers onto her back on the stage floor. He thrusts deep.")
    d = desc_of(br.finalize_writer_prompt(raw, c)[0])
    assert ("in a black mesh strappy bra top, a black mesh strappy bottom with garter straps and black fishnet thigh-high stockings "
            "exactly as") in d and ", and" not in d.split("exactly as")[0].split("pole")[1]


def test_dynsafe_act_false_minor_and_unfixed_conflict_are_not_ready():
    g0 = {"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}
    tame = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She smiles at him."
    # Passthrough default does NOT block on act:false; strict=True still raises it
    _, _, tame_rep = br.build_writer_request(g0, tame, _stage_cast(), prefix="x")
    assert tame_rep["passthrough"] is True
    with pytest.raises(br.WriterNotReady, match="act:false"):
        br.build_writer_request(g0, tame, _stage_cast(), prefix="x", strict=True)
    minor = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back. He thrusts deep. (S1) says, <d>[English] Not a child.</d>"
    with pytest.raises(br.WriterNotReady, match="minor"):
        br.build_writer_request(g0, minor, _stage_cast(), prefix="x")
    with pytest.raises(br.WriterPromptError, match="minor descriptor"):
        br.finalize_writer_prompt(minor, _stage_cast())
    bed = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the mattress. He thrusts deep."
    with pytest.raises(br.WriterNotReady, match="unfixed after 2 writer-repair rounds"):
        br.build_writer_request(g0, bed, _stage_cast(), prefix="x", strict=True, writer=lambda m: "nothing useful")


# --- dynsafe production hook: submit_parody_run.submit_writer_run (dry run only; nothing is queued) ------------------
def _oc_graph(mods=("minimaxh3_oc_poolblonde_v2_refmod_visual", "minimaxh3_adamjensen_v1_refmod")):
    inputs = {f"mod_{i}": "(none)" for i in range(1, 9)}
    for i, m in enumerate(mods, 1):
        inputs[f"mod_{i}"] = m
    return {"c0": {"inputs": {"prompt": "", "length": 243, "width": 768, "height": 1344}}, "noise": {"inputs": {"noise_seed": 0}},
            "save": {"inputs": {"filename_prefix": ""}}, "refmods": {"inputs": inputs}, "img_1": {"inputs": {"image": "old.png"}}}


GOOD = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the stage floor, "
        "and he kneels between her thighs. He enters her and thrusts deep, hips flush against her on every stroke.")


# frs16 S2: GOOD keeps the strappy bottom on at penetration (W5, NOT_READY now); GOOD_ASIDE pulls it aside first
GOOD_ASIDE = GOOD.replace("He enters her", "She pulls her thong aside, and he enters her")










def test_dynsafe_end_framing_forms_do_not_raise_k4():
    cast = br.make_cast(BED_READ, "missionary", "she has sex with him, position: missionary")
    br._set_ctx(cast)
    for cam in ("[Shot 1] The camera pushes in with small amplitude at slow speed, tightening from a waist-up two-shot to a close three-quarter angle.",
                "[Shot 1] The camera arcs to her right side with small amplitude at slow speed, settling into a low, hip-height three-quarter rear view.",
                "[Shot 1] The camera arcs right with small amplitude at slow speed, arriving at a low side two-shot at knee height."):
        assert br._END_FRAME_RE.search(cam), cam
    assert not br._END_FRAME_RE.search("[Shot 1] The camera pushes in with small amplitude at slow speed.")


# --- dynsafe brief (Derrick via Prompt maker, 2026-11-11): continuation closer, packed beats, faces, garment surface ----
def test_brief1_continuation_inherits_closing_pose_and_wardrobe_no_standing_default():
    beat1 = {"scene": "She steps out of the red dress and lets it fall onto the sofa. She kneels on the rug facing him."}
    closer = br.beat_closer(beat1, "she")
    assert closer["pose"] == "she kneels on the rug facing him"
    assert closer["wardrobe"] == "she steps out of the red dress and lets it fall onto the sofa"
    s = br.continuation_scene("She leans in.", "she", closer=closer)
    assert "the same standing pose" not in s and "(she kneels on the rug facing him)" in s
    assert "wardrobe as it was left (she steps out of the red dress" in s
    bare = br.continuation_scene("She leans in.", "she")
    assert "standing" not in bare and "the same pose the previous beat ended on" in bare
    assert br.beat_closer({"scene": "x", "end_action": "lies on her side on the bed"}, "she")["pose"] == "she lies on her side on the bed"


def test_brief2_packed_beats_split_or_send_back_never_template_filled():
    c = _stage_cast(ask="she takes off her lingerie and has sex with him, position: missionary")
    raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the "
           "stage floor. He enters her and thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert rep["state"]["builder_removed"] == [] and "She takes off the" not in desc_of(p)  # no compressed template undress
    assert c["undress"] and rep["packed_beats"]["split"][1].startswith("beat 2 (continuation")  # the ask packs two beats
    with pytest.raises(br.WriterPromptError, match="packed beats"):
        br.finalize_writer_prompt(raw, c)
    aside = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She lowers onto her back on the "
             "stage floor and pulls the strappy bottom aside. He enters her and thrusts deep.")
    _, rep2 = br.finalize_writer_prompt(aside, _stage_cast(), strict=False)
    assert "packed_beats" not in rep2  # a pull-aside is not a second beat
    solo = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She takes off the black mesh strappy "
            "bra top and drops it on the stage floor.")
    _, rep3 = br.finalize_writer_prompt(solo, _stage_cast(), strict=False)
    assert "packed_beats" not in rep3  # undress alone is one beat


def test_brief3_face_crop_and_focus_flagged_not_rewritten():
    for move, code in (("pushes in with small amplitude at slow speed to a close-up of the join", "K5"),
                       ("holds a static medium shot as focus racks to his hands", "K6"),
                       ("holds a static medium shot from the neck down", "K7")):
        raw = STAGE_HDR.replace("holds a static medium shot at hip height, keeping her face in frame", move) + \
            "She lowers onto her back on the stage floor. He thrusts deep."
        p, rep = br.finalize_writer_prompt(raw, _stage_cast(), strict=False)
        assert any(f["code"] == code for f in rep["flags"]), (code, rep["flags"])
        assert move.split(" with")[0].split(" as")[0].split(" from")[0] in p  # kept as written, not forced to a close-up
    p, rep = br.finalize_writer_prompt(STAGE_HDR + "She lowers onto her back on the stage floor. He thrusts deep.", _stage_cast(), strict=False)
    assert not any(f["code"] in ("K5", "K6", "K7") for f in rep["flags"]) and "close-up" not in desc_of(p).split(". ")[0]


def test_brief4_removed_garment_needs_a_named_surface_w6():
    c = _stage_cast()
    no_place = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She takes off the black mesh "
                "strappy bra top.")
    assert any(i["code"] == "W6" for i in br.lint_writer_prompt(no_place, c)[0])
    placed = no_place.replace("bra top.", "bra top and drops it on the stage floor.")
    assert not any(i["code"] == "W6" for i in br.lint_writer_prompt(placed, c)[0])
    _, rep = br.finalize_writer_prompt(no_place, c, strict=False)
    assert f"she took off stays on {c['garments_floor']}" in br.wardrobe_line(c, rep["state"])




# --- oralfoley (Derrick via Prompt maker, 2026-11-11: "Yes send all revised riles"): flags / NOT_READY only --------------
BJ_HDR = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. "


def test_oral_s1_line_on_the_oral_beat_is_not_ready_and_never_deleted():
    c = _stage_cast("blowjob", BJ_ASK)
    raw = BJ_HDR + ("She takes him into her mouth and sucks slowly, her lips sliding down his shaft. "
                    "(S1) says in a voice: <d>[English] Mm, you taste so good.</d> Wet suction sounds as her lips slide.")
    with pytest.raises(br.WriterPromptError, match="D1"):
        br.finalize_writer_prompt(raw, c)
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert "you taste so good" in p  # flagged, not silently deleted
    assert any(i["code"] == "D1" for i in br.lint_writer_prompt(raw, c)[0])  # sent back to the writer
    # Passthrough default logs warning without blocking; strict=True raises D1
    _, _, rep_pass = br.build_writer_request({"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}, raw, c, prefix="x")
    assert rep_pass["passthrough"] is True
    with pytest.raises(br.WriterPromptError, match="D1"):
        br.build_writer_request({"c0": {"inputs": {}}, "noise": {"inputs": {}}, "save": {"inputs": {}}}, raw, c, prefix="x", strict=True)


def test_oral_s2_may_speak_and_her_line_after_she_pulls_off_is_allowed():
    c = _stage_cast("blowjob", BJ_ASK)
    raw = BJ_HDR + ("She takes him into her mouth and sucks slowly, her lips sliding down his shaft, a wet gag on the deep stroke "
                    "and breath hissing through her nose. (S2) says in a voice: <d>[English] Choke on it. I want to hear you gag.</d> "
                    "She pulls her mouth off him with a string of spit. (S1) says in a voice: <d>[English] Fuck my throat again.</d>")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert not [x for x in rep["audio_checks"] if x["code"] in ("D1", "D2")]
    assert "Choke on it. I want to hear you gag." in p and "Fuck my throat again." in p


def test_moans_in_d_and_no_speech_words_are_not_ready():
    c = _stage_cast()
    raw = STAGE_HDR + ("She lowers onto her back on the stage floor. He thrusts deep. (S1) says in a voice: <d>[English] Mmmh, ahh.</d>")
    _, rep1 = br.finalize_writer_prompt(raw, c)  # Render cleanup step 4 (Max Architect 3, 2026-11-13, Derrick t1355): style lint is a warning, not a stop
    assert any(w.startswith("D2") for w in rep1["warnings"])
    raw2 = STAGE_HDR + "She lowers onto her back on the stage floor. He thrusts deep, no speech, the stage floor creaks."
    p2, rep2 = br.finalize_writer_prompt(raw2, c, strict=False)
    assert "no speech" not in p2.lower() and any(f["code"] == "D3" for f in rep2["flags"])
    assert any(x["code"] == "D3" and x["hard"] for x in br.audio_act_checks(["He thrusts deep, no speech."], c, True))


def test_oc_stock_dirty_talk_pair_is_not_ready_but_not_on_a_real_person_path():
    stock = HDR + ("He thrusts deep. (S1) says in a voice: <d>[English] Fuck me harder.</d> "
                   "(S2) says in a voice: <d>[English] Take it. Don't you stop.</d> Her thighs shake.")
    with pytest.raises(br.WriterPromptError, match="D4 stock dirty-talk"):
        br.finalize_writer_prompt(stock, _cast())
    _, rep = br.finalize_writer_prompt(stock, _cast(), strict=False)
    assert "Fuck me harder." in _ and "Take it. Don't you stop." in _  # never rewritten
    _, rp = br.finalize_writer_prompt(stock, _cast(index_voice=True), strict=False)
    assert not [x for x in rp["audio_checks"] if x["code"] == "D4"]  # rule 3 is OC / Cond only
    fresh = stock.replace("Fuck me harder.", "Fuck that cunt, I want your cock in my guts.").replace(
        "Take it. Don't you stop.", "Open wider, I'm splitting you in half.")
    _, rf = br.finalize_writer_prompt(fresh, _cast(), strict=False)
    assert not [x for x in rf["audio_checks"] if x["code"] == "D4"]
    assert not [x for x in br.audio_act_checks(["(S2) says, <d>[English] Good girl, daddy is close.</d>"], _cast(), True)
                if x["code"] == "D4"]  # 'daddy' / 'good girl' alone are not banned


def test_silent_explicit_clip_flagged_and_not_ready_when_talk_was_asked():
    c = _stage_cast()
    raw = STAGE_HDR + "She lowers onto her back on the stage floor. He thrusts deep."
    _, rep = br.finalize_writer_prompt(raw, c, strict=False)
    a1 = [x for x in rep["audio_checks"] if x["code"] == "A1"]
    assert a1 and not a1[0]["hard"] and any(f["code"] == "A1" for f in rep["flags"])
    c2 = _stage_cast(ask="she has sex with him and talks dirty, position: missionary")
    with pytest.raises(br.WriterPromptError, match="A1"):
        br.finalize_writer_prompt(raw, c2)


COW_ASK = "she rides him, position: cowgirl"
COW_HDR = ("detailed_description:\n[Shot 1] The camera holds a static medium shot at hip height, keeping her face and his face in "
           "frame. At first she stands barefoot on the wood floor in front of the bed exactly as <Picture 1> shows. "
           "<Subject 2> lies back on the bed, and she straddles his hips. ")


def test_cowgirl_only_her_motion_is_not_ready_and_builder_writes_no_thrust():
    c = br.make_cast(BED_READ, "cowgirl", COW_ASK)
    assert c["primary_motion"] == "" and "blowjob" not in c["summary_act"]
    raw = COW_HDR + ("PRIMARY MOTION - she rises and sinks on his cock about once per second, full depth. "
                     "Her moans break on each drop and the bed creaks.")
    with pytest.raises(br.WriterPromptError, match="R1 cowgirl"):
        br.finalize_writer_prompt(raw, c)
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    d = desc_of(p)
    assert "his pelvis" not in d and "his hips lift" not in d  # the builder never inserts his thrust
    assert any(i["code"] == "R1" for i in br.lint_writer_prompt(raw, c)[0])


def test_cowgirl_with_her_rise_sink_and_his_measured_lift_passes_the_gate():
    c = br.make_cast(BED_READ, "cowgirl", COW_ASK)
    raw = COW_HDR + ("PRIMARY MOTION - she rises until only the tip stays inside her and sinks back down hard, about once per second, "
                     "while his pelvis lifts a few inches off the mattress to meet each descent. "
                     "Wet slaps and her ragged moans fill the room, and the bed creaks under them.")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert not [x for x in rep["audio_checks"] if x["code"] == "R1"]
    assert "his pelvis lifts a few inches off the mattress to meet each descent" in p
    assert not [i for i in br.lint_writer_prompt(raw, c)[0] if i["code"] == "R1"]


def test_soundscape_and_music_headers_flagged_sound_text_kept_verbatim():
    c = _stage_cast()
    raw = (STAGE_HDR + "She lowers onto her back on the stage floor. He thrusts deep.\n\n"
           "overall_soundscape: Wet impacts land on every stroke and her moans break against the stage floor.\n\n"
           "non_diegetic_music: A slow synth score swells under the scene.")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    codes = [f["code"] for f in rep["flags"]]
    assert "S6" in codes and "M6" in codes
    assert "Wet impacts land on every stroke and her moans break against the stage floor." in p  # not rewritten
    assert "overall_soundscape:" in p and "non_diegetic_music:" in p  # U52: headers not silently stripped
    assert any("! WARNING" in w and "overall_soundscape" in w for w in rep["warnings"])
    assert any("! WARNING" in w and "non_diegetic_music" in w for w in rep["warnings"])
    raw2 = STAGE_HDR + "She lowers onto her back on the stage floor. He thrusts deep while music plays loud. Her moans rise."
    _, rep2 = br.finalize_writer_prompt(raw2, c, strict=False)
    assert any(f["code"] == "M7" for f in rep2["flags"])


# --- frs16 (Fleet Reviewer should-fixes S1-S6, Derrick t931u "Yes fix", 2026-11-11) ---------------------------------------
F02_UNDRESS = ("She takes off the black mesh halter top and the mesh thong bottom with its garter straps, unhooking the clasps, "
               "pulling them down, and they fall to the stage floor beside the pole base and stay there; the thigh-high fishnet "
               "stockings with their wide solid bands stay on her legs; <Subject 2> pulls off his t-shirt and jeans, and they drop "
               "to the floor beside the top and stay there.")


def test_frs16_s1_his_garment_is_never_her_absent_garment():
    c = _stage_cast("doggy", "she has sex with him, position: doggy")
    br._ABSENT_GARMENT_RE = re.compile(c["absent_garments"], re.I)
    assert br._ABSENT_GARMENT_RE.search("his t-shirt and jeans")  # 'jeans' is on the absent list for this still
    for his in ("<Subject 2> pulls off his t-shirt and jeans", "she tugs off his shirt, belt and jeans", "<Subject 2>'s jeans drop"):
        assert not br._ABSENT_GARMENT_RE.search(br._hers_text(his)), his
    for hers in ("she peels off her jeans", "he slides her dress off", "she steps out of the dress"):
        assert br._ABSENT_GARMENT_RE.search(br._hers_text(hers)), hers
    _, _, viol = br.track_state([F02_UNDRESS], c, repair=False)
    assert not any(v["code"] == "W4" for v in viol)
    g02 = "<Subject 2> steps in from the left, pulling off his shirt and jeans, and drops them on the floor beside the dress, where they stay."
    assert br._drop_clauses(g02, br._ABSENT_GARMENT_RE) == "<Subject 2> steps in from the left."  # no 'where they stay' orphan


def test_frs16_s1_f02_undress_sentence_kept_and_split_not_ready():
    c = _stage_cast("doggy", "she has sex with him, position: doggy")
    raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. " + F02_UNDRESS +
           " She kneels on the stage floor on hands and knees. He enters her from behind and thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert not any("does not have" in x for x in rep["stripped"]), rep["stripped"]  # no whole-sentence W4 drop
    # t1109u: the builder keeps writer-named partner clothes (t-shirt and jeans) as the single canonical line.
    assert "She takes off the" in desc_of(p)
    assert "pulls off his t-shirt and jeans" in desc_of(p)
    assert desc_of(p).count("t-shirt and jeans") == 1
    assert rep["state"]["garments"]["panties"] == "off" and rep["state"]["garments"]["stockings"] == "on"
    assert set(rep["state"]["writer_removed"]) >= {"bra", "panties"}
    assert rep.get("packed_beats")  # the kept undress + the act is two beats -> NOT_READY + split, never READY with lingerie on
    with pytest.raises(br.WriterPromptError, match="packed beats"):
        br.finalize_writer_prompt(raw, c)


def test_frs16_s1_her_absent_garment_drops_only_that_clause():
    c = _stage_cast()
    raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She takes off the black mesh strappy "
           "bra top and drops it on the stage floor; she peels off the leggings, and they fall to the floor.")
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    d = desc_of(p)
    assert "leggings" not in d and "bra top and drops it on the stage floor" in d
    assert any("absent-garment clause dropped" in x for x in rep["stripped"])
    assert rep["state"]["garments"]["bra"] == "off"
    only = STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. She peels off the leggings."
    _, rep2 = br.finalize_writer_prompt(only, c, strict=False)
    assert any("does not have" in x for x in rep2["stripped"])  # no still garment in it: the whole sentence goes (as before)


def test_frs16_s2_w5_runs_on_the_finalized_state_and_blocks():
    c = _stage_cast()
    _, rep = br.finalize_writer_prompt(GOOD, c, strict=False)
    assert rep["w5_final"]["covered"] == ["black mesh strappy bottom with garter straps"]
    with pytest.raises(br.WriterPromptError, match="W5 .*finalized state"):
        br.finalize_writer_prompt(GOOD, c)
    _, rep2 = br.finalize_writer_prompt(GOOD_ASIDE, c, strict=False)
    assert "w5_final" not in rep2 and not rep2.get("not_ready")
    assert br._JOIN_PEN_RE.search("he enters her") and not br._JOIN_PEN_RE.search("<Subject 2> enters at frame right")
    assert not br._JOIN_PEN_RE.search("his cock slides into her mouth")


def test_w5_credits_slides_aside_and_to_one_side():
    """Derrick t1132u/t1134u: credit clear pull-aside wording; do not loosen W5; pull-aside is not undress."""
    c = _stage_cast()
    assert c.get("undress") is False
    for s, want in (
        ("and she slides the gusset of her sheer white thong bikini aside", True),
        ("She pulls the sheer white thong bikini bottom to one side, exposing the join", True),
        ("She pulls her thong aside, and he enters her", True),
        ("He enters her and thrusts deep", False),
    ):
        assert bool(br._REMOVE_VERB_RE.search(s)) is want and bool(br._ASIDE_RE.search(s)) is want, s
    _, blocked = br.finalize_writer_prompt(GOOD, c, strict=False)
    assert blocked.get("w5_final")
    with pytest.raises(br.WriterPromptError, match="W5 .*finalized state"):
        br.finalize_writer_prompt(GOOD, c)
    # Matching still wardrobe (the bakeoff case): no still-facts leftover noun to strip.
    thong_read = dict(POLE_READ, garments=[
        {"type": "bikini top", "name": "sheer white stretched top"},
        {"type": "bikini bottoms", "name": "sheer white thong bikini"},
        {"type": "shoes", "name": "white leather cowboy boots"},
    ])
    thong_cast = _stage_cast(read=thong_read)
    for line in (
        "She slides the gusset of her sheer white thong bikini aside. He enters her and thrusts deep.",
        "She pulls the sheer white thong bikini bottom to one side, exposing the join. He enters her and thrusts deep.",
    ):
        raw = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. "
               "She lowers onto her back on the stage floor. " + line)
        _, rep = br.finalize_writer_prompt(raw, thong_cast, strict=False)
        assert "w5_final" not in rep and "packed_beats" not in rep, (line, rep.get("not_ready"), rep.get("w5_final"), rep.get("stripped"))
        assert "panties" in (rep["state"].get("writer_aside") or []), (line, rep["state"])
        assert not (rep.get("not_ready") or ""), (line, rep.get("not_ready"))
    # Same matcher on the existing stage inventory, using that still's own bottoms name.
    stage_line = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. "
                  "She lowers onto her back on the stage floor and pulls the strappy bottom to one side. "
                  "He enters her and thrusts deep.")
    _, rep2 = br.finalize_writer_prompt(stage_line, c, strict=False)
    assert "w5_final" not in rep2 and "packed_beats" not in rep2 and "panties" in (rep2["state"].get("writer_aside") or [])










def test_frs16_s5_callable_writer_still_gets_exactly_one_retry():
    calls = []
    raw, log = br.gated_write(lambda: calls.append(1) or (F01_REFUSAL, 158), cast=_stage_cast(), ask=ASK)
    assert raw is None and len(calls) == 2 and len(log["attempts"]) == 2




# --- argon-low Section B (2026-11-11): packed undress-plus-act with complete safe split -> ONE 2-beat continuation -------


def test_argonlow_undress_beat_sizing_and_nude_still_no_undress_beat():
    assert br.size_undress_beat_frames(garment_count=0, nude_still=True) == 0
    assert br.size_undress_beat_frames(garment_count=1, lying_down=False) == 124
    assert br.size_undress_beat_frames(garment_count=2, lying_down=False) == 192
    assert br.size_undress_beat_frames(garment_count=1, lying_down=True) == 192
    assert br.size_undress_beat_frames(garment_count=3, lying_down=False) == 243
    nude_read = dict(POLE_READ, garments=[])
    c_nude = br.make_cast(nude_read, "missionary", "she has sex with him, position: missionary")
    assert br.size_undress_beat_frames(c_nude) == 0
    raw_nude = (STAGE_HDR + "At first she stands beside the pole exactly as <Picture 1> shows. "
                "She lowers onto her back on the stage floor. He enters her and thrusts deep. Her moans rise.")
    _, rep = br.finalize_writer_prompt(raw_nude, c_nude, strict=False)
    assert "packed_beats" not in rep


# --- Step 1 misfire tests (2026-11-11 modular plan, no graph change) ---------------------------------
def test_step1_unknown_act_raises_not_ready_never_blowjob():
    with pytest.raises(br.WriterNotReady, match="NOT_READY: unknown act 'unlisted_act'"):
        br.make_cast(BED_READ, "unlisted_act", "an unlisted act")
    with pytest.raises(br.WriterNotReady, match="NOT_READY: unknown act 'unknown_position'"):
        br.make_cast(BED_READ, "unknown_position", "an unknown position")


def test_step1_no_man_penis_contact_line_or_sex_template_unless_partner_is_man_and_act_known():
    # partner_type = none (female solo)
    c_solo = br.make_cast(BED_READ, "missionary", "she relaxes on the bed", partner_type="none")
    assert c_solo["man"] == ""
    assert c_solo["contact"] == ""
    assert c_solo["his_clothes"] == ""
    assert "keeping her face in frame" in c_solo["camera_tail"]
    raw_solo = (STAGE_HDR + "At first she stands beside the bed exactly as <Picture 1> shows. "
                "She sits on the bed and touches her cheek. She sighs softly.")
    p_solo, rep_solo = br.finalize_writer_prompt(raw_solo, c_solo, strict=False)
    assert "<Subject 2>" not in p_solo and "(S2)" not in p_solo
    assert "His penis" not in p_solo
    assert "his face and the join" not in p_solo

    # partner_type = woman (F+F)
    c_fem = br.make_cast(BED_READ, "missionary", "she is with her partner", partner_type="woman")
    assert c_fem["contact"] == ""
    assert c_fem["his_clothes"] == ""


def test_step1_no_sex_is_not_a_sex_ask():
    assert not br.is_act_ask("A quiet conversation in the bedroom, no sex")
    assert not br.is_act_ask("talking on the sofa, without sex")
    assert not br.is_act_ask("non-sexual cuddling")
    assert br.is_act_ask("she has sex with him, missionary position")
    # writer_gate should not flag act:false when the ask says "no sex"
    raw_talk = (STAGE_HDR + "At first she stands beside the bed exactly as <Picture 1> shows. "
                "She sits on the bed. She says 'Let us talk about tomorrow.'")
    reasons = br.writer_gate(raw_talk, cast=CAST, ask="A quiet conversation in the bedroom, no sex")
    assert not any("act:false" in r for r in reasons)


def test_step1_taking_off_jacket_is_not_full_undress_and_striped_is_not_undress():
    assert not br._UNDRESS_ASK_RE.search("she wears a striped shirt")
    assert not br._UNDRESS_ASK_RE.search("she wears a striped bra")
    assert not br._UNDRESS_ASK_RE.search("takes off her jacket")
    c_striped = br.make_cast(BED_READ, "missionary", "She wears a striped dress and has sex")
    assert c_striped["undress"] is False
    # Draft where she removes a jacket does not trigger packed_beats
    jacket_read = dict(BED_READ, garments=[
        {"type": "jacket", "name": "silk jacket"},
        {"type": "bra", "name": "black bra"},
        {"type": "panties", "name": "black panties"},
    ])
    c_jacket = br.make_cast(jacket_read, "missionary", "she takes off her jacket and has sex")
    assert c_jacket["undress"] is False
    raw_jacket = (STAGE_HDR + "At first she stands beside the bed exactly as <Picture 1> shows. "
                  "She takes off the silk jacket and drops it on the floor. "
                  "She lowers onto her back on the white sheets. He enters her and thrusts deep.")
    p, rep = br.finalize_writer_prompt(raw_jacket, c_jacket, strict=False)
    assert "packed_beats" not in rep


def test_step1_w4_does_not_drop_partner_garments_or_still_garments():
    c = _stage_cast("doggy", "she has sex with him, position: doggy")
    # Partner's clothes do not trigger W4
    _, _, viol = br.track_state(["<Subject 2> pulls off his shirt and jeans, and they drop to the floor."], c, repair=False)
    assert not any(v[0] == "W4" for v in viol)
    # still_read v2 people[].garments are included in still_facts and not treated as absent
    v2_read = {
        "room": "a modern bedroom",
        "bed": True,
        "people": [
            {"garments": [{"name": "silk robe", "type": "robe"}]},
            {"garments": [{"name": "blue jeans", "type": "pants"}]}
        ]
    }
    f = br.still_facts(v2_read)
    assert any(g["name"] == "silk robe" for g in f["garments"])
    assert any(g["name"] == "blue jeans" for g in f["garments"])
    absent = br.absent_garment_pattern(v2_read)
    assert absent is not None
    assert not re.search(absent, "robe")
    assert not re.search(absent, "jeans")


def test_step1_comm_bad_re_loosened_for_adult_dirty_talk_and_18_plus_preserved():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import comm
    assert comm.guard_ok("good girl, take it")
    assert comm.guard_ok("bad girls get punished")
    assert comm.guard_ok("girl-on-girl scissoring")
    assert comm.guard_ok("old-school motel")
    assert not comm.guard_ok("underage girl")
    assert not comm.guard_ok("minor")
    assert not comm.guard_ok("child")
    assert comm.adult_stated("an adult woman, twenty-two years old")


def test_step1_narrow_policy_re_keeps_story_words_in_narration():
    story_sentences = [
        "She lowers her guard and kneels.",
        "A security guard pins her wrists to the table.",
        "His rule is law.",
        "She gives full consent to his touch.",
        "Two consenting adults hold each other on the bed.",
        "In this science fiction world, neon lights glow.",
        "She prompts him to continue.",
    ]
    for s in story_sentences:
        assert not br._is_policy(s), f"Story sentence should not be policy: {s}"

    meta_sentences = [
        "The prompt maintains strict adherence to the brief.",
        "The 'No timestamp' rule is respected.",
        "No minors, no real-person likeness.",
        "Adults only, 18+.",
        "Complies with h3-prompting rules.",
        "Follows content policy and safety guardrails.",
    ]
    for s in meta_sentences:
        assert br._is_policy(s), f"Meta sentence should be policy: {s}"


# --- Step 2 modules tests (2026-11-11 modular plan) -------------------------------------------------
def test_step2_acts_registry_seeding_and_statuses():
    acts = br.load_acts_registry()
    # Package 2 (R15-R23, 2026-11-12) adds four untested acts; the original 19 stay.
    # Derrick t204u adds talk (tested).
    assert len(acts) == 26
    for tid in ("missionary", "doggy", "cowgirl", "blowjob", "talk"):
        assert acts[tid]["status"] == "tested", f"{tid} must be tested"
    for uid in ("spooning", "prone_bone", "titjob", "finish", "female_solo",
                "ff_cunnilingus", "ff_scissoring", "mf_anal", "bondage", "dance", "tease", "threesome", "mmf", "ffm", "mmf_double_blowjob",
                "male_solo", "standing_mf", "airplane", "piledriver"):
        assert acts[uid]["status"] == "untested", f"{uid} must be untested"
    for oid in ("missionary", "doggy", "cowgirl", "blowjob", "spooning", "prone_bone", "titjob", "finish", "female_solo",
                "ff_cunnilingus", "ff_scissoring", "mf_anal", "bondage", "dance", "tease", "threesome", "mmf", "ffm", "mmf_double_blowjob"):
        assert oid in acts, f"original act {oid} must remain"
    # Aliases
    assert br.get_act("paizuri")["id"] == "titjob"
    assert br.get_act("twerk")["id"] == "dance"
    assert br.get_act("cunnilingus")["id"] == "ff_cunnilingus"
    assert br.get_act("scissoring")["id"] == "ff_scissoring"
    assert br.get_act("oral")["id"] == "blowjob"
    assert br.get_act("reverse cowgirl")["id"] == "reverse_cowgirl"
    # Thin/unpromoted acts must NOT be in registry
    for thin in ("tentacles", "robot", "pegging", "m_m", "transformation"):
        assert br.get_act(thin) is None, f"{thin} should not be seeded in registry"


def test_step2_partner_type_module():
    # woman partner
    c_w = br.make_cast(BED_READ, "ff_cunnilingus", "two adult women together", partner_type="woman")
    assert c_w["partner_type"] == "woman"
    assert c_w["his_clothes"] == ""
    assert c_w["contact"] != ""
    assert "His penis" not in c_w["contact"]
    assert "Her face is between her thighs" in c_w["contact"]

    # none (solo)
    c_s = br.make_cast(BED_READ, "female_solo", "she is alone on the bed")
    assert c_s["partner_type"] == "none"
    assert c_s["man"] == ""
    assert c_s["his_clothes"] == ""
    assert c_s["contact"] == ""

    # faceless partner
    c_face = br.make_cast(BED_READ, "missionary", "she has sex with partner", partner_type="faceless")
    assert c_face["partner_type"] == "faceless"
    assert c_face["his_clothes"] == ""
    assert c_face["contact"] == ""


def test_step2_role_free_text_pass_through():
    roles = [
        "brother and sister, both 21+",
        "father and adult daughter, 22yo",
        "uncle and adult niece, 25 yo",
        "cousins, adults 20+",
        "boss and employee, adults 24+",
        "cheating wife and lover, all adults",
        "captor and captured heroine, CNC power dynamic, consenting adults",
        "master and slave, BDSM adult roleplay",
        "video game heroine cosplay in fantasy setting, adult character",
    ]
    for r in roles:
        c = br.make_cast(BED_READ, "missionary", "adult roleplay", role=r)
        assert c["role"] == r, f"Role must pass through unchanged: {r}"


def test_step2_beat_kind_module():
    # dance beat does not inject sex contact line even with bounce / grind words
    c_dance = br.make_cast(BED_READ, "dance", "she dances in the room")
    assert c_dance["beat_kind"] == "dance"
    raw_dance = (STAGE_HDR + "At first she stands beside the bed exactly as <Picture 1> shows. "
                 "She sways her hips and bounces in rhythm. She grinds to the beat.")
    p, rep = br.finalize_writer_prompt(raw_dance, c_dance, strict=False)
    assert rep["act_written"] is False
    assert "PRIMARY MOTION - continuous deep" not in p
    assert "penis" not in p


def test_step2_camera_kind_module():
    # POV camera
    c_pov = br.make_cast(BED_READ, "missionary", "POV missionary", camera_kind="POV")
    assert c_pov["camera_kind"] == "POV"
    assert "partner POV" in c_pov["camera_tail"]
    raw_pov = (STAGE_HDR + "[Shot 1] The camera holds a static shot. "
               "She lowers onto her back on the white sheets. He kneels between her thighs and thrusts.")
    p, _ = br.finalize_writer_prompt(raw_pov, c_pov, strict=False)
    assert "his face" not in p.split("detailed_description:")[1].split(".")[0]

    # close-up camera
    c_cu = br.make_cast(BED_READ, "titjob", "close-up titjob", camera_kind="close-up")
    assert c_cu["camera_kind"] == "close-up"
    assert "close-up" in c_cu["camera_tail"]


def test_step2_still_read_v2_schema_and_people_count_mismatch():
    v2_read = {
        "room": "an executive hotel suite",
        "bed": True,
        "surface": "the king bed",
        "people": [
            {"hair": "blonde", "build": "athletic", "position": "stands beside the bed",
             "garments": [{"name": "silk nightie", "type": "dress"}]},
            {"hair": "dark", "build": "muscular", "position": "sits on the edge of the bed",
             "garments": [{"name": "dress shirt", "type": "top"}]}
        ],
        "props": ["champagne glass", "briefcase"],
        "restraints": ["velvet cuffs"],
        "toys": ["feather tickler"]
    }
    f = br.still_facts(v2_read)
    assert len(f["people"]) == 2
    assert "champagne glass" in f["props"]
    assert "velvet cuffs" in f["restraints"]
    assert "feather tickler" in f["toys"]

    # People-count mismatch: solo ask on a 2-person still
    with pytest.raises(br.WriterNotReady, match="people-count mismatch"):
        br.make_cast(v2_read, "female_solo", "she is alone on the bed")

    # People-count mismatch: 3 people on a 2-body act
    v2_3p = dict(v2_read, people=v2_read["people"] + [{"hair": "red", "build": "slim", "position": "stands by window", "garments": []}])
    with pytest.raises(br.WriterNotReady, match="people-count mismatch"):
        br.make_cast(v2_3p, "missionary", "they have sex")




# --- t105u–t110u addendum tests (2026-11-11 modular builder upgrade) -------------------------------






def test_t105u_settings_roles_races_pass_through_no_new_modules():
    # Settings: office, shower
    still_office = dict(BED_READ, room="an executive office with a desk", surface="the office desk", bed=False, sheets="")
    c_off = br.make_cast(still_office, "missionary", "she has sex on the office desk with her boss")
    assert c_off["surface"] == "the office desk"

    still_shower = dict(BED_READ, room="a luxury glass shower", surface="the shower floor", bed=False, sheets="")
    c_shw = br.make_cast(still_shower, "doggy", "she has sex in the shower")
    assert c_shw["surface"] == "the shower floor"

    # Roles: adult teacher, maid
    c_teach = br.make_cast(BED_READ, "missionary", "adult teacher roleplay, 24yo", role="adult teacher")
    assert c_teach["role"] == "adult teacher"

    c_maid = br.make_cast(BED_READ, "doggy", "maid in uniform roleplay, adults", role="maid")
    assert c_maid["role"] == "maid"

    # Fantasy races, aliens, tiny elves, little-person partners
    c_elf = br.make_cast(BED_READ, "missionary", "elf fantasy roleplay in enchanted forest, consenting adults")
    assert "elf fantasy" in c_elf["ask"]

    c_alien = br.make_cast(BED_READ, "missionary", "alien sci-fi scene, adult characters")
    assert "alien sci-fi" in c_alien["ask"]

    c_tiny = br.make_cast(BED_READ, "missionary", "tiny-elf adult woman at miniature scale, no taller than his hand")
    assert "tiny-elf" in c_tiny["ask"]

    c_lp = br.make_cast(BED_READ, "missionary", "little-person partner, consenting adults")
    assert "little-person" in c_lp["ask"]

    # Settings/roles/races/fetishes must not become acts. Package 2 added four catalog acts (R15-R23); t204u adds talk.
    acts = br.load_acts_registry()
    assert len(acts) == 26
    for blocked_id in ("office", "shower", "teacher", "maid", "elf", "alien", "tiny_elf",
                       "little_person", "gangbang", "orgy", "foursome", "bukkake"):
        assert blocked_id not in acts


def test_t105u_fetish_fisting_piss_spit_gape_free_text():
    import comm
    for word in ("fisting", "piss", "spit", "gape"):
        # Not blocked on the hook or by guard_ok
        assert comm.guard_ok(word)
        assert not br._is_policy(word)
        c = br.make_cast(BED_READ, "doggy", f"she does {word} on the bed with him")
        assert word in c["ask"]

    # Fetish words stay free text, not new act rows. Registry size includes the four Package 2 acts and talk (t204u).
    acts = br.load_acts_registry()
    assert len(acts) == 26
    for f in ("fisting", "piss", "spit", "gape"):
        assert f not in acts

def test_wrapped_still_read_unwraps_facts_and_inventory():
    """Phone-path still_read.json wraps facts under a top-level 'read' key."""
    wrapped = {
        "read": {
            "room": "a penthouse living room",
            "place": "penthouse",
            "bed": False,
            "surface": "the long oak counter top",
            "floor": "wood floor",
            "light": "city light through windows",
            "pose": "stands at the counter",
            "hair": "long blonde hair",
            "skin": "tanned skin",
            "build": "athletic build",
            "garments": [{"type": "dress", "name": "cream sheer dress"}],
        },
        "how": "vision",
        "source": "still.jpg",
        "source_sha256": "abc",
    }
    f = br.still_facts(wrapped)
    assert f["surface"] == "the long oak counter top"
    assert f["setting"] == "a penthouse living room"
    assert f["pose"] == "stands at the counter"
    assert any(g["name"] == "cream sheer dress" for g in f["garments"])
    inv = br.garment_inventory(wrapped)
    assert inv and inv[0]["name"] == "cream sheer dress"
    c = br.make_cast(wrapped, "missionary", "they have sex, missionary")
    assert c["inventory"] and c["still_pose"] == "stands at the counter"
    assert c["surface"] == "the long oak counter top"
    assert "long blonde hair" in c["woman"]
    # flat reads used by the rest of the suite stay unchanged
    flat = br.still_facts(BED_READ)
    assert flat["surface"] == "the bed" and any(g["name"] == "sheer nude bra" for g in flat["garments"])


def test_finalize_keeps_writer_summary_and_skips_canned_floor_beat():
    wrapped = {
        "read": {
            "room": "an ocean beach at dusk",
            "place": "beach",
            "bed": False,
            "surface": "the wet sand",
            "floor": "wet sand",
            "light": "low sun",
            "pose": "stands with her hands on a driftwood log",
            "garments": [{"type": "swimsuit", "name": "white sheer cut-out swimsuit"}],
        },
        "how": "vision",
        "source": "still.jpg",
        "source_sha256": "abc",
    }
    c = br.make_cast(wrapped, "doggy", "they have sex, doggy")
    raw = (
        "subject_definitions:\n"
        "(S1) Adult woman, 18+. Never age-play.\n"
        "summary:\n"
        "[keyframe completion] She braces standing against the driftwood log and takes him from behind.\n"
        "retention_analysis:\n"
        "The prompt maintains strict adherence to the brief.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a locked medium shot. At first she stands with her hands on a driftwood log "
        "in a white sheer cut-out swimsuit. She stays standing and braces on the log. He steps in behind her "
        "and enters her from behind, and he thrusts deep. (S1) says in a low, soft, breathy voice: "
        "<d>[English] Don't stop.</d> (S2) says in a low, rough male voice: <d>[English] Take it.</d> "
        "The camera keeps the two-shot to the last frame.\n"
    )
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    summary = p.split("summary:\n", 1)[1].split("retention_analysis:", 1)[0]
    assert "hands and knees on the floor" not in summary
    assert "gets on her hands and knees" not in summary
    assert "braces standing against the driftwood log" in summary
    codes = {i["code"] for i in rep.get("flags") or []}
    lint_codes = {i["code"] for i in br.lint_writer_prompt(raw, c)[0]}
    assert "wardrobe_unverified" not in codes and "wardrobe_unverified" not in lint_codes
    assert "pose_unverified" not in codes and "pose_unverified" not in lint_codes
    assert "an ocean beach at dusk" in p
    assert "white sheer cut-out swimsuit" in p or "cut-out swimsuit" in p


def test_finalize_uses_canned_summary_act_when_writer_summary_empty():
    c = dict(CAST)
    raw = (
        "subject_definitions:\n(S1) Adult woman, 18+.\n"
        "summary:\n\n"
        "retention_analysis:\nThe prompt maintains strict adherence to the brief.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a locked medium shot. She stands by the bed in a sheer nude bra, a garter belt, "
        "sheer panties and thigh-high stockings. She lowers onto her back on the white sheets, and he kneels between "
        "her thighs. He thrusts deep. (S1) says in a low, soft, breathy voice: <d>[English] Yes.</d> "
        "The camera keeps the two-shot to the last frame.\n"
    )
    p, _ = br.finalize_writer_prompt(raw, c, strict=False)
    summary = p.split("summary:\n", 1)[1].split("retention_analysis:", 1)[0]
    assert "lies back on the bed and takes <Subject 2> in the missionary position" in summary


def test_leftover_hook_keeps_writer_ages_w5_clause_and_landing():
    """t1221u: keep 24/28, the W5 clause, slide-up (no false take-off), and pool-at-ankles wording."""
    wrapped = {
        "read": {
            "room": "a penthouse living room",
            "place": "penthouse",
            "bed": False,
            "surface": "the long oak counter top",
            "floor": "wood floor",
            "light": "city light through windows",
            "pose": "standing at the long oak kitchen counter",
            "facing_camera": True,
            "people": 1,
            "garments": [{"type": "dress", "name": "cream sheer dress"}],
        },
        "how": "vision",
        "source": "still.jpg",
        "source_sha256": "abc",
    }
    c = br.make_cast(wrapped, "missionary", "she has sex with him, position: missionary")
    assert "who standing" not in c["still"]
    assert "with <Subject 1> standing at the long oak kitchen counter" in c["still"]
    raw = (
        "subject_definitions:\n"
        "<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of "
        "this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; "
        "an adult woman, twenty-four years of age, with natural adult body mass carried in the waist, hips, thighs and breasts; "
        "she is (S1), and <Audio 1> defines her voice timbre.\n"
        "<Subject 2> is an adult man, twenty-eight years of age, of solid adult build; he is (S2).\n"
        "summary:\n"
        "[keyframe completion] She climbs onto the oak counter and takes him in missionary.\n"
        "retention_analysis:\n"
        "The prompt maintains strict adherence to the brief.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a static medium two-shot at hip height with a 50 mm lens, framing her from head to knees "
        "at the long oak counter top and keeping the join and both faces readable throughout.\n"
        "At first, <Subject 1> stands barefoot at the long oak counter top exactly as in <Picture 1>, facing the camera; "
        "the cream sheer dress hangs open at both hips.\n"
        "She hooks both hands into the side ties of the cream sheer dress and slides it up her thighs to her ribs, "
        "where it bunches and stays, so nothing covers her vulva or his penis.\n"
        "<Subject 2> pulls down his trousers and boxers in one motion; they pool at his ankles and stay there.\n"
        "She climbs onto the oak counter. He enters her and thrusts deep. "
        "(S1) says in a low, warm adult woman's voice: <d>[English] Yes.</d>\n"
    )
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    assert "in her twenties" in p
    assert "so nothing covers her vulva or his penis" in p
    assert "she took off" not in p.lower()
    assert "pool at his ankles" in p
    assert "drop to the wood floor" not in p
    assert "dress" not in (rep.get("state") or {}).get("writer_removed", [])
    assert "dress" in (rep.get("state") or {}).get("writer_aside", [])
    assert (rep.get("state") or {}).get("garments", {}).get("dress") == "on"
    assert "w5_final" not in rep
    assert "cream sheer dress of <Picture 1>: partially_preserved" in p
    assert "pulled aside or slid up so the join is clear" in p


def test_leftover_hook_aside_keeps_w5_clause_and_skips_opening_his_face_tail():
    """t1221u: pull-aside is not a take-off; off-still camera does not append 'keeping his face in frame'."""
    wrapped = {
        "read": {
            "room": "an ocean beach at dusk",
            "place": "beach",
            "bed": False,
            "surface": "the wet sand",
            "floor": "wet sand",
            "light": "low sun",
            "pose": "standing on the wet sand",
            "people": 1,
            "garments": [{"type": "swimsuit", "name": "white sheer cut-out swimsuit"}],
        },
        "how": "vision",
        "source": "still.jpg",
        "source_sha256": "abc",
    }
    c = br.make_cast(wrapped, "doggy", "she has sex with him, position: doggy")
    assert "once he enters" in c["camera_tail"]
    raw = (
        "subject_definitions:\n"
        "<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of "
        "this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; "
        "an adult woman, twenty-four years of age, with tanned skin; she is (S1), and <Audio 1> defines her voice timbre.\n"
        "<Subject 2> is an adult man, twenty-eight years of age, of solid adult build; he is (S2).\n"
        "summary:\n"
        "[keyframe completion] She braces standing against the driftwood log and takes him from behind.\n"
        "retention_analysis:\n"
        "The prompt maintains strict adherence to the brief.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a static medium two-shot at hip height from a rear three-quarter angle with a 50 mm lens, "
        "framing her from head to calves so the join and her face stay readable as she looks back over her shoulder; "
        "hard low sun from camera-left rakes along her back and shoulders.\n"
        "At first, <Subject 1> stands barefoot on the wet sand facing the camera exactly as in <Picture 1>.\n"
        "She pulls the white sheer cut-out swimsuit aside at her right hip, where it stays, so nothing covers her vulva or his penis.\n"
        "<Subject 2> pulls down his trousers and boxers in one motion; they pool at his ankles and stay there.\n"
        "She braces on the driftwood. He enters her from behind and thrusts deep. "
        "(S1) says in a low, warm adult woman's voice: <d>[English] Yes.</d>\n"
    )
    p, rep = br.finalize_writer_prompt(raw, c, strict=False)
    desc = p.split("detailed_description:\n", 1)[1]
    cam = desc.split(". ", 1)[0]
    assert "keeping his face in frame" not in cam
    assert "so nothing covers her vulva or his penis" in p
    assert "she took off" not in p.lower()
    assert "swimsuit" not in (rep.get("state") or {}).get("writer_removed", [])
    assert "swimsuit" in (rep.get("state") or {}).get("writer_aside", [])
    assert "w5_final" not in rep
    assert "in her twenties" in p


def test_leftover_hook_rejects_under_18_writer_age():
    raw = (
        "subject_definitions:\n"
        "<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds of "
        "this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; "
        "an adult woman, seventeen years of age, with long blonde hair; she is (S1), and <Audio 1> defines her voice timbre.\n"
        "summary:\n[keyframe completion] She lies back on the bed and takes him in missionary.\n"
        "retention_analysis:\nThe prompt maintains strict adherence to the brief.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a locked medium shot. She stands by the bed in a sheer nude bra, a garter belt, "
        "sheer panties and thigh-high stockings. She lowers onto her back on the white sheets, and he kneels between "
        "her thighs. He thrusts deep. (S1) says in a low, soft, breathy voice: <d>[English] Yes.</d>\n"
    )
    p, _ = br.finalize_writer_prompt(raw, dict(CAST), strict=False)
    assert "seventeen years of age" not in p


def test_xhigh_builder_fixes_male_solo_and_floor_and_camera():
    """Male solo pre-strip, male voice_s1, retention, _resolve_camera his face, no 'the the floor', no <Subject 2>."""
    sr = {
        "read": {
            "room": "high-rise apartment",
            "place": "by a window",
            "surface": "wooden sideboard",
            "bed": False,
            "sheets": "",
            "floor": "the floor",
            "light": "soft evening light from window",
            "framing": "medium shot",
            "pose": "leaning, standing",
            "facing_camera": True,
            "people": 1,
            "garments": [{"type": "dress", "name": "sheer white halter dress"}],
            "build": "curvy",
            "skin": "fair skin",
            "hair": "blonde, damp",
        }
    }
    c = br.make_cast(sr, "male_solo", "male solo edging")
    assert c["inventory"] == [] and c["still_garments"] == ""
    assert "man's voice" in c["voice_s1"].lower() and c["voice_s1"] != br.OC_VOICE_S1
    assert c["camera_tail"] == "keeping his face in frame"
    assert br.writer_named_his_clothes("He pulls his trousers aside to clear his groin.", "the floor", subject="<Subject 1>") == ""
    raw = (
        "subject_definitions:\n"
        "<Picture 1> is the start still of the setting only.\n"
        "<Subject 1> is an adult man, twenty-eight years of age, of solid adult build; he is (S1).\n"
        "summary:\n(S1) edges beside the wooden sideboard.\n"
        "retention_analysis:\n<Picture 1>: fully_preserved.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a medium profile shot at chest height in soft evening light. "
        "At first, (S1) leans beside the wooden sideboard on his feet, by the window. "
        "He pulls his trousers aside to clear his groin. "
        "As it builds, PRIMARY MOTION - he grips his shaft and edges with steady slow strokes at one cycle per second. "
        "(S1) says in a low voice, <d>[English] Too close.</d> "
        "By the end, he holds his grip beside the sideboard, still stroking steadily with a soft gasp.\n"
    )
    p, _ = br.finalize_writer_prompt(raw, c, strict=True)
    low = p.lower()
    assert "the the" not in low
    assert "her face" not in low and "his face" in c["camera_tail"]
    assert "<subject 2>" not in low
    assert "kept from <picture 1>" not in low
    assert "stay as defined in <subject 1>" in low
    assert "twenty-six years of age" in low


def test_xhigh_writer_subject_bios_preserves_species_scale_futa_s3():
    """_writer_subject_bios keeps assemble_output comma+and format, species, scale_anchor, futa S3, without losing orc."""
    raw = (
        "subject_definitions:\n"
        "<Picture 1> is the reference image defining <Subject 1>.\n"
        "<Subject 1> is the exact same woman shown in <Picture 1>; an adult woman, 25 years of age, blonde, damp, messy; she is (S1).\n"
        "<Subject 2> is the orc, an adult, 35 years of age, towering muscular build, in a leather harness, about twice her height, who enters from left and he is (S2).\n"
        "<Subject 3> is the futa, an adult, 28 years of age, tall slim build, in a black corset, with full breasts and a thick penis, matches <Picture 2>, who enters from behind and she is (S3).\n"
    )
    bios = br._writer_subject_bios(raw)
    assert "an adult woman, 25 years of age" in bios.get("woman", "")
    assert "the orc, an adult, 35 years of age" in bios.get("man", "") and "about twice her height" in bios["man"]
    assert "with full breasts and a thick penis" in bios.get("partner3", "") and "matches <Picture 2>" in bios["partner3"]

    # Generic "the man" in writer bio does not overwrite a non-human orc cast["man"].
    sr = {
        "read": {
            "room": "beach", "place": "on a driftwood log", "surface": "log", "bed": False, "floor": "sand",
            "pose": "leaning on the log", "facing_camera": True, "framing": "medium shot", "light": "golden hour",
            "people": 1, "garments": [{"type": "bottom", "name": "sheer mesh bikini bottom"}],
        }
    }
    orc_cast = br.make_cast(sr, "doggy", "orc partner takes her from behind on the log", partner_type="non-human")
    orc_raw = (
        "subject_definitions:\n"
        "<Picture 1> is the reference image.\n"
        "<Subject 2> is the man, an adult, 30 years of age, athletic build, who enters from the right and he is (S2).\n"
        "summary:\nAn orc takes her on the log.\n"
        "retention_analysis:\nkept.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a medium shot at hip height, keeping her face, his face and the join in frame. "
        "At first, (S1) leans on the log, her sheer mesh bikini bottom covering her hips. "
        "She drops onto her hands and knees on the log and pulls the sheer mesh bikini bottom aside to one side at her hip, where it stays. "
        "His penis pushes into her vagina from behind until his hips are flush against her buttocks, and he stays buried in her. "
        "As it builds, PRIMARY MOTION - heavy thrusts at one stroke every second. "
        "(S2) says in a gravelly voice, <d>[English] Hold still.</d> "
        "By the end, he keeps thrusting. Wet skin slaps on the log.\n"
    )
    orc_out, _ = br.finalize_writer_prompt(orc_raw, orc_cast, strict=True)
    assert "orc" in [ln for ln in orc_out.splitlines() if ln.startswith("<Subject 2>")][0].lower()


def test_xhigh_continued_inherited_aside_clears_w5():
    """Continued clip inheriting prior panties='aside' clears W5 without needing a duplicate pull-aside."""
    sr = {
        "read": {
            "room": "beach", "place": "on the wet sand", "surface": "sand", "bed": False, "floor": "wet sand",
            "pose": "kneeling on the sand", "facing_camera": False, "framing": "medium shot", "light": "low sun",
            "people": 1, "garments": [{"type": "top", "name": "sheer mesh crop top"}, {"type": "bottom", "name": "sheer mesh bikini bottom"}],
        }
    }
    c = dict(
        br.make_cast(
            sr, "mmf", "mmf continued", continued=True,
            inherited_garments={"top": "on", "panties": "aside"}, partner_type2="faceless",
        ),
        s3_in_frame=True,
    )
    dd = (
        "subject_definitions:\n<Picture 1> is the reference image.\n"
        "<Subject 2> is the man, an adult, 30 years of age, athletic build, in dark board shorts, who enters from the right and he is (S2).\n"
        "<Subject 3> is the man, an adult, 32 years of age, broad-shouldered build, in dark board shorts, who enters from the left and he is (S3).\n"
        "summary:\nMMF continued.\nretention_analysis:\nkept.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a medium two-shot at hip height, keeping all three faces and the join in frame. "
        "At first, (S1) is on her knees on the sand, leaning back against (S3) while (S2) stands in front of her; "
        "(S2)'s penis is inside her mouth and (S3)'s penis is buried in her vagina from behind, hips flush. "
        "As it builds, PRIMARY MOTION - (S3) drives heavy thrusts about one stroke every second while her sheer mesh crop top shifts. "
        "By the end, both keep the pace going. Wet skin slaps and heavy breath.\n"
    )
    out, rep = br.finalize_writer_prompt(dd, c, strict=True)
    assert "w5_final" not in rep
    assert "sheer mesh bikini bottom of <Picture 1>: partially_preserved" in out
    assert "sheer mesh bikini bottom stays pulled aside" in out


def test_followup_p1_rework_rejects_youth_cast():
    import pytest
    with pytest.raises(br.WriterNotReady, match="youth|18\\+|adult age"):
        br.finalize_writer_prompt(
            "detailed_description:\n[Shot 1] medium shot. At first, she lies on the bed.\n",
            {"man": "a 17-year-old boy in jeans", "position": "missionary", "ask": "missionary",
             "surface": "the bed", "place": "a bedroom", "garments_all": [], "garments": {}, "camera_tail": ""},
        )


def test_followup_nb1_nb4_nb8_nb9_nb10_nb12_nb13():
    import re
    # NB9: compound lingerie split + sheer fabric exempt
    sr = {"read": {"room": "bedroom", "place": "bedroom", "surface": "bed", "bed": True, "sheets": "white",
                   "floor": "rug", "pose": "kneels on the bed", "facing_camera": True, "framing": "medium",
                   "light": "warm lamp", "people": 1,
                   "garments": [{"type": "lingerie", "name": "sheer beige bra and high-waist panty with garters", "look": "sheer beige"}],
                   "build": "curvy", "skin": "fair", "hair": "brown"}}
    facts = br.still_facts(sr)
    assert any("bra" in g["name"] for g in facts["garments"]) and any("panty" in g["name"] for g in facts["garments"])
    pat = br.absent_garment_pattern(facts)
    assert not re.search(pat, "the sheer fabric shifts", re.I)

    # NB1 + NB4 + NB10 + NB12
    c_oral = br.make_cast(sr, "blowjob", "blowjob on the bed", role="consensual roleplay")
    dd_oral = (
        "subject_definitions:\n<Picture 1> is the reference image.\n"
        "<Subject 2> is a muscular 30-year-old man in board shorts who enters from the left and he is (S2).\n"
        "summary:\n(S1) in a blowjob clip on the bed.\nretention_analysis:\nkept.\n"
        "detailed_description:\n"
        "[Shot 1] The camera holds a medium close-up at knee height. "
        "At first, (S1) kneels on the bed, and (S2), a muscular 30-year-old man in board shorts, stands before her. "
        "(S2)'s penis is inside her mouth, her lips sealed around his shaft. "
        "As it builds, PRIMARY MOTION - she bobs on his shaft at one cycle every second. "
        "(S2) says in a breathy voice, <d>[English] Keep going.</d> "
        "By the end, she keeps bobbing, wet suction on every stroke.\n"
    )
    out_oral, _ = br.finalize_writer_prompt(dd_oral, c_oral, strict=True)
    assert "board shorts" in out_oral
    assert "consensual roleplay" in out_oral or "all characters are consenting adults" in out_oral
    assert "adjusted as she works" in " ".join(br._garment_retention(c_oral, {"garments": {"bra": "on", "panties": "on"}, "writer_aside": ["bra"]}))
    assert "breathy" in out_oral

    # NB13: scissoring contact + lint_final_prompt clean
    c_ff = br.make_cast(sr, "ff_scissoring", "FF scissoring on the bed")
    assert "vulva is pressed to" in c_ff["contact"]
    assert br.lint_final_prompt("subject_definitions:\n<Picture 1>\nsummary:\ns\nretention_analysis:\nr\ndetailed_description:\n[Shot 1] A.\n") == []


def test_followup_item18_and_section4_lint():
    import wp_lint
    # Item 18: double_says catches ", and (S1) says"
    bad_dd = "[Shot 1] medium shot. (S1) says, and (S1) says in a low voice, <d>[English] Yes.</d>"
    assert any(h["code"] == "double_says" for h in wp_lint.lint(bad_dd, {"kind": "talk", "slots": {}, "cfg": {"speech_words_max": 30, "max_lines_per_speaker": 3}})["issues"])

    # Section 4.1: facial finish allowed without no_contact / contact_anatomy hard fail
    fin_dd = (
        "detailed_description:\n[Shot 1] The camera holds a medium close-up at eye level in warm lamp light. "
        "At first, (S1) kneels on the rug looking up at (S2). "
        "As it builds, PRIMARY MOTION - (S2) strokes himself fast, two strokes a second, ejaculating onto her cheeks and lips while she keeps her eyes open. "
        "(S1) says in an eager voice, <d>[English] Right on my face.</d> "
        "By the end, warm semen coats her cheek as she breathes hard.\n"
    )
    res_fin = wp_lint.lint(fin_dd, {"kind": "partner", "cfg": {"speech_words_max": 30, "max_lines_per_speaker": 3},
                                    "slots": {"position": "finish", "ask": "he finishes on her, facial", "surface": "the rug", "garments_all": []}})
    hard_codes = {h["code"] for h in res_fin["issues"] if h.get("hard")}
    assert "no_contact" not in hard_codes and "contact_anatomy" not in hard_codes

    # Section 4.2: consent_setup only hard-fails on talk/agreement clip, not sex clip
    sex_sleep = (
        "detailed_description:\n[Shot 1] The camera holds a medium two-shot in warm lamp light. "
        "At first, (S1) lies on her side on the bed, eyes closed, breathing slowly. "
        "(S2)'s penis slides into her vagina from behind until his hips sit flush against her buttocks, and he stays deep in her. "
        "As it builds, PRIMARY MOTION - (S2) thrusts at one slow stroke every two seconds as the mattress dips. "
        "By the end, he stays buried in her, skin sliding softly.\n"
    )
    res_sleep = wp_lint.lint(sex_sleep, {"kind": "sex", "cfg": {"speech_words_max": 30, "max_lines_per_speaker": 2},
                                         "overlays": ["consent_setup", "states"], "slots": {"position": "spooning", "ask": "sleep roleplay, spooning", "surface": "the bed", "garments_all": []}})
    assert not any(h["code"] == "consent_setup" and h.get("hard") for h in res_sleep["issues"])
