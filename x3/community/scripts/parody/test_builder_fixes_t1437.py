"""Builder fixes approved by Derrick, card t1437s5374 (2026-11-13): one test per item (Max Architect 3)."""
import build_request as br

READ = {"read": {"room": "beach", "place": "on a driftwood log", "surface": "log", "bed": False, "floor": "sand",
                 "pose": "leaning, sitting", "facing_camera": True, "framing": "medium shot", "light": "golden hour",
                 "people": 1, "garments": [{"type": "top", "name": "sheer mesh crop top", "look": "wet"},
                                           {"type": "bottom", "name": "sheer mesh bikini bottom", "look": "wet"}],
                 "build": "curvy", "skin": "damp skin", "hair": "blonde, damp"}}
HDR = ("subject_definitions:\n<Picture 1> is the reference image.\n\nsummary:\nA clip.\n\nretention_analysis:\nkept.\n\n"
       "detailed_description:\n[Shot 1] ")


def _fin(dd, position, ask, **mk):
    cast = br.make_cast(READ, position, ask, **mk)
    return br.finalize_writer_prompt(HDR + dd, cast, strict=False)


def test_1_his_clothes_re_only_his_clothes():
    assert not br._HIS_CLOTHES_RE.search("(S2) pulls her bikini bottom aside, where it stays bunched at her waist")
    assert br._HIS_CLOTHES_RE.search("his jeans stay bunched at his knees")


def test_2_same_move_no_second_move_in():
    assert br._same_move("she sinks to her knees in front of him", "(S1) drops to her knees on the sand.")
    assert not br._same_move("she lies back on the log", "(S1) drops to her knees on the sand.")


def test_3_writer_tempo_sentence_gets_label():
    dd = ("The camera holds a medium shot at hip height, keeping her face, his face and the join in frame. At first, (S1) sits on "
          "the log, leaning forward. She shifts onto her hands and knees on the log. (S2) pulls her sheer mesh bikini bottom aside "
          "to one side at her hip, where it stays. (S2) enters her from behind and stays buried in her, hips flush. As it builds, "
          "(S2) thrusts hard at about one stroke every second, her body rocking forward with each thrust. By the end, he keeps "
          "thrusting. A wet rhythmic slap.")
    out, rep = _fin(dd, "doggy", "doggy on the log")
    assert out.count("PRIMARY MOTION") == 1, out
    assert "PRIMARY MOTION - (S2) thrusts hard" in out or "PRIMARY MOTION - (S2) thrusts hard".replace("(S2)", "<Subject 2>") in out
    assert any("writer's tempo sentence" in a for a in rep["added"])


def test_4_pulls_it_aside_credits_join_garment():
    sents = ["(S2) hooks his fingers under the waistband.", "(S2) pulls it aside to one side at her hip, where it stays."]
    cast = br.make_cast(READ, "doggy", "doggy on the log")
    _, state, _ = br.track_state(sents, cast)
    assert state.get("writer_aside"), state


def test_5_no_placeholder_voice_for_absent_partner():
    out = br._speech_form("S2", {"S1": br.OC_VOICE_S1}, "<d>[English] hello there</d>")
    assert "distinct adult voice" not in out and out.startswith("(S2) says,")


def test_6_futa_camera_and_voice():
    cast = br.make_cast(READ, "missionary", "futa missionary on the log", partner_type="futa")
    assert "adult man's" not in (cast.get("voice_s2") or "") and "woman's voice" in cast["voice_s2"]
    br._CTX["position"] = "missionary"
    cam = br._resolve_camera(["The camera is a medium two-shot at hip height."], "keeping both faces in frame")[0]
    assert "his face" not in cam and "both faces" in cam, cam


def test_7_titjob_and_finish_exempt_from_w5():
    dd = ("The camera holds a medium shot, keeping her face in frame. At first, (S1) sits on the log. She kneels on the sand in "
          "front of him. (S2) slides his shaft between her breasts as she presses them around him. As it builds, PRIMARY MOTION - "
          "his shaft slides between her breasts about one cycle every second. By the end, she keeps pressing. Wet skin sounds.")
    _, rep = _fin(dd, "titjob", "titjob on the beach")
    assert "W5" not in str(rep.get("not_ready") or ""), rep.get("not_ready")


