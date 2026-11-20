"""Unit tests for scripts/parody/beta7_convert.py (W3a, U56 Decision #1)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

PARODY_DIR = Path(__file__).resolve().parent
if str(PARODY_DIR) not in sys.path:
    sys.path.insert(0, str(PARODY_DIR))

import beta7_convert as b7
import wp_lint

REF2VA_6_SECTION = """\
subject_definitions:
<Subject 1> (S1): An adult woman in her late twenties with auburn hair tied back, wearing a navy sweater and dark jeans. (<Picture 1>)
<Subject 2> (S2): An adult man in his early thirties with short brown hair, wearing a charcoal jacket. (<Picture 2>)

summary:
(S1) and (S2) stand beside a rain-streaked cafe window and exchange two brief lines while setting down coffee cups.

retention_analysis:
Preserve the warm tungsten cafe lamp, the wooden table, and the rain outside the window throughout the clip.

integrated_multimodal_description:
[Shot 1] Static medium two-shot at eye level inside a warm tungsten-lit cafe, soft rain visible on the window behind the wooden table. At first, (S1) in her navy sweater rests both hands around a ceramic mug across from (S2) in his charcoal jacket. (S1) leans slightly forward and says in a dry, steady voice, <d>[English] You brought the wrong folder again.</d> (S2) glances down at the table, taps the kraft envelope once, and says in a low amused voice, <d>[English] Check the second tab before you glare.</d> By the end, (S1) slides the envelope toward herself and lifts the corner with a slight smirk.

overall_soundscape:
- Steady rain pattering softly against the glass window
- Ceramic mug clicking gently against the wooden tabletop and quiet cafe murmur in the distance

non_diegetic_music:
Warm lo-fi acoustic guitar underscored with subtle vinyl crackle.
"""

BASE_3_SECTION = """\
## integrated_multimodal_description:
[Shot 1] Smooth handheld medium shot moving slowly along a sunlit coastal pier. At first, an adult woman in a white linen shirt walks past weathered wooden pilings toward the railing. [Shot 2] At 00:03.250 Medium close-up as she stops by the rail, rests her palms on the warm wood, and says in a calm bright voice, <d>[English] The tide is already turning.</d>

**overall_soundscape:**
Ocean waves slapping rhythmically against the pier pilings and a light coastal breeze rushing past.

