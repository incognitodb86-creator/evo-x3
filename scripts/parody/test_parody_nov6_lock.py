"""Nov 6 2026 pipeline lock (Derrick t213u): single-pass native 768x1344 b2_refmod + beta7 int8HQ +
INDEX + RefMod is the default (no photo needed), the clean R37 paste (no overall_soundscape /
no_dubs / <scenedirect>, `<d>[English] words.</d>` inline in [Shot 1]), Character (Actor) naming,
natural `action` blocking, and the standalone `--ref-audio` <Audio 1> voice-timbre wiring
(LoadAudio -> c0 `ref_audios.ref_audio_1`, the flat V3 Autogrow key, same form as
`ref_images.ref_image_1`). CPU only: no GPU, network, or process launch.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import resolve
import build_request
from build_request import (
    DEFAULT_REFMOD_TEMPLATE,
    DEFAULT_UNET,
    build_parody_request,
    clean_dialogue,
    format_parody_prompt,
    resolve_ref_audio,
)
from run_record import build_assets_record
from test_parody_reflora import INDEX_BAD_MD, INDEX_MD, BIO, make_hybrid, make_refmod

LINE = "Stay a second, the game is over, and I am just getting started."
ACTION = "leans casually against the polished wood bar counter, weight on one hip, one hand resting on the bar"
BANNED = ("overall_soundscape", "no_dubs", "<scenedirect>", "</scenedirect>", "[English in",
          "natural speaking voice")


class Nov6Lock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="nov6_")
        root = Path(self.tmp.name)
        self.index = root / "index"
        self.index.mkdir()
        (self.index / "INDEX.md").write_text(INDEX_MD, encoding="utf-8")
        (self.index / "INDEX_BAD.md").write_text(INDEX_BAD_MD, encoding="utf-8")
        self.refmods = root / "refmods"
        self.refmods.mkdir()
        self.rdir = root / "reflora"
        self.rdir.mkdir()
        self.pool = root / "approved_characters" / "HOOTERS01"
        self.pool.mkdir(parents=True)
        self.cond_src = self.pool / "hoot_start.jpg"
        self.cond_src.write_bytes(b"fake-cond-bytes-hoot-start")
        self.comfy_input = root / "ComfyUI" / "input"
        self.comfy_input.mkdir(parents=True)
        (self.comfy_input / "hoot_start.jpg").write_bytes(self.cond_src.read_bytes())
        self.assets = root / "assets" / "ref_audios"
        self.assets.mkdir(parents=True)
        self.voice = self.assets / "voice_ref.wav"
        self.voice.write_bytes(b"RIFF fake wav bytes for the ref audio gate")
        make_refmod(self.refmods / "minimaxh3_meganfox_v1_refmod.safetensors", 3)

    def tearDown(self):
        self.tmp.cleanup()

    def _resolve(self, character="Jennifer Check", actor="Megan Fox"):
        return resolve.resolve_identities(
            {"names": [actor or character], "character": character, "actor": actor, "description": BIO},
            index_dir=self.index, refmods_dir=self.refmods, reflora_dir=None)

    def _build(self, **kw):
        return build_parody_request(
            self._resolve(), seed=51083601, prefix="community/t/clip", frames=124,
            dialogue=LINE, action=ACTION, image=None, cond_source=None,
            approved_pool=self.pool.parent, comfy_input=self.comfy_input, **kw)

    # ---- default mode: single-pass, no photo, INDEX + RefMod -------------------------------
    def test_default_graph_mode_is_single_pass_in_both_clis(self):
        import inspect
        self.assertEqual(inspect.signature(build_parody_request).parameters["graph_mode"].default,
                         "single-pass")
        import submit_parody_run
        self.assertEqual(inspect.signature(submit_parody_run.submit_parody_job)
                         .parameters["graph_mode"].default, "single-pass")

    def test_single_pass_no_photo_refmod_only(self):
        g, prompt, cond = self._build()
        classes = {n["class_type"] for n in g.values()}
        self.assertNotIn("LoadImage", classes)
        self.assertNotIn("MiniMaxH3AddGuide", classes)
        self.assertNotIn("LoadAudio", classes)
        self.assertNotIn("ref_images.ref_image_1", g["c0"]["inputs"])
        self.assertNotIn("<Picture 1>", prompt)
        self.assertEqual((g["c0"]["inputs"]["width"], g["c0"]["inputs"]["height"]), (768, 1344))
        self.assertEqual(g["c0"]["inputs"]["length"], 124)
        self.assertEqual(g["unet"]["inputs"]["unet_name"], DEFAULT_UNET)
        self.assertEqual(g["refmods"]["inputs"]["mod_1"], "minimaxh3_meganfox_v1_refmod")
        self.assertFalse([k for k, v in g.items() if "lora" in v["class_type"].lower()])
        self.assertIsNone(cond["cond_sha256"])
        self.assertIsNone(cond["ref_audio_sha256"])

    def test_single_pass_photo_still_gated(self):
        with self.assertRaises(ValueError):
            build_parody_request(self._resolve(), seed=1, prefix="community/t/clip",
                                 image="not_in_pool.jpg", cond_source=None,
                                 approved_pool=self.pool.parent, comfy_input=self.comfy_input)

    def test_single_pass_hybrid_still_requires_cond(self):
        make_hybrid(self.rdir / "minimaxh3_meganfox_v1_reflora.safetensors",
                    "minimaxh3_meganfox_v1_refmod", 3)
        res = resolve.resolve_identities(
            {"names": ["Megan Fox"], "character": "Jennifer Check", "actor": "Megan Fox",
             "description": BIO}, index_dir=self.index, refmods_dir=self.refmods, reflora_dir=self.rdir)
        with self.assertRaises(ValueError):
            build_parody_request(res, seed=1, prefix="community/t/clip", image=None, cond_source=None,
                                 approved_pool=self.pool.parent, comfy_input=self.comfy_input)

    # ---- clean R37 paste -------------------------------------------------------------------
    def test_clean_r37_paste(self):
        _, prompt, _ = self._build()
        for b in BANNED:
            self.assertNotIn(b, prompt)
        self.assertIn("<Subject 1> Jennifer Check (Megan Fox), " + BIO, prompt)
        self.assertIn(f"<Subject 1> (S1) looks into the lens and says, <d>[English] {LINE}</d> "
                      "Her speaking voice is close, clear, and natural in the foreground.", prompt)
        shot = [l for l in prompt.splitlines() if l.startswith("[Shot 1]")]
        self.assertEqual(len(shot), 1)
        self.assertIn(ACTION, shot[0])
        self.assertIn("<d>[English]", shot[0], "speech rides inline in [Shot 1]")
        self.assertNotIn("PRIMARY MOTION", prompt)
        self.assertNotIn("<Audio", prompt)
        self.assertIn("summary:\n[reference generation] ", prompt)
        self.assertEqual(prompt.count("<d>"), 1)

    def test_dialogue_cleaning(self):
        self.assertEqual(clean_dialogue('"Stay a second, the game is over"'), "Stay a second, the game is over.")
        self.assertEqual(clean_dialogue("Are you coming?"), "Are you coming?")
        for bad in ("No speech, she smiles", "[sfx glass clink]", "(no dialogue)", "t=00.00 hello",
                    "<d>hi</d>", "room tone then hello", "(silent beat)"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    clean_dialogue(bad)
                with self.assertRaises(ValueError):
                    format_parody_prompt(self._resolve(), dialogue=bad)

    def test_single_name_keeps_plain_label(self):
        res = self._resolve(character="Jennifer Check", actor=None)
        prompt = format_parody_prompt(res, dialogue=LINE)
        self.assertNotIn("(Megan Fox)", prompt)

    # ---- --ref-audio <Audio 1> -------------------------------------------------------------
    def test_ref_audio_wired_graph_and_prompt(self):
        g, prompt, cond = self._build(ref_audio=str(self.voice), stage_ref_audio=True)
        self.assertEqual(g["ref_audio_1"], {"class_type": "LoadAudio",
                                            "inputs": {"audio": "ref_audios/voice_ref.wav"}})
        self.assertEqual(g["c0"]["inputs"]["ref_audios.ref_audio_1"], ["ref_audio_1", 0])
        self.assertEqual(g["c0"]["inputs"]["audio_vae"], ["avae", 0])
        self.assertTrue((self.comfy_input / "ref_audios" / "voice_ref.wav").is_file())
        self.assertEqual(len(cond["ref_audio_sha256"]), 64)
        self.assertEqual(cond["ref_audio_input_name"], "ref_audios/voice_ref.wav")
        self.assertIn("summary:\n[reference generation + audio reference] ", prompt)
        self.assertIn("<Audio 1> is the reference audio defining the exact vocal timbre, pitch, and "
                      "speaking cadence of <Subject 1>.", prompt)
        self.assertIn("<Audio 1>: reference - vocal timbre, pitch, and speaking cadence of <Subject 1>, "
                      "without copying the reference audio's spoken words.", prompt)
        self.assertIn(f"<d>[English] {LINE}</d> Her speaking voice follows the close, natural vocal "
                      "timbre and cadence of <Audio 1> in the foreground.", prompt)
        self.assertEqual(prompt.count("<Video 1>"), 1)
        for b in BANNED:
            self.assertNotIn(b, prompt)

    def test_ref_audio_recorded_in_assets(self):
        res = self._resolve()
        g, prompt, cond = build_parody_request(
            res, seed=1, prefix="community/t/clip", dialogue=LINE, image=None, cond_source=None,
            approved_pool=self.pool.parent, comfy_input=self.comfy_input,
            ref_audio=str(self.voice), stage_ref_audio=True)
        res["cond"] = cond
        a = build_assets_record(res, g)
        self.assertEqual(a["ref_audio_input_name"], "ref_audios/voice_ref.wav")
        self.assertEqual(a["ref_audio_source_path"], str(self.voice))
        self.assertEqual(len(a["ref_audio_sha256"]), 64)
        self.assertTrue(a["ref_audio_wired"])

    def test_ref_audio_fail_closed(self):
        with self.assertRaises(ValueError):
            resolve_ref_audio(r"C:\Users\derek\sydney\voice.wav", comfy_input=self.comfy_input,
                              stage_ref_audio=True)
        with self.assertRaises(ValueError):
            resolve_ref_audio(str(self.assets / "missing.wav"), comfy_input=self.comfy_input,
                              stage_ref_audio=True)
        bad_ext = self.assets / "voice.txt"
        bad_ext.write_text("x")
        with self.assertRaises(ValueError):
            resolve_ref_audio(str(bad_ext), comfy_input=self.comfy_input, stage_ref_audio=True)
        # not staged and not present under ComfyUI\input -> refuse
        with self.assertRaises(ValueError):
            resolve_ref_audio(str(self.voice), comfy_input=self.comfy_input, stage_ref_audio=False)

    def test_ref_audio_two_pass_parody_wires_every_reference_node(self):
        g, prompt, cond = self._build(graph_mode="two-pass-parody", ref_audio=str(self.voice),
                                      stage_ref_audio=True)
        r2v = [k for k, v in g.items() if v["class_type"] == "MiniMaxH3ReferenceToVideo"]
        self.assertIn("c0", r2v)
        for nid in r2v:
            self.assertEqual(g[nid]["inputs"]["ref_audios.ref_audio_1"], ["ref_audio_1", 0])


if __name__ == "__main__":
    unittest.main()