def test_c1a_join_words_count_as_entry():
    assert br._JOIN_PEN_RE.search("he thrusts deep into her from behind")
    assert br._JOIN_PEN_RE.search("staying buried in her vagina")
    assert not br._JOIN_PEN_RE.search("his shaft deep in her mouth")


def test_c1b_continued_opener_recognised():
    assert br._OPENER_RE.search("At first, (S1) is on her hands and knees on the log, her hair messy.")


def test_mmf_third_person_faceless():
    cast = br.make_cast(READ, "mmf", "mmf on the log", partner_type2="faceless")
    assert cast.get("partner_type2") == "faceless"


def test_c1a_w5_fires_without_clearance():
    dd = ("The camera holds a medium shot at hip height, keeping her face, his face and the join in frame. At first, (S1) sits on "
          "the log, leaning forward. She shifts onto her hands and knees on the log. (S2) grips her hips and thrusts deep into her "
          "from behind, staying buried in her. As it builds, PRIMARY MOTION - heavy rear thrusts about one stroke every second. "
          "By the end, he keeps thrusting. A wet rhythmic slap.")
    _, rep = _fin(dd, "doggy", "doggy on the log")
    assert "W5" in str(rep.get("not_ready") or ""), rep.get("not_ready")


# ---- MMF S3 (Derrick t1440): generated look, reference still, faceless fallback ------------------------------------------
MMF_DD = ("The camera holds a medium shot at hip height, keeping all three faces in frame. At first, (S1) sits on the log, leaning "
          "forward. She shifts onto her hands and knees on the log. (S3) pulls her sheer mesh bikini bottom aside to one side at her "
          "hip, where it stays. (S2) kneels at her head and slides past her lips deep inside her mouth while (S3) kneels behind her "
          "and enters her, staying buried in her. <Picture 2> sets his look. As it builds, PRIMARY MOTION - (S3) thrusts about one "
          "stroke every second. By the end, he keeps thrusting. Wet suction and breath through her nose.")


def _mmf_graph():
    return {"c0": {"inputs": {"prompt": "", "length": 243, "width": 768, "height": 1344}}, "noise": {"inputs": {}},
            "save": {"inputs": {}}, "img_1": {"class_type": "LoadImage", "inputs": {"image": "community/u6/x.jpg"}}}


def test_mmf_s3_generated_look_in_subject_definitions():
    cast = dict(br.make_cast(READ, "mmf", "mmf on the log", partner_type2="faceless"),
                man3="an adult man, 31 years of age, of lean build, with short dark hair, in grey linen trousers")
    out, _ = br.finalize_writer_prompt(HDR + MMF_DD, cast, strict=False)
    assert "<Subject 3> is an adult man, 31 years of age, of lean build, with short dark hair, in grey linen trousers" in out


def test_mmf_faceless_default_is_a_man():
    cast = br.make_cast(READ, "mmf", "mmf on the log", partner_type2="faceless")
    out, _ = br.finalize_writer_prompt(HDR + MMF_DD, cast, strict=False)
    assert "<Subject 3> is an adult man" in out and "<Picture 2>" not in out  # no still: the absent-ref strip stays on


def test_mmf_s3_still_picture_survives_and_is_wired():
    cast = dict(br.make_cast(READ, "mmf", "mmf on the log", partner_type2="faceless"),
                man3="an adult man, 31 years of age, of lean build", s3_still="community/flux_p1_20261030/M01_body.jpg")
    g, prompt, rep = br.build_writer_request(_mmf_graph(), HDR + MMF_DD, cast, "community/t/x", strict=False)
    assert "<Picture 2> is the reference image defining the exact visual appearance, identity, face and hairstyle of <Subject 3>." in prompt
    assert "<Picture 2> sets his look" in prompt  # the writer's own <Picture 2> sentence is no longer stripped
    assert g["img_s3"]["inputs"]["image"] == "community/flux_p1_20261030/M01_body.jpg"
    assert g["c0"]["inputs"]["ref_images.ref_image_1"] == ["img_1", 0]
    assert g["c0"]["inputs"]["ref_images.ref_image_2"] == ["img_s3", 0]


def test_c1b_mid_act_opener_kept_on_continued_clip():
    dd = ("The camera holds a medium shot at hip height, keeping her face, his face and the join in frame. At first, (S1) is on her "
          "hands and knees on the log with (S2) fully sheathed inside her from behind, her bikini bottom aside at her hip. As it builds, "
          "PRIMARY MOTION - (S2) thrusts about one stroke every second. By the end, he keeps thrusting. A wet rhythmic slap.")
    out, rep = _fin(dd, "doggy", "doggy on the log, keep going")
    assert "The clip opens on <Picture 1>" not in out, out
    assert any("opens mid-act" in a for a in rep["added"])


