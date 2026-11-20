"""Unit tests for the PM settle example-strip follow-ups: filler rules and example 6-gram gate."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _p in (
    _HERE,
    Path("/home/evo/AI/community/scripts/parody"),
    Path("/home/evo/AI/_runs/W1b/settle_src"),
):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import wp_lint
import wp_state
from settle_lib import filler_line_hit as settle_filler_hit


def test_take_it_standalone_and_opener_banned():
    fillers = ["take it", "take it all", "right there"]
    assert wp_lint.filler_line_hit("take it", fillers) is True
    assert wp_lint.filler_line_hit("take it all", fillers) is True
    assert wp_lint.filler_line_hit("take it from the sunset", fillers) is True  # opener, even with no body-part
    assert wp_lint.filler_line_hit("take it all now", fillers) is True


def test_take_inside_concrete_line_allowed():
    fillers = ["take it", "take it all", "right there"]
    # mid-line, names depth / body part / position
    assert wp_lint.filler_line_hit("now take it to the base", fillers) is False
    assert wp_lint.filler_line_hit("then take it all down her throat", fillers) is False
    assert wp_lint.filler_line_hit("just take it from behind", fillers) is False
    # mid-line with no concrete anchor still banned
    assert wp_lint.filler_line_hit("just take it already", fillers) is True


def test_right_there_is_hard_filler():
    fillers = ["take it", "take it all", "right there", "yes right there"]
    assert wp_lint.filler_line_hit("right there", fillers) is True
    assert wp_lint.filler_line_hit("yes right there", fillers) is True
    assert wp_lint.filler_line_hit("stay right there for me", fillers) is True
    # unrelated line
    assert wp_lint.filler_line_hit("keep that angle", fillers) is False


def test_other_stock_fillers_still_match():
    fillers = ["fuck me harder", "hold still"]
    assert wp_lint.filler_line_hit("fuck me harder", fillers) is True
    assert wp_lint.filler_line_hit("please fuck me harder now", fillers) is True
    assert wp_lint.filler_line_hit("hold still", fillers) is True


def test_settle_lib_same_take_it_rule():
    assert settle_filler_hit("take it", "take it") is True
    assert settle_filler_hit("now take it to the base", "take it") is False
    assert settle_filler_hit("just take it already", "take it") is True
    assert settle_filler_hit("stay right there", "right there") is True


def test_example_sixgrams_from_examples_block_only():
    prompt = (
        "RULES\n- the camera is a medium two-shot at hip height.\n"
        "EXAMPLES (level of detail only; never reuse their words)\n"
        "- Pro: [Shot 1] The camera holds a static medium two-shot. "
        "A cool rim from the window behind the bed outlines her hair against the dark headboard. "
        "The mattress creaks under his knees, her breath catches.\n"
        "SHAPE (blanks)\n"
        "detailed_description:\n[Shot 1] <camera sentence>.\n"
    )
    grams = wp_state.example_sixgrams(prompt)
    # distinctive example narrative survives the whitelist
    joined = " | ".join(grams)
    assert any("window behind the bed outlines" in g or "cool rim from the window" in g for g in grams), joined
    # no grams from the RULES or SHAPE sections
    assert not any("blanks" in g or "camera sentence" in g for g in grams)
    # a prompt with no EXAMPLES block yields nothing
    assert wp_state.example_sixgrams("just rules here, the camera is a medium two-shot at hip height") == []


def test_build_cloned_keeps_quoted_and_does_not_flag_structural():
    prompt_doc = (
        '[Shot 1] The camera is a medium two-shot at hip height.\n'
        '"he sinks in to the base from behind"\n'
        'His penis pushes into her vagina from behind until his hips are flush against her buttocks, and he stays buried in her.\n'
        '(S2) says in a low voice, <d>[English] Keep still.</d> By the end, she arches. Wet skin slaps on every stroke.'
    )
    recent_dd = (
        '[Shot 1] The camera is a medium two-shot at hip height. His penis pushes into her vagina from behind until his hips are '
        'flush against her buttocks, and he stays buried in her. <d>[English] More.</d> (S2) says in a low voice, <d>[English] Stay put.</d> '
        'By the end, she arches. Wet skin slaps on every stroke.'
    )
    cl = wp_state.build_cloned(prompt_doc, [recent_dd, recent_dd])
    assert "he sinks in to the base from behind" in cl
    assert not any("shot 1" in x or "d s2 says" in x or "hips are flush" in x or "buried in her" in x for x in cl), cl


def test_cloned_hits_gate_on_example_sixgram():
    prompt = (
        "EXAMPLES\n"
        "- Scene: a cool rim from the window behind the bed outlines her hair against the dark headboard.\n"
        "SHAPE\n"
    )
    phrases = wp_state.build_cloned(prompt, [])
    dd = "At first she sits still. A cool rim from the window behind the bed outlines her hair against the dark headboard. Motion continues."
    hits = wp_lint.cloned_hits(dd, phrases)
    assert hits, "expected the example 6-gram to trip the clone gate"
    clean = "At first she sits still on the sunlit porch rail. Motion continues as the curtain lifts."
    assert wp_lint.cloned_hits(clean, phrases) == []
