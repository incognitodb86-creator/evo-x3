"""U3 C2V continuation helpers, frame ledger, intended length, and fail-closed context validation.

Synthetic temp files and data only. No GPU, network, or live effects.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"U3 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

from c2v_chain import (
    C2V_AVAILABLE,
    C2V_STATUS,
    C2V_UNAVAILABLE_REASON,
    is_c2v_available,
    get_c2v_status,
    check_c2v_available,
    calculate_intended_length,
    build_frame_ledger,
    allocate_compensated_clips,
    validate_continuation_context,
    allocate_planned_cuts,
    frame_grid_ok,
    LengthHold,
)


class TestC2VContext(unittest.TestCase):
    """Unit tests for C2V helpers, frame ledger, intended length, and fail-closed validation."""

    def test_c2v_availability_flag(self) -> None:
        """C2V availability is False, UNPROVEN, and check_c2v_available raises RuntimeError."""
        self.assertFalse(C2V_AVAILABLE)
        self.assertFalse(is_c2v_available())
        status = get_c2v_status()
        self.assertFalse(status["available"])
        self.assertEqual(status["status"], "UNPROVEN")
        self.assertIn("native A/V carry is UNPROVEN on this box", status["reason"])
        with self.assertRaisesRegex(RuntimeError, "UNPROVEN on this box"):
            check_c2v_available()

    def test_intended_length_n_target_exact_and_rounding(self) -> None:
        """Intended length calculation: T*fps nearest frame, ties round up, delta <= 0.5."""
        # Exact integer frames: 5.0s @ 24fps = 120 frames
        res_exact = calculate_intended_length(5.0, fps=24)
        self.assertEqual(res_exact["unrounded_frames"], 120.0)
        self.assertEqual(res_exact["n_target"], 120)
        self.assertEqual(res_exact["represented_duration_s"], 5.0)
        self.assertEqual(res_exact["signed_delta_frames"], 0.0)
        self.assertEqual(res_exact["signed_delta_s"], 0.0)

        # Tie breaking: 2.5 frames rounds UP to 3 frames
        # T = 2.5 / 24 = 0.10416666666666667
        res_tie = calculate_intended_length(2.5 / 24, fps=24)
        self.assertAlmostEqual(res_tie["unrounded_frames"], 2.5, places=5)
        self.assertEqual(res_tie["n_target"], 3)
        self.assertAlmostEqual(res_tie["signed_delta_frames"], 0.5, places=5)
        self.assertLessEqual(abs(res_tie["signed_delta_frames"]), 0.5)

        # Round down: 120.4 frames -> 120
        res_down = calculate_intended_length(120.4 / 24, fps=24)
        self.assertEqual(res_down["n_target"], 120)
        self.assertAlmostEqual(res_down["signed_delta_frames"], -0.4, places=5)
        self.assertLessEqual(abs(res_down["signed_delta_frames"]), 0.5)

        # Round up: 120.6 frames -> 121
        res_up = calculate_intended_length(120.6 / 24, fps=24)
        self.assertEqual(res_up["n_target"], 121)
        self.assertAlmostEqual(res_up["signed_delta_frames"], 0.4, places=5)
        self.assertLessEqual(abs(res_up["signed_delta_frames"]), 0.5)

    def test_compensated_clip_allocation_and_frame_ledger_invariants(self) -> None:
        """Grid-attainable target: sum(delivered) == N_target, each continuation head removed once."""
        fps = 24
        # 328 frames = 124 + 102 + 102 (every generated length on the (f-5)%17 grid)
        plan = allocate_compensated_clips(328 / 24, fps=fps, clip_frames=124, context_frames=22)
        self.assertTrue(plan["is_chained"])
        self.assertEqual(plan["n_target"], 328)
        self.assertEqual(sum(c["delivered"] for c in plan["clips"]), 328)
        ledger = plan["frame_ledger"]
        self.assertEqual(len(ledger), plan["clip_count"])
        self.assertEqual((ledger[0]["context"], ledger[0]["removed_head"]), (0, 0))
        for row in ledger[1:]:
            self.assertEqual(row["context"], 22)
            self.assertEqual(row["removed_head"], 22)
            self.assertEqual(row["delivered"], row["generated"] - row["removed_head"])
            self.assertTrue(frame_grid_ok(row["generated"]))

    def test_unattainable_target_holds_not_padded(self) -> None:
        """15 s = 360 frames needs an off-grid final clip -> LengthHold (D2/D3/D4), never padding."""
        with self.assertRaisesRegex(LengthHold, "HOLD"):
            allocate_compensated_clips(15.0, fps=24)
        with self.assertRaisesRegex(LengthHold, "HOLD"):
            allocate_compensated_clips(5.0, fps=24)  # 120 frames, not a single-clip grid length

    def test_planned_cut_allocation_reaches_target_on_grid(self) -> None:
        """Planned cuts: zero context, every clip on grid, sum == N_target; fractional seconds recorded."""
        plan = allocate_planned_cuts(248 / 24, fps=24)  # 124 + 124
        self.assertEqual(plan["n_target"], 248)
        self.assertEqual(sum(c["delivered"] for c in plan["clips"]), 248)
        for c in plan["clips"]:
            self.assertTrue(frame_grid_ok(c["generated"]))
            self.assertEqual((c["context"], c["removed_head"]), (0, 0))
        with self.assertRaisesRegex(LengthHold, "HOLD"):
            allocate_planned_cuts(10.0, fps=24)  # 240 frames: no exact grid sum -> hold for D2

    def test_frame_ledger_rejects_corrupted_invariants(self) -> None:
        """build_frame_ledger fails closed if delivered != generated - removed_head or sum != N_target."""
        corrupted_clips = [
            {"tag": "clip_01", "requested": 124, "generated": 124, "context": 0, "removed_head": 0, "delivered": 100},
        ]
        with self.assertRaisesRegex(ValueError, "Ledger mismatch"):
            build_frame_ledger(corrupted_clips, fps=24, n_target=100)

        valid_clip = [
            {"tag": "clip_01", "requested": 124, "generated": 124, "context": 0, "removed_head": 0, "delivered": 124},
        ]
        with self.assertRaisesRegex(ValueError, "Frame ledger invariant violated"):
            build_frame_ledger(valid_clip, fps=24, n_target=200)

    def _valid(self, tmp: str):
        clip = Path(tmp) / "pred.mp4"
        clip.write_bytes(b"dummy_valid_video")
        pred = {"render_ok": True, "status": "complete", "has_video": True, "has_audio": True,
                "fps": 24, "delivered": 124, "identity_sha256": "ident_same", "clip_path": str(clip)}
        curr = {"fps": 24, "context_length_frames": 22, "identity_sha256": "ident_same"}
        return pred, curr

    def test_valid_continuation_context_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_valid_") as tmp:
            pred, curr = self._valid(tmp)
            validate_continuation_context(pred, curr)

    def test_fail_closed_missing_and_empty_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_file_") as tmp:
            pred, curr = self._valid(tmp)
            with self.assertRaises(FileNotFoundError):
                validate_continuation_context(dict(pred, clip_path=str(Path(tmp) / "nope.mp4")), curr)
            empty = Path(tmp) / "empty.mp4"
            empty.write_bytes(b"")
            with self.assertRaisesRegex(ValueError, "0 bytes"):
                validate_continuation_context(dict(pred, clip_path=str(empty)), curr)
            no_path = dict(pred)
            del no_path["clip_path"]
            with self.assertRaisesRegex(ValueError, "clip path not supplied"):
                validate_continuation_context(no_path, curr)

    def test_fail_closed_stream_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_av_") as tmp:
            pred, curr = self._valid(tmp)
            for patch, msg in (({"has_audio": False}, "video-only context refused"),
                               ({"has_video": False}, "audio-only context refused"),
                               ({"has_video": False, "has_audio": False}, "neither video nor audio")):
                with self.assertRaisesRegex(ValueError, msg):
                    validate_continuation_context(dict(pred, **patch), curr)
            missing = dict(pred)
            del missing["has_audio"]
            with self.assertRaisesRegex(ValueError, "stream evidence"):
                validate_continuation_context(missing, curr)

    def test_fail_closed_wrong_fps_and_frames(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_fps_") as tmp:
            pred, curr = self._valid(tmp)
            with self.assertRaisesRegex(ValueError, "fps mismatch"):
                validate_continuation_context(dict(pred, fps=30), curr)
            with self.assertRaisesRegex(ValueError, "less than required context frames"):
                validate_continuation_context(dict(pred, delivered=10), curr)

    def test_fail_closed_identity_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_id_") as tmp:
            pred, curr = self._valid(tmp)
            with self.assertRaisesRegex(ValueError, "identity hash mismatch"):
                validate_continuation_context(pred, dict(curr, identity_sha256="other"))
            no_id = dict(curr)
            del no_id["identity_sha256"]
            with self.assertRaisesRegex(ValueError, "no identity hash"):
                validate_continuation_context(pred, no_id)

    def test_fail_closed_incomplete_predecessor(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c2v_inc_") as tmp:
            pred, curr = self._valid(tmp)
            with self.assertRaisesRegex(ValueError, "render_ok is False"):
                validate_continuation_context(dict(pred, render_ok=False), curr)
            with self.assertRaisesRegex(ValueError, "status 'failed' is incomplete"):
                validate_continuation_context(dict(pred, status="failed"), curr)
            unknown = dict(pred)
            del unknown["status"]
            del unknown["render_ok"]
            with self.assertRaisesRegex(ValueError, "completion not recorded"):
                validate_continuation_context(unknown, curr)


if __name__ == "__main__":
    unittest.main()