# ---- long-scene spec B1/B2/G1-G4 (Prompt maker t243s804) -------------------------------------------------------------
LONG_DD = ("The camera holds a medium-wide shot at hip height, keeping her face, his face and the join in frame. At first, (S1) sits "
           "on the log, leaning forward. She shifts onto her hands and knees on the log. (S2) pulls her sheer mesh bikini bottom aside "
           "to one side at her hip, where it stays. (S2) enters her from behind and stays buried in her, hips flush. As it builds, "
           "PRIMARY MOTION - (S2) thrusts about one stroke every second. (S1) says in a strained voice, <d>[English] Don't stop.</d> "
           "[Shot 2] At 00:05.000, the camera cuts to a medium close-up of her face at eye level, the same rhythm continuing. "
           "(S1) says in a strained voice, <d>[English] Right there.</d> A wet rhythmic slap.")


def test_b1_single_is_todays_collapse():
    cast = br.make_cast(READ, "doggy", "doggy on the log")
    out_default, _ = br.finalize_writer_prompt(HDR + LONG_DD, cast, strict=False)
    out_single, _ = br.finalize_writer_prompt(HDR + LONG_DD, dict(cast, shots="single"), strict=False)
    assert out_default == out_single and "[Shot 2]" not in out_single


def test_b1_multi_keeps_headers_clocks_and_retention():
    cast = dict(br.make_cast(READ, "doggy", "doggy on the log"), shots="multi")
    out, rep = br.finalize_writer_prompt(HDR + LONG_DD, cast, strict=False)
    assert "[Shot 1] " in out and "[Shot 2] At 00:05.000, the camera cuts to a medium close-up of her face" in out, out
    assert "Right there" in out.split("[Shot 2] At")[1] and "Right there" not in out.split("[Shot 2] At")[0]
    assert "<Subject 1> (appears in [Shot 1], [Shot 2])" in out
    assert rep["shots"] == [{"shot": 2, "at": "00:05.000"}]


def test_b1_bad_clock_not_ready():
    import pytest
    cast = dict(br.make_cast(READ, "doggy", "doggy on the log"), shots="multi")
    for bad in ("At 00:01.000,", "At 00:09.500,"):
        with pytest.raises(br.WriterNotReady):
            br.finalize_writer_prompt(HDR + LONG_DD.replace("At 00:05.000,", bad), cast, strict=False)


def test_b2_line_cap_scales_with_length():
    lines = " ".join(f"(S1) says in a soft voice, <d>[English] line number {w}.</d>" for w in ("one", "two", "three", "four"))
    dd = ("The camera holds a medium shot, keeping her face in frame. At first, (S1) sits on the log. She shifts onto her hands and "
          "knees on the log. (S2) pulls her sheer mesh bikini bottom aside to one side at her hip, where it stays. (S2) enters her "
          "and stays buried in her. As it builds, PRIMARY MOTION - (S2) thrusts about one stroke every second. " + lines)
    base = br.make_cast(READ, "doggy", "doggy on the log")
    short, _ = br.finalize_writer_prompt(HDR + dd, dict(base, clip_seconds=4.0, speech_wps=10), strict=False)
    long_, _ = br.finalize_writer_prompt(HDR + dd, dict(base, clip_seconds=20.0, speech_wps=10), strict=False)
    assert short.count("<d>") == 1 and long_.count("<d>") == 4


def test_g1_g4_orc_is_non_human_with_look_voice_and_retention():
    cast = br.make_cast(READ, "doggy", "orc partner takes her from behind on the log")
    assert cast["partner_type"] == "non-human" and "orc" in cast["man"] and cast["voice_s2"] == br.OC_VOICE_NONHUMAN
    out, _ = br.finalize_writer_prompt(HDR + LONG_DD.split(" [Shot 2]")[0], cast, strict=False)
    assert "<Subject 2> is an adult male orc" in out and "same creature" in out and "the same man" not in out
    t = br.make_cast(READ, "doggy", "tentacles wrap her on the log")
    assert t["partner_type"] == "non-human" and t["voice_s2"] == ""
