"""U1 baseline test: template KEEP fields, short single-clip plan, take_chain_stitch characterization.

Synthetic temp files only. No GPU, network, process launch, or live run.
Blocks live effects with sys.addaudithook.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


def _deny_live_effects(event: str, args: tuple) -> None:
    if event in {"socket.connect", "subprocess.Popen", "os.system", "os.startfile"}:
        raise RuntimeError(f"U1 CPU fixture blocked {event}")


sys.addaudithook(_deny_live_effects)

from c2v_chain import plan_c2v_chain, DEFAULT_CLIP_FRAMES

REPO_ROOT = Path(r"/home/derekboone/AI/community")
TEMPLATES_DIR = REPO_ROOT / "templates"
B2_TEMPLATE = TEMPLATES_DIR / "b2.api.json"
B2_REFMOD_TEMPLATE = TEMPLATES_DIR / "b2_refmod.api.json"

# Recorded sha256 checksums
B2_RECORDED_SHA256 = "124fb1331874f27803e95c81db67fe270b30dd5533732d7032105839dfd81ca2"
B2_REFMOD_RECORDED_SHA256 = "3a6ad9ad48b233b84a15e2b42e0d2f64c4ffd03e033b60b5b630803b29d25961"

QUEUE_DIR = REPO_ROOT / "scripts" / "queue"
if str(QUEUE_DIR) not in sys.path:
    sys.path.insert(0, str(QUEUE_DIR))
import take_chain_stitch


class TestLongclipBaseline(unittest.TestCase):
    """Characterization tests for baseline templates, single-clip planning, and take_chain_stitch."""

    def test_b2_template_sha256_and_keep_fields(self) -> None:
        """b2.api.json sha256 unchanged and KEEP fields intact."""
        self.assertTrue(B2_TEMPLATE.exists(), f"Missing {B2_TEMPLATE}")
        raw = B2_TEMPLATE.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(actual_sha, B2_RECORDED_SHA256)

        data = json.loads(raw.decode("utf-8"))
        # KEEP dials: unet and 8-step scheduler
        self.assertIn("unet", data)
        unet_name = data["unet"]["inputs"]["unet_name"]
        self.assertIn("10Eros_Max_h3_8stepTURBO_beta7_int8HQ", unet_name)

        self.assertIn("s0_sched", data)
        self.assertEqual(data["s0_sched"]["inputs"]["steps"], 8)

    def test_b2_refmod_template_sha256_and_keep_fields(self) -> None:
        """b2_refmod.api.json sha256 unchanged and KEEP fields intact."""
        self.assertTrue(B2_REFMOD_TEMPLATE.exists(), f"Missing {B2_REFMOD_TEMPLATE}")
        raw = B2_REFMOD_TEMPLATE.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        self.assertEqual(actual_sha, B2_REFMOD_RECORDED_SHA256)

        data = json.loads(raw.decode("utf-8"))
        # KEEP dials: unet, 8-step scheduler, and refapply node
        self.assertIn("unet", data)
        unet_name = data["unet"]["inputs"]["unet_name"]
        self.assertIn("10Eros_Max_h3_8stepTURBO_beta7_int8HQ", unet_name)

        self.assertIn("s0_sched", data)
        self.assertEqual(data["s0_sched"]["inputs"]["steps"], 8)

        self.assertIn("refapply", data)

    def test_existing_short_single_clip_plan_unchanged(self) -> None:
        """Short single-clip plan (<= 8s) unchanged from baseline."""
        plan_5s = plan_c2v_chain(total_length_s=5.0)
        self.assertFalse(plan_5s["is_chained"])
        self.assertEqual(plan_5s["clip_count"], 1)
        self.assertEqual(len(plan_5s["clips"]), 1)
        self.assertEqual(plan_5s["clips"][0]["frames"], DEFAULT_CLIP_FRAMES)
        self.assertEqual(plan_5s["clips"][0]["effective_frames"], DEFAULT_CLIP_FRAMES)
        self.assertFalse(plan_5s["clips"][0]["is_continuation"])
        self.assertEqual(plan_5s["total_frames"], DEFAULT_CLIP_FRAMES)
        self.assertEqual(plan_5s["total_seconds"], round(DEFAULT_CLIP_FRAMES / 24, 3))

        plan_8s = plan_c2v_chain(total_length_s=8.0)
        self.assertFalse(plan_8s["is_chained"])
        self.assertEqual(plan_8s["clip_count"], 1)
        self.assertEqual(plan_8s["total_frames"], DEFAULT_CLIP_FRAMES)

    def test_take_chain_stitch_characterization_synthetic(self) -> None:
        """take_chain_stitch characterization with synthetic directories and mocked ffprobe/ffmpeg."""
        with tempfile.TemporaryDirectory(prefix="stitch_base_") as tmp_dir:
            root = Path(tmp_dir)

            # Create synthetic cells matching CELL_RE: c01_s1001, c02_s1002
            c1_dir = root / "c01_s1001"
            c1_dir.mkdir()
            (c1_dir / "c01_s1001.mp4").write_bytes(b"dummy_mp4_1")
            (c1_dir / "render_ok.json").write_text(
                json.dumps({
                    "seed": 1001,
                    "frames": 124,
                    "prompt_sha256": "sha_prompt_1",
                    "clip_sha256": "sha_clip_1",
                    "w": 1280,
                    "h": 720,
                    "bytes": 1024,
                    "rendered_at": "2026-11-05T16:00:00",
                }),
                encoding="utf-8",
            )

            c2_dir = root / "c02_s1002"
            c2_dir.mkdir()
            (c2_dir / "c02_s1002.mp4").write_bytes(b"dummy_mp4_2")
            (c2_dir / "render_ok.json").write_text(
                json.dumps({
                    "seed": 1002,
                    "frames": 124,
                    "prompt_sha256": "sha_prompt_2",
                    "clip_sha256": "sha_clip_2",
                    "w": 1280,
                    "h": 720,
                    "bytes": 1024,
                    "rendered_at": "2026-11-05T16:01:00",
                }),
                encoding="utf-8",
            )

            # Test cells discovery
            found = take_chain_stitch.cells(root)
            self.assertEqual(len(found), 2)
            self.assertEqual([c["cell"] for c in found], ["c01_s1001", "c02_s1002"])

            # Mock probe to return uniform stream facts
            def fake_probe(p: Path) -> dict:
                return {
                    "duration": 5.167,
                    "path": p,
                    "codec_name": "h264",
                    "width": 1280,
                    "height": 720,
                    "r_frame_rate": "24/1",
                    "pix_fmt": "yuv420p",
                    "sample_rate": "44100",
                    "channels": 2,
                }

            with mock.patch.object(take_chain_stitch, "probe", side_effect=fake_probe):
                provs = take_chain_stitch.uniform(found)
                self.assertEqual(len(provs), 2)
                for p in provs:
                    self.assertEqual(p["width"], 1280)
                    self.assertEqual(p["height"], 720)
                    self.assertEqual(p["r_frame_rate"], "24/1")

                out_dir = root / "_stitch"
                out_dir.mkdir()
                key_path = take_chain_stitch.write_key(root, found, out_dir)
                self.assertTrue(key_path.exists())
                key_content = key_path.read_text(encoding="utf-8")
                self.assertIn("c01_s1001", key_content)
                self.assertIn("c02_s1002", key_content)

                # Mock sh (subprocess.run) for build_film
                completed_mock = mock.MagicMock(returncode=0, stderr="", stdout="")
                with mock.patch.object(take_chain_stitch, "sh", return_value=completed_mock) as mock_sh:
                    film_path = take_chain_stitch.build_film(found, provs, out_dir, "test_film", 0.06)
                    self.assertEqual(film_path, out_dir / "test_film.mp4")
                    self.assertTrue((out_dir / "concat_list.txt").exists())
                    # Ensure mock_sh was invoked for concat and mux
                    self.assertEqual(mock_sh.call_count, 2)


if __name__ == "__main__":
    unittest.main()
