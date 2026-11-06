"""U4 stitcher bridge, sum-of-delivered and intended-length invariants, and refusal tests.

Tests refusal of: missing clip, double-trim, mixed streams, and method-smoke.
Synthetic data only. No GPU, network, or live effects.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"U4 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

REPO_ROOT = Path(r"C:\AI\community")
QUEUE_DIR = REPO_ROOT / "scripts" / "queue"
if str(QUEUE_DIR) not in sys.path:
    sys.path.insert(0, str(QUEUE_DIR))
import take_chain_stitch
import c2v_chain
from c2v_chain import bridge_parody_stitch


class TestParodyStitch(unittest.TestCase):
    """Test suite for parody stitcher bridge and validation invariants."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="parody_stitch_")
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _create_synthetic_cell(
        self,
        cell_name: str,
        delivered: int = 124,
        frames: int = 124,
        is_smoke: bool = False,
        trim_count: int = 1,
        width: int = 1280,
        height: int = 720,
        fps: str = "24/1",
        write_mp4: bool = True,
    ) -> Path:
        cell_dir = self.root / cell_name
        cell_dir.mkdir(parents=True, exist_ok=True)
        if write_mp4:
            (cell_dir / f"{cell_name}.mp4").write_bytes(b"synthetic_mp4_bytes")

        meta = {
            "cell": cell_name,
            "seed": 1234,
            "frames": frames,
            "delivered": delivered,
            "effective_frames": delivered,
            "is_smoke": is_smoke,
            "trim_count": trim_count,
            "w": width,
            "h": height,
            "r_frame_rate": fps,
        }
        (cell_dir / "render_ok.json").write_text(json.dumps(meta), encoding="utf-8")
        return cell_dir

    def test_method_smoke_refused_via_flag_or_method(self) -> None:
        """Refuses stitch when is_smoke=True or method is 'smoke' or 'method-smoke'."""
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=102)

        with self.assertRaisesRegex(ValueError, "method-smoke inputs refused"):
            bridge_parody_stitch(self.root, is_smoke=True)

        with self.assertRaisesRegex(ValueError, "method-smoke inputs refused"):
            bridge_parody_stitch(self.root, method="smoke")

        with self.assertRaisesRegex(ValueError, "method-smoke inputs refused"):
            bridge_parody_stitch(self.root, method="method-smoke")

    def test_method_smoke_refused_via_cell_metadata(self) -> None:
        """Refuses stitch when cell metadata indicates smoke generation."""
        self._create_synthetic_cell("c01_s1001", delivered=124, is_smoke=True)
        self._create_synthetic_cell("c02_s1002", delivered=102)

        with self.assertRaisesRegex(ValueError, "method-smoke inputs refused"):
            bridge_parody_stitch(self.root)

    def test_missing_clip_refused(self) -> None:
        """Refuses stitch when a cell is missing its .mp4 file."""
        self._create_synthetic_cell("c01_s1001", delivered=124, write_mp4=True)
        self._create_synthetic_cell("c02_s1002", delivered=102, write_mp4=False)

        # take_chain_stitch.cells raises SystemExit on missing clip
        with self.assertRaises((SystemExit, ValueError)):
            bridge_parody_stitch(self.root)

    def test_double_trim_refused(self) -> None:
        """Refuses stitch when continuation context head is trimmed more than once."""
        self._create_synthetic_cell("c01_s1001", delivered=124)
        # c02 has trim_count=2 (double trimmed!)
        self._create_synthetic_cell("c02_s1002", delivered=102, trim_count=2)

        with self.assertRaisesRegex(ValueError, "double-trim detected"):
            bridge_parody_stitch(self.root)

    def test_mixed_stream_types_refused(self) -> None:
        """Refuses stitch when cells have differing canvas dimensions or frame rates."""
        self._create_synthetic_cell("c01_s1001", delivered=124, width=1280, height=720)
        self._create_synthetic_cell("c02_s1002", delivered=102, width=1920, height=1080)

        def mock_probe_mixed(p: Path) -> dict:
            cell_name = p.parent.name
            if cell_name == "c01_s1001":
                w, h = 1280, 720
            else:
                w, h = 1920, 1080
            return {
                "duration": 5.0,
                "path": p,
                "codec_name": "h264",
                "width": w,
                "height": h,
                "r_frame_rate": "24/1",
                "pix_fmt": "yuv420p",
                "sample_rate": "44100",
                "channels": 2,
            }

        with mock.patch.object(take_chain_stitch, "probe", side_effect=mock_probe_mixed):
            with self.assertRaises((SystemExit, ValueError)):
                bridge_parody_stitch(self.root)

    def test_sum_of_delivered_invariant_check(self) -> None:
        """Fails closed when sum(delivered) does not match expected_frames."""
        # 124 + 102 = 226 frames delivered
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=124)

        with self.assertRaisesRegex(ValueError, "does not match expected_frames"):
            bridge_parody_stitch(self.root, expected_frames=300)

    def test_intended_length_invariant_check(self) -> None:
        """Fails closed when sum(delivered) does not match N_target from expected_duration_s."""
        # 124 + 102 = 226 frames delivered. 10.0s @ 24fps = 240 frames
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=124)

        with self.assertRaisesRegex(ValueError, "does not match N_target"):
            bridge_parody_stitch(self.root, expected_duration_s=10.0, fps=24)

    def _fake_probe(self, film_frames: int):
        def fake_probe(p: Path) -> dict:
            frames = film_frames if p.name.startswith("parody_final") else 124
            return {"duration": frames / 24, "path": p, "codec_name": "h264", "width": 1280,
                    "height": 720, "r_frame_rate": "24/1", "pix_fmt": "yuv420p",
                    "sample_rate": "44100", "channels": 2}
        return fake_probe

    def test_successful_stitcher_bridge_calls_take_chain_stitch(self) -> None:
        """Two planned-cut cells (124 + 124 = 248) assemble via take_chain_stitch; both invariants hold."""
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=124)
        completed_mock = mock.MagicMock(returncode=0, stderr="", stdout="")
        c2v_chain.FRAME_COUNT_HOOK = lambda p: 248
        try:
            with mock.patch.object(take_chain_stitch, "probe", side_effect=self._fake_probe(248)), \
                 mock.patch.object(take_chain_stitch, "sh", return_value=completed_mock) as mock_sh:
                result = bridge_parody_stitch(self.root, expected_frames=248, expected_duration_s=248 / 24,
                                              fps=24, name="parody_final")
        finally:
            c2v_chain.FRAME_COUNT_HOOK = None
        self.assertEqual(result["cells"], 2)
        self.assertEqual(result["total_delivered_frames"], 248)
        self.assertEqual(result["n_actual"], 248)
        self.assertEqual(result["film"], self.root / "_stitch" / "parody_final.mp4")
        self.assertTrue(result["key_path"].exists())
        self.assertEqual(mock_sh.call_count, 2)

    def test_short_film_fails_n_actual(self) -> None:
        """A film whose decoded length != sum(delivered) fails (no padding passes)."""
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=124)
        completed_mock = mock.MagicMock(returncode=0, stderr="", stdout="")
        c2v_chain.FRAME_COUNT_HOOK = lambda p: 124
        try:
            with mock.patch.object(take_chain_stitch, "probe", side_effect=self._fake_probe(124)), \
                 mock.patch.object(take_chain_stitch, "sh", return_value=completed_mock):
                with self.assertRaisesRegex(ValueError, "N_actual"):
                    bridge_parody_stitch(self.root, expected_frames=248, expected_duration_s=248 / 24,
                                         fps=24, name="parody_final")
        finally:
            c2v_chain.FRAME_COUNT_HOOK = None

    def test_planned_cut_partial_delivery_refused(self) -> None:
        self._create_synthetic_cell("c01_s1001", delivered=124)
        self._create_synthetic_cell("c02_s1002", delivered=102)
        with self.assertRaisesRegex(ValueError, "planned-cut cell"):
            bridge_parody_stitch(self.root)

    def test_continuation_cell_refused_while_c2v_unproven(self) -> None:
        self._create_synthetic_cell("c01_s1001", delivered=124)
        d = self._create_synthetic_cell("c02_s1002", delivered=102)
        meta = json.loads((d / "render_ok.json").read_text(encoding="utf-8"))
        meta["is_continuation"] = True
        meta["context"] = 22
        (d / "render_ok.json").write_text(json.dumps(meta), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "C2V continuation"):
            bridge_parody_stitch(self.root)


if __name__ == "__main__":
    unittest.main()
