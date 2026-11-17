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
from unittest import mock

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
        self.assertEqual(plan["overlap_frames"], 22)  # asked for
        self.assertEqual(plan["overlap_frames_applied"], [39, 22])  # each beat's audio-aligned 17k + 5 value
        self.assertEqual([b["frames"] for b in plan["beats"]], [192, 379, 566])
        b2_lay, b3_lay = (b["layout"] for b in plan["beats"][1:])
        # c2-samp fix: every continuation window's allocated audio length must equal the official
        # temporal_shape(window) length that MiniMaxH3ReferenceToVideo conditions for that window_length. Off a
        # 192-frame tail the asked 22/187 gives 349 tokens for a 348-token 209f window, and that beat's sampler
        # fails (live run prompt_id 26a05372: shape mismatch [2000, 32] vs [2074, 32] at c2_samp). Beat 3 from the
        # 379-frame latent keeps 22. The visible 192 + 187 + 187 = 566 frames are unchanged.
        self.assertEqual((b2_lay["overlap_frames"], b2_lay["window_frames"]), (39, 226))
        self.assertEqual((b3_lay["overlap_frames"], b3_lay["window_frames"]), (22, 209))
        for lay in (b2_lay, b3_lay):
            self.assertLessEqual(lay["window_frames"], br.CONTINUATION_WINDOW_MAX_FRAMES)
            self.assertEqual(lay["window_audio_t"], lay["window_audio_official_t"])
            self.assertTrue(br.continuation_window_audio_is_aligned(
                lay["base_frames"], lay["overlap_frames"], lay["extension_frames"]))
        self.assertEqual(g["c2_gen"]["inputs"]["overlap_frames"], 39)
        self.assertEqual(g["c3_gen"]["inputs"]["overlap_frames"], 22)
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

    # c2_samp cond_audio (Derrick 2026-11-15): a voice-reference RefMod on a latent-tail beat is the one shape the
    # runtime cannot pack. The poolclub voice RefMod is an audio latent [1, 32, 2, 1000] (refmod_meta latent_t=1000,
    # 25.0 s at 32 kHz) -> pack_audio gives 2*1000 = 2000 value rows, and PackedLayout reserves 2*latent_t slots for
    # it: a plain beat (beat 1) is square, and s0_samp sampled it for 66 s. A continuation beat adds one more slot
    # group - MiniMaxH3LatentTailGuide appends the previous window's audio tail as a keyframe of
    # overlap_audio_t = audio_t(base) - audio_t(base - overlap), 65 rows x2 at base 192 / overlap 39 and 37 x2 at
    # base 379 / overlap 22 - and the RefMod's value tensor never grows into those slots:
    #   value [2000, 32] vs indexing result [2130, 32] (c2_samp, prompt_id 332f0637) and [2074, 32] (beat 3).
    # All 44 continuation graphs in C:\AI\community\runs that produced an mp4 load no audio RefMod on the tail beat;
    # the only one that carried it has no output. So the voice reference stays on beat 1 and the voice carries on
    # the tail, which is beat 1's sampled audio. The visible length is untouched: 192 + 187 + 187 = 566 frames.
    VOICE_REFMOD = "minimaxh3_oc_poolclub_v1_refmod_audio"
    LOOK_REFMOD = "minimaxh3_oc_poolclub_v1_refmod_visual"

    # 2026-11-16 voice fix: the short value tensor was ComfyUI-H3-Multishot's extra_conds wrapper dropping the tail
    # keyframe audio (upstream issue #23). With the community fix the runtime packs 2*voice + 2*tail rows, equal to
    # reserved, so the full 25 s voice RefMod stays on every beat. Without it (runtime_packs_tail_audio False) the
    # builder falls back to the 8ee347e voice-off continuation beats.
    def test_voice_refmod_falls_back_to_beat_one_only_when_runtime_drops_tail_audio(self):
        base = _base_graph()
        base["refmods"]["inputs"]["mod_1"], base["refmods"]["inputs"]["mod_2"] = self.VOICE_REFMOD, self.LOOK_REFMOD
        with mock.patch.object(br, "runtime_packs_tail_audio", return_value=False):
            g, _, plan = _build(base_graph=base)
        for n in (2, 3):
            self.assertEqual(g[f"c{n}_refapply"]["inputs"]["mods"], [f"c{n}_refmods", 0])
            self.assertEqual(g[f"c{n}_refmods"]["inputs"]["mod_1"], "(none)")
        rows = {r["node"]: r for r in plan["cond_audio_rows"]}
        for n, overlap_audio_t in ((2, 65), (3, 37)):
            r = rows[f"c{n}_refapply"]
            self.assertEqual((r["packed_cond_audio_rows"], r["layout_cond_audio_rows"]), (0, 2 * overlap_audio_t))
            self.assertTrue(r["ok"])

    def test_runtime_packs_tail_audio_reads_the_multishot_wrapper(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "h3_avbank_probe.py"
            self.assertTrue(br.runtime_packs_tail_audio(str(p)))  # no wrapper: core merges both
            p.write_text('        if aud:\n            payload["cond_audio_latents"] = aud\n', encoding="utf-8")
            self.assertFalse(br.runtime_packs_tail_audio(str(p)))  # unpatched upstream v2.7.2
            p.write_text('        payload["cond_audio_latents"] = (\n            [k["audio_latent"] for k in kf\n'
                         '             if k.get("audio_latent") is not None]\n'
                         '            + [r["audio_latent"] for r in refs\n'
                         '               if r.get("audio_latent") is not None])\n', encoding="utf-8")
            self.assertTrue(br.runtime_packs_tail_audio(str(p)))  # jalberty2018 / issue #23 fix

    def test_voice_refmod_is_on_every_beat_and_cond_audio_rows_pack_refmod_plus_tail(self):
        base = _base_graph()
        base["refmods"]["inputs"]["mod_1"], base["refmods"]["inputs"]["mod_2"] = self.VOICE_REFMOD, self.LOOK_REFMOD
        with mock.patch.object(br, "runtime_packs_tail_audio", return_value=True):
            g, prompt_all, plan = _build(base_graph=base)
        self.assertEqual(plan["total_frames"], 566)  # the fix did not touch the visible length
        # beat 1 keeps the pair on the shared loader: no window, no tail keyframe, so its 2000 packed rows fill the
        # 2000 slots its layout reserves (that beat is what s0_samp sampled in the run that died at c2_samp)
        self.assertEqual(g["refapply"]["inputs"]["mods"], ["refmods", 0])
        self.assertEqual(g["refmods"]["inputs"]["mod_1"], self.VOICE_REFMOD)
        for n in (2, 3):
            # the voice-fix state: every beat's RefModApply reads the shared loader (voice + visual RefMod)
            self.assertEqual(g[f"c{n}_refapply"]["inputs"]["mods"], ["refmods", 0], f"beat {n}: voice dropped")
            self.assertNotIn(f"c{n}_refmods", g)
        # the dry row math a render cannot pass by padding: a beat packs cond audio only when its packed rows equal
        # the reserved slots (beat 1: 2000 = 2000); a latent-tail beat packs NO cond-audio block, so no indexed
        # assignment is attempted - the state all 44 continuation graphs that produced an mp4 are in.
        rows = {r["node"]: r for r in plan["cond_audio_rows"]}
        self.assertEqual(set(rows), {"refapply", "c2_refapply", "c3_refapply"})
        b1 = rows["refapply"]
        self.assertEqual((b1["packed_cond_audio_rows"], b1["layout_cond_audio_rows"]),
                         (2 * br.MEASURED_AUDIO_REFMOD_LATENT_T, 2 * br.MEASURED_AUDIO_REFMOD_LATENT_T))
        self.assertTrue(b1["cond_audio_block"] and b1["ok"], b1["error_signature"])
        for n, overlap_audio_t in ((2, 65), (3, 37)):
            r = rows[f"c{n}_refapply"]
            self.assertEqual(r["audio_refmods"], [self.VOICE_REFMOD])  # the full 25 s voice on every beat
            self.assertEqual(r["visual_refmods"], [self.LOOK_REFMOD])  # identity is still conditioned every beat
            self.assertEqual(r["keyframe_cond_audio_rows"], 2 * overlap_audio_t)  # the tail's reserved slots
            want = 2 * br.MEASURED_AUDIO_REFMOD_LATENT_T + 2 * overlap_audio_t  # 2130 (beat 2), 2074 (beat 3)
            self.assertEqual((r["packed_cond_audio_rows"], r["layout_cond_audio_rows"]), (want, want))
            self.assertTrue(r["cond_audio_block"] and r["tail_audio_in_value"])
            self.assertTrue(r["ok"], f"beat {n}: {r['error_signature']}")
        self.assertEqual([rows[k]["packed_cond_audio_rows"] for k in ("refapply", "c2_refapply", "c3_refapply")],
                         [2000, 2130, 2074])
        for r in rows.values():  # the live failure shape appears on no beat of the built graph
            self.assertNotEqual((r["packed_cond_audio_rows"], r["layout_cond_audio_rows"]), (2000, 2074))
            self.assertNotEqual((r["packed_cond_audio_rows"], r["layout_cond_audio_rows"]), (2000, 2130))
        # the pre-fix shape, in the runtime's own words (live prompt_id 332f0637: 2000 vs 2000 + 2*65 and 2*37)
        self.assertEqual(br.continuation_cond_audio_rows([br.MEASURED_AUDIO_REFMOD_LATENT_T], [65], tail_in_value=False),
                         {"refmod_cond_audio_rows": 2000, "keyframe_cond_audio_rows": 130,
                          "packed_cond_audio_rows": 2000, "layout_cond_audio_rows": 2130, "row_delta": 130,
                          "cond_audio_block": True, "tail_audio_in_value": False, "ok": False,
                          "error_signature": "value tensor of shape [2000, 32] cannot be broadcast "
                                             "to indexing result of shape [2130, 32]"})
        self.assertFalse(br.continuation_cond_audio_rows([br.MEASURED_AUDIO_REFMOD_LATENT_T], [37],
                                                         tail_in_value=False)["ok"])
        self.assertTrue(br.continuation_cond_audio_rows([br.MEASURED_AUDIO_REFMOD_LATENT_T], [], tail_in_value=False)["ok"])
        self.assertTrue(br.continuation_cond_audio_rows([], [65], tail_in_value=False)["ok"])
        # the fixed runtime: packed == reserved for the full 25 s voice on both continuation beats
        for oat, want in ((65, 2130), (37, 2074)):
            r = br.continuation_cond_audio_rows([br.MEASURED_AUDIO_REFMOD_LATENT_T], [oat], tail_in_value=True)
            self.assertEqual((r["packed_cond_audio_rows"], r["layout_cond_audio_rows"], r["ok"]), (want, want, True))  # the wired state: the tail keyframe alone
        # A 920-token (23 s) trim is still a mismatch: packed 1840 vs reserved 1970 / 1914.
        # Do not treat layout_rows <= 2000 as ok.
        t23 = br.CONTINUATION_VOICE_REFMOD_LATENT_T
        self.assertEqual((t23, 2 * t23 + 2 * 65, 2 * t23 + 2 * 37), (920, 1970, 1914))
        self.assertEqual(br.continuation_cond_audio_rows([t23], [65], tail_in_value=False),
                         {"refmod_cond_audio_rows": 1840, "keyframe_cond_audio_rows": 130,
                          "packed_cond_audio_rows": 1840, "layout_cond_audio_rows": 1970, "row_delta": 130,
                          "cond_audio_block": True, "tail_audio_in_value": False, "ok": False,
                          "error_signature": "value tensor of shape [1840, 32] cannot be broadcast "
                                             "to indexing result of shape [1970, 32]"})
        self.assertFalse(br.continuation_cond_audio_rows([t23], [37], tail_in_value=False)["ok"])
        # prompt text is unchanged by the graph change (the allowed hashes of the live pack, live-12d0733)
        for i, node in enumerate(("c0", "c2", "c3"), start=1):
            self.assertIn(f"Marker A{i}", g[node]["inputs"]["prompt"])
            self.assertIn(f"Marker B{i}", g[node]["inputs"]["prompt"])
        # prompt text is not touched by the graph change: the same pack through the builder with and without a
        # voice reference gives byte-identical c0/c2/c3 prompts (the live pack's own check is the same comparison
        # against the approved dry-run graph, and its pack hashes 808424141FE88045 / 7115D0AE1CFBFA53 /
        # ED7BC54BD52A366E are the beat files, which this change never reads)
        g_plain, prompt_plain, _ = _build()
        self.assertEqual([g[n]["inputs"]["prompt"] for n in ("c0", "c2", "c3")],
                         [g_plain[n]["inputs"]["prompt"] for n in ("c0", "c2", "c3")])
        self.assertEqual(prompt_all, prompt_plain)


        g, _, plan = _build()
        for i, (authored, node) in enumerate(zip((BEAT1, BEAT2, BEAT3), ("c0", "c2", "c3")), start=1):
            sent = g[node]["inputs"]["prompt"]
            lead = plan["beat_leads"][i - 1]["lead_in"]
            probe = lead + " "
            if lead:
                self.assertEqual(sent.count(lead), 1, f"beat {i}: the lead-in is not a single inserted block")
            stripped = sent.replace(probe, "", 1) if lead else sent
            # Continuation-window prompts carry window-local clocks; authored beat-file clocks may differ.
            # Shot wording is otherwise unchanged (pack beat files stay hash-identical).
            def _clock_neutral(s: str) -> str:
                return re.sub(r"At \d{1,2}:[0-5]\d(?:\.\d{1,3})?,", "At <CLOCK>,", s)
            self.assertEqual(_clock_neutral(stripped), _clock_neutral(authored.strip()),
                             f"beat {i}: the route changed the authored prompt text beyond shot clocks")
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

    def test_continuation_shot_clocks_are_window_local_and_globals_are_reported(self):
        g, _, plan = _build()
        # Fixture authored cut is 00:03.250 = 78f. Beat 2 applies overlap 39 (requested 22), so
        # window-local = 78 + 17 = 95 = 00:03.958; global = 192 + 95 - 39 = 248.
        # Beat 3 keeps overlap 22, so the clock is unchanged at 00:03.250; global = 379 + 78 - 22 = 435.
        self.assertEqual(plan["beats"][1]["shot_frames"], [248])
        self.assertEqual(plan["beats"][2]["shot_frames"], [435])
        b2 = g["c2"]["inputs"]["prompt"]
        self.assertIn("At 00:03.958,", b2)
        self.assertNotIn("At 00:10.333,", b2)
        b3 = g["c3"]["inputs"]["prompt"]
        self.assertIn("At 00:03.250,", b3)
        cuts2 = plan["beats"][1]["shot_clocks"]["cuts"]
        first = next(iter(cuts2.values()))
        self.assertEqual(first["window_local_frames"], 95)
        self.assertEqual(first["global_frames"], 248)
        self.assertEqual(first["window_local_clock"], "00:03.958")

    def test_prompt_all_lists_every_beat(self):
        _, prompt_all, plan = _build()
        self.assertEqual(len(plan["beats"]), 3)
        for i in (1, 2, 3):
            self.assertIn(f"===== beat {i} =====", prompt_all)
        self.assertIn("Marker A3", prompt_all)


if __name__ == "__main__":
    unittest.main()
