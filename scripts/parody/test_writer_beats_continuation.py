"""The N-beat writer-format continuation route (extend-test-3beat-20261115, Prompt maker t285u).

build_writer_beats_continuation_request feeds finished writer-format beat prompts (the writer's own four sections,
as written) into ONE native latent-tail continuation graph. CPU only: no GPU, no network, no queue, no ComfyUI.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import unittest

import build_request as br


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"writer-beats continuation CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

TEMPLATE = br.DEFAULT_REFMOD_TEMPLATE
PRONOUN = "she"

S1 = ("<Subject 1> is the exact same woman shown in <Picture 1> of the reference pictures and in the first 5 seconds "
      "of this clip, preserving her face, hairstyle, body, skin and figure with complete fidelity; a fictional adult "
      "woman aged 27, fair skin, long platinum-blonde hair; she is (S1) and stays on screen right.")
S2 = ("<Subject 2> is the exact same man shown in <Picture 1> of the reference pictures and in the first 5 seconds of "
      "this clip, preserving his face, hair, stubble, body, skin and build with complete fidelity; a fictional adult "
      "man aged 31, athletic build; he is (S2) and stays on screen left.")


def _beat(n: int, picture_line: str) -> str:
    """One writer-format beat prompt (the pack's shape: <Picture 1> identity line, bios, act, [Shot 2] cut)."""
    return (
        "subject_definitions:\n"
        + picture_line + "\n" + S1 + "\n" + S2 + "\n"
        + f"Wardrobe at the start of beat {n}: <Subject 1> wears a pink bikini top and white boots; <Subject 2> wears "
          "navy boxer briefs at mid-thigh.\n"
          + br.R11_HAND + "\n\n"
          + "summary:\n[reference generation] Bent over the low bed edge, the woman takes doggy-style fucking in beat "
        + f"{n} with her palms on the sheets.\n\n"
          "retention_analysis:\n"
          "<Subject 1> (appears in [Shot 1]): fully_preserved - her face, hairstyle, body, skin and figure are kept "
          "from <Picture 1> in every shot\n"
          "<Subject 2> (appears in [Shot 1]): fully_preserved - his face, hair, stubble, body, skin and build are kept "
          "from <Picture 1> in every shot\n"
          "<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - the charcoal wall and the low bed with "
          "grey-lavender sheets are kept; the framing continues from the previous beat\n\n"
          "detailed_description:\n"
          f"[Shot 1] The camera holds a static medium close-up on her face from a front three-quarter angle, shallow "
          f"depth of field. Warm lamp light falls across their bodies. At first, <Subject 1> is bent over the low bed "
          f"edge at screen right with her palms on the sheets, and <Subject 2> stands behind her at screen left, his "
          f"penis inside her vagina from behind, the steady strokes running. Marker A{n}: his right hand gathers her "
          "platinum hair at the back of her head, five fingers closing over it.\n"
          f"[Shot 2] At 00:03.250, the camera cuts to a medium shot in side profile at hip height. The camera holds a "
          f"static shot. PRIMARY MOTION - (S2) drives hard, deep doggy thrusts at two strokes a second. Marker B{n}: "
          'the low bed creaks under her palms. (S1) says in a hoarse, breathless voice, <d>[English] Keep going.</d>\n'
    )


BEAT1 = _beat(1, "<Picture 1> is the start still GI183, the reference image defining the exact visual appearance, "
                 "identity, face and hairstyle of <Subject 1> and <Subject 2>, and the dim bedroom: a charcoal wall, "
                 "a low bed with grey-lavender sheets, its light and the opening pose and framing of this clip: she "
                 "stands on the hardwood at screen right.")
BEAT2 = _beat(2, "<Picture 1> is the start still GI183 that opened beat 1 of this same continuous take, the reference "
                 "image defining the exact visual appearance, identity, face and hairstyle of <Subject 1> and "
                 "<Subject 2>, and the dim bedroom; this beat opens on the last moment of the previous beat: "
                 "<Subject 1> bent over the low bed edge with her palms on the sheets.")
BEAT3 = _beat(3, "<Picture 1> is the start still GI183 that opened beat 1 of this same continuous take, the reference "
                 "image defining the exact visual appearance, identity, face and hairstyle of <Subject 1> and "
                 "<Subject 2>, and the dim bedroom; this beat opens on the last moment of the previous beat: "
                 "<Subject 1> arched deep with her hair in his fist.")
END_ACTIONS = [
    "stays bent over the low bed edge with her palms on the grey sheets while his steady strokes keep landing",
    "stays bent over the low bed edge, arched deep with her hair in his fist while his hard thrusts keep landing",
    "stays bent over the low bed edge, rocking back onto his long deep strokes as he nears his climax",
]
FRAMES = [192, 187, 187]


def _base_graph():
    return json.loads(Path(TEMPLATE).read_text(encoding="utf-8"))


def _build(**kw):
    args = dict(base_graph=_base_graph(), beat_prompts=[BEAT1, BEAT2, BEAT3], prefix="community/wbc-test/clip",
                seed=51083601, frames=list(FRAMES), end_actions=list(END_ACTIONS), pronoun=PRONOUN,
                width=768, height=1344)
    args.update(kw)
    return br.build_writer_beats_continuation_request(**args)


class TestWriterBeatsContinuation(unittest.TestCase):
    def test_three_writer_beats_become_one_latent_tail_graph(self):
        g, prompt_all, plan = _build()
        self.assertEqual(plan["mode"], "native_latent_tail_continuation")
        self.assertEqual(plan["format"], "writer_beats")
        self.assertEqual(plan["clip_count"], 3)
        self.assertEqual(plan["base_frames"], 192)
        self.assertEqual(plan["total_frames"], 566)
        self.assertEqual(plan["overlap_frames"], 22)
        self.assertEqual([b["frames"] for b in plan["beats"]], [192, 379, 566])
        for b in plan["beats"][1:]:
            self.assertEqual(b["layout"]["window_frames"], 209)
            self.assertLessEqual(b["layout"]["window_frames"], br.CONTINUATION_WINDOW_MAX_FRAMES)
        self.assertEqual({k for k in g if re.fullmatch(r"c\d", k)}, {"c0", "c2", "c3"})
        self.assertEqual(g["c2_gen"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(g["c3_gen"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(g["s0_sep"]["inputs"]["av_latent"], ["c3_append", 0])
        self.assertEqual({k for k in g if "refapply" in k}, {"refapply", "c2_refapply", "c3_refapply"})
        self.assertEqual(g["c2_refapply"]["inputs"]["mods"], ["refmods", 0])
        self.assertEqual(g["c0"]["inputs"]["length"], 192)
        self.assertEqual((g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]), (768, 1344))
        self.assertEqual(g["noise"]["inputs"]["noise_seed"], 51083601)
        self.assertEqual(g["save"]["inputs"]["filename_prefix"], "community/wbc-test/clip")
        self.assertNotIn("LoRA", json.dumps(g))

    def test_authored_prompt_text_is_sent_byte_identical_plus_builder_lead_in(self):
        g, _, plan = _build()
        for i, (authored, node) in enumerate(zip((BEAT1, BEAT2, BEAT3), ("c0", "c2", "c3")), start=1):
            sent = g[node]["inputs"]["prompt"]
            lead = plan["beat_leads"][i - 1]["lead_in"]
            probe = lead + " "
            if lead:
                self.assertEqual(sent.count(lead), 1, f"beat {i}: the lead-in is not a single inserted block")
            stripped = sent.replace(probe, "", 1) if lead else sent
            self.assertEqual(stripped, authored.strip(), f"beat {i}: the route changed the authored prompt text")
            for section in ("subject_definitions", "summary", "retention_analysis", "detailed_description"):
                self.assertIn(section + ":", sent)
            self.assertIn(f"Marker A{i}", sent)
            self.assertIn(f"Marker B{i}", sent)
            self.assertIn(br.R11_HAND, sent)

    def test_beat_one_has_no_lead_in_and_continuation_beats_get_the_builders_own(self):
        g, _, plan = _build()
        b1, b2, b3 = (g[n]["inputs"]["prompt"] for n in ("c0", "c2", "c3"))
        self.assertNotIn("The shot continues from the last seen moment", b1)
        lead2, lead3 = (plan["beat_leads"][i]["lead_in"] for i in (1, 2))
        self.assertIn(lead2, b2)
        self.assertIn(lead3, b3)
        # the builder's lead-in carries the previous beat's end_action, never a stock standing pose
        self.assertIn("the same pose the previous beat ended on (she " + END_ACTIONS[0][:40], lead2)
        self.assertIn("the same pose the previous beat ended on (she " + END_ACTIONS[1][:40], lead3)
        # a beat with [Shot 2+] cuts gets the dynamic lead-in (as the parody lane's continuation_scene picks it)
        self.assertIn("The shot continues from the last seen moment:", lead2)
        self.assertIn("the shot never resets to a starting photo", lead2)
        self.assertNotIn("the same framing, ", lead2)
        self.assertLess(b2.index("The shot continues from the last seen moment"), b2.index("Marker A2"))
        self.assertLess(b2.index("The shot continues from the last seen moment"), b2.index("[Shot 2]"))

    def test_picture1_identity_line_survives_on_continuation_beats_with_no_staged_image(self):
        g, _, _ = _build(start_image="community/GI183_fixture.jpg")
        for node in ("c2", "c3"):
            sent = g[node]["inputs"]["prompt"]
            self.assertIn("<Picture 1> is the start still GI183 that opened beat 1", sent)
            self.assertIn("this beat opens on the last moment of the previous beat", sent)
        self.assertIn("img_1", g)
        self.assertEqual(g["add_guide"]["inputs"]["frame_idx"], 0)
        self.assertEqual(g["add_guide"]["inputs"]["image"], ["img_1", 0])
        self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["add_guide", 0])
        staged_on = {k for k in g if g[k].get("class_type") in ("LoadImage", "MiniMaxH3AddGuide")
                     and (k.startswith("c2") or k.startswith("c3"))}
        self.assertEqual(staged_on, set())
        self.assertNotIn("img_1", json.dumps({k: v for k, v in g.items() if k.startswith(("c2", "c3"))}))

    def test_no_h3_video_continuation_opener_is_emitted(self):
        g, _, _ = _build()
        for node in ("c0", "c2", "c3"):
            self.assertNotIn("[video continuation]", g[node]["inputs"]["prompt"])
            self.assertNotIn("<Video 1>", g[node]["inputs"]["prompt"])

    def test_incomplete_input_fails_closed(self):
        with self.assertRaises(ValueError):
            _build(beat_prompts=[BEAT1])
        with self.assertRaises(ValueError):
            _build(frames=[192, 187])
        no_ret = re.sub(r"retention_analysis:\n.*?\n\n", "", BEAT2, count=1, flags=re.S)
        self.assertNotIn("retention_analysis:", no_ret)
        with self.assertRaises(br.WriterPromptError):
            _build(beat_prompts=[BEAT1, no_ret], frames=[192, 187])
        no_shot1 = BEAT2.replace("detailed_description:\n[Shot 1] ", "detailed_description:\n", 1)
        with self.assertRaises(br.WriterPromptError):
            _build(beat_prompts=[BEAT1, no_shot1], frames=[192, 187])

    def test_prompt_all_lists_every_beat(self):
        _, prompt_all, plan = _build()
        self.assertEqual(len(plan["beats"]), 3)
        for i in (1, 2, 3):
            self.assertIn(f"===== beat {i} =====", prompt_all)
        self.assertIn("Marker A3", prompt_all)


if __name__ == "__main__":
    unittest.main()
