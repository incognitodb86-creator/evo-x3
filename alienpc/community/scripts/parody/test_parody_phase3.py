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

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from build_request import (
    DEFAULT_REFMOD_TEMPLATE,
    DEFAULT_UNET as _DEFAULT_UNET,
    _shot_end_clock,
    build_parody_request as _build_parody_request,
    format_parody_prompt,
    populate_refmod_slots,
    verify_keep_dials,
)
import comm

def build_parody_request(*a, **k):
    k.setdefault("require_cond", False)
    out = _build_parody_request(*a, **k)
    # Compat: older asserts unpack 2-tuple
    if isinstance(out, tuple) and len(out) == 3:
        return out[0], out[1]
    return out
from c2v_chain import plan_c2v_chain
from resolve import resolve_identities
from run_record import _sha256_file, build_assets_record, save_run_record, verify_run_artifacts


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
            "description": "a woman of 32 years, platinum-blonde braided hair, pale skin, violet-leaning eyes, fantasy scale top",
        }
        self.bad_req = {
            "names": ["Megan Fox"],
            "character": "Jennifer Check",
            "tone": "satirical adult parody",
            "length_s": 15,
            "description": "a woman of 28 years, long dark wavy hair, cheer jacket, heart earrings",
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
        """R7-c: The resolved description reaches the paste and the paste satisfies the adults guard.

        B2-6: the guard passes on the CLEAN paste - no meta line, no canon-age clause; the adult age
        comes from the resolved bio, and the compliance result is a record (test_b2_6_...).
        """
        prompt = format_parody_prompt(
            self.resolved_bad,
            dialogue="You have no idea what is coming next.",
            scene="standing in a dimly lit hallway at night",
        )
        self.assertIn("Jennifer Check", prompt)
        self.assertIn(self.resolved_bad["description"], prompt)
        for boilerplate in ("adults-only", "One adult performer", "canon age", "styled in parody tone"):
            self.assertNotIn(boilerplate, prompt, f"B2-6 guard/meta boilerplate in the paste: {boilerplate!r}")
        self.assertIn("You have no idea what is coming next", prompt)
        self.assertTrue(comm.guard_ok(prompt))
        self.assertTrue(comm.adult_stated(prompt))

    # ---- item 2 (2026-11-05): the paste shape of h3-prompting R5-R31 + R32-R44 + h3-parody-identity ----
    REQ_SHAPE = {
        "names": ["Emilia Clarke"],
        "character": "Daenerys Targaryen",
        "tone": "parody",
        "length_s": 5,
        "description": "a woman of 24 years, dark curly hair, pale skin, standing at a late-night counter in a red uniform",
    }

    SECTION_ORDER = [
        "subject_definitions:",
        "summary:",
        "retention_analysis:",
        "detailed_description:",
    ]
    BANNED = [
        "overall_soundscape", "non_diegetic_music", "<scenedirect>", "no_dubs", "Non-speaking characters",
        "[static medium shot", "natural speaking voice", "no music", "no songs", "No singing", "never",
        "then ", "after ", "afterwards", "next ", "<Picture 2>", "<Audio 1>", "<Video 2>", "age 28+",
        # B2-6: the guard/meta boilerplate must never enter a named-actress paste (it lives in
        # run_record.json). A real adult age (e.g. "a woman of 24 years") is not boilerplate.
        "canon age", "styled in parody tone", "One adult performer", "adults-only", "<Audio ",
    ]

    def _resolved(self):
        # RefMod lookup points at a dir that does not exist, so the prompt-shape fixture never
        # depends on installed assets (the graph side is covered by test_r7a).
        return resolve_identities(
            dict(self.REQ_SHAPE), index_dir=INDEX_DIR,
            refmods_dir=Path(r"C:\AI\community\runs\_refmods_absent"), aliases_path=ALIASES_PATH
        )

    def _sections(self, prompt):
        """[(section_name, lines)] split on the R5 section headers; R5 allows nothing else."""
        found = [(name, prompt.index(name)) for name in self.SECTION_ORDER]
        self.assertEqual([a for _, a in found], sorted(a for _, a in found), "R5 section order")
        out = []
        for i, (name, at) in enumerate(found):
            end = found[i + 1][1] if i + 1 < len(found) else len(prompt)
            out.append((name, prompt[at + len(name):end].strip().splitlines()))
        self.assertEqual(prompt[: found[0][1]].strip(), "", "text before subject_definitions")
        return out

    def test_prompt_shape_sections_and_required_lines(self):
        """R5/R6/R11/R33/R35/R36/R39/R8: five sections, the labels and the frames-derived clock."""
        prompt = format_parody_prompt(
            self._resolved(),
            dialogue="Welcome back, honey. I have your table ready, and I will only say it once",
            scene="A waitress at the late-night Hooters counter faces the camera and answers a regular",
            frames=124,
            cond_wired=True,
        )
        sections = dict(self._sections(prompt))
        self.assertTrue(any(l.startswith("<Subject 1> is the woman in <Video 1>.") for l in sections["subject_definitions:"]))
        # B2-6: the identity line is the INDEX name + the resolved bio and NOTHING else - no
        # canon-age clause, no tone label, no (character, actor) parenthetical.
        self.assertTrue(any(l.startswith("<Subject 1> Daenerys Targaryen, a woman of 24 years,")
                            and self.REQ_SHAPE["description"] in l and "the only person in the clip" in l
                            for l in sections["subject_definitions:"]))
        self.assertIn("<Picture 1> is the start frame of [Shot 1] for setting, light and framing",
                      sections["subject_definitions:"])
        joined_summary = "\n".join(sections["summary:"])
        self.assertTrue(joined_summary.startswith("[reference generation] "), "R6/R34 task tag")
        self.assertNotIn("adults-only", joined_summary, "B2-6: compliance is recorded, not pasted")
        self.assertIn("<Subject 1> (appears in [Shot 1]): fully_preserved - face, hair, body, skin, wardrobe",
                      sections["retention_analysis:"])
        self.assertIn("<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved - setting, light, framing",
                      sections["retention_analysis:"])
        detail = "\n".join(sections["detailed_description:"])
        self.assertTrue(detail.splitlines()[0].startswith("The target video is a realistic photographic portrait"), "R39 style opening")
        self.assertIn("The camera holds a static shot.", detail.splitlines()[1])
        self.assertIn("[Shot 1] 00:00.000 - 00:05.167", detail)
        self.assertIn("PRIMARY MOTION", detail)
        self.assertIn("<d>[English] Welcome back, honey. I have your table ready, and I will only say it once.</d>", detail)
        self.assertIn("Her lips and jaw shape each word", detail)
        for banned in self.BANNED:
            self.assertNotIn(banned, prompt, f"banned string in paste: {banned!r}")
        self.assertTrue(comm.guard_ok(prompt))
        self.assertTrue(comm.adult_stated(prompt))

    def test_prompt_shape_no_dialogue_has_no_speech(self):
        """R37: no dialogue means no `<d>` block and no `(S1)` speaker ID."""
        prompt = format_parody_prompt(self._resolved(), scene="standing in a stone hall at golden hour")
        self.assertNotIn("<d>", prompt)
        self.assertNotIn("</d>", prompt)
        self.assertNotIn("(S1)", prompt)
        self.assertNotIn("<Picture 1>", prompt)
        self.assertIn("[Shot 1] 00:00.000 - 00:05.167", prompt)
        self.assertTrue(any(l.startswith("<Subject 1> is the woman in <Video 1>.") for l in self._sections(prompt)[0][1]))
        self.assertTrue(comm.guard_ok(prompt))

    def test_prompt_shape_clock_follows_frames(self):
        """R8: the [Shot 1] end clock equals frames / 24 fps for other frame counts too."""
        for frames, clock in ((124, "00:05.167"), (193, "00:08.042"), (49, "00:02.042")):
            prompt = format_parody_prompt(self._resolved(), frames=frames)
            self.assertIn(f"[Shot 1] 00:00.000 - {clock}", prompt)
            self.assertEqual(prompt.count("[Shot 1]"), 2, "R8: one continuous shot, timed once")

    def test_prompt_shape_audio_ref_emits_no_audio_label(self):
        """R33/R42: an unwired `<Audio N>` label never enters the paste."""
        prompt = format_parody_prompt(self._resolved(), audio_ref="some_voice.wav")
        self.assertNotIn("<Audio", prompt)

    def test_graph_built_prompt_carries_the_picture_label(self):
        """R42 gate item 1: `<Picture 1>` in the paste only when the graph wires ref_image_1."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            pool = Path(tmp_dir) / "pool"
            pool.mkdir()
            input_dir = Path(tmp_dir) / "input"
            input_dir.mkdir()
            staged = pool / "hoot_start.jpg"
            staged.write_bytes(b"parity fixture bytes for the cond provenance gate")
            common = dict(
                seed=51083601,
                prefix="community/shape_test/clip",
                frames=124,
                dialogue="Welcome back, honey. I have your table ready, and I will only say it once.",
                scene="A waitress at the late-night Hooters counter faces the camera and answers a regular",
                image=staged.name,
                cond_source=str(staged),
                comfy_input=input_dir,
                approved_pool=pool,
            )
            graph, prompt = build_parody_request(resolved=self.resolved_good, stage_cond=True, **common)
            self.assertEqual(graph["c0"]["inputs"]["ref_images.ref_image_1"], ["img", 0])
            self.assertIn("<Picture 1> is the start frame of [Shot 1]", prompt)
            self.assertIn("<Picture 1> ([Shot 1] scene/identity anchor): fully_preserved", prompt)
            # No Cond at all (require_cond=False): the label must be absent from the paste too.
            no_cond = {k: v for k, v in common.items() if k not in ("image", "cond_source")}
            graph2, prompt2 = build_parody_request(resolved=self.resolved_good, **no_cond)
            self.assertNotIn("ref_images.ref_image_1", graph2["c0"]["inputs"])
            self.assertNotIn("<Picture 1>", prompt2)
            self.assertIn("<Subject 1> is the woman in <Video 1>.", prompt2)

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
        bio = "a woman of 31 years, platinum-blonde braided hair, pale skin, violet-leaning eyes, fantasy scale top with dark crisscross straps, golden-hour stone colonnade"
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
        # Must NOT contain banned generic phrases
        self.assertNotIn("distinctive facial features", prompt)
        self.assertNotIn("exact likeness", prompt)
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

    # ---- B2-6 (2026-11-06): the clean named-actress paste + the compliance RECORD ----
    B2_6_BANNED = [
        # The item's banned list, verbatim: guard/meta boilerplate that used to be pasted.
        "canon age", "styled in parody tone", "One adult performer", "overall_soundscape",
        "non_diegetic_music", "<Audio ",
    ]
    B2_6_RECORD_KEYS = [
        "guard_ok", "adult_stated", "tone", "character", "actor", "description_sha256",
        "age_result", "unet_name", "dials", "template_sha256", "prompt_sha256",
    ]

    def test_b2_6_clean_paste_bans_and_required_lines(self):
        """B2-6: banned boilerplate absent, required structure present, no photo in the no-photo lane."""
        prompt = format_parody_prompt(
            self._resolved(),
            dialogue="Welcome back, honey. I have your table ready, and I will only say it once",
            scene="A waitress at the late-night Hooters counter faces the camera and answers a regular",
            frames=124,
        )
        for banned in self.B2_6_BANNED:
            self.assertNotIn(banned, prompt, f"B2-6 banned boilerplate in paste: {banned!r}")
        # A no-photo paste (cond_wired=False, the default) never carries the picture label.
        self.assertNotIn("<Picture 1>", prompt)
        for required in ("subject_definitions:", "<Subject 1> is the woman in <Video 1>.",
                         "<Subject 1> Daenerys Targaryen, a woman of 24 years,",
                         f"[Shot 1] 00:00.000 - {_shot_end_clock(124)}"):
            self.assertIn(required, prompt, f"B2-6 required line missing from paste: {required!r}")
        self.assertTrue(comm.guard_ok(prompt) and comm.adult_stated(prompt))

    def test_b2_6_builder_refuses_a_bio_that_states_no_adult_age(self):
        """B2-6 fail-closed: a bio with no adult age raises, and the failure prints no prompt text.

        run_queue.py gates every clip on `comm.guard_reason(g0)` with an adult required, so the
        builder refuses here (raise, never a softened prompt) instead of dying at submit time.
        """
        no_age = dict(self._resolved(), description="dark curly hair, pale skin, a red uniform")
        with self.assertRaises(ValueError) as ctx:
            format_parody_prompt(no_age, frames=124)
        msg = str(ctx.exception)
        self.assertIn("adult", msg.lower())
        # The block's record rule: prompt text is never printed, identity is proven by SHA256.
        self.assertNotIn("primary_video_guidance_prompt", msg)
        self.assertNotIn("<Subject 1>", msg)

    def test_b2_6_compliance_lives_in_run_record_json(self):
        """B2-6: run_record.json carries guard_ok/adult_stated/tone/character/actor/description_sha256
        (+ the age result, dials and template SHA256) and NO prompt text; it is a required artifact.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = self._resolved()
            graph, prompt = build_parody_request(
                resolved=res, seed=24, prefix="community/b2_6_test/clip", frames=124)
            artifacts = save_run_record(run_dir=Path(tmp_dir) / "run", resolved=res,
                                       prompt=prompt, graph=graph, chain_plan=None)
            self.assertTrue(artifacts["run_record"].is_file(), "run_record.json must be written")
            self.assertTrue(all(verify_run_artifacts(Path(tmp_dir) / "run",
                                                     require_clip=False).values()))
            rec = json.loads(artifacts["run_record"].read_text(encoding="utf-8"))
            for key in self.B2_6_RECORD_KEYS:
                self.assertIn(key, rec, f"run_record.json missing key {key}")
            self.assertTrue(rec["guard_ok"] and rec["adult_stated"], "compliance gate must pass")
            self.assertFalse(rec["age_result"]["minor_coded_word_present"])
            # The record reports the INDEX rows exactly as the resolver resolved them.
            self.assertEqual((rec["tone"], rec["character"], rec["actor"], rec["names"]),
                             (res["tone"], res["character"], res["actor"], res["names"]))
            self.assertEqual(rec["character"], "Daenerys Targaryen")
            self.assertIn("Emilia Clarke", rec["names"])
            self.assertEqual(rec["description_sha256"],
                             hashlib.sha256(res["description"].encode("utf-8")).hexdigest())
            self.assertEqual(rec["prompt_sha256"], hashlib.sha256(prompt.encode("utf-8")).hexdigest())
            self.assertEqual(rec["unet_name"], _DEFAULT_UNET)
            self.assertEqual(rec["template_sha256"], _sha256_file(DEFAULT_REFMOD_TEMPLATE))
            # Identity is proven by hash: the bio and the paste never appear in the record.
            text = artifacts["run_record"].read_text(encoding="utf-8")
            self.assertNotIn(res["description"], text)
            self.assertNotIn("primary_video_guidance_prompt", text)


if __name__ == "__main__":
    unittest.main()