**non_diegetic_music:**
Swelling orchestral strings with soft piano chords.
"""


def test_convert_6_section_ref2va_passes_wp_lint_and_validator():
    converted, rep = b7.convert_to_beta7(REF2VA_6_SECTION, omit_pictures=[1], mode="auto")
    assert rep["mode_used"] == "render"
    assert "integrated_multimodal_description" in rep["removed_headers"]
    assert "overall_soundscape" in rep["folded_sound_headers"]
    assert "non_diegetic_music" in rep["dropped_music_headers"]
    assert rep["omitted_pictures"] == [1]

    # Banned headers and music are completely gone
    low = converted.lower()
    assert "integrated_multimodal_description:" not in low
    assert "overall_soundscape:" not in low
    assert "non_diegetic_music:" not in low
    assert "lo-fi acoustic guitar" not in low

    # Diegetic sound sentences folded into detailed_description
    assert "Steady rain pattering softly against the glass window." in converted
    assert "Ceramic mug clicking gently against the wooden tabletop" in converted

    # <Picture 1> omitted for RefMod subject, <Picture 2> preserved
    assert "<Picture 1>" not in converted
    assert "<Picture 2>" in converted

    # Live wp_lint.lint + validate_beta7 both pass with 0 header violations
    ctx = {
        "kind": "talk",
        "slots": {"surface": "wooden table", "garment": "navy sweater", "light": "warm tungsten", "place": "cafe"},
        "blacklist": [],
        "cloned": [],
        "cfg": {"speech_words_max": 25},
    }
    val = b7.validate_beta7(converted, clip_seconds=8.0, refmod_pictures=[1], lint_ctx=ctx, minimal_lint=True)
    assert val["status"] == "READY", val
    assert val["header_violations"] == []
    assert val["lint"] is not None
    assert val["lint"]["pass"] is True
    assert not any(i["code"] == "audio_header_beta7" for i in val["lint"]["issues"])

    # Also verify full (non-minimal) wp_lint has zero header_order / audio_header_beta7 issues
    full_lint = wp_lint.lint(converted, ctx, minimal=False)
    codes = {i["code"] for i in full_lint["issues"]}
    assert "header_order" not in codes
    assert "audio_header_beta7" not in codes


def test_convert_3_section_base_is_header_free_and_ready():
    converted, rep = b7.convert_to_beta7(BASE_3_SECTION, mode="auto")
    assert rep["mode_used"] == "plain"
    assert "integrated_multimodal_description:" not in converted.lower()
    assert "overall_soundscape:" not in converted.lower()
    assert "non_diegetic_music:" not in converted.lower()
    assert "orchestral strings" not in converted.lower()
    assert "Ocean waves slapping rhythmically" in converted
    assert "##" not in converted
    assert "**" not in converted

    val = b7.validate_beta7(converted, clip_seconds=8.0)
    assert val["status"] == "READY", val
    assert val["header_violations"] == []


def test_convert_plain_mode_strips_all_render_headers():
    converted, rep = b7.convert_to_beta7(REF2VA_6_SECTION, mode="plain")
    assert rep["mode_used"] == "plain"
    for h in ("subject_definitions:", "summary:", "retention_analysis:", "detailed_description:"):
        assert h not in converted.lower()
    assert converted.startswith("[Shot 1]")
    val = b7.validate_beta7(converted, clip_seconds=8.0)
    assert val["status"] == "READY", val


def test_validate_catches_banned_headers_markdown_policy_youth_and_timestamps():
    # Raw 6-section input without conversion must fail with banned headers
    raw_val = b7.validate_beta7(REF2VA_6_SECTION)
    assert raw_val["status"] == "NOT_READY"
    assert set(raw_val["header_violations"]) >= {
        "integrated_multimodal_description",
        "overall_soundscape",
        "non_diegetic_music",
    }

    # Markdown fence + Shot 1 timestamp + out-of-range Shot 2 + RefMod <Picture 1> + <Audio 0>
    bad = (
        "```text\n"
        "[Shot 1] At 00:00.000 Medium shot of <Picture 1> with <Audio 0>. "
        "[Shot 2] At 00:09.500 She speaks <d>[English] Hello.\n"
        "```"
    )
    v = b7.validate_beta7(bad, clip_seconds=8.0, refmod_pictures=[1])
    assert v["status"] == "NOT_READY"
    codes = {x["code"] for x in v["violations"]}
    assert "markdown_leakage" in codes
    assert "shot1_timestamp" in codes
    assert "shot_timestamp" in codes
    assert "refmod_picture_tag" in codes
    assert "zero_indexed_asset" in codes
    assert "dialogue_tags" in codes

    # Policy / refusal / youth stops
    pol = b7.validate_beta7("[Shot 1] This prompt complies with content policy for all adults.")
    assert pol["status"] == "NOT_READY"
    assert "policy_word" in {x["code"] for x in pol["violations"]}

    refusal = b7.validate_beta7("I cannot write that scene, let me know which non-explicit version you prefer.")
    assert refusal["status"] == "NOT_READY"
    assert "refusal" in {x["code"] for x in refusal["violations"]}

    youth = b7.validate_beta7("[Shot 1] A 16-year-old walks across the yard.")
    assert youth["status"] == "NOT_READY"
    assert "youth_hint" in {x["code"] for x in youth["violations"]}


def test_cli_json_and_exit_codes(tmp_path: Path, capsys):
    inp = tmp_path / "in.txt"
    out = tmp_path / "out.json"
    inp.write_text(BASE_3_SECTION, encoding="utf-8")

    rc = b7.main([str(inp), "--mode", "plain", "--clip-seconds", "8.0", "--validate", "--json", "-o", str(out)])
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["validation"]["status"] == "READY"
    assert data["validation"]["header_violations"] == []

    # Invalid prompt (unclosed <d>) exits 2
    bad_inp = tmp_path / "bad.txt"
    bad_inp.write_text("[Shot 1] She says <d>[English] broken tag.", encoding="utf-8")
    rc_bad = b7.main([str(bad_inp), "--validate"])
    assert rc_bad == 2
    _ = capsys.readouterr()



def _sex_pair_prompt(*, his_tag="(S2)", spoken="Hold the mug closer.") -> str:
    """Small two-subject fixture. Dialogue defaults to a non-filler line."""
    return f"""\
subject_definitions:
<Subject 1> (S1): An adult woman in her late twenties with auburn hair, wearing a navy sweater.
<Subject 2> (S2): An adult man in his early thirties with short brown hair, wearing a charcoal jacket.

summary:
(S1) and (S2) sit at a wooden table.

retention_analysis:
Preserve the warm lamp and the wooden table throughout the clip.

detailed_description:
[Shot 1] Static medium two-shot. At first, (S1) in her navy sweater sits across from (S2). <Subject 2> {his_tag} says in a low male voice, <d>[English] {spoken}</d> By the end, (S1) lifts her mug.

overall_soundscape:
Quiet cafe murmur in the distance.

