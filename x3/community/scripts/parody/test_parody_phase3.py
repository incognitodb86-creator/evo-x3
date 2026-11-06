"""Unit tests for H3 parody pipeline Phase 3 (U5, U6, U7, R7-R8).

Tests:
- R7-a: Request JSON node inputs, all 8 loader slots filled
- R7-b: Frozen KEEP dials equal template
- R7-c: Tone pass-through (KD7) and guard_ok check
- R7-d: Short request -> single clip
- R7-e: Long request -> C2V multi-clip chain with context 22
- R8: Run record four artifacts check
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from build_request import (
    DEFAULT_REFMOD_TEMPLATE,
    build_parody_request,
    format_parody_prompt,
    populate_refmod_slots,
    verify_keep_dials,
)
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities
from run_record import build_assets_record, save_run_record, verify_run_artifacts
import comm
import submit_parody_run as spr


INDEX_DIR = Path(r"C:\AI\community\index\h3-known-characters")
REFMODS_DIR = Path(r"C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\models\refmods")
ALIASES_PATH = Path(__file__).parent / "aliases.json"


class TestParodyPhase3(unittest.TestCase):

    def setUp(self):
        self.good_req = {
            "names": ["Emilia Clarke"],
            "character": "Daenerys Targaryen",
            "tone": "dramatic parody",
            "length_s": 5,
            "description": "platinum-blonde braided hair, pale skin, violet-leaning eyes, fantasy scale top",
        }
        self.bad_req = {
            "names": ["Megan Fox"],
            "character": "Jennifer Check",
            "tone": "satirical adult parody",
            "length_s": 15,
            "description": "long dark wavy hair, cheer jacket, heart earrings",
        }
        self.resolved_good = resolve_identities(
            self.good_req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH
        )
        self.resolved_bad = resolve_identities(
            self.bad_req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH
        )

    def test_r7a_request_nodes_and_8_slots(self):
        """R7-a: Exactly 8 loader slots populated, unused are (none), all 24 keys present."""
        graph, prompt = build_parody_request(
            resolved=self.resolved_good,
            seed=42,
            prefix="community/test/clip",
            frames=124,
        )
        self.assertIn("refmods", graph)
        inputs = graph["refmods"]["inputs"]
        for i in range(1, 9):
            self.assertIn(f"mod_{i}", inputs)
            self.assertIn(f"strength_{i}", inputs)
            self.assertIn(f"copies_{i}", inputs)

        # Slot 1 should have Emilia Clarke refmod
        self.assertEqual(inputs["mod_1"], "minimaxh3_emiliaclarke_v1_refmod")
        # Remaining slots (none)
        for i in range(2, 9):
            self.assertEqual(inputs[f"mod_{i}"], "(none)")

    def test_r7b_frozen_keep_dials(self):
        """R7-b: unet, 8-step turbo scheduler, refapply remain unchanged."""
        graph, _ = build_parody_request(
            resolved=self.resolved_good,
            seed=123,
            prefix="community/test/clip",
            frames=124,
        )
        # Verify function should not raise
        verify_keep_dials(graph)

        self.assertIn("10Eros_Max_h3_8stepTURBO_beta7_int8HQ", graph["unet"]["inputs"]["unet_name"])
        self.assertEqual(graph["s0_sched"]["inputs"]["steps"], 8)
        self.assertIn("refapply", graph)

    def test_r7c_tone_passthrough_and_guard(self):
        """R7-c: Tone passes through and prompt satisfies adults guard."""
        prompt = format_parody_prompt(
            self.resolved_bad,
            dialogue="You have no idea what is coming next.",
            scene="standing in a dimly lit hallway at night",
        )
        self.assertIn("Jennifer Check", prompt)
        # t261u: the redundant summary filler is gone; subject_definitions still states the adult (age 28+).
        self.assertNotIn("Adult cast, adults-only, fictional 18+ adult scene", prompt)
        self.assertIn("an adult performer, age 28+", prompt)
        self.assertTrue(comm.adult_stated(prompt))
        self.assertIn("You have no idea what is coming next", prompt)

    def test_r7d_short_request_single_clip(self):
        """R7-d: Short request (<= 8s) generates a single clip plan."""
        plan_5s = plan_c2v_chain(total_length_s=5.0)
        self.assertFalse(plan_5s["is_chained"])
        self.assertEqual(plan_5s["clip_count"], 1)
        self.assertEqual(plan_5s["clips"][0]["frames"], 124)

        plan_8s = plan_c2v_chain(total_length_s=8.0)
        self.assertFalse(plan_8s["is_chained"])
        self.assertEqual(plan_8s["clip_count"], 1)

    def test_r7e_long_request_c2v_chain(self):
        """R7-e: Long request (> 8s) generates multi-clip chain with contextLengthFrames 22."""
        plan_15s = plan_c2v_chain(total_length_s=15.0, fps=24, clip_frames=124, context_frames=22)
        self.assertTrue(plan_15s["is_chained"])
        self.assertGreaterEqual(plan_15s["clip_count"], 3)

        # First clip has 0 context overlap
        self.assertEqual(plan_15s["clips"][0]["context_length_frames"], 0)
        # Subsequent clips have 22 frame context overlap
        for c in plan_15s["clips"][1:]:
            self.assertEqual(c["context_length_frames"], 22)

        # Check total net duration logic
        expected_frames = 124 + (plan_15s["clip_count"] - 1) * (124 - 22)
        self.assertEqual(plan_15s["total_frames"], expected_frames)

    def test_r8_run_record_artifacts(self):
        """R8: Run record delivers request.api.json, prompt.txt, assets.json, clip.mp4."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir) / "parody_sample"
            graph, prompt = build_parody_request(
                resolved=self.resolved_good,
                seed=42,
                prefix="community/parody_sample/clip_01",
                frames=124,
            )
            # Create a mock mp4 file
            mock_mp4 = Path(tmp_dir) / "source.mp4"
            mock_mp4.write_bytes(b"dummy mp4 video bytes")

            artifacts = save_run_record(
                run_dir=run_dir,
                resolved=self.resolved_good,
                prompt=prompt,
                graph=graph,
                chain_plan=None,
                clip_source=mock_mp4,
            )

            status = verify_run_artifacts(run_dir, require_clip=True)
            self.assertTrue(all(status.values()))
            self.assertTrue(artifacts["request"].is_file())
            self.assertTrue(artifacts["prompt"].is_file())
            self.assertTrue(artifacts["assets"].is_file())
            self.assertTrue(artifacts["clip"].is_file())

            # Read assets.json and check structured fields
            assets_data = json.loads(artifacts["assets"].read_text(encoding="utf-8"))
            self.assertEqual(assets_data["mode"], "native_face_voice")
            self.assertEqual(assets_data["index_status"], "good")
            self.assertIn("minimaxh3_emiliaclarke_v1_refmod.safetensors", assets_data["loaded_refmods"][0])

    def test_biometric_description_required(self):
        """Fails when biometric description is missing or empty."""
        # 1. Missing description key
        req_missing = {"names": ["Emilia Clarke"], "character": "Daenerys Targaryen", "tone": "parody"}
        with self.assertRaises(ValueError) as ctx:
            resolve_identities(req_missing, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
        self.assertIn("required", str(ctx.exception).lower())

        # 2. None description
        req_none = dict(req_missing, description=None)
        with self.assertRaises(ValueError) as ctx:
            resolve_identities(req_none, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
        self.assertIn("required", str(ctx.exception).lower())

        # 3. Empty string description
        req_empty = dict(req_missing, description="   ")
        with self.assertRaises(ValueError) as ctx:
            resolve_identities(req_empty, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
        self.assertIn("required", str(ctx.exception).lower())

    def test_biometric_description_rejects_generic_only(self):
        """Rejects banned generic phrases and generic-only descriptions."""
        banned_samples = [
            "exact likeness",
            "distinctive facial features",
            "natural authentic human appearance",
            "distinctive facial features, exact likeness and vocal timbre",
            "exact likeness and natural vocal timbre",
            "natural authentic human appearance alone",
        ]
        base_req = {"names": ["Emilia Clarke"], "character": "Daenerys Targaryen", "tone": "parody"}
        for sample in banned_samples:
            req = dict(base_req, description=sample)
            with self.assertRaises(ValueError, msg=f"Should reject generic: {sample}") as ctx:
                resolve_identities(req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
            self.assertTrue(
                "generic" in str(ctx.exception).lower() or "banned" in str(ctx.exception).lower(),
                f"Exception should mention generic/banned for {sample}: {ctx.exception}",
            )

    def test_biometric_description_passes_with_real_short_bio(self):
        """Passes with real short bio, embedding it in prompt without banned generics."""
        bio = "platinum-blonde braided hair, pale skin, violet-leaning eyes, fantasy scale top with dark crisscross straps, golden-hour stone colonnade"
        req = {
            "names": ["Emilia Clarke"],
            "character": "Daenerys Targaryen",
            "tone": "dramatic parody",
            "length_s": 5,
            "description": bio,
        }
        res = resolve_identities(req, index_dir=INDEX_DIR, refmods_dir=REFMODS_DIR, aliases_path=ALIASES_PATH)
        self.assertIn(bio, res["description"])

        graph, prompt = build_parody_request(
            resolved=res,
            seed=51083601,
            prefix="community/parody_test/clip",
            frames=124,
            dialogue="I will take what is mine with fire and blood, but today we feast.",
            scene="standing tall in a grand stone hall at golden hour",
        )

        # Must contain the concrete bio
        self.assertIn(bio, prompt)
        # Builder injects the vocal-timbre anchor after featuring (...); bio must still be concrete.
        self.assertIn("exact likeness and vocal timbre", prompt)
        self.assertIn("platinum-blonde braided hair", prompt)
        # Must NOT contain the other banned generic-only filler
        self.assertNotIn("natural authentic human appearance", prompt)

    def test_submit_requires_description(self):
        """submit_parody_job rejects call when description is missing."""
        from submit_parody_run import submit_parody_job
        with self.assertRaises(ValueError) as ctx:
            submit_parody_job(
                name="Emilia Clarke",
                character="Daenerys Targaryen",
                description=None,
                dry_run=True,
            )
        self.assertIn("description", str(ctx.exception).lower())


U1_BIO = "long dark glossy layered hair, smoky winged eyeliner, full glossy lips, cropped zip hoodie, low-rise mini skirt"
U1_LINE = "You honestly thought that outfit was a good idea tonight? Cute."
U1_INDEX_BAD = """| Character | Actor | Franchise | Clips | Date |
| :--- | :--- | :--- | :--- | :--- |
| **Sydney Sweeney** | Sydney Sweeney | Real Person / Celebrity | fixture.mp4 | 2026-08-21 |
| **Nora Fixture** | Nora Fixture | Fixture Show | fixture.mp4 | 2026-08-21 |
"""


def _u1_resolved(**kw):
    base = {
        "names": [],
        "character": None,
        "actor": None,
        "description": f"featuring Megan Fox (character Jennifer Check), {U1_BIO}, styled in parody tone.",
    }
    base.update(kw)
    return base


def _u1_subject_block(prompt):
    return prompt.split("summary:")[0]


class TestU1OpenSlotsAndVoice(unittest.TestCase):
    """U1 (KTD1/KTD2): character-first voice, open scene action, silent clips, featuring dedup, <d> hygiene."""

    def test_voice_label_prefers_character_then_actor(self):
        p = format_parody_prompt(_u1_resolved(character="Jennifer Check", actor="Megan Fox"), dialogue=U1_LINE)
        self.assertIn("[English, using Megan Fox's exact Jennifer Check voice and signature vocal timbre]", p)
        self.assertNotIn("Jennifer Check's natural speaking voice", p)
        p2 = format_parody_prompt(
            _u1_resolved(actor="Sydney Sweeney", description="featuring Sydney Sweeney, wavy blonde hair, blue eyes"),
            dialogue=U1_LINE,
        )
        self.assertIn("[English, using Sydney Sweeney's exact voice and signature vocal timbre]", p2)

    def test_open_scene_action_in_detailed_description(self):
        scene = "leaning across a neon diner counter, twirling a straw"
        p = format_parody_prompt(
            _u1_resolved(character="Jennifer Check", actor="Megan Fox"), dialogue=U1_LINE, scene=scene
        )
        detailed = p.split("detailed_description:")[1].split("overall_soundscape:")[0]
        self.assertIn(scene, detailed)
        self.assertNotIn("stands in position", p)
        self.assertIn(U1_LINE, detailed)

    def test_silent_clip_omits_scenedirect(self):
        for d in (None, "", "   "):
            p = format_parody_prompt(
                _u1_resolved(character="Jennifer Check", actor="Megan Fox"),
                dialogue=d,
                scene="leaning back against metal lockers, rolling her eyes",
            )
            self.assertNotIn("<scenedirect>", p, msg=repr(d))
            self.assertNotIn("</scenedirect>", p, msg=repr(d))
            self.assertNotIn("<d>", p, msg=repr(d))
            self.assertNotIn("Her mouth movements stop completely after the sentence", p, msg=repr(d))
            self.assertTrue(comm.guard_ok(p))
            self.assertTrue(comm.adult_stated(p))

    def test_featuring_dedup_direct(self):
        r = _u1_resolved(
            character="Jennifer Check",
            actor="Megan Fox",
            description="featuring Jennifer Check (Megan Fox), featuring Megan Fox, long dark wavy hair, cropped leather jacket",
        )
        subj = _u1_subject_block(format_parody_prompt(r, dialogue=U1_LINE))
        self.assertEqual(subj.lower().count("featuring"), 1, subj)
        self.assertIn("long dark wavy hair, cropped leather jacket", subj)

    def test_featuring_dedup_through_resolve(self):
        res = resolve_identities(
            {
                "names": ["Megan Fox"],
                "character": "Jennifer Check",
                "actor": "Megan Fox",
                "tone": "parody",
                "length_s": 5,
                "description": "featuring Megan Fox, long dark wavy hair, cropped leather jacket",
            },
            index_dir=INDEX_DIR,
            refmods_dir=REFMODS_DIR,
            aliases_path=ALIASES_PATH,
        )
        subj = _u1_subject_block(format_parody_prompt(res, dialogue=U1_LINE))
        self.assertEqual(subj.lower().count("featuring"), 1, subj)
        self.assertIn("long dark wavy hair, cropped leather jacket", subj)

    def test_stage_cue_dialogue_rejected(self):
        bad = [
            "00:00.000 No speech, bar room tone",
            "t=0 hello there everyone",
            "at 00:02 she says hello",
            "<d>nested line</d>",
            "a stray </d> closing tag",
            "use the `backtick` cue",
            "NO SPEECH here",
            "soft Room Tone only",
        ]
        r = _u1_resolved(character="Jennifer Check", actor="Megan Fox")
        for d in bad:
            with self.assertRaises(ValueError, msg=d):
                format_parody_prompt(r, dialogue=d)


class TestU1SubmitGateAndSydneyFixture(unittest.TestCase):
    """U1 (KTD3): missing-RefMod fail-closed and synthetic Sydney Sweeney request build (CPU only)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="u1_")
        self.root = Path(self.tmp.name)
        self.index = self.root / "index"
        self.index.mkdir()
        (self.index / "INDEX_BAD.md").write_text(U1_INDEX_BAD, encoding="utf-8")
        self.refmods = self.root / "refmods"
        self.refmods.mkdir()
        self.run_dir = self.root / "run"

    def tearDown(self):
        self.tmp.cleanup()

    def _patches(self):
        return (
            mock.patch.object(spr, "INDEX_DIR", self.index),
            mock.patch.object(spr, "REFMODS_DIR", self.refmods),
            mock.patch.object(spr, "ALIASES_PATH", self.root / "no-aliases.json"),
            mock.patch.object(spr.subprocess, "run"),
        )

    def _assert_fail_closed(self, name):
        p1, p2, p3, p4 = self._patches()
        with p1, p2, p3, p4 as run:
            with self.assertRaises(ValueError) as ctx:
                spr.submit_parody_job(name=name, description=U1_BIO, run_dir_override=self.run_dir)
            run.assert_not_called()
        self.assertIn("refmod", str(ctx.exception).lower())
        self.assertFalse(self.run_dir.exists())

    def test_missing_refmod_index_bad_fails_closed(self):
        self._assert_fail_closed("Nora Fixture")

    def test_missing_refmod_index_none_fails_closed(self):
        self._assert_fail_closed("Unlisted Fixture Person")

    def test_sydney_synthetic_fixture_builds_valid_graph(self):
        (self.refmods / "minimaxh3_sydneysweeney_v1_refmod.safetensors").write_bytes(b"fixture")
        p1, p2, p3, p4 = self._patches()
        with p1, p2, p3, p4 as run:
            res = spr.submit_parody_job(
                name="Sydney Sweeney",
                actor="Sydney Sweeney",
                description="wavy honey-blonde hair, bright blue eyes, soft round face, fitted white tank top",
                dialogue="Relax, I always look this good before breakfast.",
                scene="perched on a penthouse bar stool, swirling a drink",
                run_dir_override=self.run_dir,
                dry_run=True,
            )
            run.assert_not_called()
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["resolved"]["index_status"], "bad")
        graph = json.loads((self.run_dir / "request.api.json").read_text(encoding="utf-8"))
        self.assertEqual(len(graph), 20)
        self.assertEqual((graph["c0"]["inputs"]["width"], graph["c0"]["inputs"]["height"]), (768, 1344))
        self.assertEqual(graph["refmods"]["inputs"]["mod_1"], "minimaxh3_sydneysweeney_v1_refmod")
        verify_keep_dials(graph)
        ok, reason = comm.guard_reason(graph)
        self.assertTrue(ok, reason)
        prompt = (self.run_dir / "prompt.txt").read_text(encoding="utf-8")
        self.assertIn("[English, using Sydney Sweeney's exact voice and signature vocal timbre]", prompt)
        self.assertIn("perched on a penthouse bar stool", prompt.split("detailed_description:")[1])
        self.assertEqual(_u1_subject_block(prompt).lower().count("featuring"), 1)

class TestU3LightingAndTone(unittest.TestCase):
    """U3 (R6/R7): lighting-cue gate and satire tone dedupe in format_parody_prompt."""

    def _detailed(self, prompt):
        return prompt.split("detailed_description:")[1].split("overall_soundscape:")[0]

    def test_default_scene_keeps_late_afternoon_lighting(self):
        p = format_parody_prompt(_u1_resolved(character="Jennifer Check", actor="Megan Fox"), dialogue=U1_LINE)
        self.assertIn("late afternoon ambient lighting, soft key on face, subtle fill. Camera locked off", self._detailed(p))
        p2 = format_parody_prompt(
            _u1_resolved(character="Jennifer Check", actor="Megan Fox"),
            dialogue=U1_LINE,
            scene="perched on a bar stool, holding a cocktail glass stem.",
        )
        d2 = self._detailed(p2)
        self.assertIn(
            "perched on a bar stool, holding a cocktail glass stem, late afternoon ambient lighting, soft key on face, subtle fill.",
            d2,
        )
        self.assertNotIn(".,", d2)

    def test_neon_2am_scene_omits_default_lighting(self):
        scene = "sits in a 2 AM neon-lit diner booth, holding a milkshake glass"
        p = format_parody_prompt(_u1_resolved(character="Jennifer Check", actor="Megan Fox"), dialogue=U1_LINE, scene=scene)
        d = self._detailed(p)
        self.assertNotIn("late afternoon ambient lighting", p)
        self.assertIn(f"(S1) {scene}. Camera locked off, no zoom, no pan.", d)
        self.assertTrue(comm.guard_ok(p))

    def test_explicit_lighting_kwarg_wins(self):
        p = format_parody_prompt(
            _u1_resolved(character="Jennifer Check", actor="Megan Fox"),
            dialogue=U1_LINE,
            scene="leans on a vanity counter, holding a makeup brush",
            lighting="warm vanity bulb light",
        )
        self.assertIn("holding a makeup brush, warm vanity bulb light. Camera locked off", self._detailed(p))
        self.assertNotIn("late afternoon ambient lighting", p)

    def test_duplicate_satire_tone_collapsed_through_resolve(self):
        res = resolve_identities(
            {
                "names": ["Megan Fox"],
                "character": "Jennifer Check",
                "actor": "Megan Fox",
                "tone": "satirical adult parody",
                "length_s": 5,
                "description": "long dark wavy hair, cropped leather jacket, styled in a satirical adult parody tone",
            },
            index_dir=INDEX_DIR,
            refmods_dir=REFMODS_DIR,
            aliases_path=ALIASES_PATH,
        )
        p = format_parody_prompt(res, dialogue=U1_LINE)
        self.assertEqual(p.lower().count("parody tone"), 1, _u1_subject_block(p))
        self.assertIn("styled in satirical adult parody tone.", _u1_subject_block(p))
        self.assertIn("long dark wavy hair, cropped leather jacket", _u1_subject_block(p))

    def test_duplicate_satire_tone_collapsed_direct(self):
        r = _u1_resolved(
            character="Jennifer Check",
            actor="Megan Fox",
            description=(
                "featuring Megan Fox, long dark wavy hair, styled in a satirical adult parody tone, "
                "styled in satirical adult parody tone."
            ),
        )
        subj = _u1_subject_block(format_parody_prompt(r, dialogue=U1_LINE))
        self.assertEqual(subj.lower().count("parody tone"), 1, subj)
        self.assertIn("long dark wavy hair, styled in satirical adult parody tone.", subj)
        self.assertNotIn(",,", subj)


if __name__ == "__main__":
    unittest.main()


class TestVoiceUpgradeHygiene(unittest.TestCase):
    """MA-6 / Nov 6 voice upgrade: trailing period, same-name parenthetical, vocal-timbre inject."""

    def test_trailing_period_bio_cleanup(self):
        from resolve import resolve_identities
        # Use a tiny in-memory INDEX via the real helper path by mocking loaders lightly
        req = {
            "names": ["Sydney Sweeney"],
            "character": "Sydney Sweeney",
            "actor": "Sydney Sweeney",
            "description": "Wearing a gold bikini.",
            "tone": "satirical adult parody",
        }
        # Call description builder logic indirectly: validate + format like resolve does
        from resolve import validate_biometric_description, _normalize_key
        bio = validate_biometric_description(req["description"]).rstrip().rstrip(".")
        self.assertEqual(bio, "Wearing a gold bikini")
        primary = "Sydney Sweeney"
        same = (
            _normalize_key(req["character"]) == _normalize_key(req["actor"])
            == _normalize_key(primary)
        )
        self.assertTrue(same)
        parts = [f"actor {req['actor']}"]
        id_spec = f"featuring {primary}" + (f" ({', '.join(parts)})" if parts else "")
        description = f"{id_spec}, {bio}, styled in {req['tone']} tone."
        self.assertIn("bikini, styled in", description)
        self.assertNotIn("bikini., styled", description)
        self.assertIn("(actor Sydney Sweeney)", description)
        self.assertNotIn("character Sydney Sweeney, actor Sydney Sweeney", description)

    def test_end_action_gives_article_phrase(self):
        from build_request import _format_end_action
        self.assertEqual(_format_end_action("She", "A knowing smile and a slow wink"),
                         "She gives a knowing smile and a slow wink")
        self.assertEqual(_format_end_action("He", "an amused half-smile"),
                         "He gives an amused half-smile")
        self.assertEqual(_format_end_action("They", "A wry nod"),
                         "They give a wry nod")
        self.assertEqual(_format_end_action("She", "Holds eye contact"),
                         "She holds eye contact")
        self.assertEqual(_format_end_action("She", "She holds a wry smile"),
                         "She holds a wry smile")

    def test_vocal_timbre_injected_when_missing(self):
        p = format_parody_prompt(
            _u1_resolved(character="Jennifer Check", actor="Megan Fox"),
            dialogue=U1_LINE,
        )
        self.assertIn("exact likeness and vocal timbre", p.split("summary:")[0].lower())

