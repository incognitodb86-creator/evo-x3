#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""(c) 2026-11-06 brief t224x214: native latent-tail continuation in ONE graph, no hard-cut stitching.

What this lane owns, and the only things checked here:
  1. a continuation beat's prompt carries the lead-in (inherit the last seen moment, micro-motion first,
     never reset to the photo); beat 1 and the single-shot path do not;
  2. the base/extension split honours the measured 243-frame sampled-window ceiling and the 17k + 5 grid;
  3. graph wiring: window -> latent-tail guide -> sampler -> append; RefModApply on every beat off one shared
     loader; the start photo on beat 1's chain only; one RandomNoise node; one SaveVideo; zero transition tokens;
  4. run_queue's objective expectation follows the CUMULATIVE clip, not the template's beat-1 length;
  5. the locked single-shot path is untouched.

The nodes' own internals (video/audio latent token counts, the 40 Hz audio boundary, the 22-frame overlap trim,
latent alignment) are NOT re-checked here: continuation_nodes.py raises on each of them at queue time.
"""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(r"C:\AI\community\scripts")
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_request as br  # noqa: E402
import run_queue  # noqa: E402

REFMOD_FILE = r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods\emilia_clarke_v1.4.safetensors"
REFMOD_ID = "emilia_clarke_v1.4"          # what the loader slot carries: the file stem
# the approved Daenerys / Emilia Clarke penthouse photo, the file the approved re-test runs
START_IMAGE = str(Path(r"C:\Users\derek\5slock\approved_characters\daenerys_penthouse_ref_20261106.jpg"))

# beat 1 = 192 frames; beat 2 extends that cumulative latent by 187 frames behind a 22-frame hidden overlap
# = a 209-frame sampled window (under the 243 ceiling) for a 379-frame / 15.7917 s deliverable
BEATS = [{"scene": "Cassie stands up from the sofa.", "end_action": "stands by the window.",
          "images": [START_IMAGE]},
         {"scene": "Cassie walks to the window.", "end_action": "looks out at the city.", "images": None}]


def _resolved(pronoun="she", character="Cassie Howard", actor="Emilia Clarke"):
    return {
        "character": character, "actor": actor, "person_key": "8c7d1b27bd", "index_status": "good",
        "refmod_path": REFMOD_FILE, "refmod_slots": {"mod_1": {"path": REFMOD_FILE, "strength": 1.0, "copies": 1}},
        "voice_ref_path": None, "pronoun": pronoun, "identity_note": "",
        "description": "Caucasian adult woman, early 30s, long straight platinum-blonde hair past the shoulders, "
                       "straight bangs across the forehead, brown eyes, defined brows, full lips. The face is the "
                       "exact identity of Emilia Clarke.",
        "identity_anchor": "Cassie Howard, an adult fictional film character",
        "voice_anchor": "low soft Midwest-American plain speech",
        "subject": "Cassie Howard (Emilia Clarke)",
    }


def _single_shot(seed=51083610):
    """The locked single shot: one 192-frame clip from the approved photo (the pre-continuation path)."""
    return br.build_parody_request(_resolved(), seed, "test_single", frames=192,
                                   scene="Cassie stands up from the sofa.",
                                   end_action="stands by the window.", images=[START_IMAGE])


def _continuation(seed=51083610, beats=None, resolved=None, **kwargs):
    """One continuation graph: returns (graph, prompt_all, plan) as build_continuation_request does.

    kwargs are the builder's shared per-beat dials (pronoun, image_role, lighting, ...) passed as arguments.
    """
    return br.build_continuation_request(resolved or _resolved(), seed, "test_cont",
                                         beats if beats is not None else BEATS, frames=192, **kwargs)


class TestContinuationLeadIn(unittest.TestCase):
    """The prompt rule: inherit the last seen moment, micro-motion first, never reset to the photo."""

    def test_beat_two_carries_the_lead_in_and_beat_one_does_not(self):
        graph, _, _ = _continuation()
        b1 = graph["c0"]["inputs"]["prompt"]
        b2 = graph["c2"]["inputs"]["prompt"]
        for cue in ("The shot continues from the last seen moment", "the same framing",
                    "natural micro-motion", "The camera does not change angle and the shot never resets"):
            self.assertIn(cue, b2)
            self.assertNotIn(cue, b1)
        self.assertIn("Cassie walks to the window", b2)          # the beat's own action, after the lead-in
        self.assertLess(b2.index("The shot continues"), b2.index("Cassie walks to the window"))

    def test_lead_in_uses_the_beat_pronoun_with_grammar(self):
        beats = [dict(BEATS[0], scene="He stands up."), dict(BEATS[1], scene="He walks to the window.")]
        # pronoun is the builder's argument (build_continuation_request **kwargs -> every beat's prompt build)
        graph, _, _ = _continuation(beats=beats, resolved=_resolved(pronoun="he"), pronoun="he")
        b2 = graph["c2"]["inputs"]["prompt"]
        self.assertIn("and he is still in the same place", b2)     # mid-sentence: lowercase
        self.assertIn("He keeps his exact voice", b2)              # sentence-initial: capitalised
        self.assertNotIn("and She is", b2)

    def test_identity_survives_on_every_beat(self):
        graph, _, _ = _continuation()
        for key in ("c0", "c2"):
            prompt = graph[key]["inputs"]["prompt"]
            self.assertIn("The face is the exact identity of Emilia Clarke", prompt)
            self.assertEqual(prompt.count("exact identity of Emilia Clarke"), 1)  # no self-name doubling


class TestContinuationFrameMath(unittest.TestCase):
    """The two rules this lane owns: the 17k + 5 grid and the 243-frame sampled-window ceiling."""

    def test_layout_arithmetic(self):
        lay = br.continuation_layout(192, 187)
        self.assertEqual((lay["base_frames"], lay["extension_frames"], lay["overlap_frames"]), (192, 187, 22))
        self.assertEqual((lay["window_frames"], lay["total_frames"]), (209, 379))
        self.assertAlmostEqual(lay["total_seconds"], 379 / 24, 4)
        self.assertEqual(lay["mode"], "native_latent_tail_continuation")

    def test_window_over_the_measured_ceiling_is_rejected(self):
        # 22 + 221 = 243 is the largest window measured on this 16 GB card; nothing above it is sampled here
        self.assertEqual(br.continuation_layout(192, 221)["window_frames"], 243)
        for ext in (238, 408):
            with self.subTest(ext=ext):
                with self.assertRaises(ValueError):
                    br.continuation_layout(192, ext)

    def test_off_grid_base_and_bad_extension_are_rejected(self):
        for base, ext in ((77, 85), (193, 187), (192, 180), (192, 0)):
            with self.subTest(base=base, ext=ext):
                with self.assertRaises(ValueError):
                    br.continuation_layout(base, ext)

    def test_chain_keeps_beat_1_and_extends_the_cumulative_latent(self):
        plan = br.plan_continuation_chain([192, 192])
        self.assertEqual(plan[0]["frames"], 192)                     # beat 1: plain single generation
        self.assertFalse(plan[0]["is_continuation"])
        lay = plan[1]["layout"]
        self.assertEqual((lay["base_frames"], lay["extension_frames"], lay["window_frames"]), (192, 187, 209))
        self.assertEqual(plan[1]["frames"], lay["total_frames"])

    def test_chain_window_never_exceeds_the_ceiling_for_any_request(self):
        for beats in ([192, 192], [243, 243], [192, 500], [192, 17, 17], [73, 73, 73, 73]):
            with self.subTest(beats=beats):
                plan = br.plan_continuation_chain(beats)
                self.assertEqual(len(plan), len(beats))
                self.assertEqual(sum(1 for p in plan if p["is_continuation"]), len(beats) - 1)
                for step in plan[1:]:
                    lay = step["layout"]
                    self.assertLessEqual(lay["window_frames"], br.CONTINUATION_WINDOW_MAX_FRAMES)
                    self.assertEqual(lay["window_frames"] % 17, 5)  # the grid the window node validates
                    self.assertEqual(lay["base_frames"] % 17, 5)

    def test_chain_needs_two_beats(self):
        with self.assertRaises(ValueError):
            br.plan_continuation_chain([192])


class TestContinuationGraphWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph, cls.prompt_all, cls.plan = _continuation()
        g = cls.graph
        # every sampled beat after the first must be reached through its own continuation chain, and the
        # graph must carry one output
        cls.beat2_chain = ["c2", "c2_refapply", "c2_gen", "c2_tail", "c2_guider", "c2_samp", "c2_append"]

    def test_beat_one_is_a_plain_single_generation_with_the_start_photo(self):
        g = self.graph
        self.assertEqual(g["c0"]["class_type"], "MiniMaxH3ReferenceToVideo")
        self.assertEqual(g["c0"]["inputs"]["length"], 192)
        # the photo reaches beat 1 through the guide node, as the frozen template wires it
        self.assertEqual(g["add_guide"]["inputs"]["image"], ["img_1", 0])
        self.assertEqual(g["add_guide"]["inputs"]["latent"], ["c0", 1])
        self.assertEqual(g["add_guide"]["inputs"]["frame_idx"], 0)
        self.assertEqual(g["refapply"]["inputs"]["conditioning"], ["add_guide", 0])

    def test_beat_two_wires_the_installed_continuation_nodes_in_order(self):
        g = self.graph
        self.assertEqual(g["c2_gen"]["class_type"], "MiniMaxH3GuidedContinuationWindow")
        self.assertEqual(g["c2_tail"]["class_type"], "MiniMaxH3LatentTailGuide")
        self.assertEqual(g["c2_samp"]["class_type"], "SamplerCustomAdvanced")
        self.assertEqual(g["c2_append"]["class_type"], "MiniMaxH3AppendContinuation")
        # beat 2 continues beat 1's SAMPLED AV latent (s0_samp output 0), as installed guided_continuation.json
        # wires it; c0 output 1 is the unseeded latent and is never the base of a continuation.
        self.assertEqual(g["c2_gen"]["inputs"],
                         {"previous_av_latent": ["s0_samp", 0], "overlap_frames": 22, "extension_frames": 187})
        self.assertEqual(g["c2"]["inputs"]["length"], ["c2_gen", 1])  # the node docs: window_length feeds length
        self.assertEqual(g["c2_tail"]["inputs"], {
            "positive": ["c2_refapply", 0], "previous_av_latent": ["s0_samp", 0],
            "target_av_latent": ["c2_gen", 0], "overlap_video_tokens": ["c2_gen", 2],
            "overlap_audio_tokens": ["c2_gen", 3]})
        self.assertEqual(g["c2_samp"]["inputs"]["latent_image"], ["c2_gen", 0])
        self.assertEqual(g["c2_append"]["inputs"], {
            "previous_av_latent": ["s0_samp", 0], "sampled_window": ["c2_samp", 0],
            "overlap_video_tokens": ["c2_gen", 2], "overlap_audio_tokens": ["c2_gen", 3],
            # the window node reports 0 unused tokens, so the completed latent is kept as-is
            "transition_video_tokens": ["c2_gen", 4], "transition_audio_tokens": ["c2_gen", 5]})

    def test_beat_two_has_no_start_photo_on_its_chain(self):
        g = self.graph
        # nothing in beat 2's chain may reference the photo: the latent tail guides frame 0
        for key in self.beat2_chain:
            refs = [v for v in g[key]["inputs"].values() if isinstance(v, list) and v and v[0] in ("img_1", "add_guide")]
            self.assertEqual(refs, [])
        self.assertEqual(g["c2_refapply"]["inputs"]["conditioning"], ["c2", 0])
        self.assertEqual(g["c2_tail"]["inputs"]["positive"], ["c2_refapply", 0])
        # the only photo nodes in the graph are beat 1's
        photo_nodes = {k for k, n in g.items()
                       if n["class_type"] in ("LoadImage", "MiniMaxH3AddGuide")}
        self.assertEqual(photo_nodes, {"img_1", "add_guide"})

    def test_refmod_is_loaded_once_and_applied_on_every_beat(self):
        g = self.graph
        self.assertEqual([k for k, n in g.items() if n["class_type"] == "MiniMaxH3RefModsLoader"], ["refmods"])
        self.assertEqual(sorted(k for k, n in g.items() if n["class_type"] == "MiniMaxH3RefModApply"),
                         ["c2_refapply", "refapply"])
        slots = {k: v for k, v in g["refmods"]["inputs"].items() if k.startswith("mod_")}
        self.assertEqual(slots["mod_1"], REFMOD_ID)
        self.assertEqual([v for k, v in slots.items() if k != "mod_1"], ["(none)"] * 7)  # one identity RefMod
        for key in ("refapply", "c2_refapply"):
            self.assertEqual(g[key]["inputs"]["mods"], ["refmods", 0])
            self.assertEqual(g[key]["inputs"]["retention"], 1.0)

    def test_one_seed_one_guider_chain_one_output(self):
        g = self.graph
        self.assertEqual([k for k, n in g.items() if n["class_type"] == "RandomNoise"], ["noise"])
        self.assertEqual(g["noise"]["inputs"]["noise_seed"], 51083610)
        self.assertEqual(g["c2_samp"]["inputs"]["noise"], ["noise", 0])   # one seed for the whole clip
        self.assertEqual(g["c2_guider"]["inputs"]["conditioning"], ["c2_tail", 0])  # not raw conditioning
        self.assertEqual(g["c2_samp"]["inputs"]["guider"], ["c2_guider", 0])
        self.assertEqual([k for k, n in g.items() if n["class_type"] == "SaveVideo"], ["save"])
        self.assertEqual(g["s0_sep"]["inputs"]["av_latent"], ["c2_append", 0])  # only the joined latent decodes
        self.assertEqual(g["dec_v"]["inputs"]["samples"], ["s0_sep", 0])
        self.assertEqual(g["dec_a"]["inputs"]["samples"], ["s0_sep", 1])
        self.assertEqual(g["mkvid"]["inputs"]["images"], ["dec_v", 0])
        self.assertEqual(g["save"]["inputs"]["video"], ["mkvid", 0])

    def test_beat_two_keeps_the_locked_sampling(self):
        g = self.graph
        for key in ("c2_samp", "s0_samp"):
            self.assertEqual(set(g[key]["inputs"]), {"guider", "latent_image", "noise", "sampler", "sigmas"})
            self.assertEqual(g[key]["inputs"]["sampler"], ["ksel", 0])
            self.assertEqual(g[key]["inputs"]["sigmas"], [f"{key.replace('_samp', '')}_sched", 0])
        self.assertEqual(g["c2_sched"]["inputs"],
                         {"denoise": 1.0, "model": ["m_shift", 0], "scheduler": "simple", "steps": 8})
        self.assertEqual(g["c2_sched"]["inputs"]["steps"], g["s0_sched"]["inputs"]["steps"])
        self.assertEqual(g["c2_guider"]["inputs"]["model"], g["s0_guide"]["inputs"]["model"])

    def test_locked_model_dials_survive_on_the_continuation_graph(self):
        g = self.graph
        self.assertEqual(g["unet"]["inputs"]["unet_name"], "10Eros_Max_h3_8stepTURBO_beta7_int8HQ.safetensors")
        self.assertEqual(g["clip"]["inputs"]["type"], "minimax")
        self.assertEqual(g["m_shift"]["inputs"]["shift_video"], 12.0)   # video shift, locked
        self.assertEqual(g["m_shift"]["inputs"]["shift_audio"], 3.0)    # audio shift, locked
        self.assertEqual(g["m_vsa"]["inputs"]["selection.keep_percent"], 10)  # 90% sparsity
        self.assertEqual(g["m_vsa"]["inputs"]["selection"], "vsa")
        self.assertEqual(g["m_attn"]["inputs"]["attention"], "comfy kitchen attention")
        self.assertEqual(g["ksel"]["inputs"]["sampler_name"], "euler")
        self.assertEqual(g["c0"]["inputs"]["ref_image_size"], "match")
        self.assertEqual(g["c2"]["inputs"]["ref_image_size"], "match")  # same dial on every beat
        self.assertEqual((g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]), (768, 1344))
        self.assertEqual((g["c2"]["inputs"]["width"], g["c2"]["inputs"]["height"]), (768, 1344))
        self.assertEqual(g["mkvid"]["inputs"]["fps"], 24)
        self.assertEqual(g["save"]["inputs"]["format"], "auto")

    def test_three_beats_chain_the_cumulative_latents(self):
        beats = [{"scene": "s one", "end_action": "a1", "images": [START_IMAGE]},
                 {"scene": "s two", "end_action": "a2"},
                 {"scene": "s three", "end_action": "a3"}]
        graph, _, plan = _continuation(beats=beats)
        # beat 2 chains off beat 1's sampled latent; every later beat chains off the cumulative append node
        self.assertEqual(graph["c2_gen"]["inputs"]["previous_av_latent"], ["s0_samp", 0])
        self.assertEqual(graph["c3_gen"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(graph["c3_tail"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(graph["c3_append"]["inputs"]["previous_av_latent"], ["c2_append", 0])
        self.assertEqual(graph["s0_sep"]["inputs"]["av_latent"], ["c3_append", 0])
        self.assertLess(graph["c3_gen"]["inputs"]["extension_frames"], 221)  # the cap binds past 379 cumulative
        beats_plan = plan["beats"]
        self.assertEqual(beats_plan[-1]["frames"],
                         beats_plan[0]["frames"] + sum(p["layout"]["extension_frames"] for p in beats_plan[1:]))


class TestContinuationObjective(unittest.TestCase):
    def test_run_queue_expects_the_cumulative_clip_not_the_beat_1_length(self):
        graph, _, plan = _continuation()
        self.assertEqual(run_queue.graph_expect(graph), (379, (768, 1344)))
        self.assertNotEqual(graph["c0"]["inputs"]["length"], 379)
        self.assertEqual(plan["total_frames"], 379)
        self.assertFalse(plan["stitched"])
        self.assertEqual(plan["clip_count"], 2)

    def test_single_shot_expectation_is_untouched(self):
        graph, _ = _single_shot()
        self.assertEqual(run_queue.graph_expect(graph), (192, (768, 1344)))


class TestSingleShotUnchanged(unittest.TestCase):
    def test_single_shot_graph_has_no_continuation_nodes(self):
        graph, prompt = _single_shot()
        types = {n["class_type"] for n in graph.values()}
        self.assertFalse(types & set(br.CONTINUATION_NODE_TYPES))
        self.assertNotIn("The shot continues from the last seen moment", prompt)
        self.assertEqual([k for k, n in graph.items() if n["class_type"] == "MiniMaxH3RefModApply"], ["refapply"])
        self.assertEqual(run_queue.graph_expect(graph), (192, (768, 1344)))

    def test_start_image_on_a_continuation_beat_is_refused(self):
        with self.assertRaises(ValueError):
            br.build_parody_request(_resolved(), 51083610, "test_cont", frames=192,
                                    scene="Cassie walks to the window.", continuation=True, images=[START_IMAGE])

    def test_one_beat_is_a_single_shot_not_a_continuation(self):
        with self.assertRaises(ValueError):
            br.build_continuation_request(_resolved(), 51083610, "test_cont", [BEATS[0]], frames=192)


if __name__ == "__main__":
    unittest.main(verbosity=2)