non_diegetic_music:
N/A
"""


def test_load_filler_lines_uses_writer_config_list():
    lines = b7.load_filler_lines()
    assert "you feel so good" in lines
    assert "yes right there" in lines
    assert lines == [
        "hold still", "stay still", "take it", "yes right there", "oh yes",
        "fuck me harder", "take it all", "you feel so good", "so fucking good",
        "don't stop now", "right there",
    ]


def test_filler_lines_marks_not_ready_and_ask_is_exempt():
    converted, _ = b7.convert_to_beta7(_sex_pair_prompt(spoken="You feel so good."), mode="auto")
    val = b7.validate_beta7(converted, clip_seconds=8.0)
    assert val["status"] == "NOT_READY"
    assert val["not_ready_reason"] == "filler_lines"
    assert any(v["code"] == "filler_lines" for v in val["violations"])

    exempt = b7.validate_beta7(
        converted,
        clip_seconds=8.0,
        lint_ctx={"ask": "She says, <d>[English] You feel so good.</d>"},
    )
    assert not any(v["code"] == "filler_lines" for v in exempt["violations"])


def test_speaker_tag_mismatch_when_his_line_uses_her_number():
    bad, _ = b7.convert_to_beta7(_sex_pair_prompt(his_tag="(S1)"), mode="auto")
    val = b7.validate_beta7(bad, clip_seconds=8.0)
    assert val["status"] == "NOT_READY"
    assert val["not_ready_reason"] == "speaker_tag_mismatch"
    assert any(v["code"] == "speaker_tag_mismatch" for v in val["violations"])

    good, _ = b7.convert_to_beta7(_sex_pair_prompt(his_tag="(S2)"), mode="auto")
    ok = b7.validate_beta7(good, clip_seconds=8.0)
    assert ok["status"] == "READY", ok
    assert not any(v["code"] == "speaker_tag_mismatch" for v in ok["violations"])

    undeclared = good.replace("(S2) says", "(S3) says").replace("<Subject 2> (S2)", "<Subject 2> (S3)")
    miss = b7.validate_beta7(undeclared, clip_seconds=8.0)
    assert miss["status"] == "NOT_READY"
    assert any("S3" in v["note"] for v in miss["violations"] if v["code"] == "speaker_tag_mismatch")


def test_six_section_completeness_on_raw_and_scoring_path():
    six = b7.six_section_report(REF2VA_6_SECTION)
    assert six["six_section_complete"] is True
    assert six["missing_sections"] == []

    raw_val = b7.validate_beta7(REF2VA_6_SECTION, require_six_sections=True)
    # Raw official text still has banned Beta 7 audio headers.
    assert raw_val["status"] == "NOT_READY"
    assert raw_val["six_section_complete"] is True
    assert "six_section_incomplete" not in {v["code"] for v in raw_val["violations"]}

    truncated = REF2VA_6_SECTION.split("non_diegetic_music:")[0].rstrip()
    incomplete = b7.validate_beta7(truncated, require_six_sections=True)
    assert incomplete["status"] == "NOT_READY"
    assert incomplete["not_ready_reason"] == "six_section_incomplete"
    assert incomplete["six_section_complete"] is False
    assert "non_diegetic_music" in incomplete.get("sections_present", []) or "non_diegetic_music" in b7.six_section_report(truncated)["missing_sections"]

    scored = b7.score_ref2va_output(REF2VA_6_SECTION, clip_seconds=8.0, omit_pictures=[1])
    assert scored["six_section_complete"] is True
    assert scored["validation"]["status"] == "READY", scored["validation"]
    assert scored["status"] == "READY"

    scored_bad = b7.score_ref2va_output(truncated, clip_seconds=8.0)
    assert scored_bad["status"] == "NOT_READY"
    assert scored_bad["not_ready_reason"] == "six_section_incomplete"


def test_regen_once_on_filler_keeps_second_result_if_still_hit():
    clean = _sex_pair_prompt(spoken="Hold the mug closer.")
    dirty = _sex_pair_prompt(spoken="You feel so good.")
    calls: list[int] = []

    def gen_recovers(seed: int) -> str:
        calls.append(seed)
        return dirty if seed == 7 else clean

    recovered = b7.run_with_single_regen(gen_recovers, seed=7, clip_seconds=8.0)
    assert calls == [7, 8]
    assert recovered["regen"]["attempted"] is True
    assert recovered["regen"]["first_codes"] == ["filler_lines"]
    assert recovered["validation"]["status"] == "READY", recovered["validation"]
    assert recovered["validation"].get("not_ready_reason") is None

    calls.clear()

    def gen_still_dirty(seed: int) -> str:
        calls.append(seed)
        return dirty

    stuck = b7.run_with_single_regen(gen_still_dirty, seed=7, clip_seconds=8.0)
    assert calls == [7, 8]
    assert stuck["validation"]["status"] == "NOT_READY"
    assert stuck["validation"]["not_ready_reason"] == "filler_lines"

    # Other validation failures do not trigger a second generate.
    calls.clear()

    def gen_policy(_seed: int) -> str:
        calls.append(_seed)
        return "[Shot 1] This prompt complies with content policy for all adults."

    policy = b7.run_with_single_regen(gen_policy, seed=3, clip_seconds=8.0)
    assert calls == [3]
    assert policy["regen"]["attempted"] is False
    assert policy["validation"]["status"] == "NOT_READY"
