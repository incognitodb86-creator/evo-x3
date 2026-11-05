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
        }
        self.bad_req = {
            "names": ["Megan Fox"],
            "character": "Jennifer Check",
            "tone": "satirical adult parody",
            "length_s": 15,
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
        self.assertIn("Adult cast, adults-only, fictional 18+ adult scene", prompt)
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


if __name__ == "__main__":
    unittest.main()
